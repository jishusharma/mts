# BLOCKED — independent headline re-derivation incomplete

Counts from `counts_long.csv`: A 15m ALL range signal n=9,008; A 15m ALL tagged-control n=12,066; B 15m ALL level-range tagged n=1,717 (the latter is fills, per CSV columns). The first two are directly present as rows in the CSV; 12,066 is the sum of A tagged control rows, but no such control row is present in the CSV, so it cannot be verified here. The headline counts table below therefore records source rows, not inferred fee-net returns.

## Scope and method

Read `RESULT_LONG.md` lines 1–63, `counts_long.csv` and `FORMULAS.md` lines 554–558. I independently looked up the headline sample counts in CSV rows and checked the applicable formula text. I did not use `study_long.py` or any other calculation script.

`FORMULAS.md` section 22 defines Bollinger band construction only. It does not define the 0.14% fee used by this study or a fee-net return calculation for these trades. `counts_long.csv` columns are `study,tf,session,entry,gate,side,k,tag,width,days,fill_rate,fills,median_stop_pct,n,reentered,signals`; it contains no gross-return sum, individual returns, win/loss results, or net-return values. Thus n is checkable, but fee-net return is not derivable from these allowed sources. Result headline n=9,008 conflicts with CSV row n=9,008? Match. Aggregate control n=12,066 has no corresponding tagged-control CSV row. BLOCKED on required fee-net recomputation and that control count.

## Findings

| Severity | Headline / source line | Result | Independent evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | RESULT_LONG.md:13, A range signal n=9008 | MATCH | counts_long.csv:2 has A_r2r, 15m, ALL, signal, range, both, any; n=9008 | None |
| HIGH | RESULT_LONG.md:13, A range signal net -0.128% | NOT_IN_DATA | counts_long.csv:2 contains n and median_stop_pct only; no return/P&L input; FORMULAS.md:554–558 has no fee model | Provide per-trade gross return or sufficient exit/P&L aggregates and the study fee formula |
| HIGH | RESULT_LONG.md:13, A tagged control n=12066 | NOT_IN_DATA | No tagged-control row found in counts_long.csv (its A control-like total in RESULT_LONG is not broken out as a CSV row) | Add control count row or its underlying counts |
| HIGH | RESULT_LONG.md:13, A tagged control net -0.118% | NOT_IN_DATA | No control returns or fee-net data in CSV; FORMULAS.md:554–558 does not define this study's fee | Provide per-trade gross return and formula |
| HIGH | RESULT_LONG.md:13, bull n=3058 | NOT_IN_DATA | No bull regime row identified in counts_long.csv schema/data for this headline | Add matching regime count row |
| HIGH | RESULT_LONG.md:14, A long -0.105% | NOT_IN_DATA | CSV includes side rows but no gross/net returns; FORMULAS.md:554–558 has no fee model | Provide return inputs and study fee rule |
| HIGH | RESULT_LONG.md:14, A short -0.151% | NOT_IN_DATA | CSV includes side rows but no gross/net returns; FORMULAS.md:554–558 has no fee model | Provide return inputs and study fee rule |
| HIGH | RESULT_LONG.md:14, wide-band n=3580 | MATCH | counts_long.csv:3 A_r2r 15m ALL signal range both width wide has n=3580 | None |
| HIGH | RESULT_LONG.md:14, wide-band net -0.133% | NOT_IN_DATA | No returns in counts_long.csv; no applicable fee definition in FORMULAS.md:554–558 | Provide return inputs and study fee rule |
| HIGH | RESULT_LONG.md:14, narrow-band n=5428 | MATCH | counts_long.csv:4 A_r2r 15m ALL signal range both width narrow has n=5428 | None |
| HIGH | RESULT_LONG.md:14, narrow-band net -0.125% | NOT_IN_DATA | No returns in counts_long.csv; no applicable fee definition in FORMULAS.md:554–558 | Provide return inputs and study fee rule |
| HIGH | RESULT_LONG.md:14, A 1h range n=2226 / net -0.103% | NOT_IN_DATA | The CSV includes 15m row schemas; no 1h headline aggregate with returns, and no net inputs | Add 1h count and return data plus applicable fee formula |
| HIGH | RESULT_LONG.md:14, A 4h range n=548 / net -0.091% | NOT_IN_DATA | No 4h headline aggregate with return inputs in counts_long.csv | Add 4h count and return data plus applicable fee formula |
| HIGH | RESULT_LONG.md:17, B range tagged n=1717 (k=1.0) | MATCH | counts_long.csv contains B_retest 15m ALL level range both k=1.0 tagged row with fills/n values; n column is 1717 | None |
| HIGH | RESULT_LONG.md:17, B fee-net values | NOT_IN_DATA | CSV lacks returns; FORMULAS.md section 22 defines bands, not fees | Provide return inputs and study fee formula |

## Follow-up

No follow-up card created. The required independent fee-net computation is blocked until the source package includes return inputs and the correct study-specific fee rule. Card not marked done.
