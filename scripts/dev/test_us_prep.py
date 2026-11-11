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
LATE = dt.datetime(2026, 11, 5, 21, 30, tzinfo=dt.timezone.utc)
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
    near = lambda x, y: abs(x - y) < 0.01  # noqa: E731
    # exact values, derived independently from the fixture formula _price (not from us_prep)
    pd = btc["prior_day"]
    assert pd["C"] == 80900.0 and pd["H"] == 80905.0 and pd["L"] == 80175.5
    assert pd["value_area"] == {"POC": 80225.0, "VAL": 80200.0, "VAH": 80750.0}
    assert btc["asia"]["H"] == 80905.0 and near(btc["asia"]["L"], 78753.588)
    assert near(btc["london"]["H"], 78759.118) and near(btc["london"]["L"], 77412.412)
    assert btc["asia"]["partial"] is False and btc["london"]["partial"] is False
    assert btc["vwap"] == 79125.18
    want = {"15m": (77214.05, 77987.41, 78760.77), "1h": (77301.98, 79650.94, 81999.89),
            "4h": (78230.68, 79762.79, 81294.89), "1d": (65756.55, 74060.0, 82363.45)}
    for tf, (lo, mid, hi) in want.items():
        bb = btc["bb"][tf]
        assert near(bb["lower"], lo) and near(bb["mid"], mid) and near(bb["upper"], hi), tf
    assert b["context_only"] is True
    # P4: close of the day (21:15Z) is 75.2k
    b4 = up.build_brief("P4", "2026-11-05", fetch=fake_fetch)
    assert abs(b4["btc"]["last"] - 75200.0) < 10.0


def test_fixture_exact_values():
    test_fixture_day_1105()


def _gappy(url):
    """Like fake_fetch but the 11-05 00:100 bar is missing from every 1m page."""
    rows = fake_fetch(url)
    if "klines" in url and "interval=1m" in url:
        gap = int(D0.timestamp() * 1000) + 100 * MIN
        rows = [r for r in rows if r[0] != gap]
    return rows


def test_partial_klines_unknown():
    try:
        up.klines(_gappy, "1m", int(D0.timestamp() * 1000), int(D0.timestamp() * 1000) + 200 * MIN)
        raise AssertionError("gap must raise")
    except ValueError:
        pass
    # truncated tail: source stops after 50 bars of a 200-bar request
    t0 = int(D0.timestamp() * 1000)
    short = lambda url: [r for r in fake_fetch(url) if r[0] < t0 + 50 * MIN]  # noqa: E731
    try:
        up.klines(short, "1m", t0, t0 + 200 * MIN)
        raise AssertionError("short page must raise")
    except ValueError:
        pass
    b = up.build_brief("P2", "2026-11-05", fetch=_gappy)
    assert b["btc"]["asia"] == "UNKNOWN" and b["btc"]["vwap"] == "UNKNOWN" and b["btc"]["last"] == "UNKNOWN"
    assert b["btc"]["london"] != "UNKNOWN"


def test_open_window_partial():
    b = up.build_brief("P1", "2026-11-05", fetch=fake_fetch)  # 09:00Z: London (08-13) still open
    assert b["btc"]["london"]["partial"] is True and b["btc"]["asia"]["partial"] is False
    assert "PARTIAL" in up.render_md(b).split("london H/L")[1].splitlines()[0]
    assert "PARTIAL" not in up.render_md(b).split("asia H/L")[1].splitlines()[0]


def test_p4_pending(tmp_path):
    ledger = [{"id": "S1", "given_utc": "2026-11-05T14:45Z", "end_utc": "2026-11-05T21:00Z", "likely": "DOWN",
               "up": "80000", "down": "76000", "text": "x", "outcome": "", "touched_utc": "", "score": ""}]
    early = dt.datetime(2026, 11, 5, 20, 0, tzinfo=dt.timezone.utc)
    res = up.score_p4("2026-11-05", fetch=fake_fetch, ledger_rows=ledger, outdir=tmp_path, now=early)
    assert res["session"] == "PENDING"
    assert res["scenarios"][0]["outcome"] == "PENDING" and res["scenarios"][0]["score"] == "PENDING"
    assert "PENDING" in up.render_p4_md(res)


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
    res = up.score_p4("2026-11-05", fetch=fake_fetch, ledger_rows=ledger, outdir=tmp_path, now=LATE)
    assert res["phases_found"] == ["P1"] and res["phases_missing"] == ["P2", "P3"]
    assert [s["id"] for s in res["scenarios"]] == ["S1"]
    assert res["scenarios"][0]["outcome"] == "DOWN" and res["scenarios"][0]["score"] == "HIT"
    assert res["session"]["H"] > res["session"]["L"]


