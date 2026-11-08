# Review of the news-effect catalogue from the market-structure and surprise lens (2026-11-08)

Card news-effect-review-market-lens-1108. Second, independent review of `REPORT.md` and `news_events.csv` (v2, 191 rows, 123 verified).
Independence: this review was written **without reading the other review** (`REVIEW_OPUS.md` exists in the folder and was not opened; the only Opus-review facts used are the ones quoted inside `REPORT.md` itself). No catalogue row was edited. No weight, flash or bias rule is proposed; this is a list of mechanisms, context variables and tests.
DECISION (OURS): the credit runner has no Fable model, so Opus wrote this from the market lens; the reviewer lens, not the model, is the independent part.

Question asked by the operator: why does the same news sometimes not work twice? The lens here is: a release does not move price, the gap between the release and what was already in the price does; what was already in the price is set by positioning, the prior move, the session, the vol regime and who is still awake to trade it.

## 1. Verdict per class

SAFE = the catalogue numbers for this class can be used as a description of the minute reaction (not as a rule). WEAK = numbers exist but the market-lens reading says they are mostly confound or noise. UNKNOWN = no verified minute, nothing to read.

| class | verdict | market-lens reason |
|---|---|---|
| `MACRO_CPI` | SAFE | 33 verified, med abs z15d 2.48 vs control 0.72 (p < 0.0001); the one class whose minute reaction is clearly real. But sign and "works twice" are unreadable without the surprise column. |
| `MACRO_NFP` | SAFE | 34 verified, p = 0.0003 vs controls; retr60 0.55 (null 0.33) says the NFP move is given back more than a random walk: a fade pattern, mechanism in section 2. |
| `FOMC` | WEAK | 23 verified and p = 0.0008, but the 60-min window mixes the 14:00 ET statement and the 14:30 ET press conference; med tpk60 = 37 min sits right after the presser starts, so the measured "FOMC reaction" is partly a presser reaction. Usable only after the split. |
| `MACRO_PPI` | WEAK | p = 0.17 vs same-clock controls, med abs z15d 0.83 vs 0.60: statistically indistinguishable from an ordinary Thursday 08:30 ET minute (which itself carries weekly jobless claims). Treat as noise until a surprise column says otherwise. |
| `ETF_REGULATORY` | UNKNOWN | 0 of 8 verified. Market lens says these are the most positioning-driven events in the set (approval odds, approvals, first trading day), so even when verified they need the prior-move column before any reading. |
| `TRUMP_POLICY` | UNKNOWN | 0 of 11 verified; social-media timestamps, weekend and evening t0, no consensus exists. Section 5. |
| `TARIFF_TRADE` | UNKNOWN | 0 of 9 verified; announce-then-pause pairs (02-01/02-03, 04-02/04-09) are the clearest "does not work twice" case in the whole set and cannot be measured yet. |
| `GEOPOLITICS` | UNKNOWN | 0 of 6 verified; weekend t0 (06-21 Saturday night) means BTC was the only open market, a different mechanism from a weekday release. |
| `HACK_EXPLOIT` | UNKNOWN | 0 of 8 verified; from the market lens only the Bybit size (about 1.5B USD of ETH) is a BTC/ETH event; the rest hit one venue or one token. |
| `COURT_LEGAL` | UNKNOWN | 0 of 10 verified; sentencings and dismissals are known days in advance, little surprise content. |
| `MACRO_OTHER` | UNKNOWN | 0 of 8 verified; a mixed bag (Jackson Hole, yen carry unwind day, shutdown start) with no common mechanism. |
| `BOJ_JAPAN` | UNKNOWN | 0 of 4 verified; the BoJ acts through the carry trade with a lag of days (07-31 hike, 08-05 unwind), a minute window is the wrong instrument. |
| `PROTOCOL` | UNKNOWN | 0 of 4 verified; block-time events are known to the minute in advance, the surprise is zero by construction. |

