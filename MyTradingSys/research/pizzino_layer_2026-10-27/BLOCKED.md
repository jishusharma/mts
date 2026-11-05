# prereg_gate.py output, 2026-11-05 (count pass only, before any return; n = trades = distinct entry days from counts.txt, sd 1.5 R design bound (PRE_REG.md:19), cost in R = 0.14 % / median stop %, m auto + 10 new cells)

- C0 default, C1 conf3, C2 conf1, C5 rr1.5, C6 TS10 (1d): n 3 sd 1.5 m 227 z_holm 3.695 MDE 3.927 R + cost 0.023 = 3.950 vs max plausible gross 0.3; n needed 603 | BLOCK: do not freeze (write BLOCKED.md with these numbers) (exit 1)
- C3 n2-5-13 (1d): n 5 sd 1.5 m 227 z_holm 3.695 MDE 3.042 R + cost 0.0044 = 3.046 vs max plausible gross 0.3; n needed 529 | BLOCK: do not freeze (write BLOCKED.md with these numbers) (exit 1)
- C4 n3-8-21 (1d): n 1 sd 1.5 m 227 z_holm 3.695 MDE 6.802 R + cost 0.0038 = 6.806 vs max plausible gross 0.3; n needed 527 | BLOCK: do not freeze (write BLOCKED.md with these numbers) (exit 1)
- C7 count_req (1d): n 0, gate not runnable (no trade)
- C8 tf4h: n 9 sd 1.5 m 227 z_holm 3.695 MDE 2.267 R + cost 0.27 = 2.537 vs max plausible gross 0.3; n needed 51406 | BLOCK: do not freeze (write BLOCKED.md with these numbers) (exit 1)
- C9 tf1h: n 20 sd 1.5 m 227 z_holm 3.695 MDE 1.521 R + cost 0.068 = 1.589 vs max plausible gross 0.3; n needed 860 | BLOCK: do not freeze (write BLOCKED.md with these numbers) (exit 1)

Reading: every cell BLOCKs (largest n 20 vs 527+ needed). Per the gate, PRE_REG.md is not frozen, no DEV return pass, no VALIDATION read, no HOLDOUT read.
