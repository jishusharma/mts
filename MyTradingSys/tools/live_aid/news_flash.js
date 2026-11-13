// News flash card for the Live Aid home page: one important headline with a little detail, else one quiet line (operator 11-13).
// Context only: descriptive words, no forecast, no advice. Pure functions; the page passes the items and the clock.
// Bar: the existing one. With news_weight fields (w, k) NEWSWEIGHT.qualifies decides (W >= 60 or K = 40); else score >= 7 (NEWS_HI in home.js, MARK in news_feed.js, OURS).
// Item: {id, t (ms), score 0-10, head, tag POSITIVE|NEGATIVE|NEUTRAL|UNKNOWN} and optional {source, url, cls, w, k}.
(function (root) {
  'use strict';
  var NW = (typeof module !== 'undefined' && module.exports) ? require('./news_weight.js') : root.NEWSWEIGHT;
  var HOUR = 3600000, MARK = 7, HEAD_MAX = 160;
  var KIND = { MACRO_CPI: 'Macro data', MACRO_NFP: 'Macro data', MACRO_PPI: 'Macro data', FOMC: 'Fed decision', BOJ_JAPAN: 'Bank of Japan',
    ETF_REGULATORY: 'ETF flows / regulation', HACK_EXPLOIT: 'Exchange / hack', GEOPOLITICS: 'War / geopolitics', TARIFF_TRADE: 'Tariffs / trade',
    COURT_LEGAL: 'Court / legal', PROTOCOL: 'Protocol change', TRUMP_POLICY: 'US policy', OTHER: 'General news' };

  function num(x) { return typeof x === 'number' && isFinite(x); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function hasW(x) { return num(x.w); }
  function important(x, now) {
    if (hasW(x) && NW && NW.qualifies) return NW.qualifies({ time: x.t, w: x.w, k: x.k }, now);
    return num(x.score) && x.score >= MARK;
  }
  function rank(x) { return hasW(x) ? x.w : (num(x.score) ? x.score * 10 : 0); }
  function recent(items, now) {
    return (items || []).filter(function (x) { return x && num(x.t) && x.t <= now && now - x.t <= HOUR; });
  }
  function pick(items, now) {
    var r = recent(items, now), imp = r.filter(function (x) { return important(x, now); })
      .sort(function (a, b) { return rank(b) - rank(a) || b.t - a.t; });
    return { top: imp[0] || null, also: imp.slice(1, 3), minor: r.length - imp.length, quiet: !imp.length, total: r.length };
  }
  function firstLine(s) { return String(s || '').split('\n')[0]; }
  function cut(s, n) { return s.length <= n ? s : s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…'; }
  function ageText(ms) {
    var m = Math.max(0, Math.floor(ms / 60000));
    return m < 1 ? 'just now' : m + ' min ago';
  }
  function lean(tag) { return tag === 'POSITIVE' ? 'good for BTC' : tag === 'NEGATIVE' ? 'bad for BTC' : 'unclear'; }
  function detail(x, now) {
    var head = firstLine(x.head), cls = x.cls || (NW ? NW.classify(head) : 'OTHER'), lm = NW && NW.lastMove ? NW.lastMove(cls) : null, past = '';
    if (lm) past = 'Past: last ' + (KIND[cls] || 'similar').toLowerCase() + ' headline of this type (' + lm.date + '): BTC ' + (lm.r15 > 0 ? '+' : '') + lm.r15.toFixed(1) + '% in 15 min';
    return { head: cut(head, HEAD_MAX), kind: KIND[cls] || KIND.OTHER, lean: lean(x.tag), age: ageText(now - x.t), source: x.source || '', past: past };
  }
  function arrow(tag) { return tag === 'POSITIVE' ? ['up', '▲'] : tag === 'NEGATIVE' ? ['down', '▼'] : ['amber', '◆']; }
  function html(items, now) {
    var p = pick(items, now), link = '<div class="nf-link"><a href="#news">all ' + p.total + ' headline' + (p.total === 1 ? '' : 's') + '</a></div>', out, d, a;
    if (p.quiet) return '<div class="nf-quiet">Nothing important in the last hour (' + p.minor + ' minor headline' + (p.minor === 1 ? '' : 's') + ')</div>' + link;
    d = detail(p.top, now); a = arrow(p.top.tag);
    out = '<div class="nf-top"><span class="nf-ar nf-' + a[0] + '">' + a[1] + '</span><span class="nf-head">' + esc(d.head) + '</span></div>' +
      '<div class="nf-meta">' + [d.kind, d.lean, d.age, d.source].filter(Boolean).map(esc).join(' · ') + '</div>' +
      (d.past ? '<div class="nf-past">' + esc(d.past) + '</div>' : '');
    p.also.forEach(function (x) {
      var dd = detail(x, now), b = arrow(x.tag);
      out += '<div class="nf-also"><span class="nf-ar nf-' + b[0] + '">' + b[1] + '</span><span class="nf-ah">' + esc(cut(dd.head, 90)) + '</span><span class="nf-age">' + esc(dd.age) + '</span></div>';
    });
    return out + link;
  }
  var CSS = '.nf-top{display:flex;gap:8px;align-items:flex-start;color:var(--fg);line-height:1.35}' +
    '.nf-ar{flex:none}.nf-up{color:var(--up)}.nf-down{color:var(--down)}.nf-amber{color:var(--amber)}' +
    '.nf-head{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}' +
    '.nf-meta,.nf-past,.nf-quiet,.nf-link{color:var(--dim);font-size:12px;margin-top:4px}' +
    '.nf-also{display:flex;gap:6px;color:var(--dim);font-size:12px;margin-top:4px;border-top:1px solid var(--line);padding-top:4px}' +
    '.nf-ah{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.nf-age{flex:none}' +
    '.nf-link a{color:var(--dim)}';
  var api = { MARK: MARK, KIND: KIND, CSS: CSS, pick: pick, detail: detail, html: html };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.NEWSFLASH = api;
})(typeof window !== 'undefined' ? window : this);
