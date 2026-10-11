# Apply AIBridge extension v0.5.0 -> v0.6.0 (text-quiet, watchdog, host= routing).
# Usage: python scripts/dev/aibridge_ext_v06_patch.py [F:/AIBridge]
# Token-free: keeps the machine's own token. Every anchor must match exactly once, else nothing is written.
# Run on a v0.5.0 extension only, then reload it in chrome://extensions and press F5 on the chat tab.
import re
import shutil
import sys

root = (sys.argv[1] if len(sys.argv) > 1 else 'F:/AIBridge').rstrip('/\\')
d = root + '/extension/'


def read(f):
    return open(d + f, encoding='utf-8', newline='').read()


def sub(s, name, a, b):
    if s.count(a) != 1:
        sys.exit('ANCHOR FAIL %s (%d matches): %s' % (name, s.count(a), a[:60]))
    return s.replace(a, b)


files = {f: read(f) for f in ['content.js', 'background.js', 'loop.js', 'manifest.json']}
if '0.5.0' not in files['manifest.json']:
    sys.exit('manifest is not v0.5.0; refusing')

L = files['loop.js']
L = sub(L, 'loop', "    var to = /timeout=(\\d+)/.exec(m[1]);",
        "    var ho = /host=([A-Za-z0-9_.-]+)/.exec(m[1]);\n    if (ho) o.host = ho[1];\n    var to = /timeout=(\\d+)/.exec(m[1]);")

B = files['background.js']
if "TOKEN = '" not in B:
    sys.exit('background.js has no TOKEN line')
B = sub(B, 'bg-cwd-anchor', "const AGENT_CWD =", "const AGENT_CWD =")
m = re.search(r"const TOKEN = '[0-9a-f]+';\n", B)
if not m:
    sys.exit('TOKEN line not found')
helper = (
    "// Other machines: chrome.storage.local aibridge_machines = {\"NUC\": {\"url\": \"http://127.0.0.1:7182/run\", \"token\": \"...\", \"cwd\": \"...\"}}\n"
    "// reached through a loopback tunnel (ssh -L 7182:127.0.0.1:7181 host); the agent itself stays loopback-only.\n"
    "function pickMachine(host) {\n"
    "  return new Promise(res => {\n"
    "    if (!host) { res({ url: AGENT_URL, token: TOKEN, cwd: AGENT_CWD }); return; }\n"
    "    chrome.storage.local.get(['aibridge_machines'], r => {\n"
    "      const m = (r.aibridge_machines || {})[host];\n"
    "      res(m && m.url && m.token ? { url: m.url, token: m.token, cwd: m.cwd || AGENT_CWD } : null);\n"
    "    });\n"
    "  });\n"
    "}\n")
B = B[:m.end()] + helper + B[m.end():]
B = sub(B, 'bg-fetch', "  fetch(AGENT_URL, {\n    method: 'POST',\n    headers: { 'Content-Type': 'text/plain' },\n",
        "  pickMachine(msg.host).then(mc => {\n    if (!mc) return { status: 0, text: JSON.stringify({ error: 'unknown host', reason: 'host=' + msg.host + ' not in aibridge_machines' }) };\n    return fetch(mc.url, {\n      method: 'POST',\n      headers: { 'Content-Type': 'text/plain' },\n")
B = re.sub(r"    body: JSON\.stringify\(\{ cmd: msg\.cmd, cwd: msg\.cwd \|\| AGENT_CWD, (.*?), token: TOKEN \}\)\n  \}\)\n  \.then\(r => r\.text\(\)\.then\(t => \(\{ status: r\.status, text: t \}\)\)\)",
           lambda k: "      body: JSON.stringify({ cmd: msg.cmd, cwd: msg.cwd || mc.cwd, " + k.group(1) + ", token: mc.token })\n    }).then(r => r.text().then(t => ({ status: r.status, text: t })));\n  })", B, count=1)
if 'token: mc.token' not in B:
    sys.exit('ANCHOR FAIL bg-body')

