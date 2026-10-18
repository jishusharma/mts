"""scripts/dev/role_loader.py: role triggers, derived tokens, banner injection, SessionStart re-inject, check."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "role_loader.py"
sys.path.insert(0, str(SCRIPT.parent))
import role_loader as rl  # noqa: E402

BODY = "# Eagle_Eyes\n\nBOOT (once)\n1. `python scripts/dev/sync.py start live-market-reader`. Work in the worktree.\n"


def role_text(name="Eagle_Eyes", ver="v1", tok="PENDING", trig="eagle_eyes, eagle eyes", body=BODY):
    return f"<!-- role: {name} | version: {ver} | token: {tok} | triggers: {trig} -->\n{body}"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / rl.ROLES_REL).mkdir(parents=True)
        self.trunk = {}
        p = [mock.patch.dict("os.environ", {"MTS_ROLES_HOME": str(Path(self.tmp.name) / "state")}),
             mock.patch.object(rl, "git_fetch", lambda repo: self.fetch_ok),
             mock.patch.object(rl, "git_show", lambda repo, rel: self.trunk.get(rel)),
             mock.patch.object(rl, "git_sha8", lambda repo: "abcd1234")]
        self.fetch_ok = True
        for x in p:
            x.start()
            self.addCleanup(x.stop)

    def hook(self, prompt, sid="s1", event="UserPromptSubmit"):
        out = rl.handle({"prompt": prompt, "session_id": sid, "hook_event_name": event}, self.repo)
        return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""

    def put_role(self, text=None):
        text = text or role_text()
        self.trunk[f"{rl.ROLES_REL}/eagle_eyes.md"] = text
        (self.repo / rl.ROLES_REL / "eagle_eyes.md").write_text(text, encoding="utf-8", newline="\n")
        return text


class TestTrigger(Base):
    def test_matches(self):
        for p in ["You are Eagle_Eyes. Go.", "you are eagle eyes", "I need a pipeliner", "Start an Eagle_Eyes session",
                  "Hi.\nbe the live chart runner", "role: Lab_Guy"]:
            self.assertTrue(rl.match_roles(p, rl.local_roles(REPO)), p)

    def test_non_matches(self):
        for p in ["we discussed eagle eyes yesterday", "please show pipeliner status", 'he wrote "You are Eagle_Eyes" in the log',
                  "you are not eagle eyes", "x" * 300 + " you are eagle_eyes", ""]:
            self.assertEqual(rl.match_roles(p, rl.local_roles(self.repo)), [], p)

    def test_no_match_is_silent_and_touches_no_git(self):
        with mock.patch.object(rl, "git_fetch", side_effect=AssertionError("git used")):
            self.assertEqual(self.hook("fix the bug in sync.py"), "")

    def test_two_roles_inject_neither_and_ask(self):
        self.put_role()
        t = self.hook("You are Eagle_Eyes.\nYou are Lab_Guy.")
        self.assertIn("ask the operator", t)
        self.assertNotIn("ROLE LOADED", t)
        self.assertEqual(rl.injected("s1"), [])


class TestToken(Base):
    def test_deterministic_and_changes_on_edit(self):
        a = role_text()
        self.assertEqual(rl.compute_token(a), rl.compute_token(a.replace("PENDING", "cart-heat")))
        self.assertNotEqual(rl.compute_token(a), rl.compute_token(a + "one more line\n"))
        self.assertRegex(rl.compute_token(a), r"^[a-z]+-[a-z]+$")

    def test_word_list(self):
        self.assertEqual(len(rl.WORDS), 256)
        self.assertEqual(len(set(rl.WORDS)), 256)

    def test_check_detects_stale_pending_ok(self):
        f = self.repo / rl.ROLES_REL / "eagle_eyes.md"
        f.write_text(role_text(), encoding="utf-8", newline="\n")
        lines = []
        self.assertEqual(rl.check(self.repo, lines.append), 0)            # PENDING tolerated
        self.assertTrue(any("PENDING" in x for x in lines))
        rl.retoken_file(f)
        self.assertEqual(rl.check(self.repo, lambda x: None), 0)          # fresh
        f.write_text(f.read_text(encoding="utf-8") + "an edit\n", encoding="utf-8", newline="\n")
        lines = []
        self.assertEqual(rl.check(self.repo, lines.append), 1)            # real edit -> stale
        self.assertTrue(any("STALE" in x for x in lines))

    def test_check_malformed_header_fails(self):
        (self.repo / rl.ROLES_REL / "eagle_eyes.md").write_text("# no header\n", encoding="utf-8", newline="\n")
        self.assertEqual(rl.check(self.repo, lambda x: None), 1)

    def test_row_without_file_warns_exit0(self):
        (self.repo / "MyTradingSys/system/ROLES.md").write_text("## Rows\n| Role | Job |\n|---|---|\n| Pipeliner | x |\n",
                                                                encoding="utf-8", newline="\n")
        lines = []
        self.assertEqual(rl.check(self.repo, lines.append), 0)
        self.assertTrue(any(x.startswith("WARN Pipeliner") for x in lines))


class TestInject(Base):
    def test_banner_and_file_injected(self):
        text = self.put_role()
        t = self.hook("You are Eagle_Eyes. Go.")
        tok = rl.compute_token(text)
        self.assertTrue(t.startswith("ROLE LOADER (hook): you are Eagle_Eyes"))
        self.assertIn(f"ROLE LOADED: Eagle_Eyes v1 · token {tok} · MyTradingSys/system/roles/eagle_eyes.md @ abcd1234", t)
        self.assertIn("FIRST ACTION: 1. `python scripts/dev/sync.py start live-market-reader`", t)
        self.assertIn(BODY, t)

    def test_stale_fetch_flagged(self):
        self.put_role()
        self.fetch_ok = False
        self.assertIn("STALE: fetch failed", self.hook("You are Eagle_Eyes."))

    def test_row_only_fallback(self):
        self.trunk[rl.ROLES_MD_REL] = "## Rows\n| Eagle_Eyes | watches | boot |\n"
        t = self.hook("You are Eagle_Eyes.")
        self.assertIn("ROLE LOADED (ROW ONLY): Eagle_Eyes", t)
        self.assertIn("| Eagle_Eyes | watches", t)

    def test_no_file_no_row(self):
        self.assertIn("ROLE NOT LOADED", self.hook("You are Eagle_Eyes."))

    def test_no_reinject_same_session_until_reload(self):
        self.put_role()
        self.assertTrue(self.hook("You are Eagle_Eyes."))
        self.assertEqual(self.hook("You are Eagle_Eyes again"), "")
        self.assertTrue(self.hook("reload role Eagle_Eyes"))
        self.assertTrue(self.hook("You are Eagle_Eyes.", sid="other"))

    def test_session_start_reinjects_recorded_role(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="r1")
        t = self.hook("", sid="r1", event="SessionStart")
        self.assertTrue(t.startswith("Session resumed/compacted: re-confirm"))
        self.assertIn("ROLE LOADED: Eagle_Eyes", t)

    def test_session_start_without_role_is_silent(self):
        self.put_role()
        self.assertEqual(self.hook("", sid="fresh", event="SessionStart"), "")


class TestProcess(unittest.TestCase):
    def test_garbage_stdin_exits_0_silently(self):
        for data in ["", "not json", "[1,2]", '{"prompt": 5}']:
            r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=data, capture_output=True, text=True)
            self.assertEqual((r.returncode, r.stdout), (0, ""), data)


class TestRepoRoles(unittest.TestCase):
    def test_every_role_file_has_valid_header(self):
        files = rl.role_files(REPO)
        self.assertTrue(files)
        for f in files:
            self.assertIsNotNone(rl.parse_header(f.read_bytes().decode("utf-8").replace("\r\n", "\n")), f.name)

    def test_check_passes_on_repo(self):
        self.assertEqual(rl.check(REPO, lambda x: None), 0)


if __name__ == "__main__":
    unittest.main()
