"""ci_deps_lint.py: a gated test file must not hard-depend on a package the CI pip line does not install.

Run: python scripts/dev/test_ci_deps_lint.py   (also collected by run_extra_tests.EXTRA, pytest cwd = this dir)
The fixtures use a made-up package (zzfakepkg), so nothing depends on what the desktop has installed. The last class runs the lint on the
real repo: with today's ci.yml it is clean, with the ci.yml of 1c79da79^ (before pandas was added, the CI-red of 2026-10-16) it names
pandas for the five G5 research tests.
"""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_deps_lint as lint  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CI = "      - name: Install pytest\n        run: python -m pip install pytest numpy tzdata\n"
FAKE = "zzfakepkg"
G5 = [
    "MyTradingSys/research/chart_read_g5_2026-10-16/test_common.py",
    "MyTradingSys/research/mal_bb_mid_engulf_2026-10-16/test_study.py",
    "MyTradingSys/research/opr_bb_mtf_center_2026-10-16/test_study.py",
    "MyTradingSys/research/opr_preopen_tops_2026-10-16/test_study.py",
    "MyTradingSys/research/opr_weekly_low_round_sweep_2026-10-16/test_study.py",
]
# the one pip line of ci.yml before 1c79da79 (pandas added); used when that commit is not in the clone (CI checks out depth 1)
PRE_PANDAS_CI = "      - name: Install pytest\n        run: python -m pip install pytest numpy tzdata\n"


