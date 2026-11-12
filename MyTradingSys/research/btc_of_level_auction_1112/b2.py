"""Card btc-of-level-auction-b2-fetch-run-1112: PREREG B2 (unfinished auction at a 24h extreme) on DEV only. PREREG.md is frozen.
SOURCED = PREREG, OURS = chosen here.
Data: Binance USD-M BTCUSDT aggTrades (same market as B1's 1m klines), monthly zips on D:, stream-read, reduced per UTC 15m bar.
- Bucket (OURS reading of 'buckets 0.01 % of the bar open'): w = 0.0001 * bar open, bucket = floor(price / w), same convention as
  b1.py value_area. Top bucket = bucket of the bar high, bottom bucket = bucket of the bar low.
- Aggressor: Binance is_buyer_maker == false -> buyer aggressor (taker buy); true -> seller aggressor.
- High event: bar high >= max high of the previous 96 15m bars (all 96 present) AND top bucket buyer-aggressor volume > 0 AND seller-
  aggressor volume > 0 AND top bucket total volume >= 95th pct of top-bucket volume over the previous 2,880 15m bars
  (30 days, past only, NaN ignored, >= half valid); side short. Low event: mirror with the bottom bucket and 24h low; long.
  A bar that is both a high and a low event is dropped. De-clustered 60 min on the entry minute. Entry = 1m open after the bar.
- Missing data: a bar without trades is NaN; an event needs its own bar, the 96 previous bars and the 1m klines from the bar start to
  entry+60 complete, else dropped.
- Outcome, cost, regime, sessions: reused from btc_orderflow_map_1112/events.py (cost from fees.py). Placebo: seed 1112,
  15m-bar entries (minute 15k+15) over DEV, same UTC-hour histogram, long/short count and de-clustering (PREREG: same bar size).
- Diagnostic (not marked): share of events whose bar extreme is revisited (1m high >= bar high for a high event, low <= bar low
  for a low event) within 24h after the entry, against the same statistic on the placebo draws (same sides).
DEV only: loaders take months 2022-01 (warm-up, trailing windows only) .. 2024-05 and refuse every other split.
"""
import argparse
import glob
import io
import json
import os
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'btc_orderflow_map_1112'))
import events as ev_map  # noqa: E402

BAR_MS = 15 * 60 * 1000
BAR_MIN = 15
DAY_BARS = 96
WIN = 30 * DAY_BARS
PCT, BUCKET = 95.0, 0.0001
HORIZONS, NFLOOR, SEED, NDRAW = ev_map.HORIZONS, ev_map.NFLOOR, ev_map.SEED, ev_map.NDRAW
FIRST_MONTH, LAST_MONTH = '2022-01', '2024-05'
T0_MS = int(np.datetime64('2022-01-01T00:00', 'ms').astype('int64'))
REDUCED = 'D:/MTS_data/binance_aggtrades/reduced'
COLS = ['bar', 'open', 'high', 'low', 'close', 'top_buy', 'top_sell', 'bot_buy', 'bot_sell', 'vol']
T_PASS = 3.72


def month_ok(tag):
    return FIRST_MONTH <= tag <= LAST_MONTH


