# Independent levels fee-drag recomputation

## Method frozen before reading the comparison

Written before opening REVIEW_FABLE_2026-10-25.md or computing the real ledger aggregates. Use raw filled-trade rows only, not the study's summary or stored R outputs. One R is the filled entry-to-protective-stop distance, subject to confirmation against the frozen ledger contract. For side s (+1 long, -1 short), entry E, exit X, risk distance R: gross_R = s*(X-E)/R; fee_R = (fee_in*E + fee_out*X)/R; net_R = gross_R-fee_R. FORMULAS.md:468-470 specifies these price-based R and fee equations. FORMULAS.md:479-483 specifies arithmetic event means. Do not use the target/stop net R:R planning ratio at FORMULAS.md:400-406 as realised P/L.

The five requested outputs are filled count, mean gross_R, mean fee_R, mean net_R and filled-only win rate (net_R > 0; report target-hit rate separately if it differs). Confirm the study's frozen fee scenario and entry/risk conventions before calculating; label study-specific choices OURS. FORMULAS.md does not explicitly define this ladder's filled-only selection: cite its own ledger contract for that choice. Never treat unfilled ideas as zero-return trades. Do not run/import producer study code. Verify the independent calculator on three hand-computed trades before opening real rows; reject missing/nonpositive risk and unknown sides rather than silently dropping them. Only DEV rows may enter. Compare with the Fable review after the arithmetic is complete, preserving exact values and showing rounding gaps.

## Result and evidence limits

RESULT (2026-10-26 UTC / 2026-10-27 IST, JIS-NUC): **partial verification, not a five-number independent MATCH**. Filled count, mean stored net R and win rate match the displayed precision under the export's zero-return sentinel convention. Gross R and fee R cannot be independently reconstructed from the committed ledger. The card remains open behind a raw-ledger prerequisite. Trust: UNCHECKED; no cross-vendor receipt.

Sequence disclosure: the method above was written first, but the Fable comparison document was opened during input discovery before the real aggregates were calculated. This deviates from the requested compute-then-read order. The calculator used no review values as expected outputs; its three hand tests ran before the real ledger was opened by that calculator. This is independent arithmetic, not a blind review. A representative ledger row and the frozen summary had also been inspected during schema discovery.

Evidence aliases (all repository-relative):

- F = `MyTradingSys/backtest/layers/FORMULAS.md`.
- L = `MyTradingSys/research/levels_confluence_2026-10-14/ladder_ideas_dev.csv`.
- Z = the same folder's `frozen_rule.json`.
- D = the same folder's `ladder_dev.md`.
- B = `MyTradingSys/research/sim_desk/artifact/build_artifact.py`.
- V = `MyTradingSys/research/sim_desk/REVIEW_FABLE_2026-10-25.md`.

## Hand oracle before the real calculation

All numbers in this synthetic fixture are OURS. Each row has quantity 1. Entries, exits and risk distances are chosen by hand, not copied from producer outputs. Decimal arithmetic gives:

| Side | Entry | Exit | R distance | Entry/exit fee rates | Gross R | Fee R | Net R |
|---|---:|---:|---:|---|---:|---:|---:|
| Long | 100 | 102 | 2 | 0.0002 / 0.0002 | 1 | 0.0202 | 0.9798 |
| Short | 100 | 101 | 1 | 0.0002 / 0.0005 | -1 | 0.0705 | -1.0705 |
| Long | 100 | 100.5 | 2 | 0.0005 / 0.0005 | 0.25 | 0.050125 | 0.199875 |

All three passed exact Decimal assertions. A deliberately omitted exit fee on the first row was rejected by the same oracle. The first row, for example, has fee (0.0002*100 + 0.0002*102)/2 = 0.0202. This tests the fee equation rather than trusting net=gross-fee in a producer summary.

## Selection and actual inputs

Frozen arm: E1 S2 K5 X0_2R (Z:3-7). S2 enters only at L2; risk is the planned entry-to-stop price distance, not a fee-inclusive planning ratio (D:17-18; `ladder.py`:5-6,26,148). Maker fees on entries/targets and taker on stop/time exits are the study's sourced scenario (D:17); no slippage in that original run (V:22). The equations come from F:468-470; averaging from F:479-483. F:479 defines target-hit share, which differs from the net-positive win rate requested here and implemented by B:80. No exit-reason column exists here, so target-hit rate is not reconstructible.

The independent script used only Python csv, json, Decimal, pathlib and hashlib. It did not import or run study, desk, export or artifact functions. Producer code was read only to identify the export contract and the missing provenance.

