"""nk_extract_concepts: every NK extract video has a concept in the nk-stocktalk layer, its quotes are verbatim, NK_FACTS.md is in sync."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_conceptualizer as mc  # noqa: E402
import nk_extract_concepts as nk  # noqa: E402


def _layer():
    return next(L for L in json.loads(nk.CONCEPTS.read_text(encoding="utf-8"))["layers"] if L["id"] == nk.LAYER)


def test_every_extract_video_has_a_concept_with_a_sourced_quote_and_path():
    ids = {c["id"]: c for c in _layer()["concepts"]}
    for vid in nk.VIDEOS:
        assert (nk.IV / vid / "EXTRACT.md").is_file()
        c = ids.get(nk.PREFIX + vid.lower().replace("_", "-"))
        assert c, f"no concept for extract {vid}"
        assert vid in c["quote"]["src"] and c["quote"]["src"].count("interviews/") == 2
        assert c["params"] and all(p[2].startswith("SOURCED") for p in c["params"])


def test_concept_quotes_are_verbatim_from_the_extract():
    for vid in nk.VIDEOS:
        text = (nk.IV / vid / "EXTRACT.md").read_text(encoding="utf-8")
        c = next(c for c in _layer()["concepts"] if c["id"] == nk.PREFIX + vid.lower().replace("_", "-"))
        assert f'> "{c["quote"]["text"]}"' in text
        for p in c["params"]:
            assert p[2].split("«", 1)[1].split("»", 1)[0] in text


def test_concepts_and_facts_are_in_sync_and_page_builds():
    assert nk.differs() == []
    assert mc.load()["layers"]  # load() raises on any problem row


def test_stale_concepts_are_detected(tmp_path, monkeypatch):
    monkeypatch.setattr(nk, "FACTS", tmp_path / "NK_FACTS.md")  # facts file missing
    assert str(tmp_path / "NK_FACTS.md") in nk.differs()
    data = json.loads(nk.CONCEPTS.read_text(encoding="utf-8"))
    L = next(L for L in data["layers"] if L["id"] == nk.LAYER)
    L["concepts"] = [c for c in L["concepts"] if not c["id"].startswith(nk.PREFIX)]
    monkeypatch.setattr(nk, "current", lambda: data)
    d, _ = nk.desired(data)
    assert len([c for c in next(x for x in d["layers"] if x["id"] == nk.LAYER)["concepts"] if c["id"].startswith(nk.PREFIX)]) == len(nk.VIDEOS)
