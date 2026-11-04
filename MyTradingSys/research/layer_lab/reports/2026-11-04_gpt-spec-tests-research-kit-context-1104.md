# GPT spec tests: research kit context harness

**BUILD: added `MyTradingSys/tests/test_research_kit_context.py`; 34 passed.**

## What was checked

- Read `MyTradingSys/backtest/research_kit.py` (context harness: lines 197–307) and confirmed the requested test file did not exist in this checkout before this change.
- Added independent boundary/spec tests for RSI regime thresholds and agreement, as-of daily/weekly/monthly state, regime combination, phase mapping, UTC session cutoffs, regime-mix counts, and retest-entry behavior.
- Command: `python -m pytest MyTradingSys/tests/test_research_kit_context.py -q` — **34 passed** (one pytest cache warning on Windows; no test failures).
- No market data read; all fixtures are synthetic.

## Findings

| Severity | File:line | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/tests/test_research_kit_context.py:46` | As-of specification protects against future RSI state leaking into an earlier query. | Synthetic RSI timestamp 31 changes the band only at query time 31; time 30 remains bull. | None. |
| LOW | `MyTradingSys/tests/test_research_kit_context.py:92` | Retest tests reject signal-bar fills and lookahead beyond the configured window, and verify first-touch and gap fill prices on both sides. | Cases cover `i+1..i+n`, `n=0`, and a bars fixture that raises if read after its first fill. | None. |
| LOW | `MyTradingSys/backtest/research_kit.py:215` | Regime classification uses inclusive 60/40 levels and requires weekly/monthly agreement. | Boundary tests verify exact thresholds and mixed inputs. | None. |
| LOW | `MyTradingSys/backtest/research_kit.py:270` | Session tags honor UTC hour cutoffs at 08, 13, and 21 and roll over at midnight. | Boundary tests cover both sides of each cutoff and 23:59:59/24:00:00. | None. |

## Follow-up cards

None.
