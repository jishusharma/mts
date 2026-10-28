# WORK REVIEW - 2026-10-03

Session: MTS-2026-10-03-0500Z-CL-BLD-cicd-pipeline (surface CLI desktop, branch fast-track)
Written: 2026-10-03T05:10Z. Disk state read: HEAD 1dd9aca (session brief said 86313de; HEAD moved by one
close commit while this session ran, see section 7). Nothing committed by this session.
Companion: MyTradingSys/research/_archive/loose_2026-10/CICD_PIPELINE_2026-10-03.md (Task 2 design).
Rule for every status below: it comes from a same-session disk read (file:line or count). Where I did not
execute something I say "not executed".

## 0. SOURCES READ (receipts)

| Source | Lines | Read |
|---|---|---|
| MyTradingSys/runtime/BUILD_PIPELINE.md | 105 | full; 43 rows (0.1-7.1) |
| MyTradingSys/research/BUGS.md | 174 | full; 137 rows; 24 OPEN/BLOCKED |
| MyTradingSys/items/INDEX.md | 57 | full; 49 rows; 49 item files |
| MyTradingSys/research/apparatus_fixes.md | 105 | OPEN (2 bullets) + NEEDS OPERATOR (5 bullets) |
| MyTradingSys/runtime/NEXT_SESSION_HANDOFF.md | 84 | full (written 2026-10-01T05:56Z; stale header HEAD f3e94b0) |
| Dumps/operator/context/DSA_HANDOFF.md | 42 | full (session 0315Z) |
| MyTradingSys/research/_archive/loose_2026-10/OPERATOR_DIRECTIVE_2026-10-03-historical-testing.md | 23 | full; it is the only OPERATOR_DIRECTIVE_*.md in research/ |
| MyTradingSys/methodology/playbook.md | 55 | Part I |
| MyTradingSys/system/LESSONS_LEARNED.md | 311 | full |
| MyTradingSys/system/03_FILE_INDEX.md | 398 | header + row format + tail |
| BUILD_REPORT.md (runtime) | 43 | 2026-10-03 04:21:28Z: compile PASS, math 161, docs 5, STATUS PASS, 11 in-flight .new |

Reconciliation script (scratchpad, not in repo) parsed BUGS.md and INDEX.md rows and compared them by id.
Result: 137 BUGS rows, 49 INDEX rows, 49 item files; open set per BUGS = 24, per INDEX = 32.

## 1. REGISTRY FINDINGS (the four lists)

### 1.2 Stale list - pipeline rows whose status disagrees with disk

| Row | Pipeline says | Disk says |
|---|---|---|
| 0.2 BUILD_PIPELINE.md | IN-FIX | LANDED. File exists, indexed (03_FILE_INDEX.md L398), commit 5a6ec09 |
| 0.3 file-index rows | QUEUED | LANDED. Rows at 03_FILE_INDEX.md L397-398, commit 5a6ec09 "wave 0.3" |
| 1.1 B080 | QUEUED | LANDED. BUGS CLOSED, INDEX CLOSED, commits f97a441 + 17d74f7, tests named in receipt |
| 1.2 B075 | QUEUED | LANDED at 86313de (code + 2 Java tests + 2 Python tests + session record). Registry still OPEN. Residual exists, see B075 row |
| 2.1 R4-T1 | QUEUED "CL prompt ready, ship" | answered on disk: FABIO_PROVENANCE_AUDIT_2026-10-01.md:59 (P02 k_bal 0.8 and POC band 0.25 = NS-fixed, CONCEPT-ONLY) and :98 (P41 B_prof bundle = SIM, DATA-PLUMBING). R4 itself landed ccd0a0f. Remaining: record result in the R4 row and the operator decision (2.4) |
| 3.2 R6 | QUEUED "operator yes" | LANDED. Scheduled tasks "MTS testnet canary" and "MTS testnet status" exist, state Ready (Get-ScheduledTask); scripts/dev/testnet_canary.py exists; .gitignore L101-102 names the 30-min canary rewrite |
| 4.9 B066 | QUEUED | premise gone, see B066 row |
| 4.12 T037 | QUEUED "pom edit pending operator" | premise stale: pom.xml already declares junit-jupiter 5.10.2 and surefire 3.2.5; no pom edit needed. Real gap is elsewhere, see T037 row |
| 4.14 T044 | QUEUED "build" | premise gone: no hybrid run mode exists |
| 5.2 B077, 5.3 B078, 5.4 B079 | QUEUED | CLOSED in BUGS with code-verified receipts (5e387a1, b05c1cf). They are exercised by every testnet trade: auto_trader.py:334-336 runs executor.py --go, position_manager.py:581 places stop_market |
| 6.4 T056 | QUEUED "re-scope" | dead, see 1.5 |
| 6.9 T059 | QUEUED | defect real; the NUC task 121 premise in the BUGS receipt is dead. Pipeline row itself is fine |
| (absent) T062 | no row | BUGS OPEN, INDEX CLOSED, work landed (4575d8f, d168f3c). Not in pipeline, correctly |

