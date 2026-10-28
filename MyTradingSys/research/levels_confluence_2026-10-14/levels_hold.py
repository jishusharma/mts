"""First-touch level reactions against a touched-only, distance-matched random-line control (T05-F5).

Verdict control (FAIR, T05-F5, ported from dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py): for every candidate level
of a family (touched or not), FAIR_K random lines whose distance from the midnight open is drawn from that family's own
distances in the same calendar month, random sign, never the real level itself (redrawn), and a line counts only when it is
touched, like a real level (control hold rate = holds / touches). KEEP = lower 95% day-bootstrap CI of
(real hold rate - control hold rate) > 0, both as ratios of sums.
Legacy control (published 2026-10-15, kept as labelled legacy_* / random_* columns): midnight +/- the level's own distance with
a random sign (half the draws ARE the real level) and an untouched line counts as a non-hold. Not used for the verdict.
"""
from collections import defaultdict
import datetime as dt
import math
import random

import numpy as np

DAY_MS = 86_400_000
SEED = 20261014
BOOTSTRAPS = 2000
FAIR_SEED = 20261016        # OURS (T05 audit seed)
FAIR_K = 20                 # OURS (T05 audit: control lines per candidate level)
FAIR_MAX_REDRAW = 100       # OURS: a line that keeps landing on the real level is dropped after this many draws


def stop_width(price, level):
    return max(.004 * float(price), .001 * abs(float(level)))


def _touch_side(bar, level, prev_close=None):
    """Side from the PREVIOUS bar's close (Q79: the touch bar's own close is look-ahead).

    Price above the level before the touch => level is support => side +1.
    No previous bar (first bar of the day): fall back to the touch bar's open.
    """
    if float(bar['l']) <= level <= float(bar['h']):
        ref = float(prev_close) if prev_close is not None else float(bar['o'])
        return 1 if ref >= level else -1
    return None


def outcome(bars, level, width, prev_close=None):
    """HOLD if a full width reaction precedes a full width penetration.

    Q79: side comes from the previous bar's close; the touch bar itself earns no
    favourable (HOLD) credit, only adverse (BREAK) credit.
    """
    touched = False
    side = None
    for b in bars:
        h, lo = float(b['h']), float(b['l'])
        first_bar = False
        if not touched:
            side = _touch_side(b, level, prev_close)
            if side is None:
                continue
            touched = True
            first_bar = True
        favorable = (h >= level + width) if side == 1 else (lo <= level - width)
        adverse = (lo <= level - width) if side == 1 else (h >= level + width)
        if adverse:
            return 'BREAK'
        if favorable and not first_bar:
            return 'HOLD'
    return 'NEITHER'


def _prev_close(rows, i):
    return float(rows[i - 1]['c']) if i > 0 else None


def _bootstrap_ci(day_diffs, seed=SEED, iterations=BOOTSTRAPS):
    if not day_diffs:
        return None
    rng = random.Random(seed)
    vals = []
    keys = sorted(day_diffs)
    for _ in range(iterations):
        sampled = [keys[rng.randrange(len(keys))] for _ in keys]
        num = sum(day_diffs[d][0] for d in sampled)
        den = sum(day_diffs[d][1] for d in sampled)
        vals.append(num / den if den else 0.0)
    vals.sort()
    return vals[int(.025 * iterations)], vals[min(iterations - 1, int(.975 * iterations))]


def _month_of(day):
    d = dt.date(1970, 1, 1) + dt.timedelta(days=int(day))
    return d.year * 12 + d.month


def _fair_boot_ci(days, seed=FAIR_SEED, iterations=BOOTSTRAPS):
    """days: {day: [real_hold, real_n, ctl_hold, ctl_n]}. Ratio-of-sums day bootstrap of real rate - control rate."""
    keys = sorted(days)
    if not keys:
        return None
    arr = np.array([days[k] for k in keys], float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(keys), (iterations, len(keys)))
    s = arr[pick].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        diff = s[:, 0] / s[:, 1] - s[:, 2] / s[:, 3]
    diff = diff[~np.isnan(diff)]
    if not len(diff):
        return None
    return float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))


