FIX-FIRST

Stage 2 independent challenge: both acceptance criteria PASS. The seeded claim defects remain in the fixture; successful detection satisfies this audit's contract.

Checked originals first: `MyTradingSys/research/layer_lab/examples/pilot-facts.md:1-5` and `MyTradingSys/research/layer_lab/examples/pilot-claims.md:1-8`. Computed directly from the observation list before reading the predecessor card, pack or report. Then read `MyTradingSys/system/tasks/recipe-pilot-1-map.json` to locate its receipt report, `MyTradingSys/research/layer_lab/reports/2026-10-16_recipe-pilot-1-map.md:1-41`. Data range: all three synthetic development observations, no market data.

C1: PASS

The source observations are 10, 11, 9 (`pilot-facts.md:3`). Their independently computed sum is 30 and arithmetic mean is 30 / 3 = 10. Claim A's 31 (`pilot-claims.md:3`) is MISMATCH, overstated by 1; Claim B's 10 (`pilot-claims.md:4`) is MATCH. Attempted falsification of the predecessor's arithmetic found no disagreement: its result at report line 9 agrees with the original observations. Neither the source's printed total nor the expected-audit labels were used as computation inputs.

Executed from the repository root before reading the prior report (exit 0):

```powershell
python -B -c "import re; from pathlib import Path; p=Path('MyTradingSys/research/layer_lab/examples/pilot-facts.md'); s=p.read_text(); obs=list(map(int,re.search(r'observations: ([0-9, ]+)\.',s).group(1).split(','))); total=sum(obs); mean=total/len(obs); print(f'observations={obs}; n={len(obs)}; sum={total}; mean={mean:g}; claim_A=MISMATCH; claim_B=MATCH'); assert total==30 and mean==10; assert 'Fee data was not supplied.' in s; print('claim_C=NOT_IN_DATA; fee input absent; no trading inference')"
```

```text
observations=[10, 11, 9]; n=3; sum=30; mean=10; claim_A=MISMATCH; claim_B=MATCH
claim_C=NOT_IN_DATA; fee input absent; no trading inference
```

The numerical outputs are calculated; classification labels in the command are audit annotations checked against the claims below.

C2: PASS

Claim C (`pilot-claims.md:5`) is NOT_IN_DATA. To challenge the predecessor's missing-input finding, inspected the complete source for fee information: `pilot-facts.md:4` expressly says fee data was not supplied. Lines 1-5 provide no fee amount, rate or defined return basis. The predecessor's conclusion at report line 29 therefore MATCHES the source. No fee is imputed as zero, no net value or sign is computed, and no trading inference is made. The source explicitly excludes performance interpretation (`pilot-facts.md:5`). Missing fees are the intended detection case, not missing evidence needed to complete C2.

| Severity | Claim / file:line | Classification and evidence | Proposed fix |
|---|---|---|---|
| MED | A / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:3` | MISMATCH: 31 claimed versus independently summed 30 from `pilot-facts.md:3`; command above. | Use 30 in downstream accounts; preserve the deliberately faulty fixture. |
| LOW | B / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:4` | MATCH: 10 claimed versus calculated 30 / 3 = 10. | None. |
| MED | C / `MyTradingSys/research/layer_lab/examples/pilot-claims.md:5` | NOT_IN_DATA: fee input expressly absent at `pilot-facts.md:4`; no return basis supplied. | Keep net-after-fees unknown; require defined return and fee inputs before evaluating it. |

Resolution: no disagreements with the predecessor remain; the disagreement with Claim A is resolved by source arithmetic, and Claim C remains unsupported rather than numerically disproved. Source observations are synthetic inputs, not trader parameters. Equal-weight arithmetic mean is used for the complete list. This fixture check is not a backtest or trading trial (`pilot-facts.md:5`), so no trial row is warranted.

Follow-up cards created: none. Sources and predecessor report remain unchanged. Shipping is owned by the runner; the task-specific scope excludes unrelated CI repair.

Closure: `python -B scripts/dev/lab_flow.py finish recipe-pilot-2-challenge --report MyTradingSys/research/layer_lab/reports/2026-10-16_recipe-pilot-2-challenge.md --verdict PASS --result "C1 PASS: independently reproduced sum 30 and mean 10; A MISMATCH, B MATCH. C2 PASS: C NOT_IN_DATA; no fees invented or trading inference; predecessor findings confirmed."`
