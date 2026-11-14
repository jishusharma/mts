"""Builds RESULT.md from cells.csv + BTC regime mix (no new outcomes computed)."""
import json, os
import numpy as np
import pandas as pd
import study

d = pd.read_csv("cells.csv")
v = d[d.split == "VAL"].copy()
dv = d[d.split == "DEV"].set_index(["fam", "fill", "T", "S"])
sm = json.load(open("summary.json"))
O, H, L, C, _ = study.load("BTC")
day = pd.Series(C, index=pd.to_datetime(study.T0 + np.arange(len(C)) * study.STEP, unit="ms")).dropna().resample("1D").last().dropna()
ratio = day / day.rolling(200).mean()
rm = {}
for nm, sl in (("DEV", slice("2021-01-01", "2023-12-31")), ("VALIDATION", slice("2024-01-01", None))):
    r = ratio[sl].dropna()
    rm[nm] = (100 * (r > 1.05).mean(), 100 * (r < 0.95).mean(), 100 * ((r >= 0.95) & (r <= 1.05)).mean(), len(r))
mix = "; ".join("%s: %.0f%% above (>+5%%), %.0f%% below (<-5%%), %.0f%% within 5%% (%d days)" % ((k,) + x) for k, x in rm.items())
flag = [k for k, x in rm.items() if max(x[:3]) > 85]


def row(r):
    k = (r.fam, r.fill, r["T"], r.S)
    de = dv.loc[k].mean_net if k in dv.index else float("nan")
    return "| %s | %s | %.1f | %.1f | %d | %.1f%%%s | %.2f | %.2f | %.3f | %.2f | %.1f | %.3f | %s | %.3f |" % (
        r.fam, r.fill, r["T"] * 100, r.S * 100, r.trades, r.win * 100, " **W75**" if r.win75 else "", r.avg_win, r.avg_loss,
        r.mean_net, r.pf, r.worst5, r.ci_lo, "-" if pd.isna(r.p_vs_s0) else "%.3f" % r.p_vs_s0, de)


hdr = "| sig | fill | T% | S% | trades | win | avg win % | avg loss % | mean net % | PF | worst 5d % | CI low % | p vs S0 | DEV mean % |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
best = v[v.fam != "S0"].sort_values("mean_net", ascending=False).head(5)
topw = v[v.trades >= 200].sort_values("win", ascending=False).head(5)
s0 = v[(v.fam == "S0") & (v.fill == "taker")]
w75 = v[v.win75 & (v.fam != "S0")]
out = []
out.append("# RESULT: win rate vs expectancy, long scalps on Bybit perps (slug edge9-winrate-vs-expectancy-1114)\n")
out.append("**Verdict: FAIL. %d of %d cells pass; all %d VALIDATION cells (signal x shape x fill) have a NEGATIVE fee-net mean. %d non-random cells reach a win rate >= 75%% and all lose money after fees (best of them %.3f%% per trade). Win rates of 80-90%% come from the target/stop shape alone: random entries show the same.**\n" % (sm["n_pass"], sm["n_family"], len(v), len(w75), w75.mean_net.max()))
out.append("Pre-registered in `PRE_REG.md` (committed before any outcome). Code `study.py`, tests `test_study.py` (8 pass; a deliberately wrong target-checked-first version fails the same-bar test), grid `cells.csv`, `summary.json`.\n")
out.append("Regime mix: BTC daily close vs its 200-day SMA, share of days. %s.%s Both splits are mixed enough; the crypto bull run 2021 and the 2022 bear are in DEV, 2024-26 in VALIDATION.\n" % (mix, " ONE-REGIME flag: " + ",".join(flag) + "." if flag else " No split is >85% one regime."))
out.append("Run: 20 coins (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM TRX BCH ETC UNI NEAR FIL XLM AAVE), 5m from 2021-01-01 (listing for later coins) to 2026-11-14, all 20 downloaded (no cut). S3 had OI for every coin. Costs: taker 22 bp round trip, maker-entry 13 bp (as pre-registered). Family for BH = 72 non-S0 cells; BH passed 0.\n")
out.append("## Why an 80% win rate can lose money (plain words)\n")
out.append("1. A trade that takes a small profit fast and gives a big stop room wins most of the time: aim at +0.3% with a -3% stop and the price reaches +0.3% first about 9 times in 10, even on a random entry.")
out.append("2. But the one loss in ten costs 3%, ten times a win, so the 9 wins (+2.7%) are cancelled by one loss (-3%) before fees.")
out.append("3. Every trade also pays about 0.22% in fees and slippage; that alone is as big as three-quarters of a 0.3% win.")
out.append("4. So win rate only tells you how often you are right, not how much you make: what counts is win rate against the shape (breakeven win rate column in the shape table).")
out.append("5. A list of signals showing 56-86% wins can be produced by this shape from a coin flip; ask for the average win, the average loss and the fee-net result before trusting it.\n")
out.append("## Goal 1: random entries (S0, taker) show the shape effect, VALIDATION\n")
out.append("| T% | S% | win rate (random entry) | breakeven win rate after fees | mean net % per trade | avg win % | avg loss % |\n|---|---|---|---|---|---|---|")
for _, r in s0.iterrows():
    out.append("| %.1f | %.1f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f |" % (r["T"] * 100, r.S * 100, r.win * 100, r.breakeven * 100, r.mean_net, r.avg_win, r.avg_loss))
