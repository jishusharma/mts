# B070 - DEMOTE UTC 00:00 ANCHOR AND 0.75 SLIPPAGE

Register row: MyTradingSys/research/BUGS.md B070.
Opened: 2026-09-25, split from B067 by session MTS-2026-09-25-0829Z.

## THE DEFECT

Two crypto adaptations gate the core verdict with no Tom or cross-trader source:

1. UTC 00:00 daily open. Anchors state_code.json CVD and mts_math.py session CVD. Live verdict input.
2. 0.75 slippage multiplier. Scales every net_rr value. Verdict-changing constant.

PROJECT_VISION doctrine: modules never gate core behavior.

## EVIDENCE

B067 audit at Dumps/workers/CLOSE-2026-09-25/W4-B067-crypto-audit/REPLY.md
classified both as gates. Both are UNVALIDATED in crypto_adaptations.md.
Tom never mentions either.

## FIX SHAPE (pending operator decision)

Option A: demote both to display-only (mirror post_funding_vp demotion).
Option B: keep as gates and validate them (requires Tom citation or
documented exception per playbook.md Part I).

## STATUS

CLOSED 2026-10-04. Operator ruling (a): friction = fee model from backtest/fees.py (FORMULAS.md section 17); UTC 00:00 anchor
display-only. Session record: MyTradingSys/system/sessions/MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00.md.
