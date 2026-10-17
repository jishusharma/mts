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

## 2026-10-17 session (Haiku handover): steps 1 and 4, mts-doctor shipped

- mts-doctor card: goal shortened to 309 chars (lint was failing on 400). `tasks.py check mts-doctor` passes. Committed 9af5d872 with Result line, shipped to fast-track via sync.py ship (docs gate, all selected steps PASS).
- Step 1 (context baseline, jishu.sharma): still open. Claude Docs and visualize off (earlier). Computer use, Claude in Chrome and the 9 skills cannot be read from the repo; operator to confirm in the app. `token_audit.py --days 1` ran: usage is recorded, no toggle state in it.
- Step 4 (Q76 power-gate): the question is the pit-levels PRE_REG_V2 card (`pit-prior-va-failed-auction-dev`, state done, result BLOCKED). Gate fails: MDE+cost 0.411 R > 0.30 R; 662 days vs 2,427 needed. The card writes BLOCKED.md unless the operator overrules the plausible effect. Default stands: BLOCKED. Open decision for the operator: overrule the plausible effect and run, or keep BLOCKED.
- Steps 2, 3, 5-10: unchanged from the handover (see entries above and the open list in this file).

- 2026-10-17 Q76 (PIT power gate): operator decision recorded in OPERATOR_DECISIONS.md (q-pit-power-gate). Get the data from a trusted source where it can be had; if not, keep BLOCKED or remove the card so it does not come back. No overrule written; other sessions take the data work.
