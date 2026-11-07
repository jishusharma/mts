# Blind Read Audit: `level_approach_eth_2026-11` (`RESULT.md` vs CSVs)

- **Card**: `gemini-blind-read-ms-level-eth`
- **Audited Study**: `MyTradingSys/research/level_approach_eth_2026-11/RESULT.md`
- **Raw CSV Inputs**: `sequences.csv` (124 rows; 64 `near_miss`/`wick_back` rows), `classes.csv` (48 rows; 24 `near_miss`/`wick_back` rows), `regime_mix_dev.txt`
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini (independent blind read worker)

## 1. Headline Counts & Regime Mix Verification

- **Study nature**: SOURCED `RESULT.md:1` / `study.py:7`: Descriptive, fee-free study (no fee-net or trading costs applied). Metrics evaluated: sample counts $n, n_A, n_B$, duration/mix (weeks), hit proportions $p, p_A, p_B$, and Wilson score 95% confidence intervals.
- **64 `near_miss` / `wick_back` sequence rows in `sequences.csv`**:
  - `AGREES`: SOURCED `RESULT.md:5` (4 AGREE) vs OURS `sequences.csv` = 4 rows -> **MATCH**
  - `DISAGREES`: SOURCED `RESULT.md:5` (20 DISAGREE) vs OURS `sequences.csv` = 20 rows -> **MATCH**
  - `UNDERPOWERED`: SOURCED `RESULT.md:5` (40 UNDERPOWERED) vs OURS `sequences.csv` = 40 rows -> **MATCH**
  - Total: $4 + 20 + 40 = 64$ rows -> **MATCH** (`RESULT.md:5`)
- **Regime mix (`RESULT.md:7` vs `regime_mix_dev.txt`)**:
  - SOURCED `RESULT.md:7`: `Regime mix: POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%))`
  - OURS `regime_mix_dev.txt:1-3`:
    - Line 1: `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`
    - Line 2: `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)`
    - Line 3: `POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%)`
  - Formatted match: **MATCH** (exact string equivalence).
- **Reproduction check (`RESULT.md:10`)**:
  - SOURCED `RESULT.md:10`: `BTC futures through the unchanged C15 code: 10822 events (C15 shipped 10822); 32 kind x class x TF cells compared with the shipped tables.csv, 0 n mismatches.`
  - OURS `study.py:28` / C15 reproduction check: 10822 events, 32 cells, 0 n mismatches -> **MATCH**.
- **Invalidation row (`RESULT.md:13`)**:
  - SOURCED `RESULT.md:13`: `near_miss 1m, RSI<50, CVD12<=0, below daily BB mid: BTC n 466 p 0.210 (A 0.222 / B 0.176); ETH n 423 p 0.281 (A 0.287 / B 0.275); pooled n 889 p 0.244 vs pooled base 0.278; AGREES.`
  - OURS `sequences.csv:2`: BTC n=466 p=0.2103 (pA=0.2222, pB=0.1758); ETH n=423 p=0.2813 (pA=0.2868, pB=0.2745); POOL n=889 p=0.2441, POOL base=0.278; agreement=AGREES -> **MATCH**.

## 2. Table-by-Table Cell Recomputation & Diff Analysis

All 48 table rows in `RESULT.md` (4 Agreeing, 20 Disagreeing, 24 Class base rates) comprising 528 discrete metric cells were recomputed directly from `sequences.csv` and `classes.csv`.

Across the 528 cells:
- 517 cells (97.9%) match identically down to the 3rd decimal place.
- 11 cells (2.1%) show an exact difference of ±0.001.
- Cause of diffs: `study.py:262-263` exported CSVs using `float_format="%.4f"`, truncating intermediate values to 4 decimal places before writing to disk, whereas `study.py:155` generated `RESULT.md` directly in-memory from full IEEE 754 float precision using `"%.3f" % x`. Every single discrepancy is an exact boundary case where the 4th decimal place in the CSV is 5 (e.g. `0.4065`, `0.1905`, `0.2715`, `0.2985`, `0.3265`, `0.2885`, `0.3635`, `0.3905`, `0.3915`).

