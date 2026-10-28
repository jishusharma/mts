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


# ---------------------------------------------------------------------------------------------------------------------
# T05-F5 fair control (2026-10-28).  The control in analyze() above is UNFAIR: midnight +/- the real distance with a random
# sign makes half the five "random" lines the real level itself, and a control line never touched counts as a non-hold.
# analyze_fair() is the touched-only, distance-matched control ported from
# dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py (reference implementation; numbers must equal out/lc1_fair.csv).
# analyze() stays as the LEGACY control (published figures, shown as pub_* columns).
# Parameters (all OURS, no SOURCED ones): FAIR_SEED 20261016, K_LINES 20 per level, 2,000 day-bootstrap, KEEP = lower CI > 0.
# ---------------------------------------------------------------------------------------------------------------------
FAIR_SEED = 20261016
K_LINES = 20


def _month_of(day):
    import datetime as dt
    d = dt.date(1970, 1, 1) + dt.timedelta(days=int(day))
    return d.year * 12 + d.month


def fair_control_prices(rng, pool, mid, real_price, k=K_LINES, skip_real=False):
    """k random lines: distance drawn from `pool` (same family, same calendar month), random sign.

    Always consumes 2 rng values per draw (stream is identical for either skip_real). With skip_real a draw that lands
    on the real level is dropped (not redrawn), so a fair control line is never the real level.
    """
    out = []
    for _ in range(k):
        dist = pool[rng.randrange(len(pool))]
        p = mid + (-1 if rng.random() < .5 else 1) * dist
        if skip_real and abs(p - real_price) < 1e-9:
            continue
        out.append(p)
    return out


def _fair_boot_ci(days, seed, n_boot=BOOTSTRAPS):
    import numpy as np
    keys = sorted(days)
    arr = np.array([days[k] for k in keys], float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(keys), (n_boot, len(keys)))
    s = arr[pick].sum(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        diff = s[:, 0] / s[:, 1] - s[:, 2] / s[:, 3]
    diff = diff[~np.isnan(diff)]
    return float(np.quantile(diff, .025)), float(np.quantile(diff, .975))


def analyze_fair(bars, levels, seed=FAIR_SEED, k=K_LINES, skip_real=False):
    """Per-family hold rate vs the touched-only distance-matched control. `bars` = DEV only.

    hold = holds / touches for real levels AND control lines (an untouched line leaves the denominator).
    Also returns the legacy-control shares (orig_ctl_equal_real_share, orig_ctl_untouched_share) drawn from the same rng
    stream so the figures equal the T05 audit file.
    """
    by_day = defaultdict(list)
    for b in bars:
        by_day[int(b['t']) // DAY_MS].append(b)
    for rows in by_day.values():
        rows.sort(key=lambda b: b['t'])
    pool = defaultdict(list)
    for day, rows in by_day.items():
        mid = float(rows[0]['o'])
        for lv in levels.get(day, []):
            pool[(lv['family'], _month_of(day))].append(abs(float(lv['price']) - mid))
    rng = random.Random(seed)
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))   # family -> day -> real_h, real_n, ctl_h, ctl_n
    legacy = defaultdict(lambda: [0, 0, 0])                         # family -> levels, untouched draws, draws == real
    for day in sorted(by_day):
        rows = by_day[day]
        mid = float(rows[0]['o'])
        for lv in levels.get(day, []):
            fam = lv['family']
            price = float(lv['price'])

            def one(p):
                i = next((j for j, b in enumerate(rows) if float(b['l']) <= p <= float(b['h'])), None)
                if i is None:
                    return None
                return outcome(rows[i:], p, stop_width(mid, p), _prev_close(rows, i))

            real = one(price)
            for p in fair_control_prices(rng, pool[(fam, _month_of(day))], mid, price, k, skip_real):
                r = one(p)
                if r is not None:
                    acc[fam][day][2] += int(r == 'HOLD')
                    acc[fam][day][3] += 1
            if real is not None:
                acc[fam][day][0] += int(real == 'HOLD')
                acc[fam][day][1] += 1
            o = legacy[fam]
            o[0] += 1
            dist = abs(price - mid)
            for _ in range(5):
                sign = -1 if rng.random() < .5 else 1
                pp = mid + sign * dist
                o[2] += int(abs(pp - price) < 1e-9)
                o[1] += int(one(pp) is None)
    pub = analyze(bars, levels)['families']
    out = {}
    for fam in sorted(acc):
        d = acc[fam]
        rh = sum(v[0] for v in d.values()); rn = sum(v[1] for v in d.values())
        ch = sum(v[2] for v in d.values()); cn = sum(v[3] for v in d.values())
        lo, hi = _fair_boot_ci(d, seed)
        o = legacy[fam]
        p = pub.get(fam)
        out[fam] = {'n_touch': rn, 'hold': rh / rn, 'fair_ctl_touches': cn, 'fair_ctl_hold': ch / cn,
                    'diff': rh / rn - ch / cn, 'ci_lo': lo, 'ci_hi': hi, 'verdict': 'KEEP' if lo > 0 else 'DROP',
                    'pub_hold': p['hold_rate'] if p else float('nan'),
                    'pub_random': p['random_hold_rate'] if p else float('nan'),
                    'pub_diff': p['difference'] if p else float('nan'),
                    'pub_verdict': p['verdict'] if p else '',
                    'orig_ctl_equal_real_share': o[2] / (5 * o[0]), 'orig_ctl_untouched_share': o[1] / (5 * o[0])}
    return out
