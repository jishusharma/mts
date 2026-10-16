# AUDIT_BEFORE_RUN: context_factors PRE_REG (V1, already read once) and PRE_REG_V2 (not yet run) (2026-10-16, independent)

**Verdict: FIX-FIRST (2 items of 6), both on PRE_REG_V2 before card `context-composite-v2-dev-read` runs.** PRE_REG.md and
PRE_REG_V2.md are untouched (Q76/Q77 files). Fix route: a `PRE_REG_V3.md` (or an addendum the supervisor commits before study_v2.py)
carrying the two fixes below. Method: the 6 items of `pit_levels_2026-10-16/AUDIT_BEFORE_RUN.md`. Inputs: counts and the committed
RESULT.md numbers only; no VALIDATION/HOLDOUT bar, no new outcome read. V1 is already read (INCONCLUSIVE, 241 matched events / 164 days),
so for V1 the audit is retrospective; V1 gates held up as written (INCONCLUSIVE, never relabelled).

| # | Item | V1 PRE_REG | V2 PRE_REG_V2 |
|---|---|---|---|
| 1 | Location-only control (T minus C) | OK in design, 241/1,010 matched | **FIX-FIRST** (stop comparability) |
| 2 | MDE under day clustering | gate held (387 vs 456) | **FIX-FIRST** (plausible chosen after counts; FAIL needs a realised-MDE rule) |
| 3 | Holm k (distinct variants, days as the unit) | OK | OK |
| 4 | Leakage | OK | OK (one wording fix, non-blocking) |
| 5 | VERDICTS.csv row | row present (VERDICTS.csv:24) | OK (arm label note) |
| 6 | Frozen trigger | OK | OK |

## 1. Location-only control: V2 FIX-FIRST
The estimand is E = event net_R minus mean net_R of at-level controls (PRE_REG s.3; V2 s.1 keeps `f1_at_level`, drops only the cooldown), so a T-pass
cannot come from location alone; this is the lesson of R1 applied correctly, better than pit_levels V1. Gap: the key is hour + vol tercile + trend
(`context_null.context_key`), not stop. C requires `f3_armed` and `f2_conf_obj >= 2`, which select which ladder rung (D/12h/8h) exists; the control only needs
`f3_stop_tf != none`. Stop width sets R, so a 2 R target at a 2.11 % median stop (C, PRE_REG s.2) vs a different control stop is a different trade
(different cost in R, 0.066 R median for C only) and E mixes setup with stop geometry. **Exact fix:** before the run, count-only (no price after T), print
for C and for the V2 control pool: `f3_stop_tf` shares and median/p90 stop_pct = |close[T]-stop|/close[T] per side; and make the read cell compute E a second
time within `f3_stop_tf` strata (same key plus stop_tf, kmin 10), printed beside the verdict; PASS additionally needs the stratified E > 0 on at least the strata holding
>= 80 % of matched C events. If C and control median stop_pct differ by > 25 % relative, record it in RESULT_V2 as "R units not comparable" and do not call FAIL.

## 2. Plausible effect and MDE under day clustering: V2 FIX-FIRST
Own arithmetic (units = days, sd 1.5 R, power 0.8416, cost 0.066 R, z 3.241 at m = 42): n_needed(0.375) = (4.0826 x 1.5 / 0.309)^2 = 392.8 -> 393 (matches V2 s.3);
MDE(452 days) = 0.288 R + 0.066 = 0.354 <= 0.375 holds. But 0.375 R "was written after the counts were seen" (PRE_REG s.4), is half of a +0.75 R figure taken from another
setup (CATALOGUE T-3), and the only location-only evidence is ~0 gross (pit audit item 2). At a plausible **0.30 R**: n_needed = (4.0826 x 1.5 / 0.234)^2 = **685 days > 452**,
so the cell is not powered for any conservative effect. A FAIL verdict from an unpowered cell would "kill" the composite family on a read that could not see an effect of 0.30 R.
Day-clustering gaps: controls are reused (V1 flagged it) and 24 h trades span two days, so day-clustered SE is understated; V2 only prints week-clustered SE.
**Exact fix:** (a) FAIL is allowed only if the realised MDE (2.8 x day-clustered SE of E, as RESULT.md prints) + cost <= 0.30 R; otherwise the word is INCONCLUSIVE (never FAIL)
and the kill scope is not applied; (b) PASS needs week-clustered |t| >= 3.241 too, not only the day-clustered one; (c) write 0.375 R as "OURS, set after counts" in the verdict table,
with the 0.30 R sensitivity (685 days) beside it. (Information, not a gate: V1's realised SE was 0.0739 R on 164 days, i.e. empirical sd 0.95 R, which would make 452 days
adequate; but that comes from an outcome read, so it may not replace sd 1.5 in a frozen gate.)

## 3. Holm k: OK
m counts distinct (study, arm) variants, not events and not days; the unit conversion is only in the power gate (days). Recount today: `verdicts.py count --split DEV` = 17 (11 studies; it already
includes the V1 context row VERDICTS.csv:24, so V2's "+1" is not a double count) + 6 UNPARSED + 16 `trials.csv` rows + 1 + 2 pit V2 arms = 42; z = Phi^-1(1 - 0.05/84) = 3.241.
V2 states "a larger recount at run time wins", which is the right rule. Note: trials.csv rows are counts-only (`outcome_read` = no), so including them is conservative, not required.

## 4. Leakage: OK
`context_asof.py` sha256 efa3513f... verified equal today; PRE_REG.md sha bd56a752... verified equal. Factor columns are as-of T (spec + planted-leak tests at 46a0005c), matching
keys use the 1h close array only, entry is the 1m bar at T + 60 s. The >24 h exclusion around C events looks forward in time (a later C event removes an earlier T' from the pool): it
is selection of controls from event timestamps, not outcomes, and cannot leak a price; acceptable. Non-blocking wording fix: V2 s.5 trap 2 says the exclusion is applied "only before each C event",
s.1 says "more than 24 h from every C event" (both sides); the code must apply both, and the test (card step 4) should plant a control 12 h AFTER a C event.

## 5. VERDICTS.csv row: OK
V1 row exists and is parsed (VERDICTS.csv:24). Card step 6 runs `verdicts.py add` and V2 s.3 carries a "FAIL means stop:" sentence (parser needs it, verdicts.py:160,199). Note: give the V2
row an arm string that starts "V2 C pooled" so `count` sees a new (study, arm) variant, and run `verdicts.py backfill` + check not UNPARSED before ship (the card lists neither).

## 6. Frozen trigger: OK
C = ledger event AND f2_conf_obj >= 2 AND f3_armed AND NOT f5_veto AND f6_phaseA pair, pinned to context_asof.py sha efa3513f; V2 s.0 re-counts 1,010 / 456 = V1 and declares what changed
(control rule, m, day gate) with `decision_informed` = yes. Honest note kept in V2: the C-mean gate already failed in V1 (-0.137 R), so PASS is unreachable; V2's value is a powered E.

DECISION (OURS): the audit does not recommend cancelling V2; with the two fixes it is a legitimate cheap read.
