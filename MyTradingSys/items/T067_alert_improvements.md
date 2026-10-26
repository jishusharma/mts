# T067 - Alert improvements (incl. "buy detection")

Opened 2026-10-05 by MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Status OPEN. Verbatim ask: research/_archive/loose_2026-10/OPERATOR_ASKS_2026-10-05.md section 0, ask 5.

## Scope
a. Inputs first: B136 (OI), G12 (zone touch on 1m high/low), G2 (feed watchdog).
b. Event alerts: T063 signature (if the study passes); absorption at a marked zone (T064 definition); operator levels (T066).
c. "Buy detection": working reading = large aggressive buying (b99/b999 buy tiers in orderflow_live, with OI up = new
   longs vs OI down = short covering). OPERATOR TO CONFIRM (could mean bot detection).
Live path: layers/alerts/ is single-owner; spec + tests on Cloud, staging + restart on Desktop by the supervisor.
