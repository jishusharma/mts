"""Spec checks for the read-only per-analyst CBP recount."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cbp_scorecard


def test_missing_rows_key_is_empty():
    assert cbp_scorecard.recount({}) == {}


def test_empty_rows_is_empty():
    assert cbp_scorecard.recount({"rows": []}) == {}


def test_unknown_analyst_is_counted():
    assert cbp_scorecard.recount({"rows": [{}]}) == {
        "UNKNOWN": {"rows": 1, "trades": 0, "tradable_rows": 0}}


def test_michael_and_michaal_are_distinct():
    result = cbp_scorecard.recount({"rows": [{"analyst": "Michael"}, {"analyst": "Michaal"}]})
    assert result == {
        "Michael": {"rows": 1, "trades": 0, "tradable_rows": 0},
        "Michaal": {"rows": 1, "trades": 0, "tradable_rows": 0},
    }


def test_none_trades_contributes_zero():
    assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": None}]})["A"]["trades"] == 0


def test_empty_trades_contributes_zero():
    assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": []}]})["A"]["trades"] == 0


def test_trade_count_includes_each_trade_independent_of_tradability():
    data = {"rows": [{"analyst": "A", "trades": [{}, {"direction": "SIDEWAYS"}]}]}
    assert cbp_scorecard.recount(data)["A"] == {"rows": 1, "trades": 2, "tradable_rows": 0}


def test_complete_long_trade_is_tradable():
    trade = {"direction": "LONG", "entry": "1", "target": "2", "invalidation": "0"}
    assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": [trade]}]})["A"]["tradable_rows"] == 1


def test_complete_short_trade_is_tradable():
    trade = {"direction": "SHORT", "entry": "2", "target": "1", "invalidation": "3"}
    assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": [trade]}]})["A"]["tradable_rows"] == 1


def test_invalid_direction_is_not_tradable():
    trade = {"direction": "SIDEWAYS", "entry": "1", "target": "2", "invalidation": "0"}
    assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": [trade]}]})["A"]["tradable_rows"] == 0


def test_blank_or_em_dash_levels_are_not_tradable():
    for missing in ("", "   ", "—"):
        trade = {"direction": "LONG", "entry": "1", "target": "2", "invalidation": "0"}
        trade["target"] = missing
        assert cbp_scorecard.recount({"rows": [{"analyst": "A", "trades": [trade]}]})["A"]["tradable_rows"] == 0


def test_row_with_multiple_trades_counts_as_one_tradable_row():
    valid = {"direction": "LONG", "entry": "1", "target": "2", "invalidation": "0"}
    data = {"rows": [{"analyst": "A", "trades": [valid, valid]}]}
    assert cbp_scorecard.recount(data)["A"] == {"rows": 1, "trades": 2, "tradable_rows": 1}


def test_counts_accumulate_by_exact_analyst_key():
    data = {"rows": [{"analyst": "A", "trades": []}, {"analyst": "A", "trades": [{"direction": "LONG"}]}]}
    assert cbp_scorecard.recount(data)["A"] == {"rows": 2, "trades": 1, "tradable_rows": 0}
