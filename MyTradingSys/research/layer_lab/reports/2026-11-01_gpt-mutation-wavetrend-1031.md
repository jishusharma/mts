FIX-FIRST

The requested arithmetic and mutation checks pass: original 13/13 tests; full suite kills 5/5 mutations; golden comparisons kill 3/5. Twenty independent WT1/WT2 pairs match at 1e-9. Fix-first concerns the supporting parity contract's overclaim and fixture schema, not a demonstrated oscillator arithmetic defect. No production code or specification was changed.

## Evidence and scope

Paths below are relative to MyTradingSys unless stated otherwise. Read `backtest/layers/wavetrend/wavetrend.py:1-109`, `test_wavetrend.py:1-140`, the entire golden CSV (header plus 400 rows), input fixture (400 rows), `make_golden.py:1-25`, and the WaveTrend definition in `backtest/layers/FORMULAS.md:516-530`. Other formula families are not part of this WaveTrend parity verdict.

Source chain checked: `research/wavetrend_2026-10-17/PARITY_CONTRACT.md:1-44`; both files under its `source_snapshot/` (Crosses and marketcalls gist); `wt_parity_ref.py`, `test_wt_parity_ref.py`, `CLAUDE_VERIFY.md`, and `METHOD_AND_MTS.md`. The math and bands are sourced to saved Pine text, not trader transcript/trade ledger rows; no such rows are cited for this oscillator. No fresh online-source or Pine-runtime verification is claimed. Layer context: `system/LAYERS.md:250-261`; earlier aggregate rederivation report `research/layer_lab/reports/2026-10-27_lf-wavetrend-gpt-rederive.md` concerns atlas outcomes, not this formula audit.

Reproduction (from repository root):

`python -B MyTradingSys/research/layer_lab/gpt-mutation-wavetrend-1031/mutations.py.txt`

`python -B MyTradingSys/research/wavetrend_2026-10-17/test_wt_parity_ref.py`

Second command: seed difference settles below 1e-3 after bar 144; OK. First command loads each single-change scratch module into a fresh module namespace and executes the unchanged existing tests against it. Baseline passes before mutations; mutant failures are assertion failures, zero import/runtime errors. Scratch copies are saved as `.py.txt`; no repo test is added. Full failures and hashes: `../gpt-mutation-wavetrend-1031/test-output.txt` and `results.json`.

Only the committed January 2022 DEV fixture was used: open times 2022-01-01 00:00 through 2022-01-17 15:00 UTC, 400 contiguous one-hour bars. Timestamp equality between input and golden is asserted. No external market archive, holdout, strategy, Tom/Fabio encoding, tuning, trade return or fee-net backtest was run.

## Mutation results

Golden-only means exactly the existing golden value and event assertions (`test_wavetrend.py:33-46`), excluding synthetic tests and warm-up checks.

| Mutation (one at a time) | Source line | Full 13-test suite | Golden CSV | Failing tests |
|---|---|---|---|---|
| Channel length 10 -> 11 | wavetrend.py:16 | KILLED | KILLED | golden values, golden events, two-bar hand value |
| Average length 21 -> 22 | wavetrend.py:16 | KILLED | KILLED | golden values, golden events |
| Channel EMA numerator 2 -> 1 (a2 unchanged) | wavetrend.py:76 | KILLED | KILLED | golden values, golden events, two-bar hand value |
| Update last side on ties too (`if side != 0` -> `if True`) | wavetrend.py:57 | KILLED | SURVIVING | tie conventions |
| Outer overbought level 60 -> 61 (also mirrors oversold through shared constant) | wavetrend.py:17 | KILLED | SURVIVING | zone boundaries |

MATCH: full suite survivors = none. Golden survivors = tie cross and outer band. These are not surviving bugs in the full suite. Five hand-selected mutants are not exhaustive mutation coverage.

## Independent arithmetic

The scratch oracle uses 50-digit Decimal arithmetic, separate whole-series EMA passes with `e + (x-e)*2/(n+1)`, first-valid seeds, hlc3, 10/10/21 EMA lengths, coefficient 0.015, and a four-value arithmetic mean, directly from FORMULAS.md:520-527. It does not call production or the reference module to generate expected values. Production is called only for comparison. Warm-up is handled by choosing post-warmup indices 200,210,...,390; these indices were fixed before examining deviations. Twenty pairs = 40 numeric comparisons against each comparator.

