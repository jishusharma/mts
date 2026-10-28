# V2 extract LQvv5xgy_ik (Fabio Valentini, risk-management protocols)

Method: EXTRACTION_METHOD_V2.md. Read in 20 chunks of about 2,000 characters, offset 0 to 39,690. The video is a risk-management lecture: no trade is taken and no trade is illustrated; account set-ups and stated risk numbers are recorded as LESSON / CONTEXT rows.

## 3.1 Header
```
video_id: LQvv5xgy_ik
trader: Fabio Valentini (day trader; the transcript is first person and does not say the name)
title: unknown (the raw file has no header line)
instrument_stated: not stated (he mentions US equities for his IVB model; futures brokers, Bitcoin and stocks for other models)
instrument_inferred: none
tick_size: unknown
session / time of day: unknown ("the bottom of the first 30 minutes" of the US open is named for his IVB model; "6 hours per day scalping" in the World Trading Cup)
translation_warning: yes (auto-captioned English, spoken by a non-native speaker; garbled passages flagged in 3.6)
body_chars: 39690
n_decision_rows: 64
n_trades: 0 (no trade shown; 3 account set-ups described)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | CONTEXT | - | account types | how he runs prop, competition and personal accounts | "how I manage a competition account to how I manage my personal account" | - | none stated |
| 2 | 1 | REJECT | - | prop-firm geometry | sniper entries and high R:R / low win rate | "It's not about sniper entry, it's not about high risk to reward low win rate." | - | prop-firm environment |
| 3 | 2 | LESSON | - | - | risk first | "professional only holy grail is risk management" | - | none stated |
| 4 | 3 | LESSON | - | hedge fund | goal of a hedge fund | "The goal of the hedge fund is maximize sustainable risk adjust compounding over time" | - | none stated |
| 5 | 6 | LESSON | - | hedge fund | order of design | "they start from the risk protocol" | - | none stated |
| 6 | 13 | LESSON | - | hedge fund | risk budget | "they want to take the minimum possible amount of risk" | - | they put a maximum on it |
| 7 | 14 | LESSON | - | hedge fund 2025 example | drawdown of two funds | "they had a maximum drawdown during Trump tariff, for example, of 30%, of 20, of 18" | other market (S&P 500, index performance) ; [new source] fund index performance | none stated |
| 8 | 14 | LESSON | - | hedge fund 2025 example | drawdown of a 14% fund | "they had a maximum drawdown of 5% on the account" | - | none stated |
| 9 | 17 | LESSON | - | Medallion example | return vs risk | "maybe he had this with 10 times less risk" | - | none stated |
| 10 | 21 | LESSON | - | - | risk adjusted return | "You need to take the risk adjusted return to related to it" | other market (S&P 500) | none stated |
| 11 | 23 | LESSON | - | - | capacity | "every model have a maximum liquidity capability" | - | none stated |
| 12 | 24 | LESSON | - | scalping model | capacity | "You cannot put billions in a scalping model" | - | slippage grows with size |
| 13 | 24 | LESSON | - | prop firm | goal of prop trading | "The goal here is high pass rate and high probability of payout." | - | none stated |
| 14 | 26 | LESSON | - | prop firm | win rate geometry | "high win rate risk geometry is the best for prop firm" | - | none stated |
| 15 | 28 | LESSON | - | prop firm | win rate stated | "models that have win rate above 60-70%" | - | none stated |
| 16 | 29 | REJECT | - | prop firm | the weekly sniper trade | "in the attempt to take that sniper, you go in the low variance and you lose" | - | you lose the account; [?] 'low variance' where 'high variance' is meant |
| 17 | 31 | LESSON | - | prop firm | best approach | "the best approach that you can have is the low variance risk geometry" | - | none stated |
| 18 | 32 | LESSON | - | prop firm | risk per trade and R:R stated | "moderate risk reward, one to one, even one to 0.75, maximum one to 1.5" | - | evaluation / pass rate |
| 19 | 34 | LESSON | - | prop firm | synthetic market | "you are trading the rules that another entity put on you" | - | none stated |
| 20 | 34 | LESSON | - | prop firm | phases | "on the evaluation phase, the best one is the low variance zone" | - | evaluation phase |
| 21 | 35 | LESSON | - | prop firm | phases | "on the funded phase, you need to optimize for high outcome" | - | funded phase |
| 22 | 37 | LESSON | - | prop firm | counterparty risk | "The best option is to withdraw as much as you can and put in your personal account." | - | prop firm may have regulator problems (a $50,000 payout was flagged for review) |
| 23 | 38 | CONTEXT | - | prop firm live test | his prop approach | "using the order flow approach" | [new source] order flow (generic, no tool named) | none stated |
| 24 | 38 | LESSON | - | prop firm live test | R:R used | "This one I use a risk reward that it's even too high, but I had a really high win rate on this one." | - | market regime was completely directional (his words); no R:R number stated |
| 25 | 39 | LESSON | - | prop firm | conclusion | "the high win rate model with low variance and with low risk to reward is the best one probability of passing it" | - | none stated |
| 26 | 43 | CONTEXT | - | CME Group equity cup | model used | "Is the order flow high win rate scalping low variance" | [new source] order flow (generic, no tool named) | single account, no sequential testing, limited time |
| 27 | 44 | LESSON | - | CME Group equity cup | goal of the cup | "the goal is to keep the drawdown as low as possible" | - | time is limited, a drawdown reduces margin |
| 28 | 45 | CONTEXT | - | CME Group equity cup | result as stated | "you had a net profit of 54.6%, a maximum drawdown 0.42" | - | none stated |
| 29 | 45 | LESSON | - | CME Group equity cup | risk level used | "the risk protocol and approach that got used here, it's aggressive" | - | he took it in a positive drift; a drawdown 10 times larger is possible [?] |
| 30 | 48 | LESSON | - | CME Group equity cup | sizing rule seen in his executions | "The more I was releasing margin, the more I was getting aggressive" | - | margin released as the account grows |
| 31 | 52 | CONTEXT | - | World Trading Cup | goal of the cup | "The goal of the competition is not optimized for risk of ruin." | - | none stated |
| 32 | 52 | LESSON | - | World Trading Cup | rank target | "It's optimized, okay? For terminal rank positioning." | - | none stated |
| 33 | 56 | LESSON | - | World Trading Cup | timing of aggression | "Most participants deploy aggression too early." | - | none stated |
| 34 | 57 | LESSON | - | World Trading Cup | variance | "Early uncontrolled aggression increase the variance before you have enough information" | - | none stated |
| 35 | 58 | LESSON | - | World Trading Cup | regime | "you need to use completely different models" | [new source] market regime (compressing vs expanding) | if the market is compressing vs expanding |
| 36 | 59 | LESSON | - | World Trading Cup | late-stage aggression | "you need to input the maximum amount of aggression in the late stage" | [new source] leaderboard | you know the goal at the second/third month |
| 37 | 59 | LESSON | - | World Trading Cup | costs | "Accounting for World Trading Cup commission and real execution cost prevent false positive expectancy model." | - | none stated |
| 38 | 62 | CONTEXT | - | World Trading Cup phase one | three test accounts | "One account that trend following strategy I tested" | - | none stated |
| 39 | 62 | CONTEXT | - | World Trading Cup phase one | three test accounts | "one account I tested the volatility breakout" | - | none stated |
| 40 | 63 | REJECT | - | World Trading Cup phase one | trend following in a compressing regime | "in this phase here will not give me a leaderboard positioning" | [new source] market regime | If I see that the regime is compressing |
| 41 | 64 | LESSON | - | World Trading Cup phase two | validation | "The second month is validation and moderate risk." | - | none stated |
| 42 | 67 | LESSON | - | World Trading Cup phase three | convexity | "In the third phase is when you do convexity exploitation" | [new source] leaderboard | top slots usually above 50 to 150% |
| 43 | 68 | CONTEXT | - | World Trading Cup phase three | his activity | "I stay there 6 hours per day scalping with the model that I choose" | - | 3-400 trades in the second half of the middle month and the third month |
| 44 | 71 | CONTEXT | - | World Trading Cup result | stated result | "The cumulative month is the 68 and 22%, uh 22% maximum drawdown" | - | none stated |
| 45 | 72 | CONTEXT | - | World Trading Cup result | drawdown in the first week | "I was in drawdown for the first week and I recovered for the second" | - | none stated |
| 46 | 73 | REJECT | - | World Trading Cup | swing trading | "swing trading have is too slow" | - | not enough sample in a quarterly competition |
| 47 | 74 | LESSON | - | World Trading Cup | sample size | "it's not a sample validation that will give you any kind of satisfaction" | - | three, four, five positions |
| 48 | 75 | REJECT | - | World Trading Cup | small account | "if you enter with 2,500, you pay more commission" | - | edge will not survive 300, 400, 500 trades |
| 49 | 76 | CONTEXT | - | World Trading Cup regime test | regime result | "The mean reverting bad performance. The market was directional." | [new source] market regime (directional) | none stated |
| 50 | 77 | CONTEXT | - | World Trading Cup regime test | chosen model | "on this one, I go aggressively trend following scalping." | [new source] market regime (directional) | directional regime; 500, 600 executions in one quarter, 650 [?] |
| 51 | 78 | LESSON | - | personal account | goal | "Risk adjust return, psychological stability, and long-term compounding." | - | none stated |
| 52 | 79 | LESSON | - | personal account | compounding profit | "you could use part of this profit to input additional risk in the next sample" | - | only with moderate risk tolerance and an exceptional month |
| 53 | 82 | LESSON | - | personal account | broker risk | "You need to isolate tail risk" | - | FTX shutdown example; multiple brokers and accounts |
| 54 | 87 | LESSON | - | personal account | risk per trade stated | "it should be 1.25%, 0.5% per trade" | - | if you want to be really conservative; 1.25% as transcribed [?] |
| 55 | 89 | LESSON | - | personal account | risk per trade stated | "I saw some people risking 5%" | - | a streak of a drawdown destroys the account |
| 56 | 89 | LESSON | - | personal account | streak risk | "If you incur in a streak of a drawdown, you will destroy." | - | none stated |
| 57 | 89 | LESSON | - | - | priority order | "The pyramid of risk is the opposite of the competition." | - | personal: ability, then risk management, then return |
| 58 | 92 | LESSON | - | competition account | daily and weekly caps | "automated in terms of blocking the maximum risk per day, the maximum risk per week" | - | no number stated |
| 59 | 92 | LESSON | - | - | measurement | "If there is no measurement, there is no improvement in trading" | - | none stated |
| 60 | 93 | CONTEXT | - | US equities opening | what his IVB model reads | "the bottom of the first 30 minutes is giving a lot of value in the direction of the day" | time of day (first 30 minutes of the US open) ; [new source] opening-range bottom | none stated |
| 61 | 94 | LESSON | - | IVB model | improvement | "can be improved with option flow" | [new source] option flow | study under way |
| 62 | 95 | LESSON | - | - | model decay | "this is the reason then the strategy break" | - | if a profitable strategy is never updated |
| 63 | 95 | CONTEXT | - | investment models | long-term models | "the earning surprise that the riff portfolio" | [new source] earnings surprise (post-earnings drift) | none stated |
| 64 | 99 | LESSON | - | - | closing | "the five point of the risk protocol that I use in all environment of trading" | - | none stated |

## 3.3 Trade blocks
```
No trade was taken and no trade was illustrated (no entry, no stop, no target in this video). n_trades: 0. initial stop: no stop stated anywhere in the video.

