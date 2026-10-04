# B131 - Tom proof-5 candidate pool skews 2:1 short upstream

Status: OPEN
Opened: 2026-10-04
Filed by: MTS-2026-10-04-0916Z-DSA-COO

## Defect

The Tom backtest proof-5 pool is 215 short : 105 long. B085 assumed the
skew was in math_object_builder's proof-direction guard (book_imbalance,
last_3_delta). That hypothesis was refuted 2026-10-04: after the 13295c8
book_imbalance guard, the last_3_delta contradiction rate is comparable
(20% of longs, 17% of shorts), and the survivor rate at the proof-direction
level is at parity (8.8% short, 8.6% long).

Where the skew actually lives: upstream. SetupCandidatesBuilder.java
classifies every proof-5 row as long or short before math_object_builder
runs. The 2:1 ratio is produced there.

## Evidence

- F:\MTS\data\tom_bt\allshorts.diag.jsonl, 320 rows.
  Long rows: 105. Short rows: 215.
- Per-direction contradiction counts after 13295c8:
  long_last3_neg: 21 of 105 (20.0%).
  short_last3_pos: 37 of 215 (17.2%).
- Survivors (proof_direction_status = aligned) in the HEAD run: 19 short,
  9 long.

## Open questions

- Why does SetupCandidatesBuilder emit 2 short setups per long setup on
  the same proof-5 bar set?
- Are the zone types biased short (vah/ct_short)? Is the direction
  assignment biased toward short when price is above a value area?
- Is this a real Tom property (he trades more shorts in the sampled
  period) or an artifact of the builder?

## Fix shape (undecided)

Reading pass over SetupCandidatesBuilder.java candidate-emission logic
(around pickTarget, direction assignment, zone selection). Compare the
short-side and long-side emission paths line by line.

## Not fixed here

Filing only.

# END