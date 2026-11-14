**FAIL at bar 2 (and KILL by criteria a, b, c): fresh-coin DD20 weekly dip long, VAL n 561 trades in 92 entry weeks, gross -0.023 R (-0.58%), fee-net (12 bp + funding) -0.028 R (-0.63%), week-cluster 95% CI on net % [-4.8%, +3.4%] (in R [-0.233, +0.190]); the line is killed, DD20 was drift plus survivorship on these coins. Not an edge. Out of sample by coin, not by calendar time.**

# RESULT: T6 DD20 deep-drawdown weekly dip LONG on 44 fresh coins (2026-11-14)

PRE_REG.md (commit 1b3cfd0c2) is the law and was not edited. Research, not advice. All numbers below are parsed from summary.json, extras.json and trades.csv (extras.json is written by t6_extras.py, descriptive rows only; the bars are in t6_stats.py). Primary row = X2, 14-day time exit, no stop, net of 12 bp round trip (2 x BINANCE_TAKER + SLIPPAGE_RT_S13 from fees.py) and funding. "R" for the primary row uses the risk unit 2.5 x ATR14(1d) / entry (OURS, descriptive unit; the bars run on net % return). Data end: last daily bar 2026-11-12.

## Context

Regime: not gated (source cell is ungated). Descriptive tags: source BULL/BEAR (weekly close vs mean of last 50 weekly closes) and MTS brain cycle of the entry day. VAL signals were 80.6% source-BEAR (source study: about 75%), 58.1% brain BULL, 32.1% brain BEAR, 9.8% brain BASE.
Phase: no phase gate. Brain 6-phase label reported as a descriptive cut (below). Brain row for today, 2026-11-14: MARKDOWN / BEAR (provisional row).
Session: none; weekly bars, entry Monday 00:00 UTC, 24/7 market.
Entry: Monday 00:00 UTC open right after a completed week whose close is at or below 0.80 x the highest weekly close of the 8 weeks before it; exit close of day +13.

Regime mix: share of signals vs share of all eligible Mondays of the same coins (calendar-day proxy), from extras.json.

| split | tag | share of signals | share of Mondays |
|---|---|---|---|
| DEV (n 803 / 8912 Mondays) | source BEAR / BULL / NA | 54.3% / 22.0% / 23.7% | 52.1% / 28.0% / 19.8% |
| DEV | brain BASE / BEAR / BULL | 40.8% / 54.0% / 5.1% | 39.6% / 45.4% / 15.1% |
| VAL (n 561 / 5793 Mondays) | source BEAR / BULL / NA | 80.6% / 18.9% / 0.5% | 76.2% / 23.2% / 0.6% |
| VAL | brain BASE / BEAR / BULL | 9.8% / 32.1% / 58.1% | 12.9% / 32.5% / 54.6% |

Reading: signals are spread roughly like the calendar, so no regime concentration explains the result. DEV has few brain-BULL signals (5%), so a bull-cycle DEV read is thin. VAL holds the 2024 bull, 2025 and the 2026 slide; no result is generalised beyond this mix.

## Pass-bar table (PRE_REG bars 1-7, primary row, fresh coins)

| # | Bar | Value | Threshold | Met |
|---|---|---|---|---|
| 1 | VAL power: n and entry weeks | n 561, 92 weeks | n >= 30 and >= 20 weeks | yes |
| 2 | VAL mean net > 0 and CI low > 0 | mean -0.626%, CI low -4.81% (one-sided p 0.639) | > 0 and > 0 | NO (first failing bar) |
| 3 | DEV mean net > 0 | +2.58% (n 803) | > 0 | yes |
| 4 | Placebo: real >= 97.5th pct of draws, excess > 0 | real -0.626%, p97.5 +1.115%, excess +0.128 pp, placebo p 0.435 (real sits near the 57th percentile of draws; 0 fallbacks) | real >= p97.5 | NO |
| 5 | Ex-best-5 entry weeks mean > 0 | -4.31% (n 498; dropped 2024-W33, 2024-W45, 2024-W52, 2025-W16, 2026-W37) | > 0 | NO |
| 6 | Event mean net >= equal-weight 14-day basket baseline | -0.626% vs -0.913% (148 Mondays; gross -0.581% vs -0.822%) | event >= baseline | yes, but only because both are negative |
| 7 | Top-coin removal keeps mean > 0 | removing ONE: -1.49%; ONE+1INCH: -1.69%; plus ALGO: -1.87% | > 0 | NO (FRAGILE flag; the base mean is already negative) |

