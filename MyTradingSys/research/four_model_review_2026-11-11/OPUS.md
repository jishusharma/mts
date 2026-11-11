# Four-model review 2026-11-11: OPUS reviewer

Read-only review. Paths are relative to `MyTradingSys/research/`; OD = `../system/OPERATOR_DECISIONS.md`. Short names: BIBLE = mts_bible/BIBLE.md; BC = eagle_eyes_picture_2026-10-28/BACKTEST_CANDIDATES.md; PIC = eagle_eyes_picture_2026-10-28/PICTURE_AND_PLAN.md; VA = value_area_acceptance_2026-11-05/RESULT.md; TF = tom_fabio_course_correction_2026-11-07/; AC8 = TF/AUCTION_CENSUS_1108.md; C59 = TF/CENSUS_5M15M_1109.md; PM = TF/POSTMORTEM_OPUS.md; ADX = adx_di_2026-11/CENSUS.md; LA = live_aid_review_2026-11-11/; EH = edge_hunt_2026-11-09/. No price forecasts. All numbers are fee-free/descriptive unless "net R" is written.

**Bottom line: nothing is a proven fee-net edge (STATUS.md:7 "0 of 40 fee-net rows carry a surviving PASS"). Intraday level trading fails on fees and direction. The 4h/15m trend-pullback leads are the only ones with a positive sign in more than one period. ADX/DI and the value area are useful as context and location, never as triggers.**

## C1. What has been learned

### Seven lessons that still hold
| # | Lesson | Number, n | Source |
|---|---|---|---|
| L1 | The cycle clock: peaks 372-548 days after the halving; drops get smaller each cycle (-85, -84, -78, -54 % so far) | n = 4 cycles (anecdote, no test needed per OD:1814) | BIBLE:6-13 |
| L2 | Cycle turns are double tops or double bottoms | 5 of 6 turns | BIBLE:26 |
| L3 | The 200-week SMA is a floor zone, not a floor: within 1-11 % of the low at 3 of 4 bottoms, 36 % above it in 2022 | n = 4 | BIBLE:61 |
| L4 | Candles alone are coin flips; Live Aid ideas are right 47 % | n 20-100 per shape; ideas n = 759 | BIBLE:29; LA/RESULT.md:17 |
| L5 | Fees decide intraday, not direction. The best gross DEV effect is 3.8 bp against a 14 bp round trip; 15m auction H1 makes +0.064 R gross and -0.106 R net | n = 1,484 | PIC:19; C59:20-21 |
| L6 | Sweeps happen reliably, but the direction afterwards does not. US-window low taken first 64 %; US-open round trip low first 63 % vs 16 %; a held retest is taken within 24 h 72 % vs 57-61 % control, yet trading it nets -0.10 R | n = 137; 125; ~700 (trade n 1,504) | BC:23,46,33 |
| L7 | Order flow away from a level means continuation, not reversal: b99 big trades reverse 18 % vs 27 % baseline. Taker delta tells you how often a move gets undone (14-19 % vs 26-30 %), not which way price goes | n = 2,175; 21,855 h | TF/AUDIT_AND_COURSE_CORRECTION.md:39; eagle_eyes_picture_2026-10-28/SCENARIO_LEDGER.md:27-29 |

Two supporting facts. First, the phase gate works as a kill switch: Malkan 4h longs outside ACCUMULATION/BULL lose 0.3-1.0 R (EH/results/eh-o2-phase-lens/RESULT.md:61). Second, the research_kit regime tag finds 0 bear weeks, so every "Regime mix" line built on it never saw a bear market (same file:59).

