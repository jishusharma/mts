FIX-FIRST

# Layer lab report: setup catalog source audit

Card: gpt-catalog-notstated-audit. Coverage: all 12 requested setups (TOM-1..5, TOM-8, FAB-1..5, FAB-8). No catalog, spec, code, market data, or holdout changes. No backtest or trading-performance validation. The requested report filename retains 2026-10-15.

References below: C = `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md`; RAW = `raw_transcripts_canonical/`; FL = `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`; TL = `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`; ANG = `MyTradingSys/research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md`. Q identifiers link to the verbatim evidence appendix, each excerpt at most 25 words. Physical raw line numbers are intentional: several canonical transcripts contain their whole body on one line. Caption line numbers are a different coordinate system.

## Findings

Severity reflects effects on a future source-derived setup definition, not a measured trading loss. MISMATCH means the wording exceeds or contradicts the evidence; a proposed correction is not an adopted specification.

| ID | Severity | Status | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|---|---|
| H1 | HIGH | MISMATCH | C:361,366,370 | TOM-3 says stop location and target level type are NOT STATED. The transcript names last week's POC, combined value/single-print support, and a planned 6,768 target. It also explicitly excludes an above-high stop and directs attention to the largest footprint volumes. Exact stop price remains unspecified. | RAW/yRvMW6lgN1o_raw.txt:19, Q1-Q3; ANG:70 gives 6,768. | Restore target type and spoken example, and qualified stop-selection guidance. Keep exact stop price NOT STATED; do not invent a numeric stop or equate 12 ticks with a universal rule. |
| H2 | HIGH | MISMATCH | C:114,125,1027 | The shared section says management applies to all setups; FAB-3 context requires day P&L floor zero / risking only profit. Its own F5 example is entered after a roughly $9,000 loss. The fZ statement is a funded-session rule, not proof of a universal prerequisite. | RAW/jasv3L-d8ZE_raw.txt:33-38, Q4; FL:19 records starting daily P&L -9577.50; RAW/fZlNGWvd2Ko_raw.txt:28-31,60-61. | Scope the zero floor to the fZ session and distinguish recovery-day management. Do not silently remove F5 or impose the fZ constraint on every Fabio trade. |
| M1 | MED | MISMATCH | C:289,321 | TOM-2 still says management NOT STATED and 0 real trades, despite its added viT loss and explicit balance-acceptance exit. These are stale fields, not newly discovered trades. | RAW/viT_VzF5Fsw_raw.txt:7, Q5; C:295-318 already includes the evidence. | Reconcile the field and count with the addition. Preserve the acknowledged TOM-1/TOM-8 overlap and the failed-entry/anti-example qualification. |
| M2 | MED | MISMATCH | C:397,436,1215 | TOM-4's main stop/gaps fields and final stop tally remain stale after its sourced stop addition. | RAW/YkclL6xgu-s_raw.txt:7, Q6; C:418-427,1187 explicitly acknowledge it. | Make the main stop field say below last volumes; retain missing distance and time stop. Reconcile the final tally with the summary's four Tom setups with stated stops. |
| M3 | MED | MISMATCH | C:973 | FAB-1's session time is labelled NOT STATED, although the source describes the pre-session balance at almost 12 Central European time. This is context time, not an exact execution timestamp. | RAW/0jM5Y31YJak_raw.txt:4, Q7. | Record the spoken approximate context time, with no inferred UTC/date or exact entry time. |
| M4 | MED | MISMATCH | C:1021,1026 | FAB-3 says no fixed target and substitutes the fZ day-extreme narrative for both examples. F5 explicitly discusses its profit target; both F3c and F5 have target orders in the cited ledger. The target's structural rule remains unknown. | RAW/jasv3L-d8ZE_raw.txt:88-89, Q8; FL:10 target 24655.75 and FL:19 target 24910.25 (frame-derived). | Separate spoken aspiration, frame target orders, and unknown target-selection rule by example. Do not turn absence of a spoken rule into absence of an order. |
| M5 | MED | MISMATCH | C:1033,1058 | Assigning only F3c to failed auction, while F3a/b go only to protection wall, obscures that the failed-seller-auction narrative begins at 1:26-1:43, overlapping F3a t=90. F3b is a scale-in state, not evidence for a different exclusive setup. This does not prove that protection wall is false. | RAW/fZlNGWvd2Ko_raw.txt:36-42, Q9; FL:8-10; LBL decision rows D07-D08. | Cross-tag the fZ sequence or mark family assignment overlapping; distinguish position states/adds from independent executions. Do not force exclusive reassignment without frame review. |
| M6 | MED | MISMATCH | C:1058 | FAB-5 says 13 entry rows but enumerates F3a,b and F6-F14: 2 + 9 = 11. The summary already says 11. | Verbatim catalog fragment: "13 entry rows"; FL IDs F3a,F3b,F6,F7,F8,F9,F10,F11,F12,F13,F14, parsed with csv.DictReader. | Correct to 11 enumerated entry rows; retain the separate question whether adds and chase longs are independent setup examples. |
| M7 | MED | MISMATCH | C:991 | FAB-2 places the spoken 27,600 and 1:19 beside the fixed target label without distinguishing money, price, and risk stage. FL says target price 25514.75, $27,600 reward, 8.8R on the 15.75-point risk; 19.06 is a different displayed risk state. | RAW/8CWKfoSJu3c_raw.txt:80-84, Q10; FL:2. Arithmetic: 138 / 15.75 = 8.7619, 138 * 10 * 20 = 27600. | Label the caption as ambiguous spoken quantity; separately cite ledger price, monetary reward and stage-specific R. Do not use 27,600 as a validated short target price. |
| M8 | MED | MISMATCH | C:461,466; shared C:104 | TOM-5 management lists add/re-entry, but omits its own explicit trailing/partial-exit evidence. The shared section's claim that quoted management only comes from TOM-1 is too broad. Time is also not wholly absent: the trader says lunch break is coming. | RAW/4MoNjEQ2Dd8_raw.txt:19, Q11-Q12; full narrative describes closing one contract when the high fails to hold and tightening after liquidity develops. | Add TOM-5-specific trailing and partial rules; note spoken lunch context without fabricating an execution clock. Keep uncertain chart levels qualified. |
| M9 | MED | MISMATCH | C:60-61,114 | The blanket claim of zero Fabio initial stops in words is stronger than the available source: the same FawPr lecture gives below-reload and below-next-liquidity stops. These belong to heat-map variants, not automatically to F6-F14. | RAW/FawPrRUGNpk_raw.txt:320-327,389-399, Q13; C:1077 itself cites these rules. | Correct the universal statement and scope stops to the lecture's variants; leave individual live-trade initial stop rules unknown unless connected by evidence. |
| M10 | MED | MISMATCH | C:245 and summary C:35 | The 16 TOM-1 total mixes candidate groups, frame-assigned examples and transcript trade groups under a real-trades heading. T8 is explicitly a candidate; T11/T12 have no canonical transcript. The arithmetic is correct (10 + 1 + 5), but the certainty/unit is not uniform. | TL:20 row_kind "ENTRY_CANDIDATE(entry/exit not shown)"; TL:32,34; TOM_TRADE_LEDGER.md:6 "12 candidate trade groups". | Label 16 assigned examples/groups including candidates, and show evidence classes separately. Do not use 16 as certified independent executions or a recall denominator. |
| N1 | LOW | NOT_IN_DATA | C:1038-1043,1059,1088-1094 | FAB-4 and FAB-8 lack their cited canonical source o-w5Gxss6T0; FAB-4 also lacks 9IliXww64uM. FAB-5 DyS79/Jpd96 and TOM-1 T11/T12 likewise lack canonical transcripts. Quoted paraphrases and outside-tree frame pointers cannot certify the missing words or trade-family assignments. | C:1094 verbatim: "no quote can be verified". Path.exists checks for all six IDs returned False. FL:17-18 only support screenshot shorts, not the schematic's connection to each entry. | Preserve NOT_IN_DATA, obtain the missing sources and independently tie each trade to its setup. Do not infer false/zero from unavailable evidence. This is not BLOCKED. |

