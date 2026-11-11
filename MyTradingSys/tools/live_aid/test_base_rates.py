"""base_rates.js registry: schema, every row equals its study output, five *_rates.js globals gone (card prob-base-rates-registry-1106)."""
import csv
import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
RES = HERE.parents[1] / "research"
REG_JS = HERE / "base_rates.js"
IDS = {"us_open_levels", "us_open_first3m", "anticipation_oi_delta", "level_approach_prior_day", "bigcandle_story", "setup_board_mix", "candle_flip_cells"}
FIELDS = {"id", "event", "condition", "outcome", "horizon", "n", "units", "window", "regime_mix", "fee_status", "source", "built_utc", "table"}


def registry():
    assert REG_JS.exists(), "base_rates.js missing: run python MyTradingSys/tools/live_aid/base_rates.py build"
    s = REG_JS.read_text(encoding="utf-8")
    return json.loads(s[s.index("= ") + 2:s.rindex(";")])


def test_schema_every_row_has_n_window_units():
    reg = registry()
    assert set(reg) == IDS
    for k, r in reg.items():
        assert set(r) == FIELDS, k
        assert r["id"] == k and isinstance(r["n"], int) and r["n"] > 0, k
        for f in ("window", "units", "horizon", "outcome", "fee_status", "source", "regime_mix", "built_utc"):
            assert isinstance(r[f], str) and r[f].strip(), (k, f)
        assert re.search(r"\d{4}-\d{2}-\d{2}", r["window"]), k
        assert (RES.parent / r["source"].split(" ")[0]).exists(), (k, r["source"])


def test_us_open_table_equals_results_json():
    ref = json.loads((RES / "us_open_levels_2026-10-30" / "results.json").read_text(encoding="utf-8"))
    r = registry()["us_open_levels"]
    assert r["table"] == ref and r["n"] == ref["meta"]["days"]
    assert r["window"] == "%s..%s" % tuple(ref["meta"]["range"])


