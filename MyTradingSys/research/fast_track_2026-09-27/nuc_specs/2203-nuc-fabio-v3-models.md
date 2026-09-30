TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3.py: models A/B/C, session window, day rules and evaluation helpers of the Fabio v3 spec; re-export the signals and exec modules.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:88-120
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:154-227
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3.py. Nothing else. No test file.
OUTPUT_TOKENS: 9000
EXPECT: from MyTradingSys.backtest.layers.fabio.fabio_v3_signals import
EXPECT: from MyTradingSys.backtest.layers.fabio.fabio_v3_exec import
EXPECT: def model_a_trade(
EXPECT: def model_b(
EXPECT: def model_c(
EXPECT: def ny_open_utc(

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter.

Start with explicit re-exports of EVERY public name of fabio_v3_signals and fabio_v3_exec (the names listed on the
"signals" and "exec" lines of the contract; write them out, no star import). Then implement every name on the "v3"
line: model_a_trade, model_b, model_c (spec section 4; return dict keys exactly as the contract), ny_open_utc
(America/New_York 09:30 cash open as an aware UTC datetime, None on weekends), entry_allowed, window_bars,
aggregate_day_r, first_leg_allowed, day_gate_open (g=None means gate off), day_type, sample_size
(ceil(((1.96+0.8416)*sd/delta)**2)), ci_halfwidth, following spec sections 4, 6 and 8.
