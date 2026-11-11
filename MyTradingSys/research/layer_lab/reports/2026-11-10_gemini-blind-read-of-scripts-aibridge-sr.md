# Blind Read Report: AIBridge DeepSeek Block Guard (0.7.33 / 0.7.34)

Card: `gemini-blind-read-of-scripts-aibridge-sr`  
Date (UTC): 2026-11-10  
Worker: gemini-3.8-flash-low  

## 1. Scope & Objective

Audit and blind-read the AIBridge DeepSeek block guard mechanisms across:
- `scripts/aibridge/src/lease.ps1`
- `scripts/aibridge/extension/loop.js` (`paceCheck`, `paceJitter`, `warnState`, `armGate`, `armRelease`, `leaseAccount`, `parseLeaseReply`)
- `scripts/aibridge/extension/content.js` (`paceGate`, `tryArm`, `guardTick`, `beatArm`, `onWarning`, `pageSnapshot`)
- Regression tests: `MyTradingSys/tests/test_aibridge_pacing.py`, `MyTradingSys/tests/test_aibridge_account_lease.py`, `scripts/aibridge/tests/handsfree.test.js`

Specifically look for ways the pacing, warning, account lease, or one-armed-chat rules can be:
1. **Bypassed or skipped** (allowing unintended auto runs / bursts to reach DeepSeek).
2. **False-trigger / lock out the operator wrongly** (preventing legitimate usage or causing persistent lockout).

---

## 2. Rule-by-Rule Analysis: What Each Rule Lets Through

### A. Pacing Guard (`loop.js:364-394`, `content.js:556-568`)
- **Constants (0.7.34)** [SOURCED: `scripts/aibridge/extension/loop.js:364`]:
  `minGapMs = 20000` (20 s), `perHour = 30`, `perDay = 200`, `jitterMinMs = 5000` (5 s), `jitterMaxMs = 15000` (15 s).
- **Enforcement (`paceGate`)**:
  - Before sending a message, `paceGate` fetches timestamps from `chrome.storage.local['aibridge_pace']`.
  - Filters to timestamps within 24 hours (`now - x < 86400000`).
  - Calls `L.paceCheck(hist, now, jit)`.
  - If `c.ok`, appends `now`, stores `hist.slice(-200)`, and proceeds.
  - If `c.cap === 'gap'` and `c.waitMs <= 120000`, waits and loops.
  - If `c.cap !== 'gap'` (i.e. 'hour' or 'day') OR `c.waitMs > 120000`, refuses post (`lastPostErr = L.paceText(c)`) and returns `false`.

### B. Warning Guard & Cooldown (`loop.js:398-427`, `content.js:495-505`, `515-517`, `534-545`)
- **Regex Detection Rules** [SOURCED: `scripts/aibridge/extension/loop.js:401-416`]:
  - `suspended`: matches `/suspended|violation of (the )?user policies|account (has been |is )?(banned|disabled|blocked|restricted)/i`.
  - `captcha`: matches text or `iframe[src*="captcha" i], ...` or `#captcha`.
  - `logout`: matches text, path (`/sign_in`, `/login`, etc.), or `input[type="password"]`.
  - `unusual`: matches `/unusual activity|suspicious activity|abnormal (activity|traffic|behavio)/i`.
  - `busy`: matches `/server is busy|servers are busy|rate limit|requests are too frequent/i`.
- **Target Elements** [SOURCED: `scripts/aibridge/extension/content.js:498`]:
  Inspects only overlays: `[role="dialog"]`, `[role="alertdialog"]`, `[role="alert"]`, `[aria-modal="true"]`, `[class*="modal" i]`, `[class*="toast" i]`, `[class*="dialog" i]`. Explicitly ignores `.aibridge-*` and chat messages.
- **Cooldown Effect** [SOURCED: `scripts/aibridge/extension/loop.js:418`, `content.js:542`]:
  Sets `aibridge_cooldown_until` to `now + 24 * 3600 * 1000` (24 hours). Refuses `tryArm()` while cooldown is active.

### C. Single Armed Tab Per Profile (`loop.js:429-439`, `content.js:518-519`, `547-550`)
- Registry in `chrome.storage.local['aibridge_armed']`: `{ [tabId]: timestamp }`.
- TTL = 90,000 ms (90 s) [SOURCED: `scripts/aibridge/extension/loop.js:431`].
- Any other tab with `now - timestamp <= 90000` blocks arming (`second_tab_refused`).
- Heartbeat `beatArm()` runs every 30 s while armed. If another tab arms or overtakes, `stopAuto()` triggers.

### D. Single Machine Per Account Lease (`lease.ps1`, `loop.js:441-449`, `content.js:520-522`, `551-552`)
- File `<lease_dir>/<sanitized_account>.json` holding `{account, host, ts}`.
- Default TTL = 180 s [SOURCED: `scripts/aibridge/src/lease.ps1:13`].
- If lease exists, is owned by another host, and `age < TtlS`, returns `ok = false, reason = 'account_in_use', holder = ...`.
- On release, only holder can remove the file.