## 2. Repeat patterns in the catalogue: mechanism and how to test it

The catalogue measures the absolute move per calendar slot. From the market lens the move per slot is `|surprise| x sensitivity(context)`, and a "repeat" is a new draw of the surprise with a changed context. Each pattern below is read that way.

| repeat pattern in the catalogue (section 7 and 6) | mechanism from the market lens | how to test it (public data, no key) |
|---|---|---|
| FOMC fades over the sequence: med abs z15d first 3 = 1.74, later 1.41, rho = -0.22; med abs r15 first 3 = 0.76 % vs later 0.31 %; sign agreement with the previous meeting 36 % | The statement is pre-telegraphed (Fed speakers, the blackout, fed-funds futures), so the statement surprise fell toward zero through 2025-26; what remains at 14:00 ET is a positioning flush, and the information arrives at 14:30 ET in the presser. The fade is surprise compression, not the market "getting used to" the Fed. | Split each FOMC row into 18:00-18:29Z and 18:30-19:00Z (19:00/19:30 in winter). Split SEP meetings (Mar, Jun, Sep, Dec, with dot plot) from the others. Compute the market-implied surprise as the change in the front fed-funds future (CME public settlement) in the first 5 min; regress abs z15d on it; the sequence number should lose its sign. |
| NFP gives back more than a random walk: med retr60 0.55 vs null 0.33, share abs r60 > abs r15 56 % vs null 73 %; rho(seq) = -0.34, at the edge of significance | Two prints at the same minute (headline payrolls and the unemployment rate, plus revisions) often disagree; the first 5 min trade the headline, the next 55 trade the revision and the rate, and the equity open at 09:30 ET (minute 60) resets the move. The "fade" is a two-stage information event, not a market that stopped caring. | Add headline surprise, rate surprise and the two-month revision as separate columns. Condition retr60 on "headline and revision disagree". Measure BTC r15 against ES/NQ front-month r15 at the same minute (CME public data or SPY 1m): if the BTC move is beta to ES the NFP effect is an equity effect. |
| CPI does not fade: rho = 0.03, med abs z15d first 3 = 1.69, later 2.62; share abs r60 > abs r15 61 % (below the 73 % null) | CPI is the one print the whole leveraged crypto book positions for (the only release named in all 24 CBP transcripts of October). The first 15 min are a positioning flush with vr5 of 12 to 35, and the flush ends when the liquidation queue is empty, which is why the move does not extend as much as a random walk. | Pull Binance `fapi/v1/openInterestHist` (5m) and `fapi/v1/fundingRate` for the 24 h before each CPI; compute the OI drop in the first 15 min. Hypothesis: abs z15d scales with pre-event OI and funding, and retr60 is lowest when OI drops most (a cleared book does not come back). |
| PPI rises over the sequence (0.42 to 0.97) but is not different from controls (p = 0.17) | Thursday 08:30 ET carries weekly jobless claims and, in several months, retail sales; the catalogue's "PPI reaction" is a same-minute mixture. The "rise" is the claims and tariff-pass-through narrative of 2025-26, not PPI. | Mark every PPI row with the other releases at the same minute (BLS and Census schedules). Compare PPI-only minutes vs PPI+claims minutes. If the PPI-only group is at the control level, PPI is noise. |
| Post 2025-01-20 abs r15 is lower for FOMC (0.58 to 0.21 %) and NFP (0.56 to 0.32 %, p = 0.079) but abs z15d is not lower for CPI (2.34 to 2.73) | The vol regime, not the president: at a 2x price level with ETF two-way flow, the same information moves fewer percent but the same number of sigmas. A weight in percent would mis-read this as "news works less"; a weight in z would not. | Placebo splits at 2024-07-01, 2024-10-01, 2025-04-01, 2025-07-01, 2025-10-01: if any placebo gives a smaller p than 2025-01-20, the era split is regime. Also report abs r15 / rv24h per row and test the split on that only. |
| Sign agreement with the previous occurrence is 36 to 52 %, i.e. coin-flip | Expected: the sign follows the sign of the surprise, and surprises are serially near-independent. Agreement near 50 % is not a failure of the news, it is the proof that the catalogue has no sign information without the surprise column. | Nothing to test until `actual`/`consensus` are filled; then sign(r60) vs sign(surprise) with the "hot = down" convention of section 5. |
| The 15 largest reactions (section 9) are all CPI, NFP, FOMC with vr5 of 17 to 40 and ETH moving 1.1 to 1.5x BTC | A volume ratio above ~15 in the first 5 min on a 1m baseline is forced flow (stops and liquidations), not discretionary buying. Forced flow does not repeat on the next slot unless leverage has been rebuilt, which takes weeks. That is the direct mechanical answer to "the same news does not work twice": the second time, the people who were forced out the first time are not in the trade. | For each top-15 row read the OI change in the 15 min after t0 (openInterestHist 5m) and the Binance long/short ratio before t0 (`futures/data/globalLongShortAccountRatio`); then look at the next same-class slot: hypothesis abs z15d(next) is below class median when OI fell > 3 % on the current one. |

