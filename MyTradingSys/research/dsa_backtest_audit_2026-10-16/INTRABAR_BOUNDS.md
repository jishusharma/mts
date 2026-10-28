# Intrabar stop/target ordering bounds (T10-F2, C05)

DEV/VALIDATION only, no HOLDOUT. Force per run: stop-first (stop wins a bar holding both, the shipped default) vs target-first. Bars holding both = trades whose exit differs between the two orderings (Tom: sum of the sim's own `ambiguous` counter). Gap R = mean net R target-first minus stop-first; trade sets can differ between modes (one-at-a-time busy window), as in the published runs. Tight slice = stop distance < 0.15% of entry (OURS threshold, from the card). Fill bar: all three sims test only the stop there, so fill-bar ambiguity is not in these bounds. Fabio v3: the four selection.json cells at 2 bps, windows 2024-12-02..2026-06-25. Tom: rows with t < 2026-06-26, base fees. bt_engine: CryptoCred maker_entry, dev span (first 70% of bars).

### Tom (tom_bt.sim_limit_trade)

| sim / slice | trades (stop-first) | bars holding both | mean net R stop-first | mean net R target-first | gap R (target minus stop) | sign flips |
|---|---|---|---|---|---|---|
| Tom episode / all stops | 17 | 0 | -0.1854 (n=17) | -0.1854 (n=17) | +0.0000 | no |
| Tom episode / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Tom A / all stops | 17 | 0 | -0.1854 (n=17) | -0.1854 (n=17) | +0.0000 | no |
| Tom A / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Tom watch_episode / all stops | 4163 | 1 | -0.2963 (n=4163) | -0.2953 (n=4163) | +0.0010 | no |
| Tom watch_episode / stop<0.15% | 301 | 0 | -0.5485 (n=301) | -0.5485 (n=301) | +0.0000 | no |
| Tom p4_episode / all stops | 838 | 0 | -0.2375 (n=838) | -0.2375 (n=838) | +0.0000 | no |
| Tom p4_episode / stop<0.15% | 55 | 0 | -0.5528 (n=55) | -0.5528 (n=55) | +0.0000 | no |

### Fabio v3 (manage.simulate_trade)

| sim / slice | trades (stop-first) | bars holding both | mean net R stop-first | mean net R target-first | gap R (target minus stop) | sign flips |
|---|---|---|---|---|---|---|
| Fabio v3 model A (A|N60|p0.05|f0.003|rest|g0.8) / all stops | 1 | 0 | +1.6150 (n=1) | +1.6150 (n=1) | +0.0000 | no |
| Fabio v3 model A (A|N60|p0.05|f0.003|rest|g0.8) / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Fabio v3 model B (B|N60|z2|f0.003|rest) / all stops | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Fabio v3 model B (B|N60|z2|f0.003|rest) / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Fabio v3 model C (C|m5|f0.005|rest|g0.8) / all stops | 221 | 0 | -0.0733 (n=221) | -0.0733 (n=221) | +0.0000 | no |
| Fabio v3 model C (C|m5|f0.005|rest|g0.8) / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |
| Fabio v3 model D (D|N240|p0.05|f0.003|rest) / all stops | 1 | 0 | +0.0171 (n=1) | +0.0171 (n=1) | +0.0000 | no |
| Fabio v3 model D (D|N240|p0.05|f0.003|rest) / stop<0.15% | 0 | 0 | n/a (n=0) | n/a (n=0) | n/a | no |

### bt_engine (CryptoCred 1h signals, 1m sim)

| sim / slice | trades (stop-first) | bars holding both | mean net R stop-first | mean net R target-first | gap R (target minus stop) | sign flips |
|---|---|---|---|---|---|---|
| bt_engine/CryptoCred setup1_sr_flip / all stops | 1066 | 0 | -0.3856 (n=1066) | -0.3856 (n=1066) | +0.0000 | no |
| bt_engine/CryptoCred setup1_sr_flip / stop<0.15% | 1066 | 0 | -0.3856 (n=1066) | -0.3856 (n=1066) | +0.0000 | no |
| bt_engine/CryptoCred setup2_fib_pullback / all stops | 992 | 23 | -0.4481 (n=992) | -0.4481 (n=992) | +0.0000 | no |
| bt_engine/CryptoCred setup2_fib_pullback / stop<0.15% | 323 | 2 | -1.2191 (n=323) | -1.2191 (n=323) | +0.0000 | no |
| bt_engine/CryptoCred setup3_failed_msb_reversal / all stops | 119 | 0 | +0.0432 (n=119) | +0.0432 (n=119) | +0.0000 | no |
| bt_engine/CryptoCred setup3_failed_msb_reversal / stop<0.15% | 3 | 0 | -1.4121 (n=3) | -1.4121 (n=3) | +0.0000 | no |

- Tom (tom_bt.sim_limit_trade): input size 114124
- Fabio v3 (manage.simulate_trade): input size 386
- bt_engine (CryptoCred 1h signals, 1m sim): input size 2512800

Verdict: 0 slice(s) change the sign of mean net R between the stop-first and target-first bounds: none.
