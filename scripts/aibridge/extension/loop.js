// loop.js - pure helpers for the auto-loop. No DOM, no chrome.* so node can test them.
(function (root) {
  var L = {};
  L.VERSION = '0.7.0';

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

  root.AIBridgeLoop = L;
  if (typeof module !== 'undefined') module.exports = L;
})(typeof window !== 'undefined' ? window : globalThis);
