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
CI: no run exists for the ship, by design: extracts/gemini_out/*.md is outside the ci.yml push paths. Latest push run 40165863178 success on 67426492d; 0 red since the pilot start (read by the Lead 2026-10-25).
Weekly: 44% start, 44% end (rounded; under 1 point). 5h window: 3% start, 7% end. Supervisor context 127k at end.

## Pass rows
1 All cards shipped: PARTIAL - 2 of 3 (H2 stale-dropped by design rule 6); cherry empty, Result: lines present. PASS for shipped ones.
2 Verifier 0 + review 0 unsupported: PASS (review sample small).
3 Gate median under 2 min: NOT SEPARATELY MEASURED (combined ship, whole call under 3 min incl. refusal retry).
4 CI <=1 red, 0 reverts: PASS - 0 reverts, 0 red (no CI run for the md-only ship, see CI line).
5 Weekly under 2 points, 5h under 60%: PASS (0 points visible, 7%).
6 Turns median under 25: FAIL on count (22 and 39 incl. 13-14 wasted on the block); after fix 8 and 21.
7 0 operator turns: PASS for the pilot work (stop-guard nags only).
8 Rework after 24 h: read later.

## What broke and the fix
1. start_session refused for a session-started supervisor turn, so workers were Agents: no model read-back, no per-worker context. Fix: let the operator start the supervisor (user turn) or add an allowed spawn path for the Supervisor role.
2. Agents are bound to the supervisor's worktree by the edit hook; their own `sync.py start` worktree is refused (each lost 13-14 turns). Fix: brief Agent workers to edit in the supervisor worktree from the start with explicit-path commits, or run them as sessions.
3. Shared tree forces one combined ship and sync.py's 10-min limit needs --again; scratch ship log cannot be deleted (rm denied) so stop guard nags.
4. F6 needs a verifier-convention card (thirds computed from body after first `# ---`).

## Addendum (Doctor request, from the agent transcripts)
- (a) Denial: both Agents ran with cwd `...\.claude\worktrees\blissful-antonelli-a1669c` (the supervisor tree; all 94 transcript cwd entries). `sync.py start p3h1/p3h3` printed WORKTREE `...\worktrees\mts-jis-nb-p3h1` / `mts-jis-nb-p3h3`; the first Edit/Write there was refused by the edit hook: "This session is running in an isolated git worktree at `...\blissful-antonelli-a1669c`, but `...\mts-jis-nb-p3h1\extracts\gemini_out\-dMWA_bbm3o_audit.md` belongs to a different worktree. Do not write to other worktrees' files from this session." Same text for p3h3 (gWjHq5UMisY_gemini.md). An Agent shares the parent session's worktree identity, so it can only write there.
- (b) Model confirmed from the transcript `message.model` field: H1 `claude-haiku-5-5` on 61 assistant records, H3 `claude-haiku-5-5` on 93; the single `claude-opus-5-5` hit in each is a tool-schema listing, not a reply. Commit trailers say Haiku 5.5 (self-written, not proof). Tool uses reported by the runtime: H1 14 + 8 = 22 (runs: 14, then 22 total reported 22), H3 18 then 39 total (runtime counts: H1 22, H3 39 cumulative incl. blocked runs). Subagent tokens (cumulative per run report): H1 93,331 then 106,304; H3 85,064 then 103,609.
- (c) H2 dropped: `tasks.py brief` showed `STATE STALE: scope changed 8e56554c1543 2026-10-24T23:12:02Z after refresh 2026-10-24T22:51:26Z`; that harvest commit rewrote 3 of H2's 9 notes (HUYBdYnXUNc, agjftXPkLUE, cLgdXZnLL_0), so its line references were no longer trustworthy (plan rule 6).
- Scratch ship logs (ship_sup1.log, ship_pilot3.log, ship_pilot3b.log) are committed beside the notes per Doctor, not deleted (rm was denied). Future scratch goes to the scratchpad dir.
