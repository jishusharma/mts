"""Live adapter: candle-close sequences at the previous completed day/week high-low (1m bars in, lab arms only).

Logic reuses research/layer_lab/candle_close_2026-10-14/study.py (signatures() lines 108-122, level lookup
known()/make_events() lines 91, 134-170): UTC epoch-aligned complete candles; level = previous COMPLETED parent
period high/low (day / Monday-start week), known only at that period's end, a parent with a missing minute gives
NO level; eligible when |close/level-1| <= 0.0025; the 3 candles must be contiguous; first signal per UTC date,
family, side, edge. Orientation: side=+1 long uses the study inequalities, side=-1 (short) mirrors them.

SAMPLING: 0/126 arms passed the study's screen (results.json candidates == 0). Per side only the study's TOP arm by
mean gross return among arms with n >= 100 (by_side.csv, one row per tf/family/signature/side):
  short (side -1): tf 3m, week, strong_break  (n=168, gross +10.1bp, pre-cost)
  long  (side +1): tf 15m, day, reclaim       (n=216, gross +11.3bp, pre-cost)
Both are data-collection arms chosen post hoc from an exploratory study: no edge claim. Events carry "sampling": True.

DECISION (OURS): both level edges (high and low) of the family are scanned, as the study pooled them.
DECISION (OURS): the study's 31-day regime warm-up is not applied; a level only needs a full completed parent period.
DECISION (OURS): event "t" = open time of the LAST 1m bar of the signal candle, the minute whose close completes
  it (the emitter adds one 1m bar to get t_close).
DECISION (OURS): first-per-UTC-day dedup is within the supplied window (earlier events are stable under truncation).
Stdlib only. Needs >= 1 completed parent period of 1m history (1440 bars day, 10080 week) else no events.
"""
import math

MIN = 60000
DAY = 1440 * MIN
WEEK = 7 * DAY
MON0 = 4 * DAY  # 1970-01-05 was a Monday
BAND = 0.0025

# (tf_minutes, family, signature, side)
ARMS = [(3, "week", "strong_break", -1), (15, "day", "reclaim", 1)]


def _finite(b):
    return all(isinstance(b.get(k), (int, float)) and not isinstance(b.get(k), bool) and math.isfinite(b[k])
               for k in ("o", "h", "l", "c"))


def _aggregate(bars, minutes, anchor=0):
    """Epoch(+anchor)-aligned buckets made of exactly `minutes` consecutive finite 1m bars.
    -> {bucket_start: {t,o,h,l,c,last_t}} complete buckets only."""
    span, groups = minutes * MIN, {}
    for b in bars:
        groups.setdefault((b["t"] - anchor) // span * span + anchor, []).append(b)
    out = {}
    for s, g in groups.items():
        if len(g) == minutes and all(g[k]["t"] == s + k * MIN and _finite(g[k]) for k in range(minutes)):
            out[s] = {"t": s, "o": g[0]["o"], "h": max(x["h"] for x in g), "l": min(x["l"] for x in g),
                      "c": g[-1]["c"], "last_t": g[-1]["t"]}
    return out


def _signal(sig, side, c0, c1, c2, b):
    c, p, q = side * c0, side * c1, side * c2
    if sig == "reclaim":
        return q > 0 and p < 0 and c > 0
    if sig == "strong_break":
        span = b["h"] - b["l"]
        if span <= 0 or not (p <= 0 and c > 0):
            return False
        loc = (b["c"] - b["l"] if side == 1 else b["h"] - b["c"]) / span
        return loc >= 0.75 and abs(b["c"] - b["o"]) / span >= 0.6
    return False


def candle_close_layer(bars):
    """1m bars -> sampling alerts for the two ARMS. Side long/short as in the module docstring."""
    if len(bars) < 3:
        return []
    out, seen = [], set()
    for tf, fam, sig, side in ARMS:
        span = tf * MIN
        pspan, anchor = (DAY, 0) if fam == "day" else (WEEK, MON0)
        cand = _aggregate(bars, tf)
        parent = _aggregate(bars, pspan // MIN, anchor)
        for s in sorted(cand):
            b = cand[s]
            c1, c2 = cand.get(s - span), cand.get(s - 2 * span)
            if c1 is None or c2 is None:
                continue
            ps = (s - anchor) // pspan * pspan + anchor - pspan  # latest parent whose end <= s
            if ps not in parent:
                continue
            for edge in ("h", "l"):
                lvl = parent[ps][edge]
                if lvl <= 0 or abs(b["c"] / lvl - 1) > BAND:
                    continue
                if not _signal(sig, side, b["c"] - lvl, c1["c"] - lvl, c2["c"] - lvl, b):
                    continue
                key = (tf, fam, side, edge, s // DAY)
                if key in seen:
                    continue
                seen.add(key)
                name = "long" if side == 1 else "short"
                out.append({"t": b["last_t"], "side": name, "sampling": True, "level": round(lvl, 2),
                            "event": "cc_%s_%dm_%s_%s_%s_%s" % (sig, tf, fam, edge, name, round(lvl, 2))})
    return sorted(out, key=lambda e: (e["t"], e["event"]))
