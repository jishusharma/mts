**Verdict: FIX-FIRST (2 of 6 items: 1 and 2).** Per PRE_REG_V2 s.6 the one-run card writes BLOCKED.md and stops; PRE_REG.md, PRE_REG_V2.md and context_asof.py are untouched.

# AUDIT_BEFORE_RUN: context_factors_pit PRE_REG_V2 (2026-10-17, independent, card `context-factors-pit-audit`)

Method: the 6 items of `pit_levels_2026-10-16/AUDIT_BEFORE_RUN.md`, applied to `PRE_REG_V2.md`. Counts only: the DEV grid was rebuilt with
`python run_compare.py --full --out <scratch>` (points 128,736, 0 mismatching fields; same as `compare_result.txt`), reading no outcome, no price after T,
no VALIDATION or HOLDOUT bar. `grid_context.csv` was written to scratch and is not committed.

| # | Item | Verdict |
|---|---|---|
| 1 | Location-only control (match key vs shared ladder stop) | **FIX-FIRST** |
| 2 | MDE under day clustering | **FIX-FIRST** |
| 3 | Holm k | OK |
| 4 | Leakage | OK |
| 5 | VERDICTS.csv row | OK (one non-blocking note) |
| 6 | Frozen trigger (shas) | OK |

## 1. Location-only control: FIX-FIRST
The `context_null` key is hour + vol tercile + trend; it has no stop term. Both arms share the ladder stop rule, but the stop width sets the R unit. Median
`ladder_stop_pct` (valid episodes: at_level, first_touch, rung, stop >= floor), cell vs the at-level control pool outside the cell (a proxy for the F2-F7 pool of
PRE_REG s.5 "same kind of level"; F1's pool is the whole at-level set):

| cell | long cell / ctrl / gap | short cell / ctrl / gap |
|---|---|---|
| F1 (powered) | 1.539 / 1.568 / -2 % | 1.511 / 1.563 / -3 % |
| F2 (powered) | 1.545 / 1.646 / -6 % | 1.479 / 1.653 / -11 % |
| F3 ladder_cond | 1.838 / 1.289 / **+43 %** | 1.886 / 1.305 / **+45 %** |
| F4 | 1.745 / 1.575 / +11 % | 1.640 / 1.574 / +4 % |
| F5 | 2.271 / 1.575 / **+44 %** (n 36) | 3.542 / 1.539 / **+130 %** (n 40) |
| F6 | 1.631 / 1.567 / +4 % | 1.553 / 1.556 / 0 % |
| F7 | 1.552 / 1.573 / -1 % | 1.669 / 1.566 / +7 % |

The four design-powered cells are inside the 25 % bar. F3 (both sides) and F5 (both sides) are not: their event and control trades have different R units, yet V2 s.4
lets them reach FAIL (when MDE_real <= 0.15 R) and carries a kill scope. F3 is powered under the trunk-free convention (448 / 452 days), so a FAIL there is reachable.
**Exact fix** (new `PRE_REG_V3.md` or a committed addendum before `episodes.csv`): (a) the step before the read prints per cell the median and p90 `stop_pct` of the cell
and of its control pool and the `ladder_rung` shares; (b) a cell whose median gap exceeds 25 % relative gets the word INCONCLUSIVE ("R units not comparable"), never FAIL, and no kill scope; (c)
E is also computed within `ladder_rung` strata (same key plus rung, kmin 10) and printed beside the verdict; PASS needs the stratified E > 0 on the strata that hold >= 80 % of the matched events.
(Caveat: my control pool is the at-level complement; the real pool is the `context_null` match, which can only be measured after the matching, still count-only.)

## 2. MDE under day clustering: FIX-FIRST
Hand redo of s.2 (z 2.8 as written): own (1.25 x sqrt(1.05) = 1.281 R sd, 0.15 R, cost 0) = 571.7 -> **572**; trunk-free (1.5, 0.20, 0) = 441.0 -> **441**; trunk-net (1.5, 0.20, 0.081) = 1245.7 -> **1246**. All three
figures reproduce. Day counts of the four powered cells reproduce: F1 long 694, short 700; F2 long 654, short 657 (all 14 cells reproduce EPISODE_COUNTS.md and s.2).
Defects:
1. **The power gate and the PASS gate use different z.** n_needed uses the multiplier 2.8 (alpha 0.05, unadjusted), but PASS requires |t| >= 3.337 (Holm m = 59). With the Holm z the planning
   formula `n = ((3.337 + 0.8416) x sd / (effect - cost))^2` (the form of `layer_lab/context_fix2_mde_rule/mde_rule.py::n_needed`) gives **1274** (own), **983** (trunk-free), **2775** (trunk-net) days.
   The largest cell has 700 days, so **none of the 14 cells is powered under the PASS threshold**, and "powered by design: F1, F2" is false for the test V2 actually applies. Under V2 as written PASS is nominally reachable
   but only on a design the table, recomputed consistently, refuses; the "4 of 14" claim must not be carried to RESULT.md.
2. **FAIL clause differs from the adopted rule.** `mde_rule.verdict`: FAIL iff E <= 0 and 2.8 x SE_day + cost <= 0.30 R. V2 s.4: FAIL iff 2.8 x SE_day <= 0.15 R and NOT(E > 0 and t_day >= z). V2 lets a small positive E be FAIL and uses
   0.15 R (set after the episode counts, EPISODE_COUNTS.md, so OURS-after-counts) instead of the trunk's 0.30 R sensitivity. The 0.15 R choice is the harder one to FAIL on, so it is safe; the E-sign condition is not the trunk's.
   The PASS side (both |t| >= z and the same sign in 2022 / 2023 / 2024H1) matches the rule.
**Exact fix:** (a) replace the s.2 table with the Holm-z formula and a plausible effect stated as "OURS, set after counts", with the 0.30 R sensitivity beside it. At 0.30 R, cost 0, sd 1.5, z 3.337: n = **437** days
(own sd 1.281: 319), so F1 long/short (694 / 700), F2 long/short (654 / 657) and F3 long/short (448 / 452) are powered, F4-F7 are not. (b) rewrite the FAIL clause as: FAIL iff E <= 0 and 2.8 x SE_day <= 0.30 R (cost 0 for a filter contrast);
E > 0 below z is INCONCLUSIVE. (c) keep PASS as written (day and week |t| >= 3.337 plus sub-period signs). (d) unpowered cells can only be INCONCLUSIVE, as V2 already says.

## 3. Holm k: OK
`python scripts/dev/verdicts.py count --split DEV` today = **37** (12 studies; 6 UNPARSED rows not counted, so it is a lower bound). `trials.csv` has 8 rows (counts only). 37 + 8 + 14 = **59** >= 59; z = Phi^-1(1 - 0.05/118) = **3.3368** (recomputed). V2 s.3 states
"a larger recount at run time wins", the right rule. The F1 cell and the pit_levels F1 question are both counted. Note: the Opus chain counted m = 42, z = 3.241 for a different study; a smaller m does not bind here.

## 4. Leakage: OK
`python scripts/dev/lookahead_lint.py` (whole repo; it takes no path): 198 hits, 0 new FAIL, 0 stale allowlist rows. In this folder 20 hits: `context_asof.py` 274 / 500-501 / 518 / 520 / 553 / 558 (fwd-index, pivot-right-neighbour: the value-area walk, the confirmed-pivot detector, per-bucket volume profiles, all
allowlisted and each exercised by the planted-leak tests), 624 / 1015 / `counts.py` 146 / `indep_pandas.py` 276 (full-sample quantile WARN, allowlisted), `indep_pandas.py` 171-191, `test_context_asof.py` 68-73 (the planted-leak builders themselves). All allowlisted, none new.
`python -m pytest test_context_asof.py -q`: **18 passed**; `-k "leak or plant"`: the 7 planted leaks are still caught (`test_planted_lookahead_is_caught` x 7).

## 5. VERDICTS.csv row: OK
`grep` of `research/VERDICTS.csv` finds no row for this folder: correct before a read. Non-blocking note for the run card: `verdicts.py kill_scope_of` (verdicts.py:155-162) needs a line containing "FAIL means stop"; V2 s.4 says "Kill scope of a FAIL" (0 matches),
and `backfill` reads a table headed "Verdict arms" or "Primary" (verdicts.py:199). Use `verdicts.py add` with an explicit kill scope (V2 s.7 does) or carry the sentence into the successor file, and check that no row is UNPARSED before ship.

## 6. Frozen trigger: OK
sha256 recorded today, equal to the committed blobs at HEAD (`git show HEAD:<path> | sha256sum`; git blob ids 7f4aa6dd... and aeb7ee2c...):
- `context_asof.py` `51a2a247c06e97148bdf6177f60123236a64c276cf1dd9ce3d734cf079828976`
- `PRE_REG_V2.md` `cf44beacfe0f6f8bd58c6d0b6bcfbb9b0f5f84227d122e8e1fd633b7749be0e4`
V2 s.0 leaves the sha "recorded by the executor at step 0"; the values above are the reference. Engine, episode definition, 14 contrasts, outcome function, matching and DEV-only bar are unchanged from PRE_REG.md.

## Route
No outcome was read, so a supersede is legitimate: a `PRE_REG_V3.md` (V2 plus the fixes of items 1 and 2) committed before any outcome code; card `context-factors-one-run` stays blocked until then. DECISION (OURS, default taken, not asked): the audit does not recommend cancelling the study.
