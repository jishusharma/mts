# TRADING CARD — BTCUSDT
# Time: 2026-08-22 11:18 UTC | Price: 76846.1
# Format: SPEED-OPTIMIZED for manual trading decisions (< 10 sec scan)
# ---------------------------------------------------------------------------

================================================================================
  BTCUSDT  |  $76,846  |  11:18 UTC  |  SNAPSHOT v1.1.0
================================================================================

[STATE]  BALANCE  +  BEARISH VWAP  =  AMBIGUOUS
         VP says balanced. VWAP says falling. Need higher TF to resolve.

--------------------------------------------------------------------------------
LEVELS MAP                          DISTANCE      TOM ZONE
--------------------------------------------------------------------------------
  VAH  (Value Area High)    77344      +499       [SHORT ZONE]  <-- not here
  POC  (Point of Control)   77154      +308       [FAIR VALUE]  <-- not here
  VWAP (falling)            77004      +158       [DYNAMIC REF] <-- not here
  PRICE ------------------>  76846       0        [YOU ARE HERE]
  VAL  (Value Area Low)     76663      -183       [LONG ZONE]   <-- not here

  Tom's rule: "I can look for short trades up here and long trades down here."
  You are in the MIDDLE of the value area. Not at a level. No edge.

--------------------------------------------------------------------------------
SETUP CHECKLIST                   STATUS    WHY
--------------------------------------------------------------------------------
  Counter-Trade Short (at VAH)    [NO]      Price 499 pts below VAH
  Counter-Trade Long  (at VAL)    [NO]      Price 183 pts above VAL
  Trend Continuation Short        [MAYBE]   VWAP falling, but VP says balance
  Trend Continuation Long         [NO]      VWAP falling, price below VWAP
  Scalp (VWAP oscillation)        [NO]      VWAP is falling, not sideways
  Breakout (above/below VA)       [NO]      Price inside VA, not at boundary

