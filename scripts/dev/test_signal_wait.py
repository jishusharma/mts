"""1-minute signals (operator 2026-11-07): `wait` returns on the first new inbound signal, hook status lines are sorted and capped,
the supervisor watcher wakes on a signal. Fake signals clone in a tmp dir: no git, no network, no real sleeps."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mts_signal as S
import supervisor as SUP

ME, OTHER = "h-me", "h-other"


def tstamp(minutes_ago=0):
    return S.stamp(datetime.now(timezone.utc) - timedelta(minutes=minutes_ago))


def put(d, name, **rec):
    rec.setdefault("t", tstamp())
    (d / (rec["t"] + "-" + name + ".json")).write_text(json.dumps(rec), encoding="utf-8", newline="\n")
    return rec


def setup(monkeypatch):
    monkeypatch.setenv("MTS_SIGNALS_HOST", ME)
    monkeypatch.delenv("MTS_ACCOUNT", raising=False)


def test_wait_returns_on_planted_ask_and_times_out_otherwise(tmp_path, monkeypatch):
    setup(monkeypatch)
    since = tstamp(1)
    slept = []
    fetches = []

    def fetch():
        fetches.append(1)
        if len(fetches) == 2:       # the ask lands between the first and the second look
            put(tmp_path, "ask", **{"from": OTHER + "/A", "to": ME, "kind": "ask", "id": "q-abc123", "text": "status?"})
        return tmp_path

    rc, rec, secs = S.wait_signal(10, since=since, poll=60, sleeper=slept.append, fetch=fetch)
    assert rc == 0 and rec["id"] == "q-abc123"
    assert secs == 60 and slept == [60]            # answered within one poll interval, not 10 minutes
    # nothing new: bounded, exit 2, polls once a minute
    slept.clear()
    rc, rec, secs = S.wait_signal(3, since=tstamp(0), poll=60, sleeper=slept.append, fetch=lambda: tmp_path)
    assert (rc, rec) == (2, None) and secs == 180 and slept == [60, 60, 60]


def test_wait_ignores_old_own_and_foreign_signals(tmp_path, monkeypatch):
    setup(monkeypatch)
    put(tmp_path, "old", t=tstamp(30), **{"from": OTHER + "/A", "to": ME, "kind": "ask", "id": "q-old001", "text": "old"})
    put(tmp_path, "own", **{"from": ME + "/A", "to": OTHER, "kind": "ask", "id": "q-own001", "text": "mine"})
    put(tmp_path, "foreign", **{"from": OTHER + "/A", "to": "h-third", "kind": "ask", "id": "q-for001", "text": "not me"})
    put(tmp_path, "note", **{"from": OTHER + "/A", "to": "all", "kind": "note", "text": "chatter"})
    rc, rec, _ = S.wait_signal(0, since=tstamp(0), fetch=lambda: tmp_path, sleeper=lambda s: None)
    assert rc == 2


def test_wait_returns_on_ack_of_my_ask_and_high_broadcast(tmp_path, monkeypatch):
    setup(monkeypatch)
    since = tstamp(2)
    put(tmp_path, "mine", t=tstamp(1), **{"from": ME + "/A", "to": OTHER, "kind": "ask", "id": "q-mine01", "text": "x"})
    assert S.inbound_new(S.load(tmp_path), since) is None
    put(tmp_path, "ack", **{"from": OTHER + "/B", "to": "all", "kind": "ack", "id": "q-mine01", "state": "done", "host": OTHER, "note": "answer"})
    assert S.inbound_new(S.load(tmp_path), since)["kind"] == "ack"
    d2 = tmp_path / "b"
    d2.mkdir()
    put(d2, "hi", **{"from": OTHER + "/A", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-aaaaaa", "text": "go", "cmd": "x"})
    assert S.inbound_new(S.load(d2), since)["id"] == "b-aaaaaa"
    put(d2, "lo", **{"from": OTHER + "/A", "to": "all", "kind": "broadcast", "text": "normal"})   # a normal broadcast does not wake


def test_status_block_orders_asks_then_stuck_high_then_age_and_caps(tmp_path, monkeypatch):
    setup(monkeypatch)
    monkeypatch.setattr(S, "targets", lambda rows, b: {OTHER})
    mk = lambda name, **r: put(tmp_path, name, **r)
    # 5 mixed records, all sent by this host: 2 HIGH (one told fresh = group 2, one none = group 1), 2 asks, 1 more HIGH none
    mk("b1", t=tstamp(50), **{"from": ME + "/A", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-told00", "text": "t", "cmd": "c"})
    mk("a1", t=tstamp(40), **{"from": ME + "/A", "to": OTHER, "kind": "ask", "id": "q-ask001", "text": "a", "wait": 15, "due": 60})
    mk("b2", t=tstamp(30), **{"from": ME + "/A", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-none00", "text": "n", "cmd": "c"})
    mk("a2", t=tstamp(20), **{"from": ME + "/A", "to": OTHER, "kind": "ask", "id": "q-ask002", "text": "b", "wait": 15, "due": 60})
    mk("b3", t=tstamp(10), **{"from": ME + "/A", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-none01", "text": "n2", "cmd": "c"})
    mk("k1", **{"from": OTHER + "/B", "to": "all", "kind": "ack", "id": "b-told00", "state": "told", "host": OTHER, "login": "B"})
    out = S.status_block(S.load(tmp_path)).split("\n")
    assert len(out) == 4                                   # 3 lines + the count line
    assert "q-ask001" in out[0] and "q-ask002" in out[1]   # asks first, oldest first
    assert "b-none00" in out[2]                            # then the HIGH nobody has (b-told00 is parked: last)
    assert out[3].startswith("[MTS status] 2 more") and "acks" in out[3]
    assert "b-told00" not in "\n".join(out[:3])


def test_supervisor_wait_wakes_on_signal_within_one_step(tmp_path):
    seq = iter([None, None, "SIGNAL ask q-x from h-other: hi"])
    sleeps = []
    rc, reason = SUP.wait_for_transition(
        repo=tmp_path, shas=[], timeout=3000, interval=300,
        probe=lambda repo, shas: {"shas": {}, "ci_red": False, "busy_slots": 0},
        fetcher=lambda repo: None, sleeper=sleeps.append, signals=lambda: next(seq))
    assert rc == 0 and reason.startswith("SIGNAL ask")
    assert sleeps == [60, 60, 60]                          # polled every minute, not every 300 s


def test_supervisor_wait_without_signals_keeps_interval(tmp_path):
    sleeps = []
    rc, _ = SUP.wait_for_transition(
        repo=tmp_path, shas=[], timeout=600, interval=300,
        probe=lambda repo, shas: {"shas": {}, "ci_red": False, "busy_slots": 0},
        fetcher=lambda repo: None, sleeper=sleeps.append)
    assert rc == 3 and sleeps == [300, 300]
