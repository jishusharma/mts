# PRE-REGISTRATION V2: per-factor filter contrasts, day units and the realised-MDE rule (2026-10-16, successor to PRE_REG.md)

Status: EXPLORATORY TRIAL, frozen before any outcome read. No outcome column exists in this folder. DEV only (bar open
2022-01-01 .. 2024-06-30). Labels: SOURCED = quote + file:line; OURS = judgement. Written by the Fable session after reading the
trunk's conventions (COMPARISON.md s.4); PRE_REG.md is untouched and is never run.

## 0. Why a successor, and what is unchanged
PRE_REG.md counted power in episodes (n_min 572) with its own sd bound. The trunk's adopted convention is distinct UTC days with
Holm (Opus REPORT.md D4; `context_factors_2026-10-16/AUDIT_BEFORE_RUN.md` item 2; `pit_levels_2026-10-16/AUDIT_BEFORE_RUN.md`)
and a realised-MDE verdict rule (`layer_lab/context_fix2_mde_rule/`). Two conventions in one ledger would make verdict words
incomparable, so this successor adopts the trunk's.
- **Unchanged:** `context_asof.py` (sha recorded by the executor at step 0), the episode definition (PRE_REG.md s.5: at_level,
  first_touch, a ladder rung, stop >= the 0.56 % floor), the 14 contrasts (s.3, `episode_counts.py`), the outcome function
  (s.2: entry open[t+1], ladder stop, 1.5 R target, both touched = stop, gap fill min(open, stop), max hold 1440 bars, fees 0.14 %),
  the matching (`context_null` key and K = 20), DEV only, the traps (s.7), the outputs (s.8).
- **Changed:** units (s.1), the power table (s.2), Holm m (s.3), the verdict rule (s.4), one count-only step before the read (s.5),
  an audit before the read (s.6).
- This is a different design, not a re-run: no outcome was ever read under PRE_REG.md.

## 1. Units
The unit is the distinct UTC day of the decision bar. Episodes on one day share the daily candle, the ladder rung and the phase,
so they are not independent (Opus REPORT.md finding 6: same-day overlap). SE of every effect is day-clustered; the week-clustered
SE is printed beside it and PASS needs both (s.4).

## 2. Power table (count-only, from the committed grid rule; `daycount` in COMPARISON.md s.4)
Thresholds, all OURS: own = sd 1.25 x sqrt(1 + 1/20) = 1.28 R, plausible 0.15 R, cost 0 -> n = 572 days; trunk-free = sd 1.5 R,
plausible 0.20 R, cost 0 -> 441 days; trunk-net = sd 1.5 R, plausible 0.20 R, cost 0.081 R -> 1246 days (Opus COUNTS.md).
A filter contrast pays no extra fee (both arms trade the same way), so cost 0 is the right term for it; the net column is printed
for comparability with the Opus study.

| cell | long n | long days | own / free / net | short n | short days | own / free / net |
|---|---|---|---|---|---|---|
| F1 at a side-aware level (every episode) | 1636 | 694 | yes / yes / no | 1651 | 700 | yes / yes / no |
| F2 confluence n_layers >= 2 | 1305 | 654 | yes / yes / no | 1307 | 657 | yes / yes / no |
| F3 operator condition (ladder_cond) | 965 | 448 | no / yes / no | 965 | 452 | no / yes / no |
| F4 4h pattern in the trade direction | 261 | 161 | no / no / no | 287 | 177 | no / no / no |
| F5 band state (long re-entry / short walk veto) | 36 | 27 | no / no / no | 40 | 27 | no / no / no |
| F6 phase A with the trade | 578 | 247 | no / no / no | 382 | 162 | no / no / no |
| F7 HTF alignment | 885 | 376 | no / no / no | 667 | 299 | no / no / no |

**Powered by design: F1 long, F1 short, F2 long, F2 short** (>= 572 days and >= 441 days). The other ten cells are computed and
printed with their realised MDE; their verdict word follows s.4 and can be INCONCLUSIVE or FAIL-by-realised-MDE, never a PASS
that rests on a design the power table refused. The F1 cell is the pit_levels question (at a level vs not); its read here is a
filter contrast on episodes, not the pit_levels trade; both are listed in Holm.

## 3. Holm
m = 37 (`python scripts/dev/verdicts.py count --split DEV`, 2026-10-16: 37 variants from 12 studies) + 8 (`trials.csv`, counts
only, conservative) + 14 (these cells) = **59**; two-sided z = 3.337. A larger recount at run time wins; a smaller one does not.

## 4. Verdict rule (per cell, applied verbatim; the trunk's realised-MDE rule)
Let E = mean net_R of the episodes in the cell minus the mean net_R of their matched controls (K = 20, kmin = 10), SE_day and
SE_week the clustered standard errors, MDE_real = 2.8 x SE_day.
- **PASS** iff the cell is powered by design (s.2) AND E has the pre-declared sign (filter helps) AND |E| / SE_day >= 3.337 AND
  |E| / SE_week >= 3.337 AND the sign of E is the same in 2022, 2023 and 2024H1 (matched episodes only).
- **FAIL** iff MDE_real <= 0.15 R (the cell could have seen the plausible effect) AND NOT (E > 0 with |E| / SE_day >= 3.337).
  Kill scope of a FAIL: this contrast's definition at this engine sha only (COMPARISON.md s.3 names which factors are
  definition-fragile); never a trader, a setup family or a layer.
- **INCONCLUSIVE** otherwise; MDE_real printed; never relabelled.
- A cell whose cross-engine kappa (s.5) is below 0.4 carries the suffix "(definition-fragile)" on its verdict word in RESULT.md
  and in the VERDICTS.csv arm label.

## 5. Count-only step before the read: cross-engine agreement
Rebuild the Opus frames read-only (`python MyTradingSys/research/context_factors_2026-10-16/run_dev.py vec`, no edit there) and
this grid (`python run_compare.py`). Join on (utc_close, side) over the shared hours (2022-04-01 .. 2024-06-30). For each pair
print agreement % and Cohen's kappa: at_level vs f1_at_level; n_layers >= 2 vs f2_conf_obj >= 2; ladder_cond vs f3_armed;
ladder_rung vs f3_stop_tf; phase_a in (markup, markdown) vs f6_phase; bb_short_veto_walk vs f5_veto (short); pat_4h direction vs
f4_4h_align. Output `CROSS_ENGINE.md`, committed before `episodes.csv`. No outcome, no price after T.

## 6. Audit before the read
Card `context-factors-pit-audit` (6 items of `pit_levels_2026-10-16/AUDIT_BEFORE_RUN.md`: location-only control, MDE under day
clustering, Holm k, leakage, VERDICTS row, frozen trigger) must have written `AUDIT_BEFORE_RUN.md` in this folder with the word
OK or FIX-FIRST. On FIX-FIRST the executor writes BLOCKED.md and stops; it does not patch this file.

## 7. Outputs
`CROSS_ENGINE.md`, `episodes.csv` (no outcome), `outcome.py` + `test_outcome.py`, `RESULT.md` (14 rows: cell, side, n episodes,
days, matched, E, SE_day, SE_week, t_day, t_week, MDE_real, sub-period signs, kappa, verdict word), `EXPOSURE_LEDGER.csv`,
14 `verdicts.py add` rows with the kill scope of s.4.
