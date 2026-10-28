# Wiring audit: Tom, Fabio, Habib (every SOURCED rule vs layer code, params, tests)

Card `extracted-rules-wiring-audit-tom-fabio-habib`, 2026-10-28, MTS_Doctor (Sonnet). Read-only audit: no layer code, params or backtests changed. Sibling: Malkan/Krown card (not here).
Table: `WIRING_TOM_FABIO_HABIB.csv` (one row per sourced rule, columns rule, quote, quote file:line, code file:line, param label, test, verdict). Quotes checked with `scripts/dev/verify_extract_quotes.py` on `QUOTES_USED_TOM_FABIO.md` (exit 0, 442 fragment blocks).

## 1. What a row is
- Tom: one row per quote id TOM-001..TOM-270 in `TOM_VERBATIM_INDEX.md` (270). Quote = index excerpt (that file is the authority); rule = the heading in `conditions/*.md` (or `runtime/compiled_engine.md` for TOM-214) that cites the id; `session_timing_rules.md` has no Tom quote ids (it is crypto research), so it has no rows.
- Fabio: one row per rule in the 10 processed extracts (110, `extracts/processed/fabio_valentini/`) plus FAB-001..FAB-054 from the 4 staged extracts (54, `extracts/_staged_2026-09-27/`; FAB-002..007 are coded by name in `layers/fabio/`).
- Habib: 12 rows: 7 from the imbalance-candle study (`imbalance_qriptal_2026-10-16`, quotes from the qriptal transcripts) and 5 from the plan note (`habib_plan_imbalance_2026-10-20`, Discord screenshots, no transcript).
- Verdict: `wired` = the rule is in code (extent `full` or `partial`; partial means part of the rule is missing, see note); `unwired-worth-wiring` = testable on data we hold, not coded; `not-worth-wiring` = psychology, sizing, DAX-only (gap rules), needs L2 book history we do not have, or no mechanic.
- Where wired: Tom = the Java detector `SetupCandidatesBuilder.java` and the DAX/BTC harness `tom_dax_bt.py`; Fabio = the offline backtest layer `layers/fabio/` (no live orders; the live shadow emitter is a `.new` file); Habib = research scripts only.
- Param labels: SOURCED = the rule is his; thresholds are OURS unless a quote gives the number (`FABIO_V3_SPEC.md` 7.1 P-ids are cited for Fabio).

## 2. Counts by verdict

| Trader | wired (full) | wired (partial) | unwired-worth-wiring | not-worth-wiring | rows |
|---|---|---|---|---|---|
| Tom | 46 | 62 | 57 | 105 | 270 |
| Fabio | 48 | 42 | 14 | 60 | 164 |
| Habib | 0 | 5 | 5 | 2 | 12 |
| **all** | 94 | 109 | 76 | 167 | 446 |

Reading: Tom is wired where the detector already cites ids (stop TOM-072/073/074, target HVN TOM-018/102, balance TOM-030/031, unhealthy trend TOM-056/140, side TOM-142, zones TOM-144/166). Fabio v3 covers most order-flow rules; his heat-map rules (L2) and prop-firm risk rules are not-worth-wiring. All 56 Tom gap rows are not-worth-wiring (DAX only, held).

## 3. Unwired-worth-wiring, ranked (H first)
Rank = explicit mechanic + data we hold + not already tested negative. H: the quote is clear and the code removed or skipped it on a labelling ground. Wiring means a pre-registered test first, not a live change.

