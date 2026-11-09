"""Krown S8 4h live decision code (R7 forward test; research/fable_run7_forward_test/FORWARD_PREREG.md section 1).

The frozen R6 rule, byte for byte: signal = krown_events.setup_s8 on CLOSED BTCUSDT 4h bars (krown_core.bbwp, params from
params/krown_params.json, imported not copied); stop = far side of bars i-9..i (e2_run.stop_for: min low for a long, max high
for a short); events only from bar index 10 (e2_run.signals: i >= STOP_BARS). The stop rule is three lines and is NOT imported
from research/e2_run.py on purpose: that module pulls numpy and the whole research loader into the live runner; the parity
test (research/fable_run7_forward_test/test_s8_forward_parity.py) imports e2_run itself and proves equality on 277 events.

s8_events(bars) -> runner events {"t": signal bar OPEN ms, "event": "S8", side, entry_price: signal close, stop, bbwp};
live_runner_core/format_alert turn "t" into t_close and add layer/sub/tf. Pure, no I/O, no trade. Any bad input (not strictly
ascending, non-finite, too short) -> [] and one stderr line: fail closed, never a partial or guessed event.
decide(alert, mark, position_flat) -> "take" | "skipped_busy" | "skipped_floor": the R6 busy rule (one position per account,
a signal while a position is open is skipped) and the 0.56 % floor (OURS, 4 x 14 bp; R6 e2_run.py:64-66), counted by the caller.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402

STOP_BARS = 10          # R6 e2_run.STOP_BARS (OURS there): stop window = bars i-9..i
FLOOR = 0.0056          # R6 e2_run.FLOOR: |fill - stop| / fill below this skips the event
SIDES = ("long", "short")


def _err(msg):
    print(json.dumps({"key": "krown_live", "error": msg}), file=sys.stderr, flush=True)


def _clean(bars):
    """True when bars are strictly ascending by t with finite positive o/h/l/c."""
    last = None
    for b in bars:
        for k in ("o", "h", "l", "c"):
            v = b.get(k)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
                return False
        t = b.get("t")
        if isinstance(t, bool) or not isinstance(t, int) or (last is not None and t <= last):
            return False
        last = t
    return True


def s8_events(bars):
    """Every S8 event in `bars` (closed 4h bars, runner shape). See module docstring."""
    try:
        if not bars or not _clean(bars):
            if bars:
                _err("bars not strictly ascending or not finite")
            return []
        h, l, c = ([float(b[k]) for b in bars] for k in ("h", "l", "c"))
        p = kc.load_params()
        bw = kc.bbwp(c, p["bbwp_basis"], p["bbwp_lookback"], p["bbwp_mult"])
        out = []
        for e in ke.setup_s8(bw, h, l, c, p):
            i = e["i"]
            if i < STOP_BARS:
                continue
            win = range(i - STOP_BARS + 1, i + 1)
            stop = min(l[j] for j in win) if e["side"] == "long" else max(h[j] for j in win)
            out.append({"t": bars[i]["t"], "event": "S8", "side": e["side"], "entry_price": c[i], "stop": stop,
                        "bbwp": float(bw[i])})
        return out
    except Exception as exc:  # noqa: BLE001 - fail closed: no event, runner keeps running
        _err(f"s8_events: {exc!r}"[:200])
        return []


def decide(alert, mark, position_flat):
    """Busy first (R6 order), then floor. Anything unusable (side, stop, mark) is a floor skip: never an order at a guess."""
    if not position_flat:
        return "skipped_busy"
    try:
        stop, side = float(alert["stop"]), alert["side"]
        mark = float(mark)
        if side not in SIDES or not math.isfinite(stop) or not math.isfinite(mark) or mark <= 0 or stop <= 0:
            return "skipped_floor"
        risk = (mark - stop) if side == "long" else (stop - mark)
        return "skipped_floor" if risk <= 0 or risk / mark < FLOOR else "take"
    except (KeyError, TypeError, ValueError):
        return "skipped_floor"
