# Why sessions don't behave as expected after fixes (MTS doctor, 2026-10-23)

Verdict: fixes ship to trunk but don't reach the hooks that run. Every session's hooks run from the JIS-NB main checkout. At the time of this audit that checkout (`fast-track` @ f22763caa, 2026-10-22T12:57Z) is **195 commits behind** origin/fast-track (trunk 5cc20d877). Nothing moves it forward on its own.

## Proof (run this turn)
| Check | Result |
|---|---|
| `git rev-list --count HEAD..origin/fast-track` in the main checkout | 195 (it was 102 in REPORT_2026-10-22) |
| `SubagentStart` in the main checkout's `.claude/settings.json` | 0 hits; trunk has it (commit f3ac1d6c0) |
| Hook-wired files that differ between the main checkout and trunk | 10 files, 28 fix commits not live: settings.json 6, role_loader 4, model_guard 4, turn_meter 4, trunk_lag 4, mts_signal 2, ci_watch 1, offer_guard 1, preship 1, shot 1 |
| `trunk_lag` hook (the lag warning) in the main checkout's settings | 0 hits, so the warning about lag is itself not live |
| Would `pull --ff-only` collide with the main checkout's 54 dirty files (48 untracked, 5 deleted, 1 modified)? | No overlap with the 195-commit diff, so a fast-forward is clean |
| Cards for the pull | `doctor-main-checkout-behind` (2026-10-22) and `jis-nb-fast-forward-the-main-checkout-to` (2026-10-23) are duplicates. Neither has a status or owner, and neither was done |

## Supervisor claims on the Thinker banner fix, re-checked
| Claim | Result |
|---|---|
| Cause: no SubagentStart hook, so background Agents get no role | CONFIRMED. Docs (code.claude.com/docs/en/hooks) list SubagentStart; its payload is `agent_id` + `agent_type` only, with no prompt |
| The fix injects text | CONFIRMED in part. The handler returns valid `hookSpecificOutput.additionalContext`, which the docs allow. For a `general-purpose` agent it is a one-line self-load pointer, not the role file. Helper types (Explore etc.) get nothing (0 bytes, probed) |
| 47 passed with the fix, 5 failed on old code | REPRODUCED in a clean worktree of trunk 5cc20d877: 47 passed; with role_loader from f3ac1d6c0~1, 42 passed and 5 failed (all `TestSubagentStart`) |
| Fix is on trunk | CONFIRMED: f3ac1d6c0 is in origin/fast-track and origin/green/fast-track |
| "Settings are read at session start; restart needed" | NOT SUPPORTED. The docs say hook edits in settings files are normally picked up by the file watcher. A restart may not be needed once the main checkout is pulled; unverified on this build |
| Live probe `HOOK TEXT ABSENT` "as expected" | CONFIRMED. The cause is the main checkout lag above, not the fix |

## Second misbehaviour seen this turn
The role loader's fallback keyword match picked Lab_Guy for this audit because the prompt said "revalidate" (`revalidat` is a Lab_Guy trigger word). One common word can switch a session's role mid-conversation.

## Fix order
1. Fast-forward the main checkout: `git -C C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed pull --ff-only` (operator or coordinator; clean, see above). This one step makes all 28 fixes live.
2. Rerun the Supervisor's probe: a background Agent whose brief starts `You are Thinker.` must answer with a `ROLE LOADED` line.
3. Close the duplicate card; make the lag fail loud: card `hook-lag-gate`.
4. Card `role-fallback-common-words`: drop generic words like `revalidat` from fallback triggers, or require 2+ hits.

## Fix applied and proven (2026-10-23, operator go)
- `git -C <main checkout> pull --ff-only`: f22763caa -> 30ee53be5, 0 behind; `SubagentStart` now in the main `.claude/settings.json`; its 54 uncommitted files untouched.
- Probe: a background `general-purpose` Agent with brief `You are Thinker.` replied `ROLE LOADED: Thinker v2 · token duck-nail · ... @ 30ee53be`.
  Its transcript (`subagents/agent-a5fa34625a737606f.jsonl`) shows the hook fired, independent of the agent's own claim: line 1 `hook_success` hookEvent=SubagentStart,
  line 2 `hook_additional_context` with the ROLE LOADER pointer, line 15 the system message "SubagentStart hook additional context: ROLE LOADER (hook) ...".
- No restart was needed: this session started before the pull and the next agent got the hook (the "restart needed" claim is wrong).
- What it does not give: the role file itself. The agent receives a pointer and reads the file (one extra tool call), because SubagentStart carries no brief text.
- Cards `doctor-main-checkout-behind` and `jis-nb-fast-forward-the-main-checkout-to` dropped (done by hand). `hook-lag-gate` stays: the lag will come back without a gate.
