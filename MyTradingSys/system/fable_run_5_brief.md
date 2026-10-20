# Fable run 5 brief: the 27 grandfathered testnet sources (designed 2026-10-20 by Session_Planner; the operator runs it by hand, no session starts or messages it)

Paste-ready first (and only) message for a new Code session on Fable 5.1, in a worktree of the latest origin/fast-track:

> Read MyTradingSys/system/fable_run_5_brief.md and do it exactly as written. No questions; use the defaults named there. Reads only, one output file, then ship and stop.

Everything below is the brief. Fable gets one operator message; this file is the whole task.

## Why this pick (value per Fable token)
| # | Candidate | Value | Verdict |
|---|---|---|---|
| 1 | **Decide what the 27 grandfathered live testnet sources become** (keep / shadow / drop / re-test), with the evidence per source and the shortest route to a first promotable edge | HIGH: `promoted_setups.json` has 0 entries; every one of 27 `pre_pipeline_sources` in `execution/auto_trader_config.json` trades only on a grandfather clause tagged `review_by 2026-10-23` ("operator decision pending"); no session has written the decision; gap audit GAP-1 ranks it first; it steers what every other lane does next | **THIS RUN** |
| 2 | Fable run 4 (six setup angles) | Medium-high but blocked: needs card `fable-setups-pack-prep` shipped first (the no-hindsight pack); order set by the operator 2026-10-19 | Next, after the pack ships |
| 3 | Fable run 3 (end-to-end backtest review) | Medium-high but brief not written; `fable-major-run-design` claim on JIS-NB is designing a Fable run | Wait for that design |
Not done on trunk: grep of origin/fast-track finds no decision memo, no card and no OPERATOR_DECISIONS row for the 2026-10-23 grandfather review (only the config entries, `PROMOTION_PIPELINE.md:35-39` and the gap audit).
Fact to keep straight: `review_by` is informational and NOT enforced (`PROMOTION_PIPELINE.md:39`: expiry would silently halt trading). Nothing breaks on 10-23; the point is that the decision has an owner-less deadline and the testnet keeps sampling layers already closed as FAIL.

## Goal
Write the decision the operator would otherwise have to dig out of ten files: for each of the 27 sources, KEEP (testnet), SHADOW (signals logged, no orders), DROP (remove from the grandfather list) or RE-TEST (only with a named pre-registered cell), each backed by quoted evidence; then say which 1-3 candidates are closest to a first fee-net out-of-sample PASS and what each still needs. Premise to test, not a conclusion: "live testnet trading of these sources is information-bearing". T085 says 97 % of testnet trades end on the time exit; if that holds, testnet fills on these sources teach about plumbing, not edge, and that changes KEEP into SHADOW for most.

