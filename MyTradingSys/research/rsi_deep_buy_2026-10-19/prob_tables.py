"""RSI deep-buy probability tables, DEV then VALIDATION (SPEC.md s2 Steps D-E, OPUS_FRAMING s4; card rsi-deep-prob-tables).

Per RSI timeframe t, anchor window W (non-overlapping UTC blocks, complete only), level L and visit number n of L inside
the window (hysteresis h=3, window starts armed; visit 3 = third or later) it estimates, for each visit event
(known at the signal bar's close, fill = next bar's open):
  D  P(deeper): RSI closes <= L-d at a later bar of the same window, d in 1,2,3,5
  E  P(RSI bounce): RSI rises b points off its running minimum before the running minimum is >= 3 points under the entry
     RSI (b in 3,5,10; unresolved by the window end = excluded from n); P(price bounce): open[i+1+H]/open[i+1]-1 > fee;
     quantiles p10/p25/p50/p75/p90 of that return and p10/p50/p90 of the adverse move MAE = min low over the H bars / fill - 1
  S  survival S(n) = P(no bar low below the signal bar's low within n bars), Kaplan-Meier, n in 1,5,15,60 (OPUS_FRAMING s4.1)
Every proportion carries Wilson 95% on the event count and on the effective count = distinct UTC days of the events
(lo_d/hi_d, k scaled to the day count: events of one day cluster). Rarity = p_touch (windows with >=1 visit / windows).

Run: python prob_tables.py --pass dev   (writes prob_tables_dev.csv; refuses any bar open >= 2024-07-01)
     python prob_tables.py --pass val   (needs the frozen dev csv; reads 2024-07..2025-06 ONCE; refuses >= 2025-07 HOLDOUT)

Labels. SOURCED: RSI14 Wilder on close, UTC, taker fee 0.10% round trip (econ_floor.FEE <- backtest/fees.py), DEV cutoff
2024-07-01 and HOLDOUT from 2025-07-01 (SPEC s5), Wilson interval (z=1.96), Kaplan-Meier. OURS: h=3, level grid, d/b/H/n grids,
d=3 for the bounce race, visit buckets 1/2/3+, signal-bar low as the survival reference, windows 1h/4h/1d/1w and TFs 1m/5m/15m/1h,
day clustering, window must start at/after the cutoff for VALIDATION rows.
"""
import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import econ_floor as ef  # noqa: E402

CUTOFF_MS = ef.CUTOFF_MS
HOLDOUT_MS = int(np.datetime64("2025-07-01T00:00", "ms").astype("int64"))
FEE = ef.FEE
Z = 1.96
TFS = (1, 5, 15, 60)
WINS = (60, 240, 1440, 10080)
LEVELS = (10, 15, 20, 25, 30, 35, 40)
HYST = 3.0
DS = (1, 2, 3, 5)
BS = (3, 5, 10)
RACE_D = 3.0
HS = (1, 5, 15, 60)
FIXED_MIN = (15, 60, 240)
SURV_GRID = (1, 5, 15, 60)
MIN_MS = 60_000
DAY_MS = 86_400_000
WEEK_OFFSET_MS = 4 * DAY_MS
RET_Q = (10, 25, 50, 75, 90)
MAE_Q = (10, 50, 90)
FIELDS = ["tf_min", "win_min", "level", "visit", "metric", "param", "n_events", "n_days", "k", "p", "lo", "hi",
          "lo_d", "hi_d", "value", "n_windows", "p_touch"]


def assert_dev(d):
    if len(d["open_time"]) and np.asarray(d["open_time"]).max() >= CUTOFF_MS:
        raise ValueError("bar with open >= DEV cutoff 2024-07-01 refused")


def assert_val(d):
    if len(d["open_time"]) and np.asarray(d["open_time"]).max() >= HOLDOUT_MS:
        raise ValueError("bar with open >= 2025-07-01 (HOLDOUT) refused")


def wilson(k, n, z=Z):
    if n <= 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - m) / den), min(1.0, (c + m) / den)


def window_ids(t, rsi, tf, win):
    """Per-bar window id (-1 = bar not in a complete window with defined RSI) and window start ms per id."""
    off = WEEK_OFFSET_MS if win == 10080 else 0
    wms = win * MIN_MS
    g = (t - off) // wms
    ug, start, cnt = np.unique(g, return_index=True, return_counts=True)
    need = win // tf
    wid = np.full(len(t), -1, dtype="int64")
    starts = []
    for u, s, c in zip(ug, start, cnt):
        if c != need or np.isnan(rsi[s:s + c]).any():
            continue
        wid[s:s + c] = len(starts)
        starts.append(u * wms + off)
    return wid, np.array(starts, dtype="int64")


