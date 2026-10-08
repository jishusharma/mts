# BTC candle patterns: operator rule (P0) and classical pattern scan (P1) - DEV pilot

Status: EXPLORATORY TRIAL. Nothing here adopts a rule. Session MTS-2026-10-03-2051Z-APP-ANA-btc-candle-patterns; P1 run 2026-10-07.

## 1. Question
(a) Does the operator's daily-level rule ("long the previous candle's daily open when price goes up past it, exit when the
current daily breaks the previous day close on a closing basis") have a net edge on BTCUSDT perp? (b) Do any of 18 classical
directional candle patterns, or three volatility-state candles, carry net-of-cost predictive content on 1d or 1h bars?

## 2. Pre-registration
PRE_REG_CANDLE_PILOT.md (frozen before any run; sections 1, 2, 4, 5, 6 unchanged after results). Code: pilot/run_p0.py,
pilot/run_p1.py, tests pilot/test_pilot.py (29) and pilot/test_p1.py (11). Raw outputs: P0_RESULTS.md, P1_RESULTS.md,
p0_results.json, p1_results.json. Trial ledger: TRIAL_REGISTRY.csv.

## 3. Data
Binance USDT-M BTCUSDT perp archive, UTC bars. DEV only: daily 2020-01-01..2024-06-30 (1643 bars, 0 gaps); hourly built from 1m
2022-01-01..2024-06-30 (21888 bars, 0 gaps, 0 dropped hours). Funding = archive 8h rates charged on settlements in (entry, exit].
VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07..) untouched; cdata.py refuses dates after DEV_END.
Costs: 14 bps round trip (5 bps fee + 2 bps slippage per side) plus realised funding.

## 4. P0 verdict (operator rule, DEV daily, slip 2 bps)
Triage rule (PRE_REG s5) needs N>=20, net mean >0 with 95% CI lower bound >0, p<0.10 (here: exposure-matched random null), textbook direction.

| variant | trades | net bps/trade [95% CI] | p vs random null | triage |
|---|---|---|---|---|
| P0a long, touch entry | 571 | -0.7 [-43, 43] | 0.789 | FAIL |
| P0c long, close-confirmed | 364 | -8.1 [-63, 45] | 0.888 | FAIL |
| P0s short mirror | 591 | -56.4 [-92, -20] | 0.976 | FAIL (loses significantly) |
| P0e no-level ablation | 797 | +4.8 [-31, 40] | 0.755 | FAIL |

Verdict: P0 fails triage on all four variants. Win rate 30-38%, median trade negative (-53 to -119 bps), profits come from a few large
winners. P0a total net log return -0.04 vs buy-and-hold +2.17 over the same window (it is in the market 78% of days). The level
condition adds nothing over the exit rule plus drift (P0e is not worse than P0a). P0a at slip 0 is +3.3 bps and at slip 5 is -6.7 bps:
the result is within cost noise either way. By year the sign flips (P0a 2020 +56, 2021 -27, 2022 -72, 2023 +34, 2024 +22 bps),
so there is no regime-stable edge. Shifting the day boundary (6 anchors, 2022-01..2024-06): net -8 to -28 bps/trade, none positive.
The rule's apparent mid-sized gross edge (21 bps) is equal to what a random exposure-matched null produces.

## 5. P1 results
Inference per timeframe: studentised White Reality Check (single-step max-T, circular block bootstrap block 10/24, 1000 resamples,
seed 12345) over the 54 pattern x horizon family; BH q-values over the same 54 (INSUFFICIENT-N entries count as p=1).
INSUFFICIENT-N: n<20 (1d), n<100 (1h). Full 108-row tables are in P1_RESULTS.md. Summary (net bps per trade at best horizon shown;
no row passes):

### 1d (18 of 54 trials INSUFFICIENT-N: hammer, hanging_man, inv_hammer, shooting_star, marubozu_up, marubozu_dn)
| pattern (expected sign) | n | h1 net | h3 net [CI] | h5 net | min RC p | triage |
|---|---|---|---|---|---|---|
| bull_engulf (+) | 164 | -26 | -47 [-134, 43] | +22 | 1.000 | FAIL |
| bear_engulf (-) | 140 | -71 | -96 [-177, -19] | -77 | 1.000 | FAIL |
| bull_harami (+) | 70 | -6 | +66 [-47, 184] | +103 | 0.994 | FAIL |
| bear_harami (-) | 65 | -52 | -3 [-142, 126] | -139 | 1.000 | FAIL |
| morning_star (+) | 44 | -8 | -15 [-178, 142] | -35 | 1.000 | FAIL |
| evening_star (-) | 44 | -60 | -32 [-194, 156] | +115 | 0.976 | FAIL |
| three_white_soldiers (+) | 105 | +23 | +169 [34, 311] | +222 [19, 452] | 0.264 | FAIL (RC) |
| three_black_crows (-) | 81 | -23 | +74 [-122, 279] | +42 | 0.933 | FAIL |
| piercing (+) | 48 | -61 | -27 [-183, 136] | -29 | 1.000 | FAIL |
| dark_cloud (-) | 65 | -0.5 | -16 [-133, 92] | -57 | 1.000 | FAIL |
| hikkake_bull (+) | 29 | +48 | +39 [-157, 233] | +8 | 0.983 | FAIL |
| hikkake_bear (-) | 31 | -102 | -251 [-478, -39] | -170 | 1.000 | FAIL |

