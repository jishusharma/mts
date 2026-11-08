# Argon Independent Check: Krown's "Lows Break -> ~10% More Down" Claim & Weekend Analyst Calls (2026-11-09)

**Card:** `gemini-argon-krown-lows-break-check-1109`
**Helper Script:** `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:1-326`
**Data Sources:** `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:1-5928` (`blockchain.info` `2010-08-18` to `2017-08-16` [OURS] + Binance `BTCUSDT` `1d` `2017-08-17` to `2026-11-06` [OURS], topped up through `2026-11-08` via `https://data-api.binance.vision/api/v3/klines` [OURS]).

---

## 1. Executive Summary & Playbook Verdict

1. **The Claim Under Test:** In the operator's weekend brief (`MyTradingSys/system/PLAN_5H_2026-11-08.md:14`, `"Krown target (lows break, ~10 % lower) | ~68k, 200-week SMA 67.8k"` [SOURCED]) and Krown's November downside map (`MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:12`, `"75,000 weekly close = line in the sand; 73,300 / 70,800 / 68,100 / 65,700 below; 81,900 reclaim ends the downtrend"` [SOURCED]; video IDs `M4mTHyPxMUM` / `e2-KjJdWbgM` [SOURCED]), Krown argues that breaking prior lows leads to roughly `10%` (`-10.6%` median in `e2-KjJdWbgM` [UNVERIFIED caption on NUC]) further downside toward `~68,000` USD (`200-week SMA` at `67,765.66` USD [OURS]).
2. **Independent Base Rate (Unconditional = Coin Flip):**
   - **Calendar Monthly Low Breaks (Krown's exact framing):** Across `189` calendar months (`2011-02` to `2026-10` [OURS]), `64` months (`33.9%` [OURS]) traded below the prior month's low. Of those `64` breaks, **`35 / 64` (`54.7%` [OURS])** reached `>= 10.0%` below the prior month's low before month-end (median drop `-12.01%` [OURS], `75th` percentile `-4.08%` [OURS], `25th` percentile `-20.82%` [OURS]). On `2011-05` to `2026-09` (`185` months [OURS]), **`63` breaks** occurred (`35 / 63 = 55.6%` reaching `>= 10%` down, median `-12.32%` [OURS]), reproducing Krown's `n = 63` sample count (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:294`). However, restricted to the **modern Binance spot era (`2017-09` to `2026-10`, `110` months [OURS])**, `40` months (`36.4%` [OURS]) broke the prior month's low and only **`18 / 40` (`45.0%` [OURS])** dropped `>= 10.0%` (or `>= 10.6%`) below the prior month's low, with a **median drop of `-8.43%` [OURS]**.
   - **Daily Rolling Swing-Low Breaks (`2017-08-17` to `2026-11-08`, `3,371` Binance `1d` bars [OURS]):** After a first break of the prior `20-day` low (`n = 144` [OURS]), price reaches `>= 10%` below the broken low within `7` days only **`31.2%` (`45 / 144` [OURS])** of the time (median `-5.20%` [OURS]), **`44.1%` (`63 / 143` [OURS])** within `14` days (median `-6.87%` [OURS]), and **`53.9%` (`76 / 141` [OURS])** within `30` days (median `-12.52%` [OURS]). For a `50-day` low break (`n = 67` [OURS], matching the `52-day` gap from `2026-09-15` low `74,967.97` to `2026-11-06` low `74,888.00` [OURS]), `>= 10%` downside occurs **`43.3%` (`29 / 67` [OURS])** in `7` days, **`49.3%` (`33 / 67` [OURS])** in `14` days, and **`52.2%` (`35 / 67` [OURS])** in `30` days.
3. **The Decisive Split — Sweep & Reclaim vs Daily Close Below the Low:**
   - Every definition shows a sharp regime split based on whether the break day **sweeps and closes back above** the prior low (`close > prior_low`, rejection) versus **closes below** the prior low (`close <= prior_low`, acceptance):
     - **Monthly Low Breaks (Binance Era, `n = 40` [OURS]):** Day-1 sweep + reclaim (`n = 22` [OURS]) produces a `>= 10%` monthly drop only **`36.4%` (`8 / 22` [OURS], median `-4.55%` [OURS])** of the time, whereas a Day-1 daily close below the prior month's low (`n = 18` [OURS]) produces a `>= 10%` drop **`55.6%` (`10 / 18` [OURS], median `-11.54%` [OURS])** of the time (`64.3%` / `-13.47%` median in full `2011-2026` history [OURS]).
     - **50-Day Rolling Low Breaks (`n = 67` [OURS]):** When the break candle sweeps and closes back above the `50-day` low (`n = 40` [OURS] — the exact pattern of `2026-11-06`, where `74,888.00` swept the `2026-09-15` low `74,967.97` by `$79.97` / `-0.11%` and closed at `75,844.00` [OURS]), a `>= 10%` drop follows in only **`32.5%` (`13 / 40`, median `-3.09%` [OURS]) over `7` days**, **`37.5%` (`15 / 40`, median `-4.02%` [OURS]) over `14` days**, and **`40.0%` (`16 / 40`, median `-6.11%` [OURS]) over `30` days**. Conversely, when the break day **closes below** the `50-day` low (`n = 27` [OURS]), a `>= 10%` drop follows in **`59.3%` (`16 / 27`, median `-11.79%` [OURS]) over `7` days**, **`66.7%` (`18 / 27`, median `-12.50%` [OURS]) over `14` days**, and **`70.4%` (`19 / 27`, median `-13.59%` [OURS]) over `30` days**.
     - **Confirmed Fractal Swing Lows (`k = 7` bars left/right, `n = 63` [OURS]):** Sweep + reclaim (`n = 31` [OURS]) reaches `-10%` in **`19.4%` (`6 / 31`, median `-3.24%` [OURS]) over `7` days** and **`26.7%` (`8 / 30`, median `-5.17%` [OURS]) over `30` days**; a daily close below the fractal swing low (`n = 32` [OURS]) reaches `-10%` in **`56.2%` (`18 / 32`, median `-11.19%` [OURS]) over `7` days** and **`75.0%` (`24 / 32`, median `-15.36%` [OURS]) over `30` days**.
4. **Weighting for the Monday Playbook (`2026-11-09`):** Do **not** weight Krown's `-10%` (`~67.4k–68.2k` [OURS]) call as active from the `2026-11-06` wick (`74,888.00` [OURS]) alone. Conditioned on a sweep-and-reclaim, the `7-day` base rate for a `-10%` drop is only `16.0%–32.5%` (median `-3.09%` to `-4.20%` [OURS]). The high-probability (`59.3%–83.3%` over `7–30` days [OURS]) `-10%` downside cascade activates **only on a daily close below `74,888.00`–`74,967.97` [OURS]** (or weekly close below `75,000` [SOURCED]).

---

## 2. Current Market Reference Levels (`2026-11-08`)

Computed via `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:254-287` on `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5874-5928` + Binance `1d` klines through `2026-11-08`:

| Metric / Reference Level | Value (USD / %) | Date / Window | Provenance (`SOURCED` / `OURS`) |
|---|---|---|---|
| BTC 4h close at plan time (`18:15Z`) | `75,892` | `2026-11-08 18:15Z` | **SOURCED** — `MyTradingSys/system/PLAN_5H_2026-11-08.md:10` (`"BTC close 4h | 75,892"`) |
| BTC weekend range | `75,571 - 76,200` | `2026-11-07..08` | **SOURCED** — `MyTradingSys/system/PLAN_5H_2026-11-08.md:11` (`"Weekend range | 75,571 - 76,200"`) |
| BTC daily close (`2026-11-08` snapshot) | `75,888.00` | `2026-11-08` | **OURS** — `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:273` (`data-api.binance.vision` `BTCUSDT` `1d`) |
| October 2026 monthly low | `76,325.98` | `2026-10-30` | **OURS** — `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5920` (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:277`) |
| September 2026 swing low (`Sep-15`) | `74,967.97` (`74,961` Bybit) | `2026-09-15` | **OURS** (`MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5875`) & **SOURCED** (`MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:18`, `"Sep-15 low | 74,961 (74,968)"`) |
| November 2026 swing low (`Nov-6`) | `74,888.00` (`74,871` Bybit) | `2026-11-06` | **OURS** (`MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5927`) & **SOURCED** (`MyTradingSys/system/PLAN_5H_2026-11-08.md:12`, `"Last swing low | 74,888 (11-06)"`) |
| `Nov-6` sweep depth below `Sep-15` low | `-$79.97` (`-0.11%`) Binance (`-$90` / `-0.12%` Bybit) | `2026-11-06` | **OURS** (`74,888.00 - 74,967.97`) & **SOURCED** (`MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:20`, `"90 USD = 0.12 %"`) |
| `Nov-6` daily close (post-sweep reclaim) | `75,844.00` (live `1d`) / `75,771.76` (CSV) / `75,848` (Bybit) | `2026-11-06` | **OURS** (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:280`, `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5927`) & **SOURCED** (`MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:20`, `"daily close 11-06: 75,848"`) |
| `200-day SMA` | `73,228.74` (`73,242` on `11-06`) | `2026-11-08` | **OURS** (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:281`) & **SOURCED** (`MyTradingSys/research/mts_bible/BIBLE.md:60`, `"200d = 73,242"`) |
| `200-week SMA` | `67,765.66` (`67,765` on `11-06`) | `2026-11-08` | **OURS** (`MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:282`) & **SOURCED** (`MyTradingSys/research/mts_bible/BIBLE.md:60`, `"200w = 67,765"`) |
| `-10.0%` / `-10.6%` target from Oct low (`76,325.98`) | `68,693.38` / `68,235.43` | November 2026 | **OURS** — `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:285-286` |
| `-10.0%` / `-10.6%` target from Nov-6 low (`74,888.00`) | `67,399.20` / `66,949.87` | Forward from `74,888` | **OURS** — `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:283-284` |

---

## 3. Empirical Test of Krown's "Lows Break -> ~10% More Down" Claim

### 3A. Test 1 — Calendar Monthly Low Breaks (Krown's Monthly Framing)

In `e2-KjJdWbgM` (`2026-11-05`, cited in `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:12` [SOURCED]) and the weekend correlation call (`M4mTHyPxMUM` in `MyTradingSys/system/PLAN_5H_2026-11-08.md:14` [SOURCED]; also listed in the canonical playlist dump `MyTradingSys/research/krown_capture_2026-10-16/raw/pl/PLPEz1q0esi3gZBK5m4deI2WNH2V63qCZH.txt:11` [SOURCED]), the statistical claim is that when a calendar month trades below the prior calendar month's low (`n = 63` of `188` months since `2011` in Krown's table [UNVERIFIED caption on NUC]), the median extension below the prior month's low is `-10.6%` (`75th` percentile `-3.8%`, `25th` percentile `-22.2%` [UNVERIFIED caption on NUC]).

