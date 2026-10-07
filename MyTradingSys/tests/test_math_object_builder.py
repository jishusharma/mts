# test_math_object_builder.py — Unit tests for math_object_builder.py
# Run: pytest mts/tests/test_math_object_builder.py -v

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))

import json
from math_object_builder import build_math_object


def load_snapshot():
    with open(Path(__file__).parent.parent / "market_data" / "sample_btc_snapshot.json", "r") as f:
        return json.load(f)


# ============================================================
# DETERMINISM
# ============================================================

def test_determinism():
    snap = load_snapshot()
    m1 = build_math_object(snap)
    m2 = build_math_object(snap)
    assert m1 == m2


# ============================================================
# STRUCTURE
# ============================================================

def test_has_current_price():
    m = build_math_object(load_snapshot())
    assert "current_price" in m
    assert isinstance(m["current_price"], float)
    assert m["current_price"] > 0


def test_has_speed_flag():
    m = build_math_object(load_snapshot())
    assert "speed_picking_up" in m
    assert isinstance(m["speed_picking_up"], bool)


def test_has_zones():
    m = build_math_object(load_snapshot())
    assert "zones" in m
    assert isinstance(m["zones"], dict)
    assert len(m["zones"]) > 0


def test_has_confluence():
    m = build_math_object(load_snapshot())
    assert "confluence" in m
    assert isinstance(m["confluence"], list)


def test_has_hard_stops():
    m = build_math_object(load_snapshot())
    assert "hard_stops_compiled" in m
    assert isinstance(m["hard_stops_compiled"], dict)
    assert "price_not_at_zone" in m["hard_stops_compiled"]
    assert "any_zone_rr_below_threshold" in m["hard_stops_compiled"]
    assert "top_candidate_rr_below_threshold" in m["hard_stops_compiled"]
    assert "chasing_price" in m["hard_stops_compiled"]


# ============================================================
# ZONE FIELDS
# ============================================================

def test_zone_has_required_fields():
    m = build_math_object(load_snapshot())
    required = ["price", "distance", "substate", "cap", "tier",
                "trigger_valid_ct", "trigger_valid_tc", "trigger_valid_bo",
                "trigger_valid_scalp", "gross_rr", "net_rr", "rr_sanity",
                "stop", "target"]
    for name, z in m["zones"].items():
        for field in required:
            assert field in z, f"Zone {name} missing field: {field}"


def test_zone_prices_positive():
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        assert z["price"] > 0, f"Zone {name} has non-positive price: {z['price']}"


def test_zone_distances_in_range():
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        assert -1.0 <= z["distance"] <= 1.0, f"Zone {name} distance out of range: {z['distance']}"


def test_zone_substate_valid():
    m = build_math_object(load_snapshot())
    valid = {"at_zone", "above_zone", "below_zone"}
    for name, z in m["zones"].items():
        assert z["substate"] in valid, f"Zone {name} invalid substate: {z['substate']}"


def test_zone_tier_valid():
    m = build_math_object(load_snapshot())
    valid = {"trigger_ready", "conditional", "ignore"}
    for name, z in m["zones"].items():
        assert z["tier"] in valid, f"Zone {name} invalid tier: {z['tier']}"


def test_zone_tier_consistency():
    """Tier must be consistent with distance and cap."""
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        dist = abs(z["distance"])
        cap = z["cap"]
        if dist <= 0.001:
            assert z["tier"] == "trigger_ready"
        elif dist <= cap:
            assert z["tier"] == "conditional"
        else:
            assert z["tier"] == "ignore"


def test_zone_trigger_validity_consistency():
    """Trigger validity must match substate."""
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        sub = z["substate"]
        if sub == "at_zone":
            assert z["trigger_valid_ct"] is True
            assert z["trigger_valid_tc"] is True
            assert z["trigger_valid_scalp"] is True
            assert z["trigger_valid_bo"] is False
        elif sub in ("above_zone", "below_zone"):
            assert z["trigger_valid_ct"] is False
            assert z["trigger_valid_tc"] is False
            assert z["trigger_valid_scalp"] is False
            assert z["trigger_valid_bo"] is True


# ============================================================
# R:R LOGIC
# ============================================================

