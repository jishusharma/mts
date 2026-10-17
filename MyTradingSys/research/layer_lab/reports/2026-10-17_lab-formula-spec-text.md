# Lab formula spec text

## Verdict

BLOCKED — implementation and static coverage check are complete (23/23), but the task cannot be marked done until the card's required reviewer sign-off is recorded.

## Work and evidence

- Read `MyTradingSys/backtest/layers/FORMULAS.md` (23 numbered entries, lines 10–553) and created `MyTradingSys/backtest/layers/FORMULAS_SPEC.md` (coverage inventory and conventions, lines 1–18; F01–F23 entries, lines 20–203).
- The spec states formula inputs, bar/record availability and alignment, precision/rounding, and undefined/edge behavior. Multi-part catalogue entries have explicit sub-entry headings: F11.1–F11.8; F18.1–F18.7; F19.1–F19.8; F20.1–F20.4; F21.1–F21.9.
- Tags distinguish SOURCED definitions from OURS choices. Worked calculations appear under every top-level ID; subformulas also have their own examples.
- DEV tape source: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, restricted to opens 2024-06-30 20:00 through 23:00 UTC, all before the 2024-07-01 cutoff. Tape and field values are recorded in FORMULAS_SPEC.md lines 7–9. No post-cutoff rows were read.
- Static coverage check command:
  `python -c "from pathlib import Path; import re; f=Path('MyTradingSys/backtest/layers/FORMULAS_SPEC.md').read_text(encoding='utf-8-sig'); ids=[f'F{i:02d}' for i in range(1,24)]; missing=[x for x in ids if not re.search(r'^## '+x+r'\\b',f,re.M)]; print('catalogue_ids=23 missing=',missing,'spec_numbered_headings=',len(re.findall(r'^## F\\d{2}(?:\\.\\d)?\\b',f,re.M))); assert not missing; assert all('Worked' in f[f.index('## '+x):f.find('\\n## ',f.index('## '+x)+1) if f.find('\\n## ',f.index('## '+x)+1)>=0 else len(f)] for x in ids)"`
- Result: `catalogue_ids=23 missing=[] spec_numbered_headings=23`; all 23 top-level sections contain a `Worked` example. The check is an inline static validation rather than a persisted test file because the card scope permits only the new spec and this report.
- Completion command attempted: `python scripts/dev/tasks.py done lab-formula-spec-text --result "23/23; MyTradingSys/research/layer_lab/reports/2026-10-17_lab-formula-spec-text.md"`.
- Exact refusal: `tasks: lab-formula-spec-text cannot be marked done: weight/class needs review: add 'REVIEWED: <reviewer> <date>' to the note first`.
- The reviewer's sign-off is unavailable in this unattended session; the card remains not-done. No sign-off was added or inferred.

## Findings

| Severity | Location | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| BLOCKING | Task card `lab-formula-spec-text` | Done-state review gate is unsatisfied. | `tasks.py done` returned the exact refusal above, requiring `REVIEWED: <reviewer> <date>`. | Obtain the required review and sign-off, then rerun `tasks.py done`. |
| LOW | `MyTradingSys/backtest/layers/FORMULAS_SPEC.md:7` | Several formula-specific DEV calculations use explicitly stated shorter windows or inputs as hand examples; they do not claim a full detector event or production warmup. | The spec calls out illustrative/insufficient warmup cases where applicable. | Preserve these qualifications when extending examples to full event fixtures. |

## Follow-up cards

None.
