"""artifacts.py: the real registry is consistent; duplicate urls, bad status and missing files are caught; plan names every action."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifacts as af


class Registry(unittest.TestCase):
    def setUp(self):
        self.reg = af.load()

    def test_real_registry_ok(self):
        self.assertEqual(af.problems(self.reg), [])

    def test_duplicate_url_and_status_caught(self):
        r = copy.deepcopy(self.reg)
        r["pages"][1]["urls"]["jishu.awgp"] = r["pages"][0]["urls"]["jishu.awgp"]
        r["pages"][2]["status"] = "maybe"
        p = "\n".join(af.problems(r))
        self.assertIn("also used by", p)
        self.assertIn("not one of", p)

    def test_missing_html_and_generator_caught(self):
        r = copy.deepcopy(self.reg)
        r["pages"][0]["html"] = "nope/x.html"
        r["pages"][1]["generator"] = "scripts/dev/nope.py"
        p = "\n".join(af.problems(r))
        self.assertIn("html nope/x.html missing", p)
        self.assertIn("generator scripts/dev/nope.py missing", p)

    def test_plan_actions(self):
        text = "\n".join(af.plan(self.reg, "jishu.sharma"))
        self.assertIn("REPUBLISH    MTS Control Room", text)
        self.assertIn("RECORD URL   CBP Desk", text)
        self.assertIn("NO COPY      Tom and Fabio", text)
        self.assertNotIn("CBP Dashboard", text)
        r = copy.deepcopy(self.reg)
        r["pages"][0]["status"] = "retire"
        self.assertIn("OPERATOR UNPIN+DELETE  MTS Control Room", "\n".join(af.plan(r, "jishu.sharma")))
        self.assertIn("PUBLISH NEW  MTS Layer Map", text)
        with self.assertRaises(SystemExit):
            af.plan(self.reg, "nobody")


if __name__ == "__main__":
    unittest.main()
