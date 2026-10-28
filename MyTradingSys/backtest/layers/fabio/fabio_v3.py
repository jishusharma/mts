"""Fabio v3 core (re-export of the v3 package).

See v3/README.md for module overview and v3/tests/ for implementation tests.
See pending_test_fabio_v3.py for spec-derived acceptance tests.
"""
from MyTradingSys.backtest.layers.fabio.v3 import *  # noqa: F401, F403

# For direct module imports
from MyTradingSys.backtest.layers.fabio import v3 as _v3_pkg  # noqa: F401
