"""P0 run: the operator's daily-level rule on DEV data (PRE_REG_CANDLE_PILOT.md section 3 + Addendum A).
Writes P0_RESULTS.md and p0_results.json next to the research doc and appends to TRIAL_REGISTRY.csv.
Run: python MyTradingSys/research/candle_patterns_2026-10-04/pilot/run_p0.py
"""
import sys
sys.dont_write_bytecode = True
import csv
import datetime
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cdata  # noqa: E402
import op_rule  # noqa: E402
import bt_stats  # noqa: E402

OUT = HERE.parent
RUN_ID = "P0-2026-10-04"


def year_of(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc).year


def describe(bars, variant, funding, day_ms, slip, null_perm=2000):
    r = op_rule.simulate(bars, variant, funding, day_ms=day_ms, slip=slip)
    tr, side = r["trades"], r["side"]
    n = len(bars)
    row = {"variant": variant, "n_bars": n, "trades": len(tr), "slip": slip, "open_at_end": r["open_at_end"]}
    if not tr:
        return row, r
    net = [t["net"] for t in tr]
    gross = [t["gross"] for t in tr]
    wins = [x for x in net if x > 0]
    losses = [x for x in net if x <= 0]
    lo, hi = bt_stats.bootstrap_mean_ci(net, n_boot=10000, seed=12345)
    wl, wh = bt_stats.wilson(len(wins), len(net))
    in_mkt = sum(t["days"] for t in tr) / float(n)
    s = op_rule.curve_stats(r["net_d"])
    sg = op_rule.curve_stats(r["gross_d"])
    lens = [t["days"] for t in tr]
    nulls = op_rule.random_null(bars, lens, side, n_perm=null_perm)
    real_gross = sum(gross) / len(gross)
    p_null = (sum(1 for x in nulls if x >= real_gross) + 1.0) / (null_perm + 1)
    bh_daily = [math.log(bars[i]["c"] / bars[i - 1]["c"]) for i in range(1, n)]
    bh = op_rule.curve_stats(bh_daily)
    by_year = {}
    for t in tr:
        by_year.setdefault(year_of(bars[t["entry_i"]]["t"]), []).append(t["net"])
    row.update({
        "win_rate": len(wins) / len(net), "win_ci": [wl, wh],
        "mean_gross_bps": 1e4 * real_gross, "mean_net_bps": 1e4 * sum(net) / len(net), "net_ci_bps": [1e4 * lo, 1e4 * hi],
        "median_net_bps": 1e4 * statistics.median(net), "avg_win_bps": 1e4 * (sum(wins) / len(wins)) if wins else 0.0,
        "avg_loss_bps": 1e4 * (sum(losses) / len(losses)) if losses else 0.0,
        "median_hold_days": statistics.median(lens), "mean_hold_days": sum(lens) / len(lens),
        "time_in_market": in_mkt, "mean_fund_bps": 1e4 * sum(t["fund"] * side for t in tr) / len(tr),
        "sharpe_net": s["sharpe"], "mdd_net_log": s["max_dd_log"], "total_net_log": s["total_log"], "total_gross_log": sg["total_log"],
        "bh_total_log": bh["total_log"], "bh_sharpe": bh["sharpe"], "bh_mdd_log": bh["max_dd_log"],
        "null_mean_gross_bps": 1e4 * sum(nulls) / len(nulls), "p_vs_random_null": p_null,
        "by_year": {str(y): {"n": len(v), "mean_net_bps": 1e4 * sum(v) / len(v), "sum_net_log": sum(v)} for y, v in sorted(by_year.items())},
    })
    return row, r


def fmt(row):
    if not row.get("trades"):
        return "| %s | 0 trades |" % row["variant"]
    return "| %s | %d | %.1f%% [%.0f-%.0f] | %.1f | %.1f [%.0f, %.0f] | %.1f | %.1f/%.1f | %.1f | %.0f%% | %.2f | %.2f | %.2f | %.2f | %.3f |" % (
        row["variant"], row["trades"], 100 * row["win_rate"], 100 * row["win_ci"][0], 100 * row["win_ci"][1],
        row["mean_gross_bps"], row["mean_net_bps"], row["net_ci_bps"][0], row["net_ci_bps"][1], row["median_net_bps"],
        row["avg_win_bps"], row["avg_loss_bps"], row["median_hold_days"], 100 * row["time_in_market"],
        row["sharpe_net"], row["mdd_net_log"], row["total_net_log"], row["bh_total_log"], row["p_vs_random_null"])


