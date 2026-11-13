# Tom & Fabio Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined from Tom Vorwald and Fabio Valentini source extractions (`extracts/v2/tom/` and `extracts/v2/fabio/`).
Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.
All verbatim quotes and Source GPS tags have been validated against transcript baselines with `scripts/dev/verify_extract_quotes.py`.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| TF-R01 | Market Profile POC / Value Area | Value Area Low broken with aggressive sellers absorbed | Absorption candle closes green at POC | Reversal buy on POC bounce | Below Value Area Low | Target at protection level (VAH) | NOT_STATED | `extracts/v2/fabio/cUTsoU-15Tc_v2.md:40` |
| TF-R02 | Market Profile Value Area Low Invalidation | Price tests below Value Area Low boundary | Candle closes below Value Area Low | Setup invalidated (no long entry; close/exit longs) | Candle close below VAL | NOT_STATED | NOT_STATED | `extracts/v2/fabio/cUTsoU-15Tc_v2.md:34` |
| TF-R03 | Value Area High, Big Trades & Delta Level Confluence | Confluence of VAH, big trades and delta level reached | Rejection candle at VAH / delta level | Short entry at confluence zone | Above the identified confluence area | Next swing point / 1:3 to 1:5 R:R | London / NY Session | `extracts/v2/fabio/06R-ebyOhDI_v2.md:27` |
| TF-R04 | Delta Print Zone Re-entry Execution | Price retests dynamic delta print zone from prior swing | Rejection / topping candle at retest area | Short re-entry at dynamic delta level | Above the identified area | Target next swing point (1:3 to 1:5 R:R) | London Session | `extracts/v2/fabio/06R-ebyOhDI_v2.md:31` |
| TF-R05 | Order Flow Absorption in Consolidation | Price consolidates with aggressive participants absorbed | Candle closes green after absorption | Long continuation entry on close | Low of the absorption candle / consolidation boundary | NOT_STATED | NOT_STATED | `extracts/v2/fabio/Pz8f0wWW12M_v2.md:22` |
| TF-R06 | Vertical Volume Exhaustion Divergence | Price pushes strong to new extreme while volume dries up | Reversal candle after volume dry-up green candle | Reversal fade entry against exhaustion move | Above exhaustion candle extreme | Snap back to value area | NOT_STATED | `extracts/v2/fabio/Pz8f0wWW12M_v2.md:26` |
| TF-R07 | Low Volume Node (LVN) Rebalance Pivot | Price reaches low volume node during price discovery | Rebalancing rejection candle bouncing off LVN | Continuation entry in direction of primary trend | Beyond LVN boundary | Resumption of trend discovery | NOT_STATED | `extracts/v2/fabio/Pz8f0wWW12M_v2.md:38` |
| TF-R08 | Order Flow Level Test with Absorbed Buyers | Aggressive buyers attempt breakout but show no follow-through | Rejection candle showing buyer absorption | Short entry on test of level with confirmed absorption | Above the absorption area | 1:4.5 R:R target | NOT_STATED | `extracts/v2/fabio/Is1HvdfQm5c_v2.md:650` |
| TF-R09 | Order Flow Squeeze Setup | Retest of confirmed level at third touch | Squeeze candle holding above absorbed sellers | Long entry on squeeze test | Below the support area | 1:4.9 to 1:5 R:R target | NOT_STATED | `extracts/v2/fabio/Is1HvdfQm5c_v2.md:701` |
| TF-R10 | Profile Liquidity & Absorption at Highs | Price reaches range extreme where liquidity decreases and absorption occurs | Rejection candle showing weakness / lack of liquidity | Short counter-trend entry on weakness proof | 20 points wide stop | Target at 140 area (120 points) / 3:1 R:R | NOT_STATED | `extracts/v2/tom/BVpYGKz9PBU_v2.md:154` |
| TF-R11 | PBD Reversal Setup 20-Point Stop | Price pulls back into prior-day value area rejection | Breakdown candle confirming weakness | Short entry at 260 level | Exactly 20 points wide (at 280 / tight structure) | 140 price area (120 points) / 3:1 R:R | DAX trading | `extracts/v2/tom/BVpYGKz9PBU_v2.md:214` |
| TF-R12 | Extreme Open Counter-Trend DAX Short | Extreme market open with absence of real big-player liquidity | Impulsive opening candle traded below | Short entry at morning liquidity extreme | 20 points in DAX | Below morning liquidity / pre-session impulse | Morning session | `extracts/v2/tom/k0zm5NYn0IQ_v2.md:246` |
| TF-R13 | Volume Structure Stop Management | Price breaks down from range after seller confirmation | Breakdown candle breaking range to downside | Re-entry short on range breakdown | Exactly above the last volume levels | 285 price area | DAX morning | `extracts/v2/tom/k0zm5NYn0IQ_v2.md:303` |
| TF-R14 | Swing Low Stop Sizing Model | Swing structure high/low extreme reached | Confirming candle bouncing from swing extreme | Entry on swing reversal | Placed below the low | Predefined target (1:3.5 to 1:5 R:R) | DAX / S&P | `extracts/v2/tom/UrZ4vpHJ97g_v2.md:72` |
| TF-R15 | Fair Value Gap (FVG) Retest Reversal | Market breaks market structure leaving fair value gap | Reversal candle filling FVG | Entry at fair value gap retest | Exactly where opposite market movement expected | Predefined target based on R:R | NOT_STATED | `extracts/v2/tom/5Ljfwvtktek_v2.md:74` |

