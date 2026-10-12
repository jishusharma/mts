# Common rules for every revalidation prompt (RV01..RV08)

Why: work shipped 2026-10-11/12 was written, tested and judged by one model family. A second reader re-derives the claims.
Rules live in CLAUDE.md / AGENTS.md; this file only fixes the output.

- Read-only unless the prompt says otherwise: change no code, spec, ledger or holdout. No holdout read, no BTC run of the
  current Tom/Fabio encoding (ROADMAP section 2), no network except where a step names it, no secrets, no live path.
- Every claim is MATCH / MISMATCH / NOT_IN_DATA against a file you opened (path:line or command + output). Nothing from memory.
  A source you cannot reach is NOT_IN_DATA, never a reason to stop.
- Output: ONE report. Run as a card (codex_run / tasks.py): the card's own path, MyTradingSys/research/layer_lab/reports/<UTC date>_<card>.md.
  Run by hand: `MyTradingSys/research/revalidation/<RVnn>_<UTC date>.md`. Either way, with
  1. line 1: `VERDICT: SOUND | FIX-FIRST | BLOCKED` (one word, after the colon)
  2. what was checked: files with line ranges, commands run, data range
  3. findings table: ID | HIGH/MED/LOW | file:line | what is wrong | evidence (quote or number) | proposed fix
  4. `Known-finding check`: each finding listed under "Already known" in the prompt as CONFIRMED / REFUTED / NOT_IN_DATA with evidence
  5. `Not checked`: what you skipped and why
- For each HIGH: `python scripts/dev/tasks.py new "<title>" --lane SONNET --layer <family>` (card id in the report).
- Do not trust the prompt's own "Already known" list: re-derive it. A refuted known finding is a valuable result.
- Hand-off: `tasks.py done <card> --result "<verdict + counts + report path>"`, commit with a `Result:` line, `sync.py ship`.
