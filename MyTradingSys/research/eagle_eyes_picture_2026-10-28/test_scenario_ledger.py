import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("scenario_ledger", Path(__file__).with_name("scenario_ledger.py"))
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)


def test_first_touch_order():
    bars = [(1, 100.5, 99.5), (2, 101.2, 100.0), (3, 100.0, 98.0)]
    assert sl.first_touch(bars, 101.0, 98.5) == ("UP", 2)
    assert sl.first_touch(bars, 102.0, 98.5) == ("DOWN", 3)
    assert sl.first_touch(bars, 103.0, 90.0) == ("NEITHER", None)
    assert sl.first_touch([(1, 105.0, 95.0)], 101.0, 99.0) == ("BOTH", 1)


def test_score_and_summary():
    assert sl.score_of("UP", "UP") == "HIT"
    assert sl.score_of("UP", "DOWN") == "MISS"
    assert sl.score_of("NONE", "UP") == "NA"
    assert sl.score_of("DOWN", "BOTH") == "NA"
    rows = [{"score": "HIT", "outcome": "UP"}] * 3 + [{"score": "MISS", "outcome": "DOWN"}, {"score": "", "outcome": ""}]
    s = sl.summary(rows)
    assert "HIT 3 MISS 1" in s and "open 1" in s and "keep logging (4/20" in s


def test_add_stores_registry_rates_ids_and_old_rows_untouched(tmp_path, monkeypatch):
    f = tmp_path / "ledger.csv"
    f.write_text("id,given_utc,end_utc,likely,up,down,text,outcome,touched_utc,score\n"
                 "S001,2026-11-04T09:00Z,2026-11-05T09:00Z,DOWN,78850.0,77615.0,old,,,\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(sl, "LEDGER", f)
    sl.main(["add", "--given", "2026-11-07T00:00Z", "--end", "2026-11-08T00:00Z", "--likely", "UP", "--up", "2", "--down", "1",
             "--text", "new", "--rates", "us_open_levels, bigcandle_story"])
    sl.main(["add", "--given", "2026-11-07T00:00Z", "--end", "2026-11-08T00:00Z", "--likely", "UP", "--up", "2", "--down", "1", "--text", "none"])
    rows = sl.load(f)
    assert rows[0]["text"] == "old" and rows[0]["rates"] == "" and rows[0]["up"] == "78850.0"
    assert rows[1]["rates"] == "us_open_levels,bigcandle_story" and rows[2]["rates"] == ""


def test_monday_open_scenarios_logged_with_score_date():
    """monday-open-playbook-1109: the three Monday 2026-11-09 scenarios are in the real ledger, scored by first touch of two levels."""
    rows = {r["id"]: r for r in sl.load(sl.LEDGER)}
    assert {"S001", "S008"} <= set(rows), "old rows must stay"
    mon = [r for r in rows.values() if r["text"].startswith("Monday open 11-09")]
    assert len(mon) == 3
    by = {r["text"].split(":")[0].split("scenario ")[1]: r for r in mon}
    assert set(by) == {"B straight drop", "A small bounce then drop", "C bigger bounce"}
    for r in mon:
        assert r["end_utc"] == "2026-11-10T00:00Z" and r["given_utc"] < r["end_utc"]  # score date
        assert float(r["down"]) == 74888.0 < float(r["up"])
    assert float(by["B straight drop"]["up"]) < float(by["A small bounce then drop"]["up"]) < float(by["C bigger bounce"]["up"])
    assert by["B straight drop"]["likely"] == "DOWN"  # the one the clocks lean to; the nested rows stay NONE (no double count)
    assert by["A small bounce then drop"]["likely"] == by["C bigger bounce"]["likely"] == "NONE"


def test_monday_playbook_names_every_ledger_row():
    text = (Path(__file__).resolve().parents[1] / "monday_open_2026-11-09" / "PLAYBOOK.md").read_text(encoding="utf-8")
    ids = [r["id"] for r in sl.load(sl.LEDGER) if r["text"].startswith("Monday open 11-09")]
    assert len(ids) == 3 and all(i in text for i in ids)


def test_monday_clocks_percentile_and_session():
    spec = importlib.util.spec_from_file_location("monday_clocks", Path(__file__).resolve().parents[1] / "monday_open_2026-11-09" / "monday_clocks.py")
    mc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mc)
    assert mc.pct([4, 1, 3, 2], 0.5) == 2.5 and mc.pct([1, 2, 3], 0.0) == 1 and mc.pct([1, 2, 3], 1.0) == 3
    assert mc.pct([0.0, 10.0], 0.25) == 2.5


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
