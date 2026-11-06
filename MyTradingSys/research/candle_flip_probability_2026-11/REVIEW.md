# REVIEW: Haiku credit review of PRE_REG.md, flip_table.py, flip_model.py and RESULT.md (first run)

Job `flip-review-1106` through `scripts/dev/api_job.py` (claude-haiku-5-5, cap 3 USD, actual cost 0.03 USD, 1 turn, no tools). The prompt asked for leakage, anchor errors and
cell-count inflation, and carried the four files in full (commit 9f7dc27ae state). The reply below is verbatim. The table after it says what was done with each finding; the
changes are PRE_REG.md Amendments A1-A8 and the rerun RESULT.md.

## Verbatim reply

```
1. blocker | flip_model.py `cluster_mean_z(..., s["cid"])`; RESULT verdict | Clustering by tf+bar ignores dependence across timeframes and across time. 30m/1h/2h/3h/4h bars close at the same minutes and share one 1m path, yet they are pooled into one cell. 1d/1w colours are constant for every bar in their day or week, and the score window is about 675 days and 96 weeks. G2 aligned/US/inside shows Holm p(12) 0.000 on 10,025 bars, so its SE is understated. | Cluster by UTC day or use a week-block bootstrap, report effective days, rerun the counts, and don't publish the 16 until then.
2. major | RESULT "calibration by time left" vs cell test | The null is itself off: G2 t_left 0.0-0.2 delta +0.0274 (se 0.0016), G3 0.0-0.2 +0.0347 (se 0.0037). The cell shifts are fitted against that miscalibrated null, so "beats the null" partly measures the null's error. PRE_REG says to report this as a finding; RESULT lists it without saying so. | Add a context-free recalibrated baseline (t_left × |d| bins, fit 2024). Counted cells must beat that, and the verdict should state the miscalibration.
3. major | flip_table.py `at_band`; RESULT G1 table | Every at-band cell in G1 sits 3-5 pp under the null in every session (aligned/Asia -0.0386, aligned/US -0.0391, split/EU -0.0468). "At band" selects large |price − mean|, so it probably proxies |d|, not context. | Condition on |d| bins in the baseline and show whether at-band survives.
4. major | RESULT "Reading" paragraph | The sign claim contradicts the tables. "Below it in US" fails for G1 inside US (aligned +0.0025, split +0.0029) and G3 inside US (split +0.0288). "Above in Asia and EU with inside" fails for G1 aligned/EU/inside (-0.0074) and G1 split/Asia/inside (-0.0033). The ATR explanation is stated as matching a pattern that is not uniform. | Delete the sentence or restate it with sign-agreement counts.
5. major | flip_table.py `htf`; PRE_REG "Context" | PRE_REG says "no row-colour direction is used". That is false for 1d and 1w rows: cd = sign(price − day open) is the 1d row's own colour, and cw is the 1w row's own colour. So aligned/split for G3 1d (4,044 rows) and G4 1w (570 rows) encodes row colour against the other HTF. | Define those rows' HTF cell from the other timeframe only (or drop them), correct PRE_REG, and retest.
6. major | RESULT header; PRE_REG holdout clause | The score window 2025-01-01..2026-11-06 includes the sealed holdout (2025-07..). RESULT does not say no clean holdout remains for this family. | State it in RESULT; any shipped cell needs fresh data.
7. minor | flip_model.py `evaluate`, `delta_fit` | No minimum fit n and no shrinkage; n_fit is computed but not reported. Thin cells (G3 split/US/at has 45 rows) get raw shifts. | Shrink toward 0 or gate on n_fit; print n_fit.
8. minor | counts rule | No materiality floor. G1 aligned/Asia/at gains 0.00145 Brier and G1 overall gains -0.00010 (0.07%). The result is statistical, not economic. | State this in RESULT; add a floor if anything ships.
9. minor | RESULT "prior-close check: 47 of 48" | Not an independent check. On spot the two colours are near-identical by construction, so agreement says nothing. | Drop it as evidence.
10. minor | flip_table.py `main`, `m0` | The Bollinger centring constant is the mean over the full series, including the score window. It cancels exactly, so no numeric effect, but it reads as future information. | Centre on the fit-window mean and add a comment.
11. minor | RESULT regime line | The fit/score regime mismatch is measurable: the weekly tags exist, so delta can be split by bull vs range weeks within score. RESULT says the study "cannot separate" them. | Add the split.
12. minor | RESULT headline | Headline uses m = 12 per table; the honest family is m = 48 (or 96 with both colours). | Headline m = 48.

LEAKAGE: no. atr[b] = mean TR of bars b-14..b-1. Bollinger = 19 prior closes plus price. The m0 centring is full-sample but cancels exactly. HTF uses the containing day/week open at index ≤ g. The session uses the close minute (g+1)%1440. Fit bars close ≤ cut, score bars open ≥ cut, and straddlers are dropped per timeframe, so no fit outcome shares a bar or minute with a score outcome. Shared minutes across timeframes inside the score window are an inflation problem (finding 1), not leakage.

ANCHOR: correct. START_MS = 1704067200000 is 2024-01-01T00:00Z (a Monday). CUT_MS = 1735689600000 is 2025-01-01. START is a multiple of 1440 and 10080 minutes, so g // 1440 and g // 10080 return the containing day and week. offsets() gives j in [0, S-2] for every S, and t_left = 1 − (j+1)/S. The prior close bc[B-1] is complete. The one nit is tr[0] = H−L without a prior close, which is unused because bars under 20 are dropped. The real definitional error is finding 5.

INFLATION: multiplicity is not the main problem. m = 48 is printed and all 16 counted cells pass it. The problem is that the SEs feeding Holm ignore dependence (finding 1), so the Holm p-values are invalid at any m. The counts rule matches PRE_REG (Brier lowered, Holm p < 0.05, ≥ 30 bars), and I checked the 16 against the table.

VERDICT: Leakage and anchors pass, but the 16 counted cells rest on bar-level SEs and on a null whose time-left miscalibration and at-band |d| effect are the likely source of the shifts, so RESULT must not claim a context edge until it is rerun with day clustering and a recalibrated baseline.

```

