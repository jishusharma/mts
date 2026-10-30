"""Every artifact page we keep opens: registry html copies, the live aid and the sim desk page are loaded from disk in a
headless Chromium with the network OFF. A page fails on an uncaught script error, on NaN / [object Object] / a bare
"undefined" cell in its visible text, or (live aid) when its feeds do not fall back to NOT_IN_DATA.

Layer 3 (open it) of MyTradingSys/system/ARTIFACT_TESTING.md. Needs the playwright package and a Chromium (the desktop
ship gate has both); elsewhere the file skips and says so, it never fails for a missing browser.
Fail-first: test_planted_defects_are_caught runs the checker on a page with a thrown error and a NaN cell.
"""
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REG = REPO / "MyTradingSys" / "system" / "artifacts" / "registry.json"
EXTRA_PAGES = ["MyTradingSys/tools/live_aid/live_aid.html", "MyTradingSys/research/sim_desk/artifact/index.html"]
SETTLE_MS = 1500          # OURS: the pages' own init (feed timers, DATA render) is done well inside this
BAD_TEXT = re.compile(r"\bNaN\b|\[object Object\]")
BARE_UNDEFINED = re.compile(r"^\s*undefined\s*$|^[^A-Za-z]*undefined[^A-Za-z]*$")   # a cell, not prose ("x was undefined:")
NET_NOISE = ("Failed to load resource", "net::ERR")   # expected with the network off


def pages():
    reg = json.loads(REG.read_text(encoding="utf-8"))
    out = [p["html"] for p in reg["pages"] if p.get("html")]
    return out + [p for p in EXTRA_PAGES if (REPO / p).exists()]


def text_problems(text):
    """Visible-text defects: NaN, [object Object], a line that is only 'undefined' (a cell rendered from a missing field)."""
    found = sorted({m.group(0) for m in BAD_TEXT.finditer(text)})
    found += [f"bare undefined: {ln.strip()[:60]!r}" for ln in text.splitlines() if BARE_UNDEFINED.match(ln) and len(ln) < 40]
    return found


def check_page(ctx, path, settle_ms=SETTLE_MS):
    """Open one file:// page offline; return its problems (empty = clean) and its visible text."""
    page = ctx.new_page()
    errs, cons = [], []
    page.on("pageerror", lambda e: errs.append("script error: " + str(e).splitlines()[0][:200]))
    page.on("console", lambda m: cons.append(m.text) if m.type == "error" and not any(n in m.text for n in NET_NOISE) else None)
    try:
        page.goto(Path(path).resolve().as_uri(), wait_until="load", timeout=30000)
        page.wait_for_timeout(settle_ms)
        text = page.inner_text("body")
    finally:
        page.close()
    problems = errs + ["console error: " + c[:200] for c in cons[:5]] + text_problems(text)
    if len(text.strip()) < 200:
        problems.append(f"page nearly empty: {len(text.strip())} chars of visible text")
    return problems, text


@pytest.fixture(scope="module")
def ctx():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright package not installed: pip install playwright")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as ex:  # no browser on this machine (CI runner): say so, never fail
            pytest.skip("no Chromium for playwright: " + str(ex).splitlines()[0][:120])
        c = browser.new_context(offline=True, viewport={"width": 1400, "height": 900})
        try:
            yield c
        finally:
            browser.close()


@pytest.mark.parametrize("rel", pages())
def test_page_opens_clean_offline(ctx, rel):
    problems, _ = check_page(ctx, REPO / rel)
    assert not problems, f"{rel}: " + "; ".join(problems)


def test_live_aid_fails_closed_without_feeds(ctx):
    """Network off: every feed must read NOT_IN_DATA (STEPS.md: failed feed = NOT_IN_DATA + error), never a stale or made-up number."""
    rel = "MyTradingSys/tools/live_aid/live_aid.html"
    if not (REPO / rel).exists():
        pytest.skip(rel + " not in this tree")
    problems, text = check_page(ctx, REPO / rel)
    assert not problems, "; ".join(problems)
    assert "NOT_IN_DATA" in text, "live aid offline shows no NOT_IN_DATA: feeds are not failing closed"


def test_planted_defects_are_caught(ctx, tmp_path):
    """Fail-first: the checker itself must see a thrown error, a NaN cell and a bare undefined cell."""
    bad = tmp_path / "bad.html"
    bad.write_text("<title>t</title><main><p>" + "filler text " * 30 + "</p><table><tr><td>NaN</td></tr>"
                   "<tr><td>undefined</td></tr></table><script>throw new Error('planted');</script></main>",
                   encoding="utf-8", newline="\n")
    problems, _ = check_page(ctx, bad, settle_ms=100)
    joined = "; ".join(problems)
    assert "planted" in joined and "NaN" in joined and "bare undefined" in joined, joined
    assert text_problems("the field was undefined: now set") == []   # prose is not a defect


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q", *sys.argv[1:]]))
