# Which side is open interest picking? (2026-10-30)

These are descriptive counts only: no fees and no edge claim. Definitions are in the header of `study.py` (all OURS).

Data:
- Binance USD-M BTCUSDT 5m open interest and top-trader ratio, from the public metrics archive `data.binance.vision`. `fetch_metrics.py` puts it in `F:/MTS/data/binance_metrics`, local only.
- Price and taker delta from the 1m archive.
- DEV 2022-2025 only. Events do not overlap. n = 35,963 30-minute windows with OI up or down by at least 0.25%.

The trigger was the operator's shot 072bbb83f7b1 (10-29, 23:05-23:38Z, 1m): OI went from 93.3K to 93.6K while price drifted from 78.9k to 78.79k. CVD and net delta were flat to slightly down.

## Why OI alone cannot pick a side

- Every new contract has one buyer and one seller, so a rise in OI means more longs AND more shorts, in equal number.
- What differs is who was in a hurry (the aggressor, seen in the taker delta) and who absorbed (the passive side, seen when price does not move).

## A. OI x price over the last 30 minutes

| OI | Price | n | Up 60 min later | Up 4 h later | +0.5% first | -0.5% first |
|---|---|---|---|---|---|---|
| up | up | 6,193 | 48.5% | 49.4% | 47.9% | 43.6% |
| up | flat | 8,023 | 51.3% | 51.0% | 41.9% | 39.3% |
| up | down | 4,985 | 52.7% | 52.8% | 43.5% | 48.8% |
| down | up | 5,428 | 48.9% | 49.0% | 45.9% | 43.3% |
| down | flat | 5,038 | 49.7% | 51.0% | 37.5% | 41.3% |
| down | down | 6,296 | 53.5% | 53.4% | 43.3% | 46.7% |

Reading:
- **Direction:** every row sits between 48% and 54%. OI, with or without price, did not tell the next direction.
- **A small lean against the push:** after OI and price rose together, the next hour was up 48.5%; after OI rose and price fell, 52.7%. That is a gap of about 4 points (about 6 standard errors), below fee level as a trade.

## A2. By cycle (operator: "every time frame is different as there are cycles")

Share of windows where the close was up 60 minutes later. n per cell is 842-2,817, so one standard error is about 1.0-1.7 points.

| OI | Price | Story (OURS) | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| down | up | short covering | 44% | 48% | 52% | 55% |
| down | down | long liquidation | 54% | 58% | 53% | 48% |
| up | down | shorts pressing | 52% | 55% | 53% | 50% |
| up | flat | build-up | 52% | 52% | 50% | 52% |
| up | up | longs pressing | 49% | 47% | 49% | 50% |

Reading:
- **The operator is right for the OI-down cells.** Their meaning flips with the cycle:
  - Short-covering rallies faded in the 2022 bear market (44% up) but kept going in 2024-25 (52-55%), an 11-point swing of about 5 standard errors.
  - Long liquidations bounced in 2023 (58%) but not in 2025 (48%).
- **OI-up cells barely change across years.** Build-ups stay about 50/50 in every cycle.
- **A shorter cycle definition (price above or below its 20-day mean) changed little:** at most 3.6 points between the two halves. The year, standing in for the macro bull/bear phase, separates more.
- **Consequence:** an OI read needs the cycle as context. It goes into `bb-state-regime-tf-map` as a regime column.

## B. The operator's case: OI up, price flat, split by the aggressor

| Taker delta in the window | n | Up 60 min | +0.5% first | -0.5% first |
|---|---|---|---|---|
| buyers (share >= +0.05) | 2,035 | 49.4% | 40.9% | 36.1% |
| mixed | 3,765 | 51.6% | 44.5% | 41.2% |
| sellers (share <= -0.05) | 2,223 | 52.6% | 38.3% | 39.0% |

- **Sellers aggressive while price does not fall, with OI rising (the shot):** that is passive buyers absorbing new shorts (Fabio F-CVD3).
- **But the next ±0.5% was a coin flip,** 38% up first vs 39% down first. About 23% reached neither within 4 hours.
- **A build-up like this resolves slowly** and does not choose a side by itself.

## C/D. Top-trader long/short ratio (accounts)

- The ratio moved more than 1% in only about 6% of the build-ups (n=133 and 379).
- Sub-cells hold 39-169 cases. One cell looks strong (sellers with top longs growing: 72% up, n=39), but it is too small to trust and would need a pre-registered confirmation.

## What answers "which side" then (OURS, from the counts)

1. **OI says how much fuel there is, not its direction.**
2. **Delta says who was aggressive. Price says whether they were absorbed.** Aggression without a result means the aggressor is the side at risk.
3. **The side gets picked when a nearby level breaks.** The absorbed side's stops sit beyond it.
   - That is the next measurement: build-up, then break, then the follow-through size. It extends U2 in CARD_SPECS.md.
   - It goes in `cvd-coil-and-absorption-u7-u8`.
