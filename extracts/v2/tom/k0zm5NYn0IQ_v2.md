# V2 extract k0zm5NYn0IQ (session 2026-10-15)

Method: EXTRACTION_METHOD_V2.md. Read in full in about 2,000-character chunks (chunk starts 0, 2,000 ... 24,000, 8,369-boundary and 16,739-boundary of the body noted for the GPS thirds). One trading morning on DAX futures: a short against the strong move, stopped out, a re-entry short that is managed to partial profits.
Raw file note: the file holds three stacked header blocks (a duplicate header and a bad-ID header); body = text after the FIRST `# ---` line (the checker's definition), 25,108 characters, so the duplicate header lines are inside the counted body.

## 3.1 Header
```
video_id: k0zm5NYn0IQ
trader: Tom (first person in the transcript; surname not stated in the transcript)
title: DAX CRASH? Why I went SHORT while everyone else was LONG (Trading World Champion explains)
instrument_stated: DAX future ("So, a very special situation here. DAX future." ; "As I said, we're in the DAX future.")
instrument_inferred: none
tick_size: unknown (unit stated in points; "you can't go down to a single tick")
session / time of day: morning ("this morning time", "market open this morning", "preession", "halfhour close"); he expects real liquidity "on Monday", so the day is probably a Friday [inferred, not stated]
translation_warning: yes ("I translated it with AI"; garbled and cut sentences throughout)
body_chars: 25109
n_decision_rows: 130
n_trades: 2
```

Outcome summary: trade 1 stopped out, trade 2 (re-entry) taken to partial profits with the rest left to run. Not a single winning trade, so the loss is in the same detail as the win.

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | CONTEXT | - | - | first trade of the morning | "First trade in the morning, stop-loss." | time of day | none stated |
| 2 | 2 | CONTEXT | - | - | counter trading session | "It was a very famous counter trading session in Dux future in this morning time" | time of day | none stated |
| 3 | 4 | ENTRY | short | right here (above the morning liquidity) | market looks strong, no liquidity left | "I'm entering a short trade right here" | liquidity (lack of) [new source] | none stated (order type unknown; proof read after, see rows below) |
| 4 | 4 | CONTEXT | short | - | strong market, no liquidity | "Even though the market looks extremely strong, I can clearly see that there's no liquidity left" | liquidity (lack of) [new source] | none stated |
| 5 | 5 | STOP_SET | short | 20 points (DAX) | - | "I'm setting a stop-loss of 20 points in the DAX" | - | none stated (his stated reason is garbled: "I don't to the downside" [?]) |
| 6 | 5 | TARGET_SET | short | below the liquidity from this morning | morning liquidity, pre-session impulse | "I actually want to get back below the liquidity from this morning" | today's profile, liquidity [new source] | none stated |
| 7 | 6 | CONTEXT | short | - | big players absent | "I assume real liquidity from the big players will only return to the markets on Monday" | time of day, news (weekday) | none stated |
| 8 | 8 | PROOF (AFTER) | short | up here | footprint chart | "a lot was simply absorbed up here and already here as well" | footprint, absorption | none stated |
| 9 | 8 | LOCATION | short | price areas below (first down, then back) | where price returns | "to return to these price areas and then see whether the market triggers a reaction down there" | footprint | see whether the market triggers a reaction down there |
| 10 | 9 | CONTEXT | short | - | volume profiles vs previous day | "we are of course above the previous day" | prior-day profile, today's profile | "it's a very risky trade and you shouldn't expect it to fall incredibly deep" |
| 11 | 9 | CONTEXT | short | - | profiles balance-heavy | "the profiles themselves are all balanceheavy" | today's profile | none stated |
| 12 | 12 | LOCATION | short | 2124 area | first liquidity below (not stated as a target) | "The first liquidity we have is in the 2124 area" | liquidity [new source] | none stated |
| 13 | 12 | ADD | short | - | aggressive selling starting | "if I now see that the market really starts to sell aggressively, am I also willing to open another" | delta / aggressive sellers | if the market really starts to sell aggressively (conditional, not executed here; "one foot in the door") |
| 14 | 13 | CONTEXT | short | current-session small liquidity | step where price runs back | "the market is running back into let's call it the small liquidity of the current session" | volume step, today's profile | none stated |
| 15 | 14 | CONTEXT | short | top | finished auction | "the market formed a completed auction at the top" | today's profile | none stated |
| 16 | 14 | CONTEXT | short | - | American futures | "If I look at the American futures as a counterpart, I also see that there is much much less action there" | other market (American futures) | none stated |
| 17 | 15 | CONTEXT | short | - | stated R:R at entry | "In terms of riskreward ratio, we're currently at about 1:6" | - | stated R:R 1:6 (planned, not a price) |
| 18 | 17 | LESSON | - | - | hit rate of counter trades | "you need to know your hit rate with such counter trades" | own trade statistics | "it should definitely be in the range of 40 to 45%" if profits are taken early |
| 19 | 18 | TARGET_SET | short | impulsive candle traded below | impulsive opening candle | "we want to see this impulsive candle traded below" | bar (TF not stated) | none stated |
| 20 | 18 | CONTEXT | short | - | no liquidity at open | "I noticed that there was no real liquidity present here" | footprint, time of day (market open) | none stated |
| 21 | 20 | CONTEXT | short | market open this morning | footprint at the open | "there was an I have to buy sentiment in the market" | footprint, time of day (market open) | none stated |
| 22 | 21 | CONTEXT | short | up here | footprint | "There was a big seller here" | footprint, order book / big orders | none stated |
| 23 | 22 | CONTEXT | short | - | alpha idea | "the market open was too extreme" | time of day (market open), footprint | "it wasn't accompanied by real volume" |
| 24 | 23 | HOLD | short | - | - | "And we'll wait because the market will show me the rest" | - | none stated |
| 25 | 23 | PROOF (AFTER) | short | - | selling picking up | "now you can already see that more selling is happening in the market here" | delta / aggressive sellers | none stated |
| 26 | 24 | CONTEXT | short | - | NASDAQ | "the NASDAQ is staying relatively stable right now, that doesn't matter" | other market (NASDAQ, American futures premarket) | none stated |
| 27 | 25 | CONTEXT | short | - | open profit 1:1 (not a target) | "we've now basically achieved the profit stretch that we had previously defined for ourselves on the loss side" | - | open profit of 1:1 on the loss side; no exit |
| 28 | 27 | HOLD | short | - | waiting | "And now it's simply a matter of waiting patiently" | - | none stated |
| 29 | 28 | HOLD | short | stronger selling step | order book via volume profile | "as long as we stay below here and selling keeps coming in from above everything is fine for now" | order book / big orders, volume step | as long as we stay below the selling step and selling keeps coming in from above |
| 30 | 29 | PROOF (AFTER) | short | "Q" [?] | seller appears | "the seller came in exactly on Q" | order book / big orders, delta / aggressive sellers | none stated |
| 31 | 30 | REJECT | short | - | trailing the stop | "In this case, I don't do that" | - | "the overall position with a riskreward ratio of about 6 to1 is simply so good that I don't worry about it" |
| 32 | 31 | ADD | short | area around 13 (right here and here) | sellers showing up | "I'm definitely willing to increase the position once more" | delta / aggressive sellers | if the area around 13 comes again and the sellers show up (conditional) |
| 33 | 31 | CONTEXT | short | - | total risk | "I now also have my total loss of about $1,000" | - | stated total loss about $1,000 (planned vs realised unclear) |
| 34 | 32 | HOLD | short | top | pressure needed up here | "there needs to be pressure up here now" | liquidity [new source] | "if there is no lack of liquidity at the top, then I will get stopped out" |
| 35 | 33 | LOCATION | short | 161, 1714 | fight in that area | "There's a fight going on here in the area of 161, 1714" | order book / big orders | none stated |
| 36 | 33 | PROOF (AFTER) | short | 161, 1714 | seller more aggressive | "At the moment, the seller has the upper hand" | delta / aggressive sellers, order book / big orders | none stated |
| 37 | 34 | CONTEXT | short | - | half-hour close | "I can well imagine that we're about to see a reaction at the halfhour close" | bar close (30m), time of day | none stated |
| 38 | 35 | LESSON | - | - | balance | "where liquidity is being played, the market is in balance" | liquidity [new source] | none stated |
| 39 | 37 | HOLD | short | - | no aggressive buying seen | "I'm quite satisfied with my positioning right now and will continue to wait here patiently" | delta / aggressive buyers | risk he names: "suddenly aggressive buying happens up here", "I haven't seen that so far" |
| 40 | 37 | PROOF (AFTER) | short | - | delta | "in these last two candles we had a selling surplus" | delta / aggressive sellers | none stated |
| 41 | 38 | CONTEXT | short | - | price against him | "this doesn't look too good for me right now" | - | none stated |
| 42 | 39 | HOLD | short | stop (level not stated) | - | "I'm stubbornly sticking to my stop loss" | - | "if I get stopped out in a moment, that's just part of the game" |
| 43 | 39 | CONTEXT | short | - | re-entry plan | "Then I would look for another position" | liquidity [new source] | "if I saw again that the market is giving up its liquidity there" |
| 44 | 40 | CONTEXT | short | new highs | new highs | "Now we're also making new highs" | swing high/low | "the market up here isn't really taking off yet" |
| 45 | 40 | EXIT | short | stop | stop hit | "Now we've been stopped out and that's just part of it" | - | none stated |
| 46 | 41 | CONTEXT | short | up here | still no liquidity | "there's still no liquidity being played up here" | liquidity [new source] | none stated |
| 47 | 41 | ENTRY | short | up here (still no liquidity) | - | "I am actually going to proceed with entering another trading position" | liquidity [new source] | none stated (order type unknown; re-entry after the stop-out; proof read after) |
| 48 | 41 | STOP_SET | short | $500 (unit unclear) | - | "I'm giving the market an initial stop of $500 again for now" | - | none stated ("again": same size as before [?]) |
| 49 | 41 | CONTEXT | short | - | idea | "I still have the idea that we should come down here" | - | none stated |
| 50 | 42 | PROOF (AFTER) | short | up here | finished auction | "we have a finished auction again and also no more liquidity" | today's profile, liquidity [new source] | none stated |
| 51 | 43 | PROOF (AFTER) | short | - | selling | "It's being heavily sold" | delta / aggressive sellers | none stated |
| 52 | 43 | LESSON | short | - | re-entry after stop-out | "you can definitely enter the position again here" | - | "if you realize that your basic idea wasn't correct, but you just got stopped out" |
| 53 | 44 | PROOF (AFTER) | short | up here | large volumes traded over | "there's just no real liquidity coming in anymore" | order book / big orders | none stated |
| 54 | 45 | CONTEXT | short | - | PBD example | "what we have here now is a great example for the PBD logic" | PBD logic [new source] | none stated |
| 55 | 45 | ADD | short | - | PBD example | "that will also motivate me in a moment to increase the position if that's the case" | PBD logic [new source] | "if that's the case" [?] (what case is not named) |
| 56 | 45 | LOCATION | short | range from "our P" [?] | range | "Now, here we have our range from our P" | today's profile [?] | none stated |
| 57 | 46 | ADD | short | down side of the range | range break | "I would definitely look for another position down here" | - | if the market breaks out of this range to the downside (conditional) |
| 58 | 47 | REJECT | short | - | the safe way (waiting for the bullish zone to be traded through) | "Anyone who wants to play it safe with such counter trades logically has to wait" | - | "I'm someone who likes that, but only when the market shows me very specific situations" |
| 59 | 49 | CONTEXT | short | upper range | inside bar | "it's also forming an inside bar" | bar (TF not stated) | none stated |
| 60 | 50 | LOCATION | short | price range marked on the chart | marked range | "which definitely needs to be traded below" | - | none stated |
| 61 | 50 | CONTEXT | short | above the range | - | "everything above that is of course risky" | - | none stated |
| 62 | 51 | LOCATION | short | 320 level | buyers at 320 | "at this 320 level whether the market finds buyers there again" | - | "if the market finds buyers there again", "that's bad for us because it could mean that this structure continues" |
| 63 | 52 | CONTEXT | long | above the marked range (5-minute chart) | large volumes above the range | "I would definitely be looking for a long position" | bar (5-minute chart) | if the market accumulated large volumes above the range marked on the 5-minute chart (hypothetical long) |
| 64 | 53 | REJECT | long | - | initial balance large | "because the initial balance is so large" | today's profile (initial balance), time of day (market open) | "expansion of the trading opening is just very very big"; the buying at the open was hedging that will be corrected later |
| 65 | 54 | HOLD | short | - | - | "now it's a matter of waiting there's nothing more we can do" | - | none stated |
| 66 | 54 | PROOF (AFTER) | short | - | active selling | "there's active selling going on again right now" | delta / aggressive sellers, order book / big orders | none stated |
| 67 | 55 | LOCATION | short | 320 323 | price range | "This is exactly the price range around 320 323" | - | "what I'd really like to see now is the market being sold off aggressively"; "If liquidity starts to dry up there again, that means no one's interested anymore" |
| 68 | 58 | CONTEXT | short | line (level not stated) | decisive line | "This right here is the line that's decisive for me" | - | "everything above it is of course extremely uh strong" |
| 69 | 59 | CONTEXT | short | - | gold futures | "Gold futures are also being steadily sold off right now" | other market (gold futures) | "There's a weak low" in gold |
| 70 | 60 | CONTEXT | short | 320 | price range | "We're now exactly in this price range around 320 and coming right back to this liquidity" | liquidity [new source] | none stated |
| 71 | 60 | PROOF (AFTER) | short | 320 | absorption | "There's a bit of absorption happening here as well" | absorption | none stated |
| 72 | 61 | LOCATION | short | 317 318 319 | line drawn on smaller chart | "I've drawn the line here 317 318 319" | - | none stated ("you can't go down to a single tick") |
| 73 | 62 | CONTEXT | short | - | liquidity | "the liquidity is being played within the larger liquidity" | liquidity [new source] | none stated |
| 74 | 63 | HOLD | short | 336 to 340 | - | "as long as we stay below 336 to 340, everything is actually cool right here" | - | as long as price stays below 336 to 340 |
| 75 | 63 | PROOF (AFTER) | short | - | small buyers | "some small buyers are coming in again" | delta / aggressive buyers | "it's nothing major" |
| 76 | 64 | PROOF (AFTER) | short | - | sold off | "how aggressively it's being sold off there" | delta / aggressive sellers | none stated |
| 77 | 64 | REJECT | long | - | no information from above | "not to jump back into the market long too early" | - | "especially when you don't actually have any information for it from above" |
| 78 | 65 | HOLD | short | - | - | "let's let the market play out a bit" | - | none stated |
| 79 | 65 | PROOF (BEFORE) | short | up here | reaction | "how the market has reacted up here again" | order book / big orders, liquidity [new source] | none stated |
| 80 | 66 | ADD | short | - | another position, smaller risk | "I'm opening another position and I don't want to take on too much risk" | - | none stated (read as an add to the re-entry; see flags) |
| 81 | 66 | STOP_SET | short | above the last volume levels | volume levels | "my stop loss is now set exactly above the last volume levels" | HVN/LVN or volume step | "if we push above here again, then it's over anyway" |
| 82 | 67 | PROOF (AFTER) | short | up here | rejection | "The market showed me that there is rejection up here" | market speed | none stated |
| 83 | 68 | PROOF (AFTER) | short | up here | speed of rejection | "the speed with which it rejected this is promising for me" | market speed | none stated |
| 84 | 68 | PROOF (AFTER) | short | down here | liquidity below | "the market likes the liquidity down there" | liquidity [new source] | none stated |
| 85 | 70 | HOLD | short | 3004 [?] | block below | "leave this block below 3004 down here with liquidity" | HVN/LVN or volume step | "if you now leave this block below 3004 down here with liquidity then our trade is a great trade" |
| 86 | 70 | CONTEXT | short | - | re-entry | "it was worth it to make a re-entry here" | - | none stated |
| 87 | 71 | LESSON | - | - | block to block | "the market always moves from block to block" | HVN/LVN or volume step | none stated |
| 88 | 71 | HOLD | short | lower edge | sell-side liquidity and speed | "continues to provide liquidity on the sell side" | order book / big orders, market speed | "ideally it also maintains its speed" |
| 89 | 72 | PROOF (AFTER) | short | down here | absorption | "there's a bit of absorption down here again" | absorption | none stated |
| 90 | 72 | PROOF (AFTER) | short | - | contract sizes | "The seller is the bigger one" | order book / big orders | none stated |
| 91 | 73 | ADD | short | - | - | "And now it's time to take another risk" | - | none stated ([?] meaning unclear; see flags) |
| 92 | 73 | CONTEXT | short | - | market dithering | "the market is dithering again" | - | none stated |
| 93 | 73 | LESSON | - | - | rubber band | "the longer it aggregates liquidity in this price range, the stronger the next subsequent trend will be" | liquidity [new source] | none stated |
| 94 | 74 | CONTEXT | short | - | low volume node | "we have this low volume node here" | HVN/LVN or volume step | none stated |
| 95 | 75 | TARGET_SET | short | 285 (85 83) | low volume node below | "the next stop for us is this price range 285 like that" | HVN/LVN or volume step | see whether there is a reaction there |
| 96 | 75 | TARGET_SET | short | 85 83 | first profits | "we could potentially take our first profits there" | - | "I'll decide that when the market" [sentence cut] |
| 97 | 76 | CONTEXT | short | - | stated R:R | "roughly a little more than 2 to one" | - | stated R:R at that time |
| 98 | 77 | LESSON | - | - | break-even maths | "if you have a riskreward ratio of one" | - | "that would mean that the winning streak and the losing streak are each the same" |
| 99 | 79 | LESSON | - | - | break-even maths | "then you need at least a riskreward ratio of 1.5" | - | hit rate "in the range of 40 to 45%" with counter trading strategies |
| 100 | 79 | LESSON | - | - | profit maths | "a riskreward ratio of two or even significantly greater than two" | - | none stated |
| 101 | 81 | CONTEXT | short | 85 down to 30 | distance | "Going from 85 down to 30, that means we have 55 points" | - | stop distance for this ratio is cut in the transcript ("Moving upwards, we have the range from") |
| 102 | 81 | CONTEXT | short | - | stated R:R | "we have is equal to 3.66" | - | stated R:R 3.66 |
| 103 | 83 | PROOF (AFTER) | short | below the balance | balance | "shown us below the balance that it wants to stay there for now" | today's profile | none stated |
| 104 | 83 | TARGET_SET | short | below this low | first target zone | "in the end we have our first target zone" | swing high/low | none stated |
| 105 | 84 | LOCATION | short | 8684 [?] | zone entered | "what happens when we get into the 8684" | - | none stated |
| 106 | 84 | PARTIAL | short | ~8684 zone (not restated) | - | "So now we're taking a part out here" | - | "nothing can really go wrong anymore" |
| 107 | 86 | CONTEXT | short | - | new balance | "we have a new balance here" | today's profile | none stated |
| 108 | 87 | HOLD | short | new balance | accept down or back above | "Then it could really go lower or whether it moves back above it" | today's profile | "whether it picks up momentum from there and says I accept everything to the downside" |
| 109 | 87 | LESSON | short | - | PBD logic | "it's time at the latest after a retrace to get out of the whole thing" | PBD logic [new source] | after a retrace |
| 110 | 88 | STOP_MOVE | short | "here" (level not stated) | new balance | "it's simply effective to definitely place the stop loss here" | today's profile | none stated |
| 111 | 88 | CONTEXT | short | - | reason for the stop move | "we can't lose anymore now" | - | none stated |
| 112 | 88 | HOLD | short | 265 | momentum | "what the momentum is like if it drops below 265" | market speed | "if it drops below 265" then "we can also decide whether to take partial profits or not" |
| 113 | 89 | CONTEXT | short | - | profile view | "We have a very large initial balance" | today's profile (initial balance) | none stated |
| 114 | 90 | CONTEXT | short | up here | value area | "the value area is up here, meaning today's equilibrium is up here" | today's profile, VAH/VAL/POC | none stated |
| 115 | 90 | CONTEXT | short | up there | selling | "there was quite a bit of selling up there as well" | today's profile | none stated |
| 116 | 91 | LOCATION | short | yesterday's value high | reaction at yesterday's VAH | "see if there is a reaction here at yesterday's value high" | prior-day profile, VAH/VAL/POC | none stated |
| 117 | 92 | HOLD | short | yesterday's range | re-entering the range | "And then I would also exit the corresponding trade" | prior-day profile | if we re-enter the range and the market finds acceptance there (conditional exit, not executed) |
| 118 | 92 | PARTIAL | short | - | - | "Take profits again" | - | none stated ([?] sentence fragment; "again") |
| 119 | 93 | CONTEXT | short | - | discretionary day | "Since I'm trading discretionarily today" | - | none stated |
| 120 | 93 | LOCATION | short | 250 | round number | "There's liquidity at 250" | liquidity [new source] | "the market will surely go for it" |
| 121 | 94 | PROOF (AFTER) | short | 250 | price reached it | "Traded right into it nicely" | - | none stated |
| 122 | 94 | CONTEXT | short | - | pullback | "we'll probably see a short pullback here first" | - | none stated |
| 123 | 95 | CONTEXT | short | - | volume step | "the volume step between this upper area and the one below it" | HVN/LVN or volume step | none stated |
| 124 | 95 | HOLD | short | - | market speed | "whether the market speed will catch up" | market speed | none stated |
| 125 | 96 | PROOF (AFTER) | short | - | speed | "The market speed is decreasing" | market speed | none stated |
| 126 | 97 | LOCATION | short | "Nine" [?] (cut), yesterday's value high | yesterday's range | "That's also the value area high from yesterday's range" | prior-day profile, VAH/VAL/POC | none stated |
| 127 | 97 | PARTIAL | short | yesterday's value high | - | "So, I'm taking some profit here" | market speed, prior-day profile, VAH/VAL/POC | none stated |
| 128 | 97 | HOLD | short | - | remaining position | "just let the rest of the position run for the day whether it hits or not" | - | "end this trail" |
| 129 | 97 | STOP_MOVE | short | 310 area | remaining position | "my stop loss for the remaining position, I've now adjusted it to the 310 area" | - | none stated |
| 130 | 98 | LESSON | - | - | stops are normal | "Even if you take a few stops, that's absolutely no problem" | - | "especially when you're acting as a counter trader at such highs" |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 3-45
state (day/week): "the market looks extremely strong" but "no liquidity left"; above the previous day; profiles "balanceheavy"; "completed auction" at the top; American futures show "much much less action"; real liquidity expected back "on Monday"
location: "I'm entering a short trade right here" (top of the strong move, above the morning liquidity) ; level type: other (area with no liquidity above, finished auction at the top)
leading signal: "no real liquidity" at the open, an "I have to buy sentiment", open "too extreme" without real volume (rows 20, 21, 23)
trigger: at location ; entered BEFORE or AFTER proof: before (footprint absorption read afterwards, row 8)
entry order type: unknown ; placed before the touch: unknown
initial stop: "a stop-loss of 20 points in the DAX" ; distance: 20 points ; % of price: unknown (price not stated)
target: "get back below the liquidity from this morning" / "this impulsive candle traded below" ; distance: not stated ; stated R:R: "about 1:6" (row 17)
management: no PARTIAL, no STOP_MOVE (trailing the stop rejected, row 31); ADD rows 13 and 32 were conditional ("willing to"), no fill is stated; "1 one" on the clock (row 27) is open profit, not a target
exit: "Now we've been stopped out and that's just part of it" ; exit type: stop (price made "new highs", row 44)
rejects: row 31 no trailing stop because the position has "a riskreward ratio of about 6 to1" and "I don't worry about it"
information sources: footprint, absorption, order book / big orders, prior-day profile, today's profile, volume step, delta / aggressive sellers, other market (American futures, NASDAQ), time of day (market open, half-hour close)
outcome: stopped out; "my total loss of about $1,000" (row 33; planned versus realised not clear); R not stated
horizon: minutes not stated; inside the morning
mirror stated?: no - do not assume

TRADE 2 - short - rows 47-130
state (day/week): re-entry after the stop-out ("Now we're also making new highs"); "a finished auction again and also no more liquidity"; "a very large initial balance"; value area "up here" (higher); yesterday's value high above as a reference
location: "up here" first, then the working range "around 320 323" and "317 318 319" ; level type: acceptance area (price range) with a value high of the previous day above
leading signal: "finished auction again", "no real liquidity coming in anymore", "It's being heavily sold" (rows 50, 51, 53)
trigger: at location ; entered BEFORE or AFTER proof: before (finished auction and liquidity read after the entry, row 50)
entry order type: unknown ; placed before the touch: unknown
initial stop: "an initial stop of $500 again for now" ; distance: "$500" (unit not clear) ; % of price: unknown ; second position stop: "exactly above the last volume levels" (row 81) ; hold level: "as long as we stay below 336 to 340" (row 74)
target: "the next stop for us is this price range 285 like that" (85 83), "first target zone" below a low (rows 95, 96, 104) ; distance: "from 85 down to 30 ... 55 points" ; stated R:R: "a little more than 2 to one" then "equal to 3.66" (rows 97, 102; the stop distance used is cut in the transcript)
management: ADD row 80 (and 91 [?]); conditional ADD rows 55, 57; PARTIAL rows 106, 118 [?], 127; STOP_MOVE rows 110 (level "here"), 129 (310 area)
exit: no final exit is stated; "let the rest of the position run for the day whether it hits or not" ; exit type: unknown (position open at the end of the video)
rejects: row 58 (the safe way: waiting until the bullish zone is traded through); row 64 (no long: "the initial balance is so large", the open buyers were hedging); row 77 (not "to jump back into the market long too early")
information sources: footprint, absorption, order book / big orders, delta / aggressive buyers or sellers, today's profile (initial balance, new balance, value area), prior-day profile (value high), volume step / low volume node, market speed, other market (gold futures), bar (5-minute chart, inside bar), time of day, PBD logic [new source]
outcome: "a really great trading day" ; no money or ticks stated for this trade; "nothing can really go wrong anymore" after the first partial
horizon: "for the day"
mirror stated?: no - do not assume
```


## 3.4 Rejections and conditions
- Row 31 (REJECT, short): "In this case, I don't do that"; condition/reason: "the overall position with a riskreward ratio of about 6 to1 is simply so good that I don't worry about it"
- Row 58 (REJECT, short): "Anyone who wants to play it safe with such counter trades logically has to wait"; condition/reason: "I'm someone who likes that, but only when the market shows me very specific situations"
- Row 64 (REJECT, long): "because the initial balance is so large"; condition/reason: "expansion of the trading opening is just very very big"; the buying at the open was hedging that will be corrected later
- Row 77 (REJECT, long): "not to jump back into the market long too early"; condition/reason: "especially when you don't actually have any information for it from above"
- Row 9 (LOCATION): see whether the market triggers a reaction down there
- Row 10 (CONTEXT): "it's a very risky trade and you shouldn't expect it to fall incredibly deep"
- Row 13 (ADD): if the market really starts to sell aggressively (conditional, not executed here; "one foot in the door")
- Row 17 (CONTEXT): stated R:R 1:6 (planned, not a price)
- Row 18 (LESSON): "it should definitely be in the range of 40 to 45%" if profits are taken early
- Row 23 (CONTEXT): "it wasn't accompanied by real volume"
- Row 27 (CONTEXT): open profit of 1:1 on the loss side; no exit
- Row 29 (HOLD): as long as we stay below the selling step and selling keeps coming in from above
- Row 32 (ADD): if the area around 13 comes again and the sellers show up (conditional)
- Row 33 (CONTEXT): stated total loss about $1,000 (planned vs realised unclear)
- Row 34 (HOLD): "if there is no lack of liquidity at the top, then I will get stopped out"
- Row 39 (HOLD): risk he names: "suddenly aggressive buying happens up here", "I haven't seen that so far"
- Row 42 (HOLD): "if I get stopped out in a moment, that's just part of the game"
- Row 43 (CONTEXT): "if I saw again that the market is giving up its liquidity there"
- Row 44 (CONTEXT): "the market up here isn't really taking off yet"
- Row 52 (LESSON): "if you realize that your basic idea wasn't correct, but you just got stopped out"
- Row 55 (ADD): "if that's the case" [?] (what case is not named)
- Row 57 (ADD): if the market breaks out of this range to the downside (conditional)
- Row 62 (LOCATION): "if the market finds buyers there again", "that's bad for us because it could mean that this structure continues"
- Row 63 (CONTEXT): if the market accumulated large volumes above the range marked on the 5-minute chart (hypothetical long)
- Row 67 (LOCATION): "what I'd really like to see now is the market being sold off aggressively"; "If liquidity starts to dry up there again, that means no one's interested anymore"
- Row 68 (CONTEXT): "everything above it is of course extremely uh strong"
- Row 69 (CONTEXT): "There's a weak low" in gold
- Row 74 (HOLD): as long as price stays below 336 to 340
- Row 75 (PROOF (AFTER)): "it's nothing major"
- Row 81 (STOP_SET): "if we push above here again, then it's over anyway"
- Row 85 (HOLD): "if you now leave this block below 3004 down here with liquidity then our trade is a great trade"
- Row 88 (HOLD): "ideally it also maintains its speed"
- Row 95 (TARGET_SET): see whether there is a reaction there
- Row 96 (TARGET_SET): "I'll decide that when the market" [sentence cut]
- Row 97 (CONTEXT): stated R:R at that time
- Row 98 (LESSON): "that would mean that the winning streak and the losing streak are each the same"
- Row 99 (LESSON): hit rate "in the range of 40 to 45%" with counter trading strategies
- Row 101 (CONTEXT): stop distance for this ratio is cut in the transcript ("Moving upwards, we have the range from")
- Row 102 (CONTEXT): stated R:R 3.66
- Row 106 (PARTIAL): "nothing can really go wrong anymore"
- Row 108 (HOLD): "whether it picks up momentum from there and says I accept everything to the downside"
- Row 109 (LESSON): after a retrace
- Row 112 (HOLD): "if it drops below 265" then "we can also decide whether to take partial profits or not"
- Row 117 (HOLD): if we re-enter the range and the market finds acceptance there (conditional exit, not executed)
- Row 120 (LOCATION): "the market will surely go for it"
- Row 128 (HOLD): "end this trail"
- Row 130 (LESSON): "especially when you're acting as a counter trader at such highs"

## 3.5 Verbatim anchors
> "I'm entering a short trade right here"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "I'm setting a stop-loss of 20 points in the DAX"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "I actually want to get back below the liquidity from this morning"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "specifically into this free session impulse that we saw here"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "if I now see that the market really starts to sell aggressively, am I also willing to open another"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "we want to see this impulsive candle traded below"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "In this case, I don't do that"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "I'm definitely willing to increase the position once more"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "If we now see the area around 13 again, right here and here, and see the sellers show up"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "if there is no lack of liquidity at the top, then I will get stopped out"
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "Now we've been stopped out and that's just part of it"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "I am actually going to proceed with entering another trading position"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "I'm giving the market an initial stop of $500 again for now"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "that will also motivate me in a moment to increase the position if that's the case"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "I would definitely look for another position down here"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "if I now see that we actually break out of this range to the downside"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "Anyone who wants to play it safe with such counter trades logically has to wait"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "because the initial balance is so large meaning the expansion of the trading opening is just very very big"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "not to jump back into the market long too early"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "I'm opening another position and I don't want to take on too much risk"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "my stop loss is now set exactly above the last volume levels"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "if we push above here again, then it's over anyway"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "And now it's time to take another risk"
**Source GPS: k0zm5NYn0IQ | END**

> "the next stop for us is this price range 285 like that"
**Source GPS: k0zm5NYn0IQ | END**

> "we could potentially take our first profits there"
**Source GPS: k0zm5NYn0IQ | END**

> "in the end we have our first target zone"
**Source GPS: k0zm5NYn0IQ | END**

> "So now we're taking a part out here"
**Source GPS: k0zm5NYn0IQ | END**

> "it's simply effective to definitely place the stop loss here"
**Source GPS: k0zm5NYn0IQ | END**

> "we can also decide whether to take partial profits or not"
**Source GPS: k0zm5NYn0IQ | END**

> "Take profits again"
**Source GPS: k0zm5NYn0IQ | END**

> "the market will surely go for it"
**Source GPS: k0zm5NYn0IQ | END**

> "So, I'm taking some profit here"
**Source GPS: k0zm5NYn0IQ | END**

> "my stop loss for the remaining position, I've now adjusted it to the 310 area"
**Source GPS: k0zm5NYn0IQ | END**

## 3.6 Ambiguity flags
- Row 5: the stated reason for the 20-point stop is cut ("I don't to the downside"). Not repaired.
- Rows 12, 85, 105, 35, 67, 62, 72, 74, 95, 101, 112, 129, 120, 126: the price numbers (2124, 161 and 1714, 320 323, 317 318 319, 336 to 340, 3004, 285, 85 83, 8684, 30, 265, 250, "Nine", 310) look like truncated DAX prices (leading digits dropped by the AI captioning); the full index levels are not stated. Do not complete them.
- Row 72: "you can't go down to a single tick" is cut off; tick size not stated.
- Row 48: "$500" as a stop: the unit (dollars of risk, points, or something else) is unclear; also "again" may mean the same size as the first stop, which was 20 points.
- Row 33: "total loss of about $1,000" may be the planned risk after an add, or the realised loss of trade 1; the transcript does not say which.
- Row 80: "I'm opening another position" is read as an add inside the re-entry idea (he says "first position" at the first entry). It may instead be a third separate trade after a second stop-out that the transcript does not mention. Row 86 ("re-entry") points at the earlier row 47. Not resolved.
- Row 91: "take another risk" may mean another add or a garbled phrase. Not resolved.
- Row 118: "Take profits again." is a fragment before "Again here I will now watch"; it may be a second partial, or a leftover phrase. Counted as a possible partial.
- Rows 106, 127: the partial prices are given as "here" only; "8684" and "Nine" are the nearest numbers and are cut.
- Row 110: the new stop level is "here", no number. The reason ("we can't lose anymore now") implies a stop at or beyond breakeven, which is not stated.
- Row 30: "exactly on Q" has an unclear word ("Q") and may be a captioning error.
- Rows 54, 55, 56, 109: "PBD logic", "our P" and "That's our P" are not explained in this video; "if that's the case" does not name the case.
- Row 58: it is unclear whether he rejects the safe way for himself; he is already short at that point and says "I'm someone who likes that, but only when the market shows me very specific situations".
- Row 117: "I would also exit the corresponding trade" is a conditional plan, not an executed exit.
- Row 27: "Right now we have a riskreward ratio of 1 one" is open profit; the transcript spells the ratio "1 one" (also "6 to1", "a riskreward ratio of about 6 to1").
- Row 101: "Moving upwards, we have the range from" is cut, so the 3.66 ratio cannot be rebuilt from stated numbers (55 points is stated, the stop distance is not).
- Row 63: the long idea is hypothetical ("If I now had liquidity above"); no long is taken.
- Row 29: "selling step" is his term for the volume step; "Q" and "13" in rows 30 and 32 are cut or garbled numbers.


## 3.7 Self-check
- ENTRY rows: 2 (rows 3, 47); trade blocks: 2; each block starts at an ENTRY row.
- Last decision row pos% = 98 (>= 95).
- Gate result below.
PASS: 0 problem(s)