M = files['manifest.json']
M = sub(M, 'manifest-ver', '"version": "0.5.0"', '"version": "0.6.0"')
M = sub(M, 'manifest-host', '"http://127.0.0.1:7181/*"\n  ],\n  "background"',
        '"http://127.0.0.1:7181/*",\n    "http://127.0.0.1:7182/*",\n    "http://127.0.0.1:7183/*"\n  ],\n  "background"')

C = files['content.js']
C = sub(C, 'c-host', "{ type: 'airun', cmd: cmd, cwd: opts.cwd,", "{ type: 'airun', cmd: cmd, host: opts.host, cwd: opts.cwd,")
C = sub(C, 'c-wq', "      if (Date.now() - lastMut >= CFG.aibridge_quiet_ms) return true;", "      if (textQuiet() >= CFG.aibridge_quiet_ms) return true;")
C = sub(C, 'c-idle', "      var idle = Date.now() - lastMut >= CFG.aibridge_quiet_ms;", "      var idle = textQuiet() >= CFG.aibridge_quiet_ms;")
C = sub(C, 'c-pump', "        if (Date.now() - lastMut < CFG.aibridge_quiet_ms) { await sleep(500); continue; }", "        if (textQuiet() < CFG.aibridge_quiet_ms) { await sleep(500); continue; }")
C = sub(C, 'c-final', "    if (!(await waitQuiet(myToken, CFG.aibridge_wait_ms))) return;\n    scan(); await sleep(1500);",
        "    if (myToken !== token) return;\n    await waitQuiet(myToken, CFG.aibridge_wait_ms);   // on timeout still rescan: never leave a finished reply unread\n    if (myToken !== token) return;\n    scan(); await sleep(1500);")
C = sub(C, 'c-sleep', "  function sleep(ms) {",
        "  // text-based quiet: DeepSeek keeps animating, so DOM mutations never settle; visible text length does\n"
        "  var sigLen = -1, sigAt = Date.now();\n"
        "  function oursLen() { var n = 0, l = document.querySelectorAll('.aibridge-wrap, .aibridge-ctl'); for (var i = 0; i < l.length; i++) n += (l[i].textContent || '').length; return n; }\n"
        "  function textQuiet() { return Date.now() - sigAt; }\n"
        "  setInterval(function () { var n = ((document.body && document.body.textContent) || '').length - oursLen(); if (n !== sigLen) { sigLen = n; sigAt = Date.now(); } }, 500);\n"
        "  function sleep(ms) {")
C = sub(C, 'c-watchdog', "  setInterval(pump, 700);",
        "  setInterval(pump, 700);\n"
        "  // watchdog: a reply that finished with a block nobody queued is picked up here (never silently stuck)\n"
        "  setInterval(function () {\n"
        "    if (!alive() || baseline || working || textQuiet() < CFG.aibridge_quiet_ms) return;\n"
        "    var unrun = allBlocks().filter(function (b) { return !ranKeys[blockKey(b)]; });\n"
        "    if (!unrun.length) return;\n"
        "    if (autoRun && pending.length === 0) {\n"
        "      var u = unrun[unrun.length - 1];\n"
        "      pending.push({ block: u, since: Date.now(), len: (u.textContent || '').length, grew: true });\n"
        "      setStatus('watchdog: queued an unrun block from the finished reply');\n"
        "    } else if (!autoRun) {\n"
        "      setStatus('reply complete, ' + unrun.length + ' block(s) waiting: click Run');\n"
        "    }\n"
        "  }, 2000);")
C = sub(C, 'c-ver', "v0.5.0 loaded", "v0.6.0 loaded")

new = {'content.js': C, 'background.js': B, 'loop.js': L, 'manifest.json': M}
for f in new:
    shutil.copy(d + f, d + f + '.pre_v06')
    open(d + f, 'w', encoding='utf-8', newline='\n').write(new[f])
print('patched to v0.6.0:', ', '.join(new), '(backups *.pre_v06)')
