# NO-SOURCE SWEEP - B142, B143, B144, B145

Task: 20261009-181323-no-source-sweep-b142-b143-b144-b145
Run: MTS-2026-10-10 (DSA), worktree mts-dsa
Method: grep over extracts/processed (45 .md) and raw_transcripts_canonical (109 .txt) = 154 files
No code changed.

## B142 - ExtraSetupBuilder stop = previous 1m bar high/low
NOT FOUND in 154 files. No extract or raw transcript states a stop at the previous 1-minute bar high or low.
Nearest language: Tom CONSOLIDATED_RULES.md discusses exhaustion and volume spikes after a move, not a previous-bar stop.
Verdict: NO-SOURCE confirmed.

## B143 - CryptoCred 0.1 percent stop buffer and 1.5R target
PARTIAL. Source: extracts/processed/cryptocred/extract_BHwoN7VPrBE.md, RULE 9 (~33:00):
  "...greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5..."
This sources 1.5R as the trend-aligned baseline and 2.0R for counter-trend. The 0.1 percent stop buffer is NOT FOUND in any file.
Verdict: 1.5R SOURCED (CC Rule 9). 0.1 percent buffer NO-SOURCE.

## B144 - SCB exhaustion volume 2.0x over 240 one-minute bars
NOT FOUND in 154 files. No extract gives 2.0x volume over 240 bars.
Nearest language: extracts/processed/tom/new_selected_10/extract_HySZZSjMxF8.md line 24 and 69 describe exhaustion after increased volume; extracts/processed/tom/CONSOLIDATED_RULES.md describes exhaustion after volume spikes, without the 2.0x / 240-bar numbers.
Verdict: NO-SOURCE confirmed.

## B145 - classify_msb filter_range_noise
SOURCED. Source: extracts/processed/cryptocred/extract_BHwoN7VPrBE.md, RULE 7 (~85:00):
  "market structure breaks which are just less obvious or shorter term... in the middle of nowhere... can just be pure noise... i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade"
Corroborating: RULE 3 (context, not mechanical) and RULE 4 (do not chase every MSB).
Verdict: SOURCED (CC Rule 7, Rule 4, Rule 3).

## Summary
| Row | Parameter | Verdict |
|---|---|---|
| B142 | previous 1m bar stop | NOT FOUND in 154 files |
| B143 | 0.1 percent buffer / 1.5R target | 1.5R sourced (CC Rule 9); 0.1 percent NOT FOUND |
| B144 | 2.0x / 240-bar exhaustion | NOT FOUND in 154 files |
| B145 | filter_range_noise | SOURCED (CC Rule 7) |