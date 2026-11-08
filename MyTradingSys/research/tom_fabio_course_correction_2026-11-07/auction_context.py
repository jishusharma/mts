"""Plain Auction Theory & Multi-Timeframe Context Evaluator (Tom + Fabio Course Correction, 2026-11-07).

Replaces over-gated 1m z-score "rocket science" and location-blind tight-stop scalping with plain auction theory:
  1. Top-Down Context Ladder (Monthly 1M -> Weekly 1w -> Prior Day 1d -> Developing Session):
     - Forming candle state: open, high, low, close, elapsed fraction (tau), remaining fraction (t_left),
       displacement in ATR14 (d_atr), close-colour retention probability P_close_colour = Phi(|d_atr|*1.5958 / sqrt(t_left)),
       prior closed candle streak (e.g. R4 = 4 red candles in a row), and 20-period SMA regime.
     - Volume Profile (POC, VAH, VAL, 70% share on $50 bins, plus interior Low Volume Nodes / LVNs and contiguous
       multi-bin LVN vacuums) across Prior Month, Developing Month, Prior Week, Developing Week, and Prior Day.
       Note: `compute_volume_profile` expects 1m bars (or spreads bar volume across [l, h] when range > bin_size) so
       wider bars never leave artificial empty-bin LVNs.
  2. Level Interaction Classifier (Acceptance vs. Fast Rejection / Imbalance vs. LVN Fast Traverse):
     - Distinguishes when price is ACCEPTED at/beyond a level (consecutive bars beyond >= 6 on 5m = 2x30m closes beyond
       VA edge [SOURCED: accept80.py 77% continuation below prior-day VAL], or >= 4 consecutive closes beyond [OURS])
       vs. REJECTED QUICKLY from a level (fast approach, time_at_level <= 3 bars, relative volume spike >= 2.0x vs
       pre-touch baseline or absorption delta opposed to the probe, and V-sweep reclaim close back inside the level
       within 1-4 bars and recent within max_bars_since_reclaim, with knife_state == False)
       vs. LVN_FAST_TRAVERSE (price slicing cleanly through an interior low-volume vacuum on >= 2.0x relative volume
       toward the next HVN/POC).
  3. Trade Construction & Fee-Safe Stop Geometry (Idea + Proof + Math):
     - Enforces structural stops beyond the sweep wick / balance extreme (per d-stops-follow-trade-1106).
     - Enforces the Fee-to-Stop Geometry Gate: round-trip fee in R (fee_bps / stop_bps) must be <= max_fee_r
       (default 0.25 R, i.e., stop >= 40 bps on a 10 bps round-trip taker fill, or maker entry), preventing the
       5-8 bps tight-stop fee trap that destroyed -1.423 R to -2.912 R in past Tom/Fabio backtests.
     - Reports both linear `net_rr = gross_rr - fee_r` and exact fee-inclusive `effective_rr = (gross_rr - fee_r) / (1 + fee_r)`
       (Matching ExecutionMathConstants.netRR where a stop loss costs `1 + fee_r`).

Pure functions, zero lookahead, stdlib only. Fail closed: missing or short data returns None / explicit reason.
"""
from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from MyTradingSys.backtest import fees as _mts_fees

SIGMA_K = 2.0 * math.sqrt(2.0 / math.pi)  # 1.5957691216: sigma_bar = ATR14 / SIGMA_K (Brownian range constant)
DEFAULT_BIN_SIZE = 50.0
DEFAULT_VA_SHARE = 0.70
DEFAULT_TAKER_RT_BPS = _mts_fees.DERIBIT_TAKER * 20000.0  # 2 x 5 bps taker = 10 bps round-trip (from fees.py)
DEFAULT_MAKER_RT_BPS = _mts_fees.BINANCE_MAKER * 10000.0  # 2 bps per side maker (from fees.py)
DEFAULT_MAX_FRICTION_R = 0.25    # friction in R > 0.25 R is a tight-stop trap
DEFAULT_MIN_NET_RR = 1.20    # minimum net R:R after round-trip friction

BEARISH_HTF_BIASES = frozenset({"bearish", "rally_in_macro_bear", "counter_trend_bounce_in_macro_bear"})
BULLISH_HTF_BIASES = frozenset({"bullish", "pullback_in_macro_bull"})

LEVEL_SIDE_ALIASES = {
    "support": "support",
    "val": "support",
    "low": "support",
    "resistance": "resistance",
    "vah": "resistance",
    "high": "resistance",
}


