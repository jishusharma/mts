# FINAL REPORT
# Session: MTS-2026-09-18-0848Z
# Written: 2026-09-18T16:10Z
# Purpose: corrected diagnosis, evidence, sequencing
# Supersedes: the earlier FRAME GATING report (diagnosis was wrong)
#
# STATUS TAGS: [VERIFIED] from disk this session, [PASTE] from user paste,
# [INFERRED] reasoning from verified inputs, [UNVERIFIED] not checked.

## 0. WHAT THIS REPORT ANSWERS

Operator asked, verbatim:
  "why our day was not identified as trend?"
  "why we never saw a long entry after two +ve day closes?"
  "what is the correct order?"
  "revalidate with disk"
  "apply different lenses - does the result set answer the goals?"

This report is the answer to all four.

## 1. THE OPERATOR QUESTION, ANSWERED

Two +ve daily closes did not produce a long because:
  a. No field encodes consecutive positive closes. [VERIFIED]
  b. determineDirections (line 281-291) returns only one side per cycle.
     Above VAH it returns ["short"]. [VERIFIED from disk]
  c. determineSetupType (line 427-459) has no TC or BO branch. It
     returns only ct_short, ct_long, scalp_short, scalp_long, or null.
     [VERIFIED from disk]
  d. Therefore a long above VAH is impossible by construction. Not
     miscomputed. Not suppressed. Unavailable.

The state classifier is not the blocker. It was rewritten 2026-09-17
and now reads vwap_slope, cvd_slope, price_vs_va. It returns
trend_healthy correctly when price is above VAH. [VERIFIED]

The blocker is one function. determineSetupType. No long path exists
above VAH. No TC or BO path exists anywhere.

## 2. EVIDENCE FROM DISK

### 2.1 classifyState (SetupCandidatesBuilder.java lines 261-279)
```
261: private static String classifyState(ObjectNode root) {
262:     // Rewritten 2026-09-17 per Rule 32. Old version read daily_vp.shape=="B"
263:     // and returned balance. buildVp emitted "B" for bell shapes, so it fired
264:     // on all 2090 snapshots on disk. Engine saw balance always; emitted
265:     // scalp_short/long at VWAP in trends. Now uses real signals.
266:     // Rule 32 test: 3/3 outside-VA snapshots changed to trend_healthy.
267:     String vwapSlope = root.get("conditions").get("vwap_slope").asText();
268:     String cvdSlope = root.get("conditions").get("cvd_slope").asText();
269:     String priceVsVa = root.get("conditions").get("price_vs_va").asText();
270:     if (("flat".equals(vwapSlope) || "sideways".equals(vwapSlope))
271:             && "flat".equals(cvdSlope)
272:             && "in_va".equals(priceVsVa)) {
273:         return "balance";
274:     }
275:     if ("divergent".equals(cvdSlope)) return "trend_unhealthy";
276:     if ("above_vah".equals(priceVsVa) || "below_val".equals(priceVsVa))
277:             return "trend_healthy";
278:     if ("aligned".equals(cvdSlope)) return "trend_healthy";
279:     return "balance";
280: }
```
Reasoning: state is correct. When price is above VAH it returns
trend_healthy. It no longer reads vp_shape. The 2026-09-17 rewrite
removed the shape dependency.

### 2.2 determineDirections (lines 281-291)
```
281: private static List<String> determineDirections(ObjectNode root) {
282:     String priceVsVa = root.get("conditions").get("price_vs_va").asText();
283:     String priceVsPoc = root.get("conditions").get("price_vs_poc").asText();
284:     List<String> dirs = new ArrayList<>();
285:     if ("above_vah".equals(priceVsVa)) {
286:         dirs.add("short");
287:     } else if ("below_val".equals(priceVsVa)) {
288:         dirs.add("long");
289:     } else { // in_va
290:         if ("above".equals(priceVsPoc)) {
291:             dirs.add("short");
```
Reasoning: above VAH the only direction is short. Below VAL the only
direction is long. Inside VA the direction depends on POC. This is
the compiled engine directional filter made concrete. It is not a
bug. It is why no long above VAH is evaluated.

