/* Live Aid "Forced moves" panel (requirement R25). One colour-coded SVG: price candles + large-trade bubbles, open interest tinted by bar
   state, CVD. Pure rules first (node-testable, mirrored in flow_collector.py and tested against flow_fixture.json); the DOM part only
   runs in a browser. Thresholds are OURS, fixed in STEPS.md before any outcome was looked at. Context, never a signal.
   Data: Bybit v5 linear kline + open-interest (browser REST), spot taker volume from data-api.binance.vision, and, when
   flow_collector.py runs, flow_feed.js (large perp prints + perp CVD). Without the collector the chart still draws. */
(function () {
  'use strict';
  var FLAT = 0.1;              // percent, the page's existing flat threshold
  var RUN_MIN_BARS = 3, RUN_MIN_OI = 0.5;   // BUILD / UNWIND: >= 3 bars in a row, cumulative OI change >= 0.5 %
  var BIG_USD = 500000;        // large trade: one print >= 500,000 USD notional
  var EPS = 1e-9;
  var TFS = { '5m': { ms: 300000, bybit: '5', oi: '5min', spot: '5m' }, '30m': { ms: 1800000, bybit: '30', oi: '30min', spot: '30m' }, '1h': { ms: 3600000, bybit: '60', oi: '1h', spot: '1h' } };
  var STATES = { NEW_LONGS: ['NEW LONGS', '#3fbf8a', 'solid green'], FORCED_BUYING: ['FORCED BUYING', '#b6d24a', 'hatched green: shorts closing'],
    NEW_SHORTS: ['NEW SHORTS', '#e2665c', 'solid red'], FORCED_SELLING: ['FORCED SELLING', '#e8873a', 'hatched red: longs closing'],
    FLAT: ['FLAT', '#5b6674', 'grey'], NO_DATA: ['NOT_IN_DATA', '#5b6674', 'grey'] };

  function r2(x) { var v = Math.round(x * 100) / 100; return v === 0 ? 0 : v; }
  function ok(x) { return x !== null && x !== undefined && isFinite(x); }
  function pct(a, b) { return ok(a) && ok(b) && a !== 0 ? (b - a) / a * 100 : null; }

  /* (price change %, OI change %, CVD delta) -> {state, taker}. Flat when either change is under 0.1 % in size. */
  function barState(dpx, doi, cvd) {
    var state;
    if (!ok(dpx) || !ok(doi)) state = 'NO_DATA';
    else if (Math.abs(dpx) < FLAT || Math.abs(doi) < FLAT) state = 'FLAT';
    else if (dpx > 0) state = doi > 0 ? 'NEW_LONGS' : 'FORCED_BUYING';
    else state = doi > 0 ? 'NEW_SHORTS' : 'FORCED_SELLING';
    var taker;
    if (state === 'NO_DATA' || !ok(cvd)) taker = 'NOT_IN_DATA';
    else if (state === 'FLAT' || cvd === 0) taker = 'na';
    else taker = (cvd > 0) === (dpx > 0) ? 'agree' : 'disagree';
    return { state: state, taker: taker };
  }

  /* bars [{t,c,oi,cvd}] oldest first -> one entry per bar from index 1 (vs the bar before). */
  function series(bars) {
    var out = [];
    for (var i = 1; i < bars.length; i++) {
      var a = bars[i - 1], b = bars[i], dpx = pct(a.c, b.c), doi = pct(a.oi, b.oi), s = barState(dpx, doi, b.cvd);
      out.push({ i: i, t: b.t, dpx: dpx === null ? null : r2(dpx), doi: doi === null ? null : r2(doi), cvd: ok(b.cvd) ? b.cvd : null, state: s.state, taker: s.taker });
    }
    return out;
  }

  /* Maximal runs of bars whose OI moves the same way; >= 3 bars and |cumulative OI change| >= 0.5 % = BUILD (up) / UNWIND (down). */
  function oiRuns(bars) {
    var runs = [], i = 1, n = bars.length;
    function sgn(k) { var d = pct(bars[k - 1].oi, bars[k].oi); return d === null || d === 0 ? 0 : (d > 0 ? 1 : -1); }
    while (i < n) {
      var s = sgn(i);
      if (!s) { i++; continue; }
      var j = i;
      while (j + 1 < n && sgn(j + 1) === s) j++;
      var base = bars[i - 1], cum = pct(base.oi, bars[j].oi), dpx = pct(base.c, bars[j].c);
      if (j - i + 1 >= RUN_MIN_BARS && (s > 0 ? cum >= RUN_MIN_OI - EPS : cum <= -RUN_MIN_OI + EPS)) {
        runs.push({ kind: s > 0 ? 'BUILD' : 'UNWIND', dir: dpx === null ? 'flat' : (dpx >= FLAT ? 'up' : dpx <= -FLAT ? 'down' : 'flat'),
          bars: j - i + 1, doi: r2(cum), dpx: dpx === null ? null : r2(dpx), start: i, end: j });
      }
      i = j + 1;
    }
    return runs;
  }

  /* State over the last n bars together (base = the bar before them); CVD = sum of their deltas (null if any is missing). */
  function windowState(bars, n) {
    if (bars.length < n + 1) return null;
    var base = bars[bars.length - n - 1], last = bars[bars.length - 1], sum = 0, miss = false;
    for (var k = bars.length - n; k < bars.length; k++) { if (ok(bars[k].cvd)) sum += bars[k].cvd; else miss = true; }
    var dpx = pct(base.c, last.c), doi = pct(base.oi, last.oi), cvd = miss ? null : sum, s = barState(dpx, doi, cvd);
    return { state: s.state, taker: s.taker, dpx: dpx === null ? null : r2(dpx), doi: doi === null ? null : r2(doi), cvd: cvd === null ? null : r2(cvd) };
  }

  /* Closed bars only: Bybit rows are newest first, [startMs, o, h, l, c]; oiMap/cvdMap keyed by bar start. */
  function mergeBars(kl, oiMap, cvdMap, tfMs, now) {
    return kl.map(function (k) { var t = +k[0]; return { t: t, o: +k[1], h: +k[2], l: +k[3], c: +k[4], oi: oiMap && ok(oiMap[t]) ? oiMap[t] : null, cvd: cvdMap && ok(cvdMap[t]) ? cvdMap[t] : null }; })
      .filter(function (b) { return b.t + tfMs <= now; }).sort(function (a, b) { return a.t - b.t; });
  }
  /* Feed older than 2 bars (last closed bar ended more than 2 bars ago) = stale: the panel reads a dash. */
  function stale(bars, tfMs, now) { return !bars.length || now - (bars[bars.length - 1].t + tfMs) > 2 * tfMs; }

  /* Perp CVD per bar from 5 m buckets {bucketStartMs: [buyBtc, sellBtc]}; only bars fully after `since` count. */
  function perpCvd(buckets, bars, tfMs, since) {
    return bars.map(function (b) {
      if (!ok(since) || b.t < since) return null;
      var s = 0;
      for (var t = b.t; t < b.t + tfMs; t += 300000) { var x = buckets && buckets[t]; if (x) s += x[0] - x[1]; }
      return r2(s);
    });
  }

  function sgnTxt(x, d) { return ok(x) ? (x > 0 ? '+' : '') + x.toFixed(d === undefined ? 1 : d) : '-'; }
  function takerWords(e) { return !e || !ok(e.cvd) ? 'CVD not in data' : (e.cvd > 0 ? 'takers buying' : e.cvd < 0 ? 'takers selling' : 'takers even'); }
  /* "FORCED BUYING: price +0.6 %, OI -0.4 %, takers buying" */
  function chipText(e) {
    if (!e || e.state === 'NO_DATA') return 'NOT_IN_DATA';
    return STATES[e.state][0] + ': price ' + sgnTxt(e.dpx) + ' %, OI ' + sgnTxt(e.doi) + ' %, ' + takerWords(e) + (e.taker === 'disagree' ? ' (absorbed)' : '');
  }
  function hhmm(t) { var d = new Date(t); return ('0' + d.getUTCHours()).slice(-2) + ':' + ('0' + d.getUTCMinutes()).slice(-2) + 'Z'; }
  function runLabel(r) { return r.kind + ' ' + sgnTxt(r.doi, 1) + ' % OI, ' + r.bars + ' bars, price ' + sgnTxt(r.dpx, 1) + ' %'; }
  function usdTxt(x) { return x >= 1e6 ? (x / 1e6).toFixed(1) + 'M' : Math.round(x / 1e3) + 'k'; }

  /* model: {tf, bars, runs, trades:[{t,side,usd,px}], cvdLabel} -> SVG string. Three stacked rows on one x axis. */
  function renderSvg(m) {
    var W = 900, H = 520, gl = 58, gr = 8, bars = m.bars || [], n = bars.length;
    if (n < 2) return '<svg viewBox="0 0 ' + W + ' 60" role="img" aria-label="Forced moves chart"><text x="10" y="34" fill="#e0a43a" font-size="16">NOT_IN_DATA: no closed bars</text></svg>';
    var w = (W - gl - gr) / n, ser = series(bars), byI = {};
    ser.forEach(function (e) { byI[e.i] = e; });
    var X = function (i) { return gl + i * w + w / 2; };
    var lo = Math.min.apply(null, bars.map(function (b) { return b.l; })), hi = Math.max.apply(null, bars.map(function (b) { return b.h; }));
    var pT = 52, pB = 232, Py = function (p) { return pB - (p - lo) / (hi - lo || 1) * (pB - pT); };
    var ois = bars.map(function (b) { return b.oi; }).filter(ok), oLo = Math.min.apply(null, ois), oHi = Math.max.apply(null, ois), oT = 262, oB = 352;
    var Oy = function (v) { return oB - (v - oLo) / (oHi - oLo || 1) * (oB - oT); };
    var cum = [], acc = 0;
    bars.forEach(function (b) { if (ok(b.cvd)) { acc += b.cvd; cum.push(acc); } else cum.push(null); });
    var dm = Math.max.apply(null, bars.map(function (b) { return ok(b.cvd) ? Math.abs(b.cvd) : 0; }).concat([1e-9]));
    var cm = Math.max.apply(null, cum.map(function (v) { return ok(v) ? Math.abs(v) : 0; }).concat([1e-9])), cT = 384, cB = 470, cMid = (cT + cB) / 2;
    var sc = Math.max(dm, cm);
    var s = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Forced moves chart: price, open interest, CVD" style="width:100%;height:auto;display:block;background:#0d1013;border-radius:4px">'];
    s.push('<defs>' + ['FORCED_BUYING', 'FORCED_SELLING'].map(function (k) {
      return '<pattern id="fh-' + k + '" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="' + STATES[k][1] + '" fill-opacity=".18"/><rect width="3" height="6" fill="' + STATES[k][1] + '" fill-opacity=".75"/></pattern>'; }).join('') + '</defs>');
    function fillFor(st) { return st === 'FORCED_BUYING' || st === 'FORCED_SELLING' ? 'url(#fh-' + st + ')' : STATES[st][1]; }
    // row labels
    s.push('<text x="4" y="46" fill="#8592a1" font-size="12">Price (USD)</text><text x="4" y="258" fill="#8592a1" font-size="12">Open interest (BTC), bar tint = state</text><text x="4" y="380" fill="#8592a1" font-size="12">' + (m.cvdLabel || 'CVD not in data') + ' (bars = per bar, line = running total)</text>');
    s.push('<text x="' + (gl - 4) + '" y="' + (pT + 4) + '" fill="#8592a1" font-size="11" text-anchor="end">' + Math.round(hi) + '</text><text x="' + (gl - 4) + '" y="' + pB + '" fill="#8592a1" font-size="11" text-anchor="end">' + Math.round(lo) + '</text>');
    // state tint behind OI row and a thin strip under the candles
    bars.forEach(function (b, i) {
      var e = byI[i]; if (!e) return;
      s.push('<rect x="' + (gl + i * w) + '" y="' + oT + '" width="' + w + '" height="' + (oB - oT) + '" fill="' + fillFor(e.state) + '" fill-opacity="' + (e.state === 'FLAT' || e.state === 'NO_DATA' ? 0.25 : 0.55) + '"><title>' + hhmm(b.t) + ' ' + chipText(e) + '</title></rect>');
      s.push('<rect x="' + (gl + i * w) + '" y="' + (pB + 6) + '" width="' + w + '" height="6" fill="' + fillFor(e.state) + '"/>');
    });
    // candles
    bars.forEach(function (b, i) {
      var up = b.c >= b.o, col = up ? '#3fbf8a' : '#e2665c', x = X(i), bw = Math.max(1.5, w * 0.6);
      s.push('<line x1="' + x + '" x2="' + x + '" y1="' + Py(b.h) + '" y2="' + Py(b.l) + '" stroke="' + col + '"/><rect x="' + (x - bw / 2) + '" y="' + Math.min(Py(b.o), Py(b.c)) + '" width="' + bw + '" height="' + Math.max(1, Math.abs(Py(b.o) - Py(b.c))) + '" fill="' + col + '"/>');
    });
    // run brackets
    (m.runs || []).forEach(function (r, k) {
      var x1 = gl + r.start * w + 1, x2 = gl + (r.end + 1) * w - 1, y = 20 + (k % 2) * 14, col = r.dir === 'up' ? '#3fbf8a' : r.dir === 'down' ? '#e2665c' : '#8592a1';
      s.push('<path d="M' + x1 + ' ' + (y + 6) + 'V' + y + 'H' + x2 + 'V' + (y + 6) + '" fill="none" stroke="' + col + '" stroke-width="2"/><text x="' + ((x1 + x2) / 2) + '" y="' + (y - 3) + '" fill="' + col + '" font-size="12" text-anchor="middle">' + runLabel(r) + '</text>');
    });
    // large-trade bubbles
    (m.trades || []).forEach(function (tr) {
      var i = Math.floor((tr.t - bars[0].t) / (bars[1].t - bars[0].t));
      if (i < 0 || i >= n) return;
      var col = tr.side === 'buy' ? '#3fbf8a' : '#e2665c', r = Math.min(18, 4 * Math.sqrt(tr.usd / BIG_USD)), y = Math.max(pT, Math.min(pB, Py(tr.px)));
      s.push('<circle cx="' + X(i) + '" cy="' + y + '" r="' + r.toFixed(1) + '" fill="' + col + '" fill-opacity=".5" stroke="' + col + '"><title>' + hhmm(tr.t) + ' ' + tr.side.toUpperCase() + ' ' + usdTxt(tr.usd) + ' @' + Math.round(tr.px) + '</title></circle>');
    });
    // OI line
    var pts = [];
    bars.forEach(function (b, i) { if (ok(b.oi)) pts.push(X(i).toFixed(1) + ',' + Oy(b.oi).toFixed(1)); });
    if (pts.length > 1) s.push('<polyline points="' + pts.join(' ') + '" fill="none" stroke="#e3e8ee" stroke-width="2"/>');
    s.push('<text x="' + (gl - 4) + '" y="' + (oT + 10) + '" fill="#8592a1" font-size="11" text-anchor="end">' + (ok(oHi) ? Math.round(oHi) : '-') + '</text><text x="' + (gl - 4) + '" y="' + oB + '" fill="#8592a1" font-size="11" text-anchor="end">' + (ok(oLo) ? Math.round(oLo) : '-') + '</text>');
    // CVD bars + running line
    s.push('<line x1="' + gl + '" x2="' + (W - gr) + '" y1="' + cMid + '" y2="' + cMid + '" stroke="#232b35"/>');
    bars.forEach(function (b, i) {
      if (!ok(b.cvd)) return;
      var h = Math.abs(b.cvd) / sc * (cB - cT) / 2, up = b.cvd >= 0;
      s.push('<rect x="' + (X(i) - Math.max(1, w * 0.3)) + '" y="' + (up ? cMid - h : cMid) + '" width="' + Math.max(2, w * 0.6) + '" height="' + Math.max(0.5, h) + '" fill="' + (up ? '#3fbf8a' : '#e2665c') + '" fill-opacity=".8"/>');
    });
    var cp = [];
    cum.forEach(function (v, i) { if (ok(v)) cp.push(X(i).toFixed(1) + ',' + (cMid - v / sc * (cB - cT) / 2).toFixed(1)); });
    if (cp.length > 1) s.push('<polyline points="' + cp.join(' ') + '" fill="none" stroke="#6ea8d9" stroke-width="2"/>');
    if (!cp.length) s.push('<text x="' + (W / 2) + '" y="' + cMid + '" fill="#e0a43a" font-size="14" text-anchor="middle">NOT_IN_DATA</text>');
    // time axis
    var step = Math.max(1, Math.ceil(n / 8));
    bars.forEach(function (b, i) { if (i % step === 0) s.push('<text x="' + X(i) + '" y="' + (H - 18) + '" fill="#8592a1" font-size="11" text-anchor="middle">' + hhmm(b.t) + '</text>'); });
    s.push('</svg>');
    return s.join('');
  }

  /* Text for the 15m/1h footprint tag (id uo-fp-tf). flow = window.LIVEAID_FLOW (collector), old = window.FOOTPRINT_BIAS (footprint_bias_data.js),
     cad = re-read cadence in ms. Fresh = built within 2 x cadence + 2 min. Never shows old numbers silently: stale -> "footprint feed stale since HH:MMZ". */
  function fpLabel(flow, old, now, cad) {
    var lim = 2 * cad + 120000, fp = flow && flow.fp, ft = fp && fp.t, ot = old && old.tf ? old.built_ms : null;
    if (ok(ft) && now - ft <= lim && fp.lines && (fp.lines['15m'] || fp.lines['1h'])) return 'Bybit perp, collector: ' + [fp.lines['15m'], fp.lines['1h']].filter(Boolean).join(' | ');
    if (ok(ot) && now - ot <= lim) return (old.tf['15m'] ? old.tf['15m'].line : '') + ' | ' + (old.tf['1h'] ? old.tf['1h'].line : '');
    var newest = Math.max(ok(ft) ? ft : 0, ok(ot) ? ot : 0);
    return newest ? 'footprint feed stale since ' + hhmm(newest) : 'footprint feed stale: no data (start flow_collector.py)';
  }

  var api = { fpLabel: fpLabel, barState: barState, series: series, oiRuns: oiRuns, windowState: windowState, mergeBars: mergeBars, stale: stale, perpCvd: perpCvd, chipText: chipText,
    runLabel: runLabel, renderSvg: renderSvg, STATES: STATES, TFS: TFS, FLAT: FLAT, BIG_USD: BIG_USD, RUN_MIN_BARS: RUN_MIN_BARS, RUN_MIN_OI: RUN_MIN_OI };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  window.LAFlow = api;

  // ---------------- browser part ----------------
  var SRC = 'Context, not a signal. Tested 2026-11-13: fading forced moves 0/128 cells pass, OI build/unwind did not separate spikes that reverse from those that continue (research edge-forced-move-fade-1113). Bybit v5 linear BTCUSDT kline + open interest; CVD = spot taker volume (data-api.binance.vision: 2 x taker buy - volume) or perp prints from flow_collector.py. Flat under 0.1 %, BUILD/UNWIND = 3+ bars and 0.5 % OI, large trade = 500k USD: OURS (STEPS.md). Missing or older than 2 bars reads a dash.';
  var st = { tf: '1h', cvd: 'spot', data: {}, T: {}, err: {}, feedT: 0 };
  try { var savedTf = localStorage.getItem('la_flow_tf'); st.tf = TFS[savedTf] ? savedTf : '1h'; st.cvd = localStorage.getItem('la_flow_cvd') === 'perp' ? 'perp' : 'spot'; } catch (e) { /* storage unavailable */ }
  function save() { try { localStorage.setItem('la_flow_tf', st.tf); localStorage.setItem('la_flow_cvd', st.cvd); } catch (e) { /* ignore */ } }
  function esc(x) { return String(x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function getJson(url) {
    var ctl = new AbortController(), to = setTimeout(function () { ctl.abort(); }, 8000);
    return fetch(url, { signal: ctl.signal }).then(function (r) { clearTimeout(to); if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
  }
  function loadTf(k) {
    var c = TFS[k], lim = 74;
    var u1 = 'https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=' + c.bybit + '&limit=' + lim;
    var u2 = 'https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime=' + c.oi + '&limit=' + lim;
    var u3 = 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=' + c.spot + '&limit=' + lim;
    return Promise.all([getJson(u1), getJson(u2), getJson(u3).catch(function () { return null; })]).then(function (r) {
      var oi = {}, cv = {};
      r[1].result.list.forEach(function (x) { oi[+x.timestamp] = +x.openInterest; });
      if (r[2]) r[2].forEach(function (x) { cv[+x[0]] = 2 * +x[9] - +x[5]; });
      st.data[k] = { kl: r[0].result.list, oi: oi, cv: r[2] ? cv : null }; st.T[k] = Date.now(); st.err[k] = '';
    }, function (e) { st.err[k] = 'Bybit REST failed: ' + (e.name === 'AbortError' ? 'timeout' : e.message); });
  }
  function loadFeed() {
    var s = document.createElement('script');
    s.src = 'flow_feed.js?_=' + Date.now();
    s.onload = function () { st.feedT = window.LIVEAID_FLOW && window.LIVEAID_FLOW.t || 0; draw(); s.remove(); };
    s.onerror = function () { window.LIVEAID_FLOW = null; st.feedT = 0; draw(); s.remove(); };
    document.head.appendChild(s);
  }
  function css() {
    if (document.getElementById('flow-css')) return;
    var s = document.createElement('style'); s.id = 'flow-css';
    s.textContent = '#flow-root{display:grid;gap:8px}.fl-btn{font:600 13px var(--mono,monospace);padding:4px 12px;border-radius:4px;border:1px solid var(--line,#232b35);background:transparent;color:var(--fg,#e3e8ee);cursor:pointer}.fl-btn.on{background:var(--amber,#e0a43a);color:#0d1013;border-color:var(--amber,#e0a43a)}' +
      '.fl-chip{font:600 20px/1.25 var(--sans,system-ui);padding:8px 12px;border-radius:6px;color:#0d1013}.fl-chip2{font:600 15px/1.25 var(--sans,system-ui);padding:4px 10px;border-radius:5px;color:#0d1013;width:fit-content}' +
      '.fl-lg{display:flex;gap:10px;flex-wrap:wrap;font-size:13px}.fl-lg i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:4px;vertical-align:-1px}.fl-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}';
    document.head.appendChild(s);
  }
  function clone(b, cvd) { var x = {}; for (var k in b) x[k] = b[k]; x.cvd = cvd; return x; }
  function view() {
    var now = Date.now(), c = TFS[st.tf], d = st.data[st.tf], feed = window.LIVEAID_FLOW, fresh = feed && feed.t && now - feed.t <= 90000, out = { notes: [] };
    if (!d) { out.err = st.err[st.tf] || 'loading'; return out; }
    var bars = mergeBars(d.kl, d.oi, d.cv, c.ms, now), cvdLabel = 'spot CVD';
    if (!d.cv) out.notes.push('spot CVD NOT_IN_DATA (data-api.binance.vision unreachable)');
    if (st.cvd === 'perp') {
      if (fresh && feed.perp && feed.perp.since) {
        var pc = perpCvd(feed.perp.b, bars, c.ms, feed.perp.since);
        bars = bars.map(function (b, i) { return clone(b, pc[i]); });
        cvdLabel = 'perp CVD (since ' + hhmm(feed.perp.since) + ')';
      } else { out.notes.push('perp CVD: collector not running'); bars = bars.map(function (b) { return clone(b, null); }); cvdLabel = 'perp CVD (collector not running)'; }
    }
    out.stale = stale(bars, c.ms, now); out.bars = bars; out.cvdLabel = cvdLabel;
    out.runs = oiRuns(bars);
    out.trades = fresh && feed.trades ? feed.trades.filter(function (t) { return t.usd >= BIG_USD; }) : [];
    if (!fresh) out.notes.push('large trades: collector not running');
    return out;
  }
  function chipHtml(e, label, big) {
    var col = e ? STATES[e.state][1] : '#5b6674';
    return '<div class="' + (big ? 'fl-chip' : 'fl-chip2') + '" style="background:' + col + '">' + esc(label) + ': ' + esc(chipText(e)) + '</div>';
  }
  function draw() {
    var root = document.getElementById('flow-root'); if (!root) return;
    var v = view(), h = '<div class="fl-row"><span class="dim">Timeframe</span>' + Object.keys(TFS).map(function (k) { return '<button class="fl-btn' + (k === st.tf ? ' on' : '') + '" data-tf="' + k + '">' + k + '</button>'; }).join('') +
      '<span class="dim" style="margin-left:12px">CVD</span>' + ['spot', 'perp'].map(function (k) { return '<button class="fl-btn' + (k === st.cvd ? ' on' : '') + '" data-cvd="' + k + '">' + k + '</button>'; }).join('') + '</div>';
    if (!v.bars) { root.innerHTML = h + '<div class="nid">NOT_IN_DATA ' + esc(v.err) + '</div>'; wire(root); return; }
    var ser = series(v.bars), last = ser.length ? ser[ser.length - 1] : null;
    if (v.stale) last = null;
    var hr = null, five = st.data['5m'] ? mergeBars(st.data['5m'].kl, st.data['5m'].oi, st.data['5m'].cv, 300000, Date.now()) : null;
    if (five && !stale(five, 300000, Date.now())) hr = windowState(five, 12);
    h += chipHtml(last, st.tf + ' bar ' + (last ? hhmm(last.t) : '-'), true) + chipHtml(hr, 'Last hour', false);
    h += '<div class="fl-lg">' + ['NEW_LONGS', 'FORCED_BUYING', 'NEW_SHORTS', 'FORCED_SELLING', 'FLAT'].map(function (k) {
      var bg = k === 'FORCED_BUYING' || k === 'FORCED_SELLING' ? 'repeating-linear-gradient(45deg,' + STATES[k][1] + ' 0 3px,#1c232b 3px 6px)' : STATES[k][1];
      return '<span><i style="background:' + bg + '"></i>' + STATES[k][0] + '</span>'; }).join('') + '<span class="dim">circle = large trade (green buy, red sell)</span></div>';
    h += renderSvg({ tf: st.tf, bars: v.bars, runs: v.runs, trades: v.trades, cvdLabel: v.cvdLabel });
    if (v.notes.length) h += '<div class="tag">' + esc(v.notes.join(' | ')) + '</div>';
    root.innerHTML = h; wire(root);
    var age = document.getElementById('age-flow'); if (age) { var t0 = st.T[st.tf]; age.textContent = t0 ? Math.round((Date.now() - t0) / 1000) + 's' : '--'; age.classList.toggle('stale', !!v.stale); }
  }
  /* tile(): the Forced moves picture for the one-screen Home (R27): two compact state chips + the same SVG, no buttons. {ok, t, stale, html} */
  api.tile = function () {
    var v = view(), c = TFS[st.tf];
    if (!v.bars) return { ok: false, t: 0, html: '' };
    var ser = series(v.bars), last = ser.length ? ser[ser.length - 1] : null; if (v.stale) last = null;
    var five = st.data['5m'] ? mergeBars(st.data['5m'].kl, st.data['5m'].oi, st.data['5m'].cv, 300000, Date.now()) : null, hr = five && !stale(five, 300000, Date.now()) ? windowState(five, 12) : null;
    var mini = function (e, lab) { var col = e && e.state !== 'NO_DATA' ? STATES[e.state][1] : '#5b6674'; return '<span class="fl-chip2" style="background:' + col + '">' + esc(lab + ' ' + (e && e.state !== 'NO_DATA' ? STATES[e.state][0] + ' ' + sgnTxt(e.dpx) + '% px, ' + sgnTxt(e.doi) + '% OI' : 'no data')) + '</span>'; };
    var h = '<div class="fl-row">' + mini(last, st.tf + ' bar') + mini(hr, 'last hour') + '</div>' + renderSvg({ tf: st.tf, bars: v.bars, runs: v.runs, trades: v.trades, cvdLabel: v.cvdLabel });
    return { ok: true, t: st.T[st.tf] || 0, stale: !!v.stale, html: h };
  };
  function wire(root) {
    Array.prototype.forEach.call(root.querySelectorAll('[data-tf]'), function (b) { b.onclick = function () { st.tf = b.getAttribute('data-tf'); save(); if (!st.data[st.tf]) loadTf(st.tf).then(draw); draw(); }; });
    Array.prototype.forEach.call(root.querySelectorAll('[data-cvd]'), function (b) { b.onclick = function () { st.cvd = b.getAttribute('data-cvd'); save(); draw(); }; });
  }
  /* init({views}): registers the Forced moves view + tab, loads data. Replay mode: no network, the panel reads NOT_IN_DATA. */
  api.init = function (o) {
    css();
    if (o && o.views) o.views.flow = ['p-flow', 'Forced moves'];
    var tabs = document.getElementById('tabs');
    if (tabs && !tabs.hasAttribute('data-onescreen') && !tabs.querySelector('a[href="#flow"]')) { var a = document.createElement('a'); a.href = '#flow'; a.textContent = 'Forced moves'; var m = tabs.querySelector('a[href="#money"]'); tabs.insertBefore(a, m ? m.nextSibling : null); }
    var src = document.querySelector('#p-flow .hd .src'); if (src) src.title = SRC;
    if (/[?&]replay=fixture(&|$)/.test(location.search)) { draw(); return; }
    function cycle() { Object.keys(TFS).forEach(function (k) { if (k === st.tf || k === '5m') loadTf(k).then(draw); }); }
    cycle(); setInterval(cycle, 60000); loadFeed(); setInterval(loadFeed, 30000); draw();
  };
})();
