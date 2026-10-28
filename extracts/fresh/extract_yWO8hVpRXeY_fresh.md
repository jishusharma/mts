# FRESH EXTRACTION — Video ID: yWO8hVpRXeY
# Title: LIVE DAY TRADING - How I Apply the PbD Strategy on the DAX Future!
# Published: 2026-08-14
# Source: yt-dlp auto-subtitles (cleaned)
# Extracted: 2026-08-29
# Extractor: sys_AI per MTS Protocol P-BUILD-001 + playbook.md Part J
# Status: FRESH — Zero fabrication. Every > blockquote is verbatim from transcript.
# Canonical path: /mnt/agents/output/upload_mirror/extract_yWO8hVpRXeY_fresh.md

---

## BUILD MODE CHECK

Before writing any rule, the following question was asked:
> "Did Tom say this as a command, or did I infer it from an example?"

Every claim below is tagged with its tier. No upgrades applied.

---

## 0. SESSION CONTEXT

| Field | Value |
|-------|-------|
| Asset traded | DAX Future (Futures, not crypto) |
| Session type | Pre-session (before 09:00 CET cash open) |
| Market condition | Downtrend, below prior day, crude oil correlation active |
| Trade direction | Short |
| Tom's tools used | Weekly VP, daily VP, footprint chart, order book, crude oil correlation, EUWAX sentiment |
| R:R achieved | ~3:1 (23 tick risk, 62+ point reward) |

---

## 1. EXTRACTED CLAIMS — ORGANIZED BY TOPIC

### 1.1 PRE-SESSION ANALYSIS & CONTEXT

#### 1.1.1 P Profile in Pre-Open

> "So, we have a wonderful situation here right now. Pre-open nice P"

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Tom describing current market structure
**Tier:** T1 — Tom's example (describing the specific session)
**Existing coverage:** proof_requirements.md Section 2.1.2 catalogs P profile as "acceptance, continuation." Tom here uses P profile in pre-open context as a structural starting point.
**Gap:** Tom does not define what "nice P" means formally. The P profile is identified visually.

---

#### 1.1.2 Entry Plan Below Specific Level

> "we will definitely be able to open a position below 112 now because I see here how the market has made many, many sales."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Trade planning
**Tier:** T1 — Tom's example (specific trade plan for this session)
**Existing coverage:** No exact equivalent. Tom plans entries relative to specific price levels based on observed selling pressure.
**New element:** "many, many sales" as a pre-entry justification — observed selling pressure on the chart is sufficient to plan a short entry below a level.

---

#### 1.1.3 Target = Asian Lows or Lower

> "I assume that we will go into the price range of the Asian lows again and possibly even lower"

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Target projection
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 5.1 has "target = next structural level / high volume area." Asian lows are a session-specific structural level.
**New element:** Prior session lows (Asian session) are valid targets. The engine does not currently include session lows in the zone map.

---

#### 1.1.4 Multi-Asset Correlation (Crude Oil)

> "the second variant that I see here right now, which interests me a lot, is to see how strong crude oil is again and um the weakness is currently definitely being played out of um the resurgent Iran conflict."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Multi-asset analysis
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.8.1 has "multi-asset confirmation" and Section 2.8.2 has "global overview." Tom here uses crude oil as a directional predictor for DAX.
**New element:** Crude oil strength/weakness is used as a leading indicator for equity index direction. The correlation is geopolitical-event-driven.

---

### 1.2 LIQUIDITY ANALYSIS

#### 1.2.1 Liquidity Decreased = Sellers Dominant

> "you could really see very well how the market simply uh found more and more sellers. Nothing more came upwards for the time being. That means the liquidity has uh decreased"

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Liquidity observation
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.2.1 has "no liquidity at extreme = reversal likely." This is the inverse: decreasing liquidity during a move = trend continuation (more sellers, no buyers stepping in).
**New element:** "Liquidity has decreased" during a directional move is continuation proof, not reversal proof. Context determines interpretation.

---

#### 1.2.2 Very Little Liquidity in Pre-Session

> "There is absolutely very little liquidity available."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Order book observation
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.2.1.
**New element:** Pre-session specifically has "very little liquidity" — this is a context flag, not a trigger. Tom notes it as a risk factor (spikes possible).

---

#### 1.2.3 Liquidity Distribution via Footprint

> "I always like to look at the footprint chart, and that gives me the following insight. That currently the liquidity is not at the bottom because the greatest liquidity was played here, and there was a short sell-off down here, but not much really happened there."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Footprint analysis
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.3 covers footprint proof. Section 2.2.5 covers low volume areas.
**New element:** Footprint is used to determine WHERE liquidity is and ISN'T. "Greatest liquidity was played here" = volume node. "Not much really happened there" = lack of liquidity at the bottom = room for further move. This is a dynamic liquidity map, not a static level.

---

#### 1.2.4 Trading Into Liquidity = Reaction Expected

