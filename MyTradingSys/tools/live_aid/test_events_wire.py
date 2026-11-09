"""Upcoming-events strip contract (events_strip.js, events_wire.py; card cbp-events-to-watch-wire-1108).

Context only: the strip gates and sizes nothing. Rules are NEWS_DESIGN.md sections 4 and 7
(research/news_effects_2026-11/). Expected values are written by hand from those tables, not read from the code:
P = CPI 24, NFP 10, FOMC 12, PPI 3 (section 3); flash at T-15 and T0 for CPI, NFP, FOMC statement, at T+30 for
the presser, none for PPI, OURS rows, T-60 or 'week of' rows (section 4).
JS runs under node if present, else headless Edge/Chrome (the dev host has no node).
Run: python MyTradingSys/tools/live_aid/test_events_wire.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
JS = HERE / "events_strip.js"
MIN = 60_000
NOW = 1_800_000_000_000  # fixed clock, ms


def _browser():
    for env, rel in (("PROGRAMFILES(X86)", r"Microsoft\Edge\Application\msedge.exe"),
                     ("PROGRAMFILES", r"Google\Chrome\Application\chrome.exe"),
                     ("PROGRAMFILES", r"Microsoft\Edge\Application\msedge.exe")):
        base = os.environ.get(env)
        if base and (Path(base) / rel).exists():
            return str(Path(base) / rel)
    return shutil.which("chromium") or shutil.which("google-chrome")


def run_js(expr, data):
    """Evaluate expr (JS, sees E = EVSTRIP and D = data) and return its JSON value."""
    return run_many([(expr, data)])[0]


def run_many(items):
    """Evaluate several (expr, data) pairs in ONE runtime launch (each Edge launch costs seconds; a loaded gate host timed out)."""
    assert JS.exists(), "events_strip.js missing"
    src = JS.read_text(encoding="utf-8")
    body = "var R=[];" + "".join("R.push((function(E,D){return %s;})(window.EVSTRIP,%s));" % (e, json.dumps(d))
                                 for e, d in items)
    node = shutil.which("node")
    if node:
        p = subprocess.run([node, "-e", "var window={};" + src + "\n" + body + "process.stdout.write(JSON.stringify(R))"],
                           capture_output=True, text=True, timeout=30)
        assert p.returncode == 0, p.stderr
        return json.loads(p.stdout)
    br = _browser()
    if not br:
        pytest.skip("neither node nor Edge/Chrome available")
    html = ("<body><script>var module={exports:{}};" + src +  # module defined, as in node -e (CI failure 42473425810)
             "\ntry{" + body + "document.body.textContent='@@'+JSON.stringify(R)+'@@';}"
            "catch(e){document.body.textContent='@@ERR '+e+'@@';}</script></body>")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "t.html"
        f.write_text(html, encoding="utf-8")
        p = subprocess.run([br, "--headless=new", "--disable-gpu", "--dump-dom", f.as_uri()],
                           capture_output=True, text=True, timeout=90)
    out = p.stdout.split("@@")
    assert len(out) >= 3, p.stdout[-300:] + p.stderr[-300:]
    assert not out[1].startswith("ERR"), out[1]
    return json.loads(out[1])


def sched(id_, cls, t0, stale=False):
    return {"id": id_, "cls": cls, "t0": t0, "stale": stale}


LAST = {"CPI": {"date": "2026-10-14", "r15": -0.41, "z15d": -1.9, "vr5": 6.2},
        "NFP": {"date": "2026-10-02", "r15": 0.12, "z15d": 0.8, "vr5": 3.1},
        "FOMC": {"date": "2026-10-28", "r15": 0.05, "z15d": 0.3, "vr5": 2.0},
        "PPI": {"date": "2026-10-15", "r15": 0.0, "z15d": 0.1, "vr5": 1.0}}


def data(schedule, analysts=None, named=None):
    return {"schedule": schedule, "last": LAST, "analysts": analysts or {}, "named": named or []}


def rows_of(d):
    return run_js("E.rows(%d, D, 5)" % NOW, d)


def test_strip_order_and_columns():
    d = data([sched("cpi-past", "CPI", NOW - 5 * MIN), sched("fomc-soon", "FOMC", NOW + 30 * MIN),
              sched("nfp-3d", "NFP", NOW + 3 * 24 * 60 * MIN)])
    rows = rows_of(d)
    assert [r["id"] for r in rows] == ["fomc-soon", "nfp-3d"]          # past row gone, soonest first
    f, n = rows
    assert f["countdown"] == "00:30:00" and n["countdown"] == "3d 00:00:00"
    assert f["p"] == 12 and n["p"] == 10                              # NEWS_DESIGN section 3 P table
    assert f["last"] == LAST["FOMC"] and n["last"] == LAST["NFP"]      # date, r15, z15d, vr5 of the last same-class move
    assert (f["n"], f["long"], f["short"], f["hold"]) == (0, 0, 0, 0)
    many = data([sched("x%d" % i, "PPI", NOW + (i + 1) * MIN) for i in range(8)])
    got = rows_of(many)
    assert len(got) == 5 and got[0]["p"] == 3
    pr = rows_of(data([sched("fomc-pc", "FOMC_PRESSER", NOW + MIN)]))[0]  # presser: own row, FOMC P and FOMC last move
    assert pr["p"] == 12 and pr["last"] == LAST["FOMC"]


def test_strip_flash_times():
    T = NOW + 3 * 60 * MIN
    cases = (("CPI", [T - 15 * MIN, T]), ("NFP", [T - 15 * MIN, T]), ("FOMC", [T - 15 * MIN, T]),
             ("FOMC_PRESSER", [T]), ("PPI", []))
    nd = data([], {"hack-1": {"n": 2, "L": 0, "S": 2, "H": 0}},
              [{"id": "hack-1", "label": "Named", "t0": T}, {"id": "wk-1", "label": "Week of", "weekOf": T}])
    got = run_many([("E.rows(%d, D, 5)" % NOW, data([sched("r", cls, T)])) for cls, _ in cases]
                   + [("E.rows(%d, D, 5)" % NOW, nd)])
    rows_by_cls = [g[0] for g in got[:5]]
    rows = got[5]                                                     # OURS row and 'week of' row: no flash, no P
    assert [r["id"] for r in rows] == ["hack-1", "wk-1"] and all(r["p"] is None for r in rows)
    assert rows[1]["loose"] is True and rows[0]["loose"] is False
    crow = rows_by_cls[0]
    dues = [(T - 61 * MIN, T - 59 * MIN, False),                      # T-60: countdown only
            (T - 16 * MIN, T - 14 * MIN, True),                       # T-15
            (T - 14 * MIN, T - MIN, False),
            (T - MIN, T + MIN, True),                                 # T0
            (T, T + 5 * MIN, False)]                                  # already fired
    out = run_many([("E.flashTimes(D.row)", {"row": r}) for r in rows_by_cls]
                   + [("E.flashDue(D.row, %d, %d)" % (a, b), {"row": crow}) for a, b, _ in dues]
                   + [("E.flashTimes(D.row)", {"row": r}) for r in rows])
    assert out[:5] == [w for _, w in cases]
    assert out[5:10] == [w for _, _, w in dues]
    assert out[10:] == [[], []]


def test_strip_hold_and_stale():
    T = NOW + 60 * MIN
    d = data([sched("cpi-x", "CPI", T), sched("nfp-y", "NFP", T + MIN, stale=True)],
             {"cpi-x": {"n": 4, "L": 2, "S": 2, "H": 0}, "nfp-y": {"n": 3, "L": 3, "S": 0, "H": 0}})
    cpi, nfp = rows_of(d)
    assert cpi["chip"] == "HOLD" and (cpi["n"], cpi["long"], cpi["short"], cpi["hold"]) == (4, 2, 2, 0)
    assert nfp["chip"] == "HOLD"                                       # all analysts LONG: a count beside the row, never the chip
    assert nfp["stale"] is True and cpi["stale"] is False
    html = run_js("E.html(D.rows)", {"rows": [cpi, nfp]})
    assert "stale" in html.split("nfp-y")[1] and "stale" not in html.split("nfp-y")[0]
    assert "L2" in html and "S2" in html and "H0" in html


def test_headline_links_event():
    T = NOW + 20 * MIN
    rows = rows_of(data([sched("cpi-x", "CPI", T), sched("ppi-x", "PPI", T + MIN)]))
    titles = ["US CPI (YoY) (Oct) actual 3.1% vs 3.0% expected", "Producer Price Index rises 0.2%", "Binance lists a new token"]
    got = run_many([("E.linkHeadline(D.title, D.rows)", {"rows": rows, "title": t}) for t in titles])
    assert got == [{"id": "cpi-x", "p": 24}, {"id": "ppi-x", "p": 3}, None]


# ---- export rules (events_to_watch.json, schedule times) ----
MD = """### A One | 2026-10-14 | v1 | T1
event: cpi-2026-10-14
expected_btc_dir: down
timing: before
stated: s
evidence: "quote one"

