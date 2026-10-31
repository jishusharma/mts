# Independent Bug Hunt: Cost, Fee, Funding, Fill Assumptions and Look-Ahead (`ARGON_COST_LOOKAHEAD.md`)

**Task Card**: `gemini-argon-independent-bug-hunt-cost-lookahead`  
**Model**: Gemini 4 Argon (Medium)  
**Date**: 2026-10-31  
**Scope Inspected**:
1. `MyTradingSys/backtest/fees.py` (L1–59)
2. `MyTradingSys/backtest/sim.py` (L1–127)
3. **5 Newest Backtest Runners (by git commit history on 2026-10-31)**:
   - Runner 1: `MyTradingSys/research/cowen_q4_2026-10-31/event_study/run_event_study.py` (L1–304, commit `bdf5e584b`, plus imported `MyTradingSys/research/sim_desk/studies/cowen_bmsb.py` L1–244)
   - Runner 2: `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py` (L1–222, commit `488c01b8e`, plus imported `MyTradingSys/research/fractals_2026-10-31/f4/f4lib.py` L1–222)
   - Runner 3: `MyTradingSys/research/fractals_2026-10-31/f3/run_f3.py` (L1–362, commit `74b3ccbae` / `df207b879`)
   - Runner 4: `MyTradingSys/research/fractals_2026-10-31/f2/run_f2.py` (L1–243, commit `2abcd700a`, plus imported `MyTradingSys/research/fractals_2026-10-31/f2/hseries.py` L1–46)
   - Runner 5: `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py` (L1–269, commit `6c21cfd62`)
   - Additional newest runner inspected for completeness: `MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/run_split.py` (L1–32) & `build_feenet.py` (L1–83, commit `47e5dcf89`).

All findings below state facts with exact `file:line` citations and minimal reproducing inputs. No trading verdicts or code changes are made.

---

## Summary Table of Findings

