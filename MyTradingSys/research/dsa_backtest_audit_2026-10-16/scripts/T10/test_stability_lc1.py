"""LC1 consumers: the 8-family KEEP set is void on the fair control; the consumers must say so (annotate only, no rerun)."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
LC = REPO / "MyTradingSys/research/levels_confluence_2026-10-14"
LEGACY = "LEGACY 8-family set, void since T05-F5"


def _t(p):
    return Path(p).read_text(encoding="utf-8")


def test_stability_lc1_row_labelled_legacy():
    src = _t(Path(__file__).with_name("stability.py"))
    assert '"levels_hold LC1 KEEP (' + LEGACY in src
    assert LEGACY in src.split("def lc1_rows():")[1].split('"""')[1]


def test_ladder_consumers_labelled_legacy():
    assert "# " + LEGACY + "\nKEEP = {" in _t(LC / "event_table.py")
    assert LEGACY in _t(LC / "ladder_run.py").split('"""')[1]
    md = _t(LC / "ladder_dev.md")
    assert "SUPERSEDED-PREMISE" in md.split("## Verdict")[1].split("\n", 3)[2]
