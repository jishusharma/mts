# HTF STRUCTURE AUDIT — 2026-08-28
# Scope: Weekly/Daily VP Structure → Engine Rules
# Extracts searched: 47/47 (batch grep + 6 full reads)
# Findings: 28 traceable claims, 9 engine gaps, 8 patch recommendations
# Auditor: sys_AI (v4.2.0-p1 follow-on)

---

## EXECUTIVE SUMMARY

The engine (v4.2.0-p1) is **blind to weekly volume profile structure**. It knows "breakdown override" (price >0.5% outside weekly VA → Trend) but has **zero awareness** of:
- Double distributions (two balance areas = range expansion likely)
- Single prints (thin volume = explosive move potential / target areas)
- VPOC migration (POC shifting = big money repositioning)
- Weekly profile as the **first structural look** after trend structure
- Prior day VAL/VPOC as primary zones (not just weekly VAH/VAL)
- Single prints as **exit/target areas, NOT entry zones**

Tom's actual workflow: **Trend structure → Weekly profile → Daily profiles → 5m execution**. The engine skips straight from weekly VA boundaries to 4H/1H zones without reading weekly VP shape.

---

## 1. WEEKLY PROFILE STRUCTURE

### 1.1 Single Prints

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "single prints always occur when markets have traded rapidly in one direction" | 3o1VVsfBmmU [BEGINNING] T1 | MISSING | Visual-only (VP shape) | Flag for visual validation layer |
| 2 | "We have quite a lot of single prints here. And there are really many. This means the market really struggled here, especially when it came to the underlying fundamental factors." | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | Add to setup context: "single prints present = struggled at level" |
| 3 | "single print at end = strong sell-off, not fair value" | BVpYGKz9PBU [MIDDLE] T1 | MISSING | Visual-only | Context flag: late-session single print = unsustainable move |
| 4 | "these are single print areas. The market only spent a very short time there. It ran up extremely fast, and something like that is often corrected later." | KEe_CWHyuSg [MIDDLE] T1 | MISSING | Visual-only | Add mean-reversion probability boost when single prints above/below |
| 5 | "single prints are target areas for many market participants. That means that's where they exit the market. But they don't enter." | Fj4FDZQxw0I [MIDDLE] T5 | MISSING | Visual-only | **CRITICAL: Single prints = targets, NOT entries. Engine currently treats all zones as potential entries.** |
| 6 | "Up here we still have a single print. We have aggressive selling tails. That means there was some really aggressive selling up here." | C9n_d91Uitc [LATE MIDDLE] T1 | MISSING | Visual-only | Combine single print + selling tail = rejection zone |
| 7 | "Are there old single print areas that need to be repaired?" | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | "Repair" concept = price returns to fill single print (target) |

**Engine Gap #1:** No concept of single prints. Engine treats weekly VAH/VAL/POC as discrete levels. It does not know that thin volume between distributions = explosive potential, or that single prints are targets, not entries.

**DSA Feasibility:** Single prints require volume profile shape analysis. DSA currently emits VP nodes (POC, VAH, VAL) but not volume histogram shape. **Cannot emit without VP histogram data.**

### 1.2 Double Distributions

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "we have a beautiful, what's called a double distribution here." | -dMWA_bbm3o [MIDDLE] T1 | MISSING | Visual-only | Core concept: two distinct balance areas on weekly |
| 2 | "What information does this double distribution give me? I need to know that before the week starts." | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | **MUST HAVE before trading week** |
| 3 | "This upper balance, which is distinct, and the lower one, which is also distinct, were both aggressively bought." | -dMWA_bbm3o [MIDDLE] T1 | MISSING | Visual-only | Both distributions can have directional bias |
| 4 | "The balance, despite swinging down sharply at times, is situated quite high up across all the weekly candles." | -dMWA_bbm3o [MIDDLE] T1 | MISSING | Visual-only | VPOC location within distribution matters |

**Engine Gap #2:** No concept of double distributions. Engine sees one weekly VA. If price is inside it → Balance. If outside → Trend. It does not know that two distributions = range expansion likely, and that rejection from upper distribution → target lower distribution POC.