L has 5,976 ideas. Select E1 == True and a finite S2_K5_X0_2R: 772 rows. Of those, 517 have net exactly 0.000 and 255 have nonzero net. B:40-55 documents the zero sentinel as never-filled. The independent filter follows that contract without calling B. This confirms **255 under the committed export convention**, not exchange-style fill proof: an actual filled trade rounded to zero would be indistinguishable in this CSV. Explicit filled_qty/NO_FILL is absent. All selected touch_t values satisfy 2022-04-01 <= timestamp < 2024-07-01; sides are valid +/-1. No stale event_table.csv was read (D:14 says that table contains VALIDATION-window data).

L SHA-256: `72f81b39bdeed7e867d83bcc1377921e39d1c4f7a6db303d74bd7d383e3afa4a`.

## Five-number comparison

| Quantity | Independent result / conditional reconstruction | Fable reference | Verdict and exact difference |
|---|---|---|---|
| Filled count | 255 nonzero-net selected rows; 517 zero sentinels | V:19: 255 filled, 517 unfilled | MATCH under sentinel convention; difference 0. Raw fills not independently proved. |
| Mean gross R | Not identifiable from L. Conditional summary rescale: +0.2174473159477667374117647059 | V:9: +0.22 R | NOT INDEPENDENTLY VERIFIED. Conditional value rounds to +0.22; difference from the printed value -0.0025526840522332625882352941 R. |
| Mean fee R | Not identifiable from L. Conditional summary rescale: +0.3368860406537607411764705882 | V:21: +0.337 R | NOT INDEPENDENTLY VERIFIED. Conditional value rounds to +0.337; difference -0.0001139593462392588235294118 R. Fee is a positive cost, deducted from gross. |
| Mean net R | Sum stored net -30.457 / 255 = -0.1194392156862745098039215686 | V:19: -0.1194 R | MATCH to 4 decimal places; difference -0.0000392156862745098039215686 R. This averages ledger net outputs, not independently replayed price P/L. |
| Net-positive win rate | 104 / 255 = 40.78431372549019607843137255% | V:19: 40.8% | MATCH to 1 decimal place; difference -0.01568627450980392156862745 percentage points. |

The display export `sim_desk/results/levels_ladder.json` contains all 255 rounded net trade outcomes. Independent timestamp ordering of L matches every exported r value, not just the aggregate. Its compact trade schema is d,s,f,l2,t1,t2,r; it contains no actual stop, exit fill, fee legs or gross P/L. This is parity on a shared source, not independent fee verification.

## Why the remaining two numbers are not reconstructible

B:72-76 explicitly scales Z's precomputed mean_gross_r and mean_fee_r by 772/255 = 3.027450980392156862745098039. Z:17-18 holds the gross/fee means over all ideas. Multiplying those stored means produces the conditional numbers above, but is not a raw-row audit. No additional gross/fee information is created by this rescaling.

L's header at line 1 has no stop, exit_price, R_price, gross_r, fees_r or explicit filled status. It stores the chosen arm's net R rounded to three decimals. The row fields L1/L2/T1/T2 are planned levels, not actual exit prices; K5's running day extreme is absent, so even R cannot be reconstructed from those levels. Many gross/fee pairs can give the same net; using the headline to choose one would be circular. The original simulation would have returned fills, exits, R_price, gross_r and fees_r (`ladder.py`:219-227), but those fields were not preserved in this tracked ledger. `git ls-files '*runs*' '*trades*' '*ledger*'` contains no sim_desk raw run ledger, only runs_view.py.

Conditional full-precision net from Z scaled by 772/255 is -0.1194387247059940340392156863, differing from the rounded-row mean by -0.0000004909802804757647058823 R. The maximum mean rounding error with three-decimal row rounding is 0.0005 R, so this discrepancy is compatible with rounding; it is not an economic gap. Under that bound, genuine win signs within 0.0005 R of zero and zero-sentinel membership cannot be independently established.

The original review's +0.22 - 0.337 is approximately -0.117 because its gross number is rounded to two decimals. Using the conditional unrounded figures gives -0.119438724705994..., consistent with the net headline. There is no demonstrated arithmetic contradiction, but the gross-versus-fee explanation remains dependent on Z.

## Completion dependency

Created prerequisite `astra-low-levels-fee-drag-recompute-need-export-the-original` through tasks.py need, lane SONNET. It requests the original zero-slippage DEV run, with explicit fill state, every entry/exit price and quantity, fee rate/reason, stop/R distance, timestamps, settings and source commit. Historical public DEV inputs only. Do not rerun today's changed defaults or fetch sealed bars to manufacture a match.

