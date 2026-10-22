"""Role roster (bug-models-cannot-tell-which-roles-exist): one roster file is the single source of what roles exist;
`role_loader.py list` prints it; a session with no role line gets the best-fitting role from its task text."""
import json
import re
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

ROLES_DIR = REPO / "MyTradingSys" / "system" / "roles"
ROSTER = ROLES_DIR / "ROSTER.json"
FIELDS = ("name", "file", "start", "model", "lane", "job", "keywords")


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, cwd=str(REPO), timeout=60)


class RosterMatchesFiles(unittest.TestCase):
    def test_roster_file_exists_with_every_field(self):
        self.assertTrue(ROSTER.exists(), "MyTradingSys/system/roles/ROSTER.json missing")
        roles = json.loads(ROSTER.read_text(encoding="utf-8"))["roles"]
        for r in roles:
            for f in FIELDS:
                self.assertIn(f, r, f"{r.get('name')}: field {f} missing")
            self.assertIn(r["start"], ("operator", "embedded"), r["name"])

    def test_roster_names_equal_role_file_headers(self):
        heads = {}
        for f in sorted(ROLES_DIR.glob("*.md")):
            h = rl.parse_header(f.read_text(encoding="utf-8"))
            self.assertIsNotNone(h, f.name)
            heads[h["name"]] = f.name
        roster = {r["name"]: r["file"] for r in rl.load_roster(REPO)}
        self.assertEqual(roster, heads)

    def test_loader_constants_come_from_the_roster(self):
        names = [r["name"] for r in rl.load_roster(REPO)]
        self.assertEqual(sorted(rl.KNOWN_ROLES), sorted(names))
        self.assertEqual(sorted(rl.NO_ROSTER_NAMES), sorted(names), "no-roster fallback list drifted from the roster")
        self.assertIn("q&a_helper", rl.ALIASES["Admin_Guy"])
        self.assertIn("network_admin_guy", rl.ALIASES["Admin_Guy"])
        self.assertIn("traffic_controller", rl.ALIASES["Pipeliner"])

    def test_list_command_prints_every_role_with_file_and_start(self):
        r = run("list")
        self.assertEqual(r.returncode, 0, r.stderr.decode(errors="replace"))
        out = r.stdout.decode("utf-8")
        for role in rl.load_roster(REPO):
            line = next((ln for ln in out.splitlines() if ln.split() and ln.split()[0] == role["name"]), None)
            self.assertIsNotNone(line, f"{role['name']} not in list output")
            self.assertIn(role["file"], line)
            self.assertIn(role["start"], line)
        self.assertIn(f"{len(rl.load_roster(REPO))} roles", out)

    def test_docs_have_no_hand_typed_role_count_and_render_is_current(self):
        start_here = (REPO / "MyTradingSys/system/START_HERE.txt").read_text(encoding="utf-8")
        roles_md = (REPO / "MyTradingSys/system/ROLES.md").read_text(encoding="utf-8")
        self.assertNotRegex(start_here, r"THE ROLES \(\d+\)")
        for text in (start_here, roles_md):
            self.assertIn("roster:begin", text)
        self.assertEqual(rl.render(REPO, write=False), [], "run: python scripts/dev/role_loader.py render")
        for role in rl.load_roster(REPO):
            self.assertIn(role["name"], start_here)

    def test_check_and_lint_exit_zero(self):
        for cmd in ("check", "lint"):
            r = run(cmd)
            self.assertEqual(r.returncode, 0, f"{cmd}: {r.stdout.decode(errors='replace')}")


class ReadFirstRule(unittest.TestCase):
    """bug-haiku-stale-rule-answers: rule, role, super-session and budget answers come from a file read this turn."""

    def test_every_role_file_has_a_read_first_line_naming_real_files(self):
        for f in sorted(ROLES_DIR.glob("*.md")):
            head = f.read_text(encoding="utf-8").splitlines()[:8]
            line = next((ln for ln in head if ln.startswith("Read first:")), None)
            self.assertIsNotNone(line, f"{f.name}: no 'Read first:' line in the first 8 lines")
            paths = re.findall(r"`([\w./-]+\.(?:md|py|json|txt))`", line)
            self.assertTrue(paths, f"{f.name}: Read first line names no file")
            for p in paths:
                self.assertTrue((REPO / p).exists(), f"{f.name}: {p} does not exist")

    def test_lint_fails_when_a_role_file_has_no_read_first_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "MyTradingSys" / "system" / "roles"
            d.mkdir(parents=True)
            (d / "x.md").write_text("<!-- role: X | version: v1 | token: PENDING | triggers: x -->\n# X\n\nJob: x.\n",
                                    encoding="utf-8", newline="\n")
            lines = []
            self.assertEqual(rl.lint(tmp, out=lines.append, ci_runs=[]), 1)
            self.assertTrue(any("READ-FIRST" in ln for ln in lines), lines)

    def test_boot_text_carries_the_rules_answer_rule(self):
        text = (ROLES_DIR / "admin_guy.md").read_text(encoding="utf-8")
        with mock.patch.object(rl, "git_sha8", lambda repo: "abcd1234"), \
                mock.patch.object(rl, "git_show", lambda repo, rel: text if rel.endswith("admin_guy.md") else None), \
                mock.patch.object(rl, "lease_suffix", lambda name, repo: ""):
            boot = rl.build_text("Admin_Guy", REPO, True)
        for must in ("read the source file this turn", "file:line", "commit date", "age", "NOT_IN_DATA"):
            self.assertIn(must, boot)


