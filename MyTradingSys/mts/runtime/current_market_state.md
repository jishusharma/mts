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
updated_utc: 2026-09-15T13:12:16.219726Z
last_snapshot: BTCUSDT_20260915_131
asset: BTCUSDT
last_price: 77008.8

## WEEKLY
poc: 77590.41
vah: 78905.73
val: 77265.33
shape: B
prior_week_poc: 77155.43
two_week_ago_poc: 79892.45

## DAILY
poc: 76892.44
vah: 77617.91
val: 76687.31
shape: B

## POST_FUNDING
poc: 76892.6
vah: 77032.79
val: 76802.48

## INTRADAY_4H
poc: 76904.14
vah: 76995.35
val: 76843.34

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
1h_stale: false
15m_high: 77188.0
15m_low: 76807.2
15m_stale: false
5m_high: 77111.9
5m_low: 76818.0
5m_stale: false

## STATE
classification: B
position: in_va
last_verdict: 
unchanged_count: 2

## VWAP
price: 77330.14
slope: falling
band_+1s: 77750.56
band_+2s: 78170.99
band_-1s: 76909.71
band_-2s: 76489.29

## CVD
value: 173.364
slope: rising

## TRADE_FLOW
net_delta_1m: -0.122

## FUNDING
current_rate: 9.111e-05
extreme: False
open_interest_direction: rising
open_interest_change_1h_pct: 0.42

## SPOT_PERP
basis_pct: -0.04
direction: discount

# END
