# Layer Lab Report: `gemini-blind-read-ms-level-eth`

- **Card**: `gemini-blind-read-ms-level-eth`
- **Target Study**: `MyTradingSys/research/level_approach_eth_2026-11/RESULT.md`
- **Raw CSV Data**:
  - `MyTradingSys/research/level_approach_eth_2026-11/sequences.csv` (124 rows, 64 judged rows)
  - `MyTradingSys/research/level_approach_eth_2026-11/classes.csv` (48 rows, 24 judged rows)
  - `MyTradingSys/research/level_approach_eth_2026-11/regime_mix_dev.txt` (3 lines)
- **Detailed Audit**: `MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_MS_LEVEL_ETH.md`
- **Verification Command**:
  `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_MS_LEVEL_ETH.md'); assert p.exists() and len(p.read_text())>400 and 'VERDICT' in p.read_text()"`
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini (independent blind read worker)

---

## 1. Study Nature & Metric Definition

Per SOURCED `RESULT.md:1` and `study.py:7`, this is a descriptive, fee-free replication study across BTCUSDT and ETHUSDT USD-M futures (DEV period 2022-01 to 2024-06). No trading costs or fee-net PnL calculations are applied.
The evaluated metrics are:
- Event sample sizes $n$ (total events) and split sample sizes $n_A, n_B$ (first half / second half of DEV).
- Duration / regime mix counts: 130 weeks per symbol, 260 weeks pooled across bull, bear, range, and n/a regimes.
- Breakout proportions $p$ (sample mean / hit rate) and half-split proportions $p_A, p_B$.
- Wilson score 95% confidence intervals `[ci_lo, ci_hi]` on binomial proportions.

---

## 2. Headline Counts & Regime Mix Verification

### A. Headline Counts (`RESULT.md:5`)
- SOURCED `RESULT.md:5`: `Verdict: REPLICATES. 64 near_miss / wick_back sequence rows judged: 4 AGREE, 20 DISAGREE, 40 UNDERPOWERED (a cell under n 30).`
- OURS `sequences.csv` recomputation (`study.py:115` filter `cls in ('near_miss', 'wick_back')`):
  - Total judged rows: 64 rows [OURS `sequences.csv`] -> **MATCH**
  - `AGREES`: 4 rows [OURS `sequences.csv:2,3,11,59`] -> **MATCH**
  - `DISAGREES`: 20 rows [OURS `sequences.csv:4,5,6,7,10,12,13,14,15,27,28,29,39,43,44,45,51,60,61,63`] -> **MATCH**
  - `UNDERPOWERED`: 40 rows [OURS `sequences.csv`] -> **MATCH**

### B. Regime Mix Verification (`RESULT.md:7` vs `regime_mix_dev.txt`)
- SOURCED `RESULT.md:7`: `Regime mix: POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%))`
- OURS `regime_mix_dev.txt:1-3`:
  - BTCUSDT line: `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)` [OURS `regime_mix_dev.txt:1`]
  - ETHUSDT line: `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)` [OURS `regime_mix_dev.txt:2`]
  - POOL line: `POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%)` [OURS `regime_mix_dev.txt:3`]
- Cross-check: The prose string in `RESULT.md:7` matches the formatted assembly of `regime_mix_dev.txt` character for character -> **MATCH**.

### C. Reproduction & Invalidation Rows
- Reproduction check (SOURCED `RESULT.md:10`): BTC futures 10822 events (C15 shipped 10822), 32 cells compared with shipped `tables.csv`, 0 n mismatches. Matches OURS C15 reproduction check exactly.
- C15 invalidation row (SOURCED `RESULT.md:13`): `near_miss 1m, RSI<50, CVD12<=0, below daily BB mid`:
  - BTC: SOURCED `n 466 p 0.210 (A 0.222 / B 0.176)` vs OURS `sequences.csv:2` `n=466, p=0.2103, pA=0.2222, pB=0.1758` -> MATCH.
  - ETH: SOURCED `n 423 p 0.281 (A 0.287 / B 0.275)` vs OURS `sequences.csv:2` `n=423, p=0.2813, pA=0.2868, pB=0.2745` -> MATCH.
  - POOL: SOURCED `n 889 p 0.244 vs pooled base 0.278; AGREES` vs OURS `sequences.csv:2` `n=889, p=0.2441, base=0.278, AGREES` -> MATCH.

---

## 3. Table Recomputations & Discrepancy Diff List

All 48 rows across the 3 tables in `RESULT.md` (4 Agreeing, 20 Disagreeing, 24 Class base rates) totaling 528 metric cells were recomputed from `sequences.csv` and `classes.csv`.

