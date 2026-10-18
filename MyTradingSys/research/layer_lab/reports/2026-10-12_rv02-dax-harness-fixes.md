VERDICT: FIX-FIRST

# RV02: DAX harness H1-H8 revalidation

RESULT (2026-10-12 UTC, JIS-NUC, COD, Python 3.14.6): **62 harness + 4 data tests passed, 0 failures, 0 errors, 0 skips. Four HIGH findings remain, reproduced using synthetic fixtures.** The direct development outcome boundary works, but the end-to-end pipeline is not holdout-isolated. The fee regression also misses Java serialization rounding. No production code, spec, ledger, real-data archive, holdout, or live path was changed or evaluated.

This is a completed audit, not authorization for a market run. Missing historical/source evidence is NOT_IN_DATA, not BLOCKED. The explicit file-only/no-git instruction takes precedence over RV02's historical worktree procedure. The four HIGH findings have SONNET follow-up cards below.

## What was checked

All paths below are relative to `F:/MTS/mts-codex-lab`. References use the current on-disk line numbers, except where explicitly described as historical report references.

| Alias / source | Lines checked |
|---|---|
| D = `MyTradingSys/backtest/tom_dax_bt.py` | 1-1325, complete |
| Tests = `MyTradingSys/backtest/test_tom_dax_bt.py` | 1-1218, complete |
| `MyTradingSys/backtest/dax_engine.py`; `dax_data.py`; `fees.py`; `test_dax_data.py` | Complete: 1-69; 1-128; 1-50; entire four-test file |
| P = `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md` | 1-38, complete |
| A = `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md` | 1-198, complete, including H3/H5/H2/H6/H7/H8 addenda |
| Eight fix reports in the same reports directory | Complete: `2026-10-12_lab-dax-proof-parity.md:1-101`; `...holdout-boundaries.md:1-84`; `...session-null.md:1-80`; `...closed-executions.md:1-87`; `...net-fee-verdict.md:1-63`; `...unavailable-flow.md:1-84`; `...readiness-gate.md:1-82`; `...trial-identity.md:1-91` |
| `MyTradingSys/system/revalidation/RV02_dax_harness_fixes.md`; `_COMMON.md` | Complete; task report path used as required by common rules |
| `MyTradingSys/backtest/PRE_REG_TEMPLATE.md` | 1-65, all twelve headings |
| T = `MyTradingSys/backtest/tom_bt.py`; `verdict.py`; `runtime/net_rr_floor.py`; `system/net_rr_floor.json` | 1-337; 1-144; 1-31; 1-8 |
| J = `src/main/java/datafeed/SetupCandidatesBuilder.java` | 136-228, 274-350, 450-534, 568-626, 661-779; count, ranking, target fallback, fees and JSON rounding |
| `src/main/java/datafeed/ExecutionMathConstants.java`; `ArchiveHistoricalSource.java` | 1-47; 1-184, complete |
| `src/main/java/datafeed/MarketDataSnapshot.java` | 717-780, 1039-1348; historical fetch, warm-up, profiles, unavailable flow and closed-bar boundary |
| `MyTradingSys/runtime/math_object_builder.py`; `backtest/layers/FORMULAS.md` | 440-478; 400-406 (fee definition) |
| `research/core_readiness_2026-09-27/harness/java/TomSnapshotGen.java`; `SnapAt.java` | Complete: 1-81; 1-34 |
| Tom transfer source documents (under `MyTradingSys/research/tom_transfer_2026-10-11/`) | Complete ROADMAP, PROBE_PLAN (1-80), RECALL_DAX (1-59), BACKTEST_FAILURES_RESEARCH (1-147), PROFILE_PARITY (1-99), TOM_TRADE_LEDGER.md (1-89), TOM_TRADE_LEDGER.csv (1-38: 37 rows), TOM_LEDGER_CANONICAL_GROUPS.csv (1-13: 12 groups) |
| `research/fast_track_2026-09-27/TOM_CORE_BT_REVIEW_2026-09-30.md` | 1-117, especially H2 and M1/M2/M6/M7/M9 |
| Source transcript files under `raw_transcripts_canonical/` | Method/management excerpts from `T6hDJcHrVBM_raw.txt:13`, `zQTbdEweG3c_raw.txt:19`, `n7ZSkjb7JXs_raw.txt:19`, `ujedEcmvBMk_raw.txt:13`, `UOBgXV20yCM_raw.txt:7`, `l8RZrBfzvp4_raw.txt:13`, `k0zm5NYn0IQ_raw.txt:19`; whole files loaded, relevant text extracted. `research/TOM_VERBATIM_INDEX.md:1-25` is an index only. |
| Task/protocol context | AGENTS -> CLAUDE; STATUS; LESSONS_DIGEST plus relevant full lessons A/D/E and 2026-10-12; CODEX_START; PARALLEL; LAYER_LAB; LAYERS Tom section; current RV02 and clean-split task JSON; read-only context pack |
| Tooling inspected, not product changes | `scripts/dev/tasks.py:1-125,262-275,374-378,430-493`; `codex_run.py:233-246`; `shot.py:582-590`; `make_layers_md.py:121-124` |

