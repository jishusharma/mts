TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py: fills, management (breakeven, adds, trail) and costs in R of the Fabio v3 spec.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:13-50
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:121-153
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py. Nothing else. No test file.
OUTPUT_TOKENS: 8000
EXPECT: FEE_TAKER = 0.0005
EXPECT: FEE_MAKER = 0.0
EXPECT: def find_fill(
EXPECT: def leg_r(
EXPECT: def simulate_trade(

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter.

Implement every name in the "exec" line of the contract: FEE_MAKER = 0.0, FEE_TAKER = 0.0005, TICK = 0.1, find_fill,
leg_r, be_update, trail_update, add_size, add_allowed, simulate_trade, following spec section 5 exactly (fills 5.1,
management 5.2, costs 5.3). simulate_trade may import control_level and exhaustion from
MyTradingSys.backtest.layers.fabio.fabio_v3_signals (a sibling module written by another task; assume the contract
signatures).
