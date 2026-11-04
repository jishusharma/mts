Regime mix: 360 weeks DEV (2017-08-07..2024-06-24, BTCUSDT): bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%) | baseline OURS proxy (weekly RSI14 <= 40, close below SMA200) on in 57 of 360 weeks; the Malkan weekly-AND-monthly bear gate fires 0 weeks, so every bear cell is empty.
Verdict: **NO DEFAULT CHANGES.** 0 of 7 Part A cells and 0 of 4 Part B timeframes earn a default; `d-bear-proxy-1104` (weekly RSI14 <= 40, below SMA200) stays, and entry at the signal-bar close with no fake-out filter stays. Part A: every cell is "no default: underpowered" (power gate BLOCK on every picked cell, or no setting reached n >= 30). Part B: 15m is the only powered timeframe and its picked filter FAILS on VALIDATION (fee-net CI entirely below 0); 1h, 4h, 1d are "no default: underpowered".

# bear_proxy_context_tuning (PRE_REG.md frozen first; DEV 2017-08..2024-06, VALIDATION 2024-07..2025-06 once, HOLDOUT never loaded; BTCUSDT+ETHUSDT SPOT; cost 0.14 %; trials 188 DEV, 11 VALIDATION, Holm m = 11)

All tuned values are OURS (RSI length, threshold, proxy timeframe, SMA filter, 60-day phase cut, ATR fake-out definition, the five filters). The SOURCED Malkan 40/60 band is unchanged.

## Part A: bear proxy setting per regime/phase cell (shorts from 15m bearish W12 divergence, fee-net %, 10-bar exit)

DEV = best of 24 settings by inside-gate net (n >= 30, >= 20 days). Baseline row is the current proxy (14, 40, 1w, SMA200 on) on the same cell.

| Cell | Picked setting (OURS) | DEV pick | DEV baseline | VALIDATION pick | Verdict |
|---|---|---|---|---|---|
| ALL | rsi21 <= 35, 1d, SMA on | n 238 / 88 d, net +0.003 [-0.281, +0.287], BLOCK | n 823, -0.166 [-0.272, -0.059] | n 46 / 17 d, -0.463 [-1.147, +0.221] | no default: underpowered |
| bull / fresh | none (no setting n >= 30) | - | 0 events | - | no default: underpowered |
| bull / mature | rsi14 <= 40, 1d, SMA off | n 60 / 27 d, -0.127 [-0.650, +0.397], BLOCK | 0 events | n 6, -0.113 [-0.327, +0.100] | no default: underpowered |
| range / fresh | rsi21 <= 45, 1w, SMA off | n 200 / 88 d, -0.140 [-0.419, +0.138], BLOCK | n 128, -0.230 [-0.632, +0.171] | n 77 / 39 d, -0.117 [-0.306, +0.072] | no default: underpowered |
| range / mature | rsi21 <= 35, 1d, SMA on | n 122 / 47 d, +0.250 [-0.017, +0.518], BLOCK | n 695, -0.154 [-0.255, -0.053] | n 5 / 3 d, -2.770 [-5.595, +0.054] | no default: underpowered |
| bear / fresh | none | - | 0 events | - | no default: underpowered |
| bear / mature | none | - | 0 events | - | no default: underpowered |

- 69 of 168 setting-cell rows reached n >= 30 and >= 20 days on DEV; 0 of them has a fee-net CI above 0. The only positive DEV points (range/mature +0.250, ALL +0.003) are the best of 24 tries on 47 and 88 days and span zero; both collapsed on VALIDATION (n 5 and n 46: too thin to read, point estimates -2.77 and -0.46).
- Gate's own hit rate (proxy-on Monday weeks followed by a lower close 4 weeks later, BTC+ETH pooled, DEV): baseline 0.376 over 109 gated weeks vs 0.423 over all 584 weeks. A bear proxy does NOT make the next month more likely to be lower than the average week; the picked ALL setting is 0.21 over 28 gated weeks vs base 0.42. In range/mature: baseline 0.394 vs 0.449. The signal "weekly RSI is low" marks weeks that tend to be followed by a bounce.
- Inside vs outside the baseline gate, shorts: ALL -0.166 vs -0.194 (difference +0.028, t 0.48); range/mature +0.022 (t 0.36); range/fresh -0.017 (t -0.08). The gate changes nothing measurable.
- Cells that are structurally empty: bear (the Malkan gate never fires) and bull/fresh (a weekly RSI <= 40 cannot co-occur with the weekly >= 60 of the bull band; the few bull/mature in-gate events come only from daily-RSI proxies with the SMA filter off, since bull requires a close above SMA200).

