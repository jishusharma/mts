TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3.py: models A/B/C/D, session windows, day rules and evaluation helpers of the Fabio v3.1 spec; re-export the signals and exec modules.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:39-62
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:104-136
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:137-142
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:174-187
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:249-268
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:364-371
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3.py. Nothing else. No test file.
OUTPUT_TOKENS: 13000
EXPECT: from MyTradingSys.backtest.layers.fabio.fabio_v3_signals import
EXPECT: from MyTradingSys.backtest.layers.fabio.fabio_v3_exec import
EXPECT: def model_a_trade(
EXPECT: def model_b(
EXPECT: def model_c(
EXPECT: def model_d_trade(
EXPECT: def ny_open_utc(
EXPECT: def london_open_utc(
EXPECT: def first_leg_allowed(
EXPECT: def first_leg_risk(

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter. The spec is v3.1: lines marked v3.1 are required.

Start with explicit re-exports of EVERY public name of fabio_v3_signals and fabio_v3_exec (the names listed on the
"signals" and "exec" lines of the contract, including failed_auction, defended_level and opp_stop; write them out, no
star import). Then implement every name on the "v3" lines: model_a_trade, model_b (target_mode "edge" or "trail"),
model_c, model_d_trade (spec section 4; return dict keys exactly as the contract; every model passes mgmt, ctrl and
absorbed on to simulate_trade), ny_open_utc (America/New_York 09:30 cash open as an aware UTC datetime; None on weekends
and on every US_CLOSED date of spec section 2), london_open_utc (07:00 UTC in UK summer time, else 08:00 UTC; None on
weekends), entry_allowed, window_bars, aggregate_day_r (risk_u * net_r), first_leg_allowed and first_leg_risk (carry,
floor at 0, spec section 6), day_gate_open (g=None means gate off), day_type, sample_size
(ceil(((1.96+0.8416)*sd/delta)**2)), ci_halfwidth, following spec sections 2, 4, 6 and 8.
