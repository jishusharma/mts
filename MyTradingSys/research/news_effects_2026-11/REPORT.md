Regime mix: events bull 26% / bear 13% / range 62% (n=182); all days 2024-01-01..2026-11-07 bull 23% / bear 16% / range 61% (n=958) (BTC trailing 30-day close-to-close return +-10 %, OURS)

# News-effect event catalogue 2024-2026 (card news-effect-event-catalogue-1108)

Observation only. No weight, flash, bias or gate rule is proposed here. Reaction = BTCUSDT and ETHUSDT public 1m klines (data-api.binance.vision). Files: `news_events.csv` (192 events), `class_summary.csv`, `baseline.csv`, `build_events.py`, `check_catalogue.py` (+ `test_catalogue.py`), `fetch_calendars.py`, `events_seed.py`.

## 1. What is in it

- 192 events, 80 before and 112 after 2025-01-20 17:00 UTC (inauguration, OURS cut).
- Timestamp quality: exact (minute known) 132, approx (hour, about +-1 h) 11, day-only 49. Day-only rows carry the 24 h return from 00:00 UTC only; approx rows carry 60 m / 240 m / 1440 m; exact rows carry every column.
- SOURCED = public release calendars fetched this session: BLS CPI, jobs report (NFP), PPI release dates (bls.gov schedule pages read through Internet Archive snapshots, because bls.gov refuses direct fetches) and FOMC decision days (federalreserve.gov/monetarypolicy/fomccalendars.htm). Release times 08:30 ET and 14:00 ET converted to UTC with the New York tz rules.
- OURS = every other class (grouping is ours; 72 dates come from recall of public coverage, `date_check=recalled`, not fetched).

## 2. Definitions (all OURS)

ref = open of the 1m candle at t0. ret_Hm = close of the candle starting t0+H-1m over ref, in bps (1 bp = 0.01 pct). maxabs60 = largest wick distance from ref in the first 60 candles; peak_min = the minute it happened. vol_x = base volume in the first 15 m (exact) or 60 m (approx) over the average for the same span in the prior 120 m. Baseline (all hours / all days 2024-01-01..2026-11-07, median |open-close|): BTC 1h 20.89 bps, 1d 119.16 bps; ETH 1h 28.8, 1d 168.66.

## 3. Class table (median absolute BTC reaction; blank = too few rows with that precision)

| class | label | n | pre | post | exact | day-only | med abs 15m | med abs 60m | med abs 1440m | x base 60m | x base 1d | later/first 1440m | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CB_OTHER | OURS | 5 | 4 | 1 | 2 | 3 |  |  |  |  |  |  | unknown |
| CPI | SOURCED | 33 | 13 | 20 | 33 | 0 | 50.5 | 63.1 | 169.5 | 3.02 | 1.42 | 0.70 | measured |
| ETF_SEC | OURS | 9 | 7 | 2 | 2 | 6 |  |  | 173.1 |  | 1.45 | 0.09 | measured |
| FED_SPEECH | OURS | 3 | 1 | 2 | 2 | 1 |  |  |  |  |  |  | unknown |
| FOMC | SOURCED | 23 | 8 | 15 | 23 | 0 | 33.9 | 69.6 | 243.2 | 3.33 | 2.04 | 0.48 | measured |
| GEOPOLITICS | OURS | 3 | 0 | 3 | 0 | 3 |  |  |  |  |  |  | unknown |
| HACK | OURS | 5 | 2 | 3 | 1 | 3 |  |  |  |  |  |  | unknown |
| MACRO_SHOCK | OURS | 7 | 1 | 6 | 0 | 7 |  |  |  |  |  |  | unknown |
| NFP | SOURCED | 34 | 13 | 21 | 34 | 0 | 34.4 | 47.0 | 139.0 | 2.25 | 1.17 | 0.77 | measured |
| POLITICS_US | OURS | 19 | 9 | 10 | 1 | 13 |  |  | 159.8 |  | 1.34 | 1.73 | measured |
| PPI | SOURCED | 30 | 13 | 17 | 30 | 0 | 22.5 | 28.1 | 134.5 | 1.35 | 1.13 | 0.86 | measured |
| PROTOCOL_CORP | OURS | 7 | 3 | 4 | 4 | 2 |  |  |  |  |  |  | unknown |
| SUPPLY_OVERHANG | OURS | 6 | 6 | 0 | 0 | 6 |  |  |  |  |  |  | unknown |
| TARIFF_TRADE | OURS | 8 | 0 | 8 | 0 | 5 |  |  | 273.2 |  | 2.29 | 0.95 | measured |

x base = class median over the all-hours (60m) or all-days (1d) median. The hour of a data release is a busy hour, so x base 60m for CPI/NFP/FOMC overstates the effect versus a same-hour baseline (not computed here: gap). 'later/first' = median |1440m| of the later half of the class over the earlier half (needs 8+ rows with a 24 h return).

## 4. Before vs after 2025-01-20 (median absolute BTC 24 h return, bps; class needs 4+ rows per era)

