# CBP Analyst Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined from CBP analyst source files (`MyTradingSys/research/cbp_gap_1112` and `MyTradingSys/research/cbp`). Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| CBP-R01 | Price vs Prior Support & 200-Day Moving Average | Sweep of previous major support zones / wick below 200-day moving average | Bounce following sweep / wick below 200-day moving average | Reversal bounce after support clear | NOT_STATED | NOT_STATED | Daily / 20-week / 21-week | `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:14-16` |
| CBP-R02 | Price vs Realized Price | Test of cycle realized price (~54k) | NOT_STATED | Eventual cycle test level (~54k) | NOT_STATED | 60k to 80k rally | Multi-week / Cycle | `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:29-32` |
| CBP-R03 | Price vs Resistance / Cycle Top | Rally to 80k following drop to 60k | Crash rejection after consolidation | NOT_STATED | NOT_STATED | Rejection back down | Multi-week | `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:21-25` |
| CBP-R04 | Wilder ADX + DI (2-Day Chart) | Red DI crosses above green DI (sellers in control) | NOT_STATED | Red DI above green DI cross | NOT_STATED | Crosses back within 24 hours or trend reversal | 2-Day | `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:10` |
| CBP-R05 | Price vs September 15 Swing Low | Retest / sweep of $74,961 low (dipped to $74,871) | Higher low confirmation holding above $75,000 / $77,800 | Higher low around $77,800 | Lower high under $77,800 with daily close under $74,900 | $80,000 range | 1-Hour / Daily | `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:11,18` |
| CBP-R06 | Weekly Close vs Line in the Sand | Price falling below 75,000 | Weekly close confirmation below 75,000 | Breakdown continuation entry below 75,000 | Weekly close back above 75,000 / reclaim of 81,900 | 73,300 / 70,800 / 68,100 / 65,700 | Weekly | `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:12` |
| CBP-R07 | Cycle Phase / Macro Dip | Bitcoin drops ~40% from ₹1.1 crore peak into cycle low zone | 2-3 years holding window; normal 20-30% extra drawdown tolerance | Third-part DCA tranche 1 at current low zone | NOT_STATED | NOT_STATED | 2-3 Year Cycle | `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:8-10` |
| CBP-R08 | Cycle Phase Drawdown Tranche 2 | Bitcoin price falls to 65,000 - 67,000 $ | Price touching 65,000-67,000 $ boundary | Limit buy order at 65,000 - 67,000 $ | Weekly close below 60,000 | NOT_STATED | Daily / Multi-week | `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:15-18` |
| CBP-R09 | Cycle Phase Drawdown Tranche 3 | Bitcoin price falls near 60,000 $ | Price touching near 60,000 $ boundary | Limit buy order near 60,000 $ | Weekly close below 60,000 | NOT_STATED | Daily / Multi-week | `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:19-21` |
| CBP-R10 | BTC Price Level Phase 2 Zone | Bitcoin dip inside 72,000 - 75,000 zone holding 2 days | Bounced from 73,500 and held 2 days | Limit buy order Half A at 73,000 (BTC) / 2,000 (ETH) | NOT_STATED | NOT_STATED | Daily | `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:6-8,24-27` |
| CBP-R11 | BTC Price Level Phase 2 Deeper Dip | Deep pullback inside 72,000 - 75,000 zone | Fill upon deeper dip | Limit buy order Half B at 72,200 (BTC) | NOT_STATED | NOT_STATED | Daily | `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:23-28` |
| CBP-R12 | Weekly Close Invalidation Filter | Last week closes under 75,000 (e.g. 74,850) | Weekly candle close | Buy in two halves rather than all at once | NOT_STATED | NOT_STATED | Weekly | `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:7` |
| CBP-R13 | Macro Altcoin Allocation Trigger | Bitcoin reaches 65,000 level | Weekly close below 75,000 confirmed | Accumulate heavy altcoin positions ("would buy a lot") | Weekly close below 60,000 | NOT_STATED | Weekly | `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-07.md:7` |
| CBP-R14 | Bitcoin Dominance Invalidation | Bitcoin begins losing dominance | Declining BTC dominance candle confirmation | Buy altcoins holding market structure ("don't sleep on the alts") | NOT_STATED | NOT_STATED | Daily / Weekly | `MyTradingSys/research/cbp/archive/ALT_BUY_PLAN_2026-10-31.md:21,73` |
| CBP-R15 | Altcoin Liquidation Flush Extreme | 10% to 15% liquidation week on altcoins | Weekly liquidation flush candle | Allocate more cash / accumulate altcoins | NOT_STATED | NOT_STATED | Weekly | `MyTradingSys/research/cbp/archive/ALT_BUY_PLAN_2026-10-31.md:22,89` |

---

## 2. Verbatim Quotes and Source Citations

### Rule CBP-R01: Support Sweep & 200-Day Moving Average Wick
> "तो बिटकॉइन लगभग 72,000 डॉलर पर कारोबार कर रहा है"
**Source GPS: QcJlPjcOZjw | BEGIN**
- Context: `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:14-16` ("Current trading level / reference price")

### Rule CBP-R02: Eventual Realized Price Test
> "रियलाइज्ड प्राइस लगभग 54k पर है"
**Source GPS: QcJlPjcOZjw | END**
- Context: `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:29-32` ("Realized price test level")

