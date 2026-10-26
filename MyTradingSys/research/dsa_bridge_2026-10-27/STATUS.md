# DSA bridge (AIBridge) on every MTS machine - status 2026-10-27

Operator order 2026-10-27. Check: `python scripts/dev/aibridge_verify.py F:/AIBridge` (28 rows: payload files byte-equal, each fix marker, agent ping, HTTP round trip, autostart, Chrome extension loaded). Raw output per machine: `verify_<host>.txt` beside this file.
Install anywhere: `python scripts/dev/aibridge_install.py F:/AIBridge [--fresh] [--restart-agent]` (`--fresh` = machine has no AIBridge: own token, loopback, origin from the Chrome path hash or `--origin=`).

## Shipped fixes (git log fast-track, scripts/aibridge)
| Fix | Commit | Where it lives |
|---|---|---|
| v0.7.0 fluent auto-run, task mode, parallel chats, receipts (B184) | af9f3446a | agent, checks, concurrency, extension |
| background keep-alive: no tab discard, worker heartbeat, link dot | 2c73ba9fe, e09b4eaec | extension |
| v0.7.1 hands-free stays armed after a post (DeepSeek input swap) | 3270e7423 | extension loop.js |
| agent version 0.7.1 | 3ba37319b | agent.ps1 |
| B196 post gate keeps operator draft, visible auto-off banner | 8fb185ac0 | extension content.js, loop.js |
| selftest hardening (port, timeouts) | 3e9e1601e, fda6264c2, 5086eea49, f4404dfa8 | tests only, not installed |

## Machine x fix (evidence: verify_*.txt)
| Check | JIS-LAPTOP (was NOT installed) | JIS-NB | JIS-NUC |
|---|---|---|---|
| bridge installed | PASS (fresh install today) | PASS | PASS |
| all 14 payload files equal trunk | PASS | PASS (B196 files updated today) | PASS (B196 files updated today) |
| v0.7.0 fluent | PASS | PASS | PASS |
| keep-alive | PASS | PASS | PASS |
| v0.7.1 hands-free | PASS | PASS | PASS |
| B196 draft-keep (was missing on NB and NUC, postGate count 0) | PASS | PASS | PASS |
| agent ping 0.7.1 | PASS | PASS | PASS |
| HTTP round trip (/run, token+origin) | PASS | PASS | PASS |
| Chrome extension loaded, id = config origin | FAIL: not loaded (Chrome needs Load unpacked) | PASS (running copy predates B196: Reload needed) | PASS (same: Reload needed) |
| autostart task AIBridge-Agent | NOT_CHECKED by design | PASS (exists) | PASS (exists) |
| DeepSeek desk round trip (`desk.py post --target DSA`) | NOT_CHECKED | NOT_CHECKED | NOT_CHECKED |

Notes
- NB/NUC were reached by `ssh -i ~/.ssh/id_ed25519_mts e-ngineers@<ip>` (works from the laptop); the payload went to `F:\MTS\tmp_dsa_bridge` there and `aibridge_install.py` ran without `--restart-agent` (agent code unchanged since 0.7.1; no process stopped).
- Autostart on the laptop: not registered. SCHEDULING_POLICY.md allows no standing task for AIBridge (the NB/NUC `AIBridge-Agent` tasks predate it and are not on its exception list: open policy question for the operator). Laptop agent was started once by the installer; after a reboot start it with `powershell -File F:\AIBridge\scripts\start-agent.ps1`.
- Remaining Chrome steps (cannot be done from here: Chrome blocks typing/clicking for agents, chrome://extensions): desk row 20261026-200004 (target OPERATOR). The older NUC row 20261019-050232 is superseded by this install.
- DeepSeek round trip: probe row posted `--target DSA` (needs a live DSA chat taking rows; ANNOUNCEMENTS 10-23 says no bridge has for 125 h+).
- Laptop extension id is derived from the path (sha256 of UTF-16LE `F:\AIBridge\extension`); NUC's real Chrome id matched the formula, so the laptop config should already match.
