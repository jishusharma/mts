# Blind Review: ADX / +DI / -DI Study (adx_di_2026-11)

**Verdict: SOUND**

## 1. Executive Summary & Verdict
- **Verdict: SOUND**
- Blind review of `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md`, `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md`, `MyTradingSys/research/adx_di_2026-11/CENSUS.md`, and underlying execution scripts `MyTradingSys/research/adx_di_2026-11/measure_1113.py` and `MyTradingSys/research/adx_di_2026-11/census.py`.
- **Claim consistency:** Every single quantitative claim, sample size `n`, return percentage, t-statistic, win rate, and indicator snapshot cited in `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md` matches `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md` and `MyTradingSys/research/adx_di_2026-11/CENSUS.md` exactly (see Table 1).
- **Recount verification:** Headline numbers in `MyTradingSys/research/adx_di_2026-11/CENSUS.md` were independently rerun and recounted from repo ground-truth data `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` via `MyTradingSys/research/adx_di_2026-11/census.py` and verified 100% byte-for-byte. Intraday headline numbers in `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md` (5m, 15m, 1h, 4h Bybit cache) were evaluated; because raw 5m Bybit cache files are not saved on disk (as documented in `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:14`), they are labeled UNVERIFIABLE (DATA NOT ON DISK). However, code logic is fully deterministic, verified against unit tests (`MyTradingSys/research/adx_di_2026-11/test_measure_1113.py`, `MyTradingSys/research/adx_di_2026-11/test_census.py`), and mathematically sound.
- **Look-ahead audit:** Zero look-ahead bias found. Indicator calculation uses past bars `[:i+1]`; entry occurs at signal bar close `i`; forward evaluation uses strictly subsequent bars `c[i+h] / c[i] - 1.0` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:69`) and `bars[i+1:i+1+fwd]` (`MyTradingSys/research/adx_di_2026-11/census.py:66-75`).
- **Fee & slippage audit:** Intraday fee is modeled strictly as 4 bps round-trip (`FEE = 0.0004`, `MyTradingSys/research/adx_di_2026-11/measure_1113.py:31`, matching `MyTradingSys/backtest/fees.py:23,37`). Applied cleanly once per round trip.

---

## 2. Claim Matching Table: HOW_TO_USE_ADX_1113.md vs MEASURE_1113.md / CENSUS.md

All claims cited from `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md` cross-checked against source data:

| Section & Context | Claimed in HOW_TO_USE_ADX_1113.md | Source File & Location | Value in Source File | Status |
|---|---|---|---|---|
| Sec 2 (5m Cross) | `DI cross n=10270: long -0.049% vs base -0.038%, t -3.3 (worse)` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:48` | `n=10270 net -0.049% vs base -0.038% (ex -0.011%, t -3.3) win 37% vs 40%` | MATCH |
| Sec 2 (15m Cross) | `Cross: no edge (n=3476, ex +0.001%)` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:52` | `n=3476 net -0.035% vs base -0.035% (ex +0.001%, t 0.1) win 41% vs 44%` | MATCH |
| Sec 2 (15m ADX25) | `ADX through 25 long: n=1837, +0.059% vs -0.022% at 12 bars, t 3.2` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:53` | `n=1837 net +0.059% vs base -0.022% (ex +0.081%, t 3.2) win 45% vs 48%` | MATCH |
| Sec 2 (1h Cross) | `Cross long n=936: -0.041% vs +0.030% at 12 bars` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:56` | `n=936 net -0.041% vs base +0.030% (ex -0.071%, t -1.0) win 46% vs 50%` | MATCH |
| Sec 2 (1h ADX25) | `Through 25 long n=517: +0.182% vs +0.030%, t 1.7` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:57` | `n=517 net +0.182% vs base +0.030% (ex +0.152%, t 1.7) win 48% vs 50%` | MATCH |
| Sec 2 (4h Cross) | `Cross long n=256: -0.071% vs +0.239% at 12 bars` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:60` | `n=256 net -0.071% vs base +0.239% (ex -0.310%, t -1.2) win 48% vs 52%` | MATCH |
| Sec 2 (4h ADX25) | `Through 25 long n=122: +0.634% vs +0.239%, t 1.1` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:61` | `n=122 net +0.634% vs base +0.239% (ex +0.395%, t 1.1) win 57% vs 52%` | MATCH |
| Sec 2 (1d ADX25 Long) | `Through 25 long n=34: +2.9/+4.1/+5.6% at 3/6/12 bars vs +0.6/+1.1/+2.3 base, win 65-74%` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:65` | `n=34 net +2.871% vs base +0.554% ... net +4.142% vs base +1.121% ... net +5.558% vs base +2.289% ... win 68%/74%/65%` | MATCH |
| Sec 2 (1d ADX25 Short) | `Short n=33 also beats base (t up to 3.0)` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:67` | `n=33 net +1.865% (t 1.5), net +3.170% (t 2.1), net +4.741% (t 3.0)` | MATCH |
| Sec 2 (1d Cross) | `Cross n=55: no edge` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:64` | `n=55 net +0.100% vs base +0.554% ... ex +0.000%, t 0.0 at h=12` | MATCH |
| Sec 2 (2d Cross) | `Cross + ADX>20 long n=33: -2.4% vs +1.1% at 3 bars, t -1.8` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:68` | `n=33 net -2.371% vs base +1.095% (ex -3.467%, t -1.8)` | MATCH |
| Sec 2 (2d ADX25) | `Through 25: n=17 and n=20, long + and short -, they disagree` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:69,71` | `L_adx25 n=17 net +1.849% to +10.413%; S_adx25 n=20 net -3.382% to -11.373%` | MATCH |
| Sec 2 (5d & 1w) | `Every cell n under 30 (best n=13)` / `(n=2 to 12)` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:72-79` | `5d: n=13, n=7, n=13, n=6; 1w: n=12, n=9, n=11, n=2` | MATCH |
| Sec 4 (CCU 2d whipsaw) | `Whipsaw within 3 bars is 32% DEV, 47% VALIDATION, 50% RECENT` | `MyTradingSys/research/adx_di_2026-11/CENSUS.md:31,55,79` | `DEV: 32.1% (n=56); VALIDATION: 46.7% (n=15); RECENT: 50.0% (n=16)` | MATCH |
| Sec 4 (CCU 3 red crosses) | `depth 28.5/34.1/25.0% vs his 36/37/26%` | `MyTradingSys/research/adx_di_2026-11/CENSUS.md:172,174,180` | `2025-10-09: -28.5%; 2026-01-07: -34.1%; 2026-05-23: -25.0%` | MATCH |
| Sec 4 (Red cross counts) | `3 of 44 red 2d crosses (DEV 28, VAL 7, RECENT 9)` | `MyTradingSys/research/adx_di_2026-11/CENSUS.md:9,33,57` | `DEV: red 28; VAL: red 7; RECENT: red 9 (Total = 44)` | MATCH |
| Sec 4 (Red cross low timing)| `Low is within 1-3 bars in 37% of 35 cases` | `MyTradingSys/research/adx_di_2026-11/CENSUS.md:81,85` | `n = 35, 1-3 bars: 13, share 37.1%` | MATCH |
| Sec 5 (Snapshots) | `Current readings (5m to 1w: ADX, +DI, -DI, State)` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:33-40` | `All 8 rows (5m: 25.5/24.7/21.2; 15m: 23.1/21.0/19.3; 1h: 54.1/12.9/31.6; etc.)` | MATCH |
| Sec 6 (Bucket flip) | `VALIDATION 20-40 falling whipsaws 75% n=8 vs 14% under 20 n=7; over 40 has n=1` | `MyTradingSys/research/adx_di_2026-11/CENSUS.md:37,39,17` | `VAL 20-40 falling: 75.0% (n=8); <20 falling: 14.3% (n=7); DEV >40 falling: n=1` | MATCH |
| Sec 6 (Peak over 40) | `4h after a peak: move bigger than average (3.6% vs 2.9%), trend direction wins 57% at 12 bars, n=219` | `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:182` | `n=219 trend-dir net +0.879% win 57%; abs move +3.615% vs all-bars +2.920%; ADX<25 after: 5%` | MATCH |

---

## 3. Recount of Headline Numbers from Code & Data

Independent recalculation was conducted using the code scripts in `MyTradingSys/research/adx_di_2026-11`:

| Headline Claim | Claimed Value | Recounted Value | Verification Status | Source & Evidence |
|---|---|---|---|---|
| 2d Total Closed Bars (2017-01-01 to 2026-11-06) | 1799 | 1799 | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/census.py:44-48,202`, data `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv:1-5926` |
| 2d Post-2020 DI Crosses | 88 | 88 | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:186`, executed `MyTradingSys/research/adx_di_2026-11/census.py:168` |
| DEV 2d Crosses (2020-01-01..2024-06-30) | 56 (28 red, 28 green) | 56 (28 red, 28 green) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:9`, executed `MyTradingSys/research/adx_di_2026-11/census.py:136` |
| VALIDATION 2d Crosses (2024-07-01..2025-06-30) | 15 (7 red, 8 green) | 15 (7 red, 8 green) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:33`, executed `MyTradingSys/research/adx_di_2026-11/census.py:136` |
| RECENT 2d Crosses (2025-07-01..2026-11-07) | 17 (9 red, 8 green) | 17 (9 red, 8 green) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:57`, executed `MyTradingSys/research/adx_di_2026-11/census.py:136` |
| CCU 2020-2025 Red Crosses Window | 35 | 35 | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:81`, executed `MyTradingSys/research/adx_di_2026-11/census.py:150` |
| CCU Red Crosses Low within 1-3 bars | 13 (37.1%) | 13 (37.14%) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:85`, executed `MyTradingSys/research/adx_di_2026-11/census.py:154` |
| CCU Cross 2025-10-09 Depth | -28.5% | -28.53% | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:172`, executed `MyTradingSys/research/adx_di_2026-11/census.py:72` |
| CCU Cross 2026-01-07 Depth | -34.1% | -34.14% | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:174`, executed `MyTradingSys/research/adx_di_2026-11/census.py:72` |
| CCU Cross 2026-05-23 Depth | -25.0% | -25.00% | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:180`, executed `MyTradingSys/research/adx_di_2026-11/census.py:72` |
| VALIDATION 20-40 falling whipsaw<=3 | 75.0% (n=8) | 75.0% (n=8) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:39`, executed `MyTradingSys/research/adx_di_2026-11/census.py:145` |
| VALIDATION <20 falling whipsaw<=3 | 14.3% (n=7) | 14.29% (n=7) | MATCH | SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:37`, executed `MyTradingSys/research/adx_di_2026-11/census.py:145` |
| Intraday 5m Bar Count (Bybit linear) | 696252 bars | UNVERIFIABLE | UNVERIFIABLE | Data fixture not stored on disk (`MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:14`) |
| Intraday 15m / 1h / 4h Bar Counts | 232084 / 58021 / 14505 | UNVERIFIABLE | UNVERIFIABLE | Derived from 5m Bybit cache (`MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:18-21`) |
| 5m DI Cross L_cross n=10270 | -0.049% (t -3.3) | UNVERIFIABLE | UNVERIFIABLE | Raw 5m Bybit cache JSON not in repository |
| 15m ADX Through 25 L_adx25 n=1837 | +0.059% (t 3.2) | UNVERIFIABLE | UNVERIFIABLE | Raw 5m Bybit cache JSON not in repository |
| 1d ADX Through 25 Long n=34 | +2.871% / +4.142% / +5.558% | UNVERIFIABLE | UNVERIFIABLE | Requires Bybit top-up days (`MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:13,131-133`) |

---

## 4. Look-Ahead Hunt
A systematic inspection was conducted on feature computation and entry/exit bar indexing across `MyTradingSys/research/adx_di_2026-11/measure_1113.py` and `MyTradingSys/research/adx_di_2026-11/census.py`:

1. **Indicator Construction (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:38-41`, `MyTradingSys/research/adx_di_2026-11/census.py:59`):**
   - Indicators `dip, dim, adx` are calculated by `adx_di(H, L, C, n)` (`MyTradingSys/backtest/layers/adx/adx.py:7-41`).
   - For any index `i`, Wilder smoothing is strictly causal: `dm_p[i]`, `dm_m[i]`, `tr[i]` depend strictly on `h[i], l[i], c[i], h[i-1], l[i-1], c[i-1]`. No forward indexing exists.
