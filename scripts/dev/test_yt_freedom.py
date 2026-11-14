"""YouTube freedom (yt.py, yt_mirrors.py, yt_tor.py, yt_gha_runner.py): route order, fallback on a 429 / lock inside one call,
mirror-list parsing, nothing but YouTube through a proxy, Tor download verification. No network: every route is a fake or
its HTTP function is patched."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "MyTradingSys"))
import yt  # noqa: E402
import yt_mirrors as mirrors  # noqa: E402
import yt_tor  # noqa: E402

CUES = [(0, "hello there"), (4, "second line")]
RES = {"cues": CUES, "info": {"title": "T", "upload_date": "20261101", "uploader": "U", "duration": 9}, "lang": "hi", "auto": True}


class Fake(yt.Route):
    """A scripted route: `outcome` is a result dict or an exception instance."""
    caps = ("captions", "audio", "list")

    def __init__(self, name, outcome, exit_name=None):
        self.name, self.outcome, self._exit, self.calls = name, outcome, exit_name, 0

    def exit_name(self):
        return self._exit

    def captions(self, vid, langs):
        self.calls += 1
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome

    def audio(self, vid, dest):
        self.calls += 1
        if isinstance(self.outcome, Exception):
            raise self.outcome
        p = Path(str(dest) + ".m4a")
        p.write_bytes(b"x")
        return p

    def listing(self, target, limit):
        self.calls += 1
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return [("aaaaaaaaaaa", "t1", ""), ("bbbbbbbbbbb", "t2", "")]


class Base(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.td = Path(td.name)
        env = mock.patch.dict(os.environ, {
            "YT_ROUTES_FILE": str(self.td / "routes.json"), "YT_MIRRORS_FILE": str(self.td / "mirrors.json"),
            "YT_CACHE_DIR": str(self.td / "cache"), "YT_PROXY_DIR": str(self.td / "proxy"), "YT_PROXY": "off"})
        env.start()
        self.addCleanup(env.stop)
        canon = mock.patch.object(yt.ft, "CANON", self.td / "canon")
        canon.start()
        self.addCleanup(canon.stop)
        self.slept = []
        sl = mock.patch.object(yt, "SLEEP", lambda s: self.slept.append(s))
        sl.start()
        self.addCleanup(sl.stop)


class RouteOrder(Base):
    def test_order_is_the_documented_chain(self):
        self.assertEqual([r.name for r in yt.build_routes()],
                         ["warp", "v6", "tor", "invidious", "piped", "clients:warp", "clients:v6", "clients:tor", "asr", "gha", "fleet"])
        self.assertEqual(list(yt.ROUTE_ORDER), [r.name for r in yt.build_routes()])

    def test_runner_set_has_no_station_proxy(self):
        names = [r.name for r in yt.build_routes(runner=True)]
        self.assertEqual(names, ["direct", "tapi:direct", "invidious", "piped", "clients:direct"])
        self.assertFalse({"warp", "tor", "v6"} & set(names))

    def test_only_filter_keeps_order(self):
        self.assertEqual([r.name for r in yt.build_routes(["tor", "warp"])], ["warp", "tor"])

    def test_home_address_is_never_a_route(self):
        ok, why = yt.DirectExit().available()
        self.assertFalse(ok)
        self.assertIn("never a route", why)
        with mock.patch.dict(os.environ, {"YT_ALLOW_DIRECT": "1"}):
            self.assertTrue(yt.DirectExit().available()[0])

    def test_runner_script_refuses_outside_github_actions(self):
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_ACTIONS", "YT_RUNNER_TEST")}
        r = subprocess.run([sys.executable, str(HERE / "yt_gha_runner.py"), "--ids", "aaaaaaaaaaa"], env=env,
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("only inside GitHub Actions", r.stderr)


class Fallback(Base):
    def test_a_429_moves_to_the_next_route_in_the_same_call_without_waiting(self):
        first = Fake("tor", yt.Locked("HTTP 429", hard=True), "tor")
        second = Fake("invidious", RES)
        third = Fake("piped", RES)
        got, name, tried, final = yt.get_captions("aaaaaaaaaaa", [first, second, third], ["hi"])
        self.assertEqual(name, "invidious")
        self.assertEqual((first.calls, second.calls, third.calls), (1, 1, 0))
        self.assertTrue(tried[0].startswith("tor:locked"))
        self.assertEqual(self.slept, [])   # a lock is never waited out
        self.assertIsNotNone(yt.locked_until("exit:tor"))

    def test_locked_exit_is_skipped_without_a_request_on_the_next_video(self):
        first = Fake("tor", yt.Locked("HTTP 429", hard=True), "tor")
        second = Fake("invidious", RES)
        yt.get_captions("aaaaaaaaaaa", [first, second], ["hi"])
        yt.get_captions("bbbbbbbbbbb", [first, second], ["hi"])
        self.assertEqual(first.calls, 1)   # the second video never touched the locked exit
        self.assertEqual(second.calls, 2)

    def test_lock_levels_escalate_then_success_resets(self):
        self.assertEqual([yt.lock_hard("tor", "x") for _ in range(4)], [0.5, 2, 12, 12])
        yt.note_ok("tor")
        self.assertEqual(yt.lock_hard("tor", "x"), 0.5)

    def test_a_known_block_end_is_kept_not_shortened_to_30_minutes(self):
        end = yt._now() + timedelta(hours=60)
        r = Fake("warp", yt.Locked("legacy guard locked", hard=True, until=end), "warp")
        yt.get_captions("aaaaaaaaaaa", [r], ["hi"])
        self.assertGreater(yt.locked_until("exit:warp"), yt._now() + timedelta(hours=59))

    def test_expired_lock_is_open_again(self):
        yt.lock("exit:tor", 1, "x")
        self.assertIsNotNone(yt.locked_until("exit:tor"))
        later = yt._now() + timedelta(hours=2)
        self.assertIsNone(yt.locked_until("exit:tor", later))

    def test_sign_in_check_skips_only_that_route_not_the_exit(self):
        plain = Fake("tor", yt.Locked("sign-in check", hard=False), "tor")
        clients = Fake("clients:tor", RES, "tor")
        got, name, tried, _ = yt.get_captions("aaaaaaaaaaa", [plain, clients], ["hi"])
        self.assertEqual(name, "clients:tor")
        self.assertIsNone(yt.locked_until("exit:tor"))
        self.assertIsNotNone(yt.locked_until("route:tor"))

    def test_captions_scope_lock_leaves_audio_usable(self):
        r = Fake("tor", yt.Locked("timedtext HTTP 429", hard=True, scope="captions"), "tor")
        yt.get_captions("aaaaaaaaaaa", [r], ["hi"])
        self.assertIsNotNone(r.lock_until("captions"))
        self.assertIsNone(r.lock_until("audio"))
        self.assertIsNone(r.lock_until())

    def test_route_down_and_a_crashing_plugin_do_not_stop_the_chain(self):
        a = Fake("v6", yt.RouteDown("no ipv6"))
        b = Fake("tor", RuntimeError("boom"))
        c = Fake("invidious", RES)
        got, name, tried, _ = yt.get_captions("aaaaaaaaaaa", [a, b, c], ["hi"])
        self.assertEqual(name, "invidious")
        self.assertIn("v6:down", tried[0])
        self.assertIn("tor:down", tried[1])

    def test_final_no_captions_stops_the_chain_and_audio_goes_to_asr(self):
        a = Fake("v6", yt.Miss("no caption track", final=True))
        b = Fake("invidious", RES)
        got, name, tried, final = yt.get_captions("aaaaaaaaaaa", [a, b], ["hi"])
        self.assertTrue(final)
        self.assertEqual(b.calls, 0)

    def test_get_video_stores_files_and_names_the_route(self):
        r = Fake("v6", RES)
        o = yt.get_video("aaaaaaaaaaa", [r], ["hi"], analyst="NK")
        self.assertEqual((o["status"], o["route"]), ("OK", "v6"))
        body = (self.td / "cache" / "aaaaaaaaaaa_timed.txt").read_text(encoding="utf-8")
        self.assertIn("# Source: yt.py route v6 (auto)", body)
        self.assertIn("[00:00:04] second line", body)
        meta = json.loads((self.td / "cache" / "aaaaaaaaaaa.meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["route"], "v6")

    def test_cached_video_costs_no_request(self):
        r = Fake("v6", RES)
        yt.get_video("aaaaaaaaaaa", [r], ["hi"])
        r2 = Fake("v6", RES)
        o = yt.get_video("aaaaaaaaaaa", [r2], ["hi"])
        self.assertEqual((o["status"], r2.calls), ("CACHED", 0))

    def test_audio_flag_downloads_through_the_first_route_that_can(self):
        bad = Fake("tor", yt.RouteDown("down"))
        good = Fake("invidious", RES)
        o = yt.get_video("aaaaaaaaaaa", [bad, good], ["hi"], want_audio=True)
        self.assertEqual(o["audio_route"], "invidious")
        self.assertTrue(Path(o["audio"]).exists())

    def test_transcript_falls_to_whisper_when_no_route_has_captions(self):
        class Asr(yt.AsrRoute):
            def available(self):
                return True, ""

            def transcribe(self, vid, audio, langs, run=None):
                return {"cues": [(1, "whisper text")], "info": {}, "lang": "hi", "auto": True}
        down = Fake("v6", yt.Miss("no caption track", final=True))
        o = yt.get_video("aaaaaaaaaaa", [down, Asr()], ["hi"], want_transcript=True)
        # no audio route among the fakes except `down` (raises Miss): the chain reports FAIL/NOCAPS instead of inventing text
        self.assertNotEqual(o["status"], "OK")
        aud = Fake("invidious", RES)
        o = yt.get_video("bbbbbbbbbbb", [down, aud, Asr()], ["hi"], want_transcript=True)
        self.assertEqual((o["status"], o["route"]), ("OK", "asr"))
        self.assertIn("# Source: yt.py route asr", (self.td / "cache" / "bbbbbbbbbbb_timed.txt").read_text(encoding="utf-8"))

    def test_expand_lists_a_playlist_through_the_first_route_that_can(self):
        bad = Fake("tor", yt.RouteDown("down"))
        good = Fake("invidious", None)
        ids, tried = yt.expand("PLabcdefghijklmnop", 5, [bad, good])
        self.assertEqual(ids, ["aaaaaaaaaaa", "bbbbbbbbbbb"])
        ids, _ = yt.expand("https://youtu.be/ccccccccccc", 5, [bad])
        self.assertEqual(ids, ["ccccccccccc"])

    def test_gha_batch_dispatches_waits_and_reads_the_artifact(self):
        calls, kws = [], []

        def fake_run(cmd, cwd=None, capture_output=None, text=None, **kw):
            calls.append(cmd[1:3])
            kws.append(kw.get("creationflags"))
            cp = types.SimpleNamespace(returncode=0, stdout="", stderr="")
            if cmd[1:3] == ["run", "list"]:
                cp.stdout = json.dumps([{"databaseId": 77, "createdAt": yt._iso(yt._now()), "event": "workflow_dispatch"}])
            elif cmd[1:3] == ["run", "view"]:
                cp.stdout = json.dumps({"status": "completed", "conclusion": "success"})
            elif cmd[1:3] == ["run", "download"]:
                d = Path(cmd[cmd.index("-D") + 1])
                (d / "yt-fetch").mkdir()
                (d / "yt-fetch" / "aaaaaaaaaaa.json").write_text(json.dumps({"cues": [[0, "hi"]], "info": {}, "lang": "en"}))
                (d / "yt-fetch" / "summary.json").write_text("{}")
            return cp
        with mock.patch.object(yt.shutil, "which", return_value="gh"):
            got = yt.GhaRoute().run_batch(["aaaaaaaaaaa", "bbbbbbbbbbb"], ["en"], run=fake_run, sleep=lambda s: None)
        self.assertEqual(list(got), ["aaaaaaaaaaa"])
        self.assertEqual(got["aaaaaaaaaaa"]["cues"], [(0, "hi")])
        self.assertEqual(calls[0], ["workflow", "run"])
        self.assertEqual(set(kws), {yt.nowin.NOWIN})

    def test_fleet_ask_is_short_and_returns_the_ask_id(self):
        seen = {}

        def fake_run(cmd, **kw):
            seen["cmd"] = cmd
            return types.SimpleNamespace(returncode=0, stdout="ask q-1a2b3c sent\n", stderr="")
        qid = yt.FleetRoute().ask([f"{i:011d}" for i in range(20)], run=fake_run)
        self.assertEqual(qid, "q-1a2b3c")
        self.assertLessEqual(len(seen["cmd"][3]), 190)
        self.assertIn("task", seen["cmd"])

    def test_remote_routes_only_run_for_ids_nothing_else_got(self):
        ok = {"id": "aaaaaaaaaaa", "status": "OK", "tried": [], "files": []}
        bad = {"id": "bbbbbbbbbbb", "status": "FAIL", "tried": [], "files": []}
        fleet = yt.FleetRoute()
        with mock.patch.object(yt.FleetRoute, "ask", return_value="q-000001") as ask:
            yt.finish_remote([ok, bad], [fleet], ["hi"], True, "", self.td / "cache")
        ask.assert_called_once_with(["bbbbbbbbbbb"])
        self.assertEqual(bad["status"], "ASKED")
        self.assertEqual(ok["status"], "OK")
        with mock.patch.object(yt.FleetRoute, "ask") as ask:
            yt.finish_remote([dict(bad, status="FAIL")], [fleet], ["hi"], False, "", self.td / "cache")
        ask.assert_not_called()


class MirrorLists(Base):
    INV = [["a.example", {"type": "https", "api": True, "monitor": {"down": False, "uptime": 99.0}}],
           ["down.example", {"type": "https", "api": True, "monitor": {"down": True}}],
           ["b.example", {"type": "https", "api": False, "monitor": {"down": False, "uptime": 99.9}}],
           ["x.onion", {"type": "onion", "api": None, "monitor": None}],
           ["noapi-better.example", {"type": "https", "api": True, "monitor": {"down": False, "uptime": 99.99}}],
           ["bad-row"], "junk"]
    PIPED = ("Instance Name | Instance API URL | Instance Location(s)\n--- | --- | ---\n"
             "kavin (Official) | https://pipedapi.kavin.rocks | US\nleptons | https://pipedapi.leptons.xyz | AT\n"
             "dup | https://pipedapi.kavin.rocks | US\nnot a url | http://plain.example | x\n")

    def test_invidious_list_parsing(self):
        self.assertEqual(mirrors.parse_invidious_list(self.INV), ["noapi-better.example", "a.example", "b.example"])
        self.assertEqual(mirrors.parse_invidious_list({"not": "a list"}), [])

    def test_piped_list_parsing(self):
        self.assertEqual(mirrors.parse_piped_list(self.PIPED), ["https://pipedapi.kavin.rocks", "https://pipedapi.leptons.xyz"])

    def test_refresh_probes_caches_and_orders_good_first(self):
        def fake_get(url, timeout=0, binary=False):
            if "api.invidious.io" in url:
                return 200, json.dumps(self.INV)
            if "TeamPiped" in url:
                return 200, self.PIPED
            return 404, ""
        with mock.patch.object(mirrors, "http_get", fake_get), \
                mock.patch.object(mirrors, "probe", lambda kind, host: host in ("b.example", "https://pipedapi.leptons.xyz")):
            live = mirrors.refresh(force=True)
        self.assertEqual(live, {"invidious": ["b.example"], "piped": ["https://pipedapi.leptons.xyz"]})
        self.assertEqual(mirrors.candidates("invidious")[0], "b.example")   # proven first
        self.assertNotIn("a.example", mirrors.candidates("invidious")[:1])
        n, tot, hosts = mirrors.health_summary("invidious")
        self.assertEqual((n, hosts), (1, ["b.example"]))

    def test_failed_mirror_sits_out_its_cooldown(self):
        mirrors.save({"invidious_list": ["a.example", "b.example"]})
        mirrors.mark("invidious", "a.example", False, "bot check")
        self.assertEqual(mirrors.candidates("invidious"), ["b.example"])
        later = mirrors._utcnow() + timedelta(minutes=mirrors.FAIL_COOLDOWN_MIN + 1)
        self.assertIn("a.example", mirrors.candidates("invidious", later))

    def test_a_bot_check_page_is_a_down_mirror_not_captions(self):
        with mock.patch.object(mirrors, "http_get", lambda url, timeout=0, binary=False: (200, "<!doctype html><title>checking</title>")):
            self.assertFalse(mirrors.probe_invidious("a.example"))
            with self.assertRaises(mirrors.MirrorDown):
                mirrors.inv_captions("a.example", "aaaaaaaaaaa", ["en"], sleep=lambda s: None)

    def test_invidious_captions_pick_the_wanted_language_and_parse_vtt(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nnamaste doston\n"

        def fake_get(url, timeout=0, binary=False):
            if url.endswith("/api/v1/captions/aaaaaaaaaaa"):
                return 200, json.dumps({"captions": [
                    {"label": "English (auto-generated)", "languageCode": "en", "url": "/en"},
                    {"label": "Hindi (auto-generated)", "languageCode": "hi", "url": "/hi"}]})
            if url.endswith("/hi"):
                return 200, vtt
            if "/api/v1/videos/" in url:
                return 200, json.dumps({"title": "T", "author": "A", "published": 1794422160, "lengthSeconds": 5})
            return 404, ""
        with mock.patch.object(mirrors, "http_get", fake_get):
            r = mirrors.inv_captions("a.example", "aaaaaaaaaaa", ["hi", "en"], sleep=lambda s: None)
        self.assertEqual((r["lang"], r["cues"], r["info"]["title"]), ("hi", [(1, "namaste doston")], "T"))

    def test_ttml_parsing(self):
        ttml = '<tt><body><div><p begin="00:00:01.500" end="00:00:03.000">hello <span>there</span></p><p begin="4s">b &amp; c</p></div></body></tt>'
        self.assertEqual(mirrors.parse_ttml(ttml), [(1, "hello there"), (4, "b & c")])

    def test_target_classification(self):
        c = mirrors.classify
        self.assertEqual(c("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3"), ("video", "dQw4w9WgXcQ"))
        self.assertEqual(c("dQw4w9WgXcQ"), ("video", "dQw4w9WgXcQ"))
        self.assertEqual(c("https://youtu.be/dQw4w9WgXcQ"), ("video", "dQw4w9WgXcQ"))
        self.assertEqual(c("https://www.youtube.com/playlist?list=PLabcdefghijklmnop"), ("playlist", "PLabcdefghijklmnop"))
        self.assertEqual(c("@NKStockTalk"), ("handle", "@NKStockTalk"))
        self.assertEqual(c("https://www.youtube.com/@NKStockTalk/videos"), ("handle", "@NKStockTalk"))
        self.assertEqual(c("https://www.youtube.com/channel/UC" + "a" * 22), ("channel_id", "UC" + "a" * 22))
        self.assertEqual(c("not a target at all")[0], "unknown")

    def test_audio_format_pick_prefers_itag_140_then_lowest_bitrate(self):
        fm = [{"itag": "251", "type": "audio/webm", "bitrate": "160000"}, {"itag": "140", "type": "audio/mp4", "bitrate": "130000"},
              {"itag": "18", "type": "video/mp4"}]
        self.assertEqual(mirrors.pick_audio(fm)["itag"], "140")
        self.assertEqual(mirrors.pick_audio(fm[:1] + [{"itag": "250", "type": "audio/webm", "bitrate": "70000"}])["itag"], "250")
        self.assertIsNone(mirrors.pick_audio([fm[2]]))


class YouTubeOnly(Base):
    def test_yt_only_allows_youtube_hosts_and_refuses_everything_else(self):
        for ok in ("https://www.youtube.com/watch?v=x", "https://youtu.be/x", "https://rr1---sn-a.googlevideo.com/videoplayback",
                   "https://i.ytimg.com/vi/x/0.jpg"):
            self.assertEqual(yt.yt_only(ok), ok)
        for bad in ("https://api.ipify.org", "https://exchange.example/api/v3/ticker", "https://futures.example/x",
                    "https://www.youtube.com.evil.example/x", "https://notyoutube.com/", "https://options.example/"):
            with self.assertRaises(ValueError):
                yt.yt_only(bad)

    def _fake_ytdlp(self, info, urls, opts_seen, text="WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nhi there\n"):
        class Resp:
            status = 200

            def read(self_):
                return text.encode()

        class YDL:
            def __init__(self_, opts):
                opts_seen.append(opts)

            def __enter__(self_):
                return self_

            def __exit__(self_, *a):
                return False

            def extract_info(self_, url, download=False):
                urls.append(url)
                return info

            def urlopen(self_, url):
                urls.append(url)
                return Resp()
        mod = types.SimpleNamespace(YoutubeDL=YDL, utils=types.SimpleNamespace(DownloadError=type("DownloadError", (Exception,), {})))
        return mock.patch.dict(sys.modules, {"yt_dlp": mod})

    def test_proxy_only_ever_sees_youtube_urls(self):
        info = {"title": "T", "subtitles": {}, "automatic_captions": {"hi-orig": [{"ext": "vtt", "url": "https://www.youtube.com/api/timedtext?v=x"}]}}
        urls, opts = [], []
        tor = yt.TorExit()
        with self._fake_ytdlp(info, urls, opts):
            r = yt.ytdlp_captions(tor, "aaaaaaaaaaa", ["hi"])
        self.assertEqual(r["lang"], "hi")
        self.assertTrue(urls)
        for u in urls:
            yt.yt_only(u)
        self.assertEqual(opts[0]["proxy"], yt_tor.socks_url())

    def test_a_caption_url_on_another_host_is_never_requested_through_the_proxy(self):
        info = {"automatic_captions": {"hi": [{"ext": "vtt", "url": "https://evil.example/steal.vtt"}]}}
        urls, opts = [], []
        with self._fake_ytdlp(info, urls, opts):
            with self.assertRaises(yt.RouteDown):
                yt.ytdlp_captions(yt.TorExit(), "aaaaaaaaaaa", ["hi"])
        self.assertNotIn("https://evil.example/steal.vtt", urls)

    def test_track_choice_prefers_native_over_translation(self):
        info = {"subtitles": {}, "automatic_captions": {
            "en": [{"ext": "vtt", "url": "https://www.youtube.com/api/timedtext?v=x&tlang=en"}],
            "hi-orig": [{"ext": "vtt", "url": "https://www.youtube.com/api/timedtext?v=x&lang=hi"}]}}
        t = yt.pick_ytdlp_track(yt.tracks_from_info(info), ["en", "hi"])
        self.assertEqual((t["code"], t["translated"]), ("hi", False))   # a translation is what YouTube throttles hardest
        t = yt.pick_ytdlp_track(yt.tracks_from_info({"subtitles": {"en": [{"ext": "vtt", "url": "https://www.youtube.com/a"}]}}), ["en"])
        self.assertFalse(t["auto"])

    def test_error_classification(self):
        with self.assertRaises(yt.Locked) as c:
            yt.classify_error("HTTP Error 429: Too Many Requests")
        self.assertTrue(c.exception.hard)
        with self.assertRaises(yt.Locked) as c:
            yt.classify_error("Sign in to confirm you're not a bot")
        self.assertFalse(c.exception.hard)
        with self.assertRaises(yt.Miss) as c:
            yt.classify_error("Video unavailable")
        self.assertTrue(c.exception.final)
        with self.assertRaises(yt.RouteDown):
            yt.classify_error("socks connect failed")

    def test_mirror_traffic_never_uses_a_proxy_opener(self):
        src = (HERE / "yt_mirrors.py").read_text(encoding="utf-8")
        self.assertNotIn("ProxyHandler", src)
        self.assertNotIn("socks", src)


class TorInstall(Base):
    def test_sha256sums_parsing(self):
        txt = f"{'a' * 64}  tor-expert-bundle-windows-x86_64-1.0.tar.gz\n{'B' * 64} *other.tar.gz\njunk line\n"
        self.assertEqual(yt_tor.parse_sha256sums(txt), {"tor-expert-bundle-windows-x86_64-1.0.tar.gz": "a" * 64, "other.tar.gz": "b" * 64})

    def test_verify_needs_two_hosts_that_both_match(self):
        data = b"bundle"
        h = hashlib.sha256(data).hexdigest()
        self.assertEqual(yt_tor.verify(data, "f", {"dist": {"f": h}, "archive": {"f": h}}), h)
        with self.assertRaises(yt_tor.TorError):
            yt_tor.verify(data, "f", {"dist": {"f": h}})                              # one host is not enough
        with self.assertRaises(yt_tor.TorError):
            yt_tor.verify(data, "f", {"dist": {"f": h}, "archive": {"f": "0" * 64}})  # a disagreeing host
        with self.assertRaises(yt_tor.TorError):
            yt_tor.verify(data, "f", {"dist": {"f": h}, "archive": {"g": h}})         # not listed

    def test_install_extracts_nothing_when_the_hash_does_not_match(self):
        name = f"tor-expert-bundle-{yt_tor.platform_tag()}-9.9.tar.gz"
        sums = f"{'0' * 64}  {name}\n"

        def get(url, binary=False, timeout=0):
            if url.endswith("downloads.json"):
                return json.dumps({"version": "9.9"})
            if url.endswith("sha256sums-signed-build.txt"):
                return sums
            return b"tampered bytes" if binary else ""
        with self.assertRaises(yt_tor.TorError):
            yt_tor.install(get=get)
        self.assertFalse((self.td / "proxy" / "tor" / "tor").exists())

    def test_extract_refuses_path_escape_and_links(self):
        for kind in ("escape", "link"):
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w:gz") as tf:
                if kind == "escape":
                    ti = tarfile.TarInfo("../evil.txt")
                    ti.size = 1
                    tf.addfile(ti, io.BytesIO(b"x"))
                else:
                    ti = tarfile.TarInfo("ln")
                    ti.type = tarfile.SYMTYPE
                    ti.linkname = "/etc/passwd"
                    tf.addfile(ti)
            p = self.td / f"{kind}.tar.gz"
            p.write_bytes(buf.getvalue())
            with self.assertRaises(yt_tor.TorError):
                yt_tor.safe_extract(p, self.td / "out")
        self.assertFalse((self.td / "evil.txt").exists())

    def test_tor_listens_on_localhost_only(self):
        yt_tor.write_torrc()
        rc = yt_tor.torrc_path().read_text(encoding="utf-8")
        self.assertIn("SocksPort 127.0.0.1:", rc)
        self.assertIn("ControlPort 127.0.0.1:", rc)
        self.assertIn("CookieAuthentication 1", rc)
        self.assertTrue(yt_tor.socks_url().startswith("socks5h://127.0.0.1:"))


class Health(Base):
    def test_health_line_per_route_with_state_and_lock(self):
        up = Fake("v6", None)
        up.available = lambda: (True, "")
        down = Fake("tor", None)
        down.available = lambda: (False, "not installed")
        locked = Fake("warp", None, "warp")
        yt.lock_hard("warp", "HTTP 429")
        lines, ups = yt.health_lines([up, down, locked], probe=False)
        self.assertEqual(ups, 1)
        self.assertTrue(lines[0].startswith("v6") and " up " in lines[0])
        self.assertIn("down", lines[1])
        self.assertIn("locked", lines[2])
        self.assertIn("until", lines[2])

    def test_health_exit_code_is_nonzero_when_no_captions_route_is_up(self):
        down = Fake("tor", None)
        down.available = lambda: (False, "x")
        out = []
        self.assertEqual(yt.cmd_health(types.SimpleNamespace(cached=True), [down], out.append), 1)
        self.assertTrue(out[-1].startswith("YT_HEALTH 0"))


if __name__ == "__main__":
    unittest.main()