class BestRoleFallback(unittest.TestCase):
    def pick(self, text):
        return rl.pick_role(text, REPO)

    def test_chart_screenshot_picks_eagle_eyes(self):
        p = self.pick("Here is a chart screenshot of BTC 15m, what do you see?")
        self.assertEqual(p["name"], "Eagle_Eyes")
        self.assertIn("screenshot", p["reason"])

    def test_plain_question_picks_admin_guy(self):
        self.assertEqual(self.pick("I have a question about the Deribit testnet fee setting")["name"], "Admin_Guy")
        self.assertEqual(self.pick("Where is the decision about the weekly low layer recorded?")["name"], "Admin_Guy")

    def test_bare_question_words_pick_no_role(self):
        # review 2026-10-22 (R1): "what/why/how/where/?" alone made every chat session Admin_Guy
        for text in ("why are super sessions still asking me to click a card? what is going on?",
                     "What is the current fee setting for the Deribit testnet account?",
                     "where is the report?"):
            self.assertIsNone(self.pick(text)["name"], text)

    def test_design_question_picks_thinker(self):
        self.assertEqual(self.pick("How should we design the layer combiner so it scales to 20 layers?")["name"], "Thinker")
        self.assertEqual(self.pick("What are our options to optimise token spend?")["name"], "Thinker")

    def test_builder_and_session_planner_never_picked(self):
        for text in ("Build card t02-f1, implement it with fail-first tests and ship",
                     "builder: implement the build card", "Refine raw cards and plan the session backlog",
                     "You are a builder. implement code, write tests, ship it"):
            p = self.pick(text)
            self.assertNotIn(p["name"], ("Builder", "Session_Planner"), text)
            for t in p.get("tie", []):
                self.assertNotIn(t, ("Builder", "Session_Planner"), text)

    def test_file_paths_never_score(self):
        # pilot 2026-10-22: a Builder brief held C:/Users/x/IdeaProjects/... and "idea*" picked Thinker
        for text in ("Boot: python C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/scripts/dev/sync.py start",
                     r"Work in C:\Users\E-ngineers\IdeaProjects\mts and run scripts/dev/sync.py"):
            self.assertIsNone(self.pick(text)["name"], text)
        self.assertEqual(self.pick("I have an idea about the layer combiner")["name"], "Thinker")

    def test_no_signal_picks_nothing(self):
        p = self.pick("Fix the typo in line 4 of foo.py")
        self.assertIsNone(p["name"])
        self.assertEqual(p.get("tie", []), [])

    def test_tie_names_both_and_picks_none(self):
        p = self.pick("chart screenshot design options")  # 2 Eagle_Eyes words vs 2 Thinker words
        self.assertIsNone(p["name"])
        self.assertEqual(sorted(p["tie"]), ["Eagle_Eyes", "Thinker"])


class FallbackHook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        text = (ROLES_DIR / "eagle_eyes.md").read_text(encoding="utf-8")
        for p in (mock.patch.dict("os.environ", {"MTS_ROLES_HOME": self.tmp.name}),
                  mock.patch.object(rl, "git_fetch", lambda repo: True),
                  mock.patch.object(rl, "git_sha8", lambda repo: "abcd1234"),
                  mock.patch.object(rl, "git_show", lambda repo, rel: text if rel.endswith("eagle_eyes.md") else None)):
            p.start()
            self.addCleanup(p.stop)

    def ctx(self, prompt, sid="s1"):
        out = rl.handle({"hook_event_name": "UserPromptSubmit", "session_id": sid, "prompt": prompt}, REPO)
        return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""

    def test_first_prompt_without_role_line_loads_best_role_with_fallback_banner(self):
        c = self.ctx("Here is a chart screenshot of ETH 1h, read it please")
        self.assertRegex(c, r"ROLE LOADED: Eagle_Eyes \(fallback: [^)]+\) v\d+ ")
        self.assertIn("Eagle_Eyes", rl.injected("s1"))
        banner = next(ln for ln in c.splitlines() if ln.startswith("ROLE LOADED"))
        m = rl.BANNER_RE.search(banner)
        self.assertIsNotNone(m, "fallback banner must still parse for verify")
        self.assertEqual(m.group("name"), "Eagle_Eyes")

    def test_only_first_prompt_and_never_for_cross_session_briefs(self):
        self.assertEqual(self.ctx("Fix the typo in foo.py", sid="s2"), "")
        self.assertNotIn("ROLE LOADED", self.ctx("Here is a chart screenshot, read it", sid="s2"))
        self.assertEqual(self.ctx('<cross-session-message from="x">chart screenshot read</cross-session-message>', sid="s3"), "")

    def test_supervisor_brief_gets_no_fallback_role(self):
        # pilot 2026-10-22: the Supervisor's Builder brief starts "Background (from the session that started this one)"
        brief = "Background (from the session that started this one):\nTake the conservative option; an idea list is not needed."
        self.assertEqual(self.ctx(brief, sid="s5"), "")
        self.assertNotIn("ROLE LOADED", self.ctx(brief, sid="s5"))

    def test_tie_asks_once(self):
        c = self.ctx("chart screenshot design options", sid="s4")
        self.assertIn("ask the operator", c.lower())
        self.assertNotIn("ROLE LOADED:", c)
        self.assertEqual(self.ctx("chart screenshot design options", sid="s4"), "")


class AskedWorkRunsNow(unittest.TestCase):
    # bug-ask-go-for-asked-work: asked work runs this turn; no "say go" gate
    def test_thinker_no_go_ahead_request(self):
        text = (ROLES_DIR / "thinker.md").read_text(encoding="utf-8")
        self.assertIn("ASKED WORK RUNS NOW", text)
        self.assertIn("never end a reply asking the operator to say go", text)

    def test_boot_text_has_asked_work_rule(self):
        self.assertIn("ASKED WORK RUNS NOW", rl.RULES_ANSWER)


if __name__ == "__main__":
    unittest.main()
