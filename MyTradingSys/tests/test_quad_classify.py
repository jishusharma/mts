"""test_quad_classify.py - offline tests for runtime/quad_classify.py (price x CVD x OI quadrant classifier).

Staged as .new 2026-10-02 (TWO_CORES_FIX_PASS_2026-10-02.md item 4). Promoted 2026-10-04 (T037) to MyTradingSys/tests/test_quad_classify.py (collected by run_all_tests step 4).
Run directly:  python MyTradingSys/tests/test_quad_classify.py

Expected values come from DOCUMENTS, never from the code under test:
  [Q1] MyTradingSys/archive/mts_historical/SESSION_CLOSE_2026-09-20-0541Z.md:74-80, "6-STATE MOMENTUM (canonical)":
         L75 Price up + OI up + CVD up = trend up.            L78 Price down + OI up + CVD down = trend down.
         L76 Price up + OI down + CVD up = short squeeze.     L79 Price down + OI down + CVD down = long liquidation.
         L77 Price up + OI up + CVD down = distribution.      L80 Price down + OI up + CVD up = accumulation.
  [Q2] Label names for those sign tuples: quad_classify.py docstring (header, lines 6-9 and 12-13): trend up = new_longs,
       short squeeze = short_cover, trend down = new_shorts; distribution / long_liquidation / accumulation keep their names.
       The sign tuples in [Q1] and in the docstring agree on all six rows; [Q2] is only the label-name mapping.
  [Q3] Price x OI readings (T3 practitioner convention): research/_archive/loose_2026-10/INDICATOR_IMPLEMENTATION_HANDOFF.md:44-47
       (rising OI + rising price = new longs; rising OI + falling price = new shorts; falling OI + rising price = short
       covering; falling OI + falling price = long liquidation); research/_archive/loose_2026-10/DIVERGENCE_AUDIT_AND_RESEARCH.md:53.
  [Q4] "flat" is one of the nine labels (research/_archive/loose_2026-10/AUDIT_2026-09-17_TRACKER.md:331). [Q1] has only price-up / price-down
       rows, so an unchanged price matches no row.
  [Q5] "nearest ~1h-ago snapshot": quad_classify.py docstring line 2; the quad window is 1 h: research/
       visual_validation_protocol_vvp002.md:160 ("quad's 1h window").
  [Q6] Snapshot field paths used as inputs: cvd.cvd_recent.delta_1h (market_data/data_schema_v1.2.0.md:397-405),
       trade_flow.net_delta_15m (data_schema_v1.2.0.md:525), open_interest.change_1h_pct, current_price.

NOT TESTED (no document defines them) - recorded as "unknown (code-only)" in TWO_CORES_FIX_PASS_2026-10-02.md:
  - the dead-band thresholds PRICE_EPS 0.05 / CVD_EPS 1.0 / OI_EPS 0.02 (quad_classify.py:51-53; research/fast_track_2026-09-27/
    FORMULA_INVENTORY.md:61 "thresholds past L50", NO-SOURCE). Magnitudes below are far outside any plausible dead band
    so only the SIGN decides; no boundary is pinned.
  - the two labels that only the module's own docstring defines: weak_rally (price up, cvd down, oi down) and weak_sell
    (price down, cvd up, oi down); and any row where CVD or OI sits inside its dead band (falls to "flat" in the code).
  - delta_aligned / long_bias / short_bias sets (only described by research/_archive/loose_2026-10/AUDIT_2026-09-17_TRACKER.md:364-367, which
    quotes the code), the None returns for missing inputs, load_all() and main() (hard-coded Windows paths, print I/O).
  - price_past == 0 raises ZeroDivisionError (AUDIT_2026-09-17_TRACKER.md row 2 flags it as a defect); not pinned.
"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))   # runtime/ modules
sys.dont_write_bytecode = True

import quad_classify as qc  # noqa: E402

PAST_PRICE = 100.0


def snap_pair(price_dir, cvd_dir, oi_dir, nd15=5.0):
    """(cur, past). price +/-1.0 % ((101-100)/100*100 = 1.0), cvd delta_1h +/-100, oi change_1h_pct +/-1.0."""
    cur_price = {"up": 101.0, "down": 99.0, "none": 100.0}[price_dir]
    cvd = {"up": 100.0, "down": -100.0}[cvd_dir]
    oi = {"up": 1.0, "down": -1.0}[oi_dir]
    cur = {"current_price": cur_price,
           "cvd": {"cvd_recent": {"delta_1h": cvd}},
           "open_interest": {"change_1h_pct": oi},
           "trade_flow": {"net_delta_15m": nd15}}
    past = {"current_price": PAST_PRICE}
    return cur, past


# (price, oi, cvd) -> label.  Sign tuples from [Q1] (L75-L80); label names from [Q2].
CANONICAL = [
    # name, price, cvd, oi, expected label, [Q1] line
    ("trend_up",         "up",   "up",   "up",   "new_longs",        75),
    ("short_squeeze",    "up",   "up",   "down", "short_cover",      76),
    ("distribution",     "up",   "down", "up",   "distribution",     77),
    ("trend_down",       "down", "down", "up",   "new_shorts",       78),
    ("long_liquidation", "down", "down", "down", "long_liquidation", 79),
    ("accumulation",     "down", "up",   "up",   "accumulation",     80),
]


class QuadTruthTable(unittest.TestCase):
    def test_six_canonical_states(self):
        for name, p, c, o, want, line in CANONICAL:
            cur, past = snap_pair(p, c, o)
            r = qc.classify(cur, past)
            self.assertIsNotNone(r, name)
            self.assertEqual(r["cls"], want, f"{name} (SESSION_CLOSE_2026-09-20-0541Z.md:{line}): price {p}, oi {o}, cvd {c}")

    def test_six_canonical_labels_are_distinct(self):
        # six different sign tuples must give six different labels (no two rows collapse onto one class)
        got = set()
        for _, p, c, o, _, _ in CANONICAL:
            cur, past = snap_pair(p, c, o)
            got.add(qc.classify(cur, past)["cls"])
        self.assertEqual(len(got), 6, got)

    def test_price_oi_readings_agree_with_practitioner_convention(self):
        # [Q3]: price up + OI up = new longs; price down + OI up = new shorts; price up + OI down = short covering;
        # price down + OI down = long liquidation. CVD agreeing with the price direction in each case (as in [Q1]).
        for p, o, want in (("up", "up", "new_longs"), ("down", "up", "new_shorts"),
                           ("up", "down", "short_cover"), ("down", "down", "long_liquidation")):
            cvd = "up" if p == "up" else "down"
            cur, past = snap_pair(p, cvd, o)
            self.assertEqual(qc.classify(cur, past)["cls"], want, (p, o))

    def test_price_move_percent_is_hand_computed(self):
        # (101 - 100) / 100 * 100 = +1.0 ; (99 - 100) / 100 * 100 = -1.0   (price_1h_pct, docstring line 3)
        cur, past = snap_pair("up", "up", "up")
        self.assertAlmostEqual(qc.classify(cur, past)["price_pct"], 1.0, places=6)
        cur, past = snap_pair("down", "down", "down")
        self.assertAlmostEqual(qc.classify(cur, past)["price_pct"], -1.0, places=6)

    def test_inputs_are_echoed_from_documented_field_paths(self):
        # [Q6]: cvd_d1h <- cvd.cvd_recent.delta_1h ; oi_chg <- open_interest.change_1h_pct ; nd15 <- trade_flow.net_delta_15m
        cur, past = snap_pair("up", "down", "up", nd15=-7.5)
        r = qc.classify(cur, past)
        self.assertEqual((r["cvd_d1h"], r["oi_chg"], r["nd15"]), (-100.0, 1.0, -7.5))

    def test_unchanged_price_matches_no_row_and_is_flat(self):
        # [Q4]: price neither up nor down -> no [Q1] row applies -> "flat"
        for c in ("up", "down"):
            for o in ("up", "down"):
                cur, past = snap_pair("none", c, o)
                self.assertEqual(qc.classify(cur, past)["cls"], "flat", (c, o))
        cur, past = snap_pair("none", "up", "up")
        self.assertEqual(qc.classify(cur, past)["price_pct"], 0.0)


class NearestOneHourAgo(unittest.TestCase):
    """[Q5]: the comparison snapshot is the one nearest to (latest - 1 h). Tie-break and the choice to skip the latest
    snapshot itself are code-only and NOT tested here; distances below are unambiguous."""
    T = datetime(2026, 9, 29, 12, 0, 0, tzinfo=timezone.utc)

    def _snaps(self, minutes_before):
        out = [(self.T - timedelta(minutes=m), {"id": f"T-{m}m"}) for m in sorted(minutes_before, reverse=True)]
        out.append((self.T, {"id": "latest"}))
        return out

    def test_picks_snapshot_closest_to_60_minutes_before_latest(self):
        # distances from T-60: 120 m -> 60 ; 65 m -> 5 ; 30 m -> 30   => T-65m
        self.assertEqual(qc.nearest_1h_ago(self._snaps([120, 65, 30]))["id"], "T-65m")

    def test_closest_may_be_newer_than_60_minutes_ago(self):
        # distances from T-60: 80 m -> 20 ; 50 m -> 10 ; 5 m -> 55   => T-50m
        self.assertEqual(qc.nearest_1h_ago(self._snaps([80, 50, 5]))["id"], "T-50m")

    def test_no_snapshots_gives_none(self):
        self.assertIsNone(qc.nearest_1h_ago([]))


if __name__ == "__main__":
    unittest.main()
