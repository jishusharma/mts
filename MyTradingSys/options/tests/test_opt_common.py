"""Tests: public-only client (backoff, safety, rate limit) and gzip append integrity. Offline, fake HTTP."""
import gzip
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opt_testutil as T  # noqa: E402
from opt_testutil import C  # noqa: E402


def client_for(script, **kw):
    tr = T.ScriptedTransport(script)
    clk = T.FakeClock()
    kw.setdefault("jitter", False)
    kw.setdefault("backoff_base", 1.0)
    cl = C.DeribitPublic(C.LIVE_BASE, rate=5.0, transport=tr, sleep=clk.sleep, clock=clk.clock, **kw)
    return cl, tr, clk


OK = (200, T.envelope_ok({"index_price": 1.0}), {})
E10028 = (200, T.envelope_err(10028, "Too many requests"), {})


class Backoff(unittest.TestCase):
    def sleeps_without_rate_waits(self, clk, n_expected):
        # rate limiter sleeps are tiny (<=0.2s); backoff sleeps are >= 1.0 s with base 1.0
        return [s for s in clk.sleeps if s >= 1.0][:n_expected]

    def test_retries_10028_then_succeeds_with_doubling_delay(self):
        cl, tr, clk = client_for([E10028, E10028, OK])
        self.assertEqual(cl.call("public/get_index_price", {"index_name": "btc_usd"}), {"index_price": 1.0})
        self.assertEqual(cl.n_requests, 3)
        self.assertEqual(cl.n_retries, 2)
        self.assertEqual(self.sleeps_without_rate_waits(clk, 2), [1.0, 2.0])

    def test_retries_http_429(self):
        cl, tr, clk = client_for([(429, b"slow down", {}), OK])
        self.assertEqual(cl.call("public/get_index_price"), {"index_price": 1.0})
        self.assertEqual(cl.n_retries, 1)

    def test_retries_network_error(self):
        cl, tr, clk = client_for([urllib.error.URLError("boom"), TimeoutError("t"), OK])
        self.assertEqual(cl.call("public/get_index_price"), {"index_price": 1.0})
        self.assertEqual(cl.n_retries, 2)

    def test_recorded_10028_envelope_is_retryable(self):
        body = json.dumps(T.fixture("error_10028.json")).encode()
        cl, tr, clk = client_for([(200, body, {}), OK])
        self.assertEqual(cl.call("public/get_index_price"), {"index_price": 1.0})

    def test_non_retryable_api_error_raises_at_once(self):
        cl, tr, clk = client_for([(200, T.envelope_err(-32602, "Invalid params", {"param": "count"}), {})])
        with self.assertRaises(C.DeribitError) as cm:
            cl.call("public/get_last_trades_by_currency_and_time", {"count": 99999})
        self.assertEqual(cm.exception.code, -32602)
        self.assertEqual(cl.n_requests, 1)
        self.assertEqual(cl.n_retries, 0)

    def test_gives_up_after_max_retries(self):
        cl, tr, clk = client_for([E10028], max_retries=3)
        with self.assertRaises(C.DeribitError) as cm:
            cl.call("public/get_index_price")
        self.assertEqual(cm.exception.code, "retries_exhausted")
        self.assertEqual(cl.n_requests, 4)
        self.assertEqual(self.sleeps_without_rate_waits(clk, 3), [1.0, 2.0, 4.0])

    def test_delay_is_capped(self):
        cl, tr, clk = client_for([E10028], max_retries=5, backoff_cap=4.0)
        with self.assertRaises(C.DeribitError):
            cl.call("public/get_index_price")
        self.assertEqual(self.sleeps_without_rate_waits(clk, 5), [1.0, 2.0, 4.0, 4.0, 4.0])

    def test_retry_after_header_is_honoured(self):
        cl, tr, clk = client_for([(429, b"", {"Retry-After": "7"}), OK])
        cl.call("public/get_index_price")
        self.assertIn(7.0, clk.sleeps)

    def test_http_500_html_body_is_retried_not_crashed(self):
        cl, tr, clk = client_for([(502, b"<html>bad gateway</html>", {}), OK])
        self.assertEqual(cl.call("public/get_index_price"), {"index_price": 1.0})


