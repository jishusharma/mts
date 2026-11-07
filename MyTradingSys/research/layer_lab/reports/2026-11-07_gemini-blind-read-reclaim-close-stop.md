# Gemini Blind Read Report: `reclaim_close_stop_2026-11/RESULT.md` vs `results_DEV.csv` (2026-11-07)

- **Card**: `gemini-blind-read-reclaim-close-stop-1107`
- **Audited Target**: `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md` [SOURCED: RESULT.md:1-19]
- **Folder Data & Code**:
  - `MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv` [SOURCED: results_DEV.csv:1-7]
  - `MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md` [SOURCED: PRE_REG.md:1-26]
  - `MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py` [SOURCED: reclaim.py:1-72]
  - `MyTradingSys/research/reclaim_close_stop_2026-11/run_reclaim.py` [SOURCED: run_reclaim.py:1-99]
  - `MyTradingSys/research/reclaim_close_stop_2026-11/test_reclaim.py` [SOURCED: test_reclaim.py:1-76]
- **Cross-Referenced External Files**:
  - `MyTradingSys/backtest/fees.py` [SOURCED: fees.py:36]
  - `MyTradingSys/research/tf_break_event_study_2026-10-30/RESULT.md` [SOURCED: tf_break_event_study_2026-10-30/RESULT.md:15]
- **Status**: `VERDICT: MATCH` (`FOUND=31 DIFF=0 NOT_IN_DATA=0`)

---

## 1. Blind Read & Independent Recomputation from `results_DEV.csv`

Before reading `RESULT.md`, we inspected `PRE_REG.md`, `reclaim.py`, `run_reclaim.py`, `test_reclaim.py`, and `results_DEV.csv` (without re-running the study).

### 1.1 Fee Constant & Net Return Formula Verification
- **Taker Fee**: `fees.BINANCE_TAKER = 0.0005` per side (`5 bps`), round trip `2 * 0.0005 = 0.0010` (`0.10 %`, regime A) [SOURCED: `MyTradingSys/backtest/fees.py:13,36`; `PRE_REG.md:15`; `reclaim.py:70`: `"net=g - 2 * fees.BINANCE_TAKER"`].
- **Independent Fee-Net Check (`net_pct == gross_pct - 0.1000` across all 6 rows of `results_DEV.csv`)**:
  - `4h all`: `0.3710 - 0.1000 = 0.2710 %` (OURS recomputed vs `0.2710` [SOURCED: `results_DEV.csv:2`]) -> exact `0.0000` diff.
  - `4h low`: `0.5268 - 0.1000 = 0.4268 %` (OURS recomputed vs `0.4268` [SOURCED: `results_DEV.csv:3`]) -> exact `0.0000` diff.
  - `4h high`: `0.1852 - 0.1000 = 0.0852 %` (OURS recomputed vs `0.0852` [SOURCED: `results_DEV.csv:4`]) -> exact `0.0000` diff.
  - `1D all`: `-1.0934 - 0.1000 = -1.1934 %` (OURS recomputed vs `-1.1934` [SOURCED: `results_DEV.csv:5`]) -> exact `0.0000` diff.
  - `1D low`: `-0.1185 - 0.1000 = -0.2185 %` (OURS recomputed vs `-0.2185` [SOURCED: `results_DEV.csv:6`]) -> exact `0.0000` diff.
  - `1D high`: `-1.7028 - 0.1000 = -1.8028 %` (OURS recomputed vs `-1.8028` [SOURCED: `results_DEV.csv:7`]) -> exact `0.0000` diff.

### 1.2 Pooled Additivity & Weighted-Mean Consistency (`low` + `high` -> `all`)
Because `results_DEV.csv` contains both pooled (`all`) and per-side (`low`, `high`) aggregates, we independently recompute every pooled `all` figure from the `low` and `high` rows:

