# T058 - BROKEN LOWS/HIGHS BY TIMEFRAME: CONTINUATION vs LIQUIDITY SWEEP

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: T048 (satellite framework - hedge trigger), T053 (hedge scalping), T040 (tick/OI extremes),
T055a (positioning flow), T054 (liquidity runs at US open), 085/086 (live alert runner).
Rule: any setup found becomes a separate layer (PROJECT_VISION), never a Tom filter.

## VERBATIM ASK (operator, 2026-09-29)
Research Questions to be explored for MTS -
	a. When price breaks a lower low in any time frame - then it has different context perhaps. Weekly low broken is diff than Daily and So on!
	How do we know what a broken low suggests? more down side or a market move to take out liquidity and then change direction!
	This matters on both sides - up for highs and down for lows. So the question is - How professional traders use this knowledge and where MTS can benefit from this?
	For example for our satellite and cluster model (not sure i named that right). So here - a hedge could be guided from this knowledge.
	Back-testing can also reveal patterns - when lows are broken - what is the read for other indicators(maybe we need to compare current, before and after readings to confirm the patterns).

## STATE
2026-09-29 OPEN, fast-track (operator). "satellite and cluster model" = T048 satellite framework.
Plan (supervisor):
 R  Sonnet web research, playbook Part I -> research/fast_track_2026-09-27/T058_BROKEN_EXTREMES.md
    (how pros classify break-and-hold vs sweep-and-reclaim; per-TF evidence; T1-T3/REJECT tiers).
 D  Same worker: event definitions + backtest plan (event study by TF W/D/4h/1h/15m; outcome = continuation
    vs reclaim within N bars; indicator state before/at/after: RSI, CVD, OI delta, funding, volume, tick tiers).
    Formulas -> FORMULAS.md candidates section (not canonical until supervisor accepts).
 Q  Qwen specs for the event detector + event-study script (after D is accepted).
 S  Satellite hook: which outcome class could trigger/size a T048 hedge - written as a proposal only.
2026-09-29 R+D+S DONE (Sonnet builder): research/fast_track_2026-09-27/T058_BROKEN_EXTREMES.md. No validated evidence on per-TF sweep vs hold; only T1 mechanism (Osler stop/limit clustering) and T1 equity momentum context. Event-study plan + hedge proposal written; formulas are candidates only. Awaiting supervisor review; data gaps: OI/funding only 2025-09+, no liquidations/aggTrades.
