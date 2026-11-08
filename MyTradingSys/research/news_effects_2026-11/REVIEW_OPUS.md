# Independent review (Opus): news-effect catalogue, statistics and data validity (2026-11-08)

Card news-effect-review-opus-1108. What I reviewed: `REPORT.md`, `news_events.csv` (192 rows), the measure/calendar code in `build_events.py`.
I wrote this without reading the other review, or any other review file. I made no edits to the catalogue or its report. I propose no weight, flash or bias rule.
Check: `python check_review.py REVIEW_OPUS.md`.

**Bottom line.** One finding is safe to build on: a scheduled US CPI or NFP release moves BTC/ETH much more in the first 15 minutes than the same clock time on a normal weekday does. FOMC and PPI show a weaker version of the same thing. Nothing else in the catalogue supports a rule yet. That covers the size of a move, its direction, speed, persistence, the pre/post-Trump change, "news stops working twice", and every OURS class.

## How I checked (independent numbers)

- **Arithmetic.** I wrote my own 1m-kline measurer, separate from `build_events.py`, on public Binance klines (data-api.binance.vision). It reproduces r15, z15, vr5 and r60 for BTC and ETH on all 11 rows I re-measured (difference <= 0.001). So the numbers are computed correctly from their t0. The open problems are the t0 values and how the numbers are read.
- **Same-clock control (missing from the catalogue).** For every SCHEDULED macro row I took up to 3 weekdays before the event with no catalogue event on that day, at the same UTC minute: 371 control windows, BTC |z15|.

| class | events n | event med abs z15 | event share abs z15 > 2 | control n | control med abs z15 | control share abs z15 > 2 |
|---|---|---|---|---|---|---|
| MACRO_CPI | 33 | 2.79 | 67% | 99 | 0.80 | 14% |
| MACRO_NFP | 34 | 1.58 | 35% | 102 | 0.66 | 15% |
| FOMC | 23 | 1.37 | 26% | 69 | 0.46 | 3% |
| MACRO_PPI | 34 | 1.12 | 24% | 101 | 0.68 | 14% |
| all controls | - | - | - | 371 | 0.67 | 12% (abs z15 > 3: 4%) |

- **Random-walk null for the speed columns** (simulated pure noise, 20,000 paths of 60 minutes): P(abs r60 > abs r15) = 0.73; median tpk60 = 46 min; median retr60 = 0.32.

## Verdict per class

SAFE = the size effect beats a same-clock control with enough events to rely on. WEAK = a real hint but thin, confounded or with data errors. UNKNOWN = the catalogue cannot say. All verdicts cover **size of the 15-min move only**. Direction is UNKNOWN for every class because there is no surprise (actual vs consensus) data.

| class | verdict | why |
|---|---|---|
| MACRO_CPI | SAFE | 33 timed releases, release dates confirmed. Med abs z15 2.79 vs 0.80 control; 67% vs 14% above 2. Volume spike at the minute (vr5 11.9). Only size is safe; direction, persistence and era change are not. |
| MACRO_NFP | SAFE | 34 timed releases. 1.58 vs 0.66 control; 35% vs 15%. Shutdown dates handled correctly (Oct/Nov 2025 releases checked). About 2/3 of releases are no bigger than noise, so the effect is rare and large, not typical. |
| FOMC | WEAK | n = 23. 1.37 vs 0.46 control, so the effect is probably real. But r60 / tpk60 / retr60 mix the statement with the press conference at +30 min (see 2024-06-12 below). 2024-06-12 also had CPI the same morning. Too few events to split by era. |
| MACRO_PPI | WEAK | 24% vs 14% above 2: a small gap. 2 of 34 rows are dates when no PPI came out (ppi-2025-10-16, ppi-2025-11-14), and the real 2025-11-25 release is missing. 16 of 34 PPI days are Thursdays (same 08:30 ET minute as weekly jobless claims) and 24 of 34 are within 1 day of a CPI release, so the move cannot be attributed to PPI alone. |
| MACRO_OTHER | UNKNOWN | 3 timed rows: 2 Jackson Hole speeches (both large, z 6.2 and 8.7) and a shutdown start. n = 2 per subtype. |
| ETF_REGULATORY | UNKNOWN | 2 timed rows. The rest are APPROX/DAY_ONLY, and the fake-SEC-post row is a one-off. |
| PROTOCOL | UNKNOWN | 4 rows: 3 upgrades and a halving. All are known far ahead, so a t0 move is not expected. |
| HACK_EXPLOIT | UNKNOWN | 1 timed row. DAY_ONLY placeholder times do not capture when the news broke. |
| TARIFF_TRADE | UNKNOWN | 2 timed rows. The placeholder t0 on 2025-10-10 misses the move entirely (see re-checks). |
| TRUMP_POLICY | UNKNOWN | 1 timed row (the inauguration). The others are recalled dates with placeholder times. |
| COURT_LEGAL | UNKNOWN | 0 timed rows. day_ret only, no baseline. |
| GEOPOLITICS | UNKNOWN | 0 timed rows. Many are weekend or overnight, with placeholder times. |
| BOJ_JAPAN | UNKNOWN | 0 timed rows, n = 4. |

