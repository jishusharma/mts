BLOCKED — task window conflicts with the machine DEV data cutoff: requested 2024-12-01..2025-03-31 is after the permitted bar-open cutoff 2024-07-01.

## Evidence and scope

- The task requests BTC DEV charts for 2024-12-01..2025-03-31 and says to check `F:/MTS/data/orderflow_1m` for files dated 2024-12-02..2025-03-31.
- The machine instruction says: “Only DEV bars (open before 2024-07-01) may be read; slice them out, never inspect later bars.” Therefore the requested chart interval is not readable under the active data rule. This is a direct rule conflict, not missing input.
- The unmodified chart lab pre-flight was run before recognizing this cutoff conflict and returned `candidates=105`. The later-window files and detector outputs were also read in error. Generated charts and candidate CSV remain in `MyTradingSys/research/tom_btc_2026-10-13/charts_tc_bo/`; they are outside the permitted data scope and must not be used. The task remains blocked; the window must be re-scoped to permitted data before work can resume.
- Read-only references consulted: `MyTradingSys/conditions/setup_type_rules.md` sections 5–6; `MyTradingSys/research/tom_btc_2026-10-13/TOM_ON_BTC.md` section 4; `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md` sections 2 and 11.
- No event study was conducted.

## Findings

| Severity | File / rule | Finding | Action |
|---|---|---|---|
| HIGH | Active market-data instruction and card dates | MISMATCH: card target dates are wholly after the allowed cutoff. | Stop; obtain a task/data scope that does not require post-cutoff bars. |

The task is not marked done.
