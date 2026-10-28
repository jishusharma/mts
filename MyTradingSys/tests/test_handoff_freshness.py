"""Hand-over blocks are history (operator 2026-10-21): STATUS.md must flag a block that newer commits have overtaken."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import make_status as ms  # noqa: E402

TEXT = """# NEXT_SESSION

## Live host move: STAGED 2026-10-21 (hand-over)
Plan: `MyTradingSys/system/LIVE_HOST_MOVE.md` and `scripts/dev/make_status.py`. Operator items next.

## Old thing 2026-10-01 (hand-over)
Nothing named here.
"""


def test_block_overtaken_by_newer_commits_is_stale():
    seen = {}

    def newer(paths, since):
        seen["paths"], seen["since"] = paths, since
        return ["abc1234 laptop settings done", "def5678 SIM decision"]

    lines = ms.get_handoff_freshness(TEXT, newer, root=str(Path(__file__).resolve().parents[2]))
    assert lines[0].startswith("STALE 2026-10-21") and "2 newer commits" in lines[0]
    assert seen["since"] == "2026-10-21" and "scripts/dev/make_status.py" in seen["paths"]
    assert lines[1].startswith("FRESH 2026-10-01")      # names no file: nothing can overtake it


def test_block_with_no_newer_commits_is_fresh():
    lines = ms.get_handoff_freshness(TEXT, lambda p, s: ["abc1234 the hand-over itself"], root=str(Path(__file__).resolve().parents[2]))
    assert lines[0].startswith("FRESH 2026-10-21")
