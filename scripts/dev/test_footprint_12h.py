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


# ---------- multi-tf, large trades, cadence (card footprint-multi-tf-large-trades-cadence-1112) ----------
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

HTML = Path(__file__).resolve().parents[2] / "MyTradingSys" / "tools" / "live_aid" / "live_aid.html"
CAD_JS = Path(__file__).resolve().parents[2] / "MyTradingSys" / "tools" / "live_aid" / "footprint_cadence.js"


def test_tf_boundaries_per_tf():
    assert [fp.TF_MS[t] for t in ("15m", "1h", "2h", "12h")] == [900000, 3600000, 7200000, 43200000]
    t = START + 5 * 3600000 + 37 * 60000 + 5000  # 05:37:05Z
    assert fp.bar_start_of(t, fp.TF_MS["15m"]) == START + 5 * 3600000 + 30 * 60000
    assert fp.bar_start_of(t, fp.TF_MS["1h"]) == START + 5 * 3600000
    assert fp.bar_start_of(t, fp.TF_MS["2h"]) == START + 4 * 3600000
    assert fp.bar_start_of(t, fp.TF_MS["12h"]) == START
    assert fp.bar_start_of(t) == START  # default stays 12h


def test_tf_files_live_in_their_own_dir_and_12h_name_unchanged():
    s = START + 3 * 3600000
    assert fp.bar_path(START).name == "BTCUSDT_2026-11-11_00.json" and fp.bar_path(START).parent.name == "footprint_12h"
    p = fp.bar_path(s, tf="1h")
    assert p.name == "BTCUSDT_2026-11-11_0300.json" and p.parent.name == "footprint_1h"
    assert fp.bar_path(s + 900000, tf="15m").name == "BTCUSDT_2026-11-11_0315.json"


def test_large_trades_p999_pick_on_fixed_list():
    # qty 1..2000, all distinct: linear p99.9 = 1998.001 (index 0.999*1999), so only qty 1999 and 2000 qualify
    n = 2000
    price = [100.0 + i for i in range(n)]
    qty = [float(i + 1) for i in range(n)]
    ibm = [i % 2 == 0 for i in range(n)]  # even index = taker sold; qty 2000 is index 1999 (odd) = buy, qty 1999 index 1998 = sell
    ts = [START + i for i in range(n)]
    lt = fp.large_trades(price, qty, ibm, ts)
    assert lt == [[START + 1999, 2099.0, 2000.0, "buy"], [START + 1998, 2098.0, 1999.0, "sell"]]
    # cap: 50 largest only
    big = fp.large_trades([1.0] * 100, [5.0] * 100, [False] * 100, list(range(100)), q=0.5)
    assert len(big) == 50


def test_bar_record_carries_large_trades_and_tf_end():
    import numpy as np
    n = 2000
    arr = (np.array([100.0 + i % 50 for i in range(n)]), np.array([float(i + 1) for i in range(n)]), np.array([False] * n),
           np.array([START + i for i in range(n)], dtype="int64"), np.arange(n, dtype="int64"))
    one_h = START + 3 * 3600000
    arr = (arr[0], arr[1], arr[2], arr[3] + 3 * 3600000, arr[4])
    rec = fp.build_from_arrays(arr, one_h, "archive", one_h + 4 * 3600000, tf_ms=fp.TF_MS["1h"])
    assert rec["bar_end_ms"] == one_h + 3600000 and rec["partial"] is False and rec["tf"] == "1h"
    assert [t[2] for t in rec["large_trades"]] == [2000.0, 1999.0]


def test_12h_record_keys_unchanged_when_default():
    f = fp.fold(*arrs())
    rec = fp.bar_record(f["rows"], f, START, False, "archive", 1, START, f["n"])
    assert rec["bar_end_ms"] == START + B and rec["slot"] == "00" and "tf" not in rec and "large_trades" not in rec


def test_tf_line_is_one_short_labelled_line():
    bar = {"tf": "15m", "partial": True, "delta": 12.5, "poc": 100.0, "close": 105.0,
           "large_trades": [[1, 101.0, 30.0, "sell"], [2, 102.0, 80.0, "buy"]]}
    line = fp.tf_line("15m", bar)
    assert "\n" not in line and line.startswith("15m footprint (forming):") and "+12.5" in line
    assert "above POC 100" in line and "largest print 80 BTC buy @ 102" in line and "context, not measured" in line
    assert "UNKNOWN" in fp.tf_line("1h", None)


def test_write_js_has_tf_keys(tmp_path):
    bar = {"tf": "1h", "bar_start_ms": START, "partial": False, "delta": -3.0, "poc": 120.0, "close": 110.0, "large_trades": []}
    d = tmp_path / "f1h"
    d.mkdir()
    (d / fp.bar_path(START, tf="1h").name).write_text(json.dumps(bar), encoding="utf-8")
    out = fp.tf_lines(START + 3600000 + 1000, outdirs={"1h": d})
    assert out["1h"]["line"].startswith("1h footprint:") and out["15m"]["line"].startswith("15m footprint: UNKNOWN")


NODE_CAD = r"""
const C = require(process.argv[1]);
const open = Date.UTC(2026, 10, 12, 14, 30), M = 60000;
const at = m => C.cadenceMs(open + m * M, open);
process.stdout.write(JSON.stringify([at(-600), at(-120), at(-121), at(-30), at(-2), at(0), at(15), at(16), at(60), at(121), at(500)]));
"""


def test_cadence_function_follows_operator_schedule():
    node = shutil.which("node")
    if not node:
        import pytest
        pytest.skip("node not on PATH")
    out = subprocess.run([node, "-e", NODE_CAD, str(CAD_JS)], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr[-1500:]
    m = 60000
    # hourly outside, 15 min from -2 h, 1 min from -2..+15 min, 10 min until +2 h, hourly again
    assert json.loads(out.stdout) == [60 * m, 15 * m, 60 * m, 15 * m, 1 * m, 1 * m, 1 * m, 10 * m, 10 * m, 60 * m, 60 * m]


def test_live_aid_has_60s_timer_and_cadence_and_tf_line():
    h = HTML.read_text(encoding="utf-8")
    assert '<script src="footprint_cadence.js"></script>' in h
    assert "fpReload" in h and "setInterval(fpReload, 60000)" in h
    assert "FOOTPRINT_BIAS.tf" in h and "footprint_bias_data.js?" in h
