# RESULT: Tom return-to-value, near-band placebo (|d| <= 1) as PRIMARY, fresh pre-DEV data 2020-2021

Card `tom-v2-gross-first-dev-ext`. Pre-registration `PRE_REG.md` (committed 5fd35b41f before the run). Code `backtest/vp_return_to_value.py` (`near_band_primary`) via `run_near_placebo.py`. One run, 2026-11-01 08:40 UTC.
Data: BTCUSDT USD-M perp 1m, 2020-01-02..2021-12-31 (DEV_EXT, all bars before 2022-01-01), 730 complete UTC days, dropped {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0}. DEV, VALIDATION and HOLDOUT not read.
The 2019 start in the card does not exist as perp data (public from 2020-01); the 24 monthly files were fetched from data.binance.vision (SHA256 verified) because the F: folder is absent on this machine.

## Verdict: FAIL (CI lower bound -0.3 pp is not above 0)

## Verdict arms
| arm | n | mean (pp) | SE (pp) | verdict |
|---|---|---|---|---|
| real minus near-band placebo (|d|<=1) | 352 | 4.4 | 2.35 | FAIL |

- Primary: real return share 63.4 % (n 352, CI 58.2..68.2) vs near placebo 58.9 % (n 353, CI 53.8..64.0); difference 4.4 pp, 95 % day-block CI -0.3..8.9 (2000 resamples). Days in the primary: 365.
- n is 352 real / 353 placebo events, not the card's ~870: the |d|<=1 restriction keeps half of the 8-cycle and the window is 730 days (stated in PRE_REG 0e). The CI is wide enough that a true +4 pp near-band excess is not excluded; the pre-registered rule says FAIL, not "no effect".
- Reading: against a band shifted by at most one ATR the real prior-day value returns to POC about as often (+4.4 pp, CI spans 0). The DEV result (real 57.2 % vs near 51.2 %) and this fresh result (63.4 % vs 58.9 %) both show a positive but sub-significant gap for near bands; the large pooled gap comes from far bands (|d|>=2: real 58.5 % vs placebo 37.3 %, diff 21.1 pp, CI 13.7..28.6, descriptive).
- His 70 % claim: all-d real share 60.9 % (CI 57.2..64.4), 70 % above the CI (descriptive; same as DEV).
- FAIL means stop: the 70/30 return claim has no demonstrated value-specific content on BTC UTC-day value over this window (SETUP_REVIEW sec 6 test 2); it says nothing about cash-session profiles, other instruments, other bin sizes, or an intraday entry rule. No rule is added.

## Descriptive, not the verdict
Pooled all-d, per year, side, per-d, Part B (N=3/6/12), naked-POC and censoring tables are in `full_report.md` (title there is the vp_return template; its "DEV only" wording is the splits.py text, the window here is DEV_EXT). Raw numbers: `results.json`.

## Not in data / limits
Cash-session profile NOT_IN_DATA for BTC; UTC-day value (OURS). A count of a claim, no fee/stop/target. One window, one run; DEV result of vp_return (57.2/46.8/51.2/47.8) is not re-derived here.