13 findings: 2 HIGH, 10 MED, 1 LOW. The catalog was not edited.

## Coverage and source support

| Setup | Catalog range | Check result |
|---|---|---|
| TOM-1 | 172-252 | MATCH: named proofs, stop above volume bell, 20-point example, three entry paths, and management wording checked against n7Z/k0zm/ujed/T6h/l8RZ/zQT raw passages; tS6Z, kXhI, OUM9 evidence checked. M10 qualifies the 16 count. Prior-value location is not a universal condition: C:248 and 1111 already preserve that conflict. No additional fixed proof count found. |
| TOM-2 | 254-340 | MATCH: balance, B/lower balance, 260-to-140 illustration, invalidation wording and R:R are in BVpY; VWAP variant in 43Ja. M1: stale fields. The BVpY 305/20-point stop illustrations are examples, not a universal width. |
| TOM-3 | 342-370 | MATCH: sell limit below volume step, inside day, 12/97 ticks are said. H1: omitted target and stop guidance. Dollar headline and tick payoff are retained as separate spoken claims, not reconciled as a certified single-position R. |
| TOM-4 | 372-436 | MATCH: qLnQ pullback/proof/next high-volume target, 43Ja VWAP context, ODd trend-zone-proof sequence, Ykcl stop. M2. Zero exclusively tagged trades is not proof of no overlapping trend-following examples: UOBg explicitly describes trend-following within gap context. |
| TOM-5 | 438-469 | MATCH: 4MoN initial stop/ledge and kXhI crude re-entry below swing low. R6/R7 remain broader value-pullback instances: kXhI's quoted buying tail describes ES, not proof that crude had the identical tail. M8. |
| TOM-8 | 586-627 | MATCH: 96i gap liquidity logic, lO range/return condition, UOBg pullback/gap/Friday-value target. T4/T9 and ANG R12 are one alias group. Exact buy signal and initial structural stop remain NOT STATED. Caption prices/times are not frame-certified. |
| FAB-1 | 954-976 | MATCH: 0jM5 balance/CVD/first confirming candle, BE after explosion, redistribution exit. M3. Initial stop is only pointed at, not described structurally. |
| FAB-2 | 978-1003 | MATCH: 8CWK absorbed buyers/rewarded sellers, 10 contracts, spoken $3,150 risk and $23,000 profit, NY context; 0jM5 later short uses the same absorption idea. M7. No initial structural stop inferred from later trailing language. |
| FAB-3 | 1005-1034 | MATCH: fZ failed sellers then buyer aggression; jasv breakdown/absorption. H2, M4, M5 show where shared wording overreaches the two examples. |
| FAB-4 | 1036-1043 | NOT_IN_DATA: FL F4a/b shorts and schematic are secondary evidence; canonical source absent. The existing weak-assignment warning is justified. No invented stop or reclaim rule. |
| FAB-5 | 1045-1059 | MATCH: FawPr wall/absorption/main-direction text. M5/M6/M8-M9 concern assignment, counting and shared claims. NOT_IN_DATA: live-session words and frame revalidation; F11-F14 remain explicitly uncertain chase-long assignments. |
| FAB-8 | 1087-1094 | MATCH to FR-94..96 paraphrase and FR section 3 (70%, 24318-24317); NOT_IN_DATA against absent canonical source. No verified trade, stop, swing rule, bin size or timeframe added. |

