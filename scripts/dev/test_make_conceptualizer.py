"""make_conceptualizer.py: the real concepts.json renders; a bad status, an untagged parameter and a missing diagram are caught."""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_conceptualizer as mc  # noqa: E402


def test_real_data_is_clean_and_every_concept_renders():
    data = mc.load()
    html = mc.render(data)
    assert "<title>Conceptualizer</title>" in html
    for L in data["layers"]:
        for c in L["concepts"]:
            assert f'"id": "{c["id"]}"' in html
    blob = html.split('<script id="data" type="application/json">', 1)[1].split("</script>", 1)[0]
    assert "</" not in blob  # an svg end tag must not close the data script early


def test_problems_are_caught():
    import json
    data = json.loads((mc.SRC / "concepts.json").read_text(encoding="utf-8"))
    bad = copy.deepcopy(data)
    c = bad["layers"][0]["concepts"][0]
    c["status"] = "maybe"
    c["params"][0][2] = "GUESS"
    c["diagram"] = "nope.svg"
    del c["question"]
    text = "\n".join(mc.problems(bad))
    assert "status 'maybe'" in text
    assert "SOURCED, OURS or NOT_SEEN" in text
    assert "diagram nope.svg missing" in text
    assert "no question" in text
    assert mc.problems(data) == []


def test_not_seen_is_a_valid_tag():
    import json
    data = json.loads((mc.SRC / "concepts.json").read_text(encoding="utf-8"))
    c = data["layers"][0]["concepts"][0]
    c["params"][0][2] = "NOT_SEEN (never stated)"
    assert mc.problems(data) == []


def test_each_tag_has_its_own_css_class_and_unknown_tags_are_flagged():
    tpl = mc.TPL.read_text(encoding="utf-8")
    for cls in ("t-SOURCED", "t-OURS", "t-NOT_SEEN", "t-BAD"):
        assert "." + cls + " {" in tpl
    assert "/^NOT_SEEN/.test(t) ? 't-NOT_SEEN'" in tpl
    assert "/^OURS/.test(t) ? 't-OURS' : 't-BAD'" in tpl


def test_size_words_in_rows_are_caught():
    import json
    data = json.loads((mc.SRC / "concepts.json").read_text(encoding="utf-8"))
    c = data["layers"][0]["concepts"][0]
    c["params"][0][1] = "two lots per rung"
    c["params"].append(["Risk", "₹9,750", "SOURCED: x"])
    text = "\n".join(mc.problems(data))
    assert text.count("size word") == 2


def _real():
    import json
    return json.loads((mc.SRC / "concepts.json").read_text(encoding="utf-8"))


def test_odd_types_are_reported_not_raised():
    data = _real()
    c = data["layers"][0]["concepts"]
    c[0]["params"] = None
    c[1]["params"] = [{"a": 1}, ["a", "b", 5], ["a", "b", None]]
    c[2]["fidelity"] = {"a": 1}
    c[3]["diagram"] = 5
    c.append("x")
    text = "\n".join(mc.problems(data))
    assert "params is not a list" in text and "fidelity grade" in text and "diagram 5" in text and "not an object" in text
    assert text.count("needs 3 strings") == 3
    assert mc.problems({"layers": None}) == ["layers is not a list"]


def test_tag_must_be_the_whole_word():
    data = _real()
    p = data["layers"][0]["concepts"][0]["params"]
    p[:] = [["a", "b", "SOURCEDX"], ["a", "b", "OURSELVES"], ["a", "b", "OURS: x"], ["a", "b", "NOT_SEEN (y)"], ["a", "b", "SOURCED"]]
    assert "\n".join(mc.problems(data)).count("needs 3 strings") == 2


def test_size_variants_are_caught():
    data = _real()
    p = data["layers"][0]["concepts"][0]["params"]
    p[:] = [["a", "10lots", "OURS"], ["lot_size", "1", "OURS"], ["a", "2 लॉट", "OURS"], ["a", "Rs 5000", "OURS"], ["a", "INR 500", "OURS"],
            ["Slot", "pilot run", "OURS"]]
    assert "\n".join(mc.problems(data)).count("size word") == 5


def test_empty_text_duplicate_layer_fidelity_and_diagram_escape_are_caught():
    data = _real()
    c = data["layers"][0]["concepts"]
    c[0]["rule"] = ""
    c[1]["id"] = c[2]["id"]
    c[3]["fidelity"] = ["great", "x"]
    c[4]["diagram"] = "../concepts.json"
    data["layers"].append(data["layers"][1])
    text = "\n".join(mc.problems(data))
    for want in ("empty rule", "duplicate id", "fidelity grade", "diagram ../concepts.json", "duplicate layer id"):
        assert want in text, want


# ---- wiring checks (operator order 2026-11-14: "every MTS layer is in the Conceptualizer" is a machine check) ----
def _wired(data, families):
    """Give each layer of `data` the family ids it claims, so only the check under test can fail."""
    for i, L in enumerate(data["layers"]):
        L["families"] = [families[i % len(families)]]
        L["tests"] = [r[:6] + ["MyTradingSys/system/layer_index.json"] for r in L["tests"]]
    return data


def test_family_without_a_conceptualizer_layer_fails_the_build():
    data = _real()
    fams = ["fam_a", "fam_b"]
    _wired(data, fams)
    assert mc.problems(data, families=fams) == []
    text = "\n".join(mc.problems(data, families=fams + ["fam_orphan"]))
    assert "layer family 'fam_orphan' (layer_index.json) has no Conceptualizer layer" in text


def test_layer_claiming_an_unknown_family_or_none_fails():
    data = _real()
    _wired(data, ["fam_a"])
    data["layers"][0]["families"] = ["ghost"]
    del data["layers"][1]["families"]
    text = "\n".join(mc.problems(data, families=["fam_a"]))
    assert "family 'ghost' is not in layer_index.json" in text
    assert "families must be a non-empty list" in text


def test_test_row_needs_a_source_path_that_exists():
    data = _real()
    _wired(data, ["fam_a"])
    rows = data["layers"][0]["tests"]
    rows[:] = [["s", "1h", "10", "-0.1R", "FAIL", "l"],                                     # no source cell
               ["s", "1h", "10", "-0.1R", "FAIL", "l", ""],                                 # empty source
               ["s", "1h", "10", "-0.1R", "FAIL", "l", "MyTradingSys/nope/NOT_THERE.md"],   # missing file
               ["s", "1h", "10", "-0.1R", "FAIL", "l", "../outside.md"],                    # escapes the repo
               ["s", "1h", "10", "-0.1R", "FAIL", "l", "MyTradingSys/system/layer_index.json:3 ; scripts/dev/make_conceptualizer.py"]]  # ok
    text = "\n".join(mc.problems(data, families=["fam_a"]))
    assert text.count("no source path") == 2
    assert text.count("does not exist in the repo") == 2
    assert "test#4" not in text


def test_real_data_wiring_is_clean():
    """The shipped concepts.json: every layer_index family is wired and every test row's source exists."""
    fams = mc.family_ids()
    assert fams, "layer_index.json must be readable"
    assert mc.problems(_real(), families=fams) == []


def test_load_runs_the_wiring_check():
    import json
    import tempfile
    data = _real()
    for L in data["layers"]:
        L.pop("families", None)
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "diagrams").mkdir()
        (Path(d) / "concepts.json").write_text(json.dumps(data), encoding="utf-8")
        try:
            mc.load(Path(d))
        except SystemExit as e:
            assert "families must be a non-empty list" in str(e)
        else:
            raise AssertionError("load() must refuse a layer without families")