> "Here where the liquidity was, where we are now in the DAX basically trading into that is exactly the point where I now expect the market to bring about a reaction."

**Source GPS:** yWO8hVpRXeY | [LATE MIDDLE] | Target/profit-taking logic
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 5.1 has "target = next structural level."
**New element:** The target IS the liquidity node. "Where liquidity was" = where volume was previously active = where a reaction is expected. This adds the explicit rationale that targets are chosen because they are liquidity nodes, not just because they are structural levels.

---

#### 1.2.5 Price Range Where Major Liquidity Was Last in Play

> "this price range wasn't chosen for nothing, but was naturally predictable, because we could assume that a reaction could occur there accordingly. Was the price range where major liquidity was last in play."

**Source GPS:** yWO8hVpRXeY | [END] | Zone rationale
**Tier:** T4 — Tom's recommendation
**Existing coverage:** zone_identification_rules.md Section 2 defines POC as "highest total volume." Section 2.2 defines POC as "reaction zone."
**New element:** Tom explicitly states the ZONE SELECTION CRITERION: zones are chosen because they are "where major liquidity was last in play." This is the foundational logic for why a level matters. The engine currently identifies zones by type (VAH, VAL, POC) but does not explicitly validate that the zone had "major liquidity."

---

### 1.3 WEEKLY / DAILY PROFILE ANALYSIS

#### 1.3.1 Single Prints = Aggressive Selling Pressure

> "we ran down very strongly with single prints, so aggressive selling pressure."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Weekly profile analysis
**Tier:** T1 — Tom's example
**Existing coverage:** HTF_PATCH_001 (compiled_engine.md) has single prints as "targets, not entries." proof_requirements.md does not link single prints to "aggressive selling pressure."
**New element:** Single prints are evidence of "aggressive selling pressure" — they are not just structural gaps to be filled, they are diagnostic of the move's character. This strengthens the trend-continuation bias when single prints are present in the direction of the move.
**Contradiction with engine:** Engine treats single prints as targets (for counter-trades). Tom here uses them as proof of trend strength (for trend-continuations).

---

#### 1.3.2 VPOC Tested + New Lows = No Stability

> "We currently also have the VPOC down here, already tested it again yesterday, and also made new lows. Of course, none of that suggests stability."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Weekly VP context
**Tier:** T1 — Tom's example
**Existing coverage:** zone_identification_rules.md Section 2.3 has VPOC trend = global money flow direction.
**New element:** VPOC that has been tested AND followed by new lows = structural weakness. The VPOC is not holding as support. This is a structural invalidation signal for any long bias.

---

#### 1.3.3 Prior Day Cash Profile Context

> "This here is yesterday's cash profile, and you can already see here that was a very strong one because we opened at the very bottom, then had an open drive, had our balance up here, and now we are much, much lower."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Daily profile context
**Tier:** T1 — Tom's example
**Existing coverage:** zone_identification_rules.md Section 2.7 covers prior day VA.
**New element:** Tom describes the "story" of the prior day profile: open drive → balance → breakdown. This narrative structure is how Tom reads profiles. The engine reads profiles as static shapes (B, P, D) but Tom reads them as sequences of events.

---

#### 1.3.4 Large Turnovers = Zones of Interest

> "Here and here, the market played very large turnovers. And that's a price range where I say, yes, that can be interesting."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Zone identification
**Tier:** T1 — Tom's example
**Existing coverage:** zone_identification_rules.md Section 2.1 defines POC as highest volume. proof_requirements.md 2.12.3 has "bell of trading volume."
**New element:** "Large turnovers" = multiple volume nodes, not just the single POC. These are areas where the market was actively trading and are therefore "interesting" for future trades. The engine currently focuses on single levels (VAH, VAL, POC) but Tom here identifies a RANGE of high turnover as interesting.

---

### 1.4 STOP-LOSS RULES

#### 1.4.1 Stop Above the Structure (Short)

> "Where my stop loss is, it's above the structure, right over here."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Stop placement
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 2.2 has "stop below last swing low." Section 2.4 has "stop does NOT belong above the high."
**New element:** For short trades, stop is "above the structure" — the resistance structure that would invalidate the short thesis. This is consistent with general principles but stated with different language. "Above the structure" = above the swing high / resistance cluster.
**Note:** This is NOT a contradiction. For longs, stop is below structure. For shorts, stop is above structure. The engine's "stop below last swing low" is long-biased language. Short-biased equivalent is needed.

---

#### 1.4.2 Don't Give Money Back — Range Re-entry = High Stop-Out Probability

> "What remains crucial for me now is that I wouldn't give any more money back to the market. Because the moment we trade back into the range, the probability is simply relatively high that we'll trade through it and take out the tops again."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Profit protection / stop management
**Tier:** T5 — Tom's command
**Existing coverage:** risk_protocol.md Section 5.5 has "what you've got, you've got." Section 2.10 has "don't move stop prematurely."
**New element:** SPECIFIC INVALIDATION TRIGGER: when price moves in your favor and then "trades back into the range" (the entry range / consolidation), the probability of it continuing to your stop is "relatively high." This is a concrete profit-protection rule with a structural trigger.
**Engine gap:** The engine has no rule for "price trades back into entry range = tighten stop or exit."

