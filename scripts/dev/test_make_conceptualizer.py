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
    assert "SOURCED or OURS" in text
    assert "diagram nope.svg missing" in text
    assert "no question" in text
    assert mc.problems(data) == []
