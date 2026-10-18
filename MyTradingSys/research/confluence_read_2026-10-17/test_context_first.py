"""CONTEXT_FIRST.md must cite a file or NOT_IN_DATA in every context row and carry no outcome statistics."""
import os
import re

DOC = os.path.join(os.path.dirname(__file__), "CONTEXT_FIRST.md")


def _text():
    with open(DOC, encoding="utf-8") as fh:
        return fh.read()


def _section(text, head):
    m = re.search(r"^## " + re.escape(head) + r".*?(?=^## |\Z)", text, re.S | re.M)
    assert m, head
    return m.group(0)


def test_every_context_row_cites_source_or_not_in_data():
    lines = _section(_text(), "1. Context sheet").splitlines()
    rows = [l for l in lines if l.startswith("| ") and not l.startswith("| Field")]
    assert len(rows) >= 15
    for l in rows:
        src = [c.strip() for c in l.strip().strip("|").split("|")][-1]
        assert re.search(r"\b(OF|OI1|OI5|CMS|HTF)\b", src) or "NOT_IN_DATA" in l or src == "-", l


def test_no_outcome_statistics():
    t = _text().lower()
    for bad in ("win rate", "hit rate", "expectancy", "profit factor", "sharpe", "mean gross"):
        assert bad not in t, bad


def test_no_private_log_detail():
    assert not re.search(r"Downloads|account id", _text())
