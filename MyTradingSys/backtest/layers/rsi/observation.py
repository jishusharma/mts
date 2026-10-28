"""
RSI observation block: the latest RSI reading per timeframe, READ from what the live alert runner already persisted.

READ-ONLY, NO NEW COMPUTATION: nothing here computes an RSI or an MA, fetches klines, writes a file, or imports any
execution code. It tails MyTradingSys/runtime/alerts/<tf>.jsonl (written by alerts/live_runner_cli.py:263-273 via
alert_emitter.append_alerts_jsonl) and copies fields that already exist in an alert record. A field or timeframe with
no source stays None. Consensus is an observation (research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43): this block
never gates, vetoes or delays a core.

WHERE THE DATA LIVES (investigated 2026-10-01):
- rsi_ma_events has NO live producer: it is imported only by rsi/run_rsi_backtest.py (offline). Nothing registers it in
  alerts/live_runner_cli.py:137-194 and no persisted output of it exists. So no rsi-vs-MA "ma_support"/"ma_rejection"
  event can be reported; support_or_reject below comes from rsi_events (the level-event detector) only.
- The live source is the alert record of layer "rsi", sub "rsi_events" (registered for 1h, 15m, 5m only:
  live_runner_cli.py:137-158; adapter alerts/live_layers.py:146-166). Every alert is built by alert_emitter.format_alert
  (alert_emitter.py:36-49): "rsi" and "rsi_ma" are the RSI(14) and its SMA(14) on the latest closed bar when the alert was
  first seen (live_runner_core.py:133-142,149-151), "event" and "level_value" are the rsi_events event (rsi_events.py:82-98),
  "t_close" is the event bar's OPEN time in ms (alert_emitter.py:46-47; auto_trader.py:221), "t_confirm" is the open time
  of the latest closed bar when first seen (live_runner_core.py:151).
- The <tf>.jsonl files hold every layer's alerts for that tf (live_runner_cli.py:263-273), so the newest line is often
  another layer's; this module scans backward for the newest rsi/rsi_events line.

MAPPING (per tf, fields copied from the newest valid record; anything else is None):
    rsi                <- record["rsi"]            (RSI(14) at t_confirm's bar, not at "now")
    ma_sma             <- record["rsi_ma"]         (SMA(14): live_runner_core.py:139 `_rsi_ma(rs, "SMA", 14)`; the record
                                                    itself does not name the MA type, the producer code does)
    ma_ema             <- always None              (no EMA is produced by any live code)
    support_or_reject  <- record["event"]          (verbatim: support | rejection | failure | cross, rsi_events.py:70,78,93)
    level              <- record["level_value"]    (rsi_events.py:85,94)
    t_close            <- record["t_close"]        (extra key, for staleness checks)
    t_confirm          <- record["t_confirm"]      (extra key: the bar the rsi/ma_sma values belong to)

RULES (tested in test_observation.py):
- "Latest" = the LAST valid matching line of the file (the runner appends in time order).
- A line is skipped (never raises) when it is empty, not valid UTF-8/JSON, not a JSON object, not layer "rsi" /
  sub "rsi_events", or when its "tf" differs from the file's tf. So a garbled or half-written last line falls back
  to the previous valid rsi_events record; if there is none, that tf is all None.
- Numeric fields must be finite numbers (bool, strings, NaN, inf -> None); "event" must be a string.
- Only the tail is read: the file is scanned backward in _CHUNK-byte chunks, at most max_scan_bytes bytes, stopping at
  the first match. A match older than max_scan_bytes is not found (that tf is all None).
- Missing file / unreadable / directory / bad alerts_dir -> that tf all None; nothing is created or written.
"""

import json
import math
import os
from contextlib import closing
from pathlib import Path

TFS = ("1m", "3m", "5m", "15m", "1h", "4h", "1d")
SOURCE_LAYER = "rsi"
SOURCE_SUB = "rsi_events"

