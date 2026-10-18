# Angle (b): trader's-eye check at 12 seeded random DEV decision points (seed 20261016)

Each block: what a trader sees at that minute, computed by hand from the raw bars (pandas), then the builder's row and
the disagreements on the checked fields. Both sides are shown for the nearest level; the random side is the one checked.

## 2022-08-07 10:59 UTC close (t = 314579), checked side: long

- Price 22985.1. Last closed daily: O 23298.0 H 23341.8 L 22883.6 C 22943.3 (red, range 458.2). Last closed 12h: O 23148.2 H 23250.0 L 22883.6 C 22943.3 (red, range 366.4).
- Last closed 8h: O 22943.2 H 23034.6 L 22830.9 C 23000.0 (green, range 203.7). Last closed 4h: O 22979.8 H 23015.7 L 22930.0 C 23000.0 (green, range 85.7); pattern inside (daily inside).
- Partial daily so far: O 22943.2 H 23034.6 L 22830.9 C 22985.1 (green, range 203.7).
- Nearest support below: 22948.7 (vwap_session, 0.121467 ATR away, 3 layer(s) within 0.5 ATR). Nearest resistance above: 22999 (krown_zone, 0.046351 ATR away, 4 layer(s)).
- Phase A markup / phase B distribution; intraday balance; 4h Bollinger inside (%b 0.466881), daily inside; vol regime low; session london (weekend); funding neg.
- Stop ladder (long): daily rung 0.44159 %, 12h 0.44159 %, 8h 0.670869 % -> rung 1d (0.44159 %, cost 0.317036 R).

Builder row: c_1d=(23298, 23341.8, 22883.6, 22943.3), c_12h=(23148.2, 23250, 22883.6, 22943.3), c_8h=(22943.2, 23034.6, 22830.9, 23000), c_4h=(22979.8, 23015.7, 22930, 23000), p_1d=(22943.2, 23034.6, 22830.9, 22985.1), near_price=22948.7, near_src=vwap_session, n_layers=3, phase_a=markup, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=1d, ladder_stop_pct=0.44159, pat_4h=inside, pat_1d=inside, intraday=balance, vol_regime=low, session=london, funding=neg.
Disagreements: none.

## 2022-10-14 04:59 UTC close (t = 412139), checked side: long

- Price 19803.7. Last closed daily: O 19148.1 H 19498.6 L 17917.8 C 19365.5 (green, range 1580.8). Last closed 12h: O 18745.0 H 19498.6 L 17917.8 C 19365.5 (green, range 1580.8).
- Last closed 8h: O 18947.7 H 19498.6 L 18892.8 C 19365.5 (green, range 605.8). Last closed 4h: O 19365.4 H 19947.9 L 19330.1 C 19806.3 (green, range 617.8); pattern three_up (daily bull_pin|outside).
- Partial daily so far: O 19365.4 H 19947.9 L 19330.1 C 19803.7 (green, range 617.8).
- Nearest support below: 19787.6 (krown_zone, 0.0527079 ATR away, 2 layer(s) within 0.5 ATR). Nearest resistance above: 19840 (krown_zone, 0.118838 ATR away, 1 layer(s)).
- Phase A markup / phase B accumulation; intraday trend_up; 4h Bollinger walk_up (%b 1.34235), daily inside; vol regime mid; session asia; funding low.
- Stop ladder (long): daily rung 9.52297 %, 12h 9.52297 %, 8h 4.59965 % -> rung 8h (4.59965 %, cost 0.0304371 R).

Builder row: c_1d=(19148.1, 19498.6, 17917.8, 19365.5), c_12h=(18745, 19498.6, 17917.8, 19365.5), c_8h=(18947.7, 19498.6, 18892.8, 19365.5), c_4h=(19365.4, 19947.9, 19330.1, 19806.3), p_1d=(19365.4, 19947.9, 19330.1, 19803.7), near_price=19787.6, near_src=krown_zone, n_layers=2, phase_a=markup, bb_4h_state=walk_up, bb_1d_state=inside, ladder_rung=8h, ladder_stop_pct=4.59965, pat_4h=three_up, pat_1d=bull_pin|outside, intraday=trend_up, vol_regime=mid, session=asia, funding=low.
Disagreements: none.