Checked the full catalog text and its block-quote bindings. Semantic review concentrated on the requested ranges plus shared frame and contradictory summary fields. Source reading included full raw bodies for yRv, Ykcl, viT, BVpY, qLnQ, 43Ja, kXhI, UOBg, 4MoN, 0jM5, 8CWK, fZ and jasv; source-action/context passages for the remaining cited Tom/FawPr sources. The verifier reads all 42 raw files used by the catalog's block quotes. This is not a claim that every unrelated transcript in the canonical directory was audited.

Secondary sources read/queried: TL (38 physical lines) and FL (73 physical lines), their Markdown ledger narratives, ANG rows R1-R35 and quote appendix, TOM_LAYER_V2_SPEC sections 2-5/13/16, FABIO_TRADE_MODEL, FABIO_RULEBOOK, FABIO_V3_SPEC signal/model/parameter sections, FABIO_LINE_BY_LINE_fZlNGWvd2Ko decision and ambiguity sections, conditions/setup_type_rules.md, conditions/gap_rules.md, TOM_ON_BTC.md. These establish provenance and OURS labels; they do not replace missing primary evidence. No outside-tree frame was opened. No exact fill, contract identity, date or clock was certified from speech.

## Backtest discipline

`MyTradingSys/backtest/PRE_REG_TEMPLATE.md:1-77` read. C:3-7 explicitly excludes backtesting and test design. Items 1-12 were considered: source home, timestamped ground truth, recall/fire rate, inputs, profile parity, cost, fills, management, null, power, holdout/trials, stratification. This audit checks source home/ground-truth provenance/management only; the other readiness items are NOT_ANSWERED for any future run, not passed. Source hit-rate and R:R statements are untested speech, not backtest outcomes. No run or trial was created; no holdout read.

