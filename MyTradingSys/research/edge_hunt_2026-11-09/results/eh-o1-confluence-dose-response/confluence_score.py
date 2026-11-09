"""T13 operator-confluence dose-response at level touches (eh-o1-confluence-dose-response).

Rules: PRE_REG.md (frozen). Modes:
  python confluence_score.py count   DEV events, score distribution, regime mix (no returns)
  python confluence_score.py dev     DEV returns, slope test, DEV screen, score_cells.csv
  python confluence_score.py val     VALIDATION once (refuses unless the DEV screen passed)
Cache (outside the repo): F:/MTS/Dumps/backtest/spot_2017 (spot 1h/4h klines),
F:/MTS/Dumps/backtest/eh_s3_conf/fund/fundingRate (USD-M fundingRate archive, 2020-01..2025-06).
"""
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest import fees  # noqa: E402  (single cost module)
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402  (the only Wilder RSI)

H = 3600000
DAY = 86400000
WEEK = 7 * DAY
MONDAY_OFFSET = 4 * DAY          # 1970-01-05 (day 4) is a Monday
TF_MS = {"1h": H, "4h": 4 * H, "12h": 12 * H, "1d": DAY}

FEE_RT = round(2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13, 12)   # regime A: 2 x 5 bps taker + 2 bps RT (FORMULAS s13) = 0.0012
LVL_TOL = 0.003      # OURS (brief): within 0.3 % of the level
PIV_LVL = 5          # OURS (brief): swing pivot 5 each side
COOLDOWN = 24        # OURS (brief): one event per level per 24 bars
PIV_DIV = 3          # eh-s1 layer 2: pivot 3
DIV_MIN, DIV_MAX = 3, 20    # eh-s1 layer 2: 3..20 bars (20 OURS there)
DIV_RECENT = 6       # PRE_REG fill 8: later pivot confirmed within the last 6 bars
ARM = 6              # eh-h5: armed within the last 6 closed bars (OURS there)
LINE_SHORT, LINE_LONG = 60.0, 40.0   # SOURCED malkan_40_60.py MLK-R1
CUSHION = 2.0        # eh-s3: +-2 (OURS there)
STOP_LB = 6          # OURS (brief): extreme of the last 6 bars
TARGET_R = 2.5       # OURS (brief)
HOLD = 30            # OURS (brief)
Z95 = 1.959963984540054
Z_MDE = 2.8016       # z(0.975) + z(0.80)
HOLM_STRICT = 0.05 / 15

SPOT = Path("F:/MTS/Dumps/backtest/spot_2017")
FUND_DIRS = [Path("F:/MTS/Dumps/backtest/eh_o1_conf/fundingRate"), Path("F:/MTS/Dumps/backtest/eh_s3_conf/fund/fundingRate")]
OUT = Path(__file__).resolve().parent
SYMBOLS = ("BTCUSDT", "ETHUSDT")
TRADE_TFS = ("1h", "4h")
LAYERS = ("s1", "s2", "s3", "s4", "s5")


def ms(s):
    return int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


DATA_START = "2017-08"
SPLIT_END = {"DEV": ms("2024-07-01"), "VAL": ms("2025-07-01")}   # exclusive; bar OPEN times must be below
VAL_START = ms("2024-07-01")


class SplitViolation(Exception):
    pass


# ---------------------------------------------------------------- loading
def check_month(split, ym):
    if split not in SPLIT_END:
        raise SplitViolation("split %r is never loaded (HOLDOUT sealed)" % (split,))
    if ms(ym + "-01") >= SPLIT_END[split]:
        raise SplitViolation("%s: month %s is past the split end" % (split, ym))


