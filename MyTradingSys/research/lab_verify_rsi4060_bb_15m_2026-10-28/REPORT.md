# LAB-VERIFY: RSI 40-60 + Bollinger-band bounce, BTCUSDT 15m, fee-net

**Provenance: this is a Sonnet/Claude (Anthropic) independent read, produced by the Supervisor standing
in for the closed DeepSeek (DSA) bridge. It is NOT a second-vendor DeepSeek cross-check** -- no DeepSeek
output was consulted or reproduced here; all numbers below were computed from scratch from real Binance
klines by this script (`study.py` / `fetch.py` in this folder).

Card: `lab-verify-rsi-40-60-bb-bounce-15m`. Desk row: `20261026-204750-lab-verify-rsi-40-60-bb-bounce-15m`.

## Gap check against the prior duplicate row

Prior desk row `20261026-181737-lab-verify-rsi-40-60-plus-bollinger-boun` (no "fee-net" in its title) was
closed (git commit `9154e206d`) as a **duplicate of this row, with no numbers delivered** -- it did not
compute an event table, DEV/VALIDATION split, or fee-net result. No research folder, REPORT.md,
RESULT.md, candidate manifest, or code for this rule existed anywhere in the repo before this pass
(checked MyTradingSys/research/**, git log --all --grep rsi-40-60). So there is no gap to fill --
the full task (fetch data, compute RSI/BB independently, build the event table, fee-net it, split
DEV/VALIDATION, verdict) is done here from zero.

## Parameters (every one labeled)

| param | value | label |
|---|---|---|
| RSI length | 14, Wilder smoothing | SOURCED (card note: "RSI(14)") |
| Bollinger | 20-period SMA, +/-2 SD on close | SOURCED (card note: "BB 20/2") |
| Trend filter | close > SMA200 (15m) for long, close < SMA200 for short | OURS (card note: "close above SMA200 on 15m or 1h"; 15m chosen, not re-tuned) |
| "broke 40" / "broke 60" | RSI below 40 (above 60) for 1-3 consecutive bars | OURS, exact card note wording |
| "tags band" | bar low <= lower band (high >= upper band) at any bar during the break run | OURS, exact card note wording |
| Entry | open of the bar after RSI recovers back across 40/60 | OURS (card note: "exits at 4/8/16 bars" implies entry at recovery+1) |
| Fee | 0.2% round trip | OURS, as given verbatim in this card's done_when |
| Horizons | 4, 8, 16 bars forward | SOURCED, as given verbatim in this card's done_when |
| Mirror/short side | downtrend + RSI pop over 60 + upper-band tag (symmetric construction) | OURS interpretation of the card note's "mirror at RSI 60 and the upper band" -- the note does not fully spell out the short side's trend condition, so I mirrored the long side's logic exactly |

**Trial count: 1.** This single frozen specification (above) was run once on DEV and once on VALIDATION.
No parameter search, grid, or re-tuning happened in this pass -- the rule was already pinned by the card's
note field (SOURCED+OURS) before any bar was read, so running it once satisfies "respect DEV/VALIDATION,
no HOLDOUT peeking": DEV decided the verdict, VALIDATION (below) is a single confirmation touch, not used
to pick or adjust anything.

## Data

Binance spot BTCUSDT 15m klines, data-api.binance.vision (public market data, pre-approved). Fetched
2026-10-28: 39,000 bars, 2025-09-17T01:00Z through 2026-10-28T06:45Z (~406 days -- the practical pull depth
in the time available for this pass, not an API hard limit). RSI14 and BB20/2 computed independently in
study.py (no vendor library). **DEV = first 70% chronologically (27,300 bars, 2025-09-17 .. 2026-06-28);
VALIDATION = last 30% (11,700 bars, 2026-06-28 .. 2026-10-28)**, split fixed before any event was computed.

## DEV event table (decides the verdict)

**LONG (RSI support at 40 + lower-band tag, uptrend):** 163 events, all with a full forward window.

| h (bars) | n | gross mean % | gross t-stat | fee-net mean % (0.2% RT) | fee-net t-stat | unconditional baseline mean % |
|---|---|---|---|---|---|---|
| 4 | 163 | 0.0012 | 0.03 | -0.1988 | -5.49 | -0.0084 |
| 8 | 163 | 0.0228 | 0.50 | -0.1772 | -3.93 | -0.0169 |
| 16 | 163 | 0.0274 | 0.40 | -0.1726 | -2.53 | -0.0340 |

**SHORT (mirror, RSI resistance at 60 + upper-band tag, downtrend):** 151 events, all with a full forward window.

| h (bars) | n | gross mean % | gross t-stat | fee-net mean % (0.2% RT) | fee-net t-stat | unconditional baseline mean % |
|---|---|---|---|---|---|---|
| 4 | 151 | -0.0207 | -0.51 | -0.2207 | -5.50 | 0.0084 |
| 8 | 151 | -0.1033 | -1.71 | -0.3033 | -5.03 | 0.0169 |
| 16 | 151 | -0.1855 | -2.06 | -0.3855 | -4.29 | 0.0340 |

Gross mean returns are all within noise of zero (|t| < 1 except short@16), essentially indistinguishable
from the unconditional baseline (baseline is also ~0, as expected for a near-martingale 15m series). The
0.2% round-trip fee alone (not even the spread) swamps every gross mean, so fee-net is negative at every
horizon on both sides, with large, consistent t-stats (-2.5 to -5.5) -- the losses are statistically real,
not sampling noise.

## VALIDATION confirmation (touched once, after the DEV verdict)

**LONG:** 60 events. **SHORT:** 60 events.

| side | h | n | gross mean % | gross t | fee-net mean % | fee-net t | baseline mean % |
|---|---|---|---|---|---|---|---|
| long | 4 | 60 | -0.0390 | -0.68 | -0.2390 | -4.18 | 0.0108 |
| long | 8 | 60 | -0.1358 | -2.04 | -0.3358 | -5.04 | 0.0216 |
| long | 16 | 60 | -0.2195 | -2.68 | -0.4195 | -5.13 | 0.0432 |
| short | 4 | 60 | -0.0258 | -0.47 | -0.2258 | -4.11 | -0.0108 |
| short | 8 | 60 | 0.0242 | 0.38 | -0.1758 | -2.78 | -0.0216 |
| short | 16 | 60 | -0.0106 | -0.16 | -0.2106 | -3.25 | -0.0432 |

VALIDATION confirms DEV: gross edge is at best noise-level (long side is actually negative on VALIDATION,
getting worse with horizon), and fee-net is negative everywhere with the same large, significant t-stats.
Nothing here reverses the DEV call.

## Verdict

**NOT WORTH A LAYER.** The rule has no detectable gross edge over the unconditional 15m baseline on DEV
(confirmed on VALIDATION), and the stated 0.2% round-trip fee alone turns every cell fee-net negative with
statistically significant t-stats (fee-net is a reliable loser here, not an inconclusive small-sample
result). The divergence arm (RSI higher-low vs price lower-low) from the card's step 4 was not run in this
pass -- DECISION (OURS): out of scope for this gap-fill given the turn budget, since the primary rule
already fails cleanly on both DEV and VALIDATION and the done_when does not require the divergence arm.
If the operator wants the divergence variant checked, it needs its own card/trial.

## Caveats

- t-stats above use the raw (non-day-clustered) sample SD of each event's own forward return; adjacent
  events are not perfectly independent (the lookback window can overlap), so true SEs are somewhat larger
  than shown -- but the effect is already indistinguishable from zero gross, so clustering would not flip
  the verdict.
- No slippage/spread beyond the stated 0.2% fee was modeled.
- Entry/exit use open/close of 15m bars, not intrabar fills.
