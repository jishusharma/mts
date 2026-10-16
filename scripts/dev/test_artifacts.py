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
        # home login (2026-10-16): it republishes only its own pages (hub, Research Map, Planner), never a copy of a jishu.sharma page
        self.assertNotIn("REPUBLISH    MTS Control Room", plan)
        self.assertNotIn("REPUBLISH    MTS Layers", plan)
        self.assertIn("REPUBLISH    MTS Research Map", plan)
        awgp = "\n".join(af.plan(self.reg, "jishu.awgp"))
        self.assertIn("REPLACE      MTS Control Room <- MyTradingSys/system/artifacts/cr_moved.html", awgp)

    def test_pages_index_one_link_per_page(self):
        import make_control_room as mc
        rows = mc.page_index()
        self.assertEqual({r["title"] for r in rows}, {"MTS Control Room", "MTS Layers", "Tom and Fabio: what they taught", "CBP Monday Desk",
                                                      "CBP Consensus Desk", "MTS Home", "MTS Research Map", "MTS Session Planner"})
        own = {r["title"]: r["owner"] for r in rows}
        self.assertEqual(own["MTS Control Room"], "jishu.sharma")
        self.assertEqual(own["MTS Research Map"], "jishusharma1985")
        self.assertTrue(all("/artifact/" in r["url"] for r in rows))


class Home(unittest.TestCase):
    """MTS Home (operator 2026-10-16): one hub on the home login; every page says at its top where it lives and where notes go."""

    def setUp(self):
        self.reg = af.load()

    def test_hub_on_home_login(self):
        self.assertEqual(self.reg["home_login"], "jishusharma1985")
        self.assertEqual(af.home_url(self.reg), "https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3")
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "mts_home")["single_owner"] = "jishu.sharma"
        self.assertIn("the hub must be owned by home_login", "\n".join(af.problems(r)))
        r["home_login"] = "nobody"
        self.assertIn("home_login 'nobody' is not an account", "\n".join(af.problems(r)))

    def test_banner_inserted_once_and_refreshed(self):
        page = '<header class="top"><div class="wrap">x</div></header>\n<main class="wrap" id="main"></main>'
        once = af.put_banner(page, self.reg, "research_map")
        self.assertIn(af.home_url(self.reg), once)
        self.assertIn("Owner login: <b>jishusharma1985</b>", once)
        self.assertLess(once.index(af.BANNER_START), once.index('<main class="wrap" id="main">'))
        self.assertGreater(once.index(af.BANNER_START), once.index("</header>"))  # not inside the sticky header
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "research_map")["notes_go_to"] = "NEW PLACE"
        twice = af.put_banner(once, r, "research_map")
        self.assertEqual(twice.count(af.BANNER_START), 1)
        self.assertIn("NEW PLACE", twice)
        cr = af.put_banner('<div class="wrap"><header>', self.reg, "mts_control_room")
        self.assertIn("Owner login: <b>jishu.sharma</b>", cr)
        self.assertEqual(af.put_banner("<p>fragment</p>", self.reg, "mts_control_room", strict=False), "<p>fragment</p>")
        with self.assertRaises(SystemExit):
            af.put_banner("<p>fragment</p>", self.reg, "mts_control_room")

    def test_banner_missing_from_repo_html_caught(self):
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "mts_layer_map")["banner"] = True  # layers_board.html snapshot predates the banner
        p = "\n".join(af.problems(r))
        if af.BANNER_START not in (af.REPO / "MyTradingSys/system/artifacts/layers_board.html").read_text(encoding="utf-8"):
            self.assertIn("mts_layer_map: html has no MTS Home banner", p)

    def test_hub_lists_every_live_page_and_the_copies_to_delete(self):
        import make_home as mh
        d = mh.build(self.reg)
        titles = [p["title"] for p in d["pages"]]
        self.assertEqual(titles[:3], ["MTS Research Map", "MTS Control Room", "MTS Session Planner"])  # where Jis writes, first
        self.assertNotIn("MTS Home", titles)
        urls = {r["url"] for r in d["retire"]}
        self.assertIn("https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su", urls)  # old Control Room copy on jishu.awgp
        self.assertIn("https://claude.ai/artifact/La75j7gM19pxiQKCpVjJcW", urls)  # 'Moved' stub on jishusharma1985
        self.assertFalse(urls & {p["url"] for p in d["pages"]})
        html = mh.render(d)
        self.assertIn("<title>MTS Home</title>", html)
        self.assertNotIn("</script><", html.split("const DATA = ")[1].split(";\n")[0])


if __name__ == "__main__":
    unittest.main()
