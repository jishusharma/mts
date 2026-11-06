# Blind Read Audit: `run_copy_fork_study.py` and `copy_fork` (`pitchfork_2026-10-19`)

- **Card**: `gemini-blind-read-of-run-copy-fork-study`
- **Audited Files**: `MyTradingSys/research/pitchfork_2026-10-19/run_copy_fork_study.py`, `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py` (`copy_fork`, `CopiedFork`, `find_pivots_zigzag`, `zigzag_step`), `MyTradingSys/research/pitchfork_2026-10-19/PRE_REG_COPY_FORK.md`, `MyTradingSys/research/pitchfork_2026-10-19/RESULT_COPY_FORK.md`
- **Date**: 2026-11-06 UTC

## 1. Pivot-Triplet Indexing, Look-Ahead Check, and Stated Fork Rule Audit

1. **DEV Split Guard (`run_copy_fork_study.py:40-49` vs `PRE_REG_COPY_FORK.md:21`)**:
   - `load_bars()` stops reading `btc_4h_2020_2026.csv` as soon as `pd.Timestamp(r["datetime"]) >= splits.DEV_END` (`2024-07-01 00:00:00`) and asserts `pd.Timestamp(rows[-1]["dt"]) < splits.DEV_END`.
   - `VALIDATION` (`2024-07-01..`) and `HOLDOUT` (`2025-07-01..`) are untouched (`9,858` 4H bars from `2020-01-01 00:00:00` to `2024-06-30 20:00:00`).

2. **Stated Fork Rule & `copy_fork` Geometry (`pitchfork_detector.py:66-125, 246-254, 308-363` & `run_copy_fork_study.py:52-88, 97-116` vs `PRE_REG_COPY_FORK.md:23-29`)**:
   - **Source fork (`construct_pitchfork`, `pitchfork_detector.py:366-389`)**: Called with `variant=PitchforkVariant.STANDARD, auto_schiff=False, log_scale=log_scale` (`run_copy_fork_study.py:98`). In log scale (`LogPitchforkChannel`), pivot prices are mapped to `ln(price)` (`pitchfork_detector.py:246-248`); in linear scale (`PitchforkChannel`), raw dollar prices are used.
   - **Standard Andrews geometry (`pitchfork_detector.py:82-124`)**: Midpoint `(t_m, p_m) = ((t1 + t2)/2, (p1 + p2)/2)`, median-line slope `slope = (p_m - p0) / (t_m - t0)` (`SOURCED` Andrews, `pitchfork_detector.py:8-12`), vertical tine offsets `offset_p1 = p1 - (p0 + slope * (t1 - t0))` and `offset_p2 = p2 - (p0 + slope * (t2 - t0))` ordered into `offset_uml = max(offset_p1, offset_p2)` and `offset_lml = min(offset_p1, offset_p2)`, and `channel_width = abs(offset_uml - offset_lml)`.
   - **Copy-paste translation (`copy_fork`, `pitchfork_detector.py:343-363`)**: Translates the source fork in time and price (or `ln(price)` when `log_scale=True`) by `(dt, dp) = (anchor_index - src_t, new_p - src_p)` so the P0 handle sits on `(anchor_index, new_p)`, preserving `slope`, `offset_uml`, `offset_lml`, and `channel_width` (`SOURCED` operator 10-30 in `PRE_REG_COPY_FORK.md:24`). For a Standard fork where `g.t0 == src_t` and `g.p0 == src_p`, the pasted origin is `(t0 + dt, p0 + dp) == (anchor_index, new_p)`.
   - **Copy & Source lines (`fork_lines`, `run_copy_fork_study.py:85-87`)**: Evaluates the 3 lines (`ML`, `UML`, `LML` via offsets `0.0, g.offset_uml, g.offset_lml`) using `Line.at(t) = exp(base + slope * (t - t0))` for log scale and `base + slope * (t - t0)` for linear scale (`run_copy_fork_study.py:58-60`).
   - **Control parallels (`run_copy_fork_study.py:113-116` vs `PRE_REG_COPY_FORK.md:27`)**: Per pasted copy, draws `N_CONTROL = 10` (`OURS`) parallel lines with the same `cp.t0` and `cp.slope`, shifting `cp.p0` by `u * cp.channel_width` where `u ~ U(-1.5, 1.5)` (`U_SPAN = 1.5`, `SEED = 20261105`, `OURS`).
   - **Touch and Reaction rule (`reaction`, `run_copy_fork_study.py:63-82` vs `PRE_REG_COPY_FORK.md:28-29`)**:
     - Scans `i in range(max(start, 1), min(end, len(bars)))` for the first bar where `bars[i]["l"] <= lv <= bars[i]["h"]` (`lv = line.at(i)`).
     - Approach side is set by the prior bar close: `above = bars[i - 1]["c"] > lv` (`run_copy_fork_study.py:69`).
     - Within `j in range(i, min(i + 6, len(bars)))` (`H = 6`, `R = 0.015`, `OURS`, touch bar `j = i` included): if `above`, checks `j > i and bars[j]["c"] <= lv * (1 - R)` (adverse close through line -> `False`) before `bars[j]["h"] >= lv * (1 + R)` (favorable move away -> `True`); symmetrically for `not above` (`j > i and bars[j]["c"] >= lv * (1 + R)` vs `bars[j]["l"] <= lv * (1 - R)`). Note that on the touch bar itself (`j == i`), the adverse close check is gated by `j > i`, so only a favorable `1.5%` excursion away is tested on bar `i`, while bars `i+1 .. i+5` test adverse close first.

