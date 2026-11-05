# PRE_REG — BTC 5-day-low sweep and 50% recovery

Status: BLOCKED before outcome inspection. Scope is the DEV window only (bars opening before 2024-07-01); VAL is 2024-07-01 through 2025-06-30 and would be opened only after the frozen DEV event definition and survivors. No holdout bars are permitted.

## Context
- Regime: none; descriptive event study, no regime filter.
- Phase: sweep then recovery, as defined below.
- Session: none; all UTC hours.
- Entry: event timestamp is the close of the first 1h bar whose low is below the minimum low of the preceding 120 complete 1h bars, and whose close is at least halfway from that prior low to the sweep bar's low. If the close condition is not met, recovery may occur at a later 1h close no later than three hours after the sweep bar's close. A bar's high is not used to infer recovery. Non-overlapping events: after an event, resume scanning after its recovery bar.
- Regime mix: all eligible weeks; descriptive only. Required bull/bear/range mix is NOT_IN_DATA for this prereg because the study has no regime tagging specification or as-of daily/weekly/monthly regime inputs frozen. No bars/outcomes inspected.

## Frozen outcome plan
For each event, calculate close-to-close BTC returns from recovery close to the 4h, 24h, and 72h closes. Fees: round-trip taker cost from the repository's documented BTC fee constant, reported in percentage points; include gross and fee-net mean, median, n, and 95% bootstrap CI, clustered by UTC day. Report DEV and then the same fixed event rule on VAL survivors. No tuning, subgroup selection, or holdout access.

## Preregistration gate
`python scripts/dev/verdicts.py check "sweep low win-back"` returned no prior matching row. `python scripts/dev/prereg_gate.py --n 912 --sd 1.4 --cost 0.0 --m auto --new-cells 1 --sd-source "MyTradingSys/system/LAYER_LAB.md:58"` returned PASS (MDE 0.203 R, m=127). This invocation is not valid evidence for this study: `prereg_gate.py` requires per-event standard deviation in R, but the task defines no stop, risk unit, or R conversion. The supplied 1.4 was only a generic placeholder range in gate documentation, not a measured study input. Therefore the gate's numeric PASS cannot authorize outcome inspection; the gate is unresolved for this outcome definition.

## Blocking issue
No pre-outcome, valid per-event R standard deviation or risk-unit definition exists for the specified fixed-horizon return study. Using outcomes to estimate it would violate the preregistration-before-run requirement. Resolve by defining a risk unit and providing a pre-outcome SD source, or revising the required gate for return-based descriptive studies. No market outcomes were opened.