### Table Summary:
- **Table 1 (Agreeing rows, `RESULT.md:18-21`)**: 4 rows × 13 data cells = 52 cells. 51 match identically; 1 cell has a ±0.001 rounding artifact.
- **Table 2 (Disagreeing rows, `RESULT.md:26-45`)**: 20 rows × 13 data cells = 260 cells. 253 match identically; 7 cells have a ±0.001 rounding artifact.
- **Table 3 (Class base rates, `RESULT.md:50-73`)**: 24 rows × 9 data cells = 216 cells. 213 match identically; 3 cells have a ±0.001 rounding artifact.

### Root Cause of the 11 Discrepancies:
In `study.py:262-263`, Pandas exports the CSVs using `float_format="%.4f"`, which rounds floating point values to 4 decimal places before writing to disk. When `RESULT.md` was created in `study.py:155` (`f3(x)` returning `"%.3f" % x`), the formatting operated directly on the full-precision in-memory floats.
Every discrepancy occurs exclusively on numbers where the 4th decimal place in the CSV is 5:
- In Python, `round-to-even` or binary float representation of `0.xxx5` rounds down when formatted to 3 decimals from CSV.
- The underlying rational fraction from the integer counts (e.g. $87 / 214 = 0.406542...$) strictly rounds to the value recorded in `RESULT.md`.

### Complete Diff Table (All 11 Differences)

| Table | Row Key | Field | SOURCED (`RESULT.md`) | OURS (`CSV` 3-dec) | OURS (`CSV` raw 4-dec) | Exact Fraction ($k/n$) | Diff | Status / Explanation |
|---|---|---|---|---|---|---|---|---|
| Agreeing | `near_miss 5m 001` | ETH p | `0.407` (`RESULT.md:20`) | `0.406` (`sequences.csv:11`) | `0.4065` | $87/214 = 0.406542...$ | +0.001 | Minor rounding artifact ($87/214$ rounds to $0.407$) |
| Disagreeing | `near_miss 1m 100` | BTC pB | `0.190` (`RESULT.md:32`) | `0.191` (`sequences.csv:4`) | `0.1905` | $20/105 = 0.190476...$ | -0.001 | Minor rounding artifact ($20/105$ rounds to $0.190$) |
| Disagreeing | `near_miss 1m 100` | POOL p | `0.271` (`RESULT.md:32`) | `0.272` (`sequences.csv:4`) | `0.2715` | $158/582 = 0.271477...$ | -0.001 | Minor rounding artifact ($158/582$ rounds to $0.271$) |
| Disagreeing | `near_miss 1m 101` | BTC p | `0.299` (`RESULT.md:33`) | `0.298` (`sequences.csv:5`) | `0.2985` | $123/412 = 0.298543...$ | +0.001 | Minor rounding artifact ($123/412$ rounds to $0.299$) |
| Disagreeing | `near_miss 1m 101` | POOL CI hi | `0.326` (`RESULT.md:33`) | `0.327` (`sequences.csv:5`) | `0.3265` | Wilson upper bound | -0.001 | Minor rounding artifact |
| Disagreeing | `near_miss 5m 000` | POOL p | `0.289` (`RESULT.md:36`) | `0.288` (`sequences.csv:10`) | `0.2885` | $73/253 = 0.288537...$ | +0.001 | Minor rounding artifact ($73/253$ rounds to $0.289$) |
| Disagreeing | `wick_back 15m 110` | POOL base | `0.364` (`RESULT.md:41`) | `0.363` (`sequences.csv:43`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Minor rounding artifact ($381/1048$ rounds to $0.364$) |
| Disagreeing | `wick_back 15m 111` | POOL base | `0.364` (`RESULT.md:42`) | `0.363` (`sequences.csv:44`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Minor rounding artifact ($381/1048$ rounds to $0.364$) |
| Class base | `POOL near_miss 1h` | pA | `0.390` (`RESULT.md:55`) | `0.391` (`classes.csv:42`) | `0.3905` | $82/210 = 0.390476...$ | -0.001 | Minor rounding artifact ($82/210$ rounds to $0.390$) |
| Class base | `POOL wick_back 15m` | p | `0.364` (`RESULT.md:64`) | `0.363` (`classes.csv:45`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Minor rounding artifact ($381/1048$ rounds to $0.364$) |
| Class base | `ETHUSDT wick_back 5m` | pB | `0.391` (`RESULT.md:73`) | `0.392` (`classes.csv:32`) | `0.3915` | $101/258 = 0.391472...$ | -0.001 | Minor rounding artifact ($101/258$ rounds to $0.391$) |

Zero mismatches exist in sample counts, agreement tags, or regime totals. All 11 diffs are bounded within $[-0.001, +0.001]$ and stem entirely from floating point truncation during CSV export.

---

## 4. Verification Check

Running verification command:
`python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_MS_LEVEL_ETH.md'); assert p.exists() and len(p.read_text())>400 and 'VERDICT' in p.read_text()"` exits 0.

VERDICT: MATCH
