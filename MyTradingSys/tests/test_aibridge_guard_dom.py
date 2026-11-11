import sys; sys.dont_write_bytecode = True
"""test_aibridge_guard_dom.py - the DeepSeek block guard on the real content script in headless Edge/Chrome (fake chat page, stubbed agent).

Card dsa-bridge-avoid-deepseek-block-1108 (DSA_BLOCK_REVIEW.md ranks 2-4): hands-free refuses to arm on a refused account lease, a
second armed tab, a cooldown or a warning page; a warning that appears while armed turns it off, writes an audit row and a 24 h
cooldown. The pure rules are in handsfree.test.js; these tests prove content.js wires them. All fail on 0.7.32 (no guard: it arms).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aibridge_dom import find_browser, run_page

needs_browser = pytest.mark.skipif(not find_browser(), reason="needs headless Edge/Chrome")
ARM = "setTimeout(function(){ document.querySelector('.aibridge-ctl input').click(); }, 500);\n"
END = "setTimeout(function () { window.finish(); }, 4000);\n"


def run(js):
    return run_page(js + ARM + END, 20000, timeout=120)


def events(r):
    return [c["event"] for c in r["calls"] if c.get("event")]


@needs_browser
def test_arming_works_when_the_lease_is_granted():
    r = run("")
    assert r["dbg"]["autoRun"] is True, r
    assert any(e.startswith("LEASE ") for e in events(r)), events(r)


@needs_browser
def test_refused_lease_keeps_hands_free_off():
    r = run("window.leaseReply = { lease: 'account_in_use', holder: 'JIS-NUC' };\n")
    assert r["dbg"]["autoRun"] is False, r
    assert "account_in_use" in (r["status"] or "") and "JIS-NUC" in (r["status"] or ""), r["status"]
    assert any("arm refused (account_in_use)" in e for e in events(r)), events(r)


@needs_browser
def test_unconfirmed_lease_from_an_old_agent_keeps_it_off():
    r = run("window.leaseReply = { lease: undefined };\n")
    assert r["dbg"]["autoRun"] is False, r
    assert "lease_unconfirmed" in (r["status"] or ""), r["status"]


@needs_browser
def test_second_armed_tab_is_refused():
    r = run("window.storeLive = true; window.store = { aibridge_armed: { othertab: Date.now() } };\n")
    assert r["dbg"]["autoRun"] is False, r
    assert "second_tab_refused" in (r["status"] or ""), r["status"]


@needs_browser
def test_cooldown_blocks_arming():
    r = run("window.store = { aibridge_cooldown_v2: Date.now() + 3600000 };\n")
    assert r["dbg"]["autoRun"] is False, r
    assert "cooldown" in (r["status"] or ""), r["status"]


@needs_browser
def test_warning_page_blocks_arming_and_starts_the_cooldown():
    r = run("var d = document.createElement('div'); d.setAttribute('role', 'dialog'); d.textContent = 'Due to violation of user policies, your account has been suspended until 2026-11-11 10:22'; document.body.appendChild(d);\n")
    assert r["dbg"]["autoRun"] is False, r
    assert "aibridge_cooldown_v2" in (r["saved"] or {}), r["saved"]


@needs_browser
def test_captcha_while_armed_holds_without_cooldown():
    # 0.7.35: a captcha (Cloudflare Turnstile usually clears by itself) holds posts; it does not stop hands-free or set the 24 h cooldown
    js = ("setTimeout(function () { var d = document.createElement('div'); d.setAttribute('role', 'alert'); "
          "d.textContent = 'Verify you are human to continue'; document.body.appendChild(d); }, 2000);\n")
    r = run(js)
    assert r["dbg"]["autoRun"] is True, r
    assert any(e.startswith("HOLD captcha") for e in events(r)), events(r)
    assert "aibridge_cooldown_v2" not in (r["saved"] or {}), r["saved"]
    assert not any(e.startswith("WARNING") for e in events(r)), events(r)


@needs_browser
def test_chat_text_about_a_captcha_is_not_a_warning():
    r = run("window.dsaReply('The captcha page says: server is busy, account suspended (a quote).', []);\n")
    assert r["dbg"]["autoRun"] is True, r
