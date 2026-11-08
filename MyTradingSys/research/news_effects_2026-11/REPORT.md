# News effects on BTC and ETH: event catalogue and measured reaction (2026-11-08)

Card news-effect-event-catalogue-1108. Observation only: no trade gate, no Live Aid change, no weight, flash or bias rule is proposed here.
Files: `news_events.csv` (one row per event), `build_events.py` (rebuilds CSV and this report), `check_catalogue.py` (acceptance check), `calendar_cache.json` (public release dates).

## 1. What is in the catalogue

- **192 events**, 192 measured on 1m klines (both BTCUSDT and ETHUSDT); 71 before and 121 after the 2025-01-20 17:00Z inauguration.
- **13 classes.** Label SOURCED = a public calendar fixes the date and time (BLS release schedule via web.archive.org snapshots, Fed FOMC calendar, chain block time). Label OURS = our own grouping of recalled public events.
- Timestamp quality: SCHEDULED (calendar, minute exact) 124, EXACT_REPORTED (publicly stated time) 13, APPROX_INTRADAY (time recalled, maybe +-30 min) 14, DAY_ONLY (date known, t0 set to a placeholder time) 41.
- Analyst-named (found in the CBP extractions or transcripts, dated): 5. See Gaps.
- Reaction columns (percent, per symbol): r1/r5/r15/r60/r240 = close of the minute window vs the close of the minute before t0; up60/dn60 = highest/lowest 1m extreme in the first 60 min; vr5 = mean 1m volume of first 5 min / mean of the prior 60 min; rv60 = stdev of 1m returns of prior 60 min; z15 = r15 / (rv60 * sqrt(15)) (for Gaussian noise the median |z15| is about 0.67; 1m crypto returns are fatter-tailed, so the real noise level is unmeasured); tpk60 = minute of the largest closing excursion in the first 60 min; retr60 = how much of that excursion was given back by minute 60 (0 = none, 1 = all); day_ret = UTC-day open to close.
- Minute-level tables below use only the **timed** rows (SCHEDULED + EXACT_REPORTED, measured_ok): 137 rows. APPROX and DAY_ONLY rows are in the CSV but their minute columns are not trustworthy.

## 2. Class table (timed rows; classes with fewer than 8 timed events are shown as UNKNOWN)

| class | label | n all | n timed | pre/post 01-20 (timed) | med abs BTC r15 % | med abs BTC z15 | med abs ETH r15 % | med BTC vr5 | med tpk60 min | med retr60 | share abs r60 > abs r15 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BOJ_JAPAN | OURS | 4 | 0 | 0/0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| COURT_LEGAL | OURS | 10 | 0 | 0/0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| ETF_REGULATORY | OURS | 8 | 2 | 2/0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| FOMC | SOURCED | 23 | 23 | 8/15 | 0.34 | 1.37 | 0.49 | 6.91 | 37 | 0.43 | 70% |
| GEOPOLITICS | OURS | 6 | 0 | 0/0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| HACK_EXPLOIT | OURS | 8 | 1 | 0/1 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| MACRO_CPI | SOURCED | 33 | 33 | 13/20 | 0.50 | 2.79 | 0.88 | 11.93 | 32 | 0.32 | 61% |
| MACRO_NFP | SOURCED | 34 | 34 | 13/21 | 0.34 | 1.58 | 0.45 | 7.90 | 35 | 0.55 | 56% |
| MACRO_OTHER | OURS | 8 | 3 | 1/2 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| MACRO_PPI | SOURCED | 34 | 34 | 13/21 | 0.22 | 1.12 | 0.34 | 4.49 | 34 | 0.51 | 71% |
| PROTOCOL | SOURCED | 4 | 4 | 2/2 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| TARIFF_TRADE | OURS | 9 | 2 | 0/2 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| TRUMP_POLICY | OURS | 11 | 1 | 0/1 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

Speed reading (timed rows, all classes with n >= 8): median first-60-min peak minute above is the answer to "how fast"; share abs r60 > abs r15 says whether the 15-min move was extended or faded by one hour.

## 3. Before vs after 2025-01-20 (timed rows, classes with at least 4 timed events on each side)

| class | pre n | pre med abs BTC r15 % | pre med abs z15 | post n | post med abs BTC r15 % | post med abs z15 |
|---|---|---|---|---|---|---|
| FOMC | 8 | 0.58 | 1.63 | 15 | 0.21 | 0.91 |
| MACRO_CPI | 13 | 0.62 | 2.79 | 20 | 0.47 | 2.71 |
| MACRO_NFP | 13 | 0.56 | 2.24 | 21 | 0.32 | 1.15 |
| MACRO_PPI | 13 | 0.18 | 0.95 | 21 | 0.23 | 1.18 |

## 4. Repeat decay: did the same kind of news work a second time? (timed rows, classes with at least 8)

Per class, events in time order. "first 3" = the first three occurrences, "later" = the rest. rho = Spearman rank correlation of occurrence number vs abs BTC z15 (negative = fading). Sign agreement = share of events whose BTC r15 has the same sign as the previous event of the class (for data releases the sign depends on a surprise we do not have, see Gaps).

