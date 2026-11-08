# NEWS_DESIGN: the rules the two news builds must follow (synthesis, 2026-11-08)

**Result: of 13 news classes only CPI (33 rows) and NFP (34) earn a size prior, FOMC (23) a half one, PPI (33) none; direction is unknown for all 123 verified rows, so the chip starts at HOLD and only the market's own move (|z15d| >= 2, false rate 7% on 369 control minutes) turns it LONG or SHORT.**

- Card news-design-synthesis-1108. Inputs: `REPORT.md` (catalogue v2), `REVIEW_OPUS.md` (statistics lens), `REVIEW_MARKET.md` (market lens), OPERATOR_PREFS.md, OPERATOR_REPLY_FORMAT.md, mts_bible/BIBLE.md. Check: `python check_design.py`.
- Builds that follow this file: `news-weight-bias-flash-1108` (weight, chip, flash) and `cbp-events-to-watch-wire-1108` (event strip). Context only: no gate, no order, no sizing.
- DECISION (OURS): the "dense-symbols artifact design memo" named in the card is not in the repo (git grep finds only the card); layout follows OPERATOR_PREFS.md section 1 and OPERATOR_REPLY_FORMAT.md.
- Every rule row ends with its evidence: a count from the catalogue (section and n) or the word OURS (our choice, no row behind it; the build labels it so).

## 1. What the three sources agree on

| point | catalogue | Opus review | market review |
|---|---|---|---|
| CPI minute move is real | n 33, med abs z15d 2.48 vs control 0.72, p 0.0000 | SAFE | SAFE |
| NFP minute move is real but rare | n 34, p 0.0003, share abs z15d > 2 = 24% vs 8% | SAFE ("2/3 no bigger than noise") | SAFE |
| FOMC window holds two events (14:00 and 14:30 ET) | n 23, med tpk60 37 min | WEAK | WEAK |
| PPI is at control level | n 33, p 0.1710, 21% vs 6% above 2 | WEAK | noise |
| every OURS class is UNKNOWN | 0 of 68 own-grouping rows verified | UNKNOWN x 9 | UNKNOWN x 9 |
| direction is unknown | 0 of 123 verified rows have a surprise sign | direction UNKNOWN for every class | sign unreadable without surprise |
| "same news does not work twice" is not shown | rho -0.22 / 0.03 / -0.34 / 0.14, none reaches 0.34-0.41 | UNKNOWN | surprise compression, untested |
| pre/post 2025-01-20 is a time split, not Trump | p 0.272 / 0.606 / 0.079 / 0.357, no placebo | cannot be attributed | vol regime, not the president |
| speed columns sit near the random-walk null | share abs r60 > abs r15 56-70% vs null 73% | only tpk60 differs from noise | agrees, reads retr60 as fade |

## 2. Class table: keep, change or drop (call per class, with its count)

Calls are against the class list of the original build card (hack SHORT, ETF LONG, SEC suit SHORT, hot CPI SHORT, cool CPI LONG, rate cut LONG, war SHORT, delist SHORT). P = class prior points (section 3).

| class | call | what the build does | evidence (REPORT.md) |
|---|---|---|---|
| MACRO_CPI | KEEP | P 24; flash at T-15, T0; direction stays a 'prior' tag | n 33 verified; share abs z15d > 2 = 61% vs 7% control; p 0.0000 |
| MACRO_NFP | KEEP | P 10; flash at T-15, T0; HOLD by default (most prints are noise) | n 34; 24% vs 8%; p 0.0003; retr60 0.55 vs null 0.33 |
| FOMC | CHANGE | P 12; statement window 0-25 min only; presser is a second strip row at T+30 | n 23; p 0.0008; med tpk60 37 min; 2024-06-12 presser r60 -0.96 |
| MACRO_PPI | DROP | P 3 (control level); strip row without flash; chip HOLD | n 33; p 0.1710; 16 of 34 PPI days share the minute with claims |
| ETF_REGULATORY | CHANGE | no P; 'prior LONG/SHORT' tag only; chip HOLD until the market confirms | 0 of 8 verified |
| HACK_EXPLOIT | CHANGE | no P; 'prior SHORT' tag only; HOLD until confirmed | 0 of 8 verified; 1 timed row |
| TRUMP_POLICY | CHANGE | no P; no direction tag; HOLD until confirmed; show weekday/weekend | 0 of 11 verified |
| TARIFF_TRADE | CHANGE | no P; no direction tag; HOLD until confirmed | 0 of 9 verified; tar-20251010 placeholder t0 missed the move |
| GEOPOLITICS | CHANGE | no P; 'prior SHORT' tag only; HOLD until confirmed | 0 of 6 verified (n < 8) |
| MACRO_OTHER | DROP | not a class in the panel; Jackson Hole goes to the strip as FOMC-type row | 0 of 8 verified; 3 timed rows, n 2 per subtype |
| COURT_LEGAL | DROP | untagged headline, W from K and I only | 0 of 10 verified; dates known in advance |
| PROTOCOL | DROP | untagged headline | 0 of 4 verified; surprise zero by construction |
| BOJ_JAPAN | DROP | untagged headline | 0 of 4 verified; works over days, not minutes |

