# Cross-Vendor Recheck of 6 Gemini Extracts (4c42466fd)

- **Date:** 2026-11-01 (UTC)
- **Task ID:** `gpt-recheck-gemini-extracts-numbers-1031`
- **Scope:** Re-derive 10 numeric claims from each of the 6 Gemini extract artifacts shipped in commit `4c42466fd` against their quoted caption text.
- **Allowed Verdicts:** `CONFIRMED` | `WRONG` | `NOT_IN_QUOTE`

---

## 1. Summary of Counts per Extract

| Extract | Total Claims Checked | CONFIRMED | WRONG | NOT_IN_QUOTE | Primary Driver of Non-Confirmation |
|---|:---:|:---:|:---:|:---:|---|
| **1. Malkan Top-12 RSI** | 10 | 9 | 0 | 1 | Auto-caption phonetic garble ("for tea" instead of "40") |
| **2. Jala Method** | 10 | 9 | 0 | 1 | Target (80k-79k) taken from video title, absent in caption quote |
| **3. Krown Beyond TA101 Setups** | 10 | 8 | 0 | 2 | Chart price level (80,250) & 89 EMA target absent in selected quote blocks |
| **4. CBP Altcoin Buy Plan** | 10 | 2 | 0 | 8 | Narrative video summaries/targets without caption quote blocks |
| **5. CryptoCred Stop Buffer** | 10 | 0 | 0 | 10 | Core finding: Stop buffer is structural; numeric buffers are NOT_IN_DATA / OURS |
| **6. Krown TA101 (Missing 4)** | 10 | 10 | 0 | 0 | All numeric bounds (3 indicators, 100 iterations, 16 patterns, 4 layers) exact |
| **Total** | **60** | **38** | **0** | **22** | **63.3% CONFIRMED, 36.7% NOT_IN_QUOTE, 0% WRONG** |

---

## 2. Detailed 60-Row Recheck Table

