# PRE_REG: 4h / 8h / 12h RSI(14) <= 12 with daily RSI < 30, next candle closes higher, stop = signal-candle low, exits 1R / 2R / 3R / time (slug edge4-rsi-4h-le12-daily-lt30-1113)

Written and committed BEFORE any outcome is computed. Only the raw kline download (`fetch_klines.py`) and the fail-first tests have run. Card
`edge4-rsi-4h-le12-daily-lt30-1113`, Wave 2 of `PLAN_EDGE_5H_2026-11-13.md`. Origin: operator order 2026-11-13 18:15Z (extreme RSI on a higher timeframe,
daily RSI also low, wait for the next candle to close higher, stop below the signal candle) and the BTC-only reading that 4 of 5 episodes reached 2-3R.
Five episodes are too few, so the test pools 20 coins. Sibling: `rsi_extreme_confirm_2026-11-13` (1h, grid of thresholds and ATR stops: FAIL 0/384); this study is
the 4h-and-up version with one fixed threshold, one fixed stop, and no grid.

## Context
Regime: none as an entry gate, because the daily RSI < 30 condition IS the context gate (deeply oversold daily); the window's bull/bear mix is reported per split (BTC daily close vs its 200-day SMA), see Regime mix.
Phase: none, because no cycle-phase input is part of the rule.
Session: none, because crypto trades 24h and the rule names no session; the signal bar's hour is not filtered.
Entry: close of the confirming candle (the candle after the signal candle, only if it closes above the signal candle's close).
Regime mix: reported in REPORT.md as the share of days BTC closed above / below / within 5% of its 200-day SMA per split (DEV / VALIDATION / RECENT), plus the share of signal trades per regime; a split >85% one regime is flagged ONE-REGIME and cannot carry a PASS alone.

## Data (OURS unless marked)
| Item | Choice |
|---|---|
| Universe | 20 Bybit USDT-linear perps: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM TRX BCH ETC UNI NEAR FIL XLM AAVE (fixed before any outcome: the 10 sibling coins plus 10 older large caps). A coin enters from its first Bybit kline (>= 2020-01-01), so "since 2020" means since listing; most coins start 2020-2022. |
| Source | Bybit v5 public klines, `fetch_klines.py`: 4h (240), 12h (720), daily (D). 8h is built from aligned 4h pairs (00/08/16 UTC); an 8h bar needs both halves. Cache `runtime_data/edge4-rsi-4h-le12-1113/` (git-ignored). Public data only, no keys. |
| Bars | the partial current bar is dropped by requiring a full 12-bar walk after entry; only closed bars exist in the walk. |
| RSI | Wilder RSI(14) of the bar closes (SOURCED: Wilder 1978, n = 14), re-implemented in the run script and checked against hand values in the test. |
| Daily RSI | RSI(14) of the last daily bar whose close time is at or before the signal bar's close time (no look-ahead). |

## Rule (per timeframe TF in {4h, 8h, 12h}; long only, as the card states)
- Signal bar S (TF bars): `RSI_TF[S] <= 12` (OURS; the card's number, kept for 8h and 12h without tuning) AND daily RSI as of the S close `< 30` (OURS, card).
- Confirm bar C = S+1: `close[C] > close[S]`. If not, no trade.
- Entry at the CLOSE of C (the card; the signal needs that close, so no look-ahead).
- Stop = `low[S]` (the signal candle's low), live from the bar after C. R = entry - stop (> 0 always, as close[C] > close[S] >= low[S]). A stop fills at the stop price, or at the bar open if the bar opens below it.
- Exits (one cell each): target 1R, target 2R, target 3R (limit fills at the target price; a bar that touches both target and stop counts as a STOP: stop first, conservative), and `time`: no target, close of the 12th bar after C. In every exit the stop is live and a hard cap of 12 bars after C applies (close of that bar). 12 bars = 2 / 4 / 6 days for 4h / 8h / 12h (OURS).
- One open position per coin per cell; a signal while that cell holds a position in that coin is skipped. Cells are simulated independently.
- Trades whose bars are not contiguous (missing klines in S..C+12) are dropped, not repaired.
- Cells: 3 TF x 4 exits = 12 cells (the BH family). Nothing else is varied: no threshold grid, no stop variants, no short side.

## Costs (imported from `MyTradingSys/backtest/fees.py`, no constant of my own)
Round trip = `2 * fees.BINANCE_TAKER` + `fees.SLIPPAGE_RT_S13` (taker on both legs including stop and target fills, plus the s13 slippage allowance). Net R = (return - round trip) / (R / entry). Funding is NOT charged (holds are at most 6 days; reported as a limitation).

## Splits (SOURCED: the sibling RSI studies and the PLAN pass rule; by ENTRY bar time)
DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30; RECENT 2025-07-01..last closed bar. The verdict is read on VALIDATION. DEV and RECENT are reported; DEV is not a pass condition (PLAN pass rule), RECENT only sets ROBUST.

## Statistics, placebo, verdict
- Inference unit: net R per trade; cluster = UTC day of entry (`research_kit.cluster_mean_se`), 95% CI by cluster bootstrap over days (2000 draws, seed 20261113), one-sided normal p (mean R > 0). A CI is computed only at n >= 30.
- Placebo P1 (the PASS placebo): same coin, same split, same TF: every bar whose only condition is "next bar closes higher than this bar" (no RSI, no daily condition), same stop and exit rule. For each observed trade one placebo trade is drawn from the matching (coin, split) pool, 1000 resamples; placebo p = (1 + resample means >= observed mean) / 1001. This isolates the whole filter (RSI extreme + daily oversold) from the "bounce candle + low stop" mechanics.
- Placebo P2 (descriptive, which part carries it): as P1 but the pool is restricted to bars with daily RSI < 30 (no TF-RSI condition). If P1 is beaten but P2 is not, the TF extreme adds nothing beyond the daily-oversold context.
- BH at 10% over the 12 VALIDATION p-values (family = the 12 cells).
- PASS (a cell, the PLAN pass rule): VALIDATION n >= 30, VALIDATION mean fee-net R > 0, bootstrap 95% CI lower bound > 0, P1 placebo p <= 0.05, BH-10% significant, and the VALIDATION split not ONE-REGIME. ROBUST = PASS and RECENT n >= 30 with mean net R > 0.
- n < 30 in VALIDATION: UNDERPOWERED, never "no edge". Overall verdict: PASS if any cell is PASS; FAIL if none and at least one cell has VALIDATION n >= 30; UNDERPOWERED if every cell has n < 30.
- Headline pooled all-period numbers (n, mean net R, win rate) per TF x exit are also reported as the card asks, as descriptive rows (the all-period mean is not a pass test). Per-coin and BTC-only rows are descriptive.

## Planned report
REPORT.md: verdict line first (n, fee-net R, placebo verdict), table TF x exit x split (n, mean net R, CI, win rate, P1 p, P2 p, BH), BTC alone, signals per coin, Regime mix line; `summary.json` with the same numbers.

## Parameter labels
SOURCED: Wilder RSI(14); the splits (sibling studies). OURS: the 20-coin universe, RSI <= 12 and daily < 30 (the card's numbers, reused unchanged for 8h/12h), 12-bar cap, 1R/2R/3R (card), cost model, placebo design, BH family, regime definition (+-5% of the 200-day SMA).
