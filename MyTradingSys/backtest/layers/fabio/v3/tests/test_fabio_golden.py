"""Fabio golden-scenario translation tests (L2, TF7 / pipeline row 1.9) on the v3 engine with order-flow-bar fixtures.

Question: given the situation Fabio describes, does v3 take HIS trade (side, entry timing, stop side of the extreme,
target, management steps)? Sources, read in full: research/fast_track_2026-09-27/FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md
(decision rows D01-D30, missing pieces M1-M10), FABIO_TRADE_MODEL.md (0jM5Y31YJak + 8CWKfoSJu3c, section 1 steps 1-8),
MyTradingSys/research/_archive/loose_2026-10/TOM_FABIO_REVIEW_2026-10-03.md section 2 L2. Test ids: G<nn>; "D<nn>" = fZl decision row,
"M<n>" = fZl missing piece, "TM<n>" = FABIO_TRADE_MODEL section 1 step.

Limits (review section 2): none of his trades has a BTC date, so the bars below are our reconstruction of the described
situation in normalised units (price ~100, bin 1.0). They test translation fidelity, not edge. Every expected number is
hand-derived in the comment above its assert from the quoted situation and the v3 spec rules, never read from the code.

Scenarios v3 fails are NOT fixed here: they carry @known_gap(<ref>) and skip with the failure text, so the gate stays
green and the list stays visible. MTS_FABIO_GOLDEN_STRICT=1 turns every known gap into a hard failure (the exact failing
list). A gap that starts passing is a passing test: delete its marker.

Not translatable (no test, listed in the session record): D09/M9 scratch and re-pivot (no code path), D13 day P&L as a
sizing input across sessions (no cross-session state in run()), D21/M10 big trades in the body vs the wick (data has no
per-price big trades), D27 exit variant by day type (ex-post only), D18 "buyers wall" (needs L2 data).
"""
import functools
import os

import unittest


class _Approx:
    """pytest.approx stand-in (unittest-only gate): equal within abs tol (default 1e-6 or 1e-6 relative)."""
    def __init__(self, expected, abs=None):
        self.expected = expected
        self.tol = abs if abs is not None else max(1e-6, 1e-6 * __builtins__["abs"](expected) if isinstance(__builtins__, dict) else 1e-6)

    def __eq__(self, other):
        return -self.tol <= other - self.expected <= self.tol

    __hash__ = None

    def __repr__(self):
        return "approx(%r)" % (self.expected,)


class pytest:  # noqa: N801 - minimal shim so the scenario bodies stay byte-identical to the spec-derived originals
    approx = staticmethod(_Approx)

    @staticmethod
    def skip(msg):
        raise unittest.SkipTest(msg)

from MyTradingSys.backtest.layers.fabio.v3 import (add_allowed, add_size, engine, exhaustion, first_leg_allowed,
                                                   first_leg_risk, simulate_trade)

STRICT = os.environ.get("MTS_FABIO_GOLDEN_STRICT") == "1"


def known_gap(ref):
    """Mark a scenario v3 is known to fail. Skips with the failure text unless MTS_FABIO_GOLDEN_STRICT=1."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **k):
            try:
                fn(*a, **k)
            except AssertionError as e:
                if STRICT:
                    raise
                pytest.skip("KNOWN GAP %s: %s" % (ref, (str(e).splitlines() or [""])[0][:200]))
        return wrapper
    return deco


# ---------------------------------------------------------------- fixture builders (1m order-flow bars)
def bar(k, o, h, l, c, buy, sell, bb=0.0, bs=0.0, fpbin=100):
    """One bar. fp = all volume in one 1.0 bin (fpbin) so the profile POC is that bin's centre; b99 = big trades."""
    return {"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": float(buy), "sell_vol": float(sell),
            "delta": float(buy - sell), "b99_buy_vol": float(bb), "b99_sell_vol": float(bs), "b999_buy_vol": 0.0,
            "b999_sell_vol": 0.0, "thr_days": 30, "fp": "%d:%.1f:%.1f" % (fpbin, buy, sell)}