### Per-Cell Discrepancy Table (11 boundary rounding diffs)

| Table | Row | Metric | SOURCED (`RESULT.md`) | OURS (`CSV` 3-dec fmt) | OURS (`CSV` raw 4-dec) | Exact Unrounded | Diff | Analysis |
|---|---|---|---|---|---|---|---|---|
| Agreeing | `near_miss 5m 001` | ETH p | `0.407` (`RESULT.md:20`) | `0.406` (`sequences.csv:11`) | `0.4065` | $87/214 = 0.406542...$ | +0.001 | Rounding artifact ($87/214$ rounds to $0.407$) |
| Disagreeing | `near_miss 1m 100` | BTC pB | `0.190` (`RESULT.md:32`) | `0.191` (`sequences.csv:4`) | `0.1905` | $20/105 = 0.190476...$ | -0.001 | Rounding artifact ($20/105$ rounds to $0.190$) |
| Disagreeing | `near_miss 1m 100` | POOL p | `0.271` (`RESULT.md:32`) | `0.272` (`sequences.csv:4`) | `0.2715` | $158/582 = 0.271477...$ | -0.001 | Rounding artifact ($158/582$ rounds to $0.271$) |
| Disagreeing | `near_miss 1m 101` | BTC p | `0.299` (`RESULT.md:33`) | `0.298` (`sequences.csv:5`) | `0.2985` | $123/412 = 0.298543...$ | +0.001 | Rounding artifact ($123/412$ rounds to $0.299$) |
| Disagreeing | `near_miss 1m 101` | POOL CI hi | `0.326` (`RESULT.md:33`) | `0.327` (`sequences.csv:5`) | `0.3265` | Wilson upper bound | -0.001 | Rounding artifact |
| Disagreeing | `near_miss 5m 000` | POOL p | `0.289` (`RESULT.md:36`) | `0.288` (`sequences.csv:10`) | `0.2885` | $73/253 = 0.288537...$ | +0.001 | Rounding artifact ($73/253$ rounds to $0.289$) |
| Disagreeing | `wick_back 15m 110` | POOL base | `0.364` (`RESULT.md:41`) | `0.363` (`sequences.csv:43`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Rounding artifact ($381/1048$ rounds to $0.364$) |
| Disagreeing | `wick_back 15m 111` | POOL base | `0.364` (`RESULT.md:42`) | `0.363` (`sequences.csv:44`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Rounding artifact ($381/1048$ rounds to $0.364$) |
| Class base | `POOL near_miss 1h` | pA | `0.390` (`RESULT.md:55`) | `0.391` (`classes.csv:42`) | `0.3905` | $82/210 = 0.390476...$ | -0.001 | Rounding artifact ($82/210$ rounds to $0.390$) |
| Class base | `POOL wick_back 15m` | p | `0.364` (`RESULT.md:64`) | `0.363` (`classes.csv:45`) | `0.3635` | $381/1048 = 0.363549...$ | +0.001 | Rounding artifact ($381/1048$ rounds to $0.364$) |
| Class base | `ETHUSDT wick_back 5m` | pB | `0.391` (`RESULT.md:73`) | `0.392` (`classes.csv:32`) | `0.3915` | $101/258 = 0.391472...$ | -0.001 | Rounding artifact ($101/258$ rounds to $0.391$) |

## 3. Summary of Agreement Classifications

- All 4 `AGREES` classifications match `sequences.csv` lines 2, 3, 11, 59.
- All 20 `DISAGREES` classifications match `sequences.csv` lines 4, 5, 6, 7, 10, 12, 13, 14, 15, 27, 28, 29, 39, 43, 44, 45, 51, 60, 61, 63.
- All 40 `UNDERPOWERED` classifications match `sequences.csv`.
- Zero structural, mathematical, or classification discrepancies exist.

VERDICT: MATCH
