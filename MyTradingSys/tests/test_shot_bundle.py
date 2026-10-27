"""Tests for shot.py bundle subcommand (RU3 Eagle_Eyes evidence packet).
Verifies:
- Stored multi-chart set yields a single comprehensive evidence packet (classification,
  engine snapshot, previous read, open mismatches, mirror age).
- Extract stub with MATCH/MISMATCH lines is generated.
- Stale mirror (>60 min or lag >60 min) is flagged and not used as live data.
- Prior read and open mismatches are correctly linked or defaulted.
"""
import base64
import contextlib
import datetime as dt
import io
import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
SCRIPTS_DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(SCRIPTS_DEV))
import shot
import live_mirror

SID = "22222222-bbbb-cccc-dddd-333333333333"


def png(seed, w=1920, h=1080):
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h) + seed.encode() * 4


class ShotBundleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_shot_bundle_"))
        self.store = self.tmp / "store"
        self.engine_dir = self.tmp / "engine"
        self.mirror_dir = self.tmp / "mirror"
        self.home = self.tmp / "claude"
        self.temp = self.tmp / "temp"

        self.store.mkdir(parents=True)
        self.engine_dir.mkdir(parents=True)
        self.mirror_dir.mkdir(parents=True)

        env = {
            "MTS_SHOT_DIR": str(self.store),
            "MTS_SHOT_ENGINE_DIR": str(self.engine_dir),
            "MTS_CLAUDE_HOME": str(self.home),
            "MTS_SHOT_TEMP": str(self.temp),
            "MTS_SHOT_SLUGS": "SLUG",
        }
        self.patcher = mock.patch.dict(os.environ, env)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def state(self):
        return shot.fold(shot.load_events(self.store))

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = shot.main(list(argv))
        return rc, out.getvalue(), err.getvalue()

    def make_chart_shot(self, seed, tf, at, symbol="BTCUSDT", why="15m chart of BTC pullback"):
        data = png(seed)
        shot_id = shot.land(self.store, data, "paste", SID, at, "t", why)["id"]
        shot.classify(self.store, shot_id, "chart", why, symbol=symbol, tf=tf, at=at, tz="+00:00", source="binance")
        return shot_id

    def test_bundle_stored_multichart_set(self):
        # 1. Setup multi-chart set
        s1 = self.make_chart_shot("s1", "5m", "2026-10-18T10:00:00Z", why="5m chart pullback")
        s2 = self.make_chart_shot("s2", "15m", "2026-10-18T10:02:00Z", why="15m chart HTF bounce")

        # 2. Setup an engine snapshot for s1
        engine_file = self.engine_dir / f"{s1}.json"
        engine_file.write_text(json.dumps({
            "shot": s1,
            "symbol": "BTCUSDT",
            "at": "2026-10-18T10:00:00Z",
            "snapshot": {
                "price": 68500.0,
                "day_vwap": 68200.0,
                "net_delta": 450.0,
                "poc": 68400.0,
            }
        }), encoding="utf-8")

        p_shot = self.make_chart_shot("p0", "1h", "2026-10-18T09:30:00Z", why="1h prior context")
        prior_extract = self.tmp / "prior_extract.md"
        prior_extract.write_text(
            f"# Prior Extract\nPrior: none\n| {p_shot} | MATCH | cvd positive | cvd matches |\n"
            "Invalidation: outside 67000-69000\n",
            encoding="utf-8"
        )
        shot.read_extract(self.store, [p_shot], str(prior_extract))

        # 4. Setup an open mismatch in another shot
        m_shot = self.make_chart_shot("m0", "5m", "2026-10-18T09:00:00Z", why="5m divergence mismatch")
        m_extract = self.tmp / "mismatch_extract.md"
        m_extract.write_text(
            f"# Mismatch Extract\nPrior: none\n| {m_shot} | MISMATCH | delta divergence | delta negative |\n",
            encoding="utf-8"
        )
        shot.read_extract(self.store, [m_shot], str(m_extract))
        # Note: m_shot is NOT done, so it has an open mismatch

        # 5. Setup fresh live mirror (published 5 min ago)
        now_dt = dt.datetime.now(dt.timezone.utc)
        mirror_root = self.tmp / "repo_root"
        mirror_dest = mirror_root / live_mirror.MIRROR_DIR
        mirror_dest.mkdir(parents=True)
        manifest = {
            "schema": 1,
            "host": "JIS-NB",
            "utc": (now_dt - dt.timedelta(minutes=5)).isoformat(),
            "version": "v20261018T100000Z",
            "git_head": "abcdef12",
            "redacted_lines": 0,
            "flags": {"HALT": False, "AUTO_PAUSE": False},
            "files": []
        }
        (mirror_dest / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        sets = shot.make_sets(self.state())
        target_set = next(s for s in sets if s1 in s["ids"])
        set_id = target_set["set"]

        with mock.patch("shot.REPO", mirror_root):
            rc, out, err = self.run_main("bundle", set_id)

        self.assertEqual(rc, 0, f"Error: {err}")
        # Check classification info
        self.assertIn(f"SET {set_id}", out)
        self.assertIn("BTCUSDT", out)
        self.assertIn("5m", out)
        self.assertIn("15m", out)
        self.assertIn(s1[:8], out)
        self.assertIn(s2[:8], out)

        # Check engine snapshot
        self.assertIn("68500", out)
        self.assertIn("68200", out)

        # Check previous read
        self.assertIn(prior_extract.name, out)

        # Check open mismatches
        self.assertIn(m_shot[:8], out)
        self.assertIn("MISMATCH", out)

        # Check mirror status (fresh)
        self.assertIn("mirror@", out)
        self.assertIn("OK", out)

        # Check extract stub with MATCH / MISMATCH rows
        self.assertIn("| id | class | chart claim | data check |", out)
        self.assertIn(f"| {s1} | MATCH |", out)
        self.assertIn(f"| {s1} | MISMATCH |", out)

    def test_bundle_flags_stale_mirror_and_does_not_use_it(self):
        s1 = self.make_chart_shot("s1", "5m", "2026-10-18T10:00:00Z", why="5m chart pullback")
        s2 = self.make_chart_shot("s2", "15m", "2026-10-18T10:02:00Z", why="15m chart HTF bounce")

        # Stale mirror: published 120 minutes ago
        now_dt = dt.datetime.now(dt.timezone.utc)
        mirror_root = self.tmp / "repo_root"
        mirror_dest = mirror_root / live_mirror.MIRROR_DIR
        mirror_dest.mkdir(parents=True)
        manifest = {
            "schema": 1,
            "host": "JIS-NB",
            "utc": (now_dt - dt.timedelta(minutes=120)).isoformat(),
            "version": "v20261018T100000Z",
            "git_head": "abcdef12",
            "redacted_lines": 0,
            "flags": {"HALT": False, "AUTO_PAUSE": False},
            "files": []
        }
        (mirror_dest / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        sets = shot.make_sets(self.state())
        set_id = sets[0]["set"]

        with mock.patch("shot.REPO", mirror_root):
            rc, out, err = self.run_main("bundle", set_id)

        self.assertEqual(rc, 0, f"Error: {err}")
        # Must flag stale mirror
        self.assertIn("STALE", out)
        self.assertIn("do NOT present these numbers as live", out)
        # Stale mirror is flagged, not used as live data in extract stub
        self.assertNotIn("LIVE_MIRROR_USED", out)

    def test_bundle_unknown_set_refused(self):
        rc, out, err = self.run_main("bundle", "deadbeef")
        self.assertEqual(rc, 2)
        self.assertIn("not found", err)

    def test_bundle_json_mode_and_shot_id_lookup(self):
        s1 = self.make_chart_shot("s1", "5m", "2026-10-18T10:00:00Z", why="5m chart pullback")
        s2 = self.make_chart_shot("s2", "15m", "2026-10-18T10:02:00Z", why="15m chart HTF bounce")

        # Query using the second shot id rather than the set id prefix
        rc, out, err = self.run_main("bundle", s2, "--json")
        self.assertEqual(rc, 0, f"Error: {err}")
        data = json.loads(out)
        self.assertEqual(data["set"]["symbol"], "BTCUSDT")
        self.assertIn(s1, data["set"]["ids"])
        self.assertIn(s2, data["set"]["ids"])
        self.assertIsNone(data["previous_read"]["extract"])
        self.assertEqual(data["open_mismatches"], [])


if __name__ == "__main__":
    unittest.main()