## 3. Context variables a weight must read before it may look at the class

In order of how much of the move each one explains from the market lens:

1. **Surprise**: actual, consensus, prior, revision, for CPI/PPI/NFP (headline and core; for NFP also the rate and the two-month revision); for FOMC the fed-funds-future change in the first 5 min and whether the meeting has an SEP. Without this column the class average is a mixture and the sign is unknowable. Currently `none` in all 123 verified rows.
2. **Prior move**: BTC r24h, r5d, distance from the 20-day high and low, and the return from the previous same-class event to this one. "Sell the news" is prior move in the expected direction; a weight that ignores it will chase the first and get hit on the second.
3. **Positioning / funding**: perp funding (8 h, Binance public), OI change over 24 h and 7 d, basis (quarterly vs spot), top-trader long/short ratio. All public endpoints, no key needed. High positive funding plus an up prior move is a downside-asymmetric setup whatever the print says.
4. **Forced-flow proxy**: vr5 (already in the CSV) and the OI change in the first 15 min after t0. Above the forced-flow threshold the move is a flush, and a flush is not repeatable on the next slot.
5. **Session and clock**: ET clock of the release (08:30 vs 14:00), DST (12:30Z summer vs 13:30Z winter: the winter slot is after the European lunch, the summer slot before), day of week (PPI Thursdays with claims), minutes to the 09:30 ET equity open (the NFP/CPI 60-min window ends at the open), weekend or holiday (crypto-only price discovery).
6. **Regime**: realized vol 24 h and 7 d (rv60 and the 24 h stdev exist; add 7 d), trend state (above/below the 20 d and 50 d), the implied event move (Deribit DVOL and the front-expiry straddle, public API). If implied already prices a 2 % move, a 2 % realized move is "in line", not a surprise.
7. **Cross-asset**: ES/NQ, DXY and the 2 y yield in the first 5 min. For the scheduled macro classes the crypto move is mostly beta to these; a crypto-only weight will attribute an equity reaction to the news class.
8. **Overlap**: the `overlap` flag (same day or within 4 h) plus the non-catalogue releases at the same minute (claims, retail sales, ISM, Fed speakers, options expiry Fridays).
9. **Liquidity**: a 1 m range or volume baseline of the prior 24 h; the same order hits harder on a thin book (Asian hours, weekends, holidays).

## 4. News classes that are only noise at the minute level

