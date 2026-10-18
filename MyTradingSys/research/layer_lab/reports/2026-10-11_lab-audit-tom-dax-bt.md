BLOCKED

# Tom DAX harness readiness audit

Card: `lab-audit-tom-dax-bt`. Audit time: 2026-10-11 20:16 UTC. Surface: COD.

**The harness is not ready for the first home-market outcome run.** Eight HIGH and six MED findings are established below. The existing 29 harness tests pass, but independent synthetic probes reproduce three defects those tests miss: current Java proof-schema rejection, development outcomes consuming holdout bars, and execution on closed-market filler bars.

**Exact completion blocker:** the requested source-complete audit cannot verify the primary chart evidence. The ledger cites frames under `F:/MTS/data/tom_videos/`, outside this task's permitted workspace; LAYER_LAB.md also excludes frame reads. The available `PROFILE_PARITY.md:6-8,14-23,73-75` explicitly has no drawn prices, axis increments or verified profile anchors. Thus readiness item 5 and the frame provenance required by item 2 remain NOT_IN_DATA. The clean-split manifest is also absent in this checkout. These are missing evidence, not measured parity failures. No questions were sent, no frame or holdout data was opened, and the card was **not** marked done.

## What was checked

Paths below are relative to the repository root. Abbreviations in the tables:

- **D** = `MyTradingSys/backtest/tom_dax_bt.py`, all 703 lines.
- **P** = `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md`, all 38 lines.
- **T** = `MyTradingSys/backtest/PRE_REG_TEMPLATE.md`, all 65 lines.
- **B** = `MyTradingSys/research/tom_transfer_2026-10-11/BACKTEST_FAILURES_RESEARCH.md`, all 147 lines.
- **S** = `MyTradingSys/backtest/tom_bt.py`, all 337 lines.
- **J** = `src/main/java/datafeed/SetupCandidatesBuilder.java`, relevant source blocks 140-228, 277-350, 450-455, 568-626, 661-663, 717-727, 739-779.
- **L** = `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`, all 38 physical lines / 37 data rows. Management rows and repeated videos are not independent trades.

Additional evidence read: `fees.py:1-50`; `dax_data.py:1-128`; `verdict.py:1-144`; `test_tom_dax_bt.py:1-393`; `ExecutionMathConstants.java:1-47`; `MarketDataSnapshot.java:717-769`; `runtime/math_object_builder.py:445-469`; `backtest/layers/FORMULAS.md:400-406`; `system/net_rr_floor.json`; complete ROADMAP, PROBE_PLAN, RECALL_DAX, TOM_TRADE_LEDGER.md and PROFILE_PARITY.md in the Tom transfer folder; `TOM_CORE_BT_REVIEW_2026-09-30.md`; relevant DIAG_BTC text; and existing `tom-holdout-clean-split`, `tom-encode-spike-fade`, `tom-layer-v2-cost` cards.

Trader text checked in `raw_transcripts_canonical/`: `T6hDJcHrVBM_raw.txt:13`, `zQTbdEweG3c_raw.txt:19`, `n7ZSkjb7JXs_raw.txt:19`, `ujedEcmvBMk_raw.txt:13`, `UOBgXV20yCM_raw.txt:7`, `l8RZrBfzvp4_raw.txt:13`, and relevant excerpts of `k0zm5NYn0IQ_raw.txt:19`. These canonical files place the transcript body on one long physical line. Text establishes qualitative method/management, not verified chart prices or trade dates. `TOM_VERBATIM_INDEX.md:1-25` was checked as an index, not substituted for the transcripts.

Source-coverage limit: this is a completed inspection of the four scope files with a **partial source audit**. Primary frames, the external bibliography at B:140-147, and all the other traders' result/source chains at B:36-73 have not been independently verified. Those cross-layer and literature conclusions are not endorsed by this report. No new market result, recall score, frequency estimate, or claim that a holdout has actually been consumed is made here. The reference pack was read as context only.

Commands: numbered `Get-Content` reads and `Select-String` source searches; workspace-only `Path.rglob` inventory; the isolated unittest command and synthetic Python probes reproduced below. `rg` was unavailable, so searches used those alternatives. No harness `gen`, `rows`, `report` or `all` command was run. No git command was run. No empirical backtest trial was performed; TRIALS.md was not changed.

## Twelve-item readiness assessment

The template's twelve headings MATCH B:115-126. Its TODO slots are intentional template fields; the defect is that the DAX pre-registration has not supplied the required answers and evidence. No item is fully demonstrated ready for a new v2 outcome run.

