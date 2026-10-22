"""codex_run.py (layer lab runner): card choice, model/effort from the card, the command line, the lock, the ask templates,
the delivery index, and the CODEX lane rules in tasks.py. Spec: MyTradingSys/system/LAYER_LAB.md."""
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
import unittest.mock
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_run as R
import tasks as T


def card(cid="lab-a", kind="audit", **kw):
    c = R.make_card("Audit the Tom v2 spec", kind, ["MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md"], cid=cid,
                    cmds=kw.pop("cmds", ["python x.py"] if kind == "run" else []), tests=kw.pop("tests", "test_x fails first" if kind == "build" else ""))
    c.update({"state": "ready", **kw})
    return c


class BuildPromptLintTest(unittest.TestCase):
    def test_build_steps_tell_the_lab_to_run_the_lookahead_lint(self):
        text = " ".join(R.TEMPLATES["build"]["steps"])
        self.assertIn("lookahead_lint.py --new", text)
        self.assertIn("times[1:]", text)
        self.assertIn("lookahead_allowlist.tsv", text)


class LaneRulesTest(unittest.TestCase):
    def test_each_kind_template_meets_the_definition_of_ready(self):
        for kind in R.TEMPLATES:
            with self.subTest(kind=kind):
                if kind != "build":
                    self.assertEqual(T.problems(card(kind=kind)), [])
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    repo = Path(tmp)
                    probe = repo / "scripts/dev/test_mutation.py"
                    probe.parent.mkdir(parents=True)
                    probe.write_text("def test_dummy_output_rejected():\n    assert output != 'dummy'\n", encoding="utf-8")
                    c = card(kind=kind, mutation_check="scripts/dev/test_mutation.py::test_dummy_output_rejected")
                    self.assertEqual(T.problems(c, repo=repo), [])

    def test_build_template_leaves_the_gate_to_the_runner(self):
        text = " ".join(R.TEMPLATES["build"]["steps"]) + R.TEMPLATES["build"]["done_when"]
        self.assertIn("Do not run scripts/dev/run_all_tests.py", text)
        self.assertNotIn("quick gate passes", text)

    def test_kind_is_required_and_checked(self):
        self.assertTrue(any("kind" in m for m in T.problems(card(kind="audit") | {"kind": ""})))
        self.assertTrue(any("kind" in m for m in T.problems(card() | {"kind": "think"})))

    def test_build_needs_tests_and_run_needs_commands(self):
        self.assertTrue(any("tests" in m for m in T.problems(card(kind="build", tests=""))))
        self.assertTrue(any("commands" in m for m in T.problems(card(kind="run", cmds=[]))))

    def test_effort_override_is_checked(self):
        self.assertTrue(any("effort" in m for m in T.problems(card(effort="huge"))))
        self.assertEqual(T.problems(card(effort="xhigh")), [])

    def test_setting_defaults_to_luna_and_astra_needs_a_crucial_flag(self):
        # operator 2026-10-13: bulk and revalidation work on luna low/medium; astra only for crucial cards, medium unless the card says high
        self.assertEqual(T.codex_setting(card(kind="audit")), ("gpt-6-luna", "medium"))
        self.assertEqual(T.codex_setting(card(kind="build")), ("gpt-6-luna", "medium"))
        self.assertEqual(T.codex_setting(card(kind="run")), ("gpt-6-luna", "low"))
        self.assertEqual(T.codex_setting(card(cid="rv05-fabio-pass", kind="audit")), ("gpt-6-luna", "medium"))
        # operator 2026-10-13 (second rule): astra runs at the lightest effort only, whatever the card asks for
        self.assertEqual(T.codex_setting(card(kind="audit", crucial=True)), ("gpt-6-astra", "low"))
        self.assertEqual(T.codex_setting(card(kind="audit", crucial=True, effort="high")), ("gpt-6-astra", "low"))
        self.assertEqual(T.codex_setting(card(kind="audit", crucial=True, effort="medium")), ("gpt-6-astra", "low"))
        self.assertEqual(T.codex_setting(card(kind="audit", crucial=True, model="gpt-6-astra", effort="max")), ("gpt-6-astra", "low"))
        self.assertEqual(T.codex_setting(card(kind="run", gpt_only=True)), ("gpt-6-astra", "low"))
        # a card that names astra without the flag runs on luna; it keeps the effort it asked for
        self.assertEqual(T.codex_setting(card(kind="audit", model="gpt-6-astra", effort="medium")), ("gpt-6-luna", "medium"))
        self.assertEqual(T.codex_setting(card(kind="build", model="gpt-6-astra", effort="max")), ("gpt-6-luna", "max"))
        # any other named model is honoured
        self.assertEqual(T.codex_setting(card(kind="build", model="gpt-6.1-sol", effort="low")), ("gpt-6.1-sol", "low"))

    def test_brief_names_the_report_and_fits_the_cap(self):
        b = T.brief(card())
        self.assertIn("layer_lab/reports/<UTC date>_lab-a.md", b)
        self.assertLessEqual(len(b.splitlines()), T.MAX_BRIEF)

    def test_plain_next_hides_codex_cards_from_claude_sessions(self):
        with tempfile.TemporaryDirectory() as d:
            T.save(d, card())
            old, T.REPO = T.REPO, Path(d)
            try:
                for lane, want in ((None, "NO_READY_CARD"), ("CODEX", "lab-a [CODEX")):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        T.main(["next"] + (["--lane", lane] if lane else []))
                    self.assertIn(want, buf.getvalue())
            finally:
                T.REPO = old


