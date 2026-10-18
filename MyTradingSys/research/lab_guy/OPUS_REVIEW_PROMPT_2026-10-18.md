# Opus review prompt: trust tag and what past work needs the gate (2026-10-18)

Paste into a session set to Opus. Read-only: change nothing, ship nothing. Repo MTS, trunk `origin/fast-track` (use `git show origin/fast-track:<path>`). Be critical, no praise, at most 700 words, say what you could not verify, cite file:line.

SUBJECT: a "safe to build on" tag for lab results, and which past work must pass it.
Read in this order: `MyTradingSys/system/roles/lab_guy.md` (v3.1: E1-E7 errors, classes C0-C3, Claude's role, trust tag, Q76 experiment), `MyTradingSys/system/tasks/lab-trust-tag.json`, `scripts/dev/tasks.py`, `scripts/dev/lab_flow.py`, `MyTradingSys/system/LAB_RECIPES.md`, `LAYER_LAB.md`, `session_planner.md`, `TASK_REFINEMENT.md`, `MyTradingSys/research/layer_lab/INDEX.md`, `MyTradingSys/research/layer_lab/reports/2026-10-18_q76-dev-ext-power-check.md`, `MyTradingSys/research/pit_levels_2026-10-16/PRE_REG_V2.md`.

QUESTIONS:
1. WIRING (most important). Does the concept exist in the code today or only in prose? For each of: weight field, `REVIEWED:` stamp, receipt fingerprint, flow stage vendor, citation of another card in `scope_in`, trial ledger, data hash: say where it is read or enforced (file:line) or that nothing reads it. Where would the tag be written and where read so a card cannot start on a weaker result? List every place a card can start (tasks.py next, sync.py claim, codex_run.py, relay, session_planner dispatch, desk) and say which would bypass a gate placed in only one of them.
2. PAST WORK. Go through finished and shipped lab and research results that later work stands on: the layer_lab INDEX deliveries (event tables, formula re-derive, blindness audit), the power-gate chain (COUNT.txt, B187, PRE_REG_V2), fee/fill/cost model, FORMULAS.md, data under F:/MTS/data, the verdicts and trial ledger. For each base result give: what stands on it, which error classes (E1-E7) it could hide, its current trust level (UNCHECKED, MACHINE-OK or better, with evidence), and whether it must be RECREATED or RE-CHECKED before anything more is built on it. Rank them by how much stands on them. Do not re-run analyses; name what you could not check.
3. Which of these would you rebuild from scratch rather than patch, and in what order, so that new work is built only on tagged results? Give the smallest set that restores trust.
4. Is the tag itself sound: expiry rules, who may set it (never the producer), how it handles a result that cites data later found wrong, and what it cannot tell us? What is the main way it could create false safety?
5. Cost: how many review runs does the retro-audit of past base results need, in which pool, and what is the cheapest first batch.
6. Anything in lab_guy.md v3.1 that contradicts the code or another document.

End with: the first three cards you would file, in order, each with lane and done condition.
