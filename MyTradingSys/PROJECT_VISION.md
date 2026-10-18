# PROJECT VISION / DIRECTION
# Saved: 2026-09-15  |  Rewritten: 2026-09-23 (architecture doctrine locked)
# Purpose: direction ledger + locked architecture doctrine. Read before any new build.
# Rule 52: this is a pointer for direction, not a spec.
# Change rule: verbatim sections change only by operator edit. No agent rewrite.

## DIRECTION UPDATE (2026-10-13, operator chat; supersedes the ARCHITECTURE DOCTRINE, PRINCIPLES and "Cores and layers" / "Provenance" below where they conflict)

### OPERATOR STATEMENT (verbatim, 2026-10-13)
"We need flexible system now that can adapt to whatever change we need to bring. So we have to remove all those uh, hard rules about layers and everything." ... "why do not we just apply our own brains rather than uh, depending on uh, what we find where we have the core idea and we have the chart we have the data so let us apply the core idea on the chart and uh, see how it needs to be adjusted in order to make profitable trades."
Also: "Orderflow is real and works on all markets." and, on "Tom is core, non-negotiable": "It was a long time ago when we started - now it makes no sense to have anything like this."

### INTERPRETATION (not verbatim)
1. No fixed core. Tom, Fabio and every other system are layers. Layers may be combined or used as filters on each other; evidence
   (fee-net, out of sample) decides what trades.
