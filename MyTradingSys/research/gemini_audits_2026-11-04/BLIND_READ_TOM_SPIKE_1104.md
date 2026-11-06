# Blind Read Audit: `tom_spike_level.py` and `desk-trades-tom_spike_level-2026-11-04.json`

- **Card**: `gemini-blind-read-tom-spike-level-py-sim`
- **Audited Study Script**: `MyTradingSys/research/sim_desk/studies/tom_spike_level.py`
- **Audited Result JSON**: `MyTradingSys/research/sim_desk/results/desk-trades-tom_spike_level-2026-11-04.json`
- **Auditor**: Gemini (independent blind read worker)
- **Date**: 2026-11-05 UTC / local

---

## 1. Executive Summary & Parameter Provenance

In accordance with MTS protocol and `MOVED_RULES.md`, every parameter and metric is strictly classified as either **SOURCED** (directly referenced from trader source transcripts) or **OURS** (system/algorithmic defaults, simulator parameters, or empirical recomputations):

### SOURCED Parameters & Concepts
Quoted from `MyTradingSys/research/sim_desk/studies/tom_spike_level.py:5-6`:
- **Idea**: `"there's no liquidity left"` after a push at the session top (`k0zm5NYn0IQ:21-22`). [SOURCED]
- **Stop**: `"above the bell"` (`n7ZSkjb7JXs:299-301`). [SOURCED]
- **Target**: `"the entire distance below the start of the impulse"` (`T6hDJcHrVBM:170-172`). [SOURCED]
- **Level**: Session extreme. [SOURCED]

### OURS Parameters & Simulator Implementation Defaults
Quoted from `MyTradingSys/research/sim_desk/studies/tom_spike_level.py:7-12` and lines 22–30:
- **Session definition**: UTC day as the session (`00:00..24:00 UTC`), whereas Tom trades `08:30/09:00-17:35 Berlin cash` (BTC has no cash hours). [OURS]
- **Signal timeframe**: 5-minute bars (`BAR = 5`, `tom_spike_level.py:24`). [OURS]
- **Push definition**: Lookback of $N=6$ 5m bars spanning at least $K=4.0 \times \text{ATR14}$ (simple mean of true range) and printing a new high/low of the day (`n_push = 6`, `k_atr = 4.0`, `tom_spike_level.py:8,30`). [OURS]
- **Confirmation window**: Wait up to 3 5m candles (`CONFIRM = 3`, `tom_spike_level.py:25`) for a close beyond the spike candle's far side (below its low for short, above its high for long); invalidated if a new extreme prints first. [OURS]
- **Entry**: Market entry at next 5m open (`tom_spike_level.py:10,133-137`). [OURS]
- **Stop floor**: Spike extreme, widened to at least 0.40% from entry (`MIN_STOP = 0.4`, `tom_spike_level.py:26,139-140`). [OURS]
- **Target**: Push window origin (`start = l[w0:i+1].min()` for short, `h[w0:i+1].max()` for long, `tom_spike_level.py:109,144`). [OURS]
- **Time exit**: End of the UTC day (`t_hold = (t0 // DAY + 1) * DAY`, `tom_spike_level.py:12,143`). [OURS]
- **Fee regime & slippage**: Binance maker 0.02%, taker 0.05%, market/stop slippage 0.02% (`maker_pct = 0.02`, `taker_pct = 0.05`, `slip_pct = 0.02`, `tom_spike_level.py:30`). [OURS]
- **Window**: DEV window `2022-04-01..2024-06-30` (`tom_spike_level.py:30`). [OURS]

---

## 2. Independent Headline Numbers Recomputation

Using independent scripts directly parsing `results/desk-trades-tom_spike_level-2026-11-04.json` (specifically the 1,399 exported trades under `examples[0]['trades']`), every headline metric and statistical property was independently recomputed from first principles.

### Core Metrics Table
- **Total Filled Trades ($n$)**: 1,399 [OURS]
- **Total Net R**: $-311.1741$ R [OURS]
- **Mean Net R per Trade**: $-0.222426$ R [OURS] (rounds to $-0.222$ R)
- **Total Gross R**: $-10.4294$ R [OURS]
- **Mean Gross R per Trade**: $-0.007455$ R [OURS] (rounds to $-0.007$ R)
- **Mean Fee per Trade**: $0.214971$ R [OURS] (rounds to $0.215$ R)
- **Standard Deviation of Net R ($s$)**: $0.938426$ R [OURS]
- **Standard Error of Mean Net R ($SE$)**: $0.025089$ R [OURS]
- **Net Win Count**: 695 trades [OURS]
- **Net Win Rate**: $695 / 1399 = 49.6783\%$ [OURS] (rounds to $49.68\%$)
- **Gross Win Count**: 821 trades [OURS]
- **Gross Win Rate**: $821 / 1399 = 58.6848\%$ [OURS] (rounds to $58.68\%$)
- **Exit Breakdown**:
  - `T1` (Target hit): 781 trades ($55.83\%$) [OURS]
  - `STOP` (Stop loss hit): 537 trades ($38.38\%$) [OURS]
  - `HOLD` (End-of-day time exit): 81 trades ($5.79\%$) [OURS]
  - Total: $781 + 537 + 81 = 1,399$ trades [OURS]