| Item | Status against read evidence | Check and implication |
|---|---|---|
| 1. Source home | NOT_ANSWERED; partial MATCH | P:3,9 identifies FDAX versus CFD. The transcript T6hDJcHrVBM:13 describes the cash session and open; n7ZSkjb7JXs:19 describes pre-market and a 5-minute chart. P:11 specifies a 15-minute sampling cadence without a quoted home timeframe, session or holding-period contract. See M3. |
| 2. Ground truth / split | NOT_ANSWERED / NOT_IN_DATA | L exists, but exact entry minutes are missing or approximate in L:2,10-14,21,29,32,34. No design/check lists occur in P:1-38; workspace inventory found no HOLDOUT_CLEAN.json. Existing clean-split card remains ready with an empty result. See H2, H7, M2. |
| 3. Check recall AND fire rate | NOT_ANSWERED; MISMATCH | RECALL_DAX:3-7 reports the old 0/7 and stops the current encoding. No v2 CHECK result or daily fire-rate criterion is supplied by P. D:488-593 can simulate without these prerequisites. See H7. |
| 4. Input availability | MISMATCH | P:9-10 acknowledges absent aggressor data, but half-volume fabrication becomes negative delta labels in Java. Current counted-proof parity also fails. See H1, H6. Real exchange-volume parity is unestablished, not zero. |
| 5. Profile/snapshot parity | NOT_IN_DATA | PROFILE_PARITY:6-23,73-75 contains six computed candidates but no drawn-level comparison. P has no parity evidence or gate. See H7. |
| 6. Instrument economics | Partial MATCH / MISMATCH | FEES_FDAX is actually used for outcome legs (D:517), but the primary verdict erases those fees (H5); P's point-equivalent claim is inconsistent (M4). Stop/noise and fee-share readiness are unanswered. |
| 7. Fills | MISMATCH | S:186,218 uses touch for entry/target; no passive-side check or trade-through arm is called by D:470-472,525-555. Synthetic bars can execute trades. See M1, H4. |
| 8. Management | NOT_ANSWERED; model mismatch established | S:12-17,237-238 fixes order life and hold to eight zone-TF bars. P:14-16 imports this without a sourced management contract or explicit interpretation limit. Actual partial/re-entry/stop management is present in the transcripts and L. See M3. |
| 9. Like-for-like null | MISMATCH | D:220-255 draws across a UTC day, enters at next-bar open, and starts from filled real trades. No sourced session matching or original limit-order attrition. N7 remains unfixed. See H3. |
| 10. Power | NOT_ANSWERED; partial MATCH | P:27-28 and D:461-467 correctly refuse a pass below 100 resolved fills, but no expected N per period is computed before running. See M5. |
| 11. Holdout and trials | MISMATCH | N1 embargo/forward split missing; signal-time filtering does not isolate outcome bars. Same-date trial dedupe loses new looks; cached rows are not bound to run inputs. See H2, H8. |
| 12. Regime/session readout | NOT_ANSWERED / MISMATCH | D:484-560 groups by market, verdict, shift, variant and period only. S has regime helpers, but this driver never calls them and the pre-registration defines no strata. See M5. |

N1: **not implemented in the audited spec/runner**. N2: **present in future task-card requirements, not demonstrated or enforced here**. N7: **not implemented**. Cards describing future work are not completion evidence.

## Findings