Kill criteria: (a) VAL net <= 0: FIRED (-0.626%). (b) STOP-row VAL mean R <= 0: FIRED (-0.063 R, CI [-0.269, +0.157], 23.2% of trades stopped). (c) ex-best-5 weeks <= 0: FIRED (-4.31%). Verdict by PRE_REG vocabulary: FAIL with KILL; flag FRAGILE (bar 7). MULTIPLICITY-FLAGGED is moot (no PASS); this study's one-sided p is 0.639, worst-case Holm-adjusted min(1, 3p) = 1.0. The verdict flags are applied by hand; the stats script does not emit them.

## Main table (primary row X2, fresh coins)

| row | n | entry weeks | win % | gross | fee | funding | net no-funding | net | week-cluster 95% CI on net | gross R | net R | net R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV (entry <= 2023-12-31) | 803 | 175 | 45.8 | +2.99% | 0.12% | +0.29% | +2.87% | +2.58% | [-3.31%, +8.70%] | +0.040 | +0.025 | [-0.140, +0.179] |
| VAL (entry >= 2024-01-01) | 561 | 92 | 42.8 | -0.58% | 0.12% | -0.07% (net credit) | -0.70% | -0.63% | [-4.81%, +3.40%] | -0.023 | -0.028 | [-0.233, +0.190] |
| Pooled DEV+VAL (descriptive, not a verdict) | 1364 | 267 | 44.6 | +1.52% | 0.12% | +0.14% | +1.40% | +1.26% | [-2.63%, +5.52%] | +0.014 | +0.003 | [-0.128, +0.143] |

Median VAL trade: -2.34% net (-0.087 R). The mean is carried by a thin right tail (best VAL trade +460.8%, ONE 2026-09-07; best DEV +327%). Medians are negative in both splits.

Baselines (bar 6 and random entry): equal-weight fresh basket 14-day forward return from every Monday, net: VAL -0.913% (148 Mondays), DEV +1.74% (293 Mondays). Event mean minus basket: VAL +0.29 pp, DEV +0.84 pp. Same-coin random-entry placebo (same split and source tag): draw mean -0.754%, so VAL excess over random is +0.13 pp, inside the draw noise (placebo p 0.435). In plain words: the dip rule did about as well as buying a random Monday of the same coins.

## Secondary, control and descriptive rows

| row | n | mean | note |
|---|---|---|---|
| STOP row VAL (2.5 x ATR14, fee + funding, in R) | 561 | -0.063 R, CI [-0.269, +0.157], placebo excess -0.032 R (placebo p 0.742) | kill criterion b |
| STOP row DEV | 800 | +0.023 R, CI [-0.139, +0.174] | 3 DEV trades have no stop row (MATIC, SUSHI, WAVES, all 2021-05-24) |
| VAL no-funding net (fee only) | 561 | -0.70%, CI [-4.82%, +3.29%] | funding changed the VAL mean by +0.07 pp (credits dominate) |
| VAL, trades on the REAL funding rule | 519 | +0.13% | 42 flat-rule VAL trades average -9.97% |
| VAL by source tag: BEAR / BULL / NA | 452 / 106 / 3 | +0.64% / -5.69% / -12.70% | descriptive |
| DEV by source tag: BEAR / BULL / NA | 436 / 177 / 190 | -1.49% / +9.41% / +5.55% | sign flips between DEV and VAL: no stable tag effect |
| VAL by brain cycle: BASE / BEAR / BULL | 55 / 180 / 326 | +4.61% / -0.34% / -1.67% | BASE mean is driven by the ONE trade; descriptive |
| DEV by brain cycle: BASE / BEAR / BULL | 328 / 434 / 41 | +9.07% / -2.24% / +1.75% | descriptive |

