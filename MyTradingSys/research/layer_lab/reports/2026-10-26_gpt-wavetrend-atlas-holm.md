# WaveTrend atlas z, p and Holm recomputation

**Verdict: FIX-FIRST for the scope of the nine-cell headline.** The saved test arithmetic reproduces, the directional one-sided Holm screen has 0/9 passes, and W05/W06 are wrong-direction. The prior independent review already identified W07/W08 as invalid C1 encodings; therefore the full nine-cell headline should not be read as a valid nine-cell audit. No source study was rerun and no VALIDATION/HOLDOUT data was accessed.

## Independent calculation

Inputs were the full precision `conj.mean_bps`, `conj.se_bps`, `random_clock.mean_bps`, and `random_clock.se_bps` fields in `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/atlas_results.json` (seeded saved run). For each preregistered cell:

- `difference = conjunction mean - random-clock mean`
- `SE_difference = sqrt(SE_conjunction^2 + SE_random_clock^2)`
- `z = difference / SE_difference`
- Card-requested directional one-sided p-value: `1 - Phi(z)` (alternative: positive incremental return)
- Holm step-down adjustment over all nine p-values, alpha 0.05

The z values below reproduce the saved test z values to rounding. The saved `tests.vs_random_clock.p` values use the two-sided normal tail implemented by `atlas.py:pval`; those saved p-values and saved Holm adjustments also reproduce. The new one-sided values are reported separately because the card requested them; the preregistration and saved report use two-sided p-values, so the tail convention should be labelled explicitly in future summaries.

| Cell | Difference (bps) | SE (bps) | z | One-sided p | Holm adjusted p |
|---|---:|---:|---:|---:|---:|
| W01 | -1.3166 | 1.4429 | -0.9125 | 0.819239 | 1.000000 |
| W02 | -0.6008 | 1.3035 | -0.4609 | 0.677559 | 1.000000 |
| W03 | -0.4659 | 1.4426 | -0.3229 | 0.626633 | 1.000000 |
| W04 | -2.1708 | 4.4215 | -0.4910 | 0.688275 | 1.000000 |
| W05 | -5.9455 | 4.6980 | -1.2655 | 0.897161 | 1.000000 |
| W06 | -4.5116 | 5.6023 | -0.8053 | 0.789681 | 1.000000 |
| W07 | -2.8788 | 18.7025 | -0.1539 | 0.561167 | 1.000000 |
| W08 | 10.3440 | 16.9513 | 0.6102 | 0.270858 | 1.000000 |
| W09 | 3.1936 | 7.8590 | 0.4064 | 0.342239 | 1.000000 |

The smallest directional p is W08 at 0.270858; multiplying by nine already exceeds one, so every Holm-adjusted p is 1.000000. No cell passes alpha 0.05. The saved two-sided p values equal `2 * min(Phi(z), 1-Phi(z))` from the recomputed z (within floating-point precision), and all saved Holm adjusted p values are 1.0.

W05's conjunction mean is -5.78 bps (-0.0578%) and W06's is -4.22 bps (-0.0422%). Both are B2 continuation cells; their means and conjunction-minus-random differences are negative, so the card's wrong-direction observation is confirmed.

## Findings

| Severity | Evidence | Finding | Disposition |
|---|---|---|---|
| MED | `RESULT.md` primary-test table; `atlas.py:pval`; saved JSON `tests.vs_random_clock` | Saved p-values are two-sided, while this card requested one-sided directional p-values. The numbers are internally consistent; the tail convention is the distinction. | Keep the card-requested one-sided results distinct from the preregistered two-sided test, and label both conventions explicitly. |
| HIGH (inherited) | `MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md`, Finding 1 | W07/W08 use C1 divergence events that the prior audit found do not meet the preregistered WT-pivot definition. This prevents treating “0 of 9” as a valid complete nine-cell result. | Carry forward the prior disposition: only seven unaffected cells are interpretable in the existing frozen run; 0/7 pass. Do not edit or rerun the frozen study in this audit. |
| MED (inherited) | `RESULT.md` per-cell statements; prior audit Finding 2 | W04-W08 have realised MDEs materially larger than plausible gross effects, and the saved random-clock contrast uses independent arm SEs rather than a matched day-block inference. | Retain the existing INCONCLUSIVE / limited-evidence wording; no edge or no-effect claim follows. The prior audit's paired-inference follow-up remains separate. |

## Scope and sources

This is a read-only recomputation from the committed saved output, not a rerun of the atlas. Event counts, outcome means and standard errors were not recomputed from market bars. VALIDATION and HOLDOUT remained unread. No code, specification, test, or trading rule was changed.

Sources checked: `MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md` §§1-6; `PRE_REG.md` §§5-6; `RESULT.md`; `atlas_out/atlas_results.json`; `atlas.py` (`pval`, `holm`); prior `AUDIT_2026-10-18.md` findings 1-2.