Running `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:89-158` (`python MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py --offline`) yields:

| Sample Window | Months Evaluated (`OURS`) | Months Breaking Prior Month Low (`OURS`) | Reached `>= 10.0%` Below Prior Low (`OURS`) | Reached `>= 10.6%` Below Prior Low (`OURS`) | `75th` Pctile (3 in 4 drop at least) (`OURS`) | Median Drop Below Prior Low (`OURS`) | `25th` Pctile (1 in 4 worst) (`OURS`) | Day-1 Sweep & Reclaim (`close > prior_low`): `>= 10%` Rate & Median (`OURS`) | Day-1 Close Below (`close <= prior_low`): `>= 10%` Rate & Median (`OURS`) |
|---|---|---|---|---|---|---|---|---|---|
| **Full History (`2011-02..2026-10`)** | `189` | `64` (`33.9%`) | `35 / 64` (`54.7%`) | `35 / 64` (`54.7%`) | `-4.08%` | `-12.01%` | `-20.82%` | `8 / 22` (`36.4%`), med `-4.55%` | `27 / 42` (`64.3%`), med `-13.47%` |
| **Krown `n=63` Window (`2011-05..2026-09`)** | `185` | `63` (`34.1%`) | `35 / 63` (`55.6%`) | `35 / 63` (`55.6%`) | `-4.05%` | `-12.32%` | `-20.87%` | `8 / 22` (`36.4%`), med `-4.55%` | `27 / 41` (`65.9%`), med `-13.59%` |
| **Binance Spot Era (`2017-09..2026-10`)** | `110` | `40` (`36.4%`) | **`18 / 40` (`45.0%`)** | **`18 / 40` (`45.0%`)** | `-3.86%` | **`-8.43%`** | `-20.08%` | **`8 / 22` (`36.4%`), med `-4.55%`** | **`10 / 18` (`55.6%`), med `-11.54%`** |

