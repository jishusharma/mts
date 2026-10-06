"""T037: regime_classifier.py. Votes: vwap_slope, cvd_slope, net_delta_1h sign (+1 up/down each), vp_shape P=up D=down;
>=3 up = TREND_UP, >=3 down = TREND_DOWN else RANGE. Publication needs 3 consecutive candidate cycles. The MEDIUM/HIGH
streak thresholds are NO-SOURCE (spec gives none) and are not pinned; test_regime_classifier.py holds the sourced votes."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import regime_classifier as rc  # noqa: E402


def _snap(vs="flat", cs="flat", vp="B", nd=0.0):
    return {"conditions": {"vwap_slope": vs, "cvd_slope": cs, "vp_shape": vp}, "trade_flow": {"net_delta_1h": nd}}


def test_four_up_votes_is_trend_up():
    assert rc.classify(_snap("rising", "rising", "P", 5.0)) == ("TREND_UP", 4, 0)


def test_exactly_three_up_votes_is_trend_up():
    assert rc.classify(_snap("rising", "rising", "B", 5.0)) == ("TREND_UP", 3, 0)


def test_three_down_votes_is_trend_down():
    assert rc.classify(_snap("falling", "falling", "B", -5.0)) == ("TREND_DOWN", 0, 3)


def test_two_votes_is_range():
    assert rc.classify(_snap("rising", "rising", "B", 0.0)) == ("RANGE", 2, 0)


def test_conflicting_votes_is_range():
    assert rc.classify(_snap("rising", "falling", "B", 0.0)) == ("RANGE", 1, 1)


def test_empty_snapshot_defaults_to_range_and_none_trade_flow_ok():
    assert rc.classify({}) == ("RANGE", 0, 0)
    assert rc.classify({"conditions": None, "trade_flow": None}) == ("RANGE", 0, 0)


def test_confidence_is_low_when_label_unknown_or_candidate_conflicts():
    # TREND_REGIME_DETECTOR_SPEC.md L42: a conflicting cycle downgrades confidence; initial label UNKNOWN is LOW
    assert rc.confidence_of("UNKNOWN", "TREND_UP", 9) == "LOW"
    assert rc.confidence_of("RANGE", "TREND_UP", 9) == "LOW"


def _setup(tmp_path, monkeypatch, snap):
    snaps = tmp_path / "snaps"
    snaps.mkdir()
    (snaps / "BTCUSDT_1.json").write_text(json.dumps(snap), encoding="utf-8")
    state = tmp_path / "state_code_regime.json"
    monkeypatch.setattr(rc, "SNAP_DIR", snaps)
    monkeypatch.setattr(rc, "STATE_CODE", state)
    return state


def test_main_without_snapshot_returns_1(tmp_path, monkeypatch, capsys):
    (tmp_path / "snaps").mkdir()
    monkeypatch.setattr(rc, "SNAP_DIR", tmp_path / "snaps")
    monkeypatch.setattr(rc, "STATE_CODE", tmp_path / "s.json")
    assert rc.main() == 1
    assert "no snapshot" in capsys.readouterr().out
    assert not (tmp_path / "s.json").exists()


def test_first_cycle_stays_unknown_low(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch, _snap("rising", "rising", "P", 5.0))
    assert rc.main() == 0
    s = json.loads(state.read_text(encoding="utf-8"))
    assert (s["label"], s["confidence"], s["candidate"], s["cycles_in_candidate_state"]) == ("UNKNOWN", "LOW", "TREND_UP", 1)
    assert (s["votes_up"], s["votes_down"], s["consecutive_cycles"]) == (4, 0, 1)
    assert not state.with_suffix(".json.new").exists()


def test_third_consecutive_cycle_publishes_the_label(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch, _snap("rising", "rising", "P", 5.0))
    # BOM on purpose: the loader reads utf-8-sig
    state.write_bytes(b"\xef\xbb\xbf" + json.dumps({"label": "UNKNOWN", "candidate": "TREND_UP",
                                                      "cycles_in_candidate_state": 2, "consecutive_cycles": 0}).encode())
    rc.main()
    s = json.loads(state.read_text(encoding="utf-8"))
    assert (s["label"], s["cycles_in_candidate_state"], s["consecutive_cycles"]) == ("TREND_UP", 3, 1)
    assert s["entered_at_utc"]


def test_second_cycle_does_not_publish(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch, _snap("rising", "rising", "P", 5.0))
    state.write_text(json.dumps({"label": "UNKNOWN", "candidate": "TREND_UP", "cycles_in_candidate_state": 1,
                                 "consecutive_cycles": 1}), encoding="utf-8")
    rc.main()
    s = json.loads(state.read_text(encoding="utf-8"))
    assert (s["label"], s["cycles_in_candidate_state"]) == ("UNKNOWN", 2)


def test_candidate_change_resets_streak_and_drops_confidence(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch, _snap("flat", "flat", "B", 0.0))   # candidate RANGE
    state.write_text(json.dumps({"label": "TREND_UP", "candidate": "TREND_UP", "cycles_in_candidate_state": 9,
                                 "consecutive_cycles": 9, "entered_at_utc": "2026-10-04T00:00:00.000000Z"}), encoding="utf-8")
    rc.main()
    s = json.loads(state.read_text(encoding="utf-8"))
    assert (s["label"], s["candidate"], s["cycles_in_candidate_state"], s["confidence"]) == ("TREND_UP", "RANGE", 1, "LOW")
    assert s["entered_at_utc"] == "2026-10-04T00:00:00.000000Z"
