# PRE_REG_LONG: amendment to bb_range_to_range_2026-11-04/PRE_REG.md and bb_range_retest_2026-11-04/PRE_REG.md, long-window DEV pass (frozen 2026-11-04, before any return was computed)

Card `longdev-bb-range`. Re-measures both Bollinger studies on the long public SPOT window: A = `bb_range_to_range_2026-11-04` (e2d5f8bd1, FAIL as
encoded, 15m asia/london/ny) and B = `bb_range_retest_2026-11-04` (cceca58a9, INCONCLUSIVE, 9 cells k 0.25/0.5/1.0). Pattern copied from
`rsi_divergence_mtf_gated_2026-11-04/PRE_REG_LONG.md` (shipped 04518980). Code `study_long.py` (reuses both studies' event finder, bracket, level
arm, session-range tag, cell statistics and Holm/cluster maths unchanged, by path), tests `test_long_wiring.py`, gate runner `gate_long.py`. Counts
(no returns) are in `counts_long.csv`, `regime_mix_count_long.txt`, gate lines in `BLOCKED_LONG.md`. TRIALS.md rows were written before the dev pass.

## Why

Run A had a powered family and failed; run B was underpowered (146-186 days per cell vs 478-1783 needed). The only change here is more history
(2017-08..2024-06 instead of 2022-01..2024-06) plus one OURS bear proxy. A re-measurement, not a new idea.

## Reused unchanged

Every arm and parameter of both PRE_REGs: BB(20,2) of closes (OURS); first-excursion signal; target = opposite band, stop 0.5 x distance, 24-bar
time-out; entries signal and next-open-style "retest" (N=10) for A; re-entry close within M=10 then touch of level +- k ATR(14) within N=10,
k in {0.25, 0.5, 1.0} for B; range gate = research_kit regime == "range" as-of the signal-bar close (Malkan weekly AND monthly 60/40 SOURCED,
daily SMA200 side); session = research_kit.session_tag of the signal-bar close (asia/london/ny confirmatory, late descriptive; cutoffs OURS); the
session-range tag of B and the band-width "wide" stratum of A are OURS and are NOT the trader's (no transcript line found); cost 0.14 % round
trip SOURCED; day-clustered SE and 95 % CI; survivor rule n >= 30, >= 20 days, net > 0, Holm p < 0.05, gate-effect t >= 2. The strict Malkan bear
gate (weekly AND monthly RSI <= 40) is NOT changed and stays PRIMARY.

## Data and windows (honest split definition)

- Binance SPOT klines 2017-08..2024-06 read at their native 15m / 1h / 4h / 1d (`F:/MTS/Dumps/backtest/spot_2017`, `klines_history_2017/README.md`), not
  futures 1m, not spliced. The originals resampled futures 1m, so cells are comparable in size and sign only, not bit-for-bit.
- `backtest/splits.py`: DEV 2022-01-01..2024-07-01, VALIDATION 2024-07-01..2025-07-01, HOLDOUT 2025-07-01+. 2017-08-01..2021-12-31 is declared NEW DEV
  data (PRE_DEV in splits.py terms; no return from it was read by either card: both used 2020-2021 only as indicator warm-up). splits.py is not edited.
- Long DEV = events with signal-bar close in [2017-08-01, 2024-07-01). Data is loaded only to that instant. The first ~65 weeks have no regime (SMA200,
  monthly RSI14): their events are dropped from EVERY gate row, so the ungated control ("all") is TAGGED events only. The originals' ungated arm
  included untagged events, but their window had none (the whole 2022-2024 window was tagged), so the comparison is like for like. VALIDATION is read
  once, for survivors only (same rule, raw p < 0.05, same sign); HOLDOUT is never loaded (loader end = window end).
- The 2022-2024 part of the long window was already seen in the original runs, so the new-data-only effect is not isolated (a fresh-vs-old split is not
  pre-declared and is not computed).
- Spot archive has exchange-maintenance gaps (9-25 per series): "24 bars" means 24 bars present, not filled.

