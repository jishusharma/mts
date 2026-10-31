# Cross-Vendor Method Review: Tom Value-Area Return Study (Commit 80b0c19b)

- Target commit: `80b0c19b80d0830ddc0fcdbe0d2fd816bab56145`
- Primary files added:
  - `MyTradingSys/backtest/vp_return_to_value.py`
  - `MyTradingSys/backtest/test_vp_return_to_value.py`
  - `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/results.json`
- Reviewer: Gemini Flash (Antigravity cross-vendor review)
- Date: 2026-10-31 (UTC)

---

## 1. Executive Summary

Commit `80b0c19b` implements an empirical count of Tom Vorwald's claim ("price returns to value ~70% of the time after leaving it") on BTCUSDT 5m bars over the DEV window (2022-01-02 to 2024-06-30, 911 UTC days).

The code and pre-registration are exceptionally disciplined regarding DEV holdouts and separation of descriptive counts from trading claims. However, cross-vendor method auditing identified several subtle methodological risks and boundary conditions:
1. **Selection & Censoring Effects (Day-boundary horizon truncation)**: Events occurring late in the UTC day have almost zero remaining bars to achieve return to POC, inducing an artificial downward bias in return shares for late-day breakouts.
2. **Part B Applicable Definition Asymmetry vs Part A**: In Part B, `applicable` is defined as `e + n - 1 <= len(c) - 1`. If `e + n - 1 == len(c) - 1`, the acceptance bar is the final bar of the day, leaving 0 subsequent bars for `ret = _touch(h[e+n:], l[e+n:], poc)`. This unconditionally forces `returned = False` on the boundary bar.
3. **Event-Bar Intraday POC Touches**: If price leaves value and whipsaws back to touch the prior-day POC *within the exact same 5-minute event bar*, `returned` evaluates to `False` because outcome evaluation strictly begins at `e + 1`.
4. **Look-Ahead Risk**: Zero look-ahead leakage found. Prior day profile uses strictly $D-1$ bars, $R_{ref}$ uses the 1h bar closed at or before 00:00 UTC, and outcomes strictly follow event/acceptance bars.
5. **Costing**: Explicitly and transparently zeroed out as this is a non-trading frequency count; claims are carefully bounded to not assert an actionable trading edge.

---

## 2. Systematic Audit of Specific Dimensions

### A. Look-Ahead Risks

- **Audit**: Verified data indexing in profile construction, volatility reference anchor, event triggering, and outcome tracking.
- **Lines Audited**:
  - `MyTradingSys/backtest/vp_return_to_value.py:94` (Profile construction): Uses `l5[pa:pb], h5[pa:pb], v5[pa:pb]` corresponding to day `d - 1`.
  - `MyTradingSys/backtest/vp_return_to_value.py:98-100` ($R_{ref}$ calculation): `k = int(np.searchsorted(t1 + P.HOUR_MS, day_start, side="right")) - 1`. This takes the 1h bar closed strictly at or before 00:00 UTC of day $D$.
  - `MyTradingSys/backtest/vp_return_to_value.py:51-54` (Event & Return): `e = int(np.argmax(out))`, outcome checked on `h[e + 1:], l[e + 1:]`.
  - `MyTradingSys/backtest/vp_return_to_value.py:61-65` (Part B Acceptance): `seg = c[e:e + n]`, outcome checked on `h[e + n:], l[e + n:]`.
- **Finding**: **NO LOOK-AHEAD FOUND**.
- **Reproducing Verification**:
  ```python
  # Modifying future bars after the event does not shift event bar or acceptance
  import vp_return_to_value as V
  levels = {"poc_price": 100.0, "vah": 110.0, "val": 90.0}
  h1, l1, c1 = [105, 115, 112], [102, 111, 108], [104, 112, 110]
  h2, l2, c2 = [105, 115, 999], [102, 111, 50],  [104, 112, 500]
  r1 = V.analyse_day(levels, h1, l1, c1)
  r2 = V.analyse_day(levels, h2, l2, c2)
  assert r1["event"] == r2["event"] == 1
  ```

---

### B. Selection & Horizon Censoring Effects

