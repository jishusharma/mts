// Re-run of the Live Aid replay (research/live_aid_review_2026-11-11/replay.js) for the idea flag only, over a long 5m series.
// Usage: node replay_events.js <in 5m json [[t,o,h,l,c,vol,takerBuy],...]> <out events json>
// The Live Aid code (levelstory.js, pulse.js lane, live_aid_indicators.js) is required UNCHANGED. levels(), ladder(), the idea selection and the
// "event = run key (side+name) changes" rule are copied from replay.js. Differences, all stated in PRE_REG.md: 15m rows are folded from 5m,
// week high/low come from 15m bars (same values as 4h bars), and only the idea flag is produced (no setup/timing, no RSI/VWAP votes).
'use strict';
const fs = require('fs'), path = require('path');
const LA = path.join(__dirname, '..', '..', 'tools', 'live_aid');
const PU = require(path.join(LA, 'pulse.js')), LS = require(path.join(LA, 'levelstory.js'));
const DAY = 86400000, H = 3600000, M5 = 300000, M15 = 900000;
const raw = JSON.parse(fs.readFileSync(process.argv[2]));
// dedupe + sort 5m
raw.sort((a, b) => a[0] - b[0]);
const b5 = []; raw.forEach(r => { if (!b5.length || b5[b5.length - 1][0] !== r[0]) b5.push(r); });
const i5 = new Map(b5.map((r, i) => [r[0], i]));
// fold complete 15m rows (Binance layout: 0 open time, 1-4 OHLC, 5 vol, 6 close time, 9 taker buy)
const k15 = [];
for (const r of b5) {
  const b = Math.floor(r[0] / M15) * M15; if (r[0] !== b) continue;
  const a = i5.get(b + M5), c = i5.get(b + 2 * M5); if (a == null || c == null) continue;
  const x = b5[a], y = b5[c], s = [r, x, y];
  k15.push([b, +r[1], Math.max(+r[2], +x[2], +y[2]), Math.min(+r[3], +x[3], +y[3]), +y[4], +r[5] + +x[5] + +y[5], b + M15 - 1, 0, 0, +r[6] + +x[6] + +y[6]]);
}
const byDay = new Map(); k15.forEach(r => { const d = Math.floor(r[0] / DAY) * DAY; if (!byDay.has(d)) byDay.set(d, []); byDay.get(d).push(r); });
const hl = rows => rows.length ? { h: Math.max(...rows.map(r => +r[2])), l: Math.min(...rows.map(r => +r[3])) } : null;
const rngDay = (d, a, b) => hl((byDay.get(d) || []).filter(r => +r[0] >= a && +r[6] < b));
const dayCache = new Map();
function dayBase(d0) {
  if (dayCache.has(d0)) return dayCache.get(d0);
  const out = { base: [], asia: null, eu: null };
  const add = (p, name) => { if (p > 0) out.base.push({ price: p, lo: p, hi: p, name: name, n: 1 }); };
  const pd = rngDay(d0 - DAY, d0 - DAY, d0), p2 = rngDay(d0 - 2 * DAY, d0 - 2 * DAY, d0 - DAY);
  if (pd) { add(pd.h, 'Yesterday high'); add(pd.l, 'Yesterday low'); }
  if (p2) { add(p2.h, '2-day-ago high'); add(p2.l, '2-day-ago low'); }
  const dow = (new Date(d0).getUTCDay() + 6) % 7, w0 = d0 - dow * DAY; let rows = [];
  for (let d = w0 - 7 * DAY; d < w0; d += DAY) rows = rows.concat(byDay.get(d) || []);
  const pw = hl(rows); if (pw) { add(pw.h, 'Last week high'); add(pw.l, 'Last week low'); }
  const o = (byDay.get(d0) || []).find(r => +r[0] === d0); if (o) add(+o[1], 'Day open');
  out.asia = rngDay(d0, d0, d0 + 8 * H); out.eu = rngDay(d0, d0 + 7 * H, d0 + 13 * H);
  dayCache.set(d0, out); return out;
}
function levels(t) {
  const d0 = Math.floor(t / DAY) * DAY, db = dayBase(d0), out = db.base.slice();
  const add = (p, name) => { if (p > 0) out.push({ price: p, lo: p, hi: p, name: name, n: 1 }); };
  if (t >= d0 + 8 * H && db.asia) { add(db.asia.h, 'Asia high'); add(db.asia.l, 'Asia low'); }
  if (t >= d0 + 13 * H && db.eu) { add(db.eu.h, 'Europe high'); add(db.eu.l, 'Europe low'); }
  return out;
}
function ladder(z, px) { const up = z.filter(x => x.price > px * 1.0002).sort((a, b) => a.price - b.price), dn = z.filter(x => x.price < px * 0.9998).sort((a, b) => b.price - a.price), at = z.find(x => Math.abs(x.price / px - 1) <= 0.0002) || null; return { above: up, below: dn, at: at }; }
// count of 15m rows closed before t: rows are sorted by open; closed iff open + 15m - 1 < t
function closedCount(t) { let lo = 0, hi = k15.length; while (lo < hi) { const m = (lo + hi) >> 1; if (k15[m][6] < t) lo = m + 1; else hi = m; } return lo; }
let laneKey = -1, laneVal = null;
function laneFor(lo, arr, t) { if (laneKey === lo) return laneVal; try { laneVal = PU.lane({ '15m': arr }, '15m', 60, t); } catch (e) { laneVal = null; } laneKey = lo; return laneVal; }
const ev = []; let last = null, steps = 0, nIdea = 0;
for (let i = 1; i < b5.length; i++) {
  const t = b5[i][0]; if (b5[i - 1][0] !== t - M5) continue;       // px = last closed 5m close needs the previous bar
  const lo = closedCount(t); if (lo < 300) continue;
  steps++;
  const arr = k15.slice(Math.max(0, lo - 300), lo), px = +b5[i - 1][4];
  const lad = ladder(levels(t), px);
  const lv = []; if (lad.at) lv.push(lad.at); if (lad.above[0]) lv.push(lad.above[0]); if (lad.below[0] && lv.length < 2) lv.push(lad.below[0]);
  // wt15 is only needed once a story is built; the lane depends on the closed 15m rows only (cached per closed-bar count)
  const st = lv.map(z => { try { return LS.story(z, arr, t, { wt15: laneFor(lo, arr, t) }); } catch (e) { return null; } }).filter(Boolean);
  const ideas = st.filter(s => s.idea), mixed = ideas.some(s => s.idea !== ideas[0].idea);
  const idea = ideas.length && !mixed ? { side: ideas[0].idea, name: ideas[0].name, level: ideas[0].price, state: ideas[0].state, voidAt: ideas[0].voidAt } : null;
  const key = idea ? idea.side + idea.name : null;
  if (idea) nIdea++;
  if (key && key !== last) ev.push({ ts: t, side: idea.side, at: idea.name, state: idea.state, level: idea.level, voidAt: idea.voidAt, px: px });
  last = key;
}
fs.writeFileSync(process.argv[3], JSON.stringify(ev));
console.log(JSON.stringify({ bars5: b5.length, bars15: k15.length, steps: steps, idea_steps: nIdea, events: ev.length, first: b5[0][0], last: b5[b5.length - 1][0] }));
