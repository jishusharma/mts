# Kurisko formula audit: FORMULAS.md vs code (2026-10-30)

Verdict: SOUND: the three independently hand-computed stochastic outputs and the toy-series long event match the implementation.

## Scope and method

Checked `MyTradingSys/backtest/layers/FORMULAS.md:566-578`, `MyTradingSys/backtest/layers/kurisko/stoch_core.py:13-41`, and `MyTradingSys/backtest/layers/kurisko/quad_rotation.py:33-105`. Ran the actual layer function with this command (from repository root):

```powershell
@' ... '@ | python -
```

The Python snippet imported `compute` from `MyTradingSys.backtest.layers.kurisko.quad_rotation`, built the 10 hourly bars below, and called `compute(..., bands=((2,1),(3,1),(4,1),(5,1)), lo=20, hi=80)`. These short bands are the event fixture bands used by FORMULAS 24.5, allowing the entire calculation on ten bars; production defaults are documented in 24.1.

Bars (index: high, low, close):

```text
0 (101,100,100)  1 (100,99,99)  2 (99,98,98)  3 (98,97,97)  4 (97,96,96)
5 (96,95,95)  6 (97,94.5,96.5)  7 (96,94,95)  8 (95,93,94)  9 (94,92,93)
```

All bars are consecutive hourly opens at `i * 3,600,000` ms. Formula calculations below are independent of the Python output.

## Formula inventory and comparisons

| Formula used | FORMULAS definition | Code location / evidence | Hand result vs executed code | Finding |
|---|---|---|---|---|
| Raw stochastic %K | `raw K = 100*(C[t]-LL)/(HH-LL)` over the trailing k highs/lows; flat HH=LL is NaN (24.1, `FORMULAS.md:570`) | `stoch_core.py:23-34`, especially `:30-33`: trailing max/min, then the stated quotient; equal range is skipped and remains NaN (`:31-32`) | At bar 6, k=2: HH=max(96,97)=97; LL=min(95,94.5)=94.5; close=96.5. Hand: `100*(96.5-94.5)/(97-94.5)=80`. Code `rows[6].values[0] = 80.0`. | MATCH |
| Raw %K plus D line (d=1) | The plotted line is SMA_d(raw %K), with d=1 in these fixture bands (24.1, `FORMULAS.md:570`) | `stoch_core.py:37-41`; `quad_rotation.py:60-67` routes the stochastic bands through this function | Bar 6, k=3,d=1: highs at 4..6 are 97,96,97 (HH=97); lows 96,95,94.5 (LL=94.5); close 96.5. Hand: `100*2/2.5=80`. Code `rows[6].values[1] = 80.0`. | MATCH |
| Raw %K plus D line (d=1) | Same 24.1 formula | Same code locations, `stoch_core.py:23-41`; `quad_rotation.py:60-67` | Bar 6, k=4,d=1: bars 3..6 HH=98, LL=94.5; hand: `100*(96.5-94.5)/(98-94.5)=200/3.5=57.142857143`. Code `rows[6].values[2] = 57.142857143`. | MATCH |
| Long rotation event | Episode begins with all four lines strictly <20; event at first later bar where fast rises, with prior episode state intact (24.4, `FORMULAS.md:576`; fixture `:578`) | `quad_rotation.py:71-93`, especially turn comparison `:76-79`, strict zone test `:84-90`; `:96-99` combines sides | At bar 4 four lines first become 0, so episode start index=4 (open 14,400,000; close 18,000,000). At bar 5 all remain 0; bar 6 fast=80>bar5 fast=0. Hand: long at bar 6 with episode start close 18,000,000. Code row 6: `side='long'`, `episode_start_t=18000000`; output line values `(80,80,57.142857143,44.444444444)`. | MATCH |

## Run output

Relevant rows printed by the command:

```text
4 (0.0, 0.0, 0.0, 0.0) None None
5 (0.0, 0.0, 0.0, 0.0) None None
6 (80.0, 80.0, 57.142857143, 44.444444444) long 18000000
```

The episode timestamp is the close time of bar 4 (`14,400,000 + 3,600,000`), consistent with FORMULAS 24.4. No formula evaluated as DIFFERENT or NOT_IN_DATA.

Follow-up cards created: none.