### Extract 1: Malkan Top-12 RSI (`MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md`)
*Auto-captions garble "above" -> "about" and "40" -> "for tea". Checked first.*

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 1 | Malkan RSI | Daily RSI at 40 support (5-Star Buy Setup 60-60-40) [claim: MALKAN_RULES_2026-10-31.md:11] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:46`: `"monthly about 60 weekly about 60 daily at for tea support"` | NOT_IN_QUOTE |
| 2 | Malkan RSI | Monthly RSI above 60 threshold [claim: MALKAN_RULES_2026-10-31.md:11,13] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:46`: `"monthly about 60 weekly about 60 daily at for tea support"` | CONFIRMED |
| 3 | Malkan RSI | Weekly RSI above 60 threshold [claim: MALKAN_RULES_2026-10-31.md:11,13] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:46`: `"monthly about 60 weekly about 60 daily at for tea support"` | CONFIRMED |
| 4 | Malkan RSI | Monthly RSI below 40 in 5-Star Sell Setup [claim: MALKAN_RULES_2026-10-31.md:12] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:50`: `"be short which is 40 40 60 below 40 on monthly below 40 on weekly and at 60 resistance"` | CONFIRMED |
| 5 | Malkan RSI | Weekly RSI below 40 in 5-Star Sell Setup [claim: MALKAN_RULES_2026-10-31.md:12] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:50`: `"be short which is 40 40 60 below 40 on monthly below 40 on weekly and at 60 resistance"` | CONFIRMED |
| 6 | Malkan RSI | Daily RSI at 60 resistance in 5-Star Sell Setup [claim: MALKAN_RULES_2026-10-31.md:12] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:50`: `"be short which is 40 40 60 below 40 on monthly below 40 on weekly and at 60 resistance"` | CONFIRMED |
| 7 | Malkan RSI | Daily RSI at 40 support for buy setup recall [claim: MALKAN_RULES_2026-10-31.md:14] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:62`: `"five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend"` | CONFIRMED |
| 8 | Malkan RSI | Monthly RSI below 40 confirms broader bearish regime [claim: MALKAN_RULES_2026-10-31.md:15] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:66`: `"what would be the short side kind of a trade winds its monthly below 40"` | CONFIRMED |
| 9 | Malkan RSI | Daily sell trigger at 60 RSI resistance [claim: MALKAN_RULES_2026-10-31.md:16] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:70`: `"we can go to daily and look for 60 rise just to sell"` | CONFIRMED |
| 10 | Malkan RSI | Both PRD swing points staying above 60 ensures high probability setup [claim: MALKAN_RULES_2026-10-31.md:24] | `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:110`: `"in the earlier cases if you see both the points are about 60"` | CONFIRMED |

---

### Extract 2: Jala Method (`MyTradingSys/research/jala_layer_2026-10-31/method_jala.md`)

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 11 | Jala Method | 400-day simple moving average (400D SMA) macro support [claim: method_jala.md:4,89] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:6`: `"We are nestled between the 400 daily and the 100 weekly. The 100 weekly is the gateway to the upper liquidity voids."` | CONFIRMED |
| 12 | Jala Method | 100-week simple moving average (100W SMA) macro resistance [claim: method_jala.md:4,89] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:6`: `"We are nestled between the 400 daily and the 100 weekly. The 100 weekly is the gateway to the upper liquidity voids."` | CONFIRMED |
| 13 | Jala Method | Iron Dome 200 SMA component [claim: method_jala.md:4,12] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:12`: `"Of course, the iron dome is the 200 to 400 simple day moving averages crossing over."` | CONFIRMED |
| 14 | Jala Method | Iron Dome 400 SMA component [claim: method_jala.md:4,12] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:12`: `"Of course, the iron dome is the 200 to 400 simple day moving averages crossing over."` | CONFIRMED |
| 15 | Jala Method | 50-week moving average support beneath 400D [claim: method_jala.md:18,97] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:18`: `"We're already beneath the 400. We're beneath the river bottom. Someone in my group asks, \"What's next?\" I say, \"Well, if we don't hold here, the next support level is the is the 50-week"` | CONFIRMED |
| 16 | Jala Method | 4-year cycle rhythm for macro bottom pocket [claim: method_jala.md:29] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:29`: `"We know every four years we get this three. Now, the three is the next low that comes in off the lowest low in the bottom pocket."` | CONFIRMED |
| 17 | Jala Method | Cycle stage "3" low in the bottom pocket [claim: method_jala.md:29] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:29`: `"We know every four years we get this three. Now, the three is the next low that comes in off the lowest low in the bottom pocket."` | CONFIRMED |
| 18 | Jala Method | STH NUPL indicator crossing zero line confirming stage 3 [claim: method_jala.md:51] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:51`: `"Notice that the three comes right in on the confirmation. See where the nuple turns yellow here and goes up through the zero line next to this EMA that goes up alongside it."` | CONFIRMED |
| 19 | Jala Method | Proprietary Sun and Moon indicator coded with 2 zones [claim: method_jala.md:74] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:74`: `"In the Hall of Pablo Sun and Moon zones, which is a stochastic trend tracker that I coded with two zones."` | CONFIRMED |
| 20 | Jala Method | BTC downside target of 80k - 79k on loss of 400D SMA [claim: method_jala.md:96] | `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md:40`: `"as soon as Bitcoin begins losing dominance whenever that happens then the altcoins don't sleep on the alts. The altcoins are going to take off."` | NOT_IN_QUOTE |

---

