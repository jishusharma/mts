"""Builds the RESULT tables (markdown) from cells.csv. Run: python report.py > tables.md"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
c = pd.read_csv(os.path.join(HERE, "cells.csv"))


def f(x, d=2):
    return "-" if pd.isna(x) else ("%." + str(d) + "f") % x


print("| cell | block | n | days | win% | mean R net | trade CI | day CI | placebo p (A month / B BTC<35) | per-year | without best 5 days (n, mean) | top5 share | verdict |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for _, r in c.iterrows():
    if r.n == 0 or pd.isna(r.get("mean")):
        print("| %s %s | %s | 0 | 0 | - | - | - | - | - | - | - | - | - |" % (r.signal, r.exit, r.block))
        continue
    print("| %s %s | %s | %d | %d | %s | %s | [%s, %s] | [%s, %s] | %s / %s | %s | %d, %s | %s | %s |" % (
        r.signal, r.exit, r.block, r.n, r.days, f(100 * r.win, 0), f(r["mean"], 3), f(r.tlo), f(r.thi), f(r.dlo), f(r.dhi),
        f(r.A_p, 3), f(r.B_p, 3), r.per_year, r.ex5_n, f(r.ex5_mean, 3), f(r.top5_share), r.get("verdict", "") if isinstance(r.get("verdict"), str) else ""))
print()
print("Regime split (BTC daily close vs 200d SMA at signal bar close), POOL")
print()
print("| cell | bull n | bull mean | bull win% | bear n | bear mean | bear win% | no-SMA n |")
print("|---|---|---|---|---|---|---|---|")
for _, r in c[c.block == "POOL"].iterrows():
    print("| %s %s | %d | %s | %s | %d | %s | %s | %d |" % (r.signal, r.exit, r.bull_n, f(r.bull_mean, 3), f(100 * r.bull_win, 0), r.bear_n, f(r.bear_mean, 3), f(100 * r.bear_win, 0), r.na_n))
