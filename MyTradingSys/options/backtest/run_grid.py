"""Grid runner. python run_grid.py --strategy R1|R2|R3|R4|R7|S7|all --start YYYY-MM-DD --end YYYY-MM-DD --out DIR
Writes <S>.csv per strategy (every grid cell x period), coverage_days.csv, coverage_fill.csv; prints only counts
parsed back from the written files."""
import argparse
import csv
import itertools
import math
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import stats  # noqa: E402
import strategies as st  # noqa: E402
from instruments import DAY_MS, ms_to_ymd, ymd_to_ms  # noqa: E402
from panel import Panel  # noqa: E402

GRIDS = {
    "full": {
        "R1": dict(dow_entry=[3, 4, 6], hour=[8, 12, 16], delta=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30]),
        "R2": dict(delta=[0.10, 0.15, 0.20, 0.25, 0.30], tenor_days=[7, 14, 30], dvol_filter=[False, True]),
        "R4": dict(delta=[0.10, 0.15, 0.20, 0.25, 0.30], tenor_days=[7, 14, 30], dvol_filter=[False, True]),
        "R3": dict(tenor_days=[7, 14, 30], hedge_rule=["hourly", "band0.02"]),
        "R7": dict(strike_pct=[0.95, 0.90, 0.85], tenor_days=[30, 90], structure=["put", "collar"]),
        "S7": dict(tenor_days=[7, 30]),
    },
    "small": {
        "R1": dict(dow_entry=[4], hour=[16], delta=[0.10, 0.20]),
        "R2": dict(delta=[0.20], tenor_days=[7], dvol_filter=[False, True]),
        "R4": dict(delta=[0.20], tenor_days=[7], dvol_filter=[False, True]),
        "R3": dict(tenor_days=[7], hedge_rule=["hourly", "band0.02"]),
        "R7": dict(strike_pct=[0.90], tenor_days=[30], structure=["put", "collar"]),
        "S7": dict(tenor_days=[7]),
    },
}
ALL = ["R1", "R2", "R3", "R4", "R7", "S7"]
PARAM_COLS = ["dow_entry", "hour", "delta", "tenor_days", "dvol_filter", "hedge_rule", "strike_pct", "structure"]
STAT_COLS = ["n", "n_skipped", "n_skipped_no_instrument", "n_skipped_no_fill", "n_skipped_filter",
             "n_skipped_no_settlement", "n_skipped_no_hedge_data", "fill_rate", "trade_rate", "win_rate",
             "mean_pnl_btc", "median_pnl_btc", "worst_pnl_btc", "best_pnl_btc", "total_pnl_btc", "t_stat",
             "boot_ci_lo", "boot_ci_hi", "max_dd_pct", "sharpe_weekly", "final_equity_btc", "sum_options_btc",
             "sum_hedge_btc", "sum_funding_btc", "sum_fees_btc", "carry_cost_pct_yr", "net_cost_pct_yr",
             "covered_frac", "maxdd_overlay_pct", "maxdd_hodl_pct", "es5_overlay", "es5_hodl",
             "final_ratio_vs_hodl", "pbo_cscv"]
HEADER = ["strategy", "cell_id"] + PARAM_COLS + ["period"] + STAT_COLS
FUNCS = {"R1": st.weekend_strangle, "R2": st.covered_call, "R4": st.cash_secured_put,
         "R3": st.delta_hedged_short_straddle, "S7": st.long_straddle}


def cells_for(strategy, grid):
    g = GRIDS[grid][strategy]
    keys = list(g)
    return [dict(zip(keys, vals)) for vals in itertools.product(*[g[k] for k in keys])]


def cell_id(strategy, p):
    return strategy + "|" + "|".join("%s=%s" % (k, p[k]) for k in p)


def run_cell(panel, strategy, p, start, end):
    if strategy == "R7":
        return st.protective_put_overlay(panel, p["strike_pct"], p["tenor_days"], collar=(p["structure"] == "collar"),
                                         start=start, end=end)
    kw = dict(p)
    return FUNCS[strategy](panel, start=start, end=end, **kw)


def period_windows(start, end):
    wins = [("ALL", None, None)] + list(stats.PERIODS)
    for y in range(int(start[:4]), int(end[:4]) + 1):
        wins.append(("Y%d" % y, "%d-01-01" % y, "%d-12-31" % y))
    return wins


def _in(ms, lo, hi):
    d = ms_to_ymd(ms)
    return (lo is None or d >= lo) and (hi is None or d <= hi)


def _nz(x):
    return "" if (x is None or (isinstance(x, float) and math.isnan(x))) else repr(float(x)) if isinstance(x, float) else x


