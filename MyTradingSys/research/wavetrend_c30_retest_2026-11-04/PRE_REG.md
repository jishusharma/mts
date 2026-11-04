# PRE_REG: WaveTrend c30 re-run, retest after the dot + RSI confluence, by session (frozen 2026-11-04, before any return was computed)

Card `wavetrend-c30-retest-rsi-session`, Super Session order d-context-retest-1104 (context re-run 2). Re-runs the WaveTrend dot idea of
`research/wavetrend_2026-10-17` (atlas INCONCLUSIVE, 9 cells all FAIL, gross, bare signal bar, no RSI, no session) with the context the operator named:
"buy on retests after the dot combined with RSI confluence, then sessions also matter". A result here is a verdict on the rule AS WRITTEN below.
Code `study.py`, tests `test_wiring.py` (registered in scripts/dev/extra_tests.tsv; written first and failing once on the missing module; two
mutations of the dot band and the divergence window then made 2 of 10 fail). Context only from `backtest/research_kit.py` (regime_tag, session_tag,
retest_entry, regime_mix_line, cluster_mean_se, cluster_diff, holm). Only event COUNTS were read before this freeze (counts.csv, regime_mix_count.txt).

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| WaveTrend | hlc3; esa EMA10; d EMA(abs(ap-esa),10); ci=(ap-esa)/(0.015 d); wt1 EMA21(ci); wt2 SMA4(wt1); computed by `wt_parity_ref.py`, first 200 bars of the series unused | SOURCED LazyBear, wavetrend_2026-10-17/PARITY_CONTRACT.md s2-s3 |
| Dot | wt1 crosses wt2 on a CLOSED bar ("le" convention); buy dot needs wt1 <= -53, sell dot wt1 >= +53 | band 53 SOURCED (Pine :9-12); dot-only-in-band OURS (as the C30 lead) |
| Timeframes | 15m, 30m, 1h, BTCUSDT (Binance 1m resampled); 5m/4h/1d not run | OURS (the C30 lead lived on 30m/15m; 4h and 1d lack events, atlas s3) |
| RSI confluence "rsi" | RSI(14, Wilder, closes) on the same TF at the dot bar close: buy <= 40, sell >= 60 | RSI 14 SOURCED; the 40/60 level is OURS (Malkan 60/40 is a monthly/weekly regime band, reused here as an oversold test: not his rule) |
| RSI confluence "div" | close-based regular divergence, swing-to-swing 3..12 bars (rsi_divergence.py), bullish for buy / bearish for sell, stamped within the last 3 bars up to the dot bar | closes-only and the 12-bar window SOURCED (Malkan, operator relay d-malkan-divergence-window-1104); the 3-bar proximity is OURS |
| conf "none" | no RSI condition | CONTROL only, never a survivor |
| Entry "signal" | enter at the dot bar close | OURS |
| Entry "retest" | first pullback to the dot bar midpoint (h+l)/2 within N=6 bars AFTER the dot bar (limit at the level, open if gapped); no touch = no trade | the idea (retest after the dot) is the operator's (d-context-retest-1104), no transcript line found yet; the level and N are OURS |
| Session | UTC close time of the dot bar: asia <08, london 08-13, ny 13-21, late 21-24 (research_kit.session_tag) | OURS (cutoffs from context_asof.session_of); the operator said sessions matter, not which |
| Trend gate "with" | daily SMA200 side of the last closed daily bar agrees with the trade (buy above, sell below); "against" = opposite | SOURCED-in-repo (research_kit.regime_tag side = meta.py trend_d); the operator's "buying in a downtrend is invalid" |
| Regime rows | research_kit.regime_tag (daily SMA200 side + weekly/monthly RSI 60/40 SOURCED Malkan): reg_bull / reg_range / reg_bear, descriptive | tag from research_kit |
| Horizon | exit at close 12 bars after the entry bar | OURS (the atlas primary horizon) |
| Cost | 0.14 % round trip, taker both legs (also for retest fills; a maker-in 0.09 is not assumed) | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost; day-clustered SE (cluster = UTC day of entry); 95 % CI = mean +- 1.96 SE | SOURCED research_kit |
| Drift control | excess = mean gross - mean same-side gross of EVERY bar close in the same TF, window, gate and session (cluster_diff) | OURS |
| Overlap | events are not thinned (no one-trade-at-a-time); the day cluster handles dependence | OURS |
| Multiple testing | confirmatory family A: pooled sessions, gate "with", conf rsi/div: 3 TF x 2 sides x 2 conf x 2 entries = 24 cells, Holm m=24. Family B: the same 24 cells split by 4 sessions, Holm m=96. Everything else (conf none, gate against/all, regime rows) is descriptive | OURS (research_kit.holm) |
| DEV survivor | n >= 30, >= 20 distinct days, net mean > 0, Holm p < 0.05 (own family), excess over drift t >= 2 | OURS |
| Windows | DEV events with bar close in [2022-01-01, 2024-07-01); data loaded only to 2024-07-01; 2020-2021 bars are warm-up history. VALIDATION 2024-07-01..2025-07-01 read ONCE for DEV survivors only (rule: n >= 15, net > 0, raw p < 0.05). HOLDOUT never loaded (loader end = window end) | SOURCED backtest/splits.py |

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; counts from `study.py --pass count`)
DEV window regime mix (research_kit.regime_mix_line): `130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`. The strict
Malkan band never gives a bear week in DEV, so reg_bear rows are empty by construction; the trend gate of the confirmatory family is the
daily SMA200 side (it has both sides). Event-days of the pooled with-trend cells, signal entry, best case per TF (confluence cells have fewer):
15m up to 219, 30m 130, 1h 71 (counts.csv). Gate inputs: sd OURS (0.9 / 1.3 / 1.9 %, typical BTC 12-bar sd, not an outcome), cost 0.14, m=24:
all three BLOCK (MDE + cost 0.381 / 0.596 / 1.023 vs 0.30; n needed 486 / 1013 / 2165 days); even one cell (m=1) on 15m blocks (0.312). BLOCKED.md has the lines.
Consequence, fixed now: the DEV table is DESCRIPTIVE (a measurement of an underpowered design). A FAIL verdict cannot be issued from cells that
cannot detect a plausible effect, so the verdict ceiling is INCONCLUSIVE (underpowered) unless a cell survives the DEV rule AND VALIDATION. No PASS
without a VERDICTS row and an independent trade-loop re-run.

## What the result will say
1. RESULT.md first lines: the `Regime mix:` line, then the verdict.
2. DEV fee-net table by gate (with / against / all / regime) x TF x side x conf x entry, pooled and by session: n, days, gross, net, day-clustered CI, excess over drift.
3. The context effect = conf none vs rsi/div, signal vs retest, with vs against, and the session split, each beside its control.

## Context
Regime: daily SMA200 side must agree with the trade (buy above / sell below), plus descriptive rows by research_kit.regime_tag (Malkan 60/40 band); against-trend rows are the control.
Phase: none as a tag, because the tf_break classes are not available per dot; the retest entry (dot, then pullback) is the phase device (OURS).
Session: asia / london / ny / late by UTC dot-bar close (research_kit.session_tag), pooled in family A and per session in family B.
Entry: signal-bar close vs retest of the dot-bar midpoint within 6 bars, both run (OURS).