class PickTest(unittest.TestCase):
    def test_skips_claimed_stuck_and_foreign_lanes(self):
        a, b, c, s = card("lab-a"), card("lab-b"), card("lab-c"), card("son") | {"lane": "SONNET"}
        self.assertEqual(R.pick([s, a, b, c], {"lab-a"}, {"lab-b": R.MAX_ATTEMPTS})["id"], "lab-c")
        self.assertIsNone(R.pick([s], set(), {}))
        self.assertEqual(R.pick([a, b], set(), {"lab-a": R.MAX_ATTEMPTS - 1})["id"], "lab-a")

    def test_attempts_count_only_real_runs_that_did_not_finish(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            rows = [{"card": "x", "outcome": "INCOMPLETE"}, {"card": "x", "outcome": "BLOCKED"}, {"card": "x", "outcome": "DONE"},
                    {"card": "y", "outcome": "INCOMPLETE", "dry": True}]
            (p / "runs.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
            self.assertEqual(R.attempts(d), {"x": 2})
            self.assertEqual(R.attempts(Path(d) / "none"), {})

    def test_reopened_stamp_resets_earlier_failed_tries_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            rows = [{"card": "x", "outcome": "SHIP_FAILED"}, {"card": "x", "outcome": "SHIP_FAILED"},
                    {"card": "x", "outcome": "REOPENED"}, {"card": "x", "outcome": "BLOCKED"}, {"card": "y", "outcome": "BLOCKED"}]
            (p / "runs.jsonl").write_text(chr(10).join(json.dumps(r) for r in rows) + chr(10), encoding="utf-8")
            self.assertEqual(R.attempts(d), {"x": 1, "y": 1})


class CommandTest(unittest.TestCase):
    def test_model_effort_and_sandbox_reach_the_command_line(self):
        cmd = R.command("codex.exe", card(kind="audit", crucial=True, effort="high"), "F:/wt", "workspace-write")
        self.assertEqual(cmd[:4], ["codex.exe", "exec", "-m", "gpt-6-astra"])
        self.assertIn('model_reasoning_effort="low"', cmd)
        self.assertNotIn('model_reasoning_effort="high"', cmd)
        self.assertEqual(cmd[cmd.index("-s") + 1], "workspace-write")
        self.assertEqual(cmd[cmd.index("-C") + 1], "F:/wt")
        self.assertEqual(cmd[-1], "-")
        self.assertIn("gpt-6-luna", R.command("codex.exe", card(kind="run"), "F:/wt", "workspace-write"))

    def test_prompt_forbids_git_and_carries_report_and_brief(self):
        p = R.prompt(card(), "F:/wt", "F:/home/packs/lab-a.md", datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc))
        for want in ("do NOT run git", "layer_lab/reports/2026-10-12_lab-a.md", "tasks.py done lab-a", "do NOT mark the card done", "TASK lab-a [CODEX"):
            self.assertIn(want, p)
        self.assertNotIn("sync.py claim \"", p)

    def test_prompt_names_the_dev_kline_source_so_cards_do_not_block_on_missing_data(self):
        # gptb-volume / gptb-candle ended BLOCKED 4x: the brief named no data path and Codex looked in Dumps/backtest and binance_tf (2025+ only)
        p = R.prompt(card(kind="build"), "F:/wt", "F:/home/packs/lab-a.md", datetime(2026, 10, 17, 9, 5, tzinfo=timezone.utc))
        for want in ("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz", "2024-07-01", "NOT the DEV source"):
            self.assertIn(want, p)

    def test_commit_message_has_result_and_session_trailer(self):
        m = R.commit_message(card(), "DONE", "FIX-FIRST, 2 HIGH", datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc))
        self.assertIn("Result: FIX-FIRST, 2 HIGH", m)
        self.assertIn("MTS-Session: MTS-2026-10-12-0905Z-COD-LAB-lab-a", m)
        self.assertIn("gpt-6-luna / medium", m)


