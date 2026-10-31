# Volume-profile video BB3c8visnkI: does MTS already know this, is it used for edge, how to apply (2026-10-31)

Video: Tom Vorwald EN, "How to Use Volume Profile Like a Pro! (2026)", published 2026-10-30. Extract: `extracts/processed/tom/extract_BB3c8visnkI.md`
(19 quotes, verify_extract_quotes exit 0; index TOM-271..TOM-289). Spec addendum: `TOM_LAYER_V2_SPEC.md` section 20.
Checked against trunk at 119ddb7d0 (2026-10-31). Every "tested" cell names the file that holds the number; nothing below is a new result.

## 1. Concept by concept

| # | Concept (his words, TOM id) | MTS knows it? (where) | Used for edge? (result) | How to apply exactly (today) |
|---|---|---|---|---|
| 1 | Profile = volume at price; POC, value area = 70 % [TOM-271, TOM-277] | YES. FORMULAS.md 18.1 (bin grid, POC, 70 % value area, worked examples); engine `VALUE_AREA_PCT`; `SetupCandidatesBuilder.extractZones`; `vp_pivot_probe.py` | TESTED, NEGATIVE: touching POC / VAH / VAL is a coin flip before fees (gross -0.04..+0.01 R), -0.19..-0.25 R net; 46/48 streams = placebo, 2 worse (PHASE2_RESULT.md, 2026-10-09; n >= 1055 per stream, 2022-2026, every year negative) | Context only. Draw prior-day and weekly POC/VAH/VAL per 18.1. Never a limit-order entry on the touch: that trade is proven fee-negative on BTC |
| 2 | Low volume nodes = thin areas, price zips through [TOM-272] | YES. Fabio v3 `lvn_levels` / `select_lvn` (`layers/fabio/v3/signals.py`); guidance matrix T2/T2b (`matrix_q33.py`) | TESTED, NEGATIVE: LVN traverse (continuation) and LVN reject (fade) both about 0 gross, -0.10 % net at 60 min, 0 of 186 cells survive (MATRIX_REPORT.md, 2026-10-12) | Context only. An LVN is a boundary to read, not a trigger |
| 3 | LVN behaviour matters more than POC [TOM-276]; crossed fast + accepted above = new fair price, old range left [TOM-273, TOM-274] | PARTLY. The spec reads it (CONCEPTS.md A2, "empty areas get filled"); SpikeFadeProfile A-P3 has the mirror (failed break accepted back inside). The forward case, "accepted away from the old value", is NOT encoded anywhere | NOT TESTED as a filter. Only the entry-on-touch was tested (row 1) | Candidate invalidation rule, OURS, untested: after price crosses an LVN and closes N bars on the far side, the old-value return target is stale; drop it. Needs a card before anyone uses it (card below, part B) |
| 4 | Market returns to liquidity; balance profiles 60-70 % of the time; breakout runs away only ~30 % [TOM-275, TOM-278, TOM-280] | YES as a claim (CONCEPTS.md A1.1 quotes TOM-046, the same 70/30 from another video). No MTS number exists for it | NOT TESTED. PHASE2 tested a +-1 ATR barrier touch, which is not "did price return to value" | This is the one testable new claim. Card below, part A: count it on BTC with a placebo, pre-registered |
| 5 | From the edge of value, counter-trade back to equilibrium [TOM-279] | YES. Family A imbalance fade (TOM_LAYER_V2_SPEC section 2; `SpikeFadeDetector`, `SpikeFadeProfile`, flag `-Dmts.spikeFade`) | NOT FEE-NET POSITIVE anywhere. Tom core BTC runs: net -0.30 R (0929), -2.91 R (1007); DAX chain parked (no FDAX data); Tom-on-BTC T5/T6 cards blocked behind the eye read | Stays as built: flag-gated candidate, no live firing. The video adds no proof, stop or target to it |
| 6 | Daily profiles use the cash session only [TOM-281] | KNOWN gap. Profile parity NOT_IN_DATA for GER40; BTC has no cash session; engine anchors to 00:00 UTC (FORMULAS 18.4 `session`, `prior_day`) | n/a | OURS: BTC day = 00:00 UTC; label every "daily value" as a UTC-day value, never as his cash-session value |
| 7 | After an excess move, equilibrium (value + POC) shifting = trend change [TOM-282..TOM-284] | NO encoding. Nearest: `NakedPocTracker.java` (daily POCs, naked-POC revisit at 0.3 %) is loaded into zones but has NO backtest line in LAYERS.md or FORMULAS.md | NOT TESTED | Context read for the side (CONCEPTS A1.2). Rule to test later, OURS: day D value area entirely above day D-1 value area after D-1 was a down day = "shifted up". No number, no gate until tested |
| 8 | Gaps need not close when equilibrium shifted; "gap always closes" is problematic [TOM-285, TOM-286] | YES. `conditions/gap_rules.md` (27 rules, DAX-only; operator 2026-10-11: no BTC gaps since CME went 24/7); spec family C parked (1 trade) | NOT TESTED (no DAX data) | No BTC application. Family C gets the condition "prior-day equilibrium not shifted by the gap day"; still parked |
| 9 | VAH test: rejection first, then acceptance of higher prices [TOM-287, TOM-288] | YES. Same shape as TOM-011 failed break / A-P3 (SpikeFadeProfile) | Covered by rows 1 and 5: no fee-net result | No new rule |