Commands: numbered Python/PowerShell source reads; targeted text searches (rg unavailable); the complete two-file unittest command below; and the reproduction appendix executed directly from this report. All test temporary directories were redirected into `research/layer_lab/`. No network, git, sync, Java generation, empirical backtest, or recall command ran. Generation subprocesses in fixtures were intercepted. Synthetic `report` calls used temporary paths, fabricated readiness/session/split declarations and invented bars. Their output is correctness evidence, never a market result. No empirical trial occurred, so TRIALS.md is unchanged.

Data range: existing tests use invented dates/prices, including H-120 through H+60 at the historical cutoff label 2026-04-11 and DST/forward labels. The independent appendix uses an invented complete 1,440-minute day at 2024-11-04, a synthetic 2024-11-05 cutoff, and future metadata/command labels. It reads no actual bars from those dates.

## Findings

| ID | HIGH/MED/LOW | file:line | What is wrong | Evidence / classification | Proposed fix |
|---|---|---|---|---|---|
| R1 | HIGH | D:615-659,724-740,794-801,831-836,1002-1018,1189-1192,1315-1320; `dax_data.py:85-108`; `ArchiveHistoricalSource.java:38-54,87-106` | End-to-end development isolation is incomplete before and around the simulator. `all` calls unrestricted conversion/generation before manifest validation. Generation ignores split/read mode, loads and hashes the full archive, and defaults through 2026-10-09. Development rows deserialize all snapshot payloads before excluding timestamps. Report accounting includes future-month snapshot metadata. | **MISMATCH.** Appendix: `all --market dax` with no manifests reaches `dax_data.py convert`; intercepted generation with `read_holdout=False` requests 2026-06-30 despite the synthetic 2024-11-05 cutoff. Adding only future metadata changes evaluated/kept/errors from 1/1/0 to 8/5/1 and full_dev True to False; outcome rows are identical. Full-file snapshot/data hashes also depend on future bytes. This demonstrates forbidden access/accounting influence, not a measured leaked trade return. | Validate manifests before every stage; materialize and hash only the authorized development prefix, including complete-minute boundary and warm-up; do not decode future payloads. Scope metadata/identities to the same interval. Add end-to-end sentinels for convert, Java load, snapshot parsing and report accounting. Preserve the one-time authorized holdout path separately. |
| R2 | HIGH | J:153-160,214-220,464-494; `verdict.py:88-89`; D:201-215; Tests:485-501 | H5's regression supplies an unrounded RR that actual Java JSON does not preserve. Rounding can turn a below-floor candidate into an eligible one. | **MISMATCH.** Independent RR is 1.247752247752; J:218 serializes 1.25, and Python checks `>= 1.25`, ignoring the false `net_rr_sanity`. Appendix: exact input -> WAIT_RR; serialized input -> SETUP_FORMING with a test-only proof shift 4. Java's farthest-node fallback retains below-floor targets, so serialization is reachable. At unshifted masked ceiling 1, no actual trade follows; the fee defect becomes visible in an eligible extension/new encoding. | Carry an unrounded, frozen per-instrument RR through the decision boundary, or independently recompute from a precisely defined decision geometry in the adapter. Keep display rounding separate. Test the real producer/consumer JSON boundary, both sides of the floor; invalidate affected caches. Coordinate shared-Java changes with its owner. |
| R3 | HIGH | D:1007-1018,1152-1159,1205-1206; `TomSnapshotGen.java:42-50,76-77` | A partial snapshot month can certify full development and unlock a holdout read. The authorization token is tied only to split identity, not the completed run's arms/code/session/readiness. | **MISMATCH.** Appendix creates one valid monthly snapshot with evaluated=1 and a one-instant producer command, against a complete 1,440-minute development day. The actual report builder returns full_dev=True (frozen cadence requires 96 evaluations for that day). Checks only require month filenames, zero reported errors and no >4-day internal gaps. Generator skips any existing month meta, including a partial month. `require_full_dev` only searches for a split token. | Validate per-month generation start/end/cadence and warm-up coverage, not filenames; reject partial/stale month products and missing edge coverage. Authorize holdout from a durable completed-development manifest bound to the intended code, arms, session, readiness and data. Include these cases in synthetic guard tests. |
| R4 | HIGH | D:724-764,790-815,1029-1047; fix report `2026-10-12_lab-dax-trial-identity.md:21-25` | H8 binds two identities without checking they describe the same underlying data. Fresh rows/reports may use old snapshots alongside revised execution bars. | **MISMATCH.** `cache_inputs` checks producer code and snapshot bytes, but never compares `origin.data` hashes to the current archive; the bars hash records whatever `_BARS` currently contains. Appendix changes all execution prices from 100 to 200 after freezing snapshot provenance, makes fresh rows, and the unmocked row/report validation accepts them: producer_archive_matches=False, fresh_rows=1, report_accepted=True. Existing H8 tests reject mutation after row creation, missing this pre-row mismatch. | Validate current authorized archive identity against the snapshot producer's data identity before building/reusing rows and before simulation. Bind only the split-authorized prefix (R1), never solve this by hashing holdout files. Test fresh row creation after an archive revision and require snapshot regeneration. |
| M1 | MED | D:244-245,278-284,383-390,943-944,1111-1117; template:37 | Original M1 still open, partially addressed by H3: no trade-through execution/report arm. | **MISMATCH:** entries and targets remain inclusive touch comparisons, stress changes only slippage. **MATCH:** null rejects marketable source entries, and shared session/limit mechanics improve passivity validation for reportable opportunities. The standalone strategy helper has no passive-side guard. | Pre-register tick-aware touch and trade-through views, validate passivity before any simulation, and apply identical rules to strategy/null. |
| M2 | MED | P:26; RECALL_DAX:15-17,20,22,50; BACKTEST_FAILURES_RESEARCH:37,79-80; TOM_TRADE_LEDGER.csv:3,10-14,27,29,32-38 | Original M2 remains open in historical summaries, though later ledger repairs clarify aliases and uncertainty. Source labels are not certified execution dates/prices. | **MISMATCH:** RECALL still gives T2 entry 25343 versus corrected ledger 25318; T3 initial stop 24257 versus corrected 24265. **MATCH to later repair:** canonical groups merge T4/T9 and T6/T10; all twelve groups are exposed and uncertified. T3b family labels still mix after-stop/after-partial, while trader text supports a stop-out; observed partial and stated stop-out must stay distinct. **NOT_IN_DATA:** independent frame confirmation in this workspace-only run. | Make downstream consumers use confidence/canonical fields and dated correction notices. Keep recording versus execution dates separate; have the existing date/split owners conservatively handle unresolved exposure. Do not silently edit historical results or invent exact dates. |
| M3 | MED | P:11,14-16; D:635,943-944,1245-1250; PROBE_PLAN:52-55; transcript citations below | Original M3 still open, partially addressed: session is explicit and the eight-bar clock is now labelled inherited, but trader home/holding and management readiness remain unproved. | **MATCH:** D requires a timezone/start/end/source addendum and discloses the unsourced eight-bar clock. **MISMATCH / NOT_IN_DATA:** no complete source-home/management contract in P. Tom describes partials, runners, logical stop changes and re-entry; these do not define a fixed eight-bar bracket or 15-minute sampling as his method. | Have the spec owner supply sourced home/session/management evidence; distinguish protocol cadence from trader rules; state the fixed-bracket interpretation limit. Do not tune unsourced clocks. |
| M4 | MED | P:17-18; `fees.py:30,43-50`; D:1110-1117; template:32 | Original M4 still open: the historical point-equivalent claim differs from the frozen fee fraction; noise/fee-share readiness is absent from the numerical readout. | **MISMATCH:** EUR2.5/EUR25=.1 point RT, but 2*.000005*24000=.24 points (EUR6), 2.4 times .1. **MATCH:** fees.py already explicitly discloses the conservative approximation and that EUR2.5 was not a fetched schedule. D prints median percentage stop width, not noise units or fee/R distributions. CFD BID/futures execution equivalence is NOT_IN_DATA. | Preserve historical text with an owner-reviewed economics addendum; document actual instrument/data mapping, noise units and fee-share evidence. No current broker fee claim is made here. |
| M5 | MED | P:27-28; D:902-908,1073-1117; template:52,62 | Original M5 still open: N>=100 is a post-run threshold, not a pre-run expected-N plan; pooled output lacks regime/session strata. | **MATCH:** fewer than 100 resolved fills returns insufficient N. **MISMATCH:** D groups by arm/period only; P supplies no expected N or stratum definitions. A required readiness string is not the missing analysis. | Freeze expected opportunities/fills and past-only regime/session definitions before an authorized run; show underpowered and stratified results beside pooled results without selecting winning cells. |
| M6 | MED | T:137-138,304-310,321-335; D:1086,1103; TOM_CORE_BT_REVIEW:72-81 | Original M6 still open: the pass CI remains an iid trade bootstrap despite potentially repeated intraday/zone episodes. | **MATCH to original warning:** 2,000 iid resamples of individual trades, seed 12345; changing zone price remains part of episode identity. **NOT_IN_DATA:** the amount of dependence or CI widening, since no market sample was read. | Pre-register session/day-block uncertainty or justify independence, count effective units, and use the justified CI for the pass bar. |
| R5 | MED | D:1237-1242 versus D:181-190 and Tests:319-360 | Generated report caveats still assert the H6 bug is active and that masked BTC retains order flow. | **MISMATCH:** report says every DAX long is contradicted and BTC flow is retained; adapter clears last-three deltas and both CVD slopes whenever cvd_aligned is masked. Passing long/short fixture yields aligned / SETUP_FORMING for both. | Update report text to the current unavailable-flow contract and test report assertions against adapter behavior; distinguish historical defects from current caveats. |
| E1 | LOW | RV02:14-15; A:25-27; ledger frame references; PROFILE_PARITY:6-23,80-99 | Source coverage cannot establish a fully historical/visual revalidation. | **NOT_IN_DATA:** commit patches and pre-fix worktrees cannot be obtained under the explicit no-git instruction. Frames/raw data lie outside the instructed workspace; real-data/holdout runs are forbidden. The profile document's six comparisons remain NOT_IN_DATA even after its later frame-read addendum. External bibliography and other layers' performance/source chains were not revalidated. | Authorized owner can check historical diffs/red runs and primary frames independently. Do not turn absent verification into zero, a readiness pass, or a reason to leave this audit card unfinished. |

