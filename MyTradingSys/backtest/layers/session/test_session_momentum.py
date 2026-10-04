import unittest

from MyTradingSys.backtest.layers.session.session_momentum import session_momentum_events

# Expected numbers hand-computed from FORMULAS.md section 15 (T055 C2).
M30 = 1800000
DAY = 86400000


def b(t, o, c):
    return {"t": t, "o": o, "c": c}


BARS = [b(0, 100, 101), b(M30, 101, 102), b(DAY, 200, 198), b(DAY + M30, 198, 197)]


class TestSessionMomentum(unittest.TestCase):
    def test_rest_of_session(self):
        ev = session_momentum_events(BARS, bar_min=30, first_min=30, entry_min=30)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(0, "long"), (2, "short")])
        self.assertAlmostEqual(ev[0]["r_first"], 0.01, places=12)
        self.assertAlmostEqual(ev[1]["r_first"], -0.01, places=12)
        self.assertEqual(ev[1]["session_start"], DAY)

    def test_later_entry(self):
        ev = session_momentum_events(BARS, bar_min=30, first_min=30, entry_min=60)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(1, "long"), (3, "short")])

    def test_threshold_filters_all(self):
        self.assertEqual(session_momentum_events(BARS, bar_min=30, min_abs=0.015), [])

    def test_two_bars_in_first_window(self):
        # 1-hour first window with 30m bars: r = 102/100 - 1 = 0.02 ; entry at 60 min -> idx1
        ev = session_momentum_events(BARS[:2], bar_min=30, first_min=60, entry_min=60)
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["i"], ev[0]["side"]), (1, "long"))
        self.assertAlmostEqual(ev[0]["r_first"], 0.02, places=12)

    def test_late_session_start(self):
        # session starts 23:30 UTC (1410 min) of the previous day; bar t = DAY-M30 belongs to session S=DAY-M30
        bars = [b(DAY - M30, 100, 99), b(DAY, 99, 98)]
        ev = session_momentum_events(bars, bar_min=30, session_start_min=1410, first_min=30, entry_min=60)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(1, "short")])
        self.assertEqual(ev[0]["session_start"], DAY - M30)

    def test_ny_anchor_is_dst_aware(self):
        # B102: fixed 810 (13:30 UTC) is wrong in US standard time; "ny" = day_gates.ny_open_utc
        import datetime as dt
        def ms(y, m, d, h, mi):
            return int(dt.datetime(y, m, d, h, mi, tzinfo=dt.timezone.utc).timestamp() * 1000)
        for (y, m, d), (h, mi) in (((2026, 1, 14), (14, 30)), ((2026, 7, 15), (13, 30))):
            s = ms(y, m, d, h, mi)
            bars = [b(s - M30, 1, 1), b(s, 100, 101), b(s + M30, 101, 102)]
            ev = session_momentum_events(bars, bar_min=30, session_start_min="ny", first_min=30, entry_min=60)
            self.assertEqual([(e["i"], e["side"], e["session_start"]) for e in ev], [(2, "long", s)])

    def test_ny_anchor_skips_weekend(self):
        import datetime as dt
        sat = int(dt.datetime(2026, 1, 17, 14, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)
        bars = [b(sat, 100, 101), b(sat + M30, 101, 102)]
        self.assertEqual(session_momentum_events(bars, bar_min=30, session_start_min="ny",
                                                 first_min=30, entry_min=60), [])

    def test_missing_entry_bar_skips(self):
        self.assertEqual(session_momentum_events(BARS[:1], bar_min=30, first_min=30, entry_min=60), [])

    def test_errors(self):
        with self.assertRaises(ValueError):
            session_momentum_events([], bar_min=30)
        with self.assertRaises(ValueError):
            session_momentum_events(BARS, bar_min=30, first_min=60, entry_min=30)
        with self.assertRaises(ValueError):
            session_momentum_events(BARS, bar_min=0)


if __name__ == "__main__":
    unittest.main()
