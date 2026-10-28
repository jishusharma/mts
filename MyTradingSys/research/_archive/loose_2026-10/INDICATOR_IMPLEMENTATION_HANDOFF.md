# INDICATOR IMPLEMENTATION HANDOFF
# Session: MTS-2026-09-18-0848Z
# Written: 2026-09-18 for the next session
# Purpose: research, validate, and implement derivative positioning indicators
# Every claim cites a source. Verify before implementing.

## OPERATOR COMMANDS (verbatim, this session)

1. "how is this chart for a reading - we saw which indicators MTS needs -
   these are few i just added - see how to use them - research valid confirmed
   professional sources and actual truth on internet - there values in status
   bar and labels on price scale. so this is 5 min. if needed we can colled
   data for different time frames and keep tailing the 1-3 min timeframes.
   Of course we would like to get the API wok done but we any way need
   validations and confirmations/comparions. What u think?"

2. "make a report like last time exactly repreat my commands and ask to
   investigate and implement these"

## WHAT THIS REPORT IS

A handoff describing nine derivative indicators observed on a CoinGlass 5m
chart today, their professional reading rules, and the work required to
investigate, validate, and implement them in MTS. The report names what MTS
has, what it lacks, and what the missing pieces would need.

## THE CHART OBSERVED

Nine panels on CoinGlass, BTCUSDT Perpetual, 5-minute timeframe, 09-18 session.
Panel order top to bottom:
  1. Open Interest (Candles)
  2. Open Interest Delta
  3. Cumulative Volume Delta (CVD Candles)
  4. Net Delta
  5. Aggregated Futures CVD
  6. Net Longs
  7. Net Longs (New)
  8. Net Shorts
  9. Net Shorts (New)

## PANEL-BY-PANEL: WHAT EACH MEASURES

### 1. Open Interest (Candles)
- Value: total open futures contracts, OHLC per 5m bar
- Read: rising OI + rising price = new long money. Rising OI + falling price
  = new short money. Falling OI + rising price = short covering. Falling OI +
  falling price = long liquidation
- Source: CoinGlass official docs on OI
- MTS status: has open_interest.direction and change_1h_pct.
  Direction only. No OHLC, no bar shape.

### 2. Open Interest Delta
- Value: bar-to-bar change in OI
- Read (TradingView "OI Delta" scripts): four states by cross of delta sign
  and OI level. Positive delta + rising OI = Aggressive Longs. Negative delta
  + rising OI = Aggressive Shorts. Negative delta + falling OI = Rekt Longs.
  Positive delta + falling OI = Rekt Shorts
- Source: BackQuant, TradingView scripts (OI Delta 4-state classification)
- MTS status: NOT PRESENT.

### 3. Cumulative Volume Delta (CVD)
- Value: session-cumulative taker buy minus taker sell
- Read (CoinGlass official): "The absolute numerical value of the CVD line
  itself is not important; its analytical value lies entirely in its slope
  (trend direction) and its relationship with price action"
- Healthy: price and CVD move together. Divergence: leading reversal signal
- Source: CoinGlass docs, BackQuant, Kaiko Research
- MTS status: has cvd.value, cvd.slope, cvd.cvd_recent.*.
  B044 open: computed from kline taker-buy proxy, not aggTrade.

### 4. Net Delta
- Value: positioning, long opens minus short opens. NOT flow
- Read: align with CVD = healthy trend. Diverge from CVD = distribution or
  accumulation in progress
- Source: CoinGlass docs, MTS_DICTIONARY already flags this distinction
- MTS status: has trade_flow.net_delta_* which is mislabelled. MTS name is
  flow (Volume Delta). CoinGlass Net Delta is positioning. No field for
  CoinGlass Net Delta.

### 5. Aggregated Futures CVD
- Value: CVD across all exchanges, not just Binance
- Read: confirms or contradicts single-venue CVD. Exchange-specific CVD can
  diverge from aggregate during liquidations and arbitrage
- Source: Perplexity research on multi-venue CVD
- MTS status: NOT PRESENT. Single-venue only.

### 6-9. Net Longs, Net Longs (New), Net Shorts, Net Shorts (New)
- Value: four positioning states derived from OI + CVD cross
- Read (Coyote Net Positions, TradingView): NL = fresh buyers entering.
  NS = fresh sellers entering. LC = longs exiting or liquidated.
  SC = shorts covering or squeezed
- Source: TradingView "Coyote Net Positions" indicator
- MTS status: NONE of the four present.

## RESEARCH SOURCES VALIDATING THESE

### Tier 1 (institutional)
- CoinGlass official docs on OI, CVD, funding, long/short ratios
- BackQuant research on OI and CVD framework
- Kingfisher methodology for separating observed vs modeled data
- Glassnode on-chain positioning models

