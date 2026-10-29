"""Layer relations study (descriptive, DEV only): Binance BTCUSDT-PERP 5m taker delta, open interest and
long/short ratios, per market phase. Card: layer-relations-concepts-us-open. No edge claim, no trade advice.

Inputs (public data.binance.vision archive, fetched by MyTradingSys/backtest/fetch_binance_archive.py):
  Dumps/backtest/raw/klines/BTCUSDT-5m-YYYY-MM.csv      (fetch with --interval 5m)
  Dumps/backtest/raw/metrics/BTCUSDT-metrics-YYYY-MM-DD.csv
Fetch (DEV only):
  python MyTradingSys/backtest/fetch_binance_archive.py --start 2022-01-01 --end 2024-06-30 --datasets klines --interval 5m
  python MyTradingSys/backtest/fetch_binance_archive.py --start 2022-01-01 --end 2024-06-30 --datasets metrics
Run:  python MyTradingSys/research/layer_relations_2026-10/layer_relations_study.py [--raw Dumps/backtest/raw] [--out FILE]

DEV bounds: 2022-01-01 .. 2024-06-30 UTC, end exclusive 2024-07-01 (backtest/layers/krown/run_counts.py:29,
cc_htf_count.py:28-29, OPERATOR_DECISIONS.md:878). Nothing at or after DEV_END is kept (asserted in load()).
Every computed number is OURS (computed here from SOURCED archive columns). Phase hours are OURS.
"""
import argparse
import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DEV_START = pd.Timestamp("2022-01-01", tz="UTC")
DEV_END = pd.Timestamp("2024-07-01", tz="UTC")  # exclusive
STEP = pd.Timedelta("5min")
RATIO_COLS = {
    "TA": "count_toptrader_long_short_ratio",  # top-trader ACCOUNTS long/short ratio
    "TP": "sum_toptrader_long_short_ratio",    # top-trader POSITIONS long/short ratio
    "GA": "count_long_short_ratio",            # global (all) ACCOUNTS long/short ratio
    "TK": "sum_taker_long_short_vol_ratio",    # taker buy/sell volume ratio
}
PHASES = ["Asia", "London", "PreOpen", "USOpen", "USPM", "Late"]
PHASE_DEF = {
    "Asia": "00:00-07:00 UTC",
    "London": "07:00 UTC to 08:30 ET (EDT 12:30 UTC, EST 13:30 UTC)",
    "PreOpen": "08:30-09:30 ET (the hour before the NYSE cash open)",
    "USOpen": "09:30-11:30 ET (EDT 13:30-15:30 UTC, EST 14:30-16:30 UTC)",
    "USPM": "11:30 ET to 21:00 UTC",
    "Late": "21:00-24:00 UTC",
}
LAGS = list(range(-12, 13))
PAIRS_WIN = [("R", "D"), ("R", "dOI"), ("D", "dOI"), ("R", "dTA"), ("R", "dTP"), ("R", "dGA"),
             ("D", "dTP"), ("dOI", "dTP"), ("dOI", "dTA"), ("dTA", "dTP"), ("dGA", "dTP")]
PAIRS_LAG = [("D_b", "r"), ("D_b", "dOI"), ("r", "dOI"), ("D_b", "dTP"), ("r", "dTP"), ("r", "dTA"),
             ("dOI", "dTP"), ("dOI", "dTA"), ("dTA", "dTP")]
NAMES = {"R": "price chg", "D": "net delta share", "dOI": "OI chg", "dTA": "top-acct L/S chg",
         "dTP": "top-pos L/S chg", "dGA": "global-acct L/S chg", "r": "price chg", "D_b": "net delta share"}


