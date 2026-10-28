"""scorecard-recount-jis-nb-store: per-analyst recount from a rows.json store, and the committed scorecard matches it."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

TRADE = {"direction": "SHORT", "entry": "83000", "target": "78000", "invalidation": "above high"}


def _store():
    rows = []
    for name, n in (("Michael", 5), ("Jason", 2), ("Krown", 4), ("Michaal", 1)):
        rows += [{"analyst": name, "trades": []} for _ in range(n)]
    rows.append({"analyst": "Qriptal", "trades": [dict(TRADE), dict(TRADE)]})
    return {"rows": rows}


def test_recount_keeps_michael_and_michaal_apart():
    import cbp_scorecard
    c = cbp_scorecard.recount(_store())
    assert c["Michael"]["rows"] == 5 and c["Michaal"]["rows"] == 1
    assert c["Jason"]["rows"] == 2 and c["Krown"]["rows"] == 4
    assert c["Qriptal"] == {"rows": 1, "trades": 2, "tradable_rows": 1}
    assert c["Krown"]["tradable_rows"] == 0


def test_scorecard_doc_shows_the_store_counts():
    text = (ROOT / "MyTradingSys/research/cbp/SCORECARD_GPT.md").read_text(encoding="utf-8")
    assert "Michael (Pizzino" in text and "Michaal (van de Poppe" in text
    for line in ("| **Michael", "| **Krown"):
        row = next(ln for ln in text.splitlines() if ln.startswith(line))
        assert "| 0 (local)" not in row
    assert "13 rows" in text