class JudgeTest(unittest.TestCase):
    REP = "MyTradingSys/research/layer_lab/reports/2026-10-12_lab-a.md"
    CARD = "MyTradingSys/system/tasks/lab-a.json"

    def test_done_needs_the_card_closed_and_a_report(self):
        self.assertEqual(R.judge({"state": "done"}, [self.REP], "audit", [self.REP, self.CARD]), "DONE")
        self.assertEqual(R.judge({"state": "ready"}, [self.REP], "audit", [self.REP]), "BLOCKED")
        self.assertEqual(R.judge({"state": "done"}, [], "audit", [self.CARD]), "INCOMPLETE")
        self.assertEqual(R.judge({"state": "ready"}, [], "audit", []), "INCOMPLETE")

    def test_audit_and_run_may_not_write_code_but_build_may(self):
        code = "MyTradingSys/backtest/tom_dax_bt.py"
        for kind in ("audit", "run"):
            self.assertEqual(R.judge({"state": "done"}, [self.REP], kind, [self.REP, self.CARD, code]), "OUT_OF_SCOPE")
        self.assertEqual(R.judge({"state": "done"}, [self.REP], "build", [self.REP, self.CARD, code]), "DONE")
        self.assertEqual(R.out_of_scope("run", [self.REP, "MyTradingSys/research/layer_lab/TRIALS.md", "MyTradingSys/system/tasks/new.json"]), [])

    def test_the_generated_layers_page_is_not_out_of_scope(self):
        # tasks.py rewrites LAYERS.md after every card change, so closing a krown-/malkan-/tom-... card always dirties it
        # (malkan-hindi-rows-gpt-read, 2026-10-15 16:00Z: OUT_OF_SCOPE, 41 window points spent, nothing shipped)
        layers = "MyTradingSys/system/LAYERS.md"
        for kind in ("audit", "run"):
            self.assertEqual(R.judge({"state": "done"}, [self.REP], kind, [self.REP, self.CARD, layers]), "DONE")
        self.assertEqual(R.out_of_scope("audit", [layers, "MyTradingSys/system/NEXT_SESSION.md"]), ["MyTradingSys/system/NEXT_SESSION.md"])

    def test_out_of_scope_and_ship_failures_count_as_tries(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            (p / "runs.jsonl").write_text(json.dumps({"card": "x", "outcome": "OUT_OF_SCOPE"}) + chr(10) + json.dumps({"card": "x", "outcome": "SHIP_FAILED"}) + chr(10), encoding="utf-8")
            self.assertEqual(R.attempts(d), {"x": 2})

    def test_exe_lookup_order(self):
        self.assertEqual(R.find_exe({"MTS_CODEX_EXE": "X"}, lambda n: "P", lambda g: ["G"]), "X")
        self.assertEqual(R.find_exe({}, lambda n: "P", lambda g: ["G"]), "P")
        self.assertEqual(R.find_exe({"LOCALAPPDATA": "L"}, lambda n: None, lambda g: ["G"]), "G")
        with self.assertRaises(SystemExit):
            R.find_exe({}, lambda n: None, lambda g: [])


class BudgetTest(unittest.TestCase):
    LINE = ('{"type":"event_msg","payload":{"type":"token_count","rate_limits":{"limit_id":"codex","primary":{"used_percent":%s,'
            '"window_minutes":300,"resets_at":5000},"secondary":{"used_percent":%s,"window_minutes":10080,"resets_at":90000},"plan_type":"plus"}}}')

    def reading(self, d, five, week):
        p = Path(d) / "sessions" / "2026" / "10" / "12"
        p.mkdir(parents=True, exist_ok=True)
        (p / "rollout-a.jsonl").write_text('{"type":"other"}\n' + self.LINE % (five, week) + '\nnot json\n', encoding="utf-8")
        return R.budget(d)

    def test_reading_comes_from_the_newest_session_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R.budget(d))
            rl = self.reading(d, 70.0, 11.0)
            self.assertEqual((rl["primary"]["used_percent"], rl["secondary"]["resets_at"]), (70.0, 90000))

    def test_full_window_holds_the_card_until_it_resets(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R.hold(self.reading(d, 70.0, 11.0), 1000), "")
            full = self.reading(d, float(R.WINDOW_STOP), 11.0)
            self.assertIn("5-hour window 85% used, resets 1970-01-01 01:23Z", R.hold(full, 1000))
            self.assertEqual(R.hold(full, 5001), "")
            self.assertIn("weekly allowance", R.hold(self.reading(d, 10.0, float(R.WEEK_STOP)), 5001))
            self.assertEqual(R.hold(None, 1000), "")
            self.assertIn("5-hour window 0% used; week 85% used", R.budget_line(self.reading(d, 99.0, 85.0), 5001))

    def test_a_run_stopped_by_the_allowance_is_not_a_try(self):
        self.assertTrue(R.limit_hit("INCOMPLETE", [], "ERROR: You've hit your usage limit. Try again at 4:17 AM."))
        self.assertTrue(R.limit_hit("INCOMPLETE", ["a.md"], "noise\n" * 400 + "ERROR: You've hit your usage limit."))
        self.assertFalse(R.limit_hit("INCOMPLETE", ["a.md"], "the doc says usage limit\n" + "x\n" * 2000))
        self.assertFalse(R.limit_hit("DONE", [], "usage limit"))
        self.assertFalse(R.limit_hit("INCOMPLETE", [], "tokens used\n9"))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lab_runs"
            p.mkdir()
            (p / "runs.jsonl").write_text(json.dumps({"card": "x", "outcome": "LIMIT"}) + "\n", encoding="utf-8")
            self.assertEqual(R.attempts(d), {})


class StatusTest(unittest.TestCase):
    ROW = {"at": "2026-10-12T05:47:00Z", "card": "lab-a", "model": "gpt-6.1-sol", "effort": "medium", "tokens": 94135, "seconds": 452}

    def test_needs_look_names_each_thing_the_lab_cannot_fix(self):
        a, b, c = card("lab-a"), card("lab-b"), card("lab-c")
        self.assertEqual(R.needs_look([a, b, c], {}, [self.ROW | {"outcome": "DONE"}]), [])
        look = R.needs_look([a], {"lab-a": R.MAX_ATTEMPTS}, [self.ROW | {"outcome": "SHIP_FAILED", "note": "gate failed"}], unshipped=2, stopped="why")
        text = " | ".join(look)
        for want in ("switched off: why", "2 unshipped", "lab-a failed 2 times", "ended SHIP_FAILED (lab-a): gate failed", "queue is empty"):
            self.assertIn(want, text)
        self.assertIn("only 1 card(s) left", R.needs_look([a], {}, [])[0])
        self.assertEqual(R.needs_look([a], {}, [self.ROW | {"outcome": "LIMIT"}], held="window full"), [])
        self.assertEqual(R.needs_look([a, b, c], {}, [self.ROW | {"outcome": "SHIP_FAILED"}], closed={"lab-a"}), [])

    def test_status_is_plain_text_with_queue_deliveries_and_runs(self):
        done = card("lab-old", state="done", closed="2026-10-11T08:00:00Z", result="SOUND")
        t = R.status_text([card("lab-a"), card("lab-b"), card("lab-c")], [done], {}, [self.ROW | {"outcome": "DONE"}], None, 1791784000, "06:30Z IDLE")
        for want in ("Queue: 3 ready", "lab-a [audit, gpt-6-luna / medium]", "2026-10-11 lab-old: SOUND",
                     "2026-10-12 05:47Z lab-a DONE (gpt-6.1-sol / medium, 94k tokens, 452s)", "NEEDS A LOOK: nothing", "Last check by the scheduler: 06:30Z IDLE"):
            self.assertIn(want, t)
        self.assertNotIn("{", t)
        away = R.status_text([], [done], {}, [], None, 1791784000, host_has_lab=False)
        self.assertIn("does not run the lab", away)
        self.assertNotIn("NEEDS A LOOK", away)

    def test_brief_status_drops_the_delivered_block_and_keeps_queue_and_needs_a_look(self):
        done = card("lab-old", state="done", closed="2026-10-11T08:00:00Z", result="SOUND")
        t = R.status_text([card("lab-a"), card("lab-b"), card("lab-c")], [done], {}, [self.ROW | {"outcome": "DONE"}], None, 1791784000, "06:30Z IDLE", brief=True)
        self.assertNotIn("Delivered", t)
        self.assertNotIn("lab-old", t)
        for want in ("Queue: 3 ready", "lab-a [audit, gpt-6-luna / medium]", "NEEDS A LOOK: nothing"):
            self.assertIn(want, t)
        away = R.status_text([], [done], {}, [], None, 1791784000, host_has_lab=False, brief=True)
        self.assertIn("does not run the lab", away)
        self.assertNotIn("deliveries", away)


class LockTest(unittest.TestCase):
    def test_second_run_is_refused_until_the_lock_is_stale(self):
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lab.lock"
            alive = lambda pid: True
            self.assertTrue(R.acquire(lock, now=1000, alive=alive))
            os.utime(lock, (1000, 1000))
            self.assertFalse(R.acquire(lock, now=1000 + R.LOCK_STALE_S - 1, alive=alive))
            self.assertTrue(R.acquire(lock, now=1000 + R.LOCK_STALE_S + 1, alive=alive))

    def test_lock_of_a_dead_run_on_this_host_is_taken_over_at_once(self):
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lab.lock"
            self.assertTrue(R.acquire(lock, now=1000, alive=lambda pid: True))
            os.utime(lock, (1000, 1000))
            self.assertFalse(R.acquire(lock, now=1100, alive=lambda pid: True))
            self.assertTrue(R.acquire(lock, now=1100, alive=lambda pid: False))

    def test_creation_is_exclusive_so_two_starters_cannot_both_win(self):
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lab.lock"
            lock.write_text("not json", encoding="utf-8")   # a lock another process just created, contents not readable yet
            self.assertFalse(R.acquire(lock, alive=lambda pid: True))
            self.assertEqual(lock.read_text(encoding="utf-8"), "not json")


class UsageTest(unittest.TestCase):
    """What a run really cost: the effective model and effort the CLI printed, and tokens + allowance points from its rollout file."""
    HEADER = "OpenAI Codex v0.162.0\n--------\nworkdir: F:\\wt\nmodel: gpt-6-astra\nprovider: openai\nreasoning effort: high\nsession id: 01a1-abc\n--------\nuser\n"

    def rollout(self, home, sid="01a1-abc", pts=((16.0, 45.0, 5000), (97.0, 58.0, 5000))):
        d = Path(home) / "sessions" / "2026" / "10" / "12"
        d.mkdir(parents=True, exist_ok=True)
        rows = []
        for i, (five, week, reset) in enumerate(pts):
            rows.append({"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {
                "input_tokens": 1000 * (i + 1), "cached_input_tokens": 800 * (i + 1), "output_tokens": 50 * (i + 1), "total_tokens": 1050 * (i + 1)}},
                "rate_limits": {"primary": {"used_percent": five, "resets_at": reset}, "secondary": {"used_percent": week, "resets_at": 90000}}}})
        p = d / f"rollout-2026-10-12T22-30-07-{sid}.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
        return p

    def test_header_gives_the_model_effort_and_session_the_cli_really_used(self):
        h = R.log_header(self.HEADER)
        self.assertEqual((h["model"], h["effort"], h["session"]), ("gpt-6-astra", "high", "01a1-abc"))
        self.assertEqual(R.log_header("nothing here"), {})

    def test_rollout_gives_tokens_and_the_points_the_run_moved(self):
        with tempfile.TemporaryDirectory() as d:
            self.rollout(d)
            u = R.rollout_usage(d, "01a1-abc")
            self.assertEqual((u["tokens_total"], u["tokens_cached"], u["tokens_uncached"], u["tokens_out"]), (2100, 1600, 400, 100))
            self.assertEqual((u["window_before"], u["window_after"], u["window_pts"]), (16.0, 97.0, 81.0))
            self.assertEqual(u["week_pts"], 13.0)
            self.assertEqual(R.rollout_usage(d, "missing"), {})
            self.assertEqual(R.rollout_usage(d, ""), {})

    def test_a_window_that_reset_mid_run_counts_what_the_new_window_shows(self):
        with tempfile.TemporaryDirectory() as d:
            self.rollout(d, pts=((99.0, 45.0, 5000), (7.0, 46.0, 23000)))
            self.assertEqual(R.rollout_usage(d, "01a1-abc")["window_pts"], 7.0)

    def test_a_stale_first_reading_with_another_reset_time_is_not_a_reset(self):
        with tempfile.TemporaryDirectory() as d:
            self.rollout(d, pts=((91.0, 14.0, 3000), (99.0, 15.0, 5000)))
            u = R.rollout_usage(d, "01a1-abc")
            self.assertEqual((u["window_pts"], u["week_pts"]), (8.0, 1.0))

    def test_requested_and_effective_setting_mismatch_is_named(self):
        self.assertEqual(R.setting_mismatch(("gpt-6-luna", "medium"), {"model": "gpt-6-luna", "effort": "medium"}), "")
        self.assertEqual(R.setting_mismatch(("gpt-6-luna", "medium"), {}), "")
        m = R.setting_mismatch(("gpt-6-luna", "medium"), {"model": "gpt-6.1-sol", "effort": "low"})
        self.assertIn("asked gpt-6-luna/medium, CLI used gpt-6.1-sol/low", m)