def load(raw):
    raw = Path(raw)
    ks = []
    for f in sorted(glob.glob(str(raw / "klines" / "BTCUSDT-5m-*.csv"))):
        ks.append(pd.read_csv(f))
    k = pd.concat(ks, ignore_index=True)
    k["ts"] = pd.to_datetime(k["open_time"], unit="ms", utc=True)
    k = k[(k["ts"] >= DEV_START) & (k["ts"] < DEV_END)].drop_duplicates("ts").set_index("ts").sort_index()
    ms = []
    for f in sorted(glob.glob(str(raw / "metrics" / "BTCUSDT-metrics-*.csv"))):
        d = f.rsplit("metrics-", 1)[1][:10]
        if pd.Timestamp(d, tz="UTC") >= DEV_END:
            continue  # never open a file dated at/after DEV_END
        ms.append(pd.read_csv(f))
    m = pd.concat(ms, ignore_index=True)
    m["ts"] = pd.to_datetime(m["create_time"], utc=True)
    m = m[(m["ts"] >= DEV_START) & (m["ts"] < DEV_END)].drop_duplicates("ts").set_index("ts").sort_index()
    for c in ["sum_open_interest"] + list(RATIO_COLS.values()):
        m[c] = pd.to_numeric(m[c], errors="coerce")
        m.loc[m[c] <= 0, c] = np.nan  # a zero OI/ratio is a data hole, not a value
    assert k.index.max() < DEV_END and m.index.max() < DEV_END
    return k, m


def build_bars(k, m):
    """One row per 5m bar open b in [DEV_START, DEV_END-10min]. State series X(t) = metric at create_time t
    (snapshot at the END of the bar opening at t-5m: alignment A1, OURS, tested in alignment_check)."""
    g = pd.date_range(DEV_START, DEV_END - 2 * STEP, freq="5min")
    b = pd.DataFrame(index=g)
    kk = k.reindex(g)
    b["close"], b["open"], b["vol"], b["tbv"] = kk["close"], kk["open"], kk["volume"], kk["taker_buy_volume"]
    b["r"] = np.log(b["close"] / b["open"])
    b["delta"] = 2 * b["tbv"] - b["vol"]            # BTC, taker buy minus taker sell
    b["D_b"] = b["delta"] / b["vol"]                 # net delta share of volume, in [-1, 1]
    oi0, oi1 = m["sum_open_interest"].reindex(g), m["sum_open_interest"].reindex(g + STEP)
    oi1.index = g
    b["oi0"], b["oi1"] = oi0.values, oi1.values
    b["dOI"] = b["oi1"] / b["oi0"] - 1
    for key in ("TA", "TP", "GA", "TK"):
        s = m[RATIO_COLS[key]]
        s0, s1 = s.reindex(g), s.reindex(g + STEP)
        b[key + "0"], b[key + "1"] = s0.values, s1.values
    for key in ("TA", "TP", "GA"):
        b["d" + key] = np.log(b[key + "1"] / b[key + "0"])
    et = g.tz_convert("America/New_York")
    etm = (et.hour * 60 + et.minute).to_numpy()
    um = (g.hour * 60 + g.minute).to_numpy()
    b["phase"] = np.select(
        [um < 420, um >= 1260, (etm >= 570) & (etm < 690), (etm >= 510) & (etm < 570), etm >= 690],
        ["Asia", "Late", "USOpen", "PreOpen", "USPM"], default="London")
    b["wkday"] = g.dayofweek < 5
    b["date"] = g.date
    b["half"] = [f"{x.year}H{1 if x.month <= 6 else 2}" for x in g]
    return b


