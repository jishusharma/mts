# His own first ask counts as "he is here" (turn_meter option A)

Operator 2026-10-23: "yes - do it - and revalidate eveything once done - test it - stress test it - list scenarios of edge cases - but use quota wisely now"

## Fact
- `scripts/dev/turn_meter.py:306` `state["driven"] = int(state["user"] >= 2)`: a session is attended only from his 2nd typed prompt.
- 2026-10-23 JIS-NUC "NUC shutdown diagnosis": his one typed ask ran as unattended, hit the 1M read budget, web search and the
  NEXT_SESSION.md read were denied, and it handed over half done. Same class as the Thinker case (turn_meter.py:42-44).
- The Thinker could not make this edit: the auto-mode classifier denies a session editing its own turn limiter (Self-Modification).
  A builder session (another session) makes it.

## Patch (spec; builder applies, tests first)
1. turn_meter.py, after `def is_event_prompt`:
```python
BRIEF_START = re.compile(r"^\s*(?:you are|you're|act as|i need an?|role:)\s", re.I)


def briefed(prompt):
    """True when a first prompt is a worker brief, not his own ask: a brief another session sent (role_loader.from_session) or a
    `You are <Role>` start line, which coordinators paste into workers. Operator 2026-10-23 (Thinker option A)."""
    p = LEADING_REMINDERS.sub("", str(prompt or ""), count=1)
    try:
        import role_loader
        sent = role_loader.from_session(p)
    except Exception:
        return True         # cannot tell: capped, as before
    return sent or bool(BRIEF_START.match(p))
```
2. UserPromptSubmit: `state["driven"] = int(state["user"] >= 2 or not briefed(payload.get("prompt")))`.
3. Docstrings: `attended` and the DRIVEN_IDLE comment say "his typed prompt (2nd, or a 1st that is not a brief)".

## Tests (MyTradingSys/tests/test_turn_meter.py, class AwayFlagAndAtomicSaveTest; must fail on the old code)
- `test_a_worker_past_the_unattended_budget_is_nagged_then_stopped`: prompt "fix the gate test" becomes briefs:
  "You are Builder. Card: ...", "Background (from the session that started this one): ...", "<system-reminder>x</system-reminder>I need a builder: ...",
  "<cross-session-message ...>" -> all denied; "You are Builder" still gets the half-way nag.
- `test_his_own_first_ask_runs_to_the_end_while_he_is_there` (NEW, fails on old code): the NUC ask, the same after a leading
  `<system-reminder>`, "  fix the gate test" -> 5 Opus 300k turns, no nag, PreToolUse WebSearch allowed, attended() true.
- `test_his_first_ask_left_alone_past_30_min_is_capped_again` (NEW): typed_at 31 min ago, 5 turns -> WebSearch denied; a
  task-notification after that does not make him there.
- `test_briefed_edges` (NEW): briefs: "You are Builder.", "you're the supervisor", "Act as reviewer", "I need an auditor", "role: Builder",
  "Another Claude session asked: x"; not briefs: "you know the NUC keeps dying", "Your task: fix x", "youre late", "fix all",
  "i needed this yesterday"; role_loader import broken (sys.modules None) -> True.
- Unchanged and still green: thinker uncapped, "you are thinking too slowly" denied, event 5/40 min tests.

## Edge cases (stress list)
| # | Case | After A | OK? |
|---|---|---|---|
| 1 | His plain first ask, he walks away | free for 30 min, then 1M read budget, then hand-off | yes: the ask gets 30 min + 1M |
| 2 | Coordinator start_session brief ("Background (from the session...") | capped, as before | yes |
| 3 | Worker brief starting "You are Builder" (pasted by him or a Supervisor) | capped until his 2nd prompt, as before | yes (conservative) |
| 4 | Cross-session / task-notification / CI event as 1st prompt | event, never counted (is_event_prompt) | yes |
| 5 | Leading system-reminder then his words | stripped, counts as his ask | yes |
| 6 | Headless `claude -p` launchers (run_worker.py, nuc_wake.py, dispatch_gate.py) with a plain prompt | 30 min uncapped | RISK, bounded: each runs with --max-budget-usd; no schedulers run them (SCHEDULING_POLICY.md). Follow-up if wanted: launchers prefix "You are <Role>." |
| 7 | Background Agent subagents | is_subagent: meter skips them | yes |
| 8 | role_loader import fails | treated as brief: capped (fail closed) | yes |
| 9 | Resume/compact of an old session | state file keeps driven/typed_at; window still 30 min | yes |
| 10 | "you are thinking too slowly..." (his words, starts like a role line) | capped until 2nd prompt | acceptable false positive (old behaviour) |
| 11 | Supervisor start line | role=supervisor, 6M budget, briefed -> as before | yes |
| 12 | Thinker | uncapped_role, unchanged | yes |

## Revalidate after ship
`python -m pytest -q MyTradingSys/tests/test_turn_meter.py MyTradingSys/tests/test_model_guard.py scripts/dev/test_mts_signal.py`;
`git stash` the patch once and confirm the 3 NEW tests fail; then the next operator-typed session on any machine runs past 1M without a hand-off.
