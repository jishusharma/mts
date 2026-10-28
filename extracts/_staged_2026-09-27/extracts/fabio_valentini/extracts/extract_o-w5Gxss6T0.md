# EXTRACT: Fabio Valentini (Fabervaale ENG) — o-w5Gxss6T0
# Title: "3 Order-flow Trading Tricks Exposed!"
# Published: 2025-09-24 | Duration: 8:34 | Instrument shown: NASDAQ futures (NQ)
# Source text: operator's manual copy (timestamped) cross-checked against auto-transcript
#              extracts/fabio_valentini/raw/o-w5Gxss6T0_raw.txt
# Extractor: Opus 5.5 (REFERENCE EXTRACTION — template for Sonnet workers)
# Date extracted: 2026-09-27 | Status: EXTRACTED | Phase: 1 (clean slate)
# Tier: T3 (individual practitioner). Competition-ranking claims [0:00] = UNVERIFIED.
# ---

## ASSESSMENT
Short, dense video. Three techniques, each tied to a chart example: (A) aggression
absorbed at a level, then breakout; (B) "real" fair value gap = lowest-volume price
inside the value area of a fixed-range profile over one swing; (C) absorption read
from CVD vs price mismatch (called "volume spread analysis"). Definitions are
given in words; NO numeric thresholds are given for any of them. Numbers on screen
(delta 599 / volume 2,832 etc.) are EXAMPLE VALUES, not thresholds.

Clean-slate rule honoured: no Tom material loaded while extracting. Cross-analyst
observations are deferred to Phase 2 (see bottom, marked PHASE-2 NOTE, not rules).

---

## RULES EXTRACTED

### FAB-001 — Orderflow shows the aggressor, candles do not
**Source:** o-w5Gxss6T0 @0:14-0:38 | Tier T3 | Tag: PRINCIPLE
> "These are called deep charts, orderflow charts. They don't simply show you price
> candlesticks. They actually shows you the interaction between buyers and sellers.
> And you can filter the small traders that doesn't mean much with the big traders"

Operational content: a size filter separates large participants from small ones.
**UNDEFINED in this video:** the size threshold for "big traders".
Data implication (not a rule): needs trade-level data (Binance aggTrades), not klines.

### FAB-002 — Aggression that fails to break a protected level = absorption
**Source:** o-w5Gxss6T0 @2:09-2:24 | Tier T3 | Tag: DEFINITION
> "buyers got really aggressive on the top, but they didn't manage to break through.
> So you can see that here they are being absorbed really heavy by the sellers."

Definition as stated: high positive delta at a level + price does not break the level
= sellers absorbing (passive sellers vs aggressive buyers). Mirror case stated @2:24-2:34
(aggressive sellers absorbed from the low part).
**UNDEFINED:** what delta size counts as "really aggressive"; how many attempts.

### FAB-003 — Escalating aggression into an absorbed level → expect BREAKOUT (not reversal)
**Source:** o-w5Gxss6T0 @2:34-3:13 | Tier T3 | Tag: SETUP-CONDITION
> "So when you have this case uh punched to the wall by the sellers with absorption and
> a huge aggression of the buyers because you can see a all-time high on volume 4,600
> with 812 of delta. What you can expect is that the next move will give you a breakout"

> "What the market does is that it don't come to visit again this area that got already
> protected. But you see sellers try to protect the level but then the price skyrocket."

Conditions in his words: (1) level protected by sellers (absorption, FAB-002),
(2) buyers keep attacking, (3) a record-volume bar with large positive delta
("all-time high on volume" — session/chart record, reference window NOT stated)
→ next move = breakout in the aggressor's direction. Also: the area buyers protected
below is not revisited.
**CAUTION — the "fine line":** this is the OPPOSITE of the naive "absorption = reversal"
reading. The discriminator he shows is escalation (record volume + delta) by the side
being absorbed. He does not state the rule for when absorption instead produces a
reversal in this example. See FAB-007 and UNCLEAR U2.

### FAB-004 — Candle-gap "fair value gap" is the wrong definition
**Source:** o-w5Gxss6T0 @3:26-3:47 | Tier T3 | Tag: DEFINITION (NEGATIVE)
> "When when there is an imbalance in price action, this is typically wrong because to
> identify a real fair value gap, you need to get inside the candle and you need to see
> how the volume transacted. This is what it's actually fair value gap or void."

Rule: a price-only gap (candle imbalance) is NOT a valid FVG by his definition.
FVG = a place where volume did not transact ("void"), identified from volume-at-price.

### FAB-005 — Real FVG = lowest-volume price inside the value area of a fixed-range profile over one swing
**Source:** o-w5Gxss6T0 @3:47-5:03 | Tier T3 | Tag: DEFINITION + PROCEDURE
> "What we use in this case to get more precise is the fixed profile."

> "getting the fixed profile I will show you on this wing from the point A to point B
> and removing the price action."   [caption "wing" = "swing"]

> "the lowest volume of interaction in all the area of value area. So where 70% of the
> volume got transacted is exactly this one is the level that goes from 24,318 to 24,317.
> Is it's a small level. It's not even an area."

> "This is what actually in all this range and in this value area it's the fair value
> gap. It's where the volume didn't transacted in a balanced way."

Procedure exactly as stated:
  1. Anchor a fixed-range volume profile from swing point A to swing point B.
  2. Compute its value area (70% of volume).
  3. Inside the value area, find the single lowest-volume price level.
  4. That level (a LEVEL, "not even an area") is the fair value gap.
