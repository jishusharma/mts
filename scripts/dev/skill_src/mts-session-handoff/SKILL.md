---
name: mts-session-handoff
description: Close an MTS code-mode session. Use when ending a Claude Code session in the BinanceDataFeed repo, or when asked for a handoff, next-session prompt, or "close the session". Ships the work, then overwrites NEXT_SESSION.md. Not for DSA chat handoffs.
---

# MTS session handoff

Hard rules live in CLAUDE.md and state lives in STATUS.md. Point to them; never restate them.

## Steps
1. Gather facts from disk in one batch: this session's commit hashes (`git log`), `python scripts/dev/sync.py where`, `python scripts/dev/make_status.py`, `python scripts/dev/shot.py status`, and any AUTO_PAUSE this session set.
2. Gate and ship: `python scripts/dev/run_all_tests.py --quick` if code changed, then `python scripts/dev/sync.py ship`. The commit body carries `Result:` and the `MTS-Session: <ID>` trailer. Then `sync.py where` must show 0 unshipped. If a call is blocked, name the exact call and why, try the allowed equivalent, keep going.
3. Write the State section: only what STATUS.md does not already say.
4. Write the continuation prompt (format below).
5. Overwrite MyTradingSys/system/NEXT_SESSION.md. LF endings, no BOM, UTC times.
6. Run `python scripts/dev/check_handoff.py`. Fix every failure it prints, then print the prompt block in the reply.

## Format
Header: `# NEXT SESSION PROMPT (handoff <date>, <what the session did>; for <surface>)`

Prompt block (fenced, tag `text`), at most 30 lines:
- Line 1: role, then "Read CLAUDE.md, STATUS.md, then this file's State section."
- Step 0: `sync.py start`, then `sync.py where`.
- Numbered steps: file or command, expected result, and who decides if not the builder.
- Last line: "End: ship via sync.py ship, sync.py where must show 0 unshipped, overwrite this file."

`## State at handoff`, bullets:
- Shipped: what is on origin/fast-track, with short hashes.
- NOT shipped: what, which tree or session owns it, "do not edit".
- Stale, ignore: refs and files that look live but are not.
- Operator decisions pending: Control Room ID plus plain description on the same line.
- Near-miss: one line, only if one happened this session.

## Rules
- Every hash, count and path comes from a command whose output was seen this session. Re-run before writing; a count from memory or a worker report is not evidence.
- NEXT_SESSION.md sits under MyTradingSys, where a doc test rejects the strings git log, git status, git add, git commit, git diff, git checkout, git init and "version control". Cite commits by hash and describe actions in words.
- Other sessions' uncommitted files go under NOT shipped. Don't stash, clean or revert them.
- A decision already made is closed in the handoff, not listed as open.
- Operator questions go to the Control Room as decisions, or into the commit body as `Operator: <question>`.
- Never write budget, usage-percent or token numbers the operator did not supply.
- A labeled item (B148, D10, T085) carries its plain description on the same line.
- Plain text, no emoji or filler. Only commands and file content go in fences, each with a language tag.
- Nothing is left to the operator by hand. A step that needs the CLI becomes a `cli_tasks/` file plus a one-line note.
- Do not create a new `sessions/` file unless the operator asks.
