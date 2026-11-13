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
        text = "\n".join(af.plan(self.reg, "jishusharma1985"))
        self.assertIn("DELETED      MTS Control Room", text)  # retired and deleted on this login 2026-10-31
        self.assertIn("DELETED      BTC Live Aid", text)  # operator deleted it 2026-11-04
        self.assertIn("DELETED      Simulator Demo by Haiku", text)
        self.assertIn("OPERATOR UNPIN+DELETE  CBP Desk", "\n".join(af.plan(self.reg, "jishu.sharma")))
        # operator 2026-10-17: every page is published from the home login; the Inbox page moved there (MNuodX), Tom and Fabio has no repo html and stays on jishu.sharma
        self.assertIn("NO COPY      Tom and Fabio", "\n".join(af.plan(self.reg, "jishu.awgp")))
        self.assertNotIn("CBP Dashboard", text)
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "mts_layer_map")["status"] = "retire"
        self.assertIn("OPERATOR UNPIN+DELETE  MTS Layers", "\n".join(af.plan(r, "jishusharma1985")))
        self.assertIn("REPUBLISH    MTS Layers", text)
        r = copy.deepcopy(self.reg)
        next(pg for pg in r["pages"] if pg["slug"] == "mts_layer_map")["urls"]["jishusharma1985"] = ""
        self.assertIn("PUBLISH NEW  MTS Layers", "\n".join(af.plan(r, "jishusharma1985")))
        with self.assertRaises(SystemExit):
            af.plan(self.reg, "nobody")

    def test_list_and_plan_take_an_account_without_a_dot(self):
        # jishusharma1985 (2026-10-14) has no "." in its key; list used a.split(".")[1] and raised IndexError.
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            af.cmd_list(self.reg)
        self.assertIn("jishusharma1985=MNuodXmi5RiEihX7rFpqUp", out.getvalue())
        # single live copy (operator 2026-10-17): the home login republishes every page; the old jishu.sharma copies get the pointer page
        plan = "\n".join(af.plan(self.reg, "jishu.sharma"))
        self.assertIn("NO COPY      MTS Research Map", plan)
        self.assertIn("REPLACE      MTS Layers <- MyTradingSys/system/artifacts/cr_moved.html", plan)
        self.assertNotIn("REPUBLISH    MTS Control Room", plan)
        self.assertNotIn("REPUBLISH    MTS Layers", plan)
        self.assertIn("REPUBLISH    MTS Research Map", "\n".join(af.plan(self.reg, "jishusharma1985")))
        awgp = "\n".join(af.plan(self.reg, "jishu.awgp"))
        self.assertIn("NO COPY      MTS Control Room", awgp)  # 2026-10-17: EoHi2q is now the live page on jishu.sharma

    def test_pages_index_one_link_per_page(self):
        import make_control_room as mc
        rows = mc.page_index()
        self.assertEqual({r["title"] for r in rows}, {"MTS Layers", "Tom and Fabio: what they taught", "MTS Home", "MTS Research Map",
                                                      "Test Simulator", "CBP Analyst Desk", "Live feed one page",
                                                      "Tom and Fabio Setup Review", "Buy Crypto",
                                                      "Concept deck: Tom & Fabio", "Concept deck: Malkan RSI", "Conceptualizer"})  # 2026-10-31: Control Room, old CBP desks, Planner, BTC Live Aid retired
        own = {r["title"]: r["owner"] for r in rows}
        self.assertEqual(own["Tom and Fabio: what they taught"], "jishusharma1985")
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
        self.assertIn("Owner login: <b>jishusharma1985</b>", cr)
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
        self.assertEqual(titles[:2], ["MTS Research Map", "MTS Layers"])  # where Jis writes, first
        self.assertNotIn("MTS Home", titles)
        urls = {r["url"] for r in d["retire"]}
        self.assertIn("https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su", urls)  # the jishu.sharma Control Room is an old copy
        self.assertNotIn("https://claude.ai/artifact/MNuodXmi5RiEihX7rFpqUp", urls)  # deleted by the operator 2026-10-31
        self.assertNotIn("https://claude.ai/artifact/BcD1gSuxhvdfYMrxcPBvff", urls)  # BTC Live Aid: deleted by the operator 2026-11-04
        self.assertIn("https://claude.ai/artifact/QwsvsN3LaZKNPvD6zPTTAe", urls)  # jishu.sharma MTS Layers
        self.assertFalse(urls & {p["url"] for p in d["pages"]})
        html = mh.render(d)
        self.assertIn("<title>MTS Home</title>", html)
        self.assertNotIn("</script><", html.split("const DATA = ")[1].split(";\n")[0])

    def test_session_planner_retired_and_listed_for_delete(self):
        """Operator 2026-10-31: planning happens in the sessions; the Planner page leaves Home and waits for his delete."""
        import make_home as mh
        d = mh.build(self.reg)
        self.assertNotIn("session_planner", [p["slug"] for p in d["pages"]])
        self.assertNotIn("https://claude.ai/artifact/2Ti4CGqsFwhWpP1jwmw7UU", [r["url"] for r in d["retire"]])  # he deleted it 2026-10-31

    def test_every_page_opens_on_the_home_login(self):
        """Operator 2026-10-17: 'make a copy of everything from GitHub and publish everything from this account'."""
        import make_home as mh
        d = mh.build(self.reg)
        off = [p["title"] for p in d["pages"] if p["owner"] != self.reg["home_login"]]
        self.assertEqual(off, [])

    def test_hub_is_only_the_page_list_and_stays_compact(self):
        """Operator 2026-11-13: Waiting, Road, session recipes, super prompt and link-fix were removed from Home (stale or duplicated
        elsewhere); what stays is the colour-coded page grid, the old copies fold and the registry note."""
        import make_home as mh
        html = mh.render(mh.build(self.reg))
        self.assertLess(html.index('id="h-pages"'), html.index('id="retirebox"'))
        self.assertIn('<details class="fold" id="retirebox">', html)
        for gone in ("h-wait", "h-road", "h-use", "linkfix", "superbox", "recipes"):
            self.assertNotIn(gone, html)
        self.assertLess(len(html.encode("utf-8")), 15000)

    def test_home_build_is_deterministic_and_tiles_show_absolute_ist_utc_time(self):
        """Operator 2026-11-13: Home must not go stale on its own. Tiles carry the absolute publish time (UTC and IST); colour and age are
        worked out in the page script, so two builds hours apart hash the same."""
        from datetime import datetime, timedelta, timezone
        import make_home as mh
        t0 = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
        a = mh.render(mh.build(self.reg, now=t0))
        b = mh.render(mh.build(self.reg, now=t0 + timedelta(days=9)))
        self.assertEqual(af.content_hash(a), af.content_hash(b))
        d = mh.build(self.reg, now=t0)
        self.assertTrue(all(" UTC · " in p["pub"] and " IST" in p["pub"] for p in d["pages"] if p["pubIso"]))
        self.assertNotIn("health", d["pages"][0])
        self.assertIn("Date.now()", a)

    def test_old_utc_only_stamp_is_rewritten_once_then_kept(self):
        import tempfile
        from datetime import datetime, timezone
        page = "<html><body><main>x</main></body></html>"
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "p.html"
            f.write_text(af.put_stamp(page).replace(" · 21:30 IST", ""), encoding="utf-8")
            old = datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc)
            f.write_text(af.put_stamp(page, old).replace(" · 21:30 IST", ""), encoding="utf-8")
            self.assertTrue(af.write_stamped(f, page))                  # UTC-only stamp: rewritten with IST
            self.assertIn(" IST", f.read_text(encoding="utf-8"))
            self.assertFalse(af.write_stamped(f, page))                 # already two-zone and same content: file kept

    def test_new_pages_are_wired_into_home(self):
        """Operator 2026-10-25: every new development/page must show on MTS Home. A page shows when it is in registry.json."""
        import make_home as mh
        titles = [p["title"] for p in mh.build(self.reg)["pages"]]
        for t in ("Test Simulator", "CBP Analyst Desk", "MTS Layers", "Tom and Fabio Setup Review"):
            self.assertIn(t, titles)
        reg = copy.deepcopy(self.reg)
        extra = copy.deepcopy(next(p for p in reg["pages"] if p["slug"] == "sim_desk"))
        extra.update(slug="zz_new", title="ZZ New Page", urls={"jishusharma1985": "https://claude.ai/artifact/zzzNewPage0000000000000"})
        reg["pages"].append(extra)
        self.assertIn("ZZ New Page", [p["title"] for p in mh.build(reg)["pages"]])

    def test_every_published_artifact_url_in_the_repo_is_registered(self):
        """A claude.ai/artifact link in a tracked doc or script that registry.json does not know is a page MTS Home cannot show."""
        import json
        import re
        import subprocess
        known = set(re.findall(r"claude\.ai/artifact/([A-Za-z0-9]+)", json.dumps(self.reg)))
        files = subprocess.run(["git", "-C", str(af.REPO), "ls-files", "*.md", "*.py", "*.json", "*.txt"],
                               capture_output=True, text=True).stdout.split("\n")
        skip = ("registry.json", "test_artifacts.py", "test_artifacts_audit_links.py")
        loose = {}
        for f in files:
            if not f or f.endswith(skip) or "/tasks/" in f:
                continue
            try:
                text = (af.REPO / f).read_text(encoding="utf-8")
            except (OSError, ValueError):
                continue
            for m in re.findall(r"claude\.ai/artifact/([A-Za-z0-9]{12,})", text):
                if m not in known:
                    loose.setdefault(m, f)
        self.assertEqual(loose, {}, "register these pages in artifacts/registry.json so MTS Home lists them")


