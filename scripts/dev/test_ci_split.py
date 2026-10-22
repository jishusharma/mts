"""CI speed (operator 2026-10-22, q-ci-speed-fixes; "I want everything to be under 2 minutes"): shards split per file, one CI run per
fast-track commit, green never backwards."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_all_tests as R

CI_YML = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


class ShardTest(unittest.TestCase):
    def plan(self):
        return [R.Step(n, f"d{n}", f"Step {n}", cmd=["true"], skip=("off" if n == "3c" else None))
                for n in ("1", "2", "3", "3b", "3c", "3w", "4", "4b", "4c", "5", "6", "3x")]

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

    def test_eight_shards_split_every_test_file_once_and_no_shard_holds_much_more_than_its_share(self):
        import run_extra_tests
        n, xt, py, mods, ests, maven, k3 = 8, [], [], [], [], [], []
        for k in range(1, n + 1):
            run = [s for s in R.apply_shard(R.build_plan(False), f"{k}/{n}") if not s.skip]
            ests.append(sum(s.est for s in run))
            maven += [k for s in run if s.num == "5"]
            for s in run:
                self.assertNotIn(s.num, ("3xt", "5b", "3k") + R.PYTEST_SHARD_NUMS)   # the long file-list steps are split
                if s.num.startswith("3xt."):
                    xt += s.cmd_text.split("--only ", 1)[1].split()
                elif s.num.startswith("4."):
                    py += [a for a in s.cmd_text.split() if a.startswith("MyTradingSys/tests/")]
                elif s.num.startswith("5b."):
                    mods += s.key.split(",")
                elif s.num.startswith("3k."):
                    k3.append(s.key)
        self.assertEqual(sorted(xt), sorted(run_extra_tests.all_tests()))
        self.assertEqual(sorted(mods), sorted(R.find_layer_modules()))
        whole = [a for s in R.build_plan(False) if s.num in R.PYTEST_SHARD_NUMS for a in s.cmd_text.split() if a.startswith("MyTradingSys/tests/")]
        self.assertEqual(sorted(py), sorted(whole))
        self.assertEqual(maven, [1])   # only shard 1 sets up Java
        self.assertEqual(sorted(k3), sorted(f"{i}/{n}" for i in range(1, n + 1)))   # test_sync.py split, each slice once
        self.assertLess(max(ests), 1.15 * sum(ests) / n)

    def test_ci_prints_the_slowest_step_times_as_one_notice(self):
        R.STEP_SECONDS.clear()
        for num, sec in (("3k", 150.4), ("1", 2.0), ("3xt.6", 80.6)):
            R.format_step(num, "d", "c", True, "", sec)
        self.assertEqual(R.times_notice(2), "::notice title=Gate step times::3k=150s, 3xt.6=81s")

    def test_sync_slices_cover_every_test_once(self):
        import importlib, unittest
        sys.path.insert(0, str(Path(R.__file__).parent))
        suite = unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module("test_sync"))
        def ids(t):
            return [i for x in t for i in (ids(x) if isinstance(x, unittest.TestSuite) else [x.id()])]
        all_ids = ids(suite)
        got = []
        for i in range(3):
            got += all_ids[i::3]
        self.assertEqual(sorted(got), sorted(all_ids))

    def test_file_seconds_are_read_from_pytest_durations_and_extra_lines(self):
        R.FILE_SECONDS.clear()
        R.note_file_seconds("1.50s call     MyTradingSys/tests/test_a.py::T::t1\n0.70s setup    MyTradingSys/tests/test_a.py::T::t2\n"
                            "ok   scripts/dev/test_b.py: 3 passed in 4.10s\n")
        self.assertEqual(R.FILE_SECONDS, {"MyTradingSys/tests/test_a.py": 2.2, "scripts/dev/test_b.py": 4.1})

    def test_windows_estimates_use_runner_numbers(self):
        self.assertEqual(R.shard_est("3sig", win=True), 61)
        self.assertEqual(R.shard_est("3sig", win=False), 20)
        self.assertEqual(R.shard_est("3zz", win=True), R.WIN_FACTOR * R.SHARD_DEFAULT_S)

    def test_ci_runs_per_commit_in_fifteen_shards_with_a_forward_only_green(self):
        text = CI_YML.read_text(encoding="utf-8")
        self.assertIn("group: ci-${{ github.ref }}-${{ github.ref == 'refs/heads/fast-track' && github.sha || 'run' }}", text)
        for k in range(1, 13):
            self.assertIn(f'{{os: windows-latest, shard: "{k}/12"}}', text)
        for k in range(1, 4):
            self.assertIn(f'{{os: ubuntu-latest, shard: "{k}/3"}}', text)
        self.assertIn("run_all_tests.py --shard ${{ matrix.shard }}", text)
        self.assertIn("if: startsWith(matrix.shard, '1/')", text[text.index("actions/setup-java"):][:200] + text[:text.index("actions/setup-java")][-300:])
        mark = text[text.index("\n  mark-green:"):]
        self.assertIn("needs: offline-gate", mark)
        self.assertIn('compare/$old...$SHA', mark)
        self.assertIn("force=false", mark)
        self.assertIn("group: mark-green", mark)
        self.assertNotIn("fetch-depth: 0", mark)


if __name__ == "__main__":
    unittest.main()