**UNDEFINED:** how A and B are chosen (swing on which timeframe; impulse leg only?),
profile bin/tick size, what to do if several near-equal minima exist, timeframe.
Note: in the example the price-action FVG a PA trader would use and the volume FVG
are at DIFFERENT prices (@3:54-4:18) — that difference is the point of the lesson.

### FAB-006 — Price rejects at the volume-defined FVG
**Source:** o-w5Gxss6T0 @5:03-5:16 | Tier T3 | Tag: EXPECTATION (UNQUANTIFIED)
> "And what you will see thousand of times is that this is exactly where the price will
> reject."

Expectation: price reacts/rejects at the FAB-005 level. "Thousand of times" is a
frequency claim with NO statistics → do not use as a probability. Testable claim.
Also stated as usable by price-action traders for precision (@5:10-5:16).

### FAB-007 — Absorption via CVD: CVD makes a new extreme while price does not
**Source:** o-w5Gxss6T0 @6:32-7:06 | Tier T3 | Tag: DEFINITION
> "in this case you can see that we have a lower low on the cumulative volume delta here
> while the market is still on the same level as before. This is what it's called it's
> called absorption."

> "So there are passive buyers here that are absorbing all the aggressive sellers and
> the market is not willing to go down."

Definition: CVD lower low + price holds the prior low (equal level, not a lower low)
= passive buyers absorbing aggressive sellers → bullish. Mirror (CVD higher high,
price holds) implied by symmetry but NOT stated.
He names the method: "volume spread analysis ... understanding the result on the price
for the proxy of the volume" (@6:05-6:11).
**UNDEFINED:** CVD anchor/reset point, swing lookback, tolerance for "same level".

### FAB-008 — Use CVD absorption to confirm a failed auction and the day's direction
**Source:** o-w5Gxss6T0 @5:37-6:32, @7:06-7:22 | Tier T3 | Tag: SETUP-CONDITION
> "we are in a compressed area where buyers are pushing really hard to break the level
> and the market is compressing. But the first question that a trader can ask is we will
> be in accumulation or we will be in distribution."

> "Then it tends to be a failed auction. But a lot of traders maybe can see open candle
> and try the breakout"

> "In this case you can confirm objectively with the absorption pattern the failuction.
> You can get a clear direction for the day."   [caption "failuction" = "failed auction"]

Context: compression near a level; ambiguous accumulation vs distribution; an apparent
downside breakout attempt. FAB-007 absorption confirms the breakdown is a failed
auction → trade against the breakout (long in the example) and take it as the day's
direction.

### FAB-009 — Trend-following entry: absorption of counter-trend aggression inside momentum
**Source:** o-w5Gxss6T0 @7:22-8:14 | Tier T3 | Tag: SETUP-CONDITION
> "when you are in a momentum phase like this one and you can see a huge amount of
> aggression following an absorption, you can understand that the buyers are in control."

> "we have a sell candle that tried to create a lower low, but on the correspondent part,
> we have a huge absorption. All this pressure got zero results, but you continue to see
> sellers trying to go down here. This is again an absorption of sellers. So, it's a
> mismatch in price and volume."

Conditions: (1) momentum phase, (2) aggression following an absorption identifies the
side in control, (3) counter-side aggression (sell pressure) produces zero price result
= absorption again → join the trend. "confirm your trade with a high probability of
being right" (@8:14) — unquantified.

---

## UNCLEAR
- U1 @2:24-2:34: "599 of delta in a total volume of 2,800 and 332" — likely 2,832 total
  volume. Example value only.
- U2 FAB-003 vs FAB-007/008: both involve absorption, opposite outcomes (breakout in the
  absorbed side's direction vs reversal against the aggressor). The video shows the
  discriminator only implicitly (escalating record volume+delta in FAB-003; price holding
  while CVD extends in FAB-007). NOT resolved here — needs his other videos
  (priority: Khgj5q1-ln8 "Signature Orderflow Model", cUTsoU-15Tc, Pz8f0wWW12M).
- U3 "all-time high on volume": reference window unknown (session? visible chart?).
- U4 FAB-005 anchors A/B: chosen visually on the example; no selection rule stated.

## EXCLUDED
- @0:00-0:14 competition ranking / 500% return claim — biographical, unverified, no rule.
- @3:13-3:19 platform launch promo ("deep charts ... save your spot") — marketing, REJECT tier.
- @8:21-end outro.

## SUMMARY
| Category | Count |
|---|---|
| PRINCIPLE | 1 (FAB-001) |
| DEFINITION | 4 (FAB-002, 004, 005, 007) |
| SETUP-CONDITION | 3 (FAB-003, 008, 009) |
| EXPECTATION (unquantified) | 1 (FAB-006) |
| Numeric thresholds given | 0 |
| UNCLEAR | 4 |

---

## PHASE-2 NOTES (for consolidation — NOT rules, written after extraction closed)
- P2-a FVG: Tom Fj4FDZQxw0I defines FVGs via single prints (volume/TPO based) and says
  they act as S/R "only if the market has trend stability". Fabio FAB-004/005 also
  rejects the candle-gap definition. Two independent T3 sources reject exactly what
  src/main/java/datafeed/FvgCalculator.java implements (3-candle gap). Candidate CORE change.
- P2-b Absorption: current Java detector (SetupCandidatesBuilder 9.2) is a single-candle
  proxy (vol>2x avg20, range<0.3 ATR, delta sign vs candle colour, within 0.1% of zone).
  FAB-007 is a swing-level CVD-vs-price divergence. Different constructs; both named
  "absorption". Must be split into two named signals before any rule uses them.
- P2-c FAB-007/008 are a candidate operational definition for the open item
  D5/B063 (divergence / trend_unhealthy) and for D6b (Tom-cited SETUP_CONFIRMED trigger).
# END
