# PRE_REG: level approach study (card level-approach-study-daily-last-lower-hi, candidate C15)

Written and frozen BEFORE any run or outcome read. `level_approach.py` refuses to run unless the last line is `FROZEN_UTC: ...` and writes this file's sha256 to its output. Descriptive, fee-free; no trade rule, no edge claim.

## Gate 0g (operator's own idea, 3 shots)
The idea is the operator's: "last lower high" line (highest high since the leg that made the latest lower low) and prior-day highs; his three shots 1bb324a9ad96, 19991af5d4a3, a83eefa84968 (10-28 09:00Z wick to 81.8k; 10-28 ~19:30Z near-miss under 81.8k; 10-29 ~15:30Z through 81.8k, missed 82,035.3 by 81.6, then -1.4k).
DECISION (OURS): the shots are Oct 2026 and the 1m archive ends 2026-09-26 and DEV ends 2024-06-30, so the classifier cannot be checked on the shots from this archive. Gate 0g is therefore recorded NOT CHECKED here; the shots become live_aid hand-checks (expected labels: near_miss, near_miss, close_then_fail) once the live mirror holds those days. His definition is encoded as written; every threshold below is OURS and labelled.

## Definitions
| Item | Value | Label |
|---|---|---|
| Data | BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines), complete UTC bars only; TF bars 5m/15m/1h resampled from 1m | OURS |
| DEV window | 2022-01-01 .. 2024-06-30 (loader refuses any bar at/after 2024-07-01). Half A < 2023-07-01 <= half B, used only as a consistency check. VALIDATION/HOLDOUT unread | SOURCED (project windows) |
| Prior-day high (pdh) | high of the previous UTC day | SOURCED (operator) |
| Last lower high (lh) | max high from the latest lower-low day j (low[j] < min of the 10 prior daily lows) through the previous day; dropped when equal to pdh | operator definition SOURCED; 10-day lookback OURS |
| Approach | armed after a TF close < level*(1-0.1 %); event = first bar with high >= level*(1-0.1 %); re-arm needs a close under that line | 0.1 % OURS |
| near_miss | event bar high < level | OURS |
| wick_back | high >= level, close <= level | OURS |
| close_then_fail | close > level and one of the next 3 TF closes < level (n_close = which one: 1st or 2nd/3rd) | 3 OURS (operator: "1st, 2nd close") |
| accepted | close > level and next 3 closes all > level | OURS |
| Forward | return of the close 12 TF bars after the anchor; anchor = event bar for near_miss/wick_back, event bar + 3 for the two through classes (classification is known only then, no look-ahead); p_above_level = share with that close > level | 12 OURS |
| Features at the event bar | RSI14 (Wilder) >= 50; CVD12 = sum of (2*taker_buy_vol - vol) over the last 12 bars > 0; close >= daily BB mid (SMA20 of prior daily closes) | OURS |
| OI | NOT_IN_DATA (klines carry no OI; no OI archive reaches 2022-24 here); C15's OI column is not run | stated |

## Outputs and inference
Per kind x class x TF: n, n per half, mean/median forward %, p_above_level with Wilson 95 % CI. Sequences: per class x TF, the 8 combos of the 3 binary features, n >= 30 only, with p per half; best confirm = highest p, invalidation = lowest. No bootstrap (events overlap within a day; Wilson CIs are therefore too narrow and are stated so).

## Verdict declared now
DESCRIPTIVE ONLY. 4 classes x 4 TFs x 8 combos = 128 cells looked at, no multiplicity correction: sequences are hypotheses for a later fresh-window test, never a core, never "edge". A sequence counts as worth a test only if both halves agree in direction and n >= 30 in each. 1m events overlap heavily; per-TF n is not independent trials.

## Not allowed
No threshold changes after the run; no extra levels; no window other than DEV.

FROZEN_UTC: 2026-11-05T00:00:00Z