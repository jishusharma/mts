# CORE READINESS PLAN - Tom core and layers, tested on history, before API testing
# Date: 2026-09-27
# Purpose: Revalidation of the live decision path, measured findings, operator decisions, and designed tasks with executable acceptance
# Status: FRESH
# Canonical path: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\research/core_readiness_2026-09-27/
# Author: Opus 5.5 session 2026-09-27. Design only: nothing live was edited. All numbers below were measured, not estimated.
# Supersedes as the "what next" source: research/_archive/loose_2026-10/OPUS_REVIEW_REQUEST.md, opus_handoff_context.md, operator_summary.md, SESSION_HANDOFF_2026-09-27.md, execution_system_architecture.md (see task G2).

## 0. ONE-PARAGRAPH VERDICT

The core is not ready for API testing, and the reason is not the API. The live
decision path is Java (Tom core: zones, setups, stop, target, R:R, proof count),
then Python (proof-direction check), then PowerShell (verdict ladder, alerts).
Test coverage is inverted: the 125 math tests cover Python zone math that is NOT
on the live path, while the Java Tom core and the proof-direction block had no
regression tests at all. Measured on 9,175 archived snapshots: of 260
SETUP_FORMING signals, 158 exist only because the floor/ceiling mode suspends the
2:1 NET R:R hard stop (compiled_engine.md sec 6 row 4 and sec 2.6 say Tom never
lowers it), and 198 exist only because the proof count adds signals that point
AGAINST the trade (book imbalance, finished auction) or come from the speed proxy
tagged "CRYPTO HACK, NOT TOM". With both corrected, 23 of 260 survive. Those are
operator decisions (section 3), not bugs to silently fix. This session built and
proved the test harness that makes every such decision measurable (section 5).

## 1. LAYER MAP (verified from code, 2026-09-27)

| Layer | What | Code | Spec | Regression test before today |
|---|---|---|---|---|
| L0 ingest | Binance REST -> snapshot fields | MarketDataSnapshot.java (1468 lines) | data_schema docs | none |
| L1 Tom core | state, directions, zones, tier, setup type, stop, target, R:R, proof, score, rank | SetupCandidatesBuilder.java (842) + ExtraSetupBuilder.java | compiled_engine.md sec 1-7 | VerifyScbEdits.java, 12 reflection checks, not in Build-Check |
| L2 proof direction | aligned / contradiction | math_object_builder.py BUG-008 block via build_mo_cli.py | none in compiled_engine | 0 tests |
| L3 verdict ladder | NO_TRADE .. SETUP_FORMING | start-trading-day.ps1 Compute-Verdict L150-248 | compiled_engine.md sec 6, 8 | backtest/parity.py 689/692, not in Build-Check |
| L4 alert gate | persistence, cooldowns, position awareness, scalp pre-gate | start-trading-day.ps1 L500-760 | none | none |
| Modules | regime_classifier, quad_classify, outcome_labeler, kline_archiver, state_code (statemachine), session frame fields | runtime/*.py, StateCodeEmitter.java | PROJECT_VISION doctrine | none |
| Execution | trade plans -> Deribit | execution/*.py | T050 | validator/compiler examples only |

Python mts_math.py zone functions (distance cap, tier, R:R) are a second
implementation of L1 math. They feed only math_object zones/hard_stops_compiled,
which the live verdict does not read. Only L2 is taken from math_object live.

## 2. FINDINGS (measured; F-number, evidence, severity)

F1 CRITICAL - R:R hard stop suspended for most actionable signals.
   Compute-Verdict mode floor_reaction/ceiling_reaction (B058 A+B) skips the net_rr gate within 0.15 pct of daily VAL/VAH or 1h/15m swings.
   158 of 260 SETUP_FORMING have net_rr_sanity=false. No Tom citation. Conflicts with compiled_engine.md (runtime authority). -> decision D1.
F2 CRITICAL - B071 fail-open located exactly. start-trading-day.ps1 ~L448 `$pd = "aligned"`, build_mo_cli exit code discarded (`$null = Invoke-WithTimeout`), empty catch.
   If L2 errors, 1,917 of 9,168 snapshots would be WATCH or SETUP_FORMING unchecked (715 SETUP_FORMING). Fix designed and proven, task B1.
F3 HIGH - Proof count is not directional. countSignals() (SetupCandidatesBuilder L547-558) adds +1 for any book imbalance outside 0.67-1.5 and any finished auction, whichever side they favour, and +1 for speed (crypto proxy per compiled_engine sec 2.6 SSOT note).
   Since the golden boundary, 161 of 613 rank-1 candidates carry a book signal against their direction; speed is in 113 of 156 proof>=5 cases. -> decision D4.
F4 HIGH - Test coverage inverted (see layer map). T037 stays BLOCKED on a pom edit; the reflection pattern in scripts/tools/VerifyScbEdits.java needs no pom change and is used by task A3.
F5 HIGH - classifyState() can never return trend_unhealthy or transition: it tests cvd_slope for "divergent"/"aligned", but the snapshot only ever carries rising/falling/flat (9,175 of 9,175).
   Consequence: POC counter-trend setups (compiled_engine sec 2 zone map, "CT unhealthy trend only") are unreachable (0 POC candidates ever). This is B063 (divergence undefined) seen from the engine side. -> decision D5.
F6 HIGH - Extra candidates drive the verdict. When SetupCandidatesBuilder returns none, ExtraSetupBuilder fvg_*/momentum candidates (rank 11+) sit at setup_candidates[0] and Compute-Verdict reads [0] blindly: 343 snapshots.
   compiled_engine.md sec 2: FVG is an EXIT area, NOT entry. 116 extra candidates have inverted geometry (e.g. long with target below entry, printed net_rr 36.88). Any executor reading [0] would act on them. -> decision D3.
