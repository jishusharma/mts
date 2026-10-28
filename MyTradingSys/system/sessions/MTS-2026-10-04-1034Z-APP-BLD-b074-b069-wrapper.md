# MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper

Surface APP, role BLD. Tasks: B074 (Compute-Verdict override-first), B069 (wrapper log carries exit code + ums.log tail).
Files: scripts/core/start-trading-day.ps1, MyTradingSys/tests/test_b074_rule_order.py, items B074/B069, 03_FILE_INDEX.md.
Gate: run_all_tests --quick PASS; new tests fail pre-change. Open: B069 root cause not reproduced.
