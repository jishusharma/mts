# Tom & Fabio Rules: Indicator Extreme + Confirming Candle + Stop (Argon Twin)

This document compiles 15 mechanically testable rules mined from Tom Vorwald and Fabio Valentini source extractions (`extracts/v2/tom/` and `extracts/v2/fabio/`).
Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.
All verbatim quotes and Source GPS tags have been validated against transcript baselines with `scripts/dev/verify_extract_quotes.py`.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| TF-ARG-01 | Initial Balance (IB) Volatility Contraction Breakout | Regular trading first 30m initial balance range breakout | Candle closes above initial balance breakout | Long entry on breakout candle close | Equal distance 1:1 measuring risk amount | 1:1 Risk-to-Reward target | 30-minute Initial Balance / Daily | `extracts/v2/fabio/StaphlRH8NQ_v2.md:198` |
| TF-ARG-02 | Initial Balance & Value Area to POC Retest | First 15 to 30 min IB established, price retraces to order block | Candle holds support between Value Area and POC | Buy execution in order block between Value Area and POC | Candle close below Value Area Low (VAL) | Target at first protection level (1:2 to 1:2.5 R:R) | 15-minute / 30-minute session profile | `extracts/v2/fabio/cUTsoU-15Tc_v2.md:28` |
| TF-ARG-03 | Initial Balance Buyer Protection & Absorption | Retrace to IB Value Area with aggressive seller absorption | Candle showing buyer aggression protecting area | Buy entry on confirmed buyer protection | Stop loss below the protected area | Target at protection level (65% to 70% probability) | 15m / 30m New York session | `extracts/v2/fabio/cUTsoU-15Tc_v2.md:46` |
| TF-ARG-04 | Volume Ledge Extreme & Aggressive Seller Delta Print | Price retests volume ledge from high volume node to low volume node | Candle body printing aggressive seller orders and absorbed buyers | Limit order sell entry at dynamic volume ledge level | NOT_STATED | Next swing point (1:3 to 1:5 R:R) | New York session | `extracts/v2/fabio/06R-ebyOhDI_v2.md:51` |
| TF-ARG-05 | Order Book Liquidity Wall Breakout & Buyer Reload | Resting liquidity wall absorbed and reloaded with aggressive buyers | Breakout candle through resting liquidity level | Long entry at breakout protected below reload level | Stop loss placed below reload level / next liquidity area | First TP at major liquidity, 2nd/3rd at resting liquidity | Order book / DOM intraday | `extracts/v2/fabio/FawPrRUGNpk_v2.md:234` |
| TF-ARG-06 | Multi-touch Absorption & Squeeze Setup | Level tested 3 to 5 times holding absorbed sellers | Rejection candle with absorbed sellers and buyer reward | Limit / market entry on squeeze test at third touch | Stop loss below the support area | Target 1:4.9 to 1:5 R:R (or 1:3.5) | Intraday / Session | `extracts/v2/fabio/Is1HvdfQm5c_v2.md:701` |
| TF-ARG-07 | Breakout Limit Retest with Stop Below Aggression | Market absorption followed by buyer breakout candle | Breakout candle with buyers at the top | Limit order entry at breakout level on retest | Stop loss between buyer aggression / below the area | Trailing stop to zero / 1:3.5 target | Intraday / Order flow | `extracts/v2/fabio/Is1HvdfQm5c_v2.md:1452` |
| TF-ARG-08 | Virgin Area Retest in Momentum Trend | Strong directional trend closing beyond area without test | Retest candle testing virgin area holding support | Long entry on first test of virgin area | Covered below the support areas | 50% target at partial profit, remainder left running | Intraday / Profile framing | `extracts/v2/fabio/Khgj5q1-ln8_v2.md:49` |
| TF-ARG-09 | P-Shape Profile / Value Area Low Hook Rejection | Value building on upside (P-shape), price pulls back to VAL | Hook pattern: failed breakdown candle rejecting below VAL | Re-entry long in trend direction on hook confirmation | Trail stop to break even on breakout | Target 1:2 to 1:5 R:R | New York session | `extracts/v2/fabio/Pz8f0wWW12M_v2.md:57` |
| TF-ARG-10 | Daily Market Profile Liquidity Invalidation & Footprint Execution | Price tests daily profile structural liquidity extreme | Smaller footprint chart confirmation showing buyer liquidity push | Counter / trend entry on smaller footprint confirmation | Stop loss placed below the last liquidity (10 ticks) | Predefined target at profile resistance (70 ticks / 1:7 R:R) | Daily profile context / Footprint entry | `extracts/v2/tom/3o1VVsfBmmU_v2.md:132` |
| TF-ARG-11 | Value Area Extreme Liquidity Squeeze Buy | Market reaches price area of lowest liquidity / bid support zone | Signal candle holding bid support / reversal candle | Long entry at predefined support price area | Stop loss below the bid / below the business zone | Take-profit set above the highs / Value High area | Intraday | `extracts/v2/tom/4MoNjEQ2Dd8_v2.md:107` |
| TF-ARG-12 | DAX Pre-Market Open High Sweep & Balance Breakdown | Market takes out pre-market highs (18,258) and builds negative balance | Rejection breakdown candle flushing below pre-market highs | Short entry in DAX on negative balance confirmation | Stop loss placed at 18,257 / logical level above high | Intermediate target at low volume range (411 area) | DAX pre-market / morning cash open | `extracts/v2/tom/ujedEcmvBMk_v2.md:148` |
| TF-ARG-13 | DAX Pre-Session Liquidity Sweep Short | Pre-market impulsive move up to liquidity extreme | Breakdown candle pushing liquidity below impulse start | Short entry in DAX future before cash open | Stop loss set above the bell / above last major trades | Target at start of corresponding impulse | Pre-market DAX session | `extracts/v2/tom/n7ZSkjb7JXs_v2.md:155` |
| TF-ARG-14 | S&P Pre-Session Swing Low Liquidity Limit Buy | Market pulls back to pre-session volume levels (7,443) | Sideways acceptance candle structure | Limit buy order at 7,443 slightly below volume levels | Stop loss placed at 7,420 (below last swing low, 23 pts) | Take profit set at 7,513 (3.04:1 R:R, 0.414R EV) | Pre-session / Intraday | `extracts/v2/tom/QClPWDJ-BrU_v2.md:98` |
| TF-ARG-15 | Squeeze Exhaustion B-Profile Short Re-entry | Exponential volume surge halts, market builds B-profile balance | Breakdown candle below balance zone with lower volume | Re-entry short upon B-structure balance formation | Stop loss above the level / $40-$35 distance ($90 max) | Target at last largest volume node ($250 price level) | 1-hour chart / Multi-day | `extracts/v2/tom/tS6ZEiHj8gQ_v2.md:103` |

