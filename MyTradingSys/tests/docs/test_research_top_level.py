"""research/ top level stays decluttered (card research-top-level-declutter)."""
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2] / "research"


def test_top_level_under_30_files():
    files = [p.name for p in RESEARCH.iterdir() if p.is_file()]
    assert len(files) < 30, f"{len(files)} loose files in research/: move new reports into a topic folder"
