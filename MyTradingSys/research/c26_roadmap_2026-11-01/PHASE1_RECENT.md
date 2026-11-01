# C26 roadmap, Phase 1: what the recent phases did (Lab_Guy, 2026-11-01)

Operator order 2026-11-01: understand the recent phases FIRST, then decide how to backtest (card `c26-scenario-roadmap-sequence`).
Descriptive only: no P&L, no trade rule, no advice. This window is now SEEN (the design set) and never counts as a test.
Script `phase1_recent.py` (C26 15m definitions, all OURS); full output and every event row: `PHASE1_EVENTS.md`
(bars to 2026-11-01 07:45Z, Binance spot 15m; OI = Binance USDT-M 5m metrics; OI missing only on 11-01).

Phases: UP = 2026-07-01 (57.8k low) .. 2026-09-21 20:15Z (top 87,396); DOWN = 09-21 .. now (78.0k).
Roadmap (high side, low side mirrored): H1 pivot -> L1 pull-back low -> retest within 0.4 % that holds -> L1 swept? -> H1 taken -> back to L1?

## 1. Step odds by phase
| group | held retests | taken <=24h | taken <=72h | L1 swept first | ...then H1 taken | take-out closed back <=1h | back to L1 <=24h after take-out | OI up L1->retest | take-out in US |
|---|---|---|---|---|---|---|---|---|---|
| UP highs | 73 | 54/73 (74%) | 63/73 (86%) | 27/73 (37%) | 17/27 (63%) | 35/63 (56%) | 24/63 (38%) | 36/73 (49%) | 16/63 (25%) |
| UP lows | 73 | 54/73 (74%) | 60/73 (82%) | 26/73 (36%) | 15/26 (58%) | 43/60 (72%) | 25/60 (42%) | 31/73 (42%) | 20/60 (33%) |
| DOWN highs | 39 | 26/38 (68%) | 30/38 (79%) | 16/38 (42%) | 8/16 (50%) | 23/30 (77%) | 18/30 (60%) | 16/38 (42%) | 5/30 (17%) |
| DOWN lows | 42 | 31/41 (76%) | 34/41 (83%) | 20/41 (49%) | 13/20 (65%) | 20/34 (59%) | 11/34 (32%) | 20/41 (49%) | 11/34 (32%) |

Move after the take-out (median; + = kept going through the level, - = reversed) and how far it overshot the level:
| group | 24h after take-out | overshoot in the 4h after, median / 80th pct |
|---|---|---|
| UP highs | +0.13 % | 0.57 % / 1.06 % |
| UP lows | -0.37 % | 0.70 % / 1.41 % |
| DOWN highs | -0.94 % | 0.37 % / 0.65 % |
| DOWN lows | +0.15 % | 0.85 % / 1.67 % |

## 2. Context splits (highs and lows pooled, mirrored; closed events; small n = description, not evidence)
| phase | factor | yes: n, taken <=24h, back to L1 | no: n, taken <=24h, back to L1 |
|---|---|---|---|
| UP | OI up L1->retest | n=67, 76%, 19/59 | n=79, 72%, 30/64 |
| UP | RSI divergence at H1 | n=83, 77%, 26/70 | n=39, 64%, 13/32 |
| UP | WaveTrend OB at H1 (wt1 >= 53) | n=42, 57%, 12/32 | n=104, 81%, 37/91 |
| UP | H1 at a 72h HVN | n=60, 78%, 24/52 | n=86, 71%, 25/71 |
| UP | L1 swept before take-out | n=53, 38%, 11/32 | n=93, 95%, 38/91 |
| UP | retest held in US/LATE | n=68, 78%, 28/59 | n=78, 71%, 21/64 |
| DOWN | OI up L1->retest | n=36, 61%, 14/27 | n=43, 81%, 15/37 |
| DOWN | RSI divergence at H1 | n=37, 65%, 13/26 | n=27, 70%, 10/23 |
| DOWN | WaveTrend OB at H1 (wt1 >= 53) | n=21, 67%, 7/16 | n=58, 74%, 22/48 |
| DOWN | H1 at a 72h HVN | n=23, 83%, 8/20 | n=56, 68%, 21/44 |
| DOWN | L1 swept before take-out | n=36, 42%, 12/21 | n=43, 98%, 17/43 |
| DOWN | retest held in US/LATE | n=31, 68%, 13/25 | n=48, 75%, 16/39 |

## 3. Reading
1. The magnet did not change with the phase: 68-76 % of held levels were taken within 24h in both UP and DOWN, the same as
   the 4-year C26 rate (72 %). "The held high gets taken" is not where the context matters.
2. The context decides what happens AFTER the take-out. A take-out against the trend reverses: in DOWN, a taken high closed
   back under within 1h 77 % of the time, fell back to L1 within 24h 60 %, median -0.94 % 24h later; in UP the same step was
   56 %, 38 %, +0.13 % (it kept going). Lows mirror it: taken lows in UP bounced (-0.37 %), in DOWN they kept going (+0.15 %).
   The operator's "H1 taken, then price falls" is the DOWN-phase version of the roadmap.
3. The full five-step chain is the minority path: L1 swept first AND then H1 taken = 17/73 UP highs, 8/38 DOWN highs (about
   1 in 5). The common path is H1 taken straight away. Once L1 is swept first, H1 within 24h drops to about 40 % (vs 95-98 %
   when L1 holds): the L1 sweep is the fork in the road, not a step on it. (Part of this is timing: a fast take-out leaves no
   time for a sweep.)
4. "Shorts build" is not visible in OI: OI rose from L1 to the retest in only 42-49 % of cases, and in DOWN the retests with
   rising OI were taken LESS often (61 % vs 81 %). Rising OI is not the fuel signal in this sample.
5. Confluence at H1: RSI divergence did not make H1 hold (UP: taken MORE, 77 % vs 64 %). WaveTrend overbought at H1 is the
   one factor that leans toward "H1 holds" (UP 57 % vs 81 % taken; DOWN 67 % vs 74 %). H1 at a high-volume node was taken
   more often (78/71 %, 83/68 %). US session: take-outs were not concentrated there (17-33 % vs 27 % of the hours).
6. Stops: a take-out overshoots the level by 0.4-0.9 % (median) and 0.65-1.7 % (80th pct). A stop or hedge trigger just past
   H1 is hit in most take-outs; in DOWN highs the overshoot was smallest (0.37 % / 0.65 %).
7. Encoding check (PRE_REG_TEMPLATE 0g, 1 of the 3 needed): the operator's 10-31 chart (10-28 highs held, taken 10-29,
   then the drop) is row `H 10-28 08:30 81,823`: held 10-28 20:45, taken 10-29 in the US session after 19h, closed back
   within 1h, -5.1 % 24h later, back to L1.

## 4. What this means for Phase 2 (design notes, OURS, nothing frozen yet)
- Primary split = trend regime, fixed by a rule written before the history run (e.g. daily close vs a long MA), not by eye.
- Candidate A (core): in a DOWN regime, after a held high is taken and a 15m close comes back under it, short toward L1;
  stop beyond the 80th-pct overshoot. This is C26 arm B restricted to the regime that the recent phase points to; arm B
  failed pooled, so the regime restriction is the whole hypothesis and must win on 2022-24 down regimes on its own.
- Candidate B (hedge book): core short at a held high in a DOWN regime + a temporary long hedge for the take-out squeeze,
  closed on the close back under H1; scored on the book (net after fees.py fees, worst drawdown, core stop-outs avoided).
- Filters worth one pre-registered test each: WaveTrend OB at H1 (holds more). Dropped as triggers: OI-up as "shorts build",
  RSI divergence at H1, US-session timing.
- The L1 sweep is a branch: a separate state ("L1 swept, H1 magnet weak") rather than a step to wait for.

## 5. Where it stands now (descriptive, bars to 07:45Z)
Two open held levels: high 78,110 (pivot 10-30 15:15, retest held 11-01 03:00 ASIA) and low 77,114 (pivot 10-31 04:30,
retest held 10-31 16:00 US); price 78,008 sits between them. Regime by this split: DOWN.

## 6. Limits
- 4 months, 227 events; splits have n 16-104, so differences under about 15 points are noise. No p-values on purpose: these
  are design looks, logged as count-only rows in `TRIAL_REGISTRY_c26_roadmap.csv` (12 looks) so Phase 3 counts them.
- Phase split at one top is OURS; spot 15m bars; OI is exchange-wide Binance USDT-M only.
