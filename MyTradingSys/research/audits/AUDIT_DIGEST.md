# Audit digest (T056)
Generated: 2026-09-29T11:45:35Z
Open findings shown: 2 (capped at 40). Closed: 0.
Dropped (QUOTE not confirmed near the claimed line): 7.
Dropped by reason: line_off=5, quote_not_found=2; duplicates merged=0.

- [914-audit-a1-bt-stats-sharpe:d8746514ee] A1 H MyTradingSys/backtest/bt/bt_stats.py:42 | The implementation uses sample standard deviation (n-1) instead of population standard deviation (n) as specified in FORMULAS.md | fix: Change to use population standard deviation calculation
- [098-audit-a7-risk-guard:b35f49ffb7] A7 M MyTradingSys/execution/risk_guard.py:25 | The function does not validate that position_size_contracts is a valid number (e.g., not NaN or infinity). If such invalid inputs are passed, they could cause unexpected behavior in calculations. | fix: Add validation to ensure position_size_contracts is a finite number before proceeding with the calculation.