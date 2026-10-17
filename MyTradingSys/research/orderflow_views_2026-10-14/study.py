"""Price vs CVD divergence on 1m and 5m, with an OI split (operator shots c688/a18c/8adf, 2026-10-14).

Operator: "The buy in 1 min is quite visible as price was falling CVD was increasing - verify this ... find clues
that will prove us the EDGE". This script (1) checks today's chart readings against Binance fapi data and (2) runs
ONE pre-registered test of the pattern. Every number below is OURS (no trader gave numbers). Fixed before the
first run; every variant is printed (trial ledger = the output table).

Data: Binance USD-M BTCUSDT 1m klines (taker_buy_volume -> delta = 2*tbv - v, same as bt_data.cvd_delta),
archive F:/MTS/data/tom_raw/klines (2022-01..2026-09-26) + fapi top-up to 2026-10-14 15:21Z.
OI: Binance metrics 5m sum_open_interest (F:/MTS/Dumps/backtest/raw/metrics, 2025-09-01..) + fapi openInterestHist.

Definition (scale S1 = 1m bars with half-window H=15; S5 = 5m bars with H=12, i.e. 15 min / 60 min halves):
  at the close of bar t, LONG divergence ("price lower low, CVD higher low") when ALL hold:
    a. min(low[t-H+1..t]) < min(low[t-2H+1..t-H])            price made a lower low in the recent half
    b. the recent-half low is in the last 3 bars              we are at the low now (no hindsight pivot)
    c. close[t] < close[t-4H] * (1 - CTX)                     falling context (CTX 0.25% S1, 0.5% S5)
    d. min(cvd[t-H+1..t]) > min(cvd[t-2H+1..t-H])            CVD did NOT make a lower low (cvd = bar-close values)
  CONTROL = a+b+c without d (every lower low at the low in a falling context).  CONFIRM = a+b+c and NOT d.
  SHORT is the mirror (higher high, CVD lower high, rising context).
  Entry = open of the next 1m bar. Cooldown 120 min per side and per arm. Fee 0.05% per side (0.10% round trip).
  Outcomes: forward return at 30/60/120 min (net), and a trade: stop 0.1% beyond the recent-half extreme, target 2R,
  time exit 120 min, checked on 1m bars (stop first when both are hit in one minute).
  OI split (only where OI exists, 2025-09+): OI change over the 60 min to the bar close > 0 (UP) or <= 0 (DOWN).
  Splits: DEV 2022-2024, VAL 2025, HOLDOUT 2026.
  Edge rule (fixed before the run): DIV minus CONTROL at 60 min >= +0.05% net on DEV with Welch t >= 2, and the same
  sign on VAL and HOLDOUT. Anything else = no edge.

Usage: python study.py fetch | today | bt
"""
import csv
import datetime as dt
import gzip
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCH = Path("F:/MTS/data/tom_raw/klines")
METR = Path("F:/MTS/Dumps/backtest/raw/metrics")
TOPUP = Path("F:/MTS/data/orderflow_views_2026-10-14")
MIN = 60_000
FEE_RT = 0.10
T_TOPUP0 = int(dt.datetime(2026, 9, 27, tzinfo=dt.timezone.utc).timestamp() * 1000)
T_END = int(dt.datetime(2026, 10, 14, 15, 21, tzinfo=dt.timezone.utc).timestamp() * 1000)


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch():
    TOPUP.mkdir(parents=True, exist_ok=True)
    rows, t = [], T_TOPUP0
    while t < T_END:
        k = _get(f"https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&startTime={t}&limit=1500")
        k = [r for r in k if r[0] < T_END and r[6] < T_END]          # closed bars only
        if not k:
            break
        rows += k
        t = k[-1][0] + MIN
        time.sleep(0.2)
    with open(TOPUP / "klines_1m.csv", "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
                    "taker_buy_volume", "taker_buy_quote_volume", "ignore"])
        w.writerows(rows)
    oi, t = [], T_TOPUP0
    while t < T_END:
        r = _get("https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=500"
                 f"&startTime={t}&endTime={min(t + 500 * 300_000, T_END)}")
        if not r:
            t += 500 * 300_000
            continue
        oi += [(int(x["timestamp"]), float(x["sumOpenInterest"])) for x in r]
        t = int(r[-1]["timestamp"]) + 300_000
        time.sleep(0.2)
    with open(TOPUP / "oi_5m.csv", "w", newline="\n", encoding="utf-8") as f:
        f.write("t,oi\n" + "".join(f"{a},{b}\n" for a, b in oi))
    print(f"klines {len(rows)} bars to {rows[-1][0] if rows else None}; oi {len(oi)} rows")


