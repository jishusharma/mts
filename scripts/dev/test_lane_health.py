"""lane_health.py: GPT-lane down/up rules, error-text detection, reroute/pause/resume plan, DSA prompt format, Control Room view,
and the codex_run hooks (pick skips rerouted cards, an out-of-credits run counts as a limit, not a try)."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_run as R
import desk
import lane_health as L
import relay_board
import tasks as T

NOW = datetime(2026, 10, 12, 18, 0, tzinfo=timezone.utc)
# Error text as the Codex CLI prints it (kept as a fixture; extend it when a new wording is seen in a real log).
# Real text from JIS-NUC, 2026-10-12: lab-audit-fabio-ledger-frames (gpt-6-astra, 777 s of work, 8 files written, then this) and the
# 5-second gpt-6.1-sol LIMIT runs ("try again at 9:30 PM", NUC local time = UTC+5:30).
REAL = "ERROR: You\u2019ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at Oct 13th, 2026 2:32 AM."
CREDITS_LOG = "x" * 6000 + "\n" + REAL + "\n" + REAL + "\ntokens used\n383,362\n"
LIMIT_LOG = "x" * 6000 + "\nERROR: usage limit reached, try again at 22:41\n"
ECHOED_PROMPT = "Rules: an out of credits error marks the lane down.\n" + "y" * 6000 + "\nlab: card DONE ok\n"


def card(cid, kind="audit", **kw):
    c = R.make_card(f"Card {cid}", kind, ["MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md"], cid=cid,
                    cmds=["python x.py"] if kind == "run" else [], tests="test_x fails first" if kind == "build" else "")
    c.update({"state": "ready", **kw})
    return c


class Detect(unittest.TestCase):
    def test_credits_and_limit_text(self):
        self.assertEqual(L.classify(CREDITS_LOG), "credits")
        self.assertEqual(L.classify(LIMIT_LOG), "limit")
        for t in ("insufficient_quota", "You have exceeded your current quota", "Your credit balance is too low", "credits exhausted"):
            self.assertEqual(L.classify("a" * 5000 + t), "credits", t)

    def test_real_astra_error_is_found_and_its_line_kept(self):
        self.assertIn("try again at Oct 13th, 2026 2:32 AM", L.error_line(CREDITS_LOG))
        self.assertTrue(L.error_line(CREDITS_LOG).startswith("ERROR"))
        st = L.record_run(L.blank(), "INCOMPLETE", L.classify(CREDITS_LOG), NOW, L.error_line(CREDITS_LOG))   # INCOMPLETE: files were written
        self.assertEqual((st["status"], st["reason"]), ("down", "credits"))
        self.assertIn("2:32 AM", st["detail"])

    def test_text_far_from_the_end_is_ignored(self):
        self.assertEqual(L.classify(ECHOED_PROMPT), "")
        self.assertEqual(L.classify(""), "")

    def test_codex_run_counts_credit_failure_as_limit_not_a_try(self):
        self.assertTrue(R.limit_hit("INCOMPLETE", [], CREDITS_LOG))
        self.assertTrue(R.limit_hit("INCOMPLETE", ["a.md"], CREDITS_LOG))   # partial files do not hide it (they are salvaged)
        self.assertFalse(R.limit_hit("DONE", [], CREDITS_LOG))
        self.assertFalse(R.limit_hit("INCOMPLETE", [], ECHOED_PROMPT))


class Rules(unittest.TestCase):
    def test_credit_error_marks_lane_down_at_once_and_a_done_run_brings_it_back(self):
        st = L.record_run(L.blank(), "LIMIT", "credits", NOW)
        self.assertEqual((st["status"], st["reason"], st["since"]), ("down", "credits", "2026-10-12T18:00:00Z"))
        later = NOW + timedelta(hours=2)
        up = L.record_run(st, "DONE", "", later)
        self.assertEqual((up["status"], up["resumed"]), ("up", L.iso(later)))

    def test_since_keeps_the_first_failure_time(self):
        st = L.record_run(L.blank(), "LIMIT", "credits", NOW)
        again = L.record_run(st, "LIMIT", "credits", NOW + timedelta(hours=1))
        self.assertEqual(again["since"], st["since"])

    def test_three_empty_runs_in_a_row_mark_down_a_blocked_run_resets(self):
        st = L.blank()
        for _ in range(2):
            st = L.record_run(st, "INCOMPLETE", "", NOW)
        self.assertEqual(st["status"], "up")
        self.assertEqual(L.record_run(st, "INCOMPLETE", "", NOW)["reason"], "failing")
        self.assertEqual(L.record_run(st, "BLOCKED", "", NOW)["fails"], 0)

    def test_heartbeat_window(self):
        st = L.beat(L.blank(), NOW)
        self.assertEqual(L.sweep_state(st, NOW + timedelta(hours=2, minutes=59))["status"], "up")
        down = L.sweep_state(st, NOW + timedelta(hours=3, minutes=1))
        self.assertEqual((down["status"], down["reason"]), ("down", "heartbeat"))
        back = L.sweep_state(L.beat(down, NOW + timedelta(hours=4)), NOW + timedelta(hours=4))
        self.assertEqual(back["status"], "up")

    def test_no_heartbeat_ever_is_not_down(self):
        self.assertEqual(L.sweep_state(L.blank(), NOW)["status"], "up")

    def test_heartbeat_does_not_clear_a_credit_outage(self):
        st = L.record_run(L.blank(), "LIMIT", "credits", NOW)
        self.assertEqual(L.sweep_state(L.beat(st, NOW), NOW)["status"], "down")

    def test_probe_once_per_hour_and_never_for_manual_or_heartbeat(self):
        st = L.record_run(L.blank(), "LIMIT", "credits", NOW)
        self.assertEqual(L.allow(st, NOW + timedelta(minutes=30)), "")
        self.assertEqual(L.allow(st, NOW + timedelta(minutes=61)), "probe")
        probed = dict(st, last_probe=L.iso(NOW + timedelta(minutes=61)))
        self.assertEqual(L.allow(probed, NOW + timedelta(minutes=90)), "")
        self.assertEqual(L.allow(L.blank(), NOW), "go")
        self.assertEqual(L.allow(L.go_down(L.blank(), "manual", "x", NOW), NOW + timedelta(days=1)), "")


class Window(unittest.TestCase):
    RL = {"primary": {"used_percent": 99.0, "resets_at": int(datetime(2026, 10, 12, 21, 2, tzinfo=timezone.utc).timestamp())},
          "secondary": {"used_percent": 58.0, "resets_at": int(datetime(2026, 10, 18, 13, 41, tzinfo=timezone.utc).timestamp())}}

    def test_spent_window_marks_lane_down_until_reset_and_reroutes(self):
        now = NOW.timestamp()
        self.assertTrue(R.hold(self.RL, now))
        end = R.hold_until(self.RL, now)
        self.assertEqual(end, self.RL["primary"]["resets_at"])
        st = L.go_down(L.blank(), "window", R.hold(self.RL, now), NOW, datetime.fromtimestamp(end, timezone.utc))
        self.assertEqual((st["status"], st["reason"], st["until"]), ("down", "window", "2026-10-12T21:02:00Z"))
        self.assertEqual(L.allow(st, NOW), "")                                    # holds, and never probes (a probe would only hit the limit)
        self.assertEqual(L.allow(st, NOW + timedelta(hours=2)), "")
        pl = L.plan(st, [card("a-audit"), card("b-run", "run")], {}, set())
        self.assertEqual(len(pl["reroute"]), 2)

    def test_window_lane_returns_by_itself_after_reset_and_cards_go_back(self):
        st = L.go_down(L.blank(), "window", "x", NOW, datetime(2026, 10, 12, 21, 2, tzinfo=timezone.utc))
        before = L.sweep_state(st, datetime(2026, 10, 12, 21, 1, tzinfo=timezone.utc))
        self.assertEqual(before["status"], "down")
        after = L.sweep_state(st, datetime(2026, 10, 12, 21, 3, tzinfo=timezone.utc))
        self.assertEqual((after["status"], after["until"]), ("up", ""))
        self.assertEqual(L.allow(st, datetime(2026, 10, 12, 21, 3, tzinfo=timezone.utc)), "go")
        c = card("a-audit", reroute={"to": "DSA", "desk": "d1"})
        self.assertEqual(len(L.plan(after, [c], {"d1": {"status": "pending"}}, set())["cancel"]), 1)

    def test_window_already_reset_is_not_held(self):
        self.assertEqual(R.hold(self.RL, self.RL["primary"]["resets_at"] + 1), "")
        self.assertEqual(R.hold_until(self.RL, self.RL["primary"]["resets_at"] + 1), 0)


class Override(unittest.TestCase):
    def test_operator_up_skips_allowance_precheck_until_expiry_and_a_limit_error_clears_it(self):
        with tempfile.TemporaryDirectory() as d:
            old = L.REPO
            L.REPO = Path(d)
            try:
                st = L.go_down(L.blank(), "window", "x", NOW, NOW + timedelta(hours=3))
                L.save(L.REPO, st)
                L.main(["up", "operator: GPT is back"])
                st = L.load(L.REPO)
            finally:
                L.REPO = old
        self.assertEqual((st["status"], st["until"]), ("up", ""))
        self.assertTrue(L.override_active(st, datetime.now(timezone.utc)))
        self.assertFalse(L.override_active(st, datetime.now(timezone.utc) + timedelta(hours=4)))
        self.assertFalse(L.override_active(L.blank(), NOW))
        down = L.record_run(st, "LIMIT", "limit", NOW)
        self.assertEqual(down["override"], "")


class CommitShip(unittest.TestCase):
    def test_backslash_paths_match_git_status_and_commit(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            def g(*a):
                return subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t", *a], capture_output=True, text=True)
            g("init", "-q")
            (Path(d) / "sub").mkdir()
            (Path(d) / "sub" / "x.json").write_text("{}\n")
            g("add", "-A")
            g("commit", "-qm", "base")
            (Path(d) / "sub" / "x.json").write_text('{"a": 1}\n')
            before = int(g("rev-list", "--count", "HEAD").stdout.strip())
            old = L.git
            L.git = lambda repo, *a, check=True: g(*a)   # keeps the test's git identity
            try:
                L.commit_ship(d, ["sub\\x.json"], "lane test")   # the ship step fails here (no sync.py): only the commit matters
            finally:
                L.git = old
            self.assertEqual(int(g("rev-list", "--count", "HEAD").stdout.strip()), before + 1)

class HeartbeatSideBranch(unittest.TestCase):
    """B17: an hourly heartbeat must not edit lane_state.json (that was 55 trunk commits in 72 h); it goes to a side branch."""

    def setUp(self):
        import subprocess
        self.d = tempfile.TemporaryDirectory()
        root = Path(self.d.name)
        self.sub = lambda *a, cwd=root: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True)
        self.sub("init", "-q", "--bare", "remote.git")
        self.repo, self.other = root / "lab", root / "watchdog"
        for r in (self.repo, self.other):
            self.sub("clone", "-q", str(root / "remote.git"), r.name)
        L.save(self.repo, L.blank())
        T.save(self.repo, card("a-audit"))
        self.sub("add", "-A", cwd=self.repo)
        self.sub("commit", "-qm", "base", cwd=self.repo)
        self.sub("push", "-q", "origin", "HEAD:refs/heads/main", cwd=self.repo)
        self.sub("pull", "-q", "origin", "main", cwd=self.other)

    def tearDown(self):
        self.d.cleanup()

    def test_beat_goes_to_the_side_branch_and_the_state_file_stays_clean(self):
        L.sweep(self.repo, NOW, do_apply=True, beating=True)
        L.sweep(self.repo, NOW + timedelta(hours=2), do_apply=True, beating=True)
        self.assertEqual(self.sub("status", "--porcelain", "--", L.STATE, cwd=self.repo).stdout.strip(), "")
        self.assertEqual(L.load(self.repo)["heartbeat"], "")
        self.assertEqual(self.sub("show", f"{L.HB_REF}:heartbeat", cwd=Path(self.d.name) / "remote.git").stdout.strip(), L.iso(NOW + timedelta(hours=2)))
        self.assertEqual(self.sub("rev-list", "--count", L.HB_REF, cwd=Path(self.d.name) / "remote.git").stdout.strip(), "2")

    def test_another_host_sees_the_beat_and_a_dead_lab_still_goes_down(self):
        L.sweep(self.repo, NOW, do_apply=True, beating=True)
        line = L.sweep(self.other, NOW + timedelta(hours=1), do_apply=True)   # watchdog, no --beat: reads the side branch
        self.assertIn("gpt=up", line)
        self.assertEqual(L.load(self.other)["heartbeat"], "")
        line = L.sweep(self.other, NOW + timedelta(hours=4), do_apply=True)   # lab silent for 4 h > HEARTBEAT_DOWN_S
        self.assertIn("gpt=down reason=heartbeat", line)
        self.assertEqual(L.load(self.other)["heartbeat"], L.iso(NOW))   # a real state change still saves, with the newest beat in it

    def test_the_lab_beating_after_a_long_silence_stays_up(self):
        # JIS-NUC 2026-10-22 15:06Z: the first tick after a 34 h stall judged its own old heartbeat, went down and moved 5 cards off CODEX
        L.sweep(self.repo, NOW, do_apply=True, beating=True)
        line = L.sweep(self.repo, NOW + timedelta(hours=34), do_apply=True, beating=True)
        self.assertIn("gpt=up", line)
        self.assertIn("moved=0", line)

    def test_no_remote_falls_back_to_the_state_file(self):
        with tempfile.TemporaryDirectory() as d:
            T.save(Path(d), card("a-audit"))
            L.sweep(Path(d), NOW, do_apply=True, beating=True)
            self.assertEqual(L.load(Path(d))["heartbeat"], L.iso(NOW))


class Reroute(unittest.TestCase):
    def setUp(self):
        self.down = L.record_run(L.blank(), "LIMIT", "credits", NOW)

    def test_down_moves_noncrucial_pauses_crucial(self):
        cards = [card("a-audit"), card("b-run", "run"), card("c-build", "build"), card("d-crucial", crucial=True), card("e-only", gpt_only=True)]
        pl = L.plan(self.down, cards, {}, set())
        self.assertEqual({c["id"]: to for c, to in pl["reroute"]}, {"a-audit": "DSA", "b-run": "DSA", "c-build": "SONNET"})
        self.assertEqual(sorted(c["id"] for c, _ in pl["paused"]), ["d-crucial", "e-only"])
        self.assertIn("credits", pl["paused"][0][1])

    def test_card_that_needs_images_goes_to_claude_not_dsa(self):
        c = card("v-audit", goal="Frames are images under F:/MTS/data/fabio_videos/frames: open them.")
        self.assertTrue(L.needs_vision(c))
        self.assertEqual(L.plan(self.down, [c], {}, set())["reroute"][0][1], "SONNET")
        self.assertFalse(L.needs_vision(card("plain")))

    def test_up_moves_nothing(self):
        pl = L.plan(L.blank(), [card("a"), card("d", crucial=True)], {}, set())
        self.assertEqual([len(v) for v in pl.values()], [0] * 6)

    def test_resume_cancels_untaken_row_restores_unclaimed_build_keeps_taken(self):
        rr = lambda to, **kw: {"to": to, "desk": "r1", **kw}
        cards = [card("a", reroute=rr("DSA")), card("b", reroute=rr("DSA", desk="r2")), card("c", lane="SONNET", reroute={"to": "SONNET", "from": "CODEX"}),
                 card("d", lane="SONNET", reroute={"to": "SONNET", "from": "CODEX"})]
        rows = {"r1": {"id": "r1", "status": "pending"}, "r2": {"id": "r2", "status": "taken"}}
        pl = L.plan(L.blank(), cards, rows, {"d"})
        self.assertEqual([c["id"] for c, _ in pl["cancel"]], ["a"])
        self.assertEqual([c["id"] for c in pl["restore"]], ["c"])   # d is claimed by a Claude session: stays
        self.assertEqual(pl["close"], [])

    def test_done_row_closes_card_failed_row_pauses_it(self):
        cards = [card("a", reroute={"to": "DSA", "desk": "r1"}), card("b", reroute={"to": "DSA", "desk": "r2"})]
        pl = L.plan(self.down, cards, {"r1": {"id": "r1", "status": "done"}, "r2": {"id": "r2", "status": "failed"}}, set())
        self.assertEqual(([c["id"] for c, _ in pl["close"]], [c["id"] for c, _ in pl["clear"]]), (["a"], ["b"]))

    def test_dsa_prompt_follows_the_bridge_rules(self):
        c = card("b-run", "run", goal="rerun T089 for 2024", steps=["do it"] * 3)
        need = L.dsa_need(c, NOW)
        self.assertIn("mts-dsa", need)
        self.assertIn("2026-10-12_b-run.md", need)
        self.assertIn("--failed", need)
        for line in need.splitlines():
            self.assertLessEqual(len(line), 200)
            self.assertFalse(line.lstrip().startswith("#"), line)


class EndToEnd(unittest.TestCase):
    """A real work tree on disk: down -> rows and lanes change; up -> they change back; the Control Room view shows both."""

    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.repo = Path(self.d.name)
        for c in (card("a-audit"), card("c-build", "build"), card("d-crucial", crucial=True)):
            T.save(self.repo, c)

    def tearDown(self):
        self.d.cleanup()

    def test_lane_health_review_gate_errors_fail_closed(self):
        from unittest.mock import patch
        L.save(self.repo, L.record_run(L.blank(), 'LIMIT', 'credits', NOW))
        L.sweep(self.repo, NOW, do_apply=True)
        row = next(r for r in desk.tasks(self.repo) if r['card'] == 'a-audit')
        row.update(status='done', result='evidence')
        desk.save(self.repo, row)
        with patch.object(T, 'review_gate', side_effect=RuntimeError('broken gate')):
            out = L.sweep(self.repo, NOW + timedelta(hours=1), do_apply=True)
        self.assertNotEqual(self.cards()['a-audit']['state'], 'done')
        self.assertIn('review gate error', out)

    def cards(self):
        return {c["id"]: c for c in T.load_all(self.repo)}

    def test_credit_outage_then_recovery(self):
        L.save(self.repo, L.record_run(L.blank(), "LIMIT", "credits", NOW))
        line = L.sweep(self.repo, NOW, do_apply=True)
        self.assertIn("gpt=down reason=credits moved=2 paused=1", line)
        c = self.cards()
        self.assertEqual((c["a-audit"]["reroute"]["to"], c["a-audit"]["lane"]), ("DSA", "CODEX"))
        self.assertEqual((c["c-build"]["lane"], c["d-crucial"].get("reroute")), ("SONNET", None))
        self.assertEqual(T.problems(c["c-build"]), [])   # still a ready card in its new lane
        row = desk.get(self.repo, c["a-audit"]["reroute"]["desk"])
        self.assertEqual((row["target"], row["status"], row["card"]), ("DSA", "pending", "a-audit"))
        v = relay_board.gpt_lane(self.repo, NOW)
        self.assertEqual((v["status"], [m["id"] for m in v["rerouted"]], [p["id"] for p in v["paused"]]), ("down", ["a-audit", "c-build"], ["d-crucial"]))
        self.assertIn("PAUSED", L.status_text(v))
        # a second sweep does not post a second row
        L.sweep(self.repo, NOW + timedelta(minutes=30), do_apply=True)
        self.assertEqual(len(desk.tasks(self.repo)), 1)
        # GPT is back (a probe finished): untaken row cancelled, build card home, crucial card needs no change
        L.save(self.repo, L.record_run(L.load(self.repo), "DONE", "", NOW + timedelta(hours=2)))
        line = L.sweep(self.repo, NOW + timedelta(hours=2), do_apply=True)
        self.assertIn("gpt=up", line)
        c = self.cards()
        self.assertEqual((c["a-audit"].get("reroute"), c["c-build"]["lane"], c["c-build"].get("reroute")), (None, "CODEX", None))
        self.assertEqual(desk.tasks(self.repo)[0]["status"], "failed")
        self.assertEqual(relay_board.gpt_lane(self.repo, NOW)["paused"], [])

    def test_vision_audit_moves_to_sonnet_with_a_test_and_comes_back_clean(self):
        T.save(self.repo, card("v-audit", goal="Open the frames (png) and compare."))
        L.save(self.repo, L.record_run(L.blank(), "LIMIT", "credits", NOW))
        L.sweep(self.repo, NOW, do_apply=True)
        v = self.cards()["v-audit"]
        self.assertEqual((v["lane"], v["tests"]), ("SONNET", L.REPORT_TEST))
        self.assertEqual(T.problems(v), [])
        L.save(self.repo, L.record_run(L.load(self.repo), "DONE", "", NOW + timedelta(hours=2)))
        L.sweep(self.repo, NOW + timedelta(hours=2), do_apply=True)
        v = self.cards()["v-audit"]
        self.assertEqual((v["lane"], v["tests"], v.get("reroute")), ("CODEX", "", None))

    def test_finished_dsa_row_closes_the_card(self):
        L.save(self.repo, L.record_run(L.blank(), "LIMIT", "credits", NOW))
        L.sweep(self.repo, NOW, do_apply=True)
        row = desk.tasks(self.repo)[0]
        row.update(status="done", result="verdict SOUND, report r.md")
        desk.save(self.repo, row)
        L.sweep(self.repo, NOW + timedelta(hours=1), do_apply=True)
        done = self.cards()["a-audit"]
        self.assertEqual(done["state"], "done")
        self.assertIn("via DSA", done["result"])

    def test_finished_dsa_row_does_not_close_unreviewed_hard_card(self):
        for extra in ({"weight": "crucial"}, {"class": "C2"}):
            with self.subTest(extra=extra):
                c = self.cards()["a-audit"]
                c.update(extra)
                T.save(self.repo, c)
                L.save(self.repo, L.record_run(L.blank(), "LIMIT", "credits", NOW))
                L.sweep(self.repo, NOW, do_apply=True)
                row = desk.tasks(self.repo)[0]
                row.update(status="done", result="verdict SOUND, report r.md")
                desk.save(self.repo, row)
                out = L.sweep(self.repo, NOW + timedelta(hours=1), do_apply=True)
                self.assertNotEqual(self.cards()["a-audit"]["state"], "done")
                self.assertIn("not closed", out)

    def test_codex_run_skips_rerouted_and_prefers_crucial_on_probe(self):
        cs = [card("a", reroute={"to": "DSA", "desk": "r"}), card("b"), card("c", crucial=True)]
        self.assertEqual(R.pick(cs, set(), {})["id"], "b")
        self.assertEqual(R.pick(cs, set(), {}, probe=True)["id"], "c")

    def test_flag_command_sets_and_clears(self):
        old = T.REPO
        T.REPO = self.repo
        try:
            T.main(["flag", "a-audit", "crucial"])
            self.assertTrue(self.cards()["a-audit"]["crucial"])
            T.main(["flag", "a-audit", "crucial", "--off"])
            self.assertNotIn("crucial", self.cards()["a-audit"])
        finally:
            T.REPO = old


if __name__ == "__main__":
    unittest.main()
