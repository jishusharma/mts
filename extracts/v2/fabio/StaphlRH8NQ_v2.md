# V2 extract StaphlRH8NQ (Fabio; five structural edges and trading models)

Method: EXTRACTION_METHOD_V2.md. Read in 9 chunks of about 2,000 characters, start to end. The video is a lecture of five edges
with academic references and test charts. No live trade is taken and no chart with a live position is shown. The five models are
recorded as illustration blocks only, with the rows he states. No initial stop is stated for any model.

## 3.1 Header
```
video_id: StaphlRH8NQ
trader: Fabio (Fabio Valentini, per the task; the transcript says "Some know me as a professional scalper" and names no name)
title: unknown (the raw file has no header line; the first line is the caption "[0:00] In this video, I will show you five of")
instrument_stated: stocks (earnings drift; politician tracking), Nasdaq (opening range test), S&P 500 (buy and hold benchmark for the politician test), out-of-the-money options (underlying not stated), Bitcoin (smart DCA)
instrument_inferred: none
tick_size: unknown
session / time of day: "the first 30 minutes of a regular cash trading" (initial balance definition, model 2); other models unknown
translation_warning: yes (auto-captioned: [m:ss] and [music] markers; garbled terms such as "PAAD", "IVB", "battle of the first 30 minutes")
body_chars: 17391
n_decision_rows: 33
n_trades: 0 (5 illustration blocks, one per model; no trade with a stated initial stop)
```

