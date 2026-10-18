# PRE-REGISTRATION V2: operator context composite C vs context-matched controls, wider control pool, BTCUSDT 1h decisions, DEV (2026-10-16, successor to PRE_REG.md)

Written by a Sonnet worker (claim `q76-q77-pre-reg-v2`), docs only. No outcome code, no outcome read, no VALIDATION or HOLDOUT bar. Counts below come from the frozen frames (`frame_long.pkl`, `frame_short.pkl`) and the hourly close array only (keys, pool membership, candidate counts); no P&L, exit or return column was formed.
Status: EXPLORATORY TRIAL. Nothing here adopts a rule. Labels: SOURCED = quote + file:line; OURS = judgement.

## 0. Why a successor, and what is unchanged
`RESULT.md` (PRE_REG.md, one run, 2026-10-16): verdict INCONCLUSIVE, because only **241 of 1,010 C events had >= 10 controls** (164 matched days, need 387; `RESULT.md` "Why INCONCLUSIVE"). The cause is the pool, not the outcome: PRE_REG s.3 drew controls only from tradeable-ledger events (after the 4 h same-side cooldown) outside C and > 24 h from any C event, which left a median of 6 (long) / 7 (short) candidates per key cell against kmin 10 (`RESULT.md`, matching diagnostics). The plumbing run with random P&L printed the same 241 / 164, so the attrition depends on keys and pool only. `PRE_REG.md` s.4 itself says the matching attrition "was not counted before the freeze".
- **Same frozen C trigger (SOURCED: `PRE_REG.md` s.2, `context_asof.py` sha256 `efa3513f738337ebd48d09806b936fdef186092c14bb5b18c4df1c4415e49401`, `study.py form_c`):** ledger event AND f2_conf_obj >= 2 AND f3_armed AND NOT f5_veto AND f6_phaseA in the side's pair. Counted again today: long 554 events / 254 days, short 456 / 202, pooled 1,010 / 456 = the PRE_REG s.2 numbers (match).
- **Unchanged:** the trade (entry at the open of the 1m bar at T + 60 s, ladder stop, 2 R target, 24 h time stop, 7 bp per side + realised funding, `PRE_REG.md` s.1-2), the match key (hour, vol tercile, trend tag; `Config(bar_min=60, cooldown=4, seed=0)`, K = 20, kmin = 10, controls spaced > 4 h), cells (only C pooled is READ; every other cell REFUSED_POWER, so unread), plausible effect 0.375 R and sd 1.5 R (OURS, `PRE_REG.md` s.4 and REPORT.md D1), cost 0.066 R.
- **Changed:** the control rule (s.1), Holm m (s.3), the matched-days gate (s.3). Nothing else.
- Why this is a different design and not a re-run: the controls (population and therefore E, its SE and the matched-day set) are a different draw from a different pool. It is NOT independent evidence about C itself: C's 1,010 DEV trades were read in RESULT.md, so the DEV read of V2 shares those trades. That is why the PASS bar below still includes "mean net_R of C > 0" and why a PASS is only a licence for a VALIDATION card, never an adoption.

## 1. New control rule (DECISION (OURS), conservative, chosen on counts only)
Control pool for a side = **every DEV decision hour T' of that side (frame row) with `f1_at_level` = True and `f3_stop_tf` != none (so a ladder stop exists), that is not a C event, and is more than 24 h from every C event of that side**. The 4 h same-side cooldown of the ledger is NOT applied to the pool (that cooldown thinned the pool and was the cause); the cooldown stays on the *chosen* controls (spaced > 4 h apart, as before). Everything else as before: same key (hour, vol, trend) via `context_null.context_key`, K = 20 without replacement, `default_rng(0)` per side, C events in time order, kmin = 10, each control gets its own ladder stop and the same trade. `entry_beyond_stop` / `no_entry_bar` controls are dropped from the pool at run time (in the first run these were 0).
Why keep `f1_at_level`: the controls stay at a level (same "at a level" context as C), so E still asks whether the extra C conditions matter, not whether being at a level matters. The alternative that drops it (all stop-valid hours, 993 matched events / 455 days) is not used: it changes what the control is (not at a level), not needed to reach the gate, and was not chosen on any outcome.
Pool sizes (counts): long 6,664 hours, short 8,021 (v1: 1,447 and 1,704). Median candidates per C key cell: long 27, short 29 (v1: 6 and 7).

