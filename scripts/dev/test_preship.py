"""preship.py: the ship gate's frequent failures are caught at edit and at `git commit` time (operator 2026-10-22)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preship as P

PASS = [sys.executable, "-c", "pass"]
FAIL = [sys.executable, "-c", "import sys; print('FAIL: over cap'); sys.exit(1)"]


def git(root, *a):
    subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)


class PreshipTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name) / "repo"
        self.root.mkdir()
        os.environ["MTS_STOP_GUARD_HOME"] = str(Path(self.d.name) / "state")
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@t")
        git(self.root, "config", "user.name", "t")
        self._rules = P.RULES
        self.cmd = FAIL
        P.RULES = [("fake rule", lambda p: p.endswith(".md"), lambda r, ps: [self.cmd], True, "trim it", "test evidence")]

    def tearDown(self):
        P.RULES = self._rules
        os.environ.pop("MTS_STOP_GUARD_HOME", None)
        self.d.cleanup()

    def commit_hook(self, command, sid="s1"):
        return P.hook("hook-commit", json.dumps({"session_id": sid, "cwd": str(self.root), "tool_input": {"command": command}}))

    def stage(self, name="CLAUDE.md"):
        (self.root / name).write_text("x", encoding="utf-8")
        git(self.root, "add", name)

    def test_commit_with_a_failing_rule_is_denied_once_with_the_fix(self):
        self.stage()
        out = json.loads(self.commit_hook('git commit -m "x"'))["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("fake rule", out["permissionDecisionReason"])
        self.assertIn("FIX: trim it", out["permissionDecisionReason"])
        self.assertEqual(self.commit_hook('git commit -m "x"'), "")       # same failure: not blocked twice
        self.assertNotEqual(self.commit_hook('git commit -m "x"', sid="s2"), "")

    def test_passing_rule_unrelated_files_and_non_commit_commands_are_allowed(self):
        self.stage()
        self.cmd = PASS
        self.assertEqual(self.commit_hook("git commit -m x"), "")
        self.cmd = FAIL
        self.assertEqual(self.commit_hook("git status && git commit-tree x"), "")
        self.assertEqual(self.commit_hook("ls"), "")
        git(self.root, "reset", "-q")
        self.stage("a.py")
        self.assertEqual(self.commit_hook("git commit -m x"), "")       # no rule covers a.py

    def test_commit_forms_are_recognised(self):
        for c in ("git commit -m x", 'cd a && git -C "/x y" commit -q -F -', "git add . && git commit -am x", "(git commit)"):
            self.assertTrue(P.COMMIT.search(c), c)
        for c in ("git commit-tree x", "gitcommit", "git log --grep commit"):
            self.assertFalse(P.COMMIT.search(c), c)

    def test_commit_dash_a_includes_unstaged_tracked_edits(self):
        self.stage()
        git(self.root, "commit", "-qm", "base")
        (self.root / "CLAUDE.md").write_text("y", encoding="utf-8")
        self.assertEqual(self.commit_hook("git commit -m x"), "")       # nothing staged
        self.assertNotEqual(self.commit_hook("git commit -am x"), "")

    def test_edit_warns_once_per_rule_and_shows_a_fast_failure(self):
        f = self.root / "CLAUDE.md"
        f.write_text("x", encoding="utf-8")
        data = {"session_id": "s1", "tool_input": {"file_path": str(f)}}
        self.cmd = PASS
        note = json.loads(P.hook("hook-edit", json.dumps(data)))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("the ship gate checks this file", note)
        self.assertEqual(P.hook("hook-edit", json.dumps(data)), "")      # told once
        self.cmd = FAIL
        note = json.loads(P.hook("hook-edit", json.dumps(data)))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("now failing", note)
        self.assertEqual(P.hook("hook-edit", json.dumps(dict(data, tool_input={"file_path": str(self.root / "a.py")}))), "")

    def test_a_doc_size_cap_is_denied_every_time(self):
        P.RULES = [P.CAP_RULE[:2] + (lambda r, ps: [FAIL],) + P.CAP_RULE[3:]]
        self.stage()
        for _ in range(3):
            out = json.loads(self.commit_hook('git commit -m "x"'))["hookSpecificOutput"]
            self.assertEqual(out["permissionDecision"], "deny")
            self.assertIn("doc size cap", out["permissionDecisionReason"])

    def test_cap_failures_runs_the_real_cap_test_on_the_shipped_files_only(self):
        real = Path(__file__).resolve().parents[2] / P.CAP_TEST
        (self.root / P.CAP_TEST).parent.mkdir(parents=True)
        (self.root / P.CAP_TEST).write_text(real.read_text(encoding="utf-8"), encoding="utf-8")
        (self.root / "CLAUDE.md").write_text("x" * 100, encoding="utf-8")
        self.assertEqual(P.cap_failures(str(self.root), ["CLAUDE.md"]), [])
        (self.root / "CLAUDE.md").write_text("x" * 100_000, encoding="utf-8")
        self.assertIn("100000 <= ", " ".join(P.cap_failures(str(self.root), ["CLAUDE.md"])))
        self.assertEqual(P.cap_failures(str(self.root), ["a.py"]), [])            # no capped doc in the ship
        self.assertEqual(P.cap_failures(self.d.name, ["CLAUDE.md"]), [])          # a repo without the cap test

    def test_docs_ship_runs_the_doc_rules_only_and_sync_refuses_the_push(self):
        import sync
        other = ("own unit tests", lambda p: True, lambda r, ps: [FAIL], False, "-", "-")
        card = ("task cards", lambda p: p.endswith(".json"), lambda r, ps: [self.cmd], True, "fill the card", "-")
        P.RULES = [other, card]
        names = [r[0] for r, _ in P.docs_ship_failures(str(self.root), ["MyTradingSys/system/tasks/x.json"])]
        self.assertEqual(names, ["task cards"])
        with self.assertRaises(sync.SyncError) as e:
            sync.run_docs_gate(str(self.root), ["MyTradingSys/system/tasks/x.json"])
        self.assertIn("[task cards]", str(e.exception))
        self.assertIn("FIX: fill the card", str(e.exception))
        self.cmd = PASS
        self.assertEqual(P.docs_ship_failures(str(self.root), ["MyTradingSys/system/tasks/x.json"]), [])
        sync.run_docs_gate(str(self.root), ["MyTradingSys/system/tasks/x.json"])

    def test_off_switch_and_garbage_never_raise(self):
        self.stage()
        os.environ["MTS_PRESHIP"] = "off"
        try:
            self.assertEqual(self.commit_hook("git commit -m x"), "")
        finally:
            os.environ.pop("MTS_PRESHIP")
        self.assertEqual(P.hook("hook-commit", "not json"), "")
        self.assertEqual(P.hook("hook-edit", json.dumps({"tool_input": {"file_path": "/no/such/dir/f.md"}})), "")


class RealRulesTest(unittest.TestCase):
    """The real table routes the paths that went red in 2026-10-19..22 to a rule."""
    def names(self, path):
        return [r[0] for r, _ in P.rules_for([path])]

    def test_routing(self):
        self.assertIn("doc caps and contracts", self.names("CLAUDE.md"))
        self.assertIn("doc size cap", self.names("CLAUDE.md"))
        self.assertIn("role files", self.names("MyTradingSys/system/roles/builder.md"))
        self.assertIn("test file not in the gate", self.names("scripts/dev/test_new_thing.py"))
        self.assertNotIn("test file not in the gate", self.names("MyTradingSys/tests/test_new_thing.py"))
        self.assertIn("look-ahead lint", self.names("MyTradingSys/research/x/study.py"))
        self.assertIn("hook rows", self.names(".claude/settings.json"))
        self.assertEqual(self.names("README.txt"), [])

    def test_the_docs_ships_that_went_red_on_2026_10_23_reach_a_docs_ship_rule(self):
        for path in ("MyTradingSys/system/roles/supervisor.md", "MyTradingSys/system/ROLES.md",
                     "MyTradingSys/system/tasks/dsa-audit-04-clean-room-twin.json", "MyTradingSys/research/BUGS.md",
                     "MyTradingSys/system/groups.json"):
            with self.subTest(path=path):
                self.assertTrue(set(self.names(path)) & set(P.DOCS_SHIP_RULES))

    def test_a_repo_without_the_checkers_passes_a_docs_ship(self):
        """Ship 2026-10-24: test_sync's scratch repos have no doc cap test; the docs ship check failed them on 'file not found'."""
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(P.docs_ship_failures(d, ["CLAUDE.md", "MyTradingSys/system/roles/supervisor.md",
                                                      "MyTradingSys/system/tasks/x.json", "MyTradingSys/research/BUGS.md"]), [])

    def test_every_hook_mode_in_settings_exists(self):
        s = json.loads((Path(__file__).resolve().parents[2] / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for g in s["hooks"].values() for grp in g for h in grp["hooks"] if "preship.py" in h["command"]]
        self.assertEqual(sorted(c.split()[-1] for c in cmds), ["hook-commit", "hook-edit"])


if __name__ == "__main__":
    unittest.main()
