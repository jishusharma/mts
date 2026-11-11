# Findings Report: tvfav-usage-adx-1107

- **Card ID:** `tvfav-usage-adx-1107`
- **Goal:** TV favourite usage research: ADX and DI (Wilder 1978; 20/25 thresholds; DI-cross readers such as CCU/Steve).
- **Date:** 2026-11-11 (UTC)

## Deliverables & Verifications

1. **Research Note Created:**
   - Path: `MyTradingSys/research/tv_favorites_2026-11/USAGE_adx.md`
   - Content: 5 required sections per `MyTradingSys/system/SPEC_INDICATOR_MAP.md` Step 1:
     1. Author's Intent (Wilder 1978, +DM/-DM, TR, DX, ADX formulas and definitions).
     2. How People Use It (4 sources: J. Welles Wilder Jr., BeikabuOyaji, CCU / Steve, Quantitative Momentum & MTS Census).
     3. Crypto / Bitcoin Filter (what fails: blind crosses, LTF lag, symmetric assumptions, ignoring slope; what survives: HTF context, level rejection & wick context).
     4. Common Pitfalls and Parameters (SOURCED defaults vs OURS context columns, ADX buckets, and exhaustion filter).
     5. One-line "What it measures" (trend strength & expansion momentum alongside buyer vs seller directional dominance).

2. **Quote Verification:**
   - Command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tv_favorites_2026-11/USAGE_adx.md`
   - Outcome: Exit 0 (`PASS: 0 problem(s)` across 7 verified citations/quotes against `FORMULAS.md`, `FAVORITES_2026-11-07.md`, `PLAN_ADX_DI_VOLUME_2026-11-07.md`, `SPEC.md`, and `CENSUS.md`).

3. **Constraints:**
   - File format: Follows the companion files `USAGE_squeeze.md`, `USAGE_vfi.md`, and `USAGE_wavetrend.md`.
   - Length: ~6031 bytes.
   - Zero trading code, zero backtests, zero verdicts.