def months_for(split, start=DATA_START):
    out = []
    y, m = int(start[:4]), int(start[5:])
    while ms("%04d-%02d-01" % (y, m)) < SPLIT_END[split]:
        out.append("%04d-%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def clip_rows(rows, split):
    end = SPLIT_END[split]
    return [r for r in rows if r[0] < end]


def load_klines(sym, tf, split):
    rows = []
    for ym in months_for(split):
        check_month(split, ym)
        p = SPOT / sym / tf / "klines" / ("%s-%s-%s.csv" % (sym, tf, ym))
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as f:
            for r in csv.reader(f):
                if not r or not r[0].strip().isdigit():
                    continue
                t = int(r[0])
                if t > 10 ** 14:          # spot archive switched to microseconds in 2025
                    t //= 1000
                rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4])))
    rows = sorted(set(clip_rows(rows, split)))
    a = np.asarray(rows, dtype=float)
    b = {"t": a[:, 0].astype(np.int64), "o": a[:, 1], "h": a[:, 2], "l": a[:, 3], "c": a[:, 4], "tf": TF_MS[tf]}
    assert b["t"][-1] < SPLIT_END[split]
    return b


def load_funding(sym, split):
    rows = []
    for ym in months_for(split, "2020-01"):
        check_month(split, ym)
        for d in FUND_DIRS:
            p = d / ("%s-fundingRate-%s.csv" % (sym, ym))
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for r in csv.reader(f):
                        if r and r[0].strip().isdigit():
                            rows.append((int(r[0]), float(r[2])))
                break
    rows = sorted(set(r for r in rows if r[0] < SPLIT_END[split]))
    if not rows:
        return np.zeros(0, dtype=np.int64), np.zeros(0)
    a = np.asarray(rows, dtype=float)
    return a[:, 0].astype(np.int64), a[:, 1]


# ---------------------------------------------------------------- indicators
def rsi(closes, n=14):
    if len(closes) <= n:
        return np.full(len(closes), np.nan)
    return np.array([np.nan if v is None else v for v in rsi_core([float(x) for x in closes], n)])


def sma(x, n):
    out = np.full(len(x), np.nan)
    for k in range(n - 1, len(x)):
        w = x[k - n + 1:k + 1]
        if not np.isnan(w).any():
            out[k] = w.mean()
    return out


def pivots(h, l, k):
    """Swing high at j: high[j] > highs j-k..j-1 and >= highs j+1..j+k (mirror for lows). Needs k right bars."""
    n = len(h)
    ph = np.zeros(n, dtype=bool)
    pl = np.zeros(n, dtype=bool)
    for j in range(k, n - k):
        if h[j] > h[j - k:j].max() and h[j] >= h[j + 1:j + k + 1].max():
            ph[j] = True
        if l[j] < l[j - k:j].min() and l[j] <= l[j + 1:j + k + 1].min():
            pl[j] = True
    return ph, pl


def resample_close(t_open, c, base_ms, period, offset=0):
    """Closes of `period` bars built from base bars (open times t_open). Returns (close_time, close).
    A period bar's close time is its period end; it is usable only at or after that time (asof)."""
    key = (t_open - offset) // period
    last = np.r_[key[1:] != key[:-1], True]
    return (key[last] * period + offset + period).astype(np.int64), c[last].astype(float)


def asof(close_t, vals, T):
    idx = np.searchsorted(close_t, T, side="right") - 1
    out = np.where(idx >= 0, vals[np.clip(idx, 0, None)], np.nan)
    return out


def asof_pair(close_t, vals, T):
    """(previous, last) closed values as of T."""
    idx = np.searchsorted(close_t, T, side="right") - 1
    last = np.where(idx >= 0, vals[np.clip(idx, 0, None)], np.nan)
    prev = np.where(idx >= 1, vals[np.clip(idx - 1, 0, None)], np.nan)
    return prev, last


