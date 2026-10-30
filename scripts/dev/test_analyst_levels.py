"""analyst_levels.py: CBP pointers become a price ladder, and a chart paste shows it (operator 2026-10-30: Michael's
78k/75k and Krown's 76-77k wick sat in CBP before the 10-29 break and no read showed them)."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyst_levels as al
import shot


def row(analyst, pointers, days_ago=1, symbols=("BTC",), vid="v1"):
    d = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {"analyst": analyst, "video_id": vid, "published": d.date().isoformat(), "bias": "BEARISH",
            "symbols": list(symbols), "quotes": ["q"], "trades": [], "pointers": list(pointers), "quote_verified": True,
            "expires_at": (d + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")}


class Parse(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(al.parse_levels("Weakness below ~81k points to 78k, with main support at 75k"), [81000, 78000, 75000])
        self.assertEqual(al.parse_levels("Major support around $75,000"), [75000])
        self.assertEqual(al.parse_levels("expects wick in 76,000-77,000 range"), [76000, 77000])
        self.assertEqual(al.parse_levels("Upside next level 90-92k"), [90000, 92000])
        self.assertEqual(al.parse_levels("a decline to 78 thousand"), [78000])
        self.assertEqual(al.parse_levels("pullback between 77.5k and 78.5k"), [77500, 78500])

    def test_k_on_both_bounds(self):
        self.assertEqual(al.parse_levels("expects a wick into 76k-77k"), [76000, 77000])

    def test_counts_are_not_prices(self):
        self.assertEqual(al.parse_levels("100k liquidations today, then 75k is the level"), [75000])
        self.assertEqual(al.parse_levels("over 120k contracts liquidated near 80k"), [80000])

    def test_noise_dropped(self):
        self.assertEqual(al.parse_levels("13 EMA crossing 34 EMA on the 2-day, September 15th"), [])
        self.assertEqual(al.parse_levels("ETH range 2K to 4.5K"), [])

    def test_ladder_btc_only_sorted_one_per_video(self):
        rows = [row("Michael", ["main support at 75k", "75,000 again", "81k pivot"]),
                row("Habib", ["SOL 180"], symbols=("SOL",), vid="v2")]
        lv = al.ladder(rows)
        self.assertEqual([x["level"] for x in lv], [81000, 75000])
        self.assertEqual({x["analyst"] for x in lv}, {"Michael"})


class Hit(unittest.TestCase):
    def test_publish_day_bars_never_count(self):
        """Only the date is stored: a touch on the publish day may predate the video, so hit starts the next UTC day."""
        day = int(datetime(2026, 10, 29, tzinfo=timezone.utc).timestamp())
        bars = [(day + 3600 * k, 80_500.0, 79_500.0, 80_000.0) for k in range(24)]  # 10-29 only: 79.5k..80.5k
        bars += [(day + 86_400 + 3600 * k, 82_000.0, 81_000.0, 81_500.0) for k in range(24)]  # 10-30: 81k..82k
        lv = [dict(level=80_000.0, published="2026-10-29", expires_at=""), dict(level=81_500.0, published="2026-10-29", expires_at="")]
        al.mark(lv, bars, datetime(2026, 10, 31, tzinfo=timezone.utc))
        self.assertEqual([x["hit"] for x in lv], [False, True])
        self.assertEqual(al.hit_from("2026-10-29"), datetime(2026, 10, 30, tzinfo=timezone.utc))


class Notice(unittest.TestCase):
    def test_chart_paste_shows_analyst_levels(self):
        with tempfile.TemporaryDirectory() as d:
            store = os.path.join(d, "rows.json")
            json.dump({"schema": 1, "rows": [row("Michael", ["main support at 75k"])], "rejected": []}, open(store, "w"))
            real = al.recent_rows
            with mock.patch.object(al, "recent_rows", lambda days, now, store_=None: real(days, now, store)), \
                    mock.patch.object(al, "spot_1h", side_effect=OSError("offline")):
                out = shot.notice([{"id": "abc123", "ext": "png", "w": 10, "h": 10, "route": "paste"}], [])
        self.assertIn("ANALYST LEVELS", out)
        self.assertIn("75,000", out)
        self.assertIn("Michael", out)

    def test_chart_paste_rebuilds_live_aid_analyst_data(self):
        with mock.patch.object(shot, "refresh_live_aid_analysts") as ref, mock.patch.object(al, "hook_block", return_value=""):
            shot.notice([{"id": "abc123", "ext": "png", "w": 10, "h": 10, "route": "paste"}], [])
            shot.notice([], [])
        self.assertEqual(ref.call_count, 1)  # only when a new image landed

    def test_hook_block_never_raises(self):
        with mock.patch.object(al, "recent_rows", side_effect=RuntimeError("bad store")):
            self.assertEqual(al.hook_block(), "")


if __name__ == "__main__":
    unittest.main()
