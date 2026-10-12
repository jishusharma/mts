"""Fixtures for scripts/sched/relay.py: header stamping, every gate STOP condition, GO writes the launch lock."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "relay.py"


def run(home, *args, now="2026-10-10T10:00:00Z", extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
    env.update({"MTS_RELAY_HOME": str(home), "MTS_RELAY_NOW": now, "MTS_RELAY_NOLINT": "1", **(extra or {})})
    if env.get("MTS_RELAY_NOLINT") == "":
        del env["MTS_RELAY_NOLINT"]
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


class RelayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.f = self.tmp / "NEXT_SESSION.md"
        self.f.write_text("# NEXT SESSION\nbody\n", encoding="utf-8", newline="\n")

    def header_id(self):
        return self.f.read_text(encoding="utf-8").split("id=")[1].split(" ")[0]

    def test_brief_skips_done_and_opus(self):
        lines = ["<!-- relay: stop reason=x depth=1 id=abc -->", "# N", "   Q1. DONE 2026-10-12 x",
                 "   Q2. OPUS card y", "   Q3. build card z", "   Q4. second open"]
        self.f.write_text(chr(10).join(lines) + chr(10), encoding="utf-8", newline=chr(10))
        r = run(self.home, "brief", "--file", str(self.f), "--max", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Q3. build card z", r.stdout)
        for bad in ("Q1.", "Q2.", "Q4."):
            self.assertNotIn(bad, r.stdout)

    def test_no_header_stops(self):
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no relay header", r.stdout)

    def test_same_id_double_fire_blocked(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RELAY GO depth=0", r.stdout)
        self.assertIn("task=mts-relay-a", r.stdout)
        r2 = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:05:00Z")
        self.assertEqual(r2.returncode, 1)
        self.assertIn("already launched", r2.stdout)

    def test_new_id_within_minutes_is_allowed(self):
        # 2026-10-10 06:42 chain death: a short session handed over a NEW id 15 min after the previous launch and the
        # old 20-minute clock lock stopped the chain. The lock is keyed by handoff id now.
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(run(self.home, "gate", "--file", str(self.f), "--started-id", "none").returncode, 0)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", now="2026-10-10T10:15:00Z")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("depth=1", r.stdout)
        self.assertIn("task=mts-relay-b", r.stdout)

    def kick(self, now="2026-10-10T10:00:00Z"):
        return run(self.home, "kick", "--file", str(self.f), now=now)

    def test_kick_starts_a_go_handoff_and_records_chain_base(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")  # depth 2
        r = self.kick()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK depth=2", r.stdout)
        self.assertIn("task=mts-relay-a", r.stdout)
        # depth cap now counts from the kick: depth 2 with cap 2 would have stopped before, base 2 lets it through
        run(self.home, "handoff", "--file", str(self.f), "--go")
        g = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", extra={"MTS_RELAY_MAX_DEPTH": "2"})
        self.assertEqual(g.returncode, 0, g.stdout)

    def test_kick_idles_when_chain_moving_or_session_on_it(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(self.kick().returncode, 0)
        moving = self.kick(now="2026-10-10T10:20:00Z")
        self.assertEqual(moving.returncode, 1)
        self.assertIn("chain is moving", moving.stdout)
        working = self.kick(now="2026-10-10T10:50:00Z")
        self.assertEqual(working.returncode, 1)
        self.assertIn("session still on it", working.stdout)
        self.assertIn("lock=2026-10-10T10:00:00Z task=mts-relay-", working.stdout)
        retry = self.kick(now="2026-10-10T11:10:00Z")  # same id, 70 min: never started or died, retry (was 3 h)
        self.assertEqual(retry.returncode, 0, retry.stdout)

    def test_kick_idles_on_stop_header_no_header_and_stop_flag(self):
        self.assertEqual(self.kick().returncode, 1)
        run(self.home, "handoff", "--file", str(self.f), "--stop", "queue empty")
        r = self.kick()
        self.assertEqual(r.returncode, 1)
        self.assertIn("queue empty", r.stdout)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        run(self.home, "stop", "weekly budget")
        self.assertIn("stop flag", self.kick().stdout)

    def test_stop_header_stops_with_reason(self):
        run(self.home, "handoff", "--file", str(self.f), "--stop", "queue empty")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("queue empty", r.stdout)

    def test_unchanged_id_stops(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", self.header_id())
        self.assertEqual(r.returncode, 1)
        self.assertIn("unchanged", r.stdout)

    def test_depth_increments_and_caps(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertIn("depth=2", self.f.read_text(encoding="utf-8"))
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none", extra={"MTS_RELAY_MAX_DEPTH": "2"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("cap", r.stdout)
        run(self.home, "handoff", "--file", str(self.f), "--go", "--reset-depth")
        self.assertIn("depth=0", self.f.read_text(encoding="utf-8"))
        self.assertEqual(self.f.read_text(encoding="utf-8").count("relay:"), 1)

    def test_operator_stop_flag_and_resume(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        run(self.home, "stop", "weekly budget")
        r = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(r.returncode, 1)
        self.assertIn("weekly budget", r.stdout)
        run(self.home, "resume")
        self.assertEqual(run(self.home, "gate", "--file", str(self.f), "--started-id", "none").returncode, 0)


GOOD = """<!-- relay: go depth=0 id=aaaa1111 -->
# NEXT
```
MTS builder session.
3. TASK:
   Q1. DONE shots read.
   Q2. Read set 29ff2b with `scripts/dev/shot.py` and extract.
       DONE when: research/screenshots has the extract and shot.py status shows the set done.
   Q3. (after Q2) engine run. DONE when: json shipped.
```
"""
NL = chr(10)
NOLINT_OFF = {"MTS_RELAY_NOLINT": ""}


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.f = self.tmp / "NEXT_SESSION.md"
        self.home = self.tmp / "home"

    def lint(self, text, *args):
        self.f.write_text(text, encoding="utf-8", newline=NL)
        return run(self.home, "lint", "--file", str(self.f), "--root", str(REPO), *args, extra=NOLINT_OFF)

    def test_good_list_passes(self):
        r = self.lint(GOOD)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_missing_done_when_vague_and_missing_path_fail(self):
        bad = GOOD.replace("DONE when: research/screenshots has the extract", "take the next open item in research/nonexistent_dir/PLAN.md. Ends with research")
        r = self.lint(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no `DONE when:`", r.stdout)
        self.assertIn("vague", r.stdout)
        self.assertIn("does not exist", r.stdout)

    def test_block_too_long_and_restated_rule_fail(self):
        r = self.lint(GOOD.replace("MTS builder session.", "Worktree only." + NL + ("x" + NL) * 31))
        self.assertIn("limit 30", r.stdout)
        self.assertIn("restates a hard rule", r.stdout)

    def test_task_over_six_lines_fails(self):
        pad = "".join("       " + c + NL for c in "abcde")
        self.assertIn("split it", self.lint(GOOD.replace("       DONE when:", pad + "       DONE when:")).stdout)

    def test_go_without_open_task_and_stop_with_open_task_refused(self):
        none_open = GOOD.replace("Q2. Read set", "Q2. DONE Read set").replace("(after Q2)", "(after Q9)")
        self.assertIn("go with no unblocked open task", self.lint(none_open).stdout)
        r = self.lint(GOOD, "--want", "stop")
        self.assertEqual(r.returncode, 1)
        self.assertIn("stop refused", r.stdout)

    def test_handoff_refuses_bad_list_and_writes_nothing(self):
        self.f.write_text("# NEXT" + NL + "```" + NL + "Q" + NL + "   Q1. do things as needed" + NL + "```" + NL, encoding="utf-8", newline=NL)
        r = run(self.home, "handoff", "--file", str(self.f), "--go", extra=NOLINT_OFF)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("HANDOFF REFUSED", r.stdout)
        self.assertNotIn("relay:", self.f.read_text(encoding="utf-8"))

    def test_handoff_stop_allowed_when_all_done(self):
        self.f.write_text(GOOD.replace("Q2. Read set", "Q2. DONE Read set").replace("(after Q2)", "(after Q9)"), encoding="utf-8", newline=NL)
        r = run(self.home, "handoff", "--file", str(self.f), "--stop", "all done or blocked", extra=NOLINT_OFF)
        self.assertEqual(r.returncode, 0, r.stdout)


NUC = {"MTS_RELAY_HOST": "JIS-NUC", "MTS_RELAY_ACCOUNT": "acct-a"}
NB = {"MTS_RELAY_HOST": "JIS-NB", "MTS_RELAY_ACCOUNT": "acct-b"}


class TwoHostTest(unittest.TestCase):
    """Two hosts share one handoff through git; neither is tied to an account (relay-two-host-standby)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.f = self.tmp / "NEXT_SESSION.md"
        self.f.write_text("# NEXT SESSION\nbody\n", encoding="utf-8", newline="\n")
        self.runs = self.tmp / "relay_runs.jsonl"

    def kick(self, who, home, now, *extra_args):
        return run(self.tmp / home, "kick", "--file", str(self.f), *extra_args, now=now, extra=who)

    def test_handoff_records_host_account_session(self):
        r = run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", "--session", "relay 12", extra=NB)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        import json
        row = json.loads(self.runs.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual((row["host"], row["account"], row["session"], row["state"]), ("JIS-NB", "acct-b", "relay 12", "go"))
        self.assertIn("id=" + row["id"], self.f.read_text(encoding="utf-8"))

    def test_peer_fresh_handoff_keeps_other_host_idle_then_takeover(self):
        run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", extra=NB, now="2026-10-10T10:00:00Z")
        r = self.kick(NUC, "nuc", "2026-10-10T10:30:00Z", "--peer-quiet-min", "90")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("peer JIS-NB", r.stdout)
        r = self.kick(NUC, "nuc", "2026-10-10T11:31:00Z", "--peer-quiet-min", "90")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK", r.stdout)

    def test_own_handoff_and_flag_off_are_not_blocked(self):
        run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", extra=NB, now="2026-10-10T10:00:00Z")
        self.assertEqual(self.kick(NB, "nb", "2026-10-10T10:05:00Z", "--peer-quiet-min", "90").returncode, 0)
        self.assertEqual(self.kick(NUC, "nuc", "2026-10-10T10:05:00Z").returncode, 0)

    def test_account_switch_on_same_host_changes_nothing(self):
        run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", extra=NB, now="2026-10-10T10:00:00Z")
        other_account = {"MTS_RELAY_HOST": "JIS-NB", "MTS_RELAY_ACCOUNT": "acct-a"}
        self.assertEqual(self.kick(other_account, "nb", "2026-10-10T10:05:00Z", "--peer-quiet-min", "90").returncode, 0)

    def test_peer_stop_header_stays_idle(self):
        run(self.tmp / "nb", "handoff", "--file", str(self.f), "--stop", "operator question", extra=NB)
        r = self.kick(NUC, "nuc", "2026-10-10T18:00:00Z", "--peer-quiet-min", "90")
        self.assertEqual(r.returncode, 1)
        self.assertIn("handoff says stop", r.stdout)

    def test_oversize_handoff_moves_updates_to_history(self):
        block = "# NEXT\n```\nprompt\n   Q1. task\n```\n"
        self.f.write_text(block + "\n## Update one\n" + "x" * 3000 + "\n## Update two\nkeepme\n", encoding="utf-8", newline="\n")
        r = run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", extra={**NB, "MTS_RELAY_MAX_BYTES": "1000"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.f.read_text(encoding="utf-8")
        self.assertLess(len(text.encode("utf-8")), 1000)
        self.assertIn("Q1. task", text)
        self.assertNotIn("Update one", text)
        hist = list((self.tmp / "handoff_history").glob("*.md"))
        self.assertEqual(len(hist), 1)
        self.assertIn("keepme", hist[0].read_text(encoding="utf-8"))

    def test_oversize_block_is_refused_and_untouched(self):
        body = "# NEXT\n```\n" + "y" * 3000 + "\n```\n"
        self.f.write_text(body, encoding="utf-8", newline="\n")
        r = run(self.tmp / "nb", "handoff", "--file", str(self.f), "--go", extra={**NB, "MTS_RELAY_MAX_BYTES": "1000"})
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual(self.f.read_text(encoding="utf-8"), body)
        self.assertFalse(self.runs.exists())


if __name__ == "__main__":
    unittest.main()
