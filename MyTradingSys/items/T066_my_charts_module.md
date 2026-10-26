# T066 - "My charts": read the operator's TradingView layouts into MTS

Opened 2026-10-05 by MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Status OPEN. Verbatim ask: research/_archive/loose_2026-10/OPERATOR_ASKS_2026-10-05.md section 0, ask 4.
Tag: [OPERATOR] (operator's own ideas; separate layer).

## Route (recommended)
Claude in Chrome, operator's logged-in Chrome, read-only. Per layout: symbol, TF, drawings via Object Tree + each
drawing's settings (exact prices/times), indicators + inputs, text notes; screenshot as evidence.
Output: MyTradingSys/my_charts/<layout>_<YYYY-MM-DD>.json + .md (long-term / short-term tag).
Never sign in, edit, or save the operator's charts. Port Pine only for open-source scripts that pass ROI.

## Steps
1. Pilot: operator names 1 long-term + 1 short-term layout; Claude reads; operator checks every level.
2. Schema freeze after the pilot; then a refresh routine (on operator request, Desktop only).
3. Consumers: snapshot context field `operator_levels` (read-only), alerts at operator levels (T067).
