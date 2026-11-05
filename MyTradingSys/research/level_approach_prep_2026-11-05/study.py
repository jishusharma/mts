"""Level-approach prep base rates: U1 absorption, U2 OI tell, U3 wick-rejection TF count (card level-approach-prep).

Descriptive, fee-free: no entries, no costs, no edge claim. DEV window only (bars before 2024-07-01).
Data SOURCED: Binance USD-M BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines), Binance metrics 5m sum_open_interest
(F:/MTS/data/binance_metrics). Every threshold below = OURS, fixed in PRE_REG.md before the run.
Writes MyTradingSys/tools/live_aid/level_approach_rates.js and prints the RESULT tables.
"""
import csv
import glob
import json
import os
from datetime import datetime, timezone

KLINES = 'F:/MTS/data/tom_raw/klines'
METRICS = 'F:/MTS/data/binance_metrics'
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # DEV only; VALIDATION/HOLDOUT never read
M, DAY = 60000, 86400000
ZONE = 0.003      # OURS: approach zone, 0.3 % from the level
ABS_DS = 0.3      # OURS: absorption delta share toward the level
ABS_EXT = 0.001   # OURS: absorption = extension under 0.1 % over the next 3 bars
BREAK = 0.001     # OURS: a 1m close 0.1 % beyond the level = break
REV = 0.005       # OURS: 0.5 % back from the base close = reversal
FWD = 60          # OURS: follow-up bars
OI_FLAT = 0.001   # OURS: OI change under 0.1 % = FLAT (same as live_aid OM.flat)
WICK = 0.5        # OURS: wick toward the level >= 50 % of the bar range
TFS = (1, 2, 3, 5)
REGIME = 0.10     # OURS: trailing 30-day return > +10 % bull, < -10 % bear, else range
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JS = os.path.join(HERE, '..', '..', 'tools', 'live_aid', 'level_approach_rates.js')