## 3.2 Decision log
| # | pos% [time] | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 [0:07] | REJECT | - | vague concepts, geometric shapes | kind of edge | "talking about some vague concepts or geometric shapes" | - | wants "repetitive and predictable behavior" documented by academic research |
| 2 | 10 [1:48] | CONTEXT | - | five models | the model list | "Two long-term models on the stock market" | - ; list: 2 long-term stock, 1 intraday equities, 1 option, 1 crypto smart DCA | none stated |
| 3 | 12 [2:07] | REJECT | - | single strategy / single guru | retail habit | "retail traders that typically only trust one strategy, one model, and one guru" | - | reason: if it "stops working tomorrow" -> "panic, strategy hope, revenge trading" [music tag inside the sentence] |
| 4 | 14 [2:30] | LESSON | - | - | diversified models | "If instead you use many and diversified models" | - | none stated |
| 5 | 19 [3:16] | REJECT | - | guru performance | who to copy | "Instead of trying to replicate the performance of your favorite guru, or trust blindly" | - | replace with research and validation |
| 6 | 21 [3:41] | LESSON | - | - | validation | "you should research and you should validate what you are applying" | - | none stated |
| 7 | 27 [4:36] | LOCATION | long (positive surprise); negative surprise drifts down, side not stated as a trade | earnings beat by "40, 50, 60%" | earnings surprise | "one stock beat the expectations in the earnings by two, three times, by 40, 50, 60%" | news (earnings) | none stated |
| 8 | 29 [4:59] | CONTEXT | - | institutional execution | how the information is priced in | "one alpha execution method ... is the VWAP" | VWAP (institutions' algorithmic accumulation, not his entry rule) | none stated |
| 9 | 33 [5:37] | HOLD | long (drift upward) | post-earnings drift window | drift length | "continue to drift upward for up to 60 days" | news (earnings) | "up to 60 days"; negative surprise stocks "drift downwards" |
| 10 | 40 [6:43] | LESSON | - | - | spread chart | "the spread is 4%, okay? And for 60 days, 4% in a single stock it's a lot" | - | none stated |
| 11 | 45 [7:31] | CONTEXT | long | stocks, upside skew | structural drift | "the stocks have an upside skew and they have a structural drift" | time of day (first 30 minutes) | none stated; "battle" [?] as transcribed |
| 12 | 49 [8:10] | LOCATION | - | initial balance high and low (first 30 minutes of regular cash trading) | opening range | "the high and low price established during the first 30 minutes" | time of day (first 30 minutes), swing high/low (range high and low) | none stated |
| 13 | 50 [8:16] | CONTEXT | - | first half hour | volatility contraction then volume | "Volatility contraction during this first half hour often revolves in explosive volume" | market speed / volume [new source: volume of the opening range] | none stated |
| 14 | 53 [8:52] | ENTRY (illustration) | long (tested case) | breakout above the initial balance | session after a close above the breakout | "the breakout that close above this breakout" | bar close (timeframe not stated; "close above this breakout") | close above the breakout; test run "without order flow, without option flow, without logic of the strategy confirmation"; order type unknown |
| 15 | 54 [9:08] | TARGET_SET (illustration) | long (tested case) | - | test geometry | "the risk to reward okay of one of one measuring the same amount" | - | stated R:R one-to-one; skew "13.5%" of being right; initial stop not stated |
| 16 | 56 [9:25] | LOCATION | short | same range, short side | short side of the model | "you can take both side because you can also implement the short side" | option flow, gamma regime [new source] | "you should be able to analyze the gamma regime" |
| 17 | 61 [10:03] | ENTRY (illustration) | long or short (direction from the research, side not fixed) | after direction is validated | timing of the entry | "timing my entry with order flow and option flow for directional pressure" | order flow (unspecified) [new source: no detail], option flow [new source] | direction first (validated by statistical research), then entry timing; order type unknown; before or after proof unknown |
| 18 | 62 [10:19] | LOCATION | - | stocks in the sectors of the committees they sit on | politician trades | "trade stocks in sector directly impacted by committees they sit on" | [new source] politicians' disclosed trades | none stated |
| 19 | 66 [10:56] | CONTEXT | - | - | disclosure rule | "mandates trade disclosure within 45 days" | [new source] regulatory filings | none stated |
| 20 | 67 [11:01] | ENTRY (illustration) | not stated (copies their disclosed trades; they trade calls on tech per "leverage call options") | most active and powerful committee members | who to copy | "Copy trading the most active and powerful committee members" | [new source] regulatory filings | order type unknown; before or after proof unknown (the entry follows a disclosure) |
| 21 | 68 [11:16] | LESSON | - | - | test sample | "to avoid cherry-picking the politician, we test Nancy Pelosi, Brian Higgins, and Mark Green" | - | none stated |
| 22 | 74 [12:18] | LESSON | - | - | delay | "even if there is this delay of 45 days" | - | none stated |
| 23 | 76 [12:41] | ENTRY (illustration) | short (sell options) | out-of-the-money options | premium | "the systematic selling of out-of-the-money option" | [new source] implied volatility vs realized volatility | order type unknown; strike, expiry, size not stated |
| 24 | 78 [12:51] | CONTEXT | short (sell options) | implied vs realized volatility | volatility premium | "implied volatility, IV, is structurally higher than ex-post realized volatility" | [new source] implied volatility vs realized volatility | none stated |
| 25 | 80 [13:14] | LESSON | short (sell options) | - | tail risk | "compensation for taking on tail risk because markets are crash phobic" | - | caution stated: the premium pays for tail risk; no stop or hedge stated |
| 26 | 83 [13:38] | CONTEXT | short (sell options) | last 12 months test | implied vs realized | "realized volatility it's more often than not lower than implied volatility" | [new source] implied volatility vs realized volatility | none stated |
| 27 | 88 [14:31] | LESSON | long | - | his own model | "multiple set of mathematical condition before pressing buy and before selling the Bitcoin" | - | conditions not disclosed |
| 28 | 89 [14:40] | CONTEXT | long | buy and hold | drawdown of the alternative | "buy and hold strategy expose investor to maximum drawdown exceeding 80%" | - | none stated |
| 29 | 90 [14:53] | LOCATION | long | capitulation zone by the MVRV zeta score | on-chain cycle | "the MVRV zeta score to identify macro market cycles" | [new source] MVRV zeta score (market value vs realized value), on-chain data | none stated; the score thresholds are not stated |
| 30 | 91 [14:58] | ENTRY (illustration) | long | capitulation | MVRV zeta score | "buying heavily at capitulation" | [new source] MVRV zeta score | size dynamic; order type unknown; before or after proof unknown |
| 31 | 91 [15:00] | PARTIAL (illustration) | long | euphoria | MVRV zeta score | "reducing risk gradually at euphoria" | [new source] MVRV zeta score | gradual reductions; sizes not stated |
| 32 | 92 [15:12] | CONTEXT | - | big holders | whale behaviour | "you can monitor this by checking their holding activity" | [new source] on-chain holdings of large wallets | none stated |
| 33 | 99 [16:21] | LESSON | - | - | closing message | "the importance of starting with an hypothesis" | - | none stated |

## 3.3 Trade blocks
No trade was taken or shown. Five illustration blocks, one per model, built from the rows he states. In every block: initial stop = no stop stated;
open profit on the clock = none shown; mirror stated?: no - do not assume (model 2 states both sides, see its block).
```
ILLUSTRATION 1 - earnings surprise drift - rows 7-10 (stocks)
state (day/week): not stated ; sudden change in information, a stock beats earnings by "40, 50, 60%" (row 7)
location: positive earnings surprise ; level type: other (news event, not a price level)
leading signal: earnings surprise ; trigger: not stated ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown (no ENTRY row: he states no entry timing)
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: no target stated ; hold window "up to 60 days" (row 9) ; stated R:R: unknown
management: none stated
exit: not stated ; exit type: unknown
rejects: none in this model
information sources: news (earnings), VWAP (institutional execution, row 8, not his entry rule)
outcome: sample spread "4%" over 60 days (row 10)
horizon: "up to 60 days"
mirror stated?: partly - negative surprise stocks "drift downwards" (row 9); no short trade is described

ILLUSTRATION 2 - initial balance / opening range breakout - rows 11-17 (Nasdaq test; stocks)
state (day/week): stocks have an "upside skew" and a "structural drift" in the first 30 minutes (row 11)
location: high and low of the first 30 minutes of regular cash trading ; level type: other (opening range high/low)
leading signal: "Volatility contraction during this first half hour" then "explosive volume" (row 13)
trigger: a close above the breakout (row 14) ; entered BEFORE or AFTER proof: unknown (direction is validated first, then entry is timed with order flow and option flow, row 17)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: the test uses a reward equal to the risk, "one of one" (row 15) ; distance: unknown ; stated R:R: 1:1
management: none stated
exit: not stated (the test measures "the session after the breakout") ; exit type: unknown
rejects: none in this model; the 13.5% skew is measured "without order flow, without option flow" (row 14)
information sources: time of day, bar close (TF not stated), swing high/low (range), order flow [new source: no detail], option flow [new source], gamma regime [new source]
outcome: "skew of 13.5%" of being right in the one-to-one test (row 14)
horizon: the rest of the session
mirror stated?: yes - short side "that is more strong" but needs the gamma regime (row 16)

ILLUSTRATION 3 - politician tracking - rows 18-22 (stocks)
state (day/week): not stated
location: stocks in the sectors of the committees they sit on ; level type: other (not a price level)
leading signal: disclosure of a politician's trade ; trigger: copy of the disclosed trade (row 20) ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: no target stated ; stated R:R: unknown
management: none stated
exit: not stated ; exit type: unknown
rejects: none in this model
information sources: [new source] regulatory filings (disclosure within 45 days, row 19)
outcome: equity line compared with S&P 500 buy and hold, Pelosi "the best performer" (shown on a chart, no numbers stated here); family portfolio "54% gain in 2024 and a 65% gain in 2023"
horizon: delay of 45 days between release of the information and the price result (row 22)
mirror stated?: no - do not assume

ILLUSTRATION 4 - option premium harvesting - rows 23-26 (options; underlying not stated)
state (day/week): not stated
location: out-of-the-money options ; level type: other (strike not stated)
leading signal: implied volatility above realized volatility (row 24) ; trigger: systematic, no trigger stated ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: premium collected ("collect a persistent yield") ; distance: unknown ; stated R:R: unknown
management: none stated
exit: not stated ; exit type: unknown
rejects: none in this model
information sources: [new source] implied volatility vs realized volatility
outcome: last 12 months, realized volatility "more often than not lower than implied volatility" (row 26)
horizon: unknown
mirror stated?: no - do not assume (he states a caution: tail risk, row 25)

ILLUSTRATION 5 - smart DCA with the MVRV zeta score - rows 27-32 (Bitcoin)
state (day/week): market cycle by the MVRV zeta score
location: "capitulation" (buy) and "euphoria" (reduce) ; level type: other (indicator zone)
leading signal: the MVRV zeta score (row 29) ; trigger: capitulation (row 30) ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: no price target stated ; allocation reduced gradually at euphoria (row 31) ; stated R:R: unknown
management: PARTIAL row 31 (gradual reduction at euphoria); size adjusted dynamically (row 29)
exit: not stated beyond the gradual reduction ; exit type: unknown
rejects: none in this model; the alternative buy and hold has a drawdown "exceeding 80%" (row 28)
information sources: [new source] MVRV zeta score, on-chain data, large holders' holding activity (row 32)
outcome: equity line of the dynamic model vs static DCA vs buy and hold (chart, no numbers stated)
horizon: unknown
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 1: talking about some vague concepts or geometric shapes ; reason/condition: wants "repetitive and predictable behavior" documented by academic research
- Row 3: retail traders that typically only trust one strategy, one model, and one guru ; reason/condition: reason: if it "stops working tomorrow" -> "panic, strategy hope, revenge trading" [music tag inside the sentence]
- Row 5: Instead of trying to replicate the performance of your favorite guru, or trust blindly ; reason/condition: replace with research and validation
- Row 9 (HOLD): "up to 60 days"; negative surprise stocks "drift downwards"
- Row 11 (CONTEXT): none stated; "battle" [?] as transcribed
- Row 14 (ENTRY (illustration)): close above the breakout; test run "without order flow, without option flow, without logic of the strategy confirmation"; order type unknown
- Row 15 (TARGET_SET (illustration)): stated R:R one-to-one; skew "13.5%" of being right; initial stop not stated
- Row 16 (LOCATION): "you should be able to analyze the gamma regime"
- Row 17 (ENTRY (illustration)): direction first (validated by statistical research), then entry timing; order type unknown; before or after proof unknown
- Row 20 (ENTRY (illustration)): order type unknown; before or after proof unknown (the entry follows a disclosure)
- Row 23 (ENTRY (illustration)): order type unknown; strike, expiry, size not stated
- Row 25 (LESSON): caution stated: the premium pays for tail risk; no stop or hedge stated
- Row 27 (LESSON): conditions not disclosed
- Row 29 (LOCATION): none stated; the score thresholds are not stated
- Row 30 (ENTRY (illustration)): size dynamic; order type unknown; before or after proof unknown
- Row 31 (PARTIAL (illustration)): gradual reductions; sizes not stated

## 3.5 Verbatim anchors
> "talking about some vague concepts or geometric shapes that I cherry-picked from another charts"
**Source GPS: StaphlRH8NQ | BEGIN**

> "Two long-term models on the stock market"
**Source GPS: StaphlRH8NQ | BEGIN**

> "unlike retail traders that typically only trust one strategy, one model, and one guru"
**Source GPS: StaphlRH8NQ | BEGIN**

> "If instead you use many and diversified models, you will be more independent in changes"
**Source GPS: StaphlRH8NQ | BEGIN**

> "Instead of trying to replicate the performance of your favorite guru, or trust blindly"
**Source GPS: StaphlRH8NQ | BEGIN**

> "you should research and you should validate what you are applying"
**Source GPS: StaphlRH8NQ | BEGIN**

> "maybe one stock beat the expectations in the earnings by two, three times, by 40, 50, 60%"
**Source GPS: StaphlRH8NQ | BEGIN**

> "one alpha execution method that I was also discussing with Freddy, one ex-market maker, is the VWAP"
**Source GPS: StaphlRH8NQ | BEGIN**

> "stock with high standardized unanticipated earning continue to drift upward for up to 60 days, while negative surprise stocks drift downwards"
**Source GPS: StaphlRH8NQ | BEGIN**

> "the spread is 4%, okay? And for 60 days, 4% in a single stock it's a lot"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "the stocks have an upside skew and they have a structural drift of the battle of the first 30 minutes"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "Volatility contraction during this first half hour often revolves in explosive volume confirmed directional breakout runs that hold strong predictive power for the rest of the session"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "measuring the session after the breakout that close above this breakout, it's already blindly without order flow, without option flow, without logic of the strategy confirmation 13.5%"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "with the risk to reward okay of one of one measuring the same amount"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "you can take both side because you can also implement the short side okay that is more strong but you should be able to analyze the gamma regime"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "Getting a direction validated by statistical research and then timing my entry with order flow and option flow for directional pressure"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "Member of Congress frequently trade stocks in sector directly impacted by committees they sit on"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "the Stock Act of 2012 mandates trade disclosure within 45 days"
**Source GPS: StaphlRH8NQ | MIDDLE**

> "Copy trading the most active and powerful committee members create a structural alpha edge"
**Source GPS: StaphlRH8NQ | END**

> "to avoid cherry-picking the politician, we test Nancy Pelosi, Brian Higgins, and Mark Green portfolio"
**Source GPS: StaphlRH8NQ | END**

> "this edge can be taken as a structural alpha even if there is this delay of 45 days between the release of the information and the actual result of the price"
**Source GPS: StaphlRH8NQ | END**

> "option premium harvesting is the systematic selling of out-of-the-money option to capture the volatility risk premium"
**Source GPS: StaphlRH8NQ | END**

> "implied volatility, IV, is structurally higher than ex-post realized volatility"
**Source GPS: StaphlRH8NQ | END**

> "The risk premium is a structural compensation for taking on tail risk because markets are crash phobic"
**Source GPS: StaphlRH8NQ | END**

> "realized volatility it's more often than not lower than implied volatility"
**Source GPS: StaphlRH8NQ | END**

> "that is based on multiple set of mathematical condition before pressing buy and before selling the Bitcoin"
**Source GPS: StaphlRH8NQ | END**

> "standard buy and hold strategy expose investor to maximum drawdown exceeding 80%"
**Source GPS: StaphlRH8NQ | END**

> "value, the MVRV zeta score to identify macro market cycles and adjust allocation size dynamically"
**Source GPS: StaphlRH8NQ | END**

> "buying heavily at capitulation and reducing risk gradually at euphoria"
**Source GPS: StaphlRH8NQ | END**

> "reducing risk gradually at euphoria"
**Source GPS: StaphlRH8NQ | END**

> "you can monitor this by checking their holding activity"
**Source GPS: StaphlRH8NQ | END**

> "the important of diversification and the importance of starting with an hypothesis"
**Source GPS: StaphlRH8NQ | END**

## 3.6 Ambiguity flags
- Row 11: "battle of the first 30 minutes" [?] is probably a mis-caption of "drift"; the transcript also says "the IVB", "the initial volume breakout or the initial balance drift" (initial volume breakout vs initial balance breakout unclear). Not resolved.
- Row 14: "skew of 13.5%" is stated twice; whether 13.5% is an edge over 50% or a win rate is not stated.
- Row 15: "of one of one" is the stated risk to reward; read as 1:1 only because "measuring the same amount" follows.
- Row 17: "order flow" and "option flow" are named without detail (which order-flow tool is not stated).
- Row 7: "the PAAD" is the caption for the post-earnings drift; the "[music]" tags appear inside sentences throughout.
- Row 20: "leverage call options" in the politician section describes their portfolio, not a trade he takes.
- Row 30: whether "buying heavily" is a lump-sum buy or accumulation in steps is not stated.

## 7 self-check
1 ENTRY rows (all illustration): 5 ; trade blocks: 0, 5 illustrations. 2 Fields filled; every block says no stop stated. 3 Last row pos% 99. 4 Checker line below.

PASS: 0 problem(s)
