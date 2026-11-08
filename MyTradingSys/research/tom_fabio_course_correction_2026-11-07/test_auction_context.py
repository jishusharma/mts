"""Unit and replay tests for Plain Auction Theory & Multi-Timeframe Context Evaluator (auction_context.py).

All expected numbers are hand-computed from first principles or taken from the measured Oct-Nov 2026 BTCUSDT records:
  - 2026-10-29 Upper Sweep Short (81,971 sweep of 10-28 81,823 high -> reclaim below prior VAH 81,400 -> 77,910)
  - 2026-11-04 Range Rotation & LVN Fast Traverse (75,690 sweep -> reclaim -> 14:40 UTC impulse through LVN -> 80,504)
  - 2026-11-05 Accepted Below VAL Continuation Short (6x5m / 2x30m closes below 79,500 VAL -> 75,208)
  - 2026-11-06 15:00 UTC V-Sweep Long (74,810 sweep of Sep-15 74,961 low with 15.7x volume -> reclaim 75,290 -> 76,416)
  - Fee-trap gate rejection on 5-8 bps stops vs 10 bps taker fees, double-probe reclaim reset, multi-bin LVNs, and HTF bias sets.
"""
import importlib.util
import math
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("auction_context", HERE / "auction_context.py")
ac = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ac)


def _bar(o, h, l, c, v=100.0, delta=0.0, t=0, close_t=299999):
    return {"t": t, "close_t": close_t, "o": float(o), "h": float(h), "l": float(l), "c": float(c), "v": float(v), "delta": float(delta)}


def test_p_close_colour_hand_computed():
    # Phi(1.0) = 0.841344746. When d_atr = 1 / 1.5957691216 and t_left = 1.0, |d|*SIGMA_K/sqrt(t) = 1.0 -> 0.841345
    k = 2.0 * math.sqrt(2.0 / math.pi)
    assert ac.p_close_colour(0.0, 0.5) == pytest.approx(0.5, abs=1e-9)
    assert ac.p_close_colour(1.0 / k, 1.0) == pytest.approx(0.8413447, abs=1e-5)
    assert ac.p_close_colour(-0.5 / k, 0.25) == pytest.approx(0.8413447, abs=1e-5)
    assert ac.p_close_colour(0.4, 0.0) == 1.0
    assert ac.p_close_colour(0.0, 0.0) == 0.5
    assert ac.p_close_colour(0.5, -0.1) is None
    assert ac.p_close_colour(0.5, 1.1) is None
    assert ac.p_close_colour(float("nan"), 0.5) is None