F7 MED - Historical mode (Main "historical") is unfit for backtesting: zeroes trade_flow, book_imbalance, funding, OI; omits session and order_flow; and fetches LIVE spot_perp_basis and oi_breakdown into a past snapshot (look-ahead).
   book_imbalance=0.0 turns 100 pct of long rank-1 into L2 "contradiction" (2,233 aligned flipped). Task D1-L0.
F8 MED - Duplicate implementation drift: Python get_distance_cap differs from Java (and from compiled_engine sec 2.6) for vwap bands (0.3 vs 0.2), 1h swings (0.3 vs 0.5), prior_day_close (0.3 vs 0.4), fvg. Java matches the doc; Python tests enshrine the stale values. -> decision D2.
F9 MED - SETUP_CONFIRMED is unreachable: Compute-Verdict never emits it; compiled_engine sec 8 defines it; alert gating lists it. Proof thresholds 3 and 5 in Compute-Verdict appear nowhere in compiled_engine.md. -> decision D6.
F10 LOW - L2 input validation absent: build_math_object returns "aligned" for current_price "x" or None; raises only on cvd null.
F11 LOW - net_rr is rounded to 2 dp on output, sanity uses the unrounded value: 72 rows show 2.0 with sanity false. Display only, not a defect.
F12 LOW - Rule-order dependence in Compute-Verdict: contradiction cap runs before the broken-value override, so the same snapshot ends WAIT_PROOF or WAIT_RR depending on L2. Both non-actionable; reason text differs.

Verified OK (no action): Java L1 steps 1-8 are exactly reproducible from archived snapshot fields (118/118 candidates, 1,652/1,652 fields); risk math, tier, cap table, score formula and rank order hold on 100 pct of current-code snapshots; module-only fields (session, funding, OI, liquidation, basis, order_flow, post-funding VP) do not gate L2/L3 (0 diffs over 9,171); verdict port parity 689/692 with the 3 known B071 misses; 125 math + 5 doc tests pass.

