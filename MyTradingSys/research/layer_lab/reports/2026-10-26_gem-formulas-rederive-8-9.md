# Lab Report: Re-derivation of FORMULAS.md Sections 8–9 (2026-10-28)

**Task**: `gem-formulas-rederive-8-9`  
**Card Title**: `[GEMINI] Re-derive FORMULAS.md sections 8-9 (UTC bucket anchoring, R targets) by hand`  
**Producer**: Claude (`FORMULAS.md:151-178`, `MyTradingSys/backtest/layers/timeframe/tf_resample.py`, `MyTradingSys/backtest/layers/cryptocred/cc_setups.py`)  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/backtest/layers/FORMULAS.md` (lines 151–178)
- `MyTradingSys/backtest/layers/timeframe/tf_resample.py`
- `MyTradingSys/backtest/layers/timeframe/registry.json`
- `MyTradingSys/backtest/layers/cryptocred/cc_setups.py` (lines 22–31)

*Constraint adherence*: `test_tf_resample.py` and `TEST_PLAN.md` were NOT read, inspected, or imported.

---

## 1. Specification and Scope

### Section 8: Resample / OHLCV aggregation + bucket anchoring (`FORMULAS.md:151-162`)
- **Bucket Math**: Plain UTC calendar/epoch arithmetic:
  - Seconds/hours: `(sec // seconds) * seconds`
  - Days: epoch-day-mod-N anchored to `1970-01-01`
  - Week: Monday-anchored ISO week via `epoch_day % 7 == 4` (1970-01-01 was Thursday, day 4 modulo 7 is Monday)
  - Month: First of calendar month in UTC (`year, month, 1`)
- **Closed Bars Only**: A bucket is only emitted once `bucket_end <= last_bar_close_ms` (never partial trailing buckets).
- **OHLCV Aggregation**: `o` = first bar's open, `c` = last bar's close, `h` = max high, `l` = min low, `v` = sum of volumes.

### Section 9: CryptoCred R-target math (`FORMULAS.md:163-178`)
- **Formula**: `R-target = entry +/- target_r * |entry - stop|` in the trade's profit direction.
  - Long: `entry + target_r * (entry - stop)` where `entry > stop`.
  - Short: `entry - target_r * (stop - entry)` where `entry < stop`.

---

## 2. Independent Calculations and Re-Derivations

### Fixture Setup: 2-Week Hourly Series (336 Bars)
- **Period**: 2024-01-22 00:00:00 UTC (Monday, `epoch_day = 19744`, `19744 % 7 == 4`) through 2024-02-04 23:59:59 UTC (Sunday, 14 complete days = 336 hourly bars).
- Spans across the month boundary (Jan 31 -> Feb 1) to exercise `1M` calendar boundary rules.
- Deterministic synthetic OHLCV bars:
  - `t = 1705881600000 + i * 3600000` (ms)
  - `o = 100.0 + i * 0.5`, `h = o + 2.0`, `l = o - 1.0`, `c = o + 1.0`, `v = 100 + (i % 24) * 10`
- An equivalent 20,160 1-minute bar series was constructed with exact minute-level OHLCV touchpoints mapping to the hourly boundaries.

### Resampling and Bucket Anchoring Comparisons

| Timeframe | Expected Buckets | Emitted Buckets (1m series) | Max Diff Open | Max Diff High | Max Diff Low | Max Diff Close | Max Diff Volume | Status |
|---|---|---|---|---|---|---|---|---|
| **4h** | 84 | 84 | 0.0 | 0.0 | 0.0 | 0.0 | < 1e-11 | **MATCH** |
| **1d** | 14 | 14 | 0.0 | 0.0 | 0.0 | 0.0 | < 1e-11 | **MATCH** |
| **1w** | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | < 1e-11 | **MATCH** |
| **1M** | 1 (Jan 2024) | 1 (Jan 2024) | 0.0 | 0.0 | 0.0 | 0.0 | < 1e-11 | **MATCH** |

*Note on 1M*: January 2024 closed at `2024-02-01 00:00:00 UTC <= 2024-02-04 23:59:59 UTC` and was emitted. February 2024 closes at `2024-03-01 00:00:00 UTC > last_bar_close_ms`, so per the closed-bars-only rule, it was correctly suppressed.

### CryptoCred Section 9 R-Target Re-Derivations

Tested against `_r_target(entry, stop, side, target_r)` in [`cc_setups.py:22-31`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-formulas-rederive-8-9/MyTradingSys/backtest/layers/cryptocred/cc_setups.py#L22-L31):

| Case | Side | Entry | Stop | target_r | Formula Calculation | Function Output | Status |
|---|---|---|---|---|---|---|---|
| 1 | Long | 100.0 | 95.0 | 1.0 | `100.0 + 1.0 * 5.0 = 105.0` | 105.0 | **MATCH** (diff 0.0) |
| 2 | Long | 100.0 | 95.0 | 1.5 | `100.0 + 1.5 * 5.0 = 107.5` | 107.5 | **MATCH** (diff 0.0) |
| 3 | Long | 100.0 | 95.0 | 2.0 | `100.0 + 2.0 * 5.0 = 110.0` | 110.0 | **MATCH** (diff 0.0) |
| 4 | Long | 100.0 | 95.0 | 3.0 | `100.0 + 3.0 * 5.0 = 115.0` | 115.0 | **MATCH** (diff 0.0) |
| 5 | Short | 100.0 | 105.0 | 1.0 | `100.0 - 1.0 * 5.0 = 95.0` | 95.0 | **MATCH** (diff 0.0) |
| 6 | Short | 100.0 | 105.0 | 1.5 | `100.0 - 1.5 * 5.0 = 92.5` | 92.5 | **MATCH** (diff 0.0) |
| 7 | Short | 100.0 | 105.0 | 2.0 | `100.0 - 2.0 * 5.0 = 90.0` | 90.0 | **MATCH** (diff 0.0) |
| 8 | Short | 100.0 | 105.0 | 3.0 | `100.0 - 3.0 * 5.0 = 85.0` | 85.0 | **MATCH** (diff 0.0) |

Invalid stop checks:
- Long with `stop >= entry` (e.g. 100.0, 100.0) raises `ValueError("Invalid stop for side 'long'...")`.
- Short with `stop <= entry` (e.g. 100.0, 100.0) raises `ValueError("Invalid stop for side 'short'...")`.

---

## 3. Findings

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| LOW | [`tf_resample.py:112-117, 134-145`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-formulas-rederive-8-9/MyTradingSys/backtest/layers/timeframe/tf_resample.py#L112-L145) | `resample()` hardcodes a 1-minute bar assumption: `last_bar_close_ms = bars_1m[-1]["t"] + 60000` and calculates `n_expected` in minutes. When fed 1-hour bars directly, the final 4h, 1d, and 1w bucket is prematurely skipped as unclosed, and `gap_count` reports spurious minute gaps. | Feeding a 336-hour series directly emits 83 4h buckets (expected 84) and 1 1w bucket (expected 2). When fed equivalent 1m bars, all 84 4h and 2 1w buckets close cleanly with `gap_count=0`. | Keep `bars_1m` argument convention documented, or add an optional `bar_interval_ms=60000` parameter so higher timeframe inputs can be resampled directly. |
| None | [`cc_setups.py:22-31`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-formulas-rederive-8-9/MyTradingSys/backtest/layers/cryptocred/cc_setups.py#L22-L31) | None. R-target formula matches exact spec. | All 8 test cases matched with 0.0 diff. | None. |

---

## 4. Verdict

**Verdict: SOUND.**  
All formulas from FORMULAS.md sections 8 and 9 (UTC bucket start/end anchoring, Monday ISO week `% 7 == 4`, calendar month boundaries, OHLCV closed-bar aggregation, and directional R-target calculations) reproduce with exact precision (max diff 0.0 on price, < 1e-11 on volume due to float division). One LOW interface constraint on 1-minute input bar expectation in `tf_resample.py` is noted above.
