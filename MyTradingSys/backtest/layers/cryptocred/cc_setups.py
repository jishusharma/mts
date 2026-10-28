"""
MyTradingSys/backtest/layers/cryptocred/cc_setups.py - CryptoCred entry-pattern setups (cluster C10).
Module implements three setup functions as pure functions producing bt_engine-ready trade signals:
- setup1_sr_flip: [C10-E01 "continuation at break level (SR flip)"]
- setup2_fib_pullback: [C10-E04 "continuation at pullback level (0.618-0.786)"]
- setup3_failed_msb_reversal: [C10-E05 "reversal on failed MSB", C10-E02 "counter-trend = defensive parameters"]

Signal output contract:
Each signal is a dict with top-level keys required by bt_engine.simulate_trade:
"side" ("long"/"short"), "entry_price" (float), "entry_t" (int, the bar t of the entry trigger bar),
"stop" (float), "targets" (list with exactly one tuple: [(target_price, 1.0)]) — plus a nested "meta" dict
holding everything else ("setup", "rule_id", "msb_i", "target_r").

Module source: MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md, cluster C10 (Setup Types).
Design constraint: [C10-E03 "cut and reverse trap"] - this module never auto-chains a setup-1/2 stop-out into a setup-3 entry;
each function only looks at MSB structure independently.
"""
from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings, classify_msb
from MyTradingSys.backtest.layers.cryptocred.cc_retest import find_retest, classify_retest_timing


def _r_target(entry_price, stop, side, target_r):
    """Compute target price from entry/stop/target_r for a given side.

    risk is always the positive entry-to-stop distance; the target sits
    target_r risk-multiples away from entry in the trade's profit direction
    (above entry for long, below entry for short).
    """
    risk = (entry_price - stop) if side == "long" else (stop - entry_price)
    sgn = 1.0 if side == "long" else -1.0
    return entry_price + sgn * target_r * risk


def _limit_window_end_t(bars, msb_event, retest_kwargs=None):
    """Open time of the last bar a resting limit at the broken level stays valid: the existing
    find_retest expiry (default 200 bars) or the first bar whose close invalidates the level
    (default 0.5% beyond it), whichever comes first. Mirrors cc_retest.find_retest defaults;
    only used to expose meta['valid_until_t'] (no signal key is changed)."""
    kw = retest_kwargs or {}
    expiry = kw.get("expiry_bars", 200)
    inval = kw.get("invalidate_pct", 0.005)
    c = msb_event["confirm_i"]
    lvl = msb_event["broken_level"]
    end_k = min(c + expiry, len(bars) - 1)
    for k in range(c, end_k + 1):
        cl = bars[k]["c"]
        if (msb_event["direction"] == "bull" and cl < lvl * (1 - inval)) or \
           (msb_event["direction"] != "bull" and cl > lvl * (1 + inval)):
            return bars[k]["t"]
    return bars[end_k]["t"]


def setup1_sr_flip(bars: list, stop_buffer_pct: float = 0.001, target_r: float = 1.5, msb_kwargs: dict | None = None, retest_kwargs: dict | None = None) -> list:
    swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
    msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
    signals = []
    for msb_event in msb_events:
        retest = find_retest(bars, msb_event, **(retest_kwargs or {}))
        if retest is None:
            continue
        side = "long" if msb_event["direction"] == "bull" else "short"
        entry_price = msb_event["broken_level"]
        entry_t = retest["t"]
        stop = entry_price * (1 - stop_buffer_pct) if side == "long" else entry_price * (1 + stop_buffer_pct)
        target_price = _r_target(entry_price, stop, side, target_r)
        signal = {
            "side": side,
            "entry_price": entry_price,
            "entry_t": entry_t,
            "stop": stop,
            "targets": [(target_price, 1.0)],
            "meta": {
                "setup": "sr_flip",
                "rule_id": "C10-E01",
                "msb_i": msb_event["i"],
                "target_r": target_r
            }
        }
        if msb_event["confirm_i"] < len(bars):
            # limit-order placement info (open times of HTF bars): the setup is known at the
            # close of the MSB confirm bar; a resting limit at entry_price is valid through
            # the close of the bar opened at valid_until_t.
            signal["meta"]["placed_t"] = bars[msb_event["confirm_i"]]["t"]
            signal["meta"]["valid_until_t"] = _limit_window_end_t(bars, msb_event, retest_kwargs)
        signals.append(signal)
    return sorted(signals, key=lambda s: s["entry_t"])


