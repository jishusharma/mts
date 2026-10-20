"""Fixtures for scripts/sched/relay.py: header stamping, every kick IDLE condition, KICK writes the launch lock, unlock frees it."""
import json
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

    def kick(self, now="2026-10-10T10:00:00Z"):
        return run(self.home, "kick", "--file", str(self.f), now=now)

    def test_unlock_lets_the_next_handoff_start_at_once(self):
        # 2026-10-10 06:42 chain death: a short session handed over a NEW id 15 min after the previous launch and the
        # old 20-minute clock lock stopped the chain. The KICK session frees the lock itself now (relay_session.md step 6).
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(self.kick().returncode, 0)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        waiting = self.kick(now="2026-10-10T10:15:00Z")
        self.assertEqual(waiting.returncode, 1, waiting.stdout)
        self.assertIn("chain is moving", waiting.stdout)
        lock = self.home / "mts-relay-lock.json"
        self.assertTrue(lock.exists())
        u = run(self.home, "unlock", now="2026-10-10T10:15:00Z")
        self.assertEqual(u.returncode, 0, u.stderr)
        self.assertIn("UNLOCKED", u.stdout)
        self.assertFalse(lock.exists())
        r = self.kick(now="2026-10-10T10:16:00Z")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK depth=1", r.stdout)
        self.assertEqual(run(self.home, "unlock").returncode, 0)   # nothing to free is not an error

    def test_kick_starts_a_go_handoff(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")  # depth 2
        r = self.kick()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("KICK depth=2 id=" + self.header_id(), r.stdout)
        lock = json.loads((self.home / "mts-relay-lock.json").read_text(encoding="utf-8"))
        self.assertEqual((lock["id"], lock["depth"]), (self.header_id(), 2))

    def test_the_dead_launch_path_is_gone(self):
        # B164 (2026-10-10): an unattended session cannot run_scheduled_task another one, so `gate` and the A/B task names are gone
        run(self.home, "handoff", "--file", str(self.f), "--go")
        g = run(self.home, "gate", "--file", str(self.f), "--started-id", "none")
        self.assertEqual(g.returncode, 2)
        self.assertIn("invalid choice", g.stderr)
        k = self.kick()
        self.assertNotIn("task=", k.stdout)
        self.assertNotIn("mts-relay-", k.stdout)
        self.assertNotIn("lock=", self.kick(now="2026-10-10T10:20:00Z").stdout)

    def test_kick_idles_when_chain_moving_or_session_on_it(self):
        run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertEqual(self.kick().returncode, 0)
        moving = self.kick(now="2026-10-10T10:20:00Z")
        self.assertEqual(moving.returncode, 1)
        self.assertIn("chain is moving", moving.stdout)
        working = self.kick(now="2026-10-10T10:50:00Z")
        self.assertEqual(working.returncode, 1)
        self.assertIn("session still on it", working.stdout)
        retry = self.kick(now="2026-10-10T11:10:00Z")  # same id, 70 min: never started or died, retry (was 3 h)
        self.assertEqual(retry.returncode, 0, retry.stdout)

    def test_kick_idles_on_stop_header_no_header_and_stop_flag(self):
        self.assertEqual(self.kick().returncode, 1)
        self.assertIn("no relay header", self.kick().stdout)
        run(self.home, "handoff", "--file", str(self.f), "--stop", "queue empty")
        r = self.kick()
        self.assertEqual(r.returncode, 1)
        self.assertIn("queue empty", r.stdout)
        run(self.home, "handoff", "--file", str(self.f), "--go")
        run(self.home, "stop", "weekly budget")
        self.assertIn("stop flag", self.kick().stdout)
        run(self.home, "resume")
        self.assertEqual(self.kick().returncode, 0)

    def test_depth_increments_and_resets(self):
        for _ in range(3):
            run(self.home, "handoff", "--file", str(self.f), "--go")
        self.assertIn("depth=2", self.f.read_text(encoding="utf-8"))
        run(self.home, "handoff", "--file", str(self.f), "--go", "--reset-depth")
        self.assertIn("depth=0", self.f.read_text(encoding="utf-8"))
        self.assertEqual(self.f.read_text(encoding="utf-8").count("relay:"), 1)


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

    def test_duplicate_task_id_is_a_lint_error(self):
        dup = GOOD.replace("   Q3. (after Q2) engine run.", "   Q2. DONE older task reusing the id." + NL + "   Q3. (after Q2) engine run.")
        r = self.lint(dup, "--want", "go")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("Q2 is used twice", r.stdout)
        self.assertEqual(self.lint(GOOD, "--want", "go").returncode, 0)

    def test_host_tag_filters_go_for_other_hosts(self):
        nb = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB Read set")
        self.assertEqual(self.lint(nb, "--want", "go").returncode, 0)  # host=None: any host may run it
        r = self.lint(nb, "--want", "go", "--host", "JIS-NUC")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("for host JIS-NUC", r.stdout)
        self.assertIn("Q2=JIS-NB", r.stdout)
        self.assertEqual(self.lint(nb, "--want", "go", "--host", "jis-nb").returncode, 0)  # case-insensitive
        any_ = GOOD.replace("Q2. Read set", "Q2. host=any Read set")
        self.assertEqual(self.lint(any_, "--want", "go", "--host", "JIS-NUC").returncode, 0)

    def test_host_tag_is_stripped_before_done_and_blocked(self):
        t = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB DONE Read set").replace("Q3. (after Q2)", "Q3. host=JIS-NB (after Q9)")
        self.f.write_text(t, encoding="utf-8", newline=NL)
        r = run(self.home, "handoff", "--file", str(self.f), "--stop", "all done or blocked", extra=NOLINT_OFF)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_handoff_go_not_filtered_by_this_host(self):
        # NUC finishing its task must be able to hand a go to NB: stop is refused while a task is open
        nb = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB Read set").replace("`scripts/dev/shot.py`", "shots").replace("research/screenshots", "the dir")
        nb = nb.replace("shot.py status", "status")
        self.f.write_text(nb, encoding="utf-8", newline=NL)
        extra = dict(NOLINT_OFF, MTS_RELAY_HOST="JIS-NUC")
        self.assertEqual(run(self.home, "handoff", "--file", str(self.f), "--go", extra=extra).returncode, 0)

    def test_lint_fails_over_the_size_cap_and_passes_at_it(self):
        # 2026-10-14: NEXT_SESSION.md was 12643 bytes against the 12288 cap and `lint` said OK; the refusal only came at handoff
        self.f.write_text(GOOD, encoding="utf-8", newline=NL)
        size = len(GOOD.encode("utf-8"))
        args = ("lint", "--file", str(self.f), "--root", str(REPO))
        r = run(self.home, *args, extra=dict(NOLINT_OFF, MTS_RELAY_MAX_BYTES=str(size - 1)))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("%d bytes" % size, r.stdout)
        self.assertIn("cap %d" % (size - 1), r.stdout)
        self.assertIn("LINT FAIL", r.stdout)
        r = run(self.home, *args, extra=dict(NOLINT_OFF, MTS_RELAY_MAX_BYTES=str(size)))
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


class HostKickTest(unittest.TestCase):
    """kick honors the `host=` task tag: a go whose open tasks all belong to another host is IDLE here, KICK there."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.f = self.tmp / "NEXT_SESSION.md"
        self.f.write_text(GOOD.replace("Q2. Read set", "Q2. host=JIS-NB Read set"), encoding="utf-8", newline=NL)

    def kick(self, who, *args):
        return run(self.tmp / who["MTS_RELAY_HOST"], "kick", "--file", str(self.f), *args, extra=dict(NOLINT_OFF, **who))

    def test_nb_only_tasks_idle_on_nuc_kick_on_nb(self):
        r = self.kick(NUC)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("IDLE no unblocked task for host JIS-NUC", r.stdout)
        self.assertIn("KICK", self.kick(NB).stdout)

    def test_other_lint_errors_do_not_block_a_kick(self):
        self.f.write_text(GOOD.replace("DONE when: research/screenshots has the extract and shot.py status shows the set done.", "no end"),
                          encoding="utf-8", newline=NL)
        self.assertIn("KICK", self.kick(NUC).stdout)


class HostTagEdgeTest(unittest.TestCase):
    """RV08 (2026-10-14): host= tag edge cases. A wrong IDLE leaves a host without work; a wrong KICK pays for an empty session."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.f = self.tmp / "NEXT_SESSION.md"

    def write(self, text):
        self.f.write_text(text, encoding="utf-8", newline=NL)

    def lint(self, text, *args):
        self.write(text)
        return run(self.tmp / "home", "lint", "--file", str(self.f), "--root", str(REPO), *args, extra=NOLINT_OFF)

    def kick(self, text, who):
        self.write(text)
        return run(Path(tempfile.mkdtemp(dir=str(self.tmp))), "kick", "--file", str(self.f), "--root", str(REPO),
                   extra=dict(NOLINT_OFF, MTS_RELAY_HOST=who))

    def test_lower_and_mixed_case_tag_matches(self):
        for tag in ("host=jis-nuc", "host=Jis-Nuc", "HOST=JIS-NUC"):
            t = GOOD.replace("Q2. Read set", "Q2. %s Read set" % tag)
            self.assertEqual(self.lint(t, "--want", "go", "--host", "JIS-NUC").returncode, 0, tag)
            self.assertIn("KICK", self.kick(t, "JIS-NUC").stdout, tag)

    def test_any_in_any_case_runs_everywhere(self):
        t = GOOD.replace("Q2. Read set", "Q2. host=ANY Read set")
        for who in ("JIS-NB", "JIS-NUC", "laptop"):
            self.assertIn("KICK", self.kick(t, who).stdout, who)

    def test_two_tags_on_one_line_is_a_lint_error(self):
        t = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB host=JIS-NUC Read set")
        r = self.lint(t, "--want", "go")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("Q2 has 2 host= tags", r.stdout)

    def test_tag_on_continuation_line_is_a_lint_error(self):
        t = GOOD.replace("       DONE when: research", "       host=JIS-NB DONE when: research")
        r = self.lint(t, "--want", "go")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("Q2 has host= on a continuation line", r.stdout)

    def test_task_after_a_task_of_the_other_host(self):
        # Q3 (NUC) waits on Q2 (NB): NUC has nothing runnable, NB does
        t = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB Read set").replace("Q3. (after Q2)", "Q3. host=JIS-NUC (after Q2)")
        r = self.kick(t, "JIS-NUC")
        self.assertIn("IDLE no unblocked task for host JIS-NUC", r.stdout)
        self.assertIn("KICK", self.kick(t, "JIS-NB").stdout)

    def test_hostname_with_domain_suffix_matches_its_tag(self):
        t = GOOD.replace("Q2. Read set", "Q2. host=JIS-NB Read set")
        self.assertEqual(self.lint(t, "--want", "go", "--host", "JIS-NB.lan").returncode, 0)
        self.assertIn("KICK", self.kick(t, "jis-nb.localdomain").stdout)
        self.assertIn("IDLE", self.kick(t, "JIS-NUC.lan").stdout)

    def test_only_done_rows_idle_not_kick(self):
        t = GOOD.replace("Q2. Read set", "Q2. DONE Read set").replace("Q3. (after Q2) engine", "Q3. DONE engine")
        r = self.kick(t, "JIS-NB")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("IDLE no unblocked open task", r.stdout)


SYNC_STUB = """import sys, os
a = sys.argv[1:]
if a[0] == "start":
    if os.environ.get("STUB_SYNC_FAIL"):
        print("sync: merge of origin/fast-track conflicts"); sys.exit(1)
    print("host=T branch=x pulled=0")
elif a[0] == "claim":
    if os.environ.get("STUB_CLAIM_FAIL"):
        print("claim refused"); sys.exit(1)
    if os.path.exists("MyTradingSys/system/claims/" + a[1] + ".md"):   # what the real sync.py does for an existing slug
        print("sync: already claimed by JIS-NUC / sharma: " + a[1] + ". Pick another task or ask them."); sys.exit(1)
    open("claimed.txt", "w").write(a[1])
"""
TASKS_STUB = """import sys, os
if sys.argv[1] == "next":
    if os.environ.get("STUB_NEXT"):   # lines separated by |
        print(os.environ["STUB_NEXT"].replace("|", chr(10)))
    else:
        print("opus-card [OPUS, M, p1] big thing")
        print("sonnet-card [SONNET, M, p1] the task")
        print("second-card [SONNET, S, p2] later")
elif sys.argv[1] == "brief":
    print("TASK " + sys.argv[2] + " brief line")
"""


SYNC_API_STUB = """import sys, os
TRUNK = "fast-track"
class SyncError(Exception):
    pass
def slugify(s):
    return s.lower()
def read_claims(wt, ref):
    return []
if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "claim":
        open("claimed.txt", "w").write(a[1])
    else:
        print("host=T branch=x pulled=0")
"""
TASKS_API_STUB = """import sys
CODE_LANES = ["HAIKU", "SONNET", "OPUS"]
if __name__ == "__main__":
    if sys.argv[1] == "next":
        print("sonnet-card [SONNET, M, p1] the task")
    elif sys.argv[1] == "brief":
        print("TASK " + sys.argv[2] + " brief line")
"""


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=str(cwd), check=True, capture_output=True)