3. **Pivot-Triplet Indexing & Look-Ahead Check (`run_copy_fork_study.py:93-111, 157` & `pitchfork_detector.py:392-458`)**:
   - **Triplet & Anchor Indexing (`run_copy_fork_study.py:93-106`)**:
     - `pivots` has `931` strictly alternating High/Low extrema (`p0, p1, p2 = pivots[k], pivots[k+1], pivots[k+2]` gives `929` valid triplets).
     - `anchors = [p for p in pivots[k + 3:] if p.is_high == p0.is_high][:N_PASTES]` (`run_copy_fork_study.py:106`, `N_PASTES = 3`, `OURS`). Because `p0` and `p2` have the same `is_high` polarity and `pivots[k + 3]` has the opposite polarity, `pivots[k + 3:]` filtered by `p.is_high == p0.is_high` selects `[pivots[k + 4], pivots[k + 6], pivots[k + 8]]` — the next 3 pivots of `P0`'s type strictly after `P2`, matching `PRE_REG_COPY_FORK.md:24` (`925 * 3 + 2 + 2 + 1 + 0 = 2,775` pastes).
   - **Look-window start (`s0 = p2.index + LOOKBACK + 1` at `run_copy_fork_study.py:103`, `s = a.index + LOOKBACK + 1` at `run_copy_fork_study.py:110`)**:
     - For any pivot at bar index `idx`, `zigzag_step` confirms the local extremum over `idx - LOOKBACK .. idx + LOOKBACK` at confirmation bar `c_idx = idx + LOOKBACK` (`pitchfork_detector.py:406-408, 446`). Starting the 60-bar evaluation window at `idx + LOOKBACK + 1` (`c_idx + 1`) ensures the window starts strictly after `c_idx`.
   - **Subtlety in batch `find_pivots_zigzag` in-place leg extension (`pitchfork_detector.py:419-421, 428-430`)**:
     - `run_copy_fork_study.py:157` calls `find_pivots_zigzag` once over the full DEV series (`9,858` bars). In `zigzag_step`, when price makes a higher high while `last_type is True` (or a lower low while `last_type is False`) before a `>= 3%` reversal occurs, `pivots[-1]` is overwritten in place (`pivots[-1] = PitchforkPivot(index=i, ...)`).
     - Across the `931` final DEV pivots, `211` pivots (`210/929` triplets' `P2` and `624/2,775` paste anchors) were extended in place at least once after their initial local-extremum confirmation, and any earlier intermediate peak on that same leg was overwritten rather than tested as its own anchor. Furthermore, at bar `s = p.index + LOOKBACK + 1` (1 bar after the final peak's 4-bar local confirmation `c_idx = p.index + LOOKBACK`), the subsequent `>= 3%` opposite-leg reversal pivot `pivots[m + 1]` has not yet confirmed (`pivots[m + 1]` confirms after `s` for all `930` non-terminal pivots, though always before `s + 60`). Thus, knowing at bar `s` that `p` will not extend to a still-higher high later in the leg relies on the full-pass `find_pivots_zigzag` list (as pre-registered in `PRE_REG_COPY_FORK.md:22,25`), rather than the bar-by-bar state machine in `scan_pitchfork_signals`. This does not alter the negative conclusion (`diff = -2.3 pts`, `z = -3.43` in log scale; "no difference shown").

## 2. Per-Claim Recomputation Table (`run_copy_fork_study.py` vs `RESULT_COPY_FORK.md`)

All values below were independently recomputed (`OURS`) from `btc_4h_2020_2026.csv` and compared against `RESULT_COPY_FORK.md`.

