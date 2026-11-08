"""News weight, bias chip and tab flash (news_weight.js, card news-weight-bias-flash-1108).

Rules under test: research/news_effects_2026-11/NEWS_DESIGN.md sections 2-6. Context only: no gate, no order, no size.
Every expected value is written by hand from the design tables or from news_events.csv read here in Python, never from the code.
Run: python MyTradingSys/tools/live_aid/test_news_weight.py
"""
import csv
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "news_weight.js"
CSV = HERE.parent.parent / "research" / "news_effects_2026-11" / "news_events.csv"
MIN = 60000

RUNNER = r"""
const fs = require('fs');
const NW = require(process.argv[1]);
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(payload.map(c => NW[c.fn].apply(null, c.args || []))));
"""


def call(*calls):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")
    assert JS.exists(), "news_weight.js missing"
    p = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps([{"fn": f, "args": list(a)} for f, *a in calls]),
                       capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def one(fn, *args):
    return call((fn,) + args)[0]


def part(o):
    return one("parts", o)


def bias(**kw):
    o = {"cls": "OTHER", "prior": None, "z": None, "vr5": None, "ageMin": 5, "overlap": "", "due": None}
    o.update(kw)
    return one("bias", o)


# ---------- (1) weight ----------

def test_weight_parts():
    # CPI, move z 7.6 v 28, importance 10, 2 min after: P 24 + K 40 + I 20 = 84, F 1
    a = part({"cls": "MACRO_CPI", "importance": 10, "ageMin": 2, "z": 7.6, "vr5": 28})
    assert (a["P"], a["K"], a["I"], a["F"], a["w"]) == (24, 40, 20, 1, 84)
    # unknown class, no move, importance 9: 3 + 0 + 18 = 21
    b = part({"cls": "OTHER", "importance": 9, "ageMin": 1, "z": None, "vr5": None})
    assert (b["P"], b["K"], b["I"], b["w"]) == (3, 0, 18, 21)
    # P from the catalogue shares: CPI 24, FOMC 12, NFP 10, PPI 3, every other class 3
    got = [part({"cls": c, "importance": 0, "ageMin": 1})["P"] for c in
           ("MACRO_CPI", "FOMC", "MACRO_NFP", "MACRO_PPI", "ETF_REGULATORY", "HACK_EXPLOIT", "TRUMP_POLICY", "OTHER")]
    assert got == [24, 12, 10, 3, 3, 3, 3, 3]
    # K steps: abs z >= 2 and vr5 >= 4 gives 20; abs z >= 4 gives 40 (any vr5); else 0
    ks = [part({"cls": "OTHER", "importance": 0, "ageMin": 1, "z": z, "vr5": v})["K"] for z, v in
          [(2.0, 4.0), (-2.0, 4.0), (1.99, 50), (2.5, 3.9), (4.0, 1.0), (-4.0, 0.5), (-3.9, 10)]]
    assert ks == [20, 20, 0, 0, 40, 40, 20]
    # F: 1 for 15 min, linear to 0 at 60 min (37.5 min = 0.5)
    fs = [part({"cls": "MACRO_CPI", "importance": 10, "ageMin": m, "z": 7.6, "vr5": 28})["F"] for m in (0, 15, 37.5, 60, 75)]
    assert fs == [1, 1, 0.5, 0, 0]
    assert part({"cls": "MACRO_CPI", "importance": 10, "ageMin": 37.5, "z": 7.6, "vr5": 28})["w"] == 42
    # overlap within 4 h halves P only: CPI 24 -> 12, W = 12 + 0 + 0
    c = part({"cls": "MACRO_CPI", "importance": 0, "ageMin": 1, "overlap": "FOMC"})
    assert (c["P"], c["w"]) == (12, 12)
    # before a scheduled t0: W = P + I whatever the move or age
    d = part({"cls": "MACRO_CPI", "importance": 5, "ageMin": 0, "due": 11 * MIN + 5000, "z": 9, "vr5": 50})
    assert (d["w"], d["K"], d["F"]) == (34, 0, 1)
    # labels per part: SOURCED or OURS, hover text lists P K I F
    assert set(a["label"]) == {"P", "K", "I", "F"} and set(a["label"].values()) <= {"SOURCED", "OURS"}
    assert all(t in a["hover"] for t in ("P 24", "K 40", "I 20", "F 1"))
    assert a["label"]["I"] == "OURS" and a["label"]["P"] == "SOURCED"
    # importance missing: I 0; importance over 10 is capped
    assert part({"cls": "OTHER", "ageMin": 1})["I"] == 0
    assert part({"cls": "MACRO_CPI", "importance": 99, "ageMin": 1, "z": 9, "vr5": 9})["w"] == 84     # I capped at 20: 24 + 40 + 20


