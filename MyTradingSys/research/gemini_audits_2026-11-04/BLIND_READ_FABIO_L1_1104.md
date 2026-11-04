# Blind Read Audit: `FABIO_L1_REPORT.md` vs `fabio_l1_strict_rerun.json`

- **Card**: `gemini-blind-read-fabio-l1-strict-1104`
- **Audited Document**: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
- **Primary Data Artifact**: `MyTradingSys/backtest/layers/fabio/fabio_l1_strict_rerun.json`
- **Backtest Driver**: `MyTradingSys/backtest/layers/fabio/run_backtest.py` (noted on card as `run_fabio_l1_backtest.py`, committed in repo as `run_backtest.py`)
- **Date**: 2026-11-04 UTC
- **Auditor**: Gemini 4 Argon (Low) worker

---

## 1. Executive Summary & Parameter Labels

All rule thresholds, grid parameters, split ratios, horizons, and verdict thresholds in the Fabio L1 backtest (`FABIO_L1_REPORT.md:10-16` and `run_backtest.py:42-43,64,89,161-165,191,234`) are **OURS** (`"All thresholds are UNDEFINED in the video, hence the grids"`, `FABIO_L1_REPORT.md:10`; `"runs the three Fabio rule detectors (cvd_absorption, escalation, volume_fvg) over a grid of their UNDEFINED-in-source parameters"`, `run_backtest.py:5-7`). All empirical counts, returns, hit rates, and PBO figures in `fabio_l1_strict_rerun.json:1-559` and `FABIO_L1_REPORT.md:1-121` are **OURS** (realized backtest metrics on BTCUSDT 1m data).

`FABIO_L1_REPORT.md` contains two distinct empirical sections:
1. **Lines 90–121 (`## Strict-detector rerun (2026-11-04, detectors of 2afc18be6)`)**: Directly reports the DEV (`2022-01-01..2024-06-30`, `1,313,280` 1m bars) strict vs legacy detector rerun stored in `MyTradingSys/backtest/layers/fabio/fabio_l1_strict_rerun.json:1-559`. Every single figure in `FABIO_L1_REPORT.md:90-121` (12 table rows $\times$ 8 numeric/verdict columns, plus all prose metadata and variant event sums) matches `fabio_l1_strict_rerun.json` with zero discrepancies (`DIFF = 0`).
2. **Lines 1–89 (Initial `2022-01-01..2026-09-26` full-history legacy run)**: Reports the earlier `2,491,200`-bar run across `2022-01-01..2026-09-26` (whose raw files in `Dumps/backtest/runs/fabio_l1/` are gitignored; `FABIO_L1_REPORT.md:3-6,95-96` explicitly notes `"Window: DEV 2022-01-01..2024-06-30 only (splits.py), 1,313,280 1m bars, so these numbers are NOT comparable to the tables above (those run to 2026-09-26, mostly beyond DEV)"`). All methodological/grid constants in `FABIO_L1_REPORT.md:1-28` match `run_backtest.py` and `fabio_l1_strict_rerun.json`, and all internal arithmetic (gross minus `0.10%` fee = net, bounce vs through exact sign symmetry, and verdict rule application) in `FABIO_L1_REPORT.md:29-89` is 100% self-consistent.

---

## 2. Metadata & Driver Parameter Check (`FABIO_L1_REPORT.md` vs `fabio_l1_strict_rerun.json` & `run_backtest.py`)

