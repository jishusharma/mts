# T041 - ENGINE VERDICT TIMEFRAME GAP

Register row: MyTradingSys/research/BUGS.md T041.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (operator, 2026-09-22 continuation)

"note this gap and ask for a audit and research on this by a worker"

Context at time of ask:
  Operator observed a 7-hour up leg on the BTCUSDT 1h klines (10:00-17:00 UTC, close 85856.2 to 86527.5, +671).
  Engine verdict stayed WATCH ct_short throughout. Engine has no read on the hourly leg.
  Also: snapshot structure.1h.stale = true (levels 86309.7 / 86209.1) while MyTradingSys/market_data/klines/BTCUSDT_1h.json is fresh (mtime 2026-09-23T00:31Z).
  CVD delta_1h -1943, delta_4h -3913, OI direction falling (-0.21 pct 1h). Covering-rally shape, not fresh buying.

## STATE

2026-09-22 OPEN. Not yet classified as bug vs design. Audit will decide.
Candidate labels: (a) correct behavior — engine is designed for tape, not legs; (b) missing layer — no multi-timeframe context; (c) defect — engine cannot see legs it should see.
Second open question: structure.1h.stale = true with fresh 1h klines on disk. Is that a mtime check bug, an update path bug, or intended?

## UPDATES (chronological, newest last)

### 2026-09-23T01:00Z - coordinator

Item doc created. Worker dispatch at Dumps/workers/T041_verdict_timeframe_audit/DISPATCH.md.

## EVIDENCE - 2026-09-23T01:30Z, post-close continuity

Source: operator pasted CoinGlass 30m and 1h BTCUSDT screenshots.
Web cross-check run: CNBC TV18, CoinDesk, KuCoin, Glassnode, TradingView (all 2026-09-22).

Chart read (30m CoinGlass, from operator paste):
  price 86417.9, VWAP 85903.7, price 514 above VWAP
  OI peak ~112K -> 108.041K now
  CVD peak ~16K -> 6.44K now (chart shows ~60 pct drop from peak)
  Net Delta 14.115K flat

Web confirms:
  648M USD shorts liquidated in 24h of 751M total (KuCoin/CoinGlass).
  Futures volume +38 pct to 292B USD; OI +1 pct. Volume/OI ratio ~2. Short-squeeze shape (CoinDesk).
  Funding near 0.01 pct benchmark, neutral. Glassnode: below neutral.
  CVD negative across BTC/ETH/XRP/SOL on 24h basis (CoinDesk).
  Options expiry Sept 25: 85K densest buy zone, 88K/90K sell pressure. ~142M buying per 1 pct drop toward 85K (KuCoin/Penguin X).
  2026 pattern: OI contractions 11-19.5 pct in orderly unwinds (CryptoBriefing).

Web contradicts (timeframe or venue mismatch):
  Glassnode weekly: spot CVD -97.9M -> +46M (+147 pct). Perp CVD -312.5M -> +323.1M (+203 pct).
  Resolution: weekly turn vs 24h still negative. Both true at their windows.
  CoinDesk: BTC OI at 716,000 BTC, most since Aug 25 (rising).
  Resolution: chart decline is venue-specific; aggregate rising. Binance ~36-37 pct of total OI.

Schema gap observation (operator question, same session):
  Snapshot structure block records 5m, 15m, 1h only. No 30m, 4h, daily, weekly.
  1h structure stale=true while klines/BTCUSDT_1h.json is fresh (mtime 2026-09-23T00:31Z).
  No OI peak reference. No CVD peak reference. Drawdown from peak invisible in snapshot.
  Consequence: multi-hour range top, OI peak drawdown, CVD peak drawdown are chart-visible but not quotable as system values.

Three-angle revalidation (operator-requested mechanism):
  Angle A - reread inputs vs outputs. Every output consistent with short covering. One caveat: weekly spot CVD turned positive (+147 pct), seed of real-buying case.
  Angle B - assume wrong. Two claims require qualification. (1) CVD anchor mismatch, CoinGlass leftmost bar vs session 00:00 UTC, not comparable per MTS_DICTIONARY cross-category warning. (2) OI decline venue-specific, not aggregate.
  Angle C - model that fails. "Treat chart and snapshot as equivalent" fails on three anchor mismatches (CVD, OI, price drift). "OI down + price up always means X" fails.
  Count: three angles, one agreement. Core intuition (systematic selling into a covering rally) survives.