## 3. Weight formula: W = F x (P + K + I), 0-100

Only parts with a catalogue column behind them. Dropped from the original card: source tier and the two-source corroboration bonus (no row measures either; lean rule) and the 15-min half-life (replaced by the measured windows).

| part | rule | evidence |
|---|---|---|
| P class prior, 0-40 | 40 x share of verified events with abs z15d > 2: CPI 24, FOMC 12, NFP 10, PPI 3, every other class 3 | shares 61% / 30% / 24% / 21% (section 4, n 33 / 23 / 34 / 33); PPI set to the 7% control rate because p 0.1710 |
| K confirmation, 0-40 | BTC since the headline minute, from the page's own 1m feed: abs z15d >= 2 and vr5 >= 4 gives 20; abs z15d >= 4 gives 40; else 0 | control share abs z15d > 2 = 7% (369 windows); vr5 4 is under every class median (4.62 to 11.93); 15 of 123 rows reach abs z15d 4.2 or more |
| z15d definition | r since headline / (stdev of 1m returns over the prior 24 h x sqrt(minutes elapsed)); never the prior-hour stdev | z15 (prior hour) depends on the clock; z15d is the baseline of every table (REPORT section 1) |
| I Tree importance, 0-20 | 2 x Tree importance (0-10) | OURS mapping; importance scale is SOURCED (Tree), threshold 7 from the panel card |
| F freshness, 1 to 0 | 1.0 for the first 15 min after the headline minute, then linear to 0 at 60 min | 15 and 60 are the measured windows (123 rows); med tpk60 32-37 min lies inside; linear shape OURS |
| before a scheduled t0 | W = P + I, chip HOLD, text "due in mm:ss" | no catalogue column before t0; OURS |
| units | all thresholds in z (sigma), none in percent | percent fell post 01-20 (FOMC 0.58 to 0.21, NFP 0.56 to 0.32) while CPI z did not (2.34 to 2.73) |
| era | no Trump-era term | p 0.272 / 0.606 / 0.079 / 0.357 on the split, no placebo run |
| overlap | second event within 4 h gets K from its own minute only; P halved | 8 rows within 4 h and 4 SAME_DAY pairs (Gaps) |
| hover | shows P, K, I, F and the label SOURCED or OURS per part | OURS |

## 4. Flash rules: when, how long, what stops it

| rule | when | evidence |
|---|---|---|
| headline flash | W >= 60 | OURS threshold; the parts under it are counted |
| market flash | K = 40 (abs z15d >= 4) whatever the class | 15 of 123 verified rows reach abs z15d 4.2 or more (section 9) |
| scheduled flash | CPI, NFP, FOMC statement: at T-15 min and at T0 | p 0.0000 / 0.0003 / 0.0008, n 33 / 34 / 23 |
| FOMC presser | second flash at T+30 min | med tpk60 37 min; 2024-06-12 r60 -0.96 at the presser, r15 0.00 |
| no flash | PPI at T0; any OURS class at its event time; T-60 (countdown only) | PPI p 0.1710; 0 verified own-grouping rows; no column before t0, OURS |
| how long | until he opens the tab, else until F x (P + K + I) drops under 60, at most 60 min | 60 = r60 window (123 rows); medians tpk60 32-37 min |
| what stops it | opening the tab stops it; a newer item that qualifies re-flashes once; a bias flip LONG to SHORT or back re-flashes once; a flip to HOLD does not | OURS |
| rate cap | at most one flash per headline and one per scheduled minute | OURS |

## 5. Bias rules: LONG, SHORT, HOLD

| chip | rule | evidence |
|---|---|---|
| HOLD (default) | every item starts HOLD; a 'prior' tag (section 2) is shown beside it, it never sets the chip alone | 0 of 123 verified rows carry a surprise sign; sign agreement with the previous event 36-52% (coin flip) |
| LONG | K >= 20 and the BTC move since the headline is up and no 'prior SHORT' tag | false rate 7% (369 control minutes) |
| SHORT | K >= 20 and the BTC move since the headline is down and no 'prior LONG' tag | same 7% |
| HOLD when no move | K < 20 | 7% of ordinary minutes pass abs z15d 2; the move is the only sign evidence |
| HOLD when prior and market disagree | 'prior' tag direction opposite to the sign of the move | OURS (both sources unverified in sign) |
| HOLD when the move already happened | more than 35 min since the headline or t0 | med tpk60 32-37 min; retr60 0.32-0.55 given back by minute 60 |
| HOLD when overlapping | another catalogue or strip event within 4 h | 8 rows within 4 h, 4 SAME_DAY |
| HOLD for PPI | always, whatever K | p 0.1710 vs control |
| HOLD for analyst split | strip row where analysts split LONG and SHORT | OURS; 1 of 1 pre-event analyst call is n 1 |
| hot/cool wording | "hot CPI -> SHORT, cool -> LONG" stays a 'prior' tag until actual vs consensus rows exist | 0 surprise rows; section 5 of REPORT.md empty |
| reason text | each chip shows one reason: "no move", "move +z 3.1 v 12", "prior vs move", "late 41 min", "overlap FOMC", "PPI" | OURS |

