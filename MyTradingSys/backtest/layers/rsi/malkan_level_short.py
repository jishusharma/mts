"""
Malkan level short (card malkan-level-short-4h-count-1109): the 5-layer confluence stack read from the operator's five
BTC 4h shorts, research/malkan_level_shorts_2026-11-09/READING.md. Labels: the stack is OURS (built from his reads);
the 60 line and RSI-under-its-MA trigger are SOURCED Malkan (WEB_RESEARCH.md, SEVEN_STAR_CAPTIONS.md); the level proxy
is OURS (operator lines are hand-drawn, so a level = a confirmed pivot high or low that price has respected).

Layers (a signal is the trigger bar i; every input is known at bar i's close; HTF bars count only once closed):
  level     a bar in the last WINDOW bars tagged a pivot level from below: high >= L*(1-TOL), close <= L*(1+TOL)
  structure bearish divergence (price higher high, RSI lower high; close or wick; window 3-10 or swing 5-50)
            OR a sweep (high above a confirmed pivot high, close back under it) in the last WINDOW bars
  trigger   RSI crosses under its 14 SMA this bar, RSI < 60, and RSI was >= 60 in the last 10 bars
  wavetrend wt1 crossed under wt2 in the last 4 bars and wt1 peaked >= 45 in the last 8 (near the 53/60 band)
  htf       last closed daily RSI <= 60 and falling, OR last closed weekly RSI back under 60 from >= 60 in 2 weeks
Entry: the next 1-3 bars trade under the prior bar's open (fill there, or at the open on a gap). Stop: highest high
from the level tag to entry, +5 bps. Exit: TARGET_R target or stop (stop first on a shared bar) or MAX_BARS close.
"""
from MyTradingSys.backtest.fees import BINANCE_TAKER
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core

SIXTY = 60.0          # Malkan's line (SOURCED); kept local: malkan_40_60 owns its own copy (D2)
WINDOW = 8            # bars back from the trigger in which the level tag / structure must sit (OURS)
TOL = 0.005           # level tolerance (OURS)
PIVOT = 5             # level pivots: 5 bars each side (OURS)
LEVEL_LOOKBACK = 360  # 60 days of 4h bars (OURS)
TARGET_R = 2.0
MAX_BARS = 60
FEE = BINANCE_TAKER    # taker per side (fees.py; no own cost constants)

BASE = frozenset({"level", "trigger"})
FULL = frozenset({"level", "structure", "trigger", "wavetrend", "htf"})

# Which of the 5 operator points the FULL stack catches on the fixture (pinned by the test; see REPORT.md)
OPERATOR_POINTS_FULL_STACK = {"C1": False, "C2": False, "V1": False, "V2": False, "C3": True}
# matches READING.md: only C3 shows all 5 layers; WaveTrend drops C2, V1, V2 (V1 crossed >4 bars early); HTF drops C1, C2, V1, V2


def _sma(x, n):
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if all(v is not None for v in w):
            out[i] = sum(w) / n
    return out


def _ema(x, p):
    a, out = 2 / (p + 1), [x[0]]
    for v in x[1:]:
        out.append(a * v + (1 - a) * out[-1])
    return out


def indicators(b):
    c = [x["c"] for x in b]
    rsi = rsi_core(c, 14)
    ap = [(x["h"] + x["l"] + x["c"]) / 3 for x in b]
    esa = _ema(ap, 10)
    d = _ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0.0 for a, e, dd in zip(ap, esa, d)]
    wt1 = _ema(ci, 21)
    return {"rsi": rsi, "rsi_ma": _sma(rsi, 14), "wt1": wt1, "wt2": _sma(wt1, 4)}


def pivots(vals, k, kind):
    """[(index, value)] of k-bar pivots; pivot j is known at bar j + k."""
    out = []
    for j in range(k, len(vals) - k):
        w = vals[j - k:j + k + 1]
        if (kind == "high" and vals[j] == max(w)) or (kind == "low" and vals[j] == min(w)):
            out.append((j, vals[j]))
    return out


def _htf_rsi_asof(htf, step_ms):
    """[(close_time_ms, rsi)] of higher-timeframe bars, keyed by the time each bar closes."""
    r = rsi_core([x["c"] for x in htf], 14)
    return [(x["t"] + step_ms, v) for x, v in zip(htf, r)]


def _last_closed(series, t_close, n=1):
    """the last n (close_time, rsi) rows closed at or before t_close, newest last."""
    rows = [s for s in series if s[0] <= t_close and s[1] is not None]
    return rows[-n:]


