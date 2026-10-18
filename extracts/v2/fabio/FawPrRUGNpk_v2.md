# V2 extract FawPrRUGNpk (Fabio, liquidity heat map lecture plus live NASDAQ session read)

Method: EXTRACTION_METHOD_V2.md. Read in 28 chunks of about 2,000 characters (offsets 0 to 54,000), start to end.
Video type: teaching lecture on the liquidity heat map (patterns shown on recorded examples), then a live read of one NASDAQ session (4 May 2026). No trade is opened on camera: every ENTRY / STOP_SET / TARGET_SET row below is an illustration or a hypothetical ("if I took a short from here"). Whole video = zero executed trades, so no winner or loser exists to record.

## 3.1 Header
```
video_id: FawPrRUGNpk
trader: Fabio (Fabio Valentini, per task brief; the transcript never says his name)
title: unknown (the raw file has no header line)
instrument_stated: NASDAQ ("I scalp and day traded the NASDAQ over the last years"; "all these levels here on the Nasdaq"; price levels 27,625 to 27,940 are shown on the NASDAQ chart)
instrument_inferred: none
tick_size: unknown
session / time of day: live read on "the 4th of May, 2026", "on Monday", "the New York session"; levels "mark after the opening of the session"
translation_warning: no flag in the text (auto-captioned English; caption noise such as "view up" for VWAP, "CBD" for CVD, "cover" for stop)
body_chars: 54989 (no "# ---" header; whole file, including [m:ss] markers)
n_decision_rows: 82
n_trades: 0 (5 illustrations / hypotheticals; none executed on camera)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | LESSON | - | - | order flow | "If there is one thing you need to know as a trader, is liquidity" | - | none stated |
| 2 | 4 | CONTEXT | - | above the high / below the low | retail stop liquidity | "This is not wrong, but it's only accurate 60 to 70% of the time" | swing high/low | retail liquidity "resting above the high and below the low in a compression phase" |
| 3 | 12 | LESSON | - | - | passive vs aggressive order | "you have price certainty, but not time certainty and not execution certainty" | order book / big orders | none stated |
| 4 | 13 | LESSON | - | 5 price levels: 273 above, 122 below | passive orders each side | "In this case, the path of least resistance is down" | order book / big orders | "fixing the effort" (same aggressive effort); fewer passive orders on one side = easier move |
| 5 | 16 | LESSON | - | heat map vs order book | liquidity heat map | "you have an historical DOM" | order book / big orders | none stated |
| 6 | 17 | LESSON | long | consolidation | bid reload (110 contracts appear) | "there is someone really big that want to be filled on the long" | order book / big orders | "in a consolidation phase, compression phase"; "the algorithm of the market" will front run it |
| 7 | 18 | LESSON | - | - | bid reload | "this pattern here it's used a lot by the spoofing" | order book / big orders | caution: a displayed big order can be spoofing (placed without intent to fill) |
| 8 | 19 | LESSON | long | bid reload | bid reload vs bias | "Seeing this kind of information is an amazing information to validate your idea" | order book / big orders | "you have a bias long and you want to go long till this level" |
| 9 | 20 | LESSON | - | iceberg | reload of a small displayed size | "You need specific indicator for it, an iceberg indicator" | order book / big orders; [new source] iceberg indicator (algorithmic reload detector) | none stated |
| 10 | 22 | LESSON | - | all-time high/low of the range, session high | book sweeping (fast movement) | "You can risk few ticks to get a really good risk to reward multiplier" | order book / big orders, market speed, swing high/low | "really close to all-time high, all-time low of the range" or "the high of the New York session"; "if you are positioned" |
| 11 | 23 | STOP_MOVE (illustration) | short | trail behind the broken level | book flip (liquidity level broken, then reloaded) | "you can trail your stop loss here" | order book / big orders | already "on the short side"; "You see the break through of this level of liquidity"; "they reload the level of liquidity"; new level not priced |
| 12 | 23 | ADD (illustration) | short | same | book flip | "you can also add other contract" | order book / big orders | "they are confirming you that they want to go down" |
| 13 | 25 | LOCATION (illustration) | long | protection wall of the buyers | resting liquidity absorbed three times | "This is the mean reverting on the protection wall of the buyers in line with the main direction" | order book / big orders, absorption | "You need to start with an idea"; long bias with a setup; "resting liquidity, is not fresh liquidity" |
| 14 | 25 | PROOF (BEFORE entry, taught for scalpers) | long | near resting liquidity | big trades plus buyers reloading | "you want to see maybe big trades confirming that there is an aggression there" | delta / aggressive buyers, order book / big orders | "you are really close to a resting liquidity level and you see the buyers reloading passive liquidity and getting aggressive" |
| 15 | 26 | ENTRY (illustration) | long | the breakout of the resting level | reload plus aggression, "break break and retest" | "you can enter at the breakout protected below the reload level" | order book / big orders, delta / aggressive buyers | "you have a directional bias, a probability directional bias"; order type unknown; entered AFTER proof (reload and aggression seen first) |
| 16 | 27 | STOP_SET (illustration) | long | below the reload level | reload level | "protected below the reload level" | order book / big orders | no stop distance stated |
| 17 | 27 | TARGET_SET (illustration) | long | major liquidity areas, then other resting liquidity | resting liquidity above | "the first take profit on the major liquidity areas and the second and third take profit on other resting liquidity area" | order book / big orders | three take-profits, no size split stated |
| 18 | 27 | CONTEXT | - | - | bias source | "you need to start with a directional bias and a probability framework that comes from the order flow" | order flow (unspecified) | precondition for the reload-breakout setup |
| 19 | 28 | PROOF | short | resting buyer area, sellers breaking | seller reload | "this is the ultimate confirmation you need because you can see that they get aggressive" | delta / aggressive sellers, order book / big orders | "at the same time they reload fresh liquidity"; no entry stated (BEFORE/AFTER unknown) |
| 20 | 30 | LESSON | - | next liquidity cluster (close) | confirmation respected four more times | "the risk to reward is not the best, but the confirmation that you get here gets respected for four additional times" | order book / big orders, absorption | "the price usually goes to the next liquidity cluster"; here the next cluster "was really close" |
| 21 | 30 | CONTEXT | long | - | bias list | "let's say that you are in a directional bias long for the day" | prior-day profile / today's profile (volume profile), VWAP ("the view up" [?]), [new source] IVB, [new source] statistical pivot projection | bias comes from "anything that gives you the probability that from this area you are going to rebound" |
| 22 | 31 | STOP_SET (illustration, no-heat-map version) | long | below the low | low | "I enter here and I cover below the low" | swing high/low | he introduces it as what you would do "if you don't have the heat map"; "cover" = stop [?] |
| 23 | 32 | PROOF (BEFORE entry) | long | main resting level plus extra wall | reload plus absorption | "the best play from a probability side here is to see the reload that they put reload plus absorption" | order book / big orders, absorption | there was "a main resting liquidity level, and there is also an additional liquidity wall" |
| 24 | 32 | ENTRY (illustration) | long | the area (stop sits below the next liquidity area) | liquidity walls under the entry | "you could decide to enter here, yes" | order book / big orders | order type unknown; placed before or after the reload is not stated |
| 25 | 32 | STOP_SET (illustration, heat-map version) | long | below the next liquidity area | second wall below | "put your stop loss below the next liquidity area" | order book / big orders | reason: "you are being careful of the market not taking you out during an accumulation phase"; no stop distance stated |
| 26 | 32 | TARGET_SET (illustration) | long | next liquidity area | liquidity above | "you have still an amazing risk to reward to the next liquidity area" | order book / big orders | R:R not given as a number |
| 27 | 34 | PARTIAL (illustration) | unknown | each liquidity level eaten (grill) | aggression slicing several stacked levels | "these are all partial profit that you can take" | order book / big orders, delta / aggressive buyers or sellers (direction not stated) | "the market usually reach a point of exhaustion here" at the cluster, "and then reverts"; credit to Eric Stokke for the "grill" pattern |
| 28 | 36 | PROOF | long | break of a resting liquidity level | aggressive breakout plus fresh reload | "an additional probability booster for a break and retest pattern to go above" | order book / big orders, delta / aggressive buyers, footprint | "at the same time, okay, they load resting liquidity fresh, and they get aggressive on the level"; vs bubble read alone = "potential absorption" |
| 29 | 37 | ENTRY (illustration) | long | the test (retest) of the broken level | price positive after the break | "I can enter on the test" | order book / big orders, delta / aggressive buyers | "let me see if the result of the price is positive"; order type unknown; entered AFTER proof (breakout and reload seen first) |
| 30 | 37 | STOP_SET (illustration) | long | below the wall reload | reload wall | "protect myself below the wall reload" | order book / big orders | no stop distance stated |
| 31 | 37 | TARGET_SET (illustration) | long | next liquidity level | liquidity above | "go to the next liquidity level, maybe for a 1:2 1:3 risk to reward" | order book / big orders | stated R:R "1:2 1:3" |
| 32 | 38 | PROOF | unknown | 27,625 and 27,630 (resting liquidity) | price tried to break through twice and was absorbed | "This is a strong confirmation that this is a filled auction" | absorption, order book / big orders | "the price will reverse for the path of least resistance"; side of the reversal not stated |
| 33 | 39 | LESSON | - | higher time frame | micro mechanics vs higher timeframe | "you always need a confirmation from the higher time frame on what's happening here" | [new source] higher-time-frame confirmation (TF not given) | "this is market micro mechanics" |
| 34 | 40 | CONTEXT | long | the opening | two pushes, each with fresh liquidity | "This means they wants to go up, they want to capitalize up" | order book / big orders, time of day (opening) | "they are not putting protective liquidity to protect this level, but they are going to put protective fresh liquidity to fuel the aggression on the way up"; "Stucky Grill" pattern |
| 35 | 41 | TARGET_SET (illustration) | long | final take profit area at the top of the liquidity stack | stacked liquidity above | "till they reach the final take profit in this area" | order book / big orders | illustration of a move, not a trader's position |
| 36 | 42 | REJECT | short | wall and absorption at the top | four stacked levels above the sellers | "you have an absorption on the top, you have a liquidity wall on the top and you will think to go short here" | order book / big orders, absorption, other market (NASDAQ) | reason: "a strong cluster of four levels stacked on each other way higher than this aggressive liquidity of the sellers"; "the highest probability here is that they will get a full fill" |
| 37 | 45 | LESSON | long | liquidity wall after sellers breach | break and protect | "this is a really high probability of going to the next liquidity" | order book / big orders, delta / aggressive sellers | "a breakout sustained breakout, it's sustained by a fresh liquidity" |
| 38 | 45 | STOP_MOVE (illustration) | unknown | break even | sustained breakout with fresh liquidity | "it's enough to put your position to break even" | order book / big orders | "if they start accumulating here and they come back, there is a high probability that they will reverse the market"; side not stated |
| 39 | 47 | LESSON | - | iceberg | iceberg detector | "this one is detecting the iceberg orders" | order book / big orders; [new source] iceberg indicator | none stated |
| 40 | 49 | LESSON | long | 27,875 (approx.) | distribution via three iceberg orders; iceberg filled before the displayed level | "the iceberg got filled completely on this level" | order book / big orders, absorption | "everyone that is scalping here will think, I will enter if I see an absorption here" but "the market never reached this level"; waiting at a far level can mean no fill |
| 41 | 51 | CONTEXT | - | - | live session | "we are now in live market environment on the 4th of May, 2026" | - | none stated |
| 42 | 52 | CONTEXT | - | 27,900 / 27,939-27,940 | accumulation read | "So, this one seems to me as an accumulation phase" | order book / big orders, absorption | "you have a major filling level on the 27,900 and 40, 939, 940" [numbers as transcribed] |
| 43 | 53 | PROOF | long | reload under the move | sellers absorbed, buyers aggressive, fresh resting liquidity | "when you have an absorption of the sellers and aggression of the buyers and they put a resting liquidity" | absorption, delta / aggressive buyers, order book / big orders | "fresh to protect and fuel the movement up"; no trade stated |
| 44 | 54 | LOCATION | - | 27,890 and 27,875 | two levels that "we could reach" | "the next level that they are going to target is this intermediate level that got created now on the 27,890" | order book / big orders | role: price destination read, not a stop or target |
| 45 | 56 | CONTEXT | long | 27,890 then 27,940 | battle on a horizontal level | "it seems from how the orders are unfolding that the sellers are losing the control of the situation" | order book / big orders, delta / aggressive buyers or sellers | if buyers break 27,890 the next is "the main level of liquidity that is the 27,940" ("the grill") |
| 46 | 58 | LESSON | - | - | real vs assumed liquidity | "The real liquidity is letting you really understand how the auction move" | order book / big orders | none stated |
| 47 | 60 | LESSON | - | bubble grouping setting | platform settings | "if you want to trade absorption and reversal, you can put this in the 70 to 75%" | absorption; [new source] bubble grouping setting | none stated |
| 48 | 63 | PROOF | long | 27,912 | buyers reloading fresh liquidity | "this is the first information that you can get that there is interest in continuation" | order book / big orders, delta / aggressive buyers | "The buyers try to push, the sellers protected, but the buyers reloaded"; "the next station" = next horizontal liquidity level |
| 49 | 65 | CONTEXT | - | origin of the move | range fair value | "The fair value of all this range, you can see here, is the origin of the move" | [new source] origin of the move as fair value | "the sellers trying to recover the movement on the way down ... push the market back to the fair value" |
| 50 | 67 | PROOF | long | break of the level, then reload | bid reload after the break | "And this is an amazing confirmation of the buyers wanting to continue the auction up and having a breakout movement" | order book / big orders, delta / aggressive buyers | "immediately after they break, they reload liquidity"; "If you see this one raising, means that they are willing to get filled at higher level"; "You don't have a guarantee that the fresh liquidity gets filled" |
| 51 | 67 | CONTEXT | long | 27,915 | squeeze of the high | "the highest probability is that we squeeze this high, we go on the top on the 27,915" | order book / big orders | role: expected price destination; if they break it and "other fresh liquidity" is added, "they want to fuel the movement up" |
| 52 | 69 | LESSON | - | take profit / partial reference | buyers find a ceiling | "this is important for take profit, for partial, can give you a lot of information of where you can take a decision of unloading a position" | order book / big orders | when "the buyers are not willing to get filled at higher levels" and "the resting liquidity and the fresh liquidity is not protecting the move up" |
| 53 | 71 | CONTEXT | long | 27,925 | most important level, break test | "So, from the heat map, we can see that one of the most important level is the 27,925" | order book / big orders | if broken: "I would like to see exactly the same that we saw here, breaking and loading liquidity" |
| 54 | 72 | CONTEXT | - | 27,895 | no hot resting liquidity at the break | "there is a probability that we will see a retracement of the market" | order book / big orders | "if they don't put anything anything else" [as transcribed]; "I don't see resting liquidity getting hot on the on this level" |
| 55 | 73 | LESSON | - | liquidity area | zones not lines | "it's not a level. It's always an area" | order book / big orders | "there are orders around it" |
| 56 | 74 | CONTEXT | long | above first VWAP standard deviation | CVD and VWAP | "Buyers are dominating this auction from the beginning of the session" | delta / aggressive buyers (CVD), VWAP ("view up" [?]), [new source] VWAP standard deviation band | "we are above the first standard deviation of the view up"; VWAP is "the fair value of the day"; horizontal volume added for "absorption on the vertical levels" |
| 57 | 77 | CONTEXT | - | - | news | "We just received a missile alert in the United Arab Emirates" | news | also "a news about Iran" later |
| 58 | 78 | PROOF | - | wall hit by sellers | first reaction on the wall | "You see the first reaction they see on the wall is this one, absorption" | absorption, order book / big orders | second touch: "the market have an immediate reaction"; side not stated |
| 59 | 80 | CONTEXT | long | the first level marked after the opening | original level | "Of course, today the bias was was on the long side" | time of day (level marked after the opening), order book / big orders | "This was the most important level that we had from the beginning of the session" |
| 60 | 82 | PROOF | - | original level, top | buyers absorbed on the top, sellers take control | "this is a perfect example of a reload" | absorption, delta / aggressive buyers and sellers | the sellers "eat this original level of liquidity" |
| 61 | 83 | CONTEXT | long | 27,915 (second level) | liquidity not removed | "so they still have a bias on the long side" | order book / big orders | "they didn't remove this liquidity"; they "are raising this liquidity, you see? Before was here, then it was here" |
| 62 | 84 | CONTEXT | long | next sensitive level above | sellers add passive liquidity | "this one is the next sensitive level with a high probability of getting filled" | order book / big orders | only "if they manage to break" the level in front |
| 63 | 86 | LESSON | long | main direction of the day | retracement inside a long-bias day | "even if your bias it's on the long side, you still have retracement on the main direction of the day" | order book / big orders | none stated |
| 64 | 87 | PROOF | short | - | CVD | "the CVD as you can see is flipping lower" | delta / aggressive sellers (CVD) | no entry stated |
| 65 | 88 | REJECT | long | - | sellers dominating | "I will not try to get long while the sellers are dominating the auction because it's a suicide" | delta / aggressive sellers, order book / big orders | "I will wait for the buyers to show me some kind of protection"; "I will not try reversal play" |
| 66 | 89 | LOCATION | long | liquidity level where price accepted above | fresh liquidity, potential reload | "from this level there is a high probability that you have a rebound" | order book / big orders, absorption | then "we see from here if the aggressive buyers have the power and the strength to go higher"; watched, no entry taken |
| 67 | 90 | CONTEXT | - | horizontal level in the blue area | flip of the auction | "you have a flip of the auction and you flip the bias of the day" | order book / big orders | "if they manage to break this horizontal level that still is getting protected in the blue area"; direction of the flip not stated |
| 68 | 90 | TARGET_SET (read, no trade) | - | 27,870 or 27,850 | levels below | "So, it means that your next target is the 27,870 or the 27,850" | order book / big orders | applies only after the flip row above; side word not stated; no entry or stop |
| 69 | 90 | CONTEXT | long | 27,910 | where buyers must show strength | "As of now, buyers are still protecting and the real battle is here on the 27,910" | order book / big orders | "This is where you can see if the buyers is are having enough strength to get aggressive on the level" |
| 70 | 90 | PROOF | long | - | CBD (as transcribed) stable while price rises | "CBD is stable, so there is no aggression of the buyers, but the market is going up" | delta / aggressive buyers (CVD, "CBD" as transcribed [?]) | "if we have a flip here and we see a buy aggression of the buyers, we could make a lot of points on the up" |
| 71 | 91 | PROOF | short | 27,900 | sellers show their hand; level filled completely | "Once they reach the 27,900, the sellers show their hand really aggressively" | delta / aggressive sellers, absorption, order book / big orders | "they filled completely the 27,900"; "Look at the order that got aggressive on this level and they broke the level" |
| 72 | 92 | PROOF | short | 27,900 | two seller reloads after the break | "Reload of the sellers number one, reload of the sellers number two" | order book / big orders, delta / aggressive sellers | "So they flipped the auction"; "they wants to get this horizontal level filled" |
| 73 | 93 | CONTEXT | short | 27,870 | auction destination | "The auction would go to the 27,870" | order book / big orders | role: expected destination |
| 74 | 93 | ENTRY (hypothetical) | short | from the seller reload area | seller reload after the break | "So if I took a short from here" | order book / big orders, delta / aggressive sellers | order type unknown; BEFORE or AFTER proof: after (reloads and break seen first); not actually taken on camera |
| 75 | 93 | TARGET_SET (hypothetical) | short | lower than the low (27,870 area) | low | "I would consider bringing my full take profit way lower than the low" | swing high/low, order book / big orders | full target, no partial stated; no stop stated |
| 76 | 94 | LESSON | - | - | volatility regime | "with the liquid heat map, you can predict with a high degree of accuracy which kind of volatility you could expect" | market speed; [new source] volatility regime read | he says "today was telling us that we were high volatility" |
| 77 | 95 | ENTRY (hypothetical) | unknown | at the touch of the rejected level 27,910 / 27,912 | absorption of buyers plus reload at the level where "the Nasdaq effort printed" | "with my confirmation I would have taken the first trade here" | absorption, order book / big orders, [new source] "Nasdaq effort" area [?] | side word not stated (targets are below: "TP1 and TP2"); order type unknown; AFTER proof ("the confirmation"); not taken on camera |
| 78 | 95 | LESSON | - | entry timing | confirmation vs executing blind | "you can be filled way lower if you don't know when to search for setups" | order book / big orders | "you don't know where there is the massive liquidity wall of the passive orders" |
| 79 | 97 | TARGET_SET (hypothetical) | unknown | 27,790 and a cluster below | liquidity below the touch | "So, we have TP1 and TP2 here" | order book / big orders | "This one got consumed, this one got consumed"; "27,790 that is super far"; no stop stated |
| 80 | 97 | CONTEXT | - | - | news | "this was also a news about Iran" | news | with the collapse "Nasdaq unfolded collapsing like this" |
| 81 | 98 | PROOF | unknown | second "Nasdaq effort" area | removed and lowered heat map level; reloads | "they are willing to get filled at lower levels" | order book / big orders, absorption, [new source] "Nasdaq effort" area [?] | "you see this amazing absorption, on top of this you see reload, reload, reload, reload"; "This is all fresh liquidity fueling the movement down" |
| 82 | 100 | LESSON | - | - | absorption and reload | "It's giving you a lot of confidence about when to engage in setups" | absorption, order book / big orders | closing summary: "a better timing advantage over other players" |

## 3.3 Trade blocks
No trade was executed in this video. Five illustrations / hypotheticals follow, each starting at an ENTRY row (or at the stop row when the entry is only implied by "cover").

```
ILLUSTRATION 1 - long - rows 14-18 (reload breakout, taught example)
state (day/week): "a directional bias, a probability directional bias"; reload plus aggression near a resting liquidity level
location: "really close to a resting liquidity level" ; level type: order (resting liquidity)
leading signal: buyers reloading passive liquidity (row 14)
trigger: "you can enter at the breakout" ; entered BEFORE or AFTER proof: after (reload and aggression precede the breakout)
entry order type: unknown ; placed before the touch: unknown
initial stop: "protected below the reload level" ; distance: no stop stated in ticks or points ; % of price: unknown
target: "first take profit on the major liquidity areas" and "second and third take profit on other resting liquidity area" ; distance: unknown ; stated R:R: unknown
management: none stated
exit: none stated ; exit type: unknown
rejects: none in this block
information sources: order book / big orders, delta / aggressive buyers, absorption
outcome: none (illustration)
horizon: unknown
mirror stated?: no - do not assume
```

```
ILLUSTRATION 2 - long - rows 22-26 (enter in the area, stop below the next liquidity area)
state (day/week): "directional bias long for the day" (bias from IVB / pivot projection / volume profile / VWAP)
location: area with a main resting level and an additional wall ; level type: order (resting liquidity)
leading signal: reload plus absorption (row 23)
trigger: "the best play ... is to see the reload that they put reload plus absorption" ; entered BEFORE or AFTER proof: unknown (row 24 says "you could decide to enter here")
entry order type: unknown ; placed before the touch: unknown
initial stop: no-heat-map version "I cover below the low" ; heat-map version "put your stop loss below the next liquidity area" ; distance: no stop stated ; % of price: unknown
target: "the next liquidity area" ; distance: unknown ; stated R:R: "an amazing risk to reward" (no number)
management: none stated
exit: none stated ; exit type: unknown
rejects: stop at the low alone (row 22) because the market can spike through an accumulation phase and take you out
information sources: order book / big orders, absorption, VWAP, prior-day/today profile
outcome: none (illustration)
horizon: unknown
mirror stated?: no - do not assume
```

```
ILLUSTRATION 3 - long - rows 28-31 (enter on the test of a broken level)
state (day/week): trend-following read ("trades that have the highest probability of following up on the trend")
location: the retest of a broken resting liquidity level ; level type: order (resting liquidity)
leading signal: aggressive breakout with fresh reload (row 28)
trigger: "let me see if the result of the price is positive" then "enter on the test" ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: "protect myself below the wall reload" ; distance: no stop stated ; % of price: unknown
target: "the next liquidity level" ; distance: unknown ; stated R:R: "1:2 1:3"
management: none stated
exit: none stated ; exit type: unknown
rejects: none in this block
information sources: order book / big orders, delta / aggressive buyers, footprint ("a footprint aggression, a big trade from the execution of order")
outcome: none (illustration)
horizon: unknown
mirror stated?: no - do not assume
```

```
ILLUSTRATION 4 - short - rows 11-12 (book flip: trail and add, taught example)
state (day/week): "you are on the short side, you took a short" (entry already given in the example)
location: break of a liquidity level followed by a reload ; level type: order (resting liquidity)
leading signal: break through the level, then reload of the same level (the "door" closing)
trigger: not an entry; management of an open short ; entered BEFORE or AFTER proof: unknown (entry not described)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: none stated ; distance: unknown ; stated R:R: unknown
management: STOP_MOVE row 11 ("trail your stop loss here") ; ADD row 12 ("add other contract")
exit: none stated ; exit type: unknown
rejects: none in this block
information sources: order book / big orders
outcome: none (illustration)
horizon: unknown
mirror stated?: no - do not assume
```

```
ILLUSTRATION 5 - short and an unlabelled-side trade - rows 74-79 (live NASDAQ read, 4 May 2026, hypothetical)
state (day/week): long bias for the day (row 59, row 61); sellers take the auction over; "Nasdaq collapsing"
location: 27,900 level broken by sellers, seller reloads (rows 71, 72); later the touch of the rejected 27,910-27,912 level (row 77) ; level type: order (resting liquidity)
leading signal: seller aggression through 27,900 and two seller reloads
trigger: "if I took a short from here" (row 74) and "with my confirmation I would have taken the first trade here" (row 77) ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: "my full take profit way lower than the low" (row 75) ; "TP1 and TP2" (row 79) with 27,790 "super far" and a cluster below ; distance: unknown ; stated R:R: unknown
management: none stated (no partial named; row 75 says "full take profit")
exit: none stated ; exit type: unknown
rejects: getting long while sellers dominate (row 65); shorting into a four-level stacked cluster above (row 36)
information sources: order book / big orders, delta / aggressive sellers (CVD), absorption, VWAP, news, [new source] "Nasdaq effort" area
outcome: none taken; "today, the Nasdaq unfolded collapsing like this"; no ticks stated
horizon: unknown
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 36: no short into an absorption plus wall at the top when four stacked liquidity levels sit above; they get "a full fill".
- Row 65: no long (no reversal play) while sellers dominate the auction; wait for the buyers to show protection first ("suicide").
- Row 7: a displayed big bid can be spoofing; do not take it as proof by itself.
- Row 33: micro-mechanics read needs higher-time-frame confirmation.
- Row 15: reload-breakout entry needs a directional bias from order flow first; stop below the reload level.
- Row 29: the test entry is taken only if "the result of the price is positive".
- Row 25: the stop sits under the next liquidity area, not just under the low, so an accumulation-phase spike does not take you out.
- Row 12: add on the book flip only while they keep confirming the move ("they want to go down").
- Row 38: move to break even after a sustained breakout; a return to the area makes a reversal likely.
- Row 55: levels are areas, not single prices.
- Row 40: a limit/absorption wait at a far level can miss the trade when an iceberg fills earlier.
- Row 67: bias flips only if the protected horizontal level breaks; targets 27,870 / 27,850 follow (row 68).

