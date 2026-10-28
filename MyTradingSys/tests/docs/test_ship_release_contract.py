# test_ship_release_contract.py - B4 adoption: boot text must tell sessions to run `sync.py ship --release <slug>`
# (one push) instead of `ship` followed by a separate `release` (an extra commit and push per task).
# Standalone `sync.py release` stays valid for "nothing to ship" (claimed, then no change).
# Run: python -m pytest MyTradingSys/tests/docs/test_ship_release_contract.py -v
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
BOOT_FILES = [
    "CLAUDE.md",
    "MyTradingSys/system/PARALLEL.md",
    "MyTradingSys/system/CODEX_START.md",
    "MyTradingSys/system/TASK_REFINEMENT.md",
    "scripts/sched/relay_prompts/relay_session.md",
]
# `ship` and then a separate `release <slug>` in the same sentence/line = the old two-push close-out
OLD_CLOSE = re.compile(r"sync\.py ship`?,? (?:and then |then )?`?sync\.py release|sync\.py ship, release|ship, release")


def _text(rel):
    return (REPO / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("rel", ["CLAUDE.md", "MyTradingSys/system/PARALLEL.md"])
def test_boot_text_names_ship_release(rel):
    assert "ship --release" in _text(rel), f"{rel} must tell sessions to run `sync.py ship --release <slug>`"


@pytest.mark.parametrize("rel", BOOT_FILES)
def test_no_separate_release_after_ship(rel):
    m = OLD_CLOSE.search(_text(rel))
    assert m is None, f"{rel}: close-out still says ship then a separate release: {m.group(0)!r}"
