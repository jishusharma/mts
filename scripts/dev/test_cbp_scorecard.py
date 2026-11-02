"""Spec-derived tests for scripts/dev/cbp_scorecard.py.

Covers:
  - recount:
    * empty data or empty rows returns empty dict
    * missing analyst key defaults to UNKNOWN
    * strict distinct analyst name keys: Michael and Michaal are never merged
    * trades count accumulation across rows (including None/empty lists)
    * tradable rows incrementation based on cbp.is_tradable contract
    * multiple analysts and multi-row accumulation
  - main:
    * command-line execution with --store temp file
    * alphabetical sorting and line formatting
    * total rows and rejected summary line
    * graceful handling of missing store file
"""
import json
from pathlib import Path
import pytest

import cbp_scorecard as cs


def test_recount_empty_data_and_empty_rows():
    assert cs.recount({}) == {}
    assert cs.recount({"rows": []}) == {}


def test_recount_missing_analyst_defaults_to_unknown():
    data = {
        "rows": [
            {"trades": []}
        ]
    }
    res = cs.recount(data)
    assert "UNKNOWN" in res
    assert res["UNKNOWN"] == {"rows": 1, "trades": 0, "tradable_rows": 0}


def test_recount_preserves_distinct_michael_and_michaal():
    # Docstring rule: Michael (@MichaelPizzino) and Michaal (@michaelvdpoppe) must never be merged
    data = {
        "rows": [
            {"analyst": "Michael", "trades": [{"direction": "LONG", "entry": "68000", "target": "72000", "invalidation": "66000"}]},
            {"analyst": "Michaal", "trades": [{"direction": "SHORT", "entry": "69000", "target": "65000", "invalidation": "71000"}]},
        ]
    }
    res = cs.recount(data)
    assert set(res.keys()) == {"Michael", "Michaal"}
    assert res["Michael"]["rows"] == 1
    assert res["Michaal"]["rows"] == 1


def test_recount_trades_and_tradable_rows_accumulation():
    data = {
        "rows": [
            # Row 1: 2 trades, tradable
            {
                "analyst": "Krown",
                "trades": [
                    {"direction": "LONG", "entry": "60000", "target": "65000", "invalidation": "58000"},
                    {"direction": "SHORT", "entry": "70000", "target": "62000", "invalidation": "72000"},
                ],
            },
            # Row 2: 1 trade, not tradable (invalidation is placeholder '—')
            {
                "analyst": "Krown",
                "trades": [
                    {"direction": "LONG", "entry": "61000", "target": "66000", "invalidation": "—"},
                ],
            },
            # Row 3: 0 trades (None)
            {
                "analyst": "Krown",
                "trades": None,
            },
        ]
    }
    res = cs.recount(data)
    # Total rows = 3, trades = 2 + 1 + 0 = 3, tradable_rows = 1 (only row 1)
    assert res["Krown"] == {"rows": 3, "trades": 3, "tradable_rows": 1}


def test_recount_multi_analyst_independent_aggregation():
    data = {
        "rows": [
            {"analyst": "Cowen", "trades": []},
            {"analyst": "Cowen", "trades": [{"direction": "LONG", "entry": "50000", "target": "60000", "invalidation": "45000"}]},
            {"analyst": "Cred", "trades": [{"direction": "SHORT", "entry": "68000", "target": "64000", "invalidation": "70000"}]},
        ]
    }
    res = cs.recount(data)
    assert res["Cowen"] == {"rows": 2, "trades": 1, "tradable_rows": 1}
    assert res["Cred"] == {"rows": 1, "trades": 1, "tradable_rows": 1}


def test_main_cli_with_store_file(tmp_path, capsys):
    store_file = tmp_path / "rows.json"
    content = {
        "schema": 1,
        "rows": [
            {"analyst": "Michael", "trades": [{"direction": "LONG", "entry": "60000", "target": "65000", "invalidation": "58000"}]},
            {"analyst": "Michaal", "trades": []},
        ],
        "rejected": [
            {"analyst": "Unknown", "reason": "malformed"}
        ],
    }
    store_file.write_text(json.dumps(content), encoding="utf-8")

    code = cs.main(["--store", str(store_file)])
    assert code == 0

    out = capsys.readouterr().out
    lines = [line.strip() for line in out.strip().splitlines()]
    # Sorted order: Michaal before Michael
    assert lines[0] == "Michaal: rows 1, trades 0, tradable rows 0"
    assert lines[1] == "Michael: rows 1, trades 1, tradable rows 1"
    assert lines[2] == "total rows 2, rejected 1"


def test_main_cli_missing_store_file(tmp_path, capsys):
    missing_store = tmp_path / "nonexistent.json"
    code = cs.main(["--store", str(missing_store)])
    assert code == 0

    out = capsys.readouterr().out
    assert "total rows 0, rejected 0" in out


def test_recount_handles_row_with_empty_trades_list():
    data = {
        "rows": [
            {"analyst": "Jason", "trades": []}
        ]
    }
    res = cs.recount(data)
    assert res["Jason"] == {"rows": 1, "trades": 0, "tradable_rows": 0}
