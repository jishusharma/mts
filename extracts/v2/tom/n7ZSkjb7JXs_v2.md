# V2 extract n7ZSkjb7JXs

Method: EXTRACTION_METHOD_V2.md. Read in full in about 2,000-character chunks, start to end. One short live commentary on a pre-market DAX future short; no outcome figure is spoken in the transcript.
The raw file stacks three `# ---` header blocks; the body is the text after the last one (12928 characters). The first header says `Word count: 2467`, the second `2436`, the third `2416` (the third names video id `14_n7ZSkjb7` with `Unknown title`); not resolved here.

## 3.1 Header
```
video_id: n7ZSkjb7JXs
trader: Tom Vorwald (assumed from the task; the transcript is first person, "I give you a deep  explanation", and gives no name)
title: $3,400 in 30 minutes: This is how a World Champion ACTUALLY trades
instrument_stated: DAX future ("a live trade in the DAX future"; the intro spells it "Dex future"); also gold futures and NASDAQ futures as markets he watches
instrument_inferred: none
tick_size: unknown (the only prices spoken are "480 to 491" and "57", units not stated)
session / time of day: pre-market, "this morning", before the cash open ("the closer we get to the cash open"); the video title says 30 minutes, the transcript gives no clock time
translation_warning: yes ("I translate it with AI because it's easier for you because I'm not a native English  speaker"; cleaned transcript with cut sentences)
body_chars: 12928
n_decision_rows: 61
n_trades: 1
```
Money: the title says $3,400; the spoken words are only "I earned a lot of money. It was easy money". The title figure is not tied to a row.

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | CONTEXT | short | DAX future, pre-market | live chart, pre-market overview | "So, this morning we're starting with a live trade in the DAX future" | time of day | none stated |
| 2 | 8 | ENTRY | short | same area | - | "Why am I already going short in the DAX future before the market opens" | time of day (pre-market) | none stated; order type unknown; entered before proof (he says "too early", row 4) |
| 3 | 8 | LOCATION | short | "a really great area" (no price) | price area | "we've just reached a really great area here" | not named | none stated |
| 4 | 9 | ERROR | short | - | - | "I was already a bit too early this morning." | - | none stated |
| 5 | 9 | EXIT | short | - | - | "Took a stop loss as well." | - | none stated; earlier attempt stopped out, level and size not stated (told in summary) |
| 6 | 11 | CONTEXT | short | 480 to 491 | past targets | "the market has already reached its targets in the 480 to 491 area" | not named (past targets) | none stated |
| 7 | 11 | PROOF (AFTER) | short | 480 to 491 area | reaction | "There was also an immediate quite aggressive reaction to the significant downside there." | market speed | none stated |
| 8 | 15 | CONTEXT | short | P setup, resistance area | profile shape | "I immediately see that we have a beautiful P setup here." | today's profile | none stated |
| 9 | 16 | PROOF (AFTER) | short | resistance area | liquidity at the top | "moved into the resistance area" | single prints / thin liquidity [?] | none stated |
| 10 | 17 | TARGET_SET | short | retrace of the move (no price) | no base under the move | "the probability of us retracing this entire move down here is simply high because there" | today's profile (no base) | expectation, not an order |
| 11 | 18 | LESSON | short | resistance zone | reaction at resistance | "whenever there's a corresponding reaction at such a resistance zone, it's naturally an idea for" | order book / big orders [?] | "whenever there's a corresponding reaction" |
| 12 | 19 | LESSON | short | pre-market | time of day | "I also like to do this pre-market because I just know that with high probability" | time of day | none stated |
| 13 | 21 | CONTEXT | short | today's VPO | point of control | "we have today's Vpo that is the point of control the area where the market" | VAH/VAL/POC (today's VPO) | none stated |
| 14 | 22 | PROOF (AFTER) | short | above today's VPO | liquidity above | "There simply wasn't any more liquidity above which you can see perfectly here." | order book / big orders | none stated |
| 15 | 24 | TARGET_SET | short | "where the last liquidity started" (no price) | start of liquidity | "just sweep the market again down here where the last liquidity started" | order book / big orders | expectation ("That's why I assume") |
| 16 | 25 | CONTEXT | - | gold futures | gold chart | "I'm running a trade there where I see a similar picture." | other market (gold futures) | side not stated |
| 17 | 26 | CONTEXT | - | gold futures | news-driven rise | "the risk there is much higher since the market is currently being driven so strongly" | news, other market (gold) | "you really need to be cautious" |
| 18 | 29 | CONTEXT | short | last week's value | weekly profile, block, highs | "we're above last week's value. We're above the block, but up here we still had" | weekly profile, swing high | none stated |
| 19 | 31 | HOLD | short | equilibrium | return to value | "as long as that's the case, we let the trade run and simply wait to" | weekly profile | "the probability that the market will first return to equilibrium here is simply there" / "as long as that's the case" |
| 20 | 32 | PROOF (AFTER) | short | top | footprint | "the liquidity was no longer pushed further upward." | footprint | none stated |
| 21 | 34 | LESSON | short | - | risk reward | "all we have is a riskreward ratio that we can consider for ourselves" | - | none stated; no number stated |
| 22 | 36 | REJECT | short | - | waiting | "trying to intervene in any way right now is absolutely suboptimal." | - | reason: "we have absolutely no influence over what the market ultimately does" |
| 23 | 37 | ADD | short | below the "report" [?] (VPO?) | liquidity pushed below | "if I see that the market starts to push liquidity below the report is to" | order book / big orders | conditional, not executed here: "if I see that the market starts to push liquidity below the report" |
| 24 | 37 | STOP_MOVE | short | "above the last major trades" | big trades | "move the stop-loss up here above the last major trades accordingly" | order book / big orders | conditional on the ADD in the row above; planned, not executed |
| 25 | 38 | REJECT | short | - | time of day | "taking on too much risk at this time of day isn't really that effective in" | time of day | none stated |
| 26 | 40 | CONTEXT | short | DAX | sentiment | "I always check the UX sentiment." | [new source] sentiment indicator ("UX sentiment" [?]); small derivatives traders | "a huge number of people are long" |
| 27 | 41 | CONTEXT | short | index stocks | constituents | "I also look at which stocks in the index are currently strong and which are" | other market (index stocks: "rhyme" weak [?], "Conti" strong [?]) | none stated |
| 28 | 43 | CONTEXT | short | Bitcoin | Bitcoin strength | "What also stands out to me is that Bitcoin isn't as strong as it often" | other market (Bitcoin) | none stated |
| 29 | 45 | HOLD | short | - | patience | "So I'm keeping calm and just letting the market decide what it wants to decide." | - | none stated |
| 30 | 46 | PROOF (AFTER) | short | "back to break" [?] | liquidity | "Even here, I still don't see any liquidity." | order book / big orders | none stated |
| 31 | 47 | ADD | short | same area | risk small | "So, I'm going to add another position here because the risk is extremely small for" | order book / big orders | "the upper resistance seems to be holding"; "Otherwise, we'll lose the trade"; order type unknown |
| 32 | 48 | CONTEXT | short | upper resistance | resistance holding | "That means the upper resistance seems to be holding." | order book / big orders | "Otherwise, we'll lose the trade" |
| 33 | 50 | CONTEXT | - | gold futures | gold stalling | "gold is basically stagnating, almost asleep up there." | other market (gold) | none stated |
| 34 | 52 | CONTEXT | - | NASDAQ | NASDAQ correcting | "up here I see the NASDAQ correcting as well" | other market (NASDAQ) | none stated |
| 35 | 55 | CONTEXT | short | cash open | time of day | "the closer we get to the cash open where by the way I also want" | time of day (cash open) | "the closer we get to the cash open" |
| 36 | 57 | PROOF (AFTER) | short | under the VPO | no buyers | "What you can also see here now under the VPO at the Vpo is that" | VAH/VAL/POC (VPO), order book | none stated |
| 37 | 61 | LESSON | short | - | supply and demand | "Markets always want to go where supply and demand are being traded well and we" | - | none stated |
| 38 | 64 | ERROR | short | after the significant breakout | stops | "the protective stops were unfortunately placed in a particularly unfavorable area" | - | none stated; refers to the earlier stopped attempt [?] |
| 39 | 65 | ADD | short | same area | structure accepted | "We carefully scaled back into the market at this precise point" | market structure | retold after the fact; same event as the ADD at row 31 or a second add [?] |
| 40 | 68 | TARGET_SET | short | start of the impulse (no price) | supply and demand zone | "I assume we'll go to the start of the corresponding impulse" | order book / big orders ("no liquidity present here") | "if it drops down here and briefly accepts supply and demand" |
| 41 | 72 | PROOF (AFTER) | short | below the range | speed | "the market is starting to pick up speed below it." | market speed | none stated |
| 42 | 74 | LOCATION | short | 57 ("liquidity at 57") | liquidity | "what happens here below this liquidity at 57, right where we are now" | order book / big orders | "below that, we just need to see a bit of momentum so that our trade ends well" |
| 43 | 75 | PARTIAL | short | 57 area | no action | "So, I've now closed a small position here" | order book / big orders, market speed | reason: "the market wasn't showing any more action there for the time being" |
| 44 | 77 | HOLD | short | remaining position | risk | "And now I just can't lose any more money with this trade." | - | no stop move stated; flagged in section 3.6 |
| 45 | 80 | PROOF (AFTER) | short | balance | 5-minute close | "we also haven't had a closing price below the balance here on the 5-minute chart" | bar close (5m) | none stated |
| 46 | 81 | PROOF (AFTER) | short | below the bell | order book | "We had an air pocket in the order book." | order book / big orders, HVN/LVN | none stated |
| 47 | 82 | STOP_SET | short | above the "bell" of trading volume (no price) | volume bell, air pocket | "which is why the stop loss was set above the bell" | HVN/LVN or volume step ("bell of trading volume") | stated after the fact; no distance |
| 48 | 83 | PARTIAL | short | same as the partial at row 43 | no follow-up sell orders | "That was the reason why I took a take-profit there at first, just to avoid" | order book / big orders | restated explanation of row 43 (same event) [?] |
| 49 | 85 | HOLD | short | remaining position | liquidity below | "then I'll decide how to handle the remaining position" | order book / big orders | "if it does drop down here and briefly generates liquidity" |
| 50 | 86 | CONTEXT | short | above today's VPO | thinned volume | "whether the market above today's Vpo where the trading volume has thinned out up here" | VAH/VAL/POC (VPO), HVN/LVN | none stated |
| 51 | 89 | CONTEXT | short | the open | time of day | "and then most likely liquidity will be pushed downward at first." | time of day (market open) | "the market is about to open" |
| 52 | 90 | LESSON | - | - | experience | "you need an incredible amount of experience to trade something like this." | - | none stated |
| 53 | 91 | CONTEXT | - | gold | profit taking | "people who are looking at the pre-market and see, oh, we've made good profits are" | other market (gold) | none stated |
| 54 | 94 | PROOF (AFTER) | short | "this step" [?] | speed | "because the market has slowed down here again." | market speed, order book | none stated |
| 55 | 95 | CONTEXT | short | - | order book | "Now, what's crucial is where liquidity is being pushed in." | order book / big orders | none stated |
| 56 | 96 | LOCATION | short | 57 | 57 | "I'm going to take a quick look at what's happening at 57 and then I'll" | order book / big orders | decision pending on 57 |
| 57 | 97 | PARTIAL | short | 57 | liquidity | "Exactly. I'm taking out" | - | sentence cut off in the transcript: what is taken out is not stated [?] |
| 58 | 97 | PROOF (AFTER) | short | 57 area | liquidity | "the market isn't generating any liquidity here at all, which means the probability of a" | order book / big orders | none stated |
| 59 | 98 | STOP_MOVE | short | "back above here" (level not stated) | pullback risk | "I'm about to close my position with a stop-loss as soon as we move back" | - | "or if it breaks through, then I'm happy" |
| 60 | 99 | PROOF (AFTER) | short | low volume node | LVN | "You can see it here at this low volume node." | HVN/LVN or volume step | none stated |
| 61 | 99 | EXIT | short | - | no liquidity | "And now it's over. We're out." | order book / big orders | none stated; exit type unknown (stop-loss or manual) |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 2-61
state (day/week): pre-market; "we're above last week's value. We're above the block, but up here we still had lower highs for now"; P setup broke up into the resistance area with no liquidity above (rows 8-9, 18)
location: "a really great area" ; the resistance zone above today's VPO (rows 3, 9-14, 32) ; level type: acceptance area / VPO / resistance zone (no price given)
leading signal: no liquidity above the P setup breakout, "absolutely no base here", footprint shows liquidity no longer pushed up (rows 9-10, 14, 20)
trigger: at location, ahead of proof ("I was already a bit too early this morning") ; entered BEFORE or AFTER proof: before (the first attempt was stopped out, rows 4-5; he scaled back in, rows 31 and 39)
entry order type: unknown ; placed before the touch: unknown
initial stop: "the stop loss was set above the bell" (the bell of trading volume), stated after the fact (row 47) ; distance: not stated ; % of price: unknown (no stated price and distance)
target: no price target. Expectations only: "retracing this entire move down here" (row 10), "where the last liquidity started" (row 15), "the start of the corresponding impulse" (row 40) ; distance: not stated ; stated R:R: unknown (he says only "a riskreward ratio that we can consider for ourselves")
management: ADD row 31 (and row 39, retold, same event or a second add [?]); conditional ADD row 23 with STOP_MOVE row 24 (planned, "above the last major trades", not executed); PARTIAL row 43 (explained again in row 48, same event); PARTIAL row 57 (sentence cut off [?]); STOP_MOVE row 59 ("close my position with a stop-loss as soon as we move back above here", level not stated)
exit: "And now it's over. We're out." after "the market isn't generating any liquidity here at all" (rows 58-61) ; exit type: unknown (stop-loss or manual)
rejects: intervening (row 22, "absolutely suboptimal"); "taking on too much risk at this time of day" (row 25)
information sources: today's profile / P setup, VAH/VAL/POC (today's VPO), weekly profile, swing high (lower highs), footprint, order book / big orders, HVN/LVN (bell, air pocket, low volume node), market speed, bar close (5m), time of day (pre-market, cash open), other market (gold, NASDAQ, Bitcoin, index stocks), [new source] sentiment indicator
outcome: "I earned a lot of money. It was easy money" (intro, not tied to a row); title says $3,400 in 30 minutes ; R: unknown
horizon: pre-market up to the cash open; the title says 30 minutes
mirror stated?: no - do not assume
```
Earlier attempt: stopped out (rows 4-5), no level, size or time given. It is kept inside TRADE 1 because the entry row (row 2) is its only ENTRY statement; whether the live position is a new trade after that stop is not said (section 3.6).

## 3.4 Rejections and conditions
- Row 22 (REJECT): do not intervene now; reason "we have absolutely no influence over what the market ultimately does".
- Row 25 (REJECT): do not take on too much risk at this time of day.
- Row 19 condition: hold "as long as" the market is expected to return to equilibrium ("the probability that the market will first return to equilibrium here is simply there").
- Row 23 condition: add only "if I see that the market starts to push liquidity below the report"; then move the stop "above the last major trades" (row 24).
- Row 31 condition: add because "the upper resistance seems to be holding"; "Otherwise, we'll lose the trade" (rows 31-32).
- Row 35: "I also want to reduce risk" as the cash open nears.
- Row 42 condition: "below that, we just need to see a bit of momentum so that our trade ends well".
- Row 49 condition: if it "briefly generates liquidity" lower, "then I'll decide how to handle the remaining position".
- Row 59 condition: close "as soon as we move back above here or if it breaks through".

## 3.5 Verbatim anchors
> "Why am I already going short in the DAX future before the market opens"
**Source GPS: n7ZSkjb7JXs | BEGIN**

> "Took a stop loss as well."
**Source GPS: n7ZSkjb7JXs | BEGIN**

> "the probability of us retracing this entire move down here is simply high because there was absolutely no base here"
**Source GPS: n7ZSkjb7JXs | BEGIN**

> "just sweep the market again down here where the last liquidity started"
**Source GPS: n7ZSkjb7JXs | BEGIN**

> "trying to intervene in any way right now is absolutely suboptimal."
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "if I see that the market starts to push liquidity below the report is to add another position"
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "move the stop-loss up here above the last major trades accordingly"
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "taking on too much risk at this time of day isn't really that effective in my opinion."
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "So, I'm going to add another position here because the risk is extremely small for me right now."
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "We carefully scaled back into the market at this precise point"
**Source GPS: n7ZSkjb7JXs | MIDDLE**

> "I assume we'll go to the start of the corresponding impulse"
**Source GPS: n7ZSkjb7JXs | END**

> "So, I've now closed a small position here"
**Source GPS: n7ZSkjb7JXs | END**

> "which is why the stop loss was set above the bell"
**Source GPS: n7ZSkjb7JXs | END**

> "That was the reason why I took a take-profit there at first, just to avoid any further risks."
**Source GPS: n7ZSkjb7JXs | END**

> "Exactly. I'm taking out"
**Source GPS: n7ZSkjb7JXs | END**

> "I'm about to close my position with a stop-loss as soon as we move back above here"
**Source GPS: n7ZSkjb7JXs | END**

> "And now it's over. We're out."
**Source GPS: n7ZSkjb7JXs | END**

> "Pre-market session trading is it good or is it very dangerous?"
**Source GPS: n7ZSkjb7JXs | BEGIN**

> "So, I've now closed a small position here because I simply saw that the market wasn't showing any more action there for the time being."
**Source GPS: n7ZSkjb7JXs | END**

> "And that's why I'm about to close my position with a stop-loss as soon as we move back above here or if it breaks through, then I'm happy."
**Source GPS: n7ZSkjb7JXs | END**

## 3.6 Ambiguity flags
- Row 2/5: "I'm already going short" (present tense) next to "Took a stop loss as well": unclear whether the live short is the first entry or a re-entry after the stop (rows 4, 31, 39).
- Row 23: "the report" is probably "VPO" or "the range" (transcript wording kept).
- Row 26: "UX sentiment" is not a known indicator name; may be a mis-transcription.
- Row 27: "rhyme" (weak) and "Conti" (strong) look like auto-captioned stock names; not resolved.
- Row 30: "we're back to break" is unclear.
- Row 31 vs 39: "add another position here" and "carefully scaled back into the market" may be the same add or two adds.
- Row 43 vs 48: both are about the "small position" closed; the second tells the reason again ("took a take-profit there at first"). Counted as one event, two rows.
- Row 44: "I just can't lose any more money with this trade" suggests a break-even stop or locked profit; no stop move is stated.
- Row 45: "no closing price below the balance" for a short; the side of the balance is not stated.
- Row 46: "the bell of trading volume" is probably a high volume area on the profile; its price is not stated.
- Row 57: "Exactly. I'm taking out" is cut off in the transcript.
- Row 59: "stop-loss as soon as we move back above here" is read as a stop on a move back up; new level not stated, and a few words later he says "if it breaks through, then I'm happy".
- Row 61: no word says whether the exit was the stop or a manual exit.
- Header: the title figure ($3,400 in 30 minutes) is not spoken; the transcript has "I earned a lot of money".

## 3.8 Self-check
- Last decision row pos% is 99 (>= 95). One ENTRY row, one trade block.
- Terms from section 7 item 5: the capital letters CT appear only inside the copied title word ACTUALLY.

Checker: PASS: 0 problem(s)
