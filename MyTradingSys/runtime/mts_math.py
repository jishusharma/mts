# mts_math.py — Deterministic math layer for MTS v4.2.0-p5
# NO price level selection. NO trade construction. Pure math only.
# All functions are deterministic: same inputs -> same outputs, always.
#
# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\runtime\mts_math.py

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# B070: friction comes from the exchange fee model (backtest/fees.py, B081), not a flat 25% haircut.
_REPO = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
sys.path.insert(0, str(_REPO / "MyTradingSys" / "backtest"))
from fees import DERIBIT_TAKER  # noqa: E402


def calculate_distance(price: float, zone_price: float) -> float:
    if zone_price == 0:
        raise ValueError("zone_price cannot be zero")
    return (price - zone_price) / zone_price


def get_zone_substate(price: float, zone_price: float, fuzz: float = 0.001) -> str:
    dist = calculate_distance(price, zone_price)
    if abs(dist) <= fuzz:
        return "at_zone"
    if dist > fuzz:
        return "above_zone"
    return "below_zone"


def get_distance_cap(zone_type: str, speed_picking_up: bool = False) -> float:
    caps = {
        "weekly_vah": 0.005, "weekly_val": 0.005, "weekly_poc": 0.005,
        "daily_vah": 0.004, "daily_val": 0.004, "daily_poc": 0.004,
        "4h_vah": 0.004, "4h_val": 0.004, "4h_poc": 0.004,
        "pf_vah": 0.004, "pf_val": 0.004, "pf_poc": 0.004,
        "prior_day_vah": 0.004, "prior_day_val": 0.004, "prior_day_poc": 0.004,
        "swing_high_1h": 0.005, "swing_low_1h": 0.005,
        "swing_high_15m": 0.003, "swing_low_15m": 0.003,
        "swing_high_5m": 0.003, "swing_low_5m": 0.003,
        "vwap_band": 0.002, "fvg": 0.002,
    }
    base = caps.get(zone_type.lower(), 0.003)
    if speed_picking_up:
        base *= 2.0
    return base


def get_tier(distance: float, cap: float) -> str:
    abs_dist = abs(distance)
    if abs_dist <= 0.001:
        return "trigger_ready"
    if abs_dist <= cap:
        return "conditional"
    return "ignore"


def check_trigger_validity(substate: str, setup_type: str) -> bool:
    substate = substate.lower()
    setup = setup_type.lower()
    if setup in ("ct_short", "ct_long", "tc_long", "tc_short", "scalp"):
        return substate == "at_zone"
    if setup in ("bo_long", "bo_short"):
        return substate in ("above_zone", "below_zone")
    return False


def calculate_gross_rr(entry: float, target: float, stop: float) -> float:
    reward = abs(target - entry)
    risk = abs(entry - stop)
    if risk == 0:
        return 0.0
    return reward / risk


def calculate_net_rr(entry: float, target: float, stop: float, taker: float = DERIBIT_TAKER) -> float:
    """B070 fee model (FORMULAS.md section 17): both legs market/taker, cost = 2 * taker * entry in price units.
    net_rr = (|target - entry| - cost) / (|entry - stop| + cost). Zero risk or non-positive denominator -> 0.0."""
    risk = abs(entry - stop)
    if risk == 0:
        return 0.0
    cost = 2.0 * taker * entry
    return (abs(target - entry) - cost) / (risk + cost)


def calculate_rr_sanity(gross_rr: float, threshold: float = 1.5) -> bool:
    return gross_rr >= threshold


