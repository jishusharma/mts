"""Unit test for argon_blind_read prompt validation and comparison logic.

Gates:
- Each prompt must require nullable fields {position, entry, stop, target} with null option.
- No prompt may contain claim, reference, or truth values.
- Comparison logic must count numeric outputs for truth-null fields as INVENTED.
- Comparison logic must exclude '?' / unverified references from accuracy denominators.
- Reports must provide only descriptive 7-frame counts, never general catch-rate claims.
"""
import unittest
import sys
from pathlib import Path

# Add scripts/dev to path
sys.path.insert(0, str(Path(__file__).parent))

import argon_blind_read as abr


class TestArgonBlindRead(unittest.TestCase):
    def test_prompt_validation(self):
        """Prompt must include all nullable fields and no injected claims."""
        valid_prompt = abr.build_blind_prompt("frame_01.jpg")
        self.assertIn("position,entry,stop,target", valid_prompt)
        self.assertIn("null", valid_prompt)
        self.assertTrue(abr.validate_prompt(valid_prompt, "frame_01.jpg"))

        # Prompt with injected claim must fail validation
        bad_prompt = valid_prompt + " Claim: stop is 24690."
        self.assertFalse(abr.validate_prompt(bad_prompt, "frame_01.jpg"))

        # Prompt missing null option must fail validation
        bad_prompt2 = "Open image frame_01.jpg. Return {position,entry,stop,target} as numbers."
        self.assertFalse(abr.validate_prompt(bad_prompt2, "frame_01.jpg"))

    def test_comparison_invented_numbers(self):
        """A number for a field our audit marked null counts as INVENTED."""
        truth = {"pos": -1, "entry": 25344, "sl": None, "tp": None}
        # Model returns invented stop and target
        model_out = {"position": -1, "entry": 25344, "stop": 25400, "target": 25200}
        scored = abr.score_fields(model_out, truth)
        self.assertEqual(scored["position"], abr.MATCH)
        self.assertEqual(scored["entry"], abr.MATCH)
        self.assertEqual(scored["stop"], abr.INVENTED)
        self.assertEqual(scored["target"], abr.INVENTED)

    def test_comparison_unverified_exclusion(self):
        """Reference '?' / missing values are UNVERIFIED and excluded from accuracy denominators."""
        truth = {"pos": "?", "entry": 23887, "sl": 23857, "tp": 23962}
        model_out = {"position": 1, "entry": 23887, "stop": 23857, "target": 23962}
        scored = abr.score_fields(model_out, truth)
        self.assertEqual(scored["position"], abr.UNVERIFIED)
        self.assertEqual(scored["entry"], abr.MATCH)
        self.assertEqual(scored["stop"], abr.MATCH)
        self.assertEqual(scored["target"], abr.MATCH)

    def test_descriptive_counts_summary(self):
        """Aggregation must produce descriptive counts, not a general catch-rate."""
        items = [
            {
                "frame": "f1.jpg",
                "truth": {"pos": -3, "entry": 24690, "sl": None, "tp": 24184},
                "parsed": {"position": -3, "entry": 24690, "stop": None, "target": 24184},
            },
            {
                "frame": "f2.jpg",
                "truth": {"pos": -2, "entry": None, "sl": None, "tp": 24184},
                "parsed": {"position": -2, "entry": None, "stop": 24690, "target": 24184},
            },
        ]
        summary = abr.summarize_descriptive_counts(items)
        self.assertIn("matches", summary)
        self.assertIn("mismatches", summary)
        self.assertIn("correct_nulls", summary)
        self.assertIn("missed_nulls", summary)
        self.assertIn("invented_numbers", summary)
        self.assertIn("unverified", summary)
        # Verify invented count for f2 stop 24690 where truth is None
        self.assertEqual(summary["invented_numbers"], 1)
        self.assertEqual(summary["matches"], 5)  # f1 pos, entry, tp (3); f2 pos, tp (2)


