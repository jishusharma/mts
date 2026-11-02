import sys; sys.dont_write_bytecode = True
"""AIBridge 0.7.18 (operator 2026-11-02, real-page chain on NUC): hands-free went OFF with 'the result was not posted (the chat never
became idle)', and DeepSeek got 'block has no command' receipts for blocks that did have one. Reproduced on the fake chat page:
 a) a block whose body renders after the marker was reported as 'no command' and marked done;
 b) a stream pause longer than the quiet window ran a half-written command;
 c) a busy chat made the result post time out and end hands-free; the result is now queued and retried;
 d) stop reasons reach the agent's audit log (an `event` request), the banner alone is invisible there."""
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
def test_a_block_whose_body_renders_late_is_not_reported_empty():
    js = ARM + r"""
setTimeout(function(){
  var d = window.dsaReply('go', ['# AIRUN cwd=C:\\x']);
  var code = d.querySelector('code');
  setTimeout(function(){ code.textContent = '# AIRUN cwd=C:\\x\nWrite-Output late-body'; }, 5000);
}, 8000);
setTimeout(window.finish, 60000);
"""
    r = run_page(js, 70000)
    assert "Write-Output late-body" in _runs(r), (_runs(r), [p["text"][:80] for p in r["posted"]])
    assert not any("no command after" in p["text"] for p in r["posted"]), [p["text"][:120] for p in r["posted"]]


@needs_browser
def test_b_half_written_command_is_never_run():
    js = ARM + r"""
setTimeout(function(){
  var d = window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output par']);
  var code = d.querySelector('code');
  setTimeout(function(){ code.textContent = '# AIRUN cwd=C:\\x\nWrite-Output par-complete'; }, 3000);
}, 8000);
setTimeout(window.finish, 60000);
"""
    r = run_page(js, 70000)
    assert _runs(r) == ["Write-Output par-complete"], _runs(r)


@needs_browser
def test_c_result_is_queued_and_retried_while_the_chat_is_busy_and_stop_reasons_are_audited():
    js = ARM + r"""
var busyUntil = 0;
window.agent = function (msg) {
  busyUntil = Date.now() + 200000;                       // DeepSeek starts a long generation right after the block ran
  var d = document.createElement('div'); d.id = 'busy'; document.body.appendChild(d);
  var k = 0; var iv = setInterval(function () { if (Date.now() > busyUntil) { clearInterval(iv); return; } d.textContent += 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'; }, 400);
  return { delay_ms: 3000, body: { out: 'ran' } };
};
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output busy1']); }, 8000);
setTimeout(window.finish, 480000);
"""
    r = run_page(js, 500000, timeout=240)
    assert any("[AIRUN RESULT #1]" in p["text"] for p in r["posted"]), (r["banner"], r["status"], [p["text"][:60] for p in r["posted"]])
    events = [c for c in r["calls"] if c.get("event")]
    assert any("not posted" in c["event"] for c in events), events


@needs_browser
def test_d_auto_off_reason_reaches_the_audit_log():
    js = ARM + r"""
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output a1']); }, 8000);
setTimeout(window.finish, 150000);
"""
    r = run_page(js, 160000)
    assert r["banner"], "scenario must end in the dropped-generation stop"
    events = [c for c in r["calls"] if c.get("event")]
    assert any("auto OFF" in c["event"] and "never answered" in c["event"] for c in events), events