def metrics(trades, skipped, series=None, lo=None, hi=None):
    s = stats.summarize(trades, skipped)
    by = s["n_skipped_by_reason"]
    eq = stats.equity_btc(trades)
    n = s["n"]
    nf = by.get("no_fill", 0)
    row = {"n": n, "n_skipped": s["n_skipped"], "fill_rate": (n / (n + nf)) if (n + nf) else float("nan"),
           "trade_rate": (n / (n + s["n_skipped"])) if (n + s["n_skipped"]) else float("nan"),
           "max_dd_pct": eq["max_drawdown_pct"], "sharpe_weekly": eq["sharpe_weekly"],
           "final_equity_btc": eq["final_equity_btc"]}
    for r in ("no_instrument", "no_fill", "filter", "no_settlement", "no_hedge_data"):
        row["n_skipped_" + r] = by.get(r, 0)
    for k in ("win_rate", "mean_pnl_btc", "median_pnl_btc", "worst_pnl_btc", "best_pnl_btc", "total_pnl_btc",
              "t_stat", "boot_ci_lo", "boot_ci_hi"):
        row[k] = s[k]
    row["sum_options_btc"] = sum(t.get("pnl_options_btc", float("nan")) for t in trades) if trades and \
        "pnl_options_btc" in trades[0] else ""
    for k, key in (("sum_hedge_btc", "pnl_hedge_btc"), ("sum_funding_btc", "pnl_funding_btc")):
        row[k] = sum(t[key] for t in trades) if trades and key in trades[0] else ""
    row["sum_fees_btc"] = sum(t["fees_btc"] for t in trades) if trades else ""
    if series is not None and trades:  # R7 overlay metrics over the period window
        years = (max(t["exit_ts"] for t in trades) - min(t["entry_ts"] for t in trades)) / (365.0 * DAY_MS)
        prem = sum(sum((lg["entry_px"] * (-1.0 if lg["side"] == "sell" else 1.0) + lg["fee_entry"])
                       for lg in t["legs"]) for t in trades)
        row["carry_cost_pct_yr"] = 100.0 * prem / years if years > 0 else ""
        row["net_cost_pct_yr"] = -100.0 * sum(t["pnl_btc"] for t in trades) / years if years > 0 else ""
        idx = [i for i, d in enumerate(series["dates"]) if (lo is None or d >= lo) and (hi is None or d <= hi)]
        if len(idx) >= 2:
            om = stats.overlay_metrics(series["equity_usd"][idx], series["hodl_usd"][idx])
            row["covered_frac"] = float(series["covered"][idx].mean())
            for k in ("maxdd_overlay_pct", "maxdd_hodl_pct", "es5_overlay", "es5_hodl", "final_ratio_vs_hodl"):
                row[k] = om[k]
    return row