Cross-class claims: **pre vs post 2025-01-20: UNKNOWN.** **Repeat decay ("same news does not work twice"): UNKNOWN.** Reasons are in the list below.

## The 5 biggest ways the catalogue could mislead

1. **The speed and persistence columns look like findings but match pure noise.** "Share abs r60 > abs r15" is 56-71% per class. A random walk gives 73%, so the table does not show moves extending; if anything it hints at fading. retr60 for CPI (0.32) equals the noise value. The one column that differs from noise is tpk60: medians of 32-37 min against 46 for noise, which says the largest excursion comes earlier than chance. That is the only defensible speed statement, and for FOMC it is mixed with the press conference.
2. **z15 has no measured baseline and depends on clock time.** z15 divides by the volatility of the prior hour. Before 08:30 ET that hour is quiet; before 14:00 ET it is the active US session. So z15 is not comparable across release times or across classes. My control shows noise gives a median of 0.67 and |z| > 2 on 12% of ordinary days, against 5% for Gaussian noise. Reading z > 2 as "an effect" would flag about one ordinary day in eight.
3. **The OURS classes are selected for being memorable and timed after the fact.** They are recalled from memory (PUBLIC_WEB_RECALL, not re-fetched). 41 have a placeholder t0 and 14 are ±30 min. Events that were remembered tend to be the ones that moved price (survivorship). Events that did not move price are missing, which is exactly the "did not work twice" case. Placeholder times can miss the move completely (2025-10-10: r15 +0.10 at the placeholder, -1.56 about 50 min later). Section 6 day_ret has no baseline; on a ±3% crypto day a 2-3% median is not evidence. Nothing from these classes should feed a weight.
4. **The pre/post-Trump split confounds the era with everything else.** The "pre" period is one year (2024) and "post" is 21 months. Price level, ETF flows, the vol regime and the Fed cycle (hiking-hold vs cutting) all changed at the same time. The per-class n is 8-21 with no test or interval. FOMC 0.58 → 0.21 is 8 events against 15. The era split is a time split with one break chosen in advance. It cannot be attributed to Trump.
5. **"Repeat decay" and "sign agreement" cannot support the operator question as built.** Without surprise data, the sign of a CPI move follows the surprise, not "the news". So sign agreement of 36-52% is what coin-flip surprises would give and says nothing about the market learning. None of the rho values is significant: at n = 23-34 a two-sided 5% test needs |rho| of about 0.34-0.41, and the largest is -0.30. Splitting first 3 against the rest tests 3 events. To claim that the same news does not work twice, you need the surprise size and a matched comparison. Medians of the absolute move are not enough.

Smaller issues: there is no multiple-test correction across 13 classes × many columns. r240 after an 08:30 ET release crosses the 09:30 ET equity open. The overlap count (8 of 192 within ±4 h) misses same-day pairs such as CPI + FOMC on 2024-06-12. The top-15 table ranks by the unbaselined z.

## Events re-checked against primary sources

Dates and times come from BLS release schedules (web.archive.org snapshots, because bls.gov blocks scripts) and the Federal Reserve FOMC calendar page. Reactions come from public Binance 1m klines, re-measured with my own code.

