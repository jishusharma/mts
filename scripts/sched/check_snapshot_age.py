"""Check 4: newest runtime_data/snapshots/BTCUSDT_*.json older than the supervisor's own stale limit.

Threshold source: scripts/core supervisor `[int]$SnapshotStaleSec = 150` (the existing cadence rule), RED above it.
No snapshots at all -> RED. Hash = check + stale|fresh + newest file name (age excluded so it debounces).
"""
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, emit, run

STALE_SEC = 150


def main():
    files = list((REPO / "runtime_data" / "snapshots").glob("BTCUSDT_*.json"))
    if not files:
        return emit("snapshot_age", "RED", "no BTCUSDT snapshots found", ["none"])
    newest = max(files, key=lambda p: p.stat().st_mtime)
    age = time.time() - newest.stat().st_mtime
    if age > STALE_SEC:
        return emit("snapshot_age", "RED", f"newest {newest.name} is {int(age)}s old (> {STALE_SEC}s)",
                    ["stale", newest.name])
    return emit("snapshot_age", "OK", f"newest {newest.name} {int(age)}s old", ["fresh"])


if __name__ == "__main__":
    run(main)
