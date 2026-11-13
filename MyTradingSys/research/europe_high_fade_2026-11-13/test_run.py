"""Tests of the session-high, outcome, bootstrap and verdict logic on tiny hand-made series (numbers worked by hand)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run

D0 = 1_700_000_000_000 // run.DAY * run.DAY
H, M5 = run.H, run.M5


def test_europe_high_window_boundaries():
    bars = [
        [D0 + 6 * H + 55 * 60000, 1, 999, 1, 1],      # 06:55 opens before the session: excluded
        [D0 + 7 * H, 100, 105, 99, 101],               # 07:00 first Europe bar
        [D0 + 12 * H + 55 * 60000, 101, 110, 100, 102],  # 12:55 closes 12:59:59.999 < 13:00: included
        [D0 + 13 * H, 102, 500, 0.5, 103],             # 13:00 belongs to the US block: excluded
    ]
    assert run.europe_high(bars, D0) == (110, 99)
    assert run.europe_high([], D0) is None


def test_trade_outcome_short_long_fee_and_floor():
    # SHORT 100 -> 99 : +100 bps gross, 4 bps fee -> 96 net; void at 101 -> risk 100 bps -> R 0.96
    o = run.trade_outcome("SHORT", 100.0, 99.0, 101.0, 4.0)
    assert abs(o["gross_bps"] - 100.0) < 1e-9 and abs(o["net_bps"] - 96.0) < 1e-9 and abs(o["r"] - 0.96) < 1e-9 and o["hit"]
    # LONG 100 -> 99.9 : -10 bps gross (a loss, no hit), net -14; void 99.99 -> distance 1 bp, floored to 10 bps -> R -1.4
    o = run.trade_outcome("LONG", 100.0, 99.9, 99.99, 4.0)
    assert abs(o["net_bps"] + 14.0) < 1e-9 and o["risk_bps"] == 10.0 and abs(o["r"] + 1.4) < 1e-9 and not o["hit"]
    # a gross gain smaller than the fee is a hit that loses money
    o = run.trade_outcome("LONG", 100.0, 100.02, 99.0, 4.0)
    assert o["hit"] and o["net_bps"] < 0


def test_bootstrap_and_verdict():
    days = [1, 1, 2, 2, 3, 3, 4, 4]
    m, lo, hi = run.day_block_bootstrap(days, [0.5] * 8, draws=200)
    assert m == 0.5 and lo == 0.5 and hi == 0.5               # constant series: zero-width CI
    m, lo, hi = run.day_block_bootstrap(list(range(40)), [1.0, -1.0] * 20, draws=500)
    assert lo < 0 < hi                                          # symmetric noise: CI straddles 0
    assert run.verdict_for(29, 1.0, 0.5, True, {"up": 29}) == "UNDERPOWERED"
    assert run.verdict_for(100, 0.2, 0.05, False, {"up": 50, "down": 50}) == "FAIL"   # CI above 0 but placebo not beaten
    assert run.verdict_for(100, 0.2, -0.01, True, {"up": 50, "down": 50}) == "FAIL"
    assert run.verdict_for(100, 0.2, 0.05, True, {"up": 100, "down": 0, "range": 0}) == "PASS-ONE-REGIME"
    assert run.verdict_for(100, 0.2, 0.05, True, {"up": 50, "down": 50}) == "PASS"


def test_regime_no_lookahead():
    closes = {D0 + i * run.DAY: 100.0 for i in range(25)}
    closes[D0 + 24 * run.DAY] = 150.0                           # today's jump must not label today
    reg = run.regime_by_day(closes)
    assert reg[D0 + 24 * run.DAY] == "range" and reg[D0 + 20 * run.DAY] == "range"
    closes[D0 + 23 * run.DAY] = 150.0                           # prior day 50 % above SMA20 -> up for the next day
    assert run.regime_by_day(closes)[D0 + 24 * run.DAY] == "up"
