"""Build RESULT.md from cells.csv / base.csv / pairs.csv / results.json (+ trades cache for descriptive splits). Run after study.py."""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S  # noqa: E402

c = pd.read_csv(os.path.join(HERE, "cells.csv"))
b = pd.read_csv(os.path.join(HERE, "base.csv"))
p = pd.read_csv(os.path.join(HERE, "pairs.csv")) if os.path.getsize(os.path.join(HERE, "pairs.csv")) > 5 else pd.DataFrame()
j = json.load(open(os.path.join(HERE, "results.json")))
tr = pd.read_csv(os.path.join(S.CACHE, "trades.csv"))


def f(x, d=2, sign=False):
    return "-" if pd.isna(x) else (("%+." + str(d) + "f") if sign else ("%." + str(d) + "f")) % x


def row(x):
    return "| %s %dh +%s | %d / %d | %s | %s | %s | [%s, %s] | %s | %s | %s |" % (
        x.split, x.tf, x.exit, x.n_dev, x.n_val, f(100 * x.win_val, 0) + "%" if pd.notna(x.win_val) else "-", f(x.mean_val, 3, True),
        "DEV " + f(x.mean_dev, 3, True), f(x.lo_val, 2, True), f(x.hi_val, 2, True), f(x.vs_base, 3, True), f(x.placebo_p, 3), x.verdict)


HDR = "| layer split (TF, exit) | n DEV / VAL | win% VAL | mean R VAL | mean R DEV | CI 95% VAL | vs base | placebo p | verdict |\n|---|---|---|---|---|---|---|---|---|"


def row2(x):
    return "| %s | %d / %d | %s | %s | %s | [%s, %s] | %s | %s | %s |" % (
        "%s, %dh +%s" % (x.split, x.tf, x.exit), x.n_dev, x.n_val, (f(100 * x.win_val, 0) + "%") if pd.notna(x.win_val) else "-", f(x.mean_val, 3, True),
        f(x.mean_dev, 3, True), f(x.lo_val, 2, True), f(x.hi_val, 2, True), f(x.vs_base, 3, True), f(x.placebo_p, 3), x.verdict)


npass = int((c.verdict == "PASS").sum())
nund = int((c.verdict == "UNDERPOWERED").sum())
out = []
out.append("# RESULT: ONE layer at a time on the RSI-extreme + confirm-candle long (edge4-rsi-confirm-layers-1113)\n")
out.append("**Verdict: %s.** %d of 56 pre-registered layer tests PASS on VALIDATION (%d UNDERPOWERED, %d FAIL); pairs: %s. No edge claim." % (
    "FAIL" if npass == 0 else "SEE TABLE", npass, nund, int((c.verdict == "FAIL").sum()),
    "none passed" if (len(p) == 0 or (p.verdict != "PASS").all()) else "see table"))
out.append("Regime mix: BTC daily close vs 200d SMA (bull > +5 %%, bear < -5 %%): DEV 2020-2023 bull 51 %% / bear 40 %% / range 10 %%; VALIDATION 2024-01..%s bull 56 %% / bear 30 %% / range 15 %% (to 2025-06 bull 74 %% / bear 7 %%; from 2025-07 bull 36 %% / bear 54 %%)." % j["data_end"][:10])
out.append("Rule: 1h / 4h RSI(14) <= 20 first touch (re-arm >30), next bar green and closing above signal close = long at that close, stop = signal-bar low, exits +1R / +2R (72 h cap), 20 Bybit USDT perps from listing, fees 2 x BINANCE_TAKER (10 bp RT, taker both legs, no slippage, no funding), week-block bootstrap 2000, random-subset placebo 1000, BH 10 %% over 56. Splits: DEV <= 2023-12-31, VALIDATION from 2024-01-01 (entry time). Trades with < 168 h of forward data excluded (last 7 days). Trades: 1h %d (DEV %d / VAL %d), 4h %d (DEV %d / VAL %d)." % (
    j["coverage"]["1"]["n"], *j["n_by_tf_split"]["1h"], j["coverage"]["4"]["n"], *j["n_by_tf_split"]["4h"]))
out.append("Coverage: open interest starts %s (1h) / %s (4h) (Bybit 1h OI; %d of %d 1h and %d of %d 4h trades have a 24 h OI change); funding on all trades (Bybit 8 h history); daily ADX on %d / %d. Layers use only data closed at or before the signal bar's close.\n" % (
    j["coverage"]["1"]["oi_first"][:10], j["coverage"]["4"]["oi_first"][:10], j["coverage"]["1"]["n_oi"], j["coverage"]["1"]["n"], j["coverage"]["4"]["n_oi"], j["coverage"]["4"]["n"], j["coverage"]["1"]["n_dadx"], j["coverage"]["1"]["n"]))
out.append("## Unfiltered base (the bar every layer has to beat)\n")
out.append("| base | n DEV / VAL | win% VAL | mean R DEV | mean R VAL | CI 95% VAL |\n|---|---|---|---|---|---|")
for x in b.itertuples():
    out.append("| %dh +%s | %d / %d | %s%% | %s | %s | [%s, %s] |" % (x.tf, x.exit, x.n_dev, x.n_val, f(100 * x.win_val, 0), f(x.mean_dev, 3, True), f(x.mean_val, 3, True), f(x.lo_val, 2, True), f(x.hi_val, 2, True)))
