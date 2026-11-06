"""Pre-US-open risk flag contract (card premarket-risk-flag-1105).
Thresholds are OURS, from the 11-05 case: NQ -0.6%, Kospi -5.3%, BTC 80.4k -> 75.6k."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "premarket_risk.js"


def _utc(h, m):
    day = 1_800_000_000_000 - (1_800_000_000_000 % 86_400_000)
    return day + (h * 60 + m) * 60_000


def _run(expr, payload):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = ("const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(" + expr + "))})")
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps(payload),
                         capture_output=True, text=True, timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _eval(quotes, now):
    return _run("P.evaluate(j.q,j.now)", {"q": quotes, "now": now})


def q(price, prev, **kw):
    d = {"price": price, "prev": prev}
    d.update(kw)
    return d


CASE_1105 = {
    "NQ": q(99.4, 100), "KOSPI": q(94.7, 100), "VIX": q(24.0, 20.0),
    "movers": [q(74, 100, sym="QCOM"), q(97, 100, sym="AVGO"), q(99, 100, sym="NVDA"), q(90, 100, sym="MU")],
}


def test_1105_case_flags_with_both_reasons():
    r = _eval(CASE_1105, _utc(12, 46))
    assert r["flag"] == "ON"
    assert len(r["reasons"]) == 2
    assert r["nq"] == pytest.approx(-0.6) and r["kospi"] == pytest.approx(-5.3)
    assert r["vix"]["price"] == 24.0
    assert [m["sym"] for m in r["movers"]][:2] == ["QCOM", "MU"]  # biggest absolute move first
    assert len(r["movers"]) <= 3


def test_quiet_day_does_not_flag():
    r = _eval({"NQ": q(99.9, 100), "KOSPI": q(99.5, 100), "VIX": q(15, 15), "movers": []}, _utc(12, 46))
    assert r["flag"] == "OFF" and r["reasons"] == []


def test_missing_quote_is_unknown_never_off():
    r = _eval({"NQ": None, "KOSPI": q(99.5, 100), "VIX": None, "movers": []}, _utc(12, 46))
    assert r["flag"] == "UNKNOWN"
    assert _eval({"KOSPI": q(99.5, 100)}, _utc(12, 46))["flag"] == "UNKNOWN"
    assert _eval({}, _utc(12, 46))["flag"] == "UNKNOWN"


@pytest.mark.parametrize("bad", [q("x", 100), q(100, 0), q(None, 100), {"price": 1}])
def test_malformed_quote_is_unknown(bad):
    r = _eval({"NQ": bad, "KOSPI": q(99.5, 100)}, _utc(12, 46))
    assert r["flag"] == "UNKNOWN"


def test_one_side_triggered_flags_even_if_other_missing():
    r = _eval({"NQ": None, "KOSPI": q(96, 100)}, _utc(12, 46))
    assert r["flag"] == "ON" and len(r["reasons"]) == 1


def test_thresholds_are_strict_edges():
    assert _eval({"NQ": q(99.5, 100), "KOSPI": q(97, 100)}, _utc(12, 0))["flag"] == "OFF"
    assert _eval({"NQ": q(99.49, 100), "KOSPI": q(99, 100)}, _utc(12, 0))["flag"] == "ON"
    assert _eval({"NQ": q(100, 100), "KOSPI": q(96.99, 100)}, _utc(12, 0))["flag"] == "ON"


def test_outside_window_is_not_a_calm_off():
    r = _eval({"NQ": q(100, 100), "KOSPI": q(100, 100)}, _utc(14, 30))
    assert r["flag"] == "UNKNOWN" and "window" in r["why"].lower()
    r = _eval({"NQ": q(100, 100), "KOSPI": q(100, 100)}, _utc(14, 29))
    assert r["flag"] == "OFF"


def test_log_appends_once_per_day_and_fills_btc_4h_outcome():
    flag = _eval(CASE_1105, _utc(12, 46))
    t0 = _utc(12, 46)
    expr = "P.logFlag(j.log,j.f,j.t,j.btc)"
    log = _run(expr, {"log": [], "f": flag, "t": t0, "btc": 80400})
    assert len(log) == 1 and log[0]["btc0"] == 80400 and log[0]["btc4h"] is None
    again = _run(expr, {"log": log, "f": flag, "t": t0 + 60_000, "btc": 80300})
    assert len(again) == 1  # same UTC day, no duplicate
    off = _run(expr, {"log": [], "f": {"flag": "OFF", "reasons": []}, "t": t0, "btc": 1})
    assert off == []  # only ON flags are logged
    fill = "P.fillOutcomes(j.log,j.t,j.btc)"
    early = _run(fill, {"log": log, "t": t0 + 3 * 3_600_000, "btc": 76000})
    assert early[0]["btc4h"] is None
    done = _run(fill, {"log": log, "t": t0 + 4 * 3_600_000, "btc": 75600})
    assert done[0]["btc4h"] == 75600
    assert done[0]["btc4hPct"] == pytest.approx(-5.970, abs=0.01)
    assert _run(fill, {"log": log, "t": t0 + 5 * 3_600_000, "btc": None})[0]["btc4h"] is None