**Key Findings from Test 1 (`OURS`):**
1. **Early pre-2017 data inflates the median:** In `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:1-2556`, pre-`2017-08-17` rows come from `blockchain.info` daily close-only series (`high == low == close` [OURS]), so every pre-2017 monthly break is automatically a daily close below the prior month's low. In the **modern Binance true-OHLC era (`2017-09` to `2026-10`, `110` months [OURS])**, the unconditional share of monthly-low breaks that reach `-10%` is **`45.0%` (`18 / 40` [OURS])** and the median extension is **`-8.43%` [OURS]** (below the `10%` threshold).
2. **November 2026 Status (`OURS`):** October 2026's low was `76,325.98` (`2026-10-30`, `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5920` [OURS]). November 2026 first broke below `76,325.98` on `2026-11-05` (low `74,992.00`, close `75,585.65` in `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:5926` [OURS]) and dipped to `74,888.00` on `2026-11-06` (`-1.88%` below the October low [OURS]), which is still within the mildest quartile (`-3.86%` [OURS]) unless the `Sep-15` / `Nov-6` structural floor (`74,967.97` / `74,888.00` [OURS]) gives way on a daily/weekly closing basis.

---

### 3B. Test 2 — Daily Rolling N-Day Swing-Low First-Breaks (`2017-08-17` to `2026-11-08`, Binance `1d`)

