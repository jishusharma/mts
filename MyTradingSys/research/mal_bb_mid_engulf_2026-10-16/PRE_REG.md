# PRE-REGISTRATION: MAL-BB-MID-ENGULF screen (5m BB midline bounce, bearish engulf, second break), BTCUSDT, DEV only (frozen 2026-10-16)

**Screen, ran before G3 marks by operator decision 2026-10-16.** The operator's message "we need all layers... get everything on track" was read by the coordinator as a yes to run the four
chart-read G5 cards as screens before eye-read marks exist (the default had been to hold). Status: EXPLORATORY SCREEN, DEV-only exploration. Nothing here adopts a rule.
Card `mal-bb-mid-engulf-g5-dev-event-study`, draft `research/setup_catalog_2026-10-15/drafts/MAL-BB-MID-ENGULF.md`, evidence `evidence/bb_mid_engulf_checks.py`.
The commit that adds this file precedes the commit that adds `RESULT.md`. Template: `research/gross_effect_screen_2026-10-15/PRE_REG.md`; economics and statistics are identical to `opr_preopen_tops_2026-10-16/PRE_REG.md` s.1 and s.4.

Labels: SOURCED = the operator's words in the draft (close below the previous green bar's open; "breaks lower again"; HTF momentum) or a repo file:line. OURS = judgement or default, chosen here before any return was computed.
The operator's read states NO entry, stop or target: every trade parameter is OURS.

## 1. Economics (template s.1; code `research/chart_read_g5_2026-10-16/common.py`)
Tape Binance USD-M BTCUSDT 1m klines (DEV = bars before 2024-07-01; the loader refuses later bars). Round trip 0.14 % (2 x (5 bp fee + 2 bp slippage)) SOURCED (template). Funding: raw_fund archive absent -> flat 1 bp per 00/08/16 UTC settlement crossed, `funding NOT_IN_DATA` (OURS).
Decision at the close of the signal 5m bar, fill at the open of the second following 1m bar (template d = 1), fixed-horizon exit, **no stop, no target** (OURS, template). SHORT only (the operator's setup is bearish). OI NOT_IN_DATA on DEV; CVD level not used (windowed delta only).

## 2. Definitions (5m bars aligned to UTC, closed bars only; BB(20,2) = SMA20 of closes +/- 2 population SD, FORMULAS-consistent; RSI Wilder FORMULAS.md s.1; ATR plain SMA of TR, s.12)
- Falling market (OPERATOR idea, OURS test): 5m BB mid lower than 10 bars ago AND net taker delta (2 x taker_buy_volume - volume) over the last 6 bars < 0.
- Bounce to the midline (OPERATOR idea, OURS test): the high of one of the last 3 5m bars (including the signal bar) >= that bar's own BB mid - x x band width. **Primary x = 0** (wick touch); grid x = 0, 5 %, 10 %.
- Engulf, first confirmation: previous bar green, this bar red, **close below the previous green bar's open (variant (a), the operator's words) = primary**; (b) = (a) and the red open >= previous close; (c) = (a) and body >= r x previous body, r = 1, 1.5, 2 (OURS grid). Printed, never selected on outcomes.
- HTF filter (OURS, the draft's relay default): last closed 1h RSI14 < 50 AND last closed 4h RSI14 < 50 AND 5m close below the last closed 1h BB mid. **Primary = filter ON**; OFF is a printed variant.
- Second confirmation (OPERATOR "breaks lower again", OURS test): the next 5m bar trades below the engulf bar's low.
- Ledger: a 60-minute cooldown (OURS, template value) between events within each set.

## 3. Arms (both verdict arms use primary definitions only; h = 60 minutes after the entry open, OURS = the draft's +12 bars)
- **A1**: bounce state (falling, x = 0, HTF on) AND engulf (a) -> SHORT at the engulf-bar close. Control = bounce-state bars with NO engulf (a), same cooldown, same SHORT h = 60 (the draft's "bounce without engulf" control).
- **A2**: A1 events whose next bar trades below the engulf low -> SHORT at that next bar's close. Control = A1 events without the second break, entered at the same bar close (same elapsed time).
- Secondary, no verdict: h = 30, 120, 240; entry at a midline retest (first bar within 12 whose high >= the engulf-time mid, close entry); the variant grid (5 engulf variants x HTF on/off x x = 0, 5, 10 %, entry at the engulf close, no control); placebo (A1 side and hour 7 days earlier/later); share of trades with price lower after entry with Wilson CI; MFE/MAE in ATR(14, 5m) at +6/+12/+24 bars; 2 x 2 split by the engulf-bar delta sign and BB width expansion.

## 4. Pass rule (template s.4, fixed now; day-clustered SE by UTC day of entry)
**PASS** iff n >= 200 and mean G (after funding) >= 0.14 % and t_cost >= 2 and DIFF vs control >= +0.05 % and t_DIFF >= 2 and arm MDD (sum of net % of one clip) <= buy-and-hold DEV MDD. **INCONCLUSIVE** iff n < 200, with the MDE (2.8 x SE) printed. **FAIL** otherwise.
Study word = PASS if A1 or A2 passes; FAIL only if both are FAIL; otherwise INCONCLUSIVE. The bar N_MIN = 200 and every threshold above are not changed after the first outcome is read. Every computed cell is printed (trials.csv); two verdict arms and 37 secondary cells (6 horizon cells, 1 retest cell, 30 grid cells) are tested, so a lone PASS still needs a one-pass VALIDATION read by a separate card.

## 5. Counts, printed before any return was computed (`COUNT.md`, `python study.py --count`)
Falling bars 69,174; falling + wick touch of the mid 26,367; + HTF on 10,673. Ledgers after cooldown: engulf (a) **n = 1,179** (b 926, c r=1 1,179, r=1.5 973, r=2 831); control for A1 n = 2,486;
second break A2 n = 807; its control n = 372. All verdict arms have n >= 200, so the verdict depends on the outcome columns. The data has no missing 1m bars on DEV (0 of 1,313,280).

## 6. Data split and traps
DEV only; VALIDATION and HOLDOUT are not read. Traps as in the template s.7: features at the bar close, fills later; HTF values come only from CLOSED 1h/4h bars (test `test_htf_index_uses_closed_bars_only`); shared-cooldown ledger; overlapping outcomes handled by day clustering; no stops so no gap-fill trap; a Binance-tape result says nothing about Deribit fills.
Tests: `test_study.py` (hand-computed synthetic 5m bars: engulf (a) is true and (b) false when the red bar opens below the previous close, body ratios, bounce window, falling state, closed HTF bars, second break).

## 7. Outputs
`study.py`, `test_study.py`, `COUNT.md`, `RESULT.md` (verdict word first), `trials.csv`, `ledger.csv`, `EXPOSURE_LEDGER.csv`.