---

## 2. Verbatim Quotes and Source Citations

### Rule TF-R01: Fabio POC Absorption Long Setup
> "Maybe we have a lot of aggressive sellers here with zero result. This means that there is a big absorption on this level on the PC."
Source GPS: cUTsoU-15Tc | BEGIN

- Context: `extracts/v2/fabio/cUTsoU-15Tc_v2.md:40`
- Explanation: Aggressive sellers fail to push price lower through the Point of Control (POC), creating absorption. Entry on bounce off POC targeting Value Area High, with stop below VAL.

### Rule TF-R02: Fabio Value Area Low Close Invalidation
> "If we close a candle here, okay, the setup is invalidated."
Source GPS: cUTsoU-15Tc | BEGIN

- Context: `extracts/v2/fabio/cUTsoU-15Tc_v2.md:34`
- Explanation: If a candle closes below the Value Area Low, market acceptance below value occurs and the setup is invalidated immediately.

### Rule TF-R03: Fabio VAH, Big Trades & Delta Level Confluence
> "So you have a confluence of value area high, big trades and delta level. This one is a super strong area."
Source GPS: 06R-ebyOhDI | BEGIN

- Context: `extracts/v2/fabio/06R-ebyOhDI_v2.md:27`
- Explanation: Confluence of multiple order flow indicators (Value Area High + big trades + delta print) creates a high probability rejection area for short entries.

### Rule TF-R04: Fabio Delta Print Protection Short Re-Entry
> "it's already an execution that you can make protecting yourself above the area that we already identified."
Source GPS: 06R-ebyOhDI | MIDDLE

- Context: `extracts/v2/fabio/06R-ebyOhDI_v2.md:31`
- Explanation: Execution of short entry or re-entry at the identified delta print level with stop loss protection placed strictly above the area.

### Rule TF-R05: Fabio Consolidation Absorption Green Candle Continuation
> "we have a market that is in a consolidation phase here, and we can spot that all these aggressive market participants here got absorbed and the candle closed green. This is a potential continuation of the move"
Source GPS: Pz8f0wWW12M | MIDDLE

- Context: `extracts/v2/fabio/Pz8f0wWW12M_v2.md:22`
- Explanation: During consolidation, aggressive sellers are absorbed and price prints a green candle close, triggering a long continuation entry with stop below the consolidation low.

### Rule TF-R06: Fabio Vertical Volume Dry-Up Exhaustion
> "from the concept of vertical volume you can find an exhaustion where you can see that the market is pushing really strong, printing another green candle, but the volume is getting lower and lower. This is a dry up in volume, and usually what you see this in a pattern order flow is that you have a sudden reversal in price."
Source GPS: Pz8f0wWW12M | MIDDLE

- Context: `extracts/v2/fabio/Pz8f0wWW12M_v2.md:26`
- Explanation: Price pushes strongly in trend printing green candles while vertical volume dries up, signaling buyer exhaustion and setting up a mean-reverting reversal fade.

### Rule TF-R07: Fabio Low Volume Node (LVN) Rebalance Pivot
> "When you have a low volume node and the market goes in price discovery, you can clearly see a lot of days the price coming back to rebalance in this low volume node and using this as a pivot before resuming the direction of the auction."
Source GPS: Pz8f0wWW12M | MIDDLE

- Context: `extracts/v2/fabio/Pz8f0wWW12M_v2.md:38`
- Explanation: In trending price discovery, pullbacks into a Low Volume Node act as rebalancing pivots where price rejects and resumes the primary auction trend.

