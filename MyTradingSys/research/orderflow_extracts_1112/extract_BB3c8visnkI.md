# Order-flow extract: How to Use Volume Profile Like a Pro! (`BB3c8visnkI`)

- **Video ID:** `BB3c8visnkI`
- **Analyst:** Tom Vorwald (@TomVorwald), published 2026-10-30; analyst statements are context, never signals
- **Source:** `raw_transcripts_canonical/BB3c8visnkI_raw.txt` (browser transcript panel, 104 cues, 2186 words; on disk, no network; position = third of transcript)
- **Scope:** order-flow idea only (where volume traded, where it did not, acceptance vs rejection of value). BTC is read on its own terms; his index-futures cash session, daily-profile clock and gap talk are not carried (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## What is useful for us

### R1. High-volume price = balance (SOURCED)

Rule: Where much volume traded, supply and demand are in balance; this is the reference "fair" zone.

> "Where a lot of liquidity was traded, supply and demand are usually in balance."
**Source GPS: BB3c8visnkI | BEGIN**

### R2. Low-volume nodes are where price zips through (SOURCED)

Rule: Price ranges with little traded volume are crossed fast; they mark the dividing line between an old and a new range.

> "These price ranges are called low volume nodes."
**Source GPS: BB3c8visnkI | BEGIN**

### R3. The low-volume zone matters more than the point of control (SOURCED)

Rule: Read how price behaves in the thin zones, not only at the point of control; thin zones show where price may strive to return.

> "what's much more crucial for us is how the market behaves in these price ranges where very little liquidity occurred"
**Source GPS: BB3c8visnkI | MIDDLE**

### R4. Acceptance of a new range (SOURCED)

Rule: After a fast cross of a thin zone, new volume building above (or below) means the new range is accepted.

> "This new fair price range where the market is now generating new liquidity is apparently being accepted by the market."
**Source GPS: BB3c8visnkI | BEGIN**

### R5. Return to liquidity after leaving a range (SOURCED)

Rule: After a break out of a range, price tends to come back into high-volume area to find participants.

> "because the market always likes to return to high liquidity to see if it can find trading participants there again."
**Source GPS: BB3c8visnkI | MIDDLE**

### R6. Value area = 70% of volume (SOURCED)

Rule: The value area is the band holding 70% of the period's volume (one week in his example); its edges are the levels.

> "within this zone here the market has traded 70% of the total liquidity for this week."
**Source GPS: BB3c8visnkI | MIDDLE**

### R7. 70/30 claim: imbalance runs away only about 30% (SOURCED, his claim, not adopted)

Rule: He says a break out of balance continues only about 30% of the time and returns the other 70%.

> "But unfortunately that is only the case about 30% of the time and the other 70% he will try and strive to run back here."
**Source GPS: BB3c8visnkI | MIDDLE**

### R8. Gaps do not have to close (SOURCED)

Rule: If value shifted (trend profile), the gap can stay open; gap-fill is not automatic.

> "Now, many people say yes, then the gap will be closed. No, that doesn't have to be the case at all."
**Source GPS: BB3c8visnkI | END**

### R9. Test of the old edge then acceptance (SOURCED)

Rule: Price breaks out, tests the value area high from above, rejects and finds equilibrium higher: the sequence rejection then acceptance sets up the move.

> "the market tested exactly there and moved back up and found its equilibrium."
**Source GPS: BB3c8visnkI | END**

## What we do not do

| Item | Why |
|---|---|
| Cash-session daily profiles ("only show you the period where the so-called cash session is") | index-futures clock; BTC trades 24h, no cash session (decision 2026-11-12) |
| Gap trading from daily open vs prior close | BTC has no overnight gap; our UTC-day boundary is OURS, not a market event |
| Trading his drawn charts or price levels as signals | analyst statements are context only |
| Adopting 60-70% balance / 30% imbalance as a BTC rate | his number; BTC measured 44% for the 80% rule (value_area_acceptance_2026-11-05) |

## What we should do

- Keep value-area / acceptance reads as context only until a frozen, fee-net test passes. (OURS)
- Add low-volume-node pass-through as the one volume-profile idea no study has tested (see idea 3). (OURS)

## What we learn

- The video's whole content is one idea: price accepted or rejected relative to the prior value area decides continuation vs return. It gives no entry, stop or target rule; there is nothing to copy as parameters. (OURS)
- Our measured BTC rates are lower than his (80% rule 44%, n=493, descriptive, no fees), so the claim does not transfer as stated. (OURS)

## Testable ideas (frozen rules; every number OURS, none from Tom)

| # | Frozen rule | Tested before? |
|---|---|---|
| 1 | Acceptance continuation: previous UTC day value area (70% of 1m volume, 0.05% price buckets); after two consecutive 30m closes below VAL (above VAH) go short (long) at the next open; exit 60 min; taker fee both sides; placebo same hours | Partly. `value_area_acceptance_2026-11-05` reports 77% same-day half-width drift, descriptive, no fees, placebo pending; census ACCEPTED -0.096 R gate-pass (n=2798). No frozen fee-net test. `btc_of_level_auction_1112` B1 uses VAH/VAL as levels for absorption, not acceptance |
| 2 | Rejection return: close of a 30m bar back inside the previous-day value area after a close outside it: trade toward POC; stop at the outside extreme; exit at POC or 24 bars | Partly. 80% rule 44% reach (R85, descriptive); return to prior-day value R79 post-hoc placebo, R80 FAIL (daily, CI lower -0.3 pp). No fee-net 30m trade version |
| 3 | Thin-zone pass-through: weekly profile (1m volume, 0.05% buckets); when price enters a node with volume under 25% of the POC bucket, trade in the entry direction at the next 5m open; target the next bucket above 75% of the POC; stop one bucket back; exit 24 5m bars | No. grep of `research` finds low-volume-node text only in design maps (no trial) |
