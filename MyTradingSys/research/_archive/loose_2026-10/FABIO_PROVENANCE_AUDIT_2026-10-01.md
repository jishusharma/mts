# FABIO PROVENANCE AUDIT 2026-10-01

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio (CLD, ANA). Input: FABIO_V3_SPEC.md section 7.1, 41 rows P01-P41
[disk: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:190-232]. Read-only; no spec or code file edited.
One reader (this session). No kappa, no second reader: the Tom block already has the same single-reader limit and W3 could not
be run blind (REVALIDATION_ACTIONS_2026-10-01.md, W3). Counts below are a one-reader measurement.

## Method
1. Quotes: every quoted passage in the source column was checked as a case- and punctuation-insensitive substring of the named
   transcript after removing [m:ss] stamps [run: scripts in session scratchpad; 5 transcripts fZlNGWvd2Ko, jasv3L-d8ZE, 0jM5Y31YJak,
   8CWKfoSJu3c, LQvv5xgy_ik]. Result: 41 rows, 39 quoted passages checked, 39 found, 0 missing. Seven rows carry no quote: P25, P30, P31, P34, P35, P39, P41.
   One citation points at the second occurrence of a quote (P15, note). `0j` has all text on line 4, so its location is the line only.
2. Classification uses the Tom definitions [disk: PROVENANCE_AUDIT_TOM.md:5]: SOURCED = a quote supports the value; CONCEPT-ONLY = the
   trader names the idea, the number is ours; NO-SOURCE = no idea behind it, or a role (veto, gate, cap) he never gives it;
   DATA-PLUMBING = no trading meaning.
3. Row rules, applied the same way to every row: spec label `FABIO` alone and the quote states the rule -> SOURCED. Any `NS-grid` or
   `NS-fixed` component with a Fabio idea quoted -> CONCEPT-ONLY (the number is ours). `NS-*` or `SAFETY` with no idea quoted
   -> NO-SOURCE. `SIM` -> DATA-PLUMBING. Rows with several parameters take the weakest decisive one.
4. Strict reading (Tom-equivalent): Tom rows whose rule is keyed on an event the code detects by proxy were CONCEPT-ONLY (for example A05, A28).
   In Fabio the events (S1 balance, S2 pressure, S3 control/absorbed, S4 big push) are built from NS-labelled numbers P01-P07
   [disk: FABIO_V3_SPEC.md:64-78]. Rows keyed on them (P08, P09, P10, P15, P17, P18, P20) move from SOURCED to CONCEPT-ONLY in the strict count.
   Which rows are event-keyed was read from section 3 and 5.2 [disk: FABIO_V3_SPEC.md:79-102,152-160]. Confidence L on the strict split.

