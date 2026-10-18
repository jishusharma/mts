(function () {
  if (window.__aibridgeInstalled) return;
  window.__aibridgeInstalled = true;
  var L = window.AIBridgeLoop;
  var VER = L.VERSION;

  // ---- tunables (override via chrome.storage.local keys of the same name) ----
  var CFG = {
    aibridge_quiet_ms: 2000,    // page text must be unchanged this long = reply finished
    aibridge_max_chars: 60000,  // largest single message we send; see HANDOFF.md for the measured limit
    aibridge_cap: 50,           // blocks run in one chain before auto turns itself off
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
    sampleText(); growCheck(); pump(); watchdog(); labelTick();
  }
  // a page holding a Web Lock is not frozen by Chrome's tab lifecycle while it sits in the background
  try { if (navigator.locks && navigator.locks.request) navigator.locks.request('aibridge-keepalive-' + tabId, function () { return new Promise(function () {}); }); } catch (e) {}

  // text-based quiet: DeepSeek keeps animating, so DOM mutations never settle; visible text length does
  var sigLen = -1, sigAt = Date.now();
  function oursLen() { var n = 0, l = document.querySelectorAll('.aibridge-wrap, .aibridge-ctl'); for (var i = 0; i < l.length; i++) n += (l[i].textContent || '').length; return n; }
  function textQuiet() { return Date.now() - sigAt; }
  function sampleText() { var n = ((document.body && document.body.textContent) || '').length - oursLen(); if (n !== sigLen) { sigLen = n; sigAt = Date.now(); } }
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
  function isMarkerFirst(text) { return firstNonEmptyLine(text).indexOf('# AIRUN') === 0; }
  function stripMarker(s) { return L.stripMarker(s); }
  function findBlock(el) {
    var best = el;
    var cur = el.parentElement;
    while (cur && cur !== document.body) {
      if (!isMarkerFirst(cur.textContent || '')) break;
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
    return out;
  }
  function blockCmd(block) { return stripMarker(btext(block)).trim(); }
  function blockKey(block) {
    // fnv(cmd) + occurrence number among blocks with the same command: stable when other blocks shift the index
    var list = allBlocks();
    var h = L.fnv(blockCmd(block)), occ = 0;
    for (var i = 0; i < list.length && list[i] !== block; i++) {
      if (L.fnv(blockCmd(list[i])) === h) occ++;
    }
    return h + '@' + occ;
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
    if (!resp || !resp.ok || resp.status !== 200) return resp && resp.status === 403 ? 'refused' : 'bridge error';
    var b = resp.body || {};
    if (b.timed_out) return 'timed out';
    if (b.exit !== 0 && b.kind !== 'read') return 'exit ' + b.exit;
    return null;
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
      var bs = cur.querySelectorAll('button, [role="button"]');
      for (var i = bs.length - 1; i >= 0; i--) {
        var b = bs[i];
        if (isOurs(b) || b.getAttribute('aria-disabled') === 'true' || b.disabled) continue;
        b.click();
        return true;
      }
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
  async function postToChat(text, myToken) {
    var t0 = Date.now();
    while (true) {
      if (myToken !== token) return false;
      if (Date.now() - t0 > CFG.aibridge_wait_ms) { lastPostErr = 'the chat never became idle (or an operator draft sits in the input)'; return false; }
      var el = findInput();
      var idle = textQuiet() >= CFG.aibridge_quiet_ms;
      if (el && idle && inputText(el) === '') break;   // never overwrite an operator draft
      await sleep(400);
    }
    var el2 = findInput();
    setInput(el2, text);
    await sleep(400);
    lastSend = Date.now();
    pressEnter(el2);
    // DeepSeek can replace the input node after a send: judge by the chat's current input, not only the node we typed into
    for (var i = 0; i < 8; i++) { await sleep(250); if (L.postLanded(liveInput(el2), nowInput())) return true; }
    clickSend(el2);
    for (var j = 0; j < 12; j++) { await sleep(250); if (L.postLanded(liveInput(el2), nowInput())) return true; }
    lastPostErr = 'the chat input did not clear after sending';
    return false;
  }

  // ---- auto loop ----
  function setStatus(s) { if (ui.status) ui.status.textContent = s; }
  function refreshUi() {
    if (!ui.box) return;
    ui.cb.checked = autoRun;
    ui.count.textContent = runs + '/' + CFG.aibridge_cap;
    ui.box.className = 'aibridge-ctl' + (autoRun ? ' on' : '');
  }
  function stopAuto(why) {
    autoRun = false; stopHold = true; token++; pending = [];
    setStatus(why || 'stopped');
    refreshUi();
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
    if (prefix) setStatus(prefix + ' ' + line);
    return line;
  }

  // Run every unrun block of the finished reply, in order; post ONE message with a receipt for each block.
  async function runBatch(trigger) {
    var myToken = token;
    var blocks = allBlocks().filter(function (b) { return !ranKeys[blockKey(b)]; });
    if (!blocks.length && trigger && !ranKeys[blockKey(trigger)]) blocks = [trigger];
    if (!blocks.length) return;
    if (runs >= CFG.aibridge_cap) { stopAuto('auto OFF at the cap: ' + CFG.aibridge_cap + ' blocks ran in this chain. Tick the box again to continue (the counter restarts).'); return; }
    // mark first: a block is never run twice, and anything that appears while we run belongs to the next reply
    var items = blocks.map(function (b) { var o = L.parseMarker(btext(b)); return { block: b, cmd: blockCmd(b), opts: o, shown: o.task ? 'TASK ' + o.task + ' ' + JSON.stringify(o.params || {}) + (o.task === 'inline' ? ' plan=' + L.cmdPreview(blockCmd(b), 300) : '') : null }; });
    items.forEach(function (it) { ranKeys[blockKey(it.block)] = true; });
    pending = [];
    var seenN = items.length, cap = CFG.aibridge_max_blocks, ran = 0, stop = null;
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      resultN++; it.n = resultN; it.rid = newRid(); it.index = i + 1;
      if (i >= cap) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: over the per-reply cap of ' + cap + ' blocks. Send it in your next reply.' }; continue; }
      if (stop) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: block ' + stop.idx + ' ended with ' + stop.why + ' and this block may depend on it. Re-send it if it should still run.' }; continue; }
      if (!it.cmd && !it.opts.task) { it.resp = { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: the block has no command after the # AIRUN line.' }; continue; }
      runs++; refreshUi();
      setStatus('running #' + it.n + (seenN > 1 ? ' (block ' + (i + 1) + '/' + seenN + ')' : '') + ': ' + it.cmd.split('\n')[0].slice(0, 60));
      var resp = vet(it.rid, it.cmd, await callWithRetry(it.cmd, it.opts, true, it.rid), !!it.opts.task);
      it.resp = resp; ran++;
      if (it.block.__aibPanel) { it.block.__aibPanel.style.display = 'block'; it.block.__aibPanel.textContent = '[auto #' + it.n + ']\n' + panelText(resp); }
      if (myToken !== token) return;
      var why = failed(resp);
      if (why) stop = { idx: i + 1, why: why };
    }
    var texts = items.map(function (it) {
      return L.formatResult(it.n, it.shown || it.cmd, it.resp, '', { blocks_seen: seenN, blocks_run: ran, index: it.index, rid: it.rid });
    });
    var text = (seenN > 1 ? '[AIRUN BATCH] blocks_seen=' + seenN + ' blocks_run=' + ran + ' not_run=' + (seenN - ran) + '\n' : '') + texts.join('\n\n');
    var lastN = items[items.length - 1].n;
    var ok = await postParts(text, lastN, myToken, '#' + lastN);
    if (!ok) { if (myToken === token) stopAuto('auto OFF: the result was not posted (' + lastPostErr + '). Tick the box again to re-arm.'); return; }
    setStatus('waiting for DSA after #' + lastN);
    // DSA's reply to our result: if it contains no new block it has finished, so hand control back
    var t1 = lastMut;
    for (var w2 = 0; w2 < 100 && lastMut === t1; w2++) await sleep(300);
    if (myToken !== token) return;
    await waitQuiet(myToken, CFG.aibridge_wait_ms);   // on timeout still rescan: never leave a finished reply unread
    if (myToken !== token) return;
    scan(); await sleep(600);
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
        if (textQuiet() < CFG.aibridge_quiet_ms) { await sleep(500); continue; }
        pending.shift();
        await runBatch(item.block);
      }
    } finally { working = false; }
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
    var unrun = allBlocks().filter(function (b) { return !ranKeys[blockKey(b)]; });
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
  setInterval(watchdog, 2000);
  setInterval(linkCheck, 1000);
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
    st.textContent = '.aibridge-ctl{position:fixed;right:12px;bottom:12px;z-index:2147483647;background:#1b1b1b;color:#ddd;' +
      'font:12px/1.4 sans-serif;padding:8px 10px;border-radius:8px;border:1px solid #444;max-width:320px}' +
      '.aibridge-ctl.on{border-color:#2e9e4f}.aibridge-ctl button{margin-left:6px;font-size:12px;cursor:pointer}' +
      '.aibridge-ctl .st{margin-top:4px;color:#9ab;word-break:break-word}.aibridge-ctl .in{margin-top:2px;color:#798;font-size:11px;word-break:break-word}';
    document.head.appendChild(st);
    var box = document.createElement('div');
    box.className = 'aibridge-ctl';
    var lab = document.createElement('label');
    var cb = document.createElement('input');
    cb.type = 'checkbox';
    lab.appendChild(cb);
    lab.appendChild(document.createTextNode(' Hands-free: DSA runs every AIRUN block on its own '));
    var count = document.createElement('span');
    var status = document.createElement('div'); status.className = 'st'; status.textContent = 'off: click Run on each block';
    var info = document.createElement('div'); info.className = 'in'; info.textContent = 'AIBridge ' + VER + ' (this chat only)';
    var link = document.createElement('span'); link.textContent = '\u25CB'; link.title = 'link: starting'; link.style.marginLeft = '6px'; link.style.cursor = 'help';
    box.appendChild(lab); box.appendChild(count); box.appendChild(link); box.appendChild(status); box.appendChild(info);
    document.body.appendChild(box);
    ui = { box: box, cb: cb, count: count, status: status, info: info, link: link };
    cb.addEventListener('change', function () {
      autoRun = cb.checked;
      if (autoRun) { runs = 0; stopHold = false; preflight('on:'); } else stopAuto('off: click Run on each block');
      refreshUi();
    });
    refreshUi();
  }

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
