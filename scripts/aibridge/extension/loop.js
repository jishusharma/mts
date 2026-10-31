// loop.js - pure helpers for the auto-loop. No DOM, no chrome.* so node can test them.
(function (root) {
  var L = {};
  L.VERSION = '0.7.4';

  L.fnv = function (s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h.toString(16);
  };

  // One line of the command for a result header. Newlines shown as " ; ", capped at max chars (was 160 / first line only).
  L.cmdPreview = function (cmd, max) {
    var s = String(cmd).replace(/\r/g, '').split('\n').filter(function (x) { return x.trim() !== ''; }).join(' ; ');
    max = max || 600;
    return s.length > max ? s.slice(0, max) + ' ...[+' + (s.length - max) + ' chars]' : s;
  };

  // Header + body of one result. n = result number. resp = {ok,status,body,error,cls}.
  // meta = {blocks_seen, blocks_run, index, rid}. Every result says which block it answers (rid, lines, sha, host, time)
  // so a result can never be mistaken for another block's (B3/B4/A4).
  L.formatResult = function (n, cmdText, resp, extraNote, meta) {
    meta = meta || {};
    var tag = '[AIRUN RESULT #' + n + ']';
    var lines = [];
    var b = (resp && resp.body) || {};
    var id = '';
    if (resp && resp.ok && b) {
      id = ' host=' + (b.host || '?') + ' agent=' + (b.agent || '?') + ' kind=' + (b.kind || '?') +
        ' lines=' + (b.cmd_lines != null ? b.cmd_lines : '?') + ' sha=' + (b.cmd_sha || '?') + ' rid=' + (b.rid || meta.rid || '?');
    }
    var blk = (meta.blocks_seen != null) ? ' block=' + (meta.index || 1) + '/' + meta.blocks_seen + ' blocks_run=' + (meta.blocks_run != null ? meta.blocks_run : '?') : '';
    if (!resp) {
      lines.push(tag + ' ERROR extension_link: no answer from the AIBridge extension (it was reloaded or disabled, or this page needs F5). The agent was not asked.' + blk);
    } else if (!resp.ok) {
      var cls = resp.cls || 'error';
      if (cls === 'NOT_RUN') {
        lines.push(tag + ' ' + resp.error + blk);
      } else if (cls === 'agent_unreachable') {
        lines.push(tag + ' ERROR agent_unreachable: the extension is alive but nothing answers on the agent port (agent not running). Start it with F:\\AIBridge\\scripts\\start-agent.ps1.' + blk);
      } else {
        lines.push(tag + ' ERROR ' + cls + ': ' + resp.error + blk);
      }
    } else if (resp.status !== 200) {
      lines.push(tag + ' REFUSED http=' + resp.status + ' reason=' + (b.reason || b.error || JSON.stringify(b)) + id + blk);
    } else {
      lines.push(tag + ' exit=' + b.exit + ' ms=' + b.ms + ' timed_out=' + !!b.timed_out +
        ' out_truncated=' + !!b.out_truncated + ' out_bytes=' + b.out_bytes + ' timeout_s=' + b.timeout_s + id + blk);
    }
    lines.push('cmd: ' + L.cmdPreview(cmdText, 600));
    if (b && b.at) lines.push('ran_at: ' + b.at);
    if (extraNote) lines.push('note: ' + extraNote);
    if (resp && resp.ok && resp.status === 200) {
      lines.push('--- stdout ---');
      lines.push(b.out || '');
      if (b.err) { lines.push('--- stderr ---'); lines.push(b.err); }
    }
    lines.push('[END AIRUN RESULT #' + n + ']');
    return lines.join('\n');
  };

  // Does the reply the agent saw match the block we sent? (rid echoed, same line count). null = fine, else a problem text.
  L.checkEcho = function (rid, cmd, resp, isTask) {
    if (!resp || !resp.ok || !resp.body) return null;
    var b = resp.body;
    if (b.rid !== undefined && b.rid !== '' && rid && b.rid !== rid) return 'STALE_REPLY: asked rid=' + rid + ' but the agent answered rid=' + b.rid + '; result discarded';
    if (isTask) return null;   // the agent runs the playbook runner, not the block text
    var want = String(cmd).split('\n').length;
    if (b.cmd_lines != null && b.cmd_lines !== want) return 'LINE_MISMATCH: the extension sent ' + want + ' line(s) but the agent received ' + b.cmd_lines;
    return null;
  };

  // Split into parts of at most max characters, cut on line boundaries when possible.
  // A single part is returned unchanged. Each part gets a header so DSA can tell order.
  L.splitParts = function (text, n, max) {
    if (text.length <= max) return [text];
    var body = max - 160; // room for the part header
    if (body < 1000) body = 1000;
    var parts = [], i = 0;
    while (i < text.length) {
      var end = Math.min(i + body, text.length);
      if (end < text.length) {
        var nl = text.lastIndexOf('\n', end);
        if (nl > i + body * 0.5) end = nl + 1;
      }
      parts.push(text.slice(i, end));
      i = end;
    }
    var k = parts.length;
    return parts.map(function (p, idx) {
      var head = '[AIRUN RESULT #' + n + ' part ' + (idx + 1) + '/' + k + ']' +
        (idx < k - 1 ? ' more parts follow; reply only "ok" and do not run anything until the last part' : ' last part; continue') + '\n';
      return head + p;
    });
  };

  L.parseMarker = function (s) {
    var m = /# AIRUN([^\n]*)/.exec(s || '');
    var o = {};
    if (!m) return o;
    var cw = /cwd=("([^"]+)"|(\S+))/.exec(m[1]);
    if (cw) o.cwd = cw[2] || cw[3];
    var ho = /host=([A-Za-z0-9_.-]+)/.exec(m[1]);
    if (ho) o.host = ho[1];
    var to = /timeout=(\d+)/.exec(m[1]);
    if (to) o.timeout_s = parseInt(to[1], 10);
    var sh = /shell=(pwsh|powershell)/.exec(m[1]);
    if (sh) o.shell = sh[1];
    // task mode: "# AIRUN task=<playbook> key=value ..." runs a whole playbook in one call; task=inline takes a JSON plan from the body
    var tk = /(?:^|\s)task=([A-Za-z0-9_.-]+)/.exec(m[1]);
    if (tk) {
      o.task = tk[1];
      o.params = {};
      var re = /(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=("([^"]*)"|\S+)/g, mm;
      while ((mm = re.exec(m[1])) !== null) {
        if (['cwd', 'timeout', 'host', 'shell', 'task'].indexOf(mm[1]) >= 0) continue;
        o.params[mm[1]] = mm[3] !== undefined ? mm[3] : mm[2];
      }
    }
    return o;
  };

  // Text of a code block with its line breaks intact. innerText follows the rendered layout (line wrappers, <br>,
  // display:block spans); textContent can fuse lines. Take whichever kept more line breaks. el may be any object
  // with innerText / textContent.
  L.blockText = function (el) {
    if (!el) return '';
    var a = typeof el.innerText === 'string' ? el.innerText : '';
    var b = typeof el.textContent === 'string' ? el.textContent : '';
    var na = (a.match(/\n/g) || []).length, nb = (b.match(/\n/g) || []).length;
    var t = na > nb ? a : b;
    if (na === nb && a.length > b.length) t = a;
    return t.replace(/\r\n?/g, '\n').replace(/\u00a0/g, ' ');
  };

  // The command: everything after the "# AIRUN ..." line.
  L.stripMarker = function (s) { return s.replace(/^[\s\S]*?# AIRUN[^\n]*\n?/, ''); };

  // Link health of the background heartbeat. Two independent sources tick the page: the service-worker port (t.port) and
  // a dedicated Worker timer (t.worker, not subject to the main thread's background throttling). Times are ms epoch, 0 =
  // never. ok: a port tick is fresh. degraded: only the worker ticks (service worker asleep or port dropped): the loop
  // still runs, reconnect the port. stale: neither ticked for staleMs: the page is frozen or throttled, reconnect and say so.
  L.linkState = function (now, t, staleMs) {
    staleMs = staleMs || 5000;
    var pa = t && t.port ? now - t.port : Infinity, wa = t && t.worker ? now - t.worker : Infinity;
    var state = pa < 3000 ? 'ok' : (wa < 3000 ? 'degraded' : (Math.min(pa, wa) < staleMs ? 'ok' : 'stale'));
    return { state: state, portAge: pa, workerAge: wa, reconnect: state !== 'ok' };
  };
  // reconnect attempts are spaced: first at once, then 1 s, 2 s, 4 s ... capped at 15 s; a good tick resets the counter
  L.reconnectDelay = function (attempt) { return attempt <= 0 ? 0 : Math.min(15000, 1000 * Math.pow(2, attempt - 1)); };
  // text for the panel
  L.linkLabel = function (ls, hidden) {
    var a = function (x) { return isFinite(x) ? (x / 1000).toFixed(1) + 's' : 'never'; };
    return 'link ' + ls.state + (hidden ? ' (tab hidden)' : '') + ' port ' + a(ls.portAge) + ' worker ' + a(ls.workerAge);
  };

  // after Enter, did the message leave the chat input? before: {node, attached, text} of the input the message was typed
  // into; now: {node, text} of the chat's current input, or null. DeepSeek can replace the input node after a send, so a
  // detached node that still holds our text says nothing: a different, empty input means the send went through.
  L.postLanded = function (before, now) {
    if (!now || now.text !== '') return false;
    return !before || !before.attached || before.node !== now.node || before.text === '';
  };

  // B196: may the result be posted now? An operator draft in the input never blocks a post (the draft is saved and put back
  // after the send); only a chat that stays busy past maxMs stops hands-free (fail closed). Anything unreadable = busy.
  L.postGate = function (o) {
    if (!o) return 'stop_busy';
    if (o.idle) return 'send_keep_draft';
    return o.waitedMs > o.maxMs ? 'stop_busy' : 'wait';
  };
  // visible banner text for every auto-off (shown in the page next to the chat, not sent as a message)
  L.stopNotice = function (why) {
    return 'AIBridge hands-free is OFF: ' + (why || 'stopped') + ' Tick the box to re-arm.';
  };

  // B210: a run whose completion frame is lost leaves the panel on "running #N" forever. The run lock expires at twice the
  // block timeout (default timeout 120 s, floor 30 s); on expiry the lock is released with a visible reason and the next
  // block gets a receipt. expireMs(timeout_s) -> ms. expireText(waitedMs, agentRunning) -> the visible reason.
  L.expireMs = function (timeoutS) {
    var t = (timeoutS && timeoutS > 0) ? timeoutS : 120;
    return Math.max(30, t) * 2 * 1000;
  };
  L.expireText = function (waitedMs, agentRunning) {
    var s = Math.round(waitedMs / 1000);
    return 'run lock released after ' + s + ' s: no completion arrived' +
      (agentRunning === 0 ? ' and the agent reports running 0, so nothing was running' :
       (agentRunning == null ? ' and the agent queue could not be read' : ' and the agent still reports running ' + agentRunning + '; the command may still be executing')) +
      '. Re-send the block; if blocks keep returning nothing: Hands-free off then on, reload the extension, F5.';
  };
  // Resolve with p's value, or with an explicit lock-expired response after ms. onExpire(waitedMs) may return a promise of
  // the agent's running count (0 = idle, null = unknown); it never blocks the release for more than 5 s.
  L.raceDeadline = function (p, ms, onExpire) {
    return new Promise(function (resolve) {
      var done = false, t0 = Date.now();
      var timer = setTimeout(function () {
        if (done) return; done = true;
        var waited = Date.now() - t0, finish = function (running) {
          resolve({ ok: false, cls: 'LOCK_EXPIRED', error: L.expireText(waited, running) });
        };
        var q; try { q = onExpire ? onExpire(waited) : null; } catch (e) { q = null; }
        if (!q || !q.then) { finish(q == null ? null : q); return; }
        var fin = false, g = function (v) { if (!fin) { fin = true; finish(v == null ? null : v); } };
        setTimeout(function () { g(null); }, 5000);
        q.then(g, function () { g(null); });
      }, ms);
      p.then(function (v) { if (!done) { done = true; clearTimeout(timer); resolve(v); } },
             function (e) { if (!done) { done = true; clearTimeout(timer); resolve({ ok: false, cls: 'extension_link', error: String(e) }); } });
    });
  };

  // ---- block selection (pure; content.js describes each candidate block, this decides) ----
  // desc = {cmd, chain, nested}; chain = ancestors as {tag, cls, role, lead} (lead = first 40 chars of its own text).
  // A block inside DeepSeek's thinking panel is a draft, never an instruction. Identified by structure (tag / class / role),
  // never by the block text. FAIL CLOSED: a collapsible container (details) or a chain the page could not describe is
  // treated as thinking, so an unknown layout runs nothing instead of running drafts.
  var THINK_CLS = /think|thought|reason|cot[-_ ]|chain[-_ ]?of/i;
  L.isThinking = function (chain) {
    if (!chain || !chain.length) return true;   // cannot describe where the block sits = unknown = not runnable
    for (var i = 0; i < chain.length; i++) {
      var c = chain[i] || {}, tag = String(c.tag || '').toLowerCase();
      if (tag === 'thought' || tag === 'thinking' || tag === 'details' || tag === 'summary') return true;
      if (THINK_CLS.test(String(c.cls || '')) || THINK_CLS.test(String(c.role || ''))) return true;
      if (/^\s*(thought for|thinking|deep ?think)/i.test(String(c.lead || '')) && tag !== 'body') return true;
    }
    return false;
  };
  // -> {selected: [index...], ignored: [index...], status: text or ''}
  L.selectBlocks = function (descs) {
    var sel = [], ign = [];
    (descs || []).forEach(function (d, i) { (L.isThinking(d && d.chain) ? ign : sel).push(i); });
    return { selected: sel, ignored: ign, status: ign.length ? 'ignored ' + ign.length + ' block(s) inside the thinking panel (only the final answer runs)' : '' };
  };
  // key = fnv(text)@occurrence among the SELECTED blocks with the same text: a thinking draft or a collapsing panel never shifts it
  L.batchKeys = function (texts) {
    var seen = {};
    return (texts || []).map(function (t) { var h = L.fnv(String(t)); var o = seen[h] || 0; seen[h] = o + 1; return h + '@' + o; });
  };
  // per-batch duplicate guard: -> for each block, the 1-based number of an earlier identical block, or 0
  L.dupOf = function (texts) {
    var first = {};
    return (texts || []).map(function (t, i) { var k = String(t).replace(/\r/g, '').trim(); if (first[k] === undefined) { first[k] = i + 1; return 0; } return first[k]; });
  };

  // ---- dropped generation (D4): after a result is posted DSA must answer; if it never does, say so ----
  // state = replyWatch() ; event = {type:'posted'|'reply'|'tick'|'reset', busy: in-flight run or draft being typed}
  // -> {state, action: 'none'|'notice'|'stop'}. One notice per chain, then stop. noticeMs 45 s (OURS) keeps it under 60 s.
  L.REPLY_NOTICE_MS = 45000;
  L.replyWatch = function (state, ev, now, noticeMs) {
    var s = state ? { phase: state.phase, since: state.since, notices: state.notices } : { phase: 'idle', since: 0, notices: 0 };
    ev = ev || {};
    if (ev.type === 'posted') { s.phase = 'waiting'; s.since = now; return { state: s, action: 'none' }; }
    if (ev.type === 'reply') { s.phase = 'idle'; s.notices = 0; return { state: s, action: 'none' }; }
    if (ev.type === 'reset') return { state: { phase: 'idle', since: 0, notices: 0 }, action: 'none' };
    if (s.phase !== 'waiting' || ev.busy) { if (s.phase === 'waiting') s.since = now; return { state: s, action: 'none' }; }
    if (now - s.since < (noticeMs || L.REPLY_NOTICE_MS)) return { state: s, action: 'none' };
    if (s.notices >= 1) { s.phase = 'idle'; return { state: s, action: 'stop' }; }
    s.notices = 1; s.since = now;
    return { state: s, action: 'notice' };
  };
  L.REPLY_NOTICE_TEXT = '[AIRUN NOTICE] your last reply ended without a final answer (your generation dropped after the result). Re-send the blocks of that answer once.';
  // visible status while the page text never settles (spinner text keeps changing)
  L.quietWaitStatus = function (elapsedMs, waitMs) {
    var s = Math.round(elapsedMs / 1000);
    return elapsedMs > waitMs ? 'page text still changing after ' + s + ' s; DSA may be stuck. Untick the box to stop, or wait.' : 'waiting for the reply to settle (' + s + ' s)';
  };

  root.AIBridgeLoop = L;
  if (typeof module !== 'undefined') module.exports = L;
})(typeof window !== 'undefined' ? window : globalThis);
