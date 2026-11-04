# PRE_REG: RSI divergence under Malkan's monthly/weekly RSI gate (frozen 2026-11-04, before any return was computed)

Card `rsi-divergence-mtf-under-malkan-gate`, Super Session order d-context-retest-1104, spec d-malkan-divergence-window-1104 (included
below before the DEV run). Re-runs `research/rsi_divergence_mtf_2026-10-09` (FAIL, raw divergence, no gate, "regime NOT_IN_DATA")
with the gate Malkan states. A result here is a verdict on the rule AS WRITTEN below, not on the raw signal.
Code: `study.py` (this folder), tests `test_gate_wiring.py` (registered in scripts/dev/extra_tests.tsv). Context only from
`backtest/research_kit.py` (regime_tag, retest_entry, regime_mix_line, cluster_mean_se, cluster_diff, holm); no new trend tag.

## Parameters (every one labelled)

| Parameter | Value | Label |
|---|---|---|
| Gate: monthly AND weekly RSI | >= 60 bull, <= 40 bear (level test, last CLOSED bar as-of) | SOURCED Malkan, MALKAN_RULES_2026-10-31.md:11-16 (research_kit.RSI_BULL/BEAR) |
| Gate: daily side | close above/below SMA200 of last closed daily bar (regime bull = band bull AND above; bear = band bear AND below; else range) | SOURCED-in-repo (meta.py trend_d via research_kit); the AND combination is OURS (research_kit docstring) |
| Setup | bullish divergence in a bull regime = long; bearish divergence in a bear regime = short ("aligned"). counter / range / ungated shown as controls | OURS reading of "gate, then the daily setup" |
| Divergence | regular, close-to-close, strict local swing CLOSES (never wicks), consecutive same-kind swings, any RSI difference (decimals count), RSI 14 | SOURCED Malkan (extract quotes in rsi_divergence.py header); RSI 14 as the original run |
| Primary window | swing-to-swing 3..12 bars inclusive of both swings (arm W12) | SOURCED, operator relay of Malkan (d-malkan-divergence-window-1104); min 3 SOURCED; inclusive counting = as the original code |
| Secondary window | 3..18 bars (arm W18); past 18 = WEAK, not traded | SOURCED, operator relay of Malkan |
| Comparison windows | 3..10 (C3_10), 5..14 (C5_14): the original run's windows, comparison columns only, never survivors | OURS (coordinator ruling) |
| Event time | bar after swing B closes; regime read at that bar's CLOSE | OURS (causal; as original) |
| Entry "signal" | enter at the close of the event bar | OURS (as original) |
| Entry "retest" | first pullback to swing B's close within N=10 bars after the event bar, limit at the level, open if gapped (research_kit.retest_entry); no touch = no trade | retest idea SOURCED (MALKAN_RULES; "buy on the retest, not the touch"); the level (swing B close) and N=10 are OURS |
| Exit / horizon | close 10 bars after the entry bar | OURS, NO-SOURCE (carried from the original run's PRIMARY_H) |
| Timeframes | 15m, 1h, 4h, 1d (BTCUSDT) | OURS (Malkan's setup is on the daily; lower TFs added for n; 2m-3h-7h cells of the original are not re-run) |
| Cost | 0.14 % round trip (taker in+out incl. slippage) | SOURCED research_kit.TAKER_RT_PCT (gross_effect_screen_2026-10-15 PRE_REG s.1); original run used 0.10 % |
| Statistics | net = gross - cost; day-clustered SE (research_kit.cluster_mean_se, cluster = UTC day of entry); 95 % CI = mean +- 1.96 SE | SOURCED research_kit |
| Drift control | excess = mean gross - mean same-side gross of EVERY bar close in the same aligned regime, same TF and window (research_kit.cluster_diff) | OURS (a long in a bull regime beats zero on drift alone) |
| Multiple testing | Holm over the confirmatory family: arms W12, W18 x 4 TF x 2 sides x 2 entries = 32 cells, aligned gate only | OURS (research_kit.holm) |
| DEV survivor | aligned cell in W12/W18 with n >= 30, >= 20 distinct days, net mean > 0, Holm-adjusted p < 0.05, excess over drift t >= 2 | OURS |
| Windows | DEV events with bar close in [2022-01-01, 2024-07-01); data loaded only to 2024-07-01. Bars 2020-01..2021-12 are warm-up history for SMA200 and weekly/monthly RSI only. VALIDATION 2024-07-01..2025-07-01 read ONCE, DEV survivors only, same rule with raw p < 0.05, same sign. HOLDOUT never loaded (loader end = window end) | SOURCED backtest/splits.py |

## Arms (spec d-malkan-divergence-window-1104, added before the DEV run)

Primary arm W12 (3..12 close-based), secondary W18 (3..18), comparison columns C3_10 and C5_14. The pivot detector is
`rsi_divergence._pivots`: strict local extreme of the CLOSE, so the operator's "closes (line chart), never wicks" holds by construction.
Counts show W12 and W18 can differ only through swing pairs 13..18 bars apart.

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; counts from `study.py --pass count`, files counts.csv, regime_mix_count.txt)

DEV window regime mix (weeks, research_kit.regime_mix_line): `130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`.
Bear regime never occurs in DEV: the lowest monthly RSI in 2022 is 41.4 (raw_1d, seeded from 2020-01, so it may sit a few points above a
longer-history RSI; stated as a data limit). Bearish aligned cells are therefore EMPTY by construction.
Aligned bullish counts (W12, signal entry; retest fills 126/34/15/1): 15m 164 events / 96 days, 1h 43 / 32, 4h 18 / 17, 1d 1 / 1.
Gate inputs: n = distinct days, sd = rough unconditional BTC 10-bar return sd in % (0.8 / 1.9 / 4.0 / 10; OURS, from typical BTC volatility,
not a study outcome), cost 0.14, m = 32:
all four BLOCK (MDE + cost 0.47 / 1.48 / 4.02 / 40.2 against max plausible gross 0.30; n needed 401 / 2259 / 10014 / 62588 days).
The gate's units are R; this study has no stop, so the % return is used as the unit (stated, OURS). Even a single pre-declared cell (m = 1) blocks.

Consequence, fixed now: the DEV table is DESCRIPTIVE (measurement of an underpowered design), run because the Super Session order asks for the
numbers; a FAIL verdict cannot be issued from a cell that cannot detect a plausible effect, so the ceiling of this study's verdict is
INCONCLUSIVE (underpowered) unless a cell survives the DEV rule AND VALIDATION. BLOCKED.md holds the gate lines. No PASS is claimed without a
VERDICTS row, a causal replay test and an independent trade-loop re-run.

## What the result will say

1. RESULT.md line 1 = the window regime-mix line; line 2 = verdict.
2. Table by regime (aligned / counter / range / ungated) x TF x arm x entry: n, days, gross, net, day-clustered CI, excess over drift.
3. The gate effect = aligned vs ungated W12 rows; comparison windows beside them.

## Context
Regime: the Malkan gate itself (daily SMA200 side plus weekly/monthly RSI 60/40 band, SOURCED Malkan); divergence is taken only when aligned.
Phase: none, because this study tests the regime gate only; phase tags (OURS) are left to the next re-run.
Session: none, because session tags (OURS) are left to the next re-run.
Entry: signal-bar entry only; retest entry not tested here (OURS, next re-run).
