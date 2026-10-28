FIX-FIRST

Audit date: 2026-10-13. Card: lab-audit-fabio-ledger-frames. All 72 CSV records reviewed; every distinct image in the CSV frame column opened with `view_image`. No ledger, code, or spec changed. No backtest or holdout read. Missing facts below are NOT_IN_DATA, not blockers.

## Checked evidence and interpretation

Read `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv:1-73` (CSV below) and `FABIO_TRADE_LEDGER.md:1-90` (MD below), `system/LAYERS.md:44-75`, and `backtest/PRE_REG_TEMPLATE.md:1-65`. Source root (V below): `F:/MTS/data/fabio_videos/`. Images were read directly, including the PNG crops in `frames/`; the CSV's cited sheets and lowres sheets were all available. Additional images: sheets/8CWKfoSJu3c_00,01; sheets/9IliXww64uM_00-04,06; sheets/0jM5Y31YJak_01; sheets/Jpd96fLqr5M_00,01; lowres/DyS79Eb92Ug_w30_01,02; sheets/gLHd20jE8UQ_00,03; lowres/DyS79Eb92Ug_w7_00 (all .jpg). These additions resolve evidence outside the incorrectly cited sheet. This is a citation audit, not an exhaustive replay of every downloaded video or every uncited contact sheet.

Read the cited caption passages in V/DyS79Eb92Ug.txt (3530 lines; source-line ranges below), plus the complete deduplicated text of V/0jM5Y31YJak.en.vtt. The ledger supplies timestamps, not transcript file:line citations; this report supplies the missing anchors. Embedded subtitles in Jpd96fLqr5M sheets were also read. DyS.txt:3130-3137 confirms the t7598 risk/profit quote refers to yesterday in London, not a new trade in this session. ES account values at MD:29 MATCH sheets/9IliXww64uM_01 t120/150 (61179.06, 210370.21 and 217392.36); they do not date the fills. Dates of recording, upload, screenshot creation and trade execution are not interchangeable. A contract suffix alone does not establish a trade date.

MATCH means the stated fact is visible or spoken, not that an executable fill is independently certified. NOT_IN_DATA means absent, illegible, outside the cited sheet, or unsupported by that evidence. A dash/unknown field receives NOT_IN_DATA, not an invented zero. Approximate levels can match approximately. Dollar labels and displayed average-price lines are recorded separately: small discrepancies can reflect platform rounding/accounting; they do not justify silently replacing a visible average with a derived value. No general trading rule follows merely from one example.

## Findings