## Read exactly these (about 1,500 lines; do not read anything else, no internet, no backtests, no VALIDATION or HOLDOUT bars)
1. `MyTradingSys/execution/auto_trader_config.json` (the `pre_pipeline_sources` list, the `blocked`/reason map above it, `max_hold_*`), and `MyTradingSys/execution/auto_trader.py` lines 90-110 and 405-425 (default-deny path).
2. `MyTradingSys/system/PROMOTION_PIPELINE.md` (whole), `MyTradingSys/execution/promoted_setups.json`.
3. `MyTradingSys/system/layer_map.json` and the matching rows of `MyTradingSys/system/LAYERS.md` (verdict per layer, lane, owner).
4. `MyTradingSys/research/VERDICTS.csv` and `MyTradingSys/research/TRIAL_LEDGER.csv` (what each layer's tested cells say; counts are DEV only).
5. `MyTradingSys/research/BUGS.md` rows T085 and T086 only (grep them).
6. `MyTradingSys/research/gap_audit_2026-10-19/REPORT.md` GAP-1 section (claims to re-check, not to trust), and `MyTradingSys/research/fable_audit_2026-10-18/REGATE_AUDIT.md` (which studies are powered at all; m = 75 ledger count).
7. `MyTradingSys/research/fable_audit_2026-10-16/PROMOTION_REVIEW.md` and `CATALOGUE_AUDIT.md` section 1 and 5 (earlier Fable verdicts; do not repeat them).
8. `MyTradingSys/PROJECT_VISION.md` (the layers rule: fee-net out-of-sample results decide what trades; no fixed core) and the last 40 lines of `MyTradingSys/system/OPERATOR_DECISIONS.md`.
Map each of the 27 prefixes to its layer and its evidence by grep, not by memory. If a source has no evidence row, say NO EVIDENCE; that is an answer, not a gap to fill with a guess.

## Questions (answer each as CONFIRMED / WRONG / UNDECIDABLE with file:line)
1. GAP-1 claims "27 sources, 0 validated OOS PASS, `promoted_setups.json` empty". Re-count from the files. Which of the 27 prefixes cover the same layer twice (e.g. `layer:cryptocred:` plus its sub-prefixes)? How many distinct layers is it really?
2. For each distinct layer: the strongest result in VERDICTS.csv / LAYERS.md (verdict, n, split, fee-net yes/no, kill scope as written). Is any "FAIL, closed" actually only "INCONCLUSIVE" under the fixed gate (REGATE_AUDIT)? Never turn an INCONCLUSIVE into a PASS.
3. T085 (97 % time exits): what in the config (`max_hold_*`, stop/target distances) would produce it, and what would a testnet fill still tell us if it holds? Is there any source whose testnet trades are informative about edge today?
4. Which source costs the most attention or risk per unit of information (open subaccounts, live-path code paths, review load) and could be SHADOW without losing anything the lab needs?
5. Shortest honest route to a first promotable edge: of Tom v2, Fabio v2, LC3/LC4 levels confluence, CryptoCred 4h/1d, wavetrend, pit levels, name the one whose next step is cheapest and least likely to be a best-of-N artefact, with the exact blocking number (days short, MDE, cost R) quoted from the files.
6. Is there a reason NOT to act on 10-23 (e.g. the ledger count, a pending VALIDATION read, a hold)? If none, say the default.

## Expected output (one file)
`MyTradingSys/research/fable_audit_2026-10-20/GRANDFATHER_DECISION.md`:
- headline (3 lines): what to do on 10-23, the one number that drives it, what is still unknown.
- table, one row per distinct layer (with the prefixes it covers): evidence (quote + file:line), best result and split, fee-net y/n, recommendation KEEP / SHADOW / DROP / RE-TEST, one-line reason.
- the answers to questions 1-6, each marked CONFIRMED / WRONG / UNDECIDABLE.
- a card list (max 5): title, weight (ROUTINE / IMPORTANT / CRUCIAL / CRITICAL), executor (Sonnet session or agent), fail-first test. The config edit itself is a CRITICAL live-path card (Fable does not edit it).
- an operator-decision block (max 3 items), each with a default that applies if the operator says nothing.
Every number is QUOTED (file:line) or RE-DERIVED (arithmetic shown); every parameter you propose is labelled SOURCED (quote + file:line) or OURS (reason).

## Rules
- Reads only. Do not edit `auto_trader_config.json`, any code, PRE_REG, VERDICTS.csv or the ledger; do not touch the live tree, HALT files or processes.
- No VALIDATION or HOLDOUT reads, no backtests, no new studies. No testnet or mainnet account access, never read `.secrets/` or `.env`.
- Public repo: no account or order data in the file.
- Use defaults for every open question; do not ask.
- Stop when the file is complete, or the Fable weekly meter has risen 3 points, or 30 tool turns, whichever first. Put the meter before and after, and `get_usage` UTC time, in the last message.

## Ship and finish line
`python scripts/dev/sync.py start fable-grandfather-1020`, write the file, `python scripts/dev/sync.py ship --release fable-grandfather-1020`. Commit body `Result: <KEEP/SHADOW/DROP/RE-TEST counts and the 1-3 closest candidates>`. Verify: `git cherry origin/fast-track <sha>` empty AND `git ls-tree -r origin/fast-track --name-only` lists the file. Last message at most 10 lines: the headline, the counts, the card list, the meter numbers.

## After the run (Sonnet, coordinator)
Cards from the list go through the normal refine and review (CRITICAL config card gets a review session mid-session and pre-ship). Operator-decision defaults are logged `DECISION (OURS)` in SUPERVISOR_LOG.