### Three most important ideas that were refuted
| # | Idea | Result, n | Source |
|---|---|---|---|
| R1 | Dalton 80 % rule (back inside value means the far edge is reached) | 44 % [40..49], n = 493 | VA:9 |
| R2 | Plain Tom/Fabio level fades (sweep and reclaim) | 7y 1h -0.087 R net, n = 1,871, negative in all 8 years; pre-registered 15m with session + ladder + node exit -0.106 R, n = 1,484; T04 -0.221 R, n = 1,150 | AC8:113,152-163; C59:3; EH/EDGE_TABLE.md:12 |
| R3 | More agreeing readings means more confidence | Live Aid 4+ of 6 agree: 51 % (n = 144) vs against: 49 % (n = 288); T13 score >= 3 nets -0.163 R (n = 410) | LA/tables.md:22,25; EH/EDGE_TABLE.md:19 |

## C2. Which trades MTS should take now (testnet only)
What the operator asked for, in his words:
- (a) "low-leverage long-term longs near confirmed cycle bottoms ... buy on or after a good retest"; (b) "scalps, day and swing trades by session using Tom and Fabio levels" (OD:1808).
- "better to buy on retests after the dot combined with rsi confluence. then sessions also matter" and "BB range-to-range by session" (OD:1680).
- Krown 4h forward test (OD:2091), Malkan 4h level shorts (OD:2095), Tom swing (OD:2143).

| Rank | Trade (direction, time, trigger, what must agree) | Evidence, n | Asked by operator? |
|---|---|---|---|
| 1 | LONG, 15m, any session: WaveTrend buy dot <= -53 plus RSI bull divergence, only while the 2h trend is up (C30 H2) | VALIDATION +0.220 %/trade fee-net, n = 22, CI -0.12..+0.56; beats random entries 30/30 (C30_VALIDATION.md:10-12); DEV +0.261 % | YES (OD:1680 "dot ... rsi confluence") |
| 2 | LONG, 4h: RSI14 crosses its SMA14 (T06 long side) | +0.105 R, n = 623, CI -0.024..+0.233, Holm 0.83 (EH/results/eh-h5-rsi-ma-cross-trigger/RESULT.md:44) | Partly (RSI layer, OD:1724) |
| 3 | SHORT, 4h: Malkan level short with a 3-10 bar close-to-close divergence | +0.10 R, n = 126, about 0.9 SE; full 5-layer stack +0.13 R, n = 37 (malkan_level_shorts_2026-11-09/REPORT.md:3,30) | YES (OD:2095) |
| 4 | SHORT, 30m: first close below the lower BB, mid falling, the close a new 14-day low, exit at the mid | +0.16 / +0.62 % net in both periods, n = 38 / 35 (BC:28) | Partly (BB band walk, BC:28 shot) |
| 5 | LONG, low leverage, weekly/daily: cycle-bottom long on a daily close above the double-bottom neckline 82,850, stop below 57,800 | NO EVIDENCE on BTC trades: n = 4 cycles (BIBLE:12) and Bulkowski stock rates only (pattern_book_2026-11/WATCH_LIST.md:15) | YES, his core trade (OD:1808 a) |

- **Asked for but NO EVIDENCE or refuted:** Tom/Fabio session level fades (R2); Krown S8 4h is INCONCLUSIVE (PIC:18) and S5 has n = 35 with a CI that crosses 0 (PIC:88); the 4h rectangle breakout has no BTC count (WATCH_LIST.md:12); Tom swing was never tested (OD:2143); BB range-to-range by session has no result file (NOT_IN_DATA).
- **Gap:** the data leans to with-trend pullback triggers (ranks 1-2). The operator leans to level fades and cycle longs. Rank 5 is his own trade, but it is a phase bet with no count behind it.

