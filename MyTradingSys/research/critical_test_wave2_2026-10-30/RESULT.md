# Critical test wave 2: items 6-8 (venue gap, funding census, trial budget)

Card `critical-test-wave-2-critical-test-plan-`, 2026-11-05, Opus author (one model). Plan: `system/CRITICAL_TEST_PLAN.md` wave 2.
Scripts in this folder rerun every number: `item6_venue_gap.py` (result `item6_result.json`), `item7_funding_census.py`
(`item7_census.tsv`), `item8_minbtl.py` (`item8_minbtl.tsv`). DEV window only (item 6 loader refuses bars at or after 2024-07-01).
Regime mix: item 6 is one month, 2024-05 (BTC about 56.5k-71.9k): range 100%, bull 0%, bear 0% by eye, no regime gate applied.

## Item 6: Binance USD-M BTCUSDT perp vs Deribit BTC-PERPETUAL, 2024-05, 44,640 1m bars (all aligned)

Lag check: median |close gap| is lowest at lag 0 (6.11 bps; lag -1 6.72, +1 6.59), so the timestamps line up.

| field (Deribit minus Binance) | mean bps | abs p50 | abs p95 | abs p99 | abs max |
|---|---|---|---|---|---|
| open | +0.98 | 6.10 | 13.38 | 16.01 | 26.8 |
| close | +0.99 | 6.11 | 13.56 | 16.29 | 26.8 |
| high | +0.11 | 5.82 | 13.73 | 16.61 | 71.9 |
| low | +1.87 | 6.37 | 13.46 | 15.98 | 83.6 |
| bar range (USD) | -11.4 USD | 11.5 USD | 28.3 USD | 39.6 USD | 542.8 USD |

- 66.4% of bars have a high or low more than 5 bps apart; 1m return correlation 0.958; 8.7% of bars move in opposite directions.
- Funding over the month: Binance 0.637% (93 settlements, 8h), Deribit 0.607% (744 hourly interest_1h records): 0.03 pp apart.
- Layer stand-in (`rsi_levels`: 1h RSI(14) crossing 30/70, OURS parameters; entry at the next 1m open = one-bar fill delay; stop 1%,
  target 2R, 16 h cap; Deribit fees from `fees.py` on both runs; each venue's own funding; `bt_engine.simulate_trade`):
  events 52 Binance / 55 Deribit, 49 shared; 48 paired trades differ by mean +0.001 R, max |0.049| R;
  month sums +3.84 R (Binance) vs +0.59 R (Deribit). The 3.25 R gap comes from the 3-6 events only one venue fires, not from fills.
- Verdict FINDING (MED): Binance prices are a fair stand-in for fills at 1% stops (per-trade gap at most 0.05 R), but the
  level gap (p50 6 bps, p95 13.6 bps) is the size of the whole 10 bps taker round trip, so any stop or target under about
  0.15% and any wick-touch rule (66% of bars' wicks differ by more than 5 bps) is not transferable; signal sets differ by 6-12%.
  Card filed: `venue-gap-tight-stop-rerun-on-deribit`.

## Item 7: funding census of trade-simulating scripts (tracked .py, tests excluded)

| class | n | meaning |
|---|---|---|
| CHARGES | 9 | calls a funding charge (funding_paid / funding_cost_pct / trade_costs.net_return / bt_engine with records) |
| LIB | 5 | defines the charge: bt_data, bt_engine, trade_costs, fabio/v3/costs, layer_lab engine |
| MENTIONS | 21 | says funding (feature or filter) but charges none: fee-only lower bound |
| NONE | 69 | no funding at all: fee-only lower bound |

- Charging: cryptocred (cc_bt_adapter, run_cc_setups), rsi/run_rsi_backtest, run_t055, chart_read_g5 common, gross_effect_screen,
  oi_divergence_v2, two DSA audit canaries. Every other result (90 of 99 non-library scripts) is a fee-only lower bound.
- FINDING (MED): `fabio/v3/costs.funding_r` is tested (test_costs_fill.py) but no runner calls it, so every FABIO-V3 number is
  fee-only though the module says "the caller subtracts it". Card filed: `fabio-v3-funding-r-never-called`.
- Hold time was not parsed: an intraday script that never crosses 00/08/16 UTC owes no funding; the label stands until shown.

## Item 8: trials vs Minimum Backtest Length (Bailey et al. 2014)

MinBTL(N) = (E[max of N] / SR)^2 years, E[max] = (1-g) Z(1-1/N) + g Z(1-1/(N e)). Independent check: N 7 -> 1.92 y, 8 -> 2.13,
9 -> 2.31, 10 -> 2.48. Budget on the 2.5 y DEV window (splits.py) at Sharpe 1: **10 configs** (the plan's "about 7" used 2.25 y: 8).

| verdict row | trials | Sharpe a best-of-N needs (annual) | over budget |
|---|---|---|---|
| RSI-DEEP-PRESTUDIES | 662 | 1.98 | yes |
| VOLUME | 553 | 1.95 | yes |
| VOL-V1 / VOL-V2 | 216 / 96 | 1.76 / 1.59 | yes |
| Q33 | 186 | 1.73 | yes |
| L1-D3 | 80 | 1.55 | yes |
| BIGTRADE-EXIT | 54 | 1.46 | yes |
| TOM-VP-PHASE2 | 48 | 1.43 | yes |
| RSI-DIV-MTF | 32 | 1.33 | yes |
| PITCHFORK-4H-VP | 3 | 0.54 | no |

- 15 of 41 rows record a trial count; 9 of the 15 are over the budget; 26 rows do not record one (full list `item8_minbtl.tsv`).
- Standing passes: 1, L1-D3 1h support (PBO 0.030). It is GROSS: OOS +0.043%/trade minus the 0.10% Deribit taker round trip
  = -0.057%/trade fee-net, so it is not a pass and no DSR is owed. Both pitchfork passes were already withdrawn 2026-11-03.
- Verdict UNTESTABLE for the 26 rows without a trial count; PASS for "no standing pass lacks a DSR" (0 owed).
  Card filed: `layer-map-trials-field` (add `trials` to every layer_map row so this check runs at load).

## Review

Single model (Opus). Second-model blind read: card `[GEMINI] blind read of critical_test_wave2 RESULT.md`.
