import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import aibridge_dom


def test_chain_file_budgeted_for_shard_balancer():
    import run_all_tests
    assert run_all_tests.TEST_FILE_SECONDS.get("test_aibridge_chain.py", 0) >= 120


def test_run_page_timeout_scaled_by_env(monkeypatch):
    seen = {}

    def fake_run(*a, **kw):
        seen["t"] = kw.get("timeout")
        raise RuntimeError("stop")
    monkeypatch.setattr(aibridge_dom, "find_browser", lambda: "fake")
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("MTS_BROWSER_TIMEOUT_SCALE", "2")
    try:
        aibridge_dom.run_page("", 1000, timeout=240)
    except RuntimeError:
        pass
    assert seen["t"] == 480
    monkeypatch.setenv("MTS_BROWSER_TIMEOUT_SCALE", "junk")
    try:
        aibridge_dom.run_page("", 1000, timeout=240)
    except RuntimeError:
        pass
    assert seen["t"] == 240