| rank | id | trader | rule | what is missing |
|---|---|---|---|---|
| H1 | TOM-023 | Tom | 2.4 Scalp (SC) Triggers | VWAP as modest target: removed as NO-SOURCE 2026-10-03 |
| H2 | TOM-049 | Tom | B. Normal Trend | VWAP side sets bias (S10 in SOURCED_RULES.md): not used for direction |
| H3 | TOM-103 | Tom | 5.2 VWAP as Profit Target for Counter-Trades | VWAP as counter-trader target removed 2026-10-03 as NO-SOURCE although quoted |
| H4 | TOM-172 | Tom | 5.1 Definition | trade only up to VWAP (modest target): see TOM-103; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict follows  |
| H5 | TOM-194 | Tom | 4.5 VWAP as Profit Target for Counter-Trades | VWAP as profit target when price runs extreme: removed as NO-SOURCE; ID CLASH: the rule file quotes different text at this tag than the index excerpt; |
| M6 | FAB-015 | Fabio | Same-candle two-sided aggression with asymmetric result, des | same-candle two-sided aggression with asymmetric result: b99 buy and sell counts exist per bar (orderflow_bars.py) but no signal uses both |
| M7 | FAB-018 | Fabio | Daily directional bias filter: only take setups aligned with | daily directional bias filter: 4H/1D balance is written to disk but no model reads it |
| M8 | FAB-0jM5Y31YJak-R4 | Fabio | Minimum 1:3 reward-to-risk on initial trades | minimum 1:3 reward-to-risk as an entry gate is not coded in v3 (stop D from models.d_and_stop :38; target = edge/hvn) |
| M9 | FAB-8CWKfoSJu3c-R6 | Fabio | Psychological Level Break Control | psychological (round-number) level break control: no round-number level in any signal |
| M10 | FAB-8CWKfoSJu3c-R8 | Fabio | Squeeze Level Reaction | squeeze-level reaction exit not coded |
| M11 | FAB-FawPrRUGNpk-2of3-R9 | Fabio | Aggressive Order Squeeze | aggressive order squeeze (short-squeeze of a level) not coded |
| M12 | HAB-F7 | Habib | His strategy requires a wick at the level | wick requirement not in imb.py trigger (small body + new 20-bar extreme only) |
| M13 | HAB-P5 | Habib | wOpen (weekly open Monday 00:00Z): price above = long bias | not adopted; PRE_REG_HABIB_PLANS.md excludes it ("not tested here"); source is a Discord screenshot/hypothesis, no transcript to verify |
| M14 | TOM-004 | Tom | 1.3 Three Trigger Categories (Synthesis from Tom + Research) | breakin/breakout entry not coded |
| M15 | TOM-008 | Tom | 2.1 Counter-Trade (CT) Triggers | dynamic entry on a setup at breakout not coded; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict follows the  |
| M16 | TOM-011 | Tom | 2.2 Trend-Continuation (TC) Triggers | acceptance after pullback to business zone not coded |
| M17 | TOM-014 | Tom | 2.2 Trend-Continuation (TC) Triggers | need a closing price beyond level or cut half: management rule not coded |
| M18 | TOM-015 | Tom | 2.2 Trend-Continuation (TC) Triggers | invalidation at last significant 5m volume level not coded |
| M19 | TOM-019 | Tom | 2.3 Breakout (BO) Triggers | real acceptance vs quick spike filter not coded |
| M20 | TOM-028 | Tom | 3.4 Tier 4: Time Trigger (Context Filter) | hold or close one contract on closing price: management rule not coded |
| M21 | TOM-036 | Tom | 1.2 Identification Criteria | B-profile (strong aggressive selling) shape signal: old shape classifier removed (Rule 32), nothing replaced it |
| M22 | TOM-037 | Tom | 1.2 Identification Criteria | B-profile weakness: see TOM-036 |
| M23 | TOM-041 | Tom | 1.3 Timeframe Context | weekly VPOC trend as direction not coded (weekly_vp POC used only as zone/target) |
| M24 | TOM-050 | Tom | B. Normal Trend | VWAP side (above/below) as normal-trend bias not used; directions use VA and POC only; ID CLASH: the rule file quotes different text at this tag than  |
| M25 | TOM-051 | Tom | 2.3 Identification Criteria | permanently above VWAP = trend: not used |
| M26 | TOM-052 | Tom | 2.3 Identification Criteria | trend identification by permanent side of VWAP and VPOC/VA drift not coded (state uses slopes) |
| M27 | TOM-053 | Tom | 2.3 Identification Criteria | trend identification by permanent side of VWAP and VPOC/VA drift not coded (state uses slopes) |
| M28 | TOM-057 | Tom | 2.5 Trend Health Assessment | cross-market correlation divergence (DAX vs BTC/SPX) not coded; card tom-corr-divergence-backtest is the planned test |
| M29 | TOM-079 | Tom | 2.8 Stop Moved to Invalidation Level | stop moved to invalidation level (management arm); card tom-probe-prereg/runner covers management arms |
| M30 | TOM-080 | Tom | 2.9 Game Over Below Key Level | exit when key level breaks (game over) is a management exit, not in detector or sim |
| M31 | TOM-082 | Tom | 2.11 Trailing Stop to Last Significant Volume Level | trail to last significant volume level not coded |
| M32 | TOM-101 | Tom | 4.3 Secure Initial Profits at 3:1 | secure initial profits at 3:1: partial-exit arm not coded; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict f |
| M33 | TOM-104 | Tom | 5.4 Partial Exit on Rotation | partial exit on rotation: management arm not coded |
| M34 | TOM-117 | Tom | 8.2 Game Over Below Key Accumulation Level | exit below key accumulation level: management exit not coded |
| M35 | TOM-118 | Tom | 8.3 Price Trades Actively Above Volume Step | acceptance above a volume step (trading actively above) not coded as a signal |
| M36 | TOM-145 | Tom | 4.3 Zone Requirements | B-profile weakness at a zone: see TOM-036; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict follows the rule  |
| M37 | TOM-157 | Tom | 5.3 Zone Requirements | TC zone requirements beyond VWAP pullback (VA edge, POC) and tc_short not coded |
| M38 | TOM-158 | Tom | 5.3 Zone Requirements | TC zone requirements beyond VWAP pullback (VA edge, POC) and tc_short not coded |
| M39 | TOM-165 | Tom | 6.2 When Valid | breakout setup type (when valid) not in determineSetupType |
| M40 | TOM-173 | Tom | 6.5 Entry: Breakin or Breakout | breakin/breakout entry not coded (entries are limit-at-zone only); ID CLASH: the rule file quotes different text at this tag than the index excerpt; v |
| M41 | TOM-196 | Tom | 2.3 VPOC Trend = Global Money Flow Direction | VPOC trend as money-flow direction not coded; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict follows the ru |
| M42 | TOM-200 | Tom | 5.1 Business Zones = Smart Support/Resistance | business zone (VA edges combined) not a named zone type; ID CLASH: the rule file quotes different text at this tag than the index excerpt; verdict fol |
| M43 | TOM-202 | Tom | 6.1 Definition | single print areas (never retraced): profile single prints not coded |
| M44 | TOM-205 | Tom | 6.4 First Retest Holds, Second Retest Breaks | first retest holds / second breaks: testable event study, not coded |
| M45 | TOM-210 | Tom | 7.1 Definition | LVN computed in the profile but never a zone or setup; research Q33 matrix tom_fabio_guidance_2026-10-12 tested fast-move idea only |
| M46 | TOM-211 | Tom | 7.2 LVN as Transition Zone | LVN as transition zone / bounce not coded |
| L47 | FAB-019 | Fabio | Multiple-target management: partial exit plus a runner on no | partial exit plus runner not coded in v3 manage |
| L48 | FAB-045 | Fabio | "P-shape" profile defined: value building on the upside sign | P-shape profile -> next-day bias not coded (Tom B-profile twin TOM-036) |
| L49 | FAB-046 | Fabio | Merging repeated overlapping day-profiles builds a composite | composite of overlapping day profiles not coded |
| L50 | FAB-047 | Fabio | Repeated-top rejection with a declining POC/value area (no m | declining POC with repeated top rejection warning not coded |
| L51 | FAB-0KyIEdvVKMQ-R9 | Fabio | Session range pre-estimate via ATR or open behavior | session range pre-estimate by ATR/open: ATR exists (signals.py:91) but no pre-estimate gate; day gate g uses prior-20d volume instead |
| L52 | FAB-8CWKfoSJu3c-R5 | Fabio | Position Sizing Based on Market Control | position size by market control not coded (fixed q1 unit) |
| L53 | FAB-FawPrRUGNpk-3of3-R19 | Fabio | Short target below the session low | short target below session low not coded (targets are balance edge / HVN) |
| L54 | FAB-FawPrRUGNpk-3of3-R8 | Fabio | Price above VWAP +1 SD = buyers in control | price above VWAP +1 SD = buyers in control: no VWAP in v3 signals |
| L55 | HAB-F6 | Habib | Trade = good S/R + imbalance + good reaction | reaction at an imbalance level is undefined (what is "good"); needs his definition or more labels (README s8) |
| L56 | HAB-P2 | Habib | "Bull trap early in the week" then a drop | box/level not legible; needs typed price (README s5); source is a Discord screenshot/hypothesis, no transcript to verify |
| L57 | HAB-P4 | Habib | Long on reaction with all the imbalances, bias outlined firs | imbalance definition for plans is open (H-FVG, H-F, H-SP, H-vol; README s4); no variant adopted; source is a Discord screenshot/hypothesis, no transcr |
| L58 | TOM-017 | Tom | 2.3 Breakout (BO) Triggers | add at breakout not coded |
| L59 | TOM-024 | Tom | 3.1 Tier 1: Structural Trigger (Mandatory) | re-entry at same area on a new valid signal not coded |
| L60 | TOM-038 | Tom | 1.2 Identification Criteria | quick watch of current trend on a line chart not coded |
| L61 | TOM-039 | Tom | 1.2 Identification Criteria | trend by counting closing prices not coded |
| L62 | TOM-047 | Tom | A. Fast / Accelerated Trend | fast-trend retrace-to-origin expectation not coded |
| L63 | TOM-058 | Tom | 3.1 Balance After Strong Trend (Sorting Itself Out) | balance-after-trend (sorting itself out) not coded |
| L64 | TOM-059 | Tom | 3.2 Double Distribution | double distribution detector not coded |
| L65 | TOM-062 | Tom | Step 1: Quick Watch (Line Chart) | quick-watch trend by line chart / counting closes not coded |
| L66 | TOM-076 | Tom | 2.5 Footprint Charts for Stop Placement | footprint-based stop placement not coded (needs aggTrades footprint at entry) |
| L67 | TOM-084 | Tom | 2.13 The Mistake: Stop Inside VPOC/VA Range | reject a stop placed inside the VPOC/VA range: not checked |
| L68 | TOM-085 | Tom | 2.13 The Mistake: Stop Inside VPOC/VA Range | reject a stop placed inside the VPOC/VA range: not checked |
| L69 | TOM-106 | Tom | 5.6 Target Above Highs | target above highs (beyond swing) not coded; targets are POC/HVN only |
| L70 | TOM-107 | Tom | 6.1 Re-Entry Valid When Market Stable + Moving in Favor | re-entry after stop-out not coded |
| L71 | TOM-108 | Tom | 6.2 Re-Entry Requires Proof, Not Emotion | re-entry needs fresh proof: not coded |
| L72 | TOM-197 | Tom | 5.2 Business Zone Construction (Live Example) | live example of business-zone construction: not coded |
| L73 | TOM-204 | Tom | 6.3 FVGs Only Work With Trend Stability | FVG validity gated by trend stability not coded |
| L74 | TOM-208 | Tom | 6.7 Single Print at End of Session = Not Fair Value | single print at end of session: needs a session-end definition on 24/7 BTC; profile single prints not coded |
| L75 | TOM-209 | Tom | 6.8 FVG in Sideways Phase = Traded Through | FVG in sideways phase traded through: filter not coded |
| L76 | TOM-214 | Tom | 1. STATE CLASSIFICATION | double distribution info before the week starts: not coded (compiled_engine.md only) |

## 4. NO_QUOTE (verdict kept, quote does not verify or has no transcript)

| id | trader | reason |
|---|---|---|
| TOM-056 | Tom | index excerpt stitches two sentences ("Why? Because...") that the transcript zQTbdEweG3c does not contain; the wired unhealthy-trend rule cites TOM-056 and TOM-140 (same excerpt) |
| TOM-140 | Tom | same excerpt as TOM-056 (zQTbdEweG3c); cited in SetupCandidatesBuilder.java:284,463 |
| TOM-159 | Tom | excerpt starts "if the market shows me once again", transcript says "especially when the market shows me once again" (qLnQan0KGmQ) |
| TOM-174 | Tom | second sentence ("relaxed and patient swing trader or a fast-paced ... day trader") is not in transcript 3o1VVsfBmmU |
| FAB-012 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-032 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-035 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-047 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-049 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-027 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| FAB-028 | Fabio | extract quote contains caption annotations ([..?]) or a stitched span; no quote block of the rule matches the transcript |
| HAB-F5 | Habib | screenshot / paraphrase, no transcript |
| HAB-P1 | Habib | screenshot / paraphrase, no transcript |
| HAB-P2 | Habib | screenshot / paraphrase, no transcript |
| HAB-P3 | Habib | screenshot / paraphrase, no transcript |
| HAB-P4 | Habib | screenshot / paraphrase, no transcript |
| HAB-P5 | Habib | screenshot / paraphrase, no transcript |

## 5. Findings
1. Two wired Tom rules rest on a quote that does not verify: TOM-056 and TOM-140 (unhealthy trend, wired at `SetupCandidatesBuilder.java:284,463`). The idea itself is in the transcript ("no liquidity left here ... low volume"), the stitched excerpt is not. Fix the excerpt, not the code.
2. VWAP as a profit target (TOM-103, 172, 194, 023) was removed from `pickTarget` on 2026-10-03 as NO-SOURCE (`SetupCandidatesBuilder.java:143-144`), but all four quotes verify. Rank H.
3. VWAP side as bias (TOM-049, S10 in `tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`) is quoted and unused; `determineDirections` reads VA and POC only. Rank H.
4. 40 Tom ids carry a different quote in the rule file than in the index (most in `setup_type_rules.md`; e.g. [TOM-142] is tagged on "divide your setups into counter trend continuation or breakout" while the index and the Java comment mean "yesterday value area low / VPOC"). Those rows are marked ID CLASH; the verdict follows the rule heading. The index header claims a 1:1 mapping.
5. LVN is computed (`MarketDataSnapshot.java:555`) but never a zone, target or setup; Tom (TOM-210/211) and Fabio (FAB-044, wired in v3 model A) both teach it.
6. Fabio is wired only in the offline layer; the heat-map/reload rules (33 rows) need L2 book history that is not on disk (`FABIO_V3_SPEC.md:37`), so they are not-worth-wiring until such data exists.
7. Habib: scorer `plan_score.py` is built and tested, but 0 plans are scoreable on DEV; his imbalance candle test (construct F) is NO EDGE fee-net. No rule has a pre-registered test queued.

## 6. Not rowed
- `tom_btc_2026-10-13`, `tom_fabio_guidance_2026-10-12`, `tom_transfer_*`: research on the same ids, no separate rule set; `SOURCED_RULES.md` S1-S14 map to TOM-210/211/202/204/049 and FAB-0jM5Y31YJak rows above.
- `SpikeFade*.java` (Tom v2 family A, flag-gated): implements a BTC entry path from the Tom v2 spec, not one id per row; see `TOM_LAYER_V2_SPEC.md`.
- `fabio_asr_2026-10-16`, `fabio_date_match_2026-10-18`, `fabio_video_search_2026-10-17`, `fabio_transfer`: tooling and trade ledgers, no rules.

DECISION (OURS): rows are per quote id / extract rule, not per merged FR-nn rule of `FABIO_RULEBOOK.md`; partial wiring is counted as wired with extent partial; sizing and psychology rules are not-worth-wiring.

ROWS: 446