def test_forming_monthly_and_weekly_context_november_2026():
    # Reproduce BTC November 2026 Monthly (1M) context as of 2026-11-07:
    # 19 prior closed months averaging ~87,000 + forming Nov 2026 month (open 78,354, high 81,196, low 74,888, close 75,392)
    # 20M SMA across 19x87,253.05 + 75,392 = (1,657,808 + 75,392)/20 = 86,660.0 -> price 75,392 is 'below' 20M SMA and 'red'.
    # Prior 2 closed months red (Sep, Oct) -> streak R2.
    m_bars = [_bar(85000, 91000, 81000, 87253.05, 1000) for _ in range(17)]
    m_bars.append(_bar(90000, 92000, 85000, 87253.05, 1000))  # red
    m_bars.append(_bar(88000, 89500, 78000, 87253.05, 1000))  # red
    # Forming Nov 2026 candle: 30 days = 2,592,000,000 ms; 6.6 days elapsed (~22%)
    t0 = 1_793_491_200_000
    span = 30 * 86_400_000
    now = t0 + int(0.22 * span)
    m_bars.append(_bar(78354, 81196, 74888, 75392, 500, t=t0, close_t=t0 + span - 1))

    # Weekly bars: 15 green/mixed, then 4 consecutive red weeks in Oct 2026 (R4), then forming week
    w_bars = [_bar(84000, 88000, 82000, 85000, 300) for _ in range(15)]
    for o_px, c_px in [(86000, 84000), (84000, 82000), (82000, 80000), (80000, 78354)]:
        w_bars.append(_bar(o_px, o_px + 1000, c_px - 500, c_px, 300))
    w_bars.append(_bar(78354, 81196, 74888, 75392, 200, t=t0, close_t=t0 + 7 * 86_400_000 - 1))

    # Daily bars: 19 prior days + forming day
    d_bars = [_bar(79000, 80500, 77500, 78500, 100) for _ in range(19)]
    d_bars.append(_bar(75208, 76416, 74888, 75392, 120))

    ctx = ac.build_mtf_context(m_bars, w_bars, d_bars, now_ms=now)
    assert ctx["htf_bias"] == "bearish"
    assert "1M red & below 20M SMA" in ctx["bias_reasons"]
    assert "1w streak R4" in ctx["bias_reasons"]
    assert ctx["monthly"]["colour"] == "red"
    assert ctx["monthly"]["elapsed_pct"] == pytest.approx(0.22, abs=1e-3)
    assert ctx["monthly"]["t_left"] == pytest.approx(0.78, abs=1e-3)
    assert ctx["monthly"]["pos_in_range"] == pytest.approx((75392 - 74888) / (81196 - 74888), abs=1e-4)
    assert ctx["weekly"]["streak"] == {"colour": "red", "count": 4, "label": "R4"}


def test_volume_profile_poc_va_and_multi_bin_lvn_detection():
    # Single-bin LVN case:
    # 75,000: vol 30 | 75,050: vol 5 (LVN) | 75,100: vol 40 (POC) | 75,150: vol 20 | 75,200: vol 5
    bars = [
        _bar(75010, 75010, 75010, 75010, 30),
        _bar(75060, 75060, 75060, 75060, 5),
        _bar(75110, 75110, 75110, 75110, 40),
        _bar(75160, 75160, 75160, 75160, 20),
        _bar(75210, 75210, 75210, 75210, 5),
    ]
    vp = ac.compute_volume_profile(bars, bin_size=50.0, va_share=0.70, lvn_ratio=0.25)
    assert vp is not None
    assert (vp["val"], vp["poc"], vp["vah"]) == (75050.0, 75100.0, 75250.0)
    assert vp["lvns"] == [75050.0]

    # Contiguous multi-bin LVN vacuum (bins 75,050 and 75,100 have 0 volume between 75,000 HVN and 75,150 POC):
    bars_gap = [
        _bar(75010, 75010, 75010, 75010, 35),
        _bar(75160, 75160, 75160, 75160, 65),
    ]
    vp_gap = ac.compute_volume_profile(bars_gap, bin_size=50.0, va_share=0.70, lvn_ratio=0.25)
    assert vp_gap is not None
    assert len(vp_gap["lvn_zones"]) == 1
    assert vp_gap["lvn_zones"][0]["low"] == 75050.0
    assert vp_gap["lvn_zones"][0]["high"] == 75150.0
    assert vp_gap["lvn_zones"][0]["bins"] == 2.0