- **MACRO_PPI** as measured: indistinguishable from the same-clock control (p = 0.17), and the control minute already contains claims. Noise until a surprise column separates big-miss PPI from the rest.
- **PROTOCOL** (halving, Dencun, Pectra, Fusaka): the block height and time are known days ahead; surprise is zero by construction. Any minute move is coincidence or a scheduled positioning unwind.
- **COURT_LEGAL** sentencings and announced dismissals: the date is on the court calendar, the outcome is usually known from the plea or the filing; little surprise, no flow.
- **HACK_EXPLOIT** below ~500M USD and on one venue: a venue or token event, not a BTC/ETH event; the one exception in the set is the Bybit size, which moved ETH through forced selling of the stolen ETH and the exchange's hedging, i.e. flow, not news.
- **BOJ_JAPAN** at the minute: the carry channel works over days (the 2024-07-31 hike, the 2024-08-05 unwind); a 60-min window reads nothing.
- **FOMC statement alone** when the meeting has no SEP and the fed-funds future does not move in the first 5 min: the information came earlier through the blackout-period speakers.
- Not noise but **unreadable**: the 68 unverified rows. From the market lens the own-grouping events (ETF, tariffs, Trump policy, geopolitics) are the ones most likely to carry the "does not work twice" effect, and they are exactly the ones with no verified minute.

## 5. What Trump-era news changed (hypotheses, since no post-01-20 own-grouping row is verified)

- **The news moved off the calendar and onto a social-media clock.** Tariff and policy t0s in the CSV are 20:00Z to 22:00Z weekdays, Saturday evening (tar-20250201) and Sunday (pol-20250302, geo-20250621). At those minutes BTC and ETH are the only liquid risk markets open, so crypto becomes the price-discovery venue for macro news: bigger move on a thin book, then a partial reversal when ES opens Sunday 18:00 ET or Monday 09:30 ET. The 60-min window reads the thin-book move and misses the reversal.
- **No consensus exists for an unscheduled post.** Surprise is undefined, so the surprise column of section 3 must be replaced by "was it pre-leaked" (prior 24 h move toward the outcome) and "is it a repeat of a known threat" (the second 100 % tariff threat is not news to a book that lived through the first).
- **Announce-then-pause taught the market to fade.** Tariffs 02-01 then pause 02-03; 04-02 then 90-day pause 04-09; the 10-10 China threat then the 10-30 Busan meeting. After two such pairs a rational book sells the threat less and buys the pause less; this is the reflexive channel the catalogue cannot see because it has no sequence concept across classes. Test, once verified: abs z15d of the n-th tariff threat vs n, and the share of the threat move retraced by the following pause.
- **Policy news that is good for crypto arrives when the book is already long.** The strategic reserve post (Sunday 03-02) and the executive orders fell into a book that had been positioned since the election; the measured minute move is a squeeze, the next-day move is the distribution. The prior-move and funding columns of section 3 are the only way to separate these.
- **Scheduled macro reacts fewer percent but not fewer sigmas** (section 2, era split); plus the Oct-Nov 2025 shutdown delayed CPI/NFP/PPI (cpi-2025-10-24, nfp-2025-11-20, ppi-2025-11-25), so the prints were stale when they arrived and the surprise information content was lower by construction; those three rows should be flagged, not pooled.
- **Fed-independence headlines** (Powell attacks 04-21, the Cook removal 08-25) move crypto through the dollar and the long end, not through crypto flow; they belong with cross-asset, not with TRUMP_POLICY.

## 6. Five ways the catalogue could mislead

1. **A calendar slot is not an information event.** The class tables average absolute moves over slots with unknown surprises; a "fade" or a "works twice" reading from section 7 is a statement about the sequence of surprises, not about the market's response to the news.
2. **The FOMC window holds two events.** The 60-min window after 14:00 ET contains the 14:30 ET press conference; median tpk60 = 37 min says the peak is usually a presser peak. Every FOMC number in sections 3, 4, 6 and 7 is a mixture.
3. **The era split is a regime split.** Percent moves fell after 2025-01-20 while z moves did not; no placebo date was run. A reader will take "news works less under Trump" from section 6 when the table says "vol is lower".
4. **The same-clock control is contaminated.** "No catalogue event that day" leaves claims, retail sales, ISM, Fed speakers and options expiries in the control set; that inflates the control baseline and hides the PPI effect (if any) while making CPI look cleaner than it is because CPI days are also the days other data are not scheduled.
5. **The biggest-reaction table and the own-grouping rows are selected on the outcome.** Section 9 ranks by z15d, so it is tail events by construction, and the 68 recalled events were remembered because they moved; whenever those rows get verified they will carry hindsight selection, and a class statistic built on them will overstate the effect.

