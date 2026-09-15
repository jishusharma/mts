# CROSS-TRADER CONSOLIDATED RULES
# Phase 2 Output — Consolidation Complete
# Date: 2026-08-30
# Status: READY FOR PHASE 3 (Integration Planning)
# Purpose: Deduplicated, clustered, cataloged master list of all 85 extracted rules
# Method: Group by concept, deduplicate near-duplicates, flag conflicts, cross-reference all CT IDs
# ---

## CONSOLIDATION SUMMARY

| Metric | Value |
|--------|-------|
| Original rules extracted | 85 (CT-001 to CT-085) |
| Source transcripts | 7 (2 analysts: The Flow Horse, CryptoCred) |
| Concept clusters | 20 |
| Consolidated entries | 73 |
| Rules merged (deduplicated) | 11 pairs/groups |
| Conflicts flagged | 5 |
| Standalone rules (no merge) | 50 |

## DEDUPLICATION REGISTRY

The following original CT rules were merged into single consolidated entries because they describe the same underlying principle:

| Consolidated Entry | Merged CT IDs | Rationale |
|--------------------|---------------|-----------|
| C01-E03: Old Profiles = Context Only | CT-009, CT-002, CT-007 | All three describe time-decay of profile relevance — recency/proximity principle |
| C02-E01: Extended Sideways Compression | CT-004, CT-013 | Both describe compression -> expansion dynamics; CT-013 adds observable signatures (DVOL, barcoding) |
| C03-E01: Heavy Selling + No Breakdown = Absorption | CT-012, CT-019 | CT-019 is a specific instance of CT-012's general absorption principle |
| C06-E02: First Test Best Test | CT-082 | Both describe the danger of moving to BE on first reaction; CT-083 adds the "graveyard" framing |
| C08-E03: Do Not Chase Every MSB | CT-023, CT-026 | Both describe selective MSB significance; CT-026 specifies range-bound noise |
| C09-E02: Confluence / Probability Enhancers | CT-024, CT-030 | Both describe stacking confluence factors; CT-030 adds funding/OI |
| C11-E01: Precision Inversely Correlated with Move Size | CT-042, CT-062 | Same principle from two videos — CT-042 (entry precision) and CT-062 (stop strictness) are two sides of one coin |
| C12-E02: Management Timeframe | CT-048, CT-075 | CT-075 is the FTA-specific application of CT-048's general principle |
| C12-E04: Level Performance as Evidence | CT-050, CT-052 | CT-052 is a specific instance of CT-050's general principle (acceptance = opposite performance) |
| C14-E01: Dynamic Risk/Reward | CT-054, CT-066 | Same concept — CT-066 adds Tom Dante's "evolving R" framing and specific 2R->0.25R example |
| C15-E01: Break-Even Stops Are Psychological Cope | CT-055, CT-069, CT-083 | All three strongly caution against automatic BE; CT-055 (Trade Mgmt), CT-069 (Risk Mgmt), CT-083 (FTA) reinforce from different angles |
| C18-E01: Trade the Chart, Not P&L | CT-056, CT-070 | Same principle — CT-070 adds management-specific process orientation |

## CONFLICT REGISTRY

The following conflicts were identified during consolidation. **NOT RESOLVED** — flagged for Phase 3 (Integration Planning) assessment.

### CONFLICT 1: Retest as Confirmation vs. Retest as Best Entry

**Tension:**
- **CT-035** ("Retest is not required to confirm a level") explicitly debunks the retest confirmation myth, calling it "complete fiction." The break itself is the significant event.
- **CT-006** ("Retest after real break — throwback to reaccept") calls the retest "the easiest trade to get behind."
- **CT-082** ("First test best test") states the first test is often the best entry and traders should "stomach the retest."
- **CT-083** ("Swing trade graveyard") implies the first reaction/retest is critical to the trade's survival.

**Nature of conflict:** Conceptual tension, not hard contradiction. CT-035 addresses structural *validity* (retest not required for a level to be valid). CT-006/082/083 address entry *preference* (retest offers superior R:R and is the preferred entry). However, the strong language ("complete fiction" vs. "easiest trade") creates ambiguity about whether retests are optional nice-to-haves or structurally significant components of the trading framework.

**Source GPS:**
- CT-035: CryptoCred, inqHN8q57X4, ~06:15; ~06:45
- CT-006: The Flow Horse, Oy2Z-FQ77NM, ~09:00; ~09:15
- CT-082: CryptoCred, Yp0k8HD5xro, ~39:00; ~39:15; ~40:00
- CT-083: CryptoCred, Yp0k8HD5xro, ~40:15; ~41:00

### CONFLICT 2: Active Evidence-Based Management vs. Passive Set-and-Forget

**Tension:**
- **CT-047** ("Evidence-based trade management") advocates continuous, active reassessment of whether price action supports the thesis. If evidence conflicts, exit before full stop loss.
- **CT-067** ("Beginners — conservative targets + set and forget") recommends beginners use a passive set-and-forget approach because they are "far more likely to over-manage than under-manage."
- **CT-057** ("The dead zone") says there is a zone between stop and target where "your job is kind of to do nothing" and "let your idea play out."

**Nature of conflict:** Spectrum tension, not hard contradiction. The rules are context-dependent (beginner vs. experienced, early trade vs. late trade). However, there is no clear boundary defining WHEN active management applies vs. WHEN passive management applies. The "dead zone" concept partially addresses this but does not resolve the beginner/experienced divide.

**Source GPS:**
- CT-047: CryptoCred, _ndAoizXy64, ~01:45; ~04:15; ~04:30; ~04:45; ~05:00; ~05:15
- CT-067: CryptoCred, XeQV2ECtZVQ, ~30:00; ~30:30
- CT-057: CryptoCred, _ndAoizXy64, ~43:00; ~43:15; ~43:45

### CONFLICT 3: Cut-and-Reverse as Trap vs. Valid Reversal Setup

**Tension:**
- **CT-029** ("Cut and reverse trap") warns against automatic cut-and-reverse on invalidation: "Don't assume you've always identified absolute turning points and that the market's going to be kind enough to let you get in on the other side."
- **CT-033** ("Reversal on failed MSB") describes a specific, valid reversal setup: "Failed continuation is suggestive of reversal... if we get a higher high bullish into a lower low invalidated then you have bulls offside... bulls offside makes for a good sell setup."

**Nature of conflict:** Boundary ambiguity. Both rules are valid in different contexts, but the boundary between "trap" and "valid reversal" is not clearly defined. CT-029 warns against ASSUMING reversal; CT-033 describes CONDITIONS for reversal. The unresolved question: what specific conditions distinguish a valid reversal setup (CT-033) from a cut-and-reverse trap (CT-029)?

**Source GPS:**
- CT-029: CryptoCred, BHwoN7VPrBE, ~42:00
- CT-033: CryptoCred, BHwoN7VPrBE, ~65:00; ~66:00

### CONFLICT 4: Split Position vs. Conviction-Based Full Position

**Tension:**
- **CT-039** ("Split position = sub-optimal") strongly rejects splitting between breakout and retest: "The trade is guaranteed to be sub-optimal one way or another." Advocates conviction-based full positions: "I like to establish positions when I say with conviction."
- **CT-036** ("Breakout vs retest = R:R trade-off") neutrally presents both breakout and retest as valid approaches with different trade-offs: "Less certainty often offers superior risk reward... more certainty often offers inferior risk reward."

**Nature of conflict:** Philosophical tension. CT-039 takes a strong stance that there is a "correct" approach (conviction-based full position) and that any middle ground is bad. CT-036 presents a balanced, non-judgmental trade-off framework. A trader following CT-036 might reasonably split positions or alternate strategies; a trader following CT-039 would reject this. The two frameworks are not mutually exclusive but represent different trading philosophies.

**Source GPS:**
- CT-039: CryptoCred, inqHN8q57X4, ~21:00; ~22:00
- CT-036: CryptoCred, inqHN8q57X4, ~09:30; ~10:30

### CONFLICT 5: Breakout Chasing in Ranges vs. SR Flip Continuation

**Tension:**
- **CT-044** ("Don't chase breakouts in ranges") states: "In a range-bound environment chasing the breakdown or chasing the breakout could be quite ugly or end unfavorably... resistance is for selling and support is for buying."
- **CT-025** ("Setup 1 — continuation at break level / SR flip") describes entering on pullback to broken level after MSB: "The long trade is taken on a pullback to the broken high... broken resistance turning to support on a re-test."
- **CT-026** ("MSB in range = noise") adds: MSBs within a range (not at extremes) are noise.

**Nature of conflict:** Contextual ambiguity. CT-025 is a general setup rule that could apply in any market condition. CT-044 and CT-026 specifically restrict its application in ranges. The unresolved question: at what point does a range-bound market transition to a state where SR flip setups become valid? Is an MSB at a range extreme (per CT-026) ever valid for an SR flip entry, or is it always noise in a range? The three rules together create a gray zone.

**Source GPS:**
- CT-044: CryptoCred, inqHN8q57X4, ~36:00; ~37:00
- CT-025: CryptoCred, BHwoN7VPrBE, ~45:00
- CT-026: CryptoCred, BHwoN7VPrBE, ~85:00

---

## CONCEPT CLUSTERS

---

### C01 — Volume Profile Philosophy: Context vs. Execution
*Rules about what volume profile can and cannot do, and the distinction between structural context and executable signals.*

#### C01-E01: Volume Profile is Descriptive, Not Predictive
**Merged CTs:** CT-001
**Description:** Volume profile only shows where business was done (turnover). It does not reveal who bought/sold, position intent, or directional bias. Everything beyond raw turnover data is assumption.
**Source GPS:**
- CT-001: The Flow Horse, Oy2Z-FQ77NM, ~01:30; ~01:45 — "Volume profile just tells us where business was done. That's it... It doesn't tell us anything else. Everything else is really an assumption."

#### C01-E02: Structure vs. Flow — Profile Gives Areas, Order Flow Gives Execution
**Merged CTs:** CT-008
**Description:** Profile identifies zones of interest, but order flow (delta, absorption, CVD) determines whether to act at those zones. Always structure versus flow.
**Source GPS:**
- CT-008: The Flow Horse, Oy2Z-FQ77NM, ~17:15 — "Profile gives you the areas of interest... But it's the actual order flow that tells you whether or not you should care. It's structure versus flow, always."

#### C01-E03: Old Profiles = Context Only, Not Execution
**Merged CTs:** CT-009, CT-002, CT-007
**Description:** The relevance of profile data decays with time. Recent profiles (daily, weekly) are actionable; old profiles (monthly, quarterly) provide context only. Confusing context for execution is a common trader error. LVNs from prior session matter far more than LVNs from months ago. The closer in proximity to turnover, the more relevant the positioning.
**Source GPS:**
- CT-009: The Flow Horse, Oy2Z-FQ77NM, ~19:30; ~19:15 — "Confusing context for execution is why most traders get themselves in trouble."
- CT-002: The Flow Horse, Oy2Z-FQ77NM, ~06:00; ~16:45 — "The closer we are in proximity to where that turnover took place, the more likely that positioning is still relevant."
- CT-007: The Flow Horse, Oy2Z-FQ77NM, ~10:30; ~10:45 — "LVN from the prior session matters a lot more than an LVN from 6 months ago."

#### C01-E04: Composite Profiles — Only Useful in Tight, Well-Defined Ranges
**Merged CTs:** CT-010
**Description:** Composite profiles are useful only when the market trades tightly within a well-defined range with significant overlap. In loose/dislocated markets, extremes become more actionable than the value area.
**Source GPS:**
- CT-010: The Flow Horse, Oy2Z-FQ77NM, ~03:45 — "Composites can be really useful when the market is trading very tightly within a very well-defined range... Not where there's a lot of dislocation and loose trading."

#### C01-E05: POC Location Varies by Platform — Marginal Differences May Not Be Significant
**Merged CTs:** CT-011
**Description:** POC (Point of Control) can switch depending on platform or tick setting. Marginal differences between adjacent HVNs may not be structurally significant.
**Source GPS:**
- CT-011: The Flow Horse, Oy2Z-FQ77NM, ~02:45 — "POC will switch depending on what platform or tick setting you're using... is it that much more significant at this level than that HVN that was just barely smaller."

---

### C02 — Compression / Balance -> Expansion / Resolution
*Rules about how extended periods of balance or compression resolve into directional moves, and how to measure expected follow-through.*

