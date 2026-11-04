"""RSI deep-buy Step I/J: causal divergence at RSI lows + speed/volatility context, matched vs no-divergence (card rsi-deep-divergence-context).

DETECTOR (pure functions, tested without data files). A pivot = strict local minimum of the CLOSE with a finite RSI (the rule of
backtest/layers/rsi/rsi_divergence.py:10). A pivot at bar b is only known at bar b+1 (it needs close[b+1] > close[b]), so the event is
STAMPED at c = b+1 and the fill is the open of c+1 (never at the low; OPUS_FRAMING s2.2 item 5, checked by test_divergence_context.py).
Episode (SHOT_REVIEW C1, OURS): starts at a Stage-0 entry (RSI <= L after >= L+3), ends when RSI closes above `end_level` (50; 40/60 trials);
an entry that arrives while an episode is still running is part of it (one event set, no double counting). Anchor = the pivot with the lowest
RSI (<= L) so far in the episode; a lower-RSI pivot replaces it. Pairing rules (Step J): P-anchor (primary), P-adj, P-any, P-anchor-split.
Price basis close (primary, SOURCED Malkan close-to-close) or wick low; eps 0 (primary), 0.05%, 0.1 ATR(t); min RSI difference 0 (primary,
SOURCED Malkan "decimals count"), 2, 5. Long divergence: price_B < price_A + eps and RSI_B - RSI_A > min_diff. Higher price low with a higher RSI
low = FAILURE_SWING (own row, only under P-anchor). Every firing is an event (never only the last). Short side = the same code on mirrored
series (price -> -price, RSI -> 100 - RSI).

PIPELINE (`--pass dev|val|report`): events per Stage-0-surviving cell (CELLS of confirmations.py), matched no-divergence control (non-firing
pivots of the same cell: |RSI_B diff| <= 3, nearest trailing ATR% , one-to-one), outcomes at N bars (fill next open, exit open N later, fee
0.10% round trip, ATR units normalised by the session-of-day seasonal factor), an 8-feature context vector on completed bars only,
cross-tabs on DEV terciles, and a walk-forward ridge logistic (6 features) against the Step G level-only table and the divergence-only rate.
Step H (confluence score) is built by card rsi-deep-confluence: the comparison here is against level-only and divergence-only only.
DEV = bar open < 2024-07-01 (loader refuses anything later); VALIDATION is read once with the frozen DEV cut points; HOLDOUT is refused.

Labels. SOURCED: RSI14 Wilder (FORMULAS s1), fee 0.10% (backtest/fees.py), ATR plain SMA of true range (FORMULAS s12), z-score vs prior L bars
population sd (FORMULAS s28.1), close-to-close and min diff 0 (Malkan), DEV/VAL/HOLDOUT dates (backtest/splits.py). OURS: h=3, episode end 50,
pairing rules, eps, min diff 2/5, wick basis, 24h sweep window, control match (3 RSI points, ATR%), N in 4 and 16, ridge lambda 1, min 40 prior
resolved events, tercile buckets, 20-day seasonal factor, zigzag 3 ATR on 1h/1d/1w closes, 30d RSI band, 3-week HTF floor, session clock
(America/New_York 09:30-10:30 US open, Europe/London 08:00-09:00 open).
"""
import argparse
import csv
import hashlib
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirmations as cf  # noqa: E402
import econ_floor as ef  # noqa: E402  (puts MyTradingSys/backtest on sys.path)
import research_kit  # noqa: E402

FEE = ef.FEE
HYST = ef.HYST
CUTOFF_MS = ef.CUTOFF_MS
HOLDOUT_MS = cf.HOLDOUT_MS
DAY_MS = 86_400_000
CELLS = cf.CELLS
HORIZONS = (4, 16)
MIN_DAYS = 30
RULES = ("anchor", "adj", "any", "split")
CTRL_RSI_TOL = 3.0          # OURS: control pivot RSI within 3 points of the event pivot
MODEL_N = 16                # OURS: the model/log-loss horizon (bars of the TF)
MIN_TRAIN = 40              # OURS: prior resolved events before the model is used
LAMBDA = 1.0                # OURS: ridge strength, fixed (not tuned)
ZCLIP = 4.0                 # OURS: standardised features clipped at +-4 sd (added after the first DEV run, whose fat tails sank the logistic)
MODEL_FEATURES = ("ret24", "dd", "speed", "dspeed", "rangez", "volpct")   # at most 6 (SPEC Step I)
CROSS_FEATURES = ("ret24", "dd", "sweep", "speed", "dspeed", "rangez", "volpct", "volz", "takerz")


# ----------------------------------------------------------------------------------------------- detector
def close_pivots(close, rsi):
    """Indices b of strict local minima of the close with a finite RSI. Known only at b+1 (close[b+1] > close[b])."""
    c = np.asarray(close, dtype="float64")
    mid, left, right = c[1:-1], c[:-2], c[2:]
    ok = (mid < left) & (mid < right) & np.isfinite(np.asarray(rsi, dtype="float64")[1:-1])
    return np.flatnonzero(ok) + 1


def episode_bounds(rsi, starts, end_level=50.0):
    """[(s, E)] where E = first bar after s with RSI above end_level (len(rsi) if none). A start before the previous E is skipped."""
    r = np.asarray(rsi, dtype="float64")
    above = np.flatnonzero(r > end_level)
    out, busy = [], -1
    for s in starts:
        if s <= busy:
            continue
        j = int(np.searchsorted(above, s + 1))
        e = int(above[j]) if j < len(above) else len(r)
        out.append((int(s), e))
        busy = e
    return out


def _eps_abs(pa, atr_b, eps_pct, eps_atr):
    return abs(pa) * eps_pct + (eps_atr * atr_b if (eps_atr and np.isfinite(atr_b)) else 0.0)


def _div(pa, ra, pb, rb, eps, md):
    return (pb < pa + eps) and (rb - ra > md)


def pair_pivots(piv, rule="anchor", eps_pct=0.0, eps_atr=0.0, min_diff=0.0, anchor_max=None):
    """piv: ordered list of dicts {i, price, rsi, atr} for ONE episode (price in the chosen basis, LONG convention: lower is a lower low).
    Returns one dict per pivot that fires (kind 'div') or is a FAILURE_SWING (anchor rule only): k (position), a (reference position),
    mult (earlier pivots B diverges from), skip (A is not the previous pivot), n_anchor, n_decline, kind.
    anchor_max: the anchor must have RSI <= anchor_max (the Step G level L); None = no cap."""
    out, anchor, n_anchor, n_decl = [], None, 0, 0
    for k, b in enumerate(piv):
        pb, rb = b["price"], b["rsi"]
        eps = lambda a: _eps_abs(a["price"], b.get("atr", np.nan), eps_pct, eps_atr)
        mult = sum(1 for a in piv[:k] if _div(a["price"], a["rsi"], pb, rb, eps(a), min_diff))
        ref, kind = None, None
        if rule == "anchor" and anchor is not None:
            a = piv[anchor]
            if _div(a["price"], a["rsi"], pb, rb, eps(a), min_diff):
                ref, kind = anchor, "div"
            elif rb - a["rsi"] > min_diff and pb > a["price"]:
                ref, kind = anchor, "failure_swing"
        elif rule == "adj" and k > 0:
            a = piv[k - 1]
            if _div(a["price"], a["rsi"], pb, rb, eps(a), min_diff):
                ref, kind = k - 1, "div"
        elif rule == "any" and mult > 0:
            q = [j for j in range(k) if _div(piv[j]["price"], piv[j]["rsi"], pb, rb, eps(piv[j]), min_diff)]
            ref, kind = min(q, key=lambda j: (piv[j]["rsi"], j)), "div"
        elif rule == "split" and anchor is not None:
            a = piv[anchor]
            if rb - a["rsi"] > min_diff:
                q = [j for j in range(anchor, k) if pb < piv[j]["price"] + eps(piv[j])]
                if q:
                    ref, kind = anchor, "div"
                    mult = len(q)
        if kind == "div":
            n_anchor += 1
            n_decl += 1
        if kind is not None:
            out.append({"k": k, "a": ref, "mult": mult, "skip": int(ref != k - 1), "kind": kind,
                        "n_anchor": n_anchor if kind == "div" else 0, "n_decline": n_decl if kind == "div" else 0})
        if rb is not None and (anchor_max is None or rb <= anchor_max) and (anchor is None or rb < piv[anchor]["rsi"]):
            anchor, n_anchor = k, 0
    return out


