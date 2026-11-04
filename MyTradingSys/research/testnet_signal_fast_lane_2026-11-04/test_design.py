"""Design-card test: DESIGN.md exists and carries the four named sections."""
from pathlib import Path

DESIGN = Path(__file__).with_name("DESIGN.md")
SECTIONS = ("## 1. Host runner", "## 2. What is drawn", "## 3. Same-day steps", "## 4. Stays gated")


def test_design_has_four_sections():
    assert DESIGN.exists(), "DESIGN.md missing"
    text = DESIGN.read_text(encoding="utf-8")
    for s in SECTIONS:
        assert s in text, s
