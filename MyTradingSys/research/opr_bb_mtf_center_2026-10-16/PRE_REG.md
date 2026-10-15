# PRE-REGISTRATION: OPR-BB-MTF-CENTER screen (1h touch of the BB(20,2) mid in a lower-band trend) + Krown range tests M1-M4, BTCUSDT, DEV only (frozen 2026-10-16)

**Screen, ran before G3 marks by operator decision 2026-10-16.** The operator's message "we need all layers... get everything on track" was read by the coordinator as a yes to run the four
chart-read G5 cards as screens before eye-read marks exist (the default had been to hold). Status: EXPLORATORY SCREEN, DEV-only exploration. Nothing here adopts a rule.
Card `opr-bb-mtf-center-g5`, drafts `research/setup_catalog_2026-10-15/drafts/OPR-BB-MTF-CENTER.md` and `KRW-RANGE-BB-MAP.md`, evidence `evidence/bb_mtf_center_checks.py`.
The commit that adds this file precedes the commit that adds `RESULT.md`. Template: `research/gross_effect_screen_2026-10-15/PRE_REG.md`; economics and statistics identical to `opr_preopen_tops_2026-10-16/PRE_REG.md` s.1 and s.4.

Labels: SOURCED = the operator's words in the draft ("candles close around the centre and the selling pressure eases"; "closes above or below it decide direction, confirmation or a range"; next 1-4 h) or a repo file:line.
OURS = judgement or default chosen here before any outcome was computed. The operator states NO entry, stop or target; every trade parameter is OURS. Krown's extracts are T3 (definitions, no sample): the M tests only show how our data behaves when his definitions are made mechanical.

## 1. Economics
Tape Binance USD-M BTCUSDT 1m klines, DEV = bars before 2024-07-01 (loader refuses later bars). Round trip 0.14 % (2 x (5 bp taker fee + 2 bp slippage)), SOURCED (template). Funding: raw_fund absent -> flat 1 bp per 00/08/16 UTC settlement crossed, `funding NOT_IN_DATA` (OURS).
Decision at the close of the 1h touch bar, fill at the open of the second following 1m bar (d = 1), fixed-horizon exit, no stop, no target (OURS, template). OI NOT_IN_DATA on DEV; CVD level not used (windowed delta only). Bars are CLOSED bars aggregated from 1m (a bar with any missing 1m bar is dropped; DEV has 0 missing).

## 2. Definitions (BB(20,2) = SMA20 of closes +/- 2 population SD, the chart legend; ATR plain SMA of TR, FORMULAS.md s.12; RSI Wilder, s.1)
- Lower-band trend precondition (OURS): at least N = 6 consecutive closed 1h bars close below their own BB mid (grid N = 3, 6, 12; **primary 6**) AND the 1h mid at the previous bar is lower than 6 bars earlier.
- Touch (OURS): the 1h bar's high >= its own BB mid (**primary = wick**); variants: high within 0.10 / 0.25 half-widths of the mid; the bar closes above the mid.
- First touch only (OURS): the first touch after the precondition was met (touches inside the first N bars of the run do not count as earlier touches; later touches in the same run are not events). Event = touch bar; decision time = its close.
- U / D / R (draft outcome, descriptive): within H = 1, 2, 4 h after the touch-bar close, the 1m tape reaches the touch bar's UPPER band value (U, "counter-trend") or LOWER band value (D, "trend continuation") first, bands fixed at the touch bar; R = neither; both in one minute are counted and printed separately.
- 30m centre-close condition (OURS): the last m = 2 closed 30m bars at the touch-bar close all closed within +/- y = 0.25 half-widths of their own 30m mid (grid m = 2, 3; y = 0.25, 0.5). Primary combination (2, 0.25); ON/OFF tables printed. "Selling pressure eases" (OURS, two measures printed separately): 30m taker delta over the last 4 bars >= 0; 30m RSI14 above its value 4 bars earlier.
- Controls (OURS): mirror (up-trend: N closes above the mid, rising mid, touch by the LOW); touch of the 30m mid (N = 6, 30m bars); same trend state at random hours (seed 0, up to 3,000 bars, no touch required); wick touch of the 1h mid with no precondition. Splits: touch-bar taker delta sign, decision within 0-60 minutes after the 09:30 New York open (weekdays), BB width above/below the DEV median.

