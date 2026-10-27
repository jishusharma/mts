# Layer Lab Report: `runaway-guard-design-review` (2026-10-27 UTC)

- **Card:** `runaway-guard-design-review` (`CODEX`, size M, prio 1, weight `IMPORTANT`)
- **Reviewer:** Gemini 4 Argon (Low) (`gemini-nuc`, surface GEM, independent cross-vendor model from author Claude Sonnet 5.5)
- **Primary Deliverable:** `MyTradingSys/system/RUNAWAY_GUARD_REVIEW.md`
- **Verdict:** **ACCEPT** (6 numbered findings; all 7 section-5 questions answered with transcript quotes, bounded scratch experiment output, and live host measurements; `SCHEDULING_POLICY.md` fit verified).

## Summary of Evidence & Citations

1. **Transcript Verification (`RUNAWAY_GUARD.md:7-10`):**
   - `C:\Users\E-ngineers\.claude\projects\C--Users-E-ngineers-IdeaProjects-BinanceDataFeed\b548c0a6-bbf8-4e96-bf38-b401f4389223\subagents\agent-af27dbcb366bdce5d.jsonl:38-43` confirms subagent `af27dbcb` spawned `find / -iname "*openinterest*" -o -iname "*oi_5m*" -o -iname "*open_interest*" 2>/dev/null | grep -v node_modules | head` at `2026-10-26T01:09:27.639Z` (`06:39:27` local), timed out after 120 s (`01:11:28.366Z`, task `blra0fwc7`), and called `TaskStop` (`01:11:30.464Z`).
2. **Bounded Scratch Reproduction (`JIS-NUC`):**
   - Spawned `C:\Users\E-ngineers\Git\bin\bash.exe --login` on a 20-file scratch folder with a bounded 15 s sleep inside `find ... | grep -v node_modules | head`.
   - Verified that killing root `bash.exe` (`Stop-Process`) AND `taskkill.exe /T /F /PID <root_bash_pid>` both leave `find.exe`, `grep.exe`, `head.exe`, and `sleep.exe` running as orphans because MSYS2 forks pipeline stages from intermediate subshells that exit immediately, breaking the Windows `ParentProcessId` chain.
   - Verified that a Python `ctypes.windll.kernel32` Windows Job Object (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000`) kills 100% of the MSYS2 pipeline children (`0 survivors`).
   - All scratch processes cleaned up (`0` remaining).
3. **Layer 1 Regex (`10 deny / 10 allow`):**
   - Tested `BARE_ROOT_SCAN_RE` against 10 root-scan deny strings (`/`, `C:\`, `F:/`, `/c/`, `grep -rn ... /`, `grep -R ... C:/`, `ls -laR /`, `du -sh /`, `Get-ChildItem -Path C:\ -Recurse`) and 10 scoped allow strings (`find MyTradingSys ...`, `find /f/MTS/data/tom_raw ...`, `git ls-files ...`): `20/20 PASS`.
4. **Thresholds & Fleet Broadcast `b-8ce4da` (`RUNAWAY_GUARD.md:44,50-59`):**
   - `JIS-NUC` live (`runaway_check.ps1`): `free 19,737 MB of 32,571; paged pool 1,063 MB; nonpaged pool 480 MB; OK`. Max handle count: `System` `5,036`, `explorer` `2,282`, `ChatGPT` `2,200` (vs `100,000` threshold, `OURS`).
   - `JIS-DESKTOP` (`jis-nb`, signal `20261027T124206Z185537-jisnb-6be2.json`): `done` — `OK no runaway processes, free RAM 15.4 GB`.
   - `JIS-LAPTOP` (`desktop-f7iu69n`, signal `20261027T184516Z329008-desktopf7iu6-3df2.json`): `done` — `OK no runaway`.
   - `vm`: `NOT_IN_DATA` (no reply to `b-8ce4da`).
5. **Policy Fit (`SCHEDULING_POLICY.md:6-34`) & NUC Event 142 (`NUC_SHUTDOWN_HANDOVER.md:88-118`):**
   - Layer 1 & Layer 2 (`PreToolUse`, `SessionStart`, `UserPromptSubmit` hooks in `.claude/settings.json`) require **no** `SCHEDULING_POLICY.md` exception. Layer 4 (`always-on watcher`) is not recommended.
   - `nuc_health.ps1 -Days 7` shows 17 `event 142` watchdog resets (10 after `find.exe` was killed on `2026-10-26 15:55`, including `2026-10-27 19:41:20` where `nuc_watch.csv` at `19:35:49` logged `CPU 4%, free RAM 21,455 MB, disk 0%`). This settles that `event 142` is hardware/power delivery (`d-nuc-hw-verdict`: 120 W adapter swap arriving ~04 Nov, then UPS + BIOS `0067` + CR2032 if needed), not the runaway `find.exe`.
