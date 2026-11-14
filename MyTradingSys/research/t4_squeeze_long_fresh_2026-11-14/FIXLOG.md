# FIXLOG: T4 step A fix round 1 (mechanical, no rule changed, PRE_REG.md untouched, no pooled statistic run)

Counts are fresh non-bear trades.csv. Before: RIDE DEV 128 / VAL 111, T3R DEV 138 / VAL 112. After: RIDE DEV 106 / VAL 111, T3R DEV 113 / VAL 112.

| # | Finding | Verdict | Cause | Fix | Trades before / after |
|---|---|---|---|---|---|
| 1 | FUND_LO fires with fewer than 90 prior funding values (blocker, 2 checkers) | REAL, fixed | `pct_rank` counted NaN as "not <=" but divided by the window length, so k valid values gave a share of at most k/90 and passed `<= 0.10` on thin history | `pct_rank` returns NaN unless the whole window is finite (also blocks gaps inside the window); test `test_fund_lo_false_until_90_full_prior_values` plus the amended `test_pct_rank_...` fail on the old code | RIDE DEV 128 to 106 (22 removed, the same 22 the checkers named), T3R DEV 138 to 113 (25 removed). VAL unchanged (111, 112). Old-20 row: RIDE DEV 39, T3R DEV 44 (descriptive) |
| 2 | Funding settlement stamps inconsistent, 1 to 3 ms jitter (major) | REAL, fixed with a different rounding | 48% of prints are stamped a few ms after the boundary (max 20 ms seen); `searchsorted(side=right)` then charged or dropped a print at a bar open by jitter alone | `snap_ts` in `load_funding`: nearest whole minute. NOT nearest 8h as proposed: the cache has 4h-interval and hour-shifted coins (e.g. ANKR 682 prints at 04:00), which 8h rounding would move to the wrong bar. Test `test_funding_print_jitter_...` (0, 1, 3, 17 ms give identical funding) fails on the old code | Row set unchanged by this fix. Funding changed on 128 of 442 surviving trades (53 VAL), entry price, exit price, exit reason and phase identical, max abs R change 0.17 |
| 3 | Halving-day phase label UP_L vs UP_E (minor) | Convention stated, no code change | Label of entry day d uses the halving clock at d-1 (miner convention) | DEVIATIONS 15 | none |
| 4 | LUNA splice, FTT gap (minor) | Documented | no trade affected; placebo is VAL only | DEVIATIONS 16 | none |
| 5 | Placebo not conditioned on FUND_LO warm-up, trades independent (minor) | Documented for RESULT | PRE_REG implies it | DEVIATIONS 16 | none |
| 6 | T3R signal set is its own overlap set (minor) | Documented | already DEVIATIONS 4 | DEVIATIONS 16 | none |
| 7 | Funding window extends to next bar open for stop/target/time (minor) | Documented, conservative | miner `xt = jj + 1`, DEVIATIONS 5 | none | none |
| 8 | PRE_REG says 49 coins and t4_lib.py (minor) | Documented | frozen PRE_REG not edited | DEVIATIONS 16 | none |
| 9 | 2 lookahead WARN rows, NaN ex-best-5 read as KILL (minor) | WARN rows are bootstrap/placebo percentiles on resampled means, not features (no allowlist row self-approved; rows: t4_stats.py lines 50 and 119). NaN rule fixed in code | `ex_best_weeks` NaN made bar5 False and kill True | NaN gives verdict UNDERPOWERED, kill False | none |

Checks after the fix: 37 tests pass (8 s); lookahead_lint on the folder: 0 FAIL, the 2 WARN rows above; prereg_context_lint clean; step A rerun 27 s.
Mutation: new tests fail on the pre-fix t4_core.py (3 failed, 34 passed).

## Ship-gate rename (2026-11-14, coordinator, no rule or number change)
The tree-wide cost-constant gate (T06 scanner, step 3xm) flagged three names bound to numeric literals in t4_core.py:
COST12, FUND_PCT, FUND_SNAP_MS. Renamed to ROUND_TRIP, LO_PCTL, SNAP_MS (ROUND_TRIP_HALF for COST6). Values and formulas unchanged;
the cost still comes from fees.py. Tests re-run; trades.csv not regenerated (no behaviour change), checked below.
