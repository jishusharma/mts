# Third check: 8 argon i2_refute rows, independent reading

Method: each row's claim and the ITERATION_2.md gap read first; transcripts in `raw_transcripts_canonical/` read by me; argon quotes checked afterwards. ITERATION_2.md is not edited. Positions are by character offset of the transcript body (thirds).

## Verdict table

| row | gap | verdict | one line |
|---|---|---|---|
| IR-01 | I2-01 | PARTIAL | ORB video (Fabio) waits for the 15 or 30 minute range to finish, then trades the breakout: "skips the first 30 min" is overstated, "waits" stands; 15m is an option, not the rule |
| IR-05 | I2-03 | PARTIAL | Tom's first pass is a line chart plus closing-price count, but the weekly and daily profile still decides balance and setup; "read by profile shape" is not exclusive |
| IR-08 | I2-06 | CONFIRMED | Fabio raises the big-trade filter when volume is high; 60 was one session's setting, not a constant |
| IR-09 | I2-06 | PARTIAL | Fabio says one-minute bars are fine as well as range bars, so the bar-type gap is overstated; filter size and 5m-close trigger parts of I2-06 are untouched |
| IR-14 | I2-08 | REFUTED | Tom's retest passage says the distance shrank each test and the level broke; it is a different speaker and does not contradict "level weaker each test" |
| IR-18 | I2-11 | PARTIAL | Fabio cuts at a dollar loss ($8-9k) AND uses a 3-stop rule; the gap's headline (P&L-keyed) holds, its code note "his rule is a count of stops" is overstated |
| IR-19 | I2-13 | CONFIRMED | The "no order flow for Bitcoin" line is about his long-term on-chain account; he scalps crypto futures with order flow as income (same speaker, other video) |
| IR-23 | I2-17 | PARTIAL | Tom says breakout RR is often 1:1 to 1.5:1 (1.20 inside that); "his stated floors 1.5 to 2.5" is NOT_SEEN as a floor; 1.20 is still OURS |

## Evidence

### IR-01 (I2-01 NY open handling): PARTIAL
Claim: trade the breakout of the first 15m of the NY cash session rather than skipping the first 30m. Gap: he skips or waits the first 30 minutes; our NY block starts at the open.
My reading of cUTsoU-15Tc (Fabio, opening range breakout video): the range is the first 15, 30 or 60 minutes depending on style, and the demo waits for the 30 minutes to complete before looking for the breakout. So he does not trade inside the window; he trades after it, and uses 15 minutes as an alternative window. This agrees with the "wait" half of the gap and weakens "skip the first 30 minutes" (the window itself is the setup).

> "You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "we are waiting for the first 30 minutes of the session to be completed to define clearly the areas where we see breakout."
**Source GPS: cUTsoU-15Tc | MIDDLE**

> "usually I wait for for European time the first 30 minutes of New York opening"
**Source GPS: DyS79Eb92Ug | BEGIN**

Argon cross-check: its quote "You buy or sell the breakout of the first 15 minutes of the cash session" is in the transcript; but it is Fabio describing the generic ORB, not a statement that he skips nothing. Argon's own "rather than skipping" reading is not supported.
Amend I2-01 (gap line 12) to: "NY open handling: he waits for the opening range (15 to 30 minutes, 60 for slower use) to complete, then trades the breakout or retest; Tom stops trading in the first 30 minutes; ours starts at the open with no wait". Delete "skips".

### IR-05 (I2-03 balance by shape): PARTIAL
Claim: balance vs trend can be identified by counting closing prices, not only profile shape. Gap: balance is read by profile shape and picks the setup.
My reading of 3o1VVsfBmmU (Tom): step one is a line chart quick watch, balance or trend, by counting closing prices or other means; step two is the weekly market profile for balance or imbalance and the location; then daily profiles. Elsewhere (m3IMdc7QwN4, jXR1afMy-3o) he ties the rule to profiling combined with the closing price count. No threshold number is stated in 3o1VVsfBmmU: NOT_SEEN.

> "You can pinpoint that by counting closing prices or by all sorts of other means."
**Source GPS: 3o1VVsfBmmU | BEGIN**