## 3. Verdict arms (primary cell h = 120 minutes after the entry open, OURS = middle of the draft's 1/2/4 h; printed for 60 and 240)
- **AU**: first-touch event whose touch bar closes ABOVE its own mid ("confirmation") -> LONG at that close. Control = wick touches of the 1h mid with no precondition that also close above the mid, same cooldown.
- **AD**: first-touch event whose touch bar closes BELOW its own mid ("rejection") -> SHORT at that close. Control = wick touches with no precondition that close below the mid.
- Both ledgers carry a 120-minute cooldown (OURS = the horizon). Fee-net cost 0.14 % as above. The operator's draft asks for two plain rules "only if the frequencies show something"; the brief orders the costed screen regardless, so both are run and the U/D/R frequencies are printed beside them.

## 4. Pass rule (template s.4, fixed now; day-clustered SE by UTC day of entry)
**PASS** iff n >= 200 and mean G (after funding) >= 0.14 % and t_cost >= 2 and DIFF vs control >= +0.05 % and t_DIFF >= 2 and arm MDD <= buy-and-hold DEV MDD. **INCONCLUSIVE** iff n < 200, MDE (2.8 x SE) printed, never relabelled FAIL. **FAIL** otherwise.
Study word = PASS if AU or AD passes; FAIL only if both are FAIL; otherwise INCONCLUSIVE. N_MIN = 200 and every threshold are not changed after the first outcome is read. All computed cells are printed (trials.csv, RESULT.md).

## 5. Krown M1-M4 (descriptive tables only, no verdict, 1h and 4h; definitions `KRW-RANGE-BB-MAP.md` s.4, every number OURS)
- M1 range detector: greedy non-overlapping n-bar windows (n = 24, 48, 96) whose high zone (within x of the window high; x = 0.25 %, 0.5 %) and low zone each have >= 2 separate reactions; counts and median heights printed for the grid. **Primary range definition for M2-M4: n = 48, x = 0.5 %.**
- M2: in those ranges, the share of bars with both BB bands within y (0.25, 0.5, 1.0 %) of the range high/low, and with the BB mid within y of the range midpoint, against the same statistics on random same-length windows that fail the range test (seed 0, same count).
- M3: pokes beyond a range edge (first one within 24 bars after the window) that close back inside within k = 1, 2, 3 bars: share reaching the opposite range edge and the opposite BB band (fixed at the close-back bar) within 24 bars, against the first close outside the BB band reaching the opposite band within 24 bars.
- M4: after a bar touches the range midpoint (or the BB mid inside the range), the share of the next 1, 2, 3 closes above it, split by approach from below/above (touches within one range overlap; descriptive).

## 6. Counts, printed before any outcome was computed (`COUNT.md`, `python study.py --count`)
First-touch events (1h, N = 6, wick): **n = 476** (closing above the mid 194, below 282); wick N = 3: 571, N = 12: 327; near 0.10: 459, near 0.25: 444; close rule: 499; mirror 500; 30m-mid touches 1,014.
Verdict arms after the cooldown: **AU n = 194 (control 3,952), AD n = 282 (control 1,572)**. **AU is below the 200 bar, so AU is INCONCLUSIVE by the pre-registered rule whatever its outcome**; AD is decided by its outcome columns.
Because the study word is FAIL only if both arms are FAIL, an AD FAIL with AU INCONCLUSIVE yields INCONCLUSIVE for the study; the AD row then carries the information. Krown ranges (1h): n=48, x=0.5 %: 291 windows; (4h): 58.

## 7. Data split, traps and tests
DEV only; VALIDATION and HOLDOUT not read. Traps as in the template s.7: features at the closed bar and fills later; closed bars only (the draft's forming-bar convention is for live reading); shared cooldown; overlapping outcomes handled by day clustering; U/D/R bands fixed at the touch bar (no moving bands); a Binance-tape result says nothing about Deribit fills.
`test_study.py` (hand-computed synthetic bars): wick event after N closes below and NOT an event under the 'close' rule; first touch only and the precondition length (N = 6 / 3 / 12 give different first touches); slope condition; 'near' rule; mirror; U/D/B/R/X classification; range detector needs >= 2 reactions per side. A mutant that removes the first-touch bookkeeping fails the test.

## 8. Outputs
`study.py`, `test_study.py`, `COUNT.md`, `RESULT.md` (verdict word first), `trials.csv`, `ledger.csv`, `EXPOSURE_LEDGER.csv`.