| ID / severity | File:line | What is wrong | Evidence and claim classification | Proposed fix |
|---|---|---|---|---|
| H1 HIGH | D:79-96,153-156,627-631 | Python's purported Java proof-count mirror is stale and rejects valid current Java output. The printed two-proof ceiling is stale too. | **MISMATCH:** J:579 explicitly excludes volume_spike (B144), while D:92-93 adds it. J:615-616 still emits its detected flag. A candidate with only a detected volume spike has Java count 0; the probe returns Python count 1 and `rescore` raises `proof JSON gives 1, score.proof_count is 0 (vwap)`. With the four order-flow proofs removed, the current legacy counter has only rejection_wick left: ceiling 1, not 2. Existing test:205-220 asserts the obsolete six-to-two count. | Align the adapter with the frozen current Java schema, add a test whose expectation comes from the actual Java counter, refresh ceiling/deviation text, invalidate incompatible snapshots/rows. Do not restore the unsourced volume-spike proof or compensate by tuning shifts. |
| H2 HIGH | P:25-26; D:62-64,268-283,495,520-528,584-592,659-660 | The holdout is neither cleaned of design exposure nor isolated from development outcome evaluation. Forward-holdout handling is absent. | **MISMATCH:** B:78-87 requires clean dates and a design/check split. L:10-14,29,32-35 contains ledger exposure inside the old window, including management/outcome information. D loads the entire bar archive, filters only signal timestamps, then gives the full bars to the simulator. Synthetic signal at cutoff minus 60 seconds is selected as dev and exits on a holdout bar. `DAX_END` is still 2026-10-09; `dax_period` has no upper bound or embargo handling. A pre-existing non-SMOKE report, even partial, is enough for the read guard. `holdout_rows` is initialized to 0 and never incremented. | Consume the clean-split manifest from the existing owner card, embargo uncertain ledger exposure conservatively, pre-register forward boundaries, and isolate outcome bars as well as signals before any development read. Freeze handling of boundary-crossing orders. Enforce full-dev readiness, make read reservation durable before outcome evaluation, and record truthful counts. No actual holdout read is needed to test this. |
| H3 HIGH | D:220-255; P:22 | Null mechanics still fail N7 and the existing H2 method review. | **MISMATCH:** UTC day is the sampling stratum (`t // 86400`), not an exchange-local session. Only filled/resolved strategy trades enter the null; `e = b.o[k+1]`, entry at e, and fill_window=1 give immediate executable entries under valid OHLC. Strategy entries instead wait up to eight TF bars, can run away or expire, and use one-at-a-time scheduling (S:225-244). The null does not apply that schedule. B:106-108 and TOM_CORE_BT_REVIEW H2 require like-for-like mechanics. | Use the frozen session window/timezone, preserve passive entry offset, side, geometry, order lifetime, ran/no-fill rules, fill model and position scheduling over the original opportunities. Report the opportunity and fill counts. Preserve a reproducible random seed and draw accounting. |
| H4 HIGH | P:14-16; D:204-210,470-472; S:184-221 | The DAX real-bar mask is ignored by the execution simulator. Filler bars can create impossible entries and timeout exits. | **MISMATCH:** the two-minute open filter may retain a snapshot just after the last real bar; it does not make future bars executable. Synthetic `real=[1,0,1]` fills at index 1 with `real[1]=0`. Another fixture fills at index 0 then times out at index 1, also closed, avoiding the next real bar's gap through the stop. The existing reopening-stop test covers only a reopen before expiry. | Keep clocks and executable prices distinct. Never fill/exit on a synthetic minute; freeze what a timeout during closure means and execute it at an eligible real price. Distinguish missing download data from scheduled closures and reject incomplete coverage. Test long/short, pending orders, closed expiry and reopening gaps. |
| H5 HIGH | P:20-21; D:176-181,197-199,621-623 | The primary arm called DAX-fee is actually a gross-RR eligibility gate and is stale after the per-market Java fix. | **MISMATCH:** J:158 calls `netRR(sym,...)`; ExecutionMathConstants:23-37 already applies 0.000005 per side to GER40. D then overwrites that fee-aware value with gross_rr. This admits marginal candidates the real fee gate rejects. Using FORMULAS:403-404 with entry=100, stop=99, target=101.25 gives cost=.001 and netRR=1.249/1.001=1.247752..., below the current 1.25 floor; grossRR=1.25 passes. Outcome fees are still charged, so this is a selection defect, not a claim that simulated P&L has no fees. | Use the frozen per-instrument netRR as primary. Keep gross-only selection, if retained at all, explicitly labelled as an experimental arm. Preserve the historical pre-registration and append the reviewed current contract. Freeze the fee/floor inputs with the run. |
| H6 HIGH | P:9-10; D:115-126,644-646 | Missing aggressor information becomes a directional contradiction against longs. Clearing four proof flags does not remove that downstream use. | **MISMATCH:** dax_data:100-106 writes buy volume as exactly half total volume. MarketDataSnapshot:752-755 classifies zero as `negative`. runtime/math_object_builder:467-469 interprets three such labels as contradiction for LONG; verdict:127-128 caps SETUP_FORMING to WATCH. D's mask never clears `cvd.last_3_delta`. This is a latent asymmetric gate when an arm/new encoding reaches sufficient proof, even though the unshifted legacy rule currently cannot trade. | Carry explicit unavailable order-flow status through the adapter and all consuming gates; do not fabricate bearish or bullish evidence. Test mirror long/short candidates with absent aggressor data. Keep any shared-engine behavior change isolated from live BTC as required by the build card. |
| H7 HIGH | P:1-38; D:488-593,677-698 | No readiness gate prevents a P&L report before v2 check recall, fire rate, source fit and parity exist. | **NOT_IN_DATA / MISMATCH:** T:4-5 says every unanswered item prevents a run. PROFILE_PARITY:6-23 is explicitly unverified; the old RECALL_DAX result is 0/7 and its T2/T3 source values were later corrected in the ledger. `build_report` does not consult any readiness evidence. Existing task cards request these outputs but have no result in the inspected clean-split/cost/encode cards. `report --market dax` also does not constrain build_report's DAX/BTC loop at D:508-512; existing BTC cache triggers a BTC simulation despite the requested market. | Require a frozen completed readiness manifest before outcome reads, including one-time CHECK recall plus fire rate, usable inputs/parity or an explicitly authorized price-only scope, source home/management, costs, power and strata. Enforce selected market so a DAX-only invocation cannot run the parked BTC encoding. Reuse the existing research/encode owners; do not invent missing trader rules. |
| H8 HIGH | P:7-8,38; D:374-375,393,595,603-605,661-673 | Cached rows and trial identity are not tied to frozen inputs; new looks can disappear from the trial count or be reported under the wrong code. | **MISMATCH:** any existing monthly rows file is reused by filename alone, regardless of mask, shifts, engine, verdict or floor. Row metadata contains counters, not source/config identities. Report hashes describe current files, not necessarily the files that created the snapshots/rows. `run_id` is date plus smoke/holdout suffix; any matching row suppresses all later additions that day, even a new shift arm or code change. The verdict reads the mutable floor each call (verdict:66-70), which the report's hash list omits. B:87,125 requires every recall/design look and extension to count. | Use an immutable run manifest binding data/snapshot/cache hashes, engine/adapter/config versions, market, split, arms and seeds. Invalidate mismatched caches. Give each new experiment/look an identity; only identical rerendering should be idempotent. Register recall attempts through the same accounting contract. |
| M1 MED | P:14; D:470-472,525-555; S:179-190,218-219 | Touch-only fills and missing passive-side validation leave item 7 incomplete. | **MISMATCH:** S checks stop/target geometry but never compares a submitted limit with signal-time market price. Entry and target use inclusive touch comparisons. D adds slippage stress only; no trade-through arm is present. T:37 and the earlier method review M1/M2 require both fill views and passivity. | Freeze a tick-aware trade-through model alongside touch and validate passive order geometry at submission; match both models in H3's null. Label marketable orders honestly if intentionally allowed. |
| M2 MED | B:37,41,79-80; P:26 | Source summaries treat superseded or uncertain ledger facts as established ground truth. | **MISMATCH:** L:3 corrects T2 entry 25343 to 25318; L:10 and TOM_TRADE_LEDGER.md:51 correct T3 initial stop 24257 to 24265. L:29 calls 2026-06-08 a recording date with the trade day unlabelled, so B:79-80 cannot use it as an exact confirmed trading day. L:11 retains `reentry_after_stop` while L:27,38 says `reentry_after_partial`. ujedEcmvBMk:13 verbally mentions a stop-out, but the cited frame recap says its fill is not shown. T4/T9 and T6/T10 also reuse video/geometry with uncertain dating (L:12,14,21,29). | Reconcile identity/date/entry/management confidence before splitting or quoting recall. Separate stated, frame-observed and inferred events; group same trade/day/video to prevent cross-split duplicates. Never convert a recording clock into a trade minute. Coordinate with the ledger owner; no ledger edits made here. |
| M3 MED | P:11,14-16; B:41,122; S:12-17,237-238 | Home timeframe/holding/session provenance and the exit-model interpretation are missing from the DAX contract. | **MISMATCH / NOT_ANSWERED:** PROBE_PLAN:54-55 explicitly calls the eight-bar timeout unsourced. T6hDJcHrVBM:13 says, "Take out one position here and the rest stays in." k0zm5NYn0IQ:19 describes logical stop moves and another position after a stop; UOBgXV20yCM:7 describes predefined limit targets. These do not establish eight bars or one fixed management policy. Fifteen-minute snapshots are an engineering cadence, not sourced home timeframe. | Complete items 1 and 8 with exact qualitative quotes and separate protocol choices from trader parameters. Explicitly limit interpretation of the fixed bracket; take sourced family-specific management from the v2 spec before claiming to test Tom's method. Do not tune a timeout. |
| M4 MED | P:17-18; D:553-560; fees.py:30,43-49 | Fee arithmetic and economic readiness are incomplete. | **MISMATCH:** EUR2.5/EUR25 per point=.1 point round trip, but 2 x .000005 x 24000=.24 points (EUR6), 2.4x the stated approximation. fees.py:43-47 already discloses this and says EUR2.5 was not a fetched fee schedule; P does not. D reports percent stop width, not noise units or fee-share distributions against item 6. P uses BID CFD data with futures fees; no basis/spread execution equivalence is demonstrated. | State the actual model and approximation openly; source the intended instrument's fees/data mapping. Add the pre-registered noise and fee-share diagnostics and their interpretation. Do not turn an approximate fee estimate into an asserted current broker schedule. |
| M5 MED | P:27-28; D:461-467,484-560 | Threshold-based power labeling is not pre-run power planning, and pooled results omit regime/session readouts. | **MATCH:** below 100 fills returns insufficient N. **MISMATCH:** no expected N per period, fixed session/regime definitions or corresponding tables appear in P or D's report builder. Merely having S:253-278 regime helpers does not make them part of the readout. | Estimate N from permitted development opportunities before the outcome run, declare underpowered periods, freeze strata with past-only definitions, and show stratified results beside pooled results without selecting a winning cell. |
| M6 MED | D:532,546; S:304-310,321-335 | The pass decision uses an iid per-trade bootstrap without addressing repeated intraday dependence. | **MATCH to the earlier warning / unresolved:** TOM_CORE_BT_REVIEW M6/M7 documents clustered episodes and an iid CI. S still resamples individual trades; `_key` at S:137-138 still includes changing zone price. Thus positive lower CI is not yet demonstrated to have the intended coverage. No actual CI widening is estimated here. | Pre-register an appropriate session/day-block uncertainty method and sensitivity, count effective independent units, and carry it into the pass decision. Do not declare a future pass from an iid CI alone without justifying independence. |

