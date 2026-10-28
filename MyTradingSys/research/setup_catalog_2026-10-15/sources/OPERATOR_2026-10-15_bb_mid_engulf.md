# OPERATOR source: BB midline rejection, bearish engulf, second break (2026-10-15, shots 29b79af8ff8f and 587ee73bd78c)

Label: OPERATOR (the operator's own reading, NOT SOURCED, NOT a Malkan/Tom/Fabio quote).
Provenance of this text: the parent session (local_1c4041fd, "Fable 5.1 model usage and optimization") relayed the operator's teaching to this session as a SHORT PARAPHRASE, not a transcript. Only the sentence in double quotes in claim M4 is quoted as relayed; everything else is the relay's wording. If the operator's raw words are saved elsewhere they replace this file.
Charts: shots `29b79af8ff8f` and `587ee73bd78c`, BTCUSDT 5m CoinGlass (UTC axis), BB(20,2), RSI14 + SMA14, OI, CVD, net delta. Registered capture times 13:48Z and 13:54Z are loose: the countdown timers (02:19 and 00:55 left on the forming 13:50 bar) put the shots at about 13:52:41Z and 13:54:05Z, and the forming-bar highs/lows/closes equal our 1m bars (`../evidence/bb_mid_engulf_checks_output.txt`).

## Claims as relayed, one per line

- M1: in a falling market under selling pressure, price bounces to the BB(20,2) midline (80,615 on the chart; the operator's marked horizontal line is 80,654.5).
- M2: a red 5m candle then closes below the OPEN of the previous green candle (a bearish engulf). This is the first confirmation of the midline rejection.
- M3: the next candle breaks lower again: the second confirmation. Here it went to 79,831, below the 80,050 low that was swept earlier.
- M4: "the Bollinger Band can even expand". Check the higher timeframes: if they keep moving with the same momentum, the lower-timeframe levels will be broken.

## Context added by the relay (labelled OURS by the relay, kept as relayed)

- At 13:54Z: RSI 31.9 is below its SMA 37.9 and below 40 (the negative zone); OI is flat at its high, about 94.17K; CVD fell to -11.94K.

## Defaults the relay set (OURS, decided on DEV, never the operator's)

- "Engulf": close < previous open, previous candle green; body ratio chosen on DEV.
- HTF momentum filter: 1h and 4h RSI below 50 and price below the 1h BB midline.
