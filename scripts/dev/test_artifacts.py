"""artifacts.py: the real registry is consistent; duplicate urls, bad status and missing files are caught; plan names every action."""
import contextlib
import copy
import io
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
        # q21 (2026-10-15): the Inbox page Ep6gA5 belongs to jishu.sharma; Tom and Fabio has no copy on the other login
        self.assertIn("MTS Control Room <- MyTradingSys/system/artifacts/mts_control_room.html  url=https://claude.ai/artifact/Ep6gA5vskLodMLEseyTnfN", text)
        self.assertIn("NO COPY      Tom and Fabio", "\n".join(af.plan(self.reg, "jishu.awgp")))
        self.assertNotIn("CBP Dashboard", text)
        r = copy.deepcopy(self.reg)
        r["pages"][0]["status"] = "retire"
        self.assertIn("OPERATOR UNPIN+DELETE  MTS Control Room", "\n".join(af.plan(r, "jishu.sharma")))
        self.assertIn("REPUBLISH    MTS Layers", text)
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "mts_layer_map")["urls"]["jishu.sharma"] = ""
        self.assertIn("PUBLISH NEW  MTS Layers", "\n".join(af.plan(r, "jishu.sharma")))
        with self.assertRaises(SystemExit):
            af.plan(self.reg, "nobody")

    def test_list_and_plan_take_an_account_without_a_dot(self):
        # jishusharma1985 (2026-10-14) has no "." in its key; list used a.split(".")[1] and raised IndexError.
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            af.cmd_list(self.reg)
        self.assertIn("jishusharma1985=La75j7gM19pxiQKCpVjJcW", out.getvalue())
        # single live Control Room (operator 2026-10-15): other logins get a pointer page, never a republish of the real one
        plan = "\n".join(af.plan(self.reg, "jishusharma1985"))
        self.assertIn("NO COPY      MTS Control Room", plan)
        self.assertIn("REPLACE      MTS Layers <- MyTradingSys/system/artifacts/cr_moved.html", plan)
        self.assertNotIn("REPUBLISH", plan)
        awgp = "\n".join(af.plan(self.reg, "jishu.awgp"))
        self.assertIn("REPLACE      MTS Control Room <- MyTradingSys/system/artifacts/cr_moved.html", awgp)

    def test_pages_index_one_link_per_page(self):
        import make_control_room as mc
        rows = mc.page_index()
        self.assertEqual({r["title"] for r in rows}, {"MTS Control Room", "MTS Layers", "Tom and Fabio: what they taught", "CBP Monday Desk", "CBP Consensus Desk"})
        self.assertTrue(all(r["owner"] == "jishu.sharma" and "/artifact/" in r["url"] for r in rows))


if __name__ == "__main__":
    unittest.main()
