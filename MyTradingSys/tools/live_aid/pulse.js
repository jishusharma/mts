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
  // now > 0 drops the bar still forming (close time >= now; a folded 2m/7m/10m bucket still filling counts as forming), so the
  // grid, the lanes and the indicator card read the same closed bars. No now = every row (replays and old callers).
  function read(k, ms, now) {
    if (k && now > 0) k = k.filter(function (r) { return +r[6] < now; });
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
  function grid(TFK, now) {
    var rows = GRID.map(function (tf) { var r = read(rowsFor(TFK, tf), tf[1], now); return { tf: tf[0], ms: tf[1], r: r }; });
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

  // WaveTrend lane (operator 2026-11-10: 4h crosses come too often to use; crosses on 1m/2m/3m time the move, 15m/30m are the frame,
  // 4h is context). Last nShow bars of wt1/wt2, the cross marks (+1 up, -1 down; strong when wt1 is beyond +-hot at the cross, as in
  // LazyBear's WT_CROSS: 53 = his overbought/oversold level 2, SOURCED), volume and taker delta per bar, and the last cross in words.
  var WT_HOT = 53;   // SOURCED: LazyBear WaveTrend obLevel2 / osLevel2
  // now > 0 drops the bar still forming (close time >= now), so a lane and the indicator card read the same closed bars.
  function lane(TFK, tfName, nShow, now) {
    var tf = GRID.filter(function (g) { return g[0] === tfName; })[0]; if (!tf) return null;
    var k = rowsFor(TFK, tf); if (k && now > 0) k = k.filter(function (r) { return +r[6] < now; });
    if (!k || k.length < P.minBars) return null;
    var t = [], h = [], l = [], c = [];
    k.forEach(function (r) { t.push(+r[0]); h.push(+r[2]); l.push(+r[3]); c.push(+r[4]); });
    var w = A.wavetrend(t, h, l, c, tf[1], P.wtWarm), n = k.length, from = Math.max(0, n - (nShow || 60)), out = [], lastX = null;
    for (var i = from; i < n; i++) {
      var v = +k[i][5], b = +k[i][9], x = w.event[i];
      out.push({ t: t[i], wt1: w.wt1[i], wt2: w.wt2[i], x: x, strong: x !== 0 && Math.abs(w.wt1[i]) >= WT_HOT && sgn(w.wt1[i]) === -x, vol: v, delta: isFinite(v) && isFinite(b) ? 2 * b - v : NaN });
    }
    for (i = n - 1; i >= 0; i--) if (w.event[i]) { lastX = { side: w.event[i], ago: n - 1 - i, wt1: w.wt1[i], strong: Math.abs(w.wt1[i]) >= WT_HOT && sgn(w.wt1[i]) === -w.event[i] }; break; }
    var a = w.wt1[n - 1], b2 = w.wt2[n - 1];
    return { tf: tfName, ms: tf[1], bars: out, wt1: a, wt2: b2, side: isFinite(a) && isFinite(b2) ? sgn(a - b2) : null, zone: !isFinite(a) ? null : a >= WT_HOT ? 'hot' : a <= -WT_HOT ? 'cold' : 'mid', last: lastX };
  }
  // One line per lane, plain words: "▲ crossed up 2 bars ago from cold (strong)".
  function laneWords(L) {
    if (!L) return 'not enough candles yet';
    var z = L.zone === 'hot' ? ', overbought' : L.zone === 'cold' ? ', oversold' : '';
    if (!L.last) return (L.side === 1 ? 'rising' : L.side === -1 ? 'falling' : 'flat') + z;
    var s = L.last.side === 1 ? '▲ crossed up ' : '▼ crossed down ';
    return s + (L.last.ago === 0 ? 'this bar' : L.last.ago + ' bar' + (L.last.ago === 1 ? '' : 's') + ' ago') + (L.last.strong ? (L.last.side === 1 ? ' from oversold' : ' from overbought') : '') + z;
  }

  // Timing check (operator 2026-11-10: "the one cross worth a look" must be a picture, not a sentence). Five lights:
  // trigger = the newest big-dot cross (out of beyond +-53) on 1m / 2m / 3m, at most trigAgo bars old; 15m and 30m = that lane's
  // side; level = price within P.near of a named level; tape = net taker flow over the trigger lane's last tapeN bars.
  // ok = the light agrees with the trigger. ALIGNED = a trigger and all four others agree. Descriptive only: no entry, stop or size.
  var TP = { trigAgo: 5, tapeN: 5, tfs: ['1m', '2m', '3m'] };   // OURS, not backtested
  function timing(lanes, level) {
    lanes = lanes || {};
    var trig = null;
    TP.tfs.forEach(function (tf) {
      var L = lanes[tf]; if (!L || !L.last || !L.last.strong || L.last.ago > TP.trigAgo) return;
      var age = L.last.ago * L.ms; if (!trig || age < trig.age) trig = { tf: tf, side: L.last.side, ago: L.last.ago, age: age };
    });
    var side = trig ? trig.side : 0, sd = function (tf) { var L = lanes[tf]; return L && (L.side === 1 || L.side === -1 || L.side === 0) ? L.side : null; };
    var f15 = sd('15m'), f30 = sd('30m'), tape = null, src = lanes[trig ? trig.tf : '1m'];
    if (src && src.bars && src.bars.length >= TP.tapeN) {
      var s = 0, okT = true; src.bars.slice(-TP.tapeN).forEach(function (b) { if (!isFinite(b.delta)) okT = false; else s += b.delta; });
      tape = okT ? sgn(s) : null;
    }
    var w = function (v) { return v === 1 ? 'up' : v === -1 ? 'down' : v === 0 ? 'flat' : 'no data'; };
    var lights = [
      { k: 'trigger', v: side, ok: !!trig, t: trig ? trig.tf + ' big dot ' + w(side) + ', ' + (trig.ago ? trig.ago + ' bar' + (trig.ago === 1 ? '' : 's') + ' ago' : 'this bar') : 'no big dot on 1m 2m 3m in the last ' + TP.trigAgo + ' bars' },
      { k: '15m', v: f15, ok: !!trig && f15 === side, t: '15m WaveTrend ' + w(f15) },
      { k: '30m', v: f30, ok: !!trig && f30 === side, t: '30m WaveTrend ' + w(f30) },
      { k: 'level', v: level ? 1 : 0, ok: !!level, t: level ? 'at ' + level.name : 'not at a named level' },
      { k: 'tape', v: tape, ok: !!trig && tape === side, t: tape === 1 ? 'buyers lead the last ' + TP.tapeN + ' bars' : tape === -1 ? 'sellers lead the last ' + TP.tapeN + ' bars' : tape === 0 ? 'tape even' : 'tape no data' }
    ];
    var n = lights.filter(function (x) { return x.ok; }).length;
    return { side: side, trig: trig, lights: lights, n: n, of: lights.length, state: !trig ? 'NONE' : n === lights.length ? 'ALIGNED' : 'PARTIAL' };
  }

  var api = { GRID: GRID, P: P, WT_HOT: WT_HOT, foldK: foldK, rowsFor: rowsFor, read: read, grid: grid, setup: setup, lane: lane, laneWords: laneWords, TP: TP, timing: timing };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAPULSE = api;
})(typeof window !== 'undefined' ? window : this);
