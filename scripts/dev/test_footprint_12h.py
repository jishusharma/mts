"""Tests for footprint_12h.py on a small synthetic trade set (numbers worked out by hand below)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import footprint_12h as fp  # noqa: E402

B = fp.HALF_MS
START = 1794355200000  # 2026-11-11 00:00Z
# price, qty, is_buyer_maker (True = taker sold). $10 rows.
T = [
    (100.0, 2.0, False),  # row 100: buy 2
    (104.0, 1.0, True),   # row 100: sell 1
    (110.0, 1.0, False),  # row 110: buy 1
    (111.0, 5.0, True),   # row 110: sell 5
    (120.0, 8.0, False),  # row 120: buy 8
    (121.0, 2.0, True),   # row 120: sell 2
    (130.0, 1.0, False),  # row 130: buy 1
    (139.9, 1.0, True),   # row 130: sell 1
]


def arrs():
    return ([t[0] for t in T], [t[1] for t in T], [t[2] for t in T])


def rows():
    return fp.fold(*arrs())["rows"]


def test_bucket_sums_and_sign():
    r = rows()
    assert r == {10000: [2.0, 1.0], 11000: [1.0, 5.0], 12000: [8.0, 2.0], 13000: [1.0, 1.0]}


def test_delta_sign_buyer_maker_is_sell():
    f = fp.fold([100.0], [3.0], [True])["rows"]
    assert f[10000] == [0.0, 3.0]
    f = fp.fold([100.0], [3.0], [False])["rows"]
    assert f[10000] == [3.0, 0.0]


def test_poc_and_value_area():
    pv = fp.poc_va(rows())
    assert pv["poc"] == 120.0  # total 10 is the max (rows: 3, 6, 10, 2)
    # total 21, 70 % = 14.7: POC 10, up 2 vs down 6 -> add 110 (16 >= 14.7) -> area 110..120
    assert (pv["va_low"], pv["va_high"]) == (110.0, 120.0)
    assert abs(pv["va_share"] - 16 / 21) < 1e-3


def test_stacked_imbalance_needs_three_rows():
    # buys 5,5,5,5 over sells 0.5 one row below: rows 2..4 buy-imbalanced (diagonal), stack of 3
    p = [100, 110, 120, 130]
    q_buy = [0.5, 5, 5, 5]
    price, qty, ibm = [], [], []
    for pr, qb in zip(p, q_buy):
        price += [pr, pr]; qty += [qb, 0.5]; ibm += [False, True]
    st = fp.stacked_imbalances(fp.fold(price, qty, ibm)["rows"])
    assert st == [{"side": "buy", "low": 110.0, "high": 140.0, "rows": 3}]
    # only two imbalanced rows -> no stack
    assert fp.stacked_imbalances(fp.fold(price[:6], qty[:6], ibm[:6])["rows"]) == []


def test_absorptions_edges():
    a = fp.absorptions(rows(), edge=0.5, top=5)
    assert a[0]["price"] == 120.0 and a[0]["kind"] == "sellers absorbed buying" and a[0]["vol"] == 8.0
    assert a[1]['price'] == 110.0 and a[1]['kind'] == 'buyers absorbed selling' and a[1]['vol'] == 5.0 and len(a) == 4


def test_bar_record_totals():
    f = fp.fold(*arrs())
    rec = fp.bar_record(f["rows"], f, START, False, "archive", 1, START, f["n"])
    assert rec["buy_vol"] == 12.0 and rec["sell_vol"] == 9.0 and rec["delta"] == 3.0
    assert rec["poc"] == 120.0 and rec["open"] == 100.0 and rec["close"] == 139.9 and rec["slot"] == "00"


def _fake_pages(trades):
    def page(p):
        i = p.get("fromId")
        out = [t for t in trades if (i is None or t["a"] >= i) and (i is not None or t["T"] >= p["startTime"])]
        return out[:p["limit"]]
    return page


def test_idempotent_rerun_and_partial_resume():
    import numpy as np
    trades = [{"a": 10 + i, "p": str(p), "q": str(q), "m": m, "T": START + 1000 * i} for i, (p, q, m) in enumerate(T)]
    page = _fake_pages(trades)
    with tempfile.TemporaryDirectory() as d:
        now = START + 5000  # bar still forming, 6 trades seen
        arr, complete = fp.rest_trades(START, START + B, page=lambda p: [t for t in page(p) if t["T"] <= now], clock=lambda s: None)
        rec = fp.build_from_arrays(arr, START, "rest", now, complete_hint=complete)
        assert rec["partial"] is True and rec["trades"] == 6
        fp.save_bar(rec, d)
        assert fp.needs_build(START, now, d)  # partial -> rebuild
        # resume after the last id: only the remaining two trades come, rows are added
        arr2, c2 = fp.rest_trades(START, START + B, rec["last_agg_id"], page=page, clock=lambda s: None)
        rec2 = fp.build_from_arrays(arr2, START, "rest", START + B + 1, complete_hint=True, prior=fp.load_bar(START, d))
        assert rec2["trades"] == 8 and rec2["delta"] == 3.0 and rec2["partial"] is False
        fp.save_bar(rec2, d)
        assert not fp.needs_build(START, START + B + 1, d)  # complete -> a rerun builds nothing
        again = fp.ensure(START + B + 1, days=0, outdir=d, rest=False, log=lambda *_: None)
        assert again["built"] == [] or again["built"] == [START + B]  # only the NEXT (not yet started... gap) bar may be tried
        assert fp.load_bar(START, d)["delta"] == 3.0


def test_bias_line_one_line_and_labelled():
    f = fp.fold(*arrs())
    bars = []
    for k, sgn in enumerate((1, -1)):
        rec = fp.bar_record(f["rows"], f, START + k * B, False, "archive", 1, START, f["n"])
        rec["delta"] = 3.0 * sgn
        bars.append(rec)
    inp = fp.us_bias_inputs(now_ms=START + 3 * B, price=115.0, bars=bars)
    line = fp.bias_line(inp)
    assert "\n" not in line and line.startswith("12h footprint: sellers won last bar") and "context, not measured" in line
    assert "below its POC 120" in line
    unk = fp.bias_line(fp.us_bias_inputs(now_ms=START, bars=[]))
    assert "UNKNOWN" in unk
