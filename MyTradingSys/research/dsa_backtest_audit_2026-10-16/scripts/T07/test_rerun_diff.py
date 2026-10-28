"""T07 gate: the rerun diff covers every published number of the ten results, one study is deterministic, and every
STALE-CANDIDATE names its provenance commit. Stdlib only (CI has no pandas, no F:/MTS/data); the tables in out/ are produced by
t07_provenance.py, t07_rerun.py and t07_diff.py.
Run: python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/test_rerun_diff.py
"""
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t07_common as T  # noqa: E402

RES = HERE.parents[2]
STATUS = {"MATCH", "DIFF", "MISSING_IN_RERUN", "EXTRA_IN_RERUN", "NO_RERUN_FILE"}


def _rows(name):
    with open(HERE / "out" / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_rerun_reproduces_published_numbers_or_flags_them():
    rows = _rows("rerun_diff.csv")
    assert {r["result"] for r in rows} == set(T.RESULTS), "ten results required"
    assert len(T.RESULTS) == 10
    for key, (folder, pairs) in T.RESULTS.items():
        for pub_rel, _ in pairs:
            published = T.parse_file(RES / folder / pub_rel)
            mine = [r for r in rows if r["result"] == key and r["published_file"] == pub_rel and r["status"] != "EXTRA_IN_RERUN"]
            assert len(published) > 0, key
            assert len(mine) == len(published), (key, len(mine), len(published))
    for r in rows:
        assert r["status"] in STATUS, r
        if r["status"] == "DIFF":
            assert r["published"] != r["rerun"] or r["kind"] != "text", r


def test_one_study_is_deterministic():
    det = _rows("determinism.csv")
    assert len(det) >= 3
    for r in det:
        assert r["identical"] == "True", r


def test_every_stale_candidate_has_a_provenance_commit():
    prov = _rows("provenance.csv")
    com = _rows("provenance_commits.csv")
    assert len(prov) == 16
    stale = [p for p in prov if p["status"] == "STALE-CANDIDATE"]
    assert stale, "the audit found stale candidates; an empty list means the provenance walk broke"
    for p in stale:
        assert int(p["n_later_commits"]) >= 1 and p["latest_later_commit"], p
        assert any(c["num"] == p["num"] and c["later_sha"] == p["latest_later_commit"] for c in com), p
