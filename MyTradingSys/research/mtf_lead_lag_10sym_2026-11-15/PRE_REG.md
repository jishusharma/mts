# PRE_REG: mtf_lead_lag early-flip rules R1-R3 re-derived on 10 symbols, out of sample 2024+ (frozen 2026-11-15, before any return or hit rate was computed)

Card `rederive-mtf-lead-lag` (queue row 2, PLAN_24H_2026-11-15 section 8). Parent: `mtf_lead_lag_2026-11-09` (BTC only; R3 hit 41 % vs 23 % base, fee-net 3d +0.17 % at 1.2 SE: lead yes, trigger no).
This study keeps the three rules EXACTLY (code reused by path: lead_lag.py rsi_flips / rule_events, no line changed) and asks one question: does an early-flip rule make money fee-net on 10 symbols and on 2024+ data. Only event counts (counts.csv) were looked at before freezing.

## Context
Regime: not an entry gate; BTC market regime (research_kit.regime_tag, Malkan weekly/monthly RSI 60/40 band SOURCED plus daily SMA200 side) is a descriptive cut per event.
Phase: the rule is a multi-timeframe momentum transition (4h and 1h RSI both flip to 60+/40-, R3 with daily RSI already on that side of 50); no phase filter.
Session: none (flips dated at bar close UTC).
Entry: close of the bar that confirms the rule, held 3 days (primary), 1 and 7 days descriptive; direction = the flip direction; no stop.
Regime mix: reported in RESULT.md first line as weeks by regime over 2024-01-01..2026-11-14 (research_kit.regime_mix_line).

## Data
Binance SPOT 1h, 4h, 1d (BTC also 1w, 1M for the regime tag) klines, public market data (data-api.binance.vision; fetch.py; ignored cache runtime_data/mtf-10sym-1115/). Universe BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (same 10 majors as the sibling studies, fixed before any return; survivorship-biased, stated). Bars from 2021-12-01 (indicator warm-up); events only with the confirming close in [2024-01-01, 2026-11-08) so every event has a full 7-day look-forward. 15m is dropped (parent: 15m flips are noise). The whole window is out of sample for the frozen rules (no parameter tuned). Reading it covers the project VALIDATION and HOLDOUT windows for this family: logged in research/holdout_reads.csv, holdout BURNED for the mtf-lead-lag family.

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| RSI | Wilder 14, state BULL >= 60, BEAR <= 40 | SOURCED (Malkan lines; period OURS) |
| Flip | close of the bar whose RSI changes state into BULL/BEAR | OURS (parent) |
| R1 / R2 / R3 | 4h flip / 4h and 1h in the same new state / R2 plus last closed 1d RSI on that side of 50; one event per 24 h per direction per symbol | OURS (parent, frozen) |
| Hit | a same-direction 1d RSI flip within 7 days after the event | OURS (parent) |
| Base rate | share of every 4h close (both directions, per symbol, pooled) followed by a same-direction 1d flip within 7 days | OURS (parent idea, recomputed per symbol) |
| Forward return | `fwd_3d` = close 72 h after the entry 1h close, signed by direction; net = gross minus research_kit.TAKER_RT_PCT (0.14 % round trip) | cost SOURCED research_kit; horizon OURS |
| Baseline | the same 3-day forward return from every 4h close, both directions, same symbols and window | OURS |
| Statistics | net mean with SE clustered by UTC day of entry across all symbols (research_kit.cluster_mean_se); also clustered by ISO week; the LARGER SE decides (3-day holds overlap); normal p; Holm over m = 3 rules (research_kit.holm) | SOURCED research_kit; larger-SE rule OURS |
| EDGE (a rule) | n >= 100, net mean > 0, Holm p < 0.05, net > 0 in both sub-windows 2024-01..2025-06 and 2025-07..2026-11, hit rate >= base + 10 points (parent kill line), and net beats the baseline by more than 2 SE (research_kit.cluster_diff) | OURS (parent kill line plus Holm and sub-window rules) |
| Verdict | EDGE = at least one rule qualifies; else NO EDGE. Power gate BLOCKs (POWER_GATE.md, BLOCKED.md), so NO EDGE is worded "underpowered, INCONCLUSIVE ceiling" | OURS |
| Descriptive only | per-side, per-regime, per-sub-window, per-symbol cuts, 1 d and 7 d horizons, 1d<-4h lead tables (leads.csv) | never verdict arms |
Forward windows are the `fwd_*` fields of study.py (look-ahead by construction of the event definition, entered only at the rule's own confirming close).

## Power gate
scripts/dev/prereg_gate.py before any return: BLOCK (POWER_GATE.md). Ten symbols multiply events but same-day events are correlated, so the day and week clusters cap the effective n.

## Limits stated now
Survivor-biased majors; spot not perpetuals; no funding; correlated coins; rules not re-tuned for alts; 3-day holds overlap (week-cluster SE used).
