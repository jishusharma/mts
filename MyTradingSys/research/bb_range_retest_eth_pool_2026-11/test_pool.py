"""Tests for bb_range_retest_eth_pool_2026-11 (PRE_REG.md). The first test reads the committed dev_cells.csv of this study and of the
shipped BTC spot study; the loader tests use a temp folder (no market data needed)."""
import csv
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location("bb_eth_pool", HERE / "study.py")
st = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(st)

SHIPPED = HERE.parent / "bb_range_retest_2026-11-04" / "dev_cells.csv"
FAMILY = [(s, k) for s in ("asia", "london", "ny") for k in ("0.25", "0.5", "1.0")]


def _family(path, symbol=None):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if symbol is not None and r.get("symbol") != symbol:
                continue
            if r["gate"] == "range" and r["tag"] == "tagged" and r["side"] == "both" and (r["session"], r["k"]) in FAMILY:
                out[(r["session"], r["k"])] = r
    return out


def test_btc_row_reproduces_shipped_n():
    """BTC-only futures run vs the shipped spot run: every family cell n within REPRO_N_TOL (PRE_REG) and the same net sign."""
    old = _family(SHIPPED)
    new = _family(HERE / "dev_cells.csv", symbol="BTCUSDT")
    assert len(old) == 9 and len(new) == 9
    for key in FAMILY:
        n0, n1 = int(old[key]["n"]), int(new[key]["n"])
        assert abs(n1 - n0) <= st.REPRO_N_TOL * n0, (key, n0, n1)
        assert (float(old[key]["net"]) > 0) == (float(new[key]["net"]) > 0), key


def _write(p, rows):
    p.write_text("open_time,open,high,low,close,volume\n" + "".join("%d,1,2,0.5,1.5,10\n" % t for t in rows), encoding="utf-8")


def test_loader_refuses_end_after_dev(tmp_path):
    with pytest.raises(ValueError):
        st.load_sym_1m("ETHUSDT", st.DEV_END_MS + 60000, root=tmp_path)


def test_loader_reads_one_symbol_and_drops_bars_at_or_after_end(tmp_path):
    _write(tmp_path / "ETHUSDT-1m-2024-06.csv", [st.DEV_END_MS - 120000, st.DEV_END_MS - 60000])
    _write(tmp_path / "ETHUSDT-1m-2024-07.csv", [st.DEV_END_MS, st.DEV_END_MS + 60000])
    _write(tmp_path / "BTCUSDT-1m-2024-06.csv", [st.DEV_END_MS - 180000])
    bars = st.load_sym_1m("ETHUSDT", st.DEV_END_MS, root=tmp_path)
    assert [b["t"] for b in bars] == [st.DEV_END_MS - 120000, st.DEV_END_MS - 60000]
    assert bars[0]["c"] == 1.5


def test_cluster_key_separates_symbols_on_one_day():
    assert st.cluster_key("BTCUSDT", 19000) != st.cluster_key("ETHUSDT", 19000)
    assert st.cluster_key("BTCUSDT", 19000) == st.cluster_key("BTCUSDT", 19000)
