"""Role roster (bug-models-cannot-tell-which-roles-exist): one roster file is the single source of what roles exist;
`role_loader.py list` prints it; a session with no role line gets no role."""
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


class NoRoleLineHook(unittest.TestCase):
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

    def test_prompt_without_role_line_injects_nothing(self):
        # 2026-10-22: a planning session got Lab_Guy because its first message mentioned Gemini/GPT.
        for i, t in enumerate(("Compare Gemini and GPT and codex for the layer lab",
                               "Here is a chart screenshot of ETH 1h, read it please",
                               "chart screenshot design options")):
            self.assertEqual(self.ctx(t, sid=f"n{i}"), "", t)
            self.assertEqual(rl.injected(f"n{i}"), [])

    def test_explicit_role_line_still_loads(self):
        c = self.ctx("You are Eagle_Eyes. Read this chart.", sid="e1")
        self.assertIn("ROLE LOADED: Eagle_Eyes", c)
        self.assertIn("Eagle_Eyes", rl.injected("e1"))


if __name__ == "__main__":
    unittest.main()