def test_replay_2026_11_06_1500_utc_74810_v_sweep_long():
    # Exact Bybit perp 5m bars from CENSUS_5m_2026-10-03_11-07.md (lines 118-123) around Friday 2026-11-06 14:50 - 15:10 UTC:
    # Level = Sep-15 daily low 74,961 (and CBP 75,000 cluster).
    # Prior 12 bars: median 5m volume ~191.4 BTC (so 3,005 / 191.4 = 15.7x relative volume), non-knife approach.
    pre = [_bar(75850, 76100, 75650, 75800, v=191.4) for _ in range(12)]
    bars_1500 = [
        _bar(75819, 76137, 75691, 75692, v=1313.0),                 # 14:50
        _bar(75692, 75704, 75280, 75511, v=1862.0),                 # 14:55
        _bar(75511, 75568, 74929, 75046, v=2702.0, delta=-600.0),   # 15:00 sweeps below 74,961 to 74,929, closes 75,046
        _bar(75046, 75378, 74810, 75290, v=3005.0, delta=-450.0),   # 15:05 flushes to 74,810 (15.7x vol), reclaims 74,961 closing 75,290!
    ]
    series = pre + bars_1500
    inter = ac.classify_level_interaction(series, level_price=74961.0, level_side="support")
    assert inter["verdict"] == "FAST_REJECTION"
    assert inter["trade_bias"] == "long"
    assert inter["kind"] == "V2_sweep"
    assert inter["sweep_extreme"] == 74810.0
    assert inter["reclaim_close"] == 75290.0
    assert inter["max_rel_vol"] == pytest.approx(15.7, abs=0.1)
    assert inter["knife"] is False

    # Build trade plan at 15:05 reclaim close (75,290), stop 5 bps below 74,810 (= 74,772.60 -> 68.7 bps stop -> fee_r = 0.146 R <= 0.25 R!)
    # Targets: Session POC 76,150 (+860 pts = 1.66 gross R, 1.51 net R), Prior VAH 76,416 (+1,126 pts = 2.18 gross R, 2.03 net R)
    ctx = {"htf_bias": "bearish", "bias_reasons": ["1M red & below 20M SMA", "1w streak R4"]}
    plan = ac.build_auction_trade_plan(
        context=ctx,
        interaction=inter,
        entry_price=75290.0,
        targets=[("Session POC", 76150.0), ("Prior Day High / VAH", 76416.0)],
        stop_buffer_bps=5.0,
        fee_rt_bps=10.0,
    )
    assert plan["action"] == "TAKE_TRADE"
    assert plan["direction"] == "long"
    assert plan["setup_type"] == "failed_auction_reclaim"
    assert plan["sizing_tier"] == "scalp_counter_or_range"  # counter to 1M/1w bear bias -> disciplined scalp sizing
    assert plan["stop_bps"] == pytest.approx(68.72, abs=0.05)
    assert plan["fee_r"] == pytest.approx(0.146, abs=0.005)
    assert plan["primary_target"]["name"] == "Session POC"
    assert plan["primary_target"]["net_rr"] >= 1.45
    assert plan["runner_target"]["name"] == "Prior Day High / VAH"


