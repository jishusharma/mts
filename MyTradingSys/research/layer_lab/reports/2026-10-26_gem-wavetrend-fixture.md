# gem-wavetrend-fixture — 2026-10-28

SOUND: Numeric parity within 1e-9 on 400 fixture rows; wt1 max abs diff 1.0664e-11, wt2 max abs diff 1.0503e-11; 0 event mismatches.

## Audit Overview & Provenance
- Task: `gem-wavetrend-fixture`
- Producer vendor: GPT `gpt-6-luna` (in `MyTradingSys/research/gpt_burn_2026-10-24/gx-wavetrend-rederive/report.md`)
- Reviewer vendor: Gemini (Google Antigravity session on JIS-NUC; strict `producer != reviewer`)
- Scope in:
  - `MyTradingSys/backtest/layers/wavetrend/fixture_btcusdt_1h_dev_2022-01.csv`
  - `MyTradingSys/backtest/layers/wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv`
  - `MyTradingSys/backtest/layers/FORMULAS.md` (lines 510–524)
  - `MyTradingSys/research/gpt_burn_2026-10-24/gx-wavetrend-rederive/report.md`
- Scope out:
  - Code or spec changes; holdout data reads; BTC live/current runs.
  - Restricted files unread: `wt.py`, `audit.py`, `wavetrend.py`.

## Independent Mathematical Re-Derivation
Derivation followed FORMULAS.md:513–523 from first principles without reading production implementation:
1. `ap = (h + l + c) / 3` (HLC3)
2. `alpha_10 = 2 / (10 + 1) = 2 / 11`
3. `alpha_21 = 2 / (21 + 1) = 2 / 22 = 1 / 11`
4. Seeding:
   - Bar 0: `esa[0] = ap[0]`, `d[0] = 0.0`. Since `d <= 1e-9 * |ap|`, `ci[0] = NaN`, `wt1[0] = NaN`.
   - Bar 1: `esa[1] = esa[0] + alpha_10 * (ap[1] - esa[0])`, `d[1] = d[0] + alpha_10 * (|ap[1] - esa[1]| - d[0])`.
     `ci[1] = (ap[1] - esa[1]) / (0.015 * d[1]) = 366.666667`.
     First valid `ci` seeds `wt1`: `wt1[1] = ci[1] = 366.666667`.
   - Bar 2+: `wt1[i] = wt1[i-1] + alpha_21 * (ci[i] - wt1[i-1])`.
   - `wt2 = SMA(wt1, 4)`: requires 4 consecutive non-NaN `wt1` values; first valid at Bar 4 (`sum(wt1[1:5]) / 4`).
5. Cross events:
   - Up-cross (`+1`): `wt1 - wt2 > 0` after prior side `< 0`.
   - Down-cross (`-1`): `wt1 - wt2 < 0` after prior side `> 0`.
   - Flat/tie (`0`): skipped, preserving prior side.

## Comparison Table: Independent Derivation vs Golden Dataset

| Target Column | Total Rows | Finite Compared Pairs | Max Abs Diff | Differing > 1e-9 | NaN Mismatches |
|---|---:|---:|---:|---:|---:|
| `wt1` | 400 | 399 | 1.0664358285339404e-11 | 0 | 0 |
| `wt2` | 400 | 396 | 1.0503153902163831e-11 | 0 | 0 |
| `event` | 400 | 400 | 0 | 0 | 0 |

- Exact numeric diffs are entirely bounded by floating-point rounding order and the 12-decimal truncation in `golden_wt_btcusdt_1h_dev_2022-01.csv`.
- Confirms GPT claim: 399 wt1 pairs, 396 wt2 pairs, max abs diff 1.07e-11, 0 event diffs.

## Findings Table

| Severity | Evidence | Finding | Classification | Proposed Action |
|---|---|---|---|---|
| LOW | `test_wavetrend.py:81-93`; GPT `report.md:64` | Reset recovery test checks up to bar 259 (29 bars post-reset), which is shorter than the 200-bar warmup horizon. | TEST_COVERAGE_GAP | Add long-horizon recovery test past 200 bars in a future test card (already tracked). |
| NONE | `FORMULAS.md:513-523` vs `golden_wt_btcusdt_1h_dev_2022-01.csv` | Full numerical and event agreement between specification and golden series within floating-point tolerance (max diff 1.07e-11 <= 1e-9). | SOUND | None; formula verified. |

## Verification Command
```powershell
python -c "
import csv, math
with open('MyTradingSys/backtest/layers/wavetrend/fixture_btcusdt_1h_dev_2022-01.csv') as f:
    fixture = list(csv.DictReader(f))
with open('MyTradingSys/backtest/layers/wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv') as f:
    golden = list(csv.DictReader(f))
a10, a21 = 2.0/11.0, 2.0/22.0
esa, d, wt1_vals, wt2_vals, events, last_side = None, None, [], [], [], 0
diff_wt1, diff_wt2, diff_ev = [], [], []
for i, row in enumerate(fixture):
    ap = (float(row['high']) + float(row['low']) + float(row['close'])) / 3.0
    if i == 0:
        esa, d, ci, wt1 = ap, 0.0, float('nan'), float('nan')
    else:
        esa += a10 * (ap - esa)
        d += a10 * (abs(ap - esa) - d)
        ci = float('nan') if d <= 1e-9 * abs(ap) else (ap - esa) / (0.015 * d)
        wt1 = ci if (not wt1_vals or math.isnan(wt1_vals[-1])) else wt1_vals[-1] + a21 * (ci - wt1_vals[-1])
    wt1_vals.append(wt1)
    wt2 = sum(wt1_vals[i-3:i+1]) / 4.0 if i >= 4 and all(not math.isnan(wt1_vals[k]) for k in range(i-3, i+1)) else float('nan')
    wt2_vals.append(wt2)
    ev = 0
    if not math.isnan(wt1) and not math.isnan(wt2):
        s = 1 if wt1 > wt2 else (-1 if wt1 < wt2 else 0)
        if last_side != 0 and s != 0 and s != last_side:
            ev, last_side = s, s
        elif s != 0:
            last_side = s
    events.append(ev)
    g_wt1 = float(golden[i]['wt1']) if golden[i]['wt1'] != '' else float('nan')
    g_wt2 = float(golden[i]['wt2']) if golden[i]['wt2'] != '' else float('nan')
    g_ev = int(golden[i]['event'])
    if not math.isnan(wt1) and not math.isnan(g_wt1): diff_wt1.append(abs(wt1 - g_wt1))
    if not math.isnan(wt2) and not math.isnan(g_wt2): diff_wt2.append(abs(wt2 - g_wt2))
    if ev != g_ev: diff_ev.append((i, ev, g_ev))
assert max(diff_wt1) <= 1.07e-11 and max(diff_wt2) <= 1.06e-11 and len(diff_ev) == 0
print(f'PARITY CONFIRMED: wt1 max diff={max(diff_wt1):.4e}, wt2 max diff={max(diff_wt2):.4e}, event diffs={len(diff_ev)}')
"
```
Output: `PARITY CONFIRMED: wt1 max diff=1.0664e-11, wt2 max diff=1.0503e-11, event diffs=0`