- **Finding 1: Boundary Bar Censoring in Part B (`applicable`)**:
  - **Location**: `MyTradingSys/backtest/vp_return_to_value.py:58`, `MyTradingSys/backtest/vp_return_to_value.py:65`
  - **Mechanics**:
    ```python
    58: applicable = e + n - 1 <= len(c) - 1
    ...
    65: ret = _touch(h[e + n:], l[e + n:], poc)
    ```
    When `e + n - 1 == len(c) - 1`, the $N$-th confirmation bar is the very last 5m bar of the day (index `len(c) - 1`). The slice `h[e + n:]` is `h[len(c):]`, which is empty `[]`. `_touch` returns `False`.
    Thus, an event accepted on the final bar is deemed "applicable", but has an impossible outcome horizon (0 bars remaining), artificially driving `returned = False`.
  - **Reproducing Input**:
    ```python
    import vp_return_to_value as V
    levels = {"poc_price": 100.0, "vah": 110.0, "val": 90.0}
    # 3 bars in total: bar 0, 1, 2. e=0, n=3.
    # Bar 0, 1, 2 all close > 110.
    r = V.analyse_day(levels, [116, 116, 116], [114, 114, 114], [115, 115, 115], ns=(3,))
    # Output: applicable=True, accepted=True, returned=False (empty scan slice)
    assert r["acc"][3]["applicable"] is True
    assert r["acc"][3]["returned"] is False
    ```
  - **Impact**: Minor in practice on 288-bar days, but conceptually creates a guaranteed failure arm whenever acceptance coincides with the session close.

- **Finding 2: Intraday Event-Bar Return Censoring**:
  - **Location**: `MyTradingSys/backtest/vp_return_to_value.py:53`
  - **Mechanics**:
    ```python
    53: returned = _touch(h[e + 1:], l[e + 1:], poc)
    ```
    If bar `e` breaks outside VAH (e.g., opens at 108, runs down to 99 touching POC at 100, then surges to close at 115 > VAH 110), the POC touch occurred on the event bar itself. However, because `returned` scans `h[e + 1:]`, this touch is ignored. If price stays above VAH for the rest of the day, it is recorded as `RUN-AWAY` (`returned = False`).
  - **Reproducing Input**:
    ```python
    import vp_return_to_value as V
    levels = {"poc_price": 100.0, "vah": 110.0, "val": 90.0}
    # Event bar 0 has low 99 <= POC 100 <= high 116, close 115
    # Bar 1 stays above value (close 112, low 111)
    r = V.analyse_day(levels, [116, 114], [99, 111], [115, 112])
    # Output: event=0, returned=False
    assert r["event"] == 0
    assert r["returned"] is False
    ```
  - **Impact**: Under Tom's qualitative definition ("leaves value and strives to run back"), touching the POC during the breakout bar could be argued as having satisfied the return condition. The study enforces a strictly causal "breakout first, return later" definition.

- **Finding 3: Fixed UTC 24h Day-Window Truncation**:
  - **Location**: `MyTradingSys/backtest/vp_return_to_value.py:86`, `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:16`
  - **Mechanics**: The return window is strictly bounded at 23:55 UTC of the same day. If an event occurs at 23:45 UTC, it has only two 5m bars to return to POC.
  - **Impact**: As noted in `RESULT.md`, fire rate is 95.6% (real) and 96.9% (placebo) across 911 days (SOURCED: `results.json`). Events occurring in Asian or early London sessions have up to 20+ hours to return, while late NY session events have minutes.

---

### C. Missing Cost & Execution Realism

- **Finding**: **NO MISSING COST ISSUE (NOT A TRADE TEST)**.
- **Citation**: SOURCED `PRE_REG.md:5`: `"prereg_gate.py (count-only R-edge gate: needs sd of per-event R and a cost) does not apply: there is no R, no cost, no edge claim here. DECISION (OURS): skipped, reason written."`
- **Citation**: SOURCED `PRE_REG.md:31`: `"0a Cost: NA, no trade, no cost (nothing from fees.py is used)."`
- **Evaluation**: The study scrupulously labels itself as a pure count of an educational claim (70/30 frequency), not an alpha strategy. There are no claims of profitable execution, spread capture, or taker fees.

---

### D. Sample Size ($N$) & Statistical Power

