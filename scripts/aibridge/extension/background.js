const AGENT_URL = 'http://127.0.0.1:7181/run';
const AGENT_CWD = 'F:\\AIBridge';
const TOKEN = '__TOKEN__';
// Other machines: chrome.storage.local aibridge_machines = {"NUC": {"url": "http://127.0.0.1:7182/run", "token": "...", "cwd": "..."}}
// reached through a loopback tunnel (ssh -L 7182:127.0.0.1:7181 host); the agent itself stays loopback-only.
function pickMachine(host) {
  return new Promise(res => {
    if (!host) { res({ url: AGENT_URL, token: TOKEN, cwd: AGENT_CWD }); return; }
    chrome.storage.local.get(['aibridge_machines'], r => {
      const m = (r.aibridge_machines || {})[host];
      res(m && m.url && m.token ? { url: m.url, token: m.token, cwd: m.cwd || AGENT_CWD } : null);
    });
  });
}

// Heartbeat for pages. A background or unfocused tab throttles its own timers (1/s, then 1/min after 5 minutes), which
// is why parallel chats stalled when their window lost focus. Messages from this worker are not throttled, so each chat
// page connects a port and gets a tick every 500 ms for as long as it is open. An open port also keeps this worker alive.
const ports = new Set();
let tickTimer = null;
chrome.runtime.onConnect.addListener(port => {
  if (port.name !== 'aibridge-tick') return;
  ports.add(port);
  // exempt this chat tab from Memory Saver / automatic discarding (a discarded tab loses the content script entirely)
  try { if (port.sender && port.sender.tab) chrome.tabs.update(port.sender.tab.id, { autoDiscardable: false }); } catch (e) {}
  port.onDisconnect.addListener(() => {
    ports.delete(port);
    if (!ports.size && tickTimer) { clearInterval(tickTimer); tickTimer = null; }
  });
  if (!tickTimer) {
    tickTimer = setInterval(() => {
      const t = Date.now();
      ports.forEach(p => { try { p.postMessage({ t: t }); } catch (e) { ports.delete(p); } });
    }, 500);
  }
});

// 0.7.12 version drift: loaded = this worker's manifest, disk = manifest.json read from disk now (unpacked extension);
// 'reload' re-reads the extension from disk (the page then re-attaches itself, see content.js orphan reload).
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.type === 'version') {
    const loaded = chrome.runtime.getManifest().version;
    fetch(chrome.runtime.getURL('manifest.json'), { cache: 'no-store' }).then(r => r.json())
      .then(m => sendResponse({ loaded: loaded, disk: m.version }), () => sendResponse({ loaded: loaded, disk: null }));
    return true;
  }
  if (msg && msg.type === 'reload') { sendResponse({ ok: true }); setTimeout(() => chrome.runtime.reload(), 200); return; }
  if (msg && msg.type === 'seed') {
    // 0.7.30: the "Start DSA bridge" seed. The token stays here in the worker; the page only gets the text back.
    pickMachine(msg.host).then(mc => {
      if (!mc) return { ok: false, status: 0, text: '' };
      return fetch(mc.url.replace(/\/run$/, '/seed'), { method: 'POST', cache: 'no-store', headers: { 'X-AIBridge-Token': mc.token } })
        .then(r => r.text().then(t => ({ ok: r.status === 200, status: r.status, text: t })));
    })
    .then(x => sendResponse(x), e => sendResponse({ ok: false, status: 0, text: '', error: String(e) }));
    return true;
  }
  if (!msg || (msg.type !== 'airun' && msg.type !== 'ping')) return;
  const keepAlive = setInterval(chrome.runtime.getPlatformInfo, 25000);
  pickMachine(msg.host).then(mc => {
    if (!mc) return { status: 0, text: JSON.stringify({ error: 'unknown host', reason: 'host=' + msg.host + ' not in aibridge_machines' }) };
    if (msg.type === 'ping') {
      return fetch(mc.url.replace(/\/run$/, '/ping'), { method: 'GET', cache: 'no-store' }).then(r => r.text().then(t => ({ status: r.status, text: t })));
    }
    return fetch(mc.url, {
      method: 'POST',
      cache: 'no-store',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify({ cmd: msg.cmd, cwd: msg.cwd || mc.cwd, timeout_s: msg.timeout_s || undefined, auto: msg.auto ? true : undefined, write: msg.write ? true : undefined, rid: msg.rid || undefined, event: msg.event || undefined, dry: msg.dry ? true : undefined, shell: msg.shell || undefined, task: msg.task || undefined, task_params: msg.task_params || undefined, task_spec: msg.task_spec || undefined, token: mc.token })
    }).then(r => r.text().then(t => ({ status: r.status, text: t })));
  })
  .then(x => {
    let body = null;
    try { body = JSON.parse(x.text); } catch (e) { body = { raw: x.text }; }
    sendResponse({ ok: true, status: x.status, body: body });
  })
  // a rejected fetch means nothing answered at the port: the agent is down (the extension itself is clearly alive)
  .catch(e => sendResponse({ ok: false, cls: 'agent_unreachable', error: String(e) }))
  .finally(() => clearInterval(keepAlive));
  return true;
});