Finding count: **4 HIGH, 7 MED (the six original MED plus stale H6 report text), 1 LOW evidence limitation**. Original MED findings were not promoted merely because they remain open. Existing research owners retain the actual clean split, source-fit and readiness work.

## H1-H8 disposition and regression provenance

For every H, the original finding, complete corresponding fix report, current implementation and new tests were read. **Current behavior was independently rerun. Historical fix patches and pre-fix execution are NOT_IN_DATA for all eight**, because this run may not use git or make worktrees. Red counts below are verified as statements in the read reports, not relabelled as executions performed by this audit.

| H | Current classification | Current implementation / tests | Historical red evidence in fix report |
|---|---|---|---|
| H1 | MATCH | D:88-103 mirrors J:568-584; spike emitted but uncounted; five minus four leaves ceiling one. Tests:370-471,948-988 pass stale/current/schema guards. | proof-parity:38-57: one count failure + one error; two rejection failures. Report originally BLOCKED on unrelated quick-gate failures; current local suite passes, historical ship not independently checked. |
| H2 | MISMATCH end to end; MATCH direct outcome boundary | D:447-526,911-922,1082-1091 correctly isolates full minutes and drops unresolved boundary orders; Tests:544-704 pass. R1/R3 show upstream and authorization gaps. | holdout-boundaries:43-55: 2 tests, 3 failures; seven final boundary tests reported green. |
| H3 | MATCH to mechanical repair, source readiness still NOT_IN_DATA | D:306-409,925-959 uses explicit local/DST session, original opportunities, passive offset, same order clocks/real execution/scheduling; Tests:707-822,1039-1055 pass. Empty draws and attrition remain visible. | session-null:36-44: lifetime assertion failed, session argument unsupported; six tests subsequently green. |
| H4 | MATCH within stated mask/download-artifact contract | D:220-287 and shared DAX route skip filler execution; gap-before-timeout priority and missing raw-file guard pass Tests:133-246. Mask does not certify that every intraday hole is scheduled. | closed-executions:41-67: 8 long/short subcase failures using old shared simulator alias; later 15 failures and a disabled-guard sensitivity failure. These are not all pre-fix-commit tests. |
| H5 | MISMATCH at actual producer/consumer boundary; gross overwrite removal MATCH | Sole coded arm preserves Java net_rr; Tests:485-531 pass. Independent arithmetic matches the report but J:218 rounds it; R2 reproduces admission below the exact floor. | net-fee-verdict:32-55: old primary SETUP_FORMING versus required WAIT_RR; test injects unrounded RR. |
| H6 | MATCH adapter; MISMATCH report text | D:181-190 removes unavailable CVD direction/slope; Tests:319-368 pass and preserve unmasked snapshots. R5 covers stale prose. | unavailable-flow:39-59: 1 test / 5 failed assertions; then green. |
| H7 | MATCH report-entry completeness and explicit DAX market selection | D:413-444 is the first operation of build_report; Tests:1117-1214 pass all twelve-item missing/waiver/error cases and DAX-only CLI with BTC cache. Completeness is deliberately not evidence authentication. `all` preprocessing precedes this guard (R1). | readiness-gate:36-53: corrected pre-fix fixtures 74 failures + 2 CLI errors; supplemental case used an in-memory reconstruction, not a historical worktree. |
| H8 | MISMATCH data-chain consistency; MATCH cache mutation and new-look accounting | D:705-815,1037-1047,1277-1291; Tests:826-947,1068-1115 pass mutation/identity/rerender checks. Two shifts give 8 rows / 2 ids, rerender unchanged, fresh look 12 / 3. R4 shows inconsistent snapshot/execution data can be frozen together. Recall-driver integration is still unverified. | trial-identity:44-56: 2 tests / 4 failures (mask, shift, floor, same-day row count). |

