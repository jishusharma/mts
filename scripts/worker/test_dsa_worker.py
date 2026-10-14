"""Offline tests for the DSA browser worker lane, derived from
MyTradingSys/research/fast_track_2026-09-27/DSA_BROWSER_WORKER_PLAN.md
(flow per task, ground rules, reply schema, lane isolation). No browser, no playwright.
"""
import datetime as dt
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dsa_worker  # noqa: E402
import queue_tool  # noqa: E402
from dsa_worker import ChatPage, DsaWorker, PageError, write_atomic  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
REPLY_KEYS = {"schema", "id", "worker", "host", "model", "response", "done_reason",
              "worker_status", "started_utc", "finished_utc", "wall_seconds"}


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


class FakePage(ChatPage):
    """Answer streams for gen_s seconds after send, then stays constant."""

    def __init__(self, clock, answer="TASK: x\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: f\nNEXT: n\n",
                 gen_s=3.0, never_stops=False):
        self.clock, self.answer, self.gen_s, self.never_stops = clock, answer, gen_s, never_stops
        self.sent_at = None
        self.sent = []
        self.new_chats = 0
        self.challenge = False
        self.challenge_after_send = False
        self.send_error = None
        self.copy_text = None

    def new_chat(self):
        self.new_chats += 1
        self.sent_at = None

    def send(self, prompt):
        if self.send_error:
            raise self.send_error
        self.sent.append(prompt)
        self.sent_at = self.clock.now()

    def challenge_seen(self):
        if self.challenge_after_send and self.sent_at is not None:
            return True
        return self.challenge

    def _elapsed(self):
        return None if self.sent_at is None else self.clock.now() - self.sent_at

    def is_generating(self):
        e = self._elapsed()
        return e is not None and (self.never_stops or e < self.gen_s)

    def current_text(self):
        e = self._elapsed()
        if e is None:
            return ""
        if e >= self.gen_s and not self.never_stops:
            return self.answer
        n = max(1, int(len(self.answer) * min(e / self.gen_s, 0.9)))
        return self.answer[:n] if self.answer else ""

    def read_last(self):
        return self.copy_text if self.copy_text is not None else self.current_text()


def pkg(tid, prompt="hello", num_predict=4096, **extra):
    d = {"schema": 1, "id": tid, "task": "t", "model": "m", "num_ctx": 4096, "num_predict": num_predict,
         "prompt": prompt, "scope": [], "expect": [], "create": []}
    d.update(extra)
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.clock = Clock()
        self.cfg = dict(dsa_worker.DEFAULTS, queue_root=str(self.tmp))
        self.page = FakePage(self.clock)
        self.w = self.make_worker()
        self.inc = self.tmp / "incoming_dsa"
        self.clm = self.tmp / "claimed_dsa"
        self.done = self.tmp / "done"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_worker(self):
        return DsaWorker(self.page, self.cfg, clock=self.clock.now, sleep=self.clock.sleep, log=lambda m: None)

    def put(self, tid, lane_dir="incoming_dsa", **kw):
        d = self.tmp / lane_dir
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{tid}.task.json").write_text(json.dumps(pkg(tid, **kw)), encoding="utf-8")

    def reply(self, tid):
        return json.loads((self.done / f"{tid}.reply.json").read_text(encoding="utf-8"))

    def hb(self):
        return json.loads((self.tmp / "heartbeat_dsa.json").read_text(encoding="utf-8"))


