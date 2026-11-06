# Blind read: oi_pivot run_1h4h.py (2026-11-06)

Independent blind read of `MyTradingSys/research/oi_pivot_2026-10-26/run_1h4h.py` for D11 feeder check (card `gemini-blind-read-oi-pivot-run-1h4h-py`).
Read order: `run_1h4h.py` and `candidates.py` read first before prose summaries (`PRE_REG_1H4H.md`, `RESULT_1H4H.md`).
Recomputed independently using raw 1m klines (`F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv`) and daily 5m metrics (`F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-*.csv`).
No files under read were edited; no VALIDATION or HOLDOUT data read (DEV cutoff strictly enforced at `2024-07-01 00:00:00 UTC`).

## Independent Recomputation & Audit Focus

1. **OI Pivot Rule**:
   - `oi_flip`: OI slope $s_i = \text{OI}_i - \text{OI}_{i-3}$ over $L=3$ bars (OURS, `candidates.py:5`). Evaluated on onset (`now - prev`, `candidates.py:119`), firing against the $L$-bar price move. If slope was flat, `_prev_sign` checks back up to 6 bars (OURS, `candidates.py:59-64`). Matches `PRE_REG.md:16`.
   - `pv_oi_div`: Divergence between $L$-bar price move and current OI slope $s_i$ (price up and $s_i < 0 \rightarrow$ TOP; price down and $s_i > 0 \rightarrow$ BOTTOM). Matches `PRE_REG.md:17`.
   - `delta_sign`: Delta opposes $L$-bar price move and $|\text{delta}| / \text{volume} \ge 0.2$ (OURS, `candidates.py:9,102`). Delta formula `2*tb - v` (SOURCED `FORMULAS.md`).
   - `vol_spike`: Volume $\ge 2 \times \text{mean}(\text{volume}_{i-20..i-1})$ (OURS, `candidates.py:7,104-107`).
   - Context: 4 bars lookback for 4h context at both 1h and 4h (OURS, `run_1h4h.py:22`, `PRE_REG_1H4H.md:15`).

2. **As-of Timing & Leakage Guards**:
   - D2 OI lag: A metrics row stamped $T$ is used only by bars closing at or after $T + 5\text{ min}$ (implemented in `candidates.py:44-50` with `OI_LAG_MS = 300_000` ms). For bar closing at $T_{\text{close}}$, the latest OI stamp queried is $\le T_{\text{close}} - 5\text{ min}$.
   - DEV cutoff guard: `T_END = 1719792000000` (`2024-07-01 00:00:00 UTC`, SOURCED `layer_lab/LAB_BLOCKED_2026-10-17.md:17`). `run_1h4h.py:26-28` enforces `_guard(bars)` which raises `ValueError` if any bar open is $\ge T_{\text{END}}$. `outcome` labels bars within $H=24$ bars of DEV end as `CENSORED`, and CENSORED events are excluded from probabilities. No bar at or beyond DEV cut is ever read or used.

3. **Cost Source**:
   - `run_1h4h.py` does NOT include trading fees or slippage (cost = 0.0, OURS, `PRE_REG_1H4H.md:29-34`).
   - Reason: This is an event probability study measuring barrier arrival rate $P(\text{HIT})$ vs baseline $P_{\text{base}}$, not an R-based trading strategy.
   - If evaluated as a trade, standard MTS taker fees (SOURCED `FORMULAS.md`, 0.05% per leg = 10 bps round-trip) plus slippage (2-4 bps) would amount to ~14 bps (or 0.14 R in `prereg_gate.py:7`). Because baseline is ~0.48 and powered candidate diffs are between -0.031 and +0.008 (unprofitable gross), applying trading fees would drive net expectancy strictly negative.

## Per-Claim Table