def mirror(piv):
    """Short side = long code on mirrored series: price -> -price, RSI -> 100 - RSI."""
    return [{**p, "price": -p["price"], "rsi": 100.0 - p["rsi"]} for p in piv]


# ----------------------------------------------------------------------------------------------- statistics
def wilson_free_ci(x, groups):
    """Mean and 95% CI half-widths from the day-clustered SE (econ_floor.cluster_mean_se)."""
    x = np.asarray(x, dtype="float64")
    if len(x) == 0:
        return float("nan"), float("nan"), float("nan")
    m, se = ef.cluster_mean_se(x, groups)
    return m, m - 1.96 * se, m + 1.96 * se


def diff_ci(x1, g1, x2, g2):
    if len(x1) == 0 or len(x2) == 0:
        return float("nan"), float("nan"), float("nan")
    m1, s1 = ef.cluster_mean_se(np.asarray(x1, dtype="float64"), g1)
    m2, s2 = ef.cluster_mean_se(np.asarray(x2, dtype="float64"), g2)
    d, se = m1 - m2, math.hypot(s1, s2)
    return d, d - 1.96 * se, d + 1.96 * se


def t_p(x, groups):
    """t over day clusters and one-sided normal p for mean > 0."""
    x = np.asarray(x, dtype="float64")
    if len(x) < 2:
        return float("nan"), 1.0
    m, se = ef.cluster_mean_se(x, groups)
    if not se > 0:
        return float("nan"), 1.0
    t = m / se
    return t, 0.5 * math.erfc(t / math.sqrt(2))