def fair_control(by_day, levels, seed=FAIR_SEED, k=FAIR_K, exclude_real=True):
    """Touched-only distance-matched control for every candidate level (module docstring).

    by_day: {day: bars sorted by t}. Returns (acc, events, legacy_diag):
      acc[family][day] = [real_hold, real_touches, ctl_hold, ctl_touches] (a day appears once anything touched),
      events = one row per candidate level with its `controls` [(price, outcome or None if untouched)],
      legacy_diag[family] = [levels, legacy-style draws that are untouched, legacy-style draws equal to the real level].
    exclude_real=False reproduces t05_lc1.py draw for draw (its lines may equal the real level).
    """
    pool = defaultdict(list)
    for day, rows in by_day.items():
        mid = float(rows[0]['o'])
        for lv in levels.get(day, []):
            pool[(lv['family'], _month_of(day))].append(abs(float(lv['price']) - mid))
    rng = random.Random(seed)
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    diag = defaultdict(lambda: [0, 0, 0])
    events = []
    for day in sorted(by_day):
        rows = by_day[day]
        mid = float(rows[0]['o'])
        lo = np.array([float(b['l']) for b in rows])
        hi = np.array([float(b['h']) for b in rows])

        def one(p):
            idx = np.nonzero((lo <= p) & (p <= hi))[0]
            if len(idx) == 0:
                return None
            i = int(idx[0])
            return outcome(rows[i:], p, stop_width(mid, p), _prev_close(rows, i))

        for lv in levels.get(day, []):
            fam = lv['family']
            price = float(lv['price'])
            ps = pool[(fam, _month_of(day))]
            real = one(price)
            controls = []
            for _ in range(k):
                for _try in range(FAIR_MAX_REDRAW if exclude_real else 1):
                    dist = ps[rng.randrange(len(ps))]
                    p = mid + (-1 if rng.random() < .5 else 1) * dist
                    if not (exclude_real and abs(p - price) < 1e-9):
                        break
                else:
                    continue                      # every redraw hit the real level: no line
                r = one(p)
                controls.append((p, r))
                if r is not None:
                    acc[fam][day][2] += int(r == 'HOLD')
                    acc[fam][day][3] += 1
            if real is not None:
                acc[fam][day][0] += int(real == 'HOLD')
                acc[fam][day][1] += 1
            o = diag[fam]
            o[0] += 1
            dist = abs(price - mid)
            for _ in range(5):                    # legacy-style draws, diagnostic only
                pp = mid + (-1 if rng.random() < .5 else 1) * dist
                o[2] += int(abs(pp - price) < 1e-9)
                o[1] += int(one(pp) is None)
            events.append({'day': day, 'family': fam, 'level': price, 'outcome': real, 'controls': controls})
    return acc, events, diag