| class | n | med abs z15 first 3 | med abs z15 later | rho(seq, abs z15) | med abs r15 % first 3 | med abs r15 % later | sign agreement with previous |
|---|---|---|---|---|---|---|---|
| FOMC | 23 | 1.44 | 1.08 | -0.24 | 0.76 | 0.31 | 36% (22 pairs) |
| MACRO_CPI | 33 | 2.58 | 3.00 | -0.01 | 0.44 | 0.51 | 44% (32 pairs) |
| MACRO_NFP | 34 | 1.63 | 1.53 | -0.30 | 0.32 | 0.35 | 52% (33 pairs) |
| MACRO_PPI | 34 | 0.50 | 1.18 | 0.05 | 0.11 | 0.23 | 45% (33 pairs) |

Same-subtype repeats inside the OURS classes (timed rows only, so counts are small):

| class / subtype | timed events in order: UTC date, BTC r15 %, BTC z15 |
|---|---|
| ETF_REGULATORY / ETF_LAUNCH | 2024-01-11 +1.35 z2.6; 2024-07-22 -0.22 z-1.2 |
| MACRO_OTHER / JACKSON_HOLE | 2024-08-23 +1.58 z6.2; 2025-08-22 +2.41 z8.7 |
| PROTOCOL / ETH_UPGRADE | 2024-03-13 +0.86 z2.2; 2025-05-07 -0.02 z-0.2; 2025-12-03 +0.01 z0.1 |

## 5. Largest reactions (timed rows, by abs BTC z15)

| rank | date UTC | class | title | BTC r15 % | ETH r15 % | BTC z15 | BTC vr5 | tpk60 min |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-04 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - August 2026 data | -2.03 | -3.12 | -12.3 | 34.775 | 17 |
| 2 | 2024-06-12 12:30 | MACRO_CPI | US CPI release (BLS) - May 2024 data | +2.07 | +2.48 | +10.8 | 27.24 | 35 |
| 3 | 2025-02-12 13:30 | MACRO_CPI | US CPI release (BLS) - January 2025 data | -2.06 | -2.48 | -9.0 | 28.652 | 12 |
| 4 | 2026-10-14 12:30 | MACRO_CPI | US CPI release (BLS) - September 2026 data | -1.21 | -1.36 | -8.8 | 28.141 | 51 |
| 5 | 2025-08-22 14:00 | MACRO_OTHER | Powell Jackson Hole speech (10:00 ET) | +2.41 | +7.12 | +8.7 | 13.753 | 55 |
| 6 | 2024-05-03 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - April 2024 data | +2.19 | +1.73 | +8.6 | 13.692 | 60 |
| 7 | 2025-01-10 13:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - December 2024 data | -1.34 | -1.68 | -7.8 | 39.634 | 10 |
| 8 | 2025-08-14 12:30 | MACRO_PPI | US PPI release (BLS) - July 2025 data | -1.33 | -2.02 | -7.8 | 16.052 | 58 |
| 9 | 2025-01-15 13:30 | MACRO_CPI | US CPI release (BLS) - December 2024 data | +1.26 | +1.62 | +6.6 | 28.104 | 33 |
| 10 | 2024-08-23 14:00 | MACRO_OTHER | Powell Jackson Hole speech (10:00 ET) | +1.58 | +1.19 | +6.2 | 9.532 | 16 |
| 11 | 2024-05-15 12:30 | MACRO_CPI | US CPI release (BLS) - April 2024 data | +1.60 | +1.46 | +6.0 | 34.973 | 60 |
| 12 | 2025-07-03 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - June 2025 data | -0.61 | -0.83 | -6.0 | 12.027 | 20 |
| 13 | 2026-07-14 12:30 | MACRO_CPI | US CPI release (BLS) - June 2026 data | +0.95 | +1.33 | +6.0 | 21.09 | 54 |
| 14 | 2026-04-29 18:00 | FOMC | FOMC rate decision statement 2026-04-29 | -1.30 | -1.82 | -5.6 | 2.514 | 31 |
| 15 | 2024-06-07 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - May 2024 data | -1.27 | -1.13 | -5.5 | 8.121 | 11 |

## 6. Classes without a reliable minute timestamp (day-level view, all measured rows)

Placeholder t0 rows: the only trustworthy columns are day_ret (UTC day open to close) and the sign/size of up60/dn60 as a rough envelope.

| class | n approx/day-only | med abs BTC day_ret % | med abs ETH day_ret % | share BTC day_ret < 0 |
|---|---|---|---|---|
| BOJ_JAPAN | 4 | 2.71 | 3.38 | 50% |
| COURT_LEGAL | 10 | 1.74 | 1.92 | 40% |
| ETF_REGULATORY | 6 | 1.76 | 5.27 | 33% |
| GEOPOLITICS | 6 | 2.56 | 5.27 | 50% |
| HACK_EXPLOIT | 7 | 0.32 | 2.34 | 57% |
| MACRO_OTHER | 5 | 2.74 | 0.49 | 80% |
| TARIFF_TRADE | 7 | 3.71 | 5.19 | 71% |
| TRUMP_POLICY | 10 | 1.60 | 3.04 | 40% |

