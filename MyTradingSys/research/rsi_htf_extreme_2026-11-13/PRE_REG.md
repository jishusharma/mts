# PRE-REG: higher-timeframe RSI extreme, next candle closes above, stop = extreme low (edge4-rsi-htf-extreme-1113)

Written and committed before any trade outcome is computed. Only the BTC daily regime mix (a property of daily closes) was computed first.

## Hypothesis (operator rule, 2026-11-13)
RSI(14) on a closed 4h / 8h / 12h bar reaches an extreme; if the NEXT bar of that timeframe closes above the extreme bar's close, going long at that close with the stop at the extreme bar's low has positive fee-net expectancy, more so when the daily RSI is below 30. Seen on BTC alone: 4h RSI<=12 with daily RSI<30 reached 2-3R in 4 of 5 episodes (too few). This study pools 20 coins.

## Context
Regime/phase: counter-trend long entries in sold-off conditions (capitulation, mostly below the daily 200d SMA); no regime filter is applied, the daily RSI band is the only conditioner. Session: not filtered (TF bars cover all sessions). Entry: close of the confirming bar. Prior tests of this family: edge-rsi-extreme-confirm-1113 (0/384 PASS, fixed stops) and edge3-rsi-deep-extreme-grid-1113 (0/60 PASS, mostly UNDERPOWERED, 1h-12h on 10 coins). This study extends to 20 coins and drops the green-candle requirement (the operator's wording is only "closes above the extreme close").
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range): DEV bull 51 % / bear 40 % / range 10 %; VALIDATION bull 56 % / bear 30 % / range 15 %.

## Data and splits
Bybit v5 public linear klines (1h, 1D), 2020-01-01..now (from listing). Universe (20): BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM UNI TRX BCH ETC FIL XLM NEAR SAND; any that fail to fetch are dropped and named in RESULT. 4h/8h/12h folded from 1h, UTC epoch anchored (8h opens 00/08/16, 12h 00/12), incomplete groups dropped, still-forming bar dropped. RSI = Wilder 14 on TF closes; daily RSI = Wilder 14 on closed daily bars (last daily bar closed at or before the signal bar close).
Splits by ENTRY (confirm close) time: DEV 2020-01-01..2023-12-31, VALIDATION 2024-01-01..now.

## Rules (SOURCED = operator's words; OURS = our choice)
- Signal (SOURCED): TF RSI(14) <= T on a closed bar; T for 4h in {20, 15, 12}; for 8h and 12h in {25, 20, 15}. First touch per episode, re-arm only after RSI(TF) closes > 30 (OURS). Signal bar must be red (close < open; SOURCED "extreme (red) candle").
- Confirm (SOURCED): the next TF bar (contiguous) closes above the signal bar's close. Entry = that close. No confirm = no trade.
- Stop (SOURCED): low of the signal bar. Stop fill = min(stop, bar open); same-bar stop and target = stop first. Forward walk on 1h bars starting after the entry close (entry bar never read).
- Exits (SOURCED 1R/2R/3R and 10-bar time exit; caps OURS): +1R, +2R, +3R targets with a cap of 20 TF bars (exit at the close of the last hour of the cap if neither stop nor target hit); time exit = close of the 10th TF bar after entry. The stop is active in all exits.
- Costs: per side fees.BINANCE_TAKER (5 bp, above the brief's 4 bp, conservative) plus fees.SLIPPAGE_RT_S13 / 2 (1 bp) per side, both imported from MyTradingSys/backtest/fees.py; net R = (gross return - 2 x per-side cost) / stop distance. No funding (limitation).
- Trades need a full forward window (20 TF bars); the newest trades without one are dropped.

## Cells (40, fixed now)
A. Ungated pooled cells (36): TF/T combos (4h,20) (4h,15) (4h,12) (8h,25) (8h,20) (8h,15) (12h,25) (12h,20) (12h,15) x exits {tgt1R, tgt2R, tgt3R, time10} = 36.
B. Operator's gated cells (4): (4h, T=12) with daily RSI < 30 at signal x the same 4 exits.
Daily RSI bands {<30, 30-40, >40} are a descriptive split of each ungated cell (n and mean, no CI, not tested cells).
Primary metric: fee-net mean R per trade, pooled over coins. Also reported (not used for the verdict): per-day-cluster stats = trades dedupe by entry UTC day (all coins and signals in that cell on that day averaged into one observation), n days, mean, bootstrap CI over days; and the median R.

## Statistics
Per-trade bootstrap is week-block (ISO week of entry, all coins in a week share a block), 2000 resamples; CI = 2.5/97.5 percentiles; one-sided p = share of resampled means <= 0.
Placebo: 100 draws per cell; each real trade replaced by a random TF-bar close of the same coin in the same ISO week with the same stop distance and the same exit rule (same coin, same count). Placebo p = share of draw means >= the real mean, computed per split.
PASS (all): VALIDATION fee-net mean R > 0, bootstrap 95% CI lower bound > 0, VALIDATION n >= 30, placebo p <= 0.05, and Benjamini-Hochberg 10 % significant across the 40 VALIDATION p-values. Fewer than 30 VALIDATION trades = UNDERPOWERED. Verdicts: PASS / FAIL / UNDERPOWERED; no edge claim unless PASS.

## Limits stated now
No funding; R explodes when the signal bar range is tiny (fee / stop distance); 20 coins are highly correlated, so week blocks and the day-cluster view both matter; later listings have shorter history; daily-band splits are small-n; cells within a combo share trades (exits on the same entries), so BH over 40 is only approximately independent.
