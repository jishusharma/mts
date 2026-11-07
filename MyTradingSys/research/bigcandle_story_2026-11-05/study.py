"""Big-candle stories: what price / OI / taker-delta spikes looked like, the top-trader read, and what followed, by phase.

Descriptive, fee-free: no entries, no costs, no edge claim. DEV window only (bars before 2024-07-01); the holdout is never read
for any table. The 2026-11-04 walk-through reads only the public days 2026-08-01..2026-11-04 (cache from fetch_data.py) and
prints events and base-rate lookups, never forward outcomes.
Data SOURCED: Binance USD-M BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines), metrics 5m (F:/MTS/data/binance_metrics).
Every threshold below = OURS, fixed in PRE_REG.md before the outcome columns were read.
Writes MyTradingSys/tools/live_aid/bigcandle_rates.js, tables.md and walkthrough.md next to this file.
"""
import csv
import glob
import json
import math
import os
from datetime import datetime, timezone

import numpy as np

KLINES = 'F:/MTS/data/tom_raw/klines'
METRICS = 'F:/MTS/data/binance_metrics'
CACHE = 'F:/MTS/data/bigcandle_cache'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JS = os.path.join(HERE, '..', '..', 'tools', 'live_aid', 'base_rates_input', 'bigcandle_rates.js')

M5 = 300000
DEV_T0 = int(datetime(2022, 1, 3, tzinfo=timezone.utc).timestamp() * 1000)    # Monday: weekly candles align
DEV_END = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)   # DEV only; VALIDATION/HOLDOUT never read
WALK_T0 = int(datetime(2026, 8, 3, tzinfo=timezone.utc).timestamp() * 1000)   # Monday
WALK_END = int(datetime(2026, 11, 5, tzinfo=timezone.utc).timestamp() * 1000)
Z_BIG = 3.0            # OURS: |z| >= 3 vs the trailing 30 days of the same-granularity series (prior bars only)
TRAIL_DAYS = 30        # OURS
TT_FLAT = 0.002        # OURS: |relative change of a top-trader ratio over the hour| < 0.2 % = FLAT
BAND = 0.10            # OURS: trailing 30-day return > +10 % bull, < -10 % bear, else range (as anticipation_map)
THIN = 30              # cells with n < 30 are THIN
HORIZONS = (('1h', 12), ('4h', 48), ('24h', 288))   # in 5m bars
LOCK5 = 12             # OURS: after a 5m event, skip 12 bars so the 1h outcome windows of 5m events never overlap


def ms(t):
    return datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%MZ')


def story_label(p, o, d):
    """The 8 anticipation_map stories from the signs of price, OI and taker delta change; None if any is zero/missing."""
    if not all(x is not None and math.isfinite(x) and x != 0 for x in (p, o, d)):
        return None
    return ('UP' if p > 0 else 'DOWN') + '|' + ('UP' if o > 0 else 'DOWN') + '|' + ('BUY' if d > 0 else 'SELL')


def tt_class(pos_rel, acc_rel):
    """Top-trader class over the event hour: positions ratio (size) vs accounts ratio (head count)."""
    if pos_rel is None or acc_rel is None or not (math.isfinite(pos_rel) and math.isfinite(acc_rel)):
        return 'NA'
    if abs(pos_rel) < TT_FLAT or abs(acc_rel) < TT_FLAT:
        return 'FLAT'
    return {(True, True): 'BU', (False, False): 'BD', (True, False): 'SL', (False, True): 'SS'}[(pos_rel > 0, acc_rel > 0)]


TT_NAMES = {'BU': 'both up (size and accounts longer)', 'BD': 'both down (size and accounts shorter)',
            'SL': 'size long / accounts short', 'SS': 'size short / accounts long', 'FLAT': 'flat', 'NA': 'missing'}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def streak_group(color, length):
    if color is None:
        return None
    if length >= 3:
        return 'R3+' if color == 'R' else 'G3+'
    return 'R1-2' if color == 'R' else 'G1-2'


