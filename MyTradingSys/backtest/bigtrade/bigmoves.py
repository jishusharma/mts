"""
MyTradingSys/backtest/bigtrade/bigmoves.py - big-move ground truth (big-trade backtest A, PLAN section 3).

What it builds, per timeframe (5m 15m 1h 4h by default):
  legs_<TF>.csv    every swing leg with one 0/1 column per (r, k): flags_r<r>_k<k> = leg exists in the r-zigzag AND size >= k ATR.
  labels_<TF>.csv  per closed bar: close, ATR (Wilder and plain SMA), forward MFE / MAE-before-MFE in ATR for H bars, both sides.
  bigmoves_stats.json  numbers for BIGMOVES_REPORT.md (see report.py).

Conventions (analysis settings, printed in every report; they are not trading parameters):
  * Bars come from the 1m archive via bt_data.load_klines and tf_resample.resample (closed buckets only).
  * ATR = Wilder(14) on the bar's own TF, strictly causal (ATR[i] uses bars <= i). TR[0] is undefined, so ATR is defined from index 14.
    FORMULAS.md section 12 says MTS core uses a plain SMA: atr(kind="sma") is provided so both units exist (finding F-BT-07).
  * Legs are HINDSIGHT by design: an ATR zigzag. A pivot is the extreme bar of a swing; it is confirmed by a later bar whose
    opposite extreme is at least r x ATR[pivot bar] away. The bar that makes the extreme can never confirm its own reversal
    (intrabar order is unknown), a bar that makes a new extreme extends the swing instead of reversing it, equal extremes keep
    the earlier bar, and the final unconfirmed swing is not a leg. Leg size is |p_end - p_start| / ATR[start bar].
  * "N bars either side" of PLAN section 3 is the zigzag condition itself (extreme not exceeded from the previous pivot until a
    reversal of r x ATR). A fixed fractal width is not used because it rejects real short-swing pivots; report.py prints the
    share of pivots that also pass a +-2 bar fractal test.
  * Times in legs_*.csv and labels_*.csv are bar CLOSE times in epoch ms (same convention as fires t_fire_ms): t_start_ms is
    the close of the pivot bar, so a fire on the pivot bar's own close is the earliest possible fire (lead 0 bars).
  * Forward labels for bar j: entry = open of bar j+1 (market, next bar open), window = bars j+1..j+H, unit = ATR[j].
    mfe_long = max(high) - entry; mae_long = entry - min(low) over bars j+1..argmax bar (first bar that makes the max, inclusive);
    short is the mirror. NaN when ATR[j] is undefined or fewer than H bars follow.
"""
import csv
import datetime
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from MyTradingSys.backtest.bt.bt_data import load_klines, check_gaps  # noqa: E402
from MyTradingSys.backtest.layers.timeframe.tf_resample import resample  # noqa: E402

REGISTRY = json.loads((_REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))

TFS = ("5m", "15m", "1h", "4h")
TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000, "4h": 14400000}
R_LIST = (1.5, 2.0)
K_LIST = (3, 5, 8)
H_LIST = (24, 96)
ATR_PERIOD = 14
DATA_DIR = Path(os.environ.get("BIGTRADE_DATA", "F:/MTS/data/bigtrade"))

# Priority order: the first source that has a minute wins (bt_data keeps first inside a source too).
SOURCES = (
    (_REPO / "Dumps/backtest/raw_1m_2022", "klines"),
    (_REPO / "Dumps/backtest/raw", "klines"),
    (Path("F:/MTS/data/tom_raw"), "klines"),
)

LABEL_NAMES = ("mfe_long", "mae_long", "mfe_short", "mae_short")


