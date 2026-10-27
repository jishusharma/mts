FIX-FIRST

# Independent section 10 audit

Performed 2026-10-28 IST (2026-10-27 20:55 UTC). The filename is the card's requested delivery name, not the execution date.
Card: `gpt-formulas-rederive-10`. Audit only; no product code or specification edits.

## Blindness and evidence

- Refreshed `origin/fast-track`, base `d2632c605`; card READY and not claimed; claimed with `sync.py claim` in own worktree `F:/MTS/mts-jis-nuc-codex-gpt-formulas-rederive-10`.
- Read `FORMULAS.md:179-203` before derivation. Independent oracle and full expected JSON committed in **622a400eb**, before reading either implementation. Neither implementation test file's source or expected numbers was read, at any stage. Later pytest execution emitted only pass counts.
- Frozen script: `../gpt_formulas_rederive_10_independent.py.txt`; stdlib only, rational central moments, no implementation imports. Frozen outputs: `../gpt_formulas_rederive_10_frozen.json`.
- SHA256 of oracle bytes: `dc54bfbe2b0bc93e8fc824e8c643d76c81ab78a91a826ad00a47a81070d7b9ec`; frozen JSON: `f6a5d4f7895c8e47941052610e5131a1d85436a3c3d21a25561ae5975531a988`. Git may normalize line endings; these are the LF working-file hashes at freezing.
- Read all of `backtest/bt/bt_stats.py:1-99` and `backtest/bt/ref_pbo.py:1-108` only after freeze. Section 10 functions evaluated; Wilson/bootstrap/noise experiment functions outside this task were not audited.
- Source hashes in comparison JSON: bt_stats `6694b9b9b1cd24cd5969f5edc300374b4f8ab260cbd34a013397af5ba8ba8832`; ref_pbo `98bf955fda36677e78221f8ed4cabb27c3f41f824ceebc6117ab3f5f8b8db0ef`.

## Inputs and derivation

All fixtures and choices below are **OURS**, synthetic, dimensionless excess returns; no trader parameters, market data, tuning, BTC encoding, VALIDATION or HOLDOUT reads. Five trials here means five supplied synthetic Sharpe estimates, not five historical backtests or evidence that trials are independent. The null model assumes independent trials as required by the specification.

Ten returns: `[-.03,-.01,0,.01,.02,.04,-.02,.03,.01,.05]`.
Population mean = `1/100`; central moments m2 = `3/5000`, m3 = `0`, m4 = `177/250000000`.
Thus population SD = `sqrt(.0006)`, SR = `.01/sqrt(.0006)`, skew = `0`, raw kurtosis (not excess) = `59/30`.

**SOURCED** PSR equation: FORMULAS.md:187-192; [Bailey/Lopez de Prado, Sharpe Ratio Efficient Frontier (2012), section 3](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf).
With SR* = 0, denominator squared = `1+(59/30-1)*SR^2/4 = 749/720`;
z = `(SR-0)*sqrt(9)/sqrt(749/720) = 1.2008008008899274`; Phi(z) = `0.8850857594344322`.

Five trial SR estimates: `[-.4,-.1,.2,.5,.8]`. **OURS** population variance convention for these supplied values: mean `.2`, variance `9/50=.18`. The API receives this variance directly; it does not estimate trial variance. The observed trial mean is not added to the benchmark: expected_max_sr is the centered null threshold.

