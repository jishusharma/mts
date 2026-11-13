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
