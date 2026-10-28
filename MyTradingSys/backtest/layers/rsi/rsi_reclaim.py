"""
Operator RSI "2a" context events (research/rsi_2a_2026-10-09/RSI_2A_SPEC.md), close-based, no tuned numbers.

rsi_reclaim_events: RSI sits below a level (below = rsi < level - clearance) and later closes back above it
(above = rsi > level + clearance). Bars between the two thresholds are the "band". Each reclaim reports what the
operator wants to bucket afterwards instead of a pre-picked cut-off:
  dwell_below  bars in the last contiguous below-run (Case A = 1, Case B = 4..24 are analysis buckets, not rules here)
  band_bars    band bars between the end of that run and the reclaim bar (0 = direct cross)
  depth        level - lowest RSI in the run
direction="down" is the mirror for shorts (RSI above level + clearance, then closes back below it): the series is
mirrored with 100 - x, so "level" stays the real level (60 for the short side) and depth = highest RSI - level.
A band pop between two below-runs starts a NEW run (dwell restarts). None bars (warm-up/gap) carry state unchanged.

rsi_retest: Case C. After a reclaim, within `within` bars RSI comes back into the band (touch) and then closes above
again = "support"; closes below the lower threshold first = "fail"; otherwise "none". `within` and `clearance` are
caller arguments on purpose: no default, so no unsourced number can hide here.
"""


def _mirror(v):
    return None if v is None else 100.0 - v


def _check(rsi, ts, clearance, direction):
    if clearance < 0:
        raise ValueError("clearance must be >= 0")
    if len(rsi) != len(ts):
        raise ValueError("rsi and ts must have the same length")
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")


def rsi_reclaim_events(rsi: list, ts: list, level: float, clearance: float, direction: str = "up") -> list:
    _check(rsi, ts, clearance, direction)
    if direction == "down":
        series, lvl = [_mirror(v) for v in rsi], 100.0 - level
    else:
        series, lvl = rsi, level
    lo, hi = lvl - clearance, lvl + clearance
    events = []
    prev = None            # side of the last non-None bar: "below" | "band" | "above"
    armed = False          # a below-run exists and has not been reclaimed yet
    run_len = 0
    run_start = None
    run_min = None
    band_bars = 0
    for i, v in enumerate(series):
        if v is None:
            continue
        if v < lo:
            if prev != "below":
                run_len, run_start, run_min, band_bars = 0, i, v, 0
            run_len += 1
            run_min = min(run_min, v)
            armed = True
            prev = "below"
        elif v > hi:
            if armed:
                events.append({
                    "t": ts[i], "i": i, "event": "reclaim", "direction": direction,
                    "level_value": level, "clearance": clearance,
                    "dwell_below": run_len, "band_bars": band_bars,
                    "depth": lvl - run_min, "direct": band_bars == 0,
                    "run_start_t": ts[run_start],
                })
                armed = False
            prev = "above"
        else:
            if armed:
                band_bars += 1
            prev = "band"
    return events


def rsi_retest(rsi: list, reclaim_events: list, level: float, clearance: float, within: int,
               direction: str = "up") -> list:
    if clearance < 0:
        raise ValueError("clearance must be >= 0")
    if within < 1:
        raise ValueError("within must be >= 1")
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")
    series = [_mirror(v) for v in rsi] if direction == "down" else rsi
    lvl = 100.0 - level if direction == "down" else level
    lo, hi = lvl - clearance, lvl + clearance
    out = []
    n = len(series)
    for ev in reclaim_events:
        i = ev["i"]
        touched_at = None
        status, at = "none", None
        for j in range(i + 1, min(i + within, n - 1) + 1):
            v = series[j]
            if v is None:
                continue
            if v < lo:
                status, at = "fail", j
                break
            if v <= hi:
                if touched_at is None:
                    touched_at = j
            elif touched_at is not None:
                status, at = "support", j
                break
        out.append({"reclaim_t": ev["t"], "reclaim_i": i, "status": status,
                    "resolve_i": at, "touch_i": touched_at,
                    "bars_after": None if at is None else at - i})
    return out
