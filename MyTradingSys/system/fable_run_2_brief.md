# Fable run 2 brief: re-gate every pre-registration under the fixed gate

Self-contained brief for one Fable 5.1 session that the operator starts by hand. Reads and gate arithmetic only: no outcome study, no VALIDATION or HOLDOUT read, no code edits.

## Where run 1 left off
- Run 1 (`fable_run_1_brief.md`, result `research/fable_audit_2026-10-18/GATE_AUDIT.md`, commit b63e8589) found four faults in `scripts/dev/prereg_gate.py`:
  - sd was in SD units while cost was in R (Q1);
  - the median-cost input was lenient (Q2);
  - Holm m had no single source (Q3);
  - count-only cells were in no trial ledger (Q6).
- It used 1 Fable weekly point (23 % -> 24 %).
- gate-fix-1..5 shipped in 8f988e38 (cards done in f48bd5b5). The gate now:
  - takes `--sd` as sd of per-event R, and exits 2 when sd < 1 without `--sd-source`;
  - has `--m auto --new-cells`;
  - uses `mean_cost_R`;
  - gives verdicts.py a BLOCKED verdict and a `--ledger` option.
- gate-fix-6 (promote.py floor) is still raw and is out of scope here.
- Every pre-registration written before 8f988e38 was gated with the old rule or by hand. Nobody has re-gated them.

## Why this pick (value per Fable token, re-scored 2026-10-18)
| # | Candidate | Value | Fable token cost | Verdict |
|---|---|---|---|---|
| 1 | Re-gate all 21 pre-registrations that use the MDE gate under the fixed rule; say which ADMIT/BLOCK flips, and give go/no-go for pending one-shot DEV reads | HIGH: run 1 showed the old gate mislabels units and under-states cost. Any of the 21 may be a layer killed wrongly (4 BLOCKED: kurisko, pit, bb_top, eur_low) or a one-shot DEV read about to be spent on an under-powered design (context-composite-v2-dev-read is READY now). Choosing sd per study is judgement, not mechanics. | LOW-MEDIUM: about 1,900 lines, reasoning plus cheap `prereg_gate.py` calls, no data runs | **PICK** |
| 2 | Pre-run audit of the context-factors composite only | Medium-high, but it is a subset of #1 (item Q4 there), and context-factors-pit-audit already ran | Low | Folded into #1 |
| 3 | DSA audit programme T01-T10 (data forensics, lookahead, canaries, placebo) | High, but each item needs data runs; the cards are READY in the DSA lane | High | DSA lane, not Fable |
| 4 | Tom v2 fade leak audit (run 1 candidate 4) | Gone: tom-v2-dax-dev-backtest was dropped, and the DAX harness had Codex audits H1-H8 and revalidation in RV02 | - | Drop |
| 5 | Formula recount, SOURCED/OURS labels, cross-vendor reviews | Same as run 1: mechanical or already queued (lab-formula-spec-recount READY for CODEX) | Medium | Cheaper lanes |
| 6 | Verify the gate-fix-1..5 code | Needed, but it is a code check against tests | Low | Haiku/Sonnet other-model verify |

## Goal
For each pre-registration listed below, decide what the fixed gate says now and whether that changes anything the repo acts on:
- a BLOCK that should be lifted;
- a freeze, or a pending DEV read, that should now be blocked;
- a reported result that was under-powered.

Output one verdict row per study and a short fix list. Do not run any outcome study.

## Read exactly these (about 1,900 lines; read in this order, so the value lands even if you stop early)
1. Gate after the fixes:
   - `scripts/dev/prereg_gate.py` (70 lines) and `scripts/dev/test_prereg_gate.py`;
   - `scripts/dev/verdicts.py` (`count`, `--ledger`, BLOCKED);
   - `research/TRIAL_LEDGER.csv` head and count-only rows;
   - `git show 8f988e38 --stat` and its commit message.
2. Run 1 audit: `research/fable_audit_2026-10-18/GATE_AUDIT.md` (all of it: the unit, cost, m and kill-scope rules you apply).
3. Pending or READY reads first (cards: `system/tasks/<id>.json`):
   - `research/context_factors_2026-10-16/PRE_REG_V2.md` (card context-composite-v2-dev-read, READY), plus PRE_REG.md for s-references;
   - `research/context_factors_pit_2026-10-16/PRE_REG_V3.md` (cards context-factors-one-run and context-factors-v3-crossvendor-review);
   - `research/wavetrend_2026-10-17/PRE_REG.md` (card wavetrend-audit-c1-disposition);
   - `research/carry_basis_2026-10-18/PRE_REG.md`.
4. BLOCKED studies (PRE_REG.md + BLOCKED.md each):
   - `kurisko_2026-10-18` (re-check that the gate-fix-4 kill scope landed);
   - `pit_levels_2026-10-16` (plus PRE_REG_V2.md);
   - `bb_top_reversal_2026-10-18`;
   - `eur_low_us_sweep_followups_2026-10-18`.
