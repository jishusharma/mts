"""Standalone DEV-only diagnostic. See METHOD.md for frozen assumptions."""
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
DATA = Path('F:/MTS/data/orderflow_1m')
COST = .0006
RISK = 50.0
CAP = 20000.0


def levels(rows):
    profile = defaultdict(float)
    for row in rows:
        for cell in row['fp'].split('|'):
            p, b, s = map(float, cell.split(':'))
            profile[p] += b + s
    prices = sorted(profile)
    volumes = [profile[p] for p in prices]
    mid = int(np.argmax(volumes))
    lo = hi = mid
    total = volumes[mid]
    while total < .7 * sum(volumes):
        left = volumes[lo-1] if lo else -1
        right = volumes[hi+1] if hi+1 < len(prices) else -1
        if left >= right:
            lo -= 1
            total += volumes[lo]
        else:
            hi += 1
            total += volumes[hi]
    return sorted(set([min(float(r['l']) for r in rows),
                       max(float(r['h']) for r in rows),
                       prices[mid], prices[lo], prices[hi]]))


def signal(a, lev):
    for i in range(1, len(a)-2):
        for level in lev:
            side = 1 if a[i-1, 4] > level else -1
            if not (a[i, 3] <= level <= a[i, 2]):
                continue
            if not 0 < side * (a[i, 4] - level) <= .001 * level:
                continue
            entry = a[i+1, 1]
            targets = sorted([x for x in lev if side*(x-a[i, 4]) > 0],
                             key=lambda x: side*x)
            if not targets:
                continue
            t1 = targets[0]
            stop = level * (1 - side*.004)
            if side*(entry-stop) <= 0 or side*(t1-entry) < .004*entry:
                continue
            if side*(t1-a[i, 4]) < .004*a[i, 4]:
                continue
            t2 = targets[1] if len(targets) > 1 else entry+2*(t1-entry)
            return i+1, side, level, stop, t1, t2
    return None


def run(a, sig, mode, ladder):
    start, side, level, stop, t1, t2 = sig
    entry = a[start, 1]
    width = side*(entry-stop)
    weights = [1] if mode == 'single' else ([1, 1, 1] if mode == 'equal_dip' else [1, 2, 3])
    direction = 1 if mode == '123_confirm' else -1
    planned = [entry+side*direction*.25*k*width for k in range(len(weights))]
    unit = RISK / sum(w*(side*(p-stop)+COST*(p+stop)) for w, p in zip(weights, planned))
    qty = basis = pnl = fees = funding = 0.0
    added = 0
    pending_add = True
    pending_exit = False
    first = second = False
    original = 0.0
    peak = 0.0
    fills = []

    def close(q, p, reason, t):
        nonlocal qty, basis, pnl, fees
        q = min(q, qty)
        if q <= 0:
            return
        pnl += side*q*(p-basis/qty)-COST*q*p
        fees += COST*q*p
        basis *= (qty-q)/qty
        qty -= q
        fills.append([int(t), reason, float(q), float(p)])

    for i in range(start, len(a)):
        t, op, hi, low, cl, delta = a[i]
        # Gap/stop first; a pending add cannot precede protection.
        if qty and side*(op-stop) <= 0:
            close(qty, op, 'gap_stop', t)
            break
        if pending_exit and qty:
            close(qty, op, 'indicator', t)
            break
        if pending_add and added < len(weights) and not first:
            if side*(op-stop) > 0 and side*(t1-op) > 0:
                current_stop_pnl = pnl + side*(qty*stop-basis)-COST*qty*stop
                room = max(0, RISK+current_stop_pnl)
                q = min(weights[added]*unit,
                        room/(side*(op-stop)+COST*(op+stop)),
                        max(0, CAP/op-qty))
                if q > 0:
                    qty += q
                    basis += q*op
                    pnl -= COST*q*op
                    fees += COST*q*op
                    fills.append([int(t), 'entry', float(q), float(op)])
                    peak = max(peak, qty*op)
                added += 1
            pending_add = False
        if not qty:
            break
        cost = qty*op*.0001/480
        pnl -= cost
        funding += cost
        if (low <= stop if side == 1 else hi >= stop):
            close(qty, stop, 'stop', t)
            break
        if not first and (hi >= t1 if side == 1 else low <= t1):
            if not ladder:
                close(qty, t1, 'target', t)
                break
            first = True
            original = qty
            close(original*.5, t1, 'target1', t)
        if first and not second and (hi >= t2 if side == 1 else low <= t2):
            second = True
            close(original*.25, t2, 'target2', t)
        if first:
            closes = a[max(0, i-19):i+1, 4]
            bb = closes.mean()+side*2*closes.std()
            adverse = side*a[max(0, i-4):i+1, 5].sum() < 0
            pending_exit = adverse or (len(closes) == 20 and side*(cl-bb) >= 0)
        elif added < len(weights):
            pending_add = direction*side*(cl-entry) >= .25*added*width
        if i == len(a)-1:
            close(qty, cl, 'day_end', t)
    return dict(pnl=pnl, r=pnl/RISK, fees_slip=fees, funding_stress=funding,
                entries=sum(f[1] == 'entry' for f in fills), peak_notional=peak,
                fills=fills)


