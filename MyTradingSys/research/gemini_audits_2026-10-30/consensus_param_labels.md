# Consensus Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-consensus`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/consensus` code, find its source (analyst extract, FORMULAS.md, architecture spec, or none), and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 7
- **SOURCED count**: 4
- **OURS count**: 3
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/consensus/`)

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `consensus` | Root path relative depth | `MyTradingSys/backtest/layers/consensus/hook.py:28` | `parents[4]` | OURS | Repository filesystem layout navigation (`parents[4]` resolves to `<repo>` from `hook.py`). |
| `consensus` | Hook poll Tom alert trigger comparison | `MyTradingSys/backtest/layers/consensus/hook.py:120` | `tom["alert_no"] > seen` | OURS | Software design state machine rule: polls only emit a consensus row for new Tom alert numbers not yet processed by the hook. |
| `consensus` | Root path relative depth | `MyTradingSys/backtest/layers/consensus/writer.py:41` | `parents[4]` | OURS | Repository filesystem layout navigation (`parents[4]` resolves to `<repo>` from `writer.py`). |
| `consensus` | Millisecond timestamp divisor | `MyTradingSys/backtest/layers/consensus/writer.py:75` | `1000` | SOURCED | ISO-8601 millisecond format requirement from architecture specification; `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:33` ("utc_timestamp: ISO-8601 with ms"). |
| `consensus` | Required core Tom dictionary keys | `MyTradingSys/backtest/layers/consensus/writer.py:44` | 7 keys (`verdict`, `setup`, `side`, `entry`, `stop`, `target`, `net_rr`) | SOURCED | Quote: `"tom: {verdict, setup, side, entry, stop, target, net_rr}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:37`. |
| `consensus` | Required core Fabio dictionary keys | `MyTradingSys/backtest/layers/consensus/writer.py:45` | 6 keys (`verdict`, `model`, `side`, `entry`, `stop`, `target`) | SOURCED | Quote: `"fabio: {verdict, model, side, entry, stop, target}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:38`. |
| `consensus` | Required baseline RSI timeframes | `MyTradingSys/backtest/layers/consensus/writer.py:46` | 6 timeframes (`1m`, `3m`, `15m`, `1h`, `4h`, `1d`) | SOURCED | Quote: `"rsi: {1m, 3m, 15m, 1h, 4h, 1d}"` in `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:39`. |

---

## 2. Details and Observations

1. **Architecture Doctrine Alignment**:
   - `layers/consensus` is an observation-only sink (`README.md:1-20`, `hook.py:1-16`, `writer.py:1-29`). It contains no indicator calculations, thresholds, entry multipliers, or strategy tuning parameters.
   - The structural constants (`TOM_KEYS`, `FABIO_KEYS`, `RSI_TFS`, and timestamp format) are verbatim implementations of the specifications set forth in `ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43`.
2. **State & Path Defaults**:
   - File system hierarchy resolutions (`parents[4]`) and hook state-tracking comparisons (`alert_no > seen`) are internal infrastructure defaults (`OURS`).
   - No unlabeled numeric thresholds exist in the layer codebase.
