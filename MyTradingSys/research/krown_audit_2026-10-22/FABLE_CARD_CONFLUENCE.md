# CARD: Fable confluence run: each layer in its role, trades with measured edge, confidence and accuracy (DEV + DEV_EXT only)

Status: DESIGN ONLY. Not started. Written 2026-10-22 by the Krown-audit session, after an independent Opus review
(`REVIEW_OPUS.md`, SOUND WITH FIXES; all 13 amendments folded in, see `LAYER_CONFLUENCE_DESIGN.md` s9). Format follows
`research/fable_major_run/CARD_2026-10-20.md`.
Machine: a host with `F:/MTS/data` (event-table inputs, `krown_daily`, 1m files for DEV_EXT): DESKTOP-F7IU69N or JIS-NB.
A cloud container cannot run S1-S4 (no F: data).

## 1. Goal (one sentence)
Find out, on DEV and DEV_EXT only, whether giving each layer a role (CONTEXT, REGIME, LOCATION, TRIGGER, RISK, JUDGE) produces
trades with a fee-net gross edge above cost, using Krown's context only where it first passes a standalone read; pre-register what
survives for one VALIDATION read; define a per-trade confidence that is a calibrated probability.

## 2. Why this run, from the record
- No layer passes alone (LAYERS.md status lines). The binding constraint is the fee wall (`research/bb_top_reversal_2026-10-18/BLOCKED.md`:
  cost 0.349 R at a 15m stop): edge must be measured as gross % against cost %, not as a smaller cost/R (REVIEW_OPUS F3).
- A context study already ran and was INCONCLUSIVE (`research/context_factors_2026-10-16/RESULT.md`: E = -0.0233 R, SE 0.0739,
  241 of 387 matched days, Holm m = 37). This run must say what is different (a standalone read, a sizing arm, a structural trade)
  and reuse its tools (`context_factors_pit_2026-10-16/context_asof.py`, `context_null_2026-10-16/context_null.py`, DEV_EXT counts).
- Governance: PROJECT_VISION.md:262 "Confluence may gate a trade only after each input passed S3 on its own."
- Krown's own order of importance (trend > volatility > structure > momentum, `krown_capture_2026-10-16/transcripts/ta101_missing4/hNfjyrJEytI_timed.txt`
  00:10:22-00:10:50) gives the role order; all thresholds stay OURS.
- Fable is used where judgement matters: role assignment, trade design, falsification plan, pre-registration, verdict. Counting
  and runs go to Sonnet/Haiku first and are re-derived independently.

## 3. Data
| Set | What | Source |
|---|---|---|
| D1 | BTC 1d/1w closed bars 2017-08..2024-06-30 (1w has 8 gaps in 2022: rebuild 1w from 1d) | `F:/MTS/data/krown_daily/` (DATA_MANIFEST.csv checksums) |
| D2 | BTC perp 15m/1h/4h bars, DEV 2022-01-01..2024-06-30; DEV_EXT 2020-01-01..2021-12-31 where 1m files exist | each event table's `load_dev_*`; `context_factors_2026-10-16/COUNTS_DEV_EXT.md` for coverage |
| D3 | DEV event tables of usable trigger layers (exclude oi_delta: no rows; turn_of_candle: not a trigger; bigtrade only post-fix rows): bb_top_reversal, malkan_rsi, rsi_divergence, rsi_reclaim, session_levels, session_momentum, cc_msb, fabio_escalation, fabio_lvn_touch, funding_extreme, candle_pattern, volume, wlow_bounce `events.csv` | `research/layer_lab/*_event_table/event_table.py` (regenerate) |
| D4 | Krown context rows (S1 output); funding only (no OI before 2025-09) | `run/context_dev.csv` |
Never read: VALIDATION 2024-07-01..2025-06-30 (one pooled read, a later card), HOLDOUT 2025-07-01..2026-09-30, live state, account data.
Access log: every file opened with bar min/max in `run/ACCESS_LOG.md`.

## 4. Step plan
| Step | Model | Turns | Output | Done when |
|---|---|---|---|---|
| S0 Registry fix | Haiku 5.5 | ~5 | gate_board krown G2 with proof KROWN_SETUP_CATALOG.md; LAYERS/STATUS regen; STATE.md corrected (4 transcripts on disk since 2026-10-16); catalogue F1/F2 patch (REPORT.md A1, A2, A6) | `make_status.py` shows krown G2 |
| S1 Context table + counts pass (NO outcome read) | Sonnet 5.5 | ~25 | `backtest/layers/krown/krown_context.py` (pure; trend_1d/1w, naive trend baseline, BBWP 1d/4h + expansion direction, zone/range-edge distance in ATR, range position; point-in-time: a row is usable only after its close + write latency; events keyed at decision time = bar open + tf) + `test_krown_context.py` (hand numbers from FORMULAS.md; fails on pre-change code; a shifted-join test that must fail); `run/COUNTS.md`: D1/D2/D3 shares per layer, S histogram, D3 coverage, distinct ISO weeks per cell, week-clustered MDE per layer, cost/R distribution; outcome columns written only to `run/sealed/` | tests pass; COUNTS.md committed; bands frozen from counts |
| S2 Fable design + pre-registration | Fable 5.1, effort high | ~25 (cap 30) | `FABLE_DESIGN.md` + `PRE_REG_CONFLUENCE.md` (prompt in s5) committed before any outcome is opened | git order proves PRE_REG precedes S3 |
| S3 Standalone context read | Sonnet 5.5 | ~15 | `run/CONTEXT_READ.md`: (a) D1 vs naive trend baseline on random entries with context-matched controls, signed 24 h net return; (b) BBWP_4h/1d -> next-24 h realised volatility (rank correlation, calibration); DEV and DEV_EXT; week-clustered | verdicts per PRE_REG; a failed (a) closes the Krown CONTEXT role for filters |
| S4 Trial runs | Sonnet 5.5 | ~25 | `run/DEV_RESULTS.md`: T2 primary (taker 0.10 %, 0.14 %, maker 0.02 % + fill haircut); sizing arm (1 / predicted vol, x (1 + 0.5 D1) only if (a) passed) at equal capital; pooled conditional read of D3 layers only if (a) passed (random-effects meta-analysis, weight cap, placebo = matched random entries + 200 circular shifts >= 30 days); year split 2022 vs 2023-24H1; every variant in `research/layer_lab/TRIALS.md`; Haiku re-derives 3 numbers from FORMULAS.md | all PRE_REG tests reported, including the failures |
| S5 Fable verdict | Fable 5.1 | ~10 | `FABLE_VERDICT.md`: what goes to the single VALIDATION read (one pooled trial), what dies, what alert-only tags testnet should carry | written; no VALIDATION read |
| S6 Ship | Haiku 5.5 | ~3 | `sync.py ship` | Result line in the commit |
Order is strict: S2 after S1 ships; S3/S4 after PRE_REG is committed; S5 after S4 ships.

