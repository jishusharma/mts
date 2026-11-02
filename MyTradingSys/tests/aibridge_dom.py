import sys; sys.dont_write_bytecode = True
"""aibridge_dom.py - run the real extension content script (loop.js + content.js) in headless Edge/Chrome against a fake chat page.

Test helper for research/dsa_bridge_exploratory_2026-10-31. No agent, no network: chrome.runtime.sendMessage is a scripted stub, so each
test says exactly what the 'agent' answers. The page reports through <pre id=result> (JSON), read back with --dump-dom.
Virtual time (--virtual-time-budget) lets a 5-minute lock expiry run in seconds.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
EXT = ROOT / "scripts" / "aibridge" / "extension"


_PROBE_MARK = "aib-probe-ok"
_PROBE_CACHE = {}


def _probe(path):
    """True only if headless --dump-dom of a trivial data: page prints the marker (headless Edge on some hosts dumps nothing)."""
    if path in _PROBE_CACHE:
        return _PROBE_CACHE[path]
    prof = tempfile.mkdtemp(prefix="aib_probe_")
    ok = False
    try:
        p = subprocess.run([path, "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + prof,
                            "--dump-dom", "data:text/html," + _PROBE_MARK],
                           capture_output=True, text=True, timeout=15)
        ok = _PROBE_MARK in (p.stdout or "")
    except Exception:
        ok = False
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    _PROBE_CACHE[path] = ok
    return ok


def find_browser(candidates=None):
    """First existing candidate that passes _probe; AIB_BROWSER (explicit) is trusted unprobed. Cached per process."""
    if candidates is None:
        env = os.environ.get("AIB_BROWSER")
        if env and os.path.exists(env):
            return env
        candidates = (shutil.which("msedge"), shutil.which("chrome"),
                      r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                      r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                      r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    for c in candidates:
        if c and os.path.exists(c) and _probe(c):
            return c
    return None


PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>fake chat</title></head><body>
<div id="log"></div><div class="dock"><textarea id="chat-input" style="width:400px;height:40px"></textarea></div>
<pre id="result"></pre>
<script>
window.calls = []; window.posted = []; window.statusLog = [];
window.chrome = {
  runtime: {
    lastError: null, id: "stubid",
    connect: function () { return { onMessage: { addListener: function () {} }, onDisconnect: { addListener: function () {} }, disconnect: function () {} }; },
    getPlatformInfo: function () {},
    sendMessage: function (msg, cb) {
      window.calls.push({ t: Date.now() - window.T0, type: msg.type, cmd: msg.cmd, task: msg.task, timeout_s: msg.timeout_s, rid: msg.rid, dry: msg.dry, event: msg.event });
      if (msg.event) { cb({ ok: true, status: 200, body: { ok: true, event: true } }); return; }
      if (msg.type === 'version') { cb({ loaded: window.loadedVersion || window.AV(), disk: window.diskVersion || window.AV() }); return; }
      if (msg.type === 'reload') { window.reloaded = (window.reloaded || 0) + 1; cb({ ok: true }); return; }
      if (msg.type === 'ping') { cb({ ok: true, status: 200, body: { ok: true, agent: window.agentVersion || window.AV(), host: 'H', shell_version: '5.1', pwsh: true, running: window.agentRunning == null ? 0 : window.agentRunning } }); return; }
      if (msg.dry) { cb({ ok: true, status: 200, body: { dry: true, ok: true, reason: 'auto_fluent', kind: 'read' } }); return; }
      var r = window.agent(msg);   // {delay_ms, body} or {never:true}
      if (r.never) return;
      setTimeout(function () {
        var b = Object.assign({ exit: 0, out: '', err: '', ms: 1, timed_out: false, out_truncated: false, out_bytes: 0, timeout_s: msg.timeout_s || 60,
          host: 'H', agent: window.agentVersion || window.AV(), kind: 'read', rid: msg.rid, cmd_lines: String(msg.cmd || '').split('\n').length, cmd_sha: 'abc', at: 'T' }, r.body || {});
        cb({ ok: true, status: 200, body: b });
      }, r.delay_ms || 0);
    }
  },
  storage: { local: { get: function (k, cb) { cb({}); }, set: function () {} }, onChanged: { addListener: function () {} } }
};
window.AV = function () { return (window.AIBridgeLoop && window.AIBridgeLoop.VERSION) || '0.0.0'; };
window.T0 = Date.now();
window.agent = function (msg) { return { body: { out: 'ran:' + String(msg.cmd).split('\n')[0] } }; };
var ta = document.getElementById('chat-input');
ta.addEventListener('keydown', function (e) {
  if (e.key !== 'Enter') return;
  var v = ta.value; ta.value = '';
  window.posted.push({ t: Date.now() - window.T0, text: v });
  var d = document.createElement('div'); d.className = 'user'; d.textContent = v; document.getElementById('log').appendChild(d);
});
// helpers for scenarios
window.codeBlock = function (parent, text) {
  var w = document.createElement('div'); w.className = 'md-code-block';
  var h = document.createElement('div'); h.className = 'hdr'; h.textContent = 'powershell'; w.appendChild(h);
  var pre = document.createElement('pre'); var c = document.createElement('code'); c.textContent = text; pre.appendChild(c); w.appendChild(pre);
  parent.appendChild(w); return w;
};
window.dsaReply = function (prose, blocks, wrapperHtml) {
  var d = document.createElement('div'); d.className = 'dsa';
  if (prose) { var p = document.createElement('p'); p.textContent = prose; d.appendChild(p); }
  (blocks || []).forEach(function (b, i) { var p = document.createElement('p'); p.textContent = 'next step ' + (i + 1); d.appendChild(p); window.codeBlock(d, b); });
  document.getElementById('log').appendChild(d); return d;
};
window.finish = function () {
  var dbg = {}; try { dbg = window.__aibDebug(); } catch (e) {}
  var st = document.querySelector('.aibridge-ctl .st');
  document.getElementById('result').textContent = JSON.stringify({ calls: window.calls, posted: window.posted, status: st ? st.textContent : null, dbg: dbg,
    banner: (document.getElementById('aibridge-stop-banner') || {}).textContent || null, extra: window.extra || null });
};
</script>
<script src="loop.js"></script><script src="content.js"></script>
<script>
SCENARIO
</script></body></html>
"""


