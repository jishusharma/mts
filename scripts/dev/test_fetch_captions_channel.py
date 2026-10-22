"""fetch_captions_timed --channel/--latest: lists a channel, filters titles, fetches newest N, no network (yt_dlp mocked)."""
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as f  # noqa: E402

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

    def test_video_ids_still_work(self):
        rc, raws, _ = self.run_main(["zzzzzzzzzzz"])
        self.assertEqual((rc, raws), (0, ["zzzzzzzzzzz_raw.txt"]))


if __name__ == "__main__":
    unittest.main()