# ---------------------------------------------------------------- events
def find_events(b):
    """Level touches. Returns dicts {i, side (-1 short at highs, +1 long at lows), level, pivot}."""
    h, l, c = b["h"], b["l"], b["c"]
    n = len(c)
    ph, pl = pivots(h, l, PIV_LVL)
    live = {-1: [], 1: []}     # [level, pivot j, last_event_i]
    out = []
    for i in range(n):
        j = i - PIV_LVL - 1    # pivot confirmed at j+5 = i-1, usable from i = j+6
        if j >= 0:
            if ph[j]:
                live[-1].append([h[j], j, -10 ** 9])
            if pl[j]:
                live[1].append([l[j], j, -10 ** 9])
        for side in (-1, 1):
            keep, cand = [], []
            for lv in live[side]:
                L = lv[0]
                if (side == -1 and c[i] > L) or (side == 1 and c[i] < L):
                    continue                          # broken by a close: dead, no event
                keep.append(lv)
                touch = h[i] >= L * (1 - LVL_TOL) if side == -1 else l[i] <= L * (1 + LVL_TOL)
                if touch and i - lv[2] >= COOLDOWN:
                    cand.append(lv)
            live[side] = keep
            if cand:
                ext = h[i] if side == -1 else l[i]
                best = min(cand, key=lambda v: (abs(ext - v[0]), -v[1]))
                for lv in cand:
                    lv[2] = i
                out.append({"i": i, "side": side, "level": float(best[0]), "pivot": int(best[1])})
    return out


# ---------------------------------------------------------------- layers
def s1_sweep(b, i, side, L):
    if side == -1:
        return bool(b["h"][i] > L and b["c"][i] < L)
    return bool(b["l"][i] < L and b["c"][i] > L)


def _near(x, line):
    return (not math.isnan(x)) and abs(x - line) <= CUSHION


def s2_flag(rsi_trade, rsi_others, side):
    line = LINE_SHORT if side == -1 else LINE_LONG
    return bool(_near(rsi_trade, line) and any(_near(x, line) for x in rsi_others))


def s3_divergence(h, l, c, r, ph3, pl3, i, side):
    """eh-s1 layer 2 divergence: two confirmed pivot-3 swings 3..20 bars apart, later one beyond on wick OR close,
    RSI weaker at the later one. Later pivot confirmed by bar i and within the last DIV_RECENT bars."""
    piv = ph3 if side == -1 else pl3
    lo2 = max(i - DIV_RECENT - PIV_DIV, 0)
    for p2 in range(i - PIV_DIV, lo2 - 1, -1):
        if p2 < 0 or not piv[p2]:
            continue
        for p1 in range(p2 - DIV_MIN, max(p2 - DIV_MAX, 0) - 1, -1):
            if not piv[p1]:
                continue
            if math.isnan(r[p1]) or math.isnan(r[p2]):
                continue
            if side == -1:
                if (h[p2] > h[p1] or c[p2] > c[p1]) and r[p2] < r[p1]:
                    return True
            else:
                if (l[p2] < l[p1] or c[p2] < c[p1]) and r[p2] > r[p1]:
                    return True
    return False


def s4_signals(r, ma, side):
    """eh-h5 signal bar per bar k: armed (>= 60 / <= 40 on bars k-6..k-1), RSI below MA and below 60 (mirror)."""
    n = len(r)
    sig = np.zeros(n, dtype=bool)
    for k in range(1, n):
        w = r[max(0, k - ARM):k]
        if side == -1:
            sig[k] = bool(np.nanmax(w) >= LINE_SHORT if np.isfinite(w).any() else False) and r[k] < ma[k] and r[k] < LINE_SHORT
        else:
            sig[k] = bool(np.nanmin(w) <= LINE_LONG if np.isfinite(w).any() else False) and r[k] > ma[k] and r[k] > LINE_LONG
    return sig


def s4_at(sig, i):
    return bool(sig[i] or (i >= 1 and sig[i - 1]))


def s5_flag(daily, weekly, side):
    """eh-s1 layer 5. daily/weekly = (previous closed RSI, last closed RSI)."""
    dp, dl = daily
    wp, wl = weekly
    if side == -1:
        return bool((dl < LINE_SHORT and dl < dp) or (wp >= LINE_SHORT and wl < LINE_SHORT))
    return bool((dl > LINE_LONG and dl > dp) or (wp <= LINE_LONG and wl > LINE_LONG))


