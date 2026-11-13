// Renders the Home 5m chart + caption + WaveTrend row from SYNTHETIC bars (not market data) to fixture_home_chart.html, no browser needed.
const H = require('../../tools/live_aid/home.js'), fs = require('fs'), path = require('path');
const D0 = 1794528000000, NOW = D0 + 10 * 3600000 + 3 * 60000, rows = [];
for (let i = 0; i < 100; i++) { const t = D0 + 2 * 3600000 + i * 300000, c = 73700 + 120 * Math.sin(i / 9) + i; rows.push([t, c - 15, c + 40, c - 40, c, 1, 0, 0, 0, 0.6]); }
const zones = [[74000, 'Today high'], [73500, 'Yesterday low'], [73250, 'Yesterday busiest price'], [74300, 'Analyst call']].map(([price, name]) => ({ price, name, n: 1, items: [] }));
const md = { px: rows[rows.length - 1][4], zones, dir: 'WAIT', bull: 0, bear: 0, n: 0, lad: { above: [zones[0]], below: [zones[1]] } };
const lane = (s) => ({ side: s, zone: 'mid', wt1: 10, bars: [], last: { side: s, ago: 2, strong: true }, ms: 180000 });
const ctx = { now: NOW, rows5: rows, flagRows: [{ t: D0 + 8 * 3600000, kind: 'touch', side: 'UP', level: 'Yesterday low 73500', price: 73760, evidence: 'TOUCHING Yesterday low' }], flagStats: {}, lanes: { '1m': lane(1), '2m': lane(1), '3m': lane(1), '15m': lane(1), '30m': lane(-1), '4h': lane(1) } };
const css = 'body{background:#14171c;color:#d8dde3;font:13px sans-serif;--line:#232830;--fg:#d8dde3;--dim:#8a93a0;--up:#3fbf8a;--down:#e2665c;--amber:#e0a43a;--bg:#14171c}.up{color:var(--up)}.down{color:var(--down)}.dim{color:var(--dim)}';
const body = H.render ? '' : '';
const out = '<!doctype html><meta charset="utf-8"><style>' + css + '</style><p>SYNTHETIC fixture (not market data). Built by render_fixture.js</p>' + H._caption(ctx, md) + H._chart(ctx, md, 1000, 420) + H._wtSoWhat(ctx, md) + '<script>/*no script*/</script>';
const cssHome = fs.readFileSync(path.join(__dirname, '../../tools/live_aid/home.js'), 'utf8').match(/var CSS = ([\s\S]*?);\n  function injectCss/);
fs.writeFileSync(path.join(__dirname, 'fixture_home_chart.html'), out.replace('<style>', '<style>' + (cssHome ? eval(cssHome[1]) : '')));
console.log('ok');
