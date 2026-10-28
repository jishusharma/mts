# RESULT: EUR-LOW-US-SWEEP follow-ups, three legs, DEV only (BTCUSDT 1m, bars before 2024-07-01)

**Verdict: all three legs BLOCKED by the power gate. No outcome was read.** PRE_REG.md (commit 32090415) precedes this file. Costs: taker 0.05 %/side, funding not modelled, no slippage.
Parent: `eur_low_us_sweep_2026-10-14/RESULT.md` (short leg EXPLORATORY NEGATIVE; long-after-reclaim, LTF RSI-divergence short and pre-US double-top short were open). They stay open: BLOCKED is not FAIL.

## Verdict arms
| arm | n | mean G | SE | verdict |
|---|---|---|---|---|
| A long after sweep+reclaim (BLOCKED, power gate) | 133 | none | none | BLOCKED |
| B RSI(14) divergence short from the day high (BLOCKED, power gate) | 208 | none | none | BLOCKED |
| C pre-US double-top short (BLOCKED, power gate) | 100 | none | none | BLOCKED |

FAIL means stop: none; BLOCKED legs are not killed (no outcome was read).

## Per leg and split (DEV only; n = tradeable days)
| leg | gate | DEV n / mean net / t | VAL | HOLDOUT |
|---|---|---|---|---|
| A (EU 24 h low, reclaim <= 120 min, stop at sweep low) | MDE 0.280 + cost 0.190 = 0.470 R > 0.30 R; needs 864 days | 133 / not run | sealed, not read | sealed, not read |
| B (5m, first signal per day) | MDE 0.224 + cost 0.247 = 0.471 R > 0.30 R; needs 3723 days | 208 / not run | sealed, not read | sealed, not read |
| C | MDE 0.323 + cost 0.188 = 0.511 R > 0.30 R; needs 834 days | 100 / not run | sealed, not read | sealed, not read |

Gate inputs: sd 1.0 R (favourable; precedent 1.5 R), m 3, cost = 0.10 % / median stop distance (0.528 %, 0.405 %, 0.531 %). Counts and skip reasons: `COUNT.md`. Entry/stop geometry is known at decision time, so counting it reads no outcome.

## What this says
- Leg A (the one the parent flagged as the real question: ~93-95 % of breaks reclaim within 120 min): only 133 tradeable days exist on DEV. With a 0.10 % round-trip fee and a ~0.5 % stop, a gross edge below ~0.28 R (about 0.15 % per trade) is not detectable at 80 % power, and the fee already uses 0.19 R of the 0.30 R plausible-gross cap. The stability test (same sign DEV/VAL/HOLDOUT, leave-one-year-out) was therefore not run; there was nothing powered to test.
- Leg A vs the closed weekly-low/round-1000 screen (`opr_weekly_low_round_sweep_2026-10-16`, FAIL): different event (EU 24 h low, day-level T0, 120-minute reclaim, sweep-low stop). `verdicts.py check` blocks the family on a kill_scope it could not parse; this study does not re-run that screen's definition.
- Leg B has the most days (208) but the tightest stops (median 0.405 %), so cost is 0.247 R and it would need 3723 days. Leg C has only 100 double-tops in 912 days.
- Nothing was tuned, no variant was run: `trials.csv` lists the three arms as BLOCKED.

## Defaults taken (no operator questions)
DEV = before 2024-07-01 (repo convention) instead of the parent's 2022-24/2025/2026 split, so the parent's 2026 holdout stays unread for these legs; sd 1.0 R for the gate; Holm m = 3; 0.15 % minimum risk; "day high" = running UTC-day high.

## Verdict
BLOCKED (A, B, C): untestable at this sample and fee. Unblock options are in `BLOCKED.md`; none is taken here.
