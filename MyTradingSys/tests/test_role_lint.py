"""MyTradingSys/tests/test_role_lint.py: tests for `role_loader.py lint` (RU4)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "role_loader.py"
sys.path.insert(0, str(SCRIPT.parent))
import role_loader as rl  # noqa: E402


def _make_role(name, body):
    raw = f"<!-- role: {name} | version: v1 | token: PENDING | triggers: {name.lower()} -->\n{body}"
    tok = rl.compute_token(raw)
    return f"<!-- role: {name} | version: v1 | token: {tok} | triggers: {name.lower()} -->\n{body}"


CLEAN_ROLES_MD = """# ROLES

## Rows
| Role | Job | Boot | Output | Model |
|---|---|---|---|---|
| Eagle_Eyes | Observe | `MyTradingSys/system/roles/eagle_eyes.md` | log | Sonnet |

## Rules for every role
- Work in the worktree `sync.py start <slug>` prints; never the live tree. Share only through `sync.py ship`.
- Opus only as in WORKERS.md rule 6.
- No compaction (operator 2026-10-18): a role session runs under the turn budget in WORKERS.md rule 5 and is replaced by its one-line start prompt when it is over it.
- Roles report; they do not trade, deploy, restart, touch HALT files or read `.secrets/`.
"""

CLEAN_EAGLE_BODY = """# Eagle_Eyes
Read first: `MyTradingSys/system/ROLES.md` (rule answers: read this turn, else `NOT_IN_DATA`).

You are the standing LIVE MARKET READER for MTS. This session is never compacted.

BOOT (once per session, then again only in a replacement session)
1. `python scripts/dev/sync.py start live-market-reader`.
2. Read `MyTradingSys/system/ROLES.md`.

NO COMPACTION
No compaction (operator 2026-10-18); the turn budget applies.
"""


class TestRoleLint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "MyTradingSys/system/roles").mkdir(parents=True)
        (self.repo / "scripts/dev").mkdir(parents=True)
        (self.repo / "scripts/dev/sync.py").write_text("# stub\n", encoding="utf-8", newline="\n")
        (self.repo / "MyTradingSys/system/ROLES.md").write_text(CLEAN_ROLES_MD, encoding="utf-8", newline="\n")
        (self.repo / "MyTradingSys/system/roles/eagle_eyes.md").write_text(
            _make_role("Eagle_Eyes", CLEAN_EAGLE_BODY), encoding="utf-8", newline="\n"
        )

    def run_lint(self, repo=None):
        lines = []
        code = rl.lint(repo or self.repo, out=lines.append)
        return code, "\n".join(lines)

    def test_clean_fixture_exits_0(self):
        code, out = self.run_lint()
        self.assertEqual(code, 0, out)

    def test_compaction_contradiction_exits_1(self):
        # Historical eagle_eyes.md v1 compaction contradiction vs ROLES.md:40 "No compaction"
        contradictory_body = (
            "# Eagle_Eyes\n"
            "This session is long-lived: the operator compacts it and keeps it pinned.\n"
            "BOOT (once per session, then only after a compaction)\n"
            "1. `python scripts/dev/sync.py start live-market-reader`.\n\n"
            "COMPACTION\n"
            "The operator compacts this session. After a compaction re-run only step 2 of BOOT.\n"
        )
        (self.repo / "MyTradingSys/system/roles/eagle_eyes.md").write_text(
            _make_role("Eagle_Eyes", contradictory_body), encoding="utf-8", newline="\n"
        )
        code, out = self.run_lint()
        self.assertEqual(code, 1, out)
        self.assertIn("CONTRADICTION", out)
        self.assertIn("eagle_eyes.md", out)

    def test_dead_command_path_exits_1(self):
        bad_cmd_body = CLEAN_EAGLE_BODY + "\nRun `python scripts/dev/nonexistent_xyz.py --check`.\n"
        (self.repo / "MyTradingSys/system/roles/eagle_eyes.md").write_text(
            _make_role("Eagle_Eyes", bad_cmd_body), encoding="utf-8", newline="\n"
        )
        code, out = self.run_lint()
        self.assertEqual(code, 1, out)
        self.assertIn("DEAD-CMD", out)
        self.assertIn("scripts/dev/nonexistent_xyz.py", out)

    def test_missing_referenced_file_exits_1(self):
        missing_file_body = CLEAN_EAGLE_BODY + "\nRead `MyTradingSys/system/DOES_NOT_EXIST_XYZ.md` first.\n"
        (self.repo / "MyTradingSys/system/roles/eagle_eyes.md").write_text(
            _make_role("Eagle_Eyes", missing_file_body), encoding="utf-8", newline="\n"
        )
        code, out = self.run_lint()
        self.assertEqual(code, 1, out)
        self.assertIn("MISSING-FILE", out)
        self.assertIn("MyTradingSys/system/DOES_NOT_EXIST_XYZ.md", out)

    def test_ci_red_owner_line(self):
        runs_green = [{"conclusion": "success", "head_sha": "11112222"}]
        self.assertIn("green", rl.ci_red_owner(self.repo, runs=runs_green))
        runs_red = [{"conclusion": "failure", "head_sha": "deadbeef1234"}, {"conclusion": "failure", "head_sha": "deadbeef0000"}]
        line = rl.ci_red_owner(self.repo, runs=runs_red)
        self.assertIn("CI red and owner: RED", line)
        self.assertIn("deadbeef", line)

    def test_repo_clean_roles_exit_0_via_cli(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "lint"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