## 5. The Fable prompt (S2; paste as the first message)
```
You are the design lead for MTS confluence, step S2 of research/krown_audit_2026-10-22/FABLE_CARD_CONFLUENCE.md.
Read in order: FABLE_CARD_CONFLUENCE.md; LAYER_CONFLUENCE_DESIGN.md (section 9 first, it supersedes earlier sections);
REVIEW_OPUS.md; REPORT.md; run/COUNTS.md; MyTradingSys/system/LAYERS.md; research/context_factors_2026-10-16/RESULT.md and
PRE_REG_V2.md; the REPORT.md of each event table in research/layer_lab/*_event_table/; research/bb_top_reversal_2026-10-18/BLOCKED.md;
research/wlow_bounce_bbrsi60_2026-10-16/RESULT.md; MyTradingSys/PROJECT_VISION.md lines 255-265.
Never open run/sealed/ or any outcome column. Never read a bar >= 2024-07-01.

1. Role table: assign every layer one role (CONTEXT, REGIME, LOCATION, TRIGGER, RISK, JUDGE) with the evidence file:line;
   merge same-object layers (e.g. Krown range edges = Tom balance edges; Krown break-close = candle_close); say which roles are empty.
2. Using COUNTS.md only: mark each trigger layer TESTABLE (week-clustered MDE <= 0.10 R per unit), DESCRIPTIVE, or DROP
   (cost/R median > 0.25 at its natural stop and no horizon extension makes gross move >> cost).
3. State in one paragraph why this run is not a rerun of context_factors_2026-10-16 (what is new, what was learned there).
4. Trades, at most 5, T2 first (Krown S8 on 4h, KR-Q05 stop, KR-Q06/KR-R07 exit). For each: timeframe, side rule, the context
   conditions (only those allowed by the S3 standalone read; write both branches: if (a) passes / if it fails), trigger, stop,
   exit, size rule (vol-target), expected n on DEV and DEV_EXT, gross move needed to clear 0.10 % and 0.14 % cost, the single
   claim tested, and the result that kills it.
5. Confidence output: logistic of sign(net) (target-first for T2) on D1/D2/D3 with layer intercepts; 3 reliability bins;
   Brier on VALIDATION once. Say what the alert tag on testnet shows and that it gates nothing.
6. PRE_REG_CONFLUENCE.md: the single Holm family (context read (a), pooled test, per-layer slopes, T2, T4), week clustering or a
   20-day block bootstrap, placebo (matched random entries + 200 circular shifts >= 30 days), pass bars fixed now, the rule that a
   DEV positive must agree in sign on DEV_EXT before VALIDATION, and VALIDATION as one pooled trial.
Label every number SOURCED (quote + file:line) or OURS. Write FABLE_DESIGN.md and PRE_REG_CONFLUENCE.md, commit, sync.py ship.
Stop and ship what exists if the all-models weekly allowance rises 6 points during the run.
```

## 6. Success test (fixed now)
Pass = all of: (1) the shifted-join test fails and the real join passes; (2) COUNTS.md (n, weeks, MDE per layer and cell) is committed
before PRE_REG; (3) PRE_REG precedes CONTEXT_READ and DEV_RESULTS in git order; (4) every pre-registered test is reported with
placebo, year split and cost scenarios, failures included; (5) ACCESS_LOG shows no bar >= 2024-07-01.
Fail = any VALIDATION/HOLDOUT read, a band or threshold changed after an outcome was seen, an unlabelled number, or a confluence gate
proposed for live before the context passed its standalone read (PROJECT_VISION.md:262).

## 7. Labels and rules
SOURCED vs OURS on every parameter; Krown's, Malkan's and the operator's hit rates are hypotheses; DEV is in-sample and positives are
hypothesis-generating (every trigger already failed or was inconclusive on this DEV: survivorship); testnet only; no live wiring in
this card; no runtime/order/account data in commits; no schedulers.

## 8. Budget
Fable: S2 ~25 turns + S5 ~10. Sonnet/Haiku for S0, S1, S3, S4, S6. Stop rule: ship what exists if the all-models weekly allowance rises 6 points.

## 9. Ship
Slugs: `confluence-s0-registry`, `confluence-s1-context-counts`, `confluence-s2-fable-design`, `confluence-s3-context-read`,
`confluence-s4-dev-trials`, `confluence-s5-fable-verdict`. Commit Result lines state the file and the number.
