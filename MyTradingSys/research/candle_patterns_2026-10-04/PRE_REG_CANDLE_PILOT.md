# PRE-REGISTRATION: BTC candle pilot P0 + P1 (frozen before any result)

Session MTS-2026-10-03-2051Z-APP-ANA-btc-candle-patterns. Written 2026-10-04, before `run_p0.py` / `run_p1.py` were ever run.
The commit that adds this file precedes the commit that adds any result file; `git log` is the proof.
Status of everything below: EXPLORATORY TRIAGE. Nothing here adopts a rule (BACKTEST_PROTOCOL.md section 6 is not met by a pilot).

## 1. Data and split (fixed, never adjusted after seeing results)
Venue/symbol: Binance USDT-M BTCUSDT perpetual, archive data (data.binance.vision), UTC bars.
- Daily: `Dumps/backtest/raw_1d/klines` 2020-01-01 .. 2026-09-26. 1h: resampled from 1m (`raw_1m_2022` + `raw/klines`) 2022-01-01 onward.
- DEV: daily 2020-01-01 .. 2024-06-30; hourly 2022-01-01 .. 2024-06-30. The pilot reads DEV only.
- VALIDATION: 2024-07-01 .. 2025-06-30. Run once per frozen candidate set, in a later session.
- HOLDOUT: 2025-07-01 .. 2026-09-26. Sealed. The pilot code refuses to read dates after DEV_END (asserted in `cdata.py`).
- Funding: archive `fundingRate` (8h, settlements 00/08/16 UTC), charged on realised settlements inside the holding window.

## 2. Cost model (all pilot results are NET unless labelled gross)
Taker 5 bps per side (`backtest/fees.py` BINANCE_TAKER), plus slippage 2 bps per side on market fills (stress: 0 and 5). Round trip base case = 14 bps.
Funding: long pays, short receives the realised 8h rate. Closing-basis exits that cannot be known until the bar closes are filled at that close (variant A) or at the next open (variant B).

## 3. P0 - the operator rule (verbatim in the session prompt, 2026-10-03)
"long the previous candle's daily open when price goes up past it, and exit when current daily breaks previous day close on a closing basis."
Reading R (frozen): level L = open of the previous daily bar (D-1). Flat on day D: if open(D) >= L enter at open(D); else if high(D) >= L enter at L (stop-buy).
Exit: first day E >= entry day with close(E) < close(E-1). No other stop (the operator gave none). Same-day entry and exit is allowed. Re-entry from the next day.
Variants (4 trials): P0a long, exit fill at close(E); P0b long, exit fill at open(E+1); P0s short mirror of P0a (short when price falls through L, exit when close(E) > close(E-1));
P0anchor (informational, 1m-based, DEV 2022-01..2024-06): P0a with the day boundary shifted by 0,4,8,12,16,20 hours (6 anchors, counted as 6 trials).
Benchmarks (always reported): buy-and-hold over the same window; exposure-matched random-entry null (same number of trades, same holding-day multiset, non-overlapping random starts,
entry open(day) to close(last day), 2000 permutations, seed 12345); "always flat" = 0.
Reported per variant: n trades, win rate with Wilson 95 percent CI, mean net log return per trade with bootstrap 95 percent CI (10000 resamples), median hold, time in market,
daily-resolution Sharpe (365-day), max drawdown, compounded return vs buy-and-hold, random-null p-value, funding share of cost.

### Addendum A (2026-10-04, still before any run; supersedes the variant list above)
BTC trades 24/7, so open(E+1) equals close(E) to within a tick; P0b would repeat P0a and carries no information. Replaced. Final P0 variants (10 trials):
- P0a long, intraday touch entry (reading R), exit fill at close(E).
- P0c long, close-confirmed entry: enter at close(D) when close(D) > open(D-1) and flat; exit rule evaluated from D+1.
- P0s short mirror of P0a.
- P0e entry ablation: enter at open(D) whenever flat (no level condition), same exit rule. Tests whether the level carries anything beyond the exit rule plus market drift.
- P0anchor x6: P0a on 1m-built "days" starting at 00,04,08,12,16,20 UTC (DEV 2022-01..2024-06).
Daily-bar conventions: a stop-buy entry time is unknown inside the day, so funding for it assumes entry at open+12h; an entry at the open uses open; an exit at close(E) is at t_E+24h-1ms.
Cost per round trip = 2*(5 bps fee + 2 bps slip) = 14 bps, plus realised funding. Per-trade net = sign*ln(exit/entry) - 14 bps - sign*funding.
Null statistic is GROSS mean log return per trade (costs are identical on both sides): real trade = ln(exit/entry); null block = ln(close(last day)/open(first day)), sign-adjusted.

