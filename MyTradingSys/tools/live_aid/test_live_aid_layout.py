"""Live aid layout (operator order 2026-10-31): the "Now" table on top, click-through detail pages, news readings.

1. newsRead word rules (live_aid_indicators.js), run in node: expected tags are written here by hand from the rule list.
2. Rendered page (?replay=fixture, headless Chromium, network off): the Now table sits first and fits a 1400x900 screen,
   its Momentum RSI equals the strip's, a click opens the detail page and Back returns, the news rows show reading and
   pointer, the verdict news line names the headlines.
Skips (never fails) without node, the playwright package or a Chromium.
"""
import datetime
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
JS = HERE / "live_aid_indicators.js"
PAGE = HERE / "live_aid.html"
KLINES = json.loads((HERE / "fixture_klines.json").read_text(encoding="utf-8"))["klines"]
NOW_MS = int(KLINES[-1][0]) + 60_000
M = 60_000

# Real headline shapes (Tree News fields: _id, time, source, title, importance, suggestions); the hack title is the
# 10-29 20:39Z Tree item quoted in research/news_feeds_2026-10-30/REPORT.md.
NEWS = [
    {"_id": "n1", "time": NOW_MS - 2 * M, "source": "Tree News", "title": "POTENTIAL BINANCE HACK ONGOING - ONCHAIN", "importance": 7.4, "suggestions": []},
    {"_id": "n2", "time": NOW_MS - 9 * M, "source": "Blogs", "title": "SEC APPROVES OPTIONS ON SPOT BITCOIN ETFS", "importance": 7.8, "suggestions": [{"coin": "BTC"}]},
    {"_id": "n3", "time": NOW_MS - 15 * M, "source": "Twitter", "title": "ETHEREUM FOUNDATION SELLS 1,000 ETH", "importance": 5.0, "suggestions": [{"coin": "ETH"}]},
    {"_id": "n4", "time": NOW_MS - 30 * M, "source": "Twitter", "title": "US CPI RISES 0.3% IN SEPTEMBER, AS EXPECTED", "importance": 7.0, "suggestions": []},
    {"_id": "n5", "time": NOW_MS - 50 * M, "source": "Blogs", "title": "Bitcoin developers discuss a new soft fork proposal", "importance": 3.1, "suggestions": [{"coin": "BTC"}]},
]
EXPECT = {"n1": "NEGATIVE", "n2": "POSITIVE", "n3": "NEUTRAL", "n4": "UNKNOWN", "n5": "UNKNOWN"}

RUNNER = r"""
const A = require(process.argv[1]);
const items = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const extra = [
  {title: 'Hackers drain 40M from a DeFi lender'}, {title: 'Kraken halts withdrawals after outage'},
  {title: 'SEC rejects spot ETF filing'}, {title: 'Missiles hit oil terminal as war widens'},
  {title: 'Strategy buys 5,000 BTC'}, {title: 'Bitcoin miners sell record amount'}, {title: 'SOL ETF inflows hit record', suggestions: [{coin: 'SOL'}]},
  {title: 'Coinbase lists a new token', suggestions: ['PEPE']}, {title: ''}, null];
process.stdout.write(JSON.stringify(items.concat(extra).map(x => { const r = A.newsRead(x); return [r.tag, r.react, r.src, r.why]; })));
"""


@pytest.fixture(scope="module")
def reads():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    out = subprocess.run([node, "-e", RUNNER, str(JS)], input=json.dumps(NEWS), capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout)


def test_news_reading_rules(reads):
    tags = [r[0] for r in reads]
    assert tags[:5] == [EXPECT[x["_id"]] for x in NEWS]
    # extra: hack word, withdrawal halt, ETF rejection, war, BTC buy, BTC sell, an ETF headline about SOL only (an ETF rule
    # comes before the not-about-BTC rule), a token listing (not BTC), empty title, null item
    assert tags[5:] == ["NEGATIVE", "NEGATIVE", "NEGATIVE", "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE", "NEUTRAL", "UNKNOWN", "UNKNOWN"]
    hack, cpi, plain = reads[0], reads[3], reads[4]
    assert "-1.4" in hack[1] and "arXiv 2602.07046" in hack[1] and hack[2] == "SOURCED"   # REPORT.md section 3, both studies named
    assert "volatility" in cpi[1] and cpi[2] == "SOURCED"
    assert plain[1].startswith("No rule matched") and plain[2] == "none"
    assert reads[6][1] == "not measured here" and reads[6][2] == "none"          # withdrawal halt: no study, said so
    assert "ETH" in reads[2][1] and reads[2][2] == "SOURCED"                      # neutral cites the Tree coin tags
    assert all(r[3] for r in reads[:13])                                         # every tagged reading names its rule


# ---------- rendered page ----------
@pytest.fixture(scope="module")
def browser():
    pw = pytest.importorskip("playwright.sync_api")
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception as e:  # noqa: BLE001
            pytest.skip("no Chromium: " + str(e).splitlines()[0])
        yield b
        b.close()


