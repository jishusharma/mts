"""Malkan level-short 5-layer stack on 4h bars (card malkan-level-short-4h-count-1109). OBSERVATION / BACKTEST ONLY: no
order placement, no live import. Spec: research/malkan_level_shorts_2026-11-09/READING.md + PRE_REG.md (every parameter is
labelled there). All logic is causal: a value at bar i uses bars <= i; a higher-timeframe value is the last bar CLOSED at or
before the entry bar's open.

Layers: 1 level (confirmed 5/5 pivot-high zone that rejected price)  2 structure (divergence OR sweep)  3 trigger (RSI crosses
below its MA)  4 WaveTrend cross-down  5 higher-timeframe RSI fail. `scan` returns one chain per entry bar with a flag per
layer, so the caller can print the ladder (L1-3, +L4, +L5) and the firings (all five).

Bars: dicts {t (open ms), o, h, l, c}. ind: {"rsi","ma","wt1","wt2","wt_ev"} aligned lists (None/NaN = not available).
htf: {"d": (open_times, rsi), "w": (open_times, rsi)}.
"""
import math
from bisect import bisect_right

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma
from MyTradingSys.backtest.layers.wavetrend import wavetrend

H4_MS, DAY_MS, WEEK_MS = 4 * 3600000, 86400000, 7 * 86400000

# --- parameters; label per PRE_REG.md (OURS unless a quote is named) ---
PIVOT_K = 5                 # OURS: 5/5 pivot
ZONE_WIDTH = 0.005          # OURS: zone 0.5 pct wide, centred on the pivot high
REJECT = 0.01               # OURS: a low >= 1 pct under the pivot within k bars after it
ZONE_LIFE = 540             # OURS: bars (90 days of 4h)
WIN_MIN, WIN_MAX = 3, 10    # SOURCED: "between three and 10" (malkan_divergence_default.json), counted inclusive of both bars
SWING_K, SWING_MAX = 3, 50  # OURS swing 3/3; cap 50 borrowed from the reverse-divergence quote (GbXnw_tNMtw_raw.txt:460)
TRIGGER_WIN = 12            # OURS
RSI_LEVEL = 60.0            # SOURCED (Malkan 40/60 regime level)
ENTRY_WIN = 3               # OURS
WT_BAND, WT_NEAR = 53.0, 5.0    # band SOURCED (wavetrend.py Crosses:9-12); tolerance OURS
STOP_BACK, STOP_BUF = 3, 0.001  # OURS
MIN_STOP = 0.004            # OURS: cost rule 0a (fees < 0.25 R needs a stop >= 0.40 pct)
HORIZON = 60                # OURS: bars
FEE = 0.0004                # task card: 0.04 pct taker per side


def _ok(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))


def _pivot_high(x, r, k, strict_left=True):
    n = len(x)
    if r - k < 0 or r + k >= n:
        return False
    return all(x[q] < x[r] for q in range(r - k, r)) and all(x[q] <= x[r] for q in range(r + 1, r + k + 1))


def build_zones(bars, k=PIVOT_K, width=ZONE_WIDTH, reject=REJECT):
    """Confirmed pivot-high zones that rejected price once. Confirmed at the close of bar j+k."""
    h = [b["h"] for b in bars]
    out = []
    for j in range(k, len(bars) - k):
        if not _pivot_high(h, j, k):
            continue
        p = h[j]
        if min(bars[q]["l"] for q in range(j + 1, j + k + 1)) > p * (1 - reject):
            continue
        out.append({"j": j, "confirm": j + k, "p": p, "lo": p * (1 - width / 2), "hi": p * (1 + width / 2)})
    return out


def _series(bars, basis):
    return [b["c"] for b in bars] if basis == "close" else [b["h"] for b in bars]