class Reducer:
    """Streams trade chunks (price, qty, ts_ms, buyer_aggr bool); returns one row per finished 15m bar."""

    def __init__(self):
        self.lv = pd.DataFrame(columns=['bar', 'price', 'buy', 'sell'])
        self.oh = {}

    def feed(self, price, qty, ts, buyer_aggr):
        df = pd.DataFrame({'bar': ts // BAR_MS, 'price': price, 'buy': np.where(buyer_aggr, qty, 0.0),
                           'sell': np.where(buyer_aggr, 0.0, qty)})
        g = df.groupby('bar')['price']
        a = pd.DataFrame({'first': g.first(), 'last': g.last(), 'mx': g.max(), 'mn': g.min()})
        for bar, r in a.iterrows():
            b = int(bar)
            if b in self.oh:
                o = self.oh[b]
                o[1], o[2], o[3] = max(o[1], r['mx']), min(o[2], r['mn']), r['last']
            else:
                self.oh[b] = [r['first'], r['mx'], r['mn'], r['last']]
        lv = df.groupby(['bar', 'price'], as_index=False)[['buy', 'sell']].sum()
        self.lv = lv if self.lv.empty else pd.concat([self.lv, lv], ignore_index=True)
        return self._emit(int(df['bar'].max()))

    def finish(self):
        return self._emit(10 ** 12)

    def _emit(self, before):
        if self.lv.empty:
            return []
        m = self.lv['bar'] < before
        out = self.lv[m].groupby(['bar', 'price'], as_index=False)[['buy', 'sell']].sum()
        self.lv = self.lv[~m].reset_index(drop=True)
        rows = []
        for bar, d in out.groupby('bar'):
            o, hi, lo, cl = self.oh.pop(int(bar))
            rows.append(bar_row(int(bar), o, hi, lo, cl, d['price'].to_numpy(), d['buy'].to_numpy(), d['sell'].to_numpy()))
        return rows


def bar_row(bar, o, hi, lo, cl, price, buy, sell):
    """One reduced bar from per-price aggressor volumes (bucket = floor(price / (0.0001 * open)))."""
    w = BUCKET * o
    b = np.floor(price / w)
    t, s = b == np.floor(hi / w), b == np.floor(lo / w)
    return [bar, o, hi, lo, cl, float(buy[t].sum()), float(sell[t].sum()), float(buy[s].sum()), float(sell[s].sum()),
            float(buy.sum() + sell.sum())]


def reduce_zip(path, chunk=4_000_000):
    """Stream-read one monthly aggTrades zip (never unpacked); returns (DataFrame of reduced bars, trade count)."""
    red, rows, n = Reducer(), [], 0
    with zipfile.ZipFile(path) as zf:
        with zf.open(zf.namelist()[0]) as raw:
            f = io.BufferedReader(raw, 1 << 22)
            head = f.peek(64)[:64].split(b'\n')[0]
            hdr = None if head.split(b',')[0].strip().isdigit() else 0
            for ch in pd.read_csv(f, header=hdr, chunksize=chunk,
                                  names=[0, 1, 2, 3, 4, 5, 6] if hdr is None else None, usecols=[1, 2, 5, 6]):
                p, q, t = ch.iloc[:, 0].to_numpy(float), ch.iloc[:, 1].to_numpy(float), ch.iloc[:, 2].to_numpy('int64')
                maker = ch.iloc[:, 3].astype(str).str.lower().eq('true').to_numpy()
                n += len(ch)
                rows += red.feed(p, q, t, ~maker)
    rows += red.finish()
    return pd.DataFrame(rows, columns=COLS), n