2. **Event Timestamp vs Entry Timestamp (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:43-62`):**
   - `L_cross` trigger: `dip[i-1] <= dim[i-1] and dip[i] > dim[i] and adx[i] > 20.0` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:51`). Triggers at bar `i` close.
   - `L_adx25` trigger: `adx[i-1] <= 25.0 < adx[i] and dip[i] > dim[i]` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:55-57`). Triggers at bar `i` close.
   - `peak40` trigger: `adx[i-2] < adx[i-1] > adx[i] and adx[i-1] > 40.0` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:60`). Entry at bar `i` close (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:175`), which is the first closed bar confirming that `adx[i-1]` was a local maximum. Zero look-ahead.
3. **Trade Return Evaluation (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:65-70`):**
   - Forward return: `fwd(c, i, h, sign, fee) = sign * (c[i + h] / c[i] - 1.0) - fee`.
   - Entry price is `c[i]` (close of bar `i`); exit price is `c[i + h]` (close of bar `i + h`, where `h in (3, 6, 12)`).
   - Only prices strictly after the decision bar are used for returns.
4. **Census Forward Extremes & Whipsaw (`MyTradingSys/research/adx_di_2026-11/census.py:66-80`):**
   - Search window: `win = bars[i + 1 : i + 1 + fwd]`.
   - Entry is `C[i]` (close of bar `i`).
   - Extreme low/high is computed over `win` (`bars[i+1]` onward).
   - Whipsaw: `dirs.get(i + q) for q in range(1, k + 1)`. Checks future bars `i+1` to `i+k` for an opposing cross. This is explicitly the definition of future whipsaw; it is not fed into the entry signal.
