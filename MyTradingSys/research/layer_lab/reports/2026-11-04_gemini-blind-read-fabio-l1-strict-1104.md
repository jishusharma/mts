# Layer Lab Report: `gemini-blind-read-fabio-l1-strict-1104`

- **Card**: `gemini-blind-read-fabio-l1-strict-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_FABIO_L1_1104.md`
- **Audited Files**:
  - `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md` (`1-121`)
  - `MyTradingSys/backtest/layers/fabio/fabio_l1_strict_rerun.json` (`1-559`)
  - `MyTradingSys/backtest/layers/fabio/run_backtest.py` (`1-296`)
- **Verdict**: `VERDICT: MATCH` (`DIFF=0` across all strict and legacy DEV rerun metrics in `fabio_l1_strict_rerun.json`).

## Findings

1. **Parameter & Metric Labels (`OURS` vs `SOURCED`)**:
   - Per `FABIO_L1_REPORT.md:10` (`"All thresholds are UNDEFINED in the video, hence the grids"`) and `run_backtest.py:5-7` (`"over a grid of their UNDEFINED-in-source parameters"`), all grid parameters (`CVD_GRID` in `run_backtest.py:161`, `ESCALATION_GRID` in `run_backtest.py:162-165`), Volume FVG parameters (`n_bins=20, pct=0.70, left=2, right=2, max_wait=200` in `run_backtest.py:191,198,207`), chunking parameters (`own=1000, warm=500` in `run_backtest.py:89`), split (`is_frac=0.70` in `run_backtest.py:64`), horizons (`(1, 5, 20)` in `run_backtest.py:43`), fee (`0.001` round-trip in `run_backtest.py:42` and `fabio_l1_strict_rerun.json:5`), and realized backtest metrics are **OURS**.
2. **100% Match on Strict vs Legacy Rerun (`FABIO_L1_REPORT.md:90-121` vs `fabio_l1_strict_rerun.json:1-559`)**:
   - **Window & Commit**: `DEV 2022-01-01..2024-06-30`, `1,313,280` 1m bars, detector commit `2afc18be6`, round-trip fee `0.10%` (`0.001`) match `fabio_l1_strict_rerun.json:3-5` (`FABIO_L1_REPORT.md:90-97`).
   - **All 12 Rerun Table Rows (`FABIO_L1_REPORT.md:101-112`)**: Chosen parameters, IS `n`, IS `h=5` mean return, OOS `n` (`h=5`), OOS `h=5` gross and net mean returns, OOS `h=5` hit rate, PBO, and verdict match `fabio_l1_strict_rerun.json:9-556` with zero discrepancies:
     - `cvd_absorption 5m strict` (`json:9-52`): `w5, tol 0.2%`, IS `2029 / -0.001%` (`-0.0014%`), OOS `797`, `+0.011% / -0.089%` (`+0.0113% / -0.0887%`), hit `49.7%` (`49.69%`), PBO `0.882` (`0.8820`), `no edge`.
     - `cvd_absorption 5m legacy` (`json:284-327`): `w5, tol 0.1%`, IS `1835 / +0.008%` (`+0.0081%`), OOS `732`, `+0.013% / -0.087%` (`+0.0133% / -0.0867%`), hit `47.8%` (`47.81%`), PBO `0.693` (`0.6926`), `no edge`.
     - `cvd_absorption 15m strict` (`json:100-143`): `w2, tol 0.05%`, IS `371 / +0.002%` (`+0.0021%`), OOS `154`, `-0.008% / -0.108%` (`-0.0078% / -0.1078%`), hit `43.5%` (`43.51%`), PBO `0.760` (`0.7597`), `no edge`.
     - `cvd_absorption 15m legacy` (`json:375-418`): `w3, tol 0.2%`, IS `1133 / -0.009%` (`-0.0093%`), OOS `506`, `-0.022% / -0.122%` (`-0.0217% / -0.1217%`), hit `48.2%` (`48.22%`), PBO `0.685` (`0.6851`), `no edge`.
     - `cvd_absorption 1h strict` (`json:191-234`): `w2, tol 0.05%`, IS `52 / +0.250%` (`+0.2500%`), OOS `18`, `+0.154% / +0.054%` (`+0.1542% / +0.0542%`), hit `55.6%` (`55.56%`), PBO `0.562` (`0.5617`), `insufficient n (18 < 30)`.
     - `cvd_absorption 1h legacy` (`json:466-509`): `w5, tol 0.2%`, IS `142 / +0.081%` (`+0.0813%`), OOS `80`, `+0.008% / -0.092%` (`+0.0080% / -0.0920%`), hit `55.0%` (`55.00%`), PBO `0.623` (`0.6234`), `no edge`.
     - `escalation 5m strict` (`json:53-96`): `lt 0.2%, k 3, lb 50`, IS `2244 / +0.040%` (`+0.0401%`), OOS `1065`, `+0.033% / -0.067%` (`+0.0334% / -0.0666%`), hit `45.3%` (`45.26%`), PBO `0.171` (`0.1710`), `no edge (net < 0)`.
     - `escalation 5m legacy` (`json:328-371`): `lt 0.2%, k 3, lb 50`, IS `9556 / +0.024%` (`+0.0242%`), OOS `3913`, `+0.004% / -0.096%` (`+0.0040% / -0.0960%`), hit `43.8%` (`43.83%`), PBO `0.893` (`0.8929`), `no edge`.
     - `escalation 15m strict` (`json:144-187`): `lt 0.2%, k 1.5, lb 20`, IS `812 / +0.007%` (`+0.0070%`), OOS `291`, `+0.021% / -0.079%` (`+0.0207% / -0.0793%`), hit `47.8%` (`47.77%`), PBO `0.286` (`0.2857`), `no edge (net < 0)`.
     - `escalation 15m legacy` (`json:419-462`): `lt 0.1%, k 1.5, lb 50`, IS `1527 / +0.061%` (`+0.0613%`), OOS `501`, `-0.073% / -0.173%` (`-0.0730% / -0.1730%`), hit `47.7%` (`47.70%`), PBO `0.605` (`0.6050`), `no edge`.
     - `escalation 1h strict` (`json:235-278`): `lt 0.1%, k 1.5, lb 20`, IS `5 / +0.055%` (`+0.0553%`), OOS `0`, `n/a`, hit `n/a`, PBO `0.772` (`0.7716`), `insufficient n (OOS 0)`.
     - `escalation 1h legacy` (`json:510-553`): `lt 0.1%, k 3, lb 20`, IS `92 / +0.013%` (`+0.0126%`), OOS `22`, `-0.257% / -0.357%` (`-0.2574% / -0.3574%`), hit `31.8%` (`31.82%`), PBO `0.374` (`0.3745`), `insufficient n (22 < 30)`.
   - **Variant Event Sums & Volume FVG Parity (`FABIO_L1_REPORT.md:97,114-115`)**:
     - `escalation 1h`: `117` (`7` of `12` variants qualifying, `json:242-243`) vs `2,523` (`12` of `12`, `json:517-518`), a `95.36%` reduction (`"about 95% fewer"`, `FABIO_L1_REPORT.md:117`).
     - `escalation 15m`: `3,775` (`json:152`) vs `28,910` (`json:427`).
     - `escalation 5m`: `33,676` (`json:61`) vs `125,915` (`json:336`).
     - `cvd_absorption 1h`: `1,498` (`json:199`) vs `2,749` (`json:474`).
     - `volume_fvg` leg counts: `31,290` (`5m`, `json:98,373`), `10,598` (`15m`, `json:189,464`), `2,689` (`1h`, `json:280,555`), identical across `strict` and `legacy`.
