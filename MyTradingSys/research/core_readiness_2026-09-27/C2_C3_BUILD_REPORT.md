# C2 / C3 Build Report - D3 (module_candidates) and D4 (directional proof count)

Date: 2026-09-27
Scope: CORE_READINESS_PLAN.md tasks C2 (D3), C3 (D4), replays A3 and A4, plus unit
tests for the new countSignals rules. Built in a cloud bridge session against the
desktop repo at `BinanceDataFeed` (device_bash / remote-devices tool), using the
pre-installed JDK 17.0.20.1 + Maven 3.9.9 toolchain and the clean build copy at
`$HOME/build`. **Nothing in `src/`, `target/`, `pom.xml`, or `MyTradingSys/backtest/`
was written directly.** Every change is staged as a `.new` file next to its target.
No git add/commit was run.

## Files staged (`.new`, none applied)

| File | Change |
|---|---|
| `src/main/java/datafeed/MarketDataSnapshot.java.new` | C2/D3: ExtraSetupBuilder output routed to `module_candidates`, both live and historical paths |
| `src/main/java/datafeed/SetupCandidatesBuilder.java.new` | C3/D4: `countSignals()` made directional; speed no longer counted |
| `MyTradingSys/backtest/verdict.py.new` | C2/D3 guard: `top` = first candidate with `rank <= 3`, built on top of the **current working-tree file** (which already carries the uncommitted C1 edits - suspend_rr removal) |
| `pom.xml.new` | Adds `junit-jupiter` (test scope) + `maven-surefire-plugin`, needed because the project currently has no test setup (plan F4 / T037) |
| `src/test/java/datafeed/CountSignalsD4Test.java.new` | New unit tests for the C3 directional rules (14 tests) |

## Diffs

### `src/main/java/datafeed/MarketDataSnapshot.java` (`diff -u live new`)

Both the live-path block (~line 431) and the historical-path block (~line 1200) get
the identical two-line change: stop merging `extraCandidates` into `setupCandidates`,
and write them to a new `module_candidates` field instead. Line endings (CRLF) of the
original file are preserved exactly; this is the whole diff, applied twice:

```diff
--- src/main/java/datafeed/MarketDataSnapshot.java
+++ src/main/java/datafeed/MarketDataSnapshot.java.new
@@ -431,7 +431,6 @@
         // --- Setup Candidates (v1.3.0) ---
         ArrayNode setupCandidates = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m);
         ArrayNode extraCandidates = ExtraSetupBuilder.build(mapper, root, mtf, klines1m);
-        for (JsonNode extra : extraCandidates) setupCandidates.add(extra);
         double clusterAbovePrice = liquidationClusters.get("nearest_above").get("price").asDouble();
         double clusterBelowPrice = liquidationClusters.get("nearest_below").get("price").asDouble();
         boolean warning = false;
@@ -443,6 +442,7 @@
         }
         ((com.fasterxml.jackson.databind.node.ObjectNode)liquidationClusters).put("warning", warning);
         root.set("setup_candidates", setupCandidates);
+        root.set("module_candidates", extraCandidates);
         root.set("liquidation_clusters", liquidationClusters);
         root.set("setup_candidates", setupCandidates);
         return root;
@@ -1200,7 +1200,6 @@
         // ── Setup Candidates ──
         ArrayNode setupCandidates = SetupCandidatesBuilder.build(mapper, root, mtf, klines1m);
         ArrayNode extraCandidates = ExtraSetupBuilder.build(mapper, root, mtf, klines1m);
-        for (JsonNode extra : extraCandidates) setupCandidates.add(extra);
         double clusterAbovePrice = liquidationClusters.get("nearest_above").get("price").asDouble();
         double clusterBelowPrice = liquidationClusters.get("nearest_below").get("price").asDouble();
         boolean warning = false;
@@ -1212,6 +1211,7 @@
         }
         ((com.fasterxml.jackson.databind.node.ObjectNode)liquidationClusters).put("warning", warning);
         root.set("setup_candidates", setupCandidates);
+        root.set("module_candidates", extraCandidates);
         root.set("liquidation_clusters", liquidationClusters);
         root.set("setup_candidates", setupCandidates);
         return root;
```

