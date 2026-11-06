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