## 6. Repeat-decay rule (the "does not work twice" question)

| rule | evidence |
|---|---|
| no decay factor in W: the n-th CPI gets the same P as the first | rho(seq, abs z15d) -0.22 FOMC, 0.03 CPI, -0.34 NFP, 0.14 PPI; 5% needs 0.34-0.41 |
| show the last same-class move under the strip row: date, r15, z15d, vr5 | context he reads himself; nfp-2026-09-04 -2.03% then the next NFP -0.16% |
| the sign of the last move never sets the chip | sign agreement 36-52% over 22-33 pairs |
| word tag "flushed last time" when the previous same-class event had vr5 > 15; no weight change | 10 of the 15 largest reactions had vr5 above 15 (section 9); forced-flow mechanism is a hypothesis of the market review |
| the question stays open until surprise rows exist | 0 of 123 rows; follow-up card news-effect-surprise-data-1108-fill-actu |

## 7. Event strip rules (cbp-events-to-watch-wire-1108)

| rule | evidence |
|---|---|
| rows: next 5 of CPI, NFP, FOMC statement, FOMC presser (T+30), PPI; from the BLS and Fed schedules | 123 verified rows come from those pages (calendar_cache.json) |
| per row: countdown, P, last same-class move, analyst count and LONG/SHORT/HOLD split | 31 mentions of 6 events by 4 analysts (section 8) |
| analyst direction is a count, never the chip | 1 of 1 before-event hit = n 1 |
| shutdown-delayed prints get the word "stale" | 3 rows: cpi-2025-10-24, nfp-2025-11-20, ppi-2025-11-25 |
| headline that names a strip event links to its row and inherits its P | OURS |
| events analysts name loosely ("week of") show at day start, no flash | OURS |

## 8. Open disagreements between the reviews (stated, not hidden)

| topic | Opus review | market review | design takes |
|---|---|---|---|
| NFP fade | speed columns match noise except tpk60 | retr60 0.55 vs null 0.33 is a real two-stage fade | no class-specific fade; HOLD after 35 min for all (OURS) |
| fomc-2024-06-12 (CPI same day) | flag it | exclude it from the class stats | P uses the report's n 23 as published; the build re-derives P without SAME_DAY rows when the catalogue is rebuilt |
| PPI | WEAK: 24% vs 14% above 2 (z15, own control) | noise: p 0.17, claims at the same minute | noise (P 3, no flash, HOLD): the conservative reading |
| why news stops working twice | cannot be claimed as built | forced flow (vr5 > 15) and surprise compression, with tests | word tag only, no weight term |
| baseline | own control on z15 (prior hour): CPI 2.79 vs 0.80 | z15d (24 h): 2.48 vs 0.72 | z15d; z15 depends on the clock |
| era | UNKNOWN, no attribution | fewer percent, same sigma: weight in z | z units, no era term: both satisfied |
| source tier, corroboration bonus | not measured | not measured | dropped (OURS, lean rule) |

## 9. Mock of the News tab (one screen; numbers are catalogue rows)

```
NEWS  >> flashing: CPI 12:30Z  W 84  SHORT (move)                        12:41Z
-------------------------------------------------------------------------------
UPCOMING    | in        | P  | last same-class            | analysts
CPI  Oct    | now +11m  | 24 | 10-14 -1.21% z-7.6 v28     | 3  0L/2S/1H
PPI  Oct    | 1d 00:00  |  3 | 10-15 -0.23% z-1.1 v5      | 1  0L/1S/0H  no flash
NFP  Oct    | 2d 23:49  | 10 | 10-02 -0.16%               | 1  0L/0S/1H
FOMC stmt   | 5d 05:19  | 12 | 10-28 -0.03% z-0.2         | 2  1L/1S/0H  HOLD
FOMC press  | 5d 05:49  |  - | 10-28 r60 +0.19%           | -
-------------------------------------------------------------------------------
HEADLINES   W = F x (P + K + I)      hover W for parts, SOURCED / OURS per part
12:30 | BLS  | CPI Sep                       | W 84 | SHORT | move -z 7.6 v 28, 2 min
12:31 | Tree | BTC drops after CPI           | W 41 | HOLD  | overlap CPI
11:58 | Tree | exchange halts withdrawals    | W 23 | HOLD  | prior SHORT, no move
09:14 | Tree | SEC delays ETF decision       | W  9 | HOLD  | prior LONG, late 3 h
```

## Gaps

- No weight part reads positioning, funding, prior move or cross-asset beta (market review section 3): no catalogue column exists for them yet; add when a card fills them.
- P values are hand-copied from REPORT.md section 4; the build must read them from `news_events.csv` so a catalogue rebuild changes P without a design edit.
- The FOMC statement/presser split and the SAME_DAY exclusion are not in the catalogue yet; P 12 for FOMC is the mixed number.
- Nothing here was tested on a live headline; fail-first tests per rule are named in the two build cards.
