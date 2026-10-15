# Fable 5.1 pilot: paste everything below the line into a NEW session (model: Fable 5.1, effort: high)

---

MTS builder session, Fable 5.1 pilot. Follow CLAUDE.md boot steps 1-3 (sync.py start, STATUS.md), then do ONE task: the pre-registration for the gross-effect screen. The 15-tool-turn session cap applies.

**Measure the pilot first.** Call `get_usage` and write the three weekly/5-hour percentages and the UTC time into `PILOT_USAGE.md` in the output folder. Do the same again just before you ship. Also list the other sessions that ran in between (`list_sessions`; the Haiku "Mts dispatcher" tick runs every 10 min). Budget stop: if `Weekly · all models` has risen 3 points or more above the start value at any check, finish the section you are writing, ship what exists, and say so.

**Why this task.** Today's audits (`research/layer_lab/reports/2026-10-15_claude-side-audit.md`, `2026-10-15_revalidate-strategy-audit-with-counterev.md`, `2026-10-15_strategy-direction-audit.md`) agree that no tested configuration has a net edge. They also agree the next step is a gross-effect screen with costs declared up front, before any more detector or layer work. The operator has decided the venue: the Binance tape is the research target, and a separate Deribit execution check gates any fill or profit claim. No card or pre-registration for the screen exists yet. Read those three reports plus `research/tom_btc_2026-10-13/TOM_ON_BTC.md` (fee and stop floors, DEV/VAL/HOLDOUT split) and `research/orderflow_views_2026-10-14/` (the existing flow study and its gap-stop defect). Read what you need, not everything.

**Deliverable** (`MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md`). It is a pre-registration that a Sonnet session can execute mechanically, with no judgement calls left:
1. Economic target: instrument, size, fee tier (taker and maker), slippage bound, turnover, drawdown tolerance, and the calendar-time benchmark. Label every number SOURCED (file:line) or OURS. Where the repo has no answer, choose a default and mark it OURS.
2. Candidates: the conditional location + flow signal, and a plain price/context control that uses the same screen. Define each as an exact rule on data we already have.
3. Effect measure: gross forward return against delay after bar close plus a stated arrival latency, i.e. the decay curve. Use no labels taken at bar open. Fix the horizons.
4. Pass/fail rule fixed now: what gross effect, at which delay, must exceed round-trip cost plus slippage, with what t-stat or CI, on DEV only. Fail means stop: no detector work follows.
5. Eligible-event ledger shared by test and control (encounters, cooldowns, estimand), plus the exposure-ledger row this study writes (G6).
6. Data split: DEV only. VALIDATION is read once, later, and HOLDOUT stays sealed (A7 is open).
7. Known traps to avoid, at minimum the gap-stop booking in orderflow_views `trade()`.

Then write one task card (`tasks.py` format, lane=SONNET) that runs the screen exactly as pre-registered. Put it in the queue behind Q65, and recommend in the card note that Krown Q66-Q69 wait for the screen verdict (the operator's open Q2). Do not run the screen, do not read VALIDATION or HOLDOUT, and do not change production code.

**Finish.** Run `run_all_tests.py --quick` if you touched anything the gate covers. Then `sync.py ship` with `Result: PRE_REG + card <slug>; pilot usage all-models +X pts, Fable +Y pts`, and `sync.py release`. End with a reply of five lines or fewer: the deliverable path, the card slug, and the usage before and after.
