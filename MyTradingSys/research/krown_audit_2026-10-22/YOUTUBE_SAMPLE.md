# Krown YouTube sample, 2026-10-22 (search-snippet only)

Status: PARTIAL. youtube.com is unreachable from WebFetch (DNS error), so NO watch page, description, chapter list or transcript was read. Everything below is from WebSearch result snippets (a search-engine summary of the page text/description) plus titles/ids/classes from `../krown_capture_2026-10-16/VIDEO_LIST.csv`. Snippet text is paraphrased by the search tool, so treat numbers as "reported by snippet", not verified quotes. Nothing here compares calls to price.

## 1. What reached / what blocked
| Attempt | Result |
|---|---|
| WebFetch https://www.youtube.com/feeds/videos.xml?channel_id=UCnwxzpFzZNtLH8NgTeAROFA | BLOCKED: getaddrinfo ENOTFOUND www.youtube.com |
| WebFetch https://www.youtube.com/@KrownsCryptoCave/videos | BLOCKED (same) |
| WebFetch https://youtube.com/channel/UCnwxzpFzZNtLH8NgTeAROFA/videos | BLOCKED: ENOTFOUND youtube.com |
| WebFetch https://www.youtube.com/watch?v=uFjS2qFEZmE (and any watch page) | BLOCKED (same). Chapters, full description, transcript: NOT READ for every video |
| WebSearch (youtube.com allowed) | REACHED: titles, URLs, 1 to 3 sentence description-like snippets. No dates (only relative "N days ago", which depend on the search index time, so not used as dates) |
| Generic web search "Krown October 2026" | Only Krown Network (sponsorship press releases), unrelated to the channel |
Conclusion: the 2026-10-15..22 upload list could not be enumerated. NO upload dated after 2026-10-15 was found; the newest id visible anywhere is still TDQwVve6G3Y (CSV row 1, dated 2026-10-15 in INVENTORY s1). Needs a networked host (yt-dlp on the operator box) or the RSS feed from a machine with internet.

## 2. Uploads 2026-10-15 to 2026-10-22
NOT READ / none found. Known newest (CSV order, newest first; dates NOT READ except row 1 = 2026-10-15 per INVENTORY.md):
| # | id | title (CSV) | class |
|---|---|---|---|
| 1 | TDQwVve6G3Y | Bitcoin Hit $79,700 on the PPI Print. What Comes Next This Week | COMMENTARY_OTHER |
| 2 | BvxLX8FL3bg | Bitcoin Sold the CPI Print. The Target Is $79,700 Within 10 Days | EVENT_STRICT (already read) |
| 3 | wvu0onib6WU | Bitcoin: This Signal Points to $95,000 Within 30 Days | already read |
| 4 | uFjS2qFEZmE | Bitcoin Just Did Something Only Done 39 Times. $79,500 Within 10 Days | EVENT_STRICT |
| 7 | ztCLfX7NEmk | Bitcoin Just Did Something Only Done 8 Times. All Up Within 12 Months | EVENT_STRICT |
| 8 | IJN6hlhJ8ZY | Bitcoin's Golden Cross, Day 30: The +20% Step Comes at Day 40 | EVENT_STRICT |
| 9 | ON-z1EhTRjE | Bitcoin: The Dip Is Here. $82,500 Decides the Next 10 Days | COMMENTARY_OTHER |
Rows 5 and 6 (qwjU2jI2D-0, 6aA-P4Gvhrc) are teaching videos. Row-order is the only date evidence.

## 3. Sampled videos (snippet only; "title" = inferred from title; "snippet" = search-tool summary of page text)
Source for all snippets: WebSearch 2026-10-22, the watch URL shown. Chapters: NOT READ. Transcript: NOT READ.

### 3.1 uFjS2qFEZmE  https://www.youtube.com/watch?v=uFjS2qFEZmE
- Title: "only done 39 times. $79,500 Within 10 Days" -> n=39 priors, target $79,500, horizon 10 days (title).
- Snippet: daily corrective setup fires on any close under $82,692; target = daily 55 at $79,489; touched inside 10 days in 82% of cases. (snippet)
- Median/overshoot, invalidation, indicator settings (5/21 EMA presumably; NOT stated in snippet): NOT READ.

