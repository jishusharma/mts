# Independent Sol 6.1 review

Reviewer: Sol 6.1, delegated independent reviewer `/root/sol61_review`. Date: 2026-10-18. Two-pass review; Ultracode off; no subagents. Reviewed REPORT.md and CLAUDE_HANDOFF.md against source code at `cb00726407376fb50a3abf40bf2c1a432075038f` and independently opened primary references. No secrets, runtime data, sealed outcomes, commits or pushes were accessed or performed. Only this review file was written.

## Verdict

**ACCEPTED FOR RESEARCH/DOCUMENTATION HANDOFF after second pass, 2026-10-18.** All four required documentation corrections are reflected accurately in the revised REPORT.md and CLAUDE_HANDOFF.md. The central recommendation is sound and appropriately avoids a profitability claim. Acceptance covers the evidence review and proposed roadmap; it does not certify the simulator, fix existing code, establish strategy profitability or authorize trading. The first-pass findings are preserved below; final disposition follows at the end.

## First-pass required corrections (resolved in final documentation)

### R1 - Distinguish candidate dependence from serial return dependence

REPORT S3 correctly requests an effective trial-count treatment for correlated candidates. It does not explicitly explain that this addresses dependence *between candidate strategies*, not dependence *through time within a strategy's returns*. The S5 and general uncertainty controls are useful but do not establish that the existing DSR is calibrated for dependent returns.

Evidence: [DSR manuscript](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), July 31, 2014 version, equation 2 and appendix 3; `backtest/bt/bt_stats.py:46-67`. PSR uses sample length and marginal moments; there is no lag covariance or long-run variance input. Synthetic input consisting of 50 returns of -0.9 followed by 50 of +1.1 gives PSR 0.8401288127538633. Alternating the same values gives the identical PSR despite very different serial structure. This demonstrates absence of a temporal correction, not a measured false-positive rate.

Required edit: add the distinction to S3, the repository spot-check and P1b/handoff. Require validated treatment of temporal dependence, or label vanilla PSR/DSR an assumption-dependent diagnostic. Merely substituting an effective candidate count or asserting that data are regular-time does not solve temporal dependence. Do not prescribe an unvalidated effective-T shortcut as a fix.

### R2 - State AutoQuant's funding approximation explicitly

