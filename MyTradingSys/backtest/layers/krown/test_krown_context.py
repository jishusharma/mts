"""krown_context tests. Expected numbers are hand values from FORMULAS.md (section 1 RSI, section 12 ATR, 21.5 BBWP, 21.7 RSI period 2),
computed independently of the code. The no-lookahead tests (PRE_REG_S1_COUNTS.md s2) include a deliberately leaking join and a
deliberately leaking row builder that the point-in-time checks MUST flag."""
import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_context as kx  # noqa: E402
import krown_core as kc  # noqa: E402

HERE = Path(__file__).parent
MON = 1641168000000          # 2022-01-03 00:00 UTC, a Monday (2022-01-01 = 1640995200000 plus 2 days)
D = kx.DAY_MS


def tape(n, seed=1, t0=MON, p0=100.0):
    """Deterministic daily random walk with weekly jumps so swings, zones and ranges exist. Lists t,o,h,l,c,v."""
    rng = random.Random(seed)
    t, o, h, l, c, v = [], [], [], [], [], []
    px = p0
    for i in range(n):
        r = rng.gauss(0, 0.012) + (0.05 * rng.choice([-1, 1]) if i % 9 == 0 else 0)
        o_, c_ = px, px * (1 + r)
        hi = max(o_, c_) * (1 + abs(rng.gauss(0, 0.005)))
        lo = min(o_, c_) * (1 - abs(rng.gauss(0, 0.005)))
        t.append(t0 + i * D)
        o.append(o_), h.append(hi), l.append(lo), c.append(c_), v.append(100 + rng.random() * 50)
        px = c_
    return t, o, h, l, c, v


def small_params(**kw):
    return dict(kc.load_params(), **kw)


class TestHandNumbers(unittest.TestCase):
    def test_atr_plain_sma_formulas_12(self):
        # FORMULAS.md section 12: highs [10,11,12,11], lows [9,9,10,9], closes [9.5,10.5,11.5,10], period 3 -> 2.1667
        a = kx.atr_sma([10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10], 3)
        self.assertAlmostEqual(a[3], (2 + 2 + 2.5) / 3, places=4)
        self.assertIsNone(a[2])

    def test_bbwp_21_5_row_value(self):
        # FORMULAS.md 21.5: basis=2, lookback=3, closes [10,10,12,11,15,15,14] -> BBWP[4]=100, BBWP[5]=0, BBWP[6]=33.3333
        cl = [10, 10, 12, 11, 15, 15, 14]
        n = len(cl)
        rows = kx.build_daily_rows([MON + i * D for i in range(n)], cl, [x + 1 for x in cl], [x - 1 for x in cl], cl, [1.0] * n,
                                   small_params(bbwp_basis=2, bbwp_lookback=3))
        self.assertAlmostEqual(rows[4]["bbwp_1d_ours"], 100.0, places=4)
        self.assertAlmostEqual(rows[5]["bbwp_1d_ours"], 0.0, places=4)
        self.assertAlmostEqual(rows[6]["bbwp_1d_ours"], 100.0 / 3, places=4)

    def test_rsi_21_7_row_value(self):
        # FORMULAS.md 21.7: period 2, closes [10,11,10,12] -> RSI[2]=50, RSI[3]=100-100/6=83.3333
        cl = [10, 11, 10, 12]
        rows = kx.build_daily_rows([MON + i * D for i in range(4)], cl, cl, cl, cl, [1.0] * 4, small_params(rsi_period=2))
        self.assertAlmostEqual(rows[2]["rsi_1d_ours"], 50.0, places=4)
        self.assertAlmostEqual(rows[3]["rsi_1d_ours"], 100 - 100 / 6, places=4)
        self.assertEqual(rows[3]["rsi_zone_1d_ours"], "bull")

    def test_week_start_and_weekly_rebuild(self):
        self.assertEqual(kx.week_start_ms(MON), MON)
        self.assertEqual(kx.week_start_ms(MON + 6 * D + 3600_000), MON)          # Sunday 01:00 stays in the Monday week
        self.assertEqual(kx.week_start_ms(MON + 7 * D), MON + 7 * D)
        n = 15                                                                    # 2 full weeks + 1 day
        t = [MON + i * D for i in range(n)]
        h = [10 + i for i in range(n)]
        l = [5 + i for i in range(n)]
        c = [7 + i for i in range(n)]
        wt, wo, wh, wl, wc = kx.weekly_from_daily(t, c, h, l, c)
        self.assertEqual(wt, [MON, MON + 7 * D])
        self.assertEqual((wh[0], wl[0], wc[0]), (16, 5, 13))                      # days 0..6: max h 10+6, min l 5, last c 7+6
        self.assertEqual((wh[1], wl[1], wc[1]), (23, 12, 20))

    def test_aggregate_4h_drops_incomplete_bucket(self):
        H = 3600_000
        t = [i * H for i in range(9)]                                             # buckets 0-3, 4-7 complete; 8 alone
        o = list(range(9))
        r = kx.aggregate_4h(t, o, [x + 10 for x in o], [x - 10 for x in o], [x + 0.5 for x in o])
        self.assertEqual(r[0], [0, 4 * H])
        self.assertEqual((r[1][0], r[2][0], r[3][0], r[4][0]), (0, 13, -10, 3.5))

    def test_mde_hand(self):
        # z(0.975)=1.959964, +0.84 = 2.799964; x sd 1.5 / sqrt(100) = 0.419995
        self.assertAlmostEqual(kx.z_holm(1), 1.959964, places=4)
        self.assertAlmostEqual(kx.mde_mean(100, 100), 2.799964 * 1.5 / 10, places=4)
        # 100 events in 20 weeks, rho 0.1: deff 1.4
        self.assertAlmostEqual(kx.mde_mean(100, 20), 0.419995 * 1.4 ** 0.5, places=4)
        self.assertAlmostEqual(kx.mde_slope(100, 100, 2.0), 0.419995 / 2.0, places=4)


