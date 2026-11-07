import sys; sys.dont_write_bytecode = True
"""AIBridge long unattended chain (operator 2026-11-02): the real extension content script in headless Edge/Chrome against a fake chat,
tab simulated hidden, a scripted DSA that answers each result with the next 6 blocks. 54 blocks in 9+ replies, with a deliberate
non-zero exit (b17), a timeout (b33) and one dropped generation (no answer after the 5th reply's result until the extension's notice).
Pass = every block ran exactly once, hands-free stayed ON, no stop banner. Fake chat page: the bar for the real chat.deepseek.com
page is the NUC run (see research/aibridge_rootcause_2026-11)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aibridge_dom import find_browser, run_page

needs_browser = pytest.mark.skipif(not find_browser(), reason="needs headless Edge/Chrome")

N_BLOCKS = 54
JS = r"""
Object.defineProperty(document, 'hidden', {get: function(){ return true; }});
Object.defineProperty(document, 'visibilityState', {get: function(){ return 'hidden'; }});
window.agent = function (msg) {
  var m = /b(\d+)$/.exec(String(msg.cmd)); var i = m ? +m[1] : -1;
  if (i === 17) return { body: { exit: 1, out: 'boom' } };
  if (i === 33) return { body: { exit: -1, timed_out: true, out: '' } };
  return { body: { out: 'ran b' + i } };
};
setTimeout(function(){ document.querySelector('.aibridge-ctl input').click(); }, 500);
var N = %d, seen = 0, replies = 0, dropped = false;
function nextBlocks() {
  var done = {}; window.calls.forEach(function (c) { if (c.type === 'airun' && !c.dry) done[c.cmd] = 1; });
  var todo = [];
  for (var i = 0; i < N && todo.length < 6; i++) { if (!done['Write-Output b' + i]) todo.push('# AIRUN cwd=C:\\x\nWrite-Output b' + i); }
  return todo;
}
setTimeout(function () { replies = 1; window.dsaReply('go', nextBlocks()); }, 8000);
setInterval(function () {
  if (window.posted.length === seen) return;
  var last = window.posted[window.posted.length - 1].text; seen = window.posted.length;
  var isNotice = last.indexOf('[AIRUN NOTICE]') >= 0;
  if (replies === 5 && !dropped && !isNotice) { dropped = true; window.droppedAt = Date.now() - window.T0; return; }
  var todo = nextBlocks();
  if (!todo.length) { window.dsaReply('All done.', []); window.allDone = true; return; }
  replies++; window.dsaReply('go', todo);
}, 1000);
setTimeout(function () { window.extra = { allDone: !!window.allDone, replies: replies, dropped: dropped }; window.finish(); }, 900000);
""" % N_BLOCKS


@needs_browser
def test_long_unattended_chain_hidden_tab_with_failure_timeout_and_dropped_reply():
    r = run_page(JS, 950000, timeout=480)   # OURS: 3.5x the 137 s quiet run
    runs = [c["cmd"] for c in r["calls"] if c["type"] == "airun" and not c.get("dry") and c.get("cmd")]   # an airun without cmd is an audit event (0.7.27 no-marker line)
    counts = {}
    for c in runs:
        counts[c] = counts.get(c, 0) + 1
    dups = {k: v for k, v in counts.items() if v > 1}
    missing = ["Write-Output b%d" % i for i in range(N_BLOCKS) if "Write-Output b%d" % i not in counts]
    summary = {"ran": len(runs), "distinct": len(counts), "dups": dups, "missing": missing, "extra": r["extra"],
               "banner": r["banner"], "status": r["status"]}
    print("CHAIN", summary)
    assert not dups and not missing, summary
    assert r["extra"]["dropped"] and r["extra"]["allDone"], summary
    assert not r["banner"], summary


@needs_browser
def test_short_final_answer_is_an_answer_not_a_dropped_generation():
    """Root cause 8: ANSWER_MIN_CHARS was 10, so a final answer of 'ok' or 'Done.' (the notice itself tells DSA to 'reply ok')
    counted as no answer: a notice, then the stop banner, ending the chain with hands-free OFF."""
    js = r"""
setTimeout(function(){ document.querySelector('.aibridge-ctl input').click(); }, 500);
setTimeout(function(){ window.dsaReply('go', ['# AIRUN cwd=C:\\x\nWrite-Output b0']); }, 8000);
var seen = 0;
setInterval(function () { if (window.posted.length !== seen) { seen = window.posted.length; setTimeout(function(){ window.dsaReply('Done.', []); }, 4000); } }, 1000);   // DSA takes seconds to answer, as the real one does
setTimeout(window.finish, 150000);
"""
    r = run_page(js, 160000)
    assert not r["banner"], (r["banner"], [p["text"][:40] for p in r["posted"]])
    assert not any("[AIRUN NOTICE]" in p["text"] for p in r["posted"])