def _open(browser, news=True, height=900):
    ctx = browser.new_context(offline=True, viewport={"width": 1400, "height": height})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(KLINES) + ";")
    if news:
        page.add_init_script("window.LIVEAID_NEWS = " + json.dumps(NEWS) + ";")
    page.clock.set_fixed_time(datetime.datetime.fromtimestamp(NOW_MS / 1000, tz=datetime.timezone.utc))
    page.goto(PAGE.resolve().as_uri() + "?replay=fixture", wait_until="load", timeout=30000)
    page.wait_for_timeout(1300)
    return ctx, page, errs


def _ov(page):
    return page.eval_on_selector_all("#ov tr[data-go]", "rs => rs.map(r => [r.dataset.go, Array.from(r.children).map(c => c.innerText)])")


def test_now_table_is_on_top_and_fits_one_screen(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        rows = _ov(page)
        assert [r[1][0] for r in rows[:4]] == ["Momentum", "Levels", "Coil", "Pierce"], rows
        assert {"money", "news", "verdict", "liq", "fund", "macro", "usopen", "intrade"} <= {r[0] for r in rows}, rows
        box = page.eval_on_selector("#p-ov", "e => e.getBoundingClientRect().bottom")
        assert box <= 900, box                                                       # no scroll for the decision rows
        first = page.evaluate("Array.from(document.querySelector('main').children).filter(e => e.offsetParent !== null).map(e => e.id || e.className).slice(0, 2)")
        assert first == ["p-pos", "p-ov"], first
        # Momentum cell: RSI per timeframe, equal to the strip's printed RSI (1m and 5m are in data in the fixture)
        strip = {r[0]: r[1] for r in page.eval_on_selector_all("#strip tr", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))")}
        mom = dict(rows)["momentum"][1]
        for tf in ("1m", "5m"):
            rsi = re.match(r"[\d.]+", strip[tf]).group(0)
            assert f"{tf} {rsi}" in mom, (tf, rsi, mom)
        assert "15m NOT_IN_DATA" in mom, mom                                           # 20 bars < 40: as the strip says
        news = dict(rows)["news"][1]
        assert "POTENTIAL BINANCE HACK ONGOING" in news and "NEGATIVE" in news and "3 high" in news, news
    finally:
        ctx.close()


def test_click_opens_detail_and_back_returns(browser):
    ctx, page, errs = _open(browser)
    try:
        vis = lambda sel: page.eval_on_selector(sel, "e => e.offsetParent !== null")
        page.click("#ov tr[data-go=momentum]")
        page.wait_for_timeout(200)
        assert page.evaluate("location.hash") == "#momentum"
        assert vis("#p-strip") and vis("#back") and not vis("#p-ov") and not vis("#p-levels") and not vis("#p-news"), "momentum detail"
        page.click("#back a")
        page.wait_for_timeout(200)
        assert page.evaluate("location.hash") in ("", "#")
        assert vis("#p-ov") and vis("#p-strip") and not vis("#back"), "top view after Back link"
        page.click("#ov tr[data-go=news]")
        page.wait_for_timeout(200)
        assert vis("#p-news") and not vis("#p-ov") and not vis("#p-strip"), "news detail"
        page.go_back()
        page.wait_for_timeout(300)
        assert vis("#p-ov") and not vis("#back"), "browser Back returns to the top table"
        page.click("#ov tr[data-go=pierce]")
        page.wait_for_timeout(200)
        assert vis("#p-coil") and not vis("#p-ov"), "pierce opens the coil and pierce panel"
        assert not errs, errs
    finally:
        ctx.close()


def test_news_rows_show_reading_pointer_and_gaps(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        rows = page.eval_on_selector_all("#news tr", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))")
        assert len(rows) == len(NEWS), rows
        for x, r in zip(NEWS, rows):   # newest first, as the feed is sorted
            t = datetime.datetime.fromtimestamp(x["time"] / 1000, tz=datetime.timezone.utc).strftime("%H:%M:%S")
            assert r[0].startswith(t) and r[2] == x["source"] and r[3].startswith(x["title"]) and r[4] == EXPECT[x["_id"]], (x, r)
            assert r[5], r
        assert "-1.4" in rows[0][5] and "volatility" in rows[3][5] and rows[4][5].startswith("No rule matched")
        gaps = page.inner_text("#news-gaps")
        for g in ("N4", "N5", "live-aid-macro-calendar-cors-snapshot", "live-aid-news-panel"):
            assert g in gaps, gaps
        acts = page.inner_text("#v-acts")
        assert "POTENTIAL BINANCE HACK ONGOING" in acts and "Moves can be fast" not in acts, acts
    finally:
        ctx.close()


def test_no_news_reads_not_in_data_everywhere(browser):
    ctx, page, errs = _open(browser, news=False)
    try:
        assert not errs, errs
        assert "NOT_IN_DATA" in dict(_ov(page))["news"][1]
        assert "NOT_IN_DATA" in page.inner_text("#news")
    finally:
        ctx.close()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
