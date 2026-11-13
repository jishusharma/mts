# PRE_REG: hourly RSI extreme + confirming candle (slug edge-rsi-extreme-confirm-1113)

Written and committed BEFORE any outcome is computed. Only raw data download (fetch_bybit.py) has run.

## Hypothesis and rule
Operator rule, 2026-11-13 ~15:40Z (voice, SOURCED: operator): "Instead of buying blindly: know where the daily RSI is. Price falls, the hourly
RSI falls to around 10 (or below 15, below 20: find the range). If the NEXT hourly candle closes above the close of the previous candle, buy
there, stop below the low of that hourly candle, a comfortable distance away, maybe 1%, or better check the ATR at that time and see which
stop works best." Everything he left open (thresholds beyond "around 10", stops, exits, daily buckets, universe) is OURS.

Why this is not a repeat: RSI-DEEP-PRESTUDIES (0/150 DEV, 0/80 VAL confirmation rows) and RSI-DIV-MTF were BTC-only touch/divergence/confirmation-row
studies with their own confirmations; this tests his exact 2-candle template, cross-coin, with a daily-RSI context split and an ATR-stop comparison.

## Context
Regime: none as a gate, because the operator's rule is regime-agnostic; the daily RSI bucket below IS his context gate, and results are reported per bucket.
Phase: none, because no cycle-phase input is in his rule; the Regime mix line in RESULT reports the window composition (BTC close vs 200d SMA).
Session: none, because crypto trades 24h and his rule names no session; entry hour is not filtered.
Entry: confirming candle = the hourly candle after the setup candle closes above the setup candle's close; entry at the open of the bar after it.

## Data and definitions
- Bybit v5 public linear USDT klines, 1h and 1d, 10 coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, from listing (>= 2020-01-01) to now. Funding history from the same API.
- RSI: `rsi_core` (Wilder 14, MyTradingSys/backtest/layers/rsi/rsi_core.py), unchanged. ATR(14,1h): Wilder RMA of true range (SOURCED: Wilder 1978, n=14).
- Setup bar S: closed 1h bar with RSI1h(S close) <= T (long) or >= T (short). Confirm bar C = S+1: long if close(C) > close(S); short if close(C) < close(S).
  Entry at the open of bar E = S+2. Skip if the entry price is already beyond the stop.
- Daily bucket: RSI(14) of the last daily bar closed at or before the entry bar's open. Long buckets <30, 30-40, 40-50, >50 (his "know where the daily RSI is");
  short buckets mirrored >70, 60-70, 50-60, <50.
- Grid, long: T in {10, 15, 20, 25} (OURS; he said ~10, <15, <20) x 4 daily buckets x 4 stops x 3 exits = 192 cells.
  Grid, short (own family, mirror): T in {75, 80, 85, 90} (OURS) x 4 buckets x 4 stops x 3 exits = 192 cells. Family for BH = these 384 pooled-universe cells.
- Stops (R = |entry - stop|): (i) low(S) - 0.25 ATR; (ii) low(S) - 1.0 ATR; (iii) entry x (1 - 1%); (iv) low(S) x (1 - 1%). Short mirrored with high(S) and +.
  The 1%, 0.25 and 1.0 ATR values are OURS (his "maybe 1%" and "check the ATR").
- Exits (the stop is live in all three; a 24-bar hard cap applies to all, OURS): A) 2R target; B) 1h RSI crosses back above 50 (long) / below 50 (short) at a bar close;
  C) 24h time stop (close of the 24th bar from the entry bar).
- Intrabar: if stop and target are both inside one bar the stop is taken first (conservative). Gap through the stop fills at the open. Target fills at its price.
- One position per coin per cell at a time (a signal arriving while that cell holds a position in that coin is skipped; cells are simulated independently).
- Fees: `fees.BINANCE_TAKER` on both legs (10 bp round trip), no slippage term (reported as a limitation; stops are taker too). Funding: Bybit funding settled while held
  (entry open < settlement <= exit bar close), long pays the rate, short receives it.
- Splits by entry bar time: DEV 2020-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, RECENT 2025-07-01..now.

## Metric, tests, pass rule
- Primary metric: net R per trade = (direction x (exit/entry - 1) - 2 x taker - direction x funding) / (R/entry). Also reported: mean net %, win rate, MAE in R.
- Inference: day-clustered SE (research_kit.cluster_mean_se; all coins of one UTC day are one cluster); one-sided normal p for mean R > 0; 95% CI by cluster bootstrap over days (2000 draws).
  BH at 10% over the 384 cells, applied on the VALIDATION p-values (and shown on DEV p-values too).
- Placebo (isolates the RSI part): same coin, same daily bucket, same split, random 1h bars with only the confirm condition (next bar closes beyond the prior close) and
  no RSI condition, same stop/exit rules. For every observed trade one placebo trade is drawn from the matching (coin, bucket, split) pool, 1000 resamples;
  placebo p = share of resample means >= the observed mean. Placebo trades are not position-constrained.
- PASS (a cell): VALIDATION n >= 30, VALIDATION mean net R > 0 with bootstrap CI lower bound > 0, placebo p <= 0.05, BH-10% significant on VALIDATION, DEV mean > 0.
  ROBUST (first line of the report): PASS and RECENT n >= 30 with mean net R > 0 and CI lower bound > 0.
- n < 30 in a split: UNDERPOWERED, never "no edge". BTC alone and per-coin splits are descriptive (not in the BH family).
- Verdict: PASS if any cell is PASS, FAIL if none and the pooled cells are powered, UNDERPOWERED otherwise.
- Sibling RSI census tables are not needed: the thresholds T are fixed above before the data is read; no DEV-derived threshold is used.

## Planned report
RESULT.md with verdict, per-cell table for the best cells by DEV mean (win rate, mean R, MAE, n for DEV / VALIDATION / RECENT), a stop-variant comparison table, BTC alone, Regime mix line.
