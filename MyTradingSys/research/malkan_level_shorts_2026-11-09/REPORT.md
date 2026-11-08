# REPORT: Malkan level-short stack, BTCUSDT 4h, PRE_DEV + DEV 2017-08 .. 2024-06 (card malkan-level-short-4h-count-1109)

**Result: the stack fires 17 times in 6.9 years (primary arm); 11 of 17 reach >= 1R before the stop; fee-net +0.245 R/trade at a 1R exit (CI +-0.47: includes 0). N = 17 is underpowered, not "no edge"; the 8-arm trial count and the layer ladder (post-hoc gate) mean this is a count, not an edge. No testnet card (kill rule needs N >= 30).**

Regime mix: bull 45.7% / bear 38.3% / range 8.1% of 4h bars (daily close vs 200d SMA +-5%), 7.9% warm-up (NOT_IN_DATA). Split: PRE_DEV 2017-08..2021-12 and DEV 2022-01..2024-06 read; VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07.. **sealed, not read** (PRE_REG.md; the card's "2017-2026" is cut at the gate, DECISION OURS, conservative). The 2026 klines are a fixture for the operator-point recall check only (logged in research/holdout_reads.csv; no performance computed there).

Files: layer `backtest/layers/rsi/malkan_level_short.py`, tests `test_malkan_level_short.py` (26, fail-first), `PRE_REG.md`, `run_count.py`, `tables.md` (every arm, regime, year, 1R and 2R), `fetch_klines.py` (public Binance spot klines via data-api.binance.vision; the 4h/1d/1w CSVs stay out of git, only the small 2026 fixture is committed).

## The 5 operator points (recall check on his 2026 chart; 2026 is outside DEV, so recall only)

| Point | Fired? | Detail |
|---|---|---|
| C1 (08-28) | YES, layers 1-4, on all 8 arms | sweep of the 08-25 zone, entry 79,660 = his 79,660; layer 5 (HTF fail) NOT met (as READING.md: layer 5 is seen in V2/C3 only) so it is not a full firing |
| C3 (10-21/22) | YES, all 5 layers, on all 8 arms | sweep of the 10-12 high, entry 82,925 = his 82,925 (10-22 04) |
| C2 (09-03/04) | MISS, layer 2 | a level trade with no divergence and no sweep; the stack needs structure by design |
| V1 (09-23) | MISS, layer 1 | his red line 86,807 vs the nearest confirmed 5/5 pivot zone 87,396 (zone floor 87,177); the setup bar high 86,975 never reaches it: the pivot proxy for a hand-drawn line |
| V2 (10-06) | MISS, layer 1 | setup high 86,800 under the zone floor 87,002 of the 87,220 pivot; the 86,999 pivot confirms 10-05 20, after the setup; his 15-bar divergence is also outside the 3-10 window |

So 2 of 5 reproduce exactly (entry prices to the dollar), 3 miss for named reasons. 2 of 5 on a proxy level is the honest recall; level definition = OURS and unconfirmed by the operator (PRE_REG 0g).

## Arms (window 3-10 vs swing-to-swing; close vs wick; two trigger forms; sweep OR'd in every arm)

Ladder = chains at layers 1-3, then with WaveTrend (+L4), then with the HTF gate (+L5 = firings). Hit >=1R = reached 1R before the stop, among non-overlapping firings (all firings are non-overlapping here). Fee 0.04% per side on entry and exit notional, stop-first on a same-bar tie, time exit at 60 bars.

| arm (div / basis / trigger) | L1-3 chains | +L4 | +L5 = firings | too tight | non-overlap trades | hit >=1R | target 1R hit | net R/trade 1R exit | CI | net R/trade 2R exit | CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window 3-10 / close / cross | 163 | 76 | 17 | 0 | 17 | 64.7% | 64.7% | +0.245 | 0.47 | +0.081 | 0.69 |
| window 3-10 / close / cross+RSI<60 | 94 | 36 | 10 | 0 | 10 | 50.0% | 50.0% | -0.051 | 0.66 | -0.328 | 0.79 |
| window 3-10 / wick / cross | 168 | 75 | 15 | 0 | 15 | 66.7% | 66.7% | +0.285 | 0.50 | +0.034 | 0.73 |
| window 3-10 / wick / cross+RSI<60 | 100 | 37 | 9 | 0 | 9 | 55.6% | 55.6% | +0.061 | 0.70 | -0.247 | 0.86 |
| swing-swing / close / cross | 163 | 76 | 16 | 0 | 16 | 62.5% | 62.5% | +0.201 | 0.49 | -0.035 | 0.70 |
| swing-swing / close / cross+RSI<60 | 94 | 37 | 10 | 0 | 10 | 50.0% | 50.0% | -0.051 | 0.66 | -0.328 | 0.79 |
| swing-swing / wick / cross | 159 | 71 | 14 | 0 | 14 | 64.3% | 64.3% | +0.237 | 0.53 | +0.110 | 0.77 |
| swing-swing / wick / cross+RSI<60 | 96 | 36 | 9 | 0 | 9 | 55.6% | 55.6% | +0.061 | 0.70 | -0.247 | 0.86 |

- Window 3-10 vs swing-to-swing: 17 vs 16 firings (close basis), 15 vs 14 (wick): the window question moves almost nothing, because 12 of 17 firings are sweeps (layer 2 is mostly the sweep branch, not divergence).
- Close vs wick: 17 vs 15 (window), 16 vs 14 (swing). Wick basis fires slightly less and scores slightly higher net; the CI overlaps.
- Strict "RSI also < 60" trigger: 9-10 firings and net near 0 or negative. V1-type reads (RSI 76) are lost under it.
- All 8 arms are exploratory, trial count 8; none is selected.

## Primary arm detail (window 3-10 / close / cross)

Ladder (non-overlapping trades within each tier, 1R exit, fee-net 0.04%/side):

| tier | trades | hit >=1R | target 1R hit | net R/trade | CI |
|---|---|---|---|---|---|
| L1-3 | 145 | 43.4% | 43.4% | -0.145 | +-0.16 |
| L1-4 | 72 | 43.1% | 43.1% | -0.148 | +-0.23 |
| L1-5 (firings) | 17 | 64.7% | 64.7% | +0.245 | +-0.47 |

Firings by regime, 1R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 80.0% | +0.558 | +-0.53 |
| bear | 6 | 50.0% | 50.0% | -0.060 | +-0.88 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 1R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +0.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 66.7% | +0.295 | +-1.31 |
| 2022 | 3 | 66.7% | 66.7% | +0.284 | +-1.28 |
| 2023 | 6 | 50.0% | 50.0% | -0.053 | +-0.90 |
| 2024 | 3 | 100.0% | 100.0% | +0.942 | +-0.02 |

Firings by regime, 2R exit (non-overlapping):

| regime | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| bull | 10 | 80.0% | 40.0% | +0.280 | +-0.93 |
| bear | 6 | 50.0% | 33.3% | -0.060 | +-1.25 |
| range | 1 | 0.0% | 0.0% | -1.059 | +- |
| warm-up | 0 | | | | |

Firings by year, 2R exit:

| year | trades | hit >=1R | target hit | net R/trade | CI |
|---|---|---|---|---|---|
| 2017 | 0 | | | | |
| 2018 | 0 | | | | |
| 2019 | 1 | 100.0% | 100.0% | +1.968 | +- |
| 2020 | 1 | 0.0% | 0.0% | -1.058 | +- |
| 2021 | 3 | 66.7% | 33.3% | -0.038 | +-1.96 |
| 2022 | 3 | 66.7% | 33.3% | -0.050 | +-1.95 |
| 2023 | 6 | 50.0% | 33.3% | +0.152 | +-1.20 |
| 2024 | 3 | 100.0% | 33.3% | -0.058 | +-1.94 |

Firings (all, overlapping allowed): 17; kind: 12 sweep / 5 div.

Reading: layers 1-4 alone (145 / 72 trades) lose money fee-net (-0.145 and -0.148 R); the HTF layer is what turns it positive, and that layer was added after the operator's reads (hindsight). Bull regime carries 10 of 17 firings. 2017-2018 has zero firings (WaveTrend/RSI warm-up and the HTF gate). Year cells hold 0-6 trades: no year is evidence.

## Verdict and next

- Count answered: 17 / 16 / 15 / 14 / 10 / 9 firings by arm over 6.9 years of 4h BTC; only 2 of the 5 operator points reproduce (C1, C3).
- Fee-net expectancy primary arm +0.245 R (1R exit), +0.081 R (2R exit); both CI cross 0. N < 30 on every arm: underpowered. Kill rule met on N, so NO testnet card is filed. The DEV stack stays unvalidated; one VALIDATION read would need a new PRE_REG naming ONE arm (candidate: the primary).
- No like-for-like null (same stop, random level touch) was run; item 9 of the readiness template remains open.
- Parameters: all OURS except the 3-10 window, the 60 RSI level and the 53/60 WaveTrend bands (SOURCED, quotes in PRE_REG.md and the module header).
