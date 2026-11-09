"""malkan-level-short-testnet-forward-1109: the live, context-only form of the Malkan level short (div 3-10 close arm, BTC 4h).
Fixtures: the three 2026 BTC csv files of test_malkan_level_short.py (closed bars only). No network, no order, no exchange.
Every test needs a real events()/step(): a stub that returns [] fails each of them."""
import json
import time
from pathlib import Path

from MyTradingSys.backtest.layers.rsi import malkan_level_short as M
from MyTradingSys.backtest.layers.rsi import malkan_level_short_live as L
from MyTradingSys.backtest.layers.rsi.test_malkan_level_short import POINTS, load, near

H4 = 4 * 3600 * 1000
B4, B1D, B1W = load("4h"), load("1d"), load("1w")
N = len(B4)


def batch_arm():
    return M.signals(B4, B1D, B1W, **L.ARM)


def incremental(start=None, layers=None, structure=None):
    """events() fed one closed bar at a time on the growing history: {t_trigger: event} of the newest bar of each feed."""
    kw = {}
    if layers is not None:
        kw["layers"] = layers
    if structure is not None:
        kw["structure"] = structure
    out = {}
    for k in range(start or L.MIN_4H, N + 1):
        for e in L.events(B4[:k], B1D, B1W, **kw):
            assert e["t"] == B4[k - 1]["t"], "events() must report the newest closed bar only"
            out[e["t"]] = e
    return out


def test_arm_is_the_counted_one():
    assert L.ARM["div_window"] == (3, 10) and L.ARM["price_mode"] == "close" and L.ARM["structure"] == "div"
    assert L.ARM["layers"] == M.BASE | {"structure"}
    assert (L.PARAMS_ID, L.KILL_TRADES, L.MIN_4H) == ("malkan_level_short_4h_div3_10_2026-11-09", 30, 400)
    assert (M.TARGET_R, M.MAX_BARS, M.FEE) == (2.0, 60, M.BINANCE_TAKER)


def test_batch_signals_equal_incremental_feed_no_repaint():
    first = B4[L.MIN_4H - 1]["t"]
    batch = {s["t_trigger"]: s for s in batch_arm() if s["t_trigger"] >= first}
    inc = incremental()
    assert len(batch) >= 5 and len(inc) >= len(batch), (len(batch), len(inc))
    last_safe = B4[N - 5]["t"]                          # a fill needs up to 3 later bars: judge triggers with that tail
    assert {t for t in batch if t <= last_safe} <= set(inc)
    assert {t for t in batch if t > last_safe} <= set(inc) | {B4[N - 1]["t"]}
    for t in inc:
        if t <= last_safe and t not in batch:           # a live alert the batch does not trade: it never filled (or is skipped)
            assert L.resolve(B4, B1D, B1W, t)["status"] == "no_fill"
    for t, s in batch.items():
        assert t in inc and inc[t]["t"] == t
        r = L.resolve(B4, B1D, B1W, t)
        assert (r["entry"], r["stop"]) == (s["entry"], s["stop"])          # the paper trade is the batch trade, not a guess


def test_event_is_context_only_alert_shape():
    e = next(iter(incremental(start=N - 400).values()))
    assert e["event"] == "MALKAN_LEVEL_SHORT_DIV3_10" and e["shadow_side"] == "short" and e["collection_only"] is True
    assert "side" not in e                              # no side = the auto-trader cannot map it to an order
    assert e["stop"] > e["entry_ref"] > 0 and e["target_r"] == 2.0 and isinstance(e["full_stack"], bool)


def test_short_htf_history_fails_closed():
    inc = incremental(start=N - 500)
    assert inc, "fixture must carry a signal in its last 500 bars"
    t = max(inc)
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    b4, tc = B4[:i + 1], t + H4
    d = [x for x in B1D if x["t"] + 86400000 <= tc]
    w = [x for x in B1W if x["t"] + 7 * 86400000 <= tc]
    assert [e["t"] for e in L.events(b4, d, w)] == [t]                                 # control: enough HTF -> the signal
    assert L.events(b4, d[-(L.MIN_1D - 1):], w) == []
    assert L.events(b4, d, w[-(L.MIN_1W - 1):]) == []
    assert L.events(b4, [], []) == []
    assert L.events(B4[:L.MIN_4H - 1], d, w) == []                                      # short 4h history too


