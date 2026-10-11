"""
MyTradingSys/backtest/layers/session_levels/session_levels.py  (T087, items/T087_session_levels_observation_layer.md)

Session-levels OBSERVATION layer: previous-day high/low, Asia and EU session extremes, failed first break.
Backtest/observation only. Separate layer, never a Tom filter, nothing here places an order. The trade rows
are a fee-bearing measurement of what an entry on the observation would have returned, not a signal.

Event ("failed first break", side "high"; side "low" is the exact mirror):
  level  = previous UTC day's high (needs a complete previous day, >= MIN_PREV_BARS 1m bars)
  touch  = first 1m bar of the day, before US_OPEN_MIN, whose high exceeds level
  fail   = first bar j in [touch, touch + FAIL_WINDOW_MIN] whose CLOSE is back below level, j before US_OPEN_MIN.
           Causal: the event is stamped at j and uses only data up to j. No fail in the window = no event.
  spike  = highest high from touch to j (the "local high" to be taken again)
  asia_low = lowest low from 00:00 to min(j, ASIA_END_MIN)  (known at j)
  eu_low   = lowest low from ASIA_END_MIN to j, only when j >= ASIA_END_MIN (None otherwise)
  For side "low" the keys keep their names but hold the opposite extremes (Asia/EU session HIGH).
Outcome per target T in {asia_low, eu_low} when T is below the entry (short at close of j, fee both ways):
  first = "target" if a later bar before US_OPEN_MIN reaches T before the spike is exceeded, "stop" if the spike
          is exceeded first (a bar that does both counts as stop: conservative), "neither" otherwise.
  net   = gross return of a short at entry with target T, stop spike, time exit at the last close before
          US_OPEN_MIN, minus 2 * taker fee (fees.py).
Parameters, ALL NO-SOURCE (placeholders fixed before the run, not tuned): sessions in UTC (Asia 00:00-08:00,
EU 08:00-14:00), US open 14:00 UTC, FAIL_WINDOW_MIN = 60, a touch is any tick above the level. Tom's only
related words (Of_wlv3xaZo:7, QClPWDJ-BrU:7) name no clock, threshold or probability.
"""

MIN_MS = 60000
DAY_MS = 86400000
ASIA_END_MIN = 480
US_OPEN_MIN = 840
FAIL_WINDOW_MIN = 60
MIN_PREV_BARS = 1400
FEE = 0.0005   # fees.py DERIBIT_TAKER per side


def _by_day(bars):
    days = {}
    for b in bars:
        days.setdefault(b["t"] // DAY_MS, []).append(b)
    return days


def day_levels(bars):
    """{day_index: {high, low, asia_high, asia_low, n}} for every UTC day present."""
    out = {}
    for d, bs in _by_day(bars).items():
        asia = [b for b in bs if (b["t"] - d * DAY_MS) // MIN_MS < ASIA_END_MIN]
        out[d] = {"high": max(b["h"] for b in bs), "low": min(b["l"] for b in bs), "n": len(bs),
                  "asia_high": max(b["h"] for b in asia) if asia else None,
                  "asia_low": min(b["l"] for b in asia) if asia else None}
    return out


def _signed(b, s):
    """Signed view so one code path serves both sides: s=1 high side, s=-1 low side (prices negated)."""
    if s == 1:
        return b["h"], b["l"], b["c"]
    return -b["l"], -b["h"], -b["c"]


def _leg(entry, target, spike, sv, mins, start, fee):
    """Short in signed space from bar index `start` to the last bar before US open."""
    if target >= entry:
        return None
    first, exit_p, last = "neither", None, None
    for k in range(start, len(sv)):
        if mins[k] >= US_OPEN_MIN:
            break
        h, lo, c = sv[k]
        last = c
        if h > spike:
            first, exit_p = "stop", spike
            break
        if lo <= target:
            first, exit_p = "target", target
            break
    if exit_p is None:
        exit_p = last if last is not None else entry
    return {"first": first, "net": (entry - exit_p) / abs(entry) - 2 * fee}


def failed_break_events(bars, side="high", fee=FEE, fail_window=FAIL_WINDOW_MIN):
    if side not in ("high", "low"):
        raise ValueError("side must be 'high' or 'low'")
    s = 1 if side == "high" else -1
    days = _by_day(bars)
    levels = day_levels(bars)
    events = []
    for d in sorted(days):
        prev = levels.get(d - 1)
        if prev is None or prev["n"] < MIN_PREV_BARS:
            continue
        level_s = prev["high"] if s == 1 else -prev["low"]
        bs = days[d]
        base = d * DAY_MS
        mins = [(b["t"] - base) // MIN_MS for b in bs]
        sv = [_signed(b, s) for b in bs]
        touch = next((i for i, m in enumerate(mins) if m < US_OPEN_MIN and sv[i][0] > level_s), None)
        if touch is None:
            continue
        fail = None
        for j in range(touch, len(bs)):
            if mins[j] >= US_OPEN_MIN or mins[j] > mins[touch] + fail_window:
                break
            if sv[j][2] < level_s:
                fail = j
                break
        if fail is None:
            continue
        spike = max(sv[k][0] for k in range(touch, fail + 1))
        asia_ext = min(sv[k][1] for k in range(fail + 1) if mins[k] < ASIA_END_MIN)
        eu_idx = [k for k in range(fail + 1) if mins[k] >= ASIA_END_MIN]
        eu_ext = min(sv[k][1] for k in eu_idx) if eu_idx else None
        entry = sv[fail][2]
        events.append({
            "day": d, "side": side, "level": abs(level_s), "touch_min": mins[touch], "fail_min": mins[fail],
            "touch_session": "asia" if mins[touch] < ASIA_END_MIN else "eu",
            "entry": abs(entry), "spike": abs(spike), "asia_low": abs(asia_ext),
            "eu_low": abs(eu_ext) if eu_ext is not None else None,
            "asia": _leg(entry, asia_ext, spike, sv, mins, fail + 1, fee),
            "eu": _leg(entry, eu_ext, spike, sv, mins, fail + 1, fee) if eu_ext is not None else None,
        })
    return events