def setup2_fib_pullback(bars: list, fib_lo: float = 0.618, fib_hi: float = 0.786, stop_buffer_pct: float = 0.001, target_r: float = 1.5, msb_kwargs: dict | None = None) -> list:
    expiry_bars = 200
    swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
    msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
    signals = []
    for msb_event in msb_events:
        # Find the preceding swing of the opposite kind. broken_swing_i is a BAR index
        # (cc_structure.classify_msb sets it from H_last["i"]/L_last["i"]), not a
        # position in the `swings` list -- non-swing bars between swings mean the two
        # can diverge, so first locate the swing whose "i" matches, then walk backward
        # from its list position.
        broken_swing_i = msb_event["broken_swing_i"]
        broken_pos = next((idx for idx, s in enumerate(swings) if s["i"] == broken_swing_i), None)
        if broken_pos is None:
            continue
        if msb_event["direction"] == "bull":
            # Find the most recent swing low before the high that was broken
            prev_low = None
            for i in range(broken_pos - 1, -1, -1):
                if swings[i]["kind"] == "low":
                    prev_low = swings[i]
                    break
            if prev_low is None:
                continue
            # The impulse leg is from the low to the high that was broken
            H_price = msb_event["broken_level"]
            P_low = prev_low["price"]
            fib_zone = [H_price - fib_hi * (H_price - P_low), H_price - fib_lo * (H_price - P_low)]
            # Scan bars after confirm_i for the first bar that reaches the resting limit at the zone's upper
            # edge. A bar that blows through the whole zone (low below the zone) filled it too (B151).
            start_idx = msb_event["confirm_i"] + 1
            end_idx = min(start_idx + expiry_bars, len(bars))
            found_bar = None
            for k in range(start_idx, end_idx):
                if bars[k]["l"] <= fib_zone[1]:
                    found_bar = k
                    break
            if found_bar is None:
                continue
            entry_price = fib_zone[1]
            entry_t = bars[found_bar]["t"]
            stop = fib_zone[0] * (1 - stop_buffer_pct)
            side = "long"
        else:  # bear msb_event
            # Find the most recent swing high before the low that was broken
            prev_high = None
            for i in range(broken_pos - 1, -1, -1):
                if swings[i]["kind"] == "high":
                    prev_high = swings[i]
                    break
            if prev_high is None:
                continue
            # The impulse leg is from the high to the low that was broken
            L_price = msb_event["broken_level"]
            P_high = prev_high["price"]
            # ascending like the bull zone: nearest edge (fib_lo) first, so zone[0] is the short's resting limit
            fib_zone = [L_price + fib_lo * (P_high - L_price), L_price + fib_hi * (P_high - L_price)]
            # Scan bars after confirm_i for the first bar that reaches the resting limit at the zone's lower
            # edge. A bar that blows through the whole zone (high above the zone) filled it too (B151).
            start_idx = msb_event["confirm_i"] + 1
            end_idx = min(start_idx + expiry_bars, len(bars))
            found_bar = None
            for k in range(start_idx, end_idx):
                if bars[k]["h"] >= fib_zone[0]:
                    found_bar = k
                    break
            if found_bar is None:
                continue
            entry_price = fib_zone[0]
            entry_t = bars[found_bar]["t"]
            stop = fib_zone[1] * (1 + stop_buffer_pct)
            side = "short"
        target_price = _r_target(entry_price, stop, side, target_r)
        signal = {
            "side": side,
            "entry_price": entry_price,
            "entry_t": entry_t,
            "stop": stop,
            "targets": [(target_price, 1.0)],
            "meta": {
                "setup": "fib_pullback",
                "rule_id": "C10-E04",
                "msb_i": msb_event["i"],
                "target_r": target_r,
                "placed_t": bars[msb_event["confirm_i"]]["t"],
                "valid_until_t": bars[end_idx - 1]["t"]
            }
        }
        signals.append(signal)
    return sorted(signals, key=lambda s: s["entry_t"])


