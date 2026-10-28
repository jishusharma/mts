"""Card cryptocred-ledger-feasibility: the feasibility note exists, carries counts and a verdict."""
import re
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "research" / "cryptocred_ledger_2026-10" / "LEDGER_FEASIBILITY.md"


def _text():
    return DOC.read_text(encoding="utf-8")


def test_doc_exists():
    assert DOC.exists()


def test_counts_present():
    t = _text()
    assert re.search(r"^Dated trades/calls found: \d+", t, re.M)
    assert re.search(r"^Undated chart examples: \d+", t, re.M)
    assert re.search(r"^Extracts scanned: 5", t, re.M)


def test_verdict_line_is_one_of_two():
    m = re.search(r"^VERDICT: (SCORABLE|HYPOTHESIS)\s*$", _text(), re.M)
    assert m


def test_hypothesis_when_no_dated_record():
    t = _text()
    n = int(re.search(r"^Dated trades/calls found: (\d+)", t, re.M).group(1))
    v = re.search(r"^VERDICT: (\w+)", t, re.M).group(1)
    assert (v == "SCORABLE") == (n > 0)
