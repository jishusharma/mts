import sys; sys.dont_write_bytecode = True
"""Argon's AIBridge hands-free review (research/argon_audits_2026-11-02/aibridge_hands_free_review.md), High findings re-checked against 0.7.21:
 1) a block that ran half-written and then grew got a new text key and ran a second time;
 2) a failed post left our own text in the chat box (read as busy / an operator draft);
 3) the 0.7.14 self-update (extension reload, stale-page F5) fired during an armed chain and dropped it.
The send-button choice (finding 2, clickSend) is a pure function covered in scripts/aibridge/tests/handsfree.test.js."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aibridge_dom import find_browser, run_page

needs_browser = pytest.mark.skipif(not find_browser(), reason="needs headless Edge/Chrome")
ARM = "setTimeout(function(){ document.querySelector('.aibridge-ctl input').click(); }, 500);\n"


def _runs(r):
    return [c["cmd"] for c in r["calls"] if c["type"] == "airun" and not c.get("dry") and c.get("cmd")]


@needs_browser
def test_1_a_block_element_that_ran_never_runs_again_after_it_grows():
    js = ARM + r"""
setTimeout(function(){
  var d = window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output part']);
  var code = d.querySelector('code');
  setTimeout(function(){ code.textContent = '# AIRUN cwd=C:\\x\nWrite-Output part-and-the-rest'; }, 9000);   // the stream resumes long after the run
}, 8000);
setTimeout(window.finish, 90000);
"""
    r = run_page(js, 100000)
    assert len(_runs(r)) == 1, _runs(r)


@needs_browser
def test_2_a_failed_post_puts_the_operator_draft_back_not_our_text():
    js = ARM + r"""
var ta = document.getElementById('chat-input');
ta.addEventListener('keydown', function (e) { e.stopImmediatePropagation(); }, true);   // Enter does nothing: the post can never land
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output post1']); }, 8000);
setTimeout(function(){ window.extra = { box: ta.value }; window.finish(); }, 60000);
"""
    r = run_page(js, 70000)
    assert (r["extra"]["box"] or "") == "", r["extra"]


@needs_browser
def test_3_no_self_update_while_hands_free_is_armed():
    js = ARM + r"""
window.loadedVersion = '9.9.9'; window.diskVersion = '9.9.9.9';   // extension AND page look stale
setTimeout(window.finish, 90000);
"""
    r = run_page(js, 100000)
    assert not any(c["type"] == "reload" for c in r["calls"]), [c["type"] for c in r["calls"]]
    assert r["dbg"] is not None   # the page was never reloaded away (finish() ran)
