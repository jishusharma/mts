(function () {
  if (window.__aibridgeInstalled) return;
  window.__aibridgeInstalled = true;
  var L = window.AIBridgeLoop;
  var VER = L.VERSION;

  // ---- tunables (override via chrome.storage.local keys of the same name) ----
  var CFG = {
    aibridge_quiet_ms: 2000,    // page text must be unchanged this long = reply finished
    aibridge_max_chars: 60000,  // largest single message we send; see HANDOFF.md for the measured limit
    aibridge_cap: 200,          // blocks run in one chain before auto turns itself off
    aibridge_wait_ms: 180000,   // give up waiting for an idle chat after this long
    aibridge_max_blocks: 6      // blocks run, in order, from ONE reply (the rest get an explicit NOT RUN receipt)
  };
  var autoRun = false;
  var stopHold = false;          // a stop reason stays on the status line until the operator re-arms (watchdog must not overwrite it)
  var lastPostErr = '';          // why the last post failed, for the stop reason
  var runs = 0;
  var resultN = 0;
  var token = 0;                 // bumped by Stop to abort in-flight work
  var tabId = Math.random().toString(36).slice(2, 8);   // this chat page; parallel chats never share state
  var lastMut = Date.now();
  var baseline = true;           // true during the first scan: existing blocks are history, never auto-run
  var ranKeys = {};              // fnv(cmd)@occurrence of blocks already run or skipped
  var pending = [];              // {block, since}
  var seen = new WeakSet();
  var working = false;
  var ui = {};
  var histUntil = Date.now() + 6000;   // blocks first seen before this (page load / chat switch) are history
  var lastHref = location.href;
  var lastSend = 0;              // last time a message was sent from this page (operator Enter or our own post)
  var labelBusy = false;
  var lastIgnored = 0;           // thinking-panel blocks skipped on the last scan
  var watch = null;              // replyWatch state: a posted result waits for DSA's final answer
  var postedAnsLen = 0;          // non-thinking page text length when the result was posted
  var quietSince = 0;            // pump: since when it waits for the page text to settle

  // after the extension is reloaded this old copy is orphaned: stop it quietly and say so
  function alive() { try { return !!(chrome.runtime && chrome.runtime.id); } catch (e) { return false; } }
  var orphanShown = false;
  function orphan() {
    if (!orphanShown && ui.status) { orphanShown = true; autoRun = false; ui.status.textContent = 'extension was reloaded: refresh this page (F5)'; if (ui.cb) { ui.cb.checked = false; ui.cb.disabled = true; } }
  }

  // ---- heartbeat that survives a background / unfocused window ----
  // Page timers are throttled when the tab is hidden (1/s, then 1/min after 5 min), so a chat in a second window used to
  // stall. The service worker pushes a tick every 500 ms over a port; messages are not throttled. sleep() resolves on a
  // tick as well as on its own timer, so every await in the loop keeps its pace in the background.
  var sleepers = [];
  function sleep(ms) {
    return new Promise(function (resolve) {
      var done = false;
      function fin() { if (!done) { done = true; resolve(); } }
      sleepers.push({ due: Date.now() + ms, fin: fin });
      setTimeout(fin, ms);
    });
  }
  var tickPort = null, lastTick = 0, lastWorkerTick = 0, reconAttempt = 0, reconTimer = null;
  // connect now (no timer in the way: a hidden page's timers are throttled); a failed attempt backs off 1 s .. 15 s
  function connectTick() {
    reconTimer = null;
    if (!alive()) return;
    try {
      if (tickPort) { try { tickPort.disconnect(); } catch (e0) {} tickPort = null; }
      var p = chrome.runtime.connect({ name: 'aibridge-tick' });
      tickPort = p;
      p.onMessage.addListener(function () { reconAttempt = 0; onTick(true); });
      p.onDisconnect.addListener(function () { if (tickPort === p) { tickPort = null; scheduleReconnect(); } });
    } catch (e) { scheduleReconnect(); }
  }
  function scheduleReconnect() {
    if (reconTimer) return;
    reconAttempt++;
    var d = L.reconnectDelay(reconAttempt - 1);
    if (d === 0) connectTick(); else reconTimer = setTimeout(connectTick, d);
  }
  // second heartbeat: a dedicated Worker keeps its own 500 ms timer while the tab is in the background and works even
  // when the service worker is asleep. A page CSP may refuse a blob worker; then the port tick is the only source.
  function startWorkerTick() {
    try {
      var url = URL.createObjectURL(new Blob(['setInterval(function(){postMessage(1)},500)'], { type: 'text/javascript' }));
      var w = new Worker(url);
      w.onmessage = function () { lastWorkerTick = Date.now(); onTick(false); };
      w.onerror = function () { try { w.terminate(); } catch (e) {} };
    } catch (e) {}
  }
  // self-heal + visible status: runs on every tick from either source
  var lastLinkLabel = '', lastLinkCheck = 0, lastRecon = 0;
  function linkCheck() {
    var now = Date.now();
    if (now - lastLinkCheck < 1000) return;
    lastLinkCheck = now;
    var ls = L.linkState(now, { port: lastTick, worker: lastWorkerTick });
    if (ls.reconnect && now - lastRecon > Math.max(2000, L.reconnectDelay(reconAttempt))) { lastRecon = now; reconAttempt = Math.max(reconAttempt, 1); connectTick(); }
    if (ui.box) {
      var lab = L.linkLabel(ls, document.hidden);
      if (lab !== lastLinkLabel) { lastLinkLabel = lab; ui.box.dataset.link = ls.state; ui.box.title = lab; if (ui.link) { ui.link.textContent = ls.state === 'ok' ? '\u25CF' : (ls.state === 'degraded' ? '\u25D0' : '\u25CB'); ui.link.title = lab; } }
    }
  }
  function onTick(fromPort) {
    var now = Date.now();
    if (fromPort) lastTick = now;
    linkCheck();
    if (sleepers.length) {
      var keep = [];
      for (var i = 0; i < sleepers.length; i++) { if (sleepers[i].due <= now) sleepers[i].fin(); else keep.push(sleepers[i]); }
      sleepers = keep;
    }
    sampleText(); growCheck(); pump(); watchdog(); labelTick(); replyTick(); versionTick(); guardTick();
  }
  // a page holding a Web Lock is not frozen by Chrome's tab lifecycle while it sits in the background
  try { if (navigator.locks && navigator.locks.request) navigator.locks.request('aibridge-keepalive-' + tabId, function () { return new Promise(function () {}); }); } catch (e) {}

  // text-based quiet: DeepSeek keeps animating, so DOM mutations never settle; visible text length does
  var sig = { len: -1, at: Date.now() };
  var sigX = { len: -1, at: Date.now() };   // exact (tolerance 0) clock: 'is DSA's answer text still changing', used only by replyTick
  function oursLen() { var n = 0, l = document.querySelectorAll('.aibridge-wrap, .aibridge-ctl'); for (var i = 0; i < l.length; i++) n += (l[i].textContent || '').length; return n; }
  function textQuiet() { return Date.now() - sig.at; }
  function inputBodyLen() { var e = findInput(); return (e && e.value === undefined) ? (e.textContent || '').length : 0; }
  function sampleText() { var n = L.pageLen(((document.body && document.body.textContent) || '').length, oursLen(), inputBodyLen()); sig = L.sigStep(sig, n, Date.now());
    if (n !== sigX.len) sigX = { len: n, at: Date.now() }; }
  function isOurs(n) {
    var e = n && n.nodeType === 1 ? n : (n && n.parentElement);
    return !!(e && e.closest && e.closest('.aibridge-wrap, .aibridge-ctl'));
  }

  // ---- marker parsing ----
  function firstNonEmptyLine(text) {
    var lines = (text || '').split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      var t = lines[i].replace(/^\s+/, '');
      if (t.length > 0) return t;
    }
    return '';
  }
  function btext(el) { return L.blockText(el); }
  // 0.7.27: is the reply that holds this block complete? DeepSeek: .ds-message, then the action bar as its next sibling (loop.js replyDone)
  function replyFinished(block) {
    var m = block && block.closest ? block.closest('.ds-message') : null;
    if (!m) return L.replyDone({ hasMsg: false });
    var bar = m.nextElementSibling;
    return L.replyDone({ hasMsg: true, assistant: !!m.querySelector('.ds-assistant-message-main-content'),
      barIcons: bar ? bar.querySelectorAll('svg').length : 0 });
  }
  var warnedNoBar = false;
  function isMarkerFirst(text) { return firstNonEmptyLine(text).indexOf('# AIRUN') === 0; }
  function stripMarker(s) { return L.stripMarker(s); }
  function markerCount(text) { var m = String(text).match(/# AIRUN/g); return m ? m.length : 0; }
  function chainOf(el) {
    var out = [], cur = el.parentElement;
    while (cur && cur !== document.body && cur !== document.documentElement) {
      var own = (cur.textContent || '').replace(/^\s+/, '').slice(0, 40);
      out.push({ tag: cur.tagName, cls: cur.getAttribute('class') || '', role: cur.getAttribute('role') || '', lead: own });
      cur = cur.parentElement;
    }
    return out;
  }
  function findBlock(el) {
    var best = el;
    var cur = el.parentElement;
    while (cur && cur !== document.body) {
      if (!isMarkerFirst(cur.textContent || '')) break;
      if (markerCount(cur.textContent || '') > 1) break;   // a parent holding several blocks is not one block (bare sibling <pre>s; textContent joins them without a newline)
      best = cur;
      cur = cur.parentElement;
    }
    return best;
  }
  function allBlocks() {
    var cands = document.querySelectorAll('pre, code, [class*="code"], [class*="Code"]');
    var out = [];
    for (var i = 0; i < cands.length; i++) {
      var el = cands[i];
      if (isOurs(el)) continue;
      if (!isMarkerFirst(el.textContent || '')) continue;
      var b = findBlock(el);
      if (out.indexOf(b) < 0) out.push(b);
    }
    // thinking-panel drafts are not instructions; unknown containers fail closed (see loop.js selectBlocks)
    var sel = L.selectBlocks(out.map(function (b) { return { cmd: '', chain: chainOf(b) }; }));
    lastIgnored = sel.ignored.length;
    return sel.selected.map(function (i) { return out[i]; });
  }
  var ranEls = typeof WeakSet !== 'undefined' ? new WeakSet() : { add: function () {}, has: function () { return false; } };
  // 0.7.22 (Argon #1): the key is a hash of the text, so a block that ran half-written and then grew got a new key and ran again.
  // A block ELEMENT that already ran never runs a second time.
  function isUnrun(b) { return !ranKeys[blockKey(b)] && !ranEls.has(b); }
  function blockCmd(block) { return stripMarker(btext(block)).trim(); }
  function blockKey(block) {
    // fnv(cmd) + occurrence number among blocks with the same command: stable when other blocks shift the index
    var list = allBlocks();
    var keys = L.batchKeys(list.map(blockCmd));
    var at = list.indexOf(block);
    return at >= 0 ? keys[at] : L.fnv(L.normKey(blockCmd(block))) + '@x';
  }
  function dbgDump() {
    if (!alive()) { orphan(); return; }
    if (!ui.box) return;
    ui.box.dataset.dbg = JSON.stringify({ ver: VER, tab: tabId, autoRun: autoRun, runs: runs, resultN: resultN, working: working,
      pending: pending.map(function (p) { return { conn: p.block.isConnected, len: p.len, grew: p.grew }; }),
      quiet: Date.now() - lastMut, histLeft: histUntil - Date.now(), lastSendAgo: lastSend ? Date.now() - lastSend : null,
      tickAgo: lastTick ? Date.now() - lastTick : null, hidden: document.hidden,
      ran: Object.keys(ranKeys), blocks: allBlocks().map(blockKey) });
  }

  // ---- agent call ----
  var ridN = 0;
  function newRid() { ridN++; return tabId + '-' + Date.now().toString(36) + '-' + ridN; }
  function callAgent(cmd, opts, auto, rid, dry) {
    return new Promise(function (resolve) {
      if (!alive()) { orphan(); resolve(null); return; }
      try {
        chrome.runtime.sendMessage(
          { type: 'airun', cmd: cmd, host: opts.host, cwd: opts.cwd, timeout_s: opts.timeout_s, shell: opts.shell, auto: !!auto, rid: rid, dry: !!dry,
            task: opts.task, task_params: opts.params, task_spec: opts.task === 'inline' ? cmd : undefined },
          function (resp) {
            if (chrome.runtime.lastError) { resolve({ ok: false, cls: 'extension_link', error: 'the extension worker did not answer (' + chrome.runtime.lastError.message + ')' }); return; }
            resolve(resp || null);
          }
        );
      } catch (e) { resolve({ ok: false, cls: 'extension_link', error: String(e) }); }
    });
  }
  // One retry, only when nothing answered at the port (connection refused = the command never started).
  async function callWithRetry(cmd, opts, auto, rid) {
    var r = await callAgent(cmd, opts, auto, rid, false);
    if (r && !r.ok && r.cls === 'agent_unreachable') {
      await sleep(2000);
      var r2 = await callAgent(cmd, opts, auto, rid, false);
      if (r2) r = r2;
    }
    return r;
  }
  // 0.7.12 version drift: a mismatch is shown in the panel, put in every receipt (DSA sees it), and a stale extension reloads
  // itself when nothing is running; a page whose extension was reloaded under it re-attaches by reloading itself (idle, once per 10 min).
  var vstate = { level: 'ok', text: '' }, lastVer = 0;
  function idleNow() { return !inRun && !working && !(pending && pending.length); }
  // 0.7.22 (Argon #3): a reload or F5 drops the armed state and a chain in flight. Self-update only when hands-free is OFF; while armed the
  // red label says what to do and the update waits for the chain to end.
  function canSelfUpdate() { return idleNow() && !autoRun && !watch; }
  function versionTick() {
    var now = Date.now();
    if (now - lastVer < 60000) return;
    lastVer = now;
    if (!alive()) {
      try {
        var last = parseInt(sessionStorage.getItem('aibridge_orphan_reload') || '0', 10);
        if (idleNow() && now - last > 600000) { sessionStorage.setItem('aibridge_orphan_reload', String(now)); location.reload(); }
      } catch (e) {}
      return;
    }
    try {
      chrome.runtime.sendMessage({ type: 'version' }, function (v) {
        if (chrome.runtime.lastError || !v) return;
        ping().then(function (p) {
          var agent = p && p.ok && p.status === 200 && p.body ? p.body.agent : null;
          vstate = L.versionState(v.loaded || VER, v.disk, agent, VER);
          if (ui.verEl) ui.verEl.textContent = 'AIBridge: extension ' + (v.loaded || '?') + ' | this page ' + VER + ' | disk ' + (v.disk || '?') + ' | agent ' + (agent || '?') + (vstate.level === 'ok' ? ' - all match' : ' - MISMATCH, see below');
          if (ui.box) ui.box.dataset.ver = vstate.level;
          if (ui.ver) ui.ver.textContent = 'v' + VER + (vstate.level === 'ok' ? '' : ' !');
          refreshDetail();
          if (vstate.level !== 'ok' && ui.info) ui.info.textContent = vstate.text;
          if (vstate.level === 'page_stale' && canSelfUpdate()) {   // the extension is newer than this page's script: an F5 fixes it, so do it (idle, once per 10 min)
            try { var lp = parseInt(sessionStorage.getItem('aibridge_page_reload') || '0', 10); if (Date.now() - lp > 600000) { auditEvent('page ' + VER + ' older than extension ' + (v.loaded || '?') + ': reloading the page'); sessionStorage.setItem('aibridge_page_reload', String(Date.now())); location.reload(); } } catch (e) {}
          }
          if (vstate.level === 'ext_stale' && canSelfUpdate()) { try { chrome.runtime.sendMessage({ type: 'reload' }); } catch (e) {} }
        });
      });
    } catch (e) {}
  }
  function ping(host) {
    return new Promise(function (resolve) {
      if (!alive()) { resolve(null); return; }
      try { chrome.runtime.sendMessage({ type: 'ping', host: host }, function (r) { resolve(chrome.runtime.lastError ? null : r); }); } catch (e) { resolve(null); }
    });
  }
  function panelText(resp) {
    if (!resp) return 'no answer from the extension (reloaded/disabled? press F5)';
    if (!resp.ok) return (resp.cls || 'error') + ': ' + resp.error;
    var b = resp.body || {};
    if (resp.status !== 200) return 'HTTP ' + resp.status + '\nREFUSED: ' + (b.reason || b.error || '') + '\n' + JSON.stringify(b, null, 2);
    return 'exit=' + b.exit + '  ms=' + b.ms + (b.out_truncated ? '  OUTPUT TRUNCATED' : '') +
      (b.timed_out ? '  TIMED OUT' : '') + '  host=' + (b.host || '?') + '  lines=' + b.cmd_lines + '\n' + (b.out || '') + (b.err ? '\n[err]\n' + b.err : '');
  }
  // verify the answer belongs to this block; a mismatch turns into an explicit error result, never a silent wrong one
  function vet(rid, cmd, resp, isTask) {
    var problem = L.checkEcho(rid, cmd, resp, isTask);
    return problem ? { ok: false, cls: 'bridge_mismatch', error: problem } : resp;
  }
  function failed(resp) {
    return L.blockFailed(resp);
  }

  // ---- posting several results as one message ----
  async function postParts(text, n, myToken, label) {
    var parts = L.splitParts(text, n, CFG.aibridge_max_chars);
    for (var i = 0; i < parts.length; i++) {
      setStatus('posting ' + label + (parts.length > 1 ? ' part ' + (i + 1) + '/' + parts.length : ''));
      var ok = await postToChat(parts[i], myToken);
      if (!ok) return false;
      if (i < parts.length - 1) {
        // let DSA answer the "more parts follow" part, then ignore anything it wrote
        var t0 = lastMut;
        for (var w = 0; w < 100 && lastMut === t0; w++) await sleep(300);
        if (!(await waitQuiet(myToken, CFG.aibridge_wait_ms))) { lastPostErr = 'the chat stayed busy after part ' + (i + 1); return false; }
        allBlocks().forEach(function (b) { ranKeys[blockKey(b)] = true; });
      }
    }
    return true;
  }

  // ---- manual run (button) ----
  function runManual(block, btn, panel) {
    var cmd = blockCmd(block);
    var opts = L.parseMarker(btext(block));
    if (!cmd && !opts.task) { panel.style.display = 'block'; panel.textContent = 'empty command'; return; }
    btn.disabled = true;
    panel.style.display = 'block'; panel.textContent = 'running...';
    var myToken = token;
    var rid = newRid();
    callWithRetry(cmd, opts, false, rid).then(async function (resp0) {
      var resp = vet(rid, cmd, resp0, !!opts.task);
      btn.disabled = false;
      panel.textContent = panelText(resp);
      // close the loop: DSA gets the result of a manual Run the same way as an auto-run
      resultN++;
      var n = resultN;
      var text = L.formatResult(n, opts.task ? 'TASK ' + opts.task + ' ' + JSON.stringify(opts.params || {}) : cmd, resp, 'run manually by the operator', { blocks_seen: 1, blocks_run: 1, index: 1, rid: rid });
      var ok = await postParts(text, n, myToken, '#' + n);
      if (!ok) { setStatus('manual result #' + n + ' not posted; copy it from the panel'); return; }
      setStatus('waiting for DSA after #' + n);
    });
  }
  function labelButton(block, btn, resp) {
    var b = resp && resp.ok && resp.body;
    if (!b) { btn.textContent = 'Run (agent?)'; return; }
    if (b.ok) btn.textContent = autoRun ? 'Run (auto)' : 'Run';
    else btn.textContent = 'Run (click needed: ' + String(b.reason || '').split(':')[0] + ')';
    btn.title = b.ok ? 'kind=' + b.kind + '; ' + (b.reason || '') : (b.reason || '');
  }
  function attachButton(block) {
    if (seen.has(block)) return false;
    seen.add(block);
    var wrap = document.createElement('div');
    wrap.className = 'aibridge-wrap';
    var btn = document.createElement('button');
    btn.className = 'aibridge-btn';
    btn.textContent = 'Run';
    var panel = document.createElement('pre');
    panel.className = 'aibridge-panel';
    panel.style.display = 'none';
    btn.addEventListener('click', function () { runManual(block, btn, panel); });
    wrap.appendChild(btn);
    wrap.appendChild(panel);
    block.parentNode.insertBefore(wrap, block.nextSibling);
    block.__aibPanel = panel;
    block.__aibBtn = btn;
    return true;
  }
  // after a block has stopped streaming, ask the agent (dry run) whether auto-run would take it and label the button
  function labelTick() {
    if (labelBusy || !alive() || baseline || textQuiet() < CFG.aibridge_quiet_ms) return;
    var list = allBlocks();
    for (var i = 0; i < list.length; i++) {
      var b = list[i];
      if (!b.__aibBtn || b.__aibLabeledFor === btext(b)) continue;
      labelBusy = true;
      b.__aibLabeledFor = btext(b);
      var cmd = blockCmd(b), opts = L.parseMarker(btext(b));
      callAgent(cmd, opts, true, newRid(), true).then(function (r) { labelButton(b, b.__aibBtn, r); labelBusy = false; });
      return;
    }
  }

  // ---- chat input ----
  function visible(el) {
    var r = el.getBoundingClientRect();
    return r.width > 4 && r.height > 4 && getComputedStyle(el).visibility !== "hidden";
  }
  function findInput() {
    var c = document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"]');
    var best = null, bestBottom = -1;
    for (var i = 0; i < c.length; i++) {
      if (isOurs(c[i]) || !visible(c[i])) continue;
      var b = c[i].getBoundingClientRect().bottom;
      if (b > bestBottom) { best = c[i]; bestBottom = b; }
    }
    return best;
  }
  function rawInput(el) { return el ? ((el.value !== undefined ? el.value : el.textContent) || '') : ''; }
  function inputText(el) { return ((el.value !== undefined ? el.value : el.textContent) || '').trim(); }
  function liveInput(el) { return el ? { node: el, attached: el.isConnected, text: inputText(el) } : null; }
  function nowInput() { var e = findInput(); return e ? { node: e, text: inputText(e) } : null; }
  function setInput(el, text) {
    el.focus();
    if (el.tagName === 'TEXTAREA') {
      var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      setter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      document.execCommand('selectAll', false, null);
      document.execCommand('insertText', false, text);
    }
  }
  function pressEnter(el) {
    var o = { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true };
    el.dispatchEvent(new KeyboardEvent('keydown', o));
    el.dispatchEvent(new KeyboardEvent('keypress', o));
    el.dispatchEvent(new KeyboardEvent('keyup', o));
  }
  function clickSend(el) {
    var cur = el.parentElement;
    for (var up = 0; cur && up < 6; up++, cur = cur.parentElement) {
      var bs = Array.prototype.filter.call(cur.querySelectorAll('button, [role="button"]'), function (x) { return !isOurs(x); });
      var pick = L.pickSendButton(bs.map(function (x) {
        return { label: (x.getAttribute('aria-label') || '') + ' ' + (x.getAttribute('title') || '') + ' ' + (x.textContent || '').slice(0, 30), disabled: x.disabled || x.getAttribute('aria-disabled') === 'true' };
      }));
      if (pick >= 0) { bs[pick].click(); return true; }
    }
    return false;
  }
  async function waitQuiet(myToken, maxMs) {
    var t0 = Date.now();
    while (Date.now() - t0 < maxMs) {
      if (myToken !== token) return false;
      if (textQuiet() >= CFG.aibridge_quiet_ms) return true;
      await sleep(300);
    }
    return false;
  }
  async function postToChat(text, myToken, maxMs) {
    if (!(await paceGate(myToken))) return false;
    var t0 = Date.now(), lim = maxMs || CFG.aibridge_wait_ms;
    while (true) {
      if (myToken !== token) return false;
      if (Date.now() - t0 > lim) { lastPostErr = 'the chat never became idle (or an operator draft sits in the input)'; return false; }
      var el = findInput();
      var idle = !!el && textQuiet() >= CFG.aibridge_quiet_ms;
      if (L.postGate({ idle: idle, draft: el ? inputText(el) : '', waitedMs: Date.now() - t0, maxMs: lim }) === 'send_keep_draft') break;
      await sleep(400);
    }
    var el2 = findInput();
    var draft = rawInput(el2);   // B196: an operator draft is saved, never overwritten or lost
    setInput(el2, text);
    await sleep(400);
    lastSend = Date.now();
    pressEnter(el2);
    // DeepSeek can replace the input node after a send: judge by the chat's current input, not only the node we typed into
    var landed = false;
    for (var i = 0; i < 8 && !landed; i++) { await sleep(250); landed = L.postLanded(liveInput(el2), nowInput()); }
    if (!landed) {
      clickSend(el2);
      for (var j = 0; j < 12 && !landed; j++) { await sleep(250); landed = L.postLanded(liveInput(el2), nowInput()); }
    }
    if (!landed) {
      lastPostErr = 'the chat input did not clear after sending';
      var elx = findInput();   // 0.7.22 (Argon #2): our text left in the box would read as busy and as an operator draft; put the operator's draft back
      if (elx) setInput(elx, draft);
      return false;
    }
    if (draft.trim() !== '') {
      var el3 = findInput();
      if (el3) setInput(el3, draft);
      if (!el3 || inputText(el3) !== draft.trim()) setStatus('could not restore your draft; it was: ' + draft.slice(0, 200));
    }
    return true;
  }

  // ---- auto loop ----
  function setStatus(s) { if (ui.status) ui.status.textContent = s; if (ui.line) { ui.line.title = s; } if (ui.glyph) ui.glyph.textContent = L.ctlGlyph(s); refreshDetail(); }
  function refreshDetail(force) {   // 0.7.28: detail lines only on a problem (loop.js ctlDetail) or a click on the version
    if (!ui.box) return;
    ui.box.dataset.show = (force || L.ctlDetail(ui.status && ui.status.textContent, ui.info && ui.info.textContent, vstate.level)) ? '1' : '';
  }
  function refreshUi() {
    if (!ui.box) return;
    ui.cb.checked = autoRun;
    ui.count.textContent = runs + '/' + CFG.aibridge_cap;
    ui.box.className = 'aibridge-ctl' + (autoRun ? ' on' : '');
  }
  // ---- 0.7.33: DeepSeek block guard (card dsa-bridge-avoid-deepseek-block-1108; pure rules in loop.js) ----
  // State lives in chrome.storage.local, so every chat tab of one browser profile (= one DeepSeek account) shares it.
  var PACE_KEY = 'aibridge_pace', ARMED_KEY = 'aibridge_armed', COOL_KEY = 'aibridge_cooldown_until', ACCT_KEY = 'aibridge_account';
  var armedHere = false, acctLabel = L.leaseAccount(''), lastBeat = 0, lastWarnChk = 0, paceAudited = 0;
  function sget(keys) { return new Promise(function (res) { try { chrome.storage.local.get(keys, function (r) { res(r || {}); }); } catch (e) { res({}); } }); }
  function sset(o) { return new Promise(function (res) { try { chrome.storage.local.set(o, function () { res(); }); } catch (e) { res(); } }); }
  // one event to the agent (audit row, or the account lease); resolves with the worker's response or null
  function sendEvent(text) {
    return new Promise(function (res) {
      if (!alive()) { res(null); return; }
      try { chrome.runtime.sendMessage({ type: 'airun', event: String(text).slice(0, 400), auto: true, rid: newRid() }, function (r) { void chrome.runtime.lastError; res(r || null); }); } catch (e) { res(null); }
    });
  }
  // what the page shows outside the chat messages: dialogs, alerts, toasts (DSA may write "captcha" in a message; that is not a warning)
  function pageSnapshot() {
    var o = [];
    try {
      var l = document.querySelectorAll('[role="dialog"], [role="alertdialog"], [role="alert"], [aria-modal="true"], [class*="modal" i], [class*="toast" i], [class*="dialog" i]');
      for (var i = 0; i < l.length && o.length < 12; i++) { if (!isOurs(l[i])) o.push(String(l[i].innerText || l[i].textContent || '').slice(0, 400)); }
    } catch (e) {}
    var cf = false, pw = false;
    try { cf = !!document.querySelector('iframe[src*="captcha" i], iframe[src*="turnstile" i], iframe[src*="recaptcha" i], iframe[src*="geetest" i], #captcha, [class*="captcha" i]'); } catch (e) {}
    try { pw = !!document.querySelector('input[type="password"]'); } catch (e) {}
    return { href: location.href, overlays: o, captchaFrame: cf, hasPassword: pw };
  }
  function refuseArm(reason, text) {
    autoRun = false; stopHold = true; token++; pending = []; watch = null;
    auditEvent('arm refused (' + reason + '): ' + text);
    setStatus(text); showStopBanner(text); refreshUi();
  }
  // hands-free arms only when: no warning cooldown on this profile, no warning on the page, no other armed tab, the agent grants the account lease
  async function tryArm() {
    var now = Date.now(), r = await sget([COOL_KEY, ARMED_KEY, ACCT_KEY]);
    acctLabel = L.leaseAccount(r[ACCT_KEY]);
    if (L.cooldownLeft(r[COOL_KEY], now)) { refuseArm('cooldown', 'AIBridge hands-free refused: ' + L.cooldownText(r[COOL_KEY], now) + '. Use the chat by hand.'); return; }
    var w = L.warnState(pageSnapshot());
    if (w.warn) { await sset((function () { var o = {}; o[COOL_KEY] = L.cooldownUntil(now); return o; })()); refuseArm('warning', L.warnStopText(w)); return; }
    var g = L.armGate(r[ARMED_KEY] || {}, tabId, now);
    if (!g.ok) { refuseArm('second_tab_refused', 'second_tab_refused: chat ' + g.holder + ' in this browser profile is already armed. One armed chat per DeepSeek account: untick it there first.'); return; }
    var lr = L.parseLeaseReply(await sendEvent(L.leaseEvent('acquire', acctLabel)));
    if (!lr.ok) { refuseArm(lr.reason, lr.text); return; }
    var o2 = {}; o2[ARMED_KEY] = g.reg; await sset(o2);
    armedHere = true; autoRun = true; runs = 0; stopHold = false; lastBeat = now; lastWarnChk = now;
    refreshUi(); preflight('on:');
  }
  async function releaseArm() {
    var r = await sget([ARMED_KEY]), o = {}; o[ARMED_KEY] = L.armRelease(r[ARMED_KEY] || {}, tabId); await sset(o);
    await sendEvent(L.leaseEvent('release', acctLabel));
  }
  // every second while armed: warning page -> off + cooldown; every 30 s: keep the tab slot and the lease alive
  function guardTick() {
    if (!autoRun || !armedHere) return;
    var now = Date.now();
    if (now - lastWarnChk >= 1000) {
      lastWarnChk = now;
      var w = L.warnState(pageSnapshot());
      if (w.warn) { onWarning(w); return; }
    }
    if (now - lastBeat >= 30000) { lastBeat = now; beatArm(); }
  }
  async function onWarning(w) {
    var o = {}; o[COOL_KEY] = L.cooldownUntil(Date.now()); await sset(o);
    auditEvent('WARNING ' + w.warn + ' | hands-free off, no retry, 24 h cooldown on this profile');
    stopAuto(L.warnStopText(w), true);
  }
  async function beatArm() {
    var now = Date.now(), r = await sget([ARMED_KEY]), g = L.armGate(r[ARMED_KEY] || {}, tabId, now);
    if (!autoRun) return;
    if (!g.ok) { stopAuto('second_tab_refused: chat ' + g.holder + ' in this profile is armed too. One armed chat per DeepSeek account.'); return; }
    var o = {}; o[ARMED_KEY] = g.reg; await sset(o);
    var lr = L.parseLeaseReply(await sendEvent(L.leaseEvent('beat', acctLabel)));
    if (autoRun && lr.reason === 'account_in_use') stopAuto(lr.text);
  }
  // pacing: every auto post waits for the guard (60 s + 10-30 s jitter since the last post of this profile, 15 an hour, 80 a day).
  // A short wait is shown and waited out; an hour or day limit refuses the post (says paced) and hands-free stops.
  async function paceGate(myToken) {
    var jit = L.paceJitter();
    while (true) {
      if (myToken !== token) return false;
      var now = Date.now(), r = await sget([PACE_KEY]), hist = (r[PACE_KEY] || []).filter(function (x) { return typeof x === 'number' && now - x < 86400000; });
      var c = L.paceCheck(hist, now, jit);
      if (c.ok) { hist.push(now); var o = {}; o[PACE_KEY] = hist.slice(-200); await sset(o); return true; }
      if (c.cap !== 'gap' || c.waitMs > 120000) { lastPostErr = L.paceText(c); auditEvent('post refused: ' + lastPostErr); return false; }
      setStatus(L.paceText(c));
      if (now - paceAudited > 60000) { paceAudited = now; auditEvent('post waits: ' + L.paceText(c)); }
      await sleep(Math.min(c.waitMs, 1000));
    }
  }
  // 0.7.18: every stop and retry reason goes to the agent's audit log (the banner is invisible there)
  function auditEvent(text) {
    try { if (alive()) chrome.runtime.sendMessage({ type: 'airun', event: String(text).slice(0, 400), auto: true, rid: newRid() }, function () { void chrome.runtime.lastError; }); } catch (e) {}
  }
  var emptyFirst = 0;
  function stopAuto(why, final) {
    auditEvent('auto OFF: ' + (why || 'stopped'));
    emptyFirst = 0;
    autoRun = false; stopHold = true; token++; pending = []; watch = null;
    if (armedHere) { armedHere = false; releaseArm(); }
    setStatus(why || 'stopped');
    showStopBanner(final ? why : L.stopNotice(why));
    refreshUi();
  }
  // visible banner (extension DOM element, not a sent message) so a silent auto-off is impossible
  function showStopBanner(msg) {
    try {
      var b = document.getElementById('aibridge-stop-banner');
      if (!b) {
        b = document.createElement('div'); b.id = 'aibridge-stop-banner';
        b.style.cssText = 'position:fixed;left:50%;bottom:90px;transform:translateX(-50%);z-index:2147483647;max-width:560px;padding:10px 14px;background:#7a1f1f;color:#fff;font:13px/1.4 sans-serif;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.4);cursor:pointer';
        b.title = 'click to dismiss'; b.addEventListener('click', function () { b.remove(); });
        document.body.appendChild(b);
      }
      b.textContent = msg;
    } catch (e) { }
  }
  // preflight: prove extension -> agent round trip and say which host/shell answers
  async function preflight(prefix) {
    var r = await ping();
    var line;
    if (!r) line = 'PREFLIGHT FAIL extension_link: the extension did not answer. Reload it in chrome://extensions, then F5.';
    else if (!r.ok) line = 'PREFLIGHT FAIL agent_unreachable: no agent on port 7181. Start it: powershell -File F:\\AIBridge\\scripts\\start-agent.ps1';
    else if (r.status !== 200 || !r.body || !r.body.ok) line = 'PREFLIGHT FAIL agent answered http ' + r.status;
    else line = 'agent ' + r.body.agent + ' on ' + r.body.host + ', PowerShell ' + r.body.shell_version + (r.body.pwsh ? ' (+pwsh)' : '') + ', running ' + r.body.running;
    if (ui.info) ui.info.textContent = line;
    if (prefix) setStatus(prefix + ' ' + line); else refreshDetail();
    return line;
  }

  // Run every unrun block of the finished reply, in order; post ONE message with a receipt for each block.
  async function runBatch(trigger) {
    var myToken = token;
    var blocks = allBlocks().filter(function (b) { return isUnrun(b); });
    if (!blocks.length && trigger && isUnrun(trigger)) blocks = [trigger];
    if (!blocks.length) return;
    // 0.7.18: read a block only when complete. (a) a block with a marker but no body yet is still rendering: wait up to 30 s
    // instead of reporting 'no command' and marking it done; (b) the text must be identical across a second read 1.2 s later,
    // so a pause in the stream never runs a half-written command.
    var bodyless = blocks.filter(function (b) { return !blockCmd(b) && !L.parseMarker(btext(b)).task; });
    if (bodyless.length) {
      if (!emptyFirst) { emptyFirst = Date.now(); auditEvent('block body not rendered yet, waiting (' + bodyless.length + ' of ' + blocks.length + ')'); }
      if (Date.now() - emptyFirst < 30000) { setStatus('a block has no body yet; waiting for the page to finish rendering it'); return; }
    } else emptyFirst = 0;
    var snap = blocks.map(btext).join('\u0001');
    await sleep(1200);
    if (myToken !== token) return;
    var again = allBlocks().filter(function (b) { return isUnrun(b); });
    if (again.map(btext).join('\u0001') !== snap) { setStatus('the reply was still changing; reading it again'); return; }
    emptyFirst = 0;
    if (runs >= CFG.aibridge_cap) { stopAuto('auto OFF at the cap: ' + CFG.aibridge_cap + ' blocks ran in this chain. Tick the box again to continue (the counter restarts).'); return; }
    // mark first: a block is never run twice, and anything that appears while we run belongs to the next reply
    var items = blocks.map(function (b) { var o = L.parseMarker(btext(b)); return { block: b, cmd: blockCmd(b), opts: o, shown: o.task ? 'TASK ' + o.task + ' ' + JSON.stringify(o.params || {}) + (o.task === 'inline' ? ' plan=' + L.cmdPreview(blockCmd(b), 300) : '') : null }; });
    items.forEach(function (it) { ranKeys[blockKey(it.block)] = true; ranEls.add(it.block); });
    pending = [];
    var dups = L.dupOf(items.map(function (it) { return btext(it.block); }));
    inRun = true;
    var seenN = items.length, cap = CFG.aibridge_max_blocks, ran = 0, stop = null;
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      resultN++; it.n = resultN; it.rid = newRid(); it.index = i + 1;
      if (i >= cap) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: over the per-reply cap of ' + cap + ' blocks. Send it in your next reply.' }; continue; }
      if (dups[i]) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: duplicate of block ' + dups[i] + ' in this reply. To repeat a command on purpose, change it (add a # again line).' }; continue; }
      if (stop) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: block ' + stop.idx + ' ended with ' + stop.why + ' and this block may depend on it. Re-send it if it should still run.' }; continue; }
      if (!it.cmd && !it.opts.task) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: the block has no command after the # AIRUN line.' }; continue; }
      runs++; refreshUi();
      setStatus('running #' + it.n + (seenN > 1 ? ' (block ' + (i + 1) + '/' + seenN + ')' : '') + ': ' + it.cmd.split('\n')[0].slice(0, 60));
      var resp = vet(it.rid, it.cmd, await L.raceDeadline(callWithRetry(it.cmd, it.opts, true, it.rid), L.expireMs(it.opts.timeout_s, !!it.opts.task), function () {
        return ping(it.opts.host).then(function (r) { return (r && r.ok && r.body && r.body.running != null) ? r.body.running : null; });
      }, L.extendMs(!!it.opts.task)), !!it.opts.task);
      it.resp = resp; ran++;
      if (it.block.__aibPanel) { it.block.__aibPanel.style.display = 'block'; it.block.__aibPanel.textContent = '[auto #' + it.n + ']\n' + panelText(resp); }
      if (myToken !== token) { inRun = false; return; }
      var why = failed(resp);
      if (why) stop = { idx: i + 1, why: why };
    }
    inRun = false;
    var texts = items.map(function (it) {
      return L.formatResult(it.n, it.shown || it.cmd, it.resp, '', { blocks_seen: seenN, blocks_run: ran, index: it.index, rid: it.rid });
    });
    var text = (vstate.level !== 'ok' ? '[AIRUN WARNING] ' + vstate.text + '\n' : '') + (seenN > 1 ? '[AIRUN BATCH] blocks_seen=' + seenN + ' blocks_run=' + ran + ' not_run=' + (seenN - ran) + '\n' : '') + texts.join('\n\n');
    var lastN = items[items.length - 1].n;
    var ok = await postParts(text, lastN, myToken, '#' + lastN);
    // 0.7.18: a result that could not be posted because the chat stayed busy is queued and retried, never dropped
    for (var rt = 0; !ok && myToken === token && rt < 4 && L.postRetryable(lastPostErr); rt++) {
      auditEvent('result #' + lastN + ' not posted (' + lastPostErr + '); retry ' + (rt + 1) + '/4');
      setStatus('result #' + lastN + ' is queued: it could not be posted yet; retrying');
      await sleep(5000);
      ok = await postParts(text, lastN, myToken, '#' + lastN + ' (retry ' + (rt + 1) + ')');
    }
    if (!ok) { if (myToken === token) stopAuto('auto OFF: the result was not posted (' + lastPostErr + '). Tick the box again to re-arm.'); return; }
    setStatus('waiting for DSA after #' + lastN);
    watch = L.replyWatch(watch, { type: 'posted' }, Date.now()).state; postedAnsLen = answerLen();
    // DSA's reply to our result: if it contains no new block it has finished, so hand control back
    var t1 = lastMut;
    for (var w2 = 0; w2 < 100 && lastMut === t1; w2++) await sleep(300);
    if (myToken !== token) return;
    await waitQuiet(myToken, CFG.aibridge_wait_ms);   // on timeout still rescan: never leave a finished reply unread
    if (myToken !== token) return;
    scan(); await sleep(600);
    if (watch && watch.phase === 'waiting' && pending.length === 0) setStatus('waiting for DSA after #' + lastN + ' (a notice follows if no answer comes)');
    // stay armed: the next DSA block runs without a click; runs resets because the chain ended here
    if (myToken === token && autoRun && pending.length === 0) { runs = 0; refreshUi(); setStatus('armed: waiting for the next DSA block (untick to stop)'); }
  }
  async function pump() {
    if (!alive()) { orphan(); return; }
    if (working || !autoRun) return;
    working = true;
    try {
      while (autoRun && pending.length) {
        var item = pending[0];
        if (!item.block.isConnected) { pending.shift(); continue; }
        if (textQuiet() < CFG.aibridge_quiet_ms) {
          if (!quietSince) quietSince = Date.now();
          setStatus(L.quietWaitStatus(Date.now() - quietSince, CFG.aibridge_wait_ms));   // never a silent loop
          await sleep(500); continue;
        }
        var rf = replyFinished(item.block);
        if (rf.known && !rf.done) {   // 0.7.27: never run a block DSA is still writing
          if (!quietSince) quietSince = Date.now();
          setStatus('waiting: DSA is still writing this reply (' + Math.round((Date.now() - quietSince) / 1000) + ' s)');
          await sleep(500); continue;
        }
        if (!rf.known && !warnedNoBar) { warnedNoBar = true; auditEvent('no reply-finished marker on this page (DeepSeek DOM changed?); blocks run on the quiet rule'); }
        quietSince = 0;
        pending.shift();
        await runBatch(item.block);
      }
    } finally { working = false; quietSince = 0; }
  }
  // page text length without the thinking panel and without our own UI: growth here is DSA's answer arriving
  function answerLen() {
    var n = ((document.body && document.body.textContent) || '').length - oursLen();
    var th = document.querySelectorAll('[class*="think" i], [class*="thought" i], [class*="reason" i], thought, details');
    for (var i = 0; i < th.length; i++) {
      var p = th[i].parentElement;
      if (p && p.closest && p.closest('[class*="think" i], [class*="thought" i], [class*="reason" i], thought, details')) continue;
      if (!isOurs(th[i])) n -= (th[i].textContent || '').length;
    }
    return n;
  }
  var replyBusy = false;
  var inRun = false;             // a block is running (replyWatch never fires then)
  // one notice per chain when DSA's generation drops after our result, then a stop banner (D4); never during a run
  async function replyTick() {
    if (!watch || watch.phase !== 'waiting' || !autoRun || replyBusy) return;
    var answered = pending.length > 0 || allBlocks().some(function (b) { return isUnrun(b); }) ||
      (Date.now() - sigX.at >= CFG.aibridge_quiet_ms && answerLen() - postedAnsLen >= L.ANSWER_MIN_CHARS);
    if (answered) { watch = L.replyWatch(watch, { type: 'reply' }, Date.now()).state; return; }
    var r = L.replyWatch(watch, { type: 'tick', busy: inRun || !!inputText(findInput() || {}) }, Date.now());
    watch = r.state;
    if (r.action === 'notice') {
      replyBusy = true;
      try {
        var myToken = token;
        var ok = await postToChat(L.REPLY_NOTICE_TEXT, myToken, 15000);   // a chat that never goes idle gets the stop banner instead
        if (myToken !== token) return;
        if (!ok) { stopAuto('DSA showed no final answer after the result and the chat never went idle for a wake-up notice (' + lastPostErr + '). Re-send your request in the chat.'); return; }
        postedAnsLen = answerLen();
        setStatus('DSA sent no final answer; posted a notice, waiting once more');
      } finally { replyBusy = false; }
    } else if (r.action === 'stop') {
      watch = null;
      stopAuto('DSA never answered after the result and the notice (its generation dropped). Re-send your request in the chat.');
    }
  }
  function growCheck() {
    for (var i = 0; i < pending.length; i++) {
      var p = pending[i];
      if (!p.grew && (p.block.textContent || '').length !== p.len) p.grew = true;
    }
  }
  var lastWatch = 0;
  // watchdog: a reply that finished with a block nobody queued is picked up here (never silently stuck)
  function watchdog() {
    if (Date.now() - lastWatch < 2000) return;
    lastWatch = Date.now();
    if (!alive() || baseline || working || textQuiet() < CFG.aibridge_quiet_ms) return;
    var seen = allBlocks();
    if (!seen.length && lastIgnored > 0 && !stopHold) setStatus('ignored ' + lastIgnored + ' block(s) inside the thinking panel (only the final answer runs)');
    var unrun = seen.filter(function (b) { return isUnrun(b); });
    if (!unrun.length) return;
    if (autoRun && pending.length === 0) {
      var u = unrun[unrun.length - 1];
      pending.push({ block: u, since: Date.now(), len: (u.textContent || '').length, grew: true });
      setStatus('watchdog: queued an unrun block from the finished reply');
    } else if (!autoRun && !stopHold) {
      setStatus('reply complete, ' + unrun.length + ' block(s) waiting: click Run');
    }
  }
  // plain timers stay as the foreground path; the port tick above is what keeps a background window moving
  setInterval(dbgDump, 1000);
  setInterval(function () { sampleText(); growCheck(); }, 250);
  setInterval(pump, 250);
  setInterval(replyTick, 1000);
  setInterval(watchdog, 2000);
  setInterval(linkCheck, 1000);
  setInterval(guardTick, 1000);
  setInterval(versionTick, 5000);   // gated to once a minute inside; onTick also calls it
  setInterval(function () { if (location.href !== lastHref) { lastHref = location.href; if (!lastSend || Date.now() - lastSend > 15000) histUntil = Date.now() + 6000; } }, 500);
  document.addEventListener('click', function (e) { var t = e.target; if (!t || !t.closest || isOurs(t) || !t.closest('button, [role="button"]')) return; var inp = findInput(); if (!inp) return; var box = inp; for (var u = 0; u < 4 && box.parentElement; u++) box = box.parentElement; if (box.contains(t)) lastSend = Date.now(); }, true);

  // ---- scanning ----
  var scanTimer = null;
  function scan() {
    var list = allBlocks();
    for (var i = 0; i < list.length; i++) {
      var b = list[i];
      var fresh = attachButton(b);
      if (!fresh) continue;
      var recentSend = lastSend && Date.now() - lastSend < 30000;
      if (baseline || (Date.now() < histUntil && !recentSend)) { ranKeys[blockKey(b)] = true; continue; }   // history: never auto-run
      if (autoRun) pending.push({ block: b, since: Date.now(), len: (b.textContent || '').length, grew: false });
    }
  }
  var obs = new MutationObserver(function (recs) {
    var real = false;
    for (var i = 0; i < recs.length && !real; i++) {
      var r = recs[i];
      if (isOurs(r.target)) continue;
      var nodes = Array.prototype.slice.call(r.addedNodes).concat(Array.prototype.slice.call(r.removedNodes));
      if (nodes.length && nodes.every(isOurs)) continue;
      real = true;
    }
    if (!real) return;
    lastMut = Date.now();
    if (!scanTimer) scanTimer = setTimeout(function () { scanTimer = null; scan(); }, 250);   // throttle, not debounce: must see a block while it streams
  });

  // ---- control box ----
  function buildUi() {
    var st = document.createElement('style');
    // 0.7.28: one line (tick, runs/cap, link dot, version), draggable; the detail lines open only on a problem or a click on the version
    st.textContent = '.aibridge-ctl{position:fixed;right:12px;bottom:12px;z-index:2147483647;background:#1b1b1b;color:#ddd;' +
      'font:12px/1.3 sans-serif;padding:3px 8px;border-radius:8px;border:1px solid #444;max-width:360px;cursor:move;user-select:none}' +
      '.aibridge-ctl .ln{display:flex;align-items:center;gap:6px;white-space:nowrap}.aibridge-ctl .ln label{cursor:pointer}' +
      '.aibridge-ctl .vr{color:#798;cursor:pointer}.aibridge-ctl .gl{color:#9ab;min-width:1em}' +
      '.aibridge-ctl.on{border-color:#2e9e4f}.aibridge-ctl button{margin-left:6px;font-size:12px;cursor:pointer}' +
      '.aibridge-ctl .dt{display:none}.aibridge-ctl[data-show="1"] .dt{display:block;white-space:normal;max-width:340px}' +
      '.aibridge-ctl .st{margin-top:4px;color:#9ab;word-break:break-word}.aibridge-ctl .in{margin-top:2px;color:#798;font-size:11px;word-break:break-word}';
    document.head.appendChild(st);
    var box = document.createElement('div');
    box.className = 'aibridge-ctl';
    var line = document.createElement('div'); line.className = 'ln';
    var lab = document.createElement('label');
    var cb = document.createElement('input');
    cb.type = 'checkbox';
    lab.appendChild(cb);
    lab.appendChild(document.createTextNode(' Hands-free'));
    lab.title = 'DSA runs every AIRUN block on its own (this chat only)';
    var count = document.createElement('span'); count.title = 'blocks run / cap';
    var glyph = document.createElement('span'); glyph.className = 'gl';
    var ver = document.createElement('span'); ver.className = 'vr'; ver.textContent = 'v' + VER; ver.title = 'click: show or hide the detail lines';
    var status = document.createElement('div'); status.className = 'st'; status.textContent = 'off: click Run on each block';
    var info = document.createElement('div'); info.className = 'in'; info.textContent = 'AIBridge ' + VER + ' (this chat only)';
    var verEl = document.createElement('div'); verEl.className = 'aibridge-ver'; verEl.textContent = 'AIBridge page ' + VER + ' (checking extension and agent...)';
    var link = document.createElement('span'); link.textContent = '\u25CB'; link.title = 'link: starting'; link.style.cursor = 'help';
    var detail = document.createElement('div'); detail.className = 'dt';
    line.appendChild(lab); line.appendChild(count); line.appendChild(link); line.appendChild(glyph); line.appendChild(ver);
    detail.appendChild(status); detail.appendChild(verEl); detail.appendChild(info);
    box.appendChild(line); box.appendChild(detail);
    document.body.appendChild(box);
    ui = { box: box, cb: cb, count: count, status: status, info: info, link: link, verEl: verEl, line: line, glyph: glyph, ver: ver };
    line.title = status.textContent;
    var forced = false;
    ver.addEventListener('click', function (e) { e.stopPropagation(); forced = !forced; refreshDetail(forced); });
    // drag anywhere on the box except the tick and the version; the place is kept for this tab (sessionStorage)
    var drag = null;
    function place(x, y) {
      x = Math.max(0, Math.min(x, window.innerWidth - box.offsetWidth)); y = Math.max(0, Math.min(y, window.innerHeight - box.offsetHeight));
      box.style.left = x + 'px'; box.style.top = y + 'px'; box.style.right = 'auto'; box.style.bottom = 'auto';
    }
    box.addEventListener('mousedown', function (e) {
      if (e.button !== 0 || e.target === cb || e.target === ver || e.target.tagName === 'BUTTON' || e.target.tagName === 'LABEL') return;
      var r = box.getBoundingClientRect(); drag = { dx: e.clientX - r.left, dy: e.clientY - r.top, moved: false }; e.preventDefault();
    });
    document.addEventListener('mousemove', function (e) { if (!drag) return; drag.moved = true; place(e.clientX - drag.dx, e.clientY - drag.dy); });
    document.addEventListener('mouseup', function () {
      if (!drag) return;
      if (drag.moved) { try { sessionStorage.setItem('aibridge_ctl_pos', box.style.left + ',' + box.style.top); } catch (e) {} }
      drag = null;
    });
    try { var pos = (sessionStorage.getItem('aibridge_ctl_pos') || '').split(','); if (pos.length === 2 && pos[0]) { box.style.left = pos[0]; box.style.top = pos[1]; box.style.right = 'auto'; box.style.bottom = 'auto'; } } catch (e) {}
    cb.addEventListener('change', function () {
      if (cb.checked) { autoRun = false; tryArm(); } else stopAuto('off: click Run on each block');
      refreshUi();
    });
    refreshUi();
  }

  // 0.7.30: "Start DSA bridge" typed as the whole message is swapped for the seed (agent POST /seed through the worker) and sent.
  // Enter or the send button with exactly that text is caught before DeepSeek sees it. Agent down: nothing is sent, the phrase stays.
  var seeding = false;
  function fetchSeed() {
    return new Promise(function (resolve) {
      if (!alive()) { orphan(); resolve(null); return; }
      try {
        chrome.runtime.sendMessage({ type: 'seed' }, function (r) {
          if (chrome.runtime.lastError || !r || !r.ok || !r.text) { resolve(null); return; }
          resolve(r.text);
        });
      } catch (e) { resolve(null); }
    });
  }
  async function startDsaBridge(el) {
    if (seeding) return;
    seeding = true;
    try {
      setStatus('fetching the DSA seed...');
      var seed = await fetchSeed();
      if (!seed) { stopHold = true; setStatus(L.SEED_DOWN_TEXT); return; }
      setInput(el, seed);
      await sleep(400);
      lastSend = Date.now();
      pressEnter(el);
      var landed = false;
      for (var i = 0; i < 8 && !landed; i++) { await sleep(250); landed = L.postLanded(liveInput(el), nowInput()); }
      if (!landed) {
        clickSend(el);
        for (var j = 0; j < 12 && !landed; j++) { await sleep(250); landed = L.postLanded(liveInput(el), nowInput()); }
      }
      setStatus(landed ? 'DSA seed sent' : 'DSA seed not posted: the chat input did not clear (press Enter once)');
    } finally { seeding = false; }
  }
  function triggerTarget(e) {
    var t = e.target;
    if (!t || !t.matches || isOurs(t)) return null;
    var inp = findInput();
    if (!inp || !L.isStartTrigger(inputText(inp))) return null;
    if (e.type === 'keydown') return (e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.isTrusted && t === inp) ? inp : null;
    var box = inp; for (var u = 0; u < 4 && box.parentElement; u++) box = box.parentElement;
    return (e.isTrusted && t.closest && t.closest('button, [role="button"]') && box.contains(t)) ? inp : null;
  }
  function onTriggerEvent(e) {
    var inp = triggerTarget(e);
    if (!inp) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (e.type === 'keydown') startDsaBridge(inp);
    else if (e.type === 'click') startDsaBridge(inp);
  }
  document.addEventListener('keydown', onTriggerEvent, true);
  document.addEventListener('click', onTriggerEvent, true);

  document.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey && e.target && e.target.matches && e.target.matches('textarea, [contenteditable], [role="textbox"]') && !isOurs(e.target)) lastSend = Date.now(); }, true);

  chrome.storage.local.get(['aibridge_quiet_ms', 'aibridge_max_chars', 'aibridge_cap', 'aibridge_wait_ms', 'aibridge_max_blocks'], function (r) {
    ['aibridge_quiet_ms', 'aibridge_max_chars', 'aibridge_cap', 'aibridge_wait_ms', 'aibridge_max_blocks'].forEach(function (k) { if (r[k]) CFG[k] = r[k]; });
    autoRun = false;   // off after a reload; the operator turns it on per chat. State is per page: other chats are never touched.
    buildUi();
    scan();                 // baseline: everything already on the page is history
    baseline = false;
    obs.observe(document.body || document.documentElement, { childList: true, subtree: true, characterData: true });
    connectTick();
    startWorkerTick();
    preflight('');
  });
  window.__aibDebug = function () { return { ver: VER, tab: tabId, autoRun: autoRun, runs: runs, resultN: resultN, pending: pending.map(function (p) { return { grew: p.grew, len: p.len, connected: p.block.isConnected }; }), quietFor: Date.now() - lastMut, working: working, tickAgo: lastTick ? Date.now() - lastTick : null, hidden: document.hidden, input: (function () { var e = findInput(); return e ? { tag: e.tagName, text: inputText(e).slice(0, 30) } : null; })(), ranKeys: Object.keys(ranKeys).length }; };
  console.log('[AIBridge] content script v' + VER + ' loaded (tab ' + tabId + ')');
})();
