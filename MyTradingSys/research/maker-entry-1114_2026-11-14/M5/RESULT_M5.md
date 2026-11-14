# RESULT_M5: NY value area, POC target, maker entry at the value edge

**Verdict: FAIL (all six gates fail; filled n = 72 on VALIDATION). Resting-limit entry at VAH does not rescue the near-miss cell: maker net R per filled trade -0.046 on VALIDATION, and the fills that happen are the losers (adverse selection -0.23 R).**

Row: M5, original = edge5-ny-value-poc-target-1113, best cell balanced / stop A (session extreme + 1 bp) / SHORT, pooled over the 10 new coins (BNB XRP DOGE ADA AVAX LINK LTC DOT TRX BCH), target = prior-NY-session POC, time exit at session end. PRE_REG.md (frozen spec) followed; nothing re-tuned. Code: study.py (new logic only: `limit_level`, `maker_signal`), orig_study5.py / parent_study.py (unchanged copies of the original, only the REPO path changed), test_study.py (3 pass).

Regime mix: BTC close vs 200d SMA (5% band) over the signal days, DEV 42.3% bull / 42.8% bear / 9.1% range (5.8% n/a, n=208); VALIDATION 58.0% bull / 24.7% bear / 17.3% range (n=162). All signals are balanced-day by construction (cell gate). Calendar-day mix: DEV 54/37/9, VAL 56/30/14 (bull/bear/range).

## Baseline replication (taker, original rule)
Same signals, entry at the signal-bar close, 12 bp, stop-first, recomputed from the original 1m data: n = 370, gross +0.0768 R, net -0.0063 R. Original RESULT.md: n = 370, gross +0.077, net -0.006. Match to 3 decimals (exact on n).

## Mapping and fill model (PRE_REG, unchanged)
Limit L = VAH (SELL limit above the market; the value edge price re-entered through). Order placed at the close of the signal 1m bar (second 30m close inside value). Signal, POC-distance >= 36 bp skip, min-stop guard and stop A are evaluated exactly as in the original at the signal close; stop, target (POC), time stop from L. Fill needs a later 1m high >= L + tick (tick = smallest 1m increment of the symbol), fill price L; life 30 x 1m; cancelled if the stop trades first; stop market (taker 6 bp), POC target resting (maker 3 bp), time exit taker; maker entry 3 bp. Misses = 0 R.

## Results (maker, filled trades)
| split | signals | filled | fill rate | gross R (maker, filled) | net R maker (filled) | net R per signal (miss = 0) | taker baseline net R (all signals) | adverse selection (orig gross, filled minus all) | trade CI 95% | day CI 95% | ex best 5 days |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV (to 2023-12-31, reference) | 208 | 96 | 46.2% | +0.089 | +0.005 | +0.002 | -0.012 | -0.186 | [-0.175, +0.204] | [-0.194, +0.218] | -0.158 |
| VALIDATION (2024+) | 162 | 72 | 44.4% | +0.039 | -0.046 | -0.021 | +0.001 | -0.232 | [-0.256, +0.169] | [-0.275, +0.204] | -0.246 |

On the filled subset the ORIGINAL taker model earns gross -0.146 R and net -0.240 R (VAL), against +0.086 gross over all VAL signals: the limit at VAH fills exactly when price runs up through the edge (toward the stop), and fills less when price falls straight to the POC. Maker fees take 0.085 R per filled trade (median risk from L is about 126 bp, since the stop sits beyond the session high). Exits on VAL fills: 23 target, 20 stop, 29 time. Misses (VAL): 81 never traded through L within 30 minutes, 9 had no 1m bars before the session end; 0 stopped before fill. Fill rate 44% so not THIN (< 30%).

## Gates (VALIDATION)
| # | gate | value | pass |
|---|---|---|---|
| 1 | filled n >= 100 | 72 | no |
| 2 | mean net R > 0 | -0.046 | no |
| 3 | CI lower > 0, trade and day | -0.256 / -0.275 | no |
| 4 | like-for-like placebo p < 0.05 | p = 0.425 (placebo mean -0.064, p95 +0.132; 1000 draws, same fill model, offset drawn from the real (L - close) in 30m ATR14 units) | no |
| 5 | BH q = 0.05 over the 6 rows | provisional (other five p unknown, set to 1): not rejected; cannot pass with gate 4 failing | no |
| 6 | mean net R > 0 without best 5 days | -0.246 | no |

Failed gates: 1, 2, 3, 4, 5, 6. Verdict FAIL.

## Notes and flags
- Placebo candidates: bars of the same VALIDATION balanced-short sessions (first entry bar 89 to session end, inside the value area, POC at least 36 bp away, stop A computed at that moment), pooled across the 10 coins, session drawn uniformly then a bar; limit = close + offset x ATR (passive side), same `simulate_maker`, same stop/target/time machinery.
- ATR unit (30m, 14 windows of 30 x 1m) is our choice, defined in `atr30`; the placebo p was not tuned.
- Data: the signals use the original 1m files (with volume, through 2026-10-31); fills use F:\MTS\data_cache\binance_1m (same bars, verified identical on BNB). Cell is the single best cell of the original (8 cells), so the original selection already favoured it; the maker result is therefore not an optimistic-bias-free test either way.
- Checker not run by this agent; the tests (test_study.py) show: limit is the value edge (not the close), the signal bar is never used (a naive variant starting at the signal bar fills where the correct one does not), a touch is no fill, fee by exit type = maker + maker for a target exit.
- Extra files: run_slot.py (slot wrapper), results.json (includes VAL trade log), per-symbol pickles in F:\MTS\maker_cache\M5 (outside the repo).
