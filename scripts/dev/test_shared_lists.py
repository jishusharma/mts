"""Shared-list consistency checks CI runs and the ship gate must too (ci-parity-1113): sub-second, run as must-pass 3xm on the merged tree."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TSV = REPO / "scripts" / "dev" / "extra_tests.tsv"


def test_every_extra_tests_tsv_row_names_an_existing_file():
    # a merge revert brought a dead row back and trunk CI went red at the extra-tests step (4.2)
    rows = [ln.strip() for ln in TSV.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    dead = [p for p in rows if not (REPO / p).exists()]
    assert not dead, "scripts/dev/extra_tests.tsv: delete the dead row(s) (file missing): " + ", ".join(dead)