# <repo>/MyTradingSys/backtest/layers/rsi/observation.py -> parents[3] is <repo>/MyTradingSys.
# Same directory as auto_trader.LAYER_ALERT_DIR (execution/auto_trader.py:46) and the runner's default
# (live_runner_cli.py:249, which is cwd-relative: a runner started from another cwd writes elsewhere).
DEFAULT_ALERTS_DIR = Path(__file__).resolve().parents[3] / "runtime" / "alerts"

_CHUNK = 64 * 1024
DEFAULT_MAX_SCAN_BYTES = 16 * 1024 * 1024


def _empty():
    return {"rsi": None, "ma_sma": None, "ma_ema": None, "support_or_reject": None, "level": None,
            "t_close": None, "t_confirm": None}


def _num(v):
    """A finite real number (not bool) or None."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if isinstance(v, float) and not math.isfinite(v):
        return None
    return v


def _ms(v):
    """An epoch-ms integer (not bool; an integral float is accepted) or None."""
    v = _num(v)
    if v is None:
        return None
    if isinstance(v, float):
        return int(v) if v.is_integer() else None
    return v


def _map(rec):
    ev = rec.get("event")
    return {
        "rsi": _num(rec.get("rsi")),
        "ma_sma": _num(rec.get("rsi_ma")),
        "ma_ema": None,
        "support_or_reject": ev if isinstance(ev, str) else None,
        "level": _num(rec.get("level_value")),
        "t_close": _ms(rec.get("t_close")),
        "t_confirm": _ms(rec.get("t_confirm")),
    }


def _lines_backward(path, max_scan_bytes):
    """Yield the file's lines (bytes, no newline) newest first, reading _CHUNK bytes at a time, at most
    max_scan_bytes bytes in total. A line cut by the scan limit is dropped, never yielded half."""
    with open(path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        pos = fh.tell()
        scanned = 0
        carry = b""
        while pos > 0 and scanned < max_scan_bytes:
            step = min(_CHUNK, pos, max_scan_bytes - scanned)
            pos -= step
            scanned += step
            fh.seek(pos)
            parts = (fh.read(step) + carry).split(b"\n")
            carry = parts[0]   # may be the tail of a line that starts in an earlier chunk
            for line in reversed(parts[1:]):
                yield line
        if pos == 0:
            yield carry        # the very first line of the file, complete


def _latest_for_tf(path, tf, max_scan_bytes):
    with closing(_lines_backward(path, max_scan_bytes)) as lines:
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw.decode("utf-8"))
            except Exception:   # bad UTF-8, bad JSON, absurd nesting / huge ints: a garbled line is skipped
                continue
            if (isinstance(rec, dict) and rec.get("layer") == SOURCE_LAYER and rec.get("sub") == SOURCE_SUB
                    and rec.get("tf") == tf):
                return _map(rec)
    return None


def read_latest(*, alerts_dir=None, max_scan_bytes=DEFAULT_MAX_SCAN_BYTES):
    """{tf: {"rsi","ma_sma","ma_ema","support_or_reject","level","t_close","t_confirm"}} for the seven TFs in TFS.

    Read-only; never raises; every field/tf without a source is None (see the module docstring for the mapping and
    which tfs have a source today: only 1h, 15m, 5m can, and only once the runner has emitted an rsi_events alert there).
    alerts_dir: directory holding <tf>.jsonl (default MyTradingSys/runtime/alerts).
    """
    out = {tf: _empty() for tf in TFS}
    try:
        base = Path(alerts_dir) if alerts_dir is not None else DEFAULT_ALERTS_DIR
    except Exception:
        return out
    for tf in TFS:
        try:
            rec = _latest_for_tf(base / (tf + ".jsonl"), tf, max_scan_bytes)
        except Exception:   # missing file, a directory, permissions, anything else: that tf stays all None
            rec = None
        if rec is not None:
            out[tf] = rec
    return out
