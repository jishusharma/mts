# BLOCKED: power gate fails for all three legs (2026-10-18, card eu-low-us-sweep-follow-ups-long-after-sw)

Verdict word: BLOCKED. No outcome computed (`followups.py` has no outcome path enabled; `--count` only builds entries and stops); no VALIDATION/HOLDOUT bar read (`common.load` refuses bars from 2024-07-01).

Arithmetic (prereg_gate.py, sd 1.0 R, m 3, cost = 0.10 % round trip / median stop distance):
- A: n 133 days, median stop 0.528 % -> cost 0.190 R, MDE 0.280 R, sum 0.470 R > 0.30 R; n needed 864.
- B: n 208 days, median stop 0.405 % -> cost 0.247 R, MDE 0.224 R, sum 0.471 R > 0.30 R; n needed 3723.
- C: n 100 days, median stop 0.531 % -> cost 0.188 R, MDE 0.323 R, sum 0.511 R > 0.30 R; n needed 834.
At the precedent sd 1.5 R it is worse (A: MDE 0.421 R, n needed 1945). The cost term alone leaves only 0.11-0.12 R for MDE.

What would unblock (a new pre-reg, decided before any outcome): (a) pooled instruments/venues for roughly 7x the units of A and C (BTC DEV yields ~53 A events per year; 864 days is ~16 years), (b) a wider-stop design (stop >= ~0.8 % so cost <= 0.12 R) or maker entries with a written fee decision (operator), (c) an operator overrule of the 0.30 R plausible-gross cap. No parameter search may rescue the gate.

DECISION (OURS, conservative default, logged): BLOCKED, no run, so the leg-A stability test (same sign DEV/VAL/HOLDOUT, leave-one-year-out) was not run either; sd 1.0 R chosen as the favourable bound so a BLOCK is robust.
