# PRE_REG: WaveTrend c30 retest re-derived on 10 symbols, out of sample 2024+ (frozen 2026-11-15, before any return was computed)

Card `rederive-wt-c30-retest` (queue row 2, PLAN_24H_2026-11-15 section 8; Gemini blind card rederive-wt-c30-retest-gemini3-1114 is the audit twin). The 2026-11-04 study
`wavetrend_c30_retest_2026-11-04` ran BTCUSDT only, DEV 2022-01..2024-06: INCONCLUSIVE (power-blocked), 0 survivors of 24 pooled + 96 session cells; the only positive-CI cell
(1h sell + divergence, with-trend, retest, n 19 / 17 days) was a lead. This study keeps that rule EXACTLY (every rule function is imported by path from that study.py, no line
changed: dots, RSI and divergence confluence, retest entry, trend gate, 12-bar exit, drift control, cell statistics) and asks one question: does it make money fee-net on other
symbols and on 2024+ data it never saw. No parameter is tuned, so the whole 2024+ window is out of sample for the rule. Claim tested as encoded, not the trader's discretionary read.
Code `study.py`, tests `test_10sym.py` (4 tests; two mutations, the OOS window filter and the complete-bucket resampler rule, made 2 of 4 fail). Only event COUNTS were read
before this freeze (counts.csv, regime_mix.txt).

## Data
Binance SPOT 15m klines (public market data, data-api.binance.vision; cache runtime_data/wt-c30-10sym-1115/, ignored) for BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (same 10 as the
bb-range-retest re-derivation: the 10 most established majors, listed before 2022, chosen before any return by listing age and liquidity; survivorship-biased toward survivors, stated).
30m and 1h bars are built from the 15m bars (aligned buckets, complete buckets only). Bars from 2023-10-01 (WaveTrend uses a bar only after 200 bars), dots with close in
[2024-01-01, 2026-11-15). Daily bars per symbol from 2022-01 for the SMA200 gate. Cost = research_kit.TAKER_RT_PCT 0.14 % round trip (shared cost model, not redefined).

## Parameters (every one labelled; rule identical to 11-04 PRE_REG.md)
| Parameter | Value | Label |
|---|---|---|
| WaveTrend | hlc3; esa EMA10; d EMA10(abs(ap-esa)); ci=(ap-esa)/(0.015 d); wt1 EMA21(ci); wt2 SMA4(wt1); wt_parity_ref.py, first 200 bars unused | SOURCED LazyBear, wavetrend_2026-10-17/PARITY_CONTRACT.md |
| Dot | wt1 crosses wt2 on a closed bar; buy needs wt1 <= -53, sell wt1 >= +53 | band 53 SOURCED (Pine); dot-only-in-band OURS |
| Timeframes | 15m, 30m, 1h | OURS (as 11-04) |
| RSI confluence "rsi" | RSI(14, Wilder) on the same TF: buy <= 40, sell >= 60 at the dot bar close | RSI 14 SOURCED; 40/60 level OURS |
| Divergence confluence "div" | close-based regular divergence 3..12 bars, stamped within 3 bars up to the dot bar | closes-only and 3..12 window SOURCED (Malkan relay d-malkan-divergence-window-1104); 3-bar proximity OURS |
| Entry | "signal" = dot bar close; "retest" = first pullback to the dot-bar midpoint within 6 bars, no touch no trade | OURS |
| Horizon | exit at the close 12 bars after the entry bar | OURS |
| Trend gate "with" | the symbol's OWN daily SMA200 side of the last closed daily bar agrees with the trade (buy above, sell below); "against" = control | SOURCED-in-repo research_kit.regime_tag; per-symbol application OURS |
| Regime rows | research_kit.regime_tag: Malkan weekly/monthly RSI 60/40 band of BTC (market regime for every symbol) + the symbol's daily SMA200 side; descriptive | band SOURCED Malkan, BTC-for-all OURS |
| Cost | 0.14 % round trip taker both legs | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost; SE clustered by UTC day of the entry bar ACROSS ALL symbols (same-day coin signals are correlated); 95 % CI = mean +- 1.96 SE | SOURCED research_kit |
| Drift control | excess = mean gross - mean same-side gross of every bar close of the 10 symbols in the same TF, window and gate (cluster_diff) | OURS |
| Confirmatory family | pooled 10 symbols, gate "with", conf rsi/div: 3 TF x 2 sides x 2 conf x 2 entries = 24 cells, Holm m = 24 (research_kit.holm) | OURS |
| Survivor (EDGE) | n >= 30, >= 20 days, net mean > 0, Holm p < 0.05, excess over drift t >= 2, AND net > 0 in both sub-windows 2024-01..2025-06 and 2025-07..2026-11 | thresholds OURS (sub-window rule as the bb-range-retest re-derivation) |
| Descriptive only | conf none, gates all / against / regime rows, per-symbol rows of the confirmatory arm, sub-window nets | never survivors |
| Verdict | EDGE = at least one survivor. Otherwise NO EDGE; because the power gate BLOCKs most cells (POWER_GATE.md), wording is "NO EDGE, underpowered for a 0.30 % plausible gross; INCONCLUSIVE ceiling by the gate", never an unqualified FAIL | OURS |
| Windows | OOS 2024-01-01..2026-11-14 for every symbol. This reads the project VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) windows for this rule family: logged in research/holdout_reads.csv, holdout BURNED for the wavetrend-c30 family | operator card |

## Power gate (scripts/dev/prereg_gate.py, before any return; POWER_GATE.md / BLOCKED.md)
n = distinct event-days of the pooled with-trend rsi/div cell (signal entry), sd OURS 0.9 / 1.3 / 1.9 % (as 11-04), m 24, cost 0.14: only the best 15m cell (586 days) passes
(MDE + cost 0.286 vs 0.30); every other probed cell BLOCKs (15m div sell 0.313; 30m 0.384-0.443; 1h 0.57-0.77; n needed 486 / 1013 / 2165 days). Ten symbols multiply trades
but the day cluster (same-day coin signals correlated) caps effective n. Run anyway as an honest descriptive re-derivation; verdict ceiling as stated above.
Regime mix (BTC, 2024-01..2026-11): the strict Malkan band gives no bear week, so reg_bear rows are empty.

## What the result will say
1. RESULT.md first lines: `Regime mix:` then the verdict. 2. The 24-cell family: n, days, gross, net, CI, excess t, Holm p, sub-window nets. 3. Per-symbol table of the
11-04 lead (1h sell + div, with-trend) and the best cells, and the comparison to the 11-04 BTC-only numbers.

## Context
Regime: daily SMA200 side of the symbol must agree with the trade (buy above / sell below), plus descriptive rows by research_kit.regime_tag (Malkan 60/40 band of BTC); against-trend rows are the control.
Phase: the retest entry (dot, then pullback to the dot-bar midpoint) is the phase device (OURS); no per-dot tf_break class exists.
Session: not split here (11-04 sessions were descriptive and empty of survivors); pooled over the day.
Entry: signal-bar close vs retest of the dot-bar midpoint within 6 bars, both run.
Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)
