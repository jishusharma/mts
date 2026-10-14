# Codex bridge (operator 2026-10-11)

Codex (free trial, JIS-NUC) and Claude share ONE repo and never share a folder. Rules, lanes and install: `CODEX_START.md` (single source; AGENTS.md -> CLAUDE.md).

Unattended use (layer lab, lane `CODEX`, `codex_run.py`, model and effort per card): `LAYER_LAB.md`.

## What Codex can and cannot see
- Cannot: claude.ai chats, artifacts (Control Room), App session history, `~/.claude`. Do not try to import them wholesale.
- Can: git (`origin/fast-track`), task cards, `sync.py news`, and a **pack file** outside the repo.

## The bridge: `python scripts/dev/codex_pack.py <card-id> [--chat exported.md]`
Writes `%CODEX_HOME%\packs\<card>.md` (brief, STATUS head, lessons digest, scope_in files). Refuses any path inside the project, so nothing
clutters the repo. Chats worth keeping: export the transcript (App: session menu, or `export_transcript`), pass `--chat`; it lands in
`%CODEX_HOME%\packs\chats\` as reference, never as instructions. Artifact content (Control Room decisions) goes the same way: paste or export to a file, `--chat`.
Results return only through the card flow: `tasks.py done`, `sync.py ship` (Codex trailer `MTS-Session: ...-COD-BLD-<slug>`).

## Budget policy (corrected 2026-10-12: the low account is jishu.sharma on JIS-NB, ~26% weekly left, resets Fri 2026-10-16; jishu.awgp on JIS-NUC had used 4%)
1. JIS-NUC carries the relay queue on Claude (primary dispatcher, `scripts/sched/relay_prompts/TWO_HOST.md`); JIS-NB yields and keeps the live path, deploy and data-bound desk tasks.
2. Codex (free trial, expires) takes SONNET/HAIKU code cards in parallel with the NUC relay, so the trial is used before it runs out. The claim is the lock between them.
3. Data check before a Codex card: `F:/MTS/data` on the NUC holds `dax_archive`, `dax_raw`, `tom_videos` and `fabio_videos` with frames (one-off copy from JIS-NB, 2026-10-12; no refresh job yet, list in LAYER_LAB.md). Data made on the NB after that date is not here: check the file dates before a card relies on it.
