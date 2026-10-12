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
        self.assertFalse(R.limit_hit("INCOMPLETE", ["a.md"], CREDITS_LOG))   # it wrote something: a normal incomplete run
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


class Reroute(unittest.TestCase):
    def setUp(self):
        self.down = L.record_run(L.blank(), "LIMIT", "credits", NOW)

    def test_down_moves_noncrucial_pauses_crucial(self):
        cards = [card("a-audit"), card("b-run", "run"), card("c-build", "build"), card("d-crucial", crucial=True), card("e-only", gpt_only=True)]
        pl = L.plan(self.down, cards, {}, set())
        self.assertEqual({c["id"]: to for c, to in pl["reroute"]}, {"a-audit": "DSA", "b-run": "DSA", "c-build": "SONNET"})
        self.assertEqual(sorted(c["id"] for c, _ in pl["paused"]), ["d-crucial", "e-only"])
        self.assertIn("credits", pl["paused"][0][1])

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

    def cards(self):
        return {c["id"]: c for c in T.load_all(self.repo)}

    def test_credit_outage_then_recovery(self):
        L.save(self.repo, L.record_run(L.blank(), "LIMIT", "credits", NOW))
        line = L.sweep(self.repo, NOW, do_apply=True)
        self.assertIn("gpt=down reason=credits moved=2 paused=1", line)
        c = self.cards()
        self.assertEqual((c["a-audit"]["reroute"]["to"], c["a-audit"]["lane"]), ("DSA", "CODEX"))
        self.assertEqual((c["c-build"]["lane"], c["d-crucial"].get("reroute")), ("SONNET", None))
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
