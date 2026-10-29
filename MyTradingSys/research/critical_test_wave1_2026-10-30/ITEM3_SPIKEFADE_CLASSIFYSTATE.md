# Item 3: spike-fade, scoring/confidence/tier, classifyState, switch census (critical test wave 1, 2026-10-30)

Read-only audit plus two new test classes. No commit, no live tree, no src/main change (`git diff --stat -- src/main` empty after the mutation runs).
U = rule misunderstood (spec vs trader's words). I = rule implemented wrong (code vs spec / hand numbers).
Trader quotes were read fresh from `F:/MTS/data/tom_videos/<id>.txt` (cited `id:line`) and `raw_transcripts_canonical/<id>_raw.txt`;
`scripts/dev/check_spec_quotes.py` on the spec: 69/69 quotes verbatim (so the spec's quotes are faithful; the findings below are about use, not wording).
Spec = `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md` (TLV2). Code lines are head of this worktree; trunk (`origin/fast-track`) is byte-identical for SpikeFadeDetector and SetupCandidatesBuilder (empty `git diff HEAD origin/fast-track`).

## A. Spike-fade (family A, `SpikeFadeDetector.java`, Paths, Profile, SessionState)

| # | Rule | Tom (source) | Spec | Code | Verdict |
|---|---|---|---|---|---|
| A1 | A-C1 impulse leg ranked above the median of prior 20 same-clock legs | "the initial balance is so large ... very very big" k0zm5NYn0IQ:361-364 (txt 14:35-14:41); "powerful rocket" T6hDJcHrVBM:114-116 | TLV2:59, :377 (RANK-DEFAULT, "weakest reading") | SpikeFadeDetector:156-179 (median 175, gate 176 strict `>`) | MATCH to spec; U-FINDING LOW: median (50th pct) is not "very, very big"; spec itself labels it weakest, fire rate at 0.8/0.9 never reported by the detector |
| A2 | A-C1 AND A-C2 are mandatory gates for every fade | k0zm5NYn0IQ:51-56: "we are of course above the previous day. That means it's a very risky trade and you shouldn't expect it to fall incredibly deep" (a risk caveat, not a trigger); l8RZrBfzvp4:55-57 and n7ZSkjb7JXs:102-106 use it as context | TLV2:56-62 "all must be observable"; but rule paths TLV2:165-168: T3, T5, T6 have NO C2 (T3, T6 no C1 either) | SpikeFadeDetector:176, :183 return null | **U-FINDING HIGH**: the encoding cannot fire on 3 of 6 design groups by construction (TLV2:468 admits "T3 and T3b fire nothing: A1's idea fails A-C2"). Fits RECALL FAIL 2/5 (TLV2:451). No money impact (flag off) |
| A3 | A-C2 range form: last close above prior day's full-day high | "completely outside of the previous day's range" l8RZrBfzvp4:55-57 (txt 01:56-02:00); VP form k0zm5NYn0IQ:51 | TLV2:348, :364 | SpikeFadeDetector:181-183 (`>` strict; dayHigh[19] = latest prior session with a window bar) | MATCH (hand: close 904.5 == high -> none, 904.6 -> fires; test caseC) |
| A4 | A-C3 "no liquidity above" is the heart of the idea | "no liquidity left" k0zm5NYn0IQ:21-22; "if the market were to accumulate large volumes there ... long" k0zm5NYn0IQ:357-360 | TLV2:61, :364-366 (PRICE arm is the weaker reading) | SpikeFadeDetector:239 lists A-C3 `not_in_data` even for BTC where volume (`Bars.v`, :67) exists; PROFILE arm separate (SpikeFadeProfile) | U-FINDING MED: price-only candidate fires into volume-supported pushes Tom says he would buy; labelled by spec, but BTC data could gate it |
| A5 | A-S2 stop 20 points when nothing above | "stop-loss of 20 points in the DAX ... no reference values up here" k0zm5NYn0IQ:22-26 (DAX points) | TLV2:94; Part B TLV2:265, :323 (BTC min width 0.40 %, card 7 unbuilt) | SpikeFadeDetector:40 `A_S2_POINTS = 20.0`, :192 applied to every symbol | **I-FINDING MED**: DAX points used as BTC dollars (0.02 % of 100k); sym only picks the fee. Latent: flag off |
| A6 | A-S1 stop above the level the seller defends / top volume bell | ujedEcmvBMk:67-68, n7ZSkjb7JXs:299-301 ("above the bell") | TLV2:93, :442 (nearest prior-session HIGH above zone, no buffer) | SpikeFadeDetector:186-192 | U-FINDING MED: proxy is a daily high, not a volume level, and has no distance cap (nearest of 20 days can be percent away; hand case D: stop 1070 vs zone 1040, net 0.93 < floor). Net R:R gate absorbs it |
| A7 | A-T1 target = start of the impulse | "the entire distance below the start of the impulse" T6hDJcHrVBM:170-172 | TLV2:101, :377 (leg = session start to extreme) | SpikeFadeDetector:193 `target = open` of first window bar | U-FINDING LOW: equals Tom's start only when the session does not dip first ("started way down here", T6hDJcHrVBM:114); also at odds with "shouldn't expect it to fall incredibly deep" (A2) |
| A8 | Window 07:00-17:35 Berlin | "highest liquidity ... 8:30, 9:00 and 17:35" T6hDJcHrVBM:94-97 | TLV2:385, header labels 07:00 OURS | SpikeFadeDetector:37-38 | MATCH (end SOURCED, start OURS, labelled) |
| A9 | Proofs P2/P4/P5/P7 | k0zm5NYn0IQ:469-473; T6hDJcHrVBM:147-155; l8RZrBfzvp4:100-102 | TLV2:71-76, :443-444 | SpikeFadeDetector:198-208, :260-279 | MATCH (hand case A: P2 tie 1.0 vs 1.0 is not "above", P5 true, P4 false by low 1031 < 1036, P7 false). P5 = above ALL 20 daily highs is far stricter than "pre-market high ledge" (U LOW, labelled OURS) |
| A10 | One re-entry per session (A-M5) | k0zm5NYn0IQ:264-268; zQTbdEweG3c:168-170 | TLV2:384, :463-465 ("the builder only reads") | SpikeFadePaths:57-63 `observe` + `recordEntry` WRITE on every emitted A2/A3; SpikeFadeSessionState:36-68 in-memory `static shared` unless `-Dmts.spikeFade.stateFile` | I-FINDING MED (latent): each snapshot is a fresh JVM (NetRrFloor.java doc), so without stateFile the cap is inert; spec text "builder only reads" is wrong vs code (U LOW). A1 is never gated (class header) |
| A11 | Trigger arithmetic, 5 hand cases | - | TLV2:435-439 numbers | `SpikeFadeCriticalWave1Test` | PASS (see B) |

## B. Scoring / confidence / tier / confluence and net R:R (`SetupCandidatesBuilder.java`)

Source: none from Tom. Weights come from `MyTradingSys/market_data/dsa_task_012_setup_candidates.md:495-512` ("for ranking only, NOT a verdict"); tier cap numbers are screener inventions (tracker `_archive/loose_2026-10/AUDIT_2026-09-17_TRACKER.md` "Condition-file negative results"). Net R:R is FORMULAS 17 (`backtest/layers/FORMULAS.md:407-413`).

| # | Rule | Spec | Code | Verdict |
|---|---|---|---|---|
| B1 | raw = min(95, 50 + 7 x proofs + 10 confluence); B>=70, C+>=55, C>=40 else D | dsa_task_012:495-512 | :189-197 | MATCH to DSA spec (hand tables, 3 build() scenarios). U-FINDING LOW: constants have no trader source (OURS, ranking only); I-FINDING LOW: raw >= 50 always, so band D is unreachable and 0 proofs + no confluence is "C" |
| B2 | Confluence: other candidate zone within 0.3 % of this zone's price, +10 | dsa_task_012 step 8 | :47, :176-180, :565-575 | MATCH: 100.2 pair +10/+10; 100.3 inclusive +10/+10; 100.31 -> 0/0. Reference price is the zone's own (Python uses cluster midpoint, tracker mts_math row 4: LOW drift, not closed) |
| B3 | Tier: <=0.1 % trigger_ready, <=cap conditional, else ignore | B066 `tierFor` | :52-54, :452-461 | MATCH (boundaries 0.1, 0.4, 0.2 hand-tested; 0.05 % -> trigger_ready, 0.2501 % -> conditional). Caps NO-SOURCE (U LOW) |
| B4 | net R:R = (|T-E| - 2 f E)/(|E-S| + 2 f E), f = 0.0005 BTC | FORMULAS 17 | ExecutionMathConstants:36-43 | MATCH: 0.67 (E 100, T 99.5, S 100.5), 1.38 (1040/1010/1060), 0.93 (1040/1010/1070) |

## C. classifyState (`SetupCandidatesBuilder.java:285-303`)

| # | Rule | Tom (source) | Code | Verdict |
|---|---|---|---|---|
| C1 | Balance = vwap flat/sideways AND cvd flat AND in_va (TOM-030/031) | "Sideways means that supply and demand are in balance" BVpYGKz9PBU (TOM_VERBATIM_INDEX:44) | :294-298 | Concept MATCH; thresholds unsourced. I-FINDING LOW: this branch is dead code: removing it changes no output (mutant M6d and M6 survive; every input it catches also falls through to `balance` at :302) |
| C2 | `divergent` cvd -> trend_unhealthy (TOM-056/140) | "this trend isn't entirely healthy ... no liquidity left here and the liquidity was down here. That means low volume." zQTbdEweG3c:231-236 (txt 08:21-08:31) and k0zm5NYn0IQ:49-50 | :299 | **I-FINDING HIGH**: `grep divergent src/main/java` hits only :299; MarketDataSnapshot cvd slope (:714-718, :767-773) emits rising/falling/flat. `trend_unhealthy` (and `aligned` at :301) is unreachable in production; POC counter-trend (determineSetupType:478) can never fire. Existing test `divergentCvdIsTrendUnhealthy` feeds a value the producer never makes. U: Tom's unhealthy is a volume statement, not CVD (also audit row 4) |
| C3 | Outside today's developing VA -> trend_healthy | Tom's "healthy" is always volume/liquidity or weekly-profile/trend-structure: zQTbdEweG3c:231-236, 9eHZMVXilgc (weekly profiles, "healthy balance"), ODdF0Bn_KSc (HH/HL + weekly profiles), VOiy8mAALWA ("balance can no longer be considered healthy" = VPOCs shifting). Never "outside VA" | :300 | **U-FINDING HIGH**: unsourced; k0zm5NYn0IQ:49-56 calls the move above the previous day "not healthy". With the C2 dead branch, effective classifier = "outside today's VA" (27-combo table, test). Blocks ct_short at VAH / swing high / POC (determineSetupType:470, :478) in exactly the fade situation |
| C4 | Direction: below_val -> long only | TOM-145 "if the market is below [yesterday's VAL] then I can definitely try a short trade" BVpYGKz9PBU | determineDirections:313-314 | U-FINDING HIGH, carried OPEN from `tom_direction_health_audit_2026-10-17/AUDIT.md` row 1 (and rows 3, 4): file unchanged on trunk since the fade commits (`git log` last touches: 91d2e43c3 pitchfork wiring, d5ac4ffa6, 9226c5fa4); today's VA still used, not `prior_day.*`; no open card named `tom-direction-health-vs-sources` found in `system/tasks` |
| C5 | Python twin `mts_math.update_state` | - | `MyTradingSys/runtime/mts_math.py:350-358` | MATCH (same 5 branches, same dead states). Same defects |

### D. Tracker 2026-09-17 claims, closed

| Tracker claim | Status now |
|---|---|
| 1 classifyState no longer reads shape | CLOSED VERIFIED: :291-293 read only vwap_slope, cvd_slope, price_vs_va |
| 3 "Rule 32 test passed 3/3" | CLOSED UNVERIFIABLE as stated (3 snapshot ids never recorded). Replaced by: `SetupCandidatesBuilderRulesTest` (rows) + `SetupCandidatesCriticalWave1Test.classifyStateHandTable`/`OverProductionVocabulary` (27 combos), killing mutants M6b, M6c |
| 4 mts_math matches Java | CLOSED VERIFIED again (C5) |
| "Step 3 downstream consumers PENDING" | CLOSED: only `determineSetupType` (:101), fade `market_state` field (SpikeFadeDetector:245) and Python `STATE.classification` (display, `mts_math.py:360`) |
| rows 10/11 `transition`/`sideways` dead in determineSetupType | CONFIRMED still dead (classifyState never returns them) |

## E. Hand-computed tests and mutation proof

New classes (11 tests, all pass: `Tests run: 5` + `Tests run: 6`, 0 failures, parsed from `target/surefire-reports`):
- `src/test/java/datafeed/SpikeFadeCriticalWave1Test.java` (5): case A fires 1040/1060/1010, gross 1.5, net 1.38, rank 1.0, leg 2.9703, proofs [A-P5]; case B leg == median 0.5 % -> null, 0.55 % -> fires (stop 1025.5, gross 0.275); case C close == prior-day high -> null, +0.1 -> fires; case D A-S1 stop 1070, gross 1.0, net 0.93; case E short history -> null.
- `src/test/java/datafeed/SetupCandidatesCriticalWave1Test.java` (6): classifyState hand table (9 rows) and 27-combo production-vocabulary table (9 balance / 18 healthy / 0 unhealthy); confluence pair, inclusive 0.3 % boundary, 0.31 % none; scoring raw/band recomputed in the test; tier cutoffs.

Mutation (temporary edit, restored; `git diff --stat -- src/main` empty):
| Mutant | Result |
|---|---|
| M1 A-C1 `>` to `>=` | killed: caseB |
| M2 A_S2 20 to 25 | killed: caseA, caseB |
| M3 A-C2 `>` to `>=` | killed: caseC |
| M4 CONFLUENCE 0.3 to 0.25 | killed: confluenceBoundary |
| M5 proof weight 7 to 8 | killed: 3 build() tests |
| M6b divergent to convergent | killed: classifyStateHandTable |
| M6c below_val not healthy | killed: hand table + vocabulary |
| M7 tier 0.1 to 0.2 | killed: tierCutoffs |
| M6 balance gate cvd flat to rising; M6d gate removed | SURVIVED (equivalent mutants: proves C1 dead code) |

Not covered: P4/P7 positive branches (existing `SpikeFadeTest`), A2/A3 path arithmetic (existing `SpikeFadePathsTest`), proof detection feeding `proof_count` (taken from output, not hand-derived): UNTESTABLE here without driving `detectProofs`.

## F. Switch census (Java reads: `grep getProperty|getBoolean src/main/java`; no `System.getenv`)

| Flag (reader) | Default | Set in `start-trading-day.ps1` | Decision behind it | Verdict |
|---|---|---|---|---|
| `mts.pitchfork` (PitchforkSignalLayer:27,30) | off | YES :113 (direct snapshot), :445 (statemachine, inert: StateCodeEmitter never reads candidates), :475 (mvn fallback) | Default off from 91d2e43c3. Live ON from 60cda535e (2026-10-28, author `gemini-queue`, card `live-engine-add-dmts-pitchfork-true-prop`: `live_path:false`, `approved_by` empty, note "REVIEWED 2026-10-28 T0-ONLY"). No entry in `OPERATOR_DECISIONS.md` (grep pitchfork: 0). Only the Opus-review card carries `approved_by operator 2026-10-28`, a review ask, not an enable. LAYERS.md:257 marks it "verified on DEV" | **FINDING MED**: undocumented switch ON in the live start script, shipped under a card that says it is not live-path. Money impact bounded: `research/pitchfork_2026-10-19/PF_ARM_TRACE.md` VERDICT NO order (auto_trader side parse rejects `PF-REV-L/-S` by naming accident); PF can still become `cands[0]` and drive the displayed verdict/popup. Process severity HIGH |
| `mts.spikeFade` (SpikeFadeDetector:35) | off | no | TLV2:420-422 "Nothing reaches the live tree"; card `tom-encode-spike-fade` (archive); only `dax_engine.py:41 --spike-fade` | PASS (and recall FAIL, TLV2:451, argues to keep it off) |
| `mts.spikeFade.profileDax` (SpikeFadeProfile:34) | off | no | TLV2:480 (PROFILE_PARITY NOT_IN_DATA) | PASS |
| `mts.spikeFade.stateFile` (SpikeFadeSessionState:35) | in-memory | no | TLV2:464 | PASS while flag off; if `mts.spikeFade` is ever set without it the re-entry cap is inert (A10) |
| `mts.netRrFloorFile`, `mts.runnerMinDistanceFile` (test hooks) | `MyTradingSys/system/{net_rr_floor,runner_min_distance}.json`, cwd-relative, NaN on failure | no (ps1 reads the floor json itself) | floor: operator 2026-10-02, `review_by_utc 2026-11-10` (11 days out); runner: operator ruling 2026-10-03, session record cited in the json | PASS; fail-closed on unreadable file |
| `mts.naked_poc_dir` (NakedPocTracker:34) | `runtime_data/naked_pocs` | no (pom.xml:56 test override) | commit 39520d44d (F-BT-09) | PASS |
| `mts.symbol` (passed by `dax_engine.py:41`) | - | no | none; no Java reader | LOW: dead flag |

## Results table

| Check | Kind | Result | Evidence |
|---|---|---|---|
| A-C1 median rank gate | U | FINDING(LOW) | SpikeFadeDetector.java:175-176; k0zm5NYn0IQ:361-364 |
| A-C1+A-C2 mandatory for all fades | U | FINDING(HIGH) | SpikeFadeDetector.java:176,183; TLV2:165-168; k0zm5NYn0IQ:51-56 |
| A-C2 range form strict `>` | I | PASS | SpikeFadeDetector.java:183; SpikeFadeCriticalWave1Test caseC |
| A-C3 absent from PRICE arm | U | FINDING(MED) | SpikeFadeDetector.java:239; k0zm5NYn0IQ:357-360 |
| A-S2 20 points on BTC | I | FINDING(MED) | SpikeFadeDetector.java:40,192; TLV2:323 |
| A-S1 proxy (daily high, uncapped) | U | FINDING(MED) | SpikeFadeDetector.java:186-192; n7ZSkjb7JXs:299-301 |
| A-T1 target = open | U | FINDING(LOW) | SpikeFadeDetector.java:193; T6hDJcHrVBM:170-172 |
| Trigger/RR/net arithmetic (5 hand cases) | I | PASS | SpikeFadeCriticalWave1Test (5/5), M1-M3 killed |
| Proofs P2/P4/P5/P7 | I | PASS (P4/P7 positive: UNTESTABLE here) | SpikeFadeDetector.java:198-208 |
| A-M5 attempt cap persistence | I | FINDING(MED, latent) | SpikeFadeSessionState.java:36-68; SpikeFadePaths.java:57-63 |
| Score formula and bands | I | PASS; band D unreachable FINDING(LOW) | SetupCandidatesBuilder.java:189-197 |
| Score constants unsourced | U | FINDING(LOW) | dsa_task_012_setup_candidates.md:495-512 |
| Confluence 0.3 % inclusive | I | PASS | SetupCandidatesBuilder.java:47,565-575; M4 killed |
| Tier cutoffs, caps | I / U | PASS / FINDING(LOW) | SetupCandidatesBuilder.java:52-54,452-461 |
| Net R:R | I | PASS | ExecutionMathConstants.java:36-43; FORMULAS.md:407-413 |
| classifyState balance gate | I | FINDING(LOW) dead branch | SetupCandidatesBuilder.java:294-298; M6/M6d survive |
| classifyState trend_unhealthy reachable | I | FINDING(HIGH) | SetupCandidatesBuilder.java:299; MarketDataSnapshot.java:714-718,767-773 |
| Outside today's VA = healthy | U | FINDING(HIGH) | SetupCandidatesBuilder.java:300; zQTbdEweG3c:231-236 |
| below_val long only / today's VA | U | FINDING(HIGH, OPEN since 2026-10-17) | SetupCandidatesBuilder.java:313-314; AUDIT.md row 1 |
| Tracker claims 1,3,4 + step 3 | - | CLOSED (3 as UNVERIFIABLE, replaced by tests) | AUDIT_2026-09-17_TRACKER.md |
| mts.pitchfork live ON undocumented | switch | FINDING(MED money, HIGH process) | start-trading-day.ps1:113,445,475; commit 60cda535e |
| mts.spikeFade / profileDax / stateFile off | switch | PASS | start-trading-day.ps1 (no -Dmts.spikeFade); TLV2:420 |
| netRrFloorFile / runnerMinDistanceFile / naked_poc_dir | switch | PASS | NetRrFloor.java:28; RunnerMinDistance.java:27 |
| mts.symbol passed, never read | switch | FINDING(LOW) | dax_engine.py:41 |
