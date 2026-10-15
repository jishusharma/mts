# Gross-effect screen GPT audit

**FIX-FIRST** — The `INCONCLUSIVE` verdict is independently supported on DEV, but the runner does not protect the input manifest from silent replacement on a later run. This is a reproducibility finding, not a mismatch in the audited run's numbers.

## What was checked

- Read `gross_effect_screen_2026-10-15/PRE_REG.md` sections 2, 4, 5, and 7 before reading `RESULT.md`.
- Independently recomputed the eligible ledger counts from those frozen rules with the recorded Python source [gross_screen_independent_recount.py.txt](../gross_screen_independent_recount.py.txt), using only `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv` through `BTCUSDT-1m-2024-06.csv`. All 30 SHA256 values matched `DATA_MANIFEST.csv`; all 1,313,280 DEV bars were present, with no gaps. The loader rejected any timestamp at or after 2024-07-01. No later bar was read.
- Compared `screen.py` lines 43-131 and 134-164 with PRE_REG sections 2-5 and 7; compared output and verdict code at lines 168-255 and 271-299 with the reported values.
- Independently recomputed only T at the primary cell d=1, h=60 from the eligible timestamps and DEV opens. No other cell or variant was run; no audited screen/spec/test file was changed.

## Count and primary-cell comparison

| Measure | Independent recount | Screen / RESULT.md | Match |
|---|---:|---:|---|
| DEV bars / missing | 1,313,280 / 0 | 1,313,280 / 0 (`RESULT.md:42-44`) | MATCH |
| Ledger n_T | 40 | 40 (`RESULT.md:45`) | MATCH |
| Ledger n_notF | 1,400 | 1,400 (`RESULT.md:45`) | MATCH |
| Ledger n_C | 1,440 | 1,440 (`RESULT.md:45`) | MATCH |
| SHORT / LONG ledger rows | 735 / 705 | 735 / 705 (`RESULT.md:45`) | MATCH |
| Primary-cell available T / notF / C | 40 / 1,399 / 1,439 | 40 / 1,399 / 1,439 (`RESULT.md:46`) | MATCH |
| Primary-cell T mean raw G | -0.055276% | -0.05528% (`RESULT.md:25`) | MATCH |
| Primary-cell T mean after funding | -0.056776% | -0.0568% (`RESULT.md:8`) | MATCH |
| Primary-cell T t_cost | -1.509456 | -1.51 (`RESULT.md:8`) | MATCH |

The one unavailable primary outcome is a notF encounter whose exit would be beyond the DEV boundary; the screen does not read a later bar (`RESULT.md:37,46`). T has no dropped primary outcome. Its independent day-clustered SE is 0.130362%, giving `(mean_after_funding - 0.14) / SE = -1.509456`.

## Findings

| Severity | File:line | Evidence | Proposed fix |
|---|---|---|---|
| MED | `gross_effect_screen_2026-10-15/screen.py:259-267,351-353` | `manifest(files)` calculates the current hashes and overwrites `DATA_MANIFEST.csv` before `load_dev` runs. It never compares the inputs with the already-frozen manifest. The hashes do match for this audit, but a later changed archive could silently replace the baseline while producing a new result. | If the manifest already exists, validate the exact file set and SHA256 values before loading bars; refuse a mismatch and preserve the frozen manifest. Create it only for the original registered run. |

No other mismatch found in the checked rules: L1-L4 and the mirrored long side match PRE_REG; the 80th percentile uses NumPy's linear interpolation; D5 uses the closed five-bar window and the specified sign; and cooldown is applied once per side to all candidates before F partitioning (`screen.py:71-131`). It retains the earliest eligible candidate in a cluster and blocks same-side candidates through 60 following bars. The earliest eligible candidate is not necessarily the literal bar that set the extreme if L1/L3/L4 become true later.

## Verdict and DECISION (OURS) lines

The independent arm share is **40 / 1,440 = 2.7778%** of eligible encounters (SHORT 18/735 = 2.4490%; LONG 22/705 = 3.1206%). The result's `INCONCLUSIVE` is correct under PRE_REG section 4 because n_T=40 is below 200; the negative mean and t_cost do not relabel an underpowered arm as FAIL. This screen supports the stated stop for the family, while making no fill or profit claim.

The shared cooldown is after L but before the F split. Since candidates are time-sorted and cooldown is greedy per side, it keeps the first eligible ledger candidate in each same-side cluster; later candidates at or within 60 bars are suppressed. It does not promise to keep the literal extreme-setting bar if that bar does not yet pass all L conditions.

`RESULT.md:38` has three `DECISION (OURS)` clauses:

1. Testing INCONCLUSIVE after PASS_FLOW/PASS_CONTROL can change a verdict in a case where C passes while T is underpowered. It does **not** change this verdict: the current C mean and t_cost fail the cost hurdle (`RESULT.md:10`). PRE_REG does not define precedence; the chosen order is explicit.
2. The maker fill convention cannot change a verdict because the pass rules use the all-taker cost and section 3.7 says the maker readout cannot rescue a FAIL. It only changes a report-only readout.
3. The MDD definition can affect verdict eligibility in general because MDD is a pass condition. It does **not** change this verdict: T MDD 8.47% is below BH 67.80%, while T fails the sample-size, mean, and t-cost criteria; C MDD 214.21% exceeds BH (`RESULT.md:8-12`). The implementation follows the pre-registered cumulative-net drawdown comparison.

**DECISION (OURS):** PRE_REG does not specify percentile interpolation; the independent recount used NumPy's linear 80th-percentile interpolation, matching `np.nanpercentile(..., 80)` in `screen.py:116`. This choice does not alter the audit result because the counts match.

## Follow-up cards

None. The MED manifest guard is documented for a later implementation card; no HIGH finding was identified.
