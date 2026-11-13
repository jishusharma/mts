"""Builds RESULT.md from results.json (run after study.py)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "results.json")))
NAMES = {"S1": "S1 1h RSI<=20 (primary)", "S2": "S2 1h RSI<=15", "S3": "S3 4h RSI<=20"}
p1, p2, na = r["part1"], r["part2"], r["n_all"]
tot = {s: sum(1 for x in p2[s] if x["verdict"].startswith("PASS")) for s in p2}
L = []
a = L.append
a("# RESULT: where to sell the RSI-extreme + confirm-candle long (edge4-rsi-confirm-exits-1113)\n")
if sum(tot.values()) == 0:
    a("**Verdict: FAIL. 0 of 48 pre-registered exit rules pass (16 per set; headline set S1 = 1h RSI<=20, 20 coins, 0 of 16, no exit has a positive fee-net VALIDATION mean).** No edge claim. The best S1 exit loses about 0.08R per trade net; the 4h set (S3) is gross-positive for most exits but no CI clears zero.\n")
else:
    a("**Verdict: see table, %s passes.**\n" % tot)
a("Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV (2020-01-01..2023-12-31) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-01-01..now) bull 56 % / bear 30 % / range 15 %.\n")
a("Setup: Bybit v5 public linear 1h/1D, 20 coins since listing, entries as in edge3 (first touch, re-arm > 30, confirm = next bar green and closing above the signal close, entry = confirm close, stop = signal-bar low). Costs: 2 x fees.BINANCE_TAKER (%.2f bp/side, a little above the 4 bp in the brief) + fees.SLIPPAGE_RT_S13 (%.0f bp round trip) = %.0f bp of entry price per round trip, divided by the stop distance to get R. Closed bars, stop before target in a bar, trades need a full 168 h forward window. Placebo: 30 draws of a random same-coin same-week bar with the same stop distance and exit rule (RSI/MA exits: bars below SMA20 with RSI<=40). n per split (all / DEV / VALIDATION): %s.\n" % (r["taker"] * 1e4, r["slip_rt"] * 1e4, r["cost"] * 1e4, ", ".join("%s %d/%d/%d" % (s, *na[s]) for s in na)))
a("## Part 1: the path after entry (descriptive, all dates pooled, R = entry - signal low)\n")
a("| set | n | stopped within 72 h | stop hit in bar 1 | reach +0.5R before stop | +1R | +2R | +0.5R then stopped (before +1R) | median bars to peak |")
a("|---|---|---|---|---|---|---|---|---|")
for s, p in p1.items():
    a("| %s | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f |" % (NAMES[s], p["n"], p["stopped_72h"] * 100, p["stop_bar1"] * 100, p["reach0.5"] * 100, p["reach1"] * 100, p["reach2"] * 100, p["half_then_stop"] * 100, p["peak_bars_median"]))
a("\nMedian raw MFE / MAE in R after k hourly bars (max high / min low from entry, stop ignored):\n")
ks = ["1", "2", "4", "8", "12", "24", "48"]
a("| set | " + " | ".join("%sb" % k for k in ks) + " |")
a("|---|" + "---|" * len(ks))
for s, p in p1.items():
    a("| %s MFE | " % s + " | ".join("%.2f" % p["mfe"][k] for k in ks) + " |")
    a("| %s MAE | " % s + " | ".join("%.2f" % p["mae"][k] for k in ks) + " |")
a("\nReading: the price spends the first hours going both ways by about the same size (MFE ~ MAE), then the downside grows faster than the upside; the median peak (before the stop) is about 6 bars for S1. 1 in 7 S1 trades first gets +0.5R and then is stopped out.\n")
for s in ("S1", "S2", "S3"):
    a("## Part 2 %s: %s, VALIDATION from 2024-01-01 (%d trades on %d signal days)\n" % (s, NAMES[s], p2[s][0]["n_val"], p2[s][0]["n_days"]))
    a("| exit | n VAL | net>0 % | mean R gross | mean R net | CI trade (95%) | CI day-cluster | placebo mean (p) | DEV net | verdict |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for x in p2[s]:
        a("| %s | %d | %.0f%% | %+.3f | %+.3f | [%+.2f, %+.2f] | [%+.2f, %+.2f] | %+.3f (%.3f) | %+.3f | %s%s |" % (
            x["rule"], x["n_val"], x["win_val"] * 100, x["gross_val"], x["net_val"], x["ci_lo"], x["ci_hi"], x["day_lo"], x["day_hi"],
            x["placebo_mean"], x["placebo_p"], x["net_dev"], x["verdict"], " BH" if x["bh"] else ""))
    a("")
a("Notes: gross = no costs; net = fees + slippage. Median net R sits near -1.0 for the late/wide exits (most trades are stopped, a minority win big); medians and %-return means are in results.json. The placebo mean is lower than the real mean for almost every exit, so the signal is better than a random entry with the same stop, but the improvement is not enough to cover cost per stop distance. Placebo p has a floor of 1/31 = 0.032 (30 draws). BH is applied inside each set over its 16 p-values (one-sided trade-level bootstrap); none is significant.\n")
a("## Limits\nNo funding; 1h bars cannot order stop vs target inside a bar (stop first = pessimistic for tight targets); exits tested on one VALIDATION stretch (2024+, bull 56 %); coins overlap in time (day view and week blocks reduce, not remove, the dependence); tiny stop distances inflate cost in R and are not filtered (the operator rule has none); S3 has few signal days.\n")
a("Files: PRE_REG.md (committed before outcomes), fetch.py, rsi_grid_lib.py (edge3 lib), exits_lib.py, study.py, test_exits.py, results.json, trades_S1.csv.")
open(os.path.join(HERE, "RESULT.md"), "w").write("\n".join(L) + "\n")
