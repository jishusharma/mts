"""Tests for c30_paper_log.py: synthetic 15m bars only (no F:/ paths, no network)."""
import importlib.util
import json
import math
import random
import sys
import pytest
from pathlib import Path

_p = Path(__file__).resolve().parent / "c30_paper_log.py"
_s = importlib.util.spec_from_file_location("c30_paper_log_t", _p)
P = importlib.util.module_from_spec(_s)
sys.modules["c30_paper_log_t"] = P
_s.loader.exec_module(P)

N = 2450


def gen(seed=25, n=N):
    r = random.Random(seed)
    p, v, out = 60000.0, 0.0, []
    t0 = 1700000100000 // 900000 * 900000
    for k in range(n):
        v = 0.97 * v + r.gauss(0, 0.0012) + 0.0003 * math.sin(k / 180)
        o = p
        c = o * (1 + v + r.gauss(0, 0.0015))
        h = max(o, c) * (1 + abs(r.gauss(0, 0.0007)))
        lo = min(o, c) * (1 - abs(r.gauss(0, 0.0007)))
        out.append(dict(t=t0 + k * 900000, o=o, h=h, l=lo, c=c))
        p = c
    return out


BARS = gen()


def run_stepwise(path, bars=BARS):
    for j in range(P.MIN_BARS, len(bars) + 1):
        P.step(bars[:j], str(path))
    return P._read(path)


def batch_reference(bars):
    b, w1, w2, R, tr = P._series(bars)
    O, T = [x[1] for x in b], [x[0] for x in b]
    sigs, trades, busy = [], {}, -1
    for i in range(P.MIN_BARS - 1, len(b)):
        if i > busy and P.fires(b, w1, w2, R, tr, i):
            sigs.append(T[i])
            r = P.V.forward_trade(O, w1, w2, tr, i, 1, 0, True, T)
            if r:
                trades[T[i]] = r["net"]
                busy = i + r["bars"]
    return sigs, trades


@pytest.fixture(scope="module")
def full(tmp_path_factory):
    path = tmp_path_factory.mktemp("c30") / "full.jsonl"
    return path, run_stepwise(path)


def test_batch_equals_one_bar_at_a_time(full):
    rows = full[1]
    sigs, trades = batch_reference(BARS)
    assert len(sigs) >= 2
    assert [r["t_trigger"] for r in rows if r["kind"] == "signal"] == sigs
    outs = {r["t_trigger"]: r for r in rows if r["kind"] == "outcome"}
    assert outs, "fixture must settle at least one trade"
    for t, r in outs.items():
        assert abs(r["net_pct"] - trades[t]) < 1e-9
        assert r["source"] == "layer:wt:c30_h2_long" and r["side"] == "long" and math.isfinite(r["net_r"])
        assert r["why"] in ("X1", "trend flip", "cap")


def test_rerun_writes_no_duplicate(full):
    path, rows = full
    again = P.step(BARS, str(path))
    assert again == [] and P._read(path) == rows
    keys = [(r["kind"], r["t_trigger"]) for r in rows if r["kind"] != "kill"]
    assert len(keys) == len(set(keys))


def test_restart_resumes_from_journal(tmp_path, full):
    b = tmp_path / "b.jsonl"
    mid = P.MIN_BARS + 250
    for j in range(P.MIN_BARS, mid):
        P.step(BARS[:j], str(b))          # first process dies here
    for j in range(mid, len(BARS) + 1):    # restart: same journal file
        P.step(BARS[:j], str(b))
    assert P._read(b) == full[1]


def test_bad_data_fails_closed(tmp_path):
    path = tmp_path / "j.jsonl"
    short = BARS[:P.MIN_BARS - 1]
    gap = BARS[:P.MIN_BARS + 5]; gap = gap[:100] + gap[101:]
    nan = [dict(x) for x in BARS[:P.MIN_BARS + 5]]; nan[500]["c"] = float("nan")
    inf = [dict(x) for x in BARS[:P.MIN_BARS + 5]]; inf[300]["h"] = float("inf")
    neg = [dict(x) for x in BARS[:P.MIN_BARS + 5]]; neg[300]["l"] = -1.0
    for bad in (short, gap, nan, inf, neg, [], None):
        assert P.step(bad, str(path)) == []
    assert not path.exists()


def test_fetch_error_fails_closed(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise OSError("down")
    monkeypatch.setattr(P.urllib.request, "urlopen", boom)
    path = tmp_path / "j.jsonl"
    assert P.main(["--once", "--journal", str(path)]) == 2 and not path.exists()
    assert P.main(["--once", "--journal", str(path), "--history-warmup", "100"]) == 2


def test_kill_after_30_losing_trades(tmp_path):
    path = tmp_path / "j.jsonl"
    seed_rows = [{"kind": "outcome", "t": k, "t_trigger": k - 1, "t_exit_bar": k, "side": "long", "status": "closed",
                  "net_r": -0.1, "source": P.SOURCE, "params_id": P.PARAMS_ID} for k in range(1, 31)]
    path.write_text("".join(json.dumps(r) + "\n" for r in seed_rows))
    new = P.step(BARS[:P.MIN_BARS], str(path))
    assert [r["kind"] for r in new] == ["kill"] and new[0]["verdict"] == "KILL" and new[0]["closed"] == 30
    assert P.step(BARS[:P.MIN_BARS], str(path)) == []     # one kill row only
    assert P.kill_status(seed_rows[:29])["verdict"] == "RUNNING"
    assert P.kill_status([dict(r, net_r=0.2) for r in seed_rows])["verdict"] == "PAST_30"


def test_clean_rejects_bad_bars():
    ok = BARS[:50]
    assert P.clean(ok)
    assert not P.clean(ok[:10] + ok[11:])                                  # gap
    assert not P.clean([dict(x, c=float("nan")) if k == 5 else x for k, x in enumerate(ok)])
    assert not P.clean([dict(x, h=float("inf")) if k == 5 else x for k, x in enumerate(ok)])
    assert not P.clean([dict(x, l=0.0) if k == 5 else x for k, x in enumerate(ok)])
    assert not P.clean([dict(x, h=x["l"] * 0.5) if k == 5 else x for k, x in enumerate(ok)])
