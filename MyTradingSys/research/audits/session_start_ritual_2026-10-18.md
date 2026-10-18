# Session Start Ritual Audit vs AI-Health Token Goals (B183)

Date: 2026-10-18
Author: Gemini Flash worker (MTS session start audit)
Registry: B183 (follow-up to B172)
Reference goals: `MyTradingSys/research/TOKEN_AUDIT_2026-10-12.md` (B172)
Source data: `~/.claude/projects/*/*.jsonl` transcripts (last 3 days)

---

## 1. Executive Summary & First-Turn Input by Session Class

Under B172 (`MyTradingSys/research/TOKEN_AUDIT_2026-10-12.md:53-55`), the measured always-loaded context across all sessions was 63k-73k tokens (mean dispatcher-kick: 65,188 tokens). The goal of AI-health optimizations was to reduce always-loaded context and eliminate unnecessary prompt & ritual re-reads.

Over the last 3 days (measured via `scripts/dev/token_audit.py --days 3`), session classes exhibit distinct input profiles:

| Session Class | Count | Mean First-Turn Input (tokens) | Min First-Turn Input | Max First-Turn Input | SOURCED / OURS |
|---|---|---|---|---|---|
| **Builder** (`worker for MTS`) | 34 | 26,901 | 26,870 | 27,344 | SOURCED (`scripts/dev/token_audit.py` on `~/.claude/projects`) |
| **Relay** (`relay-session` / dispatcher kick) | 112 | 37,554 | 30,846 | 73,912 | SOURCED (`scripts/dev/token_audit.py` on `~/.claude/projects`) |
| **Coordinator** (`MTS SUPER SESSION` / tandem) | 21 | 73,270 | 72,041 | 75,712 | SOURCED (`scripts/dev/token_audit.py` on `~/.claude/projects`) |

### Key Observations:
- **Builders** load ~26.9k tokens initially (a ~59% reduction compared to the 65.2k baseline in B172).
- **Relays** average ~37.6k tokens initially, down from ~65.2k baseline in B172.
- **Coordinators** still load ~73.3k tokens due to retaining full context, supervisor guidance, and multi-lane status artifacts.

---

## 2. Startup Tool Calls in Builder Sessions (First 10 Calls)

Three recent builder session transcripts from `~/.claude/projects` were inspected:
1. `0ab87be3-49bc-4d55-85da-c1294d92a59e` (started 2026-10-17T11:18:19Z, task: `dsa-claude-standin-prompt`)
2. `f9743218-a396-403c-90c7-eaec4c729e3c` (started 2026-10-17T12:24:26Z, task: `gptb-fabio-escalation-event-table`)
3. `63975961-6a85-4785-9da8-c44cc045927e` (started 2026-10-17T12:24:55Z, task: `gptb-session-momentum-event-table`)

### Breakdown of First 10 Tool Calls Across the 3 Builder Sessions