1. **4h Pooled (`all`) from `4h low` (`n=62`) and `4h high` (`n=52`)** [SOURCED: `results_DEV.csv:2-4`]:
   - **Trade count `n`**: `62 + 52 = 114` (OURS recomputed) vs `114` (`results_DEV.csv:2`) -> exact match.
   - **Gross mean `%`**: `(62 * 0.5268 + 52 * 0.1852) / 114 = (32.6616 + 9.6304) / 114 = 42.2920 / 114 = 0.370982 %` -> rounds to `0.3710 %` at 4 d.p. and `0.371 %` at 3 d.p. (OURS recomputed vs `0.3710` in `results_DEV.csv:2` and `0.371` in `RESULT.md:9`).
   - **Fee-net mean `%`**: `(62 * 0.4268 + 52 * 0.0852) / 114 = (26.4616 + 4.4304) / 114 = 30.8920 / 114 = 0.270982 %` -> rounds to `0.2710 %` at 4 d.p. and `0.271 %` at 3 d.p. (OURS recomputed vs `0.2710` in `results_DEV.csv:2` and `0.271` in `RESULT.md:9`).
   - **Winning trades & `win_pct`**:
     - `4h low`: `62 * 0.419355 = 26.00001` -> exactly `26` wins (`26 / 62 = 41.935484 %`, rounds to `41.9355 %`).
     - `4h high`: `52 * 0.384615 = 19.99998` -> exactly `20` wins (`20 / 52 = 38.461538 %`, rounds to `38.4615 %`).
     - `4h all`: `(26 + 20) / 114 = 46 / 114 = 40.350877 %` -> rounds to `40.3509 %` at 4 d.p. and `40 %` in prose (OURS recomputed vs `40.3509` in `results_DEV.csv:2` and `40 %` in `RESULT.md:12`).
   - **Stop exits & `stop_share`**:
     - `4h low`: `62 * 0.4677 = 28.9974` -> `29` stop exits (`29 / 62 = 0.467742`, rounds to `0.4677`).
     - `4h high`: `52 * 0.5385 = 28.0020` -> `28` stop exits (`28 / 52 = 0.538462`, rounds to `0.5385`).
     - `4h all`: `(29 + 28) / 114 = 57 / 114 = 0.500000` (`50 %`) (OURS recomputed vs `0.5000` in `results_DEV.csv:2` and `50 %` in `RESULT.md:12`).
   - **Total hold bars & `mean_hold`**:
     - `4h low`: `62 * 4.0000 = 248` bars (`248 / 62 = 4.0000`).
     - `4h high`: `52 * 4.0769 = 211.9988` -> `212` bars (`212 / 52 = 4.076923`, rounds to `4.0769`).
     - `4h all`: `(248 + 212) / 114 = 460 / 114 = 4.035088` -> rounds to `4.0351` at 4 d.p. and `4.0` bars at 1 d.p. (OURS recomputed vs `4.0351` in `results_DEV.csv:2` and `4.0` in `RESULT.md:12`).
   - **Verdict**: `n = 114 >= 100`, week-block 95% CI `[-0.2534, 0.8054]` spans zero (`lo <= 0 <= hi`) -> `INCONCLUSIVE` [SOURCED: `run_reclaim.py:66-69`; `PRE_REG.md:21`].

2. **1D Pooled (`all`) from `1D low` (`n=5`) and `1D high` (`n=8`)** [SOURCED: `results_DEV.csv:5-7`]:
   - **Trade count `n`**: `5 + 8 = 13` (OURS recomputed) vs `13` (`results_DEV.csv:5`) -> exact match.
   - **Gross mean `%`**: `(5 * -0.1185 + 8 * -1.7028) / 13 = (-0.5925 - 13.6224) / 13 = -14.2149 / 13 = -1.093454 %` -> rounds to `-1.0934 %` (`results_DEV.csv:5`) and `-1.093 %` at 3 d.p. (`RESULT.md:10`).
   - **Fee-net mean `%`**: `(5 * -0.2185 + 8 * -1.8028) / 13 = (-1.0925 - 14.4224) / 13 = -15.5149 / 13 = -1.193454 %` -> rounds to `-1.1934 %` (`results_DEV.csv:5`) and `-1.193 %` at 3 d.p. (`RESULT.md:10`).
   - **Winning trades & `win_pct`**:
     - `1D low`: `5 * 0.4000 = 2` wins (`2 / 5 = 40.0000 %`).
     - `1D high`: `8 * 0.3750 = 3` wins (`3 / 8 = 37.5000 %`).
     - `1D all`: `(2 + 3) / 13 = 5 / 13 = 38.461538 %` -> rounds to `38.4615 %` (`results_DEV.csv:5`).
   - **Stop exits & `stop_share`**:
     - `1D low`: `5 * 0.4000 = 2` stop exits (`2 / 5 = 0.4000`).
     - `1D high`: `8 * 0.5000 = 4` stop exits (`4 / 8 = 0.5000`).
     - `1D all`: `(2 + 4) / 13 = 6 / 13 = 0.461538` -> rounds to `0.4615` (`results_DEV.csv:5`).
   - **Total hold bars & `mean_hold`**:
     - `1D low`: `5 * 4.0000 = 20` bars (`20 / 5 = 4.0000`).
     - `1D high`: `8 * 3.6250 = 29` bars (`29 / 8 = 3.6250`).
     - `1D all`: `(20 + 29) / 13 = 49 / 13 = 3.769231` -> rounds to `3.7692` (`results_DEV.csv:5`).
   - **CI & Verdict**:
     - `1D all`: `n = 13 >= 10` so `wk_ci` computes `[-3.8836, 1.4962]`, which rounds to `-3.884 .. 1.496`; since `n = 13 < 100`, verdict is `INCONCLUSIVE` [SOURCED: `run_reclaim.py:57,67`; `results_DEV.csv:5`].
     - `1D low` (`n=5 < 10`) and `1D high` (`n=8 < 10`): `wk_ci` returns `(np.nan, np.nan)` when `len(x) < 10` [SOURCED: `run_reclaim.py:57-58`], producing empty CSV cells `,,` in `results_DEV.csv:6-7` and `"no CI, n < 10"` in `RESULT.md:12`.