| class | pre n | pre med | post n | post med |
|---|---|---|---|---|
| CB_OTHER | 4 | 167 | 1 | unknown |
| CPI | 13 | 224 | 20 | 112 |
| ETF_SEC | 7 | 204 | 2 | unknown |
| FED_SPEECH | 1 | unknown | 2 | unknown |
| FOMC | 8 | 360 | 15 | 180 |
| GEOPOLITICS | 0 | unknown | 3 | unknown |
| HACK | 2 | unknown | 3 | unknown |
| MACRO_SHOCK | 1 | unknown | 6 | 175 |
| NFP | 13 | 144 | 21 | 114 |
| POLITICS_US | 9 | 121 | 10 | 210 |
| PPI | 13 | 146 | 17 | 119 |
| PROTOCOL_CORP | 3 | unknown | 4 | 214 |
| SUPPLY_OVERHANG | 6 | 114 | 0 | unknown |
| TARIFF_TRADE | 0 | unknown | 8 | 273 |

## 5. Does the same kind of news work twice? (scheduled classes, median |60m| BTC bps by half-year)

| class | 2024H1 | 2024H2 | 2025H1 | 2025H2 | 2026H1 | 2026H2 |
|---|---|---|---|---|---|---|
| CPI | 166 (n=6) | 25 (n=6) | 41 (n=6) | 61 (n=5) | 26 (n=6) | 107 (n=4) |
| NFP | 74 (n=6) | 41 (n=6) | 26 (n=6) | 29 (n=5) | 76 (n=6) | 54 (n=5) |
| FOMC | 172 (n=4) | 63 (n=4) | 69 (n=4) | 73 (n=4) | 79 (n=4) | 19 (n=3) |
| PPI | 30 (n=6) | 21 (n=6) | 14 (n=6) | 96 (n=3) | 28 (n=5) | 100 (n=4) |

Magnitude only. Direction cannot be judged: the catalogue has no consensus-versus-actual (surprise) column, so 'same news moved the opposite way' is not testable from this file (gap 3 below).

## 6. Ten largest BTC 60 m moves

| event | quality | BTC 60m bps | ETH 60m bps |
|---|---|---|---|
| TARIFF_TRADE-2025-04-09-pause_90d | approx | 520 | 1065 |
| ETF_SEC-2024-01-09-spot_btc_fake_tweet | approx | -351 | 295 |
| NFP-2024-05-03-release | exact | 350 | 226 |
| POLITICS_US-2025-01-20-inauguration | exact | -348 | -257 |
| FED_SPEECH-2025-08-22-jackson_hole | exact | 295 | 754 |
| CPI-2024-05-15-release | exact | 263 | 236 |
| FOMC-2024-05-01-statement | exact | 259 | 233 |
| NFP-2026-09-04-release | exact | -249 | -317 |
| PPI-2025-08-14-release | exact | -240 | -383 |
| TARIFF_TRADE-2025-10-10-china_100 | approx | -205 | -316 |

## Gaps (honest list)

1. Classes with fewer than 8 events are reported `unknown`, no number: CB_OTHER, FED_SPEECH, GEOPOLITICS, HACK, MACRO_SHOCK, PROTOCOL_CORP, SUPPLY_OVERHANG.
2. Analyst-named events from the CBP extractions and transcripts: NOT included. `F:/CryptoScrapper/cbp_v2/extractions.md` and the transcript store are absent on this machine (no F: drive). Only the repo's own Binance-hack report was used (HACK 2026-10-29).
3. No actual-versus-consensus data (CPI, NFP surprise), so no direction or surprise-size split.
4. 49 of 192 events are day-only: only a 24 h return, and that window holds other news and the weekend/US-session mix. Their 24 h numbers are weak evidence.
5. 11 approx timestamps are from memory of press coverage (about +-1 h); a wrong hour would shift the 60 m window.
6. All 72 non-calendar dates are recalled, not fetched; the price move itself is the only corroboration. Not verified against a source page.
7. INFERRED: CPI/NFP dates Oct 2025 - Feb 2026 (government shutdown reschedule). Six snapshot dates (CPI 2025-10-15, 11-13, 12-10; NFP 2025-10-03, 11-07, 12-05) were dropped because they were not held that day (both old and new dates appear across snapshots; that they were not held is recall). PPI in Oct 2025 - Feb 2026 is dropped (unverified). Rows flagged `inferred=yes`.
8. Events after mid-2025 other than the calendars, the Fusaka upgrade, the BoJ hike and the Binance hack are thin; 2026 non-calendar news is almost absent (author has no 2026 recall; no online news archive was read).
9. Calendars: 14:00 ET FOMC statement time is the usual time; unscheduled meetings and press-conference timing are not separate rows. PPI/CPI/NFP overlap with other news on the same minute (not de-confounded).
10. Overlapping events (same day: 2025-03-06/07, 2025-05-12) share one price move; rows are not independent.
11. 20-row re-derivation (`check_catalogue.py`) runs offline from `raw/derive_sample.csv` (klines saved by the builder; formula re-coded separately); `--online` refetches. Only 5m/15m/60m are re-derived, not 240m/1440m.

## Parameters, SOURCED or OURS

- SOURCED: release dates and times (BLS, Fed pages). - OURS: class grouping, quality grades, 2025-01-20 17:00 UTC era cut, minimum 8 events per class, +-10 % trailing-30-day regime cut, reaction horizons, 120 m volume baseline.

DECISION (OURS): where a time was uncertain the row is graded down (approx/day) instead of guessed to the minute.

Next: per-class same-hour baseline, surprise column from a public consensus archive, transcript-sourced events once F: is mounted.