Because the operator's prompt specifically cites current price `~75.9k` and the **`74,888` swing low** (`MyTradingSys/system/PLAN_5H_2026-11-08.md:12,14` [SOURCED]), we test all first-break events where daily low `L[t]` drops below the rolling `N`-day low `min(L[t-N .. t-1])` (given `L[t-1] >= min(L[t-N-1 .. t-2])`) across `3,371` Binance daily bars (`2017-08-17` to `2026-11-08` [OURS], `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:161-188`). Forward drawdown is measured from the broken `prior_low` over the next `F in {7, 14, 30}` calendar days (`OURS`):

| Lookback `N` (`OURS`) | Forward Window `F` (`OURS`) | Events `n` (`OURS`) | Unconditional `>= 10%` Drop (`OURS`) | Unconditional Median / Quartiles (`75th` / `50th` / `25th`) (`OURS`) | **Sweep & Reclaim (`close > prior_low`)**: `>= 10%` Rate & Median (`OURS`) | **Close Below (`close <= prior_low`)**: `>= 10%` Rate & Median (`OURS`) |
|---|---|---|---|---|---|---|
| **`14`-day low** | `7d` | `188` | `50 / 188` (**`26.6%`**) | `-2.68%` / **`-4.88%`** / `-10.22%` | `18 / 111` (**`16.2%`**), med **`-3.24%`** | `32 / 77` (**`41.6%`**), med **`-7.95%`** |
| **`14`-day low** | `14d` | `187` | `73 / 187` (**`39.0%`**) | `-3.48%` / **`-6.64%`** / `-13.68%` | `32 / 111` (**`28.8%`**), med **`-5.20%`** | `41 / 76` (**`53.9%`**), med **`-11.52%`** |
| **`14`-day low** | `30d` | `185` | `94 / 185` (**`50.8%`**) | `-4.45%` / **`-10.35%`** / `-20.30%` | `45 / 109` (**`41.3%`**), med **`-6.65%`** | `49 / 76` (**`64.5%`**), med **`-16.22%`** |
| **`20`-day low** | `7d` | `144` | `45 / 144` (**`31.2%`**) | `-2.73%` / **`-5.20%`** / `-11.81%` | `17 / 81` (**`21.0%`**), med **`-3.30%`** | `28 / 63` (**`44.4%`**), med **`-7.85%`** |
| **`20`-day low** | `14d` | `143` | `63 / 143` (**`44.1%`**) | `-3.56%` / **`-6.87%`** / `-15.36%` | `26 / 81` (**`32.1%`**), med **`-5.24%`** | `37 / 62` (**`59.7%`**), med **`-12.14%`** |
| **`20`-day low** | `30d` | `141` | `76 / 141` (**`53.9%`**) | `-4.43%` / **`-12.52%`** / `-21.00%` | `34 / 79` (**`43.0%`**), med **`-6.87%`** | `42 / 62` (**`67.7%`**), med **`-17.00%`** |
| **`30`-day low** | `7d` | `102` | `32 / 102` (**`31.4%`**) | `-2.44%` / **`-4.88%`** / `-11.85%` | `13 / 56` (**`23.2%`**), med **`-3.27%`** | `19 / 46` (**`41.3%`**), med **`-7.17%`** |
| **`30`-day low** | `14d` | `102` | `46 / 102` (**`45.1%`**) | `-3.41%` / **`-6.77%`** / `-15.72%` | `20 / 56` (**`35.7%`**), med **`-4.46%`** | `26 / 46` (**`56.5%`**), med **`-12.01%`** |
| **`30`-day low** | `30d` | `102` | `53 / 102` (**`52.0%`**) | `-4.29%` / **`-10.80%`** / `-21.02%` | `25 / 56` (**`44.6%`**), med **`-6.30%`** | `28 / 46` (**`60.9%`**), med **`-15.86%`** |
| **`50`-day low** | `7d` | `67` | `29 / 67` (**`43.3%`**) | `-2.27%` / **`-5.32%`** / `-13.50%` | **`13 / 40` (`32.5%`), med `-3.09%`** | **`16 / 27` (`59.3%`), med `-11.79%`** |
| **`50`-day low** | `14d` | `67` | `33 / 67` (**`49.3%`**) | `-3.06%` / **`-8.42%`** / `-16.92%` | **`15 / 40` (`37.5%`), med `-4.02%`** | **`18 / 27` (`66.7%`), med `-12.50%`** |
| **`50`-day low** | `30d` | `67` | `35 / 67` (**`52.2%`**) | `-4.06%` / **`-11.13%`** / `-22.40%` | **`16 / 40` (`40.0%`), med `-6.11%`** | **`19 / 27` (`70.4%`), med `-13.59%`** |

