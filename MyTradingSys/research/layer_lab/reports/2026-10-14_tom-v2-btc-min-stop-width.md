# tom-v2-btc-min-stop-width - 2026-10-14

Verdict: BLOCKED - the required DAX_BT_V2 PASS gate is not present.

## What was checked

- `Test-Path MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_V2.md` - `False`; recursive search for `*DAX*BT*V2*` under `MyTradingSys/research` - `NO_MATCH`.
- `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:312-335`: MATCH - section 11.4 defines the 0.88-N5 noise floor, fee floor, no-trade rule, and worked example.
- `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:93-108`: MATCH - this is a DAX report with proof-ceiling limitations; it does not provide the required `DAX_BT_V2.md` PASS verdict.
- `MyTradingSys/backtest/tom_bt.py`, `scripts/dev/tom_noise_units.py`, `MyTradingSys/backtest/fees.py`, `MyTradingSys/tests/test_tom_noise_units.py`: reviewed to identify the requested implementation surface; no changes made.

## Findings

| Severity | Evidence | Finding | Required next step |
|---|---|---|---|
| HIGH | `Test-Path .../DAX_BT_V2.md` - `False`; recursive search - `NO_MATCH` | The task says to start only if `DAX_BT_V2.md` says PASS. That gate artifact is missing, so implementation and data reporting cannot proceed. | Provide the required gate artifact with PASS, then rerun this card. |

No code or tests were changed or run. No BTC backtest was run. The 2026-06-25 lookback 10/20/40 N5 floors were not computed. The task card was not marked done.

## Follow-up cards created

None.