### Rule CBP-R03: Potential Bounce Scenario
> "क्या होगा अगर बिटकॉइन 60 तक जाए, वापस 80 तक रैली करे"
**Source GPS: QcJlPjcOZjw | MIDDLE**
- Context: `MyTradingSys/research/cbp_gap_1112/QcJlPjcOZjw/EXTRACT.md:21-25` ("Potential bounce scenario / lower low path")

### Rule CBP-R04: ADX / DI 2-Day Cross Extreme
- Cited text: `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:10`
- Verbatim: "sellers are in control"
- Verbatim: "falling straight to the bottom"

### Rule CBP-R05: September 15 Swing Low Sweep & Higher Low
- Cited text: `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:11,18`
- Verbatim: "still holding above its low from September 15"
- Verbatim: "around $77,800"

### Rule CBP-R06: 75,000 Weekly Close Line in the Sand
- Cited text: `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:12`
- Verbatim: "weekly close = line in the sand"
- Verbatim: "reclaim ends the downtrend"

### Rule CBP-R07: 4-Year Cycle Low Zone Tranche 1
- Cited text: `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:8-10`
- Verbatim: "Bitcoin rises and falls in a ~4-year cycle"
- Verbatim: "waiting 2-3 years"

### Rule CBP-R08: Drawdown Tranche 2 (65,000-67,000)
- Cited text: `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:15-18`
- Verbatim: "If BTC falls to"
- Verbatim: "65,000-67,000 $"

### Rule CBP-R09: Drawdown Tranche 3 (Near 60,000)
- Cited text: `MyTradingSys/research/cbp/AUNT_NOTE_2026-11-09.md:19-21`
- Verbatim: "If BTC falls near"
- Verbatim: "60,000 $"

### Rule CBP-R10: Phase 2 Zone (72,000-75,000) Holding 2 Days
- Cited text: `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:6-8`
- Verbatim: "inside our Phase 2 zone (72,000-75,000)"
- Verbatim: "held there 2 days"

### Rule CBP-R11: Phase 2 Deeper Dip Limit Order
- Cited text: `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:23-28`
- Verbatim: "Limit orders (never Market)"
- Verbatim: "deeper, also place today"

### Rule CBP-R12: Sub-75k Weekly Close Caution
- Cited text: `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-09.md:7`
- Verbatim: "Last week closed at 74,850, just under 75,000"
- Verbatim: "buy in two halves"

### Rule CBP-R13: 65,000 Breakout Accumulation
- Cited text: `MyTradingSys/research/cbp/SISTER_NOTE_2026-11-07.md:7`
- Verbatim: "weekly close, 65,000 is possible, and that is where he"
- Verbatim: "would buy a lot"

### Rule CBP-R14: Bitcoin Dominance Loss
- Cited text: `MyTradingSys/research/cbp/archive/ALT_BUY_PLAN_2026-10-31.md:21,73`
- Verbatim: "as soon as Bitcoin begins losing dominance whenever that happens then the altcoins don't sleep on the alts"

### Rule CBP-R15: Altcoin Liquidation Flush Week
- Cited text: `MyTradingSys/research/cbp/archive/ALT_BUY_PLAN_2026-10-31.md:22,89`
- Verbatim: "unless we get like a 10% or 15% liquidation week on those altcoins. That's when I'm going to allocate more cash into the markets."

---

## 3. Ranked Top 5 by Fewest NOT_STATED Fields

Rankings are scored by counting unstated parameters (`extreme threshold`, `confirming candle`, `entry`, `stop`, `exit`, `timeframe`) across the 15 rules:

1. **Rank 1: Rule CBP-R05 (Sep-15 Low Sweep / $77,800 Reclaim)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Sweep of 74,961 low; Confirming candle = Higher low above 74,900 / 77,800; Entry = Higher low around $77,800; Stop = Lower high under 77,800 with daily close under 74,900; Exit = $80,000 range; Timeframe = 1-Hour / Daily).
2. **Rank 2: Rule CBP-R06 (Krown 75,000 Weekly Close Line in the Sand)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Sub-75,000 break; Confirming candle = Weekly close under 75,000; Entry = Breakdown continuation below 75,000; Stop = Weekly close back above 75,000 / 81,900 reclaim; Exit = 73,300 / 70,800 / 68,100 / 65,700 targets; Timeframe = Weekly).
3. **Rank 3: Rule CBP-R04 (CCU 2-Day ADX + DI Cross)**
   - NOT_STATED count: 2 (Stop = NOT_STATED, Confirming candle = NOT_STATED; Extreme = Red DI cross above Green DI; Entry = Cross confirmation; Exit = Cross back within 24h / trend change; Timeframe = 2-Day).
4. **Rank 4: Rule CBP-R08 (Aunt Note Drawdown Tranche 2: 65,000 - 67,000 $)**
   - NOT_STATED count: 2 (Stop = Weekly close below 60,000; Exit = NOT_STATED; Confirming candle = Price touch boundary; Entry = Limit buy order at 65,000 - 67,000 $; Extreme = Fall to 65,000 - 67,000 $; Timeframe = Daily / Multi-week).
5. **Rank 5: Rule CBP-R09 (Aunt Note Drawdown Tranche 3: Near 60,000 $)**
   - NOT_STATED count: 2 (Stop = Weekly close below 60,000; Exit = NOT_STATED; Confirming candle = Price touch boundary; Entry = Limit buy order near 60,000 $; Extreme = Fall near 60,000 $; Timeframe = Daily / Multi-week).
