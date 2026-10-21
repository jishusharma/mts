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

    def test_reminder_on_later_prompt_no_git(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="m1")
        with mock.patch.object(rl, "git_fetch", side_effect=AssertionError("git used")):
            t = self.hook("what is the BTC read?", sid="m1")
        self.assertLessEqual(t.count(chr(10))+1, 2)
        self.assertIn("Role: Eagle_Eyes v1 (token ", t)
        self.assertIn("ROLE CONTEXT LOST", t)
        self.assertEqual(self.hook("what is the BTC read?", sid="none"), "")

    def test_session_start_reinjects_recorded_role(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="r1")
        t = self.hook("", sid="r1", event="SessionStart")
        self.assertTrue(t.startswith("Session resumed/compacted: re-confirm"))
        self.assertIn("ROLE LOADED: Eagle_Eyes", t)

    def test_session_start_without_role_is_silent(self):
        self.put_role()
        self.assertEqual(self.hook("", sid="fresh", event="SessionStart"), "")


class TestVerify(Base):
    """SV1 (SUPERVISOR.md): the supervisor checks a worker's banner before trusting its claim."""
    def setUp(self):
        super().setUp()
        self.text = self.put_role(role_text(trig="eagle_eyes"))
        self.at = {("abcd1234", f"{rl.ROLES_REL}/eagle_eyes.md"): self.text}
        self.on_trunk = {"abcd1234"}
        for x in [mock.patch.object(rl, "git_show_at", lambda repo, rev, rel: self.at.get((rev, rel))),
                  mock.patch.object(rl, "git_is_ancestor", lambda repo, sha: sha in self.on_trunk)]:
            x.start()
            self.addCleanup(x.stop)
        self.good = rl.banner("Eagle_Eyes", "v1", rl.compute_token(self.text), "eagle_eyes.md", "abcd1234")

    def verify(self, note, role=None, sid=None):
        out = []
        return rl.verify(note, self.repo, role=role, sid=sid, out=out.append), " ".join(out)

    def test_good_banner_in_a_note(self):
        code, msg = self.verify("Done.\n" + self.good + "\nResult: x shipped 1234abcd")
        self.assertEqual(code, 0, msg)
        self.assertIn("fresh", msg)

    def test_missing_banner_and_not_loaded(self):
        self.assertEqual(self.verify("I did the card. sha 1234abcd")[0], 1)
        self.assertEqual(self.verify("ROLE NOT LOADED: malformed header")[0], 1)

    def test_row_only_banner_is_not_trusted(self):
        row = rl.banner("Eagle_Eyes", "v?", "none", "eagle_eyes.md", "abcd1234", row_only=True)
        self.assertEqual(self.verify(row)[0], 1)

    def test_wrong_token_version_role_or_path(self):
        tok = rl.compute_token(self.text)
        for bad in [self.good.replace(tok, "able-acid"), self.good.replace(" v1 ", " v2 "),
                    self.good.replace("roles/eagle_eyes.md", "roles/lab_guy.md")]:
            self.assertEqual(self.verify(bad)[0], 1, bad)
        self.assertEqual(self.verify(self.good, role="Lab_Guy")[0], 1)
        self.assertEqual(self.verify(self.good, role="Eagle_Eyes")[0], 0)

    def test_sha_not_on_trunk(self):
        self.on_trunk = set()
        self.assertEqual(self.verify(self.good)[0], 1)

    def test_role_changed_since_load_is_stale_exit_2(self):
        self.put_role(role_text(trig="eagle_eyes", body=BODY + "new duty\n"))
        code, msg = self.verify(self.good)
        self.assertEqual(code, 2, msg)
        self.assertIn("STALE", msg)

    def test_hook_state_must_match_when_sid_given(self):
        self.assertEqual(self.verify(self.good, sid="w1")[0], 1)   # hook never injected for w1
        self.hook("You are Eagle_Eyes.", sid="w1")
        self.assertEqual(self.verify(self.good, sid="w1")[0], 0)

    def test_supervisor_is_a_known_role(self):
        self.assertIn("Supervisor", rl.KNOWN_ROLES)

    def test_cli_reads_stdin(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "verify", "--text", "-"], input="no banner here",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)


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

    def test_merged_roles_and_aliases_open_the_new_role(self):
        """Operator 2026-10-20: 7 top-level roles; old names stay aliases; a name may start with a digit."""
        roles = rl.local_roles(REPO)
        for new_name in ("1985Artifacts_Guy", "Admin_Guy", "Pipeliner", "Eagle_Eyes", "Lab_Guy", "MTS_Doctor", "Supervisor"):
            self.assertIn(new_name, roles)
        for gone in ("Artifacts_Guy", "Q&A_Helper", "Network_Admin_Guy", "Traffic_Controller"):
            self.assertNotIn(gone, roles)
        want = {"You are 1985Artifacts_Guy.": "1985Artifacts_Guy", "You are Artifacts_Guy.": "1985Artifacts_Guy",
                "You are Admin_Guy.": "Admin_Guy", "You are Q&A_Helper.": "Admin_Guy", "You are Network_Admin_Guy.": "Admin_Guy",
                "You are Traffic_Controller.": "Pipeliner", "You are Pipeliner.": "Pipeliner", "Start the Pipeliner.": "Pipeliner"}
        for prompt, name in want.items():
            self.assertEqual(rl.match_roles(prompt, roles), [name], prompt)

    def test_every_role_and_alias_has_a_file_and_banner(self):
        for name in rl.KNOWN_ROLES:
            f = REPO / rl.ROLES_REL / rl.file_for(name)
            self.assertTrue(f.exists(), name)
            h = rl.parse_header(f.read_bytes().decode("utf-8").replace("\r\n", "\n"))
            self.assertEqual(h["name"], name)
        import lease
        self.assertEqual(tuple(rl.SINGLETON_ROLES), tuple(lease.SINGLETONS))   # the loader and the lease agree on who is single
        self.assertEqual(lease.SINGLETONS, ("Pipeliner",))
        for alias_of, olds in rl.ALIASES.items():
            self.assertIn(alias_of, rl.KNOWN_ROLES)
            self.assertTrue(olds)

    def test_admin_guy_file_carries_the_guardrails_and_backlog_flow(self):
        text = (REPO / rl.ROLES_REL / "admin_guy.md").read_text(encoding="utf-8")
        for needle in ("VERBATIM", "Sonnet 5.5", "effort medium", "tasks.py new", "sync.py ship", "mts_signal.py send", "BACKLOG"):
            self.assertIn(needle, text)

    def test_admin_guy_runs_on_sonnet_everywhere(self):
        # operator 2026-10-21: Admin_Guy off Haiku (bug-haiku-stale-rule-answers; research/model_economics_2026-10-21.md)
        role = next(r for r in rl.load_roster(REPO) if r["name"] == "Admin_Guy")
        self.assertTrue(role["model"].startswith("Sonnet 5.5"), role["model"])
        self.assertEqual(role["lane"], "SONNET")
        for rel in ("MyTradingSys/system/START_HERE.txt", "MyTradingSys/system/ROLES.md", f"{rl.ROLES_REL}/admin_guy.md"):
            text = (REPO / rel).read_text(encoding="utf-8")
            admin = [ln for ln in text.splitlines() if "Admin_Guy" in ln or "Model :" in ln[:9]]
            self.assertFalse([ln for ln in admin if "Haiku 5.5" in ln and "Admin_Guy" in ln], rel)
        self.assertNotIn("Haiku 5.5, effort HIGH", (REPO / "MyTradingSys/system/START_HERE.txt").read_text(encoding="utf-8"))

    def test_thinker_role_registered_with_triggers_row_and_guardrails(self):
        """Operator 2026-10-20: a Thinker design-partner role; Opus-capable, never builds, records choices verbatim."""
        self.assertIn("Thinker", rl.KNOWN_ROLES)
        roles = rl.local_roles(REPO)
        self.assertIn("Thinker", roles)
        for prompt in ("You are Thinker.", "I need a thinker", "You are thinker_guy", "You are Think_Guy.", "be the think guy"):
            self.assertEqual(rl.match_roles(prompt, roles), ["Thinker"], prompt)
        self.assertEqual(rl.banner("Thinker", "v1", "a-b", "thinker.md", "abc12345").split(":")[0], "ROLE LOADED")
        self.assertIn("Thinker", rl.row_names(REPO))
        text = (REPO / rl.ROLES_REL / "thinker.md").read_text(encoding="utf-8")
        for needle in ("Opus", "LITE", "no cap", "traffic.py budget", "RECOMMEND", "OPERATOR_DECISIONS.md", "tasks.py new",
                       "Improvement scan", "`waste`", "Never", "PENDING OPERATOR"):
            self.assertIn(needle, text)
        rolesmd = (REPO / rl.ROLES_MD_REL).read_text(encoding="utf-8")
        self.assertIn("| `Thinker` |", rolesmd)
        self.assertIn("You are Thinker.", (REPO / "MyTradingSys/system/START_HERE.txt").read_text(encoding="utf-8"))
        import role_hook_launcher as rhl
        self.assertIn("Thinker", rhl.KNOWN)


if __name__ == "__main__":
    unittest.main()