class BeginTest(unittest.TestCase):
    """relay.py begin: worktree + sync start + first ready non-OPUS card + claim + brief in one call (B172 cut 2)."""

    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.origin, self.clone = tmp / "origin.git", tmp / "clone"
        git(tmp, "init", "-q", "--bare", str(self.origin))
        git(tmp, "clone", "-q", str(self.origin), str(self.clone))
        git(self.clone, "checkout", "-q", "-b", "fast-track")
        d = self.clone / "scripts" / "dev"
        d.mkdir(parents=True)
        (d / "sync.py").write_text(SYNC_STUB, encoding="utf-8", newline=NL)
        (d / "tasks.py").write_text(TASKS_STUB, encoding="utf-8", newline=NL)
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-q", "-m", "stubs")
        git(self.clone, "push", "-q", "origin", "fast-track")
        self.wt = tmp / "mts-relay"
        self.relay_home = tmp / "relay-home"

    def claim_on_origin(self, slug):
        """A claim as `sync.py claim` leaves it: a file on origin's side branch `claims` (D10 2026-10-20), none on trunk."""
        sys.path.insert(0, str(SCRIPT.parents[2] / "scripts" / "dev"))
        import sync
        sync.push_claim_commit(self.clone, sync.CLAIMS_DIR + "/" + slug + ".md",
                               NL.join(["task: " + slug, "host: JIS-NUC", "account: sharma", "area: -", "epoch: 1", ""]), "claim " + slug)
        sync.fetch_claims(self.clone)

    def begin(self, extra=None, *args):
        # per-host relay state (the begin log row) goes to this test's own dir, never to the operator's ~/.claude
        env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
        env.update({"MTS_RELAY_HOME": str(self.relay_home), **(extra or {})})
        return subprocess.run([sys.executable, str(SCRIPT), "begin", "--root", str(self.clone), "--worktree", str(self.wt),
                               "--branch", "t/relay", *args], capture_output=True, text=True, env=env)

    def test_begin_picks_ready_task_and_claims(self):
        r = self.begin()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("claimed: sonnet-card", r.stdout)
        self.assertIn("TASK sonnet-card brief line", r.stdout)
        self.assertLessEqual(len(r.stdout.splitlines()), 30)
        self.assertEqual((self.wt / "claimed.txt").read_text(), "sonnet-card")

    def test_begin_stops_on_sync_failure(self):
        r = self.begin({"STUB_SYNC_FAIL": "1"})
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("BEGIN FAILED", r.stdout)
        self.assertNotIn("claimed:", r.stdout)
        self.assertFalse((self.wt / "claimed.txt").exists())

    def test_begin_skips_opus_and_claimed(self):
        r = self.begin(None, "--skip", "sonnet-card")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("claimed: second-card", r.stdout)
        self.assertNotIn("opus-card", r.stdout.split("brief")[0].replace("TASK", ""))

    def test_begin_fails_closed_on_claim_error(self):
        r = self.begin({"STUB_CLAIM_FAIL": "1"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("BEGIN FAILED", r.stdout)
        self.assertNotIn("brief line", r.stdout)

    def test_begin_skips_a_card_that_holds_a_claim_on_origin(self):
        # 2026-10-14 (b172-trim): `tasks.py next` listed the claimed card first, `sync.py claim` refused it ("already claimed")
        # and begin printed BEGIN FAILED, so the relay stopped itself on every host
        self.claim_on_origin("sonnet-card")
        r = self.begin()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("claimed: second-card", r.stdout)
        self.assertEqual((self.wt / "claimed.txt").read_text(), "second-card")

    def test_begin_claim_match_is_by_slug_of_the_card_id(self):
        self.claim_on_origin("b172-trim")   # sync.py files the claim under slugify(id): lower case
        r = self.begin({"STUB_NEXT": "B172-Trim [SONNET, M, p1] held|second-card [SONNET, S, p2] later"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.wt / "claimed.txt").read_text(), "second-card")

    def test_begin_takes_only_builder_lanes(self):
        # a card of lane DSA matched the old [A-Z0-9]+ lane pattern and was claimed by a builder; DSA-NB / DSA-NUC / JIS-NB never matched, by accident
        lines = ["dsa-card [DSA, S, p1] run", "dsa-nb-card [DSA-NB, S, p1] run", "dsa-nuc-card [DSA-NUC, S, p1] run",
                 "jis-card [JIS-NB, S, p1] live", "codex-card [CODEX, M, p1] lab", "opus-card [OPUS, M, p1] big",
                 "haiku-card [HAIKU, S, p2] small", "sonnet-card [SONNET, S, p2] code"]
        r = self.begin({"STUB_NEXT": "|".join(lines)})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.wt / "claimed.txt").read_text(), "haiku-card")

    def test_begin_with_only_run_lane_cards_claims_nothing(self):
        r = self.begin({"STUB_NEXT": "dsa-card [DSA, S, p1] run|jis-card [JIS-NB, S, p1] live|dsa-nb-card [DSA-NB, S, p1] run"})
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("BEGIN FAILED", r.stdout)
        self.assertFalse((self.wt / "claimed.txt").exists())

    def test_begin_with_no_ready_card_still_names_the_synced_worktree(self):
        # a `look=` wake-up (a finished lane result to read) may find no ready card: the session still edits the handoff in the
        # relay tree begin already built, so the failure line is preceded by `worktree: <path>` and no card is claimed
        r = self.begin({"STUB_NEXT": "dsa-card [DSA, S, p1] run"})
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("worktree: %s" % self.wt.resolve(), r.stdout.splitlines())
        self.assertTrue(r.stdout.splitlines()[-1].startswith("BEGIN FAILED: no ready"), r.stdout)
        self.assertFalse((self.wt / "claimed.txt").exists())

    def test_begin_runs_from_a_copy_outside_the_tree(self):
        # 2026-10-14: the dispatcher runs a copy of relay.py from %TEMP%/mts_relay/, where there is no sibling scripts/dev: begin made the
        # worktree, ran `sync.py start`, then printed "BEGIN FAILED: scripts/dev next to relay.py". The modules come from the relay tree.
        d = self.clone / "scripts" / "dev"
        (d / "sync.py").write_text(SYNC_API_STUB, encoding="utf-8", newline=NL)
        (d / "tasks.py").write_text(TASKS_API_STUB, encoding="utf-8", newline=NL)
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-q", "-m", "stubs with an importable api")
        git(self.clone, "push", "-q", "origin", "fast-track")
        copy = self.wt.parent / "temp-copy" / "mts_relay"
        copy.mkdir(parents=True)
        for name in ("relay.py", "handoff_lint.py"):
            (copy / name).write_text((SCRIPT.parent / name).read_text(encoding="utf-8"), encoding="utf-8", newline=NL)
        env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_RELAY")}
        env["MTS_RELAY_HOME"] = str(self.relay_home)
        r = subprocess.run([sys.executable, str(copy / "relay.py"), "begin", "--root", str(self.clone), "--worktree", str(self.wt),
                            "--branch", "t/relay"], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("claimed: sonnet-card", r.stdout)
        self.assertEqual((self.wt / "claimed.txt").read_text(), "sonnet-card")

    def test_begin_writes_its_log_row_under_MTS_RELAY_HOME_only(self):
        # every gate run used to append begin rows for the stub cards to the real ~/.claude/mts-relay-log.jsonl (163 rows by 2026-10-14)
        stamp = "2031-01-02T03:04:05Z"   # a time no real run has: the check holds even while another process appends to the real log
        real = Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude") / "mts-relay-log.jsonl"
        r = self.begin({"MTS_RELAY_NOW": stamp})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        mine = self.relay_home / "mts-relay-log.jsonl"
        self.assertTrue(mine.exists(), "begin must log under MTS_RELAY_HOME")
        self.assertIn(stamp, mine.read_text(encoding="utf-8"))
        self.assertNotIn(stamp, real.read_text(encoding="utf-8") if real.exists() else "")


if __name__ == "__main__":
    unittest.main()
