FIX-FIRST

Stage 1 evidence map: both acceptance criteria PASS. The claim sheet contains a seeded numerical error and an unsupported fee-net assertion; these findings do not fail the criterion requiring their detection.

Checked: `MyTradingSys/research/layer_lab/examples/pilot-facts.md:1-5` (original source, read first), then `MyTradingSys/research/layer_lab/examples/pilot-claims.md:1-8`. The task card `MyTradingSys/system/tasks/recipe-pilot-1-map.json` has `flow.stage = 1` and `depends_on = []`: there is no predecessor report to read. Evidence covers only the three synthetic development observations; the source explicitly excludes trading-trial and performance interpretations (`pilot-facts.md:5`).

C1: PASS

Independently calculated from the observations at `MyTradingSys/research/layer_lab/examples/pilot-facts.md:3`: 10 + 11 + 9 = 30; count = 3; arithmetic mean = 30 / 3 = 10. Claim A states 31 (`pilot-claims.md:3`), so it is MISMATCH, overstated by 1. Claim B states 10 (`pilot-claims.md:4`), so it is MATCH. The computation uses the observation list, not the supplied totals or expected-audit labels.

Reproduction command, executed successfully from the repository root:

```powershell
python -c "from pathlib import Path; from fractions import Fraction; import re; p=Path('MyTradingSys/research/layer_lab/examples/pilot-facts.md'); line=p.read_text(encoding='utf-8').splitlines()[2]; raw=line.split('observations: ',1)[1].split('.',1)[0]; x=[int(v.strip()) for v in raw.split(',')]; print('source='+p.as_posix()+':3'); print('observations='+str(x)); print('n='+str(len(x))); print('sum='+str(sum(x))); print('mean='+str(Fraction(sum(x),len(x))))"
```

Output:

```text
source=MyTradingSys/research/layer_lab/examples/pilot-facts.md:3
observations=[10, 11, 9]
n=3
sum=30
mean=10
```

C2: PASS

Claim C, positive net return after fees (`MyTradingSys/research/layer_lab/examples/pilot-claims.md:5`), is NOT_IN_DATA. The original source explicitly states that fee data was not supplied (`pilot-facts.md:4`). No fee amount/rate or return interpretation is supplied for these observations (`pilot-facts.md:1-5`). Missing fees are not assumed to be zero; no net value, net sign, profitability or trading inference is asserted.

Assumptions: the arithmetic mean gives equal weight to the complete three-observation list at `pilot-facts.md:3`; no additional observations, weights, return units or fees are inferred. These are synthetic source values, not trader parameters.

| Severity | Claim / file:line | Classification and evidence | Proposed fix |
|---|---|---|---|
| MED | A / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:3` | MISMATCH: claimed sum 31; independently computed 30 from `pilot-facts.md:3`, command above. | In any corrected downstream account, state 30. Preserve the seeded fixture. |
| LOW | B / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:4` | MATCH: claimed mean 10; independently computed 30 / 3 = 10, command above. | None. |
| MED | C / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:5` | NOT_IN_DATA: fees explicitly absent at `pilot-facts.md:4`; the source disclaims performance use at line 5. | Keep net-after-fees unknown; require actual fee inputs and a defined return basis before evaluating it. Preserve the fixture. |

Follow-up cards created: none. The existing recipe's independent challenge stage is the next review; no claim that this later review has occurred is made here.

Closure command: `python scripts/dev/lab_flow.py finish recipe-pilot-1-map --report MyTradingSys/research/layer_lab/reports/2026-10-16_recipe-pilot-1-map.md --verdict PASS --result "C1 PASS: source sum 30, mean 10; A MISMATCH, B MATCH. C2 PASS: C NOT_IN_DATA, fees missing; no trading inference."`. The resulting criterion receipt belongs on the task card; this report is kept unchanged after receipt generation.
