VERDICT: FAIL (M1, NK2 pivot reclaim, 1h SHORT-P, resting sell limit at pivot P). Maker net R per filled trade on VALIDATION is -0.037 (CI low -0.090 per trade, -0.126 per day); fill rate 65.5%; gates 2, 3, 5, 6 fail, gates 1 and 4 pass. Not THIN.

PRE_REG: ../PRE_REG.md (frozen, not edited). Original: nk2-pivot-sr-reclaim-1114 (study.py copied verbatim as nk2_orig.py; signals, levels, phase, ATR, stop and target rules unchanged).

## Context
Regime: original NK2 phase gate (coin-day UP/DOWN/RANGE from daily ADX14 + MA20 slope at D-1); SHORT matched = DOWN or RANGE only. Unchanged, nothing re-tuned.
Regime mix: VAL all coin-days UP 24.8% / DOWN 35.1% / RANGE 40.1%; VAL signals UP 0 / DOWN 47.1% / RANGE 52.9%; VAL filled trades UP 0 / DOWN 47.9% / RANGE 52.1%.

## Step 1: original taker baseline replicated (same signals, next-open entry, 12 bp)
| | Mine | Original RESULT |
|---|---|---|
| VAL n | 6102 | 6102 |
| VAL gross R | +0.101 | +0.101 |
| VAL net R 12bp | -0.009 | -0.009 |
| VAL net R 6bp | +0.046 | +0.046 |
| VAL win % | 46.2 | 46.2 |
| DEV n / net 12bp | 8634 / -0.139 | 8634 / -0.139 |
Exact match (3 decimals), so the signal code is the original.

## Step 2: mapping (only new logic, study.py)
- Signal at 1h bar i close (short: prev close > P >= close). Sell limit L = pivot P of that day, placed at bar-i close (above the signal close; needs a retest of P from below).
- Stop and target use the original rule with entry = L (min distance max(0.6 ATR14, 0.5% of L) vs 6-bar swing high; stop close-basis on 1m closes; target = nearest pivot level below L; R:R filter >= 1.0 re-applied at L). If the filter fails at L the order is not placed and counts as a miss (did not occur: all 2108 misses were no_through).
- Time stop: original code's 25 bars from the entry bar. Signal set = the original taker run's sequential one-position signals (kept fixed, so maker and taker are compared on identical signals; maker trades are not re-serialised).
- Fill/exit: lib/maker_fill.simulate_maker (through-by-one-tick, 60 x 1m order life, cancel if stop closes first, target one tick through, stop and time taker). Tick per symbol = smallest increment in its 1m data.

## Step 4 results (maker, 6 bp round trip mix: entry maker 3, target maker 3, stop/time taker 6)
| | DEV (reference) | VALIDATION |
|---|---|---|
| signals | 8634 | 6102 |
| fills / fill rate | 5849 / 67.7% | 3994 / 65.5% |
| gross R per filled | -0.044 | +0.049 |
| mean fee R per filled | 0.079 | 0.086 |
| net R per filled (maker) | -0.122 | -0.037 |
| net R per signal (miss = 0) | -0.083 | -0.024 |
| taker baseline net R, all signals, 12 bp | -0.139 | -0.009 |
| taker baseline gross R, all signals | -0.040 | +0.101 |
| CI low per trade / per UTC-day | -0.164 / -0.185 | -0.090 / -0.126 |
| ex best 5 UTC days | -0.145 | -0.080 |
| exits (stop_close / target / time) | 3665 / 1528 / 656 | 2427 / 1130 / 437 |

Adverse selection (VAL): the original model's gross R over the filled subset is -0.094 vs +0.101 over all signals, a gap of -0.195 R. Original-model taker net on the filled subset -0.205 vs -0.009 on all. Fills happen exactly when price rallies back up through P (the rejection fails); the signals that would have worked (price keeps falling, never retests P) are the 34.5% that go unfilled. The maker fee saving (about 0.04 R) is far smaller than the selection loss.

Placebo (like-for-like, same fill model, VAL, same symbol mix, limit at close + offset drawn from the real signals' (L - close)/ATR distribution, median 0.21 ATR): observed -0.037 vs placebo mean -0.097 (95th pct -0.051); p = 0.020 (1000 draws).

## Gates (VALIDATION)
| Gate | Result |
|---|---|
| 1 filled n >= 100 | PASS (3994) |
| 2 mean net R > 0 | FAIL (-0.037) |
| 3 bootstrap CI low > 0, trade and day | FAIL (-0.090, -0.126) |
| 4 placebo p < 0.05 | PASS (0.020) |
| 5 BH q 0.05 over 6 rows | FAIL provisional: only M1's p is known here, BH with the other 5 p set to 1 gives adjusted 0.120; the coordinator must recompute with all six p. Even if M1 survived BH, gates 2, 3, 6 fail. |
| 6 ex best-5 UTC days > 0 | FAIL (-0.080) |
FAIL, gates 2, 3, 5(provisional), 6.

## Reading
Maker entry at the rejected pivot does not rescue the idea: moving to a resting order costs a selection effect (-0.19 R) bigger than the fee saving. Gross per filled trade is only +0.049 and fee is 0.086. The placebo p passes only because random limits at the same offsets are worse still (the pool is negative), not because the row makes money.

## Notes, limits and flags
- Lib: 24 tests in lib/test_maker_fill.py pass; read in full, no genuine bug found, no change made. The only fix needed was in my runner (symbol name SYMUSDT for load_m1).
- Placebo uses a finite bank (12000 simulate_maker trials per symbol, filled ones kept, draws resample the filled bank with per-symbol counts equal to the real filled trades); same fill code via study.maker_trade. It is the same distribution as the draw-until-n_filled scheme but with finite-bank resampling noise. Per-symbol fill rate of the bank is about 35%.
- Placebo offsets pooled over all 20 symbols' VAL signals; offsets are all >= 0 by construction (L = P >= signal close).
- The fill bar may credit the target (fill_bar_target=True, as spec text "from the fill bar"); the stricter option was not run (result would only be worse for a short that is already net negative).
- Time stop uses 25 bars as the original code does (PRE_REG says 24h).
- 1m data has small gaps (up to 10 h on some symbols per fetch_log); not special-cased.
- Independent checker not yet run; the checks listed in PRE_REG (truncation look-ahead test in particular) are still open. Tests in test_study.py (6, pass) include touch-is-not-a-fill and signal-bar-not-used; both fail on the naive variants (tick=0 touch fill; signal close shifted back one bar), verified by monkeypatch.

Files: study.py, nk2_orig.py, test_study.py, run.py, analyze.py, raw_run.json, results.json, run_log.txt.
