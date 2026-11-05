"""ETH 1m files live in klines_eth (moved 2026-11-05); BTC stays in klines."""
import importlib.util
from pathlib import Path

_sp = importlib.util.spec_from_file_location("level_eth_root_study", Path(__file__).resolve().parent / "study.py")
st = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(st)


def test_default_roots_per_symbol():
    assert st.root_for("ETHUSDT").name == "klines_eth"
    assert st.root_for("BTCUSDT").name == "klines"
