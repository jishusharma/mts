# Krown Video Rules Extract - fMRvOt26xcA

- URL: https://www.youtube.com/watch?v=fMRvOt26xcA
- Title: You Don't Need to Learn Chart Patterns (You Need One Thing)
- Upload Date: 2026-07-19

## Trading Rules Stated (SOURCED)

### 1. The Core Pattern Rule: Trend Structure Over Pattern Names (Setup / Filter)
- SOURCED: "you don't even need to understand patterns in any shape or form. you can just learn this one rule and you will be in a extremely extremely good spot and you will be trading patterns without even understanding them... The warning is always a failed extreme. The confirmation is always a broken one." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 00:38 - 00:48, 04:07 - 04:11)
- SOURCED: "I treat a reversal as you need both a lower high and the lower low just like a A reversal from a downtrend to an uptrend requires a higher low plus a higher high." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 06:42 - 06:50)
- Comparison with `krown_params.json`: MATCH. `krown_params.json` implements swing pivot detection (`zone_k`, `swing_tol`, `range_n`) rather than classical geometric chart pattern algorithms, exactly mirroring Krown's rule that all chart patterns reduce to swing highs and lows.

### 2. Breakout Confirmation On Closing Basis (Entry / Trigger)
- SOURCED: "as soon as you close above that neckline, yeah, good to go." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 07:45 - 07:48)
- SOURCED: "The higher low that you need to take out in order to confirm this as a reversal is this guy right here. So as soon as you close below this previous higher low then you have the initial conditions for reversal." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 12:40 - 12:50)
- SOURCED: "once it takes out that previous lower high right here on a closing basis. Reversal confirmed." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 24:22 - 24:27)
- Comparison with `krown_params.json`: MATCH. Closing beyond the swing pivot level is the required confirmation trigger (`confirm_horizon`).

### 3. Price Target Rules (Target)
- SOURCED (Bullish Reversal): "Reversal confirmed. target them the target the previous initial high right here. You might even go in higher than that as well." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 24:27 - 24:32)
- SOURCED (Bearish Breakdown): "Once you take out that previous higher low, that is your confirmation. Target the previous initial low. You might even be going lower than that." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 24:58 - 25:02)
- SOURCED (Range / Base Breakout Target): "As soon as you break that previous equal high, beautiful. You can generally target the difference between the space of the high and the low on the initial base and perhaps higher than that over time as well." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 25:47 - 25:58)
- Comparison with `krown_params.json`:
  - Retest of previous swing low / high: MATCH (`zone_k`, `zone_max`).
  - Height of initial base / measured move: CONFLICT / NOT IMPLEMENTED (OURS). `krown_params.json` does not implement classical measured move arithmetic targets.

### 4. Invalidation and Stop Placement Rules (Stop / Invalidation)
- SOURCED (Double Top): "Invalidation. The higher of the two tops, the tick above and the sequence never broke. that is effectually invalidation for this being a downside reversal." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 09:18 - 09:26)
- SOURCED (Pennant / Flag): "where is the invalidation? The pull's low, super easy." / "invalidation here, the pull's high." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 16:30 - 16:32, 17:00)
- SOURCED (Base / Cup and Handle): "And of course, where is your invalidation? Just a higher low right here. Super simple." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 26:01 - 26:03)
- Comparison with `krown_params.json`: MATCH. Invalidation levels are the preceding structural swing pivot extreme.

### 5. Negative Rules & Risk Discipline (Filter / Sizing)
- SOURCED (Anticipation Filter): "before that anyways you're just taking extra risk for no real return. I I've not found that to be a good way" (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 20:03 - 20:08)
- SOURCED (Failure Rates): "every pattern, like I said, you know, will have a failure rate. Typically, they're between about 20 to 40%, depending upon what answer you're looking at plus what time frame you're looking at um and what pattern you're looking at as well obviously." (URL: https://www.youtube.com/watch?v=fMRvOt26xcA at 02:17 - 02:26)
- SOURCED (Sizing): NO SIZING RULE STATED.

## Notes (OURS)

- Classical 16 chart patterns (head & shoulders, flags, pennants, double tops/bottoms, cup & handles) should not be memorized as rigid shapes; they are simply permutations of higher highs, higher lows, lower highs, and lower lows.
- Every reversal setup has two distinct stages:
  1. The Warning: a failed extreme (e.g. lower high in an uptrend, or higher low in a downtrend).
  2. The Confirmation: a broken opposing extreme (e.g. candle close breaking the prior swing low or neckline).
- Targets are naturally bounded by the opposing structural pivot (prior initial high or low), with extended targets measured by the vertical height of the initial base.
- Invalidation sits at the opposing swing pivot (the flagpole extreme or the preceding higher low / lower high).