class TestClaimAndReply(Base):
    def test_reply_schema_and_file_moves(self):
        self.put("001-a", prompt="PROMPT TEXT")
        self.assertEqual(self.w.step(), "done")
        r = self.reply("001-a")
        self.assertTrue(REPLY_KEYS <= set(r), REPLY_KEYS - set(r))
        self.assertEqual((r["schema"], r["id"], r["worker"], r["model"]), (1, "001-a", "dsa-web", "dsa-web"))
        self.assertEqual(r["worker_status"], "ok")
        self.assertEqual(r["done_reason"], "stop")
        self.assertIn("STATUS: DONE", r["response"])
        self.assertTrue(r["started_utc"].endswith("Z") and r["finished_utc"].endswith("Z"))
        self.assertGreater(r["wall_seconds"], 0)
        self.assertEqual(self.page.sent, ["PROMPT TEXT"])
        self.assertEqual(self.page.new_chats, 1)
        self.assertTrue((self.done / "001-a.task.json").exists())
        self.assertEqual(list(self.inc.glob("*.task.json")), [])
        self.assertEqual(list(self.clm.glob("*.task.json")), [])
        self.assertEqual(self.hb()["state"], "idle")

    def test_copy_button_text_preferred_over_inner_text(self):
        self.page.copy_text = "```py\nprint(1)\n```"
        self.put("002-b")
        self.w.step()
        self.assertEqual(self.reply("002-b")["response"], "```py\nprint(1)\n```")

    def test_tasks_processed_in_name_order(self):
        self.put("010-b")
        self.put("005-a")
        self.w.step()
        self.assertTrue((self.done / "005-a.reply.json").exists())
        self.assertFalse((self.done / "010-b.reply.json").exists())

    def test_idle_when_no_task(self):
        self.assertEqual(self.w.step(), "idle")
        self.assertEqual(self.hb()["state"], "idle")


class TestCompletion(Base):
    def test_not_done_while_stop_button_present(self):
        # text stops changing but the stop button stays: must run to timeout, not finish early
        self.page.never_stops = True
        self.put("003-c", num_predict=800)  # 800/8 = 100 s -> clamped to min_timeout_s 120
        self.w.step()
        r = self.reply("003-c")
        self.assertEqual(r["done_reason"], "timeout")
        self.assertGreaterEqual(r["wall_seconds"], 120)

    def test_stable_window_required(self):
        self.put("004-d")
        self.w.step()
        # generation takes 3 s, then text must stay unchanged stable_s (5 s)
        self.assertGreaterEqual(self.reply("004-d")["wall_seconds"], 3 + self.cfg["stable_s"])

    def test_timeout_capped_at_15_minutes(self):
        self.page.never_stops = True
        self.put("005-e", num_predict=10_000_000)
        self.w.step()
        r = self.reply("005-e")
        self.assertEqual(r["done_reason"], "timeout")
        self.assertLessEqual(r["wall_seconds"], 900 + 5)
        self.assertEqual(r["worker_status"], "ok")
        self.assertTrue(r["response"])


