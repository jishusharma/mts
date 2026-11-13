// Level registry for the whole Live Aid page (card live-aid-bias-map-one-screen-1109). Every section that names a price level
// (playbook key levels, analyst calls, MA strip averages, Levels panel) hands it over here; a level that two sections name
// within MERGE (0.15 %) is ONE zone with merged source badges, so no tab shows the same level twice. Pure functions, no DOM,
// no new statistic: a zone is only the sorted, merged list of prices the sections already computed. Descriptive only.
(function (root) {
  'use strict';
  var MERGE = 0.0015;                       // 0.15 %: the operator's merge distance (OURS, card 11-09)
  var NEAR_N = 3;                           // zones kept above and below price on the ladder
  // playbook key (daily_playbook.py NAMES) -> [one-word label, badge]; badge = what the operator reads on the band
  var KEYS = { PDH: ['High', 'PDH'], PDL: ['Low', 'PDL'], PDC: ['Close', 'PDC'], PWH: ['High', 'PWH'], PWL: ['Low', 'PWL'], DAY_OPEN: ['Open', 'DO'], WEEK_OPEN: ['Open', 'WO'],
               VAL: ['Value', 'VAL'], POC: ['Value', 'POC'], VAH: ['Value', 'VAH'] };
  var RANK = { playbook: 0, panel: 1, ma: 2, analyst: 3 };   // which label wins in a merge; analysts speak last

  function num(x) { var v = typeof x === 'number' ? x : parseFloat(x); return isFinite(v) && v > 0 ? v : null; }
  function initials(name) {
    var w = String(name || '').split(/[^A-Za-z0-9]+/).filter(Boolean);
    if (!w.length) return '?';
    return (w.length === 1 ? w[0].slice(0, 2) : w.map(function (x) { return x[0]; }).join('').slice(0, 3)).toUpperCase();
  }
  // items: [{price, src ('playbook'|'panel'|'ma'|'analyst'), label, badge, bias?}] -> items with a valid price only
  function fromPlaybook(levels) {
    return (levels || []).filter(Boolean).map(function (l) {
      var k = KEYS[l.k] || [String(l.name || l.k || 'Level').split(' ')[0], String(l.k || '').slice(0, 4)], p = num(l.price);
      return p ? { price: p, src: 'playbook', label: k[0], badge: k[1] } : null;
    }).filter(Boolean);
  }
  function fromAnalysts(list) {
    return (list || []).filter(Boolean).map(function (a) {
      var p = num(a.level);
      if (!p) return null;
      var who = String(a.analyst || '').trim(); if (/^qriptal$/i.test(who)) who = 'Habib';   // Qriptal is the channel, Habib the analyst (operator rule)
      return { price: p, src: 'analyst', label: 'Analyst', badge: initials(a.analyst), bias: a.bias || '', who: who, said: String(a.said || '').trim().slice(0, 80),
               published: String(a.published || '').slice(0, 10), expired: !!a.expired };
    }).filter(Boolean);
  }
  // Names are anchored: 'Prev day low' contains 'day low', and an unanchored test labelled yesterday's low 'Today low' (11-10).
  function fromPanel(list) {          // [{n, p}] from the Levels panel (day VWAP, day high/low, previous day, weekly open)
    return (list || []).filter(Boolean).map(function (l) {
      var p = num(l.p), n = String(l.n || '').replace(/ \(typed\)$/, '').trim();
      var b = /vwap/i.test(n) ? 'VWAP' : /^prev day high/i.test(n) ? 'PDH' : /^prev day low/i.test(n) ? 'PDL' : /^day high/i.test(n) ? 'DH' : /^day low/i.test(n) ? 'DL' : /^weekly high/i.test(n) ? 'WH' : /^weekly low/i.test(n) ? 'WL' : /^weekly open/i.test(n) ? 'WO' : n.slice(0, 4).toUpperCase();
      var lab = /vwap/i.test(n) ? 'VWAP' : /high/i.test(n) ? 'High' : /low/i.test(n) ? 'Low' : /open/i.test(n) ? 'Open' : 'Level';
      return p ? { price: p, src: 'panel', label: lab, badge: b } : null;
    }).filter(Boolean);
  }
  function fromMA(rows) {             // MASTRIP.rows(): {tf, avgs: {ema200: {v}, sma200: {v}, ...}}; only the 200s and 55 EMA of 4h, 1d, 1w (the ones traders draw)
    var out = [];
    (rows || []).forEach(function (r) {
      if (!r || !r.avgs || ['4h', '1d', '1w'].indexOf(r.tf) < 0) return;
      [['ema200', 'E200'], ['sma200', 'S200'], ['ema55', 'E55']].forEach(function (a) {
        var v = r.avgs[a[0]] && num(r.avgs[a[0]].v);
        if (v) out.push({ price: v, src: 'ma', label: 'MA', badge: r.tf.toUpperCase() + a[1] });
      });
      // weekly bull-market support band: 20-week SMA + 21-week EMA (lengths SOURCED, research/ma_layer_2026-11/MA_CONCEPTS.md)
      if (r.tf === '1w') [['sma20', '1WS20'], ['ema21', '1WE21']].forEach(function (a) {
        var v = r.avgs[a[0]] && num(r.avgs[a[0]].v);
        if (v) out.push({ price: v, src: 'ma', label: 'MA', badge: a[1] });
      });
    });
    return out;
  }
  // Merge: sorted by price, a level within MERGE of the zone's lowest price joins it (chain-free: one zone never spans more than 0.15 %).
  function merge(items, tol) {
    tol = tol == null ? MERGE : tol;
    var s = (items || []).filter(function (x) { return x && num(x.price); }).slice().sort(function (a, b) { return a.price - b.price; }), out = [];
    s.forEach(function (it) {
      var z = out[out.length - 1];
      if (z && it.price / z.lo - 1 <= tol + 1e-9) { z.hi = it.price; z.items.push(it); } else out.push({ lo: it.price, hi: it.price, items: [it] });
    });
    return out.map(function (z) {
      var badges = [], srcs = [], best = z.items[0];
      z.items.forEach(function (it) {
        if (badges.indexOf(it.badge) < 0) badges.push(it.badge);
        if (srcs.indexOf(it.src) < 0) srcs.push(it.src);
        if (RANK[it.src] < RANK[best.src]) best = it;
      });
      var kinds = z.items.map(function (i) { return i.label; }).filter(function (l, i, a) { return a.indexOf(l) === i; });
      return { lo: z.lo, hi: z.hi, price: Math.round((z.lo + z.hi) / 2 * 10) / 10, label: kinds.length > 1 ? 'Cluster' : best.label, badges: badges, srcs: srcs, n: z.items.length, items: z.items };
    });
  }
  // Ladder around px: the NEAR_N nearest zones above and the NEAR_N nearest below (a zone holding px counts as 'at').
  function ladder(zones, px, n) {
    n = n || NEAR_N;
    var up = [], dn = [], at = null;
    (zones || []).forEach(function (z) {
      if (px >= z.lo && px <= z.hi) at = z; else if (z.lo > px) up.push(z); else dn.push(z);
    });
    up.sort(function (a, b) { return a.lo - b.lo; }); dn.sort(function (a, b) { return b.hi - a.hi; });
    return { above: up.slice(0, n), below: dn.slice(0, n), at: at };
  }
  function build(src, px) { return ladder(merge([].concat(fromPlaybook(src.playbook), fromPanel(src.panel), fromMA(src.ma), fromAnalysts(src.analysts))), px); }
  // The same headline or event never twice: first one wins, key = lower-cased text without spaces and punctuation (events: id).
  function key(s) { return String(s == null ? '' : s).toLowerCase().replace(/[^a-z0-9]+/g, ''); }
  function dedupe(list, keyFn) {
    var seen = {}, f = keyFn || function (x) { return x && typeof x === 'object' ? (x.id || x.title || x.headline || x.text) : x; };
    return (list || []).filter(function (x) { var k = key(f(x)); if (!k || seen[k]) return false; seen[k] = 1; return true; });
  }
  var api = { MERGE: MERGE, NEAR_N: NEAR_N, KEYS: KEYS, initials: initials, fromPlaybook: fromPlaybook, fromAnalysts: fromAnalysts, fromPanel: fromPanel, fromMA: fromMA, merge: merge, ladder: ladder, build: build, dedupe: dedupe, key: key };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LEVELREG = api;
})(typeof window !== 'undefined' ? window : this);
