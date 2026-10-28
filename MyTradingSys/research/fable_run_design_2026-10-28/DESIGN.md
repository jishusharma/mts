# Fable run design, 2026-10-28 (Lead, Opus, login C): R6 DECIDING PRE-REG

**Goal (one sentence):** freeze the one pre-registered, powered, fee-net test that confirms or kills the BTC trading-edge program, using event counts only (no outcome read), so a Sonnet session can run it mechanically and one VALIDATION read settles it.

**Value, as the operator defines it** (SOURCED `PROJECT_VISION.md:226-229`): "MTS exists to trade BTC with a proven net edge after fees"; stage S3 = walk-forward OOS net R > 0, CI above 0; no source has passed S3. Fee-net OOS results decide what trades (`PROJECT_VISION.md:13-15`, direction 2026-10-13). So the most valuable run is the one that moves S3 to a yes/no.

**Why now:** R1 (`research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` sec. 4) found every 1m-2h family dead on cost (best gross 3.8 bp vs 14 bp) and named the only open path: a 4h-and-up rule with enough events (E1 counts screen, then E2 one pre-registered run). R2 (power pre-reg) logged usage but never wrote `R2_POWER_PREREG.md` (only `USAGE.md` R2 rows on trunk; `git log --all -- '*R2_POWER_PREREG*'` empty). Nobody owns E1/E2: no card references R1. R6 = R2's missing deliverable fused with R1's E1+E2 design.

## Candidates

| Candidate | Value to the operator | Cost | Verdict |
|---|---|---|---|
| **R6 deciding pre-reg (this)** | Directly answers S3: a frozen test whose pass/fail decides whether the trader-source program continues | ~35 turns, ~3 Fable weekly pts | **RUN** |
| R4 overhead cut list (`lead/2026-10-28_fable-runs-top5.md`) | Saves commits/quota; not the edge goal; dedupe audits (d-dedupe-lean-no-contradiction cards) already cover half | ~25 turns | later, Sonnet-able part already carded |
| R5 live-validation protocol review | Makes detector checks sound; R1: detector validation is not profit validation | ~25 turns | later; does not move S3 |
| fable-run4-setup-angles (6 new angles) | New ideas add trials to a 281-row bill (z >= 3.75 needed); rare events stay unpowered | ~40 turns | drop until R6 says a family is powerable |

Carry executability memo (R1 E3) is a 5-turn Sonnet job, not a Fable run; R6 files it as a card.

## Inputs the run reads (all on trunk 2026-10-28)
1. `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` (sections 2-4: bill, minimum effect table, E1/E2 rules). Do not re-litigate its verdict table.
2. `backtest/layers/FORMULAS.md` fees section; `backtest/fees.py:27-28`; `backtest/power_mde.py` (MDE/n_needed helper).
3. `backtest/PRE_REG_TEMPLATE.md` (12 items every pre-reg must answer).
4. `research/layer_lab/TRIALS.md` (count of tries; rows for Krown S5 `:280`, Malkan 1d `:274`).
5. `research/pit_levels_2026-10-16/PRE_REG_V2.md` (Holm formula, power gate) and `research/BUGS.md` B187 (DEV_EXT facts, F:/MTS/data/dev_ext_2019_2021 may be missing).
6. `research/context_factors_2026-10-16/COUNTS_DEV_EXT.md`; OPERATOR_DECISIONS `D3-dev-ext`.
7. Event definitions: `research/sim_desk/studies/krown.py`, `rsi.py`, `_bars.py`; `research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md`; `research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md`; card `krown-dev-event-study`.
8. `research/design_cards_2026-10-26/FABLE_FEE_STOP_RULE.md` (stop >= 4x round-trip fee).
Data: klines only (timestamps + OHLCV). BTC/ETH/SOL 4h and 1d public Binance klines may be fetched (pre-approved public data; tiny files). Every bar at or after 2024-07-01 00:00Z is refused (VALIDATION/HOLDOUT sealed).

## Output it must write
`research/fable_run6_powered_prereg/PRE_REG.md` (max 3 pages) + `counts_only.py` + `COUNTS.csv`:
1. Counts table per family x timeframe x symbol (BTC DEV, DEV_EXT if on disk else NOT_IN_DATA, ETH, SOL): events, n_needed (sd 1.37 R, cost_R = 0.14 % / median stop %, plausible 0.30 R, Holm m = family cells; all OURS except formulas SOURCED), POWERED yes/no.
2. If one family is POWERED: the frozen pre-reg (all 12 template items; universe, event rule, cooldown, entry delay, stop >= 4x fee, exit, <= 9 cells, Holm, per-UTC-day cluster correction across symbols, DEV pass t >= 3.24, VALIDATION pass t >= 2.0 same sign). If none: a STOP verdict for the BTC trading-edge program with the R1 STOP list as cards.
3. Cards via `tasks.py new` + `fill` (twins first): E2 DEV run (SONNET), the one VALIDATION read (blocked until operator told, one-line ask), carry memo E3 (SONNET). `tasks.py check`; revert any other card it rewrites.
4. `research/fable_runs_2026-10-28/USAGE.md` R6 rows (get_usage start/end).

## Stop conditions
- Weekly Fable meter +4 pts from start, or 5 h window >= 85 %, or 45 tool turns, or context >= 60 %: write what exists, ship.
- Any code path reads an outcome column (forward return, PnL, R) or a bar >= 2024-07-01: STOP, void the counts, report. `counts_only.py` must assert both.
- Done the moment the pre-reg (or STOP verdict) and cards are shipped; no outcome run inside R6.

## Estimate (OURS)
~35 turns, 40-60 min wall, peak context ~300 k, ~3 Fable weekly pts (R1 reading run cost 2 pts, `USAGE.md` R1 rows). Login C 5 h window +10-15 %.

## What would make it a waste
Re-arguing R1's dead families; reading any outcome (burns the only clean test); building detectors or fixing Krown recall (STOP list); a pre-reg a Sonnet session cannot run without asking (missing item from the 12); fetching 1m data (4h/1d suffice for counts).

## Done when (checkable on the recorded run)
`git cherry origin/fast-track` empty for the run's branch, and on trunk: `research/fable_run6_powered_prereg/PRE_REG.md` with the counts table and either a frozen pre-reg (12 items) or a STOP verdict; `COUNTS.csv` row count equals the table rows; `counts_only.py` contains the sealed-cut and no-outcome asserts; >= 2 new READY/refined cards naming PRE_REG.md; USAGE.md R6 start/end rows; commit body `Result:` = POWERED family (or STOP) + n_available vs n_needed.

DECISION (OURS): counting is done inside the Fable run (bounded by its script, about 6 turns) instead of a separate Sonnet card first, because a hand-off would stall the decision a day and the counts are what the judgement needs.
DECISION (OURS): output dir is date-free (`fable_run6_powered_prereg/`) so the run can start on any day.
