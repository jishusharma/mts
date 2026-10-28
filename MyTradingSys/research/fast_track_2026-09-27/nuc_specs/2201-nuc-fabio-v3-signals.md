TASK: Write MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py: ATR, profile helpers and signals S1-S9 (incl. S5D) of the Fabio v3.1 spec.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:1-103
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:364-371
SCOPE: MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42
SCOPE: MyTradingSys/backtest/layers/fabio/orderflow_bars.py:10-42
SCOPE: MyTradingSys/backtest/layers/fabio/fabio_of_model.py:74-108
CREATE: MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py
OUTPUT: One FILE block, full content: MyTradingSys/backtest/layers/fabio/fabio_v3_signals.py. Nothing else. No test file.
OUTPUT_TOKENS: 12000
EXPECT: def atr(
EXPECT: def build_profile(
EXPECT: def value_area(
EXPECT: def lvn_levels(
EXPECT: def balance(
EXPECT: def pressure(
EXPECT: def effort_result(
EXPECT: def breakout(
EXPECT: def failed_auction(
EXPECT: def defended_level(
EXPECT: def exhaustion(
EXPECT: climax=False

Python 3.10, stdlib only (math, statistics, datetime, zoneinfo allowed), pure functions, no I/O except where the
spec says, no network. Never mutate inputs. Bars are plain dicts with the orderflow_bars.py columns. Names, argument
names, defaults and result keys MUST match the contract in the test docstring (MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py:1-42) exactly; where the spec and
the contract differ, the contract wins. Tests (not shown to you) import everything via fabio_v3. Never import from
MyTradingSys.execution, MyTradingSys.backtest.layers.alerts, Tom/core modules, or the FEE_* constants of
fabio_of_model.py. Fabio is a separate layer, never a Tom filter. The spec is v3.1: lines marked v3.1 are required.

Implement every name in the "signals" lines of the contract: atr, build_profile, value_area, lvn_levels, select_lvn,
balance, pressure, effort_result, volume_tier, the S4 big-trade function (contract name), breakout, control_level, curve, exhaustion, failed_auction,
defended_level, following spec sections 2 and 3 exactly. exhaustion has the v3.1 clause (b) (exit only on a new balance
favouring the other side: S2 == -s or more S3 absorbed bars of side s than of side -s in [i-59, i]) and clause (d)
(climax + failed auction, only when climax=True). failed_auction and defended_level take the absorbed list as an argument
(absorbed[j] = S3(j) absorbed side). Reuse the value-area / LVN algorithm of fabio_of_model.py:74-108 with the bin size as a
parameter (do not import that module). exhaustion and every S3 call inside it return False / count 0 (never raise) when
fewer bars than a look-back exist.