def mirror(bars, axis=200.0):
    """Price/side reflection (long <-> short): p -> axis - p, buy <-> sell, delta -> -delta, fp bin lo -> axis-1-lo."""
    out = []
    for b in bars:
        fp = "|".join("%d:%s:%s" % (axis - 1 - float(lo), se, bu) for lo, bu, se in (e.split(":") for e in b["fp"].split("|")))
        out.append({"t": b["t"], "o": axis - b["o"], "h": axis - b["l"], "l": axis - b["h"], "c": axis - b["c"],
                    "buy_vol": b["sell_vol"], "sell_vol": b["buy_vol"], "delta": -b["delta"],
                    "b99_buy_vol": b["b99_sell_vol"], "b99_sell_vol": b["b99_buy_vol"], "b999_buy_vol": 0.0,
                    "b999_sell_vol": 0.0, "thr_days": 30, "fp": fp})
    return out


def prelude(n=60):
    """n quiet bars around 100.5: body +-0.1 alternating, delta +-2 (so the S3 z-scores of later bars are defined)."""
    out = []
    for k in range(n):
        up = k % 2 == 1
        c = 100.6 if up else 100.4
        out.append(bar(k, 100.5, max(100.5, c) + 0.1, min(100.5, c) - 0.1, c, 51 if up else 49, 49 if up else 51))
    return out


CFG = dict(N=6, p=0.10, z_hi=2.5, m_c=5, f=0.003, g="off", entry_mode="rest", mgmt="event", bin_size=1.0, tier="99")


def run(bars, as_of=None, **over):
    cfg = dict(CFG, **over)
    if as_of is not None:
        cfg["as_of"] = as_of
    return engine.run(bars, cfg)


# ---------------------------------------------------------------- G01-G03: model A, hidden pressure -> break (0jM5, 8CWK)
def balance_bars(n=20, buy=50, sell=50):
    """Balance around 100.5 (H 100.8, L 100.2, poc 100.5), flat price; buy/sell set the hidden CVD pressure."""
    return [bar(k, 100.5, 100.8, 100.2, 100.5, buy, sell) for k in range(n)]


# Break bar 20 (S4 needs a 15-bar window before it): closes 97.1, below the balance low 100.2, with big SELL trades; volume profile of the leg by bin
# (96: 60, 97: 10, 98: 120, 99: 6, 100: 20) -> LVN bins 97 (centre 97.5) and 99 (99.5).
BREAK_SHORT = {"o": 100.5, "h": 100.6, "l": 96.9, "c": 97.1}


def short_break_bar(k=20, bs=8.0):
    b = bar(k, BREAK_SHORT["o"], BREAK_SHORT["h"], BREAK_SHORT["l"], BREAK_SHORT["c"], 30, 70, bs=bs)
    b["fp"] = "96:30:30|97:5:5|98:60:60|99:3:3|100:10:10"
    return b


def test_g01_distribution_balance_then_break_with_big_sells_is_a_short_armed_at_the_lvn():
    # TM2+TM3: flat price, CVD falling (P = -0.3, distribution), then price follows the pressure out of the balance
    # with big trades. Balance H 100.8 / L 100.2. LVN* = 99.5 (bin 99 centre; candidate needs x >= X + 0.25*(O - X)
    # = 96.9 + 0.825 and x > c 97.1). Structural stop = s*(lvn - O) + tick = -(99.5-100.2) + 0.1 = 0.8; f*entry = 0.2985,
    # so D = 0.8 and the stop sits at 99.5 + 0.8 = 100.3, just past the broken edge 100.2 (TM4: "stop just past the extreme").
    bars = balance_bars(20, 35, 65) + [short_break_bar()]
    out = run(bars, models=("A",))
    assert (out["verdict"], out["model"], out["side"]) == ("ARMED", "A", -1)
    assert out["entry"] == pytest.approx(99.5) and out["stop"] == pytest.approx(100.3)
    assert out["stop"] > out["entry"] > 97.1                       # short: stop above entry, entry above the extreme
    assert out["target"] is None                                   # TM: no fixed target, "ride and add" (D10)
    pre = run(bars[:20], models=("A",))                             # one bar earlier the pressure has no result yet
    assert pre["verdict"] == "IDLE" and pre["side"] is None        # entry timing: the break bar itself, not before