### A One | 2026-10-14 | v1 | T1
event: cpi-2026-10-14
expected_btc_dir: down
timing: before
stated: s
evidence: "quote one again"

### B Two | 2026-10-14 | v2 | T2
event: cpi-2026-10-14
expected_btc_dir: up
timing: before
stated: s
evidence: "quote two"

### C Three | 2026-10-15 | v3 | T3
event: ppi-2026-10-15
expected_btc_dir: none
timing: after
stated: s
evidence: "quote three"
"""


def test_export_dedupes_and_counts():
    import events_wire
    out = events_wire.export_events(MD)
    by = {e["event"]: e for e in out["events"]}
    assert len(out["events"]) == 2
    cpi = by["cpi-2026-10-14"]
    assert (cpi["analysts"], cpi["long"], cpi["short"], cpi["hold"]) == (2, 1, 1, 0) and cpi["date"] == "2026-10-14"
    assert cpi["quote"] == "quote one"
    ppi = by["ppi-2026-10-15"]
    assert (ppi["analysts"], ppi["long"], ppi["short"], ppi["hold"]) == (1, 0, 0, 1)


def test_schedule_times_are_et_in_utc():
    import events_wire
    cal = {"bls": {"CPI": {"November 2026": ["2026-12-10", "08:30 AM"]}, "NFP": {}, "PPI": {}},
           "fomc": ["2026-12-09"], "corrections": {"set": {}, "drop": []}}
    rows = {r["id"]: r for r in events_wire.schedule(cal, "2026-11-01")}
    assert rows["cpi-2026-12-10"]["t0"] == 1796909400000              # 13:30Z (08:30 EST)
    assert rows["fomc-2026-12-09"]["t0"] == 1796842800000             # 19:00Z (14:00 EST)
    assert rows["fomc-pc-2026-12-09"]["t0"] == rows["fomc-2026-12-09"]["t0"] + 30 * MIN
    assert rows["fomc-pc-2026-12-09"]["cls"] == "FOMC_PRESSER"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
