# dca5f5ad7676: BTCUSDT 15m, CoinGlass (Binance), 10-27..10-31, captured ~20:45Z 10-31

Prior: none

- Legend at capture: O 76,653.7 H 76,714.4 L 76,650.5 C 76,692.0; BB(20,2) mid 76,937.9, upper 77,502.5, lower 76,373.2; OI 95.754K; CVD -26.085K; net delta -6.568K; RSI14 39.78 (SMA 38.96); Stoch RSI 60.07 / 75.97.
- Operator circles: (1) 10-28 ~08:30Z high ~81.4k, (2) 10-28 ~18:30Z high ~81.5k, both not taken out; (3) 10-29 ~15:00Z took the highs out, then the drop to ~78k.
- His point: a held high lets shorts build; the take-out comes in the next day. Measured as C26 (`research/eagle_eyes_picture_2026-10-28/failed_retest_takeout.py`): the 10-28 20:45Z held retest of 81,823 was taken 19h later and swept back.

| id | verdict | chart claim | data check |
|---|---|---|---|
| 1 | MATCH | 10-28 highs ~81.4-81.5k held on two tries | `failed_retest_takeout.py` recent row: 10-28 20:45Z held retest of 81,823 (Binance 15m) |
| 2 | MATCH | 10-29 took that high out, then dropped | same row: taken 19.0h later, closed back under within 1h (swept back True) |
| 3 | NOT_IN_DATA | "shorts built" under the held highs | no net-shorts history recorder yet (C22) |