def test_g02_accumulation_mirror_is_a_long():
    # TM2 "flat price + rising CVD = accumulation": the reflected fixture must give the reflected trade.
    out = run(mirror(balance_bars(20, 35, 65) + [short_break_bar()]), models=("A",))
    assert (out["verdict"], out["model"], out["side"]) == ("ARMED", "A", 1)
    assert out["entry"] == pytest.approx(200 - 99.5) and out["stop"] == pytest.approx(200 - 100.3)
    assert out["stop"] < out["entry"]


def test_g03_no_hidden_pressure_means_no_trade():
    # TM2 is the LEADING signal: a break with big trades out of a balance whose CVD is flat (P = 0) is not his trade.
    out = run(balance_bars(20, 50, 50) + [short_break_bar()], models=("A",))
    assert out["verdict"] == "IDLE" and out["side"] is None


def test_g04_pressure_without_big_trades_means_no_trade():
    # TM3: the trigger is pressure that gets a result WITH big trades pushing; same break, no big-trade volume.
    out = run(balance_bars(20, 35, 65) + [short_break_bar(bs=0.0)], models=("A",))
    assert out["verdict"] == "IDLE"


def test_g05_break_against_the_pressure_is_not_model_a():
    # TM3/D07: model A is "break WITH the pressure". Distribution (P = -0.3) and a break UP is model D's domain;
    # model A must stay silent on it (S5 fires only with S2).
    up = bar(20, 100.5, 101.6, 100.4, 101.5, 80, 20, bb=8.0)
    out = run(balance_bars(20, 35, 65) + [up], models=("A",))
    assert out["verdict"] == "IDLE"


# ---------------------------------------------------------------- G06-G09: fZlNGWvd2Ko T2, the long from a failed seller auction
def fzl_t2():
    """fZl T2 (L36-42, L110-146, L152-156), bar index = comment:
      0-59   quiet prelude (S3 history)
      60-65  consolidation 100.2-100.8, SELLERS press (delta -30 of 100/bar) and get absorbed (no result)   [L36-39]
      66     buyers aggress at the level: close 101.5 above the balance high, big BUY trades                   [L40-42]
      67     pullback fills the resting limit at 100.8                                                          [L43-49]
      68     sellers attack again and are absorbed (delta -50, no result), buyers continue                      [L110-116]
      69     buyers took control (delta +50, body +0.9)                                                         [L121-125]
      70     sellers took control but stopped on big trades (delta -50, no result)                              [L132-136]
      71     market explodes up from the level, big buy trades, new extreme                                     [L142-146]
      72     aggression with no result, close back inside: the failed auction                                   [L142-146]
      73     next open, where the climax exit is taken                                                          [L142-146]
    """
    b = prelude(60)
    b += [bar(60 + k, 100.5, 100.8, 100.2, 100.5, 35, 65) for k in range(6)]
    b.append(bar(66, 100.5, 101.6, 100.4, 101.5, 80, 20, bb=8.0))
    b.append(bar(67, 101.4, 101.5, 100.6, 101.0, 50, 50))
    b.append(bar(68, 101.0, 101.2, 100.5, 101.0, 25, 75))
    b.append(bar(69, 101.0, 102.0, 100.9, 101.9, 75, 25))
    b.append(bar(70, 101.9, 102.0, 101.3, 101.9, 25, 75))
    b.append(bar(71, 101.9, 103.5, 101.8, 103.4, 80, 20, bb=10.0))
    b.append(bar(72, 103.4, 103.5, 102.6, 103.3, 80, 20))
    b.append(bar(73, 102.8, 102.9, 102.4, 102.6, 50, 50))
    return b