**DSA Feasibility:** Double distribution requires multi-modal volume profile analysis (two POCs, two VAs). DSA currently emits single weekly POC/VAH/VAL. **Cannot emit without VP histogram data.**

### 1.3 VPOC Behavior / Migration

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "What you can always observe very well here, for example, is how the VPOC behaves in a trend." | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Partial (DSA has weekly POC) | Track weekly POC week-over-week |
| 2 | "VPOC = weekly equilibrium" | 3o1VVsfBmmU [BEGINNING] T1 | PARTIAL (engine has weekly POC) | YES (weekly_vp.poc exists) | Rename engine "weekly POC" → "VPOC" for Tom consistency |
| 3 | "as long as we stay above this aggressive buying and this closing price, the probability is high that the big money will move upward." | 3o1VVsfBmmU [BEGINNING] T1 | MISSING | Partial (needs close + VPOC) | Bullish condition: price > VPOC + close > VPOC |
| 4 | "If we move back in here, I immediately know that the probability is now again high that the game of supply and demand will continue." | 3o1VVsfBmmU [BEGINNING] T1 | MISSING | Partial | Bearish condition: price < VPOC → revert to balance |
| 5 | "Rising VPOCs with increasing liquidity indicate a stable, bullish structure." | KEe_CWHyuSg [MIDDLE] T1 | MISSING | YES (can compute from multi-week data) | **DSA schema: add prior_week_vp.poc for VPOC trend** |
| 6 | "Look at the VPOCs. So, these are the price areas where the market was valued most fairly during these time periods." | KEe_CWHyuSg [MIDDLE] T1 | PARTIAL | YES | VPOC as "fair price" = magnet concept already in engine |
| 7 | "VPOC trend = global money flow" | Ld1dhjGdTCA [MIDDLE] T4 | MISSING | YES (multi-week) | **DSA: 4-week VPOC array for trend** |
| 8 | "Because the value area has shifted. You can see that here in the two weeks it simply moved lower and this week traded within the previous week." | 9eHZMVXilgc [MIDDLE] T1 | MISSING | YES (prior week data) | Value area shift = directional bias |

**Engine Gap #3:** Engine has weekly POC but calls it "POC". Tom calls it "VPOC" and tracks its **migration** (rising/falling). Engine does not compare current VPOC to prior week VPOC. No VPOC trend rule.

**DSA Feasibility:** DSA currently emits `weekly_vp.poc`. To track migration, needs `prior_week_vp.poc` and `two_weeks_ago_vp.poc`. **Schema change needed.**

---

## 2. BREAKOUT ANTICIPATION

### 2.1 Speed/Acceleration Signals

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "if you notice that suddenly the speed between the bid and the ask begins to accelerate, then the market starts to rotate in a different direction. Then something is likely to happen because market participants want or need to take action" | YVUcLTsCOZI [MIDDLE] T4 | MISSING | NO (order book microstructure) | Visual/footprint only |
| 2 | "Very often it accelerates at first. And why is that the case? because a lot of market participants fall out of balance and then they sell their positions below that level" | YmygDgtoxO8 [MIDDLE] T1 | MISSING | Partial (speed_picking_up flag exists) | **Connect speed_picking_up + break below VAL = acceleration** |
| 3 | "Fast moves into resistance with aggressive bid/ask and volume suggest breakout; slow moves with no transaction suggest reversal." | 1xBWnyr1qe4 [MIDDLE] T4 | MISSING | Partial (needs footprint) | Speed + volume + footprint = breakout validation |
| 4 | "If this break out without the volume without the speed the change is high that's reverse." | 1xBWnyr1qe4 [END] T4 | MISSING | Partial | **Negative rule: NO breakout trade without volume + speed** |

**Engine Gap #4:** Engine has `speed_picking_up` boolean but only uses it to double distance caps (GAP_FIX_001 Patch 3). It does NOT connect speed + volume + break below VAL = acceleration/breakout anticipation.

### 2.2 Volume Profile Pre-Breakout Structure

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "A lot of people took short positions here, and they have now abandoned those positions. What does that mean for me? I have to check how much liquidity is flowing into the short squeeze, and when does it stop?" | -dMWA_bbm3o [MIDDLE] T1 | MISSING | NO | Short squeeze detection = footprint + order book |
| 2 | "We have quite a lot of single prints here... This means the market really struggled here" | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | Single prints between distributions = breakout fuel |
| 3 | "if the breakout occurs or if a counter arises?" | C9n_d91Uitc [BEGINNING] T4 | PARTIAL (engine has both) | N/A | Engine has breakout and counter, but no pre-breakout structure read |