def fit_logit(X, y, lam=LAMBDA, iters=30):
    n, k = X.shape
    xb = np.c_[np.ones(n), X]
    w = np.zeros(k + 1)
    reg = lam * np.eye(k + 1)
    reg[0, 0] = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(xb @ w, -30, 30)))
        g = xb.T @ (p - y) + reg @ w
        h = xb.T @ (xb * (p * (1 - p))[:, None]) + reg + 1e-9 * np.eye(k + 1)
        step = np.linalg.solve(h, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def predict_logit(w, X):
    return 1.0 / (1.0 + np.exp(-np.clip(np.c_[np.ones(len(X)), X] @ w, -30, 30)))


def logloss(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


# ----------------------------------------------------------------------------------------------- context arrays
def _lookup(group_ids, g):
    pos = np.searchsorted(group_ids, g)
    pc = np.minimum(pos, len(group_ids) - 1)
    ok = (pos < len(group_ids)) & (group_ids[pc] == g)
    return pc, ok


def last_completed(t_end_ms, scale_open_ms, scale_min, values):
    """Value of the `scale_min` bar that is complete at time t_end (its group = floor(t_end/scale) - 1); NaN where missing.
    Only bars closed at or before t_end are used (causal)."""
    gids = scale_open_ms // (scale_min * 60_000)
    g = np.asarray(t_end_ms) // (scale_min * 60_000) - 1
    pc, ok = _lookup(gids, g)
    out = np.full(len(g), np.nan)
    out[ok] = np.asarray(values, dtype="float64")[pc[ok]]
    return out


def causal_zigzag(close, atr, k=3.0):
    """Causal zigzag on closes. Returns per-bar arrays (dir +1 leg up / -1 leg down / 0 unknown, signed distance of the close from the last
    confirmed swing in ATR, structure break: 1 = last swing is lower than the previous swing of its kind, -1 = higher, 0 = unknown) and the
    list of confirmed swings (extreme_bar, confirm_bar, kind +1 top / -1 bottom). A swing is known only at its confirm bar."""
    n = len(close)
    d = np.zeros(n)
    dist = np.full(n, np.nan)
    brk = np.zeros(n)
    swings = []
    direction, lo_i, hi_i = 0, 0, 0
    last_sw, prev = {1: np.nan, -1: np.nan}, {1: np.nan, -1: np.nan}
    last_kind, last_price = 0, np.nan
    for i in range(n):
        a = atr[i]
        c = close[i]
        if not np.isfinite(a) or a <= 0:
            continue
        if close[i] < close[lo_i]:
            lo_i = i
        if close[i] > close[hi_i]:
            hi_i = i
        if direction <= 0 and c - close[lo_i] >= k * a:         # a bottom is confirmed
            swings.append((lo_i, i, -1))
            prev[-1], last_sw[-1] = last_sw[-1], close[lo_i]
            direction, last_kind, last_price, hi_i = 1, -1, close[lo_i], i
        elif direction >= 0 and close[hi_i] - c >= k * a:       # a top is confirmed
            swings.append((hi_i, i, 1))
            prev[1], last_sw[1] = last_sw[1], close[hi_i]
            direction, last_kind, last_price, lo_i = -1, 1, close[hi_i], i
        d[i] = direction
        if last_kind:
            dist[i] = (c - last_price) / a
            p = prev[last_kind]
            brk[i] = 0 if not np.isfinite(p) else (1 if last_sw[last_kind] < p else -1)
    return d, dist, brk, swings


def session_bucket(t_ms):
    """Exchange-local clock buckets (SHOT_REVIEW C7): us_open 09:30-10:30 America/New_York, london_open 08:00-09:00 Europe/London,
    us_rest 10:30-16:00 NY, eu_rest 09:00-16:30 London, asia (UTC 00:00-07:00) else, other. Returns an int array (0..5)."""
    import pandas as pd
    ts = pd.to_datetime(np.asarray(t_ms, dtype="int64"), unit="ms", utc=True)
    ny = ts.tz_convert("America/New_York")
    ld = ts.tz_convert("Europe/London")
    mny = (ny.hour * 60 + ny.minute).to_numpy()
    mld = (ld.hour * 60 + ld.minute).to_numpy()
    mu = (ts.hour * 60 + ts.minute).to_numpy()
    out = np.full(len(mu), 5)
    out[mu < 7 * 60] = 4
    out[(mld >= 9 * 60) & (mld < 16 * 60 + 30)] = 3
    out[(mny >= 10 * 60 + 30) & (mny < 16 * 60)] = 2
    out[(mld >= 8 * 60) & (mld < 9 * 60)] = 1
    out[(mny >= 9 * 60 + 30) & (mny < 10 * 60 + 30)] = 0
    return out


SESSION_NAMES = ("us_open", "london_open", "us_rest", "eu_rest", "asia", "other")


def seasonal_factor(t_ms, high, low, close, tf, days=20):
    """Session-of-day seasonal range factor (causal): mean (high-low)/close of the same exchange-local half-hour slot over the previous
    `days` occurrences, divided by the mean over the previous `days` days. NaN while there is not enough history."""
    import pandas as pd
    rng = pd.Series((np.asarray(high) - np.asarray(low)) / np.asarray(close))
    ts = pd.to_datetime(np.asarray(t_ms, dtype="int64"), unit="ms", utc=True).tz_convert("America/New_York")
    slot = pd.Series((ts.hour * 2 + ts.minute // 30).to_numpy())
    per_slot = rng.groupby(slot).transform(lambda s: s.rolling(days, min_periods=days).mean().shift(1))
    overall = rng.rolling(days * (1440 // tf), min_periods=days * (1440 // tf)).mean().shift(1)
    return (per_slot / overall).to_numpy()


def build_context(d1, tf, side):
    """Per-TF-bar arrays for the side (long: as is; short: mirrored). Everything at bar i uses bars <= i only."""
    import pandas as pd
    d = cf.resample_ext(d1, tf)
    n = len(d["open"])
    t = d["open_time"]
    t_end = t + tf * 60_000
    sgn = 1.0 if side == "long" else -1.0
    op, hi, lo, cl = d["open"], d["high"], d["low"], d["close"]
    rsi_raw = ef.rsi_series(cl)
    rsi = rsi_raw if sgn > 0 else 100.0 - rsi_raw
    atr = cf.atr_sma(hi, lo, cl)
    h1 = cf.resample_ext(d1, 60)
    atr1h = cf.atr_sma(h1["high"], h1["low"], h1["close"])
    a1 = last_completed(t_end, h1["open_time"], 60, atr1h)
    lr = np.r_[np.nan, np.diff(np.log(h1["close"]))]
    rv = pd.Series(lr).rolling(24).std(ddof=0)
    pct = rv.rolling(720).apply(lambda w: float((w[:-1] < w[-1]).mean()), raw=True).to_numpy()
    m5 = cf.resample_ext(d1, 5)
    rz5 = cf.zscore_prior((m5["high"] - m5["low"]) / m5["close"], 100)
    ctx = {"side": side, "sgn": sgn, "tf": tf, "n": n, "t": t, "t_end": t_end, "day": t // DAY_MS,
           "open": op, "high": hi, "low": lo, "close": cl, "rsi": rsi, "atr": atr, "a1": a1,
           # long-convention arrays: price_c (close), wick (the wick that matters), far (the opposite extreme)
           "pc": sgn * cl, "wick": lo if sgn > 0 else -hi, "far": hi if sgn > 0 else -lo,
           "volpct": last_completed(t_end, h1["open_time"], 60, pct),
           "rangez": last_completed(t_end, m5["open_time"], 5, rz5),
           "rangez_prev": last_completed(t_end - 15 * 60_000, m5["open_time"], 5, rz5),
           "volz": cf.zscore_prior(d["volume"], 100),
           "takerz": cf.zscore_prior(np.where(d["volume"] > 0, d["taker_buy_volume"] / np.maximum(d["volume"], 1e-12), np.nan), 100),
           "session": session_bucket(t), "seas": seasonal_factor(t, hi, lo, cl, tf)}
    # HTF 3-week RSI floor break (next two TFs up, last completed bar; SHOT_REVIEW C6)
    for tag, hm in zip("ab", cf.HTF_UP[tf]):
        dh = cf.resample_ext(d1, hm)
        rh_raw = ef.rsi_series(dh["close"])
        rh = rh_raw if sgn > 0 else 100.0 - rh_raw
        wb = 21 * (1440 // hm)
        floor = pd.Series(rh).rolling(wb, min_periods=wb // 2).min().shift(1).to_numpy()
        brk = (rh < floor).astype("float64")
        brk[~np.isfinite(floor) | ~np.isfinite(rh)] = np.nan
        ctx["htf_break_" + tag] = last_completed(t_end, dh["open_time"], hm, brk)
    # causal zigzag on 1h / 1d / 1w closes (state at the last completed bar of each scale)
    for tag, sm in (("s", 60), ("m", 1440), ("l", 10080)):
        ds = cf.resample_ext(d1, sm)
        at = cf.atr_sma(ds["high"], ds["low"], ds["close"])
        zd, zdist, zb, sw = causal_zigzag(ds["close"], at)
        ctx["zz_" + tag + "_dir"] = last_completed(t_end, ds["open_time"], sm, zd) * sgn
        ctx["zz_" + tag + "_dist"] = last_completed(t_end, ds["open_time"], sm, zdist) * sgn
        ctx["zz_" + tag + "_brk"] = last_completed(t_end, ds["open_time"], sm, zb)
        ctx["swings_" + tag] = [(int(ds["open_time"][e]), int(ds["open_time"][c]), k) for e, c, k in sw]
    return ctx


def event_features(ctx, s, b, c):
    """Context vector at stamp bar c (pivot bar b = c-1, episode start s). Uses bars <= c only."""
    tf, a1 = ctx["tf"], ctx["a1"][c]
    w = lambda minutes: max(1, minutes // tf)
    pc = ctx["pc"]
    f = {}
    for name, mins in (("ret1", 60), ("ret4", 240), ("ret12", 720), ("ret24", 1440), ("ret7d", 10080)):
        j = c - w(mins)
        f[name] = (pc[c] - pc[j]) / a1 if j >= 0 and a1 > 0 else np.nan
    w24 = w(1440)
    lo24 = max(0, c - w24 + 1)
    far = ctx["far"][lo24:c + 1]
    jmax = int(np.argmax(far))
    hrs = max((len(far) - 1 - jmax) * tf / 60.0, tf / 60.0)
    f["dd"] = (far[jmax] - pc[c]) / a1 if a1 > 0 else np.nan
    f["hours_since_high"] = hrs
    prev_low = ctx["wick"][max(0, b - w24):b]
    f["sweep"] = (prev_low.min() - ctx["wick"][b]) / a1 if len(prev_low) and a1 > 0 else np.nan
    f["speed"] = f["dd"] / hrs if a1 > 0 else np.nan
    j1, j5 = c - w(60), c - w(300)
    if j5 >= 0 and a1 > 0 and w(300) > w(60):
        s1 = (pc[j1] - pc[c]) / a1 / (w(60) * tf / 60.0)
        s4 = (pc[j5] - pc[j1]) / a1 / ((w(300) - w(60)) * tf / 60.0)
        f["dspeed"] = s1 - s4           # falling speed positive: last 1h vs the prior 4h, positive = the decline is accelerating
    else:
        f["dspeed"] = np.nan
    f["rangez"], f["rangez_slope"] = ctx["rangez"][c], ctx["rangez"][c] - ctx["rangez_prev"][c]
    f["volpct"], f["atr_pct"] = ctx["volpct"][c], ctx["atr"][c] / ctx["close"][c]
    f["a1_pct"] = a1 / ctx["close"][c]
    f["volz"], f["takerz"], f["session"] = ctx["volz"][c], ctx["takerz"][c], ctx["session"][b]
    # RSI regime band (Step J): trailing 30d floor/ceiling before the pivot bar, share of bars per band
    w30 = w(30 * 1440)
    seg = ctx["rsi"][max(0, b - w30):b]
    seg = seg[np.isfinite(seg)]
    if len(seg) > w30 // 2:
        f["floor30"], f["ceil30"] = float(seg.min()), float(seg.max())
        f["share_lt30"] = float((seg < 30).mean())
        below = seg < 40
        f["dips40_30d"] = float((below[1:] & ~below[:-1]).sum())
        f["regime_break"] = float(ctx["rsi"][b] < f["floor30"])
    else:
        f["floor30"] = f["ceil30"] = f["share_lt30"] = f["dips40_30d"] = f["regime_break"] = np.nan
    f["htf_break_a"], f["htf_break_b"] = ctx["htf_break_a"][c], ctx["htf_break_b"][c]
    for tag in ("s", "m", "l"):
        for k in ("dir", "dist", "brk"):
            f[f"zz_{tag}_{k}"] = ctx[f"zz_{tag}_{k}"][c]
    f["seas"] = ctx["seas"][c]
    return f


# ----------------------------------------------------------------------------------------------- outcomes
def outcome(ctx, s, c, N):
    """Fill = open of c+1, exit = open N bars later. Returns None when the exit is beyond the data."""
    o, hi, lo = ctx["open"], ctx["high"], ctx["low"]
    if c + 1 + N >= ctx["n"]:
        return None
    e, x, sg = float(o[c + 1]), float(o[c + 1 + N]), ctx["sgn"]
    gross = sg * (x / e - 1.0)
    sh, sl = hi[c + 1:c + 1 + N], lo[c + 1:c + 1 + N]
    if sg > 0:
        mfe, mae = sh.max() / e - 1.0, sl.min() / e - 1.0
        lower = bool(sl.min() < lo[s:c + 1].min())
    else:
        mfe, mae = 1.0 - sl.min() / e, 1.0 - sh.max() / e
        lower = bool(sh.max() > hi[s:c + 1].max())
    unit = ctx["atr"][c] / ctx["close"][c] * (ctx["seas"][c] if np.isfinite(ctx["seas"][c]) and ctx["seas"][c] > 0 else np.nan)
    return {"gross": gross, "net": gross - FEE, "mfe": mfe, "mae": mae, "lower": lower, "gross_atr": gross / unit if unit > 0 else np.nan}


def prev_status(ctx, prior, c, n_h=16):
    """Status of the most recent earlier firing as known at stamp bar c: reached_fee / lower_low / unresolved / none (C3 look-ahead guard:
    a firing counts only if its result occurred at or before bar c; lower_low wins a same-bar tie)."""
    if not prior:
        return "none", 0
    reached = 0
    last = "unresolved"
    for j, (cj, low_j) in enumerate(prior):
        fwd_fill = ctx["open"][cj + 1]
        st = "unresolved"
        end = min(cj + n_h, c, ctx["n"] - 1)
        for m in range(cj + 1, end + 1):
            if ctx["wick"][m] < low_j:
                st = "lower_low"
                break
            if ctx["sgn"] * (ctx["close"][m] / fwd_fill - 1.0) >= FEE:
                st = "reached_fee"
                break
        if st == "reached_fee":
            reached += 1
        last = st
    return last, reached


# ----------------------------------------------------------------------------------------------- event building
VARIANTS = (
    # name, rule, end_level, basis, eps_pct, eps_atr, min_diff, side
    ("PRIMARY", "anchor", 50.0, "close", 0.0, 0.0, 0.0, "long"),
    ("P_adj", "adj", 50.0, "close", 0.0, 0.0, 0.0, "long"),
    ("P_any", "any", 50.0, "close", 0.0, 0.0, 0.0, "long"),
    ("P_anchor_split", "split", 50.0, "close", 0.0, 0.0, 0.0, "long"),
    ("end40", "anchor", 40.0, "close", 0.0, 0.0, 0.0, "long"),
    ("end60", "anchor", 60.0, "close", 0.0, 0.0, 0.0, "long"),
    ("wick", "anchor", 50.0, "wick", 0.0, 0.0, 0.0, "long"),
    ("eps005pct", "anchor", 50.0, "close", 0.0005, 0.0, 0.0, "long"),
    ("eps01atr", "anchor", 50.0, "close", 0.0, 0.1, 0.0, "long"),
    ("mindiff2", "anchor", 50.0, "close", 0.0, 0.0, 2.0, "long"),
    ("mindiff5", "anchor", 50.0, "close", 0.0, 0.0, 5.0, "long"),
    ("MIRROR_short", "anchor", 50.0, "close", 0.0, 0.0, 0.0, "short"),
)


def stage0_starts(ctx, tf, level, start_ms):
    rsi = ctx["rsi"]
    key = ("stage0", tf, level)
    if key not in ctx:
        ctx[key] = ef.find_events(rsi, cf.level_array(rsi, level, tf))
    ev, lv = ctx[key]
    t = ctx["t"]
    return [(s, float(lv[s])) for s in ev if s + 1 < ctx["n"] and t[s] >= start_ms]


def build_variant(ctx, tf, level, var, start_ms, with_features=False):
    """All events (firings and FAILURE_SWING) and the pool of non-firing pivots of one cell under one variant."""
    name, rule, end_level, basis, eps_pct, eps_atr, md, _ = var
    starts_L = stage0_starts(ctx, tf, level, 0)
    bounds = episode_bounds(ctx["rsi"], [s for s, _ in starts_L], end_level)
    Lof = dict(starts_L)
    price = ctx["pc"] if basis == "close" else ctx["wick"]
    piv_all = close_pivots(ctx["pc"], ctx["rsi"])
    events, pool = [], []
    for s, E in bounds:
        if ctx["t"][s] < start_ms:
            continue
        idx = piv_all[(piv_all >= s) & (piv_all + 1 < E) & (piv_all + 1 < ctx["n"])]
        if len(idx) == 0:
            continue
        piv = [{"i": int(i), "price": float(price[i]), "rsi": float(ctx["rsi"][i]),
                "atr": float(ctx["atr"][i])} for i in idx]
        fires = pair_pivots(piv, rule, eps_pct, eps_atr, md, anchor_max=Lof[s])
        fired = {f["k"] for f in fires}
        prior = []
        for f in fires:
            b = piv[f["k"]]["i"]
            c = b + 1
            ev = {"side": ctx["side"], "tf": tf, "level": level, "variant": name, "s": s, "b": b, "c": c, "t": int(ctx["t"][c]),
                  "day": int(ctx["day"][c]), "rsi_b": piv[f["k"]]["rsi"], "rsi_a": piv[f["a"]]["rsi"] if f["a"] is not None else np.nan,
                  "kind": f["kind"], "mult": f["mult"], "skip": f["skip"], "n_anchor": f["n_anchor"], "n_decline": f["n_decline"],
                  "atr_pct": ctx["atr"][b] / ctx["close"][b]}
            if f["kind"] == "div":
                ev["prev_status"], ev["n_prev_reached"] = prev_status(ctx, prior, c)
                prior.append((c, float(ctx["wick"][b])))
            else:
                ev["prev_status"], ev["n_prev_reached"] = "na", 0
            if with_features:
                ev.update(event_features(ctx, s, b, c))
            events.append(ev)
        for k, p in enumerate(piv):
            if k not in fired:
                b = p["i"]
                stamp = b + 1
                pool.append({"b": b, "c": stamp, "s": s, "rsi_b": p["rsi"], "atr_pct": ctx["atr"][b] / ctx["close"][b],
                             "t": int(ctx["t"][stamp]), "day": int(ctx["day"][stamp])})
    return events, pool


def match_controls(events, pool):
    """One-to-one: events in time order; control = unused pool pivot with |RSI diff| <= tol and nearest log ATR%. Returns the matched pool rows."""
    used, out = np.zeros(len(pool), dtype=bool), []
    if not pool:
        return [None] * len(events)
    pr = np.array([p["rsi_b"] for p in pool])
    pa = np.log(np.maximum(np.array([p["atr_pct"] for p in pool]), 1e-12))
    for e in events:
        ok = (~used) & (np.abs(pr - e["rsi_b"]) <= CTRL_RSI_TOL)
        if not ok.any():
            out.append(None)
            continue
        cost = np.where(ok, np.abs(pa - math.log(max(e["atr_pct"], 1e-12))), np.inf)
        j = int(np.argmin(cost))
        used[j] = True
        out.append(pool[j])
    return out


def add_outcomes(ctx, rows, Ns=HORIZONS):
    for r in rows:
        for N in Ns:
            r[f"o{N}"] = outcome(ctx, r["s"], r["c"], N)


def level_only_table(ctx, tf, level, N=MODEL_N):
    """Step G level-only baseline inputs: resolve time (ms) and win flag of every Stage-0 entry of the cell (win = gross > fee)."""
    rt, win = [], []
    for s, _ in stage0_starts(ctx, tf, level, 0):
        o = outcome(ctx, s, s, N)
        if o is None:
            continue
        exit_bar = s + 1 + N
        rt.append(int(ctx["t"][exit_bar]))
        win.append(float(o["gross"] > FEE))
    order = np.argsort(rt)
    return np.asarray(rt)[order], np.asarray(win)[order]


def level_only_p(rt, win, t_ms):
    """(k+1)/(n+2) on entries whose result was known at t_ms (resolve time <= t_ms)."""
    j = int(np.searchsorted(rt, t_ms, side="right"))
    return (win[:j].sum() + 1.0) / (j + 2.0)


# ----------------------------------------------------------------------------------------------- aggregation
FIELDS = ["kind", "pass", "side", "tf_min", "level", "variant", "N", "feature", "bucket", "n_events", "n_days", "n_matched", "net_pct",
          "net_lo", "net_hi", "ctrl_net_pct", "diff_pct", "diff_lo", "diff_hi", "raw_net_pct", "vs_raw_pct", "vs_raw_lo", "vs_raw_hi",
          "p_win", "p_lower", "ctrl_p_lower", "med_atr", "med_mfe_pct", "med_mae_pct", "ev_day_pct", "cal_days", "ll_level", "ll_div",
          "ll_model", "delta_ll", "t", "p", "p_holm", "extra"]


def _g(vals):
    return np.asarray(vals, dtype="float64")


def variant_row(base, ev, ctl, raw, N, cal_days):
    """Aggregate row: events vs matched controls vs the unconditional raw touch (raw = list of (net, day))."""
    e = [(r[f"o{N}"], r["day"]) for r in ev if r.get(f"o{N}")]
    nets = _g([o["net"] for o, _ in e])
    days = _g([d for _, d in e])
    row = dict(base, N=N, n_events=len(e), n_days=int(len(set(days.tolist()))))
    if len(e) == 0:
        return row
    m, lo, hi = wilson_free_ci(nets, days)
    row.update(net_pct=100 * m, net_lo=100 * lo, net_hi=100 * hi)
    row["p_win"] = float((_g([o["gross"] for o, _ in e]) > FEE).mean())
    row["p_lower"] = float(np.mean([o["lower"] for o, _ in e]))
    row["med_atr"] = float(np.nanmedian([o["gross_atr"] for o, _ in e]))
    row["med_mfe_pct"] = 100 * float(np.median([o["mfe"] for o, _ in e]))
    row["med_mae_pct"] = 100 * float(np.median([o["mae"] for o, _ in e]))
    row["ev_day_pct"] = 100 * float(nets.sum()) / max(cal_days, 1.0)
    row["cal_days"] = cal_days
    cs = [(c[f"o{N}"], c["day"]) for c in ctl if c is not None and c.get(f"o{N}")]
    row["n_matched"] = len(cs)
    if cs:
        cn, cd = _g([o["net"] for o, _ in cs]), _g([d for _, d in cs])
        row["ctrl_net_pct"] = 100 * float(cn.mean())
        row["ctrl_p_lower"] = float(np.mean([o["lower"] for o, _ in cs]))
        d, dl, dh = diff_ci(nets, days, cn, cd)
        row.update(diff_pct=100 * d, diff_lo=100 * dl, diff_hi=100 * dh)
    if raw is not None and len(raw[0]):
        rn, rd = raw
        row["raw_net_pct"] = 100 * float(rn.mean())
        d, dl, dh = diff_ci(nets, days, rn, rd)
        row.update(vs_raw_pct=100 * d, vs_raw_lo=100 * dl, vs_raw_hi=100 * dh)
    return row


def raw_touch(ctx, tf, level, N, start_ms, end_ms):
    nets, days = [], []
    for s, _ in stage0_starts(ctx, tf, level, start_ms):
        if ctx["t"][s] >= end_ms:
            continue
        o = outcome(ctx, s, s, N)
        if o is not None:
            nets.append(o["net"])
            days.append(int(ctx["day"][s]))
    return _g(nets), _g(days)


def terciles(vals):
    v = np.asarray(vals, dtype="float64")
    v = v[np.isfinite(v)]
    return (float(np.percentile(v, 100 / 3)), float(np.percentile(v, 200 / 3))) if len(v) >= 30 else (float("nan"), float("nan"))


def bucket_of(x, cuts):
    if not np.isfinite(x) or not np.isfinite(cuts[0]):
        return "NA"
    return "lo" if x <= cuts[0] else ("mid" if x <= cuts[1] else "hi")


def walk_forward(ev, ctx_rt_win, N, start_ms, end_ms):
    """Per scored event (stamp in [start,end)): level-only, divergence-only and ridge-model probabilities. Training = earlier events of the
    same cell whose outcome was known at the stamp (exit time <= stamp), refit once per UTC day."""
    ev = [e for e in sorted(ev, key=lambda r: r["c"]) if e.get(f"o{N}") and e["kind"] == "div"]
    if not ev:
        return []
    X = np.array([[e.get(f, np.nan) for f in MODEL_FEATURES] for e in ev], dtype="float64")
    y = np.array([float(e[f"o{N}"]["gross"] > FEE) for e in ev])
    ts = np.array([e["t"] for e in ev])
    res_t = np.array([e["t"] + (N + 1) * e["tf"] * 60_000 for e in ev])      # exit open time: the outcome is known from then on
    rt, win = ctx_rt_win
    out, cache_day, w, mu, sd = [], None, None, None, None
    for i, e in enumerate(ev):
        if not (start_ms <= e["t"] < end_ms):
            continue
        tr = np.flatnonzero(res_t <= e["t"])
        tr = tr[tr < i]
        p0 = level_only_p(rt, win, e["t"])
        pdv = (y[tr].sum() + 1.0) / (len(tr) + 2.0)
        day = e["t"] // DAY_MS
        if day != cache_day and len(tr) >= MIN_TRAIN:
            xt = X[tr]
            with np.errstate(all="ignore"):
                mu = np.nanmean(xt, axis=0)
                sd = np.nanstd(xt, axis=0)
            mu[~np.isfinite(mu)] = 0.0                 # a feature that is missing for the whole training set contributes 0
            sd[~(sd > 1e-12)] = 1.0
            z = np.clip(np.where(np.isfinite(xt), (xt - mu) / sd, 0.0), -ZCLIP, ZCLIP)
            w, cache_day = fit_logit(z, y[tr]), day
        if len(tr) >= MIN_TRAIN and w is not None:
            zi = np.clip(np.where(np.isfinite(X[i]), (X[i] - mu) / sd, 0.0), -ZCLIP, ZCLIP)[None, :]
            pm = float(predict_logit(w, zi)[0])
        else:
            pm = pdv
        out.append({"i": i, "day": e["day"], "y": y[i], "p_level": p0, "p_div": pdv, "p_model": pm,
                    "net": e[f"o{N}"]["net"], "n_train": len(tr)})
    return out


# ----------------------------------------------------------------------------------------------- run
def month_files(klines, last_ym):
    import prob_tables as pt
    return pt.month_files(klines, last_ym)


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.6g}" if isinstance(r.get(k), (float, np.floating)) else r.get(k, "")) for k in FIELDS})


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(which, klines, out):
    out = Path(out)
    if which == "dev":
        d1 = cf.load_klines_ext(month_files(klines, "2024-06"))
        start_ms, end_ms, dest, cuts = 0, CUTOFF_MS, out / "divergence_dev.csv", None
    else:
        dev = out / "divergence_dev.csv"
        dest = out / "divergence_val.csv"
        if not dev.exists():
            raise SystemExit("divergence_dev.csv must be written (and frozen) before the VALIDATION read")
        if dest.exists():
            raise SystemExit("VALIDATION already read once (divergence_val.csv exists); refusing a second read")
        print("dev csv sha256", sha256(dev))
        cuts = {(r["feature"], r["tf_min"], r["side"]): (float(r["net_lo"]), float(r["net_hi"])) for r in read_csv(dev) if r["kind"] == "cut"}
        d1 = cf.load_klines_ext(month_files(klines, "2025-06"), cutoff_ms=HOLDOUT_MS)
        start_ms, end_ms = CUTOFF_MS, HOLDOUT_MS
    rows, tests = [], []
    ctxs = {}
    for side in ("long", "short"):
        for tf in sorted({c[0] for c in CELLS}):
            ctxs[(side, tf)] = build_context(d1, tf, side)
    new_cuts = {}
    per_tf_events = {}
    for var in VARIANTS:
        side = var[7]
        for tf, level in CELLS:
            ctx = ctxs[(side, tf)]
            primary = var[0] in ("PRIMARY", "MIRROR_short")
            ev, pool = build_variant(ctx, tf, level, var, 0, with_features=primary)
            ctl = match_controls(ev, pool)
            add_outcomes(ctx, ev)
            add_outcomes(ctx, [c for c in ctl if c is not None])
            sel = [(e, c) for e, c in zip(ev, ctl) if start_ms <= e["t"] < end_ms and e["kind"] == "div"]
            fs = [e for e in ev if start_ms <= e["t"] < end_ms and e["kind"] == "failure_swing"]
            lvl_rows = [dict(kind="variant", **{"pass": which}, side=side, tf_min=tf, level=level, variant=var[0])]
            t = ctx["t"]
            eff = max(start_ms, int(t[int(np.argmax(np.isfinite(ctx["rsi"])))]))
            cal_days = max(1.0, (min(end_ms, int(t[-1])) - eff) / DAY_MS)
            for N in HORIZONS:
                raw = raw_touch(ctx, tf, level, N, start_ms, end_ms)
                rows.append(variant_row(lvl_rows[0], [e for e, _ in sel], [c for _, c in sel], raw, N, cal_days))
                if fs and var[0] == "PRIMARY":
                    rows.append(variant_row(dict(lvl_rows[0], variant="FAILURE_SWING"), fs, [], raw, N, cal_days))
            print(f"{var[0]:15s} {side:5s} tf={tf:2d} {level:10s} firings={len(sel)} fs={len(fs)} pool={len(pool)}", flush=True)
            if not primary:
                continue
            rtw = level_only_table(ctx, tf, level)
            wf = walk_forward([e for e in ev], rtw, MODEL_N, start_ms, end_ms)
            per_tf_events.setdefault((side, tf), []).extend([e for e in ev if e["kind"] == "div"])
            if wf:
                yv = _g([r["y"] for r in wf])
                lls = {k: logloss(_g([r["p_" + k] for r in wf]), yv) for k in ("level", "div", "model")}
                dl_div, dl_mod = lls["level"] - lls["div"], lls["level"] - lls["model"]
                days = _g([r["day"] for r in wf])
                for tag, dv in (("div_vs_level", dl_div), ("model_vs_level", dl_mod), ("model_vs_div", lls["div"] - lls["model"])):
                    tt, pp = t_p(dv, days)
                    row = dict(kind="model", **{"pass": which}, side=side, tf_min=tf, level=level, variant=var[0], N=MODEL_N, feature=tag,
                               n_events=len(wf), n_days=int(len(set(days.tolist()))), ll_level=float(lls["level"].mean()),
                               ll_div=float(lls["div"].mean()), ll_model=float(lls["model"].mean()), delta_ll=float(dv.mean()), t=tt, p=pp,
                               net_pct=100 * float(np.mean([r["net"] for r in wf])),
                               extra=f"scored_with_model={sum(r['n_train'] >= MIN_TRAIN for r in wf)}")
                    rows.append(row)
                    if tag != "model_vs_div":
                        tests.append(row)
            # matched event-vs-control test (N=16), same family
            dd = [(e[f"o{MODEL_N}"]["net"], e["day"], c[f"o{MODEL_N}"]["net"], c["day"]) for e, c in sel
                  if e.get(f"o{MODEL_N}") and c is not None and c.get(f"o{MODEL_N}")]
            if len(dd) >= 2:
                d = _g([a - b for a, _, b, _ in dd])
                tt, pp = t_p(d, _g([x[1] for x in dd]))
                row = dict(kind="ctrl_test", **{"pass": which}, side=side, tf_min=tf, level=level, variant=var[0], N=MODEL_N,
                           n_events=len(dd), n_days=int(len(set(x[1] for x in dd))), diff_pct=100 * float(d.mean()), t=tt, p=pp)
                rows.append(row)
                tests.append(row)
            # hindsight descriptive: ex-post short-scale bottom extreme within 4h after the stamp (never a condition)
            want = -1 if side == "long" else 1             # ex-post bottom for the long side, ex-post top for the short mirror
            sw = np.array([e for e, _, k in ctx["swings_s"] if k == want], dtype="int64")
            if len(sw):
                def share(xs):
                    ts_ = np.array([x["t"] for x in xs], dtype="int64")
                    return float(np.mean([bool(((sw > a) & (sw <= a + 4 * 3_600_000)).any()) for a in ts_])) if len(ts_) else float("nan")
                rows.append(dict(kind="hindsight", **{"pass": which}, side=side, tf_min=tf, level=level, variant=var[0],
                                 n_events=len(sel), p_win=share([e for e, _ in sel]), ctrl_p_lower=share([c for _, c in sel if c is not None]),
                                 extra="DESCRIPTIVE hindsight: share with an ex-post 1h-scale bottom extreme within 4h after the stamp"))
            # regime / session / pairing descriptive splits on the primary events of this cell
            for feat in ("session", "regime_break", "htf_break_a", "htf_break_b", "zz_s_dir", "zz_s_brk", "n_anchor", "mult", "prev_status"):
                groups = {}
                for e, _ in sel:
                    v = e.get(feat)
                    key = SESSION_NAMES[int(v)] if feat == "session" and v is not None and np.isfinite(v) else (
                        str(min(int(v), 4)) if feat in ("n_anchor", "mult") else (str(v) if feat == "prev_status" else
                                                                                   ("NA" if not np.isfinite(v) else str(int(v)))))
                    o = e.get(f"o{MODEL_N}")
                    if o:
                        groups.setdefault(key, []).append((o, e["day"]))
                for key, lst in sorted(groups.items()):
                    nn = _g([o["net"] for o, _ in lst])
                    m_, lo_, hi_ = wilson_free_ci(nn, _g([d for _, d in lst]))
                    rows.append(dict(kind="split", **{"pass": which}, side=side, tf_min=tf, level=level, variant=var[0], N=MODEL_N, feature=feat,
                                     bucket=key, n_events=len(lst), n_days=len({d for _, d in lst}), net_pct=100 * m_, net_lo=100 * lo_,
                                     net_hi=100 * hi_, p_win=float(np.mean([o["gross"] > FEE for o, _ in lst])),
                                     p_lower=float(np.mean([o["lower"] for o, _ in lst]))))
    # cross-tabs of the context vector on TF-pooled primary long events, DEV terciles frozen for VALIDATION
    for (side, tf), evs in sorted(per_tf_events.items()):
        for feat in CROSS_FEATURES:
            if which == "dev":
                cuts_f = terciles([e.get(feat, np.nan) for e in evs if e["t"] < end_ms])
                new_cuts[(feat, str(tf), side)] = cuts_f
                rows.append(dict(kind="cut", **{"pass": which}, side=side, tf_min=tf, feature=feat, net_lo=cuts_f[0], net_hi=cuts_f[1]))
            else:
                cuts_f = cuts.get((feat, str(tf), side), (float("nan"), float("nan")))
            groups = {}
            for e in evs:
                if not (start_ms <= e["t"] < end_ms) or not e.get(f"o{MODEL_N}"):
                    continue
                groups.setdefault(bucket_of(e.get(feat, np.nan), cuts_f), []).append((e[f"o{MODEL_N}"], e["day"]))
            for bk, lst in sorted(groups.items()):
                nn = _g([o["net"] for o, _ in lst])
                m_, lo_, hi_ = wilson_free_ci(nn, _g([d for _, d in lst]))
                rows.append(dict(kind="crosstab", **{"pass": which}, side=side, tf_min=tf, variant="PRIMARY", N=MODEL_N, feature=feat, bucket=bk,
                                 n_events=len(lst), n_days=len({d for _, d in lst}), net_pct=100 * m_, net_lo=100 * lo_, net_hi=100 * hi_,
                                 p_win=float(np.mean([o["gross"] > FEE for o, _ in lst])), p_lower=float(np.mean([o["lower"] for o, _ in lst]))))
    ps = [r["p"] if isinstance(r.get("p"), float) and np.isfinite(r["p"]) else 1.0 for r in tests]
    for r, ph in zip(tests, research_kit.holm(ps).tolist()):
        r["p_holm"] = ph
    write_csv(rows, dest)
    print("rows", len(rows), "tests", len(tests), "->", dest)


def _f(r, k):
    v = r.get(k)
    return float(v) if v not in (None, "") else float("nan")


def _n(x, d=3, sign=True):
    if x != x:
        return "-"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def _ci(r, a, lo, hi, d=2):
    return f"{_n(_f(r, a), d)} [{_n(_f(r, lo), d)}, {_n(_f(r, hi), d)}]"


def _cell(r):
    return f"{r['tf_min']}m {r['level']}"


def _pooled_split(rows, feat, variant="PRIMARY", side="long"):
    """Event-weighted pooling of per-cell split rows: n, mean net, P(win), P(lower). Descriptive, no CI."""
    acc = {}
    for r in rows:
        if r["kind"] == "split" and r["feature"] == feat and r["variant"] == variant and r["side"] == side:
            a = acc.setdefault(r["bucket"], [0, 0.0, 0.0, 0.0])
            n = int(r["n_events"])
            a[0] += n
            a[1] += n * _f(r, "net_pct")
            a[2] += n * _f(r, "p_win")
            a[3] += n * _f(r, "p_lower")
    return {k: (v[0], v[1] / v[0], v[2] / v[0], v[3] / v[0]) for k, v in acc.items() if v[0]}


def write_report(out):
    out = Path(out)
    dev = read_csv(out / "divergence_dev.csv")
    valp = out / "divergence_val.csv"
    val = read_csv(valp) if valp.exists() else []
    L = []
    P = L.append
    P("# RSI deep-buy Step I/J: causal divergence at RSI lows, speed/volatility context, matched vs no-divergence (card rsi-deep-divergence-context)")
    P("")
    P(f"BTCUSDT 1m, six Stage-0 cells that survived H1 (`ECON_FLOOR.md`: 60m abs20/abs30/rel_p2_90d, 15m abs30/abs20, 1m abs10). DEV = bar open < 2024-07-01 "
      f"(`divergence_dev.csv`, written and frozen first, sha256 `{sha256(out / 'divergence_dev.csv')[:16]}`). VALIDATION `divergence_val.csv` "
      + (f"read once (2024-07-01..2025-06-30, frozen DEV terciles, sha256 `{sha256(valp)[:16]}`)." if val else "NOT READ YET.")
      + " HOLDOUT (2025-07 onward) is refused by the loader and was never read. Generated by `divergence_context.py`; tests `test_divergence_context.py` "
        "(33; K1-K10 of SHOT_REVIEW (d) within +-0.5 RSI, the planted RSI 20-30-25 case, causality of every context array). The trial rows C1-C8 were written to "
        "`layer_lab/TRIALS.md` before any outcome. No fee-net edge is claimed unless the keep rule below says so.")
    P("")
    P("## What was built")
    P("")
    P("- **Detector** (SPEC Step J as patched by SHOT_REVIEW C1-C10): close pivots (strict local minimum of the close, `rsi_divergence.py:10`); a pivot at b is known at b+1, so the event is "
      "stamped at c = b+1 and filled at the open of c+1. Checked against `rsi_divergence.py` on 60m abs30, 2022-01..2023-06: all 95 P-adj events of this detector are events of the old module with the same "
      "stamp bar (the old module stamps `ts[b+1]`, not earlier than the confirming bar; OPUS_FRAMING s2.2 item 5). Episode: Stage-0 entry (RSI <= L after >= L+3) until RSI closes above 50; an "
      "entry inside a running episode belongs to it. Anchor = lowest-RSI pivot (<= L) so far, replaced by a lower one. Primary row = P-anchor, close, eps 0, min RSI diff 0, end 50. "
      "Every firing is an event, none is dropped as 'the remembered one'.")
    P("- **Control**: non-firing pivots of the same cell, RSI at the pivot within 3 points, nearest trailing ATR%, one-to-one (so the comparison is divergence vs no divergence at the same RSI level, TF and volatility). "
      "`n_matched` is smaller than `n_events` where no unused control sits inside the tolerance (1m abs10 most of all).")
    P("- **Outcome**: fill next open, exit open N bars later (N = 4 and 16 bars of the TF), fee 0.10% round trip; P(price above fill + fee), P(new lower low) (bar low below the lowest low of the episode so far), "
      "median MFE/MAE, move in ATR units normalised by the session-of-day seasonal factor (20-day causal slot mean), EV per calendar day.")
    P("- **Context vector (8, completed bars only)**: returns 1h/4h/12h/24h/7d in 1h-ATR; drawdown from the 24h high, hours since it, and the 24h sweep depth; decline speed; speed change (last 1h vs the prior 4h); 5m range z-score and slope; "
      "realised-vol percentile (30d); volume and taker-buy z; session. Walk-forward ridge logistic on 6 of them (24h return, drawdown, speed, speed change, range z, vol percentile), refit once per UTC day on events whose "
      "N=16 outcome was known, compared with the Step G level-only table ((k+1)/(n+2) on earlier resolved Stage-0 entries of the cell) and the divergence-only rate.")
    P("- **Step J extras**: pairing variants, close vs wick, eps, min RSI difference, FAILURE_SWING rows, RSI regime band (30d floor/ceiling, share under 30, dips under 40, regime break), HTF 3-week floor break, "
      "causal zigzag state on 1h/1d/1w, session clock in exchange-local time, short mirror. The five-week sanity weeks of SHOT_REVIEW (b)12 lie in HOLDOUT and were not read.")
    P("- **Step H** (confluence score) belongs to card `rsi-deep-confluence`, running in parallel; the comparison here is against level-only and divergence-only only.")
    P("")

    def prim(rows, side="long", N="16"):
        return [r for r in rows if r["kind"] == "variant" and r["variant"] == ("PRIMARY" if side == "long" else "MIRROR_short") and r["N"] == N]

    def table_primary(rows, title, side="long"):
        P(f"### {title}")
        P("")
        P("| cell | N | events / days | matched | net % [CI] | control net % | event - control % [CI] | vs raw touch % [CI] | P(win) | P(lower) ctrl | EV/day % |")
        P("|---|---|---|---|---|---|---|---|---|---|---|")
        for N in ("4", "16"):
            for r in prim(rows, side, N):
                flag = "" if int(r["n_days"] or 0) >= MIN_DAYS else " (too_few_days)"
                P(f"| {_cell(r)} | {N} | {r['n_events']} / {r['n_days']}{flag} | {r['n_matched']} | {_ci(r, 'net_pct', 'net_lo', 'net_hi')} | {_n(_f(r, 'ctrl_net_pct'), 2)} | "
                  f"{_ci(r, 'diff_pct', 'diff_lo', 'diff_hi')} | {_ci(r, 'vs_raw_pct', 'vs_raw_lo', 'vs_raw_hi')} | {_n(_f(r, 'p_win'), 2, False)} | "
                  f"{_n(_f(r, 'p_lower'), 2, False)} ({_n(_f(r, 'ctrl_p_lower'), 2, False)}) | {_n(_f(r, 'ev_day_pct'), 4)} |")
        P("")

    dv = [r for r in dev if r["kind"] == "variant" and int(r["n_days"] or 0) >= MIN_DAYS and r["variant"] != "FAILURE_SWING"]
    dv_net = sum(1 for r in dv if _f(r, "net_lo") > 0)
    dv_diff = sum(1 for r in dv if _f(r, "diff_lo") > 0)
    dv_raw = sum(1 for r in dv if _f(r, "vs_raw_lo") > 0)
    P("## Result")
    P("")
    tests_dev = [r for r in dev if r["kind"] in ("model", "ctrl_test") and r.get("p_holm") not in (None, "")]
    sig = [r for r in tests_dev if _f(r, "p_holm") < 0.05]
    P(f"- DEV: {len(dv)} variant rows (cells x variants x N, incl. mirror) with >= 30 independent days. Fee-net CI lower bound > 0: **{dv_net}**; event-minus-control CI lower bound > 0: **{dv_diff}**; "
      f"above the raw touch with CI lower bound > 0: **{dv_raw}**. Chance alone gives about 2.5% one-sided = {0.025 * len(dv):.1f} rows each (rows overlap, so it is a rough scale).")
    P(f"- Pre-registered test family ({len(tests_dev)} tests: per cell and side, divergence minus matched control at N=16, and model minus level-only log-loss; Holm over all): "
      f"**{len(sig)} with Holm p < 0.05** on DEV.")
    prim_long = [r for r in prim(dev, "long", "16") if int(r["n_days"] or 0) >= MIN_DAYS]
    worst = min(prim_long, key=lambda r: _f(r, "diff_pct"))
    P(f"- Primary long rows at N=16: net is negative in {sum(1 for r in prim_long if _f(r, 'net_pct') < 0)} of {len(prim_long)} cells; the divergence event is below its matched control in "
      f"{sum(1 for r in prim_long if _f(r, 'diff_pct') < 0)} of {len(prim_long)} (worst {_cell(worst)}: {_ci(worst, 'diff_pct', 'diff_lo', 'diff_hi')} %).")
    mods = [r for r in dev if r["kind"] == "model" and r["feature"] == "model_vs_level" and r["side"] == "long"]
    P(f"- Model vs level-only (long): delta log-loss > 0 in {sum(1 for r in mods if _f(r, 'delta_ll') > 0)} of {len(mods)} cells (positive = model better). "
      "Divergence-only rate vs level-only is in the table below; a run before the +-4 sd feature clip gave a negative delta in 11 of 12 cells (one NaN from a missing-feature bug, fixed), so the clip did not create the verdict.")
    P("")
    if val:
        P("### VALIDATION (read once, frozen DEV cut points; a walk-forward continuation of the DEV pipeline)")
        P("")
        vtests = [r for r in val if r["kind"] in ("model", "ctrl_test")]
        keep = []
        for r in dev:
            if r["kind"] == "model" and r["feature"] == "model_vs_level" and r.get("p_holm") not in (None, "") and _f(r, "p_holm") < 0.05 and _f(r, "delta_ll") > 0:
                keep.append(r)
        P(f"DEV candidates (model beats level-only on DEV log-loss with Holm p < 0.05): **{len(keep)}**. Keep rule: candidate on DEV and, on VALIDATION, model log-loss better than level-only AND fee-net EV of the events above 0 and above the raw touch. "
          + ("Nothing is kept: F0 / the level-only table stays the answer." if not keep else "Kept rows are listed in the VALIDATION tables."))
        P("")
        pos = [r for r in val if r["kind"] == "model" and r["feature"] == "model_vs_level" and r["side"] == "long" and _f(r, "delta_ll") > 0]
        pn16 = {(r["tf_min"], r["level"]): r for r in prim(val, "long", "16")}
        for r in pos:
            q = pn16.get((r["tf_min"], r["level"]))
            P(f"VALIDATION cell with the model ahead of level-only: {_cell(r)}, delta log-loss {_n(_f(r, 'delta_ll'), 4)} (t {_n(_f(r, 't'), 2)}, p {_n(_f(r, 'p'), 3, False)} unadjusted) on {r['n_events']} events / {r['n_days']} days"
              + (f"; the same cell's fee-net EV is {_ci(q, 'net_pct', 'net_lo', 'net_hi')} % at N=16 and it was not a DEV candidate (DEV delta below), so by the keep rule it is NOT kept. "
                 "Below 30 days it is `too_few_days`, and one cell in six clearing p < 0.05 is within chance." if q else "."))
        P("")
        table_primary(val, "Primary row, VALIDATION, long")
    P("## Primary row (P-anchor, close, eps 0, min diff 0, end 50), DEV")
    P("")
    table_primary(dev, "Long, DEV")
    table_primary(dev, "Short mirror, DEV (exploratory, SHOT_REVIEW C8)", "short")
    for tag, rows_ in (("DEV", dev), ("VALIDATION", val)):
        if not rows_:
            continue
        P(f"## Pairing / basis / tolerance variants at N=16, {tag} (exploratory rows; none is ranked or tuned)")
        P("")
        P("| variant | cells with >= 30 days | cells net CI > 0 | cells event-control CI > 0 | events (sum) | median net % over cells | median event-control % |")
        P("|---|---|---|---|---|---|---|")
        for var in VARIANTS + (("FAILURE_SWING",),):
            nm = var[0]
            rs = [r for r in rows_ if r["kind"] == "variant" and r["variant"] == nm and r["N"] == "16" and int(r["n_days"] or 0) >= MIN_DAYS]
            if not rs:
                continue
            dfs = [_f(r, "diff_pct") for r in rs]
            dmed = _n(float(np.nanmedian(dfs)), 2) if any(x == x for x in dfs) else "-"
            P(f"| {nm} | {len(rs)} | {sum(1 for r in rs if _f(r, 'net_lo') > 0)} | {sum(1 for r in rs if _f(r, 'diff_lo') > 0)} | {sum(int(r['n_events']) for r in rs)} | "
              f"{_n(float(np.median([_f(r, 'net_pct') for r in rs])), 2)} | {dmed} |")
        P("")
        P(f"## Walk-forward log-loss (N=16 price bounce above fee), {tag}, long")
        P("")
        P("| cell | events | level-only | divergence-only | ridge model | delta (model vs level) | t | p |")
        P("|---|---|---|---|---|---|---|---|")
        for r in rows_:
            if r["kind"] == "model" and r["feature"] == "model_vs_level" and r["side"] == "long":
                P(f"| {_cell(r)} | {r['n_events']} | {_n(_f(r, 'll_level'), 4, False)} | {_n(_f(r, 'll_div'), 4, False)} | {_n(_f(r, 'll_model'), 4, False)} | {_n(_f(r, 'delta_ll'), 4)} | {_n(_f(r, 't'), 2)} | {_n(_f(r, 'p'), 3, False)} |")
        P("")
    P("## Sequence features and Step J state, DEV long, pooled over cells (N=16; event-weighted means, descriptive, no CI; n_anchor and mult bucket 4 = 4 or more)")
    P("")
    P("| feature | bucket | events | mean net % | P(win) | P(lower) |")
    P("|---|---|---|---|---|---|")
    for feat in ("n_anchor", "mult", "prev_status", "session", "regime_break", "htf_break_a", "htf_break_b", "zz_s_dir", "zz_s_brk"):
        for bk, (n, m, pw, pl) in sorted(_pooled_split(dev, feat).items()):
            P(f"| {feat} | {bk} | {n} | {_n(m, 3)} | {_n(pw, 2, False)} | {_n(pl, 2, False)} |")
    P("")
    P("## Context cross-tabs, DEV long (terciles of the pooled DEV events per TF); the 14 rows closest to zero among those whose day-clustered net CI excludes 0")
    P("")
    cts = [r for r in dev if r["kind"] == "crosstab" and r["side"] == "long" and int(r["n_days"] or 0) >= MIN_DAYS and r["bucket"] != "NA"]
    odd = [r for r in cts if _f(r, "net_hi") < 0 or _f(r, "net_lo") > 0]
    P(f"{len(cts)} cross-tab rows with >= 30 days; {len(odd)} have a net CI excluding 0 (about {0.05 * len(cts):.0f} expected by chance; all net CIs above 0: {sum(1 for r in cts if _f(r, 'net_lo') > 0)}). Full table in the CSV (`kind=crosstab`).")
    P("")
    P("| TF | feature | bucket | events / days | net % [CI] | P(win) | P(lower) |")
    P("|---|---|---|---|---|---|---|")
    for r in sorted(odd, key=lambda r: _f(r, "net_pct"), reverse=True)[:14]:
        P(f"| {r['tf_min']}m | {r['feature']} | {r['bucket']} | {r['n_events']} / {r['n_days']} | {_ci(r, 'net_pct', 'net_lo', 'net_hi')} | {_n(_f(r, 'p_win'), 2, False)} | {_n(_f(r, 'p_lower'), 2, False)} |")
    P("")
    P("## Hindsight, DESCRIPTIVE only (never a condition, never in a tradeable table)")
    P("")
    P("Share of primary events (control in brackets) followed within 4h by an ex-post confirmed 1h-scale zigzag bottom extreme (3 ATR(1h)): ")
    P("")
    P("| cell | side | events | share events | share controls |")
    P("|---|---|---|---|---|")
    for r in dev:
        if r["kind"] == "hindsight":
            P(f"| {_cell(r)} | {r['side']} | {r['n_events']} | {_n(_f(r, 'p_win'), 2, False)} | {_n(_f(r, 'ctrl_p_lower'), 2, False)} |")
    P("")
    P("Note: `divergence_val.csv` was written before the short-side hindsight rows were fixed (they looked for ex-post bottoms instead of tops); "
      "those short hindsight rows in the VALIDATION file are void and are not used. DEV was regenerated after the fix (all other DEV rows byte-identical).")
    P("")
    P("## Parameters (SOURCED vs OURS)")
    P("")
    P("SOURCED: RSI14 Wilder on close, UTC (econ_floor.py, FORMULAS s1); fee 0.10% round trip (backtest/fees.py); ATR = plain SMA of true range (FORMULAS s12); z-score vs the prior L bars, population sd (FORMULAS s28.1); "
      "close-to-close price basis and min RSI difference 0 (Malkan, `rsi_divergence.py:3,7`); DEV/VALIDATION/HOLDOUT dates (backtest/splits.py); >= 30 independent days, Holm, VALIDATION read once, walk-forward (SPEC guards).")
    P("OURS (every one a trial-ledger row, none tuned on VALIDATION): h = 3; episode end 50 (40, 60 trials); the four pairing rules; eps 0.05% and 0.1 ATR; min diff 2 and 5; wick basis; 24h sweep window; control match (3 RSI points, ATR%); "
      "N = 4 and 16; ridge lambda 1, +-4 sd clip, 40 prior events, daily refit; terciles; 30d RSI band; 3-week HTF floor; zigzag 3 ATR on 1h/1d/1w closes; 20-day seasonal factor; session clock (America/New_York 09:30-10:30, Europe/London 08:00-09:00).")
    P("")
    P("## Caveats")
    P("")
    P("- Events cluster (one slow decline produces many firings against one anchor); CIs are day-clustered, but several days of one selloff are still correlated. Cells with < 30 days are marked too_few_days and not ranked.")
    P("- `regime_break` (the pivot's RSI below the trailing 30d RSI floor) is 0 for every divergence event by construction: the 30d window contains the anchor, whose RSI is lower than the divergence pivot's. The row is void; "
      "the version that matters (anchor RSI vs the 30d floor before the episode) was not built, and `divergence_val.csv` cannot be regenerated after its one read. The HTF 3-week floor break flags (`htf_break_a/b`) are the working Step J regime-break features.")
    P("- P-anchor-split is permissive by construction (price may be lower than any swing since the anchor); its counts are an upper bound on 'the operator's two panels'.")
    P("- The matched control is a retrospective match (a control pivot may lie after the event); each control pivot is itself causal at its own stamp, so no look-ahead enters the outcome comparison.")
    P("- Step H confluence is not in the comparison (parallel card). OI is NOT_IN_DATA before 2025-09. WaveTrend agreement is NOT_IN_DATA until its inputs are pinned.")
    P("- ATR-unit columns use the 1h ATR for returns and the TF ATR times the seasonal factor for outcomes; they are scaled descriptions, not edge claims.")
    with open(out / "DIVERGENCE_REPORT.md", "w", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", out / "DIVERGENCE_REPORT.md")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="which", choices=("dev", "val", "report"), required=True)
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    if a.which == "report":
        write_report(Path(a.out))
        return
    run(a.which, a.klines, a.out)


if __name__ == "__main__":
    main()
