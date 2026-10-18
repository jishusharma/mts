import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Repo root and scripts/dev
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import artifacts as af


class TestArtifactsAuditLinks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fixture_dead_link_and_newer_repo_copy_both_show(self):
        """Done when: A fixture registry with one dead link and one newer repo copy shows both in the table."""
        # Page 1: has a dead link and matching published_sha
        p1_file = self.root / "page1.md"
        p1_file.write_text("# Page 1\n\n[Good Link](good.md)\n[Dead Link](missing.md)\n", encoding="utf-8")
        good_file = self.root / "good.md"
        good_file.write_text("# Good\n", encoding="utf-8")

        p1_sha = af.content_hash(p1_file.read_text(encoding="utf-8"))

        # Page 2: has a newer repo copy (published_sha does not match disk content)
        p2_file = self.root / "page2.md"
        p2_file.write_text("# Page 2 content on disk\n", encoding="utf-8")
        p2_sha = "0" * 64  # older / different published_sha

        fixture_reg = {
            "accounts": {"owner1": "Login 1"},
            "home_login": "owner1",
            "home_slug": "page1",
            "pages": [
                {
                    "slug": "page1",
                    "title": "Page 1",
                    "status": "canonical",
                    "pinned": True,
                    "html": "page1.md",
                    "single_owner": "owner1",
                    "urls": {"owner1": "https://claude.ai/artifact/p1url"},
                    "last_published": {"owner1": "2026-10-18"},
                    "published_sha": p1_sha,
                    "purpose": "p1",
                    "notes_go_to": "p1",
                    "refresh": "daily",
                    "owner_app": "app",
                },
                {
                    "slug": "page2",
                    "title": "Page 2",
                    "status": "canonical",
                    "pinned": False,
                    "html": "page2.md",
                    "single_owner": "owner1",
                    "urls": {"owner1": "https://claude.ai/artifact/p2url"},
                    "last_published": {"owner1": "2026-10-17"},
                    "published_sha": p2_sha,
                    "purpose": "p2",
                    "notes_go_to": "p2",
                    "refresh": "daily",
                    "owner_app": "app",
                },
            ],
        }

        # Run audit_links
        rows = af.audit_links(fixture_reg, repo=self.root)
        statuses = {r.status for r in rows}
        self.assertIn("BROKEN", statuses)
        self.assertIn("NEWER_REPO_COPY", statuses)

        # Check dead link row
        dead_rows = [r for r in rows if r.status == "BROKEN"]
        self.assertEqual(len(dead_rows), 1)
        self.assertEqual(dead_rows[0].page, "page1")
        self.assertIn("missing.md", dead_rows[0].target)

        # Check newer repo copy row
        newer_rows = [r for r in rows if r.status == "NEWER_REPO_COPY"]
        self.assertEqual(len(newer_rows), 1)
        self.assertEqual(newer_rows[0].page, "page2")

        # Table formatting includes PAGE, LINK, TARGET, STATUS headers and both items
        table = af.format_audit_table(rows)
        self.assertIn("PAGE", table)
        self.assertIn("LINK", table)
        self.assertIn("TARGET", table)
        self.assertIn("STATUS", table)
        self.assertIn("BROKEN", table)
        self.assertIn("NEWER_REPO_COPY", table)
        self.assertIn("missing.md", table)
        self.assertIn("page2", table)

    def test_injectable_reader_and_fetcher(self):
        """Reader and fetcher can be injected without reading real disk files."""
        fixture_reg = {
            "accounts": {"owner1": "Login 1"},
            "home_login": "owner1",
            "home_slug": "page_test",
            "pages": [
                {
                    "slug": "page_test",
                    "title": "Page Test",
                    "status": "canonical",
                    "pinned": True,
                    "html": "virtual/page.html",
                    "single_owner": "owner1",
                    "urls": {"owner1": "https://claude.ai/artifact/testurl"},
                    "last_published": {"owner1": "2026-10-18"},
                    "published_sha": "match_sha",
                    "purpose": "p",
                    "notes_go_to": "p",
                    "refresh": "daily",
                    "owner_app": "app",
                }
            ],
        }

        # Virtual filesystem in memory
        virtual_content = (
            "# Test Page\n\n"
            "[Doc 1](rel/doc1.md)\n"
            "[Doc 2](rel/doc2.md)\n"
            "[External](https://example.com/api)\n"
        )
        fixture_reg["pages"][0]["published_sha"] = af.content_hash(virtual_content)

        virtual_files = {
            "virtual/page.html": virtual_content,
            "virtual/rel/doc1.md": "# Doc 1 content",
            # doc2 is missing
        }

        def mock_reader(path):
            norm = str(path).replace("\\", "/")
            for k, v in virtual_files.items():
                if norm.endswith(k) or norm == k:
                    return v
            raise FileNotFoundError(f"Missing {path}")

        fetched_urls = []

        def mock_fetcher(url):
            fetched_urls.append(url)
            if "example.com" in url:
                return True
            return False

        rows = af.audit_links(fixture_reg, reader=mock_reader, fetcher=mock_fetcher)
        row_map = {r.target: r.status for r in rows}

        self.assertEqual(row_map.get("rel/doc1.md"), "OK")
        self.assertEqual(row_map.get("rel/doc2.md"), "BROKEN")
        self.assertEqual(row_map.get("https://example.com/api"), "OK")
        self.assertIn("https://example.com/api", fetched_urls)

    def test_cmd_audit_links_cli(self):
        """CLI invocation of cmd_audit_links prints table to stdout."""
        fixture_reg = {
            "accounts": {"owner1": "Login 1"},
            "home_login": "owner1",
            "home_slug": "page_cli",
            "pages": [
                {
                    "slug": "page_cli",
                    "title": "Page CLI",
                    "status": "canonical",
                    "pinned": True,
                    "html": "page_cli.html",
                    "single_owner": "owner1",
                    "urls": {"owner1": "https://claude.ai/artifact/cliurl"},
                    "last_published": {"owner1": "2026-10-18"},
                    "published_sha": "diff_sha",
                    "purpose": "p",
                    "notes_go_to": "p",
                    "refresh": "daily",
                    "owner_app": "app",
                }
            ],
        }
        (self.root / "page_cli.html").write_text("[Broken Target](bad.html)", encoding="utf-8")

        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            ret = af.cmd_audit_links(fixture_reg, repo=self.root)

        self.assertEqual(ret, 0)
        output = buf.getvalue()
        self.assertIn("PAGE", output)
        self.assertIn("LINK", output)
        self.assertIn("TARGET", output)
        self.assertIn("STATUS", output)
        self.assertIn("NEWER_REPO_COPY", output)
        self.assertIn("BROKEN", output)


if __name__ == "__main__":
    unittest.main()
