"""Tests for divergence_event.py: the appender must never write a half row or a duplicate."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import divergence_event as d


def _row(**kw):
    base = {"utc": "2026-10-26T14:36:00Z", "btc_since_open": "-0.10", "es_since_open": "0.32",
            "nq_since_open": "0.36", "out_30m": "a", "out_60m": "b", "out_120m": "c"}
    base.update(kw)
    return base


def test_append_writes_header_once_and_the_row(tmp_path):
    f = str(tmp_path / "e.csv")
    d.append(_row(), f)
    d.append(_row(utc="2026-10-27T10:00:00Z"), f)
    with open(f, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    assert lines[0] == ",".join(d.COLS)
    assert len(lines) == 3


def test_duplicate_utc_is_refused(tmp_path):
    f = str(tmp_path / "e.csv")
    d.append(_row(), f)
    try:
        d.append(_row(), f)
    except ValueError as e:
        assert "duplicate" in str(e)
    else:
        raise AssertionError("duplicate utc was accepted")
    assert len(d.rows(f)) == 1


def test_missing_outcome_is_refused(tmp_path):
    f = str(tmp_path / "e.csv")
    for col in ("out_30m", "out_60m", "out_120m", "utc"):
        try:
            d.append(_row(**{col: ""}), f)
        except ValueError as e:
            assert col in str(e), (col, str(e))
        else:
            raise AssertionError("%s empty was accepted" % col)
    assert not os.path.exists(f)


def test_shipped_csv_has_the_event_and_all_outcomes():
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "divergence_events.csv")
    rs = d.rows(f)
    assert len(rs) == 1, rs
    r = rs[0]
    assert r["utc"] == "2026-10-26T14:36:00Z"
    assert r["btc_since_open"] == "-0.10" and r["es_since_open"] == "0.32" and r["nq_since_open"] == "0.36"
    for col in ("out_30m", "out_60m", "out_120m"):
        assert "gap" in r[col] and "Z" in r[col], (col, r[col])