def load_1m():
    rows = {}
    files = sorted(ARCH.glob("BTCUSDT-1m-*.csv")) + ([TOPUP / "klines_1m.csv"] if (TOPUP / "klines_1m.csv").exists() or not DEV_ONLY else [])
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= T_END:
                    continue
                rows[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9]))
    ts = np.array(sorted(rows), dtype=np.int64)
    t0 = ts[0] - ts[0] % (5 * MIN)
    n = int((ts[-1] - t0) // MIN) + 1
    n -= n % 5
    A = np.full((n, 6), np.nan)
    idx = ((ts - t0) // MIN).astype(np.int64)
    keep = idx < n
    A[idx[keep]] = np.array([rows[t] for t in ts[keep]])
    return int(t0), A


def load_oi():
    oi = {}
    for f in sorted(METR.glob("BTCUSDT-metrics-*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
                oi[t] = float(r[2])
    p = TOPUP / "oi_5m.csv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines()[1:]:
            a, b = line.split(",")
            oi[int(a)] = float(b)
    return oi


def oi_at(oi, t):
    """OI snapshot at or before t, within 10 min; None if absent."""
    b = t - t % (5 * MIN)
    for k in range(3):
        v = oi.get(b - k * 5 * MIN)
        if v is not None:
            return v
    return None


def to_5m(A):
    m = A.reshape(-1, 5, 6)
    bad = np.isnan(m[:, :, 3]).any(axis=1)
    B = np.column_stack([m[:, 0, 0], m[:, :, 1].max(axis=1), m[:, :, 2].min(axis=1), m[:, 4, 3],
                         m[:, :, 4].sum(axis=1), m[:, :, 5].sum(axis=1)])
    B[bad] = np.nan
    return B


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def windows(x, H):
    from numpy.lib.stride_tricks import sliding_window_view as sw
    return sw(x, 2 * H)


def signals(B, H, ctx, side):
    """Boolean arrays (div, control, confirm) at bar index t (bar close). B cols o,h,l,c,v,tbv."""
    n = len(B)
    d = 2 * B[:, 5] - B[:, 4]
    cvd = np.nancumsum(np.nan_to_num(d))
    out = np.zeros((3, n), dtype=bool)
    lo, hi, c = B[:, 2], B[:, 1], B[:, 3]
    px = lo if side == "long" else -hi
    q = cvd if side == "long" else -cvd
    W = windows(px, H)                       # row j covers bars j..j+2H-1, t = j+2H-1
    Q = windows(q, H)
    prior_p, rec_p = W[:, :H].min(axis=1), W[:, H:].min(axis=1)
    prior_q, rec_q = Q[:, :H].min(axis=1), Q[:, H:].min(axis=1)
    arg = W[:, H:].argmin(axis=1)
    t = np.arange(2 * H - 1, n)
    ok = ~np.isnan(W).any(axis=1) & (t >= 4 * H)
    back = np.where(t >= 4 * H, t - 4 * H, 0)
    trend = (c[t] < c[back] * (1 - ctx)) if side == "long" else (c[t] > c[back] * (1 + ctx))
    base = ok & (rec_p < prior_p) & (arg >= H - 3) & trend
    div = rec_q > prior_q
    out[0, t] = base & div
    out[1, t] = base
    out[2, t] = base & ~div
    ext = np.full(n, np.nan)
    ext[t] = np.where(side == "long", W[:, H:].min(axis=1), -W[:, H:].min(axis=1))
    return out, ext, cvd


def trade(A1, e, ext, side):
    """Entry at 1m index e (open). Returns (ret30, ret60, ret120, trade_ret) in % net of fees, or None."""
    if e + 120 >= len(A1):
        return None
    seg = A1[e:e + 120]
    if np.isnan(seg[:, 3]).any():
        return None
    p0 = seg[0, 0]
    sgn = 1 if side == "long" else -1
    fw = [sgn * (seg[h - 1, 3] / p0 - 1) * 100 - FEE_RT for h in (30, 60, 120)]
    stop = ext * (1 - 0.001) if side == "long" else ext * (1 + 0.001)
    risk = sgn * (p0 - stop)
    if risk <= 0:
        return None
    tgt = p0 + sgn * 2 * risk
    res = sgn * (seg[-1, 3] / p0 - 1) * 100
    for h, l in zip(seg[:, 1], seg[:, 2]):
        hit_s = l <= stop if side == "long" else h >= stop
        hit_t = h >= tgt if side == "long" else l <= tgt
        if hit_s:
            res = -risk / p0 * 100
            break
        if hit_t:
            res = 2 * risk / p0 * 100
            break
    return fw + [res - FEE_RT]


# Rerun 2026-10-17 (OFV_DEV_ONLY=1): repo split, DEV = before 2024-07-01. Later rows (VALIDATION, HOLDOUT) are never evaluated.
DEV_ONLY = os.environ.get("OFV_DEV_ONLY") == "1"
DEV_END_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def split_of(ms):
    y = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).year
    return "DEV" if y <= 2024 else ("VAL" if y == 2025 else "HOLDOUT")


def run_bt():
    t0, A1 = load_1m()
    oi = load_oi()
    B5 = to_5m(A1)
    out = {"rows": [], "today": [], "trial_ledger": "scale x side x arm x split x oi; all printed, nothing tuned"}
    for scale, B, H, ctx, step in (("S1", A1, 15, 0.0025, 1), ("S5", B5, 12, 0.005, 5)):
        for side in ("long", "short"):
            sig, ext, _ = signals(B, H, ctx, side)
            for ai, arm in enumerate(("DIV", "CONTROL", "CONFIRM")):
                last = -10 ** 9
                recs = []
                for t in np.flatnonzero(sig[ai]):
                    close_ms = t0 + (t + 1) * step * MIN
                    if close_ms - last < 120 * MIN:
                        continue
                    e = (t + 1) * step
                    if DEV_ONLY and close_ms >= DEV_END_MS:
                        continue
                    r = trade(A1, e, ext[t], side)
                    if r is None:
                        continue
                    last = close_ms
                    o1, o0 = oi_at(oi, close_ms), oi_at(oi, close_ms - 60 * MIN)
                    oid = None if (o1 is None or o0 is None) else ("UP" if o1 > o0 else "DOWN")
                    recs.append((close_ms, split_of(close_ms), oid, *r))
                    if close_ms >= T_END - 16 * 60 * MIN and arm == "DIV":
                        out["today"].append({"scale": scale, "side": side, "bar_close": iso(close_ms), "oi": oid,
                                             "r30": round(r[0], 3), "r60": round(r[1], 3), "trade": round(r[3], 3)})
                for sp in (("DEV",) if DEV_ONLY else ("DEV", "VAL", "HOLDOUT", "ALL")):
                    for oo in (None, "UP", "DOWN"):
                        sel = [x for x in recs if (sp == "ALL" or x[1] == sp) and (oo is None or x[2] == oo)]
                        if oo is not None and not sel:
                            continue
                        a = np.array([x[3:] for x in sel]) if sel else np.zeros((0, 4))
                        row = {"scale": scale, "side": side, "arm": arm, "split": sp, "oi": oo or "any", "n": len(sel)}
                        for k, nm in enumerate(("r30", "r60", "r120", "trade")):
                            v = a[:, k] if len(a) else np.array([])
                            row[nm] = round(float(v.mean()), 4) if len(v) else None
                            row[nm + "_t"] = round(float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))), 2) if len(v) > 2 else None
                        row["_r60"] = a[:, 1].tolist() if len(a) else []
                        out["rows"].append(row)
    # edge test: DIV - CONTROL at 60 min, Welch t
    edge = []
    for scale in ("S1", "S5"):
        for side in ("long", "short"):
            for oo in ("any", "UP", "DOWN"):
                line = {"scale": scale, "side": side, "oi": oo}
                for sp in (("DEV",) if DEV_ONLY else ("DEV", "VAL", "HOLDOUT")):
                    g = {r["arm"]: r for r in out["rows"] if r["scale"] == scale and r["side"] == side and r["split"] == sp and r["oi"] == oo}
                    if "DIV" not in g or "CONTROL" not in g or g["DIV"]["n"] < 3:
                        line[sp] = None
                        continue
                    x, y = np.array(g["DIV"]["_r60"]), np.array(g["CONTROL"]["_r60"])
                    diff = x.mean() - y.mean()
                    se = np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
                    line[sp] = {"diff": round(float(diff), 4), "t": round(float(diff / se), 2), "n_div": len(x), "n_ctl": len(y)}
                d = line.get("DEV")
                line["edge"] = bool(d and d["diff"] >= 0.05 and d["t"] >= 2 and all(
                    line.get(s) and line[s]["diff"] > 0 for s in ("VAL", "HOLDOUT")))
                edge.append(line)
    for r in out["rows"]:
        r.pop("_r60")
    out["edge"] = edge
    (HERE / ("results_dev_rerun_2026-10-17.json" if DEV_ONLY else "results.json")).write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    for r in out["rows"]:
        if r["oi"] == "any":
            print(r["scale"], r["side"], r["arm"], r["split"], r["n"], "r60", r["r60"], r["r60_t"], "trade", r["trade"], r["trade_t"])
    for e in edge:
        print("EDGE", e)
    print("TODAY", out["today"])