class Stale(unittest.TestCase):
    """Staleness check: a page whose repo build differs from published_sha is listed; a rebuild alone (new `generated`) is not."""

    def setUp(self):
        self.reg = copy.deepcopy(af.load())

    def test_hash_ignores_generated_and_commit_only(self):
        a = '{"generated": "2026-10-17 14:19 UTC", "commit": "56a493f3", "x": 1}'
        self.assertEqual(af.content_hash(a), af.content_hash(a.replace("14:19", "15:00").replace("56a493f3", "abcdef01")))
        self.assertNotEqual(af.content_hash(a), af.content_hash(a.replace('"x": 1', '"x": 2')))
        # 2026-10-18: claim ages and minutes move with the clock, and the Control Room embeds registry publish dates;
        # without blanking them every generated page is STALE right after publish-record
        c = '{"age_h": 4.3, "minutes": 22, "pub": "2026-10-17", "x": 1}'
        self.assertEqual(af.content_hash(c), af.content_hash('{"age_h": 4.4, "minutes": 260, "pub": "2026-10-18", "x": 1}'))
        self.assertNotEqual(af.content_hash(c), af.content_hash(c.replace('"x": 1', '"x": 2')))

    def test_stale_lists_exactly_the_differing_pages(self):
        for q in self.reg["pages"]:      # the hash check on its own; feed/max_age_h flags have their own tests
            q.pop("feeds", None), q.pop("max_age_h", None)
        pages = af.tracked(self.reg)
        self.assertGreaterEqual(len(pages), 3)
        built = {pg["slug"]: f"html of {pg['slug']}" for pg in pages}
        for pg in pages:
            pg["published_sha"] = af.content_hash(built[pg["slug"]])
        builder = lambda pg: built[pg["slug"]]
        self.assertEqual(af.stale(self.reg, builder), [])
        built[pages[1]["slug"]] += " changed"
        pages[2]["published_sha"] = None
        got = af.stale(self.reg, builder)
        self.assertEqual([g[0] for g in got], [pages[1]["slug"], pages[2]["slug"]])
        self.assertIn(f"STALE {pages[1]['slug']} https://claude.ai/artifact/", "\n".join(af.stale_lines(self.reg, builder)))

    def test_publish_record_makes_page_fresh(self):
        pg = next(p for p in self.reg["pages"] if p["slug"] == "research_map")
        sha = af.publish_record(self.reg, "research_map", today="2026-10-18")
        self.assertEqual(pg["published_sha"], sha)
        self.assertEqual(pg["last_published"][af.owner(pg)], "2026-10-18")
        self.assertFalse(af.behind(self.reg, pg))
        pg["published_sha"] = "0" * 64
        self.assertTrue(af.behind(self.reg, pg))
        with self.assertRaises(SystemExit):
            af.publish_record(self.reg, "nope")

    def test_publish_record_generator_page_without_repo_html(self):
        pg = next(p for p in self.reg["pages"] if p["slug"] == "sim_desk")
        self.assertIsNone(pg["html"])
        pg["published_sha"] = None
        built = lambda page, repo=af.REPO: "sim desk build"
        orig = af.build_html
        af.build_html = built
        try:
            sha = af.publish_record(self.reg, "sim_desk", today="2026-10-31")
            self.assertEqual(pg["published_sha"], af.content_hash("sim desk build"))
            self.assertEqual(sha, pg["published_sha"])
            self.assertIn(pg, af.tracked(self.reg))
            self.assertEqual([s for s in af.stale(self.reg, built) if s[0] == "sim_desk"], [])
            self.assertFalse(af.behind(self.reg, pg))
        finally:
            af.build_html = orig
        with self.assertRaises(SystemExit):
            af.publish_record(self.reg, "concept_deck_tom_fabio")  # no html, no buildable generator, no feeds

    def test_every_page_has_generator_or_hand_made_mark(self):
        for pg in self.reg["pages"]:
            if pg.get("html") and pg["slug"] in ("research_map", "tom_fabio_deck"):
                self.assertEqual(pg["generator"], "hand-made", pg["slug"])
            self.assertIn("published_sha", pg)

    def test_home_shows_behind_badge_and_published_date(self):
        import make_home as mh
        next(p for p in self.reg["pages"] if p["slug"] == "research_map")["published_sha"] = None
        pages = {p["slug"]: p for p in mh.build(self.reg)["pages"]}
        self.assertTrue(pages["research_map"]["behind"])  # no published_sha yet
        af.publish_record(self.reg, "research_map", today="2026-10-18")
        d = mh.build(self.reg)
        self.assertFalse({p["slug"]: p for p in d["pages"]}["research_map"]["behind"])
        self.assertIn("behind repo", mh.render(d))

    def test_status_reports_pages_stale_line(self):
        import make_status as ms
        n, lines = ms.get_stale_pages()
        self.assertEqual(n, len(lines))