#### C02-E01: Extended Sideways Compression Increases Probability of Violent Resolution
**Merged CTs:** CT-004, CT-013
**Description:** The longer price spends sideways within a structure, the more likely a violent resolution when the break occurs. Observable signatures include DVOL compression, barcoding, and limp activity. Volatility compression precedes range resolution.
**Source GPS:**
- CT-004: The Flow Horse, Oy2Z-FQ77NM, ~07:45 — "And the longer that we spend sideways within a structure, the more likely that when it resolves outside of that structure, especially if violently, the more likely that that will lead to a more significant response."
- CT-013: The Flow Horse, zMM9QgxfEFI, ~04:30 — "if you looked at the Bitcoin implied volatility index or DVOL or any measure of volatility, you would see that things were really compressing... there were periods where it was just barcoding and trading for minutes on end in a, you know, a few basis points range. So, very limp activity"

#### C02-E02: Extended Balance + High-Volume Break = Measured Move Target
**Merged CTs:** CT-014
**Description:** Multi-month balance with multi-month value established, when broken with high volume, produces follow-through approximately equal to the range size (minimum target projection). Balance duration correlates with follow-through magnitude.
**Source GPS:**
- CT-014: The Flow Horse, zMM9QgxfEFI, ~09:30; ~13:15 — "the longer you build a structure like this, where you have this kind of overlap, multi-month overlap and multi-month value established, the more likely that there is significant follow-through in the event of actually cleaning through or clearing through one side of the structure... we built this size base, we should get a move that is somewhere around that region."

#### C02-E03: Real Change Happens at Range Extremes, Not Within Structure
**Merged CTs:** CT-015
**Description:** Within-range trading produces rotations with no directional edge. Real directional change occurs at range extremes where one side is forced offside and must chase or reevaluate their thesis.
**Source GPS:**
- CT-015: The Flow Horse, zMM9QgxfEFI, ~09:00 — "while you're trading within a range, nothing really changes... You're going to be trading rotations within the structure, but real change is on the outside of the extremes, where you're forcing one side that's been committing throughout the duration of the structure very clearly offside or very much in a position where they have to chase or reevaluate their thesis."

---

### C03 — Absorption / Seller Exhaustion
*Rules about identifying when selling pressure is being absorbed rather than producing breakdowns, indicating potential accumulation.*

#### C03-E01: Heavy Selling Pressure + Price Holding Sideways = Absorption / Seller Exhaustion
**Merged CTs:** CT-012, CT-019
**Description:** When heavy selling pressure (narrative-driven or large seller activity) fails to produce a price breakdown and price holds sideways or bids higher, this indicates seller exhaustion and absorption. Running out of sellers does not automatically mean buyers arrive — it means equilibrium has been found. Large seller active + price holding/bidding higher = structural bullish signal.
**Source GPS:**
- CT-012: The Flow Horse, zMM9QgxfEFI, ~02:15; ~02:45 — "numerous cases of bad news, good price. So, where there's some kind of negative press or literally outright selling... all of this still resulted in Bitcoin just trading sideways, which was really good feedback from the tape... This is one of the purest examples of just running out of sellers and the market not being able to be spooked anymore and finding an equilibrium... just because you run out of sellers doesn't mean you bring new buyers into the market."
- CT-019: The Flow Horse, zMM9QgxfEFI, ~06:15; ~06:45 — "Sailor was a massive seller... and yet Bitcoin able to hold within the structure. So, really good signs in the tape... price ended up trading higher. And then as we traded towards the right side of the structure, again, him selling and price bid higher at that point than previous."


---

### C04 — False Break / Head Fake Signatures
*Rules for identifying when a break of structure is likely a head fake rather than a genuine continuation.*

#### C04-E01: Head Fake Signature — Low Volume + Absorption + Immediate Rejection Back Into Value
**Merged CTs:** CT-005
**Description:** False break identification: lack of volume, lack of participation, lack of momentum, obvious absorption (buying immediately stuffed), and price trading back below the level into previous value. Drifting after break = weakness, not conviction. First or second attempts outside of value are more actionable than repeated tests.
**Source GPS:**
- CT-005: The Flow Horse, Oy2Z-FQ77NM, ~08:00; ~08:15 — "This is a head fake... You look for a lack of volume, a lack of participation, a lack of momentum. You might even look for very obvious levels of absorption. So, what buying comes in is immediately stuffed... If there's any sign of weakness, it's when price is just drifting lower. You want punchy, minimal selling, punchy again."

#### C04-E02: Don't Chase Breakouts in Range-Bound Markets
**Merged CTs:** CT-044
**Description:** In range-bound environments, chasing breakdowns or breakouts is unfavorable. Resistance is for selling, support is for buying. Price often pokes at or through extremes before reverting to the mean.
**Source GPS:**
- CT-044: CryptoCred, inqHN8q57X4, ~36:00; ~37:00 — "in a range-bound environment chasing the breakdown or chasing the breakout could be quite ugly or end unfavorably... in a range resistance is for selling and support is for buying... price will often poke at or through the extremes before reverting to the mean"

#### C04-E03: Strong Trend = Failed Breakdowns at Support / Failed Breakouts at Resistance
**Merged CTs:** CT-045
**Description:** In strong trends, counter-trend traders are more likely to get trapped. Bull trend: failed breakdowns at support are likely. Bear trend: failed breakouts at resistance are likely. Sellers put their foot wrong at support; buyers put their foot wrong at resistance.
**Source GPS:**
- CT-045: CryptoCred, inqHN8q57X4, ~37:30; ~40:00 — "in a bull trend or at support failed breakdown setups are likely... in a strong trend bears are more likely to get trapped than bulls right or sellers are more likely to put their foot wrong at support than buyers... if high time frame context bull no rush or need to execute bear trades can wait for bull trades higher or lower"

---

### C05 — Break Validity & Continuation Signals
*Rules for confirming genuine breaks, identifying continuation signals post-break, and defining invalidation levels.*

#### C05-E01: Break Candle Low = Hard Invalidation After High-Volume Break
**Merged CTs:** CT-016
**Description:** After a high-volume break (catalyst-driven or otherwise), the low of the break candle = hard invalidation level. Trading back below it = strong signal of failure. The catalyst-driven move low is very significant.
**Source GPS:**
- CT-016: The Flow Horse, zMM9QgxfEFI, ~10:45; ~11:15; ~11:30 — "exploring the breakaway gap that we have. We have a news-driven move. It really shouldn't trade much further below that... the low of that move is very significant. That would send, I think, a strong signal of failure... breaking back below the event, right? So, the catalyst-driven move, the low of that move is very significant."

#### C05-E02: Shallow Pullback After High-Volume Break = Legitimate Continuation
**Merged CTs:** CT-017
**Description:** Post-breakout pullback depth as continuation signal. Shallow pullback = strong demand, everyone lining up to buy the dip, continuation likely. Deep pullback = weakness, potential failure. If legitimate, it will correct more vertically than with any deeper pullback.
**Source GPS:**
- CT-017: The Flow Horse, zMM9QgxfEFI, ~12:00 — "Shallow pullback is indication that everyone is lining up to buy this dip. And because of that, it'll correct more vertically than with any kind of deeper pullback. So if this is legitimate, it's not going to correct much."

#### C05-E03: Day of Balance After Breakout = Continuation Building, Not Reversal
**Merged CTs:** CT-018
**Description:** One day of tight balance (consolidation) after a breakout = accumulation/distribution building for the next leg, not reversal. If price establishes tight value after the break, expect drift then another punch higher in the near term.
**Source GPS:**
- CT-018: The Flow Horse, zMM9QgxfEFI, ~12:45 — "It might establish another day of balance up here. It might establish one more day of tight value, but if it starts to paint something like that over the next session, I would lean towards the idea that this is probably going to lead to drift and then another punch higher in the very near term."

---

### C06 — Zone Reliability & Test Degradation
*Rules about how zone reliability changes with repeated tests, and the significance of first vs. subsequent tests.*

#### C06-E01: Test Count Degradation — Repeated Tests Weaken Zone Reliability
**Merged CTs:** CT-003
**Description:** The more times a level is tested, the less trustworthy it becomes. First or second attempts outside of value or fading extremes are more actionable than third, fourth, or fifth. Early tests are information; repeated tests along the same level are a build-up of pressure.
**Source GPS:**
- CT-003: The Flow Horse, Oy2Z-FQ77NM, ~07:15 — "The nuance is that the more times that some level is tested, the less I'm going to trust it. So, it's often the case that the first attempt or the second attempt outside of value or fading those extremes is probably going to be more actionable than the third, the fourth, and the fifth. Early tests are information. Early and rapid responses. Repeated tests, repeated tests along the same level, that's just a build-up of pressure."

#### C06-E02: First Test Best Test — Be Prepared to Stomach the Retest
**Merged CTs:** CT-082
**Description:** The first test of a high timeframe level is often the best. Before the management FTA has been broken, be prepared to stomach a retest of your entry. The first reaction at a high TF level is not conclusive — numerous intraday retests can occur within a single weekly candle. Moving to break-even on the first reaction is the "swing trade graveyard" — price often retests the high TF level on lower timeframes before the real move, and moving to BE means getting stopped out at your entry (buying resistance you sold, or selling support you bought) and missing the high timeframe move. Exception: if revisiting entry actually invalidates the idea.
**Source GPS:**
- CT-082: CryptoCred, Yp0k8HD5xro, ~39:00; ~39:15; ~40:00 — "if you're trading first test best test and a reasonable FTA has not yet been broken you should almost always be able to stomach a retest of your entry... don't put too much weight on the first reaction you get at a high timeframe level it is by no definition or by no sense conclusive... if you're for example selling a weekly level of resistance which let's say reverses relatively quickly right like one weekly candle a minute reverses it could still be retesting that level on intraday basis and there's you know seven days in a week there could be numerous or seemingly endless three tests on lower timeframe of that same level"

---

### C07 — Retest Mechanics
*Rules about the nature of retests, when they occur, how to classify them, and how to use them for entry and validation.*

#### C07-E01: Retest Is Not Required to Confirm a Level
**Merged CTs:** CT-035
**Description:** The common myth that markets must retest a broken level to confirm it as support/resistance is fiction. The significant event is the break of structure itself — it does not suddenly become magically valid only if price returns. The break itself is the significant event.
**Source GPS:**
- CT-035: CryptoCred, inqHN8q57X4, ~06:15; ~06:45 — "what you'll often see is this blanket statement that the market needs to retest x to confirm it as support resistance just forget it right i don't know i can't call this anything other than the notion because it's complete fiction... the significant event tends to be the break of structure itself it doesn't suddenly become magically valid if price decides to come back to it"

#### C07-E02: Retest After Real Break — Throwback to Reaccept Is the Easiest Trade
**Merged CTs:** CT-006
**Description:** After a convincing high-volume break outside of profiles (RTH, ETH), the throwback and attempt to reaccept back within value — the first retest — is the easiest trade to get behind. All recent relevant positioning was balanced at the broken level; trading below it means sellers are in a much better position than buyers.
**Source GPS:**
- CT-006: The Flow Horse, Oy2Z-FQ77NM, ~09:00; ~09:15 — "The last and most exciting trade using profile is actually a retest after a real break... We have a convincing break outside of these two profiles, RTH, ETH, a convincing high-volume break. See a ton of volume through the level. The easiest trade to get behind is the throwback and attempt to reaccept back within value. So, the first retest really... It's because all of this recent relevant positioning was balanced up here. If we're trading below it, we could say with much more certainty that any seller up here... is in a much better position than any buyer had been."

#### C07-E03: Breakout vs. Retest = Risk/Reward Trade-Off
**Merged CTs:** CT-036
**Description:** Breakout entry = guaranteed fill but worse R:R. Retest entry = better R:R but no guarantee price returns. Less certainty often offers superior risk/reward; more certainty often offers inferior risk/reward. This is a fundamental trade-off, not a right/wrong choice.
**Source GPS:**
- CT-036: CryptoCred, inqHN8q57X4, ~09:30; ~10:30 — "less certainty often offers superior risk reward... more certainty often offers inferior risk reward... if you're buying the retest of the level it's not clear whether the breakout's going to hold... but you get the premium if you will or the benefit of superior risk reward whereas if you're waiting for all the bullishness to kick in... the market will necessarily be further away from the breakout level... if you wait for a re-test you get superior risk reward but no trade guarantee... if you trade the breakout you get a guaranteed trade in most cases but at the cost of an inferior risk to reward"

