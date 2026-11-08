// News headline panel helpers (card news-headline-panel-tree-rest-1108; plan N1 + N6 of research/news_feeds_2026-10-30/REPORT.md).
// Context only: no gate, no size, no signal. Pure functions; the page does the fetch, this file decides WHEN and HOW MANY and what a row says.
// SOURCED: Tree News fields time (ms), source, title, url, importance 0-10. OURS: mark at importance >= 7, poll every 15 s while visible,
// 12 rows, 20 items per poll, 300 on the first load or after a gap over 2 min (a hidden tab pauses the poll), N6 word list (kept in live_aid_indicators.js newsTags, not copied).
(function (root) {
  'use strict';
  var LA = (typeof module !== 'undefined' && module.exports) ? require('./live_aid_indicators.js') : root.LiveAid;
  var MARK = 7, EVERY_MS = 15000, ROWS = 12, POLL_LIMIT = 20, FIRST_LIMIT = 300, GAP_MS = 120000;

  function mark(x) { return !!x && isFinite(parseFloat(x.importance)) && parseFloat(x.importance) >= MARK; }
  function tags(title) { return LA ? LA.newsTags(title).filter(function (g) { return g !== 'btc'; }) : []; }
  // hidden: document.hidden. lastAt: ms of the last poll start, 0 = never. The tab pauses while hidden and resumes on the next tick once visible.
  function shouldPoll(hidden, lastAt, now) { return !hidden && (!lastAt || now - lastAt >= EVERY_MS); }
  function fetchLimit(lastOkAt, now) { return (!lastOkAt || now - lastOkAt > GAP_MS) ? FIRST_LIMIT : POLL_LIMIT; }
  function headline(x) { return String(x && x.title || '').split('\n')[0].slice(0, 220); }
  function row(x) {
    var u = String(x.url || ''), imp = parseFloat(x.importance), h = headline(x);
    return { id: x._id, time: x.time, utc: new Date(x.time).toISOString().slice(11, 19), source: x.source || '', score: isFinite(imp) ? imp : null,
      hi: mark(x), headline: h, url: /^https:\/\//.test(u) ? u : '', tags: tags(h) };
  }
  // newest first, items without id or time dropped, one row per _id
  function rows(items, n) {
    var seen = {};
    return (items || []).filter(function (x) { return x && x._id && isFinite(+x.time) && !seen[x._id] && (seen[x._id] = 1); })
      .sort(function (a, b) { return b.time - a.time; }).slice(0, n || ROWS).map(row);
  }

  var api = { MARK: MARK, EVERY_MS: EVERY_MS, ROWS: ROWS, mark: mark, tags: tags, shouldPoll: shouldPoll, fetchLimit: fetchLimit, row: row, rows: rows };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.NEWSFEED = api;
})(typeof window !== 'undefined' ? window : this);
