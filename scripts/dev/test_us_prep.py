"""us_prep tests (card us-session-prep-1106). Network is injected: no test touches the internet."""
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import us_prep as up  # noqa: E402  (fails with ImportError before the module exists)

MIN = 60_000
D0 = dt.datetime(2026, 11, 5, tzinfo=dt.timezone.utc)
IV_MS = {"1m": MIN, "15m": 15 * MIN, "1h": 60 * MIN, "4h": 240 * MIN, "1d": 1440 * MIN}


def _price(ms):
    """Prior day 11-04 flat at 80900 (close 80900); 11-05 falls linearly 80900 -> 75200 by 21:15Z, flat after."""
    t = (ms - D0.timestamp() * 1000) / MIN
    if t < 0:
        return 80900.0 + (t + 1) * 0.5
    return 80900.0 - 5700.0 * min(t, 1275) / 1275


def fake_fetch(url):
    u = urlparse(url)
    q = parse_qs(u.query)
    if "finance/chart" in url:
        sym = u.path.rsplit("/", 1)[-1]
        data = {"NQ%3DF": (25000 * 0.994, 25000), "%5EKS11": (2500 * 0.947, 2500), "%5EVIX": (21.0, 19.0)}
        if sym not in data:
            sym = sym.replace("=", "%3D").replace("^", "%5E")
        p, v = data.get(sym, (100.0, 100.0))
        return {"chart": {"result": [{"meta": {"regularMarketPrice": p, "chartPreviousClose": v}}]}}
    if "klines" in url:
        iv, step = q["interval"][0], IV_MS[q["interval"][0]]
        t0, t1, lim = int(q["startTime"][0]), int(q["endTime"][0]), int(q.get("limit", ["1000"])[0])
        t = (t0 // step) * step
        rows = []
        while t < t1 and len(rows) < lim:
            o, c = _price(t), _price(t + step - MIN)
            rows.append([t, str(o), str(max(o, c) + 5), str(min(o, c) - 5), str(c), "10.0", t + step - 1])
            t += step
        return rows
    raise OSError("unreachable: " + url)


def dead_fetch(url):
    raise OSError("source unreachable")


def _numbers(x):
    if isinstance(x, bool):
        return []
    if isinstance(x, (int, float)):
        return [x]
    if isinstance(x, dict):
        return [n for v in x.values() for n in _numbers(v)]
    if isinstance(x, list):
        return [n for v in x for n in _numbers(v)]
    return []


def test_fixture_day_1105():
    b = up.build_brief("P2", "2026-11-05", fetch=fake_fetch)
    m = b["macro"]
    assert m["flag"] == "ON"
    assert abs(m["kospi_pct"] - (-5.3)) < 0.01 and abs(m["nq_pct"] - (-0.6)) < 0.01
    assert len(m["reasons"]) == 2
    btc = b["btc"]
    assert btc["prior_day"]["C"] == 80900.0
    assert btc["prior_day"]["H"] > btc["prior_day"]["C"] > btc["prior_day"]["L"]
    va = btc["prior_day"]["value_area"]
    assert va["VAL"] <= va["POC"] <= va["VAH"]
    assert btc["asia"]["H"] > btc["asia"]["L"]
    assert btc["london"]["H"] > btc["london"]["L"]
    assert btc["vwap"] < 80900.0
    for tf in ("15m", "1h", "4h", "1d"):
        bb = btc["bb"][tf]
        assert bb["lower"] < bb["mid"] < bb["upper"]
    assert b["context_only"] is True
    # P4: close of the day (21:15Z) is 75.2k
    b4 = up.build_brief("P4", "2026-11-05", fetch=fake_fetch)
    assert abs(b4["btc"]["last"] - 75200.0) < 10.0


def test_unknown_fail_closed():
    b = up.build_brief("P2", "2026-11-05", fetch=dead_fetch)
    assert b["macro"]["flag"] == "UNKNOWN"
    assert b["macro"]["nq_pct"] == "UNKNOWN" and b["macro"]["kospi_pct"] == "UNKNOWN"
    assert b["btc"]["prior_day"] == "UNKNOWN" and b["btc"]["vwap"] == "UNKNOWN"
    assert b["btc"]["bb"]["1h"] == "UNKNOWN"
    assert b["derivs"]["funding"] == "UNKNOWN" and b["derivs"]["liquidations"] == "UNKNOWN"
    assert b["econ"] == "UNKNOWN"
    assert _numbers({k: b[k] for k in ("macro", "btc", "derivs", "econ")}) == []


def test_p4_scorer_and_write(tmp_path):
    ledger = [
        {"id": "S1", "given_utc": "2026-11-05T14:45Z", "end_utc": "2026-11-05T21:00Z", "likely": "DOWN",
         "up": "80000", "down": "76000", "text": "x", "outcome": "", "touched_utc": "", "score": ""},
        {"id": "S2", "given_utc": "2026-11-04T14:45Z", "end_utc": "2026-11-04T21:00Z", "likely": "UP",
         "up": "1", "down": "0", "text": "other day", "outcome": "", "touched_utc": "", "score": ""},
    ]
    b1 = up.build_brief("P1", "2026-11-05", fetch=fake_fetch)
    up.write_brief(b1, tmp_path)
    assert (tmp_path / "2026-11-05_P1.json").exists() and (tmp_path / "2026-11-05_P1.md").exists()
    res = up.score_p4("2026-11-05", fetch=fake_fetch, ledger_rows=ledger, outdir=tmp_path)
    assert res["phases_found"] == ["P1"] and res["phases_missing"] == ["P2", "P3"]
    assert [s["id"] for s in res["scenarios"]] == ["S1"]
    assert res["scenarios"][0]["outcome"] == "DOWN" and res["scenarios"][0]["score"] == "HIT"
    assert res["session"]["H"] > res["session"]["L"]


def test_p4_scorer_unreachable_is_unknown(tmp_path):
    ledger = [{"id": "S1", "given_utc": "2026-11-05T14:45Z", "end_utc": "2026-11-05T21:00Z", "likely": "DOWN",
               "up": "80000", "down": "76000", "text": "x", "outcome": "", "touched_utc": "", "score": ""}]
    res = up.score_p4("2026-11-05", fetch=dead_fetch, ledger_rows=ledger, outdir=tmp_path)
    assert res["scenarios"][0]["score"] == "UNKNOWN" and res["session"] == "UNKNOWN"


def test_value_area_math():
    va = up.value_area([(110.0, 5.0), (160.0, 5.0), (125.0, 70.0), (135.0, 20.0)], 50.0)
    assert va == {"POC": 125.0, "VAL": 100.0, "VAH": 150.0}
    va2 = up.value_area([(110.0, 40.0), (160.0, 35.0), (210.0, 25.0)], 50.0)
    assert va2["POC"] == 125.0 and va2["VAL"] == 100.0 and va2["VAH"] == 200.0
    assert up.value_area([], 50.0) == "UNKNOWN"
