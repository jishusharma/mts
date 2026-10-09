# V2 extract QClPWDJ-BrU (session 2026-10-09, jisnb/tom-extract-2026-10-09b)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked) + playbook Part J tiers on the derived rules (section 3.7).
Read in full, one chunk. Chart walk-through on the S&P 500: one day-trade plan (pre-session, 5-minute footprint + daily cash-session profiles) and one swing-trade plan (volume profile), then the expectancy math of both. Both trades are plans with entry, stop and target; "Which it did" is the only outcome stated (day trade, direction only).

## 3.1 Header
```
video_id: QClPWDJ-BrU
trader: Tom Vorwald (channel "Tom Vorwald EN"; first person, "25 Years of Trading Experience" in the title)
title: This is How You Actually Trade Profitably! (25 Years of Trading Experience)
instrument_stated: S&P 500 ("we'll do that now with the S&P 500 in day trading")
instrument_inferred: none
tick_size: unknown (prices quoted as 7,457 / 7,461 / 7,480; he says "points" then corrects to "dollars")
session / time of day: day trade in the pre-session ("before the market opens"); swing trade any time ("24 hours a day")
translation_warning: yes (auto-captioned, non-native English; "Entry 62, stop loss, I'll just make it 52" are the last two digits of 7,462 / 7,452 inferred, see 3.6)
body_chars: 14777
n_decision_rows: 20
n_trades: 2 (plans, no fill or exit shown)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 9 | CONTEXT | - | - | session | pre-session is risky "as liquidity isn't that high yet" but "things sometimes move faster" | time of day | "before the market opens" |
| 2 | 13 | CONTEXT | long | yesterday's profile | value area, single print, VPOC | single print = "a lot of buying"; "the market has upward pressure, especially since the VPOC has established itself at the top" | daily cash-session profiles (4 days) | none stated |
| 3 | 17 | CONTEXT | long | 7,457 / 7,461 | 5-minute footprint | at 7,461 "liquidity and also time start to be gathered again" | footprint, market profile | none stated |
| 4 | 19 | LESSON | long | yesterday's upper zone | liquidity above | the market "could move up since it had liquidity up there yesterday and markets love to play liquidity" | profile | none stated |
| 5 | 20 | TARGET_SET | long | about 7,480 | liquidity fade | follow the idea "Until the point where liquidity starts to fade again", "roughly in this area of 7,480" | profile | none stated |
| 6 | 24 | STOP_SET | long | below last swing low (52) | swing low | stop "below the last swing low where the market would then be below these price areas" | swing low | "very relaxed now without thinking too much" |
| 7 | 25 | ENTRY | long | entry 62, stop 52, target 80 | key figures | "$10 stop loss", "from 62 to 80 and so I have 18 points" | plan | none stated |
| 8 | 32 | CONTEXT | long | - | R:R | "18 divided by 10" = "1.8. That's a decent setup" | plan | "If we are accordingly well over 40% in the average win rate" |
| 9 | 41 | LESSON | - | - | volume profile | "the market likes to run from liquidity to liquidity" | volume profile of the price range | none stated |
| 10 | 44 | ENTRY | long | 7,443 limit buy | acceptance | order placed where the market "accepted the prices here again"; "I'll take this sideways phase as acceptance" | volume profile | "in swing trading you do not have the chance to be in the market all the time. You have to be patient" |
| 11 | 48 | TARGET_SET | long | 7,513 limit sell | next major level | exit "at the corresponding next major level", "just slightly below the corresponding volume levels" | volume profile | none stated |
| 12 | 53 | STOP_SET | long | 7,420 | last high-liquidity station | "Where was the last time there was high liquidity? And I'd position the stop-loss below that." | volume profile | "in hindsight, you always see" / "But that's not right." (do not pick the stop from hindsight) |
| 13 | 61 | CONTEXT | long | 7,443 / 7,420 / 7,513 | R:R | risk 23, profit 70, "3.04 times as large as the risk" | plan | none stated |
| 14 | 63 | LESSON | - | - | break-even win rate | at 3.04 R:R break even at "a theoretical win rate of 25%" | math | none stated |
| 15 | 73 | LESSON | - | - | expectancy | win rate 35% at 3.04: "0.414R per trade", 300 trades = "124.2R" | math | "over the last 500 trades" (win rate base) |
| 16 | 83 | LESSON | - | - | expectancy | day trade at 1.8: break even "35.71%"; at 50% win rate "0.4R per trade", 300 trades = "120R" | math | none stated |
| 17 | 84 | LESSON | - | - | target distance | probability of reaching target "significantly higher" for the day trade (less time, less distance) | - | none stated |
| 18 | 87 | LESSON | - | - | model choice | swing earns "a bit more money with the swing trading approach, even with a much lower win rate" and needs less time and focus | math | none stated |
| 19 | 92 | LESSON | - | - | drawdown | swing model: "the sequence of your losers is naturally larger", drawdowns "a bit larger with the same position size" | - | "with the same position size" |
| 20 | 97 | LESSON | - | - | session liquidity | day trading needs selecting "when there's actually enough liquidity in the market"; swing "with appropriate limits" | time of day | none stated |

## 3.3 Trade blocks
Trade A (day trade plan, long, S&P 500, pre-session, 5-minute footprint)
- Context: yesterday's cash-session profile with VPOC at the top and a single print (rows 2-4).
- Entry: 62 (7,462 inferred). Stop: 52 (7,452 inferred), "below the last swing low". Target: 80 (about 7,480), where liquidity fades.
- R:R: 18 / 10 = 1.8 (his number). Outcome: "the market will push upwards. Which it did." No exit shown.

Trade B (swing trade plan, long, S&P 500, volume profile)
- Entry: 7,443 limit buy, in the sideways phase taken as acceptance. Stop: 7,420, below the last high-liquidity station. Target: 7,513 limit sell, just below the next major volume level.
- R:R: 70 / 23 = 3.04 (his number; 70/23 = 3.043). Outcome: not shown.

## 3.4 Rejections and conditions
- Row 12 (REJECT of a method): placing the stop from hindsight ("I could put it here and what have you") is "not right"; the stop goes below the last high-liquidity station.
- Row 8 condition: 1.8 R:R is "a decent setup" only "If we are accordingly well over 40% in the average win rate" and "Provided the market conditions remain favorable".
- Row 1 condition: pre-session liquidity "isn't that high yet"; row 20: day trading needs choosing times with enough liquidity.
- Row 10 condition: swing entries need patience; a limit order waits at the acceptance area.

## 3.5 Verbatim anchors
> "I've deliberately chosen a pre-session."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "That shows me that the probability is higher for now that the market has upward pressure, especially since the VPOC has established itself at the top."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "since it had liquidity up there yesterday and markets love to play liquidity."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "Until the point where liquidity starts to fade again. And that's roughly in this area of 7,480."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "place it below the last swing low where the market would then be below these price areas."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "Entry 62, stop loss, I'll just make it 52 now and so we have a $10 stop loss."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "If we are accordingly well over 40% in the average win rate."
**Source GPS: QClPWDJ-BrU | BEGIN**

> "I'll just claim now that the market likes to run from liquidity to liquidity."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "So it's within this whole structure and says, yes, I'll take this sideways phase as acceptance."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "Entry 7443 via limit buy."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "That is sitting just slightly below the corresponding volume levels that the market had clearly shown us here on the left side of the chart."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "Where was the last time there was high liquidity?"
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "The trade has an entry at 7,443, stop loss 7,420, take profit 7,513."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "This results in a reward that is 3.04 times as large as the risk."
**Source GPS: QClPWDJ-BrU | MIDDLE**

> "the expected value per trade, which many don't calculate because they mix things up, is 0.414R per trade."
**Source GPS: QClPWDJ-BrU | END**

> "A theoretical win rate of 35.71% would be enough to break even."
**Source GPS: QClPWDJ-BrU | END**

> "the sequence of your losers is naturally larger than in the swing trading approach."
**Source GPS: QClPWDJ-BrU | END**

## 3.6 Ambiguity flags
- Trade A prices: he says "Entry 62", "52", "from 62 to 80" right after naming 7,457 / 7,461 / 7,480, so 7,462 / 7,452 / 7,480 is inferred, not stated.
- Row 7: "18 points that I sorry, dollars": unit corrected by him; S&P points vs dollars per contract not resolved.
- Row 19: "the sequence of your losers is naturally larger than in the swing trading approach" is said while describing the swing model; he contrasts swing vs day, so read as larger in swing than in day trading. Caption slip, meaning taken from the next sentence ("would be a bit larger with the same position size").
- Row 14: he says "25%" and later "nearly 25%"; the formula 1/(1+3.04) = 24.75% agrees with "nearly 25%".
- Math check (independent, FORMULAS-style: break-even win rate = 1/(1+R), EV = p*R - (1-p)): 1/(1+1.8) = 35.71% (matches); 0.35*3.04 - 0.65 = 0.414R (matches); x300 = 124.2R (matches); 0.5*1.8 - 0.5 = 0.4R, x300 = 120R (matches).
- Row 15: the win-rate base is "the last 500 trades" while the R:R base and the projection are 300 trades; mixed as stated.

## 3.7 Candidate rules, with provenance and the Naked BTC chart test
Tier = playbook Part J (T1 example, T2 self-check, T3 calculation, T4 recommendation, T5 command). Location tag = [T/id:file line@char offset in the raw file].

R-QClP-1 | T1 (example) | Long bias when yesterday's profile has its VPOC at the top of the value area plus a single print below (buying); look for the market to revisit yesterday's upper high-volume zone.
- Source: [T/QClPWDJ-BrU:7@2104] ; [T/QClPWDJ-BrU:7@2895]
- Naked BTC chart test: yes in part. A daily volume profile (VPOC, value area) is computable from candle volume per price; "single print" needs a TPO/market profile (30-minute letters), computable from 30-minute candles. VPOC at the top has no numeric definition (which fraction of the range): NO-SOURCE.

R-QClP-2 | T1 (example) | Target = where liquidity starts to fade (next high-volume level), set just below it.
- Source: [T/QClPWDJ-BrU:7@2996] ; [T/QClPWDJ-BrU:7@7343]
- Naked BTC chart test: yes. Next volume-profile high-volume node above entry is computable. "slightly below" has no distance: NO-SOURCE.

R-QClP-3 | T1 (example) | Stop below the last high-liquidity station (swing) or below the last swing low (day); never chosen from hindsight.
- Source: [T/QClPWDJ-BrU:7@7899] ; [T/QClPWDJ-BrU:7@3606]
- Naked BTC chart test: yes. Last high-volume node below entry / last swing low are computable; the buffer below is not given (NO-SOURCE). Swing-low definition (pivot length) not given: NO-SOURCE.

R-QClP-4 | T1 (example) | Swing entry by limit buy inside a sideways phase that price re-entered after leaving it ("acceptance").
- Source: [T/QClPWDJ-BrU:7@6524] ; [T/QClPWDJ-BrU:7@6980]
- Naked BTC chart test: partly. A sideways phase and re-entry are visible on a bare chart, but no length or width defines it: NO-SOURCE.

R-QClP-5 | T3 | Calculation: break-even win rate = 1/(1+R:R); EV per trade = win% x R:R - loss%. His numbers: 3.04 -> nearly 25%, 1.8 -> 35.71%; 35% at 3.04 -> 0.414R; 50% at 1.8 -> 0.4R.
- Source: [T/QClPWDJ-BrU:7@12276] ; [T/QClPWDJ-BrU:7@10824]
- Naked BTC chart test: not chart-observable (backtest statistic). Usable as a check on our own trade list.

R-QClP-6 | T4 | A 1.8 R:R setup needs a win rate "well over 40%"; the swing model is aimed at R:R "consistently greater than three".
- Source: [T/QClPWDJ-BrU:7@4903] ; [T/QClPWDJ-BrU:7@13934]
- Naked BTC chart test: not chart-observable. "40%" is above his own break-even 35.71%, a margin he states without a rule.

R-QClP-7 | T4 | Day-trade only when there is enough liquidity in the market; pre-session is riskier because liquidity is low.
- Source: [T/QClPWDJ-BrU:7@1555] ; [T/QClPWDJ-BrU:7@14416]
- Naked BTC chart test: partly (session volume is computable), but no threshold or session window is given for BTC: NO-SOURCE.

Rules with parameters and no source: none in this file. Not found in this video: position size, trade management after entry.

## 3.8 Self-check
- Last decision row pos% >= 90: row 20 is the last decision; the closing lines have none.
- Terms CT / TC / trend_healthy / tier: tier appears only in section 3.7, as the playbook Part J tiers.
- Gate result is pasted at the end of the file after the run.

## Gate result (2026-10-09)
```
verify_extract_quotes.py: PASS: 0 problem(s) (17 anchors)
inline quoted fragments: all verbatim (extract_fix_gps.py)
```
