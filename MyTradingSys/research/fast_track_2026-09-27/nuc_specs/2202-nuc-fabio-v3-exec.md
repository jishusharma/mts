TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py: fills, management (dist and event modes, adds) and costs in R of the Fabio v3.1 spec.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:24-103
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:137-173
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:364-371
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3_exec.py. Nothing else. No test file.
OUTPUT_TOKENS: 11000
EXPECT: FEE_TAKER = 0.0005
EXPECT: FEE_MAKER = 0.0
EXPECT: def find_fill(
EXPECT: def leg_r(
EXPECT: def add_size(
EXPECT: def add_allowed(
EXPECT: def opp_stop(
EXPECT: def simulate_trade(
EXPECT: mgmt="dist"

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter. The spec is v3.1: lines marked v3.1 are required.

Implement every name in the "exec" lines of the contract: FEE_MAKER = 0.0, FEE_TAKER = 0.0005, TICK = 0.1, find_fill,
leg_r, be_update, trail_update, add_size (budget), add_allowed (add_mode, s7, max 2 adds), opp_stop, simulate_trade,
following spec section 5 exactly (fills 5.1, management 5.2 with mgmt "dist" and "event", costs 5.3). simulate_trade
records every stop change in "moves" as (i, new_stop, kind) and returns exit_idx; in event mode it uses the injected
ctrl and absorbed lists (None -> compute them with effort_result), applies E_opp via opp_stop, E_own as a de-risk that
never exits, the defended-level trail, and calls exhaustion with climax=True (s8_kw is forwarded to exhaustion).
simulate_trade may import control_level, effort_result, the S4 big-trade function, curve and exhaustion from
MyTradingSys.backtest.layers.fabio.fabio_v3_signals (a sibling module written by another task; assume the contract
signatures).