def test_replay_2026_10_29_upper_sweep_short_with_htf_trend():
    # 2026-10-29: Prior day (10-28) VAH = 81,550, High = 81,823.
    # Price probes above 81,823 to 81,971 with large absorption delta (+1,200 buy delta on red/rejection bar, 6.5x vol)
    # and closes back at 81,480 inside prior VAH.
    pre = [_bar(81100, 81350, 80950, 81200, v=100.0) for _ in range(12)]
    probe = [
        _bar(81450, 81971, 81400, 81480, v=650.0, delta=1200.0),  # 1-bar upper sweep of 81,550 VAH & 81,823 high, closes 81,480
    ]
    inter = ac.classify_level_interaction(pre + probe, level_price=81550.0, level_side="resistance")
    assert inter["verdict"] == "FAST_REJECTION"
    assert inter["trade_bias"] == "short"
    assert inter["kind"] == "1bar_wick_sweep"
    assert inter["sweep_extreme"] == 81971.0
    assert inter["absorption_seen"] is True

    ctx = {"htf_bias": "bearish", "bias_reasons": ["1M red & below 20M SMA", "1w streak R3"]}
    plan = ac.build_auction_trade_plan(
        context=ctx,
        interaction=inter,
        entry_price=81480.0,
        targets=[("Prior 1d POC", 80200.0), ("Prior 1d VAL", 78900.0)],
        stop_buffer_bps=5.0,
        fee_rt_bps=10.0,
    )
    assert plan["action"] == "TAKE_TRADE"
    assert plan["direction"] == "short"
    assert plan["sizing_tier"] == "full_with_htf"  # aligned with 1M/1w bearish bias
    assert plan["stop_bps"] == pytest.approx(65.26, abs=0.1)
    assert plan["fee_r"] == pytest.approx(0.153, abs=0.005)
    assert plan["primary_target"]["name"] == "Prior 1d POC"
    assert plan["primary_target"]["net_rr"] > 2.0

    # Verify that if 1M is in a green bounce inside a macro bear ("rally_in_macro_bear" / "counter_trend_bounce_in_macro_bear"),
    # a SHORT at resistance IS aligned with the macro bear trend ("full_with_htf"), whereas a LONG is counter-trend ("scalp_counter_or_range"):
    ctx_bounce = {"htf_bias": "rally_in_macro_bear"}
    plan_bounce_short = ac.build_auction_trade_plan(
        context=ctx_bounce,
        interaction=inter,
        entry_price=81480.0,
        targets=[("Prior 1d POC", 80200.0)],
    )
    assert plan_bounce_short["sizing_tier"] == "full_with_htf"
    assert plan_bounce_short["primary_target"]["effective_rr"] < plan_bounce_short["primary_target"]["net_rr"]

    # Conversely, a long during "rally_in_macro_bear" is sized as scalp_counter_or_range:
    inter_long = dict(inter, level_side="support", trade_bias="long", sweep_extreme=80900.0)
    plan_bounce_long = ac.build_auction_trade_plan(
        context=ctx_bounce,
        interaction=inter_long,
        entry_price=81480.0,
        targets=[("Upper VAH", 83200.0)],
    )
    assert plan_bounce_long["sizing_tier"] == "scalp_counter_or_range"


def test_replay_2026_11_04_lvn_fast_traverse_long():
    # 2026-11-04 14:40 UTC: After reclaiming prior VAL, BTC hits an interior Low Volume Node at 78,200 on 4.5x volume
    # and slices cleanly through it to 78,650 without looking back, targeting the upper HVN/VAH at 80,500.
    pre = [_bar(77800, 78050, 77700, 77950, v=100.0) for _ in range(10)]
    impulse = [
        _bar(77950, 78680, 77940, 78650, v=450.0, delta=300.0),
    ]
    inter = ac.classify_level_interaction(pre + impulse, level_price=78200.0, level_side="resistance", level_kind="lvn")
    assert inter["verdict"] == "LVN_FAST_TRAVERSE"
    assert inter["trade_bias"] == "long"

    plan = ac.build_auction_trade_plan(
        context={"htf_bias": "counter_trend_bounce_in_macro_bear"},
        interaction=inter,
        entry_price=78650.0,
        targets=[("Upper HVN / VAH", 80500.0)],
        stop_buffer_bps=25.0,
        fee_rt_bps=10.0,
    )
    assert plan["action"] == "TAKE_TRADE"
    assert plan["direction"] == "long"
    assert plan["setup_type"] == "lvn_fast_traverse"
    assert plan["structural_stop"] < 78200.0


def test_double_probe_resets_reclaim_idx_to_final_reclaim():
    # Bar 0 pierces support 75,000 and closes above (75,050), Bar 1 dips and closes BELOW 75,000 (74,900),
    # Bar 2 sweeps to 74,800 and reclaims 75,000 closing at 75,200.
    # reclaim_idx must point to Bar 2 (close 75,200, V3_sweep), NOT Bar 0!
    pre = [_bar(75300, 75400, 75200, 75250, v=100.0) for _ in range(10)]
    probes = [
        _bar(75250, 75250, 74950, 75050, v=200.0),  # offset 0: 1st probe & bounce
        _bar(75050, 75060, 74880, 74900, v=250.0),  # offset 1: closes below 75,000 -> resets reclaim_idx!
        _bar(74900, 75220, 74800, 75200, v=500.0),  # offset 2: true V3 reclaim at 75,200
    ]
    inter = ac.classify_level_interaction(pre + probes, level_price=75000.0, level_side="support")
    assert inter["verdict"] == "FAST_REJECTION"
    assert inter["kind"] == "V3_sweep"
    assert inter["reclaim_close"] == 75200.0
    assert inter["sweep_extreme"] == 74800.0


