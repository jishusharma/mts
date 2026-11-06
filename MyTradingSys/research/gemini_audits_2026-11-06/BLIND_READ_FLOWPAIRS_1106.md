# Blind Read Audit: `flow_state_pairs_1m.py` (`FLOW_STATE_PAIRS_1M.md`)

- **Card**: `gemini-blind-read-of-flow-state-pairs-1m`
- **Audited File**: `MyTradingSys/research/eagle_eyes_picture_2026-10-28/flow_state_pairs_1m.py`
- **Companion Report**: `MyTradingSys/research/eagle_eyes_picture_2026-10-28/FLOW_STATE_PAIRS_1M.md`
- **Date**: 2026-11-06 UTC

## 1. Flow-State Pair Definitions & As-Of Timing Audit

1. **Flow-State Pair Definitions (`flow_state_pairs_1m.py:27-37`, all thresholds `OURS`)**:
   - **Net Delta (`d`)**: `2 * taker_buy_volume - volume` (in BTC) per 1m bar (`flow_state_pairs_1m.py:138`).
   - **Burst threshold (`thr`)**: `|d| >= P95(|d|)` over the window (`BURST_PCT = 0.95`, `flow_state_pairs_1m.py:12,47-49`; `120.9 BTC` on the 13-day Binance window, `53.8 BTC` on the 2026-10-28 Bybit day).
   - **5m OI bucket change (`doi`)**: `OI_THR = 0.0005` (`0.05%`, `flow_state_pairs_1m.py:13`).
   - **Case A (negative burst + OI up)**: `abs(d) >= thr`, `d < 0`, and `doi >= +0.05%` (`flow_state_pairs_1m.py:31-32`).
   - **Case B (positive burst + OI up + green bar + 5-bar CVD > 0, "all positive")**: `abs(d) >= thr`, `d > 0`, `doi >= +0.05%`, `close > open` (`bar['c'] > bar['o']`), and 5-bar net delta sum `cvd[i] - cvd[i-5] > 0` (`flow_state_pairs_1m.py:35-36, 62`).
   - **Case C (positive burst + OI down)**: `abs(d) >= thr`, `d > 0`, and `doi <= -0.05%` (`flow_state_pairs_1m.py:33-34`).

2. **As-Of Rule / Look-Ahead Check**:
   - **OI bucket alignment (`oi_change`, `flow_state_pairs_1m.py:19-24`)**: For a 1m bar opening at `t` and closing at `t + 60`, `s = (t + 60) // 300 * 300` is the latest 5m timestamp `<= t + 60`, and `doi = oi[s] / oi[s - 300] - 1`. No OI reading after `t + 60` is ever accessed.
   - **5-bar CVD change (`flow_state_pairs_1m.py:55-62`)**: `cvd[i] - cvd[i - 5]` sums `d[i-4 .. i]`, using only bars up to and including bar `i`.
   - **Forward returns (`forward`, `flow_state_pairs_1m.py:40-44`)**: `bars[i + h]['c'] / bars[i]['c'] - 1` for `h in (15, 30, 60)` is used strictly as the dependent outcome variable.
   - **Note on `burst_threshold(bars)` (`flow_state_pairs_1m.py:47-49`)**: The P95 burst threshold is computed across the 13-day descriptive `SEEN` window (`FLOW_STATE_PAIRS_1M.md:4` explicitly labels the study `DESCRIPTIVE, SEEN window, no fees, no out-of-sample split`). Within each bar's feature alignment (`oi_change` and `cvd5`), no bar after `t` is used.

## 2. Per-Claim Recomputation Table (`flow_state_pairs_1m.py` vs `FLOW_STATE_PAIRS_1M.md`)

| Claim / Metric | Recomputed Value / Code Reference (`OURS`) | Stated in `FLOW_STATE_PAIRS_1M.md` | Status |
|---|---|---|---|
| Window bar count & P95 burst threshold | `18,720` 1m bars (`10-22..11-04` minus `10-28`), `4,032` OI pts, `thr = 120.9 BTC` (`flow_state_pairs_1m.py:141`) | `18,720` bars, P95 = `120.9 BTC` (`L8, L11`) | MATCH |
| Case A counts & medians (15m / 30m / 60m) | `n=160` (`99` decimated 1/15m), `+0.030% (57%)`, `+0.004% (51%)`, `+0.063% (53%)` | `160 | 99 | +0.030% | 57% | +0.004% | 51% | +0.063% | 53%` (`L19`) | MATCH |
| Case B counts & medians (15m / 30m / 60m) | `n=128` (`90` decimated 1/15m), `-0.005% (49%)`, `-0.026% (46%)`, `+0.029% (54%)` | `128 | 90 | -0.005% | 49% | -0.026% | 46% | +0.029% | 54%` (`L20`) | MATCH |
| Case C counts & medians (15m / 30m / 60m) | `n=177` (`104` decimated 1/15m), `-0.061% (39%)`, `-0.054% (44%)`, `-0.072% (42%)` | `177 | 104 | -0.061% | 39% | -0.054% | 44% | -0.072% | 42%` (`L21`) | MATCH |
| 2026-10-28 Bybit day counts & P95 | `1,440` bars, P95 `53.8 BTC`, `A=8, B=6, C=12` (`flow_state_pairs_1m.py:160`) | `53.8 BTC`, `A 8, B 6, C 12` (`L31`) | MATCH |
| 2026-10-28 20:46Z Shot A | `o 81063.0 c 80950.9`, `delta -95.3`, `cvd5 -84.6`, `OI5m +0.275%`, `case A`, fwd `+0.387% / +0.555% / +0.415%` | `-95.3 | -84.6 | +0.275% | A | +0.39 / +0.56 / +0.42%` (`L35`) | MATCH |
| 2026-10-28 20:56Z Shot B | `o 81170.1 c 81233.3`, `delta +80.0`, `cvd5 +115.7`, `OI5m +0.077%`, `case B`, fwd `+0.043% / +0.041% / +0.117%` | `+80.0 | +115.7 | +0.077% | B | +0.04 / +0.04 / +0.12%` (`L36`) | MATCH |
| 2026-10-28 20:00Z Shot C | `o 81549.4 c 81664.2`, `delta +85.0`, `cvd5 +199.5`, `OI5m -0.125%`, `case C`, fwd `-0.539% / -0.721% / -0.444%` | `+85.0 | +199.5 | -0.125% | C | -0.54 / -0.72 / -0.44%` (`L37`) | MATCH |
| As-of rule in `oi_change(oi, t)` | `s = (t + 60) // 300 * 300`, `oi[s] / oi[s - 300] - 1` (`flow_state_pairs_1m.py:22-24`) | Uses only 5m OI bucket ending at or before bar close `t+60` | MATCH |

VERDICT: MATCH