class SpendGuardTest(unittest.TestCase):
    NOW = 100000
    RL = {"primary": {"used_percent": 16.0, "resets_at": 102000}, "secondary": {"used_percent": 20.0, "resets_at": 1000000}}

    def run_row(self, at, model, effort, pts=None, week=None, outcome="DONE", card="x"):
        return {"at": at, "card": card, "model": model, "effort": effort, "outcome": outcome, "window_pts": pts, "week_pts": week}

    def stamp(self, epoch):
        return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_astra_high_does_not_fit_a_window_with_16_percent_used(self):
        why, until = R.budget_hold("gpt-6-astra", "high", self.RL, [], self.NOW)
        self.assertIn("gpt-6-astra/high", why)
        self.assertEqual(until, 102000)
        self.assertEqual(R.budget_hold("gpt-6-luna", "medium", self.RL, [], self.NOW), ("", 0))

    def test_measured_cost_of_a_setting_replaces_the_table(self):
        rows = [self.run_row(self.stamp(1000), "gpt-6-luna", "medium", pts=70.0)]
        self.assertEqual(R.est_pts("gpt-6-luna", "medium", rows)[0], 70.0)
        self.assertEqual(R.est_pts("gpt-6-luna", "medium", [])[0], R.EST_WINDOW_PTS[("gpt-6-luna", "medium")])
        self.assertEqual(R.est_pts("gpt-9", "low", [])[0], R.EST_DEFAULT)
        self.assertIn("gpt-6-luna/medium", R.budget_hold("gpt-6-luna", "medium", self.RL, rows, self.NOW)[0])

    def test_lab_may_not_spend_more_than_its_share_of_one_window(self):
        start = 102000 - R.WINDOW_S
        rows = [self.run_row(self.stamp(start + 60), "gpt-6-luna", "medium", pts=R.LAB_WINDOW_PTS - 3)]
        why, until = R.budget_hold("gpt-6-luna", "medium", self.RL, rows, self.NOW)
        self.assertIn("lab share of this 5-hour window", why)
        self.assertEqual(until, 102000)
        old = [self.run_row(self.stamp(start - 60), "gpt-6-luna", "medium", pts=R.LAB_WINDOW_PTS)]   # spent in the previous window
        self.assertEqual(R.budget_hold("gpt-6-luna", "medium", self.RL, old, self.NOW), ("", 0))

    def test_run_count_and_astra_count_per_window_are_capped(self):
        start = 102000 - R.WINDOW_S
        rows = [self.run_row(self.stamp(start + 60 * i), "gpt-6-luna", "low", pts=0.0) for i in range(1, R.LAB_RUNS_PER_WINDOW + 1)]
        self.assertIn("runs in this window", R.budget_hold("gpt-6-luna", "low", self.RL, rows, self.NOW)[0])
        rl = {**self.RL, "primary": {"used_percent": 0.0, "resets_at": 102000}}
        one = [self.run_row(self.stamp(start + 60), "gpt-6-astra", "medium", pts=1.0)]
        self.assertIn("astra", R.budget_hold("gpt-6-astra", "medium", rl, one, self.NOW)[0])
        self.assertEqual(R.budget_hold("gpt-6-astra", "medium", rl, [], self.NOW), ("", 0))

    def test_weekly_share_of_the_lab(self):
        wk_start = 1000000 - R.WEEK_S
        rows = [self.run_row(self.stamp(wk_start + 60), "gpt-6-luna", "medium", pts=1.0, week=R.LAB_WEEK_PTS - 1)]
        why, until = R.budget_hold("gpt-6-luna", "medium", self.RL, rows, wk_start + 120)
        self.assertIn("week", why)
        self.assertEqual(until, 1000000)

    def test_a_reading_whose_window_already_reset_counts_as_empty(self):
        rl = {"primary": {"used_percent": 99.0, "resets_at": 5000}, "secondary": {"used_percent": 20.0, "resets_at": 1000000}}
        self.assertEqual(R.budget_hold("gpt-6-luna", "medium", rl, [], self.NOW), ("", 0))

    def test_a_stale_reading_does_not_pin_the_window_to_its_old_reset(self):
        # JIS-NUC 2026-10-15: the newest reading's 5-hour reset was 10-14 17:01Z and no run could refresh it, so every run since
        # that reset counted as "this window" (7/4 runs) and the lab sat idle for 14 h. Past a window length, only the last 5 h count.
        stale_end = self.NOW - 3 * R.WINDOW_S
        rl = {"primary": {"used_percent": 47.0, "resets_at": stale_end}, "secondary": {"used_percent": 20.0, "resets_at": 1000000}}
        old = [self.run_row(self.stamp(stale_end + 60 * i), "gpt-6-luna", "medium", pts=0.0) for i in range(1, R.LAB_RUNS_PER_WINDOW + 3)]
        self.assertEqual(R.budget_hold("gpt-6-luna", "medium", rl, old, self.NOW), ("", 0))
        new = [self.run_row(self.stamp(self.NOW - 60 * i), "gpt-6-luna", "medium", pts=0.0) for i in range(1, R.LAB_RUNS_PER_WINDOW + 1)]
        self.assertIn("runs in this window", R.budget_hold("gpt-6-luna", "medium", rl, new, self.NOW)[0])
        recent_end = self.NOW - 600   # reset 10 minutes ago: the new window starts at that reset
        rl["primary"]["resets_at"] = recent_end
        before = [self.run_row(self.stamp(recent_end - 60 * i), "gpt-6-luna", "medium", pts=0.0) for i in range(1, R.LAB_RUNS_PER_WINDOW + 3)]
        self.assertEqual(R.budget_hold("gpt-6-luna", "medium", rl, before, self.NOW), ("", 0))

    def test_no_reading_still_applies_the_lab_caps(self):
        rows = [self.run_row(self.stamp(self.NOW - 60), "gpt-6-luna", "low", pts=0.0) for _ in range(R.LAB_RUNS_PER_WINDOW)]
        self.assertIn("runs in this window", R.budget_hold("gpt-6-luna", "low", None, rows, self.NOW)[0])
        self.assertEqual(R.budget_hold("gpt-6-luna", "low", None, [], self.NOW), ("", 0))

    def test_choose_takes_the_next_card_that_fits_instead_of_idling(self):
        big, small = card("lab-big", crucial=True), card("lab-small")
        rows = [self.run_row(self.stamp(1000), "gpt-6-astra", "low", pts=90.0)]   # measured: astra/low moved the window 90 points
        c, why = R.choose([big, small], set(), {}, rows, self.RL, self.NOW)
        self.assertEqual(c["id"], "lab-small")
        c, why = R.choose([big], set(), {}, rows, self.RL, self.NOW)
        self.assertIsNone(c)
        self.assertIn("lab-big", why)
        self.assertIn("gpt-6-astra/low", why)

    def test_a_card_that_ran_out_mid_run_waits_out_a_cool_down(self):
        rows = [self.run_row(self.stamp(self.NOW - 600), "gpt-6-luna", "medium", outcome="INCOMPLETE", card="lab-a")]
        self.assertTrue(R.cooling(rows, "lab-a", self.NOW))
        self.assertFalse(R.cooling(rows, "lab-b", self.NOW))
        self.assertFalse(R.cooling(rows, "lab-a", self.NOW + R.COOLDOWN_S + 1))
        self.assertFalse(R.cooling([self.run_row(self.stamp(self.NOW - 60), "m", "e", outcome="LIMIT", card="lab-a")], "lab-a", self.NOW))
        c, _ = R.choose([card("lab-a"), card("lab-b")], set(), {}, rows, None, self.NOW)
        self.assertEqual(c["id"], "lab-b")

    def test_min_gap_between_run_starts(self):
        rows = [self.run_row(self.stamp(self.NOW - 60), "gpt-6-luna", "low", pts=0.0)]
        self.assertIn("minutes ago", R.gap_hold(rows, self.NOW))
        self.assertEqual(R.gap_hold(rows, self.NOW + R.MIN_GAP_S), "")
        self.assertEqual(R.gap_hold([], self.NOW), "")


