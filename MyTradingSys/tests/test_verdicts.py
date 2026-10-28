"""verdicts.py: backfill on a tmp research folder, check exit codes, count."""
import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("mts_verdicts", ROOT / "scripts" / "dev" / "verdicts.py")
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)

KILLED_RESULT = """FAIL

# RESULT: ZZ-FADE-ENGULF, widget fade at the engulf close, DEV screen (primary cell h=60, cost 0.14 % round trip)

DEV-only exploration; VALIDATION and HOLDOUT were not read.

## Verdict arms (mean G %)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | verdict |
|---|---|---|---|---|---|---|
| A1: engulf close, SHORT, h=60 | 500 | 0.0124 | 0.0212 | -0.1276 | -6.02 | FAIL |
| A2: second break, SHORT, h=60 | 300 | 0.0143 | 0.0257 | -0.1257 | -4.89 | INCONCLUSIVE |
"""
KILLED_PRE = """# PRE-REGISTRATION: ZZ-FADE-ENGULF widget fade at the engulf close, BTCUSDT, DEV only (frozen 2026-10-16)

One run of the primary cell. FAIL means stop: no detector or layer work on this hypothesis family (widget engulf fade on 5m BTC).
"""
SECOND_RESULT = """INCONCLUSIVE

# RESULT: QQ-OTHER-IDEA, gadget breakout, DEV screen (primary cell h=60, cost 0.14 % round trip)

## Primary cell

| arm | n | mean | SE | t_cost | MDD |
|---|---|---|---|---|---|
| T | 40 | -0.0568 | 0.1304 | -1.51 | 8.47 |
| C | 1439 | -0.0081 | 0.0246 | -6.03 | 214.21 |
"""


def _tmp_root(tmp_path):
    root = tmp_path / "research"
    for name, res, pre in (("zz_fade_2026-10-16", KILLED_RESULT, KILLED_PRE), ("qq_other_2026-10-15", SECOND_RESULT, None)):
        d = root / name
        d.mkdir(parents=True)
        (d / "RESULT.md").write_text(res, encoding="utf-8", newline="\n")
        if pre:
            (d / "PRE_REG.md").write_text(pre, encoding="utf-8", newline="\n")
    return root


def _run(tmp_path, *args):
    root = _tmp_root(tmp_path) if not (tmp_path / "research").exists() else tmp_path / "research"
    return vd.main(["--root", str(root), "--csv", str(tmp_path / "V.csv"), *args])


def _rows(tmp_path):
    with open(tmp_path / "V.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_backfill_parses_two_studies(tmp_path, capsys):
    assert _run(tmp_path, "backfill") == 0
    rows = _rows(tmp_path)
    assert len(rows) == 4                      # A1, A2, T, C
    by = {(r["study_dir"], r["arm"].split(":")[0]): r for r in rows}
    a1 = by[("zz_fade_2026-10-16", "A1")]
    assert (a1["n"], a1["gross_mean_pct"], a1["se_pct"], a1["cost_pct"]) == ("500", "0.0124", "0.0212", "0.14")
    assert a1["verdict"] == "FAIL" and a1["split_read"] == "DEV" and a1["one_run"] == "yes"
    assert "widget engulf fade" in a1["kill_scope"]
    assert by[("zz_fade_2026-10-16", "A2")]["verdict"] == "INCONCLUSIVE"
    t, c = by[("qq_other_2026-10-15", "T")], by[("qq_other_2026-10-15", "C")]
    assert t["verdict"] == "INCONCLUSIVE" and c["verdict"] == "FAIL" and "derived" in c["kill_scope"]
    assert t["one_run"] == "no"                # no PRE_REG in that folder
    assert t["commit"] == "UNPARSED" and t["date"] == "2026-10-15"   # tmp folder is not a git repo
    out = capsys.readouterr().out
    assert "4 rows" in out and "2 studies" in out


def test_unparsed_not_guessed(tmp_path, capsys):
    d = tmp_path / "research" / "free_text_2026-10-09"
    d.mkdir(parents=True)
    (d / "RESULT.md").write_text("# Some notes\n\nNothing tabular here.\n", encoding="utf-8", newline="\n")
    assert _run(tmp_path, "backfill") == 0
    r = _rows(tmp_path)[0]
    assert r["verdict"] == r["n"] == r["split_read"] == "UNPARSED"
    assert "UNPARSED free_text_2026-10-09" in capsys.readouterr().out


def test_check_exit_codes(tmp_path, capsys):
    _run(tmp_path, "backfill")
    capsys.readouterr()
    assert _run(tmp_path, "check", "widget engulf fade") == 1        # killed family
    assert "BLOCK" in capsys.readouterr().out
    assert _run(tmp_path, "check", "gadget breakout") == 1           # one_run? no PRE_REG => only prior rows, but FAIL row C
    assert _run(tmp_path, "check", "banana pricing momentum") == 0   # new family
    assert "no prior row" in capsys.readouterr().out


def test_check_inconclusive_without_one_run_does_not_block(tmp_path):
    root = tmp_path / "research" / "only_inc_2026-10-14"
    root.mkdir(parents=True)
    (root / "RESULT.md").write_text("INCONCLUSIVE\n\n# RESULT: ONLY-INC, gizmo sweep, DEV screen\n", encoding="utf-8", newline="\n")
    _run(tmp_path, "backfill")
    assert _run(tmp_path, "check", "gizmo sweep") == 0


def test_count_split(tmp_path, capsys):
    _run(tmp_path, "backfill")
    capsys.readouterr()
    assert _run(tmp_path, "count", "--split", "DEV") == 0
    # zz_fade: A1 + A2 on DEV; qq_other says no split, so T and C are UNPARSED and not counted
    assert capsys.readouterr().out.split()[0] == "2"
    assert _run(tmp_path, "count", "--split", "VALIDATION") == 0
    assert capsys.readouterr().out.split()[0] == "0"


def test_csv_uses_lf(tmp_path):
    _run(tmp_path, "backfill")
    assert b"\r" not in (tmp_path / "V.csv").read_bytes()


def test_real_registry_has_q72():
    rows = vd.load(vd.CSV_PATH)
    q72 = [r for r in rows if r["study_dir"] == "gross_effect_screen_2026-10-15"]
    assert {r["arm"]: r["verdict"] for r in q72} == {"T": "INCONCLUSIVE", "C": "FAIL"}
    assert all(r["one_run"] == "yes" and r["commit"] == "b42cef1b" for r in q72)
    assert vd.main(["check", "session extreme fade delta flow"]) == 1
