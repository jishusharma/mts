"""Independent arithmetic for angles (b) and (c): every factor recomputed with pandas straight from the raw monthly
CSVs, from the definitions in CONTEXT_FACTORS_SPEC.md, sharing NO code with context_asof.py (only its parameter
constants are imported so a parameter change cannot masquerade as a disagreement). Used by hand_check.py (angle c) and
trader_eye.py (angle b). Never reads a bar after the decision bar: `bars_upto(t)` is the only loader.
"""
import glob
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from context_asof import (ATR_N, BB_N, BB_K, WALK_N, K_ZONE, W_LADDER_PCT, STOP_FLOOR_PCT, PIVOT_N, KROWN_MAX_AGE,   # noqa: E402
                          VP_BIN, VA_PCT, ROUND_STEP, RET30_THR, SMA_PHASE, BAL_K, PCT_WIN, SQUEEZE_PCT, APPROACH_BARS,
                          APPROACH_FAST, SWEEP_BARS, FUND_HIGH, WEEKLY_TREND_BARS, TOUCH_LOOKBACK, ARCH, FUND_ARCH)

TS0_MS = 1640995200000
MS = 60000
MONDAY0 = pd.Timestamp("2022-01-03", tz="UTC")
RULES = {"4h": "4h", "8h": "8h", "12h": "12h", "1d": "24h", "1h": "1h"}   # tick-like rules so `origin` applies
NBARS = {"1h": 60, "4h": 240, "8h": 480, "12h": 720, "1d": 1440, "1w": 10080}


def utc(t):
    return pd.Timestamp(TS0_MS + t * MS, unit="ms", tz="UTC")


def bars_upto(t, lookback_days=100):
    """DataFrame of 1m bars with open time in [t - lookback_days, t], from the raw CSVs (pandas)."""
    t_ms = TS0_MS + t * MS
    lo_ms = t_ms - lookback_days * 86400000
    months = pd.period_range(pd.Timestamp(lo_ms, unit="ms"), pd.Timestamp(t_ms, unit="ms"), freq="M")
    frames = []
    for m in months:
        f = os.path.join(ARCH, f"BTCUSDT-1m-{m.year}-{m.month:02d}.csv")
        if not os.path.exists(f):
            continue
        df = pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4, 5], names=["open_time", "O", "H", "L", "C", "V"], dtype=str)
        df = df[df["open_time"].str[:1].str.isdigit()]
        df = df.astype({"open_time": "int64", "O": float, "H": float, "L": float, "C": float, "V": float})
        df.loc[df["open_time"] > 1e14, "open_time"] //= 1000
        frames.append(df)
    df = pd.concat(frames)
    df = df[(df["open_time"] >= lo_ms) & (df["open_time"] <= t_ms)].sort_values("open_time")
    assert df["open_time"].iloc[-1] == t_ms, "the decision bar must be on disk"
    df.index = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def funding_last(t):
    """(calc_time_ms, rate) of the last settlement at/before the close of bar t, from the raw funding CSVs."""
    close_ms = TS0_MS + (t + 1) * MS
    rows = []
    for f in sorted(glob.glob(os.path.join(FUND_ARCH, "BTCUSDT-fundingRate-202[234]-*.csv"))):
        d = pd.read_csv(f)
        rows.append(d)
    d = pd.concat(rows)
    d = d[d["calc_time"] <= close_ms].sort_values("calc_time")
    if len(d) == 0:
        return None
    r = d.iloc[-1]
    return int(r["calc_time"]), float(r["last_funding_rate"])


def candles(df, tf):
    """Closed candles of timeframe tf (complete bucket = NBARS bars present), plus the partial bucket holding the last bar."""
    if tf == "1w":
        g = df.resample("168h", origin=MONDAY0, label="left", closed="left")
    else:
        g = df.resample(RULES[tf], origin="epoch", label="left", closed="left")
    agg = g.agg(O=("O", "first"), H=("H", "max"), L=("L", "min"), C=("C", "last"), V=("V", "sum"), n=("O", "size"))
    agg = agg[agg["n"] > 0]
    closed = agg[agg["n"] == NBARS[tf]]
    partial = agg.iloc[-1]
    return closed, partial


def atr_sma(c4):
    """Plain-SMA ATR (FORMULAS.md s.12) over the last ATR_N closed candles; the first candle has no TR."""
    pc = c4["C"].shift(1)
    tr = pd.concat([c4["H"] - c4["L"], (c4["H"] - pc).abs(), (c4["L"] - pc).abs()], axis=1).max(axis=1)
    tr = tr.iloc[1:]
    return tr.rolling(ATR_N).mean()


