"""Tests for selection.pick_by_delta (BT_SPEC "selection"): delta targeting from last_obs, expiry/type filters, staleness,
no-lookahead and the max_dev rejection. Expected deltas come from bt_testutil's independent erf-based Black-76."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import HOUR, YEAR_MS, ms, tr  # noqa: E402

import panel as P  # noqa: E402
import selection as S  # noqa: E402

TS = ms(2026, 10, 7, 16, 0)                 # decision: Wed 16:00 UTC
EXP = ms(2026, 10, 9, 8, 0)                 # BTC-9OCT26-*: Fri 08:00 UTC, 40 h later
T_YRS = (EXP - TS) / YEAR_MS
F = 80000.0


def inst(strike, cp, day="9OCT26"):
    return "BTC-%s-%d-%s" % (day, strike, cp)


def d(strike, is_call, iv=50.0, idx=F):
    return U.ref_abs_delta(idx, strike, iv, T_YRS, is_call)


class PickByDelta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "trades"

    def tearDown(self):
        self.tmp.cleanup()

    def panel(self, rows):
        U.write_shards(self.dir, rows)
        return P.Panel(self.dir)

    def obs(self, strike, cp, iv=50.0, idx=F, ts=None, day="9OCT26"):
        return tr(TS - HOUR if ts is None else ts, inst(strike, cp, day), "sell", 0.005, iv=iv, index=idx)

    def chain(self):
        rows = []
        for k in (76000, 78000, 80000, 81000, 82000, 84000):
            rows.append(self.obs(k, "C"))
        for k in (76000, 78000, 80000):
            rows.append(self.obs(k, "P"))
        return rows

    def test_reference_deltas_are_what_this_file_assumes(self):
        # guards the hand design below (hard-coded from an independent calc, 7 digits)
        self.assertAlmostEqual(d(82000, True), 0.237632, places=5)
        self.assertAlmostEqual(d(78000, False), 0.221769, places=5)
        self.assertAlmostEqual(d(81000, True), 0.362877, places=5)

    def test_call_nearest_abs_delta_wins(self):
        p = self.panel(self.chain())
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25), inst(82000, "C"))     # 0.2376 vs 0.3629 / 0.0768
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.50), inst(80000, "C"))     # 0.5067
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.08), inst(84000, "C"))     # 0.0768

    def test_put_uses_absolute_delta(self):
        p = self.panel(self.chain())
        self.assertEqual(S.pick_by_delta(p, TS, EXP, False, 0.22), inst(78000, "P"))    # |0.2218|
        self.assertEqual(S.pick_by_delta(p, TS, EXP, False, 0.50), inst(80000, "P"))    # |0.4933|

    def test_type_and_expiry_filters(self):
        rows = self.chain() + [
            self.obs(82000, "C", day="10OCT26"),     # perfect-delta strike but a different expiry
            self.obs(83000, "P"),                    # a put at a strike that would be nearest for a CALL target ~0.15
        ]
        p = self.panel(rows)
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25), inst(82000, "C"))     # 9OCT26, not 10OCT26
        got = S.pick_by_delta(p, TS, EXP, True, 0.15)
        self.assertTrue(got.endswith("-C") and "9OCT26" in got, got)
        self.assertEqual(S.pick_by_delta(p, TS, ms(2026, 10, 10, 8), True, 0.25), inst(82000, "C", "10OCT26"))

    def test_rejects_when_nearest_is_further_than_max_dev(self):
        p = self.panel([self.obs(84000, "C")])                                  # only |delta| 0.0768 available
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.50))              # dev 0.42 > 0.10
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.50, max_dev=0.5), inst(84000, "C"))
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.15), inst(84000, "C"))   # dev 0.0732 <= 0.10

    def test_max_dev_boundary_default_is_ten_delta_points(self):
        p = self.panel([self.obs(81000, "C")])                                  # delta 0.3629
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.25))              # dev 0.1129 > 0.10
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25, max_dev=0.12), inst(81000, "C"))
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.30), inst(81000, "C"))   # dev 0.0629

    def test_no_live_instrument_gives_none(self):
        p = self.panel([self.obs(82000, "C", ts=TS - 12 * HOUR)])               # last print 12 h old, default lookback 6 h
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.25))

    def test_lookback_is_honoured(self):
        p = self.panel([self.obs(82000, "C", ts=TS - 12 * HOUR)])
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25, lookback_ms=24 * HOUR), inst(82000, "C"))

    def test_iv_from_last_obs_drives_delta(self):
        # 82000 call at iv 100 has |delta| 0.370 while at iv 50 it is 0.238; the 80000 call (0.507) is the rival.
        rows = [self.obs(80000, "C", iv=50.0), self.obs(82000, "C", iv=100.0)]
        p = self.panel(rows)
        self.assertAlmostEqual(d(82000, True, iv=100.0), 0.3701, places=3)
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.42), inst(82000, "C"))     # 0.370 (dev .05) beats 0.507 (dev .087)
        # same strikes, but the 82000 print now carries iv 50 (delta 0.238): the 80000 call is the only candidate in range
        other = Path(self.tmp.name) / "trades2"
        U.write_shards(other, [self.obs(80000, "C", iv=50.0), self.obs(82000, "C", iv=50.0)])
        p2 = P.Panel(other)
        self.assertEqual(S.pick_by_delta(p2, TS, EXP, True, 0.42), inst(80000, "C"))    # 0.507 (dev .087) beats 0.238 (dev .182)

    def test_index_from_last_obs_drives_delta(self):
        # same strike/iv, but the print was taken when the index was 70000 => the call is far OTM => tiny delta
        p = self.panel([self.obs(82000, "C", idx=70000.0)])
        self.assertLess(d(82000, True, idx=70000.0), 0.01)
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.25))

    def test_latest_obs_before_ts_is_used_not_an_older_one(self):
        rows = [self.obs(82000, "C", idx=70000.0, ts=TS - 5 * HOUR),            # stale quote: delta ~0
                self.obs(82000, "C", idx=F, ts=TS - 10 * 60000)]                # latest: delta 0.2376
        p = self.panel(rows)
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25), inst(82000, "C"))

    def test_no_lookahead_future_obs_cannot_change_or_create_a_pick(self):
        rows = [self.obs(82000, "C", ts=TS - HOUR), self.obs(81000, "C", ts=TS - HOUR),
                self.obs(82000, "C", idx=70000.0, ts=TS + HOUR),               # after the decision: would kill the 82000 call
                self.obs(84000, "C", ts=TS + 2 * HOUR)]                        # first seen after the decision
        p = self.panel(rows)
        self.assertEqual(S.pick_by_delta(p, TS, EXP, True, 0.25), inst(82000, "C"))
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.08))              # 84000 (delta 0.077) did not exist yet

    def test_ignores_block_and_combo_obs(self):
        rows = [self.obs(81000, "C"),
                tr(TS - HOUR, inst(82000, "C"), "sell", 0.005, iv=50.0, index=F, block_trade_id="B")]
        p = self.panel(rows)
        self.assertIsNone(S.pick_by_delta(p, TS, EXP, True, 0.25))              # only 81000 (dev 0.113) is a legit candidate


if __name__ == "__main__":
    unittest.main()
