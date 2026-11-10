"""T06 paper forward (card t06-paper-forward-build-1110): the live, context-only form of the RSI-MA cross trigger.
Fixture: the 2026 BTC 4h csv of test_malkan_level_short.py (closed bars only). No network, no order, no exchange.
Every test needs a real events()/step(): a stub that returns [] fails each of them."""
import json

from MyTradingSys.backtest.layers.rsi import rsi_ma_cross_live as L
from MyTradingSys.backtest.layers.rsi.test_malkan_level_short import load

B4 = load("4h")
N = len(B4)


def batch(side):
    return {B4[i]["t"]: i for i in L.S.events_for(B4, side) if i >= L.MIN_4H - 1}


def incremental():
    """events() fed one closed bar at a time: {(t, side): event} of the newest bar of each feed."""
    out = {}
    for k in range(L.MIN_4H, N + 1):
        for e in L.events(B4[:k]):
            assert e["t"] == B4[k - 1]["t"], "events() must report the newest closed bar only"
            out[(e["t"], e["shadow_side"])] = e
    return out


def test_batch_equals_one_bar_feed():
    inc = incremental()
    for side in L.SIDES:
        b = batch(side)
        assert len(b) >= 10, (side, len(b))
        assert {t for (t, s) in inc if s == side} == set(b)          # no repaint, none missing, none extra


def test_event_is_context_only_alert_shape_and_source_tag():
    inc = incremental()
    assert {s for (_, s) in inc} == {"short", "long"}
    for (t, side), e in inc.items():
        assert "side" not in e and e["collection_only"] is True and e["shadow_side"] == side
        assert e["event"] == L.EVENT[side] and e["target_r"] == 2.5 and e["max_bars"] == 30
        assert (e["stop"] >= e["entry_ref"]) if side == "short" else (e["stop"] <= e["entry_ref"])
        i = next(k for k, b in enumerate(B4) if b["t"] == t)
        win = B4[i - 5:i + 1]
        assert e["stop"] == (max(x["h"] for x in win) if side == "short" else min(x["l"] for x in win))
    assert L.SOURCE == "layer:rsi:rsi_ma_cross"


def test_fail_closed_on_short_or_dirty_history():
    assert L.events([]) == [] and L.events(B4[:L.MIN_4H - 1]) == []
    t = max(t for (t, _) in incremental())
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    good = B4[:i + 1]
    assert L.events(good), "control: the signal bar fires"
    bad = [dict(b) for b in good]
    bad[-3]["c"] = float("nan")
    assert L.events(bad) == []
    bad2 = [dict(b) for b in good]
    bad2[-2]["t"] = bad2[-1]["t"]
    assert L.events(bad2) == []


def test_resolve_matches_study_simulation():
    n_closed = 0
    for side in L.SIDES:
        sims = {x["signal_t"]: x for x in L.S.simulate(B4, L.S.events_for(B4, side), side)}
        for t, i in batch(side).items():
            r = L.resolve(B4, t, side)
            if i == N - 1:
                assert r["status"] == "pending"
            elif t not in sims:
                assert r["status"] == "no_fill"
            else:
                x = sims[t]
                assert (r["entry"], r["stop"], r["t_fill"]) == (x["fill"], x["stop"], x["entry_t"])
                if r["status"] == "closed":
                    n_closed += 1
                    assert abs(r["net_r"] - (x["gross_r"] - L.S.fee_r(x["risk"] / x["fill"] * 1e4))) < 1e-12
                    assert r["exit"] == x["exit_reason"]
                else:
                    assert r["status"] == "open"
    assert n_closed >= 5


def test_step_journals_signal_then_outcome_once(tmp_path):
    jp = tmp_path / "j.jsonl"
    t, side = next((t, s) for (t, s) in sorted(incremental()) if t < B4[N - 40]["t"] and L.resolve(B4, t, s)["status"] == "closed")
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    evs = L.step(B4[:i + 1], str(jp))
    assert [e["t"] for e in evs] == [t]
    L.step(B4[:i + 1], str(jp))                                       # same bar again: no duplicate signal
    rows = [json.loads(x) for x in jp.read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["signal"] and rows[0]["source"] == L.SOURCE
    L.step(B4, str(jp))                                               # later bars exist: the paper trade settles
    L.step(B4, str(jp))
    rows = [json.loads(x) for x in jp.read_text().splitlines()]
    kinds = [r["kind"] for r in rows if (r["t_trigger"], r["side"]) == (t, side)]
    assert kinds == ["signal", "outcome"], kinds
    out = rows[-1] if rows[-1]["kind"] == "outcome" else next(r for r in rows if r["kind"] == "outcome")
    assert out["status"] == "closed" and isinstance(out["net_r"], float)


def test_kill_rule_after_30_losing_trades_stops_alerts(tmp_path):
    jp = tmp_path / "k.jsonl"
    rows = [{"kind": "outcome", "status": "closed", "t_trigger": k, "side": "short", "net_r": -0.1} for k in range(L.KILL_TRADES)]
    jp.write_text("".join(json.dumps(r) + "\n" for r in rows))
    t = max(t for (t, _) in incremental())
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    assert L.step(B4[:i + 1], str(jp)) == []
    assert any(json.loads(x)["kind"] == "kill" for x in jp.read_text().splitlines())
    assert L.kill_status(rows[:-1])["verdict"] == "RUNNING"
    assert L.kill_status(rows[:-1] + [dict(rows[0], net_r=5.0)])["verdict"] == "PAST_30"


def test_no_order_or_auto_trader_path():
    imports = [x for x in open(L.__file__, encoding="utf-8").read().splitlines() if x.startswith(("import ", "from "))]
    assert all(not any(b in x for b in ("auto_trader", "requests", "urllib", "ccxt", "execution")) for x in imports), imports
    assert all("side" not in e for e in incremental().values())
