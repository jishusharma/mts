// Upcoming-events strip (card cbp-events-to-watch-wire-1108; rules: research/news_effects_2026-11/NEWS_DESIGN.md sections 4 and 7).
// Context only: no gate, no size, no signal. Pure functions; events_strip_data.js (events_wire.py) supplies the data.
// SOURCED: P table = 40 x share of verified events with abs z15d > 2 (CPI 24, FOMC 12, NFP 10), PPI 3 = control rate (section 3);
// flash times CPI/NFP/FOMC statement at T-15 and T0, presser at T+30 (section 4). OURS: HOLD chip before every scheduled t0,
// "stale" word, headline link keywords, rows without a catalogue class carry no P.
// Not implemented here: the News tab pulse itself (not on trunk); flashDue() is what the pulse calls.
(function (root) {
  'use strict';
  var MIN = 60000, DAY = 86400000;
  var P = { CPI: 24, NFP: 10, FOMC: 12, FOMC_PRESSER: 12, PPI: 3 };
  var LABEL = { CPI: 'CPI', NFP: 'NFP', FOMC: 'FOMC statement', FOMC_PRESSER: 'FOMC presser', PPI: 'PPI' };
  var LASTKEY = { CPI: 'CPI', NFP: 'NFP', FOMC: 'FOMC', FOMC_PRESSER: 'FOMC', PPI: 'PPI' };
  var KEYS = [['FOMC_PRESSER', /press conference|powell says|powell speaks/i], ['FOMC', /\bfomc\b|fed (rate )?decision|federal reserve (rate )?decision|fed (holds|cuts|hikes|raises)/i],
    ['CPI', /\bcpi\b|consumer price/i], ['NFP', /\bnfp\b|non-?farm|payrolls|jobs report|employment situation/i], ['PPI', /\bppi\b|producer price/i]];

  function two(n) { return (n < 10 ? '0' : '') + n; }
  function countdown(ms) {
    var s = Math.max(0, Math.floor(ms / 1000)), d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
    return (d ? d + 'd ' : '') + two(h) + ':' + two(m) + ':' + two(s % 60);
  }
  function flashTimes(row) {
    if (!row || row.loose || !isFinite(row.t0)) return [];
    if (row.cls === 'CPI' || row.cls === 'NFP' || row.cls === 'FOMC') return [row.t0 - 15 * MIN, row.t0];
    if (row.cls === 'FOMC_PRESSER') return [row.t0];   // t0 of the presser row is statement + 30 min
    return [];                                          // PPI, analyst-named OURS rows, 'week of' rows
  }
  // true when a flash time lies in (prev, now]: each time fires once because the caller moves prev forward
  function flashDue(row, prev, now) { return flashTimes(row).some(function (t) { return t > prev && t <= now; }); }

  function rows(now, D, n) {
    D = D || {}; var an = D.analysts || {}, last = D.last || {}, out = [];
    function cnt(id) { var a = an[id] || {}; return { n: a.n || 0, long: a.L || 0, short: a.S || 0, hold: a.H || 0 }; }
    (D.schedule || []).forEach(function (s) {
      if (s.t0 < now) return;
      var c = cnt(s.id);
      out.push({ id: s.id, cls: s.cls, label: LABEL[s.cls] || s.cls, t0: s.t0, loose: false, countdown: countdown(s.t0 - now), p: P[s.cls] == null ? null : P[s.cls],
        last: last[LASTKEY[s.cls]] || null, n: c.n, long: c.long, short: c.short, hold: c.hold, chip: 'HOLD', stale: !!s.stale });
    });
    (D.named || []).forEach(function (s) {
      var loose = s.t0 == null, t0 = loose ? s.weekOf : s.t0;
      if (!isFinite(t0) || (loose ? t0 + DAY <= now : t0 < now)) return;
      var c = cnt(s.id);
      out.push({ id: s.id, cls: null, label: s.label || s.id, t0: t0, loose: loose, countdown: countdown(Math.max(0, t0 - now)), p: null, last: null,
        n: c.n, long: c.long, short: c.short, hold: c.hold, chip: 'HOLD', stale: false });
    });
    out.sort(function (a, b) { return a.t0 - b.t0 || (a.id < b.id ? -1 : 1); });
    return out.slice(0, n || 5);
  }

  // headline that names a strip event: links to the nearest row of that class and inherits its P
  function linkHeadline(title, rs) {
    var t = String(title || '');
    for (var i = 0; i < KEYS.length; i++) {
      if (!KEYS[i][1].test(t)) continue;
      for (var j = 0; j < (rs || []).length; j++) if (rs[j].cls === KEYS[i][0]) return { id: rs[j].id, p: rs[j].p };
    }
    return null;
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function num(v, d) { return isFinite(v) ? (+v).toFixed(d) : '--'; }
  function html(rs) {
    if (!rs || !rs.length) return '<tr><td colspan="6">no event ahead in the schedule data</td></tr>';
    return rs.map(function (r) {
      var l = r.last ? r.last.date + ' r15 ' + num(r.last.r15, 2) + ' z15d ' + num(r.last.z15d, 1) + ' vr5 ' + num(r.last.vr5, 1) : (r.p == null ? 'not measured' : '--');
      return '<tr id="ev-' + esc(r.id) + '"><td>' + esc(r.label) + (r.stale ? ' <span class="chip">stale</span>' : '') + (r.loose ? ' <span class="dim">week of</span>' : '') +
        '</td><td>' + r.countdown + '</td><td>' + (r.p == null ? '--' : r.p) + '</td><td>' + l + '</td>' +
        '<td title="analysts, count only (CBP): never the chip">' + r.n + ' (L' + r.long + ' S' + r.short + ' H' + r.hold + ')</td><td><span class="chip">' + r.chip + '</span></td></tr>';
    }).join('');
  }

  var api = { P: P, countdown: countdown, flashTimes: flashTimes, flashDue: flashDue, rows: rows, linkHeadline: linkHeadline, html: html };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.EVSTRIP = api;
})(typeof window !== 'undefined' ? window : this);
