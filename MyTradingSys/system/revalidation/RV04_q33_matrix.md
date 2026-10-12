# RV04 [MED] Q33 fast-move matrix: reproduction and method check (72c2090)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV04. Report: `MyTradingSys/research/revalidation/RV04_<UTC date>.md`.

Scope in: MyTradingSys/research/tom_fabio_guidance_2026-10-12/ (PRE_REG_Q33.md, matrix_q33.py, MATRIX_CELLS.csv, MATRIX_SUMMARY.json,
MATRIX_REPORT.md, FAST_MOVE_CATALOGUE.md, SOURCED_RULES.md), MyTradingSys/backtest/fees.py.
Scope out: editing, adding cells, tuning, any holdout.
Why: its verdict closed Q34 (no cross-guidance wiring). A negative result with a bug in the trigger code would close a live idea.
Steps (chunk: each step <= 300 s on the DSA bridge, outputs to files):
1. If `Dumps/backtest/raw_1m_2022/klines` is missing: `python MyTradingSys/backtest/fetch_binance_archive.py --help`, then fetch BTCUSDT
   1m 2022-01..2026-10 (USD-M perp, data.binance.vision) into it; expect 2,512,800 bars, 0 gaps.
2. `python MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py Dumps/backtest/raw_1m_2022/klines <scratch-out-dir>`
   (never over the committed outputs). Diff MATRIX_CELLS.csv: row count 336, status counts 186/89/61, survivors 0, min q 0.62.
3. Spot-recompute by hand (separate script, not by importing the runner): T1 BB breach event count, one LVN day, and 20 random FVG
   T3 events: print bar timestamps and check each event is decidable at the close of bar t (no look-ahead).
4. Method items: halves (`half = N // 2`) vs the pre-reg text "first half 2022-2024, second half 2025-2026"; 1h ATR proxy
   `2 x ATR15` vs the pre-reg's ATR(14,1h); F8 "unsupported" ignores the CVD-agree test; placebo overlap (events within 4 bars).
Already known (confirm or refute): report numbers match MATRIX_CELLS.csv (checked 2026-10-12: 336 cells, 186 tested, 0 positive at
60 min, 3 positive at 240 min, best 0.039 %); the split is at bar N//2 = about 2024-05-22, not 2025-01-01.
