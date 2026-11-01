# PRE_REG: Rumers Trading Rules Backtest on BTC DEV (2026-11-01, card rumers-testable-rules-dev-backtest)

- **Date:** 2026-11-01
- **Status:** FROZEN BEFORE FIRST RUN.
- **Data Source:** Binance BTCUSDT 1m klines (`Dumps/backtest/raw_1m_2022/BTCUSDT-1m-YYYY-MM.csv`, local, gitignored; sha256 recorded per month in runner output).
- **DEV Window:** `2022-04-01 00:00Z` .. `2024-06-30 23:59Z` (entries only; exits may run past the window).
- **Execution & Fees:** `BINANCE_TAKER * 2` from `backtest/fees.py` (0.10% round trip). Stress readout with `research_kit.TAKER_RT_PCT` (0.14%).
- **Same-bar Stop and Target:** Stop counted first (C26_PRE_REG convention).
- **Stats & Significance:** Per rule: $n$, win rate / hit-rate, mean net $R$, day-clustered SE (`research_kit.cluster_mean_se`), two-sided $p$-value (`norm_p_two`), Holm-Bonferroni correction over all $m$ rules (`research_kit.holm(p, m)`).
- **Look-Ahead Verification:** +1 bar shift and -1 bar shift run; look-ahead check must pass before reporting.

---

## 1. Frozen Testable Rules Specification

### Rule 1: `RUMERS-ORB-MANIP-REVERSAL` (Extract 1: T1, Videos: `6WfTIyJ-YzQ` R01-R06, `aTMFouI9mF4` R22-R25)
- **Quote:** `raw_transcripts_canonical/6WfTIyJ-YzQ_raw.txt` (R01, R03) -> `SOURCED`
- **Timeframe:** 15m opening range measurement; 5m execution -> `SOURCED`
- **Trigger:** First 15m candle of session (00:00 UTC or 13:30 UTC US open) has range $\ge 20\%$ of 14-day Daily ATR ("manipulation bar"). A subsequent 5m bar breaks the extreme of the John Wick hammer/pin reversal bar closing in opposite direction. -> `SOURCED` (threshold 20% `SOURCED` `T0H_jpQXdVI:R01`)
- **Direction:** Both Long and Short (reversion into range). -> `SOURCED`
- **Entry:** Next 1m bar open after 5m trigger close. -> `OURS`
- **Stop:** Absolute high/low of the manipulation candle / wick. -> `SOURCED`
- **Target / Exit:** 50% midpoint of the 15m opening candle range. -> `SOURCED`
- **Claimed by Video:** `NOT_IN_DATA`
- **0a Cost Check:** Expected median stop on 15m BTC manipulation bar is ~0.80% - 1.20%. Fee in R = $0.10 / 1.0\% = 0.10R \le 0.25R$ (PASSES cost floor).
- **0e Power:** Expected DEV $n \approx 300 - 600$ triggers across 27 months.

### Rule 2: `RUMERS-BOX-PDH-PDL-FADE` (Extract 1: T2, Video: `EoQDQVblmMY` R07-R11)
- **Quote:** `raw_transcripts_canonical/EoQDQVblmMY_raw.txt` (R07, R08, R09) -> `SOURCED`
- **Timeframe:** Daily reference levels; 5m execution -> `SOURCED`
- **Trigger:** Price pierces Previous Day High (PDH) or Previous Day Low (PDL) by $\ge 1$ tick and closes back inside the previous day range within the same 5m bar ("liquidity grab"). -> `SOURCED`
- **Direction:** Fade (Short at PDH sweep, Long at PDL sweep). -> `SOURCED`
- **Entry:** Next 1m bar open following 5m reclaim close. -> `OURS`
- **Stop:** Placed 2 ticks beyond the peak of the sweep wick. -> `SOURCED`
- **Target / Exit:** 50% midpoint of previous day range (Target 1) or opposite boundary (Target 2). -> `SOURCED`
- **Claimed by Video:** `NOT_IN_DATA`
- **0a Cost Check:** Expected median stop ~0.35% - 0.60%. Fee in R = $0.10 / 0.50\% = 0.20R \le 0.25R$ (PASSES cost floor).
- **0e Power:** Expected DEV $n \approx 400 - 800$ triggers.

### Rule 3: `RUMERS-VWAP-SEPARATOR-MEAN-REVERSION` (Extract 1: T3, Video: `kozesVBKkg4` R17-R20)
- **Quote:** `raw_transcripts_canonical/kozesVBKkg4_raw.txt` (R18, R19, R20) -> `SOURCED`
- **Timeframe:** Intraday 5m with Daily VWAP -> `SOURCED`
- **Trigger:** Price distance from Daily VWAP exceeds $1.5 \times$ 14-period 5m ATR (Separator threshold) AND 5m RSI(14) reaches $\ge 70$ (for short) or $\le 30$ (for long). -> `SOURCED`
- **Direction:** Mean reversion back to VWAP. -> `SOURCED`
- **Entry:** Close of 5m reversal candle returning toward VWAP. -> `OURS`
- **Stop:** Swing high/low of the divergence peak + 2 ticks. -> `SOURCED`
- **Target / Exit:** Touch of Daily VWAP. -> `SOURCED`
- **Claimed by Video:** `NOT_IN_DATA`
- **0a Cost Check:** Expected median stop ~0.50% - 0.90%. Fee in R = $0.10 / 0.70\% = 0.14R \le 0.25R$ (PASSES cost floor).
- **0e Power:** Expected DEV $n \approx 500 - 1200$ triggers.