def main():
    paths = sorted(p for p in DATA.glob('*.csv.gz') if '2024-12-01' <= p.name[:10] <= '2025-03-31')
    previous = None
    previous_day = None
    records, manifest, coverage = [], [], []
    for path in paths:
        with gzip.open(path, 'rt', newline='') as stream:
            rows = list(csv.DictReader(stream))
        a = np.array([[float(r[k]) for k in ['t', 'o', 'h', 'l', 'c', 'delta']] for r in rows])
        day = np.datetime64(path.name[:10], 'D')
        complete = len(a) == 1440 and np.all(np.diff(a[:, 0]) == 60000)
        complete = bool(complete and a[0, 0] == int(day.astype('int64'))*86400000)
        coverage.append(dict(day=str(day), rows=len(a), complete=complete))
        manifest.append(dict(file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        if complete and previous is not None and day-previous_day == np.timedelta64(1, 'D'):
            lev = levels(previous)
            sig = signal(a, lev)
            if sig:
                for mode in ['single', 'equal_dip', '123_dip', '123_confirm']:
                    for ladder in [False, True]:
                        result = run(a, sig, mode, ladder)
                        records.append(dict(day=str(day), arm=mode+('_staged' if ladder else '_full'),
                                            side=sig[1], level=sig[2], **result))
        previous, previous_day = (rows if complete else None), day
    arms = sorted(set(r['arm'] for r in records))
    baseline = np.array([r['r'] for r in records if r['arm'] == 'single_full'])
    rng = np.random.default_rng(42)
    indices = rng.integers(0, len(baseline), (2000, len(baseline)))
    summary = []
    for arm in arms:
        subset = [r for r in records if r['arm'] == arm]
        values = np.array([r['r'] for r in subset])
        curve = np.r_[0, np.cumsum(values)]
        ci = np.percentile((values-baseline)[indices].mean(axis=1), [2.5, 97.5])
        summary.append(dict(arm=arm, n=len(values), mean_r=float(values.mean()),
                            total_usd=float(values.sum()*RISK), win_pct=float((values>0).mean()*100),
                            max_dd_usd=float(max(np.maximum.accumulate(curve)-curve)*RISK),
                            mean_entries=float(np.mean([r['entries'] for r in subset])),
                            max_notional=max(r['peak_notional'] for r in subset),
                            paired_difference_ci=ci.tolist(),
                            monthly_mean_r={m:float(np.mean([r['r'] for r in subset if r['day'].startswith(m)]))
                                            for m in sorted(set(r['day'][:7] for r in subset))}))
    payload = dict(summary=summary, coverage=coverage, manifest=manifest,
                   trials=8, validation_read=False, records=records)
    with open(OUT/'results.json', 'w', newline='\n') as stream:
        json.dump(payload, stream, indent=2)
    print(json.dumps(dict(summary=summary, files=len(paths), complete_days=sum(r['complete'] for r in coverage)), indent=2))


if __name__ == '__main__':
    main()
