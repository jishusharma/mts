# Layer Lab Report: Blind Re-read of bb_dance_2026-10-30 RESULT.md Numbers vs output.txt

- **Task**: `gemini-blind-read-bb-dance-1103`
- **Lane**: `CODEX`
- **Audited Document**: `MyTradingSys/research/bb_dance_2026-10-30/RESULT.md`
- **Underlying Sources**:
  - `MyTradingSys/research/bb_dance_2026-10-30/output.txt`
  - `MyTradingSys/research/bb_dance_2026-10-30/live_output.txt` (cited on `RESULT.md:40`)
  - `MyTradingSys/research/bb_dance_2026-10-30/study.py` (cited on `RESULT.md:3`)
  - `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/costs.csv` (round-trip cost benchmark on `RESULT.md:38`)
- **Date**: 2026-11-03
- **Auditor**: Gemini 4 Argon (Low) worker

---

## 1. Executive Summary

Complete blind re-read and numerical verification of every quoted number (counts, percentages, sample sizes `n`, prices, `%b` ratios, bar intervals, timestamps, and dates) in `MyTradingSys/research/bb_dance_2026-10-30/RESULT.md` (`OURS`).

- **Total Numbers / Claims Audited**: 87 (`OURS`)
- **FOUND**: 85 (`OURS`: 46 in `output.txt` directly; 29 in `live_output.txt` cited on `RESULT.md:40`; 9 in `study.py` cited on `RESULT.md:3`; 1 in `T06/costs.csv:52-54`)
- **NOT_IN_DATA**: 2 (`OURS`: `15m` and `1h` on `RESULT.md:60`, which are proposed follow-up timeframes in `## Open` and not evaluated in `output.txt`)
- **DIFF**: 0 (`OURS`)

*(Note: If evaluated strictly against `output.txt` alone without `live_output.txt` or `study.py`, the breakdown across the 87 rows is **FOUND: 46, NOT_IN_DATA: 41, DIFF: 0**).*

---

## 2. Findings by Section

### 1. Header & Sample (`RESULT.md:1-5`)
- **Definitions & Data**: `1m` archive built into `5m` bars, DEV `2022-2025` only (`study.py:4-5,24,29-31`, `OURS`).
- **Sample Size**: `11,051` shorts that started on a `5m` close below the mid and touched the lower band (`output.txt:1`: `shorts with a lower-band touch: 11051`, `OURS`).

### 2. Section 1: Distance from the Band vs Candle Count (`RESULT.md:7-23`)
- **Table 1 (`RESULT.md:11-18` vs `output.txt:4-11`, all `OURS`)**:
  - `k=1`: near (`%b < 0.25`) `59%` (`0.594`), `n = 6,360` (`6360`); away (`%b >= 0.25`) `32%` (`0.319`), `n = 3,353` (`3353`) (`output.txt:6`).
  - `k=2`: near `59%` (`0.587`), `n = 4,528` (`4528`); away `31%` (`0.307`), `n = 3,934` (`3934`) (`output.txt:7`).
  - `k=3`: near `60%` (`0.604`), `n = 3,302` (`3302`); away `29%` (`0.290`), `n = 3,982` (`3982`) (`output.txt:8`).
  - `k=4`: near `60%` (`0.598`), `n = 2,490` (`2490`); away `29%` (`0.285`), `n = 3,721` (`3721`) (`output.txt:9`).
  - `k=5`: near `63%` (`0.628`), `n = 1,929` (`1929`); away `27%` (`0.267`), `n = 3,315` (`3315`) (`output.txt:10`).
  - `k=6`: near `64%` (`0.641`), `n = 1,474` (`1474`); away `26%` (`0.263`), `n = 2,874` (`2874`) (`output.txt:11`).
- **Reading (`RESULT.md:20-23`, `OURS`)**: Near band ~`60%` (`0.594..0.641`), away from band ~`30%` (`0.263..0.319`), `%b = 0` on lower band and `0.5` on mid (`study.py:9,21`).

### 3. Section 2: Exits Compared (`RESULT.md:25-38`)
- **Table 2 (`RESULT.md:27-32` vs `output.txt:13-17`, all `n = 11,051`, `OURS`)**:
  - `First close back inside after a touch` (`X0_first_close_inside`): Mean `+0.178%` (`0.178`), Median `+0.094%` (`0.094`), Share > 0 `76%` (`0.755`) (`output.txt:14`).
  - `Three bars without a touch` (`Xk3_three_bars_no_touch`): Mean `+0.178%` (`0.178`), Median `+0.067%` (`0.067`), Share > 0 `64%` (`0.636`) (`output.txt:15`).
  - `First close with %b >= 0.25` (`Xfar_close_pb_ge_025`): Mean `+0.172%` (`0.172`), Median `+0.062%` (`0.062`), Share > 0 `69%` (`0.687`) (`output.txt:16`).
  - `Close above the mid (hold)` (`Xmid_close_above_mid`): Mean `+0.168%` (`0.168`), Median `+0.005%` (`0.005`), Share > 0 `51%` (`0.512`) (`output.txt:17`).
- **Reading (`RESULT.md:38`, `OURS`)**: All four means under `+0.2%` gross against `0.12%` round-trip cost (`T06/costs.csv:52-54`).

### 4. Section 3: The 10-29 Case (`RESULT.md:40-56` vs `live_output.txt:13-41`)
- **Entry & Touches (`RESULT.md:42-44`, `OURS`)**: `20:00` close `80,412` below mid `80,798` (`live_output.txt:13`); touches on every bar `20:00` to `21:00` except `20:25` (`live_output.txt:13-25`); `20:50` `%b 0.02` (`live_output.txt:23`); last touch `21:00` (`live_output.txt:25`).
- **Fade & Low (`RESULT.md:46-49`, `OURS`)**: `21:05` `%b 0.21` (`live_output.txt:26`, `59%` in `output.txt:6`); `21:10` `%b 0.25` (`live_output.txt:27`, `31%` in `output.txt:7`); `21:15..21:55` `%b 0.30-0.46` (`live_output.txt:28-36`); `22:00-22:10` `%b 0.11-0.21` (`live_output.txt:37-39`); `22:05` low `78,627` above `20:45` low `78,297` (`live_output.txt:22,38`).
- **Table 3 (`RESULT.md:52-56`, `OURS`)**:
  - `%b >= 0.25` at `21:10`: price `79,225`, gain `(80412 - 79225) / 80412 = +1.476%` -> `+1.48%` (`live_output.txt:13,27`).
  - `Three bars without a touch` at `21:15`: price `79,567`, gain `(80412 - 79567) / 80412 = +1.051%` -> `+1.05%` (`live_output.txt:13,28`).
  - `Close above the mid` at `22:20`: price `79,166` (mid `79,137`), gain `(80412 - 79166) / 80412 = +1.550%` -> `+1.55%` (`live_output.txt:13,41`).

---

## 3. Primary Audit File

The complete 87-row verification table is recorded at:
`MyTradingSys/research/gemini_audits_2026-11-03/bb_dance_blind_read.md`

Noticed: Every empirical number in `RESULT.md` Sections 1 and 2 (46 numbers) matches `output.txt` (`output.txt:1-17`) with 0 `DIFF`, and all 29 spot case numbers in Section 3 match `live_output.txt` (`live_output.txt:13-41`), which is explicitly cited in the Section 3 header (`RESULT.md:40`).