def months_between(start, end):
    y, m = int(start[:4]), int(start[5:7])
    out = []
    while "%04d-%02d" % (y, m) <= end[:7]:
        out.append("%04d-%02d" % (y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def run_strategy(panel, strategy, grid, start, end, out_dir, write_trades):
    t0 = time.time()
    wins = period_windows(start, end)
    months = months_between(start, end)
    rows, pbo_rows, trade_rows = [], [], []
    mat = []
    for p in cells_for(strategy, grid):
        trades, skipped = run_cell(panel, strategy, p, start, end)
        cid = cell_id(strategy, p)
        series = st.overlay_equity_series(panel, trades) if strategy == "R7" else None
        base = {"strategy": strategy, "cell_id": cid}
        base.update({k: p.get(k, "") for k in PARAM_COLS})
        for name, lo, hi in wins:
            tr = [t for t in trades if _in(t["entry_ts"], lo, hi)]
            sk = [s for s in skipped if _in(s["ts"], lo, hi)]
            row = dict(base, period=name)
            row.update(metrics(tr, sk, series, lo, hi))
            rows.append(row)
        pm = np.zeros(len(months))
        for t in trades:
            pm[months.index(ms_to_ymd(t["entry_ts"])[:7])] += t["pnl_btc"]
        mat.append(pm)
        if write_trades:
            for t in trades:
                trade_rows.append({"cell_id": cid, "decision_ts": t["decision_ts"], "entry_date": ms_to_ymd(t["entry_ts"]),
                                   "exit_date": ms_to_ymd(t["exit_ts"]), "legs": ";".join(
                                       "%s %s @%.5f pay=%.5f" % (lg["side"], lg["name"], lg["entry_px"], lg["payoff_btc"])
                                       for lg in t["legs"]), "pnl_btc": t["pnl_btc"], "fees_btc": t["fees_btc"],
                                   "pnl_options_btc": t.get("pnl_options_btc", ""), "pnl_hedge_btc": t.get("pnl_hedge_btc", ""),
                                   "pnl_funding_btc": t.get("pnl_funding_btc", ""), "spot_entry": t["spot_entry"],
                                   "spot_exit": t["spot_exit"]})
    ns = 8 if len(months) >= 8 else (len(months) // 2) * 2
    pbo = stats.pbo_cscv(np.vstack(mat), ns) if (ns >= 2 and len(mat) >= 2) else float("nan")
    for r in rows:
        if r["period"] == "ALL":
            r["pbo_cscv"] = pbo
    path = os.path.join(out_dir, strategy + ".csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if (isinstance(r.get(k), float) and math.isnan(r[k])) else r.get(k, "")) for k in HEADER})
    if write_trades and trade_rows:
        with open(os.path.join(out_dir, strategy + "_trades.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(trade_rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(trade_rows)
    return time.time() - t0


def write_coverage(panel, req_start, req_end, start, end, out_dir, fill_rows):
    with open(os.path.join(out_dir, "coverage_days.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "calendar_days", "days_with_shard", "days_missing", "first_shard", "last_shard"])
        first, last = panel.date_range()
        for y in range(int(req_start[:4]), int(req_end[:4]) + 1):
            a, b = max(req_start, "%d-01-01" % y), min(req_end, "%d-12-31" % y)
            c = panel.coverage(a, b)
            w.writerow(["Y%d" % y, c["calendar_days"], c["days_with_shard"], len(c["missing"]), first, last])
        c = panel.coverage(req_start, req_end)
        w.writerow(["REQUESTED %s..%s" % (req_start, req_end), c["calendar_days"], c["days_with_shard"],
                    len(c["missing"]), first, last])
        c = panel.coverage(start, end)
        w.writerow(["EFFECTIVE %s..%s" % (start, end), c["calendar_days"], c["days_with_shard"], len(c["missing"]),
                    first, last])
    with open(os.path.join(out_dir, "coverage_fill.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["strategy", "cells", "n_trades_all_cells", "n_skipped_all_cells", "n_no_fill", "n_no_instrument",
                    "fill_rate", "elapsed_s"])
        for r in fill_rows:
            w.writerow(r)


def summarize_files(out_dir, strategies):
    """Print counts parsed from the files just written."""
    for s in strategies:
        with open(os.path.join(out_dir, s + ".csv"), newline="") as fh:
            rows = list(csv.DictReader(fh))
        allr = [r for r in rows if r["period"] == "ALL"]
        n = sum(int(r["n"]) for r in allr)
        sk = sum(int(r["n_skipped"]) for r in allr)
        nf = sum(int(r["n_skipped_no_fill"]) for r in allr)
        print("%s.csv: rows=%d cells=%d trades(all cells, ALL)=%d skipped=%d (no_fill=%d)" % (
            s, len(rows), len(allr), n, sk, nf))
    with open(os.path.join(out_dir, "coverage_days.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            if r["key"].startswith("EFFECTIVE") or r["key"].startswith("REQUESTED"):
                print("%s: calendar_days=%s days_with_shard=%s missing=%s" % (
                    r["key"], r["calendar_days"], r["days_with_shard"], r["days_missing"]))
    with open(os.path.join(out_dir, "coverage_fill.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            print("fill %s: cells=%s trades=%s skipped=%s fill_rate=%s elapsed_s=%s" % (
                r["strategy"], r["cells"], r["n_trades_all_cells"], r["n_skipped_all_cells"], r["fill_rate"],
                r["elapsed_s"]))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default="all")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default="2026-10-08")
    ap.add_argument("--out", default=os.path.join(_HERE, "..", "research", "results"))
    ap.add_argument("--grid", default="full", choices=sorted(GRIDS))
    ap.add_argument("--write-trades", action="store_true")
    ap.add_argument("--trades-dir", default=os.path.join(_HERE, "..", "data", "hist", "trades"))
    ap.add_argument("--cache-dir", default=os.path.join(_HERE, "_cache"))
    a = ap.parse_args(argv)
    strategies = ALL if a.strategy == "all" else [a.strategy]
    for s in strategies:
        if s not in GRIDS["full"]:
            ap.error("unknown strategy %s" % s)
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.cache_dir, exist_ok=True)
    gi = os.path.join(a.cache_dir, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", newline="\n") as fh:
            fh.write("*\n")
    panel = Panel(a.trades_dir, cache_dir=a.cache_dir, cache_days=24)
    first, last = panel.date_range()
    if first is None:
        ap.error("no shards in %s" % a.trades_dir)
    start, end = max(a.start, first), min(a.end, last)
    fill_rows = []
    for s in strategies:
        el = run_strategy(panel, s, a.grid, start, end, a.out, a.write_trades)
        with open(os.path.join(a.out, s + ".csv"), newline="") as fh:
            allr = [r for r in csv.DictReader(fh) if r["period"] == "ALL"]
        n = sum(int(r["n"]) for r in allr)
        sk = sum(int(r["n_skipped"]) for r in allr)
        nf = sum(int(r["n_skipped_no_fill"]) for r in allr)
        ni = sum(int(r["n_skipped_no_instrument"]) for r in allr)
        fill_rows.append([s, len(allr), n, sk, nf, ni, ("%.4f" % (n / (n + nf))) if (n + nf) else "", "%.1f" % el])
    write_coverage(panel, a.start, a.end, start, end, a.out, fill_rows)
    summarize_files(a.out, strategies)


if __name__ == "__main__":
    main()
