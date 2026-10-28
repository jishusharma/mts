"""relay.py tick (2026-10-15): the scheduled dispatcher's whole idle path is ONE T0 call that prints ONE line.

Before, an idle tick was 4-6 model calls (fetch, mkdir, 2x git show, route, kick, `date +%M`, the QUEUE line, the refiner and the
Control Room probe), each re-reading a ~78k-token first turn. Every test here uses the `tick` subcommand, which did not exist before."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "relay.py"
NL = chr(10)

GO = "<!-- relay: go depth=3 id=aaaa1111 -->" + NL
STOP = "<!-- relay: stop reason=queue empty depth=3 id=bbbb2222 -->" + NL
BLOCK = """```
MTS builder session.
   Q1. lane=DSA host=any Run the offline gate and report the failures. DONE when: the desk row is closed with the pass count
   Q3. host=JIS-NB Build the thing. DONE when: tests pass
   Q4. DONE earlier task, nothing left
```
"""
REFINER_STUB = """import sys
print(open("status.txt").read().strip())
"""


def run(home, *args, now="2026-10-15T10:00:00Z", host="JIS-NB", cwd=None, extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update({"MTS_RELAY_HOME": str(home), "MTS_RELAY_NOW": now, "MTS_RELAY_NOLINT": "1", "MTS_RELAY_HOST": host,
                "MTS_RELAY_ACCOUNT": "acct", "MTS_RELAY_NOCODEX": "1", **(extra or {})})
    for who in ("AUTHOR", "COMMITTER"):   # CI runners have no git identity; the desk commit inside tick needs one
        env.setdefault(f"GIT_{who}_NAME", "t")
        env.setdefault(f"GIT_{who}_EMAIL", "t@t")
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, cwd=str(cwd) if cwd else None)


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=str(cwd), check=True, capture_output=True)


class TickBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.repo = self.tmp / "repo"
        self.f = self.repo / "MyTradingSys" / "system" / "NEXT_SESSION.md"
        self.f.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.write(STOP + BLOCK)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")

    def write(self, text):
        self.f.write_text(text, encoding="utf-8", newline=NL)

    def tick(self, *args, **kw):
        return run(self.home, "tick", "--file", str(self.f), "--root", str(self.repo), "--no-ship", *args, cwd=self.repo, **kw)

    def lines(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout.strip().splitlines()

    def refiner(self, status):
        """A refiner tree: a clone of an origin with fast-track and a stub tasks.py that prints the status held in status.txt."""
        origin, clone = self.tmp / "origin.git", self.tmp / "mts-refiner"
        if not origin.exists():
            git(self.tmp, "init", "-q", "--bare", str(origin))
            git(self.tmp, "clone", "-q", str(origin), str(clone))
            git(clone, "checkout", "-q", "-b", "fast-track")
            (clone / "scripts" / "dev").mkdir(parents=True)
            (clone / "scripts" / "dev" / "tasks.py").write_text(REFINER_STUB, encoding="utf-8", newline=NL)
            (clone / ".gitignore").write_text("status.txt" + NL, encoding="utf-8", newline=NL)
            git(clone, "add", "-A")
            git(clone, "commit", "-q", "-m", "stub")
            git(clone, "push", "-q", "origin", "fast-track")
        (clone / "status.txt").write_text(status, encoding="utf-8", newline=NL)
        return clone


class TickLineTest(TickBase):
    def test_idle_tick_is_one_noop_line(self):
        self.home.mkdir()
        (self.home / "mts-hourly.json").write_text(json.dumps({"last_utc": "2026-10-15T09:50:00Z", "last_housekeep_utc": "2026-10-15T09:50:00Z"}))
        out = self.lines(self.tick("--refiner-tree", str(self.tmp / "none")))
        self.assertEqual(len(out), 1, out)   # the whole idle path: one call, one line, nothing for the model to decide
        self.assertTrue(out[0].startswith("TICK NOOP | handoff says stop: queue empty | route="), out[0])
        self.assertNotIn("KICK", out[0])

    def test_kick_prints_next_unlock_and_the_session_text(self):
        self.write(GO + BLOCK)
        sess = self.tmp / "relay_session.md"
        sess.write_text("# Relay session\nSTEP ONE: run NEXT.\n", encoding="utf-8", newline=NL)
        out = self.lines(self.tick("--session-file", str(sess)))
        self.assertTrue(out[0].startswith("TICK KICK depth=3 id=aaaa1111 | route=Q1 DSA posted"), out[0])
        self.assertIn("queue=total=3 runnable=1 (Q3)", out[0])
        self.assertTrue(out[1].startswith('NEXT: python "') and out[1].endswith('begin --root "%s"' % self.repo.resolve().as_posix()), out[1])
        self.assertIn("relay.py", out[1])
        self.assertTrue(out[2].startswith('UNLOCK: python "') and out[2].endswith('relay.py" unlock'), out[2])
        self.assertIn("--- relay_session.md", "\n".join(out))
        self.assertIn("STEP ONE: run NEXT.", out)
        self.assertFalse(any(ln.startswith("HOURLY") for ln in out))   # a KICK session never carries the hourly extras
        lock = json.loads((self.home / "mts-relay-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["id"], "aaaa1111")   # kick's lock side effect is unchanged
        again = self.lines(self.tick("--session-file", str(sess), now="2026-10-15T10:10:00Z"))
        self.assertTrue(again[0].startswith("TICK NOOP | a launch 10 min ago, chain is moving"), again[0])

    def test_tick_routes_before_it_kicks(self):
        self.write(GO + BLOCK)
        head = self.lines(self.tick("--session-file", str(self.f)))[0]
        self.assertIn("route=Q1 DSA posted", head)
        self.assertNotIn("not posted yet", head)   # kick's QUEUE line already sees the posted row
        self.assertEqual(len(list((self.repo / "MyTradingSys" / "system" / "desk_queue").glob("*.json"))), 1)

    def test_a_noisy_failing_ship_does_not_leak_before_the_tick_line(self):
        # route posts through `sync.py ship`, a child with inherited streams: its lines used to land ahead of the answer
        dev = self.repo / "scripts" / "dev"
        dev.mkdir(parents=True)
        (dev / "sync.py").write_text('import sys\nprint("SHIP NOISE one")\nprint("SHIP NOISE two")\nsys.exit(1)\n', encoding="utf-8", newline=NL)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "ship stub")
        self.write(GO + BLOCK)
        sess = self.tmp / "relay_session.md"
        sess.write_text("# Relay session\n", encoding="utf-8", newline=NL)
        r = run(self.home, "tick", "--file", str(self.f), "--root", str(self.repo), "--session-file", str(sess), cwd=self.repo)   # no --no-ship
        out = self.lines(r)
        self.assertTrue(out[0].startswith("TICK KICK depth=3 id=aaaa1111 | route=Q1 DSA ERROR"), out[0])
        self.assertIn("[SHIP NOISE two]", out[0])   # the failure reason travels inside the one line
        self.assertNotIn("SHIP NOISE one", r.stdout + r.stderr)

    def test_peer_idle_skips_every_extra_and_keeps_the_hourly_gate_open(self):
        nb = run(self.tmp / "nb-home", "handoff", "--file", str(self.f), "--go", host="JIS-NB", now="2026-10-15T09:50:00Z")
        self.assertEqual(nb.returncode, 0, nb.stdout + nb.stderr)
        out = self.lines(self.tick("--peer-quiet-min", "90", "--refiner-tree", str(self.refiner("REFINE_NEEDED")), host="JIS-NUC"))
        self.assertEqual(len(out), 1, out)
        self.assertTrue(out[0].startswith("TICK NOOP | peer JIS-NB wrote handoff"), out[0])
        self.assertNotIn("refine=", out[0])
        self.assertFalse((self.home / "mts-hourly.json").exists())   # not consumed: the hourly bundle waits for the peer to go quiet

    def test_fetch_failure_is_flagged_and_the_tick_still_answers(self):
        nowhere = Path(tempfile.mkdtemp())   # not a git repo: fetch, show and route all fail
        r = run(self.home, "tick", "--root", str(nowhere), "--no-ship", "--refiner-tree", str(nowhere / "none"), cwd=nowhere)
        out = self.lines(r)
        self.assertTrue(out[0].startswith("TICK NOOP | no relay header in handoff | route=ERROR cannot read the handoff | fetch=STALE"), out[0])


class HourlyGateTest(TickBase):
    def test_hourly_bundle_runs_once_per_55_minutes_not_per_minute_of_hour(self):
        tree = str(self.refiner("REFINE_OK refinable=0"))
        first = self.lines(self.tick("--refiner-tree", tree, now="2026-10-15T10:08:30Z"))
        self.assertIn("refine=OK", first[0])
        self.assertEqual(first[1:], ["HOURLY housekeep=yes"])   # first run of the day: housekeeping is due, refiner is fine
        # 10 minutes later the old `date +%M < 20` rule fired again (08 and 18 both pass); the state file does not
        second = self.lines(self.tick("--refiner-tree", tree, now="2026-10-15T10:18:30Z"))
        self.assertEqual(len(second), 1)
        self.assertNotIn("refine=", second[0])
        self.assertEqual(len(self.lines(self.tick("--refiner-tree", tree, now="2026-10-15T11:02:00Z"))), 1)   # 53 min
        due = self.lines(self.tick("--refiner-tree", tree, now="2026-10-15T11:04:00Z"))   # 55 min after 10:08:30
        self.assertIn("refine=OK", due[0])
        self.assertEqual(len(due), 1, due)   # housekeeping is once per 24 h
        state = json.loads((self.home / "mts-hourly.json").read_text(encoding="utf-8"))
        self.assertEqual(state["last_utc"], "2026-10-15T11:04:00Z")
        self.assertEqual(state["last_housekeep_utc"], "2026-10-15T10:08:30Z")

    def test_refine_needed_and_the_daily_housekeeping_name_the_model_work(self):
        tree = self.refiner("REFINE_NEEDED refinable=2 parked=0 ready=0")
        out = self.lines(self.tick("--refiner-tree", str(tree), now="2026-10-15T10:00:00Z"))
        self.assertEqual(out[1:], ["HOURLY refine=REFINE_NEEDED housekeep=yes"], out)
        nxt = self.lines(self.tick("--refiner-tree", str(tree), now="2026-10-15T11:00:00Z"))
        self.assertEqual(nxt[1:], ["HOURLY refine=REFINE_NEEDED"], nxt)
        day = self.lines(self.tick("--refiner-tree", str(tree), now="2026-10-16T10:01:00Z"))
        self.assertEqual(day[1:], ["HOURLY refine=REFINE_NEEDED housekeep=yes"], day)

    def test_gate_clock_is_separate_and_leaves_housekeeping_to_the_app_routine(self):
        tree = str(self.refiner("REFINE_NEEDED refinable=1"))
        g = self.lines(self.tick("--gate", "--refiner-tree", tree, now="2026-10-15T10:00:00Z"))
        self.assertEqual(g[1:], ["HOURLY refine=REFINE_NEEDED"], g)   # no housekeep=yes from the gate
        self.assertEqual(len(self.lines(self.tick("--gate", "--refiner-tree", tree, now="2026-10-15T10:10:00Z"))), 1)   # own 60 min clock
        app = self.lines(self.tick("--refiner-tree", tree, now="2026-10-15T10:20:00Z"))
        self.assertEqual(app[1:], ["HOURLY refine=REFINE_NEEDED housekeep=yes"], app)   # the gate did not eat the App slot

    def test_refiner_error_is_reported_never_forced(self):
        out = self.lines(self.tick("--refiner-tree", str(self.tmp / "no-such-tree")))
        self.assertTrue(out[1].startswith("HOURLY refine=ERROR worktree add:"), out)

    def test_stop_flag_skips_the_refiner(self):
        run(self.home, "stop", "weekly budget")
        out = self.lines(self.tick("--refiner-tree", str(self.refiner("REFINE_NEEDED"))))
        self.assertIn("refine=SKIPPED", out[0])
        self.assertFalse(any("REFINE_NEEDED" in ln for ln in out))

    def test_no_control_room_probe_on_this_host(self):
        # the Control Room inbox page is not readable from this login (routines:R3): the line must not ask the model to poll it
        out = "\n".join(self.lines(self.tick("--refiner-tree", str(self.refiner("REFINE_OK")))))
        self.assertNotIn("inbox", out.lower())


class DriftTest(TickBase):
    def setUp(self):
        super().setUp()
        self.inst = self.home / "scheduled-tasks" / "mts-dispatcher" / "SKILL.md"
        self.repo_copy = self.tmp / "mts-dispatcher.SKILL.md"
        self.args = ("--prompt-file", str(self.repo_copy), "--hourly-min", "100000", "--refiner-tree", str(self.tmp / "none"))
        (self.home).mkdir()
        (self.home / "mts-hourly.json").write_text(json.dumps({"last_utc": "2026-10-15T10:00:00Z", "last_housekeep_utc": "2026-10-15T10:00:00Z"}))

    def head(self):
        return self.lines(self.tick(*self.args))[0]

    def test_a_different_installed_prompt_is_flagged(self):
        self.repo_copy.write_text("new stub: relay.py tick --peer-quiet-min 90" + NL, encoding="utf-8", newline=NL)
        self.inst.parent.mkdir(parents=True)
        self.inst.write_text("old 6 KB prompt with five Bash calls", encoding="utf-8", newline=NL)
        head = self.head()
        self.assertIn("drift=SKILL installed=", head)
        self.assertIn("origin=", head)

    def test_same_text_is_not_flagged_whatever_the_line_ends_trailing_newline_or_peer_minutes(self):
        self.repo_copy.write_text("stub: relay.py tick --peer-quiet-min 90" + NL + "second line" + NL, encoding="utf-8", newline=NL)
        self.inst.parent.mkdir(parents=True)
        self.inst.write_bytes(b"stub: relay.py tick --peer-quiet-min 0\r\nsecond line")   # the NUC: CRLF, no trailing newline, other minutes
        self.assertNotIn("drift=", self.head())

    def test_no_installed_prompt_is_not_a_drift(self):
        self.repo_copy.write_text("stub", encoding="utf-8", newline=NL)
        self.assertNotIn("drift=", self.head())


if __name__ == "__main__":
    unittest.main()
