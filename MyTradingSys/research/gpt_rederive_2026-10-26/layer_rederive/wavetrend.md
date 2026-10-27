# WaveTrend independent re-derivation — 2026-10-28

FIX-FIRST: raw outcome reconstruction is NOT_IN_DATA in the permitted tracked evidence. Arithmetic consistency checks are reported separately and do not validate the producer's statistics. No keep/drop verdict is made.

Scope: `lf-wavetrend-gpt-rederive`, starting from `d2632c605`, in an isolated worktree. The family entry at `MyTradingSys/system/layer_index.json:716-735` lists the exposure ledger and four result documents. All four and the three named source documents were read. The reproducible script below is embedded here to respect the card's new-file-only scope. No producer calculation module was read, imported or executed. No outcome study, tuning, sealed-data read, Holm calculation, image review, or additional model session was performed.

Evidence boundary: `git ls-files` identifies only aggregate counts, strata, aggregate JSON statistics and a later input manifest under the study's tracked CSV/JSON files. The exposure ledger has two WaveTrend study registrations, not trades. The aggregate JSON contains summary dictionaries, not event timestamps, entry/exit prices, stop distances, individual returns, day memberships, or the 200 control draws. The manifest is metadata, not the underlying bars, and does not bind historical outcomes to its later file digests. Local untracked market data was not accessed: the active gateway announcement restricts access to public tracked files. NOT_IN_DATA means unavailable within this authorized evidence boundary, not that data cannot exist elsewhere.

Written formulas used:

- `FORMULAS.md:133-142` defines signed forward return and omission of incomplete horizons. `PRE_REG.md` section 6 explicitly uses next-open entry instead of the generic formula's event-close entry. Thus atlas `r_i = direction_i * (close[t_i+12] - open[t_i+1]) / open[t_i+1]`; `n = count(complete eligible events)`; mean bps `= 10000 * sum(r_i)/n`; mean percent `= 100 * sum(r_i)/n`; percent `= bps/100`. Missing horizon data is omitted, never set to zero. These formulas require individual events and prices, which are absent here.
- Mean R requires a risk denominator. `FORMULAS.md:468-479` gives gross R as signed price change divided by initial price risk, with fees subtracted before division for net R. The atlas specifies no stops/targets (`ATLAS_STUDY_SPEC.md` section 4). Its `R_out=3` is a band-arrival bar count, not monetary risk. Mean R and actual executed trade counts are NOT_IN_DATA; atlas N denotes measured episodes.
- Fees: `FORMULAS.md:345-351` defines net return by subtracting fees, slippage and signed funding. `PRE_REG.md` section 6 and the reports explicitly specify gross, no fees/funding. No net result can be derived without execution and funding records. The later registry cost metadata `0.14` does not prove costs were deducted from these outcomes.
- Side arithmetic: `events = side_up + side_lo`. This reconstructs an aggregate total from two aggregate components only; it does not recount raw events or unique dates. Matching multiple producer summaries is metadata consistency only.

Run from the repository root with Python (standard library only):

```powershell
@'
from pathlib import Path
p = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/wavetrend.md')
s = p.read_text(encoding='utf-8').split('```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(s, str(p), 'exec'))
'@ | python -
```

The following independent script prints the evidence tables and SHA-256 receipts. It deliberately refuses to manufacture raw counts or returns from saved means. `forward_summary` records the written calculation for use only when raw rows become available; no raw rows are available or passed in this audit.

```python
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

root = Path.cwd()
study = 'MyTradingSys/research/wavetrend_2026-10-17/'
texts = {}
def read(path):
    if path not in texts:
        texts[path] = (root / path).read_text(encoding='utf-8')
    return texts[path]
def rows(path):
    return list(csv.DictReader(io.StringIO(read(path))))
def loc(path, needle):
    for line, value in enumerate(read(path).splitlines(), 1):
        if needle in value:
            return f'{path}:{line}'
    raise ValueError((path, needle))
def forward_summary(raw_rows):
    # Independent written-formula implementation; incomplete outcomes omitted.
    rr = [r['direction'] * (r['exit_close'] - r['next_open']) / r['next_open']
          for r in raw_rows if r['exit_close'] is not None]
    return len(rr), (10000 * math.fsum(rr) / len(rr) if rr else None)
