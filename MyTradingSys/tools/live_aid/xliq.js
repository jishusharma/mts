/* Live Aid cross-exchange liquidation row (card live-aid-xliq-1113). Reads window.LIVEAID_XLIQ, written by xliq_collector.py
   into this folder (the page server's root, so a relative URL resolves). One table row per venue: 15 m forced-selling sum (USD
   notional, long vs short side), BIG when a 15 m print is above that venue's 7-day p99, else 'baseline building' (never faked).
   Pure rules (node-testable) first; the DOM part only runs in a browser. Context, never a signal: label rule OURS. */
(function () {
  'use strict';
  var NAMES = { BYBIT: 'Bybit', BINANCE: 'Binance', OKX: 'OKX' };
  var STALE_MS = 90000;   // OURS: the collector writes every 15 s; older than 90 s = not running

  function usd(x) {
    if (x == null) return '-';
    if (x >= 1e6) return '$' + (x / 1e6).toFixed(2) + 'M';
    if (x >= 1e3) return '$' + Math.round(x / 1e3) + 'k';
    return '$' + Math.round(x);
  }
  function pxLabel(p) { var r = Math.round(p); return Math.floor(r / 1000) + ',' + Math.floor((r % 1000) / 100) + 'xx'; }
  function usSession(now) { var h = new Date(now).getUTCHours(); return h >= 13 && h < 21; }

  /* feed + now -> [{venue, name, state, long15, short15, n15, max15, big, bigNote, ...}] */
  function rows(feed, now) {
    var fresh = !!(feed && feed.t && now - feed.t <= STALE_MS);
    return Object.keys(NAMES).map(function (v) {
      var s = feed && feed.venues && feed.venues[v], r = { venue: v, name: NAMES[v] };
      if (!feed) { r.state = 'nofeed'; r.note = 'xliq_feed.js not loaded (start xliq_collector.py)'; return r; }
      if (!fresh) { r.state = 'stale'; r.note = 'collector stale (feed older than 90 s)'; return r; }
      if (!s) { r.state = 'nofeed'; r.note = 'venue not in feed'; return r; }
      if (s.err && !s.n15 && !s.n7d) { r.state = 'err'; r.note = s.err; return r; }
      r.state = 'ok'; r.long15 = s.long15; r.short15 = s.short15; r.n15 = s.n15; r.max15 = s.max15; r.err = s.err || '';
      r.baseline = s.baseline; r.have_days = s.have_days; r.p99 = s.p99; r.big = s.baseline === 'ready' ? s.big : 0;
      r.bigside = r.big ? s.bigside : null; r.bigpx = r.big ? s.bigpx : null;
      r.bigNote = s.baseline === 'ready' ? (s.big ? 'BIG x' + s.big : 'no (p99 ' + usd(s.p99) + ')')
        : 'baseline building (' + (s.have_days || 0).toFixed(1) + ' of 7 d, ' + (s.n7d || 0) + ' prints)';
      return r;
    });
  }

  /* One 'So what:' line. long/short/wait wording, label rule OURS. */
  function soWhat(feed, now) {
    var rs = rows(feed, now), us = usSession(now) ? ' (US session)' : '';
    var live = rs.filter(function (r) { return r.state === 'ok'; });
    if (!live.length) return 'So what: no liquidation data (' + (rs[0] && rs[0].note || 'collector not running') + '). Read: WAIT.';
    var longs = live.filter(function (r) { return r.big && r.bigside === 'long'; });
    var shorts = live.filter(function (r) { return r.big && r.bigside === 'short'; });
    function names(a) { return a.map(function (r) { return r.name; }).join('+'); }
    function px(a) { var p = a.filter(function (r) { return r.bigpx; }).map(function (r) { return r.bigpx; }); return p.length ? ' at ' + pxLabel(p.reduce(function (x, y) { return x + y; }, 0) / p.length) : ''; }
    if (longs.length && shorts.length) return 'So what: big liquidations on both sides (long on ' + names(longs) + ', short on ' + names(shorts) + ')' + us + ' = whipsaw. Read: WAIT.';
    if (longs.length) return 'So what: big long liquidations on ' + names(longs) + px(longs) + us + ' = forced selling, watch for absorption. Read: WAIT for the flush to be absorbed, then long only.';
    if (shorts.length) return 'So what: big short liquidations on ' + names(shorts) + px(shorts) + us + ' = forced buying (squeeze), do not chase. Read: WAIT for exhaustion, then short only.';
    var building = live.filter(function (r) { return r.baseline !== 'ready'; });
    if (building.length) return 'So what: nothing can be marked BIG yet (baseline building on ' + names(building) + '); read the 15 m sums as raw size only' + us + '. Read: WAIT.';
    return 'So what: no unusually large liquidations in the last 15 m' + us + '. Read: WAIT.';
  }

  var api = { rows: rows, soWhat: soWhat, usd: usd, pxLabel: pxLabel, usSession: usSession, STALE_MS: STALE_MS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  window.LiveAidXliq = api;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function render() {
    var body = document.getElementById('xl-rows'), sw = document.getElementById('xl-sowhat');
    if (!body) return;
    var now = Date.now(), feed = window.LIVEAID_XLIQ || null;
    body.innerHTML = rows(feed, now).map(function (r) {
      if (r.state !== 'ok') return '<tr><td>' + esc(r.name) + '</td><td colspan="5" class="dim">' + esc(r.note) + '</td></tr>';
      return '<tr><td>' + esc(r.name) + '</td><td>' + usd(r.long15) + '</td><td>' + usd(r.short15) + '</td><td>' + r.n15 + '</td><td>' + usd(r.max15) +
        '</td><td>' + (r.big ? '<b>' + esc(r.bigNote) + '</b>' : esc(r.bigNote)) + (r.err ? ' <span class="dim">(' + esc(r.err) + ')</span>' : '') + '</td></tr>';
    }).join('');
    if (sw) sw.textContent = soWhat(feed, now);
  }
  function load() {
    var s = document.createElement('script');
    s.src = 'xliq_feed.js?_=' + Date.now();
    s.onload = function () { render(); s.remove(); };
    s.onerror = function () { window.LIVEAID_XLIQ = null; render(); s.remove(); };
    document.head.appendChild(s);
  }
  load(); setInterval(load, 30000);
})();
