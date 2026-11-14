Regime mix: 150 weeks OOS 2024-01-01..2026-11-14 (BTC regime): bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)
Verdict: NO EDGE. 0 of 9 confirmatory cells survive (survivors.json is []): gross is about zero (-0.08 to +0.06 % per trade), fee-net (0.14 % round trip) is -0.085 to -0.223 % per trade in every cell, and 6 of the 9 cells (asia and ny, all three k) are significantly NEGATIVE (Holm p 0.023-0.033). Wording is power-qualified: the gate BLOCKs detecting a +0.30 % gross (POWER_GATE.md), so this is "no edge found, strongly net-negative", not a proof for every variant. It says nothing about other exits, band settings, maker cost, a bear regime (none in this window, bear 0 %), or the trader's discretionary read.

# bb_range_retest re-derived on 10 symbols, OOS 2024+ (fee-net 0.14 %, PRE_REG.md frozen first, commit 14b5675d5)

Rule unchanged from bb_range_retest_2026-11-04 (BTC only, DEV 2022-24: INCONCLUSIVE, net -0.07..-0.20 %). Data: Binance spot 15m, BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, signals 2024-01-01..2026-11-14 (62,230 all-regime signals, 6,000-6,300 per symbol, 0 bar gaps). Parameters: all OURS as in the 11-04 PRE_REG (bands, M, N, k, bracket, session-range tag); range gate SOURCED Malkan 60/40 + SMA200, BTC-for-all OURS; cost SOURCED research_kit. Fill rate 63-72 % (valid, below the 95 % INVALID line).

Confirmatory family (15m, BTC-range gate, session-range tagged, 10 symbols pooled, day-clustered over all symbols; Holm m = 9). n = trades; days = distinct UTC days.

| session | k | n | days | gross % | net % [95 % CI] | target hit | Holm p | vs all-regime (t) | net 2024-01..25-06 (n) | net 2025-07..26-11 (n) |
|---|---|---|---|---|---|---|---|---|---|---|
| asia | 0.25 | 1882 | 425 | -0.050 | -0.190 [-0.326, -0.054] | 17 % | 0.033 | -0.4 | -0.216 (631) | -0.177 (1251) |
| asia | 0.5 | 1974 | 430 | -0.045 | -0.185 [-0.316, -0.054] | 18 % | 0.033 | -0.4 | -0.230 (654) | -0.163 (1320) |
| asia | 1.0 | 2046 | 433 | -0.046 | -0.186 [-0.319, -0.054] | 18 % | 0.033 | -0.6 | -0.247 (678) | -0.156 (1368) |
| london | 0.25 | 1428 | 417 | +0.047 | -0.093 [-0.235, +0.048] | 24 % | 0.585 | -0.4 | +0.017 (485) | -0.150 (943) |
| london | 0.5 | 1486 | 426 | +0.050 | -0.090 [-0.230, +0.050] | 24 % | 0.585 | -0.2 | +0.023 (499) | -0.147 (987) |
| london | 1.0 | 1547 | 432 | +0.055 | -0.085 [-0.216, +0.046] | 26 % | 0.585 | -0.1 | +0.018 (518) | -0.137 (1029) |
| ny | 0.25 | 1677 | 391 | -0.083 | -0.223 [-0.367, -0.078] | 13 % | 0.023 | +0.5 | -0.385 (545) | -0.144 (1132) |
| ny | 0.5 | 1771 | 397 | -0.078 | -0.218 [-0.360, -0.076] | 13 % | 0.023 | +0.3 | -0.375 (572) | -0.143 (1199) |
| ny | 1.0 | 1832 | 399 | -0.068 | -0.208 [-0.348, -0.068] | 14 % | 0.026 | +0.5 | -0.368 (598) | -0.130 (1234) |

Descriptive arms at k = 0.5 (all sessions): range tagged n 6,399 gross -0.027 net -0.167; range untagged n 20,379 gross -0.009 net -0.149; all-regime any-tag n 44,309 gross -0.008 net -0.148. The tag and the range gate add nothing (vs all-regime t between -0.6 and +0.5).

Per symbol (k = 0.5, range, tagged, all sessions; n / net %): BTC 647 / -0.142, ETH 635 / -0.158, SOL 655 / -0.197, XRP 682 / -0.249, DOGE 638 / -0.232, BNB 655 / -0.180, ADA 643 / -0.058, LINK 622 / -0.203, LTC 625 / -0.170, AVAX 597 / -0.066. No symbol is net positive; the best two (ADA, AVAX) have gross +0.07..+0.08 %, below the 0.14 % cost, and are not tested cells.

Reading: the only gross-positive family cell is london (+0.05 %), which is positive in 2024-01..25-06 (+0.02 %) and negative after, and is still 0.09 % below cost. Gross edge of the encoded rule is zero across 10 symbols and three years; the 0.14 % round trip makes it a steady loser. The 2024+ window includes VALIDATION and HOLDOUT of the project splits: logged in research/holdout_reads.csv, BURNED for the bb-range-retest family. Survivorship: the 10 symbols are today's liquid survivors. Files: study.py, test_10sym.py (3 tests; 2 fail with OOS_START mutated to 0), cells.csv, per_symbol.csv, counts.csv.
