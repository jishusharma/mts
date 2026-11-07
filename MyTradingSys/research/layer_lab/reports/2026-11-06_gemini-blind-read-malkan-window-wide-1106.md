# Layer Lab Report: `gemini-blind-read-malkan-window-wide-1106`

- **Card**: `gemini-blind-read-malkan-window-wide-1106`
- **Date**: 2026-11-06 UTC
- **Reader**: Gemini (independent blind read worker)
- **Deliverable Audit Report**: `MyTradingSys/research/layer_lab/reports/2026-11-06_BLIND_READ_MALKAN_WIDE_1106.md`
- **Verification Command**:
  `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/layer_lab/reports/2026-11-06_BLIND_READ_MALKAN_WIDE_1106.md'); assert p.exists() and 'VERDICT' in p.read_text()"`

## Summary of Findings

1. **Protocol Adherence**:
   - `PRE_REG.md`, `counts.csv`, `gate_lines.csv`, `symbols.json`, and `regime_mix_count.txt` were verified before narrative review.
   - All 10 USD-M futures symbols across the DEV period (2022-01-01 to 2024-06-30 UTC) were processed from raw 1m klines independently.
   - Strictly causal strength-3 pivots, RSI 14 divergences, and 10-bar forward returns were computed.

2. **Recomputation & Verification (100% Match across 80 metrics)**:
   - All 8 power gate lines in `RESULT.md:9-18` and `gate_lines.csv` match the independent recomputation:
     - 1h S3_10: n=2359, days=2119, sd=2.795%, MDE+cost=0.416% -> BLOCK [MATCH]
     - 1h B11_12: n=443, days=432, sd=2.795%, MDE+cost=0.751% -> BLOCK [MATCH]
     - 1h C13_18: n=487, days=479, sd=2.795%, MDE+cost=0.721% -> BLOCK [MATCH]
     - 1h D19_50: n=140, days=140, sd=2.795%, MDE+cost=1.214% -> BLOCK [MATCH]
     - 4h S3_10: n=599, days=591, sd=5.454%, MDE+cost=1.160% -> BLOCK [MATCH]
     - 4h B11_12: n=116, days=116, sd=5.454%, MDE+cost=2.443% -> BLOCK [MATCH]
     - 4h C13_18: n=158, days=158, sd=5.454%, MDE+cost=2.113% -> BLOCK [MATCH]
     - 4h D19_50: n=38, days=38, sd=5.454%, MDE+cost=4.163% -> BLOCK [MATCH]
   - All 16 disaggregated directional counts in `counts.csv` match independent event collection from raw data.
   - All symbol bar counts (21768 to 21888 1h bars) and regime mixture breakdown (130 weeks: bull 25 (19%), bear 0 (0%), range 105 (81%)) match exactly.

3. **Pre-Registration Alignment**:
   - Zero contradictions with `PRE_REG.md`. Power gate rule enforced correctly, `--pass dev` returns suppressed due to power block, and verdict word `BLOCKED` placed first in `RESULT.md`.

VERDICT: MATCH
