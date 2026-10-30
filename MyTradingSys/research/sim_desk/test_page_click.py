"""Layer 3 (open it) for the sim desk local app: page.html in headless Chromium against a real desk.py server.

Reuses the server fixture and Fake study of test_integration_http.py (40 trades). Expected numbers are worked by hand from the
Fake definition, never read from the page:
  net = where(i % 2, +1.0, -0.5) * x, fees 0  ->  20 trades at +1.0x, 20 at -0.5x
  mean = (20*1.0 - 20*0.5) / 40 = 0.25 R at x=1 (page default), 0.50 R at x=2.
The page prints the mean through fmt(): sign plus 3 decimals, so '+0.250 R' and '+0.500 R'.
Skips with a reason (never fails) if playwright or Chromium is missing, like scripts/dev/test_artifact_pages.py.
Fail-first: set MTS_CLICK_FAILFIRST=1 to inject a +1 trade-count bump through add_init_script; test_numbers_check_catches_a_bump
runs that same bump inside the suite and demands the numbers check fails.
"""
import os
import re

import pytest

from test_integration_http import Fake, server  # noqa: F401  (server is a pytest fixture)

N_TRADES = 40                                    # Fake.run: n = 40
MEAN_X1 = (20 * 1.0 + 20 * -0.5) / 40            # 0.25
MEAN_X2 = 2 * MEAN_X1                            # 0.5

BUMP = """
(() => { const f = window.fetch;
  window.fetch = async (u, o) => { const r = await f(u, o);
    if (String(u).includes('/api/run')) { const j = await r.clone().json(); j.n = j.n + 1;
      return new Response(JSON.stringify(j), {status: r.status, headers: {'Content-Type': 'application/json'}}); }
    return r; }; })();
"""


@pytest.fixture(scope="module")
def browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright package not installed: pip install playwright")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception as ex:
            pytest.skip("no Chromium for playwright: " + str(ex).splitlines()[0][:120])
        try:
            yield b
        finally:
            b.close()


def open_page(browser, url, bump=False):
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.errors = []
    page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    if bump or os.environ.get("MTS_CLICK_FAILFIRST") == "1":
        page.add_init_script(BUMP)
    page.goto(url)
    page.click(f'#chips .chip[data-study="{Fake.ID}"]')
    page.wait_for_selector("#run")
    return page


def run_and_wait(page, x=None):
    if x is not None:
        page.fill('#form [name=x]', str(x))
    page.click("#run")
    page.wait_for_function("() => !document.getElementById('say').textContent.startsWith('Running')", timeout=60000)
    assert "err" not in (page.get_attribute("#say", "class") or ""), page.inner_text("#say")


def numbers(page):
    boxes = page.locator("#nums .num b").all_inner_texts()
    return int(boxes[0]), boxes[1]


def check_numbers(page, mean_text, n=N_TRADES):
    got_n, got_mean = numbers(page)
    assert got_n == n, f"rendered trade count {got_n}, hand-worked {n}"
    assert got_mean == mean_text, f"rendered mean {got_mean!r}, hand-worked {mean_text!r}"


def test_run_renders_counts_and_mean(browser, server):
    url, _, _ = server
    page = open_page(browser, url)
    run_and_wait(page)
    assert page.inner_text("#verdict").split()[0] in ("PASSED", "FAILED", "NOT")
    check_numbers(page, f"+{MEAN_X1:.3f} R")
    assert page.locator("#tltab tr.t").count() == N_TRADES
    assert not page.errors, page.errors


def test_trade_row_draws_chart(browser, server):
    url, _, _ = server
    page = open_page(browser, url)
    run_and_wait(page)
    page.click("#tltab tr.t >> nth=0")
    page.wait_for_selector("#tchart svg", timeout=30000)
    txt = page.inner_text("#tchart")
    assert not re.search(r"error|Loading chart|No chart", txt, re.I), txt
    assert not page.errors, page.errors


def test_second_run_doubles_mean(browser, server):
    url, _, _ = server
    page = open_page(browser, url)
    run_and_wait(page)
    check_numbers(page, f"+{MEAN_X1:.3f} R")
    run_and_wait(page, x=2)
    check_numbers(page, f"+{MEAN_X2:.3f} R")
    assert not page.errors, page.errors


def test_numbers_check_catches_a_bump(browser, server):
    """Fail-first proof kept in the suite: a +1 on the rendered count must trip the same check the real test uses."""
    url, _, _ = server
    page = open_page(browser, url, bump=True)
    run_and_wait(page)
    with pytest.raises(AssertionError, match="rendered trade count 41"):
        check_numbers(page, f"+{MEAN_X1:.3f} R")
