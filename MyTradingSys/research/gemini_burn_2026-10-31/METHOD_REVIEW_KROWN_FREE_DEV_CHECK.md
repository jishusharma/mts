# Method Review: Krown Free Setups DEV Check (Commit abf939506)

**Target Commit:** `abf939506231b994cad22803ac521e395ee24af3` (SOURCED: `git show abf939506`)  
**Target Study:** Krown Free Setups DEV Check (`MyTradingSys/research/krown_free_2026-10-31/`)  
**Reviewer:** Gemini (Cross-vendor Method Review)  
**Date:** 2026-10-31 (UTC)  
**Evaluation Dimensions:** Look-Ahead, Selection Effects, Missing Costs, Sample Size ($n$), Claims Stronger Than Data, Unchecked Elements.

---

## Executive Summary

Commit `abf939506` implements a DEV-only verification of Eric Krown's "free trade setups" from YouTube captions, focusing specifically on the **Silver Cross (Daily EMA 21 up-cross EMA 55 with 30-day hold)**.

The implementation displays strong experimental hygiene:
- A pre-registration document was frozen prior to outcome evaluation (`PRE_REG.md:64` SHA-256 `a6a0ab3e52d557d097d0cdbd4283d8b4dd54c6b7a6fe7682ab07ce4577a43020`, enforced in code at `silver_cross_dev.py:27-32`).
- Strict DEV boundaries are enforced with an explicit cutoff timestamp rejecting any bar at or after 2024-07-01 (`silver_cross_dev.py:21,41-42`).
- Look-ahead was checked via one-bar causality truncation, future bar perturbation, and static linting (`silver_cross_dev.py:61-68`, `test_silver_cross_dev.py:53-67`).
- Pre-declared statistical verdict was `INCONCLUSIVE` due to low $n$ (`PRE_REG.md:58-61`, `DEV_CHECK.md:5,11`).

However, the method review identifies key methodological nuances, selection biases, cost considerations, and sample limitations detailed below.

---

## 1. Look-Ahead Risk Audit

### Findings: NO CRITICAL ISSUE FOUND (Low / Controlled Risk)
- **Signal Causality & Decision Point:**  
  - SOURCED: `MyTradingSys/research/krown_free_2026-10-31/silver_cross_dev.py:61-68`
  ```python
  def cross_up_days(close, fast=FAST, slow=SLOW):
      """Day indices t where diff(t-1) <= 0 and diff(t) > 0 (diff = EMA fast - EMA slow). Uses closes up to t only."""
      close = np.asarray(close, dtype=float)
      if len(close) < 2:
          return np.array([], dtype=int)
      diff = ema(close, fast) - ema(close, slow)
      return np.flatnonzero((diff[:-1] <= 0) & (diff[1:] > 0)) + 1
  ```
  Execution entry is at `open[t+1]` (the open of the next day after cross completion on `close[t]`), preventing same-bar fill look-ahead (`silver_cross_dev.py:77`).
- **Reproducing Verification Check:**  
  `test_one_bar_shift_causality` in `test_silver_cross_dev.py:53-56` confirms signal at $t$ depends strictly on data up to $t$.
- **Allowlist Additions:**  
  Commit `abf939506` added two entries to `scripts/dev/lookahead_allowlist.tsv:333-334` for forward index in the baseline unconditional calculation (`silver_cross_dev.py:116-117`).  
  SOURCED: `scripts/dev/lookahead_allowlist.tsv:333`
  ```text
  MyTradingSys/research/krown_free_2026-10-31/silver_cross_dev.py	fwd-index	allnet = np.array([d["open"][i + HOLD] / d["open"][i] - 1 - FEE_RT for i in range(first_day, len(day) - HOLD)
  ```
  Audit confirms this forward index is used exclusively in computing an unconditional baseline 30-day buy-and-hold outcome across all days, completely isolated from the event signal path.

---

## 2. Selection Effect & Setup Triage

### Findings: ISSUE IDENTIFIED (Discretionary Setup Pruning / Survivorship)
- **Citation:** `MyTradingSys/research/krown_free_2026-10-31/PRE_REG.md:9-24` and `DEV_CHECK.md:13-17`
- **Description:**  
  Out of 6 setup families extracted from Krown's channel, 5 were deemed `NOT_TESTABLE` due to missing formal definitions in the video captions (e.g. "Free AI Bot" proprietary indicator, undefined "reconnect" conditions, or target rules without stops/horizons). Only the Silver Cross 1-month hold was selected for testing.
- **Selection Effect Impact:**  
  Testing only the setup that possesses trivial mathematical definitions (2 moving averages and a fixed calendar exit) introduces an analyst selection effect: the tested setup is not necessarily representative of Krown's typical discretionary trading framework or performance claims across his full roster of free setups.