### Tier 2 (practitioner, verified)
- TradingView "OI Delta" scripts (2 confirmed implementations)
- TradingView "Coyote Net Positions" script
- Perplexity research: multi-venue CVD vs single-venue
- Bybit Academy on derivative flow metrics

### Tier 3 (practitioner, unverified)
- Various blog posts on OI quadrant classification
- Crypto twitter commentary

## THE PROFESSIONAL READING SEQUENCE

From Kingfisher and BackQuant, the correct order:

1. OI + Price - is this new money or forced flow?
2. CVD - who is aggressive right now?
3. Net Longs / Net Shorts - is positioning one-sided or balanced?
4. Funding + Liquidation map - where is the fuel?

A reading that answers all four is contextual. Agreement across panels is
evidence. Disagreement exposes uncertainty.

## WHAT THE CHART SHOWED AT 14:30Z TODAY

| Panel | Reading | Implication |
|---|---|---|
| OI Candles | Rising 107.5K to 108.2K | New capital |
| OI Delta | Mostly yellow, small green cluster | Normal activity, no cascade |
| CVD | Recovering -8K to -3.3K | Buyers returning |
| Net Delta | +3.1K rising | Positioning long |
| Agg CVD | Rising | Confirms single-venue |
| Net Longs | +2.1K | Longs entering |
| Net Longs (New) | +4.7K | Fresh longs |
| Net Shorts (New) | -1.9K | Fresh shorts |

Reading: bullish stack with a caveat. Both sides entering (NL and NS both
firing) = balanced fight, not one-sided commitment.

## WHAT MTS HAS vs WHAT IT NEEDS

| Indicator | MTS field | Binance endpoint | Status |
|---|---|---|---|
| OI Candles | open_interest.direction only | /futures/runtime_data/openInterestHist | Partial |
| OI Delta | none | derived from OI history | Missing |
| CVD | cvd.value (kline proxy) | /fapi/v1/aggTrades | Partial (B044) |
| Net Delta (flow) | trade_flow.net_delta_* | /futures/runtime_data/takerBuySellVol | Mislabelled |
| Net Delta (positioning) | none | derived from OI breakdown | Missing |
| Agg CVD | none | multi-venue, not in Binance | Missing |
| Net Longs | none | derived | Missing |
| Net Longs (New) | none | derived | Missing |
| Net Shorts | none | derived | Missing |
| Net Shorts (New) | none | derived | Missing |

## THE DEAD CODE FINDING

BinanceClient.java line 50-51 defines:
  public JsonNode takerBuySellVol(String symbol, String period, int limit) throws IOException {
    return get(BASE + "/futures/runtime_data/takerBuySellVol?symbol=" + symbol + "&period=" + period + "&limit=" + limit);
  }

Zero call sites. Method defined, never called. The B044 fix already exists
on disk. It was written and then never wired into the snapshot.

Same pattern for topLongShortPositionRatio (L66) and
topLongShortAccountRatio (L71). Both defined, both never called.

## OPERATOR PRIORITIES FROM THIS SESSION

- Build validation and confirmation before implementation
- Collect multi-timeframe data if needed
- Tail 1-3 minute timeframes for live confirmation
- API work is wanted but validation comes first
- "these are few i just added" - the CoinGlass panels are the target state

## WHAT TO INVESTIGATE (READ-ONLY)

### Investigation 1 - Verify dead code
Confirm takerBuySellVol, topLongShortPositionRatio, and
topLongShortAccountRatio are defined but never called. Search all .java
files for call sites.

### Investigation 2 - Map endpoints to indicators
For each of the nine CoinGlass panels, identify the Binance endpoint(s)
that produce it. Mark which are direct, which are derived, which are
multi-venue only.

### Investigation 3 - Check for available history
Binance /futures/runtime_data/openInterestHist and /futures/runtime_data/takerBuySellVol
have 30-day windows. Determine what history is available for validation
against the CoinGlass values in the chart.

### Investigation 4 - Research alternatives
Verify whether the nine CoinGlass panels match what the research says
to read. If CoinGlass uses different formulas from the standards, document
the difference.

### Investigation 5 - Compare MTS CVD to CoinGlass CVD
Pull the current MTS cvd.value and the CoinGlass CVD from the same moment.
Compare. The anchor differs (00:00 UTC vs leftmost visible bar). Note the
offset and the directional agreement.

## WHAT TO IMPLEMENT (ONLY AFTER INVESTIGATION)

### Phase 1 - Wire the existing dead code
1. Wire takerBuySellVol into snapshot CVD. This is the B044 fix.
2. Wire topLongShortPositionRatio and topLongShortAccountRatio into
   a new positioning block in the snapshot.