## C3. ADX/DI and the volume profile
| | ADX/DI | Value area / POC |
|---|---|---|
| Formula | VERIFIED-TV on the daily, 0.00 difference on two bars (adx_di_2026-11/TV_CROSSCHECK.md:3,17-22); 2d not verified, because 2D is paywalled (:7) | 70 % VA SOURCED to Tom; the UTC-day profile and $50 bins are OURS (PM:36; VA:5) |
| Measured (HTF) | 2d crosses: n = 88 (ADX:186). Whipsaw within 3 bars: DEV 32.1 %, n = 56; VAL 46.7 %, n = 15 (ADX:31,55). Crosses from ADX < 20 whipsaw less than 20-40 in all three splits: DEV 31.8 vs 35.7 % (n 22/28), VAL 14.3 vs 75.0 % (n 7/8), RECENT 40 vs 60 % (n 5/10) (ADX:13,15,37,39,61,63). Same sign three times, tiny n | Acceptance below VAL reaches a further half VA width 77 %, n = 300, no placebo (VA:10); as a trade, ACCEPTED nets -0.096 R, n = 2,798 (AC8:116) |
| Measured (LTF) | Live Aid, 29 days: idea right when ADX15 agrees 50 % vs against 46 % (n 234/263); fade at ADX < 20: 47 % vs ADX >= 20: 50 % (LA/tables.md:35-36,78-79). Adds nothing | Fades at VA edges are the least bad family: -0.039 R, n = 725 (AC8:122); vp_pivot_probe 0/48, tom_vp 0/20 (TF/AUDIT...:34-35) |
| CCU claim | "1-3 weeks of consolidation then a straight fall": the low comes within 1-3 2d bars in 37.1 % of red crosses, n = 35 (ADX:85). Not general | n/a |
| Cascade | 92.9 % of 2d crosses had a 1d cross first, but only 44.8 % of 1d crosses lead to a 2d cross (ADX:192,289) | n/a |
| Use | CONTEXT on 4h/1d/2d (trend vs balance label); a candidate GATE only after D1; DROP as an intraday vote or trigger | LOCATION: where to look, and the anchors for stop and target; never a trigger; drop the 80 % odds |
| Unmeasured | 1h/4h census never run (ADX:5); ADX as a gate on any fee-net trade; ADX x VA | NY-session VA (PM:56); live/developing VA (LA/RESULT.md:48); delta at the level (PM:52); placebo for the 77 % (VA:15); sourced acceptance of 12x5m (PM:107); VA as a with-trend pullback zone |

## D1 (Opus): one testable confluence rule: "Trend pullback to value"
**Hypothesis.** The C30 H2 trigger (rank 1) pays because it buys a dip inside a trend. Fades fail because they trade against the trend (PM:41; L7). The rule adds two filters:
- a measured trend-strength gate (4h ADX/DI) in place of the 2h trend;
- a structural location (the lower half of the prior-day value area), which gives a wide, plan-based stop and a volume-node target, so fee_r stays small.

The rule is long-only. Shorts are reported only, because WT top shorts failed (BC:36-39, 3 of 65 short cells positive).

| # | Condition (all on closed bars) | Label |
|---|---|---|
| 1 | Regime: 4h ADX14 >= 20 and DI+ > DI- | ADX14 SOURCED (Wilder, TV-verified); 20 OURS (CCU names no number, adx_di_2026-11/SPEC.md:5); 4h OURS |
| 2 | ADX 5-bar slope >= 0 (the trend is not fading) | OURS (the census slope5) |
| 3 | Phase: PHASE_LABEL is not BEAR or PEAK_WINDOW | OURS (phase_label.py), kill switch per eh-o2:61 |
| 4 | Location: the signal bar's low is inside [prior-day VAL, prior-day POC]; the UTC-day profile is 70 % | 70 % SOURCED (Tom); UTC day and half OURS |
| 5 | Trigger: the C30 H2 rule unchanged (15m WT buy dot <= -53 plus RSI bull divergence, PRE_REG_C30.md frozen) | frozen OURS rule; divergence on closes SOURCED (OD:1686) |
| 6 | Entry: maker limit at the trigger close; no fill within 3 bars means no trade | maker SOURCED (fees.py FEES_DERIBIT, PM:43); 3 bars OURS |
| 7 | Stop: the lower of the divergence's second pivot low and VAL, with no fixed % floor | plan invalidation SOURCED (OD:1819) |
| 8 | Target arm A: the C30 X1 exit unchanged. Arm B: prior-day VAH, BE at +1R; skip if VAH < 1.5R away | arm A frozen; arm B TOM-018 SOURCED, 1.5R and BE OURS |