def test_g06_failed_seller_auction_is_a_long_with_the_stop_under_the_absorption_level():
    # D08/M4: sellers pressed and were absorbed in the balance (S2 = -1, absorbed bar 65), buyers break up with big
    # trades: ENTER LONG. Edge = balance high 100.8 (limit); level = low of the last absorbed bar = 100.2; structural
    # D = (100.8 - 100.2) + 0.1 = 0.7 (> f*entry 0.3024), stop = 100.8 - 0.7 = 100.1. No target (D10 "take the top of the day").
    out = run(fzl_t2(), as_of=66, models=("D",))
    assert (out["verdict"], out["model"], out["side"]) == ("ARMED", "D", 1)
    assert out["entry"] == pytest.approx(100.8) and out["stop"] == pytest.approx(100.1)
    assert out["stop"] < 100.2 < out["entry"]                      # stop beyond the absorption level, long side
    assert out["target"] is None
    assert run(fzl_t2(), as_of=65, models=("D",))["verdict"] == "IDLE"      # not before the buyers' aggression
    assert run(fzl_t2(), as_of=66, models=("A",))["verdict"] == "IDLE"      # model A cannot take it (against pressure)


def test_g07_short_mirror_of_the_failed_seller_auction():
    # Same trade reflected: buyer pressure absorbed, sellers break down: SHORT, stop above the level (spec: sign-symmetric).
    out = run(mirror(fzl_t2()), as_of=66, models=("D",))
    assert (out["verdict"], out["side"]) == ("ARMED", -1)
    assert out["entry"] == pytest.approx(200 - 100.8) and out["stop"] == pytest.approx(200 - 100.1)
    assert out["stop"] > out["entry"]


def test_g08_stop_to_zero_when_the_other_sides_push_is_stopped_then_ratchet():
    # D20: bar 68 sellers attack and are absorbed -> "stop loss to zero": candidates {entry 100.8, pullback low 100.5 - 0.1}
    # both below c 101.0, best = 100.8 (BE). D24: bar 70 sellers absorbed again, pullback low since the last buyer-control
    # bar (69) is 101.3 -> candidate 101.2 > 100.8 -> ratchet to 101.2. Stops only tighten (D22 "covered below this low").
    out = run(fzl_t2(), as_of=68, models=("D",))
    assert out["verdict"] == "IN_TRADE" and out["management"]["stop_now"] == pytest.approx(100.8)
    out = run(fzl_t2(), as_of=70, models=("D",))
    assert out["verdict"] == "IN_TRADE"
    assert [(i, round(px, 6), kind) for (i, px, kind) in out["management"]["moves"]] == [
        (68, 100.8, "opp"), (70, 101.2, "opp")]
    assert out["management"]["stop_now"] == pytest.approx(101.2)


def test_g09_climax_and_failed_auction_closes_the_trade_at_the_next_open():
    # D26/TM7: bar 71 explodes to a new extreme (103.5) on big buys, bar 72 shows aggression with no result (buyers
    # delta +60, body -0.1) = failed auction -> exit at the NEXT open 102.8 (bar 73). Gross R = (102.8 - 100.8) / D 0.7.
    out = run(fzl_t2(), as_of=73, models=("D",))
    m = out["management"]
    assert out["verdict"] == "DONE" and m["reason"] == "s8" and m["exit_idx"] == 73
    assert m["exit"] == pytest.approx(102.8)
    assert out["stop"] == pytest.approx(100.1)                     # initial stop reported
    # bar 72 (buyers' aggression, no result = E_own, D14): stop -> S6 level l[71] 101.8 - 0.1 = 101.7, in force at the exit
    assert [(i, round(px, 6), k) for (i, px, k) in m["moves"]][-1] == (72, 101.7, "own")
    assert m["stop_now"] == pytest.approx(101.7)
    assert (102.8 - 100.8) / 0.7 == pytest.approx(2.857143, abs=1e-6)
    still = run(fzl_t2(), as_of=71, models=("D",))
    assert still["verdict"] == "IN_TRADE"                          # the explosion bar alone is not an exit