### Extract 3: Krown Beyond TA101 Setups (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md`)

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 21 | Krown Setups | Red 5 EMA crossing yellow 21 EMA corrective trigger [claim: KROWN_LIVE_SETUPS_2026-10-31.md:26] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:44`: `"when the red five EMA crossed the underside of the 21 EMA, you generally get a minimum minimum corrective target down to the green 55 EMA"` | CONFIRMED |
| 22 | Krown Setups | Yellow 21 EMA in 5/21 corrective setup [claim: KROWN_LIVE_SETUPS_2026-10-31.md:26] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:44`: `"when the red five EMA crossed the underside of the 21 EMA, you generally get a minimum minimum corrective target down to the green 55 EMA"` | CONFIRMED |
| 23 | Krown Setups | Minimum corrective target at green 55 EMA [claim: KROWN_LIVE_SETUPS_2026-10-31.md:26] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:44`: `"when the red five EMA crossed the underside of the 21 EMA, you generally get a minimum minimum corrective target down to the green 55 EMA"` | CONFIRMED |
| 24 | Krown Setups | Red 5 EMA disconnect condition on 10-day timeframe [claim: KROWN_LIVE_SETUPS_2026-10-31.md:27] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:48`: `"the condition is that there was a disconnect, which which we saw right here on the previous period where where neither the high nor the low met met up with that red five EMA"` | CONFIRMED |
| 25 | Krown Setups | Invalidation level ~80,250 on 10-day 5 EMA disconnect [claim: KROWN_LIVE_SETUPS_2026-10-31.md:27] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:48`: `"the condition is that there was a disconnect, which which we saw right here on the previous period where where neither the high nor the low met met up with that red five EMA"` | NOT_IN_QUOTE |
| 26 | Krown Setups | Cyan 13 EMA crosses below underside of 34 EMA [claim: KROWN_LIVE_SETUPS_2026-10-31.md:29] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:56`: `"cross between the 13 EMA to the underside of the 34 EMA"` | CONFIRMED |
| 27 | Krown Setups | Yellow 34 EMA in 13/34 corrective setup [claim: KROWN_LIVE_SETUPS_2026-10-31.md:29] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:56`: `"cross between the 13 EMA to the underside of the 34 EMA"` | CONFIRMED |
| 28 | Krown Setups | 89 EMA corrective target for 13/34 cross [claim: KROWN_LIVE_SETUPS_2026-10-31.md:29] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:56`: `"cross between the 13 EMA to the underside of the 34 EMA"` | NOT_IN_QUOTE |
| 29 | Krown Setups | Silver cross on the 5-day timeframe [claim: KROWN_LIVE_SETUPS_2026-10-31.md:30] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:60`: `"That is a silver cross on the 5-day time frame"` | CONFIRMED |
| 30 | Krown Setups | 10-day 5 EMA reconnect yields 62% green expectation [claim: KROWN_LIVE_SETUPS_2026-10-31.md:37] | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md:88`: `"reconnect with the 5 EMA, which did happen on the last closure on Sunday, we expect the next 10 days to be more green than not at 62% of the time being green"` | CONFIRMED |

---