## Holdout isolation: raw input to printed output, without --read-holdout

Let H be `split.holdout_start` and C = H - embargo. This trace distinguishes access to future inputs, influence on accounting/identity, and use in a development return. No actual holdout was opened to perform it.

| Stage | Result | Trace / boundary |
|---|---|---|
| `all` dispatch / conversion | MISMATCH | D:1315-1320 invokes gen first; D:617 calls converter without date bounds; dax_data:89-94 decodes every .bi5. `--months`, `--start`, and `--end` do not constrain conversion. R1. |
| Java archive load / generator | MISMATCH access; future evaluation visible | ArchiveHistoricalSource:38-54,87-106 loads every symbol CSV. TomSnapshotGen:38-44 prints total bar count/first/last, then evaluates requested months (D:619-635 is not split-bounded). Complete-month selection, evaluated/kept/error counts and timing can include t>=H. R1. |
| Indicator windows / warm-up | MATCH on inspected numerical fetch path | MarketDataSnapshot:1039-1051,1093-1140,1325-1347 builds asOf windows and prior-day/week windows; ArchiveHistoricalSource:153-179 excludes buckets closing after the request end; forming bars are dropped. No t>=H bar can enter a development asOf window below C through this inspected range path. This does not remedy full-file loading or certify every Java detector's source fit. |
| Snapshot hashes / row conversion | MISMATCH access and identity isolation | D:724-740 hashes the whole gzip/metadata and retains producer data hashes for the whole archive; D:831-836 schedules all meta-backed months; D:796 deserializes a full snapshot before checking t>=C. Later rejection is not a pre-read boundary. R1. |
| Development execution bars / freshness | MATCH on prices | D:493-526 scans CSV timestamps before parsing numeric OHLC and keeps only bars with t+60s<=C. Filler only bridges retained bars. D:290-296 looks backward at two minute opens. Full file bytes are streamed, but future numeric values are not used in this loader's returned arrays. |
| Cached row/report load | MATCH selected payloads; MISMATCH full-file identity/accounting | D:860-868 discards excluded row keys; build_report:1033-1034 rejects a different cutoff. However JSON envelopes are parsed before selection, snapshot hashes remain full-file, and snapshot metadata sums have no cutoff. R1. No new claim that current development-only caches contain holdout verdict rows. |
| Entry/exit beyond boundary | MATCH | D:911-922 slices complete period bars; D:287 leaves crossing orders unresolved and D:922 drops them from resolved strategy output. No reopen/timeout/target at or beyond C is available. Tests:544-583,619-631,657-674. |
| Null / placebo | MATCH boundary | D:1082-1091 passes period_b; D:375-378 clips session candidates to its size. Same local session may straddle midnight but cannot add bars beyond C. Real and null outcomes use the same isolated arrays. Null mechanics are H3, uncertainty remains M6; no separate placebo driver is invoked. |
| Stress / fees | MATCH boundary, MISMATCH fee precision | D:1111 repeats simulate with split and +1 point; D:254-257 computes fees from permitted entry/exit. Verdict is point-in-time but has R2 rounding. Outcome fees do not use future bars. |
| Session / calendar / closure accounting | MATCH fixed local session and bounded mask; NOT_IN_DATA calendar truth | D:306-350 uses supplied ZoneInfo/window, not estimated future hours. Coverage checks stop at the dev date (D:990-1000). Null/held-across-close use period masks; >4-day gap heuristic uses dev arrays. A zero mask cannot distinguish a holiday from intraday missing data. |
| Development report / authorization | MISMATCH | D:1002-1018 sums all selected metadata months, including future months by default. Future errors alter full_dev. Month-file presence does not prove complete sampling (R3). Frozen manifest bytes may also depend on holdout snapshot/producer data identities (R1). |

