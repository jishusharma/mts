"""Ship speed (branch ship-speed): ship stage timings + `ship-times`, `wait-ci` (gh mocked), the mark-green ancestor guard script."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync

HERE = Path(__file__).resolve().parent


def sh(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def commit(repo, name, text):
    (Path(repo) / name).write_text(text, newline="\n")
    sh(repo, "add", name)
    sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"add {name}")
    return sh(repo, "rev-parse", "HEAD").stdout.strip()


class FakeClock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


class StageTimings(unittest.TestCase):
    def test_clock_sums_stages_and_prints_one_line(self):
        c = FakeClock()
        clock = sync.StageClock(now=c)

        def slow(n):
            c.t += n
            return "x"
        self.assertEqual(clock.run("merge", slow, 2.0), "x")
        clock.run("gate", slow, 30.0)
        clock.run("merge", slow, 1.0)          # a push retry: summed
        self.assertEqual(clock.stages, {"merge": 3.0, "gate": 30.0})
        self.assertEqual(clock.line(), "ship timing: total 33.0s (merge 3.0, gate 30.0)")

    def test_stage_is_timed_even_when_the_stage_raises(self):
        c = FakeClock()
        clock = sync.StageClock(now=c)

        def boom():
            c.t += 5
            raise RuntimeError("x")
        with self.assertRaises(RuntimeError):
            clock.run("push", boom)
        self.assertEqual(clock.stages["push"], 5)

    def test_gate_step_rows_reads_only_rows_after_the_offset(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        f = d / "gate_timing.jsonl"
        f.write_text(json.dumps({"step": "3k", "secs": 9}) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"MTS_GATE_TIMING": str(f)}):
            off = sync.gate_timing_offset(d)
            with open(f, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps({"step": "4t", "secs": 2.5}) + "\n" + json.dumps({"step": "ship", "secs": 99}) + "\n" + "garbage\n")
            self.assertEqual(sync.gate_step_rows(d, off), {"4t": 2.5})

    def test_ship_prints_timing_line_and_logs_a_row(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        origin, work = tmp / "origin.git", tmp / "work"
        sh(tmp, "init", "-q", "--bare", "-b", "fast-track", str(origin))
        sh(tmp, "clone", "-q", str(origin), str(work))
        sh(work, "checkout", "-q", "-B", "fast-track")
        commit(work, "seed.txt", "seed\n")
        sh(work, "push", "-q", "origin", "fast-track")
        sh(work, "checkout", "-q", "-b", "feat")
        commit(work, "scripts_note.md", "docs only\n")
        log = tmp / "stages.jsonl"
        out = io.StringIO()
        env = {"MTS_SHIP_STAGES": str(log), "MTS_GATE_TIMING": str(tmp / "gt.jsonl"), "SYNC_ALLOW_SECOND_SHIP": "1"}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            sync.ship(work, gate=lambda repo, files=None: None)
        text = out.getvalue()
        line = [ln for ln in text.splitlines() if ln.startswith("ship timing: total ")]
        self.assertEqual(len(line), 1, text)
        self.assertRegex(line[0], r"^ship timing: total \d+\.\ds \(merge \d+\.\d.*push \d+\.\d")
        row = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])
        self.assertTrue(row["ok"])
        self.assertTrue({"merge", "select", "push"} <= set(row["stages"]), row)
        self.assertGreaterEqual(row["total"], row["stages"]["push"])


class ShipTimes(unittest.TestCase):
    def test_median_and_p90_per_stage_and_last_n(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        log = d / "s.jsonl"
        rows = [{"total": 10 * i, "stages": {"gate": 8 * i, "push": 1}, "steps": {"4t": float(i)}} for i in range(1, 11)]
        log.write_text("".join(json.dumps(r) + "\n" for r in rows) + "bad line\n", encoding="utf-8")
        lines = []
        n = sync.ship_times(d, path=log, out=lines.append)
        self.assertEqual(n, 10)
        gate = [ln for ln in lines if ln.startswith("gate")][0].split()
        self.assertEqual(gate[1:], ["10", "44.0", "72.8"])        # 8..80: median 44, p90 = 72 + 0.1*8 (linear interpolation)
        self.assertTrue(any(ln.startswith("step 4t") for ln in lines))
        lines.clear()
        self.assertEqual(sync.ship_times(d, last=3, path=log, out=lines.append), 3)
        self.assertEqual([ln for ln in lines if ln.startswith("total")][0].split()[1:], ["3", "90.0", "98.0"])

    def test_empty_log_says_so(self):
        lines = []
        self.assertEqual(sync.ship_times(Path("."), path=Path(tempfile.gettempdir()) / "no_such_ship_stages.jsonl", out=lines.append), 0)
        self.assertIn("no ships logged", lines[0])

    def test_main_routes_ship_times(self):
        with mock.patch.object(sync, "ship_times") as st, mock.patch.object(sync, "toplevel", return_value=Path(".")):
            self.assertEqual(sync.main(["ship-times", "--last", "5"]), 0)
        st.assert_called_once_with(Path("."), 5)


def run_row(sha, status, conclusion=None):
    return {"headSha": sha, "status": status, "conclusion": conclusion, "url": "https://x/1"}


class WaitCi(unittest.TestCase):
    def go(self, replies, max_s=1800, poll=30):
        c = FakeClock()
        calls = []

        def runner(argv):
            calls.append(argv)
            r = replies[min(len(calls) - 1, len(replies) - 1)]
            if isinstance(r, Exception):
                raise r
            return json.dumps(r)

        def sleep(s):
            c.t += s
        out = []
        rc = sync.wait_ci(Path("."), "abc1234", poll=poll, max_s=max_s, sleep=sleep, now_fn=c, runner=runner, out=out.append)
        return rc, calls, out

    def test_green_after_running(self):
        rc, calls, out = self.go([[run_row("abc1234" + "0" * 33, "in_progress")], [run_row("abc1234" + "0" * 33, "completed", "success")]])
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][:3], ["gh", "run", "list"])
        self.assertIn("fast-track", calls[0])

    def test_red(self):
        rc, _, out = self.go([[run_row("abc1234" + "0" * 33, "completed", "failure")]])
        self.assertEqual(rc, 1)
        self.assertIn("RED", out[-1])

    def test_timeout_when_never_finishes_and_polls_at_a_sane_interval(self):
        rc, calls, _ = self.go([[run_row("abc1234" + "0" * 33, "queued")]], max_s=300, poll=30)
        self.assertEqual(rc, 2)
        self.assertLessEqual(len(calls), 11)      # 300 s / 30 s, not a busy loop

    def test_other_shas_are_ignored_and_gh_errors_are_retried(self):
        rc, calls, out = self.go([OSError("rate limited"), [run_row("f" * 40, "completed", "failure")], [run_row("abc1234" + "0" * 33, "completed", "success")]])
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 3)

    def test_main_routes_and_returns_exit_code(self):
        with mock.patch.object(sync, "wait_ci", return_value=2) as w, mock.patch.object(sync, "toplevel", return_value=Path(".")):
            self.assertEqual(sync.main(["wait-ci", "abc"]), 2)
        self.assertEqual(w.call_args[0][1], "abc")

    def test_defaults_are_sane(self):
        self.assertGreaterEqual(sync.WAIT_CI_POLL_S, 10)
        self.assertEqual(sync.WAIT_CI_MAX_S, 1800)


class SelectionPrefilter(unittest.TestCase):
    """Item 4: gate_select.references skips the regex scan when the stem is not in the text at all (profiled hot spot)."""

    def test_absent_stem_never_reaches_the_regex_and_present_stem_still_matches(self):
        import gate_select
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        t = d / "test_x.py"
        t.write_text("import os\nimport widget_tool\n", encoding="utf-8")
        gate_select._text.cache_clear()
        with mock.patch.object(gate_select, "_reference_re", side_effect=AssertionError("regex used")):
            self.assertFalse(gate_select.references("zzz_absent", t))
        self.assertTrue(gate_select.references("widget_tool", t))
        self.assertFalse(gate_select.references("widget", t))      # a longer name is not a reference (regex still decides)


def have_bash():
    try:
        return subprocess.run(["bash", "-c", "true"], capture_output=True).returncode == 0
    except OSError:
        return False


@unittest.skipUnless(have_bash(), "bash not available")
class MarkGreenGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(self.origin))
        self.work = self.tmp / "work"
        sh(self.tmp, "clone", "-q", str(self.origin), str(self.work))
        self.a = commit(self.work, "a.txt", "a\n")
        self.b = commit(self.work, "b.txt", "b\n")
        sh(self.work, "checkout", "-q", "-b", "side", self.a)
        self.side = commit(self.work, "s.txt", "s\n")
        sh(self.work, "push", "-q", "origin", "--all")

    def mark(self, sha):
        script = (HERE / "mark_green.sh").as_posix()
        return subprocess.run(["bash", script, sha, "origin"], cwd=self.work, capture_output=True, text=True)

    def green(self):
        r = subprocess.run(["git", "--git-dir", str(self.origin), "rev-parse", "--verify", "-q", "refs/heads/green/fast-track"], capture_output=True, text=True)
        return r.stdout.strip()

    def test_first_publish_then_forward_then_older_is_skipped(self):
        self.assertEqual(self.mark(self.a).returncode, 0)
        self.assertEqual(self.green(), self.a)           # no pointer yet: publishes
        self.assertEqual(self.mark(self.b).returncode, 0)
        self.assertEqual(self.green(), self.b)           # descendant: moves forward
        r = self.mark(self.a)                             # older run finishing late
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skipped", r.stdout)
        self.assertEqual(self.green(), self.b)           # pointer did not move backwards

    def test_diverged_sha_is_skipped(self):
        self.mark(self.b)
        r = self.mark(self.side)
        self.assertIn("skipped", r.stdout)
        self.assertEqual(self.green(), self.b)


if __name__ == "__main__":
    unittest.main()