## Verification and numerical probes

**Existing tests:** command below ran 29 tests in 0.050 seconds, all OK. Temporary files were confined to the lab directory. This verifies the current test suite, not the missing readiness criteria; notably its proof fixtures encode the obsolete counter.

```powershell
python -B -c "import sys,tempfile,unittest; from pathlib import Path; p=Path('MyTradingSys/research/layer_lab'); p.mkdir(parents=True,exist_ok=True); tempfile.tempdir=str(p.resolve()); sys.path.insert(0,'MyTradingSys/backtest'); suite=unittest.defaultTestLoader.loadTestsFromName('test_tom_dax_bt'); result=unittest.TextTestRunner(verbosity=1).run(suite); sys.exit(not result.wasSuccessful())"
```

**Independent probes:** the following Python statements were executed in a `python -B -c` command. They import functions only and create in-memory fixtures; they never call an archive loader, report builder, git helper or market runner. Dates on synthetic bars are boundary labels, not historical observations.

```python
import sys
sys.path.insert(0, 'MyTradingSys/backtest')
import tom_dax_bt as D
T = D.T
c = {
    'rank': 1, 'direction': 'short',
    'zone': {'name': 'vwap', 'type': 'vwap'},
    'proof': {
        'rejection_wick': 'NONE', 'absorption': {'detected': False},
        'finished_auction': {'detected': False, 'direction': ''},
        'delta_flip': {'detected': False},
        'volume_spike': {'detected': True}, 'cvd_aligned': False},
    'score': {'proof_count': 0, 'raw': 50, 'confluence_bonus': 0}}
print(D.java_count(c))
try:
    D.rescore({'setup_candidates': [c]})
except ValueError as e:
    print(e)
b = T.Bars1m(int((D.T_DAX_HOLD-60)*1000),
             [100.,100.,100.], [100.,102.,100.], [100.,100.,100.],
             [100.,101.,100.], [1.]*3, [.5]*3, bytearray([1,1,1]))
r = {'t': D.T_DAX_HOLD-60, 'verdict': 'SETUP_FORMING',
     'setup': 'ct_long', 'dir': 'long', 'zone': 'vwap', 'ztype': 'vwap',
     'zprice': 100., 'stop': 99., 'target': 101.}
tr = D.simulate('dax', D.select_rows([r], False), b, 'A', D.FEES_FDAX)
print([(D.dax_period(t['t']), t['reason'],
        D.dax_period((b.t0+60000*t['exit_i'])/1000)) for t in tr])
b2 = T.Bars1m(0, [100.,100.,98.], [100.,100.,98.], [100.,100.,98.],
              [100.,100.,98.], [1.,0.,1.], [.5,0.,.5], bytearray([1,0,1]))
print(T.sim_limit_trade(b2, 1, 'long', 100., 99., 102., 1, 1, D.FEES_FDAX))
print(T.sim_limit_trade(b2, 0, 'long', 100., 99., 102., 1, 1, D.FEES_FDAX))
print(2*24000*D.FEES_FDAX['entry'])
```

