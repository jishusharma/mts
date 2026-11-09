import sys; sys.dont_write_bytecode = True
"""POST /seed on the AIBridge agent (card aibridge-start-dsa-trigger-1107, spec MyTradingSys/system/SPEC_START_DSA_TRIGGER.md).

The extension swaps the typed phrase "Start DSA bridge" for the seed it gets here. The route: same origin and token check as /run (token in
the X-AIBridge-Token header), runs `<python> scripts/dev/dsa.py start --print` in the repo root, returns text/plain. A fake python (a .cmd that
echoes its arguments) stands in for the real one, so the test pins the exact command line without running dsa.py. Windows PowerShell only.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aibridge_scratch import Scratch  # noqa: E402

pytestmark = pytest.mark.skipif(os.name != "nt", reason="the agent is Windows PowerShell")


@pytest.fixture(scope="module")
def agent(tmp_path_factory):
    d = tmp_path_factory.mktemp("fakepy")
    (d / "repo").mkdir()
    fake = d / "fakepy.cmd"
    fake.write_text("@echo off\r\necho FAKESEED cwd=%CD% args=%*\r\n", newline="")
    s = Scratch(extra_config={"repo_root": str(d / "repo"), "seed_python": str(fake)})
    s.fakerepo = str(d / "repo")
    yield s
    s.close()


def test_seed_without_token_is_refused(agent):
    st, ct, body = agent.post_text("/seed")
    assert st == 403 and "FAKESEED" not in body, (st, body)


def test_seed_with_wrong_token_is_refused(agent):
    st, ct, body = agent.post_text("/seed", {"X-AIBridge-Token": "nope"})
    assert st == 403 and "FAKESEED" not in body, (st, body)


def test_get_seed_is_refused(agent):
    st, ct, body = agent.get_text("/seed", {"X-AIBridge-Token": agent.token})
    assert st != 200 and "FAKESEED" not in body, (st, body)


def test_seed_post_without_origin_is_refused_bad_origin(agent):
    st, ct, body = agent.post_text("/seed", {"X-AIBridge-Token": agent.token}, origin=False)
    assert st == 403 and "bad_origin" in body and "FAKESEED" not in body, (st, body)


def test_seed_with_wrong_origin_is_refused(agent):
    st, ct, body = agent.post_text("/seed", {"X-AIBridge-Token": agent.token, "Origin": "https://evil.example"})
    assert st == 403 and "FAKESEED" not in body, (st, body)


def test_seed_runs_dsa_start_print_in_the_repo_root_and_returns_plain_text(agent):
    st, ct, body = agent.post_text("/seed", {"X-AIBridge-Token": agent.token}, timeout=60)
    assert st == 200, (st, body)
    assert ct.startswith("text/plain"), ct
    assert "FAKESEED" in body
    assert "scripts/dev/dsa.py start --print" in body, body
    assert os.path.normcase(agent.fakerepo) in os.path.normcase(body), body


def test_token_never_appears_in_the_audit_log(agent):
    agent.post_text("/seed", {"X-AIBridge-Token": agent.token})
    for p in Path(agent.work).rglob("*"):
        if p.is_file() and p.suffix in (".log", ".jsonl"):
            assert agent.token not in p.read_text(encoding="utf-8", errors="replace"), p


def test_seed_leaves_one_audit_row(agent):
    agent.post_text("/seed", {"X-AIBridge-Token": agent.token})
    rows = (Path(agent.sdir) / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert any("SEED" in r for r in rows), rows[-3:]


def _fake_py(tmp_path):
    fake = tmp_path / "fakepy.cmd"
    fake.write_text("@echo off\r\necho FAKESEED cwd=%CD% args=%*\r\n", newline="")
    return fake


def test_stale_repo_root_falls_back_to_a_current_sibling_worktree(tmp_path):
    import subprocess
    repo = tmp_path / "main"
    repo.mkdir()
    g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    g("init", "-q")
    (repo / "README").write_text("x")
    g("add", "README")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    wt = tmp_path / "wt"
    g("worktree", "add", "-q", str(wt))
    (wt / "scripts" / "dev").mkdir(parents=True)
    (wt / "scripts" / "dev" / "dsa.py").write_text("# start [--open] [--print]\n")
    s = Scratch(extra_config={"repo_root": str(repo), "seed_python": str(_fake_py(tmp_path))})
    try:
        st, ct, body = s.post_text("/seed", {"X-AIBridge-Token": s.token}, timeout=60)
        assert st == 200 and os.path.normcase(str(wt)) in os.path.normcase(body), (st, body)
    finally:
        s.close()


def test_seed_root_in_config_wins(tmp_path):
    root = tmp_path / "cur"
    root.mkdir()
    s = Scratch(extra_config={"repo_root": str(tmp_path), "seed_root": str(root), "seed_python": str(_fake_py(tmp_path))})
    try:
        st, ct, body = s.post_text("/seed", {"X-AIBridge-Token": s.token}, timeout=60)
        assert st == 200 and os.path.normcase(str(root)) in os.path.normcase(body), (st, body)
    finally:
        s.close()
