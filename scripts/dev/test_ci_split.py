"""CI speed (operator 2026-10-22, q-ci-speed-fixes): Windows leg split in shards, one CI run per fast-track commit, green never backwards."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all_tests as R

CI_YML = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


class ShardTest(unittest.TestCase):
    def plan(self):
        return [R.Step(n, f"d{n}", f"Step {n}", cmd=["true"], skip=("off" if n == "3c" else None))
                for n in ("1", "2", "3", "3b", "3c", "3k", "4", "4b", "4c", "5", "6", "3x")]

    def test_every_step_runs_in_exactly_one_shard(self):
        ran = []
        for k in (1, 2, 3):
            ran += [s.num for s in R.apply_shard(self.plan(), f"{k}/3") if not s.skip]
        want = [s.num for s in self.plan() if not s.skip]
        self.assertEqual(sorted(ran), sorted(want))
        self.assertEqual(len(ran), len(set(ran)))

    def test_split_is_balanced_and_one_shard_is_everything(self):
        loads = [sum(R.shard_est(s.num) for s in R.apply_shard(self.plan(), f"{k}/3") if not s.skip) for k in (1, 2, 3)]
        self.assertLess(max(loads), 0.6 * sum(loads))
        self.assertEqual([s.num for s in R.apply_shard(self.plan(), "1/1") if not s.skip], [s.num for s in self.plan() if not s.skip])
        with self.assertRaises(ValueError):
            R.apply_shard(self.plan(), "4/3")

    def test_ci_runs_per_commit_with_three_windows_shards_and_a_forward_only_green(self):
        text = CI_YML.read_text(encoding="utf-8")
        self.assertIn("group: ci-${{ github.ref }}-${{ github.ref == 'refs/heads/fast-track' && github.sha || 'run' }}", text)
        for k in (1, 2, 3):
            self.assertIn(f'{{os: windows-latest, shard: "{k}/3"}}', text)
        self.assertIn("run_all_tests.py --shard ${{ matrix.shard }}", text)
        mark = text[text.index("\n  mark-green:"):]
        self.assertIn("needs: offline-gate", mark)
        self.assertIn("merge-base --is-ancestor", mark)
        self.assertIn("--force-with-lease", mark)
        self.assertIn("group: mark-green", mark)


if __name__ == "__main__":
    unittest.main()