def run_page(scenario_js, budget_ms=60000, timeout=120):
    """scenario_js runs after the content script loaded; it must call window.finish() (in a setTimeout) when done."""
    br = find_browser()
    if not br:
        raise RuntimeError("no Edge/Chrome")
    try:   # DECISION (OURS): a loaded gate machine scales every headless-Chrome cap; bad value -> 1.0
        scale = float(os.environ.get("MTS_BROWSER_TIMEOUT_SCALE", "1.0"))
        if not scale > 0:
            scale = 1.0
    except ValueError:
        scale = 1.0
    timeout = int(timeout * scale)
    d = tempfile.mkdtemp(prefix="aib_dom_")
    prof = tempfile.mkdtemp(prefix="aib_prof_")
    try:
        for f in ("loop.js", "content.js"):
            shutil.copy(EXT / f, d)
        html = os.path.join(d, "page.html")
        open(html, "w", encoding="utf-8").write(PAGE.replace("SCENARIO", scenario_js))
        p = subprocess.run([br, "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + prof,
                            "--allow-file-access-from-files", "--enable-logging=stderr", "--v=0", "--virtual-time-budget=%d" % budget_ms, "--dump-dom", Path(html).as_uri()],
                           capture_output=True, timeout=timeout)
        dom = p.stdout.decode("utf-8", "replace")
        m = re.search(r'<pre id="result">(.*?)</pre>', dom, re.S)
        if not m or not m.group(1).strip():
            err = [l for l in p.stderr.decode("utf-8", "replace").splitlines() if "CONSOLE" in l]
            raise RuntimeError("no result in DOM; console=" + " | ".join(err)[-800:])
        import html as H
        res = json.loads(H.unescape(m.group(1)))
        res["console"] = [l.split("CONSOLE:")[1][:200] for l in p.stderr.decode("utf-8", "replace").splitlines() if "CONSOLE" in l]
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(prof, ignore_errors=True)
