// Pre-US-open risk flag (card premarket-risk-flag-1105). Descriptive only: no size, no orders.
// Thresholds are OURS, from the 11-05 case (NQ -0.6%, Kospi -5.3%, BTC 80.4k -> 75.6k).
// Pure functions: quotes in, flag out. Fail closed: a missing or malformed quote is UNKNOWN, never a calm OFF.
(function (root) {
  'use strict';
  var PM = { nqPct: -0.5, kospiPct: -3, winEndMin: 14 * 60 + 30, outcomeMs: 4 * 3600000, maxMovers: 3 };
  // Public no-key quote endpoint behind one fetch function (OURS). Browsers may block it (CORS): then every quote is null -> UNKNOWN.
  var SYMBOLS = { NQ: 'NQ=F', KOSPI: '^KS11', VIX: '^VIX' };
  var CHIPS = ['QCOM', 'NVDA', 'AMD', 'AVGO', 'MU', 'INTC', 'TSM', 'ASML', 'ARM', 'MRVL'];

  function pct(q) {
    if (!q || typeof q !== 'object') return null;
    var p = q.price, v = q.prev;
    if (typeof p !== 'number' || typeof v !== 'number' || !isFinite(p) || !isFinite(v) || v <= 0) return null;
    return 100 * (p - v) / v;
  }
  function inWindow(now) {
    if (typeof now !== 'number' || !isFinite(now)) return false;
    var d = new Date(now), dow = d.getUTCDay();
    if (dow === 0 || dow === 6) return false;
    return d.getUTCHours() * 60 + d.getUTCMinutes() < PM.winEndMin;
  }
  function evaluate(quotes, now) {
    quotes = quotes || {};
    var nq = pct(quotes.NQ), ko = pct(quotes.KOSPI);
    var out = { flag: 'UNKNOWN', reasons: [], why: '', nq: nq, kospi: ko, vix: null, movers: [] };
    var v = quotes.VIX;
    if (v && typeof v.price === 'number' && isFinite(v.price)) out.vix = { price: v.price, pct: pct(v) };
    out.movers = (Array.isArray(quotes.movers) ? quotes.movers : []).map(function (m) {
      return { sym: String((m && m.sym) || '?'), pct: pct(m) };
    }).filter(function (m) { return m.pct !== null; })
      .sort(function (a, b) { return Math.abs(b.pct) - Math.abs(a.pct); }).slice(0, PM.maxMovers);
    if (!inWindow(now)) { out.why = 'Outside the pre-US-open window (weekdays before 14:30Z): no flag read.'; return out; }
    if (nq !== null && nq < PM.nqPct) out.reasons.push('Nasdaq-100 futures ' + nq.toFixed(2) + '% vs prior close (< ' + PM.nqPct + '%)');
    if (ko !== null && ko < PM.kospiPct) out.reasons.push('Kospi ' + ko.toFixed(2) + '% vs prior close (< ' + PM.kospiPct + '%)');
    if (out.reasons.length) { out.flag = 'ON'; return out; }
    if (nq === null || ko === null) {
      out.why = 'Quote missing or unreadable: ' + (nq === null ? 'Nasdaq-100 futures' : '') + (nq === null && ko === null ? ', ' : '') + (ko === null ? 'Kospi' : '') + '. Not shown as OFF.';
      return out;
    }
    out.flag = 'OFF';
    return out;
  }
  function dayOf(t) { return Math.floor(t / 86400000); }
  // Local log: one ON entry per UTC day, BTC price at the flag, BTC 4h later filled in by fillOutcomes.
  function logFlag(log, f, now, btc) {
    log = Array.isArray(log) ? log.slice() : [];
    if (!f || f.flag !== 'ON' || typeof now !== 'number') return log;
    for (var i = 0; i < log.length; i++) if (dayOf(log[i].t) === dayOf(now)) return log;
    var b = typeof btc === 'number' && isFinite(btc) && btc > 0 ? btc : null;
    log.push({ t: now, reasons: f.reasons.slice(), nq: f.nq, kospi: f.kospi, btc0: b, btc4h: null, btc4hPct: null });
    return log;
  }
  function fillOutcomes(log, now, btc) {
    var b = typeof btc === 'number' && isFinite(btc) && btc > 0 ? btc : null;
    return (Array.isArray(log) ? log : []).map(function (e) {
      var o = Object.assign({}, e);
      if (o.btc4h === null && b !== null && o.btc0 && now - o.t >= PM.outcomeMs) {
        o.btc4h = b; o.btc4hPct = 100 * (b - o.btc0) / o.btc0;
      }
      return o;
    });
  }
  // One quote from the Yahoo chart JSON; anything else -> null.
  function parseQuote(j) {
    try {
      var m = j.chart.result[0].meta;
      var price = +m.regularMarketPrice, prev = +(m.chartPreviousClose != null ? m.chartPreviousClose : m.previousClose);
      return isFinite(price) && isFinite(prev) && prev > 0 ? { price: price, prev: prev } : null;
    } catch (e) { return null; }
  }
  function quoteUrl(sym) { return 'https://query1.finance.yahoo.com/v8/finance/chart/' + encodeURIComponent(sym) + '?range=1d&interval=1d'; }
  // The only network function. Resolves to the quotes object; a failed symbol is null (UNKNOWN downstream).
  function fetchQuotes(fetchFn) {
    var f = fetchFn || (typeof fetch === 'function' ? fetch : null);
    function one(sym) {
      if (!f) return Promise.resolve(null);
      return Promise.resolve().then(function () { return f(quoteUrl(sym)); })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(parseQuote).catch(function () { return null; });
    }
    var keys = Object.keys(SYMBOLS);
    return Promise.all(keys.map(function (k) { return one(SYMBOLS[k]); })
      .concat(CHIPS.map(function (s) { return one(s).then(function (q) { return q ? { sym: s, price: q.price, prev: q.prev } : null; }); })))
      .then(function (a) {
        var q = {}; keys.forEach(function (k, i) { q[k] = a[i]; });
        q.movers = a.slice(keys.length).filter(Boolean);
        return q;
      });
  }
  var api = { PM: PM, evaluate: evaluate, inWindow: inWindow, logFlag: logFlag, fillOutcomes: fillOutcomes, parseQuote: parseQuote, fetchQuotes: fetchQuotes };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.PREMARKET = api;
})(typeof window !== 'undefined' ? window : this);
