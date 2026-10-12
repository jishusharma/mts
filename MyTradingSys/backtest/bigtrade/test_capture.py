"""
Tests for capture.py. Expected numbers are hand-computed on tiny series (see the comment above each assertion); none was taken from the code.
Time unit in the pure-function tests is 1 ms = 1 bar (tf_ms=1) so the EARLY/MID/LATE boundaries can be checked by eye.
"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from MyTradingSys.backtest.bigtrade import bigmoves as bm  # noqa: E402
from MyTradingSys.backtest.bigtrade import capture as cp  # noqa: E402
from MyTradingSys.backtest.bigtrade import test_bigmoves as tbm  # noqa: E402  (module import: its Test classes are not re-collected here)

NAN = float("nan")


def fire(t, side="long", layer="L", key="layer:L:L:5m", tf="5m", **kw):
    d = {"layer": layer, "key": key, "tf": tf, "side": side, "t": t, "price": NAN, "stop_dist_atr": NAN, "fee_R": NAN, "fee_dominated": None,
         "atr_kind": "wilder", "file": "x"}
    d.update(kw)
    return d


def toy_legs():
    """Three long legs and one short leg, all flagged for (1.5, 3). Time unit = bar (tf_ms = 1). One unflagged long leg."""
    flags = {(r, k): np.zeros(5, dtype=np.uint8) for r in (1.5, 2.0) for k in (3, 5, 8)}
    flags[(1.5, 3)] = np.array([1, 1, 1, 1, 0], dtype=np.uint8)
    return {"side": np.array([1, 1, 1, -1, 1]), "t_start": np.array([100, 200, 300, 100, 400]), "t_end": np.array([120, 204, 310, 120, 410]),
            "flags": flags}


FIRES_T = [99, 105, 106, 111, 201, 203, 250]


class TestLegCapture(unittest.TestCase):
    def test_bucket_boundaries(self):
        cap = cp.leg_capture(FIRES_T, [100, 200, 300], [120, 204, 310])
        # Leg A (100..120, dur 20): EARLY [100,105] holds 105 (inclusive edge); MID (105,110] holds 106; LATE (110,120] holds 111; fire 99 is before it.
        # Leg B (200..204, dur 4): EARLY [200,201] holds 201 (edge); MID (201,202] empty; LATE (202,204] holds 203.  Leg C (300..310): no fire after 250.
        self.assertEqual(list(cap["early"]), [True, True, False])
        self.assertEqual(list(cap["mid"]), [True, False, False])
        self.assertEqual(list(cap["late"]), [True, True, False])
        self.assertEqual(list(cap["t_first"]), [105, 201, -1])  # first fire inside [start, start + 50%]

    def test_fire_exactly_at_leg_end_is_late_not_lost(self):
        cap = cp.leg_capture([120], [100], [120])
        self.assertEqual((bool(cap["early"][0]), bool(cap["mid"][0]), bool(cap["late"][0])), (False, False, True))
        self.assertEqual(int(cap["t_first"][0]), -1)  # LATE fires are not a capture

    def test_metrics_recall_lead_delay_and_side_filter(self):
        legs = toy_legs()
        m = cp.leg_metrics(np.array(FIRES_T), legs, 1.5, 3, 1, 1)
        # long legs flagged for (1.5,3): A, B, C -> 3 (the 4th long leg is unflagged, the short leg is another side)
        self.assertEqual(m["n_legs"], 3)
        self.assertEqual((m["n_early"], m["n_mid"], m["n_late"]), (2, 1, 2))
        self.assertAlmostEqual(m["recall_early"], 2 / 3)
        self.assertAlmostEqual(m["recall_mid"], 1 / 3)
        self.assertAlmostEqual(m["recall_late"], 2 / 3)
        self.assertAlmostEqual(m["recall_catch"], 2 / 3)  # A and B have an EARLY or MID fire, C none
        # captured legs A (first fire 105, end 120) and B (201, end 204): lead = 15 and 3 -> median 9 ; delay = 5 and 1 -> median 3
        self.assertAlmostEqual(m["median_lead_bars"], 9.0)
        self.assertAlmostEqual(m["median_delay_bars"], 3.0)
        s = cp.leg_metrics(np.array(FIRES_T), legs, 1.5, 3, -1, 1)
        # the single short leg (100..120) sees the same fires as leg A
        self.assertEqual(s["n_legs"], 1)
        self.assertEqual((s["recall_early"], s["recall_mid"], s["recall_late"]), (1.0, 1.0, 1.0))
        self.assertAlmostEqual(s["median_lead_bars"], 15.0)

    def test_no_flagged_legs_gives_nan_recall(self):
        m = cp.leg_metrics(np.array(FIRES_T), toy_legs(), 2.0, 8, 1, 1)
        self.assertEqual(m["n_legs"], 0)
        self.assertTrue(math.isnan(m["recall_early"]))


class TestEvents(unittest.TestCase):
    def test_hit_rate_base_rate_lift_z(self):
        n = 10
        labels = {"t_close_ms": np.arange(n) * 10 + 1000, "mfe_long_24": np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, NAN]),
                  "mae_long_24": np.arange(n) * 0.1}
        j = np.array([2, 4, 7, 9])
        span = (int(labels["t_close_ms"][2]), int(labels["t_close_ms"][9]))
        e = cp.event_metrics(j, labels, "long", 24, 5, span)
        # fires at bars 2,4,7,9; bar 9 has no complete horizon (NaN) -> n_valid 3; mfe 2,4,7 -> one value >= 5 -> hit_rate 1/3
        # base over bars 2..9 with finite label (bars 2..8 -> mfe 2..8): values >= 5 are 5,6,7,8 -> 4/7
        # lift = (1/3)/(4/7) = 7/12 ; z = (1/3 - 4/7) / sqrt((4/7)(3/7)/3) = (-5/21)/(2/7) = -5/6
        self.assertEqual((e["n_valid"], e["hits"]), (3, 1))
        self.assertAlmostEqual(e["hit_rate"], 1 / 3)
        self.assertAlmostEqual(e["base_rate"], 4 / 7)
        self.assertAlmostEqual(e["lift"], 7 / 12)
        self.assertAlmostEqual(e["z"], -5 / 6)
        self.assertAlmostEqual(e["med_mae"], 0.7)  # the only hit is bar 7 -> mae 0.7


class TestFeeAndAlignment(unittest.TestCase):
    def test_fee_R_and_dominated_boundary(self):
        labels = {"atr_wilder": np.full(3, 100.0), "atr_sma": np.full(3, 200.0), "close": np.full(3, 100000.0)}
        fires = [
            fire(1, price=100000.0, stop_dist_atr=0.5),  # stop 50, round-trip fee 0.001 * 100000 = 100 -> fee_R 2.0 -> dominated
            fire(1, price=100000.0, stop_dist_atr=2.0),  # stop 200 -> fee_R 0.5 -> ok
            fire(1, price=100000.0, stop_dist_atr=1.0),  # stop 100 == fee 100 -> fee_R 1.0, NOT under the fee -> ok
            fire(1),  # no stop information -> unknown, not dominated
            fire(1, fee_R=3.0),  # value given in the file wins -> dominated
            fire(1, price=100000.0, stop_dist_atr=1.0, atr_kind="sma"),  # sma ATR 200 -> stop 200 -> fee_R 0.5
        ]
        fee_r, dom = cp.fee_info(fires, np.zeros(6, dtype=int), labels)
        self.assertAlmostEqual(fee_r[0], 2.0)
        self.assertAlmostEqual(fee_r[1], 0.5)
        self.assertAlmostEqual(fee_r[2], 1.0)
        self.assertTrue(math.isnan(fee_r[3]))
        self.assertAlmostEqual(fee_r[4], 3.0)
        self.assertAlmostEqual(fee_r[5], 0.5)
        self.assertEqual(list(dom), [True, False, False, False, True, False])

    def test_fire_to_bar_mapping(self):
        t_close = np.array([1000, 2000, 3000])
        j, keep, st = cp.map_fires_to_bars([fire(t) for t in (500, 1000, 1500, 2000, 3000, 3999, 4000)], t_close, 1000)
        # 500 precedes the data; 1000, 2000, 3000 are bar closes; 1500 and 3999 sit inside a bar (mapped back to the last closed bar, never forward);
        # 4000 would be the close of a bar that is not in the data -> outside
        self.assertEqual(list(keep), [False, True, True, True, True, True, False])
        self.assertEqual(list(j[keep]), [0, 0, 1, 2, 2])
        self.assertEqual((st["n_outside_data"], st["n_misaligned"]), (2, 2))


def mk_truth():
    """Ground truth from the step series of test_bigmoves: leg1 long bar 3 -> 8, leg2 short bar 8 -> 18, ATR exactly 1."""
    b = tbm.TestBuildLegs().bars()
    legs = bm.build_legs(b)
    lab = {"t_close_ms": b["t_close"].astype(np.int64), "close": b["c"], "atr_wilder": b["atr_wilder"], "atr_sma": b["atr_sma"]}
    for H in (2,):
        f = bm.forward_labels(b["o"], b["h"], b["l"], b["atr_wilder"], H)
        for name in bm.LABEL_NAMES:
            lab["%s_%d" % (name, H)] = f[name]
    return b, legs, lab


class TestScoreGroup(unittest.TestCase):
    def test_long_and_short_fires_end_to_end(self):
        b, legs, lab = mk_truth()
        tc = b["t_close"]  # bar i closes at T0 + (i + 1) * MS5
        # long leg1: close of bar3 = T0+4*MS5 .. close of bar8 = T0+9*MS5 (dur 5 bars): EARLY <= +1.25 bars, MID <= +2.5 bars
        # fires: bar3 close (offset 0 -> EARLY), bar5 close (offset 2 bars -> MID), bar7 close (offset 4 bars -> LATE)
        fl = [fire(int(tc[3])), fire(int(tc[5])), fire(int(tc[7]))]
        rows, info = cp.score_group(("L", "layer:L:L:5m", "5m", "long"), fl, legs, lab, (1.5,), (3,), (2,))
        self.assertEqual(len(rows), 1)
        x = rows[0]
        self.assertEqual((x["n_fires"], x["n_legs"]), (3, 1))
        self.assertEqual((x["recall_early"], x["recall_mid"], x["recall_late"], x["recall_catch"]), (1.0, 1.0, 1.0, 1.0))
        self.assertAlmostEqual(x["median_lead_bars"], 5.0)  # first fire at leg start, leg lasts 5 bars
        self.assertAlmostEqual(x["median_delay_bars"], 0.0)
        # forward MFE for k=3, H=2: bar3 -> (13.0-12.0)/1 = 1.0 ; bar5 -> 1.0 ; bar7 -> 0.5 : none reach 3 -> hit_rate 0 ; base 0 -> lift undefined
        self.assertEqual((x["n_valid_2"], x["hits_2"], x["hit_rate_2"], x["base_rate_2"]), (3, 0, 0.0, 0.0))
        self.assertTrue(math.isnan(x["lift_2"]))
        # short leg2: close of bar8 = T0+9*MS5 .. close of bar18 = T0+19*MS5 (dur 10): EARLY <= +2.5 bars, MID <= +5 bars (inclusive), LATE after
        fs = [fire(int(tc[9]), side="short"), fire(int(tc[13]), side="short"), fire(int(tc[16]), side="short")]
        rows, _ = cp.score_group(("L", "layer:L:L:5m", "5m", "short"), fs, legs, lab, (1.5,), (3,), (2,))
        y = rows[0]
        # bar9 close = +1 bar -> EARLY ; bar13 close = T0+14*MS5 = exactly +5 bars -> MID (inclusive) ; bar16 close = +8 bars -> LATE
        self.assertEqual((y["n_legs"], y["recall_early"], y["recall_mid"], y["recall_late"]), (1, 1.0, 1.0, 1.0))
        self.assertAlmostEqual(y["median_lead_bars"], 9.0)  # first fire +1 bar after start, leg ends 9 bars later
        self.assertAlmostEqual(y["median_delay_bars"], 1.0)

    def test_wrong_side_fire_captures_nothing(self):
        b, legs, lab = mk_truth()
        tc = b["t_close"]
        # short fires on the long leg1's start: the only short leg starts at bar 8, so recall is 0 (EARLY/MID/LATE all empty)
        rows, _ = cp.score_group(("L", "k", "5m", "short"), [fire(int(tc[3]), side="short")], legs, lab, (1.5,), (3,), (2,))
        self.assertEqual((rows[0]["n_legs"], rows[0]["recall_early"], rows[0]["recall_mid"], rows[0]["recall_late"]), (1, 0.0, 0.0, 0.0))

    def test_fee_dominated_fires_get_their_own_set(self):
        b, legs, lab = mk_truth()
        tc = b["t_close"]
        # ATR = 1 and price 12 => round-trip fee 0.001 * 12 = 0.012. stop 0.006 ATR -> fee_R 2.0 (dominated); stop 0.024 ATR -> 0.5 (ok)
        fl = [fire(int(tc[3]), price=12.0, stop_dist_atr=0.006), fire(int(tc[5]), price=12.0, stop_dist_atr=0.024)]
        rows, info = cp.score_group(("L", "k", "5m", "long"), fl, legs, lab, (1.5,), (3,), (2,))
        by = {x["fire_set"]: x for x in rows}
        self.assertEqual(sorted(by), ["all", "ok"])
        self.assertEqual((by["all"]["n_fires"], by["ok"]["n_fires"]), (2, 1))
        self.assertAlmostEqual(by["all"]["fee_dominated_share"], 0.5)
        self.assertAlmostEqual(by["ok"]["fee_dominated_share"], 0.0)
        # the dominated fire was the one at the leg start (EARLY): without it only the MID fire (bar5) remains
        self.assertEqual((by["all"]["recall_early"], by["ok"]["recall_early"], by["ok"]["recall_mid"]), (1.0, 0.0, 1.0))
        self.assertEqual(info["n_dominated"], 1)

    def test_no_fee_info_gives_only_the_all_set(self):
        b, legs, lab = mk_truth()
        rows, _ = cp.score_group(("L", "k", "5m", "long"), [fire(int(b["t_close"][3]))], legs, lab, (1.5,), (3,), (2,))
        self.assertEqual({x["fire_set"] for x in rows}, {"all"})
        self.assertTrue(math.isnan(rows[0]["fee_dominated_share"]))

    def test_duplicate_fire_rows_count_once(self):
        b, legs, lab = mk_truth()
        t = int(b["t_close"][3])
        rows, _ = cp.score_group(("L", "k", "5m", "long"), [fire(t), fire(t), fire(t + 1000)], legs, lab, (1.5,), (3,), (2,))
        self.assertEqual((rows[0]["n_fires"], rows[0]["n_fire_rows"]), (1, 3))  # t+1000 is inside bar 4 -> mapped back to bar 3: same bar

    def test_group_with_unknown_tf_is_skipped_not_scored(self):
        b, legs, lab = mk_truth()
        rows, infos, skipped = cp.run_capture([fire(1, tf="1m", key="layer:turn_of_candle:turn_of_candle:1m")], {"5m": legs}, {"5m": lab},
                                              (1.5,), (3,), (2,))
        self.assertEqual((rows, infos), ([], []))
        self.assertEqual((skipped[0]["tf"], skipped[0]["n_fire_rows"]), ("1m", 1))


class TestFilesAndSynthetic(unittest.TestCase):
    def test_read_fires_handles_quoted_json_and_bad_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fires_x.csv"
            p.write_text('layer,key,tf,side,t_fire_ms,price,params_id,params_json,code_commit,stop_dist_atr,fee_dominated\n'
                         'rsi,layer:rsi:rsi_events:5m,5m,long,1700000400000,100.5,p1,"{""a"": 1, ""b"": 2}",abc,0.5,true\n'
                         'rsi,layer:rsi:rsi_events:5m,5m,SHORT,1700000700000,100.5,p1,"{}",abc,,\n'
                         'rsi,layer:rsi:rsi_events:5m,5m,flat,1700000700000,100.5,p1,"{}",abc,,\n'
                         'rsi,layer:rsi:rsi_events:5m,5m,long,notatime,100.5,p1,"{}",abc,,\n', encoding="utf-8", newline="\n")
            fires, bad = cp.read_fires([p])
            self.assertEqual(bad, 2)  # side "flat" and an unparsable time
            self.assertEqual([(f["side"], f["t"]) for f in fires], [("long", 1700000400000), ("short", 1700000700000)])
            self.assertEqual(fires[0]["fee_dominated"], True)
            self.assertIsNone(fires[1]["fee_dominated"])
            self.assertAlmostEqual(fires[0]["stop_dist_atr"], 0.5)

    def test_synthetic_oracle_anti_and_random_through_the_files(self):
        b, legs, lab = mk_truth()
        b["atr_sma"] = b["atr_wilder"]
        with tempfile.TemporaryDirectory() as d:
            bm.write_legs_csv(Path(d) / "legs_5m.csv", legs)
            bm.write_labels_csv(Path(d) / "labels_5m.csv", b, h_list=(24, 96))
            lg, lb = cp.load_ground_truth(d, ["5m"])
            cp.make_synthetic_fires(lg, lb, Path(d) / "synthetic" / "fires_synth.csv", tfs=("5m",), r=1.5, k=3)
            fires, bad = cp.read_fires([Path(d) / "synthetic" / "fires_synth.csv"])
            self.assertEqual(bad, 0)
            rows, infos, skipped = cp.run_capture(fires, lg, lb)
            self.assertEqual(skipped, [])
            pick = {(x["layer"], x["side"]): x for x in rows if (x["r"], x["k"], x["fire_set"]) == (1.5, 3, "all")}
            # oracle fires on the pivot-bar close of each flagged leg with the leg's side: leg1 long and leg2 short are both caught EARLY at lead = dur
            self.assertEqual(pick[("synthetic_oracle", "long")]["recall_early"], 1.0)
            self.assertEqual(pick[("synthetic_oracle", "short")]["recall_early"], 1.0)
            # anti fires: opposite side at the same instants. short fire at leg1's start precedes the short leg (starts later): 0 ; long fire at
            # leg2's start (= leg1's end) is LATE for leg1 (end is inclusive) and never EARLY
            self.assertEqual(pick[("synthetic_anti", "short")]["recall_early"], 0.0)
            self.assertEqual((pick[("synthetic_anti", "long")]["recall_early"], pick[("synthetic_anti", "long")]["recall_late"]), (0.0, 1.0))

    def test_csv_and_markdown_outputs(self):
        b, legs, lab = mk_truth()
        rows, infos, skipped = cp.run_capture([fire(int(b["t_close"][3]))], {"5m": legs}, {"5m": lab}, (1.5, 2.0), (3, 5, 8), (2,))
        meta = {"generated": "t", "fire_files": ["f.csv"], "tfs": ["5m"], "coverage": "c", "synthetic": True, "csv_path": "p.csv"}
        md = cp.render_md(rows, infos, skipped, meta, [(1.5, 3)])
        self.assertIn("SYNTHETIC FIXTURE, NOT LAYER OUTPUT", md.splitlines()[0])
        self.assertIn("## r=1.5  k=3", md)
        with tempfile.TemporaryDirectory() as d:
            cp.write_matrix_csv(Path(d) / "m.csv", rows)
            raw = (Path(d) / "m.csv").read_bytes()
            self.assertNotIn(b"\r", raw)
            self.assertEqual(len(raw.decode().strip().split("\n")), 1 + len(rows))
            self.assertEqual(len(rows), 6)  # one group, set "all", 2 r x 3 k


if __name__ == "__main__":
    unittest.main()
