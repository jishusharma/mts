# EXTRACTION ROUND 2 2026-10-01

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio (CLD, ANA; no subagent was spawned: budget row >= 85 percent assumed, and no item met the two Opus conditions).
Method: MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md. Outputs: extracts/v2/tom/<id>_v2.md (five files). One reader/extractor: this session.
Tag convention as in REVALIDATION_ACTIONS_2026-10-01.md: `[disk: path:line]`, `[T/<id>:<line>@<char>]` (char offset of the sentence containing the quote), `[run: ...]`.
A rule claim from a transcript that has no TOM-NNN id is tagged NO-SOURCE with the candidate source named; this session assigns no TOM ids.

## Selection (how counted)
Ranking = (count of the whole words risk, stop, target, size) per 1,000 words, counted by regex over the body of each transcript [run: python, word-boundary, case-insensitive].
Tom set = 57 ids found in the filenames under extracts/fresh, extracts/processed/tom and in TOM_VERBATIM_INDEX.md (by this session's count); UrZ4vpHJ97g is outside that set because it was never extracted, and is identified as Tom by the text ("Tom says that you can earn much much more", "Tom, tell us more about this") [T/UrZ4vpHJ97g:7@16525] and [T/UrZ4vpHJ97g:7@19427].
- 5.1a (already extracted): 4MoNjEQ2Dd8, as specified.
- 5.1b (not yet extracted): UrZ4vpHJ97g, 11.7 per 1,000 words, the highest among never-extracted ids whose speaker is Tom by the text. Excluded on speaker: Wvq1TZh8aF0 (13.1, Vishal Malkan RSI), 0KyIEdvVKMQ (9.8, no title, not Tom's style), cBkwYjn-6mM (guest interview).
- 5.2 (top three of the Tom set excluding 4MoNjEQ2Dd8): WSCIURybK3U 16.2, kXhIAug0Gh8 13.6, tS6ZEiHj8gQ 11.1. Next in rank, not done: UOBgXV20yCM 9.5, hQ8sOq67x5o 9.0.
Each of the three has a V1 extract; a V1 comparison was done only for 4MoNjEQ2Dd8, as the task asks.

## 5.1 Method audit: V2 against V1 on 4MoNjEQ2Dd8
V1 = extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md (45 in-vivo codes, 27 tiered rules, 4 negative rules, a 16-step "live trade sequence"). V2 was written from the raw transcript before V1 was opened (the instrument inference was corrected afterwards, see row I).
Per claim, yes or no. "V2 recovered" is judged against the transcript text, not against V1.

| # | claim | V1 | V2 recovered? | evidence |
|---|---|---|---|---|
| A1 | (a) order: entry comes before the proof (absorption read after entry) | yes (steps 4 then 5) | yes | V2 rows 2, 7, 8 [disk: extracts/v2/tom/4MoNjEQ2Dd8_v2.md] |
| A2 | (a) the 603 stop move is late (pos 91), after the adds (pos 70-71) | no: V1 step 11 precedes step 12 | yes | V2 rows 36-37 (pos 70-71) then row 45 (pos 91); V1 [disk: extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md:346-348] |
| A3 | (a) a separate first stop adjustment at pos 50 ("We now adjust our stop", level not stated) | no (merged into step 11) | yes | V2 row 27; grep "adjust our stop" in V1 returns nothing [run] |
| A4 | (a) the second partial is executed at pos 95 ("Let's take out another position") | no (V1 step 13 uses the conditional "what you've got, you've got" as the second partial) | yes | V2 row 47 vs row 40 (planned); "take out another position" is absent from V1 [run] |
| A5 | (a) entry, partial, add and exit prices are not stated | no: V1 gives ~25,600 (entry), ~25,620 (partial), ~25,600 (add), ~25,620 (exit), ~25,620+ (second partial): 5 of 16 steps carry a price the transcript does not state for that action | yes (levels left as stated or "unknown") | V1 [disk: extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md:337-351] |
| A6 | (a) switch to the 1-minute chart (pos 16) | yes (step 6) | no: V2 has no row for a time-frame switch | V1 step 6; the method has no row type for it |
| B1 | (b) conditions are tied to the decision they govern | no: conditions sit inside quotes, no condition field | yes: a condition cell on every row; 30 of 52 rows carry one | V2 3.2 table |
| B2 | (b) count of conditional phrases recovered | 11 of 34 | 25 of 34 (24 before row 43b was added) | crude measure: regex found 34 conditional phrases ("as long as", "if it/we ...", "otherwise", "unless", "we need", "it's over") in the transcript; "recovered" = the first five words of the phrase occur in the extract [run]. Some regex hits are not conditions ("we need to do now"), so the ratio is indicative only |
| B3 | (b) a phrase V2 missed | - | one: "if we push above it, then the sky's is the limit; as long as we're below it ... consolidating" (pos 83) | found by this count, added as row 43b |
| C1 | (c) reject: scalping at the first resistance | present but filed as a trader-type note (T1.13), not as a reject | yes, as REJECT (row 15) | V1 [disk: extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md:165-170] |
| C2 | (c) reject: moving the stop before an "opposite" range exists | yes (negative rule 3.1) | yes (row 31) | V1 section 3 |
| C3 | (c) reject: not doing something "so as not to" [cut] | yes (3.3, flagged incomplete) | yes (row 35, reason cut [?]) | both stop at the cut sentence |
| C4 | (c) an admitted error: "I placed an order too early" | no (grep "too early" and "placed an order" in V1 return nothing [run]) | yes (row 43, ERROR) | |
| C5 | (c) rejects V1 missed entirely | 0 of 3 REJECT rows missed; 1 mis-typed; 1 ERROR row missed | | |
| I | instrument | V1 header "Asset Traded: DAX futures (implied by price levels ~25,600)", written as a field value | V2 "not stated" plus a separate inferred field; my first inference (NASDAQ) was wrong against the transcript's own wording, where NASDAQ and S&P are other markets watched (rows 10, 32); corrected to "DAX, a guess" after reading V1 | the field split works; the inference inside it still drifted |
| T | trade count | V1 one sequence | V2 one trade block, 5 PARTIAL rows (2 executed, 3 planned), 3 ADD rows (1 planned, 2 executed), 4 STOP_MOVE rows | V2 3.2 |

Summary for 5.1a: of the 3 questions, (a) order of events: yes (V2 corrected 3 order errors in V1: A2, A3, A4); (b) "as long as" conditions: yes (25 of 34 phrases against 11 of 34, crude measure); (c) rejects V1 missed: none missed entirely, one mis-typed (C1), one admitted error missed (C4).
Sample size is n = 1 video. Generalising to "V2 recovers more than V1" is an unvalidated domain and is not claimed. V2 cost: not measured (no wall-clock or token log kept).

5.1b (UrZ4vpHJ97g, never extracted): no V1 baseline exists, so no comparison is made. V2 result: 27 decision rows, 0 trades, 3 illustrations (rows 6, 17-19), 8 anchors all passing, 3 REJECT rows (1% default risk, no predefined target, deleting the target).
Method gap found on this video and on WSCIURybK3U: V2 has no row type for a hypothetical plan, so illustrations were logged as ENTRY/STOP_SET/TARGET_SET with "(illustration)" in the type cell. A lecture video gives 16-19 LESSON rows and no trade block; the V2 trade-centred format captures little of it (UrZ4vpHJ97g: 19 of 27 rows are LESSON; WSCIURybK3U: 16 of 24).

## 5.2 Scale extraction (counts)
| id | body chars | decision rows | trades (illustrations) | anchors | rows with a condition | [?] rows | checker |
|---|---|---|---|---|---|---|---|
| 4MoNjEQ2Dd8 | 22120 | 52 | 1 | 21 | 30 | 7 | PASS: 0 problem(s) |
| UrZ4vpHJ97g | 20103 | 27 | 0 (3) | 8 | 3 | 2 | PASS: 0 problem(s) |
| WSCIURybK3U | 12681 | 24 | 0 (2) | 7 | 1 | 0 | PASS: 0 problem(s) |
| kXhIAug0Gh8 | 8790 | 34 | 4 | 13 | 9 | 3 | PASS: 0 problem(s) |
| tS6ZEiHj8gQ | 10785 | 28 | 2 | 10 | 5 | 2 | PASS: 0 problem(s) |
| total | 74479 | 165 | 7 (5) | 59 | 48 | 14 | 5 of 5 pass |
Checker = `python scripts/dev/verify_extract_quotes.py extracts/v2/tom/<file>`; counted by script over the table rows [run]. All 59 anchors passed on the first run.
Extra check this session (the official checker reads anchor lines only): every quoted fragment inside the table rows was tested as a normalised substring of its transcript [run: python over 267 fragments]. First writing: 7 of 267 (2.6 percent) were not verbatim (paraphrase, two passages joined, ASR repeat counts); all 7 were corrected; 3 remaining hits are the table header label "as long as", not quotes. Gap: V2 text in the `decision` column can drift from the transcript without the gate noticing; proposed fix below.
Kind of videos: 2 of the 5 are lectures (risk and money management) with no trade, and 3 are trade walk-throughs (one of them a day review with 4 trades).

## 5.3 Falsification-first (counts)
For every rule claim in each extract, all 102 transcripts were searched for a contradicting passage (patterns in each extract's section 3.7); only Tom-set hits that speak to the same variable count.
- Claims searched: 31 (8 + 5 + 6 + 6 + 6). Flagged: 9 claim-level flags, 6 distinct (F1-F6). No contradiction found for 22 claims.
- Inline flags are in the extracts as `[F#]` in the row and as section 3.7.
| flag | type | what | extracts |
|---|---|---|---|
| F1 | tension | "I don't want to scalp" is a per-trade choice; Tom teaches scalping with VWAP [T/43JaKHRvxHk:19@5866] | 4MoNjEQ2Dd8 row 15 |
| F2 | tension | target "above the highs" (ledge) vs "where the last largest volumes occurred" [T/tS6ZEiHj8gQ:19@6115] | 4MoNjEQ2Dd8 row 4, tS6ZEiHj8gQ row 11 |
| F3 | tension, trade-dependent | moving or trailing the stop: no move before an opposite range [T/4MoNjEQ2Dd8:19@12857], trail to the high [T/kXhIAug0Gh8:19@3349], "In this case, I don't do that" [T/k0zm5NYn0IQ:19@7033] | 4MoNjEQ2Dd8 row 31, kXhIAug0Gh8 row 12 |
| F4 | partial contradiction | no short at the peak vs "If you want to go short at the top, you have to pay dynamic attention to it." [T/rFPCtOcfUMI:13@10093] | tS6ZEiHj8gQ row 3 |
| F5 | direct contradiction | stop of a short "above this level" / "above the last supposed high" vs "It doesn't belong above the high." [T/yRvMW6lgN1o:19@6182] and a stop "above the last volume levels" [T/k0zm5NYn0IQ:19@16227] | tS6ZEiHj8gQ row 10, WSCIURybK3U row 13 |
| F6 | tension | "never ever delete this predefined target" vs "do you stick to them or do you move them?" [T/UOBgXV20yCM:7@177] | UrZ4vpHJ97g row 13 |
Hard contradictions: 1 (F5, and that row is an illustration he calls naive). The rest are context-dependent.

## 5.4 Kappa on the new extracts
NOT DONE. The same condition as W3 applies: the extractor cannot be its own second reader, and the second reader of W3 does not exist (W3 itself failed the blind condition, see REVALIDATION_ACTIONS W3). No kappa is reported; threshold 0.6 untested.
Protocol for a clean reader (not run): the reader gets EXTRACTION_METHOD_V2.md and one transcript only, writes its own decision rows (id, pos%, type) without opening the extract; rows are matched to the extract's rows by position (same pos% within 2 points and the same sentence); Cohen's kappa is computed on the `type` label over matched rows with `scripts/dev/kappa_check.py`, and the unmatched rows are reported as a count (recall) per extract. The kappa calculator exists and has a self-test.
What was measured instead (not a reliability figure): anchors 59 of 59 verbatim and correctly positioned; row fragments 264 of 267 verbatim after correction, the other 3 being the table-header label "as long as" (see 5.2).

## 5.5 Consolidation
### New rules found
Rule claims from the five transcripts that are not in conditions/*.md and not in a V1 extract (grep over extracts/fresh, extracts/processed and MyTradingSys/conditions [run]). Tag NO-SOURCE with the candidate source (no TOM id assigned):
1. Swing trading risk 0.7 percent per trade with a 12.9 percent maximum draw down; a 3.5 to 1 sample at 0.7 percent has a 14 percent largest draw down. "In swing trading, look, we risk 0.7% per trade with a maximum draw down of 12.9%." [T/UrZ4vpHJ97g:7@13851] NO-SOURCE (candidate source named; no TOM id).
2. Intraday swing hit rate "truly around 38 to 42%". [T/UrZ4vpHJ97g:7@16029] NO-SOURCE (candidate source named).
3. "which is why you must never ever delete this predefined target unless in the meantime you've used other mathematical approaches" [T/UrZ4vpHJ97g:7@8924] NO-SOURCE (candidate source named). See F6.
4. A minimum R:R of 1.5 for counter-trading at a 40 to 45 percent hit rate [T/k0zm5NYn0IQ:19@19400]: the V1 extract of that video has no "1.5" [run: grep]. NO-SOURCE (candidate source named). Found in W4 of REVALIDATION_ACTIONS.
5. Per-trade risk is derived from the strategy's key figures and a 20 percent maximum draw down, with sizing from the stop distance: "How do I get to 0.5% risk per trade?" [T/WSCIURybK3U:19@7677]; "You should assign a maximum draw down of 20% to your entire trading business." [T/UrZ4vpHJ97g:7@7393]; "I always determine my position size in direct accordance with my stop-loss level." [T/tS6ZEiHj8gQ:19@8786]. These ARE in V1 extracts [disk: extracts/fresh/extract_tS6ZEiHj8gQ_fresh.md:214; extracts/fresh/extract_WSCIURybK3U_fresh.md:149], but MyTradingSys/conditions/risk_protocol.md section 3.5 says Tom gives no sizing formula. [disk: MyTradingSys/conditions/risk_protocol.md:229-233] The statement needs rewording: no single percent, but a method exists. Stale GAP, not new Tom content.
Order-of-events and plan-versus-action facts that V1 got wrong are in 5.1 (A2-A4, C4).

### Contradictions found
6 distinct flags over 31 claims; 1 direct (F5). Table in 5.3.

### Method performance (counts)
- V2 extracts: 5; decision rows 165; anchors 59, all verbatim and correctly positioned; 7 trades and 5 illustrations; 14 rows carry [?].
- V1 against V2 on 4MoNjEQ2Dd8: V1 order errors 3 (A2, A3, A4); V1 steps with unstated prices 5 of 16; V1 conditional phrases recovered 11 of 34 (crude), V2 25 of 34; V2 misses 1 (fixed); V1 misses 1 ERROR row; V2 misses 1 time-frame switch (A6).
- Row-level drift past the gate: 7 of 267 non-anchor fragments not verbatim on first writing, 0 after correction.
- Format fit: 3 of 5 videos are trade walk-throughs where V2 works as designed; 2 of 5 are lectures where 16-19 of 24-27 rows are LESSON and hypothetical plans have no row type.
- Not measured: wall time and token cost per extract; inter-reader agreement.

### Open questions
1. Operator: should V2 get a row type for hypothetical plans (ILLUSTRATION) and a TIMEFRAME row, and should `verify_extract_quotes.py` also check quoted fragments inside table rows? (Proposal only; no code changed. The fragment check used here is a 25-line script, not committed.)
2. Operator: assign TOM ids to the five candidate rules above, or leave them NO-SOURCE; and reword risk_protocol.md section 3.5.
3. A clean second reader for kappa on W3 (blind packet) and on these five extracts (protocol in 5.4).
4. Instrument of 4MoNjEQ2Dd8: DAX vs NASDAQ is unresolved (V1 and this session both infer; neither is stated by Tom).
5. F5: the stop of a short. Q09 [T/yRvMW6lgN1o:19@6182] says it does not belong above the high; the engine puts it above a swing high. The audit already marks this (A05); the two new extracts add two Tom illustrations that put it above a level.