| ID | File : Line | Category | Severity / Nature | Short Description |
|---|---|---|---|---|
| **F01** | `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py:67-68` & `115-125` | Look-Ahead (Control Stratification) | Full-sample look-ahead in baseline control | `vol30` quintile edges and strata counts are computed over the entire 2017–2025 dataset at once; `okv` also includes all bars with `s >= 130` rather than the `s >= 150` warm-up where features exist. |
| **F02** | `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py:169,205` | Timestamp / Look-Ahead Alignment | Off-by-one bar timestamp semantics | `events_feenet.csv` `time` is the **entry bar open** ($t_{\text{sig}} + 1\text{h}$ or $+4\text{h}$), not the detector close. Comparing `rd_t <= ent_time[ix]` treats a 4h RSI-DIV event detected at $T-1\text{h}$ (whose entry bar opens at $T$, closing at $T+4\text{h}$) as already having its entry at $T$. |
| **F03** | `MyTradingSys/research/fractals_2026-10-31/f4/f4lib.py:81-97` | Fill Assumption | Missing gap-through-stop / gap-through-target logic | `sim_trade` checks `hi >= stop` and sets `X = stop` (or `X = target`) unconditionally, ignoring gap opens (`o1[k] > stop` on subsequent 1h bars) and ignoring the 8h signal bar close-to-next-1h-open gap (`E >= stop` rejects the trade via `not risk > 0` instead of filling a gap stop). |
| **F04** | `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:157-161,170-173` | Look-Ahead (Control Distribution) | Full-sample look-ahead in control level distances | `dists[grp]` pools `abs(price - cl1[i]) / atr` across the entire 2022–2025 DEV period before drawing random control levels for early 2022 events. |
| **F05** | `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:98-116` | Cost / Fill Assumption | Limit fade modeled as all-taker with entry-only fee base and fixed `-1.0R` stop on gap entry | (1) Entry gaps beyond `level` (`entry = max(level, o[m])`) shift `stop = entry - side * risk` away from the pivot instead of anchoring stop to `level`; (2) intra-bar gap openings on bars `m+1..j1-1` still fill at `stop` (`gross = -1.0`); (3) `rt_r = 2 * FEE_SIDE * entry / risk` charges exit fee on `entry` notional rather than `exit` notional (`entry * (1 +- risk/entry)`). |
| **F06** | `MyTradingSys/research/fractals_2026-10-31/f3/run_f3.py:150-151,158-159,324` | Cost / Look-Ahead / Fill | Single-leg exit fee omission, full-sample `nanmean` backfill, and unshifted `sd24` | (1) `RT_PCT = 2 * FEE_SIDE * 100.0` (`0.10%`) subtracts `FEE_SIDE * entry` twice instead of `FEE_SIDE * entry + FEE_SIDE * exit`; (2) `surrogate_returns` fills initial NaNs of `sg` with full-sample `np.nanmean(sg)` across 2022–2025 (`L159`); (3) `sd24 = trailing_std(r)` uses `shift=0` (`L289`), normalising R/trade (`L324`) by volatility that includes bar `qe` itself. |
| **F07** | `MyTradingSys/research/fractals_2026-10-31/f2/run_f2.py:218-231` | Event Overlap / Selection | Overlapping F1 fade events and post-exit H-series permutation | `run_f2.py` ingests all `7,416` touched F1 real pivot fades (`7,292` with valid H) without non-overlap filtering (up to dozens of concurrent 24h trades open simultaneously), inflating `n kept` against the `nk >= 200` decidability gate (`L152`). |
| **F08** | `MyTradingSys/research/cowen_q4_2026-10-31/event_study/run_event_study.py:26,123,126-131` vs `cowen_bmsb.py:33,222-225` | Cost / Parameter / Fill Inconsistency | Three divergences between `run_event_study.py` and `cowen_bmsb.py` | (1) `STOP_R = 1.0` anchored to next open `d[e, 1]` (`run_event_study.py:26,122-123`) vs `stop_atr = 2.0` anchored to signal close `d[i, 4]` (`cowen_bmsb.py:33,222-223`); (2) `simulate` (`run_event_study.py:130-131`) fills `target` at `float(target)` even when daily open `o` gaps past `target`; (3) zero slippage/funding over 30-day perp/spot holds vs `SLIP_DEFAULT = 0.02%` in `_bars.py:23`. |
| **F09** | `MyTradingSys/backtest/sim.py:68-86` | Cost / Fill / Selection | Exit notional fee omission, censored-trade drop, and unslipped 60s fills | (1) `fee_R = fee_pct * e / risk` (`L83`) applies exit fee to entry price `e` instead of exit price `x`; (2) `report()` (`L93`) filters to `("stop", "target")` only, dropping `timeout`, `censored_gap`, and `censored_end` trades from win-rate and `sum net R` (`L100-104`) while `L110` sums `net` over all trades including `censored_gap`; (3) target fills at exact `t` (`L76`) even when snapshot `px` gaps past `t`, and `--stops ideal` (`L74`) fills stops at `s` ignoring observed `px`. |
| **F10** | `MyTradingSys/backtest/fees.py:42-59` | Fee / Cost Contract | Unvalidated `fees_dict` and spot vs perp fee-profile mismatch | (1) `fees_dict` (`L42-44`) accepts negative, `NaN`, or `None` fees without validation; (2) `BINANCE_TAKER = 0.0005` (`L36`, documented as "Binance USDT-M perpetual", L12) is imported by spot-data studies (`run_event_study.py:18,264` and `run_f4.py` / `f4lib.py:13`, which explicitly load Binance **spot** klines where standard spot taker fee is 10 bp = `0.0010`, not 5 bp). |

---

## Detailed Findings (`file:line` & Reproducing Inputs)