## Bear proxy arm P40 (decision d-bear-proxy-1104; OURS, never Malkan's; the operator may overrule with "strict only")

The primary bear gate never fires (0 bear weeks even over 2017-2026; monthly RSI14 has not been <= 40 since 2017-08). Exactly ONE proxy arm is added,
defined exactly as in the sibling pass: **P40: bear regime = weekly RSI14 <= 40 alone (monthly ignored) AND daily close below SMA200; bull and range exactly
as the primary.** It is the gate row `bearP40`, applied to the same confirmatory cells as the range gate: A 15m x {asia, london, ny} x {signal, retest} = 6 cells,
B 15m x {asia, london, ny} x k {0.25, 0.5, 1.0}, tagged = 9 cells. The range gate itself is NOT redefined under P40, so a P40 event is also a range event
under the primary tag (weekly <= 40 with monthly above 40 is "range"); the two rows overlap and are reported side by side, not as a partition. Label: OURS.

## Confirmatory family and Holm

Primary: A range 6 + B range 9 = 15 cells. Proxy: the same 15 cells under bearP40. **Pooled Holm family m = 30** (empty cells count through m), applied with
rk.holm over every non-empty cell of the 30 (one pooled correction across both studies, stricter than within-study). Survivor rule as above, with the
gate effect = cell minus the ungated TAGGED control (A: all tagged events, same session and entry; B: all-regime tagged events, tagged, same session and k).
Everything else (1h/4h, late, sides, wide/narrow, untagged, Malkan bull/bear rows) is descriptive: never a survivor, never a verdict.

## Power gate (scripts/dev/prereg_gate.py via gate_long.py, run on counts_long.csv BEFORE any return; full lines in BLOCKED_LONG.md)

n = distinct days of the cell, sd = 1.5 x median stop % (design bound, geometry only, OURS), unit %, cost 0.14, m = `auto` (repo-wide DEV variants) + 30 = 150.

| Family | Cells | Days per cell | MDE + cost (max plausible 0.30) | Gate |
|---|---|---|---|---|
| A range (signal and retest) | 6 | 1270-1465 | 0.236-0.250 | PASS (FAIL available) |
| A bearP40 | 6 | 318-378 | 0.344-0.372 | BLOCK |
| B range | 9 | 316-394 | 0.375-0.517 | BLOCK |
| B bearP40 | 9 | 68-89 | 0.654-1.117 | BLOCK |

6 PASS, 24 BLOCK. Verdict ceilings: study A on its primary range family is powered, so no survivor = FAIL for the rule as encoded on the long window; a
survivor needs VALIDATION and cannot be PASS without a causal replay and an independent trade-loop re-run (not done: best case INCONCLUSIVE-pending-replication).
Study B and every bearP40 cell are BLOCKED: descriptive, ceiling INCONCLUSIVE (a negative table is "underpowered", never FAIL).

## What the result will say

RESULT_LONG.md line 1 = `Regime mix:` line of the long DEV window with BOTH bear counts (primary Malkan and proxy P40); then the verdict per study, the
per-cell table long vs original (n, net, CI, hit, Holm, gate effect), the retest-arm fill rate on the long window against the original 59-77 % and the
earlier next-open 99.9 %, and the P40 arm side by side.

## Context
Regime: range via research_kit.regime_tag (Malkan weekly/monthly RSI 60/40 SOURCED + daily SMA200 side), plus ONE OURS proxy P40 (weekly RSI14 <= 40 alone, below SMA200) side by side, compared against the tagged all-regime arm.
Phase: none from tf_break classes; for B the entry itself is the phase (excursion beyond the band, re-entry close, retest of the band), "range" is proxied by the regime tag (OURS).
Session: asia / london / ny (confirmatory) and late (descriptive) via research_kit.session_tag of the signal-bar close, plus the OURS session-range tag in B; attribution to the trader or Tom is NOT claimed.
Entry: A signal-bar entry and next-open-style retest entry (N=10); B retest-level arm (re-entry close, then touch of level +- k ATR within N=10, k in {0.25, 0.5, 1.0}), same as the originals.
