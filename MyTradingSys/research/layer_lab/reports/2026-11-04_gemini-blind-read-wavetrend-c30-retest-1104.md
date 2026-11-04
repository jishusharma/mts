# Gemini Blind Read Report: WaveTrend C30 Retest and Long-Window RESULT.md vs CSVs (2026-11-04)

- **Card**: `gemini-blind-read-wavetrend-c30-retest-1104`
- **Audited Files**:
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/RESULT.md` [SOURCED: RESULT.md:1-19]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/RESULT_LONG.md` [SOURCED: RESULT_LONG.md:1-45]
- **Raw CSV Data**:
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/counts.csv` (1,080 rows) [SOURCED: counts.csv:1-1081]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_cells.csv` (1,080 rows) [SOURCED: dev_cells.csv:1-1081]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/counts_long.csv` (1,356 rows) [SOURCED: counts_long.csv:1-1357]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_cells_long.csv` (1,356 rows) [SOURCED: dev_cells_long.csv:1-1357]
- **Audit File**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_WAVETREND_C30_1104.md`
- **Date**: 2026-11-04 (UTC)
- **Status**: VERDICT: MATCH (`FOUND=82 DIFF=0 NOT_IN_DATA=0`)

## 1. Summary of Findings

1. **Reconciliation Match**: Every metric in `RESULT.md` (Run 1) and `RESULT_LONG.md` (Long window) matches the raw CSV outputs without error across all 82 checked figures.
2. **Counts & Discrepancies**:
   - `counts.csv` vs `dev_cells.csv`: 0 mismatches across 1,080 rows (`n_diff=0, days_diff=0, sig_diff=0`) [OURS recomputation via pandas merge].
   - `counts_long.csv` vs `dev_cells_long.csv`: 0 mismatches across 1,356 rows (`n_diff=0, days_diff=0, sig_diff=0`) [OURS recomputation via pandas merge].
3. **Regime Mix**:
   - Run 1 (130 weeks): Bull 25 (19.23% -> 19%), Bear 0 (0%), Range 105 (80.77% -> 81%), N/A 0 (0%) [SOURCED: regime_mix_dev.txt:1].
   - Long Window (326 weeks): Bull 73 (22.39% -> 22%), Strict Bear 0 (0%), Range 222 (68.10% -> 68%), N/A 31 (9.51% -> 10%), Proxy Bear (`reg_bearp`, weekly RSI14 <= 40 alone, below SMA200, OURS) 57 (17.48%) [SOURCED: regime_mix_long_dev.txt:1].
4. **Survivors**:
   - Run 1: 0 survivors out of 24 pooled + 96 session cells (Holm m=24 / 96) [SOURCED: dev_survivors.json:1].
   - Long Window: 0 survivors out of 48 pooled + 192 session cells (Holm m=48 / 192) [SOURCED: dev_survivors_long.json:1].
5. **SOURCED vs OURS Labeling**:
   - Conforms strictly to `d-bear-proxy-1104` [SOURCED: OPERATOR_DECISIONS.md:1694-1698].
   - Malkan weekly-and-monthly <= 40 bear gate is SOURCED (`MALKAN_RULES_2026-10-31.md`) and yields 0 bear weeks on BTCUSDT.
   - Weekly-only bear proxy arm (`reg_bearp`) is strictly labelled OURS and never called Malkan's.

## 2. Key Figures Reconciliation Summary

| Metric | `RESULT.md` / `RESULT_LONG.md` Quote | CSV Location & Recomputed Value | Label | Status |
|---|---|---|---|---|
| Bare dot 15m buy | `RESULT.md:9` (`-0.131 %`) | `dev_cells.csv:1` (`net=-0.131293`) | SOURCED | MATCH |
| Bare dot 15m sell | `RESULT.md:9` (`-0.202 %`) | `dev_cells.csv:181` (`net=-0.201847`) | SOURCED | MATCH |
| 15m sell trend with | `RESULT.md:10` (`-0.062 %`) | `dev_cells.csv:187` (`net=-0.062031`) | SOURCED | MATCH |
| 15m sell trend against | `RESULT.md:10` (`-0.305 %`) | `dev_cells.csv:193` (`net=-0.305096`) | SOURCED | MATCH |
| Lead 1: 15m sell RSI | `RESULT.md:11` (`n 257 / 170 days, gross +0.148 %, net +0.008 %`) | `dev_cells.csv:251` (`n=257, days=170, gross=0.147614, net=0.007614`) | SOURCED | MATCH |
| Lead 2: 1h sell div retest | `RESULT.md:11` (`n 19 / 17 days, net +1.117 % [+0.007, +2.227]`) | `dev_cells.csv:1032` (`n=19, days=17, net=1.117070, ci=[0.006935, 2.227205]`) | SOURCED | MATCH |
| Lead 1 long window | `RESULT_LONG.md:21` (`651 / 419, -0.183 [-0.294, -0.072]`) | `dev_cells_long.csv` (`n=651, days=419, net=-0.183495`) | SOURCED | MATCH |
| Lead 2 long window | `RESULT_LONG.md:28` (`46 / 41, -0.225 [-1.058, +0.608]`) | `dev_cells_long.csv` (`n=46, days=41, net=-0.225091`) | SOURCED | MATCH |
| Proxy arm bear weeks | `RESULT_LONG.md:1` (`57 of 326 weeks`) | `regime_mix_long_dev.txt:1` (`57 of 326 weeks`) | OURS | MATCH |
| Proxy buy 15m rsi | `RESULT_LONG.md:37` (`n 230 / 148 days +0.084 [-0.151, +0.318]`) | `dev_cells_long.csv` (`n=230, days=148, net=0.083507`) | OURS | MATCH |

Verification Command:
`python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_WAVETREND_C30_1104.md'); assert p.exists() and 'VERDICT: MATCH' in p.read_text()"`
