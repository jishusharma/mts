# Stale .new Files Triage

| File | Status | Notes |
|------|--------|-------|
| BUGS.md.new | SUPERSEDED | Identical to live BUGS.md |
| kill_switch.py.new | SUPERSEDED | Live file is larger (7594B vs 4298B), contains all new content |
| risk_guard.py.new | SUPERSEDED | Live file is newer (4481B vs 4337B) |
| test_kill_switch.py.new | SUPERSEDED | Live file is much larger (10108B vs 5260B), contains all new content |
| test_risk_guard.py.new | HAS-UNMERGED-CONTENT | Import path difference: .new uses `from MyTradingSys.execution.risk_guard import` vs live uses `from risk_guard import` |

## Proposed deletions (SUPERSEDED files only):
- MyTradingSys/research/BUGS.md.new
- MyTradingSys/research/fast_track_2026-09-27/qwen_raw_015_017/kill_switch.py.new
- MyTradingSys/research/fast_track_2026-09-27/qwen_raw_015_017/risk_guard.py.new
- MyTradingSys/research/fast_track_2026-09-27/qwen_raw_015_017/test_kill_switch.py.new
