# Simulator validation: planted edge, fee-including null, trade-list diff (q16)

Card: simulator-validation-planted-edge. Test: `MyTradingSys/backtest/test_sim_planted_edge.py` (new). `tom_bt.py` and `fees.py` read only.
Run: `python -m pytest MyTradingSys/backtest/test_sim_planted_edge.py MyTradingSys/backtest/test_tom_bt.py -q` -> 34 passed.

## Result
- Trades matched 20 of 20 against a hand-built list (`test_trade_list_matches_hand_built_20_of_20`): reason, gross_r, net_r, fee_r,
  fill_i, exit_i, bars_held, ambiguous, zone_tf, all equal (floats within 1e-9).
- Planted edge: 12 target + 8 stop (2 of the 8 are both-touch bars). Recovered mean net R = 1.38 exactly (hand: (12*3 - 4*1.0495 - 4*1.0505)/20).
- Fee-including null (same 20 signals on flat noise, all time out): mean gross 0.0, mean net -0.05 R = minus the round-turn fee in R
  (0.0005*100/1 long, 0.0005*200/2 short; maker entry 0). All-taker profile: -0.10. Both within 1e-9 (spec asked 0.01).
- Verdict: no simulator defect found. tom_bt.sim_limit_trade/run_variant agree with FORMULAS.md 18.5 on every constructed case
  (stop-first on both-touch, fill-bar stop only, maker target 0 fee, taker stop/timeout fee, short mirror).

## Hand arithmetic (also in the test docstring; net_R = (side*(exit-L) - fee_in*L - fee_out*exit)/R, FORMULAS.md section 18.5)
| case | gross R | fee R | net R |
|---|---|---|---|
| long target 100/99/103 | +3.0 | 0 | +3.0 |
| long stop | -1.0 | 0.0005*99/1 = 0.0495 | -1.0495 |
| short target 200/202/194 | +3.0 | 0 | +3.0 |
| short stop | -1.0 | 0.0005*202/2 = 0.0505 | -1.0505 |
Sum 12*3 + 4*(-1.0495) + 4*(-1.0505) = 27.6, mean 1.38.

## Mutation proof (tests fail on a planted defect; command: edit one line of tom_bt.py, run, `git checkout` it back)
- `run_variant(... stop_first=True` -> `False`: 3 tests fail (`test_trade_list_matches_hand_built_20_of_20`,
  `test_both_touch_bars_resolve_to_the_stop`, `test_recovered_mean_net_r_equals_hand_value`: 1.785 != 1.38); the diff is on trade
  indices 6 and 11 only, the two both-touch bars.
- `fee_r = (fees["entry"] * entry + fees[kind] * px) / risk` -> exit fee removed: 5 tests fail (both null tests, per-trade fee test,
  planted list and mean).
- In-suite: `TestPlantedDefects` runs the same two mutations on an in-memory copy of tom_bt.py and asserts the failures, so the
  proof reruns on every CI pass (mutation anchor drift fails loudly).

## Parameters
| parameter | label | source |
|---|---|---|
| fee rates maker 0.0 / taker 0.0005 | SOURCED | `MyTradingSys/backtest/fees.py:23-24` (API-verified 2026-09-26) |
| resolution rules (stop first, fill-bar stop only, gap -> open) | SOURCED | `tom_bt.py:10-17`, FORMULAS.md 18.5 |
| geometry 100/99/103 and 200/202/194 (3R, 1R), 12/8 split, block 100 bars | OURS | synthetic by construction |
| null noise +-0.3, timeout-bar close +-0.1 alternating | OURS | keeps price inside stop/target and gross sum 0 |

## Not covered (out of scope for this card)
`min_width` gate, `slip`/`slip_pts`, `through_ticks`, no_fill/ran paths inside run_variant, one-at-a-time blocking (the last is in
test_tom_bt.py:149). Real data, VALIDATION and HOLDOUT untouched.
