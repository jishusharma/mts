"""Card btc-of-map-events-1112: PREREG A2 (absorption) and A3 (funding extreme) on DEV only. PREREG.md is frozen.
SOURCED = PREREG/card, OURS = chosen here. A1 needs aggTrades (not on disk): NOT_RUN.
- A2: 5m bars from 1m klines; delta5 = sum(2*taker_buy - volume); event = |delta5| >= 98th pct of |delta5| over the previous
  30 days (8,640 5m bars) AND |close-open|/open < 0.1 %; trade AGAINST the delta sign. Entry = next 1m open after the bar.
- A3: settlements 00/08/16Z; event = |rate| >= 90th pct of |rate| over the previous 270 settlements; trade AGAINST the payers
  (short if rate > 0). Entry = open of the 1m bar one minute after the timestamp.
- De-clustering: accept an event only if >= 60 min after the previous accepted one; events with any missing 1m bar
  from the event window through entry+60 are dropped first.
- Outcome: close of the 1m bar h minutes after the entry (h-1 bars on) over the entry open, signed, minus the round-trip cost
  from backtest/fees.py (Binance taker both sides). Percent.
- Placebo: 1,000 draws seed 1112, same UTC-hour histogram of entry times, same long/short count, same de-clustering.
DEV only: the loader takes klines up to 2024-05 and refuses every other split. No F: access unless the files exist.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'backtest'))
import fees  # noqa: E402

COST_PCT = fees.BINANCE_TAKER * 2 * 100  # round trip, percent (0.10)
KLINES = 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'
FUNDING = 'F:/MTS/Dumps/backtest/raw/fundingRate/BTCUSDT-fundingRate-*.csv'
FIRST_MONTH, LAST_MONTH = '2022-01', '2024-05'
DEV_START, DEV_END = '2022-02-01', '2024-05-31'
DAY_MIN = 1440
DEV_FIRST_MIN = 31 * DAY_MIN          # grid starts 2022-01-01; DEV starts 2022-02-01
DEV_DAYS = 851
WIN5 = 30 * 288
PCT_A2, MOVE_MAX = 98.0, 0.001
FUND_WIN, PCT_A3 = 270, 90.0
GAP_MIN, SEED, NDRAW, NFLOOR = 60, 1112, 1000, 180
HORIZONS = (15, 60)
SESSIONS = (('Asia', 0, 8), ('Europe', 8, 14), ('US', 14, 21), ('Late', 21, 24))


def session_of(hour):
    return next(n for n, a, b in SESSIONS if a <= hour < b)


def fwd_gross_pct(o, c, e, h):
    j = e + h - 1
    if e < 0 or j >= len(o) or np.isnan(o[e]) or np.isnan(c[j]):
        return np.nan
    return (c[j] / o[e] - 1) * 100


def net_pct(gross, side):
    return gross * side - COST_PCT


def decluster(entries):
    """entries: time-sorted tuples whose first item is the entry minute; keep those >= GAP_MIN after the last kept."""
    out, last = [], None
    for e in entries:
        if last is None or e[0] - last >= GAP_MIN:
            out.append(e)
            last = e[0]
    return out


def _trailing_pct(x, win, q, chunk=2000):
    """Percentile q of x[k-win:k] (past only, NaN ignored); NaN while fewer than half the window is valid."""
    out = np.full(len(x), np.nan)
    view = np.lib.stride_tricks.sliding_window_view(x, win)   # view[i] = x[i:i+win] -> threshold for k = i+win
    last = len(view) - 1                                      # k = len(x) has no bar
    for s in range(0, last, chunk):
        blk = view[s:min(s + chunk, last)]
        ok = np.isfinite(blk).sum(1) >= win // 2
        r = np.full(len(blk), np.nan)
        if ok.any():
            r[ok] = np.nanpercentile(blk[ok], q, axis=1)
        out[win + s: win + s + len(blk)] = r
    return out


def _bad_prefix(o, c, v, tb):
    """Prefix count of 1m bars missing any field; a window is complete when its count does not change."""
    bad = ~(np.isfinite(o) & np.isfinite(c) & np.isfinite(v) & np.isfinite(tb))
    return np.concatenate([[0], np.cumsum(bad)])


def a2_events(o, c, v, tb, start_bar5=0):
    """De-clustered A2 events: dicts entry (1m grid index), side (+1 long), bar5. start_bar5 = first bar allowed."""
    n5 = len(o) // 5
    m = n5 * 5
    d = (2 * tb[:m] - v[:m]).reshape(n5, 5).sum(1)
    o5, c5 = o[:m].reshape(n5, 5)[:, 0], c[:m].reshape(n5, 5)[:, 4]
    with np.errstate(invalid='ignore'):
        move = np.abs(c5 / o5 - 1)
    thr = _trailing_pct(np.abs(d), WIN5, PCT_A2)
    pre = _bad_prefix(o, c, v, tb)
    hmax = max(HORIZONS)
    out = []
    with np.errstate(invalid='ignore'):
        hits = np.flatnonzero(np.isfinite(thr) & np.isfinite(d) & (np.abs(d) >= thr) & (move < MOVE_MAX))
    for k in hits:
        k = int(k)
        e = (k + 1) * 5
        if k < start_bar5 or e + hmax > len(o) or pre[e + hmax] != pre[k * 5]:
            continue
        out.append((e, -1 if d[k] > 0 else 1, k))
    return [dict(entry=e, side=s, bar5=k) for e, s, k in decluster(out)]


def a3_signals(rate):
    """rate = chronological settlement rates; returns [(index, side)], side against the payers."""
    rate = np.asarray(rate, dtype=float)
    r = np.abs(rate)
    out = []
    for i in range(FUND_WIN, len(r)):
        if r[i] >= np.percentile(r[i - FUND_WIN:i], PCT_A3):
            out.append((i, -1 if rate[i] > 0 else 1))
    return out


def cell_stats(net, floor=NFLOOR):
    net = np.asarray(net, dtype=float)
    n = len(net)
    sd = float(net.std(ddof=1)) if n > 1 else float('nan')
    mean = float(net.mean()) if n else float('nan')
    t = mean / (sd / np.sqrt(n)) if n > 1 and sd > 0 else float('nan')
    return dict(n=n, mean=mean, sd=sd, t=float(t), pos=float((net > 0).mean()) if n else float('nan'),
                label='INSUFFICIENT_N' if n < floor else '')


def placebo_band(o, c, ev, h, seed=SEED, ndraw=NDRAW):
    """1st/99th percentile of the placebo mean net: same hour histogram, long/short count and de-clustering.
    Candidates = 5m-bar entries (minute 5k+5) inside DEV with a defined forward return."""
    rng = np.random.default_rng(seed)
    last_dev = (DEV_FIRST_MIN + DEV_DAYS * DAY_MIN)
    cand = np.arange(DEV_FIRST_MIN + 5, min(last_dev, len(o) - max(HORIZONS) - 1), 5)
    g = np.array([fwd_gross_pct(o, c, int(e), h) for e in cand])
    keep = np.isfinite(g)
    cand, g = cand[keep], g[keep]
    hour = (cand % DAY_MIN) // 60
    byh = {hh: np.flatnonzero(hour == hh) for hh in range(24)}
    ent_h = [int((e['entry'] % DAY_MIN) // 60) for e in ev]
    cnt = {hh: ent_h.count(hh) for hh in set(ent_h)}
    nlong = sum(1 for e in ev if e['side'] == 1)
    means = np.empty(ndraw)
    for i in range(ndraw):
        pick = np.concatenate([rng.choice(byh[hh], min(k, len(byh[hh])), replace=False) for hh, k in cnt.items()])
        nl = min(nlong, len(pick))
        sides = np.array([1] * nl + [-1] * (len(pick) - nl))
        rng.shuffle(sides)
        rows = sorted(zip(cand[pick].tolist(), g[pick].tolist(), sides.tolist()))
        kept = decluster(rows)
        means[i] = np.mean([net_pct(x[1], x[2]) for x in kept]) if kept else np.nan
    return float(np.nanpercentile(means, 1)), float(np.nanpercentile(means, 99))


def load_funding(pattern=FUNDING):
    """[(minute index on the 1m grid from 2022-01-01, rate)] for 00/08/16Z settlements; months <= 2024-05 only."""
    t0 = int(np.datetime64('2022-01-01T00:00', 'ms').astype('int64'))
    rows = []
    for f in sorted(glob.glob(pattern)):
        tag = os.path.basename(f).split('fundingRate-')[-1][:7]
        if '2021-10' <= tag <= LAST_MONTH:
            with open(f) as fh:
                for r in csv.DictReader(fh):
                    mi = int(round((int(r['calc_time']) - t0) / 60000.0))
                    if mi % 480 == 0:
                        rows.append((mi, float(r['last_funding_rate'])))
    rows.sort()
    return rows


def regime_label(c, day):
    j, j0 = day * DAY_MIN + DAY_MIN - 1, (day - 90) * DAY_MIN + DAY_MIN - 1
    if j0 < 0 or j >= len(c) or np.isnan(c[j]) or np.isnan(c[j0]):
        return 'n/a'
    r = c[j] / c[j0] - 1
    return 'bull' if r > .2 else 'bear' if r < -.2 else 'range'


def run_cell(o, c, ev, h):
    rows = [(e['entry'], net_pct(fwd_gross_pct(o, c, e['entry'], h), e['side'])) for e in ev]
    st = cell_stats(np.array([x[1] for x in rows]))
    st['sessions'] = {s: sum(1 for e, _ in rows if session_of((e % DAY_MIN) // 60) == s) for s, _, _ in SESSIONS}
    reg = {}
    for e, _ in rows:
        k = regime_label(c, e // DAY_MIN)
        reg[k] = reg.get(k, 0) + 1
    st['regime'] = reg
    if st['n'] >= NFLOOR:
        st['placebo'] = placebo_band(o, c, ev, h)
    return st


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True)
    ap.add_argument('--klines', default=KLINES)
    ap.add_argument('--funding', default=FUNDING)
    a = ap.parse_args(argv)
    if a.split != 'dev':
        raise SystemExit('only --split dev is allowed (PREREG: VALIDATION/GAP/RESERVE/HOLDOUT not opened by this card)')
    if not glob.glob(a.klines):
        raise SystemExit('DATA_ABSENT: no 1m kline files at %s (no F: drive here); nothing run, nothing fabricated' % a.klines)
    sys.path.insert(0, HERE)
    import clocks
    t0, o, c, v, tb = clocks.load_dev(a.klines)
    ev2 = a2_events(o, c, v, tb, start_bar5=DEV_FIRST_MIN // 5)
    fund = load_funding(a.funding)
    ev3 = []
    if fund:
        pre = _bad_prefix(o, c, v, tb)
        hmax = max(HORIZONS)
        raw = [(fund[i][0] + 1, s) for i, s in a3_signals([r for _, r in fund])
               if DEV_FIRST_MIN <= fund[i][0] < DEV_FIRST_MIN + DEV_DAYS * DAY_MIN]
        raw = [x for x in raw if x[0] + hmax <= len(o) and pre[x[0] + hmax] == pre[x[0] - 1]]
        ev3 = [dict(entry=e, side=s) for e, s in decluster(raw)]
    res = {}
    lines = ['# EVENTS: BTC order-flow map A2/A3 on DEV %s .. %s (card btc-of-map-events-1112)' % (DEV_START, DEV_END), '',
             'Frozen PREREG.md. Net = signed forward return minus %.2f %% round trip (fees.py Binance taker). Placebo = 1,000 draws '
             'seed 1112, same hour histogram / long-short count / 60-min de-clustering; band = mean net 1st..99th pct. '
             'n floor %d. VALIDATION NOT OPENED. A1 NOT_RUN (no aggTrades).' % (COST_PCT, NFLOOR), '',
             '| Event | Horizon | n | mean net % | sd | t | share positive | placebo 1-99 % | session mix | Regime mix |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for name, ev in (('A2 absorption', ev2), ('A3 funding extreme', ev3)):
        for h in HORIZONS:
            st = run_cell(o, c, ev, h)
            res['%s %dm' % (name, h)] = st
            pb = '%+.3f..%+.3f' % st['placebo'] if 'placebo' in st else 'n/a'
            lines.append('| %s | %dm | %d%s | %+.3f | %.3f | %.2f | %.1f %% | %s | %s | %s |' % (
                name, h, st['n'], ' INSUFFICIENT_N' if st['label'] else '', st['mean'], st['sd'], st['t'],
                100 * st['pos'], pb, ' '.join('%s %d' % kv for kv in st['sessions'].items()),
                ' '.join('%s %d' % kv for kv in st['regime'].items())))
    with open(os.path.join(HERE, 'EVENTS.md'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    with open(os.path.join(HERE, 'results_events.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
