"""yt_vpn_fetch wrapper + IP-aware block record in fetch_captions_timed. Offline: subprocess, ipify and fetch are mocked."""
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as ft  # noqa: E402
import yt_vpn_fetch as v  # noqa: E402

HOME_IP, VPN_IP = "203.0.113.7", "198.51.100.9"
SECRET = "SECRET-PROFILE-CONTENT-do-not-log"


class FakeProc:
    def __init__(self, lines):
        self.stdout = iter(lines)
        self.terminated = False

    def poll(self):
        return 0 if self.terminated else None

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self.terminated = True


class T(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.tmp = pathlib.Path(self.td.name)
        self.profile = self.tmp / "p.ovpn"
        self.profile.write_text(SECRET, encoding="utf-8")
        env = mock.patch.dict(os.environ, {"YT_BLOCK_FILE": str(self.tmp / "yt_block.json")})
        env.start()
        self.addCleanup(env.stop)
        self.ips = []
        for target, kw in ((v.time, {"sleep": None}), (ft.time, {"sleep": None})):
            p = mock.patch.object(target, "sleep")
            p.start()
            self.addCleanup(p.stop)
        self.proc = FakeProc(["booting\n", SECRET + "\n", v.READY + "\n"])
        for p in (mock.patch.object(v, "is_admin", return_value=True),
                  mock.patch.object(v.subprocess, "Popen", side_effect=lambda *a, **k: self.proc),
                  mock.patch.object(ft, "public_ip", side_effect=lambda: self.ips.pop(0) if len(self.ips) > 1 else self.ips[0])):
            p.start()
            self.addCleanup(p.stop)

    def run_main(self, extra=(), fetch=None, profile=None):
        argv = ["--profile", str(profile or self.profile), "--analyst", "K", "--out", str(self.tmp), *extra, "a" * 11]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), mock.patch.object(ft, "main", fetch or mock.Mock(return_value=0)) as m:
            try:
                code = v.main(argv)
            except RuntimeError as e:
                code = e
        return code, out.getvalue(), m

    def test_repo_profile_refused(self):
        inside = v.ROOT / "scripts" / "dev" / "not_a_real_profile.ovpn"
        with mock.patch.object(v.subprocess, "Popen") as popen:
            code, out, m = self.run_main(profile=inside)
        self.assertEqual(code, v.EXIT_REFUSED)
        self.assertIn("inside the repo", out)
        self.assertEqual((popen.call_count, m.call_count), (0, 0))

    def test_unchanged_ip_aborts_and_tears_down(self):
        self.ips = [HOME_IP]
        code, out, m = self.run_main()
        self.assertEqual(code, v.EXIT_REFUSED)
        self.assertEqual(m.call_count, 0)
        self.assertTrue(self.proc.terminated)

    def test_teardown_when_fetch_raises(self):
        self.ips = [HOME_IP, VPN_IP, HOME_IP]
        code, out, m = self.run_main(fetch=mock.Mock(side_effect=RuntimeError("boom")))
        self.assertIsInstance(code, RuntimeError)
        self.assertTrue(self.proc.terminated)
        self.assertIn("IP restored", out)

    def test_ip_not_restored_warns_loudly(self):
        self.ips = [HOME_IP, VPN_IP]   # stays on the VPN address after teardown
        code, out, m = self.run_main()
        self.assertEqual(code, v.EXIT_NOT_RESTORED)
        self.assertIn("WARNING", out)
        self.assertTrue(self.proc.terminated)

    def test_happy_path_one_guarded_fetch_capped_at_five(self):
        self.ips = [HOME_IP, VPN_IP, HOME_IP]
        code, out, m = self.run_main(extra=["--max-videos", "9"])
        self.assertEqual(code, 0)
        self.assertEqual(m.call_count, 1)
        argv = m.call_args.args[0]
        self.assertEqual(argv[argv.index("--max-videos") + 1], "5")
        self.assertTrue(self.proc.terminated)

    def test_routes_file_builds_args_and_log_hides_profile(self):
        rf = self.tmp / "routes.txt"
        rf.write_text("# google\n142.250.0.0/15\n2001:db8::/32\n\n", encoding="utf-8")
        self.ips = [HOME_IP, VPN_IP, HOME_IP]
        seen = []
        with mock.patch.object(v, "resolve_host", return_value=["104.26.12.205"]), \
                mock.patch.object(v.subprocess, "Popen", side_effect=lambda cmd, **k: (seen.append(cmd), self.proc)[1]):
            code, out, m = self.run_main(extra=["--only-youtube-routes", "--routes-file", str(rf)])
        cmd = seen[0]
        self.assertIn("--route-nopull", cmd)
        self.assertEqual(cmd.count("--route"), 2)   # IPv6 skipped, ipify host route added
        self.assertIn("142.250.0.0", cmd)
        self.assertIn("255.254.0.0", cmd)
        self.assertNotIn(SECRET, out)
        self.assertNotIn(SECRET, " ".join(cmd))

    def test_block_record_other_ip_ignored_same_ip_stands(self):
        self.ips = [HOME_IP]
        ft.mark_blocked()
        self.assertEqual(json.loads(ft.block_file().read_text())["ip"], HOME_IP)
        self.assertIsNotNone(ft.blocked_until())   # same IP: stands
        self.ips = [VPN_IP]
        self.assertIsNone(ft.blocked_until())      # VPN exit: home record ignored
        ft.mark_blocked()                          # 429 on the new IP writes its own record
        self.assertIsNotNone(ft.blocked_until())
        self.ips = [HOME_IP]
        self.assertIsNotNone(ft.blocked_until())   # home block was kept
        self.ips = [None]
        self.assertIsNotNone(ft.blocked_until())   # unreadable IP: fail closed

    def test_ipify_only_requested_when_record_exists(self):
        self.ips = [HOME_IP]
        with mock.patch.object(ft, "public_ip") as ip:
            self.assertIsNone(ft.blocked_until())
        self.assertEqual(ip.call_count, 0)


if __name__ == "__main__":
    unittest.main()
