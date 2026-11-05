# C31 multi-symbol (job c31-multi-sym-m2-1105; PRE_REG.md frozen first). Rule A of eagle_eyes_picture_2026-10-28/c31_halves.py,
# edge + trend down only, rerun unchanged on every USD-M 1m symbol under tom_raw (BTC, ETH), DEV window only, then pooled.
# Run: python study.py  (BTC reproduction gate first: exit 1 if the DEV row is not n=14 +/- 1)
import glob, csv, sys, os, json, statistics as st, datetime as dt, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'backtest'))
from fees import BINANCE_TAKER  # costs come from fees.py only
from splits import DEV_END as _DEV_END
DEV_END = _DEV_END.date()
HOLD = 20
RT_DRAG = 2 * BINANCE_TAKER * 1.2  # taker RT + 2 bps slip RT (FORMULAS section 13; slip OURS), same as c31_halves.py
SYMBOLS = [('BTCUSDT', 'F:/MTS/data/tom_raw/klines'), ('ETHUSDT', 'F:/MTS/data/tom_raw/klines_eth')]  # all present, max 6


def load(paths, end=DEV_END):
    """1m rows (t_sec, o, h, l, c) strictly before `end`; refuses any end past DEV."""
    if end > DEV_END:
        raise ValueError('DEV only: end %s is after %s' % (end, DEV_END))
    k = []
    for f in sorted(paths):
        for r in csv.reader(open(f)):
            if not r or r[0] == 'open_time':
                continue
            t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
            if dt.datetime.fromtimestamp(t, dt.timezone.utc).date() >= end:
                break
            k.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4])))
    k.sort()
    if k and dt.datetime.fromtimestamp(k[-1][0], dt.timezone.utc).date() >= DEV_END:
        raise ValueError('bar at or after DEV_END loaded')
    return k


def dev_files(folder, sym):
    """Monthly and daily 1m files whose name date is before DEV_END (later files are never opened)."""
    out = []
    for f in glob.glob(os.path.join(folder, '%s-1m-*.csv' % sym)):
        parts = os.path.basename(f)[:-4].split('-')[2:]
        y, m = int(parts[0]), int(parts[1])
        if dt.date(y, m, 1) < DEV_END:
            out.append(f)
    return out


def daily(k):
    """UTC daily candles [day_index, o, h, l, c, 1m path]."""
    B = []; cur = None
    for t, o, h, l, c in k:
        g = t // 86400
        if g != cur:
            B.append([g, o, h, l, c, []]); cur = g
        b = B[-1]; b[2] = max(b[2], h); b[3] = min(b[3], l); b[4] = c; b[5].append((t, o, h, l, c))
    return B


def bands(B):
    n = len(B); mid = [None] * n; up = [None] * n; sma = [None] * n
    for i in range(19, n):
        w = [b[4] for b in B[i - 19:i + 1]]; m = sum(w) / 20; sd = (sum((x - m) ** 2 for x in w) / 20) ** .5
        mid[i] = m; up[i] = m + 2 * sd
    for i in range(49, n):
        sma[i] = sum(b[4] for b in B[i - 49:i + 1]) / 50
    return mid, up, sma


def sim(e, stop, target, path):
    """SHORT. returns (hit, gross_R, net_R) or None."""
    dist = (stop - e) / e; tdist = (e - target) / e
    if dist <= 0 or tdist <= 0:
        return None
    hit = 'none'
    for t, o, h, l, c in path:
        if h >= stop:
            hit = 'STOP'; break
        if l <= target:
            hit = 'TGT'; break
    x = stop if hit == 'STOP' else target if hit == 'TGT' else path[-1][4]
    gross = (e - x) / e / dist
    return hit, gross, gross - RT_DRAG / dist


def trades(B):
    """Rule A, edge + trend down: list of (date, hit, gross_R, net_R, cost_R)."""
    mid, up, sma = bands(B); n = len(B); out = []
    for i in range(50, n - HOLD - 1):
        prev = B[i - 1]
        if not prev[4] < sma[i - 1]:
            continue
        if not any(B[j][4] > up[j] for j in range(i - 3, i)):
            continue
        ent = next((j for j, x in enumerate(B[i][5]) if x[3] < prev[4]), None)
        if ent is None:
            continue
        m1 = [x for b in B[i:i + HOLD] for x in b[5]]
        r = sim(prev[4], prev[2], mid[i - 1], m1[ent + 1:])
        if r:
            day = dt.datetime.fromtimestamp(B[i][0] * 86400, dt.timezone.utc).date()
            out.append((day,) + r + (r[1] - r[2],))
    return out


def regime_mix(B):
    """Share of days bull (close > rising SMA50) / bear (close < falling SMA50) / range (else). OURS."""
    _, _, sma = bands(B); c = {'bull': 0, 'bear': 0, 'range': 0}
    for i in range(50, len(B)):
        if B[i][4] > sma[i] > sma[i - 1]:
            c['bull'] += 1
        elif B[i][4] < sma[i] < sma[i - 1]:
            c['bear'] += 1
        else:
            c['range'] += 1
    tot = sum(c.values()) or 1
    return {k: round(100 * v / tot) for k, v in c.items()}


def row(xs):
    if not xs:
        return {'n': 0}
    ne = [x[3] for x in xs]
    return {'n': len(xs), 'tgt_pct': round(100 * sum(x[1] == 'TGT' for x in xs) / len(xs)),
            'gross_R': round(st.mean(x[2] for x in xs), 3), 'net_R': round(st.mean(ne), 3),
            'sd_R': round(st.stdev(ne), 3) if len(xs) > 1 else None, 'cost_R': round(st.mean(x[4] for x in xs), 3),
            'years': {str(y): sum(1 for x in xs if x[0].year == y) for y in sorted({x[0].year for x in xs})}}


def main():
    res = {}; pool = []
    for sym, folder in SYMBOLS:
        B = daily(load(dev_files(folder, sym)))
        xs = trades(B)
        res[sym] = dict(row(xs), regime_mix=regime_mix(B), days=len(B))
        print(sym, res[sym])
        if sym == 'BTCUSDT' and abs(len(xs) - 14) > 1:
            print('BTC reproduction FAILED: n=%d, shipped DEV-part n=14' % len(xs)); return 1
        pool += xs
    res['POOL'] = row(pool); print('POOL', res['POOL'])
    p = res['POOL']; t = p['net_R'] / (p['sd_R'] / len(pool) ** .5)
    res['POOL']['t'] = round(t, 2)
    gate = subprocess.run([sys.executable, os.path.join(HERE, '..', '..', '..', 'scripts', 'dev', 'prereg_gate.py'),
                           '--n', str(p['n']), '--sd', str(p['sd_R']), '--cost', str(p['cost_R']), '--m', 'auto',
                           '--new-cells', '1'], capture_output=True, text=True)
    res['gate'] = {'exit': gate.returncode, 'out': gate.stdout.strip()}
    print('gate exit', gate.returncode, gate.stdout.strip())
    res['verdict'] = ('UNDERPOWERED' if gate.returncode != 0 else
                      'POWERED + EDGE' if p['net_R'] > 0 and t >= 1.645 else 'POWERED + NO EDGE')
    print('VERDICT', res['verdict'])
    json.dump(res, open(os.path.join(HERE, 'summary.json'), 'w', newline='\n'), indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