def test_not_closed_htf_bars_are_never_read():
    t = max(incremental(start=N - 500))
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    b4, tc = B4[:i + 1], t + H4
    d = [x for x in B1D if x["t"] + 86400000 <= tc]
    w = [x for x in B1W if x["t"] + 7 * 86400000 <= tc]
    still_open = dict(d[-1], t=d[-1]["t"] + 86400000, c=d[-1]["c"] * 3)               # a day that has not closed at tc
    assert L.events(b4, d + [still_open], w) == L.events(b4, d, w)
    assert L.events(b4, B1D, B1W) == L.events(b4, d, w)


def test_five_layer_c3_bar_fires_once():
    inc = incremental(layers=M.FULL, structure="either")
    c3 = POINTS["C3"]
    near_c3 = [e for e in inc.values() if abs(e["t"] - c3) <= 3 * H4]
    assert len(near_c3) == 1, [e["t"] for e in near_c3]
    assert near_c3[0]["full_stack"] is True
    assert not any(near([{"t_trigger": e["t"]}], POINTS[k]) for e in inc.values() for k in ("C1", "C2", "V1", "V2"))


def test_resolve_matches_outcome_and_reports_open_then_closed():
    batch = [s for s in batch_arm() if s["j"] + M.MAX_BARS + 1 < N and s["i"] >= L.MIN_4H - 1]
    assert batch
    s = batch[0]
    t = s["t_trigger"]
    want = M.outcome(B4, s["j"], s["entry"], s["stop"])
    r = L.resolve(B4, B1D, B1W, t)
    assert r["status"] == "closed" and r["net_r"] == want["net_r"] and r["exit"] == want["exit"]
    risk = s["stop"] - s["entry"]
    assert abs(r["target"] - (s["entry"] - 2.0 * risk)) < 1e-9 and r["stop"] == s["stop"]
    # one bar after the fill: the trade is still running unless the stop/target already hit
    early = L.resolve(B4[:s["j"] + 1], B1D, B1W, t)
    assert early["status"] in ("open", "closed")
    if want["exit"] == "time":
        assert early["status"] == "open" and "net_r" not in early
    # before the fill bar exists the alert is pending, not a loss
    assert L.resolve(B4[:s["i"] + 1], B1D, B1W, t)["status"] == "pending"
    assert L.resolve(B4[:s["i"] + 1], B1D, B1W, t + 1)["status"] == "unknown"


def _rows(p):
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines()]


def test_step_journals_signal_then_paper_outcome_once(tmp_path):
    jp = tmp_path / "journal.jsonl"
    s = next(s for s in batch_arm() if s["j"] + M.MAX_BARS + 1 < N and s["i"] >= L.MIN_4H - 1)
    t = s["t_trigger"]
    ev = L.step(B4[:s["i"] + 1], B1D, B1W, jp)
    assert [e["t"] for e in ev] == [t]
    assert [r["kind"] for r in _rows(jp)] == ["signal"] and _rows(jp)[0]["t_trigger"] == t
    assert L.step(B4[:s["i"] + 1], B1D, B1W, jp) and len(_rows(jp)) == 1         # same bar polled twice: no second row
    L.step(B4, B1D, B1W, jp)                                                    # later bars: paper outcome appended
    out = [r for r in _rows(jp) if r["kind"] == "outcome" and r["t_trigger"] == t]
    want = M.outcome(B4, s["j"], s["entry"], s["stop"])
    assert len(out) == 1 and out[0]["net_r"] == want["net_r"] and out[0]["exit"] == want["exit"]
    assert {"stop", "target", "entry", "gross_r", "bars"} <= set(out[0])
    n_rows = len(_rows(jp))
    L.step(B4, B1D, B1W, jp)
    assert len(_rows(jp)) == n_rows                                             # closed trades are never re-written
    assert "api" not in json.dumps(_rows(jp)).lower()                          # journal carries market numbers only


