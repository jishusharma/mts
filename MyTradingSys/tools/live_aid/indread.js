// Live Aid INDICATOR READ (operator 2026-11-10: "volume I can see on my own chart; I need the insight: what the Volume Flow
// indicator and the others say"). His TradingView favourites, read on completed Binance spot bars of 15m (frame), 1h (bias) and
// 4h (context), each turned into one coloured cell and a few plain sentences. Descriptive only: no entry, stop or size.
// Formulas: backtest/layers/FORMULAS.md section 30 (ADX/DI, Wilder), 31 (Squeeze Momentum, LazyBear script form: band half-width
// 1.5 * sd), 32 (Volume Flow Indicator, LazyBear after Katsanos: 130 / 0.2 / 2.5 / stdev 30 / SMA 3). Those defaults are SOURCED;
// every threshold in P is OURS and not backtested (card live-aid-pulse-backtest-1109 measures it).
(function (root) {
  'use strict';
  var node = typeof module !== 'undefined' && module.exports;
  var A = node ? require('./live_aid_indicators.js') : root.LiveAid;
  var P = { adxTrend: 20, adxStrong: 25, slope: 3, flat: 0.001, cvdN: 10, pxN: 10, volN: 20, minBars: 60, wtWarm: 60, wtHot: 53, staleMs: 1860000 };   // staleMs: 2 bars + 1 min of 15m   // OURS (20 / 25 = the usual ADX reading)
  var TFS = [['15m', 900000, 'frame'], ['1h', 3600000, 'bias'], ['4h', 14400000, 'context']];
  var ROWS = [['vfi', 'Volume flow'], ['sqz', 'Squeeze'], ['adx', 'Trend ADX'], ['wt', 'WaveTrend'], ['rsi', 'RSI'], ['cvd', 'Buy vs sell']];

  function nan(n) { var a = []; for (var i = 0; i < n; i++) a.push(NaN); return a; }
  function sgn(x) { return x > 0 ? 1 : x < 0 ? -1 : 0; }
  function mean(a, from, to) { var s = 0; for (var i = from; i <= to; i++) s += a[i]; return s / (to - from + 1); }
  function pstd(a, from, to) { var m = mean(a, from, to), s = 0; for (var i = from; i <= to; i++) s += (a[i] - m) * (a[i] - m); return Math.sqrt(s / (to - from + 1)); }

  // FORMULAS 30: Wilder ADX / DI+ / DI-. First DI at bar n, first ADX at bar 2n-1.
  function adx(h, l, c, n) {
    var N = c.length, pdi = nan(N), mdi = nan(N), ax = nan(N), sT = 0, sP = 0, sM = 0, dxs = [], av = NaN;
    for (var i = 1; i < N; i++) {
      var tr = Math.max(h[i] - l[i], Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1])), up = h[i] - h[i - 1], dn = l[i - 1] - l[i];
      var p = up > dn && up > 0 ? up : 0, m = dn > up && dn > 0 ? dn : 0;
      if (i <= n) { sT += tr; sP += p; sM += m; } else { sT = sT - sT / n + tr; sP = sP - sP / n + p; sM = sM - sM / n + m; }
      if (i < n) continue;
      var pd = sT ? 100 * sP / sT : 0, md = sT ? 100 * sM / sT : 0, dx = pd + md ? 100 * Math.abs(pd - md) / (pd + md) : 0;
      pdi[i] = pd; mdi[i] = md;
      if (i <= 2 * n - 1) { dxs.push(dx); if (i === 2 * n - 1) av = mean(dxs, 0, dxs.length - 1); } else av = (av * (n - 1) + dx) / n;
      if (i >= 2 * n - 1) ax[i] = av;
    }
    return { pdi: pdi, mdi: mdi, adx: ax };
  }

  // FORMULAS 31: Squeeze Momentum. bbMult = half-width multiple of the population stdev (LazyBear's script uses the KC mult, 1.5).
  // on = Bollinger inside Keltner, off = outside, neither on a tie. Flags from bar n-1, momentum from bar 2n-2.
  function squeeze(h, l, c, n, kc, bbMult) {
    var N = c.length, on = [], off = [], mom = nan(N), src = nan(N), tr = [], i, j;
    for (i = 0; i < N; i++) tr.push(i ? Math.max(h[i] - l[i], Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1])) : h[i] - l[i]);
    for (i = 0; i < N; i++) {
      on.push(false); off.push(false);
      if (i < n - 1) continue;
      var a = i - n + 1, ma = mean(c, a, i), bb = bbMult * pstd(c, a, i), kcw = kc * mean(tr, a, i), d = bb - kcw, tol = 1e-9 * Math.max(Math.abs(bb), Math.abs(kcw), 1e-12);
      on[i] = d < -tol; off[i] = d > tol;
      var hh = -Infinity, ll = Infinity; for (j = a; j <= i; j++) { hh = Math.max(hh, h[j]); ll = Math.min(ll, l[j]); }
      src[i] = c[i] - ((hh + ll) / 2 + ma) / 2;
      if (i >= 2 * n - 2) {
        var xm = (n - 1) / 2, ym = mean(src, a, i), num = 0, den = 0;
        for (j = 0; j < n; j++) { num += (j - xm) * src[a + j]; den += (j - xm) * (j - xm); }
        mom[i] = ym + (num / den) * (n - 1 - xm);
      }
    }
    return { on: on, off: off, mom: mom };
  }

  // FORMULAS 32: Volume Flow Indicator. vfi from bar max(sdLen, len) + len - 1; sm = SMA(vfi, smooth).
  function vfi(h, l, c, v, len, coef, vcoef, sdLen, smooth) {
    var N = c.length, typ = [], inter = nan(N), vcp = nan(N), out = nan(N), sm = nan(N), vave = nan(N), i, j, first = Math.max(sdLen, len);
    for (i = 0; i < N; i++) { typ.push((h[i] + l[i] + c[i]) / 3); if (i) inter[i] = Math.log(typ[i]) - Math.log(typ[i - 1]); }
    for (i = first; i < N; i++) {
      vave[i] = mean(v, i - len, i - 1);
      var cut = coef * pstd(inter, i - sdLen + 1, i) * c[i], vc = Math.min(v[i], vcoef * vave[i]), mf = typ[i] - typ[i - 1];
      vcp[i] = mf > cut ? vc : mf < -cut ? -vc : 0;
    }
    for (i = first + len - 1; i < N; i++) { var s = 0; for (j = i - len + 1; j <= i; j++) s += vcp[j]; out[i] = s / vave[i]; }
    for (i = first + len - 1 + Math.max(smooth, 1) - 1; i < N; i++) sm[i] = smooth > 1 ? mean(out, i - smooth + 1, i) : out[i];
    return { vfi: out, sm: sm };
  }

  // One timeframe from Binance kline rows [t,o,h,l,c,vol,closeT,..,takerBuyBase at 9]; the forming bar (closeT >= now) is dropped.
  // Each cell: v = +1 green / -1 red / 0 grey / null no data, txt = what the cell prints.
  function read(k, ms, now) {
    var rows = (k || []).filter(function (r) { return !(now > 0) || +r[6] < now; });
    if (rows.length < P.minBars) return null;
    var t = [], h = [], l = [], c = [], v = [], cum = [], s = 0, okCvd = true;
    rows.forEach(function (r) { t.push(+r[0]); h.push(+r[2]); l.push(+r[3]); c.push(+r[4]); v.push(+r[5]); var b = r[9] === '' || r[9] == null ? NaN : +r[9]; if (!isFinite(b) || !isFinite(+r[5])) okCvd = false; else s += 2 * b - +r[5]; cum.push(s); });
    var n = c.length - 1, cells = {};
    var F = vfi(h, l, c, v, 130, 0.2, 2.5, 30, 3), f = F.sm[n], f0 = F.sm[n - P.slope];
    cells.vfi = !isFinite(f) ? { v: null, txt: c.length >= 263 ? 'no volume data' : 'needs 263 bars' } : { v: sgn(f), val: f, rising: isFinite(f0) ? sgn(f - f0) : 0, txt: (f > 0 ? '+' : '') + f.toFixed(1) + (f > f0 ? ' ↑' : f < f0 ? ' ↓' : '') };
    var Q = squeeze(h, l, c, 20, 1.5, 1.5), m = Q.mom[n], m0 = Q.mom[n - 1], rel = -1;
    for (var i = n; i > 0 && n - i < 6; i--) if (Q.on[i - 1] && !Q.on[i]) { rel = n - i; break; }
    cells.sqz = !isFinite(m) ? { v: null, txt: '--' } : { v: sgn(m), on: Q.on[n], rel: rel, rising: sgn(m - m0), txt: Q.on[n] ? 'COILED' : (m > 0 ? (m > m0 ? 'up, growing' : 'up, fading') : m < 0 ? (m < m0 ? 'down, growing' : 'down, fading') : 'flat') };
    var D = adx(h, l, c, 14), ax = D.adx[n], side = sgn(D.pdi[n] - D.mdi[n]);
    cells.adx = !isFinite(ax) ? { v: null, txt: '--' } : { v: ax >= P.adxTrend ? side : 0, adx: ax, side: side, strong: ax >= P.adxStrong, txt: Math.round(ax) + (ax < P.adxTrend ? ' no trend' : side > 0 ? ' up' : side < 0 ? ' down' : '') };
    var W = A.wavetrend(t, h, l, c, ms, P.wtWarm), w1 = W.wt1[n], w2 = W.wt2[n];
    cells.wt = !isFinite(w1) || !isFinite(w2) ? { v: null, txt: '--' } : { v: sgn(w1 - w2), val: w1, txt: Math.round(w1) + (w1 >= P.wtHot ? ' hot' : w1 <= -P.wtHot ? ' cold' : w1 > w2 ? ' ↑' : ' ↓') };
    var rs = A.rsi(c, 14)[n];
    cells.rsi = !isFinite(rs) ? { v: null, txt: '--' } : { v: rs > 50 ? 1 : rs < 50 ? -1 : 0, val: rs, txt: String(Math.round(rs)) };
    var cv = okCvd ? cum[n] - cum[n - P.cvdN] : NaN;
    cells.cvd = !isFinite(cv) ? { v: null, txt: '--' } : { v: sgn(cv), val: cv, txt: cv > 0 ? 'buyers' : cv < 0 ? 'sellers' : 'even' };
    var up = 0, dn = 0, tot = 0;
    ROWS.forEach(function (r) { var x = cells[r[0]].v; if (x === null) return; tot++; if (x > 0) up++; else if (x < 0) dn++; });
    return { cells: cells, up: up, dn: dn, n: tot, dpx: c[n] / c[n - P.pxN] - 1, relVol: v[n] / mean(v, n - P.volN, n - 1), t: t[n] };
  }

  // Plain sentences, most useful first (at most 3). cls: up / down / amber / dim.
  function says(R) {
    var out = [], a = R['15m'], b = R['1h'], q = a || b, nm = a ? '15m' : '1h';
    if (q && q.cells.vfi.v !== null && q.cells.cvd.v !== null) {
      var f = q.cells.vfi, cv = q.cells.cvd.v, d = Math.abs(q.dpx) < P.flat ? 0 : sgn(q.dpx), back = f.rising === d && cv === d, why = [];
      if (f.rising !== d) why.push('flow ' + (f.rising > 0 ? 'rising' : f.rising < 0 ? 'falling' : 'flat'));
      if (cv !== d) why.push(cv > 0 ? 'buyers lead the tape' : cv < 0 ? 'sellers lead the tape' : 'tape even');
      if (d > 0) out.push(back ? { cls: 'up', t: nm + ' rise is backed by volume: flow rising, buyers lead' } : { cls: 'amber', t: nm + ' rise is NOT backed by volume (' + why.join(', ') + '): fade risk' });
      else if (d < 0) out.push(back ? { cls: 'down', t: nm + ' fall is backed by volume: flow falling, sellers lead' } : { cls: 'amber', t: nm + ' fall is NOT backed by volume (' + why.join(', ') + '): bounce risk' });
      else out.push(f.rising === cv && cv ? { cls: cv > 0 ? 'up' : 'down', t: nm + ' price flat while flow is ' + (cv > 0 ? 'rising and buyers lead: quiet buying' : 'falling and sellers lead: quiet selling') }
        : { cls: 'dim', t: nm + ' price flat, volume mixed (flow ' + (f.rising > 0 ? 'rising' : f.rising < 0 ? 'falling' : 'flat') + ', ' + (cv > 0 ? 'buyers' : cv < 0 ? 'sellers' : 'nobody') + ' lead the tape)' });
      if (isFinite(q.relVol) && q.relVol >= 2 && out.length) out[0].t += '; last bar ' + q.relVol.toFixed(1) + 'x normal volume';
    }
    var tr = [a && a.cells.adx, b && b.cells.adx].filter(function (x) { return x && x.v !== null; }), tn = [a && a.cells.adx.v !== null ? '15m' : '', b && b.cells.adx.v !== null ? '1h' : ''].filter(Boolean).join(' or ');
    if (tr.length && tr.every(function (x) { return x.adx < P.adxTrend; })) out.push({ cls: 'dim', t: 'No trend on ' + tn + ' (ADX ' + tr.map(function (x) { return Math.round(x.adx); }).join(' / ') + '): range, levels matter more than indicators' });
    else if (b && b.cells.adx.v) out.push({ cls: b.cells.adx.v > 0 ? 'up' : 'down', t: '1h trend ' + (b.cells.adx.v > 0 ? 'up' : 'down') + (b.cells.adx.strong ? ', strong' : ', weak') + ' (ADX ' + Math.round(b.cells.adx.adx) + ')' });
    var co = TFS.filter(function (x) { return R[x[0]] && R[x[0]].cells.sqz.on; }).map(function (x) { return x[0]; });
    var rl = TFS.filter(function (x) { return R[x[0]] && R[x[0]].cells.sqz.rel >= 0; }).map(function (x) { return x[0] + ' ' + (R[x[0]].cells.sqz.v > 0 ? 'up' : 'down'); });
    if (rl.length) out.push({ cls: 'amber', t: 'Squeeze just released: ' + rl.join(', ') });
    else if (co.length) out.push({ cls: 'amber', t: co.join(' + ') + ' coiled (squeeze on): a fast move is loading, direction unknown' });
    return out.slice(0, 3);
  }

  // One plain verdict per timeframe (operator 11-12: the 6-row grid was unreadable). Counts the six cells already read:
  // side = buyers / sellers / mixed (a lead of 2 or more cells wins; OURS), coiled = squeeze on (quiet before a move).
  function verdict(R) {
    if (!R) return null;
    var lead = R.up - R.dn, side = lead >= 2 ? 1 : lead <= -2 ? -1 : 0;
    return { side: side, up: R.up, dn: R.dn, n: R.n, coiled: !!(R.cells.sqz && R.cells.sqz.on),
      word: side > 0 ? 'buyers winning' : side < 0 ? 'sellers winning' : 'mixed, no one winning' };
  }

  function table(TFK, now) {
    var R = {};
    TFS.forEach(function (x) { try { R[x[0]] = read(TFK && TFK[x[0]], x[1], now); } catch (e) { R[x[0]] = null; } });
    var q = R['15m'], age = q && now > 0 ? now - (q.t + 900000) : NaN;   // ms since the last 15m bar closed
    var V = {}; TFS.forEach(function (x) { V[x[0]] = verdict(R[x[0]]); });
    return { tfs: TFS, rows: ROWS, r: R, ver: V, says: says(R), age: age, stale: isFinite(age) && age > P.staleMs };
  }

  var api = { P: P, TFS: TFS, ROWS: ROWS, adx: adx, squeeze: squeeze, vfi: vfi, read: read, says: says, verdict: verdict, table: table };
  if (node) module.exports = api; else root.LAIND = api;
})(typeof window !== 'undefined' ? window : this);
