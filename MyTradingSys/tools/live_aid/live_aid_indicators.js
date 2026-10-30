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

  // ---------- analysts and verdict board (STEPS.md "Verdict rules"; all thresholds OURS) ----------
  var AV = { freshDays: 3, band: 6, at: 0.3, near: 1.5, merge: 0.25 };
  var BIAS = { BULLISH: 1, BEARISH: -1, NEUTRAL: 0 };
  function dayMs(d) { return Date.parse(String(d) + 'T00:00:00Z'); }
  // One line per roster analyst: newest valid row, rows/rejected counts, state FRESH / STALE / NO_ROW / NOT_FETCHED / OFF.
  function rosterRead(roster, rows, rejected, now) {
    return (roster || []).map(function (a) {
      var mine = (rows || []).filter(function (r) { return r.analyst === a.short; }).sort(function (x, y) { return x.published < y.published ? 1 : x.published > y.published ? -1 : 0; });
      var rej = (rejected || []).filter(function (r) { return r.analyst === a.short; }).length, last = mine[0] || null;
      var ageD = last ? Math.floor((now - dayMs(last.published)) / 86400000) : null;
      var state = !a.enabled ? 'OFF' : last ? (ageD <= AV.freshDays ? 'FRESH' : 'STALE') : a.ingested === false ? 'NOT_FETCHED' : 'NO_ROW';
      return { short: a.short, channel: a.channel || '', enabled: !!a.enabled, inRoster: a.in_roster !== false, rows: mine.length, rejected: rej,
               last: last ? last.published : '', bias: last ? last.bias : '', ageDays: ageD, state: state };
    });
  }
  // Analysts' vote: net of FRESH biases (BULLISH +1, BEARISH -1, NEUTRAL 0, NO_VIEW skipped); null when no fresh view.
  function analystVote(read) {
    var s = 0, n = 0;
    (read || []).forEach(function (a) { if (a.state === 'FRESH' && a.bias in BIAS) { s += BIAS[a.bias]; n++; } });
    return n ? Math.sign(s) : null;
  }
  // Levels within AV.band % of price, nearest first; zone AT (<= at %), NEAR (<= near %), WATCH. Expired levels dropped.
  function levelWatch(levels, px) {
    if (!(px > 0)) return [];
    return (levels || []).filter(function (x) { return !x.expired && isFinite(x.level); }).map(function (x) {
      var d = (x.level / px - 1) * 100, ad = Math.abs(d);
      return { level: x.level, analyst: x.analyst, published: x.published, said: x.said, bias: x.bias, hit: x.hit, dist: d,
               side: d >= 0 ? 'above' : 'below', zone: ad <= AV.at ? 'AT' : ad <= AV.near ? 'NEAR' : 'WATCH' };
    }).filter(function (x) { return Math.abs(x.dist) <= AV.band; }).sort(function (a, b) { return Math.abs(a.dist) - Math.abs(b.dist); });
  }
  // Levels less than AV.merge % above the previous one join its zone (lo..hi, every call in it); price inside a zone = side 'at'.
  function zones(watch, px) {
    var s = (watch || []).slice().sort(function (a, b) { return a.level - b.level; }), out = [];
    s.forEach(function (w) {
      var z = out[out.length - 1];
      if (z && (w.level / z.hi - 1) * 100 <= AV.merge) { z.hi = w.level; z.items.push(w); } else out.push({ lo: w.level, hi: w.level, items: [w] });
    });
    return out.map(function (z) {
      var inside = px >= z.lo && px <= z.hi, d = inside ? 0 : px < z.lo ? (z.lo / px - 1) * 100 : (z.hi / px - 1) * 100, ad = Math.abs(d);
      return { lo: z.lo, hi: z.hi, items: z.items, dist: d, side: inside ? 'at' : d > 0 ? 'above' : 'below', zone: ad <= AV.at ? 'AT' : ad <= AV.near ? 'NEAR' : 'WATCH' };
    }).sort(function (a, b) { return Math.abs(a.dist) - Math.abs(b.dist); });
  }
  // Lean from votes (+1 / -1 / 0; null = not in data): needs 3 available; BULLISH LEAN at 2+ bull and bull >= 2 x bear, mirror for bear.
  function lean(votes) {
    var v = (votes || []).filter(function (x) { return x === 1 || x === -1 || x === 0; });
    var bull = v.filter(function (x) { return x === 1; }).length, bear = v.filter(function (x) { return x === -1; }).length;
    var call = v.length < 3 ? 'NOT ENOUGH DATA' : bull >= 2 && bull >= 2 * bear ? 'BULLISH LEAN' : bear >= 2 && bear >= 2 * bull ? 'BEARISH LEAN' : 'MIXED';
    return { bull: bull, bear: bear, n: v.length, total: (votes || []).length, call: call };
  }
  // Watch list from zones: NOW (news EVENT, a zone within AT), NEXT (NEAR), LATER (WATCH). withLean = the zone lies in the lean's direction.
  function actions(ln, zs, pulse) {
    var out = [];
    if (pulse && pulse.level === 'EVENT') out.push({ when: 'NOW', kind: 'news', n: pulse.n });
    (zs || []).forEach(function (w) {
      out.push({ when: w.zone === 'AT' ? 'NOW' : w.zone === 'NEAR' ? 'NEXT' : 'LATER', kind: w.side === 'at' ? 'zone' : w.side === 'below' ? 'support' : 'resistance', w: w,
                 withLean: (ln && ln.call === 'BEARISH LEAN' && w.side === 'below') || (ln && ln.call === 'BULLISH LEAN' && w.side === 'above') });
    });
    var rank = { NOW: 0, NEXT: 1, LATER: 2 };
    return out.sort(function (a, b) { return rank[a.when] - rank[b.when]; });
  }


  // ---------- US open ladder (research/us_open_levels_2026-10-30; operator 2026-10-30 "anticipation ... if price goes up or down").
  // Levels known at the open: UTC-day-so-far H/L (box), prior day, prior 3 days, prior 7 days H/L, plus the first-15-min opening range.
  // rates = US_OPEN_RATES.rates: per level kind and distance bucket, reached-in-2h % and held-60-min-after-touch %. All OURS, descriptive. ----------
  var UO = { windowMs: 7200000, orMs: 900000, buckets: [['0-0.25', 0, 0.0025], ['0.25-0.5', 0.0025, 0.005], ['0.5-1', 0.005, 0.01], ['1-2', 0.01, 0.02], ['2+', 0.02, 9]],
             names: { dayH: 'day high so far', dayL: 'day low so far', pdh: 'prev day high', pdl: 'prev day low', d3h: '3-day high', d3l: '3-day low', d7h: '7-day high', d7l: '7-day low', orH: 'opening range high', orL: 'opening range low' } };
  function uoBucket(x) { for (var i = 0; i < UO.buckets.length; i++) if (x >= UO.buckets[i][1] && x < UO.buckets[i][2]) return UO.buckets[i][0]; return null; }
  // rows5m: 5m bars; daily: utcDays rows; open: the US open ms (last one if within 2 h, else the next); px: mark; rates: {kind: {bucket: {n, touch, nt, held}}}
  function usOpen(rows5m, daily, open, now, px, rates) {
    var phase = now < open ? 'before' : now - open <= UO.windowMs ? 'in' : 'after', d0 = Math.floor(open / DAY) * DAY;
    var box = { h: -Infinity, l: Infinity, n: 0 }, or = { h: -Infinity, l: Infinity, n: 0 };
    (rows5m || []).forEach(function (r) {
      var t = +r[0];
      if (t >= d0 && t < open) { box.n++; if (+r[2] > box.h) box.h = +r[2]; if (+r[3] < box.l) box.l = +r[3]; }
      if (t >= open && t < open + UO.orMs && t + 300000 <= now) { or.n++; if (+r[2] > or.h) or.h = +r[2]; if (+r[3] < or.l) or.l = +r[3]; }
    });
    var prior = (daily || []).filter(function (r) { return +r[0] < d0; }), np = prior.length, lv = [];
    function ext(n, hi) { var a = prior.slice(np - n); return hi ? Math.max.apply(null, a.map(function (r) { return +r[2]; })) : Math.min.apply(null, a.map(function (r) { return +r[3]; })); }
    if (box.n) { lv.push({ k: 'dayH', p: box.h }); lv.push({ k: 'dayL', p: box.l }); }
    if (np >= 1) { lv.push({ k: 'pdh', p: ext(1, true) }); lv.push({ k: 'pdl', p: ext(1, false) }); }
    if (np >= 3) { lv.push({ k: 'd3h', p: ext(3, true) }); lv.push({ k: 'd3l', p: ext(3, false) }); }
    if (np >= 7) { lv.push({ k: 'd7h', p: ext(7, true) }); lv.push({ k: 'd7l', p: ext(7, false) }); }
    if (or.n >= 3) { lv.push({ k: 'orH', p: or.h }); lv.push({ k: 'orL', p: or.l }); }
    var up = [], down = [];
    lv.forEach(function (x) {
      if (!isFinite(x.p) || !isFinite(px) || x.p === px) return;
      var dist = (x.p - px) / px, b = uoBucket(Math.abs(dist)), r = rates && rates[x.k] && b ? rates[x.k][b] : null;
      var row = { k: x.k, name: UO.names[x.k], p: x.p, dist: dist, bucket: b, touch: r && r.n >= 30 ? r.touch : null, held: r && r.nt >= 30 ? r.held : null, n: r ? r.n : 0, nt: r ? r.nt : 0 };
      (dist > 0 ? up : down).push(row);
    });
    up.sort(function (a, b) { return a.dist - b.dist; }); down.sort(function (a, b) { return b.dist - a.dist; });
    function merge(list) { // same price = one row, names joined
      var out = [];
      list.forEach(function (r) { var last = out[out.length - 1]; if (last && last.p === r.p) { last.name += ' = ' + r.name; if (last.touch === null) { last.touch = r.touch; last.held = r.held; last.n = r.n; last.nt = r.nt; } } else out.push(r); });
      return out;
    }
    return { phase: phase, open: open, minutes: Math.round((now - open) / 60000), box: box.n ? { h: box.h, l: box.l, bars: box.n } : null,
             or: or.n >= 3 ? { h: or.h, l: or.l, bars: or.n } : null, up: merge(up), down: merge(down), priorDays: np };
  }

  // "What the money is doing": price vs open interest (research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md).
  // All thresholds OURS, fixed in that spec before use. dp, doi are fractions; flat = under 0.1 % either way.
  var OM = { flat: 0.001, disagree: 0.002, flushPx: 0.0025, flushOi: 0.002, staleMs: 90000, slackMs: 60000, keepMs: 3900000,
             wins: [['5 min', 300000], ['15 min', 900000], ['60 min', 3600000]], barMs: 300000, eventMs: 3600000,
             pathBars: 8, pathOi: 0.002, chop: 0.008, trapOi: 0.002, cluster: 12 };
  var OS = {
    'up/up': 'Money entering on the long side: new longs are buying.',
    'down/up': 'Money entering on the short side: new shorts are selling.',
    'up/down': 'Money leaving: shorts are covering (a squeeze); the rise is not fed by new buyers.',
    'down/down': 'Money leaving: longs are closing or being liquidated (a flush).',
    'flat/up': 'Positions building without a move: both sides adding, pressure stored for the next break.',
    'flat/down': 'Positions closing quietly; interest is fading.',
    'up/flat': 'Price rising with positions about unchanged: the move is not fed by new money.',
    'down/flat': 'Price falling with positions about unchanged: the move is not fed by new money.',
    'flat/flat': 'Quiet: price and positions about unchanged.' };
  function omDir(x) { return x >= OM.flat ? 'up' : x <= -OM.flat ? 'down' : 'flat'; }
  function oiState(dp, doi) {
    if (!isFinite(dp) || !isFinite(doi)) return null;
    var k = omDir(dp) + '/' + omDir(doi);
    return { key: k, money: omDir(doi) === 'up' ? 'in' : omDir(doi) === 'down' ? 'out' : 'flat', text: OS[k] };
  }
  // h: one venue's samples [{t, px, oi}] oldest first (oi in the venue's own unit). Base = the newest sample at least ms old,
  // or the oldest one when it is within slackMs of that. A dead feed, a short history or a 0 value gives {err}, never a guess.
  function oiWindow(h, now, ms) {
    if (!h || !h.length) return { err: 'no samples' };
    var last = h[h.length - 1], base = null;
    if (now - last.t > OM.staleMs) return { err: 'feed stale, last sample ' + Math.round((now - last.t) / 1000) + ' s ago' };
    for (var i = h.length - 1; i >= 0; i--) if (h[i].t <= now - ms) { base = h[i]; break; }
    if (!base && h[0].t <= now - ms + OM.slackMs) base = h[0];
    if (!base) return { err: 'needs ' + Math.ceil((h[0].t - (now - ms + OM.slackMs)) / 60000) + ' min more of samples' };
    if (!(base.oi > 0) || !(last.oi > 0)) return { err: '0 OI value' };
    if (!(base.px > 0) || !(last.px > 0)) return { err: 'no price' };
    var dp = last.px / base.px - 1, doi = last.oi / base.oi - 1;
    return { dp: dp, doi: doi, spanMs: last.t - base.t, t: last.t, state: oiState(dp, doi) };
  }
  // vs: [{name, w (an oiWindow result), btc (open interest in BTC now)}]. Net = BTC-weighted mean of each venue's own change,
  // so a price move does not show up as a change in positions (OURS).
  function oiNet(vs) {
    var ok = vs.filter(function (v) { return v.w && !v.w.err && v.btc > 0; }), sw = 0, dp = 0, doi = 0;
    ok.forEach(function (v) { sw += v.btc; dp += v.btc * v.w.dp; doi += v.btc * v.w.doi; });
    if (!sw) return null;
    return { dp: dp / sw, doi: doi / sw, n: ok.length, of: vs.length, state: oiState(dp / sw, doi / sw) };
  }
  function oiDisagree(vs, netDoi) {
    var ok = vs.filter(function (v) { return v.w && !v.w.err; });
    var up = ok.filter(function (v) { return v.w.doi >= OM.disagree; }).map(function (v) { return v.name; });
    var dn = ok.filter(function (v) { return v.w.doi <= -OM.disagree; }).map(function (v) { return v.name; });
    if (!up.length || !dn.length) return null;
    var net = !isFinite(netDoi) || Math.abs(netDoi) < OM.flat ? 'net money about flat' : netDoi > 0 ? 'net money entering' : 'net money leaving';
    return up.join(' and ') + ' adding, ' + dn.join(' and ') + ' closing: positions moving between exchanges, ' + net + '.';
  }
  // 5m bars from klines [[t, o, h, l, c]] and OI snapshots {t: oi}. oi0 = OI at the bar open, oi1 = at its close (snapshot
  // stamped t + 5 min); a bar without its closing snapshot (the forming one) is left out.
  function oiBars(kl, ois) {
    return kl.map(function (k) { return { t: +k[0], o: +k[1], h: +k[2], l: +k[3], c: +k[4], oi0: ois[+k[0]], oi1: ois[+k[0] + OM.barMs] }; })
      .filter(function (b) { return b.oi0 > 0 && b.oi1 > 0; }).sort(function (a, b) { return a.t - b.t; });
  }
  // FLUSH: a 5m bar whose low is 0.25 % or more under the previous close while OI falls 0.2 % or more in the bar;
  // SQUEEZE: the mirror (high 0.25 % over, OI down 0.2 %). Price uses the wick: the 10-30 18:50Z flush closed -0.05 %.
  function oiEvents(bars) {
    var ev = [];
    bars.forEach(function (b, i) {
      var pc = i && bars[i - 1].t === b.t - OM.barMs ? bars[i - 1].c : b.o, doi = b.oi1 / b.oi0 - 1;
      if (doi > -OM.flushOi) return;
      var lo = b.l / pc - 1, hi = b.h / pc - 1, cl = b.c / pc - 1;
      if (lo <= -OM.flushPx) ev.push({ kind: 'FLUSH', i: i, t: b.t, px: b.l, move: lo, close: cl, doi: doi, d: b.oi1 - b.oi0, c: b.c, oi1: b.oi1 });
      else if (hi >= OM.flushPx) ev.push({ kind: 'SQUEEZE', i: i, t: b.t, px: b.h, move: hi, close: cl, doi: doi, d: b.oi1 - b.oi0, c: b.c, oi1: b.oi1 });
    });
    return ev;
  }
  // Only closed bars count. Same-kind events under 12 bars apart (C24's gap) are one event: the first bar anchors it, legs counts them.
  function oiLastEvent(bars, now) {
    var ev = oiEvents(bars.filter(function (b) { return b.t + OM.barMs <= now; })), cl = [];
    ev.forEach(function (e) {
      var c = cl[cl.length - 1];
      if (c && c.kind === e.kind && e.i - c.lastI < OM.cluster) { c.legs++; c.lastI = e.i; c.lastT = e.t; c.ext = e.kind === 'FLUSH' ? Math.min(c.ext, e.px) : Math.max(c.ext, e.px); }
      else cl.push(Object.assign({}, e, { legs: 1, lastI: e.i, lastT: e.t, ext: e.px }));
    });
    var e = cl[cl.length - 1];
    return e && now - (e.lastT + OM.barMs) <= OM.eventMs ? e : null;
  }
  // After an event: OI and price path from the event bar's close. C24 reads the OI change 40 min (8 bars) after the flush bar.
  function oiPath(bars, e, px, oi) {
    var after = bars.slice(e.i + 1), k = bars[e.i + OM.pathBars];
    var done = !!k && k.t === e.t + OM.pathBars * OM.barMs, oiAt = done ? k.oi1 : oi, pxAt = done ? k.c : px;
    var d = oiAt > 0 ? oiAt / e.oi1 - 1 : NaN;
    return { done: done, minsLeft: done ? 0 : Math.max(0, (OM.pathBars - after.length) * 5), doi: d,
             group: !isFinite(d) ? null : d >= OM.pathOi ? 'rebuilding' : d <= -OM.pathOi ? 'falling' : 'flat',
             chop: pxAt > 0 && Math.abs(pxAt / e.c - 1) <= OM.chop,
             hi: after.length ? Math.max.apply(null, after.map(function (b) { return b.h; })) : NaN,
             lo: after.length ? Math.min.apply(null, after.map(function (b) { return b.l; })) : NaN };
  }
  function oiTrap(e, path, px, oi) {
    var since = oi > 0 ? oi / e.oi1 - 1 : NaN;
    if (!(since >= OM.trapOi)) return null;
    if (e.kind === 'FLUSH' && px < path.hi) return { short: path.hi, long: e.px, text: 'shorts trapped above ' + Math.round(path.hi) + '; longs trapped below ' + Math.round(e.px) };
    if (e.kind === 'SQUEEZE' && px > path.lo) return { long: path.lo, short: e.px, text: 'longs trapped below ' + Math.round(path.lo) + '; shorts trapped above ' + Math.round(e.px) };
    return null;
  }
  function oiEventText(e, lq) {
    var hm = new Date(e.t).toISOString().slice(11, 16) + 'Z', who = e.kind === 'FLUSH' ? 'longs liquidated' : 'shorts squeezed';
    var usd = lq && (e.kind === 'FLUSH' ? lq.long : lq.short);
    return e.kind + ' ' + hm + ', ' + (e.kind === 'FLUSH' ? 'low ' : 'high ') + Math.round(e.px) + ', price ' + (e.move * 100).toFixed(2) + ' %, OI ' +
      (e.doi * 100).toFixed(2) + ' % (' + Math.round(e.d) + ' BTC), ' + who + (usd > 0 ? ' ' + (usd / 1e6).toFixed(1) + 'M seen by this page' : '') +
      (e.legs > 1 ? '; ' + e.legs + ' bars hit within 60 min, the last ' + new Date(e.lastT).toISOString().slice(11, 16) + 'Z, extreme ' + Math.round(e.ext) : '');
  }
  // MEASURED lines only (C24 row, BACKTEST_CANDIDATES.md; oi_after_flush.py, Bybit 5m 07-02..10-30). Anything else: not measured yet.
  var C24 = { study: 'C24, Bybit 5m 07-02..10-30', baseUp: 52, baseDrop: 6,
              rebuilding: { n: 18, up: 53 }, flat: { n: 9, up: 56 }, falling: { n: 22, up: 55, drop: 14 } };
  function oiExpect(e, path) {
    if (!e) return { measured: false, text: 'No flush or squeeze in the last 60 min. What follows a six-state read is not measured yet (C25, BACKTEST_CANDIDATES.md).' };
    if (e.kind === 'SQUEEZE') return { measured: false, text: 'What follows a squeeze is not measured yet (C26, BACKTEST_CANDIDATES.md).' };
    if (!path.done) return { measured: false, text: 'C24 reads the OI path 40 min after the flush, in ' + path.minsLeft + ' min; so far OI ' + (path.group || 'not in data') + '.' };
    if (!path.chop) return { measured: false, text: 'Price moved more than 0.8 % in the 40 min after the flush: outside the C24 sample, not measured.' };
    var g = C24[path.group], loose = e.close > -OM.flushPx ? ' C24 counted bars that closed -0.25 % or lower; this one closed ' + (e.close * 100).toFixed(2) + ' %, a loose match.' : '';
    var t = 'After a flush with OI ' + path.group + ' (n=' + g.n + '): up 4 h later ' + g.up + ' % vs ' + C24.baseUp + ' % base, no direction from OI alone.';
    if (path.group === 'falling') t += ' A 4 h drop over 1 %: ' + g.drop + ' % vs ' + C24.baseDrop + ' % base, a bigger move twice as likely, direction open.';
    return { measured: true, n: g.n, study: C24.study, text: t + loose };
  }

  var api = { OM: OM, oiState: oiState, oiWindow: oiWindow, oiNet: oiNet, oiDisagree: oiDisagree, oiBars: oiBars, oiEvents: oiEvents, oiLastEvent: oiLastEvent, oiPath: oiPath, oiTrap: oiTrap, oiEventText: oiEventText, C24: C24, oiExpect: oiExpect,
    AV: AV, rosterRead: rosterRead, analystVote: analystVote, levelWatch: levelWatch, zones: zones, lean: lean, actions: actions, NW: NW, newsTags: newsTags, newsMerge: newsMerge, newsPulse: newsPulse, foldBars: foldBars, FD: FD, fundRead: fundRead, premium: premium, bybitTick: bybitTick, LQ: LQ, liqDeribit: liqDeribit, liqBybit: liqBybit, liqBinance: liqBinance, liqSum: liqSum, CP: CP, coilPierce: coilPierce, IT: IT, divergence: divergence, flow: flow, flowLive: flowLive, squeeze: squeeze, dom: dom, supports: supports, vwapTest: vwapTest,
    flagDiv: flagDiv, flagSqueeze: flagSqueeze, flagFlow: flagFlow, flagDom: flagDom, flagVwap: flagVwap, confidence: confidence, rma: rma, sma: sma, rsi: rsi, bollinger: bollinger, atr: atr, dayVwap: dayVwap, utcDays: utcDays, wavetrend: wavetrend,
    inversePnlBtc: inversePnlBtc, closedPnlBtc: closedPnlBtc, columns: columns, UO: UO, usOpen: usOpen };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LiveAid = api;
})(typeof self !== 'undefined' ? self : this);
