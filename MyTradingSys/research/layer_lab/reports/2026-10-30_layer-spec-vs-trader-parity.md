# Layer Spec vs Trader Parity Report

- **Date:** 2026-10-30
- **Auditor:** Gemini (Antigravity / JIS-NUC)
- **Task:** `layer-spec-vs-trader-parity`
- **Artifacts Created:**
  - `MyTradingSys/research/wiring_audit_2026-10/PARITY_AUDIT.md`
  - `MyTradingSys/research/wiring_audit_2026-10/PARITY_UNSOURCED.csv`

---

## 1. File:Line Verification Script Check

```python
import csv, os

with open('MyTradingSys/research/wiring_audit_2026-10/PARITY_UNSOURCED.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

for r in rows:
    ref = r['code_file_line']
    file_path, line_no = ref.split(':')
    assert os.path.exists(file_path), f"Missing file: {file_path}"
    with open(file_path, encoding='utf-8', errors='ignore') as fp:
        lines = fp.readlines()
    assert 1 <= int(line_no) <= len(lines), f"Line out of range: {ref}"
    print(f"VERIFIED: {r['layer']} -> {ref} ({len(lines)} total lines)")
```

### Verification Output:
- `rsi` -> `MyTradingSys/backtest/layers/rsi/krown_hidden_divergence.py:11` (48 total lines) - OK
- `kurisko` -> `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:5` (112 total lines) - OK
- `kurisko` -> `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:4` (112 total lines) - OK
- `wavetrend` -> `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:19` (109 total lines) - OK
- `pizzino` -> `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:10` (182 total lines) - OK
- `pitchfork` -> `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:10` (539 total lines) - OK
- `trendlines` -> `MyTradingSys/backtest/layers/trendlines/trendline_core.py:23` (325 total lines) - OK
- `alerts` -> `MyTradingSys/backtest/layers/alerts/alert_emitter.py:2` (93 total lines) - OK
- `krown` -> `MyTradingSys/backtest/layers/krown/krown_core.py:20` (394 total lines) - OK
- `fabio` -> `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:50` (185 total lines) - OK

---

## 2. Layers Covered vs Not Covered
- **Covered (Enforcing Trader Rules):** `rsi`, `krown`, `fabio`, `kurisko`, `pizzino`, `wavetrend`, `pitchfork`, `trendlines`.
- **Not Covered (Infrastructure Only):** `alerts` (testnet event formatting & JSONL sink, no trader rules).