def load_klines(symbol='BTCUSDT'):
    """1m (open, high, low, close, volume, taker buy volume) by open_time ms; refuses rows at or after DEV_END_MS."""
    bars = {}
    for f in sorted(glob.glob(os.path.join(KLINES, symbol + '-1m-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t >= DEV_END_MS:
                    continue
                bars[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9]))
    return bars


def load_oi(symbol='BTCUSDT'):
    oi = {}
    for f in sorted(glob.glob(os.path.join(METRICS, symbol + '-metrics-*.csv'))):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                t = int(datetime.strptime(r['create_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)
                if t >= DEV_END_MS or not r['sum_open_interest'] or float(r['sum_open_interest']) <= 0:
                    continue  # zero OI rows = feed gaps, treated as missing
                oi[t] = float(r['sum_open_interest'])
    return oi


def span(bars, t0, n):
    out = [bars.get(t0 + i * M) for i in range(n)]
    return None if any(b is None for b in out) else out


def day_hl(bars, d0):
    day = span(bars, d0, 1440)
    return None if day is None else (max(b[1] for b in day), min(b[2] for b in day))


def outcome(bars, t_base, close, level, up):
    """From the base close: reversal (0.5 % back) before any break close (0.1 % beyond the level)? Returns (rev, brk) or None."""
    fwd = span(bars, t_base + M, FWD)
    if fwd is None:
        return None
    for b in fwd:
        if (b[3] > level * (1 + BREAK)) if up else (b[3] < level * (1 - BREAK)):
            return False, True
        if (b[2] <= close * (1 - REV)) if up else (b[1] >= close * (1 + REV)):
            return True, False
    return False, False


def oi_tell(oi, t):
    a = (t - 2 * M) // 300000 * 300000 - 300000
    b = (t + 4 * M) // 300000 * 300000
    if a not in oi or b not in oi:
        return None
    d = oi[b] / oi[a] - 1
    return 'FLAT' if abs(d) < OI_FLAT else ('UP' if d > 0 else 'DOWN')


def bucket(dist):
    return 'beyond' if dist < 0 else '0-0.1' if dist < 0.001 else '0.1-0.2' if dist < 0.002 else '0.2+'


def approaches(bars, oi, d0, level, up):
    """U1/U2 event for one level on one day, or None."""
    first = bars.get(d0)
    if first is None or ((first[0] >= level * (1 - ZONE)) if up else (first[0] <= level * (1 + ZONE))):
        return None
    for i in range(3, 1440):
        t = d0 + i * M
        b = bars.get(t)
        if b is None:
            return None
        if not ((b[1] >= level * (1 - ZONE)) if up else (b[2] <= level * (1 + ZONE))):
            continue
        push, nxt = span(bars, t - 2 * M, 3), span(bars, t + M, 3)
        if push is None or nxt is None:
            return None
        v = sum(x[4] for x in push)
        if v <= 0:
            return None
        ds = sum(2 * x[5] - x[4] for x in push) / v * (1 if up else -1)
        c = b[3]
        ext = (max(x[1] for x in nxt) / c - 1) if up else (1 - min(x[2] for x in nxt) / c)
        o = outcome(bars, t + 3 * M, nxt[-1][3], level, up)
        if o is None:
            return None
        dist = (level - c) / level if up else (c - level) / level
        return {'t': t, 'ds': ds, 'ext': ext, 'abs': ds >= ABS_DS and ext < ABS_EXT, 'rev': o[0], 'brk': o[1],
                'bucket': bucket(dist), 'oi': oi_tell(oi, t)}
    return None


def wick_tfs(bars, u, level, up):
    """Number of TFs (1/2/3/5m) with a wick rejection in the closed bars fully inside [u-15 min, u)."""
    cnt = 0
    for tf in TFS:
        ms = tf * M
        start = ((u - 15 * M) + ms - 1) // ms * ms
        hit = False
        for s in range(start, u - ms + 1, ms):
            sub = span(bars, s, tf)
            if sub is None:
                continue
            o, h, lo, c = sub[0][0], max(x[1] for x in sub), min(x[2] for x in sub), sub[-1][3]
            rng = h - lo
            if rng <= 0:
                continue
            near = (h >= level * (1 - ZONE)) if up else (lo <= level * (1 + ZONE))
            wick = (h - max(o, c)) if up else (min(o, c) - lo)
            if near and wick >= WICK * rng:
                hit = True
                break
        cnt += hit
    return cnt


def touch(bars, d0, level, up):
    """U3 event: first 1m bar reaching the level; (tf_count, hold) or None."""
    first = bars.get(d0)
    if first is None or ((first[0] >= level * (1 - ZONE)) if up else (first[0] <= level * (1 + ZONE))):
        return None
    for i in range(15, 1440):
        u = d0 + i * M
        b = bars.get(u)
        if b is None:
            return None
        if not ((b[1] >= level) if up else (b[2] <= level)):
            continue
        fwd = span(bars, u, FWD)
        if fwd is None:
            return None
        brk = any((x[3] > level * (1 + BREAK)) if up else (x[3] < level * (1 - BREAK)) for x in fwd)
        return wick_tfs(bars, u, level, up), not brk
    return None


def regime_of(close_by_day, t):
    day = t // DAY
    a, b = close_by_day.get(day - 30), close_by_day.get(day)
    if a is None or b is None:
        return 'range'
    r = b / a - 1
    return 'bull' if r > REGIME else 'bear' if r < -REGIME else 'range'


def pct(k, n):
    return round(100 * k / n) if n else None


def tables(evs, touches):
    ab = [e for e in evs if e['abs']]
    non = [e for e in evs if not e['abs']]
    mix = {}
    for e in ab:
        mix[e['bucket']] = mix.get(e['bucket'], 0) + 1
    matched, w = 0.0, 0
    for bk, k in mix.items():
        nb = [e for e in non if e['bucket'] == bk]
        if nb:
            matched += k * sum(e['rev'] for e in nb) / len(nb)
            w += k
    u1 = {'abs': {'n': len(ab), 'rev': pct(sum(e['rev'] for e in ab), len(ab)), 'brk': pct(sum(e['brk'] for e in ab), len(ab))},
          'non': {'n': len(non), 'rev': pct(sum(e['rev'] for e in non), len(non)), 'brk': pct(sum(e['brk'] for e in non), len(non))},
          'nonMatched': round(100 * matched / w) if w else None, 'all': len(evs)}
    u2 = {}
    for s in ('UP', 'FLAT', 'DOWN'):
        g = [e for e in ab if e['oi'] == s]
        u2[s] = {'n': len(g), 'rev': pct(sum(e['rev'] for e in g), len(g))}
    u3 = {}
    for k in ('0', '1', '2', '3+'):
        g = [h for c, h in touches if (str(c) if c < 3 else '3+') == k]
        u3[k] = {'n': len(g), 'hold': pct(sum(g), len(g))}
    return u1, u2, u3


def main():
    bars = load_klines()
    oi = load_oi()
    assert max(bars) < DEV_END_MS and max(oi) < DEV_END_MS
    days = sorted({t // DAY * DAY for t in bars})
    evs, touches, reg = [], [], {'bull': 0, 'bear': 0, 'range': 0}
    close_by_day = {}
    for t in sorted(bars):
        close_by_day[t // DAY] = bars[t][3]
    for d0 in days:
        hl = day_hl(bars, d0 - DAY)
        if hl is None:
            continue
        for level, up in ((hl[0], True), (hl[1], False)):
            e = approaches(bars, oi, d0, level, up)
            if e:
                evs.append(e)
                reg[regime_of(close_by_day, e['t'])] += 1
            x = touch(bars, d0, level, up)
            if x:
                touches.append(x)
    u1, u2, u3 = tables(evs, touches)
    first = datetime.fromtimestamp(evs[0]['t'] / 1000, timezone.utc).strftime('%Y-%m-%d')
    last = datetime.fromtimestamp(evs[-1]['t'] / 1000, timezone.utc).strftime('%Y-%m-%d')
    meta = {'source': 'Binance USD-M BTCUSDT 1m klines + metrics 5m OI', 'range': [first, last], 'approaches': len(evs), 'touches': len(touches),
            'zone': ZONE, 'absDs': ABS_DS, 'absExt': ABS_EXT, 'note': 'DEV window, fee-free descriptive; OURS thresholds in study.py'}
    with open(OUT_JS, 'w', newline='\n') as fh:
        fh.write('// built by research/level_approach_prep_2026-11-05/study.py; do not edit\n')
        fh.write('var LEVEL_APPROACH_RATES = ' + json.dumps({'meta': meta, 'u1': u1, 'u2': u2, 'u3': u3}, sort_keys=True) + ';\n')
    tot = sum(reg.values())
    print('approaches', len(evs), 'touches', len(touches), first, last)
    print('Regime mix: bull %d%% / bear %d%% / range %d%%' % tuple(round(100 * reg[x] / tot) for x in ('bull', 'bear', 'range')))
    print('U1', json.dumps(u1, sort_keys=True))
    print('U2', json.dumps(u2, sort_keys=True))
    print('U3', json.dumps(u3, sort_keys=True))


if __name__ == '__main__':
    main()
