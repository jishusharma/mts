MATCH: 5, DIFF: 0, NOT_IN_DATA: 0

# Blind Read Report: AIBridge 0.7.39 result cap and pagehide arm release (2411379b6)
- Date: 2026-11-11
- Task: gemini-blind-read-aibridge-0739-cap-pagehide-1111
- Auditor: Gemini (gemini-3.8-flash-low)
- Commit: `2411379b6ded36f2b14af7ecf2b7a48321ea354d`
- Scope In:
  - `scripts/aibridge/extension/loop.js` (L.capResult, L.VERSION; read)
  - `scripts/aibridge/extension/content.js` (aibridge_result_cap, pagehide listener, releaseArm; read)
  - `scripts/aibridge/tests/loop.test.js` (read)
  - `scripts/aibridge/RELEASES.json` and `scripts/aibridge/extension/manifest.json` (version; read)

## Clause Verification Table

| # | Clause Specification | Status | SOURCED File & Line | Quote / Implementation Evidence |
|---|---|---|---|---|
| 1 | capResult returns text unchanged at or under max | MATCH | `scripts/aibridge/extension/loop.js:86-88` | SOURCED `scripts/aibridge/extension/loop.js:86-88`: `L.capResult = function (text, max) { text = String(text == null ? '' : text); if (!max || text.length <= max) return text;` |
| 2 | Over max the output length is at most max plus the note and keeps a 70/30 head/tail split | MATCH | `scripts/aibridge/extension/loop.js:89-91` | SOURCED `scripts/aibridge/extension/loop.js:89`: `var keep = max - 200, head = Math.floor(keep * 0.7), tail = keep - head;`<br>SOURCED `scripts/aibridge/extension/loop.js:90-91`: `return text.slice(0, head) + '\n[RESULT CAPPED: ' + (text.length - head - tail) + ' of ' + text.length + ' chars cut from the middle; narrow the command (exclude *.jsonl, add \| head, grep -l, a path)]\n' + text.slice(text.length - tail);` |
| 3 | The note states chars cut and total | MATCH | `scripts/aibridge/extension/loop.js:90-91` | SOURCED `scripts/aibridge/extension/loop.js:90`: `'\n[RESULT CAPPED: ' + (text.length - head - tail) + ' of ' + text.length + ' chars cut from the middle; narrow the command (exclude *.jsonl, add \| head, grep -l, a path)]\n'` |
| 4 | Every result post path in content.js goes through capResult | MATCH | `scripts/aibridge/extension/content.js:10`, `scripts/aibridge/extension/content.js:309-310`, `scripts/aibridge/extension/content.js:344`, `scripts/aibridge/extension/content.js:704`, `scripts/aibridge/extension/content.js:710` | SOURCED `scripts/aibridge/extension/content.js:10`: `aibridge_result_cap: 60000,  // one result is cut to this, never posted as 5 parts of a 417 KB grep (live test 2026-11-10)`<br>SOURCED `scripts/aibridge/extension/content.js:309-310`: `async function postParts(text, n, myToken, label) { text = L.capResult(text, CFG.aibridge_result_cap);`<br>SOURCED `scripts/aibridge/extension/content.js:344`: manual run posts via `await postParts(text, n, myToken, '#' + n);`<br>SOURCED `scripts/aibridge/extension/content.js:704`: auto run batch posts via `await postParts(text, lastN, myToken, '#' + lastN);`<br>SOURCED `scripts/aibridge/extension/content.js:710`: retry posts via `ok = await postParts(text, lastN, myToken, '#' + lastN + ' (retry ' + (rt + 1) + ')');` |
| 5 | pagehide releases the arm only when this tab holds it; manifest, RELEASES.json and L.VERSION agree on 0.7.39 | MATCH | `scripts/aibridge/extension/content.js:609`, `scripts/aibridge/extension/loop.js:4`, `scripts/aibridge/extension/manifest.json:4`, `scripts/aibridge/RELEASES.json:2`, `scripts/aibridge/RELEASES.json:42` | SOURCED `scripts/aibridge/extension/content.js:609`: `window.addEventListener('pagehide', function () { if (armedHere) { armedHere = false; try { releaseArm(); } catch (e) {} } });`<br>SOURCED `scripts/aibridge/extension/loop.js:4`: `L.VERSION = '0.7.39';`<br>SOURCED `scripts/aibridge/extension/manifest.json:4`: `"version": "0.7.39",`<br>SOURCED `scripts/aibridge/RELEASES.json:2`: `"current": "0.7.39",`<br>SOURCED `scripts/aibridge/RELEASES.json:42`: `"0.7.39": "16581cff56bdb28b37ce16acfdce9086297f399a7b062dcbc85a746567755a33"` |

## Test Verification

- `scripts/aibridge/tests/loop.test.js:54-65`:
  - SOURCED `scripts/aibridge/tests/loop.test.js:54-60`:
    ```javascript
    t('capResult: short text unchanged, a 417 KB result is cut with a notice and keeps head and tail (0.7.39)', () => {
      assert.strictEqual(L.capResult('abc', 100), 'abc');
      const big = 'HEAD' + 'x'.repeat(417000) + 'TAIL';
      const c = L.capResult(big, 60000);
      assert.ok(c.length <= 60000 + 200 && c.startsWith('HEAD') && c.endsWith('TAIL') && c.includes('RESULT CAPPED'));
      assert.strictEqual(L.splitParts(c, 1, 60000).length, 1);
    });
    ```
  - SOURCED `scripts/aibridge/tests/loop.test.js:61-65`:
    ```javascript
    t('content.js releases the arm on pagehide (ghost arm after reload, 0.7.39)', () => {
      const src = require('fs').readFileSync(require('path').join(__dirname, '../extension/content.js'), 'utf8');
      assert.ok(src.split('\n').some(l => l.includes("addEventListener('pagehide'") && l.includes('armedHere = false') && l.includes('releaseArm()')));
      assert.ok(/L\.capResult\(text, CFG\.aibridge_result_cap\)/.test(src));
    });
    ```
  - Execution via `node scripts/aibridge/tests/loop.test.js`: All 29 tests passed cleanly.