def _first3_study():
    import importlib.util
    spec = importlib.util.spec_from_file_location("first3_study", RES / "us_open_first3m_2026-11-11" / "study.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_us_open_first3m_table_equals_results_json():
    ref = json.loads((RES / "us_open_first3m_2026-11-11" / "results.json").read_text(encoding="utf-8"))
    r = registry()["us_open_first3m"]
    assert r["table"] == ref and r["n"] == ref["meta"]["days"] >= 1000
    assert r["window"] == "%s..%s" % tuple(ref["meta"]["range"])
    assert "base_rates_input" in (RES / "us_open_first3m_2026-11-11" / "study.py").read_text(encoding="utf-8")


def _bars(p0, c1, c3, c30, c60, pre_open=100.0, pre_close=100.0, taker=0.5):
    """121 flat bars with hand-set prices: bar 30 opens at pre_open, bar 59 closes at pre_close, bar 60 opens at p0."""
    k = [[100.0, 100.0, 100.0, 100.0, 10.0, 10.0 * taker] for _ in range(121)]
    k[30][0], k[59][3] = pre_open, pre_close
    k[60][0], k[60][3], k[62][3], k[89][3], k[119][3] = p0, c1, c3, c30, c60
    for i in (60, 61, 62):
        k[i][4] = 30.0
    return k


def test_us_open_first3m_row_hand_case():
    st = _first3_study()
    # open 100, minute 1 closes 101, minute 3 closes 102, +30 min 99.96, +60 min 104.04; drift before the open 100 -> 99
    r = st.row_from_bars("2026-11-10", _bars(100.0, 101.0, 102.0, 99.96, 104.04, pre_close=99.0, taker=0.4))
    assert r["open_utc"] == "14:30Z"                      # 09:30 New York in winter time
    assert r["m1"] == pytest.approx(0.01) and r["m3"] == pytest.approx(0.02)
    assert r["f30"] == pytest.approx(-0.02) and r["f60"] == pytest.approx(0.02)   # from the minute-3 close, 102
    assert r["pre30"] == pytest.approx(-0.01) and r["taker"] == pytest.approx(0.4)
    assert r["vol_ratio"] == pytest.approx(3.0)           # 3 x 30 over 3 x 10
    assert st.row_from_bars("2026-07-01", _bars(100, 100, 100, 100, 100))["open_utc"] == "13:30Z"   # summer time


def test_us_open_first3m_summary_hand_case():
    st = _first3_study()
    mk = lambda d, m3, f60, pre30: dict(day=d, open_utc="14:30Z", p0=100.0, pre30=pre30, pre5=pre30, taker=0.5, m1=m3, m3=m3, f30=f60, f60=f60, vol_ratio=2.0)  # noqa: E731
    rows = [mk("2026-01-05", 0.01, 0.02, -0.01), mk("2026-01-06", 0.02, -0.01, 0.01), mk("2026-01-07", -0.03, -0.01, 0.01), mk("2026-01-08", 0.04, 0.0, -0.02)]
    t = st.summarize(rows, skipped=2)
    assert t["meta"]["days"] == 4 and t["meta"]["skipped"] == 2 and t["meta"]["range"] == ["2026-01-05", "2026-01-08"]
    assert t["follow"]["m3_f60"] == [2, 3]                # day 4 has a zero follow move: left out of both counts
    assert t["follow"]["pre30_m3"] == [1, 4]              # only 01-06 has the drift and the first 3 min on the same side
    assert t["size"]["m3"]["up"] == 3 and t["size"]["m3"]["down"] == 1
    assert t["size"]["m3"]["p50"] == 0.02                 # sorted abs [0.01, 0.02, 0.03, 0.04], index int(0.5 * 3) = 1
    assert t["follow"]["big_cut"] == 0.04 and t["follow"]["big_m3_f60"] == [0, 0]   # 4 // 4 = 1 day, its follow move is zero


def test_live_aid_shows_the_first3_line_from_the_registry():
    import os
    import shutil
    import subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    t = registry()["us_open_first3m"]["table"]
    runner = ("const A=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);"
              "console.log(JSON.stringify([A.first3Line(j.t),A.first3Line(j.bad),A.first3Line(null)]))})")
    bad = json.loads(json.dumps(t))
    bad["follow"]["m3_f60"] = [0, 0]
    out = subprocess.run([node, "-e", runner, str(HERE / "live_aid_indicators.js")], input=json.dumps({"t": t, "bad": bad}),
                         capture_output=True, text=True, timeout=60, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    line, bad_line, none_line = json.loads(out.stdout)
    f = t["follow"]
    assert "%d of %d (%d%%)" % (f["m3_f60"][0], f["m3_f60"][1], round(100 * f["m3_f60"][0] / f["m3_f60"][1])) in line
    assert "%.2f%%" % (100 * t["size"]["m3"]["p50"]) in line and "Size, not direction" in line and t["meta"]["range"][1] in line
    assert bad_line == "" and none_line == ""            # fail closed: no table, no line
    html = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert 'id="uo-first3"' in html and "A.first3Line(brRow('us_open_first3m').table)" in html


def test_flip_table_equals_cells_csv():
    with open(RES / "candle_flip_probability_2026-11" / "cells.csv", newline="", encoding="utf-8") as fh:
        ref = list(csv.DictReader(fh))
    t = registry()["candle_flip_cells"]["table"]
    assert len(t) == len(ref) == 96
    for a, b in zip(t, ref):
        assert (a["group"], a["cell"], a["colour"]) == (b["group"], b["cell"], b["colour"])
        assert (a["n"], a["n_fit"], a["weeks"]) == (int(b["n"]), int(b["n_fit"]), int(b["weeks"]))
        assert a["realised"] == pytest.approx(float(b["realised"])) and a["p"] == pytest.approx(float(b["p"]))
        assert a["survives_48"] == (b["survives_48"] == "True")


def test_anticipation_table_equals_result_md():
    # independent parse of the study's own RESULT.md table: n, share, continue %, undone % and OI % per state
    md = (RES / "anticipation_map_2026-11-05" / "RESULT.md").read_text(encoding="utf-8")
    r = registry()["anticipation_oi_delta"]
    seen = 0
    for ln in md.splitlines():
        m = re.match(r"\| (UP|DOWN) / (UP|DOWN) / (BUY|SELL) \|[^|]*\| (\d+) \| (\d+)% \| (\d+)% \| (\d+)% \| (\d+)% \|", ln)
        if m:
            c = r["table"]["rates"]["|".join(m.group(1, 2, 3))]
            assert [c["n"], c["share"], c["cont"], c["kill"], c["oiCont"]] == [int(x) for x in m.group(4, 5, 6, 7, 8)], ln
            seen += 1
    assert seen == 8 and len(r["table"]["rates"]) == 8
    assert r["n"] == r["table"]["meta"]["events"] == 21855


def test_level_approach_table_equals_result_md():
    md = (RES / "level_approach_prep_2026-11-05" / "RESULT.md").read_text(encoding="utf-8")
    r = registry()["level_approach_prior_day"]
    u1 = r["table"]["u1"]
    assert "| absorption | %d | %d%% | %d%% |" % (u1["abs"]["n"], u1["abs"]["rev"], u1["abs"]["brk"]) in md
    assert "| non-absorption | %d | %d%% | %d%% |" % (u1["non"]["n"], u1["non"]["rev"], u1["non"]["brk"]) in md
    assert u1["all"] == r["n"] == 887


def test_bigcandle_table_equals_tables_md():
    md = (RES / "bigcandle_story_2026-11-05" / "tables.md").read_text(encoding="utf-8")
    r = registry()["bigcandle_story"]
    assert "1h events %d, 5m events %d" % (r["table"]["meta"]["events_1h"], r["table"]["meta"]["events_5m"]) in md
    assert r["n"] == r["table"]["meta"]["events_1h"] == 843
    c = r["table"]["cells"]["BASE|DOWN"]
    assert re.search(r"\| all DOWN bars \| %d \| %d%% " % (c["n"], round(c["1h"]["cont"])), md)


def test_old_rates_globals_are_gone_from_the_live_aid():
    for name in ("us_open", "anticipation", "level_approach", "bigcandle"):
        assert not (HERE / (name + "_rates.js")).exists(), name
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert '<script src="base_rates.js"></script>' in page
    for g in ("US_OPEN_RATES", "ANTICIPATION_RATES", "BIGCANDLE_RATES", "LEVEL_APPROACH_RATES", "us_open_rates.js", "anticipation_rates.js", "bigcandle_rates.js", "level_approach_rates.js"):
        assert g not in page, g
    assert (HERE / "cycle_flag_data.js").exists()


def test_studies_write_into_the_registry_input_dir_not_next_to_it():
    """A study re-run must not recreate the deleted *_rates.js globals in live_aid/ (card studies-write-into-base-rates-registry)."""
    studies = ["anticipation_map_2026-11-05", "bigcandle_story_2026-11-05", "level_approach_prep_2026-11-05", "us_open_levels_2026-10-30"]
    for d in studies:
        src = (HERE.parents[1] / "research" / d / "study.py").read_text(encoding="utf-8")
        assert "base_rates_input" in src, d
        assert "'live_aid', '" not in src.replace("'live_aid', 'base_rates_input'", ""), d
        assert '"live_aid" / "' not in src.replace('"live_aid" / "base_rates_input"', ""), d
    import base_rates
    assert base_rates.INPUT_DIR == base_rates.HERE / "base_rates_input"


# ---- setup board hit rate per evidence mix (card live-aid-board-rates-1111) ----
def _ev(side, home, grid, adx15, adx1h, vfi15, wt30, r1h, ts, kind="idea"):
    return {"kind": kind, "side": side, "home": home, "grid": grid, "adx15": adx15, "adx1h": adx1h, "vfi15": vfi15, "wt30": wt30, "r1h": r1h, "ts": ts}


D = 86400000
FIXTURE = [  # ten rows; hand counts in the test below
    _ev("LONG", "LONG", "UP", 0, 0, 0, 0, 0.5, 20000 * D),
    _ev("LONG", "LONG", "UP", 0, 0, 0, 0, -0.2, 20000 * D + 1),
    _ev("LONG", "LONG", "UP", 5, 0, 0, 0, 0.1, 20001 * D),
    _ev("LONG", "LONG", "UP", 0, 0, 0, 0, 1.0, 20002 * D),
    _ev("SHORT", "SHORT", "DOWN", 0, 0, 0, 0, 0.3, 20001 * D),
    _ev("SHORT", "SHORT", "DOWN", 0, 0, 0, 0, -0.4, 20001 * D),
    _ev("LONG", "WAIT", "UP", 25, 0, 0, 0, 0.2, 20002 * D),
    _ev("LONG", "WAIT", "UP", 30, 0, 0, 0, 0.0, 20002 * D),
    _ev("LONG", "LONG", "UP", 0, 0, 0, 0, 0.9, 20003 * D, kind="setup"),   # not an idea flag: ignored
    _ev("LONG", "LONG", "UP", 0, 0, 0, 0, None, 20003 * D),                # not scored yet: ignored
]


def test_setup_board_rates_hand_case():
    import base_rates as br
    t = br.setup_board_table(FIXTURE)
    by = {(r["side"], r["mix"]): r for r in t["rows"]}
    assert set(by) == {("LONG", "home+grid"), ("LONG", "grid+adx15"), ("SHORT", "home+grid")}
    a = by[("LONG", "home+grid")]          # r1h 0.5, -0.2, 0.1, 1.0 -> 3 right of 4
    assert (a["n"], a["hits"], a["rate"]) == (4, 3, 0.75)
    b = by[("LONG", "grid+adx15")]         # 0.2 right, 0.0 is not right (strict > 0) -> 1 of 2
    assert (b["n"], b["hits"], b["rate"]) == (2, 1, 0.5)
    c = by[("SHORT", "home+grid")]
    assert (c["n"], c["hits"], c["rate"]) == (2, 1, 0.5)
    assert all(r["low_n"] is True for r in t["rows"])
    assert all(r["window"] == "2024-10-04..2024-10-06" for r in t["rows"])
    assert t["meta"]["min_n"] == 30 and t["meta"]["range"] == ["2024-10-04", "2024-10-06"]


def test_setup_board_rates_low_n_boundary():
    import base_rates as br
    mk = lambda k: [_ev("LONG", "LONG", "UP", 0, 0, 0, 0, 0.1, 20000 * D + i) for i in range(k)]
    assert br.setup_board_table(mk(29))["rows"][0]["low_n"] is True
    assert br.setup_board_table(mk(30))["rows"][0]["low_n"] is False


def test_setup_board_rates_writes_input_file(tmp_path, monkeypatch):
    import base_rates as br
    monkeypatch.setattr(br, "INPUT_DIR", tmp_path)
    ev = tmp_path / "events.json"
    ev.write_text(json.dumps(FIXTURE))
    br.write_setup_board_rates(ev)
    t = br.read_js_var(tmp_path / "setup_board_rates.js")
    assert len(t["rows"]) == 3 and t["meta"]["events"] == 8
