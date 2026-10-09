"""make_control_room.py: ledger totals and halt window, finding status mapping, health thresholds, the screenshot line,
script-safe embedding, and the real control_room.json being consistent with itself."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_control_room as cr

NOW = datetime(2026, 10, 9, 6, 0, tzinfo=timezone.utc)


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


class LabelAndStatusTest(unittest.TestCase):
    def test_source_label(self):
        self.assertEqual(cr.source_label("layer:rsi:rsi_events:5m"), "rsi_events 5m")
        self.assertEqual(cr.source_label("layer:turn_of_candle:turn_of_candle:1m"), "turn_of_candle 1m")
        self.assertEqual(cr.source_label("tom"), "tom")

    def test_finding_status(self):
        self.assertEqual(cr.finding_status("AUDITED, ESCALATED (operator decision)"), "ESCALATED")
        self.assertEqual(cr.finding_status("FIXED"), "CLOSED")
        self.assertEqual(cr.finding_status("NOT-A-DEFECT"), "CLOSED")
        self.assertEqual(cr.finding_status("FIXED for backtests 2026-10-09 (spot ...)"), "CLOSED")
        self.assertEqual(cr.finding_status("AUDITED"), "AUDITED")
        self.assertEqual(cr.finding_status("REPORTED"), "REPORTED")

    def test_findings_parse_and_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "F.md"
            write(p, "## F-BT-01  Stops collapsed   [HIGH]  status: AUDITED, ESCALATED (x)\nbody\n"
                     "## F-BT-05  Flat bars   [MEDIUM]  status: FIXED\n")
            f = cr.load_findings(p)
            self.assertEqual(f["F-BT-01"]["status"], "ESCALATED")
            self.assertEqual(f["F-BT-05"]["sev"], "MED")
            self.assertEqual(f["F-BT-05"]["status"], "CLOSED")
            self.assertEqual(cr.load_findings(Path(d) / "absent.md"), {})


class LedgerTest(unittest.TestCase):
    def test_totals_by_source_day_and_halt_window(self):
        rows = [
            {"ts": "2026-09-20T00:00:00Z", "event": "skipped_halt"},  # older than 7 days: not counted
            {"ts": "2026-10-08T01:00:00Z", "event": "trade_attempt", "plan_id": "P1", "source": "layer:rsi:rsi_events:1h"},
            {"ts": "2026-10-08T02:00:00Z", "event": "ledger_row", "plan_id": "P1", "net_pnl_usd": 2.5, "exit_reason": "target"},
            {"ts": "2026-10-08T03:00:00Z", "event": "trade_attempt", "plan_id": "P2", "source": "layer:rsi:rsi_events:1h"},
            {"ts": "2026-10-09T01:00:00Z", "event": "ledger_row", "plan_id": "P2", "net_pnl_usd": -1.0, "exit_reason": "time_exit"},
            {"ts": "2026-10-09T02:00:00Z", "event": "ledger_row", "plan_id": "P9", "net_pnl_usd": None},  # unresolved: skipped
            {"ts": "2026-10-09T03:00:00Z", "event": "skipped_halt"},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "l.jsonl"
            write(p, "\n".join(json.dumps(r) for r in rows) + "\n\n")
            led, days, span, halts = cr.load_ledger(p, NOW)
        self.assertEqual(led, [{"src": "rsi_events 1h", "n": 2, "w": 1, "net": 1.5, "time": 1}])
        self.assertEqual(days, [{"d": "2026-10-08", "net": 2.5}, {"d": "2026-10-09", "net": -1.0}])
        self.assertEqual(span, ["2026-09-20T00:00:00Z", "2026-10-09T03:00:00Z"])
        self.assertEqual(halts, 1)

    def test_missing_ledger_is_empty_not_a_crash(self):
        self.assertEqual(cr.load_ledger(Path("no/such/file.jsonl"), NOW), ([], [], [None, None], 0))


class HealthTest(unittest.TestCase):
    SHOTS = "SHOTS landed 22: new 0, classified 13, read 0, done 9 | overdue(>24h) 13 | claims ..."

    def test_stack_age_thresholds(self):
        st = lambda last: cr.health({}, last, 0, "", NOW)[0]["s"]
        self.assertEqual(st("2026-10-09T05:00:00Z"), "ok")     # 1 h
        self.assertEqual(st("2026-10-09T00:00:00Z"), "warn")   # 6 h
        self.assertEqual(st("2026-10-08T12:00:00Z"), "bad")    # 18 h
        self.assertEqual(cr.health({}, None, 0, "", NOW)[0]["v"], "No ledger")

    def test_halts_and_screenshots_and_notes(self):
        h = cr.health({"health_notes": [{"k": "Hardware", "v": "x", "s": "bad", "d": ""}]}, "2026-10-09T05:00:00Z", 987, self.SHOTS, NOW)
        by = {x["k"]: x for x in h}
        self.assertEqual(by["Daily-loss halt"]["s"], "warn")
        self.assertEqual(by["Screenshots"]["v"], "13 open")
        self.assertEqual(by["Screenshots"]["s"], "bad")
        self.assertIn("Hardware", by)

    def test_no_shots_line_means_no_tile(self):
        self.assertNotIn("Screenshots", [x["k"] for x in cr.health({}, None, 0, "nothing here", NOW)])


class RenderTest(unittest.TestCase):
    def test_script_close_tag_cannot_break_out(self):
        out = cr.render({"t": "</script><b>"}, "<script>const D = /*__DATA__*/null;</script>")
        self.assertNotIn("</script><b>", out)
        self.assertEqual(out.count("</script>"), 1)

    def test_template_without_slot_fails(self):
        with self.assertRaises(SystemExit):
            cr.render({}, "<p>no slot</p>")

    def test_real_template_has_slot(self):
        self.assertIn("/*__DATA__*/null", cr.TPL.read_text(encoding="utf-8"))


class RealConfigTest(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(cr.CFG.read_text(encoding="utf-8"))

    def test_stages_unique_and_complete(self):
        ids = [s["id"] for s in self.cfg["road"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in self.cfg["road"]:
            self.assertTrue(s["name"] and s["goal"] and s["exit"] and s["items"], s["id"])

    def test_every_item_in_one_stage_and_every_x_task_used(self):
        seen = [i for s in self.cfg["road"] for i in s["items"]]
        self.assertEqual(len(seen), len(set(seen)), "an item sits in two stages")
        for k in self.cfg["x_tasks"]:
            self.assertIn(k, seen, f"{k} defined but in no stage")

    def test_build_on_this_checkout_resolves_registry_and_x_ids(self):
        data = cr.build(self.cfg, Path(tempfile.gettempdir()) / "no_such_data_root", NOW)
        # with no findings file only F-BT ids may be unresolved; every B/T/X id must exist
        self.assertEqual([m for m in data["missing"] if not m.startswith("F-BT-")], [])
        self.assertTrue(data["verdict"])
        # the inbox resolution lookup carries closed rows too, not just the open board
        closed = [k for k, v in data["reg"].items() if v["status"] == "CLOSED"]
        self.assertTrue(closed, "reg must include closed registry rows")
        self.assertTrue(all(k not in {b["id"] for b in data["board"]} or k in {i for s in self.cfg["road"] for i in s["items"]} for k in closed))


if __name__ == "__main__":
    unittest.main()
