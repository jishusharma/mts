# Blind read: H3 pooled BTC+ETH NY-open-low BLOCKED.md (2026-11-06)

Read: h3_ny_open_pooled_2026-11/BLOCKED.md and h3_ny_open_low_2026-10/BLOCKED.md first. Recomputed with `statistics.NormalDist` (OURS, not the prereg_gate.py code path); only inputs taken from `scripts/dev/prereg_gate.py:21-30,62` (formulas, max gross 0.30, power z 0.84, cost 0.14, sd 1.5). No VALIDATION/HOLDOUT read; no file edited.

| # | Claim (file:line) | Recomputed | Result |
|---|---|---|---|
| 1 | z_holm 3.687 at m=220 (pooled BLOCKED.md:11) | inv_cdf(1-0.05/440)=3.687 | MATCH |
| 2 | MDE 0.812 R at n=70, sd 1.5 (pooled:11) | (3.687+0.84)*1.5/sqrt(70)=0.812 | MATCH |
| 3 | MDE+cost = 0.952 (pooled:11) | 0.812+0.14=0.952 > 0.30 | MATCH |
| 4 | n needed 1801 (pooled:11) | ((3.687+0.84)*1.5/(0.30-0.14))^2=1801 | MATCH |
| 5 | m=220 (pooled:11) | `verdicts.py count --split DEV --ledger` prints 220 from 46 studies (OURS run, 5 UNPARSED rows excluded = lower bound) | MATCH |
| 6 | Earlier card: m 106, MDE 1.10, n~1650 at n=35 (low BLOCKED.md:11-12) | z=3.496; MDE 1.099; need 1653 | MATCH (m differs from 220 only because the ledger grew; historical m not re-verified) |
| 7 | Earlier card: sd 0.5 gives MDE 0.37, n needed 184 (low:12) | 0.366; 183.6 | MATCH |
| 8 | "needs ~25x more events" (pooled:15) | 1801/70 = 25.7 (51.5x the 35 BTC count) | MATCH |
| 9 | 2 x 35 = 70 upper bound (pooled:10) | Arithmetic ok. Premise "ETH cannot exceed BTC-like 650 NY days" is an assumption (OURS); event count not re-derived (ETH klines absent, pooled:8) | MATCH (arithmetic); premise unverified |
| 10 | Bound is conservative: if 70 blocks, true n blocks (pooled:10) | Stress test: even n=1300 (an event EVERY NY day on both symbols) gives MDE 0.188+0.14=0.328 > 0.30, still BLOCK. Conclusion holds regardless of the ETH count | MATCH |
| 11 | BTC n=35 of 650 days (low:7-8) | Not recomputed (needs kline read; out of scope); 35/650=5.4% arithmetic only | NOT CHECKED |

Defects: none (file:line). Caveat: row 9 premise and row 11 count are not independently verified; neither changes the verdict (row 10). sd 1.5 is a two-point value (OURS), not measured.

VERDICT: MATCH