**Sample.**
- The data is BTC and ETH spot 15m. DEV is 2022-01..2024-06 (the C30 DEV window). The HOLDOUT from 2025-07 stays sealed.
- Step 1 is a count pass with no returns, as in eh-o1. C30 H2 fired 22 times in 12 VALIDATION months, so DEV with both filters may give only about 30-60 trades (OURS estimate).
- At an R sd of about 1.4 (malkan REPORT:41), the minimum effect detectable is about 0.5 R at n = 60, and about 0.15 R needs n of about 540. A backtest can therefore only refute this rule.
- The proof run is testnet-forward, per OD:1813: the rule trades as soon as the pre-reg is frozen.

**What refutes it (any one):**
- DEV arm A or B net R <= 0 under maker fees.
- Taker-arm net R <= 0.
- The filtered rule does not beat the C30 trigger alone by at least 1 SE. The filters then add nothing and are dropped.
- It does not beat 30 random entries under the same gates.
- Testnet: after 30 trades, net R <= 0, measured against the -0.087 R null (PM:72).

**Pre-registration outline (commit before any return is computed):**
- `## Context`
  - Regime: 4h ADX/DI rows 1-2.
  - Phase: PHASE_LABEL row 3, with a split per phase.
  - Session: no filter; the asia/london/ny/late block is logged (C59:11).
  - Entry: row 6.
- `Regime mix:` the PHASE_LABEL weeks of DEV, not research_kit.regime_tag (that tag finds 0 bear weeks, eh-o2:59). Also print the ADX >= 20 share of 4h bars.
- Arms: A and B, Holm with m = 2.
- Every threshold carries a label. Fees use fees.py, and slippage 2 bps per FORMULAS s13. The code mismatch (4 bps in code) is fixed first (C59:159).

**Where it can be curve-fit (flag each one):**
- The 15m H2 trigger was the best of about 250 cells (BC:39). It is positive post hoc, so its +0.22 % is already inflated.
- VALIDATION 2024-07..2025-06 has been seen at trigger level (C30_VALIDATION.md). No filter may be judged on it.
- ADX 20, the 4h timeframe and the slope window are free choices. Fix them now and never sweep them. A sweep would be a new trial.
- "Lower half of the VA" and the UTC-day profile (not NY-session) are free choices.
- Arm B's 1.5R skip and the BE level are free choices.
- Adding ETH raises n but mixes in a second market. Report per symbol.
- The recent cells that look good (2026 +0.568 R, n = 170; rally_in_macro_bear +0.158 R, n = 226; C59:102-116; Live Aid last-week-low 72 %, n = 18) must not shape the rule.

## NEXT: top 5 actions (ordered)
| # | Action | Done when |
|---|---|---|
| 1 | Freeze the D1 PRE_REG (Context, PHASE_LABEL Regime mix, labels, kill lines) and fix the 2 vs 4 bps slip mismatch | PRE_REG commit hash is older than any D1 result file |
| 2 | Run the D1 count pass on DEV (event counts by phase, ADX state and symbol, with no returns) | count table committed; if n < 30, D1 goes straight to a testnet signal |
| 3 | Start testnet-forward signal slots for ranks 1-3 (C30 H2/D1 long, T06 4h long, Malkan 4h short), with the 30-trade kill rule | each slot has a running signal and one ledger row per trade |
| 4 | Run the ADX/DI census on 1h/4h from data-api.binance.vision; fix the median-lead column printed as % | CENSUS.md has 4h/1h tables, and the leads print in days |
| 5 | Ship Live Aid flag logging with the readings at each flag (ADX, VA position, WT, RSI) | 7 days of logged flags; the agreement table is recomputed from the log, not from a replay |
