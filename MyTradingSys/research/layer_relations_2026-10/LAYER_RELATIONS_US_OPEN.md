# Layer relations by market phase, US Open first (BTCUSDT perpetual, DEV 2022-01-01..2024-06-30)

Card: layer-relations-concepts-us-open. Descriptive only: no edge claim, no trade advice, no trade rule. Operator intent (OPERATOR_DECISIONS.md:1369-1371, d-layer-relations-concepts-first): simple facts first, correlations and deviations understood as concepts before any application.

## 0. Labels, scope, what was and was not read

| Item | Value | Label |
|---|---|---|
| DEV bounds | 2022-01-01 to 2024-06-30 UTC, end exclusive 2024-07-01 | SOURCED `MyTradingSys/backtest/layers/krown/run_counts.py:29` (start, cites OPERATOR_DECISIONS.md:878), `MyTradingSys/backtest/layers/cryptocred/cc_htf_count.py:29` (end) |
| VALIDATION / HOLDOUT | not read. The script opens no file dated 2024-07-01 or later and asserts every kept timestamp is below DEV_END (`layer_relations_study.py`, `load()`). The last bar (opening 23:55 UTC on 2024-06-30) is dropped because its end-state snapshot would sit at 2024-07-01 00:00 | OURS |
| Price, taker volume | Binance USD-M BTCUSDT 5m klines, columns `open, close, volume, taker_buy_volume` | SOURCED data.binance.vision via `MyTradingSys/backtest/fetch_binance_archive.py:12,33` (`--interval 5m`); 262,656 bars loaded, 262,656 expected |
| OI, top-trader and global long/short ratios | Binance metrics, 5m: `sum_open_interest, count_toptrader_long_short_ratio (top-trader ACCOUNTS), sum_toptrader_long_short_ratio (top-trader POSITIONS), count_long_short_ratio (global accounts), sum_taker_long_short_vol_ratio` | SOURCED data.binance.vision via `fetch_binance_archive.py:14,36` (header row of every metrics CSV); 262,528 rows loaded over 912 daily files |
| Net delta | `2 * taker_buy_volume - volume` per bar; "net delta share" = that divided by volume. Binance perpetual only, not multi-exchange | OURS (computed from SOURCED columns) |
| Every number in the tables below | computed by `layer_relations_study.py` and printed in `results_tables.md` | OURS |
| Phase hours | Asia 00:00-07:00 UTC; London 07:00 UTC to 08:30 ET; PreOpen 08:30-09:30 ET; US Open 09:30-11:30 ET (13:30-15:30 UTC in EDT, 14:30-16:30 UTC in EST, handled with the real New York clock); US PM 11:30 ET to 21:00 UTC; Late 21:00-24:00 UTC. Weekdays (Mon-Fri UTC) only; US holidays are not removed | OURS |
| "Weekend control" | the US Open clock hours on Saturday and Sunday, when the cash market is shut: shows how much of a US Open result is the clock rather than the cash open | OURS |
| Statistic | Spearman rank correlation of changes inside a window (price = sum of 5m log returns; net delta share = window delta / window volume; OI = end vs start state; ratios = log end/start). `*` = outside the approximate 95% null band 1.96/sqrt(n-3). About 77 pair-by-phase cells are tested with no multiplicity correction, so about 4 stars are expected by chance; I treat only |rho| >= 0.30 as notable | OURS |
| Alignment | a metrics snapshot at `create_time t` belongs to the bar that opened at t-5 min. Checked: Spearman of net delta share vs ln(taker ratio) is +0.851 at that alignment and +0.209 / +0.045 one bar earlier / later; |price chg| vs |OI chg| is highest (+0.331) at the same alignment (`results_tables.md` C2). The same offset is assumed for the top-trader ratios and was not separately verifiable | OURS |
| Independent re-derivation | the US Open price vs net delta rho (+0.78, n=650) and price vs OI rho (+0.11) were recomputed with a separate plain-csv script (no pandas): +0.784 (650) and +0.114 (648). One window fewer for OI, same value to two decimals | OURS |
| Operator screenshots | Eagle_Eyes already read the shot store: `MyTradingSys/research/flow_layers_concepts_2026-10-28/README.md` (cited by line below). They are 2026-10 live shots, outside DEV, and are used only as a qualitative cross-check, never in a number | SOURCED |