- **Reproducing Input / Context:**  
  In `KROWN_FREE_SETUPS.md:65-70`, Krown claimed 83% green with median return 22.1% on the "10-Day Reconnect + Stoch Stack" (`ro6tMlqbbBI`), but this was excluded because "reconnect" lacked an objective touch/close rule in captions (`PRE_REG.md:16-18`).

---

## 3. Cost & Execution Modeling

### Findings: MINOR ISSUE / REALISTIC SPREAD & SLIPPAGE OMISSION
- **Citation:** `MyTradingSys/research/krown_free_2026-10-31/silver_cross_dev.py:18,79-80`
- **Code:**
  ```python
  FEE_RT = 2 * fees.BINANCE_TAKER                  # SOURCED fees.py (0.10 % round trip)
  gross = opens[xi] / opens[ei] - 1.0
  net = gross - FEE_RT
  ```
- **Description:**  
  The study sources exchange taker fees from `backtest/fees.py` ($2 \times 0.05\% = 0.10\%$ round trip). However, execution slippage and bid-ask spread costs are omitted (modeled as 0.00%).
- **Impact Assessment:**  
  In `DEV_CHECK.md:32`, the author noted that two losses were near zero:
  - 2023-06-23: net -0.41% (gross -0.31%)
  - 2024-05-18: net -0.59% (gross -0.49%)  
  Because average net return was +7.87% across a 30-day hold, a typical 2–5 bps slippage would not materially change the hit rate ($3/6$) or the inconclusive verdict, but for tight boundary trades near zero return, execution frictions are non-trivial.

---

## 4. Sample Size ($n$) and Statistical Power

### Findings: MAJOR ISSUE (Severely Underpowered Sample, Properly Disclaimed)
- **Citation:** `MyTradingSys/research/krown_free_2026-10-31/DEV_CHECK.md:5,11,47-51`
- **Metrics:**  
  - Total Events: $n = 6$ (OURS, SOURCED: `RESULT.csv:3`)
  - Total Resampling Blocks: $n_{\text{blocks}} = 5$ (events on 2023-10-08 and 2023-10-17 overlap in the 30-day hold window, `RESULT.csv:4`, `DEV_CHECK.md:31`)
  - Hit Rate: $50.0\%$ (3 of 6 green fee-net, `RESULT.csv:5`)
  - 95% Bootstrap Confidence Interval: $[0.0\%, 87.5\%]$ (`RESULT.csv:10-11`)
- **Description:**  
  With $n = 6$, the standard error of a binomial proportion $\hat{p} = 0.5$ is $\sqrt{0.5 \times 0.5 / 6} \approx 0.204$. The 95% confidence interval spans virtually the entire probability simplex ($[0\%, 87.5\%]$).  
- **Verdict & Hygiene:**  
  The study appropriately pre-registered the verdict as `INCONCLUSIVE` regardless of point estimate (`PRE_REG.md:58-61`). It did not claim "no edge" or "edge proven".

---

## 5. Claims Stronger Than Data

### Findings: NO FABRICATION / CLAIMS STRICTLY BOUNDED
- **Citation:** `MyTradingSys/research/krown_free_2026-10-31/DEV_CHECK.md:47-52`
- **Audit:**
  - Krown claimed "83% of the time it is green" on a 1-month hold since 2018 (`bXug2l6qICc` [00:03:08]).
  - The DEV check found $50.0\%$ ($3/6$).
  - Crucially, `DEV_CHECK.md:47` refrains from claiming Krown was refuted:
    > "It does not confirm his 83 %. With 6 events the 95 % CI of the hit-rate spans 0 % to 87.5 %, so 83 % is inside the interval: it neither supports nor rejects the claim."
  - The report explicitly warns that Krown's sample covered 2018–2024, whereas the DEV window is restricted to 2022-04-01 to 2024-06-30 (`DEV_CHECK.md:49-50`).

---

## 6. What Could Not Be Checked

1. **Full Historical History (2018 to March 2022):**  
   Cannot be evaluated without reading data outside the DEV partition or accessing pre-DEV archives, which is forbidden under the DEV scope constraint (`PRE_REG.md:23-24`).
2. **Krown's Exact Exit and Timing Rules:**  
   In video `bXug2l6qICc` [00:03:08], Krown states "if we fast forward just one month out from that cross". Whether he evaluated this on daily closes, specific intraday hours, or calendar 30 days vs 31 days is unspecified in the video captions. The 30 calendar days exit at daily open is an operationalized proxy (OURS).
3. **Proprietary Indicators / Unstated Parameters:**  
   The remaining 5 setup groups (e.g. Range Deviation indicator, Chandelier exit, 5 EMA reconnect definitions) cannot be checked because proprietary trading software was unreachable and code formulas were absent (`KROWN_FREE_SETUPS.md`, `PRE_REG.md:12-22`).