--------------------------------------------------------------------------------
VERDICT:  NO TRADE  |  WAIT
--------------------------------------------------------------------------------

  Tom: "Counter trades take time. I can wait for the market to make a
        pullback. It returns again to this price area of the value area."

  Tom: "I need an idea for a route plan and I need proof that this idea
        should be put into action right now."

  Missing for ANY setup:
    - Weekly profile (Step 2 of Tom's 13-step)
    - Daily profile   (Step 3 of Tom's 13-step)
    - Price at structural level (VAH, VAL, or POC)
    - Proof of rejection (footprint, delta, absorption)
    - Setup formation (candlestick pattern, B/P structure)

--------------------------------------------------------------------------------
ACTION NOW
--------------------------------------------------------------------------------
  1. DO NOT ENTER. Price is in "no man's land" — no edge.
  2. Set alerts at VAH (77344) and VAL (76663).
  3. Wait for price to reach a level + show proof.
  4. If price breaks below VAL with volume → evaluate breakout short.
  5. If price breaks above VAH with volume → evaluate breakout long.

--------------------------------------------------------------------------------
VISUAL VALIDATION REQUIRED (CoinGlass screenshots)
--------------------------------------------------------------------------------
  [ ] Weekly VP — is weekly trend up, down, or balanced?
  [ ] Daily VP  — is today balanced or trending?
  [ ] 15m/5m footprint — proof of rejection at level?
  [ ] True multi-exchange VP — screener VP is Binance-only approximation

  Without these: state classification is GUESSWORK.

--------------------------------------------------------------------------------
CRYPTO FILTERS (non-Tom, for context only)
--------------------------------------------------------------------------------
  Funding:   0.01%   [neutral]     (Tom never uses this)
  OI:        106K    [neutral]     (Tom never uses this)
  L/S ratio: 0.99    [balanced]    (Tom never uses this)
  Book:      0.65    [sell pressure] (ask > bid depth)

  These do NOT override Tom's rules. Listed for awareness only.

--------------------------------------------------------------------------------
DATA QUALITY FLAGS
--------------------------------------------------------------------------------
  [WARN] VP:     MEDIUM confidence — "may deviate 0.2-0.5% from CoinGlass"
  [WARN] VWAP:   MEDIUM confidence — "Binance 1m OHLCV approximation"
  [WARN] CVD:    MEDIUM confidence — "takerBuyBaseAssetVolume" not true delta
  [WARN] Liquidation: NO DATA — accumulator not connected
  [OK]   Price:  HIGH confidence — direct from exchange
  [OK]   Book:   HIGH confidence — direct from exchange API

================================================================================
TRACE: BVpYGKz9PBU | 43JaKHRvxHk | NkQeOVDTAec | zQTbdEweG3c | y67l86cSqb8
================================================================================

---

# DETAILED REASONING (for review, not for trading speed)
# Only read this if you want to understand WHY the card says NO TRADE.

## Why Tom Would Say WAIT

### 1. Missing Higher Timeframe Context

Tom's 13-step framework (Ld1dhjGdTCA) starts with weekly profile, then daily.
The JSON only provides closes, not profiles.

> "I need the next piece of information. And the next information for us at
> trades to traders is provided by the weekly market profile."
> Source: 3o1VVsfBmmU | T4 | [BEGINNING]

Without weekly + daily profiles, we cannot classify the market state correctly.
The VP shape "B" from the screener is a heuristic, not Tom's actual analysis.

### 2. Price Not at a Structural Level

Tom's counter-trade rule requires price to be at a boundary:

> "I can definitely look for short trades up here and long trades down here.
> And I'll keep doing that until either the big player here or the big players
> here decide that the market will continue to go long."
> Source: BVpYGKz9PBU | T1 | [BEGINNING]

"Up here" = VAH or above. "Down here" = VAL or below.
Current price (76846) is 183 pts above VAL and 499 pts below VAH.
This is the MIDDLE of the value area. No edge.

### 3. No Proof of Rejection

Tom's IDEA + PROOF framework requires BOTH:

> "I need an idea. We've now created that idea in a very simplified way.
> And in the second step, we need proof that at this price level, where we
> have an idea, a corresponding reaction from the players also occurs."
> Source: NkQeOVDTAec | T4 | [BEGINNING]

The idea would be: "Price at VAH/VAL with balance = possible counter-trade."
But price is not at VAH or VAL, so there is no idea to prove.

Even if price were at a level, the JSON provides no footprint data,
no delta, no absorption reading, no finished/unfinished auction data.

> "Of course, you also need to use other appropriate filters alongside it.
> Because it's no use if you just have the cumulative delta somewhere in the
> middle of the chart."
> Source: y67l86cSqb8 | T5 | [BEGINNING]

### 4. VWAP Contradicts VP

The VP says "balanced" (B shape). The VWAP is falling (-0.22%).
These signals contradict.

Tom's VWAP Rule 1:
> "First rule, very important, the VWAP must be based on a trend.
> Only then can I see if I might enter my trade based on counter trades
> on this VWAP."
> Source: 43JaKHRvxHk | T5 | [BEGINNING]

If VWAP is falling, the market may be trending down. But the VP says balance.
In Tom's framework, the higher timeframe profile resolves this contradiction.
Without it, the state is UNKNOWN.

### 5. CVD Provides No Signal

CVD is falling, aligned with price direction. No divergence.
Tom requires CVD + structural level:

> "Of course, you also need to use other appropriate filters alongside it."
> Source: y67l86cSqb8 | T5 | [BEGINNING]

CVD alone is 50% random (5-LLM research, state.md Decisions Log 2026-08-04).
With no structural level reached, CVD is noise.

### 6. Tom's Counter-Trade Requirements Not Met

From zQTbdEweG3c (World Champion counter-trade), Tom requires 3 things:
1. Idea (trend isn't healthy, liquidity is leaving)
2. Proof (setup shows big players doing the opposite)
3. Clean risk management (small risk, clear target)

For this snapshot:
- Idea: POSSIBLE. VWAP falling + CVD falling suggests possible trend down.
  BUT VP says balance, contradicting the idea.
- Proof: NONE. No setup formation. No footprint. No rejection at level.
- Risk management: Cannot calculate because no entry level is defined.

> "If you make trades against the trend, then you need many, many parameters
> that speak in your favor."
> Source: zQTbdEweG3c | T4 | [BEGINNING]

The parameters do NOT speak in favor of a counter-trade here.

---

## What Would Change the Verdict

| If This Happens... | Then Verdict Becomes... |
|--------------------|------------------------|
| Price reaches VAH (77344) + footprint shows rejection | Counter-Trade SHORT — evaluate proof |
| Price reaches VAL (76663) + footprint shows rejection | Counter-Trade LONG — evaluate proof |
| Weekly VP shows strong downtrend + daily confirms | Trend Continuation SHORT on pullback to VWAP |
| Weekly VP shows strong uptrend + daily confirms | Trend Continuation LONG on pullback to VWAP |
| VWAP goes flat + price oscillates around it | Scalp mode — short at upper band, long at lower |
| CVD divergence appears at VAH or VAL | Reversal setup — highest priority |

---

## Gaps Where Tom Gives No Numbers

1. **How close is "close enough" to VAH/VAL?** Tom does not specify. The 183-pt distance to VAL is within normal BTC intraday range, but Tom gives no threshold.
2. **How steep is "very steep" VWAP?** Tom does not quantify. The -0.22% slope is labeled "falling" by the screener, but this threshold is arbitrary.
3. **What VP shape definitively means "balanced"?** Tom mentions "B profile" in examples but gives no formal classification rules.
4. **What CVD divergence threshold?** Tom does not define divergence numerically.
5. **What book depth imbalance is significant?** Tom does not quantify bid/ask ratios.

---

# END OF TRADING CARD
# Status: SAMPLE — For JISHU review. Verdict: NO TRADE (confident).
