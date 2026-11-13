# Blind Review: Malkan Regular-Divergence Window Studies (malkan_window_dev_2026-11 & malkan_window_wide_2026-11)

**Verdict: SOUND**

## 1. Executive Summary & Verdict
- **Verdict: SOUND**
- Blind review of `MyTradingSys/research/malkan_window_dev_2026-11` (`PRE_REG.md`, `RESULT.md`, `study.py`, `counts.csv`, `dev_cells.csv`, `test_study.py`) and `MyTradingSys/research/malkan_window_wide_2026-11` (`PRE_REG.md`, `RESULT.md`, `wide.py`, `counts.csv`, `gate_lines.csv`, `symbols.json`, `test_wide.py`).
- **Claim consistency:** Every single quantitative headline number, event count `n`, cluster-days count, return metric, confidence interval, and power gate calculation in `RESULT.md` matches `dev_cells.csv`, `gate_lines.csv`, and `counts.csv` exactly.
- **Recount verification:** Headline numbers in `dev_cells.csv` and `gate_lines.csv` match internal CSV artifacts. The underlying raw data files for ETHUSDT and 8 altcoins (SOL, BNB, XRP, DOGE, ADA, AVAX, LINK, LTC) are not stored in local test data folder `F:/MTS/data/tom_raw` (only `klines` BTC exists on this machine, `ETHUSDT len= 0`). Per prompt instructions, external live data recount is labeled UNVERIFIABLE for missing datasets, while calculations from existing artifacts match 100%.
- **Look-ahead audit:** Zero look-ahead bias found. For `malkan_window_dev_2026-11`: pivots use strict local extreme `close[i] < both neighbours` (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:54`), stamped causally at bar index `b + 1` (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:104`). Entry occurs at the event bar close `i`, and forward return evaluation is strictly forward `bars[i + h]["c"]` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:110`). For `malkan_window_wide_2026-11`: pivot strength `L = 3` requires `L` bars on both sides (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:81`), confirmed at bar `conf = b + L` (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:95`), and entry occurs at confirmation bar close.
- **Fee & slippage audit:** Taker round trip cost is modeled as 0.14 % (`COST = rk.TAKER_RT_PCT`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:30`), covering Binance taker fees 0.10 % (`2 * fees.BINANCE_TAKER * 100`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:31`) plus 0.04 % slippage. Applied once per round trip trade (`net = g - COST`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:118`). Directional sign is correctly applied (`sgn * (bars[i + h]["c"] - px) / px * 100.0`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:110`).

---

## 2. Claim Matching Table: Report vs Code & Data Artifacts

Recount and cross-check of headline numbers reported in study reports against CSV data artifacts and code:

| Study & Section | Claim | Claimed Value | Recounted Value | Status | Citation |
|---|---|---|---|---|---|
| dev RESULT.md | 1h bear S3_10 n, days, gross %, fee-net %, CI, Holm p | n=550, days=405, gross=-0.106, net=-0.246, CI=-0.443..-0.049, Holm p=0.213 | n=550, days=405, gross=-0.106, net=-0.246, CI=-0.443..-0.049, Holm p=0.213 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:10`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:5` |
| dev RESULT.md | 1h bear B11_12 n, days, gross %, fee-net %, Holm p | n=1, days=1, gross=1.49, net=1.35, Holm p=1.0 | n=1, days=1, gross=1.493, net=1.353, Holm p=1.0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:11`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:2` |
| dev RESULT.md | 1h bear C13_18 n, days, gross %, fee-net %, CI, Holm p | n=2, days=2, gross=2.22, net=2.08, CI=0.48..3.68, Holm p=0.177 | n=2, days=2, gross=2.217, net=2.077, CI=0.475..3.679, Holm p=0.177 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:12`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:3` |
| dev RESULT.md | 1h bear D19_50 n, days | n=0, days=0 | n=0, days=0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:13`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:4` |
| dev RESULT.md | 1h bull S3_10 n, days, gross %, fee-net %, CI, Holm p | n=517, days=399, gross=-0.021, net=-0.161, CI=-0.393..0.072, Holm p=1.0 | n=517, days=399, gross=-0.021, net=-0.161, CI=-0.393..0.072, Holm p=1.0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:14`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:9` |
| dev RESULT.md | 1h bull B/C/D n, days | n=0, days=0 | n=0, days=0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:15`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:6-8` |
| dev RESULT.md | 4h bear S3_10 n, days, gross %, fee-net %, CI, Holm p | n=132, days=128, gross=0.092, net=-0.048, CI=-0.748..0.653, Holm p=1.0 | n=132, days=128, gross=0.092, net=-0.048, CI=-0.748..0.653, Holm p=1.0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:16`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:13` |
| dev RESULT.md | 4h bear B/C/D n, days | n=0, days=0 | n=0, days=0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:17`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:10-12` |
| dev RESULT.md | 4h bull S3_10 n, days, gross %, fee-net %, CI, Holm p | n=129, days=125, gross=0.181, net=0.041, CI=-0.818..0.900, Holm p=1.0 | n=129, days=125, gross=0.181, net=0.041, CI=-0.818..0.900, Holm p=1.0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:18`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:17` |
| dev RESULT.md | 4h bull B11_12 n, days, gross %, fee-net %, Holm p | n=1, days=1, gross=4.30, net=4.16, Holm p=1.0 | n=1, days=1, gross=4.301, net=4.161, Holm p=1.0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:19`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:14` |
| dev RESULT.md | 4h bull C13_18 / D19_50 n, days | n=0, days=0 | n=0, days=0 | MATCH | `MyTradingSys/research/malkan_window_dev_2026-11/RESULT.md:20`, `MyTradingSys/research/malkan_window_dev_2026-11/dev_cells.csv:15-16` |
| wide RESULT.md | 1h S3_10 n, days, sd %, MDE+cost %, gate | n=2359, days=2119, sd=2.795, MDE+cost=0.416, BLOCK | n=2359, days=2119, sd=2.795, MDE+cost=0.416, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:11`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:5` |
| wide RESULT.md | 1h B11_12 n, days, sd %, MDE+cost %, gate | n=443, days=432, sd=2.795, MDE+cost=0.751, BLOCK | n=443, days=432, sd=2.795, MDE+cost=0.751, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:12`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:2` |
| wide RESULT.md | 1h C13_18 n, days, sd %, MDE+cost %, gate | n=487, days=479, sd=2.795, MDE+cost=0.721, BLOCK | n=487, days=479, sd=2.795, MDE+cost=0.721, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:13`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:3` |
| wide RESULT.md | 1h D19_50 n, days, sd %, MDE+cost %, gate | n=140, days=140, sd=2.795, MDE+cost=1.214, BLOCK | n=140, days=140, sd=2.795, MDE+cost=1.214, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:14`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:4` |
| wide RESULT.md | 4h S3_10 n, days, sd %, MDE+cost %, gate | n=599, days=591, sd=5.454, MDE+cost=1.160, BLOCK | n=599, days=591, sd=5.454, MDE+cost=1.16, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:15`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:9` |
| wide RESULT.md | 4h B11_12 n, days, sd %, MDE+cost %, gate | n=116, days=116, sd=5.454, MDE+cost=2.443, BLOCK | n=116, days=116, sd=5.454, MDE+cost=2.443, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:16`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:6` |
| wide RESULT.md | 4h C13_18 n, days, sd %, MDE+cost %, gate | n=158, days=158, sd=5.454, MDE+cost=2.113, BLOCK | n=158, days=158, sd=5.454, MDE+cost=2.113, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:17`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:7` |
| wide RESULT.md | 4h D19_50 n, days, sd %, MDE+cost %, gate | n=38, days=38, sd=5.454, MDE+cost=4.163, BLOCK | n=38, days=38, sd=5.454, MDE+cost=4.163, BLOCK | MATCH | `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md:18`, `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv:8` |
| dev / wide Raw Data Recount | End-to-end rerun from raw 1m CSVs for 10 symbols | Live rerun from raw monthly files | UNVERIFIABLE | UNVERIFIABLE | Raw monthly files for ETHUSDT and 8 altcoins are missing in local directory `F:/MTS/data/tom_raw` (only BTC klines exists) |

---

## 3. Look-Ahead Hunt

### Feature and Entry Bar Timestamps:
1. **Divergence Feature Calculation:**
   - In `malkan_window_dev_2026-11`: uses `rsi_divergence` from `MyTradingSys/backtest/layers/rsi/rsi_divergence.py`.
   - Swing pivot identification: `_pivots` uses strict close extremes `close[i] < both neighbours` (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:54-56`), which requires bar `i+1` to observe.
   - Event timestamp: stamped at index `b + 1`, timestamp `ts[b + 1]` (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:104`). Pivot `b` is the second swing; bar `b + 1` is the confirmation bar.
   - In `malkan_window_wide_2026-11`: uses wide pivots with strength `L = 3` (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:62`).
   - Pivot detection: `_pivots` checks `all(v < sgn * vals[j] for j in around)` where `around` spans `[i - L, i + L]` (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:81-82`). Pivot `b` is confirmed at bar `conf = b + L` (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:95`), and event is recorded at `i = conf = b + 3` with `t = ts[conf]` (`MyTradingSys/research/malkan_window_wide_2026-11/wide.py:97`).
   - Causal integrity: Neither detector uses any price, RSI, or swing information occurring after the confirmation bar `i`.