#### C07-E04: Timeframe Alignment for Break Validation
**Merged CTs:** CT-037
**Description:** Break validity requires a close on the SAME timeframe as the structure anchor. A daily structure is only broken with a daily candle close; a 4H structure with a 4H close. Wick-only penetration without close = retest, not valid break. Low timeframe breakouts at high timeframe resistance can just be wicks.
**Source GPS:**
- CT-037: CryptoCred, inqHN8q57X4, ~13:00; ~13:30 — "if you've got a daily structure it's only broken if you get a daily candle close through it and if you've got a four hour structure it's only valid if you get a four hour close through it etc etc so basically scale or align the structure with the break time frames... a low time frame quote-unquote breakout at high time frame resistance can just be a wick... a low time frame breakdown at high time frame support can just be a wick"

#### C07-E05: Immediate vs. Rounded Retest — Rounded Is Clearer
**Merged CTs:** CT-038
**Description:** Immediate retest = trading at/near structure at the time of break (little time/space). Rounded retest = trading at/near structure after the breakout has played out (more time/space). Rounded retests tend to be clearer setups because the time/space validates that a meaningful break took place, eradicating the risk of falling for a failed breakout.
**Source GPS:**
- CT-038: CryptoCred, inqHN8q57X4, ~16:00; ~17:30; ~18:30 — "the immediate retest is when you trade at or near structure when it breaks right so at the time of the breakout or the breakdown... whereas on the rounded retest you're trading at or near structure after the breakout has played out... the main distinguishing factor is time and space... rounded re-tests tend to be clearer setups so the fact that the re-test is rounded implies that a meaningful break took place so you essentially eradicate the risk of falling for a failed breakout"

#### C07-E06: Split Position Between Break and Retest = Sub-Optimal Either Way
**Merged CTs:** CT-039
**Description:** Splitting a position equally between the breakout entry and the retest entry guarantees sub-optimal execution one way or another. Personal preference: establish full positions with conviction rather than hedging between two entry styles.
**Source GPS:**
- CT-039: CryptoCred, inqHN8q57X4, ~21:00; ~22:00 — "the basic premise of the false dilemma is you would split your position equally between the break and the re-test... the trade is guaranteed to be sub-optimal one way or another like something is always going to suck about it... for me personally i don't trade like this i just don't i i like to establish positions when i say with conviction"

#### C07-E07: Precedent — Instrument's Historical Retest Behavior Matters
**Merged CTs:** CT-040
**Description:** Historical retest behavior per instrument matters. If an instrument regularly offers retests, wait for one. If it doesn't, expecting a retest is unreasonable. Fast-trending instruments (especially post-consolidation impulses) are the least forgiving for easy pullbacks.
**Source GPS:**
- CT-040: CryptoCred, inqHN8q57X4, ~23:30; ~24:45 — "does the instrument that you're trading especially in its current trend or with recent price action offer regular retests and this is kind of as simple as it sounds right if it does offer regular retests well then great wait for one and if it doesn't offer a regular retest then it would be unreasonable for you to expect it... when you have a long period of sideways and then you get the trend forming bullish leg this kind of impulse that follows tends to be the least forgiving in terms of allowing you to get on board on easy pullbacks"

#### C07-E08: Big Break Forces Retest Wait — R:R Decides
**Merged CTs:** CT-041
**Description:** If the break is so large that most of the target move has already played out, chasing without a retest = poor R:R. The size of the breakdown/breakout can make a follow-up entry nonsensical. What move are you trying to capture and how much space has already played out?
**Source GPS:**
- CT-041: CryptoCred, inqHN8q57X4, ~26:30; ~27:30 — "sometimes that risk that that negative risk to reward or the negative impact on the risk reward simply from the size of the breakdown or break out or the size of the break can be so big that a follow-up entry doesn't make sense... what move am i trying to capture and how much of that space has already played out as a result of that break if the break has already taken your idea mostly to target the risk reward to chase it without a re-test often isn't there"

#### C07-E09: Hidden Retests on Lower Timeframes
**Merged CTs:** CT-043
**Description:** High timeframe trends may show "no pullbacks" on the HTF but have brief retests on lower timeframes. These LTF retests are short-lived and happen very quickly — which is exactly what you want to see when there's real imbalance in the market. A daily or weekly chart that looks like it's gone up forever may have had brief 1H or 4H pullbacks.
**Source GPS:**
- CT-043: CryptoCred, inqHN8q57X4, ~32:00; ~32:15; ~34:30 — "in fast-moving markets the high time frame breaks that occur sometimes do offer re-tests but they occur on lower time frames as a result those lower time frame retests aren't always visible on higher time frames... you can have a market where the daily time frame or weekly time frame just looks like it's gone up forever and offered no pullbacks at all but if you look on a slightly lower time frame you do get a pullback it's just very short-lived... the nature of these retests is that they're often short-lived and happen very quickly now that may seem like a negative point... that's actually exactly what you want to see when there's real imbalance in the market"

#### C07-E10: Rounded Retest Context — What Happened Between Break and Retest Matters
**Merged CTs:** CT-046
**Description:** A lot can happen between a break and the subsequent retest. If price reached a strong HTF level between break and retest, the retest is lower probability. Example: hourly support break reaches daily support, then retests hourly support-turned-resistance — selling that retest means standing in front of a daily move with an hourly level.
**Source GPS:**
- CT-046: CryptoCred, inqHN8q57X4, ~41:00; ~43:30 — "a lot can happen between a break and the subsequent retest of the level... a classic example is a break of hourly support which reaches daily support and then comes back to the hourly support turn resistance like do you want to sell that and a lot of the time the answer is no... you're not just buying a retest of an hourly level you're standing in front of a daily move with an hourly level"

---

### C08 — Market Structure Break (MSB): Definition & Significance
*Rules defining what constitutes a market structure break, how to measure it, and how to assess its significance.*

#### C08-E01: MSB Definition — Higher High / Lower Low (Sequence Violation)
**Merged CTs:** CT-021
**Description:** Bullish MSB = sequence of lower highs violated by a higher high. Bearish MSB = sequence of higher lows violated by a lower low. This is the formal definition of market structure break.
**Source GPS:**
- CT-021: CryptoCred, BHwoN7VPrBE, ~22:00 — "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low"

#### C08-E02: MSB as Context Tool, Not Mechanical Trading System
**Merged CTs:** CT-022
**Description:** Market structure is a tool to provide context for trade decisions, not a standalone mechanical entry system. It informs positioning and bias, not automatic entries.
**Source GPS:**
- CT-022: CryptoCred, BHwoN7VPrBE, ~05:30 — "market structure generally i think is a tool to provide context more so than just a mechanical trading system"

#### C08-E03: Do Not Chase Every MSB — Selective Significance
**Merged CTs:** CT-023, CT-026
**Description:** Not every minor pivot break is actionable. Ascribing significance to every single shift in market structure turns you into a breakout/breakdown chaser. MSBs within a range (not at range extremes) are noise — only MSBs at actionable range boundaries matter.
**Source GPS:**
- CT-023: CryptoCred, BHwoN7VPrBE, ~19:30 — "if you end up ascribing significance to every single shift in market structure you are turning yourself into nothing more than a breakout and breakdown chaser... it's got very little to do with how we want to use market structure as a tool to provide context"
- CT-026: CryptoCred, BHwoN7VPrBE, ~85:00 — "market structure breaks which are just less obvious or shorter term... in the middle of nowhere... can just be pure noise... i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade"

#### C08-E04: Time Frame of MSB = Expected Move Size
**Merged CTs:** CT-027
**Description:** The timeframe of the market structure break has significant bearing on the size of the move that follows. Don't expect the world to end over an intraday MSB, but don't expect a weekly MSB to fizzle out after a couple days. Higher timeframe MSBs produce larger, more sustained moves.
**Source GPS:**
- CT-027: CryptoCred, BHwoN7VPrBE, ~82:00 — "the time frame of the market structure break to have a significant bearing on the size of the move that follows... don't expect the world to end over an intraday market structure break but at the same time don't expect a weekly market structure break to fizzle out after a couple days"

#### C08-E05: Candle Bodies for Structure, Closes for Breaks
**Merged CTs:** CT-031
**Description:** Use candle bodies (not wicks) for market structure definition. For a valid break, require a close above/below on the same timeframe as the structure anchor. Wick-through without close = retest, not break.
**Source GPS:**
- CT-031: CryptoCred, BHwoN7VPrBE, ~28:30 — "my preferred variant is using candle bodies for market structure and then closes so again bodies above or below for market structure break... i at least like to see a close above or below on the same time frame as the market structure anchor so if i'm looking at daily market structure... i want to see a daily close through that high or low to constitute a market structure break"

#### C08-E06: Early Warning — Failure to Continue Making Lower Lows / Higher Highs
**Merged CTs:** CT-034
**Description:** Gradual shift in swing behavior (lower lows -> equal/higher lows, or higher highs -> equal/lower highs) is an early warning of trend slowdown. Not a trade signal — context information only. The twisting of the dial more gradually is still useful.
**Source GPS:**
- CT-034: CryptoCred, BHwoN7VPrBE, ~88:00 — "failure to continue making lower lows... it's not bullish per se but it's less bearish... the twisting of the dial more gradually is still useful... a sign of bullishness slowly emerging is when you've got clear lower highs and lower lows except those lower lows then start to form equal or higher lows... it's not bullish per se but it's less bearish right and that information itself... the twisting of the dial more gradually is still useful"


### C09 — Swing Point Quality & Selection
*Rules about how to select meaningful swing highs and lows, and how to classify levels across timeframes.*

#### C09-E01: SWING HIGH/LOW QUALITY FILTERS
**Merged CTs:** CT-020
**Description:** Swing point selection criteria: recency, significance, size of subsequent move. "Smell test" = most obvious/obvious highs and lows.
**Source GPS:**
- CT-020: BHwoN7VPrBE, ~08:00 — "a swing low is a low with a higher low on both sides and a swing high is a high with a lower high on both sides... there's no single formula... recency is important, significance and size of the move following that high or low is important... the basic smell test... what's the most obvious or outstanding high or low you probably can't go wrong with that"
- CT-020: BHwoN7VPrBE, ~08:30 — "if you have a bigger more significant swing away from the level it's probably going to be better and more significant and meaningful generally for your trading"

---

#### C09-E02: CONFLUENCE FOR SWING SELECTION
**Merged CTs:** CT-024, CT-030
**Description:** Swing points at confluent levels (SR, monthly/weekly/daily opens, old highs/lows) are more significant than isolated swings. Stack confluence factors: underlying trend, high timeframes, technical levels, funding, open interest.
**Source GPS:**
- CT-024: BHwoN7VPrBE, ~10:00 — "is the swing high or low you're assessing confluent with another key level... is there a candle open there like the monthly open weekly open daily open etc is there just a good reason to have eyes there"
- CT-024: BHwoN7VPrBE, ~12:00 — "if in doubt sr it out works quite well so by definition horizontal support resistance is derived from old highs and lows"
- CT-030: BHwoN7VPrBE, ~38:00 — "always look for probability enhancers... if the market's kind enough to be in a place where you have some sort of confluence be it the underlying trend high time frames technical confluence funding oi whatever it is you use or proven it's worth make sure to use it"

---

#### C09-E03: PROBABILITY ENHANCERS
**Merged CTs:** CT-030
**Description:** Stack confluence factors (trend, HTF, technical levels, funding, OI) to improve setup probability.
**Source GPS:**
- CT-030: BHwoN7VPrBE, ~38:00 — "always look for probability enhancers... if the market's kind enough to be in a place where you have some sort of confluence be it the underlying trend high time frames technical confluence funding oi whatever it is you use or proven it's worth make sure to use it"

---

#### C09-E04: TIMEFRAMES NOT MUTUALLY EXCLUSIVE — DEFER TO HIGHEST
**Merged CTs:** CT-084
**Description:** A single price level may be visible on multiple timeframes. When classifying which timeframe a level belongs to, defer to the highest timeframe on which it is clearly visible — but no higher. If visible on 4H, daily, and weekly but only faintly on weekly, call it a daily level. This prevents misclassification and mismatched expectations.
**Source GPS:**
- CT-084: Yp0k8HD5xro, ~39:30 — "time frames not mutually exclusive... a weekly area is also likely a daily area etc etc"
- CT-084: Yp0k8HD5xro, ~39:45 — "always the further the higher time frame so if you've got just the level in the market and it's visible on the 4-hour great it's also visible on the daily great and then the weekly... then just call it what it is which in my view I'll just call that a daily level right so defer to the highest timeframe on which it clearly visible but no higher"

