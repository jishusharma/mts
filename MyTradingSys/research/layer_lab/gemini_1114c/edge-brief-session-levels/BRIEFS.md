3 session-level pre-registration briefs

# Edge Hunt: Session-Level Pre-Registration Briefs (BTC & ETH)

## 1. Ledger & Cache Audit (No Outcomes Computed)

### 1.1 Source Ledgers Parsed (Full Row Counts)
- `MyTradingSys/research/VERDICTS.csv`: 176 lines total (1 header row at line 1 + 175 data rows at lines 2–176). Session-level / sweep / retest / opening-range rows present include `t087_session_levels_2026-10-09` (`MyTradingSys/research/VERDICTS.csv:51`), `eur_low_us_sweep_2026-10-14` (`MyTradingSys/research/VERDICTS.csv:31`), `eur_low_us_sweep_followups_2026-10-18` (`MyTradingSys/research/VERDICTS.csv:32-34`), `opr_weekly_low_round_sweep_2026-10-16` (`MyTradingSys/research/VERDICTS.csv:45-46`), `setup_alpha_beta_v2_2026-10` (`MyTradingSys/research/VERDICTS.csv:81-84`), `h3_ny_open_low_2026-10` (`MyTradingSys/research/VERDICTS.csv:125`), `rumers_2026-11-01` (`MyTradingSys/research/VERDICTS.csv:127-130`), and `edge_hunt_2026-11-09/eh-h3-first-touch-sweep` (`MyTradingSys/research/VERDICTS.csv:152`). None of the 3 setups below has a verdict row.
- `MyTradingSys/research/TRIAL_LEDGER.csv`: 123 lines total (1 header row at line 1 + 122 data rows at lines 2–123). Session/level trials present include `pit_levels_2026-10-16` (`MyTradingSys/research/TRIAL_LEDGER.csv:29-30`), `session_flow_context_2026-10-18` (`MyTradingSys/research/TRIAL_LEDGER.csv:31`), and `eur_low_us_sweep_followups_2026-10-18` (`MyTradingSys/research/TRIAL_LEDGER.csv:44-46`). None of the 3 setups below has a trial row.

