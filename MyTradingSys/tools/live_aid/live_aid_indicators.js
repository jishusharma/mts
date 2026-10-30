/* live_aid_indicators.js - indicator maths for the live aid page (browser global LiveAid, or node require).
 * Parameters: RSI 14 / SMA 14 / BB 20,2 / ATR 14 / VWAP hlc3 anchored 00:00Z = SOURCED (operator's chart setup).
 * Conventions follow TradingView: RSI and ATR use Wilder RMA seeded with the SMA of the first n values;
 * Bollinger uses population standard deviation. Arrays: index i = bar i; NaN until enough bars.
 */
(function (root) {
  'use strict';

  function rma(values, n) { // Wilder smoothing, seed = SMA of first n finite values
    var out = new Array(values.length).fill(NaN), sum = 0, cnt = 0, prev = NaN;
    for (var i = 0; i < values.length; i++) {
      var v = values[i];
      if (!isFinite(v)) continue;
      if (cnt < n) {
        sum += v; cnt++;
        if (cnt === n) { prev = sum / n; out[i] = prev; }
      } else {
        prev = (prev * (n - 1) + v) / n; out[i] = prev;
      }
    }
    return out;
  }

  function sma(values, n) { // SMA over the last n values; NaN if any of them is NaN
    var out = new Array(values.length).fill(NaN);
    for (var i = n - 1; i < values.length; i++) {
      var s = 0, ok = true;
      for (var j = i - n + 1; j <= i; j++) { if (!isFinite(values[j])) { ok = false; break; } s += values[j]; }
      if (ok) out[i] = s / n;
    }
    return out;
  }

  function rsi(closes, n) {
    n = n || 14;
    var g = [NaN], l = [NaN];
    for (var i = 1; i < closes.length; i++) {
      var d = closes[i] - closes[i - 1];
      g.push(d > 0 ? d : 0); l.push(d < 0 ? -d : 0);
    }
    var ag = rma(g, n), al = rma(l, n);
    return ag.map(function (a, i) {
      var b = al[i];
      if (!isFinite(a) || !isFinite(b)) return NaN;
      if (b === 0) return a === 0 ? 50 : 100;
      return 100 - 100 / (1 + a / b);
    });
  }

  function bollinger(closes, n, k) {
    n = n || 20; k = k || 2;
    var basis = sma(closes, n), upper = [], lower = [], pctB = [], width = [];
    for (var i = 0; i < closes.length; i++) {
      if (!isFinite(basis[i])) { upper.push(NaN); lower.push(NaN); pctB.push(NaN); width.push(NaN); continue; }
      var v = 0;
      for (var j = i - n + 1; j <= i; j++) v += (closes[j] - basis[i]) * (closes[j] - basis[i]);
      var sd = Math.sqrt(v / n), up = basis[i] + k * sd, lo = basis[i] - k * sd;
      upper.push(up); lower.push(lo);
      pctB.push(up === lo ? NaN : (closes[i] - lo) / (up - lo));
      width.push((up - lo) / basis[i]);
    }
    return { basis: basis, upper: upper, lower: lower, pctB: pctB, width: width };
  }

  function atr(highs, lows, closes, n) {
    n = n || 14;
    var tr = highs.map(function (h, i) {
      if (i === 0) return h - lows[0];
      var pc = closes[i - 1];
      return Math.max(h - lows[i], Math.abs(h - pc), Math.abs(lows[i] - pc));
    });
    return rma(tr, n);
  }

  var DAY = 86400000;
  function dayVwap(times, highs, lows, closes, vols) { // hlc3, resets at each 00:00Z
    var out = [], pv = 0, vv = 0, day = null;
    for (var i = 0; i < times.length; i++) {
      var d = Math.floor(times[i] / DAY);
      if (d !== day) { day = d; pv = 0; vv = 0; }
      var tp = (highs[i] + lows[i] + closes[i]) / 3;
      pv += tp * vols[i]; vv += vols[i];
      out.push(vv > 0 ? pv / vv : NaN);
    }
    return out;
  }

  // Deribit BTC-PERPETUAL is inverse: size in USD contracts, P&L in BTC.
  function inversePnlBtc(side, sizeUsd, entry, mark) {
    var long = sizeUsd * (1 / entry - 1 / mark);
    return side === 'short' ? -long : long;
  }

  function closedPnlBtc(side, entry, fills) { // fills: [{size, price}], each closes part of the position
    return fills.reduce(function (s, f) { return s + inversePnlBtc(side, f.size, entry, f.price); }, 0);
  }

  // Parse Binance fapi klines rows [openTime, o, h, l, c, v, ...] into column arrays.
  function columns(rows) {
    var c = { t: [], o: [], h: [], l: [], c: [], v: [] };
    rows.forEach(function (r) {
      c.t.push(+r[0]); c.o.push(+r[1]); c.h.push(+r[2]); c.l.push(+r[3]); c.c.push(+r[4]); c.v.push(+r[5]);
    });
    return c;
  }

  // WaveTrend (LazyBear), FORMULAS.md s20, same conventions as backtest/layers/wavetrend/wavetrend.py:
  // ap=hlc3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4). EMAs seed on the
  // first valid value; a time gap, a NaN bar or a flat window (d <= 1e-9*|ap|) drops the state; values shown only after
  // `warmup` valid bars (200, OURS). Cross: first bar strictly on the other side of the last strict side of wt1-wt2.
  function wavetrend(times, highs, lows, closes, tfMs, warmup) {
    warmup = warmup || 200;
    var n = closes.length, a1 = 2 / 11, a2 = 2 / 22, esa = null, dev = null, tci = null, since = 0, prevT = null;
    var raw = new Array(n).fill(NaN), keep = new Array(n).fill(false);
    for (var i = 0; i < n; i++) {
      if (prevT !== null && times[i] - prevT !== tfMs) { esa = dev = tci = null; since = 0; }
      prevT = times[i];
      if (!isFinite(highs[i]) || !isFinite(lows[i]) || !isFinite(closes[i])) { esa = dev = tci = null; since = 0; continue; }
      var ap = (highs[i] + lows[i] + closes[i]) / 3;
      esa = esa === null ? ap : a1 * ap + (1 - a1) * esa;
      var x = Math.abs(ap - esa);
      dev = dev === null ? x : a1 * x + (1 - a1) * dev;
      if (dev <= 1e-9 * Math.abs(ap)) { tci = null; since = 0; continue; }
      var ci = (ap - esa) / (0.015 * dev);
      tci = tci === null ? ci : a2 * ci + (1 - a2) * tci;
      since++; raw[i] = tci; keep[i] = since >= warmup;
    }
    var w2 = sma(raw, 4), wt1 = [], wt2 = [], ev = [], last = 0;
    for (i = 0; i < n; i++) {
      wt1.push(keep[i] ? raw[i] : NaN); wt2.push(keep[i] ? w2[i] : NaN);
      if (!isFinite(wt1[i]) || !isFinite(wt2[i])) { ev.push(0); last = 0; continue; }
      var side = (wt1[i] > wt2[i]) - (wt1[i] < wt2[i]);
      ev.push(side !== 0 && last !== 0 && side !== last ? side : 0);
      if (side !== 0) last = side;
    }
    return { wt1: wt1, wt2: wt2, event: ev };
  }

  // Fold intraday rows [t, o, h, l, c, v] into UTC-day rows with the same layout (t = 00:00Z of the day).
  function utcDays(rows) {
    var out = [], cur = null;
    rows.forEach(function (r) {
      var d = Math.floor(+r[0] / DAY) * DAY;
      if (!cur || cur[0] !== d) { cur = [d, +r[1], +r[2], +r[3], +r[4], +r[5]]; out.push(cur); return; }
      if (+r[2] > cur[2]) cur[2] = +r[2];
      if (+r[3] < cur[3]) cur[3] = +r[3];
      cur[4] = +r[4]; cur[5] += +r[5];
    });
    return out;
  }

  // ---------- in-trade readings (card live-aid-in-trade-panel). Every threshold below = OURS, fixed in STEPS.md before any data
  // was looked at. sd = +1 long, -1 short. Descriptive only: no entry, exit or size wording. ----------
  var IT = { divWin: 15, flowShortMs: 60000, flowLongMs: 900000, squeezeEps: 0.0005, domPct: 0.0025, domImb: 0.2,
             vwapBars: 5, supportN: 2, reduceAt: 3, feedMs: 30000 };

  function finiteArr(a) { return a.every(isFinite); }
  // Divergence: last 2w values split in halves h1,h2. bullish (+1): price lower low in h2 but indicator higher low; bearish (-1): mirror on highs.
  function divergence(price, ind, w) {
    w = w || IT.divWin;
    var n = price.length;
    if (n < 2 * w || ind.length !== n) return null;
    var p1 = price.slice(n - 2 * w, n - w), p2 = price.slice(n - w), i1 = ind.slice(n - 2 * w, n - w), i2 = ind.slice(n - w);
    if (!finiteArr(p1) || !finiteArr(p2) || !finiteArr(i1) || !finiteArr(i2)) return null;
    var mx = function (a) { return Math.max.apply(null, a); }, mn = function (a) { return Math.min.apply(null, a); };
    if (mn(p2) < mn(p1) && mn(i2) > mn(i1)) return 1;
    if (mx(p2) > mx(p1) && mx(i2) < mx(i1)) return -1;
    return 0;
  }
  // Taker flow from trades [{t, usd, buy}]: delta = net buy-sell USD over the last 60 s, cvd = net over the last 15 min (or since the first trade).
  function flow(trades, now) {
    if (!trades || !trades.length) return null;
    var d = 0, c = 0;
    trades.forEach(function (x) {
      var s = x.buy ? x.usd : -x.usd;
      if (now - x.t <= IT.flowLongMs) c += s;
      if (now - x.t <= IT.flowShortMs) d += s;
    });
    return { delta: d, cvd: c, spanMs: Math.min(IT.flowLongMs, now - trades[0].t) };
  }
  // Trades channel is sparse: a quiet tape is data (delta 0), not a dead feed. Live = a trade within feedMs, or at least one
  // trade since connect and the same socket's ticker within feedMs. trT / linkT = last trade / last ticker time (0 = never).
  function flowLive(trT, linkT, now) {
    if (!trT) return false;
    return now - trT <= IT.feedMs || (linkT > 0 && now - linkT <= IT.feedMs);
  }
  // Price vs open interest over a window: dp, doi are fractional changes. eps = 0.05%.
  function squeeze(dp, doi) {
    if (!isFinite(dp) || !isFinite(doi)) return null;
    var e = IT.squeezeEps;
    if (Math.abs(dp) < e) return 'flat';
    if (Math.abs(doi) < e) return dp > 0 ? 'up, OI flat' : 'down, OI flat';
    if (dp > 0) return doi > 0 ? 'up, OI up: new longs' : 'up, OI down: short covering (squeeze)';
    return doi > 0 ? 'down, OI up: new shorts' : 'down, OI down: long unwind';
  }
  // Order book within +/- domPct of px. bids/asks [[price, size]]. imb = (bid-ask)/(bid+ask); wall = biggest level in that band.
  function dom(bids, asks, px) {
    if (!bids || !asks || !bids.length || !asks.length || !isFinite(px)) return null;
    var lo = px * (1 - IT.domPct), hi = px * (1 + IT.domPct), b = 0, a = 0, wall = null;
    bids.forEach(function (x) { if (x[0] >= lo) { b += x[1]; if (!wall || x[1] > wall.size) wall = { side: 'bid', price: x[0], size: x[1] }; } });
    asks.forEach(function (x) { if (x[0] <= hi) { a += x[1]; if (!wall || x[1] > wall.size) wall = { side: 'ask', price: x[0], size: x[1] }; } });
    if (b + a === 0) return null;
    return { bid: b, ask: a, imb: (b - a) / (b + a), wall: wall };
  }
  // Nearest supports for the trade: long = levels below px, short = levels above px. levels [{n, p}].
  function supports(levels, px, sd) {
    if (!isFinite(px)) return null;
    var f = levels.filter(function (l) { return isFinite(l.p) && (sd > 0 ? l.p < px : l.p > px); });
    f.sort(function (x, y) { return Math.abs(x.p - px) - Math.abs(y.p - px); });
    return f.slice(0, IT.supportN);
  }
  // VWAP test over the last k 1m bars (v = per-bar VWAP series): touch = bar range contains vwap. held = last close on the trade side, lost = other side.
  function vwapTest(h, l, c, v, sd) {
    var n = c.length, k = IT.vwapBars;
    if (n < k || v.length !== n || !isFinite(v[n - 1])) return null;
    var touched = false;
    for (var i = n - k; i < n; i++) if (isFinite(v[i]) && l[i] <= v[i] && v[i] <= h[i]) touched = true;
    var side = (c[n - 1] - v[n - 1]) * sd;
    return { dist: c[n - 1] - v[n - 1], touched: touched, result: !touched ? 'no test' : side >= 0 ? 'held' : 'lost' };
  }
  // Flags: +1 for the trade, -1 against, 0 neutral, null NOT_IN_DATA. Stay confidence = for / available; reduce-rule R = against >= 3.
  function flagDiv(d, sd) { return d === null ? null : d === 0 ? 0 : (d === sd ? 1 : -1); }
  function flagSqueeze(dp, doi, sd) {
    if (!isFinite(dp) || !isFinite(doi)) return null;
    if (Math.abs(dp) < IT.squeezeEps) return 0;
    if (dp * sd < 0) return -1;
    return doi > IT.squeezeEps ? 1 : 0;
  }
  function flagFlow(f, sd) {
    if (!f) return null;
    var a = Math.sign(f.cvd) * sd, b = Math.sign(f.delta) * sd;
    return a > 0 && b > 0 ? 1 : a < 0 && b < 0 ? -1 : 0;
  }
  function flagDom(d, sd) { return !d ? null : d.imb * sd > IT.domImb ? 1 : d.imb * sd < -IT.domImb ? -1 : 0; }
  function flagVwap(t) { return !t ? null : t.result === 'held' ? 1 : t.result === 'lost' ? -1 : 0; }
  function confidence(flags) {
    var av = flags.filter(function (x) { return x !== null; }), f = av.filter(function (x) { return x > 0; }).length, a = av.filter(function (x) { return x < 0; }).length;
    return { avail: av.length, total: flags.length, for: f, against: a, reduceRule: av.length > 0 && a >= IT.reduceAt };
  }

  // Coil and pierce (15m), operator ask 2026-10-30. Probabilities are the MEASURED descriptive base rates of
  // research/pre_us_squeeze_2026-10-29 and research/bb_pierce_force_2026-10-29 (Binance 1m 2022-01..2026-09, no fees,
  // within 2 h of the US open). Thresholds are OURS, copied from those studies. rows: [t,o,h,l,c,v,..,takerBuy@9].
  var CP = { coilPct: 0.20, lookback: 2880, pierceAgeMax: 8, volStrong: 3.56, volWeak: 1.96, deltaWith: 0.10,
    dist: [{ max: 0.005, reach: 74, fail: 25, n: 156 }, { max: 0.015, reach: 36, fail: 54, n: 313 }, { max: Infinity, reach: 13, fail: 59, n: 540 }],
    force: { strong: { reach: 39, fail: 42, n: 197 }, weak: { reach: 26, fail: 58, n: 351 }, mid: { reach: 30, fail: 52, n: 1009 } },
    coil: { expand: 1.54, up: 29, down: 29, side: 43, both: 23, n: 192 }, noCoil: { expand: 1.26, up: 25, down: 29, side: 47, both: 16, n: 800 } };
  function coilPierce(rows, tfMs, now, pdh, pdl) {
    var closed = rows.filter(function (r) { return +r[0] + tfMs <= now; });
    var c = closed.map(function (r) { return +r[4]; }), bb = bollinger(c, 20, 2), i = c.length - 1;
    if (i < 41 || !isFinite(bb.width[i])) return null;
    function pctAt(j) { var h = bb.width.slice(Math.max(0, j - CP.lookback), j).filter(isFinite); return { p: h.filter(function (x) { return x < bb.width[j]; }).length / h.length, n: h.length }; }
    var pa = pctAt(i), pct = pa.p, hist = { length: pa.n };
    var out = { bwPct: pct, histBars: hist.length, coil: pct <= CP.coilPct, width: bb.width[i], upper: bb.upper[i], lower: bb.lower[i], mid: bb.basis[i],
      pierce: null, ctx: pct <= CP.coilPct ? CP.coil : CP.noCoil };
    for (var k = i; k > i - CP.pierceAgeMax && k > 20; k--) {
      var side = c[k] > bb.upper[k] && c[k - 1] <= bb.upper[k - 1] ? 'up' : c[k] < bb.lower[k] && c[k - 1] >= bb.lower[k - 1] ? 'down' : null;
      if (!side) continue;
      var v = +closed[k][5], vs = 0; for (var j = k - 20; j < k; j++) vs += +closed[j][5];
      var vr = v / (vs / 20), tb = closed[k].length > 9 ? +closed[k][9] : NaN;
      var ds = isFinite(tb) && v > 0 ? (2 * tb - v) / v * (side === 'up' ? 1 : -1) : NaN;
      var lvl = side === 'up' ? pdh : pdl;
      if (!isFinite(lvl) || (side === 'up' ? lvl <= c[k] : lvl >= c[k])) lvl = NaN;
      var dist = isFinite(lvl) ? Math.abs(lvl / c[k] - 1) : NaN, db = null;
      for (var q = 0; q < CP.dist.length && isFinite(dist); q++) if (dist <= CP.dist[q].max) { db = CP.dist[q]; break; }
      var fb = vr >= CP.volStrong && ds > CP.deltaWith ? 'strong' : vr < CP.volWeak ? 'weak' : 'mid';
      out.pierce = { side: side, t: +closed[k][0], ageBars: i - k, close: c[k], volRatio: vr, deltaShare: ds, level: lvl, dist: dist,
        byDist: db, coilBefore: pctAt(k - 1).p <= CP.coilPct, force: fb, byForce: CP.force[fb], midBack: side === 'up' ? c[i] < bb.basis[i] : c[i] > bb.basis[i] };
      break;
    }
    return out;
  }

  // ---------- liquidations (rules: STEPS.md "Liquidation rules"; venue side codes SOURCED from their API docs, the rest OURS) ----------
  // Event = {t, venue, side: 'long' | 'short' (the position liquidated), usd, px}.
  var LQ = { bigUsd: 100000, domRatio: 2, keepMs: 900000, tapeN: 8, liveMs: 60000 };
  function liqDeribit(x, t) { // trade with liquidation T (taker), M (maker) or MT; amount is USD
    var L = x.liquidation || '', takerLong = x.direction === 'sell', out = [];
    if (L.indexOf('T') >= 0) out.push({ t: t, venue: 'DERIBIT', side: takerLong ? 'long' : 'short', usd: +x.amount, px: +x.price });
    if (L.indexOf('M') >= 0) out.push({ t: t, venue: 'DERIBIT', side: takerLong ? 'short' : 'long', usd: +x.amount, px: +x.price });
    return out;
  }
  function liqBybit(x) { return { t: +x.T, venue: 'BYBIT', side: x.S === 'Buy' ? 'long' : 'short', usd: (+x.v) * (+x.p), px: +x.p }; }
  function liqBinance(m) { var o = m.o; return { t: +o.T, venue: 'BINANCE', side: o.S === 'SELL' ? 'long' : 'short', usd: (+o.q) * (+o.ap), px: +o.ap }; }
  function liqSum(ev, now, ms) {
    var r = { long: 0, short: 0, n: 0, big: 0 };
    ev.forEach(function (e) { if (e.t <= now && now - e.t <= ms) { r[e.side] += e.usd; r.n++; if (e.usd >= LQ.bigUsd) r.big++; } });
    r.dom = r.long + r.short === 0 ? 'none' : r.long >= LQ.domRatio * r.short ? 'longs' : r.short >= LQ.domRatio * r.long ? 'shorts' : 'mixed';
    return r;
  }

  // Funding and premium (STEPS.md "Funding rules"). Rates are per 8h (Deribit funding_8h; Bybit fundingRate, interval 8h): SOURCED.
  // Thresholds OURS: under 0.001 % per 8h = about zero; 0.03 % or more (3x the 0.01 % interest baseline) = high.
  var FD = { zero: 0.00001, high: 0.0003, perYear: 1095 };
  function fundRead(r) {
    if (r === null || r === undefined || r === '' || !isFinite(+r)) return null;
    r = +r;
    return { pct8h: r * 100, annual: r * FD.perYear * 100, side: Math.abs(r) < FD.zero ? 'zero' : r > 0 ? 'longs' : 'shorts', high: Math.abs(r) >= FD.high };
  }
  function premium(mark, idx) {
    if (!isFinite(+mark) || !isFinite(+idx) || !+idx) return null;
    var pts = mark - idx; return { pts: pts, bps: pts / idx * 1e4 };
  }
  // Bybit tickers: a snapshot replaces, a delta carries only the fields that changed.
  function bybitTick(prev, msg) {
    var o = {}, k, d = msg.data || {};
    if (msg.type !== 'snapshot' && prev) for (k in prev) o[k] = prev[k];
    for (k in d) o[k] = d[k];
    return o;
  }

  // Fold bars into a longer timeframe on UTC boundaries (4h from 1h: Deribit has no 4h resolution). Rows [t, o, h, l, c, v].
  function foldBars(rows, ms) {
    var out = [], cur = null;
    rows.forEach(function (r) {
      var b = Math.floor(+r[0] / ms) * ms;
      if (!cur || cur[0] !== b) { cur = [b, +r[1], +r[2], +r[3], +r[4], +r[5]]; out.push(cur); }
      else { cur[2] = Math.max(cur[2], +r[2]); cur[3] = Math.min(cur[3], +r[3]); cur[4] = +r[4]; cur[5] += +r[5]; }
    });
    return out;
  }

  // News (research/news_feeds_2026-10-30). Tree News `importance` 0-10: SOURCED. Mark at 7, 60 min window, EVENT at 3+: OURS
  // (normal day 5-9 items at 7 or more, hack day 2026-10-29 had 42; measured 10-26..10-30).
  var NW = { mark: 7, winMs: 3600000, event: 3 };
  var NT = [['hack', /\b(hack|hacked|hacker|hackers|exploit|exploited|drain|drained|stolen|theft|heist|breach)\b/i],
    ['halt', /\b(halts?|halted|suspends?|suspended|pauses?|paused)\b.*\b(withdrawals?|deposits?|trading)\b/i],
    ['etf', /\b(etfs?|sec)\b/i], ['fed', /\b(fed|fomc|powell|cpi|pce|nfp|payrolls?|rate (cut|hike)s?|inflation)\b/i],
    ['war', /\b(war|missiles?|sanctions?|tariffs?|invasion)\b/i], ['delist', /\b(delist|delists|delisting|delisted)\b/i],
    ['btc', /\b(bitcoin|btc)\b/i]];
  function newsTags(title) {
    var t = String(title || ''), out = [];
    NT.forEach(function (c) { if (c[1].test(t)) out.push(c[0]); });
    return out;
  }
  function newsMerge(list, incoming, max) {
    var seen = {}, out = [];
    (incoming || []).concat(list || []).forEach(function (x) { if (x && x._id && !seen[x._id]) { seen[x._id] = 1; out.push(x); } });
    out.sort(function (a, b) { return b.time - a.time; });
    return out.slice(0, max);
  }
  function newsPulse(items, now) {
    var hi = (items || []).filter(function (x) { return +x.importance >= NW.mark && x.time <= now && x.time > now - NW.winMs; });
    return { n: hi.length, level: hi.length >= NW.event ? 'EVENT' : hi.length ? 'BUSY' : 'QUIET', top: hi.sort(function (a, b) { return b.importance - a.importance; })[0] || null };
  }

  var api = { NW: NW, newsTags: newsTags, newsMerge: newsMerge, newsPulse: newsPulse, foldBars: foldBars, FD: FD, fundRead: fundRead, premium: premium, bybitTick: bybitTick, LQ: LQ, liqDeribit: liqDeribit, liqBybit: liqBybit, liqBinance: liqBinance, liqSum: liqSum, CP: CP, coilPierce: coilPierce, IT: IT, divergence: divergence, flow: flow, flowLive: flowLive, squeeze: squeeze, dom: dom, supports: supports, vwapTest: vwapTest,
    flagDiv: flagDiv, flagSqueeze: flagSqueeze, flagFlow: flagFlow, flagDom: flagDom, flagVwap: flagVwap, confidence: confidence, rma: rma, sma: sma, rsi: rsi, bollinger: bollinger, atr: atr, dayVwap: dayVwap, utcDays: utcDays, wavetrend: wavetrend,
    inversePnlBtc: inversePnlBtc, closedPnlBtc: closedPnlBtc, columns: columns };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LiveAid = api;
})(typeof self !== 'undefined' ? self : this);