def spearman(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    n = len(d)
    if n < 10 or d["x"].nunique() < 2 or d["y"].nunique() < 2:
        return np.nan, n
    return d["x"].rank().corr(d["y"].rank()), n


def windows(b):
    """One row per (date, phase) window. R = sum of bar log returns; D = window net delta / window volume;
    OI and ratio changes are end-state vs start-state of the window."""
    grp = b.groupby(["date", "phase"], sort=True)
    w = pd.DataFrame({
        "wkday": grp["wkday"].first(), "half": grp["half"].first(),
        "nbar": grp.size(), "nk": grp["vol"].count(),
        "R": grp["r"].sum(min_count=1),
        "dsum": grp["delta"].sum(min_count=1), "vsum": grp["vol"].sum(min_count=1),
        "oi_s": grp["oi0"].first(), "oi_e": grp["oi1"].last(),
    })
    for key in ("TA", "TP", "GA"):
        w[key + "_s"], w[key + "_e"] = grp[key + "0"].first(), grp[key + "1"].last()
        w["d" + key] = np.log(w[key + "_e"] / w[key + "_s"])
    w["D"] = w["dsum"] / w["vsum"]
    w["dOI"] = w["oi_e"] / w["oi_s"] - 1
    w = w[w["nk"] >= 0.95 * w["nbar"]]
    w = w.reset_index()
    return w


def band(n):
    return 1.96 / np.sqrt(max(n - 3, 1))  # approx 95% null band for a correlation (OURS; no multiplicity fix)


def fmt_rho(rho, n):
    if np.isnan(rho):
        return "n/a"
    star = "*" if abs(rho) > band(n) else ""
    return f"{rho:+.2f}{star} ({n})"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def sgn(x):
    return np.sign(x)


def run(raw):
    k, m = load(raw)
    b = build_bars(k, m)
    w = windows(b)
    out = []
    P = out.append

    # --- coverage
    P("## C1 Data coverage (DEV 2022-01-01..2024-06-30 UTC)")
    P(f"- kline 5m bars loaded: {len(k)} (expected {(DEV_END - DEV_START) // STEP}); metrics 5m rows loaded: {len(m)}.")
    cov = []
    mm = m.copy()
    mm["ym"] = mm.index.strftime("%Y-%m")
    for ym, grp in mm.groupby("ym"):
        n = len(grp)
        cov.append([ym, n] + [f"{grp[c].notna().mean() * 100:.0f}%" for c in
                              ["sum_open_interest", RATIO_COLS['TA'], RATIO_COLS['TP'], RATIO_COLS['GA'], RATIO_COLS['TK']]])
    P(md_table(["month", "metric rows", "OI", "top-acct", "top-pos", "global-acct", "taker ratio"], cov))
    P("")
    wk = b[b["wkday"]]
    allr = b[["r", "D_b", "dOI", "dTA", "dTP", "dGA"]]
    P("Bars with each series non-null (all DEV bars, n = %d): " % len(b) + ", ".join(
        f"{c} {allr[c].notna().sum()} ({allr[c].notna().mean() * 100:.0f}%)" for c in allr.columns))
    P("Share of non-null 5m ratio changes that are exactly 0 (ratio unchanged between snapshots): " + ", ".join(
        f"{c} {(b[c].dropna() == 0).mean() * 100:.0f}%" for c in ["dTA", "dTP", "dGA"]))
    P("")

    # --- alignment check
    P("## C2 Alignment check (decides how a metrics snapshot maps to a kline bar)")
    rows = []
    gi = b.index
    for s in (-1, 0, 1, 2):
        oi = m["sum_open_interest"]
        a = oi.reindex(gi + (s + 1) * STEP).values / oi.reindex(gi + s * STEP).values - 1
        tk = np.log(m[RATIO_COLS["TK"]].reindex(gi + (s + 1) * STEP).values)
        r1, n1 = spearman(pd.Series(np.abs(b["r"].values)), pd.Series(np.abs(a)))
        r2, n2 = spearman(pd.Series(b["D_b"].values), pd.Series(tk))
        rows.append([s, f"{r1:+.3f} ({n1})", f"{r2:+.3f} ({n2})"])
    P(md_table(["shift s (bars)", "Spearman |price chg| vs |OI chg|", "Spearman net delta share vs ln(taker ratio)"], rows))
    P("Shift 0 = snapshot at create_time t belongs to the bar that opened at t-5min (A1). The row with the highest value is the alignment this archive follows.")
    P("")

    # --- window counts
    wk_w = w[w["wkday"]]
    P("## C3 Windows used (phase-day, weekdays; a window needs >=95% of its kline bars)")
    cnt = []
    for ph in PHASES:
        x = wk_w[wk_w["phase"] == ph]
        cnt.append([ph, PHASE_DEF[ph], len(x), int(x["dOI"].notna().sum()), int(x["dTA"].notna().sum()),
                    int(x["dTP"].notna().sum()), int(x["dGA"].notna().sum())])
    wend = w[~w["wkday"] & (w["phase"] == "USOpen")]
    cnt.append(["USOpen (weekend control)", "same clock hours, Sat/Sun UTC (no cash market)", len(wend),
                int(wend["dOI"].notna().sum()), int(wend["dTA"].notna().sum()), int(wend["dTP"].notna().sum()), int(wend["dGA"].notna().sum())])
    P(md_table(["phase", "definition (OURS)", "windows", "with OI", "with top-acct", "with top-pos", "with global-acct"], cnt))
    P("")

    # --- co-movement
    P("## T1 Co-movement per phase: Spearman rho of window changes (n windows); * = outside approx 95% null band 1.96/sqrt(n-3), no multiplicity correction")
    rows = []
    for a, c in PAIRS_WIN:
        row = [f"{NAMES[a]} vs {NAMES[c]}"]
        for ph in PHASES:
            x = wk_w[wk_w["phase"] == ph]
            row.append(fmt_rho(*spearman(x[a], x[c])))
        row.append(fmt_rho(*spearman(wend[a], wend[c])))
        rows.append(row)
    P(md_table(["pair"] + PHASES + ["USOpen weekend ctrl"], rows))
    P("")

    # --- bar-level co-movement
    P("## T2 Co-movement at 5m bars, pooled within phase (weekdays): Spearman rho (n bars). Bars are autocorrelated, so * is not reliable here; read size, not stars")
    rows = []
    for a, c in [("r", "D_b"), ("r", "dOI"), ("D_b", "dOI"), ("r", "dTA"), ("r", "dTP"), ("D_b", "dTP"), ("dOI", "dTP"), ("dTA", "dTP")]:
        row = [f"{NAMES.get(a, a)} vs {NAMES.get(c, c)}"]
        for ph in PHASES:
            x = wk[wk["phase"] == ph]
            rho, n = spearman(x[a], x[c])
            row.append("n/a" if np.isnan(rho) else f"{rho:+.2f} ({n})")
        rows.append(row)
    P(md_table(["pair"] + PHASES, rows))
    P("")

    # --- divergence
    P("## T3 Divergence counts per phase (weekday windows). Share = windows where the two signs differ; 50% = no relation (OURS reading)")
    rows = []

    def diverge(x, a, c):
        d = x[[a, c]].dropna()
        d = d[(d[a] != 0) & (d[c] != 0)]
        if len(d) == 0:
            return "n/a"
        s = int((sgn(d[a]) != sgn(d[c])).sum())
        return f"{s}/{len(d)} = {100 * s / len(d):.0f}%"

    for a, c, lab in [("R", "D", "price vs net delta"), ("R", "dOI", "price vs OI"), ("R", "dTP", "price vs top-pos L/S"),
                      ("R", "dTA", "price vs top-acct L/S"), ("dTA", "dTP", "top-acct vs top-pos L/S"),
                      ("dGA", "dTP", "global-acct vs top-pos L/S"), ("D", "dOI", "net delta vs OI")]:
        row = [lab]
        for ph in PHASES:
            row.append(diverge(wk_w[wk_w["phase"] == ph], a, c))
        row.append(diverge(wend, a, c))
        rows.append(row)
    P(md_table(["sign differs"] + PHASES + ["USOpen weekend ctrl"], rows))
    P("")
    P("### T3b Price/OI four states per phase (weekday windows; counts)")
    rows = []
    for ph in PHASES + ["USOpen weekend ctrl"]:
        x = wend if ph.endswith("ctrl") else wk_w[wk_w["phase"] == ph]
        d = x[["R", "dOI"]].dropna()
        d = d[(d["R"] != 0) & (d["dOI"] != 0)]
        up, dn = d["R"] > 0, d["R"] < 0
        oiu, oid = d["dOI"] > 0, d["dOI"] < 0
        rows.append([ph, len(d), int((up & oiu).sum()), int((up & oid).sum()), int((dn & oiu).sum()), int((dn & oid).sum())])
    P(md_table(["phase", "n", "price up, OI up", "price up, OI down", "price down, OI up", "price down, OI down"], rows))
    P("")

    # --- lead-lag
    P("## T4 Lead-lag at 5m bars within phase (weekdays). Spearman corr(x_t, y_t+k), same window only; k>0 = x leads y. as: rho at k=0; peak |rho| lag and value; n bars at k=0")
    rows = []
    for a, c in PAIRS_LAG:
        row = [f"{NAMES.get(a, a)} -> {NAMES.get(c, c)}"]
        for ph in PHASES:
            x = wk[wk["phase"] == ph].copy()
            gk = x.groupby("date")
            res = {}
            for kk_ in LAGS:
                ys = gk[c].shift(-kk_)
                res[kk_] = spearman(x[a], ys)
            r0, n0 = res[0]
            valid = {kk_: v[0] for kk_, v in res.items() if not np.isnan(v[0])}
            if not valid:
                row.append("n/a")
                continue
            pk = max(valid, key=lambda z: abs(valid[z]))
            row.append(f"rho0 {r0:+.2f}; peak k={pk:+d} rho {valid[pk]:+.2f}; n={n0}")
        rows.append(row)
    P(md_table(["x -> y"] + PHASES, rows))
    P("Lags run -12..+12 bars (+-60 min). A peak at k=0 means no lead is visible at 5m; a peak at |k|>=1 is a candidate lead only if its rho is clearly bigger than rho at k=0 (OURS rule: gap >= 0.05).")
    P("")

    # --- stability for USOpen
    P("## T5 Stability of the US Open window co-movement by half-year (weekdays; Spearman, n)")
    rows = []
    halves = sorted(wk_w["half"].unique())
    for a, c in [("R", "D"), ("R", "dOI"), ("D", "dOI"), ("R", "dTP"), ("dOI", "dTP")]:
        row = [f"{NAMES[a]} vs {NAMES[c]}"]
        for h in halves:
            x = wk_w[(wk_w["phase"] == "USOpen") & (wk_w["half"] == h)]
            rho, n = spearman(x[a], x[c])
            row.append("n/a" if (np.isnan(rho) or n < 30) else f"{rho:+.2f} ({n})")
        rows.append(row)
    P(md_table(["pair"] + halves, rows))
    P("")

    # --- phase level descriptive
    P("## T6 What each phase looks like (weekday windows; median |window price chg| in bp, median |net delta share|, median |OI chg| in bp, median window volume in BTC)")
    rows = []
    for ph in PHASES:
        x = wk_w[wk_w["phase"] == ph]
        rows.append([ph, len(x), f"{(x['R'].abs().median() * 1e4):.0f}", f"{x['D'].abs().median():.3f}",
                     f"{(x['dOI'].abs().median() * 1e4):.0f}", f"{x['vsum'].median():.0f}",
                     f"{(x['dOI'].dropna() > 0).mean() * 100:.0f}%", f"{x['dOI'].mean() * 1e4:+.0f}"])
    P(md_table(["phase", "windows", "median abs price chg bp", "median abs net delta share", "median abs OI chg bp",
                "median volume BTC", "share windows OI up", "mean signed OI chg bp"], rows))
    P("")
    P("## T7 Carry-over between adjacent phases, same weekday: Spearman rho of window change in phase A vs the next phase B (n days)")
    order = ["Asia", "London", "PreOpen", "USOpen", "USPM", "Late"]
    piv = {v: wk_w.pivot(index="date", columns="phase", values=v) for v in ["R", "D", "dOI", "dTA", "dTP"]}
    rows = []
    for v in ["R", "D", "dOI", "dTA", "dTP"]:
        row = [NAMES[v]]
        for i in range(len(order) - 1):
            rho, n = spearman(piv[v][order[i]], piv[v][order[i + 1]])
            row.append(fmt_rho(rho, n))
        rows.append(row)
    P(md_table(["series"] + [f"{order[i]}->{order[i + 1]}" for i in range(len(order) - 1)], rows))
    P("")
    P("## T8 Does the PreOpen state go with what the US Open window does? Spearman rho (n days), weekdays")
    rows = []
    for a, c in [("R", "R"), ("D", "R"), ("dOI", "R"), ("dTP", "R"), ("dTA", "R"), ("D", "D"), ("dOI", "dOI"), ("dOI", "D")]:
        rho, n = spearman(piv[a]["PreOpen"] if a in piv else None, piv[c]["USOpen"])
        rows.append([f"PreOpen {NAMES[a]} -> USOpen {NAMES[c]}", fmt_rho(rho, n)])
    P(md_table(["pair", "rho (n)"], rows))
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="Dumps/backtest/raw")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    text = run(a.raw)
    print(text)
    if a.out:
        with open(a.out, "w", newline="\n", encoding="utf-8") as fh:
            fh.write(text + "\n")
