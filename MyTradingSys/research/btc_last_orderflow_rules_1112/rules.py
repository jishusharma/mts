"""btc-last-orderflow-rules-1112: R8 (y67l86cSqb8), R5 and R11 (9IliXww64uM) on BTC DEV. PREREG.md is frozen.

SOURCED / OURS labels are in PREREG.md. DEV only: the loader refuses any month after 2024-05.
Grid: minute i = i-th 1m bar from 2022-01-01 00:00Z; day d = i // 1440; DEV = days 31..881.
Delta = 2 * taker_buy_volume - volume (same quantity as aggTrades summed by aggressor side per minute).
Outcome: close of the 1m bar entry+59 over the entry open, signed, minus the round-trip fee (backtest/fees.py), percent.
"""
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'backtest'))
import fees  # noqa: E402
import trade_sanity  # noqa: E402

COST_PCT = fees.BINANCE_TAKER * 2 * 100
KLINES = 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'
FIRST_MONTH, LAST_MONTH = '2022-01', '2024-05'
DAY = 1440
DEV_FIRST_DAY, DEV_DAYS = 31, 851
HALF_DAY = 456                       # 2023-04-02: midpoint of DEV (OURS)
H = 60                               # horizon, minutes (OURS)
NFLOOR, NDRAW, SEED = 180, 500, 1
T0_MS = int(np.datetime64('2022-01-01T00:00', 'ms').astype('int64'))

SMA_N, LAG_H, EXT_WIN, EXT_PCT = 48, 24, 720, 95.0   # R8, all OURS
VA_FRAC, BIN_FRAC, LAST_ENTRY_MIN = 0.70, 0.0005, 1200   # R5/R11 value area, all OURS
Q_PERSIST = 0.5                      # R11, OURS


