# METHOD REVIEW: Screens Real Funding Fix (Commit 3d8722a93)

Task: `gemini-method-review-funding-screen-fix-1031`  
Lane: `CODEX`  
Reviewer: Gemini 3.8 Flash (independent cross-vendor method review)  
Reviewed Commit: `3d8722a937b9937dda738481738d995ed252e521`  
Date: 2026-10-31  

---

## 1. Executive Summary & Review Scope

Commit `3d8722a93` implemented real signed funding rate calculation for the screen studies (`gross_effect_screen_2026-10-15` and `chart_read_g5_2026-10-16`) by replacing the earlier flat 1 bp per settlement proxy with cumulative funding lookups using `bt_data.funding_cost_pct`.

This method review examines:
1. **Look-ahead risk**: Does the computation access future rates or unclosed bars?
2. **Selection effect**: Does the funding calculation filter or select trades retrospectively based on future outcomes?
3. **Missing costs / Realistic accounting**: Are all funding mechanics (intervals, boundaries, conventions) correctly charged?
4. **Sample size ($n$) considerations**: Are statistical claims supported by adequate sample size?
5. **Claims outrunning data**: Do commit messages, docstrings, or report summaries assert broader conclusions than the data support?

---

## 2. Itemized Methodological Findings

### F1. Funding Timestamp Millisecond Jitter Causes Settlement Boundary Misalignment (Look-Ahead / Boundary Window Issue)
- **Classification**: Boundary definition anomaly / Microsecond look-ahead or exclusion risk
- **File & Line**: `MyTradingSys/backtest/bt/bt_data.py:135-143` (SOURCED)
- **Evidence / Quote**:
  ```python
  def funding_cost_pct(funding, entry_ms, exit_ms, side):
      """Funding cost in % of notional: side x sum(rate of settlements s, entry < s <= exit). side +1 long pays a positive rate,
      side -1 short receives it. entry_ms / exit_ms / side broadcast as numpy arrays; funding = [(t_ms, rate)] sorted."""
      import numpy as np
      ts = np.array([x[0] for x in funding], np.int64)
      cum = np.concatenate(([0.0], np.cumsum([x[1] for x in funding])))
      a = np.searchsorted(ts, np.asarray(entry_ms, np.int64), side="right")
      b = np.searchsorted(ts, np.asarray(exit_ms, np.int64), side="right")
      return np.asarray(side) * (cum[b] - cum[a]) * 100.0
  ```
- **Context from Data**:
  As documented in `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T06_cost_fill_realism.md:59` (SOURCED):
  > "1,215 of the 2,736 are stamped 1 to 31 ms after the 00/08/16 boundary (424 of them within 5 ms; recounted 2026-10-26, the first version said '1 to 5 ms')."
- **Analysis**:
  The half-open interval is defined mathematically as `(entry_ms, exit_ms]`. If a trade opens at bar open exactly at an 8h settlement boundary (e.g. `entry_ms = 28,800,000` ms, 08:00:00.000 UTC), exchange settlement rules dictate that this newly entered position was NOT held across the 08:00:00 settlement; thus it should NOT be charged the 08:00 funding fee.
  However, because the archive's `calc_time` is jittered by +1 to +31 ms (e.g. `28,800,005`), `searchsorted(ts, entry_ms, side="right")` evaluates to index `0` instead of `1` (`28,800,000 < 28,800,005`).
  As a consequence, the settlement at `28,800,005` is considered to fall inside `(entry_ms, exit_ms]`, incorrectly charging a position opened at 08:00:00 with the 08:00 settlement.
  Conversely, a trade that exited at exactly 08:00:00.000 (`exit_ms = 28,800,000`) was held right up to the settlement boundary, but because `28,800,000 < 28,800,005`, `searchsorted` excludes the settlement from `b`, erroneously exempting it from funding.
- **Reproducing Input**:
  ```python
  import numpy as np
  import bt_data
  # Real-world scenario: settlement stamped at 08:00:00.005 UTC (28800005 ms)
  jittered_funding = [(28800005, 0.0001)]  # +1 bp rate
  # Trade enters at 08:00:00.000 (28800000 ms), exits at 08:05:00.000 (28800000 + 300000 ms)
  entry = 28800000
  exit = 29100000
  cost = bt_data.funding_cost_pct(jittered_funding, entry, exit, side=1)
  # Expected: 0.0 (trade entered at/after settlement)
  # Actual: 0.01 % (charged funding due to 5ms timestamp jitter)
  assert cost == 0.01  # Reproduces the boundary leakage
  ```

---

### F2. Silent Inversion and Synthetic Rebates on Reversed Time Windows (`entry_ms > exit_ms`)
- **Classification**: Missing sanity validation / Negative cost artifact
- **File & Line**: `MyTradingSys/backtest/bt/bt_data.py:141-143` (SOURCED)
- **Evidence / Quote**:
  ```python
  a = np.searchsorted(ts, np.asarray(entry_ms, np.int64), side="right")
  b = np.searchsorted(ts, np.asarray(exit_ms, np.int64), side="right")
  return np.asarray(side) * (cum[b] - cum[a]) * 100.0
  ```
- **Analysis**:
  The function performs no monotonic validation `exit_ms >= entry_ms`. If malformed trade data, negative delays, or negative horizons are passed such that `entry_ms > exit_ms`, `a > b`, resulting in `cum[b] - cum[a] < 0`. For a long position (`side = 1`), this inverts a positive funding payment into a funding credit (rebate).
- **Reproducing Input**:
  ```python
  import bt_data
  funding = [(1000, 0.0001), (2000, 0.0002)]
  # Entry 2000 ms, Exit 1000 ms (reversed timestamps)
  cost = bt_data.funding_cost_pct(funding, entry_ms=2000, exit_ms=1000, side=1)
  # Cost is negative (-0.02%), granting unearned profit to the trade
  assert cost < 0.0
  ```

