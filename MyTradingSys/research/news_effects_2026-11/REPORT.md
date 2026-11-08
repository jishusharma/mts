# News effects on BTC and ETH: event catalogue v2 and measured reaction (2026-11-08)

Cards news-effect-event-catalogue-1108 and news-effect-catalogue-v2-gaps-1108. Observation only: no trade gate, no Live Aid change, no weight, flash or bias rule is proposed here.
Files: `news_events.csv` (one row per event), `control_windows.csv` (same-clock controls), `analyst_events.md` (analyst mentions with quotes), `build_events.py`, `build_analyst_events.py`, `check_catalogue.py` (acceptance check), `calendar_cache.json` (public release dates and the Fed statement pages checked). Independent review of v1: `REVIEW_OPUS.md`.

## 1. What is in the catalogue

- **191 events**, 191 measured on 1m klines (BTCUSDT and ETHUSDT); 71 before and 120 after the 2025-01-20 17:00Z inauguration; 13 classes.
- **Only verified rows enter any table below** (123 of 191 rows). Verified = the date and the minute were read on a public page: the BLS schedule page (via web.archive.org snapshots) for CPI, PPI and NFP, the Fed statement page ("For release at 2:00 p.m.") for each FOMC meeting. Every other row (our own grouping, dates and times recalled from memory) is marked `verified=N` with a reason in `verify_note`, stays in the CSV, and is in **no** table.
- v2 fixes from the Opus review: the two non-release PPI rows (2025-10-16, 2025-11-14) are removed, the real 2025-11-25 PPI is added (BLS snapshots 20251120 and 20260201), tar-20251010 is marked unverified, CPI + FOMC same-day pairs carry an `overlap` flag (also PPI/NFP same day, and any event within 4 h).
- Reaction columns (percent, per symbol): r1/r5/r15/r60/r240 = close of the minute window vs the close of the minute before t0; up60/dn60 = 1m extremes in 60 min; vr5 = mean volume of the first 5 min / mean of the prior 60; rv60 = stdev of 1m returns of the prior hour; **z15 = r15 / (rv60 sqrt 15) depends on the session** (the prior hour is quiet before 08:30 ET and busy before 14:00 ET), so **z15d = r15 / (stdev of 1m returns over the prior 24 h * sqrt 15)** is the baseline used in the tables; tpk60 / retr60 = minute of the largest excursion and the share given back by minute 60; day_ret = UTC-day open to close.
- Surprise columns `actual`, `consensus`, `prior`, `surprise_sign`, `surprise_url` exist for every CPI, PPI, NFP and FOMC row. **All are `none` in this run** (section 5).

## 2. Verified vs unverified, per class

| class | label | rows | verified | unverified | verified and measured | verified pre/post 01-20 |
|---|---|---|---|---|---|---|
| BOJ_JAPAN | OURS | 4 | 0 | 4 | 0 | 0/0 |
| COURT_LEGAL | OURS | 10 | 0 | 10 | 0 | 0/0 |
| ETF_REGULATORY | OURS | 8 | 0 | 8 | 0 | 0/0 |
| FOMC | SOURCED | 23 | 23 | 0 | 23 | 8/15 |
| GEOPOLITICS | OURS | 6 | 0 | 6 | 0 | 0/0 |
| HACK_EXPLOIT | OURS | 8 | 0 | 8 | 0 | 0/0 |
| MACRO_CPI | SOURCED | 33 | 33 | 0 | 33 | 13/20 |
| MACRO_NFP | SOURCED | 34 | 34 | 0 | 34 | 13/21 |
| MACRO_OTHER | OURS | 8 | 0 | 8 | 0 | 0/0 |
| MACRO_PPI | SOURCED | 33 | 33 | 0 | 33 | 13/20 |
| PROTOCOL | SOURCED | 4 | 0 | 4 | 0 | 0/0 |
| TARIFF_TRADE | OURS | 9 | 0 | 9 | 0 | 0/0 |
| TRUMP_POLICY | OURS | 11 | 0 | 11 | 0 | 0/0 |
| **all** | | 191 | 123 | 68 | 123 | 47/76 |

No ETF, hack, Trump policy, tariff, geopolitics, court, BoJ, protocol or macro-other row is verified: a primary or news-archive page with the minute was not read for any of them in this run (section Gaps). Those classes are UNKNOWN.

