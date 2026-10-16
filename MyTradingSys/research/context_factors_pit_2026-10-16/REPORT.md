# REPORT: point-in-time context factors for backtesting (DEV only, 2026-10-16, Fable 5.1)

Session: worktree branch `claude/context-factors-backtesting-1a25f2`, claim `context-factors`. Everything in
`MyTradingSys/research/context_factors_pit_2026-10-16/`. No VALIDATION or HOLDOUT bar read; no outcome column anywhere; no
production or live-path file changed (the only files outside the folder: `scripts/dev/run_extra_tests.py` gains the test file,
`scripts/dev/lookahead_allowlist.tsv` gains 20 reviewed rows, `MyTradingSys/system/tasks/context-factors-one-run.json`).

## Verdict
**Seven context factors (side-aware levels, confluence, the operator's daily-candle stop ladder, candle patterns, Bollinger
state, phase, own additions incl. funding) are built point-in-time and proven three ways: a bar-by-bar replay build and a
vectorised build return identical rows at 128,736 DEV decision points (0 mismatching fields of 85); independent pandas
arithmetic from the raw CSVs agrees at 324 of 324 field comparisons; a trader's-eye read at 12 seeded random points agrees at
12 of 12. All 7 planted leaks (today's daily OHLC in the ladder, bands on the forming bar, pattern on the forming candle, an
unconfirmed pivot, today's profile, full-sample percentiles, next-period funding) are caught by the tests.** Four engine bugs
were found and fixed on the way (two float-precision drifts, one tie rounding, one off-by-one prior candle at bucket closes)
and one bug in the checking code (pandas week anchor), all in `ANGLES.md`. The pre-registration freezes 14 filter cells
(7 factors x 2 sides) on the operator's ladder trade against context_null matched controls; 9 cells reach the cost-free power
bar before any outcome, 5 are INCONCLUSIVE by count. Card `context-factors-one-run` (lane SONNET) runs it once.

## Factors kept and dropped
| factor | kept? | why |
|---|---|---|
| F1 side-aware levels (9 sources) | kept | PIT proven; nearest-source counts in `COUNTS.md` F1 |
| F2 confluence, age, touches | kept | PIT proven; 1,305 / 1,307 episodes with >= 2 layers |
| F3 stop ladder (1d, 12h, 8h; W = 2.5 %) | kept | PIT proven (RT-1 fixed); stop-width and cost-in-R distributions in `COUNTS.md` F3 |
| F4 candle patterns (4h/8h/12h/1d) | kept, verdict INCONCLUSIVE by count | 261 / 287 directional episodes < 572 |
| F5 Bollinger state, long confidence, short veto | kept, verdict INCONCLUSIVE by count | 36 / 40 episodes: the operator's two band rules are rare at a level |
| F6 phase A (fractal) / B (30-day return) | kept (A primary, B logged) | A and B agree on 39 % of events: they are different words |
| F7 vol regime, squeeze, session, weekend, approach, sweep, HTF alignment, funding | kept, only `htf_align` gets a verdict | others descriptive to keep Holm m small |
| open interest | dropped: NOT_IN_DATA | no OI history for DEV on disk |

## Top findings
1. **At-level is nearly universal.** With nine level sources and a half-ATR zone, 94.5 % of 1h grid rows sit "at" a side-aware
   level (20,688 of 21,888 long). A level ledger this dense says nothing by itself; the first-touch episode (1,636 long /
   1,651 short with a valid stop) is the unit that can carry a verdict. This is the biggest surprise.
2. **The prior-candle convention changes every ladder row at a bucket close.** At 8h/12h/1d closes the first draft skipped the
   candle that had just closed; 629 of 2,736 8h-close grid points change a level field and every one changes the ladder
   (`prior_rule_count.md`). Both builds now use the last closed bucket; the alternative is trial T8, counted only.
3. **Float precision is a PIT bug in disguise.** Cumsum-based bands and ATR drifted by 1e-9 over DEV and flipped band-touch and
   zone-boundary ties, so replay and vec disagreed in a way that looked like leakage. Two-pass windows fixed it (`ANGLES.md` a).
4. **The operator's stop ladder is cheap at the daily rung.** Median chosen stop 1.20 % (0.116 R of taker cost), but 10 % of
   events have a stop below 0.37 % (0.38 R of cost); the 0.56 % floor drops those (`COUNTS.md` F3).
5. **The operator's Bollinger rules rarely coincide with a level.** 36 long re-entries and 40 short walk-down vetoes at a first
   touch in 2.5 years: the rule exists, the sample does not.
6. **Hand checking can be wrong too.** The pandas checker anchored weeks on the archive's first Saturday; four "mismatches" were
   the checker's (`ANGLES.md` c).

## Prior-verdict review (ANGLES.md, last section)
All six listed studies build their levels / phase / candle context point-in-time at the lines cited. `rsi_divergence_mtf` and
`eur_low_us_sweep` read every split at once: **eur_low_us_sweep's HOLDOUT-read row in `VERDICTS.csv:3` is REAL, not a parse
error** (`RESULT.md:8, :21, :38` report DEV, VAL and HOLDOUT numbers side by side). Every prior row tests a SETUP; this
study tests context FILTERS on the ladder trade: a different family, kill scopes do not overlap (`PRE_REG.md` section 4, 9).

## Notes
- **pit_levels overlap.** `research/pit_levels_2026-10-16/` (on origin/fast-track, not touched here) audits the existing
  `backtest/` builders and defines a ledger schema; this folder builds a new engine with its own ledger. The two agree on
  `available_at`; its card tests a setup (failed auction at the prior-day value area), ours tests filters.
- **Folder name.** This work lives in `research/context_factors_pit_2026-10-16/`: when shipping, `origin/fast-track` already held `research/context_factors_2026-10-16/` from another session (same prompt, run on jis-nuc: its own `context_asof.py`, `PRE_REG.md`, `PRE_REG_V2.md` and a `RESULT.md`, i.e. an outcome already read). Merging over it would have overwritten a frozen, already-read pre-registration, so nothing here touches that folder; the two studies are independent builds of the same idea and the next session should compare their ledgers (`ANGLES.md` of each) before either card runs.
- **CI RED is stale.** `STATUS.md:6` says CI RED (oldest ungreen 86ee2701, 3.2 h); the gross screen recorded the same stale
  state the day before. No CI work in this session (docs, research scripts and tests only; quick gate run before shipping).
- `grid_context.csv` (34 MB, 43,776 rows, no outcome) is regenerated by `run_compare.py` and gitignored.

## Operator decisions (each with the default taken; nothing waits on an answer)
| # | decision | default taken (OURS) | alternative counted |
|---|---|---|---|
| 1 | "too much" width W for the ladder | 2.5 % of price (about one DEV median daily range) | 1.5 % (T4: 9,365 vs 12,558 long events at the 1d rung) |
| 2 | fixed R target of the ladder trade | 1.5 R | none counted (an outcome parameter; changing it = new PRE_REG) |
| 3 | which candle is "the previous daily candle" at a close | the candle that just closed (last_closed) | cur_k - 1 (T8: 2,545 vs 2,581 long at_level at 8h closes) |
| 4 | zone width for "at a level" | 0.5 x ATR14(4h) | 1.0 x ATR (T2: 21,610 vs 20,688 long events) |
| 5 | plausible filter effect for the power bar | 0.15 R (n_min 572 for a cost-free contrast; a net claim would need 5,943 episodes and is not pre-registered) | none |

## Comparison with the Opus run of the same prompt (added 2026-10-16, after the first ship)

The same prompt ran on Opus 5.5 earlier the same day (`research/context_factors_2026-10-16/`, shipped 00:59Z; its card read one
composite cell: INCONCLUSIVE, VERDICTS.csv row 24). `COMPARISON.md` sets the two studies side by side. What survives both
engines: PIT rebuild works, "at a level" alone selects nothing (90 % / 94.5 % of hours), no single factor is testable on DEV in
day units, directional candle patterns at a level are rare. What does not: the band-walk veto (2 % vs 26 % of events), the phase
object, the ladder width, and the power verdict. **The counts verdict above ("9 of 14 cells") rests on episode units; in the
trunk's adopted day units it is 4 of 14 (F1 and F2, both sides).** PRE_REG.md is therefore never run; `PRE_REG_V2.md` (day units,
Holm m = 59, realised-MDE rule, a cross-engine agreement step, an audit card first) replaces it, and card `context-factors-one-run`
now points there and depends on `context-factors-pit-audit`.

## Next step
Run card `context-factors-one-run` (SONNET): episode ledger committed first, then one run of the 14 cells, `RESULT.md`,
14 `verdicts.py add` rows. A PASS on any cell earns a single VALIDATION read by a separate card; nothing adopts a rule.
