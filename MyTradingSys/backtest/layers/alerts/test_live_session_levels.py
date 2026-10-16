"""Tests for alerts/live_session_levels.py. 1m fixtures hand-built; expected event minutes/levels are read from the
construction (level = previous UTC day extreme, fail = first close back inside within 60 min, before 14:00)."""
import unittest

from MyTradingSys.backtest.layers.alerts import live_session_levels as m

MIN = 60000
DAY = 86400000
D0 = (1790000000000 // DAY) * DAY
D1 = D0 + DAY


def bar(t, o=100.0, h=None, l=None, c=None):
    c = o if c is None else c
    return {"t": t, "o": o, "h": max(o, c) if h is None else h, "l": min(o, c) if l is None else l,
            "c": c, "v": 1.0, "tbv": 0.5}


def day0():
    """Full previous day, flat 100 except high 110 at minute 500 and low 90 at minute 600."""
    bs = [bar(D0 + i * MIN) for i in range(1440)]
    bs[500]["h"] = 110.0
    bs[600]["l"] = 90.0
    return bs


def day1(n=300, over=None):
    bs = [bar(D1 + i * MIN) for i in range(n)]
    for i, kw in (over or {}).items():
        bs[i].update(kw)
    return bs


def high_case():
    # minute 100 spikes to 111 (> 110), close 109.5 already back below 110 -> touch = fail = 100
    return day0() + day1(over={100: {"h": 111.0, "c": 109.5}})


def low_case():
    return day0() + day1(over={50: {"l": 89.0, "c": 90.5}})


class TestSessionLevelsLive(unittest.TestCase):
    def test_high_failed_break_short(self):
        ev = m.adapter(high_case())
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["side"], e["event"]), (D1 + 100 * MIN, "short", "sess_pdh_failed_break"))
        self.assertEqual((e["level"], e["entry"], e["spike"]), (110.0, 109.5, 111.0))
        self.assertTrue(e["sampling"])

    def test_low_failed_break_long(self):
        ev = m.adapter(low_case())
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["side"], e["event"]), (D1 + 50 * MIN, "long", "sess_pdl_failed_break"))
        self.assertEqual((e["level"], e["entry"], e["spike"]), (90.0, 90.5, 89.0))

    def test_no_fail_no_event(self):
        over = {i: {"h": 112.0, "c": 111.0} for i in range(100, 170)}
        self.assertEqual(m.adapter(day0() + day1(over=over)), [])

    def test_empty_and_short(self):
        self.assertEqual(m.adapter([]), [])
        self.assertEqual(m.adapter(day0()[:600] + day1(over={100: {"h": 111.0, "c": 109.5}})), [])
        self.assertEqual(m.adapter(day0()), [])

    def test_no_lookahead_truncation(self):
        for bars, tev in ((high_case(), D1 + 100 * MIN), (low_case(), D1 + 50 * MIN)):
            full = m.adapter(bars)
            self.assertEqual(len(full), 1)
            self.assertEqual(m.adapter([b for b in bars if b["t"] < tev]), [])
            self.assertEqual(m.adapter([b for b in bars if b["t"] <= tev]), full)
            for k in range(1, len(bars) + 1, 97):
                want = [e for e in full if e["t"] <= bars[k - 1]["t"]]
                self.assertEqual(m.adapter(bars[:k]), want, k)

    def test_restart_same_output(self):
        bars = high_case()
        self.assertEqual(m.adapter(bars), m.adapter([dict(b) for b in bars]))

    def test_both_sides_same_day_sorted(self):
        bars = day0() + day1(over={50: {"l": 89.0, "c": 90.5}, 100: {"h": 111.0, "c": 109.5}})
        ev = m.adapter(bars)
        self.assertEqual([(e["t"], e["side"]) for e in ev], [(D1 + 50 * MIN, "long"), (D1 + 100 * MIN, "short")])

    def test_nan_bar_dropped(self):
        bars = high_case()
        bars[1500]["c"] = float("nan")
        bars[1500]["h"] = float("nan")
        self.assertEqual([e["t"] for e in m.adapter(bars)], [D1 + 100 * MIN])
        nan_all = [dict(b, c=float("nan")) for b in high_case()]
        self.assertEqual(m.adapter(nan_all), [])

    def test_side_mapping(self):
        self.assertEqual(m.SIDE, {"high": "short", "low": "long"})


if __name__ == "__main__":
    unittest.main()