| event_id | primary source | what I checked | status |
|---|---|---|---|
| nfp-2026-09-04 | https://web.archive.org/web/20260801id_/https://www.bls.gov/schedule/news_release/empsit.htm | Lists "August 2026: Sep. 04, 2026 08:30 AM". 12:30Z is correct (EDT). Rank-1 numbers reproduce (BTC r15 -2.03, z -12.27, vr5 34.8). | CONFIRMED |
| cpi-2024-06-12 | https://web.archive.org/web/20240601id_/https://www.bls.gov/schedule/news_release/cpi.htm | "May 2024: Jun. 12, 2024 08:30 AM". Numbers reproduce. FOMC fell on the same day (Fed calendar: June 11-12), which the overlap count misses. | CONFIRMED |
| cpi-2025-02-12 | https://web.archive.org/web/20250115id_/https://www.bls.gov/schedule/news_release/cpi.htm | "January 2025: Feb. 12, 2025 08:30 AM". 13:30Z is correct (EST). Numbers reproduce. | CONFIRMED |
| nfp-2025-07-03 | https://web.archive.org/web/20250301id_/https://www.bls.gov/schedule/news_release/empsit.htm | "June 2025: Jul. 03, 2025" (Thursday, holiday shift). Numbers reproduce. The same snapshot lists Oct 03 / Nov 07 2025, both later cancelled by the shutdown; the catalogue correctly omits them. | CONFIRMED |
| fomc-2024-06-12 | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | June 11-12, 2024 meeting; statement 14:00 ET = 18:00Z. Numbers reproduce (r15 -0.89). At the 18:30Z press conference r15 is 0.00 but r60 is -0.96, so the class r60 mixes statement and presser. | CONFIRMED |
| fomc-2026-04-29 | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | April 28-29, 2026 meeting. Numbers reproduce (r15 -1.30, z -5.60). | CONFIRMED |
| ppi-2025-10-16 | https://web.archive.org/web/20251120id_/https://www.bls.gov/schedule/news_release/ppi.htm | BLS lists "September 2025: Nov. 25, 2025". No PPI came out on Oct 16 (shutdown). Row vr5 1.08 = no volume spike. The real release (2025-11-25 13:30Z) measures BTC r15 -0.67, z -3.24, vr5 1.65 and is missing from the CSV. | WRONG |
| ppi-2025-11-14 | https://web.archive.org/web/20260201id_/https://www.bls.gov/schedule/news_release/ppi.htm | No PPI release on 2025-11-14 in the Nov 2025 or Feb 2026 BLS snapshots (Nov 2025 data on Jan 14, 2026; October folded in). Row vr5 0.75. A phantom event. | WRONG |
| tar-20251010 | https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime=1760126400000&limit=60 | t0 20:00Z is a placeholder: BTC r15 +0.10 and vr5 0.48, so no news minute. At about 20:50Z (my recall of the 100% tariff post, not primary-verified) BTC r15 is -1.56, z -6.3, vr5 14. The time is wrong and the correct time is unverified. | UNVERIFIED |
| mac-20250822 | https://data-api.binance.vision/api/v3/klines?symbol=ETHUSDT&interval=1m&startTime=1755871200000&limit=60 | ETH r15 +7.12 looked like an outlier but reproduces from klines (BTC +2.41). I did not fetch the 10:00 ET speech time from the Fed page; the vr5 13.8 spike at t0 supports it. | UNVERIFIED |
| etf-20240109 | https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime=1704834660000&limit=60 | Numbers reproduce (BTC r15 -2.28 against ETH +1.47, the opposite sign). The vr5 34 spike supports a t0 within minutes. The time comes from memory (APPROX). | UNVERIFIED |

Result: 7 confirmed, 2 wrong (both PPI rows fall in the 2025 shutdown), 2 unverified on time. Every re-measured number matches the CSV. Likely cause of the PPI errors: `merge_snaps` keeps a date from an early snapshot even after later snapshots moved the release. CPI and NFP rows in the shutdown window are correct.

## Method changes required before any weight rule

1. **Fix the calendar.** For every scheduled row, re-take the date from the latest snapshot that lists that reference month. Drop the 2 phantom PPI rows and add 2025-11-25. Fail the build if any SCHEDULED row has vr5 < 1.5 unless it carries a stated reason.
2. **Add a same-clock control to every table.** Compare each event to matched non-event weekdays at the same UTC minute: at least 3 per event, the same measure, excluding catalogue days. Report event against control with a permutation or Mann-Whitney p-value and a bootstrap CI. Drop the Gaussian 0.67 reference.
3. **Replace or annotate the speed columns with their noise values** (P(abs r60 > abs r15) = 0.73, tpk60 46, retr60 0.32 under a random walk, or better, from the control windows). Then compare the class against those values. Without this the columns are not evidence.
4. **Add surprise data before any sign, decay or "works twice" claim.** You need actual minus consensus, standardised, per CPI/NFP/PPI/FOMC row. The decay question then becomes "same-sized surprise, smaller move later?", with a model of |r15| against |surprise| and time. An absolute-move median cannot answer it.
5. **Handle overlaps and attribution.** Flag same-day pairs (CPI+FOMC, PPI+claims, CPI within 1 day of PPI). For FOMC, measure the statement window (0-25 min) and the presser window (+30 min onward) separately. Cut r240 at the equity open or report it separately.
6. **Keep OURS classes out of anything quantitative until they are rebuilt.** Each event needs a primary-sourced minute timestamp: wire or exchange time, or a post ID with its time. The sample must be defined in advance (e.g. every tariff announcement in a fixed source over a fixed period, including the ones that did nothing), not recalled.
7. **Era tests.** Report pre/post as a difference with a bootstrap CI and a placebo break: the same test at other split dates, to see whether 2025-01-20 is special at all. Correct for multiple classes and metrics (e.g. Holm across the comparisons actually reported).

## Gaps of this review

- I fetched primary dates for the 10 rows above, not all 124 scheduled rows.
- The time of tar-20251010 and the Jackson Hole time are not primary-checked.
- Controls cover BTC only and up to 3 days per event.
- I counted the PPI confounds (16 Thursdays, 24 within 1 day of CPI) but did not split the reaction by them.
- The kline measurer and control script I used ran from a scratch folder and are not committed. The control numbers above can be reproduced from the method described in "How I checked".
