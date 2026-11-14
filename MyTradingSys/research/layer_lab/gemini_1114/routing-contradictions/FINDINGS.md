5 conflicts

# Routing, Workers, How MTS Runs, and Devices — Contradiction Scan

Scanned files (`git log -1 --format=%cs`):
- `MyTradingSys/system/ROUTING.md` (`2026-11-14`)
- `MyTradingSys/system/HOW_MTS_RUNS.md` (`2026-11-10`)
- `MyTradingSys/system/WORKERS.md` (`2026-11-09`)
- `MyTradingSys/system/DEVICES.md` (`2026-11-05`)

## Topic Table

| # | Topic | Status | Summary |
|---|---|---|---|
| 1 | Live loop host & deploy target (`JIS-NB` vs `DESKTOP-F7IU69N`) | CONFLICT | `DEVICES.md` says live loop cut over to `DESKTOP-F7IU69N` and `JIS-NB` holds no engine; `HOW_MTS_RUNS.md` & `ROUTING.md` still route live loop/deploys to `JIS-NB`. Newer: `ROUTING.md` (`2026-11-14`). Code: `tasks.py:46` keeps `JIS-NB` in `LANES`. |
| 2 | How the live tree changes (`MTS-AutoDeploy` vs manual/coordinator) | CONFLICT | `HOW_MTS_RUNS.md:21` says `MTS-AutoDeploy`; `HOW_MTS_RUNS.md:22`, `DEVICES.md:72`, `ROUTING.md:76,107` say manual/coordinator deploy (`MTS-AutoDeploy` retired). Newer: `ROUTING.md` (`2026-11-14`). Code: `sync.py:20-21` follows coordinator/supervisor deploy. |
| 3 | Worker type for size M / >30 turns (`agent` vs `session`) | CONFLICT | `WORKERS.md:18,20-21` & `ROUTING.md:9` say workers are background `Agent`s; `tasks.py:300,309-310` rejects `agent` for size M or `est_turns > AGENT_MAX_TURNS`. Newer: `ROUTING.md` (`2026-11-14`). Code: `tasks.py:309-310` requires `session`. |
| 4 | Gemini model names (`UNVERIFIED` vs `Flash` / `Argon`) | CONFLICT | `HOW_MTS_RUNS.md:27-28` says `Google's model, UNVERIFIED which`; `ROUTING.md:55,83,106` specifies `Flash` / `Argon` (`agy.exe`). Newer: `ROUTING.md` (`2026-11-14`). Code: `tasks.py:54` only defines GPT `CODEX_KINDS`. |
| 5 | DSA bridges (`DSA`, `DSA-NB`, `DSA-NUC`) status | CONFLICT | `HOW_MTS_RUNS.md:29` lists DSA bridges as active; `ROUTING.md:9,11,79-81,108` marks them `CLOSED under the standing operator hold`. Newer: `ROUTING.md` (`2026-11-14`). Code: `tasks.py:46` still includes `DSA`, `DSA-NB`, `DSA-NUC` in `LANES`. |
| 6 | Tool-turn cap (40 turns, no runtime hook) | AGREE | `WORKERS.md:30,33` and `tasks.py:305-306` agree 40 is the hand-over cap, with no runtime hook enforcing it. |
| 7 | CODEX lane ownership (GPT + Gemini `[GEMINI]`) | AGREE | `HOW_MTS_RUNS.md:26-28` and `ROUTING.md:63,65-66` agree `CODEX` lane carries both GPT (`codex_run.py`) and Gemini (`[GEMINI]` cards). |
| 8 | Machine names (`JIS-DESKTOP`/`JIS-NB`, `JIS-LAPTOP`/`DESKTOP-F7IU69N`, `JIS-NUC`) | AGREE | `HOW_MTS_RUNS.md:16`, `DEVICES.md:19-22`, and `ROUTING.md:54,57` agree on the old/new machine name mapping. |
| 9 | Model per Claude lane (`HAIKU`, `SONNET`, `OPUS`) | AGREE | `WORKERS.md:34-37`, `HOW_MTS_RUNS.md:33`, `ROUTING.md:75,89,98`, and `tasks.py:446-449` agree on Sonnet default, Haiku for scoped/mechanical work, and Opus only when operator-named or `approved_by` + `crucial`. |

## Conflict Details (Verbatim Quotes)

### 1. Live loop host & deploy target (`JIS-NB` vs `DESKTOP-F7IU69N`)
- **Side A (`MyTradingSys/system/DEVICES.md:54`, `2026-11-05`)**:
  > "The cutover ran 2026-10-22: the loop runs on the laptop and JIS-NB holds no engine."
- **Side B (`MyTradingSys/system/HOW_MTS_RUNS.md:22`, `2026-11-10`)**:
  > "| JIS-NB | Windows tasks, no model (RETIRED 2026-10-17, see SCHEDULING_POLICY.md: MTS-Supervisor, MTS-AutoDeploy, MTS-Backup, MTS-DailyHygiene are stopped/to be unregistered) | the live testnet system (auto_trader, position_manager, daily_loss_monitor, live_runner_cli, order-flow and context feeds, 2 Java feeds);"