### 1.2 Host Kline Cache Coverage (Listings Only)
- Reference rule (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:17`): SOURCED: "Read from F:/MTS/data_cache (or the host's cache path). Never committed to the repo. Repo is PUBLIC".
- `F:/MTS/data_cache`: absent on this host.
- Host cache `C:/Users/e-ngineers/MTS_data_cache` (OURS host disk listing):
  - `binance_spot_1d/BTCUSDT.json`: 3,376 bars, 2017-08-17 00:00 UTC .. 2026-11-13 00:00 UTC.
  - `binance_spot_1d/ETHUSDT.json`: 3,376 bars, 2017-08-17 00:00 UTC .. 2026-11-13 00:00 UTC.
  - `binance_spot_4h/BTCUSDT.json`: 20,239 bars, 2017-08-17 04:00 UTC .. 2026-11-13 20:00 UTC.
  - `binance_spot_4h/ETHUSDT.json`: 20,239 bars, 2017-08-17 04:00 UTC .. 2026-11-13 20:00 UTC.
- Secondary caches on host (OURS listing): `C:/MTS_data/dev_ext_2019_2021/klines` has 24 monthly `BTCUSDT-1m-2020-01.csv` .. `BTCUSDT-1m-2021-12.csv` files (BTC only, no ETH, no VAL >= 2024-01-01); `MyTradingSys/data/klines` has `BTCUSDT_5m.json`, `BTCUSDT_15m.json`, `BTCUSDT_1h.json` (BTC only). Therefore, all 3 multi-asset BTC+ETH pre-registrations below target the `binance_spot_4h` and `binance_spot_1d` caches covering full DEV and VAL.

---

## 2. Pre-Registration Briefs

### Brief 1: Asia Session High/Low (00:00–08:00 UTC) Sweep-Reclaim on 4H (BTC + ETH)
- **Gap / Verdict Status**: OURS (confirmed 0 rows in `VERDICTS.csv` and `TRIAL_LEDGER.csv`); SOURCED basis: "Weekly/monthly levels, Asia high/low as a standalone level: NOT_MEASURED." (`MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:65`).
- **Universe & Data**: OURS. `BTCUSDT` and `ETHUSDT` 4H spot klines from `C:/Users/e-ngineers/MTS_data_cache/binance_spot_4h` (pooled and per-asset).
- **Session Definition**: SOURCED: "Asia session (Tokyo/Sydney/HK window: 00:00–08:00 UTC [OURS default] or 19:00–00:00 EST / 00:00–05:00 UTC [ICT definition])." (`MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:9`). On 4H bars, Asia High = `max(high)` and Asia Low = `min(low)` across the `00:00` and `04:00` UTC bars of the same UTC day (OURS).
- **Hypothesis**: OURS (informed by SOURCED sweep-reclaim definition: "A session sweep measures a price probe that temporarily breaches a prior session extreme or prior day extreme by >= 1 tick, followed by a failure to hold acceptance and an immediate reclaim back inside the prior session boundary." `MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:13`, and "Price wicks beyond the Asian level, fails to sustain candle body closes outside" `MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:30`). When a subsequent same-day 4H bar (`08:00`, `12:00`, or `16:00` UTC) wicks beyond Asia High or Asia Low and closes strictly back inside the Asia range, entering in the reclaim direction yields positive 12 bp fee-net mean R over a random same-day 4H placebo.
- **Entry**: OURS. Market entry at the open of the next 4H bar `i+1` after bar `i` (`08:00`, `12:00`, or `16:00` UTC) completes:
  - Short: `high[i] > AsiaHigh` AND `close[i] < AsiaHigh` AND `close[i] > AsiaLow`.
  - Long: `low[i] < AsiaLow` AND `close[i] > AsiaLow` AND `close[i] < AsiaHigh`.
  - Maximum 1 trade per symbol per UTC day (first sweep-reclaim bar only).
- **Stop**: SOURCED floor formula: "max(0.6 x ATR, 0.5%)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:11`); OURS anchor: placed at `high[i] + 0.2 * ATR14[i]` (short) or `low[i] - 0.2 * ATR14[i]` (long), floored at `max(0.6 * ATR14[i], 0.005 * entry_price)` distance from entry.
- **Hold**: OURS. Fixed time cap of 6 x 4H bars (24 hours) OR first touch of the opposing Asia extreme (`AsiaLow` for shorts, `AsiaHigh` for longs) OR stop hit (conservative bar-order assumption: stop checked before target if both occur in the same bar).
- **Cost**: SOURCED: "Fee-net at 12 bp round trip (main row) AND a 6 bp row (sensitivity)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:10`).
- **Split**: SOURCED: "DEV <= 2023-12-31; VAL >= 2024-01-01" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:12`).
- **Kill Rule**: SOURCED: "PASS only if VAL fee-net 12 bp mean R > 0 with CI low > 0 AND beats the placebo band AND DEV sign agrees. Otherwise KILL with the number" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:21`); OURS minimum power gate: require `n >= 100` pooled events in VAL (and report underpowered if `< 100`).

---

### Brief 2: Crabel NR7 Contraction + London Open (08:00–12:00 UTC) Opening Range Breakout on 1D/4H (BTC + ETH)
- **Gap / Verdict Status**: OURS (confirmed 0 rows in `VERDICTS.csv` and `TRIAL_LEDGER.csv`); SOURCED open test: "Testing Toby Crabel's NR7 volatility contraction filter prior to London/NY session opening range breakouts" (`MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:87`).
- **Universe & Data**: OURS. `BTCUSDT` and `ETHUSDT` 1D + 4H spot klines from `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d` and `binance_spot_4h` (pooled and per-asset).
- **Hypothesis**: OURS (informed by SOURCED Crabel rules: "The Opening Range is the high and low established during a fixed initial time window" `MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:21` and "Narrow Range 7 (NR7: day's range is narrowest of the last 7 sessions)" `MyTradingSys/research/indicator_rulebooks/SESSION_LEVELS.md:24`). Following a completed UTC day whose range (`high - low`) is strictly the narrowest of the prior 7 completed UTC days (NR7), a 4H breakout close beyond the London-open 4H bar (`08:00–12:00 UTC`) captures directional expansion with positive 12 bp fee-net mean R over a non-NR7 / random-day 4H breakout placebo.
- **Entry**: OURS.
  - Causal daily filter on completed UTC day `d-1`: `range[d-1] < min(range[d-7 : d-1])` (strictly narrowest of the 7 days `[d-7 .. d-1]`).
  - Opening Range on day `d`: `ORH = high`, `ORL = low` of the `08:00–12:00 UTC` 4H bar on day `d`.
  - Trigger on subsequent same-day 4H bars (`12:00` or `16:00` UTC): enter at the open of bar `i+1` after the first closed 4H bar `i` with `close[i] > ORH` (Long) or `close[i] < ORL` (Short). Maximum 1 trade per symbol per day.
