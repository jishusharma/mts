# CODEX INBOX - tasks for Codex (COD) sessions

Codex sees only its own checkout, so this file is the only way to hand it work. A sender appends a note,
commits and pushes; Codex pulls, reads it at boot, and after acting records the note in its session record
(MyTradingSys/system/sessions/) with the resulting commit on `codex/work`, then removes the note here.
Codex takes offline work only (SURFACE_POLICY.md section 1); anything needing local reach goes back to SUP.
Append notes below the line, one per bullet:
`- YYYY-MM-DD HH:MM UTC | from: <session ID> | <task> | done when: <observable result>`

---
- 2026-10-10 00:00 UTC | from: MTS-2026-10-10-0000Z-CLD-BLD-codex-handshake | HANDSHAKE: create your session record (COD), read AGENTS.md, commit a one-line ack in your record on `codex/work`, and append a reply note to CLOUD_INBOX.md | done when: ack commit exists on `codex/work` and SUP has fetched it
