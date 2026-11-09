"""Tests for forward_log.py. Expected numbers hand-computed (R units, FEES_DERIBIT: entry/target maker 0, stop taker 5 bps)."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("forward_log", HERE / "forward_log.py")
fl = importlib.util.module_from_spec(_spec)
sys.modules["forward_log"] = fl
_spec.loader.exec_module(fl)

PLAN = {"direction": "long", "entry": 100000.0, "structural_stop": 99000.0}  # risk 1000 = 1R
HALF = 101500.0   # 1.5R
TGT = 103000.0    # 3R


def bar(l, h, c=None):
    return {"o": l, "h": h, "l": l, "c": c if c is not None else h}


def test_fill_then_half_and_target():
    bars = [bar(99900, 100500), bar(100100, 101200), bar(100500, 101600), bar(101000, 103100)]
    r = fl.simulate_trade(PLAN, bars, half_price=HALF, target_price=TGT)
    assert r["filled"] and r["exit_reason"] == "target"
    assert abs(r["net_r"] - 2.25) < 1e-9   # 0.5*1.5 + 0.5*3.0, all maker legs = 0 fee


def test_no_fill_within_3_bars():
    bars = [bar(100100, 100500)] * 3 + [bar(99000, 100000)]  # touches only on bar 4: too late
    r = fl.simulate_trade(PLAN, bars, half_price=HALF, target_price=TGT)
    assert not r["filled"] and r["net_r"] == 0.0


def test_be_at_plus_1r_then_stopped_at_entry():
    bars = [bar(99900, 100500), bar(100100, 101200), bar(99950, 100800)]
    r = fl.simulate_trade(PLAN, bars, half_price=HALF, target_price=TGT)
    assert r["exit_reason"] == "be_stop"
    assert abs(r["net_r"] - (-0.05)) < 1e-9   # 0 R gross, taker stop leg 0.0005*100000/1000


def test_stop_before_target_same_bar_is_loss():
    bars = [bar(99900, 100500), bar(98900, 103500)]
    r = fl.simulate_trade(PLAN, bars, half_price=HALF, target_price=TGT)
    assert r["exit_reason"] == "stop" and r["net_r"] < -1.0


def test_build_event_row_real_plan_and_session():
    ctx = {"htf_bias": "bearish"}
    inter = {"verdict": "FAST_REJECTION", "level_side": "support", "level_price": 100000.0,
             "sweep_extreme": 99000.0, "delta": -12.5}
    bars = [bar(99900, 100500), bar(100100, 101200), bar(100500, 101600), bar(101000, 103600)]
    ts = 1762693200000  # 2025-11-09 13:00:00 UTC -> ny
    row = fl.build_event_row(ctx, inter, 100000.0, [("POC", 101500.0), ("edge", 103500.0)], bars,
                             ts_ms=ts, level_family="range_edge")
    assert row["gate_pass"] and row["setup_type"] == "failed_auction_reclaim"
    assert row["session"] == "ny" and row["with_htf"] is False and row["delta"] == -12.5
    assert abs(row["fee_r"] - 0.0476) < 1e-3   # 5 bps / 104.95 bps stop
    assert row["filled"] and row["exit_reason"] == "target"
    json.dumps(row)


def test_skip_row_has_no_trade():
    row = fl.build_event_row({}, {"verdict": "NO_TOUCH"}, 100000.0, [], [], ts_ms=0, level_family="x")
    assert row["gate_pass"] is False and row["filled"] is False and row["net_r"] == 0.0


def test_session_blocks():
    h = 3600000
    assert [fl.session_block(x * h) for x in (0, 7, 12, 21)] == ["asia", "london", "ny", "late"]


def test_append_jsonl(tmp_path):
    p = tmp_path / "e.jsonl"
    fl.append_row(p, {"a": 1})
    fl.append_row(p, {"a": 2})
    assert [json.loads(x)["a"] for x in p.read_text().splitlines()] == [1, 2]


def _rows(n, net):
    return [{"gate_pass": True, "filled": True, "setup_type": "failed_auction_reclaim", "net_r": net}] * n


def test_kill_rule():
    assert fl.kill_check(_rows(30, -0.1))["killed"] is True
    assert fl.kill_check(_rows(29, -0.1))["killed"] is False
    k = fl.kill_check(_rows(30, 0.1))
    assert k["killed"] is False and k["gate_pass_fades"] == 30 and abs(k["net_r"] - 3.0) < 1e-9
    other = _rows(40, -1.0)
    for r in other:
        r = r  # va continuation is not a fade
    assert fl.kill_check([dict(r, setup_type="va_acceptance_continuation") for r in other])["gate_pass_fades"] == 0


def test_range_ended_on_daily_close_outside():
    assert fl.range_ended([77000, 80900, 75400]) is False
    assert fl.range_ended([77000, 80901]) is True
    assert fl.range_ended([77000, 75399.9]) is True
