# Blind Read: `research/adx_di_2026-11/census.py` vs `CENSUS.md` and `FORMULAS.md` Section 30

- **Card**: `gemini-blind-read-of-adx-di-census-py`
- **Reader**: Gemini (`gemini-4-argon-medium`, blind read worker), 2026-11-07
- **Read order**: `MyTradingSys/research/adx_di_2026-11/census.py` (lines 1-206) read in full before opening `MyTradingSys/research/adx_di_2026-11/CENSUS.md` (lines 1-291), `MyTradingSys/backtest/layers/adx/adx.py` (lines 1-58), and `MyTradingSys/backtest/layers/FORMULAS.md` section 30 (lines 684-691).

---

## 1. Formula, Look-Ahead, As-Of, Forward Window, and Cross Definition Audit

1. **Wilder ADX/DI (`MyTradingSys/backtest/layers/adx/adx.py:7-41` vs `MyTradingSys/backtest/layers/FORMULAS.md:689-691`)**:
   - **True Range and Directional Movement (`adx.py:17-22`)**: For bar index `i >= 1` (stored at `k = i - 1` in `tr`, `pdm`, `mdm`), `tr` computes `max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))`, `up = high[i] - high[i - 1]`, `dn = low[i - 1] - low[i]`, `+DM = up if (up > dn and up > 0) else 0.0`, `-DM = dn if (dn > up and dn > 0) else 0.0`. Matches **SOURCED** `FORMULAS.md:689` (`"TR_i = max(H_i - L_i, |H_i - C_{i-1}|, |L_i - C_{i-1}|); up = H_i - H_{i-1}, dn = L_{i-1} - L_i; +DM_i = up if up > dn and up > 0 else 0; -DM_i = dn if dn > up and dn > 0 else 0"`).
   - **Wilder Smoothing & Seed (`adx.py:23-40`)**: Initial sums `s_tr, s_p, s_m = sum(tr[:n]), sum(pdm[:n]), sum(mdm[:n])` sum bars `1..n` (`n = 14`, **OURS** default / Wilder textbook), producing the first `DI+` and `DI-` at bar index `i = n = 14` (**OURS**). Subsequent bars `i > n` update `S_i = S_{i-1} - S_{i-1}/n + x_i` (`adx.py:27-29`). `DX` is collected from bar `n`; when `len(dx) == n` (bar `i = 2n - 1 = 27`, **OURS**), `adx[2n - 1] = sum(dx) / n` (`adx.py:37-38`), and for `i >= 2n`, `adx[i] = (adx[i - 1] * (n - 1) + dx[-1]) / n` (`adx.py:39-40`). Matches **SOURCED** `FORMULAS.md:689` (`"first defined at bar n ... ADX = mean of the first n DX (first defined at bar 2n-1), then ADX_i = (ADX_{i-1} * (n-1) + DX_i) / n"`) and passes the 20-bar `n = 3` (**OURS**) hand toy in `MyTradingSys/backtest/layers/adx/test_adx.py:15-28`.
2. **Cross Definition (`adx.py:44-58` vs `FORMULAS.md:689`)**:
   - `crosses(dip, dim)` computes `d = dip[i] - dim[i]` and sign `s = (d > 0) - (d < 0)` on each bar `i` where `dip[i] is not None`. When `s != 0`, it emits `(i, "green" if s > 0 else "red")` iff `prev != 0 and s != prev`, then updates `prev = s`. Zero differences (`dip[i] == dim[i]`) leave `prev` unchanged. Matches **SOURCED** `FORMULAS.md:689` (`"Cross: the sign of DI+ - DI- flips (strict, zeros ignored); red = DI- over DI+, green = DI+ over DI-"`).