### F01. `run_f4.py`: Full-Sample Volatility Quintile Look-Ahead and Warm-Up Mismatch in B1/B2 Controls
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py:66-68` and `115-125`; `MyTradingSys/research/fractals_2026-10-31/f4/f4lib.py:101-132`.
- **Facts**:
  1. In `run_f4.py:66-68`:
     ```python
     okv = valid & np.isfinite(vol)
     edges = np.quantile(vol[okv], [0, 0.2, 0.4, 0.6, 0.8])
     strata = np.where(np.isfinite(vol), strata_of(np.nan_to_num(vol), edges), 0)
     ```
     `edges` are computed once across all `okv` bars from `2017-08` through `2025-06`. An event in 2018 is assigned a volatility stratum using future 2019–2025 volatility quantiles, and its B1/B2 control draws (`run_f4.py:119-124`, `f4lib.py:181-193`) sample replacement bars from future years (`2018..2025`) matching that full-sample stratum.
  2. Furthermore, in `f4lib.py:105-106`, `valid_bars(bt)` marks bar `s` valid starting at `s = 130` (`vol30` needs 30 bars, so `okv` is True from `s = 130`). However, `RULE` and `ANALOG` events require `bwpct_prev` (`bw.rolling(90)` on `c.rolling(20)`, which is `NaN` until bar `s = 109`), AND `valid_bars` starts at `130`. More critically, `okv` (`valid & np.isfinite(vol)`) includes every valid 8h bar in `tab[("cr", h)]` where `bh[s] > E` (`sim_trade` `risk > 0`), including bars where `bh[s] - E` is tiny (e.g., 1 cent or a few dollars when 1h open `E` is near the prior 8h high `bh[s]`), causing `fee / risk` (`TAKER * (E + X) / risk`) to explode to hundreds of R on non-event bars (`B1 mean = -4.974 R` to `-6.497 R` in `f4/output.md:7-15`, whereas `POST-HOC net-% control mean` is `-0.125%`).
- **Minimal Reproducing Input**:
  ```python
  import numpy as np, pandas as pd
  from MyTradingSys.research.fractals_2026_10_31.f4 import f4lib as L  # or via sys.path
  # Suppose bar s has close=50000, high bh[s]=50001 (1 USD above next open E=50000, target=49998), exit X=50000:
  r, p = L.sim_trade(-1, E=50000.0, stop=50001.0, lows=[49999.0], highs=[50000.5], last_close=50000.0)
  # risk = 1.0 USD, fee = 0.0005 * 100000 = 50 USD -> r = -50.0 R on a flat trade!
  assert r == -50.0 and abs(p - (-0.10)) < 1e-9
  ```

---

### F02. `run_f4.py`: `RSI-DIV-MTF` Layer Split Compares Entry-Bar Open Timestamp Against Signal-Close Timestamp
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py:70,168-169,204-205` and `MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/build_feenet.py:74-75`.
- **Facts**:
  - `f4/PRE_REG.md:31` specifies: *"RSI-DIV-MTF fired = any event in p1b_rsi_feenet/events_feenet.csv with entry time in the 3 bars (24 h) before the signal bar close, y/n"*.
  - In `run_f4.py:70`, `ent_time = bt + L.BAR` (which is the close time of 8h signal bar `s`, i.e., the entry time of the F4 trade).
  - In `run_f4.py:204-205`:
    ```python
    ct = ent_time[ix]
    fired = np.array([bool(((rd_t > c - 86400) & (rd_t <= c)).any()) for c in ct])
    ```
  - In `build_feenet.py:74-75`, `time` written to `events_feenet.csv` is `r["entry_t"]`, which is `t[entry_i]` (`event_table.py:76-77`), the **open** of the bar *after* the RSI divergence bar `i`.
  - When `rd_t == c` (`rd_t <= c`), the RSI divergence was confirmed at `c` (the close of the bar ending at `c`, which is the open of `rd_t = c`), so that is causal at `c`. However, for any event where `rd_t` is compared across datasets, `events_feenet.csv` mixes `1h` and `4h` events without filtering by timeframe (`run_f4.py:168` reads `usecols=["time"]` only).

---

