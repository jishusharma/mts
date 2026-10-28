# Claude spot-check of the reusable lab recipes (2026-10-16)

Reviewer: Claude (Sonnet 5.5) in session autopilot-3, JIS-NB, 07:11Z to 07:16Z. No subagents, no UI control, no
holdout or market data, no model stage re-run. Read: `LAB_RECIPES.md`, `lab_flow.py`, `test_lab_flow.py`, both pilot
reports, the pilot summary, both card receipts.

## Verdict

**Plumbing: PASS. Use on real MTS research: FIX-FIRST (four gaps, one scoped card).**
The ordered Sol -> Astra flow does what the summary says, and the checks that exist work. The contract does not yet
cover everything the recipes promise: the run-review rule "execute only the supplied commands" and the stage order can
be changed by editing a card file, and a stage can pass with another stage's report. None of this needs hostile
intent; a model editing its own card, or a copy-paste, is enough. The fixes are small (card `lab-flow-contract-hardening`).

## Checks

| Check | Result |
|---|---|
| `pytest scripts/dev/test_lab_flow.py test_tasks.py test_codex_run.py test_codex_pack.py -q` | 104 passed, 232 subtests, 16.75 s (matches the summary) |
| Recompute the pilot claim: 10 + 11 + 9 (`pilot-facts.md:3`) | sum 30, mean 10; claim A (31) is a MISMATCH, claim B (10) MATCH. Both model reports say the same. |
| One receipt hash: `recipe-pilot-1-map` | stored `962df31fa815c0db018d2faaf75c2e05b1ab965fb71c2cf37cc5a90b45fa707a` equals sha256 of the report file |
| Stage 2 card | model gpt-6-astra, effort low, crucial true, receipt PASS, criteria PASS, PASS |
| `lab_flow.py status recipe-pilot` | both cards done / PASS |
| Criteria coverage | C1 and C2 each have evidence in both reports (sum/mean recomputed, fee claim NOT_IN_DATA with `pilot-facts.md:4`) |

Disagreements with the summary: none on the numbers. One claim is narrower than it reads: "goal, scope, lens or model
drift ... stop advancement" is true for goal, scope_in, criteria, kind, model and lens, but not for the other card
fields (see G1, G2).

## Findings (each reproduced in a throwaway repo with the repo's own `tasks`/`lab_flow` modules)

Repro: launch the recipe from `test_lab_flow.py`'s `spec()` into a temp dir, then apply the edit named below.

| ID | Severity | What happens | Reproduced output |
|---|---|---|---|
| G1 | high for run-review and build-review | `contract()` hashes only id, recipe, goal, criteria, scope_in. `commands` (run-review) and `tests` (build-review) are card fields outside it. Adding `python study.py --range holdout` to the run card's commands after launch changes nothing the gate checks. | `gate()` returned `[]`, `problems()` returned `[]`, contract hash unchanged (True) |
| G2 | medium | `gate()` only walks `depends_on` if present. A stage-2 card edited to `depends_on: []`, `state: ready` is runnable without a stage-1 receipt. | stage 2 in `ready_cards`: True; `gate()` returned `[]` |
| G3 | medium | `finish()` takes any lab report path. Stage 2 finished with stage 1's report path and was accepted, so the "independent challenge" can be satisfied by a file it did not write. | stage 2 `done`, receipt report = the stage-1 report |
| G4 | low (documented as attestation) | A report holding only `C1: PASS` / `C2: PASS` lines is accepted. | accepted |

What the existing checks do well (tested, not just read): `tasks.py done` on a flow card is refused; a bare `done`
state does not unlock the next stage; changing a scope file or the predecessor report blocks stage 2; an observed
model mismatch revokes the receipt; unsafe scope paths (`..`, `.env`, `execution/`) are rejected; preview writes nothing.

## Proposed fix (card `lab-flow-contract-hardening`, lane CODEX, build, prio 2)

G1: include `commands` and `tests` in the contract only when non-empty (the stored recipe-pilot hashes stay valid).
G2: for stage > 1 require `depends_on == [previous stage card]`. G3: `finish` refuses a report already used by any
other receipt and requires a line naming the card id. G4: at least one `path:line` or fenced command per criterion.
Tests fail first on the current code. Existing receipts must still pass `lab_flow.accepted`.

## Measured usage

Stage runs (from the summary's table, which reads the runner's `runs.jsonl` on the lab host; I did not have that file
here and did not re-measure): Sol/medium 73 s, 271,628 tokens; Astra/low 115 s, 439,278 tokens; total 710,906 tokens
over 188 s, of which 615,040 cached (86.5 %), 91,229 uncached input, 4,637 output. Pack size 13,837 -> 2,270 bytes
(-83.6 %) is as the summary states and measures the initial pack only. My own check used the deterministic tests and
a four-case script, no model stage; Claude token usage for this review was not separately measured.

## Next pilot (recommendation)

One real, already-written MTS report with numbers that can be recomputed from committed tables, using
`critical-audit` after the hardening card ships:

- Target: `research/imbalance_qriptal_2026-10-16/filter/RESULT.md` (imbalance filter, FAIL), scope_in = that file, its
  PRE_REG.md and its committed counts/tables only.
- Criteria: (1) the headline cells -0.366 R / -0.467 R / +0.101 R reproduce from the committed counts; (2) the DEV-only
  statement holds, no VALIDATION or HOLDOUT file in the inputs; (3) the touch-bar look-ahead defect the report lists is
  reproduced on a handful of committed rows and its effect on the HOLD rates is stated (feeds Q79).
- Lenses: Sol maps claims to evidence, Astra tries to falsify; deterministic recompute first so the models only get the
  findings that could change a decision. No market rerun.
- Do not use run-review for real work until G1 is fixed: its safety rule is the one G1 breaks.

Disagreements still open: none. Review status: Claude spot-check done; the lab owner decides the follow-up card.