## 1. Series that are missing for DEV (stated plainly, nothing substituted)

| Series asked for | Status in DEV |
|---|---|
| CoinGlass aggregated futures CVD (multi-exchange) | NOT_IN_DATA. CoinGlass exposes it only on live pages and a paid API (`research/coinglass_survey_2026-10-29/SURVEY.md`, family 6; pricing at the end of that file). No DEV file exists. The Binance-only taker net delta above is a different series and is not claimed to equal it |
| CoinGlass net longs / net shorts (new and open) | NOT_IN_DATA for DEV. Same source; units are also not shown on the pages (`flow_layers_concepts_2026-10-28/README.md:10`). Nothing was derived to stand in for it |
| Top-trader accounts and positions ratio | PARTLY MISSING. Blank in the archive for 2022-01 (97% blank), 2022-02, -03, -04, -07, -08, -09, -10, -11 (100% blank), 2022-05 (86% blank), 2022-06 (21% blank), 2022-12 (44% blank); complete from 2023-01. So top-trader rows use 422 of 650 weekday windows (`results_tables.md` C1, C3) |
| Global accounts ratio | missing only in 2022-01 (60% blank); 637 of 650 windows used |
| Open interest | complete (about 99-100% every month; zero values treated as holes) |
| Binance CVD at 1m or a tick-level CVD | not built; 5m bars only |

## 2. What each phase looks like (T6)

| Phase | Windows | Median abs price move (bp) | Median abs net delta share | Median abs OI change (bp) | Mean signed OI change (bp) | Share of windows with OI up |
|---|---|---|---|---|---|---|
| Asia | 650 | 55 | 0.025 | 112 | +47 | 63% |
| London | 650 | 52 | 0.023 | 122 | +112 | 76% |
| PreOpen | 650 | 28 | 0.044 | 46 | +23 | 67% |
| US Open | 650 | 58 | 0.030 | 85 | +6 | 51% |
| US PM | 650 | 67 | 0.024 | 146 | -111 | 29% |
| Late | 650 | 36 | 0.035 | 72 | -63 | 32% |

All OURS. OI drifts up in Asia and London and down in the US afternoon and late hours; the US Open window is the balanced one (51% up).

## 3. Co-movement per phase (T1; Spearman rho of window changes, n windows; * outside null band)

| Pair | Asia | London | PreOpen | **US Open** | US PM | Late | US Open clock on weekends |
|---|---|---|---|---|---|---|---|
| price vs net delta share | +0.73* (650) | +0.77* (650) | +0.74* (650) | **+0.78*** (650) | +0.78* (650) | +0.68* (650) | +0.70* (262) |
| price vs OI | +0.07 (650) | +0.18* (650) | +0.08* (649) | **+0.11*** (649) | +0.11* (648) | -0.03 (648) | +0.16* (262) |
| net delta share vs OI | +0.09* | +0.12* | +0.03 | **+0.14*** (649) | +0.12* | -0.01 | +0.13* (262) |
| price vs top-trader ACCOUNTS ratio | -0.60* (422) | -0.67* (423) | -0.41* (421) | **-0.74*** (422) | -0.73* (423) | -0.32* (422) | -0.49* (171) |
| price vs top-trader POSITIONS ratio | -0.17* | -0.14* | -0.14* | **-0.37*** (422) | -0.11* | -0.10* | -0.01 (171) |
| price vs global ACCOUNTS ratio | -0.36* (637) | -0.48* (638) | -0.18* (637) | **-0.54*** (637) | -0.57* (637) | -0.03 (637) | -0.15* (256) |
| net delta share vs top-trader POSITIONS ratio | -0.00 | +0.03 | +0.01 | **-0.16*** (422) | +0.02 | +0.05 | +0.10 (171) |
| OI vs top-trader ACCOUNTS ratio | -0.07 | -0.31* | -0.16* | **-0.23*** (422) | -0.20* | -0.19* | -0.31* (171) |
| OI vs top-trader POSITIONS ratio | -0.03 | -0.18* | -0.20* | **-0.13*** (422) | -0.11* | -0.17* | -0.06 (171) |
| top ACCOUNTS vs top POSITIONS ratio | +0.25* | +0.06 | -0.04 | **+0.26*** (422) | +0.04 | -0.19* | -0.13 (171) |