---

## 2. Per-Cell Diff Table: `RESULT.md` vs `results_DEV.csv` (and Folder Sources)

Every table cell and prose number in `RESULT.md` is compared below against `results_DEV.csv` and the study files (`run_reclaim.py` prints `r.round(3)` to stdout at `run_reclaim.py:95`, while saving 4-decimal floats `%.4f` to `results_DEV.csv` at `run_reclaim.py:94`).

| # | Section / Row in `RESULT.md` | Metric / Claim | `RESULT.md` Value & Citation | Raw Data / Recomputed Value & Source | Label | Diff (Rounded) | Status |
|---|---|---|---|---|---|---|---|
| 1 | Header / Setup (`L3`) | Round-trip taker fee | `0.10 %` [SOURCED: `RESULT.md:3`] | `2 * 0.0005 = 0.001 = 0.10 %` [SOURCED: `fees.py:36`, `PRE_REG.md:15`, `reclaim.py:70`] | SOURCED | `0.00` | MATCH |
| 2 | Table Row 1 (`4h all DEV`, `L9`) | `n` | `114` [SOURCED: `RESULT.md:9`] | `114` (`62 + 52`) [SOURCED: `results_DEV.csv:2`] | OURS | `0` | MATCH |
| 3 | Table Row 1 (`4h all DEV`, `L9`) | `gross %` | `0.371` [SOURCED: `RESULT.md:9`] | `0.3710` (rounds to `0.371`) [SOURCED: `results_DEV.csv:2`] | OURS | `0.000` (raw `-0.0000`) | MATCH |
| 4 | Table Row 1 (`4h all DEV`, `L9`) | `mean fee-net %` | `0.271` [SOURCED: `RESULT.md:9`] | `0.2710` (`0.3710 - 0.1000`, rounds to `0.271`) [SOURCED: `results_DEV.csv:2`] | OURS | `0.000` (raw `-0.0000`) | MATCH |
| 5 | Table Row 1 (`4h all DEV`, `L9`) | `week-block 95 % CI %` (lo) | `-0.253` [SOURCED: `RESULT.md:9`] | `-0.2534` (rounds to `-0.253`) [SOURCED: `results_DEV.csv:2`] | OURS | `0.000` (raw `+0.0004`) | MATCH |
| 6 | Table Row 1 (`4h all DEV`, `L9`) | `week-block 95 % CI %` (hi) | `0.805` [SOURCED: `RESULT.md:9`] | `0.8054` (rounds to `0.805`) [SOURCED: `results_DEV.csv:2`] | OURS | `0.000` (raw `-0.0004`) | MATCH |
| 7 | Table Row 1 (`4h all DEV`, `L9`) | `verdict` | `INCONCLUSIVE` [SOURCED: `RESULT.md:9`] | `INCONCLUSIVE` (CI spans 0) [SOURCED: `results_DEV.csv:2`] | OURS | `none` | MATCH |
| 8 | Table Row 2 (`1D all DEV`, `L10`) | `n` | `13` [SOURCED: `RESULT.md:10`] | `13` (`5 + 8`) [SOURCED: `results_DEV.csv:5`] | OURS | `0` | MATCH |
| 9 | Table Row 2 (`1D all DEV`, `L10`) | `gross %` | `-1.093` [SOURCED: `RESULT.md:10`] | `-1.0934` (rounds to `-1.093`) [SOURCED: `results_DEV.csv:5`] | OURS | `0.000` (raw `+0.0004`) | MATCH |
| 10 | Table Row 2 (`1D all DEV`, `L10`) | `mean fee-net %` | `-1.193` [SOURCED: `RESULT.md:10`] | `-1.1934` (`-1.0934 - 0.1000`, rounds to `-1.193`) [SOURCED: `results_DEV.csv:5`] | OURS | `0.000` (raw `+0.0004`) | MATCH |
| 11 | Table Row 2 (`1D all DEV`, `L10`) | `week-block 95 % CI %` (lo) | `-3.884` [SOURCED: `RESULT.md:10`] | `-3.8836` (rounds to `-3.884`) [SOURCED: `results_DEV.csv:5`] | OURS | `0.000` (raw `-0.0004`) | MATCH |
| 12 | Table Row 2 (`1D all DEV`, `L10`) | `week-block 95 % CI %` (hi) | `1.496` [SOURCED: `RESULT.md:10`] | `1.4962` (rounds to `1.496`) [SOURCED: `results_DEV.csv:5`] | OURS | `0.000` (raw `-0.0002`) | MATCH |
| 13 | Table Row 2 (`1D all DEV`, `L10`) | `verdict` | `INCONCLUSIVE (n < 100)` [SOURCED: `RESULT.md:10`] | `INCONCLUSIVE` (`13 < 100`) [SOURCED: `results_DEV.csv:5`, `PRE_REG.md:21`] | OURS | `none` | MATCH |
| 14 | Descriptive (`4h low`, `L12`) | `n` | `62` [SOURCED: `RESULT.md:12`] | `62` [SOURCED: `results_DEV.csv:3`] | OURS | `0` | MATCH |
| 15 | Descriptive (`4h low`, `L12`) | `net %` | `+0.427 %` [SOURCED: `RESULT.md:12`] | `0.4268` (`0.5268 - 0.1000`, rounds to `0.427`) [SOURCED: `results_DEV.csv:3`] | OURS | `0.000` (raw `+0.0002`) | MATCH |
| 16 | Descriptive (`4h low`, `L12`) | `CI lo` | `-0.251` [SOURCED: `RESULT.md:12`] | `-0.2506` (rounds to `-0.251`) [SOURCED: `results_DEV.csv:3`] | OURS | `0.000` (raw `-0.0004`) | MATCH |
| 17 | Descriptive (`4h low`, `L12`) | `CI hi` | `1.218` [SOURCED: `RESULT.md:12`] | `1.2180` (rounds to `1.218`) [SOURCED: `results_DEV.csv:3`] | OURS | `0.000` (raw `0.0000`) | MATCH |
| 18 | Descriptive (`4h high`, `L12`) | `n` | `52` [SOURCED: `RESULT.md:12`] | `52` [SOURCED: `results_DEV.csv:4`] | OURS | `0` | MATCH |
| 19 | Descriptive (`4h high`, `L12`) | `net %` | `+0.085 %` [SOURCED: `RESULT.md:12`] | `0.0852` (`0.1852 - 0.1000`, rounds to `0.085`) [SOURCED: `results_DEV.csv:4`] | OURS | `0.000` (raw `-0.0002`) | MATCH |
| 20 | Descriptive (`4h high`, `L12`) | `CI lo` | `-0.659` [SOURCED: `RESULT.md:12`] | `-0.6588` (rounds to `-0.659`) [SOURCED: `results_DEV.csv:4`] | OURS | `0.000` (raw `-0.0002`) | MATCH |
| 21 | Descriptive (`4h high`, `L12`) | `CI hi` | `0.811` [SOURCED: `RESULT.md:12`] | `0.8115` (`r.round(3)` in Python round-half-to-even -> `0.812`, truncated/rounded `0.811`) [SOURCED: `results_DEV.csv:4`] | OURS | `0.0005` (sub-ulp half-way `0.8115`) | MATCH |
| 22 | Descriptive (`1D low`, `L12`) | `n` & CI status | `n 5` (`no CI, n < 10`) [SOURCED: `RESULT.md:12`] | `n=5`, `ci_lo=NaN, ci_hi=NaN` (`len(x) < 10`) [SOURCED: `results_DEV.csv:6`, `run_reclaim.py:57`] | OURS | `0` | MATCH |
| 23 | Descriptive (`1D high`, `L12`) | `n` & CI status | `n 8` (`no CI, n < 10`) [SOURCED: `RESULT.md:12`] | `n=8`, `ci_lo=NaN, ci_hi=NaN` (`len(x) < 10`) [SOURCED: `results_DEV.csv:7`, `run_reclaim.py:57`] | OURS | `0` | MATCH |
| 24 | Descriptive (`4h all`, `L12`) | `stop_share` | `50 %` [SOURCED: `RESULT.md:12`] | `0.5000` (`57 / 114 = 50.00 %`) [SOURCED: `results_DEV.csv:2`] | OURS | `0.00 %` | MATCH |
| 25 | Descriptive (`4h all`, `L12`) | `mean_hold` | `4.0 bars` [SOURCED: `RESULT.md:12`] | `4.0351` (`460 / 114`, rounds to `4.0` at 1 d.p.) [SOURCED: `results_DEV.csv:2`] | OURS | `0.0` (raw `-0.0351`) | MATCH |
| 26 | Descriptive (`4h all`, `L12`) | `win_pct` | `40 %` [SOURCED: `RESULT.md:12`] | `40.3509 %` (`46 / 114`, rounds to `40 %` integer) [SOURCED: `results_DEV.csv:2`] | OURS | `0 %` (raw `-0.3509 %`) | MATCH |
| 27 | Comparison (`T058 fade-R`, `L14`) | `T058 4h fade R DEV` | `-0.417 % DEV, n 111, 4-bar hold` [SOURCED: `RESULT.md:14`] | `n=111, mean % = -0.417, 4-bar hold` [SOURCED: `tf_break_event_study_2026-10-30/RESULT.md:15,32`; `PRE_REG.md:23`] | OURS | `0` | MATCH |
| 28 | Comparison (`L14`) | Reclaim-close 4h DEV summary | `+0.27 % on 114 events` [SOURCED: `RESULT.md:14`] | `net_pct = 0.2710 %` (rounds to `+0.27 %`), `n = 114` [SOURCED: `results_DEV.csv:2`] | OURS | `0.00 %` (raw `-0.0010 %`) | MATCH |
| 29 | Comparison (`L14`) | Difference vs T058 | `about 0.7 points` [SOURCED: `RESULT.md:14`] | `0.2710 - (-0.417) = 0.6880` percentage points (rounds to `0.7` at 1 d.p.) | OURS | `0.0` (raw `+0.012`) | MATCH |
| 30 | Caveats (`L19`) | Warm-up start bar | `bar 30 of a one-month warm-up` [SOURCED: `RESULT.md:19`] | `for i in range(30, n - N - cap - 1):` and `DEV: ('2021-12', '2024-06')` [SOURCED: `reclaim.py:55`, `run_reclaim.py:23`] | OURS | `0` | MATCH |
| 31 | Caveats (`L19`) | 1D event count & DEV length | `13 events in 2.5 years` [SOURCED: `RESULT.md:19`] | `n = 13` (`results_DEV.csv:5`), `2022-01..2024-06` = 30 months = `2.5` years [SOURCED: `PRE_REG.md:18`] | OURS | `0` | MATCH |

### Note on Row #21 (`4h high` CI upper bound `0.811` vs `0.8115`)
In `results_DEV.csv:4`, `ci_hi` is stored at 4 decimal places as `0.8115` [SOURCED: `results_DEV.csv:4`]. Because the underlying float is on the `.8115` half-way boundary (e.g. `0.81149...` rounds to `0.8115` at 4 d.p. and `0.811` at 3 d.p.), `RESULT.md:12` reports `0.811`, which is within `0.0005` percentage points (half a tenth of a basis point) of `0.8115` and has zero effect on the descriptive reading or arm verdict.

---

## 3. Verdict

Every table cell, descriptive statistic, fee-net deduction, pooled weighted average, and cross-study comparison in `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md` is verified against `results_DEV.csv` and the folder scripts (`reclaim.py`, `run_reclaim.py`, `PRE_REG.md`).

VERDICT: MATCH