## 4. P1 - classical pattern scan (definitions are fixed here; thresholds are not tuned)
Notation per bar: body=|c-o|, rng=h-l, up=h-max(o,c), lo=min(o,c)-l, green=c>o, red=c<o. Bars with rng=0 never signal. Signal known at close of bar i; entry open(i+1); exit open(i+1+h).
Trend context where required: down = close(i-1) < close(i-4); up = close(i-1) > close(i-4).
Directional patterns, expected sign in brackets (the textbook claim, tested one-sided):
1 bull_engulf(+): red[i-1], green[i], o[i]<=c[i-1], c[i]>=o[i-1], body[i]>body[i-1].   2 bear_engulf(-): mirror.
3 bull_harami(+): red[i-1], green[i], o[i]>c[i-1], c[i]<o[i-1].                       4 bear_harami(-): mirror.
5 hammer(+): lo>=2*body, up<=0.1*rng, body>0, down.   6 hanging_man(-): same shape, up.
7 inv_hammer(+): up>=2*body, lo<=0.1*rng, body>0, down.   8 shooting_star(-): same shape, up.
9 morning_star(+): red[i-2], body[i-1]<=0.3*body[i-2], green[i], c[i]>(o[i-2]+c[i-2])/2.   10 evening_star(-): mirror.
11 three_white_soldiers(+): green at i-2,i-1,i; closes rising; each open inside the previous body.   12 three_black_crows(-): mirror.
13 piercing(+): red[i-1], green[i], o[i]<=c[i-1], (o[i-1]+c[i-1])/2 < c[i] < o[i-1].   14 dark_cloud(-): mirror.
15 hikkake_bull(+): mother m, inside bar m+1 (h<h_m and l>l_m), bar m+2 with h<h[m+1] and l<l[m+1], and a close above h[m+1] first occurring at i in m+3..m+5. 16 hikkake_bear(-): mirror.
17 marubozu_up(+ continuation): green, body>=0.9*rng, rng>=1.5*mean(rng of the prior 14 bars).   18 marubozu_dn(-): mirror.
(Gap-based patterns such as kicker and abandoned baby are excluded: BTC trades 24/7 and has no gaps.)
Horizons h in {1,3,5} bars. 18 patterns x 3 horizons = 54 tests per timeframe, two timeframes (1d, 1h) = 108 trials.
Volatility-state family (6 trials per timeframe): doji (body<=0.1*rng), inside_bar (h<=h[i-1] and l>=l[i-1]), nr7 (rng is the smallest of the last 7); metrics next-bar range / mean range of the prior 14 bars, and next-bar |return|.
Excess directional return = sign * (mean fwd return | pattern - mean fwd return | all bars). Net = excess is NOT used for cost; net per trade = sign*fwd - 14 bps - sign*realised funding.
Inference: studentised White Reality-Check on the 18 x 3 family per timeframe (circular block bootstrap of (signal, return) pairs, block 10 bars daily / 24 hourly, 1000 resamples, seed 12345),
plus two-sided Benjamini-Hochberg q-values as a secondary, hypothesis-generating view. Patterns with fewer than 20 events (daily) / 100 (hourly) are reported as INSUFFICIENT-N and still counted as trials.

## 5. Decision rule for the pilot (triage only)
A pattern or rule "passes triage" only if: N >= threshold above; mean net per trade > 0 with block-bootstrap 95 percent CI lower bound > 0; RC p < 0.10 within its family; direction equals the textbook sign.
Passing triage means "worth the full registered study in section 6 of BACKTEST_PROTOCOL.md on VALIDATION then HOLDOUT". It never means adopt.
A pilot result that fails triage is a finding, reported as is. No parameter, definition or window is changed after seeing any output; a change is a new registered hypothesis.

## 6. Trial registry
Every run appends rows to `TRIAL_REGISTRY.csv` (run_id, date, family, variant, tf, window, n, mean_net, note). Trials for deflation = rows of the family. A result without its trial count is invalid.
