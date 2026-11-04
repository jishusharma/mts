# PRE_REG: OURS bear proxy per context (Part A) and fake-out filter per timeframe (Part B) (frozen 2026-11-04, before any return was read)

Order: `d-bear-proxy-per-context-defaults-1104` in `MyTradingSys/system/OPERATOR_DECISIONS.md` (operator, chat). Code: `study.py`; tests `test_wiring.py`.
Counts (no returns) are in `A_count.csv`, `B_count.csv`; the gate lines are in the section below. Every tuned parameter in this file is **OURS**.
The SOURCED Malkan weekly-AND-monthly <= 40 gate and `d-bear-proxy-1104` (weekly RSI14 <= 40, close below SMA200) stay the baseline; nothing here edits them.

## Data and split (same as `rsi_divergence_mtf_gated_2026-11-04/PRE_REG_LONG.md`)

- Binance SPOT klines (not futures, no splice) BTCUSDT + ETHUSDT, read at 15m/1h/4h/1d from `F:/MTS/Dumps/backtest/spot_2017`; weekly bars resampled from spot 1d. Pooled across both symbols, clustered by UTC day.
- DEV = signal-bar closes 2017-08-01..<2024-07-01 (2017-08..2021-12 is NEW DEV data, PRE_DEV in splits.py terms). VALIDATION = 2024-07-01..<2025-07-01, read once, picks only. HOLDOUT (2025-07-01+) is never loaded (loader end = window end).
- Cost 0.14 % round trip (research_kit, SOURCED). Signal = close-pivot Malkan RSI14 divergence, arm W12 (3..12 bars, STRONG) only; entry and exit rules below. Exit = close 10 bars after the entry bar (OURS, as siblings). Gaps in the spot archive are not filled ("10 bars" = bars present).

## Part A: bear proxy per context

Setting grid (24, OURS): RSI length {14, 21} x threshold {35, 40, 45} x proxy timeframe {1d, 1w} x SMA200 filter {on, off}. Proxy is ON at day D (as-of the 00:00 UTC instant) when the last closed RSI(length) of the proxy TF is <= threshold AND (filter off OR the last closed daily close is below its SMA200). Baseline = (14, 40, 1w, on).
Signals: bearish close-pivot divergence, W12, 15m (the best powered TF in the siblings), signal-bar close entry, short, exit 10 bars later. Only shorts are tested because the gate is a bear gate.
Context cells (regime x phase): regime = `research_kit.regime_tag` primary (Malkan weekly+monthly 60/40 with SMA200 side, SOURCED) bull / range / bear; phase = age of the SMA200 side in daily closes at the signal, `fresh` <= 60 days, `mature` > 60 (OURS; `research_kit.phase_tag` is not used because its W1/H/R classes belong to tf_break events, not divergence signals). Cells: ALL (pooled) + 3 regimes x 2 phases = 7. The bear cells are expected empty (Malkan bear gate fires 0 weeks) and bull cells hold almost no weekly-proxy weeks; they are reported and capped, not dropped. Events with no regime (first ~15 months) are dropped from every row.
Measure per (setting, cell): fee-net mean of shorts INSIDE the proxy-on days, the same OUTSIDE, their difference (day-clustered `cluster_diff`), and the gate's own hit rate = fraction of proxy-on Monday weeks whose last closed daily close 4 weeks later is lower (reported beside the base rate of all weeks in the cell).
Pick on DEV only: per cell the setting with the highest inside fee-net mean among settings with n >= 30 and >= 20 days (no qualifying setting = null).

## Part B: fake-out filter per timeframe

TFs 15m, 1h, 4h, 1d. Signals: close-pivot divergence both kinds (bullish long, bearish short), W12, ungated by regime, pooled kinds and symbols.
**Fake-out (OURS, precise):** with ATR = simple mean of the true range over the last 14 bars at the entry bar j and entry price p, a trade is a fake-out when, within bars j+1..j+10, price reaches p - side x 1 ATR (adverse: low for long, high for short) on a bar strictly before the first bar that reaches p + side x 1 ATR (target); a bar touching both counts as adverse first. Not-reached-either is not a fake-out. Fake-out rate = fake-outs / trades.
Filters (OURS): (a) none = enter at the close of the event bar; (b) confirm1 = enter at the close of the next bar only if it closes beyond the event bar's close in the signal direction; (c) htf_rsi = last closed RSI14 of the next higher TF (15m->1h, 1h->4h, 4h->1d, 1d->1w) moved with the signal (long: higher than the closed bar before, short: lower); (d) volume = event-bar volume > mean volume of the 20 bars before it; (e) retest = `research_kit.retest_entry` at the swing-B close level, N = 10, fill at the level or the gapped open.
Measure per TF x filter: n, days, fake-out rate, fee-net mean and day-clustered 95 % CI. Pick on DEV only: per TF the highest fee-net mean among filters with n >= 30 and >= 20 days.

## Trial count (stated up front)

DEV evaluations: Part A 24 settings x 7 cells = 168; Part B 4 TFs x 5 filters = 20; total **188**. VALIDATION: at most one test per cell/TF = 7 + 4 = **11** (Holm family m = 11, unpicked cells counted as p = 1).

## Power gate (count-only, `scripts/dev/prereg_gate.py` formula, m = 11, cost 0.14, unit %, n = distinct DEV days, sd OURS: 15m 0.8 / 1h 1.9 / 4h 4.0 / 1d 10; max plausible gross 0.30 %)

- Part B: **15m PASS** on every filter (1670-2463 days, MDE 0.059-0.072 %); **1h, 4h, 1d BLOCK** on every filter (1h: 672-1616 days, MDE 0.17-0.27 vs 0.16 allowed; 4h and 1d far short). Blocked TFs are capped "no default: underpowered" whatever VALIDATION says.
- Part A baseline (14, 40, 1w, on): ALL 324 days BLOCK; range|mature 290 BLOCK; range|fresh 46 BLOCK; bull and bear cells 0 events BLOCK. Only threshold-45 settings PASS (ALL cell 364-548 days; range|mature 4 of 24). A threshold-45 pick can be tested; every other pick is capped.
- Fixed now: the DEV tables are descriptive for blocked cells. The verdict ceiling for a blocked cell is "no default: underpowered".

## Verdict rule (fixed now)

DEFAULT only if the picked cell is power-PASS and VALIDATION is fee-net with a day-clustered 95 % CI lower bound > 0 and Holm p < 0.05 (m = 11). Powered but not DEFAULT = FAIL. Blocked or no qualifying pick = "no default: underpowered". Otherwise the baseline stays: d-bear-proxy-1104 for Part A, entry at the event-bar close (no filter) for Part B. `defaults.json` holds cell -> setting or null.

## What the result will say

RESULT.md line 1 = `Regime mix:` for the DEV window; then one table per part: cell -> picked setting -> DEV -> VALIDATION -> verdict; the gate hit rates; fake-out rate before/after per TF.

## Context
Regime: Part A cells are the Malkan gate (`research_kit.regime_tag`, SOURCED: daily SMA200 side plus weekly/monthly RSI 60/40) crossed with the OURS bear-proxy settings; Part B is ungated by regime because the fake-out filter is a per-timeframe property, not a regime one.
Phase: Part A uses an OURS SMA200-side-age phase (fresh <= 60 daily closes / mature); `phase_tag` classes W1/H/R do not exist for divergence signals; Part B none, because it is per timeframe.
Session: none, because session tags (OURS) were not requested by this order.
Entry: Part A signal-bar close; Part B signal-bar close vs confirm1 / htf_rsi / volume / retest (N = 10, OURS) compared side by side.