---

## 2. Verbatim Quotes and Source Citations

### Rule TF-ARG-01: Fabio Initial Balance Volatility Contraction Breakout
> "measuring the session after the breakout that close above this breakout, it's already blindly without order flow, without option flow, without logic of the strategy confirmation 13.5%"
**Source GPS: StaphlRH8NQ | MIDDLE**
- Source file: `extracts/v2/fabio/StaphlRH8NQ_v2.md:198`

### Rule TF-ARG-02: Fabio Initial Balance Value Area to POC Retest
> "the most sensitive level after you have this is the level contained between the value area and the PC. This is our real block of orders."
**Source GPS: cUTsoU-15Tc | BEGIN**
- Source file: `extracts/v2/fabio/cUTsoU-15Tc_v2.md:28`

### Rule TF-ARG-03: Fabio Initial Balance Buyer Protection & Absorption
> "when you have aggression of the buyers for example here okay they are protecting the area you can consider a buy with a stop loss below that goes to the protection level."
**Source GPS: cUTsoU-15Tc | END**
- Source file: `extracts/v2/fabio/cUTsoU-15Tc_v2.md:46`

### Rule TF-ARG-04: Fabio Volume Ledge Extreme & Aggressive Seller Delta Print
> "So, after this candle, the situation is super clear. So, you can already put a limit order here."
**Source GPS: 06R-ebyOhDI | END**
- Source file: `extracts/v2/fabio/06R-ebyOhDI_v2.md:51`

### Rule TF-ARG-05: Fabio Order Book Liquidity Wall Breakout & Buyer Reload
> "put your stop loss below the next liquidity area"
**Source GPS: FawPrRUGNpk | BEGIN**
- Source file: `extracts/v2/fabio/FawPrRUGNpk_v2.md:234`

