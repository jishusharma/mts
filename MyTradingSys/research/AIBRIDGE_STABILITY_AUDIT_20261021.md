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