Once those rows are committed, the same three-trade-tested equations can independently calculate all five quantities and resolve the two unverified comparisons and the fill sentinel ambiguity. The current card is deliberately not marked done. No trading/layer disposition or production change is made by this audit.

Reproduction used the throwaway file `F:/MTS/astra_levels_recompute_audit.py` outside the repository; it is not a shipped dependency. Equivalent ledger calculation: parse L as Decimal, select finite E1 rows, exclude exact-zero sentinel, count rows and positive values, and divide sum(S2_K5_X0_2R) by that count. The fixture, selection rule, input hash and exact totals above are sufficient to reproduce the verified arithmetic without that local file.

## Raw-ledger recheck (2026-10-28 UTC)

The prerequisite `astra-low-levels-fee-drag-recompute-need-export-the-original` shipped the frozen DEV fill ledger. This addendum supersedes the preceding partial-verification conclusion for gross R, fee R, and explicit fill state; the earlier analysis is retained as history. I read the frozen formula and ledger schema, wrote and ran a separate Decimal calculator outside the repository, checked it against three handwritten trades, then calculated the raw-row aggregates. The earlier Fable review had already been read during the first audit, so this is an independent arithmetic recomputation, not a blind review.

For each `filled=Y` row, `gross_R = side * (exit - entry) / R_dist`. Since `qty=1` and the ledger stores the realized USD fee legs `fee_in` and `fee_out`, `fee_R = (fee_in + fee_out) / R_dist`; `net_R = gross_R - fee_R`. These are FORMULAS.md:468-470's price-based equations expressed using the ledger's already price-weighted fee legs. The aggregate is the arithmetic mean across filled rows (FORMULAS.md:479-483); win rate is the share whose recomputed net R is strictly positive. Unfilled rows are explicitly `filled=N`, `exit_reason=NO_FILL` and are excluded, never assigned a return. The frozen contract is DEV only, 2022-04-01 through (exclusive) 2024-07-01, zero slippage, E1/S2/K5/X0_2R; its source revision is `da096725e880974683bdd6cca6b086d64c61e7fd` (levels_raw_ledger/provenance.md:3-8).

The three hand-oracle rows passed exact Decimal assertions (long win, short loss, long timeout). The independent pass read the tracked raw ledger directly, not `reconcile.py`, study code, or exporter code. It checked 772 total rows, 255 explicit fills, 517 explicit no-fills, valid sides and positive risk, unit quantity, source revision, and agreement of each calculated gross/fee/net field with its ledger field to <1.21e-13 R (float serialization tolerance). Input Git blob SHA-256: `2f72374b31b7f78bb6a31f96fa8fa0e30643a4e0d147fa32f34a38a3e6503915`.

| Quantity | Recomputed from raw filled rows | Fable review (REVIEW_FABLE_2026-10-25.md) | Result |
|---|---:|---:|---|
| Filled count | 255 (517 explicitly unfilled) | 255 filled / 517 unfilled (section 1, line 19) | MATCH, exact count |
| Mean gross R | +0.2174473159477666988727880221 | +0.22 R (lines 9, 19) | MATCH at 2 decimals; raw minus displayed = -0.0025526840522333011272 R |
| Mean fee R per trade | +0.3368860406537607551948768035 | +0.337 R (line 21) | MATCH at 3 decimals; raw minus displayed = -0.0001139593462392448051 R |
| Mean net R | -0.1194387247059940563220887814 | -0.1194 R (line 19) | MATCH at 4 decimals; raw minus displayed = -0.0000387247059940563221 R |
| Net-positive win rate | 104 / 255 = 40.78431372549019607843137255% | 40.8% (line 19) | MATCH at 1 decimal; raw minus displayed = -0.0156862745098039215686 percentage points |

Mean gross minus mean fee equals mean net algebraically; the independently accumulated Decimal totals differ only by finite-precision division in the final decimal places. Exit reasons were 102 X0, 150 STOP, and 3 TIME. No target-hit rate was inferred. All five review headlines match at their stated precision. The caveat is upstream provenance: the committed ledger exporter replays frozen idea geometry against the historical one-minute klines; this audit independently calculates from the exported per-trade rows but does not independently regenerate those fills from raw candles. No VALIDATION/HOLDOUT data, live path, or layer disposition was used or changed.

Reproduction: `python F:/MTS/astra_levels_recompute_independent.py` (throwaway calculator outside the repository; three exact hand checks before ledger loading). Detailed evidence and commands: `MyTradingSys/research/layer_lab/reports/2026-10-28_astra-low-levels-fee-drag-recompute.md`.
