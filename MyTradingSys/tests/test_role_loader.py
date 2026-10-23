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

    def test_reminder_is_not_repeated_every_prompt(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="m2")
        got = [bool(self.hook("what is the BTC read?", sid="m2")) for _ in range(2 * rl.REMIND_EVERY)]
        self.assertEqual(sum(got), 2)
        self.assertTrue(got[0])

    def test_session_start_reinjects_recorded_role(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="r1")
        t = self.hook("", sid="r1", event="SessionStart")
        self.assertTrue(t.startswith("Session resumed/compacted: re-confirm"))
        self.assertIn("ROLE LOADED: Eagle_Eyes", t)

    def test_session_start_records_the_token_it_served_when_trunk_changed(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="r2")
        old = rl.role_meta("r2", "Eagle_Eyes")["token"]
        self.put_role(role_text(body=BODY + "A rule added after the session started.\n"))
        t = self.hook("", sid="r2", event="SessionStart")
        new = rl.compute_token(self.trunk[f"{rl.ROLES_REL}/eagle_eyes.md"].replace("\r\n", "\n"))
        self.assertNotEqual(old, new)
        self.assertIn(f"token {new}", t)
        self.assertEqual(rl.role_meta("r2", "Eagle_Eyes")["token"], new)    # the reminder and banner verify read this
        r = self.hook("what is the BTC read?", sid="r2")
        self.assertIn(f"token {new}", r)

    def test_session_start_without_role_is_silent(self):
        self.put_role()
        self.assertEqual(self.hook("", sid="fresh", event="SessionStart"), "")


class TestFallbackIsASoftHint(Base):
    """Flow A2 (operator 2026-10-23): a fallback-picked role (the word "revalidat" gave a doctor session Lab_Guy) came back after
    every compaction. Only an explicit `You are X.` line is a role session; role_loader and model_guard.role_session agree."""
    FALLBACK = "Here is a chart screenshot of BTC 15m, what do you see?"

    def fb(self, sid):
        pick = {"name": "Eagle_Eyes", "reason": "task text says screenshot", "tie": []}
        with mock.patch.object(rl, "pick_role", return_value=pick):
            return self.hook(self.FALLBACK, sid=sid)

    def test_fallback_role_is_not_reinjected_after_compaction(self):
        self.put_role()
        self.assertIn("(fallback: ", self.fb("f1"))
        self.assertEqual(self.hook("", sid="f1", event="SessionStart"), "")

    def test_fallback_role_gets_no_every_6th_prompt_reminder(self):
        self.put_role()
        self.fb("f2")
        got = [self.hook("what is the BTC read?", sid="f2") for _ in range(2 * rl.REMIND_EVERY)]
        self.assertEqual([g for g in got if g], [])

    def test_explicit_role_is_reinjected_and_reminded(self):
        self.put_role()
        self.hook("You are Eagle_Eyes.", sid="f3")
        self.assertIn("ROLE LOADED: Eagle_Eyes", self.hook("", sid="f3", event="SessionStart"))
        self.assertIn("Role: Eagle_Eyes", self.hook("what is the BTC read?", sid="f3"))

    def test_explicit_after_fallback_upgrades_the_role(self):
        self.put_role()
        self.fb("f4")
        self.hook("reload role Eagle_Eyes", sid="f4")
        self.assertIn("ROLE LOADED: Eagle_Eyes", self.hook("", sid="f4", event="SessionStart"))

    def test_rules_text_carries_the_out_of_role_rule(self):
        self.put_role()
        t = self.hook("You are Eagle_Eyes.", sid="f5")
        self.assertIn("OUT OF YOUR ROLE", t)
        self.assertIn("tasks.py new", t)
        self.assertIn("You are <Owner>.", t)


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

    def test_every_role_emits_under_the_hook_cap(self):
        """Claude Code truncates hook-injected text at 10,000 chars; the rest of a role would be silently lost."""
        def local_show(repo, rel):
            p = REPO / rel
            return p.read_bytes().decode("utf-8") if p.exists() else None
        with mock.patch.object(rl, "git_show", local_show), mock.patch.object(rl, "git_sha8", lambda r: "abcd1234"), \
                mock.patch.object(rl, "lease_suffix", lambda n, r: ""):
            for f in rl.role_files(REPO):
                h = rl.parse_header(f.read_bytes().decode("utf-8").replace("\r\n", "\n"))
                n = len(rl.build_text(h["name"], REPO, True))
                self.assertLess(n, 9500, f"{f.name} emits {n} chars")

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
        for needle in ("Opus", "LITE", "no cap", "traffic.py budget", "OPERATOR_DECISIONS.md", "tasks.py new",
                       "Improvement scan", "`waste`", "Never"):   # RECOMMEND / PENDING OPERATOR left the role in c2c2a3f14 (10k hook cap)
            self.assertIn(needle, text)
        rolesmd = (REPO / rl.ROLES_MD_REL).read_text(encoding="utf-8")
        self.assertIn("| `Thinker` |", rolesmd)
        self.assertIn("You are Thinker.", (REPO / "MyTradingSys/system/START_HERE.txt").read_text(encoding="utf-8"))
        import role_hook_launcher as rhl
        self.assertIn("Thinker", rhl.KNOWN)


