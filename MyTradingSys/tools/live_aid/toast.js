// Live Aid toast (card level-touch-alerts-session-brief-1109): the newest LEVEL TOUCH / SESSION BRIEF from the live alert loop.
// Data: window.LIVE_TOASTS = [{t, event, text}] from ../../runtime/live_aid_toasts.js (written by live_level_touch.py). Alerts only.
// Shows toasts from the last 6 h (OURS), newest first, max 3 (ALERT_DOCK_SPEC: capped stack); the script tag is reloaded every 30 s.
(function (root) {
  var WINDOW_MS = 6 * 3600 * 1000, MAX = 3;
  function pick(list, now) {
    return (list || []).filter(function (r) { return r && typeof r.t === 'number' && now - r.t <= WINDOW_MS && now - r.t > -60000; })
      .sort(function (a, b) { return b.t - a.t; }).slice(0, MAX);
  }
  function html(rows) {
    return rows.map(function (r) {
      var esc = String(r.text || '').replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; });
      return '<div class="toast" role="status">' + esc + '</div>';
    }).join('');
  }
  var api = { pick: pick, html: html };
  if (typeof module !== 'undefined') module.exports = api;
  root.LIVE_TOAST = api;
  if (typeof document === 'undefined') return;
  function draw() {
    var el = document.getElementById('live-toasts');
    if (!el) {
      el = document.createElement('div'); el.id = 'live-toasts';
      el.style.cssText = 'position:fixed;right:12px;bottom:12px;max-width:min(560px,calc(100vw - 24px));display:grid;gap:6px;z-index:50;pointer-events:none';
      document.body.appendChild(el);
    }
    el.innerHTML = html(pick(root.LIVE_TOASTS, Date.now()));
    Array.prototype.forEach.call(el.children, function (c) {
      c.style.cssText = 'background:#141920;border:1px solid #e0a43a;border-radius:6px;padding:8px 12px;font:13px/1.35 ui-monospace,Consolas,monospace;color:#e3e8ee';
    });
  }
  function reload() {
    var s = document.createElement('script'); s.src = '../../runtime/live_aid_toasts.js?' + Date.now();
    s.onload = function () { draw(); s.remove(); }; s.onerror = function () { s.remove(); };
    document.head.appendChild(s);
  }
  draw(); setInterval(reload, 30000);
}(typeof window !== 'undefined' ? window : globalThis));
