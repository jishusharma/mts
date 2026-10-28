# Sealed-window guard audit

RESULT (2026-10-26 UTC / 2026-10-27 IST, JIS-NUC): 34 synthetic attacks: 27 refused, 7 leakage paths under planted cache/payload corruption; 4 additional valid-date controls. Normal UI date inputs refused sealed windows. Seven paths share cache-content trust failures; they are not seven independent defects. No real sealed market data or external network used.

Full evidence, line references, threat model, failed safety expectation per leak and complete synthetic reproducer: `MyTradingSys/research/design_cards_2026-10-26/astra_sealed_guard.md`. Existing checks: 7 date tests and 23 conditions tests passed. Implementation follow-up: sim-desk-cache-date-validation (SONNET raw; requires review). Trust: UNCHECKED. Audit scope complete; no production code changed.
