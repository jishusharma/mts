# Bollinger chart verification audit

Date: 2026-11-02. Card: gpt-audit-formulas-vs-bollinger-chart-verify.
Audit base: fd384c869. The filename retains the card's requested 2026-11-01 date.

Verdict: SAME for finite numeric closes: both implementations match the independent population-standard-deviation derivation. DIFFERENT invalid-input handling; no production edits made. This is formula verification, not a trading-edge claim.

## Definition and independent arithmetic

Specification: MyTradingSys/backtest/layers/FORMULAS.md:556 (definition, defaults, warm-up and sample variant), :558 (worked examples). Implementation A: scripts/dev/chart_verify.py:37-46 (mean :42, population divisor :43, outputs :44). Implementation B: MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:33-44 (finite guard :38-39, mean :40, population divisor :41, outputs :42).

SOURCED here means the existing section 22 specification, not an independent verification of TradingView. n=4 and mult=2 are its worked-example inputs. The n=20 sequence 1..20 and assertion tolerance 1e-12 are OURS audit fixtures. No external service was queried.

For [8,10,10,12,14,12], first window [8,10,10,12] has mean 10, squared deviations 4+0+0+4=8; variance=8/4=2. Final window [10,12,14,12] has mean 12 and the same variance. Thus half-width=2*sqrt(2), independently of the code.

| Case | Hand-derived upper / middle / lower | Chart A | Alert B upper / lower | Verdict |
|---|---|---|---|---|
| First window, index 3 | 12.828427124746 / 10 / 7.171572875254 | same triple | 12.828427124746 / 7.171572875254 | SAME |
| Final window, index 5 | 14.828427124746 / 12 / 9.171572875254 | same triple | 14.828427124746 / 9.171572875254 | SAME |
| Default n=20, closes 1..20, index 19 | 22.032562594671 / 10.5 / -1.032562594671 | same triple | 22.032562594671 / -1.032562594671 | SAME |
| Warm-up, indices 0..2 for n=4 | None in every output | None | None | SAME |
| Empty / n-1 / n closes, n=4 and n=20 | length preserved; first value at n-1 only | matches | matches | SAME |

For 1..20: sum=210, sum of squares=2870, mean=10.5; population variance=2870/20-10.5^2=33.25. Half-width=2*sqrt(33.25)=sqrt(133). Alert B exposes no middle array; that output is NOT_IN_DATA for B, rather than independently observed there.

The sample-divisor alternative for the final n=4 window has sd=sqrt(8/3), upper=15.265986323711 and lower=8.734013676289. Both functions instead return the population values above: DIFFERENT from this intentionally wrong variant, as required. At n=20 the sample/population half-width ratio is sqrt(20/19)=1.025978352085, or +2.597835208515%, agreeing with the spec's rounded 2.6%. This percentage describes distance from the middle (and total width), not a 2.6% rise in upper-band price. No sample-sd switch exists in either function.

## Boundary difference (report only)

With [1,2,3,NaN], n=4, A emits NaN for upper/middle/lower; B emits None. With positive infinity, A's middle is infinity and its bands are NaN; B emits None. With None, A raises TypeError while B emits None. This follows A's absent finite guard (:41-43) versus B's _num (:29-30) and window guard (:38-39). The section 22 definition specifies warm-up, not invalid-input policy: the inputs' desired handling is NOT_IN_DATA in that specification. This is a bounded discrepancy, not a failure of the finite-data arithmetic. Any harmonization needs a separately scoped change.

## Verification and reproduction

Before work, the required report did not exist (Test-Path returned False). The audit card makes this report its acceptance artifact; no production test or implementation change was required. The following stdlib-only checker imports both actual modules (no network call), uses hand-derived expectations, rejects the sample-sd upper, and checks warm-up plus invalid inputs. Run from the repository root with Python; all assertions passed on 2026-11-02.

```python
import importlib.util, math, sys
from pathlib import Path
root=Path.cwd()
def load(name, rel):
    spec=importlib.util.spec_from_file_location(name,root/rel)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
chart=load('chart_verify','scripts/dev/chart_verify.py')
live=load('live_bb','MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py')
x=[8,10,10,12,14,12]
u,m,l=chart.bollinger(x,4,2); a,b=live.bollinger(x,4,2)
for i,mean in [(3,10),(5,12)]:
    expected=(mean+2*math.sqrt(2),mean,mean-2*math.sqrt(2))
    assert all(math.isclose(v,e,abs_tol=1e-12) for v,e in zip((u[i],m[i],l[i]),expected))
    assert (a[i],b[i])==(u[i],l[i])
    print(i, expected, (a[i],b[i]))
assert all(z[:3]==[None]*3 for z in (u,m,l,a,b))
for n in (4,20):
    for k in (0,n-1,n):
        inp=list(range(1,k+1)); c=chart.bollinger(inp,n); d=live.bollinger(inp,n)
        assert all(v is None for z in (*c,*d) for v in z[:n-1])
        assert all(len(z)==k for z in (*c,*d))
        if k==n: assert all(z[-1] is not None for z in (*c,*d))
sample=12+2*math.sqrt(8/3)
assert not math.isclose(u[-1],sample,abs_tol=1e-6)
y=list(range(1,21)); c=chart.bollinger(y); d=live.bollinger(y)
expected=(10.5+math.sqrt(133),10.5,10.5-math.sqrt(133))
assert all(math.isclose(v,e,abs_tol=1e-12) for v,e in zip((c[0][-1],c[1][-1],c[2][-1]),expected))
assert (d[0][-1],d[1][-1])==(c[0][-1],c[2][-1])
print('n20',expected,'sample half-width increase pct',100*(math.sqrt(20/19)-1))
for bad in (float('nan'),float('inf')):
    c=chart.bollinger([1,2,3,bad],4); d=live.bollinger([1,2,3,bad],4)
    assert all(not math.isfinite(z[-1]) for z in c) and all(z[-1] is None for z in d)
try: chart.bollinger([1,2,3,None],4)
except TypeError: pass
else: raise AssertionError('expected TypeError')
assert live.bollinger([1,2,3,None],4)==([None]*4,[None]*4)
print('PASS: hand-derived cases, warm-up/length boundaries, sample-sd rejection, invalid-input differences')


```

Observed: PASS: hand-derived cases, warm-up/length boundaries, sample-sd rejection, invalid-input differences.
