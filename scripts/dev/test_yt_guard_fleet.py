"""Fleet-wide YouTube guard: shared lockout over the signals channel, 24 h budget per IP, escalating lockout, no second
network path, --status. All offline: stubs only, no YouTube request, fleet rows injected."""
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

IP = "203.0.113.7"
IDS = [c * 11 for c in "abcdefgh"]


def row(kind, **kw):
    t = kw.pop("t", datetime.now(timezone.utc))
    return dict(kind=kind, t=t.strftime("%Y%m%dT%H%M%SZ"), **kw)


class Base(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.env = mock.patch.dict(os.environ, {"YT_BLOCK_FILE": str(pathlib.Path(self.td.name) / "b.json"), "YT_PROXY": "off"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.rows = []   # what the "fleet" currently holds
        self.sent = []
        for name, kw in (("public_ip", dict(return_value=IP)),
                         ("fleet_rows", dict(side_effect=lambda fetch=True: self.rows)),
                         ("fleet_send", dict(side_effect=lambda kind, text, **x: self.sent.append((kind, x)) or True))):
            p = mock.patch.object(f, name, **kw)
            p.start()
            self.addCleanup(p.stop)
        s = mock.patch.object(f.time, "sleep")
        s.start()
        self.addCleanup(s.stop)
        f._unflushed[:] = [0, ""]


class FleetLockout(Base):
    def test_remote_429_blocks_this_machine(self):
        until = datetime.now(timezone.utc) + timedelta(hours=5)
        self.rows = [row("ytblock", ih=f.ip_hash(IP), until=until.isoformat(), level=1, host="other")]
        self.assertIsNotNone(f.blocked_until())
        with mock.patch.object(f, "yt_dlp", mock.Mock()), mock.patch.object(f, "fetch") as m:
            self.assertEqual(f.main(["--analyst", "K", "--out", self.td.name, IDS[0]]), f.EXIT_BLOCKED)
        self.assertEqual(m.call_count, 0)

    def test_remote_block_for_other_ip_ignored(self):
        until = datetime.now(timezone.utc) + timedelta(hours=5)
        self.rows = [row("ytblock", ih=f.ip_hash("198.51.100.9"), until=until.isoformat(), level=1, host="other")]
        self.assertIsNone(f.blocked_until())

    def test_local_429_is_sent_to_fleet_without_the_address(self):
        f.mark_blocked()
        kinds = [k for k, _ in self.sent]
        self.assertIn("ytblock", kinds)
        self.assertNotIn(IP, repr(self.sent))

    def test_block_appearing_mid_run_stops_before_next_request(self):
        calls = []

        def eff(vid, *a, **k):
            calls.append(vid)
            self.rows = [row("ytblock", ih=f.ip_hash(IP), host="other",
                             until=(datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(), level=1)]
            return "OK auto 1w"
        with mock.patch.object(f, "yt_dlp", mock.Mock()), mock.patch.object(f, "_fetch_net", create=True):
            res = f.guarded_run([(IDS[0], None), (IDS[1], None)],
                                lambda v: (eff(v) if v == IDS[0] else self._spent_fetch(v)), 5)
        self.assertEqual(calls, [IDS[0]])
        self.assertEqual(res[1][1], "UNVERIFIED")

    def _spent_fetch(self, v):
        try:
            f.spend("caption fetch")
        except f.YTBlocked:
            return "UNVERIFIED"
        return "OK auto 1w"

    def test_unreadable_remote_no_local_record_warns_and_proceeds(self):
        f._warned.clear()
        with mock.patch.object(f, "fleet_rows", return_value=None), mock.patch("builtins.print") as pr:
            self.assertIsNone(f.blocked_until())
        self.assertTrue(any("WARNING" in str(c) for c in pr.call_args_list))


class Budget(Base):
    def test_over_budget_defers_without_request(self):
        with mock.patch.dict(os.environ, {"YT_DAILY_BUDGET": "3"}):
            for _ in range(3):
                f.spend("metadata")
            with self.assertRaises(f.BudgetExceeded):
                f.spend("metadata")

    def test_budget_counts_other_machines_and_expires(self):
        ih = f.ip_hash(IP)
        self.rows = [row("ytuse", ih=ih, n=39, host="other"),
                     row("ytuse", ih=ih, n=500, host="other", t=datetime.now(timezone.utc) - timedelta(hours=25))]
        f.spend("x")   # 39 + 1 = 40 allowed
        with self.assertRaises(f.BudgetExceeded):
            f.spend("x")

    def test_metadata_and_listing_count(self):
        y = mock.Mock()
        y.YoutubeDL.return_value.__enter__ = lambda s: s
        y.YoutubeDL.return_value.__exit__ = lambda *a: False
        y.YoutubeDL.return_value.extract_info.return_value = {"entries": [], "upload_date": "20260101"}
        with mock.patch.object(f, "yt_dlp", y):
            f.list_channel("@x", 3)
            f.video_date("a" * 11)
            f.meta("a" * 11)
        self.assertEqual(f._unflushed[0], 3)

    def test_fetch_over_budget_is_deferred(self):
        with mock.patch.dict(os.environ, {"YT_DAILY_BUDGET": "0"}), mock.patch.object(f, "yt_dlp", mock.Mock()) as y:
            r = f.fetch(IDS[0], "K", ["en"], pathlib.Path(self.td.name))
        self.assertEqual(r, "DEFERRED")
        self.assertEqual(len(y.mock_calls), 0)


class Escalation(Base):
    def hours(self):
        u = f.mark_blocked()
        return round((u - datetime.now(timezone.utc)).total_seconds() / 3600)

    def test_6_24_72_72(self):
        self.assertEqual([self.hours() for _ in range(4)], [6, 24, 72, 72])

    def test_clean_fetch_resets(self):
        self.hours()
        self.hours()
        f.mark_clean()
        self.assertEqual(self.hours(), 6)

    def test_level_follows_fleet_rows(self):
        self.rows = [row("ytblock", ih=f.ip_hash(IP), host="other", level=2,
                         until=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat())]
        self.assertEqual(self.hours(), 72)


class NoSecondPath(Base):
    def _run(self, **kw):
        err = f.yt_dlp_error = type("DE", (Exception,), {})
        y = mock.Mock()
        y.utils.DownloadError = err
        y.YoutubeDL.return_value.__enter__ = lambda s: s
        y.YoutubeDL.return_value.__exit__ = lambda *a: False
        y.YoutubeDL.return_value.extract_info.side_effect = err("HTTP Error 429: Too Many Requests")
        with mock.patch.object(f, "yt_dlp", y), mock.patch.object(f, "transcript_api_cues") as t, \
                mock.patch.object(f, "meta") as m:
            r = f.fetch(IDS[0], "K", ["en"], pathlib.Path(self.td.name))
        return r, t, m

    def test_429_makes_no_fallback_or_metadata_request(self):
        r, t, m = self._run()
        self.assertEqual(r, "BLOCKED")
        self.assertEqual((t.call_count, m.call_count), (0, 0))
        self.assertEqual(f._unflushed[0], 1)


class Status(Base):
    def test_status_shows_budget_and_level_without_network(self):
        f.spend("x")
        f.mark_blocked()
        with mock.patch.object(f, "yt_dlp", mock.Mock()) as y, mock.patch.object(f, "public_ip") as ip, \
                mock.patch("builtins.print") as pr:
            ip.side_effect = AssertionError("network")
            self.assertEqual(f.main(["--analyst", "K", "--status"]), 0)
        out = " ".join(str(c) for c in pr.call_args_list)
        self.assertIn("lockout level 1", out)
        self.assertIn("budget used 1 of 40", out)
        self.assertIn("BLOCKED until", out)
        self.assertEqual(len(y.mock_calls), 0)


if __name__ == "__main__":
    unittest.main()