## 2022-12-27 11:59 UTC close (t = 519119), checked side: long

- Price 16823.7. Last closed daily: O 16824.5 H 16936.8 L 16781.1 C 16912.9 (green, range 155.7). Last closed 12h: O 16912.8 H 16968.0 L 16800.6 C 16823.7 (red, range 167.4).
- Last closed 8h: O 16912.8 H 16968.0 L 16830.0 C 16859.6 (red, range 138.0). Last closed 4h: O 16859.6 H 16874.8 L 16800.6 C 16823.7 (red, range 74.2); pattern three_down (daily none).
- Partial daily so far: O 16912.8 H 16968.0 L 16800.6 C 16823.7 (red, range 167.4).
- Nearest support below: 16820 (fabio_vp_day, 0.0455625 ATR away, 3 layer(s) within 0.5 ATR). Nearest resistance above: 16830 (krown_zone, 0.0775794 ATR away, 3 layer(s)).
- Phase A markdown / phase B distribution; intraday trend_down; 4h Bollinger inside (%b 0.414039), daily inside; vol regime low; session london; funding low.
- Stop ladder (long): daily rung 0.253214 %, 12h 0.137306 %, 8h nan % -> rung 1d (0.253214 %, cost 0.552892 R).

Builder row: c_1d=(16824.5, 16936.8, 16781.1, 16912.9), c_12h=(16912.8, 16968, 16800.6, 16823.7), c_8h=(16912.8, 16968, 16830, 16859.6), c_4h=(16859.6, 16874.8, 16800.6, 16823.7), p_1d=(16912.8, 16968, 16800.6, 16823.7), near_price=16820, near_src=fabio_vp_day, n_layers=3, phase_a=markdown, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=1d, ladder_stop_pct=0.253214, pat_4h=three_down, pat_1d=none, intraday=trend_down, vol_regime=low, session=london, funding=low.
Disagreements: none.

## 2023-02-22 14:59 UTC close (t = 601379), checked side: short

- Price 23927.7. Last closed daily: O 24849.9 H 25347.6 L 24150.0 C 24443.4 (red, range 1197.6). Last closed 12h: O 24443.3 H 24468.5 L 23851.5 C 24156.4 (red, range 617.0).
- Last closed 8h: O 24443.3 H 24468.5 L 23851.5 C 24059.6 (red, range 617.0). Last closed 4h: O 24059.5 H 24215.9 L 23855.3 C 24156.4 (green, range 360.6); pattern none (daily none).
- Partial daily so far: O 24443.3 H 24468.5 L 23851.5 C 23927.7 (red, range 617.0).
- Nearest support below: 23837.4 (krown_zone, 0.217639 ATR away, 1 layer(s) within 0.5 ATR). Nearest resistance above: 23962.7 (krown_zone, 0.0843562 ATR away, 3 layer(s)).
- Phase A accumulation / phase B markup; intraday trend_down; 4h Bollinger reenter_from_lower (%b 0.106157), daily inside; vol regime high; session ny; funding low.
- Stop ladder (short): daily rung 5.93413 %, 12h 2.26014 %, 8h 2.26014 % -> rung 12h (2.26014 %, cost 0.061943 R).

Builder row: c_1d=(24849.9, 25347.6, 24150, 24443.4), c_12h=(24443.3, 24468.5, 23851.5, 24156.4), c_8h=(24443.3, 24468.5, 23851.5, 24059.6), c_4h=(24059.5, 24215.9, 23855.3, 24156.4), p_1d=(24443.3, 24468.5, 23851.5, 23927.7), near_price=23962.7, near_src=krown_zone, n_layers=3, phase_a=accumulation, bb_4h_state=reenter_from_lower, bb_1d_state=inside, ladder_rung=12h, ladder_stop_pct=2.26014, pat_4h=none, pat_1d=none, intraday=trend_down, vol_regime=high, session=ny, funding=low.
Disagreements: none.

