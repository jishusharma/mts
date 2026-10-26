# Confluence pre-registration audit

Card: astra-low-confluence-prereg-leak-hunt. Trust: UNCHECKED (no cross-vendor review receipt). Audit and evidence: `MyTradingSys/research/design_cards_2026-10-26/astra_confluence_leak_hunt.md`.

RESULT (2026-10-26, JIS-NUC): 18 Holm slots reviewed: 2 CLEAN, 15 explicitly disclosed DEV-window reuse flags and 1 noncausal full-DEV sizing-calibration flag. These are definition-level audit classifications, not observed S3/S4 execution leaks. See the audit table and its P:68-73,126-127 citations. Four usable layer-events have 24h label endpoints beyond the DEV cutoff; no forbidden bars were read.

Validation: `python -m unittest discover -s MyTradingSys/backtest/layers/krown -p test_krown_context*.py` passed 24 tests. Independent csv scan: 0 context timestamp violations among 22,862 usable rows of 23,213 total in `research/krown_audit_2026-10-22/run/joined_events.csv`; full method and limits in the audit. Frozen definitions and trading code unchanged. No VALIDATION/HOLDOUT read or layer disposition decision.