### Rule TF-R08: Fabio Absorption of Buyers Test
> "the trade that in 2025 gave me the most amount of money is the test of this level with"
Source GPS: Is1HvdfQm5c | BEGIN

- Context: `extracts/v2/fabio/Is1HvdfQm5c_v2.md:650`
- Explanation: Retest of resistance where aggressive buyers show zero follow-through and are absorbed; short execution with stop above the area targeting 1:4.5 R:R.

### Rule TF-R09: Fabio Squeeze Setup with Stop Below Area
> "covering yourself below the area this is the squeeze setup"
Source GPS: Is1HvdfQm5c | BEGIN

- Context: `extracts/v2/fabio/Is1HvdfQm5c_v2.md:701`
- Explanation: The squeeze setup at the third touch of support with buyer confirmation and seller absorption, covering below the area targeting 1:4.9 to 1:5 R:R.

### Rule TF-R10: Tom Liquidity Decrease & Absorption at Highs
> "if liquidity decreases or rather if there is significant absorption up there then the probability that the market can turn becomes much higher"
Source GPS: BVpYGKz9PBU | BEGIN

- Context: `extracts/v2/tom/BVpYGKz9PBU_v2.md:154`
- Explanation: Liquidity exhaustion and footprint absorption at market highs establish high probability of counter-trend turn; entry on proof of weakness.

### Rule TF-R11: Tom 20-Point Stop Counter-Trade Setup
> "my stop loss is suddenly only 20 points wide"
Source GPS: BVpYGKz9PBU | END

- Context: `extracts/v2/tom/BVpYGKz9PBU_v2.md:214`
- Explanation: Short counter-trade entry at 260 after confirmation of market weakness, setting a tight 20-point stop loss for a 120-point target to 140 (R:R 2.66:1 to 3:1).

### Rule TF-R12: Tom DAX Short with 20-Point Stop
> "I'm setting a stop-loss of 20 points in the DAX"
Source GPS: k0zm5NYn0IQ | BEGIN

- Context: `extracts/v2/tom/k0zm5NYn0IQ_v2.md:246`
- Explanation: Counter-trend short entry at market open when extreme open lacks big-player liquidity, using a strict 20-point stop in the DAX.

### Rule TF-R13: Tom Stop Placed Above Last Volume Levels
> "my stop loss is now set exactly above the last volume levels"
Source GPS: k0zm5NYn0IQ | MIDDLE

- Context: `extracts/v2/tom/k0zm5NYn0IQ_v2.md:303`
- Explanation: In a range breakdown re-entry, the stop loss is anchored mechanically right above the latest high volume consolidation cluster.

### Rule TF-R14: Tom Stop Loss Below Swing Low
> "The next step is the stop loss, which I always place below the low."
Source GPS: UrZ4vpHJ97g | BEGIN

- Context: `extracts/v2/tom/UrZ4vpHJ97g_v2.md:72`
- Explanation: Mechanical stop loss rule placing the protective order directly below the swing low, defined where the market thesis is completely invalidated.

### Rule TF-R15: Tom Fair Value Gap (FVG) Entry
> "So, and now it runs up to the fair value gap and that is where you make your entry."
Source GPS: 5Ljfwvtktek | BEGIN

- Context: `extracts/v2/tom/5Ljfwvtktek_v2.md:74`
- Explanation: Following a structure break, price pulls back to retest an unfilled Fair Value Gap, triggering an entry with stop placed beyond the swing invalidation point.

---

## 3. Top 5 Rules Ranked by Fewest NOT_STATED Fields

Each rule is evaluated across the 7 mechanical execution fields: Indicator, Extreme Threshold, Confirming Candle, Entry, Stop, Exit, Timeframe.

| Rank | Rule ID | Description | Count of NOT_STATED Fields | List of NOT_STATED Fields |
|---|---|---|---|---|
| 1 | TF-R03 | Fabio VAH, Big Trades & Delta Confluence Short | 0 | None (all 7 parameters specified) |
| 2 | TF-R04 | Fabio Dynamic Delta Print Re-Entry Short | 0 | None (all 7 parameters specified) |
| 3 | TF-R11 | Tom 20-Point Stop Counter-Trade at 260 | 0 | None (all 7 parameters specified) |
| 4 | TF-R12 | Tom DAX Extreme Open Short with 20-Point Stop | 0 | None (all 7 parameters specified) |
| 5 | TF-R13 | Tom DAX Range Breakdown Volume Level Stop | 0 | None (all 7 parameters specified) |
