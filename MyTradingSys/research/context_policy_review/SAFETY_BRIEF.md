Safety review (operator 2026-10-21, read-only: edit nothing except your own SAFETY_<model>.md, commit nothing, start nothing).

Operator's fear: "any session can misbehave and drink all my data" (usage allowance). Today's changes: typed prompts are never blocked,
compaction never blocks, sessions the operator drives (2nd typed prompt onward) get no hand-off nag, Fable has no cap, Supervisor is capped
by context only, caps/notices are now silent to the operator. Code: scripts/dev/turn_meter.py (handle(), caps(), tier(), is_event_prompt()),
MyTradingSys/tests/test_turn_meter.py, hooks wiring in .claude/settings.json (main checkout C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed),
other guards: scripts/dev/stop_guard*, model_guard*, MyTradingSys/system/WORKERS.md rule 5, SUPER_SESSION.md.

Task: list every way a session (worker, child, Supervisor, subagent, runaway loop, operator walked away, 3 devices) can now burn usage
unbounded that was bounded before, or never was bounded. For each: concrete trigger, what stops it today (file:line) or nothing, cost, fix
that does NOT block a typed operator prompt. Run the tests yourself. Do not trust commit messages.
Output: MyTradingSys/research/context_policy_review/SAFETY_<YourModel>.md, max 40 lines, plain words, severity HIGH/MED/LOW per item.
