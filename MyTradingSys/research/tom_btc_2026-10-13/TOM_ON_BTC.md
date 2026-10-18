# Tom on BTC: everything he trades, what we applied right, wrong or never, and the plan to apply it ourselves (2026-10-13)

Session: MTS-2026-10-13-1654Z-CLD-ANA-flow-audit (second task). Base: origin/fast-track 7d92ee47. Docs and cards only.
Operator direction (verbatim, chat 2026-10-13): "I just have a feeling that orde-flow trading is real and Tom is not lying. 'Tom has
never passed that test' yes because we have never applied Tom correctly. We do not need tp prove anything abt Tom here. Orderflow is
real and works on all markets." ... "what else we have missed? What we else we have not applied? in the right way all his shapes all
his uh, setups so why do not we just apply our own brains rather than uh, depending on uh, what we find where we have the core idea
and we have the chart we have the data so let us apply the core idea on the chart and uh, see how it needs to be adjusted in order
to make profitable trades. Focus on that"
Sources read: research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md (parts A and B), conditions/setup_type_rules.md,
market_state_rules.md, zone_identification_rules.md, entry_timing_triggers.md, gap_rules.md, src/main/java/datafeed/SpikeFadeDetector.java,
backtest/fetch_binance_archive.py, backtest/layers/fabio/orderflow_bars.py, RECALL_DAX_V2.md, TRANSLATION_POSTMORTEM_2026-10-12.md.

## 1. The short version
- **We never tested Tom's method.** We tested two copies of it.
  - The old BTC engine traded the wrong places with the wrong exits.
  - The new DAX detector runs on data that has no order flow at all.
- **BTC is the better place to apply Tom.** Every input the DAX feed lacked is free on BTC:
  - real volume;
  - buyer/seller split per minute (klines `taker_buy_volume`);
  - full footprint per minute (`orderflow_bars.py` from aggTrades);
  - a retail long/short sentiment series (Binance metrics, from 2020-09).

  What BTC lacks is an opening auction and Tom's stop size. Fees force stops of at least 0.40 % with taker legs, or 0.20 %
  with a maker entry (TOM_LAYER_V2_SPEC section 11).
- **Plan: apply the idea on BTC charts by eye first, then by code, then adjust on a dev window.** Every number we choose is
  labelled OURS and checked once on data that was never used to choose it. That one check is the only thing that stops
  "adjust until profitable" from fooling us.

## 2. Inventory: everything Tom trades, and what we did with it
RIGHT = applied as he says. WRONG = applied, but not as he says. NEVER = not in any code. Columns: old = the BTC engine
(SetupCandidatesBuilder.java), v2 = the DAX detector (SpikeFadeDetector.java), BTC data = can it be computed on BTC history.

### 2.1 How he decides (the frame)
| Concept | Tom's words / file | old | v2 | BTC data | Status |
|---|---|---|---|---|---|
| Idea, then proof, then risk | "First, you have an idea. Second, you have proof ... third ... risk management" (zQTbdEweG3c:28-32) | proofs counted, no idea step | idea A-C1/A-C2, proofs A-P2/4/5/7 | yes | v2 RIGHT, old WRONG |
| Context first: market state decides the setup (balance, healthy trend, unhealthy trend, transition = wait) | setup_type_rules s1.1, s3; market_state_rules s0-s5 | coarse state from CVD slope; `trend_healthy` blocks the fade | state written as a field, never used | yes | WRONG / NEVER |
| Three trend speeds (fast, normal, creeping) and double distribution | market_state_rules s2.2, s3.2 | no | no | yes | NEVER |
| "Many, many parameters" for counter trades, no fixed count | zQTbdEweG3c:23-26 | 3 proofs required (NO-SOURCE) | count reported, not required | yes | old WRONG |
| Volume node to volume node (idea = travel between nodes) | setup_type_rules s2.1; zone_identification s7.3 | no | no | yes | NEVER |

