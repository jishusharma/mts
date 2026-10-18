# Level ledger and Java zone check (2026-10-16, session ctx-audit-ledger)

Source of the two items: `pit_levels_2026-10-16/REPORT.md` D2 (build the level ledger of PIT_CONTRACT section 1) and D3 (verify the Java zones).
DECISION (OURS): scope is the conservative minimum: the five prior-day origins (h, l, poc, vah, val) that the pit_levels and context_factors studies read, BTCUSDT 1m, DEV days only;
weekly/swing/fractal/session origins are NOT in this ledger (not built here, so not claimed). Java check = daily-profile POC/VAH/VAL only (the one Java zone with a runnable harness,
`tom_profile_parity.py`); VWAP anchor (`buildVwap`) is still NOT VERIFIED.

- `level_ledger.py` -> `LEVEL_LEDGER.csv`: **4,560 levels** (912 DEV days x 5); `available_at` = next UTC midnight, `formed_at` = open of the last bar used. No day skipped.
- `java_zone_check.py` -> `ZONE_CHECK.csv`: every 19th DEV day (48 days, 144 levels), live Java `buildVp` (dynamic ~5 USDT grid, triangular weights) vs `vp_pivot_probe.build_profile` (10 USDT bins).
  Tolerance max(Java bin, 10 USDT): **79 / 144 = 54.9 % match** (POC 28/48, VAH 24/48, VAL 27/48). Median |diff| 7.3 / 9.5 / 8.5 USDT (inside one bin), p90 85 / 33 / 40, max 2,051: on days with two competing peaks the
  two builders pick different POCs. Reading: the Java zones are NOT the research zones; tom_bt results (Java snapshots) keep the label "levels NOT VERIFIED PIT / not equal to research builder". Counts and prices only, no outcome.
- Tests: `test_level_ledger.py` (registered in run_extra_tests.py, B150). The module is new, so on the parent commit the test file cannot import (`git show <sha>^` has no level_ledger.py): fail-first by absence;
  the planted-day-1-high test pins the PIT property.
Re-run: `JAVA_HOME` JDK on PATH, then `python MyTradingSys/research/level_ledger_2026-10-16/level_ledger.py` and `java_zone_check.py`.
