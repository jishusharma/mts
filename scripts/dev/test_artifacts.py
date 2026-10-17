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
        r["pages"][1]["urls"]["jishu.sharma"] = r["pages"][0]["urls"]["jishu.sharma"]
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
        # q21 (2026-10-15; 2026-10-17 Ep6gA5 opens on no login, so EoHi2q is the page): the Inbox page belongs to jishu.sharma; Tom and Fabio has no copy on the other login
        self.assertIn("MTS Control Room <- MyTradingSys/system/artifacts/mts_control_room.html  url=https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su", text)
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
        self.assertIn("NO COPY      MTS Control Room", awgp)  # 2026-10-17: EoHi2q is now the live page on jishu.sharma

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
        self.assertNotIn("https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su", urls)  # 2026-10-17: now the live Control Room, not a copy to delete
        self.assertIn("https://claude.ai/artifact/La75j7gM19pxiQKCpVjJcW", urls)  # 'Moved' stub on jishusharma1985
        self.assertFalse(urls & {p["url"] for p in d["pages"]})
        html = mh.render(d)
        self.assertIn("<title>MTS Home</title>", html)
        self.assertNotIn("</script><", html.split("const DATA = ")[1].split(";\n")[0])

    def test_hub_lists_open_questions_and_where_to_answer(self):
        """Operator 2026-10-17: every question waiting for Jis on MTS Home, with the place to answer it."""
        import tempfile
        import make_home as mh
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "MyTradingSys/system/tasks").mkdir(parents=True)
            (root / mh.DECISIONS).write_text(
                "# OPERATOR DECISIONS\n\n"
                "## q-open | asked 2026-10-15 | Process | NO AUTO-APPLY\n\nRetire old tasks?\n\nRecommended: Yes\nAnswer: (none yet)\n\n"
                "## q-done | asked 2026-10-13 | Process\n\nDone one?\n\nRecommended: Yes\nAnswer: Yes\n\n"
                "## q-json | asked 2026-10-16 | Research\n\nOnly json?\n\n```json\n{\"answer\": \"No\"}\n```\n", encoding="utf-8")
            (root / mh.TASKS / "c1.json").write_text('{"id": "c1", "state": "raw", "asks": "May the monitor clear it?", "title": "Halt"}', encoding="utf-8")
            (root / mh.TASKS / "c2.json").write_text('{"id": "c2", "state": "done", "asks": "Old?", "title": "x"}', encoding="utf-8")
            d = mh.build(self.reg, repo=root)
        self.assertEqual([w["id"] for w in d["waiting"]], ["q-open", "c1"])
        self.assertEqual(d["waiting"][0]["title"], "Retire old tasks?")
        self.assertTrue(d["waiting"][0]["explicit"])
        self.assertEqual(d["answerAt"]["owner"], "jishu.sharma")
        self.assertIn("Waiting for you", mh.render(d))

    def test_hub_explains_failing_links_first(self):
        """Operator 2026-10-17: links to pages owned by another login fail; the reason and fix come before the lists."""
        import make_home as mh
        html = mh.render(mh.build(self.reg))
        self.assertLess(html.index('id="h-how"'), html.index('id="h-wait"'))
        self.assertIn("Link fails? Why, and the one-time fix", html)
        self.assertIn("only after", html)


if __name__ == "__main__":
    unittest.main()