Full 11-row table and the 5m-bar version (T2) are in `results_tables.md`. At 5m bars the same pairs shrink: price vs net delta share +0.76 (n=15,584) at the US Open, price vs OI +0.03, price vs top-trader accounts ratio -0.10, price vs top-trader positions ratio +0.01. The big ratio-vs-price relations exist over a window, not bar by bar.

## 4. Divergences per phase (T3, T3b; weekday windows; sign of the two window changes differs)

| Pair | Asia | London | PreOpen | **US Open** | US PM | Late | US Open clock on weekends |
|---|---|---|---|---|---|---|---|
| price vs net delta | 151/650 = 23% | 119/650 = 18% | 124/650 = 19% | **119/650 = 18%** | 133/650 = 20% | 160/650 = 25% | 52/262 = 20% |
| price vs OI | 306/650 = 47% | 304/650 = 47% | 312/649 = 48% | **305/649 = 47%** | 322/648 = 50% | 327/648 = 50% | 119/262 = 45% |
| price vs top ACCOUNTS ratio | 303/422 = 72% | 312/423 = 74% | 262/421 = 62% | **332/422 = 79%** | 317/423 = 75% | 265/422 = 63% | 114/171 = 67% |
| price vs top POSITIONS ratio | 241/422 = 57% | 229/423 = 54% | 238/421 = 57% | **262/422 = 62%** | 223/423 = 53% | 214/422 = 51% | 79/171 = 46% |
| top ACCOUNTS vs top POSITIONS ratio | 170/422 = 40% | 201/423 = 48% | 208/421 = 49% | **176/422 = 42%** | 220/423 = 52% | 243/422 = 58% | 101/171 = 59% |

Price and OI four states (counts of windows):

| Phase | n | price up, OI up | price up, OI down | price down, OI up | price down, OI down |
|---|---|---|---|---|---|
| Asia | 650 | 213 | 107 | 199 | 131 |
| London | 650 | 267 | 78 | 226 | 79 |
| PreOpen | 649 | 218 | 98 | 214 | 119 |
| **US Open** | 649 | 165 | 136 | 169 | 179 |
| US PM | 648 | 103 | 236 | 86 | 223 |
| Late | 648 | 119 | 241 | 86 | 202 |
| US Open clock, weekend | 262 | 79 | 54 | 65 | 64 |

## 5. Lead-lag (T4, T7, T8; OURS)

Lead-lag at 5m bars inside a phase window, lags -12..+12 bars (+-60 min), k>0 = first series leads:

| x -> y | US Open: rho at k=0 | US Open: peak (lag, rho) | n bars | Other phases |
|---|---|---|---|---|
| net delta share -> price | +0.76 | k=0, +0.76 | 15,584 | peak at k=0 in all six phases (+0.72..+0.76) |
| net delta share -> OI | +0.03 | k=0, +0.03 | 15,547 | k=0, +0.03..+0.04 (PreOpen peak -0.06 at k=+11, not read as a lead) |
| price -> OI | +0.03 | k=0, +0.03 | 15,563 | k=0, +0.03..+0.04 everywhere |
| net delta share -> top POSITIONS ratio | +0.10 | k=0, +0.10 | 10,099 | k=0, +0.09..+0.14 everywhere |
| price -> top POSITIONS ratio | +0.01 | k=+1, -0.08 | 10,115 | k=+1, -0.06..-0.09 in London, PreOpen, US PM, Late; Asia k=0 +0.07 |
| price -> top ACCOUNTS ratio | -0.10 | **k=+2, -0.22** | 10,115 | PreOpen k=+2 -0.13; US PM k=+2 -0.14; London k=+5 -0.11; Late k=+5 -0.07; Asia k=+1 +0.11 |
| OI -> top POSITIONS ratio | -0.14 | k=0, -0.14 | 10,115 | k=0, -0.09..-0.14 everywhere |

Reading: delta, price and OI move together inside the same 5m bar with no visible lead at this resolution. The one lag larger than the k=0 value by the 0.05 rule is price -> top-trader ACCOUNTS ratio at the US Open (-0.22 at +10 min against -0.10 at 0); it may be real or may be the snapshot timing of that ratio, which the alignment test could not check.

Carry-over between adjacent phases, same day (T7, n=650, ratio rows n=421-422): price change -0.06..+0.07 (negligible in all five hand-overs); OI change +0.01..+0.06; net delta share Asia to London +0.10*, US Open to US PM +0.13*, US PM to Late +0.11*; top-trader ACCOUNTS ratio change +0.24*, +0.15*, +0.20*, +0.24*, +0.29* across the five hand-overs; top POSITIONS ratio -0.11..-0.01. PreOpen state against the US Open window (T8): all eight pairs |rho| <= 0.07.

## 6. Stability of the US Open numbers by half-year (T5, n about 130 windows each)

| Pair | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 |
|---|---|---|---|---|---|
| price vs net delta share | +0.85 | +0.75 | +0.88 | +0.76 | +0.74 |
| price vs OI | +0.02 | +0.06 | +0.26 | +0.12 | +0.13 |
| price vs top POSITIONS ratio | n/a (missing) | n/a (missing) | -0.25 | -0.32 | -0.49 |
| OI vs top POSITIONS ratio | n/a | n/a | -0.11 | -0.23 | -0.16 |

Net delta vs price is stable; price vs OI is near zero in 2022 and +0.12..+0.26 later; the top-positions relation strengthens across the three half-years it exists, so it is not a stable number from this sample.

## 7. Observed facts (plain)

1. Taker net delta and price over a 2-hour window agree in sign in 82% of US Open windows (531 of 650; rho +0.78) and in 75-82% of every other phase; the weekend clock gives 80% (rho +0.70). The disagreeing 18-25% are the divergence cases. (T1, T3)
2. OI direction does not track price or delta over the same window (rho +0.11 US Open, +0.03 per 5m bar); it follows the clock: up in 76% of London windows, up in 29% of US PM windows (mean +112 bp vs -111 bp). In the US Open window price/OI states are an almost even four-way split (165, 136, 169, 179). (T3b, T6)
3. The top-trader ACCOUNTS long/short ratio moves against price over a window: rho -0.74 at the US Open (n=422), -0.73 US PM, -0.67 London, -0.32 Late; its sign differs from price in 79% of US Open windows (332/422). It is present on weekends too (-0.49, n=171). Per 5m bar it is only -0.10, so it is a slow, accumulating response. (T1, T2, T3)
4. The top-trader POSITIONS ratio is much weaker against price (-0.37 at the US Open, about -0.1 elsewhere, -0.01 on weekends), and its sign against net delta flips with horizon at the US Open: +0.10 per 5m bar (n=10,099), -0.16 per 2-hour window (n=422). (T1, T2)
5. Accounts and positions ratios agree with each other only weakly: +0.26 at the US Open and Asia, near 0 in London and US PM, -0.19 at Late. They differ in sign in 42% of US Open windows and 58% of Late windows. (T1, T3)
6. Nothing carries over from PreOpen into the US Open for price, delta, OI or the ratios (|rho| <= 0.07, n=421-650), but the top ACCOUNTS ratio change persists from one phase to the next (+0.15..+0.29). (T7, T8)
7. Cross-check with the live screenshots (qualitative): flow_layers_concepts F3 sees CVD and net delta disagree on one bar (`README.md:39`; not testable here because CoinGlass CVD is NOT_IN_DATA), F4 sees OI step up with price falling (`:40`), F7 sees top-trader ratios not stepping down in a 300-point drop (`:43`), and concept 3 says top-trader ratios move slowly and opposite to the hours-long swing (`:80`). The DEV window table gives the same sign and the same "slow" character (window rho -0.74, 5m rho -0.10); it does not test the 1m behaviour.

