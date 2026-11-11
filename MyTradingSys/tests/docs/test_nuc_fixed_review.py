"""nuc-fixed-review-workarounds-1101: every REVERT row in NUC_FIXED_REVIEW.md is really gone; KEEP rows are still there."""
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_drift import report_only  # noqa: E402

SYS = Path(__file__).resolve().parents[2] / "system"
ROWS = [[c.strip() for c in l.strip().strip("|").split("|")] for l in (SYS / "NUC_FIXED_REVIEW.md").read_text(encoding="utf-8").splitlines()
        if l.startswith("|") and not l.startswith("|---") and not l.startswith("| Item")]


@report_only


def test_every_row_has_a_decision():
    assert len(ROWS) >= 6
    assert all(r[2].split()[0] in ("KEEP", "REVERT") for r in ROWS)


@report_only


def test_reverted_hang_test_hold_is_gone():
    assert any(r[2] == "REVERT" and "RUNAWAY_GUARD" in r[1] for r in ROWS)
    text = (SYS / "RUNAWAY_GUARD.md").read_text(encoding="utf-8")
    assert "NUC hang test" not in text
    assert "The guard reads, it does not tune." in text


@report_only


def test_kept_items_still_present():
    pol = (SYS / "SCHEDULING_POLICY.md").read_text(encoding="utf-8")
    assert "## 4d." in pol and "## 4c." in pol
    assert "never push there" in (SYS / "NUC_HARVEST.md").read_text(encoding="utf-8")
