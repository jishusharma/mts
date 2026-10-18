"""Tests for scripts/dev/lab_query.py (Gemini/lab on-demand queries). Fixture repo with hand-written expectations,
plus checks against the real repo data read independently of lab_query.py."""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOOL = HERE / "lab_query.py"


def run(root, *args):
    p = subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


def git(root, *a, date=None):
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, encoding="utf-8", env=env).stdout.strip()


def put(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


BUGS = """# BUGS AND TASKS

## BUGS

| ID | Opened | Status | Severity | Title | Evidence | Receipt |
|---|---|---|---|---|---|---|
| B001 | 2026-09-13 | CLOSED | LOW | unrelated loop bug | x | doc-only |
| B002 | 2026-09-14 | CLOSED | HIGH | Tom proof sign inverted | SetupCandidatesBuilder.java | fixed abc |
| B003 | 2026-09-15 | OPEN | MED | Fabio ledger drops rows | ledger | |
| B004 | 2026-09-16 | WONTFIX | LOW | tom stop width note | y | no |

## TASKS

| ID | Opened | Status | Severity | Title | Evidence | Receipt |
|---|---|---|---|---|---|---|
| T001 | 2026-09-16 | OPEN | LOW | Tom task row must not appear | z | |
"""


def make_repo():
    root = tempfile.mkdtemp(prefix="lab_query_")
    git(root, "init", "-q")
    sysd = "MyTradingSys/system/"
    put(root, sysd + "layer_index.json", json.dumps({"families": [
        {"id": "tom", "name": "Tom", "status": "tom status", "spec": ["docs/tom_spec.md"], "code": ["src/tom.py"],
         "ledger": [], "results": [], "roadmap": [], "layers": ["tom_core"]},
        {"id": "fabio", "name": "Fabio", "status": "fabio status", "spec": [], "code": ["src/fabio_a.py"],
         "ledger": [], "results": [], "roadmap": [], "layers": ["fabio_a", "fabio_gone"]}]}))
    put(root, sysd + "layer_map.json", json.dumps({"asof": "2026-10-14", "layers": [
        {"id": "tom_core", "family": "Tom", "name": "core", "module": "src/tom.py (proofs)", "status": "STOP", "params": []},
        {"id": "fabio_a", "family": "Fabio", "name": "a", "module": "fabio_a.py; fabio_x*.py", "status": "L1 no edge", "params": []},
        {"id": "fabio_gone", "family": "Fabio", "name": "g", "module": "nothing_here.py", "status": "gone", "params": []}],
        "backtests": [
        {"id": "T-OLD", "title": "old", "date": "2026-09-01", "layers": ["tom_core"], "verdict": "old verdict", "report": "r/old.md", "n": "10"},
        {"id": "T-NEW", "title": "new", "date": "2026-10-09", "layers": ["tom_core"], "verdict": "new verdict", "report": "r/new.md", "n": "20"},
        {"id": "F-ONE", "title": "f", "date": "2026-10-04", "layers": ["fabio_a"], "verdict": "fabio fail", "report": "r/f.md", "n": None},
        {"id": "R-ONE", "title": "r", "date": "2026-10-12", "layers": ["rsi_levels"], "verdict": "rsi", "report": "r/r.md", "n": "5"}]}))
    put(root, "MyTradingSys/research/BUGS.md", BUGS)
    put(root, "MyTradingSys/research/TRIAL_LEDGER.csv",
        "study,variant,run_utc,split,data_source,description,status\n"
        "s1,V1,2026-10-10,DEV,d,x,pre-registered\ns1,V2,2026-10-11,DEV,d,x,pre-registered\n"
        "s2,V1,2026-10-16,DEV,d,x,read\n")
    put(root, "docs/tom_spec.md", "v1\n")
    put(root, "src/tom.py", "a\n")
    put(root, "src/fabio_a.py", "a\n")
    put(root, "other/unrelated.py", "a\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first all", date="2026-09-20T10:00:00")
    put(root, "docs/tom_spec.md", "v2\n")
    git(root, "commit", "-q", "-am", "tom spec v2", date="2026-10-05T10:00:00")
    put(root, "other/unrelated.py", "b\n")
    git(root, "commit", "-q", "-am", "unrelated change", date="2026-10-06T10:00:00")
    put(root, "src/fabio_a.py", "b\n")
    git(root, "commit", "-q", "-am", "fabio a fix", date="2026-10-07T10:00:00")
    return root


class LabQueryFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = make_repo()

    def j(self, *args):
        rc, out, err = run(self.root, *args, "--format", "json")
        self.assertEqual(rc, 0, err)
        return json.loads(out)

    def test_changes_only_family_paths_newest_first(self):
        d = self.j("changes", "tom")
        self.assertEqual([c["subject"] for c in d["commits"]], ["tom spec v2", "first all"])
        self.assertEqual(d["commits"][0]["date"][:10], "2026-10-05")
        self.assertTrue(re.fullmatch(r"[0-9a-f]{7,40}", d["commits"][0]["sha"]))

    def test_changes_limit(self):
        d = self.j("changes", "fabio", "--n", "1")
        self.assertEqual([c["subject"] for c in d["commits"]], ["fabio a fix"])

    def test_rulings_bugs_only_family_match_newest_first(self):
        d = self.j("rulings", "tom")
        self.assertEqual([r["id"] for r in d["rulings"]], ["B004", "B002"])
        self.assertEqual(d["rulings"][1]["status"], "CLOSED")
        self.assertEqual(d["rulings"][1]["severity"], "HIGH")
        self.assertEqual([r["id"] for r in self.j("rulings", "fabio")["rulings"]], ["B003"])

    def test_backtests_family_newest_first_and_trial_audit(self):
        d = self.j("backtests", "tom")
        self.assertEqual([b["id"] for b in d["backtests"]], ["T-NEW", "T-OLD"])
        self.assertEqual(d["backtests"][0]["verdict"], "new verdict")
        self.assertEqual(d["trial_audit"]["rows"], 3)
        self.assertEqual(d["trial_audit"]["by_status"], {"pre-registered": 2, "read": 1})
        self.assertEqual(d["trial_audit"]["latest_run"], "2026-10-16")
        self.assertEqual([b["id"] for b in self.j("backtests", "fabio")["backtests"]], ["F-ONE"])

    def test_layers_status_and_latest_commit(self):
        d = {l["id"]: l for l in self.j("layers")["layers"]}
        self.assertEqual(set(d), {"tom_core", "fabio_a", "fabio_gone"})
        self.assertEqual(d["tom_core"]["status"], "STOP")
        self.assertEqual(d["tom_core"]["family"], "tom")
        self.assertEqual(d["tom_core"]["latest_commit"]["subject"], "first all")
        self.assertEqual(d["fabio_a"]["latest_commit"]["subject"], "fabio a fix")
        self.assertIsNone(d["fabio_gone"]["latest_commit"])

    def test_markdown_output(self):
        rc, out, _ = run(self.root, "backtests", "tom", "--format", "md")
        self.assertEqual(rc, 0)
        self.assertIn("T-NEW", out)
        self.assertIn("new verdict", out)

    def test_unknown_family_fails(self):
        rc, _, err = run(self.root, "changes", "nope")
        self.assertNotEqual(rc, 0)
        self.assertIn("nope", err)


class LabQueryRealRepo(unittest.TestCase):
    def test_backtests_match_layer_map(self):
        m = json.loads((REPO / "MyTradingSys/system/layer_map.json").read_text(encoding="utf-8"))
        idx = json.loads((REPO / "MyTradingSys/system/layer_index.json").read_text(encoding="utf-8"))
        tom = next(f for f in idx["families"] if f["id"] == "tom")["layers"]
        want = [b["id"] for b in sorted(m["backtests"], key=lambda b: b["date"], reverse=True)
                if set(b["layers"]) & set(tom)]
        rc, out, err = run(REPO, "backtests", "tom", "--format", "json")
        self.assertEqual(rc, 0, err)
        got = [b["id"] for b in json.loads(out)["backtests"]]
        self.assertEqual(sorted(got), sorted(want))
        self.assertEqual(got[0], want[0])

    def test_trial_rows_match_csv(self):
        with open(REPO / "MyTradingSys/research/TRIAL_LEDGER.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        rc, out, _ = run(REPO, "backtests", "fabio", "--format", "json")
        self.assertEqual(json.loads(out)["trial_audit"]["rows"], len(rows))

    def test_rulings_match_bugs_md(self):
        text = (REPO / "MyTradingSys/research/BUGS.md").read_text(encoding="utf-8")
        want = {m.group(1) for m in re.finditer(r"^\| (B\d+) \|[^\n]*\bfabio\b", text, re.I | re.M)}
        rc, out, _ = run(REPO, "rulings", "fabio", "--n", "1000", "--format", "json")
        got = {r["id"] for r in json.loads(out)["rulings"]}
        self.assertTrue(want)
        self.assertEqual(got, want)

    def test_layers_cover_layer_map(self):
        m = json.loads((REPO / "MyTradingSys/system/layer_map.json").read_text(encoding="utf-8"))
        rc, out, _ = run(REPO, "layers", "--format", "json")
        self.assertEqual({l["id"] for l in json.loads(out)["layers"]}, {l["id"] for l in m["layers"]})

    def test_tom_spec_latest_commit_matches_git(self):
        rel = "MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md"
        want = git(REPO, "log", "-1", "--format=%h", "--", rel)
        rc, out, _ = run(REPO, "changes", "tom", "--n", "500", "--format", "json")
        self.assertIn(want, [c["sha"][:len(want)] for c in json.loads(out)["commits"]])


if __name__ == "__main__":
    unittest.main()
