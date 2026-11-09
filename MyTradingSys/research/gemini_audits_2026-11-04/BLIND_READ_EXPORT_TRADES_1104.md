FOUND=28 DIFF=0 NOT_IN_DATA=0

# Blind Read Audit: sim_desk `export_trades.py` and `studies/_bars.trade_rows` (`2026-11-04`)

- **Card**: `gemini-blind-read-export-trades-py-bars-` (D11 feeder check `A-20261104-1`)
- **Date**: `2026-11-04`
- **Audited Modules**:
  1. `MyTradingSys/research/sim_desk/export_trades.py`
  2. `MyTradingSys/research/sim_desk/studies/_bars.py` (`trade_rows`, `replay`, `run_trade`, `collect`)
- **Audited Stated Results**:
  1. `MyTradingSys/research/sim_desk/results/desk-trades-fabio_v3-c-2026-11-04.json`
  2. `MyTradingSys/research/sim_desk/results/desk-trades-fabio_v3-b-2026-11-04.json`
  3. `MyTradingSys/research/sim_desk/results/desk-trades-tom_vp-fade-2026-11-04.json`
  4. `MyTradingSys/research/sim_desk/results/desk-trades-tom_spike_level-2026-11-04.json`
  5. `MyTradingSys/research/sim_desk/results/desk-trades-fabio_v3-ad-2026-11-04.json`
  6. Git commit `ed0f702ce56b` commit message headline summary

---

## 1. Parameter & Formula Provenance (`SOURCED` vs `OURS`)

- **Fee Structure (`maker_pct = 0.02%`, `taker_pct = 0.05%`)**: `SOURCED` (`MyTradingSys/backtest/fees.py:1-17` `BINANCE_MAKER = 0.0002`, `BINANCE_TAKER = 0.0005`; cited in `studies/_bars.py:16,24-27`).
- **Slippage Model (`slip_pct = 0.02%` = 2 bps against market & stop fills; 0% on limit fills)**: `SOURCED` (`MyTradingSys/backtest/layers/FORMULAS.md:353` `slip_rt default 0.0002 = 2 bps RT`, `studies/_bars.py:23-27`).
- **R-Multiple Definition (`gross_r` and `fee_r` normalization)**: `SOURCED` (`MyTradingSys/backtest/layers/FORMULAS.md:659` Section 28.4 / Section 17):
  - `risk = side * (entry_px - stop_px)` (must be positive; non-positive aborts trade).
  - `gross_r = side * (exit_px - entry_px) / risk`.
  - `fee_r = (taker_rate * entry_px + exit_fee_rate * exit_px) / risk` where `taker_rate = (taker_pct + slip_pct) / 100` and `exit_fee_rate` is taker (stop / time / signal exit) or maker (limit target exit).
  - `net_r = gross_r - fee_r` (`studies/_bars.py:174-178`).
- **Percentage Ladders for Public Export (`d`, `t0`, `s`, `entry`, `stop`, `target`, `exit`, `bars`, `gross_r`, `r`, `l2`, `t1`, `t2`)**: `OURS` (`MyTradingSys/research/sim_desk/studies/_bars.py:229-247` `trade_rows`). Values represent signed percentage distance from fill price: `pct(v) = side * (v - entry_px) / entry_px * 100`.
- **Date Window (`DEV = 2022-04-01 to 2024-06-30`, warm-up from `2022-01-01`, cutoff `2024-07-01 UTC`)**: `SOURCED` (`MyTradingSys/research/sim_desk/studies/_bars.py:21-22,81-89`, `CUT_MS = 1719792000000`).

---

## 2. Recomputed Headline Metrics vs Stated Results

Headline numbers independently recomputed directly from the 1m bar series (`studies/_bars.load_1m`) replaying signals through `_bars.trade_rows` and compared against the stated result documents:

### 2.1 Summary Headline Match Table

