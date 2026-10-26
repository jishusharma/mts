# Fable: the minimum stop width that survives fees (2026-10-26)

One-page rule from the 2026-10-25 Fable review: a tight stop makes a 0.07 % round-trip
fee about a third of the risk, so the whole trade is net-negative. This card turns that
into a rule and a table, with every number labelled SOURCED or OURS.

## The rule

A layer idea needs a stop width of at least **4x its round-trip fee cost** before its
gross edge can survive fees: 4x is exactly where the fee share of one stopped-out risk
unit (R) reaches the **0.25 R cap** (SOURCED, VISION economics, `PRE_REG_CRYPTOCRED_HTF.md`
gate 6: "fee share of R < 0.25 R"). Below that floor, fees take more than a quarter of
every R at risk and the idea usually flips to net-negative.

Worked (OURS): a 0.07 % mixed round trip is 0.35 R of a 0.20 % stop (0.07/0.20 = 0.35) —
a third or more of the risk, the exact failure the review flags ("a 0.07 % round-trip fee
becomes a third of the risk", `REVIEW_FABLE_2026-10-25.md` s.1). At the 0.40 % taker floor
the same fee is only 0.25 R and fees stop being the whole result.

## Fee inputs (label per number)

| Fee | Value | Label | Source |
|---|---|---|---|
| Taker fee, one side | 0.0005 (0.05 %) | SOURCED | `backtest/fees.py` BINANCE_TAKER = DERIBIT_TAKER = 0.0005, via `FORMULAS.md` s.17 |
| Maker fee, one side | 0.0002 (0.02 %) | SOURCED | `backtest/fees.py` BINANCE_MAKER = 0.0002, via `FORMULAS.md` s.18.5 |
| Deribit maker fee, one side | 0.0 | SOURCED | `backtest/fees.py` DERIBIT_MAKER = 0.0 |
| All-taker round trip | 0.10 % | SOURCED | `FORMULAS.md` s.17: cost = 2 * 0.0005 (0.10 %) |
| Deribit maker-in / taker-out round trip | 0.05 % | SOURCED | 0.0 + 0.0005; stated as "5 bps for maker_entry [SOURCED fees.py:23-24]" in `PRE_REG_CRYPTOCRED_HTF.md` gate 6 |
| Binance mixed (maker-in / taker-out) round trip | 0.07 % | OURS (arithmetic on the two SOURCED one-side fees) | 0.0002 + 0.0005; the fill mix the levels study actually prices (`_bars.py`: entry limit = maker, stop fill = taker). Stated as "0.07 % round-trip fee" in `REVIEW_FABLE_2026-10-25.md` s.1 |

The stop floors the rule compares against: **0.40 % (taker legs) and 0.20 % (maker entry)**.
SOURCED from `PRE_REG_CRYPTOCRED_HTF.md` gate 0a: "on BTC fees stay under 0.25 R only with
a stop of at least 0.40 % (taker legs) or 0.20 % (maker entry)." NOT attributed to Tom;
no Tom file carries these. (`T080_MAKER_MODEL_2026-10-09.md` analyses stop-width buckets
<0.10 / 0.10-0.20 / 0.20-0.40 / >=0.40 % but does not state the floors.)

## Table: fee share of risk (R) by stop width, per fill mix

Fee share of risk = round-trip fee (%) / stop width (%). Every cell is recomputable by hand
from the fee inputs above, no study code needed. The three CryptoCred median stop widths
(SOURCED, `PRE_REG_CRYPTOCRED_HTF.md` gate 6, tagged OURS-UNREPRODUCED at source) are
included; the all-taker and Deribit-maker-in columns reproduce that study's `cost_r`
exactly (0.068/0.061/0.023 R and 0.034/0.030/0.011 R), so the table is checked against a
second source, not just self-consistent.

| Stop width | All-taker (RT 0.10 %) | Binance mixed, maker-in/taker-out (RT 0.07 %) | Deribit maker-in/taker-out (RT 0.05 %) |
|---|---|---|---|
| 0.10 % | 1.00 R | 0.70 R | 0.50 R |
| 0.20 %  (maker floor) | 0.50 R | 0.35 R | 0.25 R |
| 0.40 %  (taker floor) | **0.25 R** | 0.175 R | 0.125 R |
| 0.80 % | 0.125 R | 0.0875 R | 0.0625 R |
| 1.461 % (CC setup 1) | 0.068 R | 0.048 R | 0.034 R |
| 1.647 % (CC setup 2) | 0.061 R | 0.0425 R | 0.030 R |
| 4.419 % (CC setup 3) | 0.023 R | 0.0158 R | 0.011 R |

Bold row = the taker floor: 0.40 % is exactly where all-taker fee share reaches the 0.25 R
cap. The Deribit maker-in column reaches the same cap at 0.20 %, the source's maker floor.

## Minimum stop width per fill mix (fee share <= 0.25 R)

Min width = 4 x RT fee (OURS, arithmetic on the SOURCED cap).

| Fill mix | RT fee | Min width (OURS) | Source floor |
|---|---|---|---|
| All-taker | 0.10 % | 0.40 % | 0.40 % (SOURCED, gate 0a) |
| Binance mixed | 0.07 % | 0.28 % | 0.20 % maker entry (SOURCED, gate 0a — the stricter floor) |
| Deribit maker-in | 0.05 % | 0.20 % | 0.20 % (SOURCED, gate 0a) |

The all-taker and Deribit-maker-in columns reproduce the source's two floors exactly. The
mixed 0.28 % sits between them; a mixed-fill study should hold its stops to the stricter
0.20 % maker-entry floor, not its own 0.28 % arithmetic.

## Which sim-desk study should show this

The **levels** study (`sim_desk/studies/levels.py`) is the one to surface the rule and
table. It is the study where fees are the whole result: the review s.1 records +0.22 R
gross, -0.34 R fees, -0.12 R net, and the 0.07 % round trip as a third of the risk. The
levels fee-share strip (review s.3 card 2, "before fees +0.22 R, fees -0.34 R, after fees
-0.12 R") is the place to add this rule next to it, with the stop-width table above as the
hand check a reader can redo from the fee inputs without touching the study code. RSI and
WaveTrend do not gate on stop width the way levels does, so the rule belongs on the
levels page, not the others.
