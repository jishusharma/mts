"""INDICATOR_MAP.md structure test (card indicator-map-1108): every engine directory under backtest/layers/ has a row, every
row path exists, required sections present, and no 'X confirms Y' rule sentence appears outside quotes."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "MyTradingSys" / "system" / "INDICATOR_MAP.md"
LAYERS = ROOT / "MyTradingSys" / "backtest" / "layers"
SECTIONS = ["## 1. Dimension table", "## 1b. Engine inventory", "## 2. Role table", "## 3. Connected sets", "## 4. Gaps",
            "## 5. Mechanism"]


def text():
    return MAP.read_text(encoding="utf-8")


def engine_dirs():
    return sorted(d.name for d in LAYERS.iterdir()
                  if d.is_dir() and d.name != "__pycache__" and any(d.glob("*.py")))


def inventory_rows():
    body = text().split("## 1b. Engine inventory", 1)[1].split("\n## 2.", 1)[0]
    return [ln for ln in body.splitlines() if ln.startswith("| `MyTradingSys/")]


class TestIndicatorMap(unittest.TestCase):
    def test_map_exists_with_sections(self):
        self.assertTrue(MAP.exists(), "INDICATOR_MAP.md missing")
        t = text()
        for s in SECTIONS:
            self.assertIn(s, t)

    def test_every_engine_has_a_row(self):
        rows = "\n".join(inventory_rows())
        for name in engine_dirs():
            self.assertIn(f"`MyTradingSys/backtest/layers/{name}/`", rows, f"engine {name} has no row")

    def test_every_row_path_exists(self):
        rows = inventory_rows()
        self.assertTrue(rows)
        for ln in rows:
            path = re.match(r"\| `([^`]+)`", ln).group(1)
            self.assertTrue((ROOT / path).exists(), f"row path missing: {path}")

    def test_every_backticked_path_in_map_exists(self):
        for p in re.findall(r"`(MyTradingSys/[^`\s]+)`", text()):
            if "{" in p or "*" in p:
                continue
            self.assertTrue((ROOT / p).exists(), f"path in map does not exist: {p}")

    def test_no_unmapped_confirmation_claim(self):
        t = re.sub(r'"[^"]*"', "", text())
        self.assertNotRegex(t, r"(?i)\bconfirms\b")


if __name__ == "__main__":
    unittest.main()
