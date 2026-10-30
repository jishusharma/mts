"""Layer 3 of MyTradingSys/system/ARTIFACT_TESTING.md for the live aid: open live_aid.html?replay=fixture in headless
Chromium, feed it fixture_klines.json (window.LIVEAID_REPLAY, injected by the test; no sockets, fetch or news), freeze the
clock at the last bar's open + 60 s, then read the RENDERED #strip numbers and compare them with independent Python maths
(the py_* helpers of test_live_aid.py applied to the fixture, never page or live_aid_indicators.js code).

Compared (printed digits): 1m and 5m rows, RSI 1 dp, SMA of RSI 1 dp, %B x100 0 dp, BB width % 2 dp, ATR 1 dp = 10 numbers.
NOT_IN_DATA expected: the 15m row (20 bars < 40), 1h, 4h, and every vs-VWAP cell (the fixture opens at 00:00Z, so the
1m window cannot cover the day start; page rule at live_aid.html "only if the window covers 00:00Z").
Fail-first: LIVE_AID_REPLAY_BREAK=rsi defines a window.LiveAid setter that wraps rsi to return +0.1 percent (the page
assigns LiveAid after init scripts run, so a plain patch would be overwritten); the strip test must then fail, and
test_wrapped_rsi_is_caught proves the comparison catches it inside the normal run.
Skips (never fails) without the playwright package or a Chromium.
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PAGE = HERE / "live_aid.html"
FIXTURE = HERE / "fixture_klines.json"
BREAK = os.environ.get("LIVE_AID_REPLAY_BREAK", "")

# test_live_aid loads 300 live klines at import unless CI is set; the replay test always wants the committed fixture.
_ci = os.environ.get("CI")
os.environ["CI"] = "1"
sys.path.insert(0, str(HERE))
try:
    import test_live_aid as la
finally:
    if _ci is None:
        os.environ.pop("CI", None)
    else:
        os.environ["CI"] = _ci

KLINES = json.loads(FIXTURE.read_text(encoding="utf-8"))["klines"]
LAST_OPEN = int(KLINES[-1][0])
NOW_MS = LAST_OPEN + 60_000

WRAP_RSI = """
(function () {
  var real;
  Object.defineProperty(window, 'LiveAid', { configurable: true,
    get: function () { return real; },
    set: function (api) {
      var orig = api.rsi;
      api.rsi = function () { return orig.apply(this, arguments).map(function (x) { return x * 1.001; }); };
      real = api;
    } });
})();
"""


def fold(rows, ms):
    """Independent Python fold of 1m rows into ms buckets (open of first, max high, min low, close of last, sum volume)."""
    out = []
    for r in rows:
        b = int(r[0]) // ms * ms
        o, h, l, c, v = (float(r[i]) for i in range(1, 6))
        if not out or out[-1][0] != b:
            out.append([b, o, h, l, c, v])
        else:
            cur = out[-1]
            cur[2], cur[3], cur[4], cur[5] = max(cur[2], h), min(cur[3], l), c, cur[5] + v
    return out


def expected_row(rows):
    c = [r[4] for r in rows]
    h = [r[2] for r in rows]
    l = [r[3] for r in rows]
    pct, width = la.py_bb(c)
    rsi = la.py_rsi(c)
    return {
        "RSI": f"{rsi[-1]:,.1f}",
        "SMA": f"{la.py_sma(rsi, 14)[-1]:,.1f}",
        "%B": f"{pct[-1] * 100:,.0f}",
        "BBw": f"{width[-1] * 100:,.2f}",
        "ATR": f"{la.py_atr(h, l, c)[-1]:,.1f}",
    }


EXPECTED = {"1m": expected_row(fold(KLINES, 60_000)), "5m": expected_row(fold(KLINES, 300_000))}
NUM = re.compile(r"^\s*(-?[\d,]*\.?\d+)")
COLS = {"RSI": 1, "SMA": 2, "%B": 3, "BBw": 4, "ATR": 5}   # td index in a #strip number row; 6 = vs VWAP


@pytest.fixture(scope="module")
def browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright package not installed: pip install playwright")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception as ex:  # no browser here: say so, never fail
            pytest.skip("no Chromium for playwright: " + str(ex).splitlines()[0][:120])
        try:
            yield b
        finally:
            b.close()


def open_replay(browser, fixture=True, wrap=False):
    """Open the page in replay mode with the network off; return (strip rows as lists of cell texts, page errors)."""
    ctx = browser.new_context(offline=True, viewport={"width": 1400, "height": 900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    try:
        if wrap:
            page.add_init_script(WRAP_RSI)
        if fixture:
            page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(KLINES) + ";")
        page.clock.set_fixed_time(datetime.datetime.fromtimestamp(NOW_MS / 1000, tz=datetime.timezone.utc))  # a bare number is read as seconds
        page.goto(PAGE.resolve().as_uri() + "?replay=fixture", wait_until="load", timeout=30000)
        page.check("#more-tog")     # the SMA, BBw, ATR, vs VWAP columns are hidden until "More detail"
        page.wait_for_timeout(1300)  # one 1 s render tick on top of the first render
        assert page.evaluate("Date.now()") == NOW_MS, "clock is not fixed at last bar open + 60 s"
        rows = page.eval_on_selector_all("#strip tr", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))")
        visible = page.eval_on_selector_all("#strip td.x", "cs => cs.every(c => c.offsetParent !== null)")
        return rows, errs, visible
    finally:
        ctx.close()


def strip_problems(rows):
    """Mismatches between the rendered 1m/5m rows and the Python maths (empty list = all 10 numbers equal)."""
    by_tf = {r[0].strip(): r for r in rows}
    problems = []
    for tf, exp in EXPECTED.items():
        row = by_tf.get(tf)
        if row is None or len(row) < 7:
            problems.append(f"{tf}: row missing or short: {row}")
            continue
        for name, idx in COLS.items():
            m = NUM.match(row[idx])
            got = m.group(1) if m else row[idx].strip()
            if got != exp[name]:
                problems.append(f"{tf} {name}: page shows {got!r}, python maths gives {exp[name]!r}")
    return problems


def test_rendered_strip_matches_python_maths(browser):
    rows, errs, visible = open_replay(browser, wrap=BREAK == "rsi")
    assert not errs, errs
    assert visible, "hidden columns are not shown after ticking More detail"
    problems = strip_problems(rows)
    assert not problems, "; ".join(problems)


def test_wrapped_rsi_is_caught(browser):
    """Fail-first inside the run: with LiveAid.rsi wrapped (+0.1 percent) the comparison must report a mismatch."""
    rows, errs, _ = open_replay(browser, wrap=True)
    assert not errs, errs
    problems = strip_problems(rows)
    assert any("RSI" in p for p in problems), f"+0.1 percent RSI went unnoticed: {problems}"


def test_short_windows_read_not_in_data(browser):
    rows, _, _ = open_replay(browser)
    by_tf = {r[0].strip(): r for r in rows}
    for tf in ("15m", "1h", "4h"):   # 20, 5, 2 bars: fewer than the 40 the page needs
        assert tf in by_tf and "NOT_IN_DATA" in " ".join(by_tf[tf]), (tf, by_tf.get(tf))
    for tf in ("1m", "5m"):
        assert by_tf[tf][6].strip() == "NOT_IN_DATA", (tf, "vs VWAP", by_tf[tf][6])


def test_missing_fixture_reads_not_in_data(browser):
    rows, errs, _ = open_replay(browser, fixture=False)
    assert not errs, errs
    assert rows, "no strip rows rendered"
    for r in rows:
        txt = " ".join(r)
        assert "NOT_IN_DATA" in txt and "replay fixture not loaded" in txt, r


def test_fixture_is_the_expected_window():
    assert len(KLINES) == 300 and KLINES[0][0] % 86_400_000 == 0, "fixture no longer opens at 00:00Z: the vs-VWAP NOT_IN_DATA premise changed"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