def setup3_failed_msb_reversal(bars: list, failure_lookback: int = 20, stop_buffer_pct: float = 0.001, target_r: float = 2.0, msb_kwargs: dict | None = None) -> list:
    swings = find_swings(bars, **{k:v for k,v in (msb_kwargs or {}).items() if k in ("left","right","use_body")})
    msb_events = classify_msb(bars, swings, **(msb_kwargs or {}))
    signals = []
    for msb_event in msb_events:
        c = msb_event["confirm_i"]
        if len(bars) - 1 < c + failure_lookback:
            continue
        # Determine the post-break high/low
        swing_i = msb_event["broken_swing_i"]
        if msb_event["direction"] == "bull":
            broken_level = msb_event["broken_level"]
            # The "no new high" check must use the actual extreme reached while the
            # break was forming (from the swing to the confirm bar, inclusive), not
            # just the broken level itself -- price may have already wicked above it.
            structure_high = max(b["h"] for b in bars[swing_i:c+1])
            # Look at the next failure_lookback bars after c
            window_bars = bars[c+1 : c+1+failure_lookback]
            if len(window_bars) < failure_lookback:
                window_bars = bars[c+1:]
            # Check if any new high exceeds the structure extreme
            max_new_high = max(b["h"] for b in window_bars)
            if max_new_high > structure_high:
                continue  # The move continued, not failed
            # Check if the close at the end of the window is below the broken level
            last_close = window_bars[-1]["c"]
            if last_close >= broken_level:
                continue  # Not reversed yet
            # Emit reversal signal
            side = "short"
            entry_price = last_close
            entry_t = window_bars[-1]["t"]
            stop = broken_level * (1 + stop_buffer_pct)
        else:  # bear msb_event
            broken_level = msb_event["broken_level"]
            # The "no new low" check must use the actual extreme reached while the
            # break was forming (from the swing to the confirm bar, inclusive), not
            # just the broken level itself -- price may have already wicked below it.
            structure_low = min(b["l"] for b in bars[swing_i:c+1])
            # Look at the next failure_lookback bars after c
            window_bars = bars[c+1 : c+1+failure_lookback]
            if len(window_bars) < failure_lookback:
                window_bars = bars[c+1:]
            # Check if any new low is below the structure extreme
            min_new_low = min(b["l"] for b in window_bars)
            if min_new_low < structure_low:
                continue  # The move continued, not failed
            # Check if the close at the end of the window is above the broken level
            last_close = window_bars[-1]["c"]
            if last_close <= broken_level:
                continue  # Not reversed yet
            # Emit reversal signal
            side = "long"
            entry_price = last_close
            entry_t = window_bars[-1]["t"]
            stop = broken_level * (1 - stop_buffer_pct)
        target_price = _r_target(entry_price, stop, side, target_r)
        signal = {
            "side": side,
            "entry_price": entry_price,
            "entry_t": entry_t,
            "stop": stop,
            "targets": [(target_price, 1.0)],
            "meta": {
                "setup": "failed_msb_reversal",
                "rule_id": "C10-E05",
                "msb_i": msb_event["i"],
                "target_r": target_r
            }
        }
        signals.append(signal)
    return sorted(signals, key=lambda s: s["entry_t"])
