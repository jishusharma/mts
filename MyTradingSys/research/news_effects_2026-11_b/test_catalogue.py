"""pytest wrapper: the offline catalogue check must pass; and the checker must catch a corrupted row."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_catalogue as cc  # noqa: E402


def test_catalogue_passes_offline():
    assert cc.errors() == []


def test_checker_catches_bad_rows():
    rows = cc.load()
    bad = [dict(r) for r in rows]
    bad[0]["era"] = "pre" if bad[0]["era"] == "post" else "post"
    bad[1]["time_utc"] = "03:07"
    bad[1]["ts_quality"] = "exact"
    e = cc.errors(rows=bad)
    assert any("era" in x for x in e)
    assert len(cc.errors(rows=rows[:50])) > 0  # too few events
