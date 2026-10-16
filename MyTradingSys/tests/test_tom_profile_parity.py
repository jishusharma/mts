"""Paper fixture for the engine profile, FORMULAS.md 18.1 value-area expansion."""
import json
import os
import shutil
from pathlib import Path
import tempfile
import unittest

from MyTradingSys.backtest.tom_profile_parity import (
    EngineProfile, select_bars, main, profile_shape_fraction, profile_shape_matches,
)


def has_java_profile_dependencies():
    m2 = Path(os.environ.get("MTS_M2") or Path.home() / ".m2/repository")
    versions = [set(p.parent.name for p in m2.glob("com/fasterxml/jackson/core/jackson-"+k+"/*/jackson-"+k+"-*.jar")) for k in ("databind","core","annotations")]
    return shutil.which("java") and shutil.which("javac") and set.intersection(*versions)


class ProfileParityTest(unittest.TestCase):
    def test_basis_free_profile_shape_fraction(self):
        drawn = profile_shape_fraction(25100, 25400, 25220)
        computed = profile_shape_fraction(24870, 25170, 24990)
        mismatch = profile_shape_fraction(24870, 25170, 25050)
        self.assertAlmostEqual(drawn, 0.40)
        self.assertAlmostEqual(computed, 0.40)
        self.assertTrue(profile_shape_matches(drawn, computed, 0.033))
        self.assertAlmostEqual(mismatch, 0.60)
        self.assertFalse(profile_shape_matches(drawn, mismatch, 0.033))

    @unittest.skipUnless(has_java_profile_dependencies(), "Java and coherent Jackson Maven cache required for engine integration")
    def test_hand_computed_minute_profile(self):
        # EXPECT: point masses at 100,101,102,103,150 have volume 1,2,10,4,3.
        # Range=50, engine minimum 50 bins => width=1. Total=20, 70%=14.
        # POC=102 (10); add upper 103 (4) rather than lower 101 (2).
        # FORMULAS 18.1 edge convention (d8efebc2): POC = bin centre 102.5, VAH = top edge of bin 103 = 104, VAL = bottom edge of bin 102 = 102.
        rows = [[i*60000, p,p,p,p,v] for i,(p,v) in
                enumerate(zip([100,101,102,103,150],[1,2,10,4,3]))]
        with EngineProfile() as engine:
            levels = engine.profile(rows)
        self.assertEqual(levels, {"poc":102.5,"vah":104.0,"val":102.0})

    def test_explicit_window_excludes_forming_and_future_bars(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/"klines").mkdir()
            (root/"klines"/"GER40-1m-1970-01.csv").write_text(
                "0,100,100,100,100,1\n60000,102,102,102,102,2\n120000,999,999,999,999,9\n",
                encoding="utf-8", newline="\n")
            self.assertEqual([r[0] for r in select_bars(root,60000,120000)], [60000])
            self.assertRaises(ValueError, select_bars, root,120000,60000)

    @unittest.skipUnless(has_java_profile_dependencies(), "Java and coherent Jackson Maven cache required for engine integration")
    def test_cli_output_records_window_and_engine_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"klines").mkdir()
            (root/"klines"/"GER40-1m-1970-01.csv").write_text(
                "0,100,100,100,100,1\n60000,101,101,101,101,2\n120000,102,102,102,102,10\n180000,103,103,103,103,4\n240000,150,150,150,150,3\n",
                encoding="utf-8",newline="\n")
            out=root/"result.json"
            main(["--raw",str(root),"--start","1970-01-01T00:00:00Z",
                  "--at","1970-01-01T00:05:00Z","--out",str(out)])
            result=json.loads(out.read_text())
            self.assertEqual(result["bar_count"],5)
            self.assertEqual(result["levels"],{"poc":102.5,"vah":104.0,"val":102.0})
            self.assertEqual(len(result["engine_sha256"]),64)
            self.assertEqual(result["as_of_utc"],"1970-01-01T00:05:00Z")

if __name__ == "__main__":
    unittest.main()