## Part B: fake-out filter per timeframe (both divergence kinds, W12, ungated, pooled kinds and symbols)

Fake-out = 1 ATR adverse before a 1 ATR favourable move within 10 bars (PRE_REG.md). DEV pick = highest fee-net mean per TF. Fake-out rate "before" = filter none, "after" = picked filter.

| TF | Picked filter (OURS) | DEV fake-out before -> after | DEV net before -> after [CI] (n, gate) | VALIDATION fake-out none -> pick | VALIDATION net none -> pick [CI] (n) | Verdict |
|---|---|---|---|---|---|---|
| 15m | volume > mean of prior 20 bars | 45.6 % -> 44.1 % | -0.139 -> -0.110 [-0.164, -0.055] (3943, PASS) | 49.2 % -> 48.6 % | -0.203 -> -0.183 [-0.312, -0.053] (642) | FAIL (Holm 0.063) |
| 1h | volume | 49.4 % -> 49.8 % | -0.244 -> -0.223 [-0.420, -0.025] (1097, BLOCK) | 52.0 % -> 53.3 % | -0.295 -> -0.384 [-0.831, +0.062] (169) | no default: underpowered |
| 4h | higher-TF RSI agreement (1d) | 46.6 % -> 51.2 % | -0.476 -> +0.203 [-0.611, +1.018] (170, BLOCK) | 39.0 % -> 18.5 % | +0.090 -> +0.747 [-0.283, +1.777] (27) | no default: underpowered |
| 1d | retest (N = 10) | 50.0 % -> 47.4 % | -1.123 -> -0.921 [-3.369, +1.527] (137, BLOCK) | 65.2 % -> 72.2 % | -3.213 -> -3.301 [-7.397, +0.796] (18) | no default: underpowered |

- 20 of 20 DEV filter cells have a negative or zero-spanning fee-net mean; none has a CI above 0. At 15m, where the power is real (1670-2463 days per filter), every filter, including none, loses after cost: none -0.139, confirm1 -0.198, htf_rsi -0.207, volume -0.110, retest -0.172. The best 15m filter (volume) only trims loss by 0.03 points and the fake-out rate from 45.6 to 44.1 percent. Fake-out rates sit at 44-54 percent in every cell, with or without a filter: the filters do not eliminate fake-outs.
- 4h htf_rsi (+0.203 DEV, +0.747 VALIDATION) is the only positive pick on both windows, but n is 170 and 27, both CIs span zero, and the cell is power-BLOCKED. It is a lead, not a default.
- Part B 15m VALIDATION: Holm 0.063 comes from the family of 11; the raw p is 0.006 and the sign is negative. The FAIL is "net CI below zero", not "unclear".

## Defaults written (`defaults.json`)

All 7 Part A cells: null (keep `d-bear-proxy-1104`). All 4 Part B timeframes: null (keep no filter). Nothing in this study may be cited as a tuned default.

## Honest limits

- Part A is capped by power in every cell: only threshold-45 settings pass the count gate (ALL cell), and the picked settings are mostly thin (RSI 21 <= 35 fires on 88 days). A bear-proxy study needs more symbols and more bear years, not another BTC/ETH re-cut; the 2017-2024 window has 57 proxy-on weeks.
- Phase is the OURS SMA200-side age, not `phase_tag` (its W1/H/R classes belong to tf_break events). Session tags are not used.
- The pick is the maximum of 24 (Part A) or 5 (Part B) DEV means, so DEV picks are optimistic by construction; that is why VALIDATION is the only number that counts.
- Spot not futures; 2022-2024 DEV overlaps the sibling long-window studies' DEV (same data, new question). Maintenance gaps in the archive are not filled; "10 bars" means bars present.
- The 4h/1d VALIDATION cells hold 18-100 trades: read only as direction.

Files: PRE_REG.md, A_count.csv, B_count.csv (counts and power gate, no returns), A_dev.csv, B_dev.csv, picks_dev.json, regime_mix_dev.txt, A_val.csv, B_val.csv, verdicts_val.json, defaults.json, study.py, test_wiring.py (18 tests; the fake-out ordering test failed on the pre-change code with adverse/favourable order swapped, 1 failed 17 passed, then 18 passed).
