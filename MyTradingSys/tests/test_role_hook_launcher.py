"""scripts/dev/role_hook_launcher.py: a role request in a checkout without the project hook still loads from trunk
or says ROLE NOT LOADED; no double run when the project hook exists; install is idempotent."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import role_hook_launcher as rhl  # noqa: E402

ROLE = ("<!-- role: Lead | version: v1 | token: PENDING | triggers: lead -->\n# Lead\n\nBOOT (once)\n"
        "1. `python scripts/dev/sync.py start lead`. Work in the worktree.\n")


def git(d, *a):
    subprocess.run(["git", "-C", str(d), "-c", "user.email=t@t", "-c", "user.name=t", *a], check=True, capture_output=True)


def payload(cwd, sid="s", prompt="You are Lead."):
    return {"hook_event_name": "UserPromptSubmit", "session_id": sid, "cwd": str(cwd), "prompt": prompt}


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        os.environ["MTS_ROLES_HOME"] = str(Path(self.tmp.name) / "state")
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "MyTradingSys").mkdir(parents=True)
        git(self.repo.parent, "init", "-q", str(self.repo))
        (self.repo / "MyTradingSys" / "old.txt").write_text("x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "old")           # old commit: no loader, no hook
        git(self.repo, "branch", "old")
        (self.repo / "scripts" / "dev").mkdir(parents=True)
        (self.repo / "scripts" / "dev" / "role_loader.py").write_text(
            (REPO / "scripts" / "dev" / "role_loader.py").read_text(encoding="utf-8"), encoding="utf-8")
        d = self.repo / "MyTradingSys" / "system" / "roles"
        d.mkdir(parents=True)
        (d / "lead.md").write_text(ROLE, encoding="utf-8", newline="\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "trunk")
        git(self.repo, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
        git(self.repo, "checkout", "-q", "old")         # session folder = old commit

    def test_old_checkout_loads_from_trunk(self):
        out = json.loads(rhl.run(payload(self.repo)))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("you are Lead", out)
        self.assertIn("ROLE LOADED", out)

    def test_non_role_prompt_silent(self):
        self.assertEqual(rhl.run(payload(self.repo, prompt="hello")), "")

    def test_project_hook_present_no_double_run(self):
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "settings.json").write_text('{"hooks": {"x": "role_loader.py hook"}}')
        self.assertEqual(rhl.run(payload(self.repo)), "")

    def test_no_trunk_loader_says_not_loaded(self):
        git(self.repo, "update-ref", "-d", "refs/remotes/origin/fast-track")
        out = json.loads(rhl.run(payload(self.repo)))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("ROLE NOT LOADED", out)

    def test_install_idempotent_and_reversible(self):
        h = Path(self.tmp.name) / "home"
        h.mkdir()
        (h / "settings.json").write_text('{"model": "m"}')
        rhl.install(h)
        rhl.install(h)
        d = json.loads((h / "settings.json").read_text())
        self.assertEqual([len(d["hooks"][e]) for e in ("SessionStart", "UserPromptSubmit")], [1, 1])
        rhl.install(h, add=False)
        self.assertEqual(json.loads((h / "settings.json").read_text()), {"model": "m"})


if __name__ == "__main__":
    unittest.main()
