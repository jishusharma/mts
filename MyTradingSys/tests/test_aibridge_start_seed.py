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
