# PRE-REGISTRATION: OPR-WEEKLY-LOW-ROUND-SWEEP screen (prior-week low and round-1000 breaks: reclaim, acceptance, range), BTCUSDT 1m, DEV only (frozen 2026-10-16)

**Screen, ran before G3 marks by operator decision 2026-10-16.** The operator's message "we need all layers... get everything on track" was read by the coordinator as a yes to run the four
chart-read G5 cards as screens before eye-read marks exist (the default had been to hold). Status: EXPLORATORY SCREEN, DEV-only exploration. Nothing here adopts a rule.
Card `opr-weekly-low-round-sweep-g5`, draft `research/setup_catalog_2026-10-15/drafts/OPR-WEEKLY-LOW-ROUND-SWEEP.md`, evidence `evidence/weekly_low_sweep_checks.py`. The card was parked as a GPT/NUC candidate ("heavy 1m study"); the 1m tape is only 1.3 M bars and the event finder is vectorised, so it runs here in about a minute and no NUC run card is needed.
The commit that adds this file precedes the commit that adds `RESULT.md`. Template: `research/gross_effect_screen_2026-10-15/PRE_REG.md`; economics and statistics identical to `opr_preopen_tops_2026-10-16/PRE_REG.md` s.1 and s.4.

Labels: SOURCED = the operator's words in the draft (events worth studying: breaks of the prior-week low and/or a round number; outcomes reclaim, acceptance, range) or a repo file:line. OURS = judgement or default chosen here before any outcome was computed.
The operator states NO entry, stop or target: every trade parameter is OURS. Related evidence for a DIFFERENT question (hold, not sweep-and-reclaim): `research/levels_confluence_2026-10-14/levels_hold.md` (round_1000 KEEP at n = 322, prior_week_low DROP at n = 20).

## 1. Economics
Tape Binance USD-M BTCUSDT 1m klines, DEV = bars before 2024-07-01 (loader refuses later bars). Round trip 0.14 % (2 x (5 bp taker fee + 2 bp slippage)), SOURCED (template). Funding: raw_fund absent -> flat 1 bp per 00/08/16 UTC settlement crossed, `funding NOT_IN_DATA` (OURS).
Decision at the close of the entry 1m bar, fill at the open of the second following 1m bar (d = 1), fixed-horizon exit, no stop, no target (OURS, template). OI NOT_IN_DATA on DEV (archive metrics start 2025-09-01; the 1m recorder starts 2026-10-05): OI conditions are not run. CVD level not used.

## 2. Event definitions (all closes/lows are 1m; the level is fixed when the event is detected)
- Levels (OURS): **prior-week low** = the low of the previous FULL Monday-Sunday UTC week (weeks before the first two full weeks have none); **round level** = the highest multiple of 1000 not above the lowest close of the previous 60 minutes.
- First break (OURS): a 1m low at least p below the level while ALL of the previous 60 closes were at or above it. **Primary p = 0.1 %**; grid p = 0, 0.1, 0.2, 0.3 %. Events are thinned by a 60-minute cooldown (per family; the pooled ledger is the union of both families with a global 60-minute cooldown, a weekly-low event wins a tie).
- Window: 60 minutes of 1m closes from the break bar (index 0) to index 60. Penetration depth = (level - lowest low in the window) / level.
- **A, reclaim** (draft, OURS numbers): the first close above the level at index r <= k (primary k = 5, grid 3, 5, 10, 15; the break bar's own close counts as index 0), AND no close below the level in the next 15 minutes, AND the reclaim comes before m consecutive closes below. **B, acceptance**: m consecutive closes below the level (primary m = 3; also 5) at any point in the window, and not A. **C**: neither (the share staying within 0.3 x ATR(14, 1h) of the level is printed). The classes are descriptive; they use information up to 15 minutes after the reclaim and are not tradeable as defined.
- Conditions (descriptive, 2 x 2 only; cells with n < 10 are not read): family (round / weekly), stacking within 0.1 / 0.25 / 0.5 % (round event vs the prior-week low at that time; weekly event vs the nearest round-1000), US-open window (break within 0-60 minutes after 09:30 New York on weekdays), HTF stretch (last closed 1h and 4h RSI14 < 35 and the 1m close below the last closed 4h lower BB(20,2); the draft's 1d band is not used), CVD flip (delta of the 5 bars before < 0 and of the 5 bars from the break > 0; descriptive only because it uses 5 bars after the break), break-bar taker delta sign.

## 3. Verdict arms (CAUSAL entries on the pooled ledger at p = 0.1 %; k = 5, m = 3; primary horizon h = 60 minutes after the entry open, OURS, printed for 30 and 120)
- **RL**: reclaim within 5 minutes (a close above the level at index r <= 5) -> LONG at that close. Control = first breaks with NO close above the level in indices 0-5, LONG at the close of index 5 (same elapsed time, "buy the dip anyway").
- **AS**: the first three closes (indices 0-2) all below the level -> SHORT at the close of index 2. Control = first breaks where they are not all below, SHORT at the close of index 2.
- The draft's "only if a conditional frequency beats the unconditional one" gate is not applied: the brief orders the costed screen regardless. Secondary, no verdict: horizons 30/120; round-only and weekly-only; stacked within 0.25 %; placebo (same side and hour 7 days earlier/later); after-A MFE/MAE in ATR(14, 1h) at +30/+60/+120 minutes and the 12 h high being exceeded; after-B MFE/MAE and the next round-1000 level below being reached.

## 4. Pass rule (template s.4, fixed now; day-clustered SE by UTC day of entry)
**PASS** iff n >= 200 and mean G (after funding) >= 0.14 % and t_cost >= 2 and DIFF vs control >= +0.05 % and t_DIFF >= 2 and arm MDD <= buy-and-hold DEV MDD. **INCONCLUSIVE** iff n < 200, MDE (2.8 x SE) printed, never relabelled FAIL. **FAIL** otherwise.
Study word = PASS if RL or AS passes; FAIL only if both are FAIL; otherwise INCONCLUSIVE. N_MIN = 200 and every threshold are not changed after the first outcome is read. Every computed cell is printed (trials.csv, RESULT.md).

## 5. Counts, printed before any outcome was computed (`COUNT.md`, `python study.py --count`)
Pooled ledger at p = 0.1 %: **n = 1,060** (round-1000 1,006; prior-week low 103). Other p: 0 %: 1,748; 0.2 %: 581; 0.3 %: 365. Weekly-low-only ledgers are 56-189 events, below the 200 bar, so every weekly-only cell is INCONCLUSIVE by rule;
stacked events within 0.25 % number 13 at p = 0.1 % (cells with n < 10 are not read). The sizes of the RL and AS arms depend on the 1m closes after each break (they are not return columns) and are printed with the outcome run.

## 6. Data split, traps and tests
DEV only; VALIDATION and HOLDOUT not read. Traps as in the template s.7: signals use closes up to the entry bar only (the A/B/C classes are descriptive and are NOT used to enter); fills later; cooldown on a shared ledger; overlapping outcomes handled by day clustering; the level is fixed at detection; a Binance-tape result says nothing about Deribit fills.
`test_study.py` (hand-computed synthetic 1m bars): prior Monday-Sunday week low; first-break rule with the previous-closes condition and penetration grid; A/B/C including the hold test and the k/m grid; reclaim index and immediate acceptance. A mutant that removes the 15-minute hold test fails the test.

## 7. Outputs
`study.py`, `test_study.py`, `COUNT.md`, `RESULT.md` (verdict word first), `trials.csv`, `ledger.csv`, `EXPOSURE_LEDGER.csv`.
