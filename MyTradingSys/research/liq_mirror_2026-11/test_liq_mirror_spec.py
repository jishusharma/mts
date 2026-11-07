"""Spec tests for liq_mirror.py, written from its docstring contract (not the code body).
Contract: flush = >= MIN_EVENTS(3) same-side events, gaps <= GAP_MS(5 min); reversal = after the flush's last event the
price reaches ref*(1 -/+ 0.5%) the opposite way within HOLD_MS(60 min) before extending 0.5% further the flush way;
no later event in HOLD_MS = unresolved, not reversed. SELL = long liquidated (price falling). Mirror is idempotent."""
import json, os, sys, tempfile, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liq_mirror as M

MIN = 60_000


def E(side, price, t):
    return {"side": side, "price": float(price), "t": t}


def flush(side, ref=100.0):
    return [E(side, ref, 0), E(side, ref, MIN), E(side, ref, 2 * MIN)]  # last event at 2 min, price ref


def rate(evs):
    return M.base_rate({"X.jsonl": evs})


def test_constants_match_contract():
    assert (M.MIN_EVENTS, M.GAP_MS, M.HOLD_MS, M.MOVE_PCT) == (3, 300_000, 3_600_000, 0.5)


def test_sell_flush_reversal_up_counts_reversed():
    r = rate(flush("SELL") + [E("BUY", 100.6, 10 * MIN)])
    assert (r["n"], r["reversed"], r["unresolved"], r["rate"]) == (1, 1, 0, 1.0)


def test_sell_flush_extension_down_not_reversed():
    r = rate(flush("SELL") + [E("SELL", 99.4, 10 * MIN)])
    assert (r["n"], r["reversed"], r["unresolved"], r["rate"]) == (1, 0, 0, 0.0)


def test_buy_flush_is_mirror_image():
    up = rate(flush("BUY") + [E("BUY", 100.6, 10 * MIN)])    # short flush extends upward: not reversed
    dn = rate(flush("BUY") + [E("SELL", 99.4, 10 * MIN)])    # price falls back: reversed
    assert up["reversed"] == 0 and up["n"] == 1
    assert dn["reversed"] == 1 and dn["n"] == 1


def test_no_later_event_in_hold_is_unresolved():
    r = rate(flush("SELL") + [E("BUY", 100.6, 2 * MIN + 61 * MIN)])  # after HOLD_MS
    assert (r["n"], r["reversed"], r["unresolved"], r["rate"]) == (0, 0, 1, None)


def test_event_exactly_at_hold_boundary_counts():
    r = rate(flush("SELL") + [E("BUY", 100.6, 2 * MIN + 60 * MIN)])  # exactly HOLD_MS later
    assert r["reversed"] == 1 and r["unresolved"] == 0


def test_two_events_is_not_a_flush():
    r = rate([E("SELL", 100, 0), E("SELL", 100, MIN), E("BUY", 101, 5 * MIN)])
    assert (r["n"], r["unresolved"]) == (0, 0)


def test_gap_boundary_5min_joins_6min_splits():
    ok = [E("SELL", 100, 0), E("SELL", 100, 5 * MIN), E("SELL", 100, 10 * MIN), E("BUY", 101, 12 * MIN)]
    assert rate(ok)["n"] == 1
    split = [E("SELL", 100, 0), E("SELL", 100, 6 * MIN), E("SELL", 100, 12 * MIN), E("BUY", 101, 14 * MIN)]
    assert rate(split)["n"] == 0


def test_move_below_threshold_is_unresolved():
    r = rate(flush("SELL") + [E("BUY", 100.4, 10 * MIN)])  # +0.4% < 0.5%
    assert r["unresolved"] == 1 and r["n"] == 0


def test_malformed_lines_skipped_and_sorted():
    with tempfile.TemporaryDirectory() as td:
        _malformed(pathlib.Path(td))


def _malformed(tmp_path):
    p = tmp_path / "A.jsonl"
    p.write_text('not json\n{"side":"SELL","price":"1","eventTime":2000}\n{"side":"BUY"}\n'
                 '{"side":"BUY","price":"2","eventTime":1000}\n', encoding="utf-8")
    d = M.load(str(tmp_path))["A.jsonl"]
    assert [e["t"] for e in d] == [1000, 2000] and d[0]["price"] == 2.0


def test_mirror_appends_only_new_lines():
    with tempfile.TemporaryDirectory() as td:
        _append(pathlib.Path(td))


def _append(tmp_path):
    src, dst = tmp_path / "s", tmp_path / "d"
    src.mkdir()
    f = src / "BTCUSDT.jsonl"
    f.write_text('{"a":1}\n{"a":2}\n', encoding="utf-8")
    assert M.mirror(str(src), str(dst)) == {"BTCUSDT": 2}
    assert M.mirror(str(src), str(dst)) == {"BTCUSDT": 0}
    with open(f, "a", encoding="utf-8") as h:
        h.write('{"a":3}\n')
    assert M.mirror(str(src), str(dst)) == {"BTCUSDT": 1}
    assert (dst / "BTCUSDT.jsonl").read_text(encoding="utf-8") == '{"a":1}\n{"a":2}\n{"a":3}\n'
