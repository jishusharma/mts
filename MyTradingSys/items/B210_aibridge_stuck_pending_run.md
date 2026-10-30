# B210 - AIBridge stuck pending run (silent stall)

Filed: 2026-10-30 by DSA on JIS-NB.
Status: OPEN
Priority: MED
Fixer: Claude
Logger: Claude

## Symptom

- Panel shows running #NNN (block 2/2); the line under it shows running 0.
- Every later block returns no result and no error.
- Hands-free looks armed. Nothing in the chat shows a failure.

## Why it costs turns

Prompt section 0.7 covers extension_link and agent_unreachable. Both print an ERROR line, so a session knows to stop and report. A silent stall looks like a slow reply, so the session retries, which costs turns and leaves the operator to diagnose it.

## Recovery (works today)

1. Toggle Hands-free off, then on.
2. Reload the AIBridge extension at chrome://extensions.
3. Press F5 on the chat.

## Proposed fix

Extension: expire a pending run at twice the block timeout; on expiry ask the agent for its queue and release the lock with a visible reason (lock released after N s, nothing was running).
Prompt section 0.7: add the silent-stall mode and the three recovery steps above.
Test: replay a lost completion frame and assert the lock clears and the next block gets a receipt.