def load_dev(pattern=KLINES):
    """(o, h, l, c, v, tb) float arrays on the 1m grid from 2022-01-01 to 2024-05-31 23:59; missing bars = NaN."""
    rows = []
    for f in sorted(glob.glob(pattern)):
        tag = os.path.basename(f)[len('BTCUSDT-1m-'):-4][:7]
        if not (FIRST_MONTH <= tag <= LAST_MONTH):
            continue
        with open(f) as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])))
    a = np.array(rows)
    n = (DEV_FIRST_DAY + DEV_DAYS) * DAY
    idx = ((a[:, 0] - T0_MS) // 60000).astype(int)
    ok = (idx >= 0) & (idx < n)
    out = np.full((6, n), np.nan)
    for k, col in enumerate(a[:, 1:7].T):
        out[k, idx[ok]] = col[ok]
    return tuple(out)


# ---------------------------------------------------------------- R8
def trend_down(close1h):
    """OURS: 1h close below the mean of the last 48 1h closes AND below the close 24 hours earlier."""
    n = len(close1h)
    out = np.zeros(n, dtype=bool)
    for k in range(SMA_N - 1, n):
        w = close1h[k - SMA_N + 1:k + 1]
        out[k] = close1h[k] < w.mean() and close1h[k] < close1h[k - LAG_H]
    return out


def sell_extreme(delta60, win=EXT_WIN, pct=EXT_PCT):
    """OURS: -delta60[k] >= the pct-th percentile of -delta60 over the previous win hours (strictly before k)."""
    n = len(delta60)
    out = np.zeros(n, dtype=bool)
    sell = -np.asarray(delta60, dtype=float)
    for k in range(win, n):
        out[k] = sell[k] >= np.percentile(sell[k - win:k], pct)
    return out


def r8_signals(close1h, delta60, arm):
    """[(hour k, side)] at the close of 1h bar k. arm 'a': trend-down, selling, no extreme -> short (-1);
    arm 'b': trend-down and sell extreme -> long (+1)."""
    td, ex = trend_down(close1h), sell_extreme(delta60)
    d = np.asarray(delta60, dtype=float)
    out = []
    for k in range(len(d)):
        if not (td[k] and np.isfinite(d[k]) and np.isfinite(close1h[k])):
            continue
        if arm == 'a' and d[k] < 0 and not ex[k]:
            out.append((k, -1))
        elif arm == 'b' and ex[k]:
            out.append((k, 1))
    return out


# ---------------------------------------------------------------- value area (R5, R11)
def _bin(vol, i):
    return vol[i] if 0 <= i < len(vol) else -1.0


def value_area(h, l, c, v, prev_close):
    """Prior-day value area (VAL, VAH) from one day of 1m bars; None if the day is unusable."""
    tp = (h + l + c) / 3.0
    ok = np.isfinite(tp) & np.isfinite(v)
    if ok.sum() < DAY * 0.9 or not np.isfinite(prev_close):
        return None
    tp, vv = tp[ok], v[ok]
    w = BIN_FRAC * prev_close
    base = tp.min()
    b = np.floor((tp - base) / w).astype(int)
    vol = np.bincount(b, weights=vv)
    total = vol.sum()
    poc = int(np.argmax(vol))
    lo = hi = poc
    acc = vol[poc]
    while acc < VA_FRAC * total:
        down = _bin(vol, lo - 1)
        up = _bin(vol, hi + 1)
        if down < 0 and up < 0:
            break
        if up >= down:
            hi += 1
            acc += vol[hi]
        else:
            lo -= 1
            acc += vol[lo]
    return base + lo * w, base + (hi + 1) * w


def day_va(h, l, c, v, d):
    """Value area for day d from day d-1 only."""
    a, b = (d - 1) * DAY, d * DAY
    return value_area(h[a:b], l[a:b], c[a:b], v[a:b], c[b - 1])


# ---------------------------------------------------------------- R5
def r5_trade(day_open, hi, lo, val, vah):
    """hi/lo: 1m highs/lows of the day from minute 0. Returns (minute m of the touch bar, side) or None.
    Open inside [val, vah]; first bar from minute 1 to LAST_ENTRY_MIN touching VAH (short) or VAL (long); both = skip."""
    if not (val <= day_open <= vah):
        return None
    for m in range(1, min(LAST_ENTRY_MIN, len(hi) - 1) + 1):
        up, dn = hi[m] >= vah, lo[m] <= val
        if up and dn:
            return None
        if up:
            return m, -1
        if dn:
            return m, 1
    return None


# ---------------------------------------------------------------- R11
def r11_event(day_open, close15, vol15, val, vah):
    """Returns (j, side, q) for the first fresh breakout bar of the day with two follow-up bars, or None.
    Previous close for bar 0 is the day open."""
    prev = day_open
    for j in range(len(close15)):
        inside = val <= prev <= vah
        side = 1 if close15[j] > vah else -1 if close15[j] < val else 0
        if inside and side != 0:
            if j + 2 >= len(close15) or vol15[j] <= 0:
                return None
            fwd_vol = vol15[j + 1:j + 3]
            q = float(fwd_vol.mean()) / vol15[j]
            return j, side, q
        prev = close15[j]
    return None


# ---------------------------------------------------------------- outcomes
def fwd_gross_pct(o, c, e, h=H):
    j = e + h - 1
    if e < 0 or j >= len(o) or np.isnan(o[e]) or np.isnan(c[j]):
        return np.nan
    return (c[j] / o[e] - 1) * 100


def net_pct(gross, side):
    return gross * side - COST_PCT


def decluster(rows, gap=60):
    out, last = [], None
    for r in rows:
        if last is None or r[0] - last >= gap:
            out.append(r)
            last = r[0]
    return out


def regime_label(c, day):
    j, j0 = day * DAY + DAY - 1, (day - 90) * DAY + DAY - 1
    if j0 < 0 or j >= len(c) or np.isnan(c[j]) or np.isnan(c[j0]):
        return 'n/a'
    r = c[j] / c[j0] - 1
    return 'bull' if r > .2 else 'bear' if r < -.2 else 'range'


def stats(net):
    net = np.asarray(net, dtype=float)
    n = len(net)
    sd = float(net.std(ddof=1)) if n > 1 else float('nan')
    mean = float(net.mean()) if n else float('nan')
    t = mean / (sd / np.sqrt(n)) if n > 1 and sd > 0 else float('nan')
    return dict(n=n, mean=mean, sd=sd, t=float(t), pos=float((net > 0).mean()) if n else float('nan'))


def verdict(entries, nets):
    """entries: entry minutes; PASS = mean > 0 and t >= 2 and both halves mean > 0 (operator bar)."""
    st = stats(nets)
    e = np.asarray(entries)
    nt = np.asarray(nets, dtype=float)
    h1, h2 = nt[e < HALF_DAY * DAY], nt[e >= HALF_DAY * DAY]
    st['half1'] = float(h1.mean()) if len(h1) else float('nan')
    st['half2'] = float(h2.mean()) if len(h2) else float('nan')
    st['n1'], st['n2'] = len(h1), len(h2)
    if st['n'] < NFLOOR:
        st['verdict'] = 'INSUFFICIENT_N'
    else:
        ok = st['mean'] > 0 and st['t'] >= 2 and st['half1'] > 0 and st['half2'] > 0
        st['verdict'] = 'PASS' if ok else 'FAIL'
    return st


def placebo(o, c, cand, events, ndraw=NDRAW, seed=SEED):
    """Direction-matched placebo. cand: candidate entry minutes; events: [(entry, side)]. Returns (means, rank)."""
    rng = np.random.default_rng(seed)
    cand = np.asarray(cand)
    g = np.array([fwd_gross_pct(o, c, int(e)) for e in cand])
    keep = np.isfinite(g)
    cand, g = cand[keep], g[keep]
    hour = (cand % DAY) // 60
    byh = {hh: np.flatnonzero(hour == hh) for hh in range(24)}
    cnt = {}
    for e, _ in events:
        cnt[int((e % DAY) // 60)] = cnt.get(int((e % DAY) // 60), 0) + 1
    nlong = sum(1 for _, s in events if s == 1)
    means = np.empty(ndraw)
    for i in range(ndraw):
        pick = np.concatenate([rng.choice(byh[hh], min(k, len(byh[hh])), replace=False) for hh, k in cnt.items()])
        nl = min(nlong, len(pick))
        sides = np.array([1] * nl + [-1] * (len(pick) - nl))
        rng.shuffle(sides)
        rows = decluster(sorted(zip(cand[pick].tolist(), g[pick].tolist(), sides.tolist())))
        means[i] = np.mean([net_pct(x[1], x[2]) for x in rows]) if rows else np.nan
    return means


def arm_result(name, o, c, events, cand, kl):
    """events: [(entry minute, side)] -> stats + placebo + trade_sanity lines."""
    events = decluster(sorted(events))
    nets, trades = [], []
    for e, s in events:
        g = fwd_gross_pct(o, c, e)
        if not np.isfinite(g):
            continue
        n = net_pct(g, s)
        nets.append(n)
        trades.append(dict(side=s, entry_ms=T0_MS + e * 60000, exit_ms=T0_MS + (e + H - 1) * 60000,
                           entry_px=float(o[e]), exit_px=float(c[e + H - 1]), ret=n))
    ent = [e for e, _ in events if np.isfinite(fwd_gross_pct(o, c, e))]
    side = [s for e, s in events if np.isfinite(fwd_gross_pct(o, c, e))]
    st = verdict(ent, nets)
    reg = {}
    for e in ent:
        k = regime_label(c, e // DAY)
        reg[k] = reg.get(k, 0) + 1
    st['regime'] = reg
    st['long'], st['short'] = side.count(1), side.count(-1)
    if st['n'] >= 1:
        pm = placebo(o, c, cand, list(zip(ent, side)))
        st['placebo_mean'] = float(np.nanmean(pm))
        st['placebo_p1'], st['placebo_p99'] = (float(x) for x in np.nanpercentile(pm, [1, 99]))
        st['placebo_rank'] = float((pm[np.isfinite(pm)] <= st['mean']).mean())
    st['year_side'] = trade_sanity.year_side_lines(trades)
    st['sanity'] = trade_sanity.sanity_lines(trade_sanity.log_sanity(trades, kl, n=5, entry_leg='open', exit_leg='close'))
    st['name'] = name
    return st


def run(klines=KLINES):
    o, hi, lo, c, v, tb = load_dev(klines)
    kl = {T0_MS + i * 60000: (o[i], hi[i], lo[i], c[i]) for i in range(len(o)) if np.isfinite(o[i])}
    lo_e, hi_e = DEV_FIRST_DAY * DAY, (DEV_FIRST_DAY + DEV_DAYS) * DAY
    out = {}
    # ---- R8
    nh = len(o) // 60
    close1h = c[59::60][:nh]
    delta60 = (2 * tb - v).reshape(nh, 60).sum(axis=1)
    cand_h = [60 * (k + 1) for k in range(nh - 1) if lo_e <= 60 * (k + 1) <= hi_e - H]
    td, ex = trend_down(close1h), sell_extreme(delta60)
    desc = {}
    for lab, mask in (('extreme', ex), ('not extreme', ~ex)):
        g = [fwd_gross_pct(o, c, 60 * (k + 1)) for k in range(nh - 1)
             if td[k] and mask[k] and lo_e <= 60 * (k + 1) <= hi_e - H]
        g = np.array([x for x in g if np.isfinite(x)])
        desc[lab] = dict(n=len(g), mean_gross_short=float(-g.mean()) if len(g) else float('nan'))
    out['R8_descriptive'] = desc
    for arm, name in (('a', 'R8a trend-down no extreme -> short'), ('b', 'R8b trend-down sell extreme -> long')):
        ev = [(60 * (k + 1), s) for k, s in r8_signals(close1h, delta60, arm) if lo_e <= 60 * (k + 1) <= hi_e - H]
        out['R8' + arm] = arm_result(name, o, c, ev, cand_h, kl)
    # ---- R5 and R11
    cand5 = list(range(lo_e + 5, hi_e - H, 5))
    ev5, evp, evd = [], [], []
    inside_stay, inside_n, out_stay, out_n = 0, 0, 0, 0
    for d in range(DEV_FIRST_DAY, DEV_FIRST_DAY + DEV_DAYS):
        va = day_va(hi, lo, c, v, d)
        if va is None:
            continue
        val, vah = va
        a, b = d * DAY, (d + 1) * DAY
        dopen = o[a]
        if not np.isfinite(dopen) or np.isnan(hi[a:b]).any() or np.isnan(lo[a:b]).any():
            continue
        stay = hi[a:b].max() <= vah and lo[a:b].min() >= val
        if val <= dopen <= vah:
            inside_n += 1
            inside_stay += int(stay)
        else:
            out_n += 1
            out_stay += int(stay)
        t5 = r5_trade(dopen, hi[a:b], lo[a:b], val, vah)
        if t5:
            ev5.append((a + t5[0] + 1, t5[1]))
        c15 = c[a:b].reshape(96, 15)[:, -1]
        v15 = v[a:b].reshape(96, 15).sum(axis=1)
        e11 = r11_event(dopen, c15, v15, val, vah)
        if e11:
            j, s, q = e11
            (evp if q >= Q_PERSIST else evd).append((a + 15 * (j + 3), s))
    out['R5_descriptive'] = dict(open_inside_days=inside_n, stay_inside_share=inside_stay / max(inside_n, 1),
                                 open_outside_days=out_n, stay_inside_share_outside=out_stay / max(out_n, 1))
    out['R5'] = arm_result('R5 open inside prior VA, fade first edge touch', o, c, ev5, cand5, kl)
    out['R11p'] = arm_result('R11p breakout, volume persists, with the break', o, c, evp, cand5, kl)
    out['R11d'] = arm_result('R11d breakout, volume dries up, with the break', o, c, evd, cand5, kl)
    return out


def write_results(res):
    with open(os.path.join(HERE, 'results.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    lines = ['| Arm | n (L/S) | mean net % | sd | t | half 1 / half 2 | share pos | placebo mean (p1..p99) | placebo rank | verdict | Regime mix |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for k in ('R8a', 'R8b', 'R5', 'R11p', 'R11d'):
        s = res[k]
        lines.append('| %s | %d (%d/%d) | %+.4f | %.3f | %.2f | %+.4f (n %d) / %+.4f (n %d) | %.1f %% | %+.4f (%+.4f..%+.4f) | %.1f %% | %s | %s |' % (
            s['name'], s['n'], s['long'], s['short'], s['mean'], s['sd'], s['t'], s['half1'], s['n1'], s['half2'], s['n2'],
            100 * s['pos'], s['placebo_mean'], s['placebo_p1'], s['placebo_p99'], 100 * s['placebo_rank'], s['verdict'],
            ' '.join('%s %d' % kv for kv in sorted(s['regime'].items()))))
    txt = '\n'.join(lines)
    for k in ('R8a', 'R8b', 'R5', 'R11p', 'R11d'):
        txt += '\n\n%s per-year and long/short (net %%):\n\n' % res[k]['name'] + '\n'.join(res[k]['year_side'])
    return txt


if __name__ == '__main__':
    r = run()
    print(write_results(r))
    print(json.dumps({k: r[k] for k in ('R8_descriptive', 'R5_descriptive')}, indent=1))
    for k in ('R8a', 'R8b', 'R5', 'R11p', 'R11d'):
        print(k, '\n'.join(r[k]['sanity']))