### F03. `f4lib.py`: Missing Gap-Through-Stop Fill Logic in `sim_trade`
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f4/f4lib.py:75-98` and `121-131`.
- **Facts**:
  1. `sim_trade(side, E, stop, lows, highs, last_close)` (`f4lib.py:75-98`) does not take bar opens `o1` for the path bars `i0..i0+m-1`.
  2. If a 1h bar inside the holding window opens beyond `stop` (a gap open between 1h bars or after a missing/halted minute), `sim_trade` fills at exact `stop` (`X = stop`, `f4lib.py:85,92`) rather than the worse bar open.
  3. On the entry bar itself (`E = o1[i0]`), if `o1[i0]` gaps beyond the signal bar's high `bh[s]` (for a short) or low `bl[s]` (for a long), `risk = (stop - E) if side < 0 else (E - stop)` is `<= 0` (`f4lib.py:77-79`), returning `(np.nan, np.nan)`. In `run_f4.py:83,100`, `np.isfinite(r)` silently drops any signal whose entry open gapped past the stop level, rather than recording a trade or censoring it explicitly.
- **Minimal Reproducing Input**:
  ```python
  from MyTradingSys.research.fractals_2026_10_31.f4 import f4lib as L
  # Long trade: E = 100, stop = 95 (1R = 5). Next 1h bar gaps down to open=90, low=88, high=92:
  # sim_trade does not accept `opens`, so it fills at stop=95 (-1.0 gross R) instead of open=90 (-2.0 gross R).
  net_r, net_pct = L.sim_trade(1, E=100.0, stop=95.0, lows=[88.0], highs=[92.0], last_close=91.0)
  assert round(net_r + (0.0005 * 195.0) / 5.0, 6) == -1.0
  ```

---

### F04. `run_f1.py`: Full-Sample Look-Ahead in Random-Level Control Distance Pool (`dists[grp]`)
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:153-176`.
- **Facts**:
  - In `build_events(df1m)` (`run_f1.py:155-161`), the loop first iterates over **all** `1h` pivots in `2022-01..2025-06` and populates `dists[grp]` with `abs(price - cl1[i]) / atr` across the entire 3.5-year DEV dataset:
    ```python
    for (avail, price, kind, i), (m4, md) in zip(p1, flags):
        ...
        dists.setdefault(grp, []).append(abs(price - cl1[i]) / atr)
        items.append((avail, price, kind, i, grp))
    ```
  - Then in the second loop (`run_f1.py:164-175`), for each pivot at `avail` (e.g. in January 2022), `d = float(rng.choice(pool))` samples from `pool = np.array(dists[grp])`, which contains normalized pivot distances from future bars up to June 2025.
- **Minimal Reproducing Input**:
  ```python
  # An event at 2022-01-05 draws control distance `d` from `dists[grp]`, which includes 2025-06 pivots.
  # Truncating df1m at 2023-01-01 changes `pool` and therefore changes the control trades generated in 2022-01.
  ```

---

