// node tests for the "Start DSA bridge" trigger: node tests/start_trigger.test.js
// The phrase typed as the whole message boots DSA. Anything longer is an ordinary message and must never be swapped for the seed.
const assert = require('assert');
const L = require('../extension/loop.js');
let n = 0;
function t(name, fn) { fn(); n++; console.log('PASS ' + name); }

t('exact phrase matches', () => { assert.strictEqual(L.isStartTrigger('Start DSA bridge'), true); });
t('case-insensitive', () => { assert.strictEqual(L.isStartTrigger('start dsa BRIDGE'), true); });
t('one trailing dot or bang is allowed', () => {
  assert.strictEqual(L.isStartTrigger('Start DSA bridge.'), true);
  assert.strictEqual(L.isStartTrigger('Start DSA bridge!'), true);
});
t('surrounding whitespace and a trailing newline are allowed', () => { assert.strictEqual(L.isStartTrigger('  Start DSA bridge \n'), true); });
t('a longer sentence does not match', () => {
  assert.strictEqual(L.isStartTrigger('Please Start DSA bridge now'), false);
  assert.strictEqual(L.isStartTrigger('Start DSA bridge and then list files'), false);
  assert.strictEqual(L.isStartTrigger('Start DSA bridges'), false);
});
t('a second message or second line does not match', () => {
  assert.strictEqual(L.isStartTrigger('Start DSA bridge\nthen do X'), false);
  assert.strictEqual(L.isStartTrigger('Start DSA bridge\nStart DSA bridge'), false);
  assert.strictEqual(L.isStartTrigger('Start DSA bridge..'), false);
  assert.strictEqual(L.isStartTrigger('Start DSA bridge!?'), false);
});
t('empty and non-string input do not match', () => {
  assert.strictEqual(L.isStartTrigger(''), false);
  assert.strictEqual(L.isStartTrigger(null), false);
  assert.strictEqual(L.isStartTrigger(undefined), false);
});
t('the panel line for a down agent is fixed text', () => {
  assert.strictEqual(L.SEED_DOWN_TEXT, 'agent down: run aibridge_install.py --restart-agent');
});
console.log(n + ' passed');