# ---------- (2) bias chip ----------

def test_bias_hold_default():
    # no move: HOLD "no move", also when a prior tag exists (the tag never sets the chip alone)
    assert bias() == {"chip": "HOLD", "reason": "no move"}
    for cls, pr in (("HACK_EXPLOIT", "SHORT"), ("ETF_REGULATORY", "LONG"), ("GEOPOLITICS", "SHORT"), ("MACRO_CPI", "LONG")):
        r = bias(cls=cls, prior=pr, z=1.9, vr5=60)
        assert (r["chip"], r["reason"]) == ("HOLD", "no move"), cls
    assert bias(cls="MACRO_NFP", z=2.0, vr5=3.9)["chip"] == "HOLD"   # K 0: vr5 under 4


def test_bias_long_short_on_move():
    r = bias(cls="ETF_REGULATORY", z=3.1, vr5=12)
    assert (r["chip"], r["reason"]) == ("LONG", "move +z 3.1 v 12")
    r = bias(cls="OTHER", z=-3.1, vr5=12)
    assert (r["chip"], r["reason"]) == ("SHORT", "move -z 3.1 v 12")
    assert bias(z=2.0, vr5=4.0)["chip"] == "LONG"                      # K = 20 exactly
    assert bias(z=-5, vr5=0.5)["chip"] == "SHORT"                      # K = 40 needs no vr5
    # a prior tag that agrees with the move does not block it; the opposite one makes HOLD
    assert bias(cls="HACK_EXPLOIT", prior="SHORT", z=-3, vr5=9)["chip"] == "SHORT"
    r = bias(cls="HACK_EXPLOIT", prior="SHORT", z=3, vr5=9)
    assert (r["chip"], r["reason"]) == ("HOLD", "prior vs move")
    assert bias(cls="MACRO_CPI", prior="LONG", z=-6, vr5=20)["reason"] == "prior vs move"
    assert bias(cls="MACRO_CPI", prior="LONG", z=6, vr5=20)["chip"] == "LONG"
    assert bias(ageMin=35, z=3, vr5=9)["chip"] == "LONG"                # 35 min is not yet late


def test_bias_hold_late_overlap_ppi():
    r = bias(ageMin=36, z=6, vr5=20)
    assert (r["chip"], r["reason"]) == ("HOLD", "late 36 min")
    r = bias(cls="MACRO_CPI", overlap="FOMC", z=6, vr5=20)
    assert (r["chip"], r["reason"]) == ("HOLD", "overlap FOMC")
    r = bias(cls="MACRO_PPI", z=9, vr5=40)
    assert (r["chip"], r["reason"]) == ("HOLD", "PPI")
    r = bias(cls="MACRO_PPI", z=-9, vr5=40, ageMin=2)
    assert r["chip"] == "HOLD"
    r = bias(cls="MACRO_CPI", due=11 * MIN + 5000, z=9, vr5=40)
    assert r["chip"] == "HOLD" and r["reason"] == "due in 11:05"
    # one reason per chip, never empty
    assert all(isinstance(x["reason"], str) and x["reason"] for x in (bias(), bias(ageMin=50, z=6, vr5=20)))


# ---------- (3) flash ----------