### F05. `run_f1.py`: Limit-Fade Entry Modeled with Taker Fee on Entry Notional Only, Shifted Stop on Gap Entry, and No Intra-Hold Gap Slippage
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:88-117`.
- **Facts**:
  1. **Stop/Target shifted by gap entry (`L99-102`)**: `PRE_REG.md:17` states: *"Entry = level (or the 1m open if it gapped through). Stop = 1.0 x ATR14(1h at A) beyond the level (R = 1 ATR); target = 1.0 x ATR back = +1R"*. However, `run_f1.py:99-102` writes:
     ```python
     entry = max(level, o[m]) if kind > 0 else min(level, o[m])
     risk = STOP_ATR * atr
     stop = entry - side * risk
     target = entry + side * TARGET_R * risk
     ```
     When `o[m]` gaps beyond `level`, `stop` and `target` are computed from `entry` (`o[m]`), not from `level` as written in `PRE_REG.md:17` ("Stop = 1.0 x ATR14(1h at A) beyond the level"). Moreover, why would a passive limit fade order at `level` fill at a *better* price `o[m] > level` (for a short) only on a 1m bar gap after `anchor`? If the level was already below `o[m]` at `anchor`, price started above `level` (already beyond resistance) rather than approaching resistance from below!
     Specifically: `pivots()` (`L58-59`) records `price = piv[i]` at bar `k = i - 2`, confirmed at close of bar `i` (`avail`). During bars `i-1` and `i`, price can already cross *above* a pivot high `level`! Then at `i0` (the first 1m bar at `avail`), `o[i0] > level` and `h[i0] >= level` (`L94`), so `trade_outcome` immediately triggers a "fade short" even though price broke out *above* resistance 2 hours ago and is trading above `level`!
  2. **Fixed `-1.0R` on stop regardless of 1m gap opens (`L109-110`)**:
     ```python
     if s is not None and (g is None or s <= g):
         gross, why = -1.0, "stop"
     ```
     If a 1m bar during the 24h hold opens beyond `stop` (`o[m + s] > stop` for short, or `< stop` for long), `trade_outcome` still assigns `gross = -1.0` instead of `side * (o[m + s] - entry) / risk`.
  3. **Exit fee charged on `entry` notional instead of `exit` notional (`L115`)**:
     ```python
     rt_r = 2 * FEE_SIDE * entry / risk
     ```
     Unlike `FORMULAS.md` Section 18.5 (`fee_in * entry + fee_out * exit`) and `build_feenet.py:54` (`BINANCE_TAKER * (entry + exit_price) / risk`), `run_f1.py:115` approximates both legs using `entry`.
- **Minimal Reproducing Input**:
  ```python
  import numpy as np
  from MyTradingSys.research.fractals_2026_10_31.f1 import run_f1
  # 1m bar at anchor=1000 where price already broke above resistance level=100 (open=105, high=112, low=104, close=111)
  # and next bar gaps to open=120 (past stop=105+10=115):
  t = np.array([1000, 1060], dtype=np.int64)
  o = np.array([105.0, 120.0]); h = np.array([112.0, 125.0]); l = np.array([104.0, 119.0]); c = np.array([111.0, 122.0])
  out = run_f1.trade_outcome(t, o, h, l, c, anchor=1000, expiry=5000, level=100.0, kind=1, atr=10.0)
  # 1) Enters short at 105 even though price was already above resistance 100 at anchor;
  # 2) Bar 2 opens at 120 (0.5 ATR past stop=115), yet gross_r is capped at -1.0 instead of -1.5!
  assert out["gross_r"] == -1.0
  ```

---

### F06. `run_f3.py`: Exit Fee Applied to Entry Notional, Full-Sample `nanmean` in Surrogate Vol, and Unshifted `sd24`
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f3/run_f3.py:32-33,92-97,147-161,289,324`.
- **Facts**:
  1. **Fee on exit price (`L33, 150-151`)**:
     ```python
     RT_PCT = 2 * FEE_SIDE * 100.0
     ...
     gross = pos * (np.exp(fwd_real[qe]) - 1.0) * 100.0
     net = np.where(taken, gross - RT_PCT, np.nan)
     ```
     For a trade entering at $P_0$ and exiting at $P_1 = P_0 e^{r}$, exact round-trip taker fee as a percentage of entry notional is $\text{FEE\_SIDE} \times (1 + e^r) \times 100\%$, whereas `RT_PCT` charges $2 \times \text{FEE\_SIDE} \times 100\%$. Furthermore, for a short position (`pos = -1`), if log return `fwd_real[qe]` is $+0.10$ ($e^{0.10} - 1 \approx +10.52\%$), `gross = -10.52%`, which accurately uses simple return $P_1/P_0 - 1$, but `decide()` (`L140`) averages log returns `o = lib_fwd[ix]` rather than simple returns.
  2. **Full-sample `np.nanmean(sg)` in `surrogate_returns` (`L156-161`)**:
     ```python
     sg = trailing_std(r, shift=1)
     sg = np.where(np.isnan(sg), np.nanmean(sg), sg)
     ```
     For the first 20 bars (`minp=20` in `trailing_std`, `L92`) or after any data gap where `sg` is `NaN`, `sg` is imputed with `np.nanmean(sg)` computed over the **entire** 2022–2025 series (`r`). Those early bars are part of the expanding library (`Zl`) queried by later forecasts.
  3. **Unshifted `sd24` in reported R/trade (`L289, 324`)**:
     In `surrogate_returns` (`L158`), `trailing_std(r, shift=1)` is called with `shift=1` ("strictly past"). However, at `L289`:
     ```python
     sd24 = trailing_std(r) * np.sqrt(24) * 100.0
     ```
     `shift` defaults to `0`, which includes `r[qe]` (known at the close of `qe`, causal for entry at close of `qe`, though inconsistent with `shift=1` in `L158`). If `sd24[qe][tk]` ever hits `0` (flat window), `nets / sd24[qe][tk]` divides by zero.
- **Minimal Reproducing Input**:
  ```python
  import numpy as np
  from MyTradingSys.research.fractals_2026_10_31.f3 import run_f3
  # Trade with +20% simple return (fwd_real = ln(1.20)), long (pos=1):
  pos = np.array([1]); qe = np.array([0]); fwd = np.array([np.log(1.20)])
  _, net, _ = run_f3.trade_net(pos, qe, fwd)
  # Exact fee = 0.05% * 1.0 + 0.05% * 1.2 = 0.11%, so exact net = 19.89%.
  # trade_net charges 0.10%, returning 19.90% (+1 bp error):
  assert round(float(net[0]), 4) == 19.9000
  ```