@known_gap("fZl D28 / README open item: adds not executed")
def test_g10_first_load_plus_two_reloads_are_one_trade_record():
    # D28 (L152-156): "we loaded the first one here, then we reloaded here, then we reloaded here". The v3 trade
    # record is one leg (README: multi-leg adds are decision helpers only), so the 3 entries cannot be reproduced.
    m = run(fzl_t2(), as_of=73, models=("D",))["management"]
    assert "adds" in m and len(m["adds"]) == 2


# ---------------------------------------------------------------- G11-G13: management steps (hand-built bars)
def mgmt_bars():
    rows = [(100.0, 100.2, 99.8, 100.1), (100.1, 100.8, 100.0, 100.7), (100.7, 101.2, 100.4, 101.1),
            (101.1, 101.6, 101.0, 101.2), (101.2, 102.0, 101.5, 101.9)]
    return [bar(k, o, h, l, c, 50, 50) for k, (o, h, l, c) in enumerate(rows)]


def test_g11_own_side_failing_lowers_risk_by_stop_and_is_not_an_exit():
    # D14/M2: "buyers failed again, so I want to lower my risk". Long 100.0, D 1.0, stop 99.0. Bar 2 buyers in control
    # (low 100.4); bar 3 buyers absorbed (E_own): stop -> S6 level 100.4 - tick = 100.3, trade stays open.
    # D17: bar 3 armed the level the sellers protect (its high 101.6); bar 4 closes 101.9 above it with buyers in control
    # (low 101.5): trail into profit, cand 101.5 - 0.1 = 101.4. Exit is the window end at c[4].
    t = simulate_trade(mgmt_bars(), 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0, 0, 1, 0, 1],
                       absorbed=[0, 0, 0, 1, 0], end_idx=4)
    assert [(i, round(px, 6), k) for (i, px, k) in t["moves"]] == [(3, 100.3, "own"), (4, 101.4, "trail")]
    assert t["reason"] == "window_end" and t["exit_idx"] == 4 and t["exit"] == pytest.approx(101.9)


def test_g12_stop_hit_after_the_ratchet_exits_at_the_ratcheted_stop():
    # D24/D25: "not give back the profit": after the ratchet to 101.4 a bar trading down to 101.3 exits at 101.4 (taker),
    # +1.4 R-units of D 1.0 on a long from 100.0.
    rows = [(101.9, 102.0, 101.3, 101.4)]
    bars = mgmt_bars() + [bar(5, o, h, l, c, 50, 50) for (o, h, l, c) in rows]
    t = simulate_trade(bars, 0, 1, 100.0, 1.0, 99.0, mgmt="event", ctrl=[0, 0, 1, 0, 1, 0],
                       absorbed=[0, 0, 0, 1, 0, 0], end_idx=5)
    assert t["reason"] == "trail" and t["exit_idx"] == 5 and t["exit"] == pytest.approx(101.4)
    assert t["gross_r"] == pytest.approx(1.4)


def long_flow_bars(n_push, total):
    """Short trade (fill bar 9 at 99.5) with big sells on bars 9..8+n_push, then none; prices stay 97-99.4."""
    bars = []
    for k in range(total):
        bars.append(bar(k, 98.0, 99.4, 97.0, 98.0, 40, 60, bs=3.0 if 9 <= k < 9 + n_push else 0.0))
    return bars


