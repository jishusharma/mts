"""results.json -> markdown tables printed to stdout (pasted into RESULT.md)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
m = R["meta"]
def pc(x): return "n/a" if x is None else "%+.1f%%" % (100 * x)
print("| rule | side | trades (VAL) | VAL ann. return | VAL Sharpe | CI of mean (daily, 95%) | DEV Sharpe | max DD (VAL) | vs basket | placebo p | without best 5 coins (ann.) | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for k, v in R["rules"].items():
    for side in ("long", "short", "combined"):
        r = v[side]
        verdict = v["combined"]["verdict"] if side == "combined" else "-"
        print("| %s | %s | %d | %s | %.2f | [%+.3f%%, %+.3f%%] | %.2f | %.1f%% | %s | %s | %s | %s |" % (
            k, side, r["trades_val"], pc(r["val_ann"]), r["val_sharpe"], 100 * r["ci_lo"], 100 * r["ci_hi"], r["dev_sharpe"], 100 * r["mdd_val"],
            "yes" if r["beats_basket"] else "no", "n/a" if r["placebo_p"] is None else "%.3f" % r["placebo_p"], pc(r["ex5_ann"]), verdict))
print()
print("Basket (equal-weight buy-and-hold of the same coins, VAL): Sharpe %.2f, ann. return %s, cumulative %s" % (m["basket_val_sharpe"], pc(m["basket_val_ann"]), pc(m["basket_val_cum"])))
print()
print("Gates (combined book): g1 CI>0, g2 Sharpe VAL>=1 & DEV>0, g3a beats basket, g3b placebo p<=0.05, g4 BH 10%")
print("| rule | g1 | g2 | g3a | g3b | g4 | one-sided p | DEV ann. | last 90d sum | avg hold d | trades/yr | avg gross | best-5 share | best-10-days share | top5 coins | funding cov. |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k, v in R["rules"].items():
    c = v["combined"]; g = c["gates"]
    print("| %s | %s | %s | %s | %s | %s | %.4f | %s | %s | %.1f | %.0f | %.2f | %s | %s | %s | %.0f%% |" % (
        k, *["Y" if g[x] else "n" for x in ("g1_ci", "g2_sharpe", "g3a_basket", "g3b_placebo", "g4_bh")], c["p_one"], pc(c["dev_ann"]), pc(c["last90_sum"]), c["avg_hold"] or 0, c["trades_per_year"], c["avg_gross"], pc(c["top5_share"]) if c["top5_share"] is not None else "n/a (total<=0)",
        pc(c["top10d_share"]) if c["top10d_share"] is not None else "n/a (total<=0)", " ".join(c["top5"]), 100 * c["fund_cov"]))
print()
print("Per-year return (sum of daily returns, combined book):")
yrs = sorted({y for v in R["rules"].values() for y in v["combined"]["per_year"]})
print("| rule | " + " | ".join(yrs) + " |"); print("|---|" + "---|" * len(yrs))
for k, v in R["rules"].items():
    print("| %s | " % k + " | ".join(pc(v["combined"]["per_year"].get(y)) for y in yrs) + " |")
