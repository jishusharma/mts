"""Spec-derived tests for the Fabio v3 layer (written BEFORE the implementation exists).

Spec: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md, v3.1. Comments "spec :N" in T01-T50 and X01-X03 cite
v3.0 line numbers (git HEAD before v3.1); the test ids (spec section 10) are the stable reference. T51-T64 are v3.1.
Every expected number below was re-derived by hand from spec sections 2-6; none comes from repo code.
Tests import ONLY from MyTradingSys.backtest.layers.fabio.fabio_v3 (which re-exports fabio_v3_signals and
fabio_v3_exec). The module being absent is a hard ImportError, never a skip.

Contract: names, argument names, defaults and result keys the implementation has to meet ("+" = new or changed in v3.1):
  signals : atr(bars,i,N)  build_profile(bars,a,i,bin_size)  value_area(profile,bin_size)
            lvn_levels(profile,bin_size)  select_lvn(lvns,s,X,O,c)  balance(bars,i,N,k_bal,bin_size=)
            pressure(bars,i,N,p,q=0.25,k_bal=,bin_size=)  effort_result(bars,i,L=,z_hi=,r_abs=,r_ctl=)
            volume_tier(today_vol,prior_vols,min_days=10)  big_push(bars,i,m,s,tier="99")
            breakout(bars,i,N,k_bal,p,m,tier="99",bin_size=)  control_level(bars,ctrl,a,i,s)  curve(bars,i,sess_open,bin_size=)
          + exhaustion(bars,i,trade,k_bal=,tier=,bin_size=,z_hi=2.5,p=0.10,climax=False)  trade = {"s","e_i","lvl"}
          + failed_auction(bars,i,N,k_bal,p,m,absorbed,tier="99",bin_size=)->{"s","lvl","edge"}|None
          + defended_level(bars,absorbed,a,i,s)->price|None
  exec    : FEE_MAKER FEE_TAKER TICK  find_fill(bars,i,s,price,tick=0.1,end_idx=None)->(j,price)|None
            leg_r(s,q,e,x,entry_kind,exit_kind,r_unit,slip_bps=0.0)->{gross_r,fee_r,slip_r,net_r}
            be_update(s,e1,D,stop,ext,be_k=1.0)  trail_update(s,stop,lvl,c,tick=0.1)
          + add_size(s,legs,stop,pa,q1,budget=0.0)
          + add_allowed(s,e1,stop,n_adds,i,open_idx,control,push_ok,curve_state,add_mode="be",s7=True)  (max 2 adds)
          + opp_stop(s,e1,stop,pb,c,tick=0.1)
          + simulate_trade(bars,fill_idx,s,entry,D,stop,q1=,entry_kind=,be_k=,ctrl=,tick=,end_idx=,target=,slip_bps=,
                           mgmt="dist",absorbed=None,s8_kw=None)
            trade dict: {entry,D,stop0,stop,exit,reason,gross_r,fee_r,net_r,fill_idx,exit_idx,target,moves}
            moves = [(i, new_stop, kind)], kind in "be" "trail" "opp" "own"; stop-exit reason = kind of the last move
            ("stop" if none); other reasons "s8" "target" "window_end"; target None when the trade has none
  v3      : + model_a_trade(bars,k,s,O,lvn,f,dmax,ctrl=None,end_idx=None,mgmt="dist",absorbed=None)
          + model_b(bars,start_idx,balance,absorbed,f,dmax,entry_mode="rest",end_idx=None,target_mode="edge",ctrl=None,
                    mgmt="dist")                                                    target_mode "edge" | "trail"
          + model_c(bars,open_idx,ib_len,m,f,dmax,entry_mode="rest",tier="99",gate_open=True,ctrl=None,end_idx=None,
                    mgmt="dist",absorbed=None)
          + model_d_trade(bars,k,s,edge,lvl,f,dmax,entry_mode="rest",ctrl=None,absorbed=None,end_idx=None,mgmt="dist")
            models -> {"arms","fills","missed_winners","trades":[trade dicts as above]}
          + ny_open_utc(date)->aware UTC datetime|None (None on weekends and on the spec's US_CLOSED dates)
          + london_open_utc(date)->aware UTC datetime|None
            entry_allowed(i,open_idx)  window_bars(bars,date)->list|None
          + aggregate_day_r(days,trades)  (a day sums risk_u*net_r; risk_u default 1.0)
          + first_leg_allowed(closed_nets,n_first_legs=0,carry=0.0)  first_leg_risk(closed_nets,n_first_legs=0,carry=0.0)
            day_gate_open(elapsed,day_range,prior_ranges,g)  day_type(bars)  sample_size(sd,delta)  ci_halfwidth(sd,n)
"""
import ast
import datetime as dt
import math
import random
import statistics
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import fabio_v3 as V

FABIO_DIR = Path(__file__).resolve().parent
MIN = 60000
COLS = ["t", "o", "h", "l", "c", "buy_vol", "sell_vol", "delta", "cvd_day", "n_agg", "n_trades", "max_trade",
        "b99_buy_vol", "b99_sell_vol", "b99_buy_n", "b99_sell_n",
        "b999_buy_vol", "b999_sell_vol", "b999_buy_n", "b999_sell_n",
        "thr99", "thr999", "thr_days", "poc_price", "poc_delta", "poc_vol", "fp", "cvd"]


def mk(i, o=100.0, h=None, l=None, c=None, buy=0.0, sell=0.0, fp=None, b99=(0.0, 0.0), b999=(0.0, 0.0),
       thr_days=30, t=None):
    """Plain-dict bar with the orderflow_bars.py columns; unset volumes are 0."""
    c = o if c is None else c
    h = max(o, c) if h is None else h
    l = min(o, c) if l is None else l
    if fp is None:
        fp = "%d:%s:%s" % (int(math.floor(c)), float(buy), float(sell))
    b = {k: 0.0 for k in COLS}
    b.update({"t": (i * MIN if t is None else t), "o": float(o), "h": float(h), "l": float(l), "c": float(c),
              "buy_vol": float(buy), "sell_vol": float(sell), "delta": float(buy) - float(sell),
              "b99_buy_vol": float(b99[0]), "b99_sell_vol": float(b99[1]),
              "b999_buy_vol": float(b999[0]), "b999_sell_vol": float(b999[1]),
              "thr_days": thr_days, "fp": fp})
    return b


def f1():
    """Fixture F1 (spec :231-239), bin 1.0, TICK 0.1."""
    rows = [(100, 101, 99, 100, 5, 5, "100:5:5"), (100, 102, 99, 101, 6, 4, "100:6:4"),
            (101, 102, 100, 100, 3, 7, "100:3:7"), (100, 101, 99, 100, 4, 6, "99:4:6"),
            (100, 101, 99, 100.5, 3, 7, "100:3:7"), (100, 100.5, 98, 98.5, 2, 8, "98:2:8")]
    bars = [mk(i, o=o, h=h, l=l, c=c, buy=bu, sell=se, fp=fp) for i, (o, h, l, c, bu, se, fp) in enumerate(rows)]
    bars[5]["b99_sell_vol"] = 3.0
    bars[5]["b99_buy_vol"] = 0.0
    return bars


def eff_bars(prev_d, prev_r, d, r):
    """Bars 0..3 carry prev_d / prev_r, bar 4 carries d / r (L = 4 tests)."""
    out = []
    for i, (pd_, pr) in enumerate(zip(prev_d, prev_r)):
        out.append(mk(i, o=100.0, c=100.0 + pr, buy=max(pd_, 0), sell=max(-pd_, 0)))
    out.append(mk(len(prev_d), o=100.0, c=100.0 + r, buy=max(d, 0), sell=max(-d, 0)))
    return out


def calm(n, buy_sell=(1.0, 0.0), b99=(0.0, 0.0)):
    """Flat balance bars: range 1, ATR 1, close at the POC centre of the single profile bin (bin 1.0)."""
    return [mk(i, o=100.5, h=101.0, l=100.0, c=100.5, buy=buy_sell[0], sell=buy_sell[1], fp="100:1.0:0.0",
               b99=b99) for i in range(n)]


def alt_bars(n, b99=(1.0, 0.0)):
    """Alternating bars: even j o 100 c 100.5 buy 1 (d +1, r +0.5); odd j o 100.5 c 100 sell 1 (d -1, r -0.5)."""
    out = []
    for j in range(n):
        if j % 2 == 0:
            out.append(mk(j, o=100.0, c=100.5, buy=1, b99=b99))
        else:
            out.append(mk(j, o=100.5, c=100.0, sell=1, b99=b99))
    return out


def rand_series(seed=12345, n=600):
    """Same generator as test_T49 (contiguous random bars with footprint and big-trade columns)."""
    rng = random.Random(seed)
    bars, px = [], 100.0
    for i in range(n):
        o = px
        c = o + rng.gauss(0.0, 0.5)
        h = max(o, c) + abs(rng.gauss(0.0, 0.2))
        l = min(o, c) - abs(rng.gauss(0.0, 0.2))
        buy, sell = float(rng.randint(0, 10)), float(rng.randint(0, 10))
        bins = sorted({int(math.floor(o)), int(math.floor(c))})
        fp = "|".join("%d:%s:%s" % (k, float(rng.randint(0, 5)), float(rng.randint(0, 5))) for k in bins)
        bars.append(mk(i, o=o, h=h, l=l, c=c, buy=buy, sell=sell, fp=fp,
                       b99=(float(rng.randint(0, 3)), float(rng.randint(0, 3))),
                       b999=(float(rng.randint(0, 2)), float(rng.randint(0, 2)))))
        px = c
    return bars


