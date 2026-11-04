Regime mix: 130 weeks DEV: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
Verdict: FAIL for the rule as encoded in PRE_REG.md on its powered family (15m, asia / london / ny, signal and retest entry): 0 of 6 cells have net > 0, all six nets are -0.12 to -0.15 % per trade with day-clustered CIs entirely below zero. FAIL means stop: Bollinger BB(20,2) close-beyond-band, trade to the opposite band with a 2:1 bracket and 24-bar time-out, in research_kit range regime, 15m BTCUSDT, asia / london / ny signal-bar sessions, under 0.14 % round-trip cost, DEV 2022-01..2024-06; it says nothing about 1h / 4h / late (underpowered, descriptive), other band settings, other targets or stops, discretionary reads, other symbols or a bear regime (none in this DEV window). VALIDATION not read (no DEV survivor); HOLDOUT never read.

# bb_range_to_range_2026-11-04 result (DEV 2022-01-01..2024-06-30, fee-net 0.14 %, PRE_REG.md frozen first, commit 79364ea2c)

The operator's claim, "in a range the band-to-band move repeats", is not visible in this encoding: gross return is zero within noise and the move to the opposite band completes in about one trade in five, against about one in three needed to break even on a 2:1 bracket before cost.

| 15m, range gate, sides pooled | entry | n | days | gross % | net % [95 % CI] | target hit | range minus ungated (t) |
|---|---|---|---|---|---|---|---|
| asia | signal | 1200 | 656 | +0.018 | -0.122 [-0.177, -0.067] | 17 % | +0.006 (0.5) |
| london | signal | 951 | 586 | +0.002 | -0.138 [-0.200, -0.076] | 28 % | -0.001 (-0.1) |
| ny | signal | 1634 | 702 | -0.013 | -0.153 [-0.206, -0.100] | 21 % | -0.009 (-0.8) |
| asia | retest | 1200 | 657 | +0.019 | -0.121 [-0.176, -0.065] | 19 % | +0.006 (0.5) |
| london | retest | 951 | 586 | +0.010 | -0.130 [-0.193, -0.068] | 30 % | -0.001 (-0.1) |
| ny | retest | 1634 | 702 | -0.003 | -0.143 [-0.196, -0.089] | 23 % | -0.008 (-0.7) |

- The gate does nothing: 15m all sessions, signal entry, range n 4256 net -0.130 % [-0.161, -0.099] against ungated n 5311 net -0.127 % [-0.154, -0.099]; the difference has t -0.5. The range tag keeps 80 % of signals in this window (bull 19 % of weeks, bear 0), so the comparison has little contrast. The bull-regime rows (15m n 1055, net -0.115 %) are equally negative.
- Sessions: the one positive-looking cell is 15m late (n 471, net -0.053 % [-0.145, +0.040]), a prereg_gate BLOCK cell and still negative; the asia / london / ny differences are within noise of each other. Session did not rescue the claim.
- Larger ranges (Tom), descriptive: 15m wide-band signals net -0.129 % [-0.197, -0.062] (target hit 15 %), narrow net -0.130 % [-0.157, -0.103] (hit 26 %). A wide band lowers the hit rate and does not change net.
- Sides: long net -0.108 % [-0.154, -0.061], short -0.153 % [-0.195, -0.112] (15m, all sessions).
- 1h / 4h (descriptive, BLOCKED power): 1h range signal n 1080 net -0.157 % [-0.278, -0.036], 4h n 252 net -0.449 % [-0.919, +0.020]; per session 1h late +0.133 % [-0.240, +0.506] (n 141) is the only positive point, underpowered and one of 16 uncorrected looks.
- Retest entry: fills 4256 of 4260 range signals (99.9 %). As disclosed in PRE_REG, with a close at or beyond the band the next bar almost always trades through the band, so the retest arm is the next-open entry; it differs from signal entry by under 0.01 % in net.

What it does not show: that the band-to-band move never happens (it completes in 17-30 % of trades, more often in london), only that the move does not pay a bracket entered at the band close after a 0.14 % round trip. A different exit (take the mid, no fixed stop), a trend-inside-range phase tag, or a maker-fill cost (0.09 %) are untested here and would be a new PRE_REG with fresh m.

Not a PASS and no replay was needed (no survivor). Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, gate effect t >= 2): 0 survivors, dev_survivors.json is [].

Files: PRE_REG.md, BLOCKED.md, counts.csv (pre-return counts), dev_cells.csv (all cells: gate x side x width x TF x session x entry), dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, study.py, test_range_wiring.py (7 tests; all 7 failed on the pre-change stub with NotImplementedError, then 7 passed; one test fixture was corrected once after the first implementation run because its post-signal price sat inside the band, not because of a code bug).
Data: BTCUSDT 1m from F:/MTS/Dumps/backtest (raw_1m_2019, raw_1m_2022, raw), loaded only to 2024-07-01.

Label note (Haiku review 2026-11-04): the session / larger-range rule is OURS. No transcript line from Tom was found; this study tests the rule as encoded here, never as the trader said it.
