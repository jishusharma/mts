# math_object_builder.py - Build math_object from DSA snapshot
# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\runtime\math_object_builder.py
#
# SCHEMA COMPATIBILITY: Handles old (wrapped "data"), new (flat v1.2.0), and v1.3.2 (setup_candidates) DSA JSON.
#   Old: {"data": {"current_price": ..., "volume_profile": {...}, "structure": {"swing_high": ...}}}
#   New v1.2.0: {"current_price": ..., "daily_vp": {...}, "weekly_vp": {...}, "structure": {"1h": {...}, "15m": {...}}}
#   v1.3.2: {"setup_candidates": [{"rank": 1, "setup_type": ..., "zone": ..., "math": ..., "proof": ...}]}
#
# v1.3.2: When setup_candidates present, rank-1 candidate is added to math_object as
# "setup_candidate" field. Judgment layer uses this preferentially during transition.
# Legacy zone extraction continues for backward compatibility (2-week transition).
#
# All zone price levels come from the snapshot. No AI-invented prices.

import math
from typing import List, Dict, Any, Optional, Tuple
from mts_math import (
    calculate_distance,
    get_zone_substate,
    get_distance_cap,
    get_tier,
    check_trigger_validity,
    calculate_gross_rr,
    calculate_net_rr,
    calculate_rr_sanity,
    detect_confluence,
)
from net_rr_floor import NetRrFloorError, load_floor
from runner_min_distance import RunnerMinDistanceError, load_runner_min_distance_pct


# ============================================================
# SCHEMA NORMALIZATION
# ============================================================

def _is_old_schema(snapshot: Dict[str, Any]) -> bool:
    """Old schema has a "data" wrapper containing all fields."""
    return "data" in snapshot and isinstance(snapshot["data"], dict)