---

### F07. `run_f2.py`: Highly Overlapping Concurrent Trades in `FADE` Event List (`n = 7,292` over 3.5 Years)
- **Location**: `MyTradingSys/research/fractals_2026-10-31/f2/run_f2.py:217-231` and `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:164-176`.
- **Facts**:
  - `run_f1.py` (`build_events`, `L164-176`) evaluates every confirmed 1h Williams fractal (`8,746` pivots in 3.5 years $\approx 30,648$ hours, i.e., one pivot every 3.5 hours) independently with a 96-hour live touch window and a 24-hour trade holding period (`HOLD_S = 24 * 3600`, `L37`), with **no `busy_until` or `non_overlap` filter** (unlike `run_event_study.py:143`, `f4/run_f4.py:84`, and `sim.py:86`).
  - `run_f2.py:218-219` loads all `evf[evf.kind == "real"]` (`7,416` touched fades, `7,292` with valid H) directly into `raw["FADE"]`.
  - Because a single 1m price sweep touches multiple stacked 1h pivot levels from the prior 96 hours at the exact same minute (or within the same hour) and holds each for up to 24 hours, dozens of `FADE` trades share the exact same underlying price bars and the exact same hourly `h_full[idx]` value (`lookup_idx(avail, t)`, `run_f2.py:55-56`).
  - In `run_f2.py:152`, the decidability gate checks `if nk < 200 or nr < 30: v = "NOT_DECIDABLE"`, treating overlapping pivot touches as independent events for the count threshold, and in `run_c2` (`L95-103`) permutes event labels i.i.d. across overlapping events (`rng.permutation(len(y))`), ignoring within-hour/within-day clustering.
- **Minimal Reproducing Input**:
  ```python
  # Two 1h pivot highs at 50,000 and 50,010 confirmed within 10 hours of each other are both touched
  # on the same 1m bar at t = 1650000000. lookup_idx(avail, t) maps both to the exact same 1h Hurst index,
  # and both run over the exact same 24h forward bars, counting as 2 events toward nk >= 200.
  ```

---

### F08. `run_event_study.py` vs `cowen_bmsb.py`: Parameter, Stop-Anchor, Target-Gap, and Slippage Discrepancies
- **Location**: `MyTradingSys/research/cowen_q4_2026-10-31/event_study/run_event_study.py:21,26,117-132` vs `MyTradingSys/research/sim_desk/studies/cowen_bmsb.py:33-34,217-233` and `MyTradingSys/research/sim_desk/studies/_bars.py:23-24,158-168,193`.
- **Facts**:
  1. **Stop width and anchor price mismatch**:
     - `run_event_study.py:19` states: `import cowen_bmsb as cb # (band, signals: same functions as the desk study)`.
     - However, in `cowen_bmsb.py:33,222-225`, default `stop_atr = 2.0`, and `stop` / `target` are anchored to the **signal bar's close** (`close = float(d[i, 4])`, `stop = close - side * q['stop_atr'] * r`), whereas `_bars.run_trade` (`_bars.py:149`) later computes `risk = side * (px - stop)` from the next day's open `px`!
     - In contrast, `run_event_study.py:26,122-123` uses `STOP_R = 1.0` and anchors `stop` and `target` to the **entry bar's open** (`entry = d[e, 1]`, `stop, target = entry - side * STOP_R * r, entry + side * TARGET_R * r`).
  2. **Entry-bar target hit vs `_bars.py` fill-bar rule**:
     - In `_bars.py:159`, `tgt_hit[0] = False`: on the entry bar, target hits are suppressed (only stops can trigger on the fill bar).
     - In `run_event_study.py:124-131`, the loop starts at `k = e` (the entry daily bar) and allows `h >= target` (or `l <= target`) on bar `e` itself to exit at `+2R` (`return k, float(target), 'target'`). Because `e` is a **full 24-hour daily bar**, if both `l > stop` and `h >= target` occur on the entry day `e`, `run_event_study.py` awards a target win, whereas if `l <= stop` and `h >= target` both occur on day `e`, it takes `stop` without checking the 1m path order inside day `e`.
  3. **Gap-through-target on daily bars (`run_event_study.py:130-131`)**:
     - If a daily bar `k > e` opens past `target` (e.g., after a weekend or missing bar, or if `target` was modified), `simulate` checks `if (h >= target) if side > 0 else (l <= target): return k, float(target), 'target'` (`L130-131`), which is fine for a resting limit target order, except `FEE = BINANCE_TAKER` (`L21, 114`) charges a **taker** fee (`5 bp`) on that limit target fill instead of maker fee (`BINANCE_MAKER = 2 bp`), whereas `_bars.py:167` charges `maker` on `T1` target fills.
  4. **Zero slippage and zero 30-day funding (`run_event_study.py:21,26,114`)**:
     - `run_event_study.py` holds positions up to `HOLD = 30` days (`90` funding settlements on perpetuals), applies `BINANCE_TAKER` (`0.0005`, the perp fee rate from `fees.py:36`) to Binance **spot** klines (`run_event_study.py:264`), and includes neither slippage (whereas `_bars.py:23` charges `SLIP_DEFAULT = 0.02%`) nor funding.
