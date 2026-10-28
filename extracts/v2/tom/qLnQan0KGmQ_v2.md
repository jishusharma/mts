# V2 extract qLnQan0KGmQ

Method: EXTRACTION_METHOD_V2.md. Read in full, chunks of about 2,000 characters from the first to the last character (4 chunks: pos 0-25, 25-50, 50-75, 75-100). Chart walk-through on a crude oil chart with no price numbers spoken: every level is "here" / "this price range" (the screen is not in the transcript). No stop or target is given as a number.

## 3.1 Header
```
video_id: qLnQan0KGmQ
trader: Tom Vorwald (transcript garbles the name as "Thomas Forward"; first person, "I'm the Champions Maker")
title: Trading world champion reveals: How to find the PERFECT trade entry
instrument_stated: crude oil ("Yes, here we have the crude oil chart")
instrument_inferred: none
tick_size: unknown
session / time of day: unknown (context: "Iran escalation in the Middle East", "highly volatile phase"; swing horizon "trades that last a few days longer")
translation_warning: yes (auto-captioned, names garbled: "Thomas Forward", "Patrick N", "Christopher Radhika"; grammar "risk of reward ratio very good")
body_chars: 8038 (speech after the last "# ---" header; the raw file stacks three header blocks, the checker body after the first "# ---" is 8364 characters)
n_decision_rows: 51
n_trades: 4 (trade 1 short and trade 3 long are shown on the past chart; trade 2 has no stated entry, only a target; trade 4 is a hypothetical "imagine we missed all these trades"). No trade has a stated outcome in money, ticks or R.
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | LESSON | - | - | - | "You have to know the risk of reward ratio very good." | none (not a chart item) | none stated |
| 2 | 2 | LESSON | - | - | - | "You have to plan your trades very good and deep." | none | none stated |
| 3 | 6 | LESSON | - | - | volatility | "the best trades always happen where there's ultimately the highest volatility" | news (escalation phase) | "At least if you're looking for trades that last a few days longer." |
| 4 | 21 | CONTEXT | - | crude oil chart | oil under news | "due to the Iran escalation in the Middle East, crude oil is currently a vehicle with really high volatility" | news | none stated |
| 5 | 26 | LOCATION | unknown | "its fair price" (the high-volume area) | high volume | "if the market returns to its fair price" then "plan a logical trade from there" | HVN/LVN or "volume step" | "if the market returns to its fair price" |
| 6 | 28 | LESSON | - | high volumes | high volume | "Markets are always designed so that they really like to go back to the high volumes." | HVN/LVN or "volume step" | none stated |
| 7 | 31 | CONTEXT | - | high volumes | volatility vs balance | "that's obviously not very likely" (peaceful balance at high volume) | news, HVN/LVN or "volume step" | "with the kind of volatility we're seeing here right now" |
| 8 | 33 | LOCATION | short | "in this price range" (screen only) | price range at high volume | "there's an initial opportunity to execute a trade" | HVN/LVN or "volume step" | none stated |
| 9 | 34 | CONTEXT | short | - | his earlier call | "the market would most likely run until then" (told in the previous video) | HVN/LVN or "volume step" | none stated |
| 10 | 35 | CONTEXT | short | - | what happened | "We had a typical break in here and then the whole thing just dropped." (outcome, no ticks) | price action | none stated |
| 11 | 36 | ENTRY | short | the price range of row 8 | - | "the first trade that was predictable was definitely this short trade" ; order type unknown ; BEFORE or AFTER proof unknown | HVN/LVN or "volume step" | none stated |
| 12 | 39 | ENTRY | unknown | - | planning the next step | "How could you plan that?" [?] (no entry is stated; planning phrase only) ; order type unknown | balance (price action) | none stated |
| 13 | 40 | CONTEXT | unknown | - | structure | "This here is a typical B structure." | profile shape [new source] | none stated |
| 14 | 41 | CONTEXT | unknown | - | selling | "there was aggressive selling here again" | delta / aggressive buyers or sellers | none stated |
| 15 | 42 | CONTEXT | unknown | - | balance | "a balance ... which was below the previous balances" | prior balances (price action) [new source] | none stated |
| 16 | 43 | CONTEXT | unknown | - | supply and demand | "supply and demand have now shifted" | balance location | none stated |
| 17 | 44 | TARGET_SET | unknown | "here and right here" (screen only) | where to exit | "The target was here and right here where you could then look for your exit" | high volume (implied) [?] | none stated |
| 18 | 47 | LESSON | - | volume peaks | absolute volume peaks | "whenever there are absolute volume peaks, the market does special things" | HVN/LVN or "volume step" | none stated |
| 19 | 50 | REJECT | - | - | hindsight objection | "No, we already explained all of that very precisely in the previous video." (rejects "he's showing all that after the fact") | none | none stated |
| 20 | 55 | LOCATION | long | high volume (screen only) | high volume | "where do I have high volume?" | HVN/LVN or "volume step" | "you always have to do the following" (highly volatile phase) |
| 21 | 57 | PROOF | long | high volume | buyers coming in | "Does the proof come that the buyers are actually coming in?" ; BEFORE entry (wait option) | delta / aggressive buyers or sellers | none stated |
| 22 | 58 | ENTRY | long | high volume | - | "the very brave ones just buy here" ; BEFORE proof ; order type unknown | HVN/LVN or "volume step" | none stated |
| 23 | 58 | ENTRY | long | high volume | - | "you can also wait until the proof arrives" ; AFTER proof ; order type unknown | delta / aggressive buyers or sellers | proof arrives |
| 24 | 59 | PROOF | long | small time frame | excessive buying and balance | "you see excessive buying and balance here" ; AFTER entry-or-wait | delta / aggressive buyers or sellers, bar close (small time frame, TF not stated) | "If you go into a small time frame now" |
| 25 | 61 | PROOF | long | small time frame | buying twice | "Then you have proof twice that there is really very strong buying." | delta / aggressive buyers or sellers | none stated |
| 26 | 62 | ENTRY | long | two pullback spots (screen only) | pullback | "options to enter here via pullback or to enter here again via pullback" ; AFTER proof ; order type unknown (pullback) | delta / aggressive buyers or sellers | none stated |
| 27 | 65 | CONTEXT | long | "the last highest liquidity" (screen only) | last high liquidity | "where was the last highest liquidity in terms of the reference ratio?" [?] ; he says "this stretch was predictable for now" | HVN/LVN or "volume step", order book / big orders [?] | none stated |
| 28 | 67 | CONTEXT | long | that liquidity level | bounce | "the market bounced off there and went back again. And bounced off again." | price action | none stated |
| 29 | 68 | TARGET_SET | long | "the next high volume area" | next high volume | "I can plan the next leg up to the next high volume area" | HVN/LVN or "volume step" | "Especially when the market shows me once again that it's working with power" (row 30) |
| 30 | 69 | PROOF | long | these price ranges | acceptance | "it accepts these price ranges" | HVN/LVN or "volume step", market speed ("working with power") | "when the market shows me once again that it's working with power and it accepts these price ranges" |
| 31 | 70 | ENTRY | long | "right here" (screen only) | continuation | "we could plan this trend continuation perfectly right here" ; AFTER proof (rows 24-30) ; order type unknown | acceptance, HVN/LVN or "volume step" | none stated |
| 32 | 73 | REJECT | long | "from here to here" (screen only) | early entry | "Yes, you could but with very high risk." (rejects planning from the earlier, farther point) | none | none stated |
| 33 | 74 | ENTRY | long | "this trade here" (screen only) | the closer location | "Then you could definitely plan this trade here." ; order type unknown | acceptance | none stated |
| 34 | 76 | STOP_SET | long | "right here" (screen only; level not spoken) | risk reference | "The stop loss belonged right here." | unknown (not spoken) | none stated |
| 35 | 76 | LESSON | long | - | risk reward | "the risk reward ratio is gigantic" (no number) | stop and target distances (screen only) | none stated |
| 36 | 77 | LESSON | long | - | entry quality | "you didn't buy the trade at the absolute low, you didn't get that but you have predictability" | none | none stated |
| 37 | 78 | CONTEXT | long | - | hypothetical | "Let's just imagine we missed all these trades" | none | none stated |
| 38 | 79 | LOCATION | long | "these price ranges" (screen only) | balance acceptance | "we want to wait in case the market shows us again, I accept these price ranges" | HVN/LVN or "volume step", bar close [?] | "Always remember where markets are in balance, large market participants accept the prices." |
| 39 | 80 | PROOF | long | price ranges | acceptance quality | "Not with quick spikes but with real acceptance." ; BEFORE entry | market speed, HVN/LVN or "volume step" | not "quick spikes" |
| 40 | 82 | CONTEXT | long | - | last reaction | "Always check what was the previous reaction." | prior reaction at the balance | none stated |
| 41 | 83 | CONTEXT | long | - | last reaction | "Ah, it was bullish" so "the probability is initially higher that this path will then continue upwards" | prior reaction at the balance | "if it was bullish"; "Even if there was a really massive downtrend before" |
| 42 | 86 | ENTRY | long | "from exactly this price range" (screen only) | - | "achievable from exactly this price range" ; order type unknown ; BEFORE or AFTER proof unknown | acceptance | none stated |
| 43 | 87 | TARGET_SET | long | "this price range" (the second one, screen only) | next price range | "to this price range" | HVN/LVN or "volume step" [?] | none stated |
| 44 | 87 | STOP_SET | long | "that was our risk" (level not spoken) | risk | "that was our opportunity and that was our risk" [?] (stop level only on screen) | unknown | none stated |
| 45 | 88 | LESSON | - | - | hit rate | "even if we're only right every second or third time with such a trade, we have a huge risk reward ratio" | none | none stated |
| 46 | 91 | HOLD | long | the price range | balance | "as long as we don't leave this price range again" ; the market keeps balancing and may return to "this point" | HVN/LVN or "volume step" | "as long as we don't leave this price range again, remember via move and balance" |
| 47 | 92 | CONTEXT | long | "this point" (screen only) | return | "the market will continue to balance here and potentially return to this point" | HVN/LVN or "volume step" | same condition as row 46 |
| 48 | 94 | TARGET_SET | long | "the next high volume price" | next high volume | "it looks for the next high volume price and that is your target" | HVN/LVN or "volume step" | "if it accepts new prices" |
| 49 | 96 | LESSON | - | - | - | "you always need two things, the idea and the proof" | none | none stated |
| 50 | 97 | LESSON | - | - | risk reward | "Once you have both, you'll be able to establish a risk reward ratio." | none | idea and proof both present |
| 51 | 98 | LESSON | - | - | discipline | "And you have to stick to that." (the risk reward ratio) | none | none stated |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 8-11
state (day/week): "the market returns to its fair price" after an exhaustion up high (earlier video); "escalation phase", high volatility
location: "here in this price range" (screen only) ; level type: HVN/high volume area ("they really like to go back to the high volumes")
leading signal: planned in the previous video ("our plan where we clearly said if the market returns to its fair price")
trigger: arrival at the high volume price range ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: not stated ; distance: unknown ; % of price: unknown
target: not stated ; distance: unknown ; stated R:R: unknown
management: none stated
exit: not stated ; exit type: unknown ("a typical break in here and then the whole thing just dropped")
rejects: none on this trade
information sources: HVN/LVN or "volume step", news
outcome: the price dropped (no ticks or money stated)
horizon: "trades that last a few days longer" (general)
mirror stated?: no - do not assume

TRADE 2 - unknown side - rows 12-19
state (day/week): after the balance phase "it simply decided, 'Okay, we're taking the next step.'" ; "aggressive selling", balance "below the previous balances", "supply and demand have now shifted"
location: not spoken (screen only) ; level type: balance below previous balances
leading signal: "a typical B structure"
trigger: unknown (no entry stated; row 12 is a planning phrase) ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: not stated ; distance: unknown ; % of price: unknown
target: "The target was here and right here where you could then look for your exit" (screen only) ; distance: unknown ; stated R:R: unknown
management: none stated
exit: "look for your exit" at the target spots ; exit type: unknown
rejects: row 19 hindsight objection answered ("we already explained all of that very precisely in the previous video")
information sources: delta / aggressive buyers or sellers, prior balances [new source: B structure / profile shape]
outcome: not stated
horizon: unknown
mirror stated?: no - do not assume

TRADE 3 - long - rows 20-36
state (day/week): highly volatile phase ; market "bounced off there and went back again. And bounced off again" ; "it's working with power and it accepts these price ranges"
location: "where do I have high volume" (screen only) ; level type: HVN/high volume area; later "the last highest liquidity"
leading signal: high volume area planned in advance ("Yes, you could plan that here")
trigger: wait for proof of buyers at high volume, then pullback entry, later "trend continuation ... right here" ; entered BEFORE or AFTER proof: both stated as options: BEFORE ("the very brave ones just buy here", row 22) and AFTER ("wait until the proof arrives", rows 23, 26, 31)
entry order type: unknown ; placed before the touch: unknown
initial stop: "The stop loss belonged right here." (screen only, level not spoken) ; distance: unknown ; % of price: unknown
target: "the next leg up to the next high volume area" ; distance: unknown ; stated R:R: "gigantic" (no number)
management: none stated (no PARTIAL, STOP_MOVE or ADD)
exit: not stated ; exit type: unknown
rejects: row 32 planning "from here to here" ("with very high risk"); he accepts not buying "at the absolute low" (row 36)
information sources: HVN/LVN or "volume step", delta / aggressive buyers or sellers, bar close (small time frame, TF not stated), market speed, news
outcome: not stated ("risk reward ratio is gigantic", no ticks or money)
horizon: swing ("trades that last a few days longer")
mirror stated?: no - do not assume

TRADE 4 - long - rows 37-48
state (day/week): hypothetical, "Let's just imagine we missed all these trades" ; previous reaction at the balance "was bullish"
location: "these price ranges" where the market shows acceptance (screen only) ; level type: acceptance area / balance
leading signal: "Always check what was the previous reaction"
trigger: "real acceptance" (not "quick spikes") ; entered BEFORE or AFTER proof: unknown (acceptance is read first, row 39; the entry row 42 follows)
entry order type: unknown ; placed before the touch: unknown
initial stop: "that was our risk" (level not spoken) ; distance: unknown ; % of price: unknown
target: "to this price range"; "the next high volume price and that is your target" ; distance: unknown ; stated R:R: "a huge risk reward ratio"
management: HOLD row 46 only; no PARTIAL, STOP_MOVE or ADD
exit: not stated ; exit type: unknown
rejects: "quick spikes" are not acceptance (row 39)
information sources: HVN/LVN or "volume step", prior reaction, market speed
outcome: not stated
horizon: unknown
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 19 (REJECT): the "after the fact" objection, answered with the previous video.
- Row 32 (REJECT): planning the trade from the farther point is "very high risk".
- Row 39 condition: "Not with quick spikes but with real acceptance."
- Row 5 condition: "if the market returns to its fair price".
- Row 3 condition: the volatility claim holds for trades that last a few days.
- Row 7 condition: peaceful balance at high volume is unlikely under current volatility.
- Rows 30, 29 condition: the market "is working with power and it accepts these price ranges".
- Row 41 condition: "if it was bullish, the probability is initially higher that this path will then continue upwards."
- Rows 46, 47 condition: "as long as we don't leave this price range again" (hold; this is the only stop-like rule in words).
- Row 48 condition: "if it accepts new prices" then the next high volume price is the target.
- Row 50 condition: idea and proof both present before a risk reward ratio is set.

## 3.5 Verbatim anchors
> "You have to know the risk of reward ratio very good."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "You have to plan your trades very good and deep."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "the best trades always happen where there's ultimately the highest volatility."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "At least if you're looking for trades that last a few days longer."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "due to the Iran escalation in the Middle East, crude oil is currently a vehicle with really high volatility."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "if the market returns to its fair price, we have the opportunity to plan a logical trade from there."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "Markets are always designed so that they really like to go back to the high volumes."
**Source GPS: qLnQan0KGmQ | BEGIN**

> "But with the kind of volatility we're seeing here right now, that's obviously not very likely."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "there's an initial opportunity to execute a trade"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "I also told you that the market would most likely run until then."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "We had a typical break in here and then the whole thing just dropped."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "That means the first trade that was predictable was definitely this short trade."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "How could you plan that?"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "This here is a typical B structure."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "This means there was aggressive selling here again and there were reasons for it."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Then there was a balance as you can see, which was below the previous balances."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "This means that supply and demand have now shifted."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "The target was here and right here where you could then look for your exit"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "whenever there are absolute volume peaks, the market does special things."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "No, we already explained all of that very precisely in the previous video."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "You have to look, where do I have high volume?"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Does the proof come that the buyers are actually coming in?"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Sure, the very brave ones just buy here"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "but you can also wait until the proof arrives."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "If you go into a small time frame now, you see excessive buying and balance here."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Then you have proof twice that there is really very strong buying."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Now you have options to enter here via pullback or to enter here again via pullback."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "I look, where was the last highest liquidity in terms of the reference ratio?"
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Oh, but now the market bounced off there and went back again."
**Source GPS: qLnQan0KGmQ | END**

> "In theory, I can plan the next leg up to the next high volume area."
**Source GPS: qLnQan0KGmQ | END**

> "Especially when the market shows me once again that it's working with power and it accepts these price ranges."
**Source GPS: qLnQan0KGmQ | END**

> "And therefore we could plan this trend continuation perfectly right here."
**Source GPS: qLnQan0KGmQ | END**

> "Yes, you could but with very high risk."
**Source GPS: qLnQan0KGmQ | END**

> "Then you could definitely plan this trade here."
**Source GPS: qLnQan0KGmQ | END**

> "The stop loss belonged right here."
**Source GPS: qLnQan0KGmQ | END**

> "And you can already see here the risk reward ratio is gigantic."
**Source GPS: qLnQan0KGmQ | END**

> "And no, you didn't buy the trade at the absolute low"
**Source GPS: qLnQan0KGmQ | END**

> "Let's just imagine we missed all these trades"
**Source GPS: qLnQan0KGmQ | END**

> "we want to wait in case the market shows us again, I accept these price ranges."
**Source GPS: qLnQan0KGmQ | END**

> "Not with quick spikes but with real acceptance."
**Source GPS: qLnQan0KGmQ | END**

> "Always check what was the previous reaction."
**Source GPS: qLnQan0KGmQ | END**

> "the probability is initially higher that this path will then continue upwards."
**Source GPS: qLnQan0KGmQ | END**

> "achievable from exactly this price range"
**Source GPS: qLnQan0KGmQ | END**

> "to this price range"
**Source GPS: qLnQan0KGmQ | END**

> "And so you can see once again that was our opportunity and that was our risk."
**Source GPS: qLnQan0KGmQ | END**

> "even if we're only right every second or third time with such a trade, we have a huge risk reward ratio"
**Source GPS: qLnQan0KGmQ | END**

> "as long as we don't leave this price range again"
**Source GPS: qLnQan0KGmQ | END**

> "the probability is always there that the market will continue to balance here and potentially return to this point."
**Source GPS: qLnQan0KGmQ | END**

> "Or if it accepts new prices, then it looks for the next high volume price and that is your target."
**Source GPS: qLnQan0KGmQ | END**

> "you always need two things, the idea and the proof."
**Source GPS: qLnQan0KGmQ | END**

> "Once you have both, you'll be able to establish a risk reward ratio."
**Source GPS: qLnQan0KGmQ | END**

> "And you have to stick to that."
**Source GPS: qLnQan0KGmQ | END**

## 3.6 Ambiguity flags
- Row 11: "this short trade" is the only statement that the first trade was short; entry order type, proof timing and level are not given.
- Row 12: "How could you plan that?" is a planning question; no entry, side or price is stated for the B-structure idea (trade 2). The side is unknown; "aggressive selling" and a balance "below the previous balances" may point down but he does not say short or long.
- Row 17: "here and right here" are screen positions; the level type of the target is not spoken.
- Row 27: "the last highest liquidity in terms of the reference ratio" is odd wording (probably auto-caption); the level role (target, caution, reference) is not stated. Do not resolve.
- Rows 22 and 23 contradict in style but not in fact: he names both an entry before proof ("very brave ones") and after proof; he does not say which he took.
- Row 34 and row 44: "The stop loss belonged right here" and "that was our risk" give no level or distance in words; the stop level is on the screen only.
- Row 38: "I accept these price ranges" and "Always remember where markets are in balance, large market participants accept the prices" describe acceptance; no bar close or time is spoken.
- Row 41: "Ah, it was bullish" gives the previous reaction as bullish; the side long follows only from "continue upwards".
- Row 46: "as long as we don't leave this price range again" is a hold condition for the balance idea; he does not call it a stop.
- Names in the intro are garbled ("Thomas Forward", "Patrick N", "Christopher Radhika").

## 3.7 Self-check
- Last decision row pos% is 98. ENTRY rows: 11, 12, 22, 23, 26, 31, 33, 42 (trade blocks start at rows 8, 12, 20, 37; rows 8, 20, 37 are LOCATION rows that precede the first ENTRY of each block, rows 11, 12, 22, 42 are the first ENTRY of each).
- Terms checked: none of the rule-label codes or the word for rule tiers appears; the uppercase letters "CT" occur only inside the words REJECT and PERFECT.

PASS: 0 problem(s)
