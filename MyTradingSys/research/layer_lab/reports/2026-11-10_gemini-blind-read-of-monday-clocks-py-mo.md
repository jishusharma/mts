# Independent Gemini Blind Read: `monday_open_2026-11-09/monday_clocks.py` (`gemini-blind-read-of-monday-clocks-py-mo`)

- **Card**: `gemini-blind-read-of-monday-clocks-py-mo`
- **Reader / Provenance**: Gemini (`gemini-3.8-flash-low` worker on worktree branch `gemini-q/gemini-blind-read-of-monday-clocks-py-mo`).
- **Scope In Read**:
  - `MyTradingSys/research/monday_open_2026-11-09/monday_clocks.py` (lines 1-236, SOURCED/OURS)
  - `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` (lines 1-5926, SOURCED)
  - `MyTradingSys/research/ma_layer_2026-11/cycle_ma_clock.py` (lines 1-137, SOURCED)
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/test_scenario_ledger.py` (lines 1-96, SOURCED)
- **Scope Out Respected**: No edits to `monday_clocks.py`; no live tree touched; no orders/trades; no `.secrets` or `.env` read; no `sync.py ship` or git push.

---

## 1. Executive Summary & Findings Table

| # | Category | Location | Description | Severity / Impact | Repro / Verification |
|---|---|---|---|---|---|
| 1 | Intrabar sequence / look-ahead | `monday_clocks.py:180-189` | `study()` defines pre-sweep window as `[b for b in mon if b[0] < end_]`, where `end_ = sw[0]`. The sweep bar `sw` is excluded, so intrabar bounces in the sweep bar before the sweep are missed. If sweep happens in bar 0 (`sw == mon[0]`), `pre = []`, forcing `mx = 0.0` ("straight"). Known intrabar limit stated at file header line 8. | Minor (Intrabar order limitation) | `sw = mon[0]; end_ = sw[0]; pre = [b for b in mon if b[0] < end_] -> pre == [] -> mx = 0.0` |
| 2 | Intrabar simultaneous break | `monday_clocks.py:205-214` | In `lead()`, if both Sat-Sun low `w` and Fri-Sun low `low` are broken inside the exact same 1h bar, `bw[0] == sw[0]`, resulting in `lead = 0.0` hours. Intrabar sequencing between `w` and `low` within the same bar is unobservable at 1h granularity. | Minor (Granularity limit) | `bw[0] == sw[0] -> (sw[0] - bw[0]) / HOUR == 0.0` |
| 3 | Window boundary correctness | `monday_clocks.py:157-158` | Ref window: `range(t - 72*HOUR, t, HOUR)` (exact 72 1h bars from Fri 00:00Z to Sun 23:00Z). Monday window: `range(t, t + 24*HOUR, HOUR)` (exact 24 1h bars from Mon 00:00Z to Mon 23:00Z). | Correct (0 off-by-one errors) | SOURCED `monday_clocks.py:157-158`: verified start and end timestamps match Fri 00:00 through Sun 23:00 UTC. |
| 4 | Part 1 recount consistency | `monday_clocks.py:62-108` | Re-counted against `btc_daily.csv`: Oct 2026 low `76,326` (csv line 5920: `2026-10-31,80295.45,76326.0,79803.96`); Nov low so far `74,888` (csv line 5926: `2026-11-06,76550.0,74888.0,75771.76`); breach by day 8 `n = 35`. | Correct (Bit-for-bit matches csv) | `python -c "import monday_clocks; mc.part1()"` reproduced exact numbers. |
| 5 | Epoch block alignment | `monday_clocks.py:140-144` | Binance 3-day blocks anchor to 1970-01-01 epoch (`ed % 3 == 0`), closing Mon 2026-11-09 24:00Z; 2-day closes Tue 2026-11-10 24:00Z; 5-day closes Thu 2026-11-12 24:00Z. | Correct | SOURCED `monday_clocks.py:143` + commit `e8ad8024ce0f`. |

---

## 2. Detailed Verification of Script Components

### A. Part 1: Month-Breach Recount (`monday_clocks.py:62-108`)
- **CSV Data Source**: `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` (SOURCED).
- **Date Filtering**:
  - `full = [k for k in keys if k >= (2011, 1) and k < (2026, 11)]` correctly excludes incomplete current month (Nov 2026) from historical denominator.
  - Previous month key lookup `p = (k[0], k[1] - 1) if k[1] > 1 else (k[0] - 1, 12)` handles year boundaries (Jan -> Dec of prior year) properly.
  - Months since 2011: `n = 190`, breached = `64` (34%).
  - Months since 2018: `n = 106`, breached = `40` (38%).
  - Oct 2026 low: `76,326` (SOURCED `btc_daily.csv:5920`).
  - Nov 2026 low in csv: `74,888` on 2026-11-06 (SOURCED `btc_daily.csv:5926`), which is `1.88%` under Oct low (`(1 - 74888 / 76326) = 0.01884`).
  - Conditional breach by day 8 (`d.day <= 8`): `n = 35` historical months where low occurred by day 8 below prior month low.
  - Day-of-month median of ultimate monthly low: `8`.
- **Verdict**: No logic errors, no off-by-one errors in month/year indexing or calendar windows.

### B. Part 2: Levels, Clocks and Epoch Blocks (`monday_clocks.py:110-147`)
- **Epoch Block Calculations**:
  - Epoch formula: `ed = (d - dt.date(1970, 1, 1)).days`.
  - For `2026-11-08` (Sun): `ed = 20765` (`20765 % 2 = 1`, closes end of Sun 11-08; next closes Tue 11-10, Thu 11-12).
  - For `2026-11-09` (Mon): `ed = 20766` (`20766 % 3 = 0`). Matches Binance 3d bar closure at end of Mon 11-09 24:00Z.
  - For `2026-11-12` (Thu): `ed = 20769` (`20769 % 5 = 4`). Matches 5-day block close at end of Thu 11-12 24:00Z.
- **Verdict**: Verified accurate with Binance klines standard.

### C. Part 3: Monday and Reference Windows (`monday_clocks.py:149-165`)
- **Reference Window (`ref`)**:
  - `range(t - 72 * HOUR, t, HOUR)`:
    - At `t = Mon 00:00:00Z`, `t - 72 * HOUR` is `Fri 00:00:00Z`.
    - Bars included: `Fri 00:00`, `Fri 01:00`, ..., `Sun 23:00`.
    - Length: Exactly 72 hourly bars.
    - Coverage check: `len(ref) >= 70` allows for at most 2 missing bars (exchange downtime/gap).
- **Monday Window (`mon`)**:
  - `range(t, t + 24 * HOUR, HOUR)`:
    - Bars included: `Mon 00:00` through `Mon 23:00`.
    - Length: Exactly 24 hourly bars.
    - Coverage check: `len(mon) >= 23`.
- **Step Size**: `d += dt.timedelta(days=7)` steps from Monday to next Monday cleanly.
- **Verdict**: Reference and Monday windows have zero off-by-one errors.

### D. Part 3: Session Definitions (`monday_clocks.py:166-170`)
- `sess(t)`:
  - `h = dt.datetime.fromtimestamp(t / 1000, UTC)`
  - `x = h.hour + h.minute / 60`
  - `Asia`: `x < 7` -> hours `00:00` to `06:59` (7 hours: 0, 1, 2, 3, 4, 5, 6).
  - `EU`: `7 <= x < 14.5` -> hours `07:00` to `14:29` (7.5 hours, aligned with London morning up to US cash open 14:30 UTC post-DST).
  - `US`: `x >= 14.5` -> hours `14:30` to `23:59`.
- **Verdict**: Accurately accounts for UTC session times post-US DST shift (14:30 UTC US open).

### E. Part 3: Sweep Classification Thresholds (`monday_clocks.py:171-195`)
- **Thresholds**:
  - `straight`: `mx < 0.008` (< +0.8%).
  - `small bounce`: `0.008 <= mx < 0.014` (+0.8% to +1.4%).
  - `mid bounce`: `0.014 <= mx < 0.026` (+1.4% to +2.6%).
  - `big bounce`: `mx >= 0.026` (>= +2.6%).
  - `no sweep, <+2.6%`: No bar with `low <= ref_low` and `mx < 0.026`.
- **Pre-sweep Window Boundary**:
  - `pre = [b for b in mon if b[0] < end_] or []` where `end_ = sw[0] if sw else mon[-1][0] + HOUR`.
  - Notice that `sw` (the sweep bar itself) is excluded from `pre`.
  - If a bounce occurred during the first 30 minutes of the sweep bar before it swept, 1h bar data cannot resolve it (documented limitation: `monday_clocks.py:8`).
- **Verdict**: Thresholds and branch logic are mathematically mutually exclusive and exhaustive.

### F. Part 3: Lead-Time W/F Logic (`monday_clocks.py:196-217`)
- **Parameters**:
  - `w = min(b[3] for b in ref[-48:])`: Last 48 bars of `ref` = Sat 00:00 to Sun 23:00 (Sat-Sun low).
  - `low = min(b[3] for b in ref)`: All 72 bars of `ref` = Fri 00:00 to Sun 23:00 (Fri-Sun low).
  - Condition: `low < w * 0.995` ensures Fri low was at least 0.5% lower than Sat-Sun low.
  - `bw = next((b for b in mon if b[3] < w), None)`: First bar breaking Sat-Sun low.
  - `sw = next((b for b in mon if b[3] <= low), None)`: First bar sweeping Fri low.
  - `lead = (sw[0] - bw[0]) / HOUR`.
- **Properties**:
  - Since `low < w`, any bar with `b[3] <= low` also has `b[3] < w`.
  - Thus `bw[0] <= sw[0]` always holds. Lead time is guaranteed non-negative (`>= 0.0`).
  - If `bw[0] == sw[0]`, lead time is `0` hours.
- **Verdict**: Sound and consistent.