class TestFabioV3(unittest.TestCase):
    def ap(self, a, b, places=6):
        self.assertAlmostEqual(a, b, places=places)

    # ---------------------------------------------------------------- ATR / S1 / S2
    def test_T01_atr(self):
        # spec :241 TR1=max(3,2,1)=3, TR2=TR3=TR4=2 -> (3+2+2+2)/4 = 2.25 (plain SMA of TR)
        self.ap(V.atr(f1(), 4, 4), 2.25)

    def test_T02_atr_undefined(self):
        # spec :242 / :39 needs i >= N
        self.assertIsNone(V.atr(f1(), 3, 4))

    def test_T03_balance_true(self):
        # spec :243 H 102, L 99, R 3, limit 0.8*2*2.25 = 3.6, profile {99:10, 100:30} poc 100.5
        r = V.balance(f1(), 4, 4, 0.8, bin_size=1.0)
        self.assertIsNotNone(r)
        self.ap(r["H"], 102.0)
        self.ap(r["L"], 99.0)
        self.ap(r["R"], 3.0)
        self.ap(r["poc"], 100.5)

    def test_T04_balance_range_too_wide(self):
        # spec :244 k_bal 0.6 -> limit 2.7 < R 3
        self.assertIsNone(V.balance(f1(), 4, 4, 0.6, bin_size=1.0))

    def test_T05_balance_poc_band(self):
        # spec :245 c[4] = 99.7: |99.7-100.5| = 0.8 > 0.25*3 = 0.75
        bars = f1()
        bars[4]["c"] = 99.7
        self.assertIsNone(V.balance(bars, 4, 4, 0.8, bin_size=1.0))

    def test_T06_pressure(self):
        # spec :247-248 sum d = 2-4-2-4 = -8, sum v = 40, P = -0.2; drift 0.5/3 = 0.1667 <= 0.25
        self.assertEqual(V.pressure(f1(), 4, 4, 0.10, k_bal=0.8, bin_size=1.0), -1)

    def test_T07_pressure_threshold(self):
        # spec :249 p 0.25 > |P| 0.2
        self.assertEqual(V.pressure(f1(), 4, 4, 0.25, k_bal=0.8, bin_size=1.0), 0)

    def test_T08_pressure_drift(self):
        # spec :250 o[1] = 99.5 -> drift 1.0/3 = 0.333 > 0.25; S1 still true
        bars = f1()
        bars[1]["o"] = 99.5
        self.assertIsNotNone(V.balance(bars, 4, 4, 0.8, bin_size=1.0))
        self.assertEqual(V.pressure(bars, 4, 4, 0.10, k_bal=0.8, bin_size=1.0), 0)

    # ---------------------------------------------------------------- S4 / S5 / tier
    def test_T09_big_push(self):
        # spec :251 bar 5 b99 sell 3, buy 0: net(i;1) = -3; s*net > 0 for s=-1 only
        bars = f1()
        self.assertIs(V.big_push(bars, 5, 1, -1, tier="99"), True)
        self.assertIs(V.big_push(bars, 5, 1, +1, tier="99"), False)
        # tier 999 reads the b999 columns, which are 0 here -> net 0 -> False for both sides
        self.assertIs(V.big_push(bars, 5, 1, -1, tier="999"), False)

    def test_T10_breakout(self):
        # spec :252 S2(4) = -1, c[5] 98.5 < L(i-1) 99, S4 true -> -1
        self.assertEqual(V.breakout(f1(), 5, 4, 0.8, 0.10, 1, tier="99", bin_size=1.0), -1)

    def test_T11_T12_breakout_negatives(self):
        # spec :253 (T11) c[5] = 99.2 is not outside L=99 -> 0; (T12) b99 buy 3 / sell 0 -> net +3 -> 0
        bars = f1()
        bars[5]["c"] = 99.2
        self.assertEqual(V.breakout(bars, 5, 4, 0.8, 0.10, 1, tier="99", bin_size=1.0), 0)
        bars = f1()
        bars[5]["b99_buy_vol"], bars[5]["b99_sell_vol"] = 3.0, 0.0
        self.assertEqual(V.breakout(bars, 5, 4, 0.8, 0.10, 1, tier="99", bin_size=1.0), 0)

    def test_T13_adaptive_tier(self):
        # spec :254-256 prior volumes [150,250,200] -> median 200; 300/200 = 1.5 -> "999"; 290/200 = 1.45 -> "99"
        prior = [150.0, 250.0, 200.0]
        self.assertEqual(V.volume_tier(300.0, prior, min_days=3), "999")
        self.assertEqual(V.volume_tier(290.0, prior, min_days=3), "99")
        # two prior days (below min 3) -> "99"; default min 10 -> "99" even for huge volume
        self.assertEqual(V.volume_tier(300.0, [150.0, 250.0], min_days=3), "99")
        self.assertEqual(V.volume_tier(9999.0, prior), "99")

    # ---------------------------------------------------------------- S3
    def test_T14_effort_absorbed(self):
        # spec :257-258 e = (3-0)/1 = 3, res = (0-0)/0.5 = 0 -> absorbed +1
        bars = eff_bars([1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5], 3, 0.0)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": 0, "absorbed": 1})

    def test_T15_effort_control(self):
        # spec :259 r = 1.0 -> res 2.0 >= 1.0 -> control +1
        bars = eff_bars([1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5], 3, 1.0)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": 1, "absorbed": 0})

    def test_T16_effort_against(self):
        # spec :260 r = -0.5 -> res -1 <= 0.25 -> absorbed +1, no control
        bars = eff_bars([1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5], 3, -0.5)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": 0, "absorbed": 1})

    def test_T17_effort_control_sell(self):
        # spec :260 d = -3, r = -1.0 -> e -3, res -2 -> control -1
        bars = eff_bars([1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5], -3, -1.0)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": -1, "absorbed": 0})

    def test_T18_effort_in_between(self):
        # spec :261 d = 3, r = 0.25 -> res 0.5: above r_abs 0.25, below r_ctl 1.0 -> {0, 0}
        bars = eff_bars([1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5], 3, 0.25)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": 0, "absorbed": 0})

    def test_T19_effort_zero_sd(self):
        # spec :261-262 previous d all 1 -> pstdev 0 -> z None -> {0, 0}
        bars = eff_bars([1, 1, 1, 1], [0.5, -0.5, 0.5, -0.5], 3, 0.0)
        self.assertEqual(V.effort_result(bars, 4, L=4, z_hi=2.5), {"control": 0, "absorbed": 0})

    # ---------------------------------------------------------------- S6 / S7 / profile
    def test_T20_control_level(self):
        # spec :263-264
        bars = [mk(i, o=100.0, h=101.0, l=99.0) for i in range(15)]
        bars[11]["h"], bars[12]["h"], bars[13]["h"] = 105.0, 104.0, 103.0
        ctrl = [0] * 15
        ctrl[11], ctrl[12], ctrl[13] = -1, +1, -1
        self.ap(V.control_level(bars, ctrl, 10, 14, -1), 103.0)
        self.ap(V.control_level(bars, ctrl, 10, 12, -1), 105.0)
        self.assertIsNone(V.control_level(bars, ctrl, 10, 10, -1))
        # mirror, long: only ctrl[11] = +1 (l 95) -> 95 at i = 14; ctrl[12] = -1 is ignored for s = +1
        bars2 = [mk(i, o=100.0, h=101.0, l=99.0) for i in range(15)]
        bars2[11]["l"] = 95.0
        ctrl2 = [0] * 15
        ctrl2[11], ctrl2[12] = +1, -1
        self.ap(V.control_level(bars2, ctrl2, 10, 14, +1), 95.0)

    @staticmethod
    def _va_profile_bars(last_close):
        # spec :265 profile {100:10, 110:20, 120:40, 130:15, 140:5, 150:10}, bin 10, one fp bin per bar
        fps = ["100:5:5", "110:10:10", "120:20:20", "130:8:7", "140:3:2", "150:5:5"]
        bars = [mk(i, o=125.0, h=126.0, l=124.0, c=125.0, fp=fp) for i, fp in enumerate(fps)]
        bars[5]["c"] = last_close
        return bars

    def test_T21_value_area_and_curve(self):
        # spec :265-267 POC 120 (acc 40); up 15+5 = 20 < dn 20+10 = 30 -> take 110, 100 -> acc 70 >= 70
        bars = self._va_profile_bars(125.0)
        prof = V.build_profile(bars, 0, 5, 10.0)
        self.assertEqual({float(k): v for k, v in prof.items()},
                         {100.0: 10.0, 110.0: 20.0, 120.0: 40.0, 130.0: 15.0, 140.0: 5.0, 150.0: 10.0})
        va = V.value_area(prof, 10.0)
        self.ap(va["VAL"], 100.0)
        self.ap(va["VAH"], 130.0)
        self.ap(va["poc_center"], 125.0)
        for c, want in ((135.0, "premium"), (99.0, "discount"), (115.0, "fair"), (130.0, "fair")):
            self.assertEqual(V.curve(self._va_profile_bars(c), 5, 0, bin_size=10.0), want, c)

    def test_T22_value_area_tie_goes_up(self):
        # spec :268-269 {100:10,110:30,120:10}: total 50, target 35; POC 110; up 10 == dn 10 -> take above
        va = V.value_area({100.0: 10.0, 110.0: 30.0, 120.0: 10.0}, 10.0)
        self.ap(va["VAL"], 110.0)
        self.ap(va["VAH"], 130.0)

    def test_T23_lvn(self):
        # spec :270-272 bin 10, med (upper) 20, cut 10 -> LVNs at 120 and 140 -> centres 125, 145
        prof = {100.0: 30.0, 110.0: 25.0, 120.0: 5.0, 130.0: 20.0, 140.0: 4.0, 150.0: 30.0, 160.0: 10.0}
        self.assertEqual([float(x) for x in sorted(V.lvn_levels(prof, 10.0))], [125.0, 145.0])

    def test_T24_lvn_star(self):
        # spec :273-274 long, O 100, X 165: retrace threshold 16.25; both pass; nearest to X is 145
        self.ap(V.select_lvn([125.0, 145.0], +1, 165.0, 100.0, 160.0), 145.0)
        # c = 140: 145 is not below the close -> 125
        self.ap(V.select_lvn([125.0, 145.0], +1, 165.0, 100.0, 140.0), 125.0)

    # ---------------------------------------------------------------- S8
    @staticmethod
    def _s8_bars(n, net_by_bar):
        bars = calm(n)
        for j, (bu, se) in net_by_bar.items():
            bars[j]["b99_buy_vol"], bars[j]["b99_sell_vol"] = float(bu), float(se)
        return bars

    def test_T25_exhaustion_a(self):
        # spec :275-277 window of net(i;15) is [i-14, i]. Entry e_i = 60 (bars before it are padding), so that
        # (b) i-59 > e_i is false and (c) (no control on flat bars) is false: only (a) can fire.
        trade = {"s": 1, "e_i": 60, "lvl": 100.0}
        kw = dict(k_bal=0.8, tier="99", bin_size=1.0)
        # i=80 (age 20), window 66..80 sums -1 (bar 65 is outside the window: +10 must be ignored)
        bars = self._s8_bars(81, {70: (0, 1), 65: (10, 0)})
        self.assertIs(V.exhaustion(bars, 80, trade, **kw), True)
        # sum 0 -> True (<= 0)
        bars = self._s8_bars(81, {70: (1, 1), 65: (10, 0)})
        self.assertIs(V.exhaustion(bars, 80, trade, **kw), True)
        # sum +1 -> False
        bars = self._s8_bars(81, {70: (1, 0)})
        self.assertIs(V.exhaustion(bars, 80, trade, **kw), False)
        # age 14 (i = 74): not yet evaluated even though the sum is -1 (bar 59 is outside [60,74])
        bars = self._s8_bars(81, {70: (0, 1), 59: (10, 0)})
        self.assertIs(V.exhaustion(bars, 74, trade, **kw), False)
        # age 15 (i = 75): window 61..75 sums -1 -> True
        self.assertIs(V.exhaustion(bars, 75, trade, **kw), True)

    def test_T26_exhaustion_c_reversal(self):
        # spec :278 bars 0..59 alternate d +1/-1 and r +0.5/-0.5 (L=60: mean 0, pstdev 1 and 0.5); bar 60 has
        # d = -3 (e = -3) and r = -1.0 (res = -2): S3 control -1. Entry e_i = 55 -> (a) age 5, (b) false.
        def series(o_i, c_i, h_i, l_i):
            bars = []
            for j in range(60):
                if j % 2 == 0:
                    bars.append(mk(j, o=100.0, c=100.5, buy=1, sell=0))
                else:
                    bars.append(mk(j, o=100.5, c=100.0, buy=0, sell=1))
            bars.append(mk(60, o=o_i, h=h_i, l=l_i, c=c_i, buy=0, sell=3))
            return bars
        trade = {"s": 1, "e_i": 55, "lvl": 101.0}
        kw = dict(k_bal=0.8, tier="99", bin_size=1.0)
        self.assertIs(V.exhaustion(series(101.9, 100.9, 102.0, 100.8), 60, trade, **kw), True)
        # c == lvl is not a break (strict <)
        self.assertIs(V.exhaustion(series(102.0, 101.0, 102.1, 100.9), 60, trade, **kw), False)

    def test_X02_exhaustion_b_redistribution(self):
        # v3.1 (spec S8(b), section 10 X02; changed from v3.0, which expected True for e_i = 10): a new balance exits
        # only if it favours the other side. Calm bars (buy 1 / sell 0) give S2 = +1 over the new balance, which favours
        # the long -> hold. Positive big flow keeps (a) false; flat bars have no S3 events, so (c) is false.
        bars = calm(81, b99=(1.0, 0.0))
        kw = dict(k_bal=0.8, tier="99", bin_size=1.0)
        self.assertIs(V.exhaustion(bars, 80, {"s": 1, "e_i": 10, "lvl": 100.0}, **kw), False)   # balance favours us
        self.assertIs(V.exhaustion(bars, 80, {"s": 1, "e_i": 30, "lvl": 100.0}, **kw), False)   # 21 > 30 no

    # ---------------------------------------------------------------- fills
    def test_T27_fill_through(self):
        # spec :278-280 (:121-124) sell fills iff h >= P+TICK, buy iff l <= P-TICK, fill price = P
        def one(s, price, h, l):
            return V.find_fill([mk(0), mk(1, o=100.0, h=h, l=l, c=100.0)], 0, s, price, tick=0.1)
        self.assertEqual(one(-1, 100.0, 100.1, 99.0), (1, 100.0))
        self.assertIsNone(one(-1, 100.0, 100.05, 99.0))
        self.assertIsNone(one(-1, 100.0, 100.0, 99.0))
        r = one(+1, 104.0, 105.0, 103.9)
        self.assertEqual(r[0], 1)
        self.ap(r[1], 104.0)
        self.assertIsNone(one(+1, 104.0, 105.0, 103.95))

    def test_T28_limit_live_from_next_bar(self):
        # spec :121-122 armed at close of bar 0; bar 0 itself trades through the limit -> no fill there
        bars = [mk(0, o=100.0, h=101.0, l=99.0, c=100.5), mk(1, o=100.5, h=102.0, l=101.0, c=101.5)]
        self.assertIsNone(V.find_fill(bars, 0, +1, 100.0, tick=0.1))
        bars[1]["l"] = 99.8
        self.assertEqual(V.find_fill(bars, 0, +1, 100.0, tick=0.1)[0], 1)

    # ---------------------------------------------------------------- costs
    def test_T29_cost_r(self):
        # spec :289-291 (:144-150) fees on the entry notional; R unit = q1*D1 = 300
        self.assertEqual(V.FEE_MAKER, 0.0)
        self.assertEqual(V.FEE_TAKER, 0.0005)
        self.ap(V.TICK, 0.1)
        r = V.leg_r(-1, 1.0, 100000.0, 100300.0, "maker", "taker", 300.0)
        self.ap(r["gross_r"], -1.0)
        self.ap(r["fee_r"], 0.0005 * 100000.0 / 300.0)        # 0.166667
        self.ap(r["net_r"], -1.166667)
        r = V.leg_r(-1, 1.0, 100000.0, 100300.0, "taker", "taker", 300.0)
        self.ap(r["fee_r"], 0.333333)
        self.ap(r["net_r"], -1.333333)
        # slippage 2 bps per taker leg = 0.0002*100000/300 = 0.066667 each
        r = V.leg_r(-1, 1.0, 100000.0, 100300.0, "maker", "taker", 300.0, slip_bps=2.0)
        self.ap(r["slip_r"], 0.066667)
        self.ap(r["net_r"], -1.233333)
        r = V.leg_r(-1, 1.0, 100000.0, 100300.0, "taker", "taker", 300.0, slip_bps=2.0)
        self.ap(r["slip_r"], 0.133333)
        self.ap(r["net_r"], -1.466667)

    def test_T30_target_is_maker(self):
        # spec :292 (:143) model B exits at the target as a maker: fee_out 0; maker entry -> no fee at all
        r = V.leg_r(-1, 1.0, 101.5, 99.0, "maker", "maker", 1.6)
        self.ap(r["fee_r"], 0.0)
        # taker entry + maker exit: only the entry leg pays
        r = V.leg_r(-1, 1.0, 101.5, 99.0, "taker", "maker", 1.6)
        self.ap(r["fee_r"], 0.0005 * 101.5 / 1.6)

    # ---------------------------------------------------------------- management
    def test_T31_break_even(self):
        # spec :293-294 long maker e1 100, D 1, stop 99. Bar j+1 (h 101, l 99.5): no stop, BE at close.
        # Bar j+2 (l 99.9, o 100.5): exit at 100.0 "be", gross 0, fee 0.0005*100/1 = 0.05, net -0.05
        bars = [mk(0, o=100.2, h=100.6, l=99.8, c=100.3), mk(1, o=100.2, h=101.0, l=99.5, c=100.6),
                mk(2, o=100.5, h=100.8, l=99.9, c=100.0)]
        t = V.simulate_trade(bars, 0, +1, 100.0, 1.0, 99.0, q1=1.0, entry_kind="maker", be_k=1.0, end_idx=2)
        self.ap(t["exit"], 100.0)
        self.assertEqual(t["reason"], "be")
        self.ap(t["gross_r"], 0.0)
        self.ap(t["fee_r"], 0.05)
        self.ap(t["net_r"], -0.05)
        # unit: the BE helper only tightens
        self.ap(V.be_update(+1, 100.0, 1.0, 99.0, 101.0, be_k=1.0), 100.0)
        self.ap(V.be_update(+1, 100.0, 1.0, 99.0, 100.9, be_k=1.0), 99.0)

    def test_T32_add_sizing(self):
        # spec :295-298 (:137-142) long e1 100, q1 1, D1 1; pa = 104
        legs = [(1.0, 100.0)]
        self.ap(V.add_size(+1, legs, 102.0, 104.0, 1.0), 1.0)          # locked 2, dist 2; P&L at stop 2-2 = 0
        self.ap(V.add_size(+1, legs, 101.0, 104.0, 1.0), 1.0 / 3.0)    # locked 1, dist 3
        self.assertEqual(V.add_size(+1, legs, 100.5, 104.0, 1.0), 0.0)  # 0.5/3.5 = 0.1429 < 0.25 -> no add
        self.assertEqual(V.add_size(+1, legs, 100.0, 104.0, 1.0), 0.0)  # at BE: locked 0 -> no add

    def test_T33_add_gates(self):
        # spec :299-301 base case of T32 (stop 102) is allowed; each gate alone blocks it
        base = dict(s=+1, e1=100.0, stop=102.0, n_adds=0, i=100, open_idx=0, control=+1, push_ok=True,
                    curve_state="fair")
        self.assertIs(V.add_allowed(**base), True)
        self.assertIs(V.add_allowed(**dict(base, curve_state="premium")), False)
        self.assertIs(V.add_allowed(**dict(base, n_adds=3)), False)
        self.assertIs(V.add_allowed(**dict(base, i=330)), False)          # i < open+330 required
        self.assertIs(V.add_allowed(**dict(base, i=329)), True)
        self.assertIs(V.add_allowed(**dict(base, control=0)), False)
        self.assertIs(V.add_allowed(**dict(base, push_ok=False)), False)
        self.assertIs(V.add_allowed(**dict(base, stop=99.0)), False)      # stop not yet at/beyond BE
        # short mirror: discount blocks, premium does not
        sh = dict(s=-1, e1=100.0, stop=98.0, n_adds=0, i=100, open_idx=0, control=-1, push_ok=True,
                  curve_state="fair")
        self.assertIs(V.add_allowed(**sh), True)
        self.assertIs(V.add_allowed(**dict(sh, curve_state="discount")), False)
        self.assertIs(V.add_allowed(**dict(sh, curve_state="premium")), True)

    def test_T34_trail(self):
        # spec :302-304 (:135-136) long, stop 100 after BE; cand = S6 - TICK; needs tighten AND c > cand
        st = V.trail_update(+1, 100.0, 101.0, 102.0)
        self.ap(st, 100.9)
        st = V.trail_update(+1, st, 100.5, 102.0)       # later control bar l 100.5 -> cand 100.4 loosens
        self.ap(st, 100.9)
        self.ap(V.trail_update(+1, st, 102.0, 101.95), 101.9)   # cand 101.9, c 101.95 > cand
        self.ap(V.trail_update(+1, st, 102.0, 101.85), 100.9)   # c 101.85 < cand -> unchanged
        self.ap(V.trail_update(+1, st, None, 105.0), 100.9)     # no S6 level -> unchanged

    @staticmethod
    def _t35_bars(gap):
        b = [mk(0, o=106.0, h=106.5, l=105.5, c=106.0),
             mk(1, o=105.5, h=106.0, l=103.95, c=105.0),
             mk(2, o=105.0, h=105.5, l=103.9, c=105.0),
             mk(3, o=105.0, h=108.2, l=104.5, c=108.0)]
        if gap:
            b.append(mk(4, o=104.0, h=104.5, l=104.0, c=104.2))
        else:
            b.append(mk(4, o=107.0, h=107.5, l=104.3, c=105.0))
        return b

    def test_T35_model_a_end_to_end(self):
        # spec :305-311 (Dmax 5%, f 0.3%): O 100, LVN* 104 armed at close of bar 0 (c 106)
        # structural = 104-100+0.1 = 4.1; fill in bar 2 (l 103.9 <= 103.9; bar 1 l 103.95 no); stop 99.9
        ctrl = [0, 0, 0, 1, 0]
        r = V.model_a_trade(self._t35_bars(False), 0, +1, 100.0, 104.0, 0.003, 0.05, ctrl=ctrl, end_idx=4)
        self.assertEqual((r["arms"], r["fills"]), (1, 1))
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 2)
        self.ap(t["entry"], 104.0)
        self.ap(t["D"], 4.1)
        self.ap(t["stop0"], 99.9)
        # bar 3: ext 108.2 -> fav 4.2 >= 4.1 -> BE stop 104.0; trail cand = l(3) 104.5 - 0.1 = 104.4 -> stop 104.4
        # bar 4 (o 107, l 104.3): exit at 104.4
        self.ap(t["exit"], 104.4)
        self.assertEqual(t["reason"], "trail")
        self.ap(t["gross_r"], 0.4 / 4.1)                      # 0.097561
        self.ap(t["fee_r"], 0.0005 * 104.0 / 4.1)             # 0.012683 (maker entry, taker stop exit)
        self.ap(t["net_r"], 0.084878)
        # gap variant: bar 4 opens at 104.0, below the 104.4 stop -> exit at the open, gross 0
        r = V.model_a_trade(self._t35_bars(True), 0, +1, 100.0, 104.0, 0.003, 0.05, ctrl=ctrl, end_idx=4)
        t = r["trades"][0]
        self.ap(t["exit"], 104.0)
        self.ap(t["gross_r"], 0.0)

    def test_T36_model_a_skip(self):
        # spec :312 Dmax 1.0%: D 4.1 > 1.04 -> setup skipped, no order armed
        r = V.model_a_trade(self._t35_bars(False), 0, +1, 100.0, 104.0, 0.003, 0.01, ctrl=[0, 0, 0, 1, 0], end_idx=4)
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])

    @staticmethod
    def _t37_bars(absorb_bar=5):
        bars = [mk(i, o=100.0, h=101.0, l=99.0, c=100.0) for i in range(5)]
        bars += [mk(5, o=102.0, h=103.0, l=101.8, c=102.5),
                 mk(6, o=102.4, h=102.6, l=101.3, c=101.5),
                 mk(7, o=101.5, h=101.7, l=101.0, c=101.3),
                 mk(8, o=101.3, h=101.8, l=100.0, c=100.2),
                 mk(9, o=100.2, h=100.5, l=98.8, c=99.0)]
        absorbed = [0] * 10
        if absorb_bar is not None:
            absorbed[absorb_bar] = 1
        return bars, absorbed

    def test_T37_model_b_end_to_end(self):
        # spec :313-318 balance H 102 L 99. Bar 5 c 102.5 (outside, absorbed +1) -> PROBE, Xp 103.0.
        # Bar 6 c 101.5 -> RECLAIM, short, rest sell 101.5. Bar 7 h 101.7 >= 101.6 -> fill 101.5,
        # D = max(0.3045, |103.0-101.5|+0.1 = 1.6), stop 103.1, target 99. Bar 8 fav 1.5 < 1.6 (no BE).
        # Bar 9 l 98.8 <= 98.9 -> target fill at 99.0 (maker): gross 2.5/1.6, fees 0.
        bars, absorbed = self._t37_bars()
        r = V.model_b(bars, 5, {"H": 102.0, "L": 99.0}, absorbed, 0.003, 0.05, entry_mode="rest", end_idx=9)
        self.assertEqual((r["arms"], r["fills"]), (1, 1))
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 7)
        self.ap(t["entry"], 101.5)
        self.ap(t["D"], 1.6)
        self.ap(t["stop0"], 103.1)
        self.ap(t["target"], 99.0)
        self.ap(t["exit"], 99.0)
        self.assertEqual(t["reason"], "target")
        self.ap(t["gross_r"], 1.5625)
        self.ap(t["fee_r"], 0.0)
        self.ap(t["net_r"], 1.5625)

    def test_T38_model_b_negatives(self):
        # spec :319 no absorption anywhere in the probe -> no trade
        bars, absorbed = self._t37_bars(absorb_bar=None)
        r = V.model_b(bars, 5, {"H": 102.0, "L": 99.0}, absorbed, 0.003, 0.05, entry_mode="rest", end_idx=9)
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])
        # reclaim at bar 5+6 = 11 (> i+5 = 10): probe times out, no trade even though a sell would fill
        bars = [mk(i, o=100.0, h=101.0, l=99.0, c=100.0) for i in range(5)]
        bars.append(mk(5, o=102.0, h=103.0, l=101.8, c=102.5))
        bars += [mk(j, o=102.5, h=103.0, l=102.2, c=102.6) for j in range(6, 11)]
        bars.append(mk(11, o=102.4, h=102.6, l=101.3, c=101.5))
        bars += [mk(12, o=101.5, h=105.0, l=101.0, c=104.0), mk(13, o=104.0, h=105.0, l=103.0, c=104.0)]
        absorbed = [0] * 14
        absorbed[5] = 1
        r = V.model_b(bars, 5, {"H": 102.0, "L": 99.0}, absorbed, 0.003, 0.05, entry_mode="rest", end_idx=13)
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])

    @staticmethod
    def _ivb_head():
        # IB = bars 0..2 (ib_len 3): h max 105, l min 100 -> mid 102.5
        return [mk(0, o=101.0, h=104.0, l=100.5, c=103.0),
                mk(1, o=103.0, h=105.0, l=101.0, c=104.0),
                mk(2, o=103.0, h=103.5, l=100.0, c=101.0),
                mk(3, o=104.5, h=106.0, l=105.0, c=105.5, b99=(1.0, 0.0))]

    def test_T39_model_c(self):
        # spec :320-323 bar 3 c 105.5 > IBH 105 with S4 +1 -> buy limit 105; bar 4 l 104.9 -> fill 105;
        # D = max(0.315, 105-102.5+0.1 = 2.6) -> stop 102.4
        bars = self._ivb_head() + [
            mk(4, o=105.2, h=105.5, l=104.9, c=105.3),
            mk(5, o=105.3, h=106.0, l=103.0, c=104.0),
            mk(6, o=104.0, h=104.2, l=102.0, c=102.5),       # stop 102.4 hit here
            mk(7, o=102.5, h=103.0, l=102.2, c=103.0),
            mk(8, o=103.0, h=106.5, l=102.8, c=106.0, b99=(1.0, 0.0))]   # second breakout, must be ignored
        r = V.model_c(bars, 0, 3, 1, 0.003, 0.05, entry_mode="rest", tier="99", gate_open=True, end_idx=8)
        self.assertEqual(r["arms"], 1)
        self.assertEqual(len(r["trades"]), 1)
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 4)
        self.ap(t["entry"], 105.0)
        self.ap(t["D"], 2.6)
        self.ap(t["stop0"], 102.4)
        self.ap(t["exit"], 102.4)
        self.ap(t["gross_r"], -1.0)
        # gate closed -> never arms
        r = V.model_c(bars, 0, 3, 1, 0.003, 0.05, entry_mode="rest", tier="99", gate_open=False, end_idx=8)
        self.assertEqual(r["arms"], 0)

    def test_T40_missed_winner(self):
        # spec :324-325 buy limit 105 never fills (lows >= 104.95 > 104.9); D 2.6; 105 + 2*2.6 = 110.2 reached
        def run(top):
            bars = self._ivb_head() + [
                mk(4, o=105.5, h=106.0, l=105.0, c=105.8),
                mk(5, o=105.8, h=107.0, l=104.95, c=106.5),
                mk(6, o=107.0, h=top, l=106.5, c=110.0)]
            return V.model_c(bars, 0, 3, 1, 0.003, 0.05, entry_mode="rest", tier="99", gate_open=True, end_idx=6)
        r = run(110.2)
        self.assertEqual((r["arms"], r["fills"], r["missed_winners"]), (1, 0, 1))
        self.assertEqual(r["trades"], [])
        r = run(110.1)                                   # 110.1 < 110.2: not a missed winner
        self.assertEqual((r["arms"], r["fills"], r["missed_winners"]), (1, 0, 0))

    # ---------------------------------------------------------------- window / day rules
    def test_T41_dst_open(self):
        # spec :326-327 (:32-36) second Sunday March <= D < first Sunday November -> 13:30 UTC else 14:30
        cases = [((2024, 12, 2), (14, 30)), ((2025, 3, 7), (14, 30)), ((2025, 3, 10), (13, 30)),
                 ((2025, 10, 31), (13, 30)), ((2025, 11, 3), (14, 30)), ((2026, 3, 9), (13, 30)),
                 ((2026, 10, 30), (13, 30)), ((2026, 11, 2), (14, 30))]
        for ymd, hm in cases:
            r = V.ny_open_utc(dt.date(*ymd))
            self.assertIsNotNone(r, ymd)
            self.assertEqual((r.hour, r.minute), hm, ymd)
            self.assertEqual(r.date(), dt.date(*ymd), ymd)
        self.assertIsNone(V.ny_open_utc(dt.date(2025, 3, 8)))        # Saturday
        self.assertIsNone(V.ny_open_utc(dt.date(2025, 3, 9)))        # Sunday

    def test_T42_entry_cutoff_and_window_end(self):
        # spec :328-329 (:35) no entry at or after open+330; open+329 allowed
        self.assertIs(V.entry_allowed(330, 0), False)
        self.assertIs(V.entry_allowed(329, 0), True)
        self.assertIs(V.entry_allowed(1000 + 330, 1000), False)
        self.assertIs(V.entry_allowed(1000 + 329, 1000), True)
        # window end: exit at c of the last window bar, taker (long e 100, D 1, no BE: h <= 100.8)
        bars = [mk(0, o=100.0, h=100.5, l=99.8, c=100.2), mk(1, o=100.2, h=100.8, l=99.9, c=100.3),
                mk(2, o=100.3, h=100.8, l=100.0, c=100.4)]
        t = V.simulate_trade(bars, 0, +1, 100.0, 1.0, 99.0, q1=1.0, entry_kind="maker", be_k=1.0, end_idx=2)
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["exit"], 100.4)
        self.ap(t["gross_r"], 0.4)
        self.ap(t["fee_r"], 0.05)                                     # taker exit on entry notional 100
        self.ap(t["net_r"], 0.35)

    def test_T43_day_aggregation(self):
        # spec :330-331 day 1 [-1.2,-1.2,+5.0] -> 2.6; day 2 no trade -> 0; day 3 [-1.2]; mean 0.46667
        days = ["d1", "d2", "d3"]
        trades = [{"day": "d1", "net_r": -1.2}, {"day": "d1", "net_r": -1.2}, {"day": "d1", "net_r": 5.0},
                  {"day": "d3", "net_r": -1.2}]
        out = V.aggregate_day_r(days, trades)
        self.assertEqual(len(out), 3)
        for a, b in zip(out, [2.6, 0.0, -1.2]):
            self.ap(a, b)
        self.ap(statistics.mean(out), 0.466667)

    def test_T44_day_rules(self):
        # spec :332-334 (:157-159) closed net R cumulates: -1.2, -2.4 allowed; -3.6 <= -3 blocked
        self.assertIs(V.first_leg_allowed([]), True)
        self.assertIs(V.first_leg_allowed([-1.2]), True)
        self.assertIs(V.first_leg_allowed([-1.2, -1.2]), True)
        self.assertIs(V.first_leg_allowed([-1.2, -1.2, -1.2]), False)
        self.assertIs(V.first_leg_allowed([-1.5, -1.5]), False)       # exactly -3.0 counts (<= -3)
        # -1.2 then +1.5 -> +0.3 after having been <= -1: no new first legs
        self.assertIs(V.first_leg_allowed([-1.2, 1.5]), False)
        # never reached -1R: recovery rule does not apply
        self.assertIs(V.first_leg_allowed([-0.5, 0.6]), True)
        # max 10 first legs per day
        self.assertIs(V.first_leg_allowed([], n_first_legs=9), True)
        self.assertIs(V.first_leg_allowed([], n_first_legs=10), False)

    def test_T45_day_gate(self):
        # spec :335-336 (:160-163) prior medians [500,450,600] -> 500; range 400 -> G 0.8 (>= 0.8 open)
        prior = [500.0, 450.0, 600.0]
        self.assertIs(V.day_gate_open(100, 400.0, prior, 0.8), True)
        self.assertIs(V.day_gate_open(100, 390.0, prior, 0.8), False)       # 0.78
        self.assertIs(V.day_gate_open(100, 390.0, prior, None), True)       # g off
        self.assertIs(V.day_gate_open(59, 400.0, prior, 0.8), False)        # before open+60 closed
        self.assertIs(V.day_gate_open(60, 400.0, prior, 0.8), True)
        self.assertIs(V.day_gate_open(30, 400.0, prior, None), True)        # g off is always open

    def test_T46_day_type(self):
        # spec :337 (:164) o 100, c 108, h 110, l 99 -> 8/11 = 0.727 >= 0.6 trend; c 103 -> 0.273 balance
        def win(c_last):
            return [mk(0, o=100.0, h=110.0, l=101.0, c=105.0), mk(1, o=105.0, h=106.0, l=99.0, c=c_last)]
        self.assertEqual(V.day_type(win(108.0)), "trend")
        self.assertEqual(V.day_type(win(103.0)), "balance")

    def test_T47_sample_size(self):
        # spec :338-339 (:206-210) n = ((1.96+0.8416)*SD/delta)^2 rounded up
        self.assertEqual(V.sample_size(1.5, 0.2), 442)       # 441.504
        self.assertEqual(V.sample_size(1.82, 0.2), 650)      # 649.97
        self.ap(V.ci_halfwidth(1.5, 30), 0.53677, places=5)

    def test_T48_window_exclusions(self):
        # spec :340 thr_days == 0 days and windows with > 5 missing minutes are excluded (:19-22)
        d = dt.date(2025, 3, 10)                              # Monday, DST: open 13:30 UTC
        open_ms = int(dt.datetime(2025, 3, 10, 13, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)

        def day(missing, thr_days=30):
            bars = []
            for k in range(-10, 400):
                if k in missing:
                    continue
                bars.append(mk(0, o=100.0, c=100.0, t=open_ms + k * MIN, thr_days=thr_days))
            return bars
        w = V.window_bars(day(set()), d)
        self.assertEqual(len(w), 390)
        self.assertEqual(w[0]["t"], open_ms)
        self.assertEqual(w[-1]["t"], open_ms + 389 * MIN)
        self.assertEqual(len(V.window_bars(day(set(range(100, 105))), d)), 385)    # 5 missing: still valid
        self.assertIsNone(V.window_bars(day(set(range(100, 106))), d))            # 6 missing: excluded
        self.assertIsNone(V.window_bars(day(set(), thr_days=0), d))               # own-day thresholds
        self.assertIsNone(V.window_bars(day(set()), dt.date(2025, 3, 9)))         # Sunday: no window

    def test_T49_lookahead_canary(self):
        # spec :341 (:29-30) S1-S8 at i must not change when bars > i are deleted
        rng = random.Random(12345)
        bars, px = [], 100.0
        for i in range(600):                                   # 2 x 300-minute "days", contiguous
            o = px
            c = o + rng.gauss(0.0, 0.5)
            h = max(o, c) + abs(rng.gauss(0.0, 0.2))
            l = min(o, c) - abs(rng.gauss(0.0, 0.2))
            buy, sell = float(rng.randint(0, 10)), float(rng.randint(0, 10))
            bins = sorted({int(math.floor(o)), int(math.floor(c))})
            fp = "|".join("%d:%s:%s" % (k, float(rng.randint(0, 5)), float(rng.randint(0, 5))) for k in bins)
            bars.append(mk(i, o=o, h=h, l=l, c=c, buy=buy, sell=sell, fp=fp,
                           b99=(float(rng.randint(0, 3)), float(rng.randint(0, 3))),
                           b999=(float(rng.randint(0, 2)), float(rng.randint(0, 2)))))
            px = c

        def snapshot(b, i):
            ctrl = [V.effort_result(b, j, L=20, z_hi=1.5)["control"] if j >= 20 else 0 for j in range(i + 1)]
            sess = 0 if i < 300 else 300
            out = [V.atr(b, i, 14), V.balance(b, i, 20, 3.0, bin_size=1.0),
                   V.pressure(b, i, 20, 0.02, k_bal=3.0, bin_size=1.0),
                   V.effort_result(b, i, L=20, z_hi=1.5),
                   V.breakout(b, i, 20, 3.0, 0.02, 5, tier="99", bin_size=1.0),
                   V.curve(b, i, sess, bin_size=1.0)]
            for s in (+1, -1):
                out.append(V.big_push(b, i, 5, s, tier="99"))
                out.append(V.big_push(b, i, 5, s, tier="999"))
                out.append(V.control_level(b, ctrl, i - 10, i, s))
                out.append(V.exhaustion(b, i, {"s": s, "e_i": i - 20, "lvl": b[i - 5]["l"] if s > 0 else b[i - 5]["h"]},
                                        k_bal=3.0, tier="99", bin_size=1.0))
            return out
        for i in rng.sample(range(70, 600), 20):
            self.assertEqual(snapshot(bars, i), snapshot(bars[:i + 1], i), "look-ahead at i=%d" % i)

    def test_T50_isolation(self):
        # spec :342 (:5-6) fabio_v3*.py import only stdlib and orderflow_bars (+ their own siblings):
        # nothing from execution, layers.alerts, Tom/core, and no FEE_* from fabio_of_model
        files = sorted(FABIO_DIR.glob("fabio_v3*.py"))
        names = {p.name for p in files}
        for need in ("fabio_v3.py", "fabio_v3_signals.py", "fabio_v3_exec.py"):
            self.assertIn(need, names)
        bad_parts = {"execution", "alerts", "core", "tom"}
        for p in files:
            tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [(a.name, [a.name]) for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    mods = [(node.module or "", [a.name for a in node.names])]
                for mod, imported in mods:
                    parts = [x.lower() for x in mod.split(".") if x]
                    for x in parts + [n.lower() for n in imported]:
                        self.assertNotIn(x, bad_parts, "%s imports %s" % (p.name, mod))
                        self.assertFalse(x.startswith("tom_"), "%s imports %s" % (p.name, mod))
                    self.assertNotIn("fabio_of_model", parts, "%s imports %s" % (p.name, mod))
                    for n in imported:
                        self.assertFalse(n.startswith("FEE_") and "fabio_of_model" in mod,
                                         "%s imports %s from %s" % (p.name, n, mod))

    # ---------------------------------------------------------------- extra (layout contract, re-binning)
    def test_X01_reexports(self):
        # task layout: fabio_v3 re-exports every public name of fabio_v3_signals and fabio_v3_exec
        from MyTradingSys.backtest.layers.fabio import fabio_v3_exec as E
        from MyTradingSys.backtest.layers.fabio import fabio_v3_signals as S
        for mod in (S, E):
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                obj = getattr(mod, name)
                if isinstance(obj, type(math)):
                    continue
                if callable(obj) and getattr(obj, "__module__", None) != mod.__name__:
                    continue                                     # stdlib / other-module helpers
                self.assertTrue(hasattr(V, name), "%s missing from fabio_v3" % name)
                self.assertIs(getattr(V, name), obj, name)

    def test_X03_profile_rebin(self):
        # spec :25-26, :42 fp bins re-binned to k = floor(binlow/B)*B: with B = 50, bins 100..140 -> 100, 150 -> 150
        bars = self._va_profile_bars(125.0)
        prof = V.build_profile(bars, 0, 5, 50.0)
        self.assertEqual({float(k): v for k, v in prof.items()}, {100.0: 90.0, 150.0: 10.0})


    # ---------------------------------------------------------------- v3.1: event management (spec 5.2)
    def test_T51_opp_stop(self):
        # spec T51: candidates {e1, pb - s*TICK} that are on the right side of the close; best = max_s; only tightens
        self.ap(V.opp_stop(+1, 100.0, 99.0, 99.9, 100.6), 100.0)      # 100.0 vs 99.8 -> BE
        self.ap(V.opp_stop(+1, 100.0, 100.4, 100.8, 101.3), 100.7)    # 100.0 vs 100.7 -> ratchet
        self.ap(V.opp_stop(+1, 100.0, 99.0, 99.5, 99.8), 99.4)        # e1 100 is above the close 99.8 -> 99.4
        self.ap(V.opp_stop(+1, 100.0, 100.7, 100.5, 101.0), 100.7)    # best 100.4 would loosen -> unchanged
        self.ap(V.opp_stop(-1, 100.0, 101.0, 100.3, 99.5), 100.0)     # short: 100.0 vs 100.4 -> min 100.0

    @staticmethod
    def _t53_bars():
        rows = [(100.2, 100.6, 99.8, 100.3), (100.3, 100.8, 99.9, 100.6), (100.6, 101.5, 100.5, 101.4),
                (101.4, 101.6, 101.0, 101.1), (101.1, 101.5, 100.8, 101.3), (101.3, 102.0, 101.2, 101.9),
                (101.9, 102.1, 101.0, 101.5)]
        return [mk(i, o=o, h=h, l=l, c=c) for i, (o, h, l, c) in enumerate(rows)]

    def _moves(self, t, want):
        got = t["moves"]
        self.assertEqual(len(got), len(want), got)
        for (gi, gs, gk), (wi, ws, wk) in zip(got, want):
            self.assertEqual((gi, gk), (wi, wk), got)
            self.ap(gs, ws)

    def test_T52_defended_level(self):
        # spec S9 / T52: last j in (a, i] with absorbed[j] == s -> h[j] (long) / l[j] (short)
        bars = self._t53_bars()
        absb = [0, 0, 0, 1, -1, 0, 0]
        self.ap(V.defended_level(bars, absb, 0, 5, +1), 101.6)
        self.assertIsNone(V.defended_level(bars, absb, 0, 2, +1))
        self.assertIsNone(V.defended_level(bars, absb, 3, 5, +1))      # a is exclusive
        self.ap(V.defended_level(bars, absb, 0, 5, -1), 100.8)

    def test_T53_event_management(self):
        # spec T53: long maker e1 100, D 1, stop 99, fill bar 0.
        # bar 1 E_opp: pb 99.9 -> 100.0 (opp). bar 2 own control: no move. bar 3 E_own: S6 l[2] 100.5 -> 100.4 (own),
        # DL 101.6. bar 4 E_opp: a 2, pb min(101.0, 100.8) -> 100.7 (opp). bar 5 c 101.9 > DL: S6 l[5] 101.2 -> 101.1
        # (trail). bar 6 l 101.0 <= 101.1 -> exit 101.1; gross 1.1, fee 0.0005*100/1 = 0.05, net 1.05
        bars = self._t53_bars()
        ctrl = [0, 0, 1, 0, 0, 1, 0]
        absb = [0, -1, 0, 1, -1, 0, 0]
        t = V.simulate_trade(bars, 0, +1, 100.0, 1.0, 99.0, q1=1.0, entry_kind="maker", be_k=1.0, ctrl=ctrl,
                             end_idx=6, mgmt="event", absorbed=absb)
        self._moves(t, [(1, 100.0, "opp"), (3, 100.4, "own"), (4, 100.7, "opp"), (5, 101.1, "trail")])
        self.assertEqual(t["exit_idx"], 6)
        self.ap(t["exit"], 101.1)
        self.assertEqual(t["reason"], "trail")
        self.ap(t["gross_r"], 1.1)
        self.ap(t["fee_r"], 0.05)
        self.ap(t["net_r"], 1.05)
        # mgmt dist on the same bars: bar 2 fav 1.5 >= 1 -> BE 100.0, trail 100.4; bar 5 trail 101.1
        t = V.simulate_trade(bars, 0, +1, 100.0, 1.0, 99.0, q1=1.0, entry_kind="maker", be_k=1.0, ctrl=ctrl,
                             end_idx=6, mgmt="dist", absorbed=absb)
        self._moves(t, [(2, 100.0, "be"), (2, 100.4, "trail"), (5, 101.1, "trail")])
        self.ap(t["exit"], 101.1)
        self.assertEqual(t["reason"], "trail")

    def test_T54_event_without_events(self):
        # spec T54: own control bars alone move nothing in event mode -> window end at c[6] 101.5, gross 1.5, net 1.45
        bars = self._t53_bars()
        kw = dict(q1=1.0, entry_kind="maker", be_k=1.0, end_idx=6, mgmt="event")
        for ctrl, absb in (([0, 0, 1, 0, 0, 1, 0], [0] * 7), ([0] * 7, [0, 0, 0, 1, 0, 0, 0])):
            # second case: own-side absorption at bar 3 with no S6 level: no de-risk, no trail at the DL break, no exit
            t = V.simulate_trade(bars, 0, +1, 100.0, 1.0, 99.0, ctrl=ctrl, absorbed=absb, **kw)
            self.assertEqual(t["moves"], [])
            self.assertEqual(t["reason"], "window_end")
            self.assertEqual(t["exit_idx"], 6)
            self.ap(t["exit"], 101.5)
            self.ap(t["gross_r"], 1.5)
            self.ap(t["net_r"], 1.45)

    # ---------------------------------------------------------------- v3.1: S8(b), S8(d)
    def test_T55_exhaustion_b_other_side(self):
        # spec T55: calm balance (R 1, ATR 1, c = poc 100.5), buy 0 / sell 1 -> P -1, drift 0 -> S2 -1 = -s for a long
        kw = dict(k_bal=0.8, tier="99", bin_size=1.0, z_hi=2.5, p=0.10)
        bars = calm(81, buy_sell=(0.0, 1.0), b99=(1.0, 0.0))            # (a): net +15 -> false
        self.assertIs(V.exhaustion(bars, 80, {"s": 1, "e_i": 10, "lvl": 100.0}, **kw), True)
        self.assertIs(V.exhaustion(bars, 80, {"s": 1, "e_i": 30, "lvl": 100.0}, **kw), False)   # 21 > 30 no
        bars = calm(81, buy_sell=(1.0, 0.0), b99=(0.0, 1.0))            # short mirror: S2 +1 = -s; (a) -1*-15 > 0
        self.assertIs(V.exhaustion(bars, 80, {"s": -1, "e_i": 10, "lvl": 101.0}, **kw), True)
        # count clause: alternating bars, bar 100 = o c 100 buy 3 -> e 3, res 0 -> absorbed +1 (the only S3 event);
        # W' [61,120]: R 0.5, c 100.5 = poc, P = 2/62 < 0.10 -> S2 0; n(+1) 1 > n(-1) 0 -> exit for a long
        bars = alt_bars(121)
        bars[100] = mk(100, o=100.0, c=100.0, buy=3, b99=(1.0, 0.0))
        self.assertIs(V.exhaustion(bars, 120, {"s": 1, "e_i": 10, "lvl": 100.0}, **kw), True)
        # sell 3 instead: absorbed -1 (the other side absorbed), P = -4/62 -> S2 0 -> hold
        bars[100] = mk(100, o=100.0, c=100.0, sell=3, b99=(1.0, 0.0))
        self.assertIs(V.exhaustion(bars, 120, {"s": 1, "e_i": 10, "lvl": 100.0}, **kw), False)

    def test_T56_exhaustion_d_climax(self):
        # spec T56: S3(61) baseline bars 1..60: d sum 0, sd 1 -> e 3; r sum 1.3, mean 0.021667, sd 0.547142 ->
        # res -0.0396 -> absorbed +1. Bar 60: new trade extreme 102 > 100.5 with net(60;1) = 5.
        def series(c61=101.8, h61=102.0, b99_60=(5.0, 0.0)):
            bars = alt_bars(60, b99=(0.0, 0.0))
            bars.append(mk(60, o=100.0, h=102.0, l=100.0, c=101.8, buy=1, b99=b99_60))
            bars.append(mk(61, o=101.8, h=h61, l=101.5, c=c61, buy=3))
            return bars
        trade = {"s": 1, "e_i": 55, "lvl": 100.0}
        kw = dict(k_bal=0.8, tier="99", bin_size=1.0, z_hi=2.5, p=0.10)
        self.assertIs(V.exhaustion(series(), 61, trade, climax=True, **kw), True)
        self.assertIs(V.exhaustion(series(), 61, trade, climax=False, **kw), False)   # (a) age 6, (b), (c) false
        # bar 61 c 102.5: r 0.7 -> res 1.2398 -> control +1, not absorbed
        self.assertIs(V.exhaustion(series(c61=102.5, h61=102.6), 61, trade, climax=True, **kw), False)
        # no big-trade burst on bar 60
        self.assertIs(V.exhaustion(series(b99_60=(0.0, 0.0)), 61, trade, climax=True, **kw), False)

    # ---------------------------------------------------------------- v3.1: model D, model B trail
    def test_T57_failed_auction(self):
        # spec T57: S1/S2 at bar 4 as T03/T06 (S2 -1: sellers pressed); absorbed[3] = -1 inside W = [1,4];
        # bar 5 closes 102.5 > H 102 with net +3 -> long, lvl l[3] 99.0, edge 102.0
        def bars5(c5=102.5, b99=(3.0, 0.0)):
            bars = f1()
            bars[5] = mk(5, o=101.0, h=103.0, l=100.8, c=c5, buy=6, sell=4, fp="102:6:4", b99=b99)
            return bars
        kw = dict(tier="99", bin_size=1.0)
        absb = [0, 0, 0, -1, 0, 0]
        r = V.failed_auction(bars5(), 5, 4, 0.8, 0.10, 1, absb, **kw)
        self.assertIsNotNone(r)
        self.assertEqual(r["s"], 1)
        self.ap(r["lvl"], 99.0)
        self.ap(r["edge"], 102.0)
        self.assertEqual(V.breakout(bars5(), 5, 4, 0.8, 0.10, 1, **kw), 0)      # S5 needs the break WITH S2
        self.assertIsNone(V.failed_auction(bars5(), 5, 4, 0.8, 0.10, 1, [0] * 6, **kw))
        self.assertIsNone(V.failed_auction(bars5(), 5, 4, 0.8, 0.10, 1, [-1, 0, 0, 0, 0, 0], **kw))   # outside W
        self.assertIsNone(V.failed_auction(bars5(c5=101.9), 5, 4, 0.8, 0.10, 1, absb, **kw))
        self.assertIsNone(V.failed_auction(bars5(b99=(0.0, 3.0)), 5, 4, 0.8, 0.10, 1, absb, **kw))

    @staticmethod
    def _t58_bars(expire=False):
        rows = [(101.0, 102.8, 100.9, 102.5), (102.5, 102.9, 102.0, 102.6), (102.6, 102.7, 101.9, 102.4),
                (102.4, 105.2, 102.3, 105.0), (104.0, 104.2, 102.1, 102.5)]
        if expire:
            rows[2] = (102.6, 102.7, 102.0, 102.4)
            rows[4] = (104.0, 104.2, 101.8, 102.5)
        return [mk(i, o=o, h=h, l=l, c=c) for i, (o, h, l, c) in enumerate(rows)]

    def test_T58_model_d(self):
        # spec T58: rest buy 102.0 armed at close of bar 0; bar 1 l 102.0 no fill; bar 2 l 101.9 fill;
        # D = max(0.306, 102-99+0.1 = 3.1), stop0 98.9; bar 3 fav 3.2 -> BE 102.0, trail l[3]-0.1 = 102.2; bar 4 exit
        ctrl = [0, 0, 0, 1, 0]
        r = V.model_d_trade(self._t58_bars(), 0, +1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest", ctrl=ctrl, end_idx=4)
        self.assertEqual((r["arms"], r["fills"]), (1, 1))
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 2)
        self.ap(t["entry"], 102.0)
        self.ap(t["D"], 3.1)
        self.ap(t["stop0"], 98.9)
        self.ap(t["exit"], 102.2)
        self.assertEqual(t["reason"], "trail")
        self.ap(t["gross_r"], 0.2 / 3.1)                     # 0.064516
        self.ap(t["fee_r"], 0.0005 * 102.0 / 3.1)            # 0.016452
        self.ap(t["net_r"], 0.048065)
        # Dmax 1%: 3.1 > 1.02 -> no arm
        r = V.model_d_trade(self._t58_bars(), 0, +1, 102.0, 99.0, 0.003, 0.01, entry_mode="rest", ctrl=ctrl, end_idx=4)
        self.assertEqual(r["arms"], 0)
        self.assertEqual(r["trades"], [])
        # valid bars 1..3 only: bar 4 would fill but the order expired; 102 + 2*3.1 = 108.2 never reached
        r = V.model_d_trade(self._t58_bars(expire=True), 0, +1, 102.0, 99.0, 0.003, 0.05, entry_mode="rest",
                            ctrl=ctrl, end_idx=4)
        self.assertEqual((r["arms"], r["fills"], r["missed_winners"]), (1, 0, 0))
        self.assertEqual(r["trades"], [])
        # confirm: taker at o[1] 102.5, D = max(0.3075, 3.6) = 3.6, stop0 98.9; bar 3 fav 2.7 < 3.6 (no BE)
        # -> window end at c[4] 102.5: gross 0, fee 2*0.0005*102.5/3.6 = 0.028472
        r = V.model_d_trade(self._t58_bars(), 0, +1, 102.0, 99.0, 0.003, 0.05, entry_mode="confirm", ctrl=ctrl, end_idx=4)
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 1)
        self.ap(t["entry"], 102.5)
        self.ap(t["D"], 3.6)
        self.ap(t["stop0"], 98.9)
        self.ap(t["exit"], 102.5)
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["gross_r"], 0.0)
        self.ap(t["fee_r"], 0.028472)
        self.ap(t["net_r"], -0.028472)

    def test_T59_model_b_trail(self):
        # spec T59: T37 set-up without the fixed target. Bar 8 fav 1.5 < 1.6; bar 9 l 98.8 (fav 2.7) -> BE only;
        # window end at c[9] 99.0 taker: gross 2.5/1.6 = 1.5625, fee 0.0005*101.5/1.6 = 0.031719, net 1.530781
        bars, absorbed = self._t37_bars()
        r = V.model_b(bars, 5, {"H": 102.0, "L": 99.0}, absorbed, 0.003, 0.05, entry_mode="rest", end_idx=9,
                      target_mode="trail")
        self.assertEqual((r["arms"], r["fills"]), (1, 1))
        t = r["trades"][0]
        self.assertEqual(t["fill_idx"], 7)
        self.ap(t["entry"], 101.5)
        self.assertIsNone(t.get("target"))
        self.ap(t["exit"], 99.0)
        self.assertEqual(t["reason"], "window_end")
        self.ap(t["gross_r"], 1.5625)
        self.ap(t["fee_r"], 0.0005 * 101.5 / 1.6)
        self.ap(t["net_r"], 1.530781)

    # ---------------------------------------------------------------- v3.1: day budget, adds, calendar
    def test_T60_day_floor_and_carry(self):
        # spec T60 (section 6): prefix sums [0, carry, ...]; floor: peak > 0 and C <= 0 blocks; risk = min(1, C) if peak > 0
        A, R = V.first_leg_allowed, V.first_leg_risk
        self.assertIs(A([1.0, -1.0]), False)
        self.assertIs(A([1.0, -0.5]), True)
        self.ap(R([1.0, -0.5]), 0.5)
        self.ap(R([2.0]), 1.0)
        self.assertIs(A([], carry=0.6), True)
        self.ap(R([], carry=0.6), 0.6)
        self.assertIs(A([-0.6], carry=0.6), False)
        self.ap(R([-0.6], carry=0.6), 0.0)
        self.assertIs(A([], carry=-0.4), True)
        self.ap(R([], carry=-0.4), 1.0)
        self.assertIs(A([1.5], carry=-1.2), False)                     # 0, -1.2, 0.3: stop after recovery
        self.ap(R([-0.5, 0.6]), 0.1)
        self.ap(R([]), 1.0)
        self.ap(R([-1.2, -1.2]), 1.0)
        self.ap(R([-1.2, -1.2, -1.2]), 0.0)
        self.ap(R([], n_first_legs=10), 0.0)

    def test_T61_day_r_risk_units(self):
        # spec T61: day R = sum risk_u * net_r -> d1 0.5*2.0 - 1.1 = -0.1; d2 no trade 0
        out = V.aggregate_day_r(["d1", "d2"], [{"day": "d1", "net_r": 2.0, "risk_u": 0.5},
                                               {"day": "d1", "net_r": -1.1}])
        self.assertEqual(len(out), 2)
        self.ap(out[0], -0.1)
        self.ap(out[1], 0.0)

    def test_T62_adds_v31(self):
        # spec T62: q_add = min(q1, (budget + locked) / dist); long e1 100, stop 99 (locked -1), pa 101 (dist 2)
        legs = [(1.0, 100.0)]
        self.ap(V.add_size(+1, legs, 99.0, 101.0, 1.0, budget=3.0), 1.0)    # open risk at stop 1 + 2 = 3 = budget
        self.ap(V.add_size(+1, legs, 99.0, 101.0, 1.0, budget=1.5), 0.25)
        self.assertEqual(V.add_size(+1, legs, 99.0, 101.0, 1.0, budget=1.0), 0.0)
        base = dict(s=+1, e1=100.0, stop=102.0, n_adds=0, i=100, open_idx=0, control=+1, push_ok=True,
                    curve_state="fair")
        self.assertIs(V.add_allowed(**dict(base, n_adds=2)), False)       # max 2 adds (3 entries)
        self.assertIs(V.add_allowed(**dict(base, n_adds=1)), True)
        self.assertIs(V.add_allowed(**dict(base, stop=99.0, add_mode="day")), True)
        self.assertIs(V.add_allowed(**dict(base, stop=99.0, add_mode="be")), False)
        self.assertIs(V.add_allowed(**dict(base, curve_state="premium", s7=False)), True)

    def test_T63_calendar(self):
        # spec T63 (section 2 US_CLOSED, London window)
        for ymd in ((2024, 12, 25), (2025, 1, 9), (2025, 4, 18), (2025, 7, 3), (2025, 7, 4), (2025, 11, 27),
                    (2025, 11, 28), (2025, 12, 24), (2026, 4, 3), (2026, 7, 3)):
            self.assertIsNone(V.ny_open_utc(dt.date(*ymd)), ymd)
        for ymd, hm in (((2025, 12, 26), (14, 30)), ((2025, 7, 7), (13, 30))):
            r = V.ny_open_utc(dt.date(*ymd))
            self.assertEqual((r.hour, r.minute), hm, ymd)
        for ymd, hm in (((2025, 3, 28), (8, 0)), ((2025, 3, 31), (7, 0)), ((2025, 10, 24), (7, 0)),
                        ((2025, 10, 27), (8, 0))):
            r = V.london_open_utc(dt.date(*ymd))
            self.assertIsNotNone(r, ymd)
            self.assertEqual((r.hour, r.minute), hm, ymd)
            self.assertEqual(r.date(), dt.date(*ymd), ymd)
        self.assertIsNone(V.london_open_utc(dt.date(2025, 3, 29)))          # Saturday

    def test_T64_lookahead_canary_v31(self):
        # spec T64: S5D, S9 and S8 (climax on) at i must not change when bars > i are deleted
        bars = rand_series()
        rng = random.Random(54321)

        def snap(b, i):
            absb = [V.effort_result(b, j, L=20, z_hi=1.5)["absorbed"] if j >= 20 else 0 for j in range(i + 1)]
            out = [V.failed_auction(b, i, 20, 3.0, 0.02, 5, absb, tier="99", bin_size=1.0)]
            for s in (+1, -1):
                out.append(V.defended_level(b, absb, i - 10, i, s))
                out.append(V.exhaustion(b, i, {"s": s, "e_i": i - 70, "lvl": b[i - 5]["l"] if s > 0 else b[i - 5]["h"]},
                                        k_bal=3.0, tier="99", bin_size=1.0, p=0.02, climax=True))
            return out
        for i in rng.sample(range(130, 600), 20):
            self.assertEqual(snap(bars, i), snap(bars[:i + 1], i), "look-ahead at i=%d" % i)

if __name__ == "__main__":
    unittest.main()