def visit_events(rsi, wid, level, h=HYST):
    """(bar indices, visit numbers): RSI closes <= level while armed; re-arm when RSI >= level+h; window start = armed."""
    r = np.asarray(rsi, dtype="float64")
    dec = np.where((r <= level) | (r >= level + h))[0]
    idx, vn = [], []
    cur, armed, cnt = -2, True, 0
    for i in dec:
        w = wid[i]
        if w < 0:
            continue
        if w != cur:
            cur, armed, cnt = w, True, 0
        if r[i] >= level + h:
            armed = True
        elif armed:
            cnt += 1
            idx.append(i)
            vn.append(cnt)
            armed = False
    return np.array(idx, dtype="int64"), np.array(vn, dtype="int64")


def suffix_min_after(rsi, wid):
    """Per bar: min RSI over later bars of the same window (inf if none)."""
    r = np.asarray(rsi, dtype="float64")
    out = np.full(len(r), np.inf)
    n = len(r)
    i = 0
    while i < n:
        if wid[i] < 0:
            i += 1
            continue
        j = i
        while j < n and wid[j] == wid[i]:
            j += 1
        seg = r[i:j]
        rev = np.minimum.accumulate(seg[::-1])[::-1]
        out[i:j - 1] = rev[1:]
        i = j
    return out


def rsi_race(rsi, ev, wid, b, d=RACE_D):
    """1.0 = RSI rose b points off its running minimum first, 0.0 = running minimum fell d below the entry RSI first,
    nan = neither by the window end."""
    out = np.full(len(ev), np.nan)
    n = len(rsi)
    for q, i in enumerate(ev):
        e0 = rsi[i]
        m = e0
        j = i + 1
        while j < n and wid[j] == wid[i]:
            if rsi[j] >= m + b:
                out[q] = 1.0
                break
            m = min(m, rsi[j])
            if m <= e0 - d:
                out[q] = 0.0
                break
            j += 1
    return out


def price_outcomes(open_, low, ev, H):
    """(gross return open[i+1+H]/open[i+1]-1, MAE = min(low[i+1..i+H])/open[i+1]-1); nan if the exit is beyond the data."""
    ev = np.asarray(ev, dtype="int64")
    n = len(open_)
    ret = np.full(len(ev), np.nan)
    mae = np.full(len(ev), np.nan)
    ok = ev + 1 + H < n
    e = ev[ok]
    fill = open_[e + 1]
    ret[ok] = open_[e + 1 + H] / fill - 1.0
    cols = e[:, None] + 1 + np.arange(H)[None, :]
    mae[ok] = low[cols].min(axis=1) / fill - 1.0
    return ret, mae


def first_lower_low(low, ev, horizon=max(SURV_GRID), chunk=40000):
    """(first bar offset 1..horizon with low < signal-bar low, else inf ; available bars min(horizon, n-1-i))."""
    ev = np.asarray(ev, dtype="int64")
    n = len(low)
    first = np.full(len(ev), np.inf)
    avail = np.minimum(horizon, n - 1 - ev)
    for a in range(0, len(ev), chunk):
        e = ev[a:a + chunk]
        cols = np.minimum(e[:, None] + 1 + np.arange(horizon)[None, :], n - 1)
        hit = low[cols] < low[e][:, None]
        hit &= (np.arange(1, horizon + 1)[None, :] <= (n - 1 - e)[:, None])
        anyhit = hit.any(axis=1)
        first[a:a + chunk] = np.where(anyhit, hit.argmax(axis=1) + 1, np.inf)
    return first, avail


def km_survival(first, avail, grid):
    first, avail = np.asarray(first, dtype="float64"), np.asarray(avail, dtype="int64")
    if len(first) == 0:
        return [float("nan")] * len(grid)
    obs = first <= avail
    dur = np.where(obs, first, avail).astype("int64")
    tmax = max(grid)
    dead = np.bincount(dur[obs], minlength=tmax + 2)[:tmax + 2]
    allc = np.bincount(dur, minlength=tmax + 2)[:tmax + 2]
    s, surv, risk = 1.0, {}, len(dur)
    for t in range(1, tmax + 1):
        if risk > 0:
            s *= 1 - dead[t] / risk
        risk -= allc[t]
        surv[t] = s
    return [surv[g] for g in grid]