# ---- Re-land checks (card argon-fix-defects-and-re-land). Expected numbers are recomputed here
# by hand-written logic from the pilot audit file, not through argon_blind_read.score_fields.
import json

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "MyTradingSys/research/lab_guy/pilots/2026-10-18_gemini_frame_read/hard_results_gemini-3.8-flash-low.json"
RESULTS = REPO / "MyTradingSys/research/layer_lab/argon_blind_read/results_argon-low.json"
REPORT = REPO / "MyTradingSys/research/layer_lab/reports/2026-10-22_argon-blind-read-7-frames.md"
TRIALS = REPO / "MyTradingSys/research/layer_lab/TRIALS.md"
KEYS = (("position", "pos"), ("entry", "entry"), ("stop", "sl"), ("target", "tp"))


def _count(reads, truths):
    c = dict(match=0, mismatch=0, correct_null=0, missed_null=0, invented=0, unverified=0, total=0)
    for rd, tr in zip(reads, truths):
        for mk, tk in KEYS:
            t, m = tr[tk], rd.get(mk)
            c["total"] += 1
            if t == "?":
                c["unverified"] += 1
            elif t is None:
                c["invented" if m is not None else "correct_null"] += 1
            elif m is None:
                c["missed_null"] += 1
            elif abs(float(m) - float(t)) <= 0.5:
                c["match"] += 1
            else:
                c["mismatch"] += 1
    return c


def _seven():
    """(argon_reads, flash_reads, truths) for the 7 audited frames; k0zm = bottom panel."""
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    argon = {}
    for e in res["evaluations"]:
        if "top panel" in e["frame"]:
            continue
        key = "k0zm_1510_1720.png" if e["filename"] == "k0zm_panel_bottom.png" else e["filename"]
        argon[key] = e["argon_parsed"]
    truths, flash, reads = [], [], []
    for it in pilot:
        truths.append(it["truth"])
        b = it["blind"].strip().strip("`").replace("json", "", 1).strip()
        flash.append(json.loads(b))
        reads.append(argon[it["frame"]])
    return reads, flash, truths


class TestArgonReland(unittest.TestCase):
    def test_counts_recomputed(self):
        reads, flash, truths = _seven()
        a, f = _count(reads, truths), _count(flash, truths)
        self.assertEqual((a["total"], a["match"], a["mismatch"], a["correct_null"], a["missed_null"],
                          a["invented"], a["unverified"]), (28, 16, 1, 5, 0, 4, 2))
        self.assertEqual(f["invented"], 4)  # Flash invented 4 as well: Argon is NOT lower
        res = json.loads(RESULTS.read_text(encoding="utf-8"))
        d = res["descriptive_counts_7_frames"]
        self.assertEqual((d["matches"], d["invented_numbers"]), (a["match"], a["invented"]))
        self.assertEqual(res["flash_descriptive_counts_7_frames"]["invented_numbers"], f["invented"])

    def test_report_no_overstatement(self):
        txt = REPORT.read_text(encoding="utf-8")
        self.assertNotIn("down from", txt)
        self.assertNotIn("RESOLVED", txt)
        self.assertNotIn("correctly refrained", txt)
        self.assertIn("**k0zm target (25200 vs 25206)**: CONTESTED", txt)
        self.assertIn("**4** (Flash low: 4", txt)

    def test_reference_base_labelled(self):
        res = json.loads(RESULTS.read_text(encoding="utf-8"))
        self.assertEqual(res["metadata"]["pilot_reference_trust"], "UNVERIFIED")
        tops = [e for e in res["evaluations"] if "top panel" in e["frame"]]
        self.assertEqual(len(tops), 1)
        self.assertEqual(tops[0].get("truth_source"), "UNVERIFIED_LOCAL")
        txt = REPORT.read_text(encoding="utf-8")
        self.assertIn("UNVERIFIED", txt.split("## 2.")[0])
        self.assertIn("top panel", txt.lower())

    def test_trials_row_matches(self):
        rows = [l for l in TRIALS.read_text(encoding="utf-8-sig").splitlines() if "argon-blind-read-7-frames" in l]
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertIn("CONTESTED", r)
        self.assertIn("invented 4", r)
        self.assertIn("matches 16", r)
        self.assertNotIn("25206 target tag vs", r)
        self.assertIn("UNVERIFIED", r)


if __name__ == "__main__":
    unittest.main()
