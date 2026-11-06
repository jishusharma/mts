"""base_rates.js registry: schema, every row equals its study output, five *_rates.js globals gone (card prob-base-rates-registry-1106)."""
import csv
import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
RES = HERE.parents[1] / "research"
REG_JS = HERE / "base_rates.js"
IDS = {"us_open_levels", "anticipation_oi_delta", "level_approach_prior_day", "bigcandle_story", "candle_flip_cells"}
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