# ---------------------------------------------------------------- data
def load_dev():
    """DEV 5m series on the grid [DEV_T0, DEV_END): o h l c v tb from 1m klines, oi tpos tacc from metrics."""
    sums = {}
    for f in sorted(glob.glob(os.path.join(KLINES, 'BTCUSDT-1m-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t < DEV_T0 or t >= DEV_END:
                    continue
                b = t // M5 * M5
                a = sums.setdefault(b, [0, None, -1e18, 1e18, None, 0.0, 0.0, 0])
                a[0] += 1
                a[2] = max(a[2], float(r[2]))
                a[3] = min(a[3], float(r[3]))
                a[5] += float(r[5])
                a[6] += float(r[9])
                if a[1] is None or t <= a[7]:
                    a[1], a[7] = float(r[1]), t     # open of the earliest 1m bar in the bucket
                if a[4] is None or t >= a[4][0]:
                    a[4] = (t, float(r[4]))         # close of the latest 1m bar
    k5 = {b: (a[1], a[2], a[3], a[4][1], a[5], a[6]) for b, a in sums.items() if a[0] == 5}
    met = {}
    for f in sorted(glob.glob(os.path.join(METRICS, 'BTCUSDT-metrics-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                t = int(datetime.strptime(r['create_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if t >= DEV_END or t < DEV_T0:
                    continue
                met[t] = _met_row(r)
    return grid(k5, met, DEV_T0, DEV_END)


def _met_row(r):
    def f(x):
        try:
            v = float(x)
        except (TypeError, ValueError):
            return float('nan')
        return v if v > 0 else float('nan')   # blank or 0 = missing
    return (f(r['sum_open_interest']), f(r['sum_toptrader_long_short_ratio']), f(r['count_toptrader_long_short_ratio']), f(r['count_long_short_ratio']))


def load_walk():
    k5, met = {}, {}
    for f in sorted(glob.glob(os.path.join(CACHE, 'k5', 'BTCUSDT-5m-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.reader(fh):
                if r and r[0].isdigit() and WALK_T0 <= int(r[0]) < WALK_END:
                    k5[int(r[0])] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9]))
    for f in sorted(glob.glob(os.path.join(CACHE, 'met', 'BTCUSDT-metrics-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                t = int(datetime.strptime(r['create_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if WALK_T0 <= t <= WALK_END:
                    met[t] = _met_row(r)
    return grid(k5, met, WALK_T0, WALK_END)


def grid(k5, met, t0, t1):
    n = (t1 - t0) // M5
    S = {k: np.full(n, np.nan) for k in ('o', 'h', 'l', 'c', 'v', 'tb', 'oi', 'tpos', 'tacc', 'gacc')}
    for t, row in k5.items():
        i = (t - t0) // M5
        if 0 <= i < n:
            for k, x in zip(('o', 'h', 'l', 'c', 'v', 'tb'), row):
                S[k][i] = x
    for t, row in met.items():          # stamp = bar CLOSE, so it belongs to the bar that opened 5 min earlier
        i = (t - M5 - t0) // M5
        if 0 <= i < n:
            for k, x in zip(('oi', 'tpos', 'tacc', 'gacc'), row):
                S[k][i] = x
    S['t0'], S['n'] = t0, n
    return S


# ---------------------------------------------------------------- features (point in time)
def trailing_z(x, w, need=0.8):
    """z of x[i] vs the mean/sd of x over the w bars BEFORE i (prior bars only); NaN when under 80 % of them are valid."""
    ok = np.isfinite(x)
    x0 = np.where(ok, x, 0.0)
    cs = np.concatenate(([0.0], np.cumsum(x0)))
    cs2 = np.concatenate(([0.0], np.cumsum(x0 * x0)))
    cn = np.concatenate(([0.0], np.cumsum(ok.astype(float))))
    z = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        c = cn[i] - cn[i - w]
        if c < need * w or not ok[i]:
            continue
        m = (cs[i] - cs[i - w]) / c
        v = (cs2[i] - cs2[i - w]) / c - m * m
        if v > 0:
            z[i] = (x[i] - m) / math.sqrt(v)
    return z


def features(S, gran):
    """gran '5m' or '1h': arrays indexed by bar; each bar has start index s5, end index e5 on the 5m grid."""
    n, w = S['n'], (1 if gran == '5m' else 12)
    nb = n // w
    e5 = np.arange(nb) * w + (w - 1)
    s5 = np.arange(nb) * w
    o = S['o'][s5]
    c = S['c'][e5]
    dp = c / o - 1
    oi_end = S['oi'][e5]
    doi = np.concatenate(([np.nan], np.diff(oi_end)))
    d5 = 2 * S['tb'] - S['v']
    delta = d5[:nb * w].reshape(nb, w).sum(axis=1)          # NaN if any 5m bar missing
    tw = TRAIL_DAYS * 288 // w
    return {'e5': e5, 's5': s5, 'o': o, 'c': c, 'dp': dp, 'doi': doi, 'delta': delta,
            'zp': trailing_z(dp, tw), 'zo': trailing_z(doi, tw), 'zd': trailing_z(delta, tw)}


def weekly(S):
    """Consecutive red/green weekly candles (Monday 00:00 UTC grid, from 5m futures bars): per week (color, run length)."""
    wk = 7 * 288
    nw = S['n'] // wk
    col = []
    for k in range(nw):
        a, b = S['o'][k * wk], S['c'][k * wk + wk - 1]
        col.append(None if not (np.isfinite(a) and np.isfinite(b)) else ('G' if b > a else 'R'))
    before, run = [], None      # before[k] = (color, length) of the run that ENDS at week k-1
    for k in range(nw):
        before.append(run)
        if col[k] is None:
            run = None
        elif run and run[0] == col[k]:
            run = (col[k], run[1] + 1)
        else:
            run = (col[k], 1)
    before.append(run)      # the current partial week
    return col, before


def phase_of(S, e5, wk_before):
    out = []
    for e in e5:
        band = None
        if e >= TRAIL_DAYS * 288 and np.isfinite(S['c'][e]) and np.isfinite(S['c'][e - TRAIL_DAYS * 288]):
            r = S['c'][e] / S['c'][e - TRAIL_DAYS * 288] - 1
            band = 'bull' if r > BAND else 'bear' if r < -BAND else 'range'
        k = int(e // (7 * 288))
        run = wk_before[k] if k < len(wk_before) else None
        out.append((band, streak_group(*run) if run else None))
    return out


def tt_of(S, e):
    if e < 12:
        return 'NA'
    rel = []
    for key in ('tpos', 'tacc'):
        a, b = S[key][e - 12], S[key][e]
        rel.append(b / a - 1 if np.isfinite(a) and np.isfinite(b) else None)
    return tt_class(rel[0], rel[1])


def outcomes(S, e, o_start, sgn):
    """Per horizon: (continued, undone) for an event ending at 5m index e. continued = close H later beyond the event close in the
    event direction; undone = close H later back past the event's start price. None when the horizon runs off the data."""
    res = {}
    for name, h in HORIZONS:
        j = e + h
        cf = S['c'][j] if j < S['n'] else np.nan
        if not np.isfinite(cf):
            res[name] = None
        else:
            res[name] = (bool((cf - S['c'][e]) * sgn > 0), bool((cf - o_start) * sgn < 0))
    return res


def build_events(S, gran, phase_all, wk_before, lock=0):
    F = features(S, gran)
    ev, last = [], -10 ** 9
    big = (np.abs(F['zp']) >= Z_BIG) | (np.abs(F['zo']) >= Z_BIG) | (np.abs(F['zd']) >= Z_BIG)
    for i in np.nonzero(big)[0]:
        st = story_label(F['dp'][i], F['doi'][i], F['delta'][i])
        if st is None or (lock and i - last < lock):
            continue
        last = i
        e = int(F['e5'][i])
        ev.append({'i': int(i), 'e': e, 's': int(F['s5'][i]), 'story': st, 'tt': tt_of(S, e), 'band': phase_all[e][0],
                   'streak': phase_all[e][1], 'dir': 'UP' if F['dp'][i] > 0 else 'DOWN',
                   'big': ''.join(k for k, z in (('P', F['zp'][i]), ('O', F['zo'][i]), ('D', F['zd'][i])) if abs(z) >= Z_BIG),
                   'out': outcomes(S, e, F['o'][i], 1 if F['dp'][i] > 0 else -1)})
    return ev, F


def baseline(S, F, phase_all):
    """Unconditional: every bar with a non-zero price change, same outcome definitions; cells by direction x phase."""
    rows = []
    for i in range(len(F['dp'])):
        d = F['dp'][i]
        if not np.isfinite(d) or d == 0:
            continue
        e = int(F['e5'][i])
        rows.append({'dir': 'UP' if d > 0 else 'DOWN', 'band': phase_all[e][0], 'streak': phase_all[e][1],
                     'out': outcomes(S, e, F['o'][i], 1 if d > 0 else -1)})
    return rows


def tally(rows, pred):
    """n and, per horizon, (k_continued, k_undone, n_valid) for rows matching pred."""
    sel = [r for r in rows if pred(r)]
    out = {'n': len(sel)}
    for name, _ in HORIZONS:
        v = [r['out'][name] for r in sel if r['out'][name] is not None]
        out[name] = (sum(x[0] for x in v), sum(x[1] for x in v), len(v))
    return out


def cell(t):
    d = {'n': t['n']}
    for name, _ in HORIZONS:
        kc, ku, nv = t[name]
        lo, hi = wilson(kc, nv)
        d[name] = {'nv': nv, 'cont': round(100 * kc / nv, 1) if nv else None, 'lo': round(100 * lo, 1), 'hi': round(100 * hi, 1),
                   'undone': round(100 * ku / nv, 1) if nv else None}
    return d


def run_dev():
    S = load_dev()
    assert S['t0'] + S['n'] * M5 <= DEV_END
    col, before = weekly(S)
    F1h = features(S, '1h')
    ph = phase_of(S, np.arange(S['n']), before)
    ev1, F1 = build_events(S, '1h', ph, before)
    ev5, F5 = build_events(S, '5m', ph, before, lock=LOCK5)
    base1 = baseline(S, F1, ph)
    base5 = baseline(S, F5, ph)
    return S, ev1, ev5, base1, base5, F1h


def keyed(ev, base):
    """Rates for the runtime: story, story|tt, story|tt|band, story|tt|streak, each with direction baselines per phase."""
    cells = {}
    keys = {}
    for r in ev:
        s, t, b, w = r['story'], r['tt'], r['band'], r['streak']
        keys.setdefault(s, []).append(r)
        if t not in ('NA', 'FLAT'):
            keys.setdefault(s + '|' + t, []).append(r)
            if b:
                keys.setdefault(s + '|' + t + '|band:' + b, []).append(r)
            if w:
                keys.setdefault(s + '|' + t + '|streak:' + w, []).append(r)
    for r in ev:                         # direction x top-trader class across all stories; DIRP = price itself big (P in `big`)
        if r['tt'] in ('NA', 'FLAT'):
            continue
        for pre, ok in (('DIR', True), ('DIRP', 'P' in r['big'])):
            if not ok:
                continue
            base_k = '%s|%s|%s' % (pre, r['dir'], r['tt'])
            keys.setdefault(base_k, []).append(r)
            if r['band']:
                keys.setdefault(base_k + '|band:' + r['band'], []).append(r)
            if r['streak']:
                keys.setdefault(base_k + '|streak:' + r['streak'], []).append(r)
    for k, rows in keys.items():
        cells[k] = cell(tally(rows, lambda r: True))
    bases = {}
    for d in ('UP', 'DOWN'):
        bases['BASE|' + d] = cell(tally(base, lambda r, d=d: r['dir'] == d))
        for b in ('bull', 'bear', 'range'):
            bases['BASE|%s|band:%s' % (d, b)] = cell(tally(base, lambda r, d=d, b=b: r['dir'] == d and r['band'] == b))
        for w in ('R3+', 'R1-2', 'G1-2', 'G3+'):
            bases['BASE|%s|streak:%s' % (d, w)] = cell(tally(base, lambda r, d=d, w=w: r['dir'] == d and r['streak'] == w))
    return cells, bases


def pct(c, h):
    x = c[h]
    if x['cont'] is None:
        return 'n/a'
    return '%.0f%% [%.0f-%.0f]' % (x['cont'], x['lo'], x['hi'])


def md_row(label, c):
    thin = ' THIN' if c['n'] < THIN else ''
    return '| %s | %d%s | %s | %s | %s | %.0f%% / %.0f%% / %.0f%% |' % (
        label, c['n'], thin, pct(c, '1h'), pct(c, '4h'), pct(c, '24h'),
        c['1h']['undone'] or 0, c['4h']['undone'] or 0, c['24h']['undone'] or 0)


HDR = '| Cell | n | continues 1h [95% CI] | continues 4h | continues 24h | undone 1h / 4h / 24h |\n|---|---|---|---|---|---|'


def tables(ev1, ev5, base1, base5):
    out = []
    for gran, ev, base in (('1h bars', ev1, base1), ('5m bars (60-min lockout)', ev5, base5)):
        cells, bases = keyed(ev, base)
        out.append('\n### Baseline, every %s bar (continue = same direction as the bar)\n\n%s' % (gran, HDR))
        for d in ('UP', 'DOWN'):
            out.append(md_row('all %s bars' % d, bases['BASE|' + d]))
            for b in ('bull', 'range', 'bear'):
                out.append(md_row('  %s, band %s' % (d, b), bases['BASE|%s|band:%s' % (d, b)]))
            for w in ('R3+', 'R1-2', 'G1-2', 'G3+'):
                out.append(md_row('  %s, streak %s' % (d, w), bases['BASE|%s|streak:%s' % (d, w)]))
        out.append('\n### By story, big %s (|z| >= 3 in price, OI or delta)\n\n%s' % (gran, HDR))
        for s in sorted(k for k in cells if k.count('|') == 2 and k[:3] not in ('DIR', 'BAS')):
            out.append(md_row(s, cells[s]))
        out.append('\n### Story x top-trader class, %s\n\n%s' % (gran, HDR))
        for s in sorted(k for k in cells if k.count('|') == 3 and k[:3] not in ('DIR', 'BAS')):
            out.append(md_row(s, cells[s]))
        for pre, ttl in (('DIRP', 'price itself big'), ('DIR', 'any big (price, OI or delta)')):
            out.append('\n### Direction x top-trader class, %s, %s, with phase splits\n\n%s' % (gran, ttl, HDR))
            for k in sorted(k for k in cells if k.startswith(pre + '|')):
                out.append(md_row(k, cells[k]))
        out.append('\n### Story x top-trader class x phase, %s (only cells with n >= %d)\n\n%s' % (gran, THIN, HDR))
        for s in sorted(k for k in cells if k.count('|') == 4 and cells[k]['n'] >= THIN and k[:3] not in ('DIR', 'BAS')):
            out.append(md_row(s, cells[s]))
    return '\n'.join(out), keyed(ev1, base1)


# ---------------------------------------------------------------- 2026-11-04 walk-through
def walkthrough(cells=None):
    S = load_walk()
    col, before = weekly(S)
    wk = 7 * 288
    lines = ['## Weekly candles (futures 5m grid, Monday 00:00 UTC; OURS)\n']
    for k, c in enumerate(col):
        a, b = S['o'][k * wk], S['c'][k * wk + wk - 1] if (k + 1) * wk <= S['n'] else np.nan
        lines.append('- week of %s: %s (%.0f -> %.0f)' % (ms(S['t0'] + k * wk * M5)[:10], c, a, b))
    nw = S['n'] // wk
    cur = S['n'] // wk
    k0 = S['n'] // wk
    # the current partial week (11-02): open vs last close
    pw = (S['n'] - 1) // wk
    last_valid = np.nonzero(np.isfinite(S['c']))[0][-1]
    lines.append('- partial week of %s: open %.0f, last close %.0f (%s)' % (
        ms(S['t0'] + pw * wk * M5)[:10], S['o'][pw * wk], S['c'][last_valid], 'G' if S['c'][last_valid] > S['o'][pw * wk] else 'R'))
    F5 = features(S, '5m')
    ph = phase_of(S, np.arange(S['n']), before)
    d0 = int(datetime(2026, 11, 4, tzinfo=timezone.utc).timestamp() * 1000)
    i0 = (d0 - S['t0']) // M5
    day = np.arange(i0, i0 + 288)
    # hand-read method: z vs THAT DAY'S sd (hindsight; reproduces the Eagle_Eyes read, never a rule)
    lines.append('\n## 2026-11-04 5m bars with |z| >= 3 (two methods)\n')
    lines.append('Phase at 11-04: band %s, streak group %s (weeks before 11-02: %s)' % (ph[i0][0], ph[i0][1], before[(i0 // wk)]))
    lines.append('\n| bar open (UTC) | method | price chg | OI chg (BTC) | taker delta (BTC) | story | top class (1h) | big in |\n|---|---|---|---|---|---|---|---|')
    sd = {k: np.nanstd(F5[k][day]) for k in ('dp', 'doi', 'delta')}
    mu = {k: np.nanmean(F5[k][day]) for k in ('dp', 'doi', 'delta')}
    rows_day, rows_trail = [], []
    for i in day:
        zs = {k: (F5[k][i] - mu[k]) / sd[k] for k in ('dp', 'doi', 'delta')}
        big_d = ''.join(c for c, k in (('P', 'dp'), ('O', 'doi'), ('D', 'delta')) if abs(zs[k]) >= Z_BIG)
        if big_d:
            rows_day.append((i, big_d))
        big_t = ''.join(c for c, k in (('P', 'zp'), ('O', 'zo'), ('D', 'zd')) if abs(F5[k][i]) >= Z_BIG)
        if big_t:
            rows_trail.append((i, big_t))
    for meth, rows in (('day-sd (hand read)', rows_day), ('trailing 30d', rows_trail)):
        for i, big in rows:
            lines.append('| %s | %s | %+.2f%% | %+.0f | %+.0f | %s | %s | %s |' % (
                ms(S['t0'] + int(i) * M5)[11:16], meth, 100 * F5['dp'][i], F5['doi'][i], F5['delta'][i],
                story_label(F5['dp'][i], F5['doi'][i], F5['delta'][i]), tt_of(S, int(i)), big))
    # the specific hand-read numbers
    def span(a, b):
        ia, ib = (a - S['t0']) // M5, (b - S['t0']) // M5
        return ia, ib
    def t_(h, m, day_=4):
        return int(datetime(2026, 11, day_, h, m, tzinfo=timezone.utc).timestamp() * 1000)
    lines.append('\n## Hand-read numbers re-computed\n')
    i = (t_(2, 55) - S['t0']) // M5
    lines.append('- 02:55 bar (close 03:00): price %.0f -> %.0f, OI %+.0f BTC, taker delta %+.0f BTC; day low %.0f at %s' % (
        S['o'][i], S['c'][i], F5['doi'][i], F5['delta'][i], np.nanmin(S['l'][day]), ms(S['t0'] + int(day[np.nanargmin(S['l'][day])]) * M5)))
    ia, ib = (t_(14, 35) - S['t0']) // M5, (t_(15, 10) - S['t0']) // M5
    ib_40 = (t_(14, 40) - S['t0']) // M5     # hand-read reproduction of a past day (hindsight by design, never a rule)
    lines.append('- 14:35-15:10 (bars opening 14:35..15:05, 7 bars): price %.0f -> %.0f, OI sum %+.0f BTC, delta sum %+.0f; 14:40 bar delta %+.0f' % (
        S['o'][ia], S['c'][ib - 1], np.nansum(F5['doi'][ia:ib]), np.nansum(F5['delta'][ia:ib]), F5['delta'][ib_40]))
    i_03 = (t_(3, 0) - S['t0']) // M5
    lines.append('- 02:55+03:00 two bars: close %.0f (bar open 03:00 close), OI %+.0f BTC, taker delta %+.0f BTC' % (
        S['c'][i_03], F5['doi'][i] + F5['doi'][i_03], F5['delta'][i] + F5['delta'][i_03]))
    big4 = [(t_(14, 35) - S['t0']) // M5, (t_(15, 0) - S['t0']) // M5, (t_(15, 5) - S['t0']) // M5, (t_(15, 10) - S['t0']) // M5]
    lines.append('- OI sum over the four big-OI bars 14:35, 15:00, 15:05, 15:10: %+.0f BTC' % sum(F5['doi'][k] for k in big4))
    ok = np.nonzero(np.isfinite(S['oi'][day]))[0]
    a, b = int(day[ok[0]]), int(day[ok[-1]])
    lines.append('- 03:00 bar close %.0f; 03:05 bar low %.0f' % (S['c'][(t_(3, 0) - S['t0']) // M5 - 1], S['l'][(t_(3, 5) - S['t0']) // M5]))
    lines.append('- day OI, first stamp %s to last stamp %s (11-05 file not yet published): %+.0f BTC' % (
        ms(S['t0'] + (a + 1) * M5)[11:16], ms(S['t0'] + (b + 1) * M5)[11:16], S['oi'][b] - S['oi'][a]))
    for key, nm in (('tpos', 'top-trader POSITIONS ratio'), ('tacc', 'top-trader ACCOUNTS ratio'), ('gacc', 'global ACCOUNTS ratio')):
        lines.append('- %s: %.2f -> %.2f' % (nm, S[key][a], S[key][b]))
    if cells:
        F1 = features(S, '1h')
        lines.append('\n## 11-04 big hours and the DEV cell each would show on the page (same pick order as live_aid: band, streak, story+class, story; n >= 30)\n')
        lines.append('| hour (UTC) | story | top class | band | streak | big in | cell used | n | continues 1h / 4h / 24h |\n|---|---|---|---|---|---|---|---|---|')
        for k in range(i0 // 12, i0 // 12 + 24):
            big = ''.join(c for c, z in (('P', F1['zp'][k]), ('O', F1['zo'][k]), ('D', F1['zd'][k])) if abs(z) >= Z_BIG)
            story = story_label(F1['dp'][k], F1['doi'][k], F1['delta'][k])
            if not big or not story:
                continue
            e = int(F1['e5'][k])
            tt = tt_of(S, e)
            band, stk = ph[e]
            keys = ([story + '|' + tt + '|band:' + str(band), story + '|' + tt + '|streak:' + str(stk), story + '|' + tt] if tt not in ('NA', 'FLAT') else []) + [story]
            pick = next((q for q in keys if q in cells and cells[q]['n'] >= THIN), None)
            c = cells.get(pick) if pick else None
            lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                ms(S['t0'] + int(F1['s5'][k]) * M5)[11:16], story, tt, band, stk, big, pick or 'none',
                c['n'] if c else '-', ' / '.join('%.0f%%' % c[h]['cont'] for h in ('1h', '4h', '24h')) if c else '-'))
    return '\n'.join(lines), S, F5, ph


def snapshot_thresholds():
    """Latest 30-day sd of 1h price / OI / delta from the cache, for the page's 'is this hour big' flag (snapshot, as of the last cached day)."""
    S = load_walk()
    F = features(S, '1h')
    w = TRAIL_DAYS * 24
    out = {}
    for k, nm in (('dp', 'p'), ('doi', 'o'), ('delta', 'd')):
        x = F[k][-w:]
        out[nm] = round(float(np.nanstd(x)), 6 if nm == 'p' else 1)
    return out, ms(S['t0'] + (S['n'] - 1) * M5)


def main():
    S, ev1, ev5, base1, base5, _ = run_dev()
    md, (cells, bases) = tables(ev1, ev5, base1, base5)
    band = {'bull': 0, 'bear': 0, 'range': 0, None: 0}
    stk = {}
    for r in ev1:
        band[r['band']] += 1
        stk[r['streak']] = stk.get(r['streak'], 0) + 1
    tot = sum(band.values())
    first, last = ev1[0]['e'], ev1[-1]['e']
    reg = 'Regime mix (1h events): bull %d%% / bear %d%% / range %d%%; streak groups %s' % (
        round(100 * band['bull'] / tot), round(100 * band['bear'] / tot), round(100 * band['range'] / tot), json.dumps(stk, sort_keys=True, default=str))
    ttmix = {}
    for r in ev1:
        ttmix[r['tt']] = ttmix.get(r['tt'], 0) + 1
    head = '# tables (generated by study.py; DEV %s .. %s)\n\n1h events %d, 5m events %d (lockout %d bars), 1h bars %d\n%s\nTop-trader mix (1h events): %s\n' % (
        ms(S['t0'])[:10], ms(S['t0'] + last * M5)[:10], len(ev1), len(ev5), LOCK5, len(base1), reg, json.dumps(ttmix, sort_keys=True))
    with open(os.path.join(HERE, 'tables.md'), 'w', newline='\n') as fh:
        fh.write(head + md + '\n')
    wt, _, _, _ = walkthrough({**cells, **bases})
    with open(os.path.join(HERE, 'walkthrough.md'), 'w', newline='\n') as fh:
        fh.write(wt + '\n')
    th, asof = snapshot_thresholds()
    meta = {'source': 'Binance USD-M BTCUSDT 1m klines + metrics 5m (OI, top-trader ratios)', 'range': [ms(S['t0'])[:10], '2024-06-30'],
            'events_1h': len(ev1), 'events_5m': len(ev5), 'zBig': Z_BIG, 'thin': THIN, 'ttFlat': TT_FLAT, 'band': BAND,
            'sd1h': th, 'sdAsOf': asof, 'note': 'DEV window, fee-free descriptive, 1h events; OURS thresholds in study.py'}
    os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
    with open(OUT_JS, 'w', newline='\n') as fh:
        fh.write('// built by research/bigcandle_story_2026-11-05/study.py; do not edit\n')
        fh.write('var BIGCANDLE_RATES = ' + json.dumps({'meta': meta, 'cells': {**cells, **bases}}, sort_keys=True, separators=(',', ':')) + ';\n')
    print(head)
    print(md)
    print(wt)


if __name__ == '__main__':
    main()
