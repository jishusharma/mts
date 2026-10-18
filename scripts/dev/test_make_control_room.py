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


class RegistryMergeTest(unittest.TestCase):
    def test_rows_only_in_data_checkout_are_added_own_rows_win(self):
        with tempfile.TemporaryDirectory() as d:
            own = next(iter(cr.mg.load_rows()))
            write(Path(d) / "MyTradingSys/research/BUGS.md",
                  "\n".join([f"| {own['id']} | 2026-01-01 | CLOSED | LOW | stale copy | x | r |",
                             "| B999 | 2026-10-09 | OPEN | HIGH | only in live | x | |", ""]))
            cfg = json.loads(cr.CFG.read_text(encoding="utf-8"))
            data = cr.build(cfg, Path(d), NOW)
        self.assertEqual(data["reg"]["B999"]["status"], "OPEN")
        self.assertEqual(data["reg"][own["id"]]["status"], own["status"])
        self.assertNotEqual(cr.mg.BUGS, Path(d) / "MyTradingSys/research/BUGS.md")


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

    def test_finding_closed_in_config_overrides_findings_file(self):
        d = Path(tempfile.mkdtemp())
        f = d / "MyTradingSys/research/bigtrade_2026-10-09"
        f.mkdir(parents=True)
        (f / "FINDINGS.md").write_bytes(b"## F-BT-09  buildVp weights  [HIGH]  status: AUDITED, ESCALATED" + bytes([10]))
        cfg = dict(self.cfg, finding_closed={"F-BT-09": "fixed in 39520d4, deployed 2026-10-09"})
        before = cr.build(dict(self.cfg, finding_closed={}), d, NOW)["reg"]["F-BT-09"]["status"]
        after = cr.build(cfg, d, NOW)["reg"]["F-BT-09"]["status"]
        self.assertEqual((before, after), ("ESCALATED", "CLOSED"))


class LayerBoardTest(unittest.TestCase):
    """B177 (operator inbox 0c3c2rw1dc5hz27ph4ro): one Layer Board row per layer in active work."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_layer_board_one_row_per_active_layer(self):
        cfg = json.loads(cr.CFG.read_text(encoding="utf-8"))
        lay = lambda i, name, stage, rows: {"id": i, "name": name, "stage": stage, "indicators": "not recorded",
                                            "setups": "not recorded", "rows": rows, "next": "n", "src": "f.md"}
        cfg["layers"] = [lay("la", "Layer Alpha", "encode", ["B991", "B992"]), lay("lb", "Layer Beta", "spec", []),
                         lay("lc", "Layer Parked", "parked", ["B991"])]
        d = Path(tempfile.mkdtemp())
        write(d / "MyTradingSys/research/BUGS.md",
              "## BUGS\n\n| ID | Opened | Status | Severity | Title | Evidence | Receipt |\n|---|---|---|---|---|---|---|\n"
              "| B991 | 2026-10-01 | OPEN | HIGH | alpha open row | e | r |\n"
              "| B992 | 2026-10-01 | CLOSED | MED | alpha closed row | e | r |\n")
        data = cr.build(cfg, d, NOW)
        self.assertEqual([x["id"] for x in data["layers"]], ["la", "lb"])  # parked is left out
        self.assertEqual((data["layers"][0]["open_rows"], data["layers"][0]["worst"]), (1, "HIGH"))
        self.assertEqual((data["layers"][1]["open_rows"], data["layers"][1]["worst"]), (0, ""))
        html = cr.render(data, self.tpl)
        self.assertIn("Layer Alpha", html)
        self.assertIn("Layer Beta", html)
        self.assertIn('id="layer-sec"', self.tpl)

    def test_real_layers_carry_a_source_and_known_rows(self):
        cfg = json.loads(cr.CFG.read_text(encoding="utf-8"))
        self.assertTrue(cfg["layers"])
        reg = cr.build(cfg, Path(tempfile.gettempdir()) / "no_such_data_root", NOW)["reg"]
        for x in cfg["layers"]:
            self.assertTrue(x["src"] and (cr.REPO / x["src"].split(":")[0]).exists(), x["id"])
            self.assertIn(x["stage"], ("spec", "encode", "backtest", "live-testnet", "parked"), x["id"])
            for r in x["rows"]:
                self.assertIn(r, reg, f"{x['id']}: {r} is not a registry row")


class DeclutterTemplateTest(unittest.TestCase):
    """Operator inbox 2sn0idxj5o0uyfm52zca 2026-10-10: 'Declutter MTS control room'."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_reference_sections_start_collapsed(self):
        for sec in ("evid-sec", "ledger-sec", "board-sec"):
            self.assertIn('<details class="fold" id="%s">' % sec, self.tpl)  # no `open`: collapsed by default

    def test_only_decisions_waiting_on_the_operator_are_cards(self):
        self.assertIn("const needs = snap.docs.filter(d => !d.data().applied)", self.tpl)
        self.assertIn("applied decision", self.tpl)

    def test_long_inbox_text_folds_but_stays_verbatim(self):
        self.assertIn("(x.text||\"\").length > 320", self.tpl)
        self.assertEqual(self.tpl.count("${esc(x.text)}"), 2)  # clipped summary uses slice; full text rendered once per branch


