# Layer Lab Report: `gemini-blind-read-tom-spike-level-py-sim`

- **Card**: `gemini-blind-read-tom-spike-level-py-sim`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_TOM_SPIKE_1104.md`
- **Audited Files**:
  - `MyTradingSys/research/sim_desk/studies/tom_spike_level.py` (lines 1–158)
  - `MyTradingSys/research/sim_desk/results/desk-trades-tom_spike_level-2026-11-04.json` (lines 1–371556)
- **Verdict**: `VERDICT: MATCH` (`DIFF=0` across all headline metrics, trade counts, bootstrap confidence intervals, and engine verdict).

## Findings

1. **Parameter Provenance & Classification (`SOURCED` vs `OURS`)**:
   - Quoted from `tom_spike_level.py:5-6` [SOURCED]:
     - Liquidity concept: `"there's no liquidity left"` after session top push (`k0zm5NYn0IQ:21-22`).
     - Stop placement: `"above the bell"` (`n7ZSkjb7JXs:299-301`).
     - Profit target: `"the entire distance below the start of the impulse"` (`T6hDJcHrVBM:170-172`).
     - Reference level: Session extreme.
   - Quoted from `tom_spike_level.py:7-12,24-30` [OURS]:
     - Session: UTC day (`00:00..24:00 UTC`).
     - Timeframe: 5-minute candles (`BAR = 5`).
     - Push lookback and ATR threshold: $N=6$ 5m bars, $K=4.0 \times \text{ATR14}$ (`n_push = 6, k_atr = 4.0`).
     - Confirmation window: 3 candles (`CONFIRM = 3`) for close past spike bar far side.
     - Entry: Market order at next candle open.
     - Stop widening floor: Minimum 0.40% (`MIN_STOP = 0.4`).
     - Target: Push window origin.
     - Time exit: End of UTC day.
     - Fee regime: Binance maker 0.02%, taker 0.05%, slip 0.02%.
     - Window: DEV `2022-04-01..2024-06-30`.

2. **Headline Numbers Recomputation from Raw Data (`desk-trades-tom_spike_level-2026-11-04.json`)**:
   - **Trade count ($n$)**: 1,399 filled trades (matches `"filled trades": "1399"` at `line 28` and `"trades_exported": 1399` at `line 371542`). [OURS]
   - **Net Mean R per trade**: $-0.222426$ R, rounding to stated $-0.222$ R (matches `"average per trade, after fees": "-0.222 R"` at `line 29` and `"net_r": -0.222` at `line 371544`). [OURS]
   - **Total Net R**: $-311.1741$ R (matches cumulative curve terminal value `cum[-1] = -311.1741` at `line 371540`). [OURS]
   - **Day-Bootstrap 95% Confidence Interval**: $[-0.269493, -0.176289]$ R, rounding to stated `"-0.269 to -0.176 R"` (matches `"95 % range": "-0.269 to -0.176 R"` at `line 30` and why statement at `line 26`). [OURS]
   - **Gross Mean R per trade**: $-0.007455$ R (total gross R: $-10.4294$ R). [OURS]
   - **Mean Fee per trade**: $0.214971$ R. [OURS]
   - **Win Rate (Net)**: $695 / 1399 = 49.68\%$. [OURS]
   - **Win Rate (Gross)**: $821 / 1399 = 58.68\%$. [OURS]
   - **Exit Breakdown**: Target (`T1`): 781 ($55.83\%$), Stop (`STOP`): 537 ($38.38\%$), Time exit (`HOLD`): 81 ($5.79\%$). [OURS]
   - **Side Breakdown**: Short ($s = -1$): 719 ($51.39\%$), Long ($s = +1$): 680 ($48.61\%$). [OURS]
   - **Max Drawdown (Net R)**: $312.1555$ R. [OURS]

3. **Verification Command**:
   - `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_TOM_SPIKE_1104.md'); assert p.exists() and 'VERDICT: MATCH' in p.read_text()"` exits 0. [OURS]