### Rule 4: `RUMERS-ORR-25PCT-ATR-SWEEP` (Extract 3: Setup T2, Video: `4zazKDSXlh8` R06-R10)
- **Quote:** `raw_transcripts_canonical/4zazKDSXlh8_raw.txt` (R06, R07, R08, R09, R10) -> `SOURCED`
- **Timeframe:** Daily trend bias (50 SMA); 15m opening sweep filter; 5m execution -> `SOURCED`
- **Filter:** If Daily Close > 50 SMA, Longs only; if Daily Close < 50 SMA, Shorts only. -> `SOURCED` (`R06`)
- **Trigger:** First 15m candle of the session moves counter-trend with total range $\ge 25\%$ of 14-day Daily ATR. On 5m chart, price reverses and breaks extreme of the sweep reversal bar. -> `SOURCED` (`R07`, `R08`)
- **Direction:** Aligned with Daily 50 SMA (counter to the 15m sweep). -> `SOURCED`
- **Entry:** Next bar open upon 5m crossover. -> `SOURCED`
- **Stop:** Extreme low of the day (for Longs) or high of the day (for Shorts). -> `SOURCED` (`R09`)
- **Target / Exit:** Full re-consumption back to opening price of the 15m opening candle. -> `SOURCED` (`R10`)
- **Claimed by Video:** "Most of the trades, 80% or more... should be long or on the buy side" -> `SOURCED`
- **0a Cost Check:** Stop is at day extreme, typically 0.60% - 1.50%. Fee in R = $0.10 / 1.0\% = 0.10R \le 0.25R$ (PASSES cost floor).
- **0e Power:** Expected DEV $n \approx 150 - 350$ triggers.

### Rule 5: `RUMERS-MAGIC-LINE-PITCHFORK-REVERSAL` (Extract 3: Setup T1 & T5, Videos: `ferg8JGxSzk` R01-R05, `avCqX8ephOU` R21-R25)
- **Quote:** `raw_transcripts_canonical/ferg8JGxSzk_raw.txt` (R01, R03, R04), `avCqX8ephOU_raw.txt` (R21, R23, R24) -> `SOURCED`
- **Timeframe:** 1-Hour structural levels; 15m / 5m Pitchfork execution -> `SOURCED`
- **Levels:** Prior 1-Hour swing high and swing low (5-bar fractal). -> `OURS` (disambiguation)
- **Trigger:** Sucker move (2+ consecutive candles into the boundary line), followed by first reversal candle (green at support line, red at resistance line); enter when subsequent candle breaks confirmation candle extreme. -> `SOURCED`
- **Direction:** Boundary fade (Long at support, Short at resistance; no trades in middle 50% zone). -> `SOURCED`
- **Entry:** Next bar open on breakout of confirmation candle. -> `SOURCED`
- **Stop:** 2 ticks beyond the extreme of the confirmation candle / sucker wick. -> `SOURCED`
- **Target / Exit:** Opposite 1-Hour boundary line. Partial profit at 1.0R and trail stop to break-even. -> `SOURCED`
- **Claimed by Video:** `NOT_IN_DATA`
- **0a Cost Check:** Stop ~0.40% - 0.80%. Fee in R = $0.10 / 0.60\% = 0.17R \le 0.25R$ (PASSES cost floor).
- **0e Power:** Expected DEV $n \approx 250 - 500$ triggers.

---

## 2. Multi-Hypothesis Correction
- Total rules tested simultaneously: $m = 5$.
- Holm-Bonferroni critical $p$-thresholds ($\alpha = 0.05$):
  - Rank 1: $p_1 \le 0.05 / 5 = 0.0100$
  - Rank 2: $p_2 \le 0.05 / 4 = 0.0125$
  - Rank 3: $p_3 \le 0.05 / 3 = 0.0167$
  - Rank 4: $p_4 \le 0.05 / 2 = 0.0250$
  - Rank 5: $p_5 \le 0.05 / 1 = 0.0500$

---

## 3. Look-Ahead and Data Hygiene Gates
1. **Look-Ahead Shift Check:** Every rule will be executed with `shift = 0`, `shift = +1` (delayed by 1 bar), and `shift = -1` (look-ahead leak check). Shift +1 performance must degrade or maintain expected latency degradation without crashing; Shift -1 must be flagged if code attempts to use unclosed bars.
2. **One-Way Frozen Specification:** No threshold, parameter, stop distance, or exit rule may be altered after reviewing DEV PnL. Any redesign counts toward the maximum of 1 redesign per rule before permanent closure.
