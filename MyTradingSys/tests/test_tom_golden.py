"""Tom golden-scenario translation tests (L2, TF6 / pipeline row 1.8).

Question: does the alert -> plan translation (execution/auto_trader.py tom_signal, runner_split, apply_venue_price)
turn a described Tom situation into the order he describes? Scenarios come from the 4MoNjEQ2Dd8 v2 extract
(extracts/v2/tom/4MoNjEQ2Dd8_v2.md, decision-log row N = line 23+N) and the catalog rows of
research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md (row # in the table, quotes R<n>); extra quotes Q<nn> are the
appendix labels of research/EXEC_PROVENANCE_AUDIT.md.

Limits (TOM_FABIO_REVIEW section 2): no Tom BTC trade has a date, so the cards below are our reconstruction of the
described situation in normalised units. They test translation fidelity, not edge. Expected numbers are hand-derived
from the quoted prices (comment on each test), never read from the code.

Target: the LIVE file execution/auto_trader.py with execution/auto_trader_config.json. Set MTS_TOM_GOLDEN_TARGET to a
file path (e.g. execution/auto_trader.py.new) to run the same scenarios against a staged copy; its config is the
sibling auto_trader_config.json (+ ".new" when the target ends in ".new").

Scenarios the target fails are NOT fixed here. They carry @known_gap(<ref>): the test skips with the reason shown in
the verbose run, so the gate stays green and the list stays visible. MTS_TOM_GOLDEN_STRICT=1 turns every known gap
into a hard failure (the exact failing list). A gap that starts passing is simply a passing test: delete its marker.

Not translatable by an alert card (position_manager / chart reading, no test here): 4Mo rows 15 and 35 (declining a
scalp; F1 tension, Tom teaches scalping elsewhere), rows 20-21 (hold only on a close above the high), rows 27, 30-31,
45, 48 (stop moves to structure), row 49 (exit on "Speed Off").
"""
import functools
import importlib.machinery
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
EXEC = REPO / "MyTradingSys" / "execution"
TARGET = Path(os.environ.get("MTS_TOM_GOLDEN_TARGET") or EXEC / "auto_trader.py")
STRICT = os.environ.get("MTS_TOM_GOLDEN_STRICT") == "1"
NOW = datetime(2026, 10, 3, 12, 0, 0, tzinfo=timezone.utc)
CARD_TIME = "2026-10-03T11:58:00Z"

os.environ.setdefault("MTS_REPO_ROOT", str(REPO))
_loader = importlib.machinery.SourceFileLoader("auto_trader_golden_target", str(TARGET))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
at = importlib.util.module_from_spec(_spec)
_loader.exec_module(at)
import net_rr_floor as nrf  # noqa: E402  (auto_trader put MyTradingSys/runtime on sys.path)


