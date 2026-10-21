# Context load at session start: measured, then trimmed (2026-10-21)

**Verdict:** the coordinator's hypothesis holds. Role files are small; the cost is the big hand-over doc that every session reads. Splitting roles into chunks would add turns and save almost nothing, so it is NOT done.

## Measured (302 local transcripts with a boot read in the first 25 tool calls; token = chars/4)
| File | Size before | Sessions that read it (of 302) | Verdict |
|---|---|---|---|
| NEXT_SESSION.md | 29.0 KB (~7.3k tok) | ~85, avg 12k chars returned (many cut with `head`) | **shrunk** to 11.0 KB (~2.7k tok) |
| SUPERVISOR.md | 15.1 KB (~3.8k) | every Supervisor boot (role said "read first") | **shrunk** to 10.0 KB (~2.5k) |
| SUPER_SESSION.md | 18.5 KB (~4.6k) | Supervisor boot | **leave**: its Boot facts section is the part the role asks for, and a doc test pins its structure; splitting adds a turn |
| RELAY.md | 14 KB | 9 sessions, all pre-retirement | leave (retired path) |
| STATUS.md, ANNOUNCEMENTS.md | 6 KB each | ~17 / most | leave: already short and needed |
| roles/*.md | 1.5-10.6 KB (0.4-2.7k tok) | one per session | **leave**: under 4 % of the fixed ~70-80k per-turn context |

Role reading bug found: `roles/supervisor.md` said "Read first" SUPER_LOOP + SUPERVISOR + SUPER_SESSION (~39 KB, ~9.7k tok) and, two sections later, "Boot: read ACTIVE announcements and Boot facts, nothing else". The first line won in practice. Now it says the boot reads only what Boot step 3 names.

## Changed (no new gates, no new rule docs)
1. NEXT_SESSION.md: blocks dated 2026-10-18/19 moved verbatim to `system/handoff_history/2026-10-21_next_session_trim.md`; one pointer line left. 8 blocks archived, 7 remain.
2. SUPERVISOR.md: history sections (measured overhead, SV1-SV6 table, Astra review) moved verbatim to `system/handoff_history/supervisor_design_history_2026-10-18.md`; operating rules untouched. Build cards stay.
3. roles/supervisor.md: contradictory "Read first" line replaced; token refreshed with `role_loader.py retoken`.

## Saved per session (tokens in context; every turn re-reads them, at cache-read price)
- Any session that reads NEXT_SESSION.md whole: about 4.6k tokens.
- Supervisor boot: about 4.6k (NEXT_SESSION) + 1.3k (SUPERVISOR.md) + about 4k (no longer reads SUPER_LOOP/SUPER_SESSION in full unless a question needs them) = up to ~10k, about 12 % of the fixed per-turn context. Over 50 turns that is ~0.5M cache-read tokens per Supervisor; estimate, not re-measured.
- Extra turns added: 0.

## Left / next
- NEXT_SESSION.md will regrow; the rule is "archive finished blocks at hand-over" (existing practice, no new check). Sessions should `grep -n '^## '` and read only their block.
- SUPER_SESSION.md "Audit of the first one" (3 KB) is history; moving it needs a doc-test edit; skipped as low payback.
- Fixed per-turn cost (tools 39k, connectors 26k) dwarfs all of this; the biggest lever is fewer connectors/tools per session, which is a settings change for the operator, not a doc change.

DECISION (OURS): chars/4 as token estimate; archived blocks by date (2026-10-18/19), not by "finished" status, because the task queue (`tasks.py`) holds the open work and nothing is deleted.
Method: transcripts read locally and read-only; no transcript content is stored here.

## Context leaks fix (2026-10-21, session context-leaks)
Cause: Claude Code cuts hook-injected text at 10,000 chars; `role_loader.py` adds ~1.1k of banner/header, so a role file over ~8.9k lost its tail.

| Role (emitted chars) | Before | After |
|---|---|---|
| Session_Planner | 11,714 (about 1.7k cut off) | 8,837 |
| Pipeliner | 9,679 | 8,533 |
| Thinker | 9,561 | 7,983 |
| others | all under 9,000 | unchanged |

Moved, not deleted: Session_Planner refinement steps, CRITICAL protocol, unblock cases; Pipeliner Job 2 lines; Thinker scan commands. They live in `MyTradingSys/system/role_details/<role>_details.md` and the core file names the section to read at that step. DECISION (OURS): details sit outside `roles/` because the loader treats every file in `roles/` as a role (a details file there fails the header check). Guard: `test_every_role_emits_under_the_hook_cap` (< 9,500 emitted per role).

Per-turn hook text on a quiet turn (measured by running each hook): shot 0, turn_meter 0 (until its cap), mts_signal 0 (only unseen signals), ci_watch 0 (green), c_drive_guard 0, role_loader reminder ~236 (was every prompt). Repeaters: role_loader reminder (fixed: now every 6th prompt, saves ~200 chars/turn after the first), ci_watch ~236 each prompt while CI is red (kept: it is the stop signal), turn_meter ~235 each prompt past its cap (kept: intentional nag).

Not changed (operator side): `.claude/settings.json` has no `alwaysLoad`, no `ENABLE_TOOL_SEARCH=false`, no MCP servers. Loaded per session from the app: claude-in-chrome and computer-use (their instruction blocks, several k chars, load every session), scheduled-tasks, mcp-registry, visualize, terminal, ccd_*. Workers never use: claude-in-chrome, computer-use, mcp-registry, visualize, scheduled-tasks (no schedulers allowed). Switch these off in the app's connector/MCP settings for worker logins; keep ccd_session*, ccd_sidebar, ccd_pr, terminal.

Known, not mine: `supervisor.md` has no `Read first:` line, so 3 role-lint tests fail on trunk.