class Safety(unittest.TestCase):
    def test_private_and_non_public_methods_are_refused(self):
        cl, tr, clk = client_for([OK])
        for bad in ("private/get_account_summary", "private/buy", "public/../private/buy", "get_time", "public/buy?x=1",
                    "/public/get_time"):
            with self.assertRaises(ValueError, msg=bad):
                cl.call(bad)
        self.assertEqual(tr.urls, [], "a refused method must never reach the transport")

    def test_only_public_deribit_hosts_are_allowed(self):
        for bad in ("http://www.deribit.com/api/v2", "https://test.deribit.com/api/v2", "https://evil.example/api/v2",
                    "https://www.deribit.com.evil.example/api/v2", "https://www.deribit.com/other"):
            with self.assertRaises(ValueError, msg=bad):
                C.DeribitPublic(bad)
        C.DeribitPublic(C.LIVE_BASE)
        C.DeribitPublic(C.HISTORY_BASE)

    def test_rate_above_five_per_second_is_refused(self):
        with self.assertRaises(ValueError):
            C.DeribitPublic(C.LIVE_BASE, rate=5.1)
        with self.assertRaises(ValueError):
            C.RateLimiter(0)

    def test_request_is_a_plain_get_url_without_credentials(self):
        cl, tr, clk = client_for([OK])
        cl.call("public/get_index_price", {"index_name": "btc_usd"})
        self.assertEqual(tr.urls, [C.LIVE_BASE + "/public/get_index_price?index_name=btc_usd"])


class RateLimiting(unittest.TestCase):
    def test_request_starts_are_spaced_by_at_least_one_over_rate(self):
        clk = T.FakeClock()
        rl = C.RateLimiter(5.0, clock=clk.clock, sleep=clk.sleep)
        starts = []
        for _ in range(11):
            rl.acquire()
            starts.append(clk.t)
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        self.assertTrue(all(g >= 0.2 - 1e-9 for g in gaps), gaps)
        self.assertAlmostEqual(starts[-1] - starts[0], 2.0, places=6)  # 10 gaps x 0.2 s: never faster than 5 req/s


class GzAppend(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "chain" / "2026-10-08.jsonl.gz"

    def tearDown(self):
        self.tmp.cleanup()

    def lines(self):
        with gzip.open(self.path, "rt", encoding="utf-8") as f:  # strict multi-member read
            return [json.loads(x) for x in f]

    def test_appends_accumulate_and_each_is_one_member(self):
        for i in range(3):
            C.append_gz_line(self.path, json.dumps({"i": i}))
        self.assertEqual([d["i"] for d in self.lines()], [0, 1, 2])
        good, n, clean = C.gz_scan(self.path)
        self.assertTrue(clean)
        self.assertEqual(n, 3)
        self.assertEqual(good, self.path.stat().st_size)

    def test_second_append_does_not_overwrite_first(self):
        C.append_gz_line(self.path, json.dumps({"a": 1}))
        size1 = self.path.stat().st_size
        C.append_gz_line(self.path, json.dumps({"a": 2}))
        self.assertGreater(self.path.stat().st_size, size1)
        self.assertEqual([d["a"] for d in self.lines()], [1, 2])

    def test_crash_mid_write_is_detected_and_repaired_on_next_append(self):
        C.append_gz_line(self.path, json.dumps({"n": 1}))
        C.append_gz_line(self.path, json.dumps({"n": 2}))
        raw = self.path.read_bytes()
        self.path.write_bytes(raw[:-7])  # simulate a crash that cut the last member
        good, n, clean = C.gz_scan(self.path)
        self.assertFalse(clean)
        self.assertEqual(n, 1)
        self.assertEqual([json.loads(x)["n"] for x in C.read_gz_lines(self.path)], [1])  # tolerant reader
        with self.assertRaises((EOFError, OSError)):
            list(C.read_gz_lines(self.path, strict=True))
        C.append_gz_line(self.path, json.dumps({"n": 3}))
        self.assertEqual([d["n"] for d in self.lines()], [1, 3])  # strict read works again
        self.assertTrue(C.gz_scan(self.path)[2])
        self.assertTrue(Path(str(self.path) + ".badtail").exists())

    def test_garbage_tail_is_cut_back(self):
        C.append_gz_line(self.path, json.dumps({"n": 1}))
        with open(self.path, "ab") as f:
            f.write(b"\x00\x01garbage")
        self.assertFalse(C.gz_scan(self.path)[2])
        C.append_gz_line(self.path, json.dumps({"n": 2}))
        self.assertEqual([d["n"] for d in self.lines()], [1, 2])

    def test_large_snapshot_sized_line_roundtrips(self):
        big = {"rows": [{"instrument_name": "BTC-27NOV26-%d-C" % k, "mark_iv": 40.0 + k / 1e6} for k in range(5000)]}
        C.append_gz_line(self.path, json.dumps(big))
        C.append_gz_line(self.path, json.dumps({"rows": []}))
        got = self.lines()
        self.assertEqual(got[0], big)
        self.assertEqual(got[1], {"rows": []})

    def test_reader_on_empty_or_missing_header_file(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"")
        self.assertEqual(list(C.read_gz_lines(self.path)), [])


class AtomicWrite(unittest.TestCase):
    def test_lf_only_and_no_tmp_left(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x" / "a.json"
            C.atomic_write_text(p, "a\nb\n")
            self.assertEqual(p.read_bytes(), b"a\nb\n")
            self.assertEqual([x.name for x in p.parent.iterdir()], ["a.json"])


if __name__ == "__main__":
    unittest.main()
