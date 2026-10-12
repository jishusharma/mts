# Pre-registration Q33 (written 2026-10-12 BEFORE the first run; runner `matrix_q33.py`)

Spec: `FAST_MOVE_CATALOGUE.md`. Template slots (PRE_REG_TEMPLATE.md) answered for a pure context/trigger event study.

1. Source home: BTCUSDT perp, 15m evaluation grid, all sessions, 15m to 4h holds. Sources are S1..S14 in SOURCED_RULES.md; BB, RSI, squeeze are NO-SOURCE (labelled).
2. Ground truth ledger: not applicable (no trader trade reproduced). Event study only; "recall/fire rate" is replaced by per-cell n.
3. Recall: n/a. Fire rate: reported as events per cell.
4. Data: Binance archive 1m klines 2022-01-01..2026-10-11, 2,512,800 bars, 0 gaps; `taker_buy_volume` gives delta = 2*taker_buy - volume. NOT_IN_DATA on this machine: OI, long/short ratio, funding (F4, F5, F6 not run); book depth; big-trade size.
5. Parity: n/a (VP levels are my own prior-day 1m-close profiles, not Tom's drawn levels).
6. Cost: FEES_ALL_TAKER (backtest/fees.py), entry + exit both taker, no maker credit, no slippage, so a lower bound on cost realism is NOT claimed; fee share of R not computed (no stop).
7. Fills: market entry at the OPEN of the bar after the event bar; exit at the close H bars later. No stop, no target (pure forward return).
8. Exits: fixed horizon only. This is not Tom/Fabio management (both say management is the edge); a negative result here is NOT a verdict on their trades.
9. Null: placebo = same number of random bars, same side, same H, drawn from all bars (1000 draws); one-sided p = share of placebo mean >= observed mean.
10. Power: cells with n < 300 are listed as underpowered, never as "no edge".
11. Holdout: none held out (event study, grid fixed here). Instead each cell reports first-half (2022-2024) and second-half (2025-2026) means; a survivor needs the same sign in both.
12. Trial count: cells with n >= 300 across all triggers x filter states, primary horizon only for FDR.

## Frozen choices (grid collapsed to ONE value each, no tuning after the run)
- Evaluation bars: 15m (resampled from 1m). Decision at close of bar t, entry open t+1. Horizons H = 1, 4, 16 bars (15m, 60m, 240m). PRIMARY for FDR: H = 4.
- Cooldown: 4 bars per (trigger variant, move direction).
- T1: BB(20,2) on 15m close, population sd. T2/T2b: prior-UTC-day profile from 1m closes, bin = ATR(14,1h)/10, 3-bin smoothing, HVN = local max >= median of non-empty bins, LVN run <= 0.5 x median between two HVNs; traverse = band crossed within <= 2 bars of 15m closes; reject = bar wicks >= 1 bin into the band and closes back on the approach side.
- T3/T3b: 15m 3-bar FVG, unfilled <= 96 bars; first test = first bar whose range enters the zone; second test = next entry after leaving the zone, zone not closed through.
- T4: break of the 16-bar (240 min) prior high/low with close beyond, next prior-day HVN in the move direction >= 1.0 x ATR(14,15m) away, and CVD state agrees. Fade variant T4b and T5/T6 (frozen Tom/Fabio events) NOT RUN here (event files not available in this run); agreement is therefore not reported.
- F1: majority of 3 signs: close vs UTC-day VWAP; sign(POC[w-1] - POC[w-2]) of COMPLETED weekly volume profiles (log bins 0.1%); EMA20(4h) slope over 6 4h bars. F2: RSI(14) Wilder 15m, <40 / 40-60 / >60 (labelled Malkan, NO-SOURCE for Tom/Fabio; Malkan quote not verified). F3: sum(delta)/sum(volume) over 2 bars, z vs trailing 30d, +-1. F7: pctrank of BB width over 672 bars <= 20 squeeze, >= 80 expanded. F8: relative volume vs same time-of-day median of prior 20 days >= 1.5 AND CVD sign = move direction.
- Side is per cell; longs and shorts are never pooled. Filters: baseline, F1(3), F3(3), F1xF3(9), F2(3), F7(3), F8(3) one at a time, max 2 deep.
- Verdict rule: SURVIVOR = n >= 300, BH-FDR q <= 0.05 on placebo p (primary H), mean net > 0, same sign in both halves. Otherwise "nothing survives".
