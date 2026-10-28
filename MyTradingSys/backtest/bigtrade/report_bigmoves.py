"""
Renders MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md from F:/MTS/data/bigtrade/bigmoves_stats.json (written by bigmoves.py).
Every number in the tables comes from that json; nothing is typed by hand. Usage: python -B -m MyTradingSys.backtest.bigtrade.report_bigmoves
"""
import datetime
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from MyTradingSys.backtest.bigtrade import bigmoves as bm  # noqa: E402

OUT = _REPO / "MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md"


def pct(v, nd=1):
    return "-" if v is None else "%.*f%%" % (nd, 100.0 * v)


def num(v, nd=2):
    return "-" if v is None else "%.*f" % (nd, v)


def render(stats):
    cov, st = stats["coverage_1m"], stats["tf"]
    rl, kl = stats["settings"]["r_list"], stats["settings"]["k_list"]
    tfs = list(st)
    L = ["# BIGMOVES REPORT (big-move ground truth, backtest A)", "",
         "Generated %s by report_bigmoves.py from bigmoves_stats.json. Code: MyTradingSys/backtest/bigtrade/bigmoves.py. Data store: %s." % (
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), bm.DATA_DIR), ""]
    L += ["## 1. Coverage actually found", ""]
    L.append("Merged 1m BTCUSDT klines: %s .. %s UTC, %d bars (= %.0f days x 1440), %d gaps (%d missing minutes), %d OHLC inconsistencies." % (
        bm.iso(cov["first_ms"]), bm.iso(cov["last_ms"]), cov["n_bars"], cov["n_bars"] / 1440.0, cov["n_gaps"], cov["missing_minutes"], cov["ohlc_inconsistent"]))
    L += ["", "| source | bars | first | last | new | duplicates of earlier source | conflicting duplicates |", "|---|---|---|---|---|---|---|"]
    for s in stats["settings"]["sources"]:
        L.append("| %s/%s | %d | %s | %s | %d | %d | %d |" % (s["root"].replace("\\", "/"), s["dataset"], s["n_bars"], bm.iso(s["first_ms"]) if s["first_ms"] else "-",
                                                             bm.iso(s["last_ms"]) if s["last_ms"] else "-", s["n_new"], s["n_duplicate_of_earlier_source"],
                                                             s["n_conflicting_duplicates"]))
    L += ["", "tom_raw is a subset (0 minutes it has that the main archive lacks, 0 conflicting values) and ends earlier, so it does not extend coverage (F-BT-06). "
          "The daily files 2025-09-01..07 duplicate the monthly 2025-09 file (10,080 identical rows, kept once).",
          "", "Zero-volume bars: %d, flat OHLC: %d, on %d days: %s (F-BT-05). They are kept as real clock minutes." % (
              cov["zero_volume_bars"], cov["zero_volume_flat_ohlc"], len(cov["zero_volume_days"]),
              ", ".join("%s (%d)" % (d, n) for d, n in sorted(cov["zero_volume_days"].items()))), ""]
    L += ["| TF | closed bars | first open | last close | time gaps | bars with partial minutes | all-zero-volume bars | zero-range bars | ATR SMA/Wilder p5 / p50 / p95 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for tf in tfs:
        t = st[tf]
        r = t["atr_sma_over_wilder"]
        L.append("| %s | %d | %s | %s | %d | %d | %d | %d | %.3f / %.3f / %.3f |" % (
            tf, t["n_bars"], bm.iso(t["first_ms"]), bm.iso(t["last_ms"]), t["tf_time_gaps"], t["bars_with_partial_minutes"],
            t["bars_all_minutes_zero_volume"], t["bars_zero_range"], r["p5"], r["p50"], r["p95"]))
    L += ["", "## 2. Analysis settings (not trading parameters)", "",
          "- ATR(14) Wilder on the bar's own TF, strictly causal, defined from bar index 14 (TR[0] undefined). Plain-SMA ATR is stored beside it (labels_*.csv `atr_sma`) because "
          "MTS core uses SMA (FORMULAS.md section 12; F-BT-07).",
          "- Legs: ATR zigzag, r in %s (reversal needed to confirm a pivot, x ATR at the pivot bar), leg size threshold k in %s (x ATR at the leg start bar). "
          "A leg is flagged (r, k) when it exists in the r-zigzag and its size is >= k." % (rl, kl),
          "- 'N bars either side' (PLAN section 3) is implemented as the zigzag condition itself: the pivot extreme is not exceeded from the previous pivot until a "
          "reversal of r x ATR. The pivot bar can never confirm its own reversal; equal extremes keep the earlier bar; the last unconfirmed swing is not a leg. "
          "No fixed fractal width was used; the share of pivots that also pass a +-2 bar fractal test is in section 7.",
          "- Times are bar CLOSE times. dur_bars = end pivot bar - start pivot bar. Forward labels: entry = next bar open, window H in %s bars, unit = ATR at the decision bar." % (
              stats["settings"]["h_list"],), ""]
    L += ["## 3. Legs per year (flagged legs, by year of leg start)", ""]
    for tf in tfs:
        years = st[tf]["years"]
        L += ["**%s**" % tf, "", "| r | k | " + " | ".join(str(y) for y in years) + " | total |", "|---|---|" + "---|" * (len(years) + 1)]
        for r in rl:
            for k in kl:
                d = st[tf]["per_year"]["%s|%s" % (r, k)]
                L.append("| %s | %s | %s | %d |" % (r, k, " | ".join(str(d.get(str(y), 0)) for y in years), sum(d.values())))
        L.append("")
    L += ["2026 is Jan to 2026-10-07 only; 2022 starts 2022-01-01 (ATR needs 14 bars first).", ""]
    L += ["## 4. Leg size distribution (size in ATR at the start bar; all legs of the r-zigzag, not only big ones)", "",
          "| TF | r | legs | p10 | p25 | p50 | p75 | p90 | p99 | max | median dur (bars) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for tf in tfs:
        for r in rl:
            d = st[tf]["size_pct"][str(r)]
            L.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (tf, r, d["n"], num(d["p10"]), num(d["p25"]), num(d["p50"]), num(d["p75"]), num(d["p90"]),
                                                                              num(d["p99"]), num(d["max"]), num(d["median_dur_bars"], 1)))
    L += ["", "## 5. How much of the price travel sits inside big legs", "",
          "legs path = sum of |ln(p_end/p_start)| over big legs / same over every leg of that r. bar travel = sum of bar-to-bar |ln(close ratio)| inside big legs / over all bars. "
          "time = share of bars inside big legs.", "",
          "| TF | r | k | big legs | legs path | bar travel | time |", "|---|---|---|---|---|---|---|"]
    for tf in tfs:
        for r in rl:
            for k in kl:
                key = "%s|%s" % (r, k)
                t = st[tf]["travel"][key]
                L.append("| %s | %s | %s | %d | %s | %s | %s |" % (tf, r, k, st[tf]["tradable"][key]["n_big"], pct(t["legs_path_share"]), pct(t["bar_travel_share"]), pct(t["time_share"])))
    L += ["", "## 6. Big legs a human would call tradable (duration > 3 bars)", "",
          "| TF | r | k | big legs | dur > 3 bars | share | median dur (bars) |", "|---|---|---|---|---|---|---|"]
    for tf in tfs:
        for r in rl:
            for k in kl:
                t = st[tf]["tradable"]["%s|%s" % (r, k)]
                L.append("| %s | %s | %s | %d | %d | %s | %s |" % (tf, r, k, t["n_big"], t["n_dur_gt3"], pct(t["share_dur_gt3"]), num(t["median_dur_bars"], 1)))
    L += ["", "## 7. Audit of the legs (independent re-check against the raw bars)", "",
          "pivot_not_bar_extreme must be 0. interior_more_extreme_bar = a whipsaw bar strictly inside a leg that spiked past a pivot and still extended the swing "
          "(intrabar order unknown, so the zigzag cannot move the pivot). pivot_bar_engulfs_leg = the pivot bar's own opposite extreme goes beyond the other pivot "
          "(one bar as long as the whole leg). size_below_r must be 0.", "",
          "| TF | subset | legs | pivot_not_bar_extreme | interior_more_extreme_bar | pivot_bar_engulfs_leg | size_below_r |", "|---|---|---|---|---|---|---|"]
    for tf in tfs:
        rows = [("all legs", st[tf]["invariants"])] + [("r=%s k=%s" % tuple(key.split("|")), v) for key, v in st[tf]["invariants_big"].items() if key.endswith("|3") or key.endswith("|8")]
        for name, v in rows:
            L.append("| %s | %s | %d | %d | %d | %d | %d |" % (tf, name, v["legs"], v["pivot_not_bar_extreme"], v["interior_more_extreme_bar"], v["pivot_bar_engulfs_leg"], v["size_below_r"]))
    L += ["", "| TF | r | pivots | pass +-2 bar fractal | share |", "|---|---|---|---|---|"]
    for tf in tfs:
        for r in rl:
            f = st[tf]["fractal"][str(r)]
            L.append("| %s | %s | %d | %d | %s |" % (tf, r, f["pivots"], f["pass"], pct(f["share"])))
    L += ["", "Big legs (flagged k=3, r=1.5) that start within 28 bars after a maintenance-flat bar (their ATR unit is depressed): " +
          ", ".join("%s %d" % (tf, st[tf]["legs_near_flat_bar"]["1.5|3"]) for tf in tfs) + ".", ""]
    return "\n".join(L)


def main():
    stats = json.loads((bm.DATA_DIR / "bigmoves_stats.json").read_text(encoding="utf-8"))
    OUT.write_text(render(stats), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
