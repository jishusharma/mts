"""relay.py QUEUE line and lane routing (operator 2026-10-14): the relay counts its queue, and a task tagged lane=CODEX / lane=DSA
is posted once to its lane by `relay.py route` instead of burning a Claude relay session. Every test uses a subcommand or tag
that did not exist before, so all fail on the old code."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "relay.py"
SCHED = REPO / "scripts" / "sched"

HEADER = "<!-- relay: go depth=3 id=aaaa1111 -->\n"
BLOCK = """```
MTS builder session.
   Q1. lane=DSA host=any Run the offline gate and report the failures. DONE when: the desk row is closed with the pass count
   Q2. lane=CODEX Audit the layer table for stale rows. DONE when: the card is done with a result line
   Q3. host=JIS-NB Build the thing. DONE when: tests pass
   Q4. DONE earlier task, nothing left
   Q5. host=JIS-NUC Do a NUC-only thing. DONE when: x
   Q6. (after the operator answers the Control Room decision) wait
   Q7. host=any (after DSA closes desk row 20261014-134217-x) wait
```
"""
LANE_ONLY = """```
MTS builder session.
   Q1. lane=DSA host=any Run the offline gate and report the failures. DONE when: the desk row is closed with the pass count
   Q2. lane=CODEX Audit the layer table for stale rows. DONE when: the card is done with a result line
```
"""
DESK = "MyTradingSys/system/desk_queue"
CARDS = "MyTradingSys/system/tasks"


def run(home, *args, host="JIS-NB"):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update({"MTS_RELAY_HOME": str(home), "MTS_RELAY_NOW": "2026-10-14T10:00:00Z", "MTS_RELAY_NOLINT": "1",
                "MTS_RELAY_HOST": host, "MTS_RELAY_NOCODEX": "1"})
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=str(cwd), check=True, capture_output=True)


class QueueRouteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        self.f = self.root / "MyTradingSys" / "system" / "NEXT_SESSION.md"
        self.f.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write(BLOCK)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")
        self.home = self.tmp / "home"

    def write(self, block):
        self.f.write_text(HEADER + block, encoding="utf-8", newline="\n")

    def status(self, host="JIS-NB"):
        r = run(self.home, "status", "--file", str(self.f), "--host", host)
        self.assertEqual(r.returncode, 0, r.stderr)
        return next(ln for ln in r.stdout.splitlines() if ln.startswith("QUEUE"))

    def route(self, home=None):
        return run(home or self.home, "route", "--file", str(self.f), "--root", str(self.root), "--no-ship")

    def files(self, d):
        p = self.root / d
        return sorted(p.glob("*.json")) if p.is_dir() else []

    def test_status_queue_line_groups_tasks_by_why_they_wait(self):
        line = self.status()
        for want in ("total=7", "runnable=1 (Q3)", "host=JIS-NUC 1", "operator/JIS 1", "DSA desk row 1", "other blocked 0",
                     "lane CODEX 1", "lane DSA 1", "DONE 1", "look=0", "for JIS-NB"):
            self.assertIn(want, line)
        self.assertIn("2 not posted yet", line)

    def test_queue_line_is_per_host(self):
        line = self.status("JIS-NUC")
        self.assertIn("runnable=1 (Q5)", line)
        self.assertIn("host=JIS-NB 1", line)

    def test_lane_tag_parses_in_either_order_and_bad_value_fails_lint(self):
        sys.path.insert(0, str(SCHED))
        import handoff_lint as hl
        t = hl.parse_tasks(["   Q1. lane=codex host=JIS-NUC x DONE when: y", "   Q2. host=any lane=DSA z DONE when: y"])
        self.assertEqual([(x["host"], x["lane"], x["state"]) for x in t], [("JIS-NUC", "CODEX", "open"), ("any", "DSA", "open")])
        errs, _ = hl.lint("```\n   Q1. lane=GPT2 x DONE when: y\n```\n", REPO)
        self.assertTrue(any("lane=" in e for e in errs), errs)

    def test_route_posts_each_lane_task_exactly_once(self):
        r = self.route()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Q1 DSA posted", r.stdout)
        self.assertIn("Q2 CODEX posted", r.stdout)
        rows, cards = self.files(DESK), self.files(CARDS)
        self.assertEqual((len(rows), len(cards)), (1, 1))
        row, card = json.loads(rows[0].read_text("utf-8")), json.loads(cards[0].read_text("utf-8"))
        self.assertEqual((row["target"], row["status"]), ("DSA", "pending"))
        self.assertIn("Run the offline gate", row["need"])
        self.assertEqual((card["lane"], card["state"]), ("CODEX", "raw"))
        self.assertTrue(row["relay_key"].startswith("q1-") and card["relay_key"].startswith("q2-"))
        again = self.route()
        self.assertIn("nothing to post", again.stdout)
        self.assertEqual((len(self.files(DESK)), len(self.files(CARDS))), (1, 1))
        self.assertNotIn("not posted yet", self.status())

    def test_a_second_host_does_not_post_the_same_task_again(self):
        self.route()
        other = self.route(home=self.tmp / "other-host-home")
        self.assertIn("exists", other.stdout)
        self.assertEqual((len(self.files(DESK)), len(self.files(CARDS))), (1, 1))

    def test_kick_prints_queue_and_skips_a_handoff_that_is_all_lane_work(self):
        r = run(self.home, "kick", "--file", str(self.f))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK depth=3", r.stdout)
        self.assertIn("QUEUE total=7 runnable=1", r.stdout)
        self.write(LANE_ONLY)
        idle = run(self.tmp / "h2", "kick", "--file", str(self.f))
        self.assertEqual(idle.returncode, 1, idle.stdout)
        self.assertIn("IDLE no Claude-runnable task", idle.stdout)
        self.assertIn("QUEUE total=2 runnable=0", idle.stdout)

    def test_a_finished_lane_result_is_a_look_and_wakes_kick(self):
        self.write(LANE_ONLY.replace("   Q2. lane=CODEX Audit the layer table for stale rows. DONE when: the card is done with a result line\n", ""))
        self.route()
        self.assertIn("look=0", self.status())
        row_path = self.files(DESK)[0]
        row = json.loads(row_path.read_text("utf-8"))
        row.update(status="done", result="gate 41/41")
        row_path.write_text(json.dumps(row), encoding="utf-8")
        self.assertIn("look=1 [Q1 desk done]", self.status())
        r = run(self.tmp / "h3", "kick", "--file", str(self.f))
        self.assertEqual(r.returncode, 0, r.stdout)   # a result for Claude to read is Claude work


if __name__ == "__main__":
    unittest.main()