| ID / severity | File:line | What is wrong / classification | Evidence | Proposed fix |
|---|---|---|---|---|
| H1 HIGH | CSV:33,35,38,45-50; MD:61,66,71,75-76,86 | MISMATCH: several entry/stop/order-side reads materially change risk and setup interpretation. | F8 w3_01 t1325 average 25034.53, not ~25032.5; 25021.75+2040/(8*20)=25034.50. F9 w4_01 t1450 initial preview is ~25019.44, not ~25010.4. F10 w4_02 t1575 average ~25040.00, not ~25040.5. F12 w8_00 t3100 average 25105.78 and stop 25089.75, not 25085.75; w8_01 t3150 average 25108.50, stop 25098.75, TP 25148.75, not ~25100/25098.25/~25140.75. Later w9_00 stop is 25098.25: do not backdate it. F13 w9_01 average 25108.90 then 25108.05, not ~25104/~25105; green +2 LMT at 25104.75 is a buy add, not a sell partial. | Re-read full source pixels for these rows, retain label values and formula checks separately, correct chronology and rebuild affected widths/R. Do not use approximate old values to define v2. |
| H2 HIGH | CSV:29,32,34,40,44,48,51,54; MD:55,66,71,74-78,87 | NOT_IN_DATA: flat position/daily-P&L differences promoted to exact stop/TP causes and cost/slippage attribution. | F6 +10368 and F10 +4964 are visible differences; exact fills are absent. F12 -1525 is smaller than the displayed -2050 stop risk; F13 -2910 is larger than the -1760 stop label, with only 8 covered vs 10 open. No transaction list reconciles these. F11 daily 22239.02 at t3000 becomes 22193 at t3025, an additional -46.02 omitted from the sequence. | Preserve flat-state/P&L observations; mark exit price, execution type and cost allocation inferred/unknown until a fill record or continuous transition establishes them. Reconcile the -46.02 interval. |
| H3 HIGH | CSV:25-73; MD:40,54,85 | NOT_IN_DATA: 2026 trade dates and universal US-cash session claim lack evidence. | Jpd/DyS chart header shows NQ-202512, not a recording date. F4 filename 2026-01-30 214344 is screenshot creation time, not either entry time. F2 V/0jM5Y31YJak.en.vtt:82-90 says central European time before session; :826-842 tentatively says December 30, no year. DyS.txt:66-80 explicitly identifies New York and October 15 (year absent); preserve that partial evidence. Clock-only evidence cannot establish timezone/session for every video. | Use UNKNOWN dates where unsupported; preserve tentative spoken dates separately. Link exact frame clock, date and timezone per execution before replay or design/check split. |
| H4 HIGH | MD:39-44,83-90; CSV:7-16 | MISMATCH / NOT_IN_DATA: final trade count, coverage and stop statistics are not reproducible ground truth. | CSV has 17 plain long/short F1-F14 entry rows plus F15 draft, but F3b scales F3a and F4 grouping is unresolved. MD says 14 filled trades, 13 NQ/1 ES without a grouping rule. F2 transcript :1026-1058 describes three positions closed, :1234-1258 at least five positions and another later position; one F2 row cannot represent all. MD:51,90 admits unread long sessions while :84 claims all available. The 1.5pt minimum comes from the questionable F12 initial stop; no 13-row calculation is supplied. | Define parent-trade vs fill vs management vs teaching example; enumerate membership of each statistic, complete the known F2 omissions or label coverage partial, then recompute counts and widths. |
| H5 HIGH | MD:26,43,62,88; CSV:42-50,65-66 | MISMATCH / NOT_IN_DATA: generalized management and order semantics overstate the sources. | F1 sheet01 t210 TP 25513.25 then sheet02 t330 25514.75 contradicts fixed TP. F12 w8_00 t3075 stop near 25105.50 then t3100 25089.75 contradicts 'only toward profit'. F11 w7_00 t2825/2850 green +2 STP adds, not LMT. F15 is a drawing: DyS.txt:2854-2855 says 'I will not execute it. I will only put the marker.' | Describe observed changes per event, distinguish preview/drawing/submitted order/fill, and reserve universal rules for direct sourced statements. Keep F15 hypothetical, not an unfilled submitted ticket. |
| H6 HIGH | MD:50 | MISMATCH in attribution: third-party settings presented as the trader's own settings/source for encoding. | gLHd20jE8UQ_03 t420 says 'What I run on ES', filter 50; separate footer attributes NQ 30 to 40 to Fabio. This is a different presenter discussing Fabio, not Fabio stating those settings. | Label secondary-source claim; obtain Fabio's own quote before using ES 50, NQ 30-40 or aggregation mode as a layer parameter. |
| M1 MED | CSV:2-5,10-13,25-28,30,42,47,50,52-73 | MISMATCH / NOT_IN_DATA: citations often do not contain the timestamp or full interval asserted. | F1-m3 cites sheet03 (t360-450) but claims t480/510 in sheet04. F11 cites w7_01 (t2875-2950) for t2800 in w7_00. F12-m2 w8_01 ends t3200, not t3250. Many no-trade rows cite only 2-4 samples out of a 250s window. F1 PNG crop omits target/date/setup context. | Cite every needed sheet/panel and timestamp per field. Limit 'no trade' to sampled frames; a talking head cannot certify account state. |
| M2 MED | CSV:8-13,19-28; MD:20-22,35-43,49 | MISMATCH: exact numerical equalities blend rounded platform averages and cash labels. | F3c (24568.38-24565)*14*20=946.40, not 980; 24568.25 is 0.13 below that displayed average despite stop label 0. F3b 8.88*240=2131.20 vs label 2160. F5 9.47*300=2841 vs 2850; 2.07*360=745.20 vs 720. F6 30.83*80=2466.40 vs 2460. | Retain both observed values; label discrepancies, use consistent risk basis for R, and investigate platform accounting rather than declaring exact equalities. |
| M3 MED | CSV:17-18; MD:30,85 | MISMATCH / NOT_IN_DATA: chronology/grouping of ES fills. | sheet/9IliXww64uM_05 t630 clearly shows -1@6977.5 to the left (earlier) of -1@6986.75. Their belonging to one position is not established. | Keep both markers with chart timestamps; do not call the earlier lower marker a later scale-in or collapse two fills to one trade without continuity. |
| M4 MED | CSV:44; MD:87 | MISMATCH: 'day net still +2849' is actually F10 plus F11; F7-F10 total is not +4964. | -38-2121+259+4964=3064; 4964-2115=2849. Visible daily P/L at F11 close is 22239.02. | Name interval totals explicitly; separate day P/L, trade P/L and sequence P/L. |
| L1 LOW | MD:4,10-11,47,51,81,90 | MISMATCH: stale status/inventory summaries. | F3 has frame evidence, not transcript only; DyS captions exist; current CSV has 72 records/73 lines. At 4 frames per sheet, 280 sampled frames are not 280 sheets. | Replace competing FINAL/status paragraphs with a dated inventory and historical changelog. |

