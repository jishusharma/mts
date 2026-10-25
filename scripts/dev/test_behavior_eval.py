"""Tests for behavior_eval.py: schema, deterministic graders, exit code. No model calls."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import behavior_eval as be  # noqa: E402


def good(**kw):
    s = dict(id="x-one", role=None, state=["a", "b"], operator="do it",
             pass_if=["p1", "p2"], fail_if=["f1"], source="2026-10-25: real")
    s.update(kw)
    return s


class Schema(unittest.TestCase):
    def test_good(self):
        self.assertEqual(be.validate(good(), "x-one"), [])

    def test_missing_and_bounds(self):
        s = good()
        del s["operator"]
        self.assertTrue(be.validate(s, "x-one"))
        self.assertTrue(be.validate(good(state=["only one"]), "x-one"))
        self.assertTrue(be.validate(good(pass_if=["one"]), "x-one"))
        self.assertTrue(be.validate(good(fail_if=[]), "x-one"))
        self.assertTrue(be.validate(good(source="no date"), "x-one"))
        self.assertTrue(be.validate(good(det=["bogus"]), "x-one"))
        self.assertTrue(be.validate(good(), "other-name"))

    def test_shipped_scenarios_valid(self):
        scen, errs = be.load_scenarios()
        self.assertEqual(errs, [])
        self.assertGreaterEqual(len(scen), 8)
        for s in scen:
            if s["role"]:
                self.assertTrue((be.ROLE_DIR / (s["role"] + ".md")).exists(), s["id"])


class Det(unittest.TestCase):
    def test_lines_and_bold(self):
        ok, _ = be.grade_det(["max_lines:3", "bold_first_line"], "**Done.**\nline\nline")
        self.assertTrue(ok)
        ok, f = be.grade_det(["max_lines:3", "bold_first_line"], "Done\n1\n2\n3\n4")
        self.assertFalse(ok)
        self.assertEqual(f, ["max_lines:3", "bold_first_line"])

    def test_question_and_mentions(self):
        self.assertFalse(be.grade_det(["not_ends_with_question"], "ok?\n")[0])
        self.assertTrue(be.grade_det(["not_ends_with_question"], "ok.")[0])
        self.assertTrue(be.grade_det(["mentions:--again"], "run ship --again")[0])
        self.assertFalse(be.grade_det(["mentions:revert"], "forward fix")[0])

    def test_parse_grade(self):
        self.assertEqual(be.parse_grade('x {"pass": true, "why": "ok"} y'), (True, "ok"))
        with self.assertRaises(ValueError):
            be.parse_grade("no json")


class Runs(unittest.TestCase):
    def _dir(self, scen):
        d = tempfile.mkdtemp()
        for s in scen:
            Path(d, s["id"] + ".json").write_text(json.dumps(s), encoding="utf-8")
        return d, Path(d) / "runs.jsonl"

    def test_dry_run_no_model(self):
        d, log = self._dir([good()])
        with mock.patch.object(be, "call_claude") as m:
            self.assertEqual(be.main(["run", "--dry-run"], d, log), 0)
        m.assert_not_called()
        self.assertFalse(log.exists())

    def test_dry_run_invalid_exit1(self):
        d, log = self._dir([good(state=["x"])])
        self.assertEqual(be.main(["run", "--dry-run"], d, log), 1)

    def test_exit_codes_and_metrics_only_log(self):
        d, log = self._dir([good(id="x-one"), good(id="x-two")])
        replies = iter(["SECRET TEXT", '{"pass": true, "why": "fine"}',
                        "SECRET TEXT", '{"pass": false, "why": "bad"}'])
        with mock.patch.object(be, "call_claude", side_effect=lambda *a, **k: next(replies)):
            self.assertEqual(be.main(["run"], d, log), 1)
        rows = [json.loads(x) for x in log.read_text().splitlines()]
        self.assertEqual([r["pass"] for r in rows], [True, False])
        self.assertEqual(set(rows[0]), {"id", "pass", "model", "utc", "claude_md_sha"})
        self.assertNotIn("SECRET", log.read_text())

    def test_all_pass_exit0(self):
        d, log = self._dir([good()])
        replies = iter(["reply", '{"pass": true, "why": "ok"}'])
        with mock.patch.object(be, "call_claude", side_effect=lambda *a, **k: next(replies)):
            self.assertEqual(be.main(["run", "--id", "x-one"], d, log), 0)

    def test_det_failure_overrides_grader(self):
        s = good(det=["max_lines:1"])
        with mock.patch.object(be, "call_claude", return_value="a\nb\nc") as m:
            r = be.run_one(s, "haiku")
        self.assertFalse(r["pass"])
        self.assertEqual(m.call_count, 1)  # grader never consulted

    def test_cli_error_is_failure(self):
        with mock.patch.object(be, "call_claude", side_effect=RuntimeError("boom")):
            self.assertFalse(be.run_one(good(), "haiku")["pass"])

    def test_call_claude_flags(self):
        fake = mock.Mock(returncode=0, stdout=" hi \n", stderr="")
        with mock.patch.object(be.subprocess, "run", return_value=fake) as m:
            self.assertEqual(be.call_claude("p", "haiku", "sys"), "hi")
        cmd = m.call_args[0][0]
        self.assertIn("-p", cmd)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertEqual(cmd[cmd.index("--model") + 1], "haiku")


MEM_LINE = "Spawn sessions, never Agents, for worker roles (2026-10-16)."
ROLE_LINE = "Worker roles are background Agents, never start_session."


class Conflicts(unittest.TestCase):
    """Fixture copy of the known true positive: memory 'spawn sessions' vs supervisor 'Agents'."""

    def _root(self):
        root = Path(tempfile.mkdtemp())
        (root / "MyTradingSys" / "system" / "roles").mkdir(parents=True)
        (root / "CLAUDE.md").write_text("# T\n## Where to look\n| x | none |\n", encoding="utf-8")
        (root / "MyTradingSys" / "system" / "roles" / "supervisor.md").write_text(
            "# Supervisor\n" + ROLE_LINE + "\n", encoding="utf-8")
        mem = root / "mem"
        mem.mkdir()
        (mem / "spawn.md").write_text(MEM_LINE + "\n", encoding="utf-8")
        return root, mem

    def _pair(self, **kw):
        p = {"a": "memory/spawn.md:1", "a_quote": MEM_LINE,
             "b": "MyTradingSys/system/roles/supervisor.md:2", "b_quote": ROLE_LINE,
             "situation": "start a worker", "newer": "b"}
        p.update(kw)
        return p

    def test_guidance_set(self):
        root, mem = self._root()
        labs = set(be.guidance_files(mem, root))
        self.assertEqual(labs, {"CLAUDE.md", "MyTradingSys/system/roles/supervisor.md", "memory/spawn.md"})

    def test_true_positive_found(self):
        root, mem = self._root()
        reply = json.dumps([self._pair()])
        with mock.patch.object(be, "call_claude", return_value=reply):
            pairs = be.find_conflicts("haiku", None, mem, root=root)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["a"], "memory/spawn.md:1")

    def test_invented_quotes_dropped(self):
        root, mem = self._root()
        lines = be.read_lines(be.guidance_files(mem, root))
        bad = [self._pair(b_quote="Never use Agents for anything at all"),
               self._pair(a="nofile.md:1"),
               self._pair(a_quote="x"),  # too short to verify
               self._pair(b="MyTradingSys/system/roles/supervisor.md:2", a="MyTradingSys/system/roles/supervisor.md:2",
                          a_quote=ROLE_LINE)]  # same line twice
        self.assertEqual(be.verify_pairs(bad, lines), [])
        self.assertEqual(len(be.verify_pairs([self._pair(), "junk"], lines)), 1)

    def test_wrong_line_number_relocated(self):
        root, mem = self._root()
        lines = be.read_lines(be.guidance_files(mem, root))
        out = be.verify_pairs([self._pair(b="MyTradingSys/system/roles/supervisor.md:1")], lines)
        self.assertEqual(out[0]["b"], "MyTradingSys/system/roles/supervisor.md:2")

    def test_changed_filter_and_exit_codes(self):
        root, mem = self._root()
        reply = json.dumps([self._pair()])
        supervisor = root / "MyTradingSys" / "system" / "roles" / "supervisor.md"
        with mock.patch.object(be, "call_claude", return_value=reply), \
                mock.patch.object(be, "changed_lines", return_value={2}):
            self.assertEqual(len(be.find_conflicts("haiku", [str(supervisor)], mem, root=root)), 1)
        with mock.patch.object(be, "call_claude", return_value=reply), \
                mock.patch.object(be, "changed_lines", return_value={1}):  # changed line is not in the pair
            self.assertEqual(be.find_conflicts("haiku", [str(supervisor)], mem, root=root), [])

    def test_main_changed_exit1_and_sweep_report_has_no_memory_text(self):
        root, mem = self._root()
        reply = json.dumps([self._pair()])
        log = Path(tempfile.mkdtemp()) / "runs.jsonl"
        rd = Path(tempfile.mkdtemp())
        sup = str(root / "MyTradingSys" / "system" / "roles" / "supervisor.md")
        with mock.patch.multiple(be, MEMORY_DIR=mem, ROOT=root, REPORT_DIR=rd),                 mock.patch.object(be, "call_claude", return_value=reply),                 mock.patch.object(be, "changed_lines", return_value={2}):
            self.assertEqual(be.main(["conflicts", "--changed", sup], log=log), 1)
            self.assertEqual(be.main(["conflicts"], log=log), 0)
        rep = next(rd.glob("RULE_CONFLICTS_*.md")).read_text(encoding="utf-8")
        self.assertNotIn("Spawn sessions", rep)
        self.assertIn("memory/spawn.md:1", rep)
        self.assertIn(ROLE_LINE, rep)
        row = json.loads(log.read_text().splitlines()[-1])
        self.assertEqual((row["id"], row["pairs"]), ("conflicts-sweep", 1))

    def test_model_error_fails_closed(self):
        with mock.patch.object(be, "call_claude", return_value="not json"):
            self.assertEqual(be.main(["conflicts", "--changed", "CLAUDE.md"]), 1)


if __name__ == "__main__":
    unittest.main()
