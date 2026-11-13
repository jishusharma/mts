# PRE_REG: liquidation-flush reversal, cross-coin (slug edge-oi-flush-1113), written 2026-11-13 before any outcome was computed

Prior work read, not duplicated: `oi_pivot_2026-10-26/RESULT_1H4H.md` (BTC only, OI at price levels, 1h/4h, no effect in powered cells) and `liquidation_layer_2026-10-28/` (modelled heatmap, forward only, no data). This study differs: realised OI drop + large price move as an EVENT, 10 coins pooled, fixed holds up to 72h.

## Hypothesis (OURS)
A bar where open interest collapses (forced closing) together with a >2 ATR price move in the same direction exhausts the move: price mean-reverts afterwards. Long-liquidation flush (OI drop, price down) -> long; short squeeze (OI drop, price up) -> short. If the OI part adds nothing, a same-size price move without the OI drop reverts equally (placebo).

## Context
Crypto perps carry 5-10 bp round-trip friction; 4h/1d-scale moves after a flush are 2-5x larger than at 5m-1h, so fees weigh less. Cross-coin pooling gives n; BTC-only intraday rules died on fees (layer map). Flushes cluster in bear/volatile episodes (2020-03 style, 2021-05, 2022-06/11), so pooled results can be driven by few days: hence day-cluster bootstrap and per-split reporting.
Regime mix: BTCUSDT DEV window bull 19% | bear 0% | range 81% (SOURCED: MyTradingSys/research/oi_pivot_2026-10-26/RESULT_1H4H.md, window 2022-01..2024-06 only; actual per-split event mix by coin and year is computed and printed in REPORT.md, OURS).

## Data (SOURCED: Bybit v5 public)
`/v5/market/open-interest` (category linear, intervalTime 1h), `/v5/market/kline` (60), `/v5/market/funding/history`. Coins BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (USDT perps). Start date per coin = first OI row Bybit serves (recorded in REPORT.md). Assumption: an OI row stamped T is the snapshot at T. Sensitivity (reported, outside BH): entry one extra bar late.

## Rule (all OURS unless stated)
- Timeframes TF = 1h (native) and 4h (1h bars aggregated, UTC-aligned 00/04/08...). Bar i spans [T, T+TF).
- dOI_i = OI(T+TF)/OI(T) - 1. Threshold q_i = 1st percentile of dOI over the trailing 30 days (720 1h-bars / 180 4h-bars) ending at bar i-1, own coin; needs full window. Event needs dOI_i < q_i.
- ATR = Wilder ATR(14) of the same TF bars, ending at bar i-1 (no look-ahead). move_i = close_i - open_i.
- Long event: dOI_i < q_i AND move_i < -2*ATR. Short event: dOI_i < q_i AND move_i > +2*ATR. (2 and 1% and 30d are OURS.)
- Entry at open of bar i+1 (i.e. bar close, the next-bar open). Dedup per coin and TF: an event within 24h after the last kept event is dropped.
- Exits: fixed hold H in {4,12,24,72} hours (exit at open after H hours), and bracket: stop at flush-bar low (long) / high (short), target entry +/- 2R with R = |entry - stop|, scanning 1h bars from the entry bar, stop wins ties inside a bar, timeout 72h at that bar's open. (OURS)
- Costs: fees.BINANCE_TAKER * 2 round trip (repo constant, SOURCED; Bybit's own taker is similar, noted not substituted), plus actual funding paid: sum of funding rates with timestamp in (entry, exit], long pays positive.
- Return unit: % of entry price, direction-signed, net of costs.

## Placebo (OURS)
For each event: same coin, same calendar month, same side, a random bar of the same TF with same-sign move of comparable size (|move|/ATR within +/-25% of the event's, widened to >= 2 ATR if none) and NOT an OI-drop bar (dOI >= q). Same exit rule, 20 draws averaged per event. Isolates the OI condition.

## Cells and splits
Cells = 2 TF x {H4, H12, H24, H72, bracket} = 10 primary cells, both sides pooled (long-only and short-only reported descriptive, outside BH).
Splits by entry time: DEV 2020-01-01..2024-06-30 | VALIDATION 2024-07-01..2025-06-30 | RECENT 2025-07-01..now.
Primary metric: VALIDATION fee-net mean return per event.
Pass rule: VALIDATION fee-net mean > 0 AND day-cluster bootstrap 95% CI lower bound > 0 AND n >= 30 AND beats placebo (paired event-minus-placebo mean > 0 with CI lower > 0) AND BH 10% across the 10 primary cells (one-sided bootstrap p of mean<=0). n < 30 = UNDERPOWERED. Bootstrap: resample calendar days (cluster), 5000 reps, fixed seed.
