"""test_plan.py - offline tests for plan.py (hand-built gathered dicts; numbers computed by hand in the comments)."""
import copy
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan as pl  # noqa: E402
import test_open_levels as tl  # noqa: E402

DAY = dt.date(2026, 11, 13)


def L(price, name, source="session", label=None):
    return {"price": price, "name": name, "source": source, "label": label or "%s %d" % (name, price)}


def gathered(atr15=240.0, price=69207.0, extra=(), drop=()):
    lv = [L(70000, "ANALYST_70000", "analyst", "analyst cluster 70,000 (5 calls)"), L(69571, "EU_HIGH"), L(68516, "EU_LOW"),
          L(68050, "ANALYST_68050", "analyst", "analyst cluster 68,050 (3 calls)")]
    lv = [l for l in lv if l["name"] not in drop] + list(extra)
    return {"day": "2026-11-13", "frozen_utc": "2026-11-13T13:10Z", "price": price, "atr15": atr15, "atr1h": 602.0,
            "levels": sorted(lv, key=lambda l: -l["price"]), "analyst_note": ""}


def by_id(p):
    return {o["id"]: o for o in p["orders"]}


class PlanRules(unittest.TestCase):
    def test_full_plan_numbers(self):
        # ATR 240. A: 69571 + 0.2*240 = 69619 -> 69620. B: 68516 - 48 = 68468 -> 68470. stop = 240 (inside 55..989 bounds).
        # A target: min(480, 70000 - 69620 - 20 = 360) = 360. B target: min(480, 68470 - 68050 - 20 = 400) = 400.
        # C fades 70000 (beyond A target edge 69980): trigger 69980, target 480, arm_after A.
        # D: A.. B target edge 68070; analyst 68050 is beyond: trigger 68070, buy, arm_after B.
        o = by_id(pl.build_plan(gathered(), DAY))
        self.assertEqual((o["A"]["trigger"], o["A"]["stop_dist"], o["A"]["target_dist"], o["A"]["side"]), (69620, 240, 360, "buy"))
        self.assertEqual((o["B"]["trigger"], o["B"]["stop_dist"], o["B"]["target_dist"], o["B"]["side"]), (68470, 240, 400, "sell"))
        self.assertEqual((o["C"]["trigger"], o["C"]["target_dist"], o["C"]["side"], o["C"]["kind"], o["C"]["arm_after"]), (69980, 480, "sell", "fade", "A"))
        self.assertEqual((o["D"]["trigger"], o["D"]["target_dist"], o["D"]["side"], o["D"]["arm_after"]), (68070, 480, "buy", "B"))
        self.assertIn("live_aid:EU_HIGH", o["A"]["confluence"])

    def test_shape_matches_hand_made_plan(self):
        mine = pl.build_plan(gathered(), DAY)
        ref = Path(__file__).resolve().parents[2] / "research" / "us_open_trader_2026-11-13" / "plan_2026-11-13.json"
        if ref.exists():
            ref = json.loads(ref.read_text(encoding="utf-8"))
            self.assertTrue(set(ref) - {"leverage"} <= set(mine))   # V2-5: readers ignore the old leverage key
            self.assertEqual(set(ref["orders"][0]), set(mine["orders"][0]))
            for k in ("arm_utc", "flat_utc", "max_entries", "be_at_r", "fee_per_side", "instrument", "ref_feed"):
                self.assertEqual(ref[k], mine[k])

    def test_stop_floor(self):
        # ATR 20 -> 1*ATR = 20; floor 0.08 % of 69207 = 55.4 -> kept on the 10 grid, rounded up = 60
        o = by_id(pl.build_plan(gathered(atr15=20.0), DAY))
        self.assertEqual(o["A"]["stop_dist"], 60)
        self.assertGreaterEqual(60 / 69207, 0.0008)

    def test_stop_cap(self):
        # ATR 1000 = 1.44 % > cap 1.43 % of 69207 = 989.7 -> 980
        o = by_id(pl.build_plan(gathered(atr15=1000.0, drop=("ANALYST_70000", "ANALYST_68050")), DAY))
        self.assertEqual(o["A"]["stop_dist"], 980)
        self.assertLessEqual(980 / 69207, 0.0143)

    def test_target_capped_by_next_level(self):
        o = by_id(pl.build_plan(gathered(), DAY))
        self.assertEqual(o["A"]["target_dist"], 360)   # not 480: 70000 is 380 away, minus 20
        self.assertLess(o["A"]["target_dist"], 2 * o["A"]["stop_dist"])

    def test_order_skipped_when_target_under_1r(self):
        # a level at 69700: A target = 69700 - 69620 - 20 = -40 < 240 -> A skipped; its fade C is not built; B survives
        p = pl.build_plan(gathered(extra=[L(69700, "PDH", "key")]), DAY)
        o = by_id(p)
        self.assertNotIn("A", o)
        self.assertNotIn("C", o)
        self.assertIn("B", o)
        self.assertTrue(any(s["id"] == "A" and "under" in s["reason"] for s in p["skipped"]))

    def test_no_leverage_in_plan(self):
        p = pl.build_plan(gathered(), DAY)
        self.assertNotIn("leverage", p)
        self.assertEqual(p["risk_usd"], 18)
        with self.assertRaises(TypeError):
            pl.build_plan(gathered(), DAY, leverage=50)
        # the old guard stop/price*leverage is gone: a 1.43 % stop is fine now
        pl.build_plan(gathered(atr15=1000.0), DAY)

    def test_size_from_risk(self):
        # ATR 600 -> stop 600. 18 * 69207 / 600 = 2076.21 -> round down to 10 = 2070 (under the 5000 cap)
        self.assertEqual(pl.build_plan(gathered(atr15=600.0), DAY)["amount_usd"], 2070)
        # risk 30: 30 * 69207 / 600 = 3460.35 -> 3460
        self.assertEqual(pl.build_plan(gathered(atr15=600.0), DAY, risk_usd=30)["amount_usd"], 3460)
        # stop 980: 18 * 69207 / 980 = 1271.1 -> 1270
        self.assertEqual(pl.build_plan(gathered(atr15=1000.0), DAY)["amount_usd"], 1270)

    def test_refused_when_size_rounds_to_zero(self):
        with self.assertRaises(pl.PlanRefused):
            pl.build_plan(gathered(atr15=600.0), DAY, risk_usd=0.05)  # 0.05*69207/600 = 5.8 -> 0

    def test_amount_cap(self):
        # ATR 240: 18 * 69207 / 240 = 5190 > cap 10000 / 2 = 5000
        self.assertEqual(pl.build_plan(gathered(), DAY)["amount_usd"], 5000)
        old = pl.risk_guard.MAX_ACCOUNT_NOTIONAL_USD
        pl.risk_guard.MAX_ACCOUNT_NOTIONAL_USD = 4000
        try:
            self.assertEqual(pl.build_plan(gathered(), DAY)["amount_usd"], 2000)
        finally:
            pl.risk_guard.MAX_ACCOUNT_NOTIONAL_USD = old

    def test_no_level_on_one_side(self):
        p = pl.build_plan(gathered(drop=("EU_LOW",)), DAY)   # no Europe low: B and D absent, no crash
        self.assertEqual(sorted(by_id(p)), ["A", "C"])
        self.assertTrue(any(s["id"] == "B" for s in p["skipped"]))
        p = pl.build_plan(gathered(drop=("EU_HIGH", "EU_LOW")), DAY)
        self.assertEqual(p["orders"], [])

    def test_analyst_feed_unavailable_plan_still_builds_and_says_so(self):
        g = gathered(drop=("ANALYST_70000", "ANALYST_68050"))
        g["analyst_note"] = "analyst feed unavailable (OSError: x); plan uses session and prior-day levels only"
        p = pl.build_plan(g, DAY)
        o = by_id(p)
        self.assertEqual(sorted(o), ["A", "B"])          # no cluster -> no fades, breakouts target 2R
        self.assertEqual(o["A"]["target_dist"], 480)
        self.assertEqual(p["notes"], [g["analyst_note"]])
        self.assertIn("analyst feed unavailable", pl.render_md(p, g))

    def test_render_md_has_tables_and_labels(self):
        g = gathered()
        md = pl.render_md(pl.build_plan(g, DAY), g)
        for s in ("## Levels", "## Orders", "## Rules", "SOURCED", "OURS", "| A | long | breakout | 69,620 |",
                  "notional / account equity"):
            self.assertIn(s, md)
        self.assertNotIn("margin at", md)
        self.assertNotIn("x leverage", md)


