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
updated_utc: 2026-09-15T13:44:17.051159200Z
last_snapshot: BTCUSDT_20260915_134
asset: BTCUSDT
last_price: 76346.3

## WEEKLY
poc: 77590.41
vah: 78905.73
val: 77265.33
shape: B
prior_week_poc: 77155.43
two_week_ago_poc: 79892.45

## DAILY
poc: 76891.26
vah: 78088.09
val: 76585.8
shape: B

## POST_FUNDING
poc: 76365.8
vah: 76822.02
val: 76100.09

## INTRADAY_4H
poc: 76365.55
vah: 76610.99
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
15m_low: 76807.2
15m_stale: true
5m_high: 77111.9
5m_low: 76065.0
5m_stale: false

## STATE
classification: B
position: below_val
last_verdict: 
unchanged_count: 0

## VWAP
price: 77214.23
slope: falling
band_+1s: 77705.14
band_+2s: 78196.04
band_-1s: 76723.33
band_-2s: 76232.42

## CVD
value: -1445.079
slope: falling

## TRADE_FLOW
net_delta_1m: -2.247

## FUNDING
current_rate: 8.868e-05
extreme: False
open_interest_direction: rising
open_interest_change_1h_pct: 0.42

## SPOT_PERP
basis_pct: -0.05
direction: discount

# END
