# PRE-REG: power test of two thin RSI-extreme leads on NEW data (edge5-rsi-htf-power-1113)

Written and committed before any trade outcome is computed. Only descriptive BTC daily closes (regime mix) were looked at first.

## Hypothesis
Parent study (rsi_htf_extreme_2026-11-13, 20 Bybit perps since 2020): long when a 4h/8h/12h RSI(14) extreme red candle is followed by a candle closing above its close, stop = low of the extreme candle. No cell passed. Two leads were too thin to judge: (a) operator's rule 4h RSI<=12 with daily RSI<30 (24 signals, about +0.6R at 2R, same sign DEV and VALIDATION, CI across zero); (b) 12h RSI<=20 (VALIDATION +0.5R, n 47 on 15 days, DEV about -0.17R). This study re-tests the same rules, unchanged, only on data the parent never used.

## Context
Regime/phase: counter-trend long entries in sold-off conditions (capitulation); no regime filter, the daily RSI<30 gate is the only conditioner on cells 1-2. Session: not filtered. Entry: close of the confirming TF bar. Prior tests of this family: edge-rsi-extreme-confirm-1113 (0/384 PASS), edge3-rsi-deep-extreme-grid-1113 (0/60), edge4 parent (0/40, two leads). Regime split is reported, not conditioned on.
Regime mix: BTC daily close vs 200d SMA (bull = close above, bear = at or below), all BTCUSDT spot dailies: 2017-2019 bull 30% / bear 70% (n 668 days with SMA defined); 2020-now bull 59% / bear 41%; all 53% / 47%.
Regime: none as a gate, because bull and bear are pooled; BTC close vs 200d SMA bull/bear split is reported, not conditioned on.
Phase: counter-trend long in sold-off conditions (capitulation); the daily RSI<30 gate on cells S1/S2 is the only conditioner, S3 has no gate.
Session: none, not filtered (24h).
Entry: closed red TF bar with RSI14 <= T (first touch, re-arm above 30), next TF bar closes above its close; entry at that close, stop = signal bar low.
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## Data (new data only, two blocks)
Binance SPOT klines (1h and 1d) from data-api.binance.vision (public market data; no futures host), cached under runtime_data/edge5-rsi-htf-power-1113/ (ignored). Folding to 4h/8h/12h (UTC epoch anchor, incomplete groups dropped), Wilder RSI and daily-RSI lookup are the parent's code (rsi_grid_lib.py, htf_lib.py copied unchanged). Daily RSI = Wilder 14 on closed spot dailies, last daily closed at or before the signal bar close.
- Block 1 (B1): the parent's 20 coins (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM UNI TRX BCH ETC FIL XLM NEAR SAND) on spot history from listing (2017) up to entry time before 2020-01-01. Only coins that existed; others named in RESULT. Parent used data from 2020-01-01 only, so no overlap in time.
- Block 2 (B2): 40 further coins, full spot history to now (entries any date). Selection rule (pick_universe.py, run once on 2026-11-13, before any outcome): top USDT spot pairs by 24h quote volume with first daily kline before 2022-01-01, excluding the parent's 20, stablecoins, wrapped/liquid-staking tokens, fiat, gold and tokenised-stock symbols. Frozen list (40): ZEC INJ AAVE FET QNT HBAR ICP DODO ONE DASH STX RAY AR CAKE DEXE SHIB JST CRV ZEN BAT GTC ALGO RUNE GRT VET CITY AVA LSK GALA PHA AXS CFX RSR IOTA SUPER CHZ CVX TWT PEOPLE HOT. (Chosen by present liquidity, not by outcomes; survivorship note in limits.)
- Parent-20 coins after 2020-01-01 are excluded entirely (already used).

## Rules (parent's, unchanged)
- Signal (SOURCED, operator): TF RSI(14) <= T on a closed red bar; first touch per episode, re-arm only after RSI(TF) closes > 30 (OURS); next contiguous TF bar closes above the signal bar's close; entry = that close; stop = signal bar low (SOURCED). Stop fill = min(stop, bar open); same-bar stop+target = stop first; forward walk on 1h bars after the entry close; closed bars only.
- Exits: 2R target with cap 20 TF bars (SOURCED 2R; cap OURS), exit at close of cap if neither hit; time exit = close of 10th TF bar after entry (SOURCED). Stop active in both.
- Costs: per side fees.BINANCE_TAKER (5 bp) + fees.SLIPPAGE_RT_S13/2 (1 bp), imported from MyTradingSys/backtest/fees.py; net R = (gross return - round-trip cost)/stop distance. No funding (spot data, long-only).
- Trades without a full forward window dropped.

## Cells (EXACTLY 6, fixed now)
Signal x exit, signal in {S1: 4h RSI<=12 and daily RSI<30; S2: 4h RSI<=15 and daily RSI<30; S3: 12h RSI<=20, no gate} x exit in {tgt2R, time10}.
Primary metric: fee-net mean R per trade on the pooled new data (B1 + B2). B1, B2 and POOL are each reported.

## Statistics and pass rule (per cell, on POOL)
- Trade CI: iid bootstrap over trades (5000 resamples), 95% percentile. Day CI: cluster bootstrap over signal-bar UTC dates (all coins that signalled on one date form one block; ratio estimator, 5000 resamples), 95% percentile. One-sided bootstrap p = share of resampled means <= 0.
- Placebo A (coin + month matched): each real trade replaced by a random TF-bar close of the same coin in the same calendar month with the same stop distance and same exit rule; 400 draws; draw statistic = pooled mean R. Placebo B (BTC-oversold days): same, but the candidate bar may be any TF-bar close of the same coin inside the same block window (B1: before 2020-01-01; B2: any) at which the last closed BTC daily RSI < 35; 400 draws. p = (draws >= real mean + 1)/(draws + 1).
- PASS needs ALL: mean > 0; trade-CI lower > 0; day-CI lower > 0; >= 30 distinct signal days; placebo A p and placebo B p both <= 0.05/6; day-bootstrap one-sided p <= 0.05/6 (Bonferroni over 6 cells). Fewer than 30 distinct signal days = UNDERPOWERED; else FAIL. No edge claim unless PASS.
- Also reported: per-calendar-year mean R and n; share of total R from the best 5 signal days (by day sum) and mean R without those 5 days; bull vs bear split by BTC daily close vs 200d SMA at the signal bar close (n, mean, win%); win%.

## Limits stated now
Spot not perps (no funding, spot/perp basis differs); selection of B2 by current liquidity is survivorship-biased toward coins that survived; tiny stop distances inflate R; coins are highly correlated, hence the day-cluster view; B2 fine-grained history of small coins can have gaps (contiguity checks drop affected bars); S1 is a subset of S2 so those cells are not independent; Bonferroni over 6 is conservative given that.
