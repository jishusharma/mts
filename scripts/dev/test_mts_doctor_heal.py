"""O1 self-heal (HEAL_MAP.md): one test per `mts_doctor.py --heal` heal, all failing on the pre-change code (no heal_*
functions, no terminal `expired` ack state in mts_signal). Each heal is safe by construction: idempotent, reversible,
and touching no git history, live tree, runtime data or others' uncommitted files. The injected callables keep every
branch testable without a network or a real push."""
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mts_doctor as D
import mts_signal as S

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
NL = chr(10)
STAMP = NOW - timedelta(hours=72)          # a claim 3 days old (past sync.STALE_HOURS = 24)
FRESH = NOW - timedelta(hours=1)


def _claim(slug, when, host="JIS-NB"):
    return {"task": slug, "host": host, "account": "jishusharma", "area": "-", "epoch": str(int(when.timestamp()))}


def _git(tmp, *a):
    return subprocess.run(["git", "-C", str(tmp), *a], capture_output=True, text=True)


def _make_repo(tmp, cards=()):
    """An offline clone: fast-track carrying a tasks/ dir of cards. `cards` is [(id, state)]."""
    _git(tmp, "init", "-q")
    _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "x")
    td = tmp / "MyTradingSys" / "system" / "tasks"
    td.mkdir(parents=True)
    for cid, state in cards:
        (td / f"{cid}.json").write_text(json.dumps({"id": cid, "state": state}), encoding="utf-8")
    _git(tmp, "add", "-A")
    _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "cards")
    _git(tmp, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    return tmp


# ---- heal 1: release a stale claim only when its work is already shipped (HEAL_MAP.md row STALE-CLAIMS) -------------

def test_heal_releases_a_stale_claim_whose_card_is_done():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _make_repo(tmp, cards=(("shipped-card", "done"),))
        released = []
        got = D.heal_release_shipped_claims(tmp, now=NOW, claims=[("shipped-card", _claim("shipped-card", STAMP))],
                                            release_fn=lambda s: released.append(s) or True, git_fn=lambda *a: _git(tmp, *a))
        assert [s for s, _ in got] == ["shipped-card"] and released == ["shipped-card"]


def test_heal_leaves_a_stale_claim_whose_card_is_still_open():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _make_repo(tmp, cards=(("open-card", "ready"),))
        released = []
        got = D.heal_release_shipped_claims(tmp, now=NOW, claims=[("open-card", _claim("open-card", STAMP))],
                                             release_fn=lambda s: released.append(s) or True, git_fn=lambda *a: _git(tmp, *a))
        assert got == [] and released == []            # not shipped: the claim stays with its owner


def test_heal_leaves_a_fresh_claim_alongside_a_shipped_one():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _make_repo(tmp, cards=(("a", "shipped"), ("b", "done")))
        released = []
        claims = [("a", _claim("a", STAMP)), ("b", _claim("b", FRESH))]     # b is under 24 h old: working, not stale
        got = D.heal_release_shipped_claims(tmp, now=NOW, claims=claims,
                                             release_fn=lambda s: released.append(s) or True, git_fn=lambda *a: _git(tmp, *a))
        assert [s for s, _ in got] == ["a"] and released == ["a"]


def test_heal_releases_when_the_claim_host_branch_is_fully_on_trunk():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _make_repo(tmp, cards=())                        # free-form task claim: no card, so the branch check decides
        _git(tmp, "branch", "JIS-NB/free-task", "HEAD")
        _git(tmp, "update-ref", "refs/remotes/origin/JIS-NB/free-task", "HEAD")   # origin/fast-track == this sha: shipped
        released = []
        got = D.heal_release_shipped_claims(tmp, now=NOW, claims=[("free-task", _claim("free-task", STAMP))],
                                             release_fn=lambda s: released.append(s) or True, git_fn=lambda *a: _git(tmp, *a))
        assert [s for s, _ in got] == ["free-task"] and released == ["free-task"]


def test_heal_does_not_release_a_branch_still_ahead_of_trunk():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _make_repo(tmp, cards=())
        base = _git(tmp, "rev-parse", "HEAD").stdout.strip()
        _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "work")
        _git(tmp, "update-ref", "refs/remotes/origin/JIS-NB/other-task", "HEAD")
        _git(tmp, "reset", "-q", "--hard", base)          # trunk is behind the branch: not shipped
        released = []
        got = D.heal_release_shipped_claims(tmp, now=NOW, claims=[("other-task", _claim("other-task", STAMP))],
                                             release_fn=lambda s: released.append(s) or True, git_fn=lambda *a: _git(tmp, *a))
        assert got == [] and released == []


# ---- heal 2: expire a HIGH broadcast no host can ack, with a reason (HEAL_MAP.md row BROADCAST) ----------------------

def _brows(hours):
    """One HIGH broadcast pending `hours` on a host last seen 48 h ago (no session: nobody to ack it)."""
    t0 = lambda h: (NOW - timedelta(hours=h)).strftime("%Y%m%dT%H%M%SZ")
    seen = {"t": t0(48), "from": "jis-laptop/C", "to": "all", "kind": "note", "text": "loop"}
    b = {"t": t0(hours), "from": "jis-nuc/C", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-heal01", "cmd": "x"}
    return [b, seen]


def test_heal_expires_a_broadcast_pending_longer_than_its_window():
    sent = []
    out = D.heal_expire_unackable_broadcasts(".", rows=_brows(72), now=NOW,
                                             send_fn=lambda text, extra: sent.append(extra) or True)
    assert any(e.get("state") == "expired" and e.get("host") == "jis-laptop" and e.get("id") == "b-heal01" for e in sent)
    assert any("no session" in e.get("note", "") for e in sent)     # the reason travels in the note


def test_heal_leaves_a_fresh_pending_broadcast_alone():
    sent = []
    out = D.heal_expire_unackable_broadcasts(".", rows=_brows(5), now=NOW,
                                              send_fn=lambda text, extra: sent.append(extra) or True)
    assert out == [] and sent == []                         # under the window: a session may still ack it


def test_heal_leaves_a_broadcast_whose_host_is_still_active():
    sent = []
    rows = _brows(72)
    rows.append({"t": (NOW - timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ"), "from": "jis-laptop/C", "to": "all",
                 "kind": "note", "text": "loop"})            # a session ran there an hour ago: it can still ack
    out = D.heal_expire_unackable_broadcasts(".", rows=rows, now=NOW,
                                             send_fn=lambda text, extra: sent.append(extra) or True)
    assert out == [] and sent == []


def test_expired_ack_quits_the_pending_loop():
    """The point of the heal: once an `expired` ack record exists, mts_signal.pending stops listing the host and the
    BROADCAST check drops to OK. Fails on pre-change mts_signal (no terminal `expired` state: pending() keeps it)."""
    rows = _brows(72) + [{"t": NOW.strftime("%Y%m%dT%H%M%SZ"), "from": "jis-laptop/C", "kind": "ack", "id": "b-heal01",
                         "state": "expired", "host": "jis-laptop", "note": "doctor heal: no session on jis-laptop"}]
    assert S.pending(rows, "jis-laptop", NOW) == []
    assert D.broadcast_check(".", rows=rows, now=NOW)[0] == "OK"


def test_done_ack_still_outranks_expired():
    rows = _brows(72)
    t = NOW.strftime("%Y%m%dT%H%M%SZ")
    rows += [{"t": t, "from": "a", "kind": "ack", "id": "b-heal01", "state": "expired", "host": "jis-laptop"},
             {"t": t, "from": "a", "kind": "ack", "id": "b-heal01", "state": "done", "host": "jis-laptop"}]
    assert S.ack_state(rows, "b-heal01", "jis-laptop") == "done"


# ---- heal 3: the main checkout (where every session's hooks load from) is behind or diverged ---------------------------

def _two_clones(tmp):
    src, main = tmp / "src", tmp / "main"
    src.mkdir()
    _git(src, "init", "-q")
    _git(src, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "one")
    _git(src, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "two")
    _git(src, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "one")
    _git(main, "checkout", "-q", "-B", "fast-track")
    _git(main, "fetch", "-q", str(src), "+refs/heads/" + _git(src, "branch", "--show-current").stdout.strip() + ":refs/remotes/origin/fast-track")
    _git(main, "reset", "-q", "--hard", "origin/fast-track~1")
    return src, main


def test_heal_reports_one_ff_command_when_the_main_checkout_is_behind():
    with tempfile.TemporaryDirectory() as d:
        src, main = _two_clones(Path(d))
        before = _git(main, "rev-parse", "HEAD").stdout.strip()
        lines = D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a))
        assert _git(main, "rev-parse", "HEAD").stdout.strip() == before      # printed, not run: a heal never moves the shared main checkout
        assert any("merge --ff-only origin/fast-track" in l for l in lines)  # the one exact recovery command
        assert any(str(main / ".claude" / "settings.json") in l for l in lines)   # names which hook copy is in use


def test_heal_main_checkout_is_idempotent_and_moves_nothing():
    with tempfile.TemporaryDirectory() as d:
        src, main = _two_clones(Path(d))
        a = D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a))
        b = D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a))
        assert a == b                                                        # a second run reports the same lines (still behind: the command is printed again)


def test_heal_reports_one_command_when_the_main_checkout_is_diverged():
    with tempfile.TemporaryDirectory() as d:
        src, main = _two_clones(Path(d))
        _git(main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "mywork")   # now ahead too
        before = _git(main, "rev-parse", "HEAD").stdout.strip()
        D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a))
        assert _git(main, "rev-parse", "HEAD").stdout.strip() == before     # diverged: printed, not run
        assert any("merge origin/fast-track" in l for l in D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a)))


def test_heal_skips_a_live_tree():
    with tempfile.TemporaryDirectory() as d:
        main = Path(d) / "live"
        main.mkdir()
        _git(main, "init", "-q")
        _git(main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "x")
        (main / ".mts_live").write_text("live", encoding="utf-8")
        lines = D.heal_main_checkout(main, git_fn=lambda *a: _git(main, *a))
        assert any("live" in l.lower() for l in lines)


# ---- the --heal entry point ---------------------------------------------------------------

def test_heal_entry_point_runs_the_three_heals_dry():
    """`--heal --dry-run` names every HEAL row and touches nothing: no release, no signal, main checkout left alone.
    tempfile (not the pytest tmp_path fixture) so the test does not depend on the shared base temp dir, which parallel
    gate runs lock (the repo's own gate uses a per-run --basetemp for the same reason)."""
    with tempfile.TemporaryDirectory() as d:
        tmp_path = Path(d)
        _make_repo(tmp_path, cards=(("shipped-card", "done"),))
        _git(tmp_path, "branch", "JIS-NB/free-task", "HEAD")
        _git(tmp_path, "update-ref", "refs/remotes/origin/JIS-NB/free-task", "HEAD")
        got = D.heal(tmp_path, out_dir=tmp_path / "out", now=NOW, dry_run=True,
                     claims=[("shipped-card", _claim("shipped-card", STAMP)), ("free-task", _claim("free-task", STAMP))],
                     rows=_brows(72), main_checkout=tmp_path)
        assert any("release" in l and "shipped-card" in l for l in got)  # named, but no release_fn ran (dry)
        assert any("expired" in l for l in got)
        assert (tmp_path / "out" / "heal_log.jsonl").exists()           # the audit trail is written even in a dry run
