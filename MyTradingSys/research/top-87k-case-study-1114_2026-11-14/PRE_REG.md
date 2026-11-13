# PRE_REG: top-87k case study (1114) - written before any outcome is computed

Purpose: describe, not validate. The 2026 Sep-Oct top is a CASE (one episode, in-sample by construction: the operator described it first).
The rules below were fixed here, before outcomes, and are then measured on history. DEV = 2019-2023-12-31, VALIDATION = 2024-01-01..2025-12-31, CASE = 2026 (never counted in DEV/VAL).

Data: Binance spot BTCUSDT 15m (F:\MTS\data_cache\binance_spot) resampled to 1H/4H/1D/1W; Binance spot 1D klines with taker-buy volume (2017-08+, spot delta = 2*taker_buy - volume); Bybit perp funding (2020-03+) and 1D open interest (2020-08+). Binance fapi unreachable from this machine.

Phase label (causal, daily): BULL = close > SMA200d and SMA200d rising over 30d; BEAR = close < SMA200d and SMA200d falling over 30d; BASE = otherwise.

Single signals (SHORT side; mirror for LONG):
- DIV_RSI_BB: price swing high (k bars each side, confirmed k bars later; k=3 on 1D, 2 on 1W, 5 on 4H) higher than previous swing high (lookback 60 1D / 40 1W / 120 4H) while RSI14 lower at the second; RSI at first >60; at least one of the two swing highs pokes above BB(20,2) upper. Fires at confirmation bar close.
- DIV_WT_BB: same with WaveTrend(10,21), WT at first > 40.
- DIV_RSI_noBB: as DIV_RSI_BB without the BB requirement (shows what the BB filter buys).
- FAILED_BO: 1D high exceeds the highest high of the prior 60 days, and within 3 days a daily close is back below that prior 60-day high. Fires on that close.
- FUND_EXT / OI_EXT: Bybit daily funding sum (OI) at or above its trailing-365d 90th percentile; first day only, 20-day cooldown.
- CVD_DIV: daily close at a 30-day high while the sum of spot delta over the last 14 days is negative. 10-day cooldown.
- W_BELOW_20W / W_BELOW_50W: weekly close crosses below SMA20 / SMA50 of weekly closes.
- LH_BREAK: daily swing high (k=5) lower than the previous swing high, then a daily close below the lowest low between the two swing highs. Fires on the close.
- DI_DEATH: ADX14 >= 20 and -DI crosses above +DI (daily).
Mirror signals for bottoms: bullish divs outside lower BB (RSI<40 at first, WT<-40), FAILED_BD, negative funding extreme (<= trailing 10th pct), CVD_DIV_UP (close at 30d low with 14d delta sum positive), weekly close above 20W/50W, HL_BREAK (higher low, close above the highest high between the two swing lows), DI_BIRTH (+DI crosses above -DI with ADX>=20).

Sequences (to find the fewest false alarms):
- SEQ_A: DIV (RSI or WT, outside BB, 1D or 1W) then, within 40 days and before price makes a new high above the second swing high, a daily close below the lowest low between the two swing highs. Entry = that close.
- SEQ_B: SEQ_A and, at the trigger close, either weekly close < 20W SMA or -DI > +DI on 1D.
- SEQ_C: DIV then DI_DEATH within 30 days (before a new high). Entry = DI_DEATH close.
Mirror: SEQ_A_UP / SEQ_B_UP (+DI > -DI or weekly close > 20W) / SEQ_C_UP.

Outcome definitions: first-touch on daily highs/lows after the entry close (both in one day = loss). Short: win = low <= entry*0.92 before high >= entry*1.04 within 45 days. Long: win = high >= entry*1.12 before low <= entry*0.94 within 45 days. 4H signals: half the distances, 15 days. Weekly signals: 45d window still. Fixed-horizon 30d forward return minus 12 bp per side (24 bp round trip) is the number used for the bootstrap CI (10,000 resamples, events deduplicated to >= 5 days apart per signal) and the placebo (10,000 draws of the same number of random same-phase dates).
Reporting: counts by phase and by DEV/VAL/CASE; no claim of edge from the 2026 case itself.

## Amendment 1 (made after seeing that the strict adjacent-pivot divergence did not fire at the 2026 top; before outcomes of the new variant were looked at)
Added variants DIV_RSI_ANY_BB and DIV_WT_ANY_BB: the second swing high is compared with ANY earlier swing high inside the lookback that is lower in price and higher in oscillator (oscillator at that earlier high above the same threshold), still requiring a BB-upper poke at one of the two. Sequences are also run on this base (names SEQ_A_ANY, SEQ_B_ANY, SEQ_C_ANY and _UP mirrors). This is exploratory (conceived after the case), so only the DEV/VAL numbers count, not the case fit.