def item(i, w, k=0, chip="HOLD", age=5, now=0):
    return {"id": i, "w": w, "k": k, "chip": chip, "time": now - age * MIN}


def steps(seq):
    """seq: list of (items, now, viewing); returns the on flag after each step, state carried through flashInit/flashStep."""
    node_in = json.dumps(seq)
    js = r"""
const NW = require(process.argv[1]); const seq = JSON.parse(process.argv[2]);
let s = NW.flashInit(), out = [];
for (const q of seq) { s = NW.flashStep(s, q[0], q[1], q[2]); out.push(s.on); }
process.stdout.write(JSON.stringify(out));
"""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed or not on PATH")
    assert JS.exists(), "news_weight.js missing"
    p = subprocess.run([node, "-e", js, str(JS), node_in], capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def test_flash_when():
    T = 100 * MIN
    # W 59 stays quiet; W 60 flashes; K = 40 flashes whatever W; nothing flashes while he is on the tab
    assert steps([([item("a", 59, now=T)], T, False)]) == [False]
    assert steps([([item("a", 60, now=T)], T, False)]) == [True]
    assert steps([([item("a", 41, k=40, now=T)], T, False)]) == [True]
    assert steps([([item("a", 20, k=20, now=T)], T, False)]) == [False]
    assert steps([([item("a", 90, now=T)], T, True)]) == [False]
    # a headline older than 60 min never starts a flash
    assert steps([([item("a", 90, age=61, now=T)], T, False)]) == [False]
    # no items: no flash
    assert steps([([], T, False)]) == [False]


def test_flash_stop():
    T = 100 * MIN
    a = lambda w, age=5, **kw: item("a", w, age=age, now=T, **kw)  # noqa: E731
    # opening the tab stops it, and the same headline never flashes again (one flash per headline)
    assert steps([([a(80)], T, False), ([a(80)], T, True), ([a(80)], T, False)]) == [True, False, False]
    # W falls under 60 stops it
    assert steps([([a(70)], T, False), ([a(59)], T, False)]) == [True, False]
    # at most 60 min: K = 40 keeps W high but the flash ends at 60 min
    assert steps([([a(70, k=40, age=59)], T, False), ([a(70, k=40, age=60)], T, False)]) == [True, False]
    # a new qualifying item re-flashes once (after he opened the tab, and while one is flashing)
    b = item("b", 75, now=T)
    assert steps([([a(80)], T, False), ([a(80)], T, True), ([a(80), b], T, False)]) == [True, False, True]
    # LONG <-> SHORT flip re-flashes once; the flip to HOLD never does
    seq = [([a(80, chip="LONG")], T, False), ([a(80, chip="LONG")], T, True), ([a(80, chip="SHORT")], T, False), ([a(80, chip="SHORT")], T, True),
           ([a(80, chip="LONG")], T, False)]
    assert steps(seq) == [True, False, True, False, False]            # second flip of the same headline: no third flash
    seq = [([a(80, chip="LONG")], T, False), ([a(80, chip="LONG")], T, True), ([a(80, chip="HOLD")], T, False), ([a(80, chip="HOLD")], T, False)]
    assert steps(seq) == [True, False, False, False]
    # LONG then HOLD then SHORT is still a flip of sign
    seq = [([a(80, chip="LONG")], T, True), ([a(80, chip="HOLD")], T, False), ([a(80, chip="SHORT")], T, False)]
    assert steps(seq) == [False, False, True]


# ---------- (4) repeat ----------

def catalogue_last():
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    out = {}
    for r in rows:
        if r["verified"] == "Y" and r["measured_ok"] == "Y" and r["btc_z15d"] != "":
            if r["class"] not in out or r["t0_utc"] > out[r["class"]]["t0_utc"]:
                out[r["class"]] = r
    return out


def test_repeat_no_decay():
    last = catalogue_last()["MACRO_CPI"]
    # no decay: the 1st and the 33rd CPI get the same W (the function has no sequence input)
    w = [part({"cls": "MACRO_CPI", "importance": 6, "ageMin": 3, "z": 4.5, "vr5": 9, "seq": n})["w"] for n in (1, 2, 33)]
    assert w == [24 + 40 + 12] * 3
    # last same-class move: date, r15, z15d, vr5 straight from the catalogue row; shown, never used
    lm = one("lastMove", "MACRO_CPI")
    assert lm["date"] == last["t0_utc"][:10] == "2026-10-14"
    assert (lm["r15"], lm["z15d"], lm["vr5"]) == (float(last["btc_r15"]), float(last["btc_z15d"]), float(last["btc_vr5"]))
    assert lm["flushed"] is True and "flushed last time" in lm["text"]       # CPI 2026-10-14 vr5 28.1 > 15
    assert "2026-10-14" in lm["text"] and "z-7.6" in lm["text"].replace(" ", "") or "z -7.6" in lm["text"]
    nfp = one("lastMove", "MACRO_NFP")
    assert nfp["vr5"] == 6.259 and nfp["flushed"] is False and "flushed" not in nfp["text"]
    assert one("lastMove", "TRUMP_POLICY") is None
    # the word follows vr5 > 15 only (15 exactly is not flushed)
    assert one("flushedWord", {"vr5": 15.01}) == "flushed last time" and one("flushedWord", {"vr5": 15}) == ""
    # the previous sign never sets the chip: same inputs, the previous move up or down, same chip
    base = dict(cls="MACRO_CPI", z=3, vr5=9)
    assert bias(**base) == bias(**dict(base, last={"r15": 2.0})) == bias(**dict(base, last={"r15": -2.0}))
    # assess() carries the last move and the flushed word without touching W or the chip
    rowx = {"id": "x", "time": 1000 * MIN, "title": "US CPI Sep m/m", "importance": 6}
    a = one("assess", rowx, {"now": 1003 * MIN, "z": 3, "vr5": 9})
    assert a["cls"] == "MACRO_CPI" and a["last"]["date"] == "2026-10-14" and a["flushed"] == "flushed last time"
    assert a["w"] == 24 + 20 + 12


# ---------- (5) class table ----------

def test_class_table_calls():
    cases = [
        ("US CPI Sep: hotter than forecast", "MACRO_CPI", "SHORT"),
        ("US CPI Sep: cooler than expected", "MACRO_CPI", "LONG"),
        ("US CPI Sep m/m 0.3%", "MACRO_CPI", None),
        ("Nonfarm payrolls +254K", "MACRO_NFP", None),
        ("US PPI Oct", "MACRO_PPI", None),
        ("FOMC holds rates", "FOMC", None),
        ("SEC approves spot ETF", "ETF_REGULATORY", "LONG"),
        ("SEC rejects spot ETF filing", "ETF_REGULATORY", "SHORT"),
        ("Spot ETF news today", "ETF_REGULATORY", None),
        ("Exchange hacked, attacker drains hot wallet", "HACK_EXPLOIT", "SHORT"),
        ("Missile strike escalates war", "GEOPOLITICS", "SHORT"),
        ("Trump: new executive order on crypto", "TRUMP_POLICY", None),
        ("Trump threatens new tariffs on China", "TARIFF_TRADE", None),
        ("Judge rules in lawsuit against exchange", "COURT_LEGAL", None),
        ("Network hard fork scheduled", "PROTOCOL", None),
        ("BOJ raises rates, Ueda says more to come", "BOJ_JAPAN", None),
        ("Gold rallies again", "OTHER", None),
        ("", "OTHER", None),
    ]
    got = call(*[("classify", t) for t, _, _ in cases])
    assert got == [c for _, c, _ in cases]
    pri = call(*[("prior", c, t) for t, c, _ in cases])
    assert pri == [p for _, _, p in cases]
    # no tag for these classes whatever the wording
    for cls in ("TRUMP_POLICY", "TARIFF_TRADE", "COURT_LEGAL", "PROTOCOL", "BOJ_JAPAN", "MACRO_NFP", "FOMC", "MACRO_PPI", "OTHER"):
        assert one("prior", cls, "hack war ETF approves hotter than forecast cooler") is None, cls
    # nothing the design dropped: no source tier, corroboration, repeat decay or era term in the API or the source
    api = one("api")
    src = JS.read_text(encoding="utf-8").lower()
    for bad in ("tier", "corrobor", "decay", "trump era", "trump-era", "pct_thresh"):
        assert not any(bad in k.lower() for k in api), bad
    assert "corrobor" not in src.replace("no corroboration", "") and "tiebreak" not in src
    # P table = the catalogue shares (re-derived here from news_events.csv): round(40 x share abs z15d > 2, share in whole percent)
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    want = {}
    for cls in ("MACRO_CPI", "FOMC", "MACRO_NFP"):
        v = [abs(float(r["btc_z15d"])) for r in rows if r["class"] == cls and r["verified"] == "Y" and r["btc_z15d"] != ""]
        want[cls] = int(math.floor(40 * round(100 * sum(1 for z in v if z > 2) / len(v)) / 100 + 0.5))
    assert want == {"MACRO_CPI": 24, "FOMC": 12, "MACRO_NFP": 10}
    assert one("pTable") == dict(want, MACRO_PPI=3, OTHER=3)
    csv_text = CSV.read_text(encoding="utf-8")
    assert one("priorFromCsv", csv_text) == one("pTable")


# ---------- extras: K from klines, wiring, page ----------

def klines(n_before, bars_after, jump_pct, vol_after, start=1_000_000 * MIN):
    """Flat 1m bars with tiny alternating returns (sd known), then bars_after bars ramping to jump_pct. Returns (rows, headline ms)."""
    rows, p = [], 100000.0
    t0 = start + n_before * MIN
    for i in range(n_before):
        p *= 1.0002 if i % 2 else 0.9998
        rows.append([start + i * MIN, p, p, p, p, 10.0])
    p0 = rows[-1][4]
    for j in range(bars_after):
        c = p0 * (1 + jump_pct / 100 * (j + 1) / bars_after)
        rows.append([t0 + j * MIN, p0, c, p0, c, vol_after])
    return rows, t0


def test_confirm_z_on_24h_stdev_and_vr5():
    rows, t0 = klines(1500, 2, 1.0, 100.0)
    c = one("confirm", rows, t0 + 5000, t0 + 2 * MIN + 1000)
    # 24 h stdev of the alternating +-0.02 % returns is 0.02 %; r since the minute before = +1.0 %; z = 1.0 / (0.02 x sqrt(2)) = 35.4
    assert c["bars"] == 2
    assert c["z"] == pytest.approx(1.0 / (0.02 * math.sqrt(2)), rel=0.02)
    assert c["vr5"] == pytest.approx(10.0, rel=1e-9)          # 100 / mean of the prior 60 bars (10)
    # the last 60 min stdev must not be used: make the hour before calm and the day before wild
    wild = klines(1500, 2, 1.0, 100.0)[0]
    for i in range(0, 1400):
        wild[i][4] = wild[i][4] * (1.01 if i % 2 else 0.99)
        wild[i][1] = wild[i][2] = wild[i][3] = wild[i][4]
    cw = one("confirm", wild, t0 + 5000, t0 + 2 * MIN + 1000)
    assert abs(cw["z"]) < 3                                    # wild day inflates sd; a calm-hour sd would give > 30
    # forming bar is not used; fewer than 1 closed bar: no move
    assert one("confirm", rows, t0 + 5000, t0 + 30 * 1000) is None
    # short feed (under 24 h of bars): no move rather than a guess
    short, ts = klines(600, 2, 1.0, 100.0)
    assert one("confirm", short, ts + 5000, ts + 2 * MIN + 1000) is None


def test_page_wires_weight_chip_and_flash():
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert page.count('<script src="news_weight.js"></script>') == 1
    assert "NEWSWEIGHT" in page and "NW.flashStep" in page and "nw-chip" in page and "row('news'" in page
    assert "@keyframes nwflash" in page
    sys.path.insert(0, str(HERE))
    import build_artifact
    built = build_artifact.build()
    assert 'src="news_weight.js"' not in built and "root.NEWSWEIGHT = api" in built


def test_requirements_section_and_no_edge_claim():
    req = (HERE / "REQUIREMENTS.md").read_text(encoding="utf-8")
    assert "News weight" in req and "news_weight.js" in req and "NEWS_DESIGN.md" in req
    study = HERE / "news_study.py"
    assert study.exists()
    s = study.read_text(encoding="utf-8")
    assert "counts only" in s.lower() and "no edge" in s.lower()


def test_study_move_offline():
    sys.path.insert(0, str(HERE))
    import news_study
    base = 5000 * MIN
    rows = {base - MIN: 100.0, base + 14 * MIN: 101.0, base + 59 * MIN: 99.0}
    assert news_study.move(rows, base + 30000, 15) == pytest.approx(1.0)
    assert news_study.move(rows, base + 30000, 60) == pytest.approx(-1.0)
    assert news_study.move(rows, base + 30000, 5) is None            # bar missing: NA, never a guess
    items = [{"time": base + 1000, "title": "x", "importance": 5}]
    out = news_study.report(items, ["OTHER"], rows)
    assert out[0] == "OTHER  n 1" and "up 1, down 0" in out[-1] and "up 0, down 1" in out[-1]


# ---------- rendered page (headless Chromium, replay, network off); skips without playwright or a Chromium ----------

def test_page_renders_chip_flashes_and_stops_on_open():
    import datetime
    pw = pytest.importorskip("playwright.sync_api")
    start = 1_794_000_000_000 // MIN * MIN
    rows, t0 = klines(1500, 2, -1.0, 100.0, start=start)
    now_ms = t0 + 2 * MIN + 1000
    news = [{"_id": "c1", "time": t0 + 5000, "source": "BLS", "title": "US CPI Sep: hotter than forecast", "importance": 9, "suggestions": []},
            {"_id": "c2", "time": t0 - 300 * MIN, "source": "Tree", "title": "Gold rallies again", "importance": 2, "suggestions": []}]
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception as e:  # noqa: BLE001
            pytest.skip("no Chromium: " + str(e).splitlines()[0])
        ctx = b.new_context(offline=True, viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
        page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(rows) + "; window.LIVEAID_NEWS = " + json.dumps(news) + ";")
        page.clock.set_fixed_time(datetime.datetime.fromtimestamp(now_ms / 1000, tz=datetime.timezone.utc))
        page.goto((HERE / "live_aid.html").resolve().as_uri() + "?replay=fixture", wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        try:
            assert not errs, errs
            # CPI hotter than forecast, importance 9, BTC -1 % on 100x volume: W = 24 + 40 + 18 = 82, SHORT agrees with the 'prior SHORT' tag
            cell = page.eval_on_selector_all("#news tr", "rs => rs.map(r => r.children[3].innerText)")
            assert "W 82" in cell[0] and "SHORT" in cell[0], cell
            assert "W 0" in cell[1] and "HOLD" in cell[1] and "late 302 min" in cell[1], cell
            hover = page.eval_on_selector("#news .nw-w", "e => e.title")
            assert "P 24 SOURCED" in hover and "I 18 OURS" in hover and "F 1 OURS" in hover, hover
            row = lambda: page.eval_on_selector('#ov tr[data-go="news"]', "e => e.className")  # noqa: E731
            assert "nwflash" in row()                                                  # W 82 >= 60: the News row pulses
            page.evaluate("location.hash = '#news'")
            page.wait_for_timeout(1300)
            page.evaluate("location.hash = ''")
            page.wait_for_timeout(1300)
            assert "nwflash" not in row()                                              # opened once: stopped and not re-flashed
        finally:
            ctx.close()
            b.close()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