## 3. OPERATOR DECISIONS (each with the exact historical effect; the implementing task uses it as its acceptance matrix)

D1 R:R suspension (F1). Options: (a) revert - hard stop always applies; (b) keep as a documented [SYSTEM] exception in compiled_engine sec 6 with evidence.
   Effect of (a) on 9,175 snapshots: SETUP_FORMING->WAIT_RR 158, WATCH->WAIT_RR 807, WAIT_PROOF->WAIT_RR 1195, WAIT_TRIGGER->WAIT_RR 893.
   Recommendation: (a). The authority document is explicit; B058 cites alert churn, not Tom.
D2 Zone-math authority (F8). Recommendation: Java is the single implementation; Python zone functions aligned to sec 2.6 now and marked legacy. No verdict effect (off live path).
D3 Extra/FVG candidates (F6). Recommendation: move ExtraSetupBuilder output to a separate snapshot field module_candidates; setup_candidates holds ranks 1-3 only.
   Effect: WAIT_PROOF->NO_TRADE 174, WAIT_TRIGGER->NO_TRADE 114, WAIT_RR->NO_TRADE 59. No actionable verdict changes.
D4 Directional proof count (F3). Options: count book/finished-auction only when they favour the trade; move speed out of the count (module reading).
   Effect (rank-1 re-score, approximate - rank order not recomputed): SETUP_FORMING->WATCH 198, WATCH->WAIT_PROOF 521, WAIT_RR->WAIT_PROOF 110.
   D1(a)+D4 together: of 260 SETUP_FORMING, 158 -> WAIT_RR, 79 -> WATCH, 23 remain.
   Recommendation: adopt; this is gap class 3 (implemented incorrectly) per PROJECT_VISION, and speed is a declared non-Tom proxy.
