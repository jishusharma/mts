"""Krown events: {i, side, setup, tags} per bar for setups S1-S9 of KROWN_LAYER_SPEC s3.

Compatible with layers/runner.py forward_return_stats. Flag-gated: build_events returns [] unless enabled (params
`enabled`, default false) or enabled=True is passed. Alert-only descriptive events: no entry, stop or exit rule is
implemented (almost every stop distance is OURS and not in v0). Every event at bar i uses bars <= i only.
"""
import krown_core as kc

SETUPS = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9")


def _ev(i, side, setup, tags=None):
    return {"i": i, "side": side, "setup": setup, "tags": list(tags or [])}


def setup_s5(cross, c, sma200):
    """MA-CONTEXT (KR-M02): 21/55 EMA up-cross with price above the 200 -> long; down-cross below it -> short."""
    out = []
    for t, x in enumerate(cross):
        if x is None or sma200[t] is None:
            continue
        if x == "up" and c[t] > sma200[t]:
            out.append(_ev(t, "long", "S5", ["21x55=up", "above200"]))
        elif x == "down" and c[t] < sma200[t]:
            out.append(_ev(t, "short", "S5", ["21x55=down", "below200"]))
    return out


def setup_s6(leashes):
    """LEASH (KR-M06, provisional): reconnect after >= 3 disconnected closes; long when the candle sat above the EMA."""
    return [_ev(i, side, "S6", [f"leash={run}"]) for i, side, run in leashes]


def setup_s8(bbwp, h, l, c, p):
    """VOL-COMPRESSION BREAKOUT (KR-Q05): BBWP <= low inside the last s8_recent bars, first bar above the confirm level,
    close beyond the prior s8_break_n bars."""
    out = []
    n = p["s8_break_n"]
    for t in range(1, len(c)):
        b, b1 = bbwp[t], bbwp[t - 1]
        if b is None or b1 is None or not (b > p["bbwp_confirm"] >= b1):
            continue
        recent = [x for x in bbwp[max(0, t - p["s8_recent"]):t] if x is not None]
        if not recent or min(recent) > p["bbwp_low"] or t < n:
            continue
        if c[t] > max(h[t - n:t]):
            out.append(_ev(t, "long", "S8", [f"bbwp={b:.0f}"]))
        elif c[t] < min(l[t - n:t]):
            out.append(_ev(t, "short", "S8", [f"bbwp={b:.0f}"]))
    return out


def setup_s9(top_fires):
    """TOP-4 SELL FRAMEWORK (KR-P01): a sell signal for long-term holders, tagged short here for the event study."""
    return [_ev(t, "short", "S9", ["top3of4"]) for t in top_fires]


def fire_counts(events, nbars):
    out = {s: {"n": 0, "per_10_bars": 0.0} for s in SETUPS}
    for e in events:
        out[e["setup"]]["n"] += 1
    for s in SETUPS:
        out[s]["per_10_bars"] = round(out[s]["n"] * 10 / nbars, 6) if nbars else 0.0
    return out


def over_ceiling(counts, ceiling=1.0):
    """PRE_REG_KROWN item 3: fire rate per setup <= 1 event per 10 daily bars pooled."""
    return [s for s in SETUPS if counts[s]["per_10_bars"] > ceiling]