EXPECT from source/market semantics: Java-count mirror 0; no dev outcome should consume a holdout bar; no execution on `real=0`; frozen fee arithmetic .24 points at 24000.

RESULT: count 1; ValueError with the H1 message; `[('dev', 'target', 'holdout')]`; closed entry `fill_i=1`, later stop `exit_i=2`, gross -2R; closed timeout `fill_i=0, exit_i=1`, gross 0R; fee points `0.24000000000000002`. These reproduce defects in the unchanged code; they are not successful readiness assertions and are not strategy-performance trials.

Further source matches: D's timeframe rank table agrees with the inspected J zone ranks; score formula is still `min(95,50+7*count+bonus)` in J:182-185; absorption genuinely depends on signed delta (J:723), justifying its exclusion on this feed. P's four variant names, 15-minute cadence, two-minute freshness window, period start and 200 null draws are implemented. Seed 7, minimum null sample 30, eight-bar lifetime, 2000 iid bootstrap draws/seed 12345 and extension shifts are protocol/implementation choices, not established Tom quotations. P does not freeze all of them or justify their interpretation. These matches do not cure the findings.

## Follow-up cards created

Each card was created with `python -B scripts/dev/tasks.py new "<title>" --lane SONNET --prio 1 --id <id>` and has a source link to this report's exact finding. They remain raw for refinement, not marked ready or authorized to run a backtest.

