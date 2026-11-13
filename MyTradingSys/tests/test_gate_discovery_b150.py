"""B150: every tracked test_*.py is RUN by the gate or opted out with a reason; adding a test file can never fail this.

Run = named in run_all_tests.py, an execution test (step 1 lists it or run_all_tests.execution_stems adds it), under a folder the gate
collects wholesale, or picked up by run_extra_tests.all_tests() (EXTRA + discovered(): every other tracked test, any folder, no entry).
Opt out = a row of scripts/dev/gate_tiers.tsv (retired / study / slow / manual, each with its reason). Archives are ignored.
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import run_all_tests  # noqa: E402
import run_extra_tests  # noqa: E402

COLLECTED_DIRS = ("MyTradingSys/tests/", "MyTradingSys/backtest/", "MyTradingSys/options/tests/", "MyTradingSys/execution/tests/")


def tracked_tests():
    return run_extra_tests.tracked_tests(ROOT)


def is_gated(rel, gate_text, runs, tracked, execution_stems=()):
    """Run by the gate: in `runs` (extra tests), an execution stem, under a collected dir, named by full path in the gate text,
    or its bare stem is named AND no other tracked test shares that stem."""
    if rel in runs or rel.startswith(COLLECTED_DIRS) or rel in gate_text or Path(rel).stem in execution_stems:
        return True
    stem = Path(rel).stem
    if f'"{stem}"' in gate_text or f"{stem}.py" in gate_text:
        return sum(1 for t in tracked if Path(t).stem == stem) == 1
    return False


class GateDiscoveryTest(unittest.TestCase):
    def test_same_stem_in_other_dir_is_not_gated(self):
        gate = 'run("scripts/dev/test_desk.py")  # test_desk.py'
        tracked = ["scripts/dev/test_desk.py", "sim_desk/test_desk.py"]
        self.assertTrue(is_gated("scripts/dev/test_desk.py", gate, set(), tracked))
        self.assertFalse(is_gated("sim_desk/test_desk.py", gate, set(), tracked))
        self.assertTrue(is_gated("a/test_only.py", "x test_only.py", set(), ["a/test_only.py"]))

    def test_every_tracked_test_file_is_run_or_opted_out_with_a_reason(self):
        gate = (ROOT / "scripts" / "dev" / "run_all_tests.py").read_text(encoding="utf-8")
        tracked = tracked_tests()
        runs = set(run_extra_tests.all_tests(ROOT))                        # EXTRA + every discovered test, minus the opt-outs
        step1 = {a for st in run_all_tests.build_plan(False) if str(st.num) == "1" for a in st.cmd}   # the stems step 1 really runs
        stems = {Path(t).stem for t in tracked if Path(t).stem in step1}
        missing = [rel for rel in tracked if rel not in run_extra_tests.OFFGATE and not is_gated(rel, gate, runs, tracked, stems)]
        self.assertEqual(missing, [], "a tracked test no gate step runs and no gate_tiers.tsv row opts out: discovery is broken")
        reasons = [ln.split(chr(9)) for ln in (ROOT / "scripts" / "dev" / "gate_tiers.tsv").read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#")]
        self.assertTrue(reasons and all(len(r) >= 3 and r[2].strip() for r in reasons), "every opt-out row needs a reason")

    def test_extra_list_has_no_dead_entries(self):
        self.assertEqual([p for p in run_extra_tests.EXTRA if not (ROOT / p).exists()], [])


if __name__ == "__main__":
    unittest.main()
