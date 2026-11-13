// Live Aid ONE-SCREEN Home (requirement R27, operator 2026-11-13 19:05Z: "we just need the home screen").
// A grid of tiles: numbers and coloured chips first, 8 words or fewer per cell, every how-to sentence in a hover title.
// Every tile carries ONE age stamp (.o1-age) and turns an amber STALE chip when its feed is older than its limit.
// Data logic stays in the existing modules (home.js model / chart / board / stories, adx_strip.js, flow_chart.js, live_aid_indicators.js newsRead);
// this file only lays it out and adds three small OURS rules: band width (Bollinger 20, 2 SD) on 15m / 1h, the news filter
// (BTC or whole market AND a matched word rule) with a BUILDING / FADING trend, and the Ahead calendar list.
// Observation only: chips describe state, never an order, size or entry. The old Home stays (home.js render) under Details > Previous Home.
(function (root) {
  'use strict';
  var G = typeof globalThis !== "undefined" ? globalThis : root;
  var isNode = typeof module !== 'undefined' && module.exports;
  function req(p) { if (!isNode) return null; try { return require(p); } catch (e) { return null; } }
  var LH = isNode ? req('./home.js') : root.LAHOME;
  var LA = isNode ? req('./live_aid_indicators.js') : root.LiveAid;
  var AX = isNode ? req('./adx_strip.js') : root.ADXSTRIP;
  var SB = isNode ? req('./setup_board.js') : root.LASB;
  var MIN = 60000, HOUR = 3600000, DAY = 86400000;
  // feed limits (ms) before the amber STALE chip: price 30 s (page badge turns amber at 15 s), OI 90 s (A.OM.staleMs), news 120 s (poll gap rule),
  // candles 180 s, forced-moves bars 15 min (5m bars, 2 bars), calendar 26 h (CAL_MAX_AGE). OURS.
  var LIMIT = { price: 30000, oi: 90000, news: 120000, candles: 180000, flow: 900000, cal: 26 * HOUR };
  var NEWS_MAX = 10;   // Tree News importance scale 0-10 (SOURCED, REPORT.md section 3); top band = 7 and up (OURS mark, live_aid_indicators NW.mark)
  var NEWS_ROWS = 5, NEWS_DROP_MS = 2 * HOUR, TREND_MS = 30 * MIN;
  var CLI_CAL = 'python scripts/dev/ff_calendar_snapshot.py';

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n0(x) { return isFinite(x) ? Math.round(x).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '--'; }
  function sg(x, d) { return isFinite(x) ? (x > 0 ? '+' : '') + x.toFixed(d == null ? 1 : d) : '--'; }
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function hhmm(t) { var d = new Date(t); return two(d.getUTCHours()) + ':' + two(d.getUTCMinutes()); }
  function ist(t) { return hhmm(t + 330 * MIN); }
  var DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // ---------- age stamps ----------
  function ageWord(ms) { var s = Math.max(0, Math.round(ms / 1000)); return s < 90 ? s + 's' : s < 5400 ? Math.round(s / 60) + 'm' : s < 172800 ? Math.round(s / 3600) + 'h' : Math.round(s / 86400) + 'd'; }
  // t = last good update (ms, 0 = never), limit = ms. Returns {html, stale}
  function age(t, now, limit, name) {
    var ok = t > 0, a = ok ? now - t : NaN, stale = !ok || a > limit;
    var txt = !ok ? 'STALE no data' : stale ? 'STALE ' + ageWord(a) : ageWord(a) + ' ago';
    return { stale: stale, html: '<span class="o1-age' + (stale ? ' stale' : '') + '" data-feed="' + esc(name) + '" title="' + esc((name || 'feed') + ': ' + (ok ? 'updated ' + ageWord(a) + ' ago' : 'no update yet') + '; amber STALE after ' + ageWord(limit)) + '">' + txt + '</span>' };
  }
  function tile(id, title, help, ageHtml, body, cls) {
    return '<div class="o1-tile ' + (cls || '') + '" id="o1-' + id + '" data-tile="' + id + '"><div class="o1-h"><b>' + esc(title) + '</b><span class="o1-q" tabindex="0" title="' + esc(help) + '">?</span>' + ageHtml + '</div><div class="o1-b">' + body + '</div></div>';
  }
  function chip(txt, c, title) { return '<span class="o1-c ' + (c || 'dim') + '"' + (title ? ' title="' + esc(title) + '"' : '') + '>' + esc(txt) + '</span>'; }
  var nid = function (t) { return '<div class="o1-nid">' + esc(t) + '</div>'; };

  // ---------- Bollinger band width (OURS) ----------
  // width = (upper - lower) / middle = 4 x population SD / SMA, BB(20, 2) on CLOSED bars; percentile = share of the last <= 200 widths at or under the latest.
  // rows: Binance klines [t, o, h, l, c, v, closeT]; a last bar whose closeT is still ahead of now is forming and left out.
  function bbWidth(rows, now, n) {
    n = n || 20; if (!Array.isArray(rows) || !rows.length) return null;
    var last = rows[rows.length - 1], r = rows;
    if (last && +last[6] > now) r = rows.slice(0, rows.length - 1);
    var c = r.map(function (x) { return +x[4]; }).filter(function (x) { return isFinite(x) && x > 0; });
    if (c.length < n) return null;
    var w = [];
    for (var i = n - 1; i < c.length; i++) {
      var m = 0, k; for (k = i - n + 1; k <= i; k++) m += c[k]; m /= n;
      var v = 0; for (k = i - n + 1; k <= i; k++) v += (c[k] - m) * (c[k] - m);
      w.push(4 * Math.sqrt(v / n) / m);
    }
    var hist = w.slice(-200), cur = w[w.length - 1], below = hist.filter(function (x) { return x <= cur + 1e-12; }).length;
    var pct = hist.length >= 30 ? below / hist.length : null;
    return { width: cur, pct: pct, n: hist.length, coil: pct !== null && pct <= 0.2 };
  }

  // ---------- news that matters (R27 point 3) ----------
  var EXCH = /\b(binance|coinbase|kraken|bybit|okx|bitfinex|bitstamp|deribit)\b/i;
  var BTCW = /\b(bitcoin|btc)\b/i;
  function coinsOf(x) { return ((x && x.suggestions) || []).map(function (c) { return String(c && typeof c === 'object' ? c.coin : c || '').toUpperCase(); }).filter(Boolean); }
  // One headline -> {chip, coin, key} or null. chip UP / DOWN / VOLATILE comes ONLY from newsRead's matched word rule (SOURCED reading, OURS words); no rule = null.
  function classify(x) {
    if (!x || !LA) return null;
    var t = String(x.title || '').split('\n')[0], r = LA.newsRead(x), coins = coinsOf(x), btc = BTCW.test(t) || coins.indexOf('BTC') >= 0, other = coins.length > 0 && !btc;
    var rule = /^word rule: /.test(r.why) ? r.why.slice(11) : '';
    if (!rule) return null;
    var chipv = r.tag === 'POSITIVE' ? 'UP' : r.tag === 'NEGATIVE' ? 'DOWN' : rule === 'macro' ? 'VOLATILE' : null;
    if (!chipv) return null;
    var wide = rule === 'macro' || rule === 'war';   // scheduled / geopolitical news moves the whole market
    var market = btc || wide || ((rule === 'etf up' || rule === 'etf down') && !other) || ((rule === 'hack' || rule === 'halt') && EXCH.test(t) && !other);
    if (other && !wide) market = false;
    if (!market) return null;
    return { chip: chipv, coin: btc ? 'BTC' : 'MKT', key: rule };
  }
  // Last BTC % change since the headline: from the 1m bar that holds the headline time (its open) to px.
  function sinceHeadline(rows1m, t, px) {
    if (!Array.isArray(rows1m) || !rows1m.length || !(px > 0)) return null;
    if (t < +rows1m[0][0] || t >= +rows1m[rows1m.length - 1][0] + MIN) return null;
    var o = null; for (var i = rows1m.length - 1; i >= 0; i--) if (+rows1m[i][0] <= t) { o = +rows1m[i][1]; break; }
    return o > 0 ? (px / o - 1) * 100 : null;
  }
  // items: Tree rows {_id,time,title,importance,suggestions}. Returns up to 5 rows newest first.
  function newsRows(items, now, rows1m, px) {
    var by = {}, cls = [];
    (items || []).forEach(function (x) {
      if (!x || !isFinite(+x.time) || +x.time > now) return;
      var c = classify(x); if (!c) return;
      cls.push({ x: x, c: c });
    });
    cls.forEach(function (e) { (by[e.c.key] = by[e.c.key] || []).push(e); });
    var out = [];
    Object.keys(by).forEach(function (k) {
      var g = by[k].sort(function (a, b) { return +b.x.time - +a.x.time; }), top = g[0];
      var recent = g.filter(function (e) { return +e.x.time > now - TREND_MS; }).length;
      var prior = g.filter(function (e) { return +e.x.time <= now - TREND_MS && +e.x.time > now - 2 * TREND_MS; }).length;
      var trend = recent > prior || (recent === prior && recent > 0) ? 'BUILDING' : 'FADING', a = now - +top.x.time;
      if (trend === 'FADING' && a > NEWS_DROP_MS) return;
      var imp = parseFloat(top.x.importance);
      out.push({ id: top.x._id || top.x.time, t: +top.x.time, ageMs: a, score: isFinite(imp) ? imp : null, coin: top.c.coin, head: String(top.x.title || '').split('\n')[0].slice(0, 160),
        chip: top.c.chip, trend: trend, recent: recent, prior: prior, key: k, since: sinceHeadline(rows1m, +top.x.time, px) });
    });
    out.sort(function (a, b) { return b.t - a.t; });
    return out.slice(0, NEWS_ROWS);
  }
  function scoreTxt(s) { return (s == null ? '--' : s.toFixed(1)) + ' / ' + NEWS_MAX; }
  function newsTile(ctx, now, fd) {
    var a = age(fd.news, now, LIMIT.news, 'news'), rows = newsRows(ctx.newsItems, now, ctx.rows1m, ctx.px);
    var head = '<div class="o1-nr o1-nh"><span>age</span><span>score</span><span>coin</span><span>headline</span><span>read for price</span><span>trend</span><span>price since</span></div>';
    var body;
    if (!fd.news) body = nid('news feed not connected yet');
    else if (!rows.length) body = '<div class="o1-nid">no market-moving news <span class="dim">checked ' + hhmm(fd.news) + 'Z</span></div>';
    else body = head + rows.map(function (r) {
      var cc = r.chip === 'UP' ? 'up' : r.chip === 'DOWN' ? 'down' : 'amber';
      return '<div class="o1-nr" data-news="' + esc(r.id) + '"><span class="o1-n">' + ageWord(r.ageMs) + '</span><span class="o1-n" title="Tree News importance, scale 0 to ' + NEWS_MAX + '">' + scoreTxt(r.score) + '</span><span>' + r.coin + '</span>' +
        '<span class="o1-ell" title="' + esc(r.head) + '">' + esc(r.head) + '</span><span>' + chip(r.chip, cc, 'word rule: ' + r.key + ' (our rule; nothing measured per headline)') + '</span>' +
        '<span>' + chip(r.trend, r.trend === 'BUILDING' ? 'amber' : 'dim', 'headlines on this story: ' + r.recent + ' in the last 30 min, ' + r.prior + ' in the 30 min before') + '</span>' +
        '<span class="o1-n ' + (r.since == null ? 'dim' : r.since > 0 ? 'up' : r.since < 0 ? 'down' : 'dim') + '">' + (r.since == null ? '--' : sg(r.since, 2) + '%') + '</span></div>';
    }).join('');
    return tile('news', 'News that matters', 'Only BTC or whole-market headlines that match one of our word rules (hack, halt, fed or CPI, war, ETF, BTC buying or selling). Score = Tree News importance out of 10. BUILDING = more related headlines in the last 30 min than in the 30 min before. A faded story drops after 2 h. Price since = BTC move from the headline time. Context only; no headline is a trade call.', a.html, body, 'o1-news');
  }

  // ---------- Ahead (R27 point 4) ----------
  var KEYS = [['FOMC', /\bfomc\b|federal funds rate|fed (rate )?decision/i], ['CPI', /\bcpi\b|consumer price/i], ['NFP', /\bnfp\b|non-?farm|payrolls|employment change/i], ['PPI', /\bppi\b|producer price/i]];
  var LBL = { CPI: 'CPI inflation', NFP: 'Jobs report (NFP)', FOMC: 'FOMC statement', FOMC_PRESSER: 'FOMC press conf.', PPI: 'PPI' };
  var HIGH_CLS = { CPI: 1, NFP: 1, FOMC: 1, FOMC_PRESSER: 1 };
  function clsOf(title) { for (var i = 0; i < KEYS.length; i++) if (KEYS[i][1].test(title || '')) return KEYS[i][0]; return null; }
  function lastFriday(y, m) { var d = new Date(Date.UTC(y, m + 1, 0)); while (d.getUTCDay() !== 5) d = new Date(d.getTime() - DAY); return d.getTime(); }
  // Deribit expiries are Fridays 08:00Z (weekly), the last Friday of the month is the monthly; Mar / Jun / Sep / Dec monthly = quarterly (HIGH). OURS from the exchange's published rule.
  function expiries(now, n) {
    var out = [], d = new Date(now); d.setUTCHours(8, 0, 0, 0);
    var t = d.getTime(); while (new Date(t).getUTCDay() !== 5) t += DAY;
    for (var i = 0; i < 10 && out.length < n; i++, t += 7 * DAY) {
      if (t <= now) continue;
      var dt = new Date(t), lf = lastFriday(dt.getUTCFullYear(), dt.getUTCMonth()) + 8 * HOUR, monthly = Math.abs(lf - t) < HOUR, q = monthly && dt.getUTCMonth() % 3 === 2;
      out.push({ t: t, label: q ? 'Options expiry (quarterly)' : monthly ? 'Options expiry (monthly)' : 'Options expiry (weekly)', impact: q ? 'HIGH' : monthly ? 'MED' : 'LOW', src: 'OURS' });
    }
    return out;
  }
  // Next weekday US cash open from today's open time (ms) given by the page; US holidays are not modelled.
  function nextUsOpen(openToday, now) {
    if (!(openToday > 0)) return null;
    for (var i = 0; i < 9; i++) { var t = openToday + i * DAY, wd = new Date(t).getUTCDay(); if (wd >= 1 && wd <= 5 && t > now - 2 * HOUR) return t; }
    return null;
  }
  // Tile on Home only from 3 h before to 2 h after the open on a weekday: {show, phase, min}
  function usWindow(openToday, now) {
    var t = nextUsOpen(openToday, now); if (t == null) return { show: false, t: null };
    var d = t - now; return { show: d <= 3 * HOUR && d >= -2 * HOUR, t: t, phase: d > 0 ? 'before' : 'in', min: Math.round(Math.abs(d) / MIN) };
  }
  function cdWord(ms) { var m = Math.max(0, Math.floor(ms / MIN)), d = Math.floor(m / 1440), h = Math.floor(m % 1440 / 60); return d ? d + 'd ' + two(h) + 'h' : h ? h + 'h ' + two(m % 60) + 'm' : m < 1 ? '<1m' : m + 'm'; }
  // all upcoming events, oldest first. strip = EVENTS_STRIP_DATA, cal = ForexFactory events or null
  function events(now, strip, calEvents, openToday) {
    var out = [], seen = [];
    ((strip && strip.schedule) || []).forEach(function (s) {
      if (!(s.t0 > now)) return;
      out.push({ t: s.t0, label: LBL[s.cls] || s.cls, impact: HIGH_CLS[s.cls] ? 'HIGH' : 'MED', cls: s.cls, src: 'SOURCED' });
    });
    (calEvents || []).forEach(function (e) {
      var t = Date.parse(e.date); if (!(t > now) || String(e.country) !== 'USD' || String(e.impact) !== 'High') return;
      var c = clsOf(e.title), dup = c && out.some(function (o) { return o.cls && (o.cls === c || (c === 'FOMC' && o.cls === 'FOMC_PRESSER')) && Math.abs(o.t - t) < 6 * HOUR; });
      if (dup) return;
      out.push({ t: t, label: String(e.title).slice(0, 34), impact: 'HIGH', cls: c, src: 'SOURCED' });
    });
    expiries(now, 6).forEach(function (e) { out.push(e); });
    out.sort(function (a, b) { return a.t - b.t; });
    return out;
  }
  function bucket(t, now) {
    var d0 = Math.floor(now / DAY) * DAY, dow = new Date(now).getUTCDay(), toSun = ((7 - dow) % 7) + 1, wk = d0 + toSun * DAY;
    var dn = new Date(now), me = Date.UTC(dn.getUTCFullYear(), dn.getUTCMonth() + 1, 1);
    return t < d0 + DAY ? 'today' : t < wk ? 'week' : t < me ? 'month' : 'later';
  }
  function aheadTile(ctx, now, fd) {
    var strip = G.EVENTS_STRIP_DATA || ctx.strip || null, calOk = ctx.cal && ctx.cal.events && ctx.cal.t && now - ctx.cal.t <= LIMIT.cal;
    var evs = events(now, strip, calOk ? ctx.cal.events : null, ctx.usOpenT), haveCal = !!((strip && strip.schedule && strip.schedule.length) || calOk);
    var a = age(calOk ? ctx.cal.t : 0, now, LIMIT.cal, 'calendar');
    var uw = usWindow(ctx.usOpenT, now), lines = [];
    var row = function (lab, label, t, impact) {
      return '<div class="o1-ar"><span class="dim">' + lab + '</span><span class="o1-ell" title="' + esc(label) + '">' + esc(label) + '</span><span class="o1-n">' + DOW[new Date(t).getUTCDay()] + ' ' + hhmm(t) + 'Z</span><span class="o1-n dim">' + ist(t) + ' IST</span><span>' +
        chip(impact, impact === 'HIGH' ? 'amber' : 'dim') + '</span><span class="o1-n">' + cdWord(t - now) + '</span></div>';
    };
    if (uw.t && !uw.show) lines.push(row('US open', 'US cash open countdown', uw.t, 'MED'));
    var groups = [['today', 'Today'], ['week', 'This week'], ['month', 'This month'], ['later', 'Later']];
    groups.forEach(function (g) {
      var xs = evs.filter(function (e) { return bucket(e.t, now) === g[0]; }).slice(0, g[0] === 'later' ? 1 : 2);
      if (g[0] === 'later' && lines.length > 5) return;
      xs.forEach(function (e, i) { lines.push(row(i ? '' : g[1], e.label, e.t, e.impact)); });
    });
    var body = lines.join('') || nid('no event ahead in the schedule data');
    if (!haveCal) body = '<div class="o1-nid amber">calendar not loaded <span class="dim">run: ' + esc(CLI_CAL) + '</span></div>' + body;
    return tile('ahead', 'Ahead', 'Next scheduled events: today, this week, this month (UTC and IST). Impact HIGH = USD high-impact release or quarterly expiry. Schedule from the BLS / Fed calendar and ForexFactory; options expiry is Deribit Friday 08:00Z (OURS). US holidays are not modelled. Context only.', a.html, body, 'o1-ahead');
  }
  function usTile(ctx, now, fd) {
    var u = ctx.usOpen, w = usWindow(ctx.usOpenT, now), a = age(fd.candles, now, LIMIT.candles, 'candles');
    if (!w.show) return '';
    var r = u && u.r ? u.r : null, head = w.phase === 'before' ? 'opens in ' + cdWord(w.t - now) : 'opened ' + w.min + 'm ago';
    var body = '<div class="o1-big">' + head + '</div>';
    if (r && r.box && isFinite(r.box.l)) body += '<div class="o1-row"><span class="dim">day range</span><span class="o1-n">' + n0(r.box.l) + ' - ' + n0(r.box.h) + '</span><span class="o1-n dim">' + (100 * (r.box.h - r.box.l) / r.box.l).toFixed(1) + '%</span></div>';
    if (r && r.or && isFinite(r.or.l)) body += '<div class="o1-row"><span class="dim">first 15m</span><span class="o1-n">' + n0(r.or.l) + ' - ' + n0(r.or.h) + '</span></div>';
    var up = r && r.up && r.up[0], dn = r && r.down && r.down[0];
    if (up) body += '<div class="o1-row"><span class="up">above</span><span class="o1-n">' + n0(up.p) + '</span><span class="o1-n dim">' + sg(100 * up.dist, 2) + '%</span></div>';
    if (dn) body += '<div class="o1-row"><span class="down">below</span><span class="o1-n">' + n0(dn.p) + '</span><span class="o1-n dim">' + sg(100 * dn.dist, 2) + '%</span></div>';
    return tile('usopen', 'US open', 'Shown from 3 h before to 2 h after the US cash open on weekdays; otherwise it is one countdown line in Ahead. Day range and nearest levels from the page\'s US-open panel. Context only.', a.html, body, 'o1-us');
  }

  // ---------- state tiles ----------
  var LAYER = { rsi_div: 'RSI div', wt_div: 'WT div', cvd_div: 'flow div', bb_cvd: 'band+flow', sweep: 'sweep', absorb: 'absorb', vfi: 'vol flow', sqz_release: 'squeeze', adx_di: 'trend', value_area: 'value area' };
  function boardTile(ctx, md, now, fd) {
    var a = age(fd.candles, now, LIMIT.candles, 'candles'), B = null;
    try { B = SB && LH ? SB.board(LH._boardInputs(ctx)) : null; } catch (e) { B = null; }
    var body;
    if (!B) body = nid('board waiting for candles');
    else {
      var mx = Math.max(B.strength.long, B.strength.short, 4);
      var side = function (name, c, key) {
        var it = B[key] || [], n = B.strength[key];
        return '<div class="o1-side ' + c + '" data-side="' + name + '"><div class="o1-big ' + c + '">' + name + ' ' + n + '</div><div class="o1-bar ' + c + '"><span style="width:' + Math.round(n / mx * 100) + '%"></span></div>' +
          (it.slice(0, 3).map(function (x) { return '<div class="o1-li"><span class="o1-n">' + esc(x.tf) + '</span> ' + esc(LAYER[x.layer] || x.layer) + '</div>'; }).join('') || '<div class="o1-li dim">nothing live</div>') + '</div>';
      };
      body = '<div class="o1-two">' + side('LONG', 'up', 'long') + side('SHORT', 'down', 'short') + '</div>';
    }
    return tile('board', 'LONG / SHORT board', 'Count of live evidence per side from the layers (divergence, squeeze, trend, flow). A plain count, no weight, no probability; the old Home shows the n and hit rate of the current mix.', a.html, body);
  }
  var ST_CLS = { 'REJECTED': 'up', 'FAILED BREAK': 'up', 'ACCEPTED': 'down', 'BREAKING': 'down', 'TESTING': 'amber', 'APPROACHING': 'amber', 'AWAY': 'dim' };
  function levelTile(ctx, md, now, fd) {
    var a = age(fd.candles, now, LIMIT.candles, 'candles'), v = null;
    try { v = LH ? LH._stories(ctx, md) : null; } catch (e) { v = null; }
    var body;
    if (!v) body = nid('waiting for 15m candles');
    else {
      var rows = v.filter(Boolean).slice(0, 3).map(function (st) {
        return '<div class="o1-row"><span class="o1-n ' + (st.res ? 'down' : 'up') + '">' + n0(st.price) + '</span><span class="o1-ell" title="' + esc(st.name) + '">' + esc(st.name) + '</span>' + chip(st.state, ST_CLS[st.state] || 'dim', 'evidence on 15m closes: ' + st.turn + ' for a turn back, ' + st.thru + ' for a break') +
          (st.idea ? chip(st.idea + ' IDEA', st.idea === 'SHORT' ? 'down' : 'up', 'measured 49 % right over 180 days: a coin flip, not an edge') : '') + '</div>';
      }).join('');
      body = rows || nid('no level near');
    }
    return tile('level', 'At the level', 'Nearest levels read on 15m closes: APPROACHING, TESTING, REJECTED, BREAKING, ACCEPTED. An IDEA chip is our rule, measured 49 % right over 180 days (a coin flip). Levels SOURCED, state words OURS.', a.html, body);
  }
  function winTile(ctx, md, now, fd) {
    var T = ctx.ind, a = age(fd.candles, now, LIMIT.candles, 'candles'), body;
    if (!T || !T.ver) body = nid('waiting for candles');
    else {
      body = ['15m', '1h', '4h'].map(function (tf) {
        var v = T.ver[tf]; if (!v) return '<div class="o1-row"><span class="o1-n">' + tf + '</span><span class="dim">no candles</span></div>';
        var c = v.side > 0 ? 'up' : v.side < 0 ? 'down' : 'dim', w = v.side > 0 ? 'UP' : v.side < 0 ? 'DOWN' : 'MIXED', k = v.side > 0 ? v.up : v.side < 0 ? v.dn : Math.max(v.up, v.dn);
        return '<div class="o1-row"><span class="o1-n">' + tf + '</span>' + chip(w, c) + '<span class="o1-n">' + k + ' of ' + v.n + '</span>' + (v.coiled ? chip('COILED', 'amber', 'quiet before a move; direction unknown') : '') + '</div>';
      }).join('');
    }
    return tile('winning', 'Who is winning', 'Six closed-bar readings vote per timeframe: money flow, squeeze, trend strength, WaveTrend, RSI, buy vs sell volume. A lead of 2 wins. Our rule, not backtested.', a.html, body);
  }
  var MONEY = { 'up/up': ['NEW LONGS', 'up'], 'down/up': ['NEW SHORTS', 'down'], 'up/down': ['SHORT COVER', 'up'], 'down/down': ['LONGS OUT', 'down'], 'flat/up': ['BUILDING', 'amber'], 'flat/down': ['CLOSING', 'dim'],
    'up/flat': ['THIN RISE', 'dim'], 'down/flat': ['THIN FALL', 'dim'], 'flat/flat': ['QUIET', 'dim'] };
  function dirOf(x) { return x >= 0.001 ? 'up' : x <= -0.001 ? 'down' : 'flat'; }
  function moneyTile(ctx, now, fd) {
    var a = age(fd.oi, now, LIMIT.oi, 'open interest'), m = ctx.money, rows = (ctx.moneyRows || []).filter(function (r) { return r && r.net; }), body;
    var miss = m && m.missing ? m.missing.map(function (s) { return String(s).split(':')[0]; }) : [], have = m && m.venues ? m.venues.length : 0, tot = ctx.venueTotal || (have + miss.length);
    if (!rows.length) body = nid('waiting for open-interest samples');
    else {
      body = '<div class="o1-mr o1-nh"><span></span><span>price</span><span>open int.</span><span>state</span></div>' + rows.map(function (r) {
        var k = dirOf(r.net.dp) + '/' + dirOf(r.net.doi), w = MONEY[k] || ['--', 'dim'];
        return '<div class="o1-mr"><span class="o1-n">' + esc(r.label) + '</span><span class="o1-n ' + (r.net.dp > 0 ? 'up' : r.net.dp < 0 ? 'down' : 'dim') + '">' + sg(r.net.dp * 100, 2) + '%</span><span class="o1-n ' + (r.net.doi > 0 ? 'up' : r.net.doi < 0 ? 'down' : 'dim') + '">' + sg(r.net.doi * 100, 2) + '%</span><span>' + chip(w[0], w[1]) + '</span></div>';
      }).join('') + '<div class="o1-sm" title="' + esc(miss.length ? 'No data from: ' + miss.join(', ') : 'all venues read') + '">' + have + ' of ' + tot + ' venues</div>';
    }
    return tile('money', 'Money', 'Price change vs open-interest change per window, summed over the venues that have data. NEW LONGS = price up and positions up. A flat move is under 0.1 %. Hover the venue count for the names with no data. Says where positions go, not where price goes next; reading words OURS.', a.html, body);
  }
  function coilTile(ctx, now, fd) {
    var a = age(fd.candles, now, LIMIT.candles, 'candles'), rows = [['15m', bbWidth(ctx.k15, now)], ['1h', bbWidth(ctx.k1h, now)]], any = rows.some(function (r) { return r[1]; });
    var pr = ctx.coil && ctx.coil.pierce ? ctx.coil.pierce : null, body;
    if (!any) body = nid('waiting for 15m and 1h candles');
    else body = '<div class="o1-cr o1-nh"><span></span><span>state</span><span>band width</span><span>percentile</span></div>' + rows.map(function (r) {
      var b = r[1]; if (!b) return '<div class="o1-cr"><span class="o1-n">' + r[0] + '</span><span class="dim">no data</span></div>';
      return '<div class="o1-cr"><span class="o1-n">' + r[0] + '</span><span>' + chip(b.coil ? 'COIL' : 'no coil', b.coil ? 'amber' : 'dim', 'COIL = band width in the lowest 20 % of its own recent history') + '</span><span class="o1-n">' + (100 * b.width).toFixed(2) + '%</span><span class="o1-n">' + (b.pct == null ? '--' : 'p' + Math.round(b.pct * 100)) + '</span></div>';
    }).join('') + (pr ? '<div class="o1-row">' + chip('PIERCE ' + String(pr.side).toUpperCase(), pr.side === 'up' ? 'up' : 'down', '15m close outside the band, ' + pr.ageBars + ' bars ago') + '</div>' : '');
    return tile('coil', 'Coil', 'Band width = (upper - lower) / middle of the Bollinger band (20 bars, 2 SD) on closed bars. Percentile = how narrow it is against its last 200 bars; COIL = lowest 20 %. A coil says a move is likely coming, not which way. Band width and percentile OURS; 20 % cut SOURCED (coil panel).', a.html, body);
  }
  var ADX_TFS = ['5m', '15m', '1h', '4h'];
  function adxTile(ctx, now, fd) {
    var a = age(fd.candles, now, LIMIT.candles, 'candles'), K = ctx.kAdx || {}, any = false;
    var body = ADX_TFS.map(function (tf) {
      var r = null; try { r = AX && K[tf] ? AX.row(tf, K[tf], now) : null; } catch (e) { r = null; }
      if (!r) return '<div class="o1-row"><span class="o1-n">' + tf + '</span><span class="dim">no data</span></div>';
      any = true;
      var cc = r.chip === 'TREND' ? 'up' : r.chip === 'BUILDING' ? 'amber' : r.chip === 'STRETCHED' ? 'down' : 'dim';
      return '<div class="o1-row"><span class="o1-n">' + tf + '</span><span class="o1-n">' + r.adx.toFixed(1) + (r.arrow === 'up' ? ' \u2197' : r.arrow === 'down' ? ' \u2198' : '') + '</span>' + chip(r.chip || '--', cc) +
        '<span class="o1-n ' + (r.winner === 'plus' ? 'up' : r.winner === 'minus' ? 'down' : 'dim') + '">' + (r.winner === null ? '=' : (r.winner === 'plus' ? '+' : '-') + 'DI ' + r.lead.toFixed(0)) + '</span></div>';
    }).join('');
    return tile('adx', 'ADX strip', 'ADX(14) of the last closed bar with its 3-bar arrow, then who leads: +DI (green) or -DI (red) and by how many points. NO TREND under 20, WEAK 20-25, BUILDING rising, TREND 25 and up, STRETCHED high and falling. Display only: no fee-net edge measured.', a.html, any ? body : nid('waiting for candles'));
  }
  var LANES = ['1m', '2m', '3m', '15m', '30m', '4h'];
  function wtTile(ctx, now, fd) {
    var L = ctx.lanes || {}, a = age(fd.candles, now, LIMIT.candles, 'candles'), last = null, any = false;
    var chips = LANES.map(function (tf) {
      var z = L[tf], sd = z && z.side != null ? z.side : null; if (sd !== null) any = true;
      var zone = z && z.zone === 'hot' ? ' OB' : z && z.zone === 'cold' ? ' OS' : '';
      return '<span class="o1-wt ' + (sd === 1 ? 'up' : sd === -1 ? 'down' : 'dim') + '" title="' + tf + ' WaveTrend ' + (sd === 1 ? 'rising' : sd === -1 ? 'falling' : 'no data') + (zone ? (zone === ' OB' ? ', overbought' : ', oversold') : '') + '"><i>' + tf + '</i> ' + (sd === 1 ? '\u25B2' : sd === -1 ? '\u25BC' : '\u00B7') + zone + '</span>';
    }).join('');
    ['1m', '2m', '3m', '15m', '30m'].forEach(function (tf) { var z = L[tf], lx = z && z.last; if (!lx) return; var ag = lx.ago * (z.ms || 60000); if (!last || ag < last.age) last = { tf: tf, side: lx.side, age: ag, strong: lx.strong }; });
    var ln = last ? '<div class="o1-row"><span class="dim">last cross</span><span class="o1-n">' + last.tf + '</span>' + chip(last.side > 0 ? 'UP' : 'DOWN', last.side > 0 ? 'up' : 'down') + '<span class="o1-n dim">' + ageWord(last.age) + ' ago' + (last.strong ? ', big dot' : '') + '</span></div>' : '';
    return tile('wt', 'WaveTrend', 'Direction of the WaveTrend line per timeframe (green up, red down) with OB overbought / OS oversold. 1m-3m time a move, 15m-30m give the frame, 4h the background. A big dot on a cross = a strong one. 10/21/4 OURS. Display only.', a.html, any ? '<div class="o1-wts">' + chips + '</div>' + ln : nid('waiting for candles'));
  }
  function flowTile(ctx, now, fd) {
    var F = G.LAFlow && G.LAFlow.tile ? G.LAFlow.tile() : null, a = age(F && F.t || 0, now, LIMIT.flow, 'forced-moves bars');
    return tile('forced', 'Forced moves', 'R25 chart: price candles, open interest tinted by bar state, CVD. NEW LONGS / NEW SHORTS = price and open interest move together; FORCED BUYING / SELLING = price moves against falling open interest (positions closing). Context, not a signal (research edge-forced-move-fade-1113: no edge). Needs Bybit and Binance spot reachable.', a.html,
      F && F.ok ? F.html : nid('waiting for Bybit bars'), 'o1-forced');
  }

  // ---------- top strip ----------
  function session(now) {
    var d = new Date(now), h = d.getUTCHours() + d.getUTCMinutes() / 60, wd = d.getUTCDay();
    if (wd === 0 || wd === 6) return 'Weekend';
    return h >= 13 && h < 21 ? 'US' : h >= 7 && h < 13 ? 'Europe' : h < 8 ? 'Asia' : 'Off-hours';
  }
  function topStrip(ctx, md, now, fd) {
    var P = age(fd.price, now, LIMIT.price, 'price'), O = age(fd.oi, now, LIMIT.oi, 'open interest'), N = age(fd.news, now, LIMIT.news, 'news');
    var dir = md.dir, c = dir === 'LONG' ? 'up' : dir === 'SHORT' ? 'down' : 'dim';
    var bias = chip(dir === 'WAIT' ? 'NO BIAS' : dir + ' ' + Math.max(md.bull, md.bear) + '/' + md.n, c, 'Six readings vote (analysts, price vs day average, RSI 1h, RSI 4h, breakout, playbook): ' + md.bull + ' say up, ' + md.bear + ' say down. Our rule; observation only.');
    var feed = function (lab, x) { return '<span class="o1-fd"><span class="dim">' + lab + '</span> ' + x.html + '</span>'; };
    return '<div class="o1-top"><b class="o1-px" id="o1-px">' + (md.px > 0 ? n0(md.px) : '--') + '</b>' + chip(session(now) + ' session', 'dim', 'UTC clock: Asia 00-08, Europe 07-13, US 13-21 (weekend shown on Sat and Sun)') + bias +
      '<span class="o1-sp"></span>' + feed('price', P) + feed('open interest', O) + feed('news', N) + '<span class="o1-clock o1-n dim">' + hhmm(now) + 'Z / ' + ist(now) + ' IST</span></div>';
  }

  // ---------- render ----------
  function html(ctx, md, W, H, VH) {
    var now = ctx.now, fd = ctx.feeds || {};
    var ch = '', vol = '';
    try { ch = LH._chart(ctx, md, W, H); } catch (e) { ch = nid('chart: ' + e.message); }
    try { vol = LH._volPane(ctx, md, W, VH); } catch (e) { vol = ''; }
    var a = age(fd.candles, now, LIMIT.candles, 'candles');
    var chartTile = '<div class="o1-tile o1-chart" id="o1-chart" data-tile="chart"><div class="o1-h"><b>BTC 5m, last 12 h</b><span class="o1-q" tabindex="0" title="Candles with the named levels on the right, sessions shaded, US open line. Volume under it: green = buyers took more, red = sellers, white line = 20-bar average. Levels SOURCED, session hours OURS.">?</span>' + a.html + '</div><div class="o1-cb">' + ch + vol + '</div></div>';
    var us = usTile(ctx, now, fd), nb = us ? ' o1-bot3' : '';
    var s = topStrip(ctx, md, now, fd) + chartTile + '<div class="o1-grid">' + boardTile(ctx, md, now, fd) + levelTile(ctx, md, now, fd) + winTile(ctx, md, now, fd) + flowTile(ctx, now, fd) + moneyTile(ctx, now, fd) + coilTile(ctx, now, fd) + adxTile(ctx, now, fd) + wtTile(ctx, now, fd) + '</div>' +
      '<div class="o1-bot' + nb + '">' + newsTile(ctx, now, fd) + aheadTile(ctx, now, fd) + us + '</div>';
    return s.replace(/NOT_IN_DATA/g, 'no data');
  }
  function render(el, ctx) {
    if (!el || !LH) return;
    injectCss(el.ownerDocument);
    var md = LH.model(ctx);
    LH.flashes(ctx, md);
    LH._boardLog(ctx, md);
    var box = el.getBoundingClientRect(), bw = box.width || 1600, bh = box.height || 900;
    var W = Math.max(520, Math.round((bw - 32) * 0.55 - 16)), VH = 56, H = Math.max(200, Math.round(bh - 52 - 204 - 16 - 24 - VH - 14));
    el._ctx = ctx;
    el.innerHTML = html(ctx, md, W, H, VH);
  }

  var CSS = '#p-home{display:grid;grid-template-columns:minmax(0,55fr) minmax(0,45fr);grid-template-rows:auto minmax(0,1fr) 204px;gap:8px;padding:8px!important;overflow:hidden!important;font-family:var(--sans);font-size:14px}' +
    '#p-home-old{display:grid;grid-template-columns:70% 30%;gap:8px;padding:6px!important;overflow:hidden!important}' +
    '#p-home *{font-family:var(--sans)!important;font-variant-numeric:tabular-nums}#p-home svg text{font-family:var(--sans)!important}' +
    '.o1-top{grid-column:1/-1;display:flex;gap:10px;align-items:center;flex-wrap:nowrap;white-space:nowrap;overflow:hidden;min-height:38px}.o1-px{font-size:26px;font-weight:700;color:var(--amber)}.o1-sp{flex:1}.o1-fd{font-size:12px}.o1-clock{font-size:12px}' +
    '.o1-tile{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:6px 10px;min-width:0;min-height:0;overflow:hidden;display:flex;flex-direction:column}' +
    '.o1-h{display:flex;align-items:center;gap:8px;flex:none;font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}.o1-h b{font-weight:600;color:var(--fg);flex:0 1 auto;text-transform:none;font-size:14px;letter-spacing:0}' +
    '.o1-q{display:inline-block;width:16px;height:16px;line-height:15px;text-align:center;border:1px solid var(--dim);border-radius:50%;font-size:11px;cursor:help;flex:none;color:var(--dim)}.o1-h .o1-age{margin-left:auto}' +
    '.o1-age{font-size:12px;padding:1px 7px;border-radius:3px;background:var(--line);color:var(--dim);white-space:nowrap;text-transform:none;letter-spacing:0}.o1-age.stale{background:var(--amber);color:var(--bg);font-weight:600}' +
    '.o1-b{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:3px}.o1-cb{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}.o1-cb .hm-svg{width:100%;flex:none}' +
    '.o1-chart{grid-column:1;grid-row:2}.o1-grid{grid-column:2;grid-row:2;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-rows:repeat(4,minmax(0,1fr));gap:8px;min-height:0}.o1-forced{grid-row:2/4;grid-column:2}' +
    '.o1-bot{grid-column:1/-1;grid-row:3;display:grid;grid-template-columns:minmax(0,60fr) minmax(0,40fr);gap:8px;min-height:0}.o1-bot.o1-bot3{grid-template-columns:minmax(0,45fr) minmax(0,33fr) minmax(0,22fr)}' +
    '.o1-big{font-size:22px;font-weight:700;line-height:1.1}.o1-row{display:flex;gap:8px;align-items:center;white-space:nowrap;overflow:hidden;line-height:22px}.o1-n{font-variant-numeric:tabular-nums;text-align:right}' +
    '.o1-c{display:inline-block;font-size:12px;font-weight:700;padding:0 7px;border-radius:9px;border:1px solid currentColor;line-height:18px;white-space:nowrap}.o1-c.up,.up{color:var(--up)}.o1-c.down,.down{color:var(--down)}.o1-c.amber,.amber{color:var(--amber)}.o1-c.dim,.dim{color:var(--dim)}' +
    '.o1-nid{color:var(--dim);font-size:14px;padding:4px 0}.o1-sm{font-size:12px;color:var(--dim);cursor:help;margin-top:auto}.o1-ell{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
    '.o1-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.o1-side{min-width:0}.o1-bar{height:6px;background:var(--line);border-radius:3px;margin:3px 0}.o1-bar span{display:block;height:100%;border-radius:3px}.o1-bar.up span{background:var(--up)}.o1-bar.down span{background:var(--down)}.o1-li{font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:18px}' +
    '.o1-mr{display:grid;grid-template-columns:46px 1fr 1fr 1.3fr;gap:6px;align-items:center;line-height:22px}.o1-cr{display:grid;grid-template-columns:34px 1fr 1fr 1fr;gap:6px;align-items:center;line-height:22px}.o1-nh{font-size:11px;color:var(--dim);line-height:14px}.o1-nh span{text-align:right}.o1-nh span:first-child{text-align:left}' +
    '.o1-wts{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;padding:4px 0}.o1-wt{font-size:14px;font-weight:600;border:1px solid currentColor;border-radius:5px;padding:2px 8px;cursor:help}.o1-wt i{font-style:normal;font-weight:400;color:var(--dim);margin-right:2px}' +
    '.o1-nr{display:grid;grid-template-columns:44px 74px 40px minmax(0,1fr) 96px 92px 78px;gap:8px;align-items:center;line-height:22px;white-space:nowrap;overflow:hidden}.o1-nr>span:nth-child(n+5):not(:last-child){text-align:left}.o1-nr.o1-nh{line-height:14px;font-size:11px;color:var(--dim)}.o1-nr.o1-nh span:nth-child(3),.o1-nr.o1-nh span:nth-child(4),.o1-nr.o1-nh span:nth-child(5),.o1-nr.o1-nh span:nth-child(6){text-align:left}.o1-nr>span:nth-child(1),.o1-nr>span:nth-child(2){text-align:right}' +
    '.o1-ar{display:grid;grid-template-columns:70px minmax(0,1fr) 74px 74px 52px 60px;gap:8px;align-items:center;line-height:20px;white-space:nowrap;overflow:hidden}' +
    '.o1-forced .o1-b svg{flex:1 1 auto;width:100%;min-height:0}.o1-forced .fl-chip,.o1-forced .fl-chip2{font-size:12px!important;padding:2px 8px!important}' +
    '@media (max-width:900px){#p-home{display:block;overflow:auto!important}.o1-grid{display:grid;grid-template-columns:1fr;grid-template-rows:none}.o1-forced{grid-row:auto;grid-column:auto}.o1-bot{display:block}.o1-chart{margin:8px 0}}';
  function injectCss(doc) { if (!doc || doc.getElementById('o1-css')) return; var st = doc.createElement('style'); st.id = 'o1-css'; st.textContent = CSS; doc.head.appendChild(st); }

  var api = { render: render, html: html, injectCss: injectCss, bbWidth: bbWidth, classify: classify, newsRows: newsRows, sinceHeadline: sinceHeadline, scoreTxt: scoreTxt, events: events, bucket: bucket, expiries: expiries,
    nextUsOpen: nextUsOpen, usWindow: usWindow, age: age, ageWord: ageWord, session: session, LIMIT: LIMIT, NEWS_MAX: NEWS_MAX, newsTile: newsTile, aheadTile: aheadTile, usTile: usTile, moneyTile: moneyTile, coilTile: coilTile, CSS: CSS };
  if (isNode) module.exports = api; else root.LAONE = api;
})(typeof window !== 'undefined' ? window : this);