| Finding | Card ID |
|---|---|
| H1 | `lab-dax-proof-parity` |
| H2 | `lab-dax-holdout-boundaries` |
| H3 | `lab-dax-session-null` |
| H4 | `lab-dax-closed-executions` |
| H5 | `lab-dax-net-fee-verdict` |
| H6 | `lab-dax-unavailable-flow` |
| H7 | `lab-dax-readiness-gate` |
| H8 | `lab-dax-trial-identity` |

H2 coordinates with `tom-holdout-clean-split` for the manifest; H3/H6/H7 use `tom-layer-v2-cost` and `tom-encode-spike-fade` decisions; H7 consumes `tom-profile-parity-check`. The missing frame comparison already has desk request `20261011-192710-tom-profile-parity-read-drawn-levels-and` in PROFILE_PARITY:73; no duplicate external message was sent.

## Scope preservation

Persistent new content is limited to this report and the eight new task cards. `python -B scripts/dev/codex_run.py index` regenerated the lab index with the audit still queued, not delivered. `python -B scripts/dev/tasks.py lint` passed: 57 cards OK. Product code, pre-registration, template, research spec, ledger, holdout markers and trial registries were not edited. Audit-file SHA-256 at inspection (also checked at completion):

| File | SHA-256 |
|---|---|
| D | `1ba261ccfcfbeb4e930af79629849f88178a15717082c5298cbe5bb3a18e1386` |
| P | `4caea4eda1bf1288e5ca200fad89e82d0c64307f65acb735fd88451baae65942` |
| T | `2e790bab7de5ae67bd18092b0fe042049e489396127d107371cafb69ed5f880a` |
| B | `0214c962c5a1dacc2c92abe389d8d58cb017fee0da8de2025ba4506635c9ece6` |

The runner retains responsibility for shipping/releasing. `tasks.py done lab-audit-tom-dax-bt` was deliberately not invoked because mandatory source verification is blocked as stated above.

## H5 current-contract addendum (2026-10-12, lab-dax-net-fee-verdict)

MATCH: the primary arm is now `coded`, preserving the Java per-instrument `math.net_rr` through proof masking and the Python verdict. GER40 uses 0.000005 per side (ExecutionMathConstants.java:23-37); entry 100, stop 99, target 101.25 gives net RR 1.249/1.001 = 1.247752247752, below the current 1.25 floor. Gross-only `daxfee` selection is removed. This supersedes the selection contract in the historical PRE_REG_DAX.md:20-21 without editing that dated document.

The row-cache schema is advanced to refuse pre-fix rows. Each regenerated month's metadata records its frozen verdict floor, FDAX fee and execution-math hash. Complete snapshot/run provenance remains H8's separate task; this addendum does not establish readiness for an outcome run or resolve other audit findings.