### 2.3 determineSetupType (lines 427-459)
```
427: private static String determineSetupType(Zone zone, String direction, String state) {
428:     String zoneType = zone.type;
429:     boolean isShort = "short".equals(direction);
430:     if ("transition".equals(state)) return null;
431:     // CT setups
432:     if (zoneType.contains("vah") || zoneType.contains("swing_high") ||
433:            zoneType.equals("prior_day_vah")) {
434:         return isShort ? "ct_short" : null;
435:     }
436:     if (zoneType.contains("val") || zoneType.contains("swing_low") ||
437:            zoneType.equals("prior_day_val")) {
438:         return isShort ? null : "ct_long";
439:     }
440:     if (zoneType.contains("poc")) {
441:         // POC: CT only in unhealthy trend
442:         if ("trend_unhealthy".equals(state)) {
443:             return isShort ? "ct_short" : "ct_long";
444:         }
445:         return null;
446:     }
447:     if (zoneType.equals("vwap") || zoneType.startsWith("vwap_band")) {
448:         // Scalp if sideways
449:         if ("balance".equals(state) || "sideways".equals(state)) {
450:             return isShort ? "scalp_short" : "scalp_long";
451:         }
452:         return null;
453:     }
454:     if (zoneType.equals("fvg")) {
455:         return null;
456:     }
457:     if (zoneType.equals("prior_day_close")) {
458:         return isShort ? "ct_short" : "ct_long";
459:     }
460:     return null;
461: }
```
Reasoning: this function does not use state on lines 432-437. It
uses state only on POC (440) and VWAP (447). The compiled engine
rule is CT requires balance or unhealthy trend. For VAH, VAL, and
swing zones, state is ignored. That is the code-vs-rule mismatch.

Also verified: no branch returns "tc_long", "tc_short", "bo_long", or
"bo_short". The strings do not appear. There is no trend-continuation
or breakout setup type in this function.

### 2.4 Dead code check (from grep)
```
BinanceClient.java:50: public JsonNode takerBuySellVol(...)
BinanceClient.java:51:     return get(BASE + "/futures/runtime_data/takerBuySellVol...")
BinanceClient.java:65: public JsonNode topLongShortPositionRatio(...)
BinanceClient.java:66:     return get(BASE + "/futures/runtime_data/topLongShortPositionRatio...")
BinanceClient.java:70: public JsonNode topLongShortAccountRatio(...)
BinanceClient.java:71:     return get(BASE + "/futures/runtime_data/topLongShortAccountRatio...")
MarketDataSnapshot.java:1370: JsonNode whalePos = client.topLongShortPositionRatio(symbol, "1h", 5);
```
Reasoning: topLongShortPositionRatio IS called (line 1370). The
earlier claim that it is dead code was wrong. takerBuySellVol and
topLongShortAccountRatio are still dead (zero call sites).

### 2.5 B047 finished_auction sign (lines 700-710)
```
701:     if (reversal && noFollow) {
702:         res.finishedAuctionDetected = true;
703:         res.finishedAuctionDirection = deltas[i] < 0 ? "sell" : "buy";
704:         res.finishedAuctionExtremeDelta = deltas[i];
705:         res.finishedAuctionReversalDelta = deltas[i + 1];
706:         res.finishedAuctionFollowThrough = false;
707:         break;
708:     }
```
And from Python consumer (math_object_builder.py lines 390-401):
```
390:     if _dir == "short":
391:         if _fa_dir == "buy":
392:             _contradictions.append("finished_auction=BUY vs SHORT")
...
397:     elif _dir == "long":
398:         if _fa_dir == "sell":
399:             _contradictions.append("finished_auction=SELL vs LONG")
```
Reasoning: Java emits "sell" when delta is negative. Python flags
"SELL" as a contradiction for a long setup. The semantic intent
of "finished auction" is a completed one-sided move at an extreme.
Whether a negative delta at a low is a "sell" or a "buy" is the
question B047 asks. The code-side mismatch is confirmed. The
correct answer is not yet decided. Rule 32 applies.