[AutoQuant v3](https://arxiv.org/html/2512.22476v3), sections 2.4 and 4.1, accrues funding on 4h bars using carried-forward 8h rates scaled by bar duration; missing observations can invoke a constant fallback. That is different from settlement-event cashflows. The paper calling a fallback conservative does not establish a lower PnL bound for positions of both signs.

Required edit: S9 and the handoff should state the prorated-accrual limitation explicitly and say that neither equivalence to event funding nor conservatism of the fallback was verified. The report's existing warning about fixed 8h intervals is valid but incomplete. Do not present this paper's funding implementation as an exchange-accurate reference model.

Independent contrast: [Binance funding FAQ](https://www.binance.com/en/support/faq/detail/360033525031), sections 1 and 3, specifies signed transfers, event eligibility and mark-price nominal value. It also discloses possible transaction-time deviation around settlement; exact timestamp equality is not the only execution uncertainty. Retain the report's explicit applicability/version caveat.

### R3 - Include the fee approximation in the cost-helper audit

`backtest/layers/positioning/trade_costs.py:64` subtracts a fixed `fee_rt`. As a return on entry notional, it does not recalculate the closing fee on changed exit notional for constant contract quantity. This is a separate approximation from the funding issue already identified, and its error can have either sign.

Independent arithmetic, OURS synthetic example: quantity 1, entry 100, exit 110, fee 0.0005 per leg. Actual total fee divided by entry notional is `(100*0.0005 + 110*0.0005)/100 = 0.00105`; the helper's 0.001 subtraction gives net 0.099 instead of 0.09895 before other costs. This is an accounting demonstration, not a verified historical fee schedule.

Required edit: name this approximation in REPORT section 5 and handoff, and add unequal entry/exit prices to P0c's independent fee examples. Existing worked funding examples remain arithmetically correct under their stated simplification; do not relabel them a funding-sign bug.

### R4 - Do not rely on the current power helper without checking the rejection rule

The report correctly replaces universal N<100 language with effect-aware power. Its cited readiness item 0e points to `backtest/power_mde.py`, whose declared positive-edge decision and returned power disagree. Lines 3-5 say the lower two-sided 95% CI must exceed zero. Lines 41-43 add both tails, computing rejection in either direction.

Small synthetic check only: `power_mde(0.25, 1.0, 0.0, 100)` returns mean -0.5 and power 0.9999315044708436. Under its own normal approximation, positive-edge rejection has probability `Phi(-0.5*sqrt(100)/sqrt(0.75)-Phi_inverse(0.975))`, approximately 5.23e-15. High ability to detect a negative mean is not high power to pass a positive-edge gate. Its `trades_for_80_power` does correctly return infinity in this example.

Required edit: flag this observed mismatch in the spot-check/handoff and require power to match the declared decision rule in P1b. Preserve the existing card's scope rather than silently changing frozen outcomes. No broad audit of this helper or its callers was performed.

## Checks that passed

- **PBO is not probability of monetary loss.** The [February 27, 2015 PBO manuscript](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), definitions 2.1-2.2 and algorithm 2.3, uses the selected candidate's relative OOS rank. Probability of loss is a separate diagnostic. REPORT S2 correctly distinguishes them and correctly warns CSCV is not strictly forward evaluation. Code inspection confirms truncation, first-index IS tie selection and strict-less OOS ranking. A synthetic 8x2 all-zero matrix with S=4 returns PBO=1.0; this supports the report's request to define ties, not a universal numerical bug finding.
- **N=100 is not a power theorem.** Independent known-variance normal calculations under the declared positive-lower-CI rule give only 0.03145 probability of a positive rejection for N=100 and mean/SD=0.01; N=25 and mean/SD=1 gives 0.99882. These are illustrative assumptions, not recommended sample requirements. They support replacing the template shorthand with an explicit useful effect, dependence model and rejection rule.
- **Fixed-bracket lower bound is unsupported.** `PRE_REG_TEMPLATE.md:54` asserts the bound without a pathwise dominance condition. A manager exiting a profitable position early can earn less than a bracket on a continuing trend; a manager exiting a subsequently losing position early can earn more. Neither policy universally dominates. REPORT's proposed wording is correct.
- **Funding sign and basis diagnosis are correct.** The helper sums signed rates on `(entry, exit]`, returns zero for its explicit no-funding case and checks outer coverage endpoints. In an OURS synthetic long example, entry 100 and event mark 110 with funding 0.001 means 0.0011 cost per entry notional; the helper gives 0.001. Its span check cannot certify that internal events are complete. REPORT already requests coverage certification and approximation-error measurement.
- **Hudson/Urquhart is accurately limited.** The [institutional abstract](https://research.birmingham.ac.uk/en/publications/technical-trading-and-cryptocurrencies/) confirms two Bitcoin markets, three other cryptocurrencies, almost 15,000 rules and no Bitcoin OOS predictability in that study. REPORT does not invent sample dates or transfer results to Binance perpetuals.
- **AutoQuant identification and restricted PBO claim match.** Independently checked title/author, arXiv v3 dated August 7, 2026, section 4 sample windows and section 7 top-40 PBO=0.586. Journal publication was not established. Its positive and negative performance comparisons were not independently replicated.
- **Official interfaces match the selected claims.** [Public-data README](https://github.com/binance/binance-public-data) confirms the 2025 spot microsecond boundary and checksum/correction facilities. [USD-M market-data documentation](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data) confirms funding time/rate/associated mark and interval-adjustment fields. Neither establishes historical schedule completeness.
- **Lo references support the limited claims.** The [author publication page](https://alo.mit.edu/publications/page/18/) supplies the 2002 Sharpe and limit-execution abstracts; it supports dependence and hypothetical-fill caveats, not current Binance fill calibration.
- **BIS author correction checked.** [Crypto carry](https://www.bis.org/publications/working-paper-1087-crypto-carry) identifies Maik Schmeling, Andreas Schrimpf and Karamfil Todorov. The parent corrected the initial Martin/Maik error during this review; retain Maik in the final report.
- **Repository distinctions match.** Read `bt_stats.py`, `ref_pbo.py`, FORMULAS sections 10/13, PRE_REG_TEMPLATE.md, trade_costs.py, fees.py and verdict.py. Statistics exist; a snapshot setup verdict is not an end-to-end promotion gate. Central fee-profile existence does not prove historical eligibility or caller consistency. CLAUDE_HANDOFF's separation of proposed follow-ups from frozen existing verdicts is appropriate; queue state itself was not independently re-audited.

## Remaining limits and second-pass status

This was an adversarial evidence/method spot-check, not exhaustive source replication, a profitability backtest or code certification. S4, S7, S8 and V1 were not independently reopened in this batch. The S1 Wiley URL returned an access/internal error to this reviewer, so its full-text claim was not independently reconfirmed. No conclusion is drawn that the parent's earlier access failed. Access labels and primary URL provenance remain useful limits.

No historical fee, funding-eligibility, liquidation, capacity or data-vintage reconstruction was performed. Synthetic checks above ran with `python -B` on public source functions and invented values only. No runtime processes were operated and no holdout outcomes were consumed. At first-pass close, acceptance awaited confirmation of R1-R4; the completed second-pass disposition below supersedes that pending status. Implementation completion is not required for this documentation handoff.

## Final second-pass disposition - 2026-10-18

Read the revised handoff in full and checked each revised report source row, repository finding and roadmap criterion against R1-R4 and the first-pass evidence. No additional implementation, market-data run or external publication-status inference was needed.

| Finding | Final documentation check | Disposition |
|---|---|---|
| R1 DSR dependence | REPORT S3 and section 5 explicitly distinguish effective candidate count from serial dependence; S3 requires validated temporal treatment or an assumption-dependent label. P1b covers dependence-aware inference and clustered returns. Handoff item 9 carries the implementation limitation. | Resolved for this handoff; calibration work remains. |
| R2 AutoQuant funding | S9 explicitly identifies 4h accrual from carried-forward 8h rates, distinguishes settlement-event accounting and withholds both equivalence and signed-fallback conservatism. Handoff item 9 repeats the limit. | Resolved; no exchange-accurate funding endorsement. |
| R3 Fee approximation | Section 5 names fixed fee_rt and the exit/entry price dependence; P0c explicitly requires unequal entry/exit fee examples. Handoff item 9 requests the corresponding audit. | Resolved; helper remains an approximation. |
| R4 Power rejection rule | Section 5 flags the documented positive-edge versus two-tail mismatch; P1b requires an independently checked correction. Handoff item 8 preserves the display-only card's exclusions and routes a separate correction. Its null example, 0.05 versus 0.025, is consistent with the first-pass independently derived positive-rejection formula. | Resolved for documentation; no assertion that the helper was repaired. |

The revised texts preserve the valid PBO/loss distinction, effect/dependence-aware power requirement, fixed-bracket objection, funding sign and scope limitations. Maik Schmeling remains correctly named. No remaining blocking research/handoff correction was found in this pass.

Remaining limits are unchanged: targeted source spot-checks and synthetic arithmetic are not empirical replication; source-access restrictions above remain; queue enforcement and all historical market/execution reconstructions remain unverified. The proposed safeguards still need implementation and validation before any future strategy evidence can rely on them.
