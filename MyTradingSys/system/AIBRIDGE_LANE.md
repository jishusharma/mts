# AIBRIDGE LANE (MTS side)

Purpose. One page MTS reads to know what AIBridge is, what direct mode asks of it, and what
MTS never asks it to build. Rewritten 2026-10-08 (operator): DSA runs commands itself, the
reach is the project working tree, delete is allowed, the old per-command allowlist is gone.

## What AIBridge is

A local bridge that lets a web AI assistant run PowerShell on this machine through a loopback agent.

Root:            F:\AIBridge (on JIS-NB)
Entry docs:      F:\AIBridge\README.md, F:\AIBridge\SPEC.md
Status:          F:\AIBridge\ROADMAP.md
Layout:          F:\AIBridge\PROJECT_LAYOUT.md
Intro:           F:\AIBridge\docs\INTRODUCTION.md
Latest handoff:  F:\AIBridge\HANDOFF.md (dated copy beside it)
Open tasks:      F:\AIBridge\research\P3b-security-review-tasks.md
Security review: F:\AIBridge\research\P3b-security-review.md

Runtime:         F:\AIBridge\src\agent.ps1 on 127.0.0.1:7181
Config, policy, audit: same folder.
Extension:       F:\AIBridge\extension, Chrome MV3, loaded unpacked.

State 2026-10-01: P1, P2, P3a, P3b part 1 done. P3b part 2 blocked on the Chrome extension ID.
Bridge hard rules (its own project): loopback only, denials always win, audit every request,
no BOM, LF only, no emoji, read before write. A bridge-development session does not write into
the MTS repo; DSA, running commands through the bridge, does (below).

## Direct mode: what the bridge does (built 2026-10-08, F:\AIBridge, 4 commits)

Surface tag: AIBRIDGE. The model is DSA (chat.deepseek.com). Prompt contract:
DSA_SESSION_PROMPT.md section 0. Policy lives in F:\AIBridge\src\policy.json (re-read on every
request); the checks are in src\checks.ps1 (agent restart to reload). No MTS logic in bridge code.

Call format: a reply with a fenced block whose first line is
# AIRUN cwd=<dir inside a root> timeout=<s>
HTTP form: POST http://127.0.0.1:7181/run with {"cmd","cwd","timeout_s","token"} and the extension Origin.
Response: exit, out, err, ms, timed_out, out_truncated, out_bytes, timeout_s. A refusal is HTTP 403
with {"error":"refused","reason":"<code>: <text>"}.

Reach:
- Roots: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed and C:\Users\E-ngineers\IdeaProjects\mts-dsa
  (mts-dsa does not exist yet; DSA creates it once, prompt 0.6). Inside a root: read, write,
  create, move, copy, delete, run scripts, python, pytest, Maven, sync.py, desk.py.
- Refused: cwd or any path outside the roots; .secrets, .env*, key files, HALT*; writes into .git
  (reads allowed); killing processes except through scripts\core\stop-day.ps1 and mode.ps1;
  iex, Start-Process, Invoke-Command; nested shells without -File; $env: and profile variables.
- Not refused (not listed by the operator): git push and network commands. DSA ships through sync.py.

Caps: output 262144 bytes, cut with a [TRUNCATED...] marker (measured 2026-10-08: 1,080,245 bytes
produced, 262,144 kept). Timeout default 60 s, clamped to 300 s (measured: 3 s limit killed a 20 s
sleep, 999 clamped to 300). Audit: src\audit.jsonl, hash chain verified.

How enforcement is done. The checks are static text screens: they catch mistakes, not a script
that builds a path at run time. The real boundary is a limited Windows account (no admin, Modify on
the two roots, no access to .secrets or .env). Prepared, not applied:
F:\AIBridge\scripts\setup_limited_account.ps1 (dry run by default) and docs\LIMITED_ACCOUNT.md.
Applying it is an operator action on JIS-NB.

Incidents during the 2026-10-08 build (both from probes through the new bridge): a probe overwrote
BinanceDataFeed\.git\HEAD; restored to ref: refs/heads/fast-track and the screen fixed. mode.ps1 was run
twice as a probe; both exited 1 with APPARATUS ALREADY RUNNING, no state change seen. Operator check on
JIS-NB: branch, last commit, working tree status, and the loop still up.

Acceptance:
1. bridge_selftest.ps1 through the bridge prints SELFTEST: PASS. (The bridge session ran its own
   stand-in, F:\AIBridge\tests\bridge_selftest.ps1, because this repo's script had not shipped yet.)
2. The three denial probes in the script are refused (done with the stand-in's probes).
3. DSA boots from a regenerated session paste and its news section (DSA_SESSION_PROMPT.md 0.8).
4. A tracked-file edit made in mts-dsa ships with sync.py ship.
5. NOT YET MET: the result of a command reaches DSA without a paste from the operator, and the block
   runs without a click. DSA reports that today it sees results only when the operator pastes the
   panel output. Direct mode is complete only when the extension posts the result back into the chat
   input on its own (prompt 0.1 handles the gap by saying "no result seen").

## What MTS never asks AIBridge to build

No MTS-specific verb. No MTS schema. No MTS logic inside the bridge. The bridge stays a loopback
agent: run(command, cwd, timeout) -> {stdout, stderr, rc}. The roots, the deny list, the caps and
the audit key are configuration. If a need cannot be met by configuration, log it here and hold
it for the bridge operator.

## How a bridge task goes out and comes back

1. DSA composes a command and sends it in the bridge's call format.
2. The agent on 127.0.0.1:7181 applies the policy, runs it, returns stdout, stderr and rc.
3. DSA reads the result, acts, and records decisions in the MTS session record under the same session ID.
4. A refusal is data: DSA quotes it, names the one config change that would allow it, and stops.

## Open items
- Block parsing (observed 2026-10-09): the reader splits a fenced block into phantom blocks when a line inside begins with a hash, and only the first runs. In PowerShell source, build a hash from [char]35 so no source line begins with one. Long single-line commands get wrapped and come back as CommandNotFoundException; keep source lines under about 200 chars.

- Acceptance 5: extension auto-run and auto-return of results into the DSA chat (bridge project).
- Output ceiling per chat message: the bridge returns up to 262144 bytes; whether the chat accepts a
  result that large as one message is not measured. A 250 KB session paste may need ranged reads.
- Limited-account setup on JIS-NB: operator.
- Create mts-dsa (DSA, first boot).

## Pointers
- Pending patches for the merge-blocked files: DSA_SESSION_PROMPT.md.pending_patch_2026-10-09.md and MyTradingSys/system/LESSONS_LEARNED.md.pending_patch_2026-10-09.md. Splice, then delete each patch file.

- DSA_SESSION_PROMPT.md section 0 (direct mode) and 0.8 (paste and news, protected)
- SURFACE_POLICY.md section 1 (surface table)
- scripts\dev\bridge_selftest.ps1
- CLAUDE.md work routing line
- Dumps/operator/context/DSA_HANDOFF.md section 14 (worker directive)