class TestPacing(Base):
    def test_min_gap_between_tasks(self):
        self.put("011-a")
        self.put("012-b")
        self.assertEqual(self.w.step(), "done")
        self.assertEqual(self.w.step(), "paced")
        self.assertEqual(list(self.done.glob("012-b.reply.json")), [])
        self.assertEqual(len(list(self.inc.glob("*.task.json"))), 1)
        self.clock.sleep(self.cfg["min_gap_s"] + 1)
        self.assertEqual(self.w.step(), "done")

    def test_hourly_cap(self):
        self.cfg.update(min_gap_s=0, max_per_hour=2, max_per_day=60)
        for i in range(3):
            self.put(f"02{i}-x")
        self.assertEqual(self.w.step(), "done")
        self.assertEqual(self.w.step(), "done")
        self.assertEqual(self.w.step(), "paced")
        self.clock.sleep(3601)
        self.assertEqual(self.w.step(), "done")

    def test_daily_cap(self):
        self.cfg.update(min_gap_s=0, max_per_hour=100, max_per_day=3)
        for i in range(4):
            self.put(f"03{i}-x")
        for _ in range(3):
            self.assertEqual(self.w.step(), "done")
            self.clock.sleep(4000)
        self.assertEqual(self.w.step(), "paced")
        self.clock.sleep(86400)
        self.assertEqual(self.w.step(), "done")

    def test_pace_history_survives_restart(self):
        self.put("041-a")
        self.put("042-b")
        self.w.step()
        w2 = self.make_worker()
        self.assertEqual(w2.step(), "paced")

    def test_once_ignores_min_gap_only(self):
        self.put("051-a")
        self.put("052-b")
        self.w.step()
        self.assertEqual(self.w.run(once=True), 0)
        self.assertTrue((self.done / "052-b.reply.json").exists())


    def test_stale_entries_dropped_and_pace_self_heals(self):
        """B080: entries older than 24h must not count and must be dropped from the file."""
        now = 1_800_000_000.0
        self.w.clock = lambda: now
        stale = [now - 86400 * 2, now - 86400 * 5, now - 86400 * 30]
        write_atomic(self.w.pace_path, json.dumps(stale))
        self.assertIsNone(self.w.pacing_block())
        kept = json.loads(self.w.pace_path.read_text())
        self.assertEqual(kept, [], "stale entries should be pruned from the pace file")

    def test_future_and_non_numeric_entries_dropped(self):
        """B080: future (>+60s) and non-numeric entries must not count toward any window."""
        now = 1_800_000_000.0
        self.w.clock = lambda: now
        write_atomic(self.w.pace_path, json.dumps([now + 600, now + 86400]))
        self.assertIsNone(self.w.pacing_block())
        self.assertEqual(json.loads(self.w.pace_path.read_text()), [],
                         "future entries should be pruned")
        # non-numeric in the file must not raise; load returns [] via the except branch
        self.w.pace_path.write_text(json.dumps(["x", None, 1.5]))
        self.assertIsNone(self.w.pacing_block())
    def test_stale_entries_dropped_and_pace_self_heals(self):
        """B080: entries older than 24h must not count and must be dropped from the file."""
        now = 1_800_000_000.0
        self.w.clock = lambda: now
        stale = [now - 86400 * 2, now - 86400 * 5, now - 86400 * 30]
        write_atomic(self.w.pace_path, json.dumps(stale))
        self.assertIsNone(self.w.pacing_block())
        kept = json.loads(self.w.pace_path.read_text())
        self.assertEqual(kept, [], "stale entries should be pruned from the pace file")

    def test_future_and_non_numeric_entries_dropped(self):
        """B080: future (>+60s) and non-numeric entries must not count toward any window."""
        now = 1_800_000_000.0
        self.w.clock = lambda: now
        write_atomic(self.w.pace_path, json.dumps([now + 600, now + 86400]))
        self.assertIsNone(self.w.pacing_block())
        self.assertEqual(json.loads(self.w.pace_path.read_text()), [],
                         "future entries should be pruned")
        # non-numeric in the file must not raise; load returns [] via the except branch
        self.w.pace_path.write_text(json.dumps(["x", None, 1.5]))
        self.assertIsNone(self.w.pacing_block())
class TestChallenge(Base):
    def test_challenge_pauses_and_requeues(self):
        self.page.challenge_after_send = True
        self.put("061-a")
        self.assertEqual(self.w.step(), "challenge")
        self.assertEqual(self.hb()["state"], "needs-human")
        self.assertTrue((self.inc / "061-a.task.json").exists())
        self.assertEqual(list(self.clm.glob("*.task.json")), [])
        self.assertEqual(list(self.done.glob("061-a.*")), [])

    def test_challenge_present_before_send_never_pastes(self):
        self.page.challenge = True
        self.put("062-a")
        self.assertEqual(self.w.step(), "challenge")
        self.assertEqual(self.page.sent, [])

    def test_stays_paused_then_resumes_when_cleared(self):
        self.page.challenge = True
        self.put("063-a")
        self.w.step()
        new_chats = self.page.new_chats
        self.assertEqual(self.w.step(), "needs-human")
        self.assertEqual(self.page.new_chats, new_chats)  # did not touch the page again
        self.assertEqual(self.hb()["state"], "needs-human")
        self.page.challenge = False
        self.assertEqual(self.w.step(), "done")
        self.assertEqual(self.reply("063-a")["worker_status"], "ok")

    def test_once_exit_code_needs_human(self):
        self.page.challenge = True
        self.put("064-a")
        self.assertEqual(self.w.run(once=True), 3)


