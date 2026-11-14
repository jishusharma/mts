import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data_cache  # noqa: E402
import hosts  # noqa: E402


class DataCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = mock.patch.dict(os.environ, {"MTS_DATA_CACHE": self.tmp.name})
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_env_wins_and_second_call_reuses(self):
        calls = []
        a = data_cache.cached("binance/x.npz", lambda: calls.append(1) or b"abc")
        b = data_cache.cached("binance/x.npz", lambda: calls.append(1) or b"zzz")
        self.assertEqual(a, b)
        self.assertEqual(Path(self.tmp.name).resolve(), a.parent.parent.resolve())
        self.assertEqual(a.read_bytes(), b"abc")
        self.assertEqual(len(calls), 1)

    def test_failed_producer_leaves_no_partial_file(self):
        def boom():
            raise RuntimeError("net")
        with self.assertRaises(RuntimeError):
            data_cache.cached("y.npz", boom)
        self.assertEqual(list(Path(self.tmp.name).rglob("*")), [])

    def test_no_traversal(self):
        with self.assertRaises(ValueError):
            data_cache.cache_path("../evil")

    def test_host_row_default(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MTS_DATA_CACHE")
            with mock.patch.object(hosts, "HOST_PATHS", {"JIS-DESKTOP": {"data_cache": r"F:\MTS\data_cache"}}), \
                    mock.patch.object(hosts, "this_host", return_value="JIS-DESKTOP"), \
                    mock.patch("os.name", "nt"), mock.patch("os.path.isdir", return_value=True):   # a drive letter counts only on Windows
                self.assertEqual(hosts.data_cache_dir(), r"F:\MTS\data_cache")
            with mock.patch.object(hosts, "this_host", return_value="JIS-NUC"):
                self.assertIsNone(hosts.data_cache_dir())


if __name__ == "__main__":
    unittest.main()