2. Our own judgement is allowed. A number is SOURCED (trader's words, file:line) or OURS (our judgement or tuned). OURS numbers are
   chosen on DEV, checked once on VALIDATION, and the holdout is read once; every variant is counted. That replaces the NO-SOURCE ban.
3. Market: BTC. Tom's core idea (order flow + volume profile) is applied on BTC charts and BTC data, which carry the order flow the DAX
   CFD feed lacked. The DAX chain is parked and no FDAX data is bought (q11). Plan: research/tom_btc_2026-10-13/TOM_ON_BTC.md.
4. Unchanged: testnet only until the GO-LIVE BAR holds; live-tree and safety rules in CLAUDE.md.


## ARCHITECTURE DOCTRINE (locked 2026-09-23)

### OPERATOR STATEMENT (verbatim, 2026-09-23)

"We use Tom's core ideas - It is the core layer. Everything else sits on top of it and must be an independent module that could be switched on and off for computation/integration purposes and or displayed along side as complimentary readings. Understand that we will keep adding Tom's rules as we extract more transcripts. And not just from him - also from different analysts. We will then decide what gets into the core engine later as the project evolves and we back test!"

### INTERPRETATION (not verbatim)

1. [SUPERSEDED 2026-10-13: no fixed core, see DIRECTION UPDATE 2026-10-13] TOM IS CORE. Tom's rules are the core layer. Non-negotiable. Sourced from transcripts, cited per [TOM-NNN].
2. EVERYTHING ELSE IS A MODULE. Modules are switchable: on for computation and/or integration, off for baseline operation. Or displayed alongside as complementary reading. Modules never gate core behavior.
3. CORE GROWS. New Tom transcripts extend the core. Other analysts' rules may enter the core later, by the same admission gate.
4. ADMISSION IS DEFERRED. New rules wait at the module layer until project maturity and backtesting justify promotion. No rule enters the core engine without that gate.

### RELATION TO DSA SECTION 9

DSA_SESSION_PROMPT.md section 9 lists the authority order for behavior in a
session: compiled_engine first, condition files second, Tom transcripts third.
That order governs how a live session resolves conflicts. This doctrine governs
what should be in the engine over time: Tom's rules, extended by extraction,
with non-Tom layers kept modular. The two are compatible. Where they appear to
conflict, DSA governs the session; this file governs direction.

### CURRENT TAG FAMILIES IN compiled_engine.md

Inline rule tags as of 2026-09-23 (grep of compiled_engine.md):

| Tag | Count | Role |
|-----|-------|------|
| [PRINCIPLE] | 21 | reading aids, display-only |
| [SYSTEM] | 11 | mechanism, math, plumbing |
| [VISUAL FLAG] | 2 | screenshot-only, no runtime consumer |
| [SSOT] | 1 | single-source marker |

[TOM-NNN] and [CT-NNN] are source ids in traceability matrices, not inline
rule tags. Under this doctrine, inline tags will be extended to [CORE] or
[MODULE] over time. That extension is deferred; the doctrine locks the intent,
not a code change.

## THE FOUR GAP CLASSES (locked 2026-09-23)

### OPERATOR STATEMENT (verbatim, 2026-09-23)

"1. It can be that we did not extract all rules so far!
2. We extracted rules incorrectly or partially
3. Extracted rules are implemented incorrectly or partially or missed compleletly
4. Rules could be wired incorrectly or not wored at all."

(Spelling preserved verbatim: "compleletly", "wored".)

### PLAIN FORM

| # | Gap | Where it lives | Guard |
|---|-----|----------------|-------|
| 1 | Rule not yet extracted | Transcript to extract | Extraction coverage audit |
| 2 | Rule extracted incorrectly or partially | Extract file | DSA section 10 discipline (three snapshots) |
| 3 | Rule implemented incorrectly, partially, or missed | Code | Source-to-code traceability (T043) |
| 4 | Rule wired incorrectly or not wired | Runtime | Runtime verification, not just compile/test |

Gaps 1 and 2 sit upstream of the engine. Gaps 3 and 4 sit inside it.
T043 currently covers 3 and 4 only. Gaps 1 and 2 have no mechanism yet.
## USER DIRECTIVE (verbatim, 2026-09-15)

"Instead of thinking like this - think -> that we will create this capability that is session-aware and use it an as in add on to our existing system. We do not need to change any existing trade logic right now. let this evolve. First let us see how the outer frame will look like.

Note that we will integrate RSI - so it is momentum and it comes from a different trading system which is using RSI as 40-60 as per MalkanViews. So it will provide us trade setups. Similarly - we were working on probability distribution and it will do it's job and now I am not sure how we need to combine things. we need to keep things isolated at first and get independent read of these trading systems that we will integrate with MTS and then we can look for confluences and use some metric from these new trading system integrations that will be like a add on stuff. Take for example analysts verdicts on trades - so we will download video transcripts - extract and keep tabs on what they say and the confluences we get from our trading systems. Slowly we can even integrate it but it is distant! I think you should save this note verbatium for the needs of the project and it's direction that should be kept in mind before developing anything new! We can also build and maintain it to see where we are headed."

## INTERPRETATION (not verbatim)

1. ADD-ON, NOT REWRITE. Session-aware frame layers on MTS. Existing trade logic unchanged. Let it evolve.
2. OUTER FRAME FIRST. Define how the session frame looks before wiring anything in.
3. ISOLATE, THEN COMBINE. Each external system produces its own independent read first. Confluence is a later step, only after independent reads are proven.
4. INTEGRATIONS ARE PEERS. RSI/MalkanView, probability distribution, analyst verdicts each enter as a separate read layer. None replaces MTS core.
5. ANALYST LAYER IS A PIPELINE. Download transcripts -> extract -> track verdicts -> compare against MTS output. Distant. Not wired.
6. THIS FILE IS THE DIRECTION LEDGER. Read before any new build. Update when direction changes.

## INTEGRATIONS TRACKED

| System | Source | Status | Read produced |
|---|---|---|---|
| RSI 40-60 (MalkanView) | external system | design 2026-09-28 (RSI_TF_LAYER_DESIGN.md); sub-layer of the RSI layer | momentum, setup timing |
| Probability distribution | event_probability_layer_DESIGN.md | stage 3 unblocked 2026-09-28 (10,289 labels; 5,000 gate met); frequency-table MVP queued (NUC 033) | forward return probability |
| Analyst verdicts | extracts/processed/tom/ + future | distant | discretionary opinion |
| Session-aware frame | new (this project) | design | session bias, day type, initial balance |

## PRINCIPLES

- [SUPERSEDED 2026-10-13] Tom is core. Everything else is a module. Modules never gate core behavior.
- Modules are switchable: on for computation/integration, off for baseline. Or displayed alongside.
- Add, do not modify. Core MTS logic not rewritten.
- Isolate first. Combine only after each read is independently validated.
- Independent reads before confluences.
- Rule 32 still binds: no new engine rule without 3-snapshot proof.
- Direction documented here before build.
- RSI arrives first. Design its isolation path with the session frame.

## OPEN QUESTIONS

- Session anchor: RESOLVED 2026-09-16. Two anchors, two jobs. UTC 00:00 anchors raw data calculation (existing CVD block and session aggregates). US cash open (13:30 UTC summer / 14:30 UTC winter, DST-aware) anchors the session-aware frame: session high/low/open, range position, day type, initial balance, session bias. The sixteen new session fields use the US cash open anchor. No existing UTC-anchored field is renamed or moved.
- How does each integration surface its read? Snapshot field, separate file, sidecar process? (Undefined.)
- Interface between MTS core and read layers? (Undefined.)
- When a read conflicts with MTS, which wins? (Undefined. Must be decided before integration.)
  RESOLVED 2026-09-25 (worker W6, receipt per extract PROJECT_VISION.md L23-L28; L134-L138; L16-L18).
  Q1 (how each integration surfaces its read): separate read-layer file or sidecar process; read-only; switchable module; never gates core.
  Q2 (interface between MTS core and read layers): one-way read-only contract over engine-computed state; no writes back; no commands run by the reader.
  Q3 (conflict priority): MTS core wins for core behavior; read layers may annotate conflict as complementary reading only.
  Reply: Dumps/workers/CLOSE-2026-09-25/W6-project-vision/REPLY.md

## USER DIRECTIVE (verbatim, 2026-09-22) - LOCAL AI ASSISTANT + TICK-DELTA LAYER

Quoted from operator note. Preserved verbatim. Full text with the three-machine breakdown is in the companion note supplied to the session; the sections below carry the parts that change project direction.

On the assistant: "the real-time trading assistant must run LOCALLY ON THE DESKTOP, co-located with the MTS engine - not on the NUC. Reason: during an active trade I need instant answers with zero network hop (no LAN round-trip to NUC, no browser/API round-trip to hosted models). The NUC stays purely for offline code work where latency doesn't matter."

On the assistant's job: "it must NOT just repeat what the compiled engine already alerts on (that's already solved, deterministic, and doesn't need an LLM). Its value is answering ad-hoc questions I didn't pre-program a fixed display for - comparing current state to recent history, explaining why a verdict changed, contextualizing strength/weakness of a setup - grounded STRICTLY in what the engine has actually computed. Read-only: it never writes back to the engine, never runs commands, matching the existing MTS safety model."

On the tick-delta layer: "A standalone Python process subscribing to the raw tick feed (independent of the candle-close snapshot writer). Computes fast deltas on selected indicators (price, CVD, whatever else proves useful) over a short rolling tick window. Checks against a threshold - only when crossed does it emit an event (avoids flooding the assistant with tick noise). Writes to a separate event stream/file, tagged clearly as source: tick vs source: candle, so the assistant's context always knows the granularity and recency of what it is looking at. Needs its own cooldown, same as your existing candle-alert cooldown, or tick noise will spam it constantly."

On rule surface: "any tick-based thresholds you pick (what counts as a significant CVD delta, say) will need the same Tom-citation-or-documented-exception treatment your other indicators go through - this is new rule surface, not just plumbing, so it likely needs to go through the same research-tier process before it's trusted in a live decision."

## THE THREE MACHINES (added 2026-09-22)

| Machine | Role | Compute |
|---|---|---|
| Intel NUC 10 (NUC10i7FNHN, i7-10710U, 32GB) | Offline code builder, always-on. Runs Ollama on CPU (no GPU). Background work only. Not live trading. | CPU-only inference, 7B-14B quantized |
| Old desktop (i7-4770K, 32GB DDR3, locked MB/CPU/RAM trio) | Runs the MTS core engine (Java ingest + Python rule eval). Also candidate host for the real-time assistant. | CPU/RAM bound; GPU relevance only for assistant latency |
| Lenovo ThinkPad laptop | Lightweight monitoring. Not a compute node. | N/A |

Decision: GPU purchase for the desktop is not speculative. Test a small quantized model (3B-8B) on CPU first; only measured latency above tolerable threshold justifies a GPU (RTX 3060 class). Evidence-based, not speculative.

## ASSISTANT PRINCIPLES (added 2026-09-22)

- Read-only. Never writes to the engine. Never runs commands. Matches the existing MTS safety model.
- Grounded strictly in engine-computed state. The assistant's answers derive from snapshot fields, verdict strings, alerts, and history; it does not free-reason beyond them.
- Value is ad-hoc Q&A, not alert repetition. Alerts stay in the deterministic engine; the assistant handles questions the engine was not pre-programmed to answer.
- Co-located on desktop. No network hop during an active trade.
- One input granularity tag per consumed record: source:candle or source:tick. Mixing without the tag is not allowed.

## INTEGRATIONS TRACKED (rows added 2026-09-22)

| System | Source | Status | Read produced |
|---|---|---|---|
| Local AI trading assistant (desktop) | operator note 2026-09-22 | direction | ad-hoc Q&A over engine state. Read-only. |
| Tick-based delta layer | operator note 2026-09-22; item doc T040 | design | fast deltas over rolling tick window, threshold-cross events tagged source:tick |
| Ollama code builder (NUC) | operator note 2026-09-22 | direction | offline code change execution. Not live. |

## OPEN QUESTIONS (added 2026-09-22)

- Assistant model choice: which small local model for CPU-first, with GPU fallback. Undecided.
- Assistant context window shape: rolling N-minute window of recent snapshots, or single latest snapshot only. Undecided.
- Tick-delta thresholds: which indicators, what numeric thresholds, what cooldown value. All new rule surface; require research-tier process before trust. Tracked in items/T040_tick_delta_layer.md.
- Assistant input merge: shared file vs separate files for candle and tick streams, ordering and dedup rules. Design item under T040.
  RESOLVED 2026-09-25 (worker W6, receipt per extract PROJECT_VISION.md L114; L116; L118-L120; L126-L130; L135; L138; L152-L153; per extract MTS_DICTIONARY.md L162-L175).
  Q4 (assistant model choice): test a 3B-8B quantized model CPU-first on the desktop; buy an RTX 3060-class GPU only if measured latency exceeds tolerance.
  Q5 (context window shape): rolling N-minute window of recent snapshots, plus alerts and history as needed.
  Q6 (tick-delta thresholds and input merge): start with price and CVD; documented numeric thresholds; explicit cooldown; separate files for candle and tick streams; one granularity tag per consumed record (source:candle or source:tick). Thresholds are new rule surface and require research-tier before trust. Tick-delta stays module-only: it never vetoes or triggers a core setup.
  Reply: Dumps/workers/CLOSE-2026-09-25/W6-project-vision/REPLY.md

## DIRECTION DECISION (2026-09-26) - LAYER FREEZE LIFTED FOR T048

Not verbatim. Recorded per this file's own "direction documented here before
build" principle.

MyTradingSys/PROJECT_VISION.md.new (drafted 2026-09-25 13:21Z, never merged)
proposed a layer freeze pausing T048 (satellite framework + exchange API
layer), T040, the local AI assistant, and further NUC-builder build-out,
until (1) compiled_engine.md's inline tags extend to CORE/MODULE and (2)
T043 closes. Neither condition was actually met when this was found
2026-09-26: (1) is undone - zero CORE/MODULE tags exist, the doctrine above
still calls that extension deferred; (2) T043 closed WONTFIX 2026-09-23 (the
mechanism was rejected, not built - see items/T043_traceability_gap.md,
synced 2026-09-26 to match BUGS.md, having drifted since the closure).

Operator directive 2026-09-26: lift the freeze for T048 specifically. The
NUC-worker rule-tagging/traceability work continues on its own track under
T049; it is not a precondition for T048 anymore. T040 and the local AI
assistant are not addressed by this decision and remain as the unmerged
.new left them unless raised separately.

The unmerged MyTradingSys/PROJECT_VISION.md.new is superseded by this entry
for T048's purposes and left in place as a dated record, not applied.

## USER DIRECTIVE (verbatim, 2026-09-28) - RSI LAYER, TIMEFRAME LAYER, BACKTESTING

Preserved verbatim from the operator's message in the Opus supervisor session (code mode). Spelling kept.

1. Back test all and prepare Qwen for all back testing related stuff.
2. [...] where downloaded - on desktop or NUC? Build must do as much of back-testing as possible under surveillance. This RSI 40-60 must not be used for any other RSI signal that MTS may demand/need/require instead use the usual RSI default readings. Some Things I want to quote here (log as a Verbatim ) -

1. We need smoothed RSI moving average that come with the usual indicator and look for support on these moving avgs on any given time frame. Add this is a separate feature in the RSI module/indicator-layer.
2. The threshold of slipped from actual numbers like RSI taking support on the 60 line or RSI rejected from the 40 line. So it can reject from 41 0r 42 or 39/38  etc - so we need to see during back-testing that how much slippage we can allow based on actual results. This to be done for all edge cases/scenarios.
3. RSI modules must be also layered within. A full Malkanview RSo 40-60 system can spit out trades for any timeframe. But we may require things like RSI support or rejecton in 3 mins or 2 mins or 15 mins or 12 ours - whenever it changes - we get an alert for each time frame. We need usual time frames but we also need 1,2,3,10 mins and 2 day, 3 day and 5 day as well! I think we might require a separate timeframe layer that serves each module/later including core? Opus needs to decide.
4. So once we start testing indicators on test-net - we will fine tune them as per my inputs and expertise and as per professional that are WORTH listening to in the Crypto Space! Remeber about the fine tuning part and make sure our design is flexible and accurate and well aritectured for this trading software we are building.

So you get the idea.. I need evrything rolling efficiently

### INTERPRETATION (not verbatim)
Design decisions for this directive: MyTradingSys/research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md.

## DIRECTION UPDATE (2026-10-10, operator approved D23 'Apply the addendum as drafted'; not verbatim; supersedes stale rows above where they conflict)

Backtest gate (2026-10-12): every layer backtest answers the 12 items in `backtest/PRE_REG_TEMPLATE.md` before it runs.

### Goal and stages
MTS exists to trade BTC with a proven net edge after fees, first on testnet, then real money only after the
GO-LIVE BAR (system/GO_LIVE_BAR.md, D06-gate 2026-10-09) holds for 30 days. Work follows five stages:
S1 trustworthy measurements, S2 survive the fees, S3 find a real edge (walk-forward OOS net R > 0, CI above 0),
S4 prove it on testnet, S5 go-live gate. Status today: S1-S2 in progress; no source has passed S3.

### Cores and layers
Two cores since 2026-10-01: Tom and Fabio, each compiled independently with its own verdicts, plans and ledger
source flag (research/ARCHITECTURE_TWO_CORES_2026-10-01.md). Every other system (RSI/Malkan, CryptoCred,
session, positioning, probability, tick, timeframe, options, analyst/caller feeds) is a switchable layer that
never gates a core. A core or layer that fails S3 on fixed data is parked (alerts kept for data), not tuned
into passing. Promotion to core uses the S3 bar, never opinion.

### Provenance and its two exceptions
Every parameter comes from the source trader's own words (file:line) or is NO-SOURCE. Exceptions:
(1) BT-TUNED: backtests may tune toward catching big, profitable moves; tuned values are labelled and never
written to live files without an operator decision. (2) NO-SOURCE research tests: specs with no trader
behind them (chatbot handoffs, B163) may run as labelled backtests only, never as live layers.

### Sources we listen to
A trader/analyst enters only with transcripts or a verifiable call history, scored before any trade
(Qriptal scorecard B162 is the template). Each stays an isolated layer until S3.

### Economics and risk
Every result is net of real fees and funding. Stops are wide enough that fees cost under 0.25 R.
Safety checks fail closed; missing data is reported as missing, never as 0. Per-source testnet accounts,
daily-loss monitor and kill switch guard every trade. Testnet calibration (all layers fire) counts as data,
not as S4 evidence; only S3-passed configs count toward the bar. Mainnet needs a separate signed decision.

### How the project runs
Operator speaks through the Control Room (inbox verbatim, decisions). Work is cost-routed: scripts, then DSA,
then Sonnet, Opus only when named. Sessions are short and relay automatically. Code reaches the live tree only
through CI-gated auto-deploy. Off-desktop sessions read live state through the read-only mirror.
Devices: JIS-NB live loop; JIS-NUC backtests (candidate live host); laptop for travel. Qwen/Ollama lane retired.

### Parked or open
Local AI assistant: parked (no build since 2026-09-25). Symbol scope beyond BTCUSDT perp: undecided.
Confluence may gate a trade only after each input passed S3 on its own.

# END