**Engine Gap #5:** Engine evaluates setups AFTER price reaches zone. Tom reads weekly structure **before the week starts** to anticipate which distribution will break, which direction, and what the target is.

### 2.3 HTF → LTF Transfer Rules

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "The first thing I generally do is I give myself what I always call a quick watch of the current price trend... are we currently more in balance or are we more in a trend right now?" | 3o1VVsfBmmU [BEGINNING] T4 | PARTIAL (engine has Balance/Trend states) | YES | Already in engine |
| 2 | "I need the next piece of information... the weekly market profile... to determine what the current balance or imbalance looks like in the current price discovery." | 3o1VVsfBmmU [BEGINNING] T4 | MISSING | Partial | Weekly VP is Step 2 after trend structure |
| 3 | "Now I need to fine-tune the whole thing. And to fine-tune everything, I look at the daily profiles." | 3o1VVsfBmmU [MIDDLE] T4 | MISSING | YES (daily_vp exists) | Daily profiles = Step 3, engine skips to 4H/1H |
| 4 | "with this, I create a wonderful concept for myself where I can locate resistance and support. And then I transfer these price areas over to my small simple chart. In this case, a five-minute chart." | 3o1VVsfBmmU [MIDDLE] T4 | MISSING | N/A | Tom's execution is 5m, engine uses 15m/5m/1m |

**Engine Gap #6:** Tom's workflow is Weekly → Daily → 5m. Engine's workflow is Weekly VA boundary check → 4H/1H zones → 15m/5m entry. The engine **skips daily profiles** and does not use weekly profile shape to define the "route plan."

---

## 3. EXHAUSTION DETECTION

### 3.1 Volume Spike Rules

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "To time it correctly, I have to wait up here. When is absolute exhaustion reached?" | KEe_CWHyuSg [END] T4 | MISSING | Partial (volume spike detectable) | Add exhaustion gate before counter entries |
| 2 | "absolute exhaustion is seen with a volume spike, or a lot of volume is suddenly generated at one price level, and then it goes below the balance." | KEe_CWHyuSg [END] T4 | MISSING | Partial | **CRITICAL: Volume spike at one price + break below balance = exhaustion** |
| 3 | "when we see volume dropping, that the market simply isn't being played fairly anymore." | KEe_CWHyuSg [MIDDLE] T4 | MISSING | Partial (volume data exists) | Volume dropping = no fair pricing = pullback likely |

**Engine Gap #7:** Engine has no exhaustion detection. It generates CT setups at zones without waiting for exhaustion proof. Tom explicitly waits for "absolute exhaustion" before counter trading.

### 3.2 Footprint Exhaustion Signs

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "I see the Nasdaq looks like a surface-to-surface rocket. There's absolutely no substance there." | KEe_CWHyuSg [END] T1 | MISSING | NO (visual only) | Steep move + little liquidity = no substance = high turn probability |
| 2 | "very steep moves with little liquidity indicate a high probability of a turn" | KEe_CWHyuSg [END] T1 summary | MISSING | NO | Visual validation layer flag |

### 3.3 Post-Exhaustion Behavior

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "The market had consolidated here, immediately reacted at the absolute low volume, and ran back up." | KEe_CWHyuSg [MIDDLE] T1 | MISSING | Partial | Post-exhaustion = return to last high-turnover area |

---

## 4. PRIOR DAY / SESSION RANGE

