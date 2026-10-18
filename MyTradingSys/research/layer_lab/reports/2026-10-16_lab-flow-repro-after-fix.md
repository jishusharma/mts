# lab_flow repro after hardening (2026-10-16)

Re-ran the four cases of `2026-10-16_claude-recipe-pilot.md` (G1-G4) against `scripts/dev/lab_flow.py` as on fast-track,
in throwaway temp repos (`tasks.REPO` patched, a one-file scope, the same edits as the pilot). No model stage run.

| ID | Edit applied | Before (pilot report) | After |
|---|---|---|---|
| G1 | extra `--range holdout` command added to a launched run-review card | gate `[]`, contract unchanged | refused: `flow contract commands changed; launch a new flow` |
| G2 | stage 2 `depends_on: []`, `state: ready` | gate `[]`, runnable | refused: `flow depends_on must equal ['rp-1-map']` |
| G3 | stage 2 finished with stage 1's report | accepted | refused: `report already used by rp-1-map` |
| G3b | report without a line naming the card id | accepted | refused: `report must contain a line naming card id` |
| G4 | report with only `C1: PASS` / `C2: PASS` | accepted | refused: `report needs at least one path:line or fenced command evidence token per criterion` |

Result: all four gaps refused. Fail-first: with `lab_flow.py` from `e677a279^` the four new tests in
`scripts/dev/test_lab_flow.py:150-181` fail (4 failed, 16 passed); with the current file 20 passed.
Existing receipts (`recipe-pilot-*`) still pass `lab_flow.accepted` per the Codex report.
Note: the Codex attempt's BLOCKED verdict came from an unrelated sandbox cleanup test (WinError 32); the edits were
already on fast-track in that commit. Card closed from the Claude lane after the quick suite.
