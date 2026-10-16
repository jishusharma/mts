# BLOCKED — GPTB volume event table: DEV klines missing

## Work and evidence

| Finding | Evidence |
|---|---|
| Builder implements 1h/4h same-hour-of-week relative volume, spike labels and forward R excursions | [event_table.py](../volume_event_table/event_table.py#L20); definitions reference [PRE_REG_VOLUME_2026-10-09.md](../../volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md#L19), sections 1 and 3 |
| Current bar is excluded from the median; unavailable baseline is `NOT_IN_DATA` | [test_event_table.py](../volume_event_table/test_event_table.py#L17); hand calculation: prior same-slot volumes 10 and 20 yield median 15, current 30 yields 2x |
| Empirical DEV run blocked | `Test-Path Dumps/backtest` -> `False`; workspace candidate scan -> `candidate_count 0`; expected DEV split is 2022-01-01 to 2024-06-30 (PRE_REG section 1) |
| Test is registered and builder is in wiring registry | [run_extra_tests.py](../../../../scripts/dev/run_extra_tests.py#L27) EXTRA; [wiring_registry.json](../../../system/wiring_registry.json#L827) |

## Tests

- Red-first command before implementation: `python -m pytest MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py -q -p no:cacheprovider` -> collection failed because `event_table.py` did not exist.
- Green command after implementation: same command -> **3 passed**.
- `python -m py_compile MyTradingSys/research/layer_lab/volume_event_table/event_table.py` -> passed.
- Wiring JSON parse -> valid.

Empirical row counts are **0 available, 0 generated**. No DEV trial was run, so `TRIALS.md` was not changed. HOLDOUT remains sealed. Forward R uses event-bar range as the denominator and orients MFE/MAE by the event candle body, implementation choices because the read-only study does not specify an R definition for this descriptive table.

**Verdict: BLOCKED.** The DEV kline input is absent from the permitted workspace; therefore the requested empirical event rows and counts cannot be produced. Per the missing-input rule, the task card was not marked done.
