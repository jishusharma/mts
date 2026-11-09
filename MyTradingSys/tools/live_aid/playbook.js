// Daily session playbook text cards (behind the Detail line of the Map tab; the one-screen picture is map.js). The numbers are computed by daily_playbook.py and
// written to playbook_data.js (window.PLAYBOOK_DATA); this file only shows them. Fail closed: no data reads NOT_IN_DATA, a day
// that has ended or data older than 36 h reads STALE, never a guess. Descriptive only: no orders, no sizing, nothing gates.
(function (root) {
  'use strict';
  var SESSIONS = [['Asia', 0, 8], ['Europe', 7, 13], ['US', 13, 21]];   // UTC hours, same as daily_playbook.py SESSIONS (OURS)
  var STALE_MS = 36 * 3600 * 1000, DAY_MS = 86400000;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n0(x) { return Math.round(x).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function p2(x) { return (x * 100).toFixed(2) + '%'; }
  function nowSessions(ms) {
    var d = new Date(ms), h = d.getUTCHours() + d.getUTCMinutes() / 60;
    return SESSIONS.filter(function (s) { return h >= s[1] && h < s[2]; }).map(function (s) { return s[0]; });
  }
  function gradeClass(g) { return g === 'HIT' ? 'up' : g === 'MISS' ? 'down' : 'dim'; }
  function stale(data, now) {
    var d0 = Date.parse(data.day + 'T00:00:00Z'), b = Date.parse(data.built_utc);
    return !isFinite(d0) || now >= d0 + DAY_MS || !isFinite(b) || now - b > STALE_MS;
  }
  function status(c, now) { return now >= c.end_ms ? 'DONE' : now >= c.start_ms ? 'NOW' : 'NEXT'; }

  function scen(s) {
    var c = s.counts, lean = s.likely === 'NONE' ? 'no lean' : 'lean ' + s.likely;
    return '<li><b>' + esc(s.id) + '</b> ' + esc(s.name) + ': up <b class="up">' + n0(s.up) + '</b> <span class="dim">' + esc(s.up_label) + '</span> / down <b class="down">' + n0(s.down) +
      '</b> <span class="dim">' + esc(s.down_label) + '</span> &middot; ' + lean + '<br><span class="dim">history n ' + c.n + ': up first ' + c.UP + ', down first ' + c.DOWN + ', both ' + c.BOTH + ', neither ' + c.NEITHER +
      '</span><br>Invalid: ' + esc(s.invalid) + '<br><span class="dim">' + esc(s.idea) + '</span></li>';
  }
  function card(c, now, nowNames) {
    var on = nowNames.indexOf(c.name) >= 0, st = status(c, now), b = c.base || {}, t = c.today;
    var h = '<article class="pbc' + (on ? ' now' : '') + '" data-s="' + esc(c.name) + '"><h3>' + esc(c.name) + ' <span class="pbh">' + esc(c.hours) + '</span> <span class="pbst ' + st + '">' + st + '</span></h3>';
    if (b.n) h += '<div class="pbr">range p25 / p50 / p75 ' + p2(b.range_p25) + ' / ' + p2(b.range_p50) + ' / ' + p2(b.range_p75) + ' <span class="dim">n ' + b.n + '</span></div>';
    if (t) h += '<div class="pbr">' + (t.complete ? 'today' : 'so far') + ': H ' + n0(t.h) + ' L ' + n0(t.l) + ' range ' + p2(t.range_pct) + (t.pctile == null ? '' : ' <span class="dim">(' + Math.round(t.pctile * 100) + '% of history at or below)</span>') + '</div>';
    h += c.scenarios.length ? '<ul class="pbs">' + c.scenarios.map(scen).join('') + '</ul>' : '<div class="dim">' + (st === 'DONE' ? 'session over; its maps are in the ledger above' : 'no map: levels too close or too little history') + '</div>';
    if (c.events && c.events.length) h += '<div class="pbr">events: ' + c.events.map(function (e) { return esc(e.cls) + ' ' + esc(e.hhmm) + 'Z'; }).join(', ') + '</div>';
    h += '<ul class="pbn">' + (c.notes || []).map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul></article>';
    return h;
  }
  function yesterday(y) {
    if (!y || !y.rows || !y.rows.length) return '<div class="pby dim">Yesterday: no playbook rows in the ledger.</div>';
    return '<div class="pby"><b>Yesterday ' + esc(y.day) + '</b>: <span class="up">HIT ' + y.hit + '</span> &middot; <span class="down">MISS ' + y.miss + '</span> &middot; NA ' + y.na + ' &middot; open ' + y.open +
      '<table><thead><tr><th>Id</th><th>Session</th><th>Map</th><th>Lean</th><th>Up / down</th><th>Result</th></tr></thead><tbody>' + y.rows.map(function (r) {
        return '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.session) + '</td><td>' + esc(r.name) + '</td><td>' + esc(r.likely) + '</td><td>' + n0(r.up) + ' / ' + n0(r.down) + '</td><td class="' + gradeClass(r.grade) + '"><b>' + esc(r.grade) +
          '</b> <span class="dim">' + esc(r.outcome || '') + (r.touched ? ' ' + esc(r.touched.slice(11, 16)) + 'Z' : '') + '</span></td></tr>';
      }).join('') + '</tbody></table></div>';
  }
  function html(data, now) {
    if (!data || !data.sessions) return '<p class="pbmsg">PLAYBOOK NOT_IN_DATA (run MyTradingSys/tools/live_aid/daily_playbook.py)</p>';
    var nn = nowSessions(now), h = '';
    if (stale(data, now)) h += '<p class="pbmsg stale">PLAYBOOK STALE: built for ' + esc(data.day) + ' at ' + esc(data.built_utc) + '; run daily_playbook.py</p>';
    // the one-line level wall (11 levels) and the analyst list moved to the Map ladder (map.js + level_registry.js): a level shows once, there.
    h += '<div class="pbg">' + data.sessions.map(function (c) { return card(c, now, nn); }).join('') + '</div>';
    h += yesterday(data.yesterday);
    // the next event is the countdown chip on the Map (deduped there)
    h += '<div class="pbr dim">Ledger: ' + esc(String(data.ledger || '').split('\n')[0]) + '</div><ul class="pbn">' + (data.notes || []).map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul>';
    return h;
  }
  function summary(data, now) {
    if (!data || !data.sessions) return 'PLAYBOOK NOT_IN_DATA';
    var nn = nowSessions(now), cs = data.sessions.filter(function (c) { return nn.indexOf(c.name) >= 0; }), tag = 'now';
    if (!cs.length) { cs = data.sessions.filter(function (c) { return c.start_ms > now; }).slice(0, 1); tag = 'next'; }
    var y = data.yesterday || { hit: 0, miss: 0 };
    var head = cs.length ? cs.map(function (c) { return c.name; }).join('+') + ' ' + tag + ': ' + cs.reduce(function (n, c) { return n + c.scenarios.length; }, 0) + ' maps' +
      (cs[0].base && cs[0].base.n ? ', usual range ' + p2(cs[0].base.range_p50) : '') : 'no session left today';
    return (stale(data, now) ? 'STALE ' : '') + head + ' &middot; yesterday HIT ' + y.hit + ' MISS ' + y.miss;
  }
  var api = { SESSIONS: SESSIONS, STALE_MS: STALE_MS, nowSessions: nowSessions, gradeClass: gradeClass, stale: stale, html: html, summary: summary };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.PLAYBOOK = api;
})(typeof window !== 'undefined' ? window : this);