# ---------------------------------------------------------------- trade
def simulate(b, i, side, L, fund):
    t, h, l, c = b["t"], b["h"], b["l"], b["c"]
    n = len(c)
    if i + HOLD >= n:
        return None
    lo = max(0, i - STOP_LB + 1)
    entry = float(c[i])
    if side == -1:
        stop = max(float(h[lo:i + 1].max()), L)
        sd = stop - entry
    else:
        stop = min(float(l[lo:i + 1].min()), L)
        sd = entry - stop
    if sd <= 0:
        return {"skip": True}
    tgt = entry + side * TARGET_R * sd
    kind, px, k_exit = None, None, None
    for k in range(i + 1, i + HOLD + 1):
        hit_stop = h[k] >= stop if side == -1 else l[k] <= stop
        hit_tgt = l[k] <= tgt if side == -1 else h[k] >= tgt
        if hit_stop:
            kind, px, k_exit = "stop", stop, k
            break
        if hit_tgt:
            kind, px, k_exit = "target", tgt, k
            break
    if kind is None:
        kind, px, k_exit = "time", float(c[i + HOLD]), i + HOLD
    stop_frac = sd / entry
    gross = side * (px - entry) / sd
    fee = FEE_RT / stop_frac
    fund_r = 0.0
    if fund is not None and len(fund[0]):
        ft, fr = fund
        te, tx = int(t[i]) + b["tf"], int(t[k_exit]) + b["tf"]
        m = (ft > te) & (ft <= tx)
        fund_r = side * float(fr[m].sum()) / stop_frac
    return {"skip": False, "stop": stop, "stop_frac": stop_frac, "exit_kind": kind, "gross": gross,
            "fee": fee, "fund": fund_r, "net": gross - fee - fund_r, "bars_held": k_exit - i}


# ---------------------------------------------------------------- statistics
def ols_cluster(y, x, g):
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    _, inv = np.unique(g, return_inverse=True)
    G = inv.max() + 1
    S = np.zeros((G, 2))
    np.add.at(S, inv, X * u[:, None])
    meat = S.T @ S
    corr = (G / (G - 1)) * ((n - 1) / (n - 2)) if G > 1 and n > 2 else 1.0
    V = corr * XtX_inv @ meat @ XtX_inv
    se = math.sqrt(max(V[1, 1], 0.0))
    slope = float(beta[1])
    p = 0.5 * math.erfc((slope / se) / math.sqrt(2)) if se > 0 else float("nan")
    return {"n": n, "clusters": int(G), "intercept": float(beta[0]), "slope": slope, "se": se,
            "ci_lo": slope - Z95 * se, "ci_hi": slope + Z95 * se, "p_one": p, "mde": Z_MDE * se}


def cluster_mean(v, g):
    v = np.asarray(v, float)
    n = len(v)
    if n == 0:
        return {"n": 0}
    m = float(v.mean())
    se = float("nan")
    if n > 1:
        _, inv = np.unique(g, return_inverse=True)
        s = np.bincount(inv, weights=v - m)
        G = len(s)
        se = math.sqrt(float((s ** 2).sum()) * (G / (G - 1) if G > 1 else 1.0)) / n
    return {"n": n, "mean": m, "se": se, "ci_lo": m - Z95 * se, "ci_hi": m + Z95 * se,
            "p_one": 0.5 * math.erfc((m / se) / math.sqrt(2)) if se and se > 0 else float("nan"),
            "mde": Z_MDE * se}