RESULT (2026-10-12, COD lab): the synthetic H5 regression failed before the fix (`SETUP_FORMING` instead of `WAIT_RR`), passed after, and all 40 harness tests passed. Evidence, commands and changed-file lines: `2026-10-12_lab-dax-net-fee-verdict.md`. No market-data backtest or recall was run.

## H3 session-null addendum (2026-10-12, lab-dax-session-null)

MATCH: the DAX null now takes original variant opportunities before scheduling and outcome selection. An explicit frozen session addendum supplies `timezone`, `start`, `end` and `source` (trader quote + file:line), via `--null-session`. Reports refuse a missing/invalid session before coverage or outcome reads. No production session hours were supplied or inferred by this build. Synthetic fixture hours are test inputs only.

MATCH: each opportunity is sampled uniformly among real minutes of its exchange-local session, including overnight windows and seasonal timezone offsets. Entry/current-open, stop/entry and target/entry ratios preserve the passive offset, side and geometry without next-bar-open entry. Marketable source entries are rejected. Strategy and null share the real-bar touch simulator and one-at-a-time scheduler; both retain the existing eight-zone-TF-bar pending/holding clocks and ran/no-fill rules. Entry submissions and fills stay inside the supplied session; existing positions can exit outside it. Unresolved orders remain busy through available coverage and produce no resolved return. Eight bars remain an inherited protocol choice whose trader provenance is unresolved under M3, with no tuning here.

MATCH: the report prints original/session-eligible opportunity counts, real submission/fill counts, and every draw's sampled, submitted, busy-skipped, filled, resolved, expired, ran and unresolved counts. Requested/nonempty/empty draws and seed 7 are explicit; default draws remain 200. The p-value is unavailable below 30 real resolved fills or without a nonempty null draw, while accounting is still reported.

RESULT (2026-10-12, COD lab): the H3 tests failed before the fix (30 one-minute fill windows instead of 40; session argument unsupported), then passed after. Six session-null tests and all 53 harness tests pass. Full commands, changed-file references and red/green output: `2026-10-12_lab-dax-session-null.md`. Only synthetic fixtures were evaluated; PRE_REG_DAX.md and shared/live files were unchanged. The sourced production session addendum remains the owner's input, not a claim of scientific readiness.

## H2 enforcement addendum (2026-10-12, lab-dax-holdout-boundaries)

MATCH: reports now require `--split-manifest <path>` with UTC `design_end_utc`, UTC `holdout_start_utc`, and finite nonnegative `embargo_s`. The latest design exposure plus embargo must precede or equal the holdout start, with design exposure strictly before it. The manifest owner chooses the clean dates; this change does not certify ledger cleanliness or invent those dates. Development signals precede `holdout_start_utc - embargo_s`; only complete minute bars ending at or before that cutoff enter development price arrays. Forward dates are accepted without the historical DAX_END cap on development coverage.

Strategy, slippage stress and null outcomes use isolated period bars. Pending or filled orders unresolved at the development cutoff are dropped, without a fabricated close or a holdout-priced outcome. Holdout envelope timestamps are counted once across arms; excluded holdout verdict payloads are not selected during development. An explicit holdout read requires a full-development completion token for the same split, complete monthly snapshot/cache coverage, raw-day coverage, and no snapshot errors or detected long archive holes when the token is produced. Smoke/partial reports cannot authorize it. The exclusive, fsynced read reservation records the actual envelope count before outcome-bar loading; a subsequent evaluation failure leaves that reservation in place.

RESULT (2026-10-12, COD lab): before the change, the H-60 synthetic signal filled at index 1 and exited at index 2 (H), `holdout_rows` was 0 instead of 2, and absent-manifest handling reached coverage access. After the change, both requested regression tests pass and all 47 harness tests pass, including five additional synthetic boundary/manifest/reservation guards. Full commands, line references and red/green output: `2026-10-12_lab-dax-holdout-boundaries.md`. No real-data backtest, recall or holdout outcome was read. The original PRE_REG_DAX.md remains historical; H7 scientific readiness and H8 immutable trial identity remain separate findings.

## H6 unavailable-flow addendum (2026-10-12, lab-dax-unavailable-flow)

