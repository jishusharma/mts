"""fetch_captions_timed --channel/--latest: lists a channel, filters titles, fetches newest N, no network (yt_dlp mocked)."""
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as f  # noqa: E402

if f.yt_dlp is None:   # CI has no yt_dlp: stub just what the module touches
    import types
    f.yt_dlp = types.SimpleNamespace(YoutubeDL=None, utils=types.SimpleNamespace(DownloadError=Exception))

VTT = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nhello world\n"
LISTING = [("aaaaaaaaaaa", "BTC bottom"), ("bbbbbbbbbbb", "cooking #shorts"), ("ccccccccccc", "ETH cycle"),
           ("ddddddddddd", "BTC again"), ("eeeeeeeeeee", "BTC old")]


class FakeYDL:
    """Listing call (extract_flat) returns entries; per-video call writes a .vtt into the outtmpl dir."""
    nosubs = set()

    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def extract_info(self, url, download=True):
        if self.opts.get("extract_flat"):
            return {"entries": [{"id": i, "title": t} for i, t in LISTING]}
        vid = url.split("v=")[1]
        if vid not in FakeYDL.nosubs:
            pathlib.Path(str(self.opts["outtmpl"]).replace("%(id)s", vid) + ".en.vtt").write_text(VTT)
        return {"id": vid, "title": "t " + vid, "upload_date": "20261020", "duration": 60, "uploader": "U",
                "subtitles": {}}


class T(unittest.TestCase):
    def setUp(self):   # never touch the real ~/.mts/yt_block.json
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        p = mock.patch.dict("os.environ", {"YT_BLOCK_FILE": str(pathlib.Path(self._td.name) / "b.json"), "YT_PROXY": "off",
                                           "YT_WAITING_FILE": str(pathlib.Path(self._td.name) / "w.json")})
        p.start()
        self.addCleanup(p.stop)
        site = mock.patch.object(f.sites, "http_get", return_value=(0, ""))   # no real transcript-site request, no real waiting list
        site.start()
        self.addCleanup(site.stop)
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

    def test_partial_rate_limit_fails_even_with_cached_video(self):
        with mock.patch.object(f, "list_channel", return_value=LISTING[:2]), \
                mock.patch.object(f, "fetch", side_effect=["EXISTS", "RATELIMIT"]), \
                mock.patch.object(f.time, "sleep"):
            self.assertEqual(f.main(["--analyst", "Krown", "--channel", "@x", "--latest", "2"]), 1)

    def test_no_recent_videos_is_success(self):
        with mock.patch.object(f, "list_channel", return_value=LISTING[:1]), \
                mock.patch.object(f, "video_date", return_value="2026-10-01"):
            self.assertEqual(f.main(["--analyst", "Krown", "--channel", "@x", "--since", "2026-10-22"]), 0)

    def run_main(self, args, nosubs=()):
        FakeYDL.nosubs = set(nosubs)
        with tempfile.TemporaryDirectory() as td:
            canon = pathlib.Path(td) / "canon"
            with mock.patch.object(f.yt_dlp, "YoutubeDL", FakeYDL), mock.patch.object(f, "CANON", canon), \
                    mock.patch.object(f.time, "sleep"):
                rc = f.main(["--analyst", "Krown", "--out", str(canon)] + args)
            return rc, sorted(p.name for p in canon.glob("*_raw.txt")), {p.name: p.read_text() for p in canon.glob("*_raw.txt")}

    def test_latest_n_with_title_filter_keyed_by_video_id(self):
        rc, raws, texts = self.run_main(["--channel", "@x", "--latest", "2", "--include", "(?i)btc|eth",
                                         "--exclude", "(?i)#shorts"])
        self.assertEqual(rc, 0)
        self.assertEqual(raws, ["aaaaaaaaaaa_raw.txt", "ccccccccccc_raw.txt"])
        self.assertIn("# Channel: @x", texts["aaaaaaaaaaa_raw.txt"])

    def test_no_subs_candidate_is_skipped_not_counted(self):
        rc, raws, _ = self.run_main(["--channel", "@x", "--latest", "2", "--exclude", "#shorts"],
                                    nosubs={"aaaaaaaaaaa"})
        self.assertEqual(raws, ["ccccccccccc_raw.txt", "ddddddddddd_raw.txt"])

    def test_scan_depth_limits_listing(self):
        rc, raws, _ = self.run_main(["--channel", "@x", "--latest", "9", "--scan", "3", "--exclude", "#shorts"])
        self.assertEqual(raws, ["aaaaaaaaaaa_raw.txt", "ccccccccccc_raw.txt"])

    def test_timedtext_429_falls_back_to_transcript_api(self):
        class Blocked(FakeYDL):
            def extract_info(self, url, download=True):
                if download and not self.opts.get("extract_flat"):
                    raise f.yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests")
                return {"title": "t", "upload_date": "20261020", "duration": 60, "uploader": "U"}

        with tempfile.TemporaryDirectory() as td:
            canon = pathlib.Path(td) / "canon"
            with mock.patch.object(f.yt_dlp, "YoutubeDL", Blocked), mock.patch.object(f, "CANON", canon), \
                    mock.patch.object(f.time, "sleep"), mock.patch.object(f, "ALLOW_FALLBACK", True), \
                    mock.patch.object(f, "transcript_api_cues", return_value=([(1, "hello api")], "auto")):
                r = f.fetch("zzzzzzzzzzz", "Krown", ["en"], canon)
            self.assertEqual(r, "OK auto 2w")
            self.assertIn("youtube_transcript_api", (canon / "zzzzzzzzzzz_timed.txt").read_text())
            self.assertIn("hello api", (canon / "zzzzzzzzzzz_raw.txt").read_text())

    def test_429_without_fallback_is_blocked(self):
        class Blocked(FakeYDL):
            def extract_info(self, url, download=True):
                raise f.yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests")

        with tempfile.TemporaryDirectory() as td:
            canon = pathlib.Path(td) / "canon"
            with mock.patch.object(f.yt_dlp, "YoutubeDL", Blocked), mock.patch.object(f, "CANON", canon), \
                    mock.patch.object(f.time, "sleep"), mock.patch.object(f, "transcript_api_cues", return_value=None):
                self.assertEqual(f.fetch("zzzzzzzzzzz", "Krown", ["en"], canon), "BLOCKED")

    def test_video_ids_still_work(self):
        rc, raws, _ = self.run_main(["zzzzzzzzzzz"])
        self.assertEqual((rc, raws), (0, ["zzzzzzzzzzz_raw.txt"]))


if __name__ == "__main__":
    unittest.main()