| Item | `FABIO_L1_REPORT.md` Value & Line | `fabio_l1_strict_rerun.json` / `run_backtest.py` Value & Line | Label | Match Status |
|---|---|---|---|---|
| Detector commit | `2afc18be6` (`FABIO_L1_REPORT.md:90,94-95`) | `"detector_commit": "2afc18be6"` (`fabio_l1_strict_rerun.json:3`; `run_backtest.py:168`) | OURS | MATCH |
| Rerun window & bar count | `DEV 2022-01-01..2024-06-30`, `1,313,280` 1m bars (`FABIO_L1_REPORT.md:94-96`) | `"window": "DEV 2022-01-01..2024-06-30 (splits.py DEV_END), 1313280 1m bars"` (`fabio_l1_strict_rerun.json:4`) | OURS | MATCH |
| Round-trip fee | `0.10%` (`0.001`) (`FABIO_L1_REPORT.md:9,29,43,66,87,97`) | `"fee_round_trip": 0.001` (`fabio_l1_strict_rerun.json:5`; `run_backtest.py:41-42`) | OURS | MATCH |
| Horizons | `h = 1, 5, 20` bars (`FABIO_L1_REPORT.md:10`) | `HORIZONS = (1, 5, 20)` (`run_backtest.py:43`; keys `"1"`, `"5"`, `"20"` in `fabio_l1_strict_rerun.json:19-50`) | OURS | MATCH |
| Chronological split | `70% IS / 30% OOS` (`FABIO_L1_REPORT.md:7,96-97`) | `def chronological_split(bars, is_frac=0.70):` (`run_backtest.py:64`) | OURS | MATCH |
| Min IS events filter | `>= 5 IS events` (`FABIO_L1_REPORT.md:8,114`) | `min_events=5` (`run_backtest.py:129`; `"variants_with_ge5_is_events"` in `fabio_l1_strict_rerun.json:16`) | OURS | MATCH |
| PBO CSCV blocks | `S=12 blocks` (`FABIO_L1_REPORT.md:9`) | `def pbo_from_columns(cols, S=12):` (`run_backtest.py:108,129`) | OURS | MATCH |
| Escalation chunking | `1000-bar chunks with 500 bars of warm-up` (`~1500 bars`, `FABIO_L1_REPORT.md:21-22`) | `def chunked_events(fn, bars, own=1000, warm=500, **params):` (`run_backtest.py:89`) | OURS | MATCH |
| CVD grid (12 variants) | `left=right in {2,3,5} x price_tolerance in {0.05,0.1,0.2,0.5}%` (`FABIO_L1_REPORT.md:11`) | `CVD_GRID = [{"left": w, "right": w, "price_tolerance": t} for w in (2, 3, 5) for t in (0.0005, 0.001, 0.002, 0.005)]` (`run_backtest.py:161`) | OURS | MATCH |
| Escalation grid (12 variants) | `level_tolerance {0.1,0.2}% x aggression_k {1.5,2,3} x record_lookback {20,50}` (`FABIO_L1_REPORT.md:12`) | `ESCALATION_GRID = [{"level_tolerance": lt, "aggression_k": ak, "record_lookback": rl} for lt in (0.001, 0.002) for ak in (1.5, 2.0, 3.0) for rl in (20, 50)]` (`run_backtest.py:162-165`) | OURS | MATCH |
| Volume FVG params | `20 bins, 70% VA, swings 2/2, first touch within 200 bars` (`FABIO_L1_REPORT.md:13`) | `run_fvg(bars, n_is, n_bins=20, seed=42, max_wait=200)`, `swing_legs(bars, left=2, right=2, use_body=True)`, `value_area(profile, pct=0.70)` (`run_backtest.py:191,198,207`) | OURS | MATCH |
| Verdict rule | `"edge"` if `OOS n >= 30`, `OOS net mean > 0 at h=5`, `PBO < 0.5`; `"insufficient n"` if `OOS n < 30`; else `"no edge"` (`FABIO_L1_REPORT.md:16-17,118`) | Verified across all 12 rows of `FABIO_L1_REPORT.md:101-112` and all 6 rows of `FABIO_L1_REPORT.md:33-38` | OURS | MATCH |

---

## 3. Strict vs Legacy Rerun Table Verification (`FABIO_L1_REPORT.md:99-112` vs `fabio_l1_strict_rerun.json:7-558`)