By year (net, from tables.md): VAL 2024 +1.67% (n 205), 2025 -2.66% (n 219), 2026 -0.82% (n 137). DEV 2018 -7.84% (16), 2019 +0.66% (79), 2020 -3.59% (122), 2021 +15.08% (195), 2022 -2.32% (237), 2023 +1.24% (154). The positive DEV mean is a 2021 result: DEV outside 2021 is about -1.4% per trade, computed from the year rows as (803 x 2.58% - 195 x 15.08%) / 608.

By coin: 44 coins kept, 0 dropped (all have >= 60 complete weeks). Every coin has n < 30 in VAL (max 17) and in DEV (max 26): ALL per-coin rows are underpowered and none carries a conclusion; the full tables are in tables.md. Best VAL coins by mean: ONE +28.8% (n 16, one +460.8% trade), FTM +8.4% (n 6), 1INCH +6.5% (n 13), MKR +5.8% (n 7); worst: WAVES -19.2% (n 3), FTT -9.0% (n 13), LUNA -7.6% (n 16), MATIC -6.4% (n 4).

Brain 6-phase label, VAL: ACCUM-RANGE -4.24% (83), DISTRIBUTION -4.96% (215), MARKDOWN +2.45% (154), MARKUP +6.43% (108, includes the ONE trade), RELIEF -4.30% (1). DEV: CAPITULATION +11.80% (39), MARKDOWN -4.86% (225), MARKUP +12.54% (150), others near zero. Descriptive only; no label is a gate.

## Power gate

PRE_REG freeze check (stated there): n 60 weeks, sd 1.2 R, m 3 gave MDE 0.501 R + cost 0.01 vs max plausible gross 0.3, n needed 179: BLOCK, run ordered anyway. Measured now: 92 VAL entry weeks (more than the 60 assumed), but the measured sd of the per-week mean net R is 2.41 R (twice the 1.2 R assumed, driven by the ONE trade). With n 92, sd 2.41, m 3, `prereg_gate.py` prints MDE 0.813 R, n needed 722, BLOCK. So the test could only have detected a gross edge near +0.8 R per trade, while the plausible gross edge is about +0.3 R or less. A FAIL on power alone would read as untested; here the VAL point estimate is also negative (-0.028 R), and three kill criteria fire on the point estimates, which is the PRE_REG's own stopping rule. It is not proof that a small edge cannot exist.

## Deviations, fixes, disclosures

