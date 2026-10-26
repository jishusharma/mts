# Independent multiplicity bars from the trial ledger

## Method fixed before computing bars

SOURCED method: the union-bound Bonferroni adjustment, with simultaneous two-sided interval multiplier t_(1-alpha/(2N), df), from [NIST, Bonferroni's method](https://itl.nist.gov/div898/handbook/prc/section4/prc473.htm), equations for simultaneous coverage and confidence intervals (retrieved 2026-10-27 IST). The inequality requires valid individual tests; it does not require independent tests. Applying it to dependent trading outcomes requires a valid dependence-aware standard error and reference distribution; this report does not claim the NIST ANOVA assumptions hold for trades.

OURS choices for this audit: familywise alpha=0.05, two-sided tests, a one-sided positive economic claim must still clear that conservative two-sided upper bar. N initially means ledger row count in a family, not the unknown effective number of economic hypotheses. Table gives the normal-limit diagnostic z_N = inverse_Normal(1-alpha/(2N)), and the explicit finite-df t formula; do not silently substitute z_N for a small-sample clustered t threshold. Net-R bar is mean_net_R > t_N,df * SE(mean_net_R), so it cannot be a universal constant R without the frozen validation standard error and degrees of freedom. Net R already subtracts fees; do not charge them twice. FORMULAS.md:468-470 supplies realised net R; :479-483 warns that aggregation/inference uses day blocks rather than treating dependent events as independent.

SOURCED count baseline: the shipped Argon report `argon_trials_by_layer.md`, UNCHECKED until independently recounted here. Preserve its canonical family assignments, including UNMAPPED and the unregistered levels family. A line beginning '| 20' is one ledger row. Count all rows including the UNKNOWN-window entry for a conservative inventory; separately identify known DEV rows. Zero rows means no audited multiplicity budget, not zero historical tries.

Crucial distinction (OURS statistical interpretation): a single frozen candidate selected on DEV then tested once on genuinely untouched VALIDATION is one validation hypothesis. DEV's best-of-N does not by itself require N validation re-tests; the validation family is the number of claims actually tested/selected on that validation set, across reads. If N candidates or outcomes are compared on validation, freeze their family and apply the correction to that full family. Ledger-row bars below are a conservative scenario for that family size, not proof all prior selection bias has been excluded. Already-read validation cannot be made untouched by increasing a cutoff.

## Independent inventory and bars

RESULT (2026-10-26 UTC / 2026-10-27 IST, JIS-NUC), audited d82fa0d63: all 281 rows independently enumerated and assigned exactly once; canonical Argon counts match. 280 have known DEV use, one (Tom image pilot) has unknown window. One RSI row explicitly records DEV plus a prior VALIDATION read. This audit read only the public ledger, not that validation output or any market data. Input TRIALS.md SHA-256: `8fa678d635d7ca41f68519e9caa92b5c24a16fa3bbf3cd39e113edcff969d4fa`. Trust: UNCHECKED; this is a separate recount over a shared public ledger, not a source-independent inventory of every historical experiment.

For every N>0 below the exact p-value ceiling is 0.05/N, finite-df t bar is t_(1-0.025/N,df), and required net-R mean is that t bar times valid SE in R. The numeric column is **normal-limit z only**. No numerical validation SE/df was available or opened. Counts and source line ranges are SOURCED ledger facts, independently recounted; alpha, tails, row-based family definition and normal approximation are OURS audit choices, not trader parameters.

| Canonical family | Ledger N | Known DEV rows | Two-sided p ceiling | Normal-limit z | TRIALS.md lines |
|---|---:|---:|---:|---:|---|
| tom | 1 | 0 | 0.05 | 1.959964 | 278 |
| fabio | 4 | 4 | 0.0125 | 2.497705 | 8,14,17,281 |
| guidance | 0 | 0 | NOT_IN_DATA | NOT_IN_DATA | none |
| rsi | 4 | 4 | 0.0125 | 2.497705 | 9,11,274,282 |
| cryptocred | 1 | 1 | 0.05 | 1.959964 | 13 |
| positioning | 2 | 2 | 0.025 | 2.241403 | 5,279 |
| session_timing | 3 | 3 | 0.01666666667 | 2.393980 | 2,12,16 |
| volume_candles_ma | 8 | 8 | 0.00625 | 2.734369 | 3,6,10,15,261-264 |
| live_engine | 0 | 0 | NOT_IN_DATA | NOT_IN_DATA | none |
| callers | 0 | 0 | NOT_IN_DATA | NOT_IN_DATA | none |
| krown | 4 | 4 | 0.0125 | 2.497705 | 275-277,280 |
| wavetrend | 1 | 1 | 0.05 | 1.959964 | 273 |
| pitchfork | 0 | 0 | NOT_IN_DATA | NOT_IN_DATA | none |
| UNMAPPED | 253 | 253 | 0.0001976284585 | 3.722029 | 4,7,18-260,265-272 |
| **Total inventory** | **281** | **280** | **0.0001779359431 if one global row-family** | **3.748443** | 2-282 |

Tom's N=1 is an image audit row, not one known trading-edge test. Its threshold is an inventory scenario only. UNMAPPED contains 251 levels-related rows (243 original + 8 desk), one BB reversal row and one mixed-family exit rerun. Levels is not a registered canonical family here; do not relabel all those rows Krown. Applying alpha=0.05 separately to each family does not control the chance of any false discovery across all families. If all 281 rows were the full global test family, the global row-based z would be 3.748443 (280 known-DEV rows: 3.747548). Neither row total proves the true hypothesis count.

## What row counts miss

- TRIALS.md:18-257 records the original 240 levels grid arms individually. Lines 258-260 add an arm, a diagnostic and the selected FROZEN result; the FROZEN row is a repeated selected result, not a fresh independent try. Lines 265-272 add eight desk rows. The 240-grid-only normal-limit bar is 3.708691; all 251 levels-row inventory scenario gives 3.720025. Correlation between arms does not invalidate a correctly specified Bonferroni family, but neither duplicates nor absent unlogged tries let us infer a true count.
- Positioning has two ledger rows, but :279 contains 144 variants. A scenario treating that grid plus the other row as 145 hypotheses gives p<=0.0003448275862 and z=3.579064, much higher than the two-row z=2.241403. It remains a scenario: the event-enumeration row need not itself be an inferential test.
- Fabio :281 contains 32 OI cells. Treating those plus its three other rows as 35 tests gives p<=0.001428571429 and z=3.188815, instead of the four-row 2.497705. Again the other rows are not automatically economic hypotheses.
- Krown :275-277 describe 12, 30 and 3 count-grid points, explicitly no outcome read, plus one desk row at :280. Counting every point plus the desk gives 46 and z=3.266995. That is an illustration of compression, not a recommendation to charge 45 outcome tests for a counts-only calibration. The frozen outcome-test family must decide what is genuinely tested.
- RSI :282 compresses 4 timeframe x 4 window x 7 level x 3 visit buckets = 336 cells before its several metrics. The row records a validation read. Its four-row threshold is therefore not a certificate for that already-read validation programme, and there is no justified complete expanded N from the ledger alone.

These facts make an unconditional 'best-of-N luck is excluded' statement unsupported by the row count. Valid inference requires the complete, predeclared hypothesis family and individual p-values with an appropriate dependence-aware null. A controlled 5% false-positive rate is a probabilistic guarantee under assumptions, never literal exclusion of luck.

## Worked checks

Three-trial hand oracle (OURS synthetic): alpha=0.05, N=3, so each two-sided p must be <=0.05/3=1/60=0.01666666667. For p=[0.01,0.02,0.03], only the first rejects. The union-bound budget is 3*(1/60)=0.05. This known answer was asserted in the independent calculator. A one-test check reproduces z=1.95996398454; every computed z was checked using erfc(z/sqrt(2))=alpha/N, without repository quantile helpers.

RSI family example: line allocation [9,11,274,282] gives four rows. 0.05/4=0.0125; upper-tail quantile probability=1-0.05/(2*4)=0.99375; inverse normal=2.4977054744123737. With an **illustrative OURS SE of 0.15 R**, the asymptotic net mean must exceed 2.4977054744*0.15=0.37465582116185603 R. This is not a measured validation result or a fee forecast. For finite df use t_(0.99375,df)*SE instead; missing df is not silently replaced with the number of trades. Use the frozen block/cluster method specified for that actual family.

An illustrative independent-event parametrisation SE=sd_R/sqrt(n_eff) may express the same bar. With OURS sd_R=1.5 and n_eff=100, SE is 0.15 R and the same toy threshold results. The effective sample count is a design assumption here, not estimated from the ledger; actual overlapping trades cannot simply use raw n. No formula in FORMULAS.md defines a multiplicity correction: :468-470 and :479-483 supply the P/L units and block-inference context only. This correction is separately sourced above.

The desk's `luck(sd,n,tries)` at sim_desk/desk.py:99-104 uses sd*sqrt(2 ln N)/sqrt(n). It describes an extreme-value approximation to a typical best-of-N scale, not a 95% familywise critical value; it cannot replace the bar above. For N=1 it returns zero, whereas a single two-sided 5% normal test needs 1.959964*SE. This comparison is mathematical, not a trading verdict.

## Validation interpretation and next use

Before any new validation read, freeze which distinct claims will be tested and the shared family budget, confirm its window has not already informed those claims, and specify the net-R estimator, clustering/blocks and p-value method. For a single genuinely untouched frozen validation claim, N_val=1 even if DEV explored many candidates. If several DEV-selected families are validated, count the actual validation claims together or allocate their alpha shares explicitly; do not give each an uncoordinated 5% global budget. This is OURS application of the stated multiple-testing method, not a change to any frozen pre-registration.

No outcome was calculated and no layer keep/drop/demote/park decision was made. No VALIDATION/HOLDOUT dataset or probability-table output was opened. Report scope complete: per-family inventory and conditional bars are provided, with limitations rather than a false unconditional certification.

## Reproduction

The following standard-library calculator counts the complete line allocation exactly once, verifies the known-answer toy and normal tails, and prints the table. It imports no study code. Adjust root to a clean checkout. Source baseline: `MyTradingSys/research/design_cards_2026-10-26/argon_trials_by_layer.md`, summary table and line audit; this report independently parsed every TRIALS.md row and checked the allocation covers the whole file.

```python
import collections
import hashlib
import math
from pathlib import Path
from statistics import NormalDist

root=Path('F:/MTS/mts-jis-nuc-queue-batch')
p=root/'MyTradingSys/research/layer_lab/TRIALS.md'
rows={i:s for i,s in enumerate(p.read_text().splitlines(),1) if s.startswith('| 20')}
groups={
 'tom':[278], 'fabio':[8,14,17,281], 'guidance':[], 'rsi':[9,11,274,282],
 'cryptocred':[13], 'positioning':[5,279], 'session_timing':[2,12,16],
 'volume_candles_ma':[3,6,10,15,261,262,263,264], 'live_engine':[], 'callers':[],
 'krown':[275,276,277,280], 'wavetrend':[273], 'pitchfork':[],
 'UNMAPPED':[4,7]+list(range(18,261))+list(range(265,273))}
flat=[i for g in groups.values() for i in g]
assert len(flat)==len(set(flat))==len(rows)==281 and set(flat)==set(rows)
assert rows[278].split('|')[2].strip()=='argon-blind-read-7-frames'
assert all('lc-ladder-dev' in rows[i] for i in range(18,261))
assert all('sim-desk levels' in rows[i] for i in range(265,273))
alpha=.05
def bar(n):
    if not n:return None
    z=NormalDist().inv_cdf(1-alpha/(2*n))
    assert abs(math.erfc(z/math.sqrt(2))-alpha/n)<1e-13
    return z
# Hand 3-trial oracle: .05/3=1/60. Only p=.01 clears; no normal math needed.
assert [x<=alpha/3 for x in (.01,.02,.03)]==[True,False,False]
assert math.isclose(bar(1),1.959963984540054,abs_tol=1e-12)
print('TOY: PASS; union-bound sum 3*(.05/3)=.05; N=1 normal quantile hand-table check PASS')
print('hash',hashlib.sha256(p.read_bytes()).hexdigest())
print('| Family | ledger N | known DEV rows | p ceiling .05/N | normal-limit z | ledger lines |')
print('|---|---:|---:|---:|---:|---|')
for family,idx in groups.items():
    n=len(idx);dev=n-(family=='tom')
    span=','.join(map(str,idx)) if len(idx)<10 else '4,7,18-260,265-272'
    print(f'| {family} | {n} | {dev} | {alpha/n:.10g} | {bar(n):.6f} | {span} |' if n else f'| {family} | 0 | 0 | NOT_IN_DATA | NOT_IN_DATA | none |')
print('total',len(rows),'known DEV',280,'pooled z281',bar(281),'pooled z280',bar(280))
for name,n in [('levels distinct grid',240),('levels rows incl desk',251),('funding variants scenario',145),('OI cells plus other rows scenario',35),('Krown count-grid points plus desk',46)]:
    print(name,n,'p',alpha/n,'z',bar(n))
print('rsi worked z',bar(4),'illustrative SE=.15 threshold',bar(4)*.15)

```
