"""Live Aid Map tab (card live-aid-bias-map-one-screen-1109). Operator 11-09: the playbook page was a wall of words; he trades from one screen.

Pure rules run in node (level_registry.js, map.js): levels within 0.15 % merge into one zone with merged badges, the ladder keeps the
3 nearest zones each side, the bias dial counts the sections that agree, the same event or headline never shows twice, the rendered
Map stays at 60 words or fewer. The rendered page (headless Chromium, network off, ?replay=fixture) must fit one screen with no scroll at
1920x1040 and at 400x860, with 60 words or fewer; the phone page (build_artifact.py --playbook) must fit 400x860 as well.
Expected numbers are written by hand. Skips (never fails) without node, the playwright package or a Chromium.
"""
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_artifact  # noqa: E402
import test_daily_playbook as T  # noqa: E402

REG = HERE / "level_registry.js"
MAP = HERE / "map.js"
PAGE = HERE / "live_aid.html"
WORD_BUDGET = 60
SIZES = [(1920, 1040), (400, 860)]


def _node(mod, fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(mod)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr[-1500:]
    return json.loads(out.stdout)


def words(html):
    return len(re.sub(r"<[^>]+>", " ", html).replace("&middot;", " ").split())


@pytest.fixture(scope="module")
def sample(tmp_path_factory):
    d = tmp_path_factory.mktemp("map")
    (data, _) = T.build(d, analysts=[{"level": 114.9, "analyst": "Cobra", "bias": "BEARISH", "published": "2026-11-01", "said": "sell the rip"},
                                     {"level": 105.0, "analyst": "Big Cheds", "bias": "BULLISH", "published": "2026-11-01", "said": "bid"}])
    return data


NOW = T.ms(2026, 11, 2, 10) + 1800000


# ---------- level registry: one level shows once ----------

def test_two_sources_within_015_percent_make_one_zone_with_both_badges():
    z = _node(REG, "merge", [{"price": 100000, "src": "playbook", "label": "High", "badge": "PDH"},
                             {"price": 100140, "src": "analyst", "label": "Analyst", "badge": "CB"}])
    assert len(z) == 1, z                                                    # 0.14 % apart
    assert z[0]["badges"] == ["PDH", "CB"] and z[0]["n"] == 2 and z[0]["label"] == "Cluster"
    assert z[0]["lo"] == 100000 and z[0]["hi"] == 100140


def test_levels_further_than_015_percent_stay_two_zones_and_a_zone_never_chains_wider():
    two = _node(REG, "merge", [{"price": 100000, "src": "playbook", "label": "High", "badge": "PDH"}, {"price": 100160, "src": "ma", "label": "MA", "badge": "1DE200"}])
    assert len(two) == 2, two                                                # 0.16 % apart
    chain = _node(REG, "merge", [{"price": 100000 + 100 * i, "src": "panel", "label": "Low", "badge": "B%d" % i} for i in range(4)])
    assert [c["n"] for c in chain] == [2, 2], chain                          # 100000/100100 | 100200/100300: no zone spans over 0.15 %


def test_same_badge_from_two_sections_is_one_badge():
    z = _node(REG, "merge", [{"price": 100000, "src": "playbook", "label": "High", "badge": "PDH"}, {"price": 100010, "src": "panel", "label": "High", "badge": "PDH"}])
    assert len(z) == 1 and z[0]["badges"] == ["PDH"] and z[0]["label"] == "High" and z[0]["n"] == 2


def test_ladder_keeps_three_nearest_each_side_and_price_inside_a_zone_is_at():
    items = [{"price": p, "src": "playbook", "label": "High", "badge": "B%d" % p} for p in (90, 95, 99, 101, 103, 106, 112, 120)]
    lad = _node(REG, "ladder", _node(REG, "merge", items), 100)
    assert [z["price"] for z in lad["above"]] == [101, 103, 106] and [z["price"] for z in lad["below"]] == [99, 95, 90] and lad["at"] is None
    inside = _node(REG, "ladder", _node(REG, "merge", [{"price": 100, "src": "ma", "label": "MA", "badge": "X"}, {"price": 100.1, "src": "ma", "label": "MA", "badge": "Y"}]), 100.05)
    assert inside["at"] and inside["above"] == [] and inside["below"] == []


def test_registry_sources_become_badges():
    assert _node(REG, "initials", "Big Cheds") == "BC" and _node(REG, "initials", "cobra") == "CO"
    pl = _node(REG, "fromPlaybook", [{"k": "PDH", "name": "Prior day high", "price": 114.0}, {"k": "VAH", "name": "Prior-day VAH", "price": 0}])
    assert [(x["badge"], x["price"]) for x in pl] == [("PDH", 114.0)]        # a zero price is not a level
    ma = _node(REG, "fromMA", [{"tf": "1d", "avgs": {"ema200": {"v": 90.0}, "sma200": None, "ema55": {"v": 99.0}}}, {"tf": "5m", "avgs": {"ema200": {"v": 1.0}}}])
    assert [x["badge"] for x in ma] == ["1DE200", "1DE55"]                   # 5m averages are not ladder levels


def test_the_same_event_or_headline_is_shown_once():
    ev = _node(REG, "dedupe", [{"id": "cpi-2026-11-10", "cls": "CPI"}, {"id": "cpi-2026-11-10", "cls": "CPI"}, {"id": "ppi-2026-11-13", "cls": "PPI"}])
    assert [e["id"] for e in ev] == ["cpi-2026-11-10", "ppi-2026-11-13"]
    hl = _node(REG, "dedupe", [{"title": "US CPI rises 0.3%, as expected"}, {"title": "US CPI RISES 0.3% AS EXPECTED!"}, {"title": "Fed holds"}])
    assert [h["title"] for h in hl] == ["US CPI rises 0.3%, as expected", "Fed holds"]


def test_map_shows_next_event_once_even_if_session_and_next_event_both_name_it(sample):
    d = json.loads(json.dumps(sample))
    t0 = NOW + 3 * 3600000
    d["sessions"][2]["events"] = [{"id": "cpi-x", "cls": "CPI", "t0": t0, "hhmm": "13:30"}]
    d["next_event"] = {"id": "cpi-x", "cls": "CPI", "t0": t0}
    h = _node(MAP, "html", {"data": d, "now": NOW, "px": 110, "votes": [1, 1, 1, 1, 1, None]})
    assert h.count('class="lmn"') == 1 and "CPI 3h0m" in h


# ---------- bias dial ----------

def test_bias_counts_agreeing_sections_from_fixture_verdicts():
    b = _node(MAP, "bias", [1, 1, 1, 1, -1, 0], 6)
    assert (b["dir"], b["agree"], b["total"], b["cls"]) == ("LONG", 4, 6, "up")
    b = _node(MAP, "bias", [-1, -1, -1, 1, 0, None], 6)
    assert (b["dir"], b["agree"], b["n"], b["cls"]) == ("SHORT", 3, 5, "down")
    b = _node(MAP, "bias", [1, 1, -1, -1, 0, 0], 6)                          # 2 bull is not 2 x 2 bear: no lean
    assert (b["dir"], b["bull"], b["bear"], b["cls"]) == ("HOLD", 2, 2, "dim")
    b = _node(MAP, "bias", [1, 1, None, None, None, None], 6)                # under 3 sections in data: fail closed, HOLD
    assert b["dir"] == "HOLD" and b["thin"] is True and b["n"] == 2


def test_dial_agrees_with_the_verdict_board_lean_rule():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    for votes in ([1, 1, 1, 1, -1, 0], [-1, -1, 1, 0, 0, None], [1, 1, -1, -1, 0, 0], [1, -1, None, None, None, None], [0, 0, 0, 1, 1, -1]):
        src = ("const A=require(process.argv[1]),M=require(process.argv[2]);const v=JSON.parse(process.argv[3]);"
               "console.log(JSON.stringify([A.lean(v).call,M.bias(v,6).dir]))")
        out = subprocess.run([node, "-e", src, str(HERE / "live_aid_indicators.js"), str(MAP), json.dumps(votes)], capture_output=True, text=True, timeout=30)
        assert out.returncode == 0, out.stderr[-800:]
        board, dial = json.loads(out.stdout)
        assert {"BULLISH LEAN": "LONG", "BEARISH LEAN": "SHORT"}.get(board, "HOLD") == dial, (votes, board, dial)


def test_playbook_vote_follows_the_session_in_progress(sample):
    assert _node(MAP, "playbookVote", sample, NOW) in (1, -1, 0)
    assert _node(MAP, "playbookVote", None, NOW) is None


# ---------- word budget and fail closed ----------

def test_map_html_is_within_the_word_budget_and_has_no_level_line(sample):
    h = _node(MAP, "html", {"data": sample, "now": NOW, "px": 110, "votes": [1, 1, 1, 1, -1, None],
                            "panel": [{"n": "Day VWAP", "p": 109.0}, {"n": "Prev day high", "p": 112.0}], "analysts": sample["analysts"]})
    assert 'class="pbl"' not in h and "Prior day high" not in h, h[:300]
    n = words(h)
    assert 0 < n <= WORD_BUDGET, (n, re.sub(r"<[^>]+>", " ", h))
    assert h.count('class="lmz ') <= 6 and h.count("lmk ") <= 3 and "LONG" in h


def test_map_fails_closed():
    assert "NOT_IN_DATA" in _node(MAP, "html", {"data": None, "now": NOW})
    assert "NOT_IN_DATA" in _node(MAP, "summary", {"data": None, "now": NOW})


def test_map_marks_a_stale_day(sample):
    assert "STALE" in _node(MAP, "html", {"data": sample, "now": T.ms(2026, 11, 4, 10), "px": 110, "votes": []})
    assert "STALE" not in _node(MAP, "html", {"data": sample, "now": NOW, "px": 110, "votes": []})


def test_scenario_cards_are_three_at_most_and_carry_their_ledger_id(sample):
    sc = _node(MAP, "scenarios", sample, NOW)
    assert 1 <= len(sc) <= 3 and all(re.match(r"S\d+", s["id"]) for s in sc)
    h = _node(MAP, "html", {"data": sample, "now": NOW, "px": 110, "votes": []})
    for s in sc:
        assert 'data-ledger="%s"' % s["id"] in h


# ---------- rendered page: one screen, no scroll ----------

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


def _klines(now_ms, px):
    """The layout fixture's 1m rows moved to end one minute before now_ms and scaled so the last close is px (playbook fixture scale)."""
    rows = json.loads((HERE / "fixture_klines.json").read_text(encoding="utf-8"))["klines"]
    shift, k = now_ms - 60000 - int(rows[-1][0]), px / float(rows[-1][4])
    return [[int(r[0]) + shift] + [float(x) * k for x in r[1:5]] + [r[5]] + list(r[6:]) for r in rows]


def _open(browser, data, size, hash_="#playbook", analysts=None, url=None):
    ctx = browser.new_context(offline=True, viewport={"width": size[0], "height": size[1]})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    init = ["window.LIVEAID_REPLAY = %s;" % json.dumps(_klines(NOW, 110.4)),
            "Object.defineProperty(window,'PLAYBOOK_DATA',{get:function(){return %s;},set:function(){}});" % json.dumps(data)]
    if analysts is not None:
        init.append("Object.defineProperty(window,'LIVE_AID_ANALYSTS',{get:function(){return %s;},set:function(){}});" % json.dumps(analysts))
    page.add_init_script("\n".join(init))
    page.clock.set_fixed_time(dt.datetime.fromtimestamp(NOW / 1000, tz=dt.timezone.utc))
    page.goto((url or PAGE.resolve().as_uri() + "?replay=fixture") + hash_, wait_until="load", timeout=30000)
    page.wait_for_timeout(1300)
    return ctx, page, errs


def _fit(page, size):
    return page.evaluate("() => ({h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth})")


@pytest.mark.parametrize("size", SIZES, ids=["1920x1040", "400x860"])
def test_map_tab_fits_one_screen_without_scroll(browser, sample, size):
    ctx, page, errs = _open(browser, sample, size)
    try:
        assert not errs, errs
        assert page.evaluate("location.hash") == "#playbook"
        assert page.eval_on_selector("#p-playbook", "e => e.offsetParent !== null")
        assert page.query_selector("#p-playbook .lm"), "Map not drawn"
        f = _fit(page, size)
        assert f["h"] <= size[1], ("scrolls", f, size)
        assert f["w"] <= size[0], ("scrolls sideways", f, size)
        n = page.eval_on_selector("#p-playbook", "e => e.innerText.split(/\\s+/).filter(Boolean).length")
        assert n <= WORD_BUDGET, (n, page.inner_text("#p-playbook"))
        assert page.query_selector(".pbl") is None, "the one-line level wall is back"
    finally:
        ctx.close()


@pytest.mark.parametrize("size", SIZES, ids=["1920x1040", "400x860"])
def test_map_tab_shows_dial_ladder_strip_and_cards(browser, sample, size):
    ctx, page, errs = _open(browser, sample, size)
    try:
        assert not errs, errs
        dial = page.inner_text("#p-playbook .lmw")
        assert dial in ("LONG", "SHORT", "HOLD")
        col = page.eval_on_selector("#p-playbook .lmw", "e => getComputedStyle(e).color")
        assert col != "rgb(0, 0, 0)"
        zones = page.eval_on_selector_all("#p-playbook .lmz", "es => es.length")
        assert 1 <= zones <= 6, zones
        assert page.eval_on_selector("#p-playbook .lmx", "e => e.innerText").strip().startswith("\u25b6")
        assert page.eval_on_selector_all("#p-playbook .lms2", "es => es.length") == 3
        assert page.eval_on_selector_all("#p-playbook .lms2.on", "es => es.length") >= 1       # 10:30Z: Europe is lit
        assert page.eval_on_selector_all("#p-playbook .lmk", "es => es.length") <= 3
        assert page.eval_on_selector_all("#p-playbook .lmn", "es => es.length") <= 1
    finally:
        ctx.close()


def test_a_level_named_by_two_sections_shows_once_with_both_badges(browser, sample):
    pdh = next(l["price"] for l in sample["levels"] if l["k"] == "PDC")   # 124: among the 3 nearest zones above 110
    ad = {"roster": [], "rows": [], "rejected": [], "levels": [{"level": pdh * 1.0005, "analyst": "Big Cheds", "bias": "BEARISH", "published": "2026-11-01", "said": "sell"}]}
    ctx, page, errs = _open(browser, sample, SIZES[0], analysts=ad)
    try:
        assert not errs, errs
        rows = page.eval_on_selector_all("#p-playbook .lmz", "es => es.map(e => [e.querySelector('.lmp').innerText, e.title])")
        hit = [r for r in rows if "PDC" in r[1]]
        assert len(hit) == 1 and "BC" in hit[0][1], rows
        prices = [r[0] for r in rows]
        assert len(prices) == len(set(prices)), prices                          # no price twice on the ladder
    finally:
        ctx.close()


def test_now_table_row_is_the_map_summary(browser, sample):
    ctx, page, errs = _open(browser, sample, SIZES[0], hash_="")
    try:
        assert not errs, errs
        row = page.eval_on_selector("#ov tr[data-go=playbook]", "e => e.innerText")
        assert row.startswith("Map") and re.search(r"LONG|SHORT|HOLD", row), row
    finally:
        ctx.close()


def test_phone_page_fits_400x860_without_scroll(browser, sample, tmp_path):
    js = "// generated by daily_playbook.py\nwindow.PLAYBOOK_DATA = " + json.dumps(sample) + ";\n"
    out = tmp_path / "phone.html"
    out.write_text(build_artifact.build_playbook(js), encoding="utf-8", newline="\n")
    ctx = browser.new_context(offline=True, viewport={"width": 400, "height": 860})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).splitlines()[0][:200]))
    page.clock.set_fixed_time(dt.datetime.fromtimestamp(NOW / 1000, tz=dt.timezone.utc))
    try:
        page.goto(out.as_uri(), wait_until="load", timeout=30000)
        page.wait_for_timeout(500)
        assert not errs, errs
        assert page.query_selector("#pb .lm"), "Map not drawn on the phone page"
        f = _fit(page, (400, 860))
        assert f["h"] <= 860 and f["w"] <= 400, f
        assert len(page.inner_text("main").split()) <= WORD_BUDGET, page.inner_text("main")
    finally:
        ctx.close()


def test_artifact_inlines_the_registry_and_map():
    art = build_artifact.build()
    assert 'src="level_registry' not in art and 'src="map.js' not in art and "root.LEVELREG = api" in art and "root.LAMAP = api" in art
    ph = build_artifact.build_playbook(None)
    assert "root.LEVELREG = api" in ph and "root.LAMAP = api" in ph and "NOT_IN_DATA" in ph


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