class UsageDocTest(unittest.TestCase):
    def test_usage_doc_is_compact_and_carries_effective_settings(self):
        rows = [{"at": "2026-10-12T17:00:01Z", "card": "lab-a", "kind": "audit", "model": "gpt-6-astra", "effort": "high", "model_used": "gpt-6-astra",
                 "effort_used": "high", "seconds": 777, "tokens": 383362, "tokens_total": 3710850, "window_pts": 81.0, "week_pts": 13.0,
                 "outcome": "INCOMPLETE", "log": "F:/x.log", "note": "n" * 400}] * 14
        rl = {"primary": {"used_percent": 97.0, "resets_at": 1791851629}, "secondary": {"used_percent": 58.0, "resets_at": 1792438429}, "plan_type": "plus"}
        doc = R.usage_doc(rows, rl, 1791846000, "JIS-NUC")
        self.assertEqual(len(doc["runs"]), R.USAGE_RUNS)
        self.assertEqual(doc["runs"][0]["model"], "gpt-6-astra")
        self.assertEqual(doc["runs"][0]["tokens_total"], 3710850)
        self.assertNotIn("log", doc["runs"][0])
        self.assertLessEqual(len(doc["runs"][0]["note"]), 160)
        self.assertEqual(doc["allowance"]["window_used"], 97.0)
        self.assertEqual(doc["caps"]["window_pts"], R.LAB_WINDOW_PTS)
        self.assertEqual(doc["host"], "JIS-NUC")
        json.dumps(doc)


class IndexTest(unittest.TestCase):
    def test_delivered_newest_first_with_report_link_then_queue(self):
        done1 = card("lab-old", state="done", closed="2026-10-11T08:00:00Z", result="SOUND")
        done2 = card("lab-new", kind="run", state="done", closed="2026-10-12T08:00:00Z", result="recall 3/7 | fire 0.4/day")
        text = R.index_text([done1, done2, card("lab-q"), card("son") | {"lane": "SONNET"}],
                            ["2026-10-11_lab-old.md", "2026-10-12_lab-new.md", "2026-10-12_other.md"])
        self.assertLess(text.index("lab-new"), text.index("lab-old"))
        self.assertIn("[2026-10-12_lab-new.md](reports/2026-10-12_lab-new.md)", text)
        self.assertIn("recall 3/7 / fire 0.4/day", text)
        self.assertIn("| ready | lab-q | audit |", text)
        self.assertNotIn("son", text.split("## Queued")[1])
        self.assertEqual(text, R.index_text([done2, card("lab-q"), done1], ["2026-10-12_lab-new.md", "2026-10-11_lab-old.md"]))


