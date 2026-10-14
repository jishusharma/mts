# tom-v2-btc-min-stop-width — 2026-10-14

Verdict: BLOCKED

## What was checked

- `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_V2.md`: NOT_IN_DATA. `Test-Path` returned `False`; the file is absent.
- `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:312-324`: MATCH — section 11.4 specifies the noise and fee floors, and BTC enforcement.
- `MyTradingSys/system/LAYER_LAB.md` and `MyTradingSys/system/LAYERS.md`: MATCH — research-only layer lab scope and Tom references reviewed.

## Findings

| Severity | Evidence | Finding | Required next step |
|---|---|---|---|
| HIGH | `Test-Path MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_V2.md` → `False` | The task explicitly requires starting only if `DAX_BT_V2.md` says PASS. The required gate result is missing, so implementation is blocked pending that file and its PASS verdict. | Supply the DAX_BT_V2 result with PASS, then rerun this card. |

No code or tests were changed or run. No BTC backtest was run. No lookback 10/20/40 floors were computed because the start condition failed. The card was not marked done.

## Follow-up cards created

None.
