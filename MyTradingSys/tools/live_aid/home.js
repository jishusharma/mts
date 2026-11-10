// Live Aid HOME tab (operator 2026-11-09 14:40Z): the one screen he watches while trading. Full viewport, no page scroll,
// pictures over words: a candle chart with every level drawn and named in plain words, sessions and the US open marked on
// the chart, plus a side rail (direction gauge, momentum squares, liquidation bar, money arrows, news with impact).
// A flash bar fires on big news, liquidation bursts and level touches. Observation only: no order, no size, no entry wording.
// Thresholds marked OURS were chosen here, not measured. Pure model() for tests; render() draws.
(function (root) {
  'use strict';
  var REG = (typeof module !== 'undefined' && module.exports) ? require('./level_registry.js') : root.LEVELREG;
  var BIG_PRINT = 250000, BURST_1M = 1000000, TOUCH = 0.0005, NEWS_HI = 7, NEWS_FRESH = 180000;   // OURS
  var FLASH_MS = { news: 90000, liq: 60000, touch: 45000, setup: 180000, idea: 300000 };
  var VOTE_NAMES = ['Analysts', 'Price vs day average', 'RSI 1h', 'RSI 4h', 'Breakout', 'Playbook'];
  var WORDS = { PDH: 'Yesterday high', PDL: 'Yesterday low', PDC: 'Yesterday close', PWH: 'Last week high', PWL: 'Last week low', DO: 'Day open',
                WO: 'Week open', WH: 'Week high', WL: 'Week low', VAL: 'Yesterday value low', POC: 'Yesterday busiest price', VAH: 'Yesterday value high', DH: 'Today high', DL: 'Today low', VWAP: 'Day average price' };
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
    // ideas at two levels pointing opposite ways cancel: no flash (operator 11-10: buy flashes that turned into shorts)
    var ideas = (stories(ctx, md) || []).filter(function (st) { return st && st.idea; }), mixed = ideas.some(function (st) { return st.idea !== ideas[0].idea; });
    (mixed ? [] : ideas.slice(0, 1)).forEach(function (st) { var ik = 'i' + st.idea + Math.round(st.price) + st.state + Math.floor(now / 900000);
      if (!FL.seen[ik]) FL.list = FL.list.filter(function (f) { return f.kind !== 'idea'; });
      add(ik, 'idea', st.idea === 'SHORT' ? 'down' : 'up', st.idea + ' IDEA (coin flip so far): ' + st.why + ' (' + st.ev.filter(function (e) { return e.cls === (st.state === 'ACCEPTED' ? 'thru' : 'turn'); }).map(function (e) { return e.t; }).slice(0, 3).join(', ') + '). ' + st.valid + ' (your call)'); });
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
    var d0 = Math.floor(t0 / 86400000) * 86400000, labEnd = -1e9;
    [d0 - 86400000, d0, d0 + 86400000].forEach(function (day) {
      SESS.forEach(function (ss, i) {
        var xa = Math.max(L, x(day + ss[1] * 3600000) - cw / 2), xb = Math.min(R, x(day + ss[2] * 3600000) - cw / 2);
        if (xb - xa < 10) return;
        s += '<rect x="' + xa + '" y="' + T + '" width="' + (xb - xa) + '" height="' + (B - T) + '" class="hm-ses s' + i + '"/>';
        // label only where it fits: never on top of the previous one (operator 11-10 screenshot: Asia and Europe overprinted)
        var txt = ss[0] + ' ' + String(ss[1]).padStart(2, '0') + ':00-' + ss[2] + ':00Z', tx = Math.max(xa + 6, labEnd + 10);
        if (tx + txt.length * 6.5 > xb && xb - xa < txt.length * 6.5) txt = ss[0];
        if (tx + txt.length * 6.5 > R) return;
        s += '<text x="' + tx + '" y="' + (T - 8) + '" class="hm-sest">' + txt + '</text>';
        labEnd = tx + txt.length * 6.5;
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
    // volume (operator 11-10): Binance spot 5m bars in the bottom band, green = buyers took more (taker buy > sell), red = sellers;
    // yellow line = cumulative delta (CVD) over the bars shown. Same time axis as the candles.
    var kv = (ctx.k5 || []).filter(function (r) { return +r[0] >= t0; });
    if (kv.length > 3) {
      var vb = B - 2, vh = (B - T) * 0.16, vmax = 0, cum = 0, cmin = 0, cmax = 0, pts = [];
      kv.forEach(function (r) { vmax = Math.max(vmax, +r[5]); cum += 2 * +r[9] - +r[5]; cmin = Math.min(cmin, cum); cmax = Math.max(cmax, cum); pts.push([x(+r[0]), cum]); });
      s += '<text x="' + (L + 2) + '" y="' + (vb - vh - 3) + '" class="hm-vlt">Volume 5m (green buyers, red sellers) · yellow = CVD</text>';
      kv.forEach(function (r) {
        var hh = vmax ? +r[5] / vmax * vh : 0, d = 2 * +r[9] - +r[5];
        s += '<rect x="' + (x(+r[0]) - cw * 0.36) + '" y="' + (vb - hh) + '" width="' + (cw * 0.72) + '" height="' + hh + '" class="hm-vb ' + (d >= 0 ? 'up' : 'down') + '"/>';
      });
      var cy2 = function (v) { return vb - (cmax > cmin ? (v - cmin) / (cmax - cmin) : 0.5) * vh; };
      s += '<polyline points="' + pts.map(function (p) { return p[0].toFixed(1) + ',' + cy2(p[1]).toFixed(1); }).join(' ') + '" class="hm-cvd"/>';
    }
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
  // Indicator read (operator 11-10: the 11-row grid was clutter; he wants what Volume Flow, Squeeze, ADX say). indread.js builds it:
  // one row per indicator, one cell per timeframe (15m frame, 1h bias, 4h context), then up to 3 plain sentences.
  function indCard(ctx) {
    var T = ctx.ind, sub = '<span class="hm-sub" title="Closed Binance spot bars. Volume Flow, Squeeze Momentum, WaveTrend: LazyBear defaults; ADX/DI 14: Wilder. Green = up, red = down, grey = neutral, amber = coiled. The sentences are our rules, not backtested as a set.">closed bars · rules ours, not backtested</span>';
    if (!T) return '<div class="hm-card"><div class="hm-h">What the indicators say</div><div class="hm-nid">Binance candles NOT_IN_DATA (indread.js or feed missing)</div></div>';
    var cc = function (v) { return v === 1 ? 'up' : v === -1 ? 'down' : v === 0 ? 'dim' : 'nid'; };
    var head = '<div class="hm-ir hm-ih"><b></b>' + T.tfs.map(function (x) { return '<span><b>' + x[0] + '</b> ' + x[2] + '</span>'; }).join('') + '</div>';
    var rows = T.rows.map(function (r) {
      return '<div class="hm-ir"><b>' + r[1] + '</b>' + T.tfs.map(function (x) { var R = T.r[x[0]], c = R ? R.cells[r[0]] : null;
        return '<span class="hm-pc ' + (c ? cc(c.v) + (c.on ? ' coil' : '') : 'nid') + '">' + esc(c ? c.txt : 'no candles') + '</span>'; }).join('') + '</div>';
    }).join('');
    var tally = '<div class="hm-ir hm-it"><b>Agree</b>' + T.tfs.map(function (x) { var R = T.r[x[0]];
      return '<span class="' + (!R ? 'dim' : R.dn > R.up ? 'down' : R.up > R.dn ? 'up' : 'dim') + '">' + (R ? R.dn + ' down · ' + R.up + ' up' : '--') + '</span>'; }).join('') + '</div>';
    var says = (T.says || []).map(function (s) { return '<div class="hm-is ' + s.cls + '">' + esc(s.t) + '</div>'; }).join('');
    // feed stalled: the cells are old bars, say so before the reader trusts them (e2e test 11-10)
    if (T.stale) says = '<div class="hm-is amber">STALE: last 15m candle closed ' + Math.round(T.age / 60000) + ' min ago (feed stalled?) - these readings are old</div>' + says;
    return '<div class="hm-card"><div class="hm-h">What the indicators say' + sub + '</div>' + head + rows + tally + says + '</div>';
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
  // Venues that answered this cycle with their share of the open positions in BTC: "Bybit 38% + Hyperliquid 27% + ..." (operator 11-10)
  function venueWords(m) {
    var v = (m.venues || []).slice().sort(function (a, b) { return b.btc - a.btc; });
    if (!v.length) return m.n + ' venue' + (m.n === 1 ? '' : 's');
    return v.map(function (x) { return x.name + (isFinite(x.share) && v.length > 1 ? ' ' + Math.round(x.share * 100) + '%' : ''); }).join(' + ');
  }
  function moneyCard(ctx) {
    var m = ctx.money;
    if (!m) return '<div class="hm-card"><div class="hm-h">Positions</div><div class="hm-nid">waiting for open-interest samples</div></div>';
    var ar = function (x, lab) { var c = x > 0.0005 ? 'up' : x < -0.0005 ? 'down' : 'dim'; return '<span class="hm-ar ' + c + '">' + (c === 'up' ? '▲' : c === 'down' ? '▼' : '◆') + '<small>' + lab + '</small></span>'; };
    return '<div class="hm-card"><div class="hm-h">Positions <span class="hm-sub" title="' + esc((m.missing && m.missing.length ? 'Not read: ' + m.missing.join('; ') : 'All venues read')) + '">change over the last ' + esc(m.label) + ' \u00b7 from ' + esc(venueWords(m)) + '</span></div><div class="hm-mon">' + ar(m.dp, 'price') + ar(m.doi, 'open positions') + '<span class="hm-say">' + esc(m.text) + '</span></div></div>';
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
  // Timing check strip (operator 11-10: the one cross worth a look, as lights not text). pulse.js timing() decides; this only draws:
  // badge (solid green / red = all five agree, amber = some, grey = no trigger) then one pill per light. A pill's colour is its
  // own direction (green up, red down, amber = at a level, grey = none); a faded pill does not agree with the trigger.
  var TM_LAB = { trigger: 'Big dot', '15m': '15m', '30m': '30m', level: 'Level', tape: 'Tape' };
  function nearLevel(md, PU) {
    if (!md || !md.lad || !(md.px > 0) || !PU) return null;
    var c = [md.lad.at, md.lad.above[0], md.lad.below[0]].filter(function (z) { return z && Math.abs(md.px / z.price - 1) <= PU.P.near; })
      .sort(function (a, b) { return Math.abs(md.px - a.price) - Math.abs(md.px - b.price); });
    return c[0] || null;
  }
  function timingOf(ctx, md) {
    var PU = (typeof module !== 'undefined' && module.exports) ? require('./pulse.js') : root.LAPULSE;
    if (!PU || !PU.timing) return null;
    try { return PU.timing(ctx.lanes, nearLevel(md, PU)); } catch (e) { return null; }
  }
  function timingStrip(T) {
    if (!T) return '<div class="hm-tm none"><b class="hm-tmb">Timing check</b><span class="hm-tmx">pulse.js missing</span></div>';
    var sy = function (v) { return v === 1 ? '▲' : v === -1 ? '▼' : '○'; }, cl = function (v) { return v === 1 ? 'up' : v === -1 ? 'down' : 'dim'; };
    var st = T.state === 'ALIGNED' ? 'all ' + cl(T.side) : T.state === 'PARTIAL' ? 'part' : 'none';
    var badge = T.state === 'ALIGNED' ? 'WORTH A LOOK ' + sy(T.side) : T.state === 'PARTIAL' ? sy(T.side) + ' ' + T.n + ' of ' + T.of + ' lined up' : 'no trigger';
    var pills = T.lights.map(function (x) {
      var c = x.k === 'level' ? (x.v ? 'amber' : 'dim') : cl(x.v), s = x.k === 'level' ? (x.v ? '◆' : '◇') : x.k === 'trigger' ? (x.v ? '●' + sy(x.v) : '○') : sy(x.v);
      return '<span class="hm-tl ' + c + (x.ok ? ' tly' : ' tln') + '" title="' + esc(x.t) + '"><i>' + s + '</i>' + TM_LAB[x.k] + (x.k === 'trigger' && T.trig ? ' <small>' + T.trig.tf + '</small>' : '') + '<em>' + (x.ok ? '✓' : '') + '</em></span>';
    }).join('');
    return '<div class="hm-tm ' + st + '" title="The one WaveTrend cross worth a look: a big dot on 1m / 2m / 3m that agrees with 15m and 30m, at a named level, with the tape. Observation only, no entry or size. Rules ours, not backtested."><b class="hm-tmb">' + badge + '</b>' + pills + '</div>';
  }
  // WaveTrend lanes (operator 11-10): 1m 2m 3m = timing crosses, 15m 30m = the frame, 4h = context only (its crosses are too frequent
  // to act on, so no dots there). Green line wt1, red line wt2 (TradingView WT_CROSS colours); dot = cross, big dot = cross from
  // overbought/oversold (beyond +-53). Each lane keeps its own time scale: the last 60 bars of that timeframe.
  var LANES = [['1m', 'timing'], ['2m', 'timing'], ['3m', 'timing'], ['15m', 'frame'], ['30m', 'frame'], ['4h', 'context']];
  function wtLanes(ctx, W, H) {
    var PU = (typeof module !== 'undefined' && module.exports) ? require('./pulse.js') : root.LAPULSE;
    var lanes = ctx.lanes || {}, lh = H / LANES.length, L = 52, R = W - 300, s = '<svg class="hm-wts" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" style="height:' + H + 'px">';
    s += '<text x="4" y="11" class="hm-wth">WaveTrend</text>';
    LANES.forEach(function (ln, i) {
      var top = i * lh, mid = top + lh / 2, Lz = lanes[ln[0]], sc = (lh / 2 - 2) / 70, yv = function (v) { return mid - Math.max(-70, Math.min(70, v)) * sc; };
      if (i && LANES[i - 1][1] !== ln[1]) s += '<line x1="0" x2="' + W + '" y1="' + top + '" y2="' + top + '" class="hm-wtsep"/>';
      s += '<text x="4" y="' + (mid + 4) + '" class="hm-wtl">' + ln[0] + '</text><text x="4" y="' + (mid + 15) + '" class="hm-wtk">' + ln[1] + '</text>';
      s += '<line x1="' + L + '" x2="' + R + '" y1="' + mid + '" y2="' + mid + '" class="hm-wt0"/>';
      [WTH(PU), -WTH(PU)].forEach(function (b) { s += '<line x1="' + L + '" x2="' + R + '" y1="' + yv(b) + '" y2="' + yv(b) + '" class="hm-wtb"/>'; });
      var bars = Lz && Lz.bars || [], nb = bars.length, xw = (R - L) / Math.max(nb, 1), xi = function (j) { return L + (j + 0.5) * xw; };
      var line = function (key, cls) { var p = []; bars.forEach(function (b, j) { if (isFinite(b[key])) p.push(xi(j).toFixed(1) + ',' + yv(b[key]).toFixed(1)); }); return p.length > 1 ? '<polyline points="' + p.join(' ') + '" class="' + cls + '"/>' : ''; };
      s += line('wt2', 'hm-w2') + line('wt1', 'hm-w1');
      var tg = ctx._tm && ctx._tm.trig && ctx._tm.trig.tf === ln[0] ? nb - 1 - ctx._tm.trig.ago : -1;   // the timing-check trigger gets a ring
      if (tg >= 0 && bars[tg]) s += '<circle cx="' + xi(tg) + '" cy="' + yv(bars[tg].wt1) + '" r="9" class="hm-wxr ' + (ctx._tm.trig.side > 0 ? 'up' : 'down') + '"/>';
      if (ln[1] !== 'context') bars.forEach(function (b, j) { if (b.x) s += '<circle cx="' + xi(j) + '" cy="' + yv(b.wt1) + '" r="' + (b.strong ? 4.5 : 2.5) + '" class="hm-wx ' + (b.x > 0 ? 'up' : 'down') + '"/>'; });
      var words = PU ? PU.laneWords(Lz) : 'pulse.js missing', c = !Lz ? 'dim' : Lz.side === 1 ? 'up' : Lz.side === -1 ? 'down' : 'dim';
      if (ln[1] === 'context' && Lz) words = (Lz.side === 1 ? 'rising' : Lz.side === -1 ? 'falling' : 'flat') + (Lz.zone === 'hot' ? ', overbought' : Lz.zone === 'cold' ? ', oversold' : '') + ' (context only)';
      s += '<text x="' + (R + 8) + '" y="' + (mid + 4) + '" class="hm-wtw ' + c + '">' + (Lz && isFinite(Lz.wt1) ? '<tspan class="hm-wtn">' + Math.round(Lz.wt1) + '</tspan> ' : '') + esc(words) + '</text>';
    });
    return s + '</svg>';
  }
  function WTH(PU) { return PU && PU.WT_HOT || 53; }
  // Level story: nearest level above and below (or the one price sits at), read on completed 15m Binance closes (levelstory.js).
  function stories(ctx, md) {
    var LS = (typeof module !== 'undefined' && module.exports) ? require('./levelstory.js') : root.LASTORY;
    if (!LS || !ctx.k15 || !md || !md.lad) return null;
    if (ctx._st && ctx._st.md === md) return ctx._st.v;
    var ex = { wt15: ctx.lanes && ctx.lanes['15m'], doi: ctx.money ? ctx.money.doi : NaN }, lv = [];
    if (md.lad.at) lv.push(md.lad.at);
    if (md.lad.above[0] && lv.indexOf(md.lad.above[0]) < 0) lv.push(md.lad.above[0]);
    if (md.lad.below[0] && lv.length < 2) lv.push(md.lad.below[0]);
    var v = lv.map(function (z) { try { return LS.story(z, ctx.k15, ctx.now, ex); } catch (e) { return null; } });
    ctx._st = { md: md, v: v }; return v;
  }
  var ST_CLS = { 'REJECTED': 'turn', 'FAILED BREAK': 'turn', 'ACCEPTED': 'thru', 'BREAKING': 'thru', 'TESTING': 'amber', 'APPROACHING': 'amber', 'AWAY': 'dim' };
  function storyCard(ctx, md) {
    var v = stories(ctx, md);
    if (!v) return '<div class="hm-card"><div class="hm-h">At the level</div><div class="hm-nid">15m candles NOT_IN_DATA</div></div>';
    var rows = v.filter(Boolean).map(function (st) {
      var sc = ST_CLS[st.state] || 'dim', idea = st.idea ? '<b class="hm-idea ' + (st.idea === 'SHORT' ? 'down' : 'up') + '">' + st.idea + ' IDEA</b>' : '';
      var chips = st.ev.map(function (e) { return '<span class="hm-ec ' + e.cls + '" title="' + esc(e.t) + '">' + esc(e.k) + '</span>'; }).join('');
      return '<div class="hm-st"><div class="hm-st1"><span class="hm-stp ' + (st.res ? 'down' : 'up') + '">' + n0(st.price) + '</span> <span class="hm-stn">' + esc(st.name) + '</span>' +
        '<span class="hm-sts ' + sc + '">' + st.state + '</span>' + idea + '</div>' +
        '<div class="hm-ecs">' + (chips || '<em>no evidence yet</em>') + '<span class="hm-sc2">turn ' + st.turn + ' / through ' + st.thru + '</span></div>' +
        '<div class="hm-stv">' + esc(st.valid) + (st.crowd ? '<br><span class="amber">' + esc(st.crowd) + '</span>' : '') + '</div></div>';
    }).join('');
    var id2 = v.filter(function (st) { return st && st.idea; }), mx = id2.length > 1 && id2.some(function (st) { return st.idea !== id2[0].idea; });
    return '<div class="hm-card"><div class="hm-h">At the level ' + (mx ? '<b class="amber" style="font-size:13px">MIXED: levels disagree, no idea</b>' : '') + '<span class="hm-sub" title="Read on 15m closes. Green chip = evidence for a turn, red = for going through. Measured over 180 days: ideas right 49 % (n 2,852), a coin flip, not an edge (research/level_story_1110).">15m closes · measured 49 % right: a coin flip</span></div>' + (rows || '<div class="hm-nid">no level near</div>') + '</div>';
  }
  function render(el, ctx) {
    if (!el) return;
    var md = model(ctx), fl = flashes(ctx, md);
    var box = el.getBoundingClientRect(), W = Math.max(600, Math.round(box.width * 0.70)), H = Math.max(360, Math.round(box.height - 8));
    var head = '<div class="hm-top"><b class="hm-px">' + (md.px > 0 ? n0(md.px) : 'Price NOT_IN_DATA') + '</b>' +
      (md.lad.above[0] ? '<span class="hm-nx down">▲ ' + n0(md.lad.above[0].price) + ' <small>' + esc(md.lad.above[0].name) + ', ' + ((md.lad.above[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (md.lad.below[0] ? '<span class="hm-nx up">▼ ' + n0(md.lad.below[0].price) + ' <small>' + esc(md.lad.below[0].name) + ', ' + ((md.lad.below[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (ctx.scen && ctx.scen[0] ? '<span class="hm-nx dim">playbook: if up ' + n0(ctx.scen[0].up) + ' / if down ' + n0(ctx.scen[0].down) + '</span>' : '') + '</div>';
    var wh = Math.round(Math.min(300, Math.max(150, (H - 34) * 0.32)));
    ctx._tm = timingOf(ctx, md);
    el.innerHTML = '<div class="hm-chart">' + head + chart(ctx, md, W, H - 72 - wh) + timingStrip(ctx._tm) + wtLanes(ctx, W, wh) + '</div><div class="hm-rail">' + gauge(md) + storyCard(ctx, md) + indCard(ctx) + liqCard(ctx) + moneyCard(ctx) + newsCard(ctx) + '</div>';
  }
  var CSS = '#p-home{display:grid;grid-template-columns:70% 30%;gap:8px;padding:6px!important;overflow:hidden!important}' +
    '.hm-chart{position:relative;min-width:0;display:flex;flex-direction:column}.hm-svg{width:100%;flex:1;min-height:0}' +
    '.hm-top{display:flex;gap:14px;align-items:baseline;height:30px;white-space:nowrap;overflow:hidden}.hm-px{font:700 26px var(--mono,monospace);color:var(--amber)}.hm-nx{font:700 15px var(--mono,monospace)}.hm-nx small{font:12px system-ui;color:var(--dim)}' +
    '.hm-ses.s0{fill:#3b82f6;opacity:.05}.hm-ses.s1{fill:#a855f7;opacity:.06}.hm-ses.s2{fill:#f59e0b;opacity:.07}.hm-sest{fill:var(--dim);font:12px system-ui}' +
    '.hm-grid{stroke:var(--line);stroke-width:.5}.hm-ax{fill:var(--dim);font:11px var(--mono,monospace)}.hm-wk{stroke-width:1}.hm-wk.up{stroke:var(--up)}.hm-wk.down{stroke:var(--down)}.hm-bd.up{fill:var(--up)}.hm-bd.down{fill:var(--down)}' +
    '.hm-lv{stroke-width:1;stroke-dasharray:5 4;opacity:.75}.hm-lv.multi{stroke-width:2;stroke-dasharray:none;opacity:.6}.hm-lv.up{stroke:var(--up)}.hm-lv.down{stroke:var(--down)}' +
    '.hm-sc{stroke-width:3;opacity:.9}.hm-sc.up{stroke:var(--up)}.hm-sc.down{stroke:var(--down)}.hm-sct{font:700 12px system-ui}.hm-sct.up{fill:var(--up)}.hm-sct.down{fill:var(--down)}.hm-lead{stroke:var(--dim);stroke-width:.5}.hm-lt{font:12px system-ui;fill:var(--fg)}.hm-lt.up .hm-lp{fill:var(--up)}.hm-lt.down .hm-lp{fill:var(--down)}.hm-lp{font:700 12px var(--mono,monospace)}' +
    '.hm-uo{stroke:#60a5fa;stroke-width:2}.hm-uot{fill:#60a5fa;font:700 12px system-ui}.hm-now{stroke:var(--amber);stroke-width:1;stroke-dasharray:2 3}.hm-tag{fill:var(--amber)}.hm-tagt{fill:#111;font:700 12px var(--mono,monospace)}' +
    '.hm-rail{display:grid;grid-template-rows:auto auto auto auto auto 1fr;gap:6px;min-height:0;overflow:hidden}.hm-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px;min-height:0;overflow:hidden}' +
    '.hm-h{display:flex;gap:8px;align-items:baseline;font:600 13px system-ui;flex-wrap:wrap}.hm-h b{font:700 20px var(--mono,monospace)}.hm-sub{font:11px system-ui;color:var(--dim)}.up{color:var(--up)}.down{color:var(--down)}.dim{color:var(--dim)}' +
    '.hm-g{width:100%;max-height:78px}.hm-arc{fill:none;stroke-width:14}.hm-arc.up{stroke:var(--up)}.hm-arc.down{stroke:var(--down)}.hm-arc.dim{stroke:var(--line)}.hm-needle{stroke:var(--fg);stroke-width:3;stroke-linecap:round}.hm-hub{fill:var(--fg)}.hm-gl{font:700 12px system-ui}.hm-gl.up{fill:var(--up)}.hm-gl.down{fill:var(--down)}' +
    '.hm-vcs{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:12px}.hm-vc i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;background:var(--dim)}.hm-vc.up i{background:var(--up)}.hm-vc.down i{background:var(--down)}.hm-vc.nid i{background:transparent;border:1px dashed var(--dim)}.hm-vc{color:var(--fg)}' +
    '.hm-ms{display:flex;gap:8px;justify-content:space-between}.hm-mc{flex:1;text-align:center;font-size:12px}.hm-mb{position:relative;height:46px;background:var(--line);border-radius:4px;overflow:hidden}.hm-mb span{position:absolute;bottom:0;left:0;right:0;background:var(--dim)}.hm-mc.up .hm-mb span{background:var(--up)}.hm-mc.down .hm-mb span{background:var(--down)}.hm-mb em{position:absolute;left:0;right:0;bottom:50%;border-top:1px dashed var(--fg);opacity:.6}.hm-mc b{display:block}.hm-mc small{color:var(--dim)}' +
    '.hm-lr{display:grid;grid-template-columns:44px 1fr 92px;gap:6px;align-items:center;font-size:12px;margin-top:3px}.hm-lb{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--line)}.hm-lb span.down{background:var(--down)}.hm-lb span.up{background:var(--up)}.hm-lb.empty span{opacity:0}.hm-lv2{text-align:right;font-family:var(--mono,monospace)}.hm-say{font-size:12px;color:var(--fg);margin-top:3px}' +
    '.hm-pr{display:grid;grid-template-columns:30px 34px 52px 30px 1fr 14px;gap:3px;align-items:center;font-size:11px;line-height:15px}.hm-pr>b{font:700 11px var(--mono,monospace)}.hm-ph span{color:var(--dim);font-size:10px}' +
    '.hm-pc{text-align:center;border-radius:3px;font:700 11px var(--mono,monospace);color:#111}.hm-pc.up{background:var(--up)}.hm-pc.down{background:var(--down);color:#fff}.hm-pc.dim{background:var(--line);color:var(--fg)}.hm-pc.nid{background:transparent;color:var(--dim);font-weight:400}' +
    '.hm-ir{display:grid;grid-template-columns:76px 1fr 1fr 1fr;gap:3px;align-items:center;font-size:11px;line-height:16px;margin-top:2px}.hm-ir>b{font:600 11px system-ui}.hm-ih span{color:var(--dim);font-size:10px;text-align:center}.hm-ih span b{color:var(--fg);font:700 11px var(--mono,monospace)}' +
    '.hm-ir .hm-pc{white-space:nowrap;overflow:hidden}.hm-pc.coil{background:var(--amber);color:#111}.hm-it span{text-align:center;font:700 11px system-ui}.hm-is{font-size:12px;margin-top:3px;padding-left:8px;border-left:3px solid currentColor}.hm-is.dim{color:var(--fg);border-left-color:var(--dim)}' +
    '.hm-pd i{font-style:normal;font-weight:700;margin-right:5px}.hm-pd em{color:var(--dim);font-style:normal}.hm-pb{height:12px;border-radius:3px;background:var(--line)}.hm-pb.up{background:var(--up)}.hm-pb.down{background:var(--down)}' +
    '.hm-leanw{display:flex;gap:6px;align-items:center;font:700 10px system-ui;margin:3px 0 4px}.hm-leanw .hm-lean{flex:1;margin:0}.hm-lean i{position:absolute;top:0;bottom:0;border-left:1px dashed var(--fg);opacity:.5}' +
    '.hm-lean{position:relative;height:8px;margin:3px 0 4px;border-radius:4px;background:linear-gradient(90deg,var(--down),var(--line) 40%,var(--line) 60%,var(--up))}.hm-lean span{position:absolute;top:-3px;width:4px;height:14px;margin-left:-2px;background:var(--fg);border-radius:2px}' +
    '.hm-lcs{display:flex;gap:3px}.hm-lc{flex:1;text-align:center;font-size:10px;min-width:0}.hm-lc.part{opacity:.45}.hm-lcb{height:44px;display:flex;flex-direction:column;border-radius:3px;overflow:hidden;background:var(--line)}.hm-lcb .up{background:var(--up)}.hm-lcb .down{background:var(--down)}.hm-lc b{display:block;font:700 10px var(--mono,monospace)}.hm-lc small{color:var(--dim);font-size:9px}' +
    '.hm-mon{display:flex;gap:12px;align-items:center}.hm-ar{font-size:22px;text-align:center;line-height:1}.hm-ar small{display:block;font-size:10px;color:var(--dim)}' +
    '.hm-nr{display:grid;grid-template-columns:16px 40px 1fr 30px;gap:6px;align-items:center;font-size:12px;padding:2px 0;border-top:1px solid var(--line)}.hm-ns{height:6px;background:var(--line);border-radius:3px;overflow:hidden}.hm-ns span{display:block;height:100%;background:var(--amber)}.hm-nh{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hm-na{color:var(--dim);text-align:right}.hm-ev{margin-left:auto;font:700 12px system-ui;color:var(--amber);border:1px solid var(--amber);border-radius:10px;padding:0 8px}' +
    '.hm-nid{color:var(--dim);font-size:12px;padding:6px 0}' +
    '.hm-st{border-top:1px solid var(--line);padding:3px 0}.hm-st1{display:flex;gap:6px;align-items:baseline;font-size:12px}.hm-stp{font:700 13px var(--mono,monospace)}.hm-stn{color:var(--fg);overflow:hidden;white-space:nowrap;text-overflow:ellipsis;max-width:40%}' +
    '.hm-sts{margin-left:auto;font:700 11px system-ui;padding:0 6px;border-radius:8px;border:1px solid}.hm-sts.turn{color:#22c55e}.hm-sts.thru{color:#ef4444}.hm-sts.amber{color:var(--amber)}.hm-sts.dim{color:var(--dim)}' +
    '.hm-idea{font:700 12px system-ui!important;padding:0 6px;border-radius:4px;color:#111}.hm-idea.down{background:var(--down);color:#fff}.hm-idea.up{background:var(--up)}' +
    '.hm-ecs{display:flex;flex-wrap:wrap;gap:3px;margin-top:2px;align-items:center}.hm-ec{font:700 10px system-ui;padding:0 5px;border-radius:3px;background:var(--line);color:var(--fg)}.hm-ec.turn{background:#166534;color:#dcfce7}.hm-ec.thru{background:#7f1d1d;color:#fee2e2}.hm-sc2{margin-left:auto;color:var(--dim);font-size:10px}.hm-ecs em{color:var(--dim);font-size:11px}' +
    '.hm-stv{font-size:11px;color:var(--fg);margin-top:2px}.amber{color:var(--amber)}' +
    '.hm-vb{opacity:.55}.hm-vb.up{fill:var(--up)}.hm-vb.down{fill:var(--down)}.hm-cvd{fill:none;stroke:#facc15;stroke-width:1.5}.hm-vlt{fill:var(--dim);font:11px system-ui}' +
    '.hm-wts{width:100%;flex:none;border-top:1px solid var(--line)}.hm-wth{fill:var(--dim);font:700 10px system-ui}.hm-wtl{fill:var(--fg);font:700 13px var(--mono,monospace)}.hm-wtk{fill:var(--dim);font:10px system-ui}' +
    '.hm-wt0{stroke:var(--dim);stroke-width:.5;opacity:.6}.hm-wtb{stroke:var(--down);stroke-width:.5;stroke-dasharray:3 3;opacity:.6}.hm-wtsep{stroke:var(--line);stroke-width:1}' +
    '.hm-w1{fill:none;stroke:#22c55e;stroke-width:2}.hm-w2{fill:none;stroke:#ef4444;stroke-width:1.5}.hm-wx.up{fill:#22c55e}.hm-wx.down{fill:#ef4444}.hm-wx{stroke:#111;stroke-width:.5}' +
    '.hm-wxr{fill:none;stroke-width:2}.hm-wxr.up{stroke:#22c55e}.hm-wxr.down{stroke:#ef4444}' +
    '.hm-tm{display:flex;gap:6px;align-items:center;height:26px;flex:none;border-top:1px solid var(--line);padding:0 4px;white-space:nowrap;overflow:hidden}' +
    '.hm-tmb{font:700 12px system-ui;padding:2px 10px;border-radius:10px;border:1px solid var(--dim);color:var(--dim)}.hm-tm.part .hm-tmb{border-color:var(--amber);color:var(--amber)}' +
    '.hm-tm.all .hm-tmb{color:#111;border-color:transparent}.hm-tm.all.up .hm-tmb{background:var(--up)}.hm-tm.all.down .hm-tmb{background:var(--down);color:#fff}.hm-tmx{font-size:11px;color:var(--dim)}' +
    '.hm-tl{display:inline-flex;gap:4px;align-items:center;font:700 11px system-ui;padding:1px 8px;border-radius:4px;color:#111;background:var(--line)}.hm-tl i{font-style:normal}.hm-tl em{font-style:normal}.hm-tl small{font:10px var(--mono,monospace)}' +
    '.hm-tl.up{background:var(--up)}.hm-tl.down{background:var(--down);color:#fff}.hm-tl.amber{background:var(--amber)}.hm-tl.dim{color:var(--fg)}.hm-tl.tln{opacity:.4}.hm-tl.tly{outline:2px solid var(--fg);outline-offset:-2px}' +
    '.hm-wtw{font:12px system-ui;fill:var(--fg)}.hm-wtw.up{fill:var(--up)}.hm-wtw.down{fill:var(--down)}.hm-wtn{font:700 12px var(--mono,monospace)}' +
    '#flash{display:none;gap:6px;flex-direction:column}#flash.on{display:flex}#flash .fl{padding:6px 12px;border-radius:6px;font:700 15px system-ui;color:#111;animation:hmfl 1s ease-in-out 6}#flash .fl.up{background:var(--up)}#flash .fl.down{background:var(--down);color:#fff}#flash .fl.amber{background:var(--amber)}' +
    '@keyframes hmfl{50%{opacity:.35}}';
  function injectCss(doc) { if (!doc || doc.getElementById('hm-css')) return; var st = doc.createElement('style'); st.id = 'hm-css'; st.textContent = CSS; doc.head.appendChild(st); }
  var api = { model: model, zoneName: zoneName, flashes: flashes, render: render, injectCss: injectCss, WORDS: WORDS, _FL: FL, _moneyCard: moneyCard, _indCard: indCard, _stories: stories, _timingStrip: timingStrip, _nearLevel: nearLevel };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAHOME = api;
})(typeof window !== 'undefined' ? window : this);
