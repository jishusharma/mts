# Episodes per pre-registered contrast (counts only; PRE_REG.md section 3)

Episode = grid row with at_level, first_touch, a ladder rung and a stop >= the 0.56 % cost floor. n_min = 572 (MDE = 2.8 x 1.25 R x sqrt(1 + 1/20) / sqrt(n) <= 0.15 R, the cost-free filter contrast). `<n` marks a cell below n_min on the pooled count; the per-period columns are for the consistent-sign rule.

| contrast | side | 2022 | 2023 | 2024H1 | all | complement all |
|---|---|---|---|---|---|---|
| F1 at a side-aware level (every episode) | long | 646 | 696 | 294 | 1636 | 0 |
| F2 confluence n_layers >= 2 | long | 520 | 538 | 247 | 1305 | 331 |
| F3 operator condition (ladder_cond) | long | 346 | 428 | 191 | 965 | 671 |
| F4 4h pattern in the trade direction | long | 106 | 92 | 63 | 261 <n | 1375 |
| F5 long: re-entry from the lower band | long | 13 | 17 | 6 | 36 <n | 1600 |
| F6 phase A with the trade (markup long / markdown short) | long | 177 | 291 | 110 | 578 | 1058 |
| F7 HTF alignment (htf_align) | long | 184 | 494 | 207 | 885 | 751 |
| F1 at a side-aware level (every episode) | short | 681 | 646 | 324 | 1651 | 0 |
| F2 confluence n_layers >= 2 | short | 540 | 487 | 280 | 1307 | 344 |
| F3 operator condition (ladder_cond) | short | 416 | 374 | 175 | 965 | 686 |
| F4 4h pattern in the trade direction | short | 110 | 119 | 58 | 287 <n | 1364 |
| F5 short: band-walk-down veto | short | 23 | 13 | 4 | 40 <n | 1611 |
| F6 phase A with the trade (markup long / markdown short) | short | 177 | 179 | 26 | 382 <n | 1269 |
| F7 HTF alignment (htf_align) | short | 379 | 178 | 110 | 667 | 984 |

Episodes with a valid stop: long 1636, short 1651 (of 21888 grid points per side).