## 2023-05-04 20:59 UTC close (t = 703979), checked side: short

- Price 28856.8. Last closed daily: O 28656.4 H 29258.4 L 28080.0 C 29018.4 (green, range 1178.4). Last closed 12h: O 29018.4 H 29380.0 L 28938.5 C 29145.0 (green, range 441.5).
- Last closed 8h: O 29048.7 H 29380.0 L 28660.0 C 28850.0 (red, range 720.0). Last closed 4h: O 28850.0 H 28966.0 L 28660.0 C 28883.2 (green, range 306.0); pattern bull_pin (daily none).
- Partial daily so far: O 29018.4 H 29380.0 L 28660.0 C 28856.8 (red, range 720.0).
- Nearest support below: 28845.3 (krown_zone, 0.025786 ATR away, 2 layer(s) within 0.5 ATR). Nearest resistance above: 28870 (krown_zone, 0.0295978 ATR away, 4 layer(s)).
- Phase A markdown / phase B distribution; intraday trend_up; 4h Bollinger inside (%b 0.731366), daily inside; vol regime high; session ny; funding low.
- Stop ladder (short): daily rung 1.3917 %, 12h 1.81309 %, 8h 1.81309 % -> rung 1d (1.3917 %, cost 0.100596 R).

Builder row: c_1d=(28656.4, 29258.4, 28080, 29018.4), c_12h=(29018.4, 29380, 28938.5, 29145), c_8h=(29048.7, 29380, 28660, 28850), c_4h=(28850, 28966, 28660, 28883.2), p_1d=(29018.4, 29380, 28660, 28856.8), near_price=28870, near_src=krown_zone, n_layers=4, phase_a=markdown, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=1d, ladder_stop_pct=1.3917, pat_4h=bull_pin, pat_1d=none, intraday=trend_up, vol_regime=high, session=ny, funding=low.
Disagreements: none.

## 2023-06-23 13:59 UTC close (t = 775559), checked side: long

- Price 30063.3. Last closed daily: O 29988.5 H 30488.0 L 29500.1 C 29875.0 (red, range 987.9). Last closed 12h: O 29875.0 H 30195.7 L 29792.0 C 30125.3 (green, range 403.7).
- Last closed 8h: O 29875.0 H 30079.9 L 29792.0 C 29927.0 (green, range 287.9). Last closed 4h: O 29926.9 H 30195.7 L 29899.9 C 30125.3 (green, range 295.8); pattern bull_engulf|outside (daily inside).
- Partial daily so far: O 29875.0 H 30233.9 L 29792.0 C 30063.3 (green, range 441.9).
- Nearest support below: 30048.2 (krown_zone, 0.0292203 ATR away, 4 layer(s) within 0.5 ATR). Nearest resistance above: 30105 (fabio_vp_day, 0.0806944 ATR away, 1 layer(s)).
- Phase A markdown / phase B markup; intraday trend_down; 4h Bollinger inside (%b 0.703668), daily walk_up; vol regime high; session ny; funding low.
- Stop ladder (long): daily rung 1.87338 %, 12h 0.902429 %, 8h 0.902429 % -> rung 1d (1.87338 %, cost 0.0747312 R).

Builder row: c_1d=(29988.5, 30488, 29500.1, 29875), c_12h=(29875, 30195.7, 29792, 30125.3), c_8h=(29875, 30079.9, 29792, 29927), c_4h=(29926.9, 30195.7, 29899.9, 30125.3), p_1d=(29875, 30233.9, 29792, 30063.3), near_price=30048.2, near_src=krown_zone, n_layers=4, phase_a=markdown, bb_4h_state=inside, bb_1d_state=walk_up, ladder_rung=1d, ladder_stop_pct=1.87338, pat_4h=bull_engulf|outside, pat_1d=inside, intraday=trend_down, vol_regime=high, session=ny, funding=low.
Disagreements: none.