**SOURCED** expected-maximum approximation: [Bailey/Lopez de Prado, Deflated Sharpe Ratio (2014), equations 1 and 3; Appendix 2](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
Use `sqrt(.18)*[(1-gamma)*Phi^-1(.8)+gamma*Phi^-1(1-1/(5e))]` with gamma = `0.5772156649015329`.
This gives SR* = `0.5059747831919722`; substituting into PSR gives z = `-0.2874477455931064`, DSR = `0.3868847536250857`. It is the specified approximation, not an exact finite-five-trial Gaussian maximum expectation. No annualization or sample-SD substitution.

The frozen 4 x 8 matrix has **variant rows and time columns** (OURS orientation). API input is its explicit transpose, 8 time rows x 4 variants; neither API is assumed to take variant rows.

```text
 A:  3  2 -2 -1  1  4 -3  0
 B: -1  2  4  3 -2  0  1 -3
 C:  1 -2  0  3  4 -1  2  1
 D:  0  1  2 -3  3  2 -1  4
```

**SOURCED** CSCV: FORMULAS.md:194-203; [Bailey et al., Probability of Backtest Overfitting (2015), section 2.2](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).
**OURS** S=4 blocks `(t0,t1),(t2,t3),(t4,t5),(t6,t7)`, all C(4,2)=6 splits, population Sharpe in each half. Integer magnitudes may be scaled uniformly by .01 without changing ranks or PBO. For every split: choose max IS Sharpe, count strictly smaller OOS Sharpes, add one, divide by N+1=5, take logit and count logit <= 0.

| IS blocks (zero based) | IS winner | OOS rank | w | logit | Overfit |
|---|---|---|---|---|---|
| 0,1 | B | 1 | .2 | -1.3862943611198906 | yes |
| 0,2 | A | 1 | .2 | -1.3862943611198906 | yes |
| 0,3 | D | 2 | .4 | -.4054651081081643 | yes |
| 1,2 | C | 3 | .6 | .4054651081081642 | no |
| 1,3 | C | 2 | .4 | -.4054651081081643 | yes |
| 2,3 | D | 1 | .2 | -1.3862943611198906 | yes |

PBO = `5/6 = .8333333333333334`. All IS and OOS Sharpe vectors are preserved in frozen JSON, independently computed before implementation read.

## Numerical comparison

| Metric | Independent | Implementation | Absolute difference |
|---|---|---|---|
| Population SR, both modules | .4082482904638631 | .4082482904638630 | 5.55e-17 |
| PSR, bt_stats | .8850857594344322 | .8850857594344322 | 0 |
| Expected max SR, bt_stats | .5059747831919722 | .5059747831915767 | 3.9546144137148076e-13 |
| DSR, bt_stats | .3868847536250857 | .3868847536255309 | 4.4519943287468777e-13 |
| PBO, both modules | .8333333333333334 | .8333333333333334 | 0 |
| Six logits, both modules | frozen split table | identical | 0 |
| Six relative ranks, ref_pbo | .2,.2,.4,.6,.4,.2 | identical | 0 |

MATCH: max absolute numerical difference **4.4519943287468777e-13**; tiny expected-max/DSR discrepancy comes from implementation gamma rounded to `0.5772156649` at bt_stats.py:60. ref_pbo supplies Sharpe/PBO only, no PSR/DSR APIs.

## Findings

| Severity | Status | File:line | Finding and evidence | Proposed fix |
|---|---|---|---|---|
| MED | MISMATCH | ref_pbo.py:25-38,63-64; bt_stats.py:72-73 | ref accepts T=2,S=4, drops every row, evaluates six empty splits, reports PBO=1 with w=.2; bt_stats correctly rejects. Cannot form specified equal nonempty blocks. | Validate even integer S>=2, T>=S, nonempty rectangular finite matrix before forming blocks; add independent invalid-input tests. |
| MED | MISMATCH | bt_stats.py:32-44,46-55; ref_pbo.py:6-12 | Undefined zero-volatility ratios get finite probabilities: `[1]*10`, `[-1]*10`, `[0]*10` all SR=0, PSR=.5, DSR=.06451673538814016 at five trials/variance .18. Singleton returns PSR=DSR=.5. Section 10's mean/SD equation is undefined here; no sentinel contract is documented. | Define and document unavailable/error semantics for zero variance and insufficient samples, then apply consistently to PSR/DSR and CSCV; do not present sentinel probabilities as calculated evidence. |
| LOW | MISMATCH | bt_stats.py:26-28; ref_pbo.py:8-9 | Empty Sharpe input raises ValueError in bt_stats but returns 0 in reference. Both undocumented by section 10. | Use consistent invalid/empty-input contract. |
| LOW | MISMATCH | bt_stats.py:74-78; ref_pbo.py:31-38; FORMULAS.md:197-198 | Both silently truncate nondivisible T: appending `[100,-100,50,-50]` to eight rows leaves all six logits and PBO unchanged at S=4. Spec describes equal blocks but never states row loss. | Reject nondivisible T or document and report how many rows were dropped. |
| LOW | MATCH | bt_stats.py:91-97; ref_pbo.py:67-82 | Identical nonconstant variant series all have w=.2, so both PBO=1. This follows the spec's strict-less rank, rather than proving predictive deterioration. IS ties choose first variant. | Document tie bias and interpretation; any midrank policy requires a separate spec decision. |

No HIGH findings. Follow-up created: `stats-cscv-degenerate-input-contract` (SONNET, raw, scoped to these boundaries). No fixes attempted in this audit.

Other edge checks: zero trial variance at five trials -> max SR=0 (MATCH); negative variance rejected (MATCH); zero/one trial rejected (outside the approximation's domain, no spec-supported one-trial formula); S=0 yields reference ZeroDivisionError versus bt ValueError; odd S rejected by both; no variants raises ValueError; ragged rows raise IndexError. Full outcomes in comparison JSON. These are input-contract issues, not mismatches in the valid-data formula.

The primary return fixture has zero skew. A clearly **post-freeze supplemental** nonzero-skew fixture changes only its last return .05 to .09: independently computed PSR `.9356016162579048`, exact implementation match. Positive scaling by seven preserves SR and PSR; PSR benchmark equal to observed SR gives .5.

## Reproduction and checks

```text
python MyTradingSys/research/layer_lab/gpt_formulas_rederive_10_independent.py.txt
python MyTradingSys/research/layer_lab/gpt_formulas_rederive_10_compare.py.txt
python -m pytest MyTradingSys/backtest/bt/test_bt_stats.py MyTradingSys/backtest/bt/test_ref_pbo.py -q --tb=no
```

Comparison asserts complete frozen-output equality and max diff < 1e-12; writes `../gpt_formulas_rederive_10_comparison.json` (29 numerical comparisons). Existing tests: **13 passed in 9.20s**. Tests were run after freezing; test code/expected numbers were never opened. An initial comparison harness path error was corrected before these results; the frozen oracle and expected values were untouched.

PRE_REG_TEMPLATE.md read: items 0a-f and 1-12 are N/A to this deterministic synthetic arithmetic audit, except item 11's separation discipline: no historical data or holdout accessed. Five trial estimates and CSCV six splits are explicit fixtures, not new strategy trials. No strategy/backtest was selected, run or tuned; TRIALS.md unchanged.

Verdict: valid-input section 10 arithmetic is SOUND to floating precision; overall **FIX-FIRST** for misleading finite output on invalid/degenerate data. A passing test suite does not resolve the documented boundary findings. This report is an independent audit receipt, not a claim of a higher lab trust tag or completed external review.
