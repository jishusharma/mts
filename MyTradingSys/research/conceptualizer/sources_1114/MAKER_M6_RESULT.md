# RESULT_M6: Europe-low sweep reclaim in the US session, maker entry at the swept low (PRE_REG maker-entry-1114)

**VERDICT: FAIL. Gates 2, 3, 6 failed (mean net R filled -0.346; CI upper bound below 0; ex-best-5-days -0.542). Gate 1 (n 399) and gate 4 (placebo p 0.028) passed; gate 5 is only provisional (BH over this one row, m=1; the lead must redo it over the 6 rows). Not THIN (fill 38.8%).**

Regime mix: VALIDATION signals up 39.3 % / down 33.0 % / range 27.7 % (404 / 339 / 285; BTC prior-day close vs SMA20 +-2 %, the original's rule, descriptive only; no phase gate, the original row is a session gate). Filled: up 155 / down 133 / range 111.

Source: edge-session-sweep-reclaim-1113 (worktree <local-path> `eur_low_sweep_reclaim_pooled_2026-11-13`). "Best maker cell" = LONG, exit HIGH (EH), original VAL n 173, +0.105 [-0.298, +0.577], at 2 bp maker / 5 bp taker fees on Bybit perp 5m.

## What was done
- Signal exactly as the original (weekdays, Europe 07:00-13:30Z EL/EH, first US-window 5m bar with low < EL, first 5m close > EL within 12 bars, stop S = lowest low sweep..reclaim, min risk 0.15 %, target EH, time stop 20:00Z). Evaluated on 5m bars aggregated from Binance spot 1m (BTC from 2020-03, ETH 2021-03, SOL 2021-10, the original's listing starts). Original used Bybit perp 5m: source differs.
- Maker mapping (OURS, the only new part): buy limit at L = EL placed at the reclaim-bar close; PRE_REG fill model (through by 1 tick, life 5 x 1m = one 5m entry bar, stop S, target EH tick-through, time exit 20:00Z, fees 3/3/6 bp). Parameters frozen, nothing tuned.
- Signal universe = original taker signals (those with a valid original next-open trade): DEV 932, VAL 1028 (VAL here is 2024-01-01 on, per PRE_REG; the original VAL was 2024-07..2025-06).
- Placebo: 1000 draws at n 399; each draw samples a real VAL signal's (passive offset in ATR14 of 5m, stop % of L, target R, symbol), a random same-symbol weekday US-window 5m bar in VAL with close > that day's EL, L = close - offset x ATR, same simulate_maker. 128,012 candidate bars.

## Taker baseline replication (original machinery, next-open entry; gross R and net at the original 10 bp)
| window | mine n / net 10bp | original RESULT n / net 10bp | gap |
|---|---|---|---|
| DEV 2020-03..2024-06 | 1102 / -0.383 | 1130 / -0.360 | -0.023 R |
| VAL 2024-07..2025-06 | 372 / -0.289 | 384 / -0.230 | -0.059 R |
| RECENT 2025-07.. | 486 / -0.323 | 511 / -0.294 | -0.029 R |
Same sign, n within 3 %, net within 0.02-0.06 R: a reasonable but not exact replication (Binance spot vs Bybit perp prices; weekend-edge and gap differences). The original MAKER cell (+0.105, 2 bp entry fee, entry fill only after trade-through, 60-min life, fill-bar exits not scanned) is a different model; the original taker numbers are the replication target here.

## VALIDATION (2024-01-01 on), maker model, PRE_REG fill rules
| item | value |
|---|---|
| signals / filled / fill rate | 1028 / 399 / 38.8 % (misses: 307 never traded through L in 5 min, 322 min-risk at L) |
| gross R filled (maker model) | -0.078 |
| fee R filled | 0.267 |
| **net R per filled trade, maker** | **-0.346**, CI per trade [-0.561, -0.099], per UTC-day [-0.585, -0.088] |
| net R per signal (miss = 0) | -0.134 |
| taker baseline, 12 bp, all signals | -0.387 (gross -0.078) |
| taker baseline on the filled subset | gross -0.276, net12 -0.551 |
| adverse selection (original gross over filled minus over all) | -0.198 R (filled subset is the WORSE one for the original model) |
| exits (filled) | stop 299, target 45, time 55; hit rate 21.3 % |
| ex-best-5-UTC-days mean net R | -0.542 |
| placebo | observed -0.346 vs draw mean -0.734 (p95 -0.402), p = 0.028 |

DEV (reference only): 932 / 354 filled (38.0 %), net R filled -0.413 [-0.577, -0.238], gross -0.183, per signal -0.157, taker12 all -0.412, adverse selection -0.191.

## Gates (VALIDATION)
| gate | result |
|---|---|
| 1 filled n >= 100 | PASS (399) |
| 2 mean net R > 0 | FAIL (-0.346) |
| 3 CI lower > 0 (trade and day) | FAIL (-0.561 / -0.585) |
| 4 placebo p < 0.05 | PASS (0.028), but placebo is a tight-stop loser (-0.73 R), beating it is not an edge |
| 5 BH q 0.05 over 6 rows | provisional PASS with m=1, lead to recompute (moot: row already fails 2, 3, 6) |
| 6 ex best 5 days > 0 | FAIL (-0.542) |

## Descriptive extras (not gates, nothing selected on them)
- Order life 60 min (the original's maker life), sensitivity only: VAL fill 57.7 %, net R filled -0.325 [-0.511, -0.125], per signal -0.188, gross -0.051. Still a FAIL; more fills, same negative sign.
- Per symbol VAL net R filled: BTC 108 fills -0.402, ETH 137 -0.251, SOL 154 -0.391.
- Per regime VAL net R filled: up 155 -0.427, range 111 -0.699, down 133 +0.044 (one regime, post-hoc split, CI not computed; a lead at best, not a PASS).
- Fee burden per signal is 0.309 R at 12 bp taker (gross -0.078 to net -0.387) versus 0.267 R per filled maker trade, a small saving; 75 % of fills exit at the stop (299 of 399) and maker gross R (-0.078) is no better than the taker's.

## Honest caveats
- Data source differs from the original (Binance spot 1m vs Bybit perp 5m); the replication gap is 0.02-0.06 R.
- 322 of 1028 VAL signals count as misses because the risk at L = EL (L - S) is under 0.15 % of L, although the original trade (entry at the later open) passed the rule; that follows the frozen min-risk rule at the actual entry price.
- Fill-bar-target is credited (lib default fill_bar_target=True per the PRE_REG "from the fill bar"); stop wins ties.
- Gate 5 needs the other five rows' placebo p. The look-ahead truncation test and the independent checker have not been run on M6.
- Tick: BTC/ETH 0.01, SOL 0.0001 (smallest increment over full history, per PRE_REG).

Files: study.py (run: `python study.py`), test_study.py (10 tests, pass; each wrong variant, fill on touch, reading the signal bar, fill better than L, 60-min life, is asserted to differ), results.json (aggregates + per-signal rows).