---

### F3. Missing Deduplication of Funding Timestamp Settlements in `load_funding`
- **Classification**: Multiple settlement double-counting risk
- **File & Line**: `MyTradingSys/backtest/bt/bt_data.py:154-168` (SOURCED)
- **Evidence / Quote**:
  ```python
  rates = []
  for csv_file in sorted(dataset_path.glob("*.csv")):
      ...
      for row in reader:
          t = int(row[0])  # calc_time
          rate = float(row[2])
          rates.append((t, rate))
  rates.sort()
  return rates
  ```
- **Analysis**:
  `load_funding` glob-loads all CSV files and directly appends `(t, rate)` without deduplication on `t`. If monthly raw files overlap at boundaries or duplicate rows exist across archive dumps, duplicate records with the same `calc_time` are appended.
  In `funding_cost_pct`, `cum` is formed by `np.cumsum([x[1] for x in funding])`. Duplicate timestamps both get included in `cum[b] - cum[a]`, causing funding costs to be double- or multi-counted.
- **Reproducing Input**:
  ```python
  import numpy as np
  import bt_data
  # Two identical records for timestamp 1000 ms
  dup_funding = [(1000, 0.0001), (1000, 0.0001)]
  cost = bt_data.funding_cost_pct(dup_funding, entry_ms=500, exit_ms=1500, side=1)
  # Expected: 0.01 % (single settlement of 1 bp)
  # Actual: 0.02 % (double counted)
  assert np.isclose(cost, 0.02)
  ```

---

### F4. Small $n$ Power Limitation in Arm T ($n=40$) and Claims of Invariance
- **Classification**: Small sample size ($n$) vs claims of verdict stability
- **File & Line**: `MyTradingSys/research/gross_effect_screen_2026-10-15/FUNDING_RERUN.md:10-16` (SOURCED)
- **Evidence / Quote**:
  ```markdown
  Primary cell (d=1, h=60), mean G after funding, % per encounter (before the 0.14 % trading cost):

  | arm | n | old flat 1 bp | real funding | move (pp) |
  |---|---|---|---|---|
  | T | 40 | -0.05678 | -0.05610 | +0.00067 |
  | notF | 1399 | -0.00674 | -0.00548 | +0.00126 |
  | C | 1439 | -0.00813 | -0.00688 | +0.00125 |

  Verdict INCONCLUSIVE before and after: no flip. Largest arm move +0.0013 pp; largest single-cell funding difference 0.129 %.
  ```
- **Analysis**:
  The pre-registration `PRE_REG.md:77` (SOURCED) specifies `N_min = 200` encounters for test arm T. Realized `n_T = 40` (SOURCED: `RESULT.md:8`), meaning arm T was already severely underpowered and mechanically forced into `INCONCLUSIVE` (as `n_T < 200` triggers `INCONCLUSIVE` per `PRE_REG.md:80`).
  While `FUNDING_RERUN.md:16` accurately states "Verdict INCONCLUSIVE before and after: no flip", this "invariance" is primarily an algebraic property of $n_T = 40 < 200$ rather than the economic insignificance of real funding. In fact, on secondary cells (as noted in `T06_cost_fill_realism.md:59`), funding differences can exceed $0.129\ \text{pp}$ and swing secondary cell means by up to $+0.018\ \text{pp}$.

---

### F5. Look-Ahead and Out-of-Sample Integrity Checks
- **Classification**: Look-ahead & Split enforcement
- **File & Line**: `MyTradingSys/research/gross_effect_screen_2026-10-15/screen.py:39-43` (SOURCED)
- **Status**: **NO ISSUE FOUND** for the split filter.
- **Verification**:
  `screen.py` passes `CUTOFF_MS = 1_719_792_000_000` (2024-07-01 00:00:00 UTC) to `bt_data.load_funding_strict(FUND_BASE, CUTOFF_MS)`.
  `load_funding_strict` enforces:
  `rates = [r for r in load_funding(d.parent) if end_ms is None or r[0] < end_ms]`
  This strictly prevents any VALIDATION or HOLDOUT funding rates from entering the screen calculation.

---

## 3. Scope of Unchecked Items & Limitations

During this review, the following could not be verified directly against the live environment:
1. **Live archive directory presence**: The local disk at `F:/MTS/Dumps/backtest` does not exist in this worktree environment (which is standard for isolated worker worktrees). The fail-closed behavior was independently tested and verified via mock folders in `test_funding_absent_fails_closed`.
2. **Exhaustive rate verification of the 2,736 live raw CSV rows**: Raw CSV dump rows could not be parsed live due to missing local dump data; numbers for settlement jitter (+1 to +31 ms) were sourced from prior verified audit reports (`T06_cost_fill_realism.md:59`).

---

## 4. Summary of Review Recommendations

1. **Snap settlement timestamps to nominal boundary**: When loading funding rates or calculating settlement indices, snap timestamps within $[0, +60\text{s}]$ of nominal 8-hour intervals (`00:00`, `08:00`, `16:00`) to the exact nominal boundary (e.g. `t - (t % 3600000)`) to avoid microsecond jitter misallocating trades entered or exited at the boundary.
2. **Add monotonic check**: Ensure `bt_data.funding_cost_pct` asserts `np.all(exit_ms >= entry_ms)` to avoid synthetic negative cost rebates.
3. **Deduplicate funding rates**: Ensure `load_funding` uses a dictionary or deduplicates rates on timestamp before returning.

Noticed: The test suites `test_bt_data.py`, `test_screen.py`, and `test_common.py` all pass cleanly with no modifications required.
