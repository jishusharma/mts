# PRE-REGISTRATION: C30 WaveTrend bottom buy + bullish RSI divergence, BTCUSDT, VALIDATION read (frozen 2026-10-31)

Study id `eagle_c30_prereg`. Written BEFORE any bar on or after 2024-07-01 is read for this rule. The commit that adds this file
precedes the commit of any VALIDATION result. Promotion path: `MyTradingSys/system/PROMOTION_PIPELINE.md` (stage 2, pre-registered screen).
Operator ask (10-31): "I hope that these things are being recorded, and what is next in the pipeline is understood".

## 0. Where the lead came from (DEV only, 2022-01-01..2024-06-30)
- Code: `wt_rsi_div.py` (git 7fb60b44f), using `wavetrend_dots.py`, `wt_context.py`, `wt_lower_tf.py`. Data: Binance spot BTCUSDT 5m klines (public), built into 30m/15m.
- Search size: C30 ran 256 cells (4 signals x 3 trend sources x 4 exits x 6 charts, minus the 2h-trend source on 2h/4h). Before it, C27-C29
  searched WaveTrend dots on the same DEV window. Every DEV number is in-sample and selected; that is why this read exists.
- DEV numbers of the two frozen hypotheses (fee-net, per trade):

| Id | Chart | Rule | Exit | n | Win | Mean | SD | 95 % CI low |
|---|---|---|---|---|---|---|---|---|
| H1 | 30m | buy dot with wt1 <= -53 AND bullish RSI divergence, any trend | X1 centre cross | 88 | 80 % | +0.346 % | 2.34 | -0.143 % |
| H2 | 15m | same signal, only when the last CLOSED 2h bar's structure is up | X1 centre cross | 44 | 75 % | +0.261 % | 0.62 | +0.077 % |

H1 already fails the pipeline bar (CI low > 0) on DEV: a few large losers sit behind the 80 % win rate. It stays as a hypothesis because it was
the headline lead; H2 is its cleaner form. No other cell is tested on VALIDATION.

## 1. Frozen rule (every parameter; changing any = a new pre-reg)
| Item | Value | Label |
|---|---|---|
| WaveTrend | hlc3; esa = EMA 10; d = EMA(abs(ap - esa), 10); ci = (ap - esa) / (0.015 d); wt1 = EMA(ci, 21); wt2 = SMA(wt1, 4) | SOURCED (LazyBear, wavetrend_2026-10-17/PARITY_CONTRACT.md) |
| Buy dot | wt1 crosses above wt2 on the bar's close (wt1[i] > wt2[i], wt1[i-1] <= wt2[i-1]) with wt1[i] <= -53 | SOURCED band, OURS level choice |
| RSI | 14, Wilder, on closes | SOURCED |
| Bullish divergence | p = lowest low of bars i-40..i-8, q = lowest low of bars i-7..i; L[q] < L[p], RSI[q] > RSI[p], RSI[p] <= 40 | OURS |
| 2h trend (H2) | swing structure W=5 on 2h bars (`wt_context.structure`), value of the last 2h bar closed by the 15m bar's close | OURS |
| Entry | open of bar i+1 | OURS |
| Exit X1 | first bar k > i with wt1[k] > 0, filled at open of k+1; cap 60 bars; H2 also exits if the 2h trend turns down | OURS |
| One trade at a time | a new signal is ignored while a trade is open | OURS |
| Fee | BINANCE_TAKER x 2 (`MyTradingSys/backtest/fees.py`), no funding (holds are hours; funding disclosed as a gap) | SOURCED constant |

## 2. Read and verdict
- Window: VALIDATION 2024-07-01..2025-06-30 (the standard split, gross_effect_screen_2026-10-15/PRE_REG.md:92), read ONCE by card
  `c30-validation-read`, with warm-up bars taken from before 2024-07-01. HOLDOUT 2025-07-01..2026-09-30 stays sealed (opening it needs the operator).
- Data check first (`bt_preflight.py` P1/P2/P2b/P6/P7/P8 on the VALIDATION bars); a failed check = no verdict, fix, then read.
- Per hypothesis, fee-net per-trade mean, SD, n, 95 % CI (normal, mean +/- 1.96 SE), win rate, worst trade, both half-years.
- **PASS (per hypothesis):** n >= 15 AND mean > 0 AND Holm-adjusted (m = 2) one-sided p < 0.05 (t-test on per-trade net).
- **FAIL:** mean <= 0. **INCONCLUSIVE:** anything else (most likely outcome; see power).
- Power, stated now: expected n is about 35 (H1) and 18 (H2) in one year. If the true mean equals the DEV mean, the chance of PASS is
  roughly 15 % (H1) and 45 % (H2) (normal approximation, first Holm step at 0.025). An INCONCLUSIVE does not reopen DEV tuning.

## 3. What each verdict does next
- PASS: write a promotion manifest and run `promote.py check` (it also needs a backtest report with the BT-TUNED label and fee-net OOS
  CI low > 0, n >= 30). One year of VALIDATION cannot give n >= 30 for H2; the backtest gate therefore needs the HOLDOUT read, which is
  the operator's call. A passing setup then goes to `shadow` (logged, never trades), then `testnet` only with a sized flag (live-path rules).
- FAIL or INCONCLUSIVE: the card on the simulator and BACKTEST_CANDIDATES C30 record the verdict; the rule is not re-tuned on VALIDATION.
- Real money is never a stage here (GO_LIVE_BAR.md).

## 4. Known weaknesses (disclosed now)
1. Selected from about 256 cells plus C27-C29; the DEV numbers are optimistic by construction.
2. Spot klines, not perp; no funding; taker fees both sides; fills at the next open, no slippage.
3. H1's DEV mean rests on a fat-tailed distribution (SD 2.34 vs mean 0.35).
