# PRE_REG: RSI-extreme + confirm-candle long with one layer, re-derived on 10 symbols, 2024+ out of sample (frozen 2026-11-15, before any return was computed)

Card `rederive-rsi-confirm-layers` (queue row 1, PLAN_24H_2026-11-15 section 8). Parent study `rsi_confirm_layers_2026-11-13` (20 Bybit perps, 56 layer tests, 0 PASS, fee 10 bp round trip, BH 10 %).
This study keeps the base rule and all 14 layer definitions UNCHANGED (code reused by path from the 11-13 folder, no line edited) and changes only: 10 symbols, the shared cost model
(research_kit.TAKER_RT_PCT 0.14 % round trip instead of 0.10 %), Holm adjustment over 56 day-clustered tests instead of BH over bootstrap p, an explicit regime phase split, and data to 2026-11-15.
Sibling card rederive-rsi-htf-extreme covers the 4h-12 / daily-gate variant; it is not repeated here.

## Hypothesis (operator, "apply different layers")
Bare rule: RSI(14) of 1h or 4h closes <= 20 (first touch); the next bar is green and closes above the signal close = long at that close, stop = signal-bar low. ONE closed-data layer
measured at the signal bar separates bounces from continuations well enough to give positive fee-net expectancy out of sample. Claim tested as encoded, not the trader's discretionary read.

## Context
Regime: the BTC market regime (research_kit.regime_tag: weekly AND monthly RSI 60/40 band plus daily SMA200 side, as-of the signal close) is a descriptive phase split on VALIDATION, not a gate. The layers (daily ADX, DI, trend state) are themselves the regime question.
Phase: counter-trend dip buy into an oversold flush; the layers ask which flush is a bounce. Phase split reported: regime bull vs range (bear never fires on BTC with this tag, stated), and BTC above/below SMA200.
Session: all 24 h; signal-bar session is itself two of the layers (Asia 00-08 UTC, US 16-24 UTC).
Entry: close of the confirming bar (SOURCED, operator). Stop: signal-bar low (SOURCED, operator "red candle low"). Prior family result: 0 of 60 (edge3) and 0 of 384 (edge-rsi-extreme-confirm) and 0 of 56 (11-13 layers, 20 coins).
Regime mix: BTC weeks by research_kit.regime_tag (Binance spot BTCUSDT 1d/1w/1M): DEV 2020-03-01..2023-12-31 200 weeks bull 39 (20%) / bear 0 (0%) / range 161 (80%); VALIDATION 2024-01-01..2026-11-14 150 weeks bull 58 (39%) / bear 0 (0%) / range 92 (61%); first half 2024-01..2025-06 79 weeks bull 63% / range 37%; second half 2025-07..2026-11 71 weeks bull 11% / range 89%. (regime_mix.txt; computed from BTC closes only, before any trade return.)

## Data, universe, splits
Bybit v5 public linear USDT perps (public market data), 1h and 1D klines, 8h funding history, 1h open interest (fetch.py; ignored cache runtime_data/rsi-confirm-10sym-1115/): BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX
(the 10 most established majors, all listed before 2022; same list as the sibling 10-symbol re-derivations; chosen by listing age and liquidity before any return; survivorship-biased toward survivors, stated; a strict subset of the 20 coins of the parent study).
Still-forming bar dropped; trades with < 168 h of forward data excluded (last 7 days). Splits by ENTRY (confirm close) time: DEV 2020-01-01..2023-12-31 (stability only), VALIDATION 2024-01-01..data end (decides).
Out-of-sample honesty: the parent study already looked at the 2024+ results of these layers on a superset of these coins, so the 2024+ window is only partly fresh for the layers (new: cost, symbols subset, ~10 extra days, Holm). No parameter is tuned here; the verdict is a re-test, not a discovery.

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| Signal | Wilder RSI(14) of TF closes <= 20, first touch per episode, re-arm after RSI > 30; TF in {1h, 4h} (4h folded from 1h, UTC-anchored) | threshold 20 OURS (parent grid's widest), RSI(14) and Wilder SOURCED (Wilder) |
| Confirm | next bar green and close > signal close; entry = its close | SOURCED (operator) |
| Stop | low of signal bar; fill = min(stop, bar open) | SOURCED (operator); gap fill OURS |
| Exits | +1R or +2R target, R = entry - stop; 72 h cap exit at close; same-bar stop+target = stop | OURS |
| Cost | 0.14 % round trip, taker both legs incl. slippage, charged on entry price and divided by the stop distance (= R); funding not charged (holds <= 72 h, limitation) | SOURCED research_kit.TAKER_RT_PCT (no cost constant defined here) |
| 14 layers | dADX<20, dADX 20-25, dADX>25, dDI-down, 4hADX>=40, OI-unwind (<= -3 % / 24 h), VolCap (>= 3 x 50-bar mean), BTC>200MA, BTC/ETH, Asia, US, FundNeg, Deep (RSI <= 10), SmallR (lowest DEV tercile of stop distance) | exactly as 11-13 PRE_REG (thresholds OURS except ADX 25 and RSI 20/10 common conventions, no trader source) |
| Regime tag | research_kit.regime_tag on BTC, as-of signal close | band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo, "range = the rest" OURS, BTC-for-all-symbols OURS |

## Tests, statistics, decision rule
Family = 4 base sets (1h/4h x +1R/+2R) x 14 layers = 56 tests, decided on VALIDATION. Statistic: mean fee-net R of the filtered trades; SE clustered by UTC day of entry across ALL symbols
(research_kit.cluster_mean_se; same-day trades on different coins are correlated); one-sided p for mean R <= 0 from t = mean/SE (normal); Holm step-down over m = 56 (research_kit.holm).
A layer PASSES only if ALL hold on VALIDATION: n >= 30; mean net R > 0; Holm-adjusted p <= 0.05; filtered mean > unfiltered base mean of the same set; mean > 0 in both halves of VALIDATION
(2024-01..2025-06 and 2025-07..data end); beats a random-subset placebo (1000 random same-n subsets of the unfiltered VALIDATION base trades, p <= 0.05). n < 30 = UNDERPOWERED, never PASS.
Also reported (not decision): week-block bootstrap 95 % CI (2000 resamples, seed fixed), win%, MDE = 2.8 x SE per cell, DEV n and mean, phase split (regime bull/range, BTC above/below SMA200) of the 4 base sets and of any layer with Holm p <= 0.20.
Pairs of layers (stage 2 of the parent) are NOT run: they would add multiplicity and the parent found no layer passing the DEV screen worth pairing.
Verdict EDGE only if at least one layer PASSES; otherwise NO EDGE. Whatever the outcome, no edge claim goes to testnet from this study alone.

## Limits stated now
Trades overlap across correlated coins (day clusters handle part); no funding charge; VALIDATION first half is bull-heavy and the second half range-heavy (bear never fires); 56 tests at n of 30 to 250 per cell means most cells are low power (MDE reported per cell);
survivorship-biased universe; Bybit data (the parent also used Bybit) while the regime context is Binance spot.