- **Stop**: SOURCED floor formula: "max(0.6 x ATR, 0.5%)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:11`); OURS anchor: placed at the midpoint `(ORH + ORL) / 2` or `max(0.6 * ATR14_4h[i], 0.005 * entry_price)` from entry, whichever is wider.
- **Hold**: OURS. Exit at the first of: `2.0R` profit target, stop hit, or 6 x 4H bars (24 hours) time stop.
- **Cost**: SOURCED: "Fee-net at 12 bp round trip (main row) AND a 6 bp row (sensitivity)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:10`).
- **Split**: SOURCED: "DEV <= 2023-12-31; VAL >= 2024-01-01" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:12`).
- **Kill Rule**: SOURCED: "PASS only if VAL fee-net 12 bp mean R > 0 with CI low > 0 AND beats the placebo band AND DEV sign agrees. Otherwise KILL with the number" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:21`); OURS minimum power gate: require `n >= 80` pooled events in VAL.

---

### Brief 3: Prior-Day High/Low (PDH/PDL) Accepted Breakout + 4H Retest Continuation (BTC + ETH)
- **Gap / Verdict Status**: OURS (confirmed 0 rows in `VERDICTS.csv` and `TRIAL_LEDGER.csv`; prior PDH/PDL studies tested failed-break fades only, e.g. `MyTradingSys/research/VERDICTS.csv:51,152`).
- **Universe & Data**: OURS. `BTCUSDT` and `ETHUSDT` 1D + 4H spot klines from `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d` and `binance_spot_4h` (pooled and per-asset).
- **Level Definition**: SOURCED: "level  = previous UTC day's high" (`MyTradingSys/backtest/layers/session_levels/session_levels.py:9`) and `PDL = previous UTC day's low` (mirror).
- **Hypothesis**: OURS. Unlike naive PDH/PDL fades (which fail fee-net on BTC), when a 4H bar first closes decisively beyond PDH or PDL (acceptance) and a subsequent 4H bar within the next 3 bars pulls back to retest that broken level and closes back in the breakout direction (polarity flip), entering in the breakout direction yields positive 12 bp fee-net mean R vs. a same-phase random 4H entry placebo.
- **Entry**: OURS.
  - Acceptance bar `b` (any 4H bar on UTC day `d`): first 4H bar of day `d` with `close[b] > PDH` (Long setup) or `close[b] < PDL` (Short setup).
  - Retest confirmation bar `r` in `[b+1 .. b+3]`:
    - Long: `low[r] <= PDH + 0.1 * ATR14_4h[r]` AND `close[r] > PDH` (touches/retests PDH from above and holds).
    - Short: `high[r] >= PDL - 0.1 * ATR14_4h[r]` AND `close[r] < PDL` (touches/retests PDL from below and holds).
  - Fill at open of bar `r+1`. Maximum 1 trade per symbol per UTC day.
- **Stop**: SOURCED floor formula: "max(0.6 x ATR, 0.5%)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:11`); OURS anchor: placed at `low[r] - 0.2 * ATR14_4h[r]` (Long) or `high[r] + 0.2 * ATR14_4h[r]` (Short), floored at `max(0.6 * ATR14_4h[r], 0.005 * entry_price)` from entry.
- **Hold**: OURS. Exit at the first of: `2.0R` profit target, stop hit, or 12 x 4H bars (48 hours) time stop.
- **Cost**: SOURCED: "Fee-net at 12 bp round trip (main row) AND a 6 bp row (sensitivity)" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:10`).
- **Split**: SOURCED: "DEV <= 2023-12-31; VAL >= 2024-01-01" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:12`).
- **Kill Rule**: SOURCED: "PASS only if VAL fee-net 12 bp mean R > 0 with CI low > 0 AND beats the placebo band AND DEV sign agrees. Otherwise KILL with the number" (`MyTradingSys/research/buy_zone_1114/NEXT5_TESTS.md:21`); OURS minimum power gate: require `n >= 100` pooled events in VAL.