SET-UP A - prop-firm evaluation (rows 13-25) - side: none
state: prop-firm evaluation, regime "completely directional" in his live test ; trigger: unknown (no trade) ; initial stop: no stop stated ; target: no target stated ; stated R:R: "one to one, even one to 0.75, maximum one to 1.5" ; stated win rate: above 60-70% ; risk per trade: "moderate" (no number)
information sources: [new source] order flow (generic) ; mirror stated?: no - do not assume

SET-UP B - CME Group equity cup (rows 26-30) - side: none
state: single account, limited time ; model: "order flow high win rate scalping low variance" ; initial stop: no stop stated ; target: no target stated ; sizing: margin released -> size raised ; result as stated: "54.6%" net profit, "0.42" maximum drawdown, 50 or 60 executions
information sources: [new source] order flow (generic) ; mirror stated?: no - do not assume

SET-UP C - World Trading Cup (rows 31-50) - side: none
state: 3-month competition ; phase 1 regime test with three accounts, phase 2 validation, phase 3 aggression ; trend following scalping chosen in a directional regime ; initial stop: no stop stated ; target: no target stated ; result as stated: cumulative "68" (as transcribed), "22%" maximum drawdown ; 3-400 trades, 6 hours per day
information sources: [new source] market regime, leaderboard ; mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 2: sniper entries and high R:R / low win rate (prop-firm geometry). Condition: prop-firm environment.
- Row 6: condition - they put a maximum on it.
- Row 12: condition - slippage grows with size.
- Row 16: the weekly sniper trade (prop firm). Condition: you lose the account; [?] 'low variance' where 'high variance' is meant.
- Row 18: condition - evaluation / pass rate.
- Row 20: condition - evaluation phase.
- Row 21: condition - funded phase.
- Row 22: condition - prop firm may have regulator problems (a $50,000 payout was flagged for review).
- Row 24: condition - market regime was completely directional (his words); no R:R number stated.
- Row 27: condition - time is limited, a drawdown reduces margin.
- Row 29: condition - he took it in a positive drift; a drawdown 10 times larger is possible [?].
- Row 30: condition - margin released as the account grows.
- Row 35: condition - if the market is compressing vs expanding.
- Row 36: condition - you know the goal at the second/third month.
- Row 40: trend following in a compressing regime (World Trading Cup phase one). Condition: If I see that the regime is compressing.
- Row 42: condition - top slots usually above 50 to 150%.
- Row 46: swing trading (World Trading Cup). Condition: not enough sample in a quarterly competition.
- Row 47: condition - three, four, five positions.
- Row 48: small account (World Trading Cup). Condition: edge will not survive 300, 400, 500 trades.
- Row 52: condition - only with moderate risk tolerance and an exceptional month.
- Row 53: condition - FTX shutdown example; multiple brokers and accounts.
- Row 54: condition - if you want to be really conservative; 1.25% as transcribed [?].
- Row 55: condition - a streak of a drawdown destroys the account.
- Row 57: condition - personal: ability, then risk management, then return.
- Row 58: condition - no number stated.
- Row 61: condition - study under way.
- Row 62: condition - if a profitable strategy is never updated.