- **Minimal Reproducing Input**:
  ```python
  import numpy as np
  from MyTradingSys.research.cowen_q4_2026_10_31.event_study import run_event_study as es
  # Daily bar e=0 opens at 100, low=91 (> stop 90), high=125 (>= target 120), r=10:
  d = np.zeros((30, 5))
  d[:, 1] = 100.0; d[:, 2] = 101.0; d[:, 3] = 99.0; d[:, 4] = 100.0
  d[0] = [0, 100.0, 125.0, 91.0, 110.0]
  # Entry bar e=0 immediately exits at target=120.0 on the entry bar itself:
  assert es.simulate(d, e=0, side=1, r=10.0) == (0, 120.0, 'target')
  ```

---

### F09. `MyTradingSys/backtest/sim.py`: Exit Fee Charged on Entry Price, Censored/Timeout Trades Dropped from Resolved Summary, and Ideal Stop / Target Gap Handling
- **Location**: `MyTradingSys/backtest/sim.py:68-110`.
- **Facts**:
  1. **Exit fee charged on entry price `e` instead of exit price `x` (`sim.py:82-83`)**:
     ```python
     fee_pct = taker + (maker if kind == "target" else taker)
     fee_R = fee_pct * e / risk
     ```
     Per `FORMULAS.md` Section 18.5, exit fee is proportional to exit price `x` (`(taker * e + fee_out * x) / risk`), as implemented in `tom_bt.py:206` (`(fees["entry"] * entry + fees[kind] * px) / risk`). `sim.py:83` multiplies both legs by `e`.
  2. **Timeout and censored trades excluded from `report()` headline stats (`sim.py:93, 100-104`)**:
     ```python
     res = [x for x in trades if x["kind"] in ("stop", "target")]
     ```
     `res` excludes `"timeout"`, `"censored_gap"`, and `"censored_end"`. Consequently, `sum gross R`, `avg fee R`, `avg net R`, and `sum net R` printed at `sim.py:102-104` completely omit `"timeout"` trades (trades held $> 12\text{h}$, `L70-71`), whereas the per-setup breakdown at `sim.py:110` (`sum(y["net"] for y in L)`) sums `net` over **all** trades in `L` (including `"timeout"`, `"censored_gap"`, and `"censored_end"`!). Thus, the sum of per-setup `sum net R` lines at `L110` does **not** equal the headline `sum net R` at `L102-104` whenever any trade ends in `timeout`, `censored_gap`, or `censored_end`.
  3. **Target fills at `t` on 60s discrete snapshots even if price gapped, while `stops="observed"` fills stops at `px` (`sim.py:73-76`)**:
     - At `L74`: `if (d == "long" and px <= s) or (d == "short" and px >= s): res = ("stop", s if stops == "ideal" else px); break`
     - At `L76`: `if (d == "long" and px >= t) or (d == "short" and px <= t): res = ("target", t); break`
     - Because `sim.py` steps through discrete ~60s point snapshots (`q["price"]`, with no high/low range over the 60s interval), intra-minute wicks that hit `stop` and bounce before the 60s snapshot are missed (`sim.py:17`). Conversely, if `--stops ideal` is passed on CLI (`L115`), gap stops fill at `s` with zero slippage.
  4. **Rule B consecutive-snapshot check ignores whether row `i-1` was already consumed by a trade (`sim.py:56-59, 86`)**:
     - When a trade exits on bar `j`, `i` advances to `j + 1` (`L86`). Under Rule B (`L56-59`), if `rows[j + 1]` has `SETUP_FORMING`, it checks `p = rows[i - 1]` (which is `rows[j]`, the **exit bar** of the previous trade!) and enters immediately on `j + 1` if `rows[j]` also had `SETUP_FORMING` with the same setup and dir.
