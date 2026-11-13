"""
MyTradingSys/research/adx_di_2026-11/measure_1113.py - card adx-measure-1113. Context measurement, no orders, no edge claim.
Formula: adx.py adx_di (Wilder, n=14) reused unchanged. Thresholds 20/25/40 and n=14 only, no tuning:
  14 = Wilder 1978 (SOURCED); 20 / 25 / 40 = Wilder / Schaap rule-of-thumb levels (SOURCED, see CCU_RULES / USAGE_adx).
Data: 5m BTCUSDT linear klines from Bybit public API (cache JSON, fetched by the runner), resampled up with tf_resample;
      1d/2d/5d/1w from research/btc_cycles_2026-11/btc_daily.csv (2017+) topped up with Bybit-derived days.
  python measure_1113.py <bybit_5m.json> [--out MEASURE_1113.md]
The cache JSON is rows [open_time_ms, open, high, low, close, volume] (Bybit v5 kline order, ascending).
"""
import csv
import datetime
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "backtest", "layers", "adx"))
sys.path.insert(0, os.path.join(ROOT, "backtest", "layers", "timeframe"))
from adx import adx_di  # noqa: E402
from tf_resample import resample  # noqa: E402

DAILY = os.path.join(ROOT, "research", "btc_cycles_2026-11", "btc_daily.csv")
REGISTRY = os.path.join(ROOT, "backtest", "layers", "timeframe", "registry.json")
N = 14
LV_LO, LV_MID, LV_HI = 20.0, 25.0, 40.0
HORIZONS = (3, 6, 12)
FEE = 0.0004                    # 4 bps round trip, intraday frames only
INTRADAY = ("5m", "15m", "1h", "4h")
TFS = ("5m", "15m", "1h", "4h", "1d", "2d", "5d", "1w")
MIN_N = 30
DAY_MS = 86400000


def compute(bars, n=N):
    """(dip, dim, adx) lists via adx.py; bars = dicts with h, l, c."""
    return adx_di([b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars], n)


def events(dip, dim, adx):
    """dict name -> bar indices (signal bar close). Pure function of the three series."""
    ev = {k: [] for k in ("L_cross", "L_adx25", "S_cross", "S_adx25", "peak40")}
    for i in range(2, len(adx)):
        if None in (dip[i], dim[i], adx[i], dip[i - 1], dim[i - 1], adx[i - 1]):
            continue
        up = dip[i] > dim[i]
        dn = dim[i] > dip[i]
        if dip[i - 1] <= dim[i - 1] and up and adx[i] > LV_LO:
            ev["L_cross"].append(i)
        if dim[i - 1] <= dip[i - 1] and dn and adx[i] > LV_LO:
            ev["S_cross"].append(i)
        if adx[i - 1] <= LV_MID < adx[i]:
            if up:
                ev["L_adx25"].append(i)
            if dn:
                ev["S_adx25"].append(i)
        if adx[i - 2] is not None and adx[i - 2] < adx[i - 1] > adx[i] and adx[i - 1] > LV_HI:
            ev["peak40"].append(i)
    return ev


def fwd(c, i, h, sign, fee):
    """Net forward return of direction sign opened at close i, closed at close i+h; None if no data."""
    if i + h >= len(c):
        return None
    return sign * (c[i + h] / c[i] - 1.0) - fee


def stats(vals):
    v = [x for x in vals if x is not None]
    n = len(v)
    if n == 0:
        return {"n": 0, "mean": None, "win": None, "sd": None}
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0.0
    return {"n": n, "mean": m, "win": sum(1 for x in v if x > 0) / n, "sd": sd}


def pct(x, d=3):
    return "-" if x is None else ("%+.*f%%" % (d, x * 100))


def cell(e, b):
    if e["n"] == 0:
        return None
    ex = e["mean"] - b["mean"]
    t = ex / (e["sd"] / math.sqrt(e["n"])) if e["sd"] else 0.0
    return {"n": e["n"], "mean": e["mean"], "base": b["mean"], "ex": ex, "win": e["win"], "bwin": b["win"],
            "t": t, "under": e["n"] < MIN_N}