Note: `setup_candidates` is still (redundantly) `root.set` twice in the original code
right after `liquidation_clusters` - left as-is per the minimal-diff rule; not touched.

### `src/main/java/datafeed/SetupCandidatesBuilder.java` (`diff -u live new`)

```diff
--- src/main/java/datafeed/SetupCandidatesBuilder.java
+++ src/main/java/datafeed/SetupCandidatesBuilder.java.new
@@ -204,7 +204,7 @@
         // Step 9: Proof detection using klines1m
         for (Candidate c : candidates) {
             ProofResult proofs = detectProofs(c, klines1m, currentPrice, root, filteredZones);
-            c.proofCount = proofs.countSignals();
+            c.proofCount = proofs.countSignals(c.direction);
             c.proofNode = proofs.toJson(mapper);
         }
 
@@ -544,16 +544,26 @@
         double volumeSpikeProximityPct = 0.0;
         double volumeSpikeActualLevel = 0.0;
 
-        int countSignals() {
+        int countSignals(String direction) {
             int count = 0;
             if (!"NONE".equals(rejectionWick)) count++;
             if (absorptionDetected) count++;
-            if (finishedAuctionDetected) count++;
+            if (finishedAuctionDetected) {
+                // D4: count only when the exhausted side is opposite the trade direction
+                // (long favours a finished sell-side auction; short favours a finished buy-side auction).
+                boolean favoursTrade = "long".equals(direction) ? "sell".equals(finishedAuctionDirection) : "buy".equals(finishedAuctionDirection);
+                if (favoursTrade) count++;
+            }
             if (deltaFlipDetected && deltaFlipAtZone) count++;
             if (volumeSpikeDetected && volumeSpikeAtLevel) count++;
-            if (speedPickingUp) count++;
+            // D4: speed proxy no longer counted toward proof (still emitted in the proof JSON).
             if (cvdAligned) count++;
-            if (bookImbalance != 0.0 && (bookImbalance < 0.67 || bookImbalance > 1.5)) count++;
+            if (bookImbalance != 0.0) {
+                // D4: count book imbalance only when it favours the trade direction
+                // (long: bid-heavy > 1.5; short: ask-heavy < 0.67).
+                boolean favoursTrade = "long".equals(direction) ? bookImbalance > 1.5 : bookImbalance < 0.67;
+                if (favoursTrade) count++;
+            }
             return count;
         }
```

`bookImbalance` is `order_book_depth.bid_ask_ratio` (bid-heavy = high ratio = favours
long); `finishedAuctionDirection` is `"sell"`/`"buy"` for the exhausted side (a
finished sell-side auction favours a long reversal). `speed` fields are untouched in
`toJson()`, so `proof.speed.*` is still emitted for observability - only its
contribution to the count is removed.

### `MyTradingSys/backtest/verdict.py` (`diff -u live new`, live file already has C1)

```diff
--- MyTradingSys/backtest/verdict.py
+++ MyTradingSys/backtest/verdict.py.new
@@ -66,10 +66,19 @@
     price = _d(snap.get("current_price"))
     cond = snap.get("conditions") or {}
     cands = snap.get("setup_candidates") or []
-    if len(cands) == 0 or cands[0] is None:
+    # D3 guard (CORE_READINESS_PLAN.md, operator ruling 2026-09-27, task C2): the
+    # Java-side fix moves ExtraSetupBuilder output to module_candidates, but this
+    # guard also protects against any archived/older snapshot where setup_candidates
+    # still mixes SetupCandidatesBuilder ranks 1-3 with ExtraSetupBuilder extras
+    # (rank 11+) - top must always be the first candidate with rank <= 3.
+    top = None
+    for c in cands:
+        if c is not None and int(c.get("rank") or 999) <= 3:
+            top = c
+            break
+    if top is None:
         return dict(verdict="NO_TRADE", reason="no candidates", top=None,
                     mode="normal", direction="", price=price, net_rr=0.0, proof=0)
-    top = cands[0]
     m = top.get("math") or {}
```