def run_lint(files, ci=CI, entries=None):
    """Write `files` (rel path -> source) into a tmp dir and lint it: [(entry, [chain labels], package)]."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
        found, _, _ = lint.lint(root, ci, files=sorted(files), entries=entries)
        return [(e, [lint.label(c) for c in chain], pkg) for e, chain, pkg in found]


def pkgs(found):
    return sorted({p for _, _, p in found})


class Flagged(unittest.TestCase):
    def test_sibling_module_that_imports_a_fake_package_is_flagged_with_its_chain(self):
        found = run_lint({
            "pkg/test_a.py": "import common\n\ndef test_x():\n    pass\n",
            "pkg/common.py": f"import json\nimport {FAKE}\n",
        })
        self.assertEqual(found, [("pkg/test_a.py", ["test_a.py", "common.py"], FAKE)])
        self.assertEqual(lint.format_violation("pkg/test_a.py", ["pkg/test_a.py", "pkg/common.py"], FAKE),
                         f"pkg/test_a.py -> common.py -> {FAKE}")

    def test_direct_and_from_imports_two_siblings_deep(self):
        found = run_lint({
            "d/test_a.py": "from study import run\n",
            "d/study.py": "import common\n",
            "d/common.py": f"from {FAKE}.sub import thing\n",
        })
        self.assertEqual(found, [("d/test_a.py", ["test_a.py", "study.py", "common.py"], FAKE)])

    def test_sys_path_insert_of_a_parent_dir_is_followed(self):
        # the way chart_lab / study modules find their siblings: Path(__file__).resolve().parents[N] / "a" / "b"
        files = {
            "t/test_a.py": """
                import sys
                from pathlib import Path
                ROOT = Path(__file__).resolve().parents[1]
                sys.path.insert(0, str(ROOT / "lib" / "deep"))
                import helper
            """,
            "lib/deep/helper.py": f"import {FAKE}\n",
            "other/helper.py": "import json\n",     # the same name elsewhere must not be picked
        }
        self.assertEqual(pkgs(run_lint(files)), [FAKE])
        files["t/test_a.py"] = """
            import os, sys
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "other"))
            import helper
        """
        self.assertEqual(run_lint(files), [])   # now the clean helper.py is the one that loads

    def test_relative_and_package_imports_are_followed(self):
        found = run_lint({
            "proj/__init__.py": "",
            "proj/tests/__init__.py": "",
            "proj/tests/test_a.py": "from . import util\nfrom proj import core\n",
            "proj/tests/util.py": "x = 1\n",
            "proj/core.py": f"import {FAKE}\n",
        })
        self.assertEqual(pkgs(found), [FAKE])

    def test_a_conftest_above_the_test_counts(self):
        found = run_lint({"d/conftest.py": f"import {FAKE}\n", "d/test_a.py": "import json\n"})
        self.assertEqual(pkgs(found), [FAKE])

    def test_try_that_does_not_catch_import_errors_is_no_guard(self):
        wrong_error = f"try:\n    import {FAKE}\nexcept ValueError:\n    pass\n"
        reraise = f"try:\n    import {FAKE}\nexcept ImportError:\n    raise\n"
        for src in (wrong_error, reraise):
            self.assertEqual(pkgs(run_lint({"d/test_a.py": src})), [FAKE], src)

    def test_importorskip_after_the_import_is_too_late(self):
        found = run_lint({"d/test_a.py": f"import pytest\nimport common\npytest.importorskip('{FAKE}')\n", "d/common.py": f"import {FAKE}\n"})
        self.assertEqual(pkgs(found), [FAKE])

    def test_if_only_guards_its_own_body(self):
        src = f"import importlib.util\nHAS = importlib.util.find_spec('{FAKE}') is not None\nif HAS:\n    x = 1\nimport {FAKE}\n"
        self.assertEqual(pkgs(run_lint({"d/test_a.py": src})), [FAKE])

    def test_a_package_the_ci_line_lacks_is_flagged_and_one_it_pulls_in_is_not(self):
        files = {"d/test_a.py": "import numpy\nimport dateutil.parser\nimport pandas\n"}
        self.assertEqual(pkgs(run_lint(files)), ["dateutil", "pandas"])               # pytest numpy tzdata
        self.assertEqual(run_lint(files, ci=CI.replace("tzdata", "pandas tzdata")), [])   # pandas brings dateutil


class NotFlagged(unittest.TestCase):
    def test_same_import_behind_importorskip(self):
        files = {
            "d/test_a.py": f"import pytest\npd = pytest.importorskip('{FAKE}')\nimport common\n",
            "d/common.py": f"import {FAKE}\n",
        }
        self.assertEqual(run_lint(files), [])
        files["d/test_a.py"] = f"import pytest\npytest.importorskip('{FAKE}.sub')\nimport {FAKE}\n"
        self.assertEqual(run_lint(files), [])

    def test_same_import_behind_try_except(self):
        files = {
            "d/test_a.py": "try:\n    import common\nexcept ImportError:\n    common = None\n",
            "d/common.py": f"import {FAKE}\n",     # an ImportError inside the sibling is caught by the test's try as well
            "d/test_b.py": f"try:\n    import {FAKE}\nexcept (ImportError, OSError):\n    {FAKE} = None\n",
            "d/test_c.py": f"try:\n    import {FAKE}\nexcept Exception:\n    pass\n",
            "d/test_d.py": f"try:\n    import {FAKE}\nexcept:\n    pass\n",
            "d/test_e.py": f"try:\n    import {FAKE}\nexcept ModuleNotFoundError:\n    pass\n",
        }
        self.assertEqual(run_lint(files), [])

    def test_find_spec_flag_and_availability_flag_guards(self):
        # test_chart_lab (Pillow) and test_fabio_prescreen (cv2) in the real repo
        files = {
            "d/test_a.py": f"""
                import importlib.util
                import pytest
                HAS = importlib.util.find_spec("{FAKE}") is not None
                pytestmark = pytest.mark.skipif(not HAS, reason="x")
                if HAS:
                    from chart import plot
            """,
            "d/chart.py": f"import {FAKE}\n",
            "d/test_b.py": f"""
                import unittest
                try:
                    import {FAKE}
                    HAVE = True
                except ImportError:
                    HAVE = False
                if HAVE:
                    import chart
            """,
            "d/test_c.py": f"""
                import importlib.util
                import pytest
                if importlib.util.find_spec("{FAKE}") is None:
                    pytest.skip("no {FAKE}", allow_module_level=True)
                import {FAKE}
            """,
        }
        self.assertEqual(run_lint(files), [])

    def test_function_level_type_checking_and_main_imports(self):
        found = run_lint({"d/test_a.py": f"""
            from typing import TYPE_CHECKING
            if TYPE_CHECKING:
                import {FAKE}

            def test_x():
                import {FAKE}

            class T:
                def m(self):
                    from {FAKE} import y

            if __name__ == "__main__":
                import {FAKE}
        """})
        self.assertEqual(found, [])

    def test_stdlib_repo_and_ci_packages(self):
        files = {
            "d/test_a.py": "import os, sys, json, collections.abc, zoneinfo\nimport numpy as np\nimport pytest\nimport common\nfrom pkg import mod\nimport tzdata\n",
            "d/common.py": "import pathlib\nfrom . import nothing_here\n",
            "d/pkg/__init__.py": "",
            "d/pkg/mod.py": "import csv\n",
        }
        self.assertEqual(run_lint(files), [])

    def test_removed_stdlib_modules_still_count_as_stdlib(self):
        # CI runs Python 3.12; a 3.13+ desktop no longer lists these in sys.stdlib_module_names
        self.assertEqual(run_lint({"d/test_a.py": "import cgi, telnetlib, imghdr\n"}), [])

    def test_archives_and_b150_skips_are_not_linted(self):
        files = {
            "MyTradingSys/archive/old/test_old.py": f"import {FAKE}\n",
            "Dumps/test_dump.py": f"import {FAKE}\n",
            "scripts/test_skipped.py": f"import {FAKE}\n",
            "scripts/test_kept.py": "import json\n",
            "MyTradingSys/tests/test_gate_discovery_b150.py": "SKIP = {'scripts/test_skipped.py': 'needs the thing'}\n",
        }
        self.assertEqual(run_lint(files), [])

    def test_walk_of_a_directory_that_is_not_a_git_repo(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_a.py").write_text(f"import {FAKE}\n", encoding="utf-8")
            found, _, n = lint.lint(d, CI)
        self.assertEqual((n, [p for _, _, p in found]), (1, [FAKE]))


class CiYmlParse(unittest.TestCase):
    def test_pip_line_variants(self):
        text = ("      - run: echo hello && pip list\n"
                "      - run: python -m pip install -U pytest>=7 'numpy==2.0.*' pandas[performance] tzdata --quiet\n"
                "      - run: pip3 install -r requirements.txt PyYAML  # comment pillow\n")
        self.assertEqual(lint.ci_distributions(text), ["pytest", "numpy", "pandas", "tzdata", "pyyaml"])
        names = lint.ci_import_names(["pyyaml", "pillow", "pandas"])
        self.assertTrue({"yaml", "PIL", "pandas", "dateutil", "numpy"} <= names)

    def test_no_pip_line_fails_closed(self):
        with self.assertRaises(ValueError):
            lint.lint(REPO, "jobs:\n  x:\n    steps: []\n", files=[], entries=[])
        with tempfile.TemporaryDirectory() as d:
            yml = Path(d) / "ci.yml"
            yml.write_text("name: CI\n", encoding="utf-8")
            self.assertEqual(lint.main(["--root", d, "--ci-yml", str(yml)]), 1)
            self.assertEqual(lint.main(["--root", d, "--ci-yml", str(Path(d) / "missing.yml")]), 1)

    def test_main_exit_codes_and_one_line_per_violation(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / lint.CI_YML).write_text(CI, encoding="utf-8")
            (root / "test_a.py").write_text("import common\n", encoding="utf-8")
            (root / "common.py").write_text(f"import {FAKE}\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = lint.main(["--root", d])
            lines = buf.getvalue().splitlines()
            self.assertEqual(rc, 1)
            self.assertEqual(lines[0], f"test_a.py -> common.py -> {FAKE}")
            self.assertTrue(lines[1].startswith("ci_deps_lint: FAIL - 1 hard import"))
            (root / "common.py").write_text("import json\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(lint.main(["--root", d]), 0)
            self.assertIn("ci_deps_lint: OK", buf.getvalue())


class RealRepo(unittest.TestCase):
    """The repo as committed. Parsed once for both ci.yml states."""

    @classmethod
    def setUpClass(cls):
        cls.repo = lint.Repo(REPO)
        cls.entries = [e for e in lint.test_files(cls.repo) if e in G5 or e.endswith("test_chart_lab.py") or e.endswith("test_fabio_prescreen.py")]

    def pre_pandas_ci(self):
        r = subprocess.run(["git", "-C", str(REPO), "show", "1c79da79^:.github/workflows/ci.yml"], capture_output=True, text=True)
        if r.returncode != 0 or "pip install" not in r.stdout:
            return PRE_PANDAS_CI           # shallow clone (CI checks out depth 1): the same pip line as a literal
        self.assertEqual(lint.ci_distributions(r.stdout), lint.ci_distributions(PRE_PANDAS_CI))   # the literal is a faithful copy
        return r.stdout

    def test_todays_ci_yml_covers_every_gated_test_file(self):
        text = (REPO / lint.CI_YML).read_text(encoding="utf-8")
        found, dists, n = lint.lint(REPO, text, repo=self.repo)
        self.assertEqual(found, [])
        self.assertGreater(n, 250)           # the real test set was walked, not an empty list
        self.assertEqual(dists, ["pytest", "numpy", "pandas", "tzdata"])

    def test_ci_yml_before_pandas_names_pandas_for_the_five_g5_tests(self):
        # 1c79da79 added pandas to the pip line after CI went red on exactly these files (ModuleNotFoundError at collection)
        found, dists, _ = lint.lint(REPO, self.pre_pandas_ci(), repo=self.repo)
        self.assertEqual(dists, ["pytest", "numpy", "tzdata"])
        flagged = {(e, p) for e, _, p in found}
        for rel in G5:
            self.assertIn((rel, "pandas"), flagged, rel)
        # and the chain goes through the sibling module, not just the test file itself
        chains = {e: [lint.label(c) for c in chain] for e, chain, p in found if p == "pandas"}
        self.assertIn("common.py", chains[G5[0]])
        self.assertIn("study.py", chains[G5[1]])

    def test_the_known_guarded_cases_stay_guarded_even_with_the_old_line(self):
        found, _, _ = lint.lint(REPO, self.pre_pandas_ci(), repo=self.repo)
        flagged = {e for e, _, _ in found}
        self.assertNotIn("MyTradingSys/research/tom_btc_2026-10-13/test_chart_lab.py", flagged)     # Pillow behind find_spec
        self.assertNotIn("scripts/dev/test_fabio_prescreen.py", flagged)                             # cv2 behind try/except ImportError
        edges = []
        lint.lint(REPO, (REPO / lint.CI_YML).read_text(encoding="utf-8"), repo=self.repo, edges=edges, entries=self.entries)
        self.assertIn(("PIL", "guarded"), {(p, how) for _, _, p, how in edges})
        self.assertIn(("cv2", "guarded"), {(p, how) for _, _, p, how in edges})


if __name__ == "__main__":
    unittest.main()
