# PRE_REG: Malkan MAL-R03 / MAL-R04 RSI divergence, 20 coins pooled, 1h + 4h (card edge4-malkan-divergence-r03-r04-1113)

Frozen BEFORE any outcome (R, return, win rate) is computed. Only data fetching and event COUNTS precede it.

## Sources (quoted)
- MAL-R03 (`research/layer_lab/gemini_edge_1113/mine-malkan/RULES.md:13,69-88`, extract_Wvq1TZh8aF0.md:462-480): "It is making a new high from A to B but RSI has made a lower high from A to B, which means its upward speed has reduced at point B." / "It will be confirmed when he shows the red candle." / "What would be my stop loss above the high, understand there is a shadow here also in this candle." Exit in the source = point C (trough between A and B).
- MAL-R04 (RULES.md:14,90-102, extract_Wvq1TZh8aF0.md:481-499): "Bullish divergence will come in a down trend. Right? And he will give us the signal to buy." / "...when I see a bullish candle the bullish candle is formed it is confirmed my entry is done means buy" / "...stop loss is the low...". Exit in the source = point C (peak between A and B).
- Operator-confirmed definition (card): divergence on CLOSES (never wicks), swing points 12 or 18 bars apart (relay of Malkan, as in malkan_div_flags_2026-11-04).

## Hypothesis
A regular RSI divergence between two close-swings (price makes a more extreme close, RSI less extreme), confirmed by a candle in the trade direction, on 1h/4h across 20 liquid perps, has fee-net positive expectancy after a stop beyond the swing. Prior BTC-only studies (rsi_divergence_mtf_2026-10-09: 31/32 cells net negative after 10 bp; rsi_divergence_mtf_gated_2026-11-04: 1h aligned n 43 net +0.111 % CI [-0.39,+0.62], 4h n 18, all CIs span zero; gate left 0 bearish setups) never had power: new here is pooling 20 coins, no regime gate, 1h + 4h, a stop/R bracket.

## Rule (exact)
1. Bars: Bybit v5 linear USDT perp 1h klines; 4h folded from 1h, UTC epoch-anchored (00/04/08...), only complete groups. Closed bars only.
2. RSI: Wilder RSI(14) on closes (SOURCED: RSI 14 as in the Malkan RSI studies).
3. Swings (SOURCED: closes not wicks): strict local extreme of the CLOSE (close[i] below/above both neighbours). Consecutive same-kind swings A then B (code reused: `backtest/layers/rsi/rsi_divergence.py::rsi_divergence`, min 3 bars, bars counted inclusive of both swings).
4. Divergence: bearish (R03): close[B] > close[A] and RSI[B] < RSI[A]; bullish (R04): close[B] < close[A] and RSI[B] > RSI[A]; any RSI difference (decimals count). Spacing B-A+1 in 3..W with W in {12, 18} (W SOURCED, operator relay; min 3 SOURCED as in the existing code). W18 contains W12 events plus pairs 13-18 apart.
5. Confirmation (SOURCED: red / bullish candle): the bar right after swing B (bar b+1, the bar whose close confirms the pivot) must be red (close < open) for R03, green for R04. If not, no trade for that divergence (no later bar is searched). Entry = close of bar b+1 (OURS: close of the confirming bar, per card).
6. Stop (SOURCED in kind: "above the high / below the low, including the shadow"; the span is OURS per card "beyond the divergence swing"): R03 = max(high of swing-B bar, high of confirming bar); R04 = min(low of swing-B bar, low of confirming bar). Stop fill = stop, or the bar open if it gapped through; same bar stop + target = stop first.
7. Exits (3, each with stop active): target +1R; target +2R (R = entry-to-stop distance); time exit at the close of the 12th bar after entry (OURS, card). Targets also capped by the 12-bar time exit. (The source exit, point C, is NOT_STATED as a fixed multiple, so R-multiples are OURS.)
8. Costs: 2 x `fees.BINANCE_TAKER` (5 bp per side) + `fees.SLIPPAGE_RT_S13` (2 bp round trip), all imported from `MyTradingSys/backtest/fees.py`, charged on the entry price and converted to R by dividing by the stop distance. This is MORE conservative than the 4 bp/side order in the card; no bare constants. Funding not modelled (holds <= 12 bars).
9. Trades whose 12 forward bars are not available are dropped. The last data point is the fetch time.