- DEVIATIONS.md #1 and FIXLOG.md (audit major 2): the SOURCED "longest contiguous run" rule drops the pre-gap history of LUNA (5 events) and FTT (11 events), about 16 DEV trades. The PRE_REG survivorship note says LUNA and FTT are kept to their last bar; that sentence is NOT satisfied (the PRE_REG contradicts itself). DEV excludes pre-gap LUNA/FTT, so the survivorship bias for longs is larger than the PRE_REG note states. The audit found the sign of the omission mixed (FTT +0.61, +0.34, +0.30 trades are also missing). VAL is unaffected (every dropped trade is before 2024). Using all runs would be a rule change and needs a new PRE_REG; not done. The line fails on VAL, so this does not change the verdict.
- FIXLOG.md (audit major 1): constant FEE_RT renamed RT_COST so the repo cost-constant gate passes; the value is still computed from fees.py; trades.csv byte-identical (1364 trades, DEV 803, VAL 561).
- Concentration (minor finding): ZIL 2026-02-02 (+40.0% net, funding credit +32.9%), AXS 2026-02-09 (+36.1%, credit +32.7%) and ONE 2026-09-07 (+460.8% net, funding credit +11.0%) dominate the trade-weighted VAL mean. VAL without these three trades: n 558, mean -1.59% (vs -0.63% with them). The ZIL and AXS credits are cached funding prints and may not have been earnable.
- 202 of 1364 trades (160 DEV, 42 VAL) use the flat funding rule (1 bp per 8 h, OURS, conservative; 0.42% over 14 days): entries before a coin's first funding print (DEV, mostly 2018-2020), after the cache end 2026-10-31 (20 VAL trades with entry in 2026-10), or on coins whose funding cache ends before the window. The REAL-rule VAL mean is +0.13%, the FLAT-rule VAL mean is -9.97% (n 42); that gap is a price result of those trades, since the flat charge itself is only 0.42%.
- 12 events are not in the list because their 14-day window runs past the data end for coins that still trade (PRE_REG data-end rule, checked by the recompute and audit checkers). See active-today.
- ATR convention: Wilder ATR14 seeded by the simple mean of the first 14 true ranges, first TR uses its own close as previous close (source study convention), not a FORMULAS.md function; labelled source-study / OURS. It only affects the R columns and the STOP row, not the primary % bars.
- Placebo and basket pool (not specified in PRE_REG, DEVIATIONS.md #4): every Monday of the same coin from week 9 on, includes the event Mondays themselves (a small bias toward the real mean) and, for the basket, drops DELIST-EXIT rows.
- 1 DELIST-EXIT trade (OMG 2024-06-10); 3 DEV trades have no stop row.
- No allowlist rows needed: lookahead lint has no t6 hits.
- Added at stage 4: t6_extras.py (descriptive tables, writes extras.json). No bar, rule, parameter or PRE_REG text was changed. No stats bug had to be fixed.

## What this does and does not show

- Out of sample by coin, not by calendar time: the 44 fresh coins fall in the same weeks as the 22 source coins, so a market-wide episode counts twice if old and fresh are pooled. The pooled row here is fresh only (DEV+VAL).
- Spot prices stand in for a perp; funding is real where cached and a flat OURS assumption elsewhere; no fill model, no borrow, no liquidity limit for small coins. Fee and funding are not the reason for the fail: gross VAL is already -0.58%.
- Survivorship: hindsight candidate list (coins that existed 2019-2021 and were listed) biases results upward for longs; LUNA/FTT collapse trades are optimistic where present, and pre-gap LUNA/FTT are absent (above). Even with an upward-biased sample, VAL is negative.
- What it shows: on 44 coins the source cell's +2.6% VAL mean did not appear (-0.63%); the DEV +2.58% is a 2021 result; the rule did not beat random same-coin Mondays (placebo p 0.435) and it fails the removal of 5 weeks or of one coin. The source cell itself had a CI low of -0.2% and placebo p 0.053, so this replication supports the weakest reading of the source: its positive number was drift plus a few weeks.
- What it does not show: that the dip never pays on any universe, that weekly dip entries with another exit or stop cannot work, or anything about calendar-time out-of-sample behaviour.

## Active today (descriptive, NOT advice)

- Fresh coins: no new DD20 event is known beyond the last closed event week (week ending 2026-11-08; the week ending 2026-11-15 is not closed). 12 events from the last two closed event weeks are still inside their 14-day window or unresolved at the data end 2026-11-12, so they are not in the trade list: entry 2026-11-02 XTZ, ONT, QTUM, BAT, CRV, YFI, 1INCH, ONE (exits due 2026-11-15); entry 2026-11-09 KNC, COMP, FTT, DASH (exits due 2026-11-22).
- BTC (not in the fresh universe, descriptive): last complete week close 74,851 is 0.865 x the prior 8-week max close 86,530, so it is NOT a DD20 event (needs <= 0.80); last daily close 71,460 on 2026-11-12. Brain 2026-11-14: MARKDOWN / BEAR (provisional).
- The line is killed by its own kill criteria; a live signal is not a reason to trade it.

Next: END: killed by PRE_REG kill criteria a, b and c (VAL fee-net -0.63%, STOP row -0.063 R, ex-best-5 weeks -4.31%); DD20 was drift plus survivorship on fresh coins. A new rule or exit would need a new PRE_REG; the pre-gap LUNA/FTT contradiction needs no resolving because VAL decides.