def main():
    funding = cdata.Funding()
    bars = cdata.load_daily()
    window = "2020-01-01..2024-06-30"
    rows = []
    registry = []
    for variant in ("P0a", "P0c", "P0s", "P0e"):
        for slip in (0.0002, 0.0, 0.0005):
            row, _ = describe(bars, variant, funding, cdata.DAY, slip, null_perm=2000 if slip == 0.0002 else 200)
            row["window"], row["tf"] = window, "1d"
            rows.append(row)
        base = [r for r in rows if r["variant"] == variant and r["slip"] == 0.0002][0]
        registry.append((RUN_ID, "2026-10-04", "P0", variant, "1d", window, base.get("trades", 0), base.get("mean_net_bps"), "net bps/trade at slip 2bps"))
    # P0anchor: 1m-built days, 2022-01..2024-06
    m1 = cdata.load_1m(cdata.HOURLY_START_MS, cdata.DEV_END_MS)
    anchors = []
    for off_h in (0, 4, 8, 12, 16, 20):
        ab, dropped = cdata.resample_offset(m1, 1440, off_h * 60)
        row, _ = describe(ab, "P0a", funding, cdata.DAY, 0.0002)
        row["anchor_utc_hour"], row["dropped_partial_days"] = off_h, dropped
        row["window"], row["tf"] = "2022-01-01..2024-06-30", "1d(anchor)"
        anchors.append(row)
        registry.append((RUN_ID, "2026-10-04", "P0anchor", "P0a@%02d" % off_h, "1d(anchor)", row["window"], row.get("trades", 0), row.get("mean_net_bps"), "net bps/trade"))
    (OUT / "p0_results.json").write_text(json.dumps({"main": rows, "anchors": anchors}, indent=1), encoding="utf-8", newline="\n")
    reg = OUT / "TRIAL_REGISTRY.csv"
    new = not reg.exists()
    with open(reg, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if new:
            w.writerow(["run_id", "date", "family", "variant", "tf", "window", "n", "mean_net_bps", "note"])
        for r in registry:
            w.writerow(r)
    hdr = ("| variant | trades | win rate [Wilson 95] | gross bps/trade | net bps/trade [boot 95 CI] | median net bps | avg win/loss bps | median hold d | in market | Sharpe(net,365) | max DD (log) | total net (log) | B&H total (log) | p vs random null |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    md = ["# P0 RESULTS - operator rule on DEV data (generated by run_p0.py)", "",
          "DEV 2020-01-01..2024-06-30 daily UTC bars, Binance BTCUSDT perp. Costs: 5 bps fee + 2 bps slip per side, realised funding. EXPLORATORY; see PRE_REG_CANDLE_PILOT.md.", "",
          "## Main variants (slip 2 bps)", hdr]
    md += [fmt(r) for r in rows if r["slip"] == 0.0002]
    md += ["", "## Slippage stress (net bps/trade, trades, total net log)", "| variant | slip 0 | slip 2 | slip 5 |", "|---|---|---|---|"]
    for v in ("P0a", "P0c", "P0s", "P0e"):
        cells = []
        for s in (0.0, 0.0002, 0.0005):
            r = [x for x in rows if x["variant"] == v and x["slip"] == s][0]
            cells.append("%.1f bps, n=%d, tot %.2f" % (r.get("mean_net_bps", float("nan")), r.get("trades", 0), r.get("total_net_log", float("nan"))))
        md.append("| %s | %s |" % (v, " | ".join(cells)))
    md += ["", "## By entry year (slip 2 bps): n / mean net bps / sum net log"]
    for v in ("P0a", "P0c", "P0s", "P0e"):
        r = [x for x in rows if x["variant"] == v and x["slip"] == 0.0002][0]
        md.append("- %s: " % v + "; ".join("%s: %d / %.0f / %.2f" % (y, d["n"], d["mean_net_bps"], d["sum_net_log"]) for y, d in r.get("by_year", {}).items()))
    md += ["", "## Anchor sensitivity - P0a with the day boundary shifted (2022-01..2024-06)", hdr]
    md += [fmt(dict(r, variant="P0a@%02dh" % r["anchor_utc_hour"])) for r in anchors]
    md += ["", "Mean funding paid per long trade is in p0_results.json (mean_fund_bps). B&H total is over the same bars."]
    (OUT / "P0_RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