class LayersPageLinkTest(unittest.TestCase):
    """The Control Room links to the MTS Layers page; it no longer carries a second layer table."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_control_room_links_layers_page(self):
        self.assertNotIn('id="layers"', self.tpl)
        self.assertIn("https://claude.ai/artifact/7eeXJJ9Sb44LaJeCu8jxfJ", self.tpl)  # MTS Layers, registry single_owner
        self.assertIn("MTS Layers", self.tpl)


class InboxItemWithoutRefTest(unittest.TestCase):
    """B181: an Inbox item with no ref (or no reply) still shows status + reply + ref, never nothing."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_inbox_item_without_ref_shows_status_and_reply(self):
        self.assertIn("received, no registry row yet", self.tpl)
        self.assertIn("no reply yet", self.tpl)
        # the reply box is rendered unconditionally, not only when reply or ref exist
        self.assertNotIn("${x.reply||res?`<div class=\"reply\">", self.tpl)
        self.assertNotIn("x.reply||res?", self.tpl)


class BacklogSectionTest(unittest.TestCase):
    """Backlog section (2026-10-10): cards come from tasks.py, the page only writes taskops docs; nothing is edited in the page."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_build_carries_the_backlog_summary(self):
        data = cr.build(json.loads(cr.CFG.read_text(encoding="utf-8")), cr.REPO, NOW)
        self.assertEqual(set(data["backlog"]), {"counts", "line", "rows"})
        self.assertTrue(data["backlog"]["line"].startswith(("REFINE_OK", "REFINE_NEEDED")))

    def test_page_writes_only_taskops_and_never_a_card(self):
        self.assertIn('id="bl-sec"', self.tpl)
        self.assertIn('db.collection("taskops")', self.tpl)
        self.assertIn('blDb.collection("taskops").add(', self.tpl)
        self.assertNotIn('collection("tasks")', self.tpl)   # cards live in the repo; the page is a view plus requests


class SessionsSectionTest(unittest.TestCase):
    """Sessions section (2026-10-13): the operator sees what each session shipped without opening a chat or a terminal."""
    tpl = (Path(__file__).resolve().parent / "control_room.tpl.html").read_text(encoding="utf-8")

    def test_build_carries_the_session_log(self):
        data = cr.build(json.loads(cr.CFG.read_text(encoding="utf-8")), cr.REPO, NOW)
        self.assertEqual(set(data["sessions"]), {"hours", "stats", "units", "shipped"})
        self.assertEqual(set(data["sessions"]["stats"]),
                         {"sessions", "closed", "open", "empty", "median_min", "commits", "bookkeeping", "no_result"})

    def test_page_shows_sessions_and_hides_when_absent(self):
        self.assertIn('id="sess-sec"', self.tpl)
        self.assertIn("const S = D.sessions; if(!S)", self.tpl)
        self.assertIn("Ended, nothing shipped", self.tpl)


if __name__ == "__main__":
    unittest.main()