| Export Run Name | Metric Description | Raw / Recomputed Value (`OURS`) | Stated Value in JSON / Commit (`SOURCED`) | Source Reference | Status |
|---|---|---|---|---|---|
| `fabio_v3-c` | Filled trades ($N$) | `518` | `518` | `desk-trades-fabio_v3-c-2026-11-04.json:46` | `MATCH` |
| `fabio_v3-c` | Average net R per trade | `+0.062 R` (`+0.061689 R`) | `+0.062 R` | `desk-trades-fabio_v3-c-2026-11-04.json:47` | `MATCH` |
| `fabio_v3-c` | 95% bootstrap CI range | `-0.135 to +0.268 R` | `-0.135 to +0.268 R` | `desk-trades-fabio_v3-c-2026-11-04.json:48` | `MATCH` |
| `fabio_v3-c` | Verdict | `NOT ENOUGH DATA` | `NOT ENOUGH DATA` | `desk-trades-fabio_v3-c-2026-11-04.json:45` | `MATCH` |
| `fabio_v3-c` | Cumulative Net R | `+31.9543 R` | `+31.9543 R` | `desk-trades-fabio_v3-c-2026-11-04.json:51` (`cum[-1]`) | `MATCH` |
| `fabio_v3-c` | Wins / Losses / Win Rate | `164 / 354 (31.66%)` | `164 / 354 (31.66%)` | `desk-trades-fabio_v3-c-2026-11-04.json:51` | `MATCH` |
| `fabio_v3-c` | Trades exported | `518` | `518` | `desk-trades-fabio_v3-c-2026-11-04.json:53` | `MATCH` |
| `fabio_v3-b` | Filled trades ($N$) | `64` | `64` | `desk-trades-fabio_v3-b-2026-11-04.json:46` | `MATCH` |
| `fabio_v3-b` | Average net R per trade | `-0.445 R` (`-0.445060 R`) | `-0.445 R` | `desk-trades-fabio_v3-b-2026-11-04.json:47` | `MATCH` |
| `fabio_v3-b` | 95% bootstrap CI range | `-0.694 to -0.186 R` | `-0.694 to -0.186 R` | `desk-trades-fabio_v3-b-2026-11-04.json:48` | `MATCH` |
| `fabio_v3-b` | Verdict | `FAILED` | `FAILED` | `desk-trades-fabio_v3-b-2026-11-04.json:45` | `MATCH` |
| `fabio_v3-b` | Cumulative Net R | `-28.4839 R` | `-28.4839 R` | `desk-trades-fabio_v3-b-2026-11-04.json:51` (`cum[-1]`) | `MATCH` |
| `fabio_v3-b` | Wins / Losses / Win Rate | `25 / 39 (39.06%)` | `25 / 39 (39.06%)` | `desk-trades-fabio_v3-b-2026-11-04.json:51` | `MATCH` |
| `fabio_v3-b` | Trades exported | `64` | `64` | `desk-trades-fabio_v3-b-2026-11-04.json:53` | `MATCH` |
| `tom_vp-fade` | Filled trades ($N$) | `2052` | `2052` | `desk-trades-tom_vp-fade-2026-11-04.json:46` | `MATCH` |
| `tom_vp-fade` | Average net R per trade | `-0.247 R` (`-0.246997 R`) | `-0.247 R` | `desk-trades-tom_vp-fade-2026-11-04.json:47` | `MATCH` |
| `tom_vp-fade` | 95% bootstrap CI range | `-0.285 to -0.211 R` | `-0.285 to -0.211 R` | `desk-trades-tom_vp-fade-2026-11-04.json:48` | `MATCH` |
| `tom_vp-fade` | Verdict | `FAILED` | `FAILED` | `desk-trades-tom_vp-fade-2026-11-04.json:45` | `MATCH` |
| `tom_vp-fade` | Cumulative Net R | `-506.8366 R` | `-506.8366 R` | `desk-trades-tom_vp-fade-2026-11-04.json:51` (`cum[-1]`) | `MATCH` |
| `tom_vp-fade` | Wins / Losses / Win Rate | `785 / 1267 (38.26%)` | `785 / 1267 (38.26%)` | `desk-trades-tom_vp-fade-2026-11-04.json:51` | `MATCH` |
| `tom_vp-fade` | Trades exported | `2052` | `2052` | `desk-trades-tom_vp-fade-2026-11-04.json:53` | `MATCH` |
| `tom_spike_level` | Filled trades ($N$) | `1399` | `1399` | `desk-trades-tom_spike_level-2026-11-04.json:46` | `MATCH` |
| `tom_spike_level` | Average net R per trade | `-0.222 R` (`-0.222427 R`) | `-0.222 R` | `desk-trades-tom_spike_level-2026-11-04.json:47` | `MATCH` |
| `tom_spike_level` | 95% bootstrap CI range | `-0.269 to -0.176 R` | `-0.269 to -0.176 R` | `desk-trades-tom_spike_level-2026-11-04.json:48` | `MATCH` |
| `tom_spike_level` | Verdict | `FAILED` | `FAILED` | `desk-trades-tom_spike_level-2026-11-04.json:45` | `MATCH` |
| `tom_spike_level` | Cumulative Net R | `-311.1741 R` | `-311.1741 R` | `desk-trades-tom_spike_level-2026-11-04.json:51` (`cum[-1]`) | `MATCH` |
| `tom_spike_level` | Wins / Losses / Win Rate | `695 / 704 (49.68%)` | `695 / 704 (49.68%)` | `desk-trades-tom_spike_level-2026-11-04.json:51` | `MATCH` |
| `tom_spike_level` | Trades exported | `1399` | `1399` | `desk-trades-tom_spike_level-2026-11-04.json:53` | `MATCH` |

---

## 3. Exit Breakdown Cross-Verification

Recomputed exit reasons from `_bars.trade_rows` matching the underlying trade simulations:

- `fabio_v3-c` (518 trades):
  - `STOP`: 309 trades (`59.65%`)
  - `HOLD` (time-out at session close): 209 trades (`40.35%`)
  - `T1` (target): 0 trades (Model C exits via stop or session close rule)
- `fabio_v3-b` (64 trades):
  - `STOP`: 37 trades (`57.81%`)
  - `T1`: 19 trades (`29.69%`)
  - `HOLD`: 8 trades (`12.50%`)
- `tom_vp-fade` (2052 trades):
  - `STOP`: 426 trades (`20.76%`)
  - `T1`: 858 trades (`41.81%`)
  - `SIGNAL`: 647 trades (`31.53%`)
  - `HOLD`: 121 trades (`5.90%`)
- `tom_spike_level` (1399 trades):
  - `STOP`: 537 trades (`38.38%`)
  - `T1`: 781 trades (`55.83%`)
  - `HOLD`: 81 trades (`5.79%`)

---

## 4. `NOT_MEASURED` Status Verification

- `fabio_v3-ad`:
  - Result ID: `desk-trades-fabio_v3-ad-2026-11-04`
  - Verdict: `NOT MEASURED` (`tone: warn`)
  - Filled trades: `0`
  - Reason: `studies/fabio_v3.py` Models A and D require order flow features (CVD and delta) which only start 2024-12-02, whereas the DEV window ends 2024-06-30. Correctly unmeasured on DEV.

---

## 5. Verdict

Every headline number of `sim_desk/export_trades.py` and `studies/_bars.trade_rows` was independently verified and matches the stated backtest results with zero discrepancy.

VERDICT: MATCH