## Counts (41 rows)
| verdict | rows (by the spec's labels) | rows (strict, Tom-equivalent) |
|---|---|---|
| SOURCED | 14 | 7 |
| CONCEPT-ONLY | 19 | 26 |
| NO-SOURCE | 7 | 7 |
| DATA-PLUMBING | 1 | 1 |
| total | 41 | 41 |

Counted by: parsing the 41 rows of the table by script and tallying the verdict assigned per row below [run: python Counter].
NO-SOURCE rows: P25, P29, P30, P31, P34, P35, P39. Two of them (P29, P30) carry the SAFETY label and are exempt from the Provenance
rule by direct operator approval [disk: MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md:15], leaving 5 binding NO-SOURCE rows.
Rows carrying an NS-grid or NS-fixed number: 25 of 41 (P01, P02, P03, P04, P05, P06, P07, P11, P12, P13, P14, P16, P19, P21, P25, P28, P30, P31, P32, P33, P34, P35, P36, P39, P40).

## Headline (the Fabio counterpart of the Tom finding)
No number that decides whether a Fabio trade exists has a Fabio quote, with two exceptions: the 30-minute initial balance (P38) and the
break-even day floor (P26). The decisive numbers are the S1-S4 windows and thresholds (P01-P07), the stop floor (P31),
the model A retrace (P35), the model B reclaim bars (P36), the day gate (P40) and the max-first-legs and Dmax caps (P30); each is NS-grid, NS-fixed or SAFETY.
The Fabio quotes support the ideas behind them (balance, pressure, absorption, failed auction, scaling, day floor), which is the Tom pattern.
Unvalidated domain: a statement that Fabio is better or worse sourced than Tom (17 percent vs 49 percent NO-SOURCE by raw row share) is NOT made: the tables have
different row granularity (Tom 74 single-item rows, Fabio 41 rows bundling up to 12 items), and no accepted method compares them.

## Findings for the operator (not decisions)
1. The spec registers NS-grid values as grids to run: 139 NY cells, 151 with stage 3 [disk: FABIO_V3_SPEC.md:245-246]. The Provenance rule says unsourced
   parameters are flagged and removed or replaced, never tuned [disk: CLAUDE.md Provenance rule]. Running the grid tunes NO-SOURCE numbers.
2. P41 hides about 12 items in one row (see note); a per-item split is needed before the count can be called complete.
3. Fabio's own transcript states a 1:19 R:R and calls it uncommon [T/8CWKfoSJu3c:83-86]; no Fabio quote supports the P31 stop floor 0.3-0.5%.
4. P12 (S7 off variant) rests on ja:70-71, a quote that does not show the side of the position being scaled.
5. The gate in the Fabio handoff ("a NO-SOURCE count for Fabio is required before any Fabio testnet entry") is met by this file's count;
   it does not say the spec is ready for testnet: 19 rows hold an NS number inside a quoted idea.

## Table
| id | parameter | value | spec label | quotes verbatim? (location) | verdict | strict | note |
|---|---|---|---|---|---|---|---|
| P01 | S1 balance; N | {60,120,240} | NS-grid | yes 0j:4 | CONCEPT-ONLY | = |  |
| P02 | k_bal; POC band | 0.8; 0.25 | NS-fixed | yes 0j:4 | CONCEPT-ONLY | = |  |
| P03 | S2 pressure p; drift q | {0.05,0.10}; 0.25 | NS-grid; NS-fixed | yes 0j:4 | CONCEPT-ONLY | = |  |
| P04 | S3 L, z_hi, r_abs, r_ctl | 60, {2.0,2.5,3.0}, 0.25, 1.0 | NS-grid (z_hi) / NS-fixed | yes 0j:4; yes 8C:42 | CONCEPT-ONLY | = |  |
| P05 | big trade = 99th/99.9th pct, prior 30 d | - | NS-fixed | yes 0j:4 | CONCEPT-ONLY | = |  |
| P06 | tier VR 1.5, 20 d, min 10 | - | NS-fixed | yes ja:25-26 | CONCEPT-ONLY | = |  |
| P07 | S4 window m | {5,15} (C), 15 | NS-grid / NS-fixed | yes 0j:4 | CONCEPT-ONLY | = |  |
| P08 | S5 trigger on the close | - | FABIO | yes 0j:4 | SOURCED | CONCEPT-ONLY |  |
| P09 | S5D / model D trigger | - | FABIO | yes fZ:40-42 | SOURCED | CONCEPT-ONLY |  |
| P10 | S6 anchor = last own control | - | FABIO | yes 8C:201-202 | SOURCED | CONCEPT-ONLY |  |
| P11 | S7 add gate; VA 70% | on; 0.70 | FABIO; NS-fixed | yes 8C:53-54 | CONCEPT-ONLY | = | Quote is about adding while already loaded with 10 contracts; supports the gate idea, not the 0.70 VA (NS-fixed). |
| P12 | S7 off | variant | NS-grid | yes ja:70-71 | CONCEPT-ONLY | = | Quote shows an add 'on the way down'; the position side in ja:66-73 is not established by the quote alone. Spec labels it an operator decision. |
| P13 | S8(a) 15 bars | 15 | NS-fixed | yes 0j:4 | CONCEPT-ONLY | = |  |
| P14 | S8(b) rule; N 60 | 60 | FABIO; NS-fixed | yes 0j:4; yes fZ:98-99 | CONCEPT-ONLY | = |  |
| P15 | S8(c) | - | FABIO | yes 8C:207-208 (also 5-6) | SOURCED | CONCEPT-ONLY | Quote occurs twice in 8C (lines 5-6 and 207-208); cited 207-208 is correct. |
| P16 | S8(d); 1-bar look-back | on (event) | FABIO; NS-fixed | yes fZ:144-146 | CONCEPT-ONLY | = |  |
| P17 | E_opp stop to BE | event | FABIO | yes fZ:113-115 | SOURCED | CONCEPT-ONLY |  |
| P18 | E_opp ratchet to pb | event | FABIO | yes fZ:132-134; yes fZ:122 | SOURCED | CONCEPT-ONLY |  |
| P19 | E_own de-risk; by stop (not size) | event | FABIO; NS-fixed | yes fZ:67-68 | CONCEPT-ONLY | = |  |
| P20 | trail after defended break | event | FABIO | yes fZ:93-96 | SOURCED | CONCEPT-ONLY |  |
| P21 | mgmt dist, be_k | {1.0,2.0} | NS-grid | yes 0j:4 | CONCEPT-ONLY | = |  |
| P22 | max adds | 2 (3 entries) | FABIO | yes fZ:152-154; yes 0j:4 | SOURCED | = | Example only (one session loaded three times), like Tom K01; the cap of 2 adds is read off that example. |
| P23 | add_mode be (default) | - | FABIO | yes 0j:4 | SOURCED | = |  |
| P24 | add_mode day | variant | FABIO, variant by operator | yes fZ:57-59 | SOURCED | = | Quote is about reducing losses by scaling; spec registers it as an operator variant. |
| P25 | add cap q1; min add 0.25 q1 | - | NS-fixed | no quote in row | NO-SOURCE | = |  |
| P26 | floor at day R 0 | - | FABIO | yes fZ:29-31 | SOURCED | = |  |
| P27 | carry; first-leg risk <= C | - | FABIO | yes fZ:15-16; yes fZ:60-61 | SOURCED | = |  |
| P28 | stop after recovery; -1R | -; -1 | FABIO; NS-fixed | yes ja:181-182 | CONCEPT-ONLY | = |  |
| P29 | daily stop | -3R | SAFETY | yes fZ:79-81 | NO-SOURCE | = | Value -3R is ours; the quote gives Fabio's own worst-session size in USD, not a rule. SAFETY: exempt by operator approval 3 (SUPERVISOR_INBOX.md:15). |
| P30 | max 10 first legs; Dmax 1.0% | - | SAFETY; NS-fixed | no quote in row | NO-SOURCE | = | SAFETY by operator approval 3. Dmax 1.0% also removes candidate trades before arming (spec 4 'no arm if D > Dmax'): eligibility gate or safety limit is an operator call. |
| P31 | stop floor f | {0.3%,0.5%} | NS-grid | no quote in row | NO-SOURCE | = | Stop floor with no Fabio quote; the spec itself says the Tom floor was unsourced (LESSONS E) and then registers {0.3%,0.5%} as a grid. |
| P32 | structural stop behind the level, +1 TICK | - | FABIO; NS-fixed | yes fZ:45-46 | CONCEPT-ONLY | = |  |
| P33 | NY cash-open window; 390; cutoff 330; window-end exit | - | FABIO; SIM; NS-fixed; NS-fixed | yes 8C:7-8 | CONCEPT-ONLY | = | 390-minute window and 330 cutoff are NS-fixed; only 'New York session' is Fabio's. |
| P34 | US_CLOSED excluded; London/Asia windows | - | SIM (operator); NS-grid | no quote in row | NO-SOURCE | = | London/Asia window times: no Fabio quote; the word 'asia' occurs 0 times in the five cited transcripts [run]. US_CLOSED list is calendar plumbing. |
| P35 | model A LVN, retrace 25% | - | NS-fixed | no quote in row | NO-SOURCE | = | Spec says 'not in these transcripts'; model A has no Fabio source in the five cited files. |
| P36 | model B reclaim 5, rest 3 bars, edge target | - | NS-fixed | yes 8C:40-41 | CONCEPT-ONLY | = |  |
| P37 | model B trail variant | variant | FABIO | yes fZ:51-52 | SOURCED | = | Quote states an aim (amazing R:R, top of the day), not a rule; weakest of the SOURCED rows. |
| P38 | model C IB 30 min | 30 | FABIO | yes LQ:841-843 | SOURCED | = | The number 30 is in the quote (verified LQ:841-843). |
| P39 | model D rest validity | 3 bars | NS-fixed | no quote in row | NO-SOURCE | = |  |
| P40 | day gate g, 20 d, open+60 | {off,0.8} | NS-grid | yes 8C:87 | CONCEPT-ONLY | = | Same video states 1:19 R:R is not common and volatility is not there every day (8C:83-88); g=0.8 is ours. |
| P41 | fees, slip, funding, fills, stop-first, TICK, B_prof, VA/LVN | - | SIM | no quote in row | DATA-PLUMBING | = | Bundle of about 12 items (fees, slippage, funding, fills, TICK, B_prof, VA/LVN, ATR, day-type 0.6, regimes, stats). Cannot be classified as one row; VA/LVN thresholds and day-type 0.6 are not plumbing. |