## 8. Candidate concepts (one sentence each; for later testing, not claims of an edge)

1. Taker net delta is mostly a restatement of price over a window (rho 0.68-0.78 in every phase), so a price/delta divergence is the minority case (18-25% of windows) and only that minority carries information the price does not.
2. Open interest is a time-of-day drift (builds in Asia and London, bleeds in the US afternoon) more than a price-linked signal, so an OI change needs its phase baseline before it is read as new positions or closing.
3. The US Open window is the phase where OI is least biased (51% up, mean +6 bp), which is also where price/OI states split most evenly, so the same OI move there means more than the same move in London.
4. The top-trader accounts ratio behaves as a slow contrarian gauge of price over hours (rho -0.74 at the US Open, 79% opposite sign), building up across phases rather than reacting inside a 5-minute bar.
5. The top-trader positions ratio and the accounts ratio are two different measures that agree little (rho +0.26 at best), so "top traders" must name which one is meant.
6. The relation between net delta and the top-trader positions ratio changes sign with horizon (+0.10 per 5m, -0.16 per 2h at the US Open), so a flow-versus-positioning statement needs its time scale attached.
7. A PreOpen reading tells nothing about the US Open window in this sample (|rho| <= 0.07), so the US Open behaves as its own phase rather than a continuation of the hour before.
8. Part of the US Open pattern is the clock, not the cash market: weekend windows at the same hours show similar price/delta (0.70) and top-accounts (-0.49) relations, while the top-positions relation vanishes (-0.01).

## 9. Limits (read before using any row)

- Binance perpetual only. CoinGlass multi-exchange CVD and net longs/shorts are not in DEV data (section 1); the screenshot comparison is qualitative.
- Top-trader rows start effectively in 2023 (n=422 of 650); the 2022 half-years are n/a. Every top-trader statement comes from 2022-06, 2022-12 and 2023-01 onward only.
- Snapshot alignment was verified for OI and the taker ratio, assumed for the top-trader and global ratios. A lead of one bar is within that uncertainty.
- Windows are 2-hour (US Open) to 7-hour (Asia) blocks; days are not independent of volatility regimes. No multiplicity correction; stars are indicative.
- US holidays are not removed from weekday windows. Funding settlement times (00:00, 08:00, 16:00 UTC) fall inside the Asia window, the London window and, in EST, the US Open window (16:00 UTC); not isolated.
- Whether any of this is tradable after fees is not asked and not answered.

## 10. Reproduce

```
python MyTradingSys/backtest/fetch_binance_archive.py --start 2022-01-01 --end 2024-06-30 --datasets klines --interval 5m
python MyTradingSys/backtest/fetch_binance_archive.py --start 2022-01-01 --end 2024-06-30 --datasets metrics
python MyTradingSys/research/layer_relations_2026-10/layer_relations_study.py --out MyTradingSys/research/layer_relations_2026-10/results_tables.md
```

The data lands in `Dumps/backtest/raw/` (gitignored, public market data). The script output is `results_tables.md` (aggregate statistics only).