Note on sign: for bearish patterns "net" is the short-side return, so negative means shorting after the pattern lost money.
Three white soldiers at h3/h5 is the only 1d row with a positive net CI (lower bound 34 and 19 bps) but its family-adjusted RC p
is 0.26/0.46 (n=105; BH q 0.993). Bearish patterns on 1d mostly lost as shorts, consistent with BTC upward drift over DEV.

### 1h (6 of 54 INSUFFICIENT-N: marubozu_up/dn, n 59-61)
All 48 testable rows have net below zero or a CI lower bound below zero; 14 bps cost dominates a gross edge of at most +10 bps.
Closest rows: inv_hammer h1 (gross +9.5, net -4.6 [-11, 2], RC p 0.057, BH q 0.216) and bear_harami h1/h3 (net -9.0/-4.9, RC p
0.32/0.25). Nothing reaches q<0.10 on BH over the 54 trials. Typical rows have gross edge within +-3 bps of zero.

### Volatility-state family (observation only; no triage rule)
Hypothesis tested one-sided: after doji / inside bar / NR7 the next bar expands (range ratio and |return| above the all-bar mean).
Result: the opposite. After NR7 the next-bar range ratio is 0.875 (1d) and 0.826 (1h) vs 1.05-1.06 for all bars; inside_bar and
NR7 next-bar |return| is also lower (1h: -0.0002/-0.0005, BH q 0.001). All six RC p = 1.00 or 0.95+. This is mostly volatility
clustering plus the narrow signal bar being inside the 14-bar denominator (a mechanical bias of the pre-registered metric); it is
not evidence of a tradable compression-then-breakout effect and no direction was traded.

## 6. Passing triage -> VALIDATION
None. No P0 variant and no P1 pattern/horizon on either timeframe meets all four conditions. Nothing is queued for VALIDATION
(validation was not run).

Observation only (not candidates; chosen after seeing output so must not be promoted without a new pre-registered hypothesis):
three_white_soldiers 1d h3/h5 positive net with CI above zero but RC-insignificant; vol-state persistence (next bar after NR7 is calmer).

## 7. Limitations
- DEV only, one asset, one venue, ~4.5y daily / 2.5y hourly. BTC drifted up strongly (B&H +2.17 log daily), which hurts all bearish/short rows.
- Daily families have few events for rarer shapes (6 of 18 patterns INSUFFICIENT-N on 1d, 2 on 1h); absence of a result there is not evidence of absence.
- Implementation choices not set by the pre-reg: common bar range i<=n-7 for all h; BH across all 54 trials with INSUFFICIENT-N as p=1;
  CI by circular block bootstrap of the net series (1000 resamples); vol-ratio denominator = 14 bars ending at the signal bar.
- Overlapping forward windows at h>1 and clustered signals make trades non-independent; the block bootstrap addresses this only approximately.
- Funding on 1d stop-buy entries is approximated (entry assumed open+12h); fixed fee/slip model, no spread or capacity effects.
- RC is single-step max-T, conservative relative to step-down procedures (Romano-Wolf); BH is a secondary view.

## 8. Trial count
130 registry rows (TRIAL_REGISTRY.csv): P0 10 (4 variants + 6 anchors), P1 directional 108 (54 per tf), P1 volatility 12 (6 per tf).
Any later study should deflate for >=130 trials in this family.

## 9. Literature context (citations_verified.txt only)
Candlestick results in equities are mixed: Marshall, Young and Rose (2006, J. Banking & Finance) and Marshall, Young and Cahan
(2007/8, Rev. Quant. Finance Acct.) find no value after costs in US and Japanese data; Lu, Shiu and Liu (2012) and Tharavanij et al.
(2017) report some patterns profitable in specific markets. Crypto: Cohen (2021) optimises patterns for Bitcoin systems; Ho et al.
(2021, IEEE BigData) ask the same question; Moser and Brauneis (2026) study intraday forecasts from patterns. Data-snooping
controls used here follow White (2000), Sullivan, Timmermann and White (1999), Hansen (2005), Hsu, Hsu and Kuan (2010), Romano and
Wolf, and Benjamini and Hochberg (1995). Block bootstrap: Politis and Romano (1994). The present null result is consistent with the
sceptical equity findings and with Park and Irwin (2007) on technical analysis; it does not contradict the crypto studies, which use
different samples, patterns, horizons or optimised thresholds.