## 3. Class table (verified rows; classes with fewer than 8 verified events are UNKNOWN)

Speed and persistence columns are shown beside the random-walk null (simulated, 20,000 paths of 60 one-minute steps): **P(abs r60 > abs r15) = 0.73**, median tpk60 = 46 min, median retr60 = 0.33. Opus review value for the first: 0.73. A class value near the null is not evidence of extension or fade.

| class | n | med abs BTC r15 % | med abs BTC z15d | med abs ETH r15 % | med BTC vr5 | med tpk60 min (null 46) | med retr60 (null 0.33) | share abs r60 > abs r15 (null 73%) |
|---|---|---|---|---|---|---|---|---|
| BOJ_JAPAN | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| COURT_LEGAL | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| ETF_REGULATORY | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| FOMC | 23 | 0.34 | 1.69 | 0.49 | 6.91 | 37 | 0.43 | 70% |
| GEOPOLITICS | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| HACK_EXPLOIT | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| MACRO_CPI | 33 | 0.50 | 2.48 | 0.88 | 11.93 | 32 | 0.32 | 61% |
| MACRO_NFP | 34 | 0.34 | 1.14 | 0.45 | 7.90 | 35 | 0.55 | 56% |
| MACRO_OTHER | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| MACRO_PPI | 33 | 0.23 | 0.83 | 0.36 | 4.62 | 33 | 0.52 | 70% |
| PROTOCOL | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| TARIFF_TRADE | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| TRUMP_POLICY | 0 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

FOMC r60, tpk60 and retr60 mix the 14:00 ET statement with the 14:30 ET press conference; the two windows are not split here.

## 4. Same-clock control: event vs ordinary weekdays at the same UTC minute

For each verified scheduled release, up to 3 weekdays before it with no catalogue event that day, same UTC minute (BTC only, 369 windows in `control_windows.csv`; US market holidays not removed). Baseline z15d (24 h), so the comparison does not depend on the session. p = Mann-Whitney on abs z15d (normal approximation, one test per class, no multiple-test correction).

| class | events | controls | event med abs r15 % | control med abs r15 % | event med abs z15d | control med abs z15d | event share abs z15d > 2 | control share abs z15d > 2 | p |
|---|---|---|---|---|---|---|---|---|---|
| MACRO_CPI | 33 | 99 | 0.50 | 0.17 | 2.48 | 0.72 | 61% | 7% | 0.0000 |
| MACRO_PPI | 33 | 99 | 0.23 | 0.17 | 0.83 | 0.60 | 21% | 6% | 0.1710 |
| MACRO_NFP | 34 | 102 | 0.34 | 0.15 | 1.14 | 0.55 | 24% | 8% | 0.0003 |
| FOMC | 23 | 69 | 0.34 | 0.11 | 1.69 | 0.54 | 30% | 4% | 0.0008 |
| all controls | | 369 | | 0.16 | | 0.60 | | 7% | |

## 5. Reaction by surprise sign (CPI, NFP, FOMC)

Surprise = actual vs consensus. A row enters this table only with a numeric actual, a numeric consensus and a cited public URL. **No such row exists in this run**: the BLS pages answer 403 to scripts, the FRED API timed out, Wayback rate-limited, and no free archived consensus page was reachable; the Fed gives no consensus. Every CPI, PPI, NFP and FOMC row therefore says `none` and is excluded from surprise stats; nothing was filled by guess.

| class | sign | n | median BTC r60 % (signed) | direction hit rate (hot expected down, cool up) |
|---|---|---|---|---|
| MACRO_CPI | hot | 0 | n/a | n/a |
| MACRO_CPI | cool | 0 | n/a | n/a |
| MACRO_CPI | in line | 0 | n/a | n/a |
| MACRO_NFP | hot | 0 | n/a | n/a |
| MACRO_NFP | cool | 0 | n/a | n/a |
| MACRO_NFP | in line | 0 | n/a | n/a |
| FOMC | hot | 0 | n/a | n/a |
| FOMC | cool | 0 | n/a | n/a |
| FOMC | in line | 0 | n/a | n/a |

Rows with sign `none` (excluded from surprise stats): MACRO_CPI 33, MACRO_PPI 33, MACRO_NFP 34, FOMC 23. Analyst remarks that CPI 2026-10-14 and PPI 2026-10-15 were "hot" (section 8) are speech, not a sourced actual vs consensus, and are not used here.