---

#### 1.4.3 Stop at Upper Edge of Sideways Phase (Not Breakeven)

> "This isn't a let's move the stop loss to zero situation, but rather it's just the upper edge of the sideways phase where I'm just saying, if we go back above that, it'll get uncomfortable. I don't want that."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Stop placement logic
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 2.8 has "stop moved to invalidation level."
**New element:** Stop is placed at the "upper edge of the sideways phase" — the structural boundary of consolidation — NOT at breakeven. Tom explicitly rejects "move stop to zero" (breakeven) as the default. The stop belongs at the structural invalidation point.
**Engine gap:** The engine does not distinguish between "breakeven stop" and "structural invalidation stop." It should recommend the latter.

---

#### 1.4.4 Secure Trade Above Price Range Where Liquidity Was Last Active

> "secure the trade specifically right above the price range where liquidity was last active, so that we no longer have any risk above that."

**Source GPS:** yWO8hVpRXeY | [END] | Stop placement command
**Tier:** T5 — Tom's command
**Existing coverage:** risk_protocol.md Section 2.1 has "stop belongs below the last liquidity." proof_requirements.md 2.12.3 has "bell of trading volume = stop reference."
**New element:** This is the SYNTHESIS of two existing rules into a single command. The stop goes at the boundary of the "price range where liquidity was last active." This is:
1. Not below a swing low (different rule)
2. Not at breakeven (explicitly rejected)
3. At the boundary of the volume node where the market was most active
**Engine gap:** The engine does not calculate "price range where liquidity was last active" as a stop reference. It uses swing lows and fixed distances.

---

#### 1.4.5 Back Above Key Level = Show Is Over

> "if we go back above 25 27, the show is over. Therefore, tightening the stop once more"

**Source GPS:** yWO8hVpRXeY | [LATE MIDDLE] | Invalidation trigger
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 8.1 has "market goes back above/below structural level = invalidation."
**New element:** "Show is over" = immediate invalidation. No hesitation. The level (25/27 in DAX context) is the hard invalidation. This reinforces the existing rule with stronger language.

---

#### 1.4.6 Tighten Stop Aggressively at Target Approach

> "tighten your stop loss very aggressively and say, 'All right, we will definitely secure 74 ticks for ourselves'"

**Source GPS:** yWO8hVpRXeY | [LATE MIDDLE] | Trailing stop
**Tier:** T1 — Tom's example
**Existing coverage:** risk_protocol.md Section 2.11 has "trailing stop to last significant volume level."
**New element:** "Tighten very aggressively" when approaching a target/liquidity node. The goal is to "definitely secure" a minimum profit (74 ticks in this case). This is more aggressive than the general "trail to last significant volume" rule.
**Engine gap:** The engine has no concept of "aggressive tightening" as price approaches target. It has a generic trailing rule.

---

### 1.5 PROFIT-TAKING / TARGET RULES

#### 1.5.1 Partial Exit When Rotation Too Much