class TestDimensions(unittest.TestCase):
    def test_d1_table(self):
        f = kx.d1_direction
        self.assertEqual(f(1, 1, 1), 1)
        self.assertEqual(f(1, 1, 0), 0)
        self.assertEqual(f(1, 0, 1), 0)
        self.assertEqual(f(1, 0, 0), 0)               # REVIEW_OPUS F17: both range -> 0
        self.assertEqual(f(1, 1, -1), -1)
        self.assertEqual(f(-1, 1, 1), -1)
        self.assertEqual(f(-1, -1, 0), 0)
        self.assertEqual(f(-1, -1, -1), 1)
        self.assertIsNone(f(1, None, 1))

    def test_d2_fade_and_breakout(self):
        g = kx.d2_regime
        # exhausted: bbwp 90, expansion ran down (-1), event long (+1) -> fade +1, breakout -1
        self.assertEqual(g(kx.FADE, 1, 90, 60, -1), 1)
        self.assertEqual(g(kx.BREAKOUT, 1, 90, 60, -1), -1)
        # fresh: min of last 6 was 20, now 70, expansion up (+1), event long -> fade -1, breakout +1
        self.assertEqual(g(kx.FADE, 1, 70, 20, 1), -1)
        self.assertEqual(g(kx.BREAKOUT, 1, 70, 20, 1), 1)
        # fresh expansion DOWN against a long: fade -1, breakout -1 (review finding 7); a short breakout with it: +1
        self.assertEqual(g(kx.FADE, 1, 70, 20, -1), -1)
        self.assertEqual(g(kx.BREAKOUT, 1, 70, 20, -1), -1)
        self.assertEqual(g(kx.BREAKOUT, -1, 70, 20, -1), 1)
        # neither
        self.assertEqual(g(kx.FADE, 1, 60, 55, 1), 0)
        # both (bbwp 90 after a base of 20, expansion against the event side) -> 0
        self.assertEqual(g(kx.FADE, 1, 90, 20, -1), 0)
        self.assertIsNone(g(kx.FADE, 1, None, None, None))

    def test_d3_zone_edge_middle(self):
        zones = [("L", 90.0, 100.0), ("H", 130.0, 140.0)]
        atr = 10.0
        self.assertEqual(kx.d3_location(1, 104.0, zones, atr, None, None), 1)         # 4 below 5 = 0.5 ATR from the support zone
        self.assertEqual(kx.d3_location(1, 105.5, zones, atr, None, None), 0)         # 5.5 away, no range
        self.assertEqual(kx.d3_location(-1, 104.0, zones, atr, None, None), 0)        # support zone is the wrong side for a short
        self.assertEqual(kx.d3_location(-1, 126.0, zones, atr, None, None), 1)
        # range 100..200: price 150 is mid-range -> -1; 110 (pos 0.1) is the low edge -> long +1; short at 110 -> 0 (pos < 1/3)
        self.assertEqual(kx.d3_location(1, 150.0, [], atr, 200.0, 100.0), -1)
        self.assertEqual(kx.d3_location(1, 110.0, [], atr, 200.0, 100.0), 1)
        self.assertEqual(kx.d3_location(-1, 110.0, [], atr, 200.0, 100.0), 0)
        self.assertIsNone(kx.d3_location(1, 110.0, [], None, 200.0, 100.0))

    def test_zone_string_roundtrip(self):
        z = [{"kind": "L", "lo": 1.5, "hi": 2.25}, {"kind": "H", "lo": 7.0, "hi": 8.0}]
        self.assertEqual(kx.parse_zones(kx._zones_str(z)), [("L", 1.5, 2.25), ("H", 7.0, 8.0)])
        self.assertEqual(kx.parse_zones(""), [])