D5 Unhealthy trend / transition states (F5 + B063). Needs a Tom-cited divergence definition before code. Until then document in compiled_engine sec 1 that the engine emits balance/trend_healthy only.
D6 Proof thresholds and SETUP_CONFIRMED (F9). Document 3/5 as [SYSTEM] in compiled_engine sec 8 (critical file, four-step proof), and either define a Tom-cited trigger for SETUP_CONFIRMED or remove it from the alert lists. An executor must never key on SETUP_CONFIRMED until then.
D7 B071 floor (F2). When L2 fails, cap at WAIT_PROOF with reason "proof_dir error" (spec'd in fail_closed_spec.py). Recommendation: accept as written.

## 4. TASKS (ordered; owner per model guidance; every acceptance is a command with an exact expected output)

Run all harness commands from repo root on the desktop. Harness path H = MyTradingSys\research\core_readiness_2026-09-27\harness
Baselines were measured 2026-09-27; the corpus grows while the loop runs, so counts under "new (not in baseline)" are expected.

PHASE A - guardrails (no behaviour change). Do first.
A1 [Haiku or NUC worker] Adopt proof-direction cases: copy CASES and test_cases() from H\proof_direction_cases.py to MyTradingSys\tests\test_proof_direction.py (rename test_cases to test_proof_direction_cases, keep import path via sys.path to runtime).
   Accept: `python -m pytest MyTradingSys/tests -q` -> 126 passed + docs; Build-Check STATUS: PASS; UNIT_TEST_PLAN.md updated (single source of test counts; fix its mojibake while there).
A2 [Sonnet] New script scripts\tools\core_check.ps1 that runs, in order, and prints one STATUS line: `python $H\core_invariants.py --since 2026-09-24T13:51:32Z` (expect RESULT: PASS), `python $H\verdict_golden.py` (expect NO CHANGE vs baseline), `python $H\module_isolation.py --group A` and `--group B` (expect PASS, 0 diffs, 0 exceptions), `python MyTradingSys\backtest\parity.py` (expect PARITY n-3 / n, misses only 2026-09-24T18:54:11, 18:55:10, 19:06:11).
   Not wired into Build-Check (4-5 min runtime); run before and after every core change and at session end. Accept: core_check.ps1 STATUS: PASS on current tree.
A3 [Sonnet] L1 replay on desktop: `.\$H\java\run_replay.ps1` (builds a temp test copy, never touches src).
   Accept: RESULT: PASS over every snapshot since 2026-09-24T13:51:32Z (>= 624). Mutation proof: edit the temp copy 0.75 -> 0.70, expect RESULT: FAIL with math.net_rr diffs. Add a line for it to core_check.ps1.
A4 [Sonnet, desktop network] Extend the replay to step 9 (proof): per snapshot, fetch Binance klines as of timestamp_utc with the same limits and dropFormingBar rule as MarketDataSnapshot.fetchMultiTimeframeAsOf (1m limit 1440), cache under Dumps\kline_cache\, pass real klines1m, and compare proof fields, proof_count, score, rank with MAX_CANDIDATES at 3.
   Accept: pilot 200 snapshots spread over 09-24..now; rank-1 proof_count match >= 95 pct; every mismatch classified as bar-boundary (fetch time vs timestamp) or defect. This decides whether L1 is fully replayable, which unlocks testing beyond the 14 archived days.
A5 [Sonnet] L0 contract: H\snapshot_contract.py (to write) - required top-level keys present, enums within observed sets (cvd_slope, vwap_slope in rising/falling/flat; price_vs_va in in_va/above_vah/below_val), val <= poc <= vah for every VP block, every level within 25 pct of current_price, numeric types. Record baseline counts like core_invariants.py; PASS = no regression.

PHASE B - B071 fail-closed (critical files: start-trading-day.ps1 is on the critical list - four-step proof).
B1 [Sonnet build, Opus review] 
   PowerShell: `$pd = "error"` before the build_mo_cli call; capture its rc; set $pd from the math object only when rc -eq 0 and the value is aligned or contradiction; else Log-Line "PD_ERROR rc=<rc>". In Compute-Verdict, after the contradiction cap: if $proofDir is not aligned/contradiction and verdict is WATCH or SETUP_FORMING -> WAIT_PROOF, reason "proof_dir error".
   build_mo_cli.py: wrap in try/except, exit 1 on any exception, write no output file.
   Python port backtest/verdict.py: reference patch below (proven on a scratch copy 2026-09-27).
   Accept: `python $H\fail_closed_spec.py` -> RESULT: PASS (today: FAIL, S1 no parameter, S2 1,917); `python $H\verdict_golden.py` -> NO CHANGE; parity unchanged. Live proof: one cycle with build_mo_cli.py renamed for that cycle only -> log shows PD_ERROR and no SETUP_FORMING.
   Reference patch for verdict.py (replace proof_dir_of; add the cap after the contradiction line):
     VALID_PD = ("aligned", "contradiction")
     def proof_dir_of(snap, fail_closed=False):
         try:
             mo = build_math_object(snap); pd = mo.get("proof_direction_status")
         except Exception:
             return "error" if fail_closed else "aligned"
         if pd in VALID_PD: return pd
         if pd is None and not (snap.get("setup_candidates") or []): return "aligned"
         return "error" if fail_closed else (pd or "aligned")
     ...
     if str(pd).lower() not in VALID_PD and v in ("WATCH", "SETUP_FORMING"):
         v, r = "WAIT_PROOF", "proof_dir error"
   Then close B071 with receipt; T051 precondition "B071 fixed" met.

PHASE C - decisions into code (only after the operator rules on D1-D6; each change proven by an exact transition matrix)
Method for every C task: write the matrix from section 3 into a JSON file {"OLD/pd->NEW/pd": count}; run `python $H\verdict_golden.py --expect that.json`; must print EXPECTED MATRIX: MATCH (counts measured on the baseline rows only). Then `--write-baseline` to freeze the new behaviour, and update core_invariants baselines where the task says.
C1 [Sonnet] D1: remove the suspend_rr path in Compute-Verdict (critical file) and verdict.py. Keep the mode field for display. Expected matrix: section 3 D1(a) restricted to baseline rows.
C2 [Sonnet] D3: MarketDataSnapshot.java writes ExtraSetupBuilder output to module_candidates, not setup_candidates (both live and historical paths). Java-side change: verdict_golden cannot see it (it replays archived snapshots), so accept with: core_invariants I12 and I14 set to baseline 0 from the deploy time (--since <deploy>) and PASS after 1 hour of live loop; plus a verdict.py guard: top = first candidate with rank <= 3 (expected matrix = section 3 D3).
C3 [Sonnet build, Opus review] D4: countSignals() counts book imbalance only when it favours the trade (long: > 1.5, short: < 0.67), finished auction only when the exhausted side is the opposite side (long: "sell", short: "buy"), and no longer counts speed (keep speed in the proof JSON). Accept: A3 replay unchanged (steps 1-8), A4 replay shows proof_count deltas equal to the recount rule, live snapshots after deploy satisfy a new core_invariants check I16 "proof_count equals directional recount".
C4 [Sonnet] D2: mts_math.get_distance_cap aligned to compiled_engine sec 2.6 (critical file), tests updated, docstring marks zone math legacy/advisory. Accept: new check - for every rank-1 candidate, get_distance_cap(zone.type) == math.distance_cap (today 7,958 diffs over all candidates) -> 0.
C5 [Opus] D5/D6 text for compiled_engine.md sec 1 and sec 8 (critical, operator approval, four-step proof). No code.

PHASE D - L0 historical mode (enables testing beyond archived data; needs A4 result first)
D1-L0 [Sonnet] MarketDataSnapshot.fetchHistoricalSnapshot: no live calls (remove buildSpotPerpBasis and buildOiBreakdown from the historical path; emit them with confidence UNAVAILABLE); flow fields that cannot be reconstructed become null, not 0.0, with a data_quality block listing them; add the session block (buildSession works from klines); set the liquidation warning node that is built and never attached. L2 must treat book_imbalance null as unknown (add a proof_direction case: long, book None -> aligned).
   Accept: text search of the historical method shows zero calls to spotPrice, premiumIndex, longShortRatio, topLongShortPositionRatio; one historical snapshot for a timestamp that also exists live matches the live archive on all kline-derived fields (VPs, VWAP, CVD session value/slope, structure, prior_day, session) within 0.01 pct.

PHASE E - execution layer corrections (last session's code; required before any testnet order)
E1 [Sonnet build, Opus review] executor.py: protective stop is type stop_market with trigger_price and trigger mark_price, reduce_only, placed right after the FIRST entry fill and resized (private/edit amount) after every further fill. Today it is a reduce-only LIMIT at the stop price: for a long that is a sell limit below market, which fills immediately and closes the position. Today it is also placed only after every rung resolves (up to 10 minutes unprotected).
E2 [Sonnet] deribit_orders.cancel_all_by_label calls private/cancel_all_by_currency (cancels every BTC order). Replace with private/cancel_by_label (label, currency) - endpoint verified in Deribit docs 2026-09-27.
E3 [Haiku or NUC worker] research/_archive/loose_2026-10/deribit_api_research.md error table is wrong: 10002 is qty_too_low, not insufficient funds; not_enough_funds is 10009; 11005 amount_too_large; 13009 unauthorized; 11006 post_only_reject; 11007 reduce_only_reject. Mark the heartbeat section unverified (method names not confirmed). Amount for BTC-PERPETUAL is USD, multiples of 10.
E4 [Sonnet] plan_compiler targets: sizes rounded up can exceed the position (valid_ladder_four_rung: 40 + 40 > 70). Floor each target to 10 and give the remainder to the last target; sum must equal position.
E5 [Sonnet] trade_plan_validator: amount is USD notional, so the check is total_units <= max_notional exactly (remove the 1.5x slack).
E6 [Sonnet] Any execution or assistant consumer selects the rank-1 candidate by rank, never setup_candidates[0] (F6), and refuses verdict SETUP_CONFIRMED (F9) until D6 lands.

PHASE G - governance (non-critical, any model, NUC-suitable)
G1 Add 03_FILE_INDEX.md rows for: execution\ (deribit_orders.py, executor.py, journal.py, reconciler.py, plan_compiler.py, trade_plan_validator.py, trade_plan_schema.json, examples\), backtest\ (six files), research\core_readiness_2026-09-27\ (this folder).
G2 Archive to MyTradingSys\archive\ (log in 02b): research\_archive\loose_2026-10\opus_handoff_context.md, operator_summary.md, SESSION_HANDOFF_2026-09-27.md, execution_system_architecture.md, OPUS_REVIEW_REQUEST.md, step6_multi_account_design_note.md (content folded into this plan). Keep deribit_api_research.md after E3.
G3 Delete the stray root file named `=====\"` (untracked, 16 KB) after a backup.
G4 BUGS.md rows (append, one per finding not already covered): F1 (link B058), F3, F5 (link B063), F6, F7, F8, F9, F10, E1, E2. Each needs an items\ doc (Build-Check enforces it); one shared doc pointing at this plan is enough per ID.

## 5. HARNESS INVENTORY (all in harness\, all read-only, stdlib Python 3.10+)

| File | Layer | Today on 2026-09-27 |
|---|---|---|
| core_invariants.py | L1 output invariants, 15 checks, baselines | PASS (full corpus and --since golden boundary) |
| verdict_golden.py + verdict_golden_baseline.csv | L2+L3 golden, transition matrix, --expect | NO CHANGE (9,160 rows) |
| module_isolation.py | doctrine check, modules never gate L2/L3 | PASS group A and B |
| proof_direction_cases.py | L2 unit cases, 15 | PASS |
| fail_closed_spec.py | B071 executable spec | FAIL by design; PASS on the reference patch |
| java\ReplayScbSteps1to8.java + run_replay.ps1 | L1 replay steps 1-8 | PASS 118/118 candidates, mutation-tested |
| _common.py | path setup | - |

Uses MyTradingSys\backtest\snapshots.py and verdict.py (existing). The golden boundary for current Tom-core code is 2026-09-24T13:51:32Z (last SetupCandidatesBuilder change; last pf_ zone candidate 13:24:11Z).

## 6. PRE-API GATE (all true before T050 phase 2 testnet orders)

1. D1-D7 ruled; C tasks for accepted decisions landed with MATCH matrices.
2. B071 closed: fail_closed_spec PASS, verdict_golden NO CHANGE, live PD_ERROR proof.
3. core_check.ps1 PASS including L1 replay (A3); A4 result recorded.
4. E1-E6 landed; Opus review of executor.py before any testnet order.
5. Governance G1-G4 done; Build-Check PASS.
T051 (backtest) stays parked; it may resume after 1-3 on the operator's word. Layer correctness above is not T051.

## 7. THE NUC BUILDER IN THIS PLAN

The NUC worker (T049) is a mechanical worker: it receives a self-contained packed task, returns .new files plus a reply, and a script verifies hidden EXPECT lines. It has no repository, no network to exchanges, no shell on the desktop.
Suitable here: A1, E3, G1, G2 listings, G4 row drafting, and continuing T049 phase 5 rule tagging (slice 1, TOM-214, is live).
Not suitable: A3/A4 (need repo, build, Binance), B1 and C tasks (critical files, judgment), decisions.
Pattern to reuse: the numeric acceptance lines in section 4 are ready to paste as EXPECT lines.

# END