class TestErrors(Base):
    def test_three_consecutive_errors_need_human(self):
        self.cfg.update(min_gap_s=0)
        self.page.send_error = PageError("selector missing")
        for i in range(3):
            self.put(f"07{i}-e")
        self.assertEqual(self.w.step(), "error")
        self.assertEqual(self.w.step(), "error")
        self.assertEqual(self.hb()["state"], "idle")
        self.assertEqual(self.w.step(), "error")
        self.assertEqual(self.hb()["state"], "needs-human")
        r = self.reply("070-e")
        self.assertEqual(r["worker_status"], "error")
        self.assertIn("selector missing", r["error"])
        self.put("079-next")
        self.assertEqual(self.w.step(), "needs-human")
        self.assertTrue((self.inc / "079-next.task.json").exists())
        # operator resumes
        self.page.send_error = None
        (self.tmp / "dsa_resume.flag").write_text("", encoding="utf-8")
        self.assertEqual(self.w.step(), "done")

    def test_success_resets_error_count(self):
        self.cfg.update(min_gap_s=0)
        self.page.send_error = PageError("boom")
        self.put("081-e")
        self.put("082-e")
        self.w.step()
        self.w.step()
        self.page.send_error = None
        self.put("083-ok")
        self.assertEqual(self.w.step(), "done")
        self.page.send_error = PageError("boom")
        self.put("084-e")
        self.put("085-e")
        self.w.step()
        self.w.step()
        self.assertNotEqual(self.hb()["state"], "needs-human")

    def test_prompt_too_long_is_error_reply_without_touching_page(self):
        self.cfg.update(max_prompt_chars=100, min_gap_s=0)
        self.put("091-big", prompt="x" * 101)
        self.assertEqual(self.w.step(), "error")
        r = self.reply("091-big")
        self.assertEqual(r["worker_status"], "error")
        self.assertIn("prompt too long", r["error"])
        self.assertEqual(self.page.sent, [])
        self.assertEqual(self.page.new_chats, 0)

    def test_empty_answer_is_error(self):
        self.page.answer = ""
        self.put("092-empty", num_predict=100)
        self.assertEqual(self.w.step(), "error")
        self.assertEqual(self.reply("092-empty")["worker_status"], "error")


class TestCrash(Base):
    def test_crash_returns_task_to_incoming_dsa(self):
        self.page.send_error = RuntimeError("driver died")
        self.put("101-a")
        with self.assertRaises(RuntimeError):
            self.w.step()
        self.assertTrue((self.inc / "101-a.task.json").exists())
        self.assertEqual(list(self.clm.glob("*.task.json")), [])
        self.assertEqual(list(self.done.glob("101-a.*")), [])

    def test_restore_claimed_on_start(self):
        self.put("102-a", lane_dir="claimed_dsa")  # left behind by a hard kill
        self.assertEqual(self.w.run(once=True), 0)
        self.assertTrue((self.done / "102-a.reply.json").exists())


class TestLaneIsolation(Base):
    def test_worker_never_touches_default_lane(self):
        self.put("201-q", lane_dir="incoming")
        self.put("202-q", lane_dir="claimed")
        self.put("203-d")
        self.w.run(once=True)
        self.assertTrue((self.tmp / "incoming" / "201-q.task.json").exists())
        self.assertTrue((self.tmp / "claimed" / "202-q.task.json").exists())
        self.assertFalse((self.done / "201-q.reply.json").exists())
        self.assertFalse((self.done / "202-q.reply.json").exists())
        self.assertTrue((self.done / "203-d.reply.json").exists())

    def test_worker_ignores_default_lane_when_own_lane_empty(self):
        self.put("204-q", lane_dir="incoming")
        self.assertEqual(self.w.step(), "idle")
        self.assertEqual(self.page.new_chats, 0)