---

## 3. Potential Bypass / Leakage Vulnerabilities

### Finding 1: Manual "Run" Button Bypasses All Guards (Pacing, Warning, Arming, and Lease)
- **File & Line**: [content.js:313-333](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L313-L333)
- **Mechanism**:
  When the operator clicks the "Run" button attached to an AIRUN block, `runManual()` executes `callWithRetry(cmd, opts, false, rid)` and then posts the result to chat via `postParts()` -> `postToChat()`.
  Crucially:
  1. `runManual` does not check `armedHere`, `armGate`, `warnState`, or `aibridge_cooldown_until`.
  2. In `postToChat()`, `paceGate(myToken)` is called, but `paceGate` only guards against rapid auto posts. If `c.cap !== 'gap' || c.waitMs > 120000`, `postToChat` returns `false`, but the agent command **has already executed**!
  3. Furthermore, multiple tabs across multiple machines can click "Run" simultaneously without acquiring `lease.ps1` or tab arming.
- **Replay Idea**:
  Open 5 tabs or 2 machines on the same DeepSeek account. Paste blocks in all of them and click "Run". All 5 execute against their respective agents and attempt to post back results, completely bypassing the single-machine and single-tab guards.

### Finding 2: Start DSA Bridge Seed Trigger Bypasses Pacing and Account Lease
- **File & Line**: [content.js:883-902](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L883-L902), [content.js:912-920](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L912-L920)
- **Mechanism**:
  Typing "Start DSA bridge" intercepts Enter/click and calls `startDsaBridge(inp)`. This sends the seed text directly to DeepSeek via `pressEnter` / `clickSend`. It does not call `paceGate()`, does not check `aibridge_cooldown_until`, does not verify `armGate`, and does not register in `PACE_KEY` history.
- **Replay Idea**:
  During a 24-hour warning cooldown, type "Start DSA bridge" and press Enter. The extension intercepts the message and posts the seed prompt anyway.