def iso(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


# ----------------------------------------------------------------------------------------------- loading

def load_1m(sources=SOURCES, start_ms=None, end_ms=None):
    """Merge 1m kline sources (first source wins a duplicated minute). Returns (bars sorted by t, per-source report)."""
    merged = {}
    report = []
    for root, dataset in sources:
        bars = load_klines(root, dataset, start_ms, end_ms)
        n_new = n_dup = n_conflict = 0
        for b in bars:
            old = merged.get(b["t"])
            if old is None:
                merged[b["t"]] = b
                n_new += 1
            else:
                n_dup += 1
                if any(old[k] != b[k] for k in ("o", "h", "l", "c", "v")):
                    n_conflict += 1
        report.append({
            "root": str(root), "dataset": dataset, "n_bars": len(bars),
            "first_ms": bars[0]["t"] if bars else None, "last_ms": bars[-1]["t"] if bars else None,
            "n_new": n_new, "n_duplicate_of_earlier_source": n_dup, "n_conflicting_duplicates": n_conflict,
        })
    out = sorted(merged.values(), key=lambda b: b["t"])
    if out and not (1.0e12 < out[0]["t"] and out[-1]["t"] < 3.0e12):
        raise ValueError("kline open_time is not epoch milliseconds (microsecond archive files?)")
    return out, report


def coverage_1m(bars):
    """Facts about the merged 1m series: span, gaps, zero-volume bars, OHLC inconsistencies."""
    if not bars:
        return {"n_bars": 0}
    gaps = check_gaps(bars)
    zero_vol = [b for b in bars if b["v"] == 0]
    days = {}
    for b in zero_vol:
        d = iso(b["t"])[:10]
        days[d] = days.get(d, 0) + 1
    bad = sum(1 for b in bars if b["h"] < max(b["o"], b["c"], b["l"]) or b["l"] > min(b["o"], b["c"], b["h"])
              or min(b["o"], b["h"], b["l"], b["c"]) <= 0)
    return {
        "n_bars": len(bars), "first_ms": bars[0]["t"], "last_ms": bars[-1]["t"],
        "n_gaps": len(gaps), "missing_minutes": int(sum((b - a) // 60000 - 1 for a, b in gaps)),
        "zero_volume_bars": len(zero_vol), "zero_volume_flat_ohlc": sum(1 for b in zero_vol if b["o"] == b["h"] == b["l"] == b["c"]),
        "zero_volume_days": days, "ohlc_inconsistent": bad,
    }


def resample_bars(bars_1m, tf):
    """Closed TF bars as numpy arrays (tf_resample.resample does the bucketing)."""
    rows = resample(bars_1m, tf, REGISTRY)
    ms = TF_MS[tf]
    t_open = np.array([r["t"] for r in rows], dtype=np.int64)
    return {
        "tf": tf, "t_open": t_open, "t_close": t_open + ms,
        "o": np.array([r["o"] for r in rows], dtype=float), "h": np.array([r["h"] for r in rows], dtype=float),
        "l": np.array([r["l"] for r in rows], dtype=float), "c": np.array([r["c"] for r in rows], dtype=float),
        "v": np.array([r["v"] for r in rows], dtype=float),
        "n_bars": np.array([r["n_bars"] for r in rows], dtype=np.int64),
        "gap_count": np.array([r["gap_count"] for r in rows], dtype=np.int64),
    }


# ----------------------------------------------------------------------------------------------- ATR

def true_range(h, l, c):
    """TR[i] = max(h-l, |h-c[i-1]|, |l-c[i-1]|) for i >= 1; TR[0] is undefined (NaN). FORMULAS.md section 12."""
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    c = np.asarray(c, dtype=float)
    tr = np.full(len(h), np.nan)
    if len(h) > 1:
        pc = c[:-1]
        tr[1:] = np.maximum(np.maximum(h[1:] - l[1:], np.abs(h[1:] - pc)), np.abs(l[1:] - pc))
    return tr


def atr(h, l, c, period=ATR_PERIOD, kind="wilder"):
    """ATR array, NaN before index `period`. wilder: seed = mean(TR[1..period]) at index period, then (prev*(p-1)+TR)/p.
    sma: mean(TR[i-period+1..i]). Strictly causal: value at i uses bars <= i only."""
    tr = true_range(h, l, c)
    n = len(tr)
    out = np.full(n, np.nan)
    if n <= period:
        return out
    if kind == "sma":
        cs = np.concatenate([[0.0], np.cumsum(tr[1:])])  # cs[m] = sum(TR[1..m])
        out[period:] = (cs[period:n] - cs[0:n - period]) / period
    elif kind == "wilder":
        a = float(np.mean(tr[1:period + 1]))
        out[period] = a
        trl = tr.tolist()
        for i in range(period + 1, n):
            a = (a * (period - 1) + trl[i]) / period
            out[i] = a
    else:
        raise ValueError("kind must be wilder or sma")
    return out


# ----------------------------------------------------------------------------------------------- forward labels

def forward_labels(o, h, l, atr_arr, H, chunk=40000):
    """Per bar j: MFE and MAE-before-MFE (ATR units) for a market entry at open[j+1] over bars j+1..j+H. See module docstring."""
    o = np.asarray(o, dtype=float)
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    atr_arr = np.asarray(atr_arr, dtype=float)
    n = len(o)
    out = {name: np.full(n, np.nan) for name in LABEL_NAMES}
    m = n - H  # valid j are 0..m-1 (needs bars j+1..j+H)
    if m <= 0:
        return out
    hw = sliding_window_view(h[1:], H)  # row j = highs of bars j+1..j+H
    lw = sliding_window_view(l[1:], H)
    for s in range(0, m, chunk):
        e = min(m, s + chunk)
        hh = hw[s:e]
        ll = lw[s:e]
        entry = o[s + 1:e + 1]
        a = atr_arr[s:e]
        rows = np.arange(e - s)
        ih = hh.argmax(axis=1)  # first bar that makes the max high
        il = ll.argmin(axis=1)  # first bar that makes the min low
        mfe_l = hh[rows, ih] - entry
        mae_l = entry - np.minimum.accumulate(ll, axis=1)[rows, ih]
        mfe_s = entry - ll[rows, il]
        mae_s = np.maximum.accumulate(hh, axis=1)[rows, il] - entry
        ok = a > 0  # NaN > 0 is False
        with np.errstate(divide="ignore", invalid="ignore"):
            for name, val in (("mfe_long", mfe_l), ("mae_long", mae_l), ("mfe_short", mfe_s), ("mae_short", mae_s)):
                out[name][s:e] = np.where(ok, val / a, np.nan)
    return out


# ----------------------------------------------------------------------------------------------- legs

def zigzag_pivots(o, h, l, c, atr_arr, r):
    """ATR zigzag. Returns [(idx, typ, price)] with typ +1 swing high, -1 swing low, in time order, confirmed pivots only."""
    o_l, h_l, l_l, c_l = (np.asarray(x, dtype=float).tolist() for x in (o, h, l, c))
    h_np = np.asarray(h, dtype=float)
    l_np = np.asarray(l, dtype=float)
    a_l = np.asarray(atr_arr, dtype=float).tolist()
    n = len(h_l)
    s = next((i for i in range(n) if a_l[i] == a_l[i] and a_l[i] > 0), None)
    if s is None or s >= n - 1:
        return []
    piv = []
    d = 0
    e = 0
    ext = 0.0
    imin = imax = s
    min_l = l_l[s]
    max_h = h_l[s]
    for i in range(s + 1, n):
        if d == 0:  # no direction yet: wait for the first r x ATR move
            up = (h_l[i] - min_l) >= r * a_l[imin]
            dn = (max_h - l_l[i]) >= r * a_l[imax]
            if up and dn:  # outside bar: assume the candle colour gives the intrabar order
                if c_l[i] >= o_l[i]:
                    dn = False
                else:
                    up = False
            if up:
                piv.append((imin, -1, min_l))
                d = 1
                e = imin + 1 + int(np.argmax(h_np[imin + 1:i + 1]))
                ext = h_l[e]
            elif dn:
                piv.append((imax, 1, max_h))
                d = -1
                e = imax + 1 + int(np.argmin(l_np[imax + 1:i + 1]))
                ext = l_l[e]
            else:
                if l_l[i] < min_l:
                    imin, min_l = i, l_l[i]
                if h_l[i] > max_h:
                    imax, max_h = i, h_l[i]
        elif d == 1:
            if h_l[i] > ext:
                e, ext = i, h_l[i]
            elif l_l[i] <= ext - r * a_l[e]:
                piv.append((e, 1, ext))
                d = -1
                e = e + 1 + int(np.argmin(l_np[e + 1:i + 1]))
                ext = l_l[e]
        else:
            if l_l[i] < ext:
                e, ext = i, l_l[i]
            elif h_l[i] >= ext + r * a_l[e]:
                piv.append((e, -1, ext))
                d = 1
                e = e + 1 + int(np.argmax(h_np[e + 1:i + 1]))
                ext = h_l[e]
    return piv


def build_legs(b, r_list=R_LIST, k_list=K_LIST, atr_key="atr_wilder"):
    """Union of the zigzag legs for every r, with one flag per (r, k). `b` is a resample_bars dict plus atr_wilder / atr_sma."""
    atr_arr = b[atr_key]
    legs_by_r = {}
    for r in r_list:
        piv = zigzag_pivots(b["o"], b["h"], b["l"], b["c"], atr_arr, r)
        legs_by_r[r] = {(p0[0], p1[0], 1 if p0[1] == -1 else -1) for p0, p1 in zip(piv[:-1], piv[1:])}
    union = sorted(set().union(*legs_by_r.values())) if legs_by_r else []
    m = len(union)
    i0 = np.array([u[0] for u in union], dtype=np.int64)
    i1 = np.array([u[1] for u in union], dtype=np.int64)
    side = np.array([u[2] for u in union], dtype=np.int64)  # +1 long (low to high), -1 short
    p0 = np.where(side == 1, b["l"][i0], b["h"][i0]) if m else np.zeros(0)
    p1 = np.where(side == 1, b["h"][i1], b["l"][i1]) if m else np.zeros(0)
    atr0 = atr_arr[i0] if m else np.zeros(0)
    size = np.abs(p1 - p0) / atr0 if m else np.zeros(0)
    in_r = {r: np.array([u in legs_by_r[r] for u in union], dtype=bool) for r in r_list}
    flags = {(r, k): (in_r[r] & (size >= k)).astype(np.uint8) for r in r_list for k in k_list}
    return {
        "tf": b["tf"], "r_list": tuple(r_list), "k_list": tuple(k_list),
        "i0": i0, "i1": i1, "side": side, "p0": p0, "p1": p1, "size": size, "atr0": atr0,
        "dur": i1 - i0, "t_start": b["t_close"][i0] if m else np.zeros(0, dtype=np.int64),
        "t_end": b["t_close"][i1] if m else np.zeros(0, dtype=np.int64), "in_r": in_r, "flags": flags,
    }


def flag_name(r, k):
    return "flags_r%s_k%s" % (r, k)


def write_legs_csv(path, legs):
    tf = legs["tf"]
    header = ["leg_id", "tf", "side", "t_start_ms", "t_end_ms", "p_start", "p_end", "size_atr", "atr_at_start", "dur_bars"]
    header += [flag_name(r, k) for r in legs["r_list"] for k in legs["k_list"]]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        for n in range(len(legs["i0"])):
            row = ["%s-%06d" % (tf, n + 1), tf, "long" if legs["side"][n] == 1 else "short", int(legs["t_start"][n]), int(legs["t_end"][n]),
                   "%.10g" % legs["p0"][n], "%.10g" % legs["p1"][n], "%.6f" % legs["size"][n], "%.8g" % legs["atr0"][n], int(legs["dur"][n])]
            row += [int(legs["flags"][(r, k)][n]) for r in legs["r_list"] for k in legs["k_list"]]
            w.writerow(row)


def read_legs_csv(path):
    """Inverse of write_legs_csv: arrays for capture.py. side is +1 long / -1 short."""
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        rows = list(rd)
    col = {name: i for i, name in enumerate(header)}
    out = {
        "leg_id": [r[col["leg_id"]] for r in rows], "tf": rows[0][col["tf"]] if rows else "",
        "side": np.array([1 if r[col["side"]] == "long" else -1 for r in rows], dtype=np.int64),
        "t_start": np.array([int(r[col["t_start_ms"]]) for r in rows], dtype=np.int64),
        "t_end": np.array([int(r[col["t_end_ms"]]) for r in rows], dtype=np.int64),
        "p0": np.array([float(r[col["p_start"]]) for r in rows]), "p1": np.array([float(r[col["p_end"]]) for r in rows]),
        "size": np.array([float(r[col["size_atr"]]) for r in rows]), "atr0": np.array([float(r[col["atr_at_start"]]) for r in rows]),
        "dur": np.array([int(r[col["dur_bars"]]) for r in rows], dtype=np.int64), "flags": {},
    }
    for name, i in col.items():
        if name.startswith("flags_r"):
            r_s, k_s = name[len("flags_r"):].split("_k")
            out["flags"][(float(r_s), int(k_s))] = np.array([int(r[i]) for r in rows], dtype=np.uint8)
    return out


def label_columns(h_list=H_LIST):
    return ["%s_%d" % (name, H) for H in h_list for name in LABEL_NAMES]


def write_labels_csv(path, b, h_list=H_LIST):
    cols = ["t_close_ms", "close", "atr_wilder", "atr_sma"]
    data = [b["t_close"].astype(float), b["c"], b["atr_wilder"], b["atr_sma"]]
    fmts = ["%d", "%.10g", "%.8g", "%.8g"]
    for H in h_list:
        lab = forward_labels(b["o"], b["h"], b["l"], b["atr_wilder"], H)
        for name in LABEL_NAMES:
            cols.append("%s_%d" % (name, H))
            data.append(lab[name])
            fmts.append("%.6g")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        np.savetxt(fh, np.column_stack(data), delimiter=",", fmt=fmts, header=",".join(cols), comments="", newline="\n")


def read_labels_csv(path):
    with open(path, encoding="utf-8") as fh:
        cols = fh.readline().strip().split(",")
    arr = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    out = {c: arr[:, i] for i, c in enumerate(cols)}
    out["t_close_ms"] = out["t_close_ms"].astype(np.int64)
    return out


# ----------------------------------------------------------------------------------------------- statistics

def check_leg_invariants(b, legs, mask=None):
    """Independent re-check of legs against the raw bars (audit), optionally on a subset (bool mask over legs).
    pivot_not_bar_extreme: leg price is not the high/low of its pivot bar (must be 0).
    interior_more_extreme_bar: a bar STRICTLY between the pivots has a lower low (long leg) / higher high than the pivot, i.e. a whipsaw bar that
        spiked past the pivot and still extended the swing (intrabar order unknown, so the zigzag cannot move the pivot).
    pivot_bar_engulfs_leg: the pivot bar's own opposite extreme goes beyond the other pivot (one bar as long as the whole leg); unverifiable order.
    size_below_r: leg smaller than r x ATR for an r it is in (must be 0)."""
    h, l = b["h"], b["l"]
    idx = range(len(legs["i0"])) if mask is None else np.flatnonzero(mask)
    bad_pivot = bad_inner = engulf = bad_size = n = 0
    for q in idx:
        n += 1
        a, z = int(legs["i0"][q]), int(legs["i1"][q])
        if legs["side"][q] == 1:  # low at a, high at z
            if l[a] != legs["p0"][q] or h[z] != legs["p1"][q]:
                bad_pivot += 1
            if z - a > 1 and (l[a + 1:z].min() < legs["p0"][q] or h[a + 1:z].max() > legs["p1"][q]):
                bad_inner += 1
            if h[a] > legs["p1"][q] or l[z] < legs["p0"][q]:
                engulf += 1
        else:  # high at a, low at z
            if h[a] != legs["p0"][q] or l[z] != legs["p1"][q]:
                bad_pivot += 1
            if z - a > 1 and (h[a + 1:z].max() > legs["p0"][q] or l[a + 1:z].min() < legs["p1"][q]):
                bad_inner += 1
            if l[a] < legs["p1"][q] or h[z] > legs["p0"][q]:
                engulf += 1
    for r in legs["r_list"]:
        m = legs["in_r"][r] if mask is None else (legs["in_r"][r] & mask)
        bad_size += int(np.sum(legs["size"][m] < r - 1e-12))
    return {"legs": n, "pivot_not_bar_extreme": bad_pivot, "interior_more_extreme_bar": bad_inner, "pivot_bar_engulfs_leg": engulf,
            "size_below_r": bad_size}


def fractal_share(b, legs, r, n_side=2):
    """Share of r-zigzag pivots that also pass a +-n_side bar fractal test (strict on the left, non-strict on the right)."""
    h, l = b["h"], b["l"]
    m = legs["in_r"][r]
    piv = set()
    for a, z, sd in zip(legs["i0"][m], legs["i1"][m], legs["side"][m]):
        piv.add((int(a), -1 if sd == 1 else 1))
        piv.add((int(z), 1 if sd == 1 else -1))
    ok = tot = 0
    n = len(h)
    for idx, typ in piv:
        if idx < n_side or idx >= n - n_side:
            continue
        tot += 1
        if typ == 1:
            good = h[idx] > h[idx - n_side:idx].max() and h[idx] >= h[idx + 1:idx + n_side + 1].max()
        else:
            good = l[idx] < l[idx - n_side:idx].min() and l[idx] <= l[idx + 1:idx + n_side + 1].min()
        ok += int(good)
    return {"pivots": tot, "pass": ok, "share": (ok / tot) if tot else None}


def _years(ms_arr):
    return (ms_arr.astype("datetime64[ms]").astype("datetime64[Y]").astype(int) + 1970)


def compute_tf_stats(b, legs):
    """Numbers for BIGMOVES_REPORT.md: coverage, legs per year, size distribution, travel share, tradable share."""
    n = len(b["c"])
    r_list, k_list = legs["r_list"], legs["k_list"]
    ms = TF_MS[b["tf"]]
    dt = np.diff(b["t_open"])
    stats = {
        "n_bars": int(n), "first_ms": int(b["t_open"][0]), "last_ms": int(b["t_close"][-1]),
        "tf_time_gaps": int(np.sum(dt != ms)), "tf_missing_bars": int(np.sum(dt[dt != ms] // ms - 1)),
        "bars_with_partial_minutes": int(np.sum(b["gap_count"] > 0)),
        "bars_all_minutes_zero_volume": int(np.sum(b["v"] == 0)), "bars_zero_range": int(np.sum(b["h"] == b["l"])),
        "n_legs_union": int(len(legs["i0"])),
    }
    ratio = b["atr_sma"] / b["atr_wilder"]
    ratio = ratio[np.isfinite(ratio)]
    stats["atr_sma_over_wilder"] = {q: float(np.percentile(ratio, p)) for q, p in (("p5", 5), ("p50", 50), ("p95", 95))}
    years = _years(legs["t_start"]) if len(legs["t_start"]) else np.zeros(0, dtype=int)
    ylist = sorted({int(y) for y in _years(b["t_close"])})
    # all-bar abs log return, cumulative, for the travel share
    lr = np.abs(np.diff(np.log(b["c"])))
    cs = np.concatenate([[0.0], np.cumsum(lr)])  # cs[j] = travel from bar 0 to bar j
    total_travel = float(cs[-1])
    stats["per_year"], stats["size_pct"], stats["tradable"], stats["travel"] = {}, {}, {}, {}
    stats["years"] = ylist
    for r in r_list:
        m = legs["in_r"][r]
        sz = legs["size"][m]
        stats["size_pct"][str(r)] = {"n": int(m.sum()), **{"p%d" % p: float(np.percentile(sz, p)) for p in (10, 25, 50, 75, 90, 99)},
                                       "max": float(sz.max()) if len(sz) else None,
                                       "median_dur_bars": float(np.median(legs["dur"][m])) if m.any() else None}
        leg_logs = np.abs(np.log(legs["p1"][m] / legs["p0"][m]))
        for k in k_list:
            f = legs["flags"][(r, k)].astype(bool)
            key = "%s|%s" % (r, k)
            stats["per_year"][key] = {str(y): int(np.sum(f & (years == y))) for y in ylist}
            big = int(f.sum())
            gt3 = int(np.sum(f & (legs["dur"] > 3)))
            stats["tradable"][key] = {"n_big": big, "n_dur_gt3": gt3, "share_dur_gt3": (gt3 / big) if big else None,
                                      "median_dur_bars": float(np.median(legs["dur"][f])) if big else None}
            inside = float(np.sum(cs[legs["i1"][f]] - cs[legs["i0"][f]]))
            fm = f[m]
            stats["travel"][key] = {
                "legs_path_share": float(np.sum(leg_logs[fm]) / np.sum(leg_logs)) if len(leg_logs) else None,
                "bar_travel_share": inside / total_travel if total_travel else None,
                "time_share": float(np.sum(legs["dur"][f]) / n),
            }
    stats["invariants"] = check_leg_invariants(b, legs)
    stats["invariants_big"] = {"%s|%s" % (r, k): check_leg_invariants(b, legs, legs["flags"][(r, k)].astype(bool)) for r in r_list for k in k_list}
    stats["fractal"] = {str(r): fractal_share(b, legs, r) for r in r_list}
    # legs that start within 2 x ATR-period bars after a maintenance-flat bar (zero volume, high == low): their ATR unit is depressed
    flat = (b["v"] == 0) & (b["h"] == b["l"])
    near = np.zeros(n, dtype=bool)
    for lag in range(0, min(2 * ATR_PERIOD + 1, n)):
        near[lag:] |= flat[:n - lag]
    stats["legs_near_flat_bar"] = {"%s|%s" % (r, k): int(np.sum(legs["flags"][(r, k)].astype(bool) & near[legs["i0"]])) for r in r_list for k in k_list}
    return stats


# ----------------------------------------------------------------------------------------------- driver

def build_tf(bars_1m, tf, out_dir, r_list=R_LIST, k_list=K_LIST, h_list=H_LIST, write_labels=True):
    b = resample_bars(bars_1m, tf)
    b["atr_wilder"] = atr(b["h"], b["l"], b["c"], ATR_PERIOD, "wilder")
    b["atr_sma"] = atr(b["h"], b["l"], b["c"], ATR_PERIOD, "sma")
    legs = build_legs(b, r_list, k_list)
    out_dir = Path(out_dir)
    write_legs_csv(out_dir / ("legs_%s.csv" % tf), legs)
    if write_labels:
        write_labels_csv(out_dir / ("labels_%s.csv" % tf), b, h_list)
    return b, legs, compute_tf_stats(b, legs)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Build big-move ground truth (legs + forward labels).")
    ap.add_argument("--tfs", default=",".join(TFS))
    ap.add_argument("--out", default=str(DATA_DIR))
    ap.add_argument("--no-labels", action="store_true")
    a = ap.parse_args(argv)
    t0 = datetime.datetime.now()
    bars, src_report = load_1m()
    cov = coverage_1m(bars)
    print("loaded %d 1m bars %s .. %s" % (cov["n_bars"], iso(cov["first_ms"]), iso(cov["last_ms"])), flush=True)
    stats = {"settings": {"atr_period": ATR_PERIOD, "r_list": list(R_LIST), "k_list": list(K_LIST), "h_list": list(H_LIST),
                          "atr_kind": "wilder", "sources": src_report}, "coverage_1m": cov, "tf": {}}
    for tf in a.tfs.split(","):
        b, legs, st = build_tf(bars, tf, a.out, write_labels=not a.no_labels)
        stats["tf"][tf] = st
        print("%s: %d bars, %d legs, invariants %s" % (tf, st["n_bars"], st["n_legs_union"], st["invariants"]), flush=True)
    path = Path(a.out) / "bigmoves_stats.json"
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=1)
    print("wrote", path, "in", datetime.datetime.now() - t0)


if __name__ == "__main__":
    main()
