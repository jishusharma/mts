# PRE_REG nk2-pivot-sr-reclaim-1114 (written before any outcome was computed)

Rule: NK StockTalk pivot S/R (video 3EpXq8JC4jU, concept srp; flash_deep EXTRACT). Label: SOURCED = NK said it; OURS = our choice.

## Parameters
| Item | Value | Label |
|---|---|---|
| Pivot type | standard floor pivots P=(H+L+C)/3, R1=2P-L, S1=2P-H, R2=P+(H-L), S2=P-(H-L), R3=H+2(P-L), S3=L-2(H-P); NOT Fib/Camarilla | SOURCED |
| Pivot inputs | previous UTC daily H/L/C (known at day open) | OURS (crypto day = UTC) |
| Timeframes | 15m and 1h (1h = 15m resampled, UTC aligned) | SOURCED |
| Long trigger | prev bar close < X <= this bar close, X in {P, S1} (close back above after a fall) | SOURCED (reclaim of pivot); S1 variant OURS |
| Short trigger (mirror) | prev bar close > Y >= this bar close, Y in {P, R1} (failed reclaim / rejection) | OURS mirror |
| Entry | open of the next bar after the trigger close | OURS (no look-ahead) |
| Stop | swing extreme of last 6 bars incl. trigger bar, widened to min distance max(0.6 x ATR14(tf), 0.5% of entry); evaluated on a CLOSE basis (exit at that bar close) | close-basis SOURCED; swing 6, min distance OURS |
| Target | nearest pivot level (of P,R1-3,S1-3) beyond entry in the trade direction; intrabar touch fills at the level | SOURCED (T1=R1,T2=R2,T3=R3) |
| R:R filter | skip if target distance < 1.0 x stop distance | OURS |
| Time stop | exit at close after 24h (96 x 15m / 24 x 1h bars) | OURS |
| Position | one per symbol at a time | OURS |
| Same-bar ambiguity | close beyond stop wins over target (pessimistic) | OURS |
| RSI(14)<30 filter | NOT used (single variant; NK mentions it) | NOT TESTED |
| CPR | not tested | NOT TESTED |

## Fees
Primary 12 bp round trip taker on notional (fee in R = 0.0012*entry/stop distance). One pre-registered maker row: same trades at 6 bp (optimistic: assumes the limit fills at the next open). Report mean fee as a fraction of R.

## Universe and split
20 Binance spot USDT coins: BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO, from 2019 (listing) at 15m. DEV to 2023-12-31, VALIDATION from 2024-01-01 (nothing tuned on DEV; all parameters above fixed; DEV is reported only).

## Context (operator order)
Phase of day D from data up to the close of D-1 (daily bars): MA20 slope = MA20[D-1] - MA20[D-6]; ADX(14, Wilder) >= 20 with DI+ > DI- and slope > 0 = UP; ADX >= 20, DI- > DI+, slope < 0 = DOWN; else RANGE.
Primary rows (matched direction): LONG in UP or RANGE; SHORT in DOWN or RANGE (RANGE = fades both ways). Control rows (mismatched, not gated): LONG in DOWN, SHORT in UP.
Primary row = timeframe x trigger family: {15m,1h} x {LONG-P, LONG-S1, SHORT-P, SHORT-R1} = 8 rows. Regime mix reported per row (share of trades in UP/DOWN/RANGE) and over all days.
Regime: none beyond the daily phase label; the share of trades in UP/DOWN/RANGE and over all days is reported only.
Phase: daily UP/DOWN/RANGE from ADX(14), DI and MA20 slope; LONG in UP or RANGE, SHORT in DOWN or RANGE; mismatched (long in DOWN, short in UP) = control rows, not gated.
Session: none, because 15m and 1h bars on UTC-day pivots in a 24h market, no hour filter.
Entry: close back above pivot P or S1 after a lower close (short mirror with P/R1); entry at the OPEN of the next bar after the trigger close.
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## PASS gates (all on VALIDATION, taker 12 bp, per primary row)
1. n >= 100 trades. 2. mean net R > 0. 3. bootstrap 95% CI lower > 0 per trade AND per UTC-day cluster (10000 / 5000 resamples, seed 7). 4. placebo p < 0.05: matched random entries (same symbol, same side, same allowed phases, same timeframe, VALIDATION period, same stop/target/R:R machinery, no trigger) drawn 1000 times at the same n per symbol; p = (1+#random mean >= observed)/(1001); pool = up to 2000 random bars per symbol/side/tf. 5. survives Benjamini-Hochberg q=0.05 over the 8 primary rows' placebo p. 6. mean net R still > 0 after removing the 5 highest-R UTC days.
Verdict is PASS only if a row passes all six; else FAIL (state which gate). BTC today block is descriptive only.
