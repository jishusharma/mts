# Independent G7 audit — gx3-gap-g7-slippage

Task brief executed: `python scripts/dev/tasks.py brief gap-g7-stop-slippage`. Card incomplete: mandatory pre-fetch review is absent. Completed steps 2–3 and preserved the gate; no aggTrades fetched and no measured default claimed. Every artifact is under `MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/`, overriding the card's legacy paths under the user's explicit write restriction. No git, sync.py, tasks.py done, push, account access or existing-code/test/card edits were performed.

## Findings

1. **HIGH — Missing mandatory C2 review receipt.** `MyTradingSys/research/lab_guy/specs/gap-g7-stop-slippage.md:7` requires a REVIEW-SPEC: ACCEPT|FIX|REWORK line in that note before any fetch. Parsing the complete 31-line file finds **0** such anchored lines, including **0** ACCEPT stamps. Thus fetch and the card's measurement done-when cannot proceed. Reproduce: `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/prepare_days.py`; evidence.json records `review_spec_stamps: []` and the source SHA256 `a08286abb95dbc2c61f60ec235a8292e7afcdff4ba86f7c3a1223a39679113f3`. An authorized NUC reviewer must review/fix the spec and add the receipt; this worker cannot edit that existing file. This is a prerequisite failure, not a trading-code defect.

2. **HIGH — Trade-through gap is incorrectly described as tick-bounded.** `MyTradingSys/research/lab_guy/specs/gap-g7-stop-slippage.md:23` claims first-trade overshoot is bounded by the $0.10 tick. Prices can skip ticks. At level 50,000, consecutive tick-aligned prices 49,999.90 and 50,005.00 yield a first crossing overshoot of **$5 = 50 ticks = 1bp = .025R** at the .40% stop. Both prices obey the stated grid; the gap violates the asserted bound. This also contradicts the required $5 test at spec line 11. Reproduce: `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/write_report.py` (assertion uses those exact prices), or `test_latency_and_same_timestamp` in test_slippage.py. Correct the wording before the C2 stamp; retain full gap overshoots. No claim about actual frequency or market medians is possible from synthetic data.

## Independent derivation and checks

Expected values were derived before helper implementation from prereg lines 11/23 and FORMULAS.md:286 (risk as price-distance fraction), :350 (signed fractional return) and :468 (price displacement divided by R). FORMULAS contains no dedicated G7 formula; prereg item 5 supplies the level denominator and three fixed stop widths. No production slippage code supplied expected values. Direction is crossing direction (+1 upward, -1 downward), so adverse slip is positive in either direction and post-trigger reversals remain negative. Delta zero uses the first qualifying crossing trade; +250/+1000ms use the last trade at or before the target. Same-ms ambiguity is explicitly covered by the fixture.

Tests: initial run **failed** on absent slippage.py (one collection error); unchanged expectations then **13 passed** after independent helper implementation. Recorded in tests_red.txt / tests_green.txt. Reproduce green: `python -B -m pytest MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/test_slippage.py -q -p no:cacheprovider --confcutdir=MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage`.

Day selection: prescribed `bt_data.load_klines` with start_ms=1640995200000 and end_ms=1719792000000 returned **1,313,280 bars**, first 2022-01-01 00:00 UTC, last 2024-06-30 23:59 UTC. **912 complete days**, no missing days, no incomplete days, **304 per tercile**, **12 distinct selected days** before any slippage data. All returned timestamps assert strictly below cutoff. Loader scans CSV timestamps to apply its filter; no post-cutoff OHLC prices were returned or analyzed. Selection choices OURS: daily range (H-L)/first UTC open *100; rank thirds with chronological tie-break; four nearest endpoint-inclusive indices (0,101,202,303). Full eligible ranks retained in eligible_days.csv.

## Done-when disposition

| Requirement | Result |
|---|---|
| Tests red then green; gap, exact, none, both directions, latencies, ties, cutoff | PASS, 13 cases |
| DEV selection, 12 days, no selected validation/holdout day | PASS |
| Review in spec before fetch | BLOCKED: zero receipts |
| One-day public aggTrades fetch / ZIP SHA256 / events | NOT RUN; blank hashes explicitly marked BLOCKED |
| Nine bucket/latency measurements, R widths, median/p90/bootstrap | NOT MET; SLIPPAGE.md contains NA, not invented results |
| Counts-only extension, cap eight / THIN | Frozen, not evaluated before four processed days |
| TRIALS rows | Local TRIALS.md written; central ledger excluded by write boundary |
| No aggTrades ZIP left | No download or scratch created; output recursive ZIP count zero |
| Default labelled OURS / UNCHECKED; no adoption | Rule documented, numeric default unavailable |
| Content commit SHA / empty git cherry / git ls-tree | Not run: user forbids git; harvester verification required |

Remaining work also requires resolving the explicit write-boundary conflict: spec line 19 requires scratch outside the repository, while this worker may write only inside `MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage`. The authorized coordinator must supply an allowed arrangement for a later fetch run. No substitute download location was used.

Reproduce preparation with `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/prepare_days.py`; reproduce report checks with `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx3-gap-g7-slippage/write_report.py`. evidence.json and sha256.txt provide parsed counts and local artifact integrity. These are local audit artifacts, not shipped or accepted research.

Result: BLOCKED before aggTrades fetch: missing mandatory REVIEW-SPEC; 13 tests pass, 912 DEV days checked, 12 selected, no measured slippage default.
