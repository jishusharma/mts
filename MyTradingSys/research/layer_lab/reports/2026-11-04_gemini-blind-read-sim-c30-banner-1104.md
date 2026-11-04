# Layer Lab Report: `gemini-blind-read-sim-c30-banner-1104`

- **Card**: `gemini-blind-read-sim-c30-banner-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_SIM_C30_BANNER_1104.md`
- **Audit Outcome**: `VERDICT: MATCH`

## Findings

1. **Trade Count `n=35` Match**:
   - `c30_validation_verdict.json:7` specifies `"n": 35` for H1.
   - `c30_validation_verdict.json:24-204` contains exactly 35 H1 validation trades.
   - `eagle-c30-wt-rsi-div.json:24903` banner specifies `"n": 35`.
   - `eagle-c30-wt-rsi-div.json:24907` banner text contains `"n=35 (trade list)"`.
   - Result: MATCH.

2. **Mean Net % `-0.066` Match**:
   - `c30_validation_verdict.json:8` gives `"mean": -0.06591502449152191` (rounds to `-0.066`).
   - Summing the 35 raw trade returns in `c30_validation_verdict.json:24-204` gives sum = `-2.3072`, mean = `-0.06591999999999999` (rounds to `-0.066`).
   - In `eagle-c30-wt-rsi-div.json:24908`, banner specifies `"net_pct": -0.066`.
   - In `eagle-c30-wt-rsi-div.json:24907`, banner text contains `"net -0.066 %/trade after fees"`.
   - Result: MATCH.