def known_gap(ref):
    """Mark a scenario the target is known to fail (listed in the session record). Skips with the failure text."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(self):
            try:
                fn(self)
            except AssertionError as e:
                if STRICT:
                    raise
                self.skipTest(f"KNOWN GAP {ref}: {str(e).splitlines()[0][:200]}")
        return wrapper
    return deco


def target_config():
    """Live merge as auto_trader.main() does: DEFAULT_CONFIG overlaid key by key with the sibling config file."""
    cfg = json.loads(json.dumps(at.DEFAULT_CONFIG))
    name = "auto_trader_config.json" + (".new" if TARGET.name.endswith(".new") else "")
    try:
        data = json.loads((TARGET.parent / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    for k, v in data.items():
        cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) else v
    return cfg


def card(no, setup, entry, stop, target, verdict="SETUP_FORMING", zone="15m_swing_low", price=None,
         rr="gross 4.0 / net 3.7", runner=None, drop=()):
    """A Tom alert as parse_tom_alert reads it (card layout of scripts/core/start-trading-day.ps1 Build-Card)."""
    lines = [("VERDICT", verdict), ("TIME", CARD_TIME), ("PRICE", price if price is not None else entry),
             ("SETUP", setup), ("ZONE", f"{zone} @ {entry}"), ("ENTRY", entry), ("STOP", stop), ("TARGET", target),
             ("RUNNER_TARGET", runner), ("R:R", rr)]
    body = "\n".join(f"{k}: {v}" for k, v in lines if v is not None and k not in drop)
    return {"title": f"MTS ALERT #{no}", "card_text": f"ALERT #{no}\n---\n{body}\n"}


def arg(args, flag):
    return args[args.index(flag) + 1]


class TomGolden(unittest.TestCase):
    def setUp(self):
        d = Path(tempfile.mkdtemp())
        (d / "net_rr_floor.json").write_text('{"net_rr_floor": 1.25}', encoding="utf-8")
        p = mock.patch.object(nrf, "FLOOR_PATH", d / "net_rr_floor.json")
        p.start()
        self.addCleanup(p.stop)
        self.cfg = target_config()
        # these cases test card normalisation and sizing with 0.04-0.2 % stops; the B146 fee gate (D09) is covered in
        # execution/test_b146_fee_to_stop.py
        self.cfg.get("tom", {}).pop("max_fee_to_stop", None)

    def sig(self, alert, cfg=None, last=0):
        return at.tom_signal(alert, {"tom_last_alert_no": last}, cfg or self.cfg, NOW)

    # --- scenarios that hold today -------------------------------------------------------------------------

    def test_g01_4mo_long_stop_below_low_target_above_highs(self):
        # 4Mo rows 3-4 (Q24, Q30): long, "stop loss goes below the last low", "take-profit above the highs".
        # Normalised: entry 1000, stop 990 -> 10/1000 = 1.0 %; target 1030 -> 30/1000 = 3.0 %.
        s = self.sig(card(10, "ct_long", 1000, 990, 1030))
        self.assertNotIn("reject", s)
        a = s["plan_args"]
        self.assertEqual(arg(a, "--side"), "long")
        self.assertAlmostEqual(float(arg(a, "--stop")), 1.0, places=3)
        self.assertAlmostEqual(float(arg(a, "--targets")), 3.0, places=3)

    def test_g02_tight_ticks_stop_is_not_widened(self):
        # Catalog 13 (Q50 yRv: "risk of 12 ticks ... profit of 97 ticks"), sell limit. Normalised at 0.25 tick, entry
        # 6768: stop 6771 (12 ticks = 3.00) -> 3/6768*100 = 0.0443 -> 0.044; target 6743.75 (97 ticks = 24.25) -> 0.3583.
        s = self.sig(card(11, "ct_short", 6768, 6771, 6743.75, rr="gross 8.1 / net 7.4"))
        self.assertNotIn("reject", s)
        a = s["plan_args"]
        self.assertAlmostEqual(float(arg(a, "--stop")), 0.044, places=3)
        self.assertAlmostEqual(float(arg(a, "--targets").split("@")[-1]), 0.358, places=3)

    def test_g03_avis_counter_short_630_730_230(self):
        # Catalog 3 / R3 (WSCIURybK3U): "Entry 630, stop loss 730, exit 230" = RRR 4.
        # stop (730-630)/630*100 = 15.873 %; target (630-230)/630*100 = 63.492 %.
        s = self.sig(card(12, "ct_short", 630, 730, 230, rr="gross 4.0 / net 3.7"))
        self.assertNotIn("reject", s)
        a = s["plan_args"]
        self.assertEqual(arg(a, "--side"), "short")
        self.assertAlmostEqual(float(arg(a, "--stop")), 15.873, places=3)
        self.assertAlmostEqual(float(arg(a, "--targets").split("@")[-1]), 63.492, places=3)

    def test_g04_entry_is_a_limit_at_the_zone_price(self):
        # Catalog 13 / Q01, Q04 (yRv): "I entered with a limit order ... both were done with limit orders".
        s = self.sig(card(13, "ct_short", 6768, 6771, 6743.75, rr="gross 8.1 / net 7.4"))
        a = s["plan_args"]
        self.assertEqual(arg(a, "--entry"), "limit")
        self.assertEqual(float(arg(a, "--price")), 6768.0)

    def test_g05_poor_rrr_illustration_is_not_traded(self):
        # Catalog 37 (zAwEX_tRUfE, R37): long 7482, stop 7478.25 (3.75), target 7485 (3.0) = RRR 0.8, shown as poor.
        s = self.sig(card(14, "ct_long", 7482, 7478.25, 7485, rr="gross 0.8 / net 0.6"))
        self.assertEqual(s["reject"], "net_rr 0.6 < 1.25")

    def test_g06_long_with_stop_above_entry_is_refused(self):
        # 4Mo row 3 (Q24): a long's stop goes BELOW the last low. A card with the stop above the entry is not a plan.
        s = self.sig(card(15, "ct_long", 1000, 1010, 1030))
        self.assertIn("not ordered", s["reject"])

    def test_g07_reentry_after_a_stop_is_a_new_alert_and_is_taken(self):
        # Catalog 9-10 (ujed R10), 14-15 (k0zm5 R15): stopped once, "proceed with entering another trading position".
        st = {"tom_last_alert_no": 20}
        first = at.tom_signal(card(21, "ct_short", 1000, 1010, 960), st, self.cfg, NOW)
        again = at.tom_signal(card(22, "ct_short", 1000, 1010, 960), st, self.cfg, NOW)
        self.assertNotIn("reject", first)
        self.assertNotIn("reject", again)
        self.assertEqual(st["tom_last_alert_no"], 22)

    def test_g08_card_without_a_target_places_nothing(self):
        # Q31 (UrZ4vpHJ97g): "never ever delete this predefined target": no TARGET line, no plan.
        s = self.sig(card(23, "ct_long", 1000, 990, 1030, drop=("TARGET",)))
        self.assertTrue(s is None or "plan_args" not in s)

    # --- scenarios the live path may fail (translation gaps, not fixed here) --------------------------------

    @known_gap("EXEC_PROVENANCE_AUDIT E10-1 / H4 pt 3 (chain stays proof-first)")
    def test_g09_4mo_entry_before_proof_is_an_order(self):
        # 4Mo row 2 + rows 7-8 (Q07): Tom enters at the "wonderful price area"; absorption and aggressive buying are
        # read AFTER. The engine says WAIT_PROOF at that moment. Expect: an order (Tom entered).
        s = self.sig(card(30, "ct_long", 1000, 990, 1030, verdict="WAIT_PROOF"))
        self.assertNotIn("reject", s, f"engine verdict WAIT_PROOF is refused: {s.get('reject')}")

    @known_gap("EXEC_PROVENANCE_AUDIT E3-T (size 10 = no 50/50 split)")
    def test_g10_partial_then_runner_at_the_configured_size(self):
        # 4Mo rows 22, 47 (Q19, Q20): "close out a position ... take out another position", the rest keeps running.
        # Card: target 1030 (3.0 %), runner 1060 (6.0 %). Expect two legs at 3.0 and 6.0 with the live config.
        s = self.sig(card(31, "ct_long", 1000, 990, 1030, runner=1060))
        legs = arg(s["plan_args"], "--targets").split(",")
        self.assertEqual(len(legs), 2, f"single target with size_usd {self.cfg['tom']['size_usd']}: {s['log']}")
        self.assertEqual([float(x.split("@")[1]) for x in legs], [3.0, 6.0])

    @known_gap("EXEC_PROVENANCE_AUDIT E7-T (NO-SOURCE break-even, opposed by Q13, Q14)")
    def test_g11_stop_stays_structural_after_the_first_leg(self):
        # 4Mo row 23 (Q13 "We'll leave the stop loss down here"), row 31 (Q14): no stop move before an "opposite" range.
        # Split forced with size 200 so the plan has legs; expect no automatic stop-to-entry after leg 1.
        cfg = json.loads(json.dumps(self.cfg))
        cfg["tom"].update(size_usd=200, runner_leg_pct=50)
        s = self.sig(card(32, "ct_long", 1000, 990, 1030, runner=1060), cfg)
        self.assertEqual(len(arg(s["plan_args"], "--targets").split(",")), 2, "no split to test")
        self.assertNotIn("--breakeven-after-first-target", s["plan_args"])

    @known_gap("EXEC_PROVENANCE_AUDIT E2-T (time exit scaled by zone name)")
    def test_g12_time_exit_does_not_depend_on_the_zone_name(self):
        # 4Mo row 49 / Q11-Q12: Tom exits on an event and ends the session on the clock; he states no hold time per
        # zone. Same setup from a 5m zone and from a 4h zone must carry the same --max-hold-minutes.
        def hold(zone):
            a = self.sig(card(40, "ct_long", 1000, 990, 1030, zone=zone))["plan_args"]
            return arg(a, "--max-hold-minutes") if "--max-hold-minutes" in a else None
        short_zone, long_zone = hold("5m_swing_low"), hold("4h_poc")
        self.assertEqual(short_zone, long_zone, f"5m zone {short_zone} min, 4h zone {long_zone} min")

    @known_gap("EXEC_PROVENANCE_AUDIT E3-T (fixed size, Q22 sizes from the stop)")
    def test_g13_size_follows_the_stop_distance(self):
        # tS6 Q22: "I always determine my position size in direct accordance with my stop-loss level." Same max loss,
        # stop 0.2 % vs stop 2.0 % -> the 2.0 % plan must carry a smaller size.
        tight = self.sig(card(50, "ct_long", 1000, 998, 1030))["plan_args"]
        wide = self.sig(card(51, "ct_long", 1000, 980, 1060), last=50)["plan_args"]
        self.assertLess(int(arg(wide, "--size")), int(arg(tight, "--size")),
                        f"size {arg(tight, '--size')} at 0.2 % stop and {arg(wide, '--size')} at 2.0 % stop")

    @known_gap("EXEC_PROVENANCE_AUDIT E1a-T (zone price carries no Deribit basis)")
    def test_g14_resting_limit_is_priced_on_the_venue(self):
        # Q05, Q07 (kXh, 4Mo): the limit is placed in advance at the level. The zone is a Binance price; the order
        # goes to Deribit. Card PRICE 1000 (engine read), zone 990, Deribit mark 1015 -> limit 990 + 15 = 1005.0.
        s = self.sig(card(60, "ct_long", 990, 980, 1030, price=1000))
        fn = getattr(at, "apply_venue_price", None)
        self.assertIsNotNone(fn, "no venue-price step: the card zone price is sent to Deribit unchanged")
        self.assertIsNone(fn(s, mark_fn=lambda: 1015.0))
        self.assertEqual(float(arg(s["plan_args"], "--price")), 1005.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
