import math
import unittest
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.wlow_bounce import detector as D
from MyTradingSys.backtest.layers.wlow_bounce import status as S

MON = int(datetime(2026, 10, 5, tzinfo=timezone.utc).timestamp() * 1000)   # a Monday 00:00 UTC
LOOSE = dict(D.PARAMS, band_x=0.02)   # synthetic ramps sit ~1.3 % under the (V-widened) band; the default 0.5 % is tested via injected arrays


def mk(rows):
    out, prev = [], rows[0][0]
    for k, (c, low) in enumerate(rows):
        o = prev
        out.append(dict(t=MON + k * D.HOUR_MS, o=o, h=max(o, c) * 1.0005, l=min(o, c) * 0.9995 if low is None else low,
                        c=c, v=1000.0, tbv=500.0))
        prev = c
    return out


def shape(hold, bounce=(81200, 82300, 83100), dip=True):
    """Week 1 (low 80500), week 2 calm, then the 2026-10-15 shape: break the prior weekly low, V-bounce, hold."""
    s = [(83000 + 1000 * math.sin(k / 9.0), 80500.0 if k == 100 else None) for k in range(168)]
    s += [(83000 + 200 * math.sin(k / 7.0), None) for k in range(100)]
    s += [(81500, None), (80200, 80100.0) if dip else (81000, None)]
    return s + [(c, None) for c in bounce] + [(c, None) for c in hold]


class HoldOk(unittest.TestCase):
    def setUp(self):
        self.c = [dict(t=MON + i * D.HOUR_MS, o=100, h=101, l=99, c=100.0, v=1, tbv=0.5) for i in range(6)]
        self.bb = [100.2] * 6

    def test_ok_flat_rsi_under_60_near_band(self):
        self.assertTrue(D.hold_ok(self.c, self.bb, [56.0, 57.0, 57.5, 57.0, 56.5, 57.0], 5))

    def test_rsi_at_or_above_60_fails(self):
        self.assertFalse(D.hold_ok(self.c, self.bb, [56.0, 57.0, 57.5, 57.0, 56.5, 60.0], 5))

    def test_rsi_not_flat_fails(self):
        self.assertFalse(D.hold_ok(self.c, self.bb, [50.0, 52.0, 53.0, 55.0, 57.0, 59.0], 5))

    def test_below_band_fails(self):
        self.assertFalse(D.hold_ok(self.c, [101.0] * 6, [57.0] * 6, 5))

    def test_rsi_below_floor_fails(self):
        self.assertFalse(D.hold_ok(self.c, self.bb, [50.0] * 6, 5))


class WeeklyLow(unittest.TestCase):
    def test_iso_uses_only_completed_prior_week(self):
        c = mk(shape([83140, 83180]))
        W = D.weekly_low_series(c)
        self.assertIsNone(W[10])                    # week 1 has no prior complete week
        self.assertEqual(W[200], 80500.0)           # week 2 -> week 1 low
        self.assertEqual(W[168], 80500.0)

    def test_roll168(self):
        c = mk(shape([83140]))
        self.assertEqual(D.weekly_low_series(c, "roll168")[200], 80500.0)


class Events(unittest.TestCase):
    def test_1015_shape_triggers_and_is_active(self):
        c = mk(shape([83140, 83180, 83220, 83260]))
        ev = D.find_events(c, LOOSE)
        self.assertEqual([e["status"] for e in ev], ["TRIGGERED"])
        self.assertEqual(ev[0]["W"], 80500.0)
        self.assertGreaterEqual(ev[0]["trigger"] - ev[0]["bounce"], 4)
        self.assertEqual(D.status_now(c, LOOSE)["state"], "ACTIVE")

    def test_two_hold_bars_is_armed_not_active(self):
        c = mk(shape([83140, 83180]))
        self.assertEqual(D.status_now(c, LOOSE)["state"], "ARMED")

    def test_no_break_is_idle(self):
        c = mk(shape([83140, 83180, 83220, 83260], dip=False))
        self.assertEqual(D.find_events(c, LOOSE), [])
        self.assertEqual(D.status_now(c, LOOSE)["state"], "IDLE")

    def test_no_bounce_is_no_event(self):
        rows = shape([], bounce=())
        rows += [(80000 - 10 * i, None) for i in range(12)]
        ev = D.find_events(mk(rows), LOOSE)
        self.assertEqual(ev[-1]["status"], "NO_BOUNCE")

    def test_default_params_do_not_trigger_when_far_from_band(self):
        c = mk(shape([83140, 83180, 83220, 83260]))
        self.assertEqual(D.status_now(c)["state"], "ARMED")   # window open, hold never met at the default 0.5 % band

    def test_future_bars_do_not_change_trigger(self):
        c = mk(shape([83140, 83180, 83220, 83260, 90000, 70000]))
        t = D.find_events(c, LOOSE)[0]["trigger"]
        t2 = D.find_events(c[:t + 1], LOOSE)[0]["trigger"]
        self.assertEqual(t, t2)


class Flow(unittest.TestCase):
    def test_delta_sum(self):
        c = [dict(v=10.0, tbv=7.0), dict(v=10.0, tbv=2.0)]
        self.assertEqual(D.delta_sum(c, 0, 1), 4 + -6)

    def test_report_runs_offline(self):
        c = mk(shape([83140, 83180, 83220, 83260]))
        r = S.report(c, (93670.0, 12.0), LOOSE)
        self.assertEqual(r["state"], "ACTIVE")
        self.assertEqual(r["oi_now"], 93670.0)
        self.assertIn("episode_cvd_change", r)


if __name__ == "__main__":
    unittest.main()
