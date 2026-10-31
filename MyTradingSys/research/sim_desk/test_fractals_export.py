"""The fractals results shown in the simulator must carry the same n and net R as each study's RESULT.md."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "artifact"))
import fractals_export as fx  # noqa: E402

FR = fx.FR


def md_table(path, first_cell):
    """Rows (list of cell lists) of the first markdown table whose header starts with first_cell."""
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("|") and ln.split("|")[1].strip() == first_cell:
            rows = []
            for r in lines[i:][2:]:
                if not r.startswith("|"):
                    break
                rows.append([c.strip() for c in r.strip().strip("|").split("|")])
            return rows
    raise AssertionError("table %r not found in %s" % (first_cell, path))


def test_p1b_matches_result_md():
    s = fx.p1b_stats()
    txt = open(os.path.join(FR, "p1b_rsi_feenet", "RESULT.md"), encoding="utf-8").read()
    assert ("Pooled fee-net mean R = %.3f" % s["mean_net"]) in txt
    assert ("on %d DEV events" % s["n"]) in txt
    row = [r for r in md_table(os.path.join(FR, "p1b_rsi_feenet", "RESULT.md"), "Slice") if r[0] == "4h"][0]
    assert int(row[1]) == s["by_tf"]["4h"][0] and abs(float(re.match(r"[+-]?[0-9.]+", row[3]).group()) - s["by_tf"]["4h"][2]) < 0.0006


def test_f1_matches_result_md():
    s = fx.f1_stats()
    for r in md_table(os.path.join(FR, "f1", "RESULT.md"), "group"):
        g = s["groups"]
        if r[0] == "CONF_ANY":
            n = g["CONF_4H"][0] + g["CONF_1D"][0]
            m = (g["CONF_4H"][0] * g["CONF_4H"][1] + g["CONF_1D"][0] * g["CONF_1D"][1]) / n
        else:
            n, m = g[r[0]]
        assert int(r[1]) == n, r[0]
        assert abs(float(r[2]) - m) < 0.00006, r[0]


def test_f2_matches_result_md():
    s = fx.f2_stats()
    for r in md_table(os.path.join(FR, "f2", "RESULT.md"), "test"):
        k = s[r[0]]
        assert int(r[3]) == k["n_kept"] and int(r[4]) == k["n_removed"], r[0]
        assert abs(float(r[5].split("[")[0]) - k["kept_mean"]) < 0.0006, r[0]


def test_f3_matches_result_md():
    s = fx.f3_stats()
    for r in md_table(os.path.join(FR, "f3", "RESULT.md"), "variant"):
        name = r[0].split()[0]
        assert int(r[2]) == s[name]["n"], name
        assert abs(float(r[4]) - s[name]["mean_pct"]) < 0.0006, name


def test_built_results_are_valid():
    res = fx.build_all()
    assert len(res) == 5
    assert len({r["id"] for r in res}) == 5
    for r in res:
        assert r["family"] == fx.FAMILY and r["provenance"] == "exported"
        assert all(w["label"] in ("SOURCED", "OURS") for w in r["what"]), r["id"]
        for e in r["examples"]:
            for t in e.get("trades", [])[:50]:
                assert not ({"entry", "exit", "price"} & set(t)), r["id"]
        assert len(json.dumps(r)) < 1500000, r["id"]
