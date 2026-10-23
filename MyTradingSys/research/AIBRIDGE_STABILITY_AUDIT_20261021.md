# AIBRIDGE STABILITY AUDIT - 2026-10-21 (JIS-NB)

This file tracks all observed AIBridge (v0.7.1) defects during the DSA session on JIS-NB.
Goal: use this log to write the final bug report for fixing the bridge.

## 1. Silent Drop of Task-Mode Blocks (Bug B195)
### Observation
The quick gate was sent three times via task=mts-gate. No result was posted. No refusal was posted. The block just vanished.
### Impact
The model waits indefinitely. The operator must manually intervene.
### Fix Needed
Acknowledge every task-mode send with a rid immediately. If it drops, post a receipt in the chat.

## 2. Auto-OFF on Operator Draft (Bug B196)
### Observation
The operator started typing a reply in the DeepSeek chat box. The extension detected the draft, failed its "idle" check, and silently turned hands-free OFF. The next block sat unrun with no receipt in the chat. Only a tiny status card showed the state.
### Impact
Operator typing breaks the automation. The model is blocked.
### Fix Needed
Ignore drafts in the input box. If auto-off must happen, post a chat-visible message, not just a status card.

## 3. "Stuck Waiting" State (Bug B196)
### Observation
The extension was armed (ticked) but the status card read "waiting for DSA after #48". The block sat unrun. It lost its place in the turn sequence.
### Impact
Silent stall. 
### Fix Needed
Timeout and re-sync or fail visibly.

## 4. Empty Block Receipts
### Observation
Sent two blocks with commands. Received "NOT RUN: the block has no command after the # AIRUN line. blocks_seen=2 blocks_run=0".
### Impact
The extension stripped the body before execution.
### Fix Needed
Investigate parsing robustness under load or rapid switching.

## 5. False Success from Task Runner (mts-ship)
### Observation
TASK mts-ship reported "TASK RESULT: PASS" while the gate step inside it explicitly printed "FAILED: 3 step(s)".
### Impact
Automation pretends things are green when they are red.
### Fix Needed
Task runner must fail if the gate fails. (This is an MTS tool bug, not the bridge, but breaks stability).

## 6. Stale and Replayed Blocks

### Observation
Two separate failures of the same family.

(a) Replay: a turn carrying 2 blocks had both blocks replayed from the previous turn on top of the current
2 blocks. The receipt read blocks_seen=4 blocks_run=4 for a 2-block reply. The two extra runs were an old
dsa.py put and an old commit, so a commit ran twice.

(b) Out of order and late: in a 2-block turn the second block (a git log, rid -24) returned first; the first
block (sync.py release, rid -23) returned about 30 minutes later, after later turns had already been sent.

(c) Silent drop on the release: the same release block was sent, produced no result, was re-sent by hand,
and only the manual run came back. The desk row also showed one ship that was never receipted.
### Impact
Commands are executed out of order and from history. A destructive command could be re-run.
### Fix Needed
The extension must track the turn ID (or block hash) and refuse to execute any block that does not belong to the latest DSA message. If a block is stale, post a visible receipt "STALE_REPLY_DROPPED" and wait for the new block.

## 7. Ambiguous Ship State

### Observation
A task=mts-ship block produced no result at all. Later, sync.py ship run by hand reported "shipped 25 file(s)".
Whether the earlier task-mode ship ran invisibly, was refused, or never started could not be told from the chat
or from disk. No receipt, no log id, no way to distinguish.

### Impact
The operator cannot tell a slow ship from a lost one, and a repeated send risks a double push.

### Fix Needed
Task-mode blocks write a run id to the chat the moment they are accepted, and the agent logs one line per
task-mode send with accepted/refused and the reason.

## Summary - what makes DSA unstable today

1. A block can vanish with no receipt (B195). Every long stall in this session traced to this.
2. Hands-free turns itself off or strands itself, and says so only on a small status card (B196).
3. Blocks are replayed from history and results return out of order and late (this file, 6).
4. Empty bodies reach the agent as "no command after the AIRUN line".
5. Task runners report PASS over a red gate (mts-ship, MTS tool not the bridge).

The first three are the same root: the extension does not tie a block to one turn, and it does not
acknowledge acceptance. A per-turn id, an ack on accept, and a receipt on every non-run would remove all
three.
