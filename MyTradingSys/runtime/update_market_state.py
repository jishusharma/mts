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
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "MyTradingSys" / "runtime"
SNAPSHOT_DIR = ROOT / "runtime_data" / "snapshots"
STATE_FILE = RUNTIME / "current_market_state.md"

sys.path.insert(0, str(RUNTIME))
from mts_math import parse_state, diff_state, update_state, format_state


# ANALYST_LEVELS: display-only NOTE layer. Never a trade input; any failure gives 'no levels'.
# LEVELS_TIMEOUT_S and LEVELS_MAX_AGE_S are OURS (no source quote): short so the state refresh is never held up.
LEVELS_SCRIPT = ROOT / "scripts" / "dev" / "analyst_levels.py"
LEVELS_TIMEOUT_S = 25
LEVELS_MAX_AGE_S = 3600
NO_LEVELS = "no levels"


def fetch_levels(timeout=LEVELS_TIMEOUT_S):
    """Run analyst_levels.py --json; return the parsed dict or None on any error/timeout/bad output."""
    try:
        r = subprocess.run([sys.executable, str(LEVELS_SCRIPT), "--json"], capture_output=True,
                           text=True, timeout=timeout, encoding="utf-8", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            return None
        data = json.loads(r.stdout)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def levels_section(data, now=None):
    """Text for the ANALYST_LEVELS section: nearest open level above/below price. Fails closed."""
    now = now or datetime.now(timezone.utc)
    lines = ["## ANALYST_LEVELS", "note: display only, not a trade input"]
    try:
        price = float(data["price"])
        asof = datetime.fromisoformat(data["asof"])
        if asof.tzinfo is None:
            asof = asof.replace(tzinfo=timezone.utc)
        if abs((now - asof).total_seconds()) > LEVELS_MAX_AGE_S:
            raise ValueError("stale")
        lv = [x for x in data["levels"] if not x.get("expired")]
        above = sorted((x for x in lv if float(x["level"]) > price), key=lambda x: x["level"])
        below = sorted((x for x in lv if float(x["level"]) <= price), key=lambda x: -x["level"])
        if not above and not below:
            raise ValueError("empty")

        def row(tag, x):
            lines.append("%s: %s | %s | published %s | %s" % (
                tag, x["level"], x["analyst"], str(x["published"])[:10], "hit" if x.get("hit") else "open"))

        for tag, grp in (("nearest_above", above), ("nearest_below", below)):
            if grp:
                row(tag, grp[0])
            else:
                lines.append("%s: %s" % (tag, NO_LEVELS))
        lines.append("price: %s" % price)
        lines.append("asof: %s" % data["asof"])
    except Exception:
        lines = ["## ANALYST_LEVELS", "note: display only, not a trade input", "levels: " + NO_LEVELS]
    return "\n".join(lines) + "\n"


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
        old_state.pop("ANALYST_LEVELS", None)  # note layer is rebuilt every run, never diffed
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
    try:
        sec = levels_section(fetch_levels())
    except Exception:
        sec = "## ANALYST_LEVELS\nlevels: " + NO_LEVELS + "\n"
    content = content.rstrip("\n") + "\n\n" + sec
    atomic_write(STATE_FILE, content)

    print()
    print("WROTE:", STATE_FILE)
    print("  new updated_utc:", new_state.get("META", {}).get("updated_utc"))
    print("  size:", STATE_FILE.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
