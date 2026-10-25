# Pilot 3 results (Haiku workers, 2026-10-25, Supervisor pilot3_sup, login C)
Plan: PILOT3_HAIKU.md. Run 05:46Z-06:00Z (about 14 min). Two workers, not three: H2 dropped as stale (card scope changed by 8e56554c1 after its refresh).

| | H1 audits | H3 Tom extracts | H2 |
|---|---|---|---|
| Model | haiku (Agent `model` param; get_session read-back impossible: start_session refused) | same | not run |
| Context start/mid/end | NOT MEASURED (Agents have no get_usage context); subagent tokens 93k + 106k cumulative over 2 runs | 85k + 104k | - |
| Tool turns | 14 blocked run + 8 resumed = 22 | 18 blocked + 21 resumed = 39 | - |
| Minutes | about 8 | about 8 | - |
| Verifier exit | 0 on both audits (supervisor re-ran) | 0 on all 7 (supervisor re-ran) | - |
| Review | Sonnet Agent, 3 sampled lines + REJECTED entries: SUPPORTED (1 footer line untestable, "73 words" not recounted, item-8 REJECTED entry unchecked) | not sampled (H1 clean); supervisor hand-checked both F5 quotes in transcript_gWjHq5UMisY.txt (split across caption lines 14-15, 186-188): found | - |
| Scope (the diff stat) | 3 files, in scope | 4 files (3 extracts + FIXES_APPLIED_tom.md), in scope | - |
| Deferred | none | F6 (9 GPS tags): re-tagging breaks verifier thirds convention; needs verifier card | - |

Ship: ONE combined ship of both commits (ece3e75ff, 38dfe0116) from the supervisor tree: exit 0, "shipped 8 files", `git cherry origin/fast-track` empty. First attempt refused by sync.py (second ship within 10 min; used --again, legit batch). Gate wait: ship command total under 3 min (not timed separately).
CI: latest success before ship; CI run on the ship commit read at end of notes below.
Weekly: 44% start, 44% end (rounded; under 1 point). 5h window: 3% start, 7% end. Supervisor context 127k at end.

## Pass rows
1 All cards shipped: PARTIAL - 2 of 3 (H2 stale-dropped by design rule 6); cherry empty, Result: lines present. PASS for shipped ones.
2 Verifier 0 + review 0 unsupported: PASS (review sample small).
3 Gate median under 2 min: NOT SEPARATELY MEASURED (combined ship, whole call under 3 min incl. refusal retry).
4 CI <=1 red, 0 reverts: 0 reverts; see CI line.
5 Weekly under 2 points, 5h under 60%: PASS (0 points visible, 7%).
6 Turns median under 25: FAIL on count (22 and 39 incl. 13-14 wasted on the block); after fix 8 and 21.
7 0 operator turns: PASS for the pilot work (stop-guard nags only).
8 Rework after 24 h: read later.

## What broke and the fix
1. start_session refused for a session-started supervisor turn, so workers were Agents: no model read-back, no per-worker context. Fix: let the operator start the supervisor (user turn) or add an allowed spawn path for the Supervisor role.
2. Agents are bound to the supervisor's worktree by the edit hook; their own `sync.py start` worktree is refused (each lost 13-14 turns). Fix: brief Agent workers to edit in the supervisor worktree from the start with explicit-path commits, or run them as sessions.
3. Shared tree forces one combined ship and sync.py's 10-min limit needs --again; scratch ship log cannot be deleted (rm denied) so stop guard nags.
4. F6 needs a verifier-convention card (thirds computed from body after first `# ---`).
