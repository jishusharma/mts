// Live Aid LEVEL STORY (operator 2026-11-10 21Z): at the nearest named level above and below, say WHERE price is with respect to it
// (approaching, testing, rejected, breaking, accepted, failed break), WHAT the evidence says (wick, Bollinger band, volume, taker delta,
// absorption, open interest, 15m WaveTrend), the IDEA that is forming, and what VALIDATES or VOIDS it. Built on COMPLETED 15m closes:
// 1m/2m wicks run up and down; many analyst calls at a level mean "wait for the close there" (operator).
// Tom (auction): a level is accepted when price closes beyond it and holds (2 closes, as accept80.py uses 2 x 30m), rejected when it
// probes and closes back. Fabio (order flow): aggressive buying into resistance that cannot close above it = buyers absorbed (sellers
// in control), the mirror at support. Descriptive only: never an entry, exit or size; he decides. Every number in P is OURS, untested
// (card live-aid-pulse-backtest-1109 scores the flashes).
(function (root) {
  'use strict';
  var A = (typeof module !== 'undefined' && module.exports) ? require('./live_aid_indicators.js') : root.LiveAid;
  var P = { touch: 0.0005, near: 0.003, wick: 0.5, relVol: 1.5, bbNear: 0.1, look: 3, idea: 3 };   // OURS

  function n0(x) { return Math.round(x).toLocaleString('en-US'); }
  // Completed 15m Binance rows only (close time before now).
  function closed(k, now) { return (k || []).filter(function (r) { return +r[6] < now; }); }

  function story(lv, k15, now, ex) {
    ex = ex || {};
    var k = closed(k15, now), all = k15 || [];
    if (!lv || !(lv.price > 0) || k.length < 25) return null;
    var L = lv.price, last = k[k.length - 1], cNow = all.length ? +all[all.length - 1][4] : +last[4];
    // side from the close BEFORE the recent window (else a break flips the side and can never be seen); found by test_levelstory
    var ref = k[Math.max(0, k.length - 1 - P.look)], res = L >= +ref[4];   // resistance if price came from under it, else support
    var sgn = res ? 1 : -1, beyond = function (c) { return res ? c > L : c < L; };
    var c = k.map(function (r) { return +r[4]; }), v = k.map(function (r) { return +r[5]; });
    var bb = A.bollinger(c, 20, 2), bi = c.length - 1, up = bb.upper[bi], lo = bb.lower[bi], wd = up - lo;
    var avgV = v.slice(-21, -1).reduce(function (s, x) { return s + x; }, 0) / 20;
    // closes beyond, counted back from the last completed bar
    var nb = 0; for (var i = k.length - 1; i >= 0 && beyond(+k[i][4]); i--) nb++;
    var prevIn = k.length > nb ? !beyond(+k[k.length - 1 - nb][4]) : false;
    // the touch: a completed bar in the last 3 whose wick reached the level but closed back
    var touch = null;
    for (i = k.length - 1; i >= Math.max(0, k.length - P.look); i--) {
      var r = k[i], h = +r[2], l = +r[3], o = +r[1], cl = +r[4], rng = h - l, reach = res ? h >= L * (1 - P.touch) : l <= L * (1 + P.touch);
      if (reach && !beyond(cl)) { touch = { i: i, ext: res ? h : l, wickShare: rng > 0 ? (res ? h - Math.max(o, cl) : Math.min(o, cl) - l) / rng : 0, vol: +r[5], delta: 2 * +r[9] - +r[5] }; break; }
    }
    var forming = all.length > k.length ? all[all.length - 1] : null;
    var testing = forming && (res ? +forming[2] >= L * (1 - P.touch) : +forming[3] <= L * (1 + P.touch));
    // failed break: closed beyond in the last 3 bars, now back inside
    var failed = false; for (i = k.length - 2; i >= Math.max(0, k.length - 1 - P.look); i--) if (beyond(+k[i][4])) { failed = !beyond(+last[4]); break; }
    var state = nb >= 2 && prevIn ? 'ACCEPTED' : nb >= 2 ? 'ACCEPTED' : nb === 1 ? 'BREAKING' : failed ? 'FAILED BREAK' : touch ? 'REJECTED' : testing ? 'TESTING' : Math.abs(cNow / L - 1) <= P.near ? 'APPROACHING' : 'AWAY';

    // evidence (signed: + = for the turn away from the level, - = for going through)
    var ev = [], turn = 0, thru = 0, add = function (k2, txt, w, cls) { ev.push({ k: k2, t: txt, cls: cls }); if (w > 0) turn += w; else thru -= w; };
    var bbPos = !isFinite(wd) || wd <= 0 ? null : res ? (+last[2] >= up ? 'outside' : +last[2] >= up - P.bbNear * wd ? 'at' : null) : (+last[3] <= lo ? 'outside' : +last[3] <= lo + P.bbNear * wd ? 'at' : null);
    if (bbPos) add('BB', (bbPos === 'outside' ? 'outside ' : 'at ') + (res ? 'upper' : 'lower') + ' Bollinger (15m)', 1, 'turn');
    if (touch) {
      if (touch.wickShare >= P.wick) add('Wick', 'long ' + (res ? 'upper' : 'lower') + ' wick ' + Math.round(touch.wickShare * 100) + '% of the bar', 1, 'turn');
      var rv = avgV > 0 ? touch.vol / avgV : NaN;
      if (rv >= P.relVol) add('Vol', 'volume ' + rv.toFixed(1) + 'x normal on the touch', 1, 'turn');
      if (sgn * touch.delta > 0) add('Absorb', (res ? 'buyers' : 'sellers') + ' hit it hard but could not close ' + (res ? 'above' : 'below') + ' (absorbed)', 2, 'turn');
      else if (sgn * touch.delta < 0) add('CVD', (res ? 'sellers' : 'buyers') + ' led the touch bar', 1, 'turn');
    }
    if (state === 'ACCEPTED' || state === 'BREAKING') {
      var sb = k.slice(-nb), dl = sb.reduce(function (s, r) { return s + 2 * +r[9] - +r[5]; }, 0), vb = sb.reduce(function (s, r) { return s + +r[5]; }, 0) / nb;
      add('Close', nb + ' close' + (nb > 1 ? 's' : '') + ' ' + (res ? 'above' : 'below'), nb >= 2 ? -3 : -1, 'thru');
      if (sgn * dl > 0) add('CVD', (res ? 'buyers' : 'sellers') + ' drove the break', -1, 'thru'); else add('CVD', 'break without ' + (res ? 'buyers' : 'sellers') + ' (thin)', 1, 'turn');
      if (avgV > 0 && vb / avgV >= P.relVol) add('Vol', 'break volume ' + (vb / avgV).toFixed(1) + 'x', -1, 'thru');
    }
    if (state === 'FAILED BREAK') add('Trap', 'closed ' + (res ? 'above' : 'below') + ', then back ' + (res ? 'under' : 'over') + ' (trapped)', 2, 'turn');
    var w = ex.wt15;
    if (w && isFinite(w.wt1)) {
      if (res ? (w.zone === 'hot' || (w.last && w.last.side === -1 && w.last.ago <= 2)) : (w.zone === 'cold' || (w.last && w.last.side === 1 && w.last.ago <= 2)))
        add('WT', '15m WaveTrend ' + (w.zone === 'hot' ? 'overbought' : w.zone === 'cold' ? 'oversold' : 'just crossed ' + (res ? 'down' : 'up')), 1, 'turn');
      else if (w.side === sgn) add('WT', '15m WaveTrend still pushing ' + (res ? 'up' : 'down'), -1, 'thru');
    }
    if (isFinite(ex.doi) && Math.abs(ex.doi) > 0.0005) add('OI', 'open positions ' + (ex.doi > 0 ? 'rising' : 'falling') + ' (15 min)', 0, 'dim');

    // the idea and what checks it
    var idea = null, why = '', valid = '', voidAt = null, ext = touch ? touch.ext : res ? Math.max(+last[2], L) : Math.min(+last[3], L);
    if ((state === 'REJECTED' || state === 'FAILED BREAK') && turn >= P.idea && turn > thru) {
      idea = res ? 'SHORT' : 'LONG'; voidAt = ext;
      why = (state === 'FAILED BREAK' ? 'failed break of ' : 'rejected at ') + lv.name;
      valid = 'holds while 15m closes stay ' + (res ? 'below ' : 'above ') + n0(L) + '; void on a 15m close ' + (res ? 'above ' : 'below ') + n0(voidAt);
    } else if (state === 'ACCEPTED' && thru >= P.idea && thru > turn) {
      idea = res ? 'LONG' : 'SHORT'; voidAt = L;
      why = 'accepted ' + (res ? 'above ' : 'below ') + lv.name;
      valid = 'holds while 15m closes stay ' + (res ? 'above ' : 'below ') + n0(L) + '; a close back ' + (res ? 'under' : 'over') + ' = failed break';
    } else {
      valid = state === 'BREAKING' ? 'one close ' + (res ? 'above' : 'below') + ': a 2nd 15m close there = accepted, a close back = failed break'
        : state === 'AWAY' ? 'nothing to do at this level yet'
        : 'wait for the 15m close: back ' + (res ? 'under ' : 'over ') + n0(L) + ' with a wick = rejection; 2 closes ' + (res ? 'above' : 'below') + ' = accepted';
    }
    var crowd = lv.n >= 3 ? lv.n + ' calls here: wait for the 15m close, 1m wicks do not count' : '';
    return { price: L, name: lv.name, n: lv.n || 1, res: res, state: state, ev: ev, turn: turn, thru: thru, idea: idea, why: why, valid: valid, voidAt: voidAt, crowd: crowd, bb: bbPos };
  }

  var api = { P: P, story: story, closed: closed };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LASTORY = api;
})(typeof window !== 'undefined' ? window : this);
