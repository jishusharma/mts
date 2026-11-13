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
import test_levels as tl  # noqa: E402

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
            self.assertTrue(set(ref) <= set(mine))
            self.assertEqual(set(ref["orders"][0]), set(mine["orders"][0]))
            for k in ("arm_utc", "flat_utc", "max_entries", "be_at_r", "fee_per_side", "leverage", "instrument", "ref_feed"):
                self.assertEqual(ref[k], mine[k])

    def test_stop_floor(self):
        # ATR 20 -> 1*ATR = 20; floor 0.08 % of 69207 = 55.4 -> kept on the 10 grid, rounded up = 60
        o = by_id(pl.build_plan(gathered(atr15=20.0), DAY))
        self.assertEqual(o["A"]["stop_dist"], 60)
        self.assertGreaterEqual(60 / 69207, 0.0008)

    def test_stop_cap(self):
        # ATR 1000 = 1.44 % > cap 1.43 % of 69207 = 989.7 -> 980; leverage 30 keeps 980/69207*30 = 0.42 < 0.5
        o = by_id(pl.build_plan(gathered(atr15=1000.0, drop=("ANALYST_70000", "ANALYST_68050")), DAY, leverage=30))
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

    def test_refused_when_stop_too_close_to_liquidation(self):
        # stop 240 / 69207 * 150 = 0.52 >= 0.5
        with self.assertRaises(pl.PlanRefused):
            pl.build_plan(gathered(), DAY, leverage=150)
        pl.build_plan(gathered(), DAY, leverage=100)   # 0.35 is fine

    def test_amount_cap(self):
        self.assertEqual(pl.build_plan(gathered(), DAY)["amount_usd"], 5000)   # min(5000, 10000/2)
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
        for s in ("## Levels", "## Orders", "## Rules", "SOURCED", "OURS", "| A | long | breakout | 69,620 |"):
            self.assertIn(s, md)


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

    def test_cli_refusal_exit_code_and_no_files(self):
        with tempfile.TemporaryDirectory() as d:
            rc = pl.main(["--day", "2026-11-13", "--out-dir", d, "--now", "2026-11-13T13:10:00Z", "--leverage", "400"],
                         fetch=tl.fake_fetch, analysts=lambda now: [])
            self.assertEqual(rc, 2)
            self.assertEqual(list(Path(d).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
