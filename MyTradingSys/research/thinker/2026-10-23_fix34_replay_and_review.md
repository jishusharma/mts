# Fix #3/#4 (role-line detection): replay test + independent review, 2026-10-23

Status: the Builder shipped 9f0cb459c before this check finished (the Supervisor's hold message was blocked by model_guard,
root cause #2). The review below found false positives in that shipped code. It is NOT accepted.

## Replay test (real data, old HEAD code vs the new code)
Script: every first user message of 784 real transcripts in `~/.claude/projects/*/*.jsonl` through the old and new
`transcript_starts_supervisor` and `match_roles`. Independent truth = a line starting `You are Supervisor` in the first 4000 chars.
- turn_meter Supervisor detected: old 3, new 7, truth 6. New misses vs truth: 0. One new detection with truth=False:
  `C--Users-E-ngineers-IdeaProjects-BinanceDataFeed/fa50b45d*.jsonl` (must be inspected: possible false exemption).
- role_loader changed on 10 transcripts. 8 look right (Lab_Guy, Thinker, Eagle_Eyes, Session_Planner, 1985Artifacts_Guy now
  load behind wrappers). Two need a verdict:
  - `You are Supervisor. Login C. Two hours, simulator desk...` now matches Supervisor AND Session_Planner (old: Supervisor only).
  - `Operator request (verbatim intent, 2026-10-20): "What about a thinker? ...` now loads Thinker from a quote.

## Independent review (Sonnet, diff only, each finding reproduced with python)
1. Worker escapes its turn cap: a `You are Supervisor.` line anywhere in the first 6 lines counts, including inside
   `<cross-session-message>`, `<task-notification>`, `<pasted_content>`, or "Example start line below:\nYou are Supervisor."
   Fix: only the first non-empty line after clean(); skip EVENT_PROMPTS text; `_user_texts` takes only the first user entry.
2. Regex does not require the line to end: "You are the supervisor of nothing; review code." matches.
   Fix: end with `[ \t]*(?:[.:!]|$|\s+Login\b)`; add `-` to the lookahead.
3. Sticky `is_supervisor_start` runs on every prompt: a later pasted line sets role=supervisor for good and overwrites thinker.
   Fix: set only when no role is set yet and it is the first user prompt.
4. Paste tags are stripped, so a pasted role line counts (probably intended, but see 1).
5. False negatives (not regressions): `Task:\r\n` (CRLF), `Task: You are X.` on one line, `**You are Supervisor.**`.
6. A first line over 200 KB returns False (not new).
7. `turn_meter.py` top-level `import role_line` has no soft fallback: a missing file breaks the hook.
</content>
</invoke>
