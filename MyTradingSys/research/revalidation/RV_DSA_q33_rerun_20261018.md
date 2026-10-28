# RV-DSA Q33 matrix re-run - JIS-NUC, 2026-10-18

Command: `python MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py <BinanceDataFeed>/Dumps/backtest/raw_1m_2022/klines <scratch>` (39 s, no fetch needed; klines present from 2026-10-12 re-fetch).

- Rows in MATRIX_CELLS.csv: 336
- Status counts: tested 186 / underpowered 89 / n<20 61 (matches 186/89/61)
- Survivors: 0 (`survivors: []`)
- Smallest q: 0.620 (every tested cell)
- Diff vs committed: MATRIX_CELLS.csv and MATRIX_SUMMARY.json byte-identical (`cmp`).
