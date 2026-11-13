# PRE_REG: SHORTS at stacked seller layers, DOWN phase only (edge9-downtrend-seller-layers-1114)

Written 2026-11-14 before any outcome of this study was computed (no trade, return or hit-rate was looked at).
Operator order 2026-11-13 20:15Z: BTC is in a 6-week downtrend; look for shorts where sellers sit (Tom/Fabio layers: value area high, POC, low-volume nodes), several layers stacked, only inside the matching phase.

## Context
Regime: DOWN phase is the gate (coin daily close < its 20-day SMA AND 20-day SMA falling over 5 days, decided at the prior UTC daily close). Control row = same signals on all days. RESULT.md carries a `Regime mix:` line (BTC close vs 200-day SMA, 5% band, as sibling studies) and the share of study trades that fall in DOWN.
Phase: downtrend; sellers defend prior-day value above price. SOURCED in kind: Tom/Fabio value-area and POC definitions (FAB-042 value area/POC, FAB-047 declining POC/VA = weakness, FAB-049 failed auction at the VAH, FAB-005 lowest-volume price inside the value area = low-volume node; `where_is.py "value area"`, `backtest/layers/fabio/`). Exact use as a short trigger is OURS.
Session: 24 h crypto; UTC day for "prior day"; 15m signal bars, 1h for RSI.
Entry: touch of a layer from below on a 15m bar that closes back below it; short at the next 15m open. Stop 0.1% above the touch bar high. Exits: 1R, 2R, prior-day low, 12 h time stop.

## Data
Bybit v5 public linear 15m klines (api.bybit.com, category=linear), full available history per coin, closed bars only (the still-forming last bar is dropped). 10 coins: BTC ETH SOL XRP DOGE BNB ADA AVAX LINK LTC (USDT perps). Spreading volume: kline volume (base). Daily bars = UTC aggregation of 15m (complete days only). No Binance futures host is used.
Split: DEV to 2023-12-31, VALIDATION 2024-01-01 onward (by signal bar time). The verdict uses VALIDATION only.

## Layers (price levels computed ONLY from days strictly before the trade day)
Profile (all value-area layers): 15m bars of the window, HLC3 assigned to bins of 5 bp of the window's mean close (repo auction_context convention, OURS bin), volume per bin; POC = max bin; value area = 70% of volume grown from the POC by adding the heavier neighbouring bin (SOURCED 70%, Tom/Fabio; growth rule OURS).
- L1 prior UTC day value area high (VAH). SOURCED in kind (Tom/Fabio), 15m-bar construction OURS.
- L2 prior day POC, touched from below. SOURCED in kind.
- L3 prior day high. OURS (plain prior-day extreme).
- L4 low-volume node of the prior 3 UTC days: the lowest-volume bin strictly inside that 3-day profile's value area (FAB-005 definition), one node per day. SOURCED in kind; 3-day window OURS.
- L5 1h RSI(14, Wilder) >= 60 on the last closed 1h bar at the touch. OURS (NK-style overbought in a downtrend; state, not a price level).
- L6 net taker selling on the touch bar: DROPPED. Bybit v5 klines carry no taker buy/sell split and the public-trade archives for 10 coins x full history do not fit the 80-minute box. Said again in RESULT.md.

## Signal (per coin, 15m bar j)
- Price layers L1..L4 with level P are "touched from below" when open_j < P <= high_j and close_j < P (rejection). The reference level R = the highest touched level. Signal at the close of bar j, short at open of bar j+1.
- Confluence count k = number of price layers (L1..L4, one count per layer) whose level lies within 0.2% of R (|P-R| <= 0.002 R) plus 1 if L5 holds. k >= 1 always. Rows: k=1, k=2, k>=3.
- Single-layer rows: L1, L2, L3, L4 = signals where that layer is among those counted within the 0.2% cluster; L5 row = signals with RSI >= 60. A signal can sit in several rows (overlap is stated). Plus an ALL row.
- One open trade per coin at a time; signals while a trade is open are skipped. Skip if the next open >= the stop.
- DOWN gate: signal bar's UTC date has DOWN true (computed from daily closes through the previous UTC date). Control rows (ALL, k=1, k=2, k>=3) use all days with the same signals (descriptive, outside the BH family).

## Exits (three variants, each reported; every row x exit is its own hypothesis)
Stop = touch bar high x 1.001. Exit E1: target 1R below entry; E2: 2R; E3: prior UTC day low (variant skipped when it is < 36 bp = 3 x round trip below entry; skips counted). Time stop: close of the 48th 15m bar after entry (12 h). Bars from j+1 onward count (entry at j+1 open); stop-first when one bar touches both.
Net R = (-(exit-entry)/entry - round-trip cost) / ((stop-entry)/entry); cost per side = fees.BINANCE_TAKER (5 bp) + fees.BINANCE_TAKER/5 (1 bp slippage) = 6 bp, round trip 12 bp (OURS slippage; taker from repo fees.py). Gross R printed alongside.

## Pass rule (per row x exit, VALIDATION trades, DOWN days, ALL required)
1. mean net R > 0. 2. 95% bootstrap CI lower bound > 0 on the per-trade view (5000 draws) AND on the day-cluster view (resample UTC dates across coins, 5000 draws). 3. n_VAL >= 100 (else UNDERPOWERED when the mean is positive, FAIL otherwise). 4. Placebo p < 0.05: random shorts on DOWN days matched trade-by-trade on coin, UTC hour of the entry bar and holding time (enter at a random 15m open of that coin/hour on a VALIDATION DOWN day, exit at the close after the same number of 15m bars, same risk denominator and costs; 2000 draws; p = share of draws with mean >= real mean). 5. BH at 10% across all row x exit hypotheses (9 rows x 3 exits = 27) on the one-sided day-cluster bootstrap p. 6. Mean net R > 0 after removing the 5 best UTC days (by summed R).
Verdict PASS only if all hold. Win rate (share of net R > 0) is printed beside mean R in every row. DEV numbers are descriptive.

## Parameter labels
| param | value | label |
|---|---|---|
| value area share | 70% | SOURCED (Tom/Fabio) |
| VAH / POC / LVN as levels | | SOURCED in kind; use as short trigger OURS |
| profile bin 5 bp, HLC3, 15m bars, growth rule | | OURS (repo auction_context convention) |
| prior day = UTC day | | OURS |
| LVN window 3 days | | OURS |
| prior-day high layer | | OURS |
| RSI(14) 1h >= 60 | | OURS |
| phase gate SMA20 and 5-day slope | | OURS (operator order) |
| touch from below + close below = rejection | | OURS (operator order) |
| cluster width 0.2% | | OURS (operator order) |
| stop 0.1% above touch high; 1R / 2R / prior-day low; 12 h | | OURS (operator order) |
| costs 5 bp taker + 1 bp slip per side | | taker SOURCED repo fees.py, slip OURS |
| split 2023-12-31 / 2024-01-01 | | OURS (operator order) |
| 10 coins | | OURS (operator order) |

## Also
Descriptive list (not a trade instruction) of BTC seller layers for 2026-11-13 and 2026-11-14 UTC with prices, from the same code, plus last price and DOWN state.
