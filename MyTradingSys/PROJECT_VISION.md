# PROJECT VISION / DIRECTION
# Saved: 2026-09-15  |  Updated: 2026-09-22 (assistant + tick-delta + machines added)
# Purpose: Direction to keep in mind before developing anything new.
# Maintained. Update as the project evolves.
# Rule 52: this is a pointer for direction, not a spec.

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
| RSI 40-60 (MalkanView) | external system | planned | momentum, setup timing |
| Probability distribution | event_probability_layer_DESIGN.md | parked (needs 500+ labels; currently ~154) | forward return probability |
| Analyst verdicts | extracts/processed/tom/ + future | distant | discretionary opinion |
| Session-aware frame | new (this project) | design | session bias, day type, initial balance |

## PRINCIPLES

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

# END