### 2.2 Where he trades (zones and shapes)
| Concept | Tom's words / file | old | v2 | BTC data | Status |
|---|---|---|---|---|---|
| Session extreme of an oversized impulse leg (his most common trade) | A-C1, spec s2.1 | zones at VAH / swing high, not the leg's top | yes (rank vs prior sessions) | yes | old WRONG, v2 RIGHT |
| Above prior value (day or week) | A-C2: "above the previous day", "above last week's value" | no | coded as above the prior day's HIGH, stricter than his words; makes session S3 unreachable (RECALL_DAX_V2:40-41) | yes | v2 WRONG |
| No liquidity above: thin profile at the top, volume below | A-C3 (k0zm5NYn0IQ:21-22) | no | NOT_IN_DATA on CFD | yes | NEVER |
| P shape whose breakout fails back into balance | A-P3 (n7ZSkjb7JXs:55-59) | no | NOT_IN_DATA on CFD | yes | NEVER |
| b shape pullback on a smaller timeframe | A-P8 (zQTbdEweG3c:144-146) | no | NOT_IN_DATA on CFD | yes | NEVER |
| Old-high ledge taken out (weak highs) | A-P5 (T6hDJcHrVBM:153-155) | no | yes | yes | v2 RIGHT |
| POC / VPOC as reaction and target; VPOC trend = money flow | zone_identification s2 | POC zones yes; VPOC trend no | no | yes | partly |
| VAH/VAL, prior-day value as roadmap ("business zones") | zone_identification s3, s5 | VAH/VAL zones yes; roadmap no | no | yes | partly |
| VWAP: needs context; trend continuation pullback; target for counter trades | zone_identification s4 | VWAP zones yes; `scalp_*` at VWAP has no ledger trade | no | yes | partly WRONG |
| FVG / single prints are targets, not entries | zone_identification s6 | FVG entries removed 2026-10-01 | no | yes | RIGHT |
| LVN as transition, HVN as target | zone_identification s7; TOM-018 | HVN targets yes | no | yes | partly |
| Opening range / initial balance size | zone_identification s8; A-C1 | no | rank of the leg | needs a BTC "open" | WRONG for BTC |

### 2.3 When it is really time (proof)
| Concept | Tom's words / file | old | v2 | BTC data | Status |
|---|---|---|---|---|---|
| Finished auction at the high | A-P1 (k0zm5NYn0IQ:84-86) | yes | NOT_IN_DATA | footprint | old RIGHT, never tested at the right place |
| Fast rejection from the high | A-P2 | wick | yes | yes | RIGHT |
| Inside bar at the top | A-P4 (T6hDJcHrVBM:147-150) | no | yes | yes | v2 RIGHT |
| Selling surplus in delta, big seller in footprint, absorption | A-P6 (k0zm5NYn0IQ:249-250, :19) | delta flip, absorption yes | NOT_IN_DATA | yes, exact | old RIGHT, wrong place |
| Price back below the opening price | A-P7 (l8RZrBfzvp4:100-102) | no | yes | needs a BTC open | v2 RIGHT |
| Order book empty above | A-P9 | live only | no | bookDepth bands from 2023 (proxy) | partly |
| Retail heavily long (sentiment) | A-P10 (paraphrase) | no | NOT_IN_DATA | Binance long/short ratios from 2020-09 | NEVER, and BTC has it |
| Other markets not confirming | A-C4 | no | no | ETH yes; ES/NQ not on disk | NEVER |
| Volume spike 2x over 240 bars | none (B144) | yes | no | - | old WRONG (NO-SOURCE) |
| Unhealthy = CVD divergence | Tom: unhealthy = no volume under the move (spec s8) | yes | no | yes | old WRONG |

