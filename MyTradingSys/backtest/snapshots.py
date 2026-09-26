import sys
sys.dont_write_bytecode = True
"""Snapshot loading shared by parity.py and replay.py.
Java writes nanosecond fractions (e.g. .663997400Z); Python 3.10
datetime.fromisoformat rejects more than 6 digits, which silently dropped
8116 of 8993 files in the first replay attempt. Truncate to microseconds."""
import json, re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP_DIR = ROOT / "runtime_data" / "snapshots"
OUT_DIR = ROOT / "Dumps" / "backtest"

_FRAC = re.compile(r"(\.\d{6})\d+")


def parse_ts(raw):
    s = _FRAC.sub(r"\1", str(raw)).replace("Z", "+00:00")
    return datetime.fromisoformat(s).timestamp()


def iter_snapshots(symbol="BTCUSDT"):
    """Yields (path, snapshot, epoch_seconds). Counts failures instead of
    hiding them: the caller prints the counts."""
    stats = {"files": 0, "load_fail": 0, "ts_fail": 0}
    out = []
    for p in sorted(SNAP_DIR.glob(symbol + "_*.json")):
        stats["files"] += 1
        try:
            s = json.load(open(p, encoding="utf-8"))
        except Exception:
            stats["load_fail"] += 1
            continue
        try:
            t = parse_ts(s.get("timestamp_utc", ""))
        except Exception:
            stats["ts_fail"] += 1
            continue
        out.append((p, s, t))
    out.sort(key=lambda x: x[2])
    return out, stats