def _normalize_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize old or new schema into a common internal format.

    Normalized structure:
    {
        "current_price": float,
        "daily_vp": {"poc": ..., "vah": ..., "val": ...},
        "weekly_vp": {"poc": ..., "vah": ..., "val": ..., "prior_week_poc": ...},
        "post_funding_vp": {"poc": ..., "vah": ..., "val": ...},
        "intraday_4h_vp": {"poc": ..., "vah": ..., "val": ...},
        "vwap": {"price": ..., "bands": {...}, "slope": ...},
        "structure": {
            "1h": {"swing_high": ..., "swing_low": ..., "stale": ...},
            "15m": {...},
            "5m": {...}
        },
        "conditions": {"speed_picking_up": ..., "fvg_nearest_unfilled": {...}, "fvg_unfilled_count": ...},
        "prior_day": {"close": ..., "high": ..., "low": ..., "poc": ..., "vah": ..., "val": ...},
        "trade_flow": {"net_delta": ...},
        "order_book_depth": {"bid_ask_ratio": ...},
        "naked_poc": {"naked_pocs": [...]},  # optional
    }
    """
    if _is_old_schema(snapshot):
        data = snapshot["data"]
        normalized: Dict[str, Any] = {
            "current_price": data.get("current_price", 0.0),
            "daily_vp": data.get("volume_profile", {}),
            "weekly_vp": data.get("weekly_vp", {}),
            "post_funding_vp": {},
            "intraday_4h_vp": {},
            "vwap": data.get("vwap", {}),
            "structure": {},
            "conditions": data.get("conditions", {}),
            "prior_day": data.get("prior_day", {}),
            "trade_flow": data.get("trade_flow", {}),
            "order_book_depth": data.get("order_book_depth", {}),
            "naked_poc": data.get("naked_poc", {}),
        }
        # Old structure is flat - map to 1h
        old_struct = data.get("structure", {})
        if old_struct:
            normalized["structure"]["1h"] = old_struct
        # Old FVG is an array - pick first unfilled as nearest_unfilled
        old_fvgs = data.get("fvg", [])
        for fvg in old_fvgs:
            if not fvg.get("filled", True):
                normalized["conditions"]["fvg_nearest_unfilled"] = fvg
                break
        return normalized
    else:
        # New v1.2.0 schema - mostly flat, just ensure all keys exist
        return {
            "current_price": snapshot.get("current_price", 0.0),
            "daily_vp": snapshot.get("daily_vp", {}),
            "weekly_vp": snapshot.get("weekly_vp", {}),
            "post_funding_vp": snapshot.get("post_funding_vp", {}),
            "intraday_4h_vp": snapshot.get("intraday_4h_vp", {}),
            "vwap": snapshot.get("vwap", {}),
            "structure": snapshot.get("structure", {}),
            "conditions": snapshot.get("conditions", {}),
            "prior_day": snapshot.get("prior_day", {}),
            "trade_flow": snapshot.get("trade_flow", {}),
            "order_book_depth": snapshot.get("order_book_depth", {}),
            "naked_poc": snapshot.get("naked_poc", {}),
            "setup_candidates": snapshot.get("setup_candidates", []),
            "cvd": snapshot.get("cvd", {}),
        }


# ============================================================
# ZONE EXTRACTION
# ============================================================

# RULE TOM-166 (overlaps: volume nodes, value highs, POCs), TOM-144 (VPOC as equilibrium level)
def _extract_zones(normalized: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all structural zone prices from a NORMALIZED snapshot.

    Returns list of {"name": str, "price": float, "type": str} dicts.
    Zone types match mts_math.get_distance_cap() keys.
    """
    zones: List[Dict[str, Any]] = []

    # --- Volume Profiles ---
    vp_map = [
        ("weekly_vp", "weekly_poc", "weekly_vah", "weekly_val"),
        ("daily_vp", "daily_poc", "daily_vah", "daily_val"),
        ("intraday_4h_vp", "4h_poc", "4h_vah", "4h_val"),
    ]
    for vp_key, poc_type, vah_type, val_type in vp_map:
        vp = normalized.get(vp_key, {})
        if vp.get("poc"):
            zones.append({"name": f"{vp_key}_poc", "price": vp["poc"], "type": poc_type})
        if vp.get("vah"):
            zones.append({"name": f"{vp_key}_vah", "price": vp["vah"], "type": vah_type})
        if vp.get("val"):
            zones.append({"name": f"{vp_key}_val", "price": vp["val"], "type": val_type})

    # --- VWAP and bands ---
    vwap = normalized.get("vwap", {})
    if vwap.get("price"):
        zones.append({"name": "vwap", "price": vwap["price"], "type": "vwap_band"})
    bands = vwap.get("bands", {})
    for key, val in bands.items():
        # Handle Unicode artifact keys like "+1?" "+2?" etc.
        clean_key = key.replace("?", "").replace("sigma", "").strip()
        zones.append({"name": f"vwap_band_{clean_key}", "price": val, "type": "vwap_band"})

    # --- Prior day ---
    pd = normalized.get("prior_day", {})
    if pd.get("poc"):
        zones.append({"name": "prior_day_poc", "price": pd["poc"], "type": "prior_day_poc"})
    if pd.get("vah"):
        zones.append({"name": "prior_day_vah", "price": pd["vah"], "type": "prior_day_vah"})
    if pd.get("val"):
        zones.append({"name": "prior_day_val", "price": pd["val"], "type": "prior_day_val"})
    if pd.get("close"):
        zones.append({"name": "prior_day_close", "price": pd["close"], "type": "prior_day_close"})

    # --- Structure (per-TF swing levels) ---
    struct = normalized.get("structure", {})
    for tf in ["1h", "15m", "5m"]:
        s = struct.get(tf, {})
        if s.get("swing_high"):
            zones.append({"name": f"{tf}_swing_high", "price": s["swing_high"], "type": f"swing_high_{tf}"})
        if s.get("swing_low"):
            zones.append({"name": f"{tf}_swing_low", "price": s["swing_low"], "type": f"swing_low_{tf}"})

    # --- FVG (from conditions, not array) ---
    cond = normalized.get("conditions", {})
    fvg = cond.get("fvg_nearest_unfilled")
    if fvg and isinstance(fvg, dict):
        mid = (fvg.get("top", 0) + fvg.get("bottom", 0)) / 2.0
        if mid > 0:
            zones.append({"name": "fvg_nearest", "price": mid, "type": "fvg"})

    # --- Naked POCs (optional) ---
    naked = normalized.get("naked_poc", {}).get("naked_pocs", [])
    for i, np in enumerate(naked):
        if np.get("poc"):
            zones.append({"name": f"naked_poc_{np.get('date', i)}", "price": np["poc"], "type": "weekly_poc"})

    return zones


# ============================================================
# STOP / TARGET SELECTION
# ============================================================

