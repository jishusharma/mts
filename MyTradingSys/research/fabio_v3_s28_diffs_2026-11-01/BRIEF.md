# Brief: Fabio v3 code vs FORMULAS.md s28.6 (planner 2026-11-01)

Card: fabio-v3-code-vs-formulas-s28-diffs. Code: `MyTradingSys/backtest/layers/fabio/v3/`. Spec: `layers/FORMULAS.md` s28.
IS/DEV only. No engine wiring, no backtest rerun, simulate_trade one-leg contract unchanged.

## Decisions (OURS, planner 2026-11-01)
| # | Difference | Resolution |
|---|---|---|
| 1 | balance/atr need [i-N, i] contiguous, spec says [i-N+1, i] | Amend the SPEC: ATR_N(i) reads TR[i-N+1], which reads c[i-N]; fail closed on a gap |
| 2 | simulate_trade/walk_trade manage the first leg only | Build `simulate_trade_legs` (name OURS) applying the s28.4 add rules; simulate_trade untouched |
| 3 | day_gate_open closed on empty history or median <= 0 | Amend the SPEC (s28.5): closed, label SAFETY |

## Tests (write first; only T-C is red on the unchanged tree, T-A and T-B pin the amended spec and are proven by the mutation checks; hand numbers from s28)
- T-A (diff 1): s28 6-bar worked example, i=4, N=4: balance {H 102, L 99, R 3, poc 100.5}, ATR 2.25 (TR 3,2,2,2). Same bars with a timestamp gap between bar 0 and bar 1: atr and balance None. Gap between bars 2 and 3: None.
- T-B (diff 3): day_gate_open(60, 800, [1000]*20, 0.8) True; (60, 790, same) False; (60, 800, [], 0.8) False; (60, 800, [0]*20, 0.8) False.
- T-C (diff 2), s28.4 worked add, long, q1 = 1, e1 = 100000, D1 = 300, stop0 = 99700:
  - mode be, stop at 100100, add at pa = 100200: locked 100, dist 100, q_add 1. Stopped at 100100: gross R = (100 - 100)/300 = 0.
  - Fees: leg 1 maker in, taker stop out: (0 + 0.0005)*100000/300 = 0.166667; leg 2 taker in and out: 0.001*100200/300 = 0.334. Net R = -0.500667.
  - stop at e1: q_add 0, no add, result equals simulate_trade. Mode day, closed day R 0.5, D1 300, r1 1: q_add 0.1667 < 0.25, skip. A third add is refused (cap 2).
  - Fee convention (s28.4): fee R = (fee_in + fee_out)*e_k*q_k/(q1*D1) on the ENTRY notional of each leg, also on a stop exit; do not switch to exit notional.
  - Compute every expected number independently of the code.

## Mutation checks (list both results in the Result line)
- atr: contiguous(bars, i - N, i) -> contiguous(bars, i - N + 1, i): T-A must go red.
- day_gate_open returns open on empty history: T-B must go red.

## Done
v3/tests green; FORMULAS.md s28.6 replaced by a RESOLVED line naming the sha; README updated; Result lists golden numbers moved (expected none) and the mutation results.
Verify line: content sha, `git cherry origin/fast-track <sha>` empty, `git ls-tree -r origin/fast-track --name-only` shows the files.
