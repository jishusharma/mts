# B133 - DSA defaults to CLI or ships the mts go launch block when the App is the correct surface

Status: OPEN. Severity: MED. Opened 2026-10-04.
Filed by: MTS-2026-10-04-1325Z-DSA-COO

## Operator directive (verbatim, 2026-10-04)

"CLI only for the listed reaches - remove CLI from that list - anything CLI
does can be done by Claude Code Win App. It is UI - good for me!"

## Policy change

Landed as SURFACE_POLICY.md section 1b rewrite at d36ec97
("SURFACE_POLICY 1b: App covers every reach; CLI is fallback").

Before (block d36ec97 replaced):
  "## 1b. Surface choice (operator directive 2026-10-03)
   App first. CLI is fallback, not default...
   1. Claude Win App (Code / Cowork / Chat / Cloud modes) - use whenever it
      can do the job.
   2. CLI - only when the task needs something the App cannot reach: local
      Maven, local testnet, the live loop, PowerShell-only files, scripts
      that import from the repo tree, a disk write to a gitignored path, or
      anything the App explicitly refuses."

After (current on disk):
  "## 1b. Surface choice (operator directive 2026-10-04)
   App first, always. Claude Code Win App (Code / Cowork / Chat / Cloud
   modes) covers every reach: local Maven, local testnet, the live loop,
   PowerShell-only files, scripts that import from the repo tree, and
   writes to gitignored paths. CLI is a fallback, not a default."

## Instances in MTS-2026-10-04-0916Z-DSA-COO after d36ec97 landed

1. Phase 0 plan. DSA wrote: "Phase 0 - operator, CLI, before any writer
   touches the tree" and "One command. Run it." with the loop restart
   framed as a CLI action. The policy says the App covers the live loop.
   DSA labelled it CLI anyway.

2. R7 dispatch. DSA wrote "R7 is a code + backtest task with the test gate
   and F: drive data. It is a CC dispatch." Two errors: CC is cloud, not
   App; and the task needs F: which cloud cannot reach. Operator corrected.

3. Handoff note. DSA wrote "Loop restart runs in a CLI window." in the
   hard rules section. Contradicts section 1b directly.

4. B104 prompt-hygiene thread. DSA composed a CLI-style prompt without the
   mts go launch block; operator: "u missed the prompt format". Break #6 of
   B104 nine-break list is exactly this. B104 is CLOSED at 41dc5f3, but the
   behaviour repeated this session.

## Nearest open rows

- B101 (OPEN, LOW): "DSA asks for CLAUDE.md and mts go launch block before
  composing a CL prompt". Ask side only.
- B132 (OPEN): dispatch vs surface. Different subject.

No row carried the surface-choice defect against the 2026-10-04 directive
before this filing.

## Fix shapes

(a) prompt_check.ps1 gains a check: reject a composed prompt that contains
    the mts go launch block when the surface target is App.
(b) DSA_SESSION_PROMPT.md section 9 gains a line: the mts go launch block
    belongs to CLI prompts only; App prompts open with the task brief.
(c) SURFACE_POLICY section 1b already states the rule; B133 exists so the
    behaviour gap has a tracker and a fix lands in prompt_check.

## Evidence pointers

- SURFACE_POLICY 1b rewrite, landed d36ec97.
- B104 (CLOSED 41dc5f3), break #6.
- B101 (OPEN), ask-side only.

# END

## Root causes (2026-10-04, operator request)

Three causes, one on disk, one on the composer, one on the format.

1. Rule text is ambiguous. USER.md LIKES reads "Every CLI prompt DSA
   prints opens with the mts go launch block." DSA_SESSION_PROMPT.md
   section 9 reads "CLI prompts open with the mts go launch block." Both
   are scoped to CLI. Both are correct. Neither names the App prompt. No
   line on disk says what an App prompt opens with, so the CLI form is the
   only opening the composer has.

2. Composer read the block as a prefix, not a surface marker. The row for
   this bug was read, quoted, and ignored two turns later when the B093
   prompt was composed. The rule and the violation were held in the same
   working set.

3. Mechanical: the surface line sits below the block. A reader who scans
   top-down sees the block first and never notices the surface mismatch.
   The format enforced the error.

## Fix (three parts)

1. Code: prompt_check.ps1 gains check 12 (a body carrying the mts go
   line with surface marker App fails) and check 13 (exactly one surface
   marker line required). Dispatched as B133 prompt.
2. Doc: DSA_SESSION_PROMPT.md section 9 gains one line. App prompts open
   with Session ID, Mode line, repo root, then the task brief. The mts go
   launch block belongs to CLI prompts only.
3. Lesson: LESSONS_LEARNED.md entry logged 2026-10-04.

## Receipt: part 1 (code), 2026-10-05
Commit 81c7e9f (session MTS-2026-10-04-2005Z-APP-BLD-b133-surface). scripts/dev/prompt_check.ps1:
- check 12: a prompt whose only SURFACE marker is APP and which carries a line matching `mts go` FAILs; CLI marker or no marker is not applicable.
- check 13: exactly one line `SURFACE: APP` or `SURFACE: CLI`; zero, two or more FAIL.
scripts/dev/test_prompt_check.ps1: fixtures 13-16 added (16 of 16 PASS); fixtures 1-12 keep passing with a SURFACE: APP line added to their header and log-row count 11 -> 13.
Parts 2 (DSA_SESSION_PROMPT.md section 9) and 3 (lesson) remain open.
