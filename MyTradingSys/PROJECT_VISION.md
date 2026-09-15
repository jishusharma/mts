# PROJECT VISION / DIRECTION
# Saved: 2026-09-15
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

- Session anchor: UTC 00:00 / US cash open / both. (Blocker.)
- How does each integration surface its read? Snapshot field, separate file, sidecar process? (Undefined.)
- Interface between MTS core and read layers? (Undefined.)
- When a read conflicts with MTS, which wins? (Undefined. Must be decided before integration.)

# END
