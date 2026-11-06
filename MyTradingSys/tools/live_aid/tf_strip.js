// Timeframe strip (scalp read in 20 s): candle colour, flip, CVD, Bollinger position, time left, alignment line, levels ladder.
// Descriptive only: no size, no orders. Fail closed: missing or short data is null (shown as a dash), never a guess.
// Kline rows are the Binance shape [openTime,o,h,l,c,vol,closeTime,quoteVol,trades,takerBuyBase,...]; spot from data-api.binance.vision.
// OURS: Bollinger(20,2) population stdev, "near" band = outer 20% of the band width, value-area bin = 50 USD, 70%, bins labelled by lower edge,
// volume placed in the bin of the bar's hlc3, expansion adds the larger neighbour bin.
(function (root) {
  'use strict';
  var TFS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w'];
  var SCALP = ['1m', '3m', '5m', '15m'], CONTEXT = ['1h', '2h', '4h', '6h', '12h'];
  var DAY = 86400000;
  var BASE = 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT';

  function num(x) { var v = typeof x === 'number' ? x : parseFloat(x); return isFinite(v) ? v : null; }
  function valid(k) { return Array.isArray(k) && num(k[1]) !== null && num(k[4]) !== null && num(k[0]) !== null; }

  // green when close above open, red when below; equal or unreadable = null
  function colour(k) {
    if (!valid(k)) return null;
    var o = num(k[1]), c = num(k[4]);
    return c > o ? 'green' : c < o ? 'red' : null;
  }

  // forming bar colour differs from the last closed bar. ageMs = time since the forming bar opened (the best a kline gives).
  function flip(klines, now) {
    if (!Array.isArray(klines) || klines.length < 2) return null;
    var f = klines[klines.length - 1], p = klines[klines.length - 2];
    var cf = colour(f), cp = colour(p);
    if (!cf || !cp) return null;
    return { flipped: cf !== cp, ageMs: Math.max(0, now - num(f[0])) };
  }

  // taker buy minus sell volume of one bar: buy = field 9, sell = volume - buy, delta = 2*buy - volume
  function cvd(k) {
    if (!Array.isArray(k)) return null;
    var vol = num(k[5]), buy = num(k[9]);
    if (vol === null || buy === null || vol < 0 || buy < 0 || buy > vol) return null;
    var d = 2 * buy - vol;
    return { delta: d, dir: d > 0 ? 'up' : d < 0 ? 'down' : null };
  }

  // Bollinger(20,2) on the last 20 closes including the forming bar. pos 0 = lower band, 100 = upper band (unclamped in raw, clamped in pos).
  function bbPos(closes) {
    if (!Array.isArray(closes) || closes.length < 20) return null;
    var w = closes.slice(-20).map(num);
    if (w.some(function (x) { return x === null; })) return null;
    var m = w.reduce(function (a, b) { return a + b; }, 0) / 20;
    var sd = Math.sqrt(w.reduce(function (a, b) { return a + (b - m) * (b - m); }, 0) / 20);
    if (!(sd > 0)) return null;
    var lo = m - 2 * sd, up = m + 2 * sd, c = w[19], raw = 100 * (c - lo) / (up - lo);
    var label = raw < 0 ? 'below lower' : raw < 20 ? 'near lower' : raw <= 80 ? 'mid' : raw <= 100 ? 'near upper' : 'above upper';
    return { raw: raw, pos: Math.max(0, Math.min(100, raw)), label: label, lower: lo, mid: m, upper: up };
  }

  function timeLeftMs(k, now) {
    var ce = Array.isArray(k) ? num(k[6]) : null;
    if (ce === null) return null;
    var left = ce + 1 - now;
    return left >= -20000 ? Math.max(0, left) : null; // older than 20 s past close: the forming bar is missing
  }

  // 1m bars -> {val, vah, poc} on 50 USD bins, 70 %. null when there is no volume.
  function valueArea(bars, bin, share) {
    bin = bin || 50; share = share || 0.7;
    var b = {}, tot = 0;
    (bars || []).forEach(function (k) {
      var h = num(k[2]), l = num(k[3]), c = num(k[4]), v = num(k[5]);
      if (h === null || l === null || c === null || v === null || v <= 0) return;
      var i = Math.floor(((h + l + c) / 3) / bin);
      b[i] = (b[i] || 0) + v; tot += v;
    });
    var keys = Object.keys(b).map(Number);
    if (!keys.length || !(tot > 0)) return null;
    var poc = keys[0];
    keys.forEach(function (i) { if (b[i] > b[poc] || (b[i] === b[poc] && i < poc)) poc = i; });
    var lo = poc, hi = poc, acc = b[poc], min = Math.min.apply(null, keys), max = Math.max.apply(null, keys);
    while (acc < share * tot && (lo > min || hi < max)) {
      var up = hi < max ? (b[hi + 1] || 0) : -1, dn = lo > min ? (b[lo - 1] || 0) : -1;
      if (up >= dn) { hi++; acc += Math.max(up, 0); } else { lo--; acc += Math.max(dn, 0); }
    }
    return { val: lo * bin, vah: (hi + 1) * bin, poc: poc * bin };
  }

  function utcDay(t) { return t - (t % DAY); }
  function range(bars) {
    var h = null, l = null;
    bars.forEach(function (k) {
      var kh = num(k[2]), kl = num(k[3]);
      if (kh === null || kl === null) return;
      h = h === null ? kh : Math.max(h, kh); l = l === null ? kl : Math.min(l, kl);
    });
    return h === null ? null : { h: h, l: l };
  }

  // Levels from 1m bars (prior UTC day start .. now). Missing pieces are absent, never guessed.
  function levels(bars1m, now, price) {
    var out = [], d0 = utcDay(now), p0 = d0 - DAY;
    var bars = (bars1m || []).filter(valid);
    var prior = bars.filter(function (k) { return k[0] >= p0 && k[0] < d0; });
    var today = bars.filter(function (k) { return k[0] >= d0 && k[0] <= now; });
    var add = function (name, v) { if (v !== null && v !== undefined && isFinite(v)) out.push({ name: name, price: v }); };
    if (prior.length >= 1380) { // a day with holes is not a prior day (fail closed)
      var r = range(prior); add('Prior day high', r.h); add('Prior day low', r.l); add('Prior day close', num(prior[prior.length - 1][4]));
      var va = valueArea(prior, 50, 0.7);
      if (va) { add('Prior VAH', va.vah); add('Prior VAL', va.val); add('Prior POC', va.poc); }
    }
    var sess = function (name, a, z) {
      var s = today.filter(function (k) { return k[0] >= d0 + a * 3600000 && k[0] < d0 + z * 3600000; });
      var rr = s.length ? range(s) : null;
      if (rr) { add(name + ' high', rr.h); add(name + ' low', rr.l); }
    };
    sess('Asia', 0, 8); sess('London', 8, 13);
    var pv = 0, v = 0;
    today.forEach(function (k) {
      var h = num(k[2]), l = num(k[3]), c = num(k[4]), vol = num(k[5]);
      if (h === null || l === null || c === null || vol === null || vol <= 0) return;
      pv += vol * (h + l + c) / 3; v += vol;
    });
    if (v > 0) add('Day VWAP', pv / v);
    var p = num(price);
    if (p === null) return [];
    return out.map(function (x) { return { name: x.name, price: x.price, dist: x.price - p, side: x.price > p ? 'above' : x.price < p ? 'below' : 'at' }; })
      .sort(function (a, b) { return Math.abs(a.dist) - Math.abs(b.dist); });
  }

  // One strip row from one timeframe's klines (last = forming bar).
  function row(klines, now) {
    if (!Array.isArray(klines) || klines.length < 2) return null;
    var f = klines[klines.length - 1];
    var left = timeLeftMs(f, now), col = colour(f);
    if (left === null || !valid(f)) return null;
    var closed = klines.slice(0, -1).slice(-3).map(colour);
    return { colour: col, last3: closed, flip: flip(klines, now), cvd: cvd(f), bb: bbPos(klines.map(function (k) { return k[4]; })), leftMs: left };
  }

  function groupCount(rows, names) {
    var g = 0, r = 0;
    names.forEach(function (n) { var x = rows[n]; if (x && x.colour === 'green') g++; else if (x && x.colour === 'red') r++; });
    return { green: g, red: r, n: g + r, total: names.length };
  }
  function lean(c) { return c.n === 0 ? null : c.green * 2 > c.n ? 'green' : c.red * 2 > c.n ? 'red' : 'mixed'; }

  // "Scalp 4/4 green · Context 2/5 green: counter-trend scalp"
  function alignment(rows) {
    var s = groupCount(rows, SCALP), c = groupCount(rows, CONTEXT);
    var part = function (nm, x) { return x.n === 0 ? nm + ' —' : nm + ' ' + x.green + '/' + x.n + ' green'; };
    var ls = lean(s), lc = lean(c), v;
    if (!ls || !lc) v = 'not enough data';
    else if (ls === 'mixed' || lc === 'mixed') v = 'mixed, no clear side';
    else v = ls === lc ? 'scalp with the trend' : 'counter-trend scalp';
    return part('Scalp', s) + ' · ' + part('Context', c) + ': ' + v;
  }

  function fmtLeft(ms) {
    if (ms === null || ms === undefined) return '—';
    var s = Math.floor(ms / 1000), d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60), ss = s % 60;
    if (d) return d + 'd ' + h + 'h';
    if (h) return h + 'h ' + m + 'm';
    return m + 'm ' + (ss < 10 ? '0' : '') + ss + 's';
  }
  function fmtAgo(ms) {
    if (ms === null || ms === undefined) return '—';
    var m = Math.floor(ms / 60000);
    return m < 120 ? m + 'm' : Math.floor(m / 60) + 'h';
  }

  var api = { TFS: TFS, SCALP: SCALP, CONTEXT: CONTEXT, BASE: BASE, colour: colour, flip: flip, cvd: cvd, bbPos: bbPos, timeLeftMs: timeLeftMs,
    valueArea: valueArea, levels: levels, row: row, alignment: alignment, fmtLeft: fmtLeft, fmtAgo: fmtAgo };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.TFSTRIP = api;
})(typeof window !== 'undefined' ? window : this);