Confirmed the current working-tree `verdict.py` already has the C1 edits (suspend_rr
removed, `VALID_PD`/`proof_dir_of` from B1) before this guard was layered on top of
it - `verdict.py.new` = current file + this one hunk, nothing else touched.

### `pom.xml` (`diff -u live new`, BOM preserved)

```diff
--- pom.xml
+++ pom.xml.new
@@ -37,11 +37,22 @@
             <artifactId>slf4j-nop</artifactId>
             <version>2.0.9</version>
         </dependency>
+        <dependency>
+            <groupId>org.junit.jupiter</groupId>
+            <artifactId>junit-jupiter</artifactId>
+            <version>5.10.2</version>
+            <scope>test</scope>
+        </dependency>
     </dependencies>
 
     <build>
         <plugins>
             <plugin>
+                <groupId>org.apache.maven.plugins</groupId>
+                <artifactId>maven-surefire-plugin</artifactId>
+                <version>3.2.5</version>
+            </plugin>
+            <plugin>
                 <groupId>org.codehaus.mojo</groupId>
                 <artifactId>exec-maven-plugin</artifactId>
                 <version>3.1.0</version>
```

### `src/test/java/datafeed/CountSignalsD4Test.java.new` (new file)

14 JUnit 5 tests exercising `ProofResult.countSignals(direction)` directly via
reflection (it is a private nested class with no public accessor - same
reflection-based verification style already used in this project's
`scripts/tools/VerifyScbEdits.java`, cited in plan finding F4, rather than widening
visibility just for testability). Covers: book-imbalance favour/against for both
directions, finished-auction favour/against for both directions, speed never counted
in either direction, unaffected signals (rejection wick, CVD) still count in both
directions, and a combined multi-signal sum. Full file staged at
`src/test/java/datafeed/CountSignalsD4Test.java.new`; requires `pom.xml.new` (adds
junit-jupiter + surefire) and the `src/test/java/datafeed/` directory to be created.

Build/test proof (run against a scratch copy with all four `.new` files applied,
never in the repo's own `target/`):

```
mvn -q -B compile   -> exit 0
mvn -q -B test      -> exit 0
target/surefire-reports/datafeed.CountSignalsD4Test.txt:
  Tests run: 14, Failures: 0, Errors: 0, Skipped: 0
```

## A3 - replay steps 1-8, unmodified source (baseline)

Ran the harness's own file-selection rule (`runtime_data/snapshots/BTCUSDT_*.json`
whose trailing epoch-ms filename component is `>= 1790257892000`, i.e.
2026-09-24T13:51:32Z, the documented golden boundary) against the reference
`ReplayScbSteps1to8.java`, built in a throwaway copy (`MAX_CANDIDATES` raised to 999),
never touching `src/` or `target/`:

```
snapshots=1332 archived_scb_candidates=2149 found_in_replay=2149 missing=0
field_checks ok=30086 bad=0 bad_by_field={}
RESULT: PASS
```

The corpus has grown since the harness README's cloud-sandbox verification
(49 snapshots -> 118/118 candidates, 1652/1652 fields); this run covers the full
current since-golden-boundary set (1332 snapshots) with the same 100% match rate.

**Mutation check** (proves the harness can actually fail): changed
`c.netRR = c.grossRR * 0.75;` to `* 0.70;` in the throwaway copy only:

```
field_checks ok=27672 bad=2414 bad_by_field={math.net_rr=2149, math.net_rr_sanity=265}
RESULT: FAIL
```

## A3 - replay steps 1-8, MODIFIED source (after C2 + C3)

