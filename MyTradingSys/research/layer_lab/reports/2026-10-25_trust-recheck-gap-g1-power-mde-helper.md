# Trust re-check: gap-g1-power-mde-helper

Reviewer: OpenAI / GPT-6 (Codex; serving snapshot not exposed to this session). Independent check used the written G1 specification and section 9 formula only for the calculations; the producer implementation was read afterward only to perform the requested test mutation.

## Independent numbers

The written inputs are the two-point payoff `+RR` with probability `p`, `-1` otherwise, fixed cost `c`, and a two-sided 95% lower-bound test. Thus `mean = p*RR - (1-p) - c`, `sd = sqrt(p*(1-p))*(RR+1)`, and `N80 = ((1.96 + 0.8416)*sd/mean)^2`.

| G1 table value | Independent calculation | Result |
|---|---:|---|
| REPORT.md:94, `p=.45, RR=1.5, c=.012`: 80%-power N about 951 | mean 0.113; sd 1.243734296383; N80 950.836857943, rounds to 951 | MATCH |
| REPORT.md:99, `p=.45, RR=2.5, c=.062`: 80%-power N about 90 | mean 0.513; sd 1.741228014937; N80 90.424108632, rounds to 90 | MATCH |

Both align with the G1 table using the table's nearest-integer rounding. Formula source: REPORT.md:211-213. No market data or holdout was read.

## Test and mutation check

Command: `python -m pytest MyTradingSys/tests/test_power_mde.py -q` -> **7 passed** (one pytest cache warning about an already-existing cache path).

Test review: `MyTradingSys/tests/test_power_mde.py:5-36` checks all six G1 table rows at n=100/150/300 and the two anchor rows. The tolerances are appropriately tighter for the high-power anchor and wide enough for the table's whole-percent rounding. It would detect a material threshold/power error.

Fail-first probe: copied the implementation and test to a temporary scratch directory, changed only `_Z_975` from the 97.5th to 98.5th normal quantile in the scratch implementation, and ran the copied tests against it. Result: **7 failed**, including every parameterized G1 row and the anchor test. The scratch directory was removed; the real implementation and test file were unchanged.

## Finding and proposal

No numerical mismatch found. The test suite bites on the one-line threshold mutation. Proposed result trust tag: **VERIFIED-C2**, based on this independent re-derivation and test sensitivity check. The trust tag is a proposal for the runner's receipt workflow; this report does not modify a trust receipt.
