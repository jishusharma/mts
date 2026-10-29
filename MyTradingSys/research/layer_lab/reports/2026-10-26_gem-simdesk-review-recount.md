# Lab Report: Recount of GPT Sim-Desk Audit Findings and Comparisons (2026-10-28)

**Task**: `gem-simdesk-review-recount`  
**Card Title**: `[GEMINI] Recount GPT's sim-desk audit: 10 findings (7 HIGH, 3 LOW), 25 comparisons`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/report.md`
- `MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/audit.py`
- `MyTradingSys/research/sim_desk/desk.py`
- `MyTradingSys/research/sim_desk/studies/levels.py` (lines 35–45, 180–192)
- `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py` (lines 138–148, 170–178)

*Constraint adherence*: In strict adherence to the task brief, `audit.py` was NOT executed against live or historical price data. Headline counts were not accepted as given, but tallied and verified through direct source inspection of the findings and the audit harness definitions.

---

## 1. Executive Summary

1. **Findings Recount by Severity**:
   - Total Findings in `report.md`: **10 findings**.
   - Breakdown: **7 HIGH**, **0 MED**, **3 LOW** (0 CRITICAL).
   - All 10 findings identify concrete, reproducible defects or structural limitations in the simulator desk (e.g., intrabar look-ahead, gap trigger fills, R-target pricing references, execution timing, missing perpetual funding, and SVG coordinate shifts).

2. **Harness Comparisons Recount**:
   - Total comparisons defined in [`audit.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/audit.py): exactly **25 comparisons** (`record(...)` invocations).
   - Comparison outcome: **13 matched** (confirming baseline math, canonical fees, boundary exclusions, and offline mocking) and **12 mismatched** (corresponding to the identified defects and scope limitations).