## 2023-08-20 17:59 UTC close (t = 859319), checked side: long

- Price 26111.3. Last closed daily: O 26042.0 H 26269.4 L 25783.4 C 26088.3 (green, range 486.0). Last closed 12h: O 26088.4 H 26197.0 L 26027.9 C 26163.9 (green, range 169.1).
- Last closed 8h: O 26073.6 H 26209.6 L 25948.5 C 26095.0 (green, range 261.1). Last closed 4h: O 26163.8 H 26209.6 L 25948.5 C 26095.0 (red, range 261.1); pattern outside (daily inside).
- Partial daily so far: O 26088.4 H 26209.6 L 25948.5 C 26111.3 (green, range 261.1).
- Nearest support below: 26100 (fabio_vp_day, 0.0420242 ATR away, 3 layer(s) within 0.5 ATR). Nearest resistance above: 26269.4 (krown_zone, 0.587967 ATR away, 0 layer(s)).
- Phase A distribution / phase B markdown; intraday balance; 4h Bollinger inside (%b 0.380906), daily walk_down; vol regime high; session ny (weekend); funding neg.
- Stop ladder (long): daily rung 1.25578 %, 12h 0.319402 %, 8h 0.623485 % -> rung 1d (1.25578 %, cost 0.111485 R).

Builder row: c_1d=(26042, 26269.4, 25783.4, 26088.3), c_12h=(26088.4, 26197, 26027.9, 26163.9), c_8h=(26073.6, 26209.6, 25948.5, 26095), c_4h=(26163.8, 26209.6, 25948.5, 26095), p_1d=(26088.4, 26209.6, 25948.5, 26111.3), near_price=26100, near_src=fabio_vp_day, n_layers=3, phase_a=distribution, bb_4h_state=inside, bb_1d_state=walk_down, ladder_rung=1d, ladder_stop_pct=1.25578, pat_4h=outside, pat_1d=inside, intraday=balance, vol_regime=high, session=ny, funding=neg.
Disagreements: none.

## 2023-11-06 10:59 UTC close (t = 971219), checked side: long

- Price 35172.3. Last closed daily: O 35069.7 H 35455.2 L 34356.0 C 35025.5 (red, range 1099.2). Last closed 12h: O 35103.6 H 35455.2 L 34356.0 C 35025.5 (red, range 1099.2).
- Last closed 8h: O 35025.5 H 35137.9 L 34743.2 C 34918.5 (red, range 394.7). Last closed 4h: O 34992.9 H 35044.0 L 34743.2 C 34918.5 (red, range 300.8); pattern none (daily bull_pin|outside).
- Partial daily so far: O 35025.5 H 35299.9 L 34743.2 C 35172.3 (green, range 556.7).
- Nearest support below: 35154.3 (krown_zone, 0.0487098 ATR away, 5 layer(s) within 0.5 ATR). Nearest resistance above: 35260 (fabio_vp_day, 0.237325 ATR away, 2 layer(s)).
- Phase A markup / phase B markup; intraday trend_up; 4h Bollinger inside (%b 0.596401), daily inside; vol regime mid; session london; funding low.
- Stop ladder (long): daily rung 2.32086 %, 12h 2.32086 %, 8h 1.21999 % -> rung 1d (2.32086 %, cost 0.0603225 R).

Builder row: c_1d=(35069.7, 35455.2, 34356, 35025.5), c_12h=(35103.6, 35455.2, 34356, 35025.5), c_8h=(35025.5, 35137.9, 34743.2, 34918.5), c_4h=(34992.9, 35044, 34743.2, 34918.5), p_1d=(35025.5, 35299.9, 34743.2, 35172.3), near_price=35154.3, near_src=krown_zone, n_layers=5, phase_a=markup, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=1d, ladder_stop_pct=2.32086, pat_4h=none, pat_1d=bull_pin|outside, intraday=trend_up, vol_regime=mid, session=london, funding=low.
Disagreements: none.

