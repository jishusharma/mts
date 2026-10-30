# Oversold 5m cascade: does a bounce come, and do momentum-shift signals call it? (2026-10-30)

Descriptive counts only: no fees, no edge claim. Definitions in the header of `study.py` (all OURS). Data: Binance USD-M BTCUSDT 1m archive rolled to 5m, OI from the metrics archive, DEV 2022-2025. 2026 untouched.

Trigger: operator shot 97857881eb00 (10-30 00:15Z). Cascade 80.4k to 77.63k, 5m closes under the lower BB, RSI 19, OI rising while CVD falls. The trigger state fired live at 23:50Z (close 78,115 < band 78,254, RSI 23.7, 4.7% under the 24 h high).

## At the trigger (n=755)

| | +0.5% first | -0.5% first | Up 60 min | Max up >= 1% in 4 h |
|---|---|---|---|---|
| All | 47.8% | 49.3% | 55.8% | 44.1% |
| OI up the last hour (shorts pressing, the shot) n=178 | 48.9% | 50.0% | 54.5% | 45.5% |
| OI down (longs flushed) n=431 | 48.0% | 48.5% | 56.4% | 46.6% |
| At a 1,000 round number n=247 | 49.0% | 48.6% | 57.1% | 42.9% |
| Under the prior-day low n=378 | 48.4% | 47.1% | 56.1% | 42.3% |

- A small lean up over the next hour (56%, about 3 standard errors over 50%), no lean on the next ±0.5%.
- The trigger bar's low was broken within 4 h in 87%: the cascade usually makes one more low.
- OI, round numbers and the prior-day low did not change the odds by more than 2 points.
- By year, up 60 min ran 51% (2022, 2025) to 62% (2024): the cycle again.

## Momentum-shift signals (first firing within 2 h after the trigger)

| Signal | Fired | Median lag | +0.5% first | -0.5% first | Low broken later |
|---|---|---|---|---|---|
| RANDOM bar (base rate) | 100% | 65 min | 44.9% | 49.4% | 51% |
| S1 first close back inside the band | 100% | 10 min | 46.1% | 50.9% | 65% |
| S2 RSI back above 30 | 99% | 15 min | 46.0% | 49.6% | 56% |
| S3 bullish RSI divergence on a new low | 57% | 25 min | 46.6% | 50.8% | 72% |
| S4 green bar, taker share >= +0.20 | 91% | 30 min | 45.2% | 50.7% | 52% |
| S5 close above the high of the low bar | 92% | 30 min | 48.8% | 45.4% | 49% |

- **No signal anticipates the bounce.** Four of five sit within 1.7 points of a random bar.
- **S5 (reclaim of the low bar's high) is the only one that tilts:** 48.8 / 45.4 against 44.9 / 49.4 random, about 2 standard errors. It held in 2024 and 2025 (52%, 54% up first) but not 2022-23. Worth a pre-registered check, not a claim.
- **S1 and S3, the textbook 'back inside the band' and 'divergence', fire early and the low then breaks more often (65%, 72%)**: they mark the first pause, not the turn.

## Answer to the operator

- MTS does not anticipate bounces accurately yet, and the tested shift signals do not either; the honest live read is the base rates above.
- Next: S5 with level context (swing low, round number, VAL) in `level-approach-prep`, with a 2026 confirmation run before anything reaches the panel.