| Session | Tool Call # | Tool & Action / Command | Result Bytes Read | Needed for this task? (yes / no / only if live-path) | Why / Redundancy Analysis |
|---|---|---|---|---|---|
| **S1** (`0ab87be3`) | 1 | Bash: `cd /f/MTS; ls; python sync.py start ...` (failed cwd) | 2,116 | **no** | Worker started in root where `sync.py` is not directly located; command failed |
| S1 | 2 | Bash: `cd /f/MTS/repo && ls ...; find . -name sync.py` | 89 | **no** | Blind exploratory directory probe |
| S1 | 3 | Bash: `cd /f/MTS/repo/MyTradingSys && cat CLAUDE.md | head -80` | 357 | **no** | Redundant CLAUDE.md read (CLAUDE.md is already loaded in system prompt) |
| S1 | 4 | Bash: `cd /f/MTS; find . -maxdepth 4 ( -name sync.py ... )` | 1,260 | **no** | Directory search probe |
| S1 | 5 | Bash: `cd /f/MTS; grep -rl "dsa-claude-standin-prompt" ...` | 796 | **no** | Task card search probe |
| S1 | 6 | Bash: `cd /f/MTS; for d in mts-*/; do git branch ...` | 1,411 | **no** | Worktree inventory probe |
| S1 | 7 | Bash: `cd /f/MTS/mts-codex-lab; head -c 3000 CLAUDE.md; sync.py start` | 8,342 | **yes** (sync.py start) / **no** (CLAUDE.md) | `sync.py start` finally ran from a valid worktree; re-read CLAUDE.md again |
| S1 | 8 | Bash: `cd <worktree> && sync.py claim; cat <task>.json` | 2,029 | **yes** | Enters assigned worktree, claims task, reads card |
| S1 | 9 | Bash: `cat DSA_STANDIN_PROMPT.md; git log ...` | 2,755 | **yes** | First real task execution step |
| S1 | 10 | Bash: `cd <worktree> && cat DSA_STANDIN_PROMPT.md ...` | 2,755 | **yes** | Redundant re-run of tool call 9 due to cwd confusion |
| **S2** (`f9743218`) | 1 | Bash: `python scripts/dev/sync.py start ...` | 653 | **no** | Failed in root CWD (No such file or directory) |
| S2 | 2 | Bash: `cd /f/MTS && python scripts/dev/sync.py start ...` | 653 | **no** | Failed in root CWD again |
| S2 | 3 | Bash: `ls | head -50; find . -name sync.py ...` | 1,814 | **no** | Exploratory directory probe |
| S2 | 4 | Bash: `cd /f/MTS && ls | head -50; find . ...` | 1,814 | **no** | Exploratory directory probe |
| S2 | 5 | Bash: `ls -d mts-*; ls -d *fabio* ...` | 1,997 | **no** | Exploratory worktree probe |
| S2 | 6 | Bash: `cd /f/MTS && ls -d mts-* ...` | 1,997 | **no** | Exploratory worktree probe |
| S2 | 7 | Bash: `grep -rl "gptb-fabio-escalation..." ...` | 2,532 | **no** | Task card search probe |
| S2 | 8 | Bash: `cd /f/MTS && grep -rl "gptb-fabio-escalation..." ...` | 2,532 | **no** | Task card search probe |
| S2 | 9 | Bash: `cd /f/MTS/mts-codex-lab && python scripts/dev/sync.py --help` | 1,650 | **no** | Tool discovery probe |
| S2 | 10 | Bash: `python scripts/dev/sync.py start ...; tasks.py brief ...` | 7,324 | **yes** | `sync.py start` and brief successfully executed |
| **S3** (`63975961`) | 1 | Bash: `cd F:/MTS && python scripts/dev/sync.py start ...` | 653 | **no** | Failed in root CWD |
| S3 | 2 | Read: `F:/MTS/CLAUDE.md` | 68 | **no** | Failed Read (file does not exist in root) |
| S3 | 3 | Bash: `cd F:/MTS && ls -la; find . -name sync.py` | 4,262 | **no** | Exploratory directory probe |
| S3 | 4 | Bash: `cd F:/MTS && ls -d */ | tail -30 ...` | 1,107 | **no** | Exploratory directory probe |
| S3 | 5 | Bash: `cd F:/MTS/repo && ls; git branch ...` | 168 | **no** | Exploratory directory probe |
| S3 | 6 | Bash: `cd F:/MTS/repo && ls MyTradingSys; git worktree list` | 473 | **no** | Exploratory directory probe |
| S3 | 7 | Bash: `cd F:/MTS && for d in mts-*; do git status; done` | 1,631 | **no** | Exploratory worktree probe |
| S3 | 8 | Bash: `cd /f/MTS/mts-jis-nuc-... && python sync.py --help` | 3,568 | **no** | Tool discovery probe |
| S3 | 9 | Bash: `cd /f/MTS/mts-codex-lab && python sync.py start ...` | 1,251 | **yes** | `sync.py start` run to produce WORKTREE notice |
| S3 | 10 | Bash: `cd <target-worktree> && mts_signal.py read; tasks.py brief ...` | 7,273 | **yes** | Brief, signals, and task claim |

---

## 3. Start Ritual Artifacts and Necessity Table

The startup ritual prescribed in `CLAUDE.md:5-11` specifies:
- `sync.py start <slug>`
- Read `STATUS.md`
- Read `ANNOUNCEMENTS.md`
- Read `LESSONS_DIGEST.md` (only for live-path or backtest work)
- Pick/claim card from `tasks.py` / `NEXT_SESSION.md`

| Startup Artifact / Action | Typical Size on Disk | Typical Tool Output Bytes | Needed for this task? | Rationale / Redundancy | SOURCED / OURS |
|---|---|---|---|---|---|
| **CLAUDE.md** | 6,290 bytes (48 lines) | 68 - 8,342 bytes (when read/catted) | **no** | Redundant. Explicitly stated at `CLAUDE.md:3`: *"Already loaded: do not Read this again."* Re-reading wastes 1-2 tool calls. | SOURCED (`CLAUDE.md:3`) |
| **sync.py start <slug>** | N/A (command) | 1,251 - 7,324 bytes | **yes** | Essential to print target worktree and switch branches. However, stdout is unnecessarily verbose (prints 10+ open claims and live mirror sync status). | SOURCED (`CLAUDE.md:6`) |
| **MyTradingSys/research/STATUS.md** | 5,859 bytes (73 lines) | 0 bytes in sampled builders | **no** (for builder tasks) / **yes** (for coordinators) | Builders are given isolated task cards. Reading entire repo status is unneeded for a scoped task; essential only for coordinators/dispatchers. | OURS |
| **MyTradingSys/system/ANNOUNCEMENTS.md** | 5,398 bytes (49 lines) | 0 bytes in sampled builders | **only if STOP/HOLD is active** | Coordinators/dispatchers check STOP/HOLD before dispatching workers. Builders dispatched by coordinators do not need to independently re-read. | OURS |
| **MyTradingSys/system/LESSONS_DIGEST.md** | 7,613 bytes (78 lines) | 0 bytes in sampled builders | **only if live-path** | Explicitly scoped at `CLAUDE.md:7`: *"LESSONS_DIGEST.md only for live-path or backtest work."* Redundant for routine audit/scaffolding tasks. | SOURCED (`CLAUDE.md:7`) |
| **Directory / CWD Probes** (`ls`, `find`, `grep`) | N/A | 10,000 - 18,000 bytes across 5-8 turns | **no** | Completely redundant waste caused by launching sessions in parent directory instead of the assigned worktree. | OURS |

