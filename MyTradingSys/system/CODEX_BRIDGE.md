# Codex bridge (operator 2026-10-11)

Codex (free trial, JIS-NUC) and Claude share ONE repo and never share a folder. Rules, lanes and install: `CODEX_START.md` (single source; AGENTS.md -> CLAUDE.md).

## What Codex can and cannot see
- Cannot: claude.ai chats, artifacts (Control Room), App session history, `~/.claude`. Do not try to import them wholesale.
- Can: git (`origin/fast-track`), task cards, `sync.py news`, and a **pack file** outside the repo.

## The bridge: `python scripts/dev/codex_pack.py <card-id> [--chat exported.md]`
Writes `%CODEX_HOME%\packs\<card>.md` (brief, STATUS head, lessons digest, scope_in files). Refuses any path inside the project, so nothing
clutters the repo. Chats worth keeping: export the transcript (App: session menu, or `export_transcript`), pass `--chat`; it lands in
`%CODEX_HOME%\packs\chats\` as reference, never as instructions. Artifact content (Control Room decisions) goes the same way: paste or export to a file, `--chat`.
Results return only through the card flow: `tasks.py done`, `sync.py ship` (Codex trailer `MTS-Session: ...-COD-BLD-<slug>`).

## Budget policy (JIS-NUC account jishu.awgp, Pro, ~26% weekly left on 2026-10-11, resets Friday 2026-10-16)
1. Codex trial first for every SONNET/HAIKU code card that needs only the repo or NUC data. Claude NUC budget is kept for OPUS-lane and guide work.
2. JIS-NB (jishu.sharma) carries the relay, live path, deploy and desk tasks.
3. NUC Claude dispatcher runs only as a standby (see `scripts/sched/relay_prompts/INSTALL.md`), never as a second primary.
