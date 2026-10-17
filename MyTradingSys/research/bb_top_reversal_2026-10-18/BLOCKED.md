# BLOCKED: power gate fails (2026-10-18, card bb-top-reversal-candle-backtest)

Verdict word: BLOCKED. No outcome computed; no bb_top_bt.py written; no VALIDATION/HOLDOUT bar read (count_gate.py loads DEV only, via event_table.load_dev_npz).

Arithmetic (prereg_gate.py): n 759 days, sd 1.5 R, m 58 -> z_holm 3.332, MDE (3.332+0.84)*1.5/sqrt(759) = 0.227 R. Round-trip taker 0.001 / median stop distance 0.002863 = 0.349 R. MDE + cost = 0.576 R > 0.30 R plausible gross. Cost alone (0.349 R) already exceeds 0.30 R, so no sample size passes ("n needed inf"): a 15m red-high stop is ~0.29% away, so 0.10% taker round trip eats 0.35 R.

What would unblock: (a) maker/limit entry and exit modelling with a written fee decision (operator), (b) a wider-stop variant (stop >= ~0.5% so cost <= 0.2 R) as a new pre-reg, (c) an operator overrule of the 0.30 R plausible-gross cap. No parameter search may rescue the gate.

DECISION (OURS, conservative default): BLOCKED, no run. sd = 1.5 is the worst-case bound rather than a scored proxy, to avoid reading outcomes; with sd 1.0 the cost term still blocks.
