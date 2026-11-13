# PRE_REG: Malkan MAL-R03 / MAL-R04 regular RSI divergence, 1h and 4h, 20 perps (slug edge4-malkan-a-1114, part of edge4-malkan-divergence-r03-r04-1113)

Written and committed BEFORE any outcome is computed. Only the kline download (`fetch_klines.py`) and its fail-first tests have run. Rules are taken from
`MyTradingSys/research/layer_lab/gemini_edge_1113/mine-malkan/RULES.md` (MAL-R03 bearish, MAL-R04 bullish; source `extract_Wvq1TZh8aF0.md:462-499`). Part b
writes the detector and trade engine, part c runs and reports; this file fixes the rule and the data.

## Context
Regime: none as an entry gate (R04 is described "in a downtrend", R03 mirrors it, but no trend filter is applied; the trend is reported, not gated).
Phase: none, no cycle input.
Session: none, crypto trades 24h; no hour filter.
Entry: the close of the confirming candle (see Rule).
Regime mix: reported in the part-c REPORT.md as the share of days BTC closed above / below / within 5% of its 200-day SMA per split (DEV / VALIDATION / RECENT) and the share of signal trades per regime; a split over 85% one regime is flagged ONE-REGIME and cannot carry a PASS alone.

## Rule (both sides; R03 short, R04 long)
| Element | Choice | Label |
|---|---|---|
| Divergence | R03: price higher high A to B while RSI makes a lower high. R04: price lower low A to B while RSI makes a higher low | SOURCED (Malkan, quotes in RULES.md) |
| Confirming candle | R03: a red candle after peak B. R04: a bullish (green) candle after trough B. Entry on the close of that candle | SOURCED |
| Stop | R03: above the signal candle high including the shadow. R04: below the signal candle low | SOURCED |
| Target | Point C: R03 the trough between peaks A and B (lowest close); R04 the peak between troughs A and B (highest close) | SOURCED |
| RSI | Wilder RSI(14) of closes | SOURCED (Wilder 1978, n = 14; Malkan uses 14) |
| Swing detection | closes only (no wicks) for A, B and C; A and B are the two most recent swing extremes inside the lookback | OURS |
| Lookback | 12 or 18 bars between A and B (two variants) | OURS |
| Timeframes | 1h and 4h (Malkan trades daily; intraday is OURS so the sample is large enough) | OURS |
| Exit | target C, stop, or hard cap 2x lookback bars after entry at the close; a bar touching both target and stop counts as the stop (conservative) | OURS |

Cells: 2 sides x 2 lookbacks x 2 timeframes = 8 cells (the BH family). No other parameter is varied. A trade whose stop is on the wrong side of the entry, or whose target is not beyond entry in the trade direction, is skipped. One open position per coin per cell.

## Data (OURS)
Universe: 20 Bybit USDT-linear perps: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM TRX BCH ETC UNI NEAR FIL XLM AAVE (the sibling edge4_rsi_4h_le12 list, fixed before any outcome). A coin enters from its first Bybit kline (>= 2020-01-01).
Source: Bybit v5 public klines, `fetch_klines.py`, 1h (60) and 4h (240); public data only, no keys. Cache `runtime_data/edge4-malkan-r03-r04-1113/` (git-ignored). Only closed bars are kept, duplicates collapsed, gaps reported (tests: `test_fetch_klines.py`). Trades whose bars are not contiguous are dropped, not repaired.

## Costs
Round trip = `2 * fees.BINANCE_TAKER` + `fees.SLIPPAGE_RT_S13` from `MyTradingSys/backtest/fees.py` (no constant of my own), taker on every fill including stop and target. Funding not charged (limitation).

## Splits, statistics, verdict
DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30; RECENT 2025-07-01..last closed bar, by entry bar time. The verdict is read on VALIDATION.
Unit: net R per trade; cluster = UTC day of entry, 95% CI by cluster bootstrap (2000 draws, seed 20261114), one-sided p (mean R > 0), CI only at n >= 30.
Placebo: same coin, split, timeframe and side: every bar that merely closes in the trade direction (no divergence), same stop and C-style target built from the same lookback, 1000 resamples; placebo p = (1 + resample means >= observed) / 1001.
BH at 10% over the 8 VALIDATION p-values.
PASS (a cell): VALIDATION n >= 30, mean fee-net R > 0, CI lower bound > 0, placebo p <= 0.05, BH-10% significant, split not ONE-REGIME. ROBUST = PASS and RECENT n >= 30 with mean net R > 0.
n < 30 in VALIDATION: UNDERPOWERED, never "no edge". Overall: PASS if any cell PASS; FAIL if none and at least one cell has n >= 30; UNDERPOWERED if every cell n < 30.