def build_events(o, h, l, c, v, enabled=None, params=None):
    p = dict(kc.load_params(), **(params or {}))
    if enabled is None:
        enabled = p["enabled"]
    if not enabled:
        return []
    n = len(c)
    ratio = kc.vol_ratio(v, p["vol_sma"])
    state = kc.trend_state(h, l, c, p["zone_k"], p["swing_tol"])
    sw = kc.swings(h, l, p["zone_k"])
    bw = kc.bbwp(c, p["bbwp_basis"], p["bbwp_lookback"], p["bbwp_mult"])
    ema_fast, ema_slow = kc.ema(c, p["ma_fast"]), kc.ema(c, p["ma_slow"])
    sma_long = kc.sma(c, p["ma_long"])
    ema_leash = kc.ema(c, p["ma_leash"])
    rsi_line = kc.rsi(c, p["rsi_period"])
    m_line, m_sig = kc.macd(c, p["macd_fast"], p["macd_slow"], p["macd_signal"])
    m_cross = kc.crosses(m_line, m_sig)
    ratio30 = kc.vol_ratio(v, p["tops_vol_sma"])

    def proof(t):
        """(bull, bear) proof candle at t: hammer / strict bullish engulfing, star / strict bearish engulfing."""
        eng = kc.engulfing(h, l, c, t)
        return (kc.is_hammer(o[t], h[t], l[t], c[t], p) or eng == "bull",
                kc.is_shooting_star(o[t], h[t], l[t], c[t], p) or eng == "bear")

    events = []
    for t in range(1, n):
        bull, bear = proof(t)
        st = state[t]["state"]
        zs = kc.zones_from(sw, h, l, c, ratio, t, p) if t >= 2 * p["zone_k"] else []
        r = ratio[t]
        # S1 ZONE-TEST: tested and held, with the trend (KR-Z17), a proof candle and volume >= 2x
        if r is not None and r >= p["s1_vol_mult"]:
            for z in zs:
                if z["kind"] == "L" and st == "up" and bull and l[t] <= z["hi"] and c[t] >= z["lo"]:
                    events.append(_ev(t, "long", "S1", [f"turns={z['turns']}", f"vol={r:.1f}"]))
                    break
                if z["kind"] == "H" and st == "down" and bear and h[t] >= z["lo"] and c[t] <= z["hi"]:
                    events.append(_ev(t, "short", "S1", [f"turns={z['turns']}", f"vol={r:.1f}"]))
                    break
        # S2 BREAK-CLOSE: first close beyond a zone's outer boundary on volume above average
        if r is not None and r >= p["s2_vol_mult"]:
            for z in zs:
                if z["kind"] == "H" and c[t] > z["hi"] >= c[t - 1]:
                    events.append(_ev(t, "long", "S2", [f"turns={z['turns']}", f"vol={r:.1f}"]))
                    break
                if z["kind"] == "L" and c[t] < z["lo"] <= c[t - 1]:
                    events.append(_ev(t, "short", "S2", [f"turns={z['turns']}", f"vol={r:.1f}"]))
                    break
        rs = kc.range_state(h, l, c, t, p)
        # S3 RANGE-EDGE: edges only, with a proof candle (KR-R01)
        if rs and rs["edge"] == "low" and bull and not rs["breakout"]:
            events.append(_ev(t, "long", "S3", ["edge=low"]))
        elif rs and rs["edge"] == "high" and bear and not rs["breakout"]:
            events.append(_ev(t, "short", "S3", ["edge=high"]))
        # S4 COIL-BREAK: compression on the previous bar, then a range-breaking close
        if rs and rs["breakout"] and t - 1 >= 0:
            cs = kc.coil_score(h, l, t - 1, p["coil_recent"], p["range_n"])
            if cs is not None and cs < p["coil_max"]:
                events.append(_ev(t, "long" if rs["breakout"] == "up" else "short", "S4", [f"coil={cs:.2f}"]))
        # S7 CAPITULATION: hammer on the biggest volume bar of the window after a downtrend (KR-V07, provisional)
        lb = p["s7_vol_lookback"]
        if bull and kc.is_hammer(o[t], h[t], l[t], c[t], p) and state[t - 1]["state"] == "down" and t >= lb \
                and v[t] >= max(v[t - lb:t + 1]):
            events.append(_ev(t, "long", "S7", ["biggest_volume"]))
    events += setup_s5(kc.crosses(ema_fast, ema_slow), c, sma_long)
    events += setup_s6(kc.leash(l, h, ema_leash, p["leash_n"]))
    events += setup_s8(bw, h, l, c, p)
    # S9 TOP-4: four signals (KR-P01)
    div = set(kc.bear_divergence(h, l, rsi_line, p["zone_k"]))
    candle = [t >= 2 and (kc.is_shooting_star(o[t], h[t], l[t], c[t], p) or kc.engulfing(h, l, c, t) == "bear"
                          or kc.three_crows(o, c, t)) for t in range(n)]
    volx = [ratio30[t] is not None and ratio30[t] >= p["vol_mult"] for t in range(n)]
    volat = [bw[t] is not None and bw[t] > p["bbwp_high"] for t in range(n)]
    mom = [t in div or m_cross[t] == "down" for t in range(n)]
    events += setup_s9(kc.tops(candle, volx, volat, mom, p["tops_window"], p["tops_need"]))
    events.sort(key=lambda e: (e["i"], e["setup"], e["side"]))
    return events
