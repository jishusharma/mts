# PRE_REG: reclaim_close_stop re-derived on 10 symbols, out of sample 2024+ (frozen 2026-11-15, before any return was computed)

Card `rederive-reclaim-close-stop` (queue row 2, PLAN_24H_2026-11-15 section 8). The 2026-11 study `reclaim_close_stop_2026-11` ran BTCUSDT only, DEV 2022-01..2024-06: INCONCLUSIVE
(4h n 114, net +0.271 %, CI -0.253..0.805; 1D n 13). This study keeps that rule EXACTLY (code reused by path: reclaim.events, which reuses tf_break_event_study confirmed_pivots; no line changed)
and asks one question: does it make money fee-net on other symbols and on 2024+ data it never saw. No parameter is tuned, so the whole 2024+ window is out of sample for the rule.
Claim tested as encoded (enter at the reclaim close, stop = a close back beyond the level), not a discretionary read. Source of the idea: Brando cP6xvs2I02s 03:58-04:02, 08:29-08:35.

## Data
Binance SPOT 4h and 1d klines (public market data, data-api.binance.vision; fetch.py; cache runtime_data/reclaim-10sym-1115/, ignored) for BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (same 10
majors as the sibling 10-symbol studies, chosen by listing age and liquidity before any return: survivorship-biased toward survivors, stated). Bars from 2021-12-01 (indicator warm-up and swing history),
trades only with the reclaim-bar close in [2024-01-01, 2026-11-15). Note: spot not USD-M perpetual (the BTC study used perp klines); prices differ by basis only. Regime context from BTCUSDT 1d/1w/1M spot for every symbol (market regime, OURS).
Cost = research_kit.TAKER_RT_PCT 0.14 % round trip (no cost constant is defined here; the BTC study used 0.10 %, so its +0.27 % becomes about +0.23 % at this cost).

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| Level | fractal swing, L=3 bars each side (4h and 1D), confirmed at close of bar k+L, latest live swing per side | OURS (from tf_break_event_study, as the BTC study) |
| Break | first bar piercing the level consumes it; close beyond level by 0.1 x ATR14 (SMA) is a break, else wick sweep, no trade | OURS (as BTC study) |
| Reclaim window N | 6 bars on 4h, 3 on 1D | OURS |
| Entry | close of the first reclaim bar; low break -> LONG, high break -> SHORT, sides pooled | OURS |
| Exit / stop | first close strictly beyond the level in the next cap bars, else close of bar j+cap; cap 6 (4h), 5 (1D); fills at bar close, no slippage | OURS |
| Cost | 0.14 % round trip | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost, % of entry; mean with SE clustered by UTC day of the fill across ALL symbols (research_kit.cluster_mean_se, normal p via norm_p_two) | SOURCED research_kit |
| Confirmatory family | pooled 10 symbols x {4h, 1D}, sides pooled = 2 arms; Holm over m = 2 (research_kit.holm) | OURS |
| EDGE (an arm) | n >= 100, net mean > 0, Holm-adjusted p < 0.05, AND net mean > 0 in both sub-windows 2024-01..2025-06 and 2025-07..2026-11 | OURS |
| Verdict | EDGE = at least one arm qualifies; otherwise NO EDGE. Because the power gate BLOCKs (POWER_GATE.md, BLOCKED.md) the strongest wording is "NO EDGE, underpowered for a 0.30 % plausible gross, INCONCLUSIVE ceiling", never an unqualified FAIL | OURS |
| Descriptive only | per-side, per-regime (bull/bear/range of BTC via research_kit.regime_tag), per-sub-window, per-symbol rows | never verdict arms |
| Windows | OOS 2024-01-01..2026-11-14 for every symbol. This reads the project VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) windows for this rule family: log it in research/holdout_reads.csv; holdout BURNED for the reclaim-close-stop family | operator card |
Forward outcome windows are the `fwd` slices inside reclaim.forward_reclaim (look-ahead by construction of the event definition, entered only at the reclaim bar's own close).

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; POWER_GATE.md)
n = distinct days with an event (4h 639 of 1345 events, 1D 135 of 200; counts.csv, no returns), sd 2.45 % (4h, SOURCED from the BTC tf_break RESULT) and 4.0 % (1D, OURS assumed), cost 0.14, m 2: both arms BLOCK
(4h MDE 0.299 + 0.14 = 0.439 vs 0.30; 1D 1.201). Ten symbols multiply events but same-day coin events are correlated, so the day-cluster caps the effective n. Run anyway as descriptive; ceiling stated above.

## What the result will say
RESULT.md first lines: `Regime mix:` then the verdict. Then the family table (n, days, gross, net, SE, t, p, Holm p, sub-window nets) and the descriptive cuts, and the comparison to the BTC-only numbers.

## Context
Regime: not an entry gate; the BTC market regime (research_kit.regime_tag: Malkan weekly/monthly RSI 60/40 band SOURCED + daily SMA200 side) is reported per event as a descriptive cut.
Phase: the entry itself is the phase (break of a fractal swing then reclaim of it = failed-break / retest of the level, 4h and 1D).
Session: none (4h and 1D bars; no intraday session split).
Entry: reclaim-bar close (market at close), stop = first close back beyond the level.
Regime mix: reported in RESULT.md as weeks by regime over 2024-01-01..2026-11-14 (research_kit.regime_mix_line).
