# PRE_REG: bb_range_retest re-derived on 10 symbols, out of sample 2024+ (frozen 2026-11-15, before any return was computed)

Card `rederive-bb-range-retest` (queue row 2, PLAN_24H_2026-11-15 section 8; Gemini blind card rederive-bb-range-retest-gemini3-1114 is the audit twin). The 2026-11-04 study
`bb_range_retest_2026-11-04` ran BTCUSDT only, DEV 2022-01..2024-06: INCONCLUSIVE (power-blocked), all 9 cells net -0.07 to -0.20 % per trade, 0 survivors. This study keeps
that rule EXACTLY (event finder, re-entry close, k-ATR retest limit, static opposite-band target, 2:1 stop, 24-bar time-out, session-range tag, range gate; code reused by
path from bb_range_to_range_2026-11-04/study.py and bb_range_retest_2026-11-04/study.py, no line changed) and asks one question: does it make money fee-net on other symbols and
on 2024+ data it never saw. No parameter is tuned, so the whole 2024+ window is out of sample for the rule. Claim tested as encoded, not the trader's discretionary read.

## Data
Binance SPOT 15m klines (public market data, data-api.binance.vision; fetch.py; cache runtime_data/bb-retest-10sym-1115/, ignored) for BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX
(the 10 most established majors, all listed before 2022; chosen before any return, by listing age and liquidity, so survivorship-biased toward survivors, stated). Bars from 2023-10-01
(warm-up for BB, ATR and the 20-session range history), trades only with signal-bar close in [2024-01-01, 2026-11-15). Regime context from BTCUSDT 1d/1w/1M spot for every
symbol (market regime, OURS). Cost = research_kit.TAKER_RT_PCT 0.14 % round trip (the shared cost model, same as 11-04; no cost constant is defined here).

## Parameters (every one labelled)
| Parameter | Value | Label |
|---|---|---|
| Bands | BB(20, 2) of closes, population std, as-of | OURS (as 11-04) |
| Signal, re-entry M=10, touch N=10, k grid {0.25, 0.5, 1.0} x ATR(14) | exactly as 11-04 PRE_REG Parameters | OURS |
| Exit | static opposite band target, stop 0.5 x distance to target, 24-bar time-out, stop first on a double touch, gap fills at open | OURS |
| Range gate | research_kit regime == "range" of BTC, as-of the signal close | band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo, "range = the rest" OURS; BTC-for-all-symbols OURS |
| Session | research_kit.session_tag (asia / london / ny confirmatory, late descriptive) | cutoffs OURS |
| Session-range tag | per symbol, running session range strictly above the median of the previous 20 same-name sessions (>= 10 needed) | OURS (no analyst quote; not the trader's) |
| Cost | 0.14 % round trip | SOURCED research_kit.TAKER_RT_PCT |
| Statistics | net = gross - cost, % of entry; SE clustered by UTC day of the fill bar across ALL symbols (same-day trades on different coins share one cluster, because coins are correlated) | SOURCED research_kit |
| Confirmatory family | pooled 10 symbols x {asia, london, ny} x k {0.25, 0.5, 1.0}, range gate, tagged, sides pooled = 9 cells; Holm over m = 9 (research_kit.holm) | OURS |
| Survivor (EDGE) | cell with n >= 30, >= 20 days, net mean > 0, Holm p < 0.05, tagged-range minus tagged-all-regime difference t >= 2 (cluster_diff), AND net > 0 in both sub-windows 2024-01..2025-06 and 2025-07..2026-11 | OURS (the sub-window rule is new here) |
| Verdict | EDGE = at least one survivor. Otherwise NO EDGE; because the power gate BLOCKs (POWER_GATE.md), the strongest wording is "NO EDGE, underpowered for a 0.30 % plausible gross; INCONCLUSIVE ceiling by the gate", never an unqualified FAIL | OURS |
| Descriptive only | per-symbol table (range, tagged, all sessions), late session, untagged and any-tag arms, all-regime arms, per sub-window nets, per-side | never survivors |
| Fill-rate check | arm INVALID if fills / signals >= 95 % (as 11-04) | OURS |
| Windows | OOS 2024-01-01..2026-11-14 for every symbol. This reads the project VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) windows for this rule family: logged in research/holdout_reads.csv, holdout BURNED for the bb-range-retest family (card order: OOS 2024+) | operator card |

## Power gate (scripts/dev/prereg_gate.py, run BEFORE any return; output in POWER_GATE.md)
n = distinct days with a range-gated tagged fill (days 391-433 per cell), sd = 1.5 x median stop % (geometry only), m auto + 9 = 257, cost 0.14: all 9 cells BLOCK (MDE + cost
0.43-0.59 vs 0.30 plausible; n needed 1468-3069 days). Ten symbols multiply trades but the day-cluster (same-day coin signals are correlated) caps the effective n. Run anyway as
an honest descriptive re-derivation; the verdict ceiling is stated above.

## What the result will say
1. RESULT.md first lines: `Regime mix:` then the verdict. 2. Family table (9 cells): n, days, fill rate, gross, net, CI, target hit, Holm p, vs_ungated t, sub-window nets.
3. Per-symbol table; comparison to the BTC-only 11-04 numbers.

## Context
Regime: range only, via research_kit.regime_tag on BTC (Malkan weekly/monthly RSI 60/40 band + daily SMA200 side); compared against the all-regime arm.
Phase: the entry itself is the phase (excursion beyond the band, re-entry close, retest of the band); "range" is proxied by the regime tag (OURS).
Session: asia / london / ny (confirmatory) and late (descriptive) via research_kit.session_tag of the signal-bar close, plus the OURS session-range tag.
Entry: retest-level arm only (re-entry close inside the band, then touch of level +- k ATR within N bars; research_kit.retest_entry).
Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)