class TestQueueTool(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.old_queue = queue_tool.QUEUE
        queue_tool.QUEUE = self.tmp
        # spec must live inside the repo (rel_of); scope is a small real file
        self.specdir = Path(tempfile.mkdtemp(dir=REPO, prefix=".tmp_dsa_test_"))
        self.spec = self.specdir / "900-dsa-hello.md"
        self.spec.write_text("TASK: say hello\nSCOPE: scripts/worker/dsa_selectors.json\n"
                             "OUTPUT: one line\nEXPECT: hello\n\nReply with the word hello.\n", encoding="utf-8")

    def tearDown(self):
        queue_tool.QUEUE = self.old_queue
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.specdir, ignore_errors=True)

    def run_tool(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = queue_tool.main(list(argv))
        return rc, buf.getvalue()

    def test_pack_default_lane_goes_to_incoming_only(self):
        rc, out = self.run_tool("pack", str(self.spec))
        self.assertEqual(rc, 0, out)
        self.assertTrue((self.tmp / "incoming" / "900-dsa-hello.task.json").exists())
        self.assertEqual(list((self.tmp / "incoming_dsa").glob("*.task.json")), [])
        self.assertNotIn("lane", json.loads((self.tmp / "incoming" / "900-dsa-hello.task.json").read_text()))

    def test_pack_dsa_lane_goes_to_incoming_dsa_only(self):
        rc, out = self.run_tool("pack", "--lane", "dsa", str(self.spec))
        self.assertEqual(rc, 0, out)
        self.assertTrue((self.tmp / "incoming_dsa" / "900-dsa-hello.task.json").exists())
        self.assertEqual(list((self.tmp / "incoming").glob("*.task.json")), [])

    def test_duplicate_id_refused_across_lanes(self):
        self.run_tool("pack", "--lane", "dsa", str(self.spec))
        rc, out = self.run_tool("pack", str(self.spec))
        self.assertEqual(rc, 1)
        self.assertIn("already exists", out)

    def test_status_prints_dsa_worker_line(self):
        self.run_tool("pack", "--lane", "dsa", str(self.spec))
        rc, out = self.run_tool("status")
        line = [ln for ln in out.splitlines() if ln.startswith("DSA-WORKER")]
        self.assertEqual(len(line), 1, out)
        self.assertIn("incoming_dsa 1", line[0])
        (self.tmp / "heartbeat_dsa.json").write_text(json.dumps(
            {"host": "H", "state": "running", "task": "900-dsa-hello", "utc": queue_tool.utc_stamp(),
             "worker": "dsa-web"}), encoding="utf-8")
        rc, out = self.run_tool("status")
        line = [ln for ln in out.splitlines() if ln.startswith("DSA-WORKER")][0]
        self.assertIn("running", line)
        self.assertIn("900-dsa-hello", line)

    # --- lane status: both lanes are dormant by design, so an absent or stale heartbeat is not an alarm
    def beat(self, name, age_s, **kw):
        t = queue_tool.utc_now() - dt.timedelta(seconds=age_s)
        hb = {"host": "H", "state": "idle", "task": "", "utc": queue_tool.utc_stamp(t), "worker": "w"}
        hb.update(kw)
        (self.tmp / name).write_text(json.dumps(hb), encoding="utf-8")

    def status_lines(self):
        rc, out = self.run_tool("status")
        self.assertEqual(rc, 0, out)
        by = lambda prefix: [ln for ln in out.splitlines() if ln.startswith(prefix)]
        return out, by("WORKER"), by("DSA-WORKER")

    def test_status_without_heartbeats_says_the_lanes_are_retired_not_missing(self):
        self.run_tool("pack", "--lane", "dsa", str(self.spec))
        out, worker, dsa = self.status_lines()
        self.assertEqual(len(worker), 1, out)
        self.assertIn("retired 2026-10-01", worker[0])
        self.assertIn("Qwen", worker[0])
        self.assertEqual(len(dsa), 1, out)
        self.assertIn("dormant", dsa[0])
        self.assertIn("AIBridge", dsa[0])
        self.assertIn("incoming_dsa 1; running 0", dsa[0])  # counts stay
        for stale_wording in ("no heartbeat", "version 2", "not running", "WARNING"):
            self.assertNotIn(stale_wording, out)
        self.assertIn("QUEUE    waiting 0", out)

    def test_status_with_old_heartbeats_is_dormant_and_names_the_last_beat(self):
        self.beat("heartbeat.json", 7 * 86400, host="JIS-NUC")
        self.beat("heartbeat_dsa.json", 3 * 86400, state="needs-human", worker="dsa-web")
        out, worker, dsa = self.status_lines()
        self.assertIn("retired 2026-10-01", worker[0])
        self.assertIn("last heartbeat idle 168 h ago", worker[0])
        self.assertIn("dormant", dsa[0])
        self.assertIn("last heartbeat needs-human", dsa[0])
        self.assertNotIn("WARNING", out)  # neither the NUC-off alarm nor the needs-human alarm: the lane is not supposed to run

    def test_status_heartbeat_age_boundary_is_three_minutes(self):
        self.beat("heartbeat.json", 150)
        self.beat("heartbeat_dsa.json", 200)
        out, worker, dsa = self.status_lines()
        self.assertNotIn("retired", worker[0])
        self.assertIn("idle", worker[0])
        self.assertIn("dormant", dsa[0])

    def test_status_fresh_heartbeats_print_the_live_lines(self):
        self.beat("heartbeat.json", 5, state="running", task="777-x", host="JIS-NUC", worker="abc")
        self.beat("heartbeat_dsa.json", 5, state="needs-human", note="challenge or login page; clear it by hand")
        out, worker, dsa = self.status_lines()
        self.assertIn("running task 777-x", worker[0])
        self.assertIn("host JIS-NUC", worker[0])
        self.assertNotIn("retired", worker[0])
        self.assertIn("needs-human", dsa[0])
        self.assertNotIn("dormant", dsa[0])
        self.assertIn("WARNING  DSA worker needs the operator", out)

    def test_status_unreadable_heartbeat_is_still_reported(self):
        (self.tmp / "heartbeat.json").write_text("{not json", encoding="utf-8")
        (self.tmp / "heartbeat_dsa.json").write_text("{not json", encoding="utf-8")
        out, worker, dsa = self.status_lines()
        self.assertIn("heartbeat unreadable", worker[0])
        self.assertIn("heartbeat unreadable", dsa[0])

    def test_verify_accepts_dsa_reply_end_to_end(self):
        self.run_tool("pack", "--lane", "dsa", str(self.spec))
        clock = Clock()
        cfg = dict(dsa_worker.DEFAULTS, queue_root=str(self.tmp))
        page = FakePage(clock, answer="TASK: t\nSTATUS: DONE\nSUMMARY: hello\nFINDINGS: f\nNEXT: n\n")
        w = DsaWorker(page, cfg, clock=clock.now, sleep=clock.sleep, log=lambda m: None)
        self.assertEqual(w.step(), "done")
        rc, out = self.run_tool("verify")
        self.assertEqual(rc, 0, out)
        self.assertIn("STATUS:   DONE", out)
        self.assertTrue((self.tmp / "done" / "900-dsa-hello.verdict.txt").exists())

    def test_verify_fails_timeout_reply(self):
        self.run_tool("pack", "--lane", "dsa", str(self.spec))
        (self.tmp / "done").mkdir(exist_ok=True)
        (self.tmp / "done" / "900-dsa-hello.reply.json").write_text(json.dumps(
            {"schema": 1, "id": "900-dsa-hello", "worker": "dsa-web", "host": "H", "model": "dsa-web",
             "response": "hello", "done_reason": "timeout", "worker_status": "ok",
             "started_utc": "x", "finished_utc": "y", "wall_seconds": 900}), encoding="utf-8")
        rc, out = self.run_tool("verify", "900-dsa-hello")
        self.assertEqual(rc, 2, out)
        self.assertIn("timed out", out)


if __name__ == "__main__":
    unittest.main()