No future-price influence on a development trade return was reproduced on the repaired direct simulation path. That narrower MATCH is insufficient for end-to-end isolation. Static inspection of the explicit holdout path also shows `rows --read-holdout` only calls require_full_dev (D:821-839), while reservation occurs later in build_report (D:979-983); any owner repair should include row-stage reservation/access ordering. This audit never invoked that path on real data.

## Fee arithmetic and parameter/source check

MATCH to FORMULAS:403-404, fees.py:48 and ExecutionMathConstants:31-37, for the H5 fixture E=100, stop=99, target=101.25:

`cost = 2 * 0.000005 * 100 = 0.001`

`net RR = (1.25 - 0.001) / (1 + 0.001) = 1249 / 1001 = 1.247752247752...`

The report's **1.247752** is correct to six decimals and below the 1.25 floor in system/net_rr_floor.json:2. The floor is operator-set testnet collection policy (:3-6), not a Tom quote. The round-trip .24-point calculation at price 24000 explains M4. Do not confuse the decision RR formula with realized outcome fees: the simulator charges entry fee at entry and exit fee at the realized exit (D:256), whereas the decision model approximates both legs at entry.

| Parameter / rule | Check against source |
|---|---|
| 15-minute cadence; two-minute freshness; 2024-11-04 start / historical 2026-04-11 split / 2026-10-09 end | MATCH implementation to P:11-13,25; D:70-73,290-296,619-635. These are research protocol inputs, not independently sourced trader parameters. Current report split is owner-supplied; generator still has the historical end cap. |
| Four variants; one pending/position slot | MATCH P:19 and T:141-168,225-244 to D:74,925-959. Source fidelity remains distinct from mirroring old code. |
| Five counted proofs, mask of four, score min(95,50+7*n+bonus), tfRank tie-break | MATCH J:182-194,280-350,568-584 to D:88-180. Absorption needs signed delta (J:723), so masking it as well as P's other three flow proofs is justified and disclosed. Ceiling 1 means WATCH needs synthetic shift >=2 and SETUP_FORMING >=4; these are extensions, not sourced Tom rules. |
| Half-volume placeholder and rounding | MATCH dax_data:100-106 / four data tests: 6-decimal volume and 7-decimal half-volume produce exact zero delta in the tested micro-volume cases; H6 labels this information unavailable before direction gates. No assertion of real exchange volume. |
| FEES_FDAX, +1-point stress | MATCH P:17-18 to fees.py:48-50 and D:1111; fraction matches Java:23. Exact fee gate mismatch is R2; .1 versus .24 points is M4. |
| 200 null draws; seed 7; >=30 real resolved fills for p; 2000 bootstrap draws / seed 12345 | 200 MATCH P:22. Seeds and minimum-null N MATCH implementation D:353,403-404 and T:304; frozen in D:1042. They are numerical protocol choices, not Tom quotations, and P does not itself pre-register all of them. No lags/shift-permutation experiment was run. |
| Eight zone-timeframe bars; >4-day hole threshold | Eight MATCH inherited T:12-17 but explicitly NO-SOURCE in PROBE_PLAN:55; now disclosed in D:1249. Hole threshold D:1133-1145 is an engineering heuristic, not an exchange calendar or trader rule. |
| Source management and session language | MATCH qualitative text: T6hDJcHrVBM_raw.txt:13, "Take out one position here and the rest stays in"; k0zm5NYn0IQ_raw.txt:19 describes moving stops "with logic behind not with only numbers"; UOBgXV20yCM_raw.txt:7 discusses predefined profit targets via limit order; ujedEcmvBMk_raw.txt:13 describes being flushed out then re-entry. n7ZSkjb7JXs_raw.txt:19 discusses pre-market and a 5-minute chart. None certifies exact ledger timestamps or a universal eight-bar management rule. |

