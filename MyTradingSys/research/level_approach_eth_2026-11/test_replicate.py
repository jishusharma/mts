"""Tests for the C15 ETH / pooled replication (PRE_REG.md agreement rule, DEV-only loader)."""
import importlib.util
from pathlib import Path

import pytest

_sp = importlib.util.spec_from_file_location("level_eth_study", Path(__file__).resolve().parent / "study.py")
st = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(st)

BASE = {"BTCUSDT": 0.30, "ETHUSDT": 0.30}


def cells(btc, eth, n=50):
    return {("BTCUSDT", "A"): (n, btc), ("BTCUSDT", "B"): (n, btc), ("ETHUSDT", "A"): (n, eth), ("ETHUSDT", "B"): (n, eth)}


def test_agreement_rule():
    # BTC above its base rate in both halves, ETH below in both: symbols disagree in sign, never AGREES
    assert st.agreement(cells(0.40, 0.20), BASE, (0.33, 0.37), 0.30) == "DISAGREES"


def test_agreement_rule_all_same_sign_and_pooled_off_base():
    assert st.agreement(cells(0.20, 0.22), BASE, (0.15, 0.27), 0.30) == "AGREES"


def test_agreement_rule_pooled_ci_covers_base():
    assert st.agreement(cells(0.28, 0.29), BASE, (0.24, 0.33), 0.30) == "DISAGREES"


def test_agreement_rule_one_thin_cell_is_underpowered():
    c = cells(0.20, 0.22)
    c[("ETHUSDT", "B")] = (29, 0.22)
    assert st.agreement(c, BASE, (0.15, 0.27), 0.30) == "UNDERPOWERED"


def test_loader_refuses_end_after_dev(tmp_path):
    with pytest.raises(ValueError):
        st.load_symbol("ETHUSDT", root=tmp_path, end_ms=st.CUTOFF_MS + 60_000)