---

### 3C. Test 3 — Confirmed Fractal Swing-Low Breaks (`k in {5, 7, 10}` Days Left/Right, Binance `1d`)

To avoid overlapping rolling windows and test clean structural swing lows (`L[s]` strictly lower than `k` daily bars to the left and `<= k` daily bars to the right, `MyTradingSys/research/monday_open_2026-11-09/krown_lows_break_check.py:191-227`), we measure the first subsequent day `t > s + k` that breaks `L[s]` (`2017-08-17` to `2026-11-08` [OURS]):

| Fractal Order `k` (`OURS`) | Forward Window `F` (`OURS`) | Events `n` (`OURS`) | Unconditional `>= 10%` Drop (`OURS`) | Unconditional Median / Quartiles (`75th` / `50th` / `25th`) (`OURS`) | **Sweep & Reclaim (`close > swing_low`)**: `>= 10%` Rate & Median (`OURS`) | **Close Below (`close <= swing_low`)**: `>= 10%` Rate & Median (`OURS`) |
|---|---|---|---|---|---|---|
| **`k = 5` bars** | `7d` | `84` | `28 / 84` (**`33.3%`**) | `-2.73%` / **`-5.21%`** / `-11.61%` | `10 / 45` (**`22.2%`**), med **`-3.42%`** | `18 / 39` (**`46.2%`**), med **`-8.98%`** |
| **`k = 5` bars** | `14d` | `84` | `34 / 84` (**`40.5%`**) | `-3.59%` / **`-6.64%`** / `-14.37%` | `13 / 45` (**`28.9%`**), med **`-4.80%`** | `21 / 39` (**`53.8%`**), med **`-11.27%`** |
| **`k = 5` bars** | `30d` | `83` | `42 / 83` (**`50.6%`**) | `-4.43%` / **`-10.35%`** / `-19.99%` | `17 / 44` (**`38.6%`**), med **`-5.73%`** | `25 / 39` (**`64.1%`**), med **`-12.61%`** |
| **`k = 7` bars** | `7d` | `63` | `24 / 63` (**`38.1%`**) | `-2.76%` / **`-6.09%`** / `-12.61%` | **`6 / 31` (`19.4%`), med `-3.24%`** | **`18 / 32` (`56.2%`), med `-11.19%`** |
| **`k = 7` bars** | `14d` | `63` | `26 / 63` (**`41.3%`**) | `-3.65%` / **`-7.57%`** / `-14.32%` | **`7 / 31` (`22.6%`), med `-4.17%`** | **`19 / 32` (`59.4%`), med `-12.07%`** |
| **`k = 7` bars** | `30d` | `62` | `32 / 62` (**`51.6%`**) | `-4.43%` / **`-11.74%`** / `-21.13%` | **`8 / 30` (`26.7%`), med `-5.17%`** | **`24 / 32` (`75.0%`), med `-15.36%`** |
| **`k = 10` bars** | `7d` | `49` | `19 / 49` (**`38.8%`**) | `-3.07%` / **`-6.94%`** / `-13.50%` | **`4 / 25` (`16.0%`), med `-4.20%`** | **`15 / 24` (`62.5%`), med `-12.07%`** |
| **`k = 10` bars** | `14d` | `49` | `20 / 49` (**`40.8%`**) | `-3.80%` / **`-7.57%`** / `-16.92%` | **`4 / 25` (`16.0%`), med `-4.20%`** | **`16 / 24` (`66.7%`), med `-12.63%`** |
| **`k = 10` bars** | `30d` | `49` | `25 / 49` (**`51.0%`**) | `-4.67%` / **`-11.08%`** / `-22.40%` | **`5 / 25` (`20.0%`), med `-5.39%`** | **`20 / 24` (`83.3%`), med `-17.61%`** |

