import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "where_is.py")
REPO = os.path.dirname(os.path.dirname(HERE))


def w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run(root, *args):
    env = dict(os.environ, WHERE_IS_LOCAL=os.path.join(root, "none.jsonl"))
    return subprocess.run([sys.executable, SCRIPT, *args, "--root", root], capture_output=True, text=True, env=env)


class T(unittest.TestCase):
    def test_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            w(t, "MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv",
              "video_id,channel,language,method,transcript_file,extract_file,extract_source,quotes,quotes_verified,used_by\n"
              "W1HrDl70Lhk,Tom,en,captions,x.txt,MyTradingSys/research/e/ex.md,m,3,PASS,none\n"
              "ZZZ,Fabio,,,,,,,,none\n")
            w(t, "MyTradingSys/research/e/ex.md", "x")
            w(t, "MyTradingSys/research/wiring_audit_2026-10/WIRING_X.csv",
              "trader,rule_id,rule,quote,quote_file_line,rule_file_line,source,code_file_line,param,test,verdict,extent\n"
              "Tom,TOM-001,Trigger,q,a,b,s,src/gone.java:1,p,t,wired,full\n")
            w(t, "MyTradingSys/system/layer_index.json", json.dumps({"families": []}))
            self.assertEqual(run(t, "build").returncode, 0)
            r = run(t, "w1hrdl70lhk")
            self.assertEqual(r.returncode, 0)
            self.assertIn("MyTradingSys/research/e/ex.md", r.stdout)
            self.assertIn("method=captions", r.stdout)
            self.assertIn("ZZZ", run(t, "ZZZ").stdout)  # unextracted video still has a row
            self.assertIn("TOM-001", run(t, "TOM-001").stdout)
            self.assertNotIn("gone.java", run(t, "TOM-001").stdout)  # missing path never listed
            r = run(t, "nosuchtopic")
            self.assertEqual(r.returncode, 1)
            self.assertIn("not indexed", r.stdout)


class Real(unittest.TestCase):
    def test_every_ledger_video_and_rule_has_a_row(self):
        idx = open(os.path.join(REPO, "MyTradingSys/system/WHERE_IS.md"), encoding="utf-8").read()
        led = csv.DictReader(open(os.path.join(REPO, "MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv"), encoding="utf-8"))
        for r in led:
            self.assertIn("| " + r["video_id"], idx)
        for f in ("WIRING_MALKAN_KROWN.csv", "WIRING_TOM_FABIO_HABIB.csv"):
            for r in csv.DictReader(open(os.path.join(REPO, "MyTradingSys/research/wiring_audit_2026-10", f), encoding="utf-8")):
                if r.get("rule_id"):
                    self.assertIn("| " + r["rule_id"], idx)


if __name__ == "__main__":
    unittest.main()
