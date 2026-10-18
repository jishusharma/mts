// node tests for the hands-free checkbox: node tests/handsfree.test.js
// The chat input is checked after every post. DeepSeek can replace the input node after a send; a post that landed must
// not be reported as failed, because a failed post switches hands-free off (content.js runBatch -> stopAuto).
const assert = require('assert');
const L = require('../extension/loop.js');
let n = 0;
function t(name, fn) { fn(); n++; console.log('PASS ' + name); }

// an input as postLanded sees it: the node it was typed into, whether that node is still in the page, and its text
const node = (id, text, attached) => ({ id: id, text: text, attached: attached !== false });
const sentFrom = (el) => (el ? { node: el.id, attached: el.attached, text: el.text } : null);
const nowFrom = (el) => (el ? { node: el.id, text: el.text } : null);

t('postLanded: same input node is cleared after Enter -> landed', () => {
  assert.strictEqual(L.postLanded(sentFrom(node('a', '')), nowFrom(node('a', ''))), true);
});
t('postLanded: same input node still holds the message -> not landed (a real failure)', () => {
  assert.strictEqual(L.postLanded(sentFrom(node('a', 'msg')), nowFrom(node('a', 'msg'))), false);
});
t('postLanded: chat replaced the input node and the new one is empty -> landed', () => {
  // the old node is detached and still holds the text we typed; the send itself succeeded
  assert.strictEqual(L.postLanded(sentFrom(node('a', 'msg', false)), nowFrom(node('b', ''))), true);
});
t('postLanded: no input in the page -> not landed', () => {
  assert.strictEqual(L.postLanded(sentFrom(node('a', 'msg')), null), false);
});

// stubbed state machine of runBatch's post step over a chain: each block runs, then its result is posted
function runChain(blockCount, postReplacesInput, cap) {
  const state = { autoRun: true, runs: 0 };
  let input = node('in1', '');
  for (let i = 0; i < blockCount; i++) {
    if (state.runs >= cap) { state.autoRun = false; break; }
    state.runs++;
    const typedInto = input;
    typedInto.text = 'result #' + (i + 1);          // the result we typed into the input
    if (postReplacesInput) {
      typedInto.attached = false;                   // the chat re-rendered the input: the node we typed into is gone
      input = node('in' + (i + 2), '');
    } else {
      typedInto.text = '';                          // the chat cleared the same node
    }
    if (!L.postLanded(sentFrom(typedInto), nowFrom(input))) { state.autoRun = false; break; }
  }
  if (state.autoRun) state.runs = 0;   // chain ended here: the counter resets, the box stays armed
  return state;
}

t('chain of several blocks, input node replaced after every post: checkbox stays checked', () => {
  const s = runChain(4, true, 50);
  assert.strictEqual(s.autoRun, true);
  assert.strictEqual(s.runs, 0);
});
t('chain of several blocks, input node kept: checkbox stays checked', () => {
  assert.strictEqual(runChain(4, false, 50).autoRun, true);
});
t('a post that really failed still switches hands-free off', () => {
  // same node, message still in it: the send did not go through
  assert.strictEqual(L.postLanded(sentFrom(node('a', 'msg')), nowFrom(node('a', 'msg'))), false);
});

console.log(n + ' tests passed');