---

## 4. Other Analysts' Weekend / This-Week Calls for Monday (`2026-11-09`)

Per the card's `done_when` (`MyTradingSys/system/tasks/gemini-argon-krown-lows-break-check-1109.json:21` [SOURCED]), below are **6 other analysts' calls** from the `2026-11-03..2026-11-07` CBP store update (`MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:9-16` and `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:8-12` [SOURCED]). Because the canonical raw transcript files (`raw_transcripts_canonical/<VIDEO_ID>_raw.txt`) for the November 4–6 uploads reside on `JIS-NB` (`F:/CryptoScrapper`) and `JIS-NUC`'s YouTube caption guard (`scripts/dev/fetch_captions_timed.py --status`) is locked until `2026-11-09T01:54:07Z`, raw video caption verification is marked **`UNVERIFIED`** for each row below, while the repo CBP store text is verified against `CBP_ALT_UPDATE_2026-11-07.md` and `PLAN_ADX_DI_VOLUME_2026-11-07.md` via `scripts/dev/verify_extract_quotes.py`:

| # | Analyst | Video ID | Date | Directional Call | Key Levels (USD / %) (`SOURCED`) | Caption Quote Status (`verify_extract_quotes.py`) & Repo CBP Store Citation |
|---|---|---|---|---|---|---|
| 1 | **Michael Pizzino** | `WHH4qSfCCyM` | `2026-11-06` | **Conditional / Cautious:** Bullish relief only if `77,800–78,000` higher low forms; bearish to `71k–73k` (and `57k–58k` at risk) if `75,000` fails | `77,800` / `78,000` (higher low), `75,000` (weekly hold), `71,000–73,000` (next downside), `57,000–58,000` (macro lows) | **`UNVERIFIED`** (raw transcript `WHH4qSfCCyM_raw.txt` not on NUC). Repo store citation: `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:11` (`"still holding above its low from September 15"`, `"if the level of 75 thousand does not hold"`) and `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:12-13` (`"the line in the sand; below it, further decline"`). |
| 2 | **Benjamin Cowen** | `UNVERIFIED` (CBP row `2026-11-06`; prior: `MRBXsqgIGb8`) | `2026-11-06` | **Bearish below `74,900`:** Breakdown below `74,900` sends BTC straight to the lower range or `200-week SMA` | `74,900` (breakdown trigger), `67,800` (`200-week SMA` target; `67,765.66` [OURS]) | **`UNVERIFIED`** (raw transcript not on NUC). Repo store citation: `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:14` (`"straight to the lower range or the 200-week"`) and `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:21` (`"Cowen points at the 200-week"`). |
| 3 | **CCU (Steve)** | `AnAx1PanZm4` | `2026-11-05` | **Cautious / Whipsaw Watch:** `2-day` `ADX+DI` red cross on `11-04` crossed back within `24h` on `11-05`; wait for signal confirmation (`1–3 weeks` consolidation vs drop) | `1–3 weeks` consolidation; historical `2d` red-cross drops cited: `-36%` (`Oct 2025`), `-37%` (`Jan 2026`), `-26%` (`May 2026`) | **`UNVERIFIED`** (raw transcript `AnAx1PanZm4_raw.txt` not on NUC). Repo store citation: `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:10` (`"sellers are in control"`, `"1-3 weeks of consolidation"`, `"less than 24 hours later the lines crossed back"`, `"watch which signal will actually be confirmed"`). |
| 4 | **Qriptal (Habib)** | `UNVERIFIED` (CBP row `2026-11-05`) | `2026-11-05` | **Bullish at Support:** Expects `72,000–73,200` to hold as the bear-market bottom; looking to long BTC there (and ETH `2,250–2,350`) | `72,000–73,200` BTC support / long zone; `2,250–2,350` ETH buy zone | **`UNVERIFIED`** (raw transcript not on NUC). Repo store citation: `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:15` (`"the support they expect to hold"`, `"the bottom of the bear market is here"`) and `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:22`. |
| 5 | **Jala** | `UNVERIFIED` (CBP row `2026-11-06`) | `2026-11-06` | **Neutral / Support Hold:** Expects the `72,000–73,200` support band (`200-day SMA` confluence at `73,228.74` [OURS]) to hold | `72,000–73,200` support zone | **`UNVERIFIED`** (raw transcript not on NUC). Repo store citation: `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:15` (`"the support they expect to hold"`). |
| 6 | **Jason Pizzino** | `UNVERIFIED` (CBP row `2026-11-04`; prior: `wA2bbv94A5k`) | `2026-11-04` | **Neutral / Support Hold:** Identifies `72,500` (`50%` retracement of the rise) inside the `72,000–73,200` support zone expected to hold | `72,500` (`50%` retracement level), `72,000–73,200` cluster | **`UNVERIFIED`** (raw transcript not on NUC). Repo store citation: `MyTradingSys/research/cbp/CBP_ALT_UPDATE_2026-11-07.md:15` (`"72.5k = 50 % of the rise"`). |