5. Studies already read, PRE_REG plus their RESULT/verdict row in `research/VERDICTS.csv` only (do not open data):
   - mal_bb_mid_engulf_2026-10-16
   - opr_bb_mtf_center_2026-10-16
   - opr_preopen_tops_2026-10-16
   - opr_weekly_low_round_sweep_2026-10-16
   - wlow_bounce_bbrsi60_2026-10-16
   - gross_effect_screen_2026-10-15
   - trendlines_2026-10-17
   - cryptocred_htf_2026-10
   - volume_2026-10-09 (main + addendum A)
   - context_factors_pit_2026-10-16 PRE_REG.md and PRE_REG_V2.md
6. Context only: `backtest/layers/FORMULAS.md` section 13 (cost), and `system/TASK_REFINEMENT.md` around the PRE_REG gate line.

Paths are under `MyTradingSys/` unless they start with `scripts/`.

## Questions (answer per study; CONFIRMED / FLIPS / UNDECIDABLE with file:line)
These are suspicions to test, not conclusions.
1. **Inventory.** For each study, from the text, find:
   - the gate inputs as written: n, sd, cost, m;
   - whether they came from `prereg_gate.py` or hand math;
   - the unit of sd (SD units or R);
   - the study's state: frozen, BLOCKED, read, or pending.
2. **Re-gate.** Recompute with the fixed rule. You may run `python scripts/dev/prereg_gate.py` on numbers; it reads no data.
   - sd in R must be either measured (file:line) or a two-point bound for the study's exit (e.g. for a fixed target T and stop -1, sd = (T+1)*sqrt(p(1-p)) at a stated p); label it OURS with the arithmetic.
   - Cost is the mean of fee/stop where the text gives the stop spread; otherwise give a stated bound.
   - Use m auto (the DEV count from `verdicts.py count --split DEV --ledger` + new cells).
   - Does the ADMIT/BLOCK verdict flip?
3. **Results already read.** Where a study has a verdict:
   - Was its n below the corrected MDE floor, so that a PASS is under-powered or a FAIL is not evidence of no edge?
   - Name the exact VERDICTS.csv row and the wording it should carry.
4. **Pending one-shot reads.** For context composite V2, pit V3, wavetrend and carry_basis: GO / NO-GO / GO-WITH-CHANGE, before the DEV read is spent.
   - A change to n, cells or exit after freeze is a new trial: say so, and give the ledger row it needs.
5. **BLOCKED kill scopes.** For pit, bb_top and eur_low, write the narrow kill-scope sentence, the way GATE_AUDIT Q4 did for Kurisko. Does any BLOCK lift under the corrected sd/cost?
6. **Family consistency.**
   - Is any trial counted twice, or missing, across TRIAL_LEDGER.csv and VERDICTS.csv after gate-fix-5?
   - Does m auto give each pending study a different z_holm than its PRE_REG states?
   - Quote both numbers.

## Expected output (one file)
`MyTradingSys/research/fable_audit_2026-10-18/REGATE_AUDIT.md`:
- one table row per study: study, state, inputs as written, corrected inputs, old verdict, new verdict, CONFIRMED / FLIPS / UNDECIDABLE, file:line;
- every number marked RE-DERIVED (with the arithmetic) or QUOTED (file:line); every parameter labelled SOURCED or OURS;
- a go/no-go list for the pending reads (Q4), at the top;
- a fix list, max 8 items, each = card title + a test or check that fails today (a VERDICTS.csv wording change counts; give the exact new text).

## Stop criteria
Stop and write up when one of these happens:
- every study in read-list items 3-5 has a row (UNDECIDABLE allowed);
- the Fable weekly meter has risen 6 points;
- 45 tool turns.

If you stop early, write rows for what you reached; the order above puts pending reads first.

Do not edit code, PRE_REGs, VERDICTS.csv or the ledger. Do not run any study. Do not read VALIDATION or HOLDOUT data.

## Budget estimate
- Input ~100-130k tokens of reading, output ~10-15k tokens, ~30-40 turns.
- Expect +2 to +6 Fable weekly points. Run 1 read ~1,300 lines for 1 point; this read is about 1.5x that, plus gate calls.

## Operator does by hand
1. In the app, open a new Code session in a worktree of this repo and pick Fable 5.1 in the model menu.
2. First message: `Read MyTradingSys/system/fable_run_2_brief.md and do it exactly. No questions; use defaults. Reads and prereg_gate.py calls only.`
3. Note the Fable weekly meter before and after (`get_usage`), and paste both numbers into the session's last message.

## Results come back
The Fable session ships `REGATE_AUDIT.md` with `python scripts/dev/sync.py ship`. The Result line is: N studies, K flips, go/no-go count.

It then posts one line:
`python scripts/dev/desk.py post "Fable run 2 done: REGATE_AUDIT.md" --need "triage fix list and go/no-go into cards" --done-when "cards created; pending-read cards updated" --target DSA`

A Sonnet session then:
- turns the fix list into cards;
- writes the go/no-go into the pending cards (context-composite-v2-dev-read and others) before any of them runs;
- marks card fable-run2-regate-all-prereg done, with the commit sha as the result.
