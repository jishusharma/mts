// node tests for block selection: node scripts/aibridge/tests/block_select.test.js
// D1/D2/D7: thinking-panel drafts never run, repeated identical commands are keyed per occurrence, a duplicate inside one reply is NOT RUN.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const L = require('../extension/loop.js');
let n = 0;
function t(name, fn) { fn(); n++; console.log('PASS ' + name); }

const think = [{ tag: 'div', cls: 'chat-message' }, { tag: 'div', cls: 'ds-think-content' }];
const answer = [{ tag: 'div', cls: 'chat-message' }, { tag: 'div', cls: 'ds-markdown' }];
const d = (cmd, chain) => ({ cmd: cmd, chain: chain });

t('2 thinking drafts + 6 final blocks -> the 6 final blocks, once each', () => {
  const descs = [d('c1', think), d('c2', think)];
  for (let i = 1; i <= 6; i++) descs.push(d('c' + i, answer));
  const r = L.selectBlocks(descs);
  assert.deepStrictEqual(r.selected, [2, 3, 4, 5, 6, 7]);
  assert.deepStrictEqual(r.ignored, [0, 1]);
  assert.ok(/thinking/.test(r.status));
  const keys = L.batchKeys(r.selected.map(i => descs[i].cmd));
  assert.strictEqual(new Set(keys).size, 6);
});
t('key is stable when the thinking panel collapses (drafts leave the page)', () => {
  const withDrafts = [d('c1', think), d('c2', think), d('c1', answer), d('c2', answer)];
  const sel = L.selectBlocks(withDrafts).selected.map(i => withDrafts[i].cmd);
  const after = L.batchKeys(sel);
  const collapsed = L.batchKeys(['c1', 'c2']);
  assert.deepStrictEqual(after, collapsed);
});
t('same command twice keeps two different keys (per occurrence), a later reply gets a fresh one', () => {
  const k = L.batchKeys(['x', 'x', 'y', 'x']);
  assert.strictEqual(new Set(k).size, 4);
  assert.deepStrictEqual(L.batchKeys(['x', 'x']), k.slice(0, 2));
});
t('duplicate inside one reply -> second points at the first (NOT_RUN duplicate of block K)', () => {
  assert.deepStrictEqual(L.dupOf(['a', 'b', 'a', 'a\r\n']), [0, 0, 1, 1]);
  assert.deepStrictEqual(L.dupOf(['a', 'b']), [0, 0]);
});
t('thinking by tag / role / summary text, not by block text', () => {
  assert.strictEqual(L.isThinking([{ tag: 'thought' }]), true);
  assert.strictEqual(L.isThinking([{ tag: 'details' }]), true);
  assert.strictEqual(L.isThinking([{ tag: 'div', cls: 'x', lead: 'Thought for 5 seconds' }]), true);
  assert.strictEqual(L.isThinking([{ tag: 'div', cls: 'reasoning-box' }]), true);
  assert.strictEqual(L.isThinking(answer), false);
  // a block whose own text mentions thinking is still runnable
  assert.strictEqual(L.isThinking([{ tag: 'div', cls: 'md', lead: 'AIRUN thinking about it' }]), false);
});
t('fail closed: a block whose container cannot be described is not selected', () => {
  const r = L.selectBlocks([d('c1', null), d('c2', []), d('c3', answer)]);
  assert.deepStrictEqual(r.selected, [2]);
  assert.strictEqual(L.selectBlocks([]).selected.length, 0);
  assert.strictEqual(L.selectBlocks(undefined).selected.length, 0);
});
t('fixture deepseek_reply.html: class names in the fixture are recognised', () => {
  const html = fs.readFileSync(path.join(__dirname, 'fixtures', 'deepseek_reply.html'), 'utf8');
  assert.ok(/HAND-BUILT/.test(html));
  const cls = (html.match(/class="([^"]+)"/g) || []).map(s => s.slice(7, -1));
  assert.ok(cls.indexOf('ds-think-content') >= 0 && L.isThinking([{ tag: 'div', cls: 'ds-think-content' }]));
  assert.ok(cls.indexOf('ds-markdown') >= 0 && !L.isThinking([{ tag: 'div', cls: 'ds-markdown' }]));
});

console.log(n + ' tests passed');