def _phi(x: float) -> float:
    """Standard normal CDF Phi(x)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def p_close_colour(d_atr: float, t_left: float) -> Optional[float]:
    """Null probability P(forming bar closes with its current colour) from displacement d_atr and t_left in [0, 1]."""
    if not (isinstance(d_atr, (int, float)) and isinstance(t_left, (int, float))):
        return None
    if not (math.isfinite(d_atr) and math.isfinite(t_left)) or t_left < 0.0 or t_left > 1.0:
        return None
    if t_left == 0.0:
        return 1.0 if d_atr != 0.0 else 0.5
    return _phi(abs(d_atr) * SIGMA_K / math.sqrt(t_left))


def compute_atr14(bars: Sequence[Dict[str, float]]) -> Optional[float]:
    """Mean True Range of the last 14 closed bars before the forming bar (bars[-1] is the forming bar).
    Requires at least 16 bars (1 prior close + 14 closed TRs + 1 forming bar). Fail closed -> None."""
    if not bars or len(bars) < 16:
        return None
    n = len(bars)
    tr_sum = 0.0
    for i in range(n - 15, n - 1):
        h, l, pc = float(bars[i]["h"]), float(bars[i]["l"]), float(bars[i - 1]["c"])
        if h < l:
            return None
        tr_sum += max(h - l, abs(h - pc), abs(l - pc))
    atr = tr_sum / 14.0
    return atr if atr > 0.0 else None


def compute_sma(bars: Sequence[Dict[str, float]], length: int, use_closed_only: bool = False) -> Optional[float]:
    """Simple moving average of closes over `length` bars (Matches ma_strip.js convention: last `length` closes
    including the forming bar by default, or closed bars only when `use_closed_only=True`). Fail closed -> None."""
    seq = bars[:-1] if use_closed_only else bars
    if not seq or len(seq) < length or length <= 0:
        return None
    closes = [float(b["c"]) for b in seq[-length:]]
    return sum(closes) / float(length)


def closed_streak(bars: Sequence[Dict[str, float]]) -> Dict[str, Any]:
    """Count consecutive same-colour closed bars immediately preceding the forming bar (bars[-1]).
    Returns {'colour': 'green'|'red'|None, 'count': int, 'label': e.g. 'R4' or 'G2' or 'FLAT'}."""
    if not bars or len(bars) < 2:
        return {"colour": None, "count": 0, "label": "NONE"}
    closed = bars[:-1]
    col = None
    cnt = 0
    for b in reversed(closed):
        o, c = float(b["o"]), float(b["c"])
        cur = "green" if c > o else ("red" if c < o else None)
        if cur is None:
            break
        if col is None:
            col = cur
            cnt = 1
        elif cur == col:
            cnt += 1
        else:
            break
    if col is None:
        return {"colour": None, "count": 0, "label": "FLAT"}
    prefix = "G" if col == "green" else "R"
    return {"colour": col, "count": cnt, "label": f"{prefix}{cnt}"}


def evaluate_forming_candle(
    bars: Sequence[Dict[str, float]],
    now_ms: Optional[int] = None,
    sma_len: int = 20,
) -> Optional[Dict[str, Any]]:
    """Evaluate the forming candle (bars[-1]) in the context of its prior closed history (bars[:-1]).

    Each bar dict has keys: t (open ms), o, h, l, c, v (optional), close_t (optional close ms).
    Causality guard: if `now_ms` is provided and `bars[-1]['t'] > now_ms`, raises ValueError (lookahead bar).
    Captures the monthly / weekly / daily context:
      - direction ('green' | 'red' | 'flat'), open, high, low, close, range
      - pos_in_range in [0, 1] (where current price stands inside the forming candle's high-low range)
      - upper_wick_pct, lower_wick_pct (rejection at the forming candle's extremes)
      - elapsed_pct (tau) and t_left in [0, 1] if close_t and now_ms are provided
      - atr14, d_atr = (close - open) / atr14, p_keep_colour
      - streak of prior closed candles (e.g. 'R4' = 4 red weeks in a row)
      - sma (e.g. 20M SMA for monthly cycle bias) and price_vs_sma ('above' | 'below')
    """
    if not bars:
        return None
    f = bars[-1]
    if now_ms is not None and "t" in f and int(f["t"]) > now_ms:
        raise ValueError(f"Causality violation: forming bar open t={f['t']} is after now_ms={now_ms}")
    o, h, l, c = float(f["o"]), float(f["h"]), float(f["l"]), float(f["c"])
    if h < l or max(o, c) > h + 1e-9 or min(o, c) < l - 1e-9:
        return None
    rng = h - l
    colour = "green" if c > o else ("red" if c < o else "flat")
    pos_in_range = (c - l) / rng if rng > 0.0 else 0.5
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    upper_wick_pct = upper_wick / rng if rng > 0.0 else 0.0
    lower_wick_pct = lower_wick / rng if rng > 0.0 else 0.0

    elapsed_pct: Optional[float] = None
    t_left: Optional[float] = None
    if now_ms is not None and "t" in f and "close_t" in f:
        t0, t1 = int(f["t"]), int(f["close_t"])
        span = t1 - t0 + 1
        if span > 0 and t0 <= now_ms <= t1 + 1:
            elapsed_pct = max(0.0, min(1.0, (now_ms - t0) / float(span)))
            t_left = 1.0 - elapsed_pct

    atr = compute_atr14(bars)
    d_atr = (c - o) / atr if (atr is not None and atr > 0.0) else None
    p_keep = p_close_colour(d_atr, t_left) if (d_atr is not None and t_left is not None) else None
    streak = closed_streak(bars)
    sma_val = compute_sma(bars, sma_len)
    price_vs_sma = None
    if sma_val is not None and sma_val > 0.0:
        price_vs_sma = "above" if c > sma_val else ("below" if c < sma_val else "at")

    return {
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "range": rng,
        "colour": colour,
        "pos_in_range": pos_in_range,
        "upper_wick_pct": upper_wick_pct,
        "lower_wick_pct": lower_wick_pct,
        "elapsed_pct": elapsed_pct,
        "t_left": t_left,
        "atr14": atr,
        "d_atr": d_atr,
        "p_keep_colour": p_keep,
        "streak": streak,
        f"sma{sma_len}": sma_val,
        f"price_vs_sma{sma_len}": price_vs_sma,
    }


def compute_volume_profile(
    bars: Sequence[Dict[str, float]],
    bin_size: float = DEFAULT_BIN_SIZE,
    va_share: float = DEFAULT_VA_SHARE,
    lvn_ratio: float = 0.25,
    spread_range: bool = False,
) -> Optional[Dict[str, Any]]:
    """Compute Volume Profile (POC, VAL, VAH, HVNs, and interior LVNs) from bars.

    By default (`spread_range=False`), matches `tf_strip.js` `valueArea` convention on 1m bars: each bar's volume `v`
    is allocated to the bin of its HLC3 = (h + l + c) / 3, where bin index k = floor(hlc3 / bin_size), bin lower edge =
    k * bin_size, upper edge = (k + 1) * bin_size. When `spread_range=True` (useful for 5m/15m bars whose range spans
    multiple $50 bins), each bar's volume is distributed uniformly across all bins touched by `[l, h]` so wider bars do
    not create artificial empty-bin LVNs.
      - POC = bin lower edge with highest volume (`poc_mid = poc + 0.5 * bin_size` is also returned).
      - 70% Value Area expands one bin at a time toward the larger immediate neighbour (up >= dn -> up).
      - VAL = lo_bin * bin_size, VAH = (hi_bin + 1) * bin_size.
      - LVNs = interior low-volume troughs (including contiguous multi-bin vacuums) strictly between min_k and max_k
        whose bin volume(s) <= lvn_ratio * poc_vol and whose bounding neighbours on both sides have strictly higher volume.
    """
    if not bars or bin_size <= 0.0 or not (0.0 < va_share <= 1.0):
        return None
    bins: Dict[int, float] = {}
    tot_vol = 0.0
    high_px: Optional[float] = None
    low_px: Optional[float] = None

    for b in bars:
        h, l, c = float(b["h"]), float(b["l"]), float(b["c"])
        v = float(b.get("v", b.get("buy_vol", 0.0) + b.get("sell_vol", 0.0)))
        if v <= 0.0 or h < l:
            continue
        if spread_range and h > l:
            k_lo = int(math.floor(l / bin_size + 1e-9))
            k_hi = int(math.floor(h / bin_size + 1e-9))
            n_bins = k_hi - k_lo + 1
            v_per = v / float(n_bins)
            for k_idx in range(k_lo, k_hi + 1):
                bins[k_idx] = bins.get(k_idx, 0.0) + v_per
        else:
            hlc3 = (h + l + c) / 3.0
            idx = int(math.floor(hlc3 / bin_size + 1e-9))
            bins[idx] = bins.get(idx, 0.0) + v
        tot_vol += v
        high_px = h if high_px is None else max(high_px, h)
        low_px = l if low_px is None else min(low_px, l)

    if not bins or tot_vol <= 0.0:
        return None

    min_k, max_k = min(bins), max(bins)
    poc_k = min_k
    for k in sorted(bins):
        if bins[k] > bins[poc_k]:
            poc_k = k

    lo_k = hi_k = poc_k
    acc = bins[poc_k]
    target = va_share * tot_vol
    while acc < target and (lo_k > min_k or hi_k < max_k):
        up_v = bins.get(hi_k + 1, 0.0) if hi_k < max_k else -1.0
        dn_v = bins.get(lo_k - 1, 0.0) if lo_k > min_k else -1.0
        if up_v >= dn_v:
            hi_k += 1
            if up_v > 0.0:
                acc += up_v
        else:
            lo_k -= 1
            if dn_v > 0.0:
                acc += dn_v

    poc_vol = bins[poc_k]
    lvns: List[float] = []
    lvn_zones: List[Dict[str, float]] = []
    hvns: List[float] = []

    # Detect interior LVNs, grouping contiguous low-volume bins (v <= lvn_ratio * poc_vol)
    k = min_k + 1
    while k < max_k:
        vk = bins.get(k, 0.0)
        if vk <= lvn_ratio * poc_vol:
            run_start = k
            run_end = k
            min_v = vk
            min_bin = k
            while run_end + 1 < max_k and bins.get(run_end + 1, 0.0) <= lvn_ratio * poc_vol:
                run_end += 1
                v_cur = bins.get(run_end, 0.0)
                if v_cur < min_v:
                    min_v = v_cur
                    min_bin = run_end
            v_left = bins.get(run_start - 1, 0.0)
            v_right = bins.get(run_end + 1, 0.0)
            if min_v < v_left and min_v < v_right:
                rep_px = min_bin * bin_size if run_start == run_end else ((run_start + run_end) / 2.0) * bin_size
                lvns.append(rep_px)
                lvn_zones.append({
                    "low": run_start * bin_size,
                    "high": (run_end + 1) * bin_size,
                    "price": rep_px,
                    "bins": float(run_end - run_start + 1),
                })
            k = run_end + 1
        else:
            k += 1

    for k in range(min_k + 1, max_k):
        vk = bins.get(k, 0.0)
        v_prev = bins.get(k - 1, 0.0)
        v_next = bins.get(k + 1, 0.0)
        if vk >= v_prev and vk >= v_next and vk >= 0.5 * poc_vol and k != poc_k:
            hvns.append(k * bin_size)

    return {
        "val": lo_k * bin_size,
        "poc": poc_k * bin_size,
        "poc_mid": (poc_k + 0.5) * bin_size,
        "vah": (hi_k + 1) * bin_size,
        "width": (hi_k + 1 - lo_k) * bin_size,
        "high": high_px,
        "low": low_px,
        "total_vol": tot_vol,
        "lvns": lvns,
        "lvn_zones": lvn_zones,
        "hvns": hvns,
    }


def _us_dst(day) -> bool:
    """US daylight time (Energy Policy Act 2005): from the 2nd Sunday of March to the 1st Sunday of November.
    Day-level: the cash session (09:30-16:00) never straddles the 02:00 switch."""
    import datetime as _dt
    y = day.year
    mar1, nov1 = _dt.date(y, 3, 1), _dt.date(y, 11, 1)
    start = mar1 + _dt.timedelta(days=(6 - mar1.weekday()) % 7 + 7)      # 2nd Sunday of March
    end = nov1 + _dt.timedelta(days=(6 - nov1.weekday()) % 7)             # 1st Sunday of November
    return start <= day < end


def ny_session_window(day) -> tuple:
    """(start_ms, end_ms) UTC of the New York cash session 09:30-16:00 America/New_York on `day`
    (tf-ny-session-va-profile-1109; TOM-281, Pz8f0wWW12M:654). EDT = UTC-4, EST = UTC-5."""
    import datetime as _dt
    off = 4 if _us_dst(day) else 5
    base = _dt.datetime(day.year, day.month, day.day, tzinfo=_dt.timezone.utc)
    start = base + _dt.timedelta(hours=9 + off, minutes=30)
    end = base + _dt.timedelta(hours=16 + off)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def prior_ny_session_profile(bars: Sequence[Dict[str, float]], now_ms: int, bin_size: float = DEFAULT_BIN_SIZE,
                             step_ms: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """VAH/VAL/POC of the last NY cash session that ended at or before `now_ms`, from intraday bars (keys t,o,h,l,c,v).
    Only bars that open and close inside the session window and close by now_ms enter (zero lookahead). None when the
    bars hold no completed weekday session within the last 6 days. US exchange holidays are not modelled."""
    import datetime as _dt
    if not bars:
        return None
    if step_ms is None:
        step_ms = (bars[1]["t"] - bars[0]["t"]) if len(bars) > 1 else 300_000
    day = _dt.datetime.fromtimestamp(now_ms / 1000, _dt.timezone.utc).date()
    for back in range(0, 6):
        d = day - _dt.timedelta(days=back)
        if d.weekday() >= 5:              # no cash session on Saturday/Sunday (US holidays not modelled)
            continue
        s0, s1 = ny_session_window(d)
        if s1 > now_ms:
            continue
        sess = [b for b in bars if s0 <= b["t"] and b["t"] + step_ms <= s1 and b["t"] + step_ms <= now_ms]
        if not sess:
            continue
        prof = compute_volume_profile(sess, bin_size=bin_size)
        if not prof:
            return None
        return {"date": d.isoformat(), "start_ms": s0, "end_ms": s1, "bars": len(sess),
                "vah": float(prof["vah"]), "val": float(prof["val"]), "poc": float(prof["poc"])}
    return None


def build_mtf_context(
    monthly_bars: Sequence[Dict[str, float]],
    weekly_bars: Sequence[Dict[str, float]],
    daily_bars: Sequence[Dict[str, float]],
    prior_day_intraday: Optional[Sequence[Dict[str, float]]] = None,
    prior_week_intraday: Optional[Sequence[Dict[str, float]]] = None,
    developing_day_intraday: Optional[Sequence[Dict[str, float]]] = None,
    now_ms: Optional[int] = None,
    bin_size: float = DEFAULT_BIN_SIZE,
) -> Dict[str, Any]:
    """Build the unified Top-Down Context Ladder (Monthly -> Weekly -> Daily / Yesterday -> Developing Today).

    Addresses the core failure identified in the audit: Tom/Fabio layers previously looked only at a 24h snapshot
    or a 60-minute rolling 1m window, completely blind to where price stands in the forming Monthly (1M) and
    Weekly (1w) candles, the 20M SMA macro cycle, multi-week red/green streaks, and Yesterday's / Last Week's
    acceptance prices (POC, VAH, VAL).
    """
    m_state = evaluate_forming_candle(monthly_bars, now_ms=now_ms, sma_len=20)
    w_state = evaluate_forming_candle(weekly_bars, now_ms=now_ms, sma_len=20)
    d_state = evaluate_forming_candle(daily_bars, now_ms=now_ms, sma_len=20)

    prior_day_vp = compute_volume_profile(prior_day_intraday, bin_size=bin_size) if prior_day_intraday else None
    prior_week_vp = compute_volume_profile(prior_week_intraday, bin_size=bin_size) if prior_week_intraday else None
    dev_day_vp = compute_volume_profile(developing_day_intraday, bin_size=bin_size) if developing_day_intraday else None

    current_price = d_state["close"] if d_state else (w_state["close"] if w_state else (m_state["close"] if m_state else None))

    # Determine Price vs Prior Day Value Area (without disabling counter-trend failed-breakout fades!)
    price_vs_prior_va = None
    if current_price is not None and prior_day_vp is not None:
        if current_price > prior_day_vp["vah"]:
            price_vs_prior_va = "above_vah"
        elif current_price < prior_day_vp["val"]:
            price_vs_prior_va = "below_val"
        else:
            price_vs_prior_va = "in_va"

    # Synthesize HTF Macro Bias from Monthly (1M) + Weekly (1w):
    # Monthly is the highest timeframe driving the macro bias; Weekly streak and forming candle confirm or warn of exhaustion.
    # If the forming 1M candle is very early (elapsed_pct < 0.10 and p_keep_colour < 0.60), we note that its colour is still nascent.
    htf_bias = "neutral"
    bias_reasons: List[str] = []
    if m_state is not None:
        m_el = m_state.get("elapsed_pct")
        m_pk = m_state.get("p_keep_colour")
        nascent = (m_el is not None and m_el < 0.10) and (m_pk is None or m_pk < 0.60)
        if m_state.get("price_vs_sma20") == "below" and m_state["colour"] == "red":
            htf_bias = "bearish"
            bias_reasons.append("1M red & below 20M SMA" + (" (early month)" if nascent else ""))
        elif m_state.get("price_vs_sma20") == "above" and m_state["colour"] == "green":
            htf_bias = "bullish"
            bias_reasons.append("1M green & above 20M SMA" + (" (early month)" if nascent else ""))
        elif m_state.get("price_vs_sma20") == "below" and m_state["colour"] == "green":
            htf_bias = "rally_in_macro_bear"
            bias_reasons.append("1M green bounce below 20M SMA")
        elif m_state.get("price_vs_sma20") == "above" and m_state["colour"] == "red":
            htf_bias = "pullback_in_macro_bull"
            bias_reasons.append("1M red pullback above 20M SMA")
        else:
            bias_reasons.append(f"1M {m_state['colour']}")
        if m_pk is not None:
            bias_reasons.append(f"1M P_keep={m_pk:.0%}")

    if w_state is not None:
        st = w_state["streak"]
        if st["count"] >= 3:
            bias_reasons.append(f"1w streak {st['label']}")
            if st["colour"] == "red" and htf_bias == "neutral":
                htf_bias = "bearish"
            elif st["colour"] == "green" and htf_bias == "neutral":
                htf_bias = "bullish"

    # Collect structural levels ladder (sorted by distance from current_price when available, else by price)
    levels: List[Dict[str, Any]] = []

    def _add_lvl(name: str, price: Optional[float], tf: str, kind: str) -> None:
        if price is not None and math.isfinite(price) and price > 0.0:
            dist_pct = ((price - current_price) / current_price * 100.0) if (current_price and current_price > 0.0) else None
            levels.append({"name": name, "price": price, "tf": tf, "kind": kind, "dist_pct": dist_pct})

    if m_state is not None:
        _add_lvl("1M open", m_state["open"], "1M", "open")
        _add_lvl("1M high", m_state["high"], "1M", "extreme")
        _add_lvl("1M low", m_state["low"], "1M", "extreme")
        if m_state.get("sma20"):
            _add_lvl("20M SMA", m_state["sma20"], "1M", "ma")
    if monthly_bars and len(monthly_bars) >= 2:
        pm = monthly_bars[-2]
        _add_lvl("Prior 1M high", float(pm["h"]), "1M", "prior_extreme")
        _add_lvl("Prior 1M low", float(pm["l"]), "1M", "prior_extreme")
        _add_lvl("Prior 1M close", float(pm["c"]), "1M", "prior_close")

    if w_state is not None:
        _add_lvl("1w open", w_state["open"], "1w", "open")
        _add_lvl("1w high", w_state["high"], "1w", "extreme")
        _add_lvl("1w low", w_state["low"], "1w", "extreme")
    if weekly_bars and len(weekly_bars) >= 2:
        pw = weekly_bars[-2]
        _add_lvl("Prior 1w high", float(pw["h"]), "1w", "prior_extreme")
        _add_lvl("Prior 1w low", float(pw["l"]), "1w", "prior_extreme")
    if prior_week_vp is not None:
        _add_lvl("Prior 1w POC", prior_week_vp["poc"], "1w", "poc")
        _add_lvl("Prior 1w VAH", prior_week_vp["vah"], "1w", "vah")
        _add_lvl("Prior 1w VAL", prior_week_vp["val"], "1w", "val")

    if daily_bars and len(daily_bars) >= 2:
        pd = daily_bars[-2]
        _add_lvl("Prior 1d high", float(pd["h"]), "1d", "prior_extreme")
        _add_lvl("Prior 1d low", float(pd["l"]), "1d", "prior_extreme")
        _add_lvl("Prior 1d close", float(pd["c"]), "1d", "prior_close")
    if prior_day_vp is not None:
        _add_lvl("Prior 1d POC", prior_day_vp["poc"], "1d", "poc")
        _add_lvl("Prior 1d VAH", prior_day_vp["vah"], "1d", "vah")
        _add_lvl("Prior 1d VAL", prior_day_vp["val"], "1d", "val")
        for idx, lvn_px in enumerate(prior_day_vp["lvns"]):
            _add_lvl(f"Prior 1d LVN#{idx + 1}", lvn_px, "1d", "lvn")

    if dev_day_vp is not None:
        _add_lvl("Developing 1d POC", dev_day_vp["poc"], "1d_dev", "poc")
        _add_lvl("Developing 1d VAH", dev_day_vp["vah"], "1d_dev", "vah")
        _add_lvl("Developing 1d VAL", dev_day_vp["val"], "1d_dev", "val")

    if current_price and current_price > 0.0:
        levels.sort(key=lambda x: abs(x["dist_pct"]))
    else:
        levels.sort(key=lambda x: x["price"])

    return {
        "current_price": current_price,
        "htf_bias": htf_bias,
        "bias_reasons": bias_reasons,
        "monthly": m_state,
        "weekly": w_state,
        "daily": d_state,
        "prior_day_vp": prior_day_vp,
        "prior_week_vp": prior_week_vp,
        "developing_day_vp": dev_day_vp,
        "price_vs_prior_va": price_vs_prior_va,
        "levels": levels,
    }


def is_knife_approach(bars: Sequence[Dict[str, float]], touch_idx: int, side: str, lookback: int = 12) -> bool:
    """Detect whether price is approaching a level as an un-retraced vertical knife (wick_census.py rule).
    - For a LOW sweep ('support' / 'long' fade): over the `lookback` bars before `touch_idx`, the drop from the highest
      high to `bars[touch_idx]['o']` is <= -2.0% AND the largest bounce inside those bars is < 25% of that drop.
    - Mirror for a HIGH sweep ('resistance' / 'short' fade): rise >= +2.0% AND largest dip < 25% of that rise.
    - Fail closed: if `touch_idx < 3` (too few bars before touch to verify a non-knife approach), returns True (treat
      unknown approach history as unsafe to fade).
    When True, fading the first wick is a coin-flip / negative-EV knife catch (29% win rate in CENSUS_5m)."""
    if touch_idx >= len(bars):
        return False
    if touch_idx < 3:
        return True  # fail closed: insufficient pre-touch bars to verify non-knife approach
    start = max(0, touch_idx - lookback)
    pre = bars[start:touch_idx]
    o = float(bars[touch_idx]["o"])
    norm_side = LEVEL_SIDE_ALIASES.get(side, side)
    if norm_side in ("support", "long", "LOW"):
        top = max(float(r["h"]) for r in pre)
        if top <= 0.0:
            return False
        drop_pct = (o / top - 1.0) * 100.0
        if drop_pct > -2.0:
            return False
        run_lo = float(pre[0]["l"])
        max_bounce = 0.0
        for r in pre:
            run_lo = min(run_lo, float(r["l"]))
            max_bounce = max(max_bounce, float(r["c"]) - run_lo)
        return max_bounce < 0.25 * (top - o)
    else:
        bot = min(float(r["l"]) for r in pre)
        if bot <= 0.0:
            return False
        rise_pct = (o / bot - 1.0) * 100.0
        if rise_pct < 2.0:
            return False
        run_hi = float(pre[0]["h"])
        max_dip = 0.0
        for r in pre:
            run_hi = max(run_hi, float(r["h"]))
            max_dip = max(max_dip, run_hi - float(r["c"]))
        return max_dip < 0.25 * (o - bot)


def classify_level_interaction(
    bars: Sequence[Dict[str, float]],
    level_price: float,
    level_side: str,
    zone_tol_pct: float = 0.15,
    level_kind: str = "boundary",
    max_bars_since_reclaim: int = 3,
    accept_minutes: Optional[int] = None,
    bar_minutes: int = 5,
) -> Dict[str, Any]:
    """Classify how price interacts with a structural level on intraday bars (e.g. 5m or 15m).

    `level_side`:
      - 'support' (or aliases 'val' / 'low'): level is below prior price; testing if buyers reject lower prices or if sellers accept below.
      - 'resistance' (or aliases 'vah' / 'high'): level is above prior price; testing if sellers reject higher prices or if buyers accept above.
    `level_kind`:
      - 'boundary' (default: VAH, VAL, POC, prior high/low) or 'lvn' (interior Low Volume Node vacuum).

    Core Tom & Fabio Auction Concepts:
      1. FAST REJECTION / V-SWEEP (Failed Auction -> Fade / Reclaim Trade):
         - Price probes beyond `level_price` (`l < level_price` for support, `h > level_price` for resistance),
         - Spends minimal time beyond the level (`bars_beyond <= 3`, i.e., 1-bar wick or 2-4 bar V-sweep),
         - Closes back inside `level_price` (reclaim close) and the reclaim is fresh (`n - 1 - reclaim_idx <= max_bars_since_reclaim`),
         - Accompanied by Effort/Volume (`rel_vol >= 2.0` vs the pre-touch median volume of up to 48 bars immediately before
           `touch_idx`, or opposing delta / absorption),
         - Not a vertical knife (`knife == False`).
      2. ACCEPTANCE BEYOND LEVEL (Value Migration -> Continuation / Never Fade):
         - Price closes beyond `level_price` for `consec_beyond >= N` consecutive bars, or >= round(N*2/3) while still
           outside, or parks inside the zone (`bars_in_zone >= 6`, OURS) without rejecting. Default N = 6 bars (OURS: on 5m
           that is 30 min, half of the sourced duration; on 1h it is 6 h). `accept_minutes` + `bar_minutes` set
           N = accept_minutes / bar_minutes; accept_minutes=60 is the SOURCED accept80.py duration (2 consecutive 30m closes
           below prior-day VAL; REVIEW_FABLE.md:47, card census-acceptance-threshold-mislabel-1109).
      3. LVN_FAST_TRAVERSE (Impulse Vacuum Traverse -> Trend Continuation):
         - When `level_kind == 'lvn'` and price slices across `level_price` in 1-3 bars on high volume (`max_rel_vol >= 2.0`)
           and closes cleanly beyond `level_price` without reclaiming.
    """
    if not bars or len(bars) < 5 or level_price <= 0.0:
        return {"verdict": "INSUFFICIENT_DATA"}
    if level_side not in LEVEL_SIDE_ALIASES:
        raise ValueError(f"level_side must be 'support'/'val'/'low' or 'resistance'/'vah'/'high', got {level_side!r}")
    norm_side = LEVEL_SIDE_ALIASES[level_side]

    n = len(bars)
    vols = [float(b.get("v", b.get("buy_vol", 0.0) + b.get("sell_vol", 0.0))) for b in bars]

    # Scan the recent window (last 12 bars): if any bar probed beyond level_price, touch_idx is the FIRST probing bar;
    # otherwise, touch_idx is the first bar whose extreme entered zone_tol_pct of level_price.
    scan_start = max(0, n - 12)
    touch_idx: Optional[int] = None
    for i in range(scan_start, n):
        h, l = float(bars[i]["h"]), float(bars[i]["l"])
        probed = (l <= level_price) if norm_side == "support" else (h >= level_price)
        if probed:
            touch_idx = i
            break
    if touch_idx is None:
        for i in range(scan_start, n):
            h, l = float(bars[i]["h"]), float(bars[i]["l"])
            approach_dist_pct = (abs(l - level_price) if norm_side == "support" else abs(h - level_price)) / level_price * 100.0
            if approach_dist_pct <= zone_tol_pct:
                touch_idx = i
                break

    if touch_idx is None:
        return {"verdict": "NO_INTERACTION", "level_price": level_price, "level_side": norm_side}

    # Pre-touch volume baseline: up to 48 bars immediately preceding touch_idx (never overlapping the touch window)
    pre_vol_slice = vols[max(0, touch_idx - 48):touch_idx]
    med_vol = statistics.median(pre_vol_slice) if pre_vol_slice else statistics.median(vols)
    if med_vol <= 0.0:
        med_vol = 1.0

    window = bars[touch_idx:]
    bars_in_zone = 0
    bars_beyond = 0
    consec_beyond = 0
    max_consec_beyond = 0
    reclaim_idx: Optional[int] = None
    sweep_extreme = float(window[0]["l"]) if norm_side == "support" else float(window[0]["h"])
    max_rel_vol = 0.0
    absorption_seen = False

    for offset, b in enumerate(window):
        idx = touch_idx + offset
        o, h, l, c = float(b["o"]), float(b["h"]), float(b["l"]), float(b["c"])
        v = vols[idx]
        rv = v / med_vol
        if rv > max_rel_vol:
            max_rel_vol = rv
        delta = float(b.get("delta", 0.0))

        if norm_side == "support":
            if l < sweep_extreme:
                sweep_extreme = l
                if c > level_price:
                    reclaim_idx = idx
            if c <= level_price:
                bars_beyond += 1
                consec_beyond += 1
                max_consec_beyond = max(max_consec_beyond, consec_beyond)
                reclaim_idx = None  # reset if a subsequent bar closes back below support after an earlier bounce
            else:
                consec_beyond = 0
                if (l < level_price or bars_beyond > 0) and reclaim_idx is None:
                    reclaim_idx = idx
            if (delta < 0 and c >= o) or (h > l and (min(o, c) - l) / (h - l) >= 0.5 and rv >= 2.0):
                absorption_seen = True
        else:
            if h > sweep_extreme:
                sweep_extreme = h
                if c < level_price:
                    reclaim_idx = idx
            if c >= level_price:
                bars_beyond += 1
                consec_beyond += 1
                max_consec_beyond = max(max_consec_beyond, consec_beyond)
                reclaim_idx = None  # reset if a subsequent bar closes back above resistance after an earlier dip
            else:
                consec_beyond = 0
                if (h > level_price or bars_beyond > 0) and reclaim_idx is None:
                    reclaim_idx = idx
            if (delta > 0 and c <= o) or (h > l and (h - max(o, c)) / (h - l) >= 0.5 and rv >= 2.0):
                absorption_seen = True

        if abs(c - level_price) / level_price * 100.0 <= zone_tol_pct:
            bars_in_zone += 1

    last_close = float(bars[-1]["c"])
    currently_inside = (last_close > level_price) if norm_side == "support" else (last_close < level_price)
    probed_beyond = (sweep_extreme < level_price) if norm_side == "support" else (sweep_extreme > level_price)
    knife = is_knife_approach(bars, touch_idx, norm_side)

    # 1. Check LVN Fast Traverse (when level is an LVN vacuum and price slices across it on high volume without reclaiming)
    if level_kind == "lvn" and probed_beyond and not currently_inside and 1 <= bars_beyond <= 3 and max_rel_vol >= 2.0:
        impulse_dir = "short" if norm_side == "support" else "long"
        return {
            "verdict": "LVN_FAST_TRAVERSE",
            "trade_bias": impulse_dir,
            "level_price": level_price,
            "level_side": norm_side,
            "level_kind": level_kind,
            "touch_idx": touch_idx,
            "bars_beyond": bars_beyond,
            "sweep_extreme": sweep_extreme,
            "max_rel_vol": round(max_rel_vol, 2),
            "knife": knife,
            "reason": (
                f"Impulse sliced through LVN {level_price:.1f} ({impulse_dir}) in {bars_beyond} bar(s) "
                f"on {max_rel_vol:.1f}x relative volume without reclaiming."
            ),
        }

    # 2. Check Acceptance (consecutive time at/beyond level builds value -> do NOT fade). N = 6 bars OURS by default;
    #    accept_minutes / bar_minutes gives the SOURCED accept80.py 60 min (2x30m closes) on any timeframe.
    n_acc = 6 if accept_minutes is None else max(1, round(accept_minutes / max(1, bar_minutes)))
    n_early = max(1, round(n_acc * 2 / 3))
    if max_consec_beyond >= n_acc or (not currently_inside and consec_beyond >= n_early) or (bars_in_zone >= 6 and not probed_beyond):
        return {
            "verdict": "ACCEPTED",
            "trade_bias": "continuation" if not currently_inside else "balance_hold",
            "level_price": level_price,
            "level_side": norm_side,
            "touch_idx": touch_idx,
            "bars_beyond": bars_beyond,
            "consec_beyond": consec_beyond,
            "bars_in_zone": bars_in_zone,
            "sweep_extreme": sweep_extreme,
            "max_rel_vol": round(max_rel_vol, 2),
            "knife": knife,
            "reason": (
                f"Price spent {consec_beyond} consecutive bars ({bars_beyond} total) beyond / {bars_in_zone} bars in zone: "
                f"level accepted (no rejection; threshold {n_acc} bars: "
                + ("OURS default" if accept_minutes is None else f"{accept_minutes} min / {bar_minutes}m bars") + ")."
            ),
        }

    # 3. Check Fast Rejection / V-Sweep Reclaim (1-bar sweep wick or 2-4 bar V-sweep that reclaimed the level recently)
    if probed_beyond and currently_inside and reclaim_idx is not None and bars_beyond <= 3:
        bars_since_reclaim = (n - 1) - reclaim_idx
        reclaim_bars = reclaim_idx - touch_idx + 1
        kind = "1bar_wick_sweep" if reclaim_bars == 1 else f"V{reclaim_bars}_sweep"
        if bars_since_reclaim > max_bars_since_reclaim:
            return {
                "verdict": "STALE_REJECTION",
                "trade_bias": "skip_stale",
                "kind": kind,
                "level_price": level_price,
                "level_side": norm_side,
                "touch_idx": touch_idx,
                "reclaim_idx": reclaim_idx,
                "bars_since_reclaim": bars_since_reclaim,
                "sweep_extreme": sweep_extreme,
                "max_rel_vol": round(max_rel_vol, 2),
                "knife": knife,
                "reason": f"{kind} reclaimed {bars_since_reclaim} bars ago (> max {max_bars_since_reclaim}); setup is stale.",
            }
        if knife:
            return {
                "verdict": "REJECTED_KNIFE_SKIP",
                "trade_bias": "skip_knife",
                "kind": kind,
                "level_price": level_price,
                "level_side": norm_side,
                "touch_idx": touch_idx,
                "reclaim_idx": reclaim_idx,
                "reclaim_bars": reclaim_bars,
                "bars_since_reclaim": bars_since_reclaim,
                "sweep_extreme": sweep_extreme,
                "reclaim_close": float(bars[reclaim_idx]["c"]),
                "max_rel_vol": round(max_rel_vol, 2),
                "absorption_seen": absorption_seen,
                "knife": True,
                "reason": "Sweep reclaimed quickly, but approach is an un-retraced vertical knife (>2% drop/rise with <25% bounce) or short pre-window.",
            }
        has_effort = max_rel_vol >= 2.0 or absorption_seen
        return {
            "verdict": "FAST_REJECTION" if has_effort else "WEAK_REJECTION",
            "trade_bias": "long" if norm_side == "support" else "short",
            "kind": kind,
            "level_price": level_price,
            "level_side": norm_side,
            "touch_idx": touch_idx,
            "reclaim_idx": reclaim_idx,
            "reclaim_bars": reclaim_bars,
            "bars_since_reclaim": bars_since_reclaim,
            "bars_beyond": bars_beyond,
            "sweep_extreme": sweep_extreme,
            "reclaim_close": float(bars[reclaim_idx]["c"]),
            "max_rel_vol": round(max_rel_vol, 2),
            "absorption_seen": absorption_seen,
            "knife": False,
            "reason": f"{kind} swept {level_price:.1f} to {sweep_extreme:.1f} and reclaimed in {reclaim_bars} bar(s) with {max_rel_vol:.1f}x rel vol.",
        }

    # 4. Still probing / unconfirmed
    return {
        "verdict": "PROBING_UNCONFIRMED",
        "trade_bias": "wait_for_reclaim_or_acceptance",
        "level_price": level_price,
        "level_side": norm_side,
        "touch_idx": touch_idx,
        "bars_beyond": bars_beyond,
        "consec_beyond": consec_beyond,
        "bars_in_zone": bars_in_zone,
        "sweep_extreme": sweep_extreme,
        "max_rel_vol": round(max_rel_vol, 2),
        "knife": knife,
        "reason": "Price is probing the level; wait for either a fast reclaim close inside (<=3 bars beyond) or acceptance outside.",
    }


def build_auction_trade_plan(
    context: Dict[str, Any],
    interaction: Dict[str, Any],
    entry_price: float,
    targets: Sequence[Tuple[str, float]],
    stop_buffer_pct_10k: float = 5.0,
    fee_rt_bps: float = DEFAULT_TAKER_RT_BPS,
    max_fee_r: float = DEFAULT_MAX_FRICTION_R,
    min_net_rr: float = DEFAULT_MIN_NET_RR,
    stop_buffer_bps: Optional[float] = None,
) -> Dict[str, Any]:
    """Build a complete 'Idea + Proof + Math' trade plan and enforce fee-safe structural stop geometry.

    Supports three plain auction setups:
      Setup 1 — Fast Rejection / Failed Breakout Reclaim (`interaction['verdict'] == 'FAST_REJECTION'`):
        - Side: 'long' off support/VAL/low sweep, 'short' off resistance/VAH/high sweep.
        - Structural stop: beyond `interaction['sweep_extreme']` by `stop_buffer_bps`.
        - Target: nearest volume node (POC, then opposite VA edge) in trade direction with net_rr >= min_net_rr.
      Setup 2 — Value Area Acceptance / Breakout Continuation (`interaction['verdict'] == 'ACCEPTED'` and `trade_bias == 'continuation'`):
        - Side: 'short' when accepted below VAL/support, 'long' when accepted above VAH/resistance.
        - Structural stop: back inside the broken level (`level_price` +/- buffer, min 25 bps).
        - Target: next HTF volume node / 0.5x-1.0x VA extension.
      Setup 3 — LVN Fast Traverse (`interaction['verdict'] == 'LVN_FAST_TRAVERSE'`):
        - Side: `interaction['trade_bias']` ('long' when slicing up through LVN, 'short' when slicing down).
        - Structural stop: on the far side of the LVN (`level_price` +/- buffer, min 25 bps).
        - Target: next HVN/POC at the end of the low-volume vacuum.

    Automatically rejects trades that violate:
      - Knife gate (`interaction['knife'] == True` on a fade)
      - Fee-to-Stop Geometry Gate (`fee_r = fee_rt_bps / stop_bps > max_fee_r`)
      - Net R:R Gate (`net_rr < min_net_rr`)
    """
    verdict = interaction.get("verdict")
    level_price = float(interaction.get("level_price", 0.0))
    level_side = LEVEL_SIDE_ALIASES.get(str(interaction.get("level_side", "")), interaction.get("level_side"))
    if stop_buffer_bps is None:
        stop_buffer_bps = stop_buffer_pct_10k

    if verdict == "FAST_REJECTION":
        direction = "long" if level_side == "support" else "short"
        setup_type = "failed_auction_reclaim"
        extreme = float(interaction["sweep_extreme"])
        buf = extreme * (stop_buffer_bps / 10000.0)
        structural_stop = (extreme - buf) if direction == "long" else (extreme + buf)
    elif verdict == "ACCEPTED" and interaction.get("trade_bias") == "continuation":
        direction = "short" if level_side == "support" else "long"
        setup_type = "va_acceptance_continuation"
        buf = level_price * (max(stop_buffer_bps, 25.0) / 10000.0)
        structural_stop = (level_price + buf) if direction == "short" else (level_price - buf)
    elif verdict == "LVN_FAST_TRAVERSE":
        direction = str(interaction["trade_bias"])
        setup_type = "lvn_fast_traverse"
        buf = level_price * (max(stop_buffer_bps, 25.0) / 10000.0)
        structural_stop = (level_price + buf) if direction == "short" else (level_price - buf)
    else:
        return {
            "action": "SKIP",
            "reason": f"No confirmed setup: interaction verdict is {verdict!r} ({interaction.get('reason', '')})",
            "context_bias": context.get("htf_bias"),
            "interaction": interaction,
        }

    risk_pts = (entry_price - structural_stop) if direction == "long" else (structural_stop - entry_price)
    if risk_pts <= 0.0 or entry_price <= 0.0:
        return {
            "action": "SKIP",
            "reason": f"Invalid stop geometry: entry {entry_price} vs stop {structural_stop} for {direction}",
            "context_bias": context.get("htf_bias"),
            "interaction": interaction,
        }

    stop_bps = (risk_pts / entry_price) * 10000.0
    fee_r = fee_rt_bps / stop_bps

    if fee_r > max_fee_r:
        min_stop_bps = fee_rt_bps / max_fee_r
        return {
            "action": "SKIP_FEE_TRAP",
            "reason": (
                f"Stop width {stop_bps:.1f} bps is too tight for {fee_rt_bps:.1f} bps round-trip fees "
                f"(fee = {fee_r:.2f} R > max {max_fee_r:.2f} R; need stop >= {min_stop_bps:.0f} bps or maker execution)."
            ),
            "direction": direction,
            "setup_type": setup_type,
            "entry": entry_price,
            "structural_stop": round(structural_stop, 2),
            "stop_bps": round(stop_bps, 2),
            "fee_r": round(fee_r, 3),
        }

    # Filter and sort candidate targets in trade direction
    # Reports both linear net_rr = gross_rr - fee_r and exact fee-inclusive effective_rr = (gross_rr - fee_r) / (1 + fee_r)
    valid_targets: List[Dict[str, Any]] = []
    for t_name, t_price in targets:
        t_px = float(t_price)
        reward_pts = (t_px - entry_price) if direction == "long" else (entry_price - t_px)
        if reward_pts <= 0.0:
            continue
        gross_rr = reward_pts / risk_pts
        net_rr = gross_rr - fee_r
        effective_rr = (gross_rr - fee_r) / (1.0 + fee_r)
        valid_targets.append({
            "name": t_name,
            "price": round(t_px, 2),
            "reward_pts": round(reward_pts, 2),
            "gross_rr": round(gross_rr, 2),
            "net_rr": round(net_rr, 2),
            "effective_rr": round(effective_rr, 2),
        })

    valid_targets.sort(key=lambda x: x["reward_pts"])
    qualifying = [t for t in valid_targets if t["net_rr"] >= min_net_rr]
    if not qualifying:
        return {
            "action": "SKIP_LOW_RR",
            "reason": f"No volume target in direction achieves net R:R >= {min_net_rr:.2f} after {fee_r:.2f} R fee.",
            "direction": direction,
            "setup_type": setup_type,
            "entry": entry_price,
            "structural_stop": round(structural_stop, 2),
            "stop_bps": round(stop_bps, 2),
            "fee_r": round(fee_r, 3),
            "candidates": valid_targets,
        }

    primary_target = qualifying[0]
    runner_target = qualifying[1] if len(qualifying) > 1 else None

    # Explicit set check for HTF (1M / 1w) alignment:
    # Shorts at resistance during a macro bear ("bearish" or "rally_in_macro_bear" / "counter_trend_bounce_in_macro_bear")
    # and longs at support during a macro bull ("bullish" or "pullback_in_macro_bull") align with the macro cycle.
    htf_bias = str(context.get("htf_bias", "neutral"))
    with_htf = (
        (direction == "short" and htf_bias in BEARISH_HTF_BIASES)
        or (direction == "long" and htf_bias in BULLISH_HTF_BIASES)
    )
    sizing_tier = "full_with_htf" if with_htf else "scalp_counter_or_range"

    return {
        "action": "TAKE_TRADE",
        "direction": direction,
        "setup_type": setup_type,
        "sizing_tier": sizing_tier,
        "htf_bias": htf_bias,
        "bias_reasons": context.get("bias_reasons", []),
        "entry": round(entry_price, 2),
        "structural_stop": round(structural_stop, 2),
        "stop_bps": round(stop_bps, 2),
        "fee_r": round(fee_r, 3),
        "primary_target": primary_target,
        "runner_target": runner_target,
        "proof_summary": interaction.get("reason", ""),
    }
