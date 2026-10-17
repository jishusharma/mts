# Operator guide log (NB, jishu.sharma)

## 2026-10-17 progress

- Step 1 (context baseline, jishu.sharma): Claude Docs and visualize show disabled in this session. Computer use, Claude in Chrome and the 9 skills not yet confirmed by the operator.
- Step 2 (DSA bridge): repo extension copied to F:\AIBridge\extension (background.js TOKEN line kept, backup background.js.pre_keepalive). Operator reloaded AIBridge; the link dot shows after "Hands-free" and is filled (operator report). Panel still shows agent 0.7.0: filed as task card aibridge-version-not-bumped (shipped to fast-track).
- Step 3 (HALT / HALT_DAILY_LOSS): NOT resolved. Operator decision 2026-10-17: the daily loss halt is not wanted as a stop on trading. Reason given: too many losses should not stop trading; a placed trade with a stop loss runs to its end and there is no halt in question. Recorded only. No file was deleted or edited; no live-path change made. Implementing this would be a live-path change needing its own card, tests and the normal gates, and it removes the account-level stop that the blind-halt policy relies on. Open question for the operator: keep account-level stop or not.
- Steps 4-10: open.

Result: operator decision on HALT recorded; no live state changed.

## Subnote 2026-10-17: two questions for the operator's confirmation

1. Does every trade get a stop loss? Code reading (MyTradingSys/execution/executor.py header, R2/R7): each entry places a server-side stop_market covering the full filled size on the first fill. If the stop cannot be confirmed after a fill, the code closes the position and halts. Code says yes; NOT confirmed on the exchange. Needs a check on the Deribit testnet: one trade, stop order visible, size equal to position.
2. Can one account hold two positions in the same asset (two longs, or a long and a short)? Code reading (executor.py R8 and M8): NO. Pre-flight refuses a new plan if the instrument already has a position or open orders. M8 says two plans on one instrument need per-plan position accounting first. Not confirmed on the exchange; check the testnet with one position open, then try a second order.
