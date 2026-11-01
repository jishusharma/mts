import unittest

from MyTradingSys.backtest.layers.fabio.fabio_escalation import (
    bar_delta,
    escalation_events,
)


def bar(t, o, c, v, tbv, h=None, l=None):
    return {
        "t": t, "o": o, "c": c, "v": v, "tbv": tbv,
        "h": h if h is not None else max(o, c),
        "l": l if l is not None else min(o, c),
    }


class TestBarDelta(unittest.TestCase):
    def test_formula(self):
        self.assertEqual(bar_delta({"v": 20, "tbv": 12.5}), 5.0)
        self.assertEqual(bar_delta({"v": 10, "tbv": 5}), 0.0)


# Hand-verified fixture (see 088-fabio-escalation.md packed spec, and a scratch
# run of cc_structure.find_swings): with left=1,right=1,use_body=True this
# series has exactly ONE swing: a "high" at i=2, price=100, confirmed_i=3.
# Deltas (2*tbv-v): [1,1,1,1,5,1,10,1,1,1].
#  - i=4: h=100.05 (within 0.1% of 100) -> "at level", aggressive (|5|>=2*avg(1,1,1)=2),
#    direction up; close=91 <= 100.1 -> absorbed. first_absorbed_i=4.
#  - i=5: h=100.03 at level, but |1| < 2*avg(1,1,5)=4.667 -> not aggressive, no-op.
#  - i=6: h=100.08 at level, |10| >= 2*avg(1,5,1)=4.667 -> aggressive, direction up;
#    volume window [3..6]=(15,20,18,25) -> 25 is max (record); |delta| window
#    (1,5,1,10) -> 10 is max (record) -> ESCALATION fires at k=6, side="long".
def _escalation_fixture():
    return [
        bar(0, 80, 90, 10, 5.5),
        bar(1, 78, 95, 10, 5.5),
        bar(2, 76, 100, 10, 5.5),   # swing high i=2, price=100
        bar(3, 74, 90, 15, 8),
        bar(4, 72, 91, 20, 12.5, h=100.05, l=71),
        bar(5, 70, 92, 18, 9.5, h=100.03, l=69),
        bar(6, 68, 93, 25, 17.5, h=100.08, l=67),
        bar(7, 66, 94, 10, 5.5, h=95, l=65),
        bar(8, 64, 95, 10, 5.5, h=94, l=63),
        bar(9, 62, 96, 10, 5.5, h=93, l=61),
    ]


class TestEscalationEvents(unittest.TestCase):
    def test_escalation_fires_on_record_volume_and_record_delta(self):
        bars = _escalation_fixture()
        events = escalation_events(
            bars, left=1, right=1, use_body=True,
            level_tolerance=0.001, aggression_k=2.0, record_lookback=3,
            require_break=False,   # legacy reading: fixture bar 6 closes at 93, inside the level
        )
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual(ev["i"], 6)
        self.assertEqual(ev["t"], bars[6]["t"])
        self.assertEqual(ev["level_i"], 2)
        self.assertEqual(ev["level_price"], 100)
        self.assertEqual(ev["level_kind"], "high")
        self.assertEqual(ev["side"], "long")
        self.assertEqual(ev["kind"], "escalation_breakout")
        self.assertEqual(ev["absorbed_i"], 4)
        self.assertEqual(ev["escalation_i"], 6)
        self.assertEqual(ev["delta_k"], 10)
        self.assertEqual(ev["volume_k"], 25)

    def test_no_escalation_when_delta_not_a_record(self):
        # Lower i6's delta below i4's absorbed-test delta (5) so it is no longer
        # the record within its own lookback window, even though volume is.
        bars = _escalation_fixture()
        bars[6] = bar(6, 68, 93, 25, 14.0, h=100.08, l=67)  # delta = 2*14-25 = 3
        events = escalation_events(
            bars, left=1, right=1, level_tolerance=0.001,
            aggression_k=2.0, record_lookback=3, require_break=False,
        )
        self.assertEqual(events, [])

    def test_bad_params_raise(self):
        bars = _escalation_fixture()
        with self.assertRaises(ValueError):
            escalation_events(bars, level_tolerance=-0.001)
        with self.assertRaises(ValueError):
            escalation_events(bars, aggression_k=0)
        with self.assertRaises(ValueError):
            escalation_events(bars, record_lookback=0)


KW = dict(left=1, right=1, use_body=True, level_tolerance=0.001, aggression_k=2.0, record_lookback=3)


class TestRequireBreak(unittest.TestCase):
    """FAB-003 says BREAKOUT: the record bar must close beyond the level (break definition is OURS)."""

    def test_record_bar_closing_inside_level_does_not_fire_by_default(self):
        # fixture bar 6 is the record bar but closes at 93 < level 100: no breakout.
        self.assertEqual(escalation_events(_escalation_fixture(), **KW), [])

    def test_legacy_flag_keeps_old_event(self):
        ev = escalation_events(_escalation_fixture(), require_break=False, **KW)
        self.assertEqual([e["i"] for e in ev], [6])

    def test_record_bar_closing_beyond_level_fires(self):
        bars = _escalation_fixture()
        bars[6] = bar(6, 68, 100.05, 25, 17.5, h=100.08, l=67)   # close 100.05 > level 100
        ev = escalation_events(bars, **KW)
        self.assertEqual([(e["i"], e["side"], e["level_i"]) for e in ev if e["level_i"] == 2], [(6, "long", 2)])

    def test_close_exactly_at_level_is_not_a_break(self):
        bars = _escalation_fixture()
        bars[6] = bar(6, 68, 100.0, 25, 17.5, h=100.08, l=67)
        self.assertEqual([e for e in escalation_events(bars, **KW) if e["level_i"] == 2], [])

    def test_short_side_mirror(self):
        # negate prices around 200: swing low at 100 -> use mirrored fixture, deltas flipped
        bars = []
        for b in _escalation_fixture():
            bars.append({"t": b["t"], "o": 200 - b["o"], "c": 200 - b["c"], "v": b["v"],
                         "tbv": b["v"] - b["tbv"], "h": 200 - b["l"], "l": 200 - b["h"]})
        self.assertEqual(escalation_events(bars, **KW), [])                       # closes inside the level
        self.assertEqual([e["i"] for e in escalation_events(bars, require_break=False, **KW)], [6])
        bars[6] = dict(bars[6], c=99.95)                                          # close below low level 100
        ev = [e for e in escalation_events(bars, **KW) if e["level_i"] == 2]
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(6, "short")])

    def test_fail_closed_short_and_empty(self):
        self.assertEqual(escalation_events(_escalation_fixture()[:3], **KW), [])
        with self.assertRaises(ValueError):
            escalation_events([], **KW)

    def test_restart_same_bars_same_events(self):
        bars = _escalation_fixture()
        bars[6] = bar(6, 68, 100.05, 25, 17.5, h=100.08, l=67)
        self.assertEqual(escalation_events(bars, **KW), escalation_events(list(bars), **KW))


if __name__ == "__main__":
    unittest.main()
