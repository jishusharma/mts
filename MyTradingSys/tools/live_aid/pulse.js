// Live Aid PULSE (operator 2026-11-09 17Z): one coloured read per timeframe 1m 2m 3m 5m 7m 10m 15m 30m 1h 2h 4h from RSI, WaveTrend,
// Binance spot CVD (taker buy minus sell) and their divergences with price, an overall lean, and a "setup forming" flag when price
// sits at a named level with the lean and a divergence pointing the same way. Descriptive only: no entry, stop or size; he decides.
// Source: Binance spot klines (data-api.binance.vision: rows [t,o,h,l,c,vol,closeT,quoteVol,trades,takerBuyBase,...]); 2m/7m/10m
// are folded from 1m on UTC-day buckets (same as the page's strip). Every threshold in P = OURS, not yet backtested
// (card live-aid-pulse-backtest-1109 measures it).
(function (root) {
  'use strict';
  var A = (typeof module !== 'undefined' && module.exports) ? require('./live_aid_indicators.js') : root.LiveAid;
  var GRID = [['1m', 60000, '1m'], ['2m', 120000, '1m'], ['3m', 180000, '3m'], ['5m', 300000, '5m'], ['7m', 420000, '1m'], ['10m', 600000, '1m'],
              ['15m', 900000, '15m'], ['30m', 1800000, '30m'], ['1h', 3600000, '1h'], ['2h', 7200000, '2h'], ['4h', 14400000, '4h']];
  // RSI vote uses the same 50 line as the Home Direction gauge (operator 11-10: 46 grey here but red on the gauge read as a contradiction)
  var P = { rsiUp: 50, rsiDn: 50, cvdN: 10, divW: 15, wtWarm: 60, minBars: 40, lean: 0.25, near: 0.0015,   // OURS
            w: { '1m': 1, '2m': 1, '3m': 1, '5m': 1, '7m': 2, '10m': 2, '15m': 2, '30m': 2, '1h': 3, '2h': 3, '4h': 3 },
            lowTfs: ['1m', '2m', '3m', '5m', '7m', '10m', '15m'], highTfs: ['1h', '2h', '4h'] };

  // Fold Binance kline rows into ms buckets counted from the UTC day start; volume (5) and taker buy (9) are summed.
  function foldK(k, ms) {
    var out = [], cur = null, DAY = 86400000;
    (k || []).forEach(function (r) {
      var t = +r[0], a = Math.floor(t / DAY) * DAY, b = a + Math.floor((t - a) / ms) * ms;
      if (!cur || cur[0] !== b) { cur = [b, +r[1], +r[2], +r[3], +r[4], +r[5], b + ms - 1, 0, 0, +r[9]]; out.push(cur); }
      else { cur[2] = Math.max(cur[2], +r[2]); cur[3] = Math.min(cur[3], +r[3]); cur[4] = +r[4]; cur[5] += +r[5]; cur[9] += +r[9]; }
    });
    return out;
  }
  function rowsFor(TFK, tf) {
    var src = TFK && TFK[tf[2]]; if (!src || !src.length) return null;
    return tf[2] === tf[0] ? src : foldK(src, tf[1]);
  }
  function sgn(x) { return x > 0 ? 1 : x < 0 ? -1 : 0; }

  // One timeframe: votes RSI (above 50 up, below 50 down), WaveTrend (wt1 vs wt2), CVD (net taker flow of the last 10 bars);
  // divergences (last 15 bars vs the 15 before, LiveAid.divergence) of price vs RSI, wt1 and cumulative delta count double.
  function read(k, ms) {
    if (!k || k.length < P.minBars) return null;
    var t = [], h = [], l = [], c = [], cum = [], s = 0, okCvd = true;
    k.forEach(function (r) {
      t.push(+r[0]); h.push(+r[2]); l.push(+r[3]); c.push(+r[4]);
      var v = +r[5], b = +r[9];
      if (!isFinite(v) || !isFinite(b)) okCvd = false; else s += 2 * b - v;
      cum.push(s);
    });
    var n = c.length - 1, rs = A.rsi(c, 14), w = A.wavetrend(t, h, l, c, ms, P.wtWarm);
    var rsi = rs[n], a = w.wt1[n], b2 = w.wt2[n], cv = okCvd ? cum[n] - cum[Math.max(0, n - P.cvdN)] : NaN;
    var div = { rsi: A.divergence(c, rs, P.divW), wt: A.divergence(c, w.wt1, P.divW), cvd: okCvd ? A.divergence(c, cum, P.divW) : null };
    var v = { rsi: !isFinite(rsi) ? null : rsi > P.rsiUp ? 1 : rsi < P.rsiDn ? -1 : 0, wt: isFinite(a) && isFinite(b2) ? sgn(a - b2) : null, cvd: isFinite(cv) ? sgn(cv) : null };
    var dsum = (div.rsi || 0) + (div.wt || 0) + (div.cvd || 0), score = (v.rsi || 0) + (v.wt || 0) + (v.cvd || 0) + 2 * dsum;
    return { rsi: rsi, wt1: a, wt2: b2, cvd: cv, v: v, div: div, dsum: dsum, score: score, bias: score >= 2 ? 1 : score <= -2 ? -1 : 0 };
  }

  // Whole grid + weighted lean in [-1, 1] (each row's score / 7, the most one row can reach, weighted 1 / 2 / 3 low to high).
  function grid(TFK) {
    var rows = GRID.map(function (tf) { var r = read(rowsFor(TFK, tf), tf[1]); return { tf: tf[0], ms: tf[1], r: r }; });
    var num = 0, den = 0, hiNum = 0, hiDen = 0;
    rows.forEach(function (x) {
      if (!x.r) return; var wt = P.w[x.tf], sc = Math.max(-7, Math.min(7, x.r.score)) / 7;
      num += wt * sc; den += wt;
      if (P.highTfs.indexOf(x.tf) >= 0) { hiNum += sc; hiDen++; }
    });
    var lean = den ? num / den : NaN, hi = hiDen ? hiNum / hiDen : NaN;
    return { rows: rows, lean: lean, hi: hi, dir: !isFinite(lean) ? 'NO DATA' : lean >= P.lean ? 'UP' : lean <= -P.lean ? 'DOWN' : 'MIXED', n: rows.filter(function (x) { return x.r; }).length };
  }

  // Setup forming: price within 0.15 % of a named level (either side); the big picture (1h-4h lean, or the Home direction) points away from it;
  // at least one divergence on 1m-15m agrees. Returns null or {side, level, name, divs[], why[]}. Wording stays descriptive.
  function setup(g, ladder, px, homeDir) {
    if (!g || !(px > 0) || !ladder) return null;
    // a level within 0.15 % on EITHER side counts: price poking just through a level (a sweep) is the classic spot for a turn
    var near = function (z) { return z && Math.abs(px / z.price - 1) <= P.near; };
    var cand = [ladder.at, ladder.above && ladder.above[0], ladder.below && ladder.below[0]].filter(near)
      .sort(function (a, b) { return Math.abs(px - a.price) - Math.abs(px - b.price); });
    var res = cand[0], sup = cand[0];
    var divs = function (sd) {
      var out = [];
      g.rows.forEach(function (x) {
        if (!x.r || P.lowTfs.indexOf(x.tf) < 0) return;
        ['rsi', 'wt', 'cvd'].forEach(function (key) { if (x.r.div[key] === sd) out.push(x.tf + ' ' + { rsi: 'RSI', wt: 'WaveTrend', cvd: 'CVD' }[key]); });
      });
      return out;
    };
    var tries = [];
    if (res) tries.push({ side: 'SHORT', z: res, sd: -1, big: (isFinite(g.hi) && g.hi < 0) || homeDir === 'SHORT' });
    if (sup) tries.push({ side: 'LONG', z: sup, sd: 1, big: (isFinite(g.hi) && g.hi > 0) || homeDir === 'LONG' });
    for (var i = 0; i < tries.length; i++) {
      var q = tries[i], d = divs(q.sd);
      if (q.big && d.length) return { side: q.side, level: q.z.price, name: q.z.name, divs: d,
        why: ['at ' + q.z.name, 'big picture ' + (q.sd < 0 ? 'down' : 'up'), (q.sd < 0 ? 'bearish' : 'bullish') + ' divergence ' + d.slice(0, 3).join(', ') + (d.length > 3 ? ' +' + (d.length - 3) : '')] };
    }
    return null;
  }

  var api = { GRID: GRID, P: P, foldK: foldK, rowsFor: rowsFor, read: read, grid: grid, setup: setup };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAPULSE = api;
})(typeof window !== 'undefined' ? window : this);
