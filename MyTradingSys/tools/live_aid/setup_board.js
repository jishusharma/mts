// Live Aid SETUP BOARD core (card live-aid-board-core-1111): turns existing layer outputs into two evidence lists, LONG and SHORT.
// Pure function, no I/O. Each item names its layer, timeframe and side. strength = number of live items on that side: a plain
// count, no weight and no probability (nothing here is backtested). Descriptive only: no entry, stop or size.
// Input: { '<tf>': { div:{rsi,wt,cvd} (+1 bullish / -1 bearish, from LiveAid.divergence), bb:{out:+1 above upper / -1 below lower,
//   cvd:'dip'|'spike'}, sweep:+1 swept lows and closed back / -1 swept highs and closed back, absorb:+1 buyers absorb / -1 sellers absorb,
//   vfi:{v}, sqz:{rel,v} (rel>=0 = released this bar, v = momentum sign), adx:{v} (side when trending, 0 none), va:'below'|'above'|'inside' } }
// Side rules, OURS (not the trader's, not backtested): outside the lower band with a CVD dip = long (flush exhaustion), outside the
// upper band with a CVD spike = short (blow-off); value area below = long, above = short (reversion reading).
(function (root) {
  'use strict';
  var node = typeof module !== 'undefined' && module.exports;
  var LAYERS = ['rsi_div', 'wt_div', 'cvd_div', 'bb_cvd', 'sweep', 'absorb', 'vfi', 'sqz_release', 'adx_di', 'value_area'];

  function sgn(x) { return typeof x === 'number' && isFinite(x) ? (x > 0 ? 1 : x < 0 ? -1 : 0) : 0; }

  // one timeframe -> {layer: side(+1/-1)} for live items only
  function sides(x) {
    var s = {}, d = x.div || {};
    if (sgn(d.rsi)) s.rsi_div = sgn(d.rsi);
    if (sgn(d.wt)) s.wt_div = sgn(d.wt);
    if (sgn(d.cvd)) s.cvd_div = sgn(d.cvd);
    if (x.bb) {
      if (x.bb.out < 0 && x.bb.cvd === 'dip') s.bb_cvd = 1;
      else if (x.bb.out > 0 && x.bb.cvd === 'spike') s.bb_cvd = -1;
    }
    if (sgn(x.sweep)) s.sweep = sgn(x.sweep);
    if (sgn(x.absorb)) s.absorb = sgn(x.absorb);
    if (x.vfi && sgn(x.vfi.v)) s.vfi = sgn(x.vfi.v);
    if (x.sqz && typeof x.sqz.rel === 'number' && x.sqz.rel >= 0 && sgn(x.sqz.v)) s.sqz_release = sgn(x.sqz.v);
    if (x.adx && sgn(x.adx.v)) s.adx_di = sgn(x.adx.v);
    if (x.va === 'below') s.value_area = 1; else if (x.va === 'above') s.value_area = -1;
    return s;
  }

  function board(inputs) {
    var out = { long: [], short: [], strength: { long: 0, short: 0 } };
    Object.keys(inputs || {}).forEach(function (tf) {
      var x = inputs[tf];
      if (!x || typeof x !== 'object') return;
      var s = sides(x);
      LAYERS.forEach(function (l) {
        if (!s[l]) return;
        var side = s[l] > 0 ? 'long' : 'short';
        out[side].push({ layer: l, tf: tf, side: side });
      });
    });
    out.strength.long = out.long.length; out.strength.short = out.short.length;
    return out;
  }

  var api = { LAYERS: LAYERS, board: board };
  if (node) module.exports = api; else root.LASB = api;
})(typeof window !== 'undefined' ? window : this);