class LimitFallback(unittest.TestCase):
    def test_salvage_moves_untracked_and_restores_tracked(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            wt, home = Path(d) / "wt", Path(d) / "home"
            wt.mkdir()
            run = lambda *a: subprocess.run(["git", "-C", str(wt), *a], check=True, capture_output=True)
            run("init", "-q")
            (wt / "tracked.txt").write_text("v1", encoding="utf-8")
            run("add", ".")
            run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "i")
            (wt / "tracked.txt").write_text("v2", encoding="utf-8")
            (wt / "new.png").write_bytes(b"x")
            dest, n = R.salvage(wt, home, "card", datetime(2026, 10, 12, 17, 0, tzinfo=timezone.utc))
            self.assertEqual(n, 2)
            self.assertEqual(R.changed_files(wt), [])
            self.assertEqual((wt / "tracked.txt").read_text(encoding="utf-8"), "v1")
            self.assertEqual((dest / "tracked.txt").read_text(encoding="utf-8"), "v2")
            self.assertTrue((dest / "new.png").is_file())

    def test_salvage_clears_unmerged_and_staged_files(self):
        # JIS-NUC 2026-10-14: a stash-pop conflict left INDEX.md unmerged (no MERGE_HEAD) plus staged new files; every tick
        # then died on `git checkout -- INDEX.md` ("path is unmerged") and the lab stayed idle.
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            wt, home = Path(d) / "wt", Path(d) / "home"
            wt.mkdir()
            run = lambda *a: subprocess.run(["git", "-C", str(wt), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                            capture_output=True)
            run("init", "-q")
            (wt / "INDEX.md").write_text("v1\n", encoding="utf-8")
            run("add", ".")
            run("commit", "-qm", "i")
            (wt / "INDEX.md").write_text("mine\n", encoding="utf-8")
            run("stash", "-q")
            (wt / "INDEX.md").write_text("theirs\n", encoding="utf-8")
            run("commit", "-qam", "t")
            (wt / "staged_new.md").write_text("n\n", encoding="utf-8")
            run("add", "staged_new.md")
            run("stash", "pop")
            self.assertIn("UU INDEX.md", run("status", "--porcelain").stdout.decode())
            dest, n = R.salvage(wt, home, "tick", datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc))
            self.assertEqual(n, 2)
            self.assertEqual(R.changed_files(wt), [])
            self.assertEqual((wt / "INDEX.md").read_text(encoding="utf-8"), "theirs\n")
            self.assertTrue((dest / "staged_new.md").is_file())
            self.assertIn("mine", (dest / "INDEX.md").read_text(encoding="utf-8"))

    def _two_branches(self, d, lab_file, trunk_file):
        import subprocess
        wt = Path(d) / "wt"
        (wt / "MyTradingSys/research/layer_lab").mkdir(parents=True)
        run = lambda *a: subprocess.run(["git", "-C", str(wt), "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True)
        run("init", "-q")
        run("symbolic-ref", "HEAD", "refs/heads/trunk")   # git < 2.28 (JIS-NUC runs 2.24) has no init -b
        run("config", "user.name", "t")   # merge_trunk commits without -c: CI runners may have no global identity
        run("config", "user.email", "t@t")
        for f in {lab_file, trunk_file, R.LAB + "/INDEX.md"}:
            (wt / f).write_text("base\n", encoding="utf-8")
        run("add", ".")
        run("commit", "-qm", "base")
        run("switch", "-q", "-c", "lab")
        (wt / lab_file).write_text("lab\n", encoding="utf-8")
        run("commit", "-qam", "lab")
        run("switch", "-q", "trunk")
        (wt / trunk_file).write_text("trunk\n", encoding="utf-8")
        run("commit", "-qam", "trunk")
        run("switch", "-q", "lab")
        return wt, run

    def test_merge_trunk_resolves_a_generated_index_clash(self):
        # JIS-NUC 2026-10-14 16:00Z: the tick's merge stopped on INDEX.md (generated), left MERGE_HEAD, every later tick failed.
        with tempfile.TemporaryDirectory() as d:
            idx = R.LAB + "/INDEX.md"
            wt, run = self._two_branches(d, idx, idx)
            R.merge_trunk(wt, "trunk")
            self.assertEqual(R.changed_files(wt), [])
            self.assertNotEqual(run("rev-parse", "-q", "--verify", "MERGE_HEAD").returncode, 0)
            self.assertEqual(run("merge-base", "--is-ancestor", "trunk", "HEAD").returncode, 0)

    def test_refresh_survives_a_merge_left_in_progress(self):
        # Supervisor pilot 2026-10-22: `codex_run.py tick` died with "cannot switch branch while merging" (MERGE_HEAD left behind);
        # refresh switched branch before merge_trunk could abort it.
        import socket
        import subprocess
        with tempfile.TemporaryDirectory() as d, unittest.mock.patch.dict("os.environ", {"CODEX_HOME": str(Path(d) / "home")}):
            wt, run = self._two_branches(d, "code.py", "code.py")
            bare = Path(d) / "origin.git"
            subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
            run("remote", "add", "origin", str(bare))
            run("push", "-q", "origin", "trunk:" + R.sync.TRUNK)
            run("switch", "-q", "-c", f"{socket.gethostname().lower()}/codex-lab", "lab")
            self.assertNotEqual(run("merge", "--no-edit", "trunk").returncode, 0)   # real clash: MERGE_HEAD stays
            self.assertEqual(run("rev-parse", "-q", "--verify", "MERGE_HEAD").returncode, 0)
            with self.assertRaises(SystemExit) as e:
                R.refresh(wt)   # the clash itself still needs a session, but the tick must get as far as saying so
            self.assertIn("clashes on code.py", str(e.exception))
            self.assertNotEqual(run("rev-parse", "-q", "--verify", "MERGE_HEAD").returncode, 0)

    def test_merge_trunk_aborts_a_real_clash_and_leaves_the_tree_clean(self):
        with tempfile.TemporaryDirectory() as d:
            wt, run = self._two_branches(d, "code.py", "code.py")
            with self.assertRaises(SystemExit) as e:
                R.merge_trunk(wt, "trunk")
            self.assertIn("code.py", str(e.exception))
            self.assertEqual(R.changed_files(wt), [])
            self.assertNotEqual(run("rev-parse", "-q", "--verify", "MERGE_HEAD").returncode, 0)



class WatchdogTest(unittest.TestCase):
    NOW = 1791784000
    ROW = {"at": "2026-10-12T05:47:00Z", "card": "lab-a", "outcome": "BLOCKED", "seconds": 40, "report": "", "note": ""}

    def test_early_bails_are_free_then_charged(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "lab_runs").mkdir()
            rows = [self.ROW] * 3 + [self.ROW | {"seconds": 900, "note": "gate failed"}]
            (Path(d) / "lab_runs" / "runs.jsonl").write_text(chr(10).join(json.dumps(r) for r in rows), encoding="utf-8")
            self.assertEqual(R.attempts(d), {"lab-a": 2})   # 2 free bails; the 3rd bail and the real failure are charged

    def test_stall_and_bail_streak_and_stale_reading_are_named(self):
        ready = [card("lab-a")]
        old = [self.ROW | {"outcome": "DONE", "seconds": 600, "at": "2026-10-11T00:00:00Z"}]
        text = " | ".join(R.stall_findings(old, ready, {}, True, "", self.NOW, age=3 * 3600))
        for want in ("STALLED", "nothing ran for", "reading is 3.0 h old"):
            self.assertIn(want, text)
        self.assertEqual(R.stall_findings(old, ready, {}, True, "window full", self.NOW), [])   # a hold is not a stall
        self.assertEqual(R.stall_findings(old, ready, {}, True, R.guard_hold("2026-10-16T13:30Z IDLE lab budget: x: 4 lab runs"), self.NOW), [])   # the spend guard is a hold
        rows = [{"card": "x", "at": "2026-10-16T10:30:00Z", "outcome": "BLOCKED"}]
        self.assertEqual(R.reopened([{"id": "x", "reopened": "2026-10-16T14:00:00Z"}], rows), {"x"})
        self.assertEqual(R.reopened([{"id": "x", "reopened": "2026-10-16T09:00:00Z"}, {"id": "y"}], rows), set())
        self.assertEqual(R.guard_hold("2026-10-16T13:30Z DONE card"), "")
        self.assertEqual(R.stall_findings(old, ready, {}, False, "", self.NOW), [])             # lane down is lane_health's job
        bails = [self.ROW | {"card": c, "at": "2026-10-14T00:00:00Z"} for c in ("a", "b", "c")]
        self.assertIn("bailed early 3 runs in a row", " | ".join(R.stall_findings(bails, [], {}, True, "", self.NOW)))
        self.assertIn("STALLED", " | ".join(R.needs_look(ready, {}, old, watch=R.stall_findings(old, ready, {}, True, "", self.NOW))))

class TimeBoxTest(unittest.TestCase):
    """2026-10-15: the tick's `lane_health sweep --ship` ran the quick gate with no time limit; a hung gate held the tick for 30+ minutes
    and no card ran. The sweep is boxed and a timeout must kill the whole process tree (children hold the pipes)."""

    HANG = "import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']); time.sleep(120)"

    def test_boxed_returns_124_for_a_hung_process_tree_and_passes_normal_output(self):
        t0 = time.time()
        r = R.boxed([sys.executable, "-c", self.HANG], Path.cwd(), 3)
        self.assertEqual(r.returncode, 124)
        self.assertIn("TIMEOUT after 3s", r.stderr)
        self.assertLess(time.time() - t0, 60)   # not the 120 s the grandchild sleeps
        ok = R.boxed([sys.executable, "-c", "print('hi')"], Path.cwd(), 30)
        self.assertEqual((ok.returncode, ok.stdout.strip()), (0, "hi"))

    def test_a_hung_sweep_is_cut_off_and_recorded_so_the_tick_can_go_on(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            wt, runs = Path(d) / "wt", Path(d) / "runs"
            (wt / "scripts" / "dev").mkdir(parents=True)
            runs.mkdir()
            (wt / "scripts" / "dev" / "lane_health.py").write_text(self.HANG + chr(10), encoding="utf-8", newline=chr(10))
            old, R.SWEEP_TIMEOUT_S = R.SWEEP_TIMEOUT_S, 3
            try:
                t0 = time.time()
                sw = R.run_sweep(wt, runs, "--apply", "--ship")
            finally:
                R.SWEEP_TIMEOUT_S = old
            self.assertEqual(sw.returncode, 124)
            self.assertLess(time.time() - t0, 60)
            self.assertIn("TIMEOUT", (runs / "last_lane.txt").read_text(encoding="utf-8"))


class ShipHoldTest(unittest.TestCase):
    """lab-ship-failed-poisons-branch: a gate-red SHIP_FAILED commit stays on the lab branch; new runs must stop (no git reset)."""
    GATE_RED = "Step 4c: Pytest tests: FAIL" + chr(10) + "Step 5: Maven tests: SKIP" + chr(10)

    def test_gate_red_ship_writes_hold_and_next_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(R.record_ship_failure(d, "lab-a", self.GATE_RED))
            hold = (Path(d) / "lab.hold").read_text(encoding="utf-8")
            self.assertIn("lab-a", hold)
            self.assertIn("Step 4c", hold)
            out = io.StringIO()
            with unittest.mock.patch.dict(os.environ, {"CODEX_HOME": d}), contextlib.redirect_stdout(out):
                self.assertNotEqual(R.cmd_next(type("A", (), {"dry": False})()), 0)
            self.assertIn("HOLD", out.getvalue())
            self.assertIn("lab-a", R.needs_look([card()], {}, [], lab_hold=R.read_hold(d))[0])

    def test_timeout_ship_writes_no_hold(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(R.record_ship_failure(d, "lab-a", "partial" + chr(10) + "TIMEOUT after 1500s: process tree killed"))
            self.assertFalse((Path(d) / "lab.hold").exists())
            self.assertEqual(R.read_hold(d), "")

    def test_hold_survives_restart_and_clears_by_deleting_the_file(self):
        with tempfile.TemporaryDirectory() as d:
            R.record_ship_failure(d, "lab-a", "no step lines at all")   # unknown step still fails closed
            self.assertIn("step unknown", R.read_hold(d))
            (Path(d) / "lab.hold").unlink()
            self.assertEqual(R.read_hold(d), "")


class AskMutationFlagTest(unittest.TestCase):
    """`codex_run.py ask --kind build` must be able to set the mutation_check that tasks.problems() demands for CODEX build cards."""
    PROBE = "scripts/test_probe.py::test_rejects_dummy"

    def _repo(self, td):
        repo = Path(td)
        (repo / "scripts").mkdir()
        (repo / "scripts" / "test_probe.py").write_text(
            "def test_rejects_dummy():\n    assert out != dummy  # rejects dummy or shuffled output\n", encoding="utf-8")
        return repo

    def _ask(self, repo, *extra):
        argv = ["ask", "Build the thing", "--kind", "build", "--scope", "MyTradingSys/x.py", "--id", "lab-mut", "--tests", "test_x fails first", *extra]
        out = io.StringIO()
        with unittest.mock.patch.object(R, "REPO", repo), contextlib.redirect_stdout(out):
            try:
                R.main(argv)
            except SystemExit as e:
                return str(e.code), out.getvalue()
        return "", out.getvalue()

    def test_make_card_carries_the_mutation_check(self):
        c = R.make_card("Build it", "build", ["a.py"], cid="lab-m", mutation_check=self.PROBE)
        self.assertEqual(c["mutation_check"], self.PROBE)

    def test_ask_build_with_the_flag_writes_a_ready_card(self):
        with tempfile.TemporaryDirectory() as td:
            err, out = self._ask(self._repo(td), "--mutation-check", self.PROBE)
            self.assertEqual(err, "")
            self.assertIn("wrote", out)

    def test_ask_build_without_the_flag_names_it(self):
        with tempfile.TemporaryDirectory() as td:
            err, _ = self._ask(self._repo(td))
            self.assertIn("--mutation-check", err)

    def test_ask_audit_needs_no_flag(self):
        with tempfile.TemporaryDirectory() as td:
            out = io.StringIO()
            with unittest.mock.patch.object(R, "REPO", Path(td)), contextlib.redirect_stdout(out):
                R.main(["ask", "Audit it", "--kind", "audit", "--scope", "MyTradingSys/x.py", "--id", "lab-aud"])
            self.assertIn("wrote", out.getvalue())


if __name__ == "__main__":
    unittest.main()