def test_rr_only_for_non_ignored_zones():
    """R:R should be computed only for zones within cap."""
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        if z["tier"] == "ignore":
            assert z["gross_rr"] is None
            assert z["net_rr"] is None
            assert z["rr_sanity"] is None


def test_rr_sanity_matches_gross():
    """rr_sanity must be True iff gross_rr >= 1.5."""
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        if z["gross_rr"] is not None:
            expected = z["gross_rr"] >= 1.5
            assert z["rr_sanity"] == expected, (
                f"Zone {name}: gross_rr={z['gross_rr']}, sanity={z['rr_sanity']}"
            )


def test_net_rr_uses_fee_model():
    """B070: net_rr = (reward - 2*taker*entry) / (risk + 2*taker*entry), not gross * 0.75."""
    m = build_math_object(load_snapshot())
    for name, z in m["zones"].items():
        if z["gross_rr"] is not None:
            cost = 2.0 * 0.0005 * z["price"]
            expected = round((abs(z["target"] - z["price"]) - cost) / (abs(z["price"] - z["stop"]) + cost), 4)
            assert abs(z["net_rr"] - expected) < 0.0001, (
                f"Zone {name}: net_rr={z['net_rr']}, expected={expected}"
            )


# ============================================================
# CONFLUENCE
# ============================================================

def test_confluence_zones_exist():
    m = build_math_object(load_snapshot())
    for c in m["confluence"]:
        for zname in c["zones"]:
            assert zname in m["zones"], f"Confluence references unknown zone: {zname}"


def test_confluence_midpoint_reasonable():
    m = build_math_object(load_snapshot())
    for c in m["confluence"]:
        prices = [m["zones"][z]["price"] for z in c["zones"]]
        expected_mid = sum(prices) / len(prices)
        assert abs(c["midpoint"] - expected_mid) < 0.01


def test_confluence_spread_nonnegative():
    m = build_math_object(load_snapshot())
    for c in m["confluence"]:
        assert c["spread"] >= 0


def test_confluence_at_least_two_zones():
    m = build_math_object(load_snapshot())
    for c in m["confluence"]:
        assert len(c["zones"]) >= 2


# ============================================================
# HARD STOPS
# ============================================================

def test_hard_stops_boolean():
    m = build_math_object(load_snapshot())
    for k, v in m["hard_stops_compiled"].items():
        assert isinstance(v, bool), f"hard_stop {k} is not bool: {type(v)}"


def test_price_not_at_zone_matches_tiers():
    m = build_math_object(load_snapshot())
    any_trigger_ready = any(z["tier"] == "trigger_ready" for z in m["zones"].values())
    assert m["hard_stops_compiled"]["price_not_at_zone"] == (not any_trigger_ready)


def test_chasing_price_matches_tiers():
    m = build_math_object(load_snapshot())
    all_ignore = all(z["tier"] == "ignore" for z in m["zones"].values())
    assert m["hard_stops_compiled"]["chasing_price"] == all_ignore


# ============================================================
# SCHEMA COMPATIBILITY — v1.2.0 (flat) vs old (wrapped "data")
# Added: 2026-09-01
# ============================================================

from math_object_builder import _is_old_schema, _normalize_snapshot

