# CURRENT MARKET STATE
# Purpose: Persistent slow-moving structural data for delta computation.
#   Updated per JSON snapshot. Overwritten (not appended).
#   Read at session start. Updated after each card generation.
# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\runtime\current_market_state.md
#
# Format: Markdown sections with key: value pairs.
#   Sections: META/WEEKLY/DAILY/POST_FUNDING/INTRADAY_4H/PRIOR_DAY/SWING/STATE/VWAP/CVD/TRADE_FLOW/FUNDING/SPOT_PERP
#   Values are raw numbers/strings. No units in values.
#   "unchanged_count" = consecutive snapshots with no structural change.

---

## META
updated_utc: 2026-09-15T17:10:17.028874700Z
last_snapshot: BTCUSDT_20260915_171
asset: BTCUSDT
last_price: 76188.7

## WEEKLY
poc: 76935.31
vah: 77955.54
val: 75655.02
shape: B
prior_week_poc: 77155.43
two_week_ago_poc: 79892.45

## DAILY
poc: 76386.02
vah: 76846.59
val: 75590.04
shape: B

## POST_FUNDING
poc: 76376.5
vah: 76616.95
val: 75825.49

## INTRADAY_4H
poc: 76429.29
vah: 76474.78
val: 76277.66

## PRIOR_DAY
close: 78153.3
high: 79570.9
low: 76350.1
poc: 78380.6
vah: 78785.7
val: 77415.36

## SWING
1h_high: 79570.9
1h_low: 75560.0
1h_stale: false
15m_high: 76977.4
15m_low: 75560.0
15m_stale: false
5m_high: 76471.4
5m_low: 76151.3
5m_stale: false

## STATE
classification: B
position: in_va
last_verdict: 
unchanged_count: 0

## VWAP
price: 76842.45
slope: falling
band_+1s: 77506.51
band_+2s: 78170.56
band_-1s: 76178.4
band_-2s: 75514.35

## CVD
value: -2931.998
slope: flat

## TRADE_FLOW
net_delta_1m: -119.655

## FUNDING
current_rate: 8.718e-05
extreme: False
open_interest_direction: flat
open_interest_change_1h_pct: -0.05

## SPOT_PERP
basis_pct: -0.04
direction: discount

# END
