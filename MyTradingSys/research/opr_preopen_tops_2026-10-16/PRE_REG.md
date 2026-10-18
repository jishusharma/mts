# PRE-REGISTRATION: OPR-PREOPEN-TOPS break-speed screen, BTCUSDT 1m, DEV only (frozen 2026-10-16)

**Screen, ran before G3 marks by operator decision 2026-10-16.** The operator's message "we need all layers... get everything on track" was read by the
coordinator as a yes to run the four chart-read G5 cards as screens before eye-read marks exist (the default had been to hold). Status: EXPLORATORY SCREEN, DEV-only
exploration. Nothing here adopts a rule. Card `opr-preopen-tops-g5-dev-event-study-brea`, draft `research/setup_catalog_2026-10-15/drafts/OPR-PREOPEN-TOPS.md`.
The commit that adds this file precedes the commit that adds `RESULT.md` (`git log` is the proof). Template: `research/gross_effect_screen_2026-10-15/PRE_REG.md`.

Labels: SOURCED = the operator's words (quote in the draft) or a repo file:line. OURS = judgement or default, chosen here before any return was computed.
The operator's reads state NO entry, stop or target, so every trade parameter below is OURS.

## 1. Economics (all from the template, `gross_effect_screen_2026-10-15/PRE_REG.md` s.1; shared code `research/chart_read_g5_2026-10-16/common.py`)
| Item | Value | Label |
|---|---|---|
| Tape | Binance USD-M BTCUSDT 1m klines, `F:/MTS/data/tom_raw/klines`, DEV = bars before 2024-07-01 (loader refuses later bars) | SOURCED (template s.6) |
| Round-trip cost | 0.14 % = 2 x (5 bp taker fee + 2 bp slippage) | SOURCED (template s.1, `backtest/fees.py:27`) |
| Funding | `F:/MTS/Dumps/backtest/raw_fund` absent -> flat 1 bp per 00/08/16 UTC settlement crossed, printed `funding NOT_IN_DATA` | OURS (template) |
| Delay | decision at the close of the break bar; fill at the open of the second following 1m bar (d = 1 minute extra) | OURS (template s.3.2) |
| Gross effect | G = side x (p_out / p_in - 1) x 100, p_in = open[t+1+d], p_out = open[t+1+d+h] | SOURCED (template s.3.3) |
| Size / stops | 1,000 USDT clip, 1x, **no stop, no target**: fixed-horizon exit at h | OURS (template: this kind of screen has no stops) |
| OI | NOT_IN_DATA on DEV (metrics archive starts 2025-09-01); OI covariates are not run | SOURCED (template s.2) |