## 7. Re-check of catalogue rows

Status: CONFIRMED = the primary page was re-read in this run and agrees with the row; UNVERIFIED = the row's own numbers are internally consistent (the market-lens column) but the primary page was not re-read in this run (bls.gov answers 403 to scripts, so BLS rows are checked against the schedule URL only by reference). WRONG = the row contradicts the source. None were WRONG.

| event_id | primary source | status | market-lens reading of the row |
|---|---|---|---|
| `fomc-2026-04-29` | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260429a.htm | CONFIRMED: page says "For release at 2:00 p.m. EDT" = 18:00Z, matches t0 | r15 -1.30 %, z15d -8.0, vr5 only 2.5, tpk60 31: a large move on low volume at the statement, peak at the presser start; information, not a flush. |
| `fomc-2026-10-28` | https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm | CONFIRMED: page says "For release at 2:00 p.m. EDT" = 18:00Z, matches t0 | r15 -0.03 %, r60 +0.19 %, 14 analyst mentions before and none after: the most-talked-about meeting of the set produced nothing at the minute; the surprise was zero. |
| `fomc-2024-06-12` | https://www.federalreserve.gov/newsevents/pressreleases/monetary20240612a.htm | UNVERIFIED: page answers HTTP 200 in this run, release line not re-read; same-day CPI overlap flagged in the row | CPI at 12:30Z already moved +2.07 %; the FOMC window that day measures a book that was flushed 5.5 h earlier. Should be excluded from the FOMC class stats, not just flagged. |
| `cpi-2024-06-12` | https://www.bls.gov/schedule/news_release/cpi.htm | UNVERIFIED (BLS schedule by reference; 403 to scripts) | Rank 1 reaction: +2.07 %, z15d +10.2, vr5 27, tpk60 35. A cool print into a short-positioned book on FOMC day: the textbook squeeze; non-repeatable by construction. |
| `cpi-2025-02-12` | https://www.bls.gov/schedule/news_release/cpi.htm | UNVERIFIED (BLS schedule by reference) | -2.06 %, z15d -10.0, vr5 28.7, tpk60 12, retr60 0.22: a hot print, peak in 12 min, little retrace; a flush that held because the prior week was already a distribution. |
| `nfp-2026-09-04` | https://www.bls.gov/schedule/news_release/empsit.htm | UNVERIFIED (BLS schedule by reference) | -2.03 % BTC, -3.12 % ETH, vr5 34.8, tpk60 17, retr60 0.05: the largest forced-flow signature in the set (ETH 1.5x BTC = the levered leg); the next NFP (10-02) did -0.16 %: the "does not work twice" case in its purest form. |
| `nfp-2024-05-03` | https://www.bls.gov/schedule/news_release/empsit.htm | UNVERIFIED (BLS schedule by reference) | +2.19 %, tpk60 60, retr60 low: extension into the equity open, a soft print read as a rate-cut print; beta to ES, test with the cross-asset column. |
| `cpi-2024-05-15` | https://www.bls.gov/schedule/news_release/cpi.htm | UNVERIFIED (BLS schedule by reference) | +1.60 %, vr5 35, tpk60 60: the move kept going for the full hour; with the ETF flow of May 2024 the first move was absorbed, not faded. |
| `ppi-2025-08-14` | https://www.bls.gov/schedule/news_release/ppi.htm | UNVERIFIED (BLS schedule by reference) | -1.33 %, z15d -6.1, vr5 16: the one PPI in the top 15; it came the day after a cool CPI (08-12) had set the book long for cuts, i.e. prior move and positioning, not PPI as a class. |
| `fomc-2026-06-17` | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm | UNVERIFIED (Fed page not re-read in this run) | -1.21 %, vr5 17, tpk60 6, retr60 0.52: peak in 6 min and half given back: a flush at the statement with no presser follow-through, the opposite shape of 04-29. |
| `cpi-2026-10-14` | https://www.bls.gov/schedule/news_release/cpi.htm | UNVERIFIED (BLS schedule by reference) | -1.21 %, z15d -7.6, vr5 28, tpk60 51, retr60 0.19; 7 analyst mentions, all after the fact calling it "hot". Consistent with a hot surprise into a long book; the analysts added nothing before. |
| `nfp-2025-01-10` | https://www.bls.gov/schedule/news_release/empsit.htm | UNVERIFIED (BLS schedule by reference) | -1.34 % r15 but -0.43 % r60, vr5 39.6 (the highest in the set), tpk60 10, retr60 0.79: the largest volume spike with the largest give-back; a pure liquidation that mean-reverted within the hour. |
| `cpi-2026-07-14` | https://www.bls.gov/schedule/news_release/cpi.htm | UNVERIFIED (BLS schedule by reference) | +0.95 % r15, +1.59 % r60, tpk60 54, retr60 0.14: extension with low retrace; the repeat of a cool-print pattern that held because funding was not stretched (to be tested with the funding column). |
| `fomc-2024-12-18` | https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm | UNVERIFIED (Fed page not re-read in this run) | -0.89 % r15, -1.90 % r60, tpk60 60, retr60 0: the hawkish-cut meeting; the move was all presser, which the unsplit window credits to the statement. |