## 2023-11-10 10:59 UTC close (t = 976979), checked side: long

- Price 36775.2. Last closed daily: O 35626.7 H 38499.9 L 35304.0 C 36719.5 (green, range 3195.9). Last closed 12h: O 36816.9 H 38499.9 L 35304.0 C 36719.5 (red, range 3195.9).
- Last closed 8h: O 36719.6 H 36940.6 L 36461.8 C 36480.2 (red, range 478.8). Last closed 4h: O 36754.9 H 36836.8 L 36465.4 C 36480.2 (red, range 371.4); pattern bear_engulf|inside (daily three_up).
- Partial daily so far: O 36719.6 H 36940.6 L 36350.0 C 36775.2 (green, range 590.6).
- Nearest support below: 36648.7 (vwap_session, 0.178683 ATR away, 2 layer(s) within 0.5 ATR). Nearest resistance above: 37000 (round_1k, 0.317581 ATR away, 2 layer(s)).
- Phase A markup / phase B markup; intraday trend_up; 4h Bollinger inside (%b 0.724491), daily inside; vol regime high; session london; funding high.
- Stop ladder (long): daily rung 4.00052 %, 12h 4.00052 %, 8h 0.852205 % -> rung 8h (0.852205 %, cost 0.16428 R).

Builder row: c_1d=(35626.7, 38499.9, 35304, 36719.5), c_12h=(36816.9, 38499.9, 35304, 36719.5), c_8h=(36719.6, 36940.6, 36461.8, 36480.2), c_4h=(36754.9, 36836.8, 36465.4, 36480.2), p_1d=(36719.6, 36940.6, 36350, 36775.2), near_price=36648.7, near_src=vwap_session, n_layers=2, phase_a=markup, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=8h, ladder_stop_pct=0.852205, pat_4h=bear_engulf|inside, pat_1d=three_up, intraday=trend_up, vol_regime=high, session=london, funding=high.
Disagreements: none.

## 2023-12-16 13:59 UTC close (t = 1028999), checked side: short

- Price 42417.1. Last closed daily: O 43032.3 H 43098.0 L 41668.0 C 41968.0 (red, range 1430.0). Last closed 12h: O 41968.0 H 42448.4 L 41638.1 C 42349.9 (green, range 810.3).
- Last closed 8h: O 41968.0 H 42448.4 L 41638.1 C 42243.1 (green, range 810.3). Last closed 4h: O 42243.0 H 42368.9 L 42114.7 C 42349.9 (green, range 254.2); pattern none (daily inside).
- Partial daily so far: O 41968.0 H 42577.0 L 41638.1 C 42417.1 (green, range 938.9).
- Nearest support below: 42216.5 (vwap_session, 0.297057 ATR away, 4 layer(s) within 0.5 ATR). Nearest resistance above: 42440 (krown_zone, 0.0339144 ATR away, 2 layer(s)).
- Phase A markup / phase B markup; intraday balance; 4h Bollinger inside (%b 0.466603), daily inside; vol regime high; session ny (weekend); funding low.
- Stop ladder (short): daily rung 1.60525 %, 12h 0.073791 %, 8h 0.073791 % -> rung 1d (1.60525 %, cost 0.0872139 R).

Builder row: c_1d=(43032.3, 43098, 41668, 41968), c_12h=(41968, 42448.4, 41638.1, 42349.9), c_8h=(41968, 42448.4, 41638.1, 42243.1), c_4h=(42243, 42368.9, 42114.7, 42349.9), p_1d=(41968, 42577, 41638.1, 42417.1), near_price=42440, near_src=krown_zone, n_layers=2, phase_a=markup, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=1d, ladder_stop_pct=1.60525, pat_4h=none, pat_1d=inside, intraday=balance, vol_regime=high, session=ny, funding=low.
Disagreements: none.

## 2024-05-09 09:59 UTC close (t = 1237559), checked side: short

