# gptb-forward-excursion-helper

**Built:** `forward_excursion/event_table.py` and its test; test output: **5 passed**.

## What was built and checked

- `MyTradingSys/research/layer_lab/forward_excursion/event_table.py:4-51`: pure helper over supplied OHLC lists; entry is the close of `bars[i_entry]`, and horizon counts subsequent bars. Returns `mfe_r`, `mae_r`, `first_hit`, and `truncated`. Same-bar 1R ambiguity resolves stop first (OURS); `r_price <= 0` raises `ValueError`.
- `MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py:22-51`: five synthetic tests, including six-bar long and short fixtures with hand-computed 2.0R MFE / 0.5R MAE, stop-first ambiguity, truncated horizon, and invalid risk size. No market data rows were read; test fixture row count is six bars per side.
- Gate and wiring registrations: `scripts/dev/run_extra_tests.py:29`; `MyTradingSys/system/wiring_registry.json:834`.
- `MyTradingSys/research/layer_lab/forward_excursion/REPORT.md`: build record.

## Test sequence

- Red: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q` -> collection error, `FileNotFoundError` for the absent implementation.
- Green: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q -p no:cacheprovider` -> `5 passed in 0.07s`.

## Findings

| Severity | Evidence | Finding | Proposed fix |
|---|---|---|---|
| LOW | MATCH - `event_table.py:30-50`; test `:32-42` | Stop-first ambiguity and available-bar truncation are implemented and tested. | None. |

Follow-up cards: none.