---

## 4. Total Start Cost in Turns and Equivalent Tokens

### Measured Start Cost per Builder Session:
- **Turns to first real work:**
  - S1: **8 turns** spent in path discovery and re-reading before first task action (turn 9).
  - S2: **9 turns** spent in path discovery and tool help before first task action (turn 10).
  - S3: **9 turns** spent in path discovery and worktree checks before first task action (turn 10).
  - **Average start cost in turns:** **8.7 turns** (SOURCED: transcripts `0ab87be3`, `f9743218`, `63975961`).
- **Cumulative bytes read during startup:** **~20,000 - 24,000 bytes** (~5,000 - 6,000 input tokens added to context window).
- **Equivalent token re-read cost:**
  - Context size during startup is ~26.9k tokens.
  - 8 redundant turns x 26.9k tokens = **~215,200 cache-read input tokens** wasted per builder session before real work begins (OURS).
  - Multiplied across 34 builder sessions in 3 days: **~7.3M cache-read tokens** wasted solely in startup hunting (OURS).

---

## 5. Comparison to B172 Goals

In `MyTradingSys/research/TOKEN_AUDIT_2026-10-12.md:60-68`, B172 set 5 ranked cuts:

| B172 Goal / Ranked Cut | B172 Target | Current Status in Transcripts (2026-10-18) | Assessment |
|---|---|---|---|
| **Cut 1: Trim always-loaded prefix** | Reduce ~65k prefix by 30-50% | **Achieved for Builders:** First-turn input reduced from 65.2k to **26.9k tokens** (~58.7% reduction). Relay sessions reduced to **37.6k tokens** (~42.4% reduction). Coordinators remain at ~73.3k. | **PASS** (Builders & Relays meet B172 Cut 1 target). |
| **Cut 2: Template ritual into 1 call** | Reduce 21 mean turns by 8-10 turns | **Partially Achieved:** `relay.py begin` was introduced for relays. However, **builders still take 8-9 setup turns** due to CWD exploration and missing pre-launch worktree pinning. | **NEEDS FOLLOW-UP** (Builder ritual still wastes 8-9 turns). |
| **Cut 3: Hand session its task card** | Avoid re-reading NEXT_SESSION.md | **Achieved:** Prompts now specify task slug directly (`Boot: sync.py start <slug>`). | **PASS**. |
| **Cut 4: Cap tool output** | Cap tool output writes to save 20-40k writes | **Incomplete:** `sync.py start` still outputs full claim tables (1.2KB - 7.3KB output) adding unnecessary write tokens. | **NEEDS FOLLOW-UP**. |
| **Cut 5: Session turn caps** | Enforce 15-turn cap | **Partially Achieved:** Relay/dispatcher sessions are bounded (mean ~6 turns); builder sessions average 30-50 turns. | **ONGOING**. |

---

## 6. Follow-up Cards for Real Trims

Three actionable trim cards were registered under reference `B183` via `tasks.py new --ref B183`:

1. **`trim-builder-cwd-and-prelaunch-worktree`** (Ref: B183, Lane: SONNET, Prio: 3, Size: S)
   - *Goal:* Launch builder sessions directly inside their assigned worktree CWD with pre-seeded branch/repo context.
   - *Expected Saving:* Eliminates 5-8 exploratory probe tool calls (`ls`, `find`, `grep`), saving **~150k-200k cache-read tokens** per builder session.
2. **`trim-claudemd-re-read-guard`** (Ref: B183, Lane: SONNET, Prio: 3, Size: S)
   - *Goal:* Add explicit instruction in worker launch prompt preventing workers from executing `cat CLAUDE.md` or `Read CLAUDE.md`.
   - *Expected Saving:* Eliminates 1-2 redundant read calls and 6.3KB output, saving **~30k-50k cache-read tokens** per builder session.
3. **`trim-sync-start-output-cap`** (Ref: B183, Lane: SONNET, Prio: 3, Size: S)
   - *Goal:* Add `--quiet` flag or concise default to `sync.py start` for worker sessions, omitting the full claims table and mirror dump.
   - *Expected Saving:* Reduces `sync.py start` output from ~1.5KB-7KB to <200 bytes, saving write tokens on every turn 1.

---
*Audit completed without touching live tree, HALT files, `.secrets`, or `.env`. No rows in `BUGS.md` were closed.*