def _prop_row(base, metric, param, flags, days):
    n = int(len(flags))
    k = int(np.sum(flags))
    p = k / n if n else float("nan")
    nd = int(len(np.unique(days))) if n else 0
    lo, hi = wilson(k, n)
    lod, hid = wilson(round(p * nd), nd) if n else (float("nan"), float("nan"))
    return {**base, "metric": metric, "param": param, "n_events": n, "n_days": nd, "k": k, "p": p, "lo": lo, "hi": hi,
            "lo_d": lod, "hi_d": hid}


def _val_row(base, metric, param, x, days, v):
    return {**base, "metric": metric, "param": param, "n_events": int(len(x)),
            "n_days": int(len(np.unique(days))) if len(x) else 0, "value": v}


def analyse_cell(base, d, ev, rsi, wid, sufmin, level, t_ev, hs):
    """All rows for one (tf, win, level, visit-bucket) cell. `ev` = event bar indices of the cell."""
    rows = []
    days = t_ev // DAY_MS
    if len(ev) == 0:
        return rows
    for dd in DS:
        rows.append(_prop_row(base, "p_deeper", f"d{dd}", sufmin[ev] <= level - dd, days))
    for b in BS:
        res = rsi_race(rsi, ev, wid, b)
        ok = ~np.isnan(res)
        rows.append(_prop_row(base, "p_rsi_bounce", f"b{b}", res[ok] == 1.0, days[ok]))
    for H in hs:
        ret, mae = price_outcomes(d["open"], d["low"], ev, H)
        ok = ~np.isnan(ret)
        rows.append(_prop_row(base, "p_price_bounce", f"H{H}", ret[ok] > FEE, days[ok]))
        for q in RET_Q:
            rows.append(_val_row(base, f"ret_q{q}", f"H{H}", ret[ok], days[ok],
                                 float(np.percentile(ret[ok], q)) if ok.any() else float("nan")))
        for q in MAE_Q:
            rows.append(_val_row(base, f"mae_q{q}", f"H{H}", mae[ok], days[ok],
                                 float(np.percentile(mae[ok], q)) if ok.any() else float("nan")))
    first, avail = first_lower_low(d["low"], ev)
    for g, s in zip(SURV_GRID, km_survival(first, avail, SURV_GRID)):
        full = avail >= g
        nf = int(full.sum())
        kf = int((full & ~(first <= g)).sum())
        lo, hi = wilson(kf, nf)
        rows.append({**base, "metric": "S", "param": f"n{g}", "n_events": int(len(ev)),
                     "n_days": int(len(np.unique(days))), "k": kf, "p": s, "lo": lo, "hi": hi})
    return rows


def horizons(tf):
    hs = set(HS)
    for m in FIXED_MIN:
        if m % tf == 0:
            hs.add(m // tf)
    return sorted(hs)


def run_tf(d1, tf, start_ms):
    """Rows for one RSI timeframe on the loaded 1m dict `d1`; only windows starting at/after start_ms."""
    d = ef.resample(d1, tf)
    rsi = ef.rsi_series(d["close"])
    t = d["open_time"]
    rows = []
    for win in WINS:
        if win <= tf:
            continue
        wid, starts = window_ids(t, rsi, tf, win)
        keep = np.where(starts >= start_ms)[0]
        wid = np.where(np.isin(wid, keep), wid, -1)
        n_win = int(len(keep))
        sufmin = suffix_min_after(rsi, wid)
        for L in LEVELS:
            ev_all, vn_all = visit_events(rsi, wid, float(L))
            for vb in (1, 2, 3):
                m = (vn_all == vb) if vb < 3 else (vn_all >= 3)
                ev = ev_all[m]
                base = {"tf_min": tf, "win_min": win, "level": L, "visit": vb if vb < 3 else "3+", "n_windows": n_win,
                        "p_touch": (len(ev) / n_win if (vb == 1 and n_win) else "")}
                rows.extend(analyse_cell(base, d, ev, rsi, wid, sufmin, L, t[ev], horizons(tf)))
        print(f"tf={tf}m win={win}m windows={n_win} rows={len(rows)}", flush=True)
    return rows


def month_files(klines, last_ym):
    out = []
    for p in sorted(Path(klines).glob("BTCUSDT-1m-*.csv")):
        mo = re.fullmatch(r"BTCUSDT-1m-(\d{4}-\d{2})\.csv", p.name)
        if mo and mo.group(1) <= last_ym:
            out.append(p)
    return out


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v)
                        for k, v in {f: r.get(f, "") for f in FIELDS}.items()})


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