def fmt_cells(cells):
    parts = []
    for c in cells:
        if c is None:
            parts.append("n=0")
            continue
        flag = " UNDERPOWERED" if c["under"] else ""
        parts.append("n=%d net %s vs base %s (ex %s, t %.1f) win %.0f%% vs %.0f%%%s" % (
            c["n"], pct(c["mean"]), pct(c["base"]), pct(c["ex"]), c["t"], c["win"] * 100, c["bwin"] * 100, flag))
    return parts


def load_5m(path):
    raw = json.load(open(path))
    # stamp at last minute so tf_resample (built for 1m bars) buckets 5m bars correctly
    return [{"t": int(r[0]) + 4 * 60000, "o": r[1], "h": r[2], "l": r[3], "c": r[4]} for r in raw]


def load_daily(start="2017-01-01"):
    out = []
    with open(DAILY, newline="") as f:
        for r in csv.DictReader(f):
            if r["date"] < start:
                continue
            d = datetime.datetime.strptime(r["date"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
            out.append({"t": int(d.timestamp() * 1000) + DAY_MS - 60000, "o": float(r["close"]),
                        "h": float(r["high"]), "l": float(r["low"]), "c": float(r["close"])})
    return out


def build_series(bars5, registry):
    ser = {"5m": bars5}
    for tf in ("15m", "1h", "4h"):
        ser[tf] = resample(bars5, tf, registry)
    d_csv = load_daily()
    last_csv = d_csv[-1]["t"]
    d_fetch = [b for b in resample(bars5, "1d", registry) if b["t"] + DAY_MS - 60000 > last_csv]
    daily = d_csv + [{"t": b["t"] + DAY_MS - 60000, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"]} for b in d_fetch]
    ser["1d"] = [{"t": b["t"] - (DAY_MS - 60000), "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"]} for b in daily]
    for tf in ("2d", "5d", "1w"):
        ser[tf] = resample(daily, tf, registry)
    # 5m bars were stamped at their last minute for the resampler; show open times again
    ser["5m"] = [dict(b, t=b["t"] - 4 * 60000) for b in bars5]
    return ser, len(d_csv), len(d_fetch)


def ts(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def fade_table(c, dip, dim, adx, valid, fee):
    rows = []
    low = [i for i in valid if adx[i] < LV_LO]
    hi = [i for i in valid if adx[i] >= LV_LO]
    for label, idxs in (("ADX<20", low), ("ADX>=20", hi)):
        for rule in ("fade last bar", "fade DI leader", "follow DI leader"):
            cs = []
            for h in HORIZONS:
                vals = []
                for i in idxs:
                    if i < 1:
                        continue
                    if rule == "fade last bar":
                        s = -1 if c[i] > c[i - 1] else (1 if c[i] < c[i - 1] else 0)
                    elif rule == "fade DI leader":
                        s = -1 if dip[i] > dim[i] else 1
                    else:
                        s = 1 if dip[i] > dim[i] else -1
                    if s:
                        vals.append(fwd(c, i, h, s, fee))
                st = stats(vals)
                cs.append("n=%d net %s win %.0f%%%s" % (st["n"], pct(st["mean"]), (st["win"] or 0) * 100,
                                                        " UNDERPOWERED" if st["n"] < MIN_N else ""))
            rows.append((label, rule, cs))
    return len(low) / len(valid), rows


def fwd_abs_move(c, valid, h):
    """Mean absolute h-bar move over every bar in valid (the unconditional comparison for the peak table)."""
    return stats([abs(c[i + h] / c[i] - 1.0) for i in valid if i + h < len(c)])["mean"]


def fwd_peak_outcomes(c, dip, dim, adx, pk, h, fee):
    """Outcomes h bars after each peak event: (net returns holding the trend direction, abs moves, count with ADX<25)."""
    cont, absm, below = [], [], 0
    for i in pk:
        if i + h >= len(c):
            continue
        s = 1 if dip[i - 1] > dim[i - 1] else -1     # trend direction at the peak bar
        cont.append(fwd(c, i, h, s, fee))
        absm.append(abs(c[i + h] / c[i] - 1.0))
        if adx[i + h] is not None and adx[i + h] < LV_MID:
            below += 1
    return cont, absm, below


def peak_row(c, dip, dim, adx, pk, valid, fee):
    out = []
    for h in HORIZONS:
        cont, absm, below = fwd_peak_outcomes(c, dip, dim, adx, pk, h, fee)
        st = stats(cont)
        base_abs = fwd_abs_move(c, valid, h)
        out.append("n=%d trend-dir net %s win %.0f%%; abs move %s vs all-bars %s; ADX<25 after: %s%s" % (
            st["n"], pct(st["mean"]), (st["win"] or 0) * 100,
            pct(sum(absm) / len(absm)) if absm else "-", pct(base_abs),
            ("%.0f%%" % (100.0 * below / len(absm))) if absm else "-", " UNDERPOWERED" if st["n"] < MIN_N else ""))
    return out


def run(path, out_path):
    registry = json.load(open(REGISTRY))
    bars5 = load_5m(path)
    ser, n_csv, n_top = build_series(bars5, registry)
    A, B, D, CUR, COV = [], [], [], [], []
    for tf in TFS:
        bars = ser[tf]
        c = [b["c"] for b in bars]
        dip, dim, adx = compute(bars)
        fee = FEE if tf in INTRADAY else 0.0
        valid = [i for i in range(len(c)) if adx[i] is not None]
        ev = events(dip, dim, adx)
        COV.append((tf, len(bars), ts(bars[0]["t"]), ts(bars[-1]["t"]), len(valid)))
        j = len(bars) - 1
        CUR.append((tf, ts(bars[j]["t"]), adx[j], dip[j], dim[j], "+DI>-DI" if dip[j] > dim[j] else "-DI>+DI"))
        for name, sign in (("L_cross", 1), ("L_adx25", 1), ("S_cross", -1), ("S_adx25", -1)):
            cells = []
            for h in HORIZONS:
                e = stats([fwd(c, i, h, sign, fee) for i in ev[name]])
                b = stats([fwd(c, i, h, sign, fee) for i in valid])
                cells.append(cell(e, b))
            A.append((tf, name, fmt_cells(cells)))
        share, rows = fade_table(c, dip, dim, adx, valid, fee)
        B.append((tf, share, rows))
        D.append((tf, len(ev["peak40"]), peak_row(c, dip, dim, adx, ev["peak40"], valid, fee)))
    write(out_path, COV, CUR, A, B, D, n_csv, n_top, len(bars5))


def write(out_path, COV, CUR, A, B, D, n_csv, n_top, n5):
    L = ["# MEASURE_1113 - ADX / +DI / -DI measured on BTC, 8 timeframes (card adx-measure-1113)", "",
         "Generated by `measure_1113.py` (formula: `backtest/layers/adx/adx.py`, Wilder n=14, reused unchanged). "
         "Context measurement: no orders, no edge claim. Run at %s UTC." %
         datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"), "",
         "**No tuning.** Period 14 = Wilder 1978 (SOURCED). Levels 20 / 25 / 40 = Wilder and Schaap rule-of-thumb levels "
         "(SOURCED: `research/cbp/ccu_DXntdN3jfTg_extract.md`, `research/tv_favorites_2026-11/USAGE_adx.md`). "
         "Horizons 3/6/12 bars, entry at the signal bar's close, exit at close of bar +h. Fee 4 bps round trip on 5m/15m/1h/4h only; "
         "none on 1d+ (OURS). Baseline = same-direction position opened at EVERY bar with ADX defined, same horizon, same fee. "
         "`t` = (event mean - baseline) / (event sd / sqrt n): OURS, overlapping bars inflate it, rough only. "
         "n<30 = UNDERPOWERED. Everything below is OURS (inference from these runs).", "",
         "## Data", "", "| Item | Value |", "|---|---|",
         "| 5m source | Bybit v5 `api.bybit.com/v5/market/kline` BTCUSDT linear, %d 5m bars (public data; fapi.binance.com unreachable). "
         "Bybit perp, not Binance: prices differ a few bps, shape does not |" % n5,
         "| 15m / 1h / 4h | resampled from the 5m bars with `tf_resample` (UTC buckets) |",
         "| 1d / 2d / 5d / 1w | `research/btc_cycles_2026-11/btc_daily.csv` from 2017-01-01 (%d days) + %d top-up days from Bybit; 2d/5d registry epoch-day buckets, 1w Monday-anchored |" % (n_csv, n_top),
         "| On-disk fixtures | `MyTradingSys/data/klines/BTCUSDT_{5m,15m,1h}.json` hold ~100 bars each: too short, not used |", "",
         "| TF | bars | first bar (UTC) | last closed bar (UTC) | bars with ADX |", "|---|---|---|---|---|"]
    for tf, nb, f, l, nv in COV:
        L.append("| %s | %d | %s | %s | %d |" % (tf, nb, f, l, nv))
    L += ["", "Intraday history starts 2020-04 (Bybit listing); intraday before that is UNKNOWN.", "",
          "## Current reading at run time (last closed bar)", "",
          "| TF | bar open (UTC) | ADX | +DI | -DI | state |", "|---|---|---|---|---|---|"]
    for tf, t, a, p, m, s in CUR:
        L.append("| %s | %s | %.1f | %.1f | %.1f | %s |" % (tf, t, a, p, m, s))
    L += ["", "## (a) Trend entries: DI cross with ADX>20, and ADX rising through 25 with the DI order", "",
          "Long = +DI crosses above -DI with ADX>20 (L_cross) or ADX crosses 25 upward with +DI>-DI (L_adx25). "
          "Short = mirrored. Cells = horizon 3 | 6 | 12 bars. `net` = mean return of the signal trades, `base` = same-direction any-bar baseline, "
          "`ex` = difference, `win` = share of trades above zero vs baseline share.", "",
          "| TF | signal | h=3 | h=6 | h=12 |", "|---|---|---|---|---|"]
    for tf, name, cs in A:
        L.append("| %s | %s | %s |" % (tf, name, " | ".join(cs)))
    L += ["", "## (b) ADX below 20: share of time, and fade versus follow", "",
          "Rules (parameter-free, OURS): fade last bar = go against the signal bar's direction; fade DI leader = short when +DI>-DI, long otherwise; "
          "follow DI leader = the opposite. Compared in the ADX<20 and ADX>=20 states. Net of fee on intraday.", ""]
    for tf, share, rows in B:
        L += ["### %s - ADX<20 on %.0f%% of bars" % (tf, share * 100), "",
              "| state | rule | h=3 | h=6 | h=12 |", "|---|---|---|---|---|"]
        for lab, rule, cs in rows:
            L.append("| %s | %s | %s |" % (lab, rule, " | ".join(cs)))
        L.append("")
    L += ["## (c) ADX peak above 40, first turn down", "",
          "Event: ADX[i-1] is a local maximum above 40 and ADX[i]<ADX[i-1]; entry at close of bar i. Trend direction = sign(+DI minus -DI) at the peak bar. "
          "'trend-dir' = holding in that direction; 'abs move' = mean absolute move vs the mean over all bars; "
          "'ADX<25 after' = share where ADX is below 25 h bars later.", "",
          "| TF | events | h=3 | h=6 | h=12 |", "|---|---|---|---|---|"]
    for tf, n, cs in D:
        L.append("| %s | %d | %s |" % (tf, n, " | ".join(cs)))
    L += ["", "## SUMMARY_PLACEHOLDER", ""]
    open(out_path, "w", encoding="utf-8").write("\n".join(L))
    print("wrote", out_path)


if __name__ == "__main__":
    a = sys.argv[1:]
    out = os.path.join(HERE, "MEASURE_1113.md")
    if "--out" in a:
        out = a[a.index("--out") + 1]
    run(a[0], out)
