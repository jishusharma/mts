# B081 Fee-source conflict

Opened 2026-10-01. Status OPEN. Severity HIGH.

## Problem

Four different fee sets for the same instrument (Deribit BTC-PERPETUAL) exist in the code. Every layer verdict is unreliable until one is chosen and imported everywhere.

## Known sources

- MyTradingSys/backtest/sim.py:18-20: maker 0, taker 0.05%. Cites "verified 2026-09-26 via public/get_instrument".
- MyTradingSys/backtest/layers/fabio/fabio_of_model.py:40-44: FEE_TAKER=0.00035, FEE_MAKER=-0.00015. Cites "T055b_PROVEN_SETUPS.md fee floor".
- MyTradingSys/backtest/layers/.../run_backtest.py:41: 0.10% flat round trip.
- A fourth set noted in the FORMULA_AUDIT_2026-09-30.md.

## Prior id history

Operator approved the single-source fix under id B080 on 2026-09-30. B080 was subsequently reassigned to the DSA worker pace bug. Re-filed here as B081.

## Proposed resolution

One module: MyTradingSys/backtest/fees.py with FEE_MAKER, FEE_TAKER, and a round_trip_cost() helper. Every backtest imports from it. Verify the live Deribit fee on testnet before choosing the constants.

## Workaround

None. Any backtest run before this is fixed uses an unknown fee regime.