14 pipeline rows are stale or partly stale (0.2, 0.3, 1.1, 1.2, 2.1, 3.2, 4.9, 4.12, 4.14, 5.2, 5.3, 5.4, 6.4, 6.9).
Confirmed: B075 landed at 86313de (git log -1 shows its subject; session record
system/sessions/MTS-2026-10-03-0430Z-CLI-BLD-b075-historical.md present). B075 is NOT fully done, see below.

### 1.3 Orphan list

BUGS open row with no INDEX row: none (all 24 present).
INDEX row with no BUGS row (six): T053, T054, T055, T056, T057, T058. Each has an item file and a pipeline row
(6.1, 6.2, 6.3, 6.4, 6.5, 6.6). BUGS.md line 3 calls itself the single source of truth, so these are orphans of
BUGS.md. Build-Check.ps1 does not catch them: its two INDEX checks run BUGS -> INDEX (L175-194) and
files <-> INDEX (L205-238), never INDEX -> BUGS.
Status disagreement (id in both, different status):
- T062: BUGS OPEN with no receipt; INDEX CLOSED. Evidence closes it (4575d8f archived scripts/manager/*, d168f3c archived its test;
  scripts/manager/ now holds only __pycache__). Fix: BUGS Status CLOSED, Receipt "4575d8f, d168f3c".
- B077, B078, B079: BUGS CLOSED; INDEX still OPEN (INDEX L41-43). Fix: three INDEX status cells to CLOSED.
- T051: BUGS BLOCKED, INDEX PARKED. Not a disagreement: the BUGS row states PARKED is not a legal BUGS status.
Not orphans: B060 and B061 (BUGS CLOSED, no INDEX row; INDEX only needs rows for open ids, Build-Check L180-183).
Not orphans: R4-T1, R4-T2, R4-T3, R4-D, R5, R6, R7 and the 0.x rows. They are pipeline slugs, not registry ids.
Id gap: B068 appears in no file under MyTradingSys (grep -l, 0 hits); the id was never issued. Not a defect.

### 1.1 Merge list

| Merge | Keep | Reason |
|---|---|---|
| B076 + T052 | B076 | same defect (SETUP_CONFIRMED never emitted) and its fix (Tom-cited trigger). T052 depends on B076 (pipeline 4.3 blocker 4.2). Close T052 as WONTFIX "merged into B076" (precedent: T023 merged into B049) |
| T034 + T055 (positioning half) | T034 | Net/New Longs and Shorts is one feature asked twice. T055 keeps "proven BTC setups" |
| AF L81-85 pre-open playbook gap + T054 | T054 | pre-market / US-session alert is T054's ask |
| B059 + B066 | none | deliberate split on 2026-09-24; both close (see rows) |
| B072 + B073 + B074 | none | same origin (CORE_READINESS_PLAN F10-F12) and same files, but three different defects. Run as one work unit "L2 hygiene" |

### 1.4 Critical three (live defect risk if open through the next trading week)

1. B072 - fail-open input check. math_object_builder.py:66,93 pass current_price through unchecked (default 0.0); a string or
   None returns "aligned". Live path: build_mo_cli.py -> math_object_builder.build_math_object -> proof_direction ->
   start-trading-day.ps1 verdict (L474-487) -> alert -> auto_trader.py (reads last_alert.json). Same fail-open class as B071.
2. B070 - unsourced gates. ExecutionMathConstants.java:42 netRR = gross * (1 - 0.25) feeds every candidate
   (SetupCandidatesBuilder.java:156); the UTC-midnight anchor drives session CVD (StateCodeEmitter.java:68-71, 178-190).
   Live path: SetupCandidatesBuilder -> snapshot net_rr -> math_object_builder.py hard stop 4 (L392-406) -> verdict -> auto_trader.
   Neither number has a Tom source (CLAUDE.md Provenance).
3. B073 - rounded value gates trades. Java rounds net_rr to 2 dp for output (SetupCandidatesBuilder.java:216) but sets the sanity flag on the
   unrounded value (L158). Since 2026-10-02 Python gates on the rounded output (math_object_builder.py:392-406, float(_net) < load_floor()), so a net of 1.996
   shows 2.00 and passes a 2.0 floor. Same live path as B070. Small per trade, systematic.
Watch (not top three): B069 (61 intermittent update_market_state failures since 2026-09-24, evidence overwritten each cycle),
AF L106 (tape sidecar unwatched by supervisor).

### 1.5 Dead list - premise gone

| Item | Why dead | Action |
|---|---|---|
| T056 Qwen audit program | Qwen decommissioned 2026-10-01; T049 and B082 CLOSED on that fact | BUGS row (to be created) then WONTFIX |
| NUC 2201-2203 (Fabio v3 pack) | same | drop from handoff |
| T059 receipt "NUC task 121" | same; defect itself is alive | strip the NUC clause when the row is touched |
| T044 hybrid REST/WS alert | no hybrid run mode in Main or scripts (grep hybrid, 0 hits); B045 WONTFIX says WebSocket migration not started | WONTFIX citing B045 |
| T037 "pom edit" | pom already has JUnit 5 + surefire; 5 test classes in src/test/java | rewrite title to the real gap |
| B066 | see row | close |
| AF L99 stop-day orphan | stop-day.ps1 (38 lines) no longer kills; loop finally uses taskkill /F /T (start-trading-day.ps1:826,836); supervisor L242; B003 + B014 receipts | mark CLOSED by B014 in apparatus_fixes |
| Handoff "Book-imbalance 0.0 fix" | landed: None/0.0 rule in proof_direction (per b075 session record) and MyTradingSys/tests/test_book_imbalance_nodata.py exists; not re-executed | drop from handoff |
| T062 | done, not dead; close it | registry correction |

## 2. THE TABLE (every open item, all sources)

Columns: id | defect or feature | real on disk | sources | smallest correct fix | blocker | dependents | band | reason.
"Sources" abbreviations: BUGS, IDX (items/INDEX.md), PIPE (BUILD_PIPELINE row), AF (apparatus_fixes), NSH (NEXT_SESSION_HANDOFF), DSH (DSA_HANDOFF), BR (BUILD_REPORT).

### 2a. Registry rows open in BUGS.md (24)

| id | defect / feature | real | sources | smallest fix | blocker | dependents | band | reason |
|---|---|---|---|---|---|---|---|---|
| B059 | pf_vp bin-edge drift moves rank-1 zone | yes, fix on disk (MarketDataSnapshot.java:490-519 fixedBinSize overload) | BUGS IDX PIPE 4.4 | close with receipt: replay bin edges over on-disk snapshots (13097 files in runtime_data/snapshots), cite hash 52FF88CF | none | B066 | fix-next | fix landed 2026-09-24; only the live-tape receipt is missing and the tape is on disk |
| B063 | divergence has no dictionary entry, no condition rule, no verdict consumer | yes (no hit in conditions/ or runtime/*.py; only scripts/tools/divergence_monitor.py; dictionary path not checked) | BUGS IDX PIPE 4.10 | operator picks restore or deprecate; deprecate = WONTFIX | operator | none | park | decision, not code |
| B066 | rank-1 shown at trigger_ready 150 pts from price | no. SetupCandidatesBuilder.java:75 and :209 give trigger_ready only when distance_pct <= 0.1. Replay of the latest 390 rank-1 rows in snapshots/: 0 rows trigger_ready with distance_pct > 0.1. When the gate landed was not traced | BUGS IDX PIPE 4.9 | close with receipt = those two lines + the 390-row count | none | none | drop | premise gone |
| B069 | update_market_state.py exits 1 intermittently under the wrapper | yes: 61 STATE_UPDATE_WARN vs 4588 state_updated in runtime_data/apparatus_log.txt since 2026-09-24; start-trading-day.ps1:449 redirects output to runtime_data/ums.log, which is overwritten each cycle, so the failing run is lost (item text "stderr to NUL" is out of date) | BUGS IDX PIPE 4.16 | on rc != 0 copy ums.log to runtime_data/ums_fail_<utc>.log; stage start-trading-day.ps1 as .new (critical, live) | supervisor restart | none | fix-next | low but live; evidence is destroyed every cycle |
| B070 | UTC 00:00 anchor and 0.25 friction (0.75 multiplier) gate the verdict | yes (see 1.4 #2). Ownership centralised in ExecutionMathConstants.java by W2; value unchanged | BUGS IDX PIPE 4.1 | flag both NO-SOURCE in their config/constants file; replace friction with the fee model from fees.py (single source, B081) or display-only; UTC anchor display-only per B067 audit | operator ruling on the friction value (the 2.0 floor rests on it) | T037 tests, R7 | fix-now | gates every candidate on the live path |
| B072 | current_price "x" or None returns "aligned" | yes (1.4 #1) | BUGS IDX PIPE 4.6 | in _normalize_snapshot raise ValueError unless price is finite and > 0; B071 wrapper caps verdict at WAIT_PROOF (fail closed). Test: "x", None, 0, NaN | none | none | fix-now | fail-open class on live path |
| B073 | net_rr 2 dp output vs unrounded sanity flag | yes (1.4 #3) | BUGS IDX PIPE 4.7 | emit net_rr at 4 dp, or compute the sanity flag on the rounded value (round-then-sanity); one test at 1.996 | none | none | fix-next | boundary trades pass a 2.0 floor |
| B074 | contradiction cap runs before broken-value override | yes (start-trading-day.ps1:232 vs :241) | BUGS IDX PIPE 4.8 | document the order, or swap; only the reason text differs | none | none | park | both outcomes non-actionable |
| B075 | historical snapshot unfit for backtests | partial. 86313de: no live calls, flow fields null + UNAVAILABLE, session attached. Residual (per its session record and SetupCandidatesBuilder.java:552,635,822, not executed): candidates still emit proof.book_imbalance 0.0 and read net_delta via asDouble (null becomes 0.0) | BUGS IDX item PIPE 1.2 | keep B075 OPEN, set Receipt "partial 86313de", make candidate builder null-aware on the historical path, Python test on a historical snapshot | none | R4-T3, T051, D1-L0 | fix-now | registry wrong today; residual decides whether backtests are valid |
| B076 | SETUP_CONFIRMED never emitted | yes: only consumed (start-trading-day.ps1:247,252,643; mts-dashboard.ps1; auto_trader.py:58); verdict.py comment says it is a live state-machine step | BUGS IDX PIPE 4.2 DSH | merge T052 into B076; no code until a Tom-cited trigger exists | T052 content | R5 ordering | fix-next | missing capability, not a wrong trade |
| T034 | Net Longs / Net Shorts positioning states | no-file (0 hits in src/, scripts/, runtime/*.py) | BUGS IDX PIPE 4.11 | fold into T055; build after T055 gives sourced definitions | Rule 33 readers | T055 | park | needs research first |
| T037 | test coverage gap | yes, premise moved. Build-Check.ps1:25 runs mvn -q -DskipTests compile, so no Java test ever runs in that gate. 5 classes sit in src/test/java; MyTradingSys/tests/java/MarketDataSnapshotTest.java.new unpromoted; runtime/test_quad_classify.py.new and test_regime_classifier.py.new unpromoted | BUGS IDX PIPE 4.12 BR | Build-Check Java step to mvn -q test; promote the 3 staged tests | none (no pom edit) | every Java change | fix-now | gate hole, cheap |
| T040 | tick delta layer | no-file. R3 orderflow_live.py writes 1m aggTrades bars, not a threshold-emitting tick layer | BUGS IDX PIPE 4.13 | thresholds from measuring R3 data first; each needs Tom citation or documented exception | research gate | T054 T055 T058 | park | new rule surface |
| T042 | OI/CVD peak reference not emitted | yes (only VP second-peak at MarketDataSnapshot.java:570-578; no OI/CVD peak) | BUGS IDX PIPE 4.5 | add producer only when a named consumer exists | consumer | none | park | producer without consumer |
| T044 | hybrid REST/WS divergence alert | no (premise gone, 1.5) | BUGS IDX PIPE 4.14 | WONTFIX citing B045 | none | none | drop | no hybrid mode |
| T046 | stage 3 decisions bundle (5) | not verified (what_is_next.md exists; the five decisions not enumerated by me) | BUGS IDX PIPE 4.15 | operator answers | operator | Stage 4 | park | decisions |
| T048 | satellite framework umbrella | partial | BUGS IDX PIPE 5.5 | none; tracks T050 | T050 ph4 | T053 T058 | park | umbrella |
| T050 | Deribit execution layer, phases 3+ | partial: phase 1+2 PASS, phase 3 primitives PASS 2026-10-02 (T050_PHASE3 note) | BUGS IDX PIPE 5.1 | testnet run of the executor path end to end, then phase 4 reconciliation | none (B077-B079 closed) | T048 T051 | fix-next | live path, testnet only |
| T051 | backtest on MTS raw verdict, parked | yes parked | BUGS IDX PIPE 5.6 | none | T050 ph4 (B071 now closed) | none | park | operator parked it |
| T052 | Tom-cited SETUP_CONFIRMED trigger | no-file | BUGS IDX PIPE 4.3 DSH | search Tom corpus; none found = record NO-SOURCE, keep unreachable by design; merge into B076 | none | B076 | fix-next | default before R5 because R5 is operator-blocked |
| T059 | SESSION_PASTE size guard | yes: start-session.ps1:314-317 only warns at 80 KB; scheduler check_paste_size.py and DSA section 2 use 150 KB | BUGS IDX PIPE 6.9 | one threshold (150 KB), split at a section boundary | none | none | fix-next | small, unblocks DSA paste |
| T060 | low-vol anomaly on BTC | no-file | BUGS IDX PIPE 6.7 | method note first (playbook Part I step 1), then own backtest | operator on panel option | none | park | T3 evidence only |
| T061 | WaveTrend LazyBear layer | no-file | BUGS IDX PIPE 6.8 | add formula + source to backtest/layers/FORMULAS.md, then layer + test, collection-only | none | none | fix-next | fully specified, no live risk |
| T062 | deprecate manager | yes, done (4575d8f, d168f3c) | BUGS(OPEN) IDX(CLOSED) | BUGS Status CLOSED + receipt | none | none | fix-now | registry correction |

### 2b. In INDEX / pipeline / item files but not in BUGS (orphans, 6)

| id | feature | real | smallest fix | band | reason |
|---|---|---|---|---|---|
| T053 | two-account hedge / leveraged scalping research | yes (doc); partly overtaken: two testnet subaccounts exist (TESTNET_SUBACCOUNTS.md) | add BUGS row; re-scope after T058 | park | research |
| T054 | US session / pre-market alert, US-equity correlation, news | yes (doc) | add BUGS row; absorb AF L81-85 | park | research |
| T055 | positioning flow + proven BTC setups | yes (doc) | add BUGS row; positioning half merges into T034 | park | research |
| T056 | Qwen audit program | dead (1.5) | add BUGS row as WONTFIX | drop | premise gone |
| T057 | simplify / declutter | partly done (declutter_backups.py exists; purge commit 5c8f83b) | add BUGS row; the intake sweep and CI/CD design are the next slice | fix-next | cheap T0 scripts |
| T058 | broken lows/highs: continuation vs sweep | yes (doc) | add BUGS row; needs R3 order-flow data | park | research |
Severity for the six new BUGS rows: none is recorded in the item docs. This review proposes LOW (research) and MED (T057);
the operator or the next builder confirms. BUGS.md needs a legal severity cell.

### 2c. Pipeline-only slugs

| slug | state | smallest fix | blocker | band | reason |
|---|---|---|---|---|---|
| R4-T1 | answered on disk (see 1.2) | write the P02/P41 result into the R4 row | none | fix-now | zero cost; unblocks R4-D |
| R4-T2 | yes: htf_context_live.py:88-89 and :103 return False when prev_bal is None or i < N_4H, collapsing "unknown" into "false" | return None in those two places, keep False only for a computed negative; add a test (collection-only writer, not live-imported) | none | fix-now | R4 data collects for 14 days; every day of wrong labels is lost data |
| R4-T3 | open | sweep of balance() parameters, OPERATOR-EXPERIMENT | operator ranges + B075 residual | fix-next | R4 finding: 0 of 1260 closes pass the POC band at N=240 (session record), so the sweep is informative |
| R4-D | open | parameter decision | R4-T1 result + R4-T3 | park | operator |
| R5 | open | Model B shadow on 15m/4H | R4-D | park | blocked |
| R6 | LANDED | mark LANDED | none | drop | done |
| R7 | open | Tom BT re-run on D1 target rule | Wave 4 | park | blocked |
R4 parameter tokens (disk read): the pipeline names K_BAL, BAL_POC_BAND, B_PROF. They are not in htf_context_live.py (its tokens are MIN_MS, H4_MS,
N_4H, N_1D, FP_BIN, SYMBOL, BASE). They are defined in MyTradingSys/backtest/layers/fabio/v3/signals.py:25-27 (B_PROF = 50.0 L25,
BAL_POC_BAND = 0.25 L26, K_BAL = 0.8 L27), used at signals.py:183 (balance default args) and :203 (POC band). htf_context_live.py imports
balance from that module (L27). So not MISSED: the tokens exist, inherited by import. Values match the pipeline row.

### 2d. apparatus_fixes.md

| id | item | real | smallest fix | band | reason |
|---|---|---|---|---|---|
| AF L99 | stop-day orphan java | no (1.5) | mark CLOSED by B014 | drop | stale |
| AF L111 | alert card lacks "what fired" line | partial: SSOT_TRIGGER line exists (start-trading-day.ps1:304, fed by NEXT_TRIGGER :770) but names the next trigger, not the change that fired | add a FIRED line from the materiality gate's changed fields | park | cosmetic; critical live file |
| AF L73 | third Rule 32 snapshot for trend override | override is live (start-trading-day.ps1:241-253) | operator collects or confirms | park | operator |
| AF L81-85 | pre-open playbook gap | yes | merge into T054 | park | research |
| AF L103/L109 | 30s heartbeat edit to _scratch_monitor.ps1 | file is runtime_data/_scratch_monitor.ps1 (not under scripts/); likely superseded by scheduler tick (MTS-Scheduler-Tick exists); coverage vs tick.py not compared | operator: defer | park | probably superseded |
| AF L106 | supervisor does not watch tape sidecar lock | yes (no tape or sidecar term in loop-supervisor.ps1; Watch-Aux covers the four aux processes per DSH) | add a stale-field alarm; supervisor owns the file | fix-next | live supervision gap |
| AF L112 | state vs zone alerts: independent or batched | open | operator decides; alert_rate_check.py is the instrument | park | operator |

### 2e. Handoff-only items (no registry id)

| item | source | real | smallest fix | band |
|---|---|---|---|---|
| Tom engine rebuild spec (36 of 76 parameters no Tom source; 2:1 net rule miscited) | NSH | yes (CLAUDE.md Provenance) | give it a registry id (next free T063); produce the per-parameter NO-SOURCE table locally; cloud spend stays the operator's call (credits $42 of $100, expire 2026-11-05 per NSH) | fix-next |
| classify_msb fix | NSH | partial: cc_structure.classify_msb exists; staged tests test_cc_structure.py.new and test_cc_retest.py.new about 6997 min old (BR); the source fix itself I did not locate | give it an id; promote staged tests then fix | fix-next |
| MISSING_PIECES sections 0 and 4 unread | NSH | file exists at research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md | read, convert findings to rows | fix-next |
| Staged .new inventory (11 files, BR 04:21Z) | BR | yes; oldest 6997 min; no ids except T037 | per file: promote or drop; scripts/sched/check_new_aging.py already flags over 24 h | fix-next |
| 2113 zAwEX_tRUfE recon template deviation | NSH | content usable | none | drop |
| R5 vs T052 decision | DSH | open | default T052 first (R5 is blocked on R4-D); operator may overrule, flow does not wait | fix-next |
| R4 status check, close batch commit | DSH | done: R4 = ccd0a0f; close = ee9ecd2 | none | drop |

## 3. DEPENDENCY SPINE

B075 residual -> R4-T3 -> R4-D -> R5. R4-T1 + R4-T3 -> R4-D.
T052 -> B076. T050 phase 4 -> T048, T051. Wave 4 -> R7.
T037 (gate runs Java tests) -> every Java change after it.
B070 operator ruling -> R7 (target rule re-run needs a stable net_rr).
B072, B073, B074 bundle on math_object_builder.py (critical file: hash, edit, hash, diff).

## 4. RANK SUMMARY

fix-now (8): T062, B075 (registry + residual), T037, B072, B070, R4-T1, R4-T2, B077-B079 INDEX corrections.
fix-next (15): B059, B069, B073, B076, T050, T052, T059, T061, T057, AF L106, Tom spec id, classify_msb, MISSING_PIECES read, staged .new sweep, R4-T3.
park: B063, B074, T034, T040, T042, T046, T048, T051, T060, T053, T054, T055, T058, R4-D, R5, R7, AF L73/L81-85/L103/L111/L112.
drop: B066, T044, T056, R6, AF L99, NUC 2201-2203, 2113 recon, handoff book-imbalance item.

## 5. WHAT THE NEXT BUILDER DOES FIRST (no stop between)

1. Registry corrections in one pass (BUGS.md rows: T062 CLOSED; B075 receipt; add T053-T058 rows; T052 merged; T044, T056, B066 closed or WONTFIX; INDEX B077-B079 CLOSED).
2. T037 gate change in Build-Check.ps1. 3. B072 + B073 + B074 bundle (one critical-file edit). 4. R4-T2. 5. B075 residual.
Operator-blocked items (B070 value, R4-D, B063, T046) are skipped and logged, not waited on.

## 6. T5 MISSED (could not verify, and why)

- I did not run Build-Check.ps1, run_all_tests.py or mvn. mvn compile writes target/, which the live loop uses (the B075 session also left target/ alone). Counts quoted are from BUILD_REPORT.md 04:21:28Z.
- B066: I did not trace when the 0.1 pct tier gate landed; the replay shows the premise absent today only.
- B075 residual and B074 order: read from code and the session record, not executed.
- T046: the five decisions in what_is_next.md were not enumerated.
- classify_msb: the source fix the handoff means was not located; only the staged tests were seen.
- AF L103/L109: not compared against scripts/sched/tick.py coverage.
- Severity of T053-T058: not recorded anywhere on disk; proposed values only.
- The brief says "tail 40" of LESSONS_LEARNED; I read the whole file (311 lines), so nothing was cut.

## 7. HEAD MOVED DURING THIS SESSION

Brief and session start: HEAD 86313de, last-snapshot tag at 1b7a9a1. At 05:09Z HEAD is 1dd9aca ("close: MTS-2026-10-03-0430Z-DSA-COO ...") and
last-snapshot points at it. That commit also swept runtime churn into history: execution/pm_heartbeats/*.json, runtime/orderflow_live/*.csv, _qhist,
_state.json, runtime/session_log.json, BUILD_REPORT.md, a testnet status note (git show --stat HEAD). Minutes later the same paths show modified again.
This is the stage-everything hazard (gitsnap in scripts/load.ps1:87 runs git add -A). It is the main evidence behind the release gate in the design note.

## 8. ADDED DURING THIS SESSION (concurrent session, about 05:15Z)

Uncommitted edits by another session appeared in the working tree while this review ran (git status): BUGS.md row B083, INDEX.md row B083,
new items/B083_prompt_check_gate.md, new research/PROMPT_FAILURE_ANALYSIS_2026-10-03.md. All counts above are as of 05:10Z and exclude B083.
This is the intake gap in action: a new task arrived mid-run and no sweep existed to pick it up. Next free ids are now B084 and T063.

| id | defect / feature | real | sources | smallest fix | blocker | dependents | band | reason |
|---|---|---|---|---|---|---|---|---|
| B083 | DSA composes prompts without disk verification; build scripts/dev/prompt_check.ps1 that greps a composed prompt against disk | yes: scripts/dev/prompt_check.ps1 absent (ls scripts/dev); LESSONS_LEARNED.md L309-311 already names it as pending | BUGS IDX item | build it as an advisory check that prints WARN rows and never refuses a launch | operator ruling: commit 5c8f83b purged the DSA prompt-conformance gate on 2026-10-03 ("purge MTS of restrictions that block Claude") and the directive says no step stops; B083 as written ("refuses launch on FAIL", LESSONS L309-311) would reverse both | none | park | decide advisory vs gate first; outside the CI/CD pipeline either way (CICD note 2.10) |

# END
