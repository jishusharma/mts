# PRE_REG: forced-move fade vs new-position follow (edge-forced-move-fade-1113, 2026-11-13)
Committed before any outcome is computed. Sibling study (edge_oi_flush_2026-11-13, FAILED) used 1h/4h bars and price-flush + OI-drop; this one is 15m impulse bars, OI classes both ways.

## Context
Operator example, BTC 15m 13:30Z 2026-11-13: bar spiked 69,190 -> 70,187 on ~10x volume, OI fell the next bar, price returned within 2 h. Question: does OI over the impulse separate forced flow (stops/liquidations) from new positions, and does fading the forced move pay after fees. Existing work: edge_oi_flush (1h/4h, long-only-flush framing) found no pass; data reused only for funding.
Regime mix: not classified before outcomes (OURS); reported as events/days per split and per month in results.

## Data
Bybit v5 public: kline 15m, open-interest intervalTime=15min, funding history (cached), 10 USDT perps BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX. Splits DEV 2020-01-01..2024-06-30 / VALIDATION 2024-07-01..2025-06-30 / RECENT 2025-07-01..now.

## Event (all params OURS except ATR(14) Wilder, 20-bar volume median, which are conventional)
Impulse bar i (15m): range_i >= k*ATR14 (ATR through bar i-1), k in {2,3}; volume_i >= 3 x median(volume of 20 bars before i); high_i > max(high of 16 bars before i) (up impulse) or low_i < min(low of 16 bars before) (down impulse); both -> skip.
dOI = OI(T_i + 30 min) / OI(T_i) - 1 (covers impulse bar and next bar; OI timestamp taken as snapshot time). Class A FORCED: dOI <= -x; B NEW: dOI >= +x; x in {0.3%, 0.6%}; else C flat.
Entry = close of bar i+1 (price known after the OI window). Dedup: per coin, drop an event within 8 bars after the previous kept event of the same hypothesis cell.
Impulse extreme E = high_i (up) / low_i (down); mid M = (high_i+low_i)/2; ATR = ATR at bar i.

## H1: fade A events (side = -direction)
Stop = E +/- 0.25 ATR (beyond extreme). Skip if entry already beyond the stop or already past M (nothing left to retrace); skip counts reported.
Exits (4 cells): T2/T4/T8 = time exit at 2/4/8 h after entry; BR = target M, else stop, else 8 h timeout. Stop active in all modes; if stop and target/limit hit within the same bar the stop is taken (conservative). Stop fill at stop price.
## H2: follow B events (side = +direction)
Stop = M -/+ 0.25 ATR (impulse gave back half). Skip if entry already beyond stop. Exits: T2/T4/T8; BR = target entry + 2R (R = entry-stop distance), else stop, else 8 h.
## Controls (descriptive, not in BH): fade/follow ALL impulses regardless of OI class; fade class B; follow class A.
## H3 (CVD absorption): BTC/ETH/SOL only from 2024-07 if Bybit public trade archive downloads are quick enough (files are 30-260 MB/day); otherwise dropped and said so.

## Costs
fees.BINANCE_TAKER * 2 round trip (imported) plus actual funding settlements inside the hold (sign by side). Return = fee-net % on notional, unleveraged.

## Test
Cells: H1 and H2 x k{2,3} x x{0.3,0.6} x exit{T2,T4,T8,BR} = 32 primary cells, VALIDATION split, both directions pooled. Unit = event; events pooled across coins, so inference is day-cluster bootstrap (5000 reps, UTC day clusters), one-sided p for mean > 0; BH 10% over the 32 cells (n < 30 -> p = 1).
Placebo: per event, 10 random bars same coin, same calendar month, same direction, not themselves impulse bars (range < 1.5 ATR or volume < 2x median or no 16-bar extreme), entered at that bar's close with stop/target distances equal to the event's in ATR units; placebo value = mean of the 10. Event-minus-placebo per event, day-cluster CI.
PASS (cell) = VALIDATION fee-net mean > 0, day-cluster 95% CI lower > 0, n >= 30, event-minus-placebo CI lower > 0, BH 10% survives. RECENT and DEV shown; a pass whose RECENT mean is negative is flagged non-durable. Verdict per hypothesis: PASS if any cell passes, UNDERPOWERED if best cell n < 30, else FAIL.

---
# ADDENDUM H4 (operator order 16:35Z): OI build then unwind on 30m and 1h. Committed before ANY outcome is computed (none exist yet).
Bars: 30m and 1h UTC-aligned, aggregated from the 15m klines (OHLC) with OI at bar close = 15min OI snapshot at (bar open + TF). Same 10 coins, splits, fee/funding rule, day-cluster bootstrap, BH 10%, placebo as above. Params OURS.
Notation: OI_k = OI at close of bar k; ATR = Wilder ATR14 of that TF through bar j-1; N in {6,12} bars; y in {1,2}%.
BUILD at bar j: OI_j / OI_(j-N) - 1 >= y% AND |close_j - close_(j-N)| >= 1.0 ATR; built side s = sign(close_j - close_(j-N)) (up = longs built, down = shorts built).
H4b (follow while building): enter at close of the first bar of a BUILD run (BUILD true, previous bar false), side = s. 
H4a (unwind fade): at bar j, with a BUILD bar (side s) within bars j-N..j-1, peak = max OI over bars j-N..j-1, unwind start = OI_j <= peak * (1 - 0.5%) and OI_(j-1) > peak * (1 - 0.5%) (first such bar). Enter at close of bar j, side = -s.
Exits: time only, 4h / 12h / 24h after entry, no stop (OURS; keeps the OI signal the only moving part). Dedup: per coin, drop an event within N bars of the previous kept event of the same cell.
Cells: {H4a, H4b} x TF{30m,1h} x N{6,12} x y{1,2} x hold{4h,12h,24h} = 96 primary cells, VALIDATION split, BH 10% over 96 (n < 30 -> p = 1).
Placebo: 10 random bars same coin, same month, same TF, no BUILD true on that bar and no OI move >= 0.5% in the last N bars, same side as the event, same time exit. Event-minus-placebo day-cluster CI.
PASS and verdict rules as above, per hypothesis (H4a, H4b). Control (descriptive): H4a with side reversed (follow the unwind).
