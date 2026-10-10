# AGENTS.md - Codex (surface COD) entry point

Read `CLAUDE.md` first and follow it; it is the single source of rules. Then read
`MyTradingSys/system/SURFACE_POLICY.md` and `MyTradingSys/research/STATUS.md`.

Codex-specific:
- Work only on branch `codex/work` in your own checkout/worktree. Never commit to `fast-track` or `main`/`master`; never push to them, merge, rebase or reset.
- Surface is `COD`. Session ID: `MTS-YYYY-MM-DD-HHMMZ-COD-<ROLE>[-<slug>]`; record it in `MyTradingSys/system/sessions/`; commit trailer `MTS-Session: <ID>`.
- Tasks arrive in `MyTradingSys/system/CODEX_INBOX.md`. Return results as commits on `codex/work` plus the session record; SUP gates and merges.
- Offline work only: research, specs, tests derived from FORMULAS.md, reviews, docs. Changes to `execution/` or `layers/alerts/` are staged as `<file>.new` and proposed; claim ownership in SUPERVISOR_LOG first.
- Never stop/restart live processes, touch HALT files, open trades, or read `.secrets/` / `.env`. Testnet only.
- Provenance, gates (`python scripts/dev/run_all_tests.py`) and "Tom is core" apply unchanged.