### 2.6 MTS-FRAME consumption (grep across scripts and runtime)
```
mts-watch.ps1:82-89: displays MTS-FRAME from state_code_regime.json
regime_classifier.py:9: writes state_code_regime.json
```
Reasoning: nothing else reads MTS-FRAME. Not the verdict path.
Not the setup assignment. Display only.

### 2.7 Current runtime
```
Wrapper PID 15424 (mode.ps1 -M armed)
No supervisor (SUP COUNT=0)
Latest snapshot BTCUSDT_2026-09-18_1789747456985.json at 16:04:16Z
state_code_regime: label=RANGE, entered 15:58:22Z, votes_up 2, votes_down 0
DSP section 11: last update 2026-09-18T15:54Z
Handoff: rewritten 2026-09-18T15:55:04Z
```
Reasoning: session is live and current. Loop advanced through the day.
The parallel session updated DSP and handoff.

## 3. WHY EARLIER DIAGNOSIS WAS WRONG

The earlier "FRAME GATING" report said:

  "classifyState reads vp_shape -> TWOPEAK -> balance. State stuck. Frame
   label computed but not consumed. Fix frame gating first."

Disk says:
  classifyState no longer reads vp_shape (rewritten 2026-09-17).
  State classifier correct.
  Frame label computed and displayed but not consumed.
  Actual defect is elsewhere.

The earlier report relied on an audit claim (AUDIT_2026-09-17_TRACKER.md)
that said "classifyState no longer reads shape." It carried the
"stuck in balance" framing from prior sessions and did not re-read
the function.

Reasoning for the error: prior sessions treated "vp_shape = TWOPEAK
all snapshots" as the cause. It is a symptom. The vp_shape field
exists and is TWOPEAK, but the classifier does not read it. The
symptom was mistaken for the cause.

## 4. CORRECTED ORDER OF WORK

### Step 1 - Smallest correct fix
Add a state check to determineSetupType lines 432-437.

Proposed change:
```
432: if (zoneType.contains("vah") || zoneType.contains("swing_high") ||
433:         zoneType.equals("prior_day_vah")) {
434:     if ("trend_healthy".equals(state)) return null;
435:     return isShort ? "ct_short" : null;
436: }
```
Same shape for the VAL and swing_low branch. When state is
trend_healthy, no CT setup is emitted at VAH or VAL. Engine goes
silent on that zone.

Reasoning: this is the smallest change that fixes the code-vs-rule
mismatch. It touches two branches. It does not add new setup types.
It does not change direction logic. It enforces the compiled engine
rule: CT requires balance or unhealthy trend.

Rule 32 evidence: three snapshots from today where state =
trend_healthy and price_vs_va = above_vah and a ct_short candidate
was produced. Today tape has hundreds of them. Verify from
apparatus_log and the snapshot files.

### Step 2 - Build the missing path
No TC or BO branch exists. To allow trend-continuation longs, the
engine needs a new setup type in determineSetupType:
```
if ("trend_healthy".equals(state) &&
        (zoneType.equals("vwap") || zoneType.startsWith("vwap_band"))) {
    return isShort ? null : "tc_long";
}
```
Plus the corresponding verdict handling in start-trading-day.ps1.
This is a new feature, not a fix. Rule 32 applies. Rule 33 applies
(new field for TC setup type if it does not exist as a vocabulary
term in the verdict path).

Reasoning: this is the answer to "why no long entry after two +ve
days." The path does not exist. Adding it is a build, not a repair.
Do not bundle with Step 1. Different change, different evidence.

### Step 3 - B047 finished_auction sign
Resolve whether deltas[i] < 0 ? "sell" : "buy" is semantically
correct. Requires Tom source and a specific reading of what
"finished auction at a low" means. Rule 32 for the fix.