3. **Signal Look-Ahead & As-Of Check (`census.py:54-81,110-120`)**:
   - **Signal bar (`census.py:59-68`)**: At cross bar index `i`, `dir = d`, `adx = adx[i]`, `slope = adx[i] - adx[i - 5]` (`SLOPE = 5`, **OURS**, `census.py:24`), and `close = C[i]` depend strictly on `bars[0..i]`. **Zero bars after `i` are read to trigger the cross, classify direction, assign ADX bucket (`<20`, `20-40`, `>40`, OURS, `census.py:84-87`), or compute the 5-bar ADX slope.**
   - **Forward window (`census.py:66-76`)**: `win = bars[i + 1:i + 1 + fwd]` (`FWD = 30`, **OURS**, `census.py:23`) starts strictly at bar `i + 1` (the bar after the cross bar) and spans at most `30` bars (`i + 1 .. i + 30`). It is used exclusively for ex-post outcome columns (`depth` and `bars_to`). When `len(win) < 30` (fewer than `30` forward bars exist after bar `i`), `depth` and `bars_to` remain `None` (`-` in `CENSUS.md`) and are excluded from `n_dp`.
   - **Whipsaw outcome columns (`census.py:77-79`)**: `ws1`, `ws2`, `ws3` inspect `dirs.get(i + q) not in (None, d) for q in range(1, k + 1)` (`k in (1, 2, 3)`, **OURS**), strictly after bar `i`.
   - **Cascade 1d -> 2d (`census.py:110-120`)**: Uses close timestamps `t1 = bars1d[r["i"]]["t"] + DAY_MS` (`census.py:113`) and `tc = bars2d[r["i"]]["t"] + 2 * DAY_MS` (`census.py:114`). Lead candidates filter `0 <= tc - t1 <= 20 * DAY_MS` (`20` days = `10` 2d bars, **OURS**, `census.py:117`), so a 1d cross must close at or before the 2d cross close (`t1 <= tc`) to count as leading. `max(cand) // DAY_MS` (`census.py:118`) selects the earliest same-direction 1d cross inside `[tc - 20d, tc]`, matching **SOURCED** `census.py:111` (`"lead in days of the first same-direction 1d cross whose close lies in the previous 10 2d bars (20 days)"`).

---

## 2. Count & Table Verification (`census.py` vs `CENSUS.md`)

All counts and cells were independently recomputed from `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv`:

- **Dataset & Resampling (`CENSUS.md:3`)**:
  - **SOURCED** `CENSUS.md:3`: `"btc_daily.csv (2017-01-01..2026-11-06, 3597 daily bars -> 1799 closed 2d bars), n = 14, indicator warm-up from 2017-01-01, crosses reported from 2020-01-01."`
  - **OURS** recompute: `3597` daily bars (`2017-01-01..2026-11-06`), `1799` closed 2d bars (`2016-12-31..2026-11-05` bucket start dates), `126` total 2d crosses (`88` from `2020-01-01`), `240` total 1d crosses (`165` from `2020-01-01`) -> **MATCH**.
- **Table (b) Bucket x Slope per Split (`CENSUS.md:9-79`)**:
  - **DEV (`2020-01-01..2024-06-30`, **OURS** `census.py:25`)**: **SOURCED** `CENSUS.md:9,31` reports `56 crosses (red 28, green 28)`, `all | all | all | 56 | 56 | 32.1% | 56 | 14.8% | 16.0`. **OURS** recompute: `n = 56` (`28` red, `28` green), `n_ws = 56`, `whipsaw<=3 = 18/56 = 32.14%`, `n_dp = 56`, `median abs depth = 14.75%` (`14.8%`), `median bars = 16.0`; all 19 rows match `CENSUS.md:13-31` -> **MATCH**.
  - **VALIDATION (`2024-07-01..2025-06-30`, **OURS** `census.py:26`)**: **SOURCED** `CENSUS.md:33,55` reports `15 crosses (red 7, green 8)`, `all | all | all | 15 | 15 | 46.7% | 15 | 17.3% | 9.0`. **OURS** recompute: `n = 15` (`7` red, `8` green), `whipsaw<=3 = 7/15 = 46.67%`, `median abs depth = 17.31%` (`17.3%`), `median bars = 9.0`; all 19 rows match `CENSUS.md:37-55` -> **MATCH**.
  - **RECENT (`2025-07-01..2026-11-07`, **OURS** `census.py:27-28`)**: **SOURCED** `CENSUS.md:57,79` reports `17 crosses (red 9, green 8)`, `all | all | all | 17 | 16 | 50.0% | 14 | 15.0% | 16.0`. **OURS** recompute: `n = 17` (`9` red, `8` green), `n_ws = 16` (`2026-11-05` has `nfwd = 0` so `ws3 = None`), `whipsaw<=3 = 8/16 = 50.0%`, `n_dp = 14` (last `3` crosses have `nfwd < 30`), `median abs depth = 14.99%` (`15.0%`), `median bars = 16.0`; all 19 rows match `CENSUS.md:61-79` -> **MATCH**.
