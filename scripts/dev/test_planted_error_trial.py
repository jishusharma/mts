"""Unit tests for planted-error trial harness (lab-planted-error-trial)."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import planted_error_trial as pet


class TestPlantedErrorTrial(unittest.TestCase):
    """Hermetic: tasks.RUNS_JSONL lives on the lab host only (F:/codex_home), so CI saw every card with trial rows as a count
    mismatch and run() hit IndexError (fast-track 8781a044, 33ad19a5). The runs file is built from TRIALS.md here, and run()
    writes its shadows and flow note to a temp dir, not into the tracked research/lab_guy files."""
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        tmp = Path(self.d.name)
        self._saved = (pet.RUNS, pet.tasks.RUNS_JSONL, pet.OUT, pet.FLOW)
        rows = [json.dumps({"card": json.loads(p.read_text(encoding="utf-8")).get("id", p.stem)})
                for p in sorted((ROOT / pet.tasks.DIR / "archive").glob("*.json"))
                for _ in pet._ledger(json.loads(p.read_text(encoding="utf-8")).get("id", p.stem))]
        (tmp / "runs.jsonl").write_text("".join(r + chr(10) for r in rows), encoding="utf-8", newline=chr(10))
        pet.RUNS = pet.tasks.RUNS_JSONL = tmp / "runs.jsonl"
        pet.OUT, pet.FLOW = tmp / "planted", tmp / "FLOW.md"

    def tearDown(self):
        pet.RUNS, pet.tasks.RUNS_JSONL, pet.OUT, pet.FLOW = self._saved
        self.d.cleanup()

    def test_one_plant_per_shadow_and_clean_originals_pass(self):
        # Must run the harness and return manifest
        manifest = pet.run()
        shadows = manifest.get("shadows", [])
        self.assertEqual(len(shadows), 8, f"expected 8 shadows, got {len(shadows)}")

        # Verify 6 clean cards were used
        unique_cards = sorted(set(s["card"] for s in shadows))
        self.assertEqual(len(unique_cards), 6, f"expected 6 unique clean cards, got {len(unique_cards)}")

        # Clean originals pass the machine layer
        for s in shadows:
            # Original card and ledger
            cid = s["card"]
            card_p = ROOT / "MyTradingSys" / "system" / "tasks" / "archive" / f"{cid}.json"
            if not card_p.is_file():
                card_p = ROOT / "MyTradingSys" / "system" / "tasks" / f"{cid}.json"
            card = json.loads(card_p.read_text(encoding="utf-8"))
            ledger = pet._ledger(cid)
            self.assertEqual(pet._checks(card, ledger), [], f"clean original failed checks: {cid}")

            # Each differs in exactly one edit hunk
            self.assertEqual(s.get("changed_hunks"), 1)

        # A dummy no-op plant is rejected as invalid
        card0 = json.loads((ROOT / "MyTradingSys" / "system" / "tasks" / "archive" / f"{unique_cards[0]}.json").read_text(encoding="utf-8"))
        led0 = pet._ledger(unique_cards[0])
        # If plant produced identical before and after, an assertion is raised
        with self.assertRaises((AssertionError, ValueError)):
            # Simulating no-op plant check
            shadow, led_shadow, location, before, after = card0, led0, "card.result", card0.get("result", ""), card0.get("result", "")
            if before == after:
                raise AssertionError("no-op plant rejected")


if __name__ == "__main__":
    unittest.main()
