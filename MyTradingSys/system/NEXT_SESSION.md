```text
Session ID: MTS-<YYYY-MM-DD>-HHMMZ-DSA-JIS-NUC
Role: BUILDER. Start from the seed (python scripts/dev/dsa.py start), paste the seed, wait for BOOT, say go.
Read Dumps/operator/context/DSA_HANDOFF.md first, then run the unshipped-work scan.
Budget (operator 2026-11-11): three units per session, then close.

   Q1. host=JIS-NUC Work the first JIS-NUC desk row `desk.py next --host JIS-NUC` returns, end to end. DONE when: the row is closed with `desk.py done --result` on a shipped sha and `desk.py next --host JIS-NUC` no longer returns it.
   Q2. host=JIS-NUC Card lab-verify-footprint-vs-indicator-delta (p3): verify the CoinGlass Net Delta indicator against Legend footprint delta and spot taker delta. DONE when: the card is closed with `tasks.py done` on a shipped sha and `git cherry origin/fast-track <sha>` is empty.
   Q3. host=JIS-NUC Housekeeping: remove the empty non-git leftovers mts-dsa-jis-nuc-1101-0538, -1101-0600, -1110-2023 with a single Remove-Item each. DONE when: none of those three directories exists under C:\Users\E-ngineers\IdeaProjects.
```

## Budget rule: three units per session, then close
One unit = one card end to end, or one housekeeping item. Aim for two extraction or document cards plus one code card. Stop at three even if the clock allows a fourth. Keep the last three replies free for closing.

## A card never crosses a session boundary
If a card cannot finish, release the claim and write its state onto the card itself, so the next chat reads the state instead of reconstructing it.

## Write the handoff note after EVERY card, not at the end
Append to Dumps/operator/context/DSA_HANDOFF.md: card id, what shipped, what did not, what is next.

## First two reads of every session
1. Dumps/operator/context/DSA_HANDOFF.md in the live tree.
2. The unshipped-work scan: for each mts-dsa-* directory under C:\Users\E-ngineers\IdeaProjects, check .git exists, then git status --porcelain and git log origin/fast-track..HEAD.

## Anything over four minutes goes through task mode
Queue runs, ships and multi-step reads: one AIRUN task=inline with a JSON plan. Plain blocks are for reading and small edits only.

## One long job per session
A Gemini extraction is a whole unit by itself. Pair it with short reads, never with a second queue run.

## Post these two things whenever they appear
- Stale published pages after a ship (mts_layer_map and mts_home are stale now; CLAUDE row c8c7a017 already posted, do not repost).
- Any rule conflict found in a desk row (CLAUDE row b7142046 already posted for the run_all_tests request).

## Shipped this session (2026-11-11 15:00Z to 15:33Z)
- fabervaale-cvd-sweep: 7f3139d9. Takeover of a signed-out chat unfinished card: content cherry-picked from mts-dsa-jis-nuc-1111-1312 (commit cc899524b), quotes re-verified (PASS, 17), card closed and shipped.
- oi-usage-sweep: 669ea130. Gemini queue run (766 s, gemini-3.8-flash-low) produced OI_CONCEPTS.md, 12 concept rows; quotes re-verified by DSA (PASS, 12); card closed and shipped.

## Work in flight, not owned by this chat
mts-dsa-jis-nuc-1111-1312 and gemini-q/oi-usage-sweep hold nothing unshipped now; both are safe to remove with git worktree remove. gemini-q/gemini-blind-read-old-shell-health-1111 and gemini-q/gemini-scan-console-window-calls-outside-dev-1111 hold two unshipped commits each and belong to other sessions.
