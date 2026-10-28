"""B070: the Java taker-fee constant must equal backtest/fees.py (the single source), and mts_math uses the same number."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "runtime"))

import fees  # noqa: E402


def _java_taker():
    src = (ROOT / "src" / "main" / "java" / "datafeed" / "ExecutionMathConstants.java").read_text(encoding="utf-8")
    return float(re.search(r"TAKER_FEE_PER_SIDE\s*=\s*([0-9.]+)\s*;", src).group(1))


def test_java_taker_equals_fees_py():
    assert _java_taker() == fees.DERIBIT_TAKER == fees.BINANCE_TAKER


def test_python_default_taker_is_fees_py():
    import mts_math
    assert mts_math.DERIBIT_TAKER == fees.DERIBIT_TAKER


def test_java_fdax_equals_fees_py():
    src = (ROOT / "src" / "main" / "java" / "datafeed" / "ExecutionMathConstants.java").read_text(encoding="utf-8")
    java = float(re.search(r"FDAX_FEE_PER_SIDE\s*=\s*([0-9.]+)\s*;", src).group(1))
    assert java == fees.FDAX_FEE_PER_SIDE
    assert fees.FEES_FDAX["entry"] == fees.FEES_FDAX["stop"] == fees.FDAX_FEE_PER_SIDE


def test_java_symbol_map_is_ger40_fdax_else_btc():
    src = (ROOT / "src" / "main" / "java" / "datafeed" / "ExecutionMathConstants.java").read_text(encoding="utf-8")
    assert re.search(r'"GER40"\.equals\(symbol\)\s*\?\s*FDAX_FEE_PER_SIDE\s*:\s*TAKER_FEE_PER_SIDE', src)
