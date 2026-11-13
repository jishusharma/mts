// ADX / DI strip (R26): Wilder ADX(14), +DI, -DI per timeframe 1w..5m, last CLOSED bar plus the forming bar dimmer.
// Descriptive only: gates nothing, no orders. Fail closed: too few bars = null (a dash), never a guess.
// Definition: backtest/layers/adx/adx.py (FORMULAS.md section 30, VERIFIED-TV 2026-11-07); this file must equal it (test_adx_strip.py).
// Evidence and "how to use": research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md (no fee-net edge for a DI cross on any frame).
// SOURCED: n = 14 and the 25 trend level (Wilder; masters in MASTERS_1113.md). OURS: the 20 and 40 levels (as in MEASURE/HOW_TO), arrow = ADX vs 3 bars ago,
// "through 25" = ADX crossed up through 25 within the last 3 closed bars, DI cross shown within 10 bars, 2d/3d/5d folded from daily bars on
// epoch-day buckets anchored 1970-01-01 (same as tf_resample.py and the census/measure numbers; 1w Monday-anchored). The fold anchor is OURS.
// Kline rows are the Binance shape [openTime,o,h,l,c,vol,closeTime,...] from data-api.binance.vision spot.
(function (root) {
  'use strict';
  var BASE = 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT';
  var N = 14, DAY = 86400000, LIMIT = 1000;
  var LV_NONE = 20, LV_TREND = 25, LV_STRETCH = 40, ARROW_BARS = 3, THROUGH_BARS = 3, CROSS_BARS = 10;
  // tf -> [feed interval, fold days or 0]
  var TFS = ['1w', '5d', '3d', '2d', '1d', '4h', '1h', '15m', '5m'];
  var SRC = { '1w': ['1w', 0], '5d': ['1d', 5], '3d': ['1d', 3], '2d': ['1d', 2], '1d': ['1d', 0], '4h': ['4h', 0], '1h': ['1h', 0], '15m': ['15m', 0], '5m': ['5m', 0] };
  var USE = { '1w': 'regime read, thin data', '5d': 'regime read, thin data', '3d': 'regime read, untested', '2d': 'regime read, thin data',
    '1d': 'filter: through 25', '4h': 'context only, underpowered', '1h': 'filter only', '15m': 'do not use', '5m': 'do not use' };
  var FAST = { '4h': 1, '1h': 1, '15m': 1, '5m': 1 };

  function num(x) { var v = typeof x === 'number' ? x : parseFloat(x); return isFinite(v) ? v : null; }

  // Wilder ADX/DI, a line-for-line twin of adx.py adx_di: returns {dip, dim, adx}, arrays as long as the bars, null where undefined.
  function adxSeries(bars, n) {
    n = n || N;
    var m = bars ? bars.length : 0, dip = new Array(m), dim = new Array(m), adx = new Array(m), i, k;
    for (i = 0; i < m; i++) { dip[i] = null; dim[i] = null; adx[i] = null; }
    if (m < n + 1) return { dip: dip, dim: dim, adx: adx };
    var h = [], l = [], c = [];
    for (i = 0; i < m; i++) {
      var b = bars[i];
      h.push(Array.isArray(b) ? num(b[2]) : null); l.push(Array.isArray(b) ? num(b[3]) : null); c.push(Array.isArray(b) ? num(b[4]) : null);
      if (h[i] === null || l[i] === null || c[i] === null) return { dip: dip, dim: dim, adx: adx };   // unreadable bar: fail closed
    }
    var tr = [], pdm = [], mdm = [];
    for (i = 1; i < m; i++) {
      tr.push(Math.max(h[i] - l[i], Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1])));
      var up = h[i] - h[i - 1], dn = l[i - 1] - l[i];
      pdm.push(up > dn && up > 0 ? up : 0); mdm.push(dn > up && dn > 0 ? dn : 0);
    }
    var sTr = 0, sP = 0, sM = 0, dx = [];
    for (i = 0; i < n; i++) { sTr += tr[i]; sP += pdm[i]; sM += mdm[i]; }
    for (k = n - 1; k < m - 1; k++) {
      if (k >= n) { sTr = sTr - sTr / n + tr[k]; sP = sP - sP / n + pdm[k]; sM = sM - sM / n + mdm[k]; }
      i = k + 1;
      if (sTr <= 0) { dip[i] = 0; dim[i] = 0; } else { dip[i] = 100 * sP / sTr; dim[i] = 100 * sM / sTr; }
      var tot = dip[i] + dim[i];
      dx.push(tot > 0 ? 100 * Math.abs(dip[i] - dim[i]) / tot : 0);
      if (dx.length === n) { var s = 0; for (var j = 0; j < n; j++) s += dx[j]; adx[i] = s / n; }
      else if (dx.length > n) adx[i] = (adx[i - 1] * (n - 1) + dx[dx.length - 1]) / n;
    }
    return { dip: dip, dim: dim, adx: adx };
  }

  // Fold daily kline rows into nDays buckets: epoch-day bucket start = floor(epochDay / nDays) * nDays (anchor 1970-01-01, OURS).
  // A first bucket that starts before the data is dropped; the last bucket may be partial (its closeTime is still the bucket end, so it reads as forming).
  function fold(dailyBars, nDays) {
    var out = [], cur = null, curB = null, first = true;
    (dailyBars || []).forEach(function (k) {
      var t = num(k && k[0]), o = num(k && k[1]), h = num(k && k[2]), l = num(k && k[3]), c = num(k && k[4]);
      if (t === null || o === null || h === null || l === null || c === null) return;
      var day = Math.floor(t / DAY), b = Math.floor(day / nDays) * nDays;
      if (b !== curB) {
        if (cur) out.push(cur);
        curB = b;
        cur = (first && day !== b) ? null : [b * DAY, o, h, l, c, num(k[5]) || 0, (b + nDays) * DAY - 1];
        first = false;
        return;
      }
      if (!cur) return;
      cur[2] = Math.max(cur[2], h); cur[3] = Math.min(cur[3], l); cur[4] = c; cur[5] += num(k[5]) || 0;
    });
    if (cur) out.push(cur);
    return out;
  }

  // Last bar is forming when its closeTime (k[6]) has not passed.
  function closedOf(bars, now) {
    if (!bars || !bars.length) return { closed: [], forming: false };
    var last = bars[bars.length - 1], cl = num(last[6]);
    var forming = cl !== null && cl >= now;
    return { closed: forming ? bars.slice(0, bars.length - 1) : bars.slice(), forming: forming };
  }

  function chipOf(adx, rising, falling) {
    if (adx === null) return null;
    if (adx < LV_NONE) return 'NO TREND';
    if (adx >= LV_STRETCH && falling) return 'STRETCHED';
    if (adx >= LV_TREND) return 'TREND';
    return rising ? 'BUILDING' : 'WEAK';   // 20-25 and not rising: WEAK (ours: the spec chip set has no word for it)
  }

  // State of the last bar of a series {dip, dim, adx}; null when ADX is not defined there.
  function rowState(s) {
    if (!s || !s.adx || !s.adx.length) return null;
    var L = s.adx.length - 1, a = s.adx[L], p = s.dip[L], q = s.dim[L];
    if (a === null || p === null || q === null) return null;
    var ago = L - ARROW_BARS >= 0 ? s.adx[L - ARROW_BARS] : null;
    var arrow = ago === null ? null : a > ago ? 'up' : a < ago ? 'down' : 'flat';
    var through = false, i;
    for (i = Math.max(1, L - THROUGH_BARS + 1); i <= L; i++) if (s.adx[i] !== null && s.adx[i - 1] !== null && s.adx[i - 1] < LV_TREND && s.adx[i] >= LV_TREND) through = true;
    var prev = 0, cross = null;   // same rule as adx.py crosses(): strict sign flip from the last non-zero sign
    for (i = 0; i <= L; i++) {
      if (s.dip[i] === null || s.dim[i] === null) continue;
      var d = s.dip[i] - s.dim[i], sg = d > 0 ? 1 : d < 0 ? -1 : 0;
      if (sg !== 0) { if (prev !== 0 && sg !== prev) cross = { i: i, dir: sg > 0 ? 'green' : 'red' }; prev = sg; }
    }
    var crossAgo = cross ? L - cross.i : null;
    return { adx: a, dip: p, dim: q, winner: p > q ? 'plus' : p < q ? 'minus' : null, lead: Math.abs(p - q), arrow: arrow,
      chip: chipOf(a, arrow === 'up', arrow === 'down'), through25: through,
      diCross: cross && crossAgo <= CROSS_BARS ? { dir: cross.dir, barsAgo: crossAgo } : null };
  }

  // One row from one timeframe's kline rows (already folded when needed). now = ms.
  function row(tf, bars, now) {
    if (!Array.isArray(bars) || !bars.length) return null;
    var co = closedOf(bars, now), st = rowState(adxSeries(co.closed, N));
    if (!st) return null;
    var fm = null;
    if (co.forming) { var all = rowState(adxSeries(bars, N)); if (all) fm = { adx: all.adx, dip: all.dip, dim: all.dim }; }
    st.tf = tf; st.forming = fm; st.use = USE[tf] || ''; st.bars = co.closed.length;
    return st;
  }

  function f1(x) { return x === null || x === undefined || !isFinite(x) ? '—' : x.toFixed(1); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var ARR = { up: '&#8599;', down: '&#8600;', flat: '&rarr;' };

  // Row HTML (symbols over words). r = row() result or null. Pure: no DOM.
  function viewRow(tf, r, err) {
    var use = USE[tf] || '';
    if (!r) return '<tr><td class="tfn">' + tf + '</td><td colspan="4" class="dim">—' + (err ? ' <span class="err">' + esc(err) + '</span>' : '') + '</td><td class="dim">' + esc(use) + '</td></tr>';
    var tot = r.dip + r.dim, pw = tot > 0 ? 100 * r.dip / tot : 50;
    var lead = r.winner === null ? '=' : (r.winner === 'plus' ? '+' : '-') + 'DI ' + r.lead.toFixed(1);
    var chipCls = r.chip === 'TREND' ? 'up' : r.chip === 'BUILDING' ? 'fresh' : r.chip === 'STRETCHED' ? 'down' : '';
    var marks = (r.through25 ? '<span class="mk fresh" title="ADX crossed up through 25 within the last 3 closed bars">&#8593;25</span>' : '') +
      (r.diCross ? '<span class="mk ' + (r.diCross.dir === 'green' ? 'up' : 'down') + '" title="DI cross: ' + (r.diCross.dir === 'green' ? '+DI above -DI' : '-DI above +DI') + '. Not an entry: no fee-net edge measured on any frame">' + (r.diCross.dir === 'green' ? '+&gt;-' : '-&gt;+') + ' ' + r.diCross.barsAgo + 'b</span>' : '');
    var fm = r.forming ? ' <span class="adxf" title="forming bar: ADX ' + f1(r.forming.adx) + ', +DI ' + f1(r.forming.dip) + ', -DI ' + f1(r.forming.dim) + '">(' + f1(r.forming.adx) + ')</span>' : '';
    return '<tr><td class="tfn">' + tf + '</td>' +
      '<td class="num"><b>' + f1(r.adx) + '</b>' + (r.arrow ? '<span class="sl" title="ADX vs 3 bars ago: ' + r.arrow + '">' + ARR[r.arrow] + '</span>' : '') + fm + '</td>' +
      '<td><span class="adxb" title="+DI ' + f1(r.dip) + ' / -DI ' + f1(r.dim) + '"><i class="up" style="width:' + pw.toFixed(0) + '%"></i><i class="down" style="width:' + (100 - pw).toFixed(0) + '%"></i></span> <span class="' + (r.winner === 'plus' ? 'up' : r.winner === 'minus' ? 'down' : 'dim') + '">' + lead + '</span></td>' +
      '<td>' + (r.chip ? '<span class="mk ' + chipCls + '">' + r.chip + '</span>' : '<span class="dim">—</span>') + '</td>' +
      '<td>' + (marks || '<span class="dim">—</span>') + '</td><td class="dim">' + esc(use) + '</td></tr>';
  }

  var CSS = '.adxs{margin-top:14px}.adxs table{font-size:14px}.adxs td{padding:4px 6px;white-space:nowrap}.adxs td.tfn{font-weight:600}.adxs .sl{color:var(--dim);font-size:12px;margin-left:3px}' +
    '.adxs .adxf{color:var(--dim);opacity:.65;font-size:12px}.adxb{display:inline-flex;width:110px;height:8px;border-radius:2px;overflow:hidden;vertical-align:middle;background:var(--line)}.adxb i{display:block;height:100%}.adxb i.up{background:var(--up)}.adxb i.down{background:var(--down)}' +
    '.adxs .note{color:var(--dim);font-size:12px;margin:6px 0 0}';
  var NOTE = 'Higher frames (1w/5d/3d/2d) say whether a trend exists; lower frames only say if the current move is strong; a DI cross is not an entry (measured: no fee-net edge on any frame).';
  var SRC_TIP = 'Wilder ADX(14), +DI, -DI of the last CLOSED bar (dimmer number in brackets = forming bar); arrow = ADX vs 3 bars ago. Bar: green +DI, red -DI, the winner and its lead in points. Chips: NO TREND ADX under 20; WEAK 20-25 not rising; BUILDING 20-25 and rising; TREND 25 or more; STRETCHED 40 or more and falling. Up-25 mark = ADX crossed up through 25 within the last 3 closed bars; DI cross shown within 10 bars. Level 25 is SOURCED (Wilder); 20, 40, the 3-bar arrow, 3-bar and 10-bar windows are OURS. 2d/3d/5d are folded from daily bars on epoch-day buckets anchored 1970-01-01 (OURS; 2d unverified against TradingView, which hides it); 1w Monday-anchored. Spot BTCUSDT from data-api.binance.vision. The use column is the verdict table of research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md. Descriptive only: gates nothing. Refresh 60 s for 4h and lower, 15 min for the rest.';

  function fetchJson(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }); }

  // Panel driver (browser only): fills the panel placeholder (#p-adxs), polls the spot feed, renders.
  function mount() {
    if (typeof document === 'undefined' || typeof fetch === 'undefined') return;
    if (/[?&]replay=fixture(&|$)/.test(location.search)) return;   // replay mode has no network
    var div = document.getElementById('p-adxs');   // placeholder under the Moving averages panel in live_aid.html
    if (!div || document.getElementById('adxs-rows')) return;
    var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    div.innerHTML = '<div class="hd"><h2>ADX / DI</h2><span class="src" title="' + esc(SRC_TIP) + '">DISPLAY ONLY</span><span class="age" id="age-adxs">--</span></div>' +
      '<div class="scroll"><table><thead><tr><th>TF</th><th>ADX</th><th>+DI / -DI</th><th></th><th>marks</th><th>use</th></tr></thead><tbody id="adxs-rows"></tbody></table></div>' +
      '<p class="note">' + esc(NOTE) + '</p><span class="err" id="adxs-err"></span>';
    var R = {}, E = {}, T = {}, cache = {};
    function render() {
      document.getElementById('adxs-rows').innerHTML = TFS.map(function (tf) { return viewRow(tf, R[tf] || null, E[tf]); }).join('');
      var t = T['5m'] || T['1d'];
      document.getElementById('age-adxs').textContent = t ? Math.round((Date.now() - t) / 1000) + 's' : '--';
    }
    function load(tfs) {
      var need = {}, fail = {};
      tfs.forEach(function (tf) { need[SRC[tf][0]] = 1; });
      return Promise.all(Object.keys(need).map(function (iv) {
        return fetchJson(BASE + '&interval=' + iv + '&limit=' + LIMIT).then(function (k) { cache[iv] = k; }, function (e) { cache[iv] = null; fail[iv] = String(e && e.message || e); });
      })).then(function () {
        var now = Date.now();
        tfs.forEach(function (tf) {
          var s = SRC[tf], k = cache[s[0]];
          if (!k) { E[tf] = fail[s[0]] || 'no data'; return; }
          try { R[tf] = row(tf, s[1] ? fold(k, s[1]) : k, now); delete E[tf]; T[tf] = now; } catch (e) { E[tf] = e.message; }
        });
        render();
        var errs = Object.keys(E).map(function (x) { return x + ': ' + E[x]; });
        document.getElementById('adxs-err').textContent = errs.length ? 'Feed problems: ' + errs.join('; ') : '';
      });
    }
    function fast() { return load(TFS.filter(function (t) { return FAST[t]; })); }
    function slow() { return load(TFS.filter(function (t) { return !FAST[t]; })); }
    render(); fast(); slow(); setInterval(fast, 60000); setInterval(slow, 900000); setInterval(render, 5000);
  }

  var api = { BASE: BASE, TFS: TFS, SRC: SRC, USE: USE, N: N, adxSeries: adxSeries, fold: fold, closedOf: closedOf, chipOf: chipOf, rowState: rowState,
    row: row, viewRow: viewRow, mount: mount, NOTE: NOTE };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else {
    root.ADXSTRIP = api;
    if (typeof document !== 'undefined') { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount(); }
  }
})(typeof window !== 'undefined' ? window : this);
