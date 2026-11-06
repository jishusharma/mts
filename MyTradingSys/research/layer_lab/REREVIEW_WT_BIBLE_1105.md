# Re-review: WT Bible SPEC.md after bbaa2d3f1 vs the 8 defects of REVIEW_GEMINI_1104.md (2026-11-05, blind, Builder)

Target `research/wt_bible_studies_2026-11-04/SPEC.md` (24 lines). Checked against `backtest/splits.py:4-6` and `backtest/layers/wavetrend/wavetrend.py:62-70` (`htf_index`). Defects 1,3,4,5 were also read blind in a365fdfc (RESOLVED); this pass re-checks all 8 from the file as it stands.

| # | Old defect | Status | Line evidence |
|---|---|---|---|
| 1 | E1/E7 burned VALIDATION/HOLDOUT feeds the Card 1 verdict | CLOSED | SPEC l.5 discloses the seen bars; l.17 says a BTCUSDT 2024-07..2025-06 read is exploratory, the PRE_REG must name an unpeeked target, and the builder adds the `holdout_reads.csv` row via `splits.read_holdout`. `research/holdout_reads.csv` exists. |
| 2 | E2 cites non-existent `system/layer_bible/wavetrend.md` | OPEN | SPEC l.2 still cites it; the file is absent on disk (only `research/gemini_burn_2026-10-25/layer_facts/wavetrend.md` and `research/gpt_rederive_2026-10-26/layer_rederive/wavetrend.md` exist). l.10 and l.12 also say "Bible" with no resolvable path. Fix: cite a real file or commit the verbatim operator transcript. |
| 3 | E5 unfrozen bins and m | CLOSED | l.14 freezes all five bins (terciles on DEV only, 0-12/12-24/>24, 21-08/08-13/13-21, lower/not, up/down); l.15 m = 14 marginal cells with the arithmetic shown. |
| 4 | E2/E3 colloquial divergence rule | CLOSED | l.11 gives dip bar = min wt1 between crosses, window = dip bar..confirming bar, k = 3 bars OURS; l.12 gives "waves above 0" = down-cross with min(wt1,wt2) > 0. Residual in N1. |
| 5 | E4/E3 invalid paired difference (Card 2) | CLOSED | l.21 replaces pairing with nested mean minus rejected-dot mean, day-block bootstrap, n_nested and n_rejected stated. |
| 6 | E3 Card 3 cycle uses "last valid top before next bottom" (non-causal, half cycle) | OPEN | l.24 unchanged: "full cycle = valid bottom up-cross to the last valid top before the next bottom". Still needs the next bottom to know the last top, and measures only the up leg. Acceptable only if Card 3 is labelled retrospective-descriptive and `layer_state.py` is forbidden to use it live; SPEC l.24 says it feeds `layer_state.py`. Fix: bottom-to-next-bottom period, plus a causal state rule for the live line. |
| 7 | E3 4h slope alignment / lookahead | OPEN | l.13 ("4h wt1 slope"), l.14, l.21 (sign of wt1 now minus wt1 three 4h bars ago) never say closed 4h bars only or `htf_index` (`wavetrend.py:62-70`, open + htf_ms <= t). l.3 says "closed bars" only for the base data. |
| 8 | E6 no slippage / latency | OPEN (LOW) | l.3 fee 0.14 % only; l.11 enters at the confirming bar close; no slippage buffer or next-open rule anywhere. |

## New defects (max 6)
- N1 [E3] l.11 "wt1 >= 45 and at least 10 higher": higher than what is undefined (the confirming cross's wt1? the dip? the second high?). Builder cannot implement without guessing.
- N2 [E5/E3] l.16 lists two metrics, net bp at 24 bars and first-touch -1 % vs +1 %, while l.11 fixes the exit at 24 bars "never earlier". The two exits contradict, and the second metric multiplies the cells m = 14 counts (no m for it). Pick one primary, the other descriptive and outside m.
- N3 [E2] l.14 tercile edges of DEV events are computed on DEV but l.15 counts the "his-context subset" as a cell without saying it is binary vs the rest or vs the non-context events.

## Judgement
Closed: 1,3,4,5 (the four HIGH items). Open: 2 (MEDIUM), 6 (MEDIUM), 7 (MEDIUM), 8 (LOW), plus N1, N2 which block an exact implementation of Card 1. Defect 7 and N1/N2 change what a builder computes, so the three WT cards cannot take a real REVIEWED stamp yet.

VERDICT: FIX-FIRST
