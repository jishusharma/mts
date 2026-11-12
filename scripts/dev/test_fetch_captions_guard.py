"""YouTube guard in fetch_captions_timed / fetch_captions: budget cap, first-429 block record, blocked run, --status. Offline."""
import os
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as f  # noqa: E402

IDS = [f"{c}" * 11 for c in "abcdefg"]   # 7 distinct 11-char ids


class T(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.rec = pathlib.Path(self.td.name) / "yt_block.json"
        p = mock.patch.dict(os.environ, {"YT_BLOCK_FILE": str(self.rec), "YT_PROXY": "off"})
        p.start()
        self.addCleanup(p.stop)
        ip = mock.patch.object(f, "public_ip", return_value="203.0.113.7")   # no real ipify request
        ip.start()
        self.addCleanup(ip.stop)
        # no real mts-signals fleet: a live ytblock row from another box would block this IP (fleet_rows/fleet_send mocked)
        fr = mock.patch.object(f, "fleet_rows", return_value=[])
        fr.start()
        self.addCleanup(fr.stop)
        fs = mock.patch.object(f, "fleet_send", return_value=True)
        fs.start()
        self.addCleanup(fs.stop)
        s = mock.patch.object(f.time, "sleep")
        self.sleep = s.start()
        self.addCleanup(s.stop)

    def run_main(self, ids, fetch_effect, extra=()):
        with mock.patch.object(f, "yt_dlp", mock.Mock()), mock.patch.object(f, "fetch", side_effect=fetch_effect) as m:
            code = f.main(["--analyst", "K", "--out", self.td.name, *extra, *ids])
        return code, m

    def test_budget_cap_defers_sixth_video(self):
        code, m = self.run_main(IDS[:6], lambda *a, **k: "OK auto 5w")
        self.assertEqual(m.call_count, 5)
        self.assertEqual([c.args[0] for c in m.call_args_list], IDS[:5])
        self.assertEqual(code, 1)   # deferred counts as not done
        self.assertFalse(f.blocked_until())

    def test_first_429_writes_record_and_stops(self):
        code, m = self.run_main(IDS[:4], ["OK auto 5w", "BLOCKED", "OK auto 5w", "OK auto 5w"])
        self.assertEqual(m.call_count, 2)   # no call after the block
        self.assertIsNotNone(f.blocked_until())
        rec = f.read_block()
        self.assertTrue(rec["host"])
        self.assertEqual(code, 1)

    def test_blocked_record_means_zero_calls(self):
        f.mark_blocked()
        code, m = self.run_main(IDS[:2], lambda *a, **k: "OK auto 5w")
        self.assertEqual(m.call_count, 0)
        self.assertEqual(code, f.EXIT_BLOCKED)

    def test_block_message_names_next_path(self):   # a block ends the scripted path, never the task (YT_PROXY.md path order)
        import contextlib
        import io
        want = "next path: Browser 2 transcript panel, see YT_PROXY.md"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.run_main(IDS[:2], ["BLOCKED", "OK auto 5w"])      # a fresh 429 in this run
        self.assertTrue(buf.getvalue().rstrip().endswith(want), buf.getvalue())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code, m = self.run_main(IDS[:2], lambda *a, **k: "OK auto 5w")   # now locked: exit 3, no request
        self.assertEqual((code, m.call_count), (f.EXIT_BLOCKED, 0))
        self.assertTrue(buf.getvalue().rstrip().endswith(want), buf.getvalue())

    def test_status_zero_calls(self):
        f.mark_blocked()
        with mock.patch.object(f, "yt_dlp", mock.Mock()) as y, mock.patch.object(f, "fetch") as m, \
                mock.patch.object(f, "list_channel") as lc:
            self.assertEqual(f.main(["--analyst", "K", "--status"]), 0)
            self.assertEqual(f.main(["--analyst", "K", "--status", "--channel", "@x"]), 0)
        self.assertEqual((m.call_count, lc.call_count, len(y.mock_calls)), (0, 0, 0))

    def test_fleet_ytblock_row_for_this_ip_blocks(self):   # the one deliberate fleet row: the guard must see it
        until = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat(timespec="seconds")
        row = {"kind": "ytblock", "ih": f.ip_hash("203.0.113.7"), "until": until}
        with mock.patch.object(f, "fleet_rows", return_value=[row]):
            got = f.blocked_until()
        self.assertIsNotNone(got)
        self.assertEqual(got.isoformat(timespec="seconds"), until)

    def test_channel_mode_shares_guard(self):
        rows = [(i, "t") for i in IDS[:3]]
        with mock.patch.object(f, "yt_dlp", mock.Mock()), mock.patch.object(f, "list_channel", return_value=rows), \
                mock.patch.object(f, "fetch", side_effect=["BLOCKED"]) as m:
            code = f.main(["--analyst", "K", "--out", self.td.name, "--channel", "@x", "--latest", "3"])
        self.assertEqual(m.call_count, 1)
        self.assertIsNotNone(f.blocked_until())
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