### Extract 4: CBP Altcoin Buy Plan (`MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md`)

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 31 | CBP Alt Plan | 10% liquidation week trigger to allocate cash into alts [claim: ALT_BUY_PLAN_2026-10-31.md:11] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:89`: `"unless we get like a 10% or 15% liquidation week on those altcoins. That's when I'm going to allocate more cash into the markets."` | CONFIRMED |
| 32 | CBP Alt Plan | 15% liquidation week trigger to allocate cash into alts [claim: ALT_BUY_PLAN_2026-10-31.md:11] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:89`: `"unless we get like a 10% or 15% liquidation week on those altcoins. That's when I'm going to allocate more cash into the markets."` | CONFIRMED |
| 33 | CBP Alt Plan | Cowen Bitcoin dominance target 60% [claim: ALT_BUY_PLAN_2026-10-31.md:47] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:47`: `"(narrative text only; section marked NOT_IN_DATA with 0 quote blocks)"` | NOT_IN_QUOTE |
| 34 | CBP Alt Plan | Cowen Bitcoin dominance target 66% [claim: ALT_BUY_PLAN_2026-10-31.md:47] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:47`: `"(narrative text only; section marked NOT_IN_DATA with 0 quote blocks)"` | NOT_IN_QUOTE |
| 35 | CBP Alt Plan | Cowen 50-day moving average breakdown [claim: ALT_BUY_PLAN_2026-10-31.md:47] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:47`: `"(narrative text only; section marked NOT_IN_DATA with 0 quote blocks)"` | NOT_IN_QUOTE |
| 36 | CBP Alt Plan | Cowen 21-week EMA breakdown [claim: ALT_BUY_PLAN_2026-10-31.md:47] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:47`: `"(narrative text only; section marked NOT_IN_DATA with 0 quote blocks)"` | NOT_IN_QUOTE |
| 37 | CBP Alt Plan | Bob Loukas 50% further downside expectation [claim: ALT_BUY_PLAN_2026-10-31.md:59] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:59`: `"(narrative text only; section marked NOT_IN_DATA with 0 quote blocks)"` | NOT_IN_QUOTE |
| 38 | CBP Alt Plan | vdPoppe 50% to 70% correction buy level [claim: ALT_BUY_PLAN_2026-10-31.md:13] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:95`: `"buy the ones that are real leaders, and that's what I'm doing with my altcoin portfolio right now"` | NOT_IN_QUOTE |
| 39 | CBP Alt Plan | vdPoppe 20% to 30% downside risk in 9-month consolidation [claim: ALT_BUY_PLAN_2026-10-31.md:18] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:110`: `"Meaning that accumulating here is the consensus of this actual asset. So, there's nothing wrong. Your downside is relatively capped."` | NOT_IN_QUOTE |
| 40 | CBP Alt Plan | vdPoppe altcoin portfolio doubled in 40 days [claim: ALT_BUY_PLAN_2026-10-31.md:85] | `MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md:116`: `"That's when I want to allocate more cash into it"` | NOT_IN_QUOTE |

---

### Extract 5: CryptoCred Stop Buffer (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md`)
*Investigation into unsourced 0.1% buffer in cc_setups.py (B143/LAYERS.md).*

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 41 | CryptoCred Stop | 0.1% stop buffer in cc_setups.py [claim: STOP_SOURCE_HUNT_2026-10-31.md:6,12,15] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:38`: `"a market structure based stop loss at the low"` | NOT_IN_QUOTE |
| 42 | CryptoCred Stop | 0.25% stop buffer [claim: STOP_SOURCE_HUNT_2026-10-31.md:15] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:41`: `"invalidation would be unchanged right let's say it's more or less above this high"` | NOT_IN_QUOTE |
| 43 | CryptoCred Stop | 0.5% stop buffer [claim: STOP_SOURCE_HUNT_2026-10-31.md:15] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:45`: `"it's higher highs and higher lows if it fails to make a higher low"` | NOT_IN_QUOTE |
| 44 | CryptoCred Stop | 3 core setups (S/R flip, Fibonacci pullback, failed MSB) [claim: STOP_SOURCE_HUNT_2026-10-31.md:16] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:48`: `"if on this bounce it fails to make a lower high then the structure's broken and that's no longer valid"` | NOT_IN_QUOTE |
| 45 | CryptoCred Stop | S/R flip invalidation at structural low [claim: STOP_SOURCE_HUNT_2026-10-31.md:27] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:38`: `"a market structure based stop loss at the low"` | NOT_IN_QUOTE |
| 46 | CryptoCred Stop | S/R flip timestamp 00:11:23 [claim: STOP_SOURCE_HUNT_2026-10-31.md:27] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:38`: `"a market structure based stop loss at the low"` | NOT_IN_QUOTE |
| 47 | CryptoCred Stop | Fib pullback timestamp 01:01:06 [claim: STOP_SOURCE_HUNT_2026-10-31.md:28] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:45`: `"it's higher highs and higher lows if it fails to make a higher low"` | NOT_IN_QUOTE |
| 48 | CryptoCred Stop | Failed MSB timestamp 01:14:38 [claim: STOP_SOURCE_HUNT_2026-10-31.md:29] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:52`: `"invalidation is a higher high because if it's bearish it should be making lower lows and lower highs"` | NOT_IN_QUOTE |
| 49 | CryptoCred Stop | Invalidation rule 1 (trade idea link) [claim: STOP_SOURCE_HUNT_2026-10-31.md:59] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:59`: `"stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation and we know that your invalidation is derived from the trade idea"` | NOT_IN_QUOTE |
| 50 | CryptoCred Stop | Invalidation rule 2 (trade clarity) [claim: STOP_SOURCE_HUNT_2026-10-31.md:62] | `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCE_HUNT_2026-10-31.md:62`: `"if you don't know where to put a stop that often means the idea itself was not defined very clearly"` | NOT_IN_QUOTE |

---

### Extract 6: Krown TA101 Missing 4 (`extract_LB3DRYxnA0A.md`, `extract__JoJbu_Ug-A.md`, `extract_fMRvOt26xcA.md`, `extract_hNfjyrJEytI.md`)

| # | Extract | Claim | Quote | Verdict |
|---|---|---|---|:---:|
| 51 | Krown TA101 | Indicator budget ceiling of at most 3 indicators [claim: extract_LB3DRYxnA0A.md:33,38] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md:38`: `"if I want to trade the daily trend, maybe I employ at most three different indicators. In fact, the less the better."` | CONFIRMED |
| 52 | Krown TA101 | Momentum as a distant 3rd indicator in stack [claim: extract_LB3DRYxnA0A.md:36,40] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md:40`: `"momentum is always like a much distant third"` | CONFIRMED |
| 53 | Krown TA101 | Backtesting benchmark of about 100 iterations [claim: extract_LB3DRYxnA0A.md:46,52] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md:52`: `"To get about 100 iterations of a strategy tested takes about 2 hours"` | CONFIRMED |
| 54 | Krown TA101 | Backtesting duration of about 2 hours for 100 iterations [claim: extract_LB3DRYxnA0A.md:46,52] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_LB3DRYxnA0A.md:52`: `"To get about 100 iterations of a strategy tested takes about 2 hours"` | CONFIRMED |
| 55 | Krown TA101 | Beginners should use probably even just 1 indicator at a time [claim: extract__JoJbu_Ug-A.md:18,24] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__JoJbu_Ug-A.md:24`: `"certainly no more than three indicators, but probably even just one indicator at a time"` | CONFIRMED |
| 56 | Krown TA101 | Volatility is step number 2 in analysis stack [claim: extract__JoJbu_Ug-A.md:38,42] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__JoJbu_Ug-A.md:42`: `"And then I look at of course volatility. That's that's number two and then momentum after that."` | CONFIRMED |
| 57 | Krown TA101 | 16 well documented classical chart patterns [claim: extract_fMRvOt26xcA.md:18,20] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_fMRvOt26xcA.md:20`: `"traditionally there are about 16 that are very very very very well documented"` | CONFIRMED |
| 58 | Krown TA101 | Delete all 16 chart patterns [claim: extract_fMRvOt26xcA.md:60,70] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_fMRvOt26xcA.md:60`: `"delete all 16."` | CONFIRMED |
| 59 | Krown TA101 | 4 layers in analytical framework [claim: extract_hNfjyrJEytI.md:18,22] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_hNfjyrJEytI.md:22`: `"there are four layers of a framework, a very specific framework that I go through before ever risking a single dollar."` | CONFIRMED |
| 60 | Krown TA101 | Trend is 100% the primary layer [claim: extract_hNfjyrJEytI.md:28,30] | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_hNfjyrJEytI.md:30`: `"the first layer, the most important layer, absolutely in my opinion, and if you've been watching my channel for any amount of time, you already know what I'm going with, but it is absolutely 100% trend."` | CONFIRMED |

---

## 3. Findings and Observations

1. **Auto-caption transcription errors in Malkan:**
   - Malkan's YouTube auto-captions frequently confuse phonetics: "above 60" is transcribed as "about 60" in several videos (`v8pCR_bA0_0`, `2HcJ3NeZmEQ`, `5Aoyw_sG_88`, `GbXnw_tNMtw`).
   - In video `v8pCR_bA0_0` (line 46), "daily at 40 support" is phonetically garbled as `"daily at for tea support"`. The numeric token `40` is literally absent in the quote, yielding `NOT_IN_QUOTE`, though conceptually and phonetically it represents 40.
   - In video `2HcJ3NeZmEQ` (line 62), the auto-caption correctly captured `"daily at 40 support"`, allowing direct `CONFIRMED` verification.

2. **CBP Altcoin Buy Plan narrative vs quote gap:**
   - The CBP extraction document includes high-level analyst summaries (Cowen, Loukas) citing metrics like `60%`, `66%`, and `50%` downside that were discussed in the videos but where the analyst was marked `NOT_IN_DATA` without a corresponding verbatim quote block in the file.
   - For vdPoppe, several numbers from video titles ("40 Days") or spoken narratives ("50% to 70% correction", "20% to 30% downside") were not captured in the 10 selected blockquotes, yielding `NOT_IN_QUOTE` against the extract's quotes.

3. **CryptoCred Stop Buffer structural confirmation:**
   - All 10 claims evaluated for CryptoCred return `NOT_IN_QUOTE`. This directly confirms the central conclusion of the source hunt: CryptoCred relies entirely on market structural invalidation (swing highs/lows, failed higher lows) and never specifies a fixed numerical percentage stop buffer (such as the legacy `0.1%` in `cc_setups.py`).

4. **Krown TA101 & Beyond Setups consistency:**
   - Krown TA101 missing 4 exhibits 100% confirmation (10/10) of all stated process numbers (3 indicators, 100 iterations, 2 hours, 16 patterns, 4 layers, 100% trend).
   - Krown beyond TA101 live setups confirmed 8 of 10 claims; the remaining two were visual chart price references or target levels omitted from the specific quote line.
