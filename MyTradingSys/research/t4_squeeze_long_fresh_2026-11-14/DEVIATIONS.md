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
