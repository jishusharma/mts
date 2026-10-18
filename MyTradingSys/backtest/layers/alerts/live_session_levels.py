"""
Live adapter (wave W1a): previous-day high/low failed first break -> alert events. SAMPLING layer, no edge.

Wraps session_levels/session_levels.py:82 failed_break_events on 1m bars (as T087 ran it). Defaults, all
NO-SOURCE per that module (Asia 00-08 UTC, US open 14:00, fail window 60 min); not tuned here.
Side: high-side failed break (price poked above prior-day high then closed back below) -> short;
low-side failed break -> long (the module's own mirror).
Causality: the event is stamped at the fail bar and the fields kept here (level, touch/fail minute, entry,
spike) only use data up to that bar. The module's forward legs ("asia"/"eu" outcomes) look ahead and are
DROPPED. Event "t" = OPEN time of the fail bar (bars carry open time). Truncation of the bars never changes
earlier events (a fail needs its own bar). Stateless: same bars -> same output.
DECISION (OURS): bars with non-finite o/h/l/c are dropped first; the module needs a complete previous day
(>= 1400 bars) so shorter input -> []. Event name unique per (t, side). Proposed size 20/2 (OURS).
"""
import math

from MyTradingSys.backtest.layers.session_levels.session_levels import failed_break_events, MIN_MS, DAY_MS

SIDE = {"high": "short", "low": "long"}
NAME = {"high": "sess_pdh_failed_break", "low": "sess_pdl_failed_break"}


def _clean(bars):
    out = []
    for b in bars:
        try:
            if all(math.isfinite(float(b[k])) for k in ("o", "h", "l", "c")):
                out.append(b)
        except (KeyError, TypeError, ValueError):
            continue
    return out


def session_levels_layer(bars):
    bars = _clean(bars)
    if not bars:
        return []
    out = []
    for side in ("high", "low"):
        for e in failed_break_events(bars, side=side):
            t = e["day"] * DAY_MS + e["fail_min"] * MIN_MS
            out.append({"t": t, "event": NAME[side], "side": SIDE[side], "sampling": True,
                        "level": e["level"], "entry": e["entry"], "spike": e["spike"],
                        "touch_min": e["touch_min"], "fail_min": e["fail_min"]})
    out.sort(key=lambda x: (x["t"], x["event"]))
    return out


adapter = session_levels_layer
