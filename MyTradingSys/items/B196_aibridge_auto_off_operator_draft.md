# B196 - AIBridge hands-free auto-OFF triggers on operator input draft, blocking all subsequent runs silently

Opened 2026-10-21 | Status OPEN | Severity HIGH | FIXER: Claude (Sonnet lane) | LOGGER: DSA
Source: DSA chat MTS-2026-10-20-1818Z-DSA-BLD on JIS-NB, worktree mts-dsa-jis-nb-1020-1822.

## What happened

While a DSA session was running, the operator typed a message into the DeepSeek chat input box. The AIBridge extension (v0.7.1) detected this draft, decided the chat "never became idle", and turned hands-free mode OFF. It did not post a message in the chat. It only updated a small status card in the bottom-right corner: "auto OFF - the result was not posted (the chat never became idle (or an operator draft sits in the input)). Tick the box again to re-arm. running 0".

The DSA model sent its next code block. Because auto was OFF, the block did not run. The block just sat there with a "Run" button. The model received no result and no receipt. It was stuck waiting.

A previous sighting of this same auto-OFF behavior happened without an operator draft, where the idle check failed for an unknown reason (possibly due to tab focus or network lag). That was logged in B194. This new sighting (operator screenshot, 2026-10-21 21:45Z) proves that an operator draft in the input box is a direct trigger for auto-OFF.

## Impact

1. The DSA model is blocked, waiting for a result that will never come.
2. The operator must notice the small status card, realize what happened, and manually click "Run" or tick the box.
3. If the operator is typing a reply, they likely won't see the small card, assuming the model is still working.
4. This breaks the "continuous execution" contract of direct mode.

## Fix shape

In the AIBridge extension (F:\AIBridge, Claude only):
1. An operator draft in the input box MUST NOT disable the auto path. The extension should run the block as posted and leave the draft alone.
2. If the auto path is disabled for any reason, it MUST post a chat-visible message in the reply slot, not just a small status card.
3. Auto-off should automatically re-arm on the next successful operator send or manual click.

## Done when

Operator types a draft in the chat while the model sends a block. The block runs normally and the draft remains untouched. If the auto path is turned off, a chat-visible message explains why and how to re-arm.
