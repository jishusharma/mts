# T10 bridge playbook (merged from the bridge logs of the DSA audit reports)

Built 2026-10-24 by the T10 worker (Claude builder session, not a DSA chat). Status: PARTIAL. Only reports that were on origin/fast-track at start sha b43de092f were read.

## 1. Which reports were read

| Report | Shipped | Bridge log content | Used here |
|---|---|---|---|
| T01 data forensics | yes (3a9b389a8) | full table, 17 rows covering results #1-#50, JIS-NUC | yes, main source |
| T02 look-ahead and time | yes | "No AIBridge was used" (Claude worker, Lenovo) | no bridge rows; chunk process read from T02_F1_chunks.tsv |
| T03 planted edges | yes (c73617400 is the fix) | "Not applicable: 0 bridge replies" | no bridge rows |
| T08 split and trials | yes (e96f3dbd2) | prose only, "no AIBridge calls were made"; one truncated brief read, one stale wildcard command | yes, 2 lessons |
| T04 independent rebuild | NO report. Only scripts/T04/_make_log.py (ambiguity log helper) | missing | listed as missing |
| T05 placebo nulls | missing | missing | listed as missing |
| T06 costs and fills | missing | missing | listed as missing |
| T07 reproducibility | missing | missing | listed as missing |
| T09 backtest-to-live parity | missing | missing | listed as missing |

Plain reading: of 4 shipped reports, 1 used the bridge. The bridge evidence is one chat on one machine (T01, JIS-NUC). Rules below that rest on the brief or AIBRIDGE_LANE.md and not on a T01 result number are marked UNPROVEN. Rerun this merge when T04-T07 and T09 ship.

## 2. Call patterns that saved the most replies

1. Write-then-run pair (T01, results #36-#37, #42-#43, #45-#46). Block 1 writes the script with the whole text piped into dsa.py put; block 2 runs it with Tee-Object into scripts/Tnn/out/<name>_run.txt. Every finding then names a run file. Four to five read-only probes per reply ran cleanly in 1-2 s total (#9-#17, #22-#25, #28-#35).
2. Long scans (64 s inventory plus invariants, #36-#37) worked as a plain call because they stayed under the plain timeout (default 60 s, clamped to 300 s per AIBRIDGE_LANE.md lines 57-58). Anything over 300 s goes to task mode (cap 1800 s) in chunks.
3. Chunking by card, not by reply (T02-F1): 132 unreviewed allowlist rows were split into 4 chunk cards of about 30-35 rows, each its own commit (660a7fe05 reviewed 35 rows, c68e93ced reviewed 30). No chunk was lost when one worker stopped.
4. Count first, then read (T08 lesson): after a truncated brief read, the worker re-read only sections 5-7 plus its own part. Persist tables to files, then print counts.

## 3. Failures and recoveries

| Failure | Where proven | Recovery that worked |
|---|---|---|
| task=mts-boot failed at step 1, repo path truncated to C:\Users\E (NOT RUN, WorkingDirectory) | T01 result #1 | manual boot in #18-#21 (worktree check, dsa.py host, sync start); same facts, one defect to fix in the playbook |
| `dir /B` rejected: cmd syntax in a PowerShell 5.1 block | T01 #5, #6 | Get-ChildItem -Name |
| 262144-byte output cap, [TRUNCATED] marker | T01 #19 | wrote the news file in #21, read ranges |
| Report file corrupted by PowerShell 5.1 string .Replace([char]0x2014, '--') followed by a regex strip of [\u0080-\uFFFF]: every literal i was lost | T01 #50 | rewrote the whole file fresh; do not patch a corrupted file |
| Brief path missing on the host (Dumps/backtest/raw/fundingRate absent on JIS-NUC; data lives in raw_fund/ and raw_1m_2022/) | T01 #38-#41 | treated as a finding (funding path drift), not a stop |
| Combined brief read truncated | T08 | read sections 5-7 and the card section separately |
| Stale Windows wildcard command | T08 | explicit paths |
| Brief paths T03_*.md wrong in a listing | T01 #27, fixed in #28 | re-list the folder |

## 4. Ten rules for the next DSA audit chat

1. Boot by hand if task=mts-boot fails once. Do not retry it (T01 #1, #18-#21).
2. Use the write-then-run pair: dsa.py put the script, then run it with Tee-Object into scripts/Tnn/out/ (T01 #36-#46).
3. PowerShell 5.1 only: Get-ChildItem -Name, no `dir /B`, no `&&`, no ps7-only syntax (T01 #5-#6; refusal code ps7_only in AIBRIDGE_LANE.md line 53).
4. Never clean unicode with .Replace([char]X, s) chains or a high-range regex. Write ASCII, or write the file fresh (T01 #50).
5. Anything that may exceed 262144 bytes goes to a file first; read a count or a range (T01 #19; brief 4b).
6. A path in the brief that does not exist on this host is a candidate finding. Search the sibling folders (raw_fund, raw_1m_2022) and go on (T01 #38-#41).
7. Batch 4-5 independent read-only probes per reply; put dependent steps in the next reply (T01 #13-#17, #28-#35).
8. Over 60 s: use task mode with chunks (one month, one study, one chunk card), each chunk its own file; the last step merges (brief 3.3; T02-F1 chunk cards). UNPROVEN on the bridge: no shipped report ran a task-mode chunk.
9. No result back: do not resend. Send the read-only heartbeat (hostname, UTC time, output file size and last line, git status) (brief 3.5). UNPROVEN: no shipped log shows a heartbeat.
10. Keep Tnn_PROGRESS.md current after every step and the bridge table as you go, not at the end. T01 lost its report text once (#50) and had to rewrite it, so a current progress file and a running table shorten the recovery (brief 4a, 4c).

## 5. Proposed DSA_SESSION_PROMPT.md changes (not edited here; posted to Claude with desk.py)

- P1: "If task=mts-boot fails, boot manually (worktree, dsa.py host, sync.py start) once and log the bug."
- P2: "Blocks are PowerShell 5.1. Never edit a report with .Replace(char) or a high-range regex; rewrite the file."
- P3: "A brief path missing on this host is a candidate finding; check raw_fund and raw_1m_2022 siblings before BLOCKED."
- P4: "Write the bridge table into the report while working; one row per result range."

## 6. Open items

- Rerun this merge after T04, T05, T06, T07 and T09 ship (their bridge rows will test rules 8 and 9).
- No bridge evidence exists for agent_unreachable or extension_link recovery in any shipped report.
