================================================================================
  BTCUSDT  |  $78,677.20  |  11:00:29 UTC  |  SNAPSHOT v1.1.0
================================================================================

[STATE]  BALANCE  |  Weekly B + Daily B + Post-funding B + 4H B. VWAP slope 0.0022% = shallow. CVD flat.

--------------------------------------------------------------------------------
LEVELS MAP                          DISTANCE      ZONE
--------------------------------------------------------------------------------
  W-VAH    79,860.04   +1,182.84   [SHORT     ] <-- not here
  D-VAH    79,159.92     +482.72   [SHORT     ] <-- not here
  D-POC    79,019.64     +342.44   [FAIR      ] <-- not here
  W-POC    78,899.73     +222.53   [FAIR      ] <-- not here
  PF-VAH   78,791.25     +114.05   [DYNAMIC   ] <-- near
  FVG      78,779.60     +102.40   [RESISTANCE] <-- near
  VWAP     78,775.77      +98.57   [DYNAMIC   ] <-- near
  PRICE    78,677.20       +0.00   [HERE      ] 
  D-VAL    78,558.71     -118.49   [LONG      ] <-- near
  PF-POC   78,479.51     -197.69   [FAIR      ] <-- near
  PF-VAL   78,368.90     -308.30   [LONG      ] <-- not here
  W-VAL    78,114.48     -562.72   [LONG      ] <-- not here
--------------------------------------------------------------------------------
SETUP CHECKLIST                   STATUS
--------------------------------------------------------------------------------
  CT Short (at VAH)                 [NO   ]  Price 483 pts below D-VAH. CT short requires price at upper boundary.
  CT Long  (at VAL)                 [MAYBE]  Balance + B profile supports idea. Price 118 pts above D-VAL. No footprint proof yet.
  TC Long                           [NO   ]  Market is balance, not trend. VWAP not steep.
  TC Short                          [NO   ]  Market is balance, not trend. VWAP not steep.
  Scalp (VWAP)                      [NO   ]  VWAP rising, not sideways. Tom: "Only if VWAP is sideways."
  Breakout (below VAL)              [MAYBE]  Price above D-VAL. No break, no speed/volume proof.
--------------------------------------------------------------------------------
VERDICT:  WAIT / WATCH  |  Band C (60/100)
--------------------------------------------------------------------------------

> "I can definitely look for short trades up here and long trades down here."
> BVpYGKz9PBU

ACTION NOW:
  1. ALERT at D-VAL 78558.71 — CT Long if price reaches + proof
  2. ALERT at PF-VAH 78791.25 — watch for rejection
  3. PULL 15m footprint at VAL — check absorption/rejection
  4. WAIT — price in no man's land, no edge
  5. DO NOT enter before proof

--------------------------------------------------------------------------------
DATA QUALITY
--------------------------------------------------------------------------------
  [OK]   Price, Book, Funding, OI, Timeframes  |  HIGH confidence
  [WARN] VP (all), VWAP, CVD, Liquidation            |  MEDIUM — verify on CoinGlass

[Full card with detailed reasoning + trace + R:R math saved to disk]

--------------------------------------------------------------------------------
DETAILED REASONING — for review only
--------------------------------------------------------------------------------

Story: Since 08:00 UTC funding reset, price dropped to PF-POC ~78479.51,
then recovered to current 78677.20. Recovery stalled below unfilled bearish
FVG at 78779.60. Price is in upper half of 3h
micro-balance but lower half of daily balance. Higher TF wins: daily dominates.

Why CT Long at VAL is the only viable idea:
- Balance market = CT is primary mode
- Price below D-POC = in "unfair" lower area, probability of return to POC
- B profile on all TFs = weakness at extremes
- CVD flat = no strong selling pressure
- Prior day close = current price = market has gone nowhere

Why no trigger exists yet:
- Price has not reached D-VAL (78558.71)
- No rejection wick at current level
- No absorption visible in JSON data

R:R Math (theoretical CT Long at VAL):
  Entry:  78558.71
  Stop:   78396.80 (15m swing low)
  Target: 79019.64 (D-POC)
  Risk:   161.91 pts
  Reward: 460.93 pts
  Gross R:R: 2.85:1
  NET R:R:   2.14:1 (after 25% friction)
  Status: ABOVE Tom's 2:1 minimum

Why verdict is WAIT not EVALUATE:
- EVALUATE requires all mandatory TRUE + at least one proof present
- Price at zone = UNKNOWN (not at VAL yet)
- Footprint proof = UNKNOWN (requires visual validation)
- Two mandatory conditions UNKNOWN → Band C

================================================================================
TRACE: BVpYGKz9PBU | 43JaKHRvxHk | Ld1dhjGdTCA | YmygDgtoxO8 | zQTbdEweG3c |
       qLnQan0KGmQ | NkQeOVDTAec | VumVuGnCcFM | Fj4FDZQxw0I | 3JqMyzE8jIQ |
       oa8kxSLLkAo | 4MoNjEQ2Dd8 | k0zm5NYn0IQ | y67l86cSqb8
================================================================================