- **Side B (`MyTradingSys/system/ROUTING.md:76`, `2026-11-14`)**:
  > "| Deploy to the live tree, process checks, HALT state reads | JIS-NB | desk row `--target JIS-NB` (or the NB coordinator's deploy step, DEPLOY_RUNBOOK.md) |"
- **Newer**: `ROUTING.md` (`2026-11-14`).
- **Code**: `scripts/dev/tasks.py:46` keeps `"JIS-NB"` in `LANES = ("HAIKU", "SONNET", "OPUS", "DSA", "DSA-NB", "DSA-NUC", "JIS-NB", "CODEX")`.

### 2. How the live tree changes (`MTS-AutoDeploy` vs manual/coordinator)
- **Side A (`MyTradingSys/system/HOW_MTS_RUNS.md:21`, `2026-11-10`)**:
  > "work trees only; the live tree changes only through MTS-AutoDeploy"
- **Side B (`MyTradingSys/system/DEVICES.md:72`, `2026-11-05`)**:
  > "Only the live tree on JIS-NB (marked `.mts_live`) never ships; it changes only by manual or coordinator-run deploy (DEPLOY_RUNBOOK.md; MTS-AutoDeploy RETIRED 2026-10-17, see SCHEDULING_POLICY.md)."
- **Side B (`MyTradingSys/system/ROUTING.md:107`, `2026-11-14`)**:
  > "- C6 HOW_MTS_RUNS.md (10-15) still says the live tree changes only through MTS-AutoDeploy and lists dispatchers as running (marked RETIRED in place); SCHEDULING_POLICY.md and CLAUDE.md (manual or coordinator deploy) win."
- **Newer**: `ROUTING.md` (`2026-11-14`).
- **Code**: `scripts/dev/sync.py:20-21` follows coordinator/supervisor deploy: `so it changes only by the supervisor deploy (stop, ff-merge, gate, restart).`

### 3. Worker type for size M / >30 turns (`agent` vs `session`)
- **Side A (`MyTradingSys/system/WORKERS.md:20`, `2026-11-09`)**:
  > "3. **One-use Agent** (background, Sonnet, used once, never SendMessage'd) for size S or M with `est_turns` <= 30"
- **Side A (`MyTradingSys/system/ROUTING.md:9`, `2026-11-14`)**:
  > "(2) Worker type: WORKERS.md rule 7 wins, workers are background Agents; "session" only for interactive roles (the NB deploy row, the "session / N" items in Routed open items are legacy labels read as Agent)."
- **Side B (`scripts/dev/tasks.py:309-310`)**:
  > `elif w == "agent" and isinstance(t, int) and (t > AGENT_MAX_TURNS or card.get("size") != "S"):`
  > `    p.append(f"worker agent only for size S and est_turns <= {AGENT_MAX_TURNS}: make it a session")`
- **Newer**: `ROUTING.md` (`2026-11-14`).
- **Code**: `scripts/dev/tasks.py:309-310` enforces `session` for size M or `est_turns > AGENT_MAX_TURNS`.

### 4. Gemini model names (`UNVERIFIED` vs `Flash` / `Argon`)
- **Side A (`MyTradingSys/system/HOW_MTS_RUNS.md:27`, `2026-11-10`)**:
  > "| JIS-NUC | Gemini `gemini-nuc` (Antigravity, `agy.exe`) | any Claude login starts it, no scheduler (ROUTING.md "Gemini access"): lane CODEX cards the Codex lab has not claimed (GEMINI_START.md) | Google's model, UNVERIFIED which |"
- **Side B (`MyTradingSys/system/ROUTING.md:83`, `2026-11-14`)**:
  > "| Cross-vendor review of a Claude or GPT result | JIS-NUC | card lane CODEX for Gemini (`gemini_queue.py`) or GPT (`codex_run.py`); a reviewer never the producer's model | Gemini Flash (Argon for C2/C3) / GPT |"
- **Newer**: `ROUTING.md` (`2026-11-14`).
- **Code**: `scripts/dev/tasks.py:54` only defines GPT `CODEX_KINDS` (`"gpt-6-luna"`), not Gemini models.

### 5. DSA bridges (`DSA`, `DSA-NB`, `DSA-NUC`) status
- **Side A (`MyTradingSys/system/HOW_MTS_RUNS.md:29`, `2026-11-10`)**:
  > "| JIS-NB and JIS-NUC | DSA (DeepSeek chat, no Claude login) | lanes DSA, DSA-NB, DSA-NUC: run-and-report jobs from the desk board (`desk.py`) through AIBridge | DeepSeek |"
- **Side B (`MyTradingSys/system/ROUTING.md:9`, `2026-11-14`)**:
  > "(3) DSA bridges (DSA/DSA-NB/DSA-NUC): CLOSED under the standing operator hold (he drove DSA 11-10/11, then said run no more rows); rows below naming them are history, reopened only by his word."
- **Newer**: `ROUTING.md` (`2026-11-14`).
- **Code**: `scripts/dev/tasks.py:46` still includes `"DSA", "DSA-NB", "DSA-NUC"` in `LANES`.