## Twelve-item PRE_REG_TEMPLATE assessment

The new gate verifies declaration completeness; it does not supply the scientific answers. The template's twelve items MATCH BACKTEST_FAILURES_RESEARCH:115-126. The inspected transfer directory contains profile JSONs, but no production HOLDOUT_CLEAN.json; the clean-split task remains refined with empty result and a date-column dependency. No readiness approval is inferred.

| # | Assessment | Evidence / remaining requirement |
|---|---|---|
| 1 Home market/TF/session/hold | Partial MATCH / NOT_IN_DATA | P:9 acknowledges CFD versus FDAX; qualitative source excerpts above. Session manifest required but no sourced production interval verified; management/TF contract M3. |
| 2 Frame ledger + design/check split | NOT_IN_DATA | 37 rows / 12 candidate groups, all exposed and execution-uncertified (ledger.md:4-15 and canonical CSV). Current clean-split card lacks delivered manifest; no primary frames inspected here. |
| 3 CHECK recall AND fire rate | NOT_IN_DATA | RECALL_DAX:3-8 is a historical 0/7 STOP, not a v2 held-back check. ledger.md:7 warns against using those denominators. No new recall/frequency estimate made. |
| 4 Proof inputs available | Partial MATCH | H1/H6 correctly handle absent aggressor flow; ceiling is one. CFD profile-volume parity/OI/other unavailable inputs are not established as usable trader evidence. P:9-10, PROFILE_PARITY:6. |
| 5 Profile/snapshot parity | NOT_IN_DATA | PROFILE_PARITY:14-23 has six unavailable comparisons; :80-99 adds frame observations but keeps verdict NOT_IN_DATA. No numerical parity outcome independently endorsed. |
| 6 Economics/noise/fee share | MISMATCH / partial MATCH | Frozen fee rates match; exact precision gate R2 and diagnostics M4 remain. |
| 7 Touch AND trade-through / passivity | MISMATCH / partial MATCH | H3 passivity check improves mechanics; touch-only M1 remains. |
| 8 Management match or stated mismatch | Partial MATCH | D:1249 acknowledges inherited clocks; source management differs, M3. No claim this bracket tests the full trader method. |
| 9 Like-for-like null | MATCH mechanical contract | H3 tests cover source opportunities, local window/DST, offsets, clocks, execution and scheduling. Production window provenance NOT_IN_DATA. |
| 10 Pre-run power | MISMATCH / NOT_IN_DATA | Correct insufficient-N label, but expected N absent; M5. No empirical count inferred from the teaching ledger. |
| 11 Clean holdout / all looks counted | MISMATCH | Direct outcome slice MATCH; R1/R3/R4 remain, actual clean split absent. New arm/look accounting MATCH H8 tests; historical/recall trial integration not re-executed. |
| 12 Regime/session strata | MISMATCH | Current report is pooled within arm/period; M5. No future data was used to invent strata. |

## Known-finding check

**CONFIRMED (current reproduction):** `test_tom_dax_bt.py` has 62 passing tests on JIS-NUC. `test_dax_data.py` adds 4 passing tests. Combined run: 66 in 1.867 seconds; no skipped tests. This confirms the number/host now; the exact earlier 2026-10-12 execution is supported only by the read H8 report:74-79, not a recovered historical process log.

Exact command used (only TemporaryDirectory placement is changed; all test cases/assertions are unchanged):

```powershell
python -B -c "import sys,tempfile,unittest,platform; from pathlib import Path; sys.path.insert(0,str(Path('MyTradingSys/backtest').resolve())); root=Path('MyTradingSys/research/layer_lab').resolve(); tempfile.tempdir=str(root); original=tempfile.TemporaryDirectory; tempfile.TemporaryDirectory=lambda *a,**kw: original(*a,**dict(kw,dir=str(root))); print('HOST',platform.node(),'PYTHON',platform.python_version()); suite=unittest.defaultTestLoader.loadTestsFromNames(['test_tom_dax_bt','test_dax_data']); result=unittest.TextTestRunner(verbosity=2).run(suite); print('COUNTS',result.testsRun,'FAILURES',len(result.failures),'ERRORS',len(result.errors),'SKIPPED',len(result.skipped)); sys.exit(not result.wasSuccessful())"
```

