TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py: ATR, profile helpers and signals S1-S8 of the Fabio v3 spec.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:1-87
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32
SCOPE: MyTradingSys/backtest/layers/fabio/orderflow_bars.py:10-42
SCOPE: MyTradingSys/backtest/layers/fabio/fabio_of_model.py:74-108
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py. Nothing else. No test file.
OUTPUT_TOKENS: 9000
EXPECT: def atr(
EXPECT: def build_profile(
EXPECT: def value_area(
EXPECT: def lvn_levels(
EXPECT: def balance(
EXPECT: def pressure(
EXPECT: def effort_result(
EXPECT: def exhaustion(

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-32) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter.

Implement every name in the "signals" line of the contract: atr, build_profile, value_area, lvn_levels, select_lvn,
balance, pressure, effort_result, volume_tier, big_push, breakout, control_level, curve, exhaustion, following spec
sections 2 and 3 exactly. Reuse the value-area / LVN algorithm of fabio_of_model.py:74-108 with the bin size as a
parameter (do not import that module). exhaustion and the S3 call inside it return False (never raise) when fewer
bars than the lookback exist.