def structure_at(i, bars, ind, zone, arm):
    """Layer 2 at setup bar i (bar already overlaps the zone). Returns {"kind","ref"} or None.
    sweep: high pierces the zone pivot and the bar closes back under it. div: price higher than a reference high while the RSI
    at that bar is lower; arm["div"] "W" = reference inside the 3-10 bar window (inclusive count), "S" = last confirmed 3/3 swing
    high within 50 bars; arm["basis"] close|wick."""
    b = bars[i]
    if b["h"] > zone["p"] and b["c"] < zone["p"]:
        return {"kind": "sweep", "ref": zone["j"]}
    x = _series(bars, arm["basis"])
    rsi = ind["rsi"]
    if i < 1 or x[i] < x[i - 1] or not _ok(rsi[i]):
        return None
    if arm["div"] == "W":
        for r in range(i - WIN_MIN + 1, max(i - WIN_MAX + 1, 1) - 1, -1):     # bars = i - r + 1 in [3, 10]
            if r < 1 or r + 1 > i or not _ok(rsi[r]):
                continue
            if x[r] >= x[r - 1] and x[r] >= x[r + 1] and x[i] > x[r] and rsi[i] < rsi[r]:
                return {"kind": "div", "ref": r}
        return None
    for r in range(i - SWING_K - 1, max(i - SWING_MAX, SWING_K) - 1, -1):    # most recent confirmed swing before i
        if _pivot_high(x, r, SWING_K):
            if _ok(rsi[r]) and x[i] > x[r] and rsi[i] < rsi[r]:
                return {"kind": "div", "ref": r}
            return None
    return None


def trigger_after(i, ind, tw=TRIGGER_WIN, strict60=False):
    """Layer 3: first bar k in [i, i+tw] where RSI closes below its MA from at-or-above it, with RSI >= 60 at some bar since
    the setup (bar i-1 on). strict60 also needs RSI[k] < 60."""
    rsi, ma = ind["rsi"], ind["ma"]
    n = len(rsi)
    for k in range(max(i, 1), min(i + tw, n - 1) + 1):
        if not all(_ok(v) for v in (rsi[k - 1], ma[k - 1], rsi[k], ma[k])):
            continue
        if not (rsi[k - 1] >= ma[k - 1] and rsi[k] < ma[k]):
            continue
        seen = [rsi[q] for q in range(max(i - 1, 0), k) if _ok(rsi[q])]
        if not seen or max(seen) < RSI_LEVEL:
            continue
        if strict60 and not rsi[k] < RSI_LEVEL:
            continue
        return k
    return None


def entry_after(k, bars, win=ENTRY_WIN):
    """First bar j in (k, k+win] whose low trades through the prior bar's open; fill min(open, prior open). (j, price) or None."""
    for j in range(k + 1, min(k + win, len(bars) - 1) + 1):
        ref = bars[j - 1]["o"]
        if bars[j]["l"] <= ref:
            return j, min(bars[j]["o"], ref)
    return None


def wt_ok(i, k, ref, ind):
    """Layer 4: wt1 down-cross between setup-2 and trigger bar k, with a peak (4 bars to the cross) within WT_NEAR of the band
    OR lower than the peak around the structure reference. NaN fails closed."""
    ev, wt1 = ind["wt_ev"], ind["wt1"]
    cross = [q for q in range(max(i - 2, 0), k + 1) if ev[q] == -1]
    if not cross:
        return False
    c0 = cross[-1]
    peak = [wt1[q] for q in range(max(c0 - 3, 0), c0 + 1) if _ok(wt1[q])]
    if not peak:
        return False
    peak = max(peak)
    if peak >= WT_BAND - WT_NEAR:
        return True
    refp = [wt1[q] for q in range(max(ref - 1, 0), min(ref + 2, len(wt1))) if _ok(wt1[q])]
    return bool(refp) and peak < max(refp)


def htf_asof(series, t, htf_ms, back=0):
    """Value of the (back+1)-th last HTF bar CLOSED at or before t (open + htf_ms <= t), else None."""
    times, vals = series
    idx = bisect_right(times, t - htf_ms) - 1 - back
    return vals[idx] if 0 <= idx < len(vals) else None


def htf_ok(d, d_prev, w, w_prev):
    """Layer 5: daily RSI below 60 and turning down, OR weekly RSI back under 60 after a prior-4-week max >= 60."""
    if _ok(d) and _ok(d_prev) and d < RSI_LEVEL and d < d_prev:
        return True
    prev = [v for v in (w_prev or []) if _ok(v)]
    return bool(_ok(w) and prev and w < RSI_LEVEL and max(prev) >= RSI_LEVEL)


