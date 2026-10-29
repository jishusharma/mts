# GPT preregistration gate boundary tests

Producer: GPT-6 Luna. The gate implementation `scripts/dev/prereg_gate.py` is unchanged. All expected z, MDE, and finite-sample values below were calculated independently from its printed docstring formula with `statistics.NormalDist`; tests do not import or call `prereg_gate` functions.

## Independent expected values

The spec in `prereg_gate.py:1-10` states `z_holm = Phi^-1(1 - 0.05/(2m))`, `MDE = (z_holm + 0.84) * sd / sqrt(n)`, and gross limit 0.30 R.

| Quantity | Inputs | Independent expected value | Test observation |
|---|---|---:|---|
| z_holm | m=1 | 1.959963985 (1.960) | Output rounded to 1.960 |
| z_holm | m=5 | 2.575829304 (2.576) | Output rounded to 2.576 |
| z_holm | m=9 | 2.772921295 (2.773) | Output rounded to 2.773 |
| MDE | n=100, sd=1.2, m=1 | 0.335995678 R (0.336) | BLOCK; output 0.336 R |
| MDE | n=1000, sd=2, m=5 | 0.216036014 R (0.216) | PASS; output 0.216 R |
| MDE | n=5000, sd=3, m=9 | 0.153283269 R (0.153) | PASS; output 0.153 R |
| Exact gross boundary | n=100, sd=1.05, m=1; cost=0.006003781623 | MDE 0.293996218377 R; total 0.300000000000 R | Exit 0, PASS |
| Just above boundary | Same, cost + 0.000001 | Total 0.300001 R | Exit 1, BLOCK |
| Finite n needed | sd=1.2, m=5, cost=0.05, max=0.30 | 268.828181706 (prints 269) | Output `n needed 269` |
| sd boundary | sd=1, no `--sd-source` | Input error | Exit 2 |
| sd just above boundary | n=10000, sd=1.0001, m=1, cost=0 | MDE 0.028002440 R | Accepted; exit 0 |
| Cost at/above gross limit | cost=0.30 and 0.31, max=0.30 | n needed = infinity | Both print `n needed inf`; exit 1 |

The 11 new methods cover those values, plus all three independent z values and the exact/just-above exit boundaries. The original five tests remain in place.

## Verification

`python scripts/dev/test_prereg_gate.py -v` on the real script: **16 tests passed** (5 existing + 11 new).

Fail-first mutation checks used temporary copies of `prereg_gate.py`, `verdicts.py`, and the test file. The repository implementation was not edited:

| Scratch mutation | Test command result | New test that failed |
|---|---|---|
| `POWER_Z = 0.84` → `0.80` | Failed as intended | Exact boundary, just-above boundary, all 3 MDE points, finite-n need |
| `<= a.max_gross` → `< a.max_gross` | Failed as intended | `test_exact_gross_limit_passes` |
| `a.sd <= 1` → `a.sd < 1` | Failed as intended | `test_sd_one_requires_source_but_just_above_one_is_valid` |

**Mutation score: 3/3 flips rejected by at least one new test.** `git diff -- scripts/dev/prereg_gate.py` is empty; only `scripts/dev/test_prereg_gate.py` changed for this card.

## Independent review

The card requires a Claude or Gemini reviewer because GPT produced this work. Review is pending; this report does not claim reviewer approval.
