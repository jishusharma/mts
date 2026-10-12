# RV07 [MED] Layer tooling: LAYERS.md, layer_index.json, layer_map, tasks --layer, shot.py finding:card (dc3afe4, caaa393, bd4b3c1)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV07. Report: `MyTradingSys/research/revalidation/RV07_<UTC date>.md`.

Scope in: scripts/dev/make_layers_md.py, make_layer_map.py, layer_map.tpl.html, tasks.py (layers, CODEX_KINDS, lint), shot.py
(outcome_exists, done), MyTradingSys/system/LAYERS.md, layer_index.json, layer_map.json, artifacts/layer_map.html and their tests.
Scope out: edits; republishing the Control Room or the artifact.
Why: these are the navigation layer every session reads first; a wrong row sends work to a wrong file.
Checks: (1) every path in layer_index.json / layer_map.json / LAYERS.md exists (mechanical); (2) each layer_map backtest row: open its
report and compare `verdict`, `n`, `effects` with the report text; sample all 12 rows added in bd4b3c1 (Q42); (3) tasks.py: a card
whose `layers` names a missing family, circular depends_on, a CODEX card with no kind; (4) shot.py `done`: ids that substring-match
(`FEAT-1` against FEAT-11 via `git grep -F`), `note:` and `feature:` outcomes on a shot with MISMATCH claims, card id of a card
that exists only in another worktree; (5) artifact HTML vs JSON: same row count, no stale embedded copy.
Already known (confirm or refute): (a) `shot.py done --outcome note:"<8+ chars>"` closes a shot with MISMATCH claims, only
`noaction:` needs 20+ chars (shot.py:527); (b) `outcome_exists` for F-BT-/FEAT- tokens is a `git grep -F` substring (shot.py:503).
