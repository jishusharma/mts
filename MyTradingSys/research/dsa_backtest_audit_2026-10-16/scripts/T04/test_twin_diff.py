"""T04 gate: the committed twin-vs-shipped diff tables account for every shipped ledger row, and every difference carries one class.
Pure csv/stdlib (CI has no pandas, no F:/MTS/data). The diff tables are produced by t04_diff.py.
Run: python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T04/test_twin_diff.py
"""
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
CLASSES = {"spec_ambiguity", "shipped_bug", "twin_bug"}
STATUS = {"matched", "return_differs", "twin_only", "shipped_only"}
CASES = {
    "mal_bb_A1": ("diff_mal_bb_A1.csv", "mal_bb_mid_engulf_2026-10-16/ledger.csv"),
    "wlow_pooled": ("diff_wlow_pooled.csv", "opr_weekly_low_round_sweep_2026-10-16/ledger.csv"),
}


def _rows(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _check(diff_name, ledger_rel):
    d = _rows(HERE / "out" / diff_name)
    n_ledger = len(_rows(R / ledger_rel))
    c = {s: 0 for s in STATUS}
    for r in d:
        assert r["status"] in STATUS, r
        c[r["status"]] += 1
        if r["status"] == "matched":
            assert r["diff_class"] == "", r
        else:
            assert r["diff_class"] in CLASSES | {"residual"}, r
    # every shipped ledger row is matched, return-different or listed as shipped-only
    assert c["matched"] + c["return_differs"] + c["shipped_only"] == n_ledger
    # the table is exactly (shipped rows) + (twin-only rows)
    assert len(d) == n_ledger + c["twin_only"]
    assert len({r["key_ts_ms"] for r in d}) == len(d)
    return c


def test_every_shipped_event_is_matched_or_listed():
    for diff_name, ledger_rel in CASES.values():
        _check(diff_name, ledger_rel)


def test_every_difference_has_one_class():
    for diff_name, _ in CASES.values():
        for r in _rows(HERE / "out" / diff_name):
            if r["status"] != "matched":
                assert r["diff_class"] in CLASSES, "unclassified difference: %r" % (r,)


def test_rl_arm_table_is_classified():
    for r in _rows(HERE / "out" / "diff_wlow_RL.csv"):
        if r["status"] != "matched":
            assert r["diff_class"] in CLASSES, r
