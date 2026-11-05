# RESULT: Pizzino layer BTC backtest (pz-4), 2026-11-05 - BLOCKED at the power gate, counts only

**Regime mix:** 360 weeks: bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%), BTCUSDT spot 2017-08..2024-06 (same window and data as research/bear_proxy_context_tuning_2026-11-04/regime_mix_dev.txt; not recomputed here).

**Result:** the SPEC.md section 6 setup fires 3 times in 7 years of BTC daily bars (2017-08..2024-06). No cell reaches the power gate (largest n 20 on 1h vs 527+ needed), so no return was computed, VALIDATION and HOLDOUT were not read, and there is no keep or drop verdict. Mean R: NOT RUN (gate BLOCK). Fee-net: N/A.

## Per cell (DEV-stage 2017-08-17..2024-06-30, `study.py --pass count`, counts.txt)

| Cell | Change from default | TF | n trades | days | median stop % | mean R | fee-net | split |
|---|---|---|---|---|---|---|---|---|
| C0 | default (SPEC 6) | 1d | 3 | 3 | 6.11 | NOT RUN | N/A | DEV-stage only |
| C1 | conf +3 | 1d | 3 | 3 | 6.11 | NOT RUN | N/A | DEV-stage only |
| C2 | conf +1 | 1d | 3 | 3 | 6.11 | NOT RUN | N/A | DEV-stage only |
| C3 | n (2,5,13) | 1d | 5 | 5 | 31.81 | NOT RUN | N/A | DEV-stage only |
| C4 | n (3,8,21) | 1d | 1 | 1 | 36.94 | NOT RUN | N/A | DEV-stage only |
| C5 | RRmin 1.5 | 1d | 3 | 3 | 6.11 | NOT RUN | N/A | DEV-stage only |
| C6 | TS 10 | 1d | 3 | 3 | 6.11 | NOT RUN | N/A | DEV-stage only |
| C7 | Jason 3-bar count within 5 bars | 1d | 0 | 0 | - | NOT RUN | N/A | DEV-stage only |
| C8 | base TF 4h (OURS, outside SPEC) | 4h | 9 | 9 | 0.52 | NOT RUN | N/A | DEV-stage only |
| C9 | base TF 1h (OURS, outside SPEC) | 1h | 21 | 20 | 2.07 | NOT RUN | N/A | DEV-stage only |

## Why so few (funnel.txt, default cell, 2510 daily bars, counts only)

- The trend states are common: conf >= +2 on 752 days, <= -2 on 450 days.
- The bottleneck is the retest: a first touch of a just-broken level within 20 bars happens 11 times for PH(1) long, 6 times for PL(1) short, 25 and 27 times for the 50% line. Of those, 23 pass hold + conf + half, and the RR >= 1 target check plus one-position-at-a-time leave 3. Changing conf (C1, C2) changes nothing: all 3 trades are already conf +-3.
- The 4h cell has a 0.52 % median stop, so cost alone is 0.27 R per trade.

## Independent recount

`recount.py` (pivots via pz.pivots_known recomputed every bar, its own entry and exit loop, not study.py) prints `recount C0_default 1d DEV-stage n 3` (recount.txt) = C0 n 3 above. Mean R is not recounted because it was not computed.

## Decisions (OURS, taken without operator input)

- Gate BLOCK on every cell: followed the gate (BLOCKED.md), no return pass. Running returns on n 1-21 would add trials that cannot show anything.
- HOLDOUT: not read (no chosen cell; backtest/splits.py keeps it sealed).
- Filter on existing layers: deferred to pz-5-confluence-and-live; the encoded setup is too rare to gate other layers, and its conf state (common, 1202 days at |conf| >= 2) is the part worth testing as a filter there.
- Base TF 4h and 1h cells added outside SPEC V-tf, labelled OURS, only to look for power.
- Export id `pz-4-backtest-2026-11-05` (file `sim_desk/results/pz-4-backtest-2026-11-05.json`, not the card's `pz-4-backtest.json`): the desk tests require a dated id on new rows.

## Next

The powered question is the conf state as a context filter (pz-5), or the setup pooled across many symbols. Single-symbol BTC cannot power the SPEC 6 setup at any TF tried.