## 3.5 Verbatim anchors
> "how I manage a competition account to how I manage my personal account"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "It's not about sniper entry, it's not about high risk to reward low win rate."
**Source GPS: LQvv5xgy_ik | BEGIN**

> "professional only holy grail is risk management"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "The goal of the hedge fund is maximize sustainable risk adjust compounding over time"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "they start from the risk protocol"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "they want to take the minimum possible amount of risk"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "they had a maximum drawdown during Trump tariff, for example, of 30%, of 20, of 18"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "they had a maximum drawdown of 5% on the account"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "maybe he had this with 10 times less risk"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "You need to take the risk adjusted return to related to it"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "every model have a maximum liquidity capability"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "You cannot put billions in a scalping model"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "The goal here is high pass rate and high probability of payout."
**Source GPS: LQvv5xgy_ik | BEGIN**

> "high win rate risk geometry is the best for prop firm"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "models that have win rate above 60-70%"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "in the attempt to take that sniper, you go in the low variance and you lose"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "the best approach that you can have is the low variance risk geometry"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "moderate risk reward, one to one, even one to 0.75, maximum one to 1.5"
**Source GPS: LQvv5xgy_ik | BEGIN**

> "you are trading the rules that another entity put on you"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "on the evaluation phase, the best one is the low variance zone"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "on the funded phase, you need to optimize for high outcome"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "The best option is to withdraw as much as you can and put in your personal account."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "using the order flow approach"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "This one I use a risk reward that it's even too high, but I had a really high win rate on this one."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "the high win rate model with low variance and with low risk to reward is the best one probability of passing it"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "Is the order flow high win rate scalping low variance"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "the goal is to keep the drawdown as low as possible"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "you had a net profit of 54.6%, a maximum drawdown 0.42"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "the risk protocol and approach that got used here, it's aggressive"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "The more I was releasing margin, the more I was getting aggressive"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "The goal of the competition is not optimized for risk of ruin."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "It's optimized, okay? For terminal rank positioning."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "Most participants deploy aggression too early."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "Early uncontrolled aggression increase the variance before you have enough information"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "you need to use completely different models"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "you need to input the maximum amount of aggression in the late stage"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "Accounting for World Trading Cup commission and real execution cost prevent false positive expectancy model."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "One account that trend following strategy I tested"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "one account I tested the volatility breakout"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "in this phase here will not give me a leaderboard positioning"
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "The second month is validation and moderate risk."
**Source GPS: LQvv5xgy_ik | MIDDLE**

