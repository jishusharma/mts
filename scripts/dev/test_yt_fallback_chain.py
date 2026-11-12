"""YouTube caption block never stops work (operator 2026-11-12): path 4 switch, waiting list, CBP pacing. Network mocked."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "MyTradingSys"))
import fetch_captions_timed as f  # noqa: E402
import yt_transcript_sites as sites  # noqa: E402
import cbp_run  # noqa: E402

VID = "abcdefghijk"
VTT = ("WEBVTT\nKind: captions\nLanguage: en\n\n00:00:00.000 --> 00:00:02.000\nhello there bitcoin\n\n"
       "00:00:02.000 --> 00:00:04.000\nfloor at sixty thousand\n")


def fake_site(url):
    if "/captions/" in url:
        return 200, VTT
    if "/videos/" in url:
        return 200, json.dumps({"title": "T", "author": "Chan", "published": 1794422160, "lengthSeconds": 4})
    return 404, ""


class Base(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.td = Path(td.name)
        env = mock.patch.dict(os.environ, {"YT_BLOCK_FILE": str(self.td / "yt_block.json"), "YT_PROXY": "off",
                                           "YT_WAITING_FILE": str(self.td / "yt_waiting.json"), "YT_SITE_INSTANCES": "site.test"})
        env.start()
        self.addCleanup(env.stop)
        for name, kw in (("public_ip", {"return_value": "203.0.113.7"}), ("fleet_rows", {"return_value": []}),
                         ("fleet_send", {"return_value": True})):
            p = mock.patch.object(f, name, **kw)
            p.start()
            self.addCleanup(p.stop)
        s = mock.patch.object(f.time, "sleep")
        s.start()
        self.addCleanup(s.stop)
        canon = mock.patch.object(f, "CANON", self.td)
        canon.start()
        self.addCleanup(canon.stop)

    def main(self, *args, site=fake_site, fetch=None):
        with mock.patch.object(sites, "http_get", side_effect=site) as h, mock.patch.object(f, "yt_dlp", mock.Mock()), \
                mock.patch.object(f, "fetch", side_effect=fetch or (lambda *a, **k: "OK auto 5w")) as m, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = f.main(["--analyst", "K", "--out", str(self.td), *args])
        return code, m, h, out.getvalue()


class PathSwitch(Base):
    def test_429_goes_on_to_the_site_path_by_itself(self):
        code, m, h, out = self.main(VID, fetch=lambda *a, **k: "BLOCKED")
        self.assertEqual(code, 0)
        head = (self.td / f"{VID}_timed.txt").read_text(encoding="utf-8")
        self.assertIn("# Source: public transcript site site.test", head)
        self.assertIn("# Word count: 7", head)
        self.assertIn("hello there bitcoin floor at sixty thousand", (self.td / f"{VID}_raw.txt").read_text(encoding="utf-8"))
        self.assertTrue(f.blocked_until())   # the lock itself is still recorded
        self.assertEqual(m.call_count, 1)    # and YouTube was asked exactly once

    def test_locked_address_makes_no_youtube_request_and_still_gets_the_video(self):
        f.mark_blocked()
        code, m, h, out = self.main(VID)
        self.assertEqual((code, m.call_count), (0, 0))
        self.assertTrue((self.td / f"{VID}_timed.txt").exists())
        self.assertTrue(all(c.args[0].startswith("https://site.test/") for c in h.call_args_list))

    def test_site_request_is_generic(self):
        import urllib.request
        seen = {}

        class R:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"{}"

        def fake_open(req, timeout=None, context=None):
            seen["h"] = dict(req.header_items())
            return R()
        with mock.patch.object(urllib.request, "urlopen", fake_open):
            sites.http_get("https://site.test/api/v1/captions/x")
        self.assertEqual(set(k.lower() for k in seen["h"]), {"user-agent", "accept"})


class WaitingList(Base):
    def test_unfetchable_video_is_listed_with_paths_tried(self):
        f.mark_blocked()
        code, m, h, out = self.main(VID, site=lambda url: (0, ""))
        self.assertEqual(code, f.EXIT_BLOCKED)
        rows = json.loads((self.td / "yt_waiting.json").read_text(encoding="utf-8"))
        self.assertEqual([r["id"] for r in rows], [VID])
        self.assertIn("ytdlp:locked", rows[0]["paths_tried"])
        self.assertTrue(rows[0]["time"])
        with contextlib.redirect_stdout(io.StringIO()) as o:
            self.assertEqual(f.main(["--waiting"]), 0)
        self.assertIn(VID, o.getvalue())

    def test_later_success_clears_the_entry(self):
        sites.add_waiting(VID, "@c", ["ytdlp:locked"])
        f.mark_blocked()
        self.main(VID)
        self.assertEqual(sites.read_waiting(), [])


class Pacing(Base):
    ANS = [{"short": n, "channel": "@" + n, "enabled": True} for n in "ABCDE"]

    def run_fetch_new(self, recent_values, rc=0):
        cmds, pauses = [], []
        seq = iter(recent_values)
        last = [0]

        def recent():
            last[0] = next(seq, last[0])
            return last[0]

        def run(cmd, check=False):
            cmds.append(cmd)
            return mock.Mock(returncode=rc)
        with mock.patch.object(cbp_run, "analysts", return_value=({"exclude_regex": "x", "include_regex": "y"}, self.ANS)), \
                mock.patch.object(cbp_run, "catch_up", return_value=[]) as cu, \
                contextlib.redirect_stdout(io.StringIO()):
            inc = cbp_run.fetch_new("2026-11-01", None, run=run, sleep=pauses.append, recent=recent)
        return cmds, pauses, inc, cu

    def test_pause_between_analysts_and_video_cap(self):
        cmds, pauses, inc, cu = self.run_fetch_new([0] * 20)
        self.assertEqual(len(cmds), 5)
        self.assertEqual(pauses, [cbp_run.ANALYST_PAUSE_S] * 4)
        for c in cmds:
            self.assertEqual(c[c.index("--max-videos") + 1], str(cbp_run.MAX_VIDEOS_PER_ANALYST))

    def test_hourly_cap_stops_new_analysts_and_sends_them_to_path_4(self):
        cmds, pauses, inc, cu = self.run_fetch_new([0, 0, cbp_run.HOURLY_REQUEST_CAP] + [cbp_run.HOURLY_REQUEST_CAP] * 20)
        self.assertEqual(len(cmds), 2)
        self.assertEqual(inc, ["C", "D", "E"])
        self.assertEqual(cu.call_count, 3)

    def test_unfinished_fetch_goes_to_path_4_but_the_lock_exit_does_not(self):
        _, _, _, cu = self.run_fetch_new([0] * 20, rc=1)
        self.assertEqual(cu.call_count, 5)
        _, _, _, cu = self.run_fetch_new([0] * 20, rc=f.EXIT_BLOCKED)
        self.assertEqual(cu.call_count, 0)   # the fetcher already did path 4 itself on exit 3

    def test_requests_last_hour_counts_only_the_last_hour(self):
        from datetime import datetime, timedelta, timezone
        now = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)
        iso = lambda m: (now - timedelta(minutes=m)).isoformat(timespec="seconds")
        (self.td / "yt_block.json").write_text(json.dumps({"req": {"a": [iso(5), iso(59), iso(61)], "b": [iso(10), iso(600)]}}))
        self.assertEqual(cbp_run.requests_last_hour(now), 3)


if __name__ == "__main__":
    unittest.main()
