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

## 2026-10-04T12:50Z - direction path read

Reading pass over SetupCandidatesBuilder.java direction logic complete.

- determineDirections (L253-274): above_vah -> [short, long]; below_val ->
  [long]; in_va above POC -> [short]; in_va below POC -> [long]; in_va at
  POC -> [short, long]. Symmetric in the general case.
- determineSetupType (L412-447): vah-family zones -> ct_short only;
  val-family zones -> ct_long only; POC zones -> both directions only in
  trend_unhealthy; vwap and vwap_band -> both in balance, long-only in
  trend_healthy; fvg -> null; prior_day_close -> both.
- Zone list from extractZones (partial read): 4 vah-family, 4 val-family,
  4 POC, 1 vwap, 4 vwap_band. Balanced across short-only and long-only
  families.

The direction-assignment path reads as symmetric. The 2:1 short skew is not
visible here.

Next stage: the proof-count distribution. The 320 proof-5 rows are a filtered
subset, not the raw candidate pool. If the proof detectors (rejection_wick,
absorption, delta_flip, volume_spike) fire more readily on vah-zone shorts
than on val-zone longs, the proof-5 subset skews short even though the raw
candidate pool is balanced. Read the proof detector code in
SetupCandidatesBuilder.java and math_object_builder.py.

B131 stays OPEN. Next fix shape is a reading pass over the proof detectors.

## 2026-10-04T13:20Z - mechanism identified (DSA read)

Base rate from allshorts.diag.stdout.txt, top-candidate direction by
proof count, all 120892 rows in the 57-month cache:

    proof 0: long=6004  short=4827
    proof 1: long=11045 short=9328
    proof 2: long=20105 short=19000
    proof 3: long=19668 short=19828
    proof 4: long=5231  short=5536      (balanced)
    proof 5: long=105   short=215       (2:1 short)

The pool is balanced through proof 4. The skew enters at the 4 to 5
transition. One signal contributes asymmetrically at the marginal
step.

The signal is book_imbalance, counted in SetupCandidatesBuilder.java
L575-580:

    if (bookImbalance != null && bookImbalance != 0.0) {
        boolean favoursTrade = "long".equals(direction)
            ? bookImbalance > 1.5
            : bookImbalance < 0.67;
        if (favoursTrade) count++;
    }

Short: bid_ask_ratio < 0.67 (ask-heavy) counts.
Long:  bid_ask_ratio > 1.5 (bid-heavy) counts.
In the 57-month sample the ask-heavy side is far more common. Every
short candidate receives one count; every long receives zero on that
slot. Longs must score 5 of the remaining 6; shorts must score 4 of
the remaining 6. At a 5-of-7 threshold that produces the observed
2:1 pattern at proof 5 and the balance below it.

The other direction-relevant detectors are symmetric:

- rejection_wick (L663-700): short branch checks high >= zone and
  close < zone; long branch checks low <= zone and close > zone.
  Quality buckets identical. No proximity threshold either side.
- finished_auction (L736-750): direction-neutral detection; direction
  gate in countSignals L565-570, by design.
- delta_flip (L753-780): direction-neutral.
- cvd_aligned (L819-835): reads cvd.slope and net_delta_1m.
  Regime-driven, not structurally biased.

The math_object_builder proof-direction guard (L440-476) runs after
Java emits direction. It cannot be the source. B085 hypothesis is
refuted by the base rate data above.

Sample-version note: allshorts.diag.prefix.jsonl flags all 105 longs
with book_imbalance ask-heavy in pd_details; allshorts.diag.jsonl
(mtime 2026-10-02 14:21:45Z, three seconds earlier) does not. The
two runs reflect pre-fix and post-fix states. Which is which is not
proven from this read. The 13295c8 guard exact effect on this diag
pair is a separate check.

Evidence-cell correction: B131 own evidence cell says survivors in
the HEAD run are 19 short, 9 long. allshorts.diag.prefix.stdout.txt
shows survivors n=19, all short, zero long. The 9 long figure is
not supported by the diag output.

## Fix shape (revised)

Book_imbalance is the asymmetry. Three shapes:

A. Remove book_imbalance from the proof count entirely. It becomes
   display-only in the proof JSON. Consistent with PROJECT_VISION:
   book imbalance has no Tom source per MTS_DICTIONARY (corpus
   vocabulary hit count 0).
B. Symmetrise the gate: longs count only when bid-heavy > 1.5,
   shorts count only when ask-heavy < 0.67. Same as current, but
   explicit that the absence of an opposing signal is not proof.
C. Cap countSignals at 6 non-book signals. Book_imbalance stays in
   JSON, never counts.

Shape A matches the doctrine that non-Tom signals do not gate core.
The edit is one conditional at SetupCandidatesBuilder.java L575-580.
Needs a test that proves a balanced input pool yields a balanced
proof-5 output.

RESOLUTION 2026-10-05T03:30Z: shape A applied. book_imbalance removed from
countSignals (SetupCandidatesBuilder.java); JSON and math_object_builder guard untouched.
Tests: SetupCandidatesBuilderRulesTest.proofCountFourOfSixIgnoresBookImbalance,
proofCountFiveOfSixIgnoresBookImbalance; CountSignalsD4Test book tests flipped to expect 0.
mvn test: 130 run, 0 fail. Follow-up: re-run allshorts diag to confirm proof-5 parity.
