"""One-screen Home (home_one.js, requirement R27, operator 2026-11-13 19:05Z: "we just need the home screen").

1. Pure rules in node, expected values written here by hand (not from the module): news filter (BTC or whole market AND a matched word rule),
   BUILDING / FADING trend, 2 h drop, 5-row cap, "x / 10" score, price since the headline, Bollinger band width (BB 20, 2 SD, population),
   US-open window (weekday, 3 h before to 2 h after), Ahead buckets and the "calendar not loaded" line, stale chip.
2. Rendered page (?replay=fixture, headless Chromium, 1920x1080, network off): tab bar Home | In trade | Details, no NOT_IN_DATA text on the
   Home face (the previous Home, kept under #homeold, does show it: negative control), every tile has an age stamp, nothing taller than
   the viewport, a rich synthetic input fills every tile (band width equals the hand calculation), Details still reaches the old panels.
Skips (never fails) without node, the playwright package or a Chromium.
"""
import datetime
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MOD = HERE / "home_one.js"
PAGE = HERE / "live_aid.html"
KLINES = json.loads((HERE / "fixture_klines.json").read_text(encoding="utf-8"))["klines"]
NOW_MS = int(KLINES[-1][0]) + 60_000
M = 60_000
H = 3_600_000

# Monday 2026-11-16 12:00Z (US standard time: cash open 14:30Z). 2026-11-14 is a Saturday.
MON = int(datetime.datetime(2026, 11, 16, 12, 0, tzinfo=datetime.timezone.utc).timestamp() * 1000)
OPEN_MON = int(datetime.datetime(2026, 11, 16, 14, 30, tzinfo=datetime.timezone.utc).timestamp() * 1000)


def node_eval(expr, arg=None):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not on PATH")
    runner = ("const O=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{const A=j?JSON.parse(j):null;"
              "process.stdout.write(JSON.stringify((function(O,A){" + expr + "})(O,A)))})")
    out = subprocess.run([node, "-e", runner, str(MOD)], input=json.dumps(arg), capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout)


# ---------------- news filter ----------------
def _n(i, mins, title, imp, coins=()):
    return {"_id": i, "time": NOW_MS - int(mins * M), "title": title, "importance": imp, "suggestions": [{"coin": c} for c in coins], "source": "t"}


def _rows(items, rows1m=None, px=None):
    return node_eval("return O.newsRows(A.items, A.now, A.rows1m, A.px);", {"items": items, "now": NOW_MS, "rows1m": rows1m, "px": px})


def test_news_filter_keeps_btc_and_market_with_a_rule_only():
    items = [
        _n("etf", 5, "SEC approves options on spot Bitcoin ETFs", 8.2, ["BTC"]),            # BTC + etf up rule -> UP
        _n("cpi", 20, "US CPI rises 0.3% in September, as expected", 7.0),                  # whole market, macro rule -> VOLATILE
        _n("hack", 10, "POTENTIAL BINANCE HACK ONGOING - ONCHAIN", 7.4),                    # exchange named + hack rule -> DOWN
        _n("eth", 3, "ETHEREUM FOUNDATION SELLS 1,000 ETH", 9.0, ["ETH"]),                  # another coin: dropped even at 9.0
        _n("sol", 4, "SOL ETF inflows hit record", 8.0, ["SOL"]),                           # etf rule but about SOL: dropped
        _n("defi", 6, "Hackers drain 40M from a DeFi lender", 8.5),                         # hack rule, no BTC, no exchange: dropped
        _n("norule", 2, "Bitcoin developers discuss a new soft fork proposal", 9.8, ["BTC"]),  # top band but no rule: never invented
    ]
    got = {r["id"]: r for r in _rows(items)}
    assert set(got) == {"etf", "cpi", "hack"}, sorted(got)
    assert (got["etf"]["chip"], got["etf"]["coin"]) == ("UP", "BTC")
    assert (got["cpi"]["chip"], got["cpi"]["coin"]) == ("VOLATILE", "MKT")
    assert (got["hack"]["chip"], got["hack"]["coin"]) == ("DOWN", "MKT")


def test_news_score_is_x_over_ten():
    assert node_eval("return [O.scoreTxt(8.2), O.scoreTxt(null), O.NEWS_MAX];") == ["8.2 / 10", "-- / 10", 10]