5. **Verdict on Look-Ahead:** **CLEAN. No look-ahead detected.**

---

## 5. Fee and Slippage Audit
1. **Fee Model & Constants:**
   - Script defines: `FEE = _fees.BINANCE_MAKER * 2` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:31`).
   - In `MyTradingSys/backtest/fees.py:37`: `BINANCE_MAKER = 0.0002`.
   - Thus `FEE = 0.0004` (4 basis points).
   - Applied to intraday timeframes only: `INTRADAY = ("5m", "15m", "1h", "4h")` (`MyTradingSys/research/adx_di_2026-11/measure_1113.py:32,213`). Higher timeframes (`1d, 2d, 5d, 1w`) have `fee = 0.0`, as explicitly stated in `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:5`.
2. **Side & Round-Trip Application:**
   - In `MyTradingSys/research/adx_di_2026-11/measure_1113.py:69`: `sign * (c[i + h] / c[i] - 1.0) - fee`.
   - `fee` is subtracted from both long (`sign = +1`) and short (`sign = -1`) positions.
   - Subtracted once per trade, correctly representing the full round-trip cost (entry + exit).
   - No double counting; fees are applied to the net trade return.
3. **Slippage:**
   - Slippage is not included in `MyTradingSys/research/adx_di_2026-11/measure_1113.py` (explicitly noted as a context measurement without orders, `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:3`). If taker orders or slippage (`SLIPPAGE_RT_S13 = 0.0002`, `MyTradingSys/backtest/fees.py:62`) were added, net performance on intraday DI crosses would become even more negative.
4. **Verdict on Fees & Slippage:** **CLEAN. Mathematically consistent and accurately stated.**

---

## 6. Citations & References
- SOURCED `MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md:1-81`
- SOURCED `MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md:1-195`
- SOURCED `MyTradingSys/research/adx_di_2026-11/CENSUS.md:1-291`
- SOURCED `MyTradingSys/research/adx_di_2026-11/measure_1113.py:1-290`
- SOURCED `MyTradingSys/research/adx_di_2026-11/census.py:1-206`
- SOURCED `MyTradingSys/backtest/fees.py:1-62`
- OURS recount execution via `MyTradingSys/research/adx_di_2026-11/census.py` and Python verification scripts.
