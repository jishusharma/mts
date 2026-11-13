"""live_aid_learn tests (card live-aid-learning-loop-1111). Synthetic events, no network."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import live_aid_learn as la  # noqa: E402  (ImportError before the module exists)


def ev(kind, state, at, wins, n):
    return [{"kind": kind, "side": "LONG", "state": state, "at": at, "r1h": 0.1 if i < wins else -0.1} for i in range(n)]


def rows_by_name(rows):
    return {r["name"]: r for r in rows}


def test_n_and_hit_rate_exact():
    r = rows_by_name(la.score(ev("idea", "REJECTED", "Day open", 36, 60)))
    assert r["idea"]["n"] == 60 and abs(r["idea"]["hit"] - 60.0) < 1e-9


def test_large_gap_enough_n_is_implement():
    r = rows_by_name(la.score(ev("idea", "REJECTED", "Day open", 36, 60)))["idea"]
    assert r["verdict"].startswith("test")


def test_small_n_goes_to_operator_not_implement():
    rows = la.score(ev("idea", "FAILED BREAK", "Asia low", 18, 20))
    r = rows_by_name(rows)["idea fade @ Asia low"]
    assert r["n"] == 20 and r["verdict"].startswith("NOT-ENOUGH-EVIDENCE")
    assert la.split(rows)[0] == []  # nothing to implement


def test_small_gap_not_implement():
    r = rows_by_name(la.score(ev("setup", "", "x", 52, 100)))["setup"]
    assert r["verdict"].startswith("NOT-ENOUGH-EVIDENCE")


def test_none_r1h_skipped():
    e = ev("idea", "REJECTED", "Day open", 5, 10) + [{"kind": "idea", "side": "LONG", "state": "REJECTED", "at": "Day open", "r1h": None}]
    assert rows_by_name(la.score(e))["idea"]["n"] == 10


def test_diff_against_previous_day():
    prev = "| name | n | hit |\n|---|---|---|\n| idea | 50 | 40% |\n"
    assert la.parse_prev(prev) == {"idea": 40.0}


def test_tables_md_fallback_parses_committed_review():
    rows = la.load_tables_md(la.REVIEW / "tables.md")
    d = rows_by_name(rows)
    assert d["idea"]["n"] == 759 and round(d["idea"]["hit"]) == 47
    assert d["idea fade @ Yesterday low"]["verdict"].startswith("test")
    assert d["idea fade @ Last week low"]["verdict"].startswith("NOT-ENOUGH-EVIDENCE")


def test_page_csv_header_scores_rows(tmp_path):
    """Header of home.js FLAG_COLS + synthetic klines: rows > 0, r1h computed, SHORT sign flipped."""
    t0 = 1794000000000 // 60000 * 60000
    kl = tmp_path / "k.json"
    kl.write_text('[[%d,"0","0","0","101","0"],[%d,"0","0","0","99","0"]]' % (t0 + 3600000, t0 + 3600000 + 60000))
    csvp = tmp_path / "log.csv"
    iso = lambda ms: __import__("datetime").datetime.fromtimestamp(ms / 1000, __import__("datetime").timezone.utc).isoformat()
    csvp.write_text("\n".join(["t,kind,side,level,evidence,price", "%s,idea,LONG,Day open,REJECTED,100" % iso(t0), "%s,idea,SHORT,Day open,REJECTED,100" % iso(t0 + 60000), "%s,idea,LONG,Day open,REJECTED,100" % iso(t0 + 7200000), ""]))
    rows = la.load_log(csvp, la.load_klines(kl))
    assert [r["r1h"] for r in rows] == [1.0, 1.0, None]  # LONG +1%, SHORT vs 99 = +1%, no kline
    assert rows[0]["at"] == "Day open" and rows[0]["state"] == "REJECTED"
    assert rows_by_name(la.score(rows))["idea"]["n"] == 2