## 3.5 Verbatim anchors
> "you can trail your stop loss here"
**Source GPS: FawPrRUGNpk | BEGIN**

> "you can also add other contract"
**Source GPS: FawPrRUGNpk | BEGIN**

> "you can enter at the breakout protected below the reload level"
**Source GPS: FawPrRUGNpk | BEGIN**

> "protected below the reload level"
**Source GPS: FawPrRUGNpk | BEGIN**

> "the first take profit on the major liquidity areas and the second and third take profit on other resting liquidity area"
**Source GPS: FawPrRUGNpk | BEGIN**

> "I enter here and I cover below the low"
**Source GPS: FawPrRUGNpk | BEGIN**

> "you could decide to enter here, yes"
**Source GPS: FawPrRUGNpk | BEGIN**

> "put your stop loss below the next liquidity area"
**Source GPS: FawPrRUGNpk | BEGIN**

> "you have still an amazing risk to reward to the next liquidity area"
**Source GPS: FawPrRUGNpk | BEGIN**

> "these are all partial profit that you can take"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "I can enter on the test"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "protect myself below the wall reload"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "go to the next liquidity level, maybe for a 1:2 1:3 risk to reward"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "till they reach the final take profit in this area"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "you have an absorption on the top, you have a liquidity wall on the top and you will think to go short here"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "it's enough to put your position to break even"
**Source GPS: FawPrRUGNpk | MIDDLE**

