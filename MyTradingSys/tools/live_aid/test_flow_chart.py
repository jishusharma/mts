"""Tests for the Forced moves panel (flow_chart.js, requirement R25). Rules run in node against flow_fixture.json, whose expected values were
worked out by hand (thresholds from STEPS.md: flat under 0.1 %, BUILD/UNWIND = 3+ bars and 0.5 % OI):
  run 1: OI 1000 -> 1012 over 4 bars = +1.20 %, price 100 -> 100.9 = +0.90 %;  run 2: OI 1012 -> 985 over 6 bars = -27/1012 = -2.67 %, price 100.9 -> 99.5 = -1.39 %.
  window of 4: price 100.3 -> 99.5 = -0.80 %, OI 1005 -> 985 = -1.99 %, CVD -3-2-1-1 = -7."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

import build_artifact

HERE = Path(__file__).resolve().parent
JS = HERE / "flow_chart.js"
HTML = HERE / "live_aid.html"
FIX = json.loads((HERE / "flow_fixture.json").read_text(encoding="utf-8"))
NODE = shutil.which("node")
RUNNER = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
pytestmark = pytest.mark.skipif(NODE is None, reason="node not installed")
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def js(fn, *a):
    out = subprocess.run([NODE, "-e", RUNNER, str(JS)], input=json.dumps({"fn": fn, "a": list(a)}), capture_output=True, text=True,
                         encoding="utf-8", timeout=60, creationflags=NOWIN)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def mk(rows, step=60000):
    return [{"t": i * step, "c": r[0], "oi": r[1], "cvd": r[2] if len(r) > 2 else None} for i, r in enumerate(rows)]


@pytest.mark.parametrize("case", FIX["bar_state"], ids=lambda c: str(c["in"]))
def test_bar_state_table(case):
    assert js("barState", *case["in"]) == case["out"]


@pytest.mark.parametrize("case", FIX["oi_runs"], ids=lambda c: c["name"])
def test_oi_runs_fixture(case):
    assert js("oiRuns", mk(case["bars"])) == case["out"]


def test_window_state_fixture():
    w = FIX["window"]
    assert js("windowState", mk(w["bars"]), w["n"]) == w["out"]
    assert js("windowState", mk(w["bars"][:3]), 4) is None


def test_series_states_for_the_build_then_unwind_case():
    ser = js("series", mk(FIX["oi_runs"][0]["bars"]))
    # idx 1-4: price up 0.2..0.3 %, OI up 0.3 %; idx 5-10: price down 0.1..0.4 %, OI down 0.2..0.5 %
    assert [e["state"] for e in ser] == ["NEW_LONGS"] * 4 + ["FORCED_SELLING"] * 6


def test_chip_text_plain_words():
    assert js("chipText", {"state": "FORCED_BUYING", "dpx": 0.6, "doi": -0.4, "cvd": 5, "taker": "agree"}) == "FORCED BUYING: price +0.6 %, OI -0.4 %, takers buying"
    assert js("chipText", {"state": "FORCED_SELLING", "dpx": -0.6, "doi": -0.4, "cvd": 5, "taker": "disagree"}).endswith("takers buying (absorbed)")
    assert js("chipText", {"state": "NO_DATA"}) == "NOT_IN_DATA" and js("chipText", None) == "NOT_IN_DATA"
    assert js("runLabel", {"kind": "BUILD", "doi": 1.8, "bars": 5, "dpx": 0.9}) == "BUILD +1.8 % OI, 5 bars, price +0.9 %"


def test_stale_and_closed_bars():
    H = 3600000
    kl = [[str(2 * H), "1", "1", "1", "1"], [str(H), "1", "1", "1", "1"], ["0", "1", "1", "1", "1"]]
    bars = js("mergeBars", kl, {}, None, H, 2 * H + 10)         # the bar opened at 2H is still forming: dropped
    assert [b["t"] for b in bars] == [0, H] and bars[0]["oi"] is None and bars[0]["cvd"] is None
    assert js("stale", bars, H, 2 * H + 2 * H) is False          # last bar ended at 2H, now 4H: exactly 2 bars old
    assert js("stale", bars, H, 4 * H + 1) is True and js("stale", [], H, 0) is True


def test_perp_cvd_only_counts_bars_after_since():
    b5 = {"300000": [3, 1], "600000": [0, 2]}
    bars = [{"t": 0}, {"t": 300000}, {"t": 600000}]
    assert js("perpCvd", b5, bars, 300000, 300000) == [None, 2, -2]       # 3-1 = +2, 0-2 = -2; bar 0 is before since
    assert js("perpCvd", None, bars, 300000, None) == [None, None, None]


def test_footprint_label_collector_fresh_and_stale():
    now, cad = 10_000_000_000, 60000
    lim = 2 * cad + 120000
    flow = {"fp": {"t": now - 1000, "lines": {"15m": "15m 16:30Z delta +1.0 BTC", "1h": "1h 16:00Z delta -2.0 BTC"}}}
    old = {"tf": {"15m": {"line": "OLD15"}, "1h": {"line": "OLD1H"}}, "built_ms": now - 5000}
    assert js("fpLabel", flow, old, now, cad) == "Bybit perp, collector: 15m 16:30Z delta +1.0 BTC | 1h 16:00Z delta -2.0 BTC"
    assert js("fpLabel", None, old, now, cad) == "OLD15 | OLD1H"                                     # collector absent, file fresh
    stale_old = dict(old, built_ms=now - lim - 1)                                                   # 1 ms past 2 x cadence + 2 min
    s = js("fpLabel", None, stale_old, now, cad)
    assert s.startswith("footprint feed stale since ") and "OLD" not in s
    flow_stale = {"fp": {"t": now - lim - 1, "lines": {"15m": "x"}}}
    assert "x" not in js("fpLabel", flow_stale, stale_old, now, cad) and "stale since" in js("fpLabel", flow_stale, stale_old, now, cad)
    assert js("fpLabel", None, None, now, cad).startswith("footprint feed stale")


def test_render_svg_has_three_rows_runs_bubbles_and_hatching():
    rows = FIX["oi_runs"][0]["bars"]
    bars = [{"t": i * 3600000, "o": r[0], "h": r[0] + 0.1, "l": r[0] - 0.1, "c": r[0], "oi": r[1], "cvd": 1 if i % 2 else -1} for i, r in enumerate(rows)]
    runs = js("oiRuns", bars)
    svg = js("renderSvg", {"tf": "1h", "bars": bars, "runs": runs, "trades": [{"t": 5 * 3600000 + 5, "side": "buy", "usd": 2_000_000, "px": 100.5}], "cvdLabel": "spot CVD"})
    assert svg.count("<circle") == 1 and "BUILD +1.2 % OI, 4 bars, price +0.9 %" in svg and "UNWIND -2.7 % OI, 6 bars, price -1.4 %" in svg
    assert "fh-FORCED_SELLING" in svg and "spot CVD" in svg and "Open interest" in svg and "Price (USD)" in svg
    assert "NOT_IN_DATA" in js("renderSvg", {"bars": []})


def test_panel_and_script_tags_exist_and_are_inlined_in_artifact():
    html = HTML.read_text(encoding="utf-8")
    assert 'id="p-flow"' in html and 'id="flow-root"' in html and html.count('<script src="flow_chart.js"></script>') == 1
    assert html.index('id="p-flow"') < html.index('id="p-money"')              # directly above "What the money is doing"
    assert '<script src="flow_chart.js"></script>' in build_artifact.TAGS
    assert "<script>\n" + JS.read_text(encoding="utf-8") in build_artifact.build()
    assert "fpLabel(" in html and "Tested 2026-11-13: fading forced moves 0/128 cells pass" in html


def test_feed_file_is_gitignored():
    out = subprocess.run(["git", "check-ignore", "-q", str(HERE / "flow_feed.js")], cwd=HERE, capture_output=True, creationflags=NOWIN)
    assert out.returncode == 0