def today():
    t0, A1 = load_1m()
    oi = load_oi()
    day0 = int(dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
    i0 = (day0 - t0) // MIN
    i22 = i0 - 120
    seg = A1[i22:]
    ts = t0 + (i22 + np.arange(len(seg))) * MIN
    d = 2 * seg[:, 5] - seg[:, 4]
    cvd22 = np.cumsum(d)
    rep = {}
    # 5m table 12:00..15:20 with CVD anchored 22:00Z 13 Oct and OI
    tab = []
    for k in range(0, len(seg) - 4, 5):
        if ts[k] < day0 + 12 * 3600_000:
            continue
        s = seg[k:k + 5]
        tab.append({"t": iso(ts[k])[11:], "o": s[0, 0], "h": s[:, 1].max(), "l": s[:, 2].min(), "c": s[-1, 3],
                    "delta": round(float(d[k:k + 5].sum()), 1), "cvd22_close": round(float(cvd22[k + 4]), 1),
                    "oi_at_close": oi_at(oi, int(ts[k]) + 5 * MIN)})
    rep["bars_5m"] = tab
    # 1m: CVD and price extremes after 13:50
    m = ts >= day0 + (13 * 60 + 50) * MIN
    j = np.flatnonzero(m)
    jc = j[np.argmin(cvd22[j])]
    jp = j[np.argmin(seg[j, 2])]
    rep["cvd_low_after_1350"] = {"t": iso(ts[jc]), "cvd22": round(float(cvd22[jc]), 1), "price_close": seg[jc, 3], "price_low": seg[jc, 2]}
    rep["price_low_after_1350"] = {"t": iso(ts[jp]), "low": seg[jp, 2], "cvd22": round(float(cvd22[jp]), 1)}
    rep["last_closed_1m"] = {"t": iso(ts[-1]), "close": seg[-1, 3], "cvd22": round(float(cvd22[-1]), 1)}
    rep["cvd_rise_from_low_to_last"] = round(float(cvd22[-1] - cvd22[jc]), 1)
    # VWAP anchored at 00:00Z (hlc3) and the anchor that fits 82643.0 at 15:17 close
    tp = (seg[:, 1] + seg[:, 2] + seg[:, 3]) / 3
    v = seg[:, 4]
    def vwap(a, b):
        return float((tp[a:b + 1] * v[a:b + 1]).sum() / v[a:b + 1].sum())
    i1517 = int(np.flatnonzero(ts == day0 + (15 * 60 + 17) * MIN)[0])
    rep["vwap_00Z_at_1517"] = round(vwap(120, i1517), 1)
    rep["vwap_00Z_at_last"] = round(vwap(120, len(seg) - 1), 1)
    best = min(range(0, i1517), key=lambda a: abs(vwap(a, i1517) - 82643.0))
    rep["anchor_fitting_82643"] = {"anchor": iso(ts[best]), "vwap": round(vwap(best, i1517), 1)}
    best2 = min(range(0, len(seg) - 1), key=lambda a: abs(vwap(a, len(seg) - 1) - 82999.5))
    rep["anchor_fitting_82999.5"] = {"anchor": iso(ts[best2]), "vwap": round(vwap(best2, len(seg) - 1), 1)}
    # OI points read off the charts
    rep["oi"] = {h: oi_at(oi, day0 + int(h[:2]) * 3600_000 + int(h[3:]) * MIN) for h in
                 ("10:00", "12:15", "12:30", "13:30", "14:00", "14:55", "15:00", "15:10", "15:15", "15:20")}
    (HERE / "today.json").write_text(json.dumps(rep, indent=1, default=float), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "bars_5m"}, indent=1, default=float))
    for r in tab:
        print(r)


if __name__ == "__main__":
    {"fetch": fetch, "today": today, "bt": run_bt}[sys.argv[1]]()
