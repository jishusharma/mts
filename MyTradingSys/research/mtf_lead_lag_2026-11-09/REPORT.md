# Timeframe flip lead-lag, BTC 2019-2026 (mtf-timeframe-lead-lag-research)

**You can see the daily flip coming, but you can't trade it alone. The best early-flip rule (R3: 4h and 1h both flip to RSI 60+ or 40-, with the daily RSI already on that side of 50) is followed by a same-direction daily flip within 7 days 41 % of the time out of sample, against a 23 % base rate. It anticipates the flip. But trading it gives only +0.17 % per trade at 3 days after fees, against -0.10 % unconditional, about 1.2 standard errors. That fails the pre-registered kill line, so use it as context, not as a trigger.**

Pre-registration: `PRE_REG.md` (committed 719a0b214 before any run). Code: `lead_lag.py`, tests `test_lead_lag.py` (3, causality). Results: `RESULT_dev.json` (2019-11-08 .. 2023-12-31), `RESULT_val.json` (2024-01-01 .. 2026-11-07, opened once after the DEV commit 5f27287b6; no rule changed). Data: Binance spot BTCUSDT 15m/1h/4h/1d/1w, data-api.binance.vision, closed bars.

## Context

- Regime: DEV and VALIDATION pooled across regimes (no regime split was run; listed as a gap below).
- Phase: none. Session: none (flips are dated at bar close, UTC).
- Entry (forward-return check only): close of the bar that confirms the rule; 0.10 % round trip (fees.FEES_ALL_TAKER).

## How early does each timeframe flip? (RSI 60/40 state flips; WT = WaveTrend cross)

| Higher flip <- lower TF | DEV n | DEV median lead (IQR) | VAL n | VAL median lead (IQR) | Read |
|---|---|---|---|---|---|
| RSI 1d <- 4h | 122 | 16 h (4-36) | 78 | 12 h (8-32) | the useful lead: a 4h flip comes about half a day before the daily one |
| RSI 1d <- 1h | 122 | 7 h | 78 | 8 h | always present (1h flips are frequent), so it says little |
| WT 1d <- 4h | 227 | 32 h (20-48) | 142 | 36 h (20-52) | WaveTrend gives about 1.5 days of warning |
| RSI 1w <- 1d | 14 | 144 h, only 64 % had a lead | 11 | 96 h, 45 % | too few weekly flips to rely on |
| WT 1w <- 1d | 30 | 72 h, 47 % | 19 | 96 h, 42 % | about half of weekly flips come with no daily warning in the prior 7 days |

15m and 1h "lead" every higher flip because they flip many times a week. Their lead time is close to the time since the last noise flip, not a signal. The 4h is the lowest timeframe whose flip carries information about the daily one.

## Early-flip rules (frozen in PRE_REG)

| Rule | DEV events | DEV hit | VAL events | VAL hit | VAL base | VAL fee-net 3d (SE) | baseline 3d |
|---|---|---|---|---|---|---|---|
| R1 4h flips | 548 | 36.9 % | 395 | 38.7 % | 22.7 % | -0.00 % (0.21) | -0.10 % |
| R2 4h + 1h in the same new state | 887 | 33.6 % | 600 | 35.0 % | 22.7 % | +0.07 % (0.17) | -0.10 % |
| R3 R2 + daily RSI on that side of 50 | 655 | 39.4 % | 442 | **41.0 %** | 22.7 % | +0.17 % (0.21) | -0.10 % |

Kill line: VAL hit >= base + 10 points (R1, R2 and R3 all pass) AND 3d fee-net beats the baseline by more than 2 SE (none pass; R3 is about 1.2 SE). Verdict: **no usable early-flip trigger from RSI/WT states alone; R3 is a valid anticipation filter.**

DEV looked better than VAL for the trade (R3 +0.43 % at 3d, +0.82 % at 7d), and that edge roughly halved out of sample. That's normal decay; it is why the DEV number was never the decision.

## Use for the operator's ask ("identify the flip early, then anticipate it")

- Watch the 4h: when 4h and 1h RSI both reach 60+ (or 40-) and the daily RSI is already above (below) 50, a daily flip in that direction follows within a week 4 times in 10, nearly twice the base rate. The typical warning is 12-16 h on RSI, about 36 h on WaveTrend.
- Use it to stand aside from fades against the coming daily flip, or to size with it. Don't use it as an entry by itself.

## Not done

Regime split (bull/bear by 200-day SMA), other symbols, and combining R3 with a level or structure trigger (the Malkan level stack or the auction census): that combination is the natural follow-up and would need its own pre-registration.