def signals(b4, b1d, b1w, layers=FULL, div_window=(3, 10), price_mode="close", structure="either", step_ms=4 * 3600 * 1000):
    """structure: "div", "sweep" or "either" (READING.md layer 2 is div OR sweep)."""
    ind = indicators(b4)
    rsi, ma, wt1, wt2 = ind["rsi"], ind["rsi_ma"], ind["wt1"], ind["wt2"]
    h = [x["h"] for x in b4]
    c = [x["c"] for x in b4]
    px = c if price_mode == "close" else h
    ph = pivots(h, PIVOT, "high")
    lv = sorted(ph + pivots([x["l"] for x in b4], PIVOT, "low"))
    sw = pivots(px, 2, "high")                      # structure swings, known 2 bars later
    d_rsi = _htf_rsi_asof(b1d, 86400000)
    w_rsi = _htf_rsi_asof(b1w, 7 * 86400000)
    out, skip_to = [], -1
    for i in range(30, len(b4) - 1):
        if i < skip_to or rsi[i] is None or ma[i] is None or rsi[i - 1] is None or ma[i - 1] is None:
            continue
        ok = {}
        ok["trigger"] = (rsi[i] < ma[i] and rsi[i] < SIXTY and (rsi[i - 1] >= ma[i - 1] or rsi[i - 1] >= SIXTY)
                         and max(v for v in rsi[i - 10:i + 1] if v is not None) >= SIXTY)
        if "trigger" in layers and not ok["trigger"]:
            continue
        lo = i - WINDOW
        if "level" in layers:
            known = [(j, v) for j, v in lv if j + PIVOT < i and i - j <= LEVEL_LOOKBACK]
            ok["level"] = any(h[k] >= L * (1 - TOL) and c[k] <= L * (1 + TOL) and j + PIVOT < k
                              for k in range(lo, i + 1) for j, L in known)
            if not ok["level"]:
                continue
        if "structure" in layers:
            s_known = [(j, v) for j, v in sw if j + 2 <= i and i - j <= 60]
            div = False
            for a in range(len(s_known) - 1):
                for bb in range(a + 1, len(s_known)):
                    j1, p1 = s_known[a]
                    j2, p2 = s_known[bb]
                    if j2 < lo or not (div_window[0] <= j2 - j1 <= div_window[1]):
                        continue
                    if p2 > p1 and rsi[j1] is not None and rsi[j2] is not None and rsi[j2] < rsi[j1]:
                        div = True
            sweep = any(h[k] > P and c[k] < P for k in range(lo, i + 1)
                        for j, P in ph if j + PIVOT < k and k - j <= LEVEL_LOOKBACK)
            ok["structure"] = {"div": div, "sweep": sweep, "either": div or sweep}[structure]
            if not ok["structure"]:
                continue
        if "wavetrend" in layers:
            cross = any(wt2[k] is not None and wt2[k - 1] is not None and wt1[k] < wt2[k] and wt1[k - 1] >= wt2[k - 1]
                        for k in range(i - 3, i + 1))
            ok["wavetrend"] = cross and max(wt1[i - 7:i + 1]) >= 45
            if not ok["wavetrend"]:
                continue
        if "htf" in layers:
            tc = b4[i]["t"] + step_ms
            d2 = _last_closed(d_rsi, tc, 2)
            w3 = _last_closed(w_rsi, tc, 3)
            daily = len(d2) == 2 and d2[1][1] <= SIXTY and d2[1][1] < d2[0][1]
            weekly = len(w3) == 3 and w3[2][1] < SIXTY and max(w3[0][1], w3[1][1]) >= SIXTY
            ok["htf"] = daily or weekly
            if not ok["htf"]:
                continue
        entry = j = None                               # one of the next 3 bars trades under the prior bar's open
        for jj in range(i + 1, min(i + 4, len(b4))):
            ref = b4[jj - 1]["o"]
            if b4[jj]["l"] < ref:
                entry, j = min(b4[jj]["o"], ref), jj
                break
        if entry is None:
            continue
        stop = max(h[max(lo, 0):j + 1]) * 1.0005
        if stop <= entry:
            continue
        out.append({"t_trigger": b4[i]["t"], "i": i, "j": j, "entry": entry, "stop": stop})
        skip_to = i + 6
    return out


def outcome(bars, j, entry, stop, target_r=TARGET_R, fee=FEE, max_bars=MAX_BARS):
    """short from bar j (the fill bar). Stop wins a bar that touches both. R net of a taker fee each side."""
    risk = stop - entry
    tgt, one_r = entry - target_r * risk, entry - risk
    fee_r = fee * 2 * entry / risk     # round trip, in R
    hit_1r = False
    for k in range(j, min(j + max_bars, len(bars))):
        if bars[k]["h"] >= stop:
            return {"hit_1r": hit_1r, "gross_r": -1.0, "net_r": -1.0 - fee_r, "bars": k - j, "exit": "stop"}
        if bars[k]["l"] <= one_r:
            hit_1r = True
        if bars[k]["l"] <= tgt:
            return {"hit_1r": True, "gross_r": target_r, "net_r": target_r - fee_r, "bars": k - j, "exit": "target"}
    k = min(j + max_bars, len(bars)) - 1
    g = (entry - bars[k]["c"]) / risk
    return {"hit_1r": hit_1r, "gross_r": g, "net_r": g - fee_r, "bars": k - j, "exit": "time"}
