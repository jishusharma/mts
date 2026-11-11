// Replay of the Live Aid Home logic (pulse.js, levelstory.js, indread.js, home.js model) over past candles.
// The page keeps no log of its flags, so this rebuilds them: one step every 5 min, closed bars only (no forming bar).
// Levels are rebuilt here (prior day H/L, 2-day low/high, prior week H/L, day open, completed Asia / Europe H/L):
// the page also merges analyst and MA levels, which are not replayable. Votes: VWAP, RSI 1h, RSI 4h only (3 of 6).
'use strict';
const fs = require('fs'), path = require('path');
const LA = path.join(__dirname, '..', '..', 'tools', 'live_aid');
const A = require(path.join(LA, 'live_aid_indicators.js')), PU = require(path.join(LA, 'pulse.js')), LS = require(path.join(LA, 'levelstory.js')), IND = require(path.join(LA, 'indread.js'));
const K = {}; ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1d'].forEach(tf => K[tf] = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', tf + '.json'))));
function END0() { return +K['1m'][K['1m'].length - 1][6]; }
const DAY = 86400000, H = 3600000, f = t => new Date(t).toISOString().slice(5, 16).replace('T', ' ');
const START = END0() - (+process.argv[2] || 2) * DAY - (END0() % DAY), END = +K['1m'][K['1m'].length - 1][6];
const hl = rows => rows.length ? { h: Math.max(...rows.map(r => +r[2])), l: Math.min(...rows.map(r => +r[3])) } : null;
function levels(t) {
  const d0 = Math.floor(t / DAY) * DAY, m = K['15m'], rng = (a, b) => hl(m.filter(r => +r[0] >= a && +r[6] < b)), out = [];
  const add = (p, name) => { if (p > 0) out.push({ price: p, lo: p, hi: p, name: name, n: 1 }); };
  const pd = rng(d0 - DAY, d0), p2 = rng(d0 - 2 * DAY, d0 - DAY);
  if (pd) { add(pd.h, 'Yesterday high'); add(pd.l, 'Yesterday low'); }
  if (p2) { add(p2.h, '2-day-ago high'); add(p2.l, '2-day-ago low'); }
  const dow = (new Date(d0).getUTCDay() + 6) % 7, w0 = d0 - dow * DAY, pw = hl(K['4h'].filter(r => +r[0] >= w0 - 7 * DAY && +r[0] < w0));
  if (pw) { add(pw.h, 'Last week high'); add(pw.l, 'Last week low'); }
  const o = m.find(r => +r[0] === d0); if (o) add(+o[1], 'Day open');
  if (t >= d0 + 8 * H) { const a = rng(d0, d0 + 8 * H); if (a) { add(a.h, 'Asia high'); add(a.l, 'Asia low'); } }
  if (t >= d0 + 13 * H) { const e = rng(d0 + 7 * H, d0 + 13 * H); if (e) { add(e.h, 'Europe high'); add(e.l, 'Europe low'); } }
  return out;
}
function ladder(z, px) { const up = z.filter(x => x.price > px * 1.0002).sort((a, b) => a.price - b.price), dn = z.filter(x => x.price < px * 0.9998).sort((a, b) => b.price - a.price), at = z.find(x => Math.abs(x.price / px - 1) <= 0.0002) || null; return { above: up, below: dn, at: at }; }
const I1 = new Map(K['1m'].map((r, i) => [+r[0], i]));
function day1m(d0, t) { const i = I1.get(d0); if (i == null) return []; const o = []; for (let j = i; j < K['1m'].length && +K['1m'][j][6] < t; j++) o.push(K['1m'][j]); return o; }
const out = [];
for (let t = START; t <= END; t += 300000) {
  const TFK = {}; Object.keys(K).forEach(tf => { if (tf === '1d') return; const a = K[tf]; let lo = 0, hi = a.length; while (lo < hi) { const m = (lo + hi) >> 1; if (+a[m][6] < t) lo = m + 1; else hi = m; } TFK[tf] = a.slice(Math.max(0, lo - (tf === '1m' ? 1000 : 300)), lo); });
  const m1 = TFK['1m']; if (m1.length < 300) continue;
  const px = +m1[m1.length - 1][4], d0 = Math.floor(t / DAY) * DAY;
  let pv = 0, vv = 0; day1m(d0, t).forEach(r => { pv += (+r[2] + +r[3] + +r[4]) / 3 * +r[5]; vv += +r[5]; });
  const vwap = vv ? pv / vv : NaN, rsiOf = tf => { const c = TFK[tf].map(r => +r[4]); return A.rsi(c, 14)[c.length - 1]; };
  const votes = [isFinite(vwap) ? Math.sign(px - vwap) : null, Math.sign(rsiOf('1h') - 50), Math.sign(rsiOf('4h') - 50)];
  const bull = votes.filter(x => x === 1).length, bear = votes.filter(x => x === -1).length, dir = bull >= 2 && bull >= 2 * bear ? 'LONG' : bear >= 2 && bear >= 2 * bull ? 'SHORT' : 'WAIT';
  const g = PU.grid(TFK, t), lad = ladder(levels(t), px), lanes = {}; ['1m', '2m', '3m', '15m', '30m', '4h'].forEach(tf => { try { lanes[tf] = PU.lane(TFK, tf, 60, t); } catch (e) { lanes[tf] = null; } });
  const su = PU.setup(g, lad, px, dir);
  const near = [lad.at, lad.above[0], lad.below[0]].filter(z => z && Math.abs(px / z.price - 1) <= PU.P.near).sort((a, b) => Math.abs(px - a.price) - Math.abs(px - b.price))[0] || null;
  const tm = PU.timing(lanes, near);
  const lv = []; if (lad.at) lv.push(lad.at); if (lad.above[0]) lv.push(lad.above[0]); if (lad.below[0] && lv.length < 2) lv.push(lad.below[0]);
  const st = lv.map(z => { try { return LS.story(z, TFK['15m'], t, { wt15: lanes['15m'] }); } catch (e) { return null; } }).filter(Boolean);
  const ideas = st.filter(s => s.idea), mixed = ideas.some(s => s.idea !== ideas[0].idea);
  const ind = IND.table(TFK, t), c15 = ind.r['15m'], c1h = ind.r['1h'];
  out.push({ t: t, px: px, dir: dir, gdir: g.dir, lean: +g.lean.toFixed(2), hi: +g.hi.toFixed(2),
    setup: su ? { side: su.side, name: su.name, level: su.level } : null,
    timing: tm.state === 'ALIGNED' ? { side: tm.side > 0 ? 'LONG' : 'SHORT', tf: tm.trig.tf } : null, tmN: tm.trig ? tm.n : 0, tmSide: tm.side,
    idea: ideas.length && !mixed ? { side: ideas[0].idea, name: ideas[0].name, level: ideas[0].price, state: ideas[0].state, voidAt: ideas[0].voidAt } : null, mixed: mixed,
    st: st.map(s => s.name + ':' + s.state + (s.idea ? ':' + s.idea : '')),
    adx15: c15 ? Math.round(c15.cells.adx.adx) * (c15.cells.adx.side || 1) : null, adx1h: c1h ? Math.round(c1h.cells.adx.adx) * (c1h.cells.adx.side || 1) : null,
    vfi15: c15 && c15.cells.vfi.v, sqz15: c15 ? (c15.cells.sqz.on ? 'COIL' : c15.cells.sqz.v) : null, wt30: lanes['30m'] ? lanes['30m'].side : null, wt15: lanes['15m'] ? lanes['15m'].side : null, says: ind.says.map(s => s.cls + '|' + s.t), indUp: c15 ? c15.up : null, indDn: c15 ? c15.dn : null });
}
fs.writeFileSync(path.join(__dirname, 'data', 'steps.json'), JSON.stringify(out));
// events: a flag when it first appears (a new run), scored on 1m closes after it
const m1 = K['1m'], fwd = (t, side, mins) => { const s = side === 'LONG' ? 1 : -1, i0 = I1.get(t), a = i0 == null ? [] : m1.slice(i0, i0 + mins); if (!a.length) return null; const p0 = +a[0][1];
  return { end: s * (+a[a.length - 1][4] / p0 - 1) * 100, mfe: Math.max(...a.map(r => s * ((s > 0 ? +r[2] : +r[3]) / p0 - 1))) * 100, mae: Math.min(...a.map(r => s * ((s > 0 ? +r[3] : +r[2]) / p0 - 1))) * 100, full: a.length >= mins - 1 }; };