Every metric in the 12-row rerun table (`FABIO_L1_REPORT.md:99-112`) is verified against `fabio_l1_strict_rerun.json` below (all values **OURS**; `net = gross - 0.10%` round-trip fee from `fabio_l1_strict_rerun.json:5`):

| Row | Rule & TF | Mode | Chosen Params (`REPORT` vs `JSON`) | IS `n` / `h=5` Mean (`REPORT` vs `JSON`) | OOS `n` (`h=5`) (`REPORT` vs `JSON`) | OOS `h=5` Gross / Net (`REPORT` vs `JSON`) | OOS Hit `h=5` (`REPORT` vs `JSON`) | PBO (`REPORT` vs `JSON`) | Verdict (`REPORT` vs Rule) | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `cvd_absorption` `5m` (`FABIO_L1_REPORT.md:101`) | `strict` (`json:9-52`) | `w5, tol 0.2%` vs `left=5, right=5, price_tolerance=0.002` (`json:11-15`) | `2029 / -0.001%` vs `n=2029, mean=-1.4017e-05` (`-0.0014%`, `json:24-27`) | `797` vs `797` (`json:41-42`) | `+0.011% / -0.089%` vs `+0.0001134` (`+0.0113%`) / `-0.0008866` (`-0.0887%`, `json:43`) | `49.7%` vs `0.496863` (`49.69%`, `json:44`) | `0.882` vs `0.882035` (`json:10`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 2 | `cvd_absorption` `5m` (`FABIO_L1_REPORT.md:102`) | `legacy` (`json:284-327`) | `w5, tol 0.1%` vs `left=5, right=5, price_tolerance=0.001` (`json:286-290`) | `1835 / +0.008%` vs `n=1835, mean=8.1183e-05` (`+0.0081%`, `json:299-301`) | `732` vs `732` (`json:316-317`) | `+0.013% / -0.087%` vs `+0.0001333` (`+0.0133%`) / `-0.0008667` (`-0.0867%`, `json:318`) | `47.8%` vs `0.478142` (`47.81%`, `json:319`) | `0.693` vs `0.692641` (`json:285`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 3 | `cvd_absorption` `15m` (`FABIO_L1_REPORT.md:103`) | `strict` (`json:100-143`) | `w2, tol 0.05%` vs `left=2, right=2, price_tolerance=0.0005` (`json:102-106`) | `371 / +0.002%` vs `n=371, mean=2.0961e-05` (`+0.0021%`, `json:115-117`) | `154` vs `154` (`json:132-133`) | `-0.008% / -0.108%` vs `-7.8143e-05` (`-0.0078%`) / `-0.0010781` (`-0.1078%`, `json:134`) | `43.5%` vs `0.435065` (`43.51%`, `json:135`) | `0.760` vs `0.759740` (`json:101`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 4 | `cvd_absorption` `15m` (`FABIO_L1_REPORT.md:104`) | `legacy` (`json:375-418`) | `w3, tol 0.2%` vs `left=3, right=3, price_tolerance=0.002` (`json:377-381`) | `1133 / -0.009%` vs `n=1133, mean=-9.2544e-05` (`-0.0093%`, `json:390-392`) | `506` vs `506` (`json:407-408`) | `-0.022% / -0.122%` vs `-0.0002167` (`-0.0217%`) / `-0.0012167` (`-0.1217%`, `json:409`) | `48.2%` vs `0.482213` (`48.22%`, `json:410`) | `0.685` vs `0.685065` (`json:376`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 5 | `cvd_absorption` `1h` (`FABIO_L1_REPORT.md:105`) | `strict` (`json:191-234`) | `w2, tol 0.05%` vs `left=2, right=2, price_tolerance=0.0005` (`json:193-197`) | `52 / +0.250%` vs `n=52, mean=0.0025002` (`+0.2500%`, `json:206-208`) | `18` vs `18` (`json:223-224`) | `+0.154% / +0.054%` vs `+0.0015422` (`+0.1542%`) / `+0.0005422` (`+0.0542%`, `json:225`) | `55.6%` vs `0.555556` (`55.56%`, `json:226`) | `0.562` vs `0.561688` (`json:192`) | `insufficient n (18 < 30)` | MATCH |
| 6 | `cvd_absorption` `1h` (`FABIO_L1_REPORT.md:106`) | `legacy` (`json:466-509`) | `w5, tol 0.2%` vs `left=5, right=5, price_tolerance=0.002` (`json:468-472`) | `142 / +0.081%` vs `n=142, mean=0.0008133` (`+0.0813%`, `json:481-483`) | `80` vs `80` (`json:498-499`) | `+0.008% / -0.092%` vs `+8.0233e-05` (`+0.0080%`) / `-0.0009198` (`-0.0920%`, `json:500`) | `55.0%` vs `0.55` (`55.00%`, `json:501`) | `0.623` vs `0.623377` (`json:467`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 7 | `escalation` `5m` (`FABIO_L1_REPORT.md:107`) | `strict` (`json:53-96`) | `lt 0.2%, k 3, lb 50` vs `level_tolerance=0.002, aggression_k=3.0, record_lookback=50` (`json:55-59`) | `2244 / +0.040%` vs `n=2244, mean=0.0004010` (`+0.0401%`, `json:68-70`) | `1065` vs `1065` (`json:85-86`) | `+0.033% / -0.067%` vs `+0.0003345` (`+0.0334%`) / `-0.0006655` (`-0.0666%`, `json:87`) | `45.3%` vs `0.452582` (`45.26%`, `json:88`) | `0.171` vs `0.170996` (`json:54`) | `no edge (net < 0)` | MATCH |
| 8 | `escalation` `5m` (`FABIO_L1_REPORT.md:108`) | `legacy` (`json:328-371`) | `lt 0.2%, k 3, lb 50` vs `level_tolerance=0.002, aggression_k=3.0, record_lookback=50` (`json:330-334`) | `9556 / +0.024%` vs `n=9556, mean=0.0002425` (`+0.0242%`, `json:343-345`) | `3913` vs `3913` (`json:360-361`) | `+0.004% / -0.096%` vs `+4.0444e-05` (`+0.0040%`) / `-0.0009596` (`-0.0960%`, `json:362`) | `43.8%` vs `0.438283` (`43.83%`, `json:363`) | `0.893` vs `0.892857` (`json:329`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 9 | `escalation` `15m` (`FABIO_L1_REPORT.md:109`) | `strict` (`json:144-187`) | `lt 0.2%, k 1.5, lb 20` vs `level_tolerance=0.002, aggression_k=1.5, record_lookback=20` (`json:146-150`) | `812 / +0.007%` vs `n=812, mean=7.0432e-05` (`+0.0070%`, `json:159-161`) | `291` vs `291` (`json:176-177`) | `+0.021% / -0.079%` vs `+0.0002074` (`+0.0207%`) / `-0.0007926` (`-0.0793%`, `json:178`) | `47.8%` vs `0.477663` (`47.77%`, `json:179`) | `0.286` vs `0.285714` (`json:145`) | `no edge (net < 0)` | MATCH |
| 10 | `escalation` `15m` (`FABIO_L1_REPORT.md:110`) | `legacy` (`json:419-462`) | `lt 0.1%, k 1.5, lb 50` vs `level_tolerance=0.001, aggression_k=1.5, record_lookback=50` (`json:421-425`) | `1527 / +0.061%` vs `n=1527, mean=0.0006126` (`+0.0613%`, `json:434-436`) | `501` vs `501` (`json:451-452`) | `-0.073% / -0.173%` vs `-0.0007300` (`-0.0730%`) / `-0.0017300` (`-0.1730%`, `json:453`) | `47.7%` vs `0.477046` (`47.70%`, `json:454`) | `0.605` vs `0.604978` (`json:420`) | `no edge` (`net < 0`, `PBO >= 0.5`) | MATCH |
| 11 | `escalation` `1h` (`FABIO_L1_REPORT.md:111`) | `strict` (`json:235-278`) | `lt 0.1%, k 1.5, lb 20` vs `level_tolerance=0.001, aggression_k=1.5, record_lookback=20` (`json:237-241`) | `5 / +0.055%` vs `n=5, mean=0.0005534` (`+0.0553%`, `json:250-252`) | `0` vs `0` (`json:267-268`) | `n/a` vs `null` (`json:269`) | `n/a` vs `null` (`json:270`) | `0.772` vs `0.771645` (`json:236`) | `insufficient n (OOS 0)` | MATCH |
| 12 | `escalation` `1h` (`FABIO_L1_REPORT.md:112`) | `legacy` (`json:510-553`) | `lt 0.1%, k 3, lb 20` vs `level_tolerance=0.001, aggression_k=3.0, record_lookback=20` (`json:512-516`) | `92 / +0.013%` vs `n=92, mean=0.0001259` (`+0.0126%`, `json:525-527`) | `22` vs `22` (`json:542-543`) | `-0.257% / -0.357%` vs `-0.0025737` (`-0.2574%`) / `-0.0035737` (`-0.3574%`, `json:544`) | `31.8%` vs `0.318182` (`31.82%`, `json:545`) | `0.374` vs `0.374459` (`json:511`) | `insufficient n (22 < 30)` | MATCH |

---

## 4. Counted Event Totals & Additional JSON Metrics (`FABIO_L1_REPORT.md:114-121` vs `fabio_l1_strict_rerun.json`)

All prose figures in `FABIO_L1_REPORT.md:114-121` and remaining fields in `fabio_l1_strict_rerun.json` (all **OURS**):

| Metric / Claim | `FABIO_L1_REPORT.md` Value & Line | `fabio_l1_strict_rerun.json` Value & Line | Status |
|---|---|---|---|
| `escalation_1h` strict total IS events (all variants) | `117` (`FABIO_L1_REPORT.md:114`) | `"total_is_events_all_variants": 117` (`fabio_l1_strict_rerun.json:243`) | MATCH |
| `escalation_1h` strict qualifying variants (`>= 5` IS events) | `7 of 12` (`FABIO_L1_REPORT.md:114`) | `"variants_with_ge5_is_events": 7` (`fabio_l1_strict_rerun.json:242`) | MATCH |
| `escalation_1h` legacy total IS events (all variants) | `2,523` (`FABIO_L1_REPORT.md:115`) | `"total_is_events_all_variants": 2523`, `"variants_with_ge5_is_events": 12` (`fabio_l1_strict_rerun.json:517-518`) | MATCH |
| `escalation_1h` strict vs legacy reduction % | `about 95% fewer` (`FABIO_L1_REPORT.md:117`) | $1 - 117 / 2523 = 95.36\%$ (`fabio_l1_strict_rerun.json:243,518`) | MATCH |
| `escalation_15m` strict vs legacy total IS events | `3,775 vs 28,910` (`FABIO_L1_REPORT.md:115`) | `3775` (`json:152`) vs `28910` (`json:427`), both `12` qualifying variants (`json:151,426`) | MATCH |
| `escalation_5m` strict vs legacy total IS events | `33,676 vs 125,915` (`FABIO_L1_REPORT.md:115`) | `33676` (`json:61`) vs `125915` (`json:336`), both `12` qualifying variants (`json:60,335`) | MATCH |
| `cvd_absorption_1h` strict vs legacy total IS events | `1,498 vs 2,749` (`FABIO_L1_REPORT.md:115`) | `1498` (`json:199`) vs `2749` (`json:474`), both `12` qualifying variants (`json:198,473`) | MATCH |
| `cvd_absorption_5m` strict vs legacy total IS events (in JSON) | Not quoted in prose (`12` variants qualifying) | `39372` (`json:16-17`) vs `47634` (`json:291-292`) | MATCH (in JSON) |
| `cvd_absorption_15m` strict vs legacy total IS events (in JSON) | Not quoted in prose (`12` variants qualifying) | `9424` (`json:107-108`) vs `13519` (`json:382-383`) | MATCH (in JSON) |
| `volume_fvg` leg counts (`5m`, `15m`, `1h`) in strict vs legacy | `"Volume FVG does not use the changed detectors: identical in both modes"` (`FABIO_L1_REPORT.md:97`) | `5m`: `31290` (`json:98,373`); `15m`: `10598` (`json:189,464`); `1h`: `2689` (`json:280,555`) — identical in strict and legacy | MATCH |
| `cvd 1h strict` prose summary | `+0.054% net on n = 18 and PBO 0.56` (`FABIO_L1_REPORT.md:118-119`) | `mean_return=0.0015422` (`+0.0542%` net), `n=18`, `pbo=0.561688` (`json:192,224-225`) | MATCH |
| `Strict 5m/15m escalation` low PBO prose summary | `low PBO (0.17 / 0.29) but negative net` (`FABIO_L1_REPORT.md:121`) | `5m` PBO `0.170996` (`json:54`), net `-0.0666%`; `15m` PBO `0.285714` (`json:145`), net `-0.0793%` | MATCH |

### Additional `h=1` and `h=20` Metrics Extracted from `fabio_l1_strict_rerun.json` (all **OURS**)

For completeness (Step 2 of the card), here are all `h=1` and `h=20` IS and OOS metrics from `fabio_l1_strict_rerun.json`:
- **`cvd_absorption_5m` strict (`json:19-50`)**: IS `h=1`: `n=2029, mean=-0.00087%, hit=48.74%`; IS `h=20`: `n=2028, mean=-0.01715%, hit=50.39%`. OOS `h=1`: `n=797, mean=-0.00491%, hit=47.18%`; OOS `h=20`: `n=797, mean=+0.00404%, hit=50.69%`.
- **`cvd_absorption_5m` legacy (`json:294-325`)**: IS `h=1`: `n=1835, mean=+0.00341%, hit=48.12%`; IS `h=20`: `n=1834, mean=-0.01849%, hit=48.91%`. OOS `h=1`: `n=732, mean=-0.00784%, hit=46.04%`; OOS `h=20`: `n=732, mean=-0.00085%, hit=49.04%`.
- **`escalation_5m` strict (`json:63-94`)**: IS `h=1`: `n=2244, mean=+0.00751%, hit=38.41%`; IS `h=20`: `n=2244, mean=+0.04004%, hit=41.13%`. OOS `h=1`: `n=1065, mean=+0.00087%, hit=45.26%`; OOS `h=20`: `n=1065, mean=+0.03361%, hit=46.95%`.
- **`escalation_5m` legacy (`json:338-369`)**: IS `h=1`: `n=9556, mean=-0.00093%, hit=41.45%`; IS `h=20`: `n=9556, mean=+0.01690%, hit=41.09%`. OOS `h=1`: `n=3913, mean=-0.00388%, hit=43.42%`; OOS `h=20`: `n=3913, mean=+0.00471%, hit=43.52%`.
- **`cvd_absorption_15m` strict (`json:110-141`)**: IS `h=1`: `n=371, mean=-0.00121%, hit=48.52%`; IS `h=20`: `n=371, mean=-0.02608%, hit=48.25%`. OOS `h=1`: `n=154, mean=-0.01150%, hit=51.30%`; OOS `h=20`: `n=154, mean=+0.06870%, hit=51.95%`.
- **`cvd_absorption_15m` legacy (`json:385-416`)**: IS `h=1`: `n=1133, mean=+0.00882%, hit=49.60%`; IS `h=20`: `n=1133, mean=+0.00037%, hit=48.98%`. OOS `h=1`: `n=506, mean=+0.00039%, hit=47.63%`; OOS `h=20`: `n=506, mean=+0.01425%, hit=49.01%`.
- **`escalation_15m` strict (`json:154-185`)**: IS `h=1`: `n=812, mean=+0.01031%, hit=38.79%`; IS `h=20`: `n=812, mean=+0.00633%, hit=39.29%`. OOS `h=1`: `n=291, mean=+0.02692%, hit=40.89%`; OOS `h=20`: `n=290, mean=+0.13163%, hit=47.24%`.
- **`escalation_15m` legacy (`json:429-460`)**: IS `h=1`: `n=1527, mean=+0.02526%, hit=41.85%`; IS `h=20`: `n=1527, mean=+0.09795%, hit=44.79%`. OOS `h=1`: `n=501, mean=-0.01024%, hit=45.51%`; OOS `h=20`: `n=501, mean=+0.02970%, hit=42.51%`.
- **`cvd_absorption_1h` strict (`json:201-232`)**: IS `h=1`: `n=52, mean=+0.01313%, hit=55.77%`; IS `h=20`: `n=52, mean=+0.55017%, hit=55.77%`. OOS `h=1`: `n=18, mean=+0.17710%, hit=66.67%`; OOS `h=20`: `n=18, mean=-0.18846%, hit=33.33%`.
- **`cvd_absorption_1h` legacy (`json:476-507`)**: IS `h=1`: `n=142, mean=-0.00350%, hit=48.59%`; IS `h=20`: `n=142, mean=+0.11456%, hit=49.30%`. OOS `h=1`: `n=80, mean=-0.04832%, hit=40.00%`; OOS `h=20`: `n=79, mean=+0.24630%, hit=48.10%`.
- **`escalation_1h` strict (`json:245-276`)**: IS `h=1`: `n=5, mean=+0.24869%, hit=40.00%`; IS `h=20`: `n=5, mean=+1.56743%, hit=60.00%`. OOS `h=1,5,20`: `n=0, mean=null, hit=null`.
- **`escalation_1h` legacy (`json:520-551`)**: IS `h=1`: `n=92, mean=+0.05783%, hit=46.74%`; IS `h=20`: `n=91, mean=+0.00089%, hit=39.56%`. OOS `h=1`: `n=22, mean=-0.02177%, hit=31.82%`; OOS `h=20`: `n=22, mean=-1.00247%, hit=40.91%`.

---

## 5. Earlier Full-Period (`2022-01-01..2026-09-26`) Tables Check (`FABIO_L1_REPORT.md:29-89`)

As documented in `FABIO_L1_REPORT.md:3-6,95-96`, the upper tables (`FABIO_L1_REPORT.md:31-62,79-86`) came from the earlier `2022-01-01..2026-09-26` (`2,491,200` 1m bars) legacy run whose raw dump (`Dumps/backtest/runs/fabio_l1/`) is gitignored. Checking internal consistency of every reported metric in `FABIO_L1_REPORT.md:31-86` (all **OURS**):
- **Gross-to-Net Fee Subtraction (`0.10%`)**:
  - `cvd_absorption 5m` (`FABIO_L1_REPORT.md:33`): `h5` `+0.000% - 0.100% = -0.100%`; `h20` `+0.001% - 0.100% = -0.099%` (MATCH).
  - `cvd_absorption 15m` (`FABIO_L1_REPORT.md:34`): `h5` `+0.001% - 0.100% = -0.099%`; `h20` `-0.009% - 0.100% = -0.109%` (MATCH).
  - `cvd_absorption 1h` (`FABIO_L1_REPORT.md:35`): `h5` `-0.042% - 0.100% = -0.142%`; `h20` `+0.001% - 0.100% = -0.099%` (MATCH).
  - `escalation 5m` (`FABIO_L1_REPORT.md:36`): `h5` `-0.004% - 0.100% = -0.104%`; `h20` `+0.029% - 0.100% = -0.071%` (MATCH).
  - `escalation 15m` (`FABIO_L1_REPORT.md:37`): `h5` `-0.069% - 0.100% = -0.169%`; `h20` `-0.139% - 0.100% = -0.239%` (MATCH).
  - `escalation 1h` (`FABIO_L1_REPORT.md:38,45,85,119`): `h5` `+0.213% - 0.100% = +0.113%`; `h20` `-0.000% - 0.100% = -0.100%`; `n=182, hit=48.4%, PBO=0.756` (MATCH across table and prose).
- **Volume FVG Bounce vs Through Sign Symmetry (`FABIO_L1_REPORT.md:51-58`, `run_backtest.py:217-218`)**:
  - `5m` (`58482` legs): Real IS `2660 / -0.013%` vs `+0.013%`; Real OOS `1228 / +0.011%` vs `-0.011%`; Control IS `2699 / -0.004%` vs `+0.004%`; Control OOS `1222 / -0.003%` vs `+0.003%` (exact mirror images, MATCH).
  - `15m` (`19782` legs): Real IS `823 / +0.004%` vs `-0.004%`; Real OOS `377 / -0.002%` vs `+0.002%`; Control IS `825 / +0.010%` vs `-0.010%`; Control OOS `379 / +0.027%` vs `-0.027%` (exact mirror images, MATCH).
  - `1h` (`5000` legs): Real IS `186 / +0.062%` vs `-0.062%`; Real OOS `93 / +0.274%` vs `-0.274%`; Control IS `189 / +0.134%` vs `-0.134%`; Control OOS `91 / +0.130%` vs `-0.130%` (exact mirror images, MATCH).

---

## 6. Final Verdict

Every metric reported in `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md` for the strict-detector rerun (`FABIO_L1_REPORT.md:90-121`) matches `MyTradingSys/backtest/layers/fabio/fabio_l1_strict_rerun.json` (`1-559`) and `MyTradingSys/backtest/layers/fabio/run_backtest.py` (`1-296`) with zero discrepancies.

VERDICT: MATCH

## Claude spot-check

Checked by Claude (Builder, gem-review-three-1104) with a short Python script that parses `fabio_l1_strict_rerun.json` (branch `gemini-q/gemini-blind-read-fabio-l1-strict-1104`). The JSON holds the gross mean return; fee-net = mean - 0.001 (round trip). Compared against this read and against `FABIO_L1_REPORT.md`.

| # | Number | JSON path | Recomputed | Read / report | Verdict |
|---|---|---|---|---|---|
| 1 | Strict cvd_absorption 5m, OOS h=5: n, gross, net, PBO | `strict.cvd_absorption_5m.oos_stats.5`, `.pbo` | n 797, gross +0.0113%, net -0.0887% -> -0.089, PBO 0.882 | +0.011 / -0.089, PBO 0.882 | AGREE |
| 2 | Escalation 1h strict vs legacy, total IS events | `strict.escalation_1h`, `legacy.escalation_1h` `total_is_events_all_variants` | 117 vs 2523; reduction 95.36% | 117, 2,523, "about 95% fewer" | AGREE |
| 3 | Strict cvd_absorption 1h: IS and OOS h=5, OOS hit, PBO | `is_stats.5`, `oos_stats.5`, `.pbo` | IS n 52, gross +0.2500%; OOS n 18, net +0.0542% -> +0.054, hit 55.56%, PBO 0.5617 | +0.250, +0.054, 55.6%, PBO 0.56 | AGREE |
| 4 | Escalation 15m strict vs legacy, total IS events | `strict.escalation_15m`, `legacy.escalation_15m` | 3775 vs 28910 | 3,775 vs 28,910 | AGREE |
| 5 | Strict escalation 5m, OOS h=5: n, gross, net, PBO | `strict.escalation_5m.oos_stats.5`, `.pbo` | n 1065, gross +0.0334%, net -0.0666% -> -0.067, PBO 0.171 | +0.033 / -0.067, PBO 0.17 | AGREE |

Result: 5 of 5 AGREE. The card is closed.

Path check: all 3 `MyTradingSys/...` paths the read cites exist on its branch. The branch changes only the read, its layer-lab report and its card json. No study file changed.