assert forward_summary([{'direction': 1, 'next_open': 100, 'exit_close': 101},
                        {'direction': -1, 'next_open': 100, 'exit_close': 99},
                        {'direction': 1, 'next_open': 100, 'exit_close': None}]) == (2, 100.0)
assert forward_summary([]) == (0, None)
def table(headers, values):
    print('| ' + ' | '.join(headers) + ' |')
    print('|' + '|'.join(['---'] * len(headers)) + '|')
    for value in values:
        print('| ' + ' | '.join(map(str, value)) + ' |')

index = json.loads(read('MyTradingSys/system/layer_index.json'))
def find_family(value):
    if isinstance(value, dict):
        if value.get('id') == 'wavetrend':
            return value
        for child in value.values():
            found = find_family(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_family(child)
            if found:
                return found
family = find_family(index)
for path in family['spec'] + family['results'] + family['ledger']:
    read(path)
read('MyTradingSys/backtest/layers/FORMULAS.md')
cells = rows(study + 'counts/CELLS.csv')
counts = rows(study + 'counts/counts_R3_c5_k2_G20.csv')
saved = json.loads(read(study + 'atlas_out/atlas_results.json'))
manifest = json.loads(read(study + 'input_manifest.json'))
read(study + 'counts/strata.csv')
read(study + 'counts/quality.txt')
read(study + 'atlas_out/run.log')
checks = Counter()
def status(ok):
    label = 'MATCH' if ok else 'MISMATCH'
    checks[label] += 1
    return label

print('## Script evidence output')
print('\n### Frozen cell count arithmetic (aggregate-only)\n')
out = []
for c in cells:
    summed = int(c['side_up']) + int(c['side_lo'])
    count = next(x for x in counts if all(x[k] == c[k] for k in ('tf','event','bin')))
    out.append([c['cell'], c['events'], summed, status(summed == int(c['events'])),
                count['events'], status(int(count['events']) == int(c['events'])),
                loc(study + 'counts/CELLS.csv', c['cell'] + ','),
                loc(study + 'PRE_REG.md', '| ' + c['cell'] + ' |')])
table(['Cell','Quoted frozen N','Up + lower','Arithmetic','Count-table N','Consistency','Components','Written claim'], out)

print('\n### Primary headline units (summary consistency only)\n')
result = study + 'RESULT.md'
out = []
for c in saved['cells']:
    line = next(x for x in read(result).splitlines() if x.startswith('| ' + c['cell'] + ' '))
    fields = [x.strip() for x in line.strip('|').split('|')]
    computed = c['conj']['mean_bps'] / 100
    out.append([c['cell'], fields[2], f'{computed:.4f}',
                status(f'{computed:.4f}' == fields[2]),
                'NOT_IN_DATA', loc(result, line)])
table(['Cell','Quoted mean %','Saved bps / 100','Unit consistency','Raw mean reconstruction','Claim'],out)

print('\n### Every reported outcome row: counts and means\n')
print('The saved values in this table are transcribed aggregate evidence, never raw recomputations. '
      'Each raw N and raw mean check is NOT_IN_DATA. Consistency compares the printed N/mean with saved aggregates.\n')
arm_keys = {'conjunction':'conj', 'WT alone':'wt_alone',
            'context alone':'context_alone', 'random clock':'random_clock'}
out = []
for line in read(result).splitlines():
    if not line.startswith('| '):
        continue
    f = [x.strip() for x in line.strip('|').split('|')]
    if len(f) == 16 and f[0].startswith('W') and f[4] in arm_keys:
        c = next(x for x in saved['cells'] if x['cell'] == f[0])
        arm = c[arm_keys[f[4]]]
        label, quoted_n, quoted_mean = f'{f[0]} {f[4]}', f[5], f[8]
    elif len(f) in (8,9) and f[0] in ('5m','15m','1h','4h'):
        group = saved['controls'] if len(f) == 9 else saved['descriptive']
        c = next(x for x in group if x['tf'] == f[0] and x['event'] == f[1])
        arm = c['conj']
        label, quoted_n, quoted_mean = f'{f[0]} {f[1]}', f[2], f[4]
    else:
        continue
    n_ok = status(int(quoted_n) == arm['n'])
    mean_ok = status(f"{arm['mean_bps']:.2f}" == quoted_mean)
    out.append([label,quoted_n,quoted_mean,arm['n'],f"{arm['mean_bps']:.8f}",
                f'{n_ok}/{mean_ok}', 'NOT_IN_DATA / NOT_IN_DATA',loc(result,line)])
assert len(out) == 53, len(out)
checks['NOT_IN_DATA_raw_outcome_fields'] = len(out) * 2
table(['Row','Quoted N','Quoted mean bps','Saved N','Saved mean bps',
       'N/mean consistency','Raw N / raw mean','Claim'],out)

print('\n### Data splits and fee evidence\n')
ledger_path = family['ledger'][0]
exposure = [r for r in rows(ledger_path) if 'wavetrend' in str(r).lower()]
assert len(exposure) == 2
print('Exact exposure records (study registrations, not trade ledgers):\n')
for r in exposure:
    print('- ' + json.dumps(r, sort_keys=True))
print('\nDEV calendar length from written dates: ' + str((date(2024,7,1)-date(2022,1,1)).days) + ' days.')
print('Saved reads flags: ' + json.dumps(saved['reads'], sort_keys=True) +
      '; metadata only, historical I/O is NOT_IN_DATA.')
print('Manifest: ' + str(manifest['n_files']) + ' DEV filenames; summed reported rows = ' +
      str(sum(f['rows'] for f in manifest['files'])) +
      '; file contents and historical run binding NOT_IN_DATA.')
print('\n### Tracked evidence inventory\n')
tracked = subprocess.check_output(['git','ls-files'],text=True).splitlines()
for path in tracked:
    if (path.startswith(study) and path.endswith(('.csv','.json'))) or 'tom_raw/klines/' in path:
        print('- `' + path + '`')
print('\n### SHA-256 receipts\n')
for path in sorted(texts):
    print('- `' + path + '` `' + hashlib.sha256((root/path).read_bytes()).hexdigest() + '`')
print('\nConsistency checks (not independent raw-result validations): ' + json.dumps(dict(checks),sort_keys=True))
```

Additional claim comparison (all paths are repository-relative):

| Claim | Written evidence | Independent finding | Classification |
|---|---|---|---|
| Gross, no fees/funding | RESULT.md:5; PRE_REG.md section 6; AUDIT_2026-10-18.md, Confirmed scope; DISPOSITION_2026-10-19.md:3; STATUS_2026-10-19.md:8 | Written contracts agree. No execution ledger to verify actual deductions. | MATCH for documentation; NOT_IN_DATA for raw treatment |
| DEV 2022-01-01 through 2024-06-30 | Exposure ledger:6-7; PRE_REG.md:9; RESULT.md:5 | Calendar interval independently gives 912 days. Actual event/outcome timestamp coverage unavailable. | MATCH for calendar/metadata; NOT_IN_DATA for actual split |
| VALIDATION/HOLDOUT reads 0 | RESULT.md:5; AUDIT_2026-10-18.md, Confirmed scope; saved JSON reads flags | Summary flags agree; no historical access log proves the producer read count. This audit read neither partition. | MATCH for metadata; NOT_IN_DATA for historical reads |
| W04 1155 frozen vs 1154 with outcome | PRE_REG.md frozen W04 row; RESULT.md primary W04 row and Honest MDE paragraph | Aggregate difference is 1. The claimed series-end truncation cannot be verified without the omitted timestamp and bars. It is not automatically a mismatch. | MATCH for subtraction; NOT_IN_DATA for reason/raw count |
| Mean R / executed trades | ATLAS_STUDY_SPEC.md section 4; PRE_REG.md section 6 | No strategy stops/targets or monetary risk; gross episode returns cannot be relabelled R or executed trades. | NOT_IN_DATA |
| Costs recorded as 0.14 later | DISPOSITION_2026-10-19.md, Verdict re-gate; STATUS_2026-10-19.md:9 | Registry metadata is not an observed fee deduction and cannot convert gross atlas returns to net R. | NOT_IN_DATA for fee-net outcomes |

Limitations preserved: AUDIT_2026-10-18.md and both later dispositions identify W07/W08 as invalid for the specified confirmed-WT-pivot C1 definition. This audit does not revalidate their detector or use their saved returns to infer a corrected C1 result. The later manifest's existence does not retroactively contradict the historical audit's missing-manifest finding. The reports' four FAIL/five INCONCLUSIVE classification and 0/9 passing statement depend on inference outside this card; no verdict or nine-arm Holm calculation is reproduced here.

Follow-up cards created: none. The existing separate Holm and C1 cards retain their scope. Raw reconstruction would require permitted event-level DEV timestamps, directions, next-open and horizon-close prices, UTC date groups and control draw assignments, tied to the exact historical inputs; mean R additionally requires a defined risk and execution/cost ledger.

## Script evidence output

### Frozen cell count arithmetic (aggregate-only)

| Cell | Quoted frozen N | Up + lower | Arithmetic | Count-table N | Consistency | Components | Written claim |
|---|---|---|---|---|---|---|---|
| W01 | 3893 | 3893 | MATCH | 3893 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:2 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:68 |
| W02 | 4196 | 4196 | MATCH | 4196 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:3 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:69 |
| W03 | 3509 | 3509 | MATCH | 3509 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:4 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:70 |
| W04 | 1155 | 1155 | MATCH | 1155 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:5 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:71 |
| W05 | 788 | 788 | MATCH | 788 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:6 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:72 |
| W06 | 538 | 538 | MATCH | 538 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:7 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:73 |
| W07 | 298 | 298 | MATCH | 298 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:8 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:74 |
| W08 | 271 | 271 | MATCH | 271 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:9 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:75 |
| W09 | 947 | 947 | MATCH | 947 | MATCH | MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv:10 | MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:76 |

### Primary headline units (summary consistency only)

| Cell | Quoted mean % | Saved bps / 100 | Unit consistency | Raw mean reconstruction | Claim |
|---|---|---|---|---|---|
| W01 | -0.0143 | -0.0143 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:15 |
| W02 | -0.0078 | -0.0078 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:16 |
| W03 | -0.0043 | -0.0043 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:17 |
| W04 | -0.0209 | -0.0209 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:18 |
| W05 | -0.0578 | -0.0578 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:19 |
| W06 | -0.0422 | -0.0422 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:20 |
| W07 | -0.0295 | -0.0295 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:21 |
| W08 | 0.0897 | 0.0897 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:22 |
| W09 | 0.0241 | 0.0241 | MATCH | NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:23 |

### Every reported outcome row: counts and means

The saved values in this table are transcribed aggregate evidence, never raw recomputations. Each raw N and raw mean check is NOT_IN_DATA. Consistency compares the printed N/mean with saved aggregates.

| Row | Quoted N | Quoted mean bps | Saved N | Saved mean bps | N/mean consistency | Raw N / raw mean | Claim |
|---|---|---|---|---|---|---|---|
| W01 conjunction | 3893 | -1.43 | 3893 | -1.42529242 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:29 |
| W01 WT alone | 5114 | -1.07 | 5114 | -1.06619953 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:30 |
| W01 context alone | 3893 | -0.10 | 3893 | -0.09580442 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:31 |
| W01 random clock | 3893 | -0.11 | 3893 | -0.10868839 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:32 |
| W02 conjunction | 4196 | -0.78 | 4196 | -0.77806218 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:33 |
| W02 WT alone | 5114 | -1.07 | 5114 | -1.06619953 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:34 |
| W02 context alone | 4196 | 0.01 | 4196 | 0.01157858 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:35 |
| W02 random clock | 4196 | -0.18 | 4196 | -0.17728770 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:36 |
| W03 conjunction | 3509 | -0.43 | 3509 | -0.43361364 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:37 |
| W03 WT alone | 4229 | -0.15 | 4229 | -0.15288634 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:38 |
| W03 context alone | 3509 | 0.03 | 3509 | 0.03454958 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:39 |
| W03 random clock | 3509 | 0.03 | 3509 | 0.03228348 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:40 |
| W04 conjunction | 1154 | -2.09 | 1154 | -2.09400449 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:41 |
| W04 WT alone | 1369 | -2.02 | 1369 | -2.02386211 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:42 |
| W04 context alone | 1154 | -0.29 | 1154 | -0.28845782 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:43 |
| W04 random clock | 1154 | 0.08 | 1154 | 0.07679826 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:44 |
| W05 conjunction | 788 | -5.78 | 788 | -5.77775809 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:45 |
| W05 WT alone | 873 | -4.55 | 873 | -4.55153055 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:46 |
| W05 context alone | 788 | 0.01 | 788 | 0.00682212 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:47 |
| W05 random clock | 788 | 0.17 | 788 | 0.16776660 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:48 |
| W06 conjunction | 538 | -4.22 | 538 | -4.21649873 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:49 |
| W06 WT alone | 873 | -4.55 | 873 | -4.55153055 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:50 |
| W06 context alone | 538 | 0.49 | 538 | 0.49251144 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:51 |
| W06 random clock | 538 | 0.30 | 538 | 0.29513917 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:52 |
| W07 conjunction | 298 | -2.95 | 298 | -2.94930868 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:53 |
| W07 WT alone | 392 | -6.09 | 392 | -6.08745726 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:54 |
| W07 context alone | 298 | -1.63 | 298 | -1.63244319 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:55 |
| W07 random clock | 298 | -0.07 | 298 | -0.07046857 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:56 |
| W08 conjunction | 271 | 8.97 | 271 | 8.96547957 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:57 |
| W08 WT alone | 392 | -6.09 | 392 | -6.08745726 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:58 |
| W08 context alone | 271 | -1.00 | 271 | -1.00160788 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:59 |
| W08 random clock | 271 | -1.38 | 271 | -1.37855858 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:60 |
| W09 conjunction | 947 | 2.41 | 947 | 2.40605640 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:61 |
| W09 WT alone | 1116 | -1.77 | 1116 | -1.77201041 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:62 |
| W09 context alone | 947 | -0.90 | 947 | -0.90108774 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:63 |
| W09 random clock | 947 | -0.79 | 947 | -0.78751677 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:64 |
| 5m A3_L53 | 6373 | 0.70 | 6373 | 0.70399088 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:102 |
| 5m A1_L60 | 3353 | 0.34 | 3353 | 0.34106228 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:103 |
| 5m A3_L60 | 3854 | 2.23 | 3854 | 2.22600530 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:104 |
| 15m A3_L53 | 2033 | -2.15 | 2033 | -2.15210007 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:105 |
| 15m A1_L60 | 1122 | -4.25 | 1122 | -4.24626334 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:106 |
| 15m A3_L60 | 1268 | -2.71 | 1268 | -2.71240692 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:107 |
| 1h A3_L53 | 533 | -13.75 | 533 | -13.75044304 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:108 |
| 1h A1_L60 | 291 | -24.51 | 291 | -24.50501122 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:109 |
| 1h A3_L60 | 340 | -33.13 | 340 | -33.12821297 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:110 |
| 4h A1_L53 | 102 | -6.48 | 102 | -6.47830254 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:116 |
| 4h A2_L53 | 85 | -2.57 | 85 | -2.56797432 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:117 |
| 4h B1 | 244 | 19.77 | 244 | 19.76894270 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:118 |
| 4h B2 | 56 | 5.14 | 56 | 5.14460849 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:119 |
| 4h C1 | 103 | -13.20 | 103 | -13.20352747 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:120 |
| 4h C2 | 22 | -106.62 | 22 | -106.62046496 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:121 |
| 5m C2 | 1207 | 1.56 | 1207 | 1.56161813 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:122 |
| 15m C2 | 402 | 1.25 | 402 | 1.24813872 | MATCH/MATCH | NOT_IN_DATA / NOT_IN_DATA | MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:123 |

### Data splits and fee evidence

Exact exposure records (study registrations, not trade ledgers):

- {"data_source": "F:/MTS/data/tom_raw/klines BTCUSDT 1m open/high/low/close/volume", "decision_informed": "freezes <=12 WaveTrend atlas cells, R_out/c/k/G and bin edges in PRE_REG.md; no outcome read", "rule_sha256": "9c30147606899f24ea8217cfdb47fe0c35d1a92fd7b7eb11a82ca4042a97abd9", "run_utc": "2026-10-17", "split": "DEV", "study": "wavetrend_2026-10-17/count_events.py", "verdict": "n/a (count-only: events, event-days, context bins; no return, MFE/MAE or hit-rate computed)", "window_read": "2022-01-01..2024-06-30"}
- {"data_source": "F:/MTS/data/tom_raw/klines BTCUSDT 1m open/high/low/close/volume", "decision_informed": "WaveTrend behaviour atlas per PRE_REG: gross 12-bar outcomes with random-clock and context-only controls; no rule adopted; VALIDATION/HOLDOUT unread", "rule_sha256": "4a49d7a9bdffc6b55f61f55bab87f42428165c426a051a2c89328a83908ee670", "run_utc": "2026-10-17", "split": "DEV", "study": "wavetrend_2026-10-17/atlas.py", "verdict": "INCONCLUSIVE (0 of 9 cells pass gross)", "window_read": "2022-01-01..2024-06-30"}

DEV calendar length from written dates: 912 days.
Saved reads flags: {"holdout": 0, "validation": 0}; metadata only, historical I/O is NOT_IN_DATA.
Manifest: 30 DEV filenames; summed reported rows = 1313280; file contents and historical run binding NOT_IN_DATA.

### Tracked evidence inventory

- `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/atlas_results.json`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/counts_R3_c5_k2_G20.csv`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/strata.csv`
- `MyTradingSys/research/wavetrend_2026-10-17/input_manifest.json`

### SHA-256 receipts

- `MyTradingSys/backtest/layers/FORMULAS.md` `212822be89195191878d1dea303fb471c179c2704999d384d5918b4d42d3f667`
- `MyTradingSys/research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv` `c55bbe9806439dcd4c937d51de3c097ef3510a5241af839d78fe855cef96ef37`
- `MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md` `cde1f420df1a461789cb676e8a36b632cc552bd8f0d92211699afb26a179b387`
- `MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md` `d6103bd148eb56d2fde16062ebb033e773ba091c904c64483c3826bcd3a36029`
- `MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md` `5e644e68c9c976d33fe3beca43c11caee1dd15a2bc2d2146d55969042738daa7`
- `MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md` `43dc5bd740f64ef9ec2a7356ee31788d5033d4f2fc2cfbdd286b33e109c26f37`
- `MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md` `d13942554043cbd80bcd14233d1ec7fd4d575a86a07235791ad6e4dfdd51c4fb`
- `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md` `d38d0ff2b25dcea9994de8eed507d8c41bd3705fe832330e5b3fbb89229ea693`
- `MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md` `31b5a5cbb8ce8dd7874f8d8024ba236b21a4222e1ca07bc33e3b96dad6704292`
- `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/atlas_results.json` `92c2288e8e4fc74254f68612d3dc2cef963a8439ca366187bb1aea5e5b7e402c`
- `MyTradingSys/research/wavetrend_2026-10-17/atlas_out/run.log` `555ab74ba1b6180ca00ff126322e6813f548f02056afd9aa9ac6fdee9bd0f00e`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/CELLS.csv` `61d9e4b8e7dcc302b1835e573fa8f8dc72781ccbc2aa45a13851908db7eca563`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/counts_R3_c5_k2_G20.csv` `09879b6cb9fdea5efd7a979a44395df1c0baa68cd549ec200157887671df3270`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/quality.txt` `379126e26a35f22eb6acfcb7965db833508da45ad00d2ccc770593bfb71e0cfb`
- `MyTradingSys/research/wavetrend_2026-10-17/counts/strata.csv` `7440bd2beaf9eb8b251d0fa3494c367976e4ad5d0f5ccea29ff5e0eeabe83bca`
- `MyTradingSys/research/wavetrend_2026-10-17/input_manifest.json` `29dd82c18585e55b27b47f7de19dea50841bf9c974f0d8aca84ae892901d50af`
- `MyTradingSys/system/layer_index.json` `e133ecd6b0dbea24c72f64ed6dbae4dc30e16be02c2538740f923e05fe06cf4f`

Consistency checks (not independent raw-result validations): {"MATCH": 133, "NOT_IN_DATA_raw_outcome_fields": 106}
