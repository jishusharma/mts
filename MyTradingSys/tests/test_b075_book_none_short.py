"""B075 / CORE_READINESS_PLAN.md:127 last sentence: proof_direction treats book_imbalance None as unknown (aligned),
for long (already covered in test_book_imbalance_nodata.py) and the short mirror. Expected status from the plan wording, not from code."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from test_book_imbalance_nodata import _run  # noqa: E402


def test_short_book_none_is_aligned():
    status, details = _run("short", None)
    assert status == "aligned", (status, details)
    assert not any("book_imbalance" in d for d in details), details


def test_long_book_none_is_aligned():
    status, details = _run("long", None)
    assert status == "aligned", (status, details)
