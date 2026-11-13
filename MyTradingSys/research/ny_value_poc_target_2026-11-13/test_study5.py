"""Core-rule tests for study5.py (POC distance gate, stop types, stop-first, net R)."""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study5 as s5  # noqa: E402


def test_poc_distance_gate_36bp():
    assert s5.tgt_ok(1, 100.0, 100.40)          # 40 bp above, long: ok
    assert not s5.tgt_ok(1, 100.0, 100.30)      # 30 bp: skipped
    assert not s5.tgt_ok(1, 100.0, 99.0)        # POC on the wrong side: skipped
    assert s5.tgt_ok(-1, 100.0, 99.50)          # short, 50 bp below
    assert not s5.tgt_ok(-1, 100.0, 100.5)


def test_stop_types():
    ev = dict(H=np.array([101.0, 103.0, 102.0]), L=np.array([99.0, 98.0, 99.5]), vah=102.0, val=98.5)
    assert abs(s5.stop_for("A", -1, ev, 2) - 103.0 * 1.0001) < 1e-9
    assert abs(s5.stop_for("A", 1, ev, 2) - 98.0 * 0.9999) < 1e-9
    assert abs(s5.stop_for("B", -1, ev, 2) - 102.0 * 1.001) < 1e-9
    assert abs(s5.stop_for("B", 1, ev, 2) - 98.5 * 0.999) < 1e-9


def test_net_r_and_stop_first():
    g, n = s5.gross_net(1, 100.0, 101.0, 99.0)
    assert abs(g - 1.0) < 1e-9 and abs(n - (1.0 - s5.ps.COST_RT / 0.01)) < 1e-9
    H = np.array([100.0, 101.5, 100.0]); L = np.array([100.0, 98.5, 100.0]); C = np.array([100.0, 100.0, 100.0])
    ex, kind, reach, _ = s5.ps.sim_trade(1, 0, 101.0, 99.0, H, L, C)   # bar 1 touches both: stop first
    assert kind == "stop" and ex == 99.0 and reach is True