def analyze(bars, levels, seed=SEED, fair_seed=FAIR_SEED, exclude_real=True):
    """Analyze each day's level rows; `bars` should contain DEV only. Verdict = fair control; legacy columns kept."""
    by_day = defaultdict(list)
    for b in bars:
        by_day[int(b['t']) // DAY_MS].append(b)
    for rows in by_day.values():
        rows.sort(key=lambda b: b['t'])
    rng = random.Random(seed)
    family = defaultdict(lambda: {'n': 0, 'hold': 0, 'random_hold': 0, 'days': defaultdict(lambda: [0, 0])})
    touches, pairs = [], []
    for day in sorted(by_day):
        rows = by_day[day]
        if not rows:
            continue
        midnight = float(rows[0]['o'])
        events = []
        for lev in levels.get(day, []):
            price = float(lev['price'])
            first = next((i for i, b in enumerate(rows) if float(b['l']) <= price <= float(b['h'])), None)
            if first is None:
                continue
            width = stop_width(midnight, price)
            res = outcome(rows[first:], price, width, _prev_close(rows, first))
            dist = abs(price - midnight)
            controls = []
            for _ in range(5):
                sign = -1 if rng.random() < .5 else 1
                random_price = midnight + sign * dist
                rand_first = next((i for i, b in enumerate(rows)
                                   if float(b['l']) <= random_price <= float(b['h'])), None)
                controls.append(outcome(rows[rand_first:], random_price, stop_width(midnight, random_price),
                                        _prev_close(rows, rand_first))
                                if rand_first is not None else 'NO_TOUCH')
            real_hold = int(res == 'HOLD')
            # A control line never touched in the day is NEITHER, hence not a hold.
            random_hold = sum(x == 'HOLD' for x in controls) / 5
            stat = family[lev['family']]
            stat['n'] += 1
            stat['hold'] += real_hold
            stat['random_hold'] += random_hold
            stat['days'][day][0] += real_hold - random_hold
            stat['days'][day][1] += 1
            event = {'day': day, 'level': price, 'family': lev['family'], 'side': 1 if price > midnight else -1,
                     'touch_index': first, 'outcome': res}
            events.append(event)
            touches.append(event)
        # Next farther level in the same trade direction; level must be a KEEP candidate in caller's frozen set.
        for e in events:
            candidates = [x for x in levels.get(day, [])
                          if ((1 if float(x['price']) > midnight else -1) == e['side'] and
                              (float(x['price']) - e['level']) * e['side'] > 0)]
            if not candidates:
                continue
            l2 = min(candidates, key=lambda x: abs(float(x['price']) - e['level']))
            l2_price = float(l2['price'])
            later = rows[e['touch_index'] + 1:]
            l2_idx = next((i for i, b in enumerate(later) if float(b['l']) <= l2_price <= float(b['h'])), None)
            back = False
            if l2_idx is not None:
                back = any(float(b['l']) <= e['level'] <= float(b['h']) for b in later[l2_idx + 1:])
            pairs.append({'day': day, 'l1_family': e['family'], 'l1': e['level'], 'l2_family': l2['family'],
                          'l2': l2_price, 'distance_pct': abs(l2_price - e['level']) / e['level'] * 100,
                          'l2_touched': l2_idx is not None, 'returned_l1': back})
    summary = {}
    for name, s in family.items():
        diff_by_day = s['days']
        ci = _bootstrap_ci(diff_by_day)
        summary[name] = {'n': s['n'], 'hold_rate': s['hold'] / s['n'],
                         'random_hold_rate': s['random_hold'] / s['n'],
                         'difference': (s['hold'] - s['random_hold']) / s['n'], 'ci95': ci,
                         'legacy_verdict': 'KEEP' if ci and ci[0] > 0 else 'DROP'}
    acc, fair_events, diag = fair_control(by_day, levels, seed=fair_seed, exclude_real=exclude_real)
    for name in set(summary) | set(acc):
        row = summary.setdefault(name, {'n': 0, 'hold_rate': None, 'random_hold_rate': None, 'difference': None,
                                        'ci95': None, 'legacy_verdict': 'DROP'})
        d = acc.get(name, {})
        rh = sum(v[0] for v in d.values()); rn = sum(v[1] for v in d.values())
        ch = sum(v[2] for v in d.values()); cn = sum(v[3] for v in d.values())
        ctl = ch / cn if cn else None
        diff = rh / rn - ctl if rn and ctl is not None else None
        ci = _fair_boot_ci(d, seed=fair_seed) if rn and cn else None
        o = diag.get(name, [0, 0, 0])
        row.update({'fair_ctl_touches': cn, 'fair_ctl_hold_rate': ctl, 'fair_difference': diff, 'fair_ci95': ci,
                    'fair_verdict': 'KEEP' if ci and ci[0] > 0 else 'DROP',
                    'legacy_ctl_equal_real_share': o[2] / (5 * o[0]) if o[0] else None,
                    'legacy_ctl_untouched_share': o[1] / (5 * o[0]) if o[0] else None})
        row['verdict'] = row['fair_verdict']
    kept = {name for name, row in summary.items() if row['verdict'] == 'KEEP'}
    pairs = [row for row in pairs if row['l2_family'] in kept]
    return {'families': summary, 'touches': touches, 'pairs': pairs, 'fair_events': fair_events}
