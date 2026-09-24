# MANUAL PATTERNS - Reads not yet automated
# Status: Working notes. NOT validated rules.
# Rule 32 applies before any pattern enters compiled_engine.md.
# Update when a pattern is validated or refuted.

## 1. FOOTPRINT PATTERNS (bid/ask per level)
Meaningful only at a zone. Mid-range = noise.

Absorption - large one-sided bar + price holds + immediate opposite bars.
  Trigger: bar >= 1,500 BTC one side, then opposite bars >= 150, price
           does not break.
  Example: 2026-09-10 12:52 UTC, BTC 76,634. Sell bars -2,034 / -2,630,
           absorbed by +233 / +212. Bounce followed.

Exhaustion - single large bar + declining follow-through + opposite side
returns.
  Trigger: bar >= 500, next 2-3 bars shrink, opposite direction re-enters.
  Example: 2026-09-10 14:20 UTC, BTC 77,400. +619 buy, then -402 sell,
           price rolled over.

Chain 2+ patterns for conviction.

## 2. SETUP QUALITY SCORECARD
Count signals aligned with setup direction.

SHORT-aligned:
  1. OI rising AND price falling
  2. cvd.slope falling
  3. finished_auction.direction = "sell"
  4. delta_flip pos->neg at zone
  5. book_imbalance < 0.5
  6. rejection wick MODERATE+ at zone

LONG-aligned: mirror.

Decision: 4+ = tradeable. 2-3 = wait. 0-1 = reject.
Caveat: OI ambiguous when 1h and 30m disagree. Do not count it then.

Applied: 2026-09-10 14:01 UTC, used to reject a marginal short.
Not Rule-32 validated.

## 3. BOUNCE PATTERN (candidate rule)
At a structural low, all four fire together:
  - sell climax bar (large negative delta)
  - immediate buy absorption (bars >= +150)
  - CVD flat (not making new lows)
  - OI flat (no new shorts entering)
Result: high-probability bounce.
Observed: 2026-09-10, 76,634 -> 77,400 (+766 pts). 1 observation.