def bollinger(closes):
    mid = closes.rolling(BB_N).mean()
    sd = closes.rolling(BB_N).std(ddof=0)
    up, lo = mid + BB_K * sd, mid - BB_K * sd
    return mid, up, lo, (up - lo) / mid, (closes - lo) / (up - lo)


def bb_state(closes, up, lo, bw):
    """State of the last closed bar (spec F5)."""
    c, u, l = closes.iloc[-1], up.iloc[-1], lo.iloc[-1]
    pc, pu, pl = closes.iloc[-2], up.iloc[-2], lo.iloc[-2]
    if not (u == u) or not (pu == pu):
        return "na"
    above, below = c >= u, c <= l
    p_above, p_below = pc >= pu, pc <= pl
    if not above and not below:
        return "reenter_from_lower" if p_below else "reenter_from_upper" if p_above else "inside"
    run = all((closes.iloc[-k] >= up.iloc[-k]) if above else (closes.iloc[-k] <= lo.iloc[-k]) for k in range(1, WALK_N + 1))
    expanding = bw.iloc[-1] > bw.iloc[-1 - WALK_N]
    if run and expanding:
        return "walk_up" if above else "walk_down"
    if above and not p_above:
        return "break_up"
    if below and not p_below:
        return "break_down"
    return "outside_up" if above else "outside_down"


def patterns(cl):
    """Patterns on the last closed candle (spec F4) from the closed-candle frame."""
    if len(cl) < 2:
        return "na"
    a, b = cl.iloc[-1], cl.iloc[-2]
    c = cl.iloc[-3] if len(cl) >= 3 else None
    out = []
    ag, ar = a.C > a.O, a.C < a.O
    bg, br = b.C > b.O, b.C < b.O
    if br and ag and a.C > b.O and a.O <= b.C:
        out.append("bull_engulf")
    if bg and ar and a.C < b.O and a.O >= b.C:
        out.append("bear_engulf")
    rng = a.H - a.L
    if rng > 0:
        body = abs(a.C - a.O)
        if min(a.O, a.C) - a.L >= 0.6 * rng and body <= 0.3 * rng:
            out.append("bull_pin")
        if a.H - max(a.O, a.C) >= 0.6 * rng and body <= 0.3 * rng:
            out.append("bear_pin")
    if a.H < b.H and a.L > b.L:
        out.append("inside")
    if a.H > b.H and a.L < b.L:
        out.append("outside")
    if c is not None:
        if ag and bg and c.C > c.O:
            out.append("three_up")
        if ar and br and c.C < c.O:
            out.append("three_down")
    return "|".join(sorted(out)) if out else "none"


def profile(df):
    """FORMULAS.md 18.1 profile of a bar set: (poc, val, vah), bins of VP_BIN USD, uniform spread over [l, h]."""
    w = VP_BIN
    k0 = int(math.floor(df["L"].min() / w))
    k1 = int(math.floor(df["H"].max() / w))
    vol = np.zeros(k1 - k0 + 1)
    for l, h, v in zip(df["L"].to_numpy(), df["H"].to_numpy(), df["V"].to_numpy()):
        if h > l:
            for k in range(int(math.floor(l / w)), int(math.floor(h / w)) + 1):
                ov = min(h, (k + 1) * w) - max(l, k * w)
                if ov > 0:
                    vol[k - k0] += v * ov / (h - l)
        else:
            vol[int(math.floor(l / w)) - k0] += v
    tot = vol.sum()
    if tot <= 0:
        return None
    kp = int(np.argmax(vol))
    lo = hi = kp
    acc = vol[kp]
    while acc < VA_PCT * tot and (lo > 0 or hi < len(vol) - 1):
        vl = vol[lo - 1] if lo > 0 else -1.0
        vh = vol[hi + 1] if hi < len(vol) - 1 else -1.0
        if vl >= vh and lo > 0:
            lo -= 1
            acc += vl
        elif hi < len(vol) - 1:
            hi += 1
            acc += vh
        else:
            lo -= 1
            acc += vl
    return ((k0 + kp) * w + w / 2, (k0 + lo) * w, (k0 + hi + 1) * w)