## Verification and follow-ups

`python scripts/dev/verify_extract_quotes.py MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md`: PASS, 186 quotes, 0 problems (all block quotes; does not validate semantic entailment, inline caption coordinates, or frame values).

The same verifier passed on this audit's 13 evidence excerpts (0 problems; maximum 20 words). A separate structural check passed: all 12 setup coverage rows, 13 findings, 2 HIGH follow-up cards, and at most 25 words per appendix excerpt. Full offline suite is not run for this documentation audit; runner owns shipping gates.

HIGH follow-up cards created with `python scripts/dev/tasks.py new ... --lane SONNET --ref <this file>`:
- `catalog-audit-tom3-source-fields` (H1).
- `catalog-audit-fabio-risk-scope` (H2).

## Verbatim evidence appendix

### Q1

RAW/yRvMW6lgN1o_raw.txt:19

> "Last week, we had the point of control as the target area around 6,763 roughly."
**Source GPS: yRvMW6lgN1o | BEGIN**

### Q2

RAW/yRvMW6lgN1o_raw.txt:19

> "I've initially defined 6,768 as my target level."
**Source GPS: yRvMW6lgN1o | MIDDLE**

### Q3

RAW/yRvMW6lgN1o_raw.txt:19

> "It doesn't belong above the high."
**Source GPS: yRvMW6lgN1o | MIDDLE**

### Q4

RAW/jasv3L-d8ZE_raw.txt:34

> "We are at $9,000 in draw down for the day."
**Source GPS: jasv3L-d8ZE | BEGIN**

### Q5

RAW/viT_VzF5Fsw_raw.txt:7

> "I absolutely should have given up the position up here because we completely traded through and accepted this balance here."
**Source GPS: viT_VzF5Fsw | MIDDLE**

### Q6

RAW/YkclL6xgu-s_raw.txt:7

> "where does my stop loss belong. Yes, below the last volumes."
**Source GPS: YkclL6xgu-s | END**

### Q7

RAW/0jM5Y31YJak_raw.txt:4

> "it was almost uh 12 uh central central European time"
**Source GPS: 0jM5Y31YJak | BEGIN**

### Q8

RAW/jasv3L-d8ZE_raw.txt:88

> "Our profit target is not even too far from there."
**Source GPS: jasv3L-d8ZE | MIDDLE**

### Q9

RAW/fZlNGWvd2Ko_raw.txt:40

> "capitalize on the failed auction of the seller and then aggression of the level of the buyers."
**Source GPS: fZlNGWvd2Ko | BEGIN**

### Q10

RAW/8CWKfoSJu3c_raw.txt:83

> "Final target is 27,600 for 1 to 19 risk-to-reward."
**Source GPS: 8CWKfoSJu3c | MIDDLE**

### Q11

RAW/4MoNjEQ2Dd8_raw.txt:19

> "I'm moving my stop loss up now below the last trades price area 16."
**Source GPS: 4MoNjEQ2Dd8 | END**

### Q12

RAW/4MoNjEQ2Dd8_raw.txt:19

> "And now the lunch break is coming up, so I'm ending the session."
**Source GPS: 4MoNjEQ2Dd8 | END**

### Q13

RAW/FawPrRUGNpk_raw.txt:391

> "put your stop loss below the next liquidity area."
**Source GPS: FawPrRUGNpk | BEGIN**


Audit generated UTC: 2026-10-15T19:11:13.809409+00:00

Named output: MyTradingSys/research/layer_lab/gpt-catalog-notstated-audit/CATALOG_AUDIT.md.