class BootStepTests(unittest.TestCase):
    """boot_step must find the Boot section, not prose that merely starts with the word Boot (review 2026-10-22)."""

    def test_prose_line_before_heading_is_skipped(self):
        body = ("# R\nBoot reads only what Boot step 3 names (cite file:line + commit date, else NOT_IN_DATA).\n\n"
                "## Boot (once)\n1. `python scripts/dev/sync.py start x`.\n")
        self.assertEqual(rl.boot_step(body), "1. `python scripts/dev/sync.py start x`.")

    def test_every_real_role_names_its_first_command(self):
        for f in sorted((REPO / rl.ROLES_REL).glob("*.md")):
            step = rl.boot_step(f.read_text(encoding="utf-8"))
            self.assertNotIn("NOT_IN_DATA", step, f.name)
            self.assertNotIn("first step of the file", step, f.name)
            self.assertNotIn("Open `SUPER_LOOP.md`", step, f.name)

    def test_roles_md_is_an_index_under_1200_tokens(self):
        """roles-md-index-slim: ROLES.md holds the index, role prose lives in roles/*.md (~4 chars per token)."""
        text = (REPO / "MyTradingSys/system/ROLES.md").read_text(encoding="utf-8")
        self.assertLess(len(text) // 4, 1200)


class TestWrappedFirstPrompt(Base):
    """Failure review 2026-10-23 (cause 4): start_session wraps the brief; the role line was at char 644, behind a system-reminder."""
    WRAPPED = ("<system-reminder>\nThis is a git worktree: an isolated copy of the repository. Run all commands from this directory. "
               "Do NOT cd to the original repository root. The git stash stack is shared with the main checkout and all other "
               "worktrees; never use bare git stash. Is a git repository: true. Primary working directory: C:/x/.claude/worktrees/a-b-c1\n"
               "</system-reminder>\nBackground (from the session that started this one): the operator asked for a live chart read; "
               "the supervisor wants the Admin_Guy queue and a pipeliner check left alone, and the tokens, charts and files under runtime_data untouched.\nTask:\n"
               "You are Eagle_Eyes. Read the live BTC chart and report.\n")

    def test_fixture_is_realistic(self):
        self.assertGreater(self.WRAPPED.index("You are Eagle_Eyes"), 600)

    def test_role_line_past_char_600_behind_a_reminder_loads_the_role(self):
        self.put_role()
        out = self.hook(self.WRAPPED)
        self.assertIn("Eagle_Eyes", out)
        self.assertIn("BOOT (once)", out)

    def test_pasted_wrapper_and_reminder_then_role_line(self):
        self.put_role()
        out = self.hook('<system-reminder>notice</system-reminder>\n<pasted_content id="1">\nYou are Eagle_Eyes.\nGo\n</pasted_content>')
        self.assertIn("BOOT (once)", out)

    def test_role_words_inside_a_sentence_never_switch_roles(self):
        self.put_role()
        for i, p in enumerate((
                "<system-reminder>n</system-reminder>\nBackground: x\nTask:\nPlease tell me why you are Eagle_Eyes in the log.",
                "<system-reminder>n</system-reminder>\nreview: he said you are Eagle_Eyes",
                "<system-reminder>n</system-reminder>\n" + ("filler line " * 6 + "\n") * 8 + "You are Eagle_Eyes.")):
            self.assertNotIn("BOOT (once)", self.hook(p, sid=f"s{i}"), p)


class TestCiRunsOnRoleFiles(unittest.TestCase):
    def test_a_role_file_change_triggers_ci(self):
        """Failure review 2026-10-23 cause 8: the CI path filter skipped MyTradingSys/system/**, so a role-file edit shipped untested."""
        import fnmatch
        lines = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8").split("on:", 1)[1].split("pull_request:", 1)[0]
        pats = [ln.split("- ", 1)[1].split("#")[0].strip().strip("'\"") for ln in lines.splitlines() if ln.strip().startswith("- ")]
        for f in ("MyTradingSys/system/roles/builder.md", "MyTradingSys/system/roles/ROSTER.json"):
            self.assertTrue(any(fnmatch.fnmatch(f, p) for p in pats), (f, pats))


class TestRoleLineReview(Base):
    """Review of 9f0cb459c (2026-10-23_fix34_replay_and_review.md): the 300-char scan on the cleaned text reached later sentences."""
    NOTICE = "<system-reminder>\n" + "notice text " * 30 + "\n</system-reminder>\n"

    def test_only_the_named_role_loads_when_a_later_sentence_names_another(self):
        roles = {"Supervisor": ["supervisor"], "Session_Planner": ["session_planner", "session planner"], "Thinker": ["thinker"]}
        p = self.NOTICE + "You are Supervisor. Login C. Two hours. Start a session planner for the cards."
        self.assertEqual(rl.match_roles(p, roles), ["Supervisor"])
        quote = self.NOTICE + 'Operator request (verbatim intent, 2026-10-20): "What about a thinker? I need a thinker for this."'
        self.assertEqual(rl.match_roles(quote, roles), [])

    def test_real_wrapped_briefs_with_text_after_the_name_load(self):
        """Replay 2026-10-23 (transcripts 35162ba1, 1672df64): the role name is followed by words or a digit-led name."""
        roles = {"Lab_Guy": ["lab_guy"], "1985Artifacts_Guy": ["1985artifacts_guy"]}
        wrap = "Background (from the session that started this one): " + "context " * 60 + "\n\nTask:\n"
        self.assertEqual(rl.match_roles(wrap + "You are Lab_Guy for ONE batched review pass.", roles), ["Lab_Guy"])
        self.assertEqual(rl.match_roles(wrap + "You are 1985Artifacts_Guy (roles/ file via role loader).", roles),
                         ["1985Artifacts_Guy"])

    def test_other_role_phrases_behind_long_wrappers_still_load(self):
        """Diff review of this fix, finding 1: "I need a pipeliner" behind a 300+ char wrapper; finding 2: a non-str prompt."""
        roles = {"Pipeliner": ["pipeliner"], "Thinker": ["thinker"]}
        for p in (self.NOTICE + "I need a pipeliner", "Background (from x): " + "context " * 60 + "\n\nTask:\nI need a pipeliner for this"):
            self.assertEqual(rl.match_roles(p, roles), ["Pipeliner"], p[-40:])
        self.assertEqual(rl.match_roles(5, roles), [])


if __name__ == "__main__":
    unittest.main()
