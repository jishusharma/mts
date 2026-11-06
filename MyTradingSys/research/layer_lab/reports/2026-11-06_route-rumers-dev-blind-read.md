# Gemini Blind Read Report: Rumers DEV Check 5 Frozen Rules (2026-11-06)

- **Card**: `route-rumers-dev-blind-read` [SOURCED: route-rumers-dev-blind-read.json:13]
- **Audited Target**: `MyTradingSys/research/rumers_2026-11-01/DEV_CHECK.md` [SOURCED: DEV_CHECK.md:1-74]
- **Raw JSON Data Sources**:
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift+0.json` (143 lines) [SOURCED: dev_shift+0.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift+1.json` (143 lines) [SOURCED: dev_shift+1.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift-1.json` (143 lines) [SOURCED: dev_shift-1.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_count.json` (64 lines) [SOURCED: dev_count.json:1-64]
- **Audit Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_RUMERS_DEV_1104.md`
- **Date**: 2026-11-06 (UTC)
- **Status**: VERDICT: MATCH (`FOUND=75 DIFF=0 NOT_IN_DATA=0`)

## 1. Summary of Findings

1. **Reconciliation Match**: Every table and headline metric in `DEV_CHECK.md` reproduces exactly from the raw simulation JSON files across all 75 checked numbers.
2. **Shift 0 Results (Execution at Signal Close)**:
   - **R1** (`RUMERS-ORB-MANIP-REVERSAL`): n=32, hit-rate=0.344, mean net R=-0.304 R, SE=0.684, p=0.6567, Holm p=1.0000 -> **INCONCLUSIVE** (n >= 30, n < 100). [SOURCED: dev_shift+0.json:39-56]
   - **R2** (`RUMERS-BOX-PDH-PDL-FADE`): n=632, hit-rate=0.259, mean net R=-0.073 R, SE=0.124, p=0.5588, Holm p=1.0000 -> **FAIL** (mean <= 0, n >= 100). [SOURCED: dev_shift+0.json:59-76]
   - **R3** (`RUMERS-VWAP-SEPARATOR-MEAN-REVERSION`): n=4433, hit-rate=0.272, mean net R=-0.566 R, SE=0.081, p=2.13e-12, Holm p=1.05e-11 -> **FAIL** (mean <= 0, n >= 100). [SOURCED: dev_shift+0.json:79-97]
   - **R4** (`RUMERS-ORR-25PCT-ATR-SWEEP`): n=26, hit-rate=0.615, mean net R=0.073 R, SE=0.165, p=0.6578, Holm p=1.0000 -> **NOT ENOUGH DATA** (n < 30). [SOURCED: dev_shift+0.json:100-117]
   - **R5** (`RUMERS-MAGIC-LINE-PITCHFORK-REVERSAL`): n=2177, hit-rate=0.517, mean net R=-0.167 R, SE=0.024, p=2.10e-12, Holm p=1.05e-11 -> **FAIL** (mean <= 0, n >= 100). [SOURCED: dev_shift+0.json:120-140]
   - **PASS-DEV Count**: Exactly **0 PASS-DEV** at shift 0. [SOURCED: DEV_CHECK.md:70]
3. **Audit of R2 Shift -1 Anomaly (49.658 R Mean)**:
   - In `dev_shift-1.json:61`, R2 shows a mean net R of 49.658 R with SE of 18.223 R across 618 trades.
   - Analysis confirms this is an artificial denominator artifact of the lookahead leak probe: entering at the 1m open of the signal bar when the open is virtually coincident with the wick stop level creates a microscopic risk distance `|entry - stop|` (down to 1 tick = 0.1 USDT). Dividing target profits by ~0 causes astronomical R returns on winning trades, despite a low hit rate of 26.38%.
   - At shift 0 (unbiased closed-bar entry), R2 mean net R drops to -0.073 R with Holm p=1.0000 (FAIL).
4. **Feeder Route / Conclusion**:
   - Confirmed 0 PASS-DEV across all 5 frozen rules on DEV data (2022-04-01..2024-06-30).
   - No Rumers rule earns a VALIDATION read. The study is closed with no edge.
   - Next route: `END: 0 PASS-DEV on rumers DEV check (5 frozen rules, DEV 2022-04..2024-06); study closed with 0 DEV passes`.

## 2. Key Figures Reconciliation Summary

| Metric | `DEV_CHECK.md` Citation | JSON File & Line | Label | Status |
|---|---|---|---|---|
| R1 Shift 0 net R | `DEV_CHECK.md:11` (`-0.304`) | `dev_shift+0.json:41` (`-0.303949`) | SOURCED | MATCH |
| R2 Shift 0 net R | `DEV_CHECK.md:12` (`-0.073`) | `dev_shift+0.json:61` (`-0.072746`) | SOURCED | MATCH |
| R3 Shift 0 net R | `DEV_CHECK.md:13` (`-0.566`) | `dev_shift+0.json:81` (`-0.565966`) | SOURCED | MATCH |
| R4 Shift 0 net R | `DEV_CHECK.md:14` (`0.073`) | `dev_shift+0.json:102` (`0.073115`) | SOURCED | MATCH |
| R5 Shift 0 net R | `DEV_CHECK.md:15` (`-0.167`) | `dev_shift+0.json:122` (`-0.166756`) | SOURCED | MATCH |
| R2 Shift -1 net R | `DEV_CHECK.md:12` (`49.658`) | `dev_shift-1.json:61` (`49.658032`) | SOURCED | MATCH (Leak probe artifact) |
| R1 Shift +1 net R | `DEV_CHECK.md:11` (`-0.141`) | `dev_shift+1.json:41` (`-0.140695`) | SOURCED | MATCH |
| R2 Shift +1 net R | `DEV_CHECK.md:12` (`-0.728`) | `dev_shift+1.json:61` (`-0.728168`) | SOURCED | MATCH |
| R3 Shift +1 net R | `DEV_CHECK.md:13` (`-1.224`) | `dev_shift+1.json:81` (`-1.224471`) | SOURCED | MATCH |
| R4 Shift +1 net R | `DEV_CHECK.md:14` (`0.026`) | `dev_shift+1.json:102` (`0.025987`) | SOURCED | MATCH |
| R5 Shift +1 net R | `DEV_CHECK.md:15` (`-0.289`) | `dev_shift+1.json:122` (`-0.289435`) | SOURCED | MATCH |
| R1 Triggers & Traded | `DEV_CHECK.md:23` (`96`, `32`) | `dev_count.json:40`, `dev_shift+0.json:39` | SOURCED | MATCH |
| R2 Triggers & Traded | `DEV_CHECK.md:24` (`658`, `632`) | `dev_count.json:45`, `dev_shift+0.json:59` | SOURCED | MATCH |
| R3 Triggers & Traded | `DEV_CHECK.md:25` (`6534`, `4433`) | `dev_count.json:50`, `dev_shift+0.json:79` | SOURCED | MATCH |
| R4 Triggers & Traded | `DEV_CHECK.md:26` (`38`, `26`) | `dev_count.json:55`, `dev_shift+0.json:100` | SOURCED | MATCH |
| R5 Triggers & Traded | `DEV_CHECK.md:27` (`5262`, `2177`) | `dev_count.json:60`, `dev_shift+0.json:120` | SOURCED | MATCH |
| R4 Longs share | `DEV_CHECK.md:36` (`12 of 26 = 0.46`) | `dev_shift+0.json:100,112` (`12/26=0.4615`) | SOURCED | MATCH |
| PASS-DEV count | `DEV_CHECK.md:70` (`none`) | `dev_shift+0.json:rules` (0 PASS-DEV) | OURS | MATCH |

Verification Command:
`python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_RUMERS_DEV_1104.md'); assert p.exists() and 'VERDICT: MATCH' in p.read_text()"`