def _closed(net):
    return {"kind": "outcome", "t_trigger": 1, "status": "closed", "net_r": net}


def test_kill_rule_30_closed_trades_net_r_le_zero():
    assert L.kill_status([_closed(-1.0)] * 29)["verdict"] == "RUNNING"
    assert L.kill_status([_closed(-1.0)] * 29 + [{"kind": "outcome", "status": "no_fill"}])["verdict"] == "RUNNING"
    assert L.kill_status([_closed(1.0), _closed(-1.0)] * 15)["verdict"] == "KILL"           # exactly 0 = FAIL
    assert L.kill_status([_closed(1.0), _closed(-0.9)] * 15)["verdict"] == "PAST_30"
    k = L.kill_status([_closed(-1.0)] * 30)
    assert k["closed"] == 30 and k["net_r_sum"] == -30.0


def test_step_stops_alerting_after_the_kill(tmp_path):
    jp = tmp_path / "journal.jsonl"
    jp.write_text("".join(json.dumps(_closed(-1.0)) + "\n" for _ in range(30)), encoding="utf-8")
    t = max(incremental(start=N - 500))
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    assert L.step(B4[:i + 1], B1D, B1W, jp) == []
    assert any(r["kind"] == "kill" for r in _rows(jp))


def test_runner_registers_btc_4h_context_only():
    from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
    e = cli.build_default_registry(history_fetch=lambda *a, **k: [])["malkan|level_short|4h"]
    assert (e["tf"], e["params_id"], e["confirm_lag_bars"]) == ("4h", "malkan_level_short_4h_div3_10_2026-11-09", 0)
    assert cli.HIST_NEED_BARS["malkan_ls_4h"] >= 360 + 30 + 8 + M.MAX_BARS + 3      # level lookback + warm-up + window + outcome tail
    assert cli.HIST_NEED_BARS["malkan_ls_1w"] >= 15 + 3                             # weekly RSI(14) + the 3 rows the htf layer reads
    assert e["fn"](B4[:99]) == []                                                   # no history (fetch down): fail closed
    assert "side" not in e and "layer_rules" not in e                               # a registry entry, no order mapping


def test_htf_fetch_is_closed_bars_only_and_fails_closed():
    from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
    day, wk = 86400000, 7 * 86400000
    tc = B4[600]["t"] + H4
    rows = {"1d": B1D, "1w": B1W}

    def page(symbol, iv, start, limit):                  # a Binance-like page: from startTime, includes the still-open bar
        out = [r for r in rows[iv] if r["t"] >= start][:limit]
        return [[r["t"], r["o"], r["h"], r["l"], r["c"], 1, 0, 0, 0, 0.5, 0, 0] for r in out]

    store = cli.HistoryStore(page)
    d = cli.htf_closed(store, "1d", tc, 100)
    w = cli.htf_closed(store, "1w", tc, 30)
    assert d[-1]["t"] + day <= tc < d[-1]["t"] + 2 * day and len(d) == 100
    assert w[-1]["t"] + wk <= tc < w[-1]["t"] + 2 * wk and len(w) == 30
    assert cli.htf_closed(cli.HistoryStore(lambda *a: []), "1d", tc, 100) is None
    assert cli.htf_closed(cli.HistoryStore(lambda *a: (_ for _ in ()).throw(OSError("down"))), "1w", tc, 30) is None
    assert cli.htf_closed(cli.HistoryStore(page), "1d", B1D[0]["t"] + 5 * day, 100) is None      # fewer bars exist than asked


def test_incremental_feed_is_fast_enough_for_the_poll():
    t = max(incremental(start=N - 500))
    i = next(k for k, b in enumerate(B4) if b["t"] == t)
    t0 = time.time()
    out = L.events(B4[:i + 1], B1D, B1W)
    assert len(out) == 1 and time.time() - t0 < 5.0