PROP = ("p_deeper", "p_rsi_bounce", "p_price_bounce", "S")
MIN_DAYS = 30                           # OPUS_FRAMING s4.5 / SPEC Step F: a cell needs >= 30 independent days
TFN = {"1": "1m", "5": "5m", "15": "15m", "60": "1h"}
WN = {"60": "1h", "240": "4h", "1440": "1d", "10080": "1w"}


def read_cells(path):
    out = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            out[(r["tf_min"], r["win_min"], r["level"], r["visit"], r["metric"], r["param"])] = r
    return out


def _f(x):
    return float(x) if x not in ("", None) else float("nan")


def compare(dev, val):
    """Per proportion cell with >= MIN_DAYS DEV days and >= 1 VALIDATION event: inside or outside the DEV day-based
    Wilson interval (S: the event Wilson interval, S carries no day interval)."""
    res = []
    for key, d in dev.items():
        if key[4] not in PROP or key not in val:
            continue
        v = val[key]
        if int(d["n_days"]) < MIN_DAYS or int(v["n_events"]) == 0:
            continue
        lo, hi = (_f(d["lo"]), _f(d["hi"])) if key[4] == "S" else (_f(d["lo_d"]), _f(d["hi_d"]))
        pv = _f(v["p"])
        res.append({"key": key, "dev_p": _f(d["p"]), "val_p": pv, "lo": lo, "hi": hi, "n_dev_days": int(d["n_days"]),
                    "n_val_days": int(v["n_days"]), "n_val": int(v["n_events"]), "outside": not (lo <= pv <= hi)})
    return res


def _ladder(dev, L):
    L.append("\n## DEV ladder, 1m RSI inside a 1d window, visit 1 (cell = p [Wilson-day lo, hi] (n_days); S = KM value (n events))\n")
    L.append("| level | p_deeper d3 | p_rsi_bounce b5 | p_price_bounce H15 | p_price_bounce H60 | S n15 | S n60 |\n|---|---|---|---|---|---|---|")
    for lv in ("10", "15", "20", "25", "30", "35", "40"):
        cells = []
        for m, pa in (("p_deeper", "d3"), ("p_rsi_bounce", "b5"), ("p_price_bounce", "H15"), ("p_price_bounce", "H60"),
                      ("S", "n15"), ("S", "n60")):
            r = dev.get(("1", "1440", lv, "1", m, pa))
            if not r:
                cells.append("n/a")
            elif m == "S":
                cells.append(f"{_f(r['p']):.3f} (n {r['n_events']})")
            else:
                cells.append(f"{_f(r['p']):.3f} [{_f(r['lo_d']):.3f},{_f(r['hi_d']):.3f}] ({r['n_days']}d)")
        L.append(f"| {lv} | " + " | ".join(cells) + " |")
    L.append("\n## Price bounce size and adverse move (1m RSI, 1d window, visit 1, H60 = 1 hour after the fill; DEV)\n")
    L.append("| level | ret p10 | ret p50 | ret p90 | MAE p10 | MAE p50 | MAE p90 |\n|---|---|---|---|---|---|---|")
    for lv in ("10", "20", "30", "40"):
        vals = []
        for m in ("ret_q10", "ret_q50", "ret_q90", "mae_q10", "mae_q50", "mae_q90"):
            r = dev.get(("1", "1440", lv, "1", m, "H60"))
            vals.append(f"{100 * _f(r['value']):+.2f}%" if r else "n/a")
        L.append(f"| {lv} | " + " | ".join(vals) + " |")


