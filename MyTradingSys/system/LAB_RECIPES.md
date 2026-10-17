# Reusable lab recipes

Operator 2026-10-16: reuse the lab for MTS work, use Sol 6.1 and Astra for critical decisions,
and optimize session tokens without treating economy as a quality cap. This extends LAYER_LAB.md;
its scope, claims, data restrictions and ship gates still apply.

| Recipe | Ordered lenses | Use |
|---|---|---|
| critical-audit | Sol 6.1 / medium evidence map -> Astra / low independent challenge | specs, source ledgers, formula or backtest-method audits |
| build-review | Sol 6.1 / medium implementation -> Gemini 2.5 Pro / low failure-mode review | scoped offline code with fail-first tests |
| run-review | Luna / low mechanical run -> Sol 6.1 / medium numerical verification | supplied DEV commands, recall checks, counts and repeatable research |

These are routing defaults, not claims that one model always wins. Astra retains the existing low-effort
policy; upgrade effort only with measured task evidence and a deliberate policy change. Model guidance:
https://developers.openai.com/api/docs/models (checked 2026-10-16). No voting or averaging verdicts:
disagreements require a source reference or reproduction. Claude spot-checks one material claim and
decides the next research/build action from the final report.

Each recipe stage declares a vendor and model id. Supported vendor labels are `codex`, `gemini`, and
`claude`; a reviewer stage is rejected when its model id equals stage one's producer model id, even when
the vendor labels differ. Gemini stage instructions use `agy.exe --print` and require the complete report
text to be included in the prompt because the headless command cannot read report files. The finish
receipt stores the stage's vendor and model id, and runner acceptance checks them against the recipe.
When adding a Claude stage, supply its model id and headless invocation in that stage's lens/instructions.

## Launch from Claude or Codex

Write a JSON spec, then preview and launch it:

```
python scripts/dev/lab_flow.py launch MyTradingSys/research/layer_lab/examples/pilot-spec.json --preview
python scripts/dev/lab_flow.py launch MyTradingSys/research/layer_lab/examples/pilot-spec.json
python scripts/dev/lab_flow.py status recipe-pilot
```

The example has `id`, `recipe`, `goal`, `criteria`, and `scope_in`. Reuse it with a NEW id, the real
objective and observable acceptance criteria. `scope_in` is an explicit list of existing repo files,
not directory dumps. For run-review supply `commands`; for build-review supply `tests` and every file
that may change (including gate registration). V1 requires existing files: create new-file scaffolds
before launch, or use an ordinary build card. Optional `layers` and `prio` use normal card fields.
Preview writes nothing. A duplicate id refuses without overwriting. Claims and shipping are unchanged.
Commit the spec, generated manifest and cards, then `sync.py ship`; the normal lab scheduler takes them.

Only stage one starts ready. The rest wait blocked. Each brief carries the same goal and numbered
criteria, plus its distinct lens. Packs carry file hashes and predecessor-report pointers, avoiding
duplicated boot documents and source dumps. Open the originals as needed; no evidence is silently cut.
The model must read originals before its predecessor's conclusions to reduce anchoring.

## Evidence and advancement

Write a normal lab report with evidence for every criterion and exactly one standalone status line per
criterion (`C1: PASS`, `C2: REWORK`, or `C3: BLOCKED`). Finish with:

```
python scripts/dev/lab_flow.py finish CARD_ID --report REPORT_PATH --verdict PASS --result "evidence summary"
```

Use REWORK for failed acceptance and BLOCKED for missing required evidence. PASS requires every criterion
line PASS and an existing report under layer_lab/reports. It stores the contract hash, source hashes,
report hash, criterion results, vendor and model id on the card, then unlocks the next stage. A bare tasks.py done is refused.
A changed goal, source file or prior report prevents the next stage from running. Correct the underlying
issue and launch a new flow id against the new evidence; no automatic repair/retry loop burns sessions.
PASS accepts that stage's stated deliverable; it is not a trading recommendation or proof of profitability.
Criterion lines are model attestations backed by the report, not a machine proof of their truth.

The gate also enforces four integrity checks: nonempty `commands` and `tests` are part of the launch
contract; every stage after the first must depend on exactly the preceding card; a report cannot be reused
by another flow receipt and must include a line naming its card id; and each criterion must have a
`path:line` reference or fenced command as report evidence, in addition to its status line.

## Economy and operations

Use deterministic checks first; launch multiple lenses only when the independent check can affect a
decision. Do not ask every model to repeat the entire task. Keep original sources, findings and exact
reproduction commands in files rather than carrying full chat histories. Ordinary cards retain their
existing routing and spend settings. Recipe cards use optimization mode: the old lab-share and run-count
caps do not refuse them; actual plan allowance/headroom, concurrency lock, failure cooldown and platform
limits remain. No new token cap is imposed. Each stage retains the runner's measured model/effort,
cached/uncached tokens, output tokens, duration and allowance movement in lab_runs/runs.jsonl.
Recipe cards are GPT-only, so fallback never silently replaces a promised independent GPT lens with Claude.

Claude's final spot-check should record: criterion coverage, one independently reproduced claim,
disagreements resolved or still open, total stage usage and whether the next multi-lens run is worthwhile.
If Claude's allowance is unavailable, queue the concrete spot-check with paths and defaults; do not claim
that Claude reviewed it. No live orders, holdout reads or production changes are part of this pilot.