---


### C10 — Setup Types: Entry Patterns
*Rules defining specific trade setup patterns.*

#### C10-E01: SETUP 1 — CONTINUATION AT BREAK LEVEL (SR FLIP)
**Merged CTs:** CT-025
**Description:** SR flip setup: enter on pullback to broken level after MSB. Broken support becomes resistance, broken resistance becomes support.
**Source GPS:**
- CT-025: BHwoN7VPrBE, ~45:00 — "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low... broken support turning to resistance on re-test broken resistance turning to support on a re-test"

---

#### C10-E02: COUNTER-TREND = DEFENSIVE PARAMETERS
**Merged CTs:** CT-028
**Description:** Counter-trend trades require: shorter holds, higher R:R minimums (2:1 vs 1.5:1), smaller position size.
**Source GPS:**
- CT-028: BHwoN7VPrBE, ~33:00 — "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... shorter holding periods... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5... different sizing is also another consideration... smaller or more conservative"

---

#### C10-E03: CUT AND REVERSE TRAP
**Merged CTs:** CT-029
**Description:** Automatic cut-and-reverse on invalidation is dangerous. Each setup must be evaluated independently.
**Source GPS:**
- CT-029: BHwoN7VPrBE, ~42:00 — "don't take the cut and reverse for granted... sometimes you just end up in a shitty position the market just doesn't want to mesh with you or there's something else going on so don't assume that you've always identified absolute turning points and that the market's going to be kind enough to let you get in on the other side"

---

#### C10-E04: SETUP 2 — CONTINUATION AT PULLBACK LEVEL (0.618-0.786)
**Merged CTs:** CT-032
**Description:** Fibonacci pullback zone (0.618-0.786) as continuation entry area after breakout. Explicitly noted as personal preference with "no fixed answer."
**Source GPS:**
- CT-032: BHwoN7VPrBE, ~50:00 — "the continuation trade is taken below the breakout point but above the most recent low... i'll map out the low and then the higher high and then as the market starts pulling back it's between these levels that i'll look for structure... personally i look for support resistance structures anywhere between the 618 and 786 retracement"
- CT-032: BHwoN7VPrBE, ~55:00 — "there's no fixed answer really"

---

#### C10-E05: SETUP 3 — REVERSAL ON FAILED MSB
**Merged CTs:** CT-033
**Description:** Failed continuation after MSB = reversal signal. Sequence: MSB occurs -> fails to continue (no follow-through swing) -> reversal setup at prior breakout level.
**Source GPS:**
- CT-033: BHwoN7VPrBE, ~65:00 — "the reversal setup... focuses on trading in the opposite direction of a market structure break... a high that forced the lower low is significant... price closing above it means that strong resistance has failed and strong resistance failing is bullish"
- CT-033: BHwoN7VPrBE, ~66:00 — "failed continuation is suggestive of reversal... if we get a higher high bullish into a lower low invalidated then you have bulls offside... bulls offside makes for a good sell setup"

---


### C11 — Entry Precision & Positioning
*Rules about how precise entries need to be relative to target move size.*

#### C11-E01: PRECISION INVERSELY CORRELATED WITH MOVE SIZE
**Merged CTs:** CT-042, CT-062
**Description:** Entry precision and stop strictness are inversely correlated with the size of the move you're trying to capture. Intraday scalps need precise entries and tight stops. High timeframe swings have more tolerance. Mixing these produces poor trades.
**Source GPS:**
- CT-042: inqHN8q57X4, ~28:30 — "the precision of your entry is inversely correlated with the size of the move you're trying to capture... if you're trading an intraday range there's generally less to capture so your entry must be more precise... if you're trading a high time frame swing there's more to capture so your entry can be less precise"
- CT-042: inqHN8q57X4, ~30:00 — "if you're trading within here right this is your range then you need to be a bit more selective in terms of where you enter... if your resistance is up here and your support is down here does it really matter whether you enter kind of here here maybe even up to here"
- CT-062: XeQV2ECtZVQ, ~11:00 — "strictness with stop usage and placement is inversely correlated with the size of the move you're trying to trade"
- CT-062: XeQV2ECtZVQ, ~11:30 — "if you're being precise with the trade your stop placement should also be precise if you're being less precise with the trade or dealing with a wider area or a higher time frame idea your stop placement can also be less precise or wider"
- CT-062: XeQV2ECtZVQ, ~12:00 — "make sure to not mix the two because that's when you get really shitty trades i.e low time frame trades with a lot of size and really sloppy stop placement which exacerbates losses or high time frame kind of swing ideas where you should be giving the market kind of a chance to breathe and develop structure but instead you're on the one minute chart trying to put a stop order under the first swing low or swing high that you see"

---

#### C11-E02: STRICTNESS INVERSELY CORRELATED WITH MOVE SIZE
**Merged CTs:** CT-062
**Description:** Low timeframe / precise trades need tight, precise stops. High timeframe / swing trades need wider stops that give the market room. Mixing these (e.g., wide stop on a scalp, or tight stop on a swing) produces poor trades.
**Source GPS:**
- CT-062: XeQV2ECtZVQ, ~11:00 — "strictness with stop usage and placement is inversely correlated with the size of the move you're trying to trade"
- CT-062: XeQV2ECtZVQ, ~11:30 — "if you're being precise with the trade your stop placement should also be precise if you're being less precise with the trade or dealing with a wider area or a higher time frame idea your stop placement can also be less precise or wider"
- CT-062: XeQV2ECtZVQ, ~12:00 — "make sure to not mix the two because that's when you get really shitty trades i.e low time frame trades with a lot of size and really sloppy stop placement which exacerbates losses or high time frame kind of swing ideas where you should be giving the market kind of a chance to breathe and develop structure but instead you're on the one minute chart trying to put a stop order under the first swing low or swing high that you see"

---

#### C11-E03: FTA ENTRY — PROXIMITY MATTERS
**Merged CTs:** CT-080
**Description:** Entry FTA should be close to the structure you want to trade. Management FTA should have more breathing room — the trade should have moved significantly before you start managing it. If entry FTA is too far from structure, the "confirmation" becomes meaningless.
**Source GPS:**
- CT-080: Yp0k8HD5xro, ~25:00 — "FTA for trade management levels tend to be a bit further away from structure than FTA for trade entry levels so for trade entry I normally like the FTA to be a bit closer or somewhat close to the structure where I want to do business itself"
- CT-080: Yp0k8HD5xro, ~25:15 — "whereas for management ideally I want a bit more breathing room on the high timeframe level and then for the where I manage the trade to be in an area where the markets already kind of moved significantly"

---

#### C11-E04: DON'T EXPECT MUSHROOM CLOUDS FROM LOW TF LEVELS
**Merged CTs:** CT-081
**Description:** Low timeframe levels (15m, hourly) should not be expected to produce large swings. Expectations must match the timeframe. High timeframe levels produce large moves; low timeframe levels produce small moves. Shorting a 15m breakdown into daily support without realizing it leads to instant reversal.
**Source GPS:**
- CT-081: Yp0k8HD5xro, ~33:30 — "you expect mushroom clouds or full-on crazy volatility in world ending events from low timeframe levels kind of prices in a fifteen-minute range and it breaks you know breaks a trendline or something and that's it you're expecting a two thousand dollar swing down probably not particularly reasonable"
- CT-081: Yp0k8HD5xro, ~33:45 — "if you want to trade large bigger moves you should be more oriented towards the high timeframe levels if you are trading the lower timeframe levels you need to be cognizant of how much impact or perhaps the effect size they are most likely going to have"

---


### C12 — Trade Management Framework
*Rules about the philosophy and mechanics of managing open positions.*

#### C12-E01: EVIDENCE-BASED TRADE MANAGEMENT
**Merged CTs:** CT-047
**Description:** Trade management is the set of decisions between opening and fully closing a position. The core framework is continuously reassessing whether price action supports or contradicts the original trade thesis. If evidence conflicts with the position, close before full stop loss.
**Source GPS:**
- CT-047: _ndAoizXy64, ~01:45 — "trade management a set of decisions made between opening a position and fully closing it"
- CT-047: _ndAoizXy64, ~04:15 — "the evidence sort of for your position so once the trade is opened reassessing the chart and the technicals to see how you should manage the trade"
- CT-047: _ndAoizXy64, ~04:30 — "developments in price since my entry aligned with my expectations for this trade idea so is the chart doing what I expected to do if I'm right essentially"
- CT-047: _ndAoizXy64, ~04:45 — "is price reacting is expected to my technical structure or it's break is priced moving in the expected direction within a reasonable time period is price breaking support resistance or making new lows highs etc etc"
- CT-047: _ndAoizXy64, ~05:00 — "exercise your discretion to always be reassessing whether the evidence which for us as technical traders is the price action supports your position or goes against it"
- CT-047: _ndAoizXy64, ~05:15 — "if we have a certain expectation for price and there is no alignment and indeed you're getting conflicting evidence for your position we're going to look to close that out before a full sized loss"

---

#### C12-E02: MANAGEMENT TIMEFRAME — ENTRY TF + ONE LOWER
**Merged CTs:** CT-048, CT-075
**Description:** Management timeframe should be the entry timeframe plus one lower. Weekly entries → manage on weekly + daily. Daily entries → manage on daily + 4H/6H/12H. FTA for management is typically one TF lower than the trade idea. Balancing act: no low TF consideration misses signals; too much leads to over-management.
**Source GPS:**
- CT-048: _ndAoizXy64, ~08:15 — "if the time frame is too high you may miss out on management opportunities if the time frame is too low will over manage and fake yourself out"
- CT-048: _ndAoizXy64, ~09:00 — "for a weekly setup managing on the entry timeframe so the weekly time frame and a time frame below so the daily that's a good starting point for your studies"
- CT-048: _ndAoizXy64, ~09:15 — "for the daily time frame managing on the entry time frame the daily and then maybe one intraday time frame lower like 12 hour six hour even four hour in this example is fine"
- CT-048: _ndAoizXy64, ~09:30 — "for our intraday trading again for our chart hourly chart using those same time frames or a smaller intraday time frame 30 minute chart 15 minute chart I really think is a nice foundation"
- CT-048: _ndAoizXy64, ~09:45 — "I'll be trading high timeframe from the daily and weekly but a lot of my entries and management will be on the hourly timeframe"
- CT-075: Yp0k8HD5xro, ~34:30 — "for trade management... it's usually ascertained on one timeframe lower"
- CT-075: Yp0k8HD5xro, ~34:45 — "if you have a monthly idea the first trouble area for management would typically be on the weekly timeframe if you've got a weekly idea the level of management would typically be derived from the daily timeframe and then daily idea typically derived from the intraday timeframes"
- CT-075: Yp0k8HD5xro, ~36:00 — "if you give no low timeframe consideration then you miss important management signals"
- CT-075: Yp0k8HD5xro, ~36:45 — "excessive low timeframe consideration will likely mean that you'll over manage the trade or give too much weight to noise"

---

#### C12-E03: MANAGE BOTH SIDES — LOSERS AND WINNERS
**Merged CTs:** CT-049
**Description:** Traders commonly over-manage winners while ignoring losers. Both sides require active management. If price action develops against the position (e.g., resistance flips to support when short), the probability of being correct decreases — exit before full stop loss.
**Source GPS:**
- CT-049: _ndAoizXy64, ~10:15 — "managing both sides of a trade this is really important probably one of the more neglected parts of trade management and what I mean by both sides of a trade is that managing trades that are at a loss so before they hit your stop-loss order as well as those that are in profit"
- CT-049: _ndAoizXy64, ~10:30 — "it's so common to see traders rush to manage a trade and move their stop and lock in profit and take off some size and do whatever else as soon as the trade goes on side... if the trade goes against them they take some heat they sort of pretend it's not happening"
- CT-049: _ndAoizXy64, ~11:00 — "consistently reducing one-hour losers to less than a full size stop out will make a meaningful difference to your equity curve"
- CT-049: _ndAoizXy64, ~11:45 — "if you're seeing that type of price action as a buyer there's no reason for you to in every single instance wait for your manual stop must be hit because as that price action is developing the probability of your trade being correct is decreasing"

---

