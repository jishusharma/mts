"""YouTube-only proxy in fetch_captions_timed (operator 2026-11-02): every yt-dlp call carries it, a configured but dead
proxy makes zero requests (never the home IP), YT_PROXY=off and no config mean direct. Offline."""
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as f  # noqa: E402

VID = "a" * 11


class T(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.dir = pathlib.Path(self.td.name) / "ytproxy"
        self.dir.mkdir()
        env = mock.patch.dict(os.environ, {"YT_BLOCK_FILE": str(pathlib.Path(self.td.name) / "b.json"),
                                           "YT_PROXY_DIR": str(self.dir), "YT_PROXY": ""})
        env.start()
        self.addCleanup(env.stop)
        ip = mock.patch.object(f, "public_ip", return_value="203.0.113.7")
        ip.start()
        self.addCleanup(ip.stop)
        s = mock.patch.object(f.time, "sleep")
        s.start()
        self.addCleanup(s.stop)

    def test_no_config_is_direct(self):
        self.assertIsNone(f.proxy_url())
        self.assertNotIn("proxy", f.ydl_opts({}))

    def test_config_file_selects_local_warp_port(self):
        (self.dir / "wireproxy.conf").write_text("x", encoding="utf-8")
        self.assertEqual(f.proxy_url(), "socks5://127.0.0.1:40000")
        self.assertEqual(f.ydl_opts({"quiet": True})["proxy"], "socks5://127.0.0.1:40000")

    def test_env_off_beats_config(self):
        (self.dir / "wireproxy.conf").write_text("x", encoding="utf-8")
        with mock.patch.dict(os.environ, {"YT_PROXY": "off"}):
            self.assertIsNone(f.proxy_url())

    def test_caption_fetch_passes_proxy_to_ytdlp(self):
        seen = []

        class FakeYDL:
            def __init__(self, opts):
                seen.append(opts)

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def extract_info(self, url, download=False):
                return {"id": VID, "title": "t"}

        with mock.patch.dict(os.environ, {"YT_PROXY": "socks5://127.0.0.1:40000"}), \
                mock.patch.object(f, "yt_dlp", mock.Mock(YoutubeDL=FakeYDL)), \
                mock.patch.object(f, "spend"):
            r = f.fetch(VID, "K", ["en"], pathlib.Path(self.td.name) / "out")
        self.assertEqual(r, "NOCAPS")
        self.assertTrue(seen and all(o.get("proxy") == "socks5://127.0.0.1:40000" for o in seen))

    def test_dead_proxy_makes_no_request(self):
        with mock.patch.dict(os.environ, {"YT_PROXY": "socks5://127.0.0.1:9"}), \
                mock.patch.object(f, "_port_open", return_value=False), \
                mock.patch.object(f, "yt_dlp", mock.Mock()) as y, mock.patch.object(f, "fetch") as m:
            code = f.main(["--analyst", "K", "--out", self.td.name, VID])
        self.assertEqual(code, f.EXIT_PROXY_DOWN)
        m.assert_not_called()
        y.YoutubeDL.assert_not_called()

    def test_wireproxy_started_for_run_and_stopped_after(self):
        (self.dir / "wireproxy.conf").write_text("x", encoding="utf-8")
        (self.dir / ("wireproxy.exe" if os.name == "nt" else "wireproxy")).write_text("", encoding="utf-8")
        proc = mock.Mock()
        proc.poll.return_value = None
        opens = iter([False, True])
        with mock.patch.object(f, "_port_open", side_effect=lambda *a, **k: next(opens, True)), \
                mock.patch.object(f.subprocess, "Popen", return_value=proc) as po, \
                mock.patch.object(f, "yt_dlp", mock.Mock()), mock.patch.object(f, "fetch", return_value="OK auto 5w"):
            code = f.main(["--analyst", "K", "--out", self.td.name, VID])
        self.assertEqual(code, 0)
        self.assertEqual(sum("wireproxy" in str(c.args[0][0]) for c in po.call_args_list), 1)
        proc.terminate.assert_called_once()

    def test_status_needs_no_proxy(self):
        with mock.patch.dict(os.environ, {"YT_PROXY": "socks5://127.0.0.1:9"}), \
                mock.patch.object(f, "_port_open", return_value=False):
            self.assertEqual(f.main(["--analyst", "K", "--status"]), 0)


if __name__ == "__main__":
    unittest.main()