Complete summary: `HOST JIS-NUC PYTHON 3.14.6`; `Ran 66 tests in 1.867s`; `OK`; `COUNTS 66 FAILURES 0 ERRORS 0 SKIPPED 0`; process exit 0. Generation command strings and report paths printed by tests are intercepted or temporary synthetic fixtures, not production runs. The quick/full repository gate is runner-owned and was not invoked.

## Not checked

- Historical follow-renames patches and red-on-pre-fix worktrees: prohibited git operations; NOT_IN_DATA for all H1-H8. Reported red evidence was read and distinguished from current execution.
- Real-data DAX/BTC outcomes, actual holdout, empirical CI changes, recall and profile/frame remeasurement: excluded by the task. Files under F:/MTS/data were not accessed; the context pack was the sole explicitly supplied outside-workspace read-only reference.
- External bibliography at BACKTEST_FAILURES_RESEARCH:140-147, broker/exchange fee schedules, and other traders' performance/source chains: network/out-of-scope material, not endorsed as independently verified evidence.
- Every Java rule/detector or all historical engine tests: this audit traces the cited harness/fee/proof/range boundaries, not a full independent Tom v2 specification audit. No Java compiler/runtime was launched.
- The actual future production readiness/session/split declarations, exact execution times and contract identity: not delivered/verified in the read evidence. Existing owners remain responsible.

## Follow-up cards

One card per HIGH, lane SONNET, layer tom, priority 1, scoped to synthetic repairs only:

| Finding | Card ID |
|---|---|
| R1 | `rv02-fix-dax-preprocessing-isolation` |
| R2 | `rv02-fix-dax-rounded-rr-gate` |
| R3 | `rv02-fix-dax-full-dev-authorization` |
| R4 | `rv02-fix-dax-producer-data-binding` |

Cards reference this report and its reproduction appendix. They are captured for refinement, not authorization to run a backtest or edit shared live code. Existing clean-split/date/encoding/cost owners cover source readiness. No code or spec fix was applied in this audit.

Card creation used the unmodified `tasks.main(['new', title, '--lane', 'SONNET', '--layer', 'tom', '--prio', '1', '--id', id])` CLI entry point. A Python audit hook restricted writes to the two lab-authorized directories. Each card was created successfully; the CLI's optional automatic `LAYERS.md` regeneration was denied before writing and caught by `refresh_layers`, preserving audit scope. Closure uses the same guard with `tasks.main(['done', 'rv02-dax-harness-fixes', '--result', result])`; the lab delivery index is regenerated with `python -B scripts/dev/codex_run.py index`. The derived LAYERS page can be refreshed by its authorized owner outside this audit.

## Independent synthetic reproduction

The following code ran against the unchanged product files, exit 0. It contains no failing test assertion: it records observed defects for FIX-FIRST, so a newly discovered defect does not masquerade as failure of the required passing suites. Only generated fixtures are removed, within their temporary lab directory.

RESULT:

```text
R2 exact 1.247752247752 serialized 1.25 verdicts ['WAIT_RR', 'SETUP_FORMING']
R3 evaluated 1 full_dev True expected_daily_15m_grid 96
R1_METADATA before {'evaluated': 1, 'kept': 1, 'errors': 0, 'full_dev': True} after {'evaluated': 8, 'kept': 5, 'errors': 1, 'full_dev': False} outcome_rows_identical True
R4 producer_archive_matches False fresh_rows 1 report_accepted True snapshot_price 100 execution_price 200.0
R1_ALL without_manifests_first_child dax_data.py convert synthetic interception before any child process
R1_GEN read_holdout False end 2026-06-30T23:59:00Z cutoff 1730764800.0
```

To reproduce, execute the Python fence between RV02_PROBE_START and RV02_PROBE_END using `python -B`; source paths resolve from the workspace root. This is an audit fixture, not a product-code addition or production-readiness declaration.

