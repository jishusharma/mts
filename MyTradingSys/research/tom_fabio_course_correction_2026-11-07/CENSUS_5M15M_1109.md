# Auction census on 5m and 15m, session blocks, HTF ladder gate, node exits (census-5m-15m-7y-session-ladder-1109)

**No edge. The pre-registered H1 (15m rejection fades, London/NY only, with the HTF ladder, node-to-node exit with break-even and half off at POC, Deribit maker fees) loses 0.11 R per trade over 1,484 trades (t = -1.4), and loses on the taker arm (-0.36 R, t = -5.2). Before fees it makes +0.06 R (about 0.8 SE): the fade carries no direction, and 40 bps stops make fees decisive. 5m is worse on every arm (H1 equivalent -0.34 R, n = 1,579). The node + break-even exit was the last untested exit shape (POSTMORTEM_OPUS.md s6); it joins the closed list.**

Pre-registration: `PRE_REG_5M15M_1109.md` (committed e0b5fd922 before any run). Code: `auction_census.py` (`python auction_census.py 5m15m <data_dir>`), tests `test_auction_census.py` (10 pass). Output: `census_5m15m_1109.json`. The per-event dumps (9 MB each) are not committed; the command rebuilds them in about 90 s.

## Context

- Regime: 7 years pooled (2019-11-08 .. 2026-11-07), split by HTF ladder bias and year below.
- Phase: `range_1024` (from 2026-10-24, the Bible range) has 5 trades on 15m and 7 on 5m under the H1 gate: reported, not judged.
- Session: UTC blocks asia 00-07, london 07-13, ny 13-21, late 21-24 (OURS).
- Entry: the old census rule (close of the classifier's firing bar). The Deribit arm charges it as maker, as the card asked; a market entry at the close is really taker, so the taker arm is the honest one.
- Data: Binance spot BTCUSDT 5m (738,167 bars), 15m (246,057), 1d, from data-api.binance.vision, closed bars only. No order flow (klines carry no delta).

## H1 and its parts (15m, fades = FAST_REJECTION + WEAK_REJECTION)

| what | value |
|---|---|
| trades | 1,484 |
| gross R per trade | +0.064 (SE 0.077) |
| net R, Deribit | -0.106 (SE 0.078) |
| net R, taker 5 bps each leg | -0.358 (SE 0.068) |
| net R, taker + slippage stress | -0.527 |
| exits | target 313, stop 1,063 (656 of them at break-even), time 108 |
| median stop | 39.5 bps; median node target 2.1 R |

Kill line (PRE_REG): net > 0 and > 2 SE and positive under taker. Failed on all three.

## All arms

| tf | exit | fee | gate | n | net R/trade | SE | t |
|---|---|---|---|---|---|---|---|
| 15m | bracket1R | deribit | none | 5493 | -0.162 | 0.015 | -10.6 |
| 15m | bracket1R | taker | none | 5493 | -0.470 | 0.017 | -28.1 |
| 15m | bracket1R | taker+slip | none | 5493 | -0.644 | 0.019 | -33.3 |
| 15m | node+BE | deribit | none | 5462 | -0.139 | 0.029 | -4.9 |
| 15m | node+BE | taker | none | 5462 | -0.398 | 0.027 | -14.8 |
| 15m | node+BE | taker+slip | none | 5462 | -0.573 | 0.028 | -20.7 |
| 15m | bracket1R | deribit | session | 3054 | -0.184 | 0.020 | -9.0 |
| 15m | bracket1R | taker | session | 3054 | -0.479 | 0.022 | -21.7 |
| 15m | bracket1R | taker+slip | session | 3054 | -0.647 | 0.025 | -25.7 |
| 15m | node+BE | deribit | session | 3032 | -0.123 | 0.044 | -2.8 |
| 15m | node+BE | taker | session | 3032 | -0.374 | 0.040 | -9.3 |
| 15m | node+BE | taker+slip | session | 3032 | -0.543 | 0.040 | -13.5 |
| 15m | bracket1R | deribit | ladder | 2668 | -0.183 | 0.022 | -8.4 |
| 15m | bracket1R | taker | ladder | 2668 | -0.479 | 0.025 | -19.5 |
| 15m | bracket1R | taker+slip | ladder | 2668 | -0.648 | 0.029 | -22.6 |
| 15m | node+BE | deribit | ladder | 2649 | -0.153 | 0.048 | -3.2 |
| 15m | node+BE | taker | ladder | 2649 | -0.405 | 0.044 | -9.2 |
| 15m | node+BE | taker+slip | ladder | 2649 | -0.574 | 0.044 | -13.1 |
| 15m | bracket1R | deribit | session+ladder | 1495 | -0.195 | 0.029 | -6.7 |
| 15m | bracket1R | taker | session+ladder | 1495 | -0.492 | 0.032 | -15.3 |
| 15m | bracket1R | taker+slip | session+ladder | 1495 | -0.659 | 0.037 | -17.8 |
| 15m | node+BE | deribit | session+ladder | 1484 | -0.106 | 0.078 | -1.4 |
| 15m | node+BE | taker | session+ladder | 1484 | -0.358 | 0.068 | -5.2 |
| 15m | node+BE | taker+slip | session+ladder | 1484 | -0.527 | 0.066 | -8.0 |
| 5m | bracket1R | deribit | none | 5500 | -0.221 | 0.018 | -12.5 |
| 5m | bracket1R | taker | none | 5500 | -0.722 | 0.022 | -32.4 |
| 5m | bracket1R | taker+slip | none | 5500 | -1.003 | 0.028 | -35.8 |
| 5m | node+BE | deribit | none | 5488 | -0.225 | 0.033 | -6.8 |
| 5m | node+BE | taker | none | 5488 | -0.626 | 0.035 | -18.0 |
| 5m | node+BE | taker+slip | none | 5488 | -0.907 | 0.038 | -23.6 |
| 5m | bracket1R | deribit | session | 3117 | -0.250 | 0.024 | -10.3 |
| 5m | bracket1R | taker | session | 3117 | -0.752 | 0.032 | -23.4 |
| 5m | bracket1R | taker+slip | session | 3117 | -1.036 | 0.041 | -25.1 |
| 5m | node+BE | deribit | session | 3109 | -0.258 | 0.048 | -5.4 |
| 5m | node+BE | taker | session | 3109 | -0.662 | 0.051 | -13.0 |
| 5m | node+BE | taker+slip | session | 3109 | -0.946 | 0.057 | -16.7 |
| 5m | bracket1R | deribit | ladder | 2771 | -0.251 | 0.026 | -9.7 |
| 5m | bracket1R | taker | ladder | 2771 | -0.716 | 0.034 | -21.0 |
| 5m | bracket1R | taker+slip | ladder | 2771 | -0.981 | 0.044 | -22.5 |
| 5m | node+BE | deribit | ladder | 2760 | -0.267 | 0.040 | -6.6 |
| 5m | node+BE | taker | ladder | 2760 | -0.643 | 0.046 | -14.1 |
| 5m | node+BE | taker+slip | ladder | 2760 | -0.910 | 0.053 | -17.1 |
| 5m | bracket1R | deribit | session+ladder | 1586 | -0.297 | 0.036 | -8.2 |
| 5m | bracket1R | taker | session+ladder | 1586 | -0.770 | 0.051 | -15.1 |
| 5m | bracket1R | taker+slip | session+ladder | 1586 | -1.044 | 0.067 | -15.6 |
| 5m | node+BE | deribit | session+ladder | 1579 | -0.339 | 0.054 | -6.3 |
| 5m | node+BE | taker | session+ladder | 1579 | -0.724 | 0.064 | -11.3 |
| 5m | node+BE | taker+slip | session+ladder | 1579 | -0.999 | 0.077 | -12.9 |

**15m, split by session** (fades, session+ladder gate, node+BE, Deribit fees)

| session | n | net R | SE |
|---|---|---|---|
| london | 602 | -0.015 | 0.177 |
| ny | 882 | -0.168 | 0.053 |

**15m, split by ladder** (fades, session+ladder gate, node+BE, Deribit fees)

| ladder | n | net R | SE |
|---|---|---|---|
| bearish | 251 | -0.074 | 0.101 |
| bullish | 571 | -0.141 | 0.067 |
| pullback_in_macro_bull | 436 | -0.215 | 0.077 |
| rally_in_macro_bear | 226 | +0.158 | 0.448 |

**15m, split by phase** (fades, session+ladder gate, node+BE, Deribit fees)

| phase | n | net R | SE |
|---|---|---|---|
| range_1024 | 5 | +2.369 | 1.157 |
| rest | 1479 | -0.114 | 0.078 |

**15m, split by year** (fades, session+ladder gate, node+BE, Deribit fees)

| year | n | net R | SE |
|---|---|---|---|
| 2019 | 39 | -0.477 | 0.150 |
| 2020 | 205 | -0.085 | 0.104 |
| 2021 | 183 | -0.090 | 0.114 |
| 2022 | 205 | -0.058 | 0.121 |
| 2023 | 254 | -0.307 | 0.084 |
| 2024 | 201 | -0.232 | 0.104 |
| 2025 | 227 | -0.286 | 0.117 |
| 2026 | 170 | +0.568 | 0.596 |

**5m, split by session** (fades, session+ladder gate, node+BE, Deribit fees)

| session | n | net R | SE |
|---|---|---|---|
| london | 631 | -0.312 | 0.096 |
| ny | 948 | -0.357 | 0.063 |

**5m, split by ladder** (fades, session+ladder gate, node+BE, Deribit fees)

| ladder | n | net R | SE |
|---|---|---|---|
| bearish | 271 | -0.408 | 0.139 |
| bullish | 626 | -0.278 | 0.093 |
| pullback_in_macro_bull | 451 | -0.351 | 0.089 |
| rally_in_macro_bear | 231 | -0.397 | 0.121 |

**5m, split by phase** (fades, session+ladder gate, node+BE, Deribit fees)

| phase | n | net R | SE |
|---|---|---|---|
| range_1024 | 7 | -0.844 | 0.263 |
| rest | 1572 | -0.337 | 0.054 |

**5m, split by year** (fades, session+ladder gate, node+BE, Deribit fees)

| year | n | net R | SE |
|---|---|---|---|
| 2019 | 46 | -0.637 | 0.149 |
| 2020 | 210 | -0.328 | 0.089 |
| 2021 | 191 | +0.127 | 0.240 |
| 2022 | 242 | -0.207 | 0.115 |
| 2023 | 252 | -0.514 | 0.152 |
| 2024 | 237 | -0.438 | 0.145 |
| 2025 | 238 | -0.523 | 0.108 |
| 2026 | 163 | -0.328 | 0.150 |

## Notes

- The gates help a little, and only on 15m: session + ladder takes the node exit from -0.14 to -0.11 R (Deribit). On 5m the gates make it worse.
- The node + break-even exit beats the 1R bracket on 15m (-0.11 vs -0.20 R at H1) but not enough to cross zero.
- 2026 on 15m is +0.57 R (n = 170) and `rally_in_macro_bear` is +0.16 R (n = 226), against negative results in every other year and bias. These are post-hoc cells among about 30; they are leads for the context-only testnet run (tf-testnet-forward-range-phase-amend-1109), not findings.
- Slippage stress uses `trade_costs.net_return`'s `slip_rt` default: 4 bps round trip in code, while FORMULAS.md s13 says 2 bps. That mismatch needs a fix in one of the two places (not done here).
- Folds `census-fetch-binance-mirror-1109` (use the data-api mirror, add slippage): done in this run.
