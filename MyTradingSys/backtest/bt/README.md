# MyTradingSys/backtest/bt/  - backtest engine v2 (T051 L3/L4), 2026-09-27
Built by the NUC worker from specs 011-014 (Dumps/workers/NUC-QUEUE/specs), reviewed by Claude.
Protocol: research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md
Stdlib only (csv, math, statistics, random, unittest). No pandas/numpy.
Modules: bt_data.py (raw CSV loaders), bt_engine.py (1m trade sim), bt_ladder.py (ladder fills), bt_stats.py (CIs, DSR, PBO).
Tests: test_bt_*.py, run with: python -m unittest discover -s MyTradingSys/backtest/bt -p "test_*.py"
