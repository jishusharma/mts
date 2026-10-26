# CBP gate trial

RESULT: five synthetic bad-row probes: missing quote and same-video/analyst duplicate stopped; invalid direction, expired row and missing expiry reproduce gaps before repair. Initial probe run 3 failed/2 passed; permanent strict-known-failure audit file 13 passed/3 xfailed. No real CBP rows, transcripts or stores used. Gates 4/5 were not exercised and no order permission is inferred.

Evidence and commands: `MyTradingSys/research/cbp/GATES_TRIAL_GPT.md`; fixtures: `MyTradingSys/tests/test_cbp_query.py`. Repair/review card cbp-row-schema-expiry-gaps (raw SONNET). No production code modified. Trust: UNCHECKED pending review.
