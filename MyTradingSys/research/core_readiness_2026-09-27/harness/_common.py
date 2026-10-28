import sys
sys.dont_write_bytecode = True
"""Shared path setup for the core_readiness harness. Repo root is 4 levels up."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for sub in ("backtest", "runtime"):
    p = str(ROOT / "MyTradingSys" / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
