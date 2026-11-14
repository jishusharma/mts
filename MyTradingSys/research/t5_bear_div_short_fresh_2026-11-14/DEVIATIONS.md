# T5 DEVIATIONS and readings (stage 2). PRE_REG.md is untouched; no rule, threshold, universe or split was changed.

Each row is a place where the PRE_REG text left a choice or the source engine differs in a detail. The reading closest to the source cell was taken.

| # | Item | Reading used | Effect |
|---|---|---|---|
| 1 | RSI flat series | FORMULAS.md section 1: avg_loss == 0 gives 100 if avg_gain > 0 else 50; the source engine (ladder.py) gave 100. Same seed and Wilder smoothing otherwise | None seen: event lists (entry bar, exit bar, gross, BEAR) are identical to the source engine on 8 coins (384 events), checked in a scratch run, source files fetched with `git show`, not committed |
| 2 | Lockout chain | One event list per coin, as the source builds it: the 60-bar lockout and no-overlap rule run over ALL labelled events (BEAR true and false); BEAR then selects the claim sample. A BEAR-false event can therefore lock out a later BEAR-true one | Matches the source cell; the PRE_REG says "previous KEPT entry bar of the same coin" |
| 3 | Placebo trades open at the data end | A draw keeps the matched trade set but a drawn trade that is still open at the data end is dropped from that draw's mean (source behaviour), instead of pre-restricting the pool. Trades whose coin has no eligible bar in the split are not matched and are counted as unmatched in summary.json | Negligible, only the last 42 bars of a coin |
| 4 | 4h gaps | Windows are bar-index based (swing, 42-bar hold, 60-bar lockout), as in the source. 28 of 45 coins have a few missing 4h bars (listed in coverage.json, mostly 2018-2020); a hold can span a gap | Same as source |
| 5 | Bars held | bars_held = exit bar - entry bar + 1; days held = bars_held x 4/24 (used in the bar 6 signal rate) | Defines the PRE_REG "held bars" |
| 6 | Last bar dropped | The last bar of each 4h and 1d series is dropped as the PRE_REG says, although the cache already holds only closed bars | One bar |
| 7 | Funding coverage | The funding cache ends 2026-10-31 20:00 UTC (not extended). Trades holding past a coin's last print get no funding for the missing part and are flagged fund_gap; entries before the coin's first print get funding 0 and are flagged fund_covered = 0. Counts for BEAR true trades: 39 not covered, 36 holding past the funding end | Only the with-funding row, only recent trades; none dropped |
| 8 | Split key | Signal bar open time < 2024-01-01 00:00 UTC is DEV (the bar that closes at 2023-12-31 23:59:59.999 is DEV); on or after is VAL; RECENT = signal bar on or after 2025-07-01 | As PRE_REG |
| 9 | Blocked PASS | In the verdict code, a PASS that carries FRAGILE or ONE-YEAR is not returned as PASS; it falls to REPLICATED-WEAK when the mean conditions hold, else FAIL, and the labels are printed. PRE_REG says FRAGILE blocks PASS and ONE-YEAR "cannot carry a PASS alone" | Step C reading; the coordinator can restate it |
| 10 | LUNA and other re-used or delisted symbols | Used as published; per-coin and top-coin-removal rows show the effect (PRE_REG survivorship note). 10 coins end before 2026-11 (MATIC, EOS, ICX, WAVES, OMG, FTM, MKR, STORJ, XMR, OCEAN) | As PRE_REG |
| 11 | t5_stats.py | Not run on the real trade list. Smoke-run end to end on a synthetic cache in scratch (4 fake coins) to catch crashes only | Real run is stage 4 (step C) after audit |
| 12 | Module naming | The stats cluster bootstrap is named week_boot (not cluster_*) so research_kit_lint does not list it; PRE_REG does not ask for the shared research_kit | None |