def write_report(out):
    dev, val = read_cells(out / "prob_tables_dev.csv"), read_cells(out / "prob_tables_val.csv")
    cmp_ = compare(dev, val)
    L = ["# RSI deep-buy probability tables (card rsi-deep-prob-tables, SPEC s2 Steps D-E, OPUS_FRAMING s4)\n"]
    L.append("Data: BTCUSDT 1m. DEV = open < 2024-07-01 (`prob_tables_dev.csv`, written and frozen first, sha256 "
             f"`{sha256(out / 'prob_tables_dev.csv')[:16]}`). VALIDATION = windows starting 2024-07-01..2025-06-30, read once "
             "(`prob_tables_val.csv`). HOLDOUT (2025-07 onward) is refused by the loader and was never read. Generated by "
             "`prob_tables.py`; test: `test_prob_tables.py`. Descriptive probabilities, not a trading rule; no fee-net edge is claimed.\n")
    L.append("How to read a cell: event = RSI closes at or below level L (after being 3+ above, once per window per visit); "
             "fill = next bar open. `p_deeper dK` = RSI closes <= L-K later in the same window. `p_rsi_bounce bB` = RSI rises B points "
             "off its running minimum before that minimum is 3 below the entry RSI (windows ending unresolved are excluded). "
             "`p_price_bounce H` = open[i+1+H]/open[i+1]-1 exceeds the 0.10% round-trip fee, H in bars of the RSI timeframe "
             "(H15/H60/H240 on 1m are 15m/1h/4h). `S nK` = Kaplan-Meier P(no bar low under the signal bar's low within K bars). "
             "Every proportion row has n_events, n_days, Wilson 95% (event count: lo/hi; day count, the honest one: lo_d/hi_d). "
             "Quantiles `ret_q*` and `mae_q*` (adverse move before the exit) are rows with a `value`. "
             "Events of one day cluster, so judge by n_days, not n_events.\n")
    L.append("## Rarity: share of windows that touch the level at least once (visit-1 events / windows), DEV vs VALIDATION\n")
    L.append("| RSI TF | window | level | DEV p_touch | DEV windows | VAL p_touch | VAL windows |\n|---|---|---|---|---|---|---|")
    for tf in ("1", "15", "60"):
        for win in ("240", "1440", "10080"):
            for lv in ("10", "20", "30", "40"):
                k = (tf, win, lv, "1", "p_deeper", "d1")
                if k in dev and k in val:
                    L.append(f"| {TFN[tf]} | {WN[win]} | {lv} | {_f(dev[k]['p_touch']):.4f} | {dev[k]['n_windows']} | "
                             f"{_f(val[k]['p_touch']):.4f} | {val[k]['n_windows']} |")
    _ladder(dev, L)
    L.append(f"\n## VALIDATION calibration (predicted = DEV interval, realised = VALIDATION value; cells with >= {MIN_DAYS} DEV days)\n")
    L.append("A cell is `outside` when the VALIDATION proportion falls outside the DEV 95% interval (day-based Wilson; S: event Wilson). "
             "Outside cells are not tradeable on this evidence. About 5% outside is expected by chance alone; much more means drift.\n")
    L.append("| metric | RSI TF | cells compared | outside | share outside |\n|---|---|---|---|---|")
    for m in PROP:
        for tf in ("1", "5", "15", "60"):
            c = [x for x in cmp_ if x["key"][4] == m and x["key"][0] == tf]
            if c:
                o = sum(x["outside"] for x in c)
                L.append(f"| {m} | {TFN[tf]} | {len(c)} | {o} | {o / len(c):.1%} |")
    tot_o = sum(x["outside"] for x in cmp_)
    L.append(f"\nAll metrics: {len(cmp_)} cells compared, {tot_o} outside ({tot_o / max(len(cmp_), 1):.1%}).\n")
    pb = [x for x in cmp_ if x["key"][4] == "p_price_bounce"]
    po = sum(x["outside"] for x in pb)
    L.append(f"Price-bounce cells (the tradeable probability): {len(pb)} compared, {po} outside ({po / max(len(pb), 1):.1%}).\n")
    L.append("Largest drifts among outside cells with >= 30 VALIDATION days (|VAL - DEV|, top 15):\n")
    L.append("| TF | window | level | visit | metric | param | DEV p | DEV interval | VAL p | VAL days |\n|---|---|---|---|---|---|---|---|---|---|")
    big = sorted((x for x in cmp_ if x["outside"] and x["n_val_days"] >= MIN_DAYS), key=lambda x: -abs(x["val_p"] - x["dev_p"]))[:15]
    for x in big:
        k = x["key"]
        L.append(f"| {TFN[k[0]]} | {WN[k[1]]} | {k[2]} | {k[3]} | {k[4]} | {k[5]} | {x['dev_p']:.3f} | "
                 f"[{x['lo']:.3f},{x['hi']:.3f}] | {x['val_p']:.3f} | {x['n_val_days']} |")
    L.append("\n## Price-bounce cells at or above 55% in DEV (>= 30 days) that stayed inside their interval in VALIDATION\n")
    L.append("Listed only to show where the probability is high. A bounce share above 55% is not an edge by itself: fee-net EV also needs the "
             "size and MAE columns and the multiple-testing count below.\n")
    held = [x for x in pb if x["dev_p"] >= 0.55 and not x["outside"]]
    L.append(f"{len(held)} of {len(pb)} compared price-bounce cells; first 10 by DEV p:\n")
    L.append("| TF | window | level | visit | H | DEV p | VAL p | DEV days | VAL days |\n|---|---|---|---|---|---|---|---|---|")
    for x in sorted(held, key=lambda x: -x["dev_p"])[:10]:
        k = x["key"]
        L.append(f"| {TFN[k[0]]} | {WN[k[1]]} | {k[2]} | {k[3]} | {k[5]} | {x['dev_p']:.3f} | {x['val_p']:.3f} | "
                 f"{x['n_dev_days']} | {x['n_val_days']} |")
    L.append("""
## Parameters (SOURCED vs OURS)

SOURCED: RSI14 Wilder on close, UTC alignment, complete bars (econ_floor.py, FORMULAS.md s1); fee 0.10% round trip (backtest/fees.py);
DEV cutoff 2024-07-01 and HOLDOUT start 2025-07-01 (SPEC s5); Wilson 95% (z = 1.96); Kaplan-Meier survival; at least 30 independent days per cell (OPUS_FRAMING s4.5).
OURS (every one is a trial row in layer_lab/TRIALS.md, none tuned on VALIDATION): hysteresis h = 3; levels 10..40 step 5;
visit buckets 1, 2, 3+; d in 1,2,3,5; b in 3,5,10; bounce-race fall-back d = 3; H in 1,5,15,60 bars plus 15m/1h/4h where the TF divides them;
survival reference = the signal bar's low, n in 1,5,15,60 bars; windows 1h/4h/1d/1w (weeks start Monday 00:00 UTC); TFs 1m/5m/15m/1h;
a window enters VALIDATION only if it starts on or after 2024-07-01; RSI warm-up uses the earlier months (same series as one continuous run).

## Caveats

- Look-ahead: the event (level, visit number) is known at the signal bar close; outcomes (deeper, bounce, price, survival) are labels measured after it, never used as conditions.
- Overlap: events inside one day and consecutive windows are correlated; the day-based interval is the one to use, and it is still optimistic across adjacent days.
- Multiple testing: thousands of cells are tabulated (grid in TRIALS.md); a few high-probability cells appear by chance. No Holm correction is applied because no cell is selected as a rule.
- p_rsi_bounce is close to mechanical (RSI mean-reverts); the price columns carry the verdict. Hourly RSI timeframes have few events.
- Context (Step F) is the next card (rsi-deep-context-tables); this file is the F0 unconditional baseline.
""")
    Path(out / "PROB_REPORT.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("wrote PROB_REPORT.md", len(cmp_), "cells compared,", tot_o, "outside")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="which", choices=("dev", "val", "report"), required=True)
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if a.which == "report":
        write_report(out)
        return
    if a.which == "dev":
        d1 = ef.load_klines(month_files(a.klines, "2024-06"))
        assert_dev(d1)
        start = 0
        dest = out / "prob_tables_dev.csv"
    else:
        if not (out / "prob_tables_dev.csv").exists():
            raise SystemExit("prob_tables_dev.csv must be written before the VALIDATION read")
        # RSI is recursive: DEV months are loaded as warm-up (same series); only windows starting >= cutoff are kept.
        d1 = ef.load_klines(month_files(a.klines, "2025-06"), cutoff_ms=HOLDOUT_MS)
        assert_val(d1)
        start = CUTOFF_MS
        dest = out / "prob_tables_val.csv"
        print("dev csv sha256", sha256(out / "prob_tables_dev.csv"))
    rows = []
    for tf in TFS:
        rows.extend(run_tf(d1, tf, start))
    write_csv(rows, dest)
    print("rows", len(rows), "->", dest)


if __name__ == "__main__":
    main()