> "The next information for us at trades to traders is provided by the weekly market profile."
**Source GPS: 3o1VVsfBmmU | BEGIN**

Argon cross-check: quote present. Its row reads it as an alternative to shape; the transcript makes it the first pass before the profile.
Amend I2-03 (line 14) to: "Balance is read by a closing-price count on a line chart as first pass, then by weekly and daily profile shape, which picks the setup (counter, breakout, trend); ours is a 60-minute box true in 3.1% of windows".

### IR-08 (I2-06 big-trade filter): CONFIRMED
Claim: increases the filter when session volume is high. Gap: fixed big-trade filter 60.
My reading: in jasv3L-d8ZE Fabio changes the filter during the live session because of volume. In Is1HvdfQm5c he says the filter "is on 60" for that chart, with no statement that it is permanent. Units of 60: NOT_SEEN.

> "Today there is a lot of volume. So I need to bigger filter."
**Source GPS: jasv3L-d8ZE | BEGIN**

> "the filter it's on 60"
**Source GPS: Is1HvdfQm5c | MIDDLE**

Argon cross-check: quote present (argon's [01:28] stamp is approximate; the line is near 1:17 to 1:22).
Amend I2-06 (line 17): replace "a fixed big-trade filter 60" with "a big-trade filter he sets by session volume (60 on the Is1HvdfQm5c chart, raised on a high-volume day)". A percentile in v3 is then closer to him than the gap says.

### IR-09 (I2-06 bar type): PARTIAL
Claim: the same setup reads on 1-minute bars as on 40/80 range bars. Gap: he uses range bars; v3 uses 1m bars.
My reading: at the NY open he prefers a range chart because a one-minute candle can be huge and aggregates the data, but in the same breath says "either one minute or either I like to use range". In Is1HvdfQm5c he says the sign of weakness is visible on 80 range, 40 range and one minute. So bar type is a preference, not a requirement. The big-trade filter and the 5m-close trigger parts of I2-06 are not touched by this row.

> "i can go on 80 range i can go on 40 range i can go on one minute is it visible yes"
**Source GPS: Is1HvdfQm5c | MIDDLE**

> "But if you use either one minute or either I like to use range during openings"
**Source GPS: DyS79Eb92Ug | BEGIN**

> "if you do one minute candle you can have huge candle and all the data inside gets aggregated."
**Source GPS: DyS79Eb92Ug | BEGIN**

Argon cross-check: quote present (argon stamp [76:01]; actual is about 1:30:45).
Amend I2-06 (line 17) to: "Execution object: he prefers range bars (40/80) at the open but accepts one-minute; fixed big-trade filter is replaced by a volume-set filter; 5m-close trigger; v3 uses 1m bars and a percentile". Bar type is then not a gap.

### IR-14 (I2-08 level weaker each test): REFUTED
Claim: multiple tests confirm and strengthen a level, contradicting Fabio. Gap: proof is a sequence and volume shape, including "level weaker each test".
My reading of viT_VzF5Fsw (Tom): he says the distance of each test was smaller and that this is crucial, then the market broke the top; he was making the point that his counter trade failed. "Confirming that level" is his phrasing for the third test, but the passage shows shrinking pushes, consistent with weakening. It is Tom, not Fabio, and the translation has unclear referents, so it cannot overturn Fabio's explicit rule. A third voice (qEfES84jwwo) also says more tests make a level more likely to break.

> "The second time the distance was already much smaller. And that is very crucial."
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "The market tested this top once, then twice, and then a third time, really confirming that level before it finally ran down"
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "every time that you attack the level the level gets weaker because other orders gets filled"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "So the more times that you test it, the more orders are getting chewed through and the more likely it actually is to break."
**Source GPS: qEfES84jwwo | END**

Argon cross-check: quote present; argon drops the following sentence about the distance shrinking.
No amendment. Optional wording: add "(Tom's viT_VzF5Fsw reads three tests as confirmation of the level but shows shrinking pushes; unresolved)". Whether weaker-per-test is Fabio-only: STILL OPEN as a Tom-side question.

### IR-18 (I2-11 daily loss): PARTIAL
Claim: cuts losing days at $8-9k after 3-5 stops, not a hard 3-stop count. Gap: P&L-keyed management, 3-stop day, trade-count limits not in the tests; code note says his rule is a count of stops.
My reading: both exist. In DyS79Eb92Ug he cuts at a dollar loss based on his own statistics. In Is1HvdfQm5c he says a maximum of 3 stop losses, then either lowers exposure or usually stops for the day. The dollar level is for a large account, so conversion to R or percent is NOT_SEEN.

> "I noticed that the days that start with three or four or five stop-loss end up with a losing of 20,000 15,000. I start to cut them at 8 9,000"
**Source GPS: DyS79Eb92Ug | MIDDLE**

> "if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day"
**Source GPS: Is1HvdfQm5c | MIDDLE**

Argon cross-check: quote present (argon stamp [100:51]; actual 1:28:42). Argon's "rather than a hard 3-stop" ignores the second quote.
Amend I2-11 Code note (line 205): replace "his rule is a count of stops" with "his rules are a stop count (3, then lower size or stop) and a dollar cut ($8k to $9k on his account, unit conversion NOT_SEEN)".

### IR-19 (I2-13 Fabio and Bitcoin order flow): CONFIRMED
Claim: actively trades crypto with order flow on weekends, contradicting Is1HvdfQm5c. Gap: one line says he does not use it, another says crypto order-flow scalping is extremely profitable.
My reading: DyS79Eb92Ug resolves the tension. He runs separate accounts: a futures order-flow crypto scalping account used as income, and a long-term account that does arbitrage and on-chain based allocation. The Is1HvdfQm5c line is a one-liner in a chat aside with no stated scope; read with DyS79Eb92Ug it fits the long-term Bitcoin holding. Not a real contradiction.

> "Bitcoin guys, I don't use order from Bitcoin. I use on-chain analysis"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "I use the futures order for scalping crypto as income."
**Source GPS: DyS79Eb92Ug | END**

> "I use this income to funnel in my long-term account."
**Source GPS: DyS79Eb92Ug | END**

> "And in the weekend when I'm bored on Saturday, I do crypto order flow"
**Source GPS: DyS79Eb92Ug | END**

Argon cross-check: quote present (stamp [130:07]; actual 1:54:17). Argon says "contradicting"; the better reading is "scoped differently". Is1HvdfQm5c is ASR, so the first quote stays weak evidence.
Amend I2-13 (line 24) to: "Fabio on order flow for Bitcoin: scalps crypto futures with order flow as income (weekends, own account); the 'no order flow for Bitcoin, on-chain' line refers to his long-term account; not a contradiction".

### IR-23 (I2-17 sizing and RR floor): PARTIAL
Claim: breakout RR often 1:1 to 1.5:1, so our 1.20 floor is within his stated range. Gap: our sizing tier and 1.20 RR floor have no source and sit below his stated floors.
My reading: Tom says breakout setups often have RR not above 1:1 or 1.5:1 and compensates with a high hit rate, so 1.20 lies inside what he describes. That is a description of typical breakouts, not a floor, and Tom says the minimum usable RR comes from your hit rate. Fabio's ORB video quotes 1:2 to 1:2.5 with a volume-profile entry. I find no transcript statement of "floors 1.5 to 2.5": NOT_SEEN. The "no source" half stands: 1.20 is OURS.

> "This means that with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1."
**Source GPS: uk4PZV59nYw | END**

> "you have to know your hit rate, and then through your hit rate and the minimum usable risk-reward ratio, you can know"
**Source GPS: 43JaKHRvxHk | END**

> "So now our risk-to-reward is not one to one like the test that we did but maybe it's 1 to2 one to 2.5."
**Source GPS: cUTsoU-15Tc | BEGIN**

Argon cross-check: quote present, GPS END correct.
Amend I2-17 (line 28) to: "Setup grade (AAA = value-area low plus 30 minutes in) drives size; our sizing tier and 1.20 RR floor are OURS; Tom says breakout RR is often 1:1 to 1.5:1, Fabio reports 1:2 to 1:2.5 with order-flow entries; no stated floor seen". Also line 413 "floor at his stated 1.5 to 2.5" should read "label OURS; no stated floor seen".
