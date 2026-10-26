"""
Consensus-row writer: one JSON line per call, appended to Dumps/consensus/consensus_<UTC-date>.jsonl.

OBSERVATION ONLY (research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43): a consensus row never gates, vetoes or
delays a core. This module only reads what its caller hands it, builds a new row, and appends it to a file.
It never edits a core's state, never touches the network, takes no locks, and imports nothing from execution/.

Row fields exactly as ARCHITECTURE_TWO_CORES_2026-10-01.md:33-41, in this order:
    snapshot_id, utc_timestamp, price,
    tom   {verdict, setup, side, entry, stop, target, net_rr}      or null
    fabio {verdict, model, side, entry, stop, target}              or null
    rsi   {1m, 3m, 15m, 1h, 4h, 1d [, any extra key such as 5m]}
    notes (free text or null)

Rules (all tested in test_writer.py):
- Append-only: the file is opened in mode "a" (newline="\\n") and each row is ONE write of one complete line. No file
  is ever read back, rewritten, truncated or edited here.
- Never raises and never blocks on an IO or serialization error: the error is logged (logging, stderr by default;
  nothing is printed to stdout) and append_row returns False. The row is fully serialized BEFORE the file is opened,
  so a serialization error never leaves a partial line behind. The return value is informational only.
- Arguments are never mutated (the row is built from fresh dicts).

Open items (unknown, not invented here):
- snapshot_id: no snapshot_id exists in runtime/math_object_builder.py (grep count 0); who mints it is unknown.
  This writer takes snapshot.get("snapshot_id") if the caller's snapshot has one, else writes null and adds
  "snapshot_id absent in input" to notes.
- price: snapshot["current_price"] (the key of the raw snapshot, math_object_builder.py:6,43,64,91 and of the math
  object it returns, math_object_builder.py:376); if that is absent/None, snapshot.get("price"); else null.
"""

import json
import logging
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

_LOG = logging.getLogger(__name__)

# <repo>/MyTradingSys/backtest/layers/consensus/writer.py -> parents[4] is the repo root. Dumps/* is gitignored
# (.gitignore "Dumps/*"), so Dumps/consensus/ never reaches a commit.
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DIR = REPO_ROOT / "Dumps" / "consensus"

TOM_KEYS = ("verdict", "setup", "side", "entry", "stop", "target", "net_rr")        # ARCHITECTURE:37
FABIO_KEYS = ("verdict", "model", "side", "entry", "stop", "target")                # ARCHITECTURE:38
RSI_TFS = ("1m", "3m", "15m", "1h", "4h", "1d")                                     # ARCHITECTURE:39
NO_ID_NOTE = "snapshot_id absent in input"


def _warn(msg, *args):
    try:
        _LOG.warning(msg, *args)
    except Exception:  # logging must never be the reason a core is disturbed
        pass


def _as_utc(now):
    """None -> real UTC now; naive datetime -> interpreted as UTC; aware datetime -> converted to UTC."""
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def consensus_path(now=None, base_dir=None):
    """<base_dir or DEFAULT_DIR>/consensus_<YYYYMMDD of the UTC date>.jsonl (base_dir IS the directory that holds
    the daily files; it replaces <repo>/Dumps/consensus)."""
    directory = Path(base_dir) if base_dir is not None else DEFAULT_DIR
    return directory / ("consensus_%s.jsonl" % _as_utc(now).strftime("%Y%m%d"))


def _utc_timestamp(t):
    """ISO-8601 UTC, millisecond precision, e.g. 2026-10-01T19:30:15.123Z."""
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (t.microsecond // 1000)


def _core_block(src, keys, name):
    """Project a core's dict onto exactly the documented keys (missing -> None). None -> None (core off / no alert)."""
    if src is None:
        return None
    if not isinstance(src, Mapping):
        _warn("consensus: %s block is not a mapping (%s); written as null", name, type(src).__name__)
        return None
    return {k: src.get(k) for k in keys}


def _rsi_block(rsi):
    """The six architecture TF keys always (None when absent), then any extra key carried through unchanged."""
    src = None
    if rsi is not None:
        if isinstance(rsi, Mapping):
            src = rsi
        else:
            _warn("consensus: rsi block is not a mapping (%s); six TF keys written as null", type(rsi).__name__)
    out = {tf: (src.get(tf) if src is not None else None) for tf in RSI_TFS}
    if src is not None:
        for k, v in src.items():
            if k not in out:
                out[k] = v
    return out


def _build_row(snapshot, tom, fabio, rsi, notes, t):
    if snapshot is not None and not isinstance(snapshot, Mapping):
        _warn("consensus: snapshot is not a mapping (%s); snapshot_id and price written as null",
              type(snapshot).__name__)
    snap = snapshot if isinstance(snapshot, Mapping) else {}
    snapshot_id = snap.get("snapshot_id")
    price = snap.get("current_price")
    if price is None:
        price = snap.get("price")
    parts = []
    if notes is not None and notes != "":
        parts.append(str(notes))
    if snapshot_id is None:
        parts.append(NO_ID_NOTE)
    return {
        "snapshot_id": snapshot_id,
        "utc_timestamp": _utc_timestamp(t),
        "price": price,
        "tom": _core_block(tom, TOM_KEYS, "tom"),
        "fabio": _core_block(fabio, FABIO_KEYS, "fabio"),
        "rsi": _rsi_block(rsi),
        "notes": "; ".join(parts) if parts else None,
    }


def append_row(snapshot, tom, fabio, rsi, *, notes=None, base_dir=None, now=None):
    """Append ONE consensus row (one JSON line) and return True; on any error log it and return False (never raises).

    snapshot: the caller's snapshot / math-object dict (read only; see module docstring for snapshot_id and price).
    tom:      dict like auto_trader.parse_tom_alert's result (execution/auto_trader.py:103-119) or None. Only the
              keys verdict, setup, side, entry, stop, target, net_rr are written (others, e.g. alert_no, time,
              zone_tf, are dropped; put anything worth keeping in notes). None -> "tom": null.
    fabio:    dict with verdict, model, side, entry, stop, target, or None -> "fabio": null.
    rsi:      the dict observation.read_latest() returns (7 TF keys incl. 5m) or None. The six keys 1m,3m,15m,1h,4h,1d
              are always written (null if absent); any other key (5m) is carried through unchanged after them.
    notes:    optional free text. "snapshot_id absent in input" is appended when the snapshot has no snapshot_id.
    base_dir: directory holding the daily files (default <repo>/Dumps/consensus). Created as needed.
    now:      UTC datetime for the filename date and utc_timestamp (default real UTC now; naive = UTC).
    """
    try:
        t = _as_utc(now)
        row = _build_row(snapshot, tom, fabio, rsi, notes, t)
        # Serialize first: a bad value must fail here, before the file is touched. allow_nan=False keeps every line
        # valid JSON (a NaN would otherwise be written as the non-JSON token NaN).
        line = json.dumps(row, allow_nan=False) + "\n"
        path = consensus_path(t, base_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line)
        return True
    except Exception as exc:
        _warn("consensus: row not written (%s: %s)", type(exc).__name__, exc)
        return False
