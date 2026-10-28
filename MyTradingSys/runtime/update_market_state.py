"""update_market_state.py - Update current_market_state.md from latest snapshot.

Reads the latest snapshot from runtime_data/snapshots/, diffs against current state,
and writes the updated state back. Atomic write (tmp + rename).

Run after every snapshot:
    python ./MyTradingSys/runtime/update_market_state.py
"""
import sys
import json
import glob
import os
import tempfile
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "MyTradingSys" / "runtime"
SNAPSHOT_DIR = ROOT / "runtime_data" / "snapshots"
STATE_FILE = RUNTIME / "current_market_state.md"

sys.path.insert(0, str(RUNTIME))
from mts_math import parse_state, diff_state, update_state, format_state


def find_latest_snapshot():
    files = sorted(glob.glob(str(SNAPSHOT_DIR / "BTCUSDT_*.json")), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError("No snapshots found in " + str(SNAPSHOT_DIR))
    return files[-1]


def load_snapshot(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".state_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main():
    snap_path = find_latest_snapshot()
    print("SNAPSHOT:", snap_path)
    print("STATE:   ", STATE_FILE)

    old_state = {}
    if STATE_FILE.exists():
        old_state = parse_state(str(STATE_FILE))
        print("  loaded old state, updated_utc:", old_state.get("META", {}).get("updated_utc", "(none)"))
    else:
        print("  no existing state file, starting fresh")

    snapshot = load_snapshot(snap_path)

    delta = diff_state(old_state, snapshot)
    print()
    print("DELTA:")
    print("  price_delta_pct:   ", delta.get("price_delta_pct"))
    print("  structural_change: ", delta.get("structural_change"))
    print("  state_transition:  ", delta.get("state_transition"))
    print("  unchanged_count:   ", delta.get("unchanged_count"))
    print("  changes:           ", len(delta.get("changes", [])))
    for c in delta.get("changes", [])[:8]:
        print("    -", c.get("field"), ":", c.get("old"), "->", c.get("new"), "[" + c.get("significance", "") + "]")
    if delta.get("substate_changes"):
        for s in delta["substate_changes"]:
            print("    SUBSTATE", s.get("zone"), ":", s.get("old_substate"), "->", s.get("new_substate"))

    new_state = update_state(old_state, snapshot)

    content = format_state(new_state)
    atomic_write(STATE_FILE, content)

    print()
    print("WROTE:", STATE_FILE)
    print("  new updated_utc:", new_state.get("META", {}).get("updated_utc"))
    print("  size:", STATE_FILE.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