#### C12-E04: LEVEL PERFORMANCE AS EVIDENCE
**Merged CTs:** CT-050, CT-052
**Description:** When a level performs opposite to expectation (resistance acting as support with consecutive closes above, or vice versa), this is evidence the trade thesis is wrong. Consecutive closes through a level in the wrong direction = management signal to exit. Acceptance at a level = thesis failure.
**Source GPS:**
- CT-050: _ndAoizXy64, ~13:00 — "is resistance acting as resistance if we're expecting this to force prices lower are we getting bearish price action at the level"
- CT-050: _ndAoizXy64, ~13:30 — "not a single hourly close below the level is evidence that the level is being used as support"
- CT-050: _ndAoizXy64, ~14:00 — "we pretty much have the opposite of what we had at the lower boundary we have a closed through the level retest close below another close below"
- CT-050: _ndAoizXy64, ~14:15 — "if your idea is that this level at 60 150 is resistance you're not getting any alignment from price because it's actually acting as support very clearly"
- CT-052: _ndAoizXy64, ~19:45 — "I'm selling resistance for a fast move down back to 6900 we can then look at the price action exercise our discretion and say does this look like bearish price action given I'm short and instead as you can see there was acceptance at the level and consecutive candle closes and even a short-term break in structure as a higher high was made"
- CT-052: _ndAoizXy64, ~20:30 — "if resistance is going to do its job we'll get a lower low and a breakdown right so consolidation of resistance assuming the appropriate time frame is not bullish and not what you'd expect at resistance typically"

---

#### C12-E05: TIME-BASED MANAGEMENT — TRADE EXPIRY
**Merged CTs:** CT-051
**Description:** Three setup types with time sensitivity: (1) Trap setups (SFP, failed breakouts) assume fast rejection — delay shifts probability to genuine breakout; (2) Momentum continuation assumes aggressive follow-through — stalling weakens the setup; (3) S/R setups — prolonged consolidation at a level without reaction shifts probability from bounce to failure.
**Source GPS:**
- CT-051: _ndAoizXy64, ~16:15 — "some trade ideas have an expiry date so while price space management is intuitive... some trade ideas are actually time-sensitive as well as price sensitive"
- CT-051: _ndAoizXy64, ~16:45 — "setups premise on trapped traders... you've got your swing failure pattern failed breakouts price trading beyond the value area or liquidity pool all of those setups assume a fast rejection if the setup is really a trap"
- CT-051: _ndAoizXy64, ~17:15 — "as more time progresses the probabilities shift from trap to genuine breakout because if it is a trap the time window for those guys on the wrong side to get out of breakeven or a de mitigated loss should be quite low"
- CT-051: _ndAoizXy64, ~17:45 — "setups premise on momentum continuation... those types of setups assume aggressive participation ie price not stalling once structure is exceeded"
- CT-051: _ndAoizXy64, ~18:15 — "setups premise on support resistance or equivalent structures so if price spends too much time at a structure without offering a reaction or moving away the probabilities shift from bounce to failure"

---

#### C12-E06: ACCEPTANCE AT LEVEL = THESIS FAILURE
**Merged CTs:** CT-052
**Description:** Chart example at Bitcoin $6,900 level. Selling resistance, but price shows acceptance (consecutive closes above, higher high) instead of rejection. This is a management signal to exit. Resistance doing its job produces lower lows and breakdowns; consolidation at resistance is bearish for the short thesis.
**Source GPS:**
- CT-052: _ndAoizXy64, ~19:45 — "I'm selling resistance for a fast move down back to 6900 we can then look at the price action exercise our discretion and say does this look like bearish price action given I'm short and instead as you can see there was acceptance at the level and consecutive candle closes and even a short-term break in structure as a higher high was made"
- CT-052: _ndAoizXy64, ~20:30 — "if resistance is going to do its job we'll get a lower low and a breakdown right so consolidation of resistance assuming the appropriate time frame is not bullish and not what you'd expect at resistance typically"

---

#### C12-E07: THE DEAD ZONE — NOTHING TO MANAGE
**Merged CTs:** CT-057
**Description:** There is a "dead zone" between stop and target where no management action is needed. Price oscillates with minor heat. Over-managing during this zone is a common error. Especially dangerous: managing a daily trade on the 15m timeframe.
**Source GPS:**
- CT-057: _ndAoizXy64, ~43:00 — "make sure there's something to manage there's a bit of a dead zone I've called it between your stop-loss and your take profit once the positions live and your job there's kind of to do nothing"
- CT-057: _ndAoizXy64, ~43:15 — "price will kind of oscillate a bit and give you a bit of heat glingo onside give you a bit of heat... especially soon after entry there's a good chance that for a bit depending on the timeframes that you trade there's nothing for you to manage so let your idea play out"
- CT-057: _ndAoizXy64, ~43:45 — "if your time frame game is terrible... if you've taken a daily timeframe trade and then you're suddenly on the m15 trying to move your stop I mean don't"

---

#### C12-E08: GOOD ENTRY EASES MANAGEMENT
**Merged CTs:** CT-058
**Description:** Good entries (less heat, immediate favorable reaction) make management psychologically easier. Traders give winning positions more leeway and over-manage less. Does not justify automatic break-even — just reduces stress.
**Source GPS:**
- CT-058: _ndAoizXy64, ~42:15 — "anecdotally I think for anyone and everyone I've talked to and certainly for me it's easier to manage trades which take less heat right if you get a nice entry and then price reacts well to it you're probably going to give it a bit more leeway in developing you're less likely to over manage those positions"

---


### C13 — Profit Taking & Targets
*Rules about how and where to take profits.*

#### C13-E01: PROFIT TAKING — TRAILING STOPS VS FIXED TARGETS
**Merged CTs:** CT-053
**Description:** Two profit-taking systems: (1) Trailing stops under swing lows for trending environments — captures larger moves but risks shakeouts; (2) Fixed targets at range boundaries/ATR for ranging environments. No single system works for all conditions. Risks of trailing stops: assumes trending environment, needs clear invalidation levels, shakeouts often tag obvious stops before continuation.
**Source GPS:**
- CT-053: _ndAoizXy64, ~21:30 — "technically you can trade and never take profit and instead continually move your stop as the market moves in your favor until you are stopped out in profit"
- CT-053: _ndAoizXy64, ~23:15 — "a trend following system in a trending market you're more likely I think to capture a bigger portion of a trend with trailing stops because if you are indeed in a dominant trending environment why would you try to catch the top"
- CT-053: _ndAoizXy64, ~23:30 — "a more kind of mean reverting or... a swing trading system... in a ranging environment fixed proper taking a range boundaries or ATR... makes more sense there"
- CT-053: _ndAoizXy64, ~24:00 — "trade management specifically the profit taking side of things... it's unlikely that you find long-term success with just one system for all instruments all time frames low market conditions you should have at least a couple in your toolkit"

---

#### C13-E02: FTA DEFINITION
**Merged CTs:** CT-073
**Description:** FTA = First Trouble Area. The nearest support or resistance structure to current price. For longs, FTA is nearest resistance. For shorts, FTA is nearest support. Used for profit-taking, trade management, and trade entry.
**Source GPS:**
- CT-073: Yp0k8HD5xro, ~03:45 — "FTA what does it stand for it stands for first trouble area... it is the support or resistance structure nearest the price"
- CT-073: Yp0k8HD5xro, ~04:00 — "if the market is rallying or and or if you're in a long FTA is the nearest resistance structure... if the markets falling or if you're short where could it run into trouble... that would be at an area of support"
- CT-073: Yp0k8HD5xro, ~04:30 — "we're trying to ascertain where the market is most reasonably and most likely going to give our trade some trouble and use that area to manage the trade in some capacity or act on the trade"

---

#### C13-E03: FTA FOR PROFIT-TAKING — SAME TIMEFRAME AS TRADE IDEA
**Merged CTs:** CT-074
**Description:** Profit-taking FTA is on the same timeframe as the trade entry. Daily entry -> daily FTA for take profit. Weekly entry -> weekly FTA for take profit. "Trading crumbs" — taking profit at a much lower timeframe level near entry — defeats the purpose of high timeframe swing trading. The market should obliterate lower timeframe levels if the high timeframe idea is correct.
**Source GPS:**
- CT-074: Yp0k8HD5xro, ~30:00 — "FTA for profit taking is ascertained on the same timeframe as the trade idea"
- CT-074: Yp0k8HD5xro, ~30:15 — "if I'm establishing a position at daily support I'm going to look to take profit at daily resistance"
- CT-074: Yp0k8HD5xro, ~30:30 — "if we're buying weekly support FTA for profit-taking is nearest weekly resistance"
- CT-074: Yp0k8HD5xro, ~33:00 — "we generally want to avoid trading crumbs at high timeframe levels because then what's the point of trading high timeframe levels at all if we're looking for swing trades"

---

#### C13-E04: TWO FTAS AT WORK — PROFIT FTA + MANAGEMENT FTA
**Merged CTs:** CT-076
**Description:** In a swing trade, two FTAs operate simultaneously: (1) Profit-taking FTA = the target level on the same timeframe as the trade idea; (2) Management FTA = the interim obstacle between entry and target, usually one TF lower, used for management signals. Example: weekly entry -> weekly resistance = profit FTA; daily resistance in between = management FTA.
**Source GPS:**
- CT-076: Yp0k8HD5xro, ~16:30 — "there are two FTAs at work one is that is the one is a weekly level we've established for our take profit system... and then the second type of FTA at work is okay so that my swing traders from weekly to weekly where could this weekly idea bump into some trouble"
- CT-076: Yp0k8HD5xro, ~20:30 — "you have two FTAs at work... the take profit for the swing trade which is where you exit the trade and then there's the first reasonable obstacle between your entry and your target where you manage the trade"

---

#### C13-E05: FTA DOES NOT PREVENT SWING TRADING — IT ENABLES IT
**Merged CTs:** CT-085
**Description:** A common criticism is that FTA prevents catching big moves. The opposite is true — FTA is a framework for swing trading. Entry, target, and stop are based on high timeframe levels. Interim lower timeframe levels are used to inform management decisions, not to prematurely exit.
**Source GPS:**
- CT-085: Yp0k8HD5xro, ~37:30 — "taking profit at FTA means it's impossible to swing trade which is a very common criticism that I've heard... I'd say the opposite is true and that argument is based on a misconception"
- CT-085: Yp0k8HD5xro, ~38:00 — "the base function or on the base layer we move from weekly to weekly from daily to daily from early to hourly etc etc but we use interim or levels in between those high timeframe structures to inform our decision-making"

---


### C14 — Dynamic Risk/Reward
*Rules about how R:R evolves as a trade develops.*

#### C14-E01: DYNAMIC RISK/REWARD
**Merged CTs:** CT-054, CT-066
**Description:** R:R is not static — it adjusts as soon as the trade is live. The 'fresh trade' test: if offered the current price, current stop, and current target as a new trade right now, would you take it? If no, manage the position (move stop or take profit). A trade that started at 2R can become 0.25R if price reaches 85% of target with stop untouched. Especially critical when price makes a large thrust candle close to target.
**Source GPS:**
- CT-054: _ndAoizXy64, ~25:00 — "the risk reward of a trade is not static it adjusts as soon as the trade is live and price moves away from entries as a dynamic calculation"
- CT-054: _ndAoizXy64, ~25:30 — "if someone offered you the current price your current stop-loss order and your current take profit order as a trade right now would you take it and if the answers yes then that's good so your risk rewards and trade management is reasonable if the answer is no... the risk to all of the trade is less favorable so manage it either by moving stop-loss order and or by taking profits"
- CT-054: _ndAoizXy64, ~26:15 — "if you let the trade come this close to target... and you haven't moved your stop or done anything to manage the trade then you are risking this much extra profit at the expense of a full sized loss"
- CT-054: _ndAoizXy64, ~27:30 — "dynamic risk reward is also especially important... when you really get on side with a big thrust candle so an expansive engulfing candle with a big range"
- CT-066: XeQV2ECtZVQ, ~26:00 — "the risk to reward ratio of a trade evolves as price moves away from from your entry point either to your target or even to your stop"
- CT-066: XeQV2ECtZVQ, ~27:00 — "at the inception of the trade you have 2r... then as the market comes into this level and starts to struggle... the adjusted risk to reward of the trade at the time that it's actually moved drops drastically to 0.25 r"
- CT-066: XeQV2ECtZVQ, ~29:00 — "the emphasis should be on making sure trades that are near completion don't round trip and come back to stop you out"

---