def load_reduced(folder=REDUCED):
    """dict of arrays on the 15m grid from 2022-01-01 to 2024-05-31; NaN = no trades. None if no file."""
    parts = []
    for f in sorted(glob.glob(os.path.join(folder, 'BTCUSDT-bars15-*.csv.gz'))):
        if month_ok(os.path.basename(f)[len('BTCUSDT-bars15-'):][:7]):
            parts.append(pd.read_csv(f))
    if not parts:
        return None
    d = pd.concat(parts)
    d['k'] = d['bar'] - T0_MS // BAR_MS
    last = int((np.datetime64('2024-05-31T23:45', 'ms').astype('int64') - T0_MS) // BAR_MS)
    d = d[(d['k'] >= 0) & (d['k'] <= last)]
    out = {c: np.full(last + 1, np.nan) for c in COLS[1:9]}
    for c in out:
        out[c][d['k'].to_numpy()] = d[c].to_numpy()
    return out


def b2_events(hi, lo, topbuy, topsell, botbuy, botsell, o1, c1, v1, tb1, start_bar=0, pct=PCT, win=WIN):
    """De-clustered B2 events on the 15m grid (1m arrays share the origin). dicts entry, side (+1 long), bar, ext."""
    n = len(hi)
    topv, botv = topbuy + topsell, botbuy + botsell
    prevmax, prevmin = np.full(n, np.nan), np.full(n, np.nan)
    if n > DAY_BARS:
        sw = np.lib.stride_tricks.sliding_window_view
        prevmax[DAY_BARS:] = sw(hi, DAY_BARS).max(1)[:n - DAY_BARS]   # a NaN in the window gives NaN: not an event
        prevmin[DAY_BARS:] = sw(lo, DAY_BARS).min(1)[:n - DAY_BARS]
    thr_t = ev_map._trailing_pct(topv, win, pct)
    thr_b = ev_map._trailing_pct(botv, win, pct)
    with np.errstate(invalid='ignore'):
        he = (hi >= prevmax) & (topbuy > 0) & (topsell > 0) & (topv >= thr_t)
        le = (lo <= prevmin) & (botbuy > 0) & (botsell > 0) & (botv >= thr_b)
    both = he & le
    pre = ev_map._bad_prefix(o1, c1, v1, tb1)
    hmax = max(HORIZONS)
    rows = []
    for k in np.flatnonzero((he | le) & ~both):
        k = int(k)
        e = (k + 1) * BAR_MIN
        if k < start_bar or e + hmax > len(o1) or pre[e + hmax] != pre[k * BAR_MIN]:
            continue
        rows.append((e, -1 if he[k] else 1, k, float(hi[k] if he[k] else lo[k])))
    return [dict(entry=e, side=s, bar=k, ext=x) for e, s, k, x in ev_map.decluster(rows)]


def revisit(h1, l1, e, side, ext, span=1440):
    """True/False: extreme touched again within `span` 1m bars after entry; None if the window is incomplete."""
    if e + span > len(h1):
        return None
    x = h1[e:e + span] if side == -1 else l1[e:e + span]
    if np.isnan(x).any():
        return None
    return bool(x.max() >= ext) if side == -1 else bool(x.min() <= ext)


def placebo(o, c, h1, l1, ev, hz, seed=SEED, ndraw=NDRAW):
    """(net 1st, net 99th, revisit median, revisit 1st, revisit 99th). 15m-bar entries over DEV."""
    rng = np.random.default_rng(seed)
    last_dev = ev_map.DEV_FIRST_MIN + ev_map.DEV_DAYS * ev_map.DAY_MIN
    cand = np.arange(ev_map.DEV_FIRST_MIN + BAR_MIN, min(last_dev, len(o) - max(HORIZONS) - 1), BAR_MIN)
    g = np.array([ev_map.fwd_gross_pct(o, c, int(e), hz) for e in cand])
    keep = np.isfinite(g)
    cand, g = cand[keep], g[keep]
    rv = {}
    for side in (-1, 1):
        arr = np.full(len(cand), np.nan)
        for i, e in enumerate(cand):
            e = int(e)
            seg = h1[e - BAR_MIN:e] if side == -1 else l1[e - BAR_MIN:e]
            if np.isnan(seg).any():
                continue
            r = revisit(h1, l1, e, side, seg.max() if side == -1 else seg.min())
            arr[i] = np.nan if r is None else float(r)
        rv[side] = arr
    hour = (cand % ev_map.DAY_MIN) // 60
    byh = {hh: np.flatnonzero(hour == hh) for hh in range(24)}
    cnt = {}
    for e in ev:
        hh = int((e['entry'] % ev_map.DAY_MIN) // 60)
        cnt[hh] = cnt.get(hh, 0) + 1
    nlong = sum(1 for e in ev if e['side'] == 1)
    means, shares = np.empty(ndraw), np.empty(ndraw)
    for i in range(ndraw):
        pick = np.concatenate([rng.choice(byh[hh], min(k, len(byh[hh])), replace=False) for hh, k in cnt.items()])
        nl = min(nlong, len(pick))
        sides = np.array([1] * nl + [-1] * (len(pick) - nl))
        rng.shuffle(sides)
        kept = ev_map.decluster(sorted(zip(cand[pick].tolist(), pick.tolist(), sides.tolist())))
        means[i] = np.mean([ev_map.net_pct(g[j], s) for _, j, s in kept]) if kept else np.nan
        r = np.array([rv[s][j] for _, j, s in kept], dtype=float)
        shares[i] = np.nanmean(r) if len(r) and np.isfinite(r).any() else np.nan
    q = lambda x, p: float(np.nanpercentile(x, p))  # noqa: E731
    return q(means, 1), q(means, 99), q(shares, 50), q(shares, 1), q(shares, 99)


def cell(o, c, h1, l1, evs, hz, with_placebo=True):
    rows = [(e['entry'], ev_map.fwd_gross_pct(o, c, e['entry'], hz), e['side']) for e in evs]
    net = np.array([ev_map.net_pct(g, s) for _, g, s in rows])
    st = ev_map.cell_stats(net)
    st['gross_mean'] = float(np.mean([g * s for _, g, s in rows])) if rows else float('nan')
    st['sessions'] = {s: sum(1 for e, _, _ in rows if ev_map.session_of((e % ev_map.DAY_MIN) // 60) == s)
                      for s, _, _ in ev_map.SESSIONS}
    reg, regm, sesm = {}, {}, {}
    for (e, g, s), x in zip(rows, net):
        k = ev_map.regime_label(c, e // ev_map.DAY_MIN)
        reg[k] = reg.get(k, 0) + 1
        regm.setdefault(k, []).append(x)
        sesm.setdefault(ev_map.session_of((e % ev_map.DAY_MIN) // 60), []).append(x)
    st['regime'] = reg
    st['regime_mean'] = {k: float(np.mean(x)) for k, x in regm.items()}
    st['session_mean'] = {k: float(np.mean(x)) for k, x in sesm.items()}
    ok = [x for x in (revisit(h1, l1, e['entry'], e['side'], e['ext']) for e in evs) if x is not None]
    st['revisit_n'] = len(ok)
    st['revisit_share'] = float(np.mean(ok)) if ok else float('nan')
    if with_placebo and st['n'] >= NFLOOR:
        a, b, m, ra, rb = placebo(o, c, h1, l1, evs, hz)
        st['placebo'] = [a, b]
        st['placebo_revisit'] = [m, ra, rb]
    return st


def verdict(st):
    """PREREG marks on DEV only. VALIDATION is not opened here, so PASS/LEAD cannot be awarded."""
    if st['n'] < NFLOOR:
        return 'INSUFFICIENT_N'
    a, b = st['placebo']
    if abs(st['t']) >= T_PASS and st['mean'] > 0 and not (a <= st['mean'] <= b):
        return 'PENDING_VALIDATION (DEV PASS conditions met; VALIDATION not opened, no mark)'
    return 'FAIL (gross only)' if st['gross_mean'] > 0 and st['mean'] <= 0 else 'FAIL'


HDR = ['| Event | Horizon | n | gross mean % | net mean % | sd | t | share positive | placebo net 1-99 % | revisit share (placebo median, 1-99 %) | Regime mix |',
       '|---|---|---|---|---|---|---|---|---|---|---|']


def row(name, hz, st):
    pb = '%+.3f..%+.3f' % tuple(st['placebo']) if 'placebo' in st else 'n/a'
    pr = ' (%.3f, %.3f..%.3f)' % tuple(st['placebo_revisit']) if 'placebo_revisit' in st else ''
    return '| %s | %dm | %d | %+.3f | %+.3f | %.3f | %.2f | %.1f %% | %s | %.3f of %d%s | %s |' % (
        name, hz, st['n'], st['gross_mean'], st['mean'], st['sd'], st['t'], 100 * st['pos'], pb, st['revisit_share'],
        st['revisit_n'], pr, ' '.join('%s %d' % kv for kv in st['regime'].items()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True)
    ap.add_argument('--reduced', default=REDUCED)
    ap.add_argument('--klines', default=ev_map.KLINES)
    a = ap.parse_args(argv)
    if a.split != 'dev':
        raise SystemExit('only --split dev is allowed (PREREG: VALIDATION/GAP/RESERVE/HOLDOUT not opened by this card)')
    arr = load_reduced(a.reduced)
    if arr is None:
        raise SystemExit('DATA_ABSENT: no reduced 15m tables at %s; nothing run, nothing fabricated' % a.reduced)
    import b1
    o, h, l, c, v, tb = b1.load_dev_hl(a.klines)
    ev = b2_events(arr['high'], arr['low'], arr['top_buy'], arr['top_sell'], arr['bot_buy'], arr['bot_sell'],
                   o, c, v, tb, start_bar=ev_map.DEV_FIRST_MIN // BAR_MIN)
    res = {'B2 unfinished auction %dm' % hz: cell(o, c, h, l, ev, hz) for hz in HORIZONS}
    for st in res.values():
        st['verdict'] = verdict(st)
    nbars = int(np.isfinite(arr['high']).sum())
    nhi = sum(1 for e in ev if e['side'] == -1)
    k15 = res['B2 unfinished auction 15m']
    L = ['# B2: BTC unfinished auction at a 24h extreme (fade), DEV %s .. %s (card btc-of-level-auction-b2-fetch-run-1112)'
         % (ev_map.DEV_START, ev_map.DEV_END), '',
         'Frozen PREREG.md, event B2. Data: Binance USD-M BTCUSDT aggTrades (same market as the B1 klines), 15m bars: %d of %d present '
         '(2022-01 warm-up read for trailing windows only). Net = signed trade (short at a 24h high, long at a 24h low) forward '
         'return minus %.2f %% round trip (taker both sides); gross = net + cost. De-clustered 60 min. Placebo = 1,000 draws seed 1112, '
         '15m-bar entries, same hour histogram / long-short count / de-clustering. n floor %d. VALIDATION, GAP, RESERVE, HOLDOUT NOT '
         'OPENED: PASS and LEAD need VALIDATION, so DEV can only give FAIL, INSUFFICIENT_N or PENDING_VALIDATION.'
         % (nbars, len(arr['high']), ev_map.COST_PCT, NFLOOR), '',
         'Events accepted: %d (%d short at a high, %d long at a low).' % (len(ev), nhi, len(ev) - nhi), ''] + HDR
    L += [row('B2', hz, res['B2 unfinished auction %dm' % hz]) for hz in HORIZONS]
    L += ['', 'Verdict per PREREG words:', '', '| Cell | Verdict |', '|---|---|']
    L += ['| B2 %dm | %s |' % (hz, res['B2 unfinished auction %dm' % hz]['verdict']) for hz in HORIZONS]
    L += ['', 'Mean net % by regime and session (regime = trailing 90d return >+20 % bull, <-20 % bear, OURS):', '',
          '| Horizon | by regime | by session | session n |', '|---|---|---|---|']
    for hz in HORIZONS:
        st = res['B2 unfinished auction %dm' % hz]
        L.append('| %dm | %s | %s | %s |' % (hz, ' '.join('%s %+.3f' % kv for kv in st['regime_mean'].items()),
                                             ' '.join('%s %+.3f' % kv for kv in st['session_mean'].items()),
                                             ' '.join('%s %d' % kv for kv in st['sessions'].items())))
    L += ['', 'Regime mix: ' + ' '.join('%s %d' % kv for kv in k15['regime'].items()) + ' (accepted DEV events, same set for both horizons)',
          '', 'Revisit diagnostic (not marked): share of events whose bar extreme is touched again within 24h of the entry, against '
          'the placebo median and 1-99 % band for the same sides (last-but-one column of the table).']
    with open(os.path.join(HERE, 'B2.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    with open(os.path.join(HERE, 'results_b2.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    print('\n'.join(L))


if __name__ == '__main__':
    main()