MATCH: when `cvd_aligned` is masked, the adapter now explicitly marks snapshot CVD `UNAVAILABLE`, clears `last_3_delta`, removes placeholder numeric/recent CVD, and marks both CVD slope fields unavailable before downstream direction and verdict evaluation. The existing proof masks remain in effect. Empty-mask snapshots retain their original CVD. The row-cache schema advances to v3 so pre-fix verdicts cannot be silently reused (`tom_dax_bt.py:81,178-195`). Shared engine and live files were not edited.

RESULT (2026-10-12, COD lab): the half-volume synthetic regression failed before the fix with long `contradiction` / `WATCH` versus short `aligned` / `SETUP_FORMING`; after the fix both are `aligned` / `SETUP_FORMING`, and all 55 harness tests pass. A test-only shift of four exposes the latent five-proof verdict cap; it is not a production parameter change or a readiness claim. Commands, changed-file references and red/green output: `2026-10-12_lab-dax-unavailable-flow.md`. No real-data backtest, recall or holdout read was performed.

## H7 readiness enforcement addendum (2026-10-12, lab-dax-readiness-gate)

MATCH: `build_report` now requires an explicit `--readiness-manifest` JSON before split/session loading, archive coverage, simulation or holdout reservation. `items` must cover the numbered PRE_REG_TEMPLATE headings `1` through `12` exactly. Each item needs `ANSWERED` or `WAIVED`, a non-placeholder answer and evidence; a waiver additionally needs a named approver. The parsed declaration is frozen in memory and its exact-byte SHA-256, answers, evidence and approvers are printed in the report. This checks completeness, not scientific evidence validity, and supplies no production answers or waivers (`tom_dax_bt.py:411-445,828-831,993-1005,1121`).

MATCH: the inspected checkout already constrained the market loop; a synthetic CLI regression now verifies `report --market dax` with a BTC cache present makes four DAX simulation calls, zero BTC simulation calls and zero BTC price reads (`tom_dax_bt.py:874`; `test_tom_dax_bt.py:968-1007`). Thus the historical H7 market-loop defect was already corrected before this card; this build adds its explicit guard.

RESULT (2026-10-12, COD lab): corrected pre-fix H7 tests produced 74 failures (data accessed before readiness) and two CLI errors (unrecognized readiness option). After the fix, all three H7 tests and all 58 harness tests pass. Full commands and red/green evidence: `2026-10-12_lab-dax-readiness-gate.md`. Real-data outcomes, recall, BTC encoding runs and holdout reads were not performed. PRE_REG_DAX.md remains unchanged; production evidence remains the existing research/encode owners' responsibility.

## H8 frozen-input identity addendum (2026-10-12, lab-dax-trial-identity)

MATCH: snapshot generation records archive hashes, Java sources, generator/config hashes, Java/javac and dependency-jar hashes, and its exact command in a producer sidecar. Row caches require that provenance and bind the snapshot and snapshot-metadata hashes, adapter/verdict/engine/config hashes, frozen floor, market, mask, kinds, shifts, cutoff and DAX price/real-bar arrays. Missing or mismatched provenance, changed row content and changed envelope identities are refused. Legacy snapshots need a fresh generation directory; legacy rows need regeneration. Development row generation now requires the owner's split and loads development bars only (`tom_dax_bt.py:606-869`).

MATCH: the run manifest freezes validated cache identities, execution data, code/config, floor, market, full split, readiness, session, arms, existing seeds/fees, smoke/holdout mode and optional `--look-id`; it is saved before simulation. Its full SHA-256 supplies the run id. New inputs or a fresh look label have a different id; identical inputs and label rerender idempotently. Trial deduplication uses `(run_id, variant)`, so an additional same-day shift arm is counted. Reports print the frozen manifest rather than attributing historical rows to today's HEAD (`tom_dax_bt.py:705-721,1019-1047,1118-1130,1162-1177,1277-1293,1308`). The helper/label provides a common identity vocabulary for future recall callers; existing recall drivers outside this card were not changed or run.

RESULT (2026-10-12, COD lab): the two requested H8 regression tests failed on the pre-change code with four failures: changed shifts, mask and floor each failed to raise, and the second arm left four registry rows instead of eight. Both tests now pass; all 62 harness tests pass. Additional synthetic guards cover snapshot/code/metadata/row-content changes, DAX real-bar changes, missing producer provenance, generation archive changes, durable pre-simulation manifests, fresh look labels and immutable-manifest tampering. Evidence and commands: `2026-10-12_lab-dax-trial-identity.md`. No real-data outcome/recall, BTC encoding run or holdout read was performed; PRE_REG_DAX.md and shared/live files remain unchanged.