- **Minimal Reproducing Input**:
  ```python
  import io, contextlib
  from MyTradingSys.backtest import sim
  # Trade 1 hits target (+2R gross), Trade 2 times out after 12h at -0.5R gross:
  rows = [
      {"t": 0, "ts": "t0", "verdict": "SETUP_FORMING", "setup": "S1", "dir": "long", "price": 100.0, "stop": 90.0, "target": 120.0},
      {"t": 60, "ts": "t1", "verdict": "NONE", "setup": "", "dir": "", "price": 120.0, "stop": 0, "target": 0},
      {"t": 120, "ts": "t2", "verdict": "SETUP_FORMING", "setup": "S1", "dir": "long", "price": 100.0, "stop": 90.0, "target": 120.0},
  ] + [{"t": 120 + 60 * k, "ts": f"tk{k}", "verdict": "NONE", "setup": "", "dir": "", "price": 95.0, "stop": 0, "target": 0} for k in range(1, 722)]
  trades = sim.run(rows, rule="A", stops="observed", taker=0.0005, maker=0.0)
  buf = io.StringIO()
  with contextlib.redirect_stdout(buf):
      sim.report(trades, "test")
  out = buf.getvalue()
  # Headline "sum net R 2.00" omits the timeout trade (-0.51 R), while per-setup S1 prints "sum net R 1.49"!
  assert "sum net R 2.00" in out and "sum net R 1.49" in out
  ```

---

### F10. `MyTradingSys/backtest/fees.py`: Unvalidated `fees_dict` and Spot vs Perpetual Fee-Schedule Mismatch
- **Location**: `MyTradingSys/backtest/fees.py:12-14,35-37,42-50`.
- **Facts**:
  1. `fees.py:12-14,35-37` defines `BINANCE_TAKER = 0.0005` (5 bps per side) and `BINANCE_MAKER = 0.0002` (2 bps per side) explicitly as **"Binance USDT-M perpetual, default tier"**. `fees.py` defines **no** Binance Spot fee profile (where standard VIP 0 spot fee is 10 bps per side = `0.0010`). As a result, studies running on Binance **spot** klines (`run_event_study.py:18,264` and `f4lib.py:13` / `run_f4.py:64`) import `BINANCE_TAKER` (`0.0005`), undercharging spot exchange fees by 50% (10 bps RT instead of 20 bps RT) unless they are intended as perp proxies using spot price history.
  2. `fees_dict(entry, target, stop, timeout)` (`fees.py:42-44`) performs no validation against negative numbers, `NaN`, `Inf`, or `None`, allowing silent propagation of invalid fee dicts if called with bad parameters.
- **Minimal Reproducing Input**:
  ```python
  import math
  from MyTradingSys.backtest import fees
  d = fees.fees_dict(float("nan"), -0.01, None, float("inf"))
  assert math.isnan(d["entry"]) and d["target"] < 0 and d["stop"] is None
  ```

---

Noticed:
- `MyTradingSys/backtest/sim.py:93` vs `110`: `report()` excludes `"timeout"` trades from the headline `resolved` net R statistics (`L93, 102-104`) while including `"timeout"`, `"censored_gap"`, and `"censored_end"` in the per-setup `sum net R` column (`L110`), causing headline and per-setup net R totals to disagree.
- `MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py:67` and `MyTradingSys/research/fractals_2026-10-31/f1/run_f1.py:160`: both studies build their control distributions (`vol30` quintile edges in F4; `dists[grp]` normalized pivot distances in F1) across the full multi-year DEV window at once rather than causally up to each event's timestamp.