| # | Claim (`RESULT_COPY_FORK.md` / `PRE_REG_COPY_FORK.md`) | Independently Recomputed Value / Code Ref (`OURS`) | Stated Value (`SOURCED`) | Result |
|---|---|---|---|---|
| 1 | DEV bar range & count (`RESULT_COPY_FORK.md:3`, `run_copy_fork_study.py:44-48`) | `2020-01-01 00:00:00 .. 2024-06-30 20:00:00`, `n = 9858` (guarded by `< splits.DEV_END`) | `2020-01-01 00:00:00 .. 2024-06-30 20:00:00 (n=9858)` (`RESULT_COPY_FORK.md:3`) | MATCH |
| 2 | ZigZag pivot count (`RESULT_COPY_FORK.md:3`, `run_copy_fork_study.py:157`) | `931` pivots (`lookback=4`, `min_change_pct=0.03`) | `pivots 931` (`RESULT_COPY_FORK.md:3`) | MATCH |
| 3 | Weekly regime mix (`RESULT_COPY_FORK.md:5`, `run_copy_fork_study.py:133-152`) | `234 weeks: bull 38 (16%) \| bear 0 (0%) \| range 131 (56%) \| n/a 65 (28%)` | `234 weeks: bull 38 (16%) \| bear 0 (0%) \| range 131 (56%) \| n/a 65 (28%)` (`RESULT_COPY_FORK.md:5`) | MATCH |
| 4 | Source forks & pasted copies (`RESULT_COPY_FORK.md:9-10`, `run_copy_fork_study.py:93-110`) | `929` source forks (`2787` source lines), `2775` pastes (`8325` copy lines, `27750` control lines) | `929` source forks, `2775` pastes (`RESULT_COPY_FORK.md:9-10`) | MATCH |
| 5 | Log (primary) copy lines touched / react & rate (`RESULT_COPY_FORK.md:9`) | `5657 / 8325` touched, `4223` react (`74.6509%` -> `74.7%`) | `5657/8325 touched, 4223 react \| 74.7%` (`RESULT_COPY_FORK.md:9`) | MATCH |
| 6 | Log (primary) control lines touched / react & rate (`RESULT_COPY_FORK.md:9`) | `15454 / 27750` touched, `11887` react (`76.9186%` -> `76.9%`) | `15454/27750 touched, 11887 react \| 76.9%` (`RESULT_COPY_FORK.md:9`) | MATCH |
| 7 | Log (primary) diff (pts), `z`, and Read verdict (`RESULT_COPY_FORK.md:9`) | `diff = -2.2677 pts` (`-2.3`), `z = -3.4318` (`-3.43`), `no difference shown` | `-2.3 \| -3.43 \| no difference shown` (`RESULT_COPY_FORK.md:9`) | MATCH |
| 8 | Log (primary) source-fork lines touched / react (`RESULT_COPY_FORK.md:9`) | `1456 / 2787` touched, `1117` react (`76.7170%` -> `76.7%`) | `1456/2787 touched, 1117 react (76.7%)` (`RESULT_COPY_FORK.md:9`) | MATCH |
| 9 | Linear (secondary) copy lines touched / react & rate (`RESULT_COPY_FORK.md:10`) | `5724 / 8325` touched, `4265` react (`74.5108%` -> `74.5%`) | `5724/8325 touched, 4265 react \| 74.5%` (`RESULT_COPY_FORK.md:10`) | MATCH |
| 10 | Linear (secondary) control lines touched / react & rate (`RESULT_COPY_FORK.md:10`) | `15598 / 27750` touched, `11967` react (`76.7214%` -> `76.7%`) | `15598/27750 touched, 11967 react \| 76.7%` (`RESULT_COPY_FORK.md:10`) | MATCH |
| 11 | Linear (secondary) diff (pts), `z`, and Read verdict (`RESULT_COPY_FORK.md:10`) | `diff = -2.2105 pts` (`-2.2`), `z = -3.3621` (`-3.36`), `no difference shown` | `-2.2 \| -3.36 \| no difference shown` (`RESULT_COPY_FORK.md:10`) | MATCH |
| 12 | Linear (secondary) source-fork lines touched / react (`RESULT_COPY_FORK.md:10`) | `1460 / 2787` touched, `1106` react (`75.7534%` -> `75.8%`) | `1460/2787 touched, 1106 react (75.8%)` (`RESULT_COPY_FORK.md:10`) | MATCH |
| 13 | Stated fork rule & anchor indexing (`run_copy_fork_study.py:98-115`, `pitchfork_detector.py:343-363`) | Standard Andrews fork on `(p0, p1, p2)`, translated by `copy_fork` to first 3 pivots of `p0`'s polarity in `pivots[k+3:]`, evaluated on `s = index + 5 .. index + 64` | Matches `PRE_REG_COPY_FORK.md:23-29` (`s = anchor + lookback + 1 .. +60`; note batch `find_pivots_zigzag` overwrites extending legs in place at `pitchfork_detector.py:421,430`) | MATCH |

Defects: none that alter the pre-registered calculation or `RESULT_COPY_FORK.md` numbers (caveat on batch `find_pivots_zigzag` in-place extension of extending legs at `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:421,430` when called from `MyTradingSys/research/pitchfork_2026-10-19/run_copy_fork_study.py:157` noted in Section 1.3 above).

VERDICT: MATCH