## 2. DEV counts under the new rule (counts only; reproducible by the script in the new card step 2)
| side | C events | C days | matched C events (>= 10 controls after 4 h spacing) | matched days | C events with no key |
|---|---|---|---|---|---|
| long | 554 | 254 | **546** | **254** | 0 |
| short | 456 | 202 | **428** | **198** | 0 |
| pooled | 1,010 | 456 | **974** | **452** | 0 |

(v1: 241 matched events / 164 days.) Matching used only context keys, pool membership and a seeded shuffle: no price after T, no entry, no outcome.

## 3. Gate, Holm, verdict rule
- **Holm m = 42** (OURS, recounted): `verdicts.py count --split DEV` = 17 variants (11 studies) + 6 rows with split UNPARSED + 16 factor x definition rows in `trials.csv` + 1 this successor + 2 arms of the `pit_levels_2026-10-16/PRE_REG_V2.md` study = 42 (V1 used 37 with a count of 14). z_holm = 3.241 (two-sided 0.05 / 42). If a recount before the run gives a larger m, the larger m is used.
- **Power gate:** `n_needed = ((z_holm + 0.8416) x sd / (plausible - cost))^2 = (4.083 x 1.5 / (0.375 - 0.066))^2 = 393 days` (V1: 387 at m = 37). **Reachable on DEV counts alone:** 452 matched days >= 393 (margin 59 days); MDE on 452 days = 4.083 x 1.5 / sqrt(452) = 0.288 R, + cost 0.066 = 0.354 R <= 0.375 R. If the run's matched days fall below 393 the verdict is INCONCLUSIVE (never FAIL).
- **Verdict rule for C pooled (all gates of `PRE_REG.md` s.4 kept verbatim except m, the day count and the control pool):** PASS iff matched days >= 393 AND E > 0 AND |t| >= 3.241 (Holm, two-sided) AND mean net_R of C > 0 over all executed C trades AND over the matched events AND E > 0 in each of 2022 (Apr-Dec), 2023, 2024H1 AND MDD(C) <= MDD(matched controls' mean path) on the matched events and on all executed trades. INCONCLUSIVE iff matched days < 393. FAIL otherwise. No bar is lowered; the Holm bar rose (3.205 -> 3.241) and the day gate rose (387 -> 393).
- **Honest expectation, disclosed before the run:** RESULT.md already printed mean net_R of C = -0.137 R over all 1,010 executed trades. That gate cannot pass on the same trades, so V2 can return FAIL or INCONCLUSIVE but not PASS. Its value is a powered E (the trigger effect against controls that exist for 974 of 1,010 events) and the right to call the composite dead at its kill scope. The gate is kept anyway because lowering it after reading it is exactly what the rules forbid. DECISION (OURS): run it; the cost is one cheap card.
- Printed beside the READ cell, no verdict: E per side, maker-in readout, week-clustered SE, skipped counts, exit mix, **control reuse** (mean uses per distinct control; above 5 is flagged "SE understated", as in `RESULT.md`).
- **Kill scope of a FAIL:** the composite C exactly as defined at `context_asof.py` sha `efa3513f...` (1h decisions, these layers, the D/12h/8h ladder, 2 R target, 24 h time stop), against the s.1 controls. FAIL means stop: no detector, chart, layer or management work on this composite; it parks no single factor, no trader's setup, Tom, Fabio, Krown or any layer.

## 4. Ledger, exposure, split
`ledger_C.csv`, `controls.csv`, `EXPOSURE_LEDGER.csv` rows (study `context_factors_2026-10-16` V2, `rule_sha256` of this file at the run commit, m = 42, `decision_informed` = yes: s.1 was chosen after V1 was read, on counts), and one `verdicts.py add` row. Outputs go to the files `*_v2.csv` and `RESULT_V2.md` so that V1 files stay untouched. DEV only; VALIDATION read once, later, by a separate card after a PASS; HOLDOUT sealed (operator).

## 5. Known traps
1. The pool now contains hours adjacent to each other (no cooldown): the 4 h spacing among the chosen K controls and the >24 h exclusion around C keep control windows from overlapping a C trade, but control trades can overlap each other; controls are reused (see reuse print). 2. A control's 24 h trade may run across a later C event's day: only the >24 h exclusion before each C event is applied (same as V1). 3. `context_asof.py` changed after this commit voids the run (check the sha). 4. Funding sign: long pays a positive rate.

## 6. DECISION log
- DECISION (OURS): pool = all same-side `f1_at_level` hours with a ladder stop (no ledger cooldown), chosen over "all stop-valid hours" because it keeps the controls at a level.
- DECISION (OURS): Holm m = 42 and n_needed = 393 days recomputed, not copied.
- DECISION (OURS): the mean-net_R-of-C gate stays although V1 already shows it failing.
