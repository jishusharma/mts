# DEVIATIONS: T4 step A/C code vs the frozen PRE_REG (no rule changed)

Readings chosen where PRE_REG is silent or self-inconsistent, each closest to the SOURCE CELL (miner.py). PRE_REG.md is untouched.

1. Candidate list size: PRE_REG says "49" but the frozen list holds 48 names (cache README: 48 alts plus BTC and ETH). The list as written is used; all 48 have 4h spot and funding, none dropped.
2. Overlap filter runs per window (DEV and VAL separately), as the miner's `cell_picks` does. A DEV trade that runs into 2024 therefore does not block a VAL signal. PRE_REG's "per coin" is silent on windows.
3. Overlap rule is the miner's: a signal is skipped if its bar index is below the last occupied bar of the open trade; a signal ON that bar is allowed (RIDE exits at the next open, so there is no overlap).
4. RIDE and T3R share the same onset signals but each kind has its own overlap filter (different holding times), so the T3R signal set is not a subset of the RIDE signal set.
5. Funding window closes at the open of the bar after the exit bar for every exit kind (the miner's `xt = jj + 1`); for a T3R target or stop fill inside a bar this charges the prints up to that bar end.
6. The funding cache ends 2026-10-31 20:00Z (fetch worker note). FUND_LO cannot fire after that date, and 0 trades exit beyond the file (column `fund_covered`, count in coverage.json).
7. Placebo (step C): "resolved" is implemented by redrawing an unresolved random bar up to 12 times; matches still unresolved are dropped and counted (`dropped_matches`). Candidates need no ATR (the stop distance is the real trade's S / entry).
8. Basket baseline: "past their entry-window start" = day >= max(2020-01-01, first funding day of the coin), the first funding day rounded up to the next UTC day when the first print is not at 00:00.
9. BTC closes for the phase label are read from the miner cache; spot_1d and spot_4h of the wave cache are used for the fresh coins. Old-20 row uses the miner cache for all inputs (its 4h/1d/funding files, same loader).
10. Brain label columns (`brain_label`, `brain_cycle`) are looked up by the entry UTC day row of phase_daily.csv (the row for date d is built from closes through d-1). Descriptive only.
11. Entry bar of a coin's last bar: a signal on the final bar has no next open and is never a candidate.
12. `t4_core.py` sets `onset[0] = False` explicitly; the miner reached the same result only because no indicator is defined on bar 0.
13. FUND_LO is STRICT (fix round 1): False unless all 90 prior daily-fd3 values are finite. This departs from miner.py (which counts NaN as "not <=" and still divides by 90) and follows the PRE_REG sentence. Removes 22 RIDE / 25 T3R DEV trades from 2020 (0 VAL). See FIXLOG.md.
14. Funding print stamps are snapped to the nearest minute in `load_funding` (the cache jitters about half of the prints by 1 to 20 ms after the settlement instant). Minute snapping, not 8h snapping, because some coins pay every 4h or at shifted hours. Changes funding of 128 of the 442 trades that exist before and after, max |R| change 0.17. See FIXLOG.md.
15. Phase day convention: the phase label of an entry day d is the BTC label built from closes through d-1, and the halving clock is counted at d-1 (miner.py phase_table, keyed to d+1). The 8 trades with signal 2024-04-20 (entry that day) therefore read days-since-halving at 2024-04-19 (last halving 2020-05-11, 1439 days, late) and are labelled UP_L, not UP_E. Entries, exits and R do not depend on it; only the by-phase breakdown does.
16. Data notes for RESULT: LUNAUSDT splices old LUNA into LUNA2 (5e-05 on 2022-05-13 to 1.0 on 2022-05-31); FTT has a 1867-bar gap (2022-11-15 to 2023-09-22); 31 of 50 4h files have 2 to 8 bar outages. No trade is contaminated (only LUNA trade 2021-03-21, no FTT trades). Placebo runs on VAL only. Placebo candidates need no 90-day funding warm-up and draws are independent across trades (bar 4 slightly anti-conservative vs the clustered mean). Bar 5 uses the T3R-own overlap set. PRE_REG wording "49" coins and `t4_lib.py` mean 48 coins and `t4_core.py`.
17. Stats: an undefined ex-best-5 mean (fewer than 6 entry weeks) gives UNDERPOWERED, never KILL.
