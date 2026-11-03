"""ci_fail.py: the log parser is pure and tested offline; the log fetch never forwards the login to the redirect target."""
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_fail as C

LOG = """2026-11-03T16:00:01.1Z collecting ...
2026-11-03T16:00:02.2Z FAILED MyTradingSys/tests/test_a.py::test_x - assert 1 == 2
2026-11-03T16:00:03.3Z ERROR MyTradingSys/tests/test_b.py::test_y
2026-11-03T16:00:04.4Z FAILED MyTradingSys/tests/test_a.py::test_x - assert 1 == 2
2026-11-03T16:00:05.5Z Step 3b: FAIL
2026-11-03T16:00:06.6Z ===== 2 failed, 40 passed in 3s =====
2026-11-03T16:00:07.7Z all good here
"""


def test_parse_failures_keeps_failing_ids_dedups_and_strips_timestamps():
    got = C.parse_failures(LOG)
    assert got == ["FAILED MyTradingSys/tests/test_a.py::test_x - assert 1 == 2",
                   "ERROR MyTradingSys/tests/test_b.py::test_y", "Step 3b: FAIL", "===== 2 failed, 40 passed in 3s ====="]


def test_parse_failures_empty_and_limit():
    assert C.parse_failures("") == [] and C.parse_failures("all passed\n") == []
    many = "\n".join("FAILED t%d" % i for i in range(50))
    assert len(C.parse_failures(many, limit=5)) == 5


def test_redirect_target_gets_no_authorization(monkeypatch):
    seen = []

    class Hdrs(dict):
        pass

    class Opener:
        def open(self, req, timeout=0):
            seen.append(("api", dict(req.header_items())))
            raise urllib.error.HTTPError(req.full_url, 302, "found", Hdrs(Location="https://store.example/log"), None)

    class Resp:
        def read(self):
            return b"FAILED t1"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout=0):
        seen.append(("store", dict(req.header_items())))
        return Resp()

    monkeypatch.setattr(C.ci_watch, "token", lambda: "SECRET")
    monkeypatch.setattr("urllib.request.build_opener", lambda *a: Opener())
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    assert C.fetch_log("https://api.example/logs") == "FAILED t1"
    assert "Bearer SECRET" in seen[0][1].values()
    assert not any(k.lower() == "authorization" for k in seen[1][1])