out.append("\nThe bare rule is negative fee-net on 1h in both periods; 4h VALIDATION is positive but not distinguishable from zero (CI includes 0) and negative in DEV.\n")
out.append("## All 56 layer tests (VALIDATION decides; DEV shown for stability; placebo p = share of same-size random subsets of the base with mean >= the layer's)\n")
out.append(HDR)
for tf in (1, 4):
    for ex in ("1R", "2R"):
        for x in c[(c.tf == tf) & (c.exit == ex)].itertuples():
            out.append(row2(x))
out.append("\nPASS needs all of: n >= 30, mean > 0, CI lower > 0, beats base, placebo p <= 0.05, BH 10 %. BH column in cells.csv. The two layers with Deep n = 0..5 ('UNDERPOWERED') carry p ~ 0 by construction and take BH ranks; excluding them does not change any verdict.\n")
near = c[(c.n_val >= 30) & (c.mean_val > 0) & (c.lo_val > 0)]
out.append("## Closest calls (VALIDATION mean > 0 and CI lower > 0)\n")
out.append(HDR)
for x in near.itertuples():
    out.append(row2(x))
out.append("\nFAIL reason for each: BH 10 %% over 56 not met (smallest real p is %.3f, BH needs <= 0.0054 at rank 3), and DEV mean is negative for the same split, so the sign does not hold across periods.\n" % near.p_val.min() if len(near) else "None had CI lower > 0.\n")
out.append("## Stage 2: pairs (only layers that passed the DEV screen: n >= 30, mean > 0, above DEV base)\n")
out.append("DEV-screen layers per base: %s\n" % json.dumps(j["dev_screen_layers"]))
if len(p):
    out.append(HDR)
    for x in p.itertuples():
        out.append(row2(x))
else:
    out.append("No pairs qualified.")
out.append("\n## Descriptive only (not tested; no verdict)\n")
tr["Europe"] = (tr.hour >= 8) & (tr.hour < 16)
tr["RSI 10-15"] = (tr.rsi > 10) & (tr.rsi <= 15)
tr["RSI 15-20"] = (tr.rsi > 15) & (tr.rsi <= 20)
tr["RSI <=15"] = tr.rsi <= 15
tr["R tercile 2"] = (tr.stopdist > tr.tf.map({1: j["coverage"]["1"]["small_r_cut"], 4: j["coverage"]["4"]["small_r_cut"]}))
out.append("| subset | TF | n VAL | mean R +1R VAL | mean R +2R VAL | n DEV | mean R +2R DEV |\n|---|---|---|---|---|---|---|")
for nm in ("Europe", "RSI 10-15", "RSI 15-20", "RSI <=15"):
    for tf in (1, 4):
        s = tr[(tr.tf == tf) & tr[nm]]
        v, d = s[s.entry_t >= S.VAL0], s[s.entry_t < S.VAL0]
        out.append("| %s | %dh | %d | %s | %s | %d | %s |" % (nm, tf, len(v), f(v.net_1R.mean(), 3, True), f(v.net_2R.mean(), 3, True), len(d), f(d.net_2R.mean(), 3, True)))
out.append("\n## Reading\n")
out.append("- Nothing separates winners from losers robustly. The bare rule loses on 1h (-0.17 R at +1R after fees). Layers that look good on VALIDATION (OI-unwind and US session on 1h; daily ADX 20-25 on 4h) all had NEGATIVE DEV means, i.e. the sign flips between periods, which is what chance across 56 looks gives.")
out.append("- Only 4hADX>=40 has the same sign in both periods on 1h (DEV -0.03/+0.11, VAL -0.01/+0.05 R at +1R/+2R), but its mean is ~0 and CI includes 0: it removes losses, it does not create an edge.")
out.append("- Funding negative, volume capitulation, BTC above 200MA, BTC/ETH-vs-alt (BTC/ETH worse than alts), small stop and Asia do not help. 'Deep' (RSI <= 10) has 1 VALIDATION trade (5 DEV): the operator's example regime is too rare to test.")
out.append("- Power: 1h VALIDATION n 60-400 per split, 4h 15-140; 4h results are mostly UNDERPOWERED-adjacent noise (CI width ~ 0.5-1.0 R).")
out.append("\nLimits: no slippage, no funding charge, 10 bp RT fee (taker); trades across the 20 coins overlap in time (week blocks cover part); VALIDATION is mostly bull; ADX/DI per FORMULAS.md Wilder 14 (not TradingView-cross-checked here, HOW_TO_USE_ADX note applies); DEV screen thresholds are OURS; the OI/funding timestamp alignment uses the last record at or before signal close.")
out.append("\nBest next test if anything: 4hADX>=40 + OI-unwind on 1h as a forward (testnet) paper log, since those are the only layers with a plausible mechanism and non-negative VALIDATION; do not promote on this evidence.")
open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out)[:3000])
