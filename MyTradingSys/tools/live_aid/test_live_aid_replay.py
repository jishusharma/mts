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
        except Exception as ex:  # no bundled Chromium: try the installed Chrome, else say so, never fail
            try:
                b = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
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


# ---------- macro calendar strip (card live-aid-macro-calendar): rendered text vs hand-worked expectations ----------
FF = json.loads((HERE / "fixture_ff_calendar.json").read_text(encoding="utf-8"))["events"]
CAL_URL_GLOB = "**/ff_calendar_thisweek.json"


def _cal_page(browser, iso_now, events=None, offline=True):
    ctx = browser.new_context(offline=offline, viewport={"width": 1400, "height": 900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    return ctx, page, errs


def _cal_text(browser, iso_now, events):
    ctx, page, errs = _cal_page(browser, iso_now)
    try:
        page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(KLINES) + ";")
        if events is not None:
            page.add_init_script("window.LIVEAID_CAL = " + json.dumps(events) + ";")
        page.clock.set_fixed_time(datetime.datetime.fromisoformat(iso_now.replace("Z", "+00:00")))
        page.goto(PAGE.resolve().as_uri() + "?replay=fixture", wait_until="load", timeout=30000)
        page.wait_for_timeout(1300)
        assert not errs, errs
        return (page.inner_text("#mc-next"), page.inner_text("#mc-sub"),
                page.eval_on_selector_all("#mc-rows tr", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))"))
    finally:
        ctx.close()


def test_calendar_strip_renders_next_and_last(browser):
    """12:00Z 10-29: GDP 12:30Z is 30 min away (hand: 12:30 - 12:00); results newest first: FOMC Press Conference 10-28 18:30Z, Federal Funds Rate 18:00Z."""
    nxt, sub, rows = _cal_text(browser, "2026-10-29T12:00:00Z", FF)
    assert nxt == "in 30 min", nxt
    assert "Advance GDP q/q at 12:30Z" in sub and "forecast 3.2%" in sub and "previous 1.5%" in sub, sub
    assert [r[1] for r in rows] == ["FOMC Press Conference", "Federal Funds Rate"], rows
    assert rows[0][0].strip() == "10-28 18:30Z" and rows[1][0].strip() == "10-28 18:00Z", rows
    assert rows[1][2].strip() == "not in feed" and rows[1][3].strip() == "4.00%" and rows[1][4].strip() == "4.00%", rows


def test_calendar_time_honesty_at_the_event_minute(browser):
    """At exactly 12:30Z the GDP row is a result (time <= now), nothing is next, and the countdown is not negative."""
    nxt, sub, rows = _cal_text(browser, "2026-10-29T12:30:00Z", FF)
    assert nxt == "none left", nxt
    assert [r[1] for r in rows][0] == "Advance GDP q/q" and len(rows) == 3, rows
    assert "-" not in nxt
    # a minute earlier the GDP row must not be listed as a result
    _, _, rows2 = _cal_text(browser, "2026-10-29T12:29:00Z", FF)
    assert "Advance GDP q/q" not in [r[1] for r in rows2], rows2


def test_no_calendar_without_data(browser):
    nxt, sub, rows = _cal_text(browser, "2026-10-29T12:00:00Z", None)
    assert nxt == "NO CALENDAR" and rows == [], (nxt, rows)


def test_no_calendar_on_429_then_numbers_on_200(browser):
    """Normal mode (no replay): a 429 from the feed gives NO CALENDAR and no numbers; a 200 with the fixture gives the strip."""
    for status, want_numbers in ((429, False), (200, True)):
        ctx, page, errs = _cal_page(browser, "2026-10-29T12:00:00Z", offline=False)
        try:
            page.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())      # local files load, every other feed is down
            body = json.dumps(FF) if status == 200 else "slow down"

            def answer(route, _request=None, st=status, b=body):
                route.fulfill(status=st, body=b, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"})
            page.route(CAL_URL_GLOB, answer)
            page.clock.set_fixed_time(datetime.datetime(2026, 10, 29, 12, 0, tzinfo=datetime.timezone.utc))
            page.goto(PAGE.resolve().as_uri(), wait_until="load", timeout=30000)
            page.wait_for_timeout(1500)
            nxt = page.inner_text("#mc-next")
            if want_numbers:
                assert nxt == "in 30 min", nxt
            else:
                assert nxt == "NO CALENDAR" and "429" in page.inner_text("#mc-sub") and page.query_selector_all("#mc-rows tr") == [], (nxt, page.inner_text("#mc-sub"))
        finally:
            ctx.close()


def _snap_page_text(browser, snap_js, cors_feed=False):
    """Normal mode, every network call aborted (the feed has no CORS header), the same-origin snapshot file served as snap_js (None = file missing)."""
    ctx, page, errs = _cal_page(browser, "2026-10-29T12:00:00Z", offline=False)
    try:
        def local(route):
            if "ff_calendar_snapshot.js" in route.request.url:
                if snap_js is None:
                    route.abort()
                else:
                    route.fulfill(status=200, body=snap_js, content_type="application/javascript")
            elif route.request.url.startswith("file:"):
                route.continue_()
            else:
                route.abort()                                    # incl. nfs.faireconomy.media: blocked like a real CORS failure
        page.route("**/*", local)
        page.clock.set_fixed_time(datetime.datetime(2026, 10, 29, 12, 0, tzinfo=datetime.timezone.utc))
        page.goto(PAGE.resolve().as_uri(), wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        return page.inner_text("#mc-next"), page.inner_text("#mc-sub")
    finally:
        ctx.close()


def test_snapshot_file_feeds_the_strip_when_the_feed_is_cors_blocked(browser):
    """Snapshot written by ff_calendar_snapshot.render, 1 h old at 12:00Z 10-29: next High USD = Advance GDP at 12:30Z -> 'in 30 min'."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ffsnap", HERE.parents[2] / "scripts/dev/ff_calendar_snapshot.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    now_ms = int(datetime.datetime(2026, 10, 29, 12, 0, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    nxt, sub = _snap_page_text(browser, m.render(FF, now_ms - 3600_000))
    assert nxt == "in 30 min" and "Advance GDP q/q at 12:30Z" in sub, (nxt, sub)
    nxt, sub = _snap_page_text(browser, m.render(FF, now_ms - 27 * 3600_000))      # 27 h old -> too old
    assert nxt == "NO CALENDAR", (nxt, sub)
    nxt, sub = _snap_page_text(browser, None)                                       # no file, feed blocked
    assert nxt == "NO CALENDAR" and "no snapshot file" in sub, (nxt, sub)
    nxt, sub = _snap_page_text(browser, "window.LIVEAID_CAL_SNAP = {};")            # unreadable copy
    assert nxt == "NO CALENDAR", (nxt, sub)


def test_snapshot_script_render_and_refusal():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ffsnap", HERE.parents[2] / "scripts/dev/ff_calendar_snapshot.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = m.render(FF, 1234)
    assert out.startswith("window.LIVEAID_CAL_SNAP = {\"fetched_ms\":1234,\"events\":[") and out.endswith(";" + chr(10))
    assert json.loads(out[len("window.LIVEAID_CAL_SNAP = "):-2])["events"] == FF
    with pytest.raises(ValueError):
        m.render([], 1)


# ---------- "What the money is doing" (OI_COMMENTARY_SPEC.md): the 10-30 18:50Z flush replayed through the rendered tile ----------
# window.LIVEAID_OI = the committed Bybit 5m fixture (klines + OI snapshots); the page keeps only rows stamped <= now, as the
# live REST call would return them. Clock 19:10:30Z: the 18:50 and 19:00 flush bars are closed, the 19:10 bar is forming.
OIFX = json.loads((HERE / "fixture_bybit_flush_1030.json").read_text(encoding="utf-8"))
OI_NOW = datetime.datetime(2026, 10, 30, 19, 10, 30, tzinfo=datetime.timezone.utc)


def _money(browser, inject=True):
    ctx = browser.new_context(offline=True, viewport={"width": 1400, "height": 900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    try:
        if inject:
            page.add_init_script("window.LIVEAID_OI = " + json.dumps({"klines": OIFX["klines"], "oi": OIFX["oi"]}) + ";")
        page.clock.set_fixed_time(OI_NOW)
        page.goto(PAGE.resolve().as_uri() + "?replay=fixture", wait_until="load", timeout=30000)
        page.wait_for_timeout(1300)
        rows = page.eval_on_selector_all("#m-rows tr", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))")
        return rows, page.inner_text("#m-lines"), page.inner_text("#m-call"), errs
    finally:
        ctx.close()


def _bybit_window(mins):
    """Independent: Bybit samples = (kline open time, open price, OI snapshot at that time), newest at or before now; base =
    newest sample at least `mins` old. Returns (price change %, OI change %) as the page prints them (2 dp, signed)."""
    now = int(OI_NOW.timestamp() * 1000)
    oi = {int(t): v for t, v in OIFX["oi"].items()}
    pts = [(k[0], k[1], oi[k[0]]) for k in OIFX["klines"] if k[0] <= now and oi.get(k[0], 0) > 0]
    last = pts[-1]
    base = [p for p in pts if p[0] <= now - mins * 60000][-1]
    f = lambda x: ("+" if x > 0 else "") + f"{x:,.2f}"
    return f((last[1] / base[1] - 1) * 100) + "%", f((last[2] / base[2] - 1) * 100) + "%"


def test_money_tile_replays_the_1850_flush(browser):
    rows, lines, call, errs = _money(browser)
    assert not errs, errs
    assert "FLUSH 18:50Z, low 76232, price -0.55 %, OI -0.37 % (-256 BTC), longs liquidated" in lines, lines
    assert "2 bars hit within 60 min, the last 19:00Z" in lines, lines
    by = {r[0]: r for r in rows}
    assert list(by) == ["5 min", "15 min", "60 min"], rows
    for w, mins in (("5 min", 5), ("15 min", 15), ("60 min", 60)):
        px, doi = _bybit_window(mins)
        r = by[w]
        assert r[2] == "NOT_IN_DATA" and r[4] == "NOT_IN_DATA", r   # Deribit and Binance: no samples in replay
        assert r[3] == doi and r[5] == doi and r[1] == px, (w, r, px, doi)   # one venue: all-venues net = Bybit
    assert call != "NOT_IN_DATA" and call != "--", call


def test_money_tile_without_oi_reads_not_in_data(browser):
    rows, lines, call, errs = _money(browser, inject=False)
    assert not errs, errs
    assert call == "NOT_IN_DATA" and "FLUSH" not in lines and "NOT_IN_DATA" in lines, (call, lines)


# ---------- Position bar: #pos-dist, #pos-atr, #uncovered (live_aid.html renderTop "2. position") ----------
# The page has no replay hook for the Deribit mark (S is closed over), so the test serves an in-memory copy of live_aid.html
# with one injected line in the replay branch (S.dbt/S.dbtMark from window.LIVEAID_MARK); live_aid.html itself is untouched.
# Bars are flat: every 1m bar o=c=100000, h=100010, l=99990, so every 15m bar has range 20 and the Wilder ATR14 is exactly 20.
# Hand-computed: short, entry 100100, mark 100060 -> entry - mark = +40.0 pts; 40 / 20 = +2.00 x ATR15;
# size 1000 USD with rungs 300 + 200 -> uncovered 1000 - 500 = 500 USD of 1,000.
PB_T0 = 1_793_318_400_000          # 2026-10-30 00:00:00Z, a 15m boundary
PB_ROWS = [[PB_T0 + i * 60_000, 100000, 100010, 99990, 100000, 1] for i in range(600)]   # 40 whole 15m bars
PB_NOW = PB_ROWS[-1][0] + 60_000
PB_STORE = {"side": "short", "size": "1000", "entry": "100100", "rungs": [{"price": 100300, "size": 300}, {"price": 100500, "size": 200}], "levels": []}
PB_HOOK = "setInterval(render, 1000);\n    route();\n    return;"
PB_WANT = {"pos-dist": "+40.0 pts", "pos-atr": "+2.00 x ATR15", "uncovered": "uncovered 500 USD of 1,000"}
# Fail-first: each mutation edits one formula in the served copy; the comparison must then differ.
PB_MUTATIONS = {
    "dist-sign": ("var d = entry - mark;", "var d = mark - entry;"),
    "atr-divide": ("sgn(d / a15, 2) + ' x ATR15'", "sgn(d * a15, 2) + ' x ATR15'"),
    "uncovered-sum": ("fmt(size - covered, 0)", "fmt(size + covered, 0)"),
}


def _posbar(browser, mutate=None):
    src = PAGE.read_text(encoding="utf-8")
    assert src.count(PB_HOOK) == 1, "replay branch moved: update PB_HOOK"
    src = src.replace(PB_HOOK, "S.dbt = S.dbtMark = S.dbtIdx = window.LIVEAID_MARK; S.dbtF8 = 0.0001; S.oi = 1e8; S.oiT = Date.now(); S.dbtT = Date.now();\n    " + PB_HOOK)
    if mutate:
        old, new = PB_MUTATIONS[mutate]
        assert src.count(old) == 1, ("formula text moved", mutate)
        src = src.replace(old, new)
    uri = PAGE.resolve().as_uri()
    ctx = browser.new_context(offline=True, viewport={"width": 1400, "height": 900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    try:
        page.route(uri + "*", lambda route: route.fulfill(status=200, content_type="text/html", body=src)
                   if route.request.url.split("?")[0] == uri else route.continue_())
        page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(PB_ROWS) + "; window.LIVEAID_MARK = 100060;"
                             "localStorage.setItem('liveaid.v1', " + json.dumps(json.dumps(PB_STORE)) + ");")
        page.clock.set_fixed_time(datetime.datetime.fromtimestamp(PB_NOW / 1000, tz=datetime.timezone.utc))
        page.goto(uri + "?replay=fixture", wait_until="load", timeout=30000)
        page.wait_for_timeout(1300)
        return {i: page.inner_text("#" + i).strip() for i in PB_WANT}, errs
    finally:
        ctx.close()


def test_position_bar_distance_atr_and_uncovered_render(browser):
    got, errs = _posbar(browser)
    assert not errs, errs
    assert got == PB_WANT, got


@pytest.mark.parametrize("mutation", sorted(PB_MUTATIONS))
def test_position_bar_comparison_catches_a_changed_formula(browser, mutation):
    got, errs = _posbar(browser, mutate=mutation)
    assert not errs, errs
    assert got != PB_WANT, (mutation, got)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