def test_replay_2026_11_05_accepted_below_val_continuation_short():
    # 2026-11-05: Prior day (11-04) VAL = 79,500.
    # Instead of rejecting quickly, price closes 6 consecutive 5m bars (= 30m) below 79,500 without reclaiming -> ACCEPTED.
    pre = [_bar(79800, 79950, 79600, 79650, v=120.0) for _ in range(10)]
    accepted_bars = [
        _bar(79550, 79560, 79320, 79350, v=300.0),
        _bar(79350, 79420, 79250, 79300, v=240.0),
        _bar(79300, 79380, 79180, 79220, v=210.0),
        _bar(79220, 79290, 79100, 79150, v=190.0),
        _bar(79150, 79240, 79050, 79120, v=180.0),
        _bar(79120, 79190, 78980, 79020, v=220.0),
    ]
    inter = ac.classify_level_interaction(pre + accepted_bars, level_price=79500.0, level_side="support")
    assert inter["verdict"] == "ACCEPTED"
    assert inter["trade_bias"] == "continuation"
    assert inter["bars_beyond"] == 6

    # Because it is ACCEPTED below VAL (Value Area Acceptance Rule A: 77% continuation), build_auction_trade_plan builds a SHORT continuation!
    ctx = {"htf_bias": "bearish", "bias_reasons": ["1M red & below 20M SMA", "1w streak R4"]}
    plan = ac.build_auction_trade_plan(
        context=ctx,
        interaction=inter,
        entry_price=79020.0,
        targets=[("0.5x VA Extension", 77800.0), ("Prior Week Low", 75736.0)],
        stop_buffer_bps=25.0,
        fee_rt_bps=10.0,
    )
    assert plan["action"] == "TAKE_TRADE"
    assert plan["direction"] == "short"
    assert plan["setup_type"] == "va_acceptance_continuation"
    assert plan["structural_stop"] > 79500.0  # stop back inside prior VAL


def test_fee_trap_gate_blocks_tight_stop_scalps():
    # Reproduce the exact failure mode of Fabio RESCORE.md (5.3 bps stop on 10 bps taker fee -> fee = 1.88 R):
    pre = [_bar(80050, 80100, 80010, 80030, v=100.0) for _ in range(12)]
    tiny_sweep = [_bar(80010, 80035, 79985, 80020, v=400.0, delta=-200.0)]  # sweeps 80,000 by only $15 (1.9 bps)
    inter = ac.classify_level_interaction(pre + tiny_sweep, level_price=80000.0, level_side="support")
    assert inter["verdict"] == "FAST_REJECTION"

    plan = ac.build_auction_trade_plan(
        context={"htf_bias": "neutral"},
        interaction=inter,
        entry_price=80020.0,
        targets=[("POC", 80500.0)],
        stop_buffer_bps=2.0,  # total stop = (80020 - 79985)/80020 + 2 bps = 6.37 bps -> fee_r = 10 / 6.37 = 1.57 R!
        fee_rt_bps=10.0,
        max_fee_r=0.25,
    )
    assert plan["action"] == "SKIP_FEE_TRAP"
    assert plan["fee_r"] > 1.0


