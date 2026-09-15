# CURRENT MARKET STATE
# Purpose: Persistent slow-moving structural data for delta computation.
#   Updated per JSON snapshot. Overwritten (not appended).
#   Read at session start. Updated after each card generation.
# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\mts\runtime\current_market_state.md
#
# Format: Markdown sections with key: value pairs.
#   Sections: META/WEEKLY/DAILY/POST_FUNDING/INTRADAY_4H/PRIOR_DAY/SWING/STATE/VWAP/CVD/TRADE_FLOW/FUNDING/SPOT_PERP
#   Values are raw numbers/strings. No units in values.
#   "unchanged_count" = consecutive snapshots with no structural change.

---

## META
updated_utc: 2026-09-15T13:46:15.754372400Z
last_snapshot: BTCUSDT_20260915_134
asset: BTCUSDT
last_price: 76314.9

## WEEKLY
poc: 77590.41
vah: 78905.73
val: 77265.33
shape: B
prior_week_poc: 77155.43
two_week_ago_poc: 79892.45

## DAILY
poc: 76891.26
vah: 78213.28
val: 76565.77
shape: B

## POST_FUNDING
poc: 76365.8
vah: 76812.0
val: 76100.09

## INTRADAY_4H
poc: 76365.55
vah: 76600.97
val: 76065.0

## PRIOR_DAY
close: 78153.3
high: 79570.9
low: 76350.1
poc: 78380.6
vah: 78785.7
val: 77415.36

## SWING
1h_high: 79570.9
1h_low: 76667.3
1h_stale: true
15m_high: 77188.0
15m_low: 76065.0
15m_stale: false
5m_high: 77111.9
5m_low: 76065.0
5m_stale: false

## STATE
classification: B
position: below_val
last_verdict: 
unchanged_count: 0

## VWAP
price: 77208.33
slope: falling
band_+1s: 77702.51
band_+2s: 78196.69
band_-1s: 76714.15
band_-2s: 76219.97

## CVD
value: -1274.397
slope: falling

## TRADE_FLOW
net_delta_1m: 28.105

## FUNDING
current_rate: 8.952e-05
extreme: False
open_interest_direction: rising
open_interest_change_1h_pct: 0.42

## SPOT_PERP
basis_pct: -0.02
direction: discount

# END