- **Sides Breakdown**:
  - `SHORT` ($s = -1$, fade spike up): 719 trades ($51.39\%$) [OURS]
  - `LONG` ($s = +1$, fade spike down): 680 trades ($48.61\%$) [OURS]
  - Total: $719 + 680 = 1,399$ trades [OURS]
- **Profit Factor (Net)**: $\sum R_{\text{win}} / \sum |R_{\text{loss}}| = 398.2435 / 709.4176 = 0.56138$ [OURS]
- **Max Drawdown (Net R)**: $312.1555$ R [OURS]
- **Cumulative Curve Final Net R**: $-311.1741$ R (`cum[-1]`, matching trade sum exactly) [OURS]

### Day-Bootstrap 95% Confidence Interval Recomputation
Recomputed with the simulator's day-block bootstrap (`ladder_run.Boot(all_dev_days)` across all 822 DEV days from `2022-04-01` to `2024-06-30`, seed 42):
- **Bootstrap Mean Net R**: $-0.222426$ R [OURS]
- **Bootstrap 95% CI Lower Bound (`lo`)**: $-0.269493$ R $\rightarrow$ rounds to $-0.269$ R [OURS]
- **Bootstrap 95% CI Upper Bound (`hi`)**: $-0.176289$ R $\rightarrow$ rounds to $-0.176$ R [OURS]
- **Range String**: `"-0.269 to -0.176 R"` [OURS]

---

## 3. Per-Number Match Table (Stated JSON vs Independently Recomputed)

| Headline Metric / Item | Stated in JSON (`results/...json`) & Line | Independently Recomputed Value | Label | Match Status |
|---|---|---|---|---|
| Study ID | `"id": "desk-trades-tom_spike_level-2026-11-04"` (`line 2`) | `desk-trades-tom_spike_level-2026-11-04` | OURS | MATCH |
| Window | `"DEV only, 2022-04-01 to 2024-06-30..."` (`line 23`) | `2022-04-01 to 2024-06-30` (822 days) | OURS | MATCH |
| Filled Trades Count ($n$) | `"value": "1399"` (`line 28`), `"trades_exported": 1399` (`line 371542`), `"n": 1399` (`line 371544`) | `len(trades) = 1399` | OURS | MATCH |
| Average Net R per Trade | `"value": "-0.222 R"` (`line 29`), `"net_r": -0.222` (`line 371544`) | `-0.222426 R` (rounds to `-0.222 R`) | OURS | MATCH |
| 95% Confidence Range | `"value": "-0.269 to -0.176 R"` (`line 30`) | `[-0.269493, -0.176289]` $\rightarrow$ `-0.269 to -0.176 R` | OURS | MATCH |
| Try Number | `"value": "1"` (`line 31`), `"try_no": 1` (`line 371544`) | `1` | OURS | MATCH |
| Verdict Label | `"label": "FAILED"` (`line 24`), `"verdict": "FAILED"` (`line 371544`) | `FAILED` (entire 95% CI below 0) | OURS | MATCH |
| Verdict Reason Text | `"the whole 95 % range of the average -0.269 to -0.176 R is below zero: it loses money after fees"` (`line 26`) | Verified: $hi = -0.176 < 0.0$ | OURS | MATCH |
| Cumulative Final Net R | `-311.1741` (`line 371540`) | `sum(r) = -311.1741` | OURS | MATCH |
| Study Defaults in `tom_spike_level.py` | `symbol='BTCUSDT', sides='BOTH', n_push=6, k_atr=4.0, maker_pct=0.02, taker_pct=0.05, slip_pct=0.02` (`tom_spike_level.py:30`) | Matches JSON `what` & `title` parameter specification | OURS | MATCH |

---

## 4. Verdict Application Analysis

The simulator desk applies strict gating rules (`desk.py:verdict`):
1. $n < 30 \implies$ `NOT ENOUGH DATA`
2. $n \ge 30$:
   - If entire 95% range is below 0 ($hi \le 0$) $\implies$ `FAILED`
   - If entire 95% range is above 0 ($lo > 0$) $\implies$ `PASSED`
   - If 95% range spans 0 $\implies$ `INCONCLUSIVE` / `NOT ENOUGH DATA`

Here, $n = 1,399 \ge 30$, and the 95% bootstrap range $[-0.269, -0.176]$ R is strictly negative. Thus, `verdict = FAILED` is 100% compliant with the engine specification.

---

## 5. Final Audit Verdict

VERDICT: MATCH