## Per-row audit

Each row below refers to CSV line and its exact `frame` path (already opened). M=MATCH, X=MISMATCH, N=NOT_IN_DATA. Columns: D=date, T=trade time/session, K=market, S=side/position state, Q=quantity, E=entry, SL=stop, TP=target, EX=exit price/type, W=setup/management words. A MATCH for a no-position row means sampled visible state only. For management rows missing entry, N is intentional. No EX is directly certified by the cited stills. Dates for all rows are N as complete execution dates, including F1's inferred month and F4's filename-derived date. Supplemental evidence is explicitly named where used.

| CSV line / ID | D | T | K | S | Q | E | SL | TP | EX | W | Evidence / limitation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 F1 | N | N | M | M | M | M | M | N | N | M | PNG 0090 entry/stop; target and full labels in sheets02-04, not this crop. |
| 3 F1-m1 | N | N | M | M | M | N | M | N | N | M | PNG0240 25640, +2550; target outside crop. |
| 4 F1-m2 | N | N | M | M | M | N | M | M | N | M | sheet02 t300/330. |
| 5 F1-m3 | N | N | M | M | M | N | M | M | N | M | t450; t480/510 confirmed in supplemental sheet04. |
| 6 F1-x | N | N | M | N | N | N | M | M | N | M | sheet04 prior live labels; equity bar not execution. |
| 7 F2 | N | M | M | M | N | N | N | N | N | M | Chart levels match annotations, not proven fills; VTT:394-706,826-1002. |
| 8 F3a | N | N | M | M | M | M | N | N | N | M | t90 +2 24544.50; protection-wall annotation t30. |
| 9 F3b | N | N | M | M | M | M | M | M | N | M | t120 +12; target reads 24656.26 preview; not filled TP. |
| 10 F3c | N | N | M | M | M | M | M | M | N | M | t180 label risking 980 to make 25000; cash equality M2. |
| 11 F3c-m1 | N | N | M | M | M | N | M | N | N | M | t270 stop 24568.25 label 0; target off panel. |
| 12 F3c-m2 | N | N | M | M | M | N | M | M | N | M | t300 24584.75, 4620. |
| 13 F3c-m3 | N | N | M | M | M | N | M | M | N | M | t330 24604 and 24647.25. |
| 14 F3c-x | N | N | M | M | N | N | N | N | N | M | t360 flat, daily 28485; +22017 arithmetic matches. |
| 15 F2-m1 | N | M | M | N | N | N | N | N | N | M | Distribution box 21441.14-21448.84; positions not shown. |
| 16 F2-x | N | M | M | N | N | N | N | N | N | M | Low ~21250/CVD reversal; no fill. |
| 17 F4a | N | X | M | M | M | M | N | N | N | M | -1@6986.75; file clock not entry clock. |
| 18 F4b | N | X | M | M | M | M | N | N | N | X | -1@6977.5 earlier than F4a; scale-in unproven. |
| 19 F5 | N | N | M | M | M | M | M | M | N | N | -15 24960.28; setup wording needs own quote, not merely boxes. |
| 20 F5-m1 | N | N | M | M | M | N | M | N | N | M | -17 open, +15 STP, not all size protected. |
| 21 F5-m2 | N | N | M | M | M | M | M | N | N | M | -18 average24959.18/STP24961.25; TP off cited panel. |
| 22 F5-m3 | N | N | M | M | M | N | M | N | N | M | Observed pullbacks/unchanged stop at sampled times. |
| 23 F5-m4 | N | N | M | M | M | N | M | M | N | M | t630 stop24925/TP24917. |
| 24 F5-x | N | N | M | M | N | N | N | N | N | M | t660 flat/+2331.50; +11909 matches, exact exit unknown. |
| 25 F6 | N | M | M | M | M | M | M | N | N | M | t270/300 +4 average24914.33; caption value-area-low in sheet03 t390. |
| 26 F6-m1 | N | N | M | M | M | M | M | N | N | M | t360 still4, t390 6; do not assign6 to entire interval. |
| 27 F6-m2 | N | N | M | M | M | M | M | M | N | M | t450 zero label24914.50, TP25001. |
| 28 F6-m3 | N | N | M | M | M | M | M | M | N | M | t480/540/600 24954.50/24966.50/24971. |
| 29 F6-x | N | M | M | M | N | N | M | M | N | N | Flat/+21290; TP cause inferred (H2). |
| 30 F7 | N | M | M | M | M | M | M | M | N | M | Derived25022.75 vs displayed25022.70 (approximate); txt:478-520. |
| 31 F7-m1 | N | N | M | M | M | N | M | N | N | M | t1275 stop25006.75; txt:525-533. |
| 32 F7-x | N | M | M | M | N | N | N | N | N | M | Flat21252, -38; txt:533-538 supports auction failure, not fill price. |
| 33 F8 | N | M | M | M | M | X | M | N | N | M | Average25034.53; txt:546-558. |
| 34 F8-x | N | M | M | M | N | N | M | N | N | N | Flat19131; -2121 matches; slippage/cause unverified. |
| 35 F9 | N | M | M | M | M | M | X | N | N | M | Average25034.25 approximately; preview25019.44 then submitted25019.50; txt:575-598. |
| 36 F9-m1 | N | N | M | M | M | N | M | N | N | M | Stop held at25019.50; covers4, open8. |
| 37 F9-x | N | M | M | M | N | N | N | N | N | M | Flat19390, +259. |
| 38 F10 | N | M | M | M | M | X | M | N | N | M | Average~25040.00; txt:631-645. |
| 39 F10-m1 | N | N | M | M | M | M | M | M | N | M | t1600/1625 25043/25038->25051.50/25074.25. |
| 40 F10-x | N | M | M | M | N | N | M | M | N | N | Flat24354; exact TP fill unknown. |
| 41 F10-z | N | N | M | M | M | N | N | N | N | M | t1900/1925 flat24354 only; cited sheet begins1875. |
| 42 F11 | N | M | M | M | M | M | M | N | N | X | Supplemental w7_00 t2800 supports prices; adds are STP, target preview. |
| 43 F11-m1 | N | M | M | M | M | M | M | N | N | M | +8 average25107.20/STP25094.25; approx25107 accepted. |
| 44 F11-x | N | M | M | M | N | N | M | N | N | N | Flat22239.02, -2114.98; day-net wording wrong. |
| 45 F12 | N | M | M | M | M | X | X | N | N | N | Average25105.78 t3100; stop25089.75; claimed cash/width inconsistent. |
| 46 F12-m1 | N | M | M | M | M | M | M | M | N | M | +8 25107.33/25098.50; white preview correctly flagged non-order. |
| 47 F12-m2 | N | M | M | M | M | X | X | X | N | M | +10 25108.50/25098.75/25148.75 at3150. |
| 48 F12-x | N | M | M | M | N | N | M | N | N | N | Later25098.25 observed; flat20668, -1525; stop cause unproven. |
| 49 F13 | N | M | M | M | M | X | M | X | N | N | Average25108.90; +2 buy LMT25104.75; causal label not sourced. |
| 50 F13-m1 | N | M | M | M | M | X | M | N | N | M | Average25108.05; STP8/open10. |
| 51 F13-x | N | M | M | M | N | N | M | N | N | N | Flat17758; txt:1451-1457 supports closure/P&L, not slippage account. |
| 52 F-noTrade-3575-3750 | N | M | M | M | M | N | N | N | N | M | Cited3725/3750 flat; earlier3575 in w10_00; preview at3600 does not establish a submitted order. |
| 53 F14 | N | M | M | M | M | M | M | M | N | M | +8 25101.38/25086.25/25186.75; txt:1565-1592. |
| 54 F14-x | N | M | M | M | N | N | M | N | N | N | t3950 flat15147; -2611 matches, precise cause unverified. |
| 55 F-noTrade-4025-4275 | N | M | M | M | M | N | N | N | N | M | Cited4125-4200 flat15147; full interval N. |
| 56 F-noTrade-4275-4525 | N | M | M | M | M | N | N | N | N | M | Cited4275-4350 flat/journal; rest N. |
| 57 F-noTrade-4775-5025 | N | M | M | M | M | N | N | N | N | M | Chart4875/4925/4950 flat; t4900 talking head contradicts all4850-4950 chart claim. |
| 58 F-noTrade-5025-5275 | N | M | M | M | M | N | N | N | N | M | 5125-5200 flat15147; rest N. |
| 59 F-noTrade-5275-5525 | N | N | N | N | N | N | N | N | N | M | Talking heads5275-5350; account state not visible. |
| 60 F-noTrade-5525-5775 | N | M | M | M | M | N | N | N | N | M | 5525-5575 flat;5600 heads; rest N. |
| 61 F-noTrade-5775-6025 | N | M | M | M | M | N | N | N | N | M | 5875-5950 flat, hypothetical drawn path. |
| 62 F-noTrade-6025-6275 | N | M | M | M | M | N | N | N | N | M | 6025-6100 flat15147; rest N. |
| 63 F-noTrade-6275-6525 | N | M | M | M | M | N | N | N | N | M | 6400-6450 flat;6375 heads; rest N. |
| 64 F-noTrade-6525-6775 | N | M | M | M | M | N | N | N | N | M | 6525 flat;6550-6600 heads; rest N. |
| 65 F15-draft | N | M | M | N | N | M | M | M | N | X | Drawing LONG10/25010.75/24999.25/25087.50 matches as plan only; open qty0. txt:2854-2870. |
| 66 F-noTrade-7025-7275 | N | M | M | M | M | N | N | N | N | X | Drawing remains7050, gone7100; never submitted ticket proven. |
| 67 F-noTrade-7275-7525 | N | M | M | M | M | N | N | N | N | M | 7400/7450 flat; others heads. |
| 68 F-noTrade-7525-7775 | N | M | M | M | M | N | N | N | N | M | 7525-7600 flat; rest N. |
| 69 F-noTrade-7775-8025 | N | M | M | M | M | N | N | N | N | M | 7825/7850 flat;7775/7800 heads. |
| 70 F-noTrade-8025-8275 | N | M | M | M | M | N | N | N | N | M | 8250 flat,8225 heads; rest N. |
| 71 F-noTrade-8275-8493 | N | M | M | M | M | N | N | N | N | M | 8300 flat; cited sheet ends8350, video-end assertion N. |
| 72 F-noTrade-Is1H-0-250 | N | N | N | N | N | N | N | N | N | M | Agenda200/225; no chart, no account-state evidence. |
| 73 F-noTrade-Is1H-250-500 | N | N | N | N | N | N | N | N | N | M | Board450/475: shift satisfaction from EOD result to process. |

