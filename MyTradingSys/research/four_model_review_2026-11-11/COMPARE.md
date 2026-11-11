# Four-model review 2026-11-11: comparison and what to do

Reviews: OPUS.md, SONNET.md, HAIKU.md, SUPERVISOR.md (Fable) in this folder. Each answered the same three tasks (C1 what was
learned, C2 which trades, C3 ADX/DI and volume profile) and one own task. Compared by the Supervisor. No edge claim, no forecast.

## 1. Where all four agree
| Point | Number |
|---|---|
| No trade type has a passing result after fees | 0 of 15 trials passed (edge_hunt_2026-11-09/EDGE_TABLE.md:3) |
| Fading a level (Tom/Fabio sweep and reclaim, the thing Live Aid flashes) loses | -0.106 R, n 1,484; 7y 1h -0.087 R, n 1,871 |
| Counting agreeing indicators does not make a flag more right | 51 % with 4+ of 6 agreeing vs 49 % against |
| ADX/DI and the value area are context and location, never a trigger | ADX agrees 50 % vs against 46 %; 80 % rule = 44 %, n 493 |
| Live Aid must log what it flags before anything can be learned from it | card live-aid-flag-log-1111 |
| The leads worth a forward test are 4h, not intraday | 4h RSI cross long +0.105 R; Malkan 4h level short +0.10 R (n 126) |

## 2. Where they differ
| Topic | Opus | Sonnet | Haiku | Supervisor | Taken |
|---|---|---|---|---|---|
| Best lead | 15m WaveTrend buy dot + RSI divergence in a 2h uptrend: +0.22 % net, n 22, beats random 30/30 (C30_VALIDATION.md:10-12, checked) | Malkan short, 4h RSI cross | none ranked above "no evidence" | Krown S8 forward slot, then RSI cross, Malkan | Opus: I missed C30; it joins the forward slots |
| ADX 2-day cross | from ADX under 20 it whipsaws less in all 3 periods (tiny n) | 32-50 % whipsaw, context only | unstable; cross-check file says VERIFIED in the header and PARTIAL 7/9 in the body | context only | context only; fix the file's verdict line |
| Value area on Live Aid | location only | build NY-session profile + delta log | the board never receives it: home.js boardInputs passes vfi, sqz, adx only (checked, home.js:315-327), so setup_board.js value_area never fires; two definitions of yesterday's value area on one page | location only | Haiku's wiring find becomes a card |
| What was lost | - | 57 Eagle Eyes recommendations: 29 done, 6 open, 22 lost (operator trade journal, flow recorders, live exits unlike the backtest, Alert Dock) | - | - | top lost items become cards |

## 3. Opus's own task: one testable rule ("trend pullback to value")
Long only: 4h ADX 20 or more with DI+ on top and not falling; price in the lower half of yesterday's value area; the frozen
WaveTrend + divergence trigger; limit entry; stop below the pivot or value low; target yesterday's value high. A backtest can only
refute it (expected 30-60 trades), so the proof is testnet-forward. Seven curve-fit risks listed in OPUS.md.

## 4. Why no edge so far, and the fee question (operator, 2026-11-11 ~16Z)
His arithmetic is right for a winning trade: a 100 USD move on 1 BTC minus about 70 USD of market-order fees leaves about 30.
The loss side is what was missing: the losing trade loses 100 and still pays 70. With target and stop the same size, the win
rate needed to break even is (move + fee) / (2 x move):

| Move traded per BTC | Break-even win rate, market orders (70 USD) | With limit orders (35 USD) |
|---|---|---|
| 100 USD | 85 % | 68 % |
| 300 USD | 62 % | 56 % |
| 500 USD | 57 % | 54 % |
| 1,000 USD | 54 % | 52 % |
| 2,000 USD | 52 % | 51 % |

(OURS arithmetic; fee 10 bp round trip taker is SOURCED fees.py via AUCTION_CENSUS_1108.md parameter table.)
- Tom and Fabio's own stops, copied from index futures, are 5-8 bp (about 40-60 USD on BTC): the fee is larger than the stop
  (AUDIT_AND_COURSE_CORRECTION.md:14). That is why "after fees" kept deciding.
- The deeper reason: at the levels we tested, direction is right about half the time (47-51 %). Before fees the result is about
  zero (+0.064 R gross, n 1,484), so fees turn zero into a loss. Fees are not the cause; a coin-flip entry is.
- A quoted "60-70 % win rate" says nothing without the size of the average win and loss and the number of trades. A rule that
  takes small profits and holds wide stops wins 70 % of the time and still loses money.
- What we have not tested properly: trades with the higher-timeframe trend (all the failed tests were fades), moves of 500 USD
  or more, his own discretionary trades (never journaled), and a sequence (bias, then level, then timing) instead of a count.

## 5. What gets done (in order)
1. Edge session (Sonnet, started 2026-11-11): the four leads go to testnet-forward paper slots with a 30-trade stop rule; the
   Opus rule is pre-registered and counted; with-trend "naked" Tom/Fabio session trades with moves of 500 USD or more are tested.
2. live-aid-flag-log-1111, then live-aid-learning-loop-1111 (already filed).
3. Cards from this review: value area not reaching the Live Aid board; one bias line instead of level-fade flashes
   (existing live-aid-one-bias-line-1110); operator trade journal; ADX cross-check verdict line; ADX 1h/4h census.
4. Score Bible scenario S008 on 2026-11-16.
