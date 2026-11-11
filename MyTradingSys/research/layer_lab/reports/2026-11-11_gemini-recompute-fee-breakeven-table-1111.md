COUNTS: MATCH=11 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Recomputation: Fee Break-Even Table (COMPARE s4, EDGE_PLAN a) & Binance Taker Fee

- **Card**: `gemini-recompute-fee-breakeven-table-1111`
- **Date**: 2026-11-11 UTC
- **Reader / Auditor**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-recompute-fee-breakeven-table-1111`)
- **Scope In (read-only)**:
  - `MyTradingSys/research/four_model_review_2026-11-11/COMPARE.md` (s4; lines 29-42; read)
  - `MyTradingSys/research/edge_plan_2026-11-11/EDGE_PLAN.md` (a; lines 5-14; read)
  - `MyTradingSys/backtest/fees.py` (lines 12-14, 36; read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-recompute-fee-breakeven-table-1111.md` (new report)
- **Scope Out Respected**:
  - No edit to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`; no `REVIEWED` stamp.

---

## 1. Executive Summary

- Total target clauses audited: **11**
- Recomputation & audit result: **MATCH = 11, DIFF = 0, NOT_IN_DATA = 0**
- Break-even win rate formula: `win rate = (move + fee) / (2 * move)` [SOURCED: `COMPARE.md:31-32`]
- Recomputed values for market orders (fee = 70 USD) across moves [100, 300, 500, 1000, 2000] USD:
  - 100 USD: `(100 + 70) / 200 = 0.8500` -> **85%** [MATCH]
  - 300 USD: `(300 + 70) / 600 = 0.6166...` -> **62%** [MATCH]
  - 500 USD: `(500 + 70) / 1000 = 0.5700` -> **57%** [MATCH]
  - 1,000 USD: `(1000 + 70) / 2000 = 0.5350` -> **54%** [MATCH]
  - 2,000 USD: `(2000 + 70) / 4000 = 0.5175` -> **52%** [MATCH]
- Recomputed values for limit orders (fee = 35 USD) across moves [100, 300, 500, 1000, 2000] USD:
  - 100 USD: `(100 + 35) / 200 = 0.6750` -> **68%** [MATCH]
  - 300 USD: `(300 + 35) / 600 = 0.5583...` -> **56%** [MATCH]
  - 500 USD: `(500 + 35) / 1000 = 0.5350` -> **54%** [MATCH]
  - 1,000 USD: `(1000 + 35) / 2000 = 0.5175` -> **52%** [MATCH]
  - 2,000 USD: `(2000 + 35) / 4000 = 0.50875` -> **51%** [MATCH]
- Fee check & BTC Price recomputation:
  - `BINANCE_TAKER = 0.0005` (5 bp per side = 10 bp round trip) [SOURCED: `fees.py:12-14,36`].
  - 10 bp round trip on 1 BTC = `0.0010 * BTC_PRICE`.
  - For round-trip fee = 70 USD: `0.0010 * BTC_PRICE = 70 USD` => `BTC_PRICE = 70 / 0.0010 = 70,000 USD` [OURS arithmetic].

---

## 2. Clause Audit Table (11 Clauses)

| # | Clause / Parameter | Stated in `COMPARE.md` (s4) | Stated in `EDGE_PLAN.md` (a) | Recomputed Value (OURS) | Status | Quote file:line & Verification |
|---|---|---|---|---|---|---|
| 1 | Move 100 USD, Market (fee 70 USD) | `85 %` (`COMPARE.md:36`) | `85 %` (`EDGE_PLAN.md:9`) | `(100+70)/(2*100) = 85.0000%` -> `85 %` | `MATCH` | SOURCED `COMPARE.md:36`: `| 100 USD | 85 % | 68 % |` and SOURCED `EDGE_PLAN.md:9`: `| 100 USD | 85 % | 68 % |`. Matches exact arithmetic. |
| 2 | Move 300 USD, Market (fee 70 USD) | `62 %` (`COMPARE.md:37`) | `62 %` (`EDGE_PLAN.md:10`) | `(300+70)/(2*300) = 61.6667%` -> `62 %` | `MATCH` | SOURCED `COMPARE.md:37`: `| 300 USD | 62 % | 56 % |` and SOURCED `EDGE_PLAN.md:10`: `| 300 USD | 62 % | 56 % |`. Matches rounded integer. |
| 3 | Move 500 USD, Market (fee 70 USD) | `57 %` (`COMPARE.md:38`) | `57 %` (`EDGE_PLAN.md:11`) | `(500+70)/(2*500) = 57.0000%` -> `57 %` | `MATCH` | SOURCED `COMPARE.md:38`: `| 500 USD | 57 % | 54 % |` and SOURCED `EDGE_PLAN.md:11`: `| 500 USD | 57 % | 54 % |`. Matches exact arithmetic. |
| 4 | Move 1,000 USD, Market (fee 70 USD) | `54 %` (`COMPARE.md:39`) | `54 %` (`EDGE_PLAN.md:12`) | `(1000+70)/(2*1000) = 53.5000%` -> `54 %` | `MATCH` | SOURCED `COMPARE.md:39`: `| 1,000 USD | 54 % | 52 % |` and SOURCED `EDGE_PLAN.md:12`: `| 1,000 USD | 54 % | 52 % |`. Matches rounded integer (53.5% rounds to 54%). |
| 5 | Move 2,000 USD, Market (fee 70 USD) | `52 %` (`COMPARE.md:40`) | `52 %` (`EDGE_PLAN.md:13`) | `(2000+70)/(2*2000) = 51.7500%` -> `52 %` | `MATCH` | SOURCED `COMPARE.md:40`: `| 2,000 USD | 52 % | 51 % |` and SOURCED `EDGE_PLAN.md:13`: `| 2,000 USD | 52 % | 51 % |`. Matches rounded integer (51.75% rounds to 52%). |
| 6 | Move 100 USD, Limit (fee 35 USD) | `68 %` (`COMPARE.md:36`) | `68 %` (`EDGE_PLAN.md:9`) | `(100+35)/(2*100) = 67.5000%` -> `68 %` | `MATCH` | SOURCED `COMPARE.md:36`: `| 100 USD | 85 % | 68 % |` and SOURCED `EDGE_PLAN.md:9`: `| 100 USD | 85 % | 68 % |`. Matches rounded integer (67.5% rounds to 68%). |
| 7 | Move 300 USD, Limit (fee 35 USD) | `56 %` (`COMPARE.md:37`) | `56 %` (`EDGE_PLAN.md:10`) | `(300+35)/(2*300) = 55.8333%` -> `56 %` | `MATCH` | SOURCED `COMPARE.md:37`: `| 300 USD | 62 % | 56 % |` and SOURCED `EDGE_PLAN.md:10`: `| 300 USD | 62 % | 56 % |`. Matches rounded integer. |
| 8 | Move 500 USD, Limit (fee 35 USD) | `54 %` (`COMPARE.md:38`) | `54 %` (`EDGE_PLAN.md:11`) | `(500+35)/(2*500) = 53.5000%` -> `54 %` | `MATCH` | SOURCED `COMPARE.md:38`: `| 500 USD | 57 % | 54 % |` and SOURCED `EDGE_PLAN.md:11`: `| 500 USD | 57 % | 54 % |`. Matches rounded integer (53.5% rounds to 54%). |
| 9 | Move 1,000 USD, Limit (fee 35 USD) | `52 %` (`COMPARE.md:39`) | `52 %` (`EDGE_PLAN.md:12`) | `(1000+35)/(2*1000) = 51.7500%` -> `52 %` | `MATCH` | SOURCED `COMPARE.md:39`: `| 1,000 USD | 54 % | 52 % |` and SOURCED `EDGE_PLAN.md:12`: `| 1,000 USD | 52 % | 51 % |`. Matches rounded integer (51.75% rounds to 52%). |
| 10 | Move 2,000 USD, Limit (fee 35 USD) | `51 %` (`COMPARE.md:40`) | `51 %` (`EDGE_PLAN.md:13`) | `(2000+35)/(2*2000) = 50.8750%` -> `51 %` | `MATCH` | SOURCED `COMPARE.md:40`: `| 2,000 USD | 52 % | 51 % |` and SOURCED `EDGE_PLAN.md:13`: `| 2,000 USD | 52 % | 51 % |`. Matches rounded integer (50.875% rounds to 51%). |
| 11 | Fee rate & BTC price for 10 bp = 70 USD | `fee 10 bp round trip taker` (`COMPARE.md:42`) | `10 bp round trip taker` (`EDGE_PLAN.md:6`) | `BINANCE_TAKER = 0.0005`; 10 bp RT = 70 USD at BTC = 70,000 USD | `MATCH` | SOURCED `fees.py:12-13`: `BINANCE_TAKER / BINANCE_MAKER: Binance USDT-M perpetual, default tier. maker 0.0002 (4 bps RT), taker 0.0005 (10 bps RT)` and `fees.py:36`: `BINANCE_TAKER = 0.0005`. Price calculation: `70 / 0.0010 = 70,000 USD` [OURS arithmetic]. |