> "In the third phase is when you do convexity exploitation"
**Source GPS: LQvv5xgy_ik | END**

> "I stay there 6 hours per day scalping with the model that I choose"
**Source GPS: LQvv5xgy_ik | END**

> "The cumulative month is the 68 and 22%, uh 22% maximum drawdown"
**Source GPS: LQvv5xgy_ik | END**

> "I was in drawdown for the first week and I recovered for the second"
**Source GPS: LQvv5xgy_ik | END**

> "swing trading have is too slow"
**Source GPS: LQvv5xgy_ik | END**

> "it's not a sample validation that will give you any kind of satisfaction"
**Source GPS: LQvv5xgy_ik | END**

> "if you enter with 2,500, you pay more commission"
**Source GPS: LQvv5xgy_ik | END**

> "The mean reverting bad performance. The market was directional."
**Source GPS: LQvv5xgy_ik | END**

> "on this one, I go aggressively trend following scalping."
**Source GPS: LQvv5xgy_ik | END**

> "Risk adjust return, psychological stability, and long-term compounding."
**Source GPS: LQvv5xgy_ik | END**

> "you could use part of this profit to input additional risk in the next sample"
**Source GPS: LQvv5xgy_ik | END**

> "You need to isolate tail risk"
**Source GPS: LQvv5xgy_ik | END**