- **CCU Check Table (`CENSUS.md:81-89`)**:
  - **SOURCED** `CENSUS.md:81-89`: `n = 35` red crosses in `2020-01-01..2025-06-30` with full 30-bar window; buckets `1-3: 13 (37.1%, -3.6%)`, `4-7: 7 (20.0%, -7.3%)`, `8-12: 3 (8.6%, -13.9%)`, `13-20: 5 (14.3%, -21.6%)`, `21-30: 7 (20.0%, -22.9%)`.
  - **OURS** recompute: `13 + 7 + 3 + 5 + 7 = 35`, shares and medians match to 0.1% -> **MATCH**.
- **Table (a) Every 2d Cross (`CENSUS.md:95-186`)**:
  - **SOURCED** `CENSUS.md:97-186`: `88` rows (`2020-01-05` through `2026-11-05`).
  - **OURS** recompute: all `88` rows match on `date`, `dir`, `ADX`, `slope5`, `bars to extreme`, `depth`, `nfwd`, `whip1`, `whip2`, `whip3` -> **MATCH**.
- **Table (c) Cascade 1d -> 2d (`CENSUS.md:188-289`)**:
  - **SOURCED** `CENSUS.md:192-194`:
    - `| DEV | 56 | 52 | 92.9% | 400.0% |`
    - `| VALIDATION | 15 | 12 | 80.0% | 850.0% |`
    - `| RECENT | 17 | 15 | 88.2% | 1300.0% |`
  - **OURS** recompute: counts (`52/56 = 92.9%`, `12/15 = 80.0%`, `15/17 = 88.2%`) and all `88` per-cross lead rows (`CENSUS.md:200-287`) match, **EXCEPT** the `median lead (days)` column in `CENSUS.md:192-194`: the true medians of `h` are `4.0`, `8.5`, and `13.0` days (**OURS**), which `census.py:177` formats as `400.0%`, `850.0%`, and `1300.0%` due to passing `1` to the `pct` argument of `fmt(v, pct=False, d=1)` (see Finding F1).
  - **SOURCED** `CENSUS.md:289`: `"1d crosses followed by a same-direction 2d cross within 5 2d bars (10 days): 74 of 165 (44.8%); red 41 of 83; green 33 of 82."` **OURS** recompute: `74 / 165 = 44.85%`, red `41 / 83`, green `33 / 82` -> **MATCH**.

---

## 3. Findings Table