def test_news_trend_building_fading_and_two_hour_drop():
    items = [
        # etf story: 1 headline in the last 30 min, 1 in the 30 min before -> equal and non-zero = BUILDING
        _n("e1", 5, "SEC approves Bitcoin ETF options", 8, ["BTC"]), _n("e2", 40, "Bitcoin ETF launch approved in Hong Kong", 7, ["BTC"]),
        # war story: nothing in the last 30 min, two before, newest 45 min old -> FADING but younger than 2 h: still listed
        _n("w1", 45, "Missiles hit oil terminal as war widens, Bitcoin dips", 7.5, ["BTC"]), _n("w2", 50, "New sanctions announced, Bitcoin falls", 7.1, ["BTC"]),
        # macro story: only a 3 h old headline -> FADING and older than 2 h: dropped
        _n("m1", 180, "US CPI rises 0.3% in September", 7.0),
    ]
    got = {r["key"]: r for r in _rows(items)}
    assert set(got) == {"etf up", "war"}, sorted(got)
    assert got["etf up"]["trend"] == "BUILDING" and got["etf up"]["id"] == "e1" and (got["etf up"]["recent"], got["etf up"]["prior"]) == (1, 1)
    assert got["war"]["trend"] == "FADING" and got["war"]["id"] == "w1" and (got["war"]["recent"], got["war"]["prior"]) == (0, 2)


def test_news_building_when_more_recent_than_before():
    items = [_n("a", 2, "Bitcoin hacked exchange hot wallet drained", 8), _n("b", 12, "Binance hack: funds drained", 8), _n("c", 40, "Kraken hack suspected", 7)]
    r = _rows(items)
    assert len(r) == 1 and r[0]["key"] == "hack" and r[0]["trend"] == "BUILDING" and (r[0]["recent"], r[0]["prior"]) == (2, 1)


def test_news_at_most_five_rows_newest_first():
    items = [_n("hack", 1, "Bitcoin exchange hack", 8), _n("halt", 2, "Binance halts withdrawals", 8), _n("macro", 3, "FOMC holds rates, Bitcoin flat", 8), _n("war", 4, "War widens, Bitcoin falls", 8),
             _n("etf", 5, "Bitcoin ETF approved", 8, ["BTC"]), _n("sell", 6, "Bitcoin miners sell record amount", 8, ["BTC"]), _n("buy", 7, "Strategy buys 5,000 BTC", 8, ["BTC"])]
    r = _rows(items)
    assert len(r) == 5
    assert [x["id"] for x in r] == sorted([x["id"] for x in r], key=lambda i: [y["_id"] for y in items].index(i))   # newest first


def test_news_since_headline_percent():
    t0 = NOW_MS - 20 * M
    rows = [[t0 - M, 99_000, 99_500, 98_900, 99_100], [t0, 100_000, 100_200, 99_900, 100_100], [t0 + M, 100_100, 100_500, 100_000, 100_400]]
    r = _rows([_n("etf", 20, "SEC approves Bitcoin ETF", 8, ["BTC"])], rows, 101_000)
    assert r[0]["since"] == pytest.approx(1.0, abs=1e-9)    # 101,000 vs the open 100,000 of the bar that holds the headline
    assert _rows([_n("etf", 20, "SEC approves Bitcoin ETF", 8, ["BTC"])], rows[:1], 101_000)[0]["since"] is None   # headline outside the loaded bars


# ---------------- band width ----------------
def _bars(closes, step=15 * M, t0=0):
    return [[t0 + i * step, c, c, c, c, 1, t0 + (i + 1) * step - 1] for i, c in enumerate(closes)]


def test_band_width_matches_hand_calculation():
    # 20 closes alternating 100 / 110: mean 105, population SD 5, width = (upper - lower) / middle = 4 x 5 / 105
    closes = [100.0 if i % 2 == 0 else 110.0 for i in range(60)]
    r = node_eval("return O.bbWidth(A.rows, A.now);", {"rows": _bars(closes), "now": 10**12})
    assert r["width"] == pytest.approx(20 / 105, rel=1e-12)
    assert r["pct"] == pytest.approx(1.0) and r["coil"] is False         # every window is identical: the latest is at the top of its history
    assert r["n"] == 41


