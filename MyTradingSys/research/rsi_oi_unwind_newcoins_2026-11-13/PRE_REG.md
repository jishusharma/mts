# PRE-REG: out-of-sample check of two RSI-extreme layer cells on 40 new coins (edge5-rsi-oi-unwind-newcoins-1113)

Written and committed before any outcome (stop/target/return) is computed. Parent: research/rsi_confirm_layers_2026-11-13 (20 coins, no slippage). Only the 40-coin universe (a ranking by current turnover and listing age, not an outcome) was fetched first.

## Hypothesis
Two layer cells looked better than the unfiltered rule on the parent's VALIDATION but failed its pass rule and were negative on DEV: (1) 1h signal with 24 h open-interest change <= -3 % (+2R), (2) 4h signal with daily ADX 20-25 (+2R). If either is real it must show up on coins the parent never touched, with costs that now include slippage.

## Context
Regime/phase: counter-trend dip buy after an RSI(14) <= 20 flush; the layer asks whether a flush where open interest fell (positions closed, forced unwind) is a bounce rather than a continuation (cells A, C), and whether a flush inside a young, mid-strength daily trend (ADX 20-25) bounces (cell B). Session: A and B all 24 h; C only signal bar opening 13:00-20:59 UTC (US session, signal bar open hour 13..20; OURS). Entry: close of the confirming bar (SOURCED, operator rule).
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %), as measured in the parent: 2020-2023 bull 51 % / bear 40 % / range 10 %; 2024-now bull 56 % / bear 30 % / range 15 %. The new coins mostly list 2021-2025, so their sample sits mostly in the 2023-2026 regime; per-coin history start is reported.

## Rule (unchanged from the parent; SOURCED = operator words, OURS = our choice)
- Signal bar s on TF in {1h, 4h} (4h folded from 1h, UTC-anchored): Wilder RSI(14) of TF closes <= 20 (OURS, parent), first touch per episode, re-arm after RSI > 30 (OURS).
- Confirm (SOURCED): bar s+1 green and closes above close of s. Entry = close of s+1. Stop = low of s (SOURCED). Long only.
- Exit (OURS, parent): target +2R, R = entry - stop; 72 h cap exit at close; stop fill = min(stop, bar open); same-bar stop+target = stop (stop first). Forward walk on 1h bars after the entry bar. Last 7 days without full forward window excluded; still-forming bar dropped.
- Cost (SOURCED from fees.py): 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 per round trip, as a fraction of entry price, divided by stop distance to get R. Funding not charged (<= 72 h holds; limitation).

## Universe (fixed now)
Bybit v5 USDT linear perpetuals not among the parent's 20 (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM NEAR UNI TRX BCH ETC FIL APT ARB). Rule: rank by current 24 h turnover, drop non-crypto instruments (equity, ETF, commodity, gold tokens PAXG/XAUT), stablecoins and wrapped tokens, require listing age >= 1 year, take the first 40:
ZEC AKE HYPE BARD 1000PEPE ENA INIT SUI ARIA AAVE JCT WLD XMR INJ PUMPFUN XLM ONDO SOPH TAO TRUMP ZRO H FARTCOIN BMT TIA USELESS HBAR PIEVERSE ICP QNT AERO STRK VVV OP KGEN WLFI XPL JUP Q ERA
(Survivorship: current-turnover ranking favours coins that did well; stated limitation.) 1h + 1D klines and 1h open interest fetched from listing; OI coverage per coin reported.

## Cells (exactly three; each is a subset of the unfiltered base of its own TF, +2R)
- A: 1h signal AND 24 h OI change <= -3 % (OI at or before signal bar close / OI 24 h earlier - 1; trades without OI excluded, n reported).
- B: 4h signal AND daily ADX(14) (Wilder, last closed daily bar at signal close) in [20, 25).
- C: A AND signal bar opens in 13..20 UTC.

## Pass rule (all must hold per cell; the whole new-coin set is the test set, no DEV/VALIDATION fitting)
1. Fee-net mean R > 0.
2. 95 % bootstrap CI lower bound > 0 on both the per-trade view (iid resample) and the day-cluster view (resample UTC signal dates across coins, 5000 draws, seed fixed).
3. n >= 100 (B: n >= 60) and >= 40 distinct signal days.
4. Cell mean > unfiltered base mean (same TF, same coins).
5. Random-subset placebo: 2000 draws (>= 500) of the same size from the unfiltered base trades of that TF; p = share of draws with mean >= cell mean; need p <= 0.05/3.
6. Bonferroni over 3 cells: the day-cluster one-sided bootstrap p (share of resampled means <= 0) must also be <= 0.05/3.
Below the n or days floor = UNDERPOWERED (never PASS). Also reported: 2024-onward and per-year means; share of total R from the best 5 signal days and the mean without those days (descriptive; a cell whose mean without best 5 days is <= 0 is flagged FRAGILE in the verdict but the pass rule above decides).

## Limits stated now
Trades overlap across correlated coins (day-cluster view handles part); funding and borrow not charged; slippage is a flat 2 bp round trip, small coins likely worse; survivorship of the universe; OI history starts at each coin's own history and may be shorter than klines.
