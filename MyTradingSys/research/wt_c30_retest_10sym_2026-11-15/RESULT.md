Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)
Verdict: NO EDGE (0 of 24 confirmatory cells survive; underpowered ceiling by the gate, so INCONCLUSIVE-grade wording, not an unqualified FAIL). Fee-net 0.14 % round trip, 10 Binance spot symbols, OOS 2024-01-01..2026-11-14, rule frozen unchanged from 2026-11-04.

# wt_c30_retest_10sym_2026-11-15 result

Reproduce: `python fetch.py` (1d) + 15m cache from bb-retest-10sym-1115, then `python study.py --pass count` / `--pass run` (about 3 min each); tables `counts.csv`, `cells.csv` (456 rows), `survivors.json` (empty), tests `test_10sym.py`.
Parameters: dot band 53, WT params, RSI 14, 3..12-bar close divergence and the 0.14 % cost are SOURCED; the RSI 40/60 level, 3-bar divergence proximity, midpoint retest within 6 bars, 12-bar exit, TFs, per-symbol SMA200 application, BTC regime for all symbols and the survivor thresholds are OURS (PRE_REG.md labels each).

- Family (pooled 10 symbols, gate with-trend, rsi/div, 3 TF x 2 sides x 2 entries = 24 cells, Holm m=24): 0 survivors. 0 cells have a net CI entirely above zero; 9 of the 24 have net CI entirely below zero (all four 15m sell, 15m buy rsi retest, 30m sell rsi signal, 1h sell rsi signal and retest, 1h sell div retest).
- Best cells: 30m sell + div retest n 526 / 247 days gross +0.152 %, net +0.012 % [-0.188, +0.212], excess t 1.60, Holm p 1.0, sub-windows net -0.090 / +0.093 (fails the same-sign rule). 30m sell + div signal n 604 / 283 days net -0.063 %. 15m buy + div signal n 999 / 370 days net -0.029 % [-0.192, +0.133], excess t 1.30, sub-windows +0.051 / -0.165.
- The 11-04 lead (1h sell + divergence, with-trend, retest): now n 276 / 164 days, gross -0.230 %, net -0.370 % [-0.726, -0.014], excess t -1.21; per symbol 1 of 10 symbols positive (ADA +0.07 %, n 29), BTC alone -0.241 % (n 18). The BTC-only +1.117 % (n 19 / 17 days) did not replicate: it was small-n noise.
- Controls: bare dots (conf none, signal entry) lose fee-net in every TF, side and gate (15m buy all -0.122 %, 15m sell all -0.156 %, 30m -0.182 / -0.186, 1h -0.270 / -0.363). The trend gate again helps SELL dots more than BUY dots (30m sell with -0.133 vs against -0.245; 1h sell -0.279 vs -0.451) and does not turn any of them positive.
- Across all 396 cells with n >= 30: 0 have a net CI entirely above zero, 144 entirely below.
- Retest entry vs signal entry: no systematic gain (better in 5, worse in 7 of the 12 pooled rsi/div pairs).

Power: the gate BLOCKs 6 of 7 probed cells (POWER_GATE.md; n needed 486 / 1013 / 2165 event-days for 15m / 30m / 1h at m=24 against a 0.30 % plausible gross). Ten symbols multiply trades (n up to 3,946) but the day cluster keeps effective n near 300-590 days. Gross returns sit within about +-0.15 % of zero for the 15m / 30m cells, so the cost (0.14 %) alone erases what exists; an effect larger than the cost would have shown in the 15m cells (they pass the gate on days) and none did.
Gaps: spot data, no funding; taker fill on both legs, spot-like fills at close or limit level; survivorship-biased 10 majors; sessions not re-split; 12-bar horizon and midpoint level not varied; reg_bear empty (no bear week in the strict Malkan band). Reads VALIDATION and HOLDOUT windows for this family: BURNED for the wavetrend-c30 family (holdout_reads.csv).
