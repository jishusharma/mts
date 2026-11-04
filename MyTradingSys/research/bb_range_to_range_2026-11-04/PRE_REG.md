# PRE_REG: Bollinger range-to-range, by session (frozen 2026-11-04, before any return was computed)

Card `bb-range-to-range-by-session`, Super Session order d-context-retest-1104 (re-run 3). The operator's edge claim: in a range, the move from
one Bollinger band to the other repeats; Tom: larger ranges, by session. This tests the claim AS ENCODED below, not the trader's discretionary
read. Context only from `backtest/research_kit.py` (regime_tag, session_tag, retest_entry, regime_mix_line, cluster_mean_se, cluster_diff,
holm); no trend tag is written here. Code `study.py`, tests `test_range_wiring.py` (7 tests; on the pre-change stub all 7 failed with
NotImplementedError, then 7 passed). Counts (no returns published) come from `study.py --pass count` into counts.csv.

## Parameters (every one labelled)

| Parameter | Value | Label |
|---|---|---|
| Bands | BB(20, 2) of CLOSES, population std, bar i uses closes i-19..i only | OURS (common default; no transcript line found for the operator's settings; same as research/bb_state_map_2026-10) |
| Range definition | research_kit regime == "range": NOT (weekly AND monthly RSI >= 60 with close above daily SMA200, or both <= 40 with close below), read as-of the signal-bar close | band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo, "range = the rest" OURS (research_kit docstring) |
| Signal (long) | first bar of an excursion whose CLOSE <= lower band; short mirrored with CLOSE >= upper band; sides pooled in the confirmatory family | OURS |
| Target | the opposite band's value at the signal bar, fixed for the trade ("the band-to-band move") | OURS |
| Stop | entry -+ 0.5 x (distance to target), i.e. reward : risk 2 : 1 by construction; stop first when one bar touches both; gap through the stop fills at the open | OURS |
| Time-out | close of the 24th bar after the entry bar | OURS |
| Entry "signal" | fill at the close of the signal bar | OURS |
| Entry "retest" | limit at the touched band, first pullback within N=10 bars after the signal bar (research_kit.retest_entry), open if gapped, no touch = no trade; bars up to and including the fill bar are never read for the exit | N=10 OURS; the level is OURS. Disclosed: because the signal closes at/below the band, the next bar usually opens below it, so this arm is close to "enter at the next open"; its fill rate is reported |
| Session | research_kit.session_tag of the SIGNAL-bar close (asia / london / ny / late, cutoffs 08, 13, 21 UTC) for both entries | cutoffs OURS (research_kit) |
| "Larger range" (Tom) | wide = band width (upper - lower)/mid at the signal bar >= median of the prior 500 bars' widths; DESCRIPTIVE columns only, not in the family | OURS (no sourced threshold found) |
| Phase | not gated (see Context) | - |
| Timeframes | 15m, 1h, 4h, BTCUSDT 1m resampled | OURS |
| Cost | 0.14 % round trip | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost, % of entry price; day-clustered SE (cluster = UTC day of the entry bar), 95 % CI = mean +- 1.96 SE | SOURCED research_kit |
| Comparison arm | the UNGATED arm: the same events in every regime (including untagged), same TF, session, entry; gate effect = mean(range) - mean(ungated) with research_kit.cluster_diff (shared days counted). bull and bear regime rows are shown as controls | OURS |
| Confirmatory family | 15m x {asia, london, ny} x {signal, retest} x gate range x sides pooled = 6 cells, the only cells prereg_gate passes (below). Holm over m = 6 (research_kit.holm) | OURS |
| DEV survivor | family cell with n >= 30, >= 20 distinct days, net mean > 0, Holm-adjusted p < 0.05, AND range-minus-ungated difference t >= 2 | OURS |
| Descriptive cells | 15m late; every 1h and 4h cell; per-side; wide/narrow strata; bull/bear/ungated gates. Shown, never survivors, never a verdict | OURS |
| Windows | DEV: signal-bar closes in [2022-01-01, 2024-07-01) (backtest/splits.py); bars loaded only to 2024-07-01; 2020-2021 are warm-up history for SMA200 and weekly/monthly RSI only. VALIDATION 2024-07-01..2025-07-01 read ONCE, for DEV survivors only (same rule, raw p < 0.05, same sign). HOLDOUT never loaded (loader end = window end) | SOURCED backtest/splits.py |
| Verdict ceiling | The family is powered (gate PASS), so FAIL is available: no survivor = FAIL for the encoded rule on 15m asia/london/ny only. A survivor needs VALIDATION; PASS additionally needs a causal replay test and an independent trade-loop re-run (not done here, so no PASS is claimed; best case INCONCLUSIVE-pending-replication). 1h/4h/late carry no verdict | OURS |

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; n = distinct days with a range-gated signal, from counts.csv)

sd = design bound of the per-trade return, 1.5 x the median stop % in counts.csv (reward 2 stops, loss 1 stop; OURS, geometry only, no return
used). Unit % (no fixed R; stated, OURS), cost 0.14, m auto + 6 new cells = 121.

| Cell | n days | sd % | MDE + cost | max plausible | gate |
|---|---|---|---|---|---|
| 15m london | 586 | 0.64 | 0.256 | 0.30 | PASS |
| 15m asia | 656 | 0.70 | 0.259 | 0.30 | PASS |
| 15m ny | 702 | 0.88 | 0.285 | 0.30 | PASS |
| 15m late | 374 | 0.85 | 0.332 | 0.30 | BLOCK (descriptive) |
| 1h (four sessions, 137-437 days, sd 1.4-1.8) | | | 0.46-0.82 (m 139 run) | 0.30 | BLOCK (descriptive) |
| 4h (48-111 days, sd 3.2-3.4) | | | 1.6-2.2 | 0.30 | BLOCK (descriptive) |

Margins are thin (0.256-0.285 of 0.30): a pass means a gross edge of about 0.12-0.15 % per trade is detectable at 80 % power, not that one exists.
Regime mix of the DEV window (research_kit.regime_mix_line): `130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`. The range
gate keeps 80 % of 15m signals (4260 of 5315), so it is a mild gate here; "in a range" cannot be separated from "most of 2022-2024".

## What the result will say

1. RESULT.md first line = the window regime-mix line; then the verdict.
2. Table gate (range / ungated / bull / bear) x TF x session x entry: n, days, gross, net, CI, target-hit rate, gate effect and t; the 6-cell family with Holm p.
3. Descriptive: per side, wide vs narrow ("larger ranges"), 1h/4h/late cells.

## Context
Regime: range only, via research_kit.regime_tag (Malkan weekly/monthly RSI 60/40 band + daily SMA200 side); compared against the ungated arm and the bull/bear rows.
Phase: none, because the tf_break classes (research_kit.phase_tag) are not computed in this study; "range" is proxied by the regime tag alone (OURS).
Session: asia / london / ny (confirmatory) and late (descriptive) via research_kit.session_tag of the signal-bar close.
Entry: both signal-bar entry and retest entry (research_kit.retest_entry, N=10), same signals, compared.
