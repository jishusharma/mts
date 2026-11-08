// News weight, bias chip and tab flash (card news-weight-bias-flash-1108; rules: research/news_effects_2026-11/NEWS_DESIGN.md sections 2-6).
// Context only: no gate, no order, no size, no signal feed; he reads W and the chip and acts, nothing is automatic. Pure functions; the page does the wiring.
// W = F x (P + K + I), 0-100. Every number below is a catalogue count (SOURCED, news_events.csv) or carries the word OURS.
(function (root) {
  'use strict';
  var MIN = 60000;

  // ---- P: class prior, 0-40 = 40 x share of verified events with abs z15d > 2 (SOURCED: news_events.csv, verified rows, shares 61% / 30% / 24% on n 33 / 23 / 34).
  // The page cannot read the csv from disk, so the numbers are copied here and test_news_weight.py re-derives them from the csv (a catalogue rebuild turns it red).
  // PPI and every other class: 3 = 40 x the 7% control rate (369 control minutes); PPI p 0.1710 sits at control level. Keep priorFromCsv() as the one rule.
  var P_TABLE = { MACRO_CPI: 24, FOMC: 12, MACRO_NFP: 10, MACRO_PPI: 3, OTHER: 3 };
  // ---- last same-class move per class (SOURCED: last verified, measured row of news_events.csv: date, btc_r15 %, btc_z15d, btc_vr5). Shown, never used in W or the chip.
  var LAST = {
    MACRO_CPI: { date: '2026-10-14', r15: -1.2083, z15d: -7.607, vr5: 28.141 },
    MACRO_PPI: { date: '2026-10-15', r15: -0.2274, z15d: -0.828, vr5: 11.615 },
    FOMC: { date: '2026-10-28', r15: -0.0346, z15d: -0.233, vr5: 9.286 },
    MACRO_NFP: { date: '2026-11-06', r15: -0.3151, z15d: -1.022, vr5: 6.259 }
  };
  // thresholds in z (sigma), none in percent. SOURCED: control share abs z15d > 2 is 7%; vr5 4 is under every class median (4.62 to 11.93); 15 of 123 rows reach abs z15d 4.2+.
  var K_Z = 2, K_VR = 4, K_Z_BIG = 4, K_LO = 20, K_HI = 40;
  // I = 2 x Tree importance (0-10): mapping OURS, importance scale SOURCED (Tree).
  var I_MULT = 2;
  // F: 1.0 for the first 15 min, linear to 0 at 60 min. 15 and 60 are the measured windows (123 rows); the linear shape is OURS.
  var F_FLAT = 15, F_END = 60;
  // flash: W >= 60 is OURS; K = 40 market flash SOURCED (15 of 123 rows). Ends at 60 min (r60 window).
  var FLASH_W = 60;
  // chip: HOLD when more than 35 min passed (median tpk60 32-37 min, SOURCED); overlap window 4 h (8 rows within 4 h, SOURCED)
  var LATE_MIN = 35, OVERLAP_MS = 4 * 3600000;
  // flushed-last-time word: previous same-class vr5 > 15 (10 of the 15 largest reactions, SOURCED; the mechanism is a hypothesis, no weight change)
  var FLUSH_VR5 = 15;
  // an event for the overlap rule: a macro release, or a classified headline marked importance >= 7 (the panel mark, OURS)
  var MACRO = { MACRO_CPI: 1, MACRO_NFP: 1, FOMC: 1, MACRO_PPI: 1 }, EVENT_MARK = 7;
  var SHORT_NAME = { MACRO_CPI: 'CPI', MACRO_NFP: 'NFP', FOMC: 'FOMC', MACRO_PPI: 'PPI', ETF_REGULATORY: 'ETF', HACK_EXPLOIT: 'hack', GEOPOLITICS: 'war',
    TRUMP_POLICY: 'Trump', TARIFF_TRADE: 'tariff', COURT_LEGAL: 'court', PROTOCOL: 'protocol', BOJ_JAPAN: 'BOJ', OTHER: 'news' };

  function num(x) { return typeof x === 'number' && isFinite(x); }
  function clamp(x, a, b) { return Math.min(b, Math.max(a, x)); }
  function f2(x) { return String(+x.toFixed(2)); }
  function signed(x, d) { return (x > 0 ? '+' : x < 0 ? '-' : '') + Math.abs(x).toFixed(d); }
  function pFor(cls) { return P_TABLE.hasOwnProperty(cls) ? P_TABLE[cls] : P_TABLE.OTHER; }
  function pTable() { return JSON.parse(JSON.stringify(P_TABLE)); }

  // ---- catalogue reader: P per class from the csv text (quoted fields allowed)
  function parseCsv(text) {
    var rows = [], row = [], cur = '', q = false, i, c;
    for (i = 0; i < text.length; i++) {
      c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
      else if (c === '"') q = true;
      else if (c === ',') { row.push(cur); cur = ''; }
      else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cur); cur = ''; if (row.length > 1 || row[0] !== '') rows.push(row); row = []; }
      else cur += c;
    }
    if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
    return rows;
  }
  function priorFromCsv(text) {
    var t = parseCsv(String(text || '')), h = t[0] || [], ci = h.indexOf('class'), vi = h.indexOf('verified'), zi = h.indexOf('btc_z15d'), n = {}, hit = {}, out = {};
    t.slice(1).forEach(function (r) {
      var z = parseFloat(r[zi]);
      if (r[vi] !== 'Y' || !isFinite(z)) return;
      n[r[ci]] = (n[r[ci]] || 0) + 1; if (Math.abs(z) > 2) hit[r[ci]] = (hit[r[ci]] || 0) + 1;
    });
    ['MACRO_CPI', 'FOMC', 'MACRO_NFP'].forEach(function (c) { out[c] = n[c] ? Math.round(40 * Math.round(100 * (hit[c] || 0) / n[c]) / 100) : P_TABLE.OTHER; });
    out.MACRO_PPI = 3; out.OTHER = 3;
    return out;
  }

  // ---- classes (section 2). Word rules OURS (the headline wording picks the class; the catalogue has no word rule).
  function classify(title) {
    var s = String(title || '');
    if (/\bCPI\b|consumer price/i.test(s)) return 'MACRO_CPI';
    if (/non-?farm|\bNFP\b|payrolls/i.test(s)) return 'MACRO_NFP';
    if (/\bPPI\b|producer price/i.test(s)) return 'MACRO_PPI';
    if (/\bBOJ\b|bank of japan|\bUeda\b/i.test(s)) return 'BOJ_JAPAN';
    if (/\bFOMC\b|\bfed (?:holds|cuts|hikes|raises|keeps|leaves)|interest rate decision/i.test(s)) return 'FOMC';
    if (/\bETFs?\b/i.test(s)) return 'ETF_REGULATORY';
    if (/\b(?:hack\w*|exploit\w*|drain\w*|stolen|breach\w*)\b/i.test(s)) return 'HACK_EXPLOIT';
    if (/\btariffs?\b|trade war|trade deal/i.test(s)) return 'TARIFF_TRADE';
    if (/\b(?:war|missiles?|airstrikes?|invasion|invades?|ceasefire|sanctions?)\b/i.test(s)) return 'GEOPOLITICS';
    if (/\b(?:court|judge|lawsuit|sues?|indict\w*|ruling|rules in)\b/i.test(s)) return 'COURT_LEGAL';
    if (/hard fork|\bmainnet\b|\bhalving\b|protocol upgrade/i.test(s)) return 'PROTOCOL';
    if (/\btrump\b/i.test(s) && /executive order|\bsigns?\b|\bbill\b|policy|reserve|crypto|\bban\b/i.test(s)) return 'TRUMP_POLICY';
    return 'OTHER';
  }
  // 'prior' tags only for ETF (by wording), hack SHORT, geopolitics SHORT, hot CPI SHORT, cool CPI LONG. No tag for any other class. A tag never sets the chip alone.
  function prior(cls, title) {
    var s = String(title || ''), up, dn;
    if (cls === 'HACK_EXPLOIT' || cls === 'GEOPOLITICS') return 'SHORT';
    if (cls === 'ETF_REGULATORY') {
      up = /\b(?:approv\w*|launch\w*|inflows?|green ?light\w*)/i.test(s); dn = /\b(?:reject\w*|den(?:y|ies|ied)|delay\w*|postpon\w*|outflows?|withdr[ae]w\w*|sues?|lawsuit)\b/i.test(s);
      return up && !dn ? 'LONG' : dn && !up ? 'SHORT' : null;
    }
    if (cls === 'MACRO_CPI') {
      up = /\b(?:hot|hotter|higher than|above (?:expectations|forecast|consensus)|accelerat\w*)\b/i.test(s); dn = /\b(?:cool|cooler|cools|softer|lower than|below (?:expectations|forecast|consensus)|eases|slows)\b/i.test(s);
      return up && !dn ? 'SHORT' : dn && !up ? 'LONG' : null;
    }
    return null;
  }
  function isEvent(cls, importance) { return !!MACRO[cls] || (cls !== 'OTHER' && num(+importance) && +importance >= EVENT_MARK); }
  // another event within 4 h: pool = [{id, cls, time}] of event headlines, events = [{cls, t0}] (strip rows). A classified item ignores its own class (same event restated).
  function overlapOf(cls, time, id, pool, events) {
    var best = null, bd = Infinity;
    function look(c, t, i) {
      var d = Math.abs(t - time);
      if (i !== undefined && i === id) return;
      if (c === 'OTHER' || (cls !== 'OTHER' && c === cls) || d > OVERLAP_MS || d >= bd) return;
      best = c; bd = d;
    }
    (pool || []).forEach(function (p) { look(p.cls, p.time, p.id); });
    (events || []).forEach(function (e) { look(e.cls, e.t0); });
    return best ? (SHORT_NAME[best] || best) : '';
  }

  // ---- K from the page's own BTC 1m feed since the headline minute. z = r since the minute before / (stdev of 1m returns over the prior 24 h x sqrt(minutes elapsed)).
  // Never the prior-hour stdev (z15 depends on the clock). Closed bars only. rows: [openTime, o, h, l, c, volume].
  function confirm(rows, t, now) {
    if (!rows || !rows.length) return null;
    var m0 = Math.floor(t / MIN) * MIN, by = {}, i, bars = [], lr = [], pv = [], v5 = [], a, b, sd, mu, r, mp;
    rows.forEach(function (x) { by[+x[0]] = x; });
    for (i = m0; i + MIN <= now; i += MIN) { if (by[i]) bars.push(by[i]); }
    if (!bars.length || !by[m0] || !by[m0 - MIN]) return null;
    for (i = m0 - 1441 * MIN; i < m0 - MIN; i += MIN) { a = by[i]; b = by[i + MIN]; if (a && b && +a[4] > 0 && +b[4] > 0) lr.push(Math.log(+b[4] / +a[4])); }
    if (lr.length < 1300) return null;                      // the catalogue also needs 1300 of 1440 returns; short feed: no move rather than a guess
    mu = lr.reduce(function (s, x) { return s + x; }, 0) / lr.length;
    sd = Math.sqrt(lr.reduce(function (s, x) { return s + (x - mu) * (x - mu); }, 0) / (lr.length - 1)) * 100;
    if (!(sd > 0)) return null;
    r = (+bars[bars.length - 1][4] / +by[m0 - MIN][4] - 1) * 100;
    for (i = m0 - 60 * MIN; i < m0; i += MIN) { if (by[i]) pv.push(+by[i][5]); }
    bars.slice(0, 5).forEach(function (x) { v5.push(+x[5]); });
    mp = pv.length >= 30 ? pv.reduce(function (s, x) { return s + x; }, 0) / pv.length : 0;
    return { bars: bars.length, r: r, sd: sd, z: r / (sd * Math.sqrt(bars.length)), vr5: mp > 0 ? (v5.reduce(function (s, x) { return s + x; }, 0) / v5.length) / mp : null };
  }
  // K: abs z >= 2 and vr5 >= 4 gives 20; abs z >= 4 gives 40 (any vr5); else 0
  function kOf(z, vr5) {
    if (!num(z)) return 0;
    var a = Math.abs(z);
    return a >= K_Z_BIG ? K_HI : (a >= K_Z && num(vr5) && vr5 >= K_VR) ? K_LO : 0;
  }
  // F by minutes since the headline minute
  function fresh(ageMin) { return !num(ageMin) || ageMin <= F_FLAT ? 1 : ageMin >= F_END ? 0 : 1 - (ageMin - F_FLAT) / (F_END - F_FLAT); }

  // ---- W. o: {cls, importance, ageMin, z, vr5, overlap (label or ''), due (ms to a scheduled t0, > 0 before it)}. No sequence input: no decay of the n-th event.
  function parts(o) {
    o = o || {};
    var cls = o.cls || 'OTHER', sched = num(o.due) && o.due > 0, imp = parseFloat(o.importance), I = isFinite(imp) ? clamp(I_MULT * imp, 0, 20) : 0,
      P = pFor(cls) / (o.overlap ? 2 : 1), K = sched ? 0 : kOf(o.z, o.vr5), F = sched ? 1 : fresh(o.ageMin), w = clamp(Math.round(F * (P + K + I)), 0, 100);
    return { w: w, P: P, K: K, I: I, F: F, scheduled: sched, label: { P: 'SOURCED', K: 'SOURCED', I: 'OURS', F: 'OURS' },
      hover: 'W ' + w + ' = F x (P + K + I). P ' + f2(P) + ' SOURCED (' + (cls === 'OTHER' ? 'every other class' : cls) + ' catalogue share, 40 x share abs z15d > 2' + (o.overlap ? '; halved, overlap ' + o.overlap + ', OURS' : '') + '). K ' + K +
        ' SOURCED (BTC 1m since the headline: abs z >= 2 and vr5 >= 4 gives 20, abs z >= 4 gives 40; control 7%). I ' + f2(I) + ' OURS (2 x Tree importance, importance SOURCED). F ' + f2(F) +
        ' OURS (1 for 15 min, linear to 0 at 60; windows SOURCED, shape OURS). Context only.' };
  }

  // ---- chip. o: {cls, prior, z, vr5, ageMin, overlap, due}. HOLD by default; LONG or SHORT only on the market's own move.
  function bias(o) {
    o = o || {};
    var k, dir, why;
    if (o.cls === 'MACRO_PPI') return { chip: 'HOLD', reason: 'PPI' };
    if (num(o.due) && o.due > 0) { var s = Math.floor(o.due / 1000); return { chip: 'HOLD', reason: 'due in ' + String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0') }; }
    if (o.overlap) return { chip: 'HOLD', reason: 'overlap ' + o.overlap };
    if (num(o.ageMin) && o.ageMin > LATE_MIN) return { chip: 'HOLD', reason: 'late ' + Math.floor(o.ageMin) + ' min' };
    k = kOf(o.z, o.vr5);
    if (k < K_LO) return { chip: 'HOLD', reason: 'no move' };
    dir = o.z > 0 ? 'LONG' : 'SHORT';
    if (o.prior && o.prior !== dir) return { chip: 'HOLD', reason: 'prior vs move' };
    why = 'move ' + (o.z > 0 ? '+' : '-') + 'z ' + Math.abs(o.z).toFixed(1) + (num(o.vr5) ? ' v ' + Math.round(o.vr5) : '');
    return { chip: dir, reason: why };
  }

  // ---- repeat (section 6): shown, never a weight term, never sets the chip
  function flushedWord(last) { return last && num(last.vr5) && last.vr5 > FLUSH_VR5 ? 'flushed last time' : ''; }
  function lastMove(cls) {
    var l = LAST[cls];
    if (!l) return null;
    var fl = !!flushedWord(l);
    return { date: l.date, r15: l.r15, z15d: l.z15d, vr5: l.vr5, flushed: fl,
      text: l.date + ' r15 ' + signed(l.r15, 2) + '% z ' + signed(l.z15d, 1) + ' v ' + Math.round(l.vr5) + (fl ? ' flushed last time' : '') };
  }

  // ---- one headline. row: {id, time, title, importance}. ctx: {now, rows (1m feed) or z + vr5, overlap | pool + events, due}
  function assess(row, ctx) {
    ctx = ctx || {};
    var cls = classify(row.title), ageMin = (ctx.now - row.time) / MIN, mv = null, z = ctx.z, vr5 = ctx.vr5, pr = prior(cls, row.title),
      ov = typeof ctx.overlap === 'string' ? ctx.overlap : overlapOf(cls, row.time, row.id, ctx.pool, ctx.events), p, b, last = lastMove(cls);
    if (z === undefined && ctx.rows && ageMin >= 0 && ageMin < F_END) { mv = confirm(ctx.rows, row.time, ctx.now); z = mv ? mv.z : null; vr5 = mv ? mv.vr5 : null; }
    p = parts({ cls: cls, importance: row.importance, ageMin: ageMin, z: z, vr5: vr5, overlap: ov, due: ctx.due });
    b = bias({ cls: cls, prior: pr, z: z, vr5: vr5, ageMin: ageMin, overlap: ov, due: ctx.due });
    // the 1m feed could not give a move (under 24 h of bars, a gap, or no closed bar yet): say so rather than "no move"
    if (ctx.rows !== undefined && z === null && b.reason === 'no move' && ageMin >= 0 && ageMin < F_END) b.reason = ageMin < 1 ? 'no closed bar' : 'no 1m data';
    return { id: row.id, time: row.time, cls: cls, name: SHORT_NAME[cls] || cls, prior: pr, w: p.w, k: p.K, parts: p, hover: p.hover, chip: b.chip, reason: b.reason,
      ageMin: ageMin, z: num(z) ? z : null, vr5: num(vr5) ? vr5 : null, last: last, flushed: last ? flushedWord(last) : '' };
  }

  // ---- flash state (section 4). items: [{id, w, k, chip, time}]; viewing: he has the News tab open. Returns a new state, .on = pulse the News tab.
  // Qualifies: W >= 60 or K = 40, headline younger than 60 min. A headline starts one flash; a LONG<->SHORT flip of a qualifying headline re-flashes once; a flip to HOLD never does.
  // Opening the tab stops it and counts as seen; it also ends when no item qualifies (W under 60 and K under 40) or at 60 min. Scheduled-minute flashes (T-15, T0) belong to the event strip card.
  function flashInit() { return { on: false, since: 0, why: '', flashed: {}, flips: {}, dir: {} }; }
  function qualifies(it, now) { return (now - it.time) / MIN < F_END && (it.w >= FLASH_W || it.k === K_HI); }
  function flashStep(s, items, now, viewing) {
    var n = { on: !!s.on, since: s.since, why: s.why, flashed: Object.assign({}, s.flashed), flips: Object.assign({}, s.flips), dir: Object.assign({}, s.dir) }, start = false, any = false;
    n.why = '';
    (items || []).forEach(function (it) {
      var q = qualifies(it, now), prev;
      if (it.chip === 'LONG' || it.chip === 'SHORT') {
        prev = n.dir[it.id];
        if (prev && prev !== it.chip && q && !n.flips[it.id]) { n.flips[it.id] = 1; start = true; n.why = 'flip ' + it.chip; }
        n.dir[it.id] = it.chip;
      }
      if (q) { any = true; if (!n.flashed[it.id]) { n.flashed[it.id] = 1; start = true; if (n.why.indexOf('flip') !== 0) n.why = 'new W ' + it.w; } }
    });
    if (viewing) { n.on = false; }
    else if (start) { n.on = true; n.since = now; }
    else if (n.on && !any) { n.on = false; }
    return n;
  }

  var api = { P_TABLE: P_TABLE, pTable: pTable, priorFromCsv: priorFromCsv, classify: classify, prior: prior, isEvent: isEvent, overlapOf: overlapOf, confirm: confirm, kOf: kOf, fresh: fresh,
    parts: parts, bias: bias, lastMove: lastMove, flushedWord: flushedWord, assess: assess, flashInit: flashInit, flashStep: flashStep, qualifies: qualifies,
    api: function () { return Object.keys(api); } };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.NEWSWEIGHT = api;
})(typeof window !== 'undefined' ? window : this);