### 2.4 How he gets in, out and manages
| Concept | Tom's words / file | old | v2 | BTC data | Status |
|---|---|---|---|---|---|
| Entry A1 at the top | l8RZrBfzvp4:212-214 | limit at zone | yes | yes | RIGHT |
| Entry A2 pullback after the first buying zone is traded through | k0zm5NYn0IQ:316-321 | no | card exists, blocked | yes | NEVER |
| Entry A3 break of the top range | k0zm5NYn0IQ:308-312 | no `tc_short` | card exists, blocked | yes | NEVER |
| Stop above the seller / above the volume bell (a level, not a distance) | A-S1 | 0.1 % floor, later tiny (median 0.082 %) | nearest prior-session high, else 20 DAX points | yes | WRONG |
| Target: start of the impulse; first target at the nearest node / VPOC; a few points early | A-T1..T5 | 2-3.5R window (NO-SOURCE) | impulse start only | yes | WRONG / partly |
| Adds when sellers show again and risk is small | A-M1 | no | no | yes | NEVER |
| Partial when action stalls or before untraded volume | A-M3 | no | no | yes | NEVER |
| Stop to no-loss once a new balance forms below | A-M4 | no | no | yes | NEVER |
| Re-entry after a stop on a fresh signal | A-M5 | no | no | yes | NEVER |
| No trailing at R:R about 6 | A-M2 | 8-bar timeout (NO-SOURCE) | 17:35 exit | yes | WRONG |
| Losing first attempts are part of it (40-45 % hit rate) | spec s3 | every match taken | every attempt counted | yes | v2 RIGHT |

### 2.5 His other trade types (never coded as he describes them)
| Type | Where | old | v2 | BTC fit |
|---|---|---|---|---|
| Trend continuation: pullback to a fair zone (VWAP, value, structure) in a healthy, volume-backed trend; target the next high-volume area | setup_type_rules s5 | `tc_long` at VWAP only; no `tc_short` | no | good: BTC trends, and a value-to-value stop is wide |
| Breakout / break-in: a balance resolves with proof of direction | setup_type_rules s6 | no | no | good |
| Scalp in balance (VWAP/POC rotation) | setup_type_rules s7 | `scalp_*` at VWAP | no | poor: stops too small for BTC fees |
| Gap close (DAX) | gap_rules.md (27 rules), spec s4 | no | parked | none: no BTC gaps (operator 2026-10-11) |

## 3. What else we missed (beyond the table)
1. **Order flow at the right place.** The old engine did read delta and absorption, but at VAH and swing highs, and it was
   blocked in exactly the state Tom fades (spec s6). We never measured order flow at the top of an oversized leg.
2. **Timeframe and cadence.** Tom reads a 5-minute chart and a footprint (n7ZSkjb7JXs:290-293). The old engine decided every
   15 minutes; the v2 detector runs on 1-minute bars with no footprint.
3. **Stops are a level, not a distance.** He puts the stop above the seller or the volume bell; its width is an output. On BTC,
   that level must also be at least 0.40 % away (0.20 % with a maker entry), or the trade is too small for the fees.
4. **His exits are half his method.** Partials before untraded volume, no-loss after a new balance, adds, one re-entry. The fixed
   bracket we tested throws all of that away.
5. **Sentiment and cross-market.** Two of his proofs (retail positioning, other markets not confirming) have direct BTC
   analogues on disk or free (long/short ratios, ETH). Neither was ever used.
6. **The "open".** Tom's spike is measured from a session start. BTC has no auction, but it does have busy starts: 00:00 UTC
   daily open, the US cash open (13:30 / 14:30 UTC, already the session anchor in PROJECT_VISION), the London open and the CME
   week open. Which one plays his role on BTC is an OURS choice to test, not to assume.
7. **Market state as the switch.** Tom picks the trade type from the state (balance, healthy trend, unhealthy trend,
   transition = wait). We built one trade type at a time and never the switch.

