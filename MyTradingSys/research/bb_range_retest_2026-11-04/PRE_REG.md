# PRE_REG: Bollinger band retest-LEVEL arm, by session (frozen 2026-11-04, before any return was computed)

Card `bb-range-retest-level-arm` (context re-run 3b, Super Session order d-context-retest-1104). The earlier study `bb_range_to_range_2026-11-04`
(e2d5f8bd1, FAIL) had a "retest" entry that filled 99.9 % of signals, i.e. the next open, so the operator's context rule (enter on the
return to the band, not at the extreme) was never applied. This study encodes a real return-to-the-band entry. It tests the claim AS
ENCODED below, not the trader's discretionary read. Context only from `backtest/research_kit.py` (regime_tag, session_tag, retest_entry,
regime_mix_line, cluster_mean_se, cluster_diff, holm); no trend tag is written here. Events, bracket, cell statistics and data loading are
reused by path from `bb_range_to_range_2026-11-04/study.py`. Code `study.py`, tests `test_level_arm.py` (5 tests; on the pre-change stub all 5
failed with NotImplementedError at study.py:17, then 5 passed). Counts (no returns) come from `study.py --pass count` into counts.csv.

## Parameters (every one labelled)

| Parameter | Value | Label |
|---|---|---|
| Bands | BB(20, 2) of CLOSES, population std, bar i uses closes i-19..i only | OURS (as the earlier study) |
| Signal | first bar of an excursion whose CLOSE <= lower band (long) / >= upper band (short); level = the band touched at that bar (static), target = the opposite band at that bar (static); sides pooled in the family | OURS |
| Step 1: re-entry | first close back INSIDE the band within M = 10 bars after the signal bar (long close > level, short close < level); none = no trade | M OURS |
| Step 2: touch | resting limit at level +- k x ATR(14 at the signal bar) on the inside of the band; first bar within N = 10 bars after the re-entry bar whose low (long) / high (short) reaches it (research_kit.retest_entry); fills at the limit, or at the open if gapped; no touch = no trade | k grid {0.25, 0.5, 1.0} OURS; N OURS; ATR(14) OURS |
| Exit | static opposite band as target; stop = entry -+ 0.5 x (distance to target) (reward : risk 2 : 1); stop first when a bar touches both; gap through the stop fills at the open; time-out close of the 24th bar after the fill bar; the re-entry and fill bars are never read for the exit | OURS (as the earlier study) |
| Range gate | research_kit regime == "range", read as-of the signal-bar close | band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo, "range = the rest" OURS |
| Session | research_kit.session_tag of the signal-bar close (asia / london / ny confirmatory, late descriptive) | cutoffs OURS (research_kit) |
| Session-range tag ("larger range", Tom) | the signal bar's session has a running range (high - low so far, % of close, incl. the signal bar) STRICTLY above the median of the final ranges of the previous 20 same-name sessions (>= 10 needed, else untagged); as-of | OURS: no transcript line for Tom or the trader was found, so the rule and every number in it are OURS and are not attributed to the trader (coordinator correction 2026-11-04) |
| Cost | 0.14 % round trip | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost, % of entry price; day-clustered SE (cluster = UTC day of the fill bar), 95 % CI = mean +- 1.96 SE | SOURCED research_kit |
| Comparison arms | (a) ungated: same tagged events in every regime, difference via cluster_diff (vs_ungated); (b) untagged: range-gated events without the tag (vs_untagged, descriptive); (c) concept-only row: the e2d5f8bd1 signal and "retest" entries, copied from its dev_cells.csv, not re-run | OURS |
| Confirmatory family | 15m BTCUSDT x {asia, london, ny} x k {0.25, 0.5, 1.0}, range gate, tagged, sides pooled = 9 cells, Holm over m = 9 (research_kit.holm) | OURS |
| DEV survivor | family cell with n >= 30, >= 20 distinct days, net mean > 0, Holm-adjusted p < 0.05, AND tagged-range minus tagged-ungated difference t >= 2 | OURS |
| Descriptive cells | 15m late; per side; untagged and any-tag arms; all-regime arms; never survivors, never a verdict | OURS |
| Fill-rate check | fills / signals (and fills / re-entered signals) per cell is reported; the arm is INVALID (and RESULT says so) if it is >= 95 % like the earlier "retest". Counts: 59-77 % of signals fill, about 91-99 % of re-entered ones (counts.csv) | OURS |
| Windows | DEV: signal-bar closes in [2022-01-01, 2024-07-01) (backtest/splits.py); bars loaded only to 2024-07-01. VALIDATION 2024-07-01..2025-07-01 read ONCE, for DEV survivors only (same rule, raw p < 0.05, same sign). HOLDOUT never loaded | SOURCED backtest/splits.py |
| Verdict ceiling | The power gate BLOCKS every family cell (BLOCKED.md): the tag keeps about a quarter of signals (146-186 days per cell vs 478-1783 needed). So FAIL is not available: the best case is INCONCLUSIVE, and a negative DEV table is reported as underpowered, never as FAIL. No PASS is claimed (no replay or independent trade-loop re-run) | OURS |

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; n = distinct days with a range-gated tagged fill, from counts.csv)

sd = design bound 1.5 x the median stop % in counts.csv (geometry only, no return used; OURS), unit %, cost 0.14, m auto + 9 new = 127. Full output in
BLOCKED.md: every one of the 9 cells BLOCK (MDE + cost 0.40-0.67 vs 0.30 max plausible). Regime mix of the DEV window:
`130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`. The range gate is mild here (81 % of weeks), so "in a range" cannot be separated
from "most of 2022-2024".

## What the result will say

1. RESULT.md first lines = `Regime mix:` line, then the verdict.
2. Family table (9 cells): n, days, fill rate, gross, net, CI, target-hit, Holm p, vs_ungated t.
3. The e2d5f8bd1 run as the concept-only comparison row; the fill-rate comparison (99.9 % vs this arm).

## Context
Regime: range only, via research_kit.regime_tag (Malkan weekly/monthly RSI 60/40 band + daily SMA200 side); compared against the all-regime arm.
Phase: none from tf_break classes; the entry itself is the phase (excursion beyond the band, re-entry close, then the retest of the band); "range" is proxied by the regime tag (OURS).
Session: asia / london / ny (confirmatory) and late (descriptive) via research_kit.session_tag of the signal-bar close, plus the OURS session-range tag.
Entry: retest-level arm only (re-entry close inside the band, then touch of level +- k ATR within N bars; research_kit.retest_entry); the earlier next-open "retest" is a concept-only comparison row.