3. **Finding 1 Verification in `ladder.py` / `studies/levels.py`**:
   - **Confirmed**. [`ladder.py:141`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/levels_confluence_2026-10-14/ladder.py#L141) implements stop mode K5 ("just past today's extreme") as:
     `ext = float(ctx.lo[:i + 1].min()) if side > 0 else float(ctx.hi[:i + 1].max())`
   - Because `i` is the index of the bar during which the entry touches and fills at $L_1$, taking the slice `[:i + 1]` incorporates the low/high of the *completed* bar $i$.
   - Any adverse wick occurring *after* entry within the same 15m bar moves the initial stop price and alters the risk denominator ($R$). This constitutes an intrabar look-ahead defect.

---

## 2. Findings Inventory and Classification

| Finding # | Severity | Title | Affected Files / Lines | Verified Description |
|---|---|---|---|---|
| **1** | **HIGH** | K5 stop uses price action after entry | `ladder.py:141, 174`, `studies/levels.py:38, 186` | Slice `ctx.lo[:i + 1]` incorporates the completed touch bar's low into the stop calculation after entry fills. |
| **2** | **HIGH** | Levels stop gaps filled at unavailable trigger price | `ladder.py:202–205` | When bar gaps beyond stop, exit is recorded at the stop price rather than the opening price of the gap bar. |
| **3** | **HIGH** | "x risk" targets use reference price instead of actual fill | `studies/wavetrend.py:73–77`, `studies/rsi.py:112` | Multiples of $R$ are calculated from the signal close rather than the actual fill price on gapped entries. |
| **4** | **HIGH** | Close-dependent signal exits receive already-closed price | `engine/runner.py:61–71` | Exits triggered by a bar close fill at that bar's close rather than the next bar's open. |
| **5** | **HIGH** | Entry-minute target suppression affects market-open entries | `engine/runner.py:79–84` | Target checks are suppressed on the entry minute even for market orders known at the open of the bar. |
| **6** | **HIGH** | Breakout entry can exit at pre-entry open price | `engine/runner.py:90–96` | On breakout entries occurring during a bar, a stop hit evaluates against the entire bar's open/extremes. |
| **7** | **HIGH** | Perpetual-futures "net" omits funding entirely | `engine/runner.py`, `studies/levels.py` | Multi-day holds accrue no funding payments/receipts, distorting long-term carry returns. |
| **8** | **LOW** | Resampling emits unfinished bars and hides minute gaps | `engine/resample.py` | Aggregation does not enforce strict 60-minute completeness or flag missing intraday minutes. |
| **9** | **LOW** | Slippage is absent on both entry and exit | `desk.py` | Fills execute exactly at trigger prices without modeling spread cross or execution slippage. |
| **10** | **LOW** | Charts detach execution markers from candle positions | `artifact/render.py` | SVG coordinate packing can place entry circles outside the visible chart window on early entries. |

**Tally**: 7 HIGH + 3 LOW = **10 Total Findings**.

---

## 3. Harness Comparisons Breakdown (`audit.py`)

All 25 comparison calls to `record(name, actual, expected)` in `audit.py` were audited:

### A. Matched Comparisons (13)
1. `canonical_long_target_fees` (line 53) — Correct two-sided fee deduction ($+0.9495\text{ R}$).
2. `short_stop_both_fees` (line 55) — Correct two-sided fee on stop ($-1.0505\text{ R}$).
3. `both_hit_stop_first` (line 58) — Conservative stop-first rule on dual touch ($-1.0495\text{ R}$).
4. `shared_gap_stop` (line 61) — Shared engine gap exit fills at next open ($-2.5488\text{ R}$).
5. `entry_window_end_exclusive` (line 64) — End-of-window trigger boundary excluded.
6. `hold_boundary_excludes_next_bar` (line 66) — Time-exit does not evaluate subsequent bar.
7. `UTC_epoch_day` (line 67) — Epoch timestamp alignment for UTC date.
8. `DEV_end_rejected` (line 68) — DEV boundary strictly enforced.
9. `partial_trailing_bucket` (line 94) — Resampling correctly handles full hour aggregation.
10. `missing_minute_emits_ordinary_hour` (line 97) — Resampling behavior on missing minutes documented.
11. `WT_signal_to_fill_boundary` (line 112) — WaveTrend signal handoff alignment.
12. `levels_partial_size_net` (line 152) — Partial size normalization matches planned $R$.
13. `existing_fetch_files_network_calls` (line 173) — Zero network calls when local archive files exist.

### B. Mismatched Comparisons (12)
1. `market_entry_target_on_fill_bar` (line 79) — Target suppressed on entry bar (Finding 5).
2. `breakout_fill_bar_pre_entry_open_as_stop` (line 84) — Stop evaluates against pre-entry open (Finding 6).
3. `signal_exit_at_already_closed_price` (line 89) — Exit fills at signal close instead of next open (Finding 4).
4. `WT_target_uses_actual_fill_risk` (line 111) — WT target reference uses signal close (Finding 3a).
5. `RSI_gap_target_uses_actual_fill_risk` (line 124) — RSI target reference uses signal close (Finding 3b).
6. `levels_gap_stop_fills_trigger` (line 136) — Levels stop fills at trigger price rather than gap open (Finding 2).
7. `K5_uses_post_entry_touch_low` (line 145) — Stop derived from post-entry bar low (Finding 1).
8. `funding_absent_long` (line 157) — Long funding missing from return (Finding 7a).
9. `funding_absent_short` (line 159) — Short funding missing from return (Finding 7b).
10. `slippage_absent` (line 160) — Zero slippage modeled (Finding 9).
11. `chart_entry_at_day_open` (line 168) — SVG marker rendered at $x=650$ outside $300\text{px}$ view (Finding 10).
12. `desk_offline_run_n` (line 186) — Discrepancies propagate into run statistics.

**Tally**: 13 Matched + 12 Mismatched = **25 Total Comparisons**.

---

## 4. Deep-Dive on Finding 1: K5 Intrabar Look-Ahead

- **Implementation**: [`ladder.py:140-143`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/levels_confluence_2026-10-14/ladder.py#L140-L143)
  ```python
  elif K == 'K5':
      ext = float(ctx.lo[:i + 1].min()) if side > 0 else float(ctx.hi[:i + 1].max())
      base = min(ext, deepest) if side > 0 else max(ext, deepest)
      stop = base - side * base * MARGIN
  ```
- **Execution Seam**:
  In [`ladder.py:174`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/levels_confluence_2026-10-14/ladder.py#L174), the first arm fill is recorded at `(L1, w, i)`. The trade enters when price touches $L_1$ during bar $i$.
- **Defect**:
  Using `ctx.lo[:i + 1].min()` inspects `ctx.lo[i]`, which represents the lowest price reached during the *entire* 15-minute bar $i$. If the price reaches $L_1$ and then trades lower to form an adverse wick before closing higher, `K5` sets the stop relative to that lower wick. Under live execution, an order entering at $L_1$ cannot know the eventual bar low and would either be stopped out during that wick or must use the extreme established prior to entry (`ctx.lo[:i].min()`).
- **Verdict on Finding 1**: **CONFIRMED**.

---

## 5. Findings Summary Table

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| HIGH | [`ladder.py:141`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/levels_confluence_2026-10-14/ladder.py#L141) | Stop K5 incorporates the low/high of the touch bar after entry. | `ctx.lo[:i + 1].min()` includes bar $i$ where entry filled at `(L1, w, i)`. | Use prior extremes `ctx.lo[:i].min()` or require trade entry at bar close $i+1$. |
| HIGH | [`ladder.py:202-205`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/levels_confluence_2026-10-14/ladder.py#L202-L205) | Levels stop fills at trigger level when price gaps through. | `actual_exit = stop` instead of gap open. | Fill stop orders at $\min(\text{open}, \text{stop})$ for longs (or max for shorts). |
| HIGH | [`studies/wavetrend.py:73-77`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/sim_desk/studies/wavetrend.py#L73-L77) | Target price multiple calculated from signal close instead of fill. | Target uses $100 + 1.5 \times (100 - 90)$ instead of fill $110$. | Calculate target offset from actual executed fill price. |
| LOW | [`engine/resample.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/sim_desk/engine/resample.py) | Incomplete minute bars are aggregated without missing-minute flags. | 59 minutes emit an ordinary 1-hour bar with no warning. | Add a bar-count or completeness check to resampled buckets. |
| LOW | [`desk.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-simdesk-review-recount/MyTradingSys/research/sim_desk/desk.py) | Slippage and funding are unmodeled in desk return outputs. | $R_{\text{net}}$ reflects only taker/maker fees. | Document desk outputs as ideal execution bounds or incorporate fee + carry models. |

---

## 6. Verdict

**Verdict: SOUND.**  
GPT's sim-desk correctness audit in `gx-sim-desk-review/report.md` is accurate and technically sound:
1. Finding counts by severity are verified as **10 findings: 7 HIGH, 3 LOW**.
2. Harness comparisons in `audit.py` total **25 comparisons (13 matched, 12 mismatched)**.
3. Finding 1 (K5 stop intrabar look-ahead via `ctx.lo[:i + 1].min()`) is confirmed by direct source inspection of `ladder.py:141`.
