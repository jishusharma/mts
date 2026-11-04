# RESULT: level approach study (C15), DEV only, descriptive, fee-free

Pre-reg `PRE_REG.md` sha256 034766c763c6835ce84466a4e68e4712dfe8da8739a27b2656c36dc465b30856. Data: BTCUSDT 1m 2022-01..2024-06, 10,822 approach events. Validation/holdout unread. Gate 0g on the 3 operator shots: NOT CHECKED (shots are Oct 2026, archive ends 2026-09-26; becomes a live_aid hand-check, expected near_miss, near_miss, close_then_fail). OI: NOT_IN_DATA.

**Verdict: DESCRIPTIVE, no edge claim.** What the table says is that the class label itself carries the information; the layer features add little.

## Read this first
- p_above_level for `accepted` (~0.66-0.88) and `close_then_fail` (~0.25-0.39) is **partly built in**: the class is defined by closes 1-3 bars after the touch, and the outcome is the close 12 bars after that. It shows persistence, not new information.
- The clean rows are `near_miss` and `wick_back` (class known at the event bar): only ~0.26-0.40 of them end above the level 12 bars later; mean forward move is about 0 (+-0.3 %) in all of them, so a level touch that fails to close through is not followed by a drift either way.
- Wilson CIs treat events as independent; they are not (1m events cluster within days), so true CIs are wider.

## Table: kind x class x TF (fwd = mean forward % over 12 bars; p = share ending above the level; ci = Wilson 95 %)
|kind|cls|tf|n|nA|nB|fwd|p|ci|
|---|---|---|---|---|---|---|---|---|
|lh|accepted|15m|37|19|18|0.171|0.703|0.54-0.83|
|lh|accepted|1h|32|19|13|0.778|0.875|0.72-0.95|
|lh|accepted|1m|49|29|20|-0.119|0.735|0.6-0.84|
|lh|accepted|5m|45|26|19|0.131|0.689|0.54-0.8|
|lh|close_then_fail|15m|38|19|19|-0.530|0.342|0.21-0.5|
|lh|close_then_fail|1h|27|17|10|-0.024|0.370|0.22-0.56|
|lh|close_then_fail|1m|42|31|11|-0.067|0.357|0.23-0.51|
|lh|close_then_fail|5m|48|25|23|-0.205|0.250|0.15-0.39|
|lh|near_miss|15m|76|41|35|0.219|0.395|0.29-0.51|
|lh|near_miss|1h|29|16|13|1.007|0.483|0.31-0.66|
|lh|near_miss|1m|526|298|228|-0.005|0.293|0.26-0.33|
|lh|near_miss|5m|179|100|79|0.077|0.341|0.28-0.41|
|lh|wick_back|15m|76|51|25|-0.029|0.395|0.29-0.51|
|lh|wick_back|1h|56|32|24|-0.168|0.196|0.11-0.32|
|lh|wick_back|1m|72|48|24|-0.142|0.278|0.19-0.39|
|lh|wick_back|5m|85|60|25|-0.308|0.294|0.21-0.4|
|pdh|accepted|15m|213|130|83|-0.039|0.714|0.65-0.77|
|pdh|accepted|1h|153|90|63|0.172|0.745|0.67-0.81|
|pdh|accepted|1m|238|169|69|-0.065|0.731|0.67-0.78|
|pdh|accepted|5m|237|158|79|-0.112|0.658|0.6-0.72|
|pdh|close_then_fail|15m|191|129|62|0.001|0.319|0.26-0.39|
|pdh|close_then_fail|1h|143|88|55|0.273|0.392|0.32-0.47|
|pdh|close_then_fail|1m|193|136|57|-0.017|0.373|0.31-0.44|
|pdh|close_then_fail|5m|225|149|76|-0.015|0.373|0.31-0.44|
|pdh|near_miss|15m|690|395|295|-0.004|0.323|0.29-0.36|
|pdh|near_miss|1h|220|118|102|0.153|0.341|0.28-0.41|
|pdh|near_miss|1m|3824|2349|1475|0.001|0.257|0.24-0.27|
|pdh|near_miss|5m|1485|878|607|0.029|0.302|0.28-0.33|
|pdh|wick_back|15m|415|272|143|-0.069|0.328|0.28-0.37|
|pdh|wick_back|1h|335|213|122|-0.083|0.325|0.28-0.38|
|pdh|wick_back|1m|383|292|91|-0.005|0.402|0.35-0.45|
|pdh|wick_back|5m|460|330|130|-0.007|0.387|0.34-0.43|

## Best confirm / invalidation sequences (near_miss, wick_back; n >= 30; RSI>=50, CVD12>0, close >= daily BB mid; 1 = true)
Four lowest and four highest p_above_level across class x TF; pA/pB = dev halves (A < 2023-07-01).
|cls|tf|rsi_ge50|cvd12_pos|above_dbb_mid|n|p_above_level|ci_lo|ci_hi|pA|pB|
|---|---|---|---|---|---|---|---|---|---|---|
|near_miss|15m|1|0|0|64|0.203|0.123|0.317|0.286|0.103|
|near_miss|1m|0|0|0|466|0.210|0.176|0.250|0.222|0.176|
|near_miss|1m|1|1|0|894|0.217|0.191|0.245|0.234|0.181|
|near_miss|1m|0|1|0|122|0.230|0.164|0.312|0.212|0.270|
|near_miss|5m|0|0|1|187|0.369|0.303|0.440|0.409|0.312|
|wick_back|1h|1|1|0|122|0.385|0.304|0.474|0.378|0.417|
|wick_back|1m|1|1|1|194|0.392|0.326|0.462|0.409|0.355|
|wick_back|5m|0|0|1|40|0.500|0.352|0.648|0.484|0.556|

Reading: the spread between best and worst combo is 0.20 to 0.50, with the top (5m wick_back, all three false, n=40) the only one near a coin flip, and its CI (0.35-0.65) is wide; the 1h near_miss "all true" row flips between halves (0.53 vs 0.17). Nothing here passes the pre-registered rule (both halves agree, n >= 30 each, and distinct from the class base rate) strongly enough to name a confirm rule. Invalidation side is steadier: near_miss with RSI < 50 and CVD12 <= 0 and below daily BB mid (1m, n=466, p=0.21 vs class base 0.29, halves 0.22/0.18) points to continued rejection. Full 128-cell table: `sequences.csv` (all kinds pooled), events: `events.csv`.

## Feeds live_aid
Use base rates per class x TF from the table above as the "what happened last time" line; sequences are hypotheses for a fresh-window test (VALIDATION), not a rule.