LIVE_V120 = {
    "timestamp_utc": "2026-09-01T05:21:06.253981600Z",
    "asset": "BTCUSDT",
    "current_price": 78784.5,
    "weekly_vp": {"poc": 78537.47, "vah": 78722.75, "val": 77786.35, "shape": "B", "prior_week_poc": 79284.54, "two_week_ago_poc": 77250.28},
    "daily_vp": {"poc": 78711.9, "vah": 78922.62, "val": 78390.82, "shape": "B"},
    "post_funding_vp": {"poc": 78573.33, "vah": 78928.42, "val": 78078.21, "shape": "B"},
    "intraday_4h_vp": {"poc": 78695.04, "vah": 78866.85, "val": 78634.41, "shape": "B"},
    "vwap": {"price": 78575.58, "slope": "falling", "bands": {"+1s": 78784.24, "+2s": 78992.9, "-1s": 78366.91, "-2s": 78158.25}},
    "cvd": {"value": -398.267, "slope": "rising", "divergence": False, "last_3_delta": ["negative", "negative", "positive"], "cvd_recent": {"slope_1h": "rising", "slope_4h": "rising", "delta_1h": 260.829, "delta_4h": 404.376}},
    "trade_flow": {"net_delta_1m": -36.041, "net_delta_5m": -100.0, "net_delta_15m": -200.0, "net_delta_1h": -500.0},
    "structure": {"1h": {"swing_high": 79228.5, "swing_low": 77663.1, "stale": False}, "15m": {"swing_high": 78947.7, "swing_low": 78150.0, "stale": False}, "5m": {"swing_high": 78947.7, "swing_low": 78652.2, "stale": False}},
    "order_book_depth": {"bid_ask_ratio": 1.07},
    "conditions": {"price_vs_poc": "above", "price_vs_va": "in_va", "vp_shape": "B", "vwap_slope": "falling", "cvd_slope": "rising", "cvd_divergence": False, "cvd_trade_flow_aligned": False, "fvg_unfilled_count": 2, "fvg_nearest_unfilled": {"type": "bearish", "top": 78805.9, "bottom": 78784.5}, "book_imbalance": 1.07, "funding_extreme": False, "oi_trend": "flat", "speed_picking_up": False, "volume_spike_at_level": False, "rejection_wick_at_zone": False},
    "prior_day": {"close": 78549.6, "high": 79228.5, "low": 77350.7, "poc": 77981.64, "vah": 78527.45, "val": 77465.87},
    "funding": {"current_rate": 1.0E-4, "extreme": False},
    "open_interest": {"direction": "flat", "change_1h_pct": 0.1},
    "session_timing": {"current_session": "asian", "funding_reset_window": False, "us_equity_open_window": False, "us_equity_open_in_minutes": 488},
    "liquidation_warning": {"status": "none"}
}


def test_schema_detection_old():
    """Old schema has 'data' wrapper."""
    assert _is_old_schema({"data": {"current_price": 100.0}}) is True


def test_schema_detection_new():
    """New v1.2.0 schema is flat."""
    assert _is_old_schema({"current_price": 100.0, "daily_vp": {"poc": 99.0}}) is False


def test_v120_current_price():
    m = build_math_object(LIVE_V120)
    assert m["current_price"] == 78784.5


def test_v120_zone_count():
    m = build_math_object(LIVE_V120)
    assert len(m["zones"]) >= 24


def test_v120_trigger_ready_exists():
    m = build_math_object(LIVE_V120)
    assert any(z["tier"] == "trigger_ready" for z in m["zones"].values())


def test_v120_per_tf_structure():
    m = build_math_object(LIVE_V120)
    assert m["zones"]["1h_swing_high"]["price"] == 79228.5
    assert m["zones"]["15m_swing_high"]["price"] == 78947.7
    assert m["zones"]["5m_swing_high"]["price"] == 78947.7
    assert m["zones"]["1h_swing_low"]["price"] == 77663.1
    assert m["zones"]["15m_swing_low"]["price"] == 78150.0
    assert m["zones"]["5m_swing_low"]["price"] == 78652.2


def test_v120_fvg_from_conditions():
    m = build_math_object(LIVE_V120)
    fvg = m["zones"]["fvg_nearest"]
    expected_mid = (78805.9 + 78784.5) / 2.0
    assert abs(fvg["price"] - expected_mid) < 0.01


def test_v120_4h_and_pf_vp_present():
    """4h VP is Tom-sourced core. post_funding_vp was demoted 2026-09-24
    to a display-only module per PROJECT_VISION.md doctrine; it must not
    appear in the zone list."""
    m = build_math_object(LIVE_V120)
    assert "intraday_4h_vp_poc" in m["zones"]
    assert "post_funding_vp_poc" not in m["zones"]


def test_v120_confluence_detected():
    m = build_math_object(LIVE_V120)
    assert len(m["confluence"]) >= 2


def test_v120_hard_stops():
    m = build_math_object(LIVE_V120)
    assert m["hard_stops_compiled"]["price_not_at_zone"] is False
    assert m["hard_stops_compiled"]["chasing_price"] is False


