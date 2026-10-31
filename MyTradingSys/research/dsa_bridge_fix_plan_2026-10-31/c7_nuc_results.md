# dsabr-c7 install + e2e on JIS-NUC (2026-10-31)

Host: JIS-NUC. Bridge: AIBridge 0.7.6 (RELEASES.json current).

## 1. aibridge_install.py F:/AIBridge --restart-agent

Exit 0.

```
agent started: 0.7.6 on JIS-NUC pid 44408
  src/agent.ps1
  src/checks.ps1
  src/concurrency.ps1
  src/audit.ps1
  extension/panel.css
  extension/content.js
  extension/loop.js
  extension/manifest.json
  extension/background.js
  scripts/start-agent.ps1
  scripts/run-task.ps1
  docs/V07_CONTRACT.md
  policy_patch.json
  RELEASES.json
  tests/loop.test.js
  tests/handsfree.test.js
  tests/agent_live_selftest.py
  tasks/build-check.json
  tasks/mts-boot.json
  tasks/mts-gate.json
  tasks/mts-ship.json
  src/policy.json (merged)
installed AIBridge v0.7.6 into F:/AIBridge
```

## 2. aibridge_verify.py F:/AIBridge

Exit 0. Result: `aibridge_verify: PASS (0 FAIL of 29)`.

```
PASS         installed                                                              F:/AIBridge
PASS         file:RELEASES.json                                                     identical to payload
PASS         file:docs/V07_CONTRACT.md                                              identical to payload
PASS         file:extension/background.js                                           identical to payload
PASS         file:extension/content.js                                              identical to payload
PASS         file:extension/loop.js                                                 identical to payload
PASS         file:extension/manifest.json                                           identical to payload
PASS         file:extension/panel.css                                               identical to payload
PASS         file:scripts/run-task.ps1                                              identical to payload
PASS         file:scripts/start-agent.ps1                                           identical to payload
PASS         file:src/agent.ps1                                                     identical to payload
PASS         file:src/audit.ps1                                                     identical to payload
PASS         file:src/checks.ps1                                                    identical to payload
PASS         file:src/concurrency.ps1                                               identical to payload
PASS         file:tasks/build-check.json                                            identical to payload
PASS         file:tasks/mts-boot.json                                               identical to payload
PASS         file:tasks/mts-gate.json                                               identical to payload
PASS         file:tasks/mts-ship.json                                               identical to payload
PASS         fix:v0.7.0 fluent auto-run, task mode, parallel chats                  src/concurrency.ps1 has marker [af9f3446a]
PASS         fix:keep-alive: tab not discarded, worker heartbeat                    extension/background.js has marker [2c73ba9fe]
PASS         fix:v0.7.1 hands-free stays armed after a post                         extension/loop.js has marker [3270e7423]
PASS         fix:agent version constant (matches extension)                         src/agent.ps1 has marker [3ba37319b]
PASS         fix:B196 post gate keeps operator draft, auto-off banner               extension/loop.js has marker [8fb185ac0]
PASS         fix:B196 stop notice banner                                            extension/loop.js has marker [8fb185ac0]
PASS         fix:policy: fluent auto_mode                                           src/policy.json has marker [af9f3446a]
PASS         agent_ping                                                             answers: 0.7.6 (payload 0.7.6)
PASS         roundtrip                                                              exit=0 out='06c8ed6d93\r\n'
PASS         autostart                                                              task AIBridge-Agent registered
PASS         extension_loaded                                                       Chrome profile Profile 5 has id kgighilgkdgkdghegpibjbjcidcmejkg; config origin matches
aibridge_verify: PASS (0 FAIL of 29)
```

## 3. e2e_bridge.py --target installed F:/AIBridge --json

Exit 0. Top-level `"ok": true`. E5 is NOT_CHECKED (live DeepSeek chat not requested; needs `--live` from a Chrome-capable session).

```
E0 PASS aibridge_verify: 29 rows, no FAIL
E1 PASS tier B 6 selected, 6 keys; tier A audit non-dry runs per nonce [1, 1, 1, 1, 1, 1]
E2 PASS 2 thinking drafts ignored, 2 answer blocks selected; duplicate in answer -> block 1
E3 PASS 3 failing plans -> exit!=0 + TASK RESULT: FAIL; control PASS; fake command exit 0 (documented)
E4 PASS notice at 50s, stop at 110s; pump status: page text still changing after 200 s; DSA may be stuck. Unti
E5 NOT_CHECKED live DeepSeek chat not requested (use --live from a Chrome-capable session)
```

```json
{
 "bridge_version": "0.7.6",
 "target": "installed",
 "payload": "C:\\Users\\E-ngineers\\IdeaProjects\\mts-jis-nuc-dsabr-c7\\scripts\\aibridge",
 "utc": "20261031T134258Z",
 "ok": true,
 "cases": [
  {"case": "E0", "verdict": "PASS", "evidence": "aibridge_verify: 29 rows, no FAIL"},
  {"case": "E1", "verdict": "PASS", "evidence": "tier B 6 selected, 6 keys; tier A audit non-dry runs per nonce [1, 1, 1, 1, 1, 1]"},
  {"case": "E2", "verdict": "PASS", "evidence": "2 thinking drafts ignored, 2 answer blocks selected; duplicate in answer -> block 1"},
  {"case": "E3", "verdict": "PASS", "evidence": "3 failing plans -> exit!=0 + TASK RESULT: FAIL; control PASS; fake command exit 0 (documented)"},
  {"case": "E4", "verdict": "PASS", "evidence": "notice at 50s, stop at 110s; pump status: page text still changing after 200 s; DSA may be stuck. Unti"},
  {"case": "E5", "verdict": "NOT_CHECKED", "evidence": "live DeepSeek chat not requested (use --live from a Chrome-capable session)"}
 ]
}
```

## Manual step (operator)

Extension reload in chrome://extensions and F5 on the DeepSeek tab on JIS-NUC are not done by this run.

## Desk broadcast

Sent to jis-nb (`--to jis-nb --prio high`) as `python scripts/dev/aibridge_install.py F:/AIBridge --restart-agent`. Broadcast id b-93631b. Acks not awaited, per the card.