### Rule TF-ARG-06: Fabio Multi-touch Absorption & Squeeze Setup
> "covering yourself below the area this is the squeeze setup"
**Source GPS: Is1HvdfQm5c | BEGIN**
- Source file: `extracts/v2/fabio/Is1HvdfQm5c_v2.md:701`

### Rule TF-ARG-07: Fabio Breakout Limit Retest with Stop Below Aggression
> "and you have buyers at the top you have this breakout you can put a limit order this level with"
**Source GPS: Is1HvdfQm5c | END**
- Source file: `extracts/v2/fabio/Is1HvdfQm5c_v2.md:1452`

### Rule TF-ARG-08: Fabio Virgin Area Retest in Momentum Trend
> "The first setup that I will be able to take is the test of this virgin area."
**Source GPS: Khgj5q1-ln8 | END**
- Source file: `extracts/v2/fabio/Khgj5q1-ln8_v2.md:49`

### Rule TF-ARG-09: Fabio P-Shape Profile / Value Area Low Hook Rejection
> "And when you break this level, you can decide to put your stop loss to break even."
**Source GPS: Pz8f0wWW12M | END**
- Source file: `extracts/v2/fabio/Pz8f0wWW12M_v2.md:57`

### Rule TF-ARG-10: Tom Daily Market Profile Liquidity Invalidation & Footprint Execution
> "my stop loss in this case let's say is 10 ticks"
**Source GPS: 3o1VVsfBmmU | MIDDLE**
- Source file: `extracts/v2/tom/3o1VVsfBmmU_v2.md:132`

### Rule TF-ARG-11: Tom Value Area Extreme Liquidity Squeeze Buy
> "The stop loss goes below the last low here"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**
- Source file: `extracts/v2/tom/4MoNjEQ2Dd8_v2.md:107`

### Rule TF-ARG-12: Tom DAX Pre-Market Open High Sweep & Balance Breakdown
> "I placed the stop at 257 because I assumed the market was done up there and had fixed everything."
**Source GPS: ujedEcmvBMk | BEGIN**
- Source file: `extracts/v2/tom/ujedEcmvBMk_v2.md:148`

### Rule TF-ARG-13: Tom DAX Pre-Session Liquidity Sweep Short
> "which is why the stop loss was set above the bell"
**Source GPS: n7ZSkjb7JXs | END**
- Source file: `extracts/v2/tom/n7ZSkjb7JXs_v2.md:155`

### Rule TF-ARG-14: Tom S&P Pre-Session Swing Low Liquidity Limit Buy
> "The trade has an entry at 7,443, stop loss 7,420, take profit 7,513."
**Source GPS: QClPWDJ-BrU | MIDDLE**
- Source file: `extracts/v2/tom/QClPWDJ-BrU_v2.md:98`

### Rule TF-ARG-15: Tom Squeeze Exhaustion B-Profile Short Re-entry
> "the profit target should be where the last largest volumes occurred"
**Source GPS: tS6ZEiHj8gQ | MIDDLE**
- Source file: `extracts/v2/tom/tS6ZEiHj8gQ_v2.md:103`

---

## 3. Top 5 Rules Ranked by Fewest NOT_STATED Fields

Each rule is evaluated across the 7 mechanical execution fields: Indicator, Extreme Threshold, Confirming Candle, Entry, Stop, Exit, Timeframe.

| Rank | Rule ID | Description | Count of NOT_STATED Fields | List of NOT_STATED Fields |
|---|---|---|---|---|
| 1 | TF-ARG-14 | Tom S&P Pre-Session 7443 Limit Buy (SL 7420, TP 7513) | 0 | None (all 7 parameters specified) |
| 2 | TF-ARG-10 | Tom Daily Profile Invalidation Footprint Entry (SL 10t, TP 70t) | 0 | None (all 7 parameters specified) |
| 3 | TF-ARG-01 | Fabio Initial Balance Volatility Contraction Breakout | 0 | None (all 7 parameters specified) |
| 4 | TF-ARG-02 | Fabio Initial Balance VA-to-POC Retest Long | 0 | None (all 7 parameters specified) |
| 5 | TF-ARG-03 | Fabio IB Buyer Protection Long (SL Below Protected Area) | 0 | None (all 7 parameters specified) |