# ---------------------------------------------------------------- pipeline
def symbol_events(sym, split, want_returns):
    b1 = load_klines(sym, "1h", split)
    b4 = load_klines(sym, "4h", split)
    fund = load_funding(sym, split) if want_returns else None
    r1 = rsi(b1["c"])
    r4 = rsi(b4["c"])
    ct12, c12 = resample_close(b1["t"], b1["c"], H, 12 * H)
    ctd, cd = resample_close(b1["t"], b1["c"], H, DAY)
    ctw, cw = resample_close(ctd - DAY, cd, DAY, WEEK, MONDAY_OFFSET)
    r12, rd, rw = rsi(c12), rsi(cd), rsi(cw)
    rsi_tf = {"1h": (b1["t"] + H, r1), "4h": (b4["t"] + 4 * H, r4), "12h": (ct12, r12), "1d": (ctd, rd)}
    rows, cens = [], {"censored": 0, "skip_stop": 0}
    for tf, b in (("1h", b1), ("4h", b4)):
        r = r1 if tf == "1h" else r4
        ma = sma(r, 14)
        sig = {-1: s4_signals(r, ma, -1), 1: s4_signals(r, ma, 1)}
        ph3, pl3 = pivots(b["h"], b["l"], PIV_DIV)
        evs = find_events(b)
        if not evs:
            continue
        T = np.array([int(b["t"][e["i"]]) + b["tf"] for e in evs], dtype=np.int64)
        others = {o: asof(rsi_tf[o][0], rsi_tf[o][1], T) for o in ("1h", "4h", "12h", "1d") if o != tf}
        dp, dl = asof_pair(ctd, rd, T)
        wp, wl = asof_pair(ctw, rw, T)
        for k, e in enumerate(evs):
            i, side, L = e["i"], e["side"], e["level"]
            row = {"sym": sym, "tf": tf, "i": i, "side": side, "level": L, "t": int(b["t"][i]),
                   "day": int(b["t"][i] // DAY), "year": datetime.fromtimestamp(b["t"][i] / 1000, tz=timezone.utc).year}
            row["s1"] = int(s1_sweep(b, i, side, L))
            row["s2"] = int(s2_flag(r[i], [others[o][k] for o in others], side))
            row["s3"] = int(s3_divergence(b["h"], b["l"], b["c"], r, ph3, pl3, i, side))
            row["s4"] = int(s4_at(sig[side], i))
            row["s5"] = int(s5_flag((dp[k], dl[k]), (wp[k], wl[k]), side))
            row["score"] = sum(row[x] for x in LAYERS)
            if want_returns:
                sim = simulate(b, i, side, L, fund)
                if sim is None:
                    cens["censored"] += 1
                    continue
                if sim["skip"]:
                    cens["skip_stop"] += 1
                    continue
                row.update(sim)
            rows.append(row)
    return rows, cens


def all_events(split, want_returns):
    rows, cens = [], {"censored": 0, "skip_stop": 0}
    for s in SYMBOLS:
        r, c = symbol_events(s, split, want_returns)
        rows += r
        for k in cens:
            cens[k] += c[k]
    return rows, cens


def regime_mix_dev():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rk_eh_o1", ROOT / "MyTradingSys" / "backtest" / "research_kit.py")
    rk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rk)
    b1 = load_klines("BTCUSDT", "1h", "DEV")
    ctd, cd = resample_close(b1["t"], b1["c"], H, DAY)
    ctw, cw = resample_close(ctd - DAY, cd, DAY, WEEK, MONDAY_OFFSET)
    mkeys = np.array([int(datetime.fromtimestamp((x - DAY) / 1000, tz=timezone.utc).strftime("%Y%m")) for x in ctd])
    last = np.r_[mkeys[1:] != mkeys[:-1], True]
    mt = []
    for k in mkeys[last]:
        y, m = divmod(int(k), 100)
        mt.append(ms("%04d-%02d-01" % (y + (m == 12), 1 if m == 12 else m + 1)))
    mt = np.array(mt, dtype=np.int64)
    mc = cd[last]
    keepm = mt <= SPLIT_END["DEV"]
    rw, rm = rsi(cw), rsi(mc[keepm])
    wpair = [(int(a), float(v)) for a, v in zip(ctw, rw) if not math.isnan(v)]
    mpair = [(int(a), float(v)) for a, v in zip(mt[keepm], rm) if not math.isnan(v)]
    first_monday = ((int(b1["t"][0]) - MONDAY_OFFSET) // WEEK + 1) * WEEK + MONDAY_OFFSET
    wk = list(range(first_monday, SPLIT_END["DEV"], WEEK))
    tags = rk.weekly_regimes(wk, (list(ctd), list(cd)), ([p[0] for p in wpair], [p[1] for p in wpair]),
                             ([p[0] for p in mpair], [p[1] for p in mpair]))
    return rk.regime_mix_line(tags)


def count_pass():
    rows, _ = all_events("DEV", False)
    out = {"n": len(rows), "score_dist": {}, "by_year_side": {}, "by_tf_sym": {}, "layer_rate": {}}
    for s in range(6):
        out["score_dist"][s] = sum(1 for r in rows if r["score"] == s)
    out["score_ge3"] = sum(1 for r in rows if r["score"] >= 3)
    for r in rows:
        k = "%d %s" % (r["year"], "short" if r["side"] == -1 else "long")
        out["by_year_side"][k] = out["by_year_side"].get(k, 0) + 1
        k2 = "%s %s" % (r["sym"], r["tf"])
        out["by_tf_sym"][k2] = out["by_tf_sym"].get(k2, 0) + 1
    for x in LAYERS:
        out["layer_rate"][x] = round(sum(r[x] for r in rows) / max(len(rows), 1), 4)
    out["regime_mix_dev"] = regime_mix_dev()
    return out


def cell(name, rs):
    if not rs:
        return {"cut": name, "n": 0}
    net = np.array([r["net"] for r in rs])
    g = np.array([r["day"] for r in rs])
    st = cluster_mean(net, g)
    return {"cut": name, "n": len(rs), "hit": round(float((net > 0).mean()), 4),
            "gross": round(float(np.mean([r["gross"] for r in rs])), 4),
            "fee_r": round(float(np.mean([r["fee"] for r in rs])), 4),
            "fund_r": round(float(np.mean([r["fund"] for r in rs])), 4),
            "net": round(st["mean"], 4), "se": round(st["se"], 4), "ci_lo": round(st["ci_lo"], 4),
            "ci_hi": round(st["ci_hi"], 4), "mde": round(st["mde"], 4)}


def slope_of(rs, score_key=None, drop=None):
    y = np.array([r["net"] for r in rs])
    if drop:
        x = np.array([r["score"] - r[drop] for r in rs], float)
    else:
        x = np.array([r["score"] for r in rs], float)
    g = np.array([r["day"] for r in rs])
    return ols_cluster(y, x, g)


def analyse(rows, cens, label):
    prim = slope_of(rows)
    ge3 = [r for r in rows if r["score"] >= 3]
    c3 = cell("score>=3", ge3)
    screen = bool(prim["slope"] > 0 and prim["ci_lo"] > 0 and c3["n"] >= 30 and c3.get("net", -1) > 0)
    cells = [cell("all", rows), c3]
    for s in range(6):
        cells.append(cell("score=%d" % s, [r for r in rows if r["score"] == s]))
    for tf in TRADE_TFS:
        cells.append(cell("tf=%s" % tf, [r for r in rows if r["tf"] == tf]))
    for sd, nm in ((-1, "short"), (1, "long")):
        cells.append(cell("side=%s" % nm, [r for r in rows if r["side"] == sd]))
    for x in LAYERS:
        cells.append(cell("%s=1" % x, [r for r in rows if r[x] == 1]))
        cells.append(cell("%s=0" % x, [r for r in rows if r[x] == 0]))
    for y in sorted(set(r["year"] for r in rows)):
        cells.append(cell("year=%d" % y, [r for r in rows if r["year"] == y]))
    slopes = {"primary": prim}
    for x in LAYERS:
        slopes["drop_" + x] = slope_of(rows, drop=x)
    for tf in TRADE_TFS:
        rs = [r for r in rows if r["tf"] == tf]
        slopes["tf_" + tf] = slope_of(rs)
    for s in SYMBOLS:
        slopes["sym_" + s] = slope_of([r for r in rows if r["sym"] == s])
    for sd, nm in ((-1, "short"), (1, "long")):
        slopes["side_" + nm] = slope_of([r for r in rows if r["side"] == sd])
    for y in sorted(set(r["year"] for r in rows)):
        rs = [r for r in rows if r["year"] == y]
        if len(set(r["score"] for r in rs)) > 1:
            slopes["year_%d" % y] = slope_of(rs)
    exits = {k: sum(1 for r in rows if r["exit_kind"] == k) for k in ("stop", "target", "time")}
    stopq = np.percentile([r["stop_frac"] * 1e4 for r in rows], [10, 50, 90]).round(1).tolist()
    return {"label": label, "screen": screen, "cens": cens, "exits": exits, "stop_bps_p10_50_90": stopq,
            "slopes": slopes, "cells": cells}


def write_cells(res, path):
    keys = ["split", "cut", "n", "hit", "gross", "fee_r", "fund_r", "net", "se", "ci_lo", "ci_hi", "mde"]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(keys)
        for rr in res:
            for c in rr["cells"]:
                w.writerow([rr["label"]] + [c.get(k, "") for k in keys[1:]])
            for name, s in rr["slopes"].items():
                w.writerow([rr["label"], "slope:" + name, s["n"], "", "", "", "", round(s["slope"], 4),
                            round(s["se"], 4), round(s["ci_lo"], 4), round(s["ci_hi"], 4), round(s["mde"], 4)])


def main(mode):
    if mode == "count":
        print(json.dumps(count_pass(), indent=1))
        return
    if mode == "dev":
        rows, cens = all_events("DEV", True)
        res = analyse(rows, cens, "DEV")
        write_cells([res], OUT / "score_cells.csv")
        (OUT / "dev_screen.json").write_text(json.dumps({"screen": res["screen"], "primary": res["slopes"]["primary"]},
                                                        indent=1) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({k: v for k, v in res.items() if k != "cells"}, indent=1, default=str))
        for c in res["cells"]:
            print(c)
        return
    if mode == "val":
        scr = json.loads((OUT / "dev_screen.json").read_text(encoding="utf-8"))
        if not scr["screen"]:
            raise SystemExit("DEV screen failed: VALIDATION is not read")
        rows, cens = all_events("VAL", True)
        rows = [r for r in rows if r["t"] >= VAL_START]
        res = analyse(rows, cens, "VAL")
        p = res["slopes"]["primary"]
        res["holm_pass"] = bool(p["slope"] > 0 and p["p_one"] <= HOLM_STRICT)
        print(json.dumps({k: v for k, v in res.items() if k != "cells"}, indent=1, default=str))
        return
    if mode == "explore":
        # EXPLORATORY only (cannot promote): what drives the primary slope.
        rows, _ = all_events("DEV", True)
        top = sorted(rows, key=lambda r: -r["fee"])[:5]
        print("largest fee_r:", [(r["sym"], r["tf"], datetime.fromtimestamp(r["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H"),
                                  r["score"], round(r["stop_frac"] * 1e4, 3), round(r["fee"], 1)) for r in top])
        g = np.array([r["day"] for r in rows])
        x = np.array([r["score"] for r in rows], float)
        print("gross-R slope:", ols_cluster(np.array([r["gross"] for r in rows]), x, g))
        for lo_bps in (10, 25):
            rs = [r for r in rows if r["stop_frac"] * 1e4 >= lo_bps]
            print("net-R slope, stop >= %d bps:" % lo_bps, slope_of(rs))
            for s in range(6):
                print("  ", cell("score=%d stop>=%d" % (s, lo_bps), [r for r in rs if r["score"] == s]))
        return
    raise SystemExit("mode: count | dev | val | explore")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "count")