### Step 4 - B044 takerBuySellVol
Wire the existing dead method into snapshot CVD. Replaces the
kline proxy. Better flow data feeds every proof flag. Rule 33 for
the change (it changes the source of a field, but the field
already exists).

### Step 5 - L29 VP shape classifier
Lower priority now. The shape field is not read by classifyState.
It is still read by other rules (compiled engine higher-TF
conflict resolution). Fix when a rule needs it.

### Step 6 - Indicator phases
OI delta, positioning states, aggregated CVD. New fields. Multi-
session work. Not blocking anything.

## 5. WHAT THE CORRECTED DIAGNOSIS CHANGES

| Item | Earlier report | Corrected |
|---|---|---|
| Root cause | classifyState stuck | determineSetupType missing state check |
| Frame gating fix | recommended | not sufficient (no TC/BO to redirect to) |
| classifyState reads shape | yes | no (rewritten 09-17) |
| topLongShortPositionRatio dead | yes | no (called at line 1370) |
| TC/BO path exists | implied | no, never built |
| First fix | frame gate | state gate on VAH/VAL branches |

## 6. WHAT THE CORRECTED DIAGNOSIS KEEPS

- Frame is display-only. Confirmed.
- takerBuySellVol dead. Confirmed.
- topLongShortAccountRatio dead. Confirmed.
- Extraction chain broken (2 of 50). Confirmed.
- TOM_VERBATIM_INDEX 0 referenced. Confirmed.
- compiled_engine stale (2026-09-16 20:57Z). Confirmed.
- B047 line 703 unchanged. Confirmed.
- Session live. Confirmed.

## 7. WHAT TO SEND TO THE NEXT SESSION

This report. Also the earlier one, marked superseded on diagnosis.
Also this verification block:

```
"### verify determineSetupType ###"
$scb = ".\src\main\java\datafeed\SetupCandidatesBuilder.java"
$lines = Get-Content $scb
for ($i=426; $i -lt 460; $i++) { "{0,5}: {1}" -f ($i+1), $lines[$i] }

"### verify classifyState ###"
for ($i=260; $i -lt 280; $i++) { "{0,5}: {1}" -f ($i+1), $lines[$i] }

"### verify determineDirections ###"
for ($i=280; $i -lt 300; $i++) { "{0,5}: {1}" -f ($i+1), $lines[$i] }

"### state values in recent snapshots ###"
Get-ChildItem .\runtime_data\snapshots\BTCUSDT_*.json | Sort LastWriteTime -Desc |
  Select -First 10 | ForEach-Object {
    $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
    "$($_.LastWriteTimeUtc.ToString('HH:mm:ss')) va=$($j.conditions.price_vs_va) vwapSlope=$($j.conditions.vwap_slope) cvdSlope=$($j.conditions.cvd_slope)"
  }

"### count ct_short at VAH today ###"
Select-String -Path .\runtime_data\apparatus_log.txt -Pattern 'ct_short.*daily_vah|ct_short.*4h_vah|ct_short.*weekly_vah' |
  Measure-Object | Select -ExpandProperty Count
```

## 8. WHAT REMAINS UNRESOLVED

- B047: is the finished_auction sign semantically correct? Not
  answered. Needs Tom source read and a decision.
- Does any other function use state in a way that would break if
  the state gate is added to determineSetupType? Not verified.
- Does the alert card, dashboard, or verdict path depend on
  determineSetupType returning a CT setup when state is
  trend_healthy? Not verified. If yes, adding the state gate will
  change downstream behavior in unexpected places.
- Is the current state_code_regime.json RANGE the correct label at
  16:04Z given the day price action? The vote classifier says
  RANGE with votes_up 2. Whether the classifier is right is a
  separate question.

## 9. THE ONE SENTENCE

The engine produced no long entries today not because the state
classifier failed, but because determineSetupType has no long
path above VAH and no state check to suppress CT setups in trend
conditions. The fix is a two-branch state gate on lines 432-437,
plus a separate feature build to add TC/BO paths. The earlier
frame-gating recommendation is superseded.

# END
