# GPT T06 break-even recount (2026-10-27)

FIX-FIRST

## Checked

- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T06_cost_fill_realism.md`: section 7, lines 104–121; did not inspect section 1 or the findings table.
- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/breakeven.csv`: all 13 data rows; independently compared the measured rows and the break-even arithmetic.
- `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/costs.csv`: all 204 data rows; grouped rows by file, `kind`, and `imports_fees`.
- `scripts/T06/t06_tables.py` and `scripts/T06/t06_scan.py`: checked generation, classification and scan scope. Did not execute the scanner because it shells out to `git ls-files`; the sandbox instruction prohibits git commands.
- `MyTradingSys/backtest/fees.py:22–28`: Deribit and Binance fee constants cited by the audit.
- No backtest was run and no market data was read. PRE_REG_TEMPLATE's 12 run prerequisites therefore do not apply to this CSV recount.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `T06_cost_fill_realism.md:113–115`; `scripts/T06/breakeven.csv:8,10` | AD is called “best measured,” but H2 has the higher measured gross mean. | Both CSV rows say `measured, real funding`; AD: n=282, gross_pct=0.03591 = 3.591 bp; H2: n=104, gross_pct=0.03801 = 3.801 bp. H2 is higher by 0.210 bp. “Best” across these measured rows is H2; AD is the best measured row in the MTF study only. | Relabel AD as “best MTF” and identify H2 as “best measured overall” (or state the comparison scope explicitly). |
| MED | `scripts/T06/costs.csv:1–204`; `scripts/T06/t06_tables.py:83–87`; `scripts/T06/t06_scan.py:1–8` | The inventory CSV does not support the quoted 201 rows / 164 assignments / 70 files / 57 own-cost / 13 imports tally, and its per-file import flag is internally inconsistent. | Direct CSV recount: 204 rows = 166 `assign` + 38 `literal_in_text`, across 76 unique files. Grouping by file and flag gives 61 files with only `0`, 14 with only `1`, and 1 with both values. The mixed file is `MyTradingSys/research/sim_desk/studies/_bars.py`: CSV rows 194–195 flag `1`, while rows 203–204 flag `0`; source line 16 imports `BINANCE_MAKER` and `BINANCE_TAKER` from `MyTradingSys.backtest.fees`. This makes file-level tallies ambiguous and conflicts with the generator's single cached per-file import classification (`t06_tables.py:45–53`). | Regenerate `costs.csv` from one stable tracked-file snapshot, then recount unique files with one import flag per file; inspect why the existing artifact contains contradictory flags for `_bars.py`. |

The break-even values themselves are arithmetically consistent with gross mean × 100: AD 3.59 bp and H2 3.80 bp. Their displayed regime headrooms also follow the documented formula `(gross_bp − fee_bp) / 2` (for example H2 all-maker: (3.801−0)/2 = 1.9005 bp/fill, displayed 1.9). The source fee constants match `fees.py:23–28`. The quoted cost-inventory counts are not reproducible from the current CSV without resolving its flag conflict; no replacement whole-repository count is claimed here.

## Follow-up cards

None. No HIGH findings.

## Verdict

FIX-FIRST