def simulate(bars, j, entry, stop, target_r=1.0, horizon=HORIZON):
    """Short from `entry` on bar j. Per bar: stop first (a stop touch on the entry bar counts: its order is unknown), then the
    target. hit1/hit2/mfe_r track the best excursion before the stop. Fee-net = gross - FEE*(entry+exit)/risk."""
    risk = stop - entry
    last = min(j + horizon, len(bars) - 1)
    hit1 = hit2 = False
    mfe = 0.0
    out = None
    for q in range(j, last + 1):
        b = bars[q]
        if b["h"] >= stop:
            out = ("stop", q, stop, -1.0)
            break
        mfe = max(mfe, (entry - b["l"]) / risk)
        hit1 = hit1 or mfe >= 1.0
        hit2 = hit2 or mfe >= 2.0
        if mfe >= target_r:
            out = ("target", q, entry - target_r * risk, target_r)
            break
    if out is None:
        px = bars[last]["c"]
        out = ("time", last, px, (entry - px) / risk)
    kind, q, px, rg = out
    return {"outcome": kind, "exit_idx": q, "exit": px, "r_gross": rg, "r_net": rg - FEE * (entry + px) / risk,
            "hit1": hit1, "hit2": hit2, "mfe_r": mfe, "risk_pct": risk / entry}


def scan(bars, ind, htf, arm, k=PIVOT_K):
    """Every chain (zone touch + structure + trigger + entry) with per-layer flags, one per entry bar (best zone kept)."""
    n = len(bars)
    zones = build_zones(bars, k=k)
    for z in zones:   # a close above the zone top kills it
        z["death"] = z["j"] + ZONE_LIFE
        for q in range(z["confirm"] + 1, min(z["j"] + ZONE_LIFE, n - 1) + 1):
            if bars[q]["c"] > z["hi"]:
                z["death"] = q
                break
    chains = {}
    strict = bool(arm.get("strict60", False))
    for z in zones:
        for i in range(z["confirm"] + 1, min(z["death"], n - 1) + 1):
            b = bars[i]
            if not (b["h"] >= z["lo"] and b["l"] <= z["hi"]):
                continue
            s = structure_at(i, bars, ind, z, arm)
            if s is None:
                continue
            kk = trigger_after(i, ind, strict60=strict)
            if kk is None:
                continue
            if any(bars[q]["c"] > z["hi"] for q in range(i, kk + 1)):
                continue        # closed above the level from the setup bar to the trigger: the level did not hold (OURS)
            e = entry_after(kk, bars)
            if e is None:
                continue
            j, px = e
            stop = max(bars[q]["h"] for q in range(max(i - STOP_BACK, 0), j + 1)) * (1 + STOP_BUF)
            t = bars[j]["t"]
            l4 = wt_ok(i, kk, s["ref"], ind)
            l5 = htf_ok(htf_asof(htf["d"], t, DAY_MS, 0), htf_asof(htf["d"], t, DAY_MS, 1), htf_asof(htf["w"], t, WEEK_MS, 0),
                        [htf_asof(htf["w"], t, WEEK_MS, q) for q in range(1, 5)])
            tight = (stop - px) / px < MIN_STOP
            c = {"setup": i, "trigger": kk, "entry_idx": j, "entry": px, "stop": stop, "kind": s["kind"], "ref": s["ref"],
                 "zone_p": z["p"], "t": t, "l1": True, "l2": True, "l3": True, "l4": l4, "l5": l5, "too_tight": tight,
                 "fires": bool(l4 and l5 and not tight)}
            old = chains.get(j)
            if old is None or (c["fires"], c["zone_p"]) > (old["fires"], old["zone_p"]):
                chains[j] = c
    return [chains[j] for j in sorted(chains)]


def indicators_and_htf(b4, bd, bw):
    """RSI14 Wilder + SMA14 + WaveTrend (n1=10 n2=21) on 4h bars; daily/weekly RSI14 for the layer-5 gate."""
    rsi = rsi_core([b["c"] for b in b4])
    ma = rsi_ma(rsi, "SMA", 14)
    rows = wavetrend.compute([(b["t"], b["h"], b["l"], b["c"]) for b in b4], H4_MS)
    ind = {"rsi": rsi, "ma": ma, "wt1": [r.wt1 for r in rows], "wt2": [r.wt2 for r in rows], "wt_ev": [r.event for r in rows]}
    htf = {"d": ([b["t"] for b in bd], rsi_core([b["c"] for b in bd])),
           "w": ([b["t"] for b in bw], rsi_core([b["c"] for b in bw]))}
    return ind, htf
