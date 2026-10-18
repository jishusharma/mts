# B184 - AIBridge: multi-block count over-reports, executes the first block and drops the rest

Source: DSA session MTS-2026-10-12-0952Z, direct mode on JIS-NB, 2026-10-12. Observed on AIRUN RESULT #1 and #2 in the same session, both single-block replies.

## Findings

F1. Multi-block count is wrong. Result #1 note: '2 other AIRUN block(s) in the same reply were NOT run'. Result #2 note: '4 other AIRUN block(s)'. Each reply carried exactly one fenced AIRUN block.

F2. Executes the first, drops the rest silently. On multi-block detection the bridge runs block 1 and drops the remainder with no structured error.

F3. cmd: echoes only the first line of the block.

F4. The multi-block check runs after the first block has executed. It should run before.

F5. Add blocks_seen and blocks_run to every result JSON.

F6. Bridge rule is 'one block per reply'; DSA_SESSION_PROMPT.md section 0.5 says 'one command per call'. Align.

## Note

Filed as B183; that id was taken by a parallel writer (session-start-ritual audit) between the read and the write. Renumbered to B184. The other B183 row is not mine.

## Plan

Owner: Claude (F:\AIBridge). Order: F4, F1, F5, F3, F6. Ship with tests under F:\AIBridge\src.

Related: B168, B176.

## Status 2026-10-14 (v0.7.0, payload in scripts/aibridge, installer scripts/dev/aibridge_install.py)

Shipped on JIS-NB (F:\AIBridge, agent restarted, answers /ping 0.7.0). NUC: desk task posted. Contract: scripts/aibridge/docs/V07_CONTRACT.md.
F1-F5: all blocks of a reply run in order (cap 6) with one receipt each, blocks_seen/blocks_run in every header, NOT RUN receipts for the rest.
Field reports 2026-10-12/14, bridge side: multi-line fidelity + lines/sha echo; deterministic fluent auto-run (only irreversible forms need a click);
rid echo + STALE_REPLY guard + no-store; PS 5.1 lint (ps7_only) + shell=pwsh; fresh registry env per command; child TEMP in run\tmp;
roots + Temp; GET /ping + labelled errors (extension_link vs agent_unreachable); start-agent.ps1 (-Watch); parallel chats
(per-page state, 500 ms worker tick for hidden windows, Web Lock, agent runs up to 8 commands at once); task mode (playbooks + inline plans).
Not mine: items 8-12 (Build-Check, DSA prompt) are the DSA-prompt session's claims. Not verified against live chat.deepseek.com DOM.
