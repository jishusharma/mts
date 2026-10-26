"""test_regime_classifier.py - offline tests for runtime/regime_classifier.py (per-cycle trend regime detector).

Staged as .new 2026-10-02 (TWO_CORES_FIX_PASS_2026-10-02.md item 4). Promoted 2026-10-04 (T037) to MyTradingSys/tests/test_regime_classifier.py (collected by run_all_tests step 4).
Run directly:  python MyTradingSys/tests/test_regime_classifier.py

Expected values come from ONE document, never from the code under test:
  [R] MyTradingSys/research/_archive/loose_2026-10/TREND_REGIME_DETECTOR_SPEC.md
        L12-13  vwap_slope / cvd_slope take rising | falling | sideways;   L19  vp_shape takes B | P | D
        L27-34  votes: vwap_slope rising/falling -> up/down; cvd_slope rising/falling -> up/down;
                net_delta_1h > 0 / < 0 -> up/down; vp_shape == "P" -> up, == "D" -> down   (B, sideways, 0 = no vote)
        L37-39  up >= 3 -> TREND_UP ; elif down >= 3 -> TREND_DOWN ; else RANGE
        L41-43  anti-whipsaw: the candidate label must hold 3 consecutive cycles before it is published; a single
                conflicting cycle downgrades confidence, not the label
        L45-53  output sub-object: label TREND_UP | TREND_DOWN | RANGE, confidence LOW | MEDIUM | HIGH,
                consecutive_cycles, entered_at_utc;   L56 initial label = UNKNOWN until first publish
        L76-77  debug fields votes_up, votes_down, cycles_in_candidate_state are exposed
  Spec/audit note, not tested away: the spec maps vp_shape "D" to a DOWN vote (L34) although MarketDataSnapshot defines
  D as balanced (research/_archive/loose_2026-10/AUDIT_2026-09-17_TRACKER.md regime row 4; fast_track_2026-09-27/TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md:133).
  The test follows the spec; whether the spec should change is not decided here.

NOT TESTED (no document defines them) - recorded as "unknown (code-only)" in TWO_CORES_FIX_PASS_2026-10-02.md:
  - confidence_of() levels: when MEDIUM / HIGH are reached (code: streak >= 3 / >= 5, regime_classifier.py:41-42); the spec
    gives the three names (L51) and says a conflicting cycle "downgrades" confidence (L42) but no streak thresholds.
  - consecutive_cycles bookkeeping (spec L52 names the field, gives no rule), entered_at_utc value rules beyond "set when a
    label is published", reads of a missing/odd snapshot or state file (conditions None, non-numeric state values),
    latest_snapshot() glob/mtime choice, and the hard-coded Windows ROOT paths.

main() is not a pure function (file reads/writes). The debounce tests below redirect the two module-level paths
(SNAP_DIR, STATE_CODE) to a temp dir and refuse to run a cycle if STATE_CODE is not inside it, so the real
state_code_regime.json is never touched.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))   # runtime/ modules
sys.dont_write_bytecode = True

import regime_classifier as rc  # noqa: E402

RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def snap(vwap="sideways", cvd="sideways", nd1h=0.0, vp="B"):
    return {"conditions": {"vwap_slope": vwap, "cvd_slope": cvd, "vp_shape": vp},
            "trade_flow": {"net_delta_1h": nd1h}}


UP4 = snap("rising", "rising", 5.0, "P")        # 4 up votes
DOWN4 = snap("falling", "falling", -5.0, "D")   # 4 down votes
FLAT0 = snap()                                  # 0 votes (sideways, sideways, 0, B)


class VoteTable(unittest.TestCase):
    def test_all_four_up(self):
        self.assertEqual(rc.classify(UP4), ("TREND_UP", 4, 0))

    def test_all_four_down(self):
        self.assertEqual(rc.classify(DOWN4), ("TREND_DOWN", 0, 4))

    def test_no_votes_is_range(self):
        self.assertEqual(rc.classify(FLAT0), ("RANGE", 0, 0))

    def test_each_voter_counts_exactly_one_up_vote(self):
        # spec L27,29,31,33: one voter up, the other three neutral -> (1 up, 0 down) -> RANGE
        cases = {"vwap_slope": snap(vwap="rising"), "cvd_slope": snap(cvd="rising"),
                 "net_delta_1h": snap(nd1h=0.1), "vp_shape": snap(vp="P")}
        for name, s in cases.items():
            self.assertEqual(rc.classify(s), ("RANGE", 1, 0), name)

    def test_each_voter_counts_exactly_one_down_vote(self):
        # spec L28,30,32,34
        cases = {"vwap_slope": snap(vwap="falling"), "cvd_slope": snap(cvd="falling"),
                 "net_delta_1h": snap(nd1h=-0.1), "vp_shape": snap(vp="D")}
        for name, s in cases.items():
            self.assertEqual(rc.classify(s), ("RANGE", 0, 1), name)

    def test_three_up_is_trend_up_whichever_voter_is_neutral(self):
        # spec L37: up >= 3 (boundary is 3, not 4). Each voter in turn is neutral.
        for neutral in ("vwap", "cvd", "nd", "vp"):
            s = snap("rising", "rising", 5.0, "P")
            if neutral == "vwap": s["conditions"]["vwap_slope"] = "sideways"
            if neutral == "cvd": s["conditions"]["cvd_slope"] = "sideways"
            if neutral == "nd": s["trade_flow"]["net_delta_1h"] = 0.0
            if neutral == "vp": s["conditions"]["vp_shape"] = "B"
            self.assertEqual(rc.classify(s), ("TREND_UP", 3, 0), neutral)

    def test_three_down_is_trend_down_whichever_voter_is_neutral(self):
        # spec L38
        for neutral in ("vwap", "cvd", "nd", "vp"):
            s = snap("falling", "falling", -5.0, "D")
            if neutral == "vwap": s["conditions"]["vwap_slope"] = "sideways"
            if neutral == "cvd": s["conditions"]["cvd_slope"] = "sideways"
            if neutral == "nd": s["trade_flow"]["net_delta_1h"] = 0.0
            if neutral == "vp": s["conditions"]["vp_shape"] = "B"
            self.assertEqual(rc.classify(s), ("TREND_DOWN", 0, 3), neutral)

    def test_two_two_split_is_range(self):
        # spec L39 "else RANGE": vote split 2 up / 2 down
        self.assertEqual(rc.classify(snap("rising", "rising", -5.0, "D")), ("RANGE", 2, 2))

    def test_two_up_none_down_is_range(self):
        self.assertEqual(rc.classify(snap("rising", "sideways", 5.0, "B")), ("RANGE", 2, 0))

    def test_three_up_one_down_is_trend_up(self):
        # up is tested first (spec L37): 3 up + 1 down -> TREND_UP with the down vote still counted
        self.assertEqual(rc.classify(snap("rising", "rising", 5.0, "D")), ("TREND_UP", 3, 1))

    def test_three_down_one_up_is_trend_down(self):
        self.assertEqual(rc.classify(snap("falling", "falling", -5.0, "P")), ("TREND_DOWN", 1, 3))

    def test_net_delta_exactly_zero_is_no_vote(self):
        # spec L31-32: only > 0 and < 0 vote
        self.assertEqual(rc.classify(snap("rising", "rising", 0.0, "B")), ("RANGE", 2, 0))

    def test_confidence_values_stay_in_documented_domain(self):
        # spec L51: LOW | MEDIUM | HIGH. Exact thresholds are code-only and not pinned.
        for published in ("UNKNOWN", "RANGE", "TREND_UP", "TREND_DOWN"):
            for cand in ("RANGE", "TREND_UP", "TREND_DOWN"):
                for streak in (0, 1, 2, 3, 4, 5, 9):
                    self.assertIn(rc.confidence_of(published, cand, streak), RANK, (published, cand, streak))


class Debounce(unittest.TestCase):
    """spec L41-43 and L56 through main(), with the two module paths redirected to a temp dir."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="regime_test_")
        self.tmp = Path(self._tmp)
        self._saved = (rc.SNAP_DIR, rc.STATE_CODE)
        rc.SNAP_DIR = self.tmp / "snaps"
        rc.SNAP_DIR.mkdir()
        rc.STATE_CODE = self.tmp / "state_code_regime.json"

    def tearDown(self):
        rc.SNAP_DIR, rc.STATE_CODE = self._saved
        shutil.rmtree(self._tmp, ignore_errors=True)

    def cycle(self, snapshot):
        # safety: never let a test cycle write the real runtime state file
        self.assertEqual(rc.STATE_CODE.parent, self.tmp)
        self.assertEqual(rc.SNAP_DIR.parent, self.tmp)
        for f in rc.SNAP_DIR.glob("*.json"):
            f.unlink()
        (rc.SNAP_DIR / "BTCUSDT_test.json").write_text(json.dumps(snapshot), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc.main()
        return json.loads(rc.STATE_CODE.read_text(encoding="utf-8"))

    def test_label_is_unknown_until_candidate_holds_three_cycles(self):
        s1 = self.cycle(UP4)
        self.assertEqual((s1["label"], s1["candidate"], s1["cycles_in_candidate_state"]), ("UNKNOWN", "TREND_UP", 1))
        s2 = self.cycle(UP4)
        self.assertEqual((s2["label"], s2["cycles_in_candidate_state"]), ("UNKNOWN", 2))
        s3 = self.cycle(UP4)
        self.assertEqual((s3["label"], s3["cycles_in_candidate_state"]), ("TREND_UP", 3))
        self.assertTrue(s3["entered_at_utc"])

    def test_output_fields_follow_the_spec(self):
        s = self.cycle(UP4)
        for k in ("label", "confidence", "consecutive_cycles", "entered_at_utc",      # spec L50-53
                  "votes_up", "votes_down", "cycles_in_candidate_state"):             # spec L76-77
            self.assertIn(k, s)
        self.assertIn(s["confidence"], RANK)
        self.assertIn(s["label"], ("UNKNOWN", "TREND_UP", "TREND_DOWN", "RANGE"))
        self.assertEqual((s["votes_up"], s["votes_down"]), (4, 0))

    def _published_up(self, n=3):
        last = None
        for _ in range(n):
            last = self.cycle(UP4)
        self.assertEqual(last["label"], "TREND_UP")
        return last

    def test_single_conflicting_cycle_keeps_the_label_and_does_not_raise_confidence(self):
        base = self._published_up(5)
        after = self.cycle(FLAT0)                      # one RANGE cycle
        self.assertEqual(after["label"], "TREND_UP")   # spec L42-43: not the label
        self.assertEqual(after["candidate"], "RANGE")
        self.assertLessEqual(RANK[after["confidence"]], RANK[base["confidence"]])   # downgrades, never upgrades
        back = self.cycle(UP4)
        self.assertEqual(back["label"], "TREND_UP")

    def test_label_changes_only_after_three_consecutive_new_candidate_cycles(self):
        self._published_up(3)
        self.assertEqual(self.cycle(FLAT0)["label"], "TREND_UP")    # RANGE run = 1
        self.assertEqual(self.cycle(FLAT0)["label"], "TREND_UP")    # run = 2
        third = self.cycle(FLAT0)                                   # run = 3
        self.assertEqual(third["label"], "RANGE")
        self.assertEqual(third["cycles_in_candidate_state"], 3)

    def test_interrupted_runs_never_publish(self):
        # from published TREND_UP: runs RANGE x2, TREND_DOWN x2, then RANGE x3. Only the last run reaches 3.
        self._published_up(3)
        seq = [(FLAT0, "TREND_UP"), (FLAT0, "TREND_UP"), (DOWN4, "TREND_UP"), (DOWN4, "TREND_UP"),
               (FLAT0, "TREND_UP"), (FLAT0, "TREND_UP"), (FLAT0, "RANGE")]
        for i, (s, want) in enumerate(seq):
            self.assertEqual(self.cycle(s)["label"], want, f"step {i}")


if __name__ == "__main__":
    unittest.main()