MATCH: maximum absolute error vs module **6.465938895416912e-12**; vs golden **6.7914562862370076e-12**, both below 1e-9. All 20 rows, independent full-precision numbers, module numbers, golden numbers and open timestamps are in `../gpt-mutation-wavetrend-1031/independent-20.csv:2-21`. For example index 200: independent WT1 3.197653821517513, WT2 4.545412858318857; module 3.1976538215212993 / 4.5454128583223845.

MATCH: source snapshots lines 7-12 pin 10,21,+/-60,+/-53; lines 14-21 pin hlc3, both channel EMAs, 0.015, average EMA and SMA4. Module lines 16-19,24-43,46-69,76-109 agree with FORMULAS section 20 for these constants, inclusive zones, tie skipping, NaN reset, gap suppression, first valid EMA seed, 200 valid-ci warmup, flat tolerance, bar-close availability and last closed HTF selection. WARMUP, tolerance, tie convention and zone names are explicitly OURS. Hand calculation 5.5/0.015 and SMA4 examples agree. Spreadsheet-style parity, not Pine-runtime parity.

## Findings

| Severity | File:line | What is wrong / classification | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | research/wavetrend_2026-10-17/PARITY_CONTRACT.md:23 | MISMATCH: finite numeric convergence is promoted to an unconditional claim that seed choice cannot affect any later event. | `test_wt_parity_ref.py:26-33` measures WT1 error on one 1,500-bar synthetic path; it never proves event equality or bounds distance of WT1-WT2 from zero. A nonzero error can change a sign near zero. Measured bar 144 MATCH; universal event conclusion unsupported. | State the measured numeric bound and path only; remove the universal event guarantee or add a bounded event-margin argument in a separately reviewed change. |
| LOW | research/wavetrend_2026-10-17/PARITY_CONTRACT.md:29; backtest/layers/wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv:1 | MISMATCH: contract says a fixture without both timestamps is invalid; golden contains open_time but no available_at. | CSV header is open_time,wt1,wt2,event. Module returns available_at and existing test checks open+H, so this is a fixture-contract mismatch, not observed look-ahead. | Add close/availability to the fixture or explicitly distinguish input fixtures from emitted rows in the contract. |
| LOW | backtest/layers/wavetrend/test_wavetrend.py:33-46; golden CSV:1 | MATCH (coverage limitation): golden alone misses two specified mutants. | Cross-rule mutant and band mutant survive golden assertions; synthetic tie and boundary tests kill both. Golden has no zone column. | Retain mandatory synthetic tests; do not advertise the CSV alone as complete rule coverage. No new test needed for these already-killed mutants. |
| LOW | backtest/layers/FORMULAS.md:530; research/wavetrend_2026-10-17/PARITY_CONTRACT.md:32 | NOT_IN_DATA: Pine-runtime parity unavailable. | Saved formula sources and pandas fixture exist; no same-bar TradingView export supplied in this evidence chain. | Keep existing spreadsheet-only label; acquire dated same-input export before making Pine-runtime parity claims. Not a blocker for this audit. |

## PRE_REG applicability

Read `backtest/PRE_REG_TEMPLATE.md`. This is an indicator audit, not a backtest: (1) source home = saved mechanical Pine formula; fixture BTCUSDT 1h; (2) trader ground-truth ledger N/A; (3) trade recall/fire-rate gate N/A; (4) required H/L/C/t inputs present; (5) raw-formula parity checked above, Pine runtime NOT_IN_DATA; (6) costs/stop/R N/A; (7) fills N/A; (8) exits N/A; (9) trading null N/A; (10) power N/A, 20 pairs are arithmetic checks not edge observations; (11) DEV-only and trial logged, no holdout; (12) regime/session returns N/A. Pre-build items 0a-0g N/A: no strategy build or profitability claim.

Earlier attempt is already recorded in TRIALS.md as blocked by a test-path scope conflict. This delivery follows the corrected scratch-only task and leaves prior artifacts intact. Current Decimal recomputation uses a separate specified 20-point sample; it does not replace the earlier attempt's numerical receipt.

Follow-up card created: `wavetrend-parity-contract-audit-1101` (SONNET, raw), for the MED and timestamp findings. No HIGH findings; no new test for a full-suite survivor is needed. No git, claim, ship, release or push was run; runner owns delivery.

Noticed: golden-only parity must not replace the existing tie and zone tests.
