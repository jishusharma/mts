"""First-touch level reactions and distance-matched seeded random-line controls."""
from collections import defaultdict
import datetime as dt
import math
import random

import numpy as np

DAY_MS = 86_400_000
SEED = 20261014          # OURS: legacy control + legacy bootstrap (published study)
FAIR_SEED = 20261016     # OURS: fair control draws + fair bootstrap (T05 audit seed; reproduces out/lc1_fair.csv)
BOOTSTRAPS = 2000        # OURS
FAIR_LINES = 20          # OURS: random lines per candidate level in the fair control (T05-F5)
LEGACY_LINES = 5         # OURS: published control lines per level


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


def month_of(day):
    d = dt.date(1970, 1, 1) + dt.timedelta(days=int(day))
    return d.year * 12 + d.month


def legacy_control_prices(mid, dist, k, rng):
    """PUBLISHED control (legacy column): mid +/- the real level's own distance, random sign.
    Half of these lines ARE the real level (T05-F5)."""
    out = []
    for _ in range(k):
        sign = -1 if rng.random() < .5 else 1
        out.append(mid + sign * dist)
    return out


def fair_control_prices(pool, mid, k, rng):
    """FAIR control: k lines whose distance from the midnight open is drawn from `pool` (distances of the same family's
    candidate levels in the same calendar month, touched or not), random sign. The real level is hit only with
    probability 1/(2*len(pool)), not 1/2."""
    out = []
    for _ in range(k):
        dist = pool[rng.randrange(len(pool))]
        out.append(mid + (-1 if rng.random() < .5 else 1) * dist)
    return out


def _fair_boot_ci(days, seed=FAIR_SEED, iterations=BOOTSTRAPS):
    """days: day -> [real_hold, real_n, ctl_hold, ctl_n]. Ratio-of-sums day bootstrap of real rate minus control rate."""
    keys = sorted(days)
    arr = np.array([days[k] for k in keys], float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(keys), (iterations, len(keys)))
    sums = arr[pick].sum(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        diff = sums[:, 0] / sums[:, 1] - sums[:, 2] / sums[:, 3]
    diff = diff[~np.isnan(diff)]
    return float(np.quantile(diff, .025)), float(np.quantile(diff, .975))


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
    # fair control distance pools: family x calendar month, ALL candidate levels (touched or not)
    pool = defaultdict(list)
    for day, rows in by_day.items():
        mid0 = float(rows[0]['o'])
        for lev in levels.get(day, []):
            pool[(lev['family'], month_of(day))].append(abs(float(lev['price']) - mid0))
    frng = random.Random(FAIR_SEED)
    fair = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))   # family -> day -> real_h, real_n, ctl_h, ctl_n
    diag = defaultdict(lambda: [0, 0, 0, 0, 0])   # family -> legacy lines drawn, untouched, equal to real, fair lines equal to real, fair lines drawn
    family = defaultdict(lambda: {'n': 0, 'hold': 0, 'random_hold': 0, 'days': defaultdict(lambda: [0, 0])})
    touches, pairs = [], []
    for day in sorted(by_day):
        rows = by_day[day]
        if not rows:
            continue
        midnight = float(rows[0]['o'])
        for lev in levels.get(day, []):
            fam, price = lev['family'], float(lev['price'])
            ps = pool[(fam, month_of(day))]

            def one(p):
                i = next((j for j, b in enumerate(rows) if float(b['l']) <= p <= float(b['h'])), None)
                if i is None:
                    return None
                return outcome(rows[i:], p, stop_width(midnight, p), _prev_close(rows, i))

            diag[fam][4] += FAIR_LINES
            for p in fair_control_prices(ps, midnight, FAIR_LINES, frng):
                diag[fam][3] += int(abs(p - price) < 1e-9)
                r = one(p)
                if r is not None:
                    fair[fam][day][2] += int(r == 'HOLD')
                    fair[fam][day][3] += 1
            real = one(price)
            if real is not None:
                fair[fam][day][0] += int(real == 'HOLD')
                fair[fam][day][1] += 1
            # diagnostics on the published control (also keeps the draw stream identical to the T05 audit run)
            for p in legacy_control_prices(midnight, abs(price - midnight), LEGACY_LINES, frng):
                diag[fam][0] += 1
                diag[fam][1] += int(one(p) is None)
                diag[fam][2] += int(abs(p - price) < 1e-9)
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
            for random_price in legacy_control_prices(midnight, dist, LEGACY_LINES, rng):
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
        legacy_diff = (s['hold'] - s['random_hold']) / s['n']
        f = fair[name]
        rh = sum(v[0] for v in f.values()); rn = sum(v[1] for v in f.values())
        ch = sum(v[2] for v in f.values()); cn = sum(v[3] for v in f.values())
        fci = _fair_boot_ci(f)
        d = diag[name]
        summary[name] = {'n': s['n'], 'hold_rate': s['hold'] / s['n'],
                         # DECISION columns: touched-only distance-matched control
                         'random_hold_rate': ch / cn, 'fair_control_touches': cn, 'difference': rh / rn - ch / cn,
                         'ci95': fci, 'verdict': 'KEEP' if fci[0] > 0 else 'DROP',
                         # LEGACY columns: published control (half the lines are the real level, untouched = non-hold)
                         'legacy_random_hold_rate': s['random_hold'] / s['n'], 'legacy_difference': legacy_diff,
                         'legacy_ci95': ci, 'legacy_verdict': 'KEEP' if ci and ci[0] > 0 else 'DROP',
                         'legacy_equal_real_share': d[2] / d[0], 'legacy_untouched_share': d[1] / d[0],
                         'fair_equal_real_share': d[3] / d[4]}
    kept = {name for name, row in summary.items() if row['verdict'] == 'KEEP'}
    pairs = [row for row in pairs if row['l2_family'] in kept]
    return {'families': summary, 'touches': touches, 'pairs': pairs}