class Cli(unittest.TestCase):
    def test_cli_writes_json_and_md(self):
        with tempfile.TemporaryDirectory() as d:
            rc = pl.main(["--day", "2026-11-13", "--out-dir", d, "--now", "2026-11-13T13:10:00Z"],
                         fetch=tl.fake_fetch, analysts=lambda now: [])
            self.assertEqual(rc, 0)
            plan = json.loads((Path(d) / "plan_2026-11-13.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["day"], "2026-11-13")
            self.assertTrue((Path(d) / "PLAN_US_OPEN_2026-11-13.md").exists())
            # ATR15 = 110 -> stop 110, A trigger = 69571 + 22 = 69593 -> 69590
            a = [o for o in plan["orders"] if o["id"] == "A"][0]
            self.assertEqual((a["trigger"], a["stop_dist"]), (69590, 110))
            self.assertIn("## What we already know", (Path(d) / "PLAN_US_OPEN_2026-11-13.md").read_text(encoding="utf-8"))

    def test_cli_refusal_exit_code_and_no_files(self):
        with tempfile.TemporaryDirectory() as d:
            rc = pl.main(["--day", "2026-11-13", "--out-dir", d, "--now", "2026-11-13T13:10:00Z", "--risk-usd", "0.01"],
                         fetch=tl.fake_fetch, analysts=lambda now: [])
            self.assertEqual(rc, 2)
            self.assertEqual(list(Path(d).iterdir()), [])


def _w(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


LEDGER = ("id,given_utc,end_utc,likely,up,down,text,outcome,touched_utc,score,rates\n"
          'S001,2026-11-04T09:00Z,x,DOWN,1,2,"closed one",UP,t,MISS,\n'
          'S008,2026-11-05T09:00Z,x,UP,78000.0,77000.0,"open one, with comma",,,,\n'
          'S025,2026-11-06T09:00Z,x,NONE,1,2,"open two",,,,\n')
BIBLE = ("# Bible\n## 1. The four-year cycle (data: x)\nbody\n## 3. Reading of 2026-11-06 (Lead C): two clocks disagree\n- b\n"
         "## 5. Reading of 2026-11-07 (Lead C): the MA clock\n## 6. Reading of 2026-11-08 (Builder): Monday open, calls vs clocks\n"
         "## 7. Reading of 2026-11-09: cycle low, session volume\n## 8. Open study list\n")
LV = "MyTradingSys/research/eagle_eyes_picture_2026-10-28/scenario_ledger.csv"


class Knowledge(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.root = Path(self._t.name)
        self.rt = self.root / "rt"

    def tearDown(self):
        self._t.cleanup()

    def km(self):
        return pl.knowledge_md(DAY, repo_root=self.root, runtime_dir=self.rt)

    def test_all_missing_gives_lines_not_crash(self):
        md = self.km()
        self.assertIn("## What we already know", md)
        for s in ("BIBLE.md", "scenario_ledger.csv", "us_open_levels_2026-10-30/RESULT.md", "us_open_first3m_2026-11-11/RESULT.md", "2026-11-12"):
            self.assertIn(s, md)
        self.assertEqual(md.count("not found"), 4)   # bible, ledger, two studies
        self.assertIn("no score or readings", md)

    def test_bible_quotes_three_newest_dated_readings_with_file_line(self):
        _w(self.root, "MyTradingSys/research/mts_bible/BIBLE.md", BIBLE)
        md = self.km()
        # dated headings: line 4 (11-06), 6 (11-07), 7 (11-08), 8 (11-09). Newest three = lines 8, 7, 6; the open study list has no date
        self.assertIn("BIBLE.md:8", md)
        self.assertIn("BIBLE.md:7", md)
        self.assertIn("BIBLE.md:6", md)
        self.assertNotIn("BIBLE.md:4", md)
        self.assertNotIn("Open study list", md)

    def test_open_ledger_rows_only(self):
        _w(self.root, LV, LEDGER)
        md = self.km()
        self.assertIn("S008", md)
        self.assertIn("S025", md)
        self.assertNotIn("S001", md)
        self.assertIn("open one, with comma", md)
        self.assertIn("2 open", md)

    def test_ledger_file_not_modified(self):
        _w(self.root, LV, LEDGER)
        p = self.root / LV
        before = (p.read_bytes(), p.stat().st_mtime_ns)
        self.km()
        self.assertEqual(before, (p.read_bytes(), p.stat().st_mtime_ns))

    def test_study_one_line_each(self):
        _w(self.root, "MyTradingSys/research/us_open_levels_2026-10-30/RESULT.md", "# Levels study title\n\nBTCUSDT 1m 2022..2026, descriptive.\n| a |\n")
        _w(self.root, "MyTradingSys/research/us_open_first3m_2026-11-11/RESULT.md", "# First3m title\n\nBTCUSDT 1m 2023, no entries.\n")
        md = self.km()
        self.assertIn("Levels study title", md)
        self.assertIn("descriptive", md)
        self.assertIn("First3m title", md)
        self.assertNotIn("| a |", md)

    def test_yesterday_score_and_readings(self):
        # 2026-11-13 is a Friday: yesterday = Thursday 2026-11-12
        _w(self.rt, "2026-11-12.jsonl", json.dumps({"order_id": "A", "r_net": 1.5, "mode": "replay"}) + "\n" +
           json.dumps({"order_id": "B", "r_net": -1.0, "mode": "replay"}) + "\n" +
           json.dumps({"summary": True, "trades": 2, "mode": "replay"}) + "\n")
        _w(self.rt, "readings_2026-11-12.jsonl", json.dumps({"ts_utc": "2026-11-12T13:00:00Z", "binance_spot": 70000, "levels_touched": ["EU_HIGH"], "gaps": ["liq"]}) + "\n" +
           json.dumps({"ts_utc": "2026-11-12T14:00:00Z", "binance_spot": 70500, "levels_touched": ["EU_HIGH", "PDH"], "gaps": ["liq", "coinglass"]}) + "\n")
        md = self.km()
        self.assertIn("2 trades", md)
        self.assertIn("+0.50", md)          # 1.5 - 1.0, from the trade rows
        self.assertIn("2 readings", md)
        self.assertIn("13:00", md)
        self.assertIn("70,500", md)
        self.assertIn("EU_HIGH", md)
        self.assertIn("PDH", md)

    def test_previous_day_skips_weekend(self):
        self.assertEqual(pl.prev_weekday(dt.date(2026, 11, 16)), dt.date(2026, 11, 13))   # Monday -> Friday
        self.assertEqual(pl.prev_weekday(dt.date(2026, 11, 13)), dt.date(2026, 11, 12))

    def test_corrupt_files_do_not_crash(self):
        _w(self.rt, "2026-11-12.jsonl", "{not json\n")
        _w(self.root, LV, "\x00\x01garbage")
        self.assertIn("## What we already know", self.km())

    def test_render_md_includes_knowledge_when_given(self):
        g = gathered()
        md = pl.render_md(pl.build_plan(g, DAY), g, know="## What we already know\n\nX-MARK\n")
        self.assertIn("X-MARK", md)


if __name__ == "__main__":
    unittest.main()
