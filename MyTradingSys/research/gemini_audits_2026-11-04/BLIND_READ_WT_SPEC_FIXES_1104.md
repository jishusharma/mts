# Blind read: WT SPEC.md fixes for Gemini defects 1, 3, 4, 5 (Card 1 and Card 2)

Method: SPEC.md read first (lines 1-22, Card 1 l.9-17, Card 2 l.19-21); defect list in REVIEW_GEMINI_1104.md read after, and only its defects 1, 3, 4, 5. Test: is the rule exact enough to code without a judgment call, and is every number labelled SOURCED or OURS. No study run, no new number invented. Reader: Claude Builder (card labelled Gemini).

| Defect | SPEC.md line that now answers it | Exact enough to code? Labelled? | Status |
|---|---|---|---|
| 1 Burned VALIDATION/HOLDOUT feeds the Card 1 verdict | l.5 discloses the seen bars and says later VALIDATION/HOLDOUT reads are NOT clean first looks, "prefer a different instrument or a later forward window"; l.17: BTCUSDT 2024-07..2025-06 "is not a clean confirmation ... exploratory", PRE_REG must name the unpeeked target before any run, builder adds the `holdout_reads.csv` row via `splits.read_holdout` | Yes: rule forbids the burned window as confirmation and requires naming the target before a run. Labelled (OURS) | RESOLVED |
| 3 m (Holm) and bin edges unfrozen | l.14 "Bin edges (OURS), frozen here": drop size = DEV terciles of wt1 min (3), hours since last top dot 0-12/12-24/>24 (3), session 21-08/08-13/13-21 UTC (3), RSI14 lower vs not (2), 4h slope sign (2); l.15 "m = 14 (marginal cells) = 3+3+3+2+2 = 13 + 1 his-context subset" feeding `prereg_gate.py --m 14` (3+3+3+2+2 = 13 checked) | Yes: marginal not Cartesian, integer fixed. Labelled OURS. Tercile edges are data-derived but fixed by rule on DEV only | RESOLVED |
| 4 Colloquial divergence event | l.11: "high around the earlier cross" = max high over +-k bars, k = 3 (OURS); "since that dip" = from the bar of min wt1 between the two crosses to the confirming bar; l.12: wave = down-cross with min(wt1,wt2) > 0, count 3 SOURCED Bible | The three phrases Gemini named are exact. Labelled | RESOLVED (see residuals) |
| 5 Paired net-bp difference undefined | l.21: primary read per TF = mean net bp of nested trades minus mean net bp of the baseline dots the gate rejects, 95 % day-block bootstrap CI (block = one UTC day, zero-trade days stay in resample), n_nested and n_rejected stated; notes why a pairwise difference is undefined | Yes: statistic, resampling unit and counts defined; no sizing needed because the unit is per-trade mean. Labelled OURS | RESOLVED |

## Residuals (not part of the four defects; for the spec owner)
- l.11 "at least 10 higher" does not say higher than what (read as: earlier cross wt1 >= confirming-cross wt1 + 10); and if several earlier down-crosses qualify within 48 h, which one is used is not stated. A coder must pick: judgment call left.
- l.16 adds a second metric (first-touch -1 % vs +1 %) next to net bp at 24 bars; m=14 counts feature cells, not metrics, so whether the second metric multiplies m is not stated.

VERDICT: RESOLVED