def test_g13_exit_when_big_trades_stop_pushing_and_hold_while_they_continue():
    # TM7: "takes profit when big trades stop pushing". Short entry 99.5 (D 0.8, stop 100.3) filled on bar 9, S8(a):
    # at i = fill + 15 = 24 the net big trades of bars 10..24 must be <= 0 (here zero): exit at o[25].
    # With big sells continuing through bar 30 there is no S8 exit before the window end.
    base = dict(s=-1, entry=99.5, D=0.8, stop=100.3, mgmt="event")
    stop_push = simulate_trade(long_flow_bars(1, 40), 9, end_idx=39, **base)
    assert stop_push["reason"] == "s8" and stop_push["exit_idx"] == 25 and stop_push["exit"] == pytest.approx(98.0)
    keep_push = simulate_trade(long_flow_bars(30, 40), 9, end_idx=39, **base)
    assert keep_push["reason"] == "window_end" and keep_push["exit_idx"] == 39


# ---------------------------------------------------------------- G14-G17: risk budget and adds (fZl D05, D12; 8CWK TM5/TM8)
def test_g14_day_floor_is_zero_after_a_profitable_session():
    # D05/D02: London +10 (units of the trade's R), NY gives back 4.5: still allowed (C 5.5 > 0). Giving back everything
    # (C = 0 with a positive peak) stops the session: "if we go back to break even, we stop the session".
    assert first_leg_allowed([-4.5], 1, carry=10.0) is True
    assert first_leg_allowed([-4.5, -5.5], 2, carry=10.0) is False
    # D12 "I'm only risking the profit of the day": first-leg risk is min(1, closed day R).
    assert first_leg_risk([], 0, carry=0.6) == pytest.approx(0.6)
    assert first_leg_risk([], 0, carry=10.0) == pytest.approx(1.0)


def test_g15_add_before_break_even_is_funded_by_the_day_profit_only():
    # D12/D13 "loading and scaling in ... only risking the profit of the day": long q1 = 1 at 100, stop still 99 (before
    # BE), add at 101. locked = 1*(99-100) = -1, dist = 101-99 = 2. add_mode "be" (stop at/beyond entry) refuses; add_mode
    # "day" with budget 5 sizes q = min(1, (5 + -1)/2) = 1; with budget 0 q = (0-1)/2 < 0.25 -> no add.
    assert add_allowed(1, 100.0, 99.0, 0, 50, 0, 1, True, "fair", add_mode="be") is False
    assert add_allowed(1, 100.0, 99.0, 0, 50, 0, 1, True, "fair", add_mode="day") is True
    assert add_size(1, [(1.0, 100.0)], 99.0, 101.0, 1.0, budget=5.0) == pytest.approx(1.0)
    assert add_size(1, [(1.0, 100.0)], 99.0, 101.0, 1.0, budget=0.0) == 0.0
    assert add_size(1, [(1.0, 100.0)], 99.0, 101.0, 1.0, budget=2.0) == pytest.approx(0.5)     # (2 - 1)/2


def test_g16_at_most_three_entries():
    # fZl recap: first load + 2 reloads = 3 entries; a third add is refused.
    assert add_allowed(1, 100.0, 100.0, 1, 50, 0, 1, True, "fair") is True
    assert add_allowed(1, 100.0, 100.0, 2, 50, 0, 1, True, "fair") is False


def test_g17_no_adds_low_in_the_curve():
    # 8CWK TM5: "does not add low in the curve (at discount for a short)"; mirror: no long add in premium.
    assert add_allowed(-1, 100.0, 100.0, 0, 50, 0, -1, True, "discount") is False
    assert add_allowed(-1, 100.0, 100.0, 0, 50, 0, -1, True, "premium") is True
    assert add_allowed(1, 100.0, 100.0, 0, 50, 0, 1, True, "premium") is False


# ---------------------------------------------------------------- G18-G20: S8 exits with 60 bars of S3 history
def hold_bars(absorbed_delta):
    """Long trade filled at bar 60. Bars 61..121: a consolidation around 100.5 (+-0.1 bodies). Bars with k % 5 == 0 are
    SELLER efforts without result (delta `absorbed_delta`, body 0); the others have the +-2 alternating delta."""
    b = prelude(61)
    for k in range(61, 122):
        if k % 5 == 0:
            b.append(bar(k, 100.5, 100.8, 100.2, 100.5, 50 + absorbed_delta / 2.0, 50 - absorbed_delta / 2.0))
        else:
            up = k % 2 == 1
            c = 100.6 if up else 100.4
            b.append(bar(k, 100.5, max(100.5, c) + 0.1, min(100.5, c) - 0.1, c, 51 if up else 49, 49 if up else 51,
                         bb=1.0 if k % 2 else 0.0))
    return b


def test_g18_in_trade_consolidation_with_sellers_absorbed_is_held():
    # D18/M3: a consolidation inside a long where the SELLERS got absorbed is HOLD. Here 13 of 61 bars carry a moderate
    # seller effort without result (delta -20): n(-s) = 13 > n(s) = 0 and P = -260/6100 = -0.043 (< p 0.10), so S2 is 0:
    # neither branch of S8(b) fires. (a) big buys continue (net > 0), (c)/(d) not met.
    bars = hold_bars(-20)
    assert exhaustion(bars, 121, {"s": 1, "e_i": 60, "lvl": None}, k_bal=0.8, tier="99", bin_size=1.0, z_hi=2.5, p=0.10) is False


@known_gap("fZl D18 / M3: S8(b) exits on S2 == -s even when the absorbed side is the sellers")
def test_g19_in_trade_consolidation_with_heavy_seller_absorption_is_still_held():
    # D18 with the sellers' effort heavy enough that the window CVD reads as distribution (P = -0.13 < -p): Fabio's
    # words are "sellers got completely absorbed ... buyers not making results ... HOLD, tight if it breaks down".
    # v3 S8(b) reads S2 == -s as "new balance favouring the other side" and exits: pressure sign and absorbed side
    # contradict each other (fZl section 4, row D07 CONFLICT carried into the exit).
    bars = hold_bars(-60)
    assert exhaustion(bars, 121, {"s": 1, "e_i": 60, "lvl": None}, k_bal=0.8, tier="99", bin_size=1.0, z_hi=2.5, p=0.10) is False


def test_g20_opposite_control_breaking_the_last_level_exits():
    # TM7: "if these aggressive buyers take back control, I want to be out". Short, last seller-control level (S6) 100.3.
    # Bar 61: buyers delta +60 with a +1.0 body = control +1 (z of both >> thresholds) closing at 101.0 > 100.3: exit.
    # Same bar closing below the level (100.2): no exit (s*(c - lvl) < 0 fails).
    bars = prelude(61) + [bar(61, 100.5, 101.1, 100.4, 101.0, 80, 20)]
    trade = {"s": -1, "e_i": 55, "lvl": 100.3}
    kw = dict(k_bal=0.8, tier="99", bin_size=1.0, z_hi=2.5, p=0.10)
    assert exhaustion(bars, 61, trade, **kw) is True
    below = prelude(61) + [bar(61, 100.5, 100.6, 99.4, 100.2, 80, 20)]
    assert exhaustion(below, 61, trade, **kw) is False


class GoldenScenarios(unittest.TestCase):
    """unittest entry point: one test per module-level test_g* scenario function (the gate runs unittest, not pytest)."""


def _bind(fn):
    return lambda self: fn()


for _name, _fn in list(globals().items()):
    if _name.startswith("test_") and callable(_fn):
        setattr(GoldenScenarios, _name, _bind(_fn))


if __name__ == "__main__":
    unittest.main()