> "it should be 1.25%, 0.5% per trade"
**Source GPS: LQvv5xgy_ik | END**

> "I saw some people risking 5%"
**Source GPS: LQvv5xgy_ik | END**

> "If you incur in a streak of a drawdown, you will destroy."
**Source GPS: LQvv5xgy_ik | END**

> "The pyramid of risk is the opposite of the competition."
**Source GPS: LQvv5xgy_ik | END**

> "automated in terms of blocking the maximum risk per day, the maximum risk per week"
**Source GPS: LQvv5xgy_ik | END**

> "If there is no measurement, there is no improvement in trading"
**Source GPS: LQvv5xgy_ik | END**

> "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

> "can be improved with option flow"
**Source GPS: LQvv5xgy_ik | END**

> "this is the reason then the strategy break"
**Source GPS: LQvv5xgy_ik | END**

> "the earning surprise that the riff portfolio"
**Source GPS: LQvv5xgy_ik | END**

> "the five point of the risk protocol that I use in all environment of trading"
**Source GPS: LQvv5xgy_ik | END**

## 3.6 Ambiguity flags
- Row 6: the transcript says "The goal of the hedge fund is to optimize for maximum risk" (not extracted as a row); the next sentences say they take "the minimum possible amount of risk". Not resolved.
- Row 16: "you go in the low variance and you lose" - likely means high variance; not corrected.
- Row 44: "the 68 and 22%" - the 68 has no unit; the 22% maximum drawdown is stated.
- Row 28: "a maximum drawdown 0.42" has no unit; "net profit of 54.6%" is as transcribed.
- Row 54: "it should be 1.25%, 0.5% per trade" - the first figure may be mistranscribed; not corrected.
- Row 7: "30%, of 20, of 18" - fund drawdown figures are spoken in a hesitating way.
- Row 29: a drawdown "10 times this" is spoken as a possibility, not a measured figure.
- Row 50: "650 execution" is hedged by "if I'm not wrong".

## 7 self-check
1 ENTRY rows: 0; trade blocks: 0 (no trade in the video). 2 Fields filled. 3 Last row pos% 99. 4 Checker line below.

PASS: 0 problem(s)
