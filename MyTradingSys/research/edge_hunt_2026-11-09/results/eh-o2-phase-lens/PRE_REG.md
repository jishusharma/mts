# PRE_REG eh-o2-phase-lens (trials T14, T15) - written before any return is computed

Worker: eh-o2-phase-lens (Opus 5.5), wave 3 of edge hunt 2026-11-09. Plan: ../../PLAN.md; trials: ../../TRIALS.md (m = 15).
Operator lens: L6 (cycle clock), L1 (HTF RSI 40/60, "what phase the Bitcoin is in"), L7 (phase-first).

## Context
- Regime: PHASE_LABEL = cycle phase (BTC cycle clock, point-in-time) x last closed weekly RSI14 zone (HIGH > 60, MID 40..60, LOW < 40). The research_kit regime tag is reported as the `Regime mix:` line only.
- Phase: T14 only in the balance cell (zone MID, phase not PEAK_WINDOW, not BOTTOM_WINDOW); T15 only in ACCUMULATION or BULL with zone MID or HIGH.
- Session: none, because neither rule names a session (T14 is a prior-UTC-day level rule, T15 a 4h RSI rule).
- Entry: signal bar close, taker (T14: the reclaim close; T15: the MLK-S1 signal bar close).

## Trials (frozen in TRIALS.md; not split, not re-cut)
- **T14**: BTC 1h futures level fade (sweep of prior UTC day high/low and close back inside within 3 bars) in the balance cell; primary statistic mean net R per trade, SE clustered by UTC day.
- **T15**: MLK-S1 4h RSI-40 bounce long (malkan_40_60.malkan_setup_bull) on BTC+ETH spot 4h, only in ACCUMULATION/BULL with weekly zone MID/HIGH; mean net R, SE clustered by ISO week.

## Rules table (copied from the brief, frozen)
| Item | Rule | Label |
|---|---|---|
| Cycle phase | ACCUMULATION = known bottom -> next halving; BULL = halving -> halving + 548 d, or until a known peak; PEAK WINDOW = halving + 372..548 d (cycles 1-3 halving-to-peak range); BEAR = known peak -> peak + 406 d; BOTTOM WINDOW = peak + 363..406 d | day counts SOURCED (BIBLE.md:8-10, cycles.md:6-8, 13); phase names and the knowability rule OURS |
| Weekly RSI zone | last closed weekly RSI14: > 60 HIGH, 40..60 MID, < 40 LOW | lines SOURCED (Malkan, research_kit.py RSI_BULL/RSI_BEAR, MALKAN_RULES_2026-10-31.md:11-16); zone use OURS |
| Balance cell (T14) | weekly zone MID AND phase not PEAK WINDOW and not BOTTOM WINDOW | OURS |
| T14 event | BTC 1h: a bar trades beyond the prior UTC day high/low after the close 12 bars earlier was inside, and closes back inside within 3 bars; enter at that close (taker), stop at the extreme, 2R, 24 bars; one event per level per day | auction census FAST_REJECTION in kind, no classifier; OURS |
| T15 event | MLK-R1 S1 long at 40 exactly as malkan_40_60.py defines it on 4h (malkan_regime lookback 20, rsi_events level 40 tol 2 "support", regime BULL, green candle; malkan_40_60.py:4-8, :63-66 citing WEB_RESEARCH.md lines 108-134), stop at the signal swing low, 2.5R, 30 bars, only in ACCUMULATION or BULL with weekly zone MID or HIGH | malkan_40_60 SOURCED; phase filter and exit OURS |
| Exploratory | T14 and T15 events in every other phase cell (net R per cell); the phase calendar per week since 2017 | cannot promote |

## Knowability rule (OURS; tested in test_phase_label.py)
Inputs at bar time t: the halving dates (scheduled by block height; treated as known in advance, OURS) and BTC spot daily bars that CLOSED before t. The turn dates in cycles.csv are never read by phase_label; they are used only in a test that checks the point-in-time detector finds them, and to print a hindsight calendar for comparison.
Let H = last halving <= t, Hn = next halving, dH = days since H.
1. Provisional peak P(t) = the day of the highest daily high over closed days from max(H, data start) to t. A peak is **known** at t when t - P(t) >= 363 d (no new high for 363 days; the brief's "known only after the bar 363 days later").
2. Post-peak state = (dH > 548) or (a known peak exists). Outside it: dH < 372 -> BULL; 372 <= dH <= 548 -> PEAK_WINDOW.
3. Inside the post-peak state, reference peak p = P(t). Bottom candidate = lowest daily low over closed days in (p, t). The bottom is **known** once a later closed daily close >= 2 x that low (100 % rally off the low, OURS). Known bottom -> ACCUMULATION until Hn.
4. Else, d = t - p: d < 363 -> BEAR; 363 <= d <= 406 -> BOTTOM_WINDOW; d > 406 -> TRANSITION (OURS: the clock's bottom window has passed and no bottom is confirmed yet; the brief's five names leave this gap open).
5. No data / RSI warm-up -> zone None (cell "n/a").
Expected (hindsight check, not used by the label): peak 2017-12-17 known 2018-12-15; peak 2021-11-10 known 2022-11-08; bottom 2018-12-15 known on the first close >= 6312.52; bottom 2022-11-21 known on the first close >= 30952.

## OURS fills (chosen once, never tuned)
- DECISION (OURS): halving dates are known in advance (block schedule); ACCUMULATION ends at the actual halving day.
- DECISION (OURS): the clock and the weekly zone use BTC spot 1d (2017-08-17+), resampled to weeks Monday 00:00 UTC; a weekly value is usable only at or after its week close (next Monday 00:00 UTC). The first partial week (2017-08-14) is kept.
- DECISION (OURS): T15 ETH events use the BTC cycle phase and ETH's own weekly RSI zone (Malkan's HTF gate is read on the traded chart).
- DECISION (OURS): T14 "closes back inside within 3 bars" = the breach bar or one of the next 2 bars closes strictly inside (L_prev < close < H_prev); the stop is the extreme (max high / min low) from the breach bar to the reclaim bar; "12 bars earlier" = close[i-12] with L_prev <= close <= H_prev; first qualifying event per level per UTC day.
- DECISION (OURS): T15 "signal swing low" = the lowest low from the first bar of the RSI band run (RSI within 40 +- 2) through the signal bar.
- DECISION (OURS): exits are evaluated from the bar after entry; target and stop are touch-fills at the price, stop wins a same-bar tie; time stop at the close of bar entry+24 (T14) / entry+30 (T15), taker. All events taken (no one-position filter); overlap is handled by the clustered SE.
- DECISION (OURS): costs regime A = 2 x fees.DERIBIT_TAKER + fees.SLIPPAGE_RT_S13 (12 bps RT) on entry notional; fee_r = cost / stop fraction; funding R = side_sign x sum(rate over records in (t_in, t_out]) / stop fraction (FORMULAS.md:354-358). The futures fundingRate archive exists from 2020-01 (2019-09..12 files 404), so funding is 0 before 2020-01; T14 futures 1h data also starts 2020-01 (2019 monthly files 404).
- Splits: DEV = data start .. 2024-06-30; VALIDATION 2024-07-01 .. 2025-06-30 read once only if the DEV screen passes; HOLDOUT never loaded (loader refuses end > 2025-07-01, test shows it).
- Statistics: DEV screen n >= 30, mean net R > 0, 95 % CI lower > 0; SE = research_kit.cluster_mean_se; MDE = 2.8 x SE; verdict rules PLAN.md s5 / brief.

## Amendment 1 (written while coding the tests, still before any return or count)
- DECISION (OURS): T14 breach bar = the first bar of an excursion: close[i-1] inside the prior-day range (L <= close <= H) as well as close[i-12]; without it every bar of one excursion would be a new breach and the 3-bar reclaim window would slide.
- DECISION (OURS): the prior UTC day must have >= 20 hourly bars to define its high/low.
- DECISION (OURS): phase_calendar.csv covers DEV weeks only (2017-08-21 .. 2024-06-24); VALIDATION prices are read only if a trial passes the DEV screen.
- DECISION (OURS): the VALIDATION Holm test at m = 15 uses the conservative first-step bound min(1, 15 p) because the other trials p-values are not available to this worker; a pass under this bound is a pass under Holm.
- DECISION (OURS): an event whose exit needs bars past the split end is dropped and counted; T15 events with stop >= entry are dropped and counted.
