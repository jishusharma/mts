# NEXT_SESSION

## Supervisor (login C, JIS-NB) workload split 2026-10-19 ~20:00 IST (login C weekly 90%, cap 95-96% for the next 5 h; weekly resets 10-20 20:00Z)
Run with zero operator input; defaults for open questions. Login C has ~5% weekly left: NB ships only (no new builds, workers, Fable) until the reset. Others take, in order, whoever has budget:
- NEW operator study RSI deep-buy (buy the per-TF RSI extreme, no stop, scale-in, exit at RSI 40/50/60 or divergence on a chosen TF): design `research/rsi_deep_buy_2026-10-19/SPEC.md`; cards (raw, chained) `rsi-deep-depth-map` -> `rsi-deep-prereg` -> `rsi-deep-engine` (CODEX/GPT) -> `rsi-deep-run-dev` (DSA-NB) plus `rsi-deep-prob-tables`, `-context-tables`, `-confluence`, `-divergence-context`; OPUS_FRAMING.md in the same folder wins over SPEC where they differ (run its Stage 0 `rsi-deep-econ-floor` FIRST); Session_Planner refines them, Lab_Guy stamps, Gemini cross-reviews. Start with depth-map on a machine with the 1m klines.
- Lenovo (code/doc/registry only): ship STUCK commits after merging origin/fast-track (one ship at a time, `MTS_GATE_JOBS=2`): t02-f3 part a b9c448c7, t02-f1 chunk 3 f9497e45; then chunk 4 and t02-f3 b, c (`tasks.py check` promotes); close t02-f1 c2/c3, t02-f3 a with `tasks.py done`; `sync.py tidy --apply`.
- NUC: kurisko-quad-rotation chain (check trunk first), funding-carry (claim STALE 26h: release or take), rv05-h2/h3, indicator-values-multi-model-audit; GPT lab stalled 32 h (read last_tick.txt/last_lane.txt on the lab host).
- Any session signed in as jishusharma1985: republish Home 8hKA1rhNRo6RAEdt5mtLg3 (+ Research Map, Planner), still owed.
- Lab_Guy: review stamps for dsa-audit-02/03 so `tasks.py done` works.
- Release the stale NB claim `eu-low-us-sweep-follow-ups-long-after-sw` (34 h, blocked by the power gate).
Threads archived 2026-10-19 (clean trees): Fable run 1/2 briefs, live-read-router, Tandem 10-18 coordination, nb-planner-3, lenovo-guide, labguy-pass-b. Kept: pinned roles, Eagle_Eyes replacement, AWS AI services (idle), CBP analyst feed (Haiku 3x/day: SCHEDULING_POLICY check owed).

## Archived Hand-overs
Historical hand-overs from 2026-10-18 and 2026-10-19 (Lenovo coordinator, super session, layers wave 1, NB tandem, CI red fix, MTS_Doctor report) are archived in [2026-10-19_trim.md](handoff_history/2026-10-19_trim.md).
