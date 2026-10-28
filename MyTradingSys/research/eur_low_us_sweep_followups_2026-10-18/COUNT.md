# COUNT: events per leg on the DEV tape (bars before 2024-07-01), no outcome computed

Gate rule: scripts/dev/prereg_gate.py, sd 1.0 R (OURS; precedent runs used 1.5), m 3 (the three legs), cost = 0.10% round trip / median stop distance. MDE + cost must be <= 0.30 R.

| leg | candidates | skipped (reason: n) | n tradeable (= days) | median risk % | cost R | MDE R | MDE+cost R | n needed | gate |
|---|---|---|---|---|---|---|---|---|---|
| A long after sweep+reclaim | 161 | {'risk_small': 14, 'noreclaim': 11, 'entry_through_stop': 3} | 133 | 0.528 | 0.190 | 0.280 | 0.470 | 856 | BLOCK |
| B RSI-divergence short | 243 | {'risk_small': 28, 'entry_through_stop': 7} | 208 | 0.405 | 0.247 | 0.224 | 0.471 | 3676 | BLOCK |
| C pre-US double-top short | 102 | {'risk_small': 2} | 100 | 0.531 | 0.188 | 0.323 | 0.512 | 836 | BLOCK |