## 8. Method changes required before any weight rule

1. **Fill the surprise columns from a dated source** (actual, consensus, prior, revision per CPI/PPI/NFP; fed-funds-future 5-min change and SEP flag per FOMC) and re-run sections 5, 6 and 7 on surprise z, not on class. Until then the sign and "works twice" questions stay open, as the report itself says.
2. **Split FOMC** into statement (18:00-18:29Z / 19:00-19:29Z) and presser windows and into SEP vs non-SEP meetings; exclude same-day CPI+FOMC rows from the class stats rather than flagging them.
3. **Add the positioning and prior-move columns** from public endpoints: r24h, r5d, funding (8 h), OI change 24 h, OI change in the first 15 min after t0, top-trader long/short, Deribit DVOL; all key-free. Report abs z15d conditioned on funding tercile and on sign(prior 24 h) vs sign(r60).
4. **Add the cross-asset column** (ES or SPY, DXY, 2 y yield, first 5 min) and report BTC r15 minus beta x ES r15; a news weight should act on the residual, not the raw move.
5. **Run placebo split dates** for the era test and correct for the number of tests; report the era effect on abs r15 / rv24h, not on abs r15.
6. **Clean the control set** with a full US release calendar (claims, retail sales, ISM, Fed speakers, options expiry) instead of "no catalogue event that day".
7. **Verify the own-grouping rows** (wire time, post id, block time) before any class number is shown for them, and mark each with session (weekend/evening) and "repeat of a prior threat" so the reflexive pattern of section 5 can be measured.
8. **Add a forced-flow flag** (vr5 above threshold and OI drop in 15 min) and report every class statistic with and without flagged rows; a weight must never learn from the flushed rows alone.

## Gaps of this review

- Only 2 primary pages were re-read in this run (the two Fed pages above); the BLS schedule pages answer 403 to scripts, so the 12 BLS and other Fed rows are UNVERIFIED here, not WRONG.
- Every mechanism in sections 2 and 5 is a hypothesis with a stated test; none is tested in this run and none is a finding.
- The Trump-era section rests on unverified rows and on public memory of the event clock; it must be re-read after the own-grouping rows are verified.
- No weight, flash or bias rule is proposed; no catalogue row was changed.
