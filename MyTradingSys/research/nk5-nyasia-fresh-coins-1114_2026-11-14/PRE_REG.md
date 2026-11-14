# PRE_REG nk5-nyasia-fresh-coins-1114 (written and committed before any run on the fresh coins)

Question: does the one near-miss row of nk5-session-open-15-10-5-1114 ("NY-asia", phase-matched, hold to 08:00 UTC; 12 bp mean net R +0.074, n 1663 VAL, but day-cluster CI low -0.151, ex-best-5 -0.108) survive on coins it never saw?
Rule: NY-asia ALONE. Exactly the source rule and parameters (study.py here is the source study.py with every other row removed; no new parameter, no new exit). Source study read from branch JIS-NB/nk5-session-open-15-10-5-1114.

## Context
Phase for UTC day D uses data to the close of D-1 only (daily bars from 5m): slope = SMA20(close)[D-1] - SMA20(close)[D-6]; ADX(14) Wilder with +DI/-DI. UP: ADX>=20, +DI>-DI, slope>0. DOWN: ADX>=20, -DI>+DI, slope<0. Else RANGE. (ADX 20 = operator order; 5-day slope window OURS, unchanged from source.)
Matched direction: UP long only; DOWN short only; RANGE fade both ways. Mismatched direction not traded here (control rows are not part of this test).
Regime mix: reported in RESULT.md (share of coin-days UP/DOWN/RANGE over the fresh universe, trades by phase, long/short split). The source VAL mix was RANGE 39.9 / DOWN 35.6 / UP 24.6.

## Signal and trade (unchanged from source)
At anchor T = NY cash close 16:00 America/New_York (20:00 or 21:00 UTC), bars closed at or before T only; entry at the 5m open at T.
- 15m RSI(14) Wilder: long touch = min of last 4 closed 15m values <= 35; short touch = max >= 65 (35/65 and 4-bar window OURS).
- HM (OURS reconstruction): RSI(9); green = EMA(3), red = WMA(21); buy = red<green (SOURCED), sell = red>green. Long = long touch AND 10m HM buy AND 5m HM buy. Short mirror.
- One exit: time exit at the 5m open of 08:00 UTC the next day. Stop S = max(0.5% of entry, 0.6 x ATR14 of last closed 1h bar), R = S, checked on 5m highs/lows, filled at stop price (no gap slippage; limitation). No target.
- Net R = (signed return - fee)/(S/entry). Fee 12 bp round-trip taker PRIMARY; 6 bp row also reported (not gated). One trade per coin per day per direction.

## Universe and data
Fresh Binance spot USDT coins, none in the source 20 (BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX EOS XLM ETC DASH ZEC BCH ATOM NEO IOTA VET): AVAX DOT UNI AAVE FIL NEAR ALGO XTZ SAND MANA THETA GRT HBAR ENJ (14, liquid, listed by 2021). Full history from first listed bar, 5m klines via data-api.binance.vision into F:\MTS\data_cache\binance_fresh\nk5_nyasia\. Whole history is out of sample for the rule (the rule was only ever evaluated on the source 20). A coin with a data fetch failure is dropped and named in RESULT.md, never replaced after seeing outcomes. Descriptive splits (pre-2024 / 2024+) are reported, not gated.
Forward rows: BTC and ETH, NY-asia anchors on UTC days from 2026-11-13 whose 08:00 UTC exit has passed (source data ended 2026-11-13 21:00 UTC). Reported as descriptive rows, not gated (n tiny).

## Gates (fresh coins, full history, 12 bp, matched rule; PASS needs all)
1. n >= 100 trades.
2. Mean net R > 0 at 12 bp.
3. Day-cluster bootstrap 95% CI lower bound > 0 (2000 resamples, seed 1).
4. Mean net R > 0 after removing the best 5 trading days (by summed R).
5. Placebo: p < 0.05 vs 2000 draws of random same-size entry sets from the same coin-days pool, same-phase and same-direction stratified, same stop, same exit, same fee.
Also reported (not gated): trade-level bootstrap CI, 6 bp row, per-coin means, DEV/2024+ splits.
Verdict: PASS only if all five hold; otherwise FAIL listing failed gates. No parameter changes after seeing results.

## Tests
test_study.py: causality test (truncating data after T leaves signal and phase unchanged) passes on the real code and fails under STUDY_BUG=1 (look-ahead: signal read from the bar closing at T+15m and phase from the same-day close). Plus a structural test that the only row is NY-asia anchored at the NY close.