### 3.2 BvxLX8FL3bg  (already read in repo) https://www.youtube.com/watch?v=BvxLX8FL3bg
- Snippet (via search for its title): CPI printed hot, BTC sold the print hour (-0.88%), daily corrective setup heads to the 55 line at $79,695, 2.4% below spot. Title says target $79,700 within 10 days. Consistent with 3.1 (same family, level moved).

### 3.3 ztCLfX7NEmk / qsPAh6IBNco  (same signal, daily vs live)
- ztCLfX7NEmk title: "only done 8 times. All Up Within 12 Months" (watch URL not fetched; no snippet returned for it). NOT READ.
- Related live replay qsPAh6IBNco https://www.youtube.com/watch?v=qsPAh6IBNco title "Bitcoin Live: Every Average Just Flipped Bullish. +144% Within 12 Months"; snippet: 55 EMA crossed over the 377 on Oct 5; 8 earlier instances all higher a year later; median +144%. (year of "Oct 5" taken to be 2026, not stated: inferred.)

### 3.4 IJN6hlhJ8ZY  https://www.youtube.com/watch?v=IJN6hlhJ8ZY
- Title: golden cross, day 30, +20% step at day 40. Snippet (search tool, possibly mixing with DyB0RL8GnhA): correction target daily 55 EMA $79,000; 82% of like cases got there in 10 days; overshoot median $75,000. A different video (not verified as Krown's) cites golden cross 30-day low median -9.8%, usually day 14. Treat as UNVERIFIED mapping.

### 3.5 wvu0onib6WU  (already read) https://www.youtube.com/watch?v=wvu0onib6WU
- Snippet: "10-day signal confirms Friday"; 19 prior cases, green 79% a month later; since-2018 median +14.5%. Matches RULES_DRAFT; nothing new.

### 3.6 Older, not-yet-read picks (snippets)
- V0gjxlaW2Qk is on the exclusion list (already read), so skipped. Substitutes seen in snippets:
- AUP1UMotI5w https://www.youtube.com/watch?v=AUP1UMotI5w  (EVENT_STRICT): three green weeks in a row, highest weekly close in 35 weeks; 47 prior cases, median +26% in 13 weeks, +18% since 2018. (snippet)
- sZPfKVEoK0I https://www.youtube.com/watch?v=sZPfKVEoK0I (EVENT_STRICT): weekly momentum over 80 for first time in a year; 12 prior signals all green 9 weeks later. (snippet, from the V0gjxlaW2Qk search)
- Strategy Development & Breakdown playlist: all 36 CSV rows are mostly 2023/24 scalp/automation videos (e.g. C0wM-iKfwaI, mV1Gc2nRGgo, AHJ5nss172k); no snippet fetched for any. NOT READ. HhNEhykPVVc "It's Hard To Beat This Bitcoin Daily Trading Strategy" is the top candidate for a stated entry/exit rule.
- No random older EVENT_STRICT/Strategy video was actually read this run (blocked).

### 3.7 Other recent ids seen in snippets (CSV rows; content NOT READ)
dQuYp63p5xI (CSV row 32) "Bitcoin's Corrective Setup Into the Fed: The 55 EMA Target, the Overshoot and the Bounce": snippet: after a daily 5/21 corrective cross, 55 EMA ($73,135) is target, tested 100%, 88% inside ten days, median 3 days, 16 past cases since 2012, overshoot under the 55 median -3.8%. https://www.youtube.com/watch?v=dQuYp63p5xI
F1hAri0p6dI (row 15) "The Monthly Signal Says $92,000 by October 31" https://www.youtube.com/watch?v=F1hAri0p6dI : snippet: Kalshi snapshot (Oct high >90k 57c; >95k 26c; low <80k 52c; Fed hold Oct 28 81%); band near 92,000.
gTPgrtZXR00 "Bitcoin's October Signal: The Low by Day 5, Then +31%" https://www.youtube.com/watch?v=gTPgrtZXR00 (not in my CSV grep; channel attribution unverified).

## 4. Dated-call ledger (post-2026-09-30)
Exact upload dates NOT READ for every row; "date" = unknown, order = CSV row. Window start = upload day (inferred). Asset = BTC for all.
| video id | date | call / target | window | invalidation | source text |
|---|---|---|---|---|---|
| uFjS2qFEZmE | NOT READ (row 4, before 10-15) | touch daily 55 at $79,489 (title $79,500) after close < $82,692; 82% historic | 10 days | NOT READ | snippet above; title |
| BvxLX8FL3bg | NOT READ (row 2) | daily 55 at $79,695 (title $79,700) after CPI | 10 days | NOT READ | title; snippet 3.2 |
| TDQwVve6G3Y | 2026-10-15 (row 1) | title: BTC "hit $79,700" on PPI; next-week outlook | "this week" | NOT READ | title only; content NOT READ (so target reached by 10-15 per title, no price compared) |
| IJN6hlhJ8ZY | NOT READ (row 8) | 55 EMA $79,000; later +20% step at golden-cross day 40; overshoot median $75,000 | 10 days / day 40 | NOT READ | snippet 3.4 (uncertain) |
| ztCLfX7NEmk / qsPAh6IBNco | NOT READ; 55/377 cross "Oct 5" | up within 12 months, median +144% (8 priors) | 12 months | NOT READ | snippet 3.3 |
| wvu0onib6WU | NOT READ (already in RULES_DRAFT) | $95,000 | 30 days | see RULES_DRAFT | title |
| ON-z1EhTRjE | NOT READ (row 9) | title: $82,500 decides next 10 days | 10 days | $82,500 (title, direction NOT READ) | title only |
The repo's earlier call (BTC 90k..100k by end-Oct 2026; 12h higher low 80k; invalidation 75k/62k) is already in INVENTORY s3. Note: levels in the three newest rows (82,692 -> 79,5xx) show the 55 target moved lower within days; the snippets do not say whether these are the same call updated.

## 5. Event-study families and inputs
| Family | Trigger -> horizon (source) | Inputs |
|---|---|---|
| Daily corrective 5/21 EMA cross -> 55 EMA touch | close under X; 10 days; 82-88% touch, n 16 to 39 (3.1, 3.7) | daily OHLC (EMA 5/21/55) only |
| Overshoot below 55 | median -3.8% / $75k (3.7, 3.4) | daily OHLC |
| Golden cross day-path | day 30, dip median -9.8%, +20% step day 40 (3.4; RULES_DRAFT) | daily close, 50/200 SMA |
| 55 EMA over 377 | 12 months, n 8, median +144% (3.3) | daily OHLC (EMA 55/377) |
| Weekly overbought stochastic > 80 | 9 to 13 weeks, n 12 to 13, 12 of 13 green (3.6; V0gjxlaW2Qk) | weekly OHLC; stochastic length NOT READ |
| 10-day stochastic signal | 1 month, n 19, 79% green (3.5) | 10-day bars aggregated from daily; origin of the 10-day grid NOT READ |
| Three green weeks | 13 weeks, n 47, +26% median (3.6) | weekly close |
| Monthly signal | to Oct 31, $92k band (3.7) | monthly OHLC; prediction-market prices are context, not a trigger |
| CPI/PPI day studies | "138 CPI Days", "91 reports" titles (nujnKp4lVbo); he refuses macro-print trading per INVENTORY | OHLC plus macro release calendar (external dates), maybe intraday hour bars |
| Oct/Sep seasonality | "Red September 9 of 9", "October signal: low by day 5, +31%" (crQGmxaD8Oo, gTPgrtZXR00 titles) | daily/monthly OHLC, calendar |
No snippet mentioned funding or open interest. Nothing here needs more than daily/weekly/monthly OHLCV plus an event calendar for the CPI family; indicator settings (stochastic length, 10-day grid) are NOT READ.

## 6. Next step to finish
Run on a networked host: RSS feed + `yt-dlp --flat-playlist --print "%(id)s %(upload_date)s %(title)s"` for the last 7 days, then `--write-auto-subs --sub-langs en-orig` for uFjS2qFEZmE, IJN6hlhJ8ZY, ztCLfX7NEmk, AUP1UMotI5w, sZPfKVEoK0I, HhNEhykPVVc. Then fill every NOT READ above.