## 6. Before and after 2025-01-20 (verified rows, classes with at least 4 on each side)

| class | pre n | pre med abs BTC r15 % | pre med abs z15d | post n | post med abs BTC r15 % | post med abs z15d | p (abs z15d) |
|---|---|---|---|---|---|---|---|
| FOMC | 8 | 0.58 | 1.78 | 15 | 0.21 | 0.97 | 0.272 |
| MACRO_CPI | 13 | 0.62 | 2.34 | 20 | 0.47 | 2.73 | 0.606 |
| MACRO_NFP | 13 | 0.56 | 1.32 | 21 | 0.32 | 1.02 | 0.079 |
| MACRO_PPI | 13 | 0.18 | 0.58 | 20 | 0.24 | 0.92 | 0.357 |

This is a time split, not a Trump effect: price level, ETF flows, volatility regime and the Fed cycle changed at the same time; no placebo split date was run.

## 7. Repeat decay (verified rows, classes with at least 8)

rho = Spearman rank correlation of occurrence number vs abs BTC z15d (negative = fading). Without surprise data the sign of a data-release move follows the surprise, so sign agreement is shown only as a count.

| class | n | med abs z15d first 3 | med abs z15d later | rho(seq, abs z15d) | med abs r15 % first 3 | med abs r15 % later | sign agreement with previous |
|---|---|---|---|---|---|---|---|
| FOMC | 23 | 1.74 | 1.41 | -0.22 | 0.76 | 0.31 | 36% (22 pairs) |
| MACRO_CPI | 33 | 1.69 | 2.62 | 0.03 | 0.44 | 0.51 | 44% (32 pairs) |
| MACRO_NFP | 34 | 1.09 | 1.14 | -0.34 | 0.32 | 0.35 | 52% (33 pairs) |
| MACRO_PPI | 33 | 0.42 | 0.97 | 0.14 | 0.11 | 0.24 | 44% (32 pairs) |

At n = 23 to 34 a two-sided 5% test needs |rho| of about 0.34 to 0.41. Same-subtype repeats inside the own-grouping classes are not shown: none of those rows is verified.

## 8. Analyst-named events (CBP transcripts) and the measured 1 h move

`analyst_events.md` holds **31 analyst mentions** (transcript id and a verbatim quote each; `scripts/dev/verify_extract_quotes.py` accepts all of them) of **6 distinct catalogue events** by 4 analysts, from the 24 transcripts of 2026-10-14 to 10-22 in the CBP inbox (the 61 raw transcripts in the repo are mostly Hindi RSI teaching videos and name no catalogue event). 7 mentions state a BTC direction; 1 of those are stated before the event, the rest describe what happened. The brief asked for 30 or more analyst-named events: the 30-mention bar is met, but the distinct-event count is 6 because the transcripts cover one month around CPI, PPI and the FOMC.

| event | class | date UTC | verified | BTC r15 % | BTC r60 % | mentions | analysts | before / after | stated BTC direction |
|---|---|---|---|---|---|---|---|---|---|
| cpi-2026-10-14 | MACRO_CPI | 2026-10-14 12:30 | Y | -1.21 | -1.43 | 7 | Benjamin Cowen, Krown, Michaal | 0 / 7 | down after, down after |
| fomc-2026-09-16 | FOMC | 2026-09-16 18:00 | Y | +0.04 | -0.18 | 6 | Benjamin Cowen | 2 / 4 | up after, up after, down before |
| fomc-2026-10-28 | FOMC | 2026-10-28 18:00 | Y | -0.03 | +0.19 | 14 | Benjamin Cowen, Krown | 14 / 0 | none |
| pol-20241106 | TRUMP_POLICY | 2024-11-06 07:30 | N | unverified t0, not shown | not shown | 1 | Jason Pizzino | 0 / 1 | none |
| pol-20250120 | TRUMP_POLICY | 2025-01-20 17:00 | N | unverified t0, not shown | not shown | 1 | Jason Pizzino | 0 / 1 | down after |
| ppi-2026-10-15 | MACRO_PPI | 2026-10-15 12:30 | Y | -0.23 | -1.04 | 2 | Krown | 1 / 1 | down after |

Stated expectation vs measured BTC 1 h move (mentions that state a direction):

