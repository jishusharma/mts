// Live Aid HOME tab (operator 2026-11-09 14:40Z): the one screen he watches while trading. Full viewport, no page scroll,
// pictures over words: a candle chart with every level drawn and named in plain words, sessions and the US open marked on
// the chart, plus a side rail (direction gauge, momentum squares, liquidation bar, money arrows, news with impact).
// A flash bar fires on big news, liquidation bursts and level touches. Observation only: no order, no size, no entry wording.
// Thresholds marked OURS were chosen here, not measured. Pure model() for tests; render() draws.
(function (root) {
  'use strict';
  var REG = (typeof module !== 'undefined' && module.exports) ? require('./level_registry.js') : root.LEVELREG;
  var BIG_PRINT = 250000, BURST_1M = 1000000, TOUCH = 0.0005, NEWS_HI = 7, NEWS_FRESH = 180000;   // OURS
  var FLASH_MS = { news: 90000, liq: 60000, touch: 45000, setup: 180000 };
  var VOTE_NAMES = ['Analysts', 'Price vs day average', 'RSI 1h', 'RSI 4h', 'Breakout', 'Playbook'];
  var WORDS = { PDH: 'Yesterday high', PDL: 'Yesterday low', PDC: 'Yesterday close', PWH: 'Last week high', PWL: 'Last week low', DO: 'Day open',
                WO: 'Week open', VAL: 'Yesterday value low', POC: 'Yesterday busiest price', VAH: 'Yesterday value high', DH: 'Today high', DL: 'Today low', VWAP: 'Day average price' };
  var SESS = [['Asia', 0, 8], ['Europe', 7, 13], ['US', 13, 21]];

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n0(x) { return isFinite(x) ? Math.round(x).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '--'; }
  function usd(x) { return x >= 1e6 ? (x / 1e6).toFixed(1) + 'M' : x >= 1e3 ? Math.round(x / 1e3) + 'k' : String(Math.round(x || 0)); }
  function maWord(b) {
    var m = /^(\d?[HDW]|1[HDW]|4H)(E|S)(\d+)$/i.exec(b); if (!m) return null;
    var tf = m[1].toUpperCase(), per = { '1D': 'day', '1W': 'week', '4H': '4h', '1H': '1h' }[tf] || tf.toLowerCase();
    return m[3] + '-' + per + ' average';
  }
  function itemWord(it) {
    if (it.src === 'analyst') return 'Analyst call';
    return WORDS[it.badge] || maWord(it.badge) || it.label || it.badge;
  }
  // zone -> plain-words name: up to 2 distinct names, then "+N more"
  function zoneName(z) {
    var w = [];
    z.items.forEach(function (it) { var s = itemWord(it); if (w.indexOf(s) < 0) w.push(s); });
    var an = z.items.filter(function (i) { return i.src === 'analyst'; }).length;
    w = w.map(function (s) { return s === 'Analyst call' && an > 1 ? an + ' analyst calls' : s; });
    return w.slice(0, 2).join(' + ') + (w.length > 2 ? ' +' + (w.length - 2) : '');
  }

  // ---------- model ----------
  // ctx: {now, px, rows5 [[t,o,h,l,c],...], votes[6], map (LAMAP model), mom {tf: {rsi}}, liq {m1, m5, m15, last[]}, money, news [{id,t,score,head,tag}], ev {cls,t0}, scen [{up,down,likely,id}]}
  function model(ctx) {
    var now = ctx.now, px = ctx.px, m = ctx.map || {};
    var zones = REG ? REG.merge([].concat(REG.fromPlaybook(m.data && m.data.levels), REG.fromPanel(m.panel), REG.fromMA(m.ma), REG.fromAnalysts(m.analysts))) : [];
    zones.forEach(function (z) { z.name = zoneName(z); });
    var lad = REG && px > 0 ? REG.ladder(zones, px, 4) : { above: [], below: [], at: null };
    var v = (ctx.votes || []).slice(0, 6), bull = 0, bear = 0, n = 0;
    v.forEach(function (x) { if (x === 1 || x === -1 || x === 0) { n++; if (x === 1) bull++; if (x === -1) bear++; } });
    var dir = n < 3 ? 'WAIT' : bull >= 2 && bull >= 2 * bear ? 'LONG' : bear >= 2 && bear >= 2 * bull ? 'SHORT' : 'WAIT';
    return { now: now, px: px, zones: zones, lad: lad, votes: v, bull: bull, bear: bear, n: n, dir: dir, score: n ? (bull - bear) / 6 : 0 };
  }

  // ---------- flash (state kept on root so it survives redraws) ----------
  var FL = { seen: {}, list: [] };
  function flashes(ctx, md) {
    var now = ctx.now, add = function (k, kind, cls, text) { if (FL.seen[k]) return; FL.seen[k] = now; FL.list.push({ k: k, kind: kind, cls: cls, text: text, t: now }); };
    (ctx.news || []).forEach(function (x) {
      if (x.score >= NEWS_HI && now - x.t <= NEWS_FRESH) add('n' + x.id, 'news', x.tag === 'POSITIVE' ? 'up' : x.tag === 'NEGATIVE' ? 'down' : 'amber', 'NEWS ' + x.score.toFixed(0) + '/10: ' + x.head);
    });
    var l = ctx.liq || {};
    (l.last || []).forEach(function (e) {
      if (e.usd >= BIG_PRINT && now - e.t <= 60000) add('l' + e.t + e.usd, 'liq', e.side === 'long' ? 'down' : 'up', usd(e.usd) + ' of ' + (e.side === 'long' ? 'LONGS' : 'SHORTS') + ' forced out at ' + n0(e.px));
    });
    if (l.m1 && l.m1.long + l.m1.short >= BURST_1M) add('b' + Math.floor(now / 60000), 'liq', l.m1.long >= l.m1.short ? 'down' : 'up', 'LIQUIDATION BURST: ' + usd(l.m1.long + l.m1.short) + ' in 1 min, mostly ' + (l.m1.long >= l.m1.short ? 'longs' : 'shorts'));
    var PU = (typeof module !== 'undefined' && module.exports) ? require('./pulse.js') : root.LAPULSE;
    var su = ctx.setup !== undefined ? ctx.setup : (PU && ctx.pulse ? PU.setup(ctx.pulse, md.lad, md.px, md.dir) : null);
    if (su) add('s' + su.side + Math.round(su.level) + Math.floor(now / 900000), 'setup', su.side === 'SHORT' ? 'down' : 'up', su.side + ' SETUP FORMING: ' + su.why.join('; ') + ' (your call)');
    if (md.px > 0) md.zones.forEach(function (z) {
      if (Math.abs(md.px / z.price - 1) <= TOUCH) add('t' + Math.round(z.price) + Math.floor(now / 900000), 'touch', 'amber', 'TOUCHING ' + z.name + ' ' + n0(z.price));
    });
    FL.list = FL.list.filter(function (f) { return now - f.t <= FLASH_MS[f.kind]; });
    var out = FL.list.slice(-3).reverse(), fb = root.document && root.document.getElementById('flash');
    if (fb) { fb.innerHTML = out.map(function (f) { return '<div class="fl ' + f.cls + '">' + esc(f.text) + '</div>'; }).join(''); fb.classList.toggle('on', out.length > 0); }
    return out;
  }

  // ---------- drawing ----------
  function chart(ctx, md, W, H) {
    var rows = (ctx.rows5 || []).slice(-144);
    if (rows.length < 5 || !(md.px > 0)) return '<div class="hm-nid">Candles NOT_IN_DATA (no feed yet)</div>';
    var hi = -Infinity, lo = Infinity;
    rows.forEach(function (r) { hi = Math.max(hi, +r[2]); lo = Math.min(lo, +r[3]); });
    var a = md.lad.above[0], b = md.lad.below[0];
    if (a) hi = Math.max(hi, Math.min(a.price, md.px * 1.02)); if (b) lo = Math.min(lo, Math.max(b.price, md.px * 0.98));
    var pad = (hi - lo) * 0.06; hi += pad; lo -= pad;
    var L = 8, R = W - 270, T = 26, B = H - 30, cw = (R - L) / (rows.length + 8);
    var y = function (p) { return T + (hi - p) / (hi - lo) * (B - T); };
    var t0 = +rows[0][0], step = 300000, x = function (t) { return L + ((t - t0) / step + 0.5) * cw; };
    var s = '<svg class="hm-svg" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none">';
    // sessions: shaded bands, name + hours at the top
    var d0 = Math.floor(t0 / 86400000) * 86400000;
    [d0 - 86400000, d0].forEach(function (day) {
      SESS.forEach(function (ss, i) {
        var xa = Math.max(L, x(day + ss[1] * 3600000) - cw / 2), xb = Math.min(R, x(day + ss[2] * 3600000) - cw / 2);
        if (xb - xa < 10) return;
        s += '<rect x="' + xa + '" y="' + T + '" width="' + (xb - xa) + '" height="' + (B - T) + '" class="hm-ses s' + i + '"/>' +
             '<text x="' + (xa + 6) + '" y="' + (T - 8) + '" class="hm-sest">' + ss[0] + ' ' + String(ss[1]).padStart(2, '0') + ':00-' + ss[2] + ':00Z</text>';
      });
    });
    // grid + price axis
    var gstep = Math.pow(10, Math.floor(Math.log10((hi - lo) / 5))), gs = [1, 2, 2.5, 5, 10].map(function (k) { return k * gstep; }).filter(function (g) { return (hi - lo) / g <= 8; })[0];
    for (var g = Math.ceil(lo / gs) * gs; g <= hi; g += gs) s += '<line x1="' + L + '" x2="' + R + '" y1="' + y(g) + '" y2="' + y(g) + '" class="hm-grid"/><text x="' + (R + 4) + '" y="' + (y(g) + 4) + '" class="hm-ax">' + n0(g) + '</text>';
    // time axis every 2h
    rows.forEach(function (r) { var t = +r[0]; if (t % 7200000 === 0) s += '<text x="' + x(t) + '" y="' + (B + 18) + '" class="hm-ax" text-anchor="middle">' + new Date(t).toISOString().slice(11, 16) + '</text>'; });
    // US cash open line 14:30Z today
    var uo = Math.floor(ctx.now / 86400000) * 86400000 + 14.5 * 3600000, ux = x(uo);
    if (ux > L && ux < R) s += '<line x1="' + ux + '" x2="' + ux + '" y1="' + T + '" y2="' + B + '" class="hm-uo"/><text x="' + (ux + 4) + '" y="' + (B - 6) + '" class="hm-uot">US open 14:30Z</text>';
    // levels: every zone in range, named in words
    var labs = [];
    md.zones.forEach(function (z) {
      if (z.price < lo || z.price > hi) return;
      var yy = y(z.price), up = z.price > md.px, c = up ? 'down' : 'up';
      s += '<line x1="' + L + '" x2="' + R + '" y1="' + yy + '" y2="' + yy + '" class="hm-lv ' + c + (z.n > 1 ? ' multi' : '') + '"/>';
      labs.push({ y: yy, c: c, t: z.name, p: z.price, n: z.n });
    });
    // scenario targets from the playbook map
    (ctx.scen || []).slice(0, 1).forEach(function (sc) {
      [['up', sc.up, 'IF UP'], ['down', sc.down, 'IF DOWN']].forEach(function (q) {
        if (!(q[1] >= lo && q[1] <= hi)) return;
        s += '<line x1="' + (R - 160) + '" x2="' + R + '" y1="' + y(q[1]) + '" y2="' + y(q[1]) + '" class="hm-sc ' + q[0] + '"/>' +
             '<text x="' + (R - 158) + '" y="' + (y(q[1]) + (q[0] === 'up' ? -6 : 16)) + '" class="hm-sct ' + q[0] + '">' + q[2] + ' ' + n0(q[1]) + ' (playbook)</text>';
      });
    });
    // candles
    rows.forEach(function (r) {
      var o = +r[1], h = +r[2], l = +r[3], c = +r[4], xx = x(+r[0]), col = c >= o ? 'up' : 'down';
      s += '<line x1="' + xx + '" x2="' + xx + '" y1="' + y(h) + '" y2="' + y(l) + '" class="hm-wk ' + col + '"/>' +
           '<rect x="' + (xx - cw * 0.36) + '" y="' + Math.min(y(o), y(c)) + '" width="' + (cw * 0.72) + '" height="' + Math.max(1, Math.abs(y(o) - y(c))) + '" class="hm-bd ' + col + '"/>';
    });
    // now line + tag
    var py = y(md.px);
    s += '<line x1="' + L + '" x2="' + R + '" y1="' + py + '" y2="' + py + '" class="hm-now"/>';
    // level labels: right gutter, de-overlapped
    labs.sort(function (p, q) { return p.y - q.y; });
    var last = -99; labs.forEach(function (lb) { lb.ly = Math.max(lb.y, last + 17); last = lb.ly; });
    labs.forEach(function (lb) {
      s += '<line x1="' + R + '" x2="' + (R + 66) + '" y1="' + lb.y + '" y2="' + lb.ly + '" class="hm-lead"/>' +
           '<text x="' + (R + 70) + '" y="' + (lb.ly + 4) + '" class="hm-lt ' + lb.c + '"><tspan class="hm-lp">' + n0(lb.p) + '</tspan> ' + esc(lb.t) + '</text>';
    });
    s += '<rect x="' + (R + 2) + '" y="' + (py - 12) + '" width="64" height="24" rx="4" class="hm-tag"/><text x="' + (R + 34) + '" y="' + (py + 5) + '" text-anchor="middle" class="hm-tagt">' + n0(md.px) + '</text>';
    return s + '</svg>';
  }
  function gauge(md) {
    var ang = Math.PI * (1 - (md.score + 1) / 2), cx = 110, cy = 96, r = 80, nx = cx + r * 0.85 * Math.cos(ang), ny = cy - r * 0.85 * Math.sin(ang);
    var arc = function (a0, a1, c) { var x0 = cx + r * Math.cos(a0), y0 = cy - r * Math.sin(a0), x1 = cx + r * Math.cos(a1), y1 = cy - r * Math.sin(a1); return '<path d="M' + x0 + ' ' + y0 + ' A' + r + ' ' + r + ' 0 0 1 ' + x1 + ' ' + y1 + '" class="hm-arc ' + c + '"/>'; };
    var dirc = md.dir === 'LONG' ? 'up' : md.dir === 'SHORT' ? 'down' : 'dim';
    var s = '<svg viewBox="0 0 220 112" class="hm-g">' + arc(Math.PI, Math.PI * 0.62, 'down') + arc(Math.PI * 0.62, Math.PI * 0.38, 'dim') + arc(Math.PI * 0.38, 0, 'up') +
      '<line x1="' + cx + '" y1="' + cy + '" x2="' + nx + '" y2="' + ny + '" class="hm-needle"/><circle cx="' + cx + '" cy="' + cy + '" r="6" class="hm-hub"/>' +
      '<text x="14" y="110" class="hm-gl down">SHORT</text><text x="206" y="110" text-anchor="end" class="hm-gl up">LONG</text></svg>';
    var chips = md.votes.map(function (v, i) {
      var c = v === 1 ? 'up' : v === -1 ? 'down' : v === 0 ? 'dim' : 'nid';
      return '<span class="hm-vc ' + c + '"><i></i>' + VOTE_NAMES[i] + '</span>';
    }).join('');
    return '<div class="hm-card"><div class="hm-h">Direction <b class="' + dirc + '">' + md.dir + '</b><span class="hm-sub">' + md.bear + ' say down, ' + md.bull + ' say up, of ' + md.n + '</span></div>' + s + '<div class="hm-vcs">' + chips + '</div></div>';
  }
  // Pulse grid: one row per timeframe; cells coloured green (buyers) / red (sellers) / grey; divergence words in the row.
  function pulseCard(ctx) {
    var g = ctx.pulse;
    if (!g) return '<div class="hm-card"><div class="hm-h">Indicators</div><div class="hm-nid">Binance candles NOT_IN_DATA (pulse.js or feed missing)</div></div>';
    var cc = function (v) { return v === 1 ? 'up' : v === -1 ? 'down' : v === 0 ? 'dim' : 'nid'; };
    var rows = g.rows.map(function (x) {
      var r = x.r;
      if (!r) return '<div class="hm-pr"><b>' + x.tf + '</b><span class="hm-pc nid" style="grid-column:span 5">not enough candles yet</span></div>';
      var dv = [['rsi', 'RSI'], ['wt', 'WT'], ['cvd', 'CVD']].filter(function (k) { return r.div[k[0]]; })
        .map(function (k) { return '<i class="' + cc(r.div[k[0]]) + '">' + k[1] + (r.div[k[0]] > 0 ? '↑' : '↓') + '</i>'; }).join('');
      return '<div class="hm-pr"><b>' + x.tf + '</b>' +
        '<span class="hm-pc ' + cc(r.v.rsi) + '">' + (isFinite(r.rsi) ? Math.round(r.rsi) : '--') + '</span>' +
        '<span class="hm-pc ' + cc(r.v.wt) + '">' + (r.v.wt === 1 ? '▲' : r.v.wt === -1 ? '▼' : '--') + (isFinite(r.wt1) && Math.abs(r.wt1) >= 53 ? (r.wt1 > 0 ? ' hot' : ' cold') : '') + '</span>' +
        '<span class="hm-pc ' + cc(r.v.cvd) + '">' + (r.v.cvd === 1 ? '▲' : r.v.cvd === -1 ? '▼' : '--') + '</span>' +
        '<span class="hm-pd">' + (dv || '<em>-</em>') + '</span><span class="hm-pb ' + cc(r.bias) + '"></span></div>';
    }).join('');
    var pos = isFinite(g.lean) ? Math.round((g.lean + 1) * 50) : 50, dc = g.dir === 'UP' ? 'up' : g.dir === 'DOWN' ? 'down' : 'dim';
    return '<div class="hm-card"><div class="hm-h">Indicators lean <b class="' + dc + '">' + g.dir + '</b><span class="hm-sub">Binance spot; RSI, WaveTrend (WT), CVD = buyers minus sellers; arrows in Divergence = which way it points</span></div>' +
      '<div class="hm-lean"><span style="left:' + pos + '%"></span></div>' +
      '<div class="hm-pr hm-ph"><b></b><span>RSI</span><span>WT</span><span>CVD</span><span>Divergence</span><span>Lean</span></div>' + rows + '</div>';
  }
  // Liquidations: one column per window; red part = longs forced out, green part = shorts; height = share, total under it.
  var LIQ_WIN = [['1m', 60000], ['2m', 120000], ['3m', 180000], ['5m', 300000], ['7m', 420000], ['10m', 600000], ['15m', 900000], ['30m', 1800000], ['1h', 3600000], ['2h', 7200000], ['4h', 14400000]];
  function liqCard(ctx) {
    var l = ctx.liq; if (!l || !l.win) return '<div class="hm-card"><div class="hm-h">Liquidations</div><div class="hm-nid">no feed</div></div>';
    var cols = LIQ_WIN.map(function (w) {
      var s = l.win[w[0]] || { long: 0, short: 0 }, tot = s.long + s.short, pl = tot ? s.long / tot * 100 : 0, part = l.since && ctx.now - l.since < w[1];
      return '<div class="hm-lc' + (part ? ' part' : '') + '" title="' + w[0] + ': longs ' + usd(s.long) + ', shorts ' + usd(s.short) + (part ? ' (only since this page opened)' : '') + '">' +
        '<div class="hm-lcb' + (tot ? '' : ' empty') + '"><span class="up" style="height:' + (tot ? 100 - pl : 0) + '%"></span><span class="down" style="height:' + pl + '%"></span></div>' +
        '<b>' + w[0] + '</b><small>' + (tot ? usd(tot) : '0') + '</small></div>';
    }).join('');
    var w15 = l.win['15m'] || { long: 0, short: 0 }, word = !(w15.long + w15.short) ? '15 min quiet' : w15.long >= 2 * w15.short ? '15 min: longs forced out (selling fuel spent if price sits on a floor)' : w15.short >= 2 * w15.long ? '15 min: shorts forced out (buying fuel spent if price sits on a ceiling)' : '15 min: both sides';
    return '<div class="hm-card"><div class="hm-h">Liquidations <span class="hm-sub">red = longs forced out, green = shorts; faded = page not open that long</span></div><div class="hm-lcs">' + cols + '</div><div class="hm-say">' + esc(word) + '</div></div>';
  }
  function moneyCard(ctx) {
    var m = ctx.money;
    if (!m) return '<div class="hm-card"><div class="hm-h">Positions</div><div class="hm-nid">waiting for open-interest samples</div></div>';
    var ar = function (x, lab) { var c = x > 0.0005 ? 'up' : x < -0.0005 ? 'down' : 'dim'; return '<span class="hm-ar ' + c + '">' + (c === 'up' ? '▲' : c === 'down' ? '▼' : '◆') + '<small>' + lab + '</small></span>'; };
    return '<div class="hm-card"><div class="hm-h">Positions <span class="hm-sub">' + esc(m.label) + ', ' + m.n + ' venues (Deribit, Bybit; Binance blocked here)</span></div><div class="hm-mon">' + ar(m.dp, 'price') + ar(m.doi, 'open positions') + '<span class="hm-say">' + esc(m.text) + '</span></div></div>';
  }
  function newsCard(ctx) {
    var list = (ctx.news || []).filter(function (x) { return ctx.now - x.t <= 3600000; }).sort(function (a, b) { return b.score - a.score || b.t - a.t; }).slice(0, 4);
    var rows = list.map(function (x) {
      var c = x.tag === 'POSITIVE' ? 'up' : x.tag === 'NEGATIVE' ? 'down' : 'dim';
      return '<div class="hm-nr"><span class="hm-ni ' + c + '">' + (c === 'up' ? '▲' : c === 'down' ? '▼' : '◆') + '</span><span class="hm-ns"><span style="width:' + Math.min(100, x.score * 10) + '%"></span></span><span class="hm-nh">' + esc(x.head.slice(0, 90)) + '</span><span class="hm-na">' + Math.round((ctx.now - x.t) / 60000) + 'm</span></div>';
    }).join('') || '<div class="hm-nid">no headline in the last hour</div>';
    var ev = ctx.ev ? '<span class="hm-ev">' + esc(ctx.ev.name) + ' in ' + esc(ctx.ev.inTxt) + '</span>' : '';
    return '<div class="hm-card hm-news"><div class="hm-h">News, last hour <span class="hm-sub">▲ good for BTC ▼ bad; bar = weight 0-10</span>' + ev + '</div>' + rows + '</div>';
  }
  function render(el, ctx) {
    if (!el) return;
    var md = model(ctx), fl = flashes(ctx, md);
    var box = el.getBoundingClientRect(), W = Math.max(600, Math.round(box.width * 0.70)), H = Math.max(360, Math.round(box.height - 8));
    var head = '<div class="hm-top"><b class="hm-px">' + (md.px > 0 ? n0(md.px) : 'Price NOT_IN_DATA') + '</b>' +
      (md.lad.above[0] ? '<span class="hm-nx down">▲ ' + n0(md.lad.above[0].price) + ' <small>' + esc(md.lad.above[0].name) + ', ' + ((md.lad.above[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (md.lad.below[0] ? '<span class="hm-nx up">▼ ' + n0(md.lad.below[0].price) + ' <small>' + esc(md.lad.below[0].name) + ', ' + ((md.lad.below[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (ctx.scen && ctx.scen[0] ? '<span class="hm-nx dim">playbook: if up ' + n0(ctx.scen[0].up) + ' / if down ' + n0(ctx.scen[0].down) + '</span>' : '') + '</div>';
    el.innerHTML = '<div class="hm-chart">' + head + chart(ctx, md, W, H - 34) + '</div><div class="hm-rail">' + gauge(md) + pulseCard(ctx) + liqCard(ctx) + moneyCard(ctx) + newsCard(ctx) + '</div>';
  }
  var CSS = '#p-home{display:grid;grid-template-columns:70% 30%;gap:8px;padding:6px!important;overflow:hidden!important}' +
    '.hm-chart{position:relative;min-width:0;display:flex;flex-direction:column}.hm-svg{width:100%;flex:1;min-height:0}' +
    '.hm-top{display:flex;gap:14px;align-items:baseline;height:30px;white-space:nowrap;overflow:hidden}.hm-px{font:700 26px var(--mono,monospace);color:var(--amber)}.hm-nx{font:700 15px var(--mono,monospace)}.hm-nx small{font:12px system-ui;color:var(--dim)}' +
    '.hm-ses.s0{fill:#3b82f6;opacity:.05}.hm-ses.s1{fill:#a855f7;opacity:.06}.hm-ses.s2{fill:#f59e0b;opacity:.07}.hm-sest{fill:var(--dim);font:12px system-ui}' +
    '.hm-grid{stroke:var(--line);stroke-width:.5}.hm-ax{fill:var(--dim);font:11px var(--mono,monospace)}.hm-wk{stroke-width:1}.hm-wk.up{stroke:var(--up)}.hm-wk.down{stroke:var(--down)}.hm-bd.up{fill:var(--up)}.hm-bd.down{fill:var(--down)}' +
    '.hm-lv{stroke-width:1;stroke-dasharray:5 4;opacity:.75}.hm-lv.multi{stroke-width:2;stroke-dasharray:none;opacity:.6}.hm-lv.up{stroke:var(--up)}.hm-lv.down{stroke:var(--down)}' +
    '.hm-sc{stroke-width:3;opacity:.9}.hm-sc.up{stroke:var(--up)}.hm-sc.down{stroke:var(--down)}.hm-sct{font:700 12px system-ui}.hm-sct.up{fill:var(--up)}.hm-sct.down{fill:var(--down)}.hm-lead{stroke:var(--dim);stroke-width:.5}.hm-lt{font:12px system-ui;fill:var(--fg)}.hm-lt.up .hm-lp{fill:var(--up)}.hm-lt.down .hm-lp{fill:var(--down)}.hm-lp{font:700 12px var(--mono,monospace)}' +
    '.hm-uo{stroke:#60a5fa;stroke-width:2}.hm-uot{fill:#60a5fa;font:700 12px system-ui}.hm-now{stroke:var(--amber);stroke-width:1;stroke-dasharray:2 3}.hm-tag{fill:var(--amber)}.hm-tagt{fill:#111;font:700 12px var(--mono,monospace)}' +
    '.hm-rail{display:grid;grid-template-rows:auto auto auto auto 1fr;gap:6px;min-height:0;overflow:hidden}.hm-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px;min-height:0;overflow:hidden}' +
    '.hm-h{display:flex;gap:8px;align-items:baseline;font:600 13px system-ui;flex-wrap:wrap}.hm-h b{font:700 20px var(--mono,monospace)}.hm-sub{font:11px system-ui;color:var(--dim)}.up{color:var(--up)}.down{color:var(--down)}.dim{color:var(--dim)}' +
    '.hm-g{width:100%;max-height:78px}.hm-arc{fill:none;stroke-width:14}.hm-arc.up{stroke:var(--up)}.hm-arc.down{stroke:var(--down)}.hm-arc.dim{stroke:var(--line)}.hm-needle{stroke:var(--fg);stroke-width:3;stroke-linecap:round}.hm-hub{fill:var(--fg)}.hm-gl{font:700 12px system-ui}.hm-gl.up{fill:var(--up)}.hm-gl.down{fill:var(--down)}' +
    '.hm-vcs{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:12px}.hm-vc i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;background:var(--dim)}.hm-vc.up i{background:var(--up)}.hm-vc.down i{background:var(--down)}.hm-vc.nid i{background:transparent;border:1px dashed var(--dim)}.hm-vc{color:var(--fg)}' +
    '.hm-ms{display:flex;gap:8px;justify-content:space-between}.hm-mc{flex:1;text-align:center;font-size:12px}.hm-mb{position:relative;height:46px;background:var(--line);border-radius:4px;overflow:hidden}.hm-mb span{position:absolute;bottom:0;left:0;right:0;background:var(--dim)}.hm-mc.up .hm-mb span{background:var(--up)}.hm-mc.down .hm-mb span{background:var(--down)}.hm-mb em{position:absolute;left:0;right:0;bottom:50%;border-top:1px dashed var(--fg);opacity:.6}.hm-mc b{display:block}.hm-mc small{color:var(--dim)}' +
    '.hm-lr{display:grid;grid-template-columns:44px 1fr 92px;gap:6px;align-items:center;font-size:12px;margin-top:3px}.hm-lb{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--line)}.hm-lb span.down{background:var(--down)}.hm-lb span.up{background:var(--up)}.hm-lb.empty span{opacity:0}.hm-lv2{text-align:right;font-family:var(--mono,monospace)}.hm-say{font-size:12px;color:var(--fg);margin-top:3px}' +
    '.hm-pr{display:grid;grid-template-columns:30px 34px 52px 30px 1fr 14px;gap:3px;align-items:center;font-size:11px;line-height:15px}.hm-pr>b{font:700 11px var(--mono,monospace)}.hm-ph span{color:var(--dim);font-size:10px}' +
    '.hm-pc{text-align:center;border-radius:3px;font:700 11px var(--mono,monospace);color:#111}.hm-pc.up{background:var(--up)}.hm-pc.down{background:var(--down);color:#fff}.hm-pc.dim{background:var(--line);color:var(--fg)}.hm-pc.nid{background:transparent;color:var(--dim);font-weight:400}' +
    '.hm-pd i{font-style:normal;font-weight:700;margin-right:5px}.hm-pd em{color:var(--dim);font-style:normal}.hm-pb{height:12px;border-radius:3px;background:var(--line)}.hm-pb.up{background:var(--up)}.hm-pb.down{background:var(--down)}' +
    '.hm-lean{position:relative;height:8px;margin:3px 0 4px;border-radius:4px;background:linear-gradient(90deg,var(--down),var(--line) 40%,var(--line) 60%,var(--up))}.hm-lean span{position:absolute;top:-3px;width:4px;height:14px;margin-left:-2px;background:var(--fg);border-radius:2px}' +
    '.hm-lcs{display:flex;gap:3px}.hm-lc{flex:1;text-align:center;font-size:10px;min-width:0}.hm-lc.part{opacity:.45}.hm-lcb{height:44px;display:flex;flex-direction:column;border-radius:3px;overflow:hidden;background:var(--line)}.hm-lcb .up{background:var(--up)}.hm-lcb .down{background:var(--down)}.hm-lc b{display:block;font:700 10px var(--mono,monospace)}.hm-lc small{color:var(--dim);font-size:9px}' +
    '.hm-mon{display:flex;gap:12px;align-items:center}.hm-ar{font-size:22px;text-align:center;line-height:1}.hm-ar small{display:block;font-size:10px;color:var(--dim)}' +
    '.hm-nr{display:grid;grid-template-columns:16px 40px 1fr 30px;gap:6px;align-items:center;font-size:12px;padding:2px 0;border-top:1px solid var(--line)}.hm-ns{height:6px;background:var(--line);border-radius:3px;overflow:hidden}.hm-ns span{display:block;height:100%;background:var(--amber)}.hm-nh{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hm-na{color:var(--dim);text-align:right}.hm-ev{margin-left:auto;font:700 12px system-ui;color:var(--amber);border:1px solid var(--amber);border-radius:10px;padding:0 8px}' +
    '.hm-nid{color:var(--dim);font-size:12px;padding:6px 0}' +
    '#flash{display:none;gap:6px;flex-direction:column}#flash.on{display:flex}#flash .fl{padding:6px 12px;border-radius:6px;font:700 15px system-ui;color:#111;animation:hmfl 1s ease-in-out 6}#flash .fl.up{background:var(--up)}#flash .fl.down{background:var(--down);color:#fff}#flash .fl.amber{background:var(--amber)}' +
    '@keyframes hmfl{50%{opacity:.35}}';
  function injectCss(doc) { if (!doc || doc.getElementById('hm-css')) return; var st = doc.createElement('style'); st.id = 'hm-css'; st.textContent = CSS; doc.head.appendChild(st); }
  var api = { model: model, zoneName: zoneName, flashes: flashes, render: render, injectCss: injectCss, WORDS: WORDS, _FL: FL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAHOME = api;
})(typeof window !== 'undefined' ? window : this);
