# PRE_REG: Pizzino layer, BTC backtest (pz-4) - BLOCKED by prereg_gate.py, NOT FROZEN (2026-11-05)

Card `pz-4-backtest`. Rules = SPEC.md section 6 as coded in `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py`; harness `study.py`
(this folder), wiring tests `test_study_wiring.py` (7 tests; all fail at import on the tree without study.py, then 7 pass). The count pass
(`study.py --pass count`, trades and days only, no return) ran first; prereg_gate.py BLOCKS every cell (BLOCKED.md), so this file is NOT
frozen and no return pass ran. It records the design for the next attempt.

## Design (every parameter labelled; SOURCED = SPEC.md P01-P14, the rest OURS)

| Item | Value | Label |
|---|---|---|
| Data | BTCUSDT spot klines, F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/<tf>, loader end = window end | OURS (the repo's 7-year spot set) |
| Windows | DEV-stage = signal bars 2017-08-17..<2024-07-01 (PRE_DEV + DEV, backtest/splits.py); VALIDATION 2024-07-01..<2025-07-01 read ONCE for one chosen cell; HOLDOUT 2025-07-01+ never loaded | SOURCED splits.py |
| Setup | SPEC 6: retest `hold` of an up-broken PH(1)[-1] or the 50% line (N 2, tol 0.5 %, R 20), conf >= +2, close above mid; short mirrored | SPEC P11/P12 SOURCED, numbers OURS |
| Entry / stop / target | next open; stop PL(1)[-1] (short PH(1)[-1]); target nearest degree-1 pivot beyond entry, else 2R; skip if RR < 1.0; time stop open of bar entry+20 | P13/P14 SOURCED, numbers OURS |
| Fills | stop first when one bar touches both; gap through stop or target fills at the open; one position at a time; trades still open at the window end are dropped | OURS |
| Cost | 0.14 % round trip of entry, in R = 0.0014 x entry / risk | SOURCED research_kit.TAKER_RT_PCT |
| Family (10 cells) | C0 default; C1 conf +3; C2 conf +1; C3 n (2,5,13); C4 n (3,8,21); C5 RRmin 1.5; C6 TS 10; C7 bar-count filter B 5 (W 50, degree-3 T); C8 base TF 4h; C9 base TF 1h | SPEC section 9 variants; C8/C9 OURS, outside SPEC V-tf (added only to look for power) |
| Power sd | 1.5 R per trade, design bound from the geometry (loss -1 R, win +1 to +2 R), no return used | OURS |
| Survivor rule | n >= 30, net mean > 0, Holm p < 0.05 over m auto; VALIDATION same sign, raw p < 0.05 | OURS |
| Filter use ("as a filter on existing layers") | deferred to pz-5-confluence: no other layer has a daily BTC signal set with enough trades to gate (DECISION OURS) | OURS |

## Context
Regime: none, because the SPEC's own conf (nested swing states) is the trend gate; research_kit.regime_tag not applied (window mix in RESULT.md).
Phase: none, because tf_break classes are not part of SPEC.md.
Session: none, because the base TF is daily (1h/4h cells are not split by session).
Entry: SPEC.md section 6 retest-hold of a broken pivot or 50% line, fill at the next bar open.