class TestJoinNoLookahead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t, cls.o, cls.h, cls.l, cls.c, cls.v = tape(420)
        cls.rows = kx.build_daily_rows(cls.t, cls.o, cls.h, cls.l, cls.c, cls.v)
        # decision times: bar open + tf for 15m, 1h, 4h, 1d events, including the exact close / close+latency boundaries
        rng = random.Random(7)
        cls.decisions = [MON + rng.randrange(60 * D, 419 * D, 900_000) for _ in range(300)]
        cls.decisions += [r["open_ms"] + D for r in cls.rows[100:140]]                 # exactly at a daily close
        cls.decisions += [r["available_at"] for r in cls.rows[100:140]]                # exactly at close + latency
        cls.decisions += [r["available_at"] + 1 for r in cls.rows[100:140]]

    def pairs(self, **kw):
        return [(d, kx.join_row(self.rows, d, **kw)) for d in self.decisions]

    def test_real_join_passes(self):
        self.assertEqual(kx.check_point_in_time(self.pairs()), [])

    def test_boundary_is_strict(self):
        r = self.rows[200]
        self.assertIsNot(kx.join_row(self.rows, r["available_at"]), r)                 # available_at == decision_ts: not usable
        self.assertIs(kx.join_row(self.rows, r["available_at"] + 1), r)
        # a 1d event decided at the close of day i sees day i-1, never day i (close + 1 min latency): F17
        dts = r["open_ms"] + D
        self.assertEqual(kx.join_row(self.rows, dts)["open_ms"], r["open_ms"] - D)

    def test_shifted_join_leaks(self):
        """A join keyed on bar OPEN (so the bar still forming is used) MUST fail the point-in-time check."""
        opens = [r["open_ms"] for r in self.rows]
        leaky = self.pairs(availability=opens)
        bad = kx.check_point_in_time(leaky)
        self.assertGreater(len(bad), 100, "the leaking join was not flagged")
        # and it really changes the answer: for most decisions the leaking join picks a later row than the real one
        later = sum(1 for (d, a), (_, b) in zip(self.pairs(), leaky) if b is not None and a is not None and b["open_ms"] > a["open_ms"])
        self.assertGreater(later, 100)

    def test_row_shifted_one_bar_forward_leaks(self):
        """Context row shifted one bar forward in time (row i joined where row i-1 is allowed) MUST fail the check."""
        keys = [r["available_at"] for r in self.rows]
        shifted_keys = [keys[0] - D] + keys[:-1]                                       # row i claims row i-1's availability
        bad = kx.check_point_in_time([(d, kx.join_row(self.rows, d, availability=shifted_keys)) for d in self.decisions])
        self.assertGreater(len(bad), 100)

    def test_truncation_equals_full_history(self):
        """Recompute the row for decision time t from data truncated at t: equal to the full-history row (PRE_REG s2.2)."""
        for i in (140, 199, 260, 333, 419):
            sub = kx.build_daily_rows(self.t[:i + 1], self.o[:i + 1], self.h[:i + 1], self.l[:i + 1], self.c[:i + 1], self.v[:i + 1])
            self.assertEqual(sub[i], self.rows[i], "daily row %d depends on bars after it" % i)

    def test_truncation_catches_a_leaking_builder(self):
        """A builder that peeks one bar ahead (trend of the NEXT bar) must differ from its truncated recomputation."""
        def leaky_rows(n):
            r = kx.build_daily_rows(self.t[:n], self.o[:n], self.h[:n], self.l[:n], self.c[:n], self.v[:n])
            for i in range(n - 1):
                r[i] = dict(r[i], trend_1d_ours=r[i + 1]["trend_1d_ours"], close_1d=r[i + 1]["close_1d"])
            return r
        full = leaky_rows(420)
        caught = 0
        for i in (140, 199, 260, 333):
            if leaky_rows(i + 1)[i] != full[i]:
                caught += 1
        self.assertGreaterEqual(caught, 3)

    def test_h4_truncation(self):
        rng = random.Random(3)
        n = 400
        t = [i * kx.H4_MS for i in range(n)]
        c = [100.0]
        for _ in range(n - 1):
            c.append(c[-1] * (1 + rng.gauss(0, 0.01)))
        full = kx.build_h4_rows(t, c, c, c, c)
        for i in (150, 220, 399):
            sub = kx.build_h4_rows(t[:i + 1], c[:i + 1], c[:i + 1], c[:i + 1], c[:i + 1])
            self.assertEqual(sub[i], full[i])
        self.assertEqual(full[10]["available_at"], t[10] + kx.H4_MS + kx.LATENCY_MS)

    def test_available_at_is_close_plus_latency(self):
        """A builder that forgot the write latency (or used the open) would pass the boundary tests, so pin the formula (review finding 10)."""
        for r in self.rows[:60]:
            self.assertEqual(r["available_at"], r["open_ms"] + kx.DAY_MS + kx.LATENCY_MS)
        self.assertEqual(kx.LATENCY_MS, 60_000)

    def test_price_lookup_uses_last_closed_15m_bar(self):
        import run_counts as rc
        c15 = {900_000 * k: 100.0 + k for k in range(0, 40)}
        ctx = rc.Ctx([], [], c15)
        # decision at 10:00 grid point k=40*... use k=20 (5h): the bar closing exactly then opened at k=19
        self.assertEqual(ctx.price(900_000 * 20), 119.0)
        self.assertEqual(ctx.price(900_000 * 20 + 1), 119.0)                  # a mid-bar decision still uses the bar that closed before
        self.assertEqual(ctx.price(900_000 * 21 - 1), 119.0)

    def test_planted_leak_lint_on_sources(self):
        """No join in the shipped code may bisect on bar-open keys: `availability=` is a test-only argument."""
        for name in ("krown_context.py", "run_counts.py"):
            f = HERE / name
            if not f.exists():
                continue
            src = f.read_text(encoding="utf-8")
            body = src.split("def join_row", 1)[-1] if name == "krown_context.py" else src
            if name == "run_counts.py":
                self.assertNotIn("availability=", src, name)
                self.assertNotIn("availability_keys(", src.replace("kx.availability_keys", ""), name)
            self.assertIn("available_at", body)


if __name__ == "__main__":
    unittest.main()