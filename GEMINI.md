# MTS - Gemini sessions

The rules for Gemini sessions are identical to `CLAUDE.md` in this folder (via `AGENTS.md`). Read that file; it is the single source. Do not copy rules here.
Claude-only parts to skip: Boot steps 4-5 (relay hand-over), screenshots, pages follow builds, DSA posting.
Entry point and first-message prompt: `MyTradingSys/system/GEMINI_START.md`. Protocol: `MyTradingSys/system/PARALLEL.md`.
Never ask back (operator 2026-10-18): after looking at the queue, claim the top ready card of your lane and start it. "Would you like me to claim X?" is a failure; the task is implied.
Never read `.secrets/`, `.env` or keys. Work only in your own work tree, never the live tree.
