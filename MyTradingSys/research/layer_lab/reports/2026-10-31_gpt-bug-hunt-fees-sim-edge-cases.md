# GPT bug hunt: fees and simulator edge cases

FIX-FIRST — invalid fee rates and NaN prices can silently corrupt or suppress simulator results; funding is not modeled by this simulator.

Checked `MyTradingSys/backtest/fees.py:19-49`, `sim.py:44-87`, `test_no_own_costs.py`, `test_sim_planted_edge.py`, and `backtest/layers/FORMULAS.md:350-361`. Synthetic read-only calls: valid profile-B target gives gross 2.0, fee_R .05, net 1.95; negative taker `-.001` gives fee_R -.1 and net 2.1; NaN entry yields no trade; NaN path followed by target yields an apparently valid target (net 1.95). `fees_dict(-1, NaN, 0, 2)` returns those invalid values unchanged. Independent formula example for funding: long 100→101 with positive funding .0004, fee .001, slippage .0002 gives net .0084; `sim.run` has no funding/slippage arguments.

Detailed reproducing inputs, expected versus actual, line references, and test proposals are in [fees_sim_bug_hunt.md](../test_hunt_2026-10-31/fees_sim_bug_hunt.md). Proposed regression cases are in [proposed_test_fees_sim.py](../test_hunt_2026-10-31/proposed_test_fees_sim.py); they were not executed.

No DEV market data was needed; all reproductions used in-memory synthetic rows. No engine or live-tree files changed.