#### C14-E02: DYNAMIC RISK/REWARD (EVOLVING R)
**Merged CTs:** CT-066
**Description:** Tom Dante's "evolving R" concept. As price moves toward target, the remaining R:R degrades if stop is not adjusted. A trade that started at 2R can become 0.25R if price reaches 85% of target with stop untouched. Purpose: wake-up call to manage trades near completion, not to force arbitrary management on every trade.
**Source GPS:**
- CT-066: XeQV2ECtZVQ, ~26:00 — "the risk to reward ratio of a trade evolves as price moves away from from your entry point either to your target or even to your stop"
- CT-066: XeQV2ECtZVQ, ~27:00 — "at the inception of the trade you have 2r... then as the market comes into this level and starts to struggle... the adjusted risk to reward of the trade at the time that it's actually moved drops drastically to 0.25 r"
- CT-066: XeQV2ECtZVQ, ~29:00 — "the emphasis should be on making sure trades that are near completion don't round trip and come back to stop you out"

---


### C15 — Break-Even Stop Skepticism
*Rules strongly cautioning against automatic or premature break-even stop placement.*

#### C15-E01: SKEPTICISM OF AUTOMATIC BREAK-EVEN STOPS
**Merged CTs:** CT-055, CT-069, CT-083
**Description:** Moving stops to break-even is not risk-free — the risk changes to being stopped out while still correct. Most BE stop decisions are made for psychological comfort, not because they improve trade outcomes. Moving to BE means selling support (if long) or buying resistance (if short) — the opposite of the original thesis. High timeframe levels often see multiple intraday retests before the real move. Automatic BE abandons the technical framework. Justifiable only if revisiting entry actually invalidates the idea, which is rare. The 'swing trade graveyard' = moving to BE on the first reaction at a high TF level, getting stopped out at entry, then missing the high timeframe move.
**Source GPS:**
- CT-055: _ndAoizXy64, ~28:30 — "moving a trade to break even as soon as possible after it moves positively away from entry... doing that removes all risk from the trade it becomes a free trade"
- CT-055: _ndAoizXy64, ~29:15 — "the risk doesn't become risk-free is just the nature of the risk changes when you move your stuff to break-even the risk becomes getting stopped out while still being right before your idea can materialize"
- CT-055: _ndAoizXy64, ~29:45 — "price will very often retest technical structures especially if they are high timeframe levels... on an intraday basis you'll actually see multiple tests of that structure before it eventually leads to move"
- CT-055: _ndAoizXy64, ~31:00 — "you end up buying the resistance you sold or selling the support that you bought"
- CT-055: _ndAoizXy64, ~31:45 — "your fettering your discretion and abandoning your technical trading framework if you just automatically move to break-even without having a technical basis for doing so"
- CT-069: XeQV2ECtZVQ, ~43:00 — "most break even stop and partial profit decisions are made to achieve psychological comfort not because those decisions improve trade outcomes in the long run"
- CT-069: XeQV2ECtZVQ, ~45:00 — "break even stopping along... i'm bearish in the place that i bought previously"
- CT-069: XeQV2ECtZVQ, ~45:30 — "selling where you bought previously... that's the exception to the rule what you're really doing is saying i don't have conviction in this trade"
- CT-069: XeQV2ECtZVQ, ~46:30 — "it can be justifiable where revisiting the entry invalidates the idea or makes the setup very likely to fail but i'd be willing to bet nine times out of ten when people put a break even stop on a trade it's not a considered opinion"
- CT-083: Yp0k8HD5xro, ~40:15 — "you get involved at the trade at the level the market moves in your favor... normally you'll see traders just put their stop... moves to break-even because you feel good... what price will often do or sometimes do then bounce at a lower timeframe first trouble area... because you moved to break-even you're unable to stomach a retest of your entry... the high timeframe move materializes and breaks first trouble area in the process"
- CT-083: Yp0k8HD5xro, ~41:00 — "I generally almost never encourage swing traders to move their stop or adjust their parameters based on the very very first reaction that a market gives to a high timeframe level"

---

#### C15-E02: BREAK-EVEN STOPS ARE PSYCHOLOGICAL COPE
**Merged CTs:** CT-069
**Description:** Break-even stops are usually psychological coping, not process-driven decisions. Moving stop to BE means selling support (if long) or buying resistance (if short) — the opposite of the original thesis. Justifiable only if revisiting entry actually invalidates the idea, which is rare. Partial profits similarly arbitrary unless justified by evolving R.
**Source GPS:**
- CT-069: XeQV2ECtZVQ, ~43:00 — "most break even stop and partial profit decisions are made to achieve psychological comfort not because those decisions improve trade outcomes in the long run"
- CT-069: XeQV2ECtZVQ, ~45:00 — "break even stopping along... i'm bearish in the place that i bought previously"
- CT-069: XeQV2ECtZVQ, ~45:30 — "selling where you bought previously... that's the exception to the rule what you're really doing is saying i don't have conviction in this trade"
- CT-069: XeQV2ECtZVQ, ~46:30 — "it can be justifiable where revisiting the entry invalidates the idea or makes the setup very likely to fail but i'd be willing to bet nine times out of ten when people put a break even stop on a trade it's not a considered opinion"

---

#### C15-E03: SWING TRADE GRAVEYARD — BREAK-EVEN ON FIRST REACTION
**Merged CTs:** CT-083
**Description:** Moving stops to break-even on the first reaction at a high TF level is the "swing trade graveyard." Price often retests the high TF level on lower timeframes before the real move. Moving to BE means getting stopped out at your entry (buying resistance you sold, or selling support you bought) and missing the high timeframe move. Exception: if revisiting entry actually invalidates the idea.
**Source GPS:**
- CT-083: Yp0k8HD5xro, ~40:15 — "you get involved at the trade at the level the market moves in your favor... normally you'll see traders just put their stop... moves to break-even because you feel good... what price will often do or sometimes do then bounce at a lower timeframe first trouble area... because you moved to break-even you're unable to stomach a retest of your entry... the high timeframe move materializes and breaks first trouble area in the process"
- CT-083: Yp0k8HD5xro, ~41:00 — "I generally almost never encourage swing traders to move their stop or adjust their parameters based on the very very first reaction that a market gives to a high timeframe level"

---


### C16 — Invalidation, Stops & Stop Placement
*Rules about defining trade invalidation and placing stops.*

#### C16-E01: INVALIDATION AS FALSIFIABLE IDEA
**Merged CTs:** CT-060
**Description:** Every trade idea must be falsifiable. Invalidation is derived from the trade idea itself — not from unrelated factors. Price-based, time-based, and volatility-based invalidation examples given. The link between idea and invalidation must be clear and proximate.
**Source GPS:**
- CT-060: XeQV2ECtZVQ, ~03:00 — "invalidation is when your idea is almost certainly in brackets wrong it's just where you're wrong"
- CT-060: XeQV2ECtZVQ, ~02:30 — "there needs to be some sense of invalidation for when that idea is most likely if not outrightly no longer correct"
- CT-060: XeQV2ECtZVQ, ~04:00 — "invalidation is usually a product of the idea itself it's sort of built in to the trade idea"
- CT-060: XeQV2ECtZVQ, ~04:30 — "there should be a very clear link between the trade idea itself and the invalidation of that idea if those two things are completely disparate then you know something is likely wrong"
- CT-060: XeQV2ECtZVQ, ~07:30 — "the reason you're wrong is very closely tied to the reason for taking the trade in the first place"

---

#### C16-E02: STOP PLACEMENT = INVALIDATION
**Merged CTs:** CT-061
**Description:** Stop placement must reflect the trade's invalidation point. If you would want to enter where your stop is, the stop placement (and likely the trade idea) is flawed. Stop hunting complaints are usually explained by poor stop placement, not deliberate market manipulation.
**Source GPS:**
- CT-061: XeQV2ECtZVQ, ~09:00 — "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation and we know that your invalidation is derived from the trade idea"
- CT-061: XeQV2ECtZVQ, ~09:15 — "if you don't know where to put a stop that often means the idea itself was not defined very clearly"
- CT-061: XeQV2ECtZVQ, ~10:00 — "would i want to buy where my long gets stopped out and or would i want to sell where my short gets stopped out if the answer is yes then there's a good chance that the trade sucks especially if you trade technicals and maybe you should be looking to trade at your stop rather than exiting the trade at your stop"

---

#### C16-E03: HARD STOP VS SOFT STOP
**Merged CTs:** CT-063
**Description:** Hard stop = market order, full close, for precise setups. Soft stop = mental/manual scaling, for swing ideas with wider invalidation. Beginners should use hard stops exclusively. Getting stopped out teaches better trade identification over time.
**Source GPS:**
- CT-063: XeQV2ECtZVQ, ~12:45 — "hard stop... market order to close the full position at a certain price or loss threshold... best used for clearly defined setups and or setups where entry is close to invalidation which usually means more size"
- CT-063: XeQV2ECtZVQ, ~13:15 — "soft stop... mental stop to start closing out the position... more suitable for your kind of swing tradie and ideas that are less reliant on precision"
- CT-063: XeQV2ECtZVQ, ~14:00 — "as a beginner you should just use hard stops... soft stops just require more experience"

---


### C17 — Risk / Position Sizing
*Rules about position size calculation, risk variation, leverage, and crypto correlations.*

#### C17-E01: POSITION SIZE FORMULA
**Merged CTs:** CT-064
**Description:** Explicit formula: Position Size = (Portfolio × Risk%) / Distance to Invalidation. Example given: $100K portfolio, 2% risk, 5% stop distance = $40K position size. Does not account for slippage/fees — assumes liquid markets.
**Source GPS:**
- CT-064: XeQV2ECtZVQ, ~17:00 — "position size is calculated by multiplying your portfolio by your risk percentage and then dividing that by the distance to your invalidation from your entry"
- CT-064: XeQV2ECtZVQ, ~17:30 — "position size equals portfolio times risk percentage divided by distance and validation"

---

#### C17-E02: RISK PER TRADE AS SPECTRUM (EV + FREQUENCY)
**Merged CTs:** CT-065
**Description:** Risk per trade should vary based on setup expected value (EV) and frequency. High-frequency + marginal EV = small or no risk. High-frequency + good EV = moderate risk. Low-frequency + great EV = largest risk. High-frequency + high EV = "golden goose" — milk it while it lasts, then discard when it breaks.
**Source GPS:**
- CT-065: XeQV2ECtZVQ, ~18:30 — "fixed risk per trade is mostly [__]... it assumes that all the setups carry the same expected value"
- CT-065: XeQV2ECtZVQ, ~20:00 — "frequent setups with marginal odds that warrants marginal bets... frequent setups with good odds that typically warrants bigger bets... less frequent setups with great odds generally warrant the biggest bets"
- CT-065: XeQV2ECtZVQ, ~22:00 — "bet less if anything on meh odds and bet more with higher conviction on lower frequency good odds"
- CT-065: XeQV2ECtZVQ, ~21:00 — "if you find like a high frequency high ev edge that's kind of the golden goose of trading... milk it while it's there just be very aware that as soon as that stops working it's likely going to not be an edge at all"

---

#### C17-E03: LEVERAGE = COLLATERALIZATION, NOT P&L
**Merged CTs:** CT-071
**Description:** Leverage does not change P&L — position size does. Leverage only affects how much collateral is required and how close liquidation is. A $10K position at 2x leverage and the same $10K position at 10x leverage produce identical P&L on a 5% move. Main risk management tools are position size and stop placement; leverage is secondary (collateralization/liquidation proximity).
**Source GPS:**
- CT-071: XeQV2ECtZVQ, ~54:00 — "cranking up the leverage slider does not increase or decrease your p l your p l is dictated by your position size"
- CT-071: XeQV2ECtZVQ, ~54:30 — "leverage merely affects how collateralized you are for that position size"
- CT-071: XeQV2ECtZVQ, ~55:00 — "leverage equals collateralization"
- CT-071: XeQV2ECtZVQ, ~55:30 — "low leverage typically means you've offered more margin or collateral for that position and your liquidation is further away from price and of course the opposite is true whereby high leverage typically means you've offered less margin or collateral for that position which means your liquidation is closer to price"

---

#### C17-E04: CRYPTO CORRELATIONS — DOWNSIDE STACKING
**Merged CTs:** CT-072
**Description:** Crypto altcoins have strong positive correlation to BTC/ETH on the downside. Holding multiple altcoin positions does not provide meaningful diversification in a risk-off environment. Downside moves are highly correlated across sectors. Fewer high-conviction trades preferred over "diversified" baskets that stack risk.
**Source GPS:**
- CT-072: XeQV2ECtZVQ, ~59:00 — "when bitcoin and ethereum nuke the rest of the market tends to nuke with them"
- CT-072: XeQV2ECtZVQ, ~59:15 — "diversification in crypto is still very tricky when it comes to the downside"
- CT-072: XeQV2ECtZVQ, ~59:45 — "you're essentially stacking your risk because if you're wrong they'll all move down in the same direction"