class PagesFollowBuilds(unittest.TestCase):
    """pages-follow-builds-1107: Updated stamp first, publishers list, REPUBLISH lines."""

    def test_put_stamp_goes_first_after_body_and_is_idempotent(self):
        from datetime import datetime, timezone
        page = "<!doctype html><html><body class=x><main>hi</main></body></html>"
        once = af.put_stamp(page, datetime(2026, 11, 7, 15, 4, tzinfo=timezone.utc))
        self.assertIn("Updated 2026-11-07 15:04 UTC", once)
        self.assertTrue(once.index("Updated") < once.index("<main>"))
        twice = af.put_stamp(once, datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc))
        self.assertEqual(twice.count("Updated"), 1)
        self.assertIn("16:00 UTC · 21:30 IST", twice)
        self.assertIn("15:04 UTC · 20:34 IST", once)

    def test_stamp_shows_ist_next_day_date_and_changes_each_minute(self):
        from datetime import datetime, timezone
        late = af.stamp_block(datetime(2026, 11, 13, 20, 0, tzinfo=timezone.utc))
        self.assertIn("2026-11-13 20:00 UTC · 01:30 IST 14 Nov", late)
        self.assertNotEqual(af.stamp_block(datetime(2026, 11, 13, 12, 6, tzinfo=timezone.utc)),
                            af.stamp_block(datetime(2026, 11, 13, 12, 7, tzinfo=timezone.utc)))
        self.assertIn("12:06 UTC · 17:36 IST", af.stamp_block(datetime(2026, 11, 13, 12, 6, tzinfo=timezone.utc)))

    def test_stamp_sits_inside_body_never_before_doctype_and_old_one_moves(self):
        """Regression: a stray control char in the <body regex made every stamp land before <!doctype> (quirks mode)."""
        page = "<!doctype html><html><head><title>t</title></head><body><p>a</p></body></html>"
        once = af.put_stamp(page)
        self.assertTrue(once.startswith("<!doctype"))
        self.assertGreater(once.index("mts-updated"), once.index("<body>"))
        old = af.STAMP_START + "<p>Updated 2026-11-01 00:00 UTC</p>" + af.STAMP_END + page          # the old misplaced stamp
        moved = af.put_stamp(old)
        self.assertTrue(moved.startswith("<!doctype"))
        self.assertEqual(moved.count("mts-stamp:start"), 1)

    def test_stamp_alone_never_makes_a_page_stale(self):
        page = "<html><body><main>x</main></body></html>"
        self.assertEqual(af.content_hash(af.put_stamp(page)), af.content_hash(af.put_stamp(page, None)))
        self.assertNotEqual(af.content_hash(page), af.content_hash(page.replace("x", "y")))
        self.assertEqual(af.content_hash(af.put_stamp(page)), af.content_hash(page))

    def test_generated_pages_carry_the_stamp_first(self):
        import make_home
        import make_layers_board
        for mod in (make_home, make_layers_board):
            with self.subTest(mod.__name__):
                import tempfile
                with tempfile.TemporaryDirectory() as d:
                    out = Path(d) / "p.html"
                    mod.main(["--out", str(out)])
                    t = out.read_text(encoding="utf-8")
                    self.assertIn("Updated 20", t)
                    self.assertLess(t.index("mts-updated"), min(i for i in (t.find("<main"), t.find('<div class="wrap"')) if i >= 0))

    def test_publishers_in_registry_and_login_mapping(self):
        reg = af.load()
        self.assertIn("jishusharma1985", af.publishers(reg))
        self.assertTrue(af.is_publisher(reg, "C"))
        self.assertFalse(af.is_publisher(reg, "A"))
        self.assertFalse(af.is_publisher(reg, ""))
        bad = copy.deepcopy(reg)
        bad["publishers"] = ["nobody"]
        self.assertIn("not an account", chr(10).join(af.problems(bad)))

    def test_republish_lines_format(self):
        reg = af.load()
        for q in reg["pages"]:
            q.pop("feeds", None), q.pop("max_age_h", None)
        pages = af.tracked(reg)
        lines = af.republish_lines(reg, lambda pg: "<html>" + pg["slug"] + "</html>")
        self.assertEqual(len(lines), len(pages))
        for ln in lines:
            kind, slug, src, url = ln.split()
            self.assertEqual(kind, "REPUBLISH")
            self.assertTrue(url.startswith(af.URL_PREFIX))