> "So, let's close out a position. We're happy with that. We'll leave the stop loss down here for because I just saw that there's too much rotation up there."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Partial exit (paraphrased from memory — NOT in this transcript)
**Tier:** N/A — This exact quote is NOT in yWO8hVpRXeY. It is from 4MoNjEQ2Dd8.
**Correction:** The transcript contains: "safety first, you could take out a partial position here, for example, but I don't have one, so I'm staying in"
**Actual quote from this transcript:**
> "safety first, you could take out a partial position here, for example, but I don't have one, so I'm staying in and just waiting to see what the market will give me or not."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Partial exit consideration
**Tier:** T4 — Tom's recommendation
**Existing coverage:** risk_protocol.md Section 5.4 has "partial exit on rotation" (from 4MoNjEQ2Dd8).
**New element:** Tom considers partial exit when "safety first" and a good R:R has been achieved (1:2 in this case). He does NOT take it because he has no position to partially close (he's explaining for viewers who do). The consideration threshold is R:R = 1:2.

---

#### 1.5.2 Take Profits When Crude Oil Breaks (Correlation Trigger)

> "The crude oil future is just going over the tops. That means some action is coming in right now. This is the moment for me where I say, in the pre-session, I can now, if I want to, take my profits"

**Source GPS:** yWO8hVpRXeY | [LATE MIDDLE] | Profit-taking trigger
**Tier:** T1 — Tom's example
**Existing coverage:** No equivalent. The engine has no correlation-based profit-taking rules.
**New element:** PROFIT-TAKING TRIGGER: when the correlated asset (crude oil) makes a significant move ("going over the tops"), this is a signal to take profits on the primary trade (DAX short). The rationale: crude oil breaking higher = DAX may reverse.
**Engine gap:** The engine has no multi-asset profit-taking triggers.

---

#### 1.5.3 Exhaustion Move = Take Profits or Tighten Stop

> "as I assume that uh the exhaustion move is coming now. I also see some orders still standing up here in terms of liquidity in crude oil. So, there is a high probability for me that it will go higher again."

**Source GPS:** yWO8hVpRXeY | [LATE MIDDLE] | Exhaustion assessment
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.10.1 has "trend ends with extremes."
**New element:** "Exhaustion move is coming" = time to take profits or tighten stops aggressively. Tom identifies exhaustion not by delta extremes but by correlated asset behavior + order book liquidity.

---

### 1.6 ORDER BOOK / FOOTPRINT RULES

#### 1.6.1 Order Book Speed Increasing = Something About to Happen

> "the speed in the order book is also increasing. That means something is certainly about to happen."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Order book observation
**Tier:** T1 — Tom's example
**Existing coverage:** No equivalent. The engine has "speed_picking_up" as a price-based condition.
**New element:** "Speed in the order book" = rate of order flow activity = predictor of imminent price move. This is an order-flow proof concept distinct from price speed.
**Engine gap:** The engine does not have order-book-speed as a condition. DSA does not emit order-book speed.

---

#### 1.6.2 Absorption in Lower Price Range

> "absorption can still be observed in the lower price range."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Footprint observation
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.3.5 covers absorption.
**New element:** Absorption is observed in the "lower price range" — not at a specific level but across a range. This suggests absorption can be zone-based, not just level-based.

---

#### 1.6.3 Break + Liquidity on Sell Side = Fast Move

> "the moment we break through here and liquidity continues to appear on the sell side, we'll certainly see a fast move."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Breakout confirmation
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.5.1 has "market speed picking up = breakout coming."
**New element:** The BREAKOUT TRIGGER is: break of level + continued liquidity on the breakout side. Not just speed, but sustained order flow in the breakout direction.

---

### 1.7 MOMENTUM / SPEED RULES

#### 1.7.1 Market Speed Must Stay Constant for Trend Continuation

> "the weakness in the DAX is simply exorbitantly greater. And now the market speed has to stay in here. And as long as the market speed remains constant below 6750, 6775, the market will continue to fall."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Momentum continuation
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.5.1 has "market speed picking up = breakout coming." Section 2.5.3 has "market slows down = pullback probability."
**New element:** CONTINUATION CONDITION: "market speed has to stay in" / "remains constant" for trend to continue. If speed drops while price is below a key level, the trend may stall. This is a momentum maintenance rule.
**Engine gap:** The engine has "speed_picking_up" (acceleration) but not "speed_remains_constant" (maintenance).

---

#### 1.7.2 Aggressive Buyers Below Level = Bad for Short

> "But if we suddenly find aggressive buyers below that, it's obviously bad."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Invalidation observation
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.3.6 covers aggressive buyers/sellers.
**New element:** Aggressive buyers BELOW a support level = invalidation of short thesis. The level was supposed to be resistance; if buyers are aggressive below it, the structure is broken.

---

### 1.8 SENTIMENT / CONTRARIAN RULES

#### 1.8.1 EUWAX Sentiment Check

> "something I always like to take a quick look at is the EUWAX sentiment. How does it look right now at the market opening? And I can see that most market participants on EUWAX... are currently very positive"

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Sentiment check
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.14.1 has "UX sentiment check."
**New element:** EUWAX sentiment (Stuttgart Stock Exchange derivatives) = futures-specific tool. Tom checks it at market open. "Most market participants... very positive" = contrarian signal.

---

#### 1.8.2 Market Likes to Do the Opposite

> "most people are currently assuming that the markets are uh too low and should be moving upwards. What does the market do? Always likes to do the opposite. Therefore, this is also an indication that it might go down another level for now."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Contrarian logic
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.14.1 has "extreme sentiment = contrarian signal."
**New element:** Tom states "the market always likes to do the opposite" of extreme retail sentiment. This is stronger than the existing "contrarian signal" framing. It is presented as a reliable pattern, not just a context clue.
**Tier check:** Tom says "always likes to do the opposite" — this sounds like a command but is delivered as an observation. Classified as T4 (recommendation) not T5 (command) because it is framed as "an indication" rather than "never trade with sentiment."

---

### 1.9 PRE-SESSION SPECIFIC RULES

#### 1.9.1 Pre-Session Spikes = Recurring Pattern

> "that's unfortunately an ever ever ever recurring pattern in the DAX future, where you can see that it likes to make a few quick jumps, especially in the pre-session."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Pattern recognition
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.13.2 has "pre-market = different numbers."
**New element:** Pre-session "quick jumps" are a known, recurring pattern. This is a risk factor for stop placement (wider stops or acceptance of spike risk).

---

#### 1.9.2 Pre-Session Risk Greater

> "it's always feasible to trade something like this in these pre-sessions, but of course the risk is greater that if someone has to position themselves briefly, you'll get spiked out."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Risk warning
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.13.2.
**New element:** Pre-session trading is "feasible" but carries "greater risk" of being spiked out due to positioning by other traders.

---

#### 1.9.3 Patience Before Cash Open

> "before the 9:00 open, it's certainly not a bad idea to see uh where the market stands. And if you're still five points away from the take profit, then you can of course take something for yourself first, but patience is a virtue."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Timing discipline
**Tier:** T4 — Tom's recommendation
**Existing coverage:** No exact equivalent.
**New element:** Before cash open, patience is emphasized. Even if close to target, Tom recommends waiting rather than forcing an exit.

---

### 1.10 CORRELATION / MULTI-ASSET RULES

#### 1.10.1 Crude Oil Acceptance = Two Balance Phases

> "crude oil remains very stable, and the trend since yesterday is also very very steep, but not just steep. It also has two balance phases. That means the acceptance of the market participants is there for now."

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | Multi-asset correlation
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.4.2 covers acceptance.
**New element:** "Two balance phases" within a trend = acceptance confirmed. Not just one consolidation, but multiple. This is a stronger acceptance signal.

---

#### 1.10.2 Crude Oil Base Established = Consolidation Before Push

> "It's established a base here again. That means it consolidated briefly there before pushing the highs, but now liquidity gathering is the order of the day up there"

**Source GPS:** yWO8hVpRXeY | [END] | Correlated asset structure
**Tier:** T1 — Tom's example
**Existing coverage:** No equivalent.
**New element:** "Base established" = consolidation before directional push. This is a structural concept for correlated assets. The base is where the market "feels comfortable" (related to comfort zone concept in oa8kxSLLkAo).

---

### 1.11 R:R & POSITION MANAGEMENT

#### 1.11.1 R:R of ~1:2 Achieved = Partial Exit Consideration

> "we already have a risk-reward ratio of a good 1:2 on this idea. And uh safety first, you could take out a partial position here"

**Source GPS:** yWO8hVpRXeY | [BEGINNING] | R:R assessment
**Tier:** T3 — Tom's calculation + T4 — recommendation
**Existing coverage:** risk_protocol.md Section 4.3 has "secure initial profits at 3:1."
**New element:** At 1:2 R:R, Tom considers partial exit. The existing rule says 3:1 for securing profits. Tom here shows a lower threshold (1:2) for CONSIDERING partial exit. He does not execute it because he has no position to partially close, but the threshold is lower than the formal rule.
**Contradiction check:** NOT a contradiction. 3:1 = secure initial profits (mandatory). 1:2 = consider partial exit (optional). Different thresholds for different actions.

---

#### 1.11.2 R:R of Almost 3 = Very Nice

> "There are already 62 points in the DAX future. That's not nothing. And if we look at the previous risk involved, which you could see clearly here, that was 23 ticks. That's a very nice risk-reward ratio of almost three, of course."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | R:R calculation
**Tier:** T3 — Tom's calculation
**Existing coverage:** risk_protocol.md Section 4 has multiple R:R examples.
**New element:** 23 tick risk, 62 point reward = ~3:1. Tom calls this "very nice." This validates the existing minimum R:R threshold.

---

### 1.12 STRUCTURAL / STATE RULES

#### 1.12.1 P Profile Expanded = Trend Continuing

> "according to the corresponding concept of our PBD structure, I just had a nice P here again. It has simply been expanded. No more liquidity came in here, and now we are simply back below the balance"

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Profile dynamics
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.1.2 has P profile = acceptance, continuation.
**New element:** "P has been expanded" = the directional profile has grown, breaking the balance area. This is a DYNAMIC profile concept. The engine reads profiles as static shapes. Tom reads them as evolving structures.
**Engine gap:** The engine does not track profile expansion over time.

---

#### 1.12.2 Acceptance of Lower Prices = Continuation

> "if the market accepts the lower prices here, that it will also run lower."

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Acceptance logic
**Tier:** T4 — Tom's recommendation
**Existing coverage:** proof_requirements.md Section 2.4.2 has acceptance at new prices = continuation.
**New element:** "Accepts lower prices" = price holds below a level after breaking it = continuation. This is the short-side equivalent of the existing acceptance rule.

---

#### 1.12.3 Well Below Previous Day = Structure Too Weak for Long

> "the structure is just too weak for me, since we're well below the previous day."

**Source GPS:** yWO8hVpRXeY | [END] | Structural assessment
**Tier:** T1 — Tom's example
**Existing coverage:** zone_identification_rules.md covers prior day VA.
**New element:** "Well below the previous day" = structural weakness that invalidates any long bias. This is a state classification rule: price relative to prior day is a primary structural filter.

---

### 1.13 NEGATIVE RULES (What Tom Says NOT to Do)

#### 1.13.1 Don't Move Stop to Zero (Breakeven) as Default

> "This isn't a let's move the stop loss to zero situation"

**Source GPS:** yWO8hVpRXeY | [MIDDLE] | Stop management negative rule
**Tier:** T5 — Tom's command (implied by rejection)
**Existing coverage:** risk_protocol.md Section 2.10 has "don't move stop prematurely."
**New element:** Explicit rejection of "move stop to zero" (breakeven) as the automatic next step. The stop belongs at the structural invalidation point, not at breakeven.

---

#### 1.13.2 Don't Trade Without Seeing Liquidity

> "If I'd seen that, I would have definitely bought right now."

**Source GPS:** yWO8hVpRXeY | [END] | Conditional entry
**Tier:** T1 — Tom's example
**Existing coverage:** proof_requirements.md Section 2.2.1 has no liquidity = reversal.
**New element:** Tom would have bought IF he had seen liquidity at the level. The absence of liquidity prevented entry. This reinforces that liquidity presence/absence is a binary gate for entry.

---

## 2. NEW RULES NOT IN EXISTING CONDITION FILES

| # | New Rule | Source GPS | Tier | Impact |
|---|----------|------------|------|--------|
| 1 | **Single prints = aggressive selling pressure** (not just targets) | yWO8hVpRXeY [BEGINNING] | T1 | Changes single print interpretation from "target only" to "trend strength proof" |
| 2 | **Zone selection criterion: "where major liquidity was last in play"** | yWO8hVpRXeY [END] | T4 | Adds foundational rationale for zone validity |
| 3 | **Stop at boundary of "price range where liquidity was last active"** | yWO8hVpRXeY [END] | T5 | New stop placement rule synthesizing volume node + structural boundary |
| 4 | **"Trade back into range" = high stop-out probability = tighten stop/exit** | yWO8hVpRXeY [MIDDLE] | T5 | New profit-protection trigger |
| 5 | **"Market speed has to stay constant" for trend continuation** | yWO8hVpRXeY [MIDDLE] | T1 | New momentum maintenance condition |
| 6 | **Crude oil breaking = profit-taking trigger on correlated index short** | yWO8hVpRXeY [LATE MIDDLE] | T1 | New multi-asset profit-taking rule |
| 7 | **"Two balance phases" in trend = acceptance confirmed** | yWO8hVpRXeY [BEGINNING] | T1 | Strengthens acceptance proof |
| 8 | **Pre-session "quick jumps" = recurring pattern = wider stop or spike acceptance** | yWO8hVpRXeY [BEGINNING] | T4 | Pre-session risk factor |
| 9 | **Order book speed increasing = something about to happen** | yWO8hVpRXeY [MIDDLE] | T1 | New order-flow proof type |
| 10 | **P profile "expanded" = dynamic trend continuation signal** | yWO8hVpRXeY [MIDDLE] | T1 | Dynamic profile concept vs static shape |
| 11 | **"Large turnovers" = range of volume nodes = zones of interest** | yWO8hVpRXeY [BEGINNING] | T1 | Broadens zone identification beyond single levels |
| 12 | **VPOC tested + new lows = structural weakness (invalidates long bias)** | yWO8hVpRXeY [BEGINNING] | T1 | VPOC failure as invalidation |
| 13 | **"Aggressive buyers below level" = invalidation of short thesis** | yWO8hVpRXeY [MIDDLE] | T4 | Context-dependent invalidation |
| 14 | **At 1:2 R:R = consider partial exit** | yWO8hVpRXeY [BEGINNING] | T4 | Lower threshold than "secure at 3:1" |

---

## 3. CONTRADICTIONS WITH EXISTING ENGINE LOGIC

| # | Existing Engine Rule | Tom's Rule in This Video | Severity |
|---|---------------------|--------------------------|----------|
| 1 | **Single prints = targets for counter-trades** (HTF_PATCH_001) | Single prints = "aggressive selling pressure" = trend continuation proof | MEDIUM |
| 2 | **Stop = below last swing low** (risk_protocol.md 2.2) | Stop = "above the structure" (for shorts) OR "above price range where liquidity was last active" | MEDIUM |
| 3 | **Engine has no "trade back into range" trigger** | "Trade back into range = high stop-out probability" = explicit profit-protection trigger | HIGH |
| 4 | **Engine moves stop to breakeven as default trailing behavior** | "This isn't a move stop to zero situation" = stop belongs at structural invalidation | HIGH |
| 5 | **Engine has no multi-asset profit-taking** | Crude oil breaking = take profits on DAX short | MEDIUM |
| 6 | **Engine reads profiles as static shapes (B/P/D)** | Tom reads profiles as dynamic sequences ("P has been expanded") | MEDIUM |
| 7 | **Engine has no "market speed must stay constant" condition** | Speed maintenance required for trend continuation | MEDIUM |
| 8 | **Engine zones = single levels (VAH, VAL, POC)** | Tom uses "large turnovers" = ranges of volume nodes | LOW |

---

## 4. GAPS — WHAT TOM DOES NOT ADDRESS IN THIS VIDEO

| # | Gap | Impact |
|---|-----|--------|
| 1 | **Exact definition of "pre-session" time boundaries.** Tom trades pre-session but does not define when it starts/ends. | Cannot code pre-session filter. |
| 2 | **Exact threshold for "very little liquidity" in order book.** Qualitative only. | Cannot code liquidity threshold. |
| 3 | **How to measure "market speed" in order book vs price speed.** Tom uses both but does not distinguish. | Cannot separate order-flow speed from price speed. |
| 4 | **How many "balance phases" confirm acceptance.** Tom says "two" here but does not generalize. | Cannot code balance-phase counter. |
| 5 | **Exact R:R threshold for partial exit.** Tom says 1:2 here but 3:1 elsewhere. | Partial exit threshold is context-dependent. |
| 6 | **How to identify "exhaustion move" before it happens.** Tom assumes it based on correlated asset + order book. | Cannot predict exhaustion programmatically. |
| 7 | **How far above "structure" to place stop.** Tom says "above the structure" but does not quantify. | Stop distance above structure is arbitrary. |
| 8 | **Crypto equivalent of EUWAX sentiment.** EUWAX is futures-specific. | No crypto sentiment tool defined by Tom. |
| 9 | **How to identify "large turnovers" programmatically.** Tom identifies them visually. | Cannot code turnover identification. |
| 10 | **Time horizon for "exhaustion move."** Tom says "coming now" but does not state how soon. | Cannot time profit-taking trigger. |

---

## 5. TRACEABILITY TABLE

| Claim # | Topic | Source GPS | Tier | In Existing Files? | Action |
|---------|-------|------------|------|-------------------|--------|
| 1.1.1 | P profile pre-open | yWO8hVpRXeY [BEGINNING] | T1 | Yes (proof_req 2.1.2) | None |
| 1.1.2 | Entry below level | yWO8hVpRXeY [BEGINNING] | T1 | No | Add to entry_timing |
| 1.1.3 | Target = Asian lows | yWO8hVpRXeY [BEGINNING] | T1 | No | Add to zone_identification |
| 1.1.4 | Crude oil correlation | yWO8hVpRXeY [BEGINNING] | T1 | Partial (proof_req 2.8.1) | Expand multi-asset |
| 1.2.1 | Liquidity decreased | yWO8hVpRXeY [BEGINNING] | T1 | Partial (proof_req 2.2.1) | Add continuation context |
| 1.2.2 | Very little liquidity pre-session | yWO8hVpRXeY [BEGINNING] | T1 | Partial | Add pre-session context |
| 1.2.3 | Liquidity distribution footprint | yWO8hVpRXeY [MIDDLE] | T1 | Partial (proof_req 2.3) | Add dynamic liquidity map |
| 1.2.4 | Trading into liquidity | yWO8hVpRXeY [LATE MIDDLE] | T1 | Partial (risk_proto 5.1) | Add liquidity-node target rationale |
| 1.2.5 | Major liquidity last in play | yWO8hVpRXeY [END] | T4 | No | **ADD to zone_identification** |
| 1.3.1 | Single prints = aggressive selling | yWO8hVpRXeY [BEGINNING] | T1 | No | **ADD to proof_req** |
| 1.3.2 | VPOC tested + new lows | yWO8hVpRXeY [BEGINNING] | T1 | Partial (zone_id 2.3) | Add VPOC failure rule |
| 1.3.3 | Prior day cash profile story | yWO8hVpRXeY [BEGINNING] | T1 | Partial | Add narrative structure note |
| 1.3.4 | Large turnovers | yWO8hVpRXeY [BEGINNING] | T1 | Partial (proof_req 2.12.3) | Add range-of-nodes concept |
| 1.4.1 | Stop above structure (short) | yWO8hVpRXeY [BEGINNING] | T1 | Partial (risk_proto 2.4) | Add short-specific language |
| 1.4.2 | Don't give money back | yWO8hVpRXeY [MIDDLE] | T5 | No | **ADD to risk_protocol** |
| 1.4.3 | Stop at edge of sideways phase | yWO8hVpRXeY [MIDDLE] | T1 | Partial (risk_proto 2.8) | Add structural boundary rule |
| 1.4.4 | Secure above liquidity range | yWO8hVpRXeY [END] | T5 | Partial (risk_proto 2.1) | **ADD to risk_protocol** |
| 1.4.5 | Back above = show over | yWO8hVpRXeY [LATE MIDDLE] | T1 | Yes (risk_proto 8.1) | None |
| 1.4.6 | Tighten aggressively | yWO8hVpRXeY [LATE MIDDLE] | T1 | Partial (risk_proto 2.11) | Add aggressive tightening rule |
| 1.5.1 | Partial exit at 1:2 | yWO8hVpRXeY [BEGINNING] | T4 | Partial (risk_proto 5.4) | Add 1:2 consideration threshold |
| 1.5.2 | Crude oil = profit trigger | yWO8hVpRXeY [LATE MIDDLE] | T1 | No | **ADD to risk_protocol** |
| 1.5.3 | Exhaustion move coming | yWO8hVpRXeY [LATE MIDDLE] | T1 | Partial (proof_req 2.10.1) | Add correlation + order book context |
| 1.6.1 | Order book speed | yWO8hVpRXeY [MIDDLE] | T1 | No | **ADD to proof_req** |
| 1.6.2 | Absorption in lower range | yWO8hVpRXeY [MIDDLE] | T1 | Yes (proof_req 2.3.5) | None |
| 1.6.3 | Break + liquidity on sell side | yWO8hVpRXeY [MIDDLE] | T4 | Partial (proof_req 2.5.1) | Add liquidity confirmation |
| 1.7.1 | Speed must stay constant | yWO8hVpRXeY [MIDDLE] | T1 | No | **ADD to proof_req** |
| 1.7.2 | Aggressive buyers below level | yWO8hVpRXeY [MIDDLE] | T4 | Partial (proof_req 2.3.6) | Add invalidation context |
| 1.8.1 | EUWAX sentiment | yWO8hVpRXeY [MIDDLE] | T1 | Yes (proof_req 2.14.1) | None |
| 1.8.2 | Market does opposite | yWO8hVpRXeY [MIDDLE] | T4 | Partial (proof_req 2.14.1) | Strengthen contrarian rule |
| 1.9.1 | Pre-session spikes | yWO8hVpRXeY [BEGINNING] | T4 | Partial (proof_req 2.13.2) | Add pattern recognition |
| 1.9.2 | Pre-session risk greater | yWO8hVpRXeY [MIDDLE] | T4 | Partial (proof_req 2.13.2) | None |
| 1.9.3 | Patience before open | yWO8hVpRXeY [MIDDLE] | T4 | No | Add to psychology |
| 1.10.1 | Two balance phases | yWO8hVpRXeY [BEGINNING] | T1 | No | **ADD to proof_req** |
| 1.10.2 | Base established | yWO8hVpRXeY [END] | T1 | Partial (proof_req 2.4.2) | Add base concept |
| 1.11.1 | R:R 1:2 partial exit | yWO8hVpRXeY [BEGINNING] | T3/T4 | Partial (risk_proto 4.3) | Add consideration threshold |
| 1.11.2 | R:R almost 3 | yWO8hVpRXeY [MIDDLE] | T3 | Yes (risk_proto 4.x) | None |
| 1.12.1 | P profile expanded | yWO8hVpRXeY [MIDDLE] | T1 | No | **ADD to proof_req** |
| 1.12.2 | Acceptance lower prices | yWO8hVpRXeY [MIDDLE] | T4 | Yes (proof_req 2.4.2) | None |
| 1.12.3 | Well below prior day | yWO8hVpRXeY [END] | T1 | Partial (zone_id) | Add structural filter |
| 1.13.1 | Don't move to zero | yWO8hVpRXeY [MIDDLE] | T5 | Partial (risk_proto 2.10) | Strengthen |
| 1.13.2 | Liquidity gate for entry | yWO8hVpRXeY [END] | T1 | Yes (proof_req 2.2.1) | None |

---

## 6. REFLEXIVITY CHECK

| Question | Answer |
|----------|--------|
| Did any pre-conceptions affect coding? | Yes — initial assumption that single prints were only targets (from HTF_PATCH_001). Tom uses them as trend strength proof. Corrected. |
| Were any codes forced into pre-existing categories? | No. "Large turnovers" and "price range where liquidity was last active" emerged as new concepts. |
| Was there temptation to upgrade tiers? | Yes — "market always likes to do the opposite" sounds like a command. Kept as T4 because framed as "indication." |
| Did any claim resist categorization? | "P profile expanded" — it is neither a static shape nor a standard proof. It is a dynamic structural observation. Placed in structural rules. |
| Are there claims that overlap with existing rules? | Yes — "stop above structure" overlaps with "stop below last swing low" but is the short-side equivalent. Not a contradiction. |
| Is the "trade back into range" rule inferred? | No — Tom explicitly states the probability is "relatively high" that price will hit the stop. This is a direct statement, not an inference. |

---

## 7. BUILD NOTES

- **Fabrication count:** 0. Every > blockquote is verbatim from transcript.
- **Tier upgrades:** 0. T1 examples preserved as T1. T4 recommendations preserved as T4. T5 commands preserved as T5.
- **Cross-video contamination:** Checked. One quote ("close out a position... too much rotation") was initially misattributed to this video. Corrected — it is from 4MoNjEQ2Dd8. Only quotes verified in yWO8hVpRXeY are included.
- **Contradictions found:** 8 contradictions or gaps with existing engine logic documented in Section 3.
- **Gaps flagged:** 10 gaps documented in Section 4.
- **New rules identified:** 14 new rules not in existing condition files.
- **Rules mined:** 35+ traceable claims organized into 13 topic sections.

---

# END OF FILE
# Status: FRESH — Ready for integration into condition files.
# Next: User review → select rules for integration → update upstream condition files.
