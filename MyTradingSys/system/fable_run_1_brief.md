# Fable run 1 brief (designed 2026-10-18; the operator runs it by hand, no session starts or messages it)

Pick: **audit the count-only gate and the Kurisko 0-of-8 freeze, plus the same MDE math inside the promotion gate.** One session, two cards (`fable-run1-gate-audit`, `fable-run1-promote-mde-audit`). Reads only: no backtest, no VALIDATION or HOLDOUT bar, no production code change.

## Why this pick (value per Fable token)
| # | Candidate | Value | Fable token cost | Verdict |
|---|---|---|---|---|
| 1 | Audit prereg_gate.py + Kurisko 0-of-8 freeze (+ promote.py G4 MDE math, same formula) | HIGH: one 35-line gate now decides every pre-registration freeze (Kurisko, pit, context, wavetrend); a wrong unit or aggregation there silently kills or admits whole layers. Prior Fable audit (FABLE_RUNS_AUDIT.md s0) said the missing check was exactly economics before fidelity. | LOW: ~1,300 lines to read, pure reasoning, no runs | **PICK** |
| 2 | Formula recount (lab-formula-spec-recount) | Medium: mechanical, already a ready Codex/Sonnet card with a hard failing test | Medium-high (many sub-ids), little judgement | Cheaper lane; skip |
| 3 | Cross-vendor review of Gemini branches / C2 cards | Medium: g1-g5 review sessions are already shipping these (Claude reviewed, GPT queue has gpt-g3-pack-audit, gpt-formulas-rederive) | High (many files) | Already covered; leave to GPT/Haiku |
| 4 | Fee-net/lookahead/holdout leak in Tom fade arm and dev studies | Medium-high but needs runs or large diffs; Tom v2 DAX backtest is blocked, nothing to leak-check yet | High | Defer until tom-v2-dax-dev-backtest unblocks |
| 5 | SOURCED/OURS label audit | Low-medium: hygiene, no decision rides on it this week | Medium | Sonnet/Haiku work |

## Goal
Decide whether "0 of 8 Kurisko cells frozen" is a correct consequence of the gate's own rule, and whether the gate (and the matching promote.py G4 code) is mathematically sound. Output a verdict per question, with a minimal fix list. Do not run an outcome study.

## Read exactly these (about 1,300 lines)
1. `scripts/dev/prereg_gate.py` and `scripts/dev/test_prereg_gate.py` (commit 9d6fc02a).
2. `MyTradingSys/research/kurisko_2026-10-18/PRE_REG.md`, `BLOCKED.md`, `counts/counts.csv`, `count_events.py` (commit 2362bbc7).
3. `MyTradingSys/backtest/layers/FORMULAS.md` sections 13 (cost), 8 (resample), 24 (Kurisko rule) only.
4. `MyTradingSys/backtest/layers/kurisko/quad_rotation.py` (112 lines; module commit dd001f2a).
5. `MyTradingSys/backtest/layers/promotion/promote.py` G4/G5 block (grep `variants`, `z_holm`, `MIN_TRADES`) and its tests; card `fable-audit-e4-promotion-variants` (commit message has the numbers).
6. Context only: `research/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md` s0 and E1/E4 lines; `scripts/dev/verdicts.py check`.

## Questions (answer each as CONFIRMED / WRONG / UNDECIDABLE with file:line)
Suspicions to test, not conclusions:
1. **Unit mix.** PRE_REG s4 runs `prereg_gate.py --sd 1`, so MDE is in SD units, then the gate adds `cost` in R and compares to 0.30 R. Is `MDE(SD) + cost(R) <= 0.30 R` valid only if 1 SD = 1 R? What is a realistic SD of R per event for a 5m stop of 18-23 bp, and does the 5m stochastic BLOCK still hold with it?
2. **Cost aggregation.** Fee R is computed as 14 bp / median stop. The mean of 14/stop over events differs, and 22-38 % of events are narrower than the fee. Is median-of-stop the right input to a one-number gate? Would a minimum-stop filter (PRE_REG s7) change which cells pass, and is that a new trial that must be counted?
3. **Statistics.** z_holm uses two-sided 0.05/(2m); MDE adds 0.84 power z with n = event-days. Is that the right MDE for a day-clustered mean (clustering, 1m events ~16/day)? One-sided vs two-sided consistency with promote.py G4 (E4: `1-0.025/variants`; check the two gates agree for the same m).
4. **Is the freeze overreach?** BLOCKED.md and PRE_REG s5 say "FEE-DOMINATED" per TF x arm. 15m and 1h were not counted. What exact kill scope may be written (verdicts.py row) without claiming Kurisko on higher TF is dead? Name the kill scope sentence.
5. **Count correctness.** Without reusing the module, re-derive by reasoning from FORMULAS 24.4 which of the 8 counts is most sensitive to a rule choice (e.g. short mirror, RSI 60 lookback, resample bucket drop) and state a hand check the operator can run in Python for one month (do NOT run on VALIDATION/HOLDOUT; DEV is <= 2024-06-30).
6. **Trial-ledger logic.** Does KQ-T01 (8 cells counted, 0 frozen) correctly enter the trial ledger count that feeds E4's `variants`? Is any cell double-counted or omitted across Kurisko, wavetrend and pit registries?

## Expected output (one file)
`MyTradingSys/research/fable_audit_2026-10-18/GATE_AUDIT.md`:
- verdict table: question 1-6, CONFIRMED/WRONG/UNDECIDABLE, one-line reason, file:line
- every number marked RE-DERIVED (with the arithmetic) or QUOTED (file:line); parameters labelled SOURCED or OURS
- fix list, each item = card title + test that must fail on current code (max 6 items)
- one paragraph: does 0-of-8 stand as written, yes/no/changes-to-kill-scope

## Stop criteria
Stop and write up when: all 6 questions have an answer or UNDECIDABLE; OR Fable weekly meter +5 points (earlier audit: ~3 points for ~6k changed lines); OR 40 tool turns. Do not start fixes, do not edit prereg_gate.py or promote.py, do not read VALIDATION or HOLDOUT.

## Budget estimate
Input ~60-80k tokens of reading, output ~8-12k tokens, ~25-35 turns. Expect +3 to +5 Fable weekly points (FABLE_RUNS_AUDIT USAGE.md: 3 points for a comparable review).

## Operator does by hand
1. In the app, open a new Code session in a worktree of this repo, pick Fable 5.1 in the model menu (the model_guard hook only lets Opus through when you ask in words; Fable is yours to choose).
2. First message: `Read MyTradingSys/system/fable_run_1_brief.md and do it exactly. No questions; use defaults. Reads only.`
3. Note the Fable weekly meter before and after (`get_usage`) and paste both numbers into the session's last message.

## Results come back
The Fable session ships `GATE_AUDIT.md` with `python scripts/dev/sync.py ship` (Result line = verdict count), then posts one line: `python scripts/dev/desk.py post "Fable run 1 done: GATE_AUDIT.md" --need "triage fix list into cards" --done-when "cards created for each fix" --target DSA`. A Sonnet session turns the fix list into cards; the two task cards above are marked done with the commit sha as result.
