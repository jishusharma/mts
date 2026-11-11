"""Card btc-of-level-auction-b1-run-1112: PREREG B1 (absorption at a prior-day level) on DEV only. PREREG.md is frozen.
SOURCED = PREREG, OURS = chosen here. B2 needs aggTrades (not on disk for DEV): NOT_RUN.
- Levels for UTC day D come from day D-1 only: PDH/PDL = high/low of 1m bars; VAH/VAL = 70 % value area of the 1m volume
  profile (typical price (h+l+c)/3, bucket 0.05 % of the previous close, POC grown by the larger of the next two buckets).
- Event bar: UTC-aligned 5m bar, delta5 = sum(2*taker_buy - volume); |delta5| >= 90th pct of |delta5| over the previous
  30 days AND |close-open|/open < 0.15 %. At a level: delta5 < 0 with the bar low within 0.10 % of PDL or VAL = long;
  delta5 > 0 with the bar high within 0.10 % of PDH or VAH = short. Same flow thresholds NOT at the matching-type level =
  the away contrast set (trade also against delta). De-clustered 60 min per set. Entry = next 1m open after the bar.
- Outcome, cost, placebo (seed 1112), regime labels, session tags: reused from btc_orderflow_map_1112/events.py (cost from fees.py).
DEV only: the loader takes klines up to 2024-05 and refuses every other split.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'btc_orderflow_map_1112'))
import events as ev_map  # noqa: E402
import clocks  # noqa: E402

DAY_MIN = 1440
PCT_B1, BODY_MAX, TOUCH, VA_FRAC, BUCKET = 90.0, 0.0015, 0.001, 0.70, 0.0005
HORIZONS, NFLOOR, SEED = ev_map.HORIZONS, ev_map.NFLOOR, ev_map.SEED
KLINES = clocks.KLINES


def value_area(tp, vol, prev_close):
    """(VAL, VAH) of the 70 % value area; bucket = 0.05 % of prev_close; None when there is no volume."""
    tp, vol = np.asarray(tp, float), np.asarray(vol, float)
    ok = np.isfinite(tp) & np.isfinite(vol)
    tp, vol = tp[ok], vol[ok]
    if len(tp) == 0 or vol.sum() <= 0 or not np.isfinite(prev_close):
        return None
    w = BUCKET * prev_close
    idx = np.floor(tp / w + 1e-9).astype(np.int64)
    lo = idx.min()
    bins = np.bincount(idx - lo, weights=vol)
    top = len(bins) - 1
    a = b = int(np.argmax(bins))
    acc, need = bins[a], VA_FRAC * bins.sum()
    while acc < need and (a > 0 or b < top):
        up = bins[b + 1:b + 3].sum() if b < top else -1.0
        dn = bins[max(a - 2, 0):a].sum() if a > 0 else -1.0
        if up >= dn:
            acc += max(up, 0.0)
            b = min(b + 2, top)
        else:
            acc += max(dn, 0.0)
            a = max(a - 2, 0)
    return float((lo + a) * w), float((lo + b + 1) * w)


def day_levels(h, l, c, tp, v, day):
    """Levels valid for UTC `day`, from day-1 bars only (arrays on the 1m grid from 2022-01-01). None if unavailable."""
    s, e = (day - 1) * DAY_MIN, day * DAY_MIN
    if day < 1 or e > len(h) or np.isfinite(h[s:e]).sum() < DAY_MIN // 2:
        return None
    va = value_area(tp[s:e], v[s:e], c[e - 1])
    if va is None:
        return None
    return dict(PDH=float(np.nanmax(h[s:e])), PDL=float(np.nanmin(l[s:e])), VAL=va[0], VAH=va[1])


def b1_events(o, h, l, c, v, tb, start_bar5=0):
    """{'at': [...], 'away': [...]} de-clustered dicts entry (1m index), side (+1 long), bar5, day."""
    tp = (h + l + c) / 3
    n5 = len(o) // 5
    m = n5 * 5
    d = (2 * tb[:m] - v[:m]).reshape(n5, 5).sum(1)
    o5, c5 = o[:m].reshape(n5, 5)[:, 0], c[:m].reshape(n5, 5)[:, 4]
    h5, l5 = h[:m].reshape(n5, 5).max(1), l[:m].reshape(n5, 5).min(1)
    with np.errstate(invalid='ignore'):
        move = np.abs(c5 / o5 - 1)
        thr = ev_map._trailing_pct(np.abs(d), ev_map.WIN5, PCT_B1)
        hits = np.flatnonzero(np.isfinite(thr) & np.isfinite(d) & (np.abs(d) >= thr) & (move < BODY_MAX))
    pre = ev_map._bad_prefix(o, c, v, tb)
    hmax = max(HORIZONS)
    cache, at, away = {}, [], []
    for k in map(int, hits):
        e = (k + 1) * 5
        if k < start_bar5 or e + hmax > len(o) or pre[e + hmax] != pre[k * 5]:
            continue
        day = (k * 5) // DAY_MIN
        if day not in cache:
            cache[day] = day_levels(h, l, c, tp, v, day)
        lv = cache[day]
        if lv is None:
            continue
        if d[k] < 0:
            hit = any(abs(l5[k] / lv[x] - 1) <= TOUCH for x in ('PDL', 'VAL'))
        else:
            hit = any(abs(h5[k] / lv[x] - 1) <= TOUCH for x in ('PDH', 'VAH'))
        (at if hit else away).append((e, -1 if d[k] > 0 else 1, k, day))

    def mk(rows):
        return [dict(entry=e, side=s, bar5=k, day=dy) for e, s, k, dy in ev_map.decluster(rows)]
    return dict(at=mk(at), away=mk(away))


def load_dev_hl(pattern=KLINES):
    """(o, h, l, c, v, tb) 1m grid from 2022-01-01 to 2024-05-31; months 2022-01..2024-05 only; missing = NaN."""
    rows = []
    for f in sorted(glob.glob(pattern)):
        tag = os.path.basename(f)[len('BTCUSDT-1m-'):-4][:7]
        if clocks.FIRST_MONTH <= tag <= clocks.LAST_MONTH:
            with open(f) as fh:
                for r in csv.reader(fh):
                    if r[0] != 'open_time':
                        rows.append((clocks._ts_ms(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]),
                                     float(r[5]), float(r[9])))
    a = np.array(rows, dtype=float)
    t0 = int(np.datetime64('2022-01-01T00:00', 'ms').astype('int64'))
    tend = int(np.datetime64(clocks.DEV_END + 'T23:59', 'ms').astype('int64'))
    a = a[(a[:, 0] >= t0) & (a[:, 0] <= tend)]
    out = np.full((6, (tend - t0) // 60000 + 1), np.nan)
    idx = ((a[:, 0] - t0) // 60000).astype(int)
    for k in range(6):
        out[k, idx] = a[:, 1 + k]
    return out


def cell(o, c, evs, h):
    st = ev_map.run_cell(o, c, evs, h)
    reg, ses = {}, {}
    for e in evs:
        net = ev_map.net_pct(ev_map.fwd_gross_pct(o, c, e['entry'], h), e['side'])
        reg.setdefault(ev_map.regime_label(c, e['entry'] // DAY_MIN), []).append(net)
        ses.setdefault(ev_map.session_of((e['entry'] % DAY_MIN) // 60), []).append(net)
    st['regime_mean'] = {k: float(np.mean(x)) for k, x in reg.items()}
    st['session_mean'] = {k: float(np.mean(x)) for k, x in ses.items()}
    return st


HDR = ['| Event | Horizon | n | mean net % | sd | t | share positive | placebo 1-99 % | session mix | Regime mix |',
       '|---|---|---|---|---|---|---|---|---|---|']


def row(name, hh, st):
    pb = '%+.3f..%+.3f' % st['placebo'] if 'placebo' in st else 'n/a'
    return '| %s | %dm | %d%s | %+.3f | %.3f | %.2f | %.1f %% | %s | %s | %s |' % (
        name, hh, st['n'], ' INSUFFICIENT_N' if st['label'] else '', st['mean'], st['sd'], st['t'], 100 * st['pos'], pb,
        ' '.join('%s %d' % kv for kv in st['sessions'].items()), ' '.join('%s %d' % kv for kv in st['regime'].items()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True)
    ap.add_argument('--klines', default=KLINES)
    a = ap.parse_args(argv)
    if a.split != 'dev':
        raise SystemExit('only --split dev is allowed (PREREG: VALIDATION/GAP/RESERVE/HOLDOUT not opened by this card)')
    if not glob.glob(a.klines):
        raise SystemExit('DATA_ABSENT: no 1m kline files at %s; nothing run, nothing fabricated' % a.klines)
    o, h, l, c, v, tb = load_dev_hl(a.klines)
    ev = b1_events(o, h, l, c, v, tb, start_bar5=ev_map.DEV_FIRST_MIN // 5)
    res = {}
    for name, evs in (('B1 at level', ev['at']), ('B1 away from level', ev['away'])):
        for hh in HORIZONS:
            res['%s %dm' % (name, hh)] = cell(o, c, evs, hh)
    L = ['# B1: BTC absorption at a prior-day level (PDH/PDL/VAH/VAL), DEV %s .. %s (card btc-of-level-auction-b1-run-1112)'
         % (ev_map.DEV_START, ev_map.DEV_END), '',
         'Frozen PREREG.md. Net = signed trade (against delta) forward return minus %.2f %% round trip (fees.py taker). '
         'Placebo = 1,000 draws seed 1112, same hour histogram / long-short count / 60-min de-clustering; band = mean net '
         '1st..99th pct. n floor %d (below: INSUFFICIENT_N, no loosening, no verdict). VALIDATION, GAP, RESERVE, HOLDOUT NOT '
         'OPENED, so no PASS/LEAD mark is possible in this card (needs VALIDATION).' % (ev_map.COST_PCT, NFLOOR), '',
         'The two cells (at level):', ''] + HDR
    L += [row('B1 at level', hh, res['B1 at level %dm' % hh]) for hh in HORIZONS]
    L += ['', 'Away-from-level contrast (reported, not marked; same flow thresholds, no matching-type level touch):', ''] + HDR
    L += [row('B1 away', hh, res['B1 away from level %dm' % hh]) for hh in HORIZONS]
    L += ['', '| Horizon | at-level mean net % | away mean net % | at minus away | level useful (at > away)? |',
          '|---|---|---|---|---|']
    for hh in HORIZONS:
        x, y = res['B1 at level %dm' % hh], res['B1 away from level %dm' % hh]
        L.append('| %dm | %+.3f | %+.3f | %+.3f | %s |' % (hh, x['mean'], y['mean'], x['mean'] - y['mean'],
                                                         'yes' if x['mean'] > y['mean'] else 'no'))
    L += ['', 'Mean net % by regime and session (at level; regime = trailing 90d return >+20 % bull, <-20 % bear, OURS):', '',
          '| Horizon | by regime | by session |', '|---|---|---|']
    for hh in HORIZONS:
        st = res['B1 at level %dm' % hh]
        L.append('| %dm | %s | %s |' % (hh, ' '.join('%s %+.3f' % kv for kv in st['regime_mean'].items()),
                                       ' '.join('%s %+.3f' % kv for kv in st['session_mean'].items())))
    L += ['', 'B2 unfinished auction at a 24h extreme: NOT_RUN (not failed). DEV aggTrades are not on disk and the fetch '
          '(100-400 GB to F:) needs operator approval; nothing fetched. Its two cells stay in the family count.']
    with open(os.path.join(HERE, 'B1.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    with open(os.path.join(HERE, 'results_b1.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    print('\n'.join(L))


if __name__ == '__main__':
    main()