### Phase 2 - Add OI delta
1. Compute OI delta per cycle from the OI history.
2. Classify into four states (Aggressive Long / Aggressive Short /
   Rekt Long / Rekt Short).
3. Emit as open_interest.delta_state.

### Phase 3 - Add positioning states
1. Derive Net Longs / Net Shorts from OI + CVD cross.
2. Emit four flags: net_longs, net_longs_new, net_shorts,
   net_shorts_new.
3. Each is boolean or a strength value.

### Phase 4 - Frame wiring
1. The frame label (MTS-FRAME) is display-only today.
2. Wire it into SetupCandidatesBuilder so TREND_UP enables TC long
   candidates at VWAP / value area pullbacks.

### Phase 5 - Multi-venue
1. Add Bybit and OKX OI/CVD feeds.
2. Emit aggregated CVD alongside single-venue.

## CONSTRAINTS

- Rule 32: any wiring that changes a verdict needs 3-snapshot proof.
- Rule 33: every field requested must be read by a rule.
- Rule 11: every claim in the implementation must cite its evidence.
- Read-only until user approves the investigation.
- No writes to critical files without four-step proof.
- All timestamp UTC. Line endings LF.
- No BOM in .py, .json, .ps1. Use Write-NoBom helpers.

## VALIDATION COMMANDS (read-only)

### Confirm dead code
    Select-String -Path .\src\main\java\datafeed\*.java -Pattern 'takerBuySellVol|topLongShortPositionRatio|topLongShortAccountRatio' -Context 1,2

### Check current MTS fields
    $snap = Get-ChildItem .\runtime_data\snapshots\BTCUSDT_*.json | Sort LastWriteTime -Desc | Select -First 1
    $j = Get-Content $snap.FullName -Raw | ConvertFrom-Json
    "cvd=$($j.cvd.value) slope=$($j.cvd.slope) oi=$($j.open_interest.direction)/$($j.open_interest.change_1h_pct)"
    "net_delta_1m=$($j.trade_flow.net_delta_1m) net_delta_15m=$($j.trade_flow.net_delta_15m)"

### Check available history on Binance endpoints (requires internet)
    # GET https://fapi.binance.com/futures/runtime_data/openInterestHist?symbol=BTCUSDT&period=5m&limit=10
    # GET https://fapi.binance.com/futures/runtime_data/takerBuySellVol?symbol=BTCUSDT&period=5m&limit=10
    # GET https://fapi.binance.com/futures/runtime_data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=10

### Check what reads each field today
    Select-String -Path .\scripts\core\*.ps1, .\scripts\live\*.ps1, .\MyTradingSys\runtime\*.py -Pattern 'open_interest\.|trade_flow\.net_delta|cvd\.value' | ForEach-Object { "$($_.Filename):$($_.LineNumber): $($_.Line.Trim())" }

## REASONING FOR THE ORDER

1. Investigation before implementation. The dead code exists but the
   path to wire it must be understood first.
2. Phase 1 first because it uses existing code. Lowest risk.
3. Phase 2 and 3 require derived computation. Medium risk.
4. Phase 4 is a verdict-wiring change. Rule 32 applies.
5. Phase 5 requires multi-venue infrastructure. Highest effort.

## WHAT NOT TO DO

- Do not add all nine indicators at once. One phase per session.
- Do not wire anything into the verdict path without Rule 32 proof.
- Do not treat CoinGlass values as ground truth (they are modeled).
- Do not assume the Binance endpoints produce the same values as
  CoinGlass. CoinGlass aggregates 20+ exchanges; Binance is one.
- Do not commit without the four-step hash proof on any critical file.

## VERIFICATION CHECKLIST FOR NEW SESSION

Run in order. Confirm each output before proceeding.

1. Boot and confirm manifest.
2. Start mts-live. Confirm MTS-PROC.
3. Read apparatus_log tail 60.
4. Read journal tail 30.
5. Confirm fire condition from code (start-trading-day.ps1 lines 153-168).
6. Confirm dead code (Investigation 1 commands above).
7. Confirm current MTS fields (Investigation 5 commands above).
8. Fetch sample from each Binance endpoint.
9. Ask user which phase to start with.
10. Only then write.

## CORRECT ORDER FOR THE NEW SESSION

1. Read this report.
2. Verify every claim against disk.
3. Confirm all dead code findings.
4. Fetch one sample from each Binance endpoint.
5. Present findings to user.
6. Ask for phase selection.
7. Investigate the chosen phase.
8. Implement only after investigation is complete.
9. Validate with Rule 32 if verdict path is touched.
10. Log to journal.

# END