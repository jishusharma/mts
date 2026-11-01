# C26 revalidation end to end (Lab_Guy, 2026-11-01): what stands, what contradicted what, where the edge can be, next steps

Operator 2026-11-01: "revalidate everything, remove contradictions, take what is useful, identify the edge, move tasks into the pipelines."
Sources read this turn: eagle-c26-magnet/ride/fade cards, C26_PRE_REG.md, PHASE1_RECENT.md, PHASE1_RANGE.md, rsi_divergence_mtf_2026-10-09,
eagle-c30-wt-rsi-div, eur_low_us_sweep_2026-10-14 (1-1-2-3 ladder), levels_confluence ladder_dev, orderflow_views (CVD), eagle-c24 / oi_side (OI),
wavetrend_2026-10-17 disposition, fees.py, splits.py, research_kit.py. Dates in brackets are the result dates.

## 1. What stands (measured more than once, or on a sealed period)
| fact | where | status |
|---|---|---|
| A held 15m level is taken within 24h 72 % vs 57-61 % control, both sides, both periods | eagle-c26-magnet [10-31] | REAL, not a trade |
| Trading the magnet with a tight stop loses the fee: arm A net -0.10 / -0.11 %, arm B -0.08 / -0.12 % (gross about 0, pooled regimes) | C26_PRE_REG.md [10-31] | NO, closed |
| After the take-out the phase decides: DOWN highs back to L1 60 %, median -0.94 % 24h later; UP highs 38 %, +0.13 % | PHASE1_RECENT.md [11-01] | design look, n 30 / 63 |
| Range above a taken DOWN high: 0.37 % median / 0.64 % 80th pct for the ones that came back; 30-45 % leave any affordable range | PHASE1_RANGE.md [11-01] | design look, n 30 |
| 1m-5m RSI-divergence shorts net about minus the fee (1m n 29,067, t -73); C30 bearish divergence shorts lose 62/65 cells | rsi_divergence_mtf RESULT.md [10-09], eagle-c30 [10-30] | NO, replicated |
| Ladders / martingales: 1-1-2-3 one-stop ladder t -0.32, 67-91 % drawdown at 10-20x; levels_ladder -0.119 R; ladder_dev all negative | eur_low_us_sweep, levels_confluence [10-14] | NO, three times |
| OI does not tell the next direction (C24 coin flip, oi_side 48-54 %, OI-divergence studies negative, Phase 1 "OI up" taken LESS) | 4 studies [09-21 .. 11-01] | consistent NO |
| WaveTrend as a trigger: no (atlas 4 FAIL / 5 inconclusive; dots no); WaveTrend OB at H1 leans "holds" (Phase 1) | wavetrend_2026-10-17, eagle-c27-29, PHASE1_RECENT | filter candidate only |
| CVD: price-vs-CVD divergence 0/12 arms, DEV-only rerun the same | orderflow_views [10-14, 10-17] | NO as a trigger |

## 2. Contradictions found and how they are resolved (each is now one rule)
1. "DEV decides" (card) vs "all history is seen" (C26_PRE_REG). Arms A/B read 2022-01..2026-10 pooled. Resolution: the regime split and the ladder
   are new rules, so DEV 2022-04..2024-06 is their FIRST LOOK, labelled SEEN-PERIOD; 2024-07..2026-06 is the one pre-registered confirmation look;
   the clean test stays FORWARD from the pre-reg date (n >= 30), as C26_PRE_REG says. No history run earns a "pass" label on its own.
2. DEV starts 2022-01-01 in `backtest/splits.py` but 2022-04-01 on the desk, the cards and the coordinator's brief. Resolution: 2022-04-01 (the desk
   lock) for every C26 run; card `splits-dev-start-date-unify` makes splits.py say so.
3. Fee per round trip: 0.10 % (`fees.py` BINANCE_TAKER x 2, used by C26/C30), 0.12 % (`trade_costs.py` with slippage), 0.14 % (`research_kit.TAKER_RT_PCT`,
   WaveTrend verdicts). Resolution: book scoring charges fees.py per leg AND prints the 0.14 % line as the stress figure; a pass must hold at 0.14 %.
   Card `fee-figure-unify` picks one number for the repo.
4. Venue: Phase 1 and the range measure use Binance SPOT 15m / 1m; DEV data, CVD and OI are USDT-M PERP. Resolution: Phase 3 runs on perp 1m
   (the DEV files), rebuilds the 15m events from it, and reports the event-count difference against the spot run as its first line.
5. "RSI divergence" has six definitions in the repo (Malkan 3-10 bars; C30 8 vs 9-40 bars with RSI >= 60; C26 Phase 1 pivot within 72h; leg B day
   high; Krown hidden; ladder K=3/LB=60). Resolution: each result is cited with its definition's name; none transfers; the direction of the evidence
   (divergence-timed shorts have no edge) is the same under all six, which is why the ladder leg is treated as a clock, not a filter.
6. "No stop inside the range" (operator) vs unbounded loss (hard rule: fail closed). Resolution, already on the card: the range top is the ladder's one
   stop; the measured 30-45 % break rate at X = 0.65-1.0 % means the leg count and size step are frozen BEFORE DEV and the worst book loss is a
   scored number, not a surprise.
7. Earlier chat claim "OI from 5m metrics and CVD from klines are available in DEV": confirmed (binance_metrics 2022-01..2025-12 daily files; perp 1m
   klines 2022-01..2025-08 with taker_buy_volume), perp venue only. Not a contradiction; the venue note above applies.
8. Phase 1 "overshoot 4h after" (0.65 % 80th) vs the full-window excursion to the exit (0.64 %): consistent; the 4h cap did not hide a wider range.
9. The C24 OI card shows the pre-fix pairing numbers (18/9/22); OI_PAIRING_RECHECK.md has 58/45/38. Verdict unchanged (no direction); the card is stale.
   Noticed, not fixed here (Eagle_Eyes folder).

## 3. Where the edge can be (hypothesis, OURS, to be frozen in Phase 2)
- Not the trigger: divergence on any timeframe is a clock that fires every few minutes (median 8-16 signals per window) and has no edge anywhere in the repo.
- Not the structure: a martingale creates no expectancy; it trades a higher win rate for a fatter tail, and the tail here is the 30-45 % range break.
- The candidate is the STATE: a held high taken in a DOWN regime, which reversed 60 % of the time with -0.94 % median in 24h, while the same event in an
  UP regime kept going. The pooled arms lost because UP and DOWN cancel and the stop sat 0.05 % past the wick. If the regime-conditioned single short
  (Candidate A: enter on the 15m close back under H1, stop at H1 + X, exit at L1 / 24h) has no gross edge above 0.14 % on DEV down-regimes, nothing
  built on it (ladder C, hedge B) can; if it has, C and B are book variants scored against it, not instead of it.
- Frozen before the DEV run (Phase 2, operator confirms on >= 3 of his charts, PRE_REG_TEMPLATE 0g): the regime rule (proposal: prior UTC daily
  close below its 50-day SMA = DOWN), X (proposal 1.0 %, from Q1b), legs (proposal 3, at fixed price steps inside the range, not per divergence), size
  step (proposal 1-1-2 and 1-2-4, both scored), exits (L1 touch / 15m close back above H1 + X = stop / 24h), fees per leg.

## 4. Next steps, moved into the pipelines
| card | lane | what done looks like |
|---|---|---|
| c26-phase2-freeze-regime-ladder | JIS-NB (Lab_Guy with the operator) | PRE_REG_C26_REGIME.md committed before any DEV P&L: regime rule, A/B/C legs, X, sizes, exits, pass rule; 3 operator charts encoded |
| c26-phase3-dev-book | SONNET Builder | perp 1m DEV 2022-04..2024-06 + one look 2024-07..2026-06: A vs C vs B per regime, net of fees.py per leg and at 0.14 %, worst book loss, power gate, one-bar shift, Holm over the pre-registered cells; three simulator cards |
| rumers-testable-rules-dev-backtest (exists) | SONNET | blocked until RUMERS_EXTRACT_1/2 land (Codex allowance out; YouTube 429 on this IP until about 12:14Z); then the HARNESS.md pre-reg per rule |
| splits-dev-start-date-unify | HAIKU | splits.py states the desk lock 2022-04-01 or carries both with a name; tests updated |
| fee-figure-unify | SONNET | one round-trip cost figure (or a named pair) used by fees.py, trade_costs.py and research_kit; docs point to it |