def fractal_pivots(cl, n):
    """(index_position, kind, price, confirmed_at_position) of strict fractal pivots on a closed-candle frame (18.2)."""
    H, L = cl["H"].to_numpy(), cl["L"].to_numpy()
    out = []
    for i in range(n, len(cl) - n):
        if all(H[i] > H[i - k] and H[i] > H[i + k] for k in range(1, n + 1)):
            out.append((i, "H", float(H[i]), i + n))
        if all(L[i] < L[i - k] and L[i] < L[i + k] for k in range(1, n + 1)):
            out.append((i, "L", float(L[i]), i + n))
    return out


def phase_a(cd):
    """Phase A on the closed daily frame: last two confirmed pivot highs and lows."""
    piv = sorted(fractal_pivots(cd, PIVOT_N), key=lambda r: (r[3], r[0], r[1]))
    hs, ls, last_dir, phase = [], [], None, "na"
    for i, kind, px, conf in piv:
        (hs if kind == "H" else ls).append(px)
    # replay the state day by day so the "last trend direction" is tracked as pivots confirm
    phase = "na"
    hs, ls = [], []
    for j in range(len(cd)):
        for i, kind, px, conf in piv:
            if conf == j:
                (hs if kind == "H" else ls).append(px)
        if len(hs) >= 2 and len(ls) >= 2:
            up = hs[-1] > hs[-2] and ls[-1] > ls[-2]
            dn = hs[-1] < hs[-2] and ls[-1] < ls[-2]
            if up or dn:
                last_dir = "up" if up else "down"
                phase = "markup" if up else "markdown"
            else:
                phase = "distribution" if last_dir == "up" else "accumulation" if last_dir == "down" else "range_initial"
    return phase