---

## 5. Synthesis: How Consensus Aligns with Our Empirical Evidence

1. **Two Distinct Downside Magnet Clusters (`SOURCED` + `OURS`):**
   - **Cluster A (`71,000–73,300` USD, `-3.4%` to `-6.4%` from `75,888` [OURS]):** Named by **Qriptal (`72,000–73,200` [SOURCED]), Jala (`72,000–73,200` [SOURCED]), Jason Pizzino (`72,500` [SOURCED]), Michael Pizzino (`71,000–73,000` [SOURCED]), and Krown's first target (`73,300` [SOURCED])**, and anchored by the **`200-day SMA` at `73,228.74` [OURS]**. In our empirical study (`Section 3B`), a sweep-and-reclaim of a `20–50` day swing low has a `30-day` median max drop of **`-6.11%` to `-6.87%` below the broken low (`74,968 * 0.9389 = 70,388` to `74,968 * 0.9313 = 69,818` [OURS])** and a `14-day` median drop of **`-4.02%` to `-5.24%` (`71,954` to `71,040` [OURS])** — placing Cluster A (`71,000–73,300`) squarely inside the normal post-sweep median excursion without requiring a full `-10%` breakdown.
   - **Cluster B (`65,700–68,200` USD, `-10.0%` to `-12.3%` below prior lows [OURS]):** Named by **Krown (`68,100` / `65,700` [SOURCED], `-10.6%` monthly-break median) and Benjamin Cowen (`67,800` `200-week SMA` [SOURCED]; `67,765.66` [OURS])**. Our backtest shows this cluster is **not** the base-case outcome after a reclaimed wick (`16.0%–32.5%` in `7d` [OURS]), but **becomes the `60%–83%` base-case outcome once a daily candle closes below `74,888.00–74,967.97` [OURS]**.
2. **Evidence-Based Decision Rule for Monday (`2026-11-09`, `OURS`):**
   - **Regime 1 — Sweep Holds (`1d close > 74,967.97` and `1w close >= 75,000`):** Treat `2026-11-06` (`74,888.00` [OURS]) as a completed liquidity sweep of `Sep-15` (`74,967.97` [OURS]), matching `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:22` (`"a sweep of the low, not a breakdown, until a daily close under 74,900"` [SOURCED]). Probability of `>= 10%` further downside (`<= 67,400` [OURS]) over the next `7` days is only **`19.4%–32.5%` [OURS]**.
   - **Regime 2 — Breakdown Confirmed (`1d close <= 74,888.00`):** Acceptance below the `Sep-15` / `Nov-6` floor shifts the historical `>= 10%` downside probability to **`56.2%–62.5%` within `7` days** and **`70.4%–83.3%` within `30` days** (median drop `-13.59%` to `-17.61%` [OURS]), activating Cluster A (`73,229` `200d SMA` [OURS]) immediately and Cluster B (`67,766` `200w SMA` / `67,399` `-10%` target [OURS]) as the primary magnet.