| # | Claim | Source (file:line) | Recomputed Value / Finding | Result |
|---|---|---|---|---|
| 1 | DEV Sample Window: BTCUSDT 2022-01-01 to 2024-06-30 UTC = 912 days | `PRE_REG_1H4H.md:12`, `run_1h4h.py:18` | 365 (2022) + 365 (2023) + 182 (2024 leap year) = 912 days (OURS) | MATCH |
| 2 | Total 1h bars: 21,888 | `PRE_REG_1H4H.md:40` | $912 \times 24 = 21,888$ bars (OURS) | MATCH |
| 3 | Total 4h bars: 5,472 | `PRE_REG_1H4H.md:40` | $21,888 / 4 = 5,472$ bars (OURS) | MATCH |
| 4 | 1h baseline $P_{\text{base}}$: BOTTOM 0.4855 / TOP 0.4770 | `PRE_REG_1H4H.md:41` | BOTTOM: $10609 / 21850 = 0.4855$; TOP: $10423 / 21850 = 0.4770$ (OURS) | MATCH |
| 5 | 4h baseline $P_{\text{base}}$: BOTTOM 0.4845 / TOP 0.4821 | `PRE_REG_1H4H.md:41` | BOTTOM: $2633 / 5434 = 0.4845$; TOP: $2620 / 5434 = 0.4821$ (OURS) | MATCH |
| 6 | Total candidate events: 14,421 over 28 non-empty cells | `PRE_REG_1H4H.md:42` | Sum of `n_events` in `pilot_1h4h_table.csv` = 14,421 across 28 non-empty cells (OURS) | MATCH |
| 7 | 4h `delta_sign` fires 0 times across all 4 cells | `RESULT_1H4H.md:6`, `PRE_REG_1H4H.md:42` | 0 events (OURS; $|\text{delta}| / \text{volume} \ge 0.2$ never met on 4h aggregated bars) | MATCH |
| 8 | Powered cells ($n_{\text{clusters}} \ge 401$): 10 of 32 cells | `RESULT_1H4H.md:4`, `PRE_REG_1H4H.md:43` | Exactly 10 cells reach $\ge 401$ day clusters (8 at 1h, 2 at 4h) (OURS) | MATCH |
| 9 | Powered cells ($n_{\text{clusters}} \ge 452$ today's gate): 10 of 32 cells | `PRE_REG_1H4H.md:43` | Exactly 10 cells reach $\ge 452$ day clusters (OURS) | MATCH |
| 10 | All 10 powered cells have $|z| < 2$ (diff -0.031 .. +0.008) | `RESULT_1H4H.md:4`, `PRE_REG_1H4H.md:45` | Range of $z$ is -1.88 to +0.49; diff range -0.0305 to +0.0082 (OURS) | MATCH |
| 11 | Most-clustered cell: 1h `oi_flip` OTHER WITH, $n_{\text{clusters}} = 836$ | `PRE_REG_1H4H.md:43` | $n_{\text{events}} = 2179$, $n_{\text{clusters}} = 836$, diff $+0.0042$, $z = +0.40$ (OURS) | MATCH |
| 12 | Largest gap overall: 4h `vol_spike` AT_LEVEL WITH, $P=0.3802$ vs $P_{\text{base}}=0.4833$, diff -0.1031, $z=-3.85$ (290 clusters, SHORT) | `RESULT_1H4H.md:5`, `PRE_REG_1H4H.md:46` | $n_{\text{events}} = 334$, $n_{\text{clusters}} = 290$, $P=0.3802$, $P_{\text{base}}=0.4833$, diff $-0.1031$, $\text{SE}=0.0268$, $z=-3.85$ (OURS) | MATCH |
| 13 | 1h `vol_spike` OTHER AGAINST: diff $+0.0502$, $z=+2.12$ (364 clusters, SHORT) | `PRE_REG_1H4H.md:47` | $n_{\text{events}} = 446$, $n_{\text{clusters}} = 364$, $P=0.5314$, $P_{\text{base}}=0.4812$, diff $+0.0502$, $\text{SE}=0.0236$, $z=+2.12$ (OURS) | MATCH |
| 14 | 32-cell table `pilot_1h4h_table.csv` reproduction | `pilot_1h4h_table.csv:1-33` | All 32 rows, 18 columns match independent recomputation to all decimal places (OURS) | MATCH |
| 15 | As-of timing D2: OI metrics lag $\ge 5\text{ min}$ | `candidates.py:11,44-50`, `PRE_REG_1H4H.md:7` | Queries OI stamped $\le \text{close\_ms} - 300\_000$; no future OI used (SOURCED `candidates.py:44`) | MATCH |
| 16 | Lookahead / DEV cutoff guard: no bar open $\ge 2024\text{-}07\text{-}01$ read | `run_1h4h.py:26-28`, `PRE_REG_1H4H.md:12` | Verified `_guard` and `outcome` CENSORED window $H=24$; 0 post-cut bars used (SOURCED `run_1h4h.py:27`) | MATCH |

## Defects and Observations

- **Defect 1 (`run_1h4h.py:16`)**: `CACHE` is hardcoded to `CACHE = Path("F:/MTS/data/oi_pivot_2026-10-26")`. On disk, this folder only contains 33 files (2024-05-29..2024-06-30) from the earlier 30-day pilot. The shared metrics repository at `F:/MTS/data/metrics/BTCUSDT/` (created by `fetch_futures_metrics.py`, shipped in commit `ea7db56d7b17`) already holds all 912 DEV files. Because `run_1h4h.py:73-77` downloads missing files from `data.binance.vision`, running `run_1h4h.py` as written makes 879 HTTP download calls rather than using the existing local shared metrics data.

## Verdict

All 32 cells of `pilot_1h4h_table.csv`, baseline rates, cluster counts, and statistical results quoted in `RESULT_1H4H.md` and `PRE_REG_1H4H.md` match the independent recomputation exactly. The OI pivot rule and D2 as-of timing are sound. One file-path defect is identified at `run_1h4h.py:16`.

VERDICT: MATCH
