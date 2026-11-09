// Live Aid Map (card live-aid-bias-map-one-screen-1109): today's playbook as ONE screen, built only from what the other Live Aid
// sections already show. Top: bias dial (LONG / SHORT / HOLD) with how many sections agree. Middle: price ladder (nearest 3 zones
// each side, levels within 0.15 % merged by level_registry.js). Bottom: session strip (Asia / Europe / US, current one lit, one
// arrow each, next-event countdown) and at most 3 scenario cards. No new statistic, no order, nothing gates. Fail closed:
// no data reads NOT_IN_DATA, a stale day reads STALE. Operator rule 11-09: symbols, colour, graphs; at most 60 words on the screen.
(function (root) {
  'use strict';
  var REG = (typeof module !== 'undefined' && module.exports) ? require('./level_registry.js') : root.LEVELREG;
  var SESSIONS = [['Asia', 0, 8], ['Europe', 7, 13], ['US', 13, 21]];     // UTC hours, as daily_playbook.py SESSIONS
  var SECTIONS = ['Analysts', 'Price vs VWAP', 'RSI 1h', 'RSI 4h', 'Pierce', 'Playbook'];   // the six verdicts the page already shows
  var STALE_MS = 36 * 3600 * 1000, DAY_MS = 86400000, SHOW_BADGES = 2, MAX_SCEN = 3;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n0(x) { return Math.round(x).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function ok(v) { return v === 1 || v === -1 || v === 0; }

  // votes: array of +1 / -1 / 0 / null (null = NOT_IN_DATA), one per section. Same threshold as the verdict board (live_aid_indicators.js lean):
  // 3 sections in data needed; LONG at 2+ bull and bull >= 2 x bear; SHORT mirrored; else HOLD.
  function bias(votes, total) {
    var v = (votes || []).filter(ok), bull = v.filter(function (x) { return x === 1; }).length, bear = v.filter(function (x) { return x === -1; }).length;
    total = total || (votes || []).length || SECTIONS.length;
    var dir = v.length < 3 ? 'HOLD' : bull >= 2 && bull >= 2 * bear ? 'LONG' : bear >= 2 && bear >= 2 * bull ? 'SHORT' : 'HOLD';
    var flat = v.length - bull - bear;
    return { dir: dir, cls: dir === 'LONG' ? 'up' : dir === 'SHORT' ? 'down' : 'dim', bull: bull, bear: bear, flat: flat, n: v.length, total: total,
             agree: dir === 'LONG' ? bull : dir === 'SHORT' ? bear : flat, thin: v.length < 3 };
  }
  // The playbook's own verdict: first map of the session in progress (else the next one): UP +1, DOWN -1, NONE 0; null when no map.
  function sessionNow(data, now) {
    var cs = (data && data.sessions) || [], on = cs.filter(function (c) { return now >= c.start_ms && now < c.end_ms; });
    return on.length ? on : cs.filter(function (c) { return c.start_ms > now; }).slice(0, 1);
  }
  function playbookVote(data, now) {
    var cs = sessionNow(data, now);
    for (var i = 0; i < cs.length; i++) {
      var s = cs[i].scenarios && cs[i].scenarios[0];
      if (s) return s.likely === 'UP' ? 1 : s.likely === 'DOWN' ? -1 : 0;
    }
    return null;
  }
  function arrow(c, now) {
    var s = c.scenarios && c.scenarios[0];
    if (s) return s.likely === 'UP' ? '\u2191' : s.likely === 'DOWN' ? '\u2193' : '\u2192';
    if (now >= c.end_ms && c.today && c.today.o && c.today.c) return c.today.c > c.today.o ? '\u2191' : c.today.c < c.today.o ? '\u2193' : '\u2192';
    return '\u00b7';
  }
  function sessions(data, now) {
    var h = new Date(now).getUTCHours() + new Date(now).getUTCMinutes() / 60, byName = {};
    ((data && data.sessions) || []).forEach(function (c) { byName[c.name] = c; });
    return SESSIONS.map(function (s) {
      var c = byName[s[0]];
      return { name: s[0], h0: s[1], h1: s[2], on: h >= s[1] && h < s[2], done: h >= s[2], arrow: c ? arrow(c, now) : '\u00b7', real: !!c && now >= c.end_ms };
    });
  }
  function scenarios(data, now) {
    var out = [];
    sessionNow(data, now).forEach(function (c) { (c.scenarios || []).forEach(function (s) { out.push(s); }); });
    var seen = {};
    return out.filter(function (s) { var k = s.up + '/' + s.down; if (seen[k]) return false; seen[k] = 1; return true; }).slice(0, MAX_SCEN);
  }
  function nextEvent(data, now) {
    var ev = [];
    ((data && data.sessions) || []).forEach(function (c) { (c.events || []).forEach(function (e) { ev.push(e); }); });
    if (data && data.next_event) ev.push(data.next_event);
    ev = REG.dedupe(ev.filter(function (e) { return e && e.t0 > now; }), function (e) { return e.id; }).sort(function (a, b) { return a.t0 - b.t0; });
    return ev[0] || null;
  }
  function countdown(ms) {
    var m = Math.max(0, Math.floor(ms / 60000)), d = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60);
    return d ? d + 'd' + h + 'h' : h ? h + 'h' + (m % 60) + 'm' : m + 'm';
  }
  function stale(data, now) {
    var d0 = Date.parse(data.day + 'T00:00:00Z'), b = Date.parse(data.built_utc);
    return !isFinite(d0) || now >= d0 + DAY_MS || !isFinite(b) || now - b > STALE_MS;
  }

  // ---------- drawing ----------
  function dial(b) {
    var cells = '';
    (b.votes || []).forEach(function (v) { cells += '<i class="' + (v === 1 ? 'up' : v === -1 ? 'down' : v === 0 ? 'flat' : 'nid') + '"></i>'; });
    return '<div class="lmd ' + b.cls + '"><b class="lmw">' + b.dir + '</b><span class="lmc">' + (b.thin ? b.n + ' of ' + b.total + ' in data' : b.dir === 'HOLD' ? '\u25b2' + b.bull + ' \u25bc' + b.bear + ' of ' + b.total : b.agree + ' of ' + b.total) +
      '</span><span class="lmv" title="' + esc(SECTIONS.join(' / ')) + '">' + cells + '</span></div>';
  }
  function zoneRow(z, side, px, far) {
    var dist = Math.abs((side === 'above' ? z.lo : z.hi) / px - 1), w = Math.round(30 + 70 * (1 - Math.min(1, far > 0 ? dist / far : 0)));
    var bd = z.badges.slice(0, SHOW_BADGES).map(function (b) { return '<i>' + esc(b) + '</i>'; }).join('') + (z.badges.length > SHOW_BADGES ? '<i>+' + (z.badges.length - SHOW_BADGES) + '</i>' : '');
    return '<div class="lmz ' + side + (z.n > 1 ? ' multi' : '') + '" title="' + esc(z.badges.join(' ')) + '"><span class="lmb" style="width:' + w + '%"></span><span class="lml">' + esc(z.label) + '</span><span class="lmg">' + bd + '</span><span class="lmp">' + n0(z.price) + '</span></div>';
  }
  function ladderHtml(lad, px) {
    if (!(px > 0)) return '<div class="lmz dim">NOT_IN_DATA</div>';
    var all = lad.above.concat(lad.below), far = 0;
    all.forEach(function (z) { far = Math.max(far, Math.abs((z.lo > px ? z.lo : z.hi) / px - 1)); });
    var h = lad.above.slice().reverse().map(function (z) { return zoneRow(z, 'above', px, far); }).join('');
    h += '<div class="lmx"><span class="lmb"></span><b>\u25b6 ' + n0(px) + '</b>' + (lad.at ? '<i>' + esc(lad.at.badges.slice(0, SHOW_BADGES).join(' ')) + '</i>' : '') + '</div>';
    h += lad.below.map(function (z) { return zoneRow(z, 'below', px, far); }).join('');
    return '<div class="lmrows">' + h + '</div>';
  }
  function strip(ss, now, ev) {
    var d = new Date(now), h = d.getUTCHours() + d.getUTCMinutes() / 60, lanes = ss.map(function (s) {
      return '<div class="lms2' + (s.on ? ' on' : s.done ? ' done' : '') + '"><span class="lmq" style="left:' + (s.h0 / 24 * 100).toFixed(2) + '%;width:' + ((s.h1 - s.h0) / 24 * 100).toFixed(2) + '%"><b>' + s.name + '</b> <u class="' + (s.arrow === '\u2191' ? 'up' : s.arrow === '\u2193' ? 'down' : 'dim') + (s.real ? ' real' : '') + '">' + s.arrow + '</u></span></div>';
    }).join('');
    var chip = ev ? '<span class="lmn" title="' + esc(ev.id) + '">' + esc(ev.cls) + ' ' + countdown(ev.t0 - now) + '</span>' : '';
    return '<div class="lmt">' + lanes + '<span class="lmnow" style="left:' + (h / 24 * 100).toFixed(2) + '%"></span></div>' + chip;
  }
  function scenHtml(list) {
    return list.map(function (s) {
      var ic = s.likely === 'UP' ? '\u25b2' : s.likely === 'DOWN' ? '\u25bc' : '\u25c6', c = s.likely === 'UP' ? 'up' : s.likely === 'DOWN' ? 'down' : 'dim';
      var body = s.likely === 'UP' ? n0(s.up) + ' \u2715 ' + n0(s.down) : s.likely === 'DOWN' ? n0(s.down) + ' \u2715 ' + n0(s.up) : n0(s.down) + ' / ' + n0(s.up);
      return '<span class="lmk ' + c + '" data-ledger="' + esc(s.id) + '" title="scenario ledger ' + esc(s.id) + ': ' + esc(s.invalid) + '"><b>' + ic + '</b> ' + body + ' <u>' + esc(s.id) + '</u></span>';
    }).join('');
  }
  // model: {data, now, px, votes (6 numbers or null, in SECTIONS order), panel, ma, analysts} -> html
  function html(m) {
    var data = m.data, now = m.now;
    if (!data || !data.sessions) return '<p class="pbmsg">NOT_IN_DATA</p>';
    var px = m.px > 0 ? m.px : data.price, votes = (m.votes || []).slice(0, SECTIONS.length);
    while (votes.length < SECTIONS.length) votes.push(null);
    votes[5] = playbookVote(data, now);
    var b = bias(votes, SECTIONS.length); b.votes = votes;
    var lad = REG.build({ playbook: data.levels, panel: m.panel, ma: m.ma, analysts: m.analysts || data.analysts }, px);
    var h = stale(data, now) ? '<p class="pbmsg stale">STALE</p>' : '';
    h += '<div class="lm">' + dial(b) + '<div class="lmlad">' + ladderHtml(lad, px) + '</div><div class="lmses">' + strip(sessions(data, now), now, nextEvent(data, now)) + '</div><div class="lmcards">' + scenHtml(scenarios(data, now)) + '</div></div>';
    return h;
  }
  var CSS = '.lm{display:grid;gap:8px}.lm i,.lm u{font-style:normal;text-decoration:none}' +
    '.lmd{display:flex;align-items:center;gap:10px;padding:6px 10px;border:2px solid var(--dim);border-radius:8px}.lmd.up{border-color:var(--up)}.lmd.down{border-color:var(--down)}' +
    '.lmw{font:700 30px/1 var(--mono,monospace)}.lmd.up .lmw{color:var(--up)}.lmd.down .lmw{color:var(--down)}.lmd.dim .lmw{color:var(--dim)}.lmc{font-size:14px;color:var(--dim)}' +
    '.lmv{margin-left:auto;display:flex;gap:3px}.lmv i{width:14px;height:22px;border-radius:2px;background:var(--line)}.lmv i.up{background:var(--up)}.lmv i.down{background:var(--down)}.lmv i.flat{background:var(--dim)}.lmv i.nid{background:transparent;border:1px dashed var(--dim)}' +
    '.lmrows{display:grid;gap:3px}.lmz,.lmx{position:relative;display:flex;align-items:center;gap:8px;height:30px;padding:0 8px;border-radius:4px;overflow:hidden;font:600 15px var(--mono,monospace)}' +
    '.lmz .lmb{position:absolute;left:0;top:0;bottom:0;opacity:.28;z-index:0}.lmz.above .lmb{background:var(--down)}.lmz.below .lmb{background:var(--up)}.lmz.multi .lmb{opacity:.5}' +
    '.lmz>*:not(.lmb),.lmx>*:not(.lmb){position:relative;z-index:1}.lmz .lml{min-width:64px}.lmg{display:flex;gap:4px}.lmg i{font:600 11px system-ui,sans-serif;padding:1px 5px;border-radius:3px;border:1px solid var(--dim);color:var(--fg)}.lmp{margin-left:auto}' +
    '.lmx{background:var(--panel);border:1px solid var(--amber);color:var(--amber);height:26px}.lmx i{font-size:11px;color:var(--dim)}' +
    '.lmt{position:relative;display:grid;gap:3px;padding:2px 0}.lms2{position:relative;height:22px;background:var(--panel);border-radius:3px}.lmq{position:absolute;top:0;bottom:0;display:flex;align-items:center;gap:6px;padding:0 6px;border-radius:3px;background:var(--line);color:var(--dim);font-size:13px;white-space:nowrap;overflow:hidden}' +
    '.lms2.on .lmq{background:var(--amber);color:#111}.lms2.on .lmq u{color:#111}.lmq u{font:700 15px system-ui}.lmq u.up{color:var(--up)}.lmq u.down{color:var(--down)}.lmq u.real{opacity:.6}.lmnow{position:absolute;top:0;bottom:0;width:2px;background:var(--fg);opacity:.8}' +
    '.lmses{display:grid;gap:6px}.lmn{justify-self:start;font:700 13px var(--mono,monospace);padding:2px 10px;border-radius:12px;border:1px solid var(--amber);color:var(--amber)}' +
    '.lmcards{display:flex;flex-wrap:wrap;gap:6px}.lmk{padding:3px 8px;border:1px solid var(--dim);border-radius:6px;font:600 14px var(--mono,monospace);white-space:nowrap}.lmk.up{border-color:var(--up)}.lmk.down{border-color:var(--down)}.lmk u{font:11px system-ui;color:var(--dim)}' +
    '@media(max-width:480px){.lmw{font-size:26px}.lmz,.lmx{font-size:14px}.lmz .lml{min-width:52px}}';
  function injectCss(doc) {
    doc = doc || (typeof document !== 'undefined' ? document : null);
    if (!doc || doc.getElementById('lm-css')) return;
    var st = doc.createElement('style'); st.id = 'lm-css'; st.textContent = CSS; doc.head.appendChild(st);
  }
  function summary(m) {
    var d = m.data;
    if (!d || !d.sessions) return 'MAP NOT_IN_DATA';
    var v = (m.votes || []).slice(0, SECTIONS.length); while (v.length < SECTIONS.length) v.push(null);
    v[5] = playbookVote(d, m.now);
    var b = bias(v, SECTIONS.length), ev = nextEvent(d, m.now);
    return (stale(d, m.now) ? 'STALE ' : '') + '<b class="' + b.cls + '">' + b.dir + '</b> ' + (b.thin ? b.n + ' of ' + b.total + ' in data' : b.agree + ' of ' + b.total) + (ev ? ' &middot; ' + esc(ev.cls) + ' ' + countdown(ev.t0 - m.now) : '');
  }
  var api = { SECTIONS: SECTIONS, bias: bias, playbookVote: playbookVote, sessions: sessions, scenarios: scenarios, nextEvent: nextEvent, countdown: countdown, stale: stale, html: html, summary: summary, CSS: CSS, injectCss: injectCss };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAMAP = api;
})(typeof window !== 'undefined' ? window : this);
