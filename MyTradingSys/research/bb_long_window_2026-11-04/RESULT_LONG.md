Regime mix: 360 weeks long DEV (2017-08-07..2024-06-24): bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%) | bear weeks: primary Malkan (weekly AND monthly <=40) 0, proxy P40 (weekly <=40 alone, below SMA200, OURS) 57
Verdict A (bb_range_to_range, powered family): FAIL again for the rule as encoded, now on 2017-08..2024-06 SPOT: 0 of 6 range cells have net > 0, all six nets are -0.115 to -0.165 % per trade with day-clustered CIs entirely below zero (Holm p < 0.001 for each, in the negative direction), n 2093-3110 trades per cell (original 951-1634). FAIL means stop, same scope as the original: BB(20,2) close-beyond-band, trade to the opposite band with a 2:1 bracket and 24-bar time-out, range regime, 15m BTCUSDT asia/london/ny, 0.14 % round trip.
Verdict B (bb_range_retest level arm) and every P40 bear-proxy cell: INCONCLUSIVE (underpowered), not FAIL: prereg_gate (m 150) BLOCKs all 9 B range cells and all 18 P40 cells (PASS only for the 6 A range cells, BLOCKED_LONG.md). 0 of 30 family cells survive (dev_survivors_long.json is []); VALIDATION not read; HOLDOUT never loaded.

# bb_long_window_2026-11-04 result: long-window DEV pass for both Bollinger studies (fee-net 0.14 %, day-clustered 95 % CI, pooled Holm m = 30)

PRE_REG_LONG.md was frozen first (commit 12da8913a); same arms and parameters as the two originals; Binance SPOT klines 2017-08..2024-06 (not futures, not spliced);
ungated control = tagged events only. Nothing about the Bollinger idea changed; only the history got 3x longer and one OURS bear proxy was added.

## Findings

- Malkan bear gate never fires: 0 bear weeks of 360 (monthly RSI14 never <= 40 since 2017-08; the first 65 weeks are n/a). Primary bear rows are empty (n 0) for both studies. The OURS proxy P40 (weekly RSI14 <= 40 alone, below SMA200; never Malkan's) gives 57 bear weeks: 2291 trades (A, 15m, all sessions, signal entry) and 359-385 level-arm fills (B, k 0.25-1.0).
- A, range gate, 15m, all sessions, signal entry: n 9008 / 1560 days, gross +0.012 %, net -0.128 % [-0.155, -0.102] (original n 4256, -0.130 % [-0.161, -0.099]); ungated tagged control n 12066, net -0.118 % [-0.141, -0.094]; gate effect -0.010 % (t -1.4). The range gate still does nothing. Bull (n 3058) net -0.087 % [-0.137, -0.037]: the best Malkan row and still negative.
- A, sides pooled before: long -0.105 % [-0.145, -0.066], short -0.151 % [-0.185, -0.117]. Wide-band ("larger range", OURS) -0.133 % [-0.189, -0.077] with 14 % target hits vs narrow -0.125 % [-0.148, -0.102], 26 %: a wide band again lowers the hit rate and changes nothing in net. 1h range n 2226 net -0.103 % [-0.211, +0.005]; 4h n 548 -0.091 % [-0.486, +0.305] (descriptive, power-blocked). 15m late (descriptive) -0.043 % [-0.108, +0.023], the least negative again.
- A, P40 proxy (OURS): six cells all net -0.110 to -0.148 %, CIs mostly below zero, gate effect t within +-0.1 of zero. Shorts-in-weak-weeks does not rescue the claim.
- A retest entry: still the next open (the fill rule is unchanged from the original): 9007 of 9008 range signals fill (99.99 %), net -0.127 % vs signal -0.128 %.
- B level arm, range gate, tagged: 0 of 9 cells net > 0, nets -0.045 to -0.238 %; asia (-0.045 / -0.065 / -0.084) has CIs that span zero, london is significant-negative on its own (-0.208 / -0.212 / -0.238, CIs below zero; Holm p 0.34 / 0.23 / 0.06), ny -0.139 to -0.144 (CIs touch zero). Session-range tag again does nothing measurable: tagged vs untagged t -1.1 to +0.9 in every cell; gate effect vs tagged all-regime t -1.1 to +1.0. All CIs are wider than +-0.12 %, so a gross edge of 0.12-0.15 % per trade is still not excluded: INCONCLUSIVE.
- B P40 proxy: the only positive nets in either study appear here: asia k0.25 +0.083 % [-0.254, +0.419] (n 105), k0.5 +0.049 % (n 111), london k0.25 +0.037 % (n 76); all CIs span zero by +-0.3 to +-0.6 %, Holm p = 1.00, gate effect t <= 0.9. Nothing to act on; n 76-116 per cell, fewer than the 30-day floor allows but far below the power need (68-89 days vs MDE + cost 0.65-1.12).
- Retest-arm fill rate on the long window (B, fills / signals, range tagged): k 0.25 / 0.5 / 1.0 = 62.6 % / 65.4 % / 67.7 % (1590 / 1660 / 1717 of 2538 signals; original 63 / 66 / 68 %); 69 % of signals close back inside the band within 10 bars (original 69 %), and 91-98 % of those touch the k-ATR limit. By session 59-72 %. The arm stays a valid return-to-the-band entry (fill < 95 %), unlike the A next-open "retest" (99.99 %). Untagged range signals fill 73.7 % at k = 0.5.
- Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, gate effect t >= 2): 0 survivors of 30. The only cells with net > 0 (three B P40 cells) have Holm p = 1.00.

## Per cell, original (DEV 2022-01..2024-06, futures 1m) vs long (2017-08..2024-06, spot), range gate, sides pooled (n trades / days, net % [95 % CI])