## Backtest readiness (12 items applied for relevance)

No backtest is present in these two ledger files and none was run. These are readiness observations, not a backtest verdict. Source: PRE_REG_TEMPLATE.md numbered sections 1-12.

| Item | Audit result |
|---|---|
| 1 Source home | Partial MATCH: NQ/ES visible; dates/timezones, exact holdings NOT_IN_DATA (H3). |
| 2 Ground truth/design-check | FIX-FIRST: fields/identities wrong; no design/check column or split in CSV:1. |
| 3 Recall and fire rate | NOT_IN_DATA in scope; no encoding test claimed or run. |
| 4 All proof inputs | Images/captions show bubble/profile context; replayable aggressor data NOT_IN_DATA in ledger. |
| 5 Profile parity | NOT_IN_DATA; annotated levels are observations, no feed parity test supplied. |
| 6 Costs/noise/fee share | NOT_IN_DATA; dollar point arithmetic present but accounting not reconciled (M2/H2). |
| 7 Touch/trade-through/passive entry | NOT_IN_DATA; distinguish STP/LMT/preview before testing (H1/H5). |
| 8 Exit management | Partial MATCH for observed trails; precise fill causes NOT_IN_DATA, universal rule MISMATCH. |
| 9 Matched null | Not applicable to citation audit; NOT_IN_DATA for any future run. |
| 10 Power | No backtest N forecast; ledger counts require H4 repair. No edge/no-edge inference made. |
| 11 Holdout and trials | No holdout read or run; no trial added. Date repair and grouped design/check split required before future use. |
| 12 Stratification | No backtest readout; NOT_IN_DATA. |

## Follow-up cards

Six SONNET cards created with `python scripts/dev/tasks.py new <title> --id <id> --lane SONNET --layer fabio --prio 2 --ref <this report>`: Existing related cards listed in LAYERS.md:70-73 overlap H1-H3; new cards reference this report's expanded evidence rather than treating those earlier cards as proof of a fix.

| Finding | Card ID |
|---|---|
| H1 | `fabio-audit-20261013-prices` |
| H2 | `fabio-audit-20261013-exits` |
| H3 | `fabio-audit-20261013-dates` |
| H4 | `fabio-audit-20261013-counts` |
| H5 | `fabio-audit-20261013-rules` |
| H6 | `fabio-audit-20261013-attribution` |

Validation: CSV parsed with Python csv.DictReader; report row numbers equal 2 through 73 exactly once; all six follow-up JSON cards exist with lane SONNET. No software tests or backtests required for this evidence audit. Task CLI regenerates LAYERS.md as a side effect; its original bytes were restored so the delivery stays within lab-report/task scope.