def test_backward_compat_old_fixture():
    """Old fixture must still produce valid output after schema fix."""
    m = build_math_object(load_snapshot())
    assert m["current_price"] > 0
    assert len(m["zones"]) > 0
    assert "daily_vp_poc" in m["zones"]  # old volume_profile -> daily_vp


# ============================================================
# BUG-007 (2026-09-10) - split any-zone vs top-candidate R:R flag
# ============================================================

def test_bug_007_new_keys_present():
    """BUG-007: both R:R flags must exist; legacy key must be gone."""
    m = build_math_object(load_snapshot())
    hs = m["hard_stops_compiled"]
    assert "any_zone_rr_below_threshold" in hs
    assert "top_candidate_rr_below_threshold" in hs
    assert "rr_below_threshold" not in hs


def test_bug_007_top_candidate_passes_while_zone_fails():
    """BUG-007: rank-1 candidate passing rr_sanity must yield top_candidate=False."""
    snap = dict(LIVE_V120)
    snap["setup_candidates"] = [{
        "rank": 1,
        "setup_type": "scalp_long",
        "direction": "long",
        "zone": {"name": "vwap_band_-2", "price": 77900.0, "type": "vwap_band_-2"},
        "math": {"distance_pct": 0.1, "distance_cap": 0.2, "tier": "conditional",
                 "substate": "above", "stop": 77800.0, "target": 78500.0,
                 "gross_rr": 6.0, "net_rr": 4.5, "net_rr_sanity": True, "rr_sanity": True},
        "proof": {"rejection_wick": "STRONG", "speed": {"picking_up": False},
                  "cvd_aligned": False, "book_imbalance": 1.0},
        "score": {"raw": 80, "confidence": "B", "proof_count": 3, "confluence_bonus": 0},
    }]
    m = build_math_object(snap)
    hs = m["hard_stops_compiled"]
    assert hs["top_candidate_rr_below_threshold"] is False, (
        "rank-1 candidate passes rr_sanity, top flag must be False, got " + str(hs["top_candidate_rr_below_threshold"])
    )


def test_bug_007_top_candidate_fails():
    """BUG-007: rank-1 candidate failing rr_sanity must yield top_candidate=True."""
    snap = dict(LIVE_V120)
    snap["setup_candidates"] = [{
        "rank": 1,
        "setup_type": "ct_long",
        "direction": "long",
        "zone": {"name": "weekly_val", "price": 78000.0, "type": "weekly_val"},
        "math": {"distance_pct": 0.1, "distance_cap": 0.5, "tier": "conditional",
                 "substate": "below", "stop": 77900.0, "target": 78100.0,
                 "gross_rr": 1.0, "net_rr": 0.75, "net_rr_sanity": False, "rr_sanity": False},
        "proof": {"rejection_wick": "WEAK", "speed": {"picking_up": False},
                  "cvd_aligned": False, "book_imbalance": 1.0},
        "score": {"raw": 50, "confidence": "C", "proof_count": 1, "confluence_bonus": 0},
    }]
    m = build_math_object(snap)
    hs = m["hard_stops_compiled"]
    assert hs["top_candidate_rr_below_threshold"] is True, (
        "rank-1 candidate fails rr_sanity, top flag must be True, got " + str(hs["top_candidate_rr_below_threshold"])
    )


def test_bug_007_no_candidates_defaults_false():
    """BUG-007: no setup_candidates key -> top_candidate flag defaults to False."""
    snap = {k: v for k, v in LIVE_V120.items() if k != "setup_candidates"}
    m = build_math_object(snap)
    assert m["hard_stops_compiled"]["top_candidate_rr_below_threshold"] is False


# ============================================================
# B072 - current_price input validation (fail closed)
# ============================================================

import math as _math
import pytest


@pytest.mark.parametrize("bad", ["x", None, 0, -5.0, float("nan"), float("inf"), True])
def test_b072_bad_current_price_raises_flat_schema(bad):
    snap = dict(LIVE_V120)
    snap["current_price"] = bad
    with pytest.raises(ValueError, match="current_price"):
        build_math_object(snap)


@pytest.mark.parametrize("bad", ["x", None])
def test_b072_bad_current_price_raises_old_schema(bad):
    snap = load_snapshot()
    snap["data"]["current_price"] = bad
    with pytest.raises(ValueError, match="current_price"):
        build_math_object(snap)


