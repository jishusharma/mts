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
updated_utc: 2026-10-11T20:09:10.703036900Z
last_snapshot: BTCUSDT_20261011_200
asset: BTCUSDT
last_price: 83637.6

## WEEKLY
poc: 83005.32
vah: 85200.75
val: 80414.81
shape: TWOPEAK
prior_week_poc: 84782.26
two_week_ago_poc: 83964.74

## DAILY
poc: 82996.77
vah: 83758.85
val: 82751.1
shape: TWOPEAK

## POST_FUNDING
poc: 83750.0
vah: 84160.0
val: 83350.0

## INTRADAY_4H
poc: 83632.47
vah: 83639.79
val: 83627.58

## PRIOR_DAY
close: 82941.0
high: 83137.2
low: 82500.0
poc: 82986.68
vah: 83051.91
val: 82680.62

## SWING
1h_high: 83870.0
1h_low: 83041.6
1h_stale: false
15m_high: 83675.4
15m_low: 83645.0
15m_stale: true
5m_high: 83692.1
5m_low: 83625.4
5m_stale: false

## STATE
classification: balance
vp_shape: TWOPEAK
position: in_va
last_verdict: 
unchanged_count: 0

## VWAP
price: 83435.54
slope: rising
band_+1s: 83826.74
band_+2s: 84217.93
band_-1s: 83044.35
band_-2s: 82653.15

## CVD
value: 3156.224
slope: falling

## TRADE_FLOW
net_delta_1m: -13.549

## FUNDING
current_rate: 2.561e-05
extreme: False
open_interest_direction: flat
open_interest_change_1h_pct: 0.01

## SPOT_PERP
basis_pct: -0.05
direction: discount

# END