| analyst | video | event | timing | stated direction | measured BTC r60 % | match |
|---|---|---|---|---|---|---|
| Benjamin Cowen | H_JhpNaRPl8 | fomc-2026-09-16 | after | up | -0.18 | description of the past, not an expectation |
| Benjamin Cowen | H_JhpNaRPl8 | fomc-2026-09-16 | after | up | -0.18 | description of the past, not an expectation |
| Benjamin Cowen | H_JhpNaRPl8 | fomc-2026-09-16 | before | down | -0.18 | hit |
| Jason Pizzino | 4kpH94Hb0GQ | pol-20250120 | after | down | not shown | description of the past, not an expectation |
| Krown | TDQwVve6G3Y | ppi-2026-10-15 | after | down | -1.04 | description of the past, not an expectation |
| Michaal | Jn9hM3jwEik | cpi-2026-10-14 | after | down | -1.43 | description of the past, not an expectation |
| Michaal | Jn9hM3jwEik | cpi-2026-10-14 | after | down | -1.43 | description of the past, not an expectation |

Direction hit rate of stated expectations before a verified event: 1 of 1. That is n = 1, which is not a test. Stated surprise (analysts only): CPI 2026-10-14 "hotter than expected" (Krown, Michaal), CPI and PPI "hot" (Cowen); no actual or consensus number was quoted, so none of it enters section 5.

## 9. Largest reactions (verified rows, by abs BTC z15d)

| rank | date UTC | class | title | BTC r15 % | ETH r15 % | BTC z15d | BTC vr5 | tpk60 min | overlap |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2024-06-12 12:30 | MACRO_CPI | US CPI release (BLS) - May 2024 data | +2.07 | +2.48 | +10.2 | 27.24 | 35 | SAME_DAY:fomc-2024-06-12 |
| 2 | 2025-02-12 13:30 | MACRO_CPI | US CPI release (BLS) - January 2025 data | -2.06 | -2.48 | -10.0 | 28.652 | 12 | - |
| 3 | 2026-09-04 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - August 2026 data | -2.03 | -3.12 | -8.9 | 34.775 | 17 | - |
| 4 | 2026-04-29 18:00 | FOMC | FOMC rate decision statement 2026-04-29 | -1.30 | -1.82 | -8.0 | 2.514 | 31 | - |
| 5 | 2024-06-07 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - May 2024 data | -1.27 | -1.13 | -7.9 | 8.121 | 11 | - |
| 6 | 2026-10-14 12:30 | MACRO_CPI | US CPI release (BLS) - September 2026 data | -1.21 | -1.36 | -7.6 | 28.141 | 51 | - |
| 7 | 2024-05-03 12:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - April 2024 data | +2.19 | +1.73 | +7.4 | 13.692 | 60 | - |
| 8 | 2024-05-15 12:30 | MACRO_CPI | US CPI release (BLS) - April 2024 data | +1.60 | +1.46 | +6.5 | 34.973 | 60 | - |
| 9 | 2025-08-14 12:30 | MACRO_PPI | US PPI release (BLS) - July 2025 data | -1.33 | -2.02 | -6.1 | 16.052 | 58 | - |
| 10 | 2026-06-17 18:00 | FOMC | FOMC rate decision statement 2026-06-17 | -1.21 | -1.36 | -5.9 | 17.281 | 6 | - |
| 11 | 2026-07-14 12:30 | MACRO_CPI | US CPI release (BLS) - June 2026 data | +0.95 | +1.33 | +5.5 | 21.09 | 54 | - |
| 12 | 2024-04-10 12:30 | MACRO_CPI | US CPI release (BLS) - March 2024 data | -1.47 | -2.12 | -5.1 | 11.925 | 58 | - |
| 13 | 2025-01-10 13:30 | MACRO_NFP | US Employment Situation / NFP (BLS) - December 2024 dat | -1.34 | -1.68 | -4.8 | 39.634 | 10 | - |
| 14 | 2025-01-15 13:30 | MACRO_CPI | US CPI release (BLS) - December 2024 data | +1.26 | +1.62 | +4.6 | 28.104 | 33 | - |
| 15 | 2026-09-10 12:30 | MACRO_PPI | US PPI release (BLS) - August 2026 data | -0.86 | -0.91 | -4.2 | 9.325 | 26 | - |

## Gaps