## What was done with each finding

| # | Finding | Answer |
|---|---|---|
| 1 | blocker: bar clusters ignore dependence across timeframes and weeks | FIXED (A1): SE and p cluster by UTC week; also >= 30 weeks per cell. Result: the count did not collapse (16 counted at m = 12, 15 survive m = 48 against the null), so the shifts are large against the week-level noise; the first-run table is superseded |
| 2 | major: the null is miscalibrated, so cells partly measure its error | ACCEPTED (A5): a baseline recalibrated on abs(d) x t_left (fit 2024) is added; against it 9 cells count and 7 survive m = 48 (4 at-band cells: G1 split/Asia, G1 split/EU, G2 aligned/Asia, G2 aligned/US; 3 inside cells: G2 aligned/US, G2 split/Asia, G3 aligned/US). RESULT states the miscalibration in the verdict section and prints the calibration table |
| 3 | major: at band proxies abs(d) | ACCEPTED (A5): at-band cells remain negative against the baseline in G1 (split Asia, EU) and G2 (aligned Asia, US) but with smaller shifts (-0.02 to -0.03 vs -0.04); Brier gains stay below 0.5% |
| 4 | major: the "Reading" sign claim contradicts the tables | FIXED: sentence deleted; replaced by computed counts of counted cells by band position and sign (7 at-band negative, 8 inside positive, 1 inside negative); no mechanism is claimed |
| 5 | major: HTF cell for 1d/1w rows contains the row's own colour | FIXED (A2): htf = na for 1d and 1w rows, out of the 12 cells, kept in the per-timeframe table; PRE_REG sentence corrected by amendment; test `test_own_timeframe_has_no_htf_cell` |
| 6 | major: score window is inside the burned holdout, RESULT silent | FIXED (A8): the verdict says it |
| 7 | minor: no minimum fit n, n_fit not shown | FIXED (A3): shift needs >= 30 fit bars, `fit bars` column added |
| 8 | minor: no materiality floor | NOT ADOPTED after the fact (a floor chosen now would be fitted to the result); RESULT calls the gains statistical, not economic (0.07-0.57% of the null's Brier); if anything ships on these cells a floor is set before the fresh-data run |
| 9 | minor: prior-close agreement is not a check | FIXED (A4): dropped as evidence, stated in RESULT |
| 10 | minor: Bollinger centring uses the full-series mean | FIXED (A6): centred on the first close; cancels exactly, no number moves |
| 11 | minor: regime split can be measured | FIXED (A7): `regime_split.csv` and a RESULT table; delta vs null has the same sign in bull and range weeks in G1-G3 (G1 -0.004/-0.005, G3 +0.023/+0.020, G2 +0.007/+0.015), so the fit-bull / score-range mismatch alone does not produce it |
| 12 | minor: headline m should be 48 | FIXED (A4) |

Reviewer's own answers: LEAKAGE no, ANCHOR correct (the one definitional error was #5), INFLATION traced to the SEs (#1), not to m. The reviewer saw the frozen files only; it did not see the 1m data.
Limits of this review: one Haiku pass, no second model, no independent re-derivation of the Brier numbers; the null formula itself was checked by a simulated random walk (test_delta_zero_on_random_walk).
