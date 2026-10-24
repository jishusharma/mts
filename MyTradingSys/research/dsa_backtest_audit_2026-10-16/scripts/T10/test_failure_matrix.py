"""T10 matrix check (stdlib only; CI installs pytest + numpy). Auto-registered: run_extra_tests.discovered() picks up
test_*.py under MyTradingSys/research/."""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEF = HERE.parent.parent / "AUDIT_BRIEF.md"
STATUSES = {"HANDLED", "NOT HANDLED", "N/A", "UNKNOWN"}
REGISTRY_KEYS = 27  # live_runner_cli.build_default_registry, counted in T02 (27 registry keys)


def _read():
    with open(HERE / "matrix.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def _brief_studies():
    text = BRIEF.read_text(encoding="utf-8")
    sect = text.split("### 1b.")[1].split("Testnet (R/overnight")[0]
    return [ln for ln in sect.splitlines() if re.match(r"\| \d+ \|", ln)]


def test_matrix_covers_every_study_and_layer():
    hdr, rows = _read()
    assert len(rows) >= 30, "need 30+ failure modes"
    assert len({r[0] for r in rows}) == len(rows), "duplicate failure-mode ids"
    cols = hdr[7:]
    studies = [c for c in cols if not c.startswith("L ")]
    layers = [c for c in cols if c.startswith("L ")]
    assert len(studies) == len(_brief_studies()) == 16
    assert len(layers) == REGISTRY_KEYS
    for r in rows:
        assert len(r) == len(hdr)
        for cell in r[7:]:
            assert cell.split(" (")[0] in STATUSES, cell
        if not r[5].strip():
            raise AssertionError("failure mode without a source: " + r[0])


def test_handled_cells_name_evidence_and_summary_matches():
    hdr, rows = _read()
    for r in rows:
        for cell in r[7:]:
            if cell.startswith("HANDLED"):
                assert "(" in cell and cell.endswith(")"), "HANDLED without file:line or result: " + cell
    with open(HERE / "matrix_summary.csv", newline="", encoding="utf-8") as f:
        summ = list(csv.reader(f))
    total = [s for s in summ if s[0] == "total"][0]
    assert sum(int(x) for x in total[2:]) == len(rows) * (len(hdr) - 7)
    assert len([s for s in summ if s[0] == "row"]) == len(rows)
    assert len([s for s in summ if s[0] == "column"]) == len(hdr) - 7
