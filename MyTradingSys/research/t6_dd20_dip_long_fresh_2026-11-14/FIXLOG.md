# T6 FIXLOG (mechanical fix round). PRE_REG.md untouched; no rule or parameter changed.

Trade count before: 1364 (DEV 803, VAL 561). After step A re-run: 1364 (DEV 803, VAL 561); trades.csv byte-identical.

| Finding | Severity | Verdict | Detail |
|---|---|---|---|
| Cost-constant gate: `FEE_RT = 2 * fees...` matched ASSIGN regex of test_no_own_costs.py | major | FIXED | Renamed to `RT_COST` (t6_core.py:19, :153; test_t6_core.py:149). Still computed from fees.BINANCE_TAKER and fees.SLIPPAGE_RT_S13. Reproduced: with the old name test_trunk_has_no_new_own_cost_file fails; with the new name 6/6 pass. No trade changes. |
| Longest-contiguous-run rule drops pre-gap LUNA (5 events) and FTT (11 events), ~16 DEV trades; PRE_REG survivorship note says kept to last bar | major | NOT FIXABLE as a mechanical fix | The PRE_REG contradicts itself: the SOURCED Daily-bars row (longest contiguous run) vs the survivorship note. Using all runs changes the sample rule, so it needs a new PRE_REG, not a code fix. Reading kept = SOURCED source rule (DEVIATIONS.md #1). VAL unaffected (all dropped trades are before 2024). RESULT.md must state: DEV excludes pre-gap LUNA/FTT, survivorship bias is larger than the note says, the survivorship wording is not satisfied. |

Minor findings carried to RESULT wording (no code change): ZIL 2026-02-02, AXS 2026-02-09 (about +33% funding credits) and ONE 2026-09-07 (+450% gross) dominate trade-weighted VAL; 3 DEV trades without stop row (MATIC, SUSHI, WAVES 2021-05-24); placebo pool starts at week 9 and includes event Mondays; 202 trades on the flat funding rule; ATR convention is source-study/OURS, not FORMULAS.md; 12 events skipped as unresolved (window past data end); verdict flags are applied by hand. Recompute checker: clean (4 trades matched, 1364 keys reproduced).