- **Classes with fewer than 8 events (total): BOJ_JAPAN (4), GEOPOLITICS (6), PROTOCOL (4).** Reported as UNKNOWN, not guessed.
- **Classes with at least 8 events but fewer than 8 verified ones (minute stats UNKNOWN): COURT_LEGAL (0 verified of 10), ETF_REGULATORY (0 verified of 8), HACK_EXPLOIT (0 verified of 8), MACRO_OTHER (0 verified of 8), TARIFF_TRADE (0 verified of 9), TRUMP_POLICY (0 verified of 11).**
- **Events with no reliable timestamp (verified=N): 68** (41 DAY_ONLY placeholder t0, 14 APPROX_INTRADAY, 13 EXACT_REPORTED but recalled). Their minute columns are in the CSV and in no table. Ids: etf-20240109, etf-20240110, etf-20240111, prt-20240313, boj-20240319, crt-20240328, geo-20240413, geo-20240419, prt-20240420, crt-20240430, etf-20240520, etf-20240523, hack-20240531, hack-20240718, etf-20240722, pol-20240727, boj-20240731, mac-20240805, crt-20240807, mac-20240823, geo-20241001, pol-20241106, etf-20241121, pol-20250117, pol-20250120, hack-20250123, pol-20250123, boj-20250124, tar-20250201, tar-20250203, hack-20250221, crt-20250227, pol-20250302, tar-20250304, pol-20250306, pol-20250307, crt-20250319, crt-20250321, tar-20250402, tar-20250409, mac-20250421, prt-20250507, tar-20250512, hack-20250515, mac-20250516, tar-20250523, crt-20250529, geo-20250613, hack-20250618, geo-20250621, geo-20250623, pol-20250717, pol-20250718, crt-20250806, pol-20250807, mac-20250822, mac-20250825, etf-20250918, mac-20251001, tar-20251010, crt-20251023, tar-20251030, hack-20251103, mac-20251112, prt-20251203, crt-20251211, boj-20251219, hack-20261029.
- **Not done in this run: source-verifying the own-grouping rows.** Each ETF, hack, Trump policy, tariff, geopolitics, court, BoJ, protocol and macro-other row needs a primary or news-archive page and a minute checked against it (wire time, post id, block time). The cited URLs are general reference pages, not proof. Follow-up card needed.
- **Inferred, not looked up:** (a) every PUBLIC_WEB_RECALL row (dates, times, titles) is the author memory of public events; every cited URL answered at build time (HTTP 200, or 403 for bls.gov). (b) ET to UTC conversion uses the US DST rule, checked by check_catalogue.py and by the Fed statement pages (EDT/EST named there). (c) BLS dates come from web.archive.org snapshots of the schedule pages (bls.gov blocks scripts); the PPI fix is described in section 1. (d) The era boundary is the 17:00Z oath. (e) The 2026-10-29 Binance row links a generic CoinDesk URL; its time comes from research/news_feeds_2026-10-30/REPORT.md.
- **No surprise data (all rows `none`).** BLS release pages: 403 to scripts. FRED CSV: timed out. Wayback BLS archive pages: 429 at times. No free archived consensus page was reachable and the Fed publishes none. Needed: actual, consensus and prior per CPI, PPI and NFP release from a dated source, and a market-implied expectation for FOMC. Until then the sign, hot-vs-cool and "works twice" questions are open. Follow-up card needed.
- **Analyst-named coverage:** 31 mentions of 6 events; all transcripts date from 2026-10-14 to 10-22 (plus the older ones named in extractions.md, which are not in the scanned inbox). Events that analysts mention but the catalogue lacks (midterms 2026-11-03, the 2026 Iran war and oil, bond yields) are not added. Only 1 mentions state a BTC direction before an event.
- **Confounding:** 4 rows have another scheduled release on the same UTC day (SAME_DAY, e.g. CPI + FOMC on 2024-06-12) and 8 have another event within 4 h; PPI days are often Thursdays with weekly jobless claims at the same minute. Not controlled; overlap rows are flagged, not removed.
- **Controls:** BTC only, up to 3 days per event, holidays not removed. z15 (prior hour) is kept in the CSV but not used for comparisons; z15d (24 h) is. FOMC statement and press conference are not split. No placebo split date, no multiple-test correction: all tables are descriptive.
- **Not covered:** exchange listings, token unlocks, liquidation moves without a named trigger, Fed speakers other than Jackson Hole.
- **No weight, flash or bias rule is proposed** in this report.
