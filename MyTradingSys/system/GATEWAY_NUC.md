# GATEWAY_NUC: the NUC runs on a gateway profile, login B is off there (operator 2026-10-26)

Public repo: no key, no URL with credentials, no account data in this file or anywhere near it.

## What changed
- The Claude app on JIS-NUC now runs a **Gateway** profile (third-party inference, a shared API key held by the operator). The subscription login B is not available on the NUC while the policy is applied.
- Other stations keep their subscription logins (A, C). When one of them runs out of data the operator may switch it to the gateway by hand; do not assume it.
- The gateway has no tracked weekly cap and does not report usage. Do not run `mts_signal.py budget` for it.
- Chat history is per profile: the Gateway profile starts empty. Worktrees and folders are plain files on disk and are the same for both profiles.

## What goes to the NUC gateway (put the load there)
- Fable-lane and other heavy card work that does not need private data: builds, refinements, audits, studies on tracked files of this public repo.
- How to send it: a card in a lane the NUC coordinator takes, or a desk row `python scripts/dev/desk.py post "<title>" --need "<exact commands>" --done-when "<observable>" --target JIS-NUC`.
- Keep the NUC busy: when a NUC session finishes a card it takes the next one (`tasks.py next`) until the operator says stop.

## Rules for every session that runs on the gateway
1. **Public tracked files only.** The model provider is a third party that can read and log every prompt, file read and command output. Never read or paste `.secrets/`, `.env`, keys, runtime, order or account data, the live tree (`.mts_live`), or F:/ backups. Not even "just to check".
2. Work only in a worktree under `<repo>/.claude/worktrees/` (new session, Worktree switch ON in the folder menu, branch fast-track). If `pwd` is the main checkout, stop and start again.
3. App settings already set on the NUC: block reads outside working directories ON, bypass-permissions mode disabled, scheduled tasks OFF. Do not change them.
4. The model's self-description is not proof of which model answered (it gave different names in two tests). Treat results as unverified: a spot-check by another session or a test run before anything ships, as for any worker (CLAUDE.md "spot-check a worker claim").
5. No mic button in gateway mode (dictation is an Anthropic-account feature). The operator dictates with Windows voice typing or a local dictation tool.
6. Ship as usual: `sync.py ship --release <slug>`, commit body carries `Result:`. Never commit the registry file the operator exported; it holds the key and lives outside the repo.

7. **Its worktree is its own (operator 2026-10-26).** A gateway session's worktree and branch belong to that session alone. No other session, login, station, Lead, tidy or cleanup script removes, resets, merges into or edits it; a cleanup touches only worktrees its own session made. Every login on a station that may run on the gateway reads this at boot.

## Switching a station on or off (operator only)
- On: merge the exported registry file on that machine, fully quit and reopen the app.
- Off: merge the matching removal file, reopen the app. Both files stay outside the repo in the operator's Documents folder.

## Open points
- Key: the first key gave "Invalid API key" on every generation (the model-list call answers 200 even for a made-up key, so "Test connection" proves nothing). A replacement key was entered on the NUC on 2026-10-26 and the session answered; re-verify before sending a big queue.
- Speed is not measured yet (card of the same name).
