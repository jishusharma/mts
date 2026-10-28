"""Causal UTC-day BTC levels; all inputs are closed 1m bars before day open."""
from collections import defaultdict

DAY_MS = 86_400_000
MIN_MS = 60_000
BIN_USD = 10.0


def _day(t):
    return int(t) // DAY_MS


def _profile(bars):
    """FORMULAS.md 18.1 uniform OHLC overlap volume profile."""
    vol = defaultdict(float)
    for b in bars:
        lo, hi, amount = float(b['l']), float(b['h']), float(b['v'])
        if amount < 0:
            raise ValueError('volume must be non-negative')
        if hi <= lo:
            vol[int(lo // BIN_USD)] += amount
            continue
        first, last = int(lo // BIN_USD), int((hi - 1e-12) // BIN_USD)
        for k in range(first, last + 1):
            overlap = max(0.0, min(hi, (k + 1) * BIN_USD) - max(lo, k * BIN_USD))
            vol[k] += amount * overlap / (hi - lo)
    if not vol or sum(vol.values()) <= 0:
        return None
    low, high = min(vol), max(vol)
    poc = min(k for k, v in vol.items() if v == max(vol.values()))
    left = right = poc
    acc, total = vol[poc], sum(vol.values())
    while acc < .70 * total and (left > low or right < high):
        vl, vh = vol.get(left - 1, -1), vol.get(right + 1, -1)
        if vl >= vh and left > low:
            left -= 1
            acc += vol[left]
        elif right < high:
            right += 1
            acc += vol[right]
        elif left > low:
            left -= 1
            acc += vol[left]
    return {'poc': poc * BIN_USD + BIN_USD / 2, 'val': left * BIN_USD,
            'vah': (right + 1) * BIN_USD}


def _aggregate_4h(bars):
    groups = defaultdict(list)
    for b in bars:
        groups[int(b['t']) // (240 * MIN_MS)].append(b)
    out = []
    for idx, rows in sorted(groups.items()):
        rows.sort(key=lambda x: x['t'])
        out.append({'t': idx * 240 * MIN_MS, 'h': max(float(x['h']) for x in rows),
                    'l': min(float(x['l']) for x in rows)})
    return out


def levels_by_day(bars):
    """Return {epoch_day: [{price,family,source}]}; levels use only prior-day data."""
    days = defaultdict(list)
    for b in bars:
        days[_day(b['t'])].append(b)
    for rows in days.values():
        rows.sort(key=lambda x: x['t'])
    out = {}
    for d in sorted(days):
        prior = days.get(d - 1, [])
        if not prior:
            out[d] = []
            continue
        result = []

        def add(price, family, source):
            if price is not None:
                result.append({'price': float(price), 'family': family, 'source': source})

        add(max(float(b['h']) for b in prior), 'prior_day_high', 'TOM')
        add(min(float(b['l']) for b in prior), 'prior_day_low', 'TOM')
        profile = _profile(prior)
        if profile:
            for key in ('poc', 'vah', 'val'):
                add(profile[key], 'prior_day_' + key, 'TOM')
        # Strictly pre-midnight boundary proxy: the previous completed bar's close.
        # This avoids consulting the bar timestamped exactly 00:00.
        add(float(prior[-1]['c']), 'daily_open', 'OURS')
        # Previous ISO week: prior bars from the previous Monday through Sunday.
        week_start = d - ((d + 3) % 7)
        week_bars = [b for day, rows in days.items() if week_start - 7 <= day < week_start for b in rows]
        if week_bars:
            add(max(float(b['h']) for b in week_bars), 'prior_week_high', 'CONSENSUS')
            add(min(float(b['l']) for b in week_bars), 'prior_week_low', 'CONSENSUS')
        # Naked POCs from the preceding ten complete UTC days, only if not revisited since.
        for source_day in range(max(min(days), d - 10), d):
            source_rows = days.get(source_day, [])
            p = _profile(source_rows)
            if not p:
                continue
            price = p['poc']
            revisited = any(float(b['l']) <= price <= float(b['h'])
                            for day in range(source_day + 1, d) for b in days.get(day, []))
            if not revisited:
                add(price, 'naked_poc', 'TOM')
        # Confirmed 5-bar fractals: pivot bar has two closed 4h bars on each side.
        all_before = [b for day, rows in days.items() if day < d for b in rows]
        h4 = _aggregate_4h(all_before)
        for i in range(2, len(h4) - 2):
            pivot = h4[i]
            if pivot['t'] < (d - 10) * DAY_MS:
                continue
            if pivot['h'] > max(x['h'] for x in h4[i - 2:i] + h4[i + 1:i + 3]):
                add(pivot['h'], '4h_fractal_high', 'FABIO')
            if pivot['l'] < min(x['l'] for x in h4[i - 2:i] + h4[i + 1:i + 3]):
                add(pivot['l'], '4h_fractal_low', 'FABIO')
        # Round 1000s spanning prior range plus nearest boundary around prior close.
        lo = min(float(b['l']) for b in prior)
        hi = max(float(b['h']) for b in prior)
        for px in range(int(lo // 1000) * 1000, int(hi // 1000) * 1000 + 1, 1000):
            add(px, 'round_1000', 'OURS')
        # Stable de-duplication across same family and price.
        unique = {}
        for row in result:
            unique[(row['family'], row['price'])] = row
        out[d] = list(unique.values())
    return out


def day_levels(bars):
    """Compatibility helper: mapping day -> level rows."""
    return levels_by_day(bars)