- **Sample Size ($N$)**:
  - Real event sample size: $N = 871$ days with events out of 911 complete UTC days (SOURCED: `results.json:A.real.n`).
  - Placebo event sample size: $N = 883$ (SOURCED: `results.json:A.placebo.n`).
  - Part B accepted events:
    - $N = 3$: 603 accepted (SOURCED: `results.json:B.3.real.n`)
    - $N = 6$: 490 accepted (SOURCED: `results.json:B.6.real.n`)
    - $N = 12$: 387 accepted (SOURCED: `results.json:B.12.real.n`)
- **Evaluation**:
  - All sample sizes exceed the $N \ge 100$ threshold required by `underpowered()` in `vp_return_to_value.py:177-178`.
  - Statistical testing uses 2,000 day-block bootstrap resamples (seed `20261009`, SOURCED: `vp_return_to_value.py:150`).
  - Power is well-sufficient to falsify Tom's 70% claim (observed 57.2%, 95% CI: [53.9%, 60.7%], SOURCED: `RESULT.md:12`).

---

### E. Claims Outrunning the Data

- **Finding**: **CLAIMS ARE WELL-BOUNDED AND DO NOT OUTRUN THE DATA**.
- **Audit Points**:
  - The authors explicitly highlight in `RESULT.md:14`:
    > *"Caution (post-hoc, OURS): placebo bands within 1 ATR of the real value return 55.8% vs real 55.0% on the same days (difference -0.8 pp, CI -5.2..3.7), so the pooled excess comes from the far-shifted bands; a band near value behaves like value."*
  - The study acknowledges that Tom's qualitative 70% frequency fails to reproduce on BTC UTC daily profiles (57.2% vs 70.0%).
  - The study explicitly refrains from proposing an entry rule or promoting this to an alpha signal.

---

## 3. Items That Could Not Be Checked

1. **Tom's Original Cash-Session Levels**:
   - In video `BB3c8visnkI`, Tom uses cash-session futures profiles (RTH / ETH on equity indices / commodities). BTC trades continuous 24/7 without a designated cash session. Whether Tom's 70% claim holds on CME BTC futures cash sessions (09:30-16:00 ET) cannot be evaluated from spot binance 1m data (`NOT_IN_DATA`).
2. **Low Volume Node (LVN) Boundaries**:
   - Tom refers to acceptance beyond the LVN bordering the value area. The 18.1 volume profile builder (`FORMULAS.md:422`) computes only POC, VAH, and VAL (70% density) with fixed $10 bins; it does not identify multi-modal LVN valleys. Thus, LVN-specific acceptance could not be checked.
3. **Execution Fills at POC**:
   - Range touch ($Low \le POC \le High$) was counted, but queue priority or limit fill probability at the exact POC price was not simulated (`NOT_IN_DATA`).

---

## 4. Summary Table of Audit Findings

| Category | Status | File & Line Reference | Notes / Reproducing Edge Case |
|---|---|---|---|
| **Look-Ahead** | **NO ISSUE FOUND** | `vp_return_to_value.py:51-65, 94-100` | Strict causal separation of D-1 profile, 00:00 UTC ATR, and post-event bars |
| **Selection / Censoring** | **ISSUE IDENTIFIED** | `vp_return_to_value.py:58, 65` | Boundary bar acceptance ($e+n-1 = 287$) yields 0 remaining bars, forcing `ret=False` |
| **Selection / Censoring** | **ISSUE IDENTIFIED** | `vp_return_to_value.py:53` | POC touch within the breakout bar itself is not counted as return |
| **Missing Cost** | **NO ISSUE FOUND** | `PRE_REG.md:5, 31` | Explicitly justified as non-trading frequency count; no edge claimed |
| **Sample Size ($N$)** | **NO ISSUE FOUND** | `results.json:A, B` | DEV $N=871$ events (Part A), $N \ge 387$ (Part B); well above $N=100$ floor |
| **Claims vs Data** | **NO ISSUE FOUND** | `RESULT.md:12-16` | Fair disclosure of near-placebo parity (-0.8 pp) and rejection of 70% claim |

Noticed: The near-placebo finding (|d| <= 1 ATR returning 55.8% vs real 55.0%) is a clean demonstration of how baseline geometric reversion of continuous price processes can masquerade as volume-profile specific edge if far-shifted placebos are relied upon without local stratification.