> "I will not try to get long while the sellers are dominating the auction because it's a suicide"
**Source GPS: FawPrRUGNpk | END**

> "So, it means that your next target is the 27,870 or the 27,850"
**Source GPS: FawPrRUGNpk | END**

> "So if I took a short from here"
**Source GPS: FawPrRUGNpk | END**

> "I would consider bringing my full take profit way lower than the low"
**Source GPS: FawPrRUGNpk | END**

> "with my confirmation I would have taken the first trade here"
**Source GPS: FawPrRUGNpk | END**

> "So, we have TP1 and TP2 here"
**Source GPS: FawPrRUGNpk | END**

## 3.6 Ambiguity flags
- Rows 22, general: "cover" / "cover yourself" is used where he means stop ("I cover below the low"). Not resolved.
- Rows 21, 56: "view up" is captioned where VWAP is meant [?]; "IVB" is not defined.
- Row 70: "CBD" is captioned where CVD is meant [?]; he reads it as the CVD (delta) line.
- Rows 77, 81: "Nasdaq effort" / "Nasdaq effort area" is unclear [?]; may be a named indicator of his platform or a caption error for another market's level.
- Row 42: "27,900 and 40, 939, 940" is garbled as transcribed; later he names 27,940 as the main level.
- Rows 27, 38, 68: side not stated; the sentence is about price patterns in general.
- Row 74 vs 77: the first states a short; the second only says "the first trade" (targets below). Not resolved.
- Row 15: "protected below the reload level" is both the stop reference and a role of the reload level; the reload is later a support/protection role, not a target.
- Row 54: "if they don't put anything anything else" is a doubled word as transcribed.
- The raw file has no title line and no "# ---" header; the speaker is identified by the brief only.

## 7 self-check
1 ENTRY rows: 5 (all illustrations or hypotheticals, none executed); trade blocks: 0 executed, 5 illustrations. 2 Fields filled (unknown where not stated). 3 Last row pos% 100. 4 No stop distance in ticks or points is stated anywhere; stated stops are all level-based ("below the reload level", "below the next liquidity area", "below the wall reload", "cover below the low"). 5 Checker line below.


PASS: 0 problem(s)
