"""First-touch level reactions and distance-matched seeded random-line controls."""
from collections import defaultdict
import math
import random

DAY_MS = 86_400_000
SEED = 20261014
BOOTSTRAPS = 2000


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


def analyze(bars, levels, seed=SEED):
    """Analyze each day's level rows; `bars` should contain DEV only."""
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
                         'verdict': 'KEEP' if ci and ci[0] > 0 else 'DROP'}
    kept = {name for name, row in summary.items() if row['verdict'] == 'KEEP'}
    pairs = [row for row in pairs if row['l2_family'] in kept]
    return {'families': summary, 'touches': touches, 'pairs': pairs}
