"""Tests for strategies.py (BT_SPEC "strategies.py"): R1 weekend strangle, R2 covered call, R4 cash-secured put, S7 long
straddle on tiny synthetic panels built in a temp dir. Every expected pnl_btc is hand-computed from the spec's rules:
pnl = premium received - premium paid - payoffs - fees; inverse payoff max(0,S-K)/S (call) | max(0,K-S)/S (put);
trade fee min(0.0003, 0.125*price) per leg; delivery fee min(0.00015, 0.125*payoff) only when ITM on a Friday expiry."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import HOUR, DAY, ms, tr  # noqa: E402

import panel as P  # noqa: E402
import strategies as SG  # noqa: E402
from instruments import ms_to_ymd  # noqa: E402

IDX = 80000.0
IV = 50.0


# ---------------------------------------------------------------------------------------------------------------
# adapters: the only code that knows how the implementation is called
def _d(x, is_end=False):
    """tests give epoch ms with an exclusive end; the engine takes YYYY-MM-DD with an inclusive end date."""
    if isinstance(x, str) or x is None:
        return x
    return ms_to_ymd(x - 1 if is_end else x)


def run_strangle(panel, hist, start, end, delta, **kw):
    return SG.weekend_strangle(panel, start=_d(start), end=_d(end, True), delta=delta, **kw)


def run_cc(panel, hist, start, end, delta, tenor_days, **kw):
    return SG.covered_call(panel, start=_d(start), end=_d(end, True), delta=delta, tenor_days=tenor_days, **kw)


def run_csp(panel, hist, start, end, delta, tenor_days, **kw):
    return SG.cash_secured_put(panel, start=_d(start), end=_d(end, True), delta=delta, tenor_days=tenor_days, **kw)


def run_long_straddle(panel, hist, start, end, tenor_days, **kw):
    return SG.long_straddle(panel, start=_d(start), end=_d(end, True), tenor_days=tenor_days, **kw)


def unpack(res):
    """-> (trades, skipped)"""
    return res


# ---------------------------------------------------------------------------------------------------------------
class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.trades_dir = self.root / "hist" / "trades"
        self.hist = self.root / "hist"

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, rows, delivery, extra_csv=None):
        U.write_shards(self.trades_dir, rows)
        U.write_delivery(self.hist, delivery)
        return P.Panel(self.trades_dir)

    def assertTradeBasics(self, t, expiry_ms, spot_exit):
        self.assertEqual(t["exit_ts"], expiry_ms)                       # spec: exit_ts = expiry
        self.assertAlmostEqual(t["spot_exit"], spot_exit, places=6)    # settlement = delivery_prices.csv value
        self.assertAlmostEqual(t["spot_entry"], IDX, places=6)         # every print in the fixture carries index 80000
        self.assertLess(t["entry_ts"], t["exit_ts"])

    def legs_by_name(self, t):
        return {leg["name"]: leg for leg in t["legs"]}


# ---------------------------------------------------------------------------------------------------------------
# R1 weekend strangle: Friday 2026-10-09 16:00 UTC decision, expiry Sunday 2026-10-11 08:00 (a "daily": no delivery fee)
FRI = ms(2026, 10, 9, 16)
SUN_EXP = ms(2026, 10, 11, 8)
P78, C82 = "BTC-11OCT26-78000-P", "BTC-11OCT26-82000-C"
START_W, END_W = ms(2026, 10, 5), ms(2026, 10, 12)


def strangle_rows(put_fill=True, call_fill=True, strikes_calls=(80000, 82000, 84000), strikes_puts=(76000, 78000, 80000)):
    rows = []
    t_obs = FRI - 4 * HOUR
    for k in strikes_calls:
        rows.append(tr(t_obs, "BTC-11OCT26-%d-C" % k, "buy", 0.0050, iv=IV, index=IDX))
    for k in strikes_puts:
        rows.append(tr(t_obs, "BTC-11OCT26-%d-P" % k, "buy", 0.0050, iv=IV, index=IDX))
    rows.append(tr(FRI - 1, P78, "sell", 0.0100, amount=5.0, index=IDX))                 # print BEFORE the decision: lookahead bait
    rows.append(tr(FRI + 60000, P78, "buy", 0.0200, amount=5.0, index=IDX))               # wrong taker side for a seller
    rows.append(tr(FRI + 120000, C82, "sell", 0.0090, amount=5.0, index=IDX, block_trade_id="BLK-1"))   # block: excluded
    if put_fill:
        rows.append(tr(FRI + 5 * 60000, P78, "sell", 0.0040, amount=1.0, index=IDX))       # the fill: put sold at 0.0040
    if call_fill:
        rows.append(tr(FRI + 10 * 60000, C82, "sell", 0.0020, amount=2.0, index=IDX))      # the fill: call sold at 0.0020
    return rows


class WeekendStrangle(Base):
    def go(self, settle, **rows_kw):
        p = self.build(strangle_rows(**rows_kw), {"2026-10-11": settle})
        return unpack(run_strangle(p, self.hist, START_W, END_W, 0.25))

    def test_otm_both_legs_pnl_is_premium_minus_entry_fees(self):
        trades, skipped = self.go(80500.0)
        self.assertEqual(len(trades), 1, (trades, skipped))
        t = trades[0]
        self.assertTradeBasics(t, SUN_EXP, 80500.0)
        legs = self.legs_by_name(t)
        self.assertEqual(set(legs), {P78, C82})                                  # 0.25 delta: 78000 put (0.222), 82000 call (0.238)
        self.assertEqual(legs[P78]["side"], "sell")
        self.assertEqual(legs[C82]["side"], "sell")
        self.assertAlmostEqual(legs[P78]["entry_px"], 0.0040, places=12)         # not the 0.0100 pre-decision or the buy-side print
        self.assertAlmostEqual(legs[C82]["entry_px"], 0.0020, places=12)         # not the block print 0.0090
        self.assertAlmostEqual(legs[P78]["fee_entry"], 0.0003, places=12)        # min(0.0003, 0.125*0.0040=0.0005)
        self.assertAlmostEqual(legs[C82]["fee_entry"], 0.00025, places=12)       # cap case: 0.125*0.0020 < 0.0003
        for leg in legs.values():
            self.assertAlmostEqual(leg["payoff_btc"], 0.0, places=12)
            self.assertAlmostEqual(leg["fee_delivery"], 0.0, places=12)
        self.assertAlmostEqual(t["pnl_btc"], 0.0040 + 0.0020 - 0.0003 - 0.00025, places=12)   # 0.00545
        self.assertEqual(skipped, [])

    def test_put_finishes_itm_sunday_has_no_delivery_fee(self):
        trades, _ = self.go(70000.0)
        t = trades[0]
        legs = self.legs_by_name(t)
        self.assertAlmostEqual(legs[P78]["payoff_btc"], 8000.0 / 70000.0, places=12)       # (78000-70000)/70000
        self.assertAlmostEqual(legs[P78]["fee_delivery"], 0.0, places=12)                  # Sunday expiry = daily
        self.assertAlmostEqual(legs[C82]["payoff_btc"], 0.0, places=12)
        self.assertAlmostEqual(t["pnl_btc"], 0.0060 - 0.00055 - 8000.0 / 70000.0, places=12)   # -0.1088357143

    def test_call_finishes_itm(self):
        trades, _ = self.go(90000.0)
        t = trades[0]
        self.assertAlmostEqual(self.legs_by_name(t)[C82]["payoff_btc"], 8000.0 / 90000.0, places=12)   # (90000-82000)/90000
        self.assertAlmostEqual(t["pnl_btc"], 0.0060 - 0.00055 - 8000.0 / 90000.0, places=12)           # -0.0834388889

    def test_strike_exactly_at_settlement_is_otm(self):
        trades, _ = self.go(78000.0)
        self.assertAlmostEqual(trades[0]["pnl_btc"], 0.0060 - 0.00055, places=12)

    def test_no_instrument_when_nothing_is_near_the_target_delta(self):
        rows = strangle_rows(strikes_calls=(90000, 95000), strikes_puts=(60000, 65000))   # |delta| ~0 : all rejected (>0.10 away)
        p = self.build(rows, {"2026-10-11": 80500.0})
        trades, skipped = unpack(run_strangle(p, self.hist, START_W, END_W, 0.25))
        self.assertEqual(trades, [])
        self.assertEqual([s["reason"] for s in skipped], ["no_instrument"])

    def test_no_fill_when_nobody_buys_into_our_offer(self):
        rows = [r for r in strangle_rows(put_fill=False, call_fill=False)]
        p = self.build(rows, {"2026-10-11": 80500.0})
        trades, skipped = unpack(run_strangle(p, self.hist, START_W, END_W, 0.25))
        self.assertEqual(trades, [])                                             # only lookahead bait / wrong side / block exist
        self.assertEqual([s["reason"] for s in skipped], ["no_fill"])

    def test_insufficient_size_is_no_fill(self):
        rows = strangle_rows(put_fill=False)
        rows.append(tr(FRI + 5 * 60000, P78, "sell", 0.0040, amount=0.5, index=IDX))      # 0.5 < 1.0 contract
        p = self.build(rows, {"2026-10-11": 80500.0})
        trades, skipped = unpack(run_strangle(p, self.hist, START_W, END_W, 0.25))
        self.assertEqual(trades, [])
        self.assertEqual([s["reason"] for s in skipped], ["no_fill"])

    def test_one_leg_not_filled_means_no_strangle(self):
        p = self.build(strangle_rows(call_fill=False), {"2026-10-11": 80500.0})
        trades, skipped = unpack(run_strangle(p, self.hist, START_W, END_W, 0.25))
        self.assertEqual(trades, [])
        self.assertEqual([s["reason"] for s in skipped], ["no_fill"])

    def test_lookahead_bait_would_change_the_answer(self):
        # If the pre-decision 0.0100 print (or the buy-side 0.0200 print) were used, pnl would differ visibly.
        trades, _ = self.go(80500.0)
        self.assertLess(trades[0]["pnl_btc"], 0.0100)

    def test_only_one_decision_in_the_week_is_made(self):
        trades, skipped = self.go(80500.0)
        self.assertEqual(len(trades) + len(skipped), 1)                          # Fri 16:00 only (dow_entry=4, hour=16)


# ---------------------------------------------------------------------------------------------------------------
# R2 covered call: delta 0.25, tenor 6 days. Decision 1: Fri 2026-10-02 09:00 -> 9OCT26 (Fri, 167 h); roll at expiry+1h
D1 = ms(2026, 10, 2, 9)
EXP1 = ms(2026, 10, 9, 8)
D2 = ms(2026, 10, 9, 9)
EXP2 = ms(2026, 10, 16, 8)
C84_9, C84_16 = "BTC-9OCT26-84000-C", "BTC-16OCT26-84000-C"


def cc_rows(is_call=True):
    cp = "C" if is_call else "P"
    rows = []
    ks = (80000, 82000, 84000, 86000, 88000) if is_call else (72000, 74000, 76000, 78000, 80000)
    for k in ks:                                                       # obs before decision 1 (expiry 9OCT26)
        rows.append(tr(D1 - 3 * HOUR, "BTC-9OCT26-%d-%s" % (k, cp), "buy", 0.004, iv=IV, index=IDX))
    for k in ks:                                                       # obs before decision 2 (expiry 16OCT26)
        rows.append(tr(D2 - 3 * HOUR, "BTC-16OCT26-%d-%s" % (k, cp), "buy", 0.004, iv=IV, index=IDX))
    return rows


class CoveredCall(Base):
    def rows(self):
        rows = cc_rows()
        rows.append(tr(D1 + 30 * 60000, C84_9, "sell", 0.0030, amount=1.0, index=IDX))     # roll 1 premium 0.0030
        rows.append(tr(D1 - 60000, C84_9, "sell", 0.0300, amount=9.0, index=IDX))          # lookahead bait
        rows.append(tr(D2 + 30 * 60000, C84_16, "sell", 0.0016, amount=1.0, index=IDX))    # roll 2 premium 0.0016
        return rows

    def go(self, s1, s2, start=ms(2026, 10, 2), end=ms(2026, 10, 10), rows=None, **kw):
        p = self.build(rows if rows is not None else self.rows(), {"2026-10-09": s1, "2026-10-16": s2})
        return unpack(run_cc(p, self.hist, start, end, 0.25, 6, **kw))

    def test_two_rolls_itm_friday_pays_delivery_fee_then_otm_roll(self):
        trades, skipped = self.go(90000.0, 80000.0)
        self.assertEqual(len(trades), 2, (trades, skipped))
        a, b = trades
        self.assertTradeBasics_roll(a, D1, EXP1, 90000.0)
        self.assertTradeBasics_roll(b, D2, EXP2, 80000.0)
        la, lb = a["legs"], b["legs"]
        self.assertEqual(len(la), 1)
        self.assertEqual((la[0]["name"], la[0]["side"]), (C84_9, "sell"))
        self.assertAlmostEqual(la[0]["entry_px"], 0.0030, places=12)
        self.assertAlmostEqual(la[0]["fee_entry"], 0.0003, places=12)             # min(0.0003, 0.000375)
        self.assertAlmostEqual(la[0]["payoff_btc"], 6000.0 / 90000.0, places=12)  # (90000-84000)/90000
        self.assertAlmostEqual(la[0]["fee_delivery"], 0.00015, places=12)         # Friday ITM: min(0.00015, 0.125*0.0667)
        self.assertAlmostEqual(a["pnl_btc"], 0.0030 - 0.0003 - 6000.0 / 90000.0 - 0.00015, places=12)   # -0.0641166667
        self.assertEqual((lb[0]["name"], lb[0]["side"]), (C84_16, "sell"))
        self.assertAlmostEqual(lb[0]["fee_entry"], 0.0002, places=12)             # cap case: 0.125*0.0016
        self.assertAlmostEqual(lb[0]["payoff_btc"], 0.0, places=12)
        self.assertAlmostEqual(lb[0]["fee_delivery"], 0.0, places=12)
        self.assertAlmostEqual(b["pnl_btc"], 0.0016 - 0.0002, places=12)           # 0.0014

    def assertTradeBasics_roll(self, t, entry_floor, expiry, spot_exit):
        self.assertEqual(t["exit_ts"], expiry)
        self.assertGreaterEqual(t["entry_ts"], entry_floor)                       # fills only at/after the decision
        self.assertAlmostEqual(t["spot_exit"], spot_exit, places=6)
        self.assertAlmostEqual(t["spot_entry"], IDX, places=6)

    def test_otm_delivery_has_no_fee_and_second_roll_starts_one_hour_after_expiry(self):
        trades, _ = self.go(80000.0, 80000.0)
        self.assertAlmostEqual(trades[0]["pnl_btc"], 0.0030 - 0.0003, places=12)
        self.assertGreaterEqual(trades[1]["entry_ts"], EXP1 + HOUR)               # roll = expiry (08:00) + 1h

    def test_small_itm_delivery_fee_is_12_5_percent_of_payoff_cap_case(self):
        s = 84400.0                                                              # payoff 400/84400 = 0.004739..; 12.5% = 0.000592 > 0.00015
        trades, _ = self.go(s, 80000.0)
        self.assertAlmostEqual(trades[0]["legs"][0]["fee_delivery"], 0.00015, places=12)
        s = 84100.0                                                              # payoff 100/84100 = 0.001189; 12.5% = 0.0001486 < 0.00015
        trades, _ = self.go(s, 80000.0)
        self.assertAlmostEqual(trades[0]["legs"][0]["fee_delivery"], 0.125 * 100.0 / 84100.0, places=12)

    def test_no_fill_roll_is_skipped_and_reported(self):
        rows = [r for r in self.rows() if not (r["instrument_name"] == C84_16 and r["direction"] == "sell")]
        trades, skipped = self.go(90000.0, 80000.0, rows=rows)
        self.assertEqual(len(trades), 1)
        self.assertEqual([s["reason"] for s in skipped], ["no_fill"])

    def test_dvol_filter_trades_only_when_previous_day_close_above_90d_mean(self):
        def dvol(prev_close, today_close):
            rows = []
            for i in range(100, 2, -1):                                          # 100 daily candles up to 2026-09-30, then 10-01, 10-02
                d = D1 - i * DAY - 9 * HOUR
                rows.append((d, 50, 50, 50, 50))
            rows.append((ms(2026, 10, 1), 50, 50, 50, prev_close))                # previous day: known at 09:00 of 10-02
            rows.append((ms(2026, 10, 2), 50, 50, 50, today_close))               # stamped 10-02 00:00: closes AFTER the decision
            U.write_csv(self.hist / "dvol_1d.csv", ("ts_ms", "open", "high", "low", "close"), rows)

        p = self.build(self.rows(), {"2026-10-09": 90000.0, "2026-10-16": 80000.0})
        dvol(80, 20)                                                              # above the mean, today's candle must not be used
        trades_hi, _ = unpack(run_cc(p, self.hist, ms(2026, 10, 2), ms(2026, 10, 3), 0.25, 6, dvol_filter=True))
        self.assertEqual(len(trades_hi), 1)
        dvol(20, 80)                                                              # below the mean (a lookahead would trade)
        trades_lo, skipped_lo = unpack(run_cc(P.Panel(self.trades_dir), self.hist, ms(2026, 10, 2), ms(2026, 10, 3), 0.25, 6,
                                              dvol_filter=True))
        self.assertEqual(trades_lo, [])
        self.assertEqual(len(skipped_lo), 1)


# ---------------------------------------------------------------------------------------------------------------
class CashSecuredPut(Base):
    P76_9, P76_16 = "BTC-9OCT26-76000-P", "BTC-16OCT26-76000-P"

    def test_put_roll_itm_friday(self):
        rows = cc_rows(is_call=False)
        rows.append(tr(D1 + 30 * 60000, self.P76_9, "sell", 0.0030, amount=1.0, index=IDX))
        rows.append(tr(D2 + 30 * 60000, self.P76_16, "sell", 0.0016, amount=1.0, index=IDX))
        p = self.build(rows, {"2026-10-09": 70000.0, "2026-10-16": 80000.0})
        trades, skipped = unpack(run_csp(p, self.hist, ms(2026, 10, 2), ms(2026, 10, 10), 0.25, 6))
        self.assertEqual(len(trades), 2, (trades, skipped))
        leg = trades[0]["legs"][0]
        self.assertEqual((leg["name"], leg["side"]), (self.P76_9, "sell"))
        self.assertAlmostEqual(leg["payoff_btc"], 6000.0 / 70000.0, places=12)    # (76000-70000)/70000
        self.assertAlmostEqual(leg["fee_delivery"], 0.00015, places=12)
        self.assertAlmostEqual(trades[0]["pnl_btc"], 0.0030 - 0.0003 - 6000.0 / 70000.0 - 0.00015, places=12)
        self.assertAlmostEqual(trades[1]["pnl_btc"], 0.0016 - 0.0002, places=12)


# ---------------------------------------------------------------------------------------------------------------
class LongStraddle(Base):
    def test_buy_atm_straddle_holds_to_friday_expiry(self):
        c80, p80 = "BTC-9OCT26-80000-C", "BTC-9OCT26-80000-P"
        rows = [tr(D1 - 3 * HOUR, c80, "sell", 0.0135, iv=IV, index=IDX), tr(D1 - 3 * HOUR, p80, "sell", 0.0135, iv=IV, index=IDX),
                tr(D1 + 20 * 60000, c80, "buy", 0.0135, amount=1.0, index=IDX),        # we BUY: need taker 'buy' prints
                tr(D1 + 25 * 60000, p80, "buy", 0.0135, amount=1.0, index=IDX)]
        p = self.build(rows, {"2026-10-09": 84000.0})
        trades, skipped = unpack(run_long_straddle(p, self.hist, ms(2026, 10, 2), ms(2026, 10, 3), 6))
        self.assertEqual(len(trades), 1, (trades, skipped))
        t = trades[0]
        legs = self.legs_by_name(t)
        self.assertEqual({k: v["side"] for k, v in legs.items()}, {c80: "buy", p80: "buy"})
        self.assertAlmostEqual(legs[c80]["payoff_btc"], 4000.0 / 84000.0, places=12)
        self.assertAlmostEqual(legs[c80]["fee_delivery"], 0.00015, places=12)
        self.assertAlmostEqual(legs[p80]["payoff_btc"], 0.0, places=12)
        # pays 0.027 premium + 2*0.0003 entry fees, receives 4000/84000, pays the 0.00015 delivery fee on the ITM call
        self.assertAlmostEqual(t["pnl_btc"], 4000.0 / 84000.0 - 0.027 - 0.0006 - 0.00015, places=12)   # 0.0198690476


if __name__ == "__main__":
    unittest.main()
