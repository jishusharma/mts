# Layer Lab Report: `gemini-blind-read-wavetrend-result-1104`

- **Card**: `gemini-blind-read-wavetrend-result-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/wavetrend_result_blind_read.md`
- **Headline Counts**: `FOUND=95 DIFF=0 NOT_IN_DATA=0`

## Findings

1. **Exact Reproduction of `RESULT.md` from `atlas_out/atlas_results.json` and `counts/` (`FOUND=95, DIFF=0, NOT_IN_DATA=0`)**:
   - `MyTradingSys/research/wavetrend_2026-10-17/make_result.py:1-98` renders `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md` directly from `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/atlas_results.json` with zero manual edits.
   - All 9 primary cell verdict rows (`W01..W09`, `RESULT.md:15-23`), all 36 cell-arm rows (`conjunction`, `WT alone`, `context alone`, `random clock`, `RESULT.md:29-64`), median episode depths (`W01 61.9, W02 61.7, W03 63.2, W04 63.7`, `RESULT.md:66`), all 9 Holm/MDE test rows (`RESULT.md:72-80`), all 9 per-cell statements (`RESULT.md:88-96`), all 9 control rows (`RESULT.md:102-110`), all 8 descriptive rows (`RESULT.md:116-123`), and all 4 module parity cross-checks (`5m 262456`, `15m 87352`, `1h 21688`, `4h 5272`, `RESULT.md:127`) match `atlas_out/atlas_results.json`, `counts/CELLS.csv:2-10`, `counts/counts_R3_c5_k2_G20.csv`, and `counts/quality.txt:1-5` exactly.