# RULE TOM-074/TOM-072 (stop beyond last swing); TF pairing NO-SOURCE (A06)
def _swing_tf_for_zone(ztype: str) -> str:
    """Map zone type to the appropriate swing TF for stop placement.

    Tom principle: match swing TF to zone precision.
    - Weekly zone -> 1h swing
    - Daily/4H/PF zone -> 15m swing
    - VWAP/FVG/Scalp -> 5m swing
    """
    if ztype.startswith("weekly_"):
        return "1h"
    if ztype.startswith(("daily_", "4h_", "pf_", "prior_day_")):
        return "15m"
    return "5m"


def _pick_stop_target_runner(
    zone: Dict[str, Any],
    price: float,
    normalized: Dict[str, Any]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Return (stop, target, runner_target) for R:R calculation from normalized snapshot data.

    DATA-DRIVEN selection:
    - Stop = nearest structural level beyond zone (per-TF swing matched to zone type)
    - Target = nearest sourced volume node (POC/HVN) in trade direction with netRR >= floor, else the farthest

    Returns target None if no node lies in the trade direction.
    """
    struct = normalized.get("structure", {})
    zone_price = zone["price"]
    zone_type = zone["type"]

    # Determine direction
    is_above = zone_price > price

    # Pick appropriate swing TF
    swing_tf = _swing_tf_for_zone(zone_type)
    swing = struct.get(swing_tf, {})
    swing_high = swing.get("swing_high")
    swing_low = swing.get("swing_low")

    # Collect all VP POCs for target selection
    # RULE TOM-018/TOM-102 (target = next high volume price/area: POCs and HVNs)
    all_pocs = []
    # DEMOTED 2026-09-24: post_funding_vp removed from target pool. Module, not core.
    for vp_key in ["weekly_vp", "daily_vp", "intraday_4h_vp"]:
        vp = normalized.get(vp_key, {})
        if vp.get("poc"):
            all_pocs.append(vp["poc"])
        # HVNs (MarketDataSnapshot.buildVp "hvns") are target candidates: Tom [TOM-018] "it looks for
        # the next high volume price and that is your target". Ignore non-numeric / non-positive entries.
        for hvn in vp.get("hvns") or []:
            if isinstance(hvn, (int, float)) and not isinstance(hvn, bool) and hvn > 0:
                all_pocs.append(hvn)
    # Add prior_day POC
    pd = normalized.get("prior_day", {})
    if pd.get("poc"):
        all_pocs.append(pd["poc"])

    # STOP selection
    # RULE TOM-074/TOM-073/TOM-072 (stop below last low / above last high); no fallback by design
    stop = None
    if is_above:
        # Short setup - stop above zone
        if swing_high is not None and swing_high > zone_price:
            stop = swing_high
    else:
        # Long setup - stop below zone
        if swing_low is not None and swing_low < zone_price:
            stop = swing_low

    # TARGET selection. RULE TOM-018/TOM-102: target = next high volume price/area (POCs, HVNs).
    # Operator ruling 2026-10-03: VWAP / VAL / VAH / prior-day high-low members and the 2.0R-3.5R window are NO-SOURCE
    # (A07-A10) and removed. Mirrors SetupCandidatesBuilder.pickTarget (Java): nearest node in direction whose
    # netRR >= floor (net_rr_floor.json), else the farthest node in direction; runner = next node beyond the target.
    try:
        floor = load_floor()
    except NetRrFloorError:
        floor = float("nan")   # nothing qualifies -> farthest node (fail closed; the verdict gate decides)
    try:
        runner_min_pct = load_runner_min_distance_pct()
    except RunnerMinDistanceError:
        runner_min_pct = float("nan")   # no node qualifies -> no runner (single target; fail closed)
    target, runner = pick_target(all_pocs, zone_price, stop, is_above, floor, runner_min_pct)
    return stop, target, runner


def pick_target(nodes, zone_price, stop, is_short, floor, runner_min_pct=0.0):
    """(target, runner_target) from volume nodes; (None, None) if no node lies in the trade direction.

    runner = next node beyond the target at least runner_min_pct percent of the target price away from it (closer
    nodes are skipped), else None. NaN runner_min_pct qualifies nothing (no runner). Mirrors the Java pickTarget."""
    in_dir = sorted((p for p in nodes if (p < zone_price if is_short else p > zone_price)),
                    key=lambda p: abs(p - zone_price))
    if not in_dir:
        return None, None
    idx = len(in_dir) - 1   # fallback: farthest
    if stop is not None and stop != zone_price:
        risk = abs(zone_price - stop)
        for i, p in enumerate(in_dir):
            net = calculate_net_rr(zone_price, p, stop)
            if net >= floor:   # NaN floor never qualifies
                idx = i
                break
    else:
        idx = 0   # no stop -> no R:R; nearest node
    target = in_dir[idx]
    runner = None
    for p in in_dir[idx + 1:]:
        if abs(p - zone_price) > abs(target - zone_price) and abs(p - target) / target * 100.0 >= runner_min_pct:
            runner = p
            break
    return target, runner


def _pick_stop_target(zone, price, normalized):
    """(stop, target) - see _pick_stop_target_runner."""
    stop, target, _runner = _pick_stop_target_runner(zone, price, normalized)
    return stop, target


# ============================================================
# MAIN BUILDER
# ============================================================

def build_math_object(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Compile a DSA snapshot into a math_object for the judgment layer.

    Handles both old (wrapped "data") and new v1.2.0 (flat) DSA schemas.
    v1.3.2: If setup_candidates present, includes rank-1 candidate for
    judgment layer preferential use. Legacy zone computation continues
    during 2-week transition period.
    The math_object contains ONLY computable values. No AI judgment.
    """
    normalized = _normalize_snapshot(snapshot)
    price = normalized["current_price"]
    # B072: fail closed on a missing / non-numeric / non-finite / non-positive price (was passed through -> "aligned").
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        raise ValueError("invalid current_price: %r (need a finite number > 0)" % (price,))
    speed = normalized.get("conditions", {}).get("speed_picking_up", False)

    zones = _extract_zones(normalized)

    zone_math: Dict[str, Any] = {}
    confluence_input: List[Dict[str, Any]] = []

    for zone in zones:
        name = zone["name"]
        zprice = zone["price"]
        ztype = zone["type"]

        dist = calculate_distance(price, zprice)
        substate = get_zone_substate(price, zprice)
        cap = get_distance_cap(ztype, speed_picking_up=speed)
        tier_label = get_tier(dist, cap)

        # Trigger validity per setup type
        trigger_ct = check_trigger_validity(substate, "ct_long")
        trigger_tc = check_trigger_validity(substate, "tc_long")
        trigger_bo = check_trigger_validity(substate, "bo_long")
        trigger_scalp = check_trigger_validity(substate, "scalp")

        # R:R - only for zones within cap
        gross_rr = None
        net_rr = None
        rr_sanity = None
        stop = None
        target = None
        runner_target = None

        if tier_label != "ignore":
            stop, target, runner_target = _pick_stop_target_runner(zone, price, normalized)
            if stop is not None and target is not None:
                gross_rr = calculate_gross_rr(zprice, target, stop)
                net_rr = calculate_net_rr(zprice, target, stop)
                # B073: round first (the emitted precision), then run the sanity check on that same value.
                gross_rr = round(gross_rr, 4)
                net_rr = round(net_rr, 4)
                rr_sanity = calculate_rr_sanity(gross_rr)

        zone_math[name] = {
            "price": zprice,
            "distance": round(dist, 6),
            "substate": substate,
            "cap": cap,
            "tier": tier_label,
            "trigger_valid_ct": trigger_ct,
            "trigger_valid_tc": trigger_tc,
            "trigger_valid_bo": trigger_bo,
            "trigger_valid_scalp": trigger_scalp,
            "gross_rr": round(gross_rr, 4) if gross_rr is not None else None,
            "net_rr": round(net_rr, 4) if net_rr is not None else None,
            "rr_sanity": rr_sanity,
            "stop": stop,
            "target": target,
            "runner_target": runner_target if runner_target is not None else 0,
        }

        confluence_input.append({"name": name, "price": zprice})

    # Confluence detection
    confluence = detect_confluence(confluence_input, threshold=0.003)

    # Hard stops compiled
    # BUG-007 (2026-09-10): split any-zone R:R from top-candidate R:R.
    # BUG-011 (2026-09-12): read net_rr_sanity (>= 2.0 NET per engine Sec 6 row 4),
    #   not rr_sanity (gross >= 1.5). Prior code was a doc-code mismatch.
    # 2026-10-02: the NET floor is MyTradingSys/system/net_rr_floor.json (single source), compared to the
    #   candidate's net_rr here; Java's net_rr_sanity flag is no longer read.
    # - any_zone_rr_below_threshold: True if ANY evaluated zone fails rr_sanity (gross).
    #   Advisory only. Does NOT gate trade execution.
    # - top_candidate_rr_below_threshold: True only if the rank-1 setup_candidate
    #   net_rr is below the floor (unreadable floor -> True, fail closed; a candidate with no net_rr at all, an
    #   old schema, falls back to its net_rr_sanity flag as before). This is what hard stop #4 reads.
    any_trigger_ready = any(z["tier"] == "trigger_ready" for z in zone_math.values())
    any_zone_rr_fail = any(z["rr_sanity"] is False for z in zone_math.values())
    all_ignore = all(z["tier"] == "ignore" for z in zone_math.values())

    top_candidate_rr_fail = False
    _candidates = snapshot.get("setup_candidates")
    if _candidates and isinstance(_candidates, list) and len(_candidates) > 0:
        _top_math = _candidates[0].get("math", {})
        try:
            _net = _top_math.get("net_rr") if isinstance(_top_math, dict) else None
            if _net is None:
                top_candidate_rr_fail = _top_math.get("net_rr_sanity") is False if isinstance(_top_math, dict) else False
            else:
                top_candidate_rr_fail = float(_net) < load_floor()
        except (NetRrFloorError, TypeError, ValueError):
            top_candidate_rr_fail = True

    result: Dict[str, Any] = {
        "current_price": price,
        "speed_picking_up": speed,
        "zones": zone_math,
        "confluence": confluence,
        "hard_stops_compiled": {
            "price_not_at_zone": not any_trigger_ready,
            "any_zone_rr_below_threshold": any_zone_rr_fail,
            "top_candidate_rr_below_threshold": top_candidate_rr_fail,
            "chasing_price": all_ignore,
        },
    }

    # v1.3.2: Add setup_candidates if present (preferred by judgment layer)
    candidates = normalized.get("setup_candidates")
    if candidates and isinstance(candidates, list) and len(candidates) > 0:
        result["setup_candidate"] = candidates[0]

        # BUG-008 (2026-09-10): proof direction consistency check.
        _top = candidates[0]
        _dir = _top.get("direction", "")
        _proof = _top.get("proof", {}) if isinstance(_top.get("proof"), dict) else {}
        _fa = _proof.get("finished_auction", {}) if isinstance(_proof.get("finished_auction"), dict) else {}
        _fa_dir = _fa.get("direction", "")
        # .get(key, default) returns None (not the default) when the key is present with a JSON null, so absent and
        # null are both handled here. null/absent/0.0/non-numeric = no order-book data (BT path): UNAVAILABLE, never 1.0.
        _book = _proof.get("book_imbalance")
        _book_ok = isinstance(_book, (int, float)) and not isinstance(_book, bool) and _book != 0.0
        result["proof_book_imbalance"] = _book if _book_ok else "UNAVAILABLE"
        _last3 = snapshot.get("cvd", {}).get("last_3_delta", [])
        _contradictions = []
        if _dir == "short":
            if _fa_dir == "sell":
                _contradictions.append("finished_auction=SELL vs SHORT")
            if isinstance(_book, (int, float)) and not isinstance(_book, bool) and _book > 3.0:
                _contradictions.append(f"book_imbalance={_book} bid-heavy vs SHORT")
            if isinstance(_last3, list) and len(_last3) == 3 and all(x == "positive" for x in _last3):
                _contradictions.append("last_3_delta=pos,pos,pos vs SHORT")
        elif _dir == "long":
            if _fa_dir == "buy":
                _contradictions.append("finished_auction=BUY vs LONG")
            # 0.0 = no order-book data (Java SetupCandidatesBuilder.java:581 skips 0.0; MarketDataSnapshot.java:213-214),
            # not ask-heavy. Operator-approved 2026-09-30 (SUPERVISOR_INBOX 22:30Z item 1). None already fails isinstance.
            if isinstance(_book, (int, float)) and not isinstance(_book, bool) and _book != 0.0 and _book < 0.33:
                _contradictions.append(f"book_imbalance={_book} ask-heavy vs LONG")
            if isinstance(_last3, list) and len(_last3) == 3 and all(x == "negative" for x in _last3):
                _contradictions.append("last_3_delta=neg,neg,neg vs LONG")
        result["proof_direction_status"] = "contradiction" if _contradictions else "aligned"
        result["proof_direction_details"] = _contradictions
        # Override speed_picking_up from candidate proof if available
        top_proof = candidates[0].get("proof", {})
        if isinstance(top_proof, dict) and "speed" in top_proof:
            speed_proof = top_proof["speed"]
            if isinstance(speed_proof, dict) and "picking_up" in speed_proof:
                result["speed_picking_up"] = speed_proof["picking_up"]

    return result