## 2. Straight answers
- **Does MTS already know this?** Yes, all nine ideas are in the sources and seven are in code (rows 1, 2, 5, 6, 8, 9 and the POC tracker in 7). The video is a beginner summary of concepts the layer already holds. New in words only: the forward "accepted away" case (row 3) and the stated 60-70 / 30 split (row 4).
- **Are we using it to find edge?** We tried the direct version twice and it failed on BTC fee-net: the profile-level touch (PHASE2, 48 streams) and the LVN trigger (Q33, 186 cells). Both are coin flips before fees. Nothing from volume profile fires live. The one piece never measured is his central claim itself: how often price returns to value after leaving it.
- **How to apply it exactly, today:** as a context read, not a trigger. Order: (1) prior-day and weekly POC/VAH/VAL per FORMULAS 18.1; (2) is price inside value (balance) or outside (imbalance); (3) if outside, has it been accepted there (closes beyond the LVN) or not; (4) only then does any layer's own trigger count. No volume-profile level is an entry or a stop on its own.

## 3. Card filed (test before any rule)
`tom-vp-return-to-value-count` (SONNET, p2, layer tom). PRE-REG first, then run; no numbers claimed here.
- Part A, his 70/30: on BTCUSDT 1m 2022-01-01..2026-10-30 (same file set as PHASE2), per UTC day D: prior-day value area per FORMULAS 18.1 on 5m bars. Event = first 5m close of day D outside prior value (above VAH or below VAL). Outcome = does any later 5m bar of day D trade back to the prior POC (return) or not (run away). Report the return share with a day-block bootstrap CI (18.7), split by year, and the placebo: the same event rule on a value area shifted by d x ATR14(1h), d from the 18.6 cycle. His claim is 70 % return. A share near the placebo share means the number is a property of any band, not of value.
- Part B, accepted away: condition the Part A outcome on "N consecutive 5m closes beyond the LVN side of value" for N in {3, 6, 12}, N NO-SOURCE and reported for all three, never picked by outcome. If the return share collapses after acceptance, row 3 becomes a sourced-shape, OURS-threshold invalidation rule for family A's return target; if it does not, the rule is dropped.
- Done when: RESULT.md with both tables, CIs, placebo, per-year split; LAYERS.md tom line gets the one-line verdict; no code outside `MyTradingSys/backtest/` and its test; test fails on a stub first.

## 4. Noticed
- `NakedPocTracker.java` is live-loaded into zones with a 0.3 % revisit threshold and has never been backtested or labelled (no LAYERS.md line, no FORMULAS section). Not touched here; the card above reports naked-POC return as a side column so it gets a first number.

## 5. Simulator desk: the concepts as clickable settings, first grid (2026-10-31, DEV 2022-04-01..2024-06-30, BTCUSDT)
Study `research/sim_desk/studies/tom_vp.py` (test `test_tom_vp.py`, 7 tests, failed before the study existed). Each row is one desk run, ledgered in
`layer_lab/TRIALS.md` (tries 1-12) and exported to `sim_desk/results/desk-tom_vp-*.json` for the hosted page. Fees 0.02/0.05 % + 0.02 % slip,
stop 1 x ATR14(1h), market entry next 5m bar, exit at the POC (or one value-area width for ACCEPT) or when the day/week ends. All OURS except the
concept each row tests. The verdict is the desk's (filled trades, 95 % day-block range).
| try | Concept on trial | Setting | n | mean net R | 95 % range | win | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | returns to value (TOM-275/280) | prior day, RETURN, no exit rule | 1054 | -0.224 | -0.300..-0.148 | 45 % | FAILED |
| 2 | + accepted away = drop the idea (TOM-273/274) | RETURN, exit after 6 closes outside | 1054 | -0.262 | -0.314..-0.208 | 46 % | FAILED |
| 3 | + shifted equilibrium filter (TOM-282..284) | RETURN, n6, skip against migration | 918 | -0.258 | -0.314..-0.203 | 47 % | FAILED |
| 4 | same with our R target | RETURN, n6, target 2R | 1038 | -0.254 | -0.315..-0.192 | 40 % | FAILED |
| 5 | counter-trade from the value edge (TOM-279) | FADE, no exit rule | 1765 | -0.238 | -0.284..-0.193 | 58 % | FAILED |
| 6 | FADE + acceptance exit + migration filter | FADE, n6, WITH | 1812 | -0.257 | -0.296..-0.218 | 46 % | FAILED |
| 7 | accepted away = new fair price, go with it (TOM-274) | ACCEPT after 3 closes | 1640 | -0.250 | -0.317..-0.176 | 36 % | FAILED |
| 8 | same | ACCEPT after 6 closes | 1420 | -0.202 | -0.277..-0.125 | 36 % | FAILED |
| 9 | same | ACCEPT after 12 closes | 1180 | -0.264 | -0.339..-0.181 | 36 % | FAILED |
| 10 | ACCEPT only with the migration | ACCEPT n6, WITH | 1247 | -0.216 | -0.297..-0.133 | 36 % | FAILED |
| 11 | weekly value, returns to value | prior week, RETURN, n6 | 148 | -0.172 | -0.397..+0.083 | 37 % | NOT ENOUGH DATA |
| 12 | weekly value, accepted away | prior week, ACCEPT n6 | 365 | +0.081 | -0.206..+0.385 | 23 % | NOT ENOUGH DATA |
Reading (OURS): every daily-value idea loses 0.20-0.26 R per trade with the whole 95 % range below zero, the same fee-sized loss PHASE2 found for level
touches; the edge fade wins 58 % of the time and still loses (small wins, full stops); the acceptance exit and the migration filter change nothing
beyond noise. The two weekly rows are unresolved, not positive: row 12 has 365 trades, a 23 % win rate and a range that spans zero. The 70/30 return
share itself is not a trade result and stays with card `tom-vp-return-to-value-count`.
