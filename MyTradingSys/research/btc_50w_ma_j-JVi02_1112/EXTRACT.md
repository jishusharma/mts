# Extract: "Bitcoin Falls Below the 50W Moving Average" (`j-JVi02_C88`, Benjamin Cowen, published 2026-11-11)

- **Video ID:** `j-JVi02_C88`
- **Analyst:** Benjamin Cowen (context source only: his statements are Context, never signals for MTS)
- **Source:** `raw_transcripts_canonical/j-JVi02_C88_raw.txt` (git-ignored cache; copied from the YouTube transcript panel in Chrome profile "Browser 2" on 2026-11-12 because the scripted fetcher was locked; 142 cues, 3445 words)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. Price levels and calendar claims are his words, not checked against our data unless CHECK.md says so.

## A. What he says (SOURCED, Context)

### C1. The break is a weekly close, six red weeks in a row

Context: the last red week closed back under the 50-week MA; the streak is what he calls an unwinding of the September move.

> "this is our sixth red week in a row"
**Source GPS: j-JVi02_C88 | BEGIN**

### C2. This rally was weaker than the 2019 and 2023 ones

Context: after crossing the 50W MA the earlier cycles ran another 30-40%; this one ran far less, so he reads it as the 2019 pattern (cross, then give it back).

> "it only went up about 9 or 10% after getting through the 50week moving average"
**Source GPS: j-JVi02_C88 | BEGIN**

### C3. Fake-out moves in an apathetic top

Context: his frame for why a cross above the MA failed: a top with no rotation into altcoins makes fake-outs more likely.

> "when you have an apathetic top like 2019 and 2025, you are more prone to having fake out moves"
**Source GPS: j-JVi02_C88 | BEGIN**

### C4. Capital rotation ahead of a big IPO

Context: his explanation for the sell-off if you do not believe the seasonality story. Not testable in our data; treat as narrative.

> "ahead of major IPOs, often times people will free up capital to then go buy that IPO"
**Source GPS: j-JVi02_C88 | MIDDLE**

### C5. He expects a low within months, lower or higher unknown

Context: a scenario, not a level.

> "I think that it'll likely form a low over the next couple of months"
**Source GPS: j-JVi02_C88 | MIDDLE**

### C6. 2018 versus 2026 at the 50W MA

Context: the structural difference he sees between the two years.

> "in 2018 from the July low, we got rejected at the 50we moving average"
**Source GPS: j-JVi02_C88 | END**

### C7. Weak into the next FOMC, judge after it

Context: his timing statement; the next meeting is the one he places in December.

> "Bitcoin stays weak probably through the next FOMC and at that point we can then make a better judgment"
**Source GPS: j-JVi02_C88 | END**

### C8. Levels he watches below the market

Context: his three zones; the first is also near the 20-week MA by his words.

> "the next level would be about 69K and then the next level below that would be about 63 to 64K"
**Source GPS: j-JVi02_C88 | END**

### C9. Stablecoin market cap falling

Context: his liquidity argument for a Q4 low.

> "stable coin market cap is actually going down"
**Source GPS: j-JVi02_C88 | END**

### C10. A fake-out is confirmed by two weekly closes under 83K

Context: his rule for when the up-move is called a fake-out.

> "once you have those two weekly closes below 83K, you're basically confirming that that's nothing more than a fake out"
**Source GPS: j-JVi02_C88 | END**

## B. What is useful for us

- A clean, checkable claim: weekly close under the 50W MA after a re-cross above it. We tested the title claim on our own weekly data (CHECK.md, 12 breaks, n=7 first breaks with a full window): the break alone gave no direction (4 of 7 rallied, 3 fell deep); breaks 1-2 years after a halving-cycle top were followed by -18% to -56% at 26 weeks (OURS reading, n=3).
- His "two weekly closes under a level confirms the fake-out" (C10) is a rule we can code: a prior-high sweep followed by two weekly closes back under the pre-sweep level. This is a candidate for the scenario ledger, not a result.
- His cycle clock (February low, summer low, Q4 low) matches the cycle bottom window already written in BIBLE.md; it adds nothing we did not hold, so it is a second reader, not evidence.

## C. What we do not do

- We do not trade from a narrative (IPO capital rotation, rate-hike seasonality, stablecoin cap): none of it is in our data layers and none has a mechanism we measure.
- We do not take his price zones (72-73K, 69K, 63-64K) as support levels: they are his chart reads (SOURCED words, unverified). The 50W MA value itself is computed independently in CHECK.md as a simple MA (OURS choice; he does not say simple or exponential).
- No signal comes from this video; an analyst call is Context.

## D. What we should do

1. Add the C10 rule to the scenario ledger as a dated BTC scenario (OURS wording: "second weekly close under the pre-sweep level confirms the fake-out"), scored at +4w (2026-12-01) and +12w (2027-01-26) as CHECK.md already proposes.
2. Test the sweep-then-two-closes-back rule on our weekly history (BTC 2015 weekly data is not in our store; 2019, 2021 and 2022 are) and report n; fee-net, no parameter search. Parameter labels: 50W window SOURCED (title), SMA OURS, 2-week confirmation SOURCED (C10), 8-week re-break window OURS.
3. Keep BTC read on its own terms: the cycle phase decides the sign of a 50W break (CHECK.md), so MTS reads the break as a phase marker.

## E. What we learn

- Cowen's current claim is a scenario (low within months, weak into December), not a forecast; his own statements allow both a lower and a higher low.
- His strongest testable idea is a failed breakout confirmed by two weekly closes back under the old level; the narrative parts (IPO, rate hikes) are not testable here.
- A transcript is now cached for this video, so these quotes can be re-verified any time without YouTube.