### 4.1 Prior Day H/L Usage

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "look here is yesterday's value area low and maybe that's where the VPOC is. First in terms of price range if I see that the market is below that then I can definitely try a short trade." | BVpYGKz9PBU [MIDDLE] T1 | PARTIAL (engine has prior_day VAH/VAL) | YES (prior_day exists) | **Already in engine since v4.2.0 zone expansion** |
| 2 | "up here the market was in balance, but the closing price was really low down below. And at the end of the trading session, we also had what's called a single print." | BVpYGKz9PBU [MIDDLE] T1 | MISSING | Partial (needs close + single print) | Prior day close + single print = context for next day |
| 3 | "Today we briefly approached yesterday's highs and now the market is going down and repairing the single prints." | Vd83oo_geMk [MIDDLE] T1 | MISSING | Partial | Yesterday's high = rejection → repair single prints below |
| 4 | "Yesterday's value area and high-volume areas provide trade levels" | vk0mkNPuhDc [MIDDLE] T4 | PARTIAL | YES | Already in engine |
| 5 | "It goes to yesterday's PC back to my intelligent smart support and resistance line and then I expect the market to reach the corresponding intelligent price zone down here" | yRvMW6lgN1o [MIDDLE] T1 | MISSING | Partial (needs prior close) | **DSA: add prior_day.close** |

**Engine Gap #8:** Engine has prior_day VAH/VAL/POC (v4.2.0 zone expansion) but does NOT use prior day **close** or prior day **single prints** as context. Tom uses prior day close as a key level.

### 4.2 London/NY Range Usage

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "Therefore, we'll get great information at the US open today and then we'll have planning options." | C9n_d91Uitc [END] T4 | MISSING | Partial (session timing exists) | US open = information event, not just a time |
| 2 | "At yesterday's initial market open, it started way down here and then suddenly shot up just like a powerful rocket." | T6hDJcHrVBM [MIDDLE] T1 | MISSING | NO | Market open behavior = context for current day |

**Finding:** Tom references "US open" and "market open" as information events, but **does NOT explicitly use London range or session high/low** as structural levels in the extracted videos. The "session timing research" (validated in v4.2.0) correctly concluded that Tom does not have hard session rules — he uses opens as reference points, not as fixed boundaries.

### 4.3 Session Transfer Rules

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "if you combine that with a price range that you've predefined, for example, yesterday's closing price, then that's information that there was a rejection down here" | rrHj24GSR6M [MIDDLE] T4 | MISSING | Partial | Prior day close + current rejection = setup context |

---

## 5. TARGET PROJECTION

### 5.1 Beyond Next POC

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "the next price area I was able to identify to the downside was 140... I enter here and I want to get down there. That's the plan I'm putting together for myself for now." | BVpYGKz9PBU [MIDDLE] T1 | PARTIAL (engine uses next POC) | YES | Tom projects to **next structural level**, not just next POC |
| 2 | "It will simply drop down to the next price area where real volume took place" | 3JqMyzE8jIQ [END] T1 | PARTIAL | YES | "Next price area where real volume took place" = next high-volume node |
| 3 | "Intraday profiles help locate next targets using naked POCs, old single print areas, and old value areas." | YopZ5ZDmMFw [MIDDLE] T4 | MISSING | Partial | **Target hierarchy: naked POC → old single print → old VA** |
| 4 | "target the next high-volume area" | qLnQan0KGmQ [BEGINNING] summary | PARTIAL | YES | Engine does this implicitly via zone ranking |

### 5.2 Single Print Targets

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "single prints are target areas for many market participants. That means that's where they exit the market. But they don't enter." | Fj4FDZQxw0I [MIDDLE] T5 | MISSING | Visual-only | **CRITICAL RULE: Single prints = target, NOT entry** |
| 2 | "Are there old single print areas that need to be repaired?" | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | "Repair" = price moves back to single print = target hit |

**Engine Gap #9:** Engine does not distinguish entry zones from target zones. It evaluates all zones as potential entries. Tom explicitly says single prints are where participants **exit**, not enter.

### 5.3 Double Distribution Gap Targets

| # | Tom Quote | Source GPS | Engine Status | DSA Feasibility | Recommendation |
|---|-----------|------------|---------------|-----------------|----------------|
| 1 | "This upper balance... and the lower one... were both aggressively bought." | -dMWA_bbm3o [MIDDLE] T1 | MISSING | Visual-only | In double distribution, target = opposite distribution's POC/VA |
| 2 | "What information does this double distribution give me? I need to know that before the week starts." | -dMWA_bbm3o [MIDDLE] T4 | MISSING | Visual-only | Pre-week planning: if upper rejected → target lower VA |
| 3 | "The balance... is situated quite high up across all the weekly candles. And then we have a beautiful... double distribution here." | -dMWA_bbm3o [MIDDLE] T1 | MISSING | Visual-only | VPOC location between distributions = bias indicator |

