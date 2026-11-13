# PRE_REG: NK first-hour low-break + close-back + near-VWAP entry, 20 coins, 5m (frozen before any outcome)

Slug nk1-first-hour-low-break-vwap-1114. Rule source: `nk_stocktalk_1113/review/concepts.json` id first-hour, video JLcDdrHkB5M (EXTRACT.md read). No outcome has been computed when this file is committed (data fetch only).

## Context
Phase for day D from data known at the close of D-1 (UTC daily bars built from the 5m data): MA20 = mean of the last 20 daily closes; slope = MA20[D-1]/MA20[D-6]-1; ADX(14) Wilder with +DI/-DI (FORMULAS.md 30.1, re-implemented here).
- UP: ADX>=20 and +DI>-DI and slope>0. DOWN: ADX>=20 and -DI>+DI and slope<0. Else RANGE. (OURS: 5-day slope lag; NK gives no phase rule.)
- Primary rows trade only the direction that fits: UP -> long, DOWN -> short, RANGE -> both fades (long on early-low break, short on early-high break). Mismatched direction (shorts in UP, longs in DOWN, RANGE excluded) = CONTROL rows only, never in the verdict or the BH family.
Regime mix: reported per split as share of coin-days UP/DOWN/RANGE, and a bull/bear share (close above own 200d SMA). A split >85% one regime is flagged ONE-REGIME.

## Data
Binance spot USDT 5m via data-api.binance.vision, cached at F:\MTS\data_cache\binance\<SYM>USDT_5m.npz. 20 coins: BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC (liquid, chosen by name before any outcome; history from the listing date, 2019 where it exists). Current partial bar dropped. Gaps: a session with a missing bar in its window is skipped.
Splits: DEV <= 2023-12-31; VALIDATION >= 2024-01-01 (by session date). Warm-up: the first 40 days of each coin never trade.

## Sessions (OURS; NK's is the NSE open, 09:15 IST)
- S_UTC: 00:00 UTC. Session end 12:00 UTC (12h, OURS).
- S_NY: NY cash open 09:30 America/New_York converted to UTC per date (13:30 summer / 14:30 winter, zoneinfo). Session end 16:00 New York time.
First hour = 12 5m bars b0..b11 from the open.

## Signal (long; short is the exact mirror with high/low swapped)
- Opening range: first 3 bars b0..b2 (15 min). L = min low of b0..b2. (NK "which low" is NOT_SEEN; OURS.)
- Break: first bar bk in b3..b11 with low < L (NK: break early, first 10 min, sometimes 30 min after; the b3+ window is OURS).
- Close back above: first bar bc in bk..b11 with close > L. 
- No big candle (SOURCED idea «बड़ा कैंडल नहीं होना चाहिए»; threshold OURS): range of bar bc <= 2.5 x the mean range of the 20 bars before the session open.
- Entry "near VWAP" (SOURCED «एंट्री वीवप के पास», no exact touch): first bar j in bc..b11 with close >= VWAP_j x (1-0.001) and close > L; entry at the OPEN of bar j+1 (market, taker). VWAP = session-anchored cumulative sum(typical price x vol)/sum(vol), typical=(h+l+c)/3 (OURS). One trade per coin-session. No trade if no j found by b11.
- Short mirror: early high H = max high b0..b2; break high > H; close back < H; entry when close <= VWAP x (1+0.001) and close < H.

## Stop and R (NK stop: "1h under VWAP or the low breaks, first"; mechanised, OURS)
- Structural stop = min low from b0 through the entry bar (the break low) minus 0 (short: max high).
- Minimum stop distance (lesson from 3 fails): R_dist = max(entry - structural stop, 0.5% x entry, 0.6 x ATR(14) of 5m at signal). Stop price = entry - R_dist. Stop fill at the stop (open if gapped through). Stop checked from the entry bar; if stop and target are both inside one bar the stop is taken.
- R = R_dist/entry. Fee as a fraction of R reported per row (fee_bp / (R x 1e4)).

## Exits (3, all pre-registered; each is a separate row)
- E1 band: target = VWAP_t + 1.5 x sd_t (short: minus), sd_t = volume-weighted sd of typical price about VWAP over the session so far; evaluated per bar after entry from the bar's own prior-bar values (no look-ahead); else stop; else session end close.
- E2 prior-day level: target = max(prior UTC-day high, entry + 1R) (short: min(prior-day low, entry - 1R)); else stop; else session end close.
- E3 session end: exit at the close of the last session bar; stop only.

## Costs
Primary: 12 bp round trip (taker) applied to price return. Pre-registered maker row: fee 6 bp, entry as a limit at the close of signal bar j (fills only if bar j+1 low <= that for long, high >= for short; unfilled = skipped; exits as above, exit fees are inside the 6 bp). Net R = (side x (exit/entry-1) - fee)/R.

## Rows and gate
Rows = 2 sessions x 3 exits x {taker 12bp, maker 6bp} = 12 PRIMARY rows (matched direction, all phases pooled, all 20 coins), read on VALIDATION. Per-phase and per-coin cells and all CONTROL rows (mismatched direction, same machinery) are descriptive. BH-FDR q=0.10 over the 12 primary-row p-values (p = share of day-cluster bootstrap means <= 0).
PASS for a row (all on VALIDATION): n>=100; mean net R>0; 95% bootstrap CI lower>0 per trade AND per day cluster (cluster = UTC date across coins; 5000 resamples, seed 1114); placebo p<0.05; survives BH; mean net R still >0 without the best 5 days (days ranked by summed net R).
Placebo: each real trade is matched by a random entry bar drawn uniformly from b3..b12 on the same coin-session and direction with the same R_dist (as % of entry) and the same exit machinery; 200 draws; p = share of draw-means >= the real mean. Verdict line: PASS if any primary row passes all gates, else FAIL (n<100 rows = UNDERPOWERED).
Tests: test_study.py runs the real study on a synthetic dataset and on the STUDY_BUG=1 look-ahead variant (entry at the signal bar's close using the next bar's extreme); the real one must give no edge on random-walk data, the bugged one must show it.
