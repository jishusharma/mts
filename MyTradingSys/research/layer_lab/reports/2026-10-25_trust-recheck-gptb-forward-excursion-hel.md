# Trust re-check: gptb-forward-excursion-helper

**Verdict: BLOCKED ? the required different-vendor review cannot be supplied in this unattended Codex session.** The producer registry identifies the build as CODEX with model `gpt-6-luna` (OpenAI); the available reviewer here is Codex / GPT-6.1-Sol (OpenAI), the same vendor. The read-only context pack explicitly requires a Gemini or Claude reviewer. I therefore make no VERIFIED-C2 proposal and do not mark the task done. Calculations and test evidence below are recorded for a future qualifying reviewer.

## Scope and provenance checked

- `MyTradingSys/system/tasks/archive/gptb-forward-excursion-helper.json`: goal and producer model (`gpt-6-luna`); producer is CODEX/GPT. The trust-tag report lists this card as a C2 candidate requiring an independent review.
- `MyTradingSys/research/layer_lab/forward_excursion/REPORT.md`: contract says entry close, subsequent-bar horizon, excursions in R, same-bar stop priority (OURS), and no market data.
- `MyTradingSys/research/layer_lab/forward_excursion/event_table.py:4-51`; `test_event_table.py:11-51`; producer report `MyTradingSys/research/layer_lab/reports/2026-10-16_gptb-forward-excursion-helper.md`.
- The pack names `MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-gptb-forward-excursion-hel.md`, but that file is absent in this checkout. No market data, outcome, or holdout rerun was used.

## Independent calculations (synthetic bars)

Entry close = 100 and R = 2 in each case; the forward bar has high 103 and low 97, as applicable. Arithmetic is measured from entry close. The script called the function directly from `event_table.py`.

| Case | Hand calculation | Function output | Finding |
|---|---|---|---|
| Long reaches target only: H=103, L=100 | MFE=(103?100)/2=1.5R; MAE=0R; target reached first | `mfe_r=1.5`, `mae_r=0.0`, `first_hit=target_1R`, `truncated=False` | MATCH ? `event_table.py:30-44`; semantics: card goal in `gptb-forward-excursion-helper.json` |
| Short reaches stop only: H=103, L=100 | MFE=max(0,(100?100)/2)=0R; MAE=(103?100)/2=1.5R; stop reached | `mfe_r=0.0`, `mae_r=1.5`, `first_hit=stop_1R`, `truncated=False` | MATCH ? `event_table.py:30-44`; semantics: card goal in `gptb-forward-excursion-helper.json` |
| Long same bar touches both: H=103, L=97 | MFE=1.5R; MAE=1.5R; OURS rule resolves first hit to stop | `mfe_r=1.5`, `mae_r=1.5`, `first_hit=stop_1R`, `truncated=False` | MATCH ? `event_table.py:39-44`; spec `forward_excursion/REPORT.md` |

## Test and mutation evidence

- Baseline: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q` -> **5 passed** (one environment cache warning).
- Test review: the dedicated both-touch assertion at `test_event_table.py:32-35` requires `stop_1R`; it detects a target-first regression. The long/short fixture assertions at `:22-29` also check exact excursion numbers and target semantics.
- Scratch mutation: reversed the two first-hit branches (target check before stop) in a temporary copy of `event_table.py`, leaving the audited source and test unchanged. Command: pytest on the scratch copy with `-q -p no:cacheprovider` -> **1 failed, 4 passed**; `test_same_bar_touching_both_levels_counts_stop_first` failed because the mutant returned `target_1R`. Mutation killed.

## Finding and tag proposal

| Severity | Evidence | Finding | Proposed action |
|---|---|---|---|
| HIGH | Producer model: archive task JSON; different-vendor requirement: supplied context pack; reviewer in this session is OpenAI GPT-6.1-Sol | Vendor independence is not met, despite the three source calculations matching and the both-touch mutation being killed. | BLOCKED; obtain the required Gemini or Claude re-check before proposing VERIFIED-C2. |

**Tag proposal:** none pending a qualifying different-vendor review. This report does not record DISPUTED because no source mismatch was found; no trust tag should be advanced from this same-vendor review.

