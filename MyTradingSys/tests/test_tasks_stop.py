"""C3: tasks.py next hides, take refuses and brief opens with STOP for cards whose STATE is SHIPPED or STALE. In-process."""
import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import tasks  # noqa: E402

TAGS = {"shipped": "SHIPPED@abc1234", "stale": "STALE:scope changed", "fine": "READY"}


def card(cid):
    return {"id": cid, "title": cid, "state": "ready", "lane": "SONNET", "size": "S", "prio": 2}


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setattr(tasks, "open_claims", lambda repo: {})
    monkeypatch.setattr(tasks, "registry", lambda repo: {})
    monkeypatch.setattr(tasks.TS, "state_tag", lambda c, repo, claim=None, reg=None: TAGS[c["id"]])
    monkeypatch.setattr(tasks.TS, "latest_block", lambda c, repo, tag: [f"STATE {tag}"])
    monkeypatch.setattr(tasks, "ready_cards", lambda repo=None, lane=None: ([card(i) for i in TAGS], {}))
    monkeypatch.setattr(tasks, "get", lambda repo, i: card(i))
    monkeypatch.setattr(tasks, "problems", lambda *a, **k: [])
    monkeypatch.setattr(tasks, "brief", lambda c: f"TASK {c['id']}")


def test_next_hides_shipped_and_stale(env, capsys):
    tasks.cmd_next(argparse.Namespace(lane=None, all=False, n=10))
    out = capsys.readouterr().out
    assert "fine " in out and "shipped" not in out and "stale" not in out


def test_take_refuses_shipped_and_stale(env):
    for cid in ("shipped", "stale"):
        with pytest.raises(SystemExit) as e:
            tasks.cmd_take(argparse.Namespace(id=cid, claim=""))
        assert "STATE" in str(e.value)


def test_brief_opens_with_stop(env, capsys):
    tasks.cmd_brief(argparse.Namespace(id="shipped"))
    assert capsys.readouterr().out.splitlines()[0].startswith("STOP: STATE SHIPPED@abc1234")
    tasks.cmd_brief(argparse.Namespace(id="fine"))
    assert "STOP" not in capsys.readouterr().out
