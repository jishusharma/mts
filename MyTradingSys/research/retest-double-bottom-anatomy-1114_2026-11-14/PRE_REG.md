# PRE_REG retest-double-bottom-anatomy-1114 (committed before any outcome is computed)

Question: after long BTC falls, how do lows resolve (retest / double bottom / higher low / lower low), and which mechanical confirmation buys the bottom with the best hit-rate and least upside given up.

## Definitions (all mechanical)
- Fall state on day t: >= 4 consecutive red weeks (Mon-start weekly close < prior weekly close) ending at the week containing t, OR close <= 0.80 x max high of prior 56 days.
- First low L: a day in fall state whose low is the lowest low of +/-10 days (fractal), episodes >= 30 days apart (keep the lower).
- Second-low class (scan up to 120 days after L): bounce = running max high since L; pullback = fall >= 8% from a bounce peak that is >= 8% above L. Second low S = lowest low from the pullback until price closes above that bounce peak (or 60 days). S/L < 0.97 lower low (sweep-and-reclaim if a daily close back above L within 5 days); 0.97-1.03 retest/double bottom; > 1.03 higher low; no >= 8% pullback before +30% above L = V-bottom (no retest).
- Confirmations (entry at the close of the trigger bar, causal):
  C1 neckline: first daily close above the bounce peak (swing high between the lows) after a >=8% pullback.
  C2 MA20: first daily close above SMA20 after L while the L-day close is below SMA20.
  C3 4H HH: first 4H close above the last confirmed 4H fractal(3) swing high formed after L, with the last fractal low >= L.
  C4 WT cross: daily WT1 crosses above WT2 with WT1 < -53 after L (indicator reference).
  B0 benchmark: buy exactly at L close (ex-post, unattainable).
- Outcome per trigger: +10% (and separately +20%) from entry before price trades 5% below L (stop = 0.95 x L); horizon 180 days; unresolved marked to market. Net of 12 bp round trip. Upside given up = entry/L - 1.
- Placebo: every fall-state day, entry at close, stop 5% below prior-20d low, same targets.
- Split: DEV episodes with L <= 2023-12-31, VALIDATION L >= 2024-01-01. Bootstrap CI over episodes (2000 draws). Pre-2017-08 has no volume/taker data (price-only, 1D only; flagged). Funding from 2019-09 (fapi); OI history not available beyond ~30 days, reported as n/a.
- Regimes: post-peak bear / base / bull labelled by drawdown from ATH and 200-day SMA slope known at L (bear: close < 200d SMA and DD > 30%; bull: close > 200d SMA and DD < 20%; else base).
- No parameters tuned after outcomes. OURS: 8%, 3%, 30 days, 10-day fractal, 0.95 stop (all OURS, not SOURCED). WT 10/21 and 53/-53 are LazyBear defaults (SOURCED).
