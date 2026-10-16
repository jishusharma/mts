"""Tests for scripts/dev/trace.py on a temporary fixture repo (read-only study trace)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACE = HERE / "trace.py"


def run_trace(root, arg):
    p = subprocess.run([sys.executable, str(TRACE), "--root", str(root), arg],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


def git(root, *a):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                   check=True, capture_output=True)


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def card(root, cid, **kw):
    d = {"id": cid, "title": cid + " title", "state": "ready", "lane": "SONNET", "depends_on": [], "refs": [],
         "layers": [], "goal": "", "done_when": "", "steps": [], "scope_in": []}
    d.update(kw)
    put(root / "MyTradingSys/system/tasks" / (cid + ".json"), json.dumps(d))


def make_repo():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    git(root, "init", "-q")
    res = root / "MyTradingSys/research"
    put(res / "alpha_2026-10-01/REPORT.md", "report\n")
    put(res / "alpha_2026-10-01/PRE_REGISTRATION.md", "prereg\n")
    put(res / "lonely_2026-10-02/NOTES.md", "n\n")
    put(res / "VERDICTS.csv",
        "study_dir,family,arm,split_read,n,gross_mean_pct,se_pct,cost_pct,verdict,kill_scope,one_run,commit,date\n"
        "alpha_2026-10-01,Alpha family,(study),DEV,10,0.1,0.05,0.2,FAIL,UNPARSED,no,abc1234,2026-10-03\n"
        "ghost_2026-09-01,Ghost family,(study),DEV,1,0,0,0,PASS,UNPARSED,no,def5678,2026-09-02\n")
    card(root, "alpha-study", state="done", layers=["tom"], goal="run research/alpha_2026-10-01 study")
    card(root, "alpha-followup", depends_on=["alpha-study"], title="follow up on alpha")
    card(root, "alpha-ref", refs=["alpha-study"], title="refers to alpha")
    card(root, "unrelated")
    sysd = root / "MyTradingSys/system"
    put(sysd / "LAYERS.md", "## Tom (`tom`)\n- results: MyTradingSys/research/alpha_2026-10-01/REPORT.md\n")
    put(sysd / "layer_index.json", json.dumps({"families": [{"id": "tom", "name": "Tom"}]}))
    put(sysd / "claims/alpha-rerun.md",
        "task: rerun alpha_2026-10-01\nhost: H\naccount: a\narea: MyTradingSys/research/alpha_2026-10-01\nepoch: 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "alpha study commit")
    return tmp, root


class TraceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.root = make_repo()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_study_with_everything(self):
        rc, out = run_trace(self.root, "alpha_2026-10-01")
        self.assertEqual(rc, 0)
        for needle in ("alpha-study", "state=done", "lane=SONNET", "alpha-followup", "alpha-ref",
                       "Alpha family", "FAIL", "REPORT.md", "PRE_REGISTRATION.md", "alpha study commit",
                       "alpha-rerun", "(`tom`)"):
            self.assertIn(needle, out)
        self.assertNotIn("unrelated", out)

    def test_study_with_no_card(self):
        rc, out = run_trace(self.root, "lonely_2026-10-02")
        self.assertEqual(rc, 0)
        self.assertIn("NOTES.md", out)
        self.assertIn("cards: none", out)
        self.assertIn("verdicts: none", out)
        self.assertIn("claim: none", out)

    def test_study_with_verdict_row_only(self):
        rc, out = run_trace(self.root, "ghost_2026-09-01")
        self.assertEqual(rc, 0)
        self.assertIn("Ghost family", out)
        self.assertIn("files: none", out)
        self.assertIn("cards: none", out)

    def test_card_id(self):
        rc, out = run_trace(self.root, "alpha-study")
        self.assertEqual(rc, 0)
        self.assertIn("alpha_2026-10-01", out)
        self.assertIn("Alpha family", out)
        self.assertIn("alpha-followup", out)

    def test_layer_id(self):
        rc, out = run_trace(self.root, "tom")
        self.assertEqual(rc, 0)
        self.assertIn("alpha-study", out)

    def test_unknown_exits_zero(self):
        rc, out = run_trace(self.root, "nothing-here")
        self.assertEqual(rc, 0)
        self.assertIn("none", out)


if __name__ == "__main__":
    unittest.main()