- Price 61272.7. Last closed daily: O 62296.0 H 62994.9 L 60843.6 C 61157.9 (red, range 2151.3). Last closed 12h: O 62224.9 H 62800.0 L 60843.6 C 61157.9 (red, range 1956.4).
- Last closed 8h: O 61157.9 H 61779.0 L 61087.0 C 61222.5 (green, range 692.0). Last closed 4h: O 61647.5 H 61753.2 L 61087.0 C 61222.5 (red, range 666.2); pattern none (daily three_down).
- Partial daily so far: O 61157.9 H 61779.0 L 60900.0 C 61272.7 (green, range 879.0).
- Nearest support below: 61000 (round_1k, 0.285155 ATR away, 3 layer(s) within 0.5 ATR). Nearest resistance above: 61384.9 (vwap_session, 0.11735 ATR away, 2 layer(s)).
- Phase A markdown / phase B markdown; intraday trend_down; 4h Bollinger inside (%b 0.0528762), daily inside; vol regime low; session london; funding low.
- Stop ladder (short): daily rung 2.81071 %, 12h 2.49263 %, 8h 0.826306 % -> rung 12h (2.49263 %, cost 0.0561656 R).

Builder row: c_1d=(62296, 62994.9, 60843.6, 61157.9), c_12h=(62224.9, 62800, 60843.6, 61157.9), c_8h=(61157.9, 61779, 61087, 61222.5), c_4h=(61647.5, 61753.2, 61087, 61222.5), p_1d=(61157.9, 61779, 60900, 61272.7), near_price=61384.9, near_src=vwap_session, n_layers=2, phase_a=markdown, bb_4h_state=inside, bb_1d_state=inside, ladder_rung=12h, ladder_stop_pct=2.49263, pat_4h=none, pat_1d=three_down, intraday=trend_down, vol_regime=low, session=london, funding=low.
Disagreements: none.

## 2024-05-17 20:59 UTC close (t = 1249739), checked side: long

- Price 66855.1. Last closed daily: O 66175.4 H 66800.0 L 64567.0 C 65217.7 (red, range 2233.0). Last closed 12h: O 65217.7 H 66550.0 L 65061.2 C 66182.7 (green, range 1488.8).
- Last closed 8h: O 66350.5 H 67400.6 L 65773.8 C 67170.0 (green, range 1626.8). Last closed 4h: O 67169.9 H 67277.8 L 66158.4 C 67007.5 (red, range 1119.4); pattern bull_pin|inside (daily none).
- Partial daily so far: O 65217.7 H 67400.6 L 65061.2 C 66855.1 (green, range 2339.4).
- Nearest support below: 66800 (krown_zone, 0.0493879 ATR away, 4 layer(s) within 0.5 ATR). Nearest resistance above: 66874.9 (krown_zone, 0.0177474 ATR away, 2 layer(s)).
- Phase A markup / phase B distribution; intraday trend_up; 4h Bollinger inside (%b 0.78684), daily reenter_from_upper; vol regime high; session ny; funding neg.
- Stop ladder (long): daily rung 3.42248 %, 12h 2.68327 %, 8h 1.61738 % -> rung 8h (1.61738 %, cost 0.0865598 R).

Builder row: c_1d=(66175.4, 66800, 64567, 65217.7), c_12h=(65217.7, 66550, 65061.2, 66182.7), c_8h=(66350.5, 67400.6, 65773.8, 67170), c_4h=(67169.9, 67277.8, 66158.4, 67007.5), p_1d=(65217.7, 67400.6, 65061.2, 66855.1), near_price=66800, near_src=krown_zone, n_layers=4, phase_a=markup, bb_4h_state=inside, bb_1d_state=reenter_from_upper, ladder_rung=8h, ladder_stop_pct=1.61738, pat_4h=bull_pin|inside, pat_1d=none, intraday=trend_up, vol_regime=high, session=ny, funding=neg.
Disagreements: none.

**12 points, 0 field disagreements.**