def test_p4_scorer_unreachable_is_unknown(tmp_path):
    ledger = [{"id": "S1", "given_utc": "2026-11-05T14:45Z", "end_utc": "2026-11-05T21:00Z", "likely": "DOWN",
               "up": "80000", "down": "76000", "text": "x", "outcome": "", "touched_utc": "", "score": ""}]
    res = up.score_p4("2026-11-05", fetch=dead_fetch, ledger_rows=ledger, outdir=tmp_path, now=LATE)
    assert res["scenarios"][0]["score"] == "UNKNOWN" and res["session"] == "UNKNOWN"


def test_value_area_math():
    va = up.value_area([(110.0, 5.0), (160.0, 5.0), (125.0, 70.0), (135.0, 20.0)], 50.0)
    assert va == {"POC": 125.0, "VAL": 100.0, "VAH": 150.0}
    va2 = up.value_area([(110.0, 40.0), (160.0, 35.0), (210.0, 25.0)], 50.0)
    assert va2["POC"] == 125.0 and va2["VAL"] == 100.0 and va2["VAH"] == 200.0
    assert up.value_area([], 50.0) == "UNKNOWN"


# ---------- Live Aid playbook wiring (us_prep is the daily trigger) ----------
class _R:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def _trees(tmp_path):
    root, main = tmp_path / "wt", tmp_path / "main"
    for d in (root, main):
        (d / up.PLAYBOOK_REL).mkdir(parents=True)
    return root, main


def test_build_playbook_copies_to_main_checkout(tmp_path):
    root, main = _trees(tmp_path)
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        (root / up.PLAYBOOK_REL / "playbook_data.js").write_text('window.PLAYBOOK_DATA = {"day": "2026-11-11"};', encoding="utf-8")
        return _R(0, "playbook 2026-11-11: 3 scenarios")

    line = up.build_playbook(root, run=run, main_root=main)
    assert line.startswith("PLAYBOOK built and copied")
    assert calls and calls[0][-1].endswith("daily_playbook.py")
    assert "2026-11-11" in (main / up.PLAYBOOK_REL / "playbook_data.js").read_text(encoding="utf-8")


def test_build_playbook_fails_soft_and_leaves_main_untouched(tmp_path):
    root, main = _trees(tmp_path)
    old = main / up.PLAYBOOK_REL / "playbook_data.js"
    old.write_text("OLD", encoding="utf-8")
    assert up.build_playbook(root, run=lambda cmd, **kw: _R(1, "", "Traceback\nURLError: dns"), main_root=main) == "PLAYBOOK FAILED: exit 1: URLError: dns"

    def boom(cmd, **kw):
        raise OSError("no python")

    assert up.build_playbook(root, run=boom, main_root=main).startswith("PLAYBOOK FAILED: OSError")
    # exit 0 without a data file is a failure too (fail closed), and a stale copy is never overwritten by nothing
    assert up.build_playbook(root, run=lambda cmd, **kw: _R(0), main_root=main).startswith("PLAYBOOK FAILED")
    assert old.read_text(encoding="utf-8") == "OLD"


def test_build_playbook_without_main_checkout_says_so(tmp_path):
    root, _main = _trees(tmp_path)

    def run(cmd, **kw):
        if cmd[0] == "git":
            return _R(128, "", "not a git repository")
        (root / up.PLAYBOOK_REL / "playbook_data.js").write_text("x", encoding="utf-8")
        return _R(0)

    assert "main checkout not found" in up.build_playbook(root, run=run)


def test_main_runs_playbook_on_p1_to_p3_not_p4(tmp_path, monkeypatch, capsys):
    seen = []
    monkeypatch.setattr(up, "build_brief", lambda phase, date: {"phase": phase, "date": date})
    monkeypatch.setattr(up, "write_brief", lambda b: tmp_path / "x.md")
    monkeypatch.setattr(up, "render_md", lambda b: "brief")
    monkeypatch.setattr(up, "render_p4_md", lambda res: "score")
    monkeypatch.setattr(up, "score_p4", lambda date: {})
    monkeypatch.setattr(up, "OUTDIR", tmp_path)
    monkeypatch.setattr(up, "build_playbook", lambda: seen.append(1) or "PLAYBOOK built: t")
    for ph in ("P1", "P2", "P3"):
        up.main(["--phase", ph, "--date", "2026-11-11"])
    assert len(seen) == 3 and "PLAYBOOK built: t" in capsys.readouterr().out
    up.main(["--phase", "P4", "--date", "2026-11-11"])
    assert len(seen) == 3
