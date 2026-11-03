# Layer Lab Report: Gemini Blind Re-read of bounce_shift_2026-10-30 RESULT.md

- **Task**: `gemini-blind-read-bounce-shift-1103`
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Date**: 2026-11-03
- **Audit Target**: `MyTradingSys/research/bounce_shift_2026-10-30/RESULT.md` (Commit `a4730f3628e5`)
- **Comparison Source**: `MyTradingSys/research/bounce_shift_2026-10-30/output.txt`
- **Audit Table Output**: `MyTradingSys/research/gemini_audits_2026-11-03/bounce_shift_blind_read.md`

## Summary of Findings

1. **Empirical Counts & Percentages in Tables**:
   - Every single number reported in **Table 1: At the trigger (n=755)** and **Table 2: Momentum-shift signals** matches `output.txt` exactly:
     - Table 1 All: `n=755` (`output.txt:8`), `+0.5% first: 47.8%` (`output.txt:8`), `-0.5% first: 49.3%` (`output.txt:8`), `Up 60 min: 55.8%` (`output.txt:8`), `Max up >= 1% in 4 h: 44.1%` (`output.txt:8`).
     - Table 1 Subsets: OI up (`n=178`), OI down (`n=431`), Round numbers (`n=247`), Prior-day low (`n=378`) all match lines 13, 16, 22, 28 of `output.txt`.
     - Table 2 Signals (RANDOM, S1, S2, S3, S4, S5): all median lags (converted from 5m bars to minutes, e.g. 13 bars = 65 min, 2 bars = 10 min), firing percentages, `up_first`, `down_first`, and `low_broken` match lines 41-46 of `output.txt`.
     - Narrative annual breakdown: 2022 (51.5% -> 51%), 2025 (50.7% -> 51%), 2024 (61.6% -> 62%) in line 20 matches `output.txt:33-36`.
     - Signal annual breakdown for S5: 2024 (51.5% -> 52%), 2025 (53.7% -> 54%), 2022 (45.3%), 2023 (45.8%) matches `output.txt:56`.

2. **Counts / Status**:
   - `FOUND`: 90 items
   - `NOT_IN_DATA`: 10 items (Live cascade observation values cited from operator shot 97857881eb00: 80.4k, 77.63k, 78,115, band 78,254, RSI 19, RSI 23.7, 4.7%, timestamps 23:50Z, 00:15Z; untouched future year 2026; narrative SE calculation reference "3 standard errors")
   - `DIFF`: 1 item (Minor typo in `RESULT.md:5`: quotes cascade trough as `77.63k` whereas `study.py:1` docstring records `77.65k`)

3. **Line 1 Header Compliance**:
   - First line of `MyTradingSys/research/gemini_audits_2026-11-03/bounce_shift_blind_read.md` is strictly:
     `# FOUND: 90, NOT_IN_DATA: 10, DIFF: 1`