def detect_confluence(zone_levels: List[Dict[str, Any]], threshold: float = 0.003) -> List[Dict[str, Any]]:
    if not zone_levels:
        return []
    sorted_zones = sorted(zone_levels, key=lambda z: z["price"])
    clusters: List[List[Dict[str, Any]]] = []
    current_cluster: List[Dict[str, Any]] = [sorted_zones[0]]
    for zone in sorted_zones[1:]:
        cluster_min = min(z["price"] for z in current_cluster)
        cluster_max = max(z["price"] for z in current_cluster)
        zone_price = zone["price"]
        cluster_mid = (cluster_min + cluster_max) / 2.0
        if abs(zone_price - cluster_mid) / cluster_mid <= threshold:
            current_cluster.append(zone)
        else:
            clusters.append(current_cluster)
            current_cluster = [zone]
    clusters.append(current_cluster)
    result = []
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        prices = [z["price"] for z in cluster]
        names = [z["name"] for z in cluster]
        midpoint = sum(prices) / len(prices)
        spread = max(prices) - min(prices)
        result.append({"zones": names, "midpoint": midpoint, "spread": spread})
    return result


# ============================================================
# STATE MANAGEMENT — v4.2.0-p4
# Persistent state diff for delta-aware trading cards.
# ============================================================

def parse_state(filepath: str) -> Dict[str, Any]:
    state: Dict[str, Any] = {}
    current_section = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith("## "):
                current_section = line_stripped[3:].strip()
                state[current_section] = {}
            elif current_section and ":" in line_stripped and not line_stripped.startswith("#"):
                key, val = line_stripped.split(":", 1)
                state[current_section][key.strip()] = val.strip()
    return state


def _cast(val):
    """Cast value to bool/float/str. Handles both strings and native types."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return float(val)
    if not isinstance(val, str):
        return val
    lower = val.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    try:
        return float(val)
    except ValueError:
        return val


def _get_snapshot_value(snapshot: Dict[str, Any], path: str):
    keys = path.split(".")
    node = snapshot
    for k in keys:
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return None
    return node


def diff_state(old_state: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    changes = []
    structural_change = False
    state_transition = False

    field_map = [
        ("WEEKLY.poc", "weekly_vp.poc", "structural"),
        ("WEEKLY.vah", "weekly_vp.vah", "structural"),
        ("WEEKLY.val", "weekly_vp.val", "structural"),
        ("WEEKLY.shape", "weekly_vp.shape", "structural"),
        ("WEEKLY.prior_week_poc", "weekly_vp.prior_week_poc", "structural"),
        ("WEEKLY.two_week_ago_poc", "weekly_vp.two_week_ago_poc", "structural"),
        ("DAILY.poc", "daily_vp.poc", "structural"),
        ("DAILY.vah", "daily_vp.vah", "structural"),
        ("DAILY.val", "daily_vp.val", "structural"),
        ("DAILY.shape", "daily_vp.shape", "structural"),
        ("POST_FUNDING.poc", "post_funding_vp.poc", "structural"),
        ("POST_FUNDING.vah", "post_funding_vp.vah", "structural"),
        ("POST_FUNDING.val", "post_funding_vp.val", "structural"),
        ("INTRADAY_4H.poc", "intraday_4h_vp.poc", "structural"),
        ("INTRADAY_4H.vah", "intraday_4h_vp.vah", "structural"),
        ("INTRADAY_4H.val", "intraday_4h_vp.val", "structural"),
        ("PRIOR_DAY.close", "prior_day.close", "structural"),
        ("PRIOR_DAY.high", "prior_day.high", "structural"),
        ("PRIOR_DAY.low", "prior_day.low", "structural"),
        ("PRIOR_DAY.poc", "prior_day.poc", "structural"),
        ("PRIOR_DAY.vah", "prior_day.vah", "structural"),
        ("PRIOR_DAY.val", "prior_day.val", "structural"),
        ("SWING.1h_high", "structure.1h.swing_high", "structural"),
        ("SWING.1h_low", "structure.1h.swing_low", "structural"),
        ("SWING.1h_stale", "structure.1h.stale", "structural"),
        ("SWING.15m_high", "structure.15m.swing_high", "structural"),
        ("SWING.15m_low", "structure.15m.swing_low", "structural"),
        ("SWING.15m_stale", "structure.15m.stale", "structural"),
        ("SWING.5m_high", "structure.5m.swing_high", "structural"),
        ("SWING.5m_low", "structure.5m.swing_low", "structural"),
        ("SWING.5m_stale", "structure.5m.stale", "structural"),
        ("VWAP.price", "vwap.price", "contextual"),
        ("VWAP.slope", "vwap.slope", "contextual"),
        ("CVD.value", "cvd.value", "contextual"),
        ("CVD.slope", "cvd.slope", "contextual"),
        ("TRADE_FLOW.net_delta_1m", "trade_flow.net_delta_1m", "contextual"),
        ("FUNDING.current_rate", "funding.current_rate", "contextual"),
        ("FUNDING.extreme", "funding.extreme", "contextual"),
        ("FUNDING.open_interest_direction", "open_interest.direction", "contextual"),
        ("FUNDING.open_interest_change_1h_pct", "open_interest.change_1h_pct", "contextual"),
        ("SPOT_PERP.basis_pct", "spot_perp_basis.basis_pct", "contextual"),
        ("STATE.classification", "conditions.vp_shape", "positional"),
    ]

    old_price = None
    new_price = _get_snapshot_value(snapshot, "current_price")

    for state_key, snap_path, significance in field_map:
        sec, k = state_key.split(".", 1)
        old_val = old_state.get(sec, {}).get(k)
        new_val = _get_snapshot_value(snapshot, snap_path)
        if old_val is not None and new_val is not None:
            old_cast = _cast(old_val)
            new_cast = _cast(new_val)
            if old_cast != new_cast:
                changes.append({"field": state_key, "old": old_cast, "new": new_cast, "significance": significance})
                if significance == "structural":
                    structural_change = True
                if state_key == "STATE.classification":
                    state_transition = True

    old_price_str = old_state.get("META", {}).get("last_price")
    if old_price_str:
        try:
            old_price = float(old_price_str)
        except ValueError:
            old_price = None
    if old_price is not None and new_price is not None:
        price_delta_pct = calculate_distance(new_price, old_price)
    else:
        price_delta_pct = 0.0

    substate_changes = []
    key_zones = [
        ("WEEKLY.vah", "weekly_vp.vah"), ("WEEKLY.val", "weekly_vp.val"),
        ("WEEKLY.poc", "weekly_vp.poc"), ("DAILY.vah", "daily_vp.vah"),
        ("DAILY.val", "daily_vp.val"), ("DAILY.poc", "daily_vp.poc"),
        ("POST_FUNDING.vah", "post_funding_vp.vah"), ("POST_FUNDING.val", "post_funding_vp.val"),
        ("POST_FUNDING.poc", "post_funding_vp.poc"), ("INTRADAY_4H.vah", "intraday_4h_vp.vah"),
        ("INTRADAY_4H.val", "intraday_4h_vp.val"), ("INTRADAY_4H.poc", "intraday_4h_vp.poc"),
        ("VWAP.price", "vwap.price"),
    ]
    for state_key, snap_path in key_zones:
        sec, k = state_key.split(".", 1)
        old_zone_price_str = old_state.get(sec, {}).get(k)
        new_zone_price = _get_snapshot_value(snapshot, snap_path)
        if old_zone_price_str is not None and new_zone_price is not None:
            old_zone_price = float(old_zone_price_str)
            if old_price is not None:
                old_sub = get_zone_substate(old_price, old_zone_price)
            else:
                old_sub = "unknown"
            new_sub = get_zone_substate(new_price, new_zone_price)
            if old_sub != new_sub:
                substate_changes.append({"zone": state_key, "old_substate": old_sub, "new_substate": new_sub})

    old_count_str = old_state.get("STATE", {}).get("unchanged_count", "0")
    try:
        old_count = int(old_count_str)
    except ValueError:
        old_count = 0
    unchanged_count = 0 if structural_change else old_count + 1

    return {
        "changes": changes,
        "price_delta_pct": round(price_delta_pct, 6),
        "substate_changes": substate_changes,
        "structural_change": structural_change,
        "state_transition": state_transition,
        "unchanged_count": unchanged_count,
    }


def update_state(old_state: Dict[str, Any], snapshot: Dict[str, Any], new_verdict: str = "") -> Dict[str, Any]:
    new_state = {
        "META": {
            "updated_utc": snapshot.get("timestamp_utc", ""),
            "last_snapshot": f"{snapshot.get('asset', 'UNKNOWN')}_{snapshot.get('timestamp_utc', '').replace('T', '_').replace(':', '').replace('-', '').replace('Z', '')[:12]}",
            "asset": snapshot.get("asset", ""),
            "last_price": str(snapshot.get("current_price", 0.0)),
        },
        "WEEKLY": {
            "poc": str(_get_snapshot_value(snapshot, "weekly_vp.poc") or ""),
            "vah": str(_get_snapshot_value(snapshot, "weekly_vp.vah") or ""),
            "val": str(_get_snapshot_value(snapshot, "weekly_vp.val") or ""),
            "shape": str(_get_snapshot_value(snapshot, "weekly_vp.shape") or ""),
            "prior_week_poc": str(_get_snapshot_value(snapshot, "weekly_vp.prior_week_poc") or ""),
            "two_week_ago_poc": str(_get_snapshot_value(snapshot, "weekly_vp.two_week_ago_poc") or ""),
        },
        "DAILY": {
            "poc": str(_get_snapshot_value(snapshot, "daily_vp.poc") or ""),
            "vah": str(_get_snapshot_value(snapshot, "daily_vp.vah") or ""),
            "val": str(_get_snapshot_value(snapshot, "daily_vp.val") or ""),
            "shape": str(_get_snapshot_value(snapshot, "daily_vp.shape") or ""),
        },
        "POST_FUNDING": {
            "poc": str(_get_snapshot_value(snapshot, "post_funding_vp.poc") or ""),
            "vah": str(_get_snapshot_value(snapshot, "post_funding_vp.vah") or ""),
            "val": str(_get_snapshot_value(snapshot, "post_funding_vp.val") or ""),
        },
        "INTRADAY_4H": {
            "poc": str(_get_snapshot_value(snapshot, "intraday_4h_vp.poc") or ""),
            "vah": str(_get_snapshot_value(snapshot, "intraday_4h_vp.vah") or ""),
            "val": str(_get_snapshot_value(snapshot, "intraday_4h_vp.val") or ""),
        },
        "PRIOR_DAY": {
            "close": str(_get_snapshot_value(snapshot, "prior_day.close") or ""),
            "high": str(_get_snapshot_value(snapshot, "prior_day.high") or ""),
            "low": str(_get_snapshot_value(snapshot, "prior_day.low") or ""),
            "poc": str(_get_snapshot_value(snapshot, "prior_day.poc") or ""),
            "vah": str(_get_snapshot_value(snapshot, "prior_day.vah") or ""),
            "val": str(_get_snapshot_value(snapshot, "prior_day.val") or ""),
        },
        "SWING": {}, "STATE": {}, "VWAP": {}, "CVD": {}, "TRADE_FLOW": {}, "FUNDING": {}, "SPOT_PERP": {},
    }
    for tf in ["1h", "15m", "5m"]:
        high = _get_snapshot_value(snapshot, f"structure.{tf}.swing_high")
        low = _get_snapshot_value(snapshot, f"structure.{tf}.swing_low")
        stale = _get_snapshot_value(snapshot, f"structure.{tf}.stale")
        if high is not None:
            new_state["SWING"][f"{tf}_high"] = str(high)
        if low is not None:
            new_state["SWING"][f"{tf}_low"] = str(low)
        if stale is not None:
            new_state["SWING"][f"{tf}_stale"] = str(stale).lower()
    vp_shape = _get_snapshot_value(snapshot, "conditions.vp_shape")
    price_vs_va = _get_snapshot_value(snapshot, "conditions.price_vs_va")
    # STATE.classification used to be a raw copy of vp_shape, which
    # collapsed to a fixed letter. Rewritten 2026-09-17 to match the
    # Java classifyState logic in SetupCandidatesBuilder.java.
    _vs = _get_snapshot_value(snapshot, "conditions.vwap_slope")
    _cs = _get_snapshot_value(snapshot, "conditions.cvd_slope")
    _pva = _get_snapshot_value(snapshot, "conditions.price_vs_va")
    if (_vs in ("flat", "sideways")) and _cs == "flat" and _pva == "in_va":
        _state = "balance"
    elif _cs == "divergent":
        _state = "trend_unhealthy"
    elif _pva in ("above_vah", "below_val"):
        _state = "trend_healthy"
    elif _cs == "aligned":
        _state = "trend_healthy"
    else:
        _state = "balance"
    new_state["STATE"]["classification"] = _state
    new_state["STATE"]["vp_shape"] = str(vp_shape or "UNKNOWN")
    new_state["STATE"]["position"] = str(price_vs_va or "UNKNOWN")
    vwap_price = _get_snapshot_value(snapshot, "vwap.price")
    vwap_slope = _get_snapshot_value(snapshot, "vwap.slope")
    if vwap_price is not None:
        new_state["VWAP"]["price"] = str(vwap_price)
    if vwap_slope is not None:
        new_state["VWAP"]["slope"] = str(vwap_slope)
    vwap_bands = _get_snapshot_value(snapshot, "vwap.bands")
    if isinstance(vwap_bands, dict):
        for band_key, band_val in vwap_bands.items():
            if band_val is not None:
                new_state["VWAP"][f"band_{band_key}"] = str(band_val)
    cvd_val = _get_snapshot_value(snapshot, "cvd.value")
    cvd_slope = _get_snapshot_value(snapshot, "cvd.slope")
    if cvd_val is not None:
        new_state["CVD"]["value"] = str(cvd_val)
    if cvd_slope is not None:
        new_state["CVD"]["slope"] = str(cvd_slope)
    tf_delta = _get_snapshot_value(snapshot, "trade_flow.net_delta_1m")
    if tf_delta is not None:
        new_state["TRADE_FLOW"]["net_delta_1m"] = str(tf_delta)
    # SPOT_PERP section
    sp_basis = _get_snapshot_value(snapshot, "spot_perp_basis.basis_pct")
    sp_dir = _get_snapshot_value(snapshot, "spot_perp_basis.direction")
    if sp_basis is not None:
        new_state["SPOT_PERP"]["basis_pct"] = str(sp_basis)
    if sp_dir is not None:
        new_state["SPOT_PERP"]["direction"] = str(sp_dir)
    # FUNDING section
    funding_fields = [
        ("current_rate", "funding.current_rate"),
        ("extreme", "funding.extreme"),
        ("open_interest_direction", "open_interest.direction"),
        ("open_interest_change_1h_pct", "open_interest.change_1h_pct"),
    ]
    for state_key, snap_path in funding_fields:
        val = _get_snapshot_value(snapshot, snap_path)
        if val is not None:
            new_state["FUNDING"][state_key] = str(val)
    delta = diff_state(old_state, snapshot)
    old_verdict = old_state.get("STATE", {}).get("last_verdict", "")
    if new_verdict:
        resolved_verdict = new_verdict
    elif delta["structural_change"]:
        resolved_verdict = ""
    else:
        resolved_verdict = old_verdict
    new_state["STATE"]["last_verdict"] = resolved_verdict
    new_state["STATE"]["unchanged_count"] = str(delta["unchanged_count"])
    return new_state


def format_state(state: Dict[str, Any]) -> str:
    """Return state as markdown string (current_market_state.md format).

    Caller is responsible for persisting to disk. This function performs
    no I/O — it is pure formatting.
    """
    lines = [
        "# CURRENT MARKET STATE",
        "# Purpose: Persistent slow-moving structural data for delta computation.",
        "#   Updated per JSON snapshot. Overwritten (not appended).",
        "#   Read at session start. Updated after each card generation.",
        r"# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\runtime\current_market_state.md",
        "#",
        "# Format: Markdown sections with key: value pairs.",
        "#   Sections: META/WEEKLY/DAILY/POST_FUNDING/INTRADAY_4H/PRIOR_DAY/SWING/STATE/VWAP/CVD/TRADE_FLOW/FUNDING/SPOT_PERP",
        "#   Values are raw numbers/strings. No units in values.",
        "#   \"unchanged_count\" = consecutive snapshots with no structural change.",
        "",
        "---",
        "",
    ]
    for section, data in state.items():
        lines.append(f"## {section}")
        for key, val in data.items():
            lines.append(f"{key}: {val}")
        lines.append("")
    lines.append("# END")
    lines.append("")
    return "\n".join(lines)


def write_state(state: Dict[str, Any], filepath: str) -> None:
    """Write state dict back to current_market_state.md format.

    DEPRECATED: Use format_state() + caller-side persistence instead.
    This function exists for backward compatibility in environments
    where the filepath is writable.
    """
    content = format_state(state)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ============================================================
# Precondition checkers (schema v1.1.0)
# State-management checks. Not engine rules. Rule 32 N/A.
# Paths verified against data_schema_v1.2.0.md + sample_btc_snapshot.json.
# NOTE: rule text says "speed regime"; snapshot has no speed.regime.
#       Mapped to data.conditions.speed_picking_up (bool).
# ============================================================

_MISSING = object()


def _path_get(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return _MISSING
    return cur


_VWAP_OK = ("sideways", "flat")


def check_scalp_preconditions(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []

    v = _path_get(snapshot, "vwap.slope")
    if v is _MISSING:
        reasons.append("missing:vwap.slope")
    elif v not in _VWAP_OK:
        reasons.append("vwap_slope_not_sideways:" + repr(v))

    s = _path_get(snapshot, "conditions.speed_picking_up")
    if s is _MISSING:
        reasons.append("missing:conditions.speed_picking_up")
    elif s is True:
        reasons.append("speed_picking_up_true")

    f = _path_get(snapshot, "session_timing.funding_reset_window")
    if f is _MISSING:
        reasons.append("missing:session_timing.funding_reset_window")
    elif f is not False:
        reasons.append("funding_reset_window_not_false:" + repr(f))

    return {"ok": len(reasons) == 0, "reasons": reasons}


_CLAUSE_OPS = {
    "price_current_above": ("current_price", lambda v, o: v > o),
    "price_current_below": ("current_price", lambda v, o: v < o),
    "cvd_slope":           ("cvd.slope",     lambda v, o: v == o),
    "vwap_slope":          ("vwap.slope",    lambda v, o: v == o),
}


def check_invalidation(clause: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(clause, dict) or not clause:
        return {"fired": None, "reason": "empty_or_non_dict_clause", "unverifiable": []}

    unverifiable = []
    failed_ops = []

    for op, operand in clause.items():
        spec = _CLAUSE_OPS.get(op)
        if spec is None:
            unverifiable.append("unknown_op:" + str(op))
            continue
        path, cmp = spec
        val = _path_get(snapshot, path)
        if val is _MISSING:
            unverifiable.append("missing:" + path)
            continue
        try:
            ok = bool(cmp(val, operand))
        except Exception:
            unverifiable.append("type_error:" + op)
            continue
        if not ok:
            failed_ops.append(op)

    if unverifiable:
        return {"fired": None, "reason": "unverifiable", "unverifiable": unverifiable}
    if not failed_ops:
        return {"fired": True, "reason": "all_clauses_met", "unverifiable": []}
    return {"fired": False, "reason": "failed:" + ",".join(failed_ops), "unverifiable": []}

