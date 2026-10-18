// node tests for the pure helpers in extension/loop.js:  node tests/loop.test.js
const assert = require('assert');
const L = require('../extension/loop.js');
let n = 0;
function t(name, fn) { fn(); n++; console.log('PASS ' + name); }

t('parseMarker: cwd timeout host shell', () => {
  const o = L.parseMarker('# AIRUN cwd="C:\\a b" timeout=120 host=NUC shell=pwsh\nx');
  assert.deepStrictEqual([o.cwd, o.timeout_s, o.host, o.shell], ['C:\\a b', 120, 'NUC', 'pwsh']);
  assert.strictEqual(o.task, undefined);
});
t('parseMarker: task and params, reserved keys stay out of params', () => {
  const o = L.parseMarker('# AIRUN task=mts-boot cwd=C:\\x timeout=300 hours=48 repo="C:\\p q"');
  assert.strictEqual(o.task, 'mts-boot');
  assert.deepStrictEqual(o.params, { hours: '48', repo: 'C:\\p q' });
  assert.strictEqual(o.timeout_s, 300);
});
t('blockText: keeps the version with more line breaks', () => {
  assert.strictEqual(L.blockText({ innerText: 'a\nb\nc', textContent: 'abc' }), 'a\nb\nc');
  assert.strictEqual(L.blockText({ innerText: 'abc', textContent: 'a\nb\nc' }), 'a\nb\nc');
  assert.strictEqual(L.blockText({ innerText: 'a\r\nb', textContent: 'a b' }), 'a\nb');
});
t('stripMarker leaves every command line', () => {
  assert.strictEqual(L.stripMarker('# AIRUN cwd=x\nl1\nl2\nl3'), 'l1\nl2\nl3');
});
t('cmdPreview: whole command, lines joined, not first line only', () => {
  assert.strictEqual(L.cmdPreview('a\nb\n\nc'), 'a ; b ; c');
  assert.ok(L.cmdPreview('x'.repeat(2000), 600).includes('[+1400 chars]'));
});
t('formatResult: ok result carries host, lines, sha, rid, block count', () => {
  const r = { ok: true, status: 200, body: { exit: 0, ms: 5, out: 'hi', host: 'JIS-NB', agent: '0.7.0', kind: 'read', cmd_lines: 3, cmd_sha: 'abc', rid: 'r1', at: 'T' } };
  const s = L.formatResult(7, 'a\nb\nc', r, '', { blocks_seen: 2, blocks_run: 2, index: 1, rid: 'r1' });
  assert.ok(s.includes('host=JIS-NB') && s.includes('lines=3') && s.includes('sha=abc') && s.includes('rid=r1'));
  assert.ok(s.includes('block=1/2 blocks_run=2') && s.includes('cmd: a ; b ; c') && s.includes('hi'));
});
t('formatResult: distinct labels for extension-off, agent-down, not-run', () => {
  assert.ok(L.formatResult(1, 'x', null).includes('extension_link'));
  assert.ok(L.formatResult(1, 'x', { ok: false, cls: 'agent_unreachable', error: 'Failed to fetch' }).includes('agent_unreachable'));
  assert.ok(L.formatResult(1, 'x', { ok: false, cls: 'NOT_RUN', error: 'NOT RUN: cap' }).includes('NOT RUN: cap'));
  const refused = L.formatResult(1, 'x', { ok: true, status: 403, body: { reason: 'manual_click_required: y', host: 'H' } });
  assert.ok(refused.includes('REFUSED http=403 reason=manual_click_required: y'));
});
t('checkEcho: stale reply and line mismatch are caught, task skips the line check', () => {
  assert.ok(L.checkEcho('r2', 'a\nb', { ok: true, body: { rid: 'r1', cmd_lines: 2 } }).startsWith('STALE_REPLY'));
  assert.ok(L.checkEcho('r1', 'a\nb\nc', { ok: true, body: { rid: 'r1', cmd_lines: 1 } }).startsWith('LINE_MISMATCH'));
  assert.strictEqual(L.checkEcho('r1', 'a\nb', { ok: true, body: { rid: 'r1', cmd_lines: 2 } }), null);
  assert.strictEqual(L.checkEcho('r1', '', { ok: true, body: { rid: 'r1', cmd_lines: 1 } }, true), null);
});
t('splitParts: short text unchanged, long text split with headers', () => {
  assert.deepStrictEqual(L.splitParts('abc', 1, 100), ['abc']);
  const p = L.splitParts(('line\n').repeat(2000), 3, 3000);
  assert.ok(p.length > 1 && p[0].startsWith('[AIRUN RESULT #3 part 1/'));
});
t('linkState: fresh port tick is ok', () => {
  const s = L.linkState(10000, { port: 9800, worker: 9900 });
  assert.strictEqual(s.state, 'ok'); assert.strictEqual(s.reconnect, false);
});
t('linkState: only worker ticking = degraded, reconnect port (service worker asleep)', () => {
  const s = L.linkState(10000, { port: 1000, worker: 9900 });
  assert.strictEqual(s.state, 'degraded'); assert.strictEqual(s.reconnect, true);
});
t('linkState: nothing ticks for 5 s = stale, never "ok" (hidden tab frozen / throttled)', () => {
  const s = L.linkState(60000, { port: 1000, worker: 2000 });
  assert.strictEqual(s.state, 'stale'); assert.strictEqual(s.reconnect, true);
  assert.strictEqual(L.linkState(60000, { port: 0, worker: 0 }).state, 'stale');
});
t('reconnectDelay: immediate first, then 1 2 4 8 15 s cap', () => {
  assert.deepStrictEqual([0, 1, 2, 3, 4, 5, 9].map(L.reconnectDelay), [0, 1000, 2000, 4000, 8000, 15000, 15000]);
});
t('linkLabel: visible status text names state, tab hidden, ages', () => {
  const l = L.linkLabel(L.linkState(10000, { port: 1000, worker: 9900 }), true);
  assert.ok(l.includes('degraded') && l.includes('tab hidden') && l.includes('worker 0.1s'));
});
console.log(n + ' passed');
