"""Edge-case tests for fabio_escalation, derived from spec 088 (no numbers taken from running the code).

Base fixture (hand-traced in test_fabio_escalation.py): left=1,right=1 -> one swing HIGH i=2 price=100,
confirmed_i=3; deltas [1,1,1,1,5,1,10,1,1,1]; absorbed at i=4, escalation at i=6 (side long).
"""
import copy
import unittest

from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events

KW = dict(left=1, right=1, use_body=True, level_tolerance=0.001, aggression_k=2.0, record_lookback=3)


def bar(t, o, c, v, tbv, h=None, l=None):
    return {"t": t, "o": o, "c": c, "v": v, "tbv": tbv,
            "h": h if h is not None else max(o, c), "l": l if l is not None else min(o, c)}


def fixture():
    return [
        bar(0, 80, 90, 10, 5.5), bar(1, 78, 95, 10, 5.5), bar(2, 76, 100, 10, 5.5),
        bar(3, 74, 90, 15, 8), bar(4, 72, 91, 20, 12.5, h=100.05, l=71),
        bar(5, 70, 92, 18, 9.5, h=100.03, l=69), bar(6, 68, 93, 25, 17.5, h=100.08, l=67),
        bar(7, 66, 94, 10, 5.5, h=95, l=65), bar(8, 64, 95, 10, 5.5, h=94, l=63),
        bar(9, 62, 96, 10, 5.5, h=93, l=61),
    ]


class TestEscalationEdges(unittest.TestCase):
    def test_empty_and_single_bar(self):
        with self.assertRaises(ValueError):  # codebase convention: find_swings raises on empty, not caught
            escalation_events([], **KW)
        self.assertEqual(escalation_events([bar(0, 1, 1, 10, 5)], **KW), [])

    def test_lookback_longer_than_series_still_fires(self):
        # window clipped to index 0. i=4: avg=(1,1,1,1)=1, |5|>=2 absorbed. i=6: avg=10/6=1.667, |10|>=3.33;
        # volume 25 is max of all, |delta| 10 is max of all -> fires.
        kw = dict(KW, record_lookback=50)
        ev = escalation_events(fixture(), **kw)
        self.assertEqual([e["i"] for e in ev], [6])

    def test_zero_delta_bar_is_not_a_test(self):
        bars = fixture()
        bars[6] = bar(6, 68, 93, 25, 12.5, h=100.08, l=67)  # delta = 0
        self.assertEqual(escalation_events(bars, **KW), [])

    def test_volume_tie_counts_as_record(self):
        bars = fixture()
        bars[4] = bar(4, 72, 91, 25, 15, h=100.05, l=71)  # v=25 (ties bar 6), delta=5 unchanged
        ev = escalation_events(bars, **KW)
        self.assertEqual([e["i"] for e in ev], [6])

    def test_delta_tie_counts_as_record(self):
        bars = fixture()
        bars[6] = bar(6, 68, 93, 25, 15, h=100.08, l=67)  # delta=5 ties bar 4; avg(1,5,1)=2.33, 5>=4.67
        ev = escalation_events(bars, **KW)
        self.assertEqual([e["i"] for e in ev], [6])
        self.assertEqual(ev[0]["delta_k"], 5)

    def test_zero_tolerance_means_no_bar_at_level(self):
        # highs 100.05/100.03/100.08 are not exactly 100 -> nothing at the level
        self.assertEqual(escalation_events(fixture(), **dict(KW, level_tolerance=0.0)), [])

    def test_huge_aggression_k_no_events(self):
        self.assertEqual(escalation_events(fixture(), **dict(KW, aggression_k=1000.0)), [])

    def test_non_index_timestamps_and_input_not_mutated(self):
        bars = fixture()
        for b in bars:
            b["t"] = 1_000_000 + 60_000 * b["t"] * 3  # gaps, still increasing
        before = copy.deepcopy(bars)
        ev = escalation_events(bars, **KW)
        self.assertEqual(bars, before)
        self.assertEqual(ev[0]["t"], 1_000_000 + 60_000 * 6 * 3)
        self.assertEqual(ev[0]["i"], 6)

    def test_mirrored_low_level_gives_short(self):
        # price p -> 200-p, h<->l swapped, delta sign flipped (tbv' = v - tbv). Swing LOW i=2 price=100.
        bars = []
        for b in fixture():
            bars.append({"t": b["t"], "o": 200 - b["o"], "c": 200 - b["c"], "v": b["v"],
                         "tbv": b["v"] - b["tbv"], "h": 200 - b["l"], "l": 200 - b["h"]})
        ev = escalation_events(bars, **KW)
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["i"], ev[0]["side"], ev[0]["level_kind"], ev[0]["absorbed_i"]), (6, "short", "low", 4))
        self.assertEqual(ev[0]["delta_k"], -10)

    def test_later_closing_under_level_record_bar_keeps_first_absorption(self):
        # Spec: only the FIRST absorbed test matters; a later record aggressive bar that also closes
        # under the level must fire escalation (not be recorded as a second absorption).
        ev = escalation_events(fixture(), **KW)
        self.assertEqual(ev[0]["absorbed_i"], 4)


if __name__ == "__main__":
    unittest.main()
