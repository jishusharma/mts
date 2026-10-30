# PRE-REG: does price return to prior-day value after leaving it? (Tom's 70/30 claim, a COUNT, not a trade test)

Card `tom-vp-return-to-value-count`. Written 2026-10-31 BEFORE any run. Template: `MyTradingSys/backtest/PRE_REG_TEMPLATE.md` (items 0a-0g, 1-12).
Labels: SOURCED = a quote or file:line; OURS = our choice, fixed here; NO-SOURCE = a measurement choice named in FORMULAS section 18, not tuned.
No rule, gate or entry is added by this study. `prereg_gate.py` (count-only R-edge gate: needs sd of per-event R and a cost) does not apply: there is no R, no cost, no edge claim here. DECISION (OURS): skipped, reason written.

## The claim (SOURCED)
- "But unfortunately that is only the case about 30% of the time and the other 70% he will try and strive to run back here": `extracts/processed/tom/extract_BB3c8visnkI.md:38` (index TOM-278..TOM-280; `TOM_LAYER_V2_SPEC.md:492`).
- "especially 60 to 70% of the time, we have so-called balance equilibrium profiles": `extract_BB3c8visnkI.md:31`. Value area = 70 % of volume: `:28`.
- Same 70/30 claim from another video (TOM-046), quoted in CONCEPTS A1.1. His number is a claim, never a gate.

## Definitions (all on 5m bars, UTC days)
- Prior-day value (NO-SOURCE bin w = 10 USD, VA 70 %): `build_profile` of the 5m bars of UTC day D-1 (`FORMULAS.md:422` section 18.1, `vp_pivot_probe.py:101`). Gives POC price, VAH, VAL. BTC day = 00:00-24:00 UTC (OURS; he uses a cash session, TOM-281, BTC has none; every "daily value" here is a UTC-day value).
- Event (OURS, from VP_VIDEO_CONCEPT_CHECK section 3): the first 5m bar of day D whose CLOSE is above VAH or below VAL. One event per day at most. Uses bars up to that close only.
- Outcome RETURN (OURS): any LATER 5m bar of day D (strictly after the event bar, up to the 23:55 bar) whose high-low range contains the prior-day POC price. Else RUN-AWAY. A day with no event = NO-EVENT (counted, not in the share).
- Side column "back inside value" (OURS, secondary, fixed now): any later 5m bar of day D that CLOSES inside [VAL, VAH].
- Placebo (NO-SOURCE, `FORMULAS.md:482` section 18.6): the same profile levels (POC, VAH, VAL) all shifted by `d x R_ref`, `R_ref` = ATR14 of 1h bars (plain SMA, FORMULAS section 12, `vp_pivot_probe.py:116`) of the last 1h bar closed at or before 00:00 UTC of day D (no look-ahead); d cycles (-3,-2,-1,-0.5,0.5,1,2,3) by (day index in the study) mod 8. Same event and outcome rule. Pooled over all d is the primary placebo; per-d rows are descriptive. Adaptation of 18.6 (OURS): "refresh_index" = day index because levels are refreshed once per day.
- Part B accepted away (N NO-SOURCE, set {3, 6, 12} from the card, all three reported, NEVER picked by outcome; d never tuned): among events with at least N-1 later bars in the day, accepted_N = the event bar and the next N-1 bars all CLOSE beyond the same edge (above VAH, or below VAL). OURS simplification: "beyond the LVN side of value" is read as beyond the value-area edge; no LVN is built (the 18.1 profile has no LVN definition). The outcome for accepted events = a bar STRICTLY AFTER the N-th close touches the POC (decision point = the N-th close; no look-ahead). Reported with the same placebo (shifted band) and difference CI. Baseline for comparison = the Part A share.
- Naked-POC side column (SOURCED threshold, OURS use): `src/main/java/datafeed/NakedPocTracker.java:26` revisit = price within 0.3 % of a previous day's POC. Column = share of ALL days D (event or not) on which any 5m bar of day D touches the D-1 POC exactly, and on which a bar's range comes within 0.3 % of it, with the same placebo shift. This is not the older-POC chain of the live tracker (stated in RESULT.md).