def test_band_width_coil_when_latest_is_narrowest():
    # wide swings for 60 bars, then 20 flat bars: latest width 0 is the minimum of its history -> percentile = 1 / n -> COIL
    closes = [100.0 + (10 if i % 2 else -10) for i in range(60)] + [100.0] * 20
    r = node_eval("return O.bbWidth(A.rows, A.now);", {"rows": _bars(closes), "now": 10**12})
    assert r["width"] == 0 and r["coil"] is True and r["pct"] <= 0.2
    # needs 20 closed bars; the forming bar (close time ahead of now) is left out
    assert node_eval("return O.bbWidth(A.rows, A.now);", {"rows": _bars(closes[:19]), "now": 10**12}) is None
    rows = _bars([100.0] * 20)
    assert node_eval("return O.bbWidth(A.rows, A.now);", {"rows": rows, "now": rows[-1][6] - 1}) is None   # 19 closed + 1 forming


# ---------------- US open window and Ahead ----------------
def test_us_open_window_weekdays_only_three_hours_before_to_two_after():
    w = lambda now, open_: node_eval("return O.usWindow(A.o, A.n);", {"o": open_, "n": now})
    assert w(MON, OPEN_MON)["show"] is True
    assert w(OPEN_MON - 3 * H - M, OPEN_MON)["show"] is False                        # just over 3 h before
    assert w(OPEN_MON + 2 * H - M, OPEN_MON)["show"] is True                         # just under 2 h after
    assert w(OPEN_MON + 2 * H + M, OPEN_MON)["show"] is False
    sat = int(datetime.datetime(2026, 11, 14, 14, 0, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    open_sat = int(datetime.datetime(2026, 11, 14, 14, 30, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    r = w(sat, open_sat)                                                             # Saturday: next open is Monday, never shown
    assert r["show"] is False and r["t"] == OPEN_MON


def test_ahead_buckets_today_week_month():
    # Monday 12:00Z: today ends Tue 00:00Z; this week ends Mon 2026-11-23 00:00Z; this month ends 2026-12-01 00:00Z
    ts = {"today": MON + 5 * H, "week": MON + 3 * 24 * H, "month": MON + 12 * 24 * H, "later": MON + 20 * 24 * H}
    got = {k: node_eval("return O.bucket(A.t, A.now);", {"t": t, "now": MON}) for k, t in ts.items()}
    assert got == {k: k for k in ts}


def test_ahead_calendar_not_loaded_names_the_command():
    html = node_eval("global.EVENTS_STRIP_DATA = {schedule: []}; return O.aheadTile({now: A.now, usOpenT: 0, cal: null}, A.now, {});", {"now": MON})
    assert "calendar not loaded" in html and "ff_calendar_snapshot.py" in html and "o1-age" in html


def test_ahead_lists_scheduled_events_with_utc_and_ist():
    strip = {"schedule": [{"id": "cpi", "cls": "CPI", "t0": MON + 3 * H}, {"id": "nfp", "cls": "NFP", "t0": MON + 3 * 24 * H}]}
    call = "global.EVENTS_STRIP_DATA = A.strip; return O.aheadTile({now: A.now, usOpenT: A.open, cal: null}, A.now, {});"
    near = node_eval(call, {"now": MON, "strip": strip, "open": OPEN_MON})              # 2.5 h before the open: the US-open tile is on Home, so Ahead drops its countdown line
    assert "US cash open countdown" not in near
    html = node_eval(call, {"now": MON - 6 * H, "strip": strip, "open": OPEN_MON})      # 8.5 h before: collapsed into the Ahead countdown line
    assert "calendar not loaded" not in html
    assert "CPI inflation" in html and "15:00Z" in html and "20:30 IST" in html          # 12:00Z + 3 h; IST = UTC + 5:30
    assert "Jobs report (NFP)" in html and "US cash open countdown" in html and "HIGH" in html


def test_age_stamp_goes_amber_stale_past_the_limit():
    now = 10**12
    fresh = node_eval("return O.age(A.t, A.now, 30000, 'price');", {"t": now - 12_000, "now": now})
    old = node_eval("return O.age(A.t, A.now, 30000, 'price');", {"t": now - 200_000, "now": now})
    none = node_eval("return O.age(0, A.now, 30000, 'price');", {"now": now})
    assert not fresh["stale"] and "12s ago" in fresh["html"] and "stale" not in fresh["html"]
    assert old["stale"] and "STALE 3m" in old["html"] and 'class="o1-age stale"' in old["html"]
    assert none["stale"] and "STALE" in none["html"]


# ---------------- rendered page ----------------
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


NEWS = [_n("n1", 2, "POTENTIAL BINANCE HACK ONGOING - ONCHAIN", 7.4), _n("n2", 9, "SEC APPROVES OPTIONS ON SPOT BITCOIN ETFS", 7.8, ["BTC"]),
        _n("n3", 15, "ETHEREUM FOUNDATION SELLS 1,000 ETH", 5.0, ["ETH"]), _n("n5", 50, "Bitcoin developers discuss a new soft fork proposal", 3.1, ["BTC"])]


def _open(browser, hash_="#home", news=True, w=1920, h=1080):
    ctx = browser.new_context(offline=True, viewport={"width": w, "height": h})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    page.add_init_script("window.LIVEAID_REPLAY = " + json.dumps(KLINES) + ";")
    if news:
        page.add_init_script("window.LIVEAID_NEWS = " + json.dumps(NEWS) + ";")
    page.clock.set_fixed_time(datetime.datetime.fromtimestamp(NOW_MS / 1000, tz=datetime.timezone.utc))
    page.goto(PAGE.resolve().as_uri() + "?replay=fixture" + hash_, wait_until="load", timeout=30000)
    page.wait_for_timeout(1300)
    return ctx, page, errs


def test_tab_bar_is_home_in_trade_details(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        assert page.eval_on_selector_all("#tabs a", "as => as.map(a => a.innerText)") == ["Home", "In trade", "Details"]
    finally:
        ctx.close()


def test_home_face_never_says_not_in_data(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        face = page.inner_text("#p-home")
        assert "NOT_IN_DATA" not in face, face[:400]
        assert page.eval_on_selector_all("#p-home .o1-tile", "ts => ts.length") >= 10
        # negative control: the previous Home (kept under Details) still prints NOT_IN_DATA on the same feed state, so this test can fail
        page.evaluate("location.hash = '#homeold'"); page.wait_for_timeout(400)
        assert "NOT_IN_DATA" in page.inner_text("#p-home-old")
    finally:
        ctx.close()


def test_every_home_tile_has_one_age_stamp(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        tiles = page.eval_on_selector_all("#p-home .o1-tile", "ts => ts.map(t => [t.dataset.tile, t.querySelectorAll('.o1-age').length])")
        assert {t[0] for t in tiles} >= {"chart", "board", "level", "winning", "forced", "money", "coil", "adx", "wt", "news", "ahead"}, tiles
        assert all(n == 1 for _, n in tiles), tiles
        feeds = page.eval_on_selector_all("#p-home .o1-top .o1-age", "es => es.map(e => e.dataset.feed)")
        assert feeds == ["price", "open interest", "news"], feeds
    finally:
        ctx.close()


def test_home_fits_1920x1080_without_scrolling(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        m = page.evaluate("""() => { const h = document.getElementById('p-home'), vh = innerHeight, vw = innerWidth;
            const tiles = Array.from(h.querySelectorAll('.o1-tile, .o1-top')).map(t => { const r = t.getBoundingClientRect(); return [t.id || t.className, r.top, r.bottom, r.right, t.scrollHeight - t.clientHeight]; });
            return { vh, vw, doc: document.documentElement.scrollHeight, home: [h.scrollHeight, h.clientHeight], tiles }; }""")
        assert m["doc"] <= m["vh"] and m["home"][0] <= m["home"][1] + 1, m
        for name, top, bottom, right, over in m["tiles"]:
            assert top >= 0 and bottom <= m["vh"] + 0.5 and right <= m["vw"] + 0.5, (name, top, bottom, right)
        grid = page.evaluate("""() => { const c = document.getElementById('o1-chart').getBoundingClientRect(), g = document.querySelector('.o1-grid').getBoundingClientRect(); return [c.width, g.width]; }""")
        assert 0.50 <= grid[0] / (grid[0] + grid[1]) <= 0.60, grid   # chart about 55 % of the width
    finally:
        ctx.close()


def test_news_tile_in_page_scores_x_of_ten_and_drops_other_coins(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        rows = page.eval_on_selector_all("#o1-news .o1-nr[data-news]", "rs => rs.map(r => Array.from(r.children).map(c => c.innerText))")
        heads = [r[3] for r in rows]
        assert any("BINANCE HACK" in h for h in heads) and any("SPOT BITCOIN ETFS" in h for h in heads), rows
        assert not any("ETHEREUM FOUNDATION" in h for h in heads) and not any("soft fork" in h for h in heads), rows    # other coin / no rule
        assert all(r[1] in ("7.4 / 10", "7.8 / 10") for r in rows), rows
        assert {r[4] for r in rows} <= {"UP", "DOWN", "VOLATILE"} and {r[5] for r in rows} <= {"BUILDING", "FADING"}, rows
    finally:
        ctx.close()


def test_news_tile_quiet_message_with_last_checked_time(browser):
    ctx, page, errs = _open(browser, news=False)
    try:
        assert not errs, errs
        assert "news feed not connected" in page.inner_text("#o1-news") or "no market-moving news" in page.inner_text("#o1-news")
        txt = page.evaluate("""() => { const o = LAONE.newsTile({now: Date.now(), newsItems: [], rows1m: null, px: 0}, Date.now(), {news: Date.now() - 5000}); return o; }""")
        assert "no market-moving news" in txt and "checked" in txt and "o1-age" in txt
    finally:
        ctx.close()


def _synthetic_bars(n, step, last_close_t):
    """Deterministic drifting saw: close_i = 100000 + 40*i + 900*sin(i/3); returns Binance-style rows [t, o, h, l, c, v, closeT]."""
    closes = [100_000 + 40 * i + 900 * math.sin(i / 3) for i in range(n)]
    rows = []
    t0 = last_close_t - n * step
    for i, c in enumerate(closes):
        o = closes[i - 1] if i else c
        rows.append([t0 + i * step, o, max(o, c) + 50, min(o, c) - 50, c, 10 + (i % 5), t0 + (i + 1) * step - 1])
    return rows, closes


def _hand_width(closes, n=20):
    w = []
    for i in range(n - 1, len(closes)):
        win = closes[i - n + 1:i + 1]
        mean = sum(win) / n
        sd = math.sqrt(sum((x - mean) ** 2 for x in win) / n)
        w.append(4 * sd / mean)
    return w


def test_rich_inputs_fill_every_tile(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        k15, c15 = _synthetic_bars(150, 15 * M, NOW_MS + 7 * M)    # last bar still forming: closeT in the future
        k1h, c1h = _synthetic_bars(120, H, NOW_MS + 7 * M)
        k5, _ = _synthetic_bars(160, 5 * M, NOW_MS + 2 * M)
        rows5 = [[r[0], r[1], r[2], r[3], r[4]] for r in k5]
        lane = {"side": 1, "zone": "hot", "wt1": 40, "ms": 60000, "last": {"ago": 3, "side": 1, "strong": True}, "bars": []}
        ctx_js = {
            "now": NOW_MS, "px": 102_000, "rows5": rows5, "k5": k5, "k15": k15, "k1h": k1h, "votes": [1, 1, 1, -1, 0, 1], "map": {},
            "boardInputs": {"15m": {"div": {"rsi": 1}, "sweep": 1}, "1h": {"bb": {"out": 1, "cvd": "spike"}}},
            "ind": {"tfs": [["15m"], ["1h"], ["4h"]], "ver": {"15m": {"side": 1, "up": 4, "dn": 1, "n": 6, "coiled": True}, "1h": {"side": -1, "up": 1, "dn": 4, "n": 6}, "4h": {"side": 0, "up": 2, "dn": 2, "n": 6}}, "r": {}},
            "lanes": {tf: lane for tf in ["1m", "2m", "3m", "15m", "30m", "4h"]},
            "money": {"text": "x", "label": "15 min", "n": 3, "dp": 0.004, "doi": 0.006, "venues": [{"name": "Deribit", "btc": 1, "share": .5}, {"name": "Bybit", "btc": 1, "share": .3}, {"name": "Binance", "btc": 1, "share": .2}],
                      "missing": ["Gate: HTTP 429 rate limited", "OKX: no data yet", "Kraken: NOT_IN_DATA", "Bitget: timeout"]},
            "moneyRows": [{"label": "5 min", "net": {"dp": 0.0003, "doi": -0.0021}}, {"label": "15 min", "net": {"dp": 0.004, "doi": 0.006}}, {"label": "60 min", "net": {"dp": -0.01, "doi": 0.004}}],
            "venueTotal": 12, "kAdx": {"5m": k5, "15m": k15, "1h": k1h, "4h": k1h},
            "feeds": {"price": NOW_MS - 3000, "oi": NOW_MS - 20_000, "news": NOW_MS - 5000, "candles": NOW_MS - 30_000},
            "newsItems": NEWS, "rows1m": [[r[0], r[1], r[2], r[3], r[4]] for r in KLINES], "cal": None, "usOpenT": 0,
        }
        page.evaluate("c => { const r = LAONE.render; LAONE.render = function () {}; r(document.getElementById('p-home'), c); }", ctx_js)
        face = page.inner_text("#p-home")
        assert "NOT_IN_DATA" not in face and "HTTP 429" not in face and "timeout" not in face, face
        # Money: only venues that HAVE data on the face, a count, the missing names in the hover
        money = page.inner_text("#o1-money")
        assert "3 of 12 venues" in money and "Gate" not in money and "429" not in money
        tip = page.get_attribute("#o1-money .o1-sm", "title")
        assert all(n in tip for n in ("Gate", "OKX", "Kraken", "Bitget")) and "429" not in tip
        chips = page.eval_on_selector_all("#o1-money .o1-mr:not(.o1-nh) .o1-c", "cs => cs.map(c => c.innerText)")
        # 5m: price +0.03 % (flat), OI -0.21 % -> CLOSING; 15m: +0.4 % / +0.6 % -> NEW LONGS; 60m: -1.0 % / +0.4 % -> NEW SHORTS
        assert chips == ["CLOSING", "NEW LONGS", "NEW SHORTS"], chips
        # Coil: band width equals the hand calculation on the closed 15m bars (the forming last bar is left out)
        w15 = _hand_width(c15[:-1])[-1] * 100
        w1h = _hand_width(c1h[:-1])[-1] * 100
        coil = page.inner_text("#o1-coil")
        assert f"{w15:.2f}%" in coil and f"{w1h:.2f}%" in coil, (w15, w1h, coil)
        assert "p" in coil and ("COIL" in coil or "no coil" in coil)
        # board, level tile text, winning, ADX, WaveTrend
        assert "LONG 2" in page.inner_text("#o1-board") and "SHORT 1" in page.inner_text("#o1-board")
        win = page.inner_text("#o1-winning")
        assert "UP" in win and "DOWN" in win and "MIXED" in win and "COILED" in win
        adx = page.inner_text("#o1-adx")
        assert all(tf in adx for tf in ("5m", "15m", "1h", "4h")) and ("TREND" in adx or "WEAK" in adx or "BUILDING" in adx or "NO TREND" in adx), adx
        wt = page.eval_on_selector_all("#o1-wt .o1-wt", "es => es.length")
        assert wt == 6
        # every tile still carries its single age stamp and the page does not scroll
        assert all(n == 1 for n in page.eval_on_selector_all("#p-home .o1-tile", "ts => ts.map(t => t.querySelectorAll('.o1-age').length)"))
        m = page.evaluate("() => [document.documentElement.scrollHeight, innerHeight, document.getElementById('p-home').scrollHeight, document.getElementById('p-home').clientHeight]")
        assert m[0] <= m[1] and m[2] <= m[3] + 1, m
    finally:
        ctx.close()


def test_stale_feed_shows_amber_chip_with_its_age(browser):
    ctx, page, errs = _open(browser)
    try:
        assert not errs, errs
        page.evaluate("""c => { const r = LAONE.render; LAONE.render = function () {}; r(document.getElementById('p-home'), c); }""", {
            "now": NOW_MS, "px": 102_000, "rows5": [], "votes": [1, 1, 1, -1, 0, 1], "map": {}, "feeds": {"price": NOW_MS - 3000, "oi": NOW_MS - 600_000, "news": NOW_MS - 5000, "candles": NOW_MS - 30_000}})
        oi = page.eval_on_selector("#p-home .o1-top .o1-age[data-feed='open interest']", "e => [e.className, e.innerText]")
        assert "stale" in oi[0] and oi[1] == "STALE 10m", oi
        price = page.eval_on_selector("#p-home .o1-top .o1-age[data-feed='price']", "e => [e.className, e.innerText]")
        assert "stale" not in price[0] and price[1] == "3s ago", price
    finally:
        ctx.close()


def test_details_keeps_every_old_panel(browser):
    ctx, page, errs = _open(browser, "#details")
    try:
        assert not errs, errs
        links = page.eval_on_selector_all("#p-details a", "as => as.map(a => a.getAttribute('href'))")
        assert links == ["#money", "#news", "#usopen", "#now", "#flow", "#playbook", "#homeold"], links
        assert page.eval_on_selector("#tabs a.on", "a => a.innerText") == "Details"
        for h, panel in (("#money", "#p-money"), ("#news", "#p-news"), ("#usopen", "#p-usopen"), ("#now", "#p-ov")):
            page.evaluate(f"location.hash = '{h}'"); page.wait_for_timeout(250)
            assert page.eval_on_selector(panel, "e => e.offsetParent !== null"), h
            assert page.eval_on_selector("#tabs a.on", "a => a.innerText") == "Details"
        assert not errs, errs
    finally:
        ctx.close()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