Same 1332-file list, same harness, built against the `.new`-equivalent
`SetupCandidatesBuilder.java` (C3 change) - `ReplayScbSteps1to8.java` never exercises
step 9 (proof detection), so C2's `MarketDataSnapshot.java` change is out of scope for
this replay by design (it doesn't touch `SetupCandidatesBuilder`/`ExtraSetupBuilder`
inputs at all):

```
snapshots=1332 archived_scb_candidates=2149 found_in_replay=2149 missing=0
field_checks ok=30086 bad=0 bad_by_field={}
RESULT: PASS
```

Output is **byte-for-byte identical** to the baseline run (`diff` clean). Steps 1-8
are unchanged, as required.

## A4 - real-kline proof-count comparison (D4 directional recount)

`ReplayScbSteps1to8.java` intentionally skips step 9 (no 1m klines in archived
snapshots). Built a small harness (`ReplayA4Dump.java`, kept out of the repo -
scratch-only) that for each snapshot: reads `timestamp_utc` + `asset`, fetches (or
reads from cache) real 1m klines via the exact window/limit/drop-forming-bar rule
`MarketDataSnapshot.fetchMultiTimeframeAsOf` uses for its `"1m"` leg
(`GET /fapi/v1/klines?...&interval=1m&startTime=asOf-86400000&endTime=asOf&limit=1440`,
then drop the trailing bar if its close time is after `asOf`), caches the raw response
under `$HOME/kline_cache/` (never in the repo), and calls
`SetupCandidatesBuilder.build(...)` with an empty `mtf` map (matching
`ReplayScbSteps1to8`'s finding that steps 1-8 read root snapshot fields, not `mtf`).
Ran it once against the OLD (unmodified) compiled class and once against the NEW (C3)
compiled class, over the identical cached klines.

**Sample**: full A4 over the entire ~9,868-snapshot corpus wasn't feasible in this
session's time budget, so used a 417-snapshot stratified sample: all 368 snapshots in
the since-golden-boundary set (1332) that have at least one rank<=3 candidate with
`net_rr_sanity=true` (the proxy used for "signal-rich"/proof-eligible snapshots -
verdict is computed downstream in Python and isn't stored per-snapshot in the Java
archive, so this is the closest available proxy to "every snapshot with a
SETUP_FORMING/WAIT_PROOF candidate"), plus a 1-in-20 stratified sample (49 snapshots)
of the remaining 964. **This is a sample, not the full corpus.**

Result over 417 snapshots / 1828 candidates, 0 fetch/build errors:

```
delta = new_proof_count - old_proof_count
delta histogram: -3:57  -2:420  -1:935  0:416
changed (delta != 0): 1412 of 1828
```

For every one of the 1828 candidates, the measured delta was independently checked
against the directional-recount rule computed from that candidate's own proof detail
(`finished_auction.detected`/`direction`, `book_imbalance`, `speed.picking_up`) and
its `direction`:

```
expected_delta = -(1 if speed.picking_up)
                 -(1 if finished_auction.detected and NOT favours direction)
                 -(1 if book_imbalance was counted under the OLD rule and NOT favours direction)
```

```
rule_matches: 1828 of 1828  (100%)
rule_mismatches: 0
boundary_flags (book_imbalance within 0.01 of the 0.67/1.5 threshold, a rounding risk
  from the 2-dp value stored in the proof JSON): 0
```

Every delta is <= 0 (the new rule can only remove points, never add), consistent with
D4's intent. No snapshot/candidate errored or was skipped in the sample.

## C2 (D3) Python-side transition matrix

Ran the `verdict.py` D3 guard against the full corpus (9868 files / 9865 unique
timestamps) using a from-scratch A/B comparison (isolating the guard's own effect,
independent of the stale `verdict_golden_baseline.csv`, which predates C1):

```
BEFORE (current working-tree verdict.py, C1 already applied) vs
AFTER  (BEFORE + this D3 guard)

total snapshots: 9865
changed: 414
  WAIT_PROOF   -> NO_TRADE : 185
  WAIT_RR      -> NO_TRADE : 122
  WAIT_TRIGGER -> NO_TRADE : 107
```

Same shape as the plan's D3 matrix (three buckets, all landing in NO_TRADE, zero
SETUP_FORMING/WATCH transitions - i.e. "no actionable verdict changes"). Counts differ
from the plan's original 174/114/59 (measured pre-C1, smaller corpus) because (a) the
corpus has grown since 2026-09-27's plan measurement and (b) this measurement is
necessarily taken on top of C1 (verdict.py's working tree already has it), which
shifts some of these 414 snapshots between WAIT_RR/WAIT_PROOF/WAIT_TRIGGER buckets
before the D3 guard is applied - the same kind of corpus/ordering drift already noted
for C1 in D1_D7_DECISION_BRIEF.md ("WAIT_TRIGGER->WAIT_RR 891, plan predicted 893").
Independently verified the 414 figure against the raw JSON (not just via the verdict
diff): corpus-wide, exactly 414 archived snapshots have `setup_candidates[0].rank > 3`
(the F6 bug scenario), and in all 414 of them there is no candidate with `rank <= 3`
anywhere in the array - so the guard correctly turns all 414 into `NO_TRADE` and no
others, matching the 414 changed count above exactly.

Per the task note, `verdict_golden.py --write-baseline` was **not** run - freezing a
new baseline is a real state change that belongs with operator/Opus review of this
whole batch, not something to do unilaterally from this build session.

## Unit tests

Project has no pre-existing `src/test/` (plan F4, T037 blocked). Staged
`pom.xml.new` (adds `junit-jupiter` test-scope dependency + `maven-surefire-plugin`)
and `src/test/java/datafeed/CountSignalsD4Test.java.new` (14 tests, see above). All
14 pass in a scratch build with the `.new` files applied.

## What could not be done / open issues

1. **Live-path acceptance for C2** (`core_invariants` checks I12 and I14 reset to
   baseline 0 "from deploy time" and PASS "after 1 hour of live loop") requires the
   actual live PowerShell/Python loop running against the operator's Windows box -
   not reproducible from this Linux bridge session. Only the offline Java-source
   verification (A3 unchanged, D3 guard matrix) was possible here.
2. **Live-path acceptance for C3** (new `core_invariants` check I16, "proof_count
   equals directional recount", against *live* snapshots after deploy) is likewise
   deploy-only; the offline equivalent (A4, real klines against archived snapshots)
   was done instead and shows a 100% rule match on the 417-snapshot sample.
3. **A4 is a sample** (417 of ~9,868 snapshots; 1828 candidates), not the full
   corpus, chosen to guarantee coverage of every rank<=3/net_rr_sanity=true
   ("signal-rich") snapshot in the since-golden-boundary set plus a stratified sample
   of the rest, due to the session's time budget. All 417 succeeded (0 errors); no
   evidence found of any deviation from the directional-recount rule, but a full-corpus
   run would give a stronger guarantee and should be considered before sign-off if
   time allows.
4. **PowerShell mirror**: `scripts/core/start-trading-day.ps1`'s `Compute-Verdict`
   was not touched in this session - C2's spec (CORE_READINESS_PLAN.md) only calls
   for the Java change plus the `verdict.py` guard; the PowerShell file was already
   handled under C1/B1 per D1_D7_DECISION_BRIEF.md and is out of scope here. No
   PowerShell interpreter is available in this Linux session to re-verify it.
5. `verdict_golden_baseline.csv` was intentionally left un-frozen (see above).
6. All scratch/build artifacts (`$HOME/build*`, `$HOME/replay_*`, `$HOME/verdict_test`,
   `$HOME/a4_harness`, `$HOME/kline_cache`) live outside the repo checkout and were
   never copied into it; only the five `.new` files listed above were staged in the
   repo tree.