## Statistics (SOURCED method `FORMULAS.md:486` section 18.7)
Return share = returns / events. 95 % CI = day-block bootstrap: days resampled with replacement, 2000 resamples, numpy `default_rng(20261009)`, share = sum over resampled days / events in them (`vp_pivot_probe.boot_stat`, line 262). Difference real minus placebo uses the SAME resampled days. Per-year split (2022, 2023, 2024 H1). His 70 % is shown against the CI; no pass/fail threshold.

## Template items
- 0a Cost: NA, no trade, no cost (nothing from `fees.py` is used). Evidence: this file, header.
- 0b Gross: NA, a count of a claim. A share near the placebo share means the number is a property of any band, not of value (card note).
- 0c Record: the source's claim has no dated calls; it is a stated frequency. Hypothesis only; no core. Evidence `extract_BB3c8visnkI.md:38`.
- 0d Data: needs 5m high, low, volume only. BTCUSDT 1m 2022-01..2024-06 in `Dumps/backtest/raw_1m_2022/klines`, read through `vp_pivot_probe.load_bars` (line 326). A day whose 5m set is incomplete (missing minutes) is dropped and counted (NOT_IN_DATA, never zero). No aggressor/OI input used.
- 0e Power: about 910 dev days, at most one event each (expected 850-910 events). Binomial SE at p=0.7 is sqrt(0.7*0.3/900)=0.0153, day-block CI about +-3 pp, so a gap of about 4-5 pp from the placebo is detectable. Part B N=12 keeps fewer events; if n < 100 the row says UNDERPOWERED, never "no effect".
- 0f Kill: this is a count, not an edge test. Result classes written now: real minus placebo difference CI contains zero = "a property of any band, not of value"; share CI excluding 70 % = "his number does not reproduce on BTC UTC-day value". No redesigns; N and d are not tuned. Row 3 of the concept check becomes a candidate rule only if Part B's share after acceptance is below the Part A share with a difference CI excluding zero, and then on a separate card.
- 0g Operator intent: not the operator's own levels; this is Tom's claim on BTC. Not applicable; labelled OURS where the encoding differs from his (UTC day, value-area edge for LVN).
- 1 Source home: Tom Vorwald, volume profile, daily balance profiles, cash session (TOM-281); here BTCUSDT 5m, UTC day, holding = until 24:00 UTC. Evidence `extract_BB3c8visnkI.md:31,38`.
- 2 Ground truth ledger: none for this claim (a frequency). NOT_IN_DATA. Evidence: the extract holds no dated trades for it.
- 3 Recall / fire rate: fire rate = event days / days, reported (expected near 100 % because BTC trades 24/7). Recall NA.
- 4 Data inputs: 5m high, low, volume only. Evidence `vp_pivot_probe.py:326`.
- 5 Profile parity: builder is `build_profile`, parity-tested by worked A/B/C in `test_vp_pivot_probe.py`; vs his drawn levels NOT_IN_DATA for BTC (`research/tom_transfer_2026-10-11/PROFILE_PARITY.md`). Bin 10 USD vs engine about 5 USD: accepted difference (`FORMULAS.md:422`).
- 6 Cost: NA (no trade).
- 7 Fills: NA. "Return" = range touches POC; a limit order at the POC would need more (not claimed).
- 8 Exits: NA.
- 9 Null: the shifted-band placebo with the same day window and the same event/outcome rule.
- 10 Power: see 0e.
- 11 Holdout: DEV only, 2022-01-01..2024-06-30 (`MyTradingSys/backtest/splits.py:4`, DEV_END 2024-07-01 exclusive, enforced with `assert_dev_only`). DECISION (OURS): the card text says 2022-2026 but also "DEV data only, no VALIDATION or HOLDOUT reads"; the conservative reading wins. VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) are not read. Trials: 1 primary + 3 Part B values + descriptive per-d and two side columns; no extension planned.
- 12 Stratified readout: per year (2022, 2023, 2024 H1) and by up-leave vs down-leave; session split NA (UTC day is the unit).

## Look-ahead guard
Value for day D uses only bars of day D-1. The event uses bars up to its own close. R_ref uses 1h bars closed at or before 00:00 of D. Outcome bars come after the event/decision bar. `scripts/dev/lookahead_lint.py` is run before shipping.
