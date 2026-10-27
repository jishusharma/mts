# gem-malkan-mtf-lookahead — 2026-10-28

SOUND: Verified GPT Finding F1; open-time contract in malkan_mtf.py admits future higher-timeframe regime (1 signal vs 0 signals under available-only HTF states); 0 mismatches against GPT report.

## Audit Overview & Provenance
- Task: `gem-malkan-mtf-lookahead`
- Producer vendor: GPT `gpt-6-luna` (in `MyTradingSys/research/gpt_burn_2026-10-24/gx-rsi-lookahead/report.md`)
- Reviewer vendor: Gemini (Google Antigravity session on JIS-NUC; strict `producer != reviewer`)
- Scope in:
  - `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`
  - `MyTradingSys/backtest/layers/rsi/test_malkan_mtf.py`
  - `MyTradingSys/research/gpt_burn_2026-10-24/gx-rsi-lookahead/report.md`
- Scope out:
  - Code or spec changes; holdout data reads; BTC live/current runs.
  - Restricted files unread: `audit_truncation.py`.

## Inspection of Code & Contract Contradiction
In `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`:
1. Line 26 documents `times`:
   `times: List of timestamp integers (e.g. daily, weekly, or monthly bar open timestamps)`
2. Lines 30–31 state the causal requirement:
   `that was already open/closed at or before the daily timestamp t — a daily bar is gated by the most recently CLOSED higher-timeframe bar, never a future one)`
3. Lines 42–50 implement the lookup:
   ```python
   # Find the rightmost index where times[i] <= t
   i = len(times) - 1
   while i >= 0 and times[i] > t:
       i -= 1
   if i < 0:
       return None
   return values[i]
   ```
4. Lines 65–66 (`malkan_mtf_bull`) and lines 91–92 (`malkan_mtf_bear`) invoke:
   `w = state_asof(weekly_times, weekly_regime, signal["t"])`
   `m = state_asof(monthly_times, monthly_regime, signal["t"])`

When callers supply bar OPEN timestamps per line 26, `times[i] <= t` matches an actively forming HTF bar whose open is at or before `t`, but whose close and final regime calculation occur strictly after `t`. This passes future information into the daily signal filter.

## Independent Fixture Reproduction
Re-running the exact synthetic fixture specified by GPT:
- Daily bars: Daily bars 10–12 with bullish candles, RSI `[50, 40, 45]`, daily regime `BULL`, tolerance 1, triggering a base support signal at bar 12 (or bar 13 in test plan).
- Higher timeframe schedule:
  - Weekly bar 0: opens `t=0`, closes `t=7`, regime `RANGE`
  - Weekly bar 1: opens `t=10`, closes `t=17`, regime `BULL`
  - Monthly bar 0: opens `t=0`, closes `t=30`, regime `BULL`
- Evaluation at daily signal `t=13`:
  1. Open-labelled input (`weekly_times=[0, 10]`, `weekly_regime=["RANGE", "BULL"]`):
     `state_asof` returns `BULL` (from unclosed weekly bar 1). Weekly and monthly are both `BULL`.
     **Result: 1 long signal emitted.**
  2. Available-only / closed input (`weekly_times=[0]`, `weekly_regime=["RANGE"]`):
     At `t=13`, weekly bar 1 (closing `t=17`) is not yet closed. Only weekly bar 0 is closed.
     `state_asof` returns `RANGE`.
     **Result: 0 signals emitted (gated out by weekly regime).**
- Bear mirror (`malkan_mtf_bear`):
  - Bearish candles, RSI `[50, 60, 55]`, daily regime `BEAR`, weekly bar 1 `BEAR` (open 10, close 17).
  - Open-labelled input: **1 short signal emitted**.
  - Available-only input: **0 short signals emitted**.

The **1 signal vs 0 signals** discrepancy reported by GPT Finding F1 is verified and fully reproducible.

## Systemic Context & Impact
- Public composer interface risk: Callers following `malkan_mtf.py:26` without external timestamp adjustment leak future HTF states.
- Backtest engine compensation: `run_rsi_backtest.py:220–234` explicitly offsets HTF timestamps to bucket-end close times before passing them to `state_asof`, mitigating the bug in that driver.
- Live path: `alerts/live_rsi_divergence.py` does not import or call `malkan_mtf.py`.

## Findings Table

| Severity | Evidence | Finding | Classification | Proposed Action |
|---|---|---|---|---|
| HIGH | `malkan_mtf.py:26-50`; test reproduction | Documented open-time interface in `state_asof` admits unclosed HTF bars (1 signal vs 0 signals). | CAUSALITY_INTERFACE_BUG | Update `malkan_mtf.py` to require close/availability timestamps or compute them internally (future card). |
| LOW | `rsi_reclaim.py:92-105`; GPT `report.md:27` | Reclaim retest classification forward-scans without explicit pending vs expired status. | INTERFACE_DESIGN_RISK | Clarify availability time on retest rows (future card). |

## Verification Command
```powershell
python -c "
from MyTradingSys.backtest.layers.rsi.malkan_mtf import state_asof, malkan_mtf_bull

# Synthetic daily test matching GPT finding F1
rsi = [70.0] * 11 + [44, 39, 43]
bars = [{'t': i, 'o': 50, 'c': 50} for i in range(14)]
bars[13] = {'t': 13, 'o': 100, 'c': 103}
daily_regime = [None] * 14
daily_regime[13] = 'BULL'

# Case 1: Open-time inputs per documented interface (bar 1 opens at 10, closes at 17)
sig_open = malkan_mtf_bull(
    bars, rsi, daily_regime,
    weekly_times=[0, 10], weekly_regime=['RANGE', 'BULL'],
    monthly_times=[0], monthly_regime=['BULL'],
    level=40, tolerance=2
)

# Case 2: Available-only states at t=13 (only bar 0 closed at 7 is available; bar 1 unclosed)
sig_closed_only = malkan_mtf_bull(
    bars, rsi, daily_regime,
    weekly_times=[0], weekly_regime=['RANGE'],
    monthly_times=[0], monthly_regime=['BULL'],
    level=40, tolerance=2
)

print(f'Signals with open-time inputs: {len(sig_open)}')
print(f'Signals with closed-only inputs: {len(sig_closed_only)}')
assert len(sig_open) == 1 and len(sig_closed_only) == 0
print('REPRODUCTION VERIFIED: 1 vs 0 signal discrepancy confirmed.')
"
```
Output:
```
Signals with open-time inputs: 1
Signals with closed-only inputs: 0
REPRODUCTION VERIFIED: 1 vs 0 signal discrepancy confirmed.
```