| ID | Severity | File:Line | Evidence |
|---|---|---|---|
| F1 | MED | `MyTradingSys/research/adx_di_2026-11/census.py:100,177`<br>`MyTradingSys/research/adx_di_2026-11/CENSUS.md:192-194` | **Median lead (days) formatted as 100x percentage in Table (c).** `fmt(v, pct=False, d=1)` (`census.py:100`) takes `pct` as its second positional argument. At `census.py:177`, `fmt(statistics.median(h) if h else None, 1)` passes `1` to `pct` (truthy) instead of `d=1` (`fmt(..., False, 1)`). Consequently, **SOURCED** `CENSUS.md:192-194` prints `400.0%`, `850.0%`, and `1300.0%` in the `median lead (days)` column instead of the true values `4.0`, `8.5`, and `13.0` days (**OURS**). |
| F2 | LOW | `MyTradingSys/research/adx_di_2026-11/census.py:67,106,113-114,182`<br>`MyTradingSys/backtest/layers/timeframe/tf_resample.py:148` | **Open-date vs close-date convention across 2d Crosses and 1d Cascade.** `tf_resample.resample` stamps each 2d bar with `t = bucket_start_ms` (`tf_resample.py:148`, 00:00 UTC of day 1 of the 2-day bucket). `cross_rows` sets `row["date"] = date_of(bars[i]["t"])` (`census.py:67`, bucket open date), so a 2d cross on `2026-11-05` (**SOURCED** `CENSUS.md:184`) is only known at the close of `2026-11-06` (`t + 2 * DAY_MS`). Meanwhile `cascade` (`census.py:113-114`) shifts both 1d and 2d timestamps to close time (`t + DAY_MS` and `t + 2 * DAY_MS`), and `census.py:182` filters 1d crosses by `date_of(t) >= "2020-01-01"` (close date = open date + 1 day). Verified across all `126` 2d crosses and `240` 1d crosses (**OURS**) that `0` crosses fall on split-boundary dates (`2019-12-31`, `2024-06-30`, `2025-06-30`), so no split count shifts. |
| F3 | LOW | `MyTradingSys/research/adx_di_2026-11/census.py:29,36,46`<br>`MyTradingSys/research/adx_di_2026-11/TV_CROSSCHECK.md:4-6`<br>`MyTradingSys/research/adx_di_2026-11/CENSUS.md:3,184` | **Partial final daily bar in `btc_daily.csv` and 1-day warmup stub bucket.** Per **SOURCED** `TV_CROSSCHECK.md:4-6` and `FORMULAS.md:685`, `btc_daily.csv` row `2026-11-06` (`close = 75771.76`) was captured ~18:00Z before 00:00Z close; `to_2d` (`census.py:46`) stamps every daily row at `t + DAY_MS - 60000`, so `bars2d[-1]` (`2026-11-05..2026-11-06`, where the final red cross at `CENSUS.md:184` fires) is treated as closed. At the start of warmup, `WARMUP_START = "2017-01-01"` (`census.py:29`) excludes `2016-12-31`, making `bars2d[0]` (`2016-12-31`) a 1-bar bucket (`n_bars = 1`, **OURS**); recomputing from `2016-12-31` yields `0.0` max ADX difference on all post-2020 crosses (**OURS**). |
| F4 | LOW | `MyTradingSys/research/adx_di_2026-11/census.py:78-79,119,182-186`<br>`MyTradingSys/research/adx_di_2026-11/CENSUS.md:3,183,289` | **Whipsaw prefix censoring & uncensored 10-day tail in 1d follow-through.** (1) `census.py:78-79` sets `ws_k = True` whenever an opposite cross occurs in `1..k` even if `len(bars) - 1 - i < k` (e.g., `2026-11-03` has `nfwd = 1` and `whip1 = whip2 = whip3 = yes`, **SOURCED** `CENSUS.md:183`), which is logically sound for a cumulative `<= k` indicator (`hit` is already determined at `q = 1`) though `CENSUS.md:3` prose says `"cells need k bars after (n_ws)"`. (2) `fol` (`census.py:119,182-186`) does not exclude 1d crosses within 10 days of the dataset end; in this dataset the last 1d cross is `2026-10-22` (`15` days before `2026-11-06`, **OURS**), so `0` rows are right-censored. |

VERDICT: FIX-FIRST