def test_knife_gate_blocks_vertical_crash_fades_including_short_pre_window():
    # Test with only 6 bars before touch_idx (fewer than 12, verifying the Flash audit fix that short windows don't fail open):
    pre = []
    px = 80000.0
    for _ in range(6):
        nxt = px - 370.0
        pre.append(_bar(px, px, nxt, nxt, v=200.0))
        px = nxt
    # bar 6 opens at 77,780 (-2.775% from 80,000), sweeps 77,700 to 77,400, closes 77,750
    knife_bar = [_bar(px, px + 10, 77400.0, 77750.0, v=900.0, delta=-500.0)]
    inter = ac.classify_level_interaction(pre + knife_bar, level_price=77700.0, level_side="support")
    assert inter["knife"] is True
    assert inter["verdict"] == "REJECTED_KNIFE_SKIP"

    plan = ac.build_auction_trade_plan(
        context={"htf_bias": "bearish"},
        interaction=inter,
        entry_price=77750.0,
        targets=[("POC", 79000.0)],
    )
    assert plan["action"] == "SKIP"

    # Also verify fail-closed behavior when touch_idx < 3 (insufficient pre-touch history to rule out a knife):
    assert ac.is_knife_approach(pre[:2] + knife_bar, touch_idx=2, side="support") is True


def test_claude_stage_d_fixes_stale_rejection_spread_range_and_causality():
    # 1. Stale rejection guard: if reclaim happened 5 bars ago (> max_bars_since_reclaim=3), verdict is STALE_REJECTION
    pre = [_bar(75300, 75400, 75200, 75250, v=100.0) for _ in range(10)]
    sweep_and_drift = [
        _bar(75250, 75300, 74850, 75150, v=400.0),  # offset 0: sweeps 75,000, reclaims 75,150
        _bar(75150, 75250, 75100, 75200, v=100.0),  # offset 1
        _bar(75200, 75300, 75150, 75250, v=100.0),  # offset 2
        _bar(75250, 75350, 75200, 75300, v=100.0),  # offset 3
        _bar(75300, 75400, 75250, 75350, v=100.0),  # offset 4: 4 bars after reclaim_idx=0 (> 3)
    ]
    inter_stale = ac.classify_level_interaction(
        pre + sweep_and_drift, level_price=75000.0, level_side="val", max_bars_since_reclaim=3
    )
    assert inter_stale["verdict"] == "STALE_REJECTION"
    assert inter_stale["trade_bias"] == "skip_stale"
    assert inter_stale["bars_since_reclaim"] == 4

    # 2. Volume profile spread_range=True distributes bar volume across [l..h] bins and reports poc_mid
    wide_bar = [_bar(75000, 75200, 75000, 75100, v=100.0)]
    vp_spread = ac.compute_volume_profile(wide_bar, bin_size=50.0, spread_range=True)
    assert vp_spread is not None
    assert vp_spread["poc_mid"] == vp_spread["poc"] + 25.0
    assert vp_spread["val"] == 75000.0 and vp_spread["vah"] >= 75200.0

    # 3. Causality check in evaluate_forming_candle raises ValueError if future bar is passed after now_ms
    with pytest.raises(ValueError, match="Causality violation"):
        ac.evaluate_forming_candle([_bar(75000, 75100, 74900, 75050, t=2000, close_t=3000)], now_ms=1000)



def test_acceptance_threshold_scales_with_bar_minutes():
    """census-acceptance-threshold-mislabel-1109: accept80 = 2x30m closes = 60 min (SOURCED); 6 bars is OURS."""
    pre = [_bar(79800, 79950, 79600, 79650, v=120.0) for _ in range(10)]
    below = [_bar(79550 - 70 * k, 79560 - 70 * k, 79320 - 70 * k, 79350 - 70 * k, v=200.0) for k in range(6)]
    bars = pre + below
    assert ac.classify_level_interaction(bars, 79500.0, "support")["verdict"] == "ACCEPTED"          # default: 6 bars (OURS)
    on5 = ac.classify_level_interaction(bars, 79500.0, "support", accept_minutes=60, bar_minutes=5)
    assert on5["verdict"] != "ACCEPTED"                                                              # 60 min = 12 x 5m closes
    on60 = ac.classify_level_interaction(bars, 79500.0, "support", accept_minutes=60, bar_minutes=60)
    assert on60["verdict"] == "ACCEPTED"                                                             # 60 min = 1 x 1h close
