# MTS - Codex sessions

The rules for Codex sessions are identical to `CLAUDE.md` in this folder. Read that file; it is the single source.
Do not copy rules here (two copies drift). Claude-only parts to skip: Boot steps 4-5 (hand-over, short sessions), screenshots, pages follow builds, DSA posting.
Reference answers (push fallback, CI/CD, Codex status): `MyTradingSys/system/QUICK_ANSWERS.md`.
Red trunk: the author reverts the breaking commit within 10 minutes, anyone else after that (`git revert`; the failing file at its last-green bytes is a revert, a new line is a forward-fix); see SUPER_SESSION.md D3.

Codex entry point and first-message prompt: `MyTradingSys/system/CODEX_START.md`. Protocol: `MyTradingSys/system/PARALLEL.md`.
Layer lab (lane `CODEX`, the Codex app project "MTS Layer Lab", unattended runs): `MyTradingSys/system/LAYER_LAB.md`.

Gemini (Antigravity, JIS-NUC) has its own entry point: `GEMINI.md` -> `MyTradingSys/system/GEMINI_START.md`.