<!-- RV02_PROBE_START -->
```python
import sys, json, gzip, tempfile, datetime as dt
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import ExitStack
sys.path.insert(0, str(Path('MyTradingSys/backtest').resolve()))
import tom_dax_bt as D
import test_tom_dax_bt as S
from verdict import compute_verdict

# R2: independently calculated fee RR, then the producer's documented rounding.
cost = 2 * .000005 * 100
exact = (1.25 - cost) / (1 + cost)
verdicts = []
for net in (exact, round(exact, 2)):
    c = S.cand(1, 'long', 'vwap', 'vwap_band', S.proof_node('MODERATE'), 1, gross=1.25, net=net)
    c['math']['target'] = 101.25
    c['math']['net_rr_sanity'] = False
    result = D.rows_for_snapshot(S.snap([c]), S.parse_ts, S.aligned,
        lambda s, pd: compute_verdict(s, pd, floor=1.25), shifts=(4,))
    verdicts.append(result['coded/4']['verdict'])
print('R2', 'exact', format(exact, '.12f'), 'serialized', round(exact, 2), 'verdicts', verdicts)

lab = Path('MyTradingSys/research/layer_lab').resolve()
with tempfile.TemporaryDirectory(dir=lab) as td:
    root = Path(td)
    archive, snaps, work, raw = [root / x for x in ('archive', 'snaps', 'work', 'raw')]
    for p in (archive/'klines', snaps, work/'rows_dax', raw):
        p.mkdir(parents=True)
    data = archive/'klines'/'GER40-1m-2024-11.csv'
    start = int(D.T_DAX_START * 1000)
    def prices(value):
        S.write_klines(data, [(start+i*60000, value, value, value, value, 1) for i in range(1440)])
    prices(100.)
    # Explicit synthetic raw artifact. Report checks presence, never decodes it.
    (raw/'2024-11-04.bi5').write_bytes(b'synthetic artifact')
    source = snaps/'2024-11.jsonl.gz'
    c = S.cand(1, 'short', 'vwap', 'vwap_band', S.proof_node(spike=True), 0)
    with gzip.open(source, 'wt', encoding='utf-8') as fh:
        fh.write(json.dumps(S.snap([c], t='2024-11-04T10:00:00Z'))+'\n')
    meta = snaps/'2024-11.meta.json'
    meta.write_text(json.dumps(dict(month='2024-11', step_min=15, evaluated=1, kept=1, errors=0)), encoding='utf-8', newline='\n')
    producer = dict(codes=D.generation_codes(), snapshot_sha256=D.file_hash(source),
        data={str(data): D.file_hash(data)}, environment={'synthetic': 'fixture'},
        command=['synthetic-generator', '--start', '2024-11-04T10:00:00Z', '--end', '2024-11-04T10:00:00Z'])
    (snaps/'2024-11.inputs.json').write_text(json.dumps(producer), encoding='utf-8', newline='\n')
    split_path = root/'split.json'
    split_path.write_text(json.dumps(dict(design_end_utc='2024-11-04T23:59:00Z',
        holdout_start_utc='2024-11-05T00:00:00Z', embargo_s=0)), encoding='utf-8', newline='\n')
    session = root/'session.json'
    session.write_text(json.dumps(dict(timezone='UTC', start='09:00', end='17:00',
        source='Synthetic fixture, no trading authority')), encoding='utf-8', newline='\n')
    a = SimpleNamespace(readiness_manifest=S.readiness_fixture(root), split_manifest=split_path,
        null_session=session, read_holdout=False, shifts=[0], months=None, market='dax',
        smoke=False, mask='all', look_id='synthetic-audit-only')
    cut = D.load_split(split_path)['dev_end']
    with ExitStack() as stack:
        for name, value in dict(DAX_ARCHIVE=archive, DAX_SNAPS=snaps, DAX_RAW=raw, WORK=work,
                                REPORT=root/'report.md', REGISTRY=root/'trials.csv',
                                HOLDOUT_MARKER=root/'holdout.json').items():
            stack.enter_context(patch.object(D, name, value))
        stack.enter_context(patch.object(D, '_BARS', D.load_development_bars(archive/'klines', cut)))
        job = ('dax', source, work/'rows_dax', (0,), D.MASK_OF, cut)
        D._rows_month(job)
        base = D.build_report(a)
        print('R3', 'evaluated', base[3]['dax']['evaluated'], 'full_dev', base[3]['dax']['full_dev'],
              'expected_daily_15m_grid', 96)
        # A future-month metadata file changes printed development accounting and authorization.
        future = snaps/'2024-12.meta.json'
        future.write_text(json.dumps(dict(evaluated=7, kept=4, errors=1)), encoding='utf-8', newline='\n')
        after = D.build_report(a)
        print('R1_METADATA', 'before', {k:base[3]['dax'][k] for k in ('evaluated','kept','errors','full_dev')},
              'after', {k:after[3]['dax'][k] for k in ('evaluated','kept','errors','full_dev')},
              'outcome_rows_identical', base[0] == after[0])
        future.unlink()
        # A normal fresh row build can combine an old snapshot with revised execution prices.
        prices(200.)
        D._BARS = D.load_development_bars(archive/'klines', cut)
        for p in (work/'rows_dax').iterdir():
            p.unlink()  # only two files made above, inside this temporary fixture
        generated = D._rows_month(job)
        D.build_report(a)
        print('R4', 'producer_archive_matches', producer['data'][str(data)] == D.file_hash(data),
              'fresh_rows', generated[1]['rows'], 'report_accepted', True,
              'snapshot_price', 100, 'execution_price', D._BARS.o[600])
        # All CLI work before readiness: subprocess invocation is intercepted, never executed.
        calls = []
        def intercept(command, **kw):
            calls.append(command)
            raise RuntimeError('synthetic interception before any child process')
        with patch.object(D.subprocess, 'run', side_effect=intercept):
            try:
                D.main(['all', '--market', 'dax'])
            except RuntimeError as exc:
                print('R1_ALL', 'without_manifests_first_child', Path(calls[0][2]).name, calls[0][3], str(exc))
        calls = []
        with patch.object(D.subprocess, 'run', side_effect=lambda command, **kw: calls.append(command)), \
             patch.object(D, 'complete_months', return_value=['2026-06']), \
             patch.object(D, 'generation_environment', return_value={'synthetic': 'fixture'}), \
             patch.object(D, 'DAX_SNAPS', root/'empty-snaps'):
            D.cmd_gen(SimpleNamespace(start=None, end=None, months=None, shards=1,
                                     read_holdout=False, split_manifest=split_path))
        gen = calls[1]
        print('R1_GEN', 'read_holdout', False, 'end', gen[gen.index('--end')+1], 'cutoff', cut)
```
<!-- RV02_PROBE_END -->
