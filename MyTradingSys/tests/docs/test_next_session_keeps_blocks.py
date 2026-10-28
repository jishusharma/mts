"""NEXT_SESSION.md is shared: a session adds or edits its own block and never drops another session's (plain pilot 2026-10-22)."""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import check_handoff as H  # noqa: E402

REL = "MyTradingSys/system/NEXT_SESSION.md"
OLD = "# NEXT_SESSION\n\n## Desk R2\nx\n\n## Live host\ny\n"


class DroppedBlocks(unittest.TestCase):
    def test_a_replaced_file_names_every_lost_block(self):
        self.assertEqual(H.dropped_blocks(OLD, "# NEXT_SESSION\n\nTask: card three\n"), ["Desk R2", "Live host"])

    def test_adding_or_editing_a_block_loses_nothing(self):
        self.assertEqual(H.dropped_blocks(OLD, OLD.replace("x", "x2") + "\n## Mine\nz\n"), [])

    def test_a_block_moved_to_history_is_not_lost(self):
        self.assertEqual(H.dropped_blocks(OLD, "# NEXT_SESSION\n\n## Live host\ny\n", "## Desk R2\nx"), [])


def base_ref():
    """The trunk commit this tree started from, not trunk now: CI tests an older commit after later hand-overs landed (ab82fc75 and
    ecd83de0 went red on the Supervisor's block appended after them). A local tree behind trunk merges it before shipping."""
    r = subprocess.run(["git", "-C", str(REPO), "merge-base", "HEAD", "origin/fast-track"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


class ShippedFileKeepsTrunkBlocks(unittest.TestCase):
    def test_working_file_keeps_every_block_on_trunk(self):
        base = base_ref()
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{base}:{REL}"], capture_output=True) if base else None
        if not r or r.returncode:
            self.skipTest("origin/fast-track not available")
        hist = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                         for p in (REPO / "MyTradingSys/system/handoff_history").glob("*.md"))
        lost = H.dropped_blocks(r.stdout.decode("utf-8"), (REPO / REL).read_text(encoding="utf-8"), hist)
        self.assertEqual(lost, [], f"NEXT_SESSION.md dropped other sessions' blocks: {lost}. Add your block; do not replace the file.")


class BaseIsWhereThisTreeLeftTrunk(unittest.TestCase):
    def test_an_older_commit_is_checked_against_itself_not_later_trunk(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            g = lambda *a: subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True).stdout.strip()
            g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
            g("commit", "-q", "--allow-empty", "-m", "old")
            old = g("rev-parse", "HEAD")
            g("commit", "-q", "--allow-empty", "-m", "later hand-over")
            g("update-ref", "refs/remotes/origin/fast-track", "HEAD")
            g("checkout", "-q", old)
            global REPO
            keep, REPO = REPO, Path(d)
            try:
                self.assertEqual(base_ref(), old)
            finally:
                REPO = keep


if __name__ == "__main__":
    unittest.main()