const ev = []; let last = {};
out.forEach(s => { [['idea', s.idea], ['setup', s.setup], ['timing', s.timing]].forEach(([k, v]) => {
  const key = v ? v.side + (v.name || v.tf) : null; if (key && key !== last[k]) { const a = fwd(s.t, v.side, 60), b = fwd(s.t, v.side, 240);
    ev.push({ t: f(s.t), kind: k, side: v.side, at: v.name || v.tf, px: Math.round(s.px), state: v.state || '', home: s.dir, grid: s.gdir, adx15: s.adx15, adx1h: s.adx1h, vfi15: s.vfi15, wt30: s.wt30, wt15: s.wt15, hi: s.hi, ts: s.t, r1h: a && +a.end.toFixed(2), mfe1h: a && +a.mfe.toFixed(2), mae1h: a && +a.mae.toFixed(2), r4h: b && b.full ? +b.end.toFixed(2) : null }); }
  last[k] = key; }); });
fs.writeFileSync(path.join(__dirname, 'events.json'), JSON.stringify(ev, null, 1));
console.log('steps', out.length, 'events', ev.length);
if (process.argv[3]) ev.forEach(e => console.log([e.t, e.kind, e.side, e.at, e.px, e.state, 'home=' + e.home, 'grid=' + e.grid, 'r1h=' + e.r1h, 'mfe=' + e.mfe1h, 'mae=' + e.mae1h, 'r4h=' + e.r4h].join(' | ')));
