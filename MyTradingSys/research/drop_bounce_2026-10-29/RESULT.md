# Fast 1m drop, bounce to the BB mid: what next? (2026-10-29)

These are descriptive counts only: no fees and no edge claim. Definitions are in the headers of `study.py` and `fractal.py`. The data is the Binance USD-M BTCUSDT 1m archive, 2022-01 to 2026-09.

The trigger was the operator's shots 7495630a229a, ab1b2752e4c1, 38a360af27ef and 703c33723270:
- Price fell from 80.85k to a 78,297 spot low (perp 78,267) at 20:47Z.
- It then bounced to the 1m BB mid around 79.3-79.5k.

## Event study (drop >= 2.5%, low 20-60 min old, bounce 25-55%, close at the 1m BB mid)

All events (n=813). The window is the next 4 hours:

| Outcome | Share |
|---|---|
| Low broken | 44% |
| Low retested within 0.3%, not broken | 10% |
| Low held, no retest | 45% |
| Retest of the low came before the 61.8% bounce level | 48% |
| 61.8% bounce level came first | 37% |
| Neither level reached | 15% |
| Next 60 1m closes below the lower band | 5% |
| Next 60 1m closes between the lower band and the mid | 43% |
| Next 60 1m closes above the mid | 52% |
| Close higher 60 minutes later | 54% |

Splits:
- **Bounce taker-buy delta (more vs less buying):** the low breaks 43% vs 46%. That is no real difference.
- **Bounce volume per bar under half the drop's:** the low breaks 52% (n=75), against 44% for all events.
- **By year:** the break rate was 34% in 2023 and 50% in 2022 and 2025. The year matters more than the bounce quality.

## Fractal search (shape of 19:55-21:30Z, correlation >= 0.85)

- **Matches:** n=511. The low broke within 4 hours in 48% and held in 40%.
- **Direction:** 53% closed higher after 60 minutes and 55% after 4 hours.
- **Size of the next move:** the median max up was +0.88% and the median max down was -0.81%.
- **Close matches only (corr >= 0.90, n=314):** the results were the same.

Close-up of the bounce (spot, live 10-29):
- **Low to 21:16Z:** the delta was -194 BTC.
- **21:17-21:19Z:** one push with a delta of +76 BTC, to 79,811.
- **After the push:** the delta went back to slightly negative. The cumulative delta since the low is -174 BTC.
- **Volume:** volume per bar fell from 148 on the drop to about 25-30 now.

## Reading

- **Direction:** after this shape, history is close to a coin flip. A break of the low within 4 hours is about as likely as a hold.
- **Bounce quality:** whether the bounce had more taker buying did not change the odds. Only a very thin bounce, with volume under half the drop's, raised the break rate a little.
- **The BB question:** about 95% of the next hour's 1m closes stayed inside the bands, split about evenly between the lower half and the upper half.

## Follow-up: the bounce failed and came back near the low (`followup.py`, shot 85ba89446b0d)

Situation, 10-29 21:47Z:
- The bounce peaked at 79,811, about 60% of the drop retraced.
- Price then faded back to 78,986, within 1% of the low, with about -157 BTC of net spot selling since 21:30Z.

Past cases where the bounce reached at least 55% retrace and then came back within 1% of the low (n=116):

| Group | Low broken within 1h | within 4h | Close higher 4h later |
|---|---|---|---|
| All (n=116) | 16% | 43% | 59% |
| Fade with net selling, delta share <= -0.10 (n=47) | 9% | 38% | 57% |
| Fade without net selling (n=69) | 22% | 46% | 59% |

Reading:
- **Selling into the fade did not raise the break rate.** It was lower: 38% vs 46% within 4h.
- **This fits Fabio's absorption (F-CVD3):** sell effort near the low without a result.
- **Not settled:** n=47 is small, the gap is within noise, and this is fee-free and descriptive.
- **A quick break is unlikely:** a break of the low within the next hour was uncommon (16%).
