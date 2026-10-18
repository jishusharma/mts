"""Live levels-confluence layer (wave W2a): first touch of the 8 KEEP level families, 1m bars, alert-only.

Reference: research/levels_confluence_2026-10-14/levels.py (builder) and event_table.py (first-touch rows); the Q79 rule
(commit e6a3b0be) fixes the side: taken from the PREVIOUS bar's close vs the level, never from the touch bar.
The research files are NOT imported (live code must not depend on research dirs); the logic is restated here.

Point in time: the levels of UTC day d are built only from bars with t < d*DAY_MS (a prior-day level does not exist
before the 00:00 UTC close of its source day). Families (LC1 levels_hold.md KEEP): prior_day_high, prior_day_low,
prior_day_poc, naked_poc, 4h_fractal_high, 4h_fractal_low, round_1000, prior_week_high.

Known caveat: the Java level builder matches these Python zones only 54.9% (level ledger, commit 59b85fd2); this module
follows the Python research code. Calibration/data source on testnet, not a claim of edge ("sampling": True).
Side: price above the level before the touch => support => "long"; below => "short". The first bar of a UTC day has no
previous bar in the day: research falls back to that bar's open (known at bar open); kept here.
"""
from collections import defaultdict

DAY_MS = 86_400_000
MIN_MS = 60_000
BIN_USD = 10.0
KEEP = ("prior_day_high", "prior_day_low", "prior_day_poc", "naked_poc",
        "4h_fractal_high", "4h_fractal_low", "round_1000", "prior_week_high")
ADAPTER_DAYS = 2   # adapter reports the last N UTC days present (alert_emitter dedups on (t, event))


def _ok(b):
    try:
        return all(float(b[k]) == float(b[k]) for k in ("t", "o", "h", "l", "c", "v"))   # NaN != NaN
    except (KeyError, TypeError, ValueError):
        return False


def _by_day(bars):
    days = defaultdict(dict)
    for b in bars or ():
        if _ok(b):
            days[int(b["t"]) // DAY_MS][int(b["t"])] = b   # last write wins on a duplicate t
    return {d: [rows[t] for t in sorted(rows)] for d, rows in days.items()}


def _profile_poc(rows):
    """POC of the uniform OHLC-overlap 10 USD volume profile (FORMULAS.md 18.1); None when no volume."""
    vol = defaultdict(float)
    for b in rows:
        lo, hi, amount = float(b["l"]), float(b["h"]), float(b["v"])
        if amount < 0:
            raise ValueError("volume must be non-negative")
        if hi <= lo:
            vol[int(lo // BIN_USD)] += amount
            continue
        for k in range(int(lo // BIN_USD), int((hi - 1e-12) // BIN_USD) + 1):
            overlap = max(0.0, min(hi, (k + 1) * BIN_USD) - max(lo, k * BIN_USD))
            vol[k] += amount * overlap / (hi - lo)
    if not vol or sum(vol.values()) <= 0:
        return None
    top = max(vol.values())
    return min(k for k, v in vol.items() if v == top) * BIN_USD + BIN_USD / 2


def _agg_4h(rows):
    groups = defaultdict(list)
    for b in rows:
        groups[int(b["t"]) // (240 * MIN_MS)].append(b)
    return [{"h": max(float(x["h"]) for x in g), "l": min(float(x["l"]) for x in g)}
            for _, g in sorted(groups.items())]


def build_levels(days, d, poc_cache=None):
    """KEEP levels of UTC day d from `days` ({epoch_day: sorted bars}); only days < d are read.
    Returns [{"family","price"}], de-duplicated on (family, price)."""
    prior = days.get(d - 1)
    if not prior:
        return []
    out = {}

    def add(family, price):
        out.setdefault((family, float(price)), {"family": family, "price": float(price)})

    def poc_of(day):
        if poc_cache is not None and day in poc_cache:
            return poc_cache[day]
        p = _profile_poc(days.get(day, []))
        if poc_cache is not None:
            poc_cache[day] = p
        return p

    add("prior_day_high", max(float(b["h"]) for b in prior))
    add("prior_day_low", min(float(b["l"]) for b in prior))
    p = poc_of(d - 1)
    if p is not None:
        add("prior_day_poc", p)
    week_start = d - ((d + 3) % 7)   # Monday of d's ISO week; prior week = the 7 days before it
    wk = [b for day in range(week_start - 7, week_start) if day < d for b in days.get(day, [])]
    if wk:
        add("prior_week_high", max(float(b["h"]) for b in wk))
    for src in range(d - 10, d):
        price = poc_of(src)
        if price is None:
            continue
        if not any(float(b["l"]) <= price <= float(b["h"]) for day in range(src + 1, d) for b in days.get(day, [])):
            add("naked_poc", price)
    # Confirmed 5-bar 4h fractals: two closed 4h bars each side; pivots from the last 10 days only (research rule).
    h4 = _agg_4h([b for day in range(d - 11, d) for b in days.get(day, [])])
    skip = len(h4) - len(_agg_4h([b for day in range(d - 10, d) for b in days.get(day, [])]))
    for i in range(max(2, skip), len(h4) - 2):
        nb = h4[i - 2:i] + h4[i + 1:i + 3]
        if h4[i]["h"] > max(x["h"] for x in nb):
            add("4h_fractal_high", h4[i]["h"])
        if h4[i]["l"] < min(x["l"] for x in nb):
            add("4h_fractal_low", h4[i]["l"])
    lo, hi = min(float(b["l"]) for b in prior), max(float(b["h"]) for b in prior)
    for px in range(int(lo // 1000) * 1000, int(hi // 1000) * 1000 + 1, 1000):
        add("round_1000", px)
    return list(out.values())


def detect_events(bars, only_days=None):
    """First touch per level per UTC day. Rows {"day","t","family","level","side"} (side +1/-1), sorted by t.
    Level availability: day d uses only bars before d*DAY_MS. Side: previous bar's close (same day) vs level (Q79).
    only_days: iterable of epoch days to report (default every day present)."""
    days = _by_day(bars)
    want = sorted(days) if only_days is None else sorted(set(only_days) & set(days))
    cache, rows = {}, []
    for d in want:
        daybars = days[d]
        for lev in build_levels(days, d, cache):
            px = lev["price"]
            i = next((j for j, b in enumerate(daybars) if float(b["l"]) <= px <= float(b["h"])), None)
            if i is None:
                continue
            ref = float(daybars[i - 1]["c"]) if i else float(daybars[i]["o"])
            rows.append({"day": d, "t": int(daybars[i]["t"]), "family": lev["family"], "level": px,
                         "side": 1 if ref >= px else -1})
    rows.sort(key=lambda r: r["t"])
    return rows


def levels_confluence_layer(bars):
    """Adapter fn(bars) -> [event] for live_runner (1m bars). Events of the last ADAPTER_DAYS UTC days present.
    t = touch bar OPEN time; event name unique per (t, level); side long (price was above the level) / short."""
    days = sorted(_by_day(bars))
    if not days:
        return []
    return [{"t": r["t"], "event": "lc_%s_%d" % (r["family"], round(r["level"])),
             "side": "long" if r["side"] > 0 else "short", "family": r["family"],
             "level": r["level"], "sampling": True}
            for r in detect_events(bars, only_days=days[-ADAPTER_DAYS:])]