if __name__ == "__main__":
    unittest.main()


class FeedContentTests(unittest.TestCase):
    """2026-11-13: feed pages go stale on content change, never on mtime alone."""

    def _reg(self, feed):
        pg = {"slug": "p", "title": "P", "status": "canonical", "pinned": True, "generator": "x", "html": None, "single_owner": "acc",
              "urls": {"acc": "https://claude.ai/artifact/AAA"}, "last_published": {"acc": "2026-11-07"}, "published_at": "2026-11-07T10:00:00Z",
              "feeds": [str(feed)]}
        return {"accounts": {"acc": ""}, "pages": [pg]}

    @staticmethod
    def _bump(feed):
        import os, time
        os.utime(feed, (time.time() + 600, time.time() + 600))   # mtime clearly after any publish

    def test_touch_without_byte_change_not_stale(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            feed = Path(d) / "f.json"
            feed.write_text("x", encoding="utf-8")
            reg = self._reg(feed)
            af.publish_record(reg, "p")
            feed.write_text("x", encoding="utf-8")      # new mtime, same bytes
            self._bump(feed)
            self.assertEqual(af.stale(reg), [])

    def test_changed_bytes_is_stale(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            feed = Path(d) / "f.json"
            feed.write_text("x", encoding="utf-8")
            reg = self._reg(feed)
            af.publish_record(reg, "p")
            feed.write_text("y", encoding="utf-8")
            self._bump(feed)
            self.assertEqual([s for s, _u, _w in af.stale(reg)], ["p"])

    def test_publish_record_then_home_registry_feed_not_stale(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            feed = Path(d) / "registry.json"
            reg = self._reg(feed)
            feed.write_text(json.dumps(reg), encoding="utf-8")
            af.publish_record(reg, "p")
            feed.write_text(json.dumps(reg), encoding="utf-8")   # registry rewritten with the record: published_at, feed_hashes
            self._bump(feed)
            self.assertEqual(af.stale(reg), [])
            af.publish_record(reg, "p", now=__import__("datetime").datetime(2026, 11, 14, tzinfo=__import__("datetime").timezone.utc))
            feed.write_text(json.dumps(reg), encoding="utf-8")
            self.assertEqual(af.stale(reg), [])


class FeedStaleTests(unittest.TestCase):
    """2026-11-13 root cause A: a page whose generator is not re-run on fresh data never showed as stale."""

    def _reg(self, tmp, **extra):
        pg = {"slug": "p", "title": "P", "status": "canonical", "pinned": True, "generator": "x", "html": None, "single_owner": "acc",
              "urls": {"acc": "https://claude.ai/artifact/AAA"}, "last_published": {"acc": "2026-11-07"}, "published_at": "2026-11-07T10:00:00Z"}
        pg.update(extra)
        return {"accounts": {"acc": ""}, "pages": [pg]}

    def test_feed_newer_than_publish_is_stale(self):
        import os, tempfile, time
        with tempfile.TemporaryDirectory() as d:
            feed = Path(d) / "board.html"
            feed.write_text("x", encoding="utf-8")
            reg = self._reg(d, feeds=[str(feed)])
            self.assertEqual([s for s, _u, _w in af.stale(reg)], ["p"])            # file is "now", published 11-07
            old = time.time() - 40 * 86400
            os.utime(feed, (old, old))
            self.assertEqual(af.stale(reg), [])                                    # feed older than the publish: current

    def test_glob_feed_and_missing_feed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a1.json").write_text("x", encoding="utf-8")
            self.assertEqual(len(af.stale(self._reg(d, feeds=[str(Path(d) / "a*.json")]))), 1)
            self.assertEqual(af.stale(self._reg(d, feeds=[str(Path(d) / "absent*.json")])), [])    # absent on this machine: skipped

    def test_max_age_h_flags_old_publish(self):
        from datetime import datetime, timezone
        reg = self._reg(".", max_age_h=24)
        now = datetime(2026, 11, 13, tzinfo=timezone.utc)
        self.assertIn("max_age_h", af.stale(reg, now=now)[0][2])
        self.assertEqual(af.stale(reg, now=datetime(2026, 11, 7, 12, tzinfo=timezone.utc)), [])

    def test_publish_record_stores_time_and_clears_stale(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            feed = Path(d) / "f.json"
            feed.write_text("x", encoding="utf-8")
            reg = self._reg(d, feeds=[str(feed)])
            self.assertTrue(af.stale(reg))
            af.publish_record(reg, "p")
            self.assertEqual(af.stale(reg), [])

    def test_republish_line_uses_publish_file_and_producer_lines(self):
        reg = self._reg(".", feeds=[], max_age_h=1, publish_file="F:/x/board.html", producer=["cbp"])
        self.assertEqual(af.republish_lines(reg), ["REPUBLISH p F:/x/board.html https://claude.ai/artifact/AAA"])
        self.assertEqual(af.producer_lines(reg, "cbp"), ["REPUBLISH p F:/x/board.html https://claude.ai/artifact/AAA"])
        self.assertEqual(af.producer_lines(reg, "other"), [])

    def test_real_registry_data_pages_declare_feeds(self):
        reg = af.load()
        by = {p["slug"]: p for p in reg["pages"]}
        for slug in ("cbp_analyst_desk", "buy_crypto", "live_feed_onepage_mock", "research_map"):
            self.assertTrue(by[slug].get("max_age_h"), slug)
        self.assertIn("cbp", by["buy_crypto"]["producer"])


class ShipRecordsTests(unittest.TestCase):
    def test_ship_records_commits_only_registry_then_ships(self):
        calls = []

        class R:
            def __init__(self, rc=0): self.returncode = rc

        def run(cmd, **kw):
            calls.append(cmd)
            return R(1 if "--quiet" in cmd else 0)      # diff --quiet rc 1 = there is a change
        self.assertEqual(af.ship_records(["mts_home"], run=run), 0)
        flat = [" ".join(map(str, c)) for c in calls]
        self.assertTrue(any(" commit " in c and "registry.json" in c for c in flat))
        self.assertIn("sync.py", flat[-1])
        self.assertTrue(flat[-1].endswith("ship"))

    def test_ship_records_noop_when_registry_unchanged(self):
        class R:
            returncode = 0
        calls = []
        self.assertEqual(af.ship_records(["x"], run=lambda c, **k: calls.append(c) or R()), 0)
        self.assertFalse(any("sync.py" in " ".join(map(str, c)) for c in calls))