For comparison, median abs BTC day_ret over all UTC days in range is not computed here (one more request); the numbers above have no baseline. Treat them as descriptive.

## Gaps

- **Classes with fewer than 8 events (total): BOJ_JAPAN (4), GEOPOLITICS (6), PROTOCOL (4).** Reported as UNKNOWN, not guessed.
- **Classes with at least 8 events but fewer than 8 timed ones (minute stats UNKNOWN): COURT_LEGAL (0 timed of 10), ETF_REGULATORY (2 timed of 8), HACK_EXPLOIT (1 timed of 8), MACRO_OTHER (3 timed of 8), TARIFF_TRADE (2 timed of 9), TRUMP_POLICY (1 timed of 11).**
- **Events with no reliable timestamp: 55** (41 DAY_ONLY with a placeholder t0 of the author choosing, 14 APPROX_INTRADAY recalled to about +-30 min). Their minute columns are in the CSV but excluded from sections 2 to 5. Ids: etf-20240109, etf-20240110, boj-20240319, crt-20240328, geo-20240413, geo-20240419, crt-20240430, etf-20240520, etf-20240523, hack-20240531, hack-20240718, pol-20240727, boj-20240731, mac-20240805, crt-20240807, geo-20241001, pol-20241106, etf-20241121, pol-20250117, hack-20250123, pol-20250123, boj-20250124, tar-20250201, tar-20250203, hack-20250221, crt-20250227, pol-20250302, pol-20250306, pol-20250307, crt-20250319, crt-20250321, tar-20250409, mac-20250421, tar-20250512, hack-20250515, mac-20250516, tar-20250523, crt-20250529, geo-20250613, hack-20250618, geo-20250621, geo-20250623, pol-20250717, pol-20250718, crt-20250806, pol-20250807, mac-20250825, etf-20250918, tar-20251010, crt-20251023, tar-20251030, hack-20251103, mac-20251112, crt-20251211, boj-20251219.
- **Inferred, not looked up:** (a) all PUBLIC_WEB_RECALL rows (dates, times, titles) are from the author memory of public events; they were NOT re-fetched one by one from the cited page. The URL is a general public reference page, not proof of the date; every URL answered at build time (HTTP 200, or 403 for bls.gov). Treat a wrong date as possible; the volume-spike check below only covers scheduled releases. (b) ET to UTC conversion of BLS/Fed times uses the US DST rule, checked by check_catalogue.py (clock) and by a volume spike at the release minute. (c) BLS dates come from web.archive.org snapshots of the BLS schedule pages (bls.gov itself blocks scripts); entries that later snapshots no longer list (shutdown-cancelled releases) were dropped by a coverage rule. (d) The era boundary uses the 17:00Z oath, not the election. (e) The Fed calendar page parse also returned a one-day non-meeting item (2025-08-22, the Jackson Hole date), dropped by a two-day-meeting filter; the 2026-10-29 Binance row links a generic CoinDesk URL and its time comes from the repo report research/news_feeds_2026-10-30/REPORT.md (Tree News headline 20:39:00Z).
- **No surprise data.** Actual vs consensus is not in the catalogue (no free timestamped consensus source was used), so the sign of a CPI/NFP/PPI/FOMC reaction cannot be read as good or bad news; only size, speed and persistence are measured. Sign agreement in section 4 is therefore weak evidence.
- **Analyst-named coverage is thin.** The CBP extractions (2026-09-27, 74 KB) and the 24 inbox plus 61 raw transcripts are almost all Oct 2026 videos. Dated named events found and catalogued: the 2026-10-14 CPI, the PPI (extraction says Oct 16, the BLS calendar says 2026-10-15; the calendar date is used), 2026-10-28 FOMC, the 2026-10-29 Binance hack and the 2025-01-20 inauguration. Named but NOT catalogued because no reliable date is on file: the 2026 Iran war (oil to 120), Powell remarks on long rates, "Trump says war is over" headlines, and the generic 2025 tariff references. Transcripts older than Sept 2026 were not found in the scanned folders.
- **Confounding.** Many events sit within 4 hours of another catalogued event (e.g. FOMC with a Powell speech, CPI with PPI the same week, weekend vs weekday liquidity). Overlap count: 8 of 192 events have another event within +-4h. Not controlled.
- **No random-time control.** z15 normalises by the prior hour volatility (Gaussian noise median about 0.67, real baseline unmeasured); no matched same-clock-time control sample was drawn. Small classes, no multiple-test correction: every medians table is descriptive, not a finding.
- **Not covered:** exchange listings, token unlocks, liquidations-driven moves without a named trigger, Fed speakers other than Jackson Hole, 2026 events other than the five above, stock-market-hours effects on ETH/BTC beyond the volume ratio.
- **No weight, flash or bias rule is proposed** in this report. The next step in the operator plan (model reviews, then one combined analysis) starts from this table and the CSV.