def test_b072_missing_current_price_raises():
    snap = {k: v for k, v in LIVE_V120.items() if k != "current_price"}
    with pytest.raises(ValueError, match="current_price"):
        build_math_object(snap)


# ============================================================
# B073 - emitted rr values and rr_sanity agree (round, then sanity)
# ============================================================

def test_b073_sanity_matches_emitted_gross_rr(monkeypatch):
    import math_object_builder as mob
    # 1.49996 rounds to 1.5 on output; the sanity flag must be computed on that same rounded value (>= 1.5).
    monkeypatch.setattr(mob, "calculate_gross_rr", lambda e, t, s: 1.49996)
    monkeypatch.setattr(mob, "calculate_net_rr", lambda e, t, s, *a, **k: 1.996)
    m = mob.build_math_object(dict(LIVE_V120))
    rows = [z for z in m["zones"].values() if z["gross_rr"] is not None]
    assert rows, "need at least one evaluated zone"
    for z in rows:
        assert z["gross_rr"] == 1.5
        assert z["net_rr"] == 1.996
        assert z["rr_sanity"] is (z["gross_rr"] >= 1.5), "rr_sanity disagrees with the emitted gross_rr"


# ============================================================
# BOOK IMBALANCE 0.0 NO-DATA BUG (2026-10-02)
# Operator-approved fix: 0.0 = no order-book data (not ask-heavy)
# ============================================================

def test_book_imbalance_zero_no_contradiction_long():
    """book_imbalance=0.0 (no data) should NOT trigger ask-heavy contradiction for LONG.

    Reference: Java SetupCandidatesBuilder.java:581 skips 0.0 as "no data".
    Operator-approved 2026-09-30 (SUPERVISOR_INBOX 22:30Z item 1).
    """
    snap = dict(LIVE_V120)
    snap["setup_candidates"] = [{
        "rank": 1,
        "setup_type": "ct_long",
        "direction": "long",
        "zone": {"name": "weekly_val", "price": 78000.0, "type": "weekly_val"},
        "math": {"distance_pct": 0.1, "distance_cap": 0.5, "tier": "conditional",
                 "substate": "below", "stop": 77900.0, "target": 78100.0,
                 "gross_rr": 2.0, "net_rr": 1.5, "net_rr_sanity": True, "rr_sanity": True},
        "proof": {"rejection_wick": "WEAK", "speed": {"picking_up": False},
                  "cvd_aligned": False, "book_imbalance": 0.0},
        "score": {"raw": 70, "confidence": "B", "proof_count": 2, "confluence_bonus": 0},
    }]
    m = build_math_object(snap)
    details = m.get("proof_direction_details", [])
    assert not any("ask-heavy vs LONG" in str(d) for d in details), (
        f"book_imbalance=0.0 (no data) must not trigger ask-heavy contradiction. Got: {details}"
    )


def test_book_imbalance_small_positive_contradicts_long():
    """book_imbalance=0.2 (ask-heavy, valid data) should trigger ask-heavy contradiction for LONG."""
    snap = dict(LIVE_V120)
    snap["setup_candidates"] = [{
        "rank": 1,
        "setup_type": "ct_long",
        "direction": "long",
        "zone": {"name": "weekly_val", "price": 78000.0, "type": "weekly_val"},
        "math": {"distance_pct": 0.1, "distance_cap": 0.5, "tier": "conditional",
                 "substate": "below", "stop": 77900.0, "target": 78100.0,
                 "gross_rr": 2.0, "net_rr": 1.5, "net_rr_sanity": True, "rr_sanity": True},
        "proof": {"rejection_wick": "WEAK", "speed": {"picking_up": False},
                  "cvd_aligned": False, "book_imbalance": 0.2},
        "score": {"raw": 70, "confidence": "B", "proof_count": 2, "confluence_bonus": 0},
    }]
    m = build_math_object(snap)
    details = m.get("proof_direction_details", [])
    assert any("book_imbalance=0.2 ask-heavy vs LONG" in str(d) for d in details), (
        f"book_imbalance=0.2 (ask-heavy, valid data) must trigger ask-heavy contradiction. Got: {details}"
    )