### Finding 3: Non-Atomic File Write in `lease.ps1` Permits Multi-Machine Race Window
- **File & Line**: [lease.ps1:4-5](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/src/lease.ps1#L4-L5), [lease.ps1:37-39](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/src/lease.ps1#L37-L39)
- **Mechanism**:
  `Invoke-AccountLease` checks `Test-Path` and `Get-Content`, then writes `[IO.File]::WriteAllText($f, $rec, ...)`. As documented in `lease.ps1:4-5`, this is explicitly non-atomic. Two machines issuing `acquire` concurrently within ~1 second will both read `$cur = $null` (or expired), and both return `ok = true; holder = $Me`.
  Until the next heartbeat (up to 30 s later via `guardTick`), both machines will run in auto mode concurrently.
- **Replay Idea**:
  Simulate two PowerShell processes invoking `Invoke-AccountLease -Action acquire` at the exact same sub-second timestamp against a shared network share `lease_dir`. Both return `ok = true`.

### Finding 4: Unconfigured Account Label Collapses Distinct Accounts to `deepseek-default`
- **File & Line**: [lease.ps1:19](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/src/lease.ps1#L19), [loop.js:442](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/loop.js#L442), [content.js:483](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L483)
- **Mechanism**:
  In `content.js:483`, `ACCT_KEY = 'aibridge_account'`. If `chrome.storage.local` does not explicitly define `aibridge_account`, `r[ACCT_KEY]` is undefined. `L.leaseAccount(undefined)` falls back to `'deepseek-default'`.
  If an operator uses two distinct browser profiles or two machines intended for different DeepSeek accounts without configuring `aibridge_account`, both claim `deepseek-default`. Machine B is locked out thinking Machine A is on the same account, OR if one gets a 24h block, the label collusion causes false lockout across machines.

---

## 4. Potential False-Trigger / Lockout Vulnerabilities

### Finding 5: Generic "Busy" Toast or Temporary Rate Limit Triggers Severe 24-Hour Cooldown
- **File & Line**: [loop.js:406](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/loop.js#L406), [loop.js:418](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/loop.js#L418), [content.js:536-544](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L536-L544)
- **Mechanism**:
  `loop.js:406` classifies any overlay containing `/server is busy|servers are busy|too many requests|rate limit|requests are too frequent|try again later/i` under `kind: 'busy'`.
  However, in `content.js:536-544`, `guardTick()` treats ANY warning returned by `L.warnState()` identically:
  ```javascript
  var w = L.warnState(pageSnapshot());
  if (w.warn) { onWarning(w); return; }
  ```
  `onWarning(w)` unconditionally sets:
  ```javascript
  var o = {}; o[COOL_KEY] = L.cooldownUntil(Date.now()); await sset(o);
  ```
  DeepSeek frequently displays transient toast notifications ("server is busy, please try again later") during high traffic periods. A temporary server blip causes a full **24-hour persistent lockout** on that browser profile. The operator cannot re-arm hands-free for 24 hours.
- **Replay Idea**:
  Inject a mock toast `<div class="toast">Server is busy. Please try again later.</div>`. Within 1 second, `guardTick()` fires, detects `busy`, invokes `onWarning()`, and locks hands-free for 24 hours (`aibridge_cooldown_until`).

### Finding 6: Tab Crash or Force-Close During Armed State Causes 90-Second Lockout
- **File & Line**: [loop.js:431-435](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/loop.js#L431-L435), [content.js:518-519](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L518-L519)
- **Mechanism**:
  When a tab is closed, refreshed, or killed, `releaseArm()` is not guaranteed to execute (`beforeunload` is not hooked to call `armRelease`). The registry in `chrome.storage.local['aibridge_armed']` retains the crashed tab's ID and timestamp.
  Any new tab or refreshed chat trying to re-arm within 90 seconds will be rejected with:
  `second_tab_refused: chat <holder> in this browser profile is already armed.`
  The operator is locked out until the 90-second TTL expires.
- **Replay Idea**:
  Check "Hands-free" on Tab 1. Kill Tab 1 (or press F5). Immediately try to check "Hands-free" on Tab 2 (or the refreshed tab). It is refused for up to 90 seconds.

### Finding 7: Agent Crash / Restart Leaves Dead Lease File for 180 Seconds
- **File & Line**: [lease.ps1:13](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/src/lease.ps1#L13), [lease.ps1:28-30](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/src/lease.ps1#L28-L30)
- **Mechanism**:
  If Machine A powers down, crashes, or switches network abruptly, the `<account>.json` lease file remains with timestamp `ts`.
  Machine B (or even Machine A after hostname change / reboot) attempting to acquire the lease is rejected with `account_in_use` until the 180 s TTL expires.

### Finding 8: Daily Post Cap Failure Stops Chain Completely Without Auto-Resume
- **File & Line**: [loop.js:378](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/loop.js#L378), [content.js:563](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L563), [content.js:669](file:///F:/MTS/gq/gemini-blind-read-of-scripts-aibridge-sr/scripts/aibridge/extension/content.js#L669)
- **Mechanism**:
  In `content.js:563`:
  ```javascript
  if (c.cap !== 'gap' || c.waitMs > 120000) {
    lastPostErr = L.paceText(c);
    auditEvent('post refused: ' + lastPostErr);
    return false;
  }
  ```
  When the 200 posts/day limit is hit, `waitMs` is the time until the oldest post in the 24h window expires (which can be several hours). Because `c.cap === 'day'`, `paceGate` immediately returns `false`.
  In `runBatch`, `postParts` fails, retry loop fails, and line 669 shuts down hands-free:
  `stopAuto('auto OFF: the result was not posted (' + lastPostErr + '). Tick the box again to re-arm.');`
  The result of the executed command is never posted to chat, DSA never receives it, and the entire chain stops dead.

---

## 5. Summary Table

| Category | Component / Guard | File:Line | Issue Description | Replay Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **Bypass** | Manual Run | `content.js:313-333` | Manual "Run" does not check warning, lease, or arm gates; executes command regardless of pacing limits. | Click "Run" while tab is unarmed, during cooldown, or from multiple machines. |
| **Bypass** | Seed Trigger | `content.js:883-902` | "Start DSA bridge" seed prompt skips pace, arm, lease, and cooldown checks. | Type "Start DSA bridge" and press Enter during active 24h cooldown. |
| **Bypass** | Lease Race | `lease.ps1:4-5, 37-39` | Non-atomic write allows two machines acquiring inside the same second to both succeed. | Concurrent acquisition by two hosts at identical second. |
| **Bypass** | Default Account | `lease.ps1:19`, `content.js:483` | Unset `aibridge_account` defaults to `deepseek-default`, merging unrelated profiles. | Multiple profiles without explicit storage keys share lease lock. |
| **False-Trigger** | Busy Toast Cooldown | `loop.js:406`, `content.js:536-544` | Transient "server is busy" notification triggers catastrophic 24-hour lockout. | DeepSeek displays standard peak-hour busy toast; extension initiates 24h cooldown. |
| **False-Trigger** | Tab Crash TTL | `loop.js:431-435`, `content.js:518-519` | Crash or hard reload leaves tab in armed registry for up to 90 seconds. | Kill armed tab and reload; immediate re-arm is refused. |
| **False-Trigger** | Agent Crash TTL | `lease.ps1:13, 28-30` | Machine abrupt stop leaves lease file active for 180 seconds. | Machine A crashes; Machine B locked out for 3 minutes. |
| **False-Trigger** | Cap Hard-Stop | `content.js:563, 669` | Reaching 200 posts/day permanently aborts result posting and disables hands-free. | 201st post of the day drops the command receipt and switches auto OFF. |

---

## 6. Verification & Test Status
- `node scripts/aibridge/tests/handsfree.test.js`: All 40 unit tests pass (20 handsfree + 20 guard/pacing/lease tests).
- `pytest MyTradingSys/tests/test_aibridge_pacing.py`: Passed (3/3 tests).
- `pytest MyTradingSys/tests/test_aibridge_account_lease.py`: Passed (6/6 tests).
- No code files modified (audit only).
