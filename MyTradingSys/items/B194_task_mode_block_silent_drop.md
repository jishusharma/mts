# B194 - task-mode gate block silently never ran; three sends, no receipt and no refusal

Opened 2026-10-21 | Status OPEN | Severity HIGH | FIXER: Claude (Sonnet lane) | LOGGER: DSA
Source: DSA chat MTS-2026-10-20-1818Z-DSA-BLD on JIS-NB, worktree mts-dsa-jis-nb-1020-1822.

## What happened

The quick gate was sent three times as a single task-mode block:

    # AIRUN task=mts-gate repo=C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nb-1020-1822 timeout=1200

Each send produced no [AIRUN RESULT] in the chat and no [AIRUN BATCH] header. There was no refusal line, no NOT RUN line, no manual_click_required, no timeout message. The operator saw the replies leave and asked twice whether the block had run. It had not.

Timeline (UTC, from this chat):
- 18:25:51 result #41, last ordinary result before the gap.
- gate send 1 and send 2: no result at all.
- 19:02:57 result #43: no cicd_run receipt file exists in MyTradingSys/runtime.
- 19:02:57 result #44: no gate python process running (one unrelated python 19548, started 23:41 local).
- gate send 3: again no result.

## Proof

- Result #43: listing MyTradingSys/runtime for cicd_run_2026-10-2* returned nothing; Get-Date returned 2026-10-21T00:32:57+05:30 (19:02:57Z). No gate run wrote a receipt.
- Result #44: Get-Process python listed only pid 19548 (started 23:41 local, about 2963 s CPU), not a gate.
- Two plain-block batches sent in the same window (results #43, #44) ran normally with blocks_seen=2, so the bridge was alive while the task-mode sends vanished.

## Why it matters

A task-mode block that is neither run nor refused is worse than a refusal: the operator cannot tell a slow run from a lost one. The prompt tells the model to say "no result seen" and wait; the human side gets no such signal, so three identical presses looked like the operator repeating himself.

## Focus evidence (2026-10-20 20:17Z, JIS-NB)

Operator asked whether AIBridge stops running blocks when the chat tab is not focused. Test: one block slept
25 s while the operator worked in another window. Result #17 returned both lines (start 2026-10-21T01:46:56+05:30,
end 01:47:21, run_ms 25320) with no refusal. An unfocused tab does not stop a block or lose its result, so the
lost task-mode gate send is not a focus effect. The gap is receipt.

Second defect seen 2026-10-20 20:26Z: two blocks sent with a command each arrived with an empty command line.
Receipt: "blocks_seen=2 blocks_run=0 not_run=2 ... NOT RUN: the block has no command after the AIRUN line"
(results #19, #20). So a block can reach the agent with its body stripped; nothing ran and nothing else said so.

## Root cause seen 2026-10-20 20:30Z (operator screenshot, not saved: chat has no disk)

The extension card read: "auto OFF - the result was not posted (the chat never became idle (or an operator
draft sits in the input)). Tick the box again to re-arm. agent 0.7.1 on JIS-NB, PowerShell 5.1, running 0".
The block below it sat unrun with an unclicked Run button. So hands-free turned itself off when its idle
check failed, said so only on a small status card, and left the chat with no receipt at all. Every later
block then waited unrun; two of them came back as "the block has no command after the AIRUN line", which is
the same failure: the body is parsed away once the auto path is off.

## Focus evidence (2026-10-20 20:17Z, JIS-NB)

One block slept 25 s while the operator worked in another window. Result #17 returned both lines (start
2026-10-21T01:46:56+05:30, end 01:47:21, run_ms 25320) with no refusal. An unfocused tab does not stop a
block or lose its result, so the lost gate send is not a focus effect.

## Fix shape

In the AIBridge extension and agent (F:\AIBridge, Claude only):
1. Immediate ack for every task-mode send (task accepted, rid) before the playbook starts.
2. A screened-out, refused, dropped or superseded task-mode block returns a receipt with the reason (screen_refused / duplicate_rid / busy / stale), never silence.
3. The extension answers a duplicate send of the same task+repo with the first run's rid instead of starting a second.
4. One bridge log line per task-mode send: rid, playbook, repo, accepted|refused, reason.
5. When hands-free turns itself off, it posts a chat-visible line in the same reply slot as a receipt, naming the
   reason and how to re-arm. No small status card only. A block left unrun by auto-off gets that same line.
6. An operator draft in the input box must not disable the auto path: the extension runs the block as posted and
   leaves the draft alone.
7. Auto-off re-arms on the next successful operator send or click, without a separate tick.

## Done when

A second task-mode send while one is live returns the live rid in the chat; a screened-out task-mode block returns a refusal receipt; the bridge log carries one line per task-mode send. Reproduced with a deliberate double send, receipt quoted in this item.

## Not the fix

Pressing the block again by hand. That worked around it once and cost the operator three waits.