## 4. The plan: apply the idea ourselves, on BTC charts and data
Rule for every number from here on: label it SOURCED (Tom's words, file:line) or OURS (our judgement, or tuned on dev).
OURS is allowed.

Windows for this program, fixed here before any data is read:
- **Why not the project's standard split.** The standard split (PRE_REG_VOLUME_2026-10-09.md:23) puts DEV before 2024-07.
  The footprint bars already on JIS-NUC (F:\MTS\data\orderflow_1m, 959k one-minute bars) start 2024-12
  (P1_BREAKDOWNS_20261006.md:13).
- **DEV:** 2024-12-01..2025-03-31. OURS numbers are chosen here. T1 may extend DEV back to 2023-07 by building more
  footprint days.
- **VALIDATION:** 2025-04-01..2025-06-30, read once per frozen config.
- **HOLDOUT:** 2025-07-01..2026-09-30, sealed. Opening it needs your decision (A7).
  - The old Tom BTC test already read the part from 2026-06-26 (B147).
  - So the clean final check is 2025-07-01..2026-06-25, plus forward data from 2026-10-14.

Every variant goes in the trial ledger. Fees net, both fill rules (touch and trade-through).

| Step | What | Who | Done when |
|---|---|---|---|
| T1 Data | Check the footprint bars on JIS-NUC cover DEV + VALIDATION (2024-12..2025-06) and list gaps. Optional: build 2023-07..2024-11 from aggTrades with `orderflow_bars.py`. Plus the Binance long/short ratios (gap G5 fetch). | DSA on the NUC (run) | day count and gap list in the card result |
| T2 Chart lab | A script draws 5-minute BTC charts at candidate moments: an oversized leg from a session start into a new high or low beyond prior value. It overlays the session profile, delta per bar and the footprint at the extreme. It also draws 20 random moments, mixed in blind. Dev window only. | Sonnet (build) | 60 candidate + 20 random PNGs and an index CSV |
| T3 Eye read | You and one Claude reader each mark every chart: take / skip, which Tom concepts are visible (table 2 ids), where stop and target go. Readers do not see each other's marks or the outcome. | you + Sonnet | marks CSV for both readers; agreement per concept |
| T4 What separates | Event study on the marked set and on all candidates in dev: forward MFE/MAE in R with the stop at the structure level (at least 0.40 %), by concept present, against random same-session moments | Sonnet (run) | table: concept, n, mean R, 95 % CI, vs random |
| T5 Encode BTC v2 | Detector on BTC with the concepts that separated: thin top (A-C3), delta surplus and absorption (A-P6), P/b shapes (A-P3, A-P8), plus the v2 OHLC proofs. Entry paths A1-A3, stop at the level, targets at node / impulse start. Flag-gated, default off. | Sonnet (build) | tests green; flag-off output identical |
| T6 Dev backtest + adjust | Fee-net dev run, both fills, maker vs taker entry. Management arms: partial at the node, no-loss after new balance, one re-entry. Each adjustment is a trial row. | Sonnet (run) | DEV table with power; chosen OURS values written down |
| T7 Validation once | Same config on VALIDATION, read once | Sonnet (run) | PASS / FAIL / INCONCLUSIVE (power stated) |
| T8 Other trade types | Repeat T2-T4 for trend continuation (pullback to value or VWAP in a volume-backed trend) and breakout/break-in | Sonnet | same tables |
| T9 Testnet | Only after T7 passes: shadow, then testnet trades | supervisor | GO_LIVE_BAR counts |

What this replaces: the Tom v2 DAX chain (cards tom-profile-shape-parity, tom-encode-fade-profile-proofs,
tom-v2-dax-dev-backtest, tom-dax-backtest) is parked by operator direction 2026-10-13; FDAX data is not bought (q11).
The DAX spec (TOM_LAYER_V2_SPEC) stays the source for Tom's words; its section 11 stop rule is the BTC cost floor.

## 5. Where this can still go wrong
- **Adjusting on outcomes is overfitting by default.** One untouched check per stage is the defence. If VALIDATION is looked at
  twice, it stops being a check.
- **Eye reads can drift toward winners.** That is why the chart lab mixes in random moments and hides the outcome.
- **Order flow can be real and still not cover BTC fees** at the stop sizes it implies. Fabio's model was positive before fees
  (+0.13 R median) and negative after them (FABIO_OF_REPORT.md:127-128). T4 tells us early, before any build.
- **A BTC "open" may not carry the liquidity effect Tom relies on.** T4 compares the session starts against each other and
  against no anchor at all.