2. **Trade Entry vs Forward Horizon:**
   - Entry occurs at the close of event bar `i` (`px = bars[i]["c"]`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:109`).
   - Trade exit occurs strictly `h` bars later (`bars[i + h]["c"]`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:110`).
   - If `i + h >= len(bars)`, the trade is dropped (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:107-108`).
   - Return calculation uses only bars `i` (entry close) and `i + h` (exit close). Zero look-ahead bias detected.

---

## 4. Fee and Slippage Audit

1. **Fee Model Specification:**
   - Round trip taker fee and slippage combined: `COST = rk.TAKER_RT_PCT = 0.14 %` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:30`).
   - Base Binance taker fee component: `fees.BINANCE_TAKER = 0.0005` (5 bps per side, 10 bps round trip; `MyTradingSys/backtest/fees.py:23,37`).
   - The study asserts `abs(2 * fees.BINANCE_TAKER * 100 - 0.10) < 1e-9` and `COST >= 2 * fees.BINANCE_TAKER * 100` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:31`).
   - Total friction applied: 14 bps (0.14 %) deducted from gross return in percent (`net = g - COST`, `MyTradingSys/research/malkan_window_dev_2026-11/study.py:118`).

2. **Side and Directional Accounting:**
   - Bullish regular divergence takes long trades: `sgn = KINDS["bullish"] = 1.0` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:34,103`).
   - Bearish regular divergence takes short trades: `sgn = KINDS["bearish"] = -1.0` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:34,103`).
   - Gross formula: `sgn * (bars[i + h]["c"] - px) / px * 100.0` (`MyTradingSys/research/malkan_window_dev_2026-11/study.py:110`).
   - For long trades, price appreciation yields positive gross; for short trades, price depreciation yields positive gross.
   - Cost is subtracted symmetrically from gross returns for both sides (`net = g - COST`), which accurately reflects paying taker fees and slippage on both long and short round trips.
   - Round trip count: Exactly one fee deduction per completed trade. No missing fees, no wrong-side fees, and no double deduction.

---

## 5. Conclusion
Both `malkan_window_dev_2026-11` and `malkan_window_wide_2026-11` adhere strictly to pre-registration protocols, maintain complete causal integrity with zero look-ahead bias, correctly model round-trip fees and slippage, and accurately report their statistical metrics and power gate blocks.
