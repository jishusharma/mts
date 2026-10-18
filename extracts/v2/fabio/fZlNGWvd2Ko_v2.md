# V2 extract fZlNGWvd2Ko (Fabio, best session of October commentary)

Method: EXTRACTION_METHOD_V2.md. Read in 4 chunks of about 2,000 characters (the file has no '# ---' header; the whole file is the body). The video is a screen-recording commentary on one session: prices on the chart are shown but never spoken, so levels have no numbers; only money amounts are spoken. Two trades: TRADE 1 a losing continuation short, TRADE 2 a scaled-in position that ends as the best session of October (a winning session).

## 3.1 Header
```
video_id: fZlNGWvd2Ko
trader: Fabio (Fabio Valentini; the transcript does not state the name)
title: unknown (the raw file has no header line; the speaker calls it the best trading session of October)
instrument_stated: not stated
instrument_inferred: none
tick_size: unknown
session / time of day: after a London session; the commented session is the one that follows ('we came from a London session'); the session name is not stated
translation_warning: no flag in the text (auto-captioned speech with fillers 'uh' 'um')
body_chars: 7508 (raw file incl. [m:ss] markers; the whole file is the body)
n_decision_rows: 51
n_trades: 2
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | CONTEXT | - | - | platform | "it's a professional order flow platform" | footprint (order flow platform, features not described) | none stated |
| 2 | 8 | CONTEXT | - | London session | prior session result | "we came from a London session where we did pretty good amount of profit" ; (around $10,000 stated in the next sentence) | time of day | none stated |
| 3 | 10 | CONTEXT | - | start of the session | choppiness | "we start the session getting caught by a little bit of choppiness here" ; (gave back around $5,000, to about 4,500) | time of day | none stated |
| 4 | 12 | ENTRY | short | unknown | - | "The first trades that we took was a continuation short" ; entry order type unknown; BEFORE/AFTER proof unknown | - | none stated |
| 5 | 14 | EXIT | short | unknown | - | "We tried this continuation and we failed" ; exit reason not stated beyond failure; exit type unknown; outcome: 'gave back two trades' | - | none stated |
| 6 | 17 | LESSON | - | break even | session drawdown cap | "if we go back to break even, we stop the session" ; (stop-the-session rule; 'maximum drawdown that is break even') | - | if the session P&L goes back to break even |
| 7 | 20 | CONTEXT | - | consolidation area | consolidation area | "this consolidation area got completely wrecked by buyers that took control" | consolidation area (range) [new source]; delta / aggressive buyers | none stated |
| 8 | 21 | CONTEXT | - | same area | sellers | "The sellers got absorbed here" | absorption | none stated |
| 9 | 22 | LOCATION | long [inferred: buyers / 'up session'; he never says long] | the level where buyers got aggressive | failed auction of the seller | "capitalize on the failed auction of the seller and then aggression of the level of the buyers" | absorption; delta / aggressive buyers; failed auction [new source] | none stated |
| 10 | 24 | STOP_SET | long [inferred: buyers / 'up session'; he never says long] | break even if the level fails | this level | "I will be really fast in putting my position to break even if this level failed" ; conditional break-even rule; no price or distance stated; no other initial stop stated (no stop stated) | - | if this level failed |
| 11 | 25 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | this level -> new pivot | this level | "if this level failed, this one become the new pivot" ; level role: if it fails, a different level becomes the pivot | - | if this level failed |
| 12 | 27 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | same area | sellers | "there are a huge amount of information that the sellers are being absorbed here" | absorption | none stated |
| 13 | 29 | TARGET_SET | long [inferred: buyers / 'up session'; he never says long] | top of the day | - | "amazing risk to reward trades to take the top of the day" ; no R:R number and no price stated | - | none stated |
| 14 | 32 | CONTEXT | - | - | session method | "aggression of the market" ; (session done 'using the big trades and the aggression of the market') | big orders ('big trades') [new source: big trades as executed prints]; delta / aggressive buyers or sellers | none stated |
| 15 | 33 | ENTRY | long [inferred: buyers / 'up session'; he never says long] | unknown (scaled in) | - | "I'm loading and scaling in position" ; 'trying to get my losses smaller and smaller'; order type unknown; BEFORE/AFTER proof unknown; first load shown on screen, price not stated | - | none stated |
| 16 | 34 | LESSON | - | - | risk budget | "I'm only risking the profit of the day" | - | none stated |
| 17 | 35 | CONTEXT | - | - | open profit | "We are up a gain 9,000 for the day" ; (around 10,000 a moment later); open profit for the day, NOT a target | - | none stated |
| 18 | 36 | ADD | long [inferred: buyers / 'up session'; he never says long] | unknown | - | "I will continue to scale my position as we go" ; no add trigger or size stated | - | none stated |
| 19 | 38 | CONTEXT | - | - | buyers | "buyers failed again" | delta / aggressive buyers; absorption | none stated |
| 20 | 39 | STOP_MOVE | unknown (see 3.6) | unknown | risk | "So I want to lower my risk" ; mechanism not stated (size or stop); no level stated | big orders | if this big trade sell gets stopped out |
| 21 | 40 | REJECT | unknown (see 3.6) | unknown | big trade sell | "I don't want to be in the position" ; reason: 'a really fast snapback of the market' | big orders / order book | if this big trade sell gets stopped out |
| 22 | 43 | STOP_MOVE | long [inferred: buyers / 'up session'; he never says long] | unknown | solid aggression | "My risk goes really low and now I'm risking $980" ; stop level not stated; open risk $980 vs 'potential $25,000' (potential, not a target price) | delta / aggressive buyers or sellers | none stated |
| 23 | 44 | TARGET_SET | long [inferred: buyers / 'up session'; he never says long] | day P&L, money | - | "Close the day above $25,000" ; money target for the day, not a price level; stated as potential | - | none stated |
| 24 | 47 | LESSON | - | - | best vs worst session | "the best session of the month it's two times and a half bigger than the worst session of the month" ; (worst session about -5,000 to -10,000) | - | none stated |
| 25 | 50 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | - | buyers | "So now the buyers are in control" | delta / aggressive buyers | none stated |
| 26 | 53 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | a level above | sellers | "you can see that sellers are trying to protect this level" ; 'all these big trades' on screen | big orders ('big trades') [new source: big trades as executed prints] | none stated |
| 27 | 54 | STOP_MOVE | long [inferred: buyers / 'up session'; he never says long] | - | next breakout | "if we have another breakout, we can trail our stop in profit" ; plan, not yet done | - | if we have another breakout |
| 28 | 55 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | - | buyers wall | "we have a buyers wall, they try to push down" | order book / big orders | none stated |
| 29 | 57 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | consolidation area | buyers | "the buyers are not making results in this case" ; ('the sellers got completely absorbed here') | absorption | none stated |
| 30 | 58 | STOP_MOVE | long [inferred: buyers / 'up session'; he never says long] | risk free, or a tight stop | this level | "if we break down this level, I want to be risk free or with a really tight stop loss" ; plan; reason: 'we will probably revisit this level here' | - | if we break down this level |
| 31 | 61 | LESSON | - | - | stop in profit | "it's pretty good to manage your position with stop loss in profit if you see something like this" | - | none stated |
| 32 | 63 | PROOF (AFTER) | long [inferred: buyers / 'up session'; he never says long] | - | sell acceleration | "the market did a really good acceleration of the sell and stop before these aggressive buyers" | market speed; delta / aggressive buyers | none stated |
| 33 | 64 | STOP_MOVE | long [inferred: buyers / 'up session'; he never says long] | zero (break even) | sellers stopped | "Now my position is stop loss to zero" ; reason: 'sellers got stopped again in the movement and buyers are starting to continue up' | delta / aggressive buyers or sellers | none stated |
| 34 | 67 | PROOF (AFTER) | long [inferred: buyers / 'up session'; he never says long] | - | candle body | "big trades in the body of the candle" ; ('another effort but still no result') | big orders ('big trades') [new source: big trades as executed prints]; absorption | none stated |
| 35 | 70 | STOP_MOVE | long [inferred: buyers / 'up session'; he never says long] | below this low | buyers took control | "Now I'm covered below this low" ; 'getting a little bit of profit' (stop in profit); 'covered' see 3.6 | swing high/low; delta / aggressive buyers | buyers took control |
| 36 | 71 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | - | locked result | "the worst case scenario, I close $10,000" ; (best case 'above 25,000'); worst case is a locked-in result, NOT a target | - | none stated |
| 37 | 73 | PROOF (AFTER) | long [inferred: buyers / 'up session'; he never says long] | acceleration level | buyers vs sellers | "no result from the buyers but also no result from the sellers" ; 'This is a potential acceleration level here that we have' | absorption; market speed | none stated |
| 38 | 76 | PARTIAL | long [inferred: buyers / 'up session'; he never says long] | unknown | sellers stopped on big trades | "So I can take other profit from the market" ; size and price not stated; may be a stop raise instead (see 3.6) | big orders ('big trades') [new source: big trades as executed prints] | sellers took control but stopped on these big trades |
| 39 | 77 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | - | locked result | "the worst case scenario, we close $15,000 for the day" ; locked-in result, NOT a target | - | none stated |
| 40 | 79 | LESSON | - | - | protecting profit | "this is a way to get back your profit from the market as soon as possible and not give back the profit that you make to the market" | - | none stated |
| 41 | 82 | PROOF (AFTER) | long [inferred: buyers / 'up session'; he never says long] | this level | market explode | "You see all these aggression and a failed auction" ; given as the reason for the close (see 3.6) | delta / aggressive buyers or sellers; failed auction [new source] | none stated |
| 42 | 83 | EXIT | long [inferred: buyers / 'up session'; he never says long] | unknown | - | "this is the reason I closed my trade" ; exit type: manual; price not stated; the market then 'skyrocket up' | delta / aggressive buyers or sellers; failed auction [new source] | none stated |
| 43 | 86 | REJECT | long [inferred: buyers / 'up session'; he never says long] | - | holding for more | "I prefer to be conservative when I have a really good sniper trades" ; rejects holding for a '40, 50,000 dollar session' (missed profit, not a target) | - | none stated |
| 44 | 87 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | first load | recap | "we loaded the first one here" ; recap of the entry; price not stated | - | none stated |
| 45 | 88 | ADD | long [inferred: buyers / 'up session'; he never says long] | reload 1 | - | "then we reloaded here, then we reloaded here" ; first of two reloads (recap); price and size not stated; trigger not stated | - | none stated |
| 46 | 88 | ADD | long [inferred: buyers / 'up session'; he never says long] | reload 2 | - | "then we reloaded here, then we reloaded here" ; second of two reloads (recap); price and size not stated; trigger not stated | - | none stated |
| 47 | 89 | STOP_SET | long [inferred: buyers / 'up session'; he never says long] | last reload level | protection level | "this one was our protection level" ; role: stop reference; the last reload level; no distance stated | - | none stated |
| 48 | 89 | CONTEXT | long [inferred: buyers / 'up session'; he never says long] | - | result | "we took all the bottom of the up session of the day" ; outcome: 'best session of the month of October'; final P&L not stated | - | none stated |
| 49 | 93 | REJECT | long [inferred: buyers / 'up session'; he never says long] | - | holding for more | "I decided to close" ; rejects holding for a '50 to 60,000 dollar day' (missed profit, not a target) | - | none stated |
| 50 | 95 | LESSON | - | - | risk vs reward | "We risk a really small amount of money to make a really banger day" | - | none stated |
| 51 | 97 | CONTEXT | - | - | prior video | "I showed you before the worst session of the month even if it was recovered" | - | none stated |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 4-5
state (day/week): the session start after a London session of about $10,000; 'a little bit of choppiness'
location: not described (chart only) ; level type: unknown
leading signal: unknown (he calls it a continuation)
trigger: unknown ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: unknown ; % of price: unknown
target: not stated ; distance: unknown ; stated R:R: unknown
management: none stated
exit: "We tried this continuation and we failed" ; exit type: unknown
rejects: none stated
information sources: none stated for this trade
outcome: loss; "we gave back two trades" inside the choppiness; the session gave back about $5,000 (to around 4,500) in total (money as stated, not R)
horizon: unknown
mirror stated?: no - do not assume

TRADE 2 - long (inferred; he never says long) - rows 15-49 (setup rows 7-13; recap rows 44-47)
state (day/week): consolidation area "completely wrecked by buyers"; sellers absorbed; "the day was pretty directional"; best session of October
location: the level where buyers got aggressive after the failed auction of the seller ; level type: consolidation area / other (no VAH/VAL/POC named)
leading signal: sellers absorbed ("a huge amount of information") and a failed auction of the seller
trigger: "aggression of the level of the buyers"; scaled in ("loading and scaling in") ; entered BEFORE or AFTER proof: unknown (first-load timing not shown in words)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated as a price or distance; only a conditional rule, row 10: "putting my position to break even if this level failed"; the last reload level was the "protection level" (row 47) ; distance: unknown ; % of price: unknown
target: "take the top of the day" (row 13); money plan "Close the day above $25,000" (row 23); no price ; distance: unknown ; stated R:R: "risking $980 to make potential $25,000" (open risk to potential, as stated; no ratio spoken)
management: ADD rows 18,45,46 (scale in; two reloads in the recap) ; STOP_MOVE rows 20 (lower risk, mechanism unclear),22 (risk $980),27 (plan: trail on another breakout),30 (plan: risk free or tight stop if the level breaks),33 (stop to zero),35 (covered below this low) ; PARTIAL row 38 ("take other profit")
exit: "this is the reason I closed my trade" (aggression and failed auction after the market exploded from the level) ; exit type: manual
rejects: row 21 not wanting to be in the position if the big trade sell is stopped out (snapback risk) ; row 43 holding for a 40-50,000 dollar session (prefers conservative with a sniper trade) ; row 49 holding for 50-60,000
information sources: absorption, delta / aggressive buyers or sellers, big orders / big trades [new source: big trades as executed prints], order book (buyers wall), swing high/low (below this low), market speed (acceleration), failed auction [new source], consolidation area [new source], time of day (London session before)
outcome: best session of October; risk "around $980" at one point, locked worst case $10,000 then $15,000, "up a gain 9,000 ... around 10,000" early; he says it could have been $40-60,000; final P&L not stated; day above $25,000 is the plan, not the confirmed result
horizon: unknown (video sped up)
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 6 (LESSON): condition "if the session P&L goes back to break even" for "if we go back to break even, we stop the session"
- Row 10 (STOP_SET): condition "if this level failed" for "I will be really fast in putting my position to break even if this level failed"
- Row 11 (CONTEXT): condition "if this level failed" for "if this level failed, this one become the new pivot"
- Row 20 (STOP_MOVE): condition "if this big trade sell gets stopped out" for "So I want to lower my risk"
- Row 21 (REJECT): "I don't want to be in the position" ; reason/context: reason: 'a really fast snapback of the market'
- Row 27 (STOP_MOVE): condition "if we have another breakout" for "if we have another breakout, we can trail our stop in profit"
- Row 30 (STOP_MOVE): condition "if we break down this level" for "if we break down this level, I want to be risk free or with a really tight stop loss"
- Row 35 (STOP_MOVE): condition "buyers took control" for "Now I'm covered below this low"
- Row 38 (PARTIAL): condition "sellers took control but stopped on these big trades" for "So I can take other profit from the market"
- Row 43 (REJECT): "I prefer to be conservative when I have a really good sniper trades" ; reason/context: rejects holding for a '40, 50,000 dollar session' (missed profit, not a target)
- Row 49 (REJECT): "I decided to close" ; reason/context: rejects holding for a '50 to 60,000 dollar day' (missed profit, not a target)

## 3.5 Verbatim anchors

> "The first trades that we took was a continuation short"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "We tried this continuation and we failed"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "if we go back to break even, we stop the session"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "I will be really fast in putting my position to break even if this level failed"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "amazing risk to reward trades to take the top of the day"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "I'm loading and scaling in position"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "I will continue to scale my position as we go"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "So I want to lower my risk"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "I don't want to be in the position"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "My risk goes really low and now I'm risking $980"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "Close the day above $25,000"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "if we have another breakout, we can trail our stop in profit"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "if we break down this level, I want to be risk free or with a really tight stop loss"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "Now my position is stop loss to zero"
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "Now I'm covered below this low"
**Source GPS: fZlNGWvd2Ko | END**

> "So I can take other profit from the market"
**Source GPS: fZlNGWvd2Ko | END**

> "this is the reason I closed my trade"
**Source GPS: fZlNGWvd2Ko | END**

> "I prefer to be conservative when I have a really good sniper trades"
**Source GPS: fZlNGWvd2Ko | END**

> "then we reloaded here, then we reloaded here"
**Source GPS: fZlNGWvd2Ko | END**

> "this one was our protection level"
**Source GPS: fZlNGWvd2Ko | END**

> "I decided to close"
**Source GPS: fZlNGWvd2Ko | END**

## 3.6 Ambiguity flags
- Rows 4-5: TRADE 1 is thin ("continuation short"; "gave back two trades"): count of trades inside, entry, stop and exit are not stated.
- Side of TRADE 2: he never says long; it is inferred from buyers in control, "skyrocket up", "bottom of the up session" (rows 9-42).
- Rows 20-21: "if this big trade sell gets stopped out, I don't want to be in the position because we will have a really fast snapback": a snapback after a sell is stopped would be up, which would help a long; the side held at this moment is unclear. "lower my risk" does not say stop or size.
- Row 35: "covered" (also "you can cover behind this level" earlier): may mean protected by a stop in profit; may be a mistranslation. "Now I'm covered below this low" reads as a stop below the low.
- Row 38: "I can take other profit from the market" may be a partial or a stop raised (the next sentence raises the worst case from $10,000 to $15,000).
- Rows 41-42: he closes after "the market explode[s] from this level" and names "aggression and a failed auction" as the reason; this reads against holding a long while the market then goes up ("skyrocket up"). Not resolved.
- Row 43: "sniper trades" may be "sniper trade" (singular) or a fixed term; kept as written.
- Row 23: "$25,000" is first called "potential"; treated as a day money plan, not a confirmed target. 40-50,000 and 50-60,000 are missed profit, not targets.
- Rows 8-9: "failed auction" is the speaker's own term; it is not in the information-source list, so flagged [new source].

## 7 self-check
1 ENTRY rows: 2; trade blocks: 2 (TRADE 1 starts at row 4, TRADE 2 at row 15). 2 Fields filled (unknown where not stated). 3 Last row pos% 97. 4 Checker line below. 5 Grep for forbidden labels done.

PASS: 0 problem(s)
