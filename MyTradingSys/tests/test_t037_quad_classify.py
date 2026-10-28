"""T037: quad_classify.py wiring (None returns, snapshot discovery, one-line output). The class table is covered by
test_quad_classify.py (sourced); the dead-band thresholds and delta_aligned rule are NO-SOURCE and deliberately not pinned."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import quad_classify as qc  # noqa: E402


def _snap(price, cvd_d1h=0.0, oi=0.0, nd15=0.0):
    return {"current_price": price, "cvd": {"cvd_recent": {"delta_1h": cvd_d1h}},
            "open_interest": {"change_1h_pct": oi}, "trade_flow": {"net_delta_15m": nd15}}


def test_no_past_snapshot_gives_none():
    assert qc.classify(_snap(100.0), None) is None


def test_missing_price_gives_none():
    assert qc.classify({"cvd": {}}, _snap(100.0)) is None


def test_parse_ts_handles_z_suffix():
    assert qc.parse_ts("2026-10-04T10:00:00Z") == datetime(2026, 10, 4, 10, 0, tzinfo=timezone.utc)


def test_nearest_1h_ago_picks_closest_to_sixty_minutes_and_skips_latest():
    t0 = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
    snaps = [(t0 - timedelta(minutes=70), {"id": "70"}), (t0 - timedelta(minutes=55), {"id": "55"}), (t0, {"id": "now"})]
    assert qc.nearest_1h_ago(snaps)["id"] == "55"   # |55-60| = 5 < |70-60| = 10
    assert qc.nearest_1h_ago([(t0, {"id": "now"})]) is None
    assert qc.nearest_1h_ago([]) is None


def _write(dirpath, name, ts, snap):
    snap = dict(snap, timestamp_utc=ts)
    (dirpath / name).write_text(json.dumps(snap), encoding="utf-8")


def test_main_prints_one_line(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(qc, "SNAPS", tmp_path)
    _write(tmp_path, "BTCUSDT_a.json", "2026-10-04T11:00:00Z", _snap(100.0))
    _write(tmp_path, "BTCUSDT_b.json", "2026-10-04T12:00:00Z", _snap(101.0, 50.0, 0.5, 10.0))
    (tmp_path / "BTCUSDT_bad.json").write_text("{not json", encoding="utf-8")   # skipped
    qc.main()
    assert capsys.readouterr().out.strip() == "QUAD: new_longs (1h price +1.00% | cvd +50 | oi +0.500% | nd15 +10.0)"


def test_main_insufficient_data(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(qc, "SNAPS", tmp_path)
    _write(tmp_path, "BTCUSDT_a.json", "2026-10-04T11:00:00Z", _snap(100.0))
    qc.main()
    assert capsys.readouterr().out.strip() == "QUAD: insufficient_data"