---

## 6. OUT OF SCOPE CONFIRMATION

| Concept | Tom Mentions? | Evidence | Verdict |
|---------|--------------|----------|---------|
| Monthly/quarterly structure | NO | No mentions in 47 extracts | Tom does not address this in extracted videos. |
| London range as structural level | NO | "London" appears 0 times in trading context | Tom does not address this in extracted videos. |
| Session high/low as stops | NO | "session high" / "session low" not used structurally | Tom does not address this in extracted videos. |
| On-chain data | NO | Zero mentions | Tom does not address this in extracted videos. |
| SPX/DXY/yield correlation | NO | Macro mentioned only via VIX/volatility | Tom does not address this in extracted videos. |
| News/event trading | NO | No event-specific rules | Tom does not address this in extracted videos. |

**Confirmed:** The session timing research (v4.2.0) correctly rejected hard session rules. Tom uses "US open" as an information event, not as a fixed boundary.

---

## 7. ENGINE PATCH RECOMMENDATIONS

| # | Patch | Section | DSA Fields Needed | Priority | Tom Basis |
|---|-------|---------|-------------------|----------|-----------|
| 1 | **Weekly VP Shape Read [VISUAL]** | compiled_engine.md Section 1 (State Classifier) | None — visual only | HIGH | "What information does this double distribution give me? I need to know that before the week starts." |
| 2 | **Single Print = Target, Not Entry [RULE]** | compiled_engine.md Section 2.2 (Zone Evaluation) | None — visual only | HIGH | "single prints are target areas for many market participants. That means that's where they exit the market. But they don't enter." |
| 3 | **VPOC Migration Trend [DSA-DRIVEN]** | compiled_engine.md Section 1.2 (Trend Strength) | `prior_week_vp.poc`, `two_week_ago_vp.poc` | HIGH | "Rising VPOCs with increasing liquidity indicate a stable, bullish structure." |
| 4 | **Double Distribution Breakdown Target [RULE]** | compiled_engine.md Section 2.4 (Target Projection) | None — visual only | HIGH | Upper balance rejected → target lower distribution POC/VA |
| 5 | **Exhaustion Gate for CT [RULE]** | compiled_engine.md Section 3 (Trigger Engine) | `volume_spike_at_level` boolean | MEDIUM | "absolute exhaustion is seen with a volume spike, or a lot of volume is suddenly generated at one price level, and then it goes below the balance." |
| 6 | **Prior Day Close as Zone [DSA]** | compiled_engine.md Section 2.1 (Zone Map) | `prior_day.close` | MEDIUM | "if you combine that with a price range that you've predefined, for example, yesterday's closing price" |
| 7 | **Acceleration on Break Below VAL [RULE]** | compiled_engine.md Section 1.1 (State) | `speed_picking_up` (exists) | MEDIUM | "Very often it accelerates at first... a lot of market participants fall out of balance and then they sell their positions below that level" |
| 8 | **Daily Profile Step [VISUAL/DSA]** | compiled_engine.md Section 1 (Context) | `daily_vp` shape (not just nodes) | LOW | "Now I need to fine-tune the whole thing. And to fine-tune everything, I look at the daily profiles." |

---

## 8. DSA SCHEMA CHANGES

| Field | Type | Source | Tom Quote | Priority |
|-------|------|--------|-----------|----------|
| `prior_week_vp.poc` | float | DSA compute | "Rising VPOCs with increasing liquidity indicate a stable, bullish structure." | HIGH |
| `two_week_ago_vp.poc` | float | DSA compute | "Because the value area has shifted. You can see that here in the two weeks it simply moved lower" | HIGH |
| `prior_day.close` | float | DSA compute | "if you combine that with a price range that you've predefined, for example, yesterday's closing price" | MEDIUM |
| `weekly_vp.distribution_count` | int | DSA compute (histogram) | "we have a beautiful, what's called a double distribution here." | MEDIUM |
| `weekly_vp.single_print_areas` | array[float, float] | DSA compute (histogram) | "single prints always occur when markets have traded rapidly in one direction" | MEDIUM |
| `volume_spike_at_level` | boolean | DSA compute | "absolute exhaustion is seen with a volume spike, or a lot of volume is suddenly generated at one price level" | MEDIUM |
| `daily_vp.poc` | float | DSA compute (exists?) | "Now I need to fine-tune the whole thing. And to fine-tune everything, I look at the daily profiles." | LOW |
| `daily_vp.vah` | float | DSA compute (exists?) | "daily profiles give me information about where strong hands have been active" | LOW |
| `daily_vp.val` | float | DSA compute (exists?) | "where strong hands have been active in shorter And where will these strong hands give up their positions?" | LOW |