| Cell | Original | Long | Hit orig / long | Holm p (m 30) | Gate effect t |
|---|---|---|---|---|---|
| A 15m asia signal | 1200 / 656, -0.122 [-0.177, -0.067] | 2697 / 1412, -0.140 [-0.182, -0.098] | 17 / 18 % | <0.001 | -1.8 |
| A 15m london signal | 951 / 586, -0.138 [-0.200, -0.076] | 2093 / 1270, -0.165 [-0.220, -0.109] | 28 / 25 % | <0.001 | -0.9 |
| A 15m ny signal | 1634 / 702, -0.153 [-0.206, -0.100] | 3110 / 1465, -0.123 [-0.168, -0.079] | 21 / 20 % | <0.001 | -0.4 |
| A 15m asia retest | 1200 / 657, -0.121 [-0.176, -0.065] | 2696 / 1416, -0.143 [-0.186, -0.101] | 19 / 20 % | <0.001 | -2.0 |
| A 15m london retest | 951 / 586, -0.130 [-0.193, -0.068] | 2093 / 1270, -0.164 [-0.218, -0.109] | 30 / 26 % | <0.001 | -0.6 |
| A 15m ny retest | 1634 / 702, -0.143 [-0.196, -0.089] | 3110 / 1465, -0.115 [-0.160, -0.069] | 23 / 23 % | <0.001 | -0.1 |
| B asia k 0.25 | 225 / 176, -0.094 [-0.240, +0.052] | 486 / 374, -0.045 [-0.171, +0.080] | fill 62 / 63 % | 1.00 | -1.0 |
| B asia k 0.5 | 235 / 182, -0.105 [-0.248, +0.037] | 507 / 389, -0.065 [-0.180, +0.050] | 65 / 66 % | 1.00 | -1.0 |
| B asia k 1.0 | 244 / 186, -0.132 [-0.270, +0.007] | 520 / 394, -0.084 [-0.193, +0.026] | 68 / 67 % | 1.00 | -1.1 |
| B london k 0.25 | 175 / 146, -0.133 [-0.321, +0.054] | 390 / 316, -0.208 [-0.379, -0.037] | 67 / 65 % | 0.34 | -0.2 |
| B london k 0.5 | 180 / 149, -0.175 [-0.350, 0.000] | 403 / 322, -0.212 [-0.374, -0.051] | 69 / 67 % | 0.23 | -0.2 |
| B london k 1.0 | 186 / 155, -0.201 [-0.369, -0.033] | 413 / 330, -0.238 [-0.393, -0.084] | 72 / 69 % | 0.06 | -0.6 |
| B ny k 0.25 | 215 / 162, -0.118 [-0.305, +0.068] | 439 / 345, -0.139 [-0.291, +0.014] | 59 / 59 % | 0.98 | +1.0 |
| B ny k 0.5 | 224 / 169, -0.083 [-0.268, +0.101] | 456 / 355, -0.141 [-0.294, +0.011] | 61 / 61 % | 0.97 | +0.6 |
| B ny k 1.0 | 233 / 174, -0.073 [-0.253, +0.108] | 478 / 370, -0.144 [-0.289, +0.002] | 64 / 64 % | 0.86 | +0.3 |

Reading: every cell keeps its sign; A is unchanged within noise with about 2x the trades (its CI halves, the answer is still a clear negative net near the 0.14 % cost with
gross about zero); B's nets drift slightly more negative in london and ny and less in asia, all within the original CIs. Holm p for the A range cells is the p of a NEGATIVE
net (they fail the net > 0 test, not the p test).

## What it says

The longer history does not rescue either encoding. A, the only powered family, is a FAIL on both windows with the same size and sign: gross about zero, the
opposite band reached in about one trade in five, 0.14 % cost leaves -0.12 to -0.17 %. B stays INCONCLUSIVE because its tagged cells are still 316-394 days (need
about 480-1800) and the proxy cells 68-89 days; its point estimates are negative and its CIs remain wide. The OURS bear proxy P40 changes neither verdict: A P40 is negative like
A range, B P40 is a handful of cells with n below 120 and CIs +-0.3 to +-0.6 %. Not a PASS anywhere; the next step would be more symbols or a different exit (take the mid), each a new PRE_REG, not another BTC DEV read.

## Data and honesty notes

- Spot, not futures; different series from the originals (no splice), so cells compare in size and sign, not bit for bit. The 2022-2024 half of the long window was already seen
  in the originals; the new-data-only (2018-2021) effect is not isolated (not pre-declared).
- Ungated control is tagged-only (the first 65 weeks have no SMA200 / monthly RSI); the originals' ungated arm included untagged events but their window had none.
- Exchange-maintenance gaps in the spot archive are not filled ("24 bars" counts bars present).
- P40 events are a subset of range events under the primary tag; the range and P40 rows are overlapping views, and the pooled Holm treats the 30 cells as one family (conservative).
- Data loaded only to 2024-07-01 (splits.DEV_END, exclusive); VALIDATION unread; HOLDOUT never loaded. Label: the session-range tag, the wide-band stratum and the P40 proxy are OURS, never the trader's or Tom's.

Files: PRE_REG_LONG.md, BLOCKED_LONG.md, counts_long.csv, dev_cells_long.csv (all cells), dev_survivors_long.json, regime_mix_count_long.txt, regime_mix_dev_long.txt, study_long.py, gate_long.py,
test_long_wiring.py (7 tests; on the pre-change stub 5 failed with `NotImplementedError: pre-change stub` at study_long.py gate_pass / holm_family, 2 passed; then 7 passed).