Candidate new item (not yet registered): T042 - schema gap. Missing 4h/daily/weekly structure, no OI/CVD peak reference, 1h stale while klines fresh.


## EVIDENCE - 2026-09-23T01:30Z, post-close continuity

Source: operator pasted CoinGlass 30m and 1h BTCUSDT screenshots.
Web cross-check run: CNBC TV18, CoinDesk, KuCoin, Glassnode, TradingView (all 2026-09-22).

Chart read (30m CoinGlass, from operator paste):
  price 86417.9, VWAP 85903.7, price 514 above VWAP
  OI peak ~112K -> 108.041K now
  CVD peak ~16K -> 6.44K now (chart shows ~60 pct drop from peak)
  Net Delta 14.115K flat

Web confirms:
  648M USD shorts liquidated in 24h of 751M total (KuCoin/CoinGlass).
  Futures volume +38 pct to 292B USD; OI +1 pct. Volume/OI ratio ~2. Short-squeeze shape (CoinDesk).
  Funding near 0.01 pct benchmark, neutral. Glassnode: below neutral.
  CVD negative across BTC/ETH/XRP/SOL on 24h basis (CoinDesk).
  Options expiry Sept 25: 85K densest buy zone, 88K/90K sell pressure. ~142M buying per 1 pct drop toward 85K (KuCoin/Penguin X).
  2026 pattern: OI contractions 11-19.5 pct in orderly unwinds (CryptoBriefing).

Web contradicts (timeframe or venue mismatch):
  Glassnode weekly: spot CVD -97.9M -> +46M (+147 pct). Perp CVD -312.5M -> +323.1M (+203 pct).
  Resolution: weekly turn vs 24h still negative. Both true at their windows.
  CoinDesk: BTC OI at 716,000 BTC, most since Aug 25 (rising).
  Resolution: chart decline is venue-specific; aggregate rising. Binance ~36-37 pct of total OI.

Schema gap observation (operator question, same session):
  Snapshot structure block records 5m, 15m, 1h only. No 30m, 4h, daily, weekly.
  1h structure stale=true while klines/BTCUSDT_1h.json is fresh (mtime 2026-09-23T00:31Z).
  No OI peak reference. No CVD peak reference. Drawdown from peak invisible in snapshot.
  Consequence: multi-hour range top, OI peak drawdown, CVD peak drawdown are chart-visible but not quotable as system values.

Three-angle revalidation (operator-requested mechanism):
  Angle A - reread inputs vs outputs. Every output consistent with short covering. One caveat: weekly spot CVD turned positive (+147 pct), seed of real-buying case.
  Angle B - assume wrong. Two claims require qualification. (1) CVD anchor mismatch, CoinGlass leftmost bar vs session 00:00 UTC, not comparable per MTS_DICTIONARY cross-category warning. (2) OI decline venue-specific, not aggregate.
  Angle C - model that fails. "Treat chart and snapshot as equivalent" fails on three anchor mismatches (CVD, OI, price drift). "OI down + price up always means X" fails.
  Count: three angles, one agreement. Core intuition (systematic selling into a covering rally) survives.

Candidate new item (not yet registered): T042 - schema gap. Missing 4h/daily/weekly structure, no OI/CVD peak reference, 1h stale while klines fresh.

### 2026-09-23T11:00Z - coordinator close-out, session MTS-2026-09-23-0831Z

Reframe: the original observation (engine missed a 7h leg) was a misframe. Worker rounds 1-3 established:
- No HTF direction layer exists in the engine (determineDirections reads price_vs_va and price_vs_poc only).
- During 2026-09-22T10:00-17:00Z the engine printed repeated ct_short setups against the recovery; it was actively fading, not blind.
- The HTF principle is present in compiled_engine.md as [PRINCIPLE - NOT ALGORITHM] (L38, L64, L128, L189, L388). Documented principle, not coded algorithm. That is a convention, not a defect.

Status: CLOSED. Not a defect. If operator wants an HTF direction layer as a feature, file separately as a task, not this bug.

Companion: B065 filed for the stale-swing consumer gap, which is the one real defect the T041 investigation surfaced.

# END
