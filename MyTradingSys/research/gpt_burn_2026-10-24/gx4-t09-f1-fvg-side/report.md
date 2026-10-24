# T09 F1: live `volume_fvg` side inversion

## Finding

**HIGH — confirmed.** `MyTradingSys/backtest/layers/alerts/live_layers.py:61` maps a confirmation close above the FVG midpoint to `short`. The tested backtest reading in `MyTradingSys/backtest/layers/fabio/run_backtest.py:199-203` computes `from_above = closes[start] > mid`, then emits bounce as `long` when true. The parity worker reproduces the backtest rule at `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/parity_core.py:~210` (search for `if layer == "fabio" and sub == "volume_fvg"`; it emits `"long" if closes[start] > mid else "short"`). Thus the live FVG event is exactly reversed relative to the bounce reading tested by parity. The audit reports 0 same-side matches among 24 live/backtest signals (`T09_live_parity.md`, section 4 and finding T09-F1).

Reproduce the historical parity result with the audit script from the worktree root (requires its local DEV data): `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/parity_core.py --force`. The isolated fixed-fixture regression is reproducible without network or market data using: `$env:PYTHONPATH='.'; pytest -q MyTradingSys/research/gpt_burn_2026-10-24/gx4-t09-f1-fvg-side/test_volume_fvg_side.py`.

Before-fix test run: **1 failed** at the assertion, actual `short`, expected `long`. Fixture has a confirmation close 10.5 above midpoint 10.0 and a bar touching 10.0. Backtest bounce direction follows from those values: above -> long. Apply `fix.patch` to make the test pass.

The patch changes only the conditional at `live_layers.py:61`, swapping the two side labels. The fixture test monkeypatches the profile dependencies and uses no network.

## Other event-to-side mappings found

Grep-equivalent source scan: `Get-ChildItem MyTradingSys/backtest/layers/alerts -Filter *.py -Recurse | Select-String -Pattern 'side.*long|side.*short|"side"'`. Excluded test-only matches. Adapter source mappings:

- `live_layers.py:37` escalation passes through `escalation_events`' `e["side"]`; consistent with `run_backtest.py`'s escalation events.
- `live_layers.py:61` volume FVG conditional; **inconsistent**, finding above.
- `live_layers.py:74,97,132` session momentum, funding/CVD fade, CryptoCred setups pass through each event's side; consistent with their respective backtest event side fields.
- `live_layers.py:162,164` RSI failure maps resistance failure to short and support failure to long; consistent with the event definitions. Other RSI event classes are deliberately side-less.
- `live_layers.py:185,187` turn-of-candle imbalance maps positive to long and negative to short; consistent with the tested imbalance direction.
- `live_levels_confluence.py:133,145` maps a level reference above/equal to price to long, otherwise short; matches its local documented rule at line 140.
- `live_candle_close.py:94-95` converts side sign (+1/-1) to long/short; consistent with documented side sign convention at line 7.
- `live_bb_top_reversal.py:63` emits short only; consistent with its explicitly one-sided card rule at line 9.
- `live_rsi_divergence.py:50` maps divergence kinds through `SIDE`; no backtest twin is named in T09, so consistency with a tested backtest cannot be established from that parity audit.
- `live_session_levels.py:42` maps via `SIDE`; its module doc at lines 6-7 documents high failed break -> short, low failed break -> long, consistent with its own mirrored event rule.
- `live_runner_cli.py:219,228` converts numeric engine side `+1/-1` to long/short, then attaches it to emitted alerts; consistent with the engine's signed-side convention. `live_runner_cli.py:326,332` assigns WLOW long when its emission flag is enabled, as documented in nearby comments (testnet calibration, not a backtest parity claim).
- `auto_trader.py` does not infer a new event direction: `layer_side` consumes the alert's explicit side (or applies configured event mapping). The historical replay calls that function in `parity_core.py` and the reported mismatch is already present in the live layer alert side.

## Files

- `fix.patch` — minimal unified diff.
- `test_volume_fvg_side.py` — fixed, network-free red regression test.

Result: Confirmed HIGH live volume_fvg inversion; fixed by one-line patch proposal; fixed fixture fails against current code.
