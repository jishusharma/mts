BLOCKED — The BTC 1h cache exists, but preregistration cannot pass validly for the requested outcome: `prereg_gate.py` requires per-event SD in R, while this task defines fixed-horizon percentage returns and no stop/risk unit. A placeholder gate run returned PASS but is explicitly invalid and cannot authorize outcome access. No klines/outcomes were read; no study results or export were produced. See `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md` and `scripts/dev/prereg_gate.py`.

## What was checked
- `python scripts/dev/verdicts.py check "sweep low win-back"` — no prior matching variant.
- `python scripts/dev/prereg_gate.py --n 912 --sd 1.4 --cost 0.0 --m auto --new-cells 1 --sd-source "MyTradingSys/system/LAYER_LAB.md:58"` — PASS, MDE 0.203 R, but inputs are invalid for this study; `sd` is not measured and this task has no R definition.
- Confirmed the specified `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` exists; did not load or inspect arrays.
- The earlier 2026-11-04 report incorrectly treated the absent study directory as a data block. This report replaces that rationale: the data is present; the exact blocker is the incompatible preregistration gate input.

## Findings

| Severity | Location | Finding | Evidence | Resolution |
|---|---|---|---|---|
| HIGH | `scripts/dev/prereg_gate.py:3-8, 25-26` | Gate requires a measured per-event SD in R; requested fixed-horizon returns do not define R. | CLI docs specify SD in R, and the `sd <= 1` guard requires a measured source. | Define risk unit and source a pre-outcome SD, or adapt the prereg gate to return units before outcomes are opened. |
| MED | `MyTradingSys/research/v_recovery_low_sweep_2026-11-04/PRE_REG.md` | Regime mix cannot be supplied from a frozen context definition; no regime split was requested and no as-of regime inputs were preregistered. | PRE_REG records regime mix as NOT_IN_DATA for this design. | Freeze context/regime inputs if required for the study. |

No test was run and no DEV/VAL outcome or sim_desk export was produced. No follow-up card created. Card remains not done because the specified pre-outcome gate is unresolved.