## 2. Event definition (draft parameter table; every number OURS unless marked)
- Days: Monday-Friday UTC dates of DEV (650). The open = 09:30 America/New_York converted to UTC (13:30Z EDT / 14:30Z EST). BTC has no cash open; using it is OURS (draft item 4). A weekday filter is OURS.
- Tops (OURS, the draft's first variant): confirmed 15m swing highs (strictly above the 3 bars to the left, >= the 3 bars to the right), bar open on or after 00:00Z of the day, third confirming bar closed before the open, no 15m high above the top between formation and the open (unbroken), top above the open price and at most 3 x ATR(14, 1h) (plain SMA of TR, FORMULAS.md s.12, last closed 1h bar) above it.
- Break (OURS, grid middle value of the draft): first 3m close, from the open to open + 390 minutes (US cash session length), above the top by >= 0.1 x ATR(14, 3m). If several tops break on the same 3m bar the lowest is the event. Events are then thinned by a 60-minute cooldown over the whole ledger (OURS, template 5.1 value).
- Speed (decision-time features only): S1 = minutes from the open to the break-bar close; S2 = (close of the break bar - lowest low of the previous 10 3m bars) / ATR(14, 3m); S3 = number of 3m bars from the open to the bar before the break with high >= top - 0.25 x ATR(14, 3m). Groups = DEV tertiles of the ledger: S1 and S3 quick/slow = lowest/highest tertile, S2 quick = highest tertile.
- **Primary definition = S1 only** (frozen). The draft's "choose the one of S1-S3 with the best DEV separation" is NOT done: that would be a forking path inside one screen. S2, S3 and a median split are computed and printed as secondary cells with no verdict.

## 3. Primary cell and arms
- Horizon: h = 60 minutes after the entry open (OURS: matches the template's only pre-registered horizon; the draft's "+1 h" is its first horizon). Printed for h = 60, 180, 390.
- **H1 (operator, signed)**: quick break (S1 lowest tertile) -> SHORT at the break close. Control = the other S1 groups, SHORT, same h.
- **H2 (operator, signed)**: slow break (S1 highest tertile) -> LONG at the break close. Control = the other S1 groups, LONG, same h.
- Covariates (OURS, descriptive): sign of taker delta over the break bar and the 3 bars before (delta = 2 x taker_buy_volume - volume, FORMULAS.md s.14); CVD level is not used.
- Descriptive frequencies with Wilson 95 % CI (cells with n < 10 are not read): close below the break close at +1 h / +3 h / +6.5 h; 15m BB(20,2) upper tagged within 6.5 h; next higher top exceeded by 0.1 within 6.5 h. MFE/MAE medians in ATR(14, 1h).
- Placebo, report only: the same side and hour 7 days earlier and later (lags printed).

## 4. Pass rule (template s.4, one arm vs its control; fixed now; day-clustered SE)
- Statistics: mean G (after funding), SE cluster-robust by UTC day of the entry, t_cost = (mean - 0.14) / SE, DIFF and t_DIFF by OLS of G on [1, arm] with day-clustered sandwich variance, arm MDD = peak-to-trough of cumulative (G - 0.14) in % of one clip vs the buy-and-hold DEV MDD in % of price (template convention). MDE at 80 % power = 2.8 x SE, printed.
- **PASS** iff n >= 200 and mean >= 0.14 % and t_cost >= 2 and DIFF >= +0.05 % and t_DIFF >= 2 and MDD <= MDD_BH. **INCONCLUSIVE** iff n < 200 (power), never relabelled FAIL. **FAIL** otherwise.
- Study word = PASS if any verdict arm (H1, H2) is PASS; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE. Two arms were tested; a PASS would still need a one-pass VALIDATION read by a separate card.
- The bar N_MIN = 200 is not lowered: see section 5.

## 5. Event counts, printed before any return was computed (`COUNT.md`, `python study.py --count`)
Ledger n = 308 break events from 650 weekdays (1,110 qualifying tops, 514 broken inside the session, 409 events before the cooldown). S1 tertile cut points 33 / 114 minutes;
arm sizes quick 105, mid 99, slow 104. **Both verdict arms have n < 200, so the pre-registered rule already makes the verdict INCONCLUSIVE whatever the outcome columns show.**
The full run is still executed to print the MDE, the descriptive frequencies and the secondary cells for the record. DECISION (OURS): no loosening of the top or break definitions to
buy power (that would be tuning on the count of a single idea); the follow-up if the operator wants a verdict is a larger event set (VALIDATION read by card, or the 4h-high tops variant), not this screen.

## 6. Data split and traps
DEV only. VALIDATION (2024-07-01..2025-06-30) and HOLDOUT (2025-07-01..2026-09-30) are not read. Traps handled as in the template s.7: decision at the bar close and fill later (no bar-open labels); cooldown on the shared ledger;
overlapping outcomes handled by day clustering; delta from windowed sums only; no stops (so no gap-fill trap); Binance-tape result says nothing about Deribit fills.

## 7. Outputs
`study.py`, `test_study.py` (fail-first, hand-computed synthetic bars), `COUNT.md`, `RESULT.md` (verdict word first), `trials.csv` (every cell computed), `ledger.csv`, `EXPOSURE_LEDGER.csv`.