---


### C18 — Psychological / Process Discipline
*Rules about trading psychology, process orientation, and avoiding P&L-driven decisions.*

#### C18-E01: TRADE THE CHART, NOT YOUR P&L
**Merged CTs:** CT-056, CT-070
**Description:** Core psychological principle: focus on process and price action, not P&L. The market is agnostic to individual trade parameters. P&L-driven decisions are emotionally driven and non-replicable. Technical trading is replicable; P&L trading is not. Trade management must be process-oriented and derived from the trade idea, not emotions. Arbitrary decisions cannot be optimized or studied.
**Source GPS:**
- CT-056: _ndAoizXy64, ~02:45 — "it's important as technical traders or as speculators generally to trade the chart not your P&L"
- CT-056: _ndAoizXy64, ~03:00 — "I started trading really well and saw big improvements in my own performance when I focused on the process of trading well rather than the P&L"
- CT-056: _ndAoizXy64, ~03:15 — "the market doesn't know doesn't care where you entered or you exit or your risk rule to any of those things it's agnostic as to your particular circumstances"
- CT-056: _ndAoizXy64, ~41:30 — "trading your P&L becomes emotionally driven and actually worse and unreplicated... if you're trading your P&L your emotions at the time your exact sizing the numbers on the screen how quick your piano changes none of that is easily replicable"
- CT-070: XeQV2ECtZVQ, ~43:30 — "trade management decisions should never be arbitrary and should almost always be derived from the trade idea itself"
- CT-070: XeQV2ECtZVQ, ~48:00 — "if you cut your trades early at break even in the long run you probably perform better by letting your setup logic play out and the same for taking profit early in the long run assuming it's arbitrary of course not like an evolving r example"
- CT-070: XeQV2ECtZVQ, ~48:30 — "if you manage your trades according to a system or somewhat objective criteria you at least have data you have evidence that you can review and optimize... however if you're just randomly closing trades... those decisions don't give you any useful or actionable information"

---

#### C18-E02: MARKET DOES NOT KNOW YOUR TRADE HISTORY
**Merged CTs:** CT-059
**Description:** Prior trade outcomes (win streak, loss streak, scratch session) must not influence current trade management. Closing a runner early to "make back losses" violates the system. Defer to the established process, not P&L recovery psychology.
**Source GPS:**
- CT-059: _ndAoizXy64, ~44:15 — "the market doesn't know or care whether you've been losing or winning... trading in contravention to your established system based on previous trades is sacrificing a good process for P&L comfort not sustainable not recommended"
- CT-059: _ndAoizXy64, ~44:30 — "let's say you've been getting scratched in the session... and then you get a runner one that makes up for all the preceding losses and your system is telling you to hold it but you might want to close it because oh my god my P&L I can make back everything I've lost I would say in those circumstances as far as you can defer to the established system and the process"

---

#### C18-E03: BEGINNERS — CONSERVATIVE TARGETS + SET AND FORGET
**Merged CTs:** CT-067
**Description:** Beginners should use conservative targets (First Trouble Area) and set-and-forget approach. Early-stage traders are more likely to over-manage than under-manage. Consistent set-and-forget data is more valuable than emotion-driven interventions.
**Source GPS:**
- CT-067: XeQV2ECtZVQ, ~30:00 — "beginners are usually better served learning via conservative targets and set and forget so conservative targets just mean like fta or the first trouble area"
- CT-067: XeQV2ECtZVQ, ~30:30 — "early on in your trading career purely probabilistically you're far more likely to over manage a trade than under manage it"

---

#### C18-E04: STREAKS — SETUP-SPECIFIC, NOT GLOBAL
**Merged CTs:** CT-068
**Description:** Losing streaks should be analyzed per-setup, not globally. One setup failing does not mean all setups are broken. Trending setups may print while ranging setups lose — don't reduce risk on winners because losers are struggling. Short-term streaks do not necessarily indicate a setup is trash; consider variance, incorrect identification, and regime shifts.
**Source GPS:**
- CT-068: XeQV2ECtZVQ, ~38:00 — "it's very unlikely that everything you do stops working see where the odds have shifted"
- CT-068: XeQV2ECtZVQ, ~36:30 — "if your ranging setups are eating [__] sure but your trending setups are completely printing why would you back off the stuff that's working just because some other stuff isn't working"
- CT-068: XeQV2ECtZVQ, ~37:00 — "ditching a profitable setup after a small string of losses is just a bad idea"
- CT-068: XeQV2ECtZVQ, ~39:00 — "if something is working well you don't know how long that's going to last for but you should take advantage of it while it's there"

---

#### C18-E05: PROCESS OVER P&L IN MANAGEMENT
**Merged CTs:** CT-070
**Description:** Trade management must be process-oriented and derived from the trade idea, not P&L or emotions. Arbitrary decisions (closing because of green P&L, fear of underwater) cannot be optimized or studied. Even if arbitrary management doesn't harm returns, it wastes the data needed for improvement.
**Source GPS:**
- CT-070: XeQV2ECtZVQ, ~43:30 — "trade management decisions should never be arbitrary and should almost always be derived from the trade idea itself"
- CT-070: XeQV2ECtZVQ, ~48:00 — "if you cut your trades early at break even in the long run you probably perform better by letting your setup logic play out and the same for taking profit early in the long run assuming it's arbitrary of course not like an evolving r example"
- CT-070: XeQV2ECtZVQ, ~48:30 — "if you manage your trades according to a system or somewhat objective criteria you at least have data you have evidence that you can review and optimize... however if you're just randomly closing trades... those decisions don't give you any useful or actionable information"

---


### C19 — FTA Management Signals
*Rules about using FTA breaks and failures as management signals during a trade.*

#### C19-E01: FAILURE TO BREAK FTA = EVIDENCE OF WEAKNESS
**Merged CTs:** CT-077
**Description:** If price fails to break the management FTA, this is evidence the trade is not ready to play out. Aggressive management: close the trade. Conservative management: prepare for a retest of entry structure. Daily resistance stopping a weekly move shows the higher timeframe move hasn't yet taken precedence.
**Source GPS:**
- CT-077: Yp0k8HD5xro, ~17:00 — "if a market fails to break lower timeframe first trouble area what does that actually mean well firstly that's evidence that it's not ready to break out or break down"
- CT-077: Yp0k8HD5xro, ~18:00 — "failure to do so is a sign of weakness or viewed another way daily resistance stopping a weekly timeframe move is also in itself a sign of weakness because it's showing the timeframe precedence"
- CT-077: Yp0k8HD5xro, ~18:15 — "if you want to be aggressive you can pretty much close the trade if FTA fails to break because the signal that the market is telling you... if you're high timeframe idea is correct the price is going to travel from weekly level to weekly level"
- CT-077: Yp0k8HD5xro, ~18:30 — "this is evidence of an entry retest so what you'll often see is a nice move from the weekly time frame price essentially takes a breather at FTA... bounces and then either makes a higher low and then breaks through or maybe retest the level"

---

#### C19-E02: SUCCESS IN BREAKING FTA = EVIDENCE IDEA IS CORRECT
**Merged CTs:** CT-078
**Description:** Breaking the management FTA is evidence the trade idea is developing correctly. Signals generated: (1) Compound/add to position (aggressive); (2) Move stop to new invalidation at the broken FTA structure; (3) Do nothing (context-dependent — more justified early in the trade, less justified when up significant R).
**Source GPS:**
- CT-078: Yp0k8HD5xro, ~19:30 — "if the market succeeds in breaking first trouble area... that's evidence that your idea is on the right path"
- CT-078: Yp0k8HD5xro, ~19:45 — "you can compound or add to your position which is quite aggressive... you can move your stop loss to new invalidation at the FTA structure"
- CT-078: Yp0k8HD5xro, ~20:00 — "do nothing is really kind of context dependent... I think trade management should inform whether you have something to do or not"

---

#### C19-E03: FTA FOR TRADE ENTRY — BREAK OF FTA AS TRIGGER
**Merged CTs:** CT-079
**Description:** When conviction at a level is low (e.g., tested too many times, not risk-defined, big inefficiency below), wait for the level to prove itself by breaking the nearby FTA. Enter on break of FTA rather than at the level itself. This is a more robust articulation of "confirmation" — paying a worse entry for higher probability. Also valid when market is "in the middle of nowhere" between levels.
**Source GPS:**
- CT-079: Yp0k8HD5xro, ~23:00 — "when price is moving between high timeframe levels and a trade at the high timeframe level itself is unfavorable a position can be established on a break of FTA"
- CT-079: Yp0k8HD5xro, ~24:00 — "6k support I'm not comfortable buying it given it's been tested too many times I need more proof... if the move from 6k weekly breaks daily resistance at 6300 FTA I will enter a trade"
- CT-079: Yp0k8HD5xro, ~26:00 — "if for whatever reason your conviction at the level is not high you're essentially saying look this is support I need more convincing if this support is going to hold it's going to have no problem breaking resistance so therefore I will enter not at support but on the break of resistance"

---


### C20 — LVN as Rejection Zone
*Rule about low volume nodes acting as rejection zones when revisited.*

#### C20-E01: LVN AS REJECTION ZONE — ACTIONABLE ON RETURN
**Merged CTs:** CT-007
**Description:** Low volume regions are areas where the market was not accepted, where it was shut off. As the market trades back there, anyone who longed from the nearby HVN on the way down may want to exit if the market returns to that level. LVNs act as rejection zones on return. Prior session LVNs far more relevant than old ones. (Also covered in C01 Proximity/Recency.)
**Source GPS:**
- CT-007: Oy2Z-FQ77NM, ~10:30 — "Low volume regions, these are areas where the market was not accepted where it was shut off... As the market trades back there, what's one reason why the market would not be accepted there on the return? Well, anyone that longed from this HVN on the way down, it's local enough, they might want to be getting out of position if the market trades back to that level."
- CT-007: Oy2Z-FQ77NM, ~10:45 — "LVN from the prior session matters a lot more than an LVN from 6 months ago."

---


## MASTER CATALOG — CT ID TO CONSOLIDATED ENTRY CROSS-REFERENCE

| CT ID | Original Rule Name | Cluster | Consolidated Entry | Analyst | Video ID |
|-------|-------------------|---------|-------------------|---------|----------|
| CT-001 | VP IS DESCRIPTIVE, NOT PREDICTIVE | C01 | C01-E01 | The Flow Horse | Oy2Z-FQ77NM |
| CT-002 | PROXIMITY PRINCIPLE — SHORT-TERM PROFILES > LONG-TERM FOR POSITIONING | C01 | C01-E03 | The Flow Horse | Oy2Z-FQ77NM |
| CT-003 | TEST COUNT DEGRADATION — REPEATED TESTS WEAKEN ZONE RELIABILITY | C06 | C06-E01 | The Flow Horse | Oy2Z-FQ77NM |
| CT-004 | SIDEWAYS COMPRESSION -> VIOLENT RESOLUTION | C02 | C02-E01 | The Flow Horse | Oy2Z-FQ77NM |
| CT-005 | HEAD FAKE SIGNATURE — LACK OF VOLUME/MOMENTUM ON BREAK | C04 | C04-E01 | The Flow Horse | Oy2Z-FQ77NM |
| CT-006 | RETEST AFTER REAL BREAK — THROWBACK TO REACCEPT | C07 | C07-E02 | The Flow Horse | Oy2Z-FQ77NM |
| CT-007 | LVN AS REJECTION ZONE — ACTIONABLE ON RETURN | C20 | C20-E01 | The Flow Horse | Oy2Z-FQ77NM |
| CT-008 | STRUCTURE VS FLOW — PROFILE GIVES AREAS, ORDER FLOW GIVES EXECUTION | C01 | C01-E02 | The Flow Horse | Oy2Z-FQ77NM |
| CT-009 | OLD PROFILES = CONTEXT, NOT EXECUTION | C01 | C01-E03 | The Flow Horse | Oy2Z-FQ77NM |
| CT-010 | COMPOSITE PROFILES — ONLY FOR TIGHT OVERLAP | C01 | C01-E04 | The Flow Horse | Oy2Z-FQ77NM |
| CT-011 | POC PLATFORM VARIANCE — DATA SOURCE CONSISTENCY MATTERS | C01 | C01-E05 | The Flow Horse | Oy2Z-FQ77NM |
| CT-012 | HEAVY SELLING PRESSURE + NO BREAKDOWN = ABSORPTION | C03 | C03-E01 | The Flow Horse | zMM9QgxfEFI |
| CT-013 | VOLATILITY COMPRESSION PRECEDES RANGE RESOLUTION | C02 | C02-E01 | The Flow Horse | zMM9QgxfEFI |
| CT-014 | EXTENDED BALANCE + HIGH-VOLUME BREAK = MEASURED MOVE TARGET | C02 | C02-E02 | The Flow Horse | zMM9QgxfEFI |
| CT-015 | REAL CHANGE HAPPENS AT EXTREMES, NOT WITHIN STRUCTURE | C02 | C02-E03 | The Flow Horse | zMM9QgxfEFI |
| CT-016 | BREAK CANDLE LOW = HARD INVALIDATION AFTER HIGH-VOLUME BREAK | C05 | C05-E01 | The Flow Horse | zMM9QgxfEFI |
| CT-017 | SHALLOW PULLBACK AFTER HIGH-VOLUME BREAK = LEGITIMATE CONTINUATION | C05 | C05-E02 | The Flow Horse | zMM9QgxfEFI |
| CT-018 | DAY OF BALANCE AFTER BREAKOUT = CONTINUATION BUILDING | C05 | C05-E03 | The Flow Horse | zMM9QgxfEFI |
| CT-019 | SELLER EXHAUSTION + PRICE HOLD = ACCUMULATION STRUCTURE | C03 | C03-E01 | The Flow Horse | zMM9QgxfEFI |
| CT-020 | SWING HIGH/LOW QUALITY FILTERS | C09 | C09-E01 | CryptoCred | BHwoN7VPrBE |
| CT-021 | MSB DEFINITION — HIGHER HIGH / LOWER LOW | C08 | C08-E01 | CryptoCred | BHwoN7VPrBE |
| CT-022 | MSB AS CONTEXT TOOL, NOT MECHANICAL SYSTEM | C08 | C08-E02 | CryptoCred | BHwoN7VPrBE |
| CT-023 | DO NOT CHASE EVERY MSB | C08 | C08-E03 | CryptoCred | BHwoN7VPrBE |
| CT-024 | CONFLUENCE FOR SWING SELECTION | C09 | C09-E02 | CryptoCred | BHwoN7VPrBE |
| CT-025 | SETUP 1 — CONTINUATION AT BREAK LEVEL (SR FLIP) | C10 | C10-E01 | CryptoCred | BHwoN7VPrBE |
| CT-026 | MSB IN RANGE = NOISE | C08 | C08-E03 | CryptoCred | BHwoN7VPrBE |
| CT-027 | TIME FRAME OF MSB = EXPECTED MOVE SIZE | C08 | C08-E04 | CryptoCred | BHwoN7VPrBE |
| CT-028 | COUNTER-TREND = DEFENSIVE PARAMETERS | C10 | C10-E02 | CryptoCred | BHwoN7VPrBE |
| CT-029 | CUT AND REVERSE TRAP | C10 | C10-E03 | CryptoCred | BHwoN7VPrBE |
| CT-030 | PROBABILITY ENHANCERS | C09 | C09-E02 | CryptoCred | BHwoN7VPrBE |
| CT-031 | CANDLE BODIES FOR STRUCTURE, CLOSES FOR BREAKS | C08 | C08-E05 | CryptoCred | BHwoN7VPrBE |
| CT-032 | SETUP 2 — CONTINUATION AT PULLBACK LEVEL (0.618-0.786) | C10 | C10-E04 | CryptoCred | BHwoN7VPrBE |
| CT-033 | SETUP 3 — REVERSAL ON FAILED MSB | C10 | C10-E05 | CryptoCred | BHwoN7VPrBE |
| CT-034 | EARLY WARNING — FAILURE TO CONTINUE | C08 | C08-E06 | CryptoCred | BHwoN7VPrBE |
| CT-035 | RETEST IS NOT REQUIRED TO CONFIRM A LEVEL | C07 | C07-E01 | CryptoCred | inqHN8q57X4 |
| CT-036 | BREAKOUT VS RETEST = RISK/REWARD TRADE-OFF | C07 | C07-E03 | CryptoCred | inqHN8q57X4 |
| CT-037 | TIMEFRAME ALIGNMENT FOR BREAK VALIDATION | C07 | C07-E04 | CryptoCred | inqHN8q57X4 |
| CT-038 | IMMEDIATE VS ROUNDED RETEST | C07 | C07-E05 | CryptoCred | inqHN8q57X4 |
| CT-039 | SPLIT POSITION = SUB-OPTIMAL EITHER WAY | C07 | C07-E06 | CryptoCred | inqHN8q57X4 |
| CT-040 | PRECEDENT — INSTRUMENT'S RETEST BEHAVIOR | C07 | C07-E07 | CryptoCred | inqHN8q57X4 |
| CT-041 | R:R DECIDES — BIG BREAK FORCES RETEST WAIT | C07 | C07-E08 | CryptoCred | inqHN8q57X4 |
| CT-042 | PRECISION INVERSELY CORRELATED WITH MOVE SIZE | C11 | C11-E01 | CryptoCred | inqHN8q57X4 |
| CT-043 | HIDDEN RETESTS ON LOWER TIMEFRAMES | C07 | C07-E09 | CryptoCred | inqHN8q57X4 |
| CT-044 | DON'T CHASE BREAKOUTS IN RANGES | C04 | C04-E02 | CryptoCred | inqHN8q57X4 |
| CT-045 | STRONG TREND = FAILED BREAKDOWNS AT SUPPORT | C04 | C04-E03 | CryptoCred | inqHN8q57X4 |
| CT-046 | ROUNDED RETEST CONTEXT — WHAT HAPPENED BETWEEN BREAK AND RETEST | C07 | C07-E10 | CryptoCred | inqHN8q57X4 |
| CT-047 | EVIDENCE-BASED TRADE MANAGEMENT | C12 | C12-E01 | CryptoCred | _ndAoizXy64 |
| CT-048 | MANAGEMENT TIMEFRAME — ENTRY TF + ONE LOWER | C12 | C12-E02 | CryptoCred | _ndAoizXy64 |
| CT-049 | MANAGE BOTH SIDES — LOSERS AND WINNERS | C12 | C12-E03 | CryptoCred | _ndAoizXy64 |
| CT-050 | LEVEL PERFORMANCE AS EVIDENCE | C12 | C12-E04 | CryptoCred | _ndAoizXy64 |
| CT-051 | TIME-BASED MANAGEMENT — TRADE EXPIRY | C12 | C12-E05 | CryptoCred | _ndAoizXy64 |
| CT-052 | ACCEPTANCE AT LEVEL = THESIS FAILURE | C12 | C12-E04 | CryptoCred | _ndAoizXy64 |
| CT-053 | PROFIT TAKING — TRAILING STOPS VS FIXED TARGETS | C13 | C13-E01 | CryptoCred | _ndAoizXy64 |
| CT-054 | DYNAMIC RISK/REWARD | C14 | C14-E01 | CryptoCred | _ndAoizXy64 |
| CT-055 | SKEPTICISM OF AUTOMATIC BREAK-EVEN STOPS | C15 | C15-E01 | CryptoCred | _ndAoizXy64 |
| CT-056 | TRADE THE CHART, NOT YOUR P&L | C18 | C18-E01 | CryptoCred | _ndAoizXy64 |
| CT-057 | THE DEAD ZONE — NOTHING TO MANAGE | C12 | C12-E07 | CryptoCred | _ndAoizXy64 |
| CT-058 | GOOD ENTRY EASES MANAGEMENT | C12 | C12-E08 | CryptoCred | _ndAoizXy64 |
| CT-059 | MARKET DOES NOT KNOW YOUR TRADE HISTORY | C18 | C18-E02 | CryptoCred | _ndAoizXy64 |
| CT-060 | INVALIDATION AS FALSIFIABLE IDEA | C16 | C16-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-061 | STOP PLACEMENT = INVALIDATION | C16 | C16-E02 | CryptoCred | XeQV2ECtZVQ |
| CT-062 | STRICTNESS INVERSELY CORRELATED WITH MOVE SIZE | C11 | C11-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-063 | HARD STOP VS SOFT STOP | C16 | C16-E03 | CryptoCred | XeQV2ECtZVQ |
| CT-064 | POSITION SIZE FORMULA | C17 | C17-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-065 | RISK PER TRADE AS SPECTRUM (EV + FREQUENCY) | C17 | C17-E02 | CryptoCred | XeQV2ECtZVQ |
| CT-066 | DYNAMIC RISK/REWARD (EVOLVING R) | C14 | C14-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-067 | BEGINNERS — CONSERVATIVE TARGETS + SET AND FORGET | C18 | C18-E03 | CryptoCred | XeQV2ECtZVQ |
| CT-068 | STREAKS — SETUP-SPECIFIC, NOT GLOBAL | C18 | C18-E04 | CryptoCred | XeQV2ECtZVQ |
| CT-069 | BREAK-EVEN STOPS ARE PSYCHOLOGICAL COPE | C15 | C15-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-070 | PROCESS OVER P&L IN MANAGEMENT | C18 | C18-E01 | CryptoCred | XeQV2ECtZVQ |
| CT-071 | LEVERAGE = COLLATERALIZATION, NOT P&L | C17 | C17-E03 | CryptoCred | XeQV2ECtZVQ |
| CT-072 | CRYPTO CORRELATIONS — DOWNSIDE STACKING | C17 | C17-E04 | CryptoCred | XeQV2ECtZVQ |
| CT-073 | FTA DEFINITION | C13 | C13-E02 | CryptoCred | Yp0k8HD5xro |
| CT-074 | FTA FOR PROFIT-TAKING — SAME TIMEFRAME AS TRADE IDEA | C13 | C13-E03 | CryptoCred | Yp0k8HD5xro |
| CT-075 | FTA FOR TRADE MANAGEMENT — ONE TIMEFRAME LOWER | C12 | C12-E02 | CryptoCred | Yp0k8HD5xro |
| CT-076 | TWO FTAS AT WORK — PROFIT FTA + MANAGEMENT FTA | C13 | C13-E04 | CryptoCred | Yp0k8HD5xro |
| CT-077 | FAILURE TO BREAK FTA = EVIDENCE OF WEAKNESS | C19 | C19-E01 | CryptoCred | Yp0k8HD5xro |
| CT-078 | SUCCESS IN BREAKING FTA = EVIDENCE IDEA IS CORRECT | C19 | C19-E02 | CryptoCred | Yp0k8HD5xro |
| CT-079 | FTA FOR TRADE ENTRY — BREAK OF FTA AS TRIGGER | C19 | C19-E03 | CryptoCred | Yp0k8HD5xro |
| CT-080 | FTA ENTRY — PROXIMITY MATTERS | C11 | C11-E03 | CryptoCred | Yp0k8HD5xro |
| CT-081 | DON'T EXPECT MUSHROOM CLOUDS FROM LOW TF LEVELS | C11 | C11-E04 | CryptoCred | Yp0k8HD5xro |
| CT-082 | FIRST TEST BEST TEST — STOMACH THE RETEST | C06 | C06-E02 | CryptoCred | Yp0k8HD5xro |
| CT-083 | SWING TRADE GRAVEYARD — BREAK-EVEN ON FIRST REACTION | C15 | C15-E01 | CryptoCred | Yp0k8HD5xro |
| CT-084 | TIMEFRAMES NOT MUTUALLY EXCLUSIVE — DEFER TO HIGHEST | C09 | C09-E04 | CryptoCred | Yp0k8HD5xro |
| CT-085 | FTA DOES NOT PREVENT SWING TRADING — IT ENABLES IT | C13 | C13-E05 | CryptoCred | Yp0k8HD5xro |

## CONSOLIDATION COMPLETENESS CHECK

| Check | Result |
|-------|--------|
| All 85 CT IDs cataloged | ✓ YES |
| Every CT ID maps to exactly one consolidated entry | ✓ YES |
| All 7 extract files represented | ✓ YES |
| Both analysts represented | ✓ YES |
| Deduplication documented | ✓ YES |
| Conflicts flagged (not resolved) | ✓ YES — 5 conflicts |
| No engine tags added | ✓ YES |
| No comparison to compiled_engine.md | ✓ YES |

---

# END