def hand_context(t, side, df=None):
    """Every factor at the close of bar t for `side`, by hand (pandas), as a flat dict with the engine's field names."""
    df = bars_upto(t) if df is None else df
    t_ms = TS0_MS + t * MS
    price = float(df["C"].iloc[-1])
    f = {"price": price}
    cl = {tf: candles(df, tf) for tf in ("1h", "4h", "8h", "12h", "1d", "1w")}
    for tf in ("4h", "8h", "12h", "1d"):
        c, p = cl[tf]
        f[f"c_{tf}"] = tuple(float(x) for x in c.iloc[-1][["O", "H", "L", "C"]]) if len(c) else None
        f[f"p_{tf}"] = (float(p.O), float(p.H), float(p.L), price)
        f[f"pat_{tf}"] = patterns(c)
    f["c_1w_hl"] = (float(cl["1w"][0].iloc[-1].H), float(cl["1w"][0].iloc[-1].L)) if len(cl["1w"][0]) else None
    c4 = cl["4h"][0]
    atr_s = atr_sma(c4)
    atr = float(atr_s.iloc[-1]) if len(atr_s) and atr_s.iloc[-1] == atr_s.iloc[-1] else float("nan")
    f["atr4"] = atr
    for tf in ("4h", "1d"):
        c = cl[tf][0]
        mid, up, lo, bw, pb = bollinger(c["C"])
        if len(c) >= BB_N + WALK_N:
            f[f"bb_{tf}_state"] = bb_state(c["C"], up, lo, bw)
            f[f"bb_{tf}_pctb"] = float(pb.iloc[-1])
            f[f"bb_{tf}_bw"] = float(bw.iloc[-1])
        else:
            f[f"bb_{tf}_state"], f[f"bb_{tf}_pctb"], f[f"bb_{tf}_bw"] = "na", float("nan"), float("nan")
        if tf == "1d":
            bb_d = (float(mid.iloc[-1]), float(up.iloc[-1]), float(lo.iloc[-1])) if mid.iloc[-1] == mid.iloc[-1] else None
    cd = cl["1d"][0]
    # phase
    f["phase_a"] = phase_a(cd) if len(cd) > 2 * PIVOT_N + 1 else "na"
    if len(cd) > SMA_PHASE:
        r = cd["C"].iloc[-1] / cd["C"].iloc[-31] - 1.0
        sma = cd["C"].iloc[-SMA_PHASE:].mean()
        f["phase_b"] = "markup" if r >= RET30_THR else "markdown" if r <= -RET30_THR else ("distribution" if cd["C"].iloc[-1] > sma else "accumulation")
    else:
        f["phase_b"] = "na"
    c1 = cl["1h"][0]
    if len(c1) >= 25 and atr == atr:
        last24 = c1.iloc[-24:]
        f["intraday"] = "balance" if last24["H"].max() - last24["L"].min() <= BAL_K * atr else ("trend_up" if c1["C"].iloc[-1] > c1["C"].iloc[-25] else "trend_down")
        prev12, last12 = c1.iloc[-24:-12], c1.iloc[-12:]
        inside = bool(((last12["C"] <= prev12["H"].max()) & (last12["C"] >= prev12["L"].min())).all())
        f["intraday_alt"] = "balance" if inside else ("trend_up" if c1["C"].iloc[-1] > c1["C"].iloc[-25] else "trend_down")
    else:
        f["intraday"] = f["intraday_alt"] = "na"
    # F7
    win = atr_s.dropna().iloc[-PCT_WIN:]
    if len(win) == PCT_WIN:
        rank = int((win <= atr).sum())
        fr = rank / PCT_WIN
        f["vol_regime"] = "low" if fr <= 1 / 3 else "mid" if fr <= 2 / 3 else "high"
    else:
        f["vol_regime"] = "na"
    _, _, _, bw4, _ = bollinger(c4["C"])
    wb = bw4.dropna().iloc[-PCT_WIN:]
    f["squeeze"] = bool(len(wb) == PCT_WIN and bw4.iloc[-1] <= np.percentile(wb, SQUEEZE_PCT))
    ts = utc(t)
    f["session"] = "asia" if ts.hour < 8 else "london" if ts.hour < 13 else "ny" if ts.hour < 21 else "late"
    f["weekend"] = ts.dayofweek >= 5
    fr = funding_last(t)
    f["funding"] = "na" if fr is None else ("neg" if fr[1] < 0 else "low" if fr[1] <= FUND_HIGH else "high")
    wk = cl["1w"][0]
    wt = ("up" if wk["C"].iloc[-1] > wk["C"].iloc[-1 - WEEKLY_TREND_BARS] else "down") if len(wk) > WEEKLY_TREND_BARS else "na"
    f["htf_align"] = (side == "long" and wt == "up") or (side == "short" and wt == "down")
    # ---- level ledger (grid points only: t % 60 == 59)
    levels = []
    if len(cd):
        d = cd.iloc[-1]
        av = int((d.name.value // 10**6 - TS0_MS) // MS) + 1439
        levels += [(float(d.H), "prior_d_hl", av), (float(d.L), "prior_d_hl", av)]
        day_bars = df[(df.index >= d.name) & (df.index < d.name + pd.Timedelta(days=1))]
        vp = profile(day_bars)
        if vp:
            levels += [(float(x), "fabio_vp_day", av) for x in vp]
    if len(wk):
        w = wk.iloc[-1]
        av = int((w.name.value // 10**6 - TS0_MS) // MS) + 10079
        levels += [(float(w.H), "prior_w_hl", av), (float(w.L), "prior_w_hl", av)]
        wbars = df[(df.index >= w.name) & (df.index < w.name + pd.Timedelta(days=7))]
        vp = profile(wbars)
        if vp:
            levels += [(float(x), "tom_vp_week", av) for x in vp]
    n4 = len(c4)
    for i, kind, px, conf in fractal_pivots(c4, PIVOT_N):
        if n4 - 1 - i <= KROWN_MAX_AGE:
            av = int((c4.index[conf].value // 10**6 - TS0_MS) // MS) + 239
            levels.append((px, "krown_zone", av))
    if len(cd) and bb_d is not None:
        d = cd.iloc[-1]
        av = int((d.name.value // 10**6 - TS0_MS) // MS) + 1439
        levels += [(x, "malkan_bb_d", av) for x in bb_d]
    day0 = ts.normalize()
    sb = df[df.index >= day0]
    tp = (sb["H"] + sb["L"] + sb["C"]) / 3
    levels.append((float((tp * sb["V"]).sum() / sb["V"].sum()), "vwap_session", int((day0.value // 10**6 - TS0_MS) // MS)))
    wk0 = MONDAY0 + pd.Timedelta(days=7 * ((ts - MONDAY0).days // 7))
    if ts >= MONDAY0:
        sb = df[df.index >= wk0]
        tp = (sb["H"] + sb["L"] + sb["C"]) / 3
        levels.append((float((tp * sb["V"]).sum() / sb["V"].sum()), "vwap_week", int((wk0.value // 10**6 - TS0_MS) // MS)))
    below = math.floor(price / ROUND_STEP) * ROUND_STEP
    if below == price:
        below -= ROUND_STEP
    levels += [(float(below), "round_1k", 0), (float(below + ROUND_STEP), "round_1k", 0)]
    if price == below + ROUND_STEP:
        levels.append((float(below + 2 * ROUND_STEP), "round_1k", 0))
    f["n_levels"] = len(levels)
    f["n_krown"] = sum(1 for lv in levels if lv[1] == "krown_zone")
    c1h = float(c1["C"].iloc[-1])
    c4h = float(c4["C"].iloc[-1]) if len(c4) else float("nan")

    def side_ok(lp, cref):
        return (cref > lp and lp < price) if side == "long" else (cref < lp and lp > price)

    def dist(lp):
        return price - lp if side == "long" else lp - price

    cands = [(dist(lp), lp, src, av) for lp, src, av in levels if side_ok(lp, c1h)]
    cands.sort(key=lambda r: (r[0], r[2], r[3]))
    if cands and atr == atr:
        d, lp, src, av = cands[0]
        f["near_price"], f["near_src"], f["near_dist_atr"] = lp, src, d / atr
        f["level_age_h"] = (t + 1 - av) / 60.0
        f["at_level"] = round(d / atr, 9) <= K_ZONE
        f["n_layers"] = len({s for dd, _, s, _ in cands if round(dd, 6) <= round(K_ZONE * atr, 6)})
        # touches: closed 1h bars after availability, within the lookback, before the bar holding t
        h1 = c1.iloc[:-1] if t % 60 == 59 else c1       # the 1h bar holding t is excluded
        first_ok = [k for k in range(len(h1)) if int((h1.index[k].value // 10**6 - TS0_MS) // MS) > av]
        h1 = h1.iloc[first_ok[0]:] if first_ok else h1.iloc[0:0]
        h1 = h1.iloc[-TOUCH_LOOKBACK:]
        tc = int(((h1["L"] <= lp) & (h1["H"] >= lp)).sum())
        f["touch_count"], f["first_touch"] = tc, tc == 0
        mv = float(c1["C"].iloc[-1 - APPROACH_BARS]) - c1h
        mv = -mv if side == "short" else mv
        f["approach"] = "fast" if mv >= APPROACH_FAST * atr else "slow" if mv > 0 else "away"
        last6 = c1.iloc[-SWEEP_BARS:]
        f["sweep"] = bool((last6["L"] < lp).any()) if side == "long" else bool((last6["H"] > lp).any())
    else:
        f.update(near_price=float("nan"), near_src="none", near_dist_atr=float("nan"), level_age_h=float("nan"), at_level=False,
                 n_layers=0, touch_count=-1, first_touch=False, approach="na", sweep=False)
    cands4 = sorted([(dist(lp), lp, src, av) for lp, src, av in levels if side_ok(lp, c4h)], key=lambda r: (r[0], r[2], r[3]))
    f["near_src_4hrule"] = cands4[0][2] if cands4 else "none"
    # ---- ladder: prior = last closed candle of 1d / 12h / 8h
    stops = {}
    for tf, key in (("1d", "stop_d_pct"), ("12h", "stop_12_pct"), ("8h", "stop_8_pct")):
        c = cl[tf][0]
        if len(c) == 0:
            stops[tf] = float("nan")
            continue
        x = c.iloc[-1]
        s = (price - x.L) / price * 100 if side == "long" else (x.H - price) / price * 100
        stops[tf] = s if s > 0 else float("nan")
        f[key] = stops[tf]
    valid = [(tf, s) for tf, s in (("1d", stops["1d"]), ("12h", stops["12h"]), ("8h", stops["8h"])) if s == s]
    under = [x for x in valid if x[1] <= W_LADDER_PCT]
    rung, stop = under[0] if under else (min(valid, key=lambda x: x[1]) if valid else ("none", float("nan")))
    f["ladder_rung"], f["ladder_stop_pct"] = rung, stop
    f["ladder_cost_r"] = 0.14 / stop if stop == stop else float("nan")
    f["ladder_below_floor"] = bool(stop == stop and stop < STOP_FLOOR_PCT)
    if len(cd):
        po = float(cd.iloc[-1].O)
        f["ladder_cond"] = price > po if side == "long" else price < po
        pday = cl["1d"][1]
        f["ladder_cond_alt"] = float(pday.H) > po if side == "long" else float(pday.L) < po
    st4 = f["bb_4h_state"]
    f["bb_long_conf"] = side == "long" and st4 == "reenter_from_lower"
    f["bb_short_veto_walk"] = side == "short" and st4 == "walk_down"
    f["bb_short_veto_band"] = side == "short" and f["bb_4h_pctb"] == f["bb_4h_pctb"] and f["bb_4h_pctb"] <= 0.0
    f["_levels"] = levels
    return f
