# FABIO TRADE MODEL - applied reading of two trade walkthroughs (supervisor, 2026-09-30)

Sources (read in full, canonical transcripts): `raw_transcripts_canonical/0jM5Y31YJak_raw.txt` (his best World Cup
session, NASDAQ, "sell model day") and `raw_transcripts_canonical/8CWKfoSJu3c_raw.txt` (NY scalp, +23k on one short
risking 3.15k). Not a rule list: this is the trade he is teaching, rebuilt as a sequence we can detect on BTC order flow.
Status: DESIGN. Nothing here is backtested yet. Fabio stays a separate layer, never a Tom filter.

## 1. The trade (both videos teach the same one)
1. **Balance first.** Before the move the market is in balance: a profile with fair value in the middle and no direction.
   Price action alone says "wait".
2. **Hidden pressure = the leading signal.** Inside that balance, CVD runs hard one way while price stays flat
   ("the market was balanced ... the pressure ... is pretty huge even before the breakout"). Flat price + falling CVD =
   distribution; flat price + rising CVD = accumulation. This is his "first milestone". **We never built this.**
3. **Trigger = pressure gets a result.** Enter on the first bar where price follows the volume pressure out of balance and
   big trades push in that direction. In 8CWK the same idea appears as a pair: the other side's aggression is absorbed
   ("punch to the wall": effort, no result) and our side's aggression is rewarded (effort, result).
4. **Tiny initial risk.** The stop sits just past the absorbed/breakout extreme. Once the market "explodes" the stop goes to
   breakeven. Most of the edge is the payoff skew: 1:3 to 1:5 per leg, 1:19 on the best leg, 10x session R.
5. **Ride and add.** He adds in the trend direction on each new big-trade confirmation, often funded by the first leg's
   profit ("risking again the profit"). He does not add low in the curve (at discount for a short).
6. **Trail behind order-flow levels.** The stop moves above the "last point of aggression/break", meaning prices where
   sellers showed control. It does not trail by bars or ATR. A retest of a seller-control level that holds is a
   continuation entry.
7. **Exit on flow exhaustion or reversal.** He takes profit when big trades stop pushing (a new, "redistribution"
   balance), when an absorption cluster or the value area low or day low is reached, or when the opposite side's
   aggression breaks the last control level ("if these aggressive buyers take back control, I want to be out").
8. **Day selection and risk budget.** He only presses on directional, volatile days ("you need volatility... not every
   day"). Risk comes from the day's profit after the first win. He stops after a big day.

## 2. Signals we need (all computable from the 1m order-flow bars on F:\MTS\data\orderflow_1m)
| # | Signal | Definition to test (thresholds = grid, counted in PBO) |
|---|---|---|
| S1 | Balance | last N bars (N in 60/120/240 1m) range <= k x ATR(1m,N) and the close near the developing POC of the window |
| S2 | Pressure divergence | inside S1: normalized CVD slope sum(delta)/sum(vol) >= p (or <= -p) while \|price change\| / range <= q |
| S3 | Effort vs result per bar | z(delta) vs z(price change), with the bar's direction relative to delta. ABSORPTION = \|z(delta)\| high & result ~0 or against; CONTROL = high z(delta) & result in the same direction |
| S4 | Big-trade push | net big-trade volume (>= 99th / 99.9th pct size, rolling 30 d) in the trade direction over the last m bars |
| S5 | Breakout | close outside the S1 range in the S2 direction with S4 > 0 (the entry bar) |
| S6 | Control levels | price of the max-aggression bar(s) of each impulse. These are the stop/trail anchors and retest entries |
| S7 | Curve position | price location in the session profile (premium / fair / discount). Shorts not added in discount, longs not in premium |
| S8 | Exhaustion | S4 decays to ~0 for m bars or a new S1 forms (redistribution). Also an opposite CONTROL bar breaking the last S6 |

## 3. What our approach was missing
- **The leading signal (S2).** Every detector we built reacts at swings or at levels. None looks for pressure building
  inside balance before the break. That is where he selects the few directional days that pay for everything.
- **Effort vs result (S3) as the core primitive.** Our cvd_absorption only looks at swings. He reads every bar as effort
  (delta, big trades) against result (price progress), for both sides.
- **Order-flow levels (S6) instead of profile levels.** Stops, trails and re-entries hang on where aggression happened.
  FABIO_OF_REPORT's model used prior-session VAH/VAL/POC with fixed 3R targets.
- **Management is the edge.** Breakeven fast, pyramid on confirmation, trail behind S6, exit on S8. The payoff is a few
  very large winners (1:5 to 1:19) and many scratches. Fixed-horizon returns (FABIO_L1) and fixed 3R targets (FABIO_OF)
  both cut exactly those winners.
- **Costs vs stop width.** FABIO_OF: median gross +0.13R, fee drag 0.66R (0.05-0.2% stops, taker both ways). He trades
  futures with limit entries. Test with the Deribit cost model: maker entry and target, taker stop. Report the fill rate.
- **Market mapping.** NASDAQ futures at the NY cash open. For BTC the analogue is the 13:30 UTC US open. Report NY
  separately, and report trend days vs balance days separately.

## 4. Test plan (when workers resume; one Sonnet job or a DSA spec + Haiku gate)
1. Build S1-S8 as pure functions over the order-flow bars, with tests using hand-built bars.
2. Event study first: how often S1+S2 happen, and whether they predict the direction and size of the next 2-6 h move
   versus balance without divergence. If S2 has no predictive power on BTC, stop there. The model is not portable.
3. Full model simulation, 1m bar by bar:
   - entry S5, first stop past the S3/S5 extreme;
   - breakeven after the first S4 expansion;
   - adds on S4 re-confirmation (max 3);
   - trail on S6, exit S8 or session end;
   - Deribit costs, fill-through rule for limit entries.
   Report win rate, avg R, expectancy, profit factor, max DD in R, and the share of R from the top 10% of trades.
   Include IS/OOS and PBO. Data 2025-01 onward (extend the F: bars back first).
4. If it passes, it goes live on testnet as its own layer (jishu_3 slot).

## 5. Tom (same exercise, not done yet - weekly cap)
TOM_CORE_BT.md (WIP, 5831ead) already shows the same class of problem. Over 2022-2026 historical snapshots Tom reaches
SETUP_FORMING only 19 times. The main reasons:
- The book-imbalance proof cannot be rebuilt from history, so max proof is 6/7.
- The R:R gate blocks most candidates: WAIT_RR 80,847 of 120,892 snapshots.
Next step: read one Tom walkthrough the same way and check whether the gates reflect his trade or over-filter it.
