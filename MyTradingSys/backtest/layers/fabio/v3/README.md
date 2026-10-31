# Fabio v3 core (FABIO_V3_SPEC.md v3.1)

Layer module: location -> context -> trigger -> management, for the NY 390-minute window on 1m order-flow bars.
Spec: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md` (sections 2-7, test plan section 10).
Status: PROMOTED 2026-10-02 (eddd237). v3 tests pass; not yet in the gate.

## Modules
| file | spec | contents |
|---|---|---|
| `signals.py` | 3 | S1 balance, S2 pressure, S3 effort_result/effort_arrays, S4 big_push + volume_tier, S5 breakout, S5D failed_auction, S6 control_level, S7 curve, S8 exhaustion, S9 defended_level, profile/VA/LVN maths |
| `costs.py` | 5.3 | TICK, EPS, fees (from `backtest/fees.py`, B081), `leg_r`, `funding_r` |
| `fill.py` | 5.1 | `fills_in_bar`, `find_fill`, `taker_fill`, `missed_winner` |
| `manage.py` | 5.2 | `be_update`, `trail_update`, `opp_stop`, `add_size`, `add_allowed`, `walk_trade`, `simulate_trade` (first leg only) |
| `day_gates.py` | 2, 6 | NY/London/Asia opens, `US_CLOSED`, `window_bars`, `first_leg_allowed/risk`, `day_gate_open`, reporting helpers |
| `models.py` | 4 | trade functions `model_a_trade`, `model_b`, `model_c`, `model_d_trade`; scanners `scan_model_a/b/c/d` |
| `engine.py` | 4 | `run(bars, config)` |

## Engine
`run(bars, config) -> {verdict, model, side, entry, stop, target, management, diagnostics}`. State is reported as of
bar `config["as_of"]` (default last); later bars are never read. `verdict` is a section-4 state:
IDLE | IMPULSE | PROBE | ARMED | SIGNAL | IN_TRADE | DONE. The first model in `config["models"]` (default A, B, C, D)
that fires (ARMED, SIGNAL, IN_TRADE, DONE) is reported, else the most advanced non-firing state.

Required config (NS-grid, no defaults): `N, p, z_hi, m_c, f, g, entry_mode, mgmt` (+ `be_k` when `mgmt == "dist"`).
Optional: `k_bal` 0.8, `bin_size` 50, `open_idx` 0, `as_of`, `models`, `target_mode` ("edge"), `slip_bps`, `tier`,
`prior_vols` (S4 tier), `prior_ranges` (callable `elapsed -> list`, day gate).

## Tests
`tests/*.py.new` (93 tests): costs+fill, day gates, management, signals, models+engine. Expected numbers come from the
spec test plan (T-ids in comments) or hand arithmetic written next to the assert; none from repo code. Staged run:
copy `tests/*.py.new` to `*.py` next to promoted modules (imports are
`MyTradingSys.backtest.layers.fabio.v3`). Before promotion they were run through a scratch import hook that serves the
`.py.new` files under that package name (not in the repo). Fail-first: with the modules absent, collection fails.

## Open items / unknowns (not guessed)
- `engine.py`: `prior_ranges` container shape; one S4 tier for the whole replay; model A `confirm`
  IN_TRADE is reported without management (the scanner does not return what the trade function needs);
  `open_idx` default; verdict when nothing is mid-state is IDLE with model None.
- `manage.py`: multi-leg adds are not executed (`add_allowed`/`add_size` are decision helpers only).
- `models.py` docstring lists the readings of the spec made for model A impulse step, model A confirm touch rule,
  model B probe extreme and the entry gate.
- Spec items still to VERIFY on desktop: Deribit tick and basis (spec :33), `US_CLOSED` dates (spec :46), the
  TRIAL_REGISTRY rows before any run (spec 7.2). Not covered by tests: T46, T47, T55-T56, T59, model A LVN state
  machine (T35 IMPULSE/ARMED scan), `curve`, funding window end-to-end.
- fees.py import sets `sys.dont_write_bytecode = True` process-wide (see `costs.py`).
