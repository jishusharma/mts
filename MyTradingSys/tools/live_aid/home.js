// Live Aid HOME tab (operator 2026-11-09 14:40Z): the one screen he watches while trading. Full viewport, no page scroll,
// pictures over words: a candle chart with every level drawn and named in plain words, sessions and the US open marked on
// the chart, plus a side rail (direction gauge, momentum squares, liquidation bar, money arrows, news with impact).
// A flash bar fires on big news, liquidation bursts and level touches. Observation only: no order, no size, no entry wording.
// Thresholds marked OURS were chosen here, not measured. Pure model() for tests; render() draws.
(function (root) {
  'use strict';
  var REG = (typeof module !== 'undefined' && module.exports) ? require('./level_registry.js') : root.LEVELREG;
  var BIG_PRINT = 250000, BURST_1M = 1000000, TOUCH = 0.0005, NEWS_HI = 7, NEWS_FRESH = 180000;   // OURS
  var FLASH_MS = { news: 90000, liq: 60000, touch: 45000 };
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
    if (it.src === 'analyst') return it.who ? it.who + ' call' : 'Analyst call';   // short analyst name on the level (operator 11-13)
    if (it.badge === '1WS20' || it.badge === '1WE21') return 'Bull market band (weekly)';   // 20-week SMA + 21-week EMA, SOURCED MA_CONCEPTS.md
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
    var now = ctx.now, add = function (k, kind, cls, text, lvl) {
      if (FL.seen[k]) return; FL.seen[k] = now; FL.list.push({ k: k, kind: kind, cls: cls, text: text, t: now });
      // flag log (card live-aid-flag-log-1111): one row per banner flashed, handed to the page, which keeps it in localStorage
      if (typeof ctx.onFlag === 'function') { try { ctx.onFlag({ t: now, kind: kind, side: cls === 'up' ? 'UP' : cls === 'down' ? 'DOWN' : 'NEUTRAL', level: lvl || '', evidence: text, price: md.px > 0 ? md.px : '' }); } catch (e) { /* logging must never break the banner */ } }
    };
    (ctx.news || []).forEach(function (x) {
      if (x.score >= NEWS_HI && now - x.t <= NEWS_FRESH) add('n' + x.id, 'news', x.tag === 'POSITIVE' ? 'up' : x.tag === 'NEGATIVE' ? 'down' : 'amber', 'NEWS ' + x.score.toFixed(0) + '/10: ' + x.head);
    });
    var l = ctx.liq || {};
    (l.last || []).forEach(function (e) {
      if (e.usd >= BIG_PRINT && now - e.t <= 60000) add('l' + e.t + e.usd, 'liq', e.side === 'long' ? 'down' : 'up', usd(e.usd) + ' of ' + (e.side === 'long' ? 'LONGS' : 'SHORTS') + ' forced out at ' + n0(e.px));
    });
    if (l.m1 && l.m1.long + l.m1.short >= BURST_1M) add('b' + Math.floor(now / 60000), 'liq', l.m1.long >= l.m1.short ? 'down' : 'up', 'LIQUIDATION BURST: ' + usd(l.m1.long + l.m1.short) + ' in 1 min, mostly ' + (l.m1.long >= l.m1.short ? 'longs' : 'shorts'));
    // IDEA / SETUP banners and the both-sides line are gone (card live-aid-board-render-1111): the two-sided board card shows both sides at once.
    if (md.px > 0) md.zones.forEach(function (z) {
      if (Math.abs(md.px / z.price - 1) <= TOUCH) add('t' + Math.round(z.price) + Math.floor(now / 900000), 'touch', 'amber', 'TOUCHING ' + z.name + ' ' + n0(z.price), z.name + ' ' + z.price);
    });
    FL.list = FL.list.filter(function (f) { return now - f.t <= FLASH_MS[f.kind]; });
    var shown = FL.list;
    var out = shown.slice(-3).reverse(), fb = root.document && root.document.getElementById('flash');
    if (fb) { fb.innerHTML = out.map(function (f) { return '<div class="fl ' + f.cls + '">' + (f.html || esc(f.text)) + '</div>'; }).join(''); fb.classList.toggle('on', out.length > 0); }
    return out;
  }

  // ---------- drawing ----------
  var MA5 = [['ema', 21, '21 EMA'], ['ema', 55, '55 EMA'], ['sma', 200, '200 SMA']];   // SOURCED: Krown KR-M01 (MA_CONCEPTS.md)
  function smaS(c, n) { var out = [], s = 0; for (var i = 0; i < c.length; i++) { s += c[i]; if (i >= n) s -= c[i - n]; out.push(i >= n - 1 ? s / n : null); } return out; }
  // EMA: alpha 2/(N+1) (SOURCED maths), seeded with the mean of the first N closes (OURS, same as ma_strip.js)
  function emaS(c, n) { var out = [], a = 2 / (n + 1), e = null, s = 0; for (var i = 0; i < c.length; i++) { if (i < n) { s += c[i]; e = i === n - 1 ? s / n : null; } else e = c[i] * a + e * (1 - a); out.push(e); } return out; }
  // Volume strip under the chart, on the same time axis as the candles: one bar per 5m bar (Binance spot), green = buyers took more,
  // red = sellers took more, white line = the 20-bar average. Nothing overlaps the candles any more.
  var VOL_AVG = 20, VOL_HI = 1.5, VOL_LO = 0.7;   // OURS: "busy" at 1.5x the 20-bar average, "thin" under 0.7x; not backtested
  function volPane(ctx, md, W, H) {
    var rows = (ctx.rows5 || []).slice(-144), k = ctx.k5 || [];
    if (rows.length < 5 || k.length < 4) return '<div class="hm-nid" style="flex:none">Volume NOT_IN_DATA</div>';
    var L = 8, R = W - 270, cw = (R - L) / (rows.length + 8), t0 = +rows[0][0], x = function (t) { return L + ((t - t0) / 300000 + 0.5) * cw; };
    var vol = k.map(function (r) { return +r[5]; }), avg = smaS(vol, VOL_AVG), vmax = 0, T = 14, B = H - 2;
    k.forEach(function (r) { if (+r[0] >= t0) vmax = Math.max(vmax, +r[5]); });
    var yv = function (v) { return B - (vmax ? v / vmax : 0) * (B - T); }, s = '<svg class="hm-vol" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" style="height:' + H + 'px">', pts = [];
    k.forEach(function (r, i) {
      if (+r[0] < t0) return;
      var d = 2 * +r[9] - +r[5], xx = x(+r[0]);
      s += '<rect x="' + (xx - cw * 0.36) + '" y="' + yv(+r[5]) + '" width="' + (cw * 0.72) + '" height="' + Math.max(0, B - yv(+r[5])) + '" class="hm-vb ' + (d >= 0 ? 'up' : 'down') + '"/>';
      if (avg[i] != null) pts.push(xx.toFixed(1) + ',' + yv(Math.min(avg[i], vmax)).toFixed(1));
    });
    if (pts.length > 1) s += '<polyline points="' + pts.join(' ') + '" class="hm-vavg"/>';
    return s + '<text x="' + (L + 4) + '" y="11" class="hm-vlt">Volume per 5m bar: green = buyers took more, red = sellers took more, white line = normal (20-bar average)</text></svg>';
  }
  // One line that says what the volume means now (operator 11-13: "if it is increasing or decreasing, what does it mean?").
  // From CLOSED 5m bars only. Words are OURS and describe, they do not forecast. VFI = LazyBear Volume Flow Indicator from indread.js.
  function volRead(ctx) {
    var k = (ctx.k5 || []).filter(function (r) { return +r[0] + 300000 <= ctx.now; }), n = k.length;
    if (n < VOL_AVG + 1) return { ratio: null, cls: 'dim', txt: 'Volume: not enough closed bars yet', html: '<div class="hm-sw hm-vr2 dim"><b>Volume</b> not enough closed bars yet</div>' };
    var v = function (i) { return +k[i][5]; }, sum = 0; for (var i = n - 1 - VOL_AVG; i < n - 1; i++) sum += v(i);
    var last = k[n - 1], ratio = v(n - 1) / (sum / VOL_AVG), buy = 2 * +last[9] - +last[5] >= 0, up = +last[4] >= +last[1];
    var a3 = (v(n - 1) + v(n - 2) + v(n - 3)) / 3, b3 = (v(n - 4) + v(n - 5) + v(n - 6)) / 3, tr = b3 > 0 && a3 / b3 >= 1.25 ? 'rising' : b3 > 0 && a3 / b3 <= 0.8 ? 'falling' : 'steady';
    var size = ratio >= VOL_HI ? 'busy' : ratio < VOL_LO ? 'thin' : 'normal', cls = size === 'busy' ? (buy ? 'up' : 'down') : 'dim';
    var mean = size === 'busy' ? (up === buy ? 'the ' + (up ? 'rise' : 'fall') + ' had real ' + (buy ? 'buying' : 'selling') + ' behind it' : 'heavy ' + (buy ? 'buying' : 'selling') + ' but the bar closed ' + (up ? 'up' : 'down') + ': the other side soaked it up')
      : size === 'thin' ? 'few traders took part in the last move' : 'nothing unusual';
    var T = ctx.ind, chips = ['15m', '1h', '4h'].map(function (tf) {
      var c = T && T.r && T.r[tf] && T.r[tf].cells && T.r[tf].cells.vfi; if (!c || c.v == null) return '';
      return '<span class="hm-wc ' + (c.v > 0 ? 'up' : c.v < 0 ? 'down' : 'dim') + '"><i>' + tf + '</i>' + (c.v > 0 ? 'in' : c.v < 0 ? 'out' : 'flat') + (c.rising > 0 ? ' ▲' : c.rising < 0 ? ' ▼' : '') + '</span>';
    }).join('');
    var txt = 'Volume: last closed 5m bar ' + ratio.toFixed(1) + 'x normal (' + size + '), ' + (buy ? 'buyers' : 'sellers') + ' took more, 3-bar trend ' + tr + ': ' + mean;
    var tip = 'Busy = 1.5x the 20-bar average or more, thin = under 0.7x (our thresholds, not backtested). Money flow = LazyBear Volume Flow Indicator on closed bars: in = above zero, out = below zero, arrow = rising or falling.';
    return { ratio: ratio, size: size, buy: buy, trend: tr, cls: cls, txt: txt,
      html: '<div class="hm-sw hm-vr2 ' + cls + '" title="' + esc(tip) + '"><b>Volume</b> ' + esc(txt.slice(8)) + (chips ? ' <span class="hm-wl">Money flow (VFI):</span> ' + chips : '') + '</div>' };
  }
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
    s += '<text x="' + (R + 4) + '" y="' + (T - 8) + '" class="hm-ax">Price (USD)</text><text x="' + R + '" y="' + (B + 18) + '" text-anchor="end" class="hm-ax">Time (UTC)</text>';
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
    // session highs/lows of today's sessions, from the closed 5m bars on screen (OURS: computed here, not a marked level)
    var dayStart = Math.floor(ctx.now / 86400000) * 86400000;
    SESS.forEach(function (ss) {
      var a0 = dayStart + ss[1] * 3600000, a1 = dayStart + ss[2] * 3600000, sb = rows.filter(function (r) { return +r[0] >= a0 && +r[0] < a1 && +r[0] + step <= ctx.now; });
      if (sb.length < 3) return;
      var sh = Math.max.apply(null, sb.map(function (r) { return +r[2]; })), sl = Math.min.apply(null, sb.map(function (r) { return +r[3]; })), done = ctx.now >= a1;
      [[sh, 'high'], [sl, 'low']].forEach(function (q) {
        if (q[0] < lo || q[0] > hi) return;
        s += '<line x1="' + Math.max(L, x(a0)) + '" x2="' + R + '" y1="' + y(q[0]) + '" y2="' + y(q[0]) + '" class="hm-lv hm-sl"/>';
        labs.push({ y: y(q[0]), c: 'dim', t: ss[0] + ' ' + q[1] + (done ? '' : ' so far') + ' (OURS)', p: q[0], n: 1 });
      });
    });
    // flag markers: where a banner fired (from the flag log rows the page keeps); hover shows what it said
    // operator 11-13 (3rd ask: "because of this red triangle the chart is not clearly visible"): markers left the candles. They sit on a
    // rail along the bottom edge of the price pane, one per 5m bar (the last flag of that bar; the count of the others is in the hover).
    var fbar = {};
    (ctx.flagRows || []).forEach(function (f) {
      var ft = +f.t; if (!(ft >= t0)) return;
      var k = Math.floor((ft - t0) / step); (fbar[k] = fbar[k] || []).push(f);
    });
    var flagSvg = '';
    Object.keys(fbar).forEach(function (k) {
      var fs = fbar[k], f = fs[fs.length - 1], ft = +f.t, fx = x(t0 + k * step);
      if (fx > R) return;
      var c = f.side === 'UP' ? 'up' : f.side === 'DOWN' ? 'down' : 'amber', dir = f.side === 'DOWN' ? -1 : 1;
      flagSvg += '<path d="M' + fx.toFixed(1) + ' ' + (B - 5.5 - 3.5 * dir) + ' l4 ' + (7 * dir) + ' h-8 z" class="hm-fm ' + c + '"><title>' +
        esc(f.kind + ' ' + new Date(ft).toISOString().slice(11, 16) + 'Z: ' + (f.evidence || '') + (fs.length > 1 ? ' (+' + (fs.length - 1) + ' more in this 5m bar)' : '')) + '</title></path>';
    });
    // candles
    rows.forEach(function (r) {
      var o = +r[1], h = +r[2], l = +r[3], c = +r[4], xx = x(+r[0]), col = c >= o ? 'up' : 'down';
      s += '<line x1="' + xx + '" x2="' + xx + '" y1="' + y(h) + '" y2="' + y(l) + '" class="hm-wk ' + col + '"/>' +
           '<rect x="' + (xx - cw * 0.36) + '" y="' + Math.min(y(o), y(c)) + '" width="' + (cw * 0.72) + '" height="' + Math.max(1, Math.abs(y(o) - y(c))) + '" class="hm-bd ' + col + '"/>';
    });
    // Volume left the price pane (operator 11-13: "I cannot see the wicks properly"): it has its own strip under the chart, volPane().
    // Moving averages on the 5m candles (operator 11-13: "the MA/EMAs Krown uses"). Lengths SOURCED: 21 EMA, 55 EMA, 200 simple
    // (research/ma_layer_2026-11/MA_CONCEPTS.md, KR-M01). Drawn only where the average exists and sits inside the price range.
    var all5 = ctx.rows5 || [], cl5 = all5.map(function (r) { return +r[4]; }), off = all5.length - rows.length, leg = '';
    MA5.forEach(function (m, mi) {
      var ser = m[0] === 'ema' ? emaS(cl5, m[1]) : smaS(cl5, m[1]), seg = [], d = '';
      rows.forEach(function (r, j) {
        var v = ser[off + j];
        if (v != null && v >= lo && v <= hi) seg.push(x(+r[0]).toFixed(1) + ',' + y(v).toFixed(1));
        else { if (seg.length > 1) d += '<polyline points="' + seg.join(' ') + '" class="hm-ma m' + mi + '"/>'; seg = []; }
      });
      if (seg.length > 1) d += '<polyline points="' + seg.join(' ') + '" class="hm-ma m' + mi + '"/>';
      var lastV = ser[ser.length - 1];
      s += d; leg += '<tspan class="hm-mal m' + mi + '" dx="10">━ ' + m[2] + (lastV != null ? ' ' + n0(lastV) : ' needs ' + m[1] + ' bars') + '</tspan>';
    });
    s += '<text x="' + (L + 4) + '" y="' + (T + 13) + '" class="hm-ax">Averages on 5m (Krown’s set)' + leg + '</text>';
    s += flagSvg;   // marker rail, drawn over the candles' bottom margin
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
  // One plain-words caption above the chart, from CLOSED 5m bars only (operator 11-13). Descriptive: where the last closed bar sits vs the
  // nearest named levels, which session, the last logged flag and its hit rate with n. Level names SOURCED (his chart, prior-day data,
  // analyst calls); session hours, nearest-level pick and this sentence OURS. No forecast, no advice.
  function caption(ctx, md) {
    var cl = (ctx.rows5 || []).filter(function (r) { return +r[0] + 300000 <= ctx.now; }), lastB = cl[cl.length - 1];
    if (!lastB) return '<div class="hm-cap dim">Closed 5m bars NOT_IN_DATA</div>';
    var c = +lastB[4], up = null, dn = null;
    (md.zones || []).forEach(function (z) { if (z.price > c && (!up || z.price < up.price)) up = z; if (z.price < c && (!dn || z.price > dn.price)) dn = z; });
    var pc = function (z) { return Math.abs((z.price / c - 1) * 100).toFixed(2) + '%'; };
    var hr = new Date(+lastB[0] + 300000).getUTCHours() + new Date(+lastB[0] + 300000).getUTCMinutes() / 60;
    var ses = SESS.filter(function (ss) { return hr >= ss[1] && hr < ss[2]; }).map(function (ss) { return ss[0]; }).join(' + ') || 'between sessions';
    var fr = (ctx.flagRows || []).filter(function (f) { return isFinite(+f.t); }), lf = fr[fr.length - 1], st = lf && ctx.flagStats && ctx.flagStats[lf.kind];
    var flag = !lf ? 'no flag logged yet' : 'last flag ' + lf.kind + (lf.level ? ' ' + lf.level : '') + ' at ' + new Date(+lf.t).toISOString().slice(11, 16) + 'Z, ' +
      (st && st.n > 0 ? 'hit rate ' + Math.round(st.hit) + '% of n ' + st.n + (st.n < 30 ? ' (too few to trust)' : '') : 'hit rate not scored yet (n 0)');
    var txt = 'Last closed 5m bar ' + new Date(+lastB[0] + 300000).toISOString().slice(11, 16) + 'Z at ' + n0(c) + ': ' +
      (up ? pc(up) + ' under ' + esc(up.name) + ' ' + n0(up.price) : 'no named level above') + ', ' + (dn ? pc(dn) + ' over ' + esc(dn.name) + ' ' + n0(dn.price) : 'no named level below') +
      ' · session ' + ses + ' · ' + esc(flag);
    return '<div class="hm-cap">' + txt + ' <small class="dim">levels SOURCED, session hours and this line OURS</small></div>' + chartKey();
  }
  // Key to everything drawn on the chart (operator 11-13: "what are these triangles ... where is the explanation"). Wording OURS.
  function chartKey() {
    return '<div class="hm-cap hm-key"><b>Key</b> small triangles on the bottom edge = the LONG / SHORT board or a level alert changed in that 5m bar: ' +
      '<span class="up">▲ green</span> long-side readings switched on · <span class="down">▼ red</span> short-side · <span class="amber">▲ amber</span> both or neither. ' +
      'A log mark, not a signal; hover one to read it. Curves = 21 EMA, 55 EMA, 200 SMA. Dashed lines = named levels. Shaded blocks = Asia, Europe, US hours.</div>';
  }
  // A level is only named in the header when the chart reaches it (within 2 % of price; chart() fits those): no off-frame level (operator 11-12).
  function inFrame(md, z) { return md.px > 0 && Math.abs(z.price / md.px - 1) <= 0.02; }
  function gauge(md) {
    var ang = Math.PI * (1 - (md.score + 1) / 2), cx = 110, cy = 96, r = 80, nx = cx + r * 0.85 * Math.cos(ang), ny = cy - r * 0.85 * Math.sin(ang);
    var arc = function (a0, a1, c) { var x0 = cx + r * Math.cos(a0), y0 = cy - r * Math.sin(a0), x1 = cx + r * Math.cos(a1), y1 = cy - r * Math.sin(a1); return '<path d="M' + x0 + ' ' + y0 + ' A' + r + ' ' + r + ' 0 0 1 ' + x1 + ' ' + y1 + '" class="hm-arc ' + c + '"/>'; };
    var dirc = md.dir === 'LONG' ? 'up' : md.dir === 'SHORT' ? 'down' : 'dim';
    var s = '<svg viewBox="0 0 220 112" class="hm-g">' + arc(Math.PI, Math.PI * 0.62, 'down') + arc(Math.PI * 0.62, Math.PI * 0.38, 'dim') + arc(Math.PI * 0.38, 0, 'up') +
      '<line x1="' + cx + '" y1="' + cy + '" x2="' + nx + '" y2="' + ny + '" class="hm-needle"/><circle cx="' + cx + '" cy="' + cy + '" r="6" class="hm-hub"/>' +
      '<text x="14" y="110" class="hm-gl down">SHORT</text><text x="206" y="110" text-anchor="end" class="hm-gl up">LONG</text></svg>';
    return '<div class="hm-card"><div class="hm-h">Direction <b class="' + dirc + '">' + md.dir + '</b><span class="hm-sub">' + md.bear + ' say down, ' + md.bull + ' say up, of ' + md.n + '</span></div>' + s + soWhat(md.dir === 'LONG' ? 1 : md.dir === 'SHORT' ? -1 : 0, md) + '</div>';
  }
  // "So what for a trade" (operator 11-12: "I need more guidance on how to trade whatever I am seeing"). One plain line per panel:
  // long / short / wait plus the level that decides. OURS, not backtested; context only, never an order.
  function soWhat(side, md) {
    var a = md && md.lad && md.lad.above[0], b = md && md.lad && md.lad.below[0], lv = function (z) { return n0(z.price) + ' (' + esc(z.name) + ')'; };
    if (side > 0) return '<div class="hm-sw up"><b>So what:</b> long side only' + (b ? ' while price holds above ' + lv(b) + '; a 15m close under it = wait' : '') + '</div>';
    if (side < 0) return '<div class="hm-sw down"><b>So what:</b> short side only' + (a ? ' while price stays under ' + lv(a) + '; a 15m close above it = wait' : '') + '</div>';
    return '<div class="hm-sw dim"><b>So what:</b> wait, nobody leads' + (a && b ? '. Act only at ' + lv(b) + ' or ' + lv(a) : '') + '</div>';
  }
  // Indicator read: ONE verdict row per timeframe in plain words (indread.js verdict()), then the so-what line.
  function indCard(ctx, md) {
    var T = ctx.ind, sub = '<span class="hm-sub" title="Six closed-bar readings per timeframe (Volume Flow, Squeeze, ADX/DI, WaveTrend, RSI, buy-vs-sell volume) counted; a lead of 2 or more wins. Our rule, not backtested.">closed bars only</span>';
    if (!T) return '<div class="hm-card"><div class="hm-h">Who is winning</div><div class="hm-nid">Binance candles NOT_IN_DATA (indread.js or feed missing)</div></div>';
    var V = T.ver || {}, coil = false;
    var rows = (T.tfs || []).map(function (x) {
      var v = V[x[0]];
      if (!v) return '<div class="hm-vr dim"><b>' + x[0] + '</b><span>no candles</span></div>';
      if (v.coiled) coil = true;
      return '<div class="hm-vr ' + (v.side > 0 ? 'up' : v.side < 0 ? 'down' : 'dim') + '"><b>' + x[0] + '</b><span>' + esc(v.word) + '</span><small>' + (v.side < 0 ? v.dn + ' of ' + v.n + ' say down' : v.side > 0 ? v.up + ' of ' + v.n + ' say up' : v.up + ' up, ' + v.dn + ' down of ' + v.n) + (v.coiled ? ' <em>COILED</em>' : '') + '</small></div>';
    }).join('');
    var s15 = V['15m'] ? V['15m'].side : 0, s1 = V['1h'] ? V['1h'].side : 0, side = s15 && s1 && s15 !== s1 ? 0 : (s1 || s15);
    var legend = '<div class="hm-lg">6 readings vote per timeframe: money flow, squeeze, trend strength, WaveTrend, RSI, buy vs sell volume. A lead of 2 wins.' + (coil ? ' COILED = quiet before a move; direction unknown.' : '') + '</div>';
    var stale = T.stale ? '<div class="hm-is amber">STALE: last 15m candle closed ' + Math.round(T.age / 60000) + ' min ago (feed stalled?) - these readings are old</div>' : '';
    return '<div class="hm-card"><div class="hm-h">Who is winning' + sub + '</div>' + stale + rows + legend + soWhat(side, md) + '</div>';
  }
  // Liquidations: one column per window; red part = longs forced out, green part = shorts; height = share, total under it.
  var LIQ_WIN = [['1m', 60000], ['2m', 120000], ['3m', 180000], ['5m', 300000], ['7m', 420000], ['10m', 600000], ['15m', 900000], ['30m', 1800000], ['1h', 3600000], ['2h', 7200000], ['4h', 14400000]];
  // Does a 1m / 2m burst continue or reverse? Only a measured share with its n is ever shown (liq_rates.js, LIQ_RATES.read); with no
  // history recorded yet the card says so instead of guessing (operator 11-13: "how much is signaling is not known to me").
  var LR = (typeof module !== 'undefined' && module.exports) ? (function () { try { return require('./liq_rates.js'); } catch (e) { return null; } })() : root.LIQ_RATES;
  function liqMeaning(l) {
    var out = [];
    ['1m', '2m'].forEach(function (w) {
      var s = l.win[w]; if (!s || !(s.long + s.short)) return;
      var side = s.long >= s.short ? 'long' : 'short', amt = Math.max(s.long, s.short), r = null;
      try { r = LR && LR.read ? LR.read(w, side, amt) : null; } catch (e) { r = null; }
      if (r && r.n) out.push(w + ': ' + usd(amt) + ' of ' + side + 's forced out. In the past, ' + Math.round(r.cont15 * 100) + '% of bursts this size kept going 15 min later (n ' + r.n + ')');
    });
    if (out.length) return '<div class="hm-sw"><b>Measured:</b> ' + esc(out.join('; ')) + '</div>';
    return '<div class="hm-lg">Continue or reverse after a 1-2 min burst: NOT MEASURED yet (no liquidation history is recorded). Treat a burst as "something happened here", not as a direction.</div>';
  }
  function liqCard(ctx, md) {
    var l = ctx.liq; if (!l || !l.win) return '<div class="hm-card"><div class="hm-h">Liquidations</div><div class="hm-nid">no feed</div></div>';
    var cols = LIQ_WIN.map(function (w) {
      var s = l.win[w[0]] || { long: 0, short: 0 }, tot = s.long + s.short, pl = tot ? s.long / tot * 100 : 0, part = l.since && ctx.now - l.since < w[1];
      return '<div class="hm-lc' + (part ? ' part' : '') + '" title="' + w[0] + ': longs ' + usd(s.long) + ', shorts ' + usd(s.short) + (part ? ' (only since this page opened)' : '') + '">' +
        '<div class="hm-lcb' + (tot ? '' : ' empty') + '"><span class="up" style="height:' + (tot ? 100 - pl : 0) + '%"></span><span class="down" style="height:' + pl + '%"></span></div>' +
        '<b>' + w[0] + '</b><small>' + (tot ? usd(tot) : '0') + '</small></div>';
    }).join('');
    var w15 = l.win['15m'] || { long: 0, short: 0 }, a = md && md.lad && md.lad.above[0], b = md && md.lad && md.lad.below[0], lvl = function (z) { return z ? ' at ' + n0(z.price) + ' (' + esc(z.name) + ')' : ''; };
    var sw = !(w15.long + w15.short) ? 'quiet in the last 15 min' : w15.long >= 2 * w15.short ? usd(w15.long) + ' of longs were forced to sell in 15 min (that selling pushed price down)' + (b ? '; next floor' + lvl(b) : '') : w15.short >= 2 * w15.long ? usd(w15.short) + ' of shorts were forced to buy in 15 min (that buying pushed price up)' + (a ? '; next ceiling' + lvl(a) : '') : 'both sides were hit in 15 min, no lean';
    return '<div class="hm-card"><div class="hm-h">Forced selling and buying <span class="hm-sub">red = longs forced to sell, green = shorts forced to buy</span></div><div class="hm-lcs">' + cols + '</div><div class="hm-sw"><b>What it shows:</b> ' + sw + '</div>' + liqMeaning(l) + '</div>';
  }
  // Venues that answered this cycle with their share of the open positions in BTC (shown as a footnote, it is a share, not a change): "Bybit 38% + Hyperliquid 27% + ..." (operator 11-10)
  function venueWords(m) {
    var v = (m.venues || []).slice().sort(function (a, b) { return b.btc - a.btc; });
    if (!v.length) return m.n + ' venue' + (m.n === 1 ? '' : 's');
    return v.map(function (x) { return x.name + (isFinite(x.share) && v.length > 1 ? ' ' + Math.round(x.share * 100) + '%' : ''); }).join(' + ');
  }
  // Open positions vs price in one sentence (operator 11-13: the venue shares read like a change and two arrows hid the active one).
  // Flat = under 0.1 % either way, the OI_COMMENTARY_SPEC threshold. The reading words per price/positions pair: OURS, not backtested.
  var MONEY_READ = { 'up/up': 'new longs buying', 'down/up': 'new shorts selling', 'up/down': 'shorts covering, no new money', 'down/down': 'longs closing or forced out',
    'flat/up': 'positions building, no move yet', 'flat/down': 'positions closing quietly', 'up/flat': 'the rise is not fed by new money', 'down/flat': 'the fall is not fed by new money', 'flat/flat': 'quiet' };
  function moneyDir(x) { return x >= 0.001 ? 'up' : x <= -0.001 ? 'down' : 'flat'; }
  function pct(x) { return (x >= 0 ? '+' : '') + (x * 100).toFixed(1) + '%'; }
  function moneyCard(ctx) {
    var m = ctx.money;
    if (!m) return '<div class="hm-card"><div class="hm-h">Positions</div><div class="hm-nid">waiting for open-interest samples</div></div>';
    var d = moneyDir(m.doi), pd = moneyDir(m.dp), c = d === 'up' ? 'up' : d === 'down' ? 'down' : 'dim';
    var arrow = '<span class="hm-ar ' + c + '">' + (d === 'up' ? '▲' : d === 'down' ? '▼' : '◆') + '</span>';
    var say = 'Open positions (' + m.n + ' venue' + (m.n === 1 ? '' : 's') + '): ' + pct(m.doi) + ' in ' + m.label + (d === 'flat' ? ' (flat)' : '') + ' while price ' + pct(m.dp) + (pd === 'flat' ? ' (flat)' : '') + ' -> ' + MONEY_READ[pd + '/' + d];
    return '<div class="hm-card"><div class="hm-h">Positions <span class="hm-sub" title="' + esc((m.missing && m.missing.length ? 'Not read: ' + m.missing.join('; ') : 'All venues read') + '. Reading words: our rule, not backtested.') + '">open positions vs price</span></div>' +
      '<div class="hm-mon">' + arrow + '<span class="hm-say">' + esc(say) + '</span></div><div class="hm-from">from: ' + esc(venueWords(m)) + ' (each venue’s share of the total)</div></div>';
  }
  var NF = (typeof module !== 'undefined' && module.exports) ? (function () { try { return require('./news_flash.js'); } catch (e) { return null; } })() : root.NEWSFLASH;
  function newsCard(ctx) {
    if (NF && NF.html) {
      var ev0 = ctx.ev ? '<span class="hm-ev">' + esc(ctx.ev.name) + ' in ' + esc(ctx.ev.inTxt) + '</span>' : '';
      return '<div class="hm-card hm-news"><div class="hm-h">News that matters <span class="hm-sub">last hour; the rest is on the News page</span>' + ev0 + '</div>' + NF.html(ctx.news || [], ctx.now) + '</div>';
    }
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
  // ONE line for the WaveTrend lanes (operator 11-13: six strips took the space and he could not use them). Timing = 1m 2m 3m, frame =
  // 15m + 30m agree, 4h = the last CLOSED 4h bar (his TradingView shows the forming bar), backdrop only. OURS, not backtested.
  // operator 11-13 (2nd ask): ONE compact row = timeframe chips (state, zone) + last cross and its age; the full sentence moves into the
  // tooltip and, when opened, above the strips (no information lost). Open/closed is remembered per viewer in localStorage (try/catch).
  var WT_KEY = 'mts_wt_open';
  function wtStore() { try { return (typeof globalThis !== 'undefined' && globalThis.localStorage) || root.localStorage || null; } catch (e) { return null; } }
  // Open by default (operator 11-13: "WaveTrend has gone completely"); only his own click on [hide strips] closes it, and that is remembered.
  function wtLoad() { try { var st = wtStore(); return !st || st.getItem(WT_KEY) !== '0'; } catch (e) { return true; } }
  function wtSave(v) { try { var st = wtStore(); if (st) st.setItem(WT_KEY, v ? '1' : '0'); } catch (e) { /* storage blocked: choice lives for this page only */ } }
  var wtOpen = wtLoad();   // strips behind a click, collapsed by default; kept across the 1 s re-render
  // operator 11-13 "Yes, fold them": seven low-evidence readings behind ONE click on the Home rail, collapsed by default, remembered per viewer.
  // Fold only, nothing deleted: Direction gauge and Money (OI) card drawn inside; Verdict, Same data other readings, Big candle story,
  // Level approach prep and Forced selling on other exchanges are their own pages, linked from here. Money and Forced selling stay folded until their feeds run.
  var FOLD_KEY = 'mts_fold_open', FOLD_PAGES = [['verdict', 'Verdict and watch list'], ['antic', 'Same data, other readings'], ['bc', 'Big candle story'], ['lap', 'Level approach prep'], ['xliq', 'Forced selling on other exchanges']];
  function foldLoad() { try { var st = wtStore(); return !!st && st.getItem(FOLD_KEY) === '1'; } catch (e) { return false; } }
  function foldSave(v) { try { var st = wtStore(); if (st) st.setItem(FOLD_KEY, v ? '1' : '0'); } catch (e) { /* storage blocked */ } }
  var foldOpen = foldLoad();
  function foldCard(ctx, md) {
    var head = '<div class="hm-card hm-fold"><div class="hm-h" data-foldtoggle="1" role="button" tabindex="0" style="cursor:pointer" title="Click to ' + (foldOpen ? 'hide' : 'show') + ' seven readings with no proven edge (Direction gauge, Verdict, Same data other readings, Big candle story, Level approach prep, Money, Forced selling)">Folded readings <span class="hm-sub">7 · ' + (foldOpen ? 'hide' : 'show') + '</span></div>';
    if (!foldOpen) return head + '</div>';
    return head + gauge(md) + moneyCard(ctx) + '<div class="hm-sub">' + FOLD_PAGES.map(function (q) { return '<a href="#' + q[0] + '">' + esc(q[1]) + '</a>'; }).join(' · ') + '</div></div>';
  }
  var WT_MS = { '1m': 60000, '2m': 120000, '3m': 180000, '15m': 900000, '30m': 1800000, '4h': 14400000 };
  function wtAge(ms) { var m = Math.round(ms / 60000); return m < 120 ? m + ' min' : Math.round(m / 60) + ' h'; }
  function wtChips(L) {
    var chips = LANES.map(function (ln) {
      var z = L[ln[0]], sd = z && z.side != null ? z.side : null, c = sd === 1 ? 'up' : sd === -1 ? 'down' : 'dim', z2 = z && z.zone === 'hot' ? ' OB' : z && z.zone === 'cold' ? ' OS' : '';
      return '<span class="hm-wc ' + c + '" title="' + ln[0] + ' ' + ln[1] + ': ' + (sd === 1 ? 'rising' : sd === -1 ? 'falling' : 'no data') + (z2 ? (z2 === ' OB' ? ', overbought' : ', oversold') : '') + '"><i>' + ln[0] + '</i>' + (sd === 1 ? '▲' : sd === -1 ? '▼' : '·') + z2 + '</span>';
    }).join('');
    var last = null;
    ['1m', '2m', '3m', '15m', '30m'].forEach(function (tf) { var z = L[tf], lx = z && z.last; if (!lx) return; var age = lx.ago * (z.ms || WT_MS[tf]); if (!last || age < last.age) last = { tf: tf, side: lx.side, age: age, strong: lx.strong }; });
    var lt = last ? '<span class="hm-wl">last cross ' + last.tf + ' ' + (last.side > 0 ? '▲ up' : '▼ down') + (last.strong ? ' (big dot)' : '') + ', ' + wtAge(last.age) + ' ago</span>' : '<span class="hm-wl dim">last cross: none in view</span>';
    return chips + lt;
  }
  function wtSentence(ctx, md) {
    var L = ctx.lanes || {}, a = L['15m'], b = L['30m'], sd = function (z) { return z && z.side != null ? z.side : null; };
    var fr = sd(a) !== null && sd(a) === sd(b) ? sd(a) : 0;
    var dot = ['1m', '2m', '3m'].some(function (tf) { var z = L[tf]; return z && z.bars && fr && z.bars.slice(-4).some(function (x) { return x.x === fr && x.strong; }); });
    var ts = ['1m', '2m', '3m'].map(function (tf) { return sd(L[tf]); }).filter(function (v) { return v !== null; });
    var tim = !ts.length ? 'no data' : ts.every(function (v) { return v === 1; }) ? 'all crossed up (long side only)' : ts.every(function (v) { return v === -1; }) ? 'all crossed down (short side only)' : 'mixed (no timing)';
    var zone = function (z, up) { return z && z.zone === 'cold' ? (up ? ' from oversold' : ', oversold') : z && z.zone === 'hot' ? (up ? ', overbought' : ' from overbought') : ''; };
    var frame = !a && !b ? 'no data' : fr > 0 ? 'rising' + zone(a, true) : fr < 0 ? 'falling' + zone(a, false) : '15m and 30m disagree';
    var h = L['4h'], h4 = h && isFinite(h.wt1) ? Math.round(h.wt1) + (h.zone === 'cold' ? ' oversold' : h.zone === 'hot' ? ' overbought' : '') : 'no data';
    var lad = md && md.lad, up = lad && lad.above && lad.above[0], dn = lad && lad.below && lad.below[0];
    var act = !a && !b ? 'wait' : fr > 0 ? (dot ? 'a big green dot just fired on 1m-3m, that is the timing; long side only' : 'wait for a big green dot on 1m-3m') + (up ? ', or a 15m close above ' + n0(up.price) : '') :
      fr < 0 ? (dot ? 'a big red dot just fired on 1m-3m, that is the timing; short side only' : 'wait for a big red dot on 1m-3m') + (dn ? ', or a 15m close below ' + n0(dn.price) : '') : 'wait';
    var txt = 'Timing 1-3m: ' + tim + ' · Frame 15m/30m: ' + frame + ' · 4h (last closed bar): ' + h4 + ' (backdrop, not a trigger) -> ' + act;
    return { cls: fr > 0 ? 'up' : fr < 0 ? 'down' : 'dim', txt: txt };
  }
  function wtSoWhat(ctx, md) {
    var r = wtSentence(ctx, md), L = ctx.lanes || {};
    return '<div class="hm-sw hm-wsw ' + r.cls + '" data-wttoggle="1" role="button" tabindex="0" title="' + esc(r.txt) + ' (click to ' + (wtOpen ? 'hide' : 'show') + ' the six strips)"><b>WaveTrend</b> ' + wtChips(L) + ' <small>[' + (wtOpen ? 'hide' : 'show') + ' strips]</small></div>' +
      (wtOpen ? '<div class="hm-sw hm-wfull ' + r.cls + '">' + esc(r.txt) + '</div><div class="hm-sw hm-whow">' + esc(WT_HOW) + '<br>' + esc(divLine(ctx)) + '</div>' : '');
  }
  // How to read the strips next to a 5m chart (operator 11-13: "the chart is 5 minutes, which timeframe do I use?"). OURS, not backtested.
  var WT_HOW = 'How to use (OURS, not backtested): the candles are 5m, the strips are faster and slower on purpose. 15m + 30m pointing the same way = which side. ' +
    'A big dot on 1m-3m in that direction = when. 4h = backdrop only. A bounce against the frame needs a divergence (below) at a named level; without one it is only a pause.';
  // Divergence of price against WaveTrend and RSI on closed bars (pulse.js read(): last 15 bars vs the 15 before, OURS). Bullish = price
  // made a lower low while the indicator made a higher low; bearish = the mirror on highs. 5m is the chart, 15m and 1h the frame.
  var DIV_TFS = ['5m', '15m', '1h'];
  function divRows(ctx) {
    var out = {};
    ((ctx.pulse && ctx.pulse.rows) || []).forEach(function (x) { if (x && DIV_TFS.indexOf(x.tf) >= 0 && x.r && x.r.div) out[x.tf] = x.r.div; });
    return out;
  }
  function divLine(ctx) {
    var d = divRows(ctx);
    return 'Divergence now (price vs WaveTrend / RSI, last 15 closed bars vs the 15 before, OURS): ' + DIV_TFS.map(function (tf) {
      var v = d[tf], w = [];
      if (!v) return tf + ' no data';
      [['wt', 'WaveTrend'], ['rsi', 'RSI']].forEach(function (q) { if (v[q[0]] > 0) w.push('bullish ' + q[1]); else if (v[q[0]] < 0) w.push('bearish ' + q[1]); });
      return tf + ' ' + (w.length ? w.join(' + ') : 'none');
    }).join(' · ') + '. Bullish = price lower low, indicator higher low (selling is tiring). It also lights the LONG / SHORT board.';
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
    var v = lv.map(function (z) { try { var st = LS.story(z, ctx.k15, ctx.now, ex); if (st) st.zone = z; return st; } catch (e) { return null; } });
    ctx._st = { md: md, v: v }; return v;
  }
  var ST_CLS = { 'REJECTED': 'turn', 'FAILED BREAK': 'turn', 'ACCEPTED': 'thru', 'BREAKING': 'thru', 'TESTING': 'amber', 'APPROACHING': 'amber', 'AWAY': 'dim' };
  var ST_SAY = { 'AWAY': 'far from it, nothing to read yet', 'APPROACHING': 'close, not touched yet', 'TESTING': 'touching it now', 'REJECTED': 'touched it and turned back',
    'FAILED BREAK': 'closed beyond it, then came back', 'BREAKING': 'one 15m close beyond it', 'ACCEPTED': 'two 15m closes beyond it: it gave way' };
  var AN = (typeof module !== 'undefined' && module.exports) ? (function () { try { return require('./analyst_note.js'); } catch (e) { return null; } })() : root.ANOTE;
  // What the analyst said at this level and what price did to it since (operator 11-13: "after it has been broken or reclaimed, how do I know what the analyst meant?")
  function analystLines(ctx, z) {
    if (!AN || !z || !z.items) return '';
    return z.items.filter(function (it) { return it.src === 'analyst' && it.who; }).slice(0, 2).map(function (it) {
      var r = null; try { r = AN.status({ price: it.price, published: it.published, bias: it.bias, who: it.who, said: it.said }, ctx.k1h || ctx.k15, ctx.now); } catch (e) { r = null; }
      return r && r.text ? '<div class="hm-an ' + (r.state === 'BROKEN' ? 'down' : r.state === 'RECLAIMED' || r.state === 'HELD' ? 'up' : 'dim') + '">' + esc(r.text) + '</div>' : '';
    }).join('');
  }
  function storyCard(ctx, md) {
    var v = stories(ctx, md);
    if (!v) return '<div class="hm-card"><div class="hm-h">At the level</div><div class="hm-nid">15m candles NOT_IN_DATA</div></div>';
    var rows = v.filter(Boolean).map(function (st) {
      var sc = ST_CLS[st.state] || 'dim', idea = st.idea ? '<b class="hm-idea ' + (st.idea === 'SHORT' ? 'down' : 'up') + '">' + st.idea + ' IDEA</b>' : '';
      var chips = st.ev.map(function (e) { return '<span class="hm-ec ' + e.cls + '" title="' + esc(e.t) + '">' + esc(e.k) + '</span>'; }).join('');
      return '<div class="hm-st"><div class="hm-st1"><span class="hm-stp ' + (st.res ? 'down' : 'up') + '">' + n0(st.price) + '</span> <span class="hm-stn">' + esc(st.name) + '</span>' +
        '<span class="hm-sts ' + sc + '">' + st.state + '</span>' + idea + '</div>' + '<div class="hm-stm">' + esc(st.state) + ' = ' + esc(ST_SAY[st.state] || '') + '</div>' + analystLines(ctx, st.zone) +
        '<div class="hm-ecs">' + (chips || '<em>no evidence yet</em>') + '<span class="hm-sc2" title="Each chip is one piece of evidence on 15m closes: green = for a turn back at the level, red = for a break through it.">evidence: ' + st.turn + ' for a turn back, ' + st.thru + ' for a break</span></div>' +
        '<div class="hm-stv">' + esc(st.valid) + (st.crowd ? '<br><span class="amber">' + esc(st.crowd) + '</span>' : '') + '</div></div>';
    }).join('');
    var id2 = v.filter(function (st) { return st && st.idea; }), mx = id2.length > 1 && id2.some(function (st) { return st.idea !== id2[0].idea; });
    return '<div class="hm-card"><div class="hm-h">At the level ' + (mx ? '<b class="amber" style="font-size:13px">MIXED: levels disagree, no idea</b>' : '') + '<span class="hm-sub" title="Read on 15m closes. Green chip = evidence for a turn, red = for going through. Measured over 180 days: ideas right 49 % (n 2,852), a coin flip, not an edge (research/level_story_1110).">15m closes · measured 49 % right: a coin flip</span></div>' + (rows || '<div class="hm-nid">no level near</div>') + '</div>';
  }
  // ---------- two-sided setup board (card live-aid-board-render-1111) ----------
  // LONG card and SHORT card side by side from setup_board.js (a plain count of live evidence per side; no weight, no probability),
  // a strength bar per side, and the n and hit rate of the CURRENT evidence mix from BASE_RATES.setup_board_mix (history, in-sample, no fees).
  // No rates file = "NO RATE". The percent is only ever copied from that table, never made up here. Observation only.
  var SB = (typeof module !== 'undefined' && module.exports) ? require('./setup_board.js') : root.LASB;
  var READINGS = ['home', 'grid', 'adx15', 'adx1h', 'vfi15', 'wt30'];   // same six, same order as base_rates.py READINGS
  var LAYER_WORDS = { rsi_div: 'RSI divergence', wt_div: 'WaveTrend divergence', cvd_div: 'Buyer/seller flow divergence', bb_cvd: 'Outside the band, flow exhausted',
    sweep: 'Swept stops and closed back', absorb: 'Absorption', vfi: 'Volume flow', sqz_release: 'Squeeze released', adx_di: 'Trend (ADX/DI)', value_area: 'Value area' };
  function sg(x) { return typeof x === 'number' && isFinite(x) ? (x > 0 ? 1 : x < 0 ? -1 : 0) : 0; }
  // Layer inputs per timeframe from what Home already computes (indicator table). Divergence, sweep, absorption and band readings are not
  // wired here yet: they simply do not appear (nothing invented). ctx.boardInputs overrides (tests, later wiring).
  function boardInputs(ctx) {
    if (ctx.boardInputs) return ctx.boardInputs;
    var T = ctx.ind, out = {}, dv = divRows(ctx);
    // divergences wired 11-13 (operator: "the hint is the divergence"): 5m / 15m / 1h, price vs RSI, WaveTrend and buyer/seller flow
    Object.keys(dv).forEach(function (tf) { out[tf] = { div: dv[tf] }; });
    if (!T || !T.r) return out;
    (T.tfs || []).forEach(function (x) {
      var R = T.r[x[0]]; if (!R || !R.cells) return;
      var c = R.cells, o = out[x[0]] || {};
      if (c.vfi && c.vfi.v != null) o.vfi = { v: c.vfi.v };
      if (c.sqz && c.sqz.v != null) o.sqz = { rel: c.sqz.rel, v: c.sqz.v };
      if (c.adx && c.adx.v != null) o.adx = { v: c.adx.v };
      out[x[0]] = o;
    });
    return out;
  }
  // The six readings of the review as +1 / -1 / 0; null when any cannot be read now (then no rate). ctx.mix overrides.
  function mixReadings(ctx, md) {
    if (ctx.mix) return ctx.mix;
    var T = ctx.ind, r = T && T.r, g = ctx.pulse, hi = g && isFinite(g.hi) ? g.hi : NaN, w = ctx.lanes && ctx.lanes['30m'];
    var cell = function (tf, k) { var R = r && r[tf]; return R && R.cells && R.cells[k] && R.cells[k].v != null ? R.cells[k].v : null; };
    var m = { home: md.dir === 'LONG' ? 1 : md.dir === 'SHORT' ? -1 : 0, grid: !isFinite(hi) ? null : hi >= 0.25 ? 1 : hi <= -0.25 ? -1 : 0,
      adx15: cell('15m', 'adx'), adx1h: cell('1h', 'adx'), vfi15: cell('15m', 'vfi'), wt30: w && w.side != null ? w.side : null };
    return READINGS.some(function (k) { return m[k] === null; }) ? null : m;
  }
  function rateRow(side, mix) {
    var tb = typeof BASE_RATES !== 'undefined' && BASE_RATES && BASE_RATES.setup_board_mix && BASE_RATES.setup_board_mix.table;
    if (!tb || !tb.rows || !mix) return null;
    var s = side === 'LONG' ? 1 : -1, key = READINGS.filter(function (k) { return s * sg(mix[k]) > 0; }).join('+') || 'none';
    for (var i = 0; i < tb.rows.length; i++) if (tb.rows[i].side === side && tb.rows[i].mix === key) return tb.rows[i];
    return null;
  }
  function boardCard(ctx, md) {
    var B = null;
    try { B = SB ? SB.board(boardInputs(ctx)) : null; } catch (e) { B = null; }
    if (!B) return '<div class="hm-card"><div class="hm-h">Setup board</div><div class="hm-nid">setup_board.js NOT_IN_DATA</div></div>';
    var mix = mixReadings(ctx, md), mx = Math.max(B.strength.long, B.strength.short, 4);
    var card = function (side, cls) {
      var key = side.toLowerCase(), items = B[key], n = B.strength[key], r = rateRow(side, mix);
      var list = items.map(function (it) { return '<li><b>' + esc(it.tf) + '</b> ' + esc(LAYER_WORDS[it.layer] || it.layer) + '</li>'; }).join('');
      var rate = r ? 'n ' + n0(r.n) + ' · right ' + Math.round(r.rate * 100) + ' % 1h later' + (r.low_n ? ' <b class="amber">LOW N</b>' : '') + ' <small>' + esc(r.window) + ', in-sample, no fees</small>'
        : '<span class="dim">NO RATE</span>';
      return '<div class="hm-bcard hm-b' + key[0] + ' ' + cls + '"><div class="hm-h"><b class="' + cls + '">' + side + '</b><span class="hm-sub">' + n + ' live</span></div>' +
        '<div class="hm-bbar ' + cls + '" data-n="' + n + '"><span style="width:' + Math.round(n / mx * 100) + '%"></span></div>' +
        (list ? '<ul class="hm-bl2">' + list + '</ul>' : '<div class="hm-nid">nothing live</div>') + '<div class="hm-brate">' + rate + '</div></div>';
    };
    return '<div class="hm-board">' + card('LONG', 'up') + card('SHORT', 'down') + '</div>';
  }
  // Flag log of the LONG / SHORT board (card live-aid-log-idea-setup-rows-1113): the board replaced the IDEA / SETUP banners, so its state
  // changes are what the page really shows now. One row (kind 'board') each time the set of live layers per side changes, incl. back to
  // nothing; evidence carries the layers and the n / rate shown, so the learner can score it against the 1h move.
  var FLB = { sig: null };
  function boardLog(ctx, md) {
    if (typeof ctx.onFlag !== 'function') return;
    var B = null; try { B = SB ? SB.board(boardInputs(ctx)) : null; } catch (e) { B = null; }
    if (!B) return;
    var mix = mixReadings(ctx, md), one = function (side) {
      var key = side.toLowerCase(), it = B[key] || [], r = rateRow(side, mix);
      return side + ' ' + it.length + ' live' + (it.length ? ': ' + it.map(function (x) { return x.tf + ' ' + (LAYER_WORDS[x.layer] || x.layer); }).join(', ') : '') + (r ? ' (n ' + Math.round(r.n) + ', right ' + Math.round(r.rate * 100) + '% 1h later)' : ' (NO RATE)');
    }, nl = (B.long || []).length, ns = (B.short || []).length, sig = one('LONG') + ' | ' + one('SHORT');
    if (sig === FLB.sig) return;
    var first = FLB.sig === null; FLB.sig = sig;
    if (first && !nl && !ns) return;
    try { ctx.onFlag({ t: ctx.now, kind: 'board', side: nl && !ns ? 'UP' : ns && !nl ? 'DOWN' : 'NEUTRAL', level: '', evidence: sig, price: md.px > 0 ? md.px : '' }); } catch (e) { /* logging must never break the page */ }
  }
  // One Bias line (operator 11-10: gauge SHORT 5 of 5 while two LONG SETUP banners said "big picture up" and the level card said MIXED).
  // Names the three clocks, which one wins (OURS: the shortest clock governs the next 15m close, the 1h-4h lean is the backdrop; the level
  // card only breaks a tie), then the two 15m-close lines. Observation only: no order, size or entry wording.
  function biasLine(ctx, md) {
    var g = ctx.pulse, hi = g && isFinite(g.hi) ? g.hi : NaN, W = { 1: 'UP', '-1': 'DOWN', 0: 'MIXED' };
    var pw = !isFinite(hi) ? 'NO DATA' : hi >= 0.25 ? 'UP' : hi <= -0.25 ? 'DOWN' : 'MIXED';
    var st = (ctx.k15 && md.lad) ? (stories(ctx, md) || []).filter(function (x) { return x && x.idea; }) : [];
    var lw = !st.length ? 'MIXED' : st.some(function (x) { return x.idea !== st[0].idea; }) ? 'MIXED' : (st[0].idea === 'LONG' ? 'UP' : 'DOWN');
    var gw = md.dir === 'LONG' ? 'UP' : md.dir === 'SHORT' ? 'DOWN' : 'WAIT';
    var c = function (w) { return w === 'UP' ? 'up' : w === 'DOWN' ? 'down' : 'dim'; };
    var win = gw !== 'WAIT' ? gw : pw !== 'NO DATA' && pw !== 'MIXED' ? pw : lw, agree = gw === pw && pw === lw || (gw === 'WAIT' && pw === lw);
    var a = md.lad && md.lad.above[0], b = md.lad && md.lad.below[0], lvl = function (z) { return n0(z.price) + ' (' + esc(z.name) + ')'; };
    // Conflict (operator 11-12, default A): a directional idea against the opposite big picture = ONE line, stand aside until a 15m close decides.
    var idea = lw !== 'MIXED' ? lw : gw !== 'WAIT' ? gw : 'MIXED', conflict = idea !== 'MIXED' && (pw === 'UP' || pw === 'DOWN') && idea !== pw;
    if (conflict) {
      var iz = lw !== 'MIXED' && st.length ? { price: st[0].price, name: st[0].name } : (idea === 'UP' ? b : a), nm = function (w) { return w === 'UP' ? 'long' : 'short'; };
      var ctxt = 'conflict: ' + nm(idea) + ' idea' + (iz ? ' at ' + lvl(iz) : '') + ' vs ' + nm(pw) + ' big picture, stand aside until a 15m close decides';
      var cdec = (a ? ' Close above ' + lvl(a) + ' = long, ' : ' ') + (b ? (a ? 'below ' : 'Close below ') + lvl(b) + ' = short.' : '');
      return '<div class="hm-card hm-bias conflict" title="' + esc(ctxt + '.' + cdec.replace(/<[^>]*>/g, '')) + '"><div class="hm-h">Bias <b class="amber">STAND ASIDE</b></div><div class="hm-say amber">' + esc(ctxt) + '.' + cdec + '</div></div>';
    }
    var cl = '<span class="' + c(gw) + '">now (minutes) ' + gw + ' ' + Math.max(md.bull, md.bear) + '/' + md.n + '</span> | <span class="' + c(pw) + '">bigger trend (1h-4h) ' + pw + '</span> | <span class="' + c(lw) + '">at the level ' + lw + '</span>';
    var dec = (a ? '<span class="up">15m close above ' + n0(a.price) + ' (' + esc(a.name) + '): long confirmed</span>' : '') + (a && b ? ' ' : '') +
      (b ? '<span class="down">15m close below ' + n0(b.price) + ' (' + esc(b.name) + '): short confirmed</span>' : '');
    var why = agree ? 'Short term, bigger trend and the level all agree.' : (gw !== 'WAIT' ? 'The next few minutes lean ' + gw + '; the bigger 1h-4h trend is ' + (pw === 'NO DATA' ? 'not read' : pw) + '. The short-term lean covers the next 15m candle only.' : (pw === 'UP' || pw === 'DOWN' ? 'No short-term lean; the bigger 1h-4h trend (' + pw + ') is the guide.' : 'Nothing leans yet.'));
    var txt = 'Bias ' + (win === 'WAIT' ? 'none yet' : win) + ': ' + cl.replace(/<[^>]*>/g, '') + '. ' + why + ' ' + dec.replace(/<[^>]*>/g, '');
    return '<div class="hm-card hm-bias ' + c(win) + '" title="' + esc(txt) + '"><div class="hm-h">Bias <b class="' + c(win) + '">' + (win === 'WAIT' ? 'none yet' : win) + '</b><span class="hm-sub">' + esc(why) + '</span></div>' +
      '<div class="hm-say">' + dec + '</div></div>';
  }
  function render(el, ctx) {
    if (!el) return;
    var md = model(ctx), fl = flashes(ctx, md);
    boardLog(ctx, md);
    var box = el.getBoundingClientRect(), W = Math.max(600, Math.round(box.width * 0.70)), H = Math.max(360, Math.round(box.height - 8));
    var head = '<div class="hm-top"><b class="hm-px">' + (md.px > 0 ? n0(md.px) : 'Price NOT_IN_DATA') + '</b>' +
      '<span class="hm-nx dim">5-minute candles, last 12 h</span>' +
      (md.lad.above[0] && inFrame(md, md.lad.above[0]) ? '<span class="hm-nx down">▲ ' + n0(md.lad.above[0].price) + ' <small>' + esc(md.lad.above[0].name) + ', ' + ((md.lad.above[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (md.lad.below[0] && inFrame(md, md.lad.below[0]) ? '<span class="hm-nx up">▼ ' + n0(md.lad.below[0].price) + ' <small>' + esc(md.lad.below[0].name) + ', ' + ((md.lad.below[0].price / md.px - 1) * 100).toFixed(2) + '%</small></span>' : '') +
      (ctx.scen && ctx.scen[0] ? '<span class="hm-nx dim">playbook: if up ' + n0(ctx.scen[0].up) + ' / if down ' + n0(ctx.scen[0].down) + '</span>' : '') + '</div>';
    // Height budget (operator 11-13: "the chart occupies all the space"): candles, then the volume strip, then WaveTrend (open by default).
    var wh = wtOpen ? Math.round(Math.min(300, Math.max(150, (H - 34) * 0.30))) : 0, vh = 78;
    if (!el._wtl) { el._wtl = true; var tg = function (e) { if (e.type === 'keydown' && e.key !== 'Enter' && e.key !== ' ') return; if (e.target.closest && e.target.closest('[data-wttoggle]')) { e.preventDefault(); wtOpen = !wtOpen; wtSave(wtOpen); render(el, el._ctx); } else if (e.target.closest && e.target.closest('[data-foldtoggle]')) { e.preventDefault(); foldOpen = !foldOpen; foldSave(foldOpen); render(el, el._ctx); } }; el.addEventListener('click', tg); el.addEventListener('keydown', tg); }
    el._ctx = ctx;
    ctx._tm = null;   // trigger row removed 11-12 (he could not select or read it); timingStrip/timingOf stay for tests
    el.innerHTML = '<div class="hm-chart">' + head + caption(ctx, md) + chart(ctx, md, W, Math.max(220, H - 122 - 26 - vh - wh - (wtOpen ? 38 : 0))) + volPane(ctx, md, W, vh) + volRead(ctx).html + wtSoWhat(ctx, md) + (wtOpen ? wtLanes(ctx, W, wh) : '') + '</div><div class="hm-rail">' + biasLine(ctx, md) + boardCard(ctx, md) + storyCard(ctx, md) + indCard(ctx, md) + liqCard(ctx, md) + newsCard(ctx) + foldCard(ctx, md) + '</div>';
  }
  var CSS = '#p-home{display:grid;grid-template-columns:70% 30%;gap:8px;padding:6px!important;overflow:hidden!important}' +
    '.hm-chart{position:relative;min-width:0;display:flex;flex-direction:column}.hm-svg{width:100%;flex:1;min-height:0}' +
    '.hm-top{display:flex;gap:14px;align-items:baseline;height:30px;white-space:nowrap;overflow:hidden}.hm-px{font:700 26px var(--mono,monospace);color:var(--amber)}.hm-nx{font:700 15px var(--mono,monospace)}.hm-nx small{font:12px system-ui;color:var(--dim)}' +
    '.hm-ses.s0{fill:#3b82f6;opacity:.05}.hm-ses.s1{fill:#a855f7;opacity:.06}.hm-ses.s2{fill:#f59e0b;opacity:.07}.hm-sest{fill:var(--dim);font:12px system-ui}' +
    '.hm-grid{stroke:var(--line);stroke-width:.5}.hm-ax{fill:var(--dim);font:11px var(--mono,monospace)}.hm-wk{stroke-width:1}.hm-wk.up{stroke:var(--up)}.hm-wk.down{stroke:var(--down)}.hm-bd.up{fill:var(--up)}.hm-bd.down{fill:var(--down)}' +
    '.hm-lv{stroke-width:1;stroke-dasharray:5 4;opacity:.75}.hm-lv.multi{stroke-width:2;stroke-dasharray:none;opacity:.6}.hm-lv.up{stroke:var(--up)}.hm-lv.down{stroke:var(--down)}' +
    '.hm-sc{stroke-width:3;opacity:.9}.hm-sc.up{stroke:var(--up)}.hm-sc.down{stroke:var(--down)}.hm-sct{font:700 12px system-ui}.hm-sct.up{fill:var(--up)}.hm-sct.down{fill:var(--down)}.hm-lead{stroke:var(--dim);stroke-width:.5}.hm-lt{font:12px system-ui;fill:var(--fg)}.hm-lt.up .hm-lp{fill:var(--up)}.hm-lt.down .hm-lp{fill:var(--down)}.hm-lp{font:700 12px var(--mono,monospace)}' +
    '.hm-uo{stroke:#60a5fa;stroke-width:2}.hm-uot{fill:#60a5fa;font:700 12px system-ui}.hm-now{stroke:var(--amber);stroke-width:1;stroke-dasharray:2 3}.hm-tag{fill:var(--amber)}.hm-tagt{fill:#111;font:700 12px var(--mono,monospace)}' +
    '.hm-rail{display:grid;grid-template-rows:auto auto auto auto auto 1fr auto;gap:6px;min-height:0;overflow:hidden}.hm-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px;min-height:0;overflow:hidden}' +
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
    '.hm-mon{display:flex;gap:12px;align-items:center}.hm-ar{font-size:22px;text-align:center;line-height:1}.hm-from{font-size:10px;color:var(--dim);margin-top:2px}' +
    '.hm-nr{display:grid;grid-template-columns:16px 40px 1fr 30px;gap:6px;align-items:center;font-size:12px;padding:2px 0;border-top:1px solid var(--line)}.hm-ns{height:6px;background:var(--line);border-radius:3px;overflow:hidden}.hm-ns span{display:block;height:100%;background:var(--amber)}.hm-nh{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hm-na{color:var(--dim);text-align:right}.hm-ev{margin-left:auto;font:700 12px system-ui;color:var(--amber);border:1px solid var(--amber);border-radius:10px;padding:0 8px}' +
    '.hm-nid{color:var(--dim);font-size:12px;padding:6px 0}' +
    '.hm-st{border-top:1px solid var(--line);padding:3px 0}.hm-st1{display:flex;gap:6px;align-items:baseline;font-size:12px}.hm-stp{font:700 13px var(--mono,monospace)}.hm-stn{color:var(--fg);overflow:hidden;white-space:nowrap;text-overflow:ellipsis;max-width:40%}' +
    '.hm-sts{margin-left:auto;font:700 11px system-ui;padding:0 6px;border-radius:8px;border:1px solid}.hm-sts.turn{color:#22c55e}.hm-sts.thru{color:#ef4444}.hm-sts.amber{color:var(--amber)}.hm-sts.dim{color:var(--dim)}' +
    '.fl-c{display:inline-block;margin:0 6px;padding:0 6px;border-radius:4px;color:#111}.fl-c.up{background:var(--up)}.fl-c.down{background:var(--down);color:#fff}' +
    '.hm-idea{font:700 12px system-ui!important;padding:0 6px;border-radius:4px;color:#111}.hm-idea.down{background:var(--down);color:#fff}.hm-idea.up{background:var(--up)}' +
    '.hm-ecs{display:flex;flex-wrap:wrap;gap:3px;margin-top:2px;align-items:center}.hm-ec{font:700 10px system-ui;padding:0 5px;border-radius:3px;background:var(--line);color:var(--fg)}.hm-ec.turn{background:#166534;color:#dcfce7}.hm-ec.thru{background:#7f1d1d;color:#fee2e2}.hm-sc2{margin-left:auto;color:var(--dim);font-size:10px}.hm-ecs em{color:var(--dim);font-size:11px}' +
    '.hm-stv{font-size:11px;color:var(--fg);margin-top:2px}.amber{color:var(--amber)}' +
    '.hm-vb{opacity:.75}.hm-vb.up{fill:var(--up)}.hm-vb.down{fill:var(--down)}.hm-vavg{fill:none;stroke:var(--fg);stroke-width:1.2;opacity:.8}.hm-vlt{fill:var(--dim);font:11px system-ui}.hm-vol{width:100%;flex:none;border-top:1px solid var(--line)}' +
    '.hm-ma{fill:none;stroke-width:1.6}.hm-ma.m0{stroke:#38bdf8}.hm-ma.m1{stroke:#c084fc}.hm-ma.m2{stroke:var(--fg);stroke-dasharray:6 3}.hm-mal{font-weight:700}.hm-mal.m0{fill:#38bdf8}.hm-mal.m1{fill:#c084fc}.hm-mal.m2{fill:var(--fg)}.hm-vr2.up b,.hm-vr2.down b{color:inherit}.hm-vr2.up{border-left:3px solid var(--up)}.hm-vr2.down{border-left:3px solid var(--down)}' +
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
    '.hm-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px}.hm-bcard{box-sizing:border-box;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 8px;min-width:0;overflow:hidden}.hm-bcard.up{border-color:var(--up)}.hm-bcard.down{border-color:var(--down)}' +
    '.hm-bbar{height:8px;border-radius:4px;background:var(--line);margin:3px 0}.hm-bbar span{display:block;height:100%;border-radius:4px}.hm-bbar.up span{background:var(--up)}.hm-bbar.down span{background:var(--down)}' +
    '.hm-bl2{margin:0;padding-left:14px;font-size:11px;max-height:64px;overflow:hidden}.hm-brate{font-size:11px;margin-top:3px}.hm-brate small{color:var(--dim);font-size:10px}' +
    '.hm-bias.up{border-color:var(--up)}.hm-bias.down{border-color:var(--down)}.hm-say .up{color:var(--up)}.hm-say .down{color:var(--down)}' +
    '.hm-vr{display:grid;grid-template-columns:34px 1fr auto;gap:6px;align-items:baseline;font-size:13px;margin-top:3px;padding-left:6px;border-left:4px solid var(--dim)}.hm-vr.up{border-left-color:var(--up)}.hm-vr.down{border-left-color:var(--down)}.hm-vr b{font:700 13px var(--mono,monospace);color:var(--fg)}.hm-vr.up span{color:var(--up)}.hm-vr.down span{color:var(--down)}.hm-vr small{color:var(--dim);font-size:11px}.hm-vr em{font-style:normal;font-weight:700;color:var(--amber)}' +
    '.hm-lg{font-size:11px;color:var(--dim);margin-top:2px}.hm-fold{max-height:60vh;overflow:auto}.hm-cap{font-size:12px;margin:2px 0 0;padding:2px 6px;border-radius:4px;background:var(--line);color:var(--fg)}.hm-sl{stroke:var(--dim);stroke-width:1;stroke-dasharray:2 4;opacity:.8}.hm-fm.up{fill:var(--up)}.hm-fm.down{fill:var(--down)}.hm-fm.amber{fill:var(--amber)}.hm-fm{stroke:var(--bg,#000);stroke-width:1}.hm-sw{font-size:12px;margin-top:4px;padding:2px 6px;border-radius:4px;background:var(--line);color:var(--fg)}.hm-wc{display:inline-block;margin-right:8px;font-size:11px;font-weight:600}.hm-wc i{font-style:normal;font-weight:400;color:var(--dim);margin-right:2px}.hm-wc.up{color:var(--up)}.hm-wc.down{color:var(--down)}.hm-wc.dim{color:var(--dim)}.hm-wl{font-size:11px;color:var(--dim);margin-left:4px}.hm-wfull{font-weight:400}.hm-whow{font-weight:400;font-size:11px;opacity:.85}.hm-key{font-size:11px;background:none;opacity:.85}.hm-key .up{color:var(--up)}.hm-key .down{color:var(--down)}.hm-key .amber{color:var(--amber)}.hm-sw b{color:var(--amber)}.hm-sw small{color:var(--dim);font-size:10px}.hm-wts+.hm-sw{margin:0}.hm-wsw{cursor:pointer}div.hm-sw{flex:none}' +
    '.hm-bias.conflict{border-color:var(--amber)}.hm-stm{font-size:11px;color:var(--dim)}.hm-an{font-size:11px;margin-top:1px;padding-left:6px;border-left:2px solid currentColor}.hm-an.dim{color:var(--fg);border-left-color:var(--dim)}' +
    '@keyframes hmfl{50%{opacity:.35}}';
  function injectCss(doc) { if (!doc || doc.getElementById('hm-css')) return; var st = doc.createElement('style'); st.id = 'hm-css'; st.textContent = CSS + (NF && NF.CSS || ''); doc.head.appendChild(st); }
  // Flag log helpers (pure, tested in node): append with cap, and CSV for the Download button.
  var FLAG_COLS = ['t', 'kind', 'side', 'level', 'evidence', 'price'];
  function flagLogAdd(log, row, cap) { var out = (log || []).concat([row]); return out.length > cap ? out.slice(out.length - cap) : out; }
  function flagCsv(log) {
    var q = function (v) { v = String(v == null ? '' : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    return [FLAG_COLS.join(',')].concat((log || []).map(function (r) { return FLAG_COLS.map(function (c) { return q(c === 't' && isFinite(r.t) ? new Date(r.t).toISOString() : r[c]); }).join(','); })).join('\n') + '\n';
  }
  var api = { flagLogAdd: flagLogAdd, flagCsv: flagCsv, model: model, zoneName: zoneName, flashes: flashes, render: render, injectCss: injectCss, WORDS: WORDS, _FL: FL, _moneyCard: moneyCard, _indCard: indCard, _stories: stories, _timingStrip: timingStrip, _nearLevel: nearLevel, _biasLine: biasLine, _liqCard: liqCard, _wtSoWhat: wtSoWhat, _wtSetOpen: function (v) { wtOpen = !!v; wtSave(wtOpen); }, _foldCard: foldCard, _boardLog: boardLog, _boardLogReset: function () { FLB.sig = null; }, _foldSetOpen: function (v) { foldOpen = !!v; foldSave(foldOpen); }, _wtLoad: function () { wtOpen = wtLoad(); return wtOpen; }, _soWhat: soWhat, _chart: chart, _caption: caption, _chartKey: chartKey, _divLine: divLine, _boardInputs: boardInputs, _inFrame: inFrame, _boardCard: boardCard, _volPane: volPane, _volRead: volRead, _emaS: emaS, _smaS: smaS, _storyCard: storyCard, _newsCard: newsCard, _liqMeaning: liqMeaning, MA5: MA5 };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAHOME = api;
})(typeof window !== 'undefined' ? window : this);
