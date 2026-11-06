// Moving-average strip (MA state per timeframe 5m..1M): price vs 21/55 EMA, 200 SMA, 200 EMA, distance, slope, pullback, 21/55 and 50/200 cross.
// Descriptive only: no size, no orders. Fail closed: too few bars for an average = null (a dash), never a guess.
// Definition and labels: research/ma_layer_2026-11/MA_CONCEPTS.md section (c); the Python twin research/ma_layer_2026-11/ma_state.py must agree (test_spec_ma_strip.py checks it).
// SOURCED: lengths 20/21/50/55/200 (Krown KR-M01, KR-M07, web bull-market band), alpha 2/(N+1) (textbook EMA).
// OURS: EMA seeded with the mean of the first N closes, slope = change over 5 bars vs 0.5 ATR14, pullback touch 0.25 ATR14,
// distance-bar cap 6 ATR14, a cross is "fresh" within 3 bars.
// Kline rows are the Binance shape [openTime,o,h,l,c,vol,...] from data-api.binance.vision; the last row is the forming bar. ATR14 comes from tf_strip.js.
(function (root) {
  'use strict';
  var TS = (typeof module !== 'undefined' && module.exports) ? require('./tf_strip.js') : root.TFSTRIP;
  var TFS = ['5m', '15m', '1h', '4h', '1d', '1w', '1M'];
  var LIMIT = 1000, SLOPE_BARS = 5, FLAT_ATR = 0.5, TOUCH_ATR = 0.25, BAR_CAP_ATR = 6, FRESH_BARS = 3;
  var AVGS = { sma20: ['sma', 20], ema21: ['ema', 21], ema55: ['ema', 55], sma50: ['sma', 50], sma200: ['sma', 200], ema200: ['ema', 200] };
  var SHOWN = [['ema21', '21'], ['ema55', '55'], ['sma200', '200 SMA'], ['ema200', '200 EMA']];

  function num(x) { var v = typeof x === 'number' ? x : parseFloat(x); return isFinite(v) ? v : null; }

  function smaSeries(c, n) {
    var out = new Array(c.length), s = 0;
    for (var i = 0; i < c.length; i++) {
      out[i] = null; s += c[i];
      if (i >= n) s -= c[i - n];
      if (i >= n - 1) out[i] = s / n;
    }
    return out;
  }
  function emaSeries(c, n) {
    var out = new Array(c.length), i;
    for (i = 0; i < c.length; i++) out[i] = null;
    if (c.length < n) return out;
    var a = 2 / (n + 1), e = 0;
    for (i = 0; i < n; i++) e += c[i];
    e /= n; out[n - 1] = e;
    for (i = n; i < c.length; i++) { e = e + a * (c[i] - e); out[i] = e; }
    return out;
  }
  // {state, barsSince}: up/down = fast above/below slow at the last bar with both defined and unequal (a tie keeps the old state);
  // barsSince = bars since the last change of state, null when none
  function crossState(fast, slow) {
    var state = null, lastChange = null;
    for (var i = 0; i < fast.length; i++) {
      var f = fast[i], s = slow[i];
      if (f === null || s === null || f === s) continue;
      var cur = f > s ? 'up' : 'down';
      if (state !== null && cur !== state) lastChange = i;
      state = cur;
    }
    if (state === null) return { state: null, barsSince: null };
    return { state: state, barsSince: lastChange === null ? null : fast.length - 1 - lastChange };
  }
  function slope(series, atr) {
    if (!(atr > 0) || series.length <= SLOPE_BARS) return null;
    var a = series[series.length - 1], b = series[series.length - 1 - SLOPE_BARS];
    if (a === null || b === null) return null;
    var d = a - b;
    return d > FLAT_ATR * atr ? 'up' : d < -FLAT_ATR * atr ? 'down' : 'flat';
  }
  function avgRow(series, price, atr) {
    var v = series[series.length - 1];
    if (v === null || !v) return null;
    return { v: v, side: price > v ? 'above' : price < v ? 'below' : null, distPct: 100 * (price - v) / v,
      distAtr: atr > 0 ? (price - v) / atr : null, ratio: price / v, slope: slope(series, atr) };
  }

  // One state row from one timeframe's klines; null when the bars are unreadable.
  function row(tf, klines) {
    if (!Array.isArray(klines) || klines.length < 2) return null;
    var closes = klines.map(function (k) { return Array.isArray(k) && k.length > 4 ? num(k[4]) : null; });
    var last = klines[klines.length - 1], h = num(last[2]), l = num(last[3]);
    if (closes.some(function (x) { return x === null; }) || h === null || l === null) return null;
    var price = closes[closes.length - 1], atr = TS.atr14(klines);
    if (atr === undefined) atr = null;
    var ser = {}, avgs = {}, k;
    for (k in AVGS) ser[k] = (AVGS[k][0] === 'sma' ? smaSeries : emaSeries)(closes, AVGS[k][1]);
    for (k in AVGS) avgs[k] = avgRow(ser[k], price, atr);
    var e21 = ser.ema21[closes.length - 1], e55 = ser.ema55[closes.length - 1], pb = null;
    if (e21 !== null && e55 !== null && atr !== null && atr > 0) {
      var sl55 = slope(ser.ema55, atr);
      if (e21 > e55 && sl55 === 'up' && l <= e21 + TOUCH_ATR * atr && price >= e55) pb = 'up';
      else if (e21 < e55 && sl55 === 'down' && h >= e21 - TOUCH_ATR * atr && price <= e55) pb = 'down';
    }
    var s20 = ser.sma20[closes.length - 1], band = null;
    if (s20 !== null && e21 !== null) {
      var lo = Math.min(s20, e21), hi = Math.max(s20, e21);
      band = price > hi ? 'above' : price < lo ? 'below' : 'inside';
    }
    return { tf: tf, bars: klines.length, price: price, atr: atr, avgs: avgs, cross2155: crossState(ser.ema21, ser.ema55),
      cross50200: crossState(ser.sma50, ser.sma200), pullback: pb, band: band };
  }
  function rows(byTf) { return TFS.map(function (tf) { return row(tf, byTf && byTf[tf]); }); }

  function fmtPct(p) { return p === null || p === undefined || !isFinite(p) ? '—' : (p > 0 ? '+' : '') + (Math.abs(p) >= 100 ? p.toFixed(0) : p.toFixed(1)) + '%'; }

  // Display model of one row (symbols over words). Returns null for a missing row.
  // cells: above/below arrow, percent distance, slope arrow. bar: price distance from the 21 EMA in ATRs, 0..100 with 50 = on the line, capped at 6 ATR.
  function view(r) {
    if (!r) return null;
    var cells = SHOWN.map(function (p) {
      var a = r.avgs[p[0]];
      if (!a) return { k: p[0], label: p[1], side: null, sym: '—', pct: '—', slope: null };
      return { k: p[0], label: p[1], side: a.side, sym: a.side === 'above' ? '▲' : a.side === 'below' ? '▼' : '=', pct: fmtPct(a.distPct), slope: a.slope };
    });
    var a21 = r.avgs.ema21, bar = null;
    if (a21 && a21.distAtr !== null) {
      var d = Math.max(-BAR_CAP_ATR, Math.min(BAR_CAP_ATR, a21.distAtr));
      bar = { pos: 50 + 50 * d / BAR_CAP_ATR, atr: a21.distAtr, side: a21.side };
    }
    var c = r.cross2155, g = r.cross50200;
    return { tf: r.tf, cells: cells, bar: bar,
      pullback: r.pullback ? { dir: r.pullback, text: r.pullback === 'up' ? 'pullback to 21' : 'rally to 21' } : null,
      cross: c.state ? { dir: c.state, barsSince: c.barsSince, fresh: c.barsSince !== null && c.barsSince <= FRESH_BARS, text: '21' + (c.state === 'up' ? '>' : '<') + '55' + (c.barsSince === null ? '' : ' ' + c.barsSince + 'b') } : null,
      gd: g.state ? { dir: g.state, text: g.state === 'up' ? 'golden' : 'death' } : null,
      inBand: r.band === 'inside' };
  }

  var api = { TFS: TFS, LIMIT: LIMIT, BASE: TS ? TS.BASE : '', smaSeries: smaSeries, emaSeries: emaSeries, crossState: crossState,
    row: row, rows: rows, view: view, fmtPct: fmtPct };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.MASTRIP = api;
})(typeof window !== 'undefined' ? window : this);