## Parameters
| Parameter | Value | Label |
|---|---|---|
| RSI length | 14 Wilder | SOURCED |
| Price series | closes only | SOURCED (operator) |
| Swing definition | strict 1-bar each side close pivot | OURS (as existing code) |
| Window W | 12, 18 | SOURCED (operator relay) |
| Min spacing | 3 | SOURCED (existing code) |
| Confirming candle | next bar red / green | SOURCED |
| Entry | close of confirming bar | OURS |
| Stop | beyond swing-B / confirm bar extreme incl. shadow | SOURCED kind, OURS span |
| Exits | +1R, +2R, 12-bar time | OURS |
| Timeframes | 1h, 4h | OURS |
| Universe | 20 coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT TRX ATOM NEAR UNI ETC BCH FIL AAVE XLM (whatever of 2020+ Bybit lists) | OURS |
| Fees | 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 | fees.py |
| Bootstrap / placebo / BH | below | OURS |

## Context
- Regime: no regime gate (Malkan's monthly/weekly gate leaves 0 bear weeks on BTC 2022-24, gated study). Pooled across all regimes; `Regime mix:` is reported per split as the share of weeks in which BTC close is above / below / inside +-5 % of its 200-day SMA (bull / bear / range), recorded to read the result against, not used to select trades.
- Phase: reversal / counter-trend. R03 shorts a higher high, R04 buys a lower low; Malkan says R04 comes "in a down trend". No trend filter in the primary cells.
- Session: no session filter; trades are reported by UTC entry-hour block (00-08, 08-16, 16-24) as a descriptive table only.
- Entry: close of the first candle in the trade direction after swing B; stop beyond the swing extreme; 1R / 2R / 12-bar.

## Cells (24, fixed; <= 32)
side {R03 short, R04 long} x TF {1h, 4h} x W {12, 18} x exit {1R, 2R, T12} = 24.

## Splits
DEV: signals with entry close <= 2023-12-31 23:59 UTC. VALIDATION: entry close >= 2024-01-01 (to data end). RECENT (>= 2025-07-01) descriptive only. DEV is used for descriptives only; no cell is dropped or tuned on DEV; every one of the 24 cells is tested once on VALIDATION.

## Statistics
- Primary metric: fee-net mean R per trade, VALIDATION.
- Bootstrap, two views (2000 resamples each, seed fixed, 2.5/97.5 percentiles of the mean; one-sided p = share of resampled means <= 0): (A) day-clustered: all signals of one UTC calendar day (all coins) are one block - PRIMARY; (B) per-trade i.i.d. - reported.
- Placebo: per cell 200 draws; each real VALIDATION trade is replaced by a random same-coin TF bar close in the same ISO week, same side, same stop distance (fraction of price), same exit rule; placebo p = share of draw means >= real mean. "Beats placebo" = p <= 0.05.
- BH at 10 % over the 24 day-clustered VALIDATION p-values.

## Pass rule (per cell, all required)
VALIDATION fee-net mean R > 0; day-clustered 95 % CI lower bound > 0; n_VAL >= 30; placebo p <= 0.05; BH 10 % significant. n_VAL < 30 = UNDERPOWERED. Else FAIL. No edge claim without PASS; a PASS is still a lead needing a causal replay test and an independent re-run (CLAUDE.md gates), not a deployable rule.

## Limitations
Bybit perp data not Binance; 20 coins highly correlated (day blocks handle part); no funding; stop and target fills at the level (no slippage beyond the 2 bp); W18 cells overlap W12 cells (same events plus a few), so the 24 tests are not independent (BH is conservative-correct under positive dependence).
