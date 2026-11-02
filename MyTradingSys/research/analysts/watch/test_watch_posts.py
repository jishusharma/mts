import csv
import io
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MyTradingSys.research.analysts.watch.watch_posts import (
    CSV_HEADER,
    append_rows,
    convert_discord_time_to_utc,
    parse_discord_markdown_table,
    read_existing_ids,
    run_watch,
)


class TestWatchPosts(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.td.name)
        self.log_path = self.temp_dir / "POSTS_LOG.csv"

    def tearDown(self):
        self.td.cleanup()

    def test_csv_header_schema(self):
        expected_header = [
            "seen_utc",
            "post_utc",
            "source",
            "channel",
            "analyst",
            "id_or_url",
            "summary",
        ]
        self.assertEqual(CSV_HEADER, expected_header)

    def test_discord_local_time_to_utc_conversion(self):
        # Discord times in the research corpus are IST (UTC+05:30)
        # 10/16/2026 5:27 PM IST -> 17:27 IST - 5:30 = 11:57 UTC
        utc_ts = convert_discord_time_to_utc("10/16/2026 5:27 PM", tz_offset_hours=5.5)
        self.assertEqual(utc_ts, "2026-10-16T11:57:00Z")

        # 5/28/2026 11:49 PM IST -> 23:49 IST - 5:30 = 18:19 UTC
        utc_ts2 = convert_discord_time_to_utc("5/28/2026 11:49 PM", tz_offset_hours=5.5)
        self.assertEqual(utc_ts2, "2026-05-28T18:19:00Z")

        # Morning timestamp: 10/13/2026 4:36 AM IST -> 04:36 - 5:30 = previous day 23:06 UTC
        utc_ts3 = convert_discord_time_to_utc("10/13/2026 4:36 AM", tz_offset_hours=5.5)
        self.assertEqual(utc_ts3, "2026-10-12T23:06:00Z")

    def test_dedupe_on_id_or_url(self):
        rows1 = [
            {
                "seen_utc": "2026-11-01T20:00:00Z",
                "post_utc": "2026-11-01T18:00:00Z",
                "source": "youtube",
                "channel": "@qriptal",
                "analyst": "Habib",
                "id_or_url": "vid_habib_001",
                "summary": "Bitcoin weekly plan update",
            }
        ]
        added = append_rows(self.log_path, rows1)
        self.assertEqual(added, 1)

        # Existing ids
        existing = read_existing_ids(self.log_path)
        self.assertIn("vid_habib_001", existing)

        # Append same id + new id
        rows2 = [
            {
                "seen_utc": "2026-11-01T20:05:00Z",
                "post_utc": "2026-11-01T18:00:00Z",
                "source": "youtube",
                "channel": "@qriptal",
                "analyst": "Habib",
                "id_or_url": "vid_habib_001",
                "summary": "Duplicate video",
            },
            {
                "seen_utc": "2026-11-01T20:05:00Z",
                "post_utc": "2026-11-01T19:00:00Z",
                "source": "youtube",
                "channel": "@ECKrown",
                "analyst": "Krown",
                "id_or_url": "vid_krown_002",
                "summary": "Daily Bitcoin close",
            },
        ]
        added2 = append_rows(self.log_path, rows2)
        self.assertEqual(added2, 1)  # Only 1 new row added

        with open(self.log_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 3)  # header + 2 unique rows

    def test_exit_3_and_zero_rows_when_yt_block_live(self):
        # When YouTube block is live, run_watch must exit 3 and write ZERO rows
        with patch("MyTradingSys.research.analysts.watch.watch_posts.is_youtube_blocked", return_value=True):
            code = run_watch(log_path=self.log_path)
            self.assertEqual(code, 3)
            self.assertFalse(self.log_path.exists())

    def test_discord_blocked_row_logged_when_access_denied(self):
        # Operator denied computer-use access -> logs DISCORD_BLOCKED row and does not crash
        with patch("MyTradingSys.research.analysts.watch.watch_posts.is_youtube_blocked", return_value=False), \
             patch("MyTradingSys.research.analysts.watch.watch_posts.fetch_youtube_posts", return_value=[]):
            code = run_watch(log_path=self.log_path, request_access_fn=lambda: False)
            self.assertEqual(code, 0)
            self.assertTrue(self.log_path.exists())

            with open(self.log_path, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                self.assertEqual(len(reader), 1)
                self.assertEqual(reader[0]["source"], "discord")
                self.assertEqual(reader[0]["id_or_url"], "DISCORD_BLOCKED")

    def test_parse_staged_youtube_records(self):
        from MyTradingSys.research.analysts.watch.watch_posts import parse_staged_youtube_records
        habib_rows = parse_staged_youtube_records("Habib", limit=2)
        self.assertGreaterEqual(len(habib_rows), 1)
        self.assertEqual(habib_rows[0]["source"], "youtube")
        self.assertEqual(habib_rows[0]["channel"], "@qriptal")
        self.assertEqual(habib_rows[0]["analyst"], "Habib")
        self.assertTrue(habib_rows[0]["id_or_url"].startswith("https://www.youtube.com/watch?v="))

        krown_rows = parse_staged_youtube_records("Krown", limit=2)
        self.assertGreaterEqual(len(krown_rows), 1)
        self.assertEqual(krown_rows[0]["source"], "youtube")
        self.assertEqual(krown_rows[0]["channel"], "@ECKrown")
        self.assertEqual(krown_rows[0]["analyst"], "Krown")

    def test_parse_discord_markdown_table_with_utc_conversion(self):
        md_content = """# Habib trade posts - Qriptal #trading-thoughts
| when (as shown) | side | entry | stop | target | result | imbalance named (tf) | verbatim quote |
|---|---|---|---|---|---|---|---|
| 10/16/2026 5:27 PM | long | | | | | 2 x 1h ("2 1h imbalances") | "we got the trap into NY open" |
| 10/13/2026 4:36 AM | long | | SL 81.5k | "Sunday plan" | | | "took the long with SL at 81.5k" |
"""
        rows = parse_discord_markdown_table(md_content, analyst="Habib", channel="#trading-thoughts")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["post_utc"], "2026-10-16T11:57:00Z")
        self.assertEqual(rows[0]["source"], "discord")
        self.assertEqual(rows[0]["channel"], "#trading-thoughts")
        self.assertEqual(rows[0]["analyst"], "Habib")
        self.assertEqual(rows[1]["post_utc"], "2026-10-12T23:06:00Z")


if __name__ == "__main__":
    unittest.main()