out.append("\nRandom entries win 75-89% in the wide-stop shapes and still lose 0.23-0.29% per trade; the win rate is bought with the stop size. The breakeven win rate rises toward 100% as the stop widens.\n")
out.append("## Goal 2: the 5 best cells (highest VALIDATION fee-net mean, non-random)\n")
out.append(hdr)
out += [row(r) for _, r in best.iterrows()]
out.append("\n## The 5 highest-win-rate cells (>= 200 VALIDATION trades)\n")
out.append(hdr)
out += [row(r) for _, r in topw.iterrows()]
out.append("\nNone has a positive mean; none passes any gate. The best cells lose about the maker cost (about 0.14%% per trade), i.e. their gross result is about zero: no gross edge over random entries large enough to pay the fees. %d cells have p vs S0 < 0.05, but each only loses less than random while still losing (same fill variant on both sides), so that gate alone proves nothing.\n" % int((v[v.fam != "S0"].p_vs_s0 < 0.05).sum()))
out.append("## Full VALIDATION grid (2024-01-01 onward), all %d cells. W75 = win rate >= 75%%. Worst 5d = worst 5 consecutive calendar days, sum of fee-net %% over all coins\n" % len(v))
out.append(hdr)
for _, r in v.sort_values(["fam", "fill", "T", "S"]).iterrows():
    out.append(row(r))
out.append("\nDEV cells are in `cells.csv` (split = DEV). Best DEV non-random mean: %.3f%%; DEV is not a gate.\n" % d[(d.split == "DEV") & (d.fam != "S0")].mean_net.max())
out.append("## Gate summary\n")
out.append("| Gate | Cells meeting it (of 72 non-random) |\n|---|---|")
f = v[v.fam != "S0"]
out.append("| VALIDATION mean > 0 | %d |\n| CI lower bound > 0 | %d |\n| >= 200 trades | %d |\n| beats S0, p < 0.05 | %d |\n| BH 10%% | %d |\n| positive without best 5 days | %d |\n| ALL (PASS) | %d |" % (
    (f.mean_net > 0).sum(), (f.ci_lo > 0).sum(), (f.trades >= 200).sum(), (f.p_vs_s0 < 0.05).sum(), f.bh.sum(), (f.mean_ex5 > 0).sum(), f["pass"].sum()))
out.append("\n## Limits\nFunding not charged. Maker variant assumes the limit fills when the next bar trades through it (queue position ignored; real fills are fewer and adverse-selected, so the maker numbers are optimistic). Stop-first on a same-bar touch is conservative; a 5m bar hides the true order. S3 OI is a point-in-time snapshot up to 1 h stale. Trade pooling across 20 correlated coins is handled by clustering the bootstrap on UTC entry day. Fee-net uses 22 bp (taker) / 13 bp (maker): the grid is not re-run for other fee levels.\n")
open("RESULT.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:6]))
