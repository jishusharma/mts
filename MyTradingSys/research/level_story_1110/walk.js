// Walks completed 15m bars, calls the LIVE levelstory.js story() unchanged (ex = {}), emits per-level-bar records.
const fs = require('fs'), path = require('path');
const LS = require(path.resolve(process.argv[2]));
const bars = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const evalFrom = +process.argv[4];
const DAY = 86400000;
const day = t => Math.floor(t / DAY);
const D = {};   // day -> {h,l,c, ah,al}
bars.forEach(r => {
  const d = day(+r[0]), o = D[d] || (D[d] = { h: -Infinity, l: Infinity, c: 0, ah: -Infinity, al: Infinity });
  o.h = Math.max(o.h, +r[2]); o.l = Math.min(o.l, +r[3]); o.c = +r[4];
  if (+r[0] - d * DAY < 8 * 3600000) { o.ah = Math.max(o.ah, +r[2]); o.al = Math.min(o.al, +r[3]); }
});
const out = [], WIN = 120;
for (let i = 0; i < bars.length; i++) {
  const t = +bars[i][0]; if (t < evalFrom) continue;
  const d = day(t), p = D[d - 1]; if (!p) continue;
  const close = +bars[i][4];
  const lvls = [{ name: 'prior day high', price: p.h }, { name: 'prior day low', price: p.l }, { name: 'prior day close', price: p.c }];
  if (t - d * DAY >= 8 * 3600000) lvls.push({ name: 'Asia high', price: D[d].ah }, { name: 'Asia low', price: D[d].al });
  const slice = bars.slice(Math.max(0, i - WIN + 1), i + 1), now = +bars[i][6] + 1;
  for (const lv of lvls) {
    const dist = Math.abs(close / lv.price - 1);
    if (dist > 0.003) { out.push({ i, lv: lv.name, near: false }); continue; }
    const s = LS.story({ name: lv.name, price: lv.price, n: 1 }, slice, now, {});
    if (!s) { out.push({ i, lv: lv.name, near: false }); continue; }
    out.push({ i, lv: lv.name, near: true, state: s.state, idea: s.idea, turn: s.turn, thru: s.thru, res: s.res, voidAt: s.voidAt, price: lv.price });
  }
}
process.stdout.write(JSON.stringify(out));
