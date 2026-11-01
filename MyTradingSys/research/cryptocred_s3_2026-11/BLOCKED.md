# BLOCKED: power gate fails (2026-11-01, card cryptocred-4h-1d-dev-s3)

Verdict word: BLOCKED. No outcome computed: no bar was loaded, no trade simulated, no VALIDATION/HOLDOUT bar read. `cc_s3_run.py` is built and tested but was never run on data.

Arithmetic (`python scripts/dev/prereg_gate.py --n 207 --sd 1.24 --cost 0.068 --m auto --new-cells 6`, exit 1): n 207 fills (4h Setup 1, PRE_REG item 3, UNCHECKED-BASE), sd 1.24 R, m 111 (105 prior DEV variants from `verdicts.py count --split DEV` + 6 new 4h cells: Setups 1,2 x trials 1,4,5), z_holm 3.509, MDE (3.509+0.84)*1.24/sqrt(207) = 0.375 R. Cost 0.068 R (PRE_REG item 6, OURS-UNREPRODUCED). MDE + cost = 0.443 R > 0.30 R plausible gross; n needed 540. Setup 2 (n 200, cost 0.061 R) is the same. Even with m = 1 the gate blocks (MDE 0.241 + 0.068 = 0.309 R > 0.30; n needed 224).

sd 1.24 is hand-computed from the pre-registered 1.5 R bracket at breakeven p = 0.427: sqrt(0.427 x 1.5^2 + 0.573 x 1^2) = sqrt(1.534) = 1.24 R (two-point, no outcome read).

Why a recount does not unblock: a resting limit fills on the level alone (`run_cc_setups.find_limit_fill`), so the new ATR stop does not change which limits fill; N stays about 207 / 200 (PRE_REG "Provenance": N is re-counted, and it falls short of 540 either way). The PRE_REG already says power is about 30 % and that a mean below the MDE is recorded as underpowered, never "no edge".

What would unblock (each is a new PRE_REG, not a parameter search): (a) a longer or wider DEV sample with at least 540 fills per setup (more symbols, for example ETH, which the PRE_REG home market names), (b) an operator overrule of the 0.30 R plausible-gross cap or of the repo-wide m, (c) a design with a smaller Holm family. Trailing-swing and FTA exits (trials 2 and 3) also need an exit simulator that `bt_engine.simulate_trade` (fixed bracket only) does not have; `cc_setups.py` logic is out of scope for this card.

DECISION (OURS, conservative default): BLOCKED, no run, no VALIDATION read. CryptoCred 4h/1d is NOT killed and its single redesign is NOT spent (PRE_REG 0f kill clauses need an outcome read).

## Kill scope (REGATE_AUDIT.md fix 4)
FAIL/INCONCLUSIVE: stop; this BLOCK (count-only, no outcome read) covers only the 6 registered 4h CryptoCred redesign cells (Setups 1 and 2 x ATR buffer 0.5/1.0/1.5, fixed 1.5 R bracket, Deribit all_taker) on BTCUSDT DEV at n about 200 each; it blocks on power (MDE 0.375 R + cost 0.068 R > 0.30 R), so the source is not killed and the redesign is not used: a larger sample, more symbols or an operator overrule is a new PRE_REG with new TRIAL_LEDGER rows.
