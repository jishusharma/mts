# BLOCKED ? gpt-spec-tests-live-confluence-feed-1104

## What was checked

- `MyTradingSys/system/LAYER_LAB.md`, Scope: the lab scope excludes the live path; the live-path rules identify `layers/alerts/` as live-path code.
- `MyTradingSys/backtest/layers/alerts/live_confluence_feed.py`: the requested feeder is under `layers/alerts/` and imports RSI divergence code for live use.
- `MyTradingSys/tests/test_live_confluence_feed.py`: NOT_IN_DATA in this checkout; attempting to read the requested path returned file-not-found.
- The read-only context pack confirms the task targets this feeder and requests test additions there.

## Finding

| Severity | Evidence | Result | Proposed resolution |
|---|---|---|---|
| HIGH | `MyTradingSys/system/LAYER_LAB.md`, `## Scope` excludes the live path; `MyTradingSys/backtest/layers/alerts/live_confluence_feed.py` is in `layers/alerts/`. | MISMATCH: the task's specified build target is explicitly outside this lab's permitted scope. No test or feeder files were changed and pytest was not run. | Reclassify/assign this card to a workflow authorized to test live-path code, then restore/provide `MyTradingSys/tests/test_live_confluence_feed.py` if still absent in that checkout. |
| LOW | Requested test path `MyTradingSys/tests/test_live_confluence_feed.py` could not be opened (file-not-found). | NOT_IN_DATA in this checkout. | Verify the path in the authorized worktree. |

## Follow-up cards

None created. Card remains open per instruction for BLOCKED results.