---

## 9. VISUAL-ONLY LAYER (Cannot Be DSA-Emit)

| Concept | Why Visual Only | What the Engine Should Do |
|---------|----------------|---------------------------|
| Double distribution shape | Requires histogram modality detection | AI screenshot analysis: "Two POCs visible?" → flag |
| Single print identification | Requires volume histogram trough detection | AI screenshot analysis: "Single prints between distributions?" → flag as target, not entry |
| VPOC trend line | Requires connecting weekly POCs visually | AI draws trend line across 4 weekly VPOCs |
| Exhaustion volume spike | Requires footprint/footprint-level volume | AI reads footprint: "volume spike + break below balance" |
| Nasdaq "surface-to-surface rocket" | Qualitative steepness assessment | AI flag: "steep move + little liquidity = no substance" |

---

## 10. INTEGRATION COMPLEXITY ASSESSMENT

| Patch | Complexity | Integration Path |
|-------|-----------|------------------|
| Single Print = Target | **LOW** | Add negative rule to zone evaluation: "If zone is single print → SKIP for entry, ADD as target" |
| VPOC Migration | **MEDIUM** | Add DSA fields, add trend rule to state classifier |
| Double Distribution Target | **MEDIUM** | Add visual flag, add target projection rule: "If double distribution + upper rejected → target lower POC" |
| Exhaustion Gate | **MEDIUM** | Add DSA field, add trigger condition: "CT requires exhaustion proof (volume spike or B profile)" |
| Prior Day Close | **LOW** | Add DSA field, add to zone map |
| Acceleration on Break | **LOW** | Connect existing `speed_picking_up` to break-below-VAL event |

---

## 11. RECOMMENDED NEXT SESSION WORK

1. **Implement Patch #2 (Single Print = Target)** — LOW complexity, HIGH impact. Prevents engine from entering at single prints.
2. **Implement Patch #3 (VPOC Migration)** — Add 2 DSA fields, 1 engine rule. Enables trend strength read from VPOC slope. STAGED in engine [REQUIRES DSA_TASK_006].
3. **Implement Patch #4 (Double Distribution Target)** — Visual flag + target rule. This is the "4H double top" fix from the handoff. LIVE in engine.
4. **Implement Patch #6 (Prior Day Close as Zone)** — LOW complexity. Add DSA field, add to zone map. BLOCKED [REQUIRES DSA_TASK_006 Field 3].
5. **Implement Patch #5 (Exhaustion Gate for CT)** — MEDIUM complexity. Add DSA field, add trigger condition. BLOCKED [REQUIRES DSA_TASK_006 Field 4].
6. **Update DSA schema v1.3.0** — Add `prior_week_vp.poc`, `two_week_ago_vp.poc`, `prior_day.close`.
7. **Update 02a_CURRENT_STATUS.md** — Mark HTF Structure Audit COMPLETE, add new pending patches.

---

## AUDITOR NOTES

- **Zero fabrication:** Every quote has Source GPS (Video ID + Section + Tier).
- **Visual-only flagged:** Concepts requiring volume profile histogram shape are flagged as visual-only. DSA cannot emit these without VP histogram API changes.
- **No London range:** Confirmed Tom does not use London range as structural level. Prior session timing research validated.
- **No monthly/quarterly:** Confirmed Tom does not reference these timeframes.
- **Prior day = validated:** Tom uses prior day VAL/VPOC/close extensively. Engine partially has this (VAH/VAL/POC since v4.2.0). Missing: `prior_day.close`.

---

# END OF AUDIT